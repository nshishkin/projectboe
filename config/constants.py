"""
Game constants and configuration values.
All screen dimensions, color, grid sizes, and default stats
"""

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Hex settings
STRATEGIC_HEX_SIZE = 40  # Radius for strategic map hexagons
TACTICAL_HEX_SIZE = 30   # Radius for tactical battlefield hexagons

# Colors (R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

# UI Colors
BG_COLOR = BLACK
TEXT_COLOR = WHITE
BORDER_COLOR = WHITE

# Button Settings
BUTTON_COLOR = (70, 70, 70)
BUTTON_HOVER_COLOR = (100, 100, 100)
BUTTON_TEXT_COLOR = WHITE
BUTTON_HEIGHT = 40
BUTTON_BORDER_WIDTH = 2

# Strategic map settings (Phase 2, but define now)
MAP_ROWS = 6
MAP_COLS = 12


# Tactical map settings (Phase 3, but define now)
BATTLEFIELD_ROWS = 10
BATTLEFIELD_COLS = 10
DEPLOYMENT_COLUMNS = 3  # Number of columns for unit deployment on each side


# Strategic map offsets
MAP_OFFSET_X = 50
MAP_OFFSET_Y = 50

# Tactical battlefield offsets
BATTLEFIELD_OFFSET_X = 50
BATTLEFIELD_OFFSET_Y = 50

UNIT_TYPES = {
    'infantry': {
        'name': 'Infantry',
        'max_hp': 50,
        'melee_attack': 50,
        'ranged_attack': 0,
        'melee_defence': 5,
        'ranged_defence': 0,
        'stamina': 90,
        'initiative': 100,
        'morale': 40,
        'base_damage': 20,
        'movement_points': 2,
        'color': (100, 100, 255),  # Синий для игрока
        'enemy_color': (255, 100, 100)  # Красный для врагов
    },
    'cavalry': {
        'name': 'Cavalry',
        'max_hp': 40,
        'melee_attack': 60,
        'ranged_attack': 0,
        'melee_defence': 3,
        'ranged_defence': 0,
        'stamina': 100,
        'initiative': 120,  # Быстрее пехоты
        'morale': 50,
        'base_damage': 20,
        'movement_points': 2,
        'color': (100, 255, 100),  # Зелёный
        'enemy_color': (255, 150, 100)
    },
    'ranged': {
        'name': 'Ranged',
        'max_hp': 30,
        'melee_attack': 25,
        'ranged_attack': 50,
        'melee_defence': 0,
        'ranged_defence': 5,
        'stamina': 80,
        'initiative': 110,
        'morale': 30,
        'base_damage': 20,
        'movement_points': 2,
        'color': (255, 255, 100),  # Жёлтый
        'enemy_color': (255, 100, 255)
    },
    'spearman': {
        'name': 'Spearman',
        'max_hp': 55,
        'melee_attack': 45,
        'ranged_attack': 0,
        'melee_defence': 8,  # Больше защиты
        'ranged_defence': 3,
        'stamina': 85,
        'initiative': 95,
        'morale': 45,
        'base_damage': 20,
        'movement_points': 2,
        'color': (150, 150, 255),
        'enemy_color': (255, 150, 150)
    },
    'archer': {
        'name': 'Archer',
        'max_hp': 35,
        'melee_attack': 20,
        'ranged_attack': 55,
        'melee_defence': 0,
        'ranged_defence': 8,
        'stamina': 75,
        'initiative': 115,
        'morale': 35,
        'base_damage': 20,
        'movement_points': 2,
        'color': (200, 200, 100),
        'enemy_color': (200, 100, 200)
    }
}
