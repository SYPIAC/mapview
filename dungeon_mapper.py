import pygame
import sys
import os
import math  # Import math module for floor function
import json
import tkinter as tk
from tkinter import filedialog

# Initialize pygame
pygame.init()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
BROWN = (139, 69, 19)
LIGHT_BLUE = (173, 216, 230)
GREEN = (50, 205, 50)
BLUE = (30, 144, 255)
RED = (220, 20, 60)

# Base settings
BASE_TILE_SIZE = 40
GRID_WIDTH_TILES = 15  # Number of tiles visible horizontally at default zoom
GRID_HEIGHT_TILES = 15  # Number of tiles visible vertically at default zoom

# Zoom settings
zoom_level = 1.0  # 1.0 is default, <1 is zoomed out, >1 is zoomed in
MIN_ZOOM = 0.15  # Shows about 100x100 tiles (15/0.15 = 100)
MAX_ZOOM = 1.5   # Shows about 10x10 tiles (15/1.5 = 10)
ZOOM_STEP = 0.1  # How much to change zoom per mouse wheel tick

# Calculated grid settings (updated when zoom changes)
TILE_SIZE = BASE_TILE_SIZE * zoom_level
GRID_WIDTH = int(GRID_WIDTH_TILES * BASE_TILE_SIZE)
GRID_HEIGHT = int(GRID_HEIGHT_TILES * BASE_TILE_SIZE)

# Palette settings
PALETTE_WIDTH = 100
PALETTE_HEIGHT = GRID_HEIGHT
TILE_PREVIEW_SIZE = 50

# Button settings
BUTTON_HEIGHT = 30
BUTTON_WIDTH = 80
BUTTON_MARGIN = 10

# Window settings
WINDOW_WIDTH = GRID_WIDTH + PALETTE_WIDTH
WINDOW_HEIGHT = GRID_HEIGHT
WINDOW_TITLE = "Dungeon Mapper"

# Camera settings
camera_x = 0 - GRID_WIDTH_TILES / 2  # Start with camera centered on (0,0)
camera_y = 0 - GRID_HEIGHT_TILES / 2  # Start with camera centered on (0,0)
scroll_speed = 1  # How many tiles to scroll per key press
middle_mouse_drag = False
drag_start_x = 0
drag_start_y = 0
drag_sensitivity = 2.5  # Higher value = less sensitive

# UI elements
save_button = None
load_button = None
status_message = ""
status_message_timer = 0

# Create the game window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption(WINDOW_TITLE)

# Tile class to store tile information
class Tile:
    def __init__(self, id, name, image_path, hotkey=None, color=None, is_palette_tile=True):
        self.id = id
        self.name = name
        self.image_path = image_path
        self.hotkey = hotkey
        self.default_color = color
        self.image = None
        self.preview_image = None
        self.base_image = None  # Store the original loaded image
        self.is_palette_tile = is_palette_tile  # Flag to indicate if tile appears in palette
    
    def load_image(self):
        # If the image exists, load it
        if os.path.exists(self.image_path):
            try:
                self.base_image = pygame.image.load(self.image_path)
                self.update_scaled_images()
                return True
            except pygame.error as e:
                print(f"Error loading image {self.image_path}: {e}")
        
        # If image doesn't exist or loading failed, create a default one
        if self.default_color:
            img = pygame.Surface((16, 16))
            img.fill(self.default_color)
            
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(self.image_path), exist_ok=True)
            
            # Save the default image
            pygame.image.save(img, self.image_path)
            
            # Store base image and scale for use in the game
            self.base_image = img
            self.update_scaled_images()
            return True
        
        return False
    
    def update_scaled_images(self):
        """Update the scaled images based on the current zoom level"""
        if self.base_image:
            # Add 1 pixel to dimensions to ensure no gaps between tiles
            current_tile_size = int(BASE_TILE_SIZE * zoom_level) + 1
            self.image = pygame.transform.scale(self.base_image, (current_tile_size, current_tile_size))
            # Preview image size doesn't change with zoom
            self.preview_image = pygame.transform.scale(self.base_image, (TILE_PREVIEW_SIZE, TILE_PREVIEW_SIZE))

# Button class for UI elements
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.is_hovered = False
        self.font = pygame.font.SysFont(None, 24)
    
    def draw(self, surface):
        # Determine button color based on hover state
        current_color = self.hover_color if self.is_hovered else self.color
        
        # Draw button background
        pygame.draw.rect(surface, current_color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)  # Add border
        
        # Draw button text
        text_surf = self.font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
    
    def click(self):
        if self.action:
            return self.action()
        return False

# Function to convert float grid coordinates to integer grid coordinates
# This ensures consistent grid snapping behavior for both positive and negative coordinates
def grid_to_cell(grid_x, grid_y):
    # Use math.floor for consistent behavior with negative numbers
    return math.floor(grid_x), math.floor(grid_y)

# Tile types
EMPTY = 0
WALL = 1
FLOOR = 2
ENTRANCE = 3  # Special entrance tile

# Define tiles
tiles = {
    WALL: Tile(WALL, "Wall", "tiles/wall.png", pygame.K_1, DARK_GRAY),
    FLOOR: Tile(FLOOR, "Floor", "tiles/floor.png", pygame.K_2, BROWN),
    ENTRANCE: Tile(ENTRANCE, "Entrance", "tiles/entrance.png", None, RED, False)  # Special entrance tile, not in palette
}

# Create the grid - use dictionary for infinite grid
# Keys are (x, y) tuples, values are tile IDs
grid = {}

# File operations for saving and loading
def show_save_dialog():
    """Show a save file dialog and return the selected path"""
    root = tk.Tk()
    root.withdraw()  # Hide the main tkinter window
    
    file_path = filedialog.asksaveasfilename(
        defaultextension=".dungeon",
        filetypes=[("Dungeon files", "*.dungeon"), ("All files", "*.*")],
        title="Save Dungeon Map"
    )
    root.destroy()
    return file_path

def show_load_dialog():
    """Show a load file dialog and return the selected path"""
    root = tk.Tk()
    root.withdraw()  # Hide the main tkinter window
    
    file_path = filedialog.askopenfilename(
        defaultextension=".dungeon",
        filetypes=[("Dungeon files", "*.dungeon"), ("All files", "*.*")],
        title="Load Dungeon Map"
    )
    root.destroy()
    return file_path

def save_map():
    """Save the current map to a file"""
    global status_message, status_message_timer
    
    # Convert grid data to serializable format
    # Since grid keys are tuples (x,y), convert them to strings for JSON
    grid_data = {}
    for pos, tile_id in grid.items():
        # Don't save the entrance tile - it's always at (0,0)
        if pos == (0, 0) and tile_id == ENTRANCE:
            continue
        grid_data[f"{pos[0]},{pos[1]}"] = tile_id
    
    # Prepare map data
    map_data = {
        "grid": grid_data,
        "camera": {
            "x": camera_x,
            "y": camera_y
        },
        "zoom": zoom_level
    }
    
    # Get file path from dialog
    file_path = show_save_dialog()
    if not file_path:
        status_message = "Save cancelled"
        status_message_timer = 120  # Show message for 2 seconds (60 fps * 2)
        return False
    
    try:
        with open(file_path, 'w') as f:
            json.dump(map_data, f, indent=2)
        status_message = f"Map saved: {os.path.basename(file_path)}"
        status_message_timer = 120
        return True
    except Exception as e:
        status_message = f"Error saving map: {str(e)}"
        status_message_timer = 180
        return False

def load_map():
    """Load a map from a file"""
    global grid, camera_x, camera_y, zoom_level, status_message, status_message_timer
    
    # Get file path from dialog
    file_path = show_load_dialog()
    if not file_path:
        status_message = "Load cancelled"
        status_message_timer = 120
        return False
    
    try:
        with open(file_path, 'r') as f:
            map_data = json.load(f)
        
        # Extract grid data (convert string keys back to tuple coordinates)
        grid_data = map_data.get("grid", {})
        new_grid = {}
        for pos_str, tile_id in grid_data.items():
            x, y = map(int, pos_str.split(","))
            new_grid[(x, y)] = tile_id
        
        # Add entrance tile at (0,0)
        new_grid[(0, 0)] = ENTRANCE
        
        # Update grid and center camera on entrance (0,0)
        grid = new_grid
        
        # Center camera on entrance
        camera_x = 0 - GRID_WIDTH_TILES / 2
        camera_y = 0 - GRID_HEIGHT_TILES / 2
        
        # Update zoom level if provided
        new_zoom = map_data.get("zoom", 1.0)
        if new_zoom != zoom_level:
            zoom_level = new_zoom
            update_grid_dimensions()
        
        status_message = f"Map loaded: {os.path.basename(file_path)}"
        status_message_timer = 120
        return True
    except Exception as e:
        status_message = f"Error loading map: {str(e)}"
        status_message_timer = 180
        return False

# Create UI buttons
def create_buttons():
    global save_button, load_button
    
    # Calculate positions for buttons
    save_x = GRID_WIDTH + (PALETTE_WIDTH - BUTTON_WIDTH * 2 - BUTTON_MARGIN) / 2
    load_x = save_x + BUTTON_WIDTH + BUTTON_MARGIN
    button_y = GRID_HEIGHT - BUTTON_HEIGHT * 2
    
    # Create buttons
    save_button = Button(save_x, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Save (Ctrl+S)", GREEN, (100, 255, 100), save_map)
    load_button = Button(load_x, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Load (Ctrl+L)", BLUE, (100, 100, 255), load_map)

# Load all tile images
def load_tile_images():
    for tile_id, tile in tiles.items():
        tile.load_image()

# Set the entrance tile at (0,0)
def set_entrance_tile():
    grid[(0, 0)] = ENTRANCE

# Load tile images
load_tile_images()

# Ensure entrance tile is at (0,0)
set_entrance_tile()

# Create UI buttons
create_buttons()

# Currently selected tile type
selected_tile = WALL

# Update all tile images when zoom changes
def update_all_tile_images():
    for tile in tiles.values():
        tile.update_scaled_images()

# Update grid dimensions based on zoom level
def update_grid_dimensions():
    global TILE_SIZE, GRID_WIDTH, GRID_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT, PALETTE_HEIGHT
    
    TILE_SIZE = BASE_TILE_SIZE * zoom_level
    GRID_WIDTH = int(GRID_WIDTH_TILES * BASE_TILE_SIZE)  # Keep screen size constant
    GRID_HEIGHT = int(GRID_HEIGHT_TILES * BASE_TILE_SIZE)
    PALETTE_HEIGHT = GRID_HEIGHT
    WINDOW_WIDTH = GRID_WIDTH + PALETTE_WIDTH
    WINDOW_HEIGHT = GRID_HEIGHT
    
    # Resize the window and update tile images
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    update_all_tile_images()
    
    # Recreate buttons for the new window size
    create_buttons()

# Convert screen coordinates to grid coordinates
def screen_to_grid(screen_x, screen_y):
    tile_size = BASE_TILE_SIZE * zoom_level
    grid_x = screen_x / tile_size + camera_x
    grid_y = screen_y / tile_size + camera_y
    return grid_x, grid_y

# Convert grid coordinates to screen coordinates
def grid_to_screen(grid_x, grid_y):
    tile_size = BASE_TILE_SIZE * zoom_level
    screen_x = (grid_x - camera_x) * tile_size
    screen_y = (grid_y - camera_y) * tile_size
    return screen_x, screen_y

def draw_grid():
    tile_size = BASE_TILE_SIZE * zoom_level
    
    # Calculate visible range (use float division for correct range)
    visible_tiles_x = GRID_WIDTH / tile_size
    visible_tiles_y = GRID_HEIGHT / tile_size
    
    # Include one extra tile in each direction to ensure coverage
    start_x = math.floor(camera_x) - 1
    end_x = math.ceil(camera_x + visible_tiles_x) + 1
    start_y = math.floor(camera_y) - 1
    end_y = math.ceil(camera_y + visible_tiles_y) + 1
    
    # Draw all visible tiles
    for grid_y in range(start_y, end_y + 1):
        for grid_x in range(start_x, end_x + 1):
            # Get screen position
            screen_x, screen_y = grid_to_screen(grid_x, grid_y)
            
            # Use floor for consistent positioning with no gaps
            x = math.floor(screen_x)
            y = math.floor(screen_y)
            
            # Add 1 to tile size to prevent gaps
            size = math.ceil(tile_size) + 1
            rect = pygame.Rect(x, y, size, size)
            
            # Skip tiles that are fully outside the visible area
            if (rect.right < 0 or rect.bottom < 0 or 
                rect.left > GRID_WIDTH or rect.top > GRID_HEIGHT):
                continue
            
            # Draw the tile if it exists in the grid
            if (grid_x, grid_y) in grid:
                tile_id = grid[(grid_x, grid_y)]
                screen.blit(tiles[tile_id].image, rect)
            else:
                # Draw empty tile (black)
                pygame.draw.rect(screen, BLACK, rect)

def draw_palette():
    # Draw palette background
    palette_rect = pygame.Rect(GRID_WIDTH, 0, PALETTE_WIDTH, PALETTE_HEIGHT)
    pygame.draw.rect(screen, LIGHT_BLUE, palette_rect)
    
    # Draw palette title
    font = pygame.font.SysFont(None, 24)
    title = font.render("Palette", True, BLACK)
    screen.blit(title, (GRID_WIDTH + 20, 20))
    
    # Draw tiles in palette
    y_position = 60
    for tile_id, tile in tiles.items():
        # Skip tiles that shouldn't appear in palette (like entrance)
        if not tile.is_palette_tile:
            continue
            
        # Draw tile preview
        tile_rect = pygame.Rect(GRID_WIDTH + 25, y_position, TILE_PREVIEW_SIZE, TILE_PREVIEW_SIZE)
        screen.blit(tile.preview_image, tile_rect)
        
        # Highlight selected tile
        if selected_tile == tile_id:
            pygame.draw.rect(screen, BLACK, tile_rect, 3)
        
        # Draw tile name and hotkey
        name_text = font.render(f"{tile.name} ({pygame.key.name(tile.hotkey)})", True, BLACK)
        screen.blit(name_text, (GRID_WIDTH + 20, y_position + TILE_PREVIEW_SIZE + 5))
        
        y_position += TILE_PREVIEW_SIZE + 30
    
    # Add entrance note
    entrance_note = font.render("Entrance at (0,0)", True, RED)
    screen.blit(entrance_note, (GRID_WIDTH + 10, y_position))
    
    # Instructions
    instructions = [
        "Left click: Paint",
        "Right click: Erase",
        "Middle click drag: Scroll",
        "Mouse wheel: Zoom in/out",
        "Arrow keys: Scroll",
        "Space: Return to origin",
        "Hotkeys: 1-2 Select tiles"
    ]
    
    y = y_position + 30
    for line in instructions:
        instr = font.render(line, True, BLACK)
        screen.blit(instr, (GRID_WIDTH + 10, y))
        y += 25
    
    # Draw zoom level
    zoom_text = font.render(f"Zoom: {zoom_level:.2f}x", True, BLACK)
    screen.blit(zoom_text, (GRID_WIDTH + 10, y))
    
    # Draw save/load buttons
    save_button.draw(screen)
    load_button.draw(screen)
    
    # Display status message if active
    if status_message and status_message_timer > 0:
        status_font = pygame.font.SysFont(None, 20)
        status_text = status_font.render(status_message, True, BLACK)
        status_y = save_button.rect.y - 25
        screen.blit(status_text, (GRID_WIDTH + 10, status_y))

def draw_coordinates(mouse_pos):
    if mouse_pos[0] < GRID_WIDTH:
        grid_x, grid_y = screen_to_grid(mouse_pos[0], mouse_pos[1])
        cell_x, cell_y = grid_to_cell(grid_x, grid_y)
        text = f"({cell_x}, {cell_y})"
        font = pygame.font.SysFont(None, 24)
        text_surface = font.render(text, True, WHITE)
        text_bg = pygame.Rect(10, 10, text_surface.get_width() + 10, text_surface.get_height() + 5)
        pygame.draw.rect(screen, BLACK, text_bg)
        screen.blit(text_surface, (15, 12))

def handle_mouse_interaction(pos, button):
    global selected_tile
    x, y = pos
    
    # Check if interaction is within the grid
    if x < GRID_WIDTH and y < GRID_HEIGHT:
        # Convert screen coordinates to grid coordinates
        grid_x, grid_y = screen_to_grid(x, y)
        # Convert to cell coordinates (integer grid coordinates)
        cell_x, cell_y = grid_to_cell(grid_x, grid_y)
        
        # Protect the entrance tile at (0,0)
        if (cell_x, cell_y) == (0, 0):
            return
        
        # Left button: paint selected tile
        if button == 1:
            grid[(cell_x, cell_y)] = selected_tile
        # Right button: erase (set to empty)
        elif button == 3:
            if (cell_x, cell_y) in grid:
                del grid[(cell_x, cell_y)]
    
    # Check if interaction is within the palette area
    elif x >= GRID_WIDTH and y < GRID_HEIGHT:
        # Check if a button was clicked
        if save_button.is_hovered:
            save_button.click()
        elif load_button.is_hovered:
            load_button.click()
        # Only handle palette selection on mouse down, not on drag
        elif button == 1:  # Left button only for palette selection
            y_position = 60
            for tile_id, tile in tiles.items():
                # Skip tiles that shouldn't appear in palette
                if not tile.is_palette_tile:
                    continue
                    
                tile_rect = pygame.Rect(GRID_WIDTH + 25, y_position, TILE_PREVIEW_SIZE, TILE_PREVIEW_SIZE)
                if tile_rect.collidepoint(pos):
                    selected_tile = tile_id
                    break
                y_position += TILE_PREVIEW_SIZE + 30

def handle_keydown(key, mods):
    global selected_tile, camera_x, camera_y
    
    # Handle Ctrl+S for save
    if key == pygame.K_s and mods & pygame.KMOD_CTRL:
        save_map()
        return
    
    # Handle Ctrl+L for load
    if key == pygame.K_l and mods & pygame.KMOD_CTRL:
        load_map()
        return
    
    # Handle tile selection hotkeys
    for tile_id, tile in tiles.items():
        if tile.hotkey and key == tile.hotkey:
            selected_tile = tile_id
            return
    
    # Handle arrow key navigation
    if key == pygame.K_LEFT:
        camera_x -= scroll_speed
    elif key == pygame.K_RIGHT:
        camera_x += scroll_speed
    elif key == pygame.K_UP:
        camera_y -= scroll_speed
    elif key == pygame.K_DOWN:
        camera_y += scroll_speed
    # Return to origin (0,0) with spacebar - center view
    elif key == pygame.K_SPACE:
        camera_x = GRID_WIDTH_TILES / 2
        camera_y = GRID_HEIGHT_TILES / 2

def handle_middle_mouse_drag(current_pos):
    global camera_x, camera_y, drag_start_x, drag_start_y
    
    # Calculate the difference in pixels
    dx = current_pos[0] - drag_start_x
    dy = current_pos[1] - drag_start_y
    
    # Use float division and explicit rounding for consistent behavior
    tile_dx = -int(round(dx / (BASE_TILE_SIZE * zoom_level * drag_sensitivity)))
    tile_dy = -int(round(dy / (BASE_TILE_SIZE * zoom_level * drag_sensitivity)))
    
    if tile_dx != 0 or tile_dy != 0:
        # Move the camera
        camera_x += tile_dx
        camera_y += tile_dy
        
        # Update the drag start position
        drag_start_x = current_pos[0]
        drag_start_y = current_pos[1]

def handle_mousewheel(y, pos):
    global zoom_level, camera_x, camera_y
    
    # Only handle zoom if mouse is over the grid
    if pos[0] >= GRID_WIDTH:
        return
    
    # Get the grid coordinates of the mouse cursor before zooming
    grid_x_before, grid_y_before = screen_to_grid(pos[0], pos[1])
    
    # Calculate new zoom level
    old_zoom = zoom_level
    if y > 0:  # Zoom in
        zoom_level = min(MAX_ZOOM, zoom_level + ZOOM_STEP)
    else:  # Zoom out
        zoom_level = max(MIN_ZOOM, zoom_level - ZOOM_STEP)
    
    # Don't continue if zoom didn't change
    if old_zoom == zoom_level:
        return
    
    # Update tile sizes and screen dimensions
    update_grid_dimensions()
    
    # Get the grid coordinates of the mouse cursor after zooming
    grid_x_after, grid_y_after = screen_to_grid(pos[0], pos[1])
    
    # Adjust camera to keep the point under the cursor at the same grid position
    camera_x += (grid_x_before - grid_x_after)
    camera_y += (grid_y_before - grid_y_after)

# Main game loop
def main():
    global middle_mouse_drag, drag_start_x, drag_start_y, status_message_timer
    
    running = True
    mouse_down = False
    current_button = 0
    last_grid_pos = None
    
    clock = pygame.time.Clock()
    
    while running:
        # Store mouse position for this frame
        mouse_pos = pygame.mouse.get_pos()
        
        # Update button hover states
        save_button.check_hover(mouse_pos)
        load_button.check_hover(mouse_pos)
        
        # Decrement status message timer
        if status_message_timer > 0:
            status_message_timer -= 1
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Mouse wheel events
                if event.button == 4:  # Scroll up
                    handle_mousewheel(1, mouse_pos)
                elif event.button == 5:  # Scroll down
                    handle_mousewheel(-1, mouse_pos)
                # Middle mouse button for dragging
                elif event.button == 2:
                    middle_mouse_drag = True
                    drag_start_x, drag_start_y = mouse_pos
                else:
                    mouse_down = True
                    current_button = event.button
                    handle_mouse_interaction(mouse_pos, current_button)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 2:
                    middle_mouse_drag = False
                else:
                    mouse_down = False
                    last_grid_pos = None
            elif event.type == pygame.MOUSEMOTION:
                if middle_mouse_drag:
                    handle_middle_mouse_drag(mouse_pos)
                elif mouse_down:
                    # Get current grid position
                    x, y = mouse_pos
                    if x < GRID_WIDTH and y < GRID_HEIGHT:
                        grid_x, grid_y = screen_to_grid(x, y)
                        cell_x, cell_y = grid_to_cell(grid_x, grid_y)
                        current_grid_pos = (cell_x, cell_y)
                        
                        # Only update if we've moved to a new grid cell
                        if current_grid_pos != last_grid_pos:
                            handle_mouse_interaction(mouse_pos, current_button)
                            last_grid_pos = current_grid_pos
            elif event.type == pygame.KEYDOWN:
                # Pass both the key and modifier state
                handle_keydown(event.key, pygame.key.get_mods())
        
        # Clear the screen
        screen.fill(BLACK)
        
        # Make sure entrance tile is always at (0,0)
        grid[(0, 0)] = ENTRANCE
        
        # Draw grid and palette
        draw_grid()
        draw_palette()
        
        # Draw coordinates of mouse position
        draw_coordinates(mouse_pos)
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 