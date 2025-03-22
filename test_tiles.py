#!/usr/bin/env python3
import pygame
import sys
from settings import *
from tiles import load_tiles, set_entrance_tile, grid_to_cell
from main import initialize

def create_test_pattern(grid, all_tiles):
    """Create a test pattern of tiles to check for gaps"""
    # Create a checkerboard pattern
    for x in range(-5, 6):
        for y in range(-5, 6):
            # Skip (0,0) as it will have the entrance tile
            if x == 0 and y == 0:
                continue
                
            # Alternating pattern
            if (x + y) % 2 == 0:
                grid[(x, y)] = WALL
            else:
                grid[(x, y)] = FLOOR
                
    print("Created test pattern with 121 tiles in a 11x11 grid around the entrance")

def main():
    """Initialize the game and create test pattern"""
    # Initialize pygame and load tiles
    pygame.init()
    init_screen()
    all_tiles = load_tiles()
    update_grid_dimensions()
    
    # Update all tile images
    for tile in all_tiles.values():
        tile.update_scaled_images()
    
    # Place entrance tile
    set_entrance_tile(grid, all_tiles)
    
    # Create the test pattern
    create_test_pattern(grid, all_tiles)
    
    print("\nTest created! Now run the main.py application to see the results.")
    print("Zoom in and out between levels 0.45 and 1.05 to check for gaps.")

if __name__ == "__main__":
    main() 