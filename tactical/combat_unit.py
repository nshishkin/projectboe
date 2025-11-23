"""
Combat unit class for tactical battlefield.
Represents individual units in combat with stats, position, and combat logic.
"""
import random
from config.constants import UNIT_TYPES


class CombatUnit:
    """
    Represents a single combat unit on the tactical battlefield.

    Units have stats loaded from UNIT_TYPES, current state (HP, position),
    and can perform combat actions like attacking other units.
    """

    def __init__(self, unit_type: str, x: int, y: int, is_player: bool):
        """
        Initialize combat unit with stats from UNIT_TYPES.

        Args:
            unit_type: Type of unit ('infantry', 'cavalry', 'ranged', etc.)
            x: Grid X position on battlefield
            y: Grid Y position on battlefield
            is_player: True if player's unit, False if enemy
        """
        self.unit_type = unit_type
        self.x = x
        self.y = y
        self.is_player = is_player

        # Load stats from UNIT_TYPES definition
        stats = UNIT_TYPES[unit_type]
        self.name = stats['name']
        self.max_hp = stats['max_hp']
        self.current_hp = stats['max_hp']
        self.melee_attack = stats['melee_attack']
        self.ranged_attack = stats['ranged_attack']
        self.melee_defence = stats['melee_defence']
        self.ranged_defence = stats['ranged_defence']
        self.stamina = stats['stamina']
        self.initiative = stats['initiative']
        self.morale = stats['morale']
        self.base_damage = stats['base_damage']

        # Visual color based on ownership
        self.color = stats['color'] if is_player else stats['enemy_color']

        # Combat state
        self.has_acted = False  # Has unit acted this turn

    def take_damage(self, damage: int) -> bool:
        """
        Apply damage to this unit.

        Args:
            damage: Amount of damage to apply

        Returns:
            True if unit died from this damage, False otherwise
        """
        self.current_hp -= damage
        if self.current_hp < 0:
            self.current_hp = 0

        return self.current_hp <= 0

    def attack(self, target: 'CombatUnit') -> int:
        """
        Attack target unit with melee attack.

        Hit chance = (attacker.melee_attack - target.melee_defence)%
        Damage on hit = attacker.base_damage

        Args:
            target: The unit being attacked

        Returns:
            Amount of damage dealt (0 if missed)
        """
        # Calculate hit chance
        hit_chance = self.melee_attack - target.melee_defence
        hit_chance = max(0, min(100, hit_chance))  # Clamp to 0-100%

        # Roll for hit
        roll = random.randint(1, 100)

        if roll <= hit_chance:
            # Hit!
            damage = self.base_damage
            is_killed = target.take_damage(damage)

            print(f"{self.name} HIT {target.name} for {damage} damage (chance: {hit_chance}%)")
            if is_killed:
                print(f"{target.name} has been slain!")

            return damage
        else:
            # Miss
            print(f"{self.name} MISSED {target.name} (chance was: {hit_chance}%)")
            return 0

    def move_to(self, x: int, y: int):
        """
        Move unit to new position.

        Args:
            x: New grid X position
            y: New grid Y position
        """
        self.x = x
        self.y = y

    def reset_turn(self):
        """Reset turn-based state at the start of a new round."""
        self.has_acted = False

    def is_adjacent(self, target: 'CombatUnit') -> bool:
        """
        Check if target unit is in an adjacent hex.

        For flat-top hexagons with offset coordinates, adjacency is complex.
        Phase 3: Simplified - just check if target is close enough.

        Args:
            target: Unit to check adjacency with

        Returns:
            True if target is adjacent (within melee range)
        """
        dx = abs(self.x - target.x)
        dy = abs(self.y - target.y)

        # Simple distance check for Phase 3
        # Adjacent if within 1 tile (allows diagonal)
        return dx <= 1 and dy <= 1 and (dx + dy) > 0

    def get_position(self) -> tuple[int, int]:
        """
        Get current grid position.

        Returns:
            Tuple of (x, y) grid coordinates
        """
        return (self.x, self.y)

    def is_alive(self) -> bool:
        """
        Check if unit is still alive.

        Returns:
            True if unit has HP remaining
        """
        return self.current_hp > 0

    def get_hp_percentage(self) -> float:
        """
        Get current HP as percentage of max.

        Returns:
            HP percentage (0.0 to 1.0)
        """
        return self.current_hp / self.max_hp if self.max_hp > 0 else 0.0

    def __repr__(self) -> str:
        """String representation for debugging."""
        owner = "Player" if self.is_player else "Enemy"
        return f"{owner} {self.name} at ({self.x},{self.y}) - HP: {self.current_hp}/{self.max_hp}"
