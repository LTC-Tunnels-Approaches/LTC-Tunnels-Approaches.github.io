const tiles = [
    {
        title: "Google",
        url: "https://www.google.com",
        description: "Search the world's information, including webpages, images, videos and more."
    },
    {
        title: "GitHub",
        url: "https://www.github.com",
        description: "Where the world builds software."
    },
    {
        title: "MDN Web Docs",
        url: "https://developer.mozilla.org",
        description: "Resources for developers, by developers."
    },
    {
        title: "Stack Overflow",
        url: "https://stackoverflow.com",
        description: "A question and answer site for professional and enthusiast programmers."
    }
];

function createTile(tile) {
    const tileElement = document.createElement('div');
    tileElement.className = 'tile';
    
    const linkElement = document.createElement('a');
    linkElement.href = tile.url;
    linkElement.target = '_blank';
    
    const titleElement = document.createElement('h2');
    titleElement.textContent = tile.title;
    
    const descriptionElement = document.createElement('p');
    descriptionElement.textContent = tile.description;
    
    linkElement.appendChild(titleElement);
    linkElement.appendChild(descriptionElement);
    tileElement.appendChild(linkElement);
    
    return tileElement;
}

function renderTiles() {
    const tilesContainer = document.getElementById('tiles-container');
    tiles.forEach(tile => {
        const tileElement = createTile(tile);
        tilesContainer.appendChild(tileElement);
    });
}

document.addEventListener('DOMContentLoaded', renderTiles);