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
    
    def __init__(self, width: int = 16, height: int = 10, hex_size: int = None,
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
        
        # Debug mode for terrain visualization
        self.debug_mode = False
        
    def render(self, screen: pygame.Surface):
        """Render the tactical map to the screen."""
        self.grid.draw(screen)
        
        # Draw terrain patterns if in debug mode
        if self.debug_mode:
            for hex_tile in self.grid.hexes:
                self._draw_terrain_pattern(screen, hex_tile)
        
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
        
        # Draw a large 'M' to indicate mountains
        center_x, center_y = hex_tile.center_x, hex_tile.center_y
        hex_size = self.hex_size  # Use full hex size for mountain peaks
        
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