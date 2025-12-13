import os

# GAME CONFIGURATIONS
TILE_SIZE = 64
GRID = 6 # updated the grid dari 7 ke 6
WIDTH = GRID * TILE_SIZE
HEIGHT = GRID * TILE_SIZE
ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")  # relative assets/

# Konstanta tile
FLOOR = 0
WALL = 1
SEALED_FLOOR = 2
MANUSCRIPT = 3
WALL_SEALED = 4
MANUSCRIPT_SEALED= 5 # NEW constant biar manuskrip dapat di SEALED_FLOOR

# --- COLORS (Fallback for debug) ---
COLOR_FLOOR = (180, 160, 120)
COLOR_WALL = (80, 80, 80)
COLOR_SEALED_FLOOR = (140, 120, 200)
COLOR_SEALED_WALL = (100, 60, 60)
COLOR_MANUSCRIPT = (255, 230, 140)
COLOR_PLAYER = (60, 140, 220)
COLOR_GHOST = (200, 60, 140)