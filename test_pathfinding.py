"""
Test pathfinding and hex geometry after refactoring.
"""
from tactical.hex_geometry import calculate_hex_distance, hex_to_pixel, pixel_to_hex
from tactical.movement import get_hex_neighbors, get_reachable_cells, find_path

print("=" * 60)
print("Testing Hex Geometry and Pathfinding")
print("=" * 60)

# Test 1: Hex distance calculation (even-q vertical layout)
print("\n1. Testing hex distance calculation:")
test_cases = [
    ((1, 8), (0, 8), 1, "Direct neighbor (left)"),
    ((1, 8), (2, 8), 1, "Direct neighbor (right)"),
    ((1, 8), (1, 7), 1, "Direct neighbor (up)"),
    ((1, 8), (1, 9), 1, "Direct neighbor (down)"),
    ((1, 8), (0, 7), 1, "Diagonal neighbor NW"),
    ((1, 8), (2, 7), 1, "Diagonal neighbor NE"),
    ((0, 0), (0, 5), 5, "Vertical distance"),
    ((0, 0), (5, 0), 5, "Horizontal distance"),
]

all_passed = True
for (pos1, pos2, expected_dist, desc) in test_cases:
    dist = calculate_hex_distance(pos1[0], pos1[1], pos2[0], pos2[1])
    status = "[OK]" if dist == expected_dist else "[FAIL]"
    if dist != expected_dist:
        all_passed = False
    print(f"  {status} {desc}: ({pos1} -> {pos2}) = {dist} (expected {expected_dist})")

# Test 2: Hex neighbors (critical for pathfinding)
print("\n2. Testing hex neighbors (even-q layout):")

# Even column (x=0)
neighbors_0_5 = get_hex_neighbors(0, 5)
expected_0_5 = [(0, 4), (0, 6), (1, 5)]  # Missing left side (x=-1)
print(f"  Position (0, 5) [even col]: {sorted(neighbors_0_5)}")

# Odd column (x=1) - shifted up
neighbors_1_8 = get_hex_neighbors(1, 8)
expected_1_8 = [(1, 7), (1, 9), (0, 7), (2, 7), (0, 8), (2, 8)]
print(f"  Position (1, 8) [odd col]:  {sorted(neighbors_1_8)}")
print(f"    Expected: {sorted(expected_1_8)}")
if sorted(neighbors_1_8) == sorted(expected_1_8):
    print(f"    [OK] Correct!")
else:
    print(f"    [FAIL] MISMATCH!")
    all_passed = False

# Test 3: Pixel conversion
print("\n3. Testing hex-to-pixel conversion:")
pixel_coords = hex_to_pixel(5, 5)
back_to_hex = pixel_to_hex(pixel_coords[0], pixel_coords[1])
print(f"  Hex (5, 5) -> Pixel {pixel_coords} -> Hex {back_to_hex}")
if back_to_hex == (5, 5):
    print(f"    [OK] Round-trip successful!")
else:
    print(f"    [FAIL] Round-trip failed!")
    all_passed = False

# Test 4: Reachable cells (BFS pathfinding)
print("\n4. Testing reachable cells (BFS):")
start_pos = (5, 5)
movement_range = 2
blocked = set()
reachable = get_reachable_cells(start_pos[0], start_pos[1], movement_range, blocked)
print(f"  From (5, 5) with range 2: {len(reachable)} cells reachable")
print(f"  Sample cells: {list(reachable.items())[:5]}")

# Verify distance
for pos, dist in list(reachable.items())[:10]:
    actual_dist = calculate_hex_distance(start_pos[0], start_pos[1], pos[0], pos[1])
    if actual_dist != dist:
        print(f"    [FAIL] ERROR: {pos} has stored dist={dist} but actual={actual_dist}")
        all_passed = False

# Test 5: Find path
print("\n5. Testing pathfinding (find_path):")
start = (0, 0)
goal = (3, 3)
path = find_path(start, goal, blocked)
if path:
    print(f"  Path from {start} to {goal}: {path}")
    print(f"    Length: {len(path)} steps")

    # Verify each step is a neighbor of the previous
    # Path includes start position, so skip first element
    valid_path = True
    for i in range(1, len(path)):
        prev = path[i-1]
        current = path[i]
        neighbors = get_hex_neighbors(prev[0], prev[1])
        if current not in neighbors:
            print(f"    [FAIL] ERROR: {current} is not a neighbor of {prev}")
            valid_path = False
            all_passed = False

    if valid_path:
        print(f"    [OK] Path is valid (all steps are neighbors)")
else:
    print(f"  [FAIL] No path found!")
    all_passed = False

# Test 6: Pathfinding with obstacles
print("\n6. Testing pathfinding with obstacles:")
start = (0, 0)
goal = (2, 0)
blocked = {(1, 0)}  # Block direct path
path_with_obstacle = find_path(start, goal, blocked)
if path_with_obstacle:
    print(f"  Path from {start} to {goal} (obstacle at (1,0)): {path_with_obstacle}")
    if (1, 0) in path_with_obstacle:
        print(f"    [FAIL] ERROR: Path goes through blocked cell!")
        all_passed = False
    else:
        print(f"    [OK] Path correctly avoids obstacle")
else:
    print(f"  [FAIL] No path found (should find alternate route)")
    all_passed = False

# Summary
print("\n" + "=" * 60)
if all_passed:
    print("[OK] ALL TESTS PASSED - Pathfinding system intact!")
else:
    print("[FAIL] SOME TESTS FAILED - Check errors above")
print("=" * 60)
