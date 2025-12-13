#main.py
import pygame
import os
import random
import sys
from settings import *
import map
import level_controller # imports the difficulties setting
from movement import Controller # import player control
movement = Controller()

# HELPER FUNCTION
# load asset dari folder asset
def load_asset(name):
    path = os.path.join(ASSET_DIR, name)
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    except Exception:
        return None

# tile polos, sebagai tile default jika gambar gagal load, debug map
def solid_surface(color):
    s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    s.fill(color)
    return s

# Initialize game and window display
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("EXORCIZE")
clock = pygame.time.Clock()

# The assets
player_img = load_asset("Avatar_Front.png")
ghost_img = load_asset("Ghost_Left.png")

floor_regular = load_asset("Floor_Regular.png")
floor_sealed  = load_asset("Floor_Sealed.png")

wall_regular  = load_asset("Wall_Regular.png")
wall_sealed   = load_asset("Wall_Sealed.png")

manuscript_img = load_asset("Manuscript.png")

# Fallback: jika asset hilang/korup
if floor_regular is None:
    floor_regular = solid_surface((180, 160, 120))
if floor_sealed is None:
    floor_sealed = solid_surface((140, 120, 200))
if wall_regular is None:
    wall_regular = solid_surface((80, 80, 80))
if wall_sealed is None:
    wall_sealed = solid_surface((100, 60, 60))
if manuscript_img is None:
    manuscript_img = solid_surface((255, 230, 140))
if player_img is None:
    player_img = solid_surface((60, 140, 220))
if ghost_img is None:
    ghost_img = solid_surface((200, 60, 140))

# DRAW THE GAME TO THE WINDOW
# Additional variable in the parameter 'curr_diff'
def draw(grid, player_pos, ghost_pos, manuscripts_left, curr_diff):
    # the loop will draw seluruh grid pada map
    for r in range(GRID):
        for c in range(GRID):
            x = c * TILE_SIZE
            y = r * TILE_SIZE
            t = grid[r][c]
            # setiap tile memiliki asset gambar yang berbeda dan akan ditempel ke window dengan screen.blit()
            if t == FLOOR:
                screen.blit(floor_regular, (x, y))
            elif t == WALL:
                screen.blit(wall_regular, (x, y))
            elif t == WALL_SEALED:                  # UPDATE: add sealed wall
                screen.blit(wall_sealed, (x, y))
            elif t == SEALED_FLOOR:
                screen.blit(floor_sealed, (x, y))
            elif t == MANUSCRIPT:
                screen.blit(floor_regular, (x, y))
                screen.blit(manuscript_img, (x, y))
            elif t == MANUSCRIPT_SEALED:            # NEW MANUSCRIPT_SEALED
                screen.blit(floor_sealed, (x, y))
                screen.blit(manuscript_img, (x, y))
    # player & ghost
    pr, pc = player_pos
    gr, gc = ghost_pos
    screen.blit(player_img, (pc * TILE_SIZE, pr * TILE_SIZE))
    screen.blit(ghost_img,  (gc * TILE_SIZE, gr * TILE_SIZE))

    # Head Display
    font = pygame.font.SysFont(None, 20)
    txt = font.render(f"Difficulty: {curr_diff} Manuscripts left: {manuscripts_left}   (Press R to regen)", True, (240,240,240))
    screen.blit(txt, (4, 4))


current_difficulty = "EASY" # the default difficulty level

# MAIN
grid, player_pos, ghost_pos = map.generate_map(current_difficulty)
# menghitung sisa dari manuscript yang belum diambil
manuscripts_left = sum(1 for r in range(GRID) for c in range(GRID) if grid[r][c] in [MANUSCRIPT, MANUSCRIPT_SEALED])

# berjalannya game
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # ---------------- MOVEMENT INPUT ----------------
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            movement.handle_mouse_click(
                pygame.mouse.get_pos(),
                grid,
                player_pos
            )

        if event.type == pygame.KEYDOWN:
            result = level_controller.game_difficulties(event, current_difficulty)
            
            if event.key == pygame.K_RETURN: # Confirm movement with 'Enter' key
                movement.confirm_move()

            if event.key == pygame.K_z: # Reset dot placement with 'z' key
                movement.reset_path()
        
            if not result['running']:
                running = False
                
            if result['regen']:
                movement.path.clear()
                movement.is_moving = False                
                current_difficulty = result['difficulty']
                grid, player_pos, ghost_pos = map.generate_map(current_difficulty)
                # UPDATE: there was a bug of which was just counting manuscript in Regular Floor
                manuscripts_left = sum(1 for r in range(GRID) for c in range(GRID) if grid[r][c] in [MANUSCRIPT, MANUSCRIPT_SEALED])

    player_pos = movement.update(player_pos)

    screen.fill((0,0,0))
    draw(grid, player_pos, ghost_pos, manuscripts_left, current_difficulty) # Additional 'current_difficulty' in the function's parameter
    movement.draw_path(screen) 
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()