"""
Animation system for tactical combat.
Handles unit movement and attack animations with smooth interpolation.
"""

from typing import TYPE_CHECKING
import math
from config.constants import TACTICAL_HEX_SIZE

if TYPE_CHECKING:
    from tactical.combat_unit import CombatUnit


class Animation:
    """Base class for all animations."""

    def __init__(self, unit: 'CombatUnit'):
        """
        Initialize animation.

        Args:
            unit: The unit to animate
        """
        self.unit = unit
        self.finished = False

    def update(self, delta_time: float) -> None:
        """
        Update animation state.

        Args:
            delta_time: Time elapsed since last update in seconds
        """
        raise NotImplementedError

    def is_finished(self) -> bool:
        """Check if animation is complete."""
        return self.finished

    def skip(self) -> None:
        """Skip to end of animation."""
        self.finished = True


class MoveAnimation(Animation):
    """Animates unit movement from one hex to another."""

    def __init__(self, unit: 'CombatUnit', target_x: float, target_y: float,
                 speed: float, start_x: float | None = None, start_y: float | None = None):
        """
        Initialize movement animation.

        Args:
            unit: The unit to animate
            target_x: Target display X coordinate (pixels)
            target_y: Target display Y coordinate (pixels)
            speed: Movement speed in hexes per second
            start_x: Optional start X coordinate (defaults to unit.display_x)
            start_y: Optional start Y coordinate (defaults to unit.display_y)
        """
        super().__init__(unit)
        self.start_x = start_x if start_x is not None else unit.display_x
        self.start_y = start_y if start_y is not None else unit.display_y
        self.target_x = target_x
        self.target_y = target_y
        self.speed = speed

        # Calculate total distance and duration
        dx = target_x - self.start_x
        dy = target_y - self.start_y
        self.total_distance = math.sqrt(dx * dx + dy * dy)

        # Calculate pixels per hex (hex height for flat-top hexagons)
        # For flat-top hexagons: height = sqrt(3) * radius
        pixels_per_hex = TACTICAL_HEX_SIZE * math.sqrt(3)
        pixels_per_second = speed * pixels_per_hex
        self.duration = self.total_distance / pixels_per_second if pixels_per_second > 0 else 0
        self.elapsed = 0.0

    def update(self, delta_time: float) -> None:
        """Update movement animation."""
        if self.finished:
            return

        self.elapsed += delta_time

        if self.elapsed >= self.duration:
            # Animation complete
            self.unit.display_x = self.target_x
            self.unit.display_y = self.target_y
            self.finished = True
        else:
            # Linear interpolation
            progress = self.elapsed / self.duration if self.duration > 0 else 1.0
            self.unit.display_x = self.start_x + (self.target_x - self.start_x) * progress
            self.unit.display_y = self.start_y + (self.target_y - self.start_y) * progress

    def skip(self) -> None:
        """Skip to end of movement."""
        self.unit.display_x = self.target_x
        self.unit.display_y = self.target_y
        self.finished = True


class AttackAnimation(Animation):
    """Animates unit attack with forward and backward motion."""

    def __init__(self, unit: 'CombatUnit', target_unit: 'CombatUnit',
                    offset: float, duration: float):
            """
            Initialize attack animation.

            Args:
                unit: The attacking unit
                target_unit: The target unit
                offset: Distance to shift towards target in pixels
                duration: Total animation duration in seconds
            """
            super().__init__(unit)
            
            # Calculate start position from logical grid position
            # This ensures correct position even if display coords haven't caught up
            from tactical.hex_geometry import hex_to_pixel
            start_pixel_x, start_pixel_y = hex_to_pixel(unit.x, unit.y)
            self.start_x = float(start_pixel_x)
            self.start_y = float(start_pixel_y)
            
            self.offset = offset
            self.duration = duration
            self.elapsed = 0.0

            # Calculate direction to target (using target's logical position too)
            target_pixel_x, target_pixel_y = hex_to_pixel(target_unit.x, target_unit.y)
            dx = target_pixel_x - self.start_x
            dy = target_pixel_y - self.start_y
            distance = math.sqrt(dx * dx + dy * dy)

            if distance > 0:
                # Normalize and scale by offset
                self.offset_x = (dx / distance) * offset
                self.offset_y = (dy / distance) * offset
            else:
                self.offset_x = 0
                self.offset_y = 0

    def update(self, delta_time: float) -> None:
        """Update attack animation."""
        if self.finished:
            return

        self.elapsed += delta_time

        if self.elapsed >= self.duration:
            # Animation complete - return to start position
            self.unit.display_x = self.start_x
            self.unit.display_y = self.start_y
            self.finished = True
        else:
            # Progress through animation
            progress = self.elapsed / self.duration

            # Forward for first half, backward for second half
            if progress < 0.5:
                # Moving forward (0 to 1)
                move_progress = progress * 2.0
            else:
                # Moving backward (1 to 0)
                move_progress = 2.0 - (progress * 2.0)

            # Apply offset
            self.unit.display_x = self.start_x + self.offset_x * move_progress
            self.unit.display_y = self.start_y + self.offset_y * move_progress

    def skip(self) -> None:
        """Skip to end of attack."""
        self.unit.display_x = self.start_x
        self.unit.display_y = self.start_y
        self.finished = True


class AnimationQueue:
    """Manages a queue of animations to play sequentially."""

    def __init__(self):
        """Initialize animation queue."""
        self.animations: list[Animation] = []
        self.current_animation: Animation | None = None

    def add(self, animation: Animation) -> None:
        """Add animation to queue."""
        self.animations.append(animation)

    def update(self, delta_time: float) -> None:
        """Update current animation."""
        # Start next animation if none playing
        if self.current_animation is None:
            if self.animations:
                self.current_animation = self.animations.pop(0)
            else:
                return

        # Update current animation
        self.current_animation.update(delta_time)

        # Check if finished
        if self.current_animation.is_finished():
            self.current_animation = None

    def is_playing(self) -> bool:
        """Check if any animation is playing."""
        return self.current_animation is not None or len(self.animations) > 0

    def skip_current(self) -> None:
        """Skip current animation."""
        if self.current_animation:
            self.current_animation.skip()
            self.current_animation = None

    def clear(self) -> None:
        """Clear all animations."""
        self.animations.clear()
        self.current_animation = None
