"""
Hexagonal grid system for tactical combat in Brothers of Eador.
Implements a hexagonal grid with axial coordinates for the tactical map.
"""
import pygame
import math
from typing import List, Tuple, Optional


class HexTile:
    """Represents a single hexagonal tile in the tactical grid."""
    
    def __init__(self, q: int, r: int, terrain_type: str = "plain", elevation: int = 0):
        self.q = q  # axial coordinate q
        self.r = r  # axial coordinate r
        self.s = -q - r  # axial coordinate s (derived, since q + r + s = 0)
        self.terrain_type = terrain_type
        self.elevation = elevation
        self.x = 0  # pixel coordinate x
        self.y = 0  # pixel coordinate y
        self.center_x = 0  # center x coordinate
        self.center_y = 0  # center y coordinate
        self.vertices = []  # list of vertex coordinates for drawing
        
    def cube_to_pixel(self, hex_size: int) -> Tuple[float, float]:
        """Convert cube coordinates to pixel coordinates (flat-topped orientation)."""
        x = hex_size * 3/2 * self.q
        y = hex_size * math.sqrt(3) * (self.r + 0.5 * (self.q % 2))
        return x, y
        
    def axial_to_pixel(self, hex_size: int, offset_x: float = 0, offset_y: float = 0) -> Tuple[float, float]:
        """Convert axial coordinates to pixel coordinates with offset (flat-topped orientation)."""
        # For flat-topped hexes in a rectangular grid
        x = hex_size * 3/2 * self.q + offset_x
        # Every other column is offset by half the height of a hex
        y = hex_size * math.sqrt(3) * (self.r + 0.5 * (self.q % 2)) + offset_y
        return x, y


class HexGrid:
    """Hexagonal grid system for tactical combat."""
    
    def __init__(self, width: int = 10, height: int = 20, hex_size: int = 30):
        self.width = width  # number of columns (q-axis)
        self.height = height  # number of rows (r-axis)
        self.hex_size = hex_size  # radius of each hexagon
        self.grid = {}  # dictionary to store hex tiles by (q, r) coordinates
        self.hexes = []  # list of all hex tiles
        
        # Generate the hexagonal grid
        self.generate_grid()
        
    def generate_grid(self):
        """Generate the hexagonal grid with random terrain."""
        for q in range(self.width):
            for r in range(self.height):
                # Create a hex tile with random terrain
                import random
                terrain_types = ["plain", "hills", "woods", "swamp", "water"]
                terrain = random.choice(terrain_types)
                hex_tile = HexTile(q, r, terrain)
                
                # Calculate pixel coordinates with appropriate offsets for horizontal layout
                # Position the grid starting from top-left of the screen area
                offset_x = self.hex_size * 1.5  # Add some margin from the left edge
                offset_y = self.hex_size * math.sqrt(3)  # Add some margin from the top edge
                
                hex_tile.center_x, hex_tile.center_y = hex_tile.axial_to_pixel(
                    self.hex_size, offset_x, offset_y
                )
                
                # Calculate vertices for drawing
                hex_tile.vertices = self.calculate_hex_vertices(
                    hex_tile.center_x, hex_tile.center_y, self.hex_size
                )
                
                # Store the hex tile
                self.grid[(q, r)] = hex_tile
                self.hexes.append(hex_tile)
    
    def calculate_hex_vertices(self, center_x: float, center_y: float, size: int) -> List[Tuple[float, float]]:
        """Calculate the 6 vertices of a flat-topped hexagon."""
        vertices = []
        for i in range(6):
            # For flat-topped hexagons, we start at 30 degrees to get flat sides at top/bottom
            # This gives us: 30°, 90°, 150°, 210°, 270°, 330°
            # This creates a hexagon with flat top and bottom
            angle_deg = 60 * i + 30
            angle_rad = math.pi / 180 * angle_deg
            x = center_x + size * math.cos(angle_rad)
            y = center_y + size * math.sin(angle_rad)
            vertices.append((x, y))
        return vertices
    
    def get_neighbors(self, hex_tile: HexTile) -> List[HexTile]:
        """Get neighboring hex tiles for flat-topped orientation."""
        # For flat-topped hexes, the neighbor directions are:
        # Right, Bottom-right, Bottom-left, Left, Top-left, Top-right
        directions = [
            (+1, 0),  # right
            (0, +1),  # bottom-right
            (-1, +1), # bottom-left
            (-1, 0),  # left
            (0, -1),  # top-left
            (+1, -1)  # top-right
        ]
        
        neighbors = []
        for dq, dr in directions:
            neighbor_q = hex_tile.q + dq
            neighbor_r = hex_tile.r + dr
            neighbor_coords = (neighbor_q, neighbor_r)
            
            if neighbor_coords in self.grid:
                neighbors.append(self.grid[neighbor_coords])
        
        return neighbors
    
    def get_hex_at(self, q: int, r: int) -> Optional[HexTile]:
        """Get the hex tile at the specified coordinates."""
        return self.grid.get((q, r))
    
    def draw(self, screen: pygame.Surface):
        """Draw the hexagonal grid to the screen."""
        for hex_tile in self.hexes:
            # Define colors for different terrain types
            terrain_colors = {
                "plain": (144, 238, 144),    # light green
                "hills": (139, 69, 19),     # brown
                "woods": (0, 100, 0),       # dark green
                "swamp": (160, 120, 40),    # swamp brown
                "water": (64, 164, 223)     # light blue
            }
            
            color = terrain_colors.get(hex_tile.terrain_type, (200, 200, 200))  # default gray
            
            # Draw the hexagon
            if len(hex_tile.vertices) >= 6:
                pygame.draw.polygon(screen, color, hex_tile.vertices)
                pygame.draw.polygon(screen, (0, 0, 0), hex_tile.vertices, 2)  # black border
                
                # Optional: Draw coordinates in the center of each hex
                # font = pygame.font.SysFont(None, 18)
                # text = font.render(f"{hex_tile.q},{hex_tile.r}", True, (0, 0, 0))
                # screen.blit(text, (hex_tile.center_x - 15, hex_tile.center_y - 10))