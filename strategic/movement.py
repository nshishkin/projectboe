"""
Movement and pathfinding utilities for strategic map.
Handles hex grid navigation and reachable cell calculation.
"""
from collections import deque
from config.constants import MAP_ROWS, MAP_COLS, TERRAIN_MOVEMENT_COSTS


def get_hex_neighbors(x: int, y: int) -> list[tuple[int, int]]:
    """
    Get 6 neighboring hexes for even-q vertical layout.
    Odd columns (x % 2 == 1) are shifted UP (y_offset is subtracted in rendering).

    Even columns (x % 2 == 0):
        - Neighbors: N(x,y-1), S(x,y+1), NW(x-1,y), NE(x+1,y), SW(x-1,y+1), SE(x+1,y+1)

    Odd columns (x % 2 == 1) - shifted up:
        - Neighbors: N(x,y-1), S(x,y+1), NW(x-1,y-1), NE(x+1,y-1), SW(x-1,y), SE(x+1,y)

    Args:
        x: Column on strategic map
        y: Row on strategic map

    Returns:
        List of valid neighbor coordinates within map bounds
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
            if 0 <= nx < MAP_COLS and 0 <= ny < MAP_ROWS]


def get_reachable_cells(start_x: int, start_y: int, movement_range: int, map_grid=None) -> dict[tuple[int, int], int]:
    """
    Calculate all cells reachable from start position within movement range.
    Uses BFS to find all cells within movement distance.

    Movement cost depends on terrain type (plains, forest, swamp, hills).

    Args:
        start_x: Starting column
        start_y: Starting row
        movement_range: Maximum movement points available
        map_grid: 2D array of Province objects (optional, if None uses cost 1 for all)

    Returns:
        Dictionary mapping (x, y) coordinates to movement cost from start
        Includes only reachable cells
    """
    # BFS queue: (x, y, movement_cost_from_start)
    queue = deque([(start_x, start_y, 0)])

    # Track visited cells and their movement costs
    visited = {(start_x, start_y): 0}

    while queue:
        x, y, cost = queue.popleft()

        # Don't expand beyond movement range
        if cost >= movement_range:
            continue

        # Check all neighbors
        for nx, ny in get_hex_neighbors(x, y):
            # Get terrain cost for this cell
            if map_grid is not None:
                terrain_type = map_grid[ny][nx].terrain_type
                move_cost = TERRAIN_MOVEMENT_COSTS.get(terrain_type, 1)
            else:
                move_cost = 1

            # Calculate new movement cost
            new_cost = cost + move_cost

            # Skip if too expensive or already visited with lower cost
            if new_cost > movement_range:
                continue
            if (nx, ny) in visited and visited[(nx, ny)] <= new_cost:
                continue

            # Mark as reachable and add to queue
            visited[(nx, ny)] = new_cost
            queue.append((nx, ny, new_cost))

    # Remove starting position from reachable cells
    if (start_x, start_y) in visited:
        del visited[(start_x, start_y)]

    return visited
