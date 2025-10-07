import os
import json
import subprocess
from collections import Counter
from flask import Flask, jsonify, render_template, request


envfile=open('.env','r')
buf=envfile.readlines()
envdata={}
for e in buf:
    k,v=e.strip('\n').split('=')
    envdata[k]=v

envfile.close()

# --- Configuration ---
SCAN_PATH = envdata['SCAN_DIR']

# --- Flask App Initialization ---
app = Flask(__name__)

# --- Git Status Logic ---

def get_git_status(project_path):
    """
    Checks the Git status of a repository.
    Returns a string indicating the status: Modified, Ahead, Behind, Up-to-date, or No remote.
    """
    if not os.path.isdir(os.path.join(project_path, '.git')):
        return None

    try:
        # 1. Check for uncommitted changes
        status_result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=project_path, capture_output=True, text=True, timeout=10
        )
        if status_result.stdout.strip():
            return "Modified"

        # 2. Fetch latest info from remote (if a remote exists)
        remote_result = subprocess.run(
            ['git', 'remote'],
            cwd=project_path, capture_output=True, text=True, timeout=10
        )
        if not remote_result.stdout.strip():
            return "No remote"
            
        subprocess.run(['git', 'fetch'], cwd=project_path, timeout=30)

        # 3. Check for ahead/behind status
        status_sb_result = subprocess.run(
            ['git', 'status', '-sb'],
            cwd=project_path, capture_output=True, text=True, timeout=10
        )
        status_line = status_sb_result.stdout.strip().split('\n')[0]
        
        if "[ahead" in status_line:
            return "Ahead"
        if "[behind" in status_line:
            return "Behind"
        
        return "Up-to-date"

    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error checking git status for {project_path}: {e}")
        return "Error"


# --- Core Logic (Functions from Step 2) ---

def analyze_languages(project_path):
    """
    Analyzes the file extensions within a project path to determine language composition.
    """
    language_map = {
        '.py': 'Python', '.js': 'JavaScript', '.c': 'C', '.cpp': 'C++',
        '.h': 'C/C++', '.rs': 'Rust', '.go': 'Go', '.java': 'Java',
        '.html': 'HTML', '.css': 'CSS', '.sh': 'Shell', '.md': 'Markdown',
        'Dockerfile': 'Docker', 'Makefile': 'Makefile', '.dart': 'Dart'
    }
    ignore_dirs = {'.git', 'node_modules', '__pycache__', '.vscode', 'venv', 'env'}
    file_counts = Counter()
    
    for root, dirs, files in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith('.')]
        for file in files:
            if file.startswith('.'):
                continue
            ext = os.path.splitext(file)[1]
            lang = language_map.get(ext)
            if not lang and file in language_map:
                lang = language_map[file]
            if lang:
                file_counts[lang] += 1
    
    total_files = sum(file_counts.values())
    if total_files == 0:
        return {}
    
    return {lang: round((count / total_files) * 100) for lang, count in file_counts.items()}

def scan_projects(path, enable_git_scan=False):
    """
    Scans the first-level subdirectories for projects (must contain README.md).
    Optionally scans for Git status if enable_git_scan is True.
    """
    projects = []
    if not os.path.isdir(path):
        return []

    for entry in os.listdir(path):
        project_path = os.path.join(path, entry)
        if not os.path.isdir(project_path) or entry == 'project_dashboard':
            continue
        
        readme_path = os.path.join(project_path, 'README.md')
        if not os.path.exists(readme_path):
            continue

        description = "No description found."
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip().startswith('# '):
                        description = line.strip()[2:]
                        break
        except Exception:
            pass

        has_git = os.path.isdir(os.path.join(project_path, '.git'))
        languages = analyze_languages(project_path)
        
        project_data = {
            "name": entry,
            "path": project_path,
            "description": description,
            "has_git": has_git,
            "languages": languages
        }

        if has_git and enable_git_scan:
            project_data["git_status"] = get_git_status(project_path)
        
        projects.append(project_data)
        
    return sorted(projects, key=lambda p: p['name'].lower())


# --- API and Page Routes ---

@app.route('/api/projects')
def get_projects():
    """API endpoint to get the list of scanned projects."""
    git_scan_enabled = request.args.get('git_scan', 'false').lower() == 'true'
    projects_data = scan_projects(SCAN_PATH, enable_git_scan=git_scan_enabled)
    return jsonify(projects_data)

@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

# --- Main Execution Block for Web Server ---

if __name__ == "__main__":
    """
    This block runs when the script is executed directly.
    It starts the Flask development web server.
    """
    print("Starting the Project Dashboard web server...")
    print(f"Open your browser and go to http://{envdata['HOST']}:{envdata['PORT']}")
    app.run(debug=True,host=envdata['HOST'], port=envdata['PORT'])
