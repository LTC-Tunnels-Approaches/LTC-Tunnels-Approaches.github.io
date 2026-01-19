import requests
import pandas as pd
from pathlib import Path
import os
import json
import sys

# Get API token from GitHub secrets (not .env)
API_TOKEN = os.getenv("MORTA_API_TOKEN")
if not API_TOKEN:
    print("❌ ERROR: MORTA_API_TOKEN not set in GitHub secrets")
    sys.exit(1)

API_URL = (
    "https://api.morta.io/v1/table/views/"
    "6dbab052-7c8c-4f6b-b4d8-595ec7d2794a/rows?size=1000"
)

script_dir = Path(__file__).parent
css_folder = script_dir / "styles"
scripts_folder = script_dir / "scripts"
output_html_file = script_dir / "index.html"

css_folder.mkdir(parents=True, exist_ok=True)
scripts_folder.mkdir(parents=True, exist_ok=True)

print("📡 Fetching data from Morta API...")
headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json",
}
response = requests.get(API_URL, headers=headers, verify=False)
if response.status_code != 200:
    print(f"❌ API request failed: {response.status_code} {response.text}")
    sys.exit(1)

print("✅ Data fetched successfully")

json_data = response.json()
rows = [item.get("rowData") for item in json_data.get("data", []) if item.get("rowData")]
df = pd.DataFrame(rows)

if "Tile_Id" in df.columns:
    df.rename(columns={"Tile_Id": "id"}, inplace=True)
if "order" in df.columns:
    df["order"] = pd.to_numeric(df["order"], errors="coerce").fillna(0).astype(int)
else:
    df["order"] = 0
df["id"] = df["id"].astype(str)
if "parent_id" in df.columns:
    df["parent_id"] = df["parent_id"].astype(str)
else:
    df["parent_id"] = None

DEFAULT_ICONS = {
    "Master Information Delivery Plan": "fa-regular fa-calendar-check",
    "Carbon Management": "fa-solid fa-seedling",
    "Consents Register": "fa-solid fa-landmark",
    "Temporary Works Register": "fa-solid fa-helmet-safety",
    "Procurement Management": "fa-solid fa-cart-shopping",
    "Digital Engineering Management": "fa-solid fa-cube",
    "Programme Management": "fa-regular fa-calendar-check",
    "Land Access": "fa-solid fa-map-location-dot",
    "Information Standards": "fa-solid fa-car-tunnel",
    "Monthly Progress Report": "fa-solid fa-chart-area",
}

GROUP_ICONS = {
    "BMJ": "fa-solid fa-helmet-safety",
    "AMJ": "fa-solid fa-pen-ruler",
    "LTC": "fa-solid fa-road-bridge",
    "Third Party": "fa-solid fa-handshake",
    "Help Centre": "fa-solid fa-circle-info",
}

GROUP_COLORS = {
    "BMJ": "linear-gradient(135deg, #dc2626 0%, #b91c1c 100%)",
    "AMJ": "linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%)",
    "LTC": "linear-gradient(135deg, #0891b2 0%, #0e7490 100%)",
    "Third Party": "linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%)",
    "Help Centre": "linear-gradient(135deg, #64748b 0%, #475569 100%)",
}

GROUP_LABELS = {
    "BMJ": ("BMJ", "Joint Venture"),
    "AMJ": ("AMJ", "Designers"),
    "LTC": ("LTC", "Project"),
    "Third Party": ("Third Party", "Supply Chain"),
    "Help Centre": ("Help Centre", "Support"),
}

def get_icon(row: pd.Series) -> str:
    icon = row.get("icon")
    if isinstance(icon, str) and icon.strip():
        return icon.strip()
    return DEFAULT_ICONS.get(row.get("title"), "fa-solid fa-square")

def parse_tags(raw) -> list:
    if isinstance(raw, list):
        return [str(t).strip() for t in raw if str(t).strip()]
    if isinstance(raw, str) and raw.strip():
        txt = raw.strip()
        if txt.startswith("[") and txt.endswith("]"):
            try:
                data = json.loads(txt)
                if isinstance(data, list):
                    return [str(t).strip() for t in data if str(t).strip()]
            except Exception:
                pass
        return [p.strip() for p in txt.split(",") if p.strip()]
    return ["BMJ"]

