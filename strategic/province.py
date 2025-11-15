"""
Province class representing a single hex tile on the strategic map.
Each province has terrain type and position.
"""

class Province:
    """
    A single province (hex tile) on the strategic map.
    
    Uses offset coordinate system where (x, y) represents logical grid position.
    Odd rows are offset by half a hex width when rendered.
    
    Attributes:
        x: Column position on the hex grid
        y: Row position on the hex grid
        terrain_type: String key from TERRAIN_TYPES ('plains', 'woods', etc.)
    """
    
    def __init__(self, x: int, y: int, terrain_type: str):
        """
        Initialize a province.
        
        Args:
            x: Column position on the hex grid
            y: Row position on the hex grid
            terrain_type: Terrain type key ('plains', 'woods', 'hills', 'swamp')
        """
        self.x = x
        self.y = y
        self.terrain_type = terrain_type
        
        # Phase 4+: Will add encounters, ownership, resources
        self.encounter = None
        self.owner = None
    
    def get_position(self) -> tuple[int, int]:
        """
        Get province grid position.
        
        Returns:
            Tuple of (x, y) grid coordinates
        """
        return (self.x, self.y)
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"Province({self.x}, {self.y}, {self.terrain_type})"