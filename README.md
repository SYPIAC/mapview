# Dungeon Mapper

A simple grid-based tool for mapping out dungeon layouts in video games.

## Features

- 10x10 grid for creating dungeon maps
- Wall and floor tiles with 16x16 graphics
- Simple palette for selecting tile types
- Left-click to paint, right-click to erase
- Drag mouse to paint/erase multiple tiles at once

## Requirements

- Python 3.6+
- Pygame library

## Installation

1. Make sure you have Python installed. If not, download and install it from [python.org](https://python.org).

2. Install Pygame using pip:
   ```
   pip install pygame
   ```

## Running the Application

To run the dungeon mapper, navigate to the project directory in your terminal and run:

```
python dungeon_mapper.py
```

## How to Use

- Select a tile type (wall or floor) from the palette on the right side
- Left-click on the grid to place the selected tile
- Right-click to erase tiles (set to empty)
- Click and drag to paint or erase multiple tiles at once

## Graphics

The application looks for tile images in the `tiles` folder. Default 16x16 pixel graphics for wall and floor tiles will be created only if they don't already exist.

You can add your own custom graphics by placing your images in the `tiles` folder with the following filenames:
- `wall.png` - For wall tiles
- `floor.png` - For floor tiles

The program will load your custom graphics on startup. Make sure your images are properly sized (recommended 16x16 pixels, but any size will be scaled to fit).

## Future Features

- Save/load maps
- Additional tile types
- Add notes to specific areas
- Export maps as images 