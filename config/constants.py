"""
Global constants for Battle of Empires.
This file contains immutable values used throughout the game (colors, dimensions, etc.)
"""

# Terrain types for strategic map
TERRAIN_PLAINS = "plains"
TERRAIN_WOODS = "woods"
TERRAIN_HILLS = "hills"
TERRAIN_SWAMPS = "swamps"

# Terrain movement costs
TERRAIN_MOVEMENT_COST = {
    TERRAIN_PLAINS: 1,
    TERRAIN_WOODS: 2,
    TERRAIN_HILLS: 2,
    TERRAIN_SWAMPS: 3
}

# Terrain combat bonuses
TERRAIN_COMBAT_BONUS = {
    TERRAIN_PLAINS: 0,      # Balanced terrain
    TERRAIN_WOODS: 1,       # Defensive bonus
    TERRAIN_HILLS: 1,       # Advantage for ranged units
    TERRAIN_SWAMPS: -1      # Disadvantage for most units
}

# Unit types
UNIT_TYPE_INFANTRY = "infantry"
UNIT_TYPE_CAVALRY = "cavalry"
UNIT_TYPE_RANGED = "ranged"
UNIT_TYPE_SIEGE = "siege"
UNIT_TYPE_SUPPORT = "support"

# Unit stat names
STAT_HITPOINTS = "hitpoints"
STAT_MELEE_ATTACK = "melee_attack"
STAT_RANGED_ATTACK = "ranged_attack"
STAT_MELEE_DEFENSE = "melee_defense"
STAT_RANGED_DEFENSE = "ranged_defense"
STAT_STAMINA = "stamina"
STAT_INITIATIVE = "initiative"
STAT_MORALE = "morale"

# Default unit stats for prototyping
DEFAULT_UNIT_STATS = {
    STAT_HITPOINTS: 50,
    STAT_MELEE_ATTACK: 50,
    STAT_RANGED_ATTACK: 40,
    STAT_MELEE_DEFENSE: 0,
    STAT_RANGED_DEFENSE: 0,
    STAT_STAMINA: 90,
    STAT_INITIATIVE: 100,
    STAT_MORALE: 40
}

# Game states
STATE_MENU = "menu"
STATE_STRATEGIC = "strategic"
STATE_TACTICAL = "tactical"

# Province states
PROVINCE_STATE_NEUTRAL = "neutral"
PROVINCE_STATE_FRIENDLY = "friendly"
PROVINCE_STATE_HOSTILE = "hostile"
PROVINCE_STATE_CONTROLLED = "controlled"

# Race types for provinces
RACE_HUMAN = "human"
RACE_ELF = "elf"
RACE_DWARF = "dwarf"
RACE_ORC = "orc"
RACE_GOBLIN = "goblin"

# Direction constants for grid movement
DIRECTION_NORTH = (0, -1)
DIRECTION_EAST = (1, 0)
DIRECTION_SOUTH = (0, 1)
DIRECTION_WEST = (-1, 0)
DIRECTIONS = [DIRECTION_NORTH, DIRECTION_EAST, DIRECTION_SOUTH, DIRECTION_WEST]

# UI Constants
UI_BUTTON_WIDTH = 120
UI_BUTTON_HEIGHT = 30
UI_PANEL_MARGIN = 10
UI_STATUS_BAR_HEIGHT = 25