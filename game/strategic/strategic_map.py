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
        
        # Debug mode for terrain visualization
        self.debug_mode = False
        
        # Cache for highlighting possible moves
        self.possible_moves = []
        self.highlighted_hexes = []
        
    def render(self, screen: pygame.Surface):
        """Render the strategic map to the screen."""
        self.grid.draw(screen)
        
        # Draw terrain patterns if in debug mode
        if self.debug_mode:
            for hex_tile in self.grid.hexes:
                self._draw_terrain_pattern(screen, hex_tile)
        
        # Draw additional strategic elements (buildings, units, etc.)
        self._draw_strategic_elements(screen)
        
        # Draw highlighted hexes for possible moves
        self._draw_highlighted_hexes(screen)
        
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
    
    def _draw_highlighted_hexes(self, screen: pygame.Surface):
        """Draw highlighted hexes for possible moves."""
        for hex_coords in self.highlighted_hexes:
            hex_tile = self.grid.get_hex_at(hex_coords[0], hex_coords[1])
            if hex_tile and len(hex_tile.vertices) >= 6:
                # Draw a semi-transparent overlay for possible moves
                overlay_surface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
                highlight_color = (0, 255, 0, 100)  # Semi-transparent green
                pygame.draw.polygon(overlay_surface, highlight_color, hex_tile.vertices)
                screen.blit(overlay_surface, (0, 0))
    
    def set_highlighted_hexes(self, hex_coords_list):
        """Set which hexes to highlight (for possible moves)."""
        self.highlighted_hexes = hex_coords_list
    
    def clear_highlighted_hexes(self):
        """Clear all highlighted hexes."""
        self.highlighted_hexes = []
    
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
    
    def toggle_debug_mode(self):
        """Toggle debug mode for terrain visualization."""
        self.debug_mode = not self.debug_mode
    
    def _draw_terrain_pattern(self, screen, hex_tile):
        """Draw terrain-specific pattern on the hex tile."""
        import pygame
        import math
        
        # Define terrain-specific patterns
        terrain_patterns = {
            'woods': self._draw_woods_pattern,
            'hills': self._draw_hills_pattern,
            'mountains': self._draw_mountains_pattern,
            'water': self._draw_water_pattern,
            'swamp': self._draw_swamp_pattern,
        }
        
        # Get the appropriate pattern function
        pattern_func = terrain_patterns.get(hex_tile.terrain_type, None)
        if pattern_func:
            pattern_func(screen, hex_tile)
    
    def _draw_woods_pattern(self, screen, hex_tile):
        """Draw a tree pattern for woods terrain."""
        import pygame
        import math
        
        # Draw several small tree shapes
        center_x, center_y = hex_tile.center_x, hex_tile.center_y
        hex_size = self.hex_size // 3  # Smaller size for pattern
        
        # Draw 3 small trees in a pattern
        tree_positions = [
            (center_x - hex_size//2, center_y - hex_size//3),
            (center_x + hex_size//3, center_y + hex_size//4),
            (center_x, center_y - hex_size//1.5)
        ]
        
        for tree_x, tree_y in tree_positions:
            # Tree top (circle)
            pygame.draw.circle(screen, (34, 139, 34), (int(tree_x), int(tree_y)), hex_size//4)
            # Tree trunk (rectangle)
            trunk_rect = pygame.Rect(int(tree_x - hex_size//8), int(tree_y + hex_size//4), hex_size//4, hex_size//2)
            pygame.draw.rect(screen, (101, 67, 33), trunk_rect)
    
    def _draw_hills_pattern(self, screen, hex_tile):
        """Draw a hill pattern for hills terrain."""
        import pygame
        import math
        
        # Draw several hill-like shapes
        center_x, center_y = hex_tile.center_x, hex_tile.center_y
        hex_size = self.hex_size // 2  # Smaller size for pattern
        
        # Draw 2 hill shapes
        hill_positions = [
            (center_x - hex_size//3, center_y + hex_size//4),
            (center_x + hex_size//2, center_y)
        ]
        
        for hill_x, hill_y in hill_positions:
            # Draw an ellipse to represent a hill
            hill_rect = pygame.Rect(int(hill_x - hex_size//2), int(hill_y - hex_size//3), hex_size, hex_size//1.5)
            pygame.draw.ellipse(screen, (139, 69, 19), hill_rect)
    
    def _draw_mountains_pattern(self, screen, hex_tile):
        """Draw a mountain pattern for mountains terrain."""
        import pygame
        import math
        
        # Draw mountain peaks
        center_x, center_y = hex_tile.center_x, hex_tile.center_y
        hex_size = self.hex_size  # Use full hex size for mountain peaks
        
        # Draw a large 'M' to indicate mountains
        font = pygame.font.SysFont(None, int(hex_size * 1.5))
        text = font.render('M', True, (50, 50, 50))  # Dark gray color
        text_rect = text.get_rect(center=(int(center_x), int(center_y)))
        screen.blit(text, text_rect)
    
    def _draw_water_pattern(self, screen, hex_tile):
        """Draw a water pattern for water terrain."""
        import pygame
        import math
        
        # Draw wave-like curves
        center_x, center_y = hex_tile.center_x, hex_tile.center_y
        hex_size = self.hex_size // 3  # Smaller size for pattern
        
        # Draw several wave lines
        for i in range(3):
            y_offset = center_y - hex_size//2 + i * hex_size//3
            start_pos = (center_x - hex_size, y_offset)
            end_pos = (center_x + hex_size, y_offset)
            
            # Draw a wave line
            points = []
            for x in range(int(start_pos[0]), int(end_pos[0]), 5):
                y = y_offset + math.sin((x - center_x) / (hex_size/3)) * (hex_size/6)
                points.append((x, y))
            
            if len(points) > 1:
                pygame.draw.aalines(screen, (30, 144, 255), False, points, 2)
    
    def _draw_swamp_pattern(self, screen, hex_tile):
        """Draw a swamp pattern for swamp terrain."""
        import pygame
        import math
        
        # Draw a large 'S' to indicate swamps
        center_x, center_y = hex_tile.center_x, hex_tile.center_y
        hex_size = self.hex_size  # Use full hex size for pattern
        
        font = pygame.font.SysFont(None, int(hex_size * 1.5))
        text = font.render('S', True, (100, 100, 50))  # Dark olive color
        text_rect = text.get_rect(center=(int(center_x), int(center_y)))
        screen.blit(text, text_rect)