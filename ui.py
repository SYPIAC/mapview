import pygame
import math
import settings
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
    
    # Import settings to get current zoom level
    import settings
    
    font = pygame.font.SysFont(None, 24)
    text = f"Grid: ({cell_x}, {cell_y})"
    zoom_text = f"Zoom: {settings.zoom_level:.2f}x"
    
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
    """Draw the tile palette on the right side of the screen with a scrollbar"""
    # Draw palette background
    palette_rect = pygame.Rect(GRID_WIDTH, 0, PALETTE_WIDTH, PALETTE_HEIGHT)
    pygame.draw.rect(surface, DARK_GRAY, palette_rect)
    
    # Draw palette title
    font = pygame.font.SysFont(None, 28)
    title_text = font.render("Palette", True, WHITE)
    surface.blit(title_text, (GRID_WIDTH + 10, 20))
    
    # Calculate tile preview size and spacing
    PREVIEW_SIZE = min(45, (PALETTE_WIDTH - 60) // 3)  # Slightly larger previews
    HORIZONTAL_SPACING = (PALETTE_WIDTH - (PREVIEW_SIZE * 3)) // 4  # Space between columns
    VERTICAL_SPACING = 15  # Increased space between rows
    ITEM_HEIGHT = PREVIEW_SIZE + 35  # Height of each tile including name and hotkey
    
    # Get list of palette tiles
    palette_tiles = [(id, tile) for id, tile in tiles.items() if tile.is_palette_tile]
    
    # Calculate total rows needed
    TILES_PER_ROW = 3
    total_rows = (len(palette_tiles) + TILES_PER_ROW - 1) // TILES_PER_ROW
    
    # Calculate visible area
    TITLE_HEIGHT = 50
    visible_height = PALETTE_HEIGHT - TITLE_HEIGHT
    rows_visible = (visible_height - VERTICAL_SPACING) // ITEM_HEIGHT
    
    # Store max scroll value in settings for other functions to use
    settings.max_palette_scroll = max(0, total_rows - rows_visible)
    
    # Scrollbar dimensions
    SCROLLBAR_WIDTH = 15
    scrollbar_height = min(visible_height, (visible_height * rows_visible) / total_rows)
    
    # Get/update scroll position (store in settings)
    if not hasattr(settings, 'palette_scroll'):
        settings.palette_scroll = 0
    settings.palette_scroll = min(settings.max_palette_scroll, settings.palette_scroll)
    
    # Draw tiles
    start_row = int(settings.palette_scroll)
    start_idx = start_row * TILES_PER_ROW
    visible_tiles = palette_tiles[start_idx:start_idx + (rows_visible * TILES_PER_ROW)]
    
    for idx, (tile_id, tile) in enumerate(visible_tiles):
        row = idx // TILES_PER_ROW
        col = idx % TILES_PER_ROW
        
        # Calculate position
        x = GRID_WIDTH + HORIZONTAL_SPACING + (col * (PREVIEW_SIZE + HORIZONTAL_SPACING))
        y = TITLE_HEIGHT + (row * ITEM_HEIGHT)
        
        # Draw selection outline
        select_rect = pygame.Rect(x - 2, y - 2, PREVIEW_SIZE + 4, PREVIEW_SIZE + 4)
        if tile_id == selected_tile_id:
            pygame.draw.rect(surface, GREEN, select_rect, 2)
        else:
            pygame.draw.rect(surface, WHITE, select_rect, 1)
        
        # Draw tile
        if tile.original_image:
            tile_img = pygame.transform.scale(tile.original_image, (PREVIEW_SIZE, PREVIEW_SIZE))
            surface.blit(tile_img, (x, y))
        else:
            tile_rect = pygame.Rect(x, y, PREVIEW_SIZE, PREVIEW_SIZE)
            pygame.draw.rect(surface, tile.color, tile_rect)
            pygame.draw.rect(surface, BLACK, tile_rect, 1)
        
        # Draw name
        name_font = pygame.font.SysFont(None, 20)
        name_text = name_font.render(tile.name, True, WHITE)
        name_x = x + (PREVIEW_SIZE - name_text.get_width()) // 2
        surface.blit(name_text, (name_x, y + PREVIEW_SIZE + 2))
        
        # Draw hotkey if available
        if tile.hotkey:
            hotkey_text = f"({tile.hotkey})"
            hotkey_surface = name_font.render(hotkey_text, True, LIGHT_BLUE)
            hotkey_x = x + (PREVIEW_SIZE - hotkey_surface.get_width()) // 2
            surface.blit(hotkey_surface, (hotkey_x, y + PREVIEW_SIZE + 2 + name_text.get_height()))
    
    # Draw scrollbar if needed
    if settings.max_palette_scroll > 0:
        scrollbar_x = GRID_WIDTH + PALETTE_WIDTH - SCROLLBAR_WIDTH - 5
        scrollbar_bg = pygame.Rect(scrollbar_x, TITLE_HEIGHT, SCROLLBAR_WIDTH, visible_height)
        pygame.draw.rect(surface, GRAY, scrollbar_bg)
        
        scroll_pos = TITLE_HEIGHT + (visible_height - scrollbar_height) * (settings.palette_scroll / settings.max_palette_scroll)
        scrollbar = pygame.Rect(scrollbar_x, scroll_pos, SCROLLBAR_WIDTH, scrollbar_height)
        pygame.draw.rect(surface, WHITE, scrollbar)
        
        # Store scrollbar rect for hit testing
        settings.scrollbar_rect = scrollbar
    else:
        settings.scrollbar_rect = None
    
    # Store palette layout information in settings for click detection
    settings.palette_layout = {
        'preview_size': PREVIEW_SIZE,
        'horizontal_spacing': HORIZONTAL_SPACING,
        'item_height': ITEM_HEIGHT,
        'title_height': TITLE_HEIGHT,
        'tiles_per_row': TILES_PER_ROW
    }
    
    return palette_rect

def handle_palette_scroll(event):
    """Handle scrolling in the palette area"""
    # Get current mouse position
    mouse_pos = pygame.mouse.get_pos()
    
    # Check if mouse is over palette area (excluding title)
    if (GRID_WIDTH <= mouse_pos[0] <= GRID_WIDTH + PALETTE_WIDTH and
        settings.palette_layout['title_height'] <= mouse_pos[1] <= PALETTE_HEIGHT):
        
        # Handle mousewheel event (Pygame 2.0+)
        if event.type == pygame.MOUSEWHEEL:
            if event.y > 0:  # Scroll up
                settings.palette_scroll = max(0, settings.palette_scroll - 0.5)
                return True
            elif event.y < 0:  # Scroll down
                settings.palette_scroll = min(
                    settings.max_palette_scroll,
                    settings.palette_scroll + 0.5
                )
                return True
        
        # Handle old-style mouse button events (Pygame 1.9.x)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Scroll up
                settings.palette_scroll = max(0, settings.palette_scroll - 0.5)
                return True
            elif event.button == 5:  # Scroll down
                settings.palette_scroll = min(
                    settings.max_palette_scroll,
                    settings.palette_scroll + 0.5
                )
                return True
    
    return False

def handle_palette_click(pos, tiles):
    """Handle clicking in the palette to select a tile"""
    # Get list of palette tiles
    palette_tiles = [(id, tile) for id, tile in tiles.items() if tile.is_palette_tile]
    
    # Get layout information from settings
    layout = settings.palette_layout
    
    # Calculate which column was clicked
    col_width = layout['preview_size'] + layout['horizontal_spacing']
    relative_x = pos[0] - GRID_WIDTH - layout['horizontal_spacing']
    col = int(relative_x // col_width)
    
    # Calculate which row was clicked
    relative_y = pos[1] - layout['title_height']
    row = int(relative_y // layout['item_height'])
    
    # Account for scroll position
    actual_row = row + int(settings.palette_scroll)
    
    # Calculate clicked index
    clicked_index = (actual_row * layout['tiles_per_row']) + col
    
    # Check if click is within valid bounds
    if (0 <= col < layout['tiles_per_row'] and  # Valid column
        relative_y >= 0 and  # Below title
        relative_x >= 0 and  # Right of grid
        relative_x <= col_width * layout['tiles_per_row'] and  # Within tile area
        clicked_index >= 0 and  # Valid index
        clicked_index < len(palette_tiles)):  # Within number of tiles
        return palette_tiles[clicked_index][0]
    
    return None

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