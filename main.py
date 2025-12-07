import pygame
import os
import random
import sys

# GAME CONFIGURATIONS
TILE_SIZE = 64
GRID = 7
WIDTH = GRID * TILE_SIZE
HEIGHT = GRID * TILE_SIZE
ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")  # relative assets/
WALL_SEALED = 4


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

# Konstanta tile
FLOOR = 0
WALL = 1
SEALED_FLOOR = 2
MANUSCRIPT = 3

# MAP GENERATOR
def generate_map():
    # insisiasi map structure dasar
    grid = [[FLOOR for _ in range(GRID)] for _ in range(GRID)]

    # random wall placement
    total_walls = random.randint(8, 14)
    placed = 0
    attempts = 0
    while placed < total_walls and attempts < 200:
        attempts += 1
        r = random.randint(0, GRID - 1)
        c = random.randint(0, GRID - 1)
        # menghindari sealed atau manuskrip terlalu awal
        if grid[r][c] == FLOOR:
            grid[r][c] = WALL
            placed += 1

    # NOTES: diubah, tidak ada minimal untuk sealed floor
    # menaruh 3 sealed floor secara random
    sealed_positions = []
    attempts = 0
    while len(sealed_positions) < 3 and attempts < 200:
        attempts += 1
        r = random.randint(0, GRID - 1)
        c = random.randint(0, GRID - 1)
        if grid[r][c] == FLOOR:
            grid[r][c] = SEALED_FLOOR
            sealed_positions.append((r, c))

    # menaruh 3 mansuksrip secara random
    manuscript_positions = []
    attempts = 0
    while len(manuscript_positions) < 3 and attempts < 500:
        attempts += 1
        r = random.randint(0, GRID - 1)
        c = random.randint(0, GRID - 1)
        if grid[r][c] == FLOOR:
            grid[r][c] = MANUSCRIPT
            manuscript_positions.append((r, c))

    # menempatkan player di floor
    player_pos = None
    attempts = 0
    while player_pos is None and attempts < 500:
        attempts += 1
        r = random.randint(0, GRID - 1)
        c = random.randint(0, GRID - 1)
        if grid[r][c] == FLOOR:
            player_pos = (r, c)

    # menempatkan player di floor (notes: tidak di player)
    ghost_pos = None
    attempts = 0
    while ghost_pos is None and attempts < 500:
        attempts += 1
        r = random.randint(0, GRID - 1)
        c = random.randint(0, GRID - 1)
        if grid[r][c] == FLOOR and (r, c) != player_pos:
            ghost_pos = (r, c)

    # fallback safety
    if player_pos is None:
        player_pos = (GRID//2, GRID//2)
    if ghost_pos is None:
        ghost_pos = (0, 0) if grid[0][0] == FLOOR else (GRID-1, GRID-1)

    # ensure tidak ada plater ataupun ghost yang spawn di wall, sealed, dan manuskrip
    pr, pc = player_pos
    if grid[pr][pc] != FLOOR:
        # cari floor tile
        for r in range(GRID):
            for c in range(GRID):
                if grid[r][c] == FLOOR:
                    player_pos = (r, c)
                    raise_stop = True
                    break
            else:
                continue
            break

    gr, gc = ghost_pos
    if grid[gr][gc] != FLOOR:
        for r in range(GRID):
            for c in range(GRID):
                if grid[r][c] == FLOOR and (r, c) != player_pos:
                    ghost_pos = (r, c)
                    raise_stop = True
                    break
            else:
                continue
            break

    return grid, player_pos, ghost_pos

# DRAW THE GAME TO THE WINDOW
def draw(grid, player_pos, ghost_pos, manuscripts_left):
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
            elif t == SEALED_FLOOR:
                screen.blit(floor_sealed, (x, y))
            elif t == MANUSCRIPT:
                screen.blit(floor_regular, (x, y))
                screen.blit(manuscript_img, (x, y))

    # player & ghost
    pr, pc = player_pos
    gr, gc = ghost_pos
    screen.blit(player_img, (pc * TILE_SIZE, pr * TILE_SIZE))
    screen.blit(ghost_img,  (gc * TILE_SIZE, gr * TILE_SIZE))

    # Head Display
    font = pygame.font.SysFont(None, 20)
    txt = font.render(f"Manuscripts left: {manuscripts_left}   (Press R to regen)", True, (240,240,240))
    screen.blit(txt, (4, 4))

# MAIN
grid, player_pos, ghost_pos = generate_map()
# menghitung sisa dari manuscript yang belum diambil
manuscripts_left = sum(1 for r in range(GRID) for c in range(GRID) if grid[r][c] == MANUSCRIPT)

# berjalannya game
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                grid, player_pos, ghost_pos = generate_map()
                manuscripts_left = sum(1 for r in range(GRID) for c in range(GRID) if grid[r][c] == MANUSCRIPT)
            if event.key == pygame.K_ESCAPE:
                running = False

    screen.fill((0,0,0))
    draw(grid, player_pos, ghost_pos, manuscripts_left)
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()