#settings.py
import os

# GAME CONFIGURATIONS
TILE_SIZE = 64
GRID = 8 # updated the grid dari 7 ke 6
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

# CONSTRAINT FOR DIFFICULTIES OF THE MAP LAYOUT
DIFFICULTY_SETTINGS = {
    "EASY": {
        "wall_range": (6, 8),       # Range tembok sedikit
        "sealed_floors": 4,         # Terdapat banyak tempat aman
        "wall_chance": 0.5,         # 50% Wall Biasa
        "spawn_dist": 4             # Hantu spawn jauh
    },
    "MEDIUM": {
        "wall_range": (10, 14),
        "sealed_floors": 3,
        "wall_chance": 0.7,         # 70% Wall Biasa
        "spawn_dist": 3
    },
    "HARD": {
        "wall_range": (12, 16),
        "sealed_floors": 1,         # hanya ada 1 tempat aman
        "wall_chance": 0.9,         # 90% Wall Biasa
        "spawn_dist": 3
    }
}