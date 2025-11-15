"""
Game constants and configuration values.
All screen dimensions, color, grid sizes, and defaul stats
"""

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors (R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

# UI Colors
BG_COLOR = BLACK
TEXT_COLOR = WHITE
BORDER_COLOR = WHITE

# Strategic map settings (Phase 2, but define now)
MAP_ROWS = 8
MAP_COLS = 8
PROVINCE_SIZE = 80  # pixels per province square

# Tactical map settings (Phase 3, but define now)
BATTLEFIELD_ROWS = 10
BATTLEFIELD_COLS = 16
TILE_SIZE = 40  # pixels per battlefield tile

# Grid offset for centering
MAP_OFFSET_X = 50
MAP_OFFSET_Y = 50