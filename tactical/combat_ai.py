"""
Combat AI for enemy units.
Uses priority-based target selection and pathfinding.
"""
import math
from typing import Optional

from tactical.combat_unit import CombatUnit
from tactical.movement import get_reachable_cells
from config.constants import TACTICAL_MOVE_COST, TACTICAL_ATTACK_COST, BATTLEFIELD_ROWS, BATTLEFIELD_COLS


class CombatAI:
    """
    AI controller for enemy units in tactical combat.

    Uses a priority-based system to:
    1. Evaluate all potential targets
    2. Select the best target based on multiple factors
    3. Plan movement and attack actions
    """

    def __init__(self):
        """Initialize AI controller."""
        # Weights for target evaluation (can be tuned for balance)
        self.weight_low_hp = 40      # Prioritize wounded targets
        self.weight_distance = 5     # Prefer closer targets
        self.weight_ranged = 25      # Prioritize ranged units
        self.weight_archer = 25      # Prioritize archers

    def select_action(self, unit: CombatUnit, battlefield) -> dict:
        """
        Select the best action for an enemy unit.

        Args:
            unit: The enemy unit making the decision
            battlefield: Current battlefield state with all units

        Returns:
            dict: Action to perform with keys:
                - 'type': 'attack', 'move', or 'skip'
                - 'target': CombatUnit (for attack)
                - 'position': (x, y) tuple (for move)
        """
        # Get all player units as potential targets
        targets = battlefield.player_units

        if not targets:
            return {'type': 'skip'}

        # Evaluate all targets and select the best one
        best_target = self._select_best_target(unit, targets)

        if not best_target:
            return {'type': 'skip'}

        # Plan action to engage the target
        return self._plan_action(unit, best_target, battlefield)

    def _select_best_target(self, attacker: CombatUnit, targets: list[CombatUnit]) -> Optional[CombatUnit]:
        """
        Evaluate all targets and return the highest priority one.

        Args:
            attacker: Unit doing the targeting
            targets: List of potential target units

        Returns:
            Best target unit or None
        """
        if not targets:
            return None

        target_scores = []
        for target in targets:
            score = self._evaluate_target(attacker, target)
            target_scores.append((target, score))

        # Sort by score (highest first) and return best
        target_scores.sort(key=lambda x: x[1], reverse=True)
        return target_scores[0][0]

    def _evaluate_target(self, attacker: CombatUnit, target: CombatUnit) -> float:
        """
        Calculate priority score for a target.

        Higher score = higher priority.

        Args:
            attacker: Unit evaluating the target
            target: Potential target unit

        Returns:
            Priority score (higher is better)
        """
        score = 0.0

        # Factor 1: Low HP targets (finish off wounded enemies)
        hp_percentage = target.get_hp_percentage()
        hp_factor = 1.0 - hp_percentage  # Lower HP = higher score
        score += hp_factor * self.weight_low_hp

        # Factor 2: Distance (closer is better)
        distance = self._calculate_distance(attacker, target)
        # Normalize distance (max battlefield diagonal ~14 hexes)
        distance_factor = max(0, 1.0 - (distance / 15.0))
        score += distance_factor * self.weight_distance * 10

        # Factor 3: Unit type priorities
        if target.unit_type == 'ranged':
            score += self.weight_ranged
        elif target.unit_type == 'archer':
            score += self.weight_archer

        return score

    def _plan_action(self, unit: CombatUnit, target: CombatUnit, battlefield) -> dict:
        """
        Plan the best action to engage a target.

        Priority:
        1. Attack if target is adjacent and we have AP
        2. Move closer to target if we have AP
        3. Skip turn if no AP

        Args:
            unit: AI unit planning action
            target: Selected target
            battlefield: Current battlefield state

        Returns:
            dict: Action to perform
        """
        # Check if we can attack immediately
        if self._is_adjacent(unit, target):
            if unit.current_action_points >= TACTICAL_ATTACK_COST:
                print(f"AI: {unit.name} attacks {target.name}")
                return {'type': 'attack', 'target': target}

        # Try to move closer to target
        if unit.current_action_points >= TACTICAL_MOVE_COST:
            move_position = self._find_best_move_towards(unit, target, battlefield)
            if move_position:
                print(f"AI: {unit.name} moves from ({unit.x},{unit.y}) towards {target.name}")
                return {'type': 'move', 'position': move_position, 'target': target}

        # No valid actions available
        print(f"AI: {unit.name} skips turn (no AP or valid moves)")
        return {'type': 'skip'}

    def _calculate_distance(self, unit1: CombatUnit, unit2: CombatUnit) -> int:
        """
        Calculate hex distance between two units using offset coordinates.

        Args:
            unit1: First unit
            unit2: Second unit

        Returns:
            Distance in hexes
        """
        # Convert offset coordinates to cube coordinates for accurate hex distance
        x1, y1 = unit1.x, unit1.y
        x2, y2 = unit2.x, unit2.y

        # Offset to cube coordinate conversion
        q1 = x1
        r1 = y1 - (x1 - (x1 & 1)) // 2

        q2 = x2
        r2 = y2 - (x2 - (x2 & 1)) // 2

        # Cube distance formula
        distance = (abs(q1 - q2) + abs(r1 - r2) + abs(q1 + r1 - q2 - r2)) // 2

        return distance

    def _is_adjacent(self, unit: CombatUnit, target: CombatUnit) -> bool:
        """
        Check if target is in an adjacent hex (distance 1).

        Args:
            unit: Source unit
            target: Target unit

        Returns:
            True if target is adjacent
        """
        return self._calculate_distance(unit, target) == 1

    def _find_best_move_towards(self, unit: CombatUnit, target: CombatUnit, battlefield) -> Optional[tuple[int, int]]:
        """
        Find the best hex to move to that gets closer to target.

        Uses reachable cells calculation and picks the one closest to target.

        Args:
            unit: Unit to move
            target: Target to approach
            battlefield: Current battlefield state

        Returns:
            (x, y) position to move to, or None if no valid moves
        """
        # Get all occupied positions as blocked cells
        blocked = set()
        for other_unit in battlefield.get_all_units():
            if other_unit != unit:  # Don't block own position
                blocked.add((other_unit.x, other_unit.y))

        # Calculate how many hexes we can move
        max_hexes = unit.current_action_points // TACTICAL_MOVE_COST

        # Get all reachable cells
        reachable = get_reachable_cells(unit.x, unit.y, max_hexes, blocked)

        if not reachable:
            return None

        # Find the reachable cell that minimizes distance to target
        best_position = None
        best_distance = float('inf')

        for (x, y), move_distance in reachable.items():
            # Calculate distance from this position to target
            # Create temporary unit at this position for distance calculation
            distance_to_target = self._hex_distance(x, y, target.x, target.y)

            # Prefer cells that get us closer to target
            # If equal distance, prefer cells that cost less AP to reach
            if distance_to_target < best_distance:
                best_distance = distance_to_target
                best_position = (x, y)
            elif distance_to_target == best_distance and move_distance < reachable.get(best_position, 999):
                # Same distance to target but cheaper to reach
                best_position = (x, y)

        return best_position

    def _hex_distance(self, x1: int, y1: int, x2: int, y2: int) -> int:
        """
        Calculate hex distance between two coordinates.

        Args:
            x1, y1: First position
            x2, y2: Second position

        Returns:
            Distance in hexes
        """
        # Convert offset to cube coordinates
        q1 = x1
        r1 = y1 - (x1 - (x1 & 1)) // 2

        q2 = x2
        r2 = y2 - (x2 - (x2 & 1)) // 2

        # Cube distance
        distance = (abs(q1 - q2) + abs(r1 - r2) + abs(q1 + r1 - q2 - r2)) // 2

        return distance
