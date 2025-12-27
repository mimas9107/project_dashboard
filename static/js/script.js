window.onload = () => fetchProjects();

async function fetchProjects() {
    const grid = document.getElementById('projectGrid');
    const res = await fetch('/api/projects');
    const projects = await res.json();
    
    const favs = projects.filter(p => p.is_favorite);
    const others = projects.filter(p => !p.is_favorite);

    let html = favs.map(p => createCard(p)).join('');
    if (favs.length > 0 && others.length > 0) {
        html += '<div class="col-12"><div class="section-divider"><span>其他專案</span></div></div>';
    }
    html += others.map(p => createCard(p)).join('');
    grid.innerHTML = html || '<div class="col-12 text-center text-muted">目前沒有專案</div>';
}

function createCard(p) {
    const langHtml = Object.entries(p.languages)
        .map(([l, pct]) => `<span class="badge lang-badge lang-${l}">${l} ${pct}%</span>`)
        .join(' ');

    return `
        <div class="col-md-4 mb-4">
            <div class="card h-100 project-card shadow-sm" onclick="showStructure('${p.name}')">
                <div class="card-body">
                    <div class="d-flex justify-content-between">
                        <h5 class="project-title">${p.name}</h5>
                        <button class="btn-fav ${p.is_favorite ? 'active' : ''}" 
                                onclick="event.stopPropagation(); toggleFav('${p.name}')">
                            <i class="bi ${p.is_favorite ? 'bi-star-fill' : 'bi-star'}"></i>
                        </button>
                    </div>
                    <p class="project-desc">${p.description}</p>
                    <div class="mb-3">${langHtml}</div>
                    <div class="d-flex justify-content-between">
                        <span class="badge ${p.git_status === 'Modified' ? 'bg-warning text-dark' : 'bg-success'}">
                            <i class="bi bi-git"></i> ${p.git_status || 'No Git'}
                        </span>
                        <button class="btn btn-sm btn-outline-light" onclick="event.stopPropagation(); openVSCode('${p.name}')">
                            VS Code
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
}

async function toggleFav(name) {
    await fetch('/api/favorite', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name})
    });
    fetchProjects();
}

async function showStructure(name) {
    document.getElementById('modalTitle').innerText = name;
    new bootstrap.Modal(document.getElementById('structureModal')).show();
    const res = await fetch(`/api/structure/${name}`);
    const data = await res.json();
    document.getElementById('treeContent').innerHTML = `<ul class="tree-list">${renderTree(data)}</ul>`;
}

function renderTree(node) {
    let html = `<li><i class="bi ${node.type === 'folder' ? 'bi-folder-fill text-warning' : 'bi-file-earmark-code'}"></i> ${node.name}`;
    if (node.children) html += `<ul class="tree-list">${node.children.map(c => renderTree(c)).join('')}</ul>`;
    return html + '</li>';
}

async function openVSCode(name) { await fetch(`/api/open/${name}`); }