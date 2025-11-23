"""
Enemy army data for testing.
In final version, enemy armies will be generated dynamically based on encounters.
"""

# Test enemy army (used for debug combat button)
TEST_ENEMY_ARMY = ['infantry', 'cavalry', 'ranged']

# Phase 4+: Different enemy army presets for testing
ENEMY_PRESETS = {
    'weak_bandits': ['infantry', 'infantry'],
    'strong_bandits': ['infantry', 'infantry', 'cavalry', 'ranged'],
    'orc_raiders': ['infantry', 'cavalry', 'cavalry'],
    'forest_monsters': ['cavalry', 'ranged', 'ranged'],
    'undead_horde': ['infantry', 'infantry', 'infantry', 'ranged']
}
