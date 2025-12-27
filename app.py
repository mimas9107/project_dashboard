import os
import subprocess
from collections import Counter
from flask import Flask, jsonify, render_template, request, abort

# --- 強健的配置讀取 ---
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

app = Flask(__name__)

# --- 工具函數：Git 狀態 ---
def get_git_status(project_path):
    if not os.path.isdir(os.path.join(project_path, '.git')):
        return None
    try:
        # 僅檢查本地修改以確保反應速度
        status_result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=project_path, capture_output=True, text=True, timeout=5
        )
        return "Modified" if status_result.stdout.strip() else "Up-to-date"
    except Exception:
        return "Error"

# --- 工具函數：語言分析 ---
def analyze_languages(project_path):
    language_map = {
        '.py': 'Python', '.js': 'JavaScript', '.rs': 'Rust', '.go': 'Go',
        '.html': 'HTML', '.css': 'CSS', '.ts': 'TypeScript', '.cpp': 'C++'
    }
    ignore_dirs = {'.git', 'node_modules', '__pycache__', 'venv', 'env'}
    file_counts = Counter()
    
    for root, dirs, files in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith('.')]
        for file in files:
            ext = os.path.splitext(file)[1]
            if ext in language_map:
                file_counts[language_map[ext]] += 1
    
    total = sum(file_counts.values())
    return {lang: round((count / total) * 100) for lang, count in file_counts.items()} if total > 0 else {}

# --- 工具函數：目錄樹產生器 ---
def get_directory_tree(path, depth=2):
    if depth < 0: return None
    tree = {'name': os.path.basename(path), 'type': 'folder', 'children': []}
    ignore = {'.git', 'node_modules', '__pycache__', 'venv'}
    
    try:
        for entry in os.scandir(path):
            if entry.name.startswith('.') or entry.name in ignore:
                continue
            if entry.is_dir():
                child = get_directory_tree(entry.path, depth - 1)
                if child: tree['children'].append(child)
            else:
                tree['children'].append({'name': entry.name, 'type': 'file'})
    except Exception: pass
    
    tree['children'].sort(key=lambda x: (x['type'] != 'folder', x['name'].lower()))
    return tree

# --- API 路由 ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/projects')
def get_projects():
    projects = []
    if not os.path.isdir(SCAN_PATH): return jsonify([])

    for entry in os.listdir(SCAN_PATH):
        p_path = os.path.join(SCAN_PATH, entry)
        # 僅掃描包含 README.md 的資料夾 
        if os.path.isdir(p_path) and os.path.exists(os.path.join(p_path, 'README.md')):
            projects.append({
                "name": entry,
                "has_git": os.path.isdir(os.path.join(p_path, '.git')),
                "languages": analyze_languages(p_path),
                "git_status": get_git_status(p_path)
            })
    return jsonify(sorted(projects, key=lambda x: x['name'].lower()))

@app.route('/api/structure/<name>')
def get_structure(name):
    target_path = os.path.normpath(os.path.join(SCAN_PATH, name))
    if not target_path.startswith(SCAN_PATH) or not os.path.isdir(target_path):
        abort(404)
    return jsonify(get_directory_tree(target_path))

@app.route('/api/open/<name>')
def open_in_code(name):
    target_path = os.path.normpath(os.path.join(SCAN_PATH, name))
    if target_path.startswith(SCAN_PATH):
        subprocess.run(['code', target_path], shell=(os.name == 'nt'))
        return jsonify({"status": "success"})
    return jsonify({"status": "failed"}), 403

if __name__ == "__main__":
    app.run(debug=True, host=envdata['HOST'], port=int(envdata['PORT']))