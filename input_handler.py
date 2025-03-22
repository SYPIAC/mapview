import pygame
import math
import time
from settings import *
from tiles import grid_to_cell, screen_to_grid
from file_io import save_map, load_map

# Additional drag tracking variables
drag_active = False  # Flag to track if we're in an active drag
drag_start_x = 0     # Mouse X position when drag started
drag_start_y = 0     # Mouse Y position when drag started
last_drag_time = 0   # Time of the last drag update

# Debug logging function
def log_debug(message):
    """Print debug messages to console with timestamp"""
    current_time = time.strftime("%H:%M:%S", time.localtime())
    print(f"[{current_time}] {message}")

def handle_keyboard_input(keys, tiles, selected_tile_id, all_tiles):
    """Handle keyboard input for navigation, tile selection, and shortcuts"""
    global camera_x, camera_y, status_message, status_message_timer
    # Import settings module to access its camera variables
    import settings
    
    # Keep track of old camera position to detect changes
    old_camera_x = camera_x
    old_camera_y = camera_y
    moved = False
    
    # Handle arrow keys for camera movement
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        camera_x -= scroll_speed / zoom_level
        # Update settings module's camera position too
        settings.camera_x = camera_x
        moved = True
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        camera_x += scroll_speed / zoom_level
        # Update settings module's camera position too
        settings.camera_x = camera_x
        moved = True
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        camera_y -= scroll_speed / zoom_level
        # Update settings module's camera position too
        settings.camera_y = camera_y
        moved = True
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        camera_y += scroll_speed / zoom_level
        # Update settings module's camera position too
        settings.camera_y = camera_y
        moved = True
    
    # Spacebar to reset to origin
    if keys[pygame.K_SPACE]:
        camera_x = 0 - GRID_WIDTH_TILES / 2
        camera_y = 0 - GRID_HEIGHT_TILES / 2
        # Update settings module's camera position too
        settings.camera_x = camera_x
        settings.camera_y = camera_y
        
        status_message = "Centered on origin"
        status_message_timer = 60  # 1 second at 60 FPS
    
    # Handle hotkeys for tile selection
    for tile_id, tile in all_tiles.items():
        if tile.hotkey and keys[getattr(pygame, f'K_{tile.hotkey}')]:
            selected_tile_id = tile_id
    
    # Return the (possibly) updated selected tile
    return selected_tile_id

def handle_mouse_motion(event, palette_rect, selected_tile_id=None, tiles=None):
    """Handle mouse movement events"""
    global drag_active, drag_start_x, drag_start_y, camera_x, camera_y, last_drag_time
    # Import settings module to access its camera variables
    import settings
    
    # Handle middle mouse drag for camera panning
    if drag_active and pygame.mouse.get_pressed()[1]:  # Middle mouse button held (index 1)
        # Calculate drag distance (scaled by drag sensitivity and zoom)
        drag_dist_x = (drag_start_x - event.pos[0]) / drag_sensitivity
        drag_dist_y = (drag_start_y - event.pos[1]) / drag_sensitivity
        
        # Only update if there's actual movement (avoid tiny jumps)
        if abs(drag_dist_x) > 0.1 or abs(drag_dist_y) > 0.1:
            # Update camera position
            camera_x += drag_dist_x / (BASE_TILE_SIZE * zoom_level)
            camera_y += drag_dist_y / (BASE_TILE_SIZE * zoom_level)
            
            # Update settings module's camera position too
            settings.camera_x = camera_x
            settings.camera_y = camera_y
            
            # Record the time of this camera movement
            last_drag_time = time.time()
        
        # Always update drag start position
        drag_start_x = event.pos[0]
        drag_start_y = event.pos[1]
    
    # If the middle mouse button is not pressed anymore, end the drag
    elif drag_active and not pygame.mouse.get_pressed()[1]:
        drag_active = False
        
    # Drawing with left or right mouse button held down
    elif event.pos[0] < GRID_WIDTH:  # Only within grid area
        # Left button down - paint tiles
        if pygame.mouse.get_pressed()[0]:  # Left mouse button
            handle_mouse_interaction(event.pos, 1, tiles, selected_tile_id)
        # Right button down - erase tiles
        elif pygame.mouse.get_pressed()[2]:  # Right mouse button
            handle_mouse_interaction(event.pos, 3, tiles, None)

def handle_mouse_button(event, tiles, selected_tile_id, palette_rect):
    """Handle mouse button events"""
    global drag_active, drag_start_x, drag_start_y, camera_x, camera_y, last_drag_time
    
    # Check if inside the grid area (not palette)
    in_grid_area = event.pos[0] < GRID_WIDTH
    
    # Middle mouse button press - start drag
    if event.button == 2 and in_grid_area:  # Middle mouse button pressed
        drag_active = True
        drag_start_x = event.pos[0]
        drag_start_y = event.pos[1]
        last_drag_time = time.time()
    
    # Middle mouse button release - end drag
    elif event.button == 2:  # Middle mouse button released        
        # Always end the drag state regardless
        drag_active = False
    
    # Left or right mouse button
    elif (event.button == 1 or event.button == 3) and in_grid_area:  # Left or right mouse button
        handle_mouse_interaction(event.pos, event.button, tiles, selected_tile_id)
    
    # Handle clicking in the palette area
    elif event.button == 1 and palette_rect.collidepoint(event.pos):  # Left button in palette
        return handle_palette_click(event.pos, tiles)
        
    return selected_tile_id