df = df.sort_values(["type", "order"])
tiles_data = []
for _, row in df.iterrows():
    tiles_data.append({
        "id": str(row["id"]),
        "title": str(row.get("title", "Untitled")),
        "colour": str(row.get("colour", "blue")),
        "category": str(row.get("category", "Public")),
        "type": str(row.get("type", "tile")),
        "icon": get_icon(row),
        "url": str(row.get("url")) if pd.notna(row.get("url")) else "",
        "tags": parse_tags(row.get("Tags")),
        "parent_id": str(row["parent_id"]) if pd.notna(row["parent_id"]) else None,
    })

tiles_json = json.dumps(tiles_data, indent=4)

unique_categories = sorted(set(tile['category'] for tile in tiles_data if tile['category']))
main_tiles = [t for t in tiles_data if t['type'] == 'tile']
found_groups = set(tag for tile in main_tiles for tag in tile['tags'] if tag in GROUP_ICONS)
preferred_order = ["BMJ", "AMJ", "LTC", "Third Party", "Help Centre"]
active_groups = [g for g in preferred_order if g in found_groups]

print(f"✅ Categories: {unique_categories}")
print(f"✅ Active groups: {active_groups}")

category_badge_map = {
    'Public': ('public', 'fa-solid fa-lock-open', 'Public'),
    'Private': ('private', 'fa-solid fa-lock', 'Private'),
    'Work in Progress': ('wip', 'fa-solid fa-spinner', 'WIP'),
}

def generate_filter_options_html():
    html = '<div class="filter-option selected" data-filter="all">\n'
    html += '    <span class="filter-badge" style="background:#94a3b8;"></span>\n'
    html += '    All Categories\n</div>\n'
    for category in unique_categories:
        badge_class, icon, display_text = category_badge_map.get(category, (category.lower().replace(' ', '-'), '', category))
        html += f'<div class="filter-option" data-filter="{category}">\n'
        html += f'    <span class="filter-badge {badge_class}"></span>\n'
        html += f'    {display_text}\n</div>\n'
    return html

def generate_group_tiles_html():
    html = ""
    for group in active_groups:
        icon = GROUP_ICONS.get(group, "fa-solid fa-square")
        label, sublabel = GROUP_LABELS.get(group, (group, ""))
        html += f'<button class="main-group-tile" data-group="{group}">\n'
        html += f'    <div class="main-group-icon"><i class="{icon}"></i></div>\n'
        html += f'    <div class="main-group-label">{label}<br><small style="font-size:12px;opacity:0.9;font-weight:400;">{sublabel}</small></div>\n'
        html += '</button>\n'
    return html

def generate_group_css():
    css = ""
    for group in active_groups:
        gradient = GROUP_COLORS.get(group, "linear-gradient(135deg, #64748b 0%, #475569 100%)")
        css += f'.main-group-tile[data-group="{group}"] {{ background: {gradient}; }}\n'
    return css

filter_options_html = generate_filter_options_html()
group_tiles_html = generate_group_tiles_html()
group_css = generate_group_css()

