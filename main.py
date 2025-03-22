#!/usr/bin/env python3
import pygame
import sys
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
    handle_mouse_interaction
)

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
                handle_mouse_button(event, all_tiles, selected_tile_id, palette_rect)
                
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
        
        # Update the display
        pygame.display.flip()
        
        # Limit to 60 FPS
        clock.tick(60)
        
    # Quit pygame before exiting
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 