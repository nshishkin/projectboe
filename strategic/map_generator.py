"""
Map generator for creating the strategic hex map.
Generates a grid of provinces with random terrain types.
"""
import random

from strategic.province import Province
from config.data_definitions import TERRAIN_TYPES
from config.constants import MAP_ROWS, MAP_COLS

def generate_map(rows: int = MAP_ROWS, cols: int = MAP_COLS) -> list[list[Province]]:
    """
    Generate a strategic map as a 2D grid of provinces.
    
    Args:
        rows: Number of rows in the hex grid (default from constants)
        cols: Number of columns in the hex grid (default from constants)
    
    Returns:
        2D list of Province objects [row][col]
    """
    map_grid=[]
    terrain_keys=list(TERRAIN_TYPES.keys())

    for y in range(rows):
        row = []
        for x in range(cols):
            # Random terrain for each province
            terrain = random.choice(terrain_keys)
            province = Province(x, y, terrain)
            row.append(province)
        map_grid.append(row)
    
    return map_grid

def get_province_at(map_grid: list[list[Province]],x: int,y: int) -> Province | None:
    """
    Get province at specific grid coordinates.
    
    Args:
        map_grid: 2D list of provinces
        x: Column coordinate
        y: Row coordinate
    
    Returns:
        Province at (x, y) or None if out of bounds
    """
    if 0 <= y < len(map_grid) and 0 <= x < len(map_grid[0]):
        return map_grid[y][x]
    return None