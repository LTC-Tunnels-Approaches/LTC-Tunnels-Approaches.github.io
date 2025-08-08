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