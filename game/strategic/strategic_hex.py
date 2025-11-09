"""
Strategic hex system for Brothers of Eador.
Implements enhanced hexagonal tiles for the strategic map with buildings, encounters, etc.
"""

import pygame
import math
from typing import List, Tuple, Optional, Dict, Any
from config.constants import TERRAIN_TYPES, TERRAIN_COLORS
from ..core.terrain_manager import TerrainWeightManager, ConstraintValidator
from .preset_manager import get_preset_manager


class StrategicHex:
    """Represents a single hexagonal tile in the strategic map with enhanced functionality."""
    
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
        self.is_passable = self._is_terrain_passable()  # Determine if the terrain is passable by units
        
        # Strategic map specific attributes
        self.buildings = []  # List of buildings on this hex
        self.encounters = []  # List of potential encounters
        self.units = []  # Units currently on this hex
        self.resources = {}  # Resources available on this hex
        self.ownership = None  # Which faction controls this hex
        self.has_road = False  # Whether this hex has a road connection
        self.fortification_level = 0  # Level of fortification (0 = none)
        
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

    def _is_terrain_passable(self) -> bool:
        """Determine if the terrain type is passable by units."""
        # Mountains are impassable, water may be as well depending on game rules
        impassable_terrains = {"mountains"}  # Add "water" here if water should be impassable
        return self.terrain_type not in impassable_terrains
    
    def add_building(self, building_type: str, level: int = 1) -> None:
        """Add a building to this hex."""
        building = {
            'type': building_type,
            'level': level,
            'is_active': True,
            'hp': self._calculate_building_hp(building_type, level)
        }
        self.buildings.append(building)
    
    def remove_building(self, building_type: str) -> bool:
        """Remove a building from this hex."""
        for i, building in enumerate(self.buildings):
            if building['type'] == building_type:
                del self.buildings[i]
                return True
        return False
    
    def upgrade_building(self, building_type: str) -> bool:
        """Upgrade a building on this hex."""
        for building in self.buildings:
            if building['type'] == building_type:
                building['level'] += 1
                building['hp'] = self._calculate_building_hp(building_type, building['level'])
                return True
        return False
    
    def _calculate_building_hp(self, building_type: str, level: int) -> int:
        """Calculate HP for a building based on type and level."""
        base_hp = {
            'fort': 100,
            'watchtower': 50,
            'barracks': 80,
            'farm': 60,
            'mine': 70,
            'lumbermill': 65,
            'temple': 75,
            'market': 85
        }
        return base_hp.get(building_type, 50) * level
    
    def get_building(self, building_type: str) -> Optional[Dict[str, Any]]:
        """Get a specific building from this hex."""
        for building in self.buildings:
            if building['type'] == building_type:
                return building
        return None
    
    def has_building(self, building_type: str) -> bool:
        """Check if this hex has a specific building."""
        return any(building['type'] == building_type for building in self.buildings)
    
    def get_building_income(self) -> Dict[str, int]:
        """Calculate income from all buildings on this hex."""
        income = {}
        for building in self.buildings:
            if building['is_active']:
                building_income = self._get_building_income(building['type'], building['level'])
                for resource, amount in building_income.items():
                    if resource in income:
                        income[resource] += amount
                    else:
                        income[resource] = amount
        return income
    
    def _get_building_income(self, building_type: str, level: int) -> Dict[str, int]:
        """Get income generated by a specific building type and level."""
        base_income = {
            'fort': {'gold': 2 * level, 'control': 1 * level},
            'watchtower': {'sight': 1 * level},
            'barracks': {'units': 1 * level},
            'farm': {'food': 3 * level, 'gold': 1 * level},
            'mine': {'gold': 4 * level, 'materials': 2 * level},
            'lumbermill': {'materials': 3 * level, 'gold': 1 * level},
            'temple': {'faith': 2 * level, 'gold': 1 * level},
            'market': {'gold': 3 * level, 'trade': 1 * level}
        }
        return base_income.get(building_type, {})
    
    def add_encounter(self, encounter_type: str, encounter_data: Dict[str, Any] = None, chance: float = 1.0) -> None:
        """Add an encounter to this hex."""
        encounter = {
            'type': encounter_type,
            'data': encounter_data or {},
            'is_active': True,
            'chance': chance,  # Chance of encounter occurring (0.0 to 1.0)
            'triggered': False  # Whether this encounter has been triggered
        }
        self.encounters.append(encounter)
    
    def remove_encounter(self, encounter_type: str) -> bool:
        """Remove an encounter from this hex."""
        for i, encounter in enumerate(self.encounters):
            if encounter['type'] == encounter_type:
                del self.encounters[i]
                return True
        return False
    
    def trigger_encounter(self, encounter_type: str) -> Optional[Dict[str, Any]]:
        """Trigger a specific encounter if it exists and chance allows."""
        import random
        for encounter in self.encounters:
            if encounter['type'] == encounter_type and encounter['is_active'] and not encounter['triggered']:
                if random.random() <= encounter['chance']:
                    encounter['triggered'] = True
                    return encounter
        return None
    
    def reset_encounters(self) -> None:
        """Reset all encounters to untriggered state."""
        for encounter in self.encounters:
            encounter['triggered'] = False
    
    def get_random_encounter(self) -> Optional[Dict[str, Any]]:
        """Get a random encounter based on chance."""
        import random
        active_encounters = [enc for enc in self.encounters if enc['is_active'] and not enc['triggered']]
        
        if not active_encounters:
            return None
        
        # Weighted random selection based on chance
        total_chance = sum(enc['chance'] for enc in active_encounters)
        if total_chance == 0:
            return None
        
        rand_val = random.uniform(0, total_chance)
        cumulative = 0
        
        for encounter in active_encounters:
            cumulative += encounter['chance']
            if rand_val <= cumulative:
                encounter['triggered'] = True
                return encounter
        
        # Fallback to last encounter if rounding errors
        if active_encounters:
            active_encounters[-1]['triggered'] = True
            return active_encounters[-1]
        
        return None
    
    def has_encounters(self) -> bool:
        """Check if this hex has any active, untriggered encounters."""
        return any(enc['is_active'] and not enc['triggered'] for enc in self.encounters)
    
    def get_encounter_types(self) -> List[str]:
        """Get a list of all encounter types on this hex."""
        return [enc['type'] for enc in self.encounters]
    
    def add_resource(self, resource_type: str, amount: int) -> None:
        """Add resources to this hex."""
        if resource_type in self.resources:
            self.resources[resource_type] += amount
        else:
            self.resources[resource_type] = amount
    
    def set_ownership(self, faction: str) -> None:
        """Set which faction controls this hex."""
        self.ownership = faction
    
    def set_road(self, has_road: bool = True) -> None:
        """Set whether this hex has a road connection."""
        self.has_road = has_road
    
    def set_fortification(self, level: int) -> None:
        """Set the fortification level of this hex."""
        self.fortification_level = max(0, level)


class StrategicGrid:
    """Strategic hexagonal grid system."""
    
    def __init__(self, width: int = 8, height: int = 8, hex_size: int = None, preset_name: str = "balanced"):
        from config.settings import PROVINCE_SIZE
        # Use the default hex size from settings if not provided
        if hex_size is None:
            hex_size = PROVINCE_SIZE
        self.width = width  # number of columns (q-axis)
        self.height = height  # number of rows (r-axis)
        self.hex_size = hex_size  # radius of each hexagon
        self.grid = {}  # dictionary to store hex tiles by (q, r) coordinates
        self.hexes = []  # list of all hex tiles
        
        # Generate the hexagonal grid with configurable terrain
        self.generate_grid(preset_name)
        
    def generate_grid(self, preset_name: str = "balanced"):
        """Generate the hexagonal grid with configurable terrain."""
        # Get the preset manager
        preset_manager = get_preset_manager()
        
        # Get the weight manager for the specified preset
        weight_manager = preset_manager.get_weight_manager_for_preset(preset_name)
        
        # Get constraints for the preset
        constraints = preset_manager.get_constraints_for_preset(preset_name)
        
        # Apply constraints to the weight manager
        weight_manager.apply_constraints(constraints)
        
        for q in range(self.width):
            for r in range(self.height):
                # Create a hex tile with terrain based on weighted selection
                terrain = weight_manager.get_weighted_choice()
                hex_tile = StrategicHex(q, r, terrain)
                
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
        
        # Validate that constraints are satisfied
        validator = ConstraintValidator()
        if not validator.validate_hard_constraints(self, constraints):
            # If constraints aren't met, try again (with a limit to prevent infinite loops)
            attempts = 0
            max_attempts = 10
            while not validator.validate_hard_constraints(self, constraints) and attempts < max_attempts:
                # Regenerate terrain for each hex
                for hex_tile in self.hexes:
                    q, r = hex_tile.q, hex_tile.r
                    terrain = weight_manager.get_weighted_choice()
                    hex_tile.terrain_type = terrain
                attempts += 1
    
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
    
    def get_neighbors(self, hex_tile: StrategicHex) -> List[StrategicHex]:
        """Get neighboring hex tiles for point-topped orientation."""
        # For point-topped hexes, the neighbor directions are:
        # Top, Top-right, Bottom-left, Top-left
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
    
    def get_hex_at(self, q: int, r: int) -> Optional[StrategicHex]:
        """Get the hex tile at the specified coordinates."""
        return self.grid.get((q, r))
    
    def draw(self, screen: pygame.Surface):
        """Draw the hexagonal grid to the screen."""
        for hex_tile in self.hexes:
            color = TERRAIN_COLORS.get(hex_tile.terrain_type, (200, 200, 200))  # default gray
            
            # Draw the hexagon
            if len(hex_tile.vertices) >= 6:
                pygame.draw.polygon(screen, color, hex_tile.vertices)
                pygame.draw.polygon(screen, (0, 0, 0), hex_tile.vertices, 2)  # black border
                
                # Optional: Draw coordinates in the center of each hex
                # font = pygame.font.SysFont(None, 18)
                # text = font.render(f"{hex_tile.q},{hex_tile.r}", True, (0, 0))
                # screen.blit(text, (hex_tile.center_x - 15, hex_tile.center_y - 10))