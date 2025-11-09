"""
Tactical biome mapper for generating tactical maps based on strategic context.
Maps strategic terrain to tactical preferences for contextually appropriate battles.
"""

from typing import Dict, Any
from game.core.terrain_manager import TerrainWeightManager


class BiomeMapper:
    """Maps strategic terrain to tactical preferences for contextually appropriate battles."""
    
    def __init__(self):
        # Define default influence factors for different strategic terrains
        self.default_influence_factors = {
            'plain': 0.5,      # Plains have moderate influence on tactical maps
            'hills': 0.7,      # Hills have stronger influence
            'woods': 0.8,      # Woods have strong influence
            'swamp': 0.9,      # Swamps have very strong influence
            'water': 0.6,      # Water has moderate influence
            'mountains': 0.9   # Mountains have very strong influence
        }
    
    def create_tactical_weight_manager(self, strategic_terrain: str, 
                                     custom_influence: float = None) -> TerrainWeightManager:
        """
        Create a TerrainWeightManager configured for tactical generation based on strategic context.
        
        Args:
            strategic_terrain: The terrain type of the strategic hex where battle occurs
            custom_influence: Custom influence factor (0.0 to 2.0+), if None uses default
            
        Returns:
            Configured TerrainWeightManager for tactical map generation
        """
        # Start with default weights (balanced tactical map)
        base_weights = {
            'plain': 0.25,
            'hills': 0.2,
            'woods': 0.2,
            'swamp': 0.15,
            'water': 0.15,
            'mountains': 0.05
        }
        
        weight_manager = TerrainWeightManager(base_weights)
        
        # Determine influence factor
        if custom_influence is not None:
            influence_factor = custom_influence
        else:
            influence_factor = self.default_influence_factors.get(strategic_terrain, 0.5)
        
        # Apply biome influence based on strategic terrain
        weight_manager.adjust_weights_for_biome(strategic_terrain, influence_factor)
        
        return weight_manager
    
    def get_biome_influence_description(self, strategic_terrain: str) -> str:
        """
        Get a description of how the strategic terrain influences tactical generation.
        
        Args:
            strategic_terrain: The strategic terrain type
            
        Returns:
            Description of the biome influence
        """
        descriptions = {
            'plain': "Tactical battles on plains tend to have more open terrain with moderate amounts of hills and woods.",
            'hills': "Tactical battles in hilly regions feature more elevated terrain with rocky outcroppings and steep areas.",
            'woods': "Tactical battles in forests have dense woodland areas with limited visibility and natural cover.",
            'swamp': "Tactical battles in swamps feature wet, muddy terrain with difficult movement and limited building options.",
            'water': "Tactical battles near water include rivers, lakes, and coastal features affecting movement and positioning.",
            'mountains': "Tactical battles in mountains have steep cliffs, rocky terrain, and challenging movement."
        }
        
        return descriptions.get(strategic_terrain, f"Tactical battles in {strategic_terrain} areas reflect the strategic terrain type.")
    
    def adjust_for_tactical_requirements(self, weight_manager: TerrainWeightManager, 
                                      requirements: Dict[str, Any]) -> TerrainWeightManager:
        """
        Adjust terrain weights based on tactical requirements.
        
        Args:
            weight_manager: The TerrainWeightManager to adjust
            requirements: Tactical requirements like 'defensive', 'open', etc.
            
        Returns:
            Adjusted TerrainWeightManager
        """
        # Create a copy to avoid modifying the original
        adjusted_manager = TerrainWeightManager(weight_manager.base_weights)
        adjusted_manager.current_weights = weight_manager.current_weights.copy()
        
        # Apply tactical requirement adjustments
        if requirements.get('defensive', False):
            # Increase terrain that provides defensive bonuses (hills, woods)
            adjusted_manager.multiply_terrain_weight('hills', 1.5)
            adjusted_manager.multiply_terrain_weight('woods', 1.3)
            # Reduce open terrain
            adjusted_manager.multiply_terrain_weight('plain', 0.8)
        
        if requirements.get('open', False):
            # Increase open terrain for ranged combat
            adjusted_manager.multiply_terrain_weight('plain', 1.5)
            # Reduce cover terrain
            adjusted_manager.multiply_terrain_weight('woods', 0.7)
            adjusted_manager.multiply_terrain_weight('hills', 0.8)
        
        if requirements.get('water_access', False):
            # Increase water terrain for naval or river battles
            adjusted_manager.multiply_terrain_weight('water', 2.0)
        
        if requirements.get('resource_rich', False):
            # Increase terrain that might contain resources
            adjusted_manager.multiply_terrain_weight('hills', 1.2)  # for mining
            adjusted_manager.multiply_terrain_weight('plain', 1.2)  # for farming
            adjusted_manager.multiply_terrain_weight('swamp', 1.1)  # for special resources
        
        return adjusted_manager


class TacticalTerrainGenerator:
    """Handles tactical-specific terrain generation with strategic context."""
    
    def __init__(self):
        self.biome_mapper = BiomeMapper()
    
    def generate_for_strategic_hex(self, strategic_terrain: str, width: int, height: int,
                                 custom_influence: float = None,
                                 tactical_requirements: Dict[str, Any] = None) -> Dict[str, float]:
        """
        Generate terrain weights for a tactical map based on strategic context.
        
        Args:
            strategic_terrain: The terrain type of the strategic hex
            width: Width of the tactical map
            height: Height of the tactical map
            custom_influence: Custom influence factor
            tactical_requirements: Special tactical requirements
            
        Returns:
            Dictionary of terrain weights for the tactical map
        """
        # Create initial weight manager based on strategic context
        weight_manager = self.biome_mapper.create_tactical_weight_manager(
            strategic_terrain, custom_influence
        )
        
        # Apply tactical requirements if specified
        if tactical_requirements:
            weight_manager = self.biome_mapper.adjust_for_tactical_requirements(
                weight_manager, tactical_requirements
            )
        
        # Return the final weights for generation
        return weight_manager.current_weights.copy()


# Global biome mapper instance
biome_mapper = BiomeMapper()
tactical_generator = TacticalTerrainGenerator()


def get_biome_mapper() -> BiomeMapper:
    """Get the global biome mapper instance."""
    return biome_mapper


def get_tactical_generator() -> TacticalTerrainGenerator:
    """Get the global tactical generator instance."""
    return tactical_generator