def handle_mousewheel(event):
    """Handle mouse wheel for zooming"""
    # Import settings directly
    import settings
    
    # Get mouse position for zooming toward/away from cursor
    mouse_x, mouse_y = pygame.mouse.get_pos()
    
    # Only zoom if mouse is in the grid area (not on palette)
    if mouse_x >= GRID_WIDTH:
        return
    
    # Determine zoom direction
    zoom_in = False
    if hasattr(event, 'y'):
        # Pygame 2.0+ style
        zoom_in = event.y > 0
    elif hasattr(event, 'button'):
        # Pre-2.0 style (pygame 1.9.x)
        zoom_in = event.button == 4  # Scroll up = zoom in
    
    # Store old zoom level for calculations
    old_zoom = settings.zoom_level
    
    # Calculate new zoom level
    new_zoom = old_zoom
    if zoom_in:  # Zoom in
        new_zoom = min(settings.MAX_ZOOM, old_zoom + settings.ZOOM_STEP)
    else:  # Zoom out
        new_zoom = max(settings.MIN_ZOOM, old_zoom - settings.ZOOM_STEP)
    
    # If zoom level didn't change, exit early
    if new_zoom == old_zoom:
        return
    
    # Get grid coordinates under mouse cursor before zoom
    grid_x, grid_y = screen_to_grid(mouse_x, mouse_y)
    
    # Apply the new zoom level
    settings.zoom_level = new_zoom
    
    # Update all related dimensions
    settings.update_grid_dimensions()
    
    # Update the global zoom_level
    global zoom_level
    zoom_level = settings.zoom_level
    
    # Calculate where the same grid point would now appear on screen
    new_screen_x = (grid_x - settings.camera_x) * (settings.BASE_TILE_SIZE * new_zoom)
    new_screen_y = (grid_y - settings.camera_y) * (settings.BASE_TILE_SIZE * new_zoom)
    
    # Calculate the difference between where the point would appear and where we want it (under mouse)
    dx = new_screen_x - mouse_x
    dy = new_screen_y - mouse_y
    
    # Convert screen difference to grid units
    grid_dx = dx / (settings.BASE_TILE_SIZE * new_zoom)
    grid_dy = dy / (settings.BASE_TILE_SIZE * new_zoom)
    
    # Adjust camera by this difference to keep point under mouse
    settings.camera_x += grid_dx
    settings.camera_y += grid_dy
    
    # Update global camera positions to match settings
    global camera_x, camera_y
    camera_x = settings.camera_x
    camera_y = settings.camera_y

def handle_palette_click(pos, tiles):
    """Handle clicking in the palette to select a tile"""
    # Find which tile was clicked based on position
    y_offset = 70
    
    for tile_id, tile in tiles.items():
        # Skip non-palette tiles (like entrance)
        if not tile.is_palette_tile:
            continue
            
        # Calculate tile selection area
        position = (GRID_WIDTH + PALETTE_WIDTH // 2 - TILE_PREVIEW_SIZE // 2, y_offset)
        select_rect = pygame.Rect(position[0] - 5, position[1] - 5, 
                                TILE_PREVIEW_SIZE + 10, TILE_PREVIEW_SIZE + 10)
        
        if select_rect.collidepoint(pos):
            return tile_id
            
        # Update y_offset for next tile
        if tile.hotkey:
            # With hotkey takes more vertical space
            name_font = pygame.font.SysFont(None, 24)
            name_text = name_font.render(tile.name, True, WHITE)
            hotkey_text = f"Key: {tile.hotkey}"
            hotkey_surface = name_font.render(hotkey_text, True, LIGHT_BLUE)
            y_offset += name_text.get_height() + hotkey_surface.get_height() + TILE_PREVIEW_SIZE + 25
        else:
            name_font = pygame.font.SysFont(None, 24)
            name_text = name_font.render(tile.name, True, WHITE)
            y_offset += name_text.get_height() + TILE_PREVIEW_SIZE + 15
    
    # No tile was clicked, return current selection
    return None

def handle_mouse_interaction(pos, button, tiles, selected_tile_id):
    """Handle placing or removing tiles from the grid"""
    # Get the grid coordinates of the mouse click
    grid_x, grid_y = screen_to_grid(pos[0], pos[1])
    cell_x, cell_y = grid_to_cell(grid_x, grid_y)
    
    # Check if clicking on the entrance tile - prevent modification
    if (cell_x, cell_y) == (0, 0):
        global status_message, status_message_timer
        status_message = "Can't modify the entrance tile at (0,0)"
        status_message_timer = 180  # 3 seconds at 60 FPS
        return
    
    # Left click - place selected tile
    if button == 1:
        grid[(cell_x, cell_y)] = selected_tile_id
    # Right click - remove tile (set to empty)
    elif button == 3:
        if (cell_x, cell_y) in grid:
            grid[(cell_x, cell_y)] = EMPTY

def check_keys_modifiers(event, all_tiles=None):
    """Check for keyboard shortcuts with modifiers"""
    global status_message, status_message_timer
    
    # Check if ctrl key is pressed
    ctrl_pressed = pygame.key.get_mods() & (pygame.KMOD_CTRL | pygame.KMOD_META)
    
    # Ctrl+S for save
    if ctrl_pressed and event.key == pygame.K_s:
        save_map(grid, (camera_x, camera_y), zoom_level)
        return True
        
    # Ctrl+L for load
    if ctrl_pressed and event.key == pygame.K_l:
        load_map(all_tiles)  # Pass the tiles parameter
        return True
        
    return False 