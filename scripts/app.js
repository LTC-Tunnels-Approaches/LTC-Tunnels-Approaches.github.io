const DEFAULT_ICON = "fa-solid fa-square";
let currentGroup = null;
let currentParentTile = null;
let navigationStack = [];
let currentFilter = 'all';
let currentFilterSub = 'all';

const mainPage = document.getElementById('main-page');
const tilesPage = document.getElementById('tiles-page');
const subtilesPage = document.getElementById('subtiles-page');
const backButton = document.getElementById('back-button');
const tilesPageTitle = document.getElementById('tiles-page-title');
const subtilesPageTitle = document.getElementById('subtiles-page-title');
const mainTilesGrid = document.getElementById('main-tiles-grid');
const subTilesGrid = document.getElementById('sub-tiles-grid');
const tilesSearch = document.getElementById('tiles-search');
const subtilesSearch = document.getElementById('subtiles-search');
const filterButton = document.getElementById('filter-button');
const filterMenu = document.getElementById('filter-menu');
const filterLabel = document.getElementById('filter-label');
const filterButtonSub = document.getElementById('filter-button-sub');
const filterMenuSub = document.getElementById('filter-menu-sub');
const filterLabelSub = document.getElementById('filter-label-sub');

const categoryIcons = {
    'Public': '<i class="fa-solid fa-lock-open badge-icon"></i>',
    'Private': '<i class="fa-solid fa-lock badge-icon"></i>',
    'Work in Progress': '<i class="fa-solid fa-spinner badge-icon"></i>'
};

function createTileHTML(tile, hasSubtiles = false, isClickable = true) {
    const categoryClass = tile.category.toLowerCase().replace(/ /g, '-');
    const subtileIndicator = hasSubtiles ? "has-subtiles" : "";
    const iconClass = (tile.icon && tile.icon.trim()) ? tile.icon : DEFAULT_ICON;
    const categoryBadge = `<div class="tile-category-badge ${categoryClass}">${categoryIcons[tile.category] || ''}${tile.category === 'Work in Progress' ? 'WIP' : tile.category}</div>`;

    if (hasSubtiles && isClickable) {
        return `<div class="tile ${tile.colour} ${subtileIndicator}" data-id="${tile.id}" data-title="${tile.title.toLowerCase()}" data-category="${tile.category}" data-clickable="true" style="cursor: pointer;">${categoryBadge}<div class="tile-content"><div class="tile-icon"><i class="${iconClass}"></i></div><div class="tile-title">${tile.title}</div></div></div>`;
    } else if (tile.url && tile.url !== '') {
        return `<a href="${tile.url}" target="_blank" class="tile ${tile.colour}" data-id="${tile.id}" data-title="${tile.title.toLowerCase()}" data-category="${tile.category}" style="text-decoration: none; color: inherit; display: block;">${categoryBadge}<div class="tile-content"><div class="tile-icon"><i class="${iconClass}"></i></div><div class="tile-title">${tile.title}</div></div></a>`;
    } else {
        return `<div class="tile ${tile.colour}" data-id="${tile.id}" data-title="${tile.title.toLowerCase()}" data-category="${tile.category}">${categoryBadge}<div class="tile-content"><div class="tile-icon"><i class="${iconClass}"></i></div><div class="tile-title">${tile.title}</div></div></div>`;
    }
}

function showPage(pageId) {
    [mainPage, tilesPage, subtilesPage].forEach(p => p.classList.remove('active'));
    document.getElementById(pageId).classList.add('active');
    backButton.classList.toggle('visible', pageId !== 'main-page');
}

function goBack() {
    if (navigationStack.length > 0) {
        const previous = navigationStack.pop();
        if (previous === 'main') {
            showPage('main-page');
            currentGroup = null;
            currentParentTile = null;
            currentFilter = 'all';
            currentFilterSub = 'all';
        } else if (previous === 'tiles') {
            showTilesForGroup(currentGroup);
            currentParentTile = null;
        }
    }
}

function showTilesForGroup(groupName) {
    currentGroup = groupName;
    navigationStack = ['main'];
    currentFilter = 'all';
    const mainTiles = window.tilesData.filter(t => t.type === 'tile' && Array.isArray(t.tags) && t.tags.includes(groupName));
    const tilesWithSubtiles = new Set();
    window.tilesData.forEach(t => { if (t.type === 'sub-tile' && t.parent_id) tilesWithSubtiles.add(t.parent_id); });
    
    tilesPageTitle.textContent = groupName + " Subjects";
    if (mainTiles.length > 0) {
        mainTilesGrid.innerHTML = mainTiles.map(tile => createTileHTML(tile, tilesWithSubtiles.has(tile.id), true)).join('');
        mainTilesGrid.querySelectorAll('.tile[data-clickable="true"]').forEach(tileEl => {
            tileEl.addEventListener('click', (e) => {
                e.preventDefault();
                const tileId = tileEl.getAttribute('data-id');
                showSubTilesForParent(tileId);
            });
        });
    } else {
        mainTilesGrid.innerHTML = `<div class="empty-state"><i class="fa-solid fa-folder-open"></i><p>No subjects available for ${groupName}</p></div>`;
    }

    tilesSearch.value = '';
    filterLabel.textContent = 'All Categories';
    filterButton.classList.remove('active');
    filterMenu.querySelectorAll('.filter-option').forEach(o => o.classList.remove('selected'));
    filterMenu.querySelector('[data-filter="all"]').classList.add('selected');
    showPage('tiles-page');
}

