# movement.py
import pygame
from settings import *

MOVE_DELAY = 150  # ms

class Controller:
    def __init__(self):
        self.path = []
        self.is_moving = False
        self.move_index = 0
        self.last_move_time = 0

    # ---------- RULES ----------
    def is_adjacent(self, a, b):
        ar, ac = a
        br, bc = b
        return max(abs(ar - br), abs(ac - bc)) == 1  # diagonal allowed

    def is_walkable(self, grid, r, c):
        return grid[r][c] in [
            FLOOR, SEALED_FLOOR,
            MANUSCRIPT, MANUSCRIPT_SEALED
        ]

    # ---------- INPUT ----------
    def handle_mouse_click(self, pos, grid, player_pos):
        if self.is_moving:
            return

        mx, my = pos
        r = my // TILE_SIZE
        c = mx // TILE_SIZE

        if not (0 <= r < GRID and 0 <= c < GRID):
            return

        if not self.is_walkable(grid, r, c):
            return

        if len(self.path) == 0:
            if self.is_adjacent(player_pos, (r, c)):
                self.path.append((r, c))
        else:
            if len(self.path) < MAX_STEPS and self.is_adjacent(self.path[-1], (r, c)):
                self.path.append((r, c))

    def confirm_move(self):
        if self.path:
            self.is_moving = True
            self.move_index = 0
            self.last_move_time = pygame.time.get_ticks()

    # ---------- UPDATE ----------
    def update(self, player_pos):
        if not self.is_moving:
            return player_pos

        now = pygame.time.get_ticks()
        if now - self.last_move_time > MOVE_DELAY:
            player_pos = self.path[self.move_index]
            self.move_index += 1
            self.last_move_time = now

            if self.move_index >= len(self.path):
                self.path.clear()
                self.is_moving = False

        return player_pos

    # ---------- RESET ----------
    def reset_path(self):
        if not self.is_moving:
            self.path.clear()

    # ---------- DRAW ----------
    def draw_path(self, screen, offset_x=0, offset_y=0):
        for r, c in self.path:
            pygame.draw.circle(
                screen,
                (228, 245, 245),
                (
                    c * TILE_SIZE + TILE_SIZE // 2 + offset_x,
                    r * TILE_SIZE + TILE_SIZE // 2 + offset_y
                ),
                5 # radius
            )
