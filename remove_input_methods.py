"""
Script to remove input handling methods from tactical_state.py
"""
import re

# Read the file
with open('tactical/tactical_state.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Methods to remove (input handling only)
methods_to_remove = {
    'handle_click',
    'handle_mousewheel',
    '_handle_end_turn',
    '_handle_debug_finish',
    '_handle_victory_ok',
    '_toggle_hex_coords',
}

print("Removing input handling methods...")

lines = content.split('\n')
output_lines = []
skip_lines = False

for i, line in enumerate(lines):
    # Check if this is a method definition
    match = re.match(r'^    def (\w+)\(', line)

    if match:
        method_name = match.group(1)

        # If we were skipping a method, stop now
        skip_lines = False

        # Check if this new method should be skipped
        if method_name in methods_to_remove:
            print(f"  Removing method: {method_name} (line {i+1})")
            skip_lines = True
            continue

    # Add line if we're not skipping
    if not skip_lines:
        output_lines.append(line)

# Write the output
output_content = '\n'.join(output_lines)
with open('tactical/tactical_state.py', 'w', encoding='utf-8') as f:
    f.write(output_content)

print(f"\nDone!")
print(f"Original: {len(lines)} lines")
print(f"New: {len(output_lines)} lines")
print(f"Removed: {len(lines) - len(output_lines)} lines")
