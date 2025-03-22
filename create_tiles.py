import os
import pygame
from settings import *

def create_tile_image(filename, color, symbol=None):
    """Create a tile image with the given color and optional symbol"""
    # Create surface with alpha channel
    surface = pygame.Surface((BASE_TILE_SIZE, BASE_TILE_SIZE), pygame.SRCALPHA)
    
    # Fill with main color
    pygame.draw.rect(surface, (*color, 255), (0, 0, BASE_TILE_SIZE, BASE_TILE_SIZE))
    
    # Add border
    pygame.draw.rect(surface, (0, 0, 0, 255), (0, 0, BASE_TILE_SIZE, BASE_TILE_SIZE), 1)
    
    # Add symbol if provided
    if symbol:
        font = pygame.font.SysFont(None, 32)
        text = font.render(symbol, True, (0, 0, 0, 255))
        text_rect = text.get_rect(center=(BASE_TILE_SIZE/2, BASE_TILE_SIZE/2))
        surface.blit(text, text_rect)
    
    # Save the image
    pygame.image.save(surface, filename)

def main():
    # Initialize pygame
    pygame.init()
    
    # Create tiles directory if it doesn't exist
    os.makedirs("tiles", exist_ok=True)
    
    # Create tile images
    tiles_data = [
        ("empty.png", BLACK),
        ("wall.png", BROWN),
        ("floor.png", LIGHT_BLUE),
        ("lever.png", (255, 215, 0), "L"),
        ("spike_trap.png", (169, 169, 169), "S"),
        ("hole.png", (47, 79, 79), "O"),
        ("chest.png", (205, 133, 63), "C"),
        ("hidden_wall.png", (105, 105, 105), "H"),
        ("mimic.png", (139, 69, 19), "M"),
        ("gem_wall.png", (147, 112, 219), "G"),
        ("gate.png", (184, 134, 11), "I"),
        ("torch_lit.png", (255, 140, 0), "T"),
        ("torch_unlit.png", (128, 128, 128), "t"),
        ("fountain.png", (0, 191, 255), "F"),
        ("entrance.png", RED, "E")
    ]
    
    for tile_data in tiles_data:
        filename = os.path.join("tiles", tile_data[0])
        if not os.path.exists(filename):
            if len(tile_data) == 3:
                create_tile_image(filename, tile_data[1], tile_data[2])
            else:
                create_tile_image(filename, tile_data[1])
            print(f"Created {filename}")
        else:
            print(f"Skipped existing {filename}")

if __name__ == "__main__":
    main() 