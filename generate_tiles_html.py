import requests
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

API_URL = "https://api.morta.io/v1/table/views/6dbab052-7c8c-4f6b-b4d8-595ec7d2794a/rows?size=1000"
API_TOKEN = os.getenv("API_TOKEN")
if not API_TOKEN:
    raise RuntimeError("API_TOKEN not set in .env")

# === OUTPUT PATHS ===
script_dir = Path(__file__).parent
css_folder = script_dir / "styles"
scripts_folder = script_dir / "scripts"
output_html_file = script_dir / "index.html"

# Create folders (if not exist)
css_folder.mkdir(parents=True, exist_ok=True)
scripts_folder.mkdir(parents=True, exist_ok=True)

# === FETCH DATA ===
headers = {
    'Accept': 'application/json',
    'Authorization': f'Bearer {API_TOKEN}',
    'Content-Type': 'application/json'
}

response = requests.get(API_URL, headers=headers)
if response.status_code != 200:
    raise RuntimeError(f"API request failed: {response.status_code} {response.text}")

json_data = response.json()
rows = [item.get('rowData') for item in json_data.get('data', []) if item.get('rowData')]
df = pd.DataFrame(rows)

if 'Tile_Id' in df.columns:
    df.rename(columns={'Tile_Id': 'id'}, inplace=True)

if 'order' in df.columns:
    df['order'] = pd.to_numeric(df['order'], errors='coerce').fillna(0).astype(int)

df['id'] = df['id'].astype(str)
if 'parent_id' in df.columns:
    df['parent_id'] = df['parent_id'].astype(str)

# === SPLIT TILES ===
main_tiles = df[df['type'] == 'tile'].sort_values('order')
sub_tiles = df[df['type'] == 'sub-tile'].sort_values(['parent_id', 'order'])

# === ICONS ===
default_icons = {
    'Master Information Delivery Plan': 'fa-regular fa-calendar-check',
    'Carbon Management': 'fa-solid fa-seedling',
    'Consents Register': 'fa-solid fa-landmark',
    'Temporary Works Register': 'fa-solid fa-helmet-safety',
    'Procurement Management': 'fa-solid fa-cart-shopping',
    'Digital Engineering Management': 'fa-solid fa-cube',
    'Programme Management': 'fa-regular fa-calendar-check',
    'Land Access': 'fa-solid fa-map-location-dot',
    'Information Standards': 'fa-solid fa-car-tunnel',
    'Monthly Progress Report': 'fa-solid fa-chart-area',
}

def get_icon(row):
    icon = row.get('icon')
    if icon and str(icon).strip():
        return icon
    return default_icons.get(row.get('title'), 'fa-solid fa-square')

# === BUILD HTML ===
html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MORTA Home Tiles</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <link rel="stylesheet" href="styles/main.css">
</head>
<body>
<div class="main-content">
    <button class='back-button' style='display:none;'>⬅️ Back</button>
    <div class="tile-container">
"""

for _, row in main_tiles.iterrows():
    tile_id = row['id']
    has_sub = tile_id in sub_tiles['parent_id'].values
    target = row.get('url', "#")
    html += f"""
        <div class="tile {row.get('colour', '')}" data-id="{tile_id}" data-has-sub="{str(has_sub).lower()}">
            <a href="{target}" target="_blank" {'onclick="return false;"' if has_sub else ''}>
                <i class="{get_icon(row)}"></i>
                <span>{row.get('title', '')}</span>
            </a>
        </div>
    """

html += "</div>"

for tile_id in main_tiles['id']:
    subs = sub_tiles[sub_tiles['parent_id'] == tile_id]
    if not subs.empty:
        html += f'<div class="sub-tiles-container" data-parent="{tile_id}" style="display:none;"><div class="sub-tiles">'
        for _, sub in subs.iterrows():
            html += f"""
                <div class="tile {sub.get('colour', '')}">
                    <a href="{sub.get('url','')}" target="_blank">
                        <i class="{get_icon(sub)}"></i>
                        <span>{sub.get('title','')}</span>
                    </a>
                </div>
            """
        html += "</div></div>"

html += """
<div class="legend">
    <span class="legend-item light-blue"></span> 🔓 Public&nbsp;&nbsp;
    <span class="legend-item blue"></span> 🔒 Private&nbsp;&nbsp;
    <span class="legend-item orange"></span> ⚒️ Work in Progress
</div>
</div> <!-- main-content -->

<script src="scripts/app.js"></script>
</body>
</html>
"""

# Write HTML file
output_html_file.write_text(html, encoding="utf-8")

print(f"✅ HTML generated at: {output_html_file.resolve()}")