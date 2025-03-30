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
        self.is_note = id == NOTE  # Is this a note tile?
        self.note_overlay_img = None  # For storing the 'N' overlay image
        
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
        LEVER: Tile(LEVER, "Lever", "tiles/lever.png", (255, 215, 0), "3"),  # Gold color
        SPIKE_TRAP: Tile(SPIKE_TRAP, "Spike Trap", "tiles/spike_trap.png", (169, 169, 169), "4"),  # Dark gray
        HOLE: Tile(HOLE, "Hole", "tiles/hole.png", (47, 79, 79), "5"),  # Dark slate gray
        CHEST: Tile(CHEST, "Chest", "tiles/chest.png", (205, 133, 63), "6"),  # Peru brown
        HIDDEN_WALL: Tile(HIDDEN_WALL, "Hidden Wall", "tiles/hidden_wall.png", (105, 105, 105), "7"),  # Dim gray
        MIMIC: Tile(MIMIC, "Mimic", "tiles/mimic.png", (139, 69, 19), "8"),  # Saddle brown
        GEM_WALL: Tile(GEM_WALL, "Gem Wall", "tiles/gem_wall.png", (147, 112, 219), "9"),  # Medium purple
        GATE: Tile(GATE, "Gate", "tiles/gate.png", (184, 134, 11), "0"),  # Dark goldenrod
        TORCH_LIT: Tile(TORCH_LIT, "Torch (Lit)", "tiles/torch_lit.png", (255, 140, 0), "MINUS"),  # Dark orange
        TORCH_UNLIT: Tile(TORCH_UNLIT, "Torch (Unlit)", "tiles/torch_unlit.png", (128, 128, 128), "EQUALS"),  # Gray
        FOUNTAIN: Tile(FOUNTAIN, "Fountain", "tiles/fountain.png", (0, 191, 255), "LEFTBRACKET"),  # Deep sky blue
        NOTE: Tile(NOTE, "Note", "tiles/note.png", BLUE, "n"),  # Blue note tile
        PIPETTE: Tile(PIPETTE, "Pipette", "tiles/pipette.png", (255, 0, 255), "q"),  # Magenta pipette tool
        CRONE: Tile(CRONE, "Crone", "tiles/crone.png", (153, 51, 153), "c"),  # Purple-ish for crone
        DOOR: Tile(DOOR, "Door", "tiles/door.png", (139, 69, 19), "e"),  # Similar to brown for door
        THRONE: Tile(THRONE, "Throne", "tiles/throne.png", (128, 0, 128), "t"),  # Purple for throne
        BOSS: Tile(BOSS, "Boss", "tiles/boss.png", (178, 34, 34), "i"),  # Red-ish color for boss
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