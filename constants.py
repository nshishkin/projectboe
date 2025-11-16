"""
Game constants and configuration values.
All screen dimensions, color, grid sizes, and defaul stats
"""

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Hex settings (for strategic and tactical maps)
HEX_SIZE = 40  # Radius of hexagon (distance from center to corner)

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
MAP_ROWS = 12
MAP_COLS = 8
 

# Tactical map settings (Phase 3, but define now)
BATTLEFIELD_ROWS = 10
BATTLEFIELD_COLS = 16
 

# Grid offset for centering
MAP_OFFSET_X = 50
MAP_OFFSET_Y = 50