main_css = r"""* { box-sizing: border-box; }
body { margin: 0; font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif; background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); min-height: 100vh; }
.page-container { max-width: 1400px; margin: 0 auto; padding: 40px 24px 60px; }
.page-title { margin: 0 0 48px; font-size: 36px; font-weight: 700; color: #1e293b; text-align: center; letter-spacing: -0.5px; }
.page-subtitle { text-align: center; color: #64748b; font-size: 16px; margin: -36px 0 48px; }
.controls-bar { position: absolute; top: 40px; right: 24px; display: flex; gap: 12px; align-items: center; }
.search-container { position: relative; width: 300px; }
.search-input { width: 100%; padding: 12px 16px 12px 44px; border: 2px solid #e2e8f0; border-radius: 12px; font-size: 14px; transition: all 0.2s ease; background: #fff; color: #1e293b; }
.search-input::placeholder { color: #94a3b8; }
.search-input:focus { outline: none; border-color: #3b82f6; box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1); }
.search-icon { position: absolute; left: 16px; top: 50%; transform: translateY(-50%); color: #94a3b8; font-size: 16px; }
.filter-dropdown { position: relative; }
.filter-button { padding: 12px 20px; background: #fff; border: 2px solid #e2e8f0; border-radius: 12px; cursor: pointer; font-size: 14px; font-weight: 500; color: #475569; display: flex; align-items: center; gap: 8px; transition: all 0.2s ease; }
.filter-button:hover { border-color: #cbd5e1; background: #f8fafc; }
.filter-button.active { background: #3b82f6; color: #fff; border-color: #3b82f6; }
.filter-menu { position: absolute; top: 100%; right: 0; margin-top: 8px; background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); padding: 8px; min-width: 200px; display: none; z-index: 100; }
.filter-menu.show { display: block; }
.filter-option { padding: 10px 14px; cursor: pointer; border-radius: 8px; transition: all 0.15s ease; display: flex; align-items: center; gap: 10px; font-size: 14px; color: #475569; }
.filter-option:hover { background: #f1f5f9; }
.filter-option.selected { background: #eff6ff; color: #3b82f6; font-weight: 500; }
.filter-badge { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.filter-badge.public { background: #10b981; }
.filter-badge.private { background: #6366f1; }
.filter-badge.wip { background: #f59e0b; }
.page { display: none; animation: fadeIn 0.3s ease; }
.page.active { display: block; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.back-button { position: fixed; top: 40px; left: 24px; border: none; background: #fff; color: #475569; padding: 12px 20px; border-radius: 12px; cursor: pointer; font-size: 15px; font-weight: 500; display: none; align-items: center; gap: 8px; transition: all 0.2s ease; z-index: 1000; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border: 2px solid #e2e8f0; }
.back-button.visible { display: flex; }
.back-button:hover { background: #f8fafc; transform: translateX(-3px); box-shadow: 0 6px 16px rgba(0,0,0,0.12); }
.main-groups-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 20px; max-width: 1200px; margin: 0 auto; }
.main-group-tile { border: none; cursor: pointer; border-radius: 16px; padding: 48px 24px; color: #fff; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 16px; box-shadow: 0 4px 16px rgba(0,0,0,0.1); transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); aspect-ratio: 1; position: relative; overflow: hidden; }
.main-group-tile::before { content: ''; position: absolute; inset: 0; background: linear-gradient(135deg, rgba(255,255,255,0.15) 0%, rgba(255,255,255,0) 100%); opacity: 0; transition: opacity 0.3s ease; }
.main-group-tile:hover::before { opacity: 1; }
""" + group_css + r""".main-group-tile .main-group-icon { font-size: 56px; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3)); color: #fff !important; }
.main-group-tile .main-group-icon i { color: #fff !important; }
.main-group-tile .main-group-label { font-size: 17px; font-weight: 600; text-align: center; letter-spacing: 0.3px; color: #fff; }
.main-group-tile:hover { transform: translateY(-6px) scale(1.02); box-shadow: 0 12px 32px rgba(0,0,0,0.18); }
.page-header { margin-bottom: 40px; padding-top: 70px; text-align: center; }
.page-header h2 { margin: 0 0 8px; font-size: 32px; color: #1e293b; font-weight: 700; letter-spacing: -0.5px; }
.page-header .subtitle { color: #64748b; font-size: 15px; }
.tiles-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 24px; }
.tile { border-radius: 16px; color: #fff; box-shadow: 0 4px 16px rgba(0,0,0,0.08); transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); position: relative; overflow: hidden; }
.tile::before { content: ''; position: absolute; inset: 0; background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 100%); opacity: 0; transition: opacity 0.3s ease; }
.tile:hover::before { opacity: 1; }
.tile.blue { background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%); }
.tile.light-blue { background: linear-gradient(135deg, #0e7490 0%, #0891b2 100%); }
.tile.orange { background: linear-gradient(135deg, #c2410c 0%, #ea580c 100%); }
.tile:hover { transform: translateY(-6px); box-shadow: 0 12px 32px rgba(0,0,0,0.15); }
.tile-content { padding: 28px 24px; min-height: 200px; display: flex; flex-direction: column; justify-content: space-between; }
.tile-category-badge { position: absolute; top: 16px; right: 16px; padding: 6px 12px; border-radius: 20px; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; display: flex; align-items: center; gap: 6px; backdrop-filter: blur(10px); }
.tile-category-badge.public { background: rgba(16,185,129,0.25); color: #6ee7b7; border: 1px solid rgba(16,185,129,0.3); }
.tile-category-badge.private { background: rgba(99,102,241,0.25); color: #a5b4fc; border: 1px solid rgba(99,102,241,0.3); }
.tile-category-badge.wip { background: rgba(245,158,11,0.25); color: #fcd34d; border: 1px solid rgba(245,158,11,0.3); }
.badge-icon { font-size: 10px; }
.tile.has-subtiles::after { content: "\f0c9"; font-family: "Font Awesome 6 Free"; font-weight: 900; position: absolute; bottom: 20px; right: 20px; font-size: 20px; color: rgba(255,255,255,0.4); transition: all 0.2s ease; }
.tile.has-subtiles:hover::after { color: rgba(255,255,255,0.7); transform: scale(1.1); }
.tile-icon { font-size: 48px; margin-bottom: 16px; opacity: 0.95; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2)); display: block; color: #fff !important; }
.tile-icon i { display: inline-block; color: #fff !important; }
.tile-title { font-size: 17px; font-weight: 600; margin-bottom: 8px; line-height: 1.4; color: #fff; text-shadow: 0 1px 2px rgba(0,0,0,0.2); }
.sub-tiles-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 20px; }
.sub-tiles-grid .tile-content { min-height: 170px; padding: 24px 20px; }
.sub-tiles-grid .tile-icon { font-size: 40px; color: #fff !important; }
.sub-tiles-grid .tile-icon i { color: #fff !important; }
.sub-tiles-grid .tile-title { font-size: 15px; }
.empty-state { text-align: center; padding: 80px 20px; color: #94a3b8; grid-column: 1 / -1; }
.empty-state i { font-size: 72px; margin-bottom: 20px; opacity: 0.3; }
.empty-state p { font-size: 18px; margin: 0; font-weight: 500; }
.tile.hidden { display: none; }
@media (max-width: 1024px) { .main-groups-grid { grid-template-columns: repeat(3, 1fr); } }
@media (max-width: 768px) { .main-groups-grid { grid-template-columns: repeat(2, 1fr); } .tiles-grid { grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); } .page-title { font-size: 28px; } .controls-bar { position: static; width: 100%; margin-bottom: 24px; flex-direction: column; } .search-container { width: 100%; } .page-header { padding-top: 20px; } }
"""

