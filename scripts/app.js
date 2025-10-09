document.addEventListener('DOMContentLoaded', () => {
    const mainContainer = document.querySelector('.tile-container');
    const subContainers = document.querySelectorAll('.sub-tiles-container');
    const backButton = document.querySelector('.back-button');

    document.querySelectorAll('.tile[data-has-sub="true"]').forEach(tile => {
        tile.addEventListener('click', e => {
            e.preventDefault();
            const tileId = tile.getAttribute('data-id');
            mainContainer.style.display = 'none';
            subContainers.forEach(c => c.style.display = 'none');
            const target = document.querySelector(`.sub-tiles-container[data-parent="${tileId}"]`);
            if (target) target.style.display = 'grid';
            backButton.style.display = 'block';
        });
    });

    backButton.addEventListener('click', () => {
        mainContainer.style.display = 'grid';
        subContainers.forEach(c => c.style.display = 'none');
        backButton.style.display = 'none';
    });
});
