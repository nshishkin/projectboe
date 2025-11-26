"""Extended test for hex distance calculation - even vs odd columns."""

def calculate_hex_distance(x1: int, y1: int, x2: int, y2: int) -> int:
    """Calculate hex distance using even-q vertical layout."""
    q1 = x1
    r1 = y1 - (x1 + (x1 & 1)) // 2

    q2 = x2
    r2 = y2 - (x2 + (x2 & 1)) // 2

    distance = (abs(q1 - q2) + abs(r1 - r2) + abs(q1 + r1 - q2 - r2)) // 2
    return distance


def get_neighbors_even_q(col: int, row: int) -> list[tuple[int, int]]:
    """Get expected neighbors for even-q vertical layout."""
    if col % 2 == 0:  # Even column (upper)
        # Neighbors for even columns
        return [
            (col, row - 1),      # N
            (col + 1, row - 1),  # NE
            (col + 1, row),      # SE
            (col, row + 1),      # S
            (col - 1, row),      # SW
            (col - 1, row - 1),  # NW
        ]
    else:  # Odd column (lower)
        # Neighbors for odd columns
        return [
            (col, row - 1),      # N
            (col + 1, row),      # NE
            (col + 1, row + 1),  # SE
            (col, row + 1),      # S
            (col - 1, row + 1),  # SW
            (col - 1, row),      # NW
        ]


def test_hex(col: int, row: int) -> bool:
    """Test neighbors for a specific hex."""
    expected = get_neighbors_even_q(col, row)
    expected = [(x, y) for x, y in expected if x >= 0 and y >= 0]  # Filter valid coords

    print(f"\nTesting hex ({col}, {row}) [{'even' if col % 2 == 0 else 'odd'} column]:")

    # Find all hexes at distance 1
    found = []
    for x in range(0, 10):
        for y in range(0, 12):
            if calculate_hex_distance(col, row, x, y) == 1:
                found.append((x, y))

    found.sort()
    expected.sort()

    if found == expected:
        print(f"  [PASS] Found correct neighbors: {found}")
        return True
    else:
        print(f"  [FAIL]")
        print(f"    Expected: {expected}")
        print(f"    Found:    {found}")
        print(f"    Missing:  {set(expected) - set(found)}")
        print(f"    Extra:    {set(found) - set(expected)}")
        return False


def test_distance_symmetry():
    """Test that distance is symmetric."""
    print("\nTesting distance symmetry:")
    test_cases = [
        ((1, 8), (0, 7)),
        ((1, 8), (2, 8)),
        ((0, 5), (1, 5)),
        ((2, 3), (3, 4)),
    ]

    all_passed = True
    for (x1, y1), (x2, y2) in test_cases:
        d1 = calculate_hex_distance(x1, y1, x2, y2)
        d2 = calculate_hex_distance(x2, y2, x1, y1)
        if d1 == d2:
            print(f"  [PASS] ({x1},{y1}) <-> ({x2},{y2}): {d1} = {d2}")
        else:
            print(f"  [FAIL] ({x1},{y1}) <-> ({x2},{y2}): {d1} != {d2}")
            all_passed = False

    return all_passed


def test_zero_distance():
    """Test that distance to self is 0."""
    print("\nTesting zero distance to self:")
    test_coords = [(0, 0), (1, 8), (5, 5), (9, 11)]

    all_passed = True
    for x, y in test_coords:
        d = calculate_hex_distance(x, y, x, y)
        if d == 0:
            print(f"  [PASS] ({x},{y}) to self: {d}")
        else:
            print(f"  [FAIL] ({x},{y}) to self: {d} (expected 0)")
            all_passed = False

    return all_passed


if __name__ == "__main__":
    print("=" * 60)
    print("Extended Hex Distance Tests (even-q vertical)")
    print("=" * 60)

    all_passed = True

    # Test different hex positions
    all_passed &= test_hex(1, 8)  # Odd column (original bug case)
    all_passed &= test_hex(0, 7)  # Even column
    all_passed &= test_hex(2, 8)  # Even column
    all_passed &= test_hex(3, 5)  # Odd column

    # Test symmetry
    all_passed &= test_distance_symmetry()

    # Test zero distance
    all_passed &= test_zero_distance()

    print("\n" + "=" * 60)
    if all_passed:
        print("[PASS] All extended tests passed!")
    else:
        print("[FAIL] Some tests failed!")
    print("=" * 60)

    exit(0 if all_passed else 1)