(css_folder / "main.css").write_text(main_css, encoding="utf-8")
print("✅ CSS generated")

app_js = r"""const DEFAULT_ICON = "fa-solid fa-square";
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
"""

(scripts_folder / "app.js").write_text(app_js, encoding="utf-8")
print("✅ JavaScript generated")

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LTC Tunnels & Approaches - Information Hub</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" />
    <link rel="stylesheet" href="styles/main.css">
</head>
<body>

<button class="back-button" id="back-button">
    <i class="fa-solid fa-arrow-left"></i>
    Back
</button>

<div class="page-container">
    <div id="main-page" class="page active">
        <h1 class="page-title">LTC Tunnels & Approaches</h1>
        <p class="page-subtitle">Information Hub</p>
        <div class="main-groups-grid">
{group_tiles_html}        </div>
    </div>

    <div id="tiles-page" class="page">
        <div class="controls-bar">
            <div class="search-container">
                <i class="fa-solid fa-search search-icon"></i>
                <input type="text" id="tiles-search" class="search-input" placeholder="Search subjects...">
            </div>
            <div class="filter-dropdown">
                <button class="filter-button" id="filter-button">
                    <i class="fa-solid fa-filter"></i>
                    <span id="filter-label">All Categories</span>
                </button>
                <div class="filter-menu" id="filter-menu">
{filter_options_html}                </div>
            </div>
        </div>

        <div class="page-header">
            <h2 id="tiles-page-title">Subjects</h2>
            <p class="subtitle">Select a subject to view details</p>
        </div>

        <div class="tiles-grid" id="main-tiles-grid"></div>
    </div>

    <div id="subtiles-page" class="page">
        <div class="controls-bar">
            <div class="search-container">
                <i class="fa-solid fa-search search-icon"></i>
                <input type="text" id="subtiles-search" class="search-input" placeholder="Search documents...">
            </div>
            <div class="filter-dropdown">
                <button class="filter-button" id="filter-button-sub">
                    <i class="fa-solid fa-filter"></i>
                    <span id="filter-label-sub">All Categories</span>
                </button>
                <div class="filter-menu" id="filter-menu-sub">
{filter_options_html}                </div>
            </div>
        </div>

        <div class="page-header">
            <h2 id="subtiles-page-title">Related Documents</h2>
            <p class="subtitle">Requirements and deliverables</p>
        </div>

        <div class="sub-tiles-grid" id="sub-tiles-grid"></div>
    </div>
</div>

<script>
window.tilesData = {tiles_json};
</script>
<script src="scripts/app.js"></script>
</body>
</html>
"""

output_html_file.write_text(html, encoding="utf-8")
print("✅ HTML generated")

print("\n" + "="*50)
print("✅ HUB GENERATION COMPLETE")
print("="*50)
print(f"📁 Output directory: {script_dir}")
print(f"📄 index.html created")
print(f"📄 styles/main.css created")
print(f"📄 scripts/app.js created")
print("="*50)
