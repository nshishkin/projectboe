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
    STRATEGIC_HEX_SIZE, MAP_ROWS, MAP_COLS,
    BG_COLOR, WHITE, BLACK, SCREEN_HEIGHT,
    BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_TEXT_COLOR,
    BUTTON_HEIGHT, BUTTON_BORDER_WIDTH
)

class StrategicState:
    def __init__(self, screen, game):
        """
        Initialize strategic state with map and hero.

        Args:
            screen: Pygame display surface to render to
            game: Reference to Game instance (for triggering combat)
        """
        self.screen = screen
        self.game = game
        self.map_grid = generate_map(MAP_ROWS, MAP_COLS)
        self.hero = Hero(0, 0)  # Start at top-left for now

        # Turn counter
        self.current_turn = 1

        # UI Buttons (positioned at bottom of screen)
        button_y = SCREEN_HEIGHT - BUTTON_HEIGHT - 10
        self.end_turn_button = pygame.Rect(50, button_y, 150, BUTTON_HEIGHT)
        self.start_combat_button = pygame.Rect(220, button_y, 180, BUTTON_HEIGHT)

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
            x = center_x + STRATEGIC_HEX_SIZE * math.cos(angle)
            y = center_y + STRATEGIC_HEX_SIZE * math.sin(angle)
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
        """Render the strategic map, hero, and UI."""
        # Draw all provinces
        for row in self.map_grid:
            for province in row:
                self._draw_province(province)

        # Draw hero on top
        self._draw_hero()

        # Draw UI (buttons and turn counter)
        self._draw_ui()

    def handle_click(self, mouse_pos: tuple[int, int]):
        """
        Handle mouse click on the strategic map or UI buttons.

        Args:
            mouse_pos: Tuple of (x, y) mouse position in pixels
        """
        # Check button clicks first
        if self._handle_button_click(mouse_pos):
            return  # Button was clicked, don't process map click

        # Convert pixel position to hex grid coordinates
        grid_coords = pixel_to_hex(mouse_pos[0], mouse_pos[1])
        if grid_coords:
            grid_x, grid_y = grid_coords

            # Check if click is within map bounds
            province = get_province_at(self.map_grid, grid_x, grid_y)

            if province:
                # Move hero to clicked province
                self.hero.move_to(grid_x, grid_y)
                print(f"Moved to {province.terrain_type} at ({grid_x}, {grid_y})")

    def _trigger_test_combat(self, province):
        """
        Trigger test combat (Phase 3 only).

        Phase 4+: Replace with proper encounter system.

        Args:
            province: Province where combat happens
        """
        # Test armies
        player_army = ['infantry', 'infantry', 'ranged']
        enemy_army = ['infantry', 'cavalry']

        # Start combat
        self.game.start_combat(player_army, enemy_army, province.terrain_type)

    def _draw_ui(self):
        """Draw UI elements (buttons and turn counter)."""
        # Get mouse position for hover detection
        mouse_pos = pygame.mouse.get_pos()

        # Draw turn counter at top
        font = pygame.font.Font(None, 36)
        turn_text = font.render(f"Turn: {self.current_turn}", True, WHITE)
        self.screen.blit(turn_text, (50, 10))

        # Draw buttons with hover effect
        self._draw_button(self.end_turn_button, "End Turn", mouse_pos)
        self._draw_button(self.start_combat_button, "Start Combat", mouse_pos)

    def _draw_button(self, rect: pygame.Rect, text: str, mouse_pos: tuple[int, int]):
        """Draw button with hover effect."""
        # Hover detection
        if rect.collidepoint(mouse_pos):
            color = BUTTON_HOVER_COLOR
        else:
            color = BUTTON_COLOR

        # Draw button background and border
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, BUTTON_TEXT_COLOR, rect, BUTTON_BORDER_WIDTH)

        # Draw text centered
        font = pygame.font.Font(None, 28)
        text_surf = font.render(text, True, BUTTON_TEXT_COLOR)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)

    def _handle_button_click(self, mouse_pos: tuple[int, int]) -> bool:
        """Handle button clicks. Returns True if a button was clicked."""
        if self.end_turn_button.collidepoint(mouse_pos):
            self._end_turn()
            return True
        elif self.start_combat_button.collidepoint(mouse_pos):
            self._start_test_combat()
            return True
        return False

    def _end_turn(self):
        """End current turn and advance to next."""
        self.current_turn += 1
        print(f"=== Turn {self.current_turn} started ===")

    def _start_test_combat(self):
        """Start test combat (manual trigger)."""
        player_army = ['infantry', 'infantry', 'ranged']
        enemy_army = ['infantry', 'cavalry']
        terrain = 'plains'
        self.game.start_combat(player_army, enemy_army, terrain)