
(function() {
    const tilesData = window.LTC_TILES_DATA || [];
    const mainRoot = document.querySelector(".groups-container");
    const detailPanel = document.getElementById("detail-panel");
    const detailTitle = document.getElementById("detail-title");
    const detailSubtitle = document.getElementById("detail-subtitle");
    const detailContent = document.getElementById("detail-content");
    const backButton = document.getElementById("back-button");

    function findTileById(id) {
        return tilesData.find(t => t.id === id);
    }

    function findChildren(parentId) {
        return tilesData.filter(t => t.parent_id === parentId);
    }

    function renderSubPage(tileId) {
        const tile = findTileById(tileId);
        if (!tile) return;

        const children = findChildren(tileId);

        detailTitle.textContent = tile.title;
        detailSubtitle.textContent = "Requirements and deliverables";

        let html = "";

        if (tile.url) {
            html += `
                <p>
                    <a href="${tile.url}" target="_blank" rel="noopener">
                        Open main document
                    </a>
                </p>
            `;
        }

        if (children.length) {
            const subTiles = children.filter(c => c.type === "tile");
            const docTiles = children.filter(c => c.type === "link");

            html += `<div class="sub-page">`;

            if (subTiles.length) {
                html += `
                    <h3>Subjects</h3>
                    <div class="tiles-grid">
                `;
                for (const child of subTiles) {
                    html += `
                        <button class="tile-card" data-tile-id="${child.id}">
                            <div class="tile-card-icon">
                                <i class="${child.icon}"></i>
                            </div>
                            <div class="tile-card-content">
                                <div class="tile-card-title">${child.title}</div>
                            </div>
                        </button>
                    `;
                }
                html += `</div>`;
            }

            if (docTiles.length) {
                html += `
                    <h3>Related documents</h3>
                    <ul>
                `;
                for (const doc of docTiles) {
                    const href = doc.url || "#";
                    html += `
                        <li>
                            <a href="${href}" target="_blank" rel="noopener">
                                ${doc.title}
                            </a>
                        </li>
                    `;
                }
                html += `</ul>`;
            }

            html += `</div>`;
        } else {
            html += `
                <div class="detail-placeholder">
                    <p>No related subjects or documents.</p>
                </div>
            `;
        }

        detailContent.innerHTML = html;
    }

    function clearDetailPanel() {
        detailTitle.textContent = "Select a subject to view details";
        detailSubtitle.textContent = "Requirements and deliverables";
        detailContent.innerHTML = `
            <div class="detail-placeholder">
                <p>Select a subject from the main page to see more information.</p>
            </div>
        `;
    }

    function handleTileClick(event) {
        const button = event.target.closest(".tile-card");
        if (!button) return;
        const tileId = button.getAttribute("data-tile-id");
        if (!tileId) return;
        renderSubPage(tileId);
    }

    function handleBackClick() {
        clearDetailPanel();
    }

    function init() {
        if (mainRoot) {
            mainRoot.addEventListener("click", handleTileClick);
        }
        if (backButton) {
            backButton.addEventListener("click", handleBackClick);
        }
    }

    init();
})();
