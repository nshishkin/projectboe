"""
Test to verify turn_order index correction works correctly.
"""

class MockUnit:
    def __init__(self, name):
        self.name = name
        self.alive = True

    def is_alive(self):
        return self.alive

    def __repr__(self):
        return self.name

# Test 1: Kill unit BEFORE current
print("=" * 60)
print("Test 1: Kill unit BEFORE current index")
print("=" * 60)

turn_order = [MockUnit("Unit1"), MockUnit("Unit2"), MockUnit("Unit3"), MockUnit("Unit4"), MockUnit("Unit5")]
current_unit_index = 3  # Unit4 is current

print(f"Initial state:")
print(f"  turn_order: {[u.name for u in turn_order]}")
print(f"  current_unit_index: {current_unit_index} -> {turn_order[current_unit_index].name}")

# Unit4 kills Unit2 (index 1)
print(f"\nUnit4 kills Unit2 (index 1 < current index 3):")
killed_unit = turn_order[1]
killed_unit.alive = False

# Find dead unit index
dead_unit_index = None
for i, u in enumerate(turn_order):
    if not u.is_alive():
        dead_unit_index = i
        break

print(f"  Dead unit found at index: {dead_unit_index}")

# Remove dead units
turn_order = [u for u in turn_order if u.is_alive()]

# Adjust index if needed
if dead_unit_index is not None and dead_unit_index < current_unit_index:
    current_unit_index -= 1
    print(f"  Index adjusted: {current_unit_index + 1} -> {current_unit_index}")

print(f"\nAfter removal:")
print(f"  turn_order: {[u.name for u in turn_order]}")
print(f"  current_unit_index: {current_unit_index} -> {turn_order[current_unit_index].name}")
print(f"  Result: {'OK - Still Unit4' if turn_order[current_unit_index].name == 'Unit4' else 'FAIL'}")

# Test 2: Kill unit AFTER current
print("\n" + "=" * 60)
print("Test 2: Kill unit AFTER current index")
print("=" * 60)

turn_order = [MockUnit("Unit1"), MockUnit("Unit2"), MockUnit("Unit3"), MockUnit("Unit4"), MockUnit("Unit5")]
current_unit_index = 1  # Unit2 is current

print(f"Initial state:")
print(f"  turn_order: {[u.name for u in turn_order]}")
print(f"  current_unit_index: {current_unit_index} -> {turn_order[current_unit_index].name}")

# Unit2 kills Unit4 (index 3)
print(f"\nUnit2 kills Unit4 (index 3 > current index 1):")
killed_unit = turn_order[3]
killed_unit.alive = False

# Find dead unit index
dead_unit_index = None
for i, u in enumerate(turn_order):
    if not u.is_alive():
        dead_unit_index = i
        break

print(f"  Dead unit found at index: {dead_unit_index}")

# Remove dead units
turn_order = [u for u in turn_order if u.is_alive()]

# Adjust index if needed
if dead_unit_index is not None and dead_unit_index < current_unit_index:
    current_unit_index -= 1
    print(f"  Index adjusted")
else:
    print(f"  Index NOT adjusted (dead unit was after current)")

print(f"\nAfter removal:")
print(f"  turn_order: {[u.name for u in turn_order]}")
print(f"  current_unit_index: {current_unit_index} -> {turn_order[current_unit_index].name}")
print(f"  Result: {'OK - Still Unit2' if turn_order[current_unit_index].name == 'Unit2' else 'FAIL'}")

print("\n" + "=" * 60)
print("All tests completed!")
print("=" * 60)
