"""
Tactical map system for Brothers of Eador.
Manages the hexagonal tactical grid and handles map-related operations.
"""
import pygame
from typing import Optional
from .grid import HexGrid
from ..core.terrain_manager import TerrainWeightManager, ConstraintValidator
from .biome_mapper import get_tactical_generator


class TacticalMap:
    """Manages the tactical map for combat encounters."""
    
    def __init__(self, width: int = 20, height: int = 10, hex_size: int = None,
                 strategic_terrain: str = "plain", custom_influence: float = None,
                 tactical_requirements: dict = None):
        from config.settings import HEX_SIZE
        # Use the default hex size from settings if not provided
        if hex_size is None:
            hex_size = HEX_SIZE
        self.width = width  # 20 hexes long (horizontal)
        self.height = height # 10 hexes high (vertical)
        self.hex_size = hex_size
        self.grid = HexGrid(width, height, hex_size, strategic_terrain, custom_influence, tactical_requirements)
        
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
        
    def randomize_terrain(self, strategic_terrain: str = "plain",
                         custom_influence: float = None,
                         tactical_requirements: dict = None):
        """Randomly assign terrain types to hexes based on strategic context."""
        from config.constants import TERRAIN_TYPES
        
        # Get the tactical generator
        tactical_generator = get_tactical_generator()
        
        # Generate terrain weights based on strategic context
        terrain_weights = tactical_generator.generate_for_strategic_hex(
            strategic_terrain=strategic_terrain,
            width=self.width,
            height=self.height,
            custom_influence=custom_influence,
            tactical_requirements=tactical_requirements
        )
        
        # Create a weight manager with the generated weights
        weight_manager = TerrainWeightManager(terrain_weights)
        
        # Generate terrain for each hex using the weighted system
        for hex_tile in self.grid.hexes:
            hex_tile.terrain_type = weight_manager.get_weighted_choice()