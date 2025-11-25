"""
Script to extract rendering methods from tactical_state.py into tactical_renderer.py
"""
import re

# Read tactical_state.py
with open('tactical/tactical_state.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find rendering methods to extract
render_methods = [
    'render',
    '_draw_battlefield',
    '_draw_units',
    '_draw_hp_bar',
    '_highlight_unit',
    '_draw_reachable_cells',
    '_draw_attackable_enemies',
    '_draw_victory_screen',
    '_draw_button',
    '_draw_combat_info',
    '_draw_debug_buttons',
    '_draw_hex_coords',
    '_draw_combat_log',
    '_draw_unit_info_panel',
]

# Extract methods
extracted_methods = {}
current_method = None
method_lines = []
indent_level = 0

for i, line in enumerate(lines):
    # Check if this is a method definition
    match = re.match(r'^    def (\w+)\(', line)
    if match:
        method_name = match.group(1)

        # Save previous method
        if current_method and current_method in render_methods:
            extracted_methods[current_method] = method_lines

        # Start new method
        if method_name in render_methods:
            current_method = method_name
            method_lines = [line]
        else:
            current_method = None
            method_lines = []
    elif current_method:
        # Continue collecting lines for current method
        # Stop when we hit another method at same indent level or class definition
        if line.strip() and not line.startswith('        ') and not line.startswith('    def '):
            # End of method
            if current_method in render_methods:
                extracted_methods[current_method] = method_lines
            current_method = None
            method_lines = []
        else:
            method_lines.append(line)

# Save last method if any
if current_method and current_method in render_methods:
    extracted_methods[current_method] = method_lines

print(f"Extracted {len(extracted_methods)} methods")
for name in extracted_methods:
    print(f"  - {name}: {len(extracted_methods[name])} lines")

# Create tactical_renderer.py
renderer_content = '''"""
Rendering subsystem for tactical combat.

Handles all drawing operations for the tactical combat screen.
"""
import pygame
import math

from tactical.hex_geometry import hex_to_pixel, get_hex_corners
from tactical.combat_unit import CombatUnit
from config.constants import (
    TACTICAL_HEX_SIZE, BATTLEFIELD_ROWS, BATTLEFIELD_COLS,
    BG_COLOR, WHITE, BLACK, GRAY, DARK_GRAY,
    BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_TEXT_COLOR,
    BUTTON_HEIGHT, BUTTON_BORDER_WIDTH
)


class TacticalRenderer:
    """
    Handles all rendering for tactical combat screen.

    Separates drawing logic from game logic for better organization.
    """

    def __init__(self, state):
        """
        Initialize renderer with reference to tactical state.

        Args:
            state: TacticalState instance
        """
        self.state = state
'''

# Add extracted methods to renderer
for method_name in render_methods:
    if method_name in extracted_methods:
        renderer_content += '\n'
        method_lines = extracted_methods[method_name]

        # Adjust each line: replace self with self.state for attributes
        for line in method_lines:
            # Keep method definition as-is (def render(self): stays def render(self):)
            if line.strip().startswith('def '):
                renderer_content += line
            else:
                # Replace self.attribute with self.state.attribute (but not self.state.state)
                # This is a simple heuristic - might need manual adjustment
                adjusted_line = line
                # Replace common patterns
                adjusted_line = adjusted_line.replace('self.screen', 'self.state.screen')
                adjusted_line = adjusted_line.replace('self.battlefield', 'self.state.battlefield')
                adjusted_line = adjusted_line.replace('self.reachable_cells', 'self.state.reachable_cells')
                adjusted_line = adjusted_line.replace('self.attackable_enemies', 'self.state.attackable_enemies')
                adjusted_line = adjusted_line.replace('self.selected_unit', 'self.state.selected_unit')
                adjusted_line = adjusted_line.replace('self.show_hex_coords', 'self.state.show_hex_coords')
                adjusted_line = adjusted_line.replace('self.combat_ended', 'self.state.combat_ended')
                adjusted_line = adjusted_line.replace('self.show_victory_window', 'self.state.show_victory_window')
                adjusted_line = adjusted_line.replace('self.current_round', 'self.state.current_round')
                adjusted_line = adjusted_line.replace('self.winner', 'self.state.winner')
                adjusted_line = adjusted_line.replace('self.ok_button', 'self.state.ok_button')
                adjusted_line = adjusted_line.replace('self.end_turn_button', 'self.state.end_turn_button')
                adjusted_line = adjusted_line.replace('self.debug_finish_button', 'self.state.debug_finish_button')
                adjusted_line = adjusted_line.replace('self.show_coords_button', 'self.state.show_coords_button')
                adjusted_line = adjusted_line.replace('self.animation_time', 'self.state.animation_time')
                adjusted_line = adjusted_line.replace('self.animation_queue', 'self.state.animation_queue')
                adjusted_line = adjusted_line.replace('self.combat_log', 'self.state.combat_log')
                adjusted_line = adjusted_line.replace('self.log_scroll_offset', 'self.state.log_scroll_offset')
                adjusted_line = adjusted_line.replace('self.max_log_messages', 'self.state.max_log_messages')
                adjusted_line = adjusted_line.replace('self.info_unit', 'self.state.info_unit')
                adjusted_line = adjusted_line.replace('self.hovered_unit', 'self.state.hovered_unit')
                adjusted_line = adjusted_line.replace('self.alt_locked_unit', 'self.state.alt_locked_unit')
                adjusted_line = adjusted_line.replace('self.get_current_unit()', 'self.state.get_current_unit()')

                # Keep self._draw* calls as-is (they refer to other methods in same class)
                # Keep self._highlight_unit, self._draw_battlefield etc as self.method()

                renderer_content += adjusted_line

# Write tactical_renderer.py
with open('tactical/tactical_renderer.py', 'w', encoding='utf-8') as f:
    f.write(renderer_content)

print("\nCreated tactical/tactical_renderer.py")
print("Next steps:")
print("1. Review tactical_renderer.py for any missed self. references")
print("2. Update tactical_state.py to use renderer")
print("3. Remove extracted methods from tactical_state.py")
