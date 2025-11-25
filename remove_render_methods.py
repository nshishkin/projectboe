"""
Script to remove ONLY rendering methods from tactical_state.py
"""
import re

# Read the file
with open('tactical/tactical_state.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Methods to remove (rendering only)
methods_to_remove = {
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
}

output_lines = []
current_method = None
skip_lines = False
indent_level = 0

for i, line in enumerate(lines):
    # Check if this is a method definition
    match = re.match(r'^    def (\w+)\(', line)

    if match:
        method_name = match.group(1)

        # If we were skipping a method, stop now
        skip_lines = False

        # Check if this new method should be skipped
        if method_name in methods_to_remove:
            print(f"Removing method: {method_name} (line {i+1})")
            skip_lines = True
            current_method = method_name
            continue  # Don't add this line
        else:
            current_method = method_name

    # Add line if we're not skipping
    if not skip_lines:
        output_lines.append(line)

# Write the output
with open('tactical/tactical_state.py', 'w', encoding='utf-8') as f:
    f.writelines(output_lines)

print(f"\nDone! Removed {len(methods_to_remove)} methods")
print(f"Original: {len(lines)} lines")
print(f"New: {len(output_lines)} lines")
print(f"Removed: {len(lines) - len(output_lines)} lines")
