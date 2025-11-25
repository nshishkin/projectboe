"""
Tactical state manager for turn-based combat.
Manages combat flow, unit selection, turn order, and victory conditions.
"""
import pygame
import math
import random

from tactical.battlefield import Battlefield
from tactical.combat_unit import CombatUnit
from tactical.combat_ai import CombatAI
from tactical.movement import get_reachable_cells, find_path
from tactical.animation import AnimationQueue, MoveAnimation, AttackAnimation
from config.constants import (
    TACTICAL_HEX_SIZE, BATTLEFIELD_ROWS, BATTLEFIELD_COLS,
    BATTLEFIELD_OFFSET_X, BATTLEFIELD_OFFSET_Y,
    BG_COLOR, WHITE, BLACK, GRAY, DARK_GRAY, SCREEN_HEIGHT,
    BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_TEXT_COLOR,
    BUTTON_HEIGHT, BUTTON_BORDER_WIDTH,
    TACTICAL_MOVE_COST, TACTICAL_ATTACK_COST,
    TACTICAL_MOVE_SPEED_PLAYER, TACTICAL_MOVE_SPEED_AI,
    TACTICAL_ATTACK_OFFSET, TACTICAL_ATTACK_DURATION
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

        # Initialize display coordinates for all units
        for unit in self.battlefield.get_all_units():
            pixel_x, pixel_y = self._hex_to_pixel(unit.x, unit.y)
            unit.display_x = float(pixel_x)
            unit.display_y = float(pixel_y)

        # Initialize animation queue
        self.animation_queue = AnimationQueue()
        self.clock = pygame.time.Clock()
        self.last_frame_time = pygame.time.get_ticks()

        # Combat log for UI display (initialize before AI)
        self.combat_log: list[str] = []  # List of recent combat messages
        self.max_log_messages = 15  # Maximum messages to keep in log
        self.log_scroll_offset = 0  # Scroll offset for combat log
        self.log_max_scroll = 0  # Maximum scroll value

        # Initialize AI controller with logging callback
        self.ai = CombatAI(log_callback=self._log_message)

        # Calculate turn order by initiative (highest first)
        self.turn_order = self._calculate_turn_order()
        self.current_unit_index = 0
        self.current_round = 1  # Track combat rounds
        self.animation_time = 0.0  # For bouncing animation

        # UI state
        self.selected_unit: CombatUnit | None = None  # Currently selected player unit (for stats display)
        self.info_unit: CombatUnit | None = None  # Unit to display info for (overrides selected_unit)
        self.hovered_unit: CombatUnit | None = None  # Unit under mouse cursor (for ALT+hover)
        self.reachable_cells: dict[tuple[int, int], int] = {}  # Valid movement targets
        self.attackable_enemies: list[CombatUnit] = []  # Enemies in range of active unit
        self.alt_pressed = False  # Track ALT key state
        self.alt_locked_unit: CombatUnit | None = None  # Unit locked with ALT+click
        self.combat_ended = False
        self.winner = None  # 'player' or 'enemy'
        self.show_victory_window = False
        self.show_hex_coords = False  # Debug mode for showing hex coordinates
        self.pending_turn_end = False  # Flag to end turn after animations complete

        # Combat buttons (bottom)
        button_y = SCREEN_HEIGHT - BUTTON_HEIGHT - 10
        self.end_turn_button = pygame.Rect(50, button_y, 150, BUTTON_HEIGHT)
        self.debug_finish_button = pygame.Rect(220, button_y, 200, BUTTON_HEIGHT)
        self.show_coords_button = pygame.Rect(440, button_y, 200, BUTTON_HEIGHT)

        # Victory window OK button (centered)
        self.ok_button = pygame.Rect(0, 0, 150, BUTTON_HEIGHT)  # Position calculated in render

        self._log_message(f"Tactical combat initialized: {len(player_army)} vs {len(enemy_army)}")
        self._log_message(f"=== ROUND {self.current_round} STARTED ===")

        # Announce first unit's turn (execute AI if enemy)
        first_unit = self.get_current_unit()
        if first_unit:
            if not first_unit.is_player:
                self._log_message(f"=== {first_unit.get_display_name()}'s turn (Enemy, Initiative: {first_unit.initiative}) ===")
                self._execute_ai_turn(first_unit)
            else:
                self._log_message(f"=== {first_unit.get_display_name()}'s turn (Initiative: {first_unit.initiative}) ===")
                # Auto-select first player unit
                self._auto_select_active_unit()

    def _calculate_turn_order(self) -> list[CombatUnit]:
        """
        Calculate turn order based on initiative stat.
        Units with equal initiative are randomized.

        Returns:
            List of all units sorted by initiative (highest first)
        """
        all_units = self.battlefield.get_all_units()
        # Add random tie-breaker for units with same initiative
        return sorted(all_units, key=lambda u: (u.initiative, random.random()), reverse=True)

    def get_current_unit(self) -> CombatUnit | None:
        """Get the unit whose turn it currently is."""
        if 0 <= self.current_unit_index < len(self.turn_order):
            return self.turn_order[self.current_unit_index]
        return None

    def _auto_select_active_unit(self):
        """
        Auto-select the current active player unit and calculate reachable cells/attackable enemies.

        Called when turn switches to a player unit.
        """
        current_unit = self.get_current_unit()
        if current_unit and current_unit.is_player:
            self.selected_unit = current_unit
            self.info_unit = None  # Clear any ALT-locked info
            self.alt_locked_unit = None

            # Calculate reachable movement cells
            self._calculate_reachable_cells()

            # Calculate attackable enemies
            self._calculate_attackable_enemies()

            self._log_message(f"Auto-selected {current_unit.get_display_name()}")

    def _end_unit_turn(self):
        """End the current unit's turn and move to next unit."""
        current_unit = self.get_current_unit()
        if current_unit:
            current_unit.has_acted = True
            self._log_message(f"{current_unit.get_display_name()}'s turn ended")

        # Don't advance turn while animations are playing
        if self.animation_queue.is_playing():
            self._log_message("Delaying turn switch until animations complete")
            self.pending_turn_end = True
        else:
            self._next_unit_turn()

    def _execute_ai_turn(self, unit: CombatUnit):
        """
        Execute AI-controlled turn for an enemy unit.

        Uses CombatAI to select and perform actions until AP is exhausted.

        Args:
            unit: Enemy unit to control
        """
        # Keep executing actions until unit has no AP left or decides to skip
        max_actions = 10  # Safety limit to prevent infinite loops
        action_count = 0

        while unit.current_action_points > 0 and action_count < max_actions:
            # Get AI decision
            action = self.ai.select_action(unit, self.battlefield)

            # Execute the action
            if action['type'] == 'attack':
                target = action['target']
                self._execute_attack(unit, target)
                action_count += 1

                # Check if target died and update turn order
                if not target.is_alive():
                    self.turn_order = [u for u in self.turn_order if u.is_alive()]

            elif action['type'] == 'move':
                target_x, target_y = action['position']
                target_unit = action.get('target')  # Optional, for logging

                # Calculate distance for AP cost
                distance = self._calculate_hex_distance(unit.x, unit.y, target_x, target_y)

                # Move the unit
                self._move_unit(unit, target_x, target_y, distance)
                action_count += 1

            else:  # 'skip' or unknown action
                break

        # End the unit's turn
        self._end_unit_turn()

    def  _calculate_hex_distance(self, x1: int, y1: int, x2: int, y2: int) -> int:
        """
        Calculate hex distance between two positions.

        Args:
            x1, y1: Starting position
            x2, y2: Ending position

        Returns:
            Distance in hexes
        """
        # Convert even-q offset to cube coordinates
        # For even-q: r = row - (col + (col & 1)) // 2
        q1 = x1
        r1 = y1 - (x1 + (x1 & 1)) // 2

        q2 = x2
        r2 = y2 - (x2 + (x2 & 1)) // 2

        # Cube distance
        distance = (abs(q1 - q2) + abs(r1 - r2) + abs(q1 + r1 - q2 - r2)) // 2

        return distance

    def _next_unit_turn(self):
        """Advance to next unit's turn."""
        self.current_unit_index += 1

        # Check if round is complete
        if self.current_unit_index >= len(self.turn_order):
            self._start_new_round()
            return

        # Execute AI for enemy units or auto-select player unit
        current_unit = self.get_current_unit()
        if current_unit and not current_unit.is_player:
            self._log_message(f"=== {current_unit.get_display_name()}'s turn (Enemy, Initiative: {current_unit.initiative}) ===")
            self._execute_ai_turn(current_unit)
        else:
            # Start player unit's turn
            if current_unit:
                self._log_message(f"=== {current_unit.get_display_name()}'s turn (Initiative: {current_unit.initiative}) ===")
                self._auto_select_active_unit()

    def _start_new_round(self):
        """Start a new combat round."""
        self.current_round += 1
        self.current_unit_index = 0

        self._log_message(f"\n=== ROUND {self.current_round} STARTED ===")

        # Restore movement points for all units
        for unit in self.turn_order:
            unit.reset_turn()

        # Recalculate turn order (re-randomize ties)
        self.turn_order = self._calculate_turn_order()

        # Execute AI if first unit is enemy, otherwise auto-select player unit
        current_unit = self.get_current_unit()
        if current_unit and not current_unit.is_player:
            self._log_message(f"=== {current_unit.get_display_name()}'s turn (Enemy, Initiative: {current_unit.initiative}) ===")
            self._execute_ai_turn(current_unit)
        else:
            if current_unit:
                self._log_message(f"=== {current_unit.get_display_name()}'s turn (Initiative: {current_unit.initiative}) ===")
                self._auto_select_active_unit()

    def update(self):
        """Update combat logic each frame."""
        if self.combat_ended:
            return

        # Calculate delta time
        current_time = pygame.time.get_ticks()
        delta_time = (current_time - self.last_frame_time) / 1000.0  # Convert to seconds
        self.last_frame_time = current_time

        # Update animations
        self.animation_queue.update(delta_time)

        # Check if we need to end turn after animations complete
        if self.pending_turn_end and not self.animation_queue.is_playing():
            self._log_message("Animations complete - switching turn now")
            self.pending_turn_end = False
            self._next_unit_turn()
            return  # Skip rest of update to avoid double-processing

        # Update animation timer (for bouncing effect)
        self.animation_time += delta_time

        # Track ALT key state
        keys = pygame.key.get_pressed()
        self.alt_pressed = keys[pygame.K_LALT] or keys[pygame.K_RALT]

        # Handle ALT + hover: Update info_unit based on hover
        if self.alt_pressed:
            # Get mouse position and check for unit under cursor
            mouse_pos = pygame.mouse.get_pos()
            grid_coords = self._pixel_to_hex(mouse_pos[0], mouse_pos[1])
            if grid_coords:
                hovered_unit = self.battlefield.get_unit_at(*grid_coords)
                # Show enemy stats on hover
                if hovered_unit and not hovered_unit.is_player:
                    self.hovered_unit = hovered_unit
                else:
                    self.hovered_unit = None
        else:
            # ALT released: Clear hover and locked unit
            self.hovered_unit = None
            self.alt_locked_unit = None

        # Check if current unit's turn should end (1 or less action points left)
        # But only if animations are not playing
        if not self.animation_queue.is_playing():
            current_unit = self.get_current_unit()
            if current_unit and current_unit.current_action_points <= 1 and not current_unit.has_acted:
                self._log_message(f"{current_unit.get_display_name()} has no action points left - turn ending")
                self._end_unit_turn()

        # Check victory/defeat conditions
        if not self.battlefield.enemy_units:
            self.combat_ended = True
            self.winner = 'player'
            self.show_victory_window = True
            self._log_message("VICTORY! All enemies defeated!")
        elif not self.battlefield.player_units:
            self.combat_ended = True
            self.winner = 'enemy'
            self.show_victory_window = True  # Show defeat window too
            self._log_message("DEFEAT! All units lost!")

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
        if self.animation_queue.is_playing():
            self.animation_queue.skip_current()
            self._log_message("Animation skipped")
            return

        # Check victory window OK button
        if self.show_victory_window:
            if self.ok_button.collidepoint(mouse_pos):
                self._handle_victory_ok()
            return

        # Check buttons
        if not self.combat_ended:
            if self.end_turn_button.collidepoint(mouse_pos):
                self._handle_end_turn()
                return
            elif self.debug_finish_button.collidepoint(mouse_pos):
                self._handle_debug_finish()
                return
            elif self.show_coords_button.collidepoint(mouse_pos):
                self._toggle_hex_coords()
                return

        if self.combat_ended:
            return

        # Check if click is on combat log panel to handle scrolling
        panel_x, panel_y = 820, 50
        panel_width, panel_height = 440, 400
        log_panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        
        if log_panel_rect.collidepoint(mouse_pos):
            # Click on log panel - allow scrolling but don't do other actions
            return

        # Convert pixel to hex grid coordinates
        grid_coords = self._pixel_to_hex(mouse_pos[0], mouse_pos[1])
        if not grid_coords:
            return

        x, y = grid_coords
        clicked_unit = self.battlefield.get_unit_at(x, y)
        current_unit = self.get_current_unit()

        # ALT + Click on enemy: Lock enemy stats
        if self.alt_pressed and clicked_unit and not clicked_unit.is_player:
            self.alt_locked_unit = clicked_unit
            self._log_message(f"Locked stats for {clicked_unit.get_display_name()} (ALT)")
            return

        # Click on player unit: Show stats
        if clicked_unit and clicked_unit.is_player:
            self.selected_unit = clicked_unit
            self._log_message(f"Showing stats for {clicked_unit.get_display_name()}")
            return

        # Click on enemy: Try to attack
        if clicked_unit and not clicked_unit.is_player:
            # Check if active unit can attack
            if current_unit and current_unit.is_player:
                if clicked_unit in self.attackable_enemies:
                    # Check if unit has AP for attack
                    if current_unit.current_action_points >= TACTICAL_ATTACK_COST:
                        self._execute_attack(current_unit, clicked_unit)
                        # Recalculate attackable enemies after attack
                        self._calculate_attackable_enemies()
                        self._calculate_reachable_cells()
                    else:
                        self._log_message(f"{current_unit.get_display_name()} has no AP for attack!")
                else:
                    self._log_message(f"{clicked_unit.get_display_name()} is out of range!")
            return

        # Click on empty hex: Try to move
        if (x, y) in self.reachable_cells:
            if current_unit and current_unit.is_player:
                distance = self.reachable_cells[(x, y)]
                self._move_unit(current_unit, x, y, distance)

                # Recalculate movement and attackable enemies
                self._calculate_reachable_cells()
                self._calculate_attackable_enemies()
        else:
            self._log_message(f"Cannot move to ({x}, {y})")

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
            new_scroll = self.log_scroll_offset - scroll_amount  # Negative because scrolling up means moving content down
            
            # Clamp scroll to valid range
            self.log_scroll_offset = max(0, min(new_scroll, self.log_max_scroll))

    def _execute_attack(self, attacker: CombatUnit, target: CombatUnit):
        """
        Execute attack from attacker to target.
        Costs TACTICAL_ATTACK_COST action points.
        Creates attack animation before dealing damage.

        Args:
            attacker: Unit performing attack
            target: Unit being attacked
        """
        # Check if attacker has action points for attack
        if attacker.current_action_points < TACTICAL_ATTACK_COST:
            self._log_message(f"{attacker.get_display_name()} has no action points to attack!")
            return

        # Create attack animation
        attack_anim = AttackAnimation(attacker, target, TACTICAL_ATTACK_OFFSET, TACTICAL_ATTACK_DURATION)
        self.animation_queue.add(attack_anim)

        # Perform attack (uses hit chance formula from CombatUnit)
        damage = attacker.attack(target)

        # Consume action points for attack
        attacker.current_action_points -= TACTICAL_ATTACK_COST
        self._log_message(f"{attacker.get_display_name()} has {attacker.current_action_points} action points left")

        # Remove dead units
        self.battlefield.remove_dead_units()

        # Update turn order if units died
        if not target.is_alive():
            self.turn_order = [u for u in self.turn_order if u.is_alive()]

    def _calculate_reachable_cells(self):
        """Calculate cells reachable by selected unit based on action points."""
        if not self.selected_unit:
            return

        # Get all occupied positions as blocked cells
        blocked = set()
        for unit in self.battlefield.get_all_units():
            if unit != self.selected_unit:  # Don't block own position
                blocked.add((unit.x, unit.y))

        # Calculate how many hexes can be reached with current action points
        # Each hex costs TACTICAL_MOVE_COST action points
        max_hexes = self.selected_unit.current_action_points // TACTICAL_MOVE_COST

        # Calculate reachable cells using BFS pathfinding
        self.reachable_cells = get_reachable_cells(
            self.selected_unit.x,
            self.selected_unit.y,
            max_hexes,
            blocked
        )

        self._log_message(f"Found {len(self.reachable_cells)} reachable cells (AP: {self.selected_unit.current_action_points})")

    def _calculate_attackable_enemies(self):
        """
        Calculate enemies that are within attack range of the selected unit.

        Uses unit.attack_range to determine which enemies can be attacked.
        """
        self.attackable_enemies.clear()

        if not self.selected_unit:
            return

        # Only calculate for active unit (current turn)
        current_unit = self.get_current_unit()
        if self.selected_unit != current_unit:
            return

        # Check each enemy unit
        for enemy in self.battlefield.enemy_units:
            distance = self._calculate_hex_distance(
                self.selected_unit.x, self.selected_unit.y,
                enemy.x, enemy.y
            )

            # Check if enemy is within attack range
            if distance <= self.selected_unit.attack_range:
                self.attackable_enemies.append(enemy)

        # Calculate all hexes that the unit can attack (excluding its own hex)
        attackable_hexes = []
        for x in range(BATTLEFIELD_COLS):
            for y in range(BATTLEFIELD_ROWS):
                distance = self._calculate_hex_distance(
                    self.selected_unit.x, self.selected_unit.y,
                    x, y
                )
                if distance <= self.selected_unit.attack_range and distance > 0:  # Exclude the unit's own hex
                    attackable_hexes.append((x, y))

        # Log with coordinates if any enemies found
        count = len(self.attackable_enemies)
        if count > 0:
            coords = ", ".join([f"({e.x},{e.y})" for e in self.attackable_enemies])
            self._log_message(f"Found {count} attackable enemies (range: {self.selected_unit.attack_range}): {coords}")
        else:
            self._log_message(f"Found 0 attackable enemies (range: {self.selected_unit.attack_range})")

        # Log all attackable hexes
        self._log_message(f"Attackable hexes (range {self.selected_unit.attack_range}): {attackable_hexes}")

    def _move_unit(self, unit: CombatUnit, target_x: int, target_y: int, distance: int):
        """
        Move unit to target position and consume action points.
        Creates move animations for each step in the path.

        Args:
            unit: Unit to move
            target_x: Target grid column
            target_y: Target grid row
            distance: Distance in hexes (will be multiplied by TACTICAL_MOVE_COST)
        """
        # Calculate action points cost (distance * cost per hex)
        ap_cost = distance * TACTICAL_MOVE_COST

        # Find path from current position to target
        blocked = set()
        for other_unit in self.battlefield.get_all_units():
            if other_unit != unit:
                blocked.add((other_unit.x, other_unit.y))

        path = find_path((unit.x, unit.y), (target_x, target_y), blocked)

        # Format path for logging
        if path:
            path_str = " -> ".join([f"({x},{y})" for x, y in path])
            self._log_message(f"Moving {unit.get_display_name()}: {path_str} (cost: {ap_cost} AP)")
        else:
            self._log_message(f"Moving {unit.get_display_name()} from ({unit.x}, {unit.y}) to ({target_x}, {target_y}) (cost: {ap_cost} AP)")

        if path:
            # Determine speed based on unit ownership
            speed = TACTICAL_MOVE_SPEED_PLAYER if unit.is_player else TACTICAL_MOVE_SPEED_AI

            # Create animation for each step in path
            # Track previous position to chain animations correctly
            prev_x, prev_y = unit.display_x, unit.display_y
            for step_x, step_y in path:
                target_pixel_x, target_pixel_y = self._hex_to_pixel(step_x, step_y)
                anim = MoveAnimation(unit, float(target_pixel_x), float(target_pixel_y), speed, prev_x, prev_y)
                self.animation_queue.add(anim)
                # Next animation starts where this one ends
                prev_x, prev_y = float(target_pixel_x), float(target_pixel_y)

            # Update display position to end of path immediately
            # This ensures that if AI does multiple moves in one turn,
            # the next animation will start from the correct position
            unit.display_x = prev_x
            unit.display_y = prev_y

        # Update logical position immediately
        unit.move_to(target_x, target_y)
        unit.current_action_points -= ap_cost
        self._log_message(f"{unit.get_display_name()} has {unit.current_action_points} action points left")

    def render(self):
        """Render the battlefield and units."""
        self.screen.fill(BG_COLOR)

        # Draw battlefield hexes
        self._draw_battlefield()

        # Draw reachable cells (before units so they're not on top)
        if self.reachable_cells:
            self._draw_reachable_cells()

        # Draw attackable enemies with red highlight
        if self.attackable_enemies:
            self._draw_attackable_enemies()
        

        # Draw units
        self._draw_units()

        # Highlight selected unit
        if self.selected_unit:
            self._highlight_unit(self.selected_unit)

        # Draw hex coordinates if enabled
        if self.show_hex_coords:
            self._draw_hex_coords()

        # Draw combat info (round and current unit)
        if not self.combat_ended:
            self._draw_combat_info()

        # Draw unit info panel
        self._draw_unit_info_panel()

        # Draw combat log panel
        self._draw_combat_log()

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
        current_unit = self.get_current_unit()

        for unit in self.battlefield.get_all_units():
            # Use display coordinates (animated position)
            center_x = unit.display_x
            center_y = unit.display_y

            # Add bouncing animation for current unit (only when not animating movement/attack)
            if unit == current_unit and not self.combat_ended and not self.animation_queue.is_playing():
                # Sin wave animation: ±5 pixels, 2 second cycle
                bounce_offset = math.sin(self.animation_time * math.pi) * 5
                center_y += bounce_offset

            # Draw unit as circle with color
            radius = int(TACTICAL_HEX_SIZE * 0.6)
            pygame.draw.circle(self.screen, unit.color, (int(center_x), int(center_y)), radius)
            pygame.draw.circle(self.screen, BLACK, (int(center_x), int(center_y)), radius, 2)

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

            pygame.draw.polygon(self.screen, unit.color, [beak_tip, beak_top, beak_bottom])
            pygame.draw.polygon(self.screen, BLACK, [beak_tip, beak_top, beak_bottom], 2)

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

    def _draw_reachable_cells(self):
        """Draw green highlights on cells the selected unit can move to."""
        for (x, y), distance in self.reachable_cells.items():
            center_x, center_y = self._hex_to_pixel(x, y)
            corners = self._get_hex_corners(center_x, center_y)

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
            self.screen.blit(overlay, (int(center_x - TACTICAL_HEX_SIZE * 1.5),
                                      int(center_y - TACTICAL_HEX_SIZE * 1.5)))

    def _draw_attackable_enemies(self):
        """Draw red borders around enemies that can be attacked by the active unit."""
        for enemy in self.attackable_enemies:
            center_x, center_y = self._hex_to_pixel(enemy.x, enemy.y)
            corners = self._get_hex_corners(center_x, center_y)

            # Draw thick red border
            red_color = (255, 0, 0)
            pygame.draw.polygon(self.screen, red_color, corners, 3)


    def _draw_victory_screen(self):
        """Draw victory/defeat window with OK button."""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # Victory or Defeat message
        font = pygame.font.Font(None, 64)
        if self.winner == 'player':
            message = "You won the battle!"
            message_color = (100, 255, 100)  # Green
        else:
            message = "You were defeated!"
            message_color = (255, 100, 100)  # Red

        text = font.render(message, True, message_color)
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

        # Odd rows offset by height
        y_offset = (hex_height/2) if grid_x % 2 == 1 else 0

        # Horizontal spacing
        pixel_x = BATTLEFIELD_OFFSET_X + (grid_x+1) * (hex_width * 3/4) 
        # Vertical spacing (adjusted for proper interlocking)
        pixel_y = BATTLEFIELD_OFFSET_Y +  (grid_y+1) * hex_height - y_offset

        return (int(pixel_x), int(pixel_y))

    def _pixel_to_hex(self, mouse_x: int, mouse_y: int) -> tuple[int, int] | None:
        """
        Convert pixel coordinates to battlefield grid coordinates.

        Uses offset coordinate system where odd columns are shifted down.
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

        # Calculate approximate column (accounting for +1 in _hex_to_pixel)
        col = int(x / (hex_width * 3/4)) - 1

        # Calculate y_offset based on column parity
        y_offset = (hex_height/2) if col % 2 == 1 else 0

        # Calculate approximate row (accounting for +1 in _hex_to_pixel)
        row = int((y + y_offset) / hex_height) - 1

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

    def _draw_combat_info(self):
        """Draw combat information (round number and current unit) at top of screen."""
        font = pygame.font.Font(None, 32)

        # Round number
        round_text = font.render(f"Round: {self.current_round}", True, WHITE)
        self.screen.blit(round_text, (20, 10))

        # Current unit info
        current_unit = self.get_current_unit()
        if current_unit:
            side = "Player" if current_unit.is_player else "Enemy"
            unit_color = (100, 255, 100) if current_unit.is_player else (255, 100, 100)
            unit_text = font.render(f"Current Turn: {current_unit.get_display_name()} ({side})", True, unit_color)
            self.screen.blit(unit_text, (20, 45))

    def _draw_debug_buttons(self):
        """Draw combat buttons."""
        mouse_pos = pygame.mouse.get_pos()

        # End Turn button (only active for player units)
        current_unit = self.get_current_unit()
        if current_unit and current_unit.is_player:
            self._draw_button(self.end_turn_button, "End Turn", mouse_pos)

        # Debug buttons
        self._draw_button(self.debug_finish_button, "Finish battle (debug)", mouse_pos)

        # Show coords button text changes based on state
        coords_text = "Hide hex coords" if self.show_hex_coords else "Show hex coords"
        self._draw_button(self.show_coords_button, coords_text, mouse_pos)

    def _handle_end_turn(self):
        """Handle End Turn button click - manually end current unit's turn."""
        current_unit = self.get_current_unit()
        if current_unit and current_unit.is_player:
            self._log_message(f"Player manually ended {current_unit.get_display_name()}'s turn")
            self._end_unit_turn()

    def _handle_debug_finish(self):
        """Handle debug finish button - kill all enemies and show victory."""
        self._log_message("DEBUG: Finishing battle instantly")

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
        self._log_message("Returning to strategic map")
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

    def _calculate_log_content_height(self):
        """Calculate total height of log content in pixels."""
        text_font = pygame.font.Font(None, 20)
        line_height = 24
        total_height = 0
        
        for message in self.combat_log:
            if len(message) > 50:
                # Calculate number of lines for wrapped message
                words = message.split(' ')
                current_line = []
                line_count = 1
                for word in words:
                    test_line = ' '.join(current_line + [word])
                    if len(test_line) <= 50:
                        current_line.append(word)
                    else:
                        if current_line:
                            line_count += 1
                        current_line = [word]
                total_height += line_count * line_height
            else:
                total_height += line_height
        
        return total_height

    def _log_message(self, message: str):
        """
        Add message to combat log and print to terminal.

        Args:
            message: Message to log
        """
        print(message)
        self.combat_log.append(message)
        # Keep only last max_log_messages
        if len(self.combat_log) > self.max_log_messages:
            self.combat_log.pop(0)
        
        # Calculate max scroll based on content
        total_content_height = self._calculate_log_content_height()
        available_height = 400 - 45  # panel_height - title_space
        self.log_max_scroll = max(0, total_content_height - available_height)

        # Auto-scroll to bottom when new message is added
        self.log_scroll_offset = self.log_max_scroll

    def _draw_combat_log(self):
        """Draw combat log panel to the right of unit info panel."""
        # Panel dimensions and position (to the right of unit info panel)
        panel_x = 820
        panel_y = 50
        panel_width = 440
        panel_height = 400

        # Draw panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, DARK_GRAY, panel_rect)
        pygame.draw.rect(self.screen, WHITE, panel_rect, 2)  # Border

        # Title
        title_font = pygame.font.Font(None, 28)
        title_text = title_font.render("Combat Log", True, WHITE)
        self.screen.blit(title_text, (panel_x + 10, panel_y + 10))

        # Draw log messages (newest at bottom)
        text_font = pygame.font.Font(None, 20)
        y_offset = panel_y + 45 - self.log_scroll_offset
        line_height = 24

        for message in self.combat_log:
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
                                self.screen.blit(line_text, (panel_x + 10, y_offset))
                            y_offset += line_height
                        current_line = [word]
                # Draw remaining line
                if current_line:
                    line_text = text_font.render(' '.join(current_line), True, WHITE)
                    # Only draw if it's within the visible area
                    if y_offset + line_height >= panel_y + 45 and y_offset <= panel_y + panel_height:
                        self.screen.blit(line_text, (panel_x + 10, y_offset))
                    y_offset += line_height
            else:
                # Short message, draw as-is
                line_text = text_font.render(message, True, WHITE)
                # Only draw if it's within the visible area
                if y_offset + line_height >= panel_y + 45 and y_offset <= panel_y + panel_height:
                    self.screen.blit(line_text, (panel_x + 10, y_offset))
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
        if self.alt_locked_unit:
            display_unit = self.alt_locked_unit
        elif self.hovered_unit:
            display_unit = self.hovered_unit
        elif self.selected_unit:
            display_unit = self.selected_unit

        if not display_unit:
            return  # No unit to display

        # Panel dimensions and position
        panel_x = 550
        panel_y = 50
        panel_width = 250
        panel_height = 400

        # Draw panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, DARK_GRAY, panel_rect)
        pygame.draw.rect(self.screen, WHITE, panel_rect, 2)  # Border

        # Font for text
        title_font = pygame.font.Font(None, 32)
        text_font = pygame.font.Font(None, 24)

        y_offset = panel_y + 10

        # Unit name
        name_text = title_font.render(display_unit.get_display_name(), True, WHITE)
        self.screen.blit(name_text, (panel_x + 10, y_offset))
        y_offset += 40

        # Side (Player/Enemy)
        side_text = "Player" if display_unit.is_player else "Enemy"
        side_color = (100, 255, 100) if display_unit.is_player else (255, 100, 100)
        side_surf = text_font.render(f"Side: {side_text}", True, side_color)
        self.screen.blit(side_surf, (panel_x + 10, y_offset))
        y_offset += 30

        # HP with bar
        hp_text = text_font.render(f"HP: {display_unit.current_hp}/{display_unit.max_hp}", True, WHITE)
        self.screen.blit(hp_text, (panel_x + 10, y_offset))
        y_offset += 25

        # HP bar
        bar_width = panel_width - 20
        bar_height = 10
        bar_x = panel_x + 10
        bar_y = y_offset
        # Background (red)
        pygame.draw.rect(self.screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        # Foreground (green, scaled by HP%)
        hp_percentage = display_unit.get_hp_percentage()
        pygame.draw.rect(self.screen, (0, 255, 0), (bar_x, bar_y, int(bar_width * hp_percentage), bar_height))
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
            self.screen.blit(stat_surf, (panel_x + 10, y_offset))
            y_offset += 30
