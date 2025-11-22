"""
Input handler for converting mouse coordinates to hex grid positions.
Uses offset coordinate system for hexagons (strategic map).
"""
import math
from constants import MAP_OFFSET_X, MAP_OFFSET_Y, STRATEGIC_HEX_SIZE, MAP_COLS, MAP_ROWS

# Calculate hex dimensions from STRATEGIC_HEX_SIZE
HEX_WIDTH = STRATEGIC_HEX_SIZE * 2
HEX_HEIGHT = STRATEGIC_HEX_SIZE * math.sqrt(3)  # Height of hexagon


def pixel_to_hex(mouse_x: int, mouse_y: int) -> tuple[int, int] | None:
    """
    Convert pixel coordinates to hex grid coordinates.

    Uses offset coordinate system where odd rows are shifted right.
    Checks nearest hexes for accurate detection.

    Args:
        mouse_x: Mouse x position in pixels
        mouse_y: Mouse y position in pixels

    Returns:
        Tuple of (x, y) hex grid coordinates, or None if out of bounds
    """
    # Adjust for map offset
    x = mouse_x - MAP_OFFSET_X
    y = mouse_y - MAP_OFFSET_Y

    # Calculate approximate position
    row = int((y - HEX_HEIGHT/2) / (HEX_HEIGHT/2))
    x_offset = (HEX_WIDTH * 3/4) if row % 2 == 1 else 0
    col = int((x - x_offset) / (HEX_WIDTH * 1.5))

    # Generate list of candidate hexes (3x3 area around approximate position)
    candidates = [
        (col, row),
        (col-1, row), (col+1, row),
        (col, row-1), (col, row+1),
        (col-1, row-1), (col+1, row-1),
        (col-1, row+1), (col+1, row+1)
    ]

    # Find the closest hex center to mouse position
    min_dist = float('inf')
    best = None

    for c, r in candidates:
        # Check if coordinates are within map bounds
        if 0 <= c < MAP_COLS and 0 <= r < MAP_ROWS:
            center_x, center_y = hex_to_pixel(c, r)
            # Calculate squared distance (faster than sqrt)
            dist = (center_x - mouse_x)**2 + (center_y - mouse_y)**2
            if dist < min_dist:
                min_dist = dist
                best = (c, r)

    return best


def hex_to_pixel(grid_x: int, grid_y: int) -> tuple[int, int]:
    """
    Convert hex grid coordinates to pixel coordinates (center of hex).

    Args:
        grid_x: Column position on hex grid
        grid_y: Row position on hex grid

    Returns:
        Tuple of (x, y) pixel coordinates for hex center
    """
    # Odd rows are offset by 3/4 of hex width
    x_offset = (HEX_WIDTH * 3/4) if grid_y % 2 == 1 else 0

    # Horizontal spacing is 1.5 * width (hexes overlap!)
    pixel_x = MAP_OFFSET_X + grid_x * (HEX_WIDTH * 1.5) + x_offset + HEX_WIDTH / 2

    # Vertical spacing (adjusted for proper interlocking)
    pixel_y = MAP_OFFSET_Y + (HEX_HEIGHT/2) +  grid_y * (HEX_HEIGHT/2) 

    return (int(pixel_x), int(pixel_y))