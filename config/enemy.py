"""
Enemy army data for testing.
In final version, enemy armies will be generated dynamically based on encounters.
"""

# Phase 4+: Different enemy army presets for testing
ENEMY_PRESETS = {
    'weak_bandits': ['infantry', 'infantry'],
    'strong_bandits': ['infantry', 'infantry', 'cavalry', 'ranged'],
    'orc_raiders': ['infantry', 'cavalry', 'cavalry'],
    'forest_monsters': ['cavalry', 'ranged', 'ranged'],
    'undead_horde': ['infantry', 'infantry', 'infantry', 'ranged'],
    'debug_player_win': ['Debug_weak'],
    'debug_player_loss': ['Debug_strong'],
    'debug_movement': ['Debug_movement'],
    'default': ['infantry', 'infantry', 'cavalry', 'ranged']
}

# Test enemy army (used for debug combat button)
TEST_ENEMY_ARMY = ENEMY_PRESETS['debug_player_loss']
