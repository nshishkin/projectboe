"""
Simple test for save/load system.
"""
from strategic import save_system
from strategic.hero import Hero
from strategic.province import Province

def test_save_load():
    """Test basic save and load functionality."""
    print("=" * 60)
    print("Testing Save System")
    print("=" * 60)

    # Create test data
    hero = Hero(3, 5)
    hero.army = ['infantry', 'archer', 'cavalry']
    hero.current_movement = 2

    province1 = Province(0, 0, 'plains')
    province2 = Province(1, 0, 'woods')
    province1.owner = 'player'

    # Create test state
    state_dict = {
        'version': '1.0',
        'turn': 5,
        'hero': hero.to_dict(),
        'map': [[province1.to_dict(), province2.to_dict()]]
    }

    print("\n1. Original State:")
    print(f"   Turn: {state_dict['turn']}")
    print(f"   Hero: ({state_dict['hero']['x']}, {state_dict['hero']['y']})")
    print(f"   Army: {state_dict['hero']['army']}")

    # Save
    print("\n2. Saving to quicksave...")
    success = save_system.save_game(state_dict, 'quicksave')
    if success:
        print("   [OK] Save successful")
    else:
        print("   [FAIL] Save failed")
        return False

    # Check if save exists
    print("\n3. Checking if save exists...")
    exists = save_system.save_exists('quicksave')
    if exists:
        print("   [OK] Save file found")
    else:
        print("   [FAIL] Save file not found")
        return False

    # Load
    print("\n4. Loading from quicksave...")
    loaded_state = save_system.load_game('quicksave')
    if loaded_state:
        print("   [OK] Load successful")
    else:
        print("   [FAIL] Load failed")
        return False

    # Verify data
    print("\n5. Verifying loaded data...")
    hero_data = loaded_state['hero']

    checks = [
        (loaded_state['turn'] == 5, f"Turn: {loaded_state['turn']} == 5"),
        (hero_data['x'] == 3, f"Hero X: {hero_data['x']} == 3"),
        (hero_data['y'] == 5, f"Hero Y: {hero_data['y']} == 5"),
        (hero_data['army'] == ['infantry', 'archer', 'cavalry'], f"Army: {hero_data['army']}"),
        (len(loaded_state['map'][0]) == 2, f"Map size: {len(loaded_state['map'][0])} == 2")
    ]

    all_passed = True
    for passed, msg in checks:
        status = "[OK]" if passed else "[FAIL]"
        print(f"   {status} {msg}")
        if not passed:
            all_passed = False

    # Test different slots
    print("\n6. Testing different save slots...")
    save_system.save_game(state_dict, 'autosave_combat')
    save_system.save_game(state_dict, 'autosave_turn')

    slots_exist = [
        save_system.save_exists('quicksave'),
        save_system.save_exists('autosave_combat'),
        save_system.save_exists('autosave_turn')
    ]

    if all(slots_exist):
        print("   [OK] All save slots created")
    else:
        print(f"   [FAIL] Some slots missing: {slots_exist}")
        all_passed = False

    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("[PASS] All tests passed!")
    else:
        print("[FAIL] Some tests failed")
    print("=" * 60)

    return all_passed


if __name__ == "__main__":
    success = test_save_load()
    exit(0 if success else 1)
