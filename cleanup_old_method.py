"""
Remove unused _calculate_hex_distance method from tactical_state.py
"""
import re

with open('tactical/tactical_state.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

output_lines = []
skip_lines = False

for i, line in enumerate(lines):
    # Check if this is the old _calculate_hex_distance method
    if re.match(r'^    def  _calculate_hex_distance\(', line):
        print(f"Removing unused method: _calculate_hex_distance (line {i+1})")
        skip_lines = True
        continue

    # Check if we hit the next method (stop skipping)
    if skip_lines and re.match(r'^    def ', line):
        skip_lines = False

    # Add line if not skipping
    if not skip_lines:
        output_lines.append(line)

with open('tactical/tactical_state.py', 'w', encoding='utf-8') as f:
    f.writelines(output_lines)

print(f"Done! Removed {len(lines) - len(output_lines)} lines")
