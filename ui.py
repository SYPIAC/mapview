import pygame
import math
from settings import *
from tiles import grid_to_cell, grid_to_screen, screen_to_grid

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.action = action
        self.is_hovered = False
        self.hotkey_text = ""  # For Ctrl+S, Ctrl+L, etc.
        
    def set_hotkey_text(self, text):
        """Set the hotkey text to display next to button"""
        self.hotkey_text = text
    
    def draw(self, surface):
        # Draw button rectangle
        if self.is_hovered:
            pygame.draw.rect(surface, self.hover_color, self.rect)
        else:
            pygame.draw.rect(surface, self.color, self.rect)
        
        # Draw outline
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        
        # Render button text
        font = pygame.font.SysFont(None, 24)
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
        # Render hotkey text if present
        if self.hotkey_text:
            hotkey_surface = font.render(self.hotkey_text, True, DARK_GRAY)
            hotkey_rect = hotkey_surface.get_rect(midleft=(self.rect.right + 5, self.rect.centery))
            surface.blit(hotkey_surface, hotkey_rect)
    
    def update(self, mouse_pos):
        """Update hover state based on mouse position"""
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
    def handle_event(self, event):
        """Handle mouse click on button"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                self.action()
                return True
        return False

def draw_coordinates(surface, mouse_pos):
    """Draw the current grid coordinates at the top left"""
    grid_x, grid_y = screen_to_grid(mouse_pos[0], mouse_pos[1])
    cell_x, cell_y = grid_to_cell(grid_x, grid_y)
    
    font = pygame.font.SysFont(None, 24)
    text = f"Grid: ({cell_x}, {cell_y})"
    zoom_text = f"Zoom: {zoom_level:.2f}x"
    
    text_surface = font.render(text, True, WHITE)
    zoom_surface = font.render(zoom_text, True, WHITE)
    
    text_outline = font.render(text, True, BLACK)
    zoom_outline = font.render(zoom_text, True, BLACK)
    
    # Draw text with outline for visibility
    for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        surface.blit(text_outline, (10 + dx, 10 + dy))
        surface.blit(zoom_outline, (10 + dx, 30 + dy))
        
    surface.blit(text_surface, (10, 10))
    surface.blit(zoom_surface, (10, 30))

def draw_status_message(surface):
    """Draw the status message at the bottom of the screen"""
    if status_message and status_message_timer > 0:
        font = pygame.font.SysFont(None, 24)
        text_surface = font.render(status_message, True, WHITE)
        text_rect = text_surface.get_rect(bottomleft=(10, WINDOW_HEIGHT - 10))
        
        # Draw background for better visibility
        bg_rect = text_rect.inflate(20, 10)
        pygame.draw.rect(surface, DARK_GRAY, bg_rect)
        pygame.draw.rect(surface, BLACK, bg_rect, 2)
        
        surface.blit(text_surface, text_rect)

def draw_palette(surface, tiles, selected_tile_id):
    """Draw the tile palette on the right side of the screen"""
    palette_rect = pygame.Rect(GRID_WIDTH, 0, PALETTE_WIDTH, PALETTE_HEIGHT)
    pygame.draw.rect(surface, DARK_GRAY, palette_rect)
    
    # Draw palette title
    font = pygame.font.SysFont(None, 28)
    title_text = font.render("Palette", True, WHITE)
    surface.blit(title_text, (GRID_WIDTH + 10, 20))
    
    # Draw each available tile
    y_offset = 70
    tile_count = 0
    
    for tile_id, tile in tiles.items():
        # Skip non-palette tiles (like entrance)
        if not tile.is_palette_tile:
            continue
            
        # Draw tile selection outline
        position = (GRID_WIDTH + PALETTE_WIDTH // 2 - TILE_PREVIEW_SIZE // 2, y_offset)
        select_rect = pygame.Rect(position[0] - 5, position[1] - 5, 
                                TILE_PREVIEW_SIZE + 10, TILE_PREVIEW_SIZE + 10)
        
        # Highlight selected tile
        if tile_id == selected_tile_id:
            pygame.draw.rect(surface, GREEN, select_rect, 3)
        else:
            pygame.draw.rect(surface, WHITE, select_rect, 1)
        
        # Draw tile image or color
        if tile.original_image:
            tile_img = pygame.transform.scale(tile.original_image, (TILE_PREVIEW_SIZE, TILE_PREVIEW_SIZE))
            surface.blit(tile_img, position)
        else:
            tile_rect = pygame.Rect(position[0], position[1], TILE_PREVIEW_SIZE, TILE_PREVIEW_SIZE)
            pygame.draw.rect(surface, tile.color, tile_rect)
            pygame.draw.rect(surface, BLACK, tile_rect, 1)
        
        # Draw tile name
        name_font = pygame.font.SysFont(None, 24)
        name_text = name_font.render(tile.name, True, WHITE)
        name_pos = (GRID_WIDTH + PALETTE_WIDTH // 2 - name_text.get_width() // 2, 
                    y_offset + TILE_PREVIEW_SIZE + 5)
        surface.blit(name_text, name_pos)
        
        # Draw hotkey if available
        if tile.hotkey:
            hotkey_text = f"Key: {tile.hotkey}"
            hotkey_surface = name_font.render(hotkey_text, True, LIGHT_BLUE)
            hotkey_pos = (GRID_WIDTH + PALETTE_WIDTH // 2 - hotkey_surface.get_width() // 2, 
                        name_pos[1] + name_text.get_height() + 5)
            surface.blit(hotkey_surface, hotkey_pos)
            y_offset += name_text.get_height() + hotkey_surface.get_height() + TILE_PREVIEW_SIZE + 25
        else:
            y_offset += name_text.get_height() + TILE_PREVIEW_SIZE + 15
        
        tile_count += 1
    
    return palette_rect

def update_buttons_position():
    """Update buttons position based on window size"""
    global save_button, load_button
    
    # Position buttons at the bottom of the palette
    save_y = WINDOW_HEIGHT - 2 * (BUTTON_HEIGHT + BUTTON_MARGIN)
    load_y = WINDOW_HEIGHT - (BUTTON_HEIGHT + BUTTON_MARGIN)
    
    save_button = Button(
        GRID_WIDTH + PALETTE_WIDTH // 2 - BUTTON_WIDTH // 2,
        save_y,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
        "Save",
        GREEN,
        (100, 255, 100),  # Lighter green for hover
        BLACK,
        lambda: None  # Will be set properly in main.py
    )
    save_button.set_hotkey_text("(Ctrl+S)")
    
    load_button = Button(
        GRID_WIDTH + PALETTE_WIDTH // 2 - BUTTON_WIDTH // 2,
        load_y,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
        "Load",
        BLUE,
        (100, 100, 255),  # Lighter blue for hover
        WHITE,
        lambda: None  # Will be set properly in main.py
    )
    load_button.set_hotkey_text("(Ctrl+L)")
    
    return save_button, load_button 