function showSubTilesForParent(parentId) {
    currentParentTile = parentId;
    navigationStack.push('tiles');
    currentFilterSub = 'all';
    const parentTile = window.tilesData.find(t => t.id === parentId);
    const subTiles = window.tilesData.filter(t => t.type === 'sub-tile' && t.parent_id === parentId && Array.isArray(t.tags) && t.tags.includes(currentGroup));
    
    if (parentTile) subtilesPageTitle.textContent = parentTile.title;
    if (subTiles.length > 0) {
        subTilesGrid.innerHTML = subTiles.map(tile => createTileHTML(tile, false, false)).join('');
    } else {
        subTilesGrid.innerHTML = `<div class="empty-state"><i class="fa-solid fa-folder-open"></i><p>No related documents available</p></div>`;
    }

    subtilesSearch.value = '';
    filterLabelSub.textContent = 'All Categories';
    filterButtonSub.classList.remove('active');
    filterMenuSub.querySelectorAll('.filter-option').forEach(o => o.classList.remove('selected'));
    filterMenuSub.querySelector('[data-filter="all"]').classList.add('selected');
    showPage('subtiles-page');
}

function applyFilters(searchTerm, categoryFilter, gridElement) {
    const tiles = gridElement.querySelectorAll('.tile');
    const term = searchTerm.toLowerCase().trim();
    let visibleCount = 0;
    
    tiles.forEach(tile => {
        const titleEl = tile.querySelector('.tile-title');
        const title = titleEl ? titleEl.textContent.toLowerCase() : '';
        const category = tile.getAttribute('data-category') || '';
        const matchesSearch = term === '' || title.includes(term);
        const matchesCategory = categoryFilter === 'all' || category === categoryFilter;
        
        if (matchesSearch && matchesCategory) {
            tile.style.display = '';
            visibleCount++;
        } else {
            tile.style.display = 'none';
        }
    });
}

filterButton.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    filterMenu.classList.toggle('show');
});

filterButtonSub.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    filterMenuSub.classList.toggle('show');
});

document.addEventListener('click', (e) => {
    if (!filterButton.contains(e.target) && !filterMenu.contains(e.target)) {
        filterMenu.classList.remove('show');
    }
    if (!filterButtonSub.contains(e.target) && !filterMenuSub.contains(e.target)) {
        filterMenuSub.classList.remove('show');
    }
});

filterMenu.querySelectorAll('.filter-option').forEach(option => {
    option.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        const filter = option.getAttribute('data-filter');
        
        filterMenu.querySelectorAll('.filter-option').forEach(o => o.classList.remove('selected'));
        option.classList.add('selected');
        
        if (filter === 'all') {
            filterLabel.textContent = 'All Categories';
            filterButton.classList.remove('active');
        } else {
            filterLabel.textContent = filter === 'Work in Progress' ? 'WIP' : filter;
            filterButton.classList.add('active');
        }
        
        currentFilter = filter;
        applyFilters(tilesSearch.value, currentFilter, mainTilesGrid);
        filterMenu.classList.remove('show');
    });
});

filterMenuSub.querySelectorAll('.filter-option').forEach(option => {
    option.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        const filter = option.getAttribute('data-filter');
        
        filterMenuSub.querySelectorAll('.filter-option').forEach(o => o.classList.remove('selected'));
        option.classList.add('selected');
        
        if (filter === 'all') {
            filterLabelSub.textContent = 'All Categories';
            filterButtonSub.classList.remove('active');
        } else {
            filterLabelSub.textContent = filter === 'Work in Progress' ? 'WIP' : filter;
            filterButtonSub.classList.add('active');
        }
        
        currentFilterSub = filter;
        applyFilters(subtilesSearch.value, currentFilterSub, subTilesGrid);
        filterMenuSub.classList.remove('show');
    });
});

tilesSearch.addEventListener('input', (e) => {
    applyFilters(e.target.value, currentFilter, mainTilesGrid);
});

subtilesSearch.addEventListener('input', (e) => {
    applyFilters(e.target.value, currentFilterSub, subTilesGrid);
});

backButton.addEventListener('click', goBack);

document.querySelectorAll('.main-group-tile').forEach(btn => {
    btn.addEventListener('click', () => {
        const groupName = btn.getAttribute('data-group');
        showTilesForGroup(groupName);
    });
});

console.log("✅ Hub initialised - filters and search working");
