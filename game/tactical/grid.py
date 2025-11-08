"""
Hexagonal grid system for tactical combat in Brothers of Eador.
Implements a hexagonal grid with axial coordinates for the tactical map.
"""
import pygame
import math
import random  # Импорт перемещен из функции generate_grid
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
        """Convert cube coordinates to pixel coordinates (point-topped orientation)."""
        x = hex_size * math.sqrt(3) * self.q
        y = hex_size * 3/2 * self.r
        if self.r % 2 != 0:  # Odd rows
            x += hex_size * math.sqrt(3) / 2
        return x, y
        
    def axial_to_pixel(self, hex_size: int, offset_x: float = 0, offset_y: float = 0) -> Tuple[float, float]:
        """Convert axial coordinates to pixel coordinates with offset (point-topped orientation)."""
        x = hex_size * math.sqrt(3) * self.q + offset_x
        y = hex_size * 3/2 * self.r + offset_y
        if self.r % 2 != 0:  # Odd rows
            x += hex_size * math.sqrt(3) / 2
        return x, y


class HexGrid:
    """Hexagonal grid system for tactical combat."""
    
    def __init__(self, width: int = 10, height: int = 20, hex_size: int = None):
        from config.settings import HEX_SIZE
        # Use the default hex size from settings if not provided
        if hex_size is None:
            hex_size = HEX_SIZE
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
                terrain_types = ["plain", "hills", "woods", "swamp", "water"]
                terrain = random.choice(terrain_types)
                hex_tile = HexTile(q, r, terrain)
                
                # Calculate pixel coordinates with appropriate offsets for horizontal layout
                # Position the grid starting from top-left of the screen area
                # Add margins to ensure the grid fits well within the view
                offset_x = self.hex_size * 2  # Add margin from the left edge
                offset_y = self.hex_size * 1.5  # Add margin from the top edge
                
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
        """Calculate the 6 vertices of a point-topped hexagon."""
        vertices = []
        for i in range(6):
            # For point-topped hexagons, we start at 30 degrees to get points at top/bottom
            # This gives us: 30°, 90°, 150°, 210°, 270°, 330°
            # This creates a hexagon with points at top and bottom
            angle_deg = 60 * i + 30
            angle_rad = math.pi / 180 * angle_deg
            x = center_x + size * math.cos(angle_rad)
            y = center_y + size * math.sin(angle_rad)
            vertices.append((x, y))
        return vertices
    
    def get_neighbors(self, hex_tile: HexTile) -> List[HexTile]:
        """Get neighboring hex tiles for point-topped orientation."""
        # For point-topped hexes, the neighbor directions are:
        # Top, Top-right, Bottom-right, Bottom-left, Top-left
        directions = [
            (0, -1),  # top
            (+1, -1), # top-right
            (+1, 0),  # bottom-right
            (0, +1),  # bottom
            (-1, +1), # bottom-left
            (-1, 0),  # top-left
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