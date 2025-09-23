document.addEventListener('DOMContentLoaded', function() {
    const container = document.querySelector('.tile-container');
    if (!container) return;
    const tiles = Array.from(container.children);

    tiles
        .sort((a, b) => {
            const orderA = parseInt(a.getAttribute('data-order'), 10) || 0;
            const orderB = parseInt(b.getAttribute('data-order'), 10) || 0;
            return orderA - orderB;
        })
        .forEach(tile => container.appendChild(tile));
});

document.querySelectorAll('.tile').forEach(tile => {
    const mainLink = tile.querySelector('.tile-main');
    const closeButton = tile.querySelector('.close-button');

    mainLink.addEventListener('click', (e) => {
        e.preventDefault();
        // Close other expanded tiles
        document.querySelectorAll('.tile.expanded').forEach(expandedTile => {
            if (expandedTile !== tile) {
                expandedTile.classList.remove('expanded');
            }
        });
        tile.classList.toggle('expanded');
    });

    closeButton.addEventListener('click', () => {
        tile.classList.remove('expanded');
    });
});

// Close expanded tiles when clicking outside
document.addEventListener('click', (e) => {
    if (!e.target.closest('.tile')) {
        document.querySelectorAll('.tile.expanded').forEach(tile => {
            tile.classList.remove('expanded');
        });
    }
});