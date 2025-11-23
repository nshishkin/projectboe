"""
Battlefield manager for tactical combat.
Manages the combat grid, unit placement, and battlefield state.
"""
from tactical.combat_unit import CombatUnit
from config.constants import BATTLEFIELD_ROWS, BATTLEFIELD_COLS


class Battlefield:
    """
    Represents the tactical battlefield grid.

    Configurable hex grid where combat takes place.
    Units are placed on opposite sides and fight until one side is eliminated.
    """

    def __init__(self, terrain_type: str):
        """
        Initialize battlefield with terrain type.

        Args:
            terrain_type: Type of terrain from strategic province
        """
        self.rows = BATTLEFIELD_ROWS
        self.cols = BATTLEFIELD_COLS
        self.terrain_type = terrain_type

        # Generate terrain grid (Phase 3: uniform, Phase 4+: obstacles)
        self.grid = self._generate_terrain()

        # Unit lists
        self.player_units: list[CombatUnit] = []
        self.enemy_units: list[CombatUnit] = []

    def _generate_terrain(self) -> list[list[str]]:
        """
        Generate terrain grid for battlefield.

        Phase 3: Entire field is same terrain type, no obstacles.

        Returns:
            2D grid where each cell contains terrain type
        """
        return [[self.terrain_type for _ in range(self.cols)]
                for _ in range(self.rows)]

    def place_units(self, player_army: list[str], enemy_army: list[str]):
        """
        Place armies on the battlefield.

        Player units placed vertically in column 2, starting from middle
        Enemy units placed vertically in third column from end, starting from middle

        Args:
            player_army: List of unit types for player (e.g., ['infantry', 'cavalry'])
            enemy_army: List of unit types for enemy
        """
        # Clear existing units
        self.player_units.clear()
        self.enemy_units.clear()

        # Place player units vertically in column 2, starting from middle
        player_start_col = 1
        player_start_row = self.rows // 2  # Middle of battlefield

        for i, unit_type in enumerate(player_army):
            x = player_start_col
            y = player_start_row + i
            unit = CombatUnit(unit_type, x, y, is_player=True)
            self.player_units.append(unit)

        # Place enemy units vertically in second column from end, starting from middle
        enemy_start_col = self.cols - 2 # second column from the end
        enemy_start_row = self.rows // 2  # Middle of battlefield

        for i, unit_type in enumerate(enemy_army):
            x = enemy_start_col
            y = enemy_start_row + i
            unit = CombatUnit(unit_type, x, y, is_player=False)
            self.enemy_units.append(unit)

    def get_unit_at(self, x: int, y: int) -> CombatUnit | None:
        """
        Get unit at specified grid position.

        Args:
            x: Grid column
            y: Grid row

        Returns:
            CombatUnit if one exists at position, None otherwise
        """
        for unit in self.player_units + self.enemy_units:
            if unit.x == x and unit.y == y:
                return unit
        return None

    def is_valid_position(self, x: int, y: int) -> bool:
        """
        Check if position is valid (in bounds and not occupied).

        Args:
            x: Grid column
            y: Grid row

        Returns:
            True if position is valid and unoccupied
        """
        # Check bounds
        if not (0 <= x < self.cols and 0 <= y < self.rows):
            return False

        # Check if occupied
        return self.get_unit_at(x, y) is None

    def remove_dead_units(self):
        """Remove dead units from unit lists."""
        self.player_units = [u for u in self.player_units if u.is_alive()]
        self.enemy_units = [u for u in self.enemy_units if u.is_alive()]

    def get_all_units(self) -> list[CombatUnit]:
        """
        Get all units on battlefield.

        Returns:
            Combined list of player and enemy units
        """
        return self.player_units + self.enemy_units

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"Battlefield({self.rows}x{self.cols}, {len(self.player_units)} player units, {len(self.enemy_units)} enemy units)"
