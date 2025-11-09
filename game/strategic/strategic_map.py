"""
Strategic map system for Brothers of Eador.
Manages the hexagonal strategic grid and handles map-related operations.
"""

import pygame
from typing import Optional
from .strategic_hex import StrategicGrid
from .preset_manager import get_preset_manager
from ..core.terrain_manager import TerrainWeightManager, ConstraintValidator


class StrategicMap:
    """Manages the strategic map for campaign gameplay."""
    
    def __init__(self, width: int = 8, height: int = 8, hex_size: int = None, preset_name: str = "balanced"):
        from config.settings import PROVINCE_SIZE
        # Use the default hex size from settings if not provided
        if hex_size is None:
            hex_size = PROVINCE_SIZE
        self.width = width  # 8 hexes long (horizontal)
        self.height = height  # 8 hexes high (vertical)
        self.hex_size = hex_size
        self.grid = StrategicGrid(width, height, hex_size, preset_name)
        
    def render(self, screen: pygame.Surface):
        """Render the strategic map to the screen."""
        self.grid.draw(screen)
        
        # Draw additional strategic elements (buildings, units, etc.)
        self._draw_strategic_elements(screen)
        
    def _draw_strategic_elements(self, screen: pygame.Surface):
        """Draw strategic elements like buildings and units on the map."""
        for hex_tile in self.grid.hexes:
            # Draw building indicators if present
            if hex_tile.buildings:
                self._draw_buildings(screen, hex_tile)
            
            # Draw encounter indicators if present
            if hex_tile.encounters:
                self._draw_encounters(screen, hex_tile)
            
            # Draw ownership indicators
            if hex_tile.ownership:
                self._draw_ownership(screen, hex_tile)
    
    def _draw_buildings(self, screen: pygame.Surface, hex_tile):
        """Draw building indicators on a hex tile."""
        center_x, center_y = hex_tile.center_x, hex_tile.center_y
        
        # Draw a small icon for each building type
        for i, building in enumerate(hex_tile.buildings):
            if building['is_active']:
                # Different colors for different building types
                building_colors = {
                    'fort': (139, 0, 0),        # Dark red
                    'watchtower': (160, 82, 45), # Sienna
                    'barracks': (105, 105, 105), # Dim gray
                    'farm': (255, 215, 0),       # Gold
                    'mine': (47, 79, 79),        # Dark slate gray
                    'lumbermill': (139, 69, 19), # Saddle brown
                    'temple': (255, 255, 255),   # White
                    'market': (255, 165, 0)      # Orange
                }
                
                color = building_colors.get(building['type'], (255, 255, 255))
                
                # Draw building as a small square
                rect_size = 6
                offset_x = (i % 2) * 8 - 4  # Alternate positions
                offset_y = (i // 2) * 8 - 4
                
                building_rect = pygame.Rect(
                    center_x + offset_x - rect_size//2,
                    center_y + offset_y - rect_size//2,
                    rect_size, rect_size
                )
                pygame.draw.rect(screen, color, building_rect)
                pygame.draw.rect(screen, (0, 0, 0), building_rect, 1)  # Black border
    
    def _draw_encounters(self, screen: pygame.Surface, hex_tile):
        """Draw encounter indicators on a hex tile."""
        center_x, center_y = hex_tile.center_x, hex_tile.center_y
        
        # Draw an exclamation mark for encounters
        if hex_tile.has_encounters():
            # Draw red exclamation mark
            pygame.draw.circle(screen, (255, 0, 0), (int(center_x + 10), int(center_y - 10)), 4)
            pygame.draw.circle(screen, (255, 0, 0), (int(center_x + 10), int(center_y - 10)), 2)
    
    def _draw_ownership(self, screen: pygame.Surface, hex_tile):
        """Draw ownership indicators on a hex tile."""
        center_x, center_y = hex_tile.center_x, hex_tile.center_y
        
        # Different colors for different factions
        faction_colors = {
            'player': (0, 0, 255),      # Blue
            'enemy': (255, 0, 0),       # Red
            'neutral': (128, 128, 128), # Gray
            'ally': (0, 255, 0)         # Green
        }
        
        color = faction_colors.get(hex_tile.ownership, (255, 255, 255))
        
        # Draw small diamond for ownership
        diamond_points = [
            (center_x, center_y + 12),
            (center_x - 4, center_y + 8),
            (center_x, center_y + 4),
            (center_x + 4, center_y + 8)
        ]
        pygame.draw.polygon(screen, color, diamond_points)
        pygame.draw.polygon(screen, (0, 0, 0), diamond_points, 1)  # Black border
    
    def get_hex_at(self, q: int, r: int):
        """Get the hex tile at the specified coordinates."""
        return self.grid.get_hex_at(q, r)
        
    def get_neighbors(self, hex_tile):
        """Get neighboring hex tiles."""
        return self.grid.get_neighbors(hex_tile)
        
    def handle_click(self, pos: tuple):
        """Handle mouse click on the strategic map."""
        # Find which hex was clicked based on position
        for hex_tile in self.grid.hexes:
            # Check if the click position is inside this hex
            # Simple distance check to hex center
            distance = ((pos[0] - hex_tile.center_x) ** 2 + (pos[1] - hex_tile.center_y) ** 2) ** 0.5
            if distance <= self.hex_size:
                return hex_tile
        return None
        
    def randomize_terrain(self, preset_name: str = "balanced"):
        """Randomly assign terrain types to hexes based on a preset."""
        from config.constants import TERRAIN_TYPES
        
        # Get the preset manager
        preset_manager = get_preset_manager()
        
        # Get the weight manager for the specified preset
        weight_manager = preset_manager.get_weight_manager_for_preset(preset_name)
        
        # Get constraints for the preset
        constraints = preset_manager.get_constraints_for_preset(preset_name)
        
        # Apply constraints to the weight manager
        weight_manager.apply_constraints(constraints)
        
        # Generate terrain for each hex using the weighted system
        for hex_tile in self.grid.hexes:
            hex_tile.terrain_type = weight_manager.get_weighted_choice()
        
        # Validate that constraints are satisfied
        validator = ConstraintValidator()
        if not validator.validate_hard_constraints(self.grid, constraints):
            # If constraints aren't met, try again (with a limit to prevent infinite loops)
            attempts = 0
            max_attempts = 10
            while not validator.validate_hard_constraints(self.grid, constraints) and attempts < max_attempts:
                for hex_tile in self.grid.hexes:
                    hex_tile.terrain_type = weight_manager.get_weighted_choice()
                attempts += 1