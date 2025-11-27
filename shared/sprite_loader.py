"""
Sprite loading utilities.
Handles loading and caching of game sprites (terrain tiles, units, etc.)
"""
import pygame
import os
from typing import Dict, Optional

class SpriteLoader:
    """
    Centralized sprite loading and caching system.
    """

    def __init__(self):
        """Initialize sprite loader with empty cache."""
        self._cache: Dict[str, pygame.Surface] = {}
        self.base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'images')

    def load_sprite(self, relative_path: str, size: Optional[tuple[int, int]] = None, rotate: float = 0) -> Optional[pygame.Surface]:
        """
        Load a sprite from disk or return cached version.

        Args:
            relative_path: Path relative to assets/images/ (e.g., 'terrain/strategic/plains.png')
            size: Optional (width, height) to scale sprite to
            rotate: Rotation angle in degrees (positive = counter-clockwise)

        Returns:
            Pygame Surface with loaded sprite, or None if file not found
        """
        # Create cache key including size and rotation
        cache_key = f"{relative_path}_{size}_{rotate}"

        # Return cached version if available
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Build full path
        full_path = os.path.join(self.base_path, relative_path)

        # Try to load the image
        try:
            sprite = pygame.image.load(full_path).convert_alpha()

            # Rotate if angle specified (before scaling to preserve quality)
            if rotate:
                sprite = pygame.transform.rotate(sprite, rotate)

            # Scale if size specified
            if size:
                sprite = pygame.transform.scale(sprite, size)

            # Cache and return
            self._cache[cache_key] = sprite
            return sprite

        except (pygame.error, FileNotFoundError) as e:
            print(f"Warning: Could not load sprite '{relative_path}': {e}")
            return None

    def load_terrain_sprite(self, terrain_type: str, layer: str = 'strategic',
                           size: Optional[tuple[int, int]] = None, rotate: float = 0) -> Optional[pygame.Surface]:
        """
        Load terrain sprite for strategic or tactical layer.

        Args:
            terrain_type: Terrain type ('plains', 'forest', 'swamp', 'hills', etc.)
            layer: 'strategic' or 'tactical'
            size: Optional size to scale to
            rotate: Rotation angle in degrees (use 30 to convert corner-top to flat-top hex)

        Returns:
            Pygame Surface or None
        """
        path = f"terrain/{layer}/{terrain_type}.png"
        return self.load_sprite(path, size, rotate)

    def load_unit_sprite(self, unit_type: str, size: Optional[tuple[int, int]] = None) -> Optional[pygame.Surface]:
        """
        Load unit sprite.

        Args:
            unit_type: Unit type ('infantry', 'cavalry', 'ranged', etc.)
            size: Optional size to scale to

        Returns:
            Pygame Surface or None
        """
        path = f"units/{unit_type}.png"
        return self.load_sprite(path, size)

    def clear_cache(self):
        """Clear all cached sprites (useful for memory management)."""
        self._cache.clear()


# Global sprite loader instance
_sprite_loader = None

def get_sprite_loader() -> SpriteLoader:
    """Get global sprite loader instance (singleton pattern)."""
    global _sprite_loader
    if _sprite_loader is None:
        _sprite_loader = SpriteLoader()
    return _sprite_loader
