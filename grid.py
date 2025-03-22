import pygame
import math
from settings import *
from tiles import grid_to_cell, grid_to_screen, screen_to_grid

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
    
    # Draw note overlays (separate pass to ensure they're drawn on top)
    mouse_pos = pygame.mouse.get_pos()
    mouse_grid_x, mouse_grid_y = screen_to_grid(mouse_pos[0], mouse_pos[1])
    mouse_cell_x, mouse_cell_y = grid_to_cell(mouse_grid_x, mouse_grid_y)
    mouse_cell = (mouse_cell_x, mouse_cell_y)
    
    for grid_pos in settings.notes.keys():
        # Draw the note indicator
        grid_x, grid_y = grid_pos
        
        # Convert to screen coordinates
        screen_x, screen_y = grid_to_screen(grid_x, grid_y)
        
        # Draw 'N' indicator in the top-left corner
        font = pygame.font.SysFont(None, max(16, int(20 * settings.zoom_level)))
        note_label = font.render("N", True, BLUE)
        surface.blit(note_label, (screen_x + 2, screen_y + 2))
        
        # Draw note text popup when hovering over a note tile
        if grid_pos == mouse_cell and mouse_pos[0] < GRID_WIDTH:
            # Get note text
            note_text = settings.notes[grid_pos]
            
            # Calculate width for text wrapping
            max_popup_width = min(300, GRID_WIDTH - 40)  # Limit popup width
            
            # Create a list to store wrapped lines
            wrapped_lines = []
            
            # Create a font for measuring and rendering
            note_font = pygame.font.SysFont(None, 24)
            
            # Simple word-wrap algorithm
            words = note_text.split()
            current_line = ""
            
            for word in words:
                # Try adding the next word
                test_line = current_line + word + " "
                # Check if it would be too wide
                width, _ = note_font.size(test_line)
                
                if width <= max_popup_width:
                    current_line = test_line  # Still fits, keep going
                else:
                    if current_line:  # If we have text for this line, add it
                        wrapped_lines.append(current_line)
                        current_line = word + " "  # Start a new line with this word
                    else:
                        # Word is too long for the whole line, force add it
                        wrapped_lines.append(word + " ")
                        current_line = ""
            
            # Add the last line if it has content
            if current_line:
                wrapped_lines.append(current_line)
            
            # If there are no lines (empty text somehow), add an empty line
            if not wrapped_lines:
                wrapped_lines = [""]
            
            # Calculate popup dimensions
            line_height = note_font.get_height()
            popup_height = (len(wrapped_lines) * line_height) + 10  # padding
            
            # Calculate width based on the widest line
            widest_line_width = max(note_font.size(line)[0] for line in wrapped_lines)
            popup_width = widest_line_width + 20  # padding
            
            # Calculate position for note popup (adjust for different positions)
            popup_x = min(mouse_pos[0] + 15, GRID_WIDTH - popup_width - 10)
            popup_y = min(mouse_pos[1] + 15, GRID_HEIGHT - popup_height - 5)
            
            # Create popup background
            popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
            pygame.draw.rect(surface, DARK_GRAY, popup_rect)
            pygame.draw.rect(surface, BLUE, popup_rect, 2)
            
            # Draw each line of the note text
            for i, line in enumerate(wrapped_lines):
                note_surface = note_font.render(line, True, WHITE)
                line_y = popup_y + 5 + (i * line_height)  # 5px padding from top
                surface.blit(note_surface, (popup_x + 10, line_y))  # 10px padding from left 