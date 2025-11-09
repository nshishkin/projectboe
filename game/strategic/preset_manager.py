"""
Strategic map preset system for configurable terrain generation.
Handles different map templates and their specific terrain distributions.
"""

from typing import Dict, Any, List
from game.core.terrain_manager import TerrainWeightManager


class MapPreset:
    """Represents a strategic map preset with specific terrain distribution."""
    
    def __init__(self, name: str, terrain_weights: Dict[str, float], constraints: Dict[str, Any] = None):
        """
        Initialize a map preset.
        
        Args:
            name: Name of the preset
            terrain_weights: Dictionary mapping terrain types to their weights
            constraints: Dictionary of constraints to apply to the map
        """
        self.name = name
        self.terrain_weights = terrain_weights
        self.constraints = constraints or {}
    
    def create_weight_manager(self) -> TerrainWeightManager:
        """Create a TerrainWeightManager configured for this preset."""
        return TerrainWeightManager(self.terrain_weights)
    
    def get_constraints(self) -> Dict[str, Any]:
        """Get the constraints for this preset."""
        return self.constraints.copy()


class PresetManager:
    """Manages different strategic map presets."""
    
    def __init__(self):
        self.presets = {}
        self._initialize_presets()
    
    def _initialize_presets(self):
        """Initialize the default map presets."""
        # Plains/Farmland preset - mostly plains with some woods and hills
        plains_preset = MapPreset(
            name="plains",
            terrain_weights={
                'plain': 0.5,
                'hills': 0.2,
                'woods': 0.2,
                'swamp': 0.05,
                'water': 0.03,
                'mountains': 0.02
            },
            constraints={
                'min_plain': 10,
                'max_mountains': 5
            }
        )
        
        # Mountainous preset - lots of mountains and hills, some woods
        mountainous_preset = MapPreset(
            name="mountainous",
            terrain_weights={
                'mountains': 0.4,
                'hills': 0.3,
                'woods': 0.2,
                'plain': 0.1,
                'swamp': 0.0,
                'water': 0.0
            },
            constraints={
                'min_mountains': 8,
                'no_swamp': True,
                'no_water': True
            }
        )
        
        # Forest preset - lots of woods with hills and some plains
        forest_preset = MapPreset(
            name="forest",
            terrain_weights={
                'woods': 0.5,
                'hills': 0.2,
                'plain': 0.2,
                'swamp': 0.05,
                'water': 0.03,
                'mountains': 0.02
            },
            constraints={
                'min_woods': 12,
                'max_mountains': 3
            }
        )
        
        # Coastal preset - balanced with emphasis on water
        coastal_preset = MapPreset(
            name="coastal",
            terrain_weights={
                'water': 0.3,
                'plain': 0.3,
                'hills': 0.2,
                'swamp': 0.15,
                'woods': 0.04,
                'mountains': 0.01
            },
            constraints={
                'min_water': 10,
                'min_plain': 5
            }
        )
        
        # Wetlands preset - lots of swamps and water
        wetlands_preset = MapPreset(
            name="wetlands",
            terrain_weights={
                'swamp': 0.5,
                'water': 0.3,
                'woods': 0.15,
                'plain': 0.04,
                'hills': 0.01,
                'mountains': 0.0
            },
            constraints={
                'min_swamp': 15,
                'no_mountains': True
            }
        )
        
        # Balanced preset - even distribution of all terrain types
        balanced_preset = MapPreset(
            name="balanced",
            terrain_weights={
                'plain': 0.25,
                'hills': 0.2,
                'woods': 0.2,
                'swamp': 0.15,
                'water': 0.15,
                'mountains': 0.05
            }
        )
        
        # Add all presets to the manager
        self.presets['plains'] = plains_preset
        self.presets['mountainous'] = mountainous_preset
        self.presets['forest'] = forest_preset
        self.presets['coastal'] = coastal_preset
        self.presets['wetlands'] = wetlands_preset
        self.presets['balanced'] = balanced_preset
    
    def get_preset(self, name: str) -> MapPreset:
        """Get a preset by name."""
        return self.presets.get(name)
    
    def get_all_preset_names(self) -> List[str]:
        """Get a list of all available preset names."""
        return list(self.presets.keys())
    
    def create_custom_preset(self, name: str, terrain_weights: Dict[str, float], 
                           constraints: Dict[str, Any] = None) -> MapPreset:
        """Create and register a custom preset."""
        preset = MapPreset(name, terrain_weights, constraints)
        self.presets[name] = preset
        return preset
    
    def get_weight_manager_for_preset(self, preset_name: str) -> TerrainWeightManager:
        """Get a TerrainWeightManager configured for a specific preset."""
        preset = self.get_preset(preset_name)
        if preset:
            return preset.create_weight_manager()
        else:
            # Return a default weight manager if preset not found
            return TerrainWeightManager()
    
    def get_constraints_for_preset(self, preset_name: str) -> Dict[str, Any]:
        """Get the constraints for a specific preset."""
        preset = self.get_preset(preset_name)
        if preset:
            return preset.get_constraints()
        else:
            return {}


# Global preset manager instance
preset_manager = PresetManager()


def get_preset_manager() -> PresetManager:
    """Get the global preset manager instance."""
    return preset_manager