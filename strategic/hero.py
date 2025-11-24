"""
Hero class representing the player's hero on the strategic map.
"""
from config.constants import HERO_MOVEMENT_POINTS

class Hero:
    """
    Player's hero with position on the strategic map.
    
    Attributes:
        x: Column position on hex grid
        y: Row position on hex grid
    """
    def __init__(self, start_x: int, start_y: int):
        """
        Initialize hero at starting position.

        Args:
            start_x: Starting column position
            start_y: Starting row position
        """
        self.x = start_x
        self.y = start_y

        # Movement
        self.movement_points = HERO_MOVEMENT_POINTS  # Maximum movement per turn
        self.current_movement = HERO_MOVEMENT_POINTS  # Current movement available

        # Phase 4+: Will add army, inventory, experience
        self.army = []
        self.inventory = []  

    def move_to(self,x: int, y: int):
        """
        Move hero to new position.
        
        Args:
            x: Target column position
            y: Target row position
        """
        self.x = x 
        self.y = y
        print(f"Hero moved to ({x},{y})")
    
    def get_position(self) -> tuple[int, int]:
        """
        Get current hero position.

        Returns:
            Tuple of (x, y) coordinates
        """
        return (self.x, self.y)

    def restore_movement(self):
        """Restore movement points to maximum (called at start of turn)."""
        self.current_movement = self.movement_points
        print(f"Hero movement restored to {self.movement_points}")

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"Hero(x={self.x}, y={self.y}, movement={self.current_movement}/{self.movement_points})"   