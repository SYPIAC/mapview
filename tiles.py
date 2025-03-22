import os
import pygame
import math
from settings import *

class Tile:
    def __init__(self, id, name, img_path, color, hotkey=None, is_palette_tile=True):
        self.id = id
        self.name = name
        self.original_image = None
        self.color = color
        self.hotkey = hotkey
        self.scaled_image = None
        self.is_palette_tile = is_palette_tile  # Whether this tile appears in the palette
        
        # Load the image if it exists, otherwise use the color
        if os.path.exists(img_path):
            self.original_image = pygame.image.load(img_path).convert_alpha()
            self.update_scaled_images()
        
    def update_scaled_images(self):
        """Update images when zoom level changes"""
        if self.original_image:
            # Get the current zoom level directly from settings
            import settings
            current_zoom = settings.zoom_level
            
            # Add 1 to dimensions to prevent gaps between tiles
            current_tile_size = int(settings.BASE_TILE_SIZE * current_zoom) + 1
            self.scaled_image = pygame.transform.scale(
                self.original_image, 
                (current_tile_size, current_tile_size)
            )

# Define tile types
def load_tiles():
    tiles = {
        EMPTY: Tile(EMPTY, "Empty", "tiles/empty.png", BLACK, is_palette_tile=False),
        WALL: Tile(WALL, "Wall", "tiles/wall.png", BROWN, "1"),
        FLOOR: Tile(FLOOR, "Floor", "tiles/floor.png", LIGHT_BLUE, "2"),
        ENTRANCE: Tile(ENTRANCE, "Entrance", "tiles/entrance.png", RED, is_palette_tile=False)
    }
    return tiles

# Grid to Cell function
def grid_to_cell(grid_x, grid_y):
    """Convert floating grid coordinates to cell coordinates"""
    return math.floor(grid_x), math.floor(grid_y)

# Function to ensure entrance tile is at (0,0)
def set_entrance_tile(grid, tiles):
    """Place the entrance tile at (0,0) and ensure it cannot be removed"""
    grid[(0, 0)] = ENTRANCE
    # If the tile's image hasn't been loaded yet (first call), just return
    if not tiles[ENTRANCE].original_image:
        return

# Screen to grid coordinates conversion
def screen_to_grid(screen_x, screen_y):
    """Convert screen coordinates to grid coordinates"""
    # Get current settings directly for consistency
    import settings
    current_zoom = settings.zoom_level
    tile_size = settings.BASE_TILE_SIZE * current_zoom
    
    # Translate cursor position to grid position
    grid_x = (screen_x / tile_size) + settings.camera_x
    grid_y = (screen_y / tile_size) + settings.camera_y
    
    return grid_x, grid_y

# Grid to screen coordinates conversion
def grid_to_screen(grid_x, grid_y):
    """Convert grid coordinates to screen coordinates"""
    # Import settings directly for consistency
    import settings
    current_zoom = settings.zoom_level
    tile_size = settings.BASE_TILE_SIZE * current_zoom
    
    # Calculate screen position
    screen_x = (grid_x - settings.camera_x) * tile_size
    screen_y = (grid_y - settings.camera_y) * tile_size
    
    # Apply floor for consistent pixel positioning
    screen_x = math.floor(screen_x)
    screen_y = math.floor(screen_y)
    
    return screen_x, screen_y 