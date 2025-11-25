"""Test hex distance calculation for even-q vertical layout."""

def calculate_hex_distance(x1: int, y1: int, x2: int, y2: int) -> int:
    """Calculate hex distance using even-q vertical layout."""
    # Convert even-q offset to cube coordinates
    q1 = x1
    r1 = y1 - (x1 + (x1 & 1)) // 2

    q2 = x2
    r2 = y2 - (x2 + (x2 & 1)) // 2

    # Cube distance
    distance = (abs(q1 - q2) + abs(r1 - r2) + abs(q1 + r1 - q2 - r2)) // 2

    return distance


def test_neighbors():
    """Test that hex (1, 8) has correct neighbors at distance 1."""
    # Unit at position (1, 8)
    center_x, center_y = 1, 8

    # Expected neighbors for even-q vertical layout
    # For odd column (1), neighbors are:
    expected_neighbors = [
        (0, 7),  # NW
        (1, 7),  # N
        (2, 7),  # NE
        (0, 8),  # SW
        (2, 8),  # SE
        (1, 9),  # S
    ]

    # Should NOT be neighbors
    non_neighbors = [
        (0, 9),  # One row below SW
        (2, 9),  # One row below SE
    ]

    print(f"Testing neighbors of hex ({center_x}, {center_y})")
    print("-" * 50)

    # Test expected neighbors
    print("\nExpected neighbors (distance should be 1):")
    all_correct = True
    for x, y in expected_neighbors:
        dist = calculate_hex_distance(center_x, center_y, x, y)
        status = "OK" if dist == 1 else "FAIL"
        if dist != 1:
            all_correct = False
        print(f"  {status} ({x}, {y}): distance = {dist}")

    # Test non-neighbors
    print("\nNon-neighbors (distance should NOT be 1):")
    for x, y in non_neighbors:
        dist = calculate_hex_distance(center_x, center_y, x, y)
        status = "OK" if dist != 1 else "FAIL"
        if dist == 1:
            all_correct = False
        print(f"  {status} ({x}, {y}): distance = {dist}")

    # Find all hexes at distance 1
    print(f"\nAll hexes at distance 1 from ({center_x}, {center_y}):")
    found_neighbors = []
    for x in range(0, 10):
        for y in range(0, 12):
            if calculate_hex_distance(center_x, center_y, x, y) == 1:
                found_neighbors.append((x, y))

    found_neighbors.sort()
    expected_neighbors_sorted = sorted(expected_neighbors)

    print(f"  Found: {found_neighbors}")
    print(f"  Expected: {expected_neighbors_sorted}")

    if found_neighbors == expected_neighbors_sorted:
        print("\n[PASS] All tests passed!")
    else:
        print("\n[FAIL] Test failed!")
        print(f"  Missing: {set(expected_neighbors_sorted) - set(found_neighbors)}")
        print(f"  Extra: {set(found_neighbors) - set(expected_neighbors_sorted)}")

    return all_correct and found_neighbors == expected_neighbors_sorted


if __name__ == "__main__":
    success = test_neighbors()
    exit(0 if success else 1)
