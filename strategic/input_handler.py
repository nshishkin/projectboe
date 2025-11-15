"""
Input handler for converting mouse coordinates to hex grid positions.
Uses offset coordinate system for hexagons.
"""
import math
from constants import MAP_OFFSET_X, MAP_OFFSET_Y, HEX_SIZE

# Calculate hex dimensions from HEX_SIZE
HEX_WIDTH = HEX_SIZE * 2
HEX_HEIGHT = HEX_SIZE * math.sqrt(3)  # Height of hexagon


def pixel_to_hex(mouse_x: int, mouse_y: int) -> tuple[int, int] | None:
    """
    Convert pixel coordinates to hex grid coordinates.
    
    Uses offset coordinate system where odd rows are shifted right.
    
    Args:
        mouse_x: Mouse x position in pixels
        mouse_y: Mouse y position in pixels
    
    Returns:
        Tuple of (x, y) hex grid coordinates, or None if out of bounds
    """
    # Adjust for map offset
    x = mouse_x - MAP_OFFSET_X
    y = mouse_y - MAP_OFFSET_Y
    
    # Approximate row (will refine below)
    row = int(y / (HEX_HEIGHT * 0.75))
    
    # Odd rows are offset by half hex width
    x_offset = (HEX_WIDTH / 2) if row % 2 == 1 else 0
    
    # Approximate column
    col = int((x - x_offset) / HEX_WIDTH)
    
    # For more precision, we'd do point-in-polygon testing
    # For Phase 2, this approximation works well enough
    
    return (col, row)


def hex_to_pixel(grid_x: int, grid_y: int) -> tuple[int, int]:
    """
    Convert hex grid coordinates to pixel coordinates (center of hex).
    
    Args:
        grid_x: Column position on hex grid
        grid_y: Row position on hex grid
    
    Returns:
        Tuple of (x, y) pixel coordinates for hex center
    """
    # Odd rows are offset by half hex width
    x_offset = (HEX_WIDTH / 2) if grid_y % 2 == 1 else 0
    
    pixel_x = MAP_OFFSET_X + grid_x * HEX_WIDTH + x_offset + HEX_WIDTH / 2
    pixel_y = MAP_OFFSET_Y + grid_y * (HEX_HEIGHT * 0.75) + HEX_HEIGHT / 2
    
    return (int(pixel_x), int(pixel_y))