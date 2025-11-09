"""
Game settings and constants for Brothers of Eador.
This file contains configurable game parameters like screen resolution, game speed, etc.
"""

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FULLSCREEN = False

# Game settings
FPS = 60
GAME_SPEED = 1.0

# Colors (RGB tuples)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64)
LIGHT_GRAY = (192, 192, 192)
BROWN = (139, 69, 19)
DARK_BROWN = (101, 67, 33)
LIGHT_BROWN = (210, 180, 140)
MIDNIGHT_BLUE = (25, 25, 112)

# Tactical grid settings
TACTICAL_GRID_WIDTH = 20  # 20 hexes horizontally
TACTICAL_GRID_HEIGHT = 10  # 10 hexes vertically
HEX_SIZE = 40  # radius of each hexagon in pixels

# Strategic map settings
STRATEGIC_MAP_WIDTH = 8
STRATEGIC_MAP_HEIGHT = 8
PROVINCE_SIZE = 32 # pixels per province

# UI settings
UI_FONT_SIZE = 16
UI_MARGIN = 10
UI_PADDING = 5

# Combat settings
INITIATIVE_BASE = 100