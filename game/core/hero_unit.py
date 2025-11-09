"""
Hero unit system for Brothers of Eador.
Manages individual hero units with position, stats, and movement capabilities.
"""

from enum import Enum
from typing import List, Tuple, Optional


class HeroFaction(Enum):
    """Enumeration of possible hero factions."""
    PLAYER = "player"
    ENEMY = "enemy"
    NEUTRAL = "neutral"
    ALLY = "ally"


class HeroUnit:
    """Represents a single hero unit with position, stats, and movement capabilities."""
    
    def __init__(self, 
                 name: str = "Hero", 
                 q: int = 0, 
                 r: int = 0, 
                 faction: HeroFaction = HeroFaction.PLAYER,
                 hero_class: str = "warrior",
                 health: int = 100,
                 max_health: int = 100,
                 movement_points: int = 5,
                 max_movement_points: int = 5,
                 level: int = 1):
        """
        Initialize a hero unit.
        
        Args:
            name: Name of the hero
            q: Axial coordinate q on the hex grid
            r: Axial coordinate r on the hex grid
            faction: Faction the hero belongs to
            hero_class: Class of the hero (warrior, mage, etc.)
            health: Current health points
            max_health: Maximum health points
            movement_points: Current movement points
            max_movement_points: Maximum movement points
            level: Hero level
        """
        self.name = name
        self.q = q
        self.r = r
        self.faction = faction
        self.hero_class = hero_class
        self.health = health
        self.max_health = max_health
        self.movement_points = movement_points
        self.max_movement_points = max_movement_points
        self.level = level
        self.has_moved_this_turn = False
        self.inventory = []
        self.abilities = []
        
    def move_to(self, q: int, r: int) -> bool:
        """
        Move the hero to a new position.
        
        Args:
            q: New q coordinate
            r: New r coordinate
            
        Returns:
            True if move was successful, False otherwise
        """
        self.q = q
        self.r = r
        self.has_moved_this_turn = True
        return True
    
    def reset_movement_points(self):
        """Reset movement points to maximum at the start of a turn."""
        self.movement_points = self.max_movement_points
        self.has_moved_this_turn = False
    
    def spend_movement_points(self, points: int) -> bool:
        """
        Spend movement points.
        
        Args:
            points: Number of points to spend
            
        Returns:
            True if enough points were available, False otherwise
        """
        if self.movement_points >= points:
            self.movement_points -= points
            return True
        return False
    
    def can_move_to(self, target_hex, terrain_movement_cost) -> bool:
        """
        Check if hero can move to a target hex based on movement points.
        
        Args:
            target_hex: Target hex to move to
            terrain_movement_cost: Dictionary mapping terrain types to movement costs
            
        Returns:
            True if hero can move to the target hex, False otherwise
        """
        if self.has_moved_this_turn:
            return False
            
        movement_cost = terrain_movement_cost.get(target_hex.terrain_type, 2)
        return self.movement_points >= movement_cost


class HeroManager:
    """Manages multiple hero units for different factions."""
    
    def __init__(self):
        self.heroes: List[HeroUnit] = []
        self.selected_hero: Optional[HeroUnit] = None
    
    def add_hero(self, hero: HeroUnit):
        """Add a hero to the manager."""
        self.heroes.append(hero)
        # If no hero is selected yet, select the first one
        if self.selected_hero is None:
            self.selected_hero = hero
    
    def remove_hero(self, hero: HeroUnit):
        """Remove a hero from the manager."""
        if hero in self.heroes:
            self.heroes.remove(hero)
            if self.selected_hero == hero:
                # Select another hero from the same faction if possible
                for h in self.heroes:
                    if h.faction == hero.faction:
                        self.selected_hero = h
                        break
                else:
                    # If no other hero from the same faction, select any hero
                    self.selected_hero = self.heroes[0] if self.heroes else None
    
    def get_heroes_by_faction(self, faction: HeroFaction) -> List[HeroUnit]:
        """Get all heroes belonging to a specific faction."""
        return [hero for hero in self.heroes if hero.faction == faction]
    
    def get_hero_at_position(self, q: int, r: int) -> Optional[HeroUnit]:
        """Get the hero at a specific position."""
        for hero in self.heroes:
            if hero.q == q and hero.r == r:
                return hero
        return None
    
    def select_hero(self, hero: HeroUnit) -> bool:
        """
        Select a hero as the active hero.
        
        Args:
            hero: Hero to select
            
        Returns:
            True if selection was successful, False otherwise
        """
        if hero in self.heroes:
            self.selected_hero = hero
            return True
        return False
    
    def get_available_moves(self, hero: HeroUnit, strategic_map, terrain_movement_cost) -> List[Tuple[int, int]]:
        """
        Get all available moves for a hero based on movement points.
        
        Args:
            hero: Hero to check moves for
            strategic_map: The strategic map to check against
            terrain_movement_cost: Dictionary mapping terrain types to movement costs
            
        Returns:
            List of (q, r) coordinates that the hero can move to
        """
        if not hero or hero.has_moved_this_turn:
            return []
        
        available_moves = []
        # Check all adjacent hexes
        current_hex = strategic_map.get_hex_at(hero.q, hero.r)
        if not current_hex:
            return []
        
        # Check immediate neighbors
        neighbors = strategic_map.get_neighbors(current_hex)
        for neighbor_hex in neighbors:
            movement_cost = terrain_movement_cost.get(neighbor_hex.terrain_type, 2)
            if hero.movement_points >= movement_cost and neighbor_hex.is_passable:
                available_moves.append((neighbor_hex.q, neighbor_hex.r))
        
        return available_moves