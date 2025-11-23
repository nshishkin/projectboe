"""
Tactical state manager for turn-based combat.
Manages combat flow, unit selection, turn order, and victory conditions.
"""
import pygame
import math

from tactical.battlefield import Battlefield
from tactical.combat_unit import CombatUnit
from config.constants import (
    TACTICAL_HEX_SIZE, BATTLEFIELD_ROWS, BATTLEFIELD_COLS,
    BATTLEFIELD_OFFSET_X, BATTLEFIELD_OFFSET_Y,
    BG_COLOR, WHITE, BLACK, GRAY, SCREEN_HEIGHT,
    BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_TEXT_COLOR,
    BUTTON_HEIGHT, BUTTON_BORDER_WIDTH
)


class TacticalState:
    """
    Manages the tactical combat state.

    Handles turn-based combat with initiative order, unit selection,
    attack execution, and victory/defeat detection.
    """

    def __init__(self, screen, game, player_army: list[str], enemy_army: list[str], terrain: str):
        """
        Initialize tactical combat.

        Args:
            screen: Pygame display surface
            game: Reference to Game instance (for returning to strategic)
            player_army: List of unit types for player (e.g., ['infantry', 'cavalry'])
            enemy_army: List of unit types for enemy
            terrain: Terrain type from strategic province
        """
        self.screen = screen
        self.game = game
        self.battlefield = Battlefield(terrain)
        self.battlefield.place_units(player_army, enemy_army)

        # Calculate turn order by initiative (highest first)
        self.turn_order = self._calculate_turn_order()
        self.current_unit_index = 0

        # UI state
        self.selected_unit: CombatUnit | None = None
        self.combat_ended = False
        self.winner = None  # 'player' or 'enemy'
        self.show_victory_window = False
        self.show_hex_coords = False  # Debug mode for showing hex coordinates

        # Debug buttons (bottom)
        button_y = SCREEN_HEIGHT - BUTTON_HEIGHT - 10
        self.debug_finish_button = pygame.Rect(50, button_y, 200, BUTTON_HEIGHT)
        self.show_coords_button = pygame.Rect(270, button_y, 200, BUTTON_HEIGHT)

        # Victory window OK button (centered)
        self.ok_button = pygame.Rect(0, 0, 150, BUTTON_HEIGHT)  # Position calculated in render

        print(f"Tactical combat initialized: {len(player_army)} vs {len(enemy_army)}")

    def _calculate_turn_order(self) -> list[CombatUnit]:
        """
        Calculate turn order based on initiative stat.

        Returns:
            List of all units sorted by initiative (highest first)
        """
        all_units = self.battlefield.get_all_units()
        return sorted(all_units, key=lambda u: u.initiative, reverse=True)

    def update(self):
        """Update combat logic each frame."""
        if self.combat_ended:
            return

        # Check victory/defeat conditions
        if not self.battlefield.enemy_units:
            self.combat_ended = True
            self.winner = 'player'
            print("VICTORY! All enemies defeated!")
        elif not self.battlefield.player_units:
            self.combat_ended = True
            self.winner = 'enemy'
            print("DEFEAT! All units lost!")

    def handle_click(self, mouse_pos: tuple[int, int]):
        """
        Handle mouse click on battlefield.

        Phase 3 logic:
        1. First click: Select player unit
        2. Second click: Attack enemy unit (if in range)

        Args:
            mouse_pos: (x, y) pixel coordinates of mouse click
        """
        # Check victory window OK button
        if self.show_victory_window:
            if self.ok_button.collidepoint(mouse_pos):
                self._handle_victory_ok()
            return

        # Check debug buttons
        if not self.combat_ended:
            if self.debug_finish_button.collidepoint(mouse_pos):
                self._handle_debug_finish()
                return
            elif self.show_coords_button.collidepoint(mouse_pos):
                self._toggle_hex_coords()
                return

        if self.combat_ended:
            return

        # Convert pixel to hex grid coordinates
        grid_coords = self._pixel_to_hex(mouse_pos[0], mouse_pos[1])
        if not grid_coords:
            return

        x, y = grid_coords
        clicked_unit = self.battlefield.get_unit_at(x, y)

        # Phase 3: Simple click logic (no movement)
        if self.selected_unit is None:
            # First click: select player unit
            if clicked_unit and clicked_unit.is_player:
                self.selected_unit = clicked_unit
                print(f"Selected {clicked_unit.name} at ({x}, {y})")
        else:
            # Second click: attack enemy or deselect
            if clicked_unit and not clicked_unit.is_player:
                # Attack enemy
                self._execute_attack(self.selected_unit, clicked_unit)
                self.selected_unit = None
            else:
                # Deselect (clicked empty space or own unit)
                print("Deselected")
                self.selected_unit = None

    def _execute_attack(self, attacker: CombatUnit, target: CombatUnit):
        """
        Execute attack from attacker to target.

        Args:
            attacker: Unit performing attack
            target: Unit being attacked
        """
        # Perform attack (uses hit chance formula from CombatUnit)
        damage = attacker.attack(target)

        # Remove dead units
        self.battlefield.remove_dead_units()

        # Update turn order if units died
        if not target.is_alive():
            self.turn_order = [u for u in self.turn_order if u.is_alive()]

    def render(self):
        """Render the battlefield and units."""
        self.screen.fill(BG_COLOR)

        # Draw battlefield hexes
        self._draw_battlefield()

        # Draw units
        self._draw_units()

        # Highlight selected unit
        if self.selected_unit:
            self._highlight_unit(self.selected_unit)

        # Draw hex coordinates if enabled
        if self.show_hex_coords:
            self._draw_hex_coords()

        # Draw debug buttons (if combat not ended)
        if not self.combat_ended:
            self._draw_debug_buttons()

        # Draw victory window
        if self.show_victory_window:
            self._draw_victory_screen()

    def _draw_battlefield(self):
        """Draw all battlefield hexagons."""
        for row in range(BATTLEFIELD_ROWS):
            for col in range(BATTLEFIELD_COLS):
                center_x, center_y = self._hex_to_pixel(col, row)
                corners = self._get_hex_corners(center_x, center_y)

                # Terrain color (from battlefield.grid)
                # Phase 3: uniform color, just use gray
                terrain_color = GRAY

                # Draw hex
                pygame.draw.polygon(self.screen, terrain_color, corners)
                pygame.draw.polygon(self.screen, BLACK, corners, 1)  # Border

    def _draw_units(self):
        """Draw all units on battlefield."""
        for unit in self.battlefield.get_all_units():
            center_x, center_y = self._hex_to_pixel(unit.x, unit.y)

            # Draw unit as circle with color
            radius = int(TACTICAL_HEX_SIZE * 0.6)
            pygame.draw.circle(self.screen, unit.color, (int(center_x), int(center_y)), radius)
            pygame.draw.circle(self.screen, BLACK, (int(center_x), int(center_y)), radius, 2)

            # Draw HP bar
            self._draw_hp_bar(unit, center_x, center_y)

    def _draw_hp_bar(self, unit: CombatUnit, center_x: float, center_y: float):
        """
        Draw HP bar above unit.

        Args:
            unit: Unit to draw HP for
            center_x: X pixel coordinate of unit center
            center_y: Y pixel coordinate of unit center
        """
        bar_width = TACTICAL_HEX_SIZE
        bar_height = 4
        bar_x = center_x - bar_width / 2
        bar_y = center_y - TACTICAL_HEX_SIZE - 5

        # Background (red)
        pygame.draw.rect(self.screen, (255, 0, 0),
                        (bar_x, bar_y, bar_width, bar_height))

        # Foreground (green, scaled by HP%)
        hp_percentage = unit.get_hp_percentage()
        pygame.draw.rect(self.screen, (0, 255, 0),
                        (bar_x, bar_y, bar_width * hp_percentage, bar_height))

    def _highlight_unit(self, unit: CombatUnit):
        """
        Highlight selected unit with bright border.

        Args:
            unit: Unit to highlight
        """
        center_x, center_y = self._hex_to_pixel(unit.x, unit.y)
        corners = self._get_hex_corners(center_x, center_y)

        # Draw thick white border
        pygame.draw.polygon(self.screen, WHITE, corners, 3)

    def _draw_victory_screen(self):
        """Draw victory window with OK button."""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # Victory message
        font = pygame.font.Font(None, 64)
        text = font.render("You won the battle", True, WHITE)
        text_rect = text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2 - 50))
        self.screen.blit(text, text_rect)

        # OK button (centered below message)
        button_x = self.screen.get_width()//2 - 75
        button_y = self.screen.get_height()//2 + 30
        self.ok_button.x = button_x
        self.ok_button.y = button_y

        # Draw OK button with hover
        mouse_pos = pygame.mouse.get_pos()
        self._draw_button(self.ok_button, "Ok", mouse_pos)

    def _get_hex_corners(self, center_x: float, center_y: float) -> list[tuple[float, float]]:
        """
        Calculate 6 corners of flat-top hexagon.

        Args:
            center_x: X coordinate of hex center
            center_y: Y coordinate of hex center

        Returns:
            List of (x, y) tuples for corners
        """
        corners = []
        for i in range(6):
            angle = math.pi / 3 * i  # 60 degrees
            x = center_x + TACTICAL_HEX_SIZE * math.cos(angle)
            y = center_y + TACTICAL_HEX_SIZE * math.sin(angle)
            corners.append((x, y))
        return corners

    def _hex_to_pixel(self, grid_x: int, grid_y: int) -> tuple[int, int]:
        """
        Convert battlefield grid coordinates to pixel coordinates.

        Same logic as strategic map but with TACTICAL_HEX_SIZE.

        Args:
            grid_x: Column on battlefield
            grid_y: Row on battlefield

        Returns:
            (x, y) pixel coordinates of hex center
        """
        hex_width = TACTICAL_HEX_SIZE * 2
        hex_height = TACTICAL_HEX_SIZE * math.sqrt(3)

        # Odd rows offset
        x_offset = (hex_width * 3/4) if grid_y % 2 == 1 else 0

        pixel_x = BATTLEFIELD_OFFSET_X + grid_x * (hex_width * 1.5) + x_offset + hex_width / 2
        pixel_y = BATTLEFIELD_OFFSET_Y + (hex_height/2) + grid_y * (hex_height/2)

        return (int(pixel_x), int(pixel_y))

    def _pixel_to_hex(self, mouse_x: int, mouse_y: int) -> tuple[int, int] | None:
        """
        Convert pixel coordinates to battlefield grid coordinates.

        Same logic as strategic map but with TACTICAL_HEX_SIZE and BATTLEFIELD bounds.

        Args:
            mouse_x: Mouse X pixel position
            mouse_y: Mouse Y pixel position

        Returns:
            (col, row) grid coordinates or None if out of bounds
        """
        hex_width = TACTICAL_HEX_SIZE * 2
        hex_height = TACTICAL_HEX_SIZE * math.sqrt(3)

        x = mouse_x - BATTLEFIELD_OFFSET_X
        y = mouse_y - BATTLEFIELD_OFFSET_Y

        # Approximate position
        row = int((y - hex_height/2) / (hex_height/2))
        x_offset = (hex_width * 3/4) if row % 2 == 1 else 0
        col = int((x - x_offset) / (hex_width * 1.5))

        # Check 9 candidates for accuracy
        candidates = [
            (col, row),
            (col-1, row), (col+1, row),
            (col, row-1), (col, row+1),
            (col-1, row-1), (col+1, row-1),
            (col-1, row+1), (col+1, row+1)
        ]

        min_dist = float('inf')
        best = None

        for c, r in candidates:
            if 0 <= c < BATTLEFIELD_COLS and 0 <= r < BATTLEFIELD_ROWS:
                center_x, center_y = self._hex_to_pixel(c, r)
                dist = (center_x - mouse_x)**2 + (center_y - mouse_y)**2
                if dist < min_dist:
                    min_dist = dist
                    best = (c, r)

        return best

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

    def _draw_debug_buttons(self):
        """Draw debug buttons."""
        mouse_pos = pygame.mouse.get_pos()
        self._draw_button(self.debug_finish_button, "Finish battle (debug)", mouse_pos)

        # Show coords button text changes based on state
        coords_text = "Hide hex coords" if self.show_hex_coords else "Show hex coords"
        self._draw_button(self.show_coords_button, coords_text, mouse_pos)

    def _handle_debug_finish(self):
        """Handle debug finish button - kill all enemies and show victory."""
        print("DEBUG: Finishing battle instantly")

        # Kill all enemy units
        for enemy in self.battlefield.enemy_units:
            enemy.current_hp = 0

        # Remove dead units
        self.battlefield.remove_dead_units()

        # Set victory state
        self.combat_ended = True
        self.winner = 'player'
        self.show_victory_window = True

    def _handle_victory_ok(self):
        """Handle OK button in victory window - return to strategic map."""
        print("Returning to strategic map")
        self.game.change_state('strategic')

    def _toggle_hex_coords(self):
        """Toggle display of hex coordinates on/off."""
        self.show_hex_coords = not self.show_hex_coords
        status = "ON" if self.show_hex_coords else "OFF"
        print(f"Hex coordinates display: {status}")

    def _draw_hex_coords(self):
        """Draw coordinates on each battlefield hex."""
        font = pygame.font.Font(None, 16)  # Small font for coordinates

        for row in range(BATTLEFIELD_ROWS):
            for col in range(BATTLEFIELD_COLS):
                # Get hex center position
                center_x, center_y = self._hex_to_pixel(col, row)

                # Create coordinate text "x,y"
                coord_text = f"{col},{row}"
                text_surf = font.render(coord_text, True, WHITE)
                text_rect = text_surf.get_rect(center=(int(center_x), int(center_y)))

                # Draw black background for better visibility
                background_rect = text_rect.inflate(4, 2)
                pygame.draw.rect(self.screen, BLACK, background_rect)

                # Draw coordinate text
                self.screen.blit(text_surf, text_rect)
