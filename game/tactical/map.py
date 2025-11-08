"""
Tactical map system for Brothers of Eador.
Manages the hexagonal tactical grid and handles map-related operations.
"""
import pygame
from typing import Optional
from .grid import HexGrid


class TacticalMap:
    """Manages the tactical map for combat encounters."""
    
    def __init__(self, width: int = 20, height: int = 10, hex_size: int = 30):
        self.width = width  # 20 hexes long (horizontal)
        self.height = height  # 10 hexes high (vertical)
        self.hex_size = hex_size
        self.grid = HexGrid(width, height, hex_size)
        
    def render(self, screen: pygame.Surface):
        """Render the tactical map to the screen."""
        self.grid.draw(screen)
        
    def get_hex_at(self, q: int, r: int):
        """Get the hex tile at the specified coordinates."""
        return self.grid.get_hex_at(q, r)
        
    def get_neighbors(self, hex_tile):
        """Get neighboring hex tiles."""
        return self.grid.get_neighbors(hex_tile)
        
    def handle_click(self, pos: tuple):
        """Handle mouse click on the tactical map."""
        # For now, just return the hex that was clicked
        # In the future, this could implement ray-casting to find which hex was clicked
        return None
        
    def randomize_terrain(self):
        """Randomly assign terrain types to hexes."""
        import random
        terrain_types = ["plain", "hills", "woods", "swamp", "water"]
        
        for hex_tile in self.grid.hexes:
            hex_tile.terrain_type = random.choice(terrain_types)