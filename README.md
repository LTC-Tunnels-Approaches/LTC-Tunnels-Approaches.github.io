# MORTA Home Tiles App

A simple, responsive tile-based interface for accessing MORTA documents and tools. Built with HTML, CSS, and JavaScript...

## Structure

```
├── index.html              # Main HTML file
├── styles/
│   └── main.css           # CSS styling
├── scripts/
│   └── app.js            # JavaScript for tile ordering
```

## Features

- Responsive tile layout
- Color-coded tiles indicating document status:
  - 🔓 Light Blue: Public documents
  - 🔒 Blue: Private documents
  - ⚒️ Orange: Work in Progress
- Dynamic tile ordering using data-order attributes
- Hover effects for better user interaction

## How It Works

### Tile Configuration

Each tile is configured with:
- Title
- Link to MORTA document
- Icon (using Font Awesome)
- Status color (blue/light-blue/orange)
- Order number

Example tile structure:
```html
<div class="tile light-blue" data-order="1">
    <a href="[MORTA_LINK]" target="_blank">
        <i class="fa-regular fa-calendar-check"></i>
        <span>Document Title</span>
    </a>
</div>
```

### Styling

- Tiles are arranged in a 4-column grid
- Each tile is 140x140 pixels
- Colors indicate document status
- Hover effects provide visual feedback

### JavaScript Features

The `app.js` script handles:
- Automatic tile ordering based on data-order attributes
- Dynamic layout management

## Setup

1. Clone the repository
2. No build process required - static HTML/CSS/JS
3. Open `index.html` in a browser or deploy to GitHub Pages

## Dependencies

- Font Awesome (for icons)
- No other external dependencies required

## Customization

To add or modify tiles:
1. Copy an existing tile div from `index.html`
2. Update the following attributes:
   - `data-order`: Position in the grid
   - `href`: Link to MORTA document
   - `class`: Tile color (blue/light-blue/orange)
   - Icon class and title
