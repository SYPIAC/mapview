import json
import os
import tkinter as tk
import tkinter.filedialog
from settings import *
from tiles import set_entrance_tile

def show_save_dialog():
    """Show a save file dialog and return the chosen file path"""
    # Create a root window and hide it
    root = tk.Tk()
    root.withdraw()
    
    # Show the save dialog
    file_path = tkinter.filedialog.asksaveasfilename(
        defaultextension=".dungeon",
        filetypes=[("Dungeon Map", "*.dungeon"), ("All Files", "*.*")],
        title="Save Dungeon Map"
    )
    
    root.destroy()
    return file_path

def show_load_dialog():
    """Show a load file dialog and return the chosen file path"""
    # Create a root window and hide it
    root = tk.Tk()
    root.withdraw()
    
    # Show the load dialog
    file_path = tkinter.filedialog.askopenfilename(
        defaultextension=".dungeon",
        filetypes=[("Dungeon Map", "*.dungeon"), ("All Files", "*.*")],
        title="Load Dungeon Map"
    )
    
    root.destroy()
    return file_path

def save_map(grid, camera_pos=None, zoom=None):
    """Save the map to a file"""
    global status_message, status_message_timer
    import settings
    
    # Get file path from dialog
    file_path = show_save_dialog()
    if not file_path:
        status_message = "Save cancelled."
        status_message_timer = 180  # 3 seconds at 60 FPS
        return
    
    try:
        # Create a copy of the grid without the entrance tile (since it's always at 0,0)
        grid_to_save = {str(k): v for k, v in grid.items() if k != (0, 0) and v != EMPTY}
        
        # Create data object with all map information
        map_data = {
            "grid": grid_to_save,
            "camera": {
                "x": settings.camera_x,
                "y": settings.camera_y
            },
            "zoom": settings.zoom_level
        }
        
        # Save to file
        with open(file_path, 'w') as f:
            json.dump(map_data, f)
        
        status_message = f"Map saved: {os.path.basename(file_path)}"
        status_message_timer = 180  # 3 seconds at 60 FPS
        
    except Exception as e:
        status_message = f"Error saving map: {str(e)}"
        status_message_timer = 300  # 5 seconds at 60 FPS

def load_map(tiles):
    """Load the map from a file"""
    global grid, status_message, status_message_timer
    import settings
    
    # Handle case when tiles is None (called from keyboard shortcut)
    if tiles is None:
        status_message = "Can't load without tile data. Use the button instead."
        status_message_timer = 180  # 3 seconds at 60 FPS
        return
    
    # Get file path from dialog
    file_path = show_load_dialog()
    if not file_path:
        status_message = "Load cancelled."
        status_message_timer = 180  # 3 seconds at 60 FPS
        return
    
    try:
        # Load data from file
        with open(file_path, 'r') as f:
            map_data = json.load(f)
        
        # Clear existing grid
        grid.clear()
        
        # Load grid data
        for pos_str, tile_id in map_data["grid"].items():
            # Convert string coordinates back to tuple
            x, y = eval(pos_str)
            grid[(x, y)] = tile_id
            
        # Restore camera position
        if "camera" in map_data:
            settings.camera_x = map_data["camera"]["x"]
            settings.camera_y = map_data["camera"]["y"]
        else:
            # Center on origin if no camera data
            settings.camera_x = 0 - GRID_WIDTH_TILES / 2
            settings.camera_y = 0 - GRID_HEIGHT_TILES / 2
            
        # Restore zoom level
        if "zoom" in map_data:
            settings.zoom_level = max(MIN_ZOOM, min(MAX_ZOOM, map_data["zoom"]))
            update_grid_dimensions()
            
            # Update scaled images for all tiles
            for tile in tiles.values():
                tile.update_scaled_images()
                
        # Add entrance tile
        set_entrance_tile(grid, tiles)
            
        status_message = f"Map loaded: {os.path.basename(file_path)}"
        status_message_timer = 180  # 3 seconds at 60 FPS
        
    except Exception as e:
        status_message = f"Error loading map: {str(e)}"
        status_message_timer = 300  # 5 seconds at 60 FPS 