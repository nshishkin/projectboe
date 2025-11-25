"""
Script to remove old geometry methods and replace their calls
"""
import re

# Read the file
with open('tactical/tactical_state.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace method calls
print("Replacing method calls...")
replacements = [
    (r'self\._hex_to_pixel\(', 'hex_to_pixel('),
    (r'self\._pixel_to_hex\(', 'pixel_to_hex('),
    (r'self\._get_hex_corners\(', 'get_hex_corners('),
    (r'self\._calculate_hex_distance\(', 'calculate_hex_distance('),
]

for pattern, replacement in replacements:
    count = len(re.findall(pattern, content))
    if count > 0:
        print(f"  {pattern} -> {replacement}: {count} occurrences")
        content = re.sub(pattern, replacement, content)

# Now remove the old method definitions
print("\nRemoving old geometry methods...")
methods_to_remove = ['_get_hex_corners', '_hex_to_pixel', '_pixel_to_hex', '_calculate_hex_distance']

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
            print(f"  Removing method: {method_name}")
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
