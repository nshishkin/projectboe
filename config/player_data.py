"""
Player hero data: army, inventory, stats.
Shared between strategic and tactical layers.
This will be loaded from/saved to save files in Phase 4+.
"""
HERO_PRESETS = {
    'debug_player_loss': ['Debug_weak'],
    'debug_player_win': ['Debug_strong'],
    'debug_movement': ['Debug_movement'],
    'default': ['infantry', 'infantry', 'cavalry', 'ranged']
}
# Hero's current army composition
HERO_ARMY = HERO_PRESETS['debug_player_loss']

# Phase 4+: Will include inventory, stats, skills, etc.
HERO_INVENTORY = []
HERO_GOLD = 100
