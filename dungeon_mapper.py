import pygame
import sys
import os

# Initialize pygame
pygame.init()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
BROWN = (139, 69, 19)
LIGHT_BLUE = (173, 216, 230)

# Grid settings
TILE_SIZE = 40
GRID_WIDTH_TILES = 15  # Number of tiles visible horizontally (increased from 10 to 15)
GRID_HEIGHT_TILES = 15  # Number of tiles visible vertically (increased from 10 to 15)
GRID_WIDTH = GRID_WIDTH_TILES * TILE_SIZE
GRID_HEIGHT = GRID_HEIGHT_TILES * TILE_SIZE

# Palette settings
PALETTE_WIDTH = 100
PALETTE_HEIGHT = GRID_HEIGHT
TILE_PREVIEW_SIZE = 50

# Window settings
WINDOW_WIDTH = GRID_WIDTH + PALETTE_WIDTH
WINDOW_HEIGHT = GRID_HEIGHT
WINDOW_TITLE = "Dungeon Mapper"

# Camera settings
camera_x = 0  # Camera x position in tiles
camera_y = 0  # Camera y position in tiles
scroll_speed = 1  # How many tiles to scroll per key press
middle_mouse_drag = False
drag_start_x = 0
drag_start_y = 0
drag_sensitivity = 2.5  # Higher value = less sensitive (was implicitly 0.5)

# Create the game window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption(WINDOW_TITLE)

# Tile class to store tile information
class Tile:
    def __init__(self, id, name, image_path, hotkey, color=None):
        self.id = id
        self.name = name
        self.image_path = image_path
        self.hotkey = hotkey
        self.default_color = color
        self.image = None
        self.preview_image = None
    
    def load_image(self):
        # If the image exists, load it
        if os.path.exists(self.image_path):
            try:
                img = pygame.image.load(self.image_path)
                self.image = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
                self.preview_image = pygame.transform.scale(img, (TILE_PREVIEW_SIZE, TILE_PREVIEW_SIZE))
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
            
            # Scale for use in the game
            self.image = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
            self.preview_image = pygame.transform.scale(img, (TILE_PREVIEW_SIZE, TILE_PREVIEW_SIZE))
            return True
        
        return False

# Tile types
EMPTY = 0
WALL = 1
FLOOR = 2

# Define tiles
tiles = {
    WALL: Tile(WALL, "Wall", "tiles/wall.png", pygame.K_1, DARK_GRAY),
    FLOOR: Tile(FLOOR, "Floor", "tiles/floor.png", pygame.K_2, BROWN)
}

# Create the grid - use dictionary for infinite grid
# Keys are (x, y) tuples, values are tile IDs
grid = {}

# Load all tile images
def load_tile_images():
    for tile_id, tile in tiles.items():
        tile.load_image()

# Load tile images
load_tile_images()

# Currently selected tile type
selected_tile = WALL

# Convert screen coordinates to grid coordinates
def screen_to_grid(screen_x, screen_y):
    grid_x = screen_x // TILE_SIZE + camera_x
    grid_y = screen_y // TILE_SIZE + camera_y
    return grid_x, grid_y

# Convert grid coordinates to screen coordinates
def grid_to_screen(grid_x, grid_y):
    screen_x = (grid_x - camera_x) * TILE_SIZE
    screen_y = (grid_y - camera_y) * TILE_SIZE
    return screen_x, screen_y

def draw_grid():
    # Calculate visible range
    start_x = camera_x
    end_x = camera_x + GRID_WIDTH_TILES
    start_y = camera_y
    end_y = camera_y + GRID_HEIGHT_TILES
    
    # Draw all visible tiles
    for grid_y in range(start_y, end_y + 1):
        for grid_x in range(start_x, end_x + 1):
            # Get screen position
            screen_x, screen_y = grid_to_screen(grid_x, grid_y)
            rect = pygame.Rect(screen_x, screen_y, TILE_SIZE, TILE_SIZE)
            
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
    
    # Instructions
    instructions = [
        "Left click: Paint",
        "Right click: Erase",
        "Middle click drag: Scroll",
        "Arrow keys: Scroll",
        "Space: Return to origin",
        "Hotkeys: 1-2 Select tiles"
    ]
    
    y = y_position + 10
    for line in instructions:
        instr = font.render(line, True, BLACK)
        screen.blit(instr, (GRID_WIDTH + 10, y))
        y += 25

def draw_coordinates(mouse_pos):
    if mouse_pos[0] < GRID_WIDTH:
        grid_x, grid_y = screen_to_grid(mouse_pos[0], mouse_pos[1])
        text = f"({grid_x}, {grid_y})"
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
        
        # Left button: paint selected tile
        if button == 1:
            grid[(grid_x, grid_y)] = selected_tile
        # Right button: erase (set to empty)
        elif button == 3:
            if (grid_x, grid_y) in grid:
                del grid[(grid_x, grid_y)]
    
    # Check if interaction is within the palette
    elif x >= GRID_WIDTH and y < GRID_HEIGHT:
        # Only handle palette selection on mouse down, not on drag
        if button == 1:  # Left button only for palette selection
            y_position = 60
            for tile_id, tile in tiles.items():
                tile_rect = pygame.Rect(GRID_WIDTH + 25, y_position, TILE_PREVIEW_SIZE, TILE_PREVIEW_SIZE)
                if tile_rect.collidepoint(pos):
                    selected_tile = tile_id
                    break
                y_position += TILE_PREVIEW_SIZE + 30

def handle_keydown(key):
    global selected_tile, camera_x, camera_y
    
    # Handle tile selection hotkeys
    for tile_id, tile in tiles.items():
        if key == tile.hotkey:
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
    # Return to origin (0,0) with spacebar
    elif key == pygame.K_SPACE:
        camera_x = 0
        camera_y = 0

def handle_middle_mouse_drag(current_pos):
    global camera_x, camera_y, drag_start_x, drag_start_y
    
    # Calculate the difference in pixels
    dx = drag_start_x - current_pos[0]
    dy = drag_start_y - current_pos[1]
    
    # Calculate the difference in tiles with reduced sensitivity
    tile_dx = int(dx // (TILE_SIZE * drag_sensitivity))
    tile_dy = int(dy // (TILE_SIZE * drag_sensitivity))
    
    if tile_dx != 0 or tile_dy != 0:
        # Move the camera
        camera_x += tile_dx
        camera_y += tile_dy
        
        # Update the drag start position
        drag_start_x = current_pos[0]
        drag_start_y = current_pos[1]

# Main game loop
def main():
    global middle_mouse_drag, drag_start_x, drag_start_y
    
    running = True
    mouse_down = False
    current_button = 0
    last_grid_pos = None
    
    clock = pygame.time.Clock()
    
    while running:
        # Store mouse position for this frame
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Middle mouse button for dragging
                if event.button == 2:
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
                        current_grid_pos = (grid_x, grid_y)
                        
                        # Only update if we've moved to a new grid cell
                        if current_grid_pos != last_grid_pos:
                            handle_mouse_interaction(mouse_pos, current_button)
                            last_grid_pos = current_grid_pos
            elif event.type == pygame.KEYDOWN:
                handle_keydown(event.key)
        
        # Clear the screen
        screen.fill(BLACK)
        
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