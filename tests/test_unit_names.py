#!/usr/bin/env python3
"""
Test script to verify that unit naming works correctly.
"""
import sys
import os
# Add current directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_unit_names():
    print("Testing unit naming functionality...")
    
    # Import the CombatUnit class
    from tactical.combat_unit import CombatUnit
    
    # Test the new naming convention
    player_unit = CombatUnit('infantry', 0, 0, True, 'Party0')
    print('Player unit display name:', player_unit.get_display_name())
    
    enemy_unit = CombatUnit('cavalry', 1, 1, False, 'Enemy0')
    print('Enemy unit display name:', enemy_unit.get_display_name())
    
    # Test without custom names (should still work)
    player_unit2 = CombatUnit('ranged', 2, 2, True)  # No custom name
    print('Player unit2 display name:', player_unit2.get_display_name())
    
    # Test the battlefield placement with proper naming
    from tactical.battlefield import Battlefield
    
    # Create a test battlefield
    battlefield = Battlefield('plains')
    
    # Test placing units - they should get proper names Party0, Party1, etc. and Enemy0, Enemy1, etc.
    battlefield.place_units(['infantry', 'ranged'], ['cavalry', 'infantry'])
    
    print("\nPlayer units after placement:")
    for i, unit in enumerate(battlefield.player_units):
        print(f" Player unit {i}: {unit.get_display_name()}")
    
    print("\nEnemy units after placement:")
    for i, unit in enumerate(battlefield.enemy_units):
        print(f"  Enemy unit {i}: {unit.get_display_name()}")
    
    print("\nAll tests completed successfully!")

if __name__ == "__main__":
    test_unit_names()