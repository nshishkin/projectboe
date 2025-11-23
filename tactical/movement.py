"""
Movement and pathfinding utilities for tactical combat.
Handles hex grid navigation and reachable cell calculation.
"""
from collections import deque
from config.constants import BATTLEFIELD_ROWS, BATTLEFIELD_COLS


def get_hex_neighbors(x: int, y: int) -> list[tuple[int, int]]:
    """
    Get 6 neighboring hexes for even-q vertical layout.
    Odd columns (x % 2 == 1) are shifted UP (y_offset is subtracted in rendering).

    Even columns (x % 2 == 0):
        - Neighbors: N(x,y-1), S(x,y+1), NW(x-1,y), NE(x+1,y), SW(x-1,y+1), SE(x+1,y+1)

    Odd columns (x % 2 == 1) - shifted up:
        - Neighbors: N(x,y-1), S(x,y+1), NW(x-1,y-1), NE(x+1,y-1), SW(x-1,y), SE(x+1,y)

    Args:
        x: Column on battlefield
        y: Row on battlefield

    Returns:
        List of valid neighbor coordinates within battlefield bounds
    """
    if x % 2 == 0:  # Even column
        neighbors = [
            (x, y-1),      # N
            (x, y+1),      # S
            (x-1, y),      # NW
            (x+1, y),      # NE
            (x-1, y+1),    # SW
            (x+1, y+1)     # SE
        ]
    else:  # Odd column (shifted up)
        neighbors = [
            (x, y-1),      # N
            (x, y+1),      # S
            (x-1, y-1),    # NW
            (x+1, y-1),    # NE
            (x-1, y),      # SW
            (x+1, y)       # SE
        ]

    # Filter out-of-bounds neighbors
    return [(nx, ny) for nx, ny in neighbors
            if 0 <= nx < BATTLEFIELD_COLS and 0 <= ny < BATTLEFIELD_ROWS]


def get_reachable_cells(start_x: int, start_y: int, movement_range: int,
                        blocked_cells: set[tuple[int, int]]) -> dict[tuple[int, int], int]:
    """
    Calculate all cells reachable from start position within movement range.
    Uses BFS to find all cells within movement distance.

    Args:
        start_x: Starting column
        start_y: Starting row
        movement_range: Maximum movement distance (in hexes)
        blocked_cells: Set of (x, y) tuples representing occupied cells

    Returns:
        Dictionary mapping (x, y) coordinates to distance from start
        Includes only reachable cells, excludes blocked cells
    """
    # BFS queue: (x, y, distance_from_start)
    queue = deque([(start_x, start_y, 0)])

    # Track visited cells and their distances
    visited = {(start_x, start_y): 0}

    while queue:
        x, y, dist = queue.popleft()

        # Don't expand beyond movement range
        if dist >= movement_range:
            continue

        # Check all neighbors
        for nx, ny in get_hex_neighbors(x, y):
            # Skip if already visited or blocked
            if (nx, ny) in visited or (nx, ny) in blocked_cells:
                continue

            # Mark as reachable and add to queue
            new_dist = dist + 1
            visited[(nx, ny)] = new_dist
            queue.append((nx, ny, new_dist))

    # Remove starting position from reachable cells
    if (start_x, start_y) in visited:
        del visited[(start_x, start_y)]

    return visited


def find_path(start: tuple[int, int], goal: tuple[int, int],
              blocked_cells: set[tuple[int, int]]) -> list[tuple[int, int]] | None:
    """
    Find shortest path from start to goal using BFS.

    Args:
        start: Starting (x, y) coordinate
        goal: Target (x, y) coordinate
        blocked_cells: Set of occupied cells to avoid

    Returns:
        List of (x, y) coordinates from start to goal (excluding start),
        or None if no path exists
    """
    if goal in blocked_cells:
        return None

    # BFS queue: (x, y, path_to_here)
    queue = deque([(start[0], start[1], [])])
    visited = {start}

    while queue:
        x, y, path = queue.popleft()

        # Found goal
        if (x, y) == goal:
            return path + [(x, y)]

        # Check all neighbors
        for nx, ny in get_hex_neighbors(x, y):
            if (nx, ny) in visited or (nx, ny) in blocked_cells:
                continue

            visited.add((nx, ny))
            queue.append((nx, ny, path + [(x, y)]))

    return None
