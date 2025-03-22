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

# Note editing variables
editing_note = False  # Are we currently editing a note?
editing_pos = None   # (x, y) position of the note being edited
note_text = ""       # Current text for the note being edited

# Debug logging function
def log_debug(message):
    """Print debug messages to console with timestamp"""
    current_time = time.strftime("%H:%M:%S", time.localtime())
    print(f"[{current_time}] {message}")

def reset_note_editing():
    """Reset note editing state to avoid lingering states"""
    global editing_note, editing_pos, note_text
    editing_note = False
    editing_pos = None
    note_text = ""

# Add reset call on module import to ensure clean state
reset_note_editing()

def handle_keyboard_input(keys, tiles, selected_tile_id, all_tiles):
    """Handle keyboard input for navigation, tile selection, and shortcuts"""
    global editing_note, editing_pos, note_text
    # Import settings module to access its camera variables
    import settings
    
    # If we're editing a note, handle text input differently
    if editing_note and editing_pos:
        return selected_tile_id
    
    # Handle arrow keys for camera movement
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        settings.camera_x -= scroll_speed / settings.zoom_level
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        settings.camera_x += scroll_speed / settings.zoom_level
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        settings.camera_y -= scroll_speed / settings.zoom_level
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        settings.camera_y += scroll_speed / settings.zoom_level
    
    # Spacebar to reset to origin
    if keys[pygame.K_SPACE]:
        settings.camera_x = 0 - GRID_WIDTH_TILES / 2
        settings.camera_y = 0 - GRID_HEIGHT_TILES / 2
        
        settings.status_message = "Centered on origin"
        settings.status_message_timer = 60  # 1 second at 60 FPS
    
    # Handle hotkeys for tile selection
    for tile_id, tile in all_tiles.items():
        if tile.hotkey and keys[getattr(pygame, f'K_{tile.hotkey}')]:
            selected_tile_id = tile_id
    
    # Return the (possibly) updated selected tile
    return selected_tile_id

def handle_mouse_motion(event, palette_rect, selected_tile_id=None, tiles=None):
    """Handle mouse movement events"""
    global drag_active, drag_start_x, drag_start_y, last_drag_time
    # Import settings module to access its camera variables
    import settings
    
    # Skip normal interaction if we're editing a note
    if editing_note:
        return
        
    # Set cursor appearance based on the selected tool
    if selected_tile_id == PIPETTE and event.pos[0] < GRID_WIDTH:
        # Change cursor to show pipette mode
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
    else:
        # Reset to default cursor
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        
    # Handle middle mouse drag for camera panning
    if drag_active and pygame.mouse.get_pressed()[1]:  # Middle mouse button held (index 1)
        # Calculate drag distance (scaled by drag sensitivity and zoom)
        drag_dist_x = (drag_start_x - event.pos[0]) / drag_sensitivity
        drag_dist_y = (drag_start_y - event.pos[1]) / drag_sensitivity
        
        # Update camera position
        settings.camera_x += drag_dist_x / (BASE_TILE_SIZE * settings.zoom_level)
        settings.camera_y += drag_dist_y / (BASE_TILE_SIZE * settings.zoom_level)
        
        # Record the time of this camera movement
        last_drag_time = time.time()
        
        # Update drag start position
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
    global drag_active, drag_start_x, drag_start_y, last_drag_time, editing_note, editing_pos, note_text
    import settings  # Import to access notes dictionary
    
    # Skip normal interaction if we're editing a note and this isn't a note confirmation
    if editing_note and event.button != 1:
        return
    
    # Middle mouse button press - start drag
    if event.button == 2:  # Middle mouse button pressed
        drag_active = True
        drag_start_x = event.pos[0]
        drag_start_y = event.pos[1]
        last_drag_time = time.time()
    
    # Middle mouse button release - end drag
    elif event.button == 2:  # Middle mouse button released        
        drag_active = False
    
    # Left or right mouse button in grid area
    elif (event.button == 1 or event.button == 3) and event.pos[0] < GRID_WIDTH:
        # Get the grid position
        grid_x, grid_y = screen_to_grid(event.pos[0], event.pos[1])
        cell_x, cell_y = grid_to_cell(grid_x, grid_y)
        cell_pos = (cell_x, cell_y)
        
        # If we're editing a note and this is a different position, save the current note first
        if editing_note and cell_pos != editing_pos and event.button == 1:
            if note_text.strip():  # Only save if there's actual text
                settings.notes[editing_pos] = note_text
                settings.status_message = f"Note saved at ({editing_pos[0]}, {editing_pos[1]})"
            else:  # If empty text, remove the note
                if editing_pos in settings.notes:
                    del settings.notes[editing_pos]
                settings.status_message = f"Empty note deleted at ({editing_pos[0]}, {editing_pos[1]})"
            settings.status_message_timer = 60
            editing_note = False
            editing_pos = None
            note_text = ""
            return
        
        # Handle right-click to delete notes
        if event.button == 3 and cell_pos in settings.notes:
            del settings.notes[cell_pos]
            settings.status_message = f"Note deleted at ({cell_x}, {cell_y})"
            settings.status_message_timer = 60
            return
        
        # Handle notes with left click when NOTE is selected
        if event.button == 1 and selected_tile_id == NOTE:
            # If already editing a note at this position, continue with text entry
            if editing_note and cell_pos == editing_pos:
                return
            
            # Start editing a new note or existing note
            editing_note = True
            editing_pos = cell_pos
            note_text = settings.notes.get(cell_pos, "")  # Get existing text or empty string
            
            # Make status message more visible and clear
            settings.status_message = f"EDITING NOTE at ({cell_x}, {cell_y}) - Type your text and press ENTER to save"
            settings.status_message_timer = 300  # Show for 5 seconds (300 frames at 60 FPS)
            
            return
        
        # If we're not handling notes specifically, proceed with normal interaction
        picked_tile = handle_mouse_interaction(event.pos, event.button, tiles, selected_tile_id)
        if picked_tile is not None:
            # Return the picked tile ID to change the selected tile
            return picked_tile
    
    return None  # No tile selection in input handler

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

def handle_mouse_interaction(pos, button, tiles, selected_tile_id):
    """Handle placing or removing tiles from the grid"""
    # Import settings to access status variables
    import settings
    
    # Get the grid coordinates of the mouse click
    grid_x, grid_y = screen_to_grid(pos[0], pos[1])
    cell_x, cell_y = grid_to_cell(grid_x, grid_y)
    
    # Check if clicking on the entrance tile - prevent modification
    if (cell_x, cell_y) == (0, 0):
        settings.status_message = "Can't modify the entrance tile at (0,0)"
        settings.status_message_timer = 180  # 3 seconds at 60 FPS
        return None
    
    # If pipette is selected and this is a left-click, try to pick up a tile
    if selected_tile_id == PIPETTE and button == 1:
        # Get the tile ID at the clicked location
        tile_id = grid.get((cell_x, cell_y), EMPTY)
        
        # Only allow picking up palette tiles
        if tile_id in tiles and tiles[tile_id].is_palette_tile:
            settings.status_message = f"Picked up: {tiles[tile_id].name}"
            settings.status_message_timer = 120  # 2 seconds at 60 FPS
            return tile_id
        else:
            settings.status_message = "Can't pick up this tile"
            settings.status_message_timer = 120
            return None
            
    # Left click - place selected tile
    elif button == 1:
        grid[(cell_x, cell_y)] = selected_tile_id
    # Right click - remove tile (set to empty)
    elif button == 3:
        if (cell_x, cell_y) in grid:
            grid[(cell_x, cell_y)] = EMPTY
            
    return None

def check_keys_modifiers(event, all_tiles=None):
    """Check for keyboard shortcuts with modifiers"""
    global editing_note, note_text, editing_pos
    import settings  # Import to access notes dictionary
    
    # If we're editing a note, handle text editing
    if editing_note:
        # Check for backspace
        if event.key == pygame.K_BACKSPACE:
            note_text = note_text[:-1]
            return True
            
        # Check for Enter key to finish editing
        if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
            # Save the note if there's text
            if note_text.strip():
                settings.notes[editing_pos] = note_text
                settings.status_message = f"NOTE SAVED at ({editing_pos[0]}, {editing_pos[1]})"
            else:
                # If empty text, remove the note
                if editing_pos in settings.notes:
                    del settings.notes[editing_pos]
                settings.status_message = f"Empty note deleted at ({editing_pos[0]}, {editing_pos[1]})"
            
            settings.status_message_timer = 180  # 3 seconds at 60 FPS
            editing_note = False
            editing_pos = None
            return True
            
        # Check for escape to cancel
        if event.key == pygame.K_ESCAPE:
            editing_note = False
            editing_pos = None
            note_text = ""
            settings.status_message = "NOTE EDITING CANCELED"
            settings.status_message_timer = 180  # 3 seconds at 60 FPS
            return True
            
        # Add normal characters to note
        if event.unicode and len(event.unicode) == 1 and ord(event.unicode) >= 32:
            note_text += event.unicode
            return True
            
        return True  # Block further key processing when editing
            
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