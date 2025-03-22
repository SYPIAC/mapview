#!/usr/bin/env python3
import pygame
import sys
import os
from settings import *
from tiles import load_tiles, set_entrance_tile, grid_to_cell
from ui import (
    draw_coordinates, 
    draw_status_message, 
    draw_palette, 
    update_buttons_position,
    handle_palette_scroll,
    handle_palette_click
)
from grid import draw_grid
from file_io import save_map, load_map
from input_handler import (
    handle_keyboard_input, 
    handle_mouse_motion, 
    handle_mouse_button,
    handle_mousewheel,
    check_keys_modifiers,
    handle_mouse_interaction,
    editing_note,
    note_text,
    editing_pos
)

def wrap_text(text, font, max_width):
    """Helper function to wrap text to a maximum width"""
    words = text.split()
    wrapped_lines = []
    current_line = ""
    
    for word in words:
        # Try adding the next word
        test_line = current_line + word + " "
        # Check if it would be too wide
        width, _ = font.size(test_line)
        
        if width <= max_width:
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
    
    # If there are no lines (empty note), create an empty line
    if not wrapped_lines:
        wrapped_lines = [""]
        
    return wrapped_lines

def fixed_update():
    """Update logic that happens every frame"""
    global status_message_timer
    
    # Decrease status message timer if active
    if status_message_timer > 0:
        status_message_timer -= 1

def initialize():
    """Initialize the game"""
    # Initialize pygame
    pygame.init()
    
    # Initialize screen
    init_screen()
    
    # Create note tile image if it doesn't exist
    note_path = "tiles/note.png"
    if not os.path.exists(note_path):
        # Create a transparent image with a blue 'N' label
        note_img = pygame.Surface((32, 32), pygame.SRCALPHA)
        # Draw small letter N in blue in the top-left corner
        font = pygame.font.SysFont(None, 20)
        n_label = font.render("N", True, BLUE)
        note_img.blit(n_label, (2, 2))
        # Save the image
        pygame.image.save(note_img, note_path)
    
    # Create pipette tile image if it doesn't exist
    pipette_path = "tiles/pipette.png"
    if not os.path.exists(pipette_path):
        # Create a transparent image with a pipette icon
        pipette_img = pygame.Surface((32, 32), pygame.SRCALPHA)
        # Draw a simple pipette shape
        pygame.draw.line(pipette_img, (255, 0, 255), (8, 24), (24, 8), 2)  # Pipette stem
        pygame.draw.circle(pipette_img, (255, 0, 255), (24, 8), 6)         # Pipette bulb
        pygame.draw.circle(pipette_img, (255, 255, 255), (24, 8), 4)       # Pipette inner bulb
        # Draw a small drop at the tip
        pygame.draw.circle(pipette_img, (0, 255, 255), (8, 24), 2)         # Cyan drop
        # Save the image
        pygame.image.save(pipette_img, pipette_path)
    
    # Load tiles
    all_tiles = load_tiles()
    
    # Update grid dimensions based on initial settings
    update_grid_dimensions()
    
    # Update all tile images
    for tile in all_tiles.values():
        tile.update_scaled_images()
    
    # Place entrance tile
    set_entrance_tile(grid, all_tiles)
    
    # Create buttons
    save_button, load_button = update_buttons_position()
    
    # Set button actions
    save_button.action = lambda: save_map(grid)
    load_button.action = lambda: load_map(all_tiles)
    
    return all_tiles, save_button, load_button

def main():
    """Main game loop"""
    # Initialize game
    all_tiles, save_button, load_button = initialize()
    
    # Create clock for limiting FPS
    clock = pygame.time.Clock()
    
    # Make the selected tile ID global so it can be accessed from mouse_motion handler
    global selected_tile_id
    selected_tile_id = WALL
    
    # Import once at the start to avoid reimporting every frame
    from input_handler import editing_note, note_text, editing_pos
    
    # Main game loop
    running = True
    while running:
        # Calculate mouse position
        mouse_pos = pygame.mouse.get_pos()
        
        # Update buttons
        save_button.update(mouse_pos)
        load_button.update(mouse_pos)
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            # Mouse movement
            elif event.type == pygame.MOUSEMOTION:
                # Create palette rect for reference
                palette_rect = pygame.Rect(GRID_WIDTH, 0, PALETTE_WIDTH, PALETTE_HEIGHT)
                # Handle mouse drag and motion
                handle_mouse_motion(event, palette_rect, selected_tile_id, all_tiles)
                
            # Mouse button events
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Create palette rect for reference
                palette_rect = pygame.Rect(GRID_WIDTH, 0, PALETTE_WIDTH, PALETTE_HEIGHT)
                
                # Check if clicked on buttons
                if save_button.handle_event(event) or load_button.handle_event(event):
                    continue
                    
                # Check for palette scrolling
                if handle_palette_scroll(event):
                    continue
                    
                # Check for palette tile selection
                if event.button == 1 and event.pos[0] >= GRID_WIDTH:  # Left click in palette area
                    new_selected = handle_palette_click(event.pos, all_tiles)
                    if new_selected is not None:
                        selected_tile_id = new_selected
                        continue
                
                # Handle all other mouse button events
                picked_tile = handle_mouse_button(event, all_tiles, selected_tile_id, palette_rect)
                if picked_tile is not None:
                    selected_tile_id = picked_tile
                    continue
                
            # Mouse button up events
            elif event.type == pygame.MOUSEBUTTONUP:
                # Create palette rect for reference
                palette_rect = pygame.Rect(GRID_WIDTH, 0, PALETTE_WIDTH, PALETTE_HEIGHT)
                # Handle button release
                handle_mouse_button(event, all_tiles, selected_tile_id, palette_rect)
                
            # Mouse wheel for zooming or palette scrolling
            elif event.type == pygame.MOUSEWHEEL:
                # If mouse is over palette area, handle palette scrolling
                if mouse_pos[0] >= GRID_WIDTH:
                    if handle_palette_scroll(event):
                        continue
                # Otherwise handle zooming
                else:
                    # Update zoom and dimensions first
                    handle_mousewheel(event)
                    # Then update all tile images
                    for tile in all_tiles.values():
                        tile.update_scaled_images()
                    
            # Support for older pygame versions (1.9.x) where mouse wheel is button 4/5
            elif event.type == pygame.MOUSEBUTTONDOWN and (event.button == 4 or event.button == 5):
                # If mouse is over palette area, handle palette scrolling
                if mouse_pos[0] >= GRID_WIDTH:
                    if handle_palette_scroll(event):
                        continue
                # Otherwise handle zooming
                else:
                    # Update zoom and dimensions first
                    handle_mousewheel(event)
                    # Then update all tile images
                    for tile in all_tiles.values():
                        tile.update_scaled_images()
                    
            # Keyboard shortcuts with modifiers
            elif event.type == pygame.KEYDOWN:
                if check_keys_modifiers(event, all_tiles):
                    continue
                
        # Handle keyboard input for navigation
        keys = pygame.key.get_pressed()
        selected_tile_id = handle_keyboard_input(keys, all_tiles, selected_tile_id, all_tiles)
        
        # Fixed update (timers, etc.)
        fixed_update()
        
        # Drawing
        screen.fill(BLACK)
        
        # Draw grid and tiles
        draw_grid(screen, all_tiles, grid)
        
        # Draw palette
        palette_rect = draw_palette(screen, all_tiles, selected_tile_id)
        
        # Draw UI elements
        draw_coordinates(screen, mouse_pos)
        draw_status_message(screen)
        
        save_button.draw(screen)
        load_button.draw(screen)
        
        # Ensure entrance tile is always at (0,0)
        set_entrance_tile(grid, all_tiles)
        
        # Re-import every frame to ensure we have the latest state
        from input_handler import editing_note, note_text, editing_pos
        
        # Display note editing status and current text if editing - DRAW LAST TO ENSURE VISIBILITY
        if editing_note and editing_pos is not None:
            # Draw a full-width notification bar at the top to indicate editing mode
            top_banner = pygame.Rect(0, 0, WINDOW_WIDTH, 30)
            pygame.draw.rect(screen, BLUE, top_banner)
            banner_font = pygame.font.SysFont(None, 24)
            banner_text = f"EDITING NOTE AT ({editing_pos[0]}, {editing_pos[1]})"
            banner_surface = banner_font.render(banner_text, True, WHITE)
            screen.blit(banner_surface, (10, 8))
            
            # Create a very prominent edit box with high contrast
            edit_font = pygame.font.SysFont(None, 24)
            
            # Make the text input area stand out more
            text_bg_rect = pygame.Rect(10, WINDOW_HEIGHT - 70, GRID_WIDTH - 20, 60)
            
            # Draw with high contrast
            pygame.draw.rect(screen, (0, 0, 80), text_bg_rect)  # Dark blue background
            pygame.draw.rect(screen, WHITE, text_bg_rect, 3)    # Thicker white outline
            
            # Add a prompt and make the text more visible
            prompt = "Note: "
            
            # Word wrap the text to fit in the edit box
            max_edit_width = text_bg_rect.width - 30  # Allow for padding
            
            # Add blinking cursor for edit feedback
            display_text = note_text
            if (pygame.time.get_ticks() // 500) % 2 == 0:
                display_text += "|"
                
            # Get wrapped text lines
            display_with_prompt = prompt + display_text
            wrapped_lines = wrap_text(display_with_prompt, edit_font, max_edit_width)
            
            # Only display the last two lines if there are more than 2
            # (since our edit box can comfortably fit 2 lines)
            if len(wrapped_lines) > 2:
                wrapped_lines = wrapped_lines[-2:]
            
            # Draw each line
            for i, line in enumerate(wrapped_lines):
                note_surface = edit_font.render(line, True, (255, 255, 100))  # Bright yellow text
                screen.blit(note_surface, (20, WINDOW_HEIGHT - 60 + (i * edit_font.get_height())))
            
            # Add a hint about saving
            hint_font = pygame.font.SysFont(None, 18)
            hint_text = "Press ENTER to save or ESC to cancel"
            hint_surface = hint_font.render(hint_text, True, (255, 255, 255))  # White text
            screen.blit(hint_surface, (20, WINDOW_HEIGHT - 25))
        
        # Update the display
        pygame.display.flip()
        
        # Limit to 60 FPS
        clock.tick(60)
        
    # Quit pygame before exiting
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 