# movement.py
import pygame
from settings import *

class Controller:
    def __init__(self):
        self.path = []
        self.is_moving = False
        self.move_index = 0
        self.last_move_time = 0
        self.direction = "DOWN"
        self.animation = 0
        self.pixel_x = None
        self.pixel_y = None
        self.target_x = None
        self.target_y = None
        self.move_start_time = 0
        self.move_duration = AVATAR_MOVE_DELAY
        self.was_moving = False
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
        self.was_moving = self.is_moving

        if not self.is_moving:
            return player_pos

        now = pygame.time.get_ticks()

        if self.pixel_x is None:
            r, c = player_pos
            self.pixel_x = c * TILE_SIZE
            self.pixel_y = r * TILE_SIZE

        if self.target_x is None:
            nr, nc = self.path[self.move_index]
            cr, cc = player_pos

            dr = nr - cr
            dc = nc - cc

            if dr == -1 and dc == 0:
                self.direction = "UP"
            elif dr == 1 and dc == 0:
                self.direction = "DOWN"
            elif dr == 0 and dc == -1:
                self.direction = "LEFT"
            elif dr == 0 and dc == 1:
                self.direction = "RIGHT"
            elif dr == -1 and dc == -1:
                self.direction = "UP_LEFT"
            elif dr == -1 and dc == 1:
                self.direction = "UP_RIGHT"
            elif dr == 1 and dc == -1:
                self.direction = "DOWN_LEFT"
            elif dr == 1 and dc == 1:
                self.direction = "DOWN_RIGHT"

            self.start_x = self.pixel_x
            self.start_y = self.pixel_y
            self.target_x = nc * TILE_SIZE
            self.target_y = nr * TILE_SIZE
            self.move_start_time = now

        t = min((now - self.move_start_time) / self.move_duration, 1)

        self.pixel_x = self.start_x + (self.target_x - self.start_x) * t
        self.pixel_y = self.start_y + (self.target_y - self.start_y) * t

        self.animation += 0.15

        if t >= 1:
            player_pos = self.path[self.move_index]
            self.move_index += 1
            self.target_x = None
            self.target_y = None

            if self.move_index >= len(self.path):
                self.path.clear()
                self.is_moving = False
                self.animation = 0
                self.direction = "DOWN"

        return player_pos


    # ---------- RESET ----------
    def reset_path(self):
        if not self.is_moving:
            self.path.clear()

    # ---------- DRAW ----------
    def draw_path(self, screen, offset_x=0, offset_y=0):    
        if self.is_moving: # Kalau jalan titiknya hilang
            return
        
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