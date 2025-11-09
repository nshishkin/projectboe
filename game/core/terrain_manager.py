"""
Terrain weight management system for configurable terrain generation.
Handles terrain weights, distributions, and biome influences for both tactical and strategic maps.
"""

import random
from typing import Dict, Any, List, Optional
from config.constants import TERRAIN_TYPES


class TerrainWeightManager:
    """Manages terrain weights and distributions for configurable generation."""
    
    def __init__(self, base_weights: Optional[Dict[str, float]] = None):
        """
        Initialize the terrain weight manager.
        
        Args:
            base_weights: Dictionary mapping terrain types to their base weights.
                         If None, uses equal weights for all terrain types.
        """
        if base_weights is None:
            # Default to equal weights for all terrain types
            self.base_weights = {terrain: 1.0 for terrain in TERRAIN_TYPES}
        else:
            self.base_weights = base_weights.copy()
        
        # Current weights that can be modified by biome influence or constraints
        self.current_weights = self.base_weights.copy()
    
    def reset_weights(self):
        """Reset current weights to base weights."""
        self.current_weights = self.base_weights.copy()
    
    def adjust_weights_for_biome(self, biome_type: str, influence_factor: float = 1.0):
        """
        Adjust weights based on strategic biome influence.
        
        Args:
            biome_type: The strategic terrain type that influences tactical generation
            influence_factor: How strongly the biome affects terrain weights (0.0 to 2.0+)
        """
        # Define biome influence patterns
        biome_influences = {
            'woods': {
                'woods': 2.0,      # Woods terrain gets double weight
                'plain': 0.8,      # Plains slightly reduced
                'hills': 1.2,      # Hills more likely near woods
                'swamp': 1.1,      # Swamps more likely near woods
                'water': 0.5,      # Water less likely
                'mountains': 0.3   # Mountains much less likely
            },
            'hills': {
                'hills': 2.0,      # Hills terrain gets double weight
                'plain': 0.7,      # Plains less likely
                'woods': 1.3,      # Woods more likely with hills
                'swamp': 0.9,      # Swamps slightly reduced
                'water': 0.8,      # Water slightly reduced
                'mountains': 1.5   # Mountains more likely near hills
            },
            'water': {
                'water': 2.0,      # Water terrain gets double weight
                'swamp': 1.8,      # Swamps more likely near water
                'plain': 0.9,      # Plains slightly reduced
                'woods': 0.7,      # Woods less likely
                'hills': 0.6,      # Hills less likely
                'mountains': 0.4   # Mountains much less likely
            },
            'mountains': {
                'mountains': 2.0,  # Mountains get double weight
                'hills': 1.5,      # Hills more likely near mountains
                'plain': 0.5,      # Plains less likely
                'woods': 0.6,      # Woods less likely
                'swamp': 0.4,      # Swamps less likely
                'water': 0.8       # Water slightly reduced
            },
            'swamp': {
                'swamp': 2.0,      # Swamps get double weight
                'water': 1.5,      # Water more likely near swamps
                'woods': 1.2,      # Woods more likely near swamps
                'plain': 0.7,      # Plains less likely
                'hills': 0.5,      # Hills less likely
                'mountains': 0.3   # Mountains much less likely
            },
            'plain': {
                'plain': 1.5,      # Plains get more weight
                'woods': 1.0,      # Normal likelihood
                'hills': 1.0,      # Normal likelihood
                'swamp': 0.8,      # Swamps less likely
                'water': 0.9,      # Water slightly reduced
                'mountains': 0.7   # Mountains less likely
            }
        }
        
        # Get the influence pattern for this biome
        influence_pattern = biome_influences.get(biome_type, {})
        
        # Apply the influence with the specified factor
        for terrain_type in self.current_weights:
            base_weight = self.base_weights[terrain_type]
            influence_multiplier = influence_pattern.get(terrain_type, 1.0)
            
            # Apply the influence factor gradually
            adjusted_multiplier = 1.0 + (influence_multiplier - 1.0) * influence_factor
            self.current_weights[terrain_type] = base_weight * adjusted_multiplier
    
    def apply_constraints(self, constraints: Dict[str, Any]):
        """
        Apply hard constraints to terrain weights.
        
        Args:
            constraints: Dictionary of constraints to apply
        """
        # Handle "no terrain type" constraints (set weight to 0)
        for constraint_key, constraint_value in constraints.items():
            if constraint_key.startswith('no_') and constraint_value is True:
                terrain_type = constraint_key[3:]  # Remove 'no_' prefix
                if terrain_type in self.current_weights:
                    self.current_weights[terrain_type] = 0.0
        
        # Handle minimum terrain requirements
        # These would need to be handled at a higher level since they require
        # guaranteeing certain terrain types appear regardless of weights
        min_constraints = {k: v for k, v in constraints.items() if k.startswith('min_')}
        if min_constraints:
            # This would be handled by the constraint validator during generation
            pass
    
    def get_weighted_choice(self) -> str:
        """
        Return a terrain type based on current weights.
        
        Returns:
            A terrain type string selected according to current weights.
        """
        # Filter out terrains with zero weight
        valid_terrains = {t: w for t, w in self.current_weights.items() if w > 0}
        
        if not valid_terrains:
            # If all weights are zero, return a random terrain
            return random.choice(TERRAIN_TYPES)
        
        terrains = list(valid_terrains.keys())
        weights = list(valid_terrains.values())
        
        # Use random.choices for weighted selection
        chosen_terrain = random.choices(terrains, weights=weights, k=1)[0]
        return chosen_terrain
    
    def get_normalized_weights(self) -> Dict[str, float]:
        """
        Get current weights normalized to sum to 1.0.
        
        Returns:
            Dictionary of terrain types with normalized weights.
        """
        total_weight = sum(self.current_weights.values())
        if total_weight == 0:
            return {terrain: 1.0/len(TERRAIN_TYPES) for terrain in TERRAIN_TYPES}
        
        return {t: w/total_weight for t, w in self.current_weights.items()}
    
    def set_terrain_weight(self, terrain_type: str, weight: float):
        """
        Set a specific terrain weight directly.
        
        Args:
            terrain_type: The terrain type to adjust
            weight: The new weight value
        """
        if terrain_type in self.current_weights:
            self.current_weights[terrain_type] = weight
    
    def multiply_terrain_weight(self, terrain_type: str, multiplier: float):
        """
        Multiply a terrain weight by a factor.
        
        Args:
            terrain_type: The terrain type to adjust
            multiplier: Factor to multiply the current weight by
        """
        if terrain_type in self.current_weights:
            self.current_weights[terrain_type] *= multiplier


class ConstraintValidator:
    """Validates that generated maps meet specified requirements."""
    
    @staticmethod
    def validate_terrain_distribution(map_grid, requirements: Dict[str, Any]) -> bool:
        """
        Check if terrain distribution meets requirements.
        
        Args:
            map_grid: The map grid to validate
            requirements: Dictionary of requirements to check
            
        Returns:
            True if requirements are met, False otherwise
        """
        # Count terrain types in the map
        terrain_counts = {}
        total_hexes = 0
        
        for hex_tile in map_grid.hexes:
            terrain_type = hex_tile.terrain_type
            terrain_counts[terrain_type] = terrain_counts.get(terrain_type, 0) + 1
            total_hexes += 1
        
        # Check percentage requirements
        for req_key, req_value in requirements.items():
            if req_key.endswith('_percent'):
                terrain_type = req_key.replace('_percent', '')
                if terrain_type in terrain_counts:
                    actual_percent = (terrain_counts[terrain_type] / total_hexes) * 100
                    if actual_percent < req_value:
                        return False
        
        # Check absolute count requirements
        for req_key, req_value in requirements.items():
            if req_key.startswith('min_') and not req_key.endswith('_percent'):
                terrain_type = req_key[4:]  # Remove 'min_' prefix
                actual_count = terrain_counts.get(terrain_type, 0)
                if actual_count < req_value:
                    return False
            elif req_key.startswith('max_') and not req_key.endswith('_percent'):
                terrain_type = req_key[4:]  # Remove 'max_' prefix
                actual_count = terrain_counts.get(terrain_type, 0)
                if actual_count > req_value:
                    return False
        
        return True
    
    @staticmethod
    def validate_hard_constraints(map_grid, constraints: Dict[str, Any]) -> bool:
        """
        Validate hard constraints like 'no water' or 'minimum hills'.
        
        Args:
            map_grid: The map grid to validate
            constraints: Dictionary of constraints to check
            
        Returns:
            True if constraints are met, False otherwise
        """
        # Count terrain types in the map
        terrain_counts = {}
        for hex_tile in map_grid.hexes:
            terrain_type = hex_tile.terrain_type
            terrain_counts[terrain_type] = terrain_counts.get(terrain_type, 0) + 1
        
        # Check for "no terrain type" constraints
        for constraint_key, constraint_value in constraints.items():
            if constraint_key.startswith('no_') and constraint_value is True:
                terrain_type = constraint_key[3:]  # Remove 'no_' prefix
                if terrain_counts.get(terrain_type, 0) > 0:
                    return False
        
        # Check minimum constraints
        for constraint_key, constraint_value in constraints.items():
            if constraint_key.startswith('min_') and not constraint_key.endswith('_percent'):
                terrain_type = constraint_key[4:]  # Remove 'min_' prefix
                actual_count = terrain_counts.get(terrain_type, 0)
                if actual_count < constraint_value:
                    return False
        
        # Check maximum constraints
        for constraint_key, constraint_value in constraints.items():
            if constraint_key.startswith('max_') and not constraint_key.endswith('_percent'):
                terrain_type = constraint_key[4:]  # Remove 'max_' prefix
                actual_count = terrain_counts.get(terrain_type, 0)
                if actual_count > constraint_value:
                    return False
        
        return True