#!/usr/bin/env python3
import pygame
import sys
from settings import *
from tiles import load_tiles, set_entrance_tile, grid_to_cell
from ui import draw_coordinates, draw_status_message, draw_palette, update_buttons_position
from grid import draw_grid
from file_io import save_map, load_map
from input_handler import (
    handle_keyboard_input, 
    handle_mouse_motion, 
    handle_mouse_button,
    handle_mousewheel,
    check_keys_modifiers
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
    save_button.action = lambda: save_map(grid, (camera_x, camera_y), zoom_level)
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
                # Check if clicked on buttons
                if save_button.handle_event(event) or load_button.handle_event(event):
                    continue
                    
                # Otherwise handle grid or palette interaction
                palette_rect = pygame.Rect(GRID_WIDTH, 0, PALETTE_WIDTH, PALETTE_HEIGHT)
                new_selected = handle_mouse_button(event, all_tiles, selected_tile_id, palette_rect)
                if new_selected is not None:
                    selected_tile_id = new_selected
                    
            # Mouse wheel for zooming
            elif event.type == pygame.MOUSEWHEEL:
                handle_mousewheel(event)
                # Update all tile images after zoom change
                for tile in all_tiles.values():
                    tile.update_scaled_images()
                # Update buttons position after resize
                save_button, load_button = update_buttons_position()
                    
            # Support for older pygame versions (1.9.x) where mouse wheel is button 4/5
            elif event.type == pygame.MOUSEBUTTONDOWN and (event.button == 4 or event.button == 5):
                handle_mousewheel(event)
                # Update all tile images after zoom change
                for tile in all_tiles.values():
                    tile.update_scaled_images()
                # Update buttons position after resize
                save_button, load_button = update_buttons_position()
                    
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