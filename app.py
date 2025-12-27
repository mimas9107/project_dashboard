import os
import json
import subprocess
from collections import Counter
from flask import Flask, jsonify, render_template, request, abort

# --- 配置讀取 ---
def load_env(filepath='.env'):
    env_data = {'SCAN_DIR': './', 'HOST': '127.0.0.1', 'PORT': 5001}
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    k, v = line.strip().split('=', 1)
                    env_data[k] = v.strip('"').strip("'")
    return env_data

envdata = load_env()
SCAN_PATH = os.path.abspath(envdata['SCAN_DIR'])
FAV_FILE = 'favorites.json'

app = Flask(__name__)

# --- 我的最愛儲存邏輯 ---
def load_favorites():
    if os.path.exists(FAV_FILE):
        try:
            with open(FAV_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: return []
    return []

def save_favorites(favs):
    with open(FAV_FILE, 'w', encoding='utf-8') as f:
        json.dump(favs, f)

# --- 工具函數 ---
def get_project_description(project_path):
    """擷取 README.md 的 H1 標題"""
    readme_path = os.path.join(project_path, 'README.md')
    if os.path.exists(readme_path):
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                for line in f:
                    content = line.strip()
                    if content.startswith('#'):
                        return content.lstrip('#').strip()[:64]
        except: pass
    return "尚無簡介文字"

def get_git_status(project_path):
    if not os.path.isdir(os.path.join(project_path, '.git')):
        return None
    try:
        status_result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=project_path, capture_output=True, text=True, timeout=3
        )
        return "Modified" if status_result.stdout.strip() else "Up-to-date"
    except: return "Error"

def analyze_languages(project_path):
    language_map = {
        '.py': 'Python', '.js': 'JavaScript', '.rs': 'Rust', '.go': 'Go',
        '.html': 'HTML', '.css': 'CSS', '.ts': 'TypeScript', '.cpp': 'C++'
    }
    ignore_dirs = {'.git', 'node_modules', '__pycache__', 'venv'}
    file_counts = Counter()
    for root, dirs, files in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith('.')]
        for file in files:
            ext = os.path.splitext(file)[1]
            if ext in language_map:
                file_counts[language_map[ext]] += 1
    total = sum(file_counts.values())
    return {lang: round((count / total) * 100) for lang, count in file_counts.items()} if total > 0 else {}

def get_directory_tree(path, depth=2):
    if depth < 0: return None
    tree = {'name': os.path.basename(path), 'type': 'folder', 'children': []}
    try:
        for entry in os.scandir(path):
            if entry.name.startswith('.') or entry.name in {'.git', 'node_modules', 'venv'}: continue
            if entry.is_dir():
                child = get_directory_tree(entry.path, depth - 1)
                if child: tree['children'].append(child)
            else:
                tree['children'].append({'name': entry.name, 'type': 'file'})
    except: pass
    tree['children'].sort(key=lambda x: (x['type'] != 'folder', x['name'].lower()))
    return tree

# --- API 路由 ---
@app.route('/')
def index(): return render_template('index.html')

@app.route('/api/projects')
def get_projects():
    favs = load_favorites()
    projects = []
    if not os.path.isdir(SCAN_PATH): return jsonify([])
    for entry in os.listdir(SCAN_PATH):
        p_path = os.path.join(SCAN_PATH, entry)
        if os.path.isdir(p_path) and os.path.exists(os.path.join(p_path, 'README.md')):
            projects.append({
                "name": entry,
                "description": get_project_description(p_path),
                "is_favorite": entry in favs,
                "languages": analyze_languages(p_path),
                "git_status": get_git_status(p_path)
            })
    return jsonify(projects)

@app.route('/api/favorite', methods=['POST'])
def toggle_favorite():
    data = request.json
    name = data.get('name')
    favs = load_favorites()
    if name in favs: favs.remove(name)
    else: favs.append(name)
    save_favorites(favs)
    return jsonify({"status": "success", "is_favorite": name in favs})

@app.route('/api/structure/<name>')
def get_structure(name):
    target = os.path.normpath(os.path.join(SCAN_PATH, name))
    if not target.startswith(SCAN_PATH): abort(403)
    return jsonify(get_directory_tree(target))

@app.route('/api/open/<name>')
def open_in_code(name):
    target = os.path.normpath(os.path.join(SCAN_PATH, name))
    if target.startswith(SCAN_PATH):
        subprocess.run(['code', target], shell=(os.name == 'nt'))
        return jsonify({"status": "success"})
    return jsonify({"status": "failed"}), 403

if __name__ == "__main__":
    app.run(debug=True, host=envdata['HOST'], port=int(envdata['PORT']))