/**
 * Project Dashboard 核心邏輯
 */

// 當頁面載入完成後初始化
window.onload = () => {
    fetchProjects();
};

/**
 * 從 API 獲取專案清單並渲染卡片
 */
async function fetchProjects() {
    const grid = document.getElementById('projectGrid');
    try {
        const res = await fetch('/api/projects');
        const projects = await res.json();
        
        if (projects.length === 0) {
            grid.innerHTML = '<div class="col-12 text-center text-muted py-5">找不到任何專案，請檢查 SCAN_DIR 設定。</div>';
            return;
        }

        grid.innerHTML = projects.map(p => createProjectCard(p)).join('');
    } catch (error) {
        console.error('無法載入專案:', error);
        grid.innerHTML = '<div class="col-12 text-center text-danger py-5">載入失敗，請確保後端服務已啟動。</div>';
    }
}

/**
 * 產生單個專案卡片的 HTML 標籤
 */
function createProjectCard(p) {
    const langBadges = Object.entries(p.languages)
        .map(([l, pct]) => `<span class="badge bg-secondary lang-badge">${l} ${pct}%</span>`)
        .join('');

    const gitClass = p.git_status === 'Modified' ? 'bg-warning text-dark' : 'bg-success';
    const gitStatus = p.git_status || 'No Git';

    return `
        <div class="col-md-4">
            <div class="card h-100 shadow-sm project-card" onclick="showStructure('${p.name}')">
                <div class="card-body">
                    <h5 class="card-title text-primary">${p.name}</h5>
                    <div class="mb-2">${langBadges}</div>
                    <div class="d-flex justify-content-between align-items-center mt-3">
                        <span class="badge ${gitClass}">
                            <i class="bi bi-git me-1"></i>${gitStatus}
                        </span>
                        <button class="btn btn-sm btn-outline-dark" onclick="event.stopPropagation(); openVSCode('${p.name}')">
                            <i class="bi bi-code-slash me-1"></i>VS Code
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
}

/**
 * 顯示專案資料夾結構
 */
async function showStructure(name) {
    const modalTitle = document.getElementById('modalTitle');
    const treeContent = document.getElementById('treeContent');
    
    modalTitle.innerText = name;
    treeContent.innerHTML = `
        <div class="text-center py-4">
            <div class="spinner-border text-primary" role="status"></div>
            <p class="mt-2 text-muted">正在掃描資料夾結構...</p>
        </div>
    `;

    const modal = new bootstrap.Modal(document.getElementById('structureModal'));
    modal.show();

    try {
        const res = await fetch(`/api/structure/${name}`);
        if (!res.ok) throw new Error('無法獲取結構');
        const data = await res.json();
        treeContent.innerHTML = `<ul class="tree-list">${renderTree(data)}</ul>`;
    } catch (error) {
        treeContent.innerHTML = `<div class="alert alert-danger">載入結構時發生錯誤：${error.message}</div>`;
    }
}

/**
 * 遞迴渲染目錄樹
 */
function renderTree(node) {
    if (!node) return '';
    
    let iconClass = node.type === 'folder' ? 'bi-folder-fill' : 'bi-file-earmark-text text-muted';
    let html = `<li><i class="bi ${iconClass}"></i> ${node.name}`;
    
    if (node.children && node.children.length > 0) {
        html += `<ul class="tree-list">${node.children.map(child => renderTree(child)).join('')}</ul>`;
    }
    
    html += '</li>';
    return html;
}

/**
 * 呼叫 API 開啟 VS Code
 */
async function openVSCode(name) {
    try {
        const res = await fetch(`/api/open/${name}`);
        const data = await res.json();
        if (data.status !== 'success') alert('開啟失敗');
    } catch (error) {
        alert('無法連線到後端服務');
    }
}