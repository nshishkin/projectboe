"""
Hexagonal grid geometry utilities for tactical combat.

Provides coordinate conversions and geometric calculations for even-q vertical layout hexagons.
"""
import math
from config.constants import (
    TACTICAL_HEX_SIZE, BATTLEFIELD_ROWS, BATTLEFIELD_COLS,
    BATTLEFIELD_OFFSET_X, BATTLEFIELD_OFFSET_Y
)


def calculate_hex_distance(x1: int, y1: int, x2: int, y2: int) -> int:
    """
    Calculate hex distance between two positions.

    Uses even-q vertical layout conversion to cube coordinates.

    Args:
        x1, y1: Starting position
        x2, y2: Ending position

    Returns:
        Distance in hexes
    """
    # Convert even-q offset to cube coordinates
    # For even-q: r = row - (col + (col & 1)) // 2
    q1 = x1
    r1 = y1 - (x1 + (x1 & 1)) // 2

    q2 = x2
    r2 = y2 - (x2 + (x2 & 1)) // 2

    # Cube distance
    distance = (abs(q1 - q2) + abs(r1 - r2) + abs(q1 + r1 - q2 - r2)) // 2

    return distance


def hex_to_pixel(grid_x: int, grid_y: int) -> tuple[int, int]:
    """
    Convert hex grid coordinates to pixel coordinates (center of hex).

    Uses even-q vertical layout (even columns offset upward).

    Args:
        grid_x: Column position on hex grid
        grid_y: Row position on hex grid

    Returns:
        Tuple of (pixel_x, pixel_y) for hex center
    """
    # # Hex dimensions for flat-top hexagons
    # # width = size * 2, height = size * sqrt(3)
    hex_width = TACTICAL_HEX_SIZE * 2
    hex_height = TACTICAL_HEX_SIZE * math.sqrt(3)

    # Odd rows are offset by height
    y_offset = (hex_height/2) if grid_x % 2 == 1 else 0

    # Horizontal spacing
    pixel_x = BATTLEFIELD_OFFSET_X + (grid_x+1) * (hex_width * 3/4) 

    # Vertical spacing (adjusted for proper interlocking)
    pixel_y = BATTLEFIELD_OFFSET_Y +  (grid_y+1) * hex_height - y_offset

    return (int(pixel_x), int(pixel_y))


def pixel_to_hex(mouse_x: int, mouse_y: int) -> tuple[int, int] | None:
    """
    Convert pixel coordinates to hex grid coordinates.

    Uses approximation + nearest neighbor search for even-q vertical layout.

    Args:
        mouse_x: Mouse X position in pixels
        mouse_y: Mouse Y position in pixels

    Returns:
        Tuple of (grid_x, grid_y) or None if outside battlefield
    """
    # Hex dimensions
    hex_width = TACTICAL_HEX_SIZE * 2
    hex_height = TACTICAL_HEX_SIZE * math.sqrt(3)
    horiz_spacing = hex_width * 0.75

    # Adjust for battlefield offset
    adjusted_x = mouse_x - BATTLEFIELD_OFFSET_X
    adjusted_y = mouse_y - BATTLEFIELD_OFFSET_Y

    # Approximate grid position
    approx_x = int((adjusted_x - TACTICAL_HEX_SIZE) / horiz_spacing)
    approx_y = int((adjusted_y - hex_height / 2) / hex_height)

    # Check this hex and neighbors (to handle edge cases near hex boundaries)
    candidates = []
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            check_x = approx_x + dx
            check_y = approx_y + dy

            # Bounds check
            if 0 <= check_x < BATTLEFIELD_COLS and 0 <= check_y < BATTLEFIELD_ROWS:
                # Calculate distance from mouse to hex center
                center_x, center_y = hex_to_pixel(check_x, check_y)
                dist = math.sqrt((mouse_x - center_x) ** 2 + (mouse_y - center_y) ** 2)
                candidates.append((dist, check_x, check_y))

    # Return closest hex
    if candidates:
        candidates.sort()  # Sort by distance
        _, grid_x, grid_y = candidates[0]

        # Final bounds check
        if 0 <= grid_x < BATTLEFIELD_COLS and 0 <= grid_y < BATTLEFIELD_ROWS:
            return grid_x, grid_y

    return None


def get_hex_corners(center_x: float, center_y: float) -> list[tuple[float, float]]:
    """
    Calculate 6 corner points of a hexagon.

    Args:
        center_x: X coordinate of hex center
        center_y: Y coordinate of hex center

    Returns:
        List of (x, y) tuples for the 6 corners
    """
    corners = []
    for i in range(6):
        angle = math.pi / 3 * i  # 60 degrees between each corner
        x = center_x + TACTICAL_HEX_SIZE * math.cos(angle)
        y = center_y + TACTICAL_HEX_SIZE * math.sin(angle)
        corners.append((x, y))
    return corners
