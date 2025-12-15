#settings.py
import os

# GAME CONFIGURATIONS
GRID = 8
TILE_SIZE = 64
WIDTH = GRID * TILE_SIZE
HEIGHT = GRID * TILE_SIZE
TOTAL_TILES = GRID * GRID
ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")  # relative assets/
TOP_BAR_HEIGHT = 40
SIDEBAR_WIDTH = 260
GAME_OFFSET_X = 0
GAME_OFFSET_Y = TOP_BAR_HEIGHT
MAX_STEPS = 5
AVATAR_MOVE_DELAY = 650 # in ms

# Konstanta tile
FLOOR = 0
WALL = 1
SEALED_FLOOR = 2
MANUSCRIPT = 3
WALL_SEALED = 4
MANUSCRIPT_SEALED= 5 # NEW constant biar manuskrip dapat di SEALED_FLOOR

# Konstanta state
PLAYER_PLANNING = 0
PLAYER_MOVING   = 1
GHOST_MOVING    = 2

turn_state = PLAYER_PLANNING

# CONSTRAINT FOR DIFFICULTIES OF THE MAP LAYOUT
DIFFICULTY_SETTINGS = {
    "EASY": {
        "wall_ratio": (0.15, 0.20),     # Range tembok sedikit
        "sealed_ratio": 0.10,           # Terdapat banyak tempat aman
        "wall_chance": 0.5,             # 50% Wall Biasa
        "spawn_dist": max(4, GRID // 2) # Hantu spawn jauh
    },
    "MEDIUM": {
        "wall_ratio": (0.25, 0.30),
        "sealed_ratio": 0.06,
        "wall_chance": 0.7,
        "spawn_dist": max(3, GRID // 3)
    },
    "HARD": {
        "wall_ratio": (0.35, 0.40),
        "sealed_ratio": 0.03,
        "wall_chance": 0.9,             # 90% Wall Biasa
        "spawn_dist": max(3, GRID // 3)
    }
}