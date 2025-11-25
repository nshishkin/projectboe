"""
Input handling subsystem for tactical combat.

Handles all user input including mouse clicks, mouse wheel, and button interactions.
"""
import pygame

from tactical.hex_geometry import pixel_to_hex
from config.constants import TACTICAL_ATTACK_COST


class TacticalInput:
    """
    Handles all input processing for tactical combat screen.

    Separates input handling logic from game state logic for better organization.
    """

    def __init__(self, state):
        """
        Initialize input handler with reference to tactical state.

        Args:
            state: TacticalState instance
        """
        self.state = state

    def handle_click(self, mouse_pos: tuple[int, int]):
        """
        Handle left mouse click on battlefield.

        New UI system:
        - Click on player unit: Show stats (but only active unit can act)
        - Click on enemy: Attack if in range
        - Click on empty hex: Move if reachable
        - ALT + Click on enemy: Lock enemy stats until ALT released
        - Click during animation: Skip current animation

        Args:
            mouse_pos: (x, y) pixel coordinates of mouse click
        """
        # Skip current animation if one is playing
        if self.state.animation_queue.is_playing():
            self.state.animation_queue.skip_current()
            self.state._log_message("Animation skipped")
            return

        # Check victory window OK button
        if self.state.show_victory_window:
            if self.state.ok_button.collidepoint(mouse_pos):
                self._handle_victory_ok()
            return

        # Check buttons
        if not self.state.combat_ended:
            if self.state.end_turn_button.collidepoint(mouse_pos):
                self._handle_end_turn()
                return
            elif self.state.debug_finish_button.collidepoint(mouse_pos):
                self._handle_debug_finish()
                return
            elif self.state.show_coords_button.collidepoint(mouse_pos):
                self._toggle_hex_coords()
                return

        if self.state.combat_ended:
            return

        # Check if click is on combat log panel to handle scrolling
        panel_x, panel_y = 820, 50
        panel_width, panel_height = 440, 400
        log_panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)

        if log_panel_rect.collidepoint(mouse_pos):
            # Click on log panel - allow scrolling but don't do other actions
            return

        # Convert pixel to hex grid coordinates
        grid_coords = pixel_to_hex(mouse_pos[0], mouse_pos[1])
        if not grid_coords:
            return

        x, y = grid_coords
        clicked_unit = self.state.battlefield.get_unit_at(x, y)
        current_unit = self.state.get_current_unit()

        # ALT + Click on enemy: Lock enemy stats
        if self.state.alt_pressed and clicked_unit and not clicked_unit.is_player:
            self.state.alt_locked_unit = clicked_unit
            self.state._log_message(f"Locked stats for {clicked_unit.get_display_name()} (ALT)")
            return

        # Click on player unit: Show stats
        if clicked_unit and clicked_unit.is_player:
            self.state.selected_unit = clicked_unit
            self.state._log_message(f"Showing stats for {clicked_unit.get_display_name()}")
            return

        # Click on enemy: Try to attack
        if clicked_unit and not clicked_unit.is_player:
            # Check if active unit can attack
            if current_unit and current_unit.is_player:
                if clicked_unit in self.state.attackable_enemies:
                    # Check if unit has AP for attack
                    if current_unit.current_action_points >= TACTICAL_ATTACK_COST:
                        self.state._execute_attack(current_unit, clicked_unit)
                        # Recalculate attackable enemies after attack
                        self.state._calculate_attackable_enemies()
                        self.state._calculate_reachable_cells()
                    else:
                        self.state._log_message(f"{current_unit.get_display_name()} has no AP for attack!")
                else:
                    self.state._log_message(f"{clicked_unit.get_display_name()} is out of range!")
            return

        # Click on empty hex: Try to move
        if (x, y) in self.state.reachable_cells:
            if current_unit and current_unit.is_player:
                distance = self.state.reachable_cells[(x, y)]
                self.state._move_unit(current_unit, x, y, distance)

                # Recalculate movement and attackable enemies
                self.state._calculate_reachable_cells()
                self.state._calculate_attackable_enemies()
        else:
            self.state._log_message(f"Cannot move to ({x}, {y})")

    def handle_mousewheel(self, event):
        """
        Handle mouse wheel events for scrolling combat log.

        Args:
            event: pygame mouse wheel event with x, y attributes
        """
        # Check if mouse is over the combat log panel
        mouse_pos = pygame.mouse.get_pos()
        panel_x, panel_y = 820, 50
        panel_width, panel_height = 440, 400
        log_panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)

        if log_panel_rect.collidepoint(mouse_pos):
            # Scroll the combat log
            scroll_amount = event.y * 20  # Adjust sensitivity
            new_scroll = self.state.log_scroll_offset - scroll_amount  # Negative because scrolling up means moving content down

            # Clamp scroll to valid range
            self.state.log_scroll_offset = max(0, min(new_scroll, self.state.log_max_scroll))

    def _handle_end_turn(self):
        """Handle End Turn button click - manually end current unit's turn."""
        current_unit = self.state.get_current_unit()
        if current_unit and current_unit.is_player:
            self.state._log_message(f"Player manually ended {current_unit.get_display_name()}'s turn")
            self.state._end_unit_turn()

    def _handle_debug_finish(self):
        """Handle debug finish button - kill all enemies and show victory."""
        self.state._log_message("DEBUG: Finishing battle instantly")

        # Kill all enemy units
        for enemy in self.state.battlefield.enemy_units:
            enemy.current_hp = 0

        # Remove dead units
        self.state.battlefield.remove_dead_units()

        # Set victory state
        self.state.combat_ended = True
        self.state.winner = 'player'
        self.state.show_victory_window = True

    def _handle_victory_ok(self):
        """Handle OK button in victory window - return to strategic map."""
        self.state._log_message("Returning to strategic map")
        self.state.game.change_state('strategic')

    def _toggle_hex_coords(self):
        """Toggle display of hex coordinates on/off."""
        self.state.show_hex_coords = not self.state.show_hex_coords
        status = "ON" if self.state.show_hex_coords else "OFF"
        print(f"Hex coordinates display: {status}")
