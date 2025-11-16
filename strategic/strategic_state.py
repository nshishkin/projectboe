"""
Strategic state manager for the strategic map layer.
Handles map rendering, hero movement, and strategic gameplay.
"""
import pygame
import math

from strategic.map_generator import generate_map, get_province_at
from strategic.hero import Hero
from strategic.input_handler import pixel_to_hex, hex_to_pixel
from data_definitions import TERRAIN_TYPES
from constants import (
    HEX_SIZE, MAP_ROWS, MAP_COLS, 
    BG_COLOR, WHITE, BLACK
)

class StrategicState:
    def __init__(self, screen):
        """
        Initialize strategic state with map and hero.
        
        Args:
            screen: Pygame display surface to render to
        """
        self.screen = screen
        self.map_grid = generate_map(MAP_ROWS, MAP_COLS)
        self.hero = Hero(0, 0)  # Start at top-left for now
        
        print(f"Strategic state initialized with {MAP_ROWS}x{MAP_COLS} map")
        # Debug: print all province centers
        # for row in self.map_grid:
        #     for province in row:
        #         center_x, center_y = hex_to_pixel(province.x, province.y)
        #         print(f"Province x{province.x},y{province.y},center is {center_x},{center_y}")
        
    def update(self):
        """Update strategic layer logic."""
        # Phase 2: Minimal logic
        # Phase 4+: Check for encounters, AI movement, etc.
        pass
        
    def _get_hex_corners(self, center_x: float, center_y: float) -> list[tuple[float, float]]:
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
            x = center_x + HEX_SIZE * math.cos(angle)
            y = center_y + HEX_SIZE * math.sin(angle)
            corners.append((x, y))
        return corners

    def _draw_province(self, province):
        """
        Draw a single province hexagon.
        
        Args:
            province: Province object to draw
        """
        # Get terrain color
        terrain_color = TERRAIN_TYPES[province.terrain_type]['color']
        
        # Get hex center position in pixels
        center_x, center_y = hex_to_pixel(province.x, province.y)
        # Get hexagon corner points
        corners = self._get_hex_corners(center_x, center_y)
        
        # Draw filled hexagon (terrain color)
        pygame.draw.polygon(self.screen, terrain_color, corners)
        
        # Draw hexagon border (black outline)
        pygame.draw.polygon(self.screen, BLACK, corners, 2)

    def _draw_hero(self):
        """Draw hero marker on current province."""
        # Get hero position in pixels
        center_x, center_y = hex_to_pixel(self.hero.x, self.hero.y)
        
        # Draw hero as white circle with black border
        pygame.draw.circle(self.screen, WHITE, (int(center_x), int(center_y)), 15)
        pygame.draw.circle(self.screen, BLACK, (int(center_x), int(center_y)), 15, 2)

    def render(self):
        """Render the strategic map and hero."""
        # Draw all provinces
        for row in self.map_grid:
            for province in row:
                self._draw_province(province)
        
        # Draw hero on top
        self._draw_hero()

    def handle_click(self, mouse_pos: tuple[int, int]):
        """
        Handle mouse click on the strategic map.
        
        Args:
            mouse_pos: Tuple of (x, y) mouse position in pixels
        """
        # Convert pixel position to hex grid coordinates
        grid_coords = pixel_to_hex(mouse_pos[0], mouse_pos[1])   
        if grid_coords:
            grid_x, grid_y = grid_coords
            
            # Check if click is within map bounds
            province = get_province_at(self.map_grid, grid_x, grid_y)
            
            if province:
                # Move hero to clicked province
                self.hero.move_to(grid_x, grid_y)
                print(f"Clicked province: {province.terrain_type} at ({grid_x}, {grid_y})")