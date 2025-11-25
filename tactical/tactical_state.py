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
from tactical.hex_geometry import (
    calculate_hex_distance, hex_to_pixel, pixel_to_hex, get_hex_corners
)
from tactical.tactical_renderer import TacticalRenderer
from tactical.tactical_input import TacticalInput
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
            pixel_x, pixel_y = hex_to_pixel(unit.x, unit.y)
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

        # Initialize renderer and input handler
        self.renderer = TacticalRenderer(self)
        self.input = TacticalInput(self)

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
                distance = calculate_hex_distance(unit.x, unit.y, target_x, target_y)

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
            grid_coords = pixel_to_hex(mouse_pos[0], mouse_pos[1])
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
            distance = calculate_hex_distance(
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
                distance = calculate_hex_distance(
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
                target_pixel_x, target_pixel_y = hex_to_pixel(step_x, step_y)
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

