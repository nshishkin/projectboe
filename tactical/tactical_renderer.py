"""
Rendering subsystem for tactical combat.

Handles all drawing operations for the tactical combat screen.
"""
import pygame
import math

from tactical.hex_geometry import hex_to_pixel, get_hex_corners
from tactical.combat_unit import CombatUnit
from config.constants import (
    TACTICAL_HEX_SIZE, BATTLEFIELD_ROWS, BATTLEFIELD_COLS,
    BG_COLOR, WHITE, BLACK, GRAY, DARK_GRAY,
    BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_TEXT_COLOR,
    BUTTON_HEIGHT, BUTTON_BORDER_WIDTH
)
from shared.sprite_loader import get_sprite_loader


class TacticalRenderer:
    """
    Handles all rendering for tactical combat screen.

    Separates drawing logic from game logic for better organization.
    """

    def __init__(self, state):
        """
        Initialize renderer with reference to tactical state.

        Args:
            state: TacticalState instance
        """
        self.state = state
        self.sprite_loader = get_sprite_loader()

    def render(self):
        """Render the battlefield and units."""
        self.state.screen.fill(BG_COLOR)

        # Draw battlefield hexes
        self._draw_battlefield()

        # Draw reachable cells (before units so they're not on top)
        if self.state.reachable_cells:
            self._draw_reachable_cells()

        # Draw attackable enemies with red highlight
        if self.state.attackable_enemies:
            self._draw_attackable_enemies()
        

        # Draw units
        self._draw_units()

        # Highlight selected unit
        if self.state.selected_unit:
            self._highlight_unit(self.state.selected_unit)

        # Draw hex coordinates if enabled
        if self.state.show_hex_coords:
            self._draw_hex_coords()

        # Draw combat info (round and current unit)
        if not self.state.combat_ended:
            self._draw_combat_info()

        # Draw unit info panel
        self._draw_unit_info_panel()

        # Draw combat log panel
        self._draw_combat_log()

        # Draw debug buttons (if combat not ended)
        if not self.state.combat_ended:
            self._draw_debug_buttons()

        # Draw victory window
        if self.state.show_victory_window:
            self._draw_victory_screen()


    def _draw_battlefield(self):
        """Draw all battlefield hexagons."""
        # Calculate actual hex geometry for sprites
        hex_width = int(TACTICAL_HEX_SIZE * 2)
        hex_height = int(TACTICAL_HEX_SIZE * math.sqrt(3))

        for row in range(BATTLEFIELD_ROWS):
            for col in range(BATTLEFIELD_COLS):
                center_x, center_y = hex_to_pixel(col, row)
                corners = get_hex_corners(center_x, center_y)

                # Try to load terrain sprite (use tactical terrain based on battlefield terrain)
                # For now, use same terrain type for all hexes (could be enhanced later)
                terrain_type = getattr(self.state, 'terrain_type', 'plains')
                terrain_sprite = self.sprite_loader.load_terrain_sprite(
                    terrain_type,
                    'tactical',
                    size=(hex_width, hex_height)
                )

                if terrain_sprite:
                    # Draw sprite centered on hex
                    sprite_rect = terrain_sprite.get_rect(center=(int(center_x), int(center_y)))
                    self.state.screen.blit(terrain_sprite, sprite_rect)
                else:
                    # Fallback: Draw filled hex with gray color
                    pygame.draw.polygon(self.state.screen, GRAY, corners)

                # Draw hex border
                pygame.draw.polygon(self.state.screen, BLACK, corners, 1)


    def _draw_units(self):
        """Draw all units on battlefield."""
        current_unit = self.state.get_current_unit()

        for unit in self.state.battlefield.get_all_units():
            # Use display coordinates (animated position)
            center_x = unit.display_x
            center_y = unit.display_y

            # Add bouncing animation for current unit (only when not animating movement/attack)
            if unit == current_unit and not self.state.combat_ended and not self.state.animation_queue.is_playing():
                # Sin wave animation: ±5 pixels, 2 second cycle
                bounce_offset = math.sin(self.state.animation_time * math.pi) * 5
                center_y += bounce_offset

            # Draw unit as circle with color
            radius = int(TACTICAL_HEX_SIZE * 0.6)
            pygame.draw.circle(self.state.screen, unit.color, (int(center_x), int(center_y)), radius)
            pygame.draw.circle(self.state.screen, BLACK, (int(center_x), int(center_y)), radius, 2)

            # Draw directional "beak" (cone)
            beak_size = int(radius * 0.5)
            if unit.is_player:
                # Player units face right
                beak_tip = (int(center_x + radius), int(center_y))
                beak_top = (int(center_x + radius * 0.3), int(center_y - beak_size))
                beak_bottom = (int(center_x + radius * 0.3), int(center_y + beak_size))
            else:
                # Enemy units face left
                beak_tip = (int(center_x - radius), int(center_y))
                beak_top = (int(center_x - radius * 0.3), int(center_y - beak_size))
                beak_bottom = (int(center_x - radius * 0.3), int(center_y + beak_size))

            pygame.draw.polygon(self.state.screen, unit.color, [beak_tip, beak_top, beak_bottom])
            pygame.draw.polygon(self.state.screen, BLACK, [beak_tip, beak_top, beak_bottom], 2)

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
        pygame.draw.rect(self.state.screen, (255, 0, 0),
                        (bar_x, bar_y, bar_width, bar_height))

        # Foreground (green, scaled by HP%)
        hp_percentage = unit.get_hp_percentage()
        pygame.draw.rect(self.state.screen, (0, 255, 0),
                        (bar_x, bar_y, bar_width * hp_percentage, bar_height))


    def _highlight_unit(self, unit: CombatUnit):
        """
        Highlight selected unit with bright border.

        Args:
            unit: Unit to highlight
        """
        # Use display coordinates (animated position) to match unit rendering
        center_x, center_y = unit.display_x, unit.display_y
        corners = get_hex_corners(center_x, center_y)

        # Draw thick white border
        pygame.draw.polygon(self.state.screen, WHITE, corners, 3)


    def _draw_reachable_cells(self):
        """Draw green highlights on cells the selected unit can move to."""
        for (x, y), distance in self.state.reachable_cells.items():
            center_x, center_y = hex_to_pixel(x, y)
            corners = get_hex_corners(center_x, center_y)

            # Draw semi-transparent green overlay
            # Lighter green for cells closer to movement limit
            alpha = 100 if distance == 1 else 60
            green_color = (0, 255, 0)

            # Create surface for transparency
            overlay = pygame.Surface((TACTICAL_HEX_SIZE * 3, TACTICAL_HEX_SIZE * 3), pygame.SRCALPHA)
            overlay_corners = [(cx - center_x + TACTICAL_HEX_SIZE * 1.5,
                               cy - center_y + TACTICAL_HEX_SIZE * 1.5)
                              for cx, cy in corners]
            pygame.draw.polygon(overlay, (*green_color, alpha), overlay_corners)

            # Blit to screen
            self.state.screen.blit(overlay, (int(center_x - TACTICAL_HEX_SIZE * 1.5),
                                      int(center_y - TACTICAL_HEX_SIZE * 1.5)))


    def _draw_attackable_enemies(self):
        """Draw red borders around enemies that can be attacked by the active unit."""
        for enemy in self.state.attackable_enemies:
            # Use display coordinates (animated position) to match unit rendering
            center_x, center_y = enemy.display_x, enemy.display_y
            corners = get_hex_corners(center_x, center_y)

            # Draw thick red border
            red_color = (255, 0, 0)
            pygame.draw.polygon(self.state.screen, red_color, corners, 3)



    def _draw_victory_screen(self):
        """Draw victory/defeat window with OK button."""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.state.screen.get_width(), self.state.screen.get_height()))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.state.screen.blit(overlay, (0, 0))

        # Victory or Defeat message
        font = pygame.font.Font(None, 64)
        if self.state.winner == 'player':
            message = "You won the battle!"
            message_color = (100, 255, 100)  # Green
        else:
            message = "You were defeated!"
            message_color = (255, 100, 100)  # Red

        text = font.render(message, True, message_color)
        text_rect = text.get_rect(center=(self.state.screen.get_width()//2, self.state.screen.get_height()//2 - 50))
        self.state.screen.blit(text, text_rect)

        # OK button (centered below message)
        button_x = self.state.screen.get_width()//2 - 75
        button_y = self.state.screen.get_height()//2 + 30
        self.state.ok_button.x = button_x
        self.state.ok_button.y = button_y

        # Draw OK button with hover
        mouse_pos = pygame.mouse.get_pos()
        self._draw_button(self.state.ok_button, "Ok", mouse_pos)


    def _draw_button(self, rect: pygame.Rect, text: str, mouse_pos: tuple[int, int]):
        """Draw button with hover effect."""
        # Hover detection
        if rect.collidepoint(mouse_pos):
            color = BUTTON_HOVER_COLOR
        else:
            color = BUTTON_COLOR

        # Draw button background and border
        pygame.draw.rect(self.state.screen, color, rect)
        pygame.draw.rect(self.state.screen, BUTTON_TEXT_COLOR, rect, BUTTON_BORDER_WIDTH)

        # Draw text centered
        font = pygame.font.Font(None, 28)
        text_surf = font.render(text, True, BUTTON_TEXT_COLOR)
        text_rect = text_surf.get_rect(center=rect.center)
        self.state.screen.blit(text_surf, text_rect)


    def _draw_combat_info(self):
        """Draw combat information (round number and current unit) at top of screen."""
        font = pygame.font.Font(None, 32)

        # Round number
        round_text = font.render(f"Round: {self.state.current_round}", True, WHITE)
        self.state.screen.blit(round_text, (20, 10))

        # Current unit info
        current_unit = self.state.get_current_unit()
        if current_unit:
            side = "Player" if current_unit.is_player else "Enemy"
            unit_color = (100, 255, 100) if current_unit.is_player else (255, 100, 100)
            unit_text = font.render(f"Current Turn: {current_unit.get_display_name()} ({side})", True, unit_color)
            self.state.screen.blit(unit_text, (20, 45))


    def _draw_debug_buttons(self):
        """Draw combat buttons."""
        mouse_pos = pygame.mouse.get_pos()

        # End Turn button (only active for player units)
        current_unit = self.state.get_current_unit()
        if current_unit and current_unit.is_player:
            self._draw_button(self.state.end_turn_button, "End Turn", mouse_pos)

        # Debug buttons
        self._draw_button(self.state.debug_finish_button, "Finish battle (debug)", mouse_pos)

        # Show coords button text changes based on state
        coords_text = "Hide hex coords" if self.state.show_hex_coords else "Show hex coords"
        self._draw_button(self.state.show_coords_button, coords_text, mouse_pos)


    def _draw_hex_coords(self):
        """Draw coordinates on each battlefield hex."""
        font = pygame.font.Font(None, 16)  # Small font for coordinates

        for row in range(BATTLEFIELD_ROWS):
            for col in range(BATTLEFIELD_COLS):
                # Get hex center position
                center_x, center_y = hex_to_pixel(col, row)

                # Create coordinate text "x,y"
                coord_text = f"{col},{row}"
                text_surf = font.render(coord_text, True, WHITE)
                text_rect = text_surf.get_rect(center=(int(center_x), int(center_y)))

                # Draw black background for better visibility
                background_rect = text_rect.inflate(4, 2)
                pygame.draw.rect(self.state.screen, BLACK, background_rect)

                # Draw coordinate text
                self.state.screen.blit(text_surf, text_rect)


    def _draw_combat_log(self):
        """Draw combat log panel to the right of unit info panel."""
        # Panel dimensions and position (to the right of unit info panel)
        panel_x = 820
        panel_y = 50
        panel_width = 440
        panel_height = 400

        # Draw panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.state.screen, DARK_GRAY, panel_rect)
        pygame.draw.rect(self.state.screen, WHITE, panel_rect, 2)  # Border

        # Title
        title_font = pygame.font.Font(None, 28)
        title_text = title_font.render("Combat Log", True, WHITE)
        self.state.screen.blit(title_text, (panel_x + 10, panel_y + 10))

        # Draw log messages (newest at bottom)
        text_font = pygame.font.Font(None, 20)
        y_offset = panel_y + 45 - self.state.log_scroll_offset
        line_height = 24

        for message in self.state.combat_log:
            if len(message) > 50:
                # Simple word wrap
                words = message.split(' ')
                current_line = []
                for word in words:
                    test_line = ' '.join(current_line + [word])
                    if len(test_line) <= 50:
                        current_line.append(word)
                    else:
                        # Draw current line
                        if current_line:
                            line_text = text_font.render(' '.join(current_line), True, WHITE)
                            # Only draw if it's within the visible area
                            if y_offset + line_height >= panel_y + 45 and y_offset <= panel_y + panel_height:
                                self.state.screen.blit(line_text, (panel_x + 10, y_offset))
                            y_offset += line_height
                        current_line = [word]
                # Draw remaining line
                if current_line:
                    line_text = text_font.render(' '.join(current_line), True, WHITE)
                    # Only draw if it's within the visible area
                    if y_offset + line_height >= panel_y + 45 and y_offset <= panel_y + panel_height:
                        self.state.screen.blit(line_text, (panel_x + 10, y_offset))
                    y_offset += line_height
            else:
                # Short message, draw as-is
                line_text = text_font.render(message, True, WHITE)
                # Only draw if it's within the visible area
                if y_offset + line_height >= panel_y + 45 and y_offset <= panel_y + panel_height:
                    self.state.screen.blit(line_text, (panel_x + 10, y_offset))
                y_offset += line_height

            # Stop if we've drawn beyond the panel
            if y_offset > panel_y + panel_height:
                break


    def _draw_unit_info_panel(self):
        """
        Draw unit information panel on the right side of the battlefield.

        Priority for display:
        1. alt_locked_unit (locked with ALT+click)
        2. hovered_unit (ALT+hover)
        3. selected_unit (current active player unit or clicked player unit)
        4. None (during enemy turn if no selection)
        """
        # Determine which unit to display
        display_unit = None
        if self.state.alt_locked_unit:
            display_unit = self.state.alt_locked_unit
        elif self.state.hovered_unit:
            display_unit = self.state.hovered_unit
        elif self.state.selected_unit:
            display_unit = self.state.selected_unit

        if not display_unit:
            return  # No unit to display

        # Panel dimensions and position
        panel_x = 550
        panel_y = 50
        panel_width = 250
        panel_height = 400

        # Draw panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.state.screen, DARK_GRAY, panel_rect)
        pygame.draw.rect(self.state.screen, WHITE, panel_rect, 2)  # Border

        # Font for text
        title_font = pygame.font.Font(None, 32)
        text_font = pygame.font.Font(None, 24)

        y_offset = panel_y + 10

        # Unit name
        name_text = title_font.render(display_unit.get_display_name(), True, WHITE)
        self.state.screen.blit(name_text, (panel_x + 10, y_offset))
        y_offset += 40

        # Side (Player/Enemy)
        side_text = "Player" if display_unit.is_player else "Enemy"
        side_color = (100, 255, 100) if display_unit.is_player else (255, 100, 100)
        side_surf = text_font.render(f"Side: {side_text}", True, side_color)
        self.state.screen.blit(side_surf, (panel_x + 10, y_offset))
        y_offset += 30

        # HP with bar
        hp_text = text_font.render(f"HP: {display_unit.current_hp}/{display_unit.max_hp}", True, WHITE)
        self.state.screen.blit(hp_text, (panel_x + 10, y_offset))
        y_offset += 25

        # HP bar
        bar_width = panel_width - 20
        bar_height = 10
        bar_x = panel_x + 10
        bar_y = y_offset
        # Background (red)
        pygame.draw.rect(self.state.screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        # Foreground (green, scaled by HP%)
        hp_percentage = display_unit.get_hp_percentage()
        pygame.draw.rect(self.state.screen, (0, 255, 0), (bar_x, bar_y, int(bar_width * hp_percentage), bar_height))
        y_offset += 20

        # Stats
        stats = [
            f"Action Points: {display_unit.current_action_points}/{display_unit.action_points}",
            f"Melee Attack: {display_unit.melee_attack}",
            f"Melee Defence: {display_unit.melee_defence}",
            f"Initiative: {display_unit.initiative}",
            f"Stamina: {display_unit.stamina}",
            f"Morale: {display_unit.morale}",
            f"Base Damage: {display_unit.base_damage}",
            f"Attack Range: {display_unit.attack_range}"
        ]

        for stat in stats:
            stat_surf = text_font.render(stat, True, WHITE)
            self.state.screen.blit(stat_surf, (panel_x + 10, y_offset))
            y_offset += 30
