import pygame

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
drag_sensitivity = 2.5  # Higher value = less sensitive

# UI elements
save_button = None
load_button = None
status_message = ""
status_message_timer = 0

# Tile types
EMPTY = 0
WALL = 1
FLOOR = 2
ENTRANCE = 3  # Special entrance tile

# Create the grid - use dictionary for infinite grid
# Keys are (x, y) tuples, values are tile IDs
grid = {}

# Create the screen initially
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption(WINDOW_TITLE)

def init_screen():
    """Initialize the screen with the current dimensions"""
    global screen
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)

def update_grid_dimensions():
    """Update all dimension-related globals when zoom changes"""
    global TILE_SIZE, GRID_WIDTH, GRID_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT, PALETTE_HEIGHT, screen, zoom_level
    
    current_zoom = zoom_level  # Store in local variable to ensure we're using the correct value
    TILE_SIZE = BASE_TILE_SIZE * current_zoom
    
    GRID_WIDTH = int(GRID_WIDTH_TILES * BASE_TILE_SIZE)  # Keep screen size constant
    GRID_HEIGHT = int(GRID_HEIGHT_TILES * BASE_TILE_SIZE)
    PALETTE_HEIGHT = GRID_HEIGHT
    WINDOW_WIDTH = GRID_WIDTH + PALETTE_WIDTH
    WINDOW_HEIGHT = GRID_HEIGHT
    
    # Resize the window
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT)) 