import pygame
import math
from settings import *
from tiles import grid_to_cell, grid_to_screen

def draw_grid(surface, tiles, grid):
    """Draw the grid and all tiles on it"""
    # Clear the screen for grid drawing
    grid_rect = pygame.Rect(0, 0, GRID_WIDTH, GRID_HEIGHT)
    pygame.draw.rect(surface, BLACK, grid_rect)
    
    # Import settings directly to get the most up-to-date camera position
    import settings
    
    # Calculate visible tile range based on camera position
    tile_size = BASE_TILE_SIZE * settings.zoom_level
    visible_width = GRID_WIDTH / tile_size
    visible_height = GRID_HEIGHT / tile_size
    
    # Use floor and ceil to ensure we cover all visible tiles plus an extra tile in each direction
    min_x = math.floor(settings.camera_x - 1)
    min_y = math.floor(settings.camera_y - 1)
    max_x = math.ceil(settings.camera_x + visible_width + 1)
    max_y = math.ceil(settings.camera_y + visible_height + 1)
    
    # Draw origin with different color
    origin_x, origin_y = grid_to_screen(0, 0)
    pygame.draw.line(surface, WHITE, (origin_x, 0), (origin_x, GRID_HEIGHT), 2)
    pygame.draw.line(surface, WHITE, (0, origin_y), (GRID_WIDTH, origin_y), 2)
    
    # Draw placed tiles
    for grid_pos, tile_id in grid.items():
        if tile_id != EMPTY:  # Skip empty tiles
            # Get grid position
            grid_x, grid_y = grid_pos
            
            # Convert to screen coordinates (this will include floor operations)
            screen_x, screen_y = grid_to_screen(grid_x, grid_y)
            
            # Get tile size with consistent rounding
            drawn_tile_size = int(tile_size) + 1  # Add 1 to ensure no gaps
            
            # Draw the tile
            tile = tiles[tile_id]
            
            # Draw the tile image
            if tile.scaled_image:
                # Draw scaled tile image - this should already be sized correctly
                surface.blit(tile.scaled_image, (screen_x, screen_y))
            else:
                # If no image, draw a filled rectangle with the tile's color
                tile_rect = pygame.Rect(screen_x, screen_y, drawn_tile_size, drawn_tile_size)
                pygame.draw.rect(surface, tile.color, tile_rect)
                pygame.draw.rect(surface, GRAY, tile_rect, 1) 