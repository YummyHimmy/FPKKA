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
screen = pygame.display.set_mode((
    WIDTH + SIDEBAR_WIDTH,
    HEIGHT + TOP_BAR_HEIGHT
))

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
                screen.blit(floor_regular, (x + GAME_OFFSET_X, y + GAME_OFFSET_Y))
            elif t == WALL:
                screen.blit(wall_regular, (x + GAME_OFFSET_X, y + GAME_OFFSET_Y))
            elif t == WALL_SEALED:                  # UPDATE: add sealed wall
                screen.blit(wall_sealed, (x + GAME_OFFSET_X, y + GAME_OFFSET_Y))
            elif t == SEALED_FLOOR:
                screen.blit(floor_sealed, (x + GAME_OFFSET_X, y + GAME_OFFSET_Y))
            elif t == MANUSCRIPT:
                screen.blit(floor_regular, (x + GAME_OFFSET_X, y + GAME_OFFSET_Y))
                screen.blit(manuscript_img, (x + GAME_OFFSET_X, y + GAME_OFFSET_Y))
            elif t == MANUSCRIPT_SEALED:            # NEW MANUSCRIPT_SEALED
                screen.blit(floor_sealed, (x + GAME_OFFSET_X, y + GAME_OFFSET_Y))
                screen.blit(manuscript_img, (x + GAME_OFFSET_X, y + GAME_OFFSET_Y))
    # player & ghost
    pr, pc = player_pos
    gr, gc = ghost_pos
    screen.blit(player_img, (
        pc * TILE_SIZE + GAME_OFFSET_X,
        pr * TILE_SIZE + GAME_OFFSET_Y
    ))
    screen.blit(ghost_img, (
        gc * TILE_SIZE + GAME_OFFSET_X,
        gr * TILE_SIZE + GAME_OFFSET_Y
    ))

    # -------- TOP BAR --------
    bar_rect = pygame.Rect(0, 0, WIDTH + SIDEBAR_WIDTH, TOP_BAR_HEIGHT)
    pygame.draw.rect(screen, (20, 20, 20), bar_rect)

    font = pygame.font.SysFont("consolas", 18)

    left_text = f"Difficulty: {curr_diff} | Manuscripts: {manuscripts_left}"
    screen.blit(font.render(left_text, True, (230, 230, 230)), (WIDTH - 95, 10))

    if turn_state == PLAYER_PLANNING:
        state = "Plan your moves carefully"
        state_color = (80, 200, 120)
    elif turn_state == PLAYER_MOVING:
        state = "Make it count"
        state_color = (200, 160, 80)
    else:  # GHOST_MOVING
        dots = "." * ((pygame.time.get_ticks() // 500) % 4)
        state = "The soul pursue" + dots
        state_color = (200, 80, 80)

    screen.blit(font.render(state, True, state_color), (12, 10))


    # -------- SIDEBAR --------
    sidebar_x = WIDTH
    sidebar_rect = pygame.Rect(
        sidebar_x,
        TOP_BAR_HEIGHT,
        SIDEBAR_WIDTH,
        HEIGHT
    )

    pygame.draw.rect(screen, (25, 25, 35), sidebar_rect)

    font_title = pygame.font.SysFont("consolas", 18, bold=True)
    font_text  = pygame.font.SysFont("consolas", 14)

    screen.blit(
        font_title.render("CONTROLS", True, (240, 220, 180)),
        (sidebar_x + 16, TOP_BAR_HEIGHT + 16)
    )

    controls = [
        "Click  : Place movement dot",
        "ENTER  : Confirm move",
        "Z      : Reset path",
        "R      : Regenerate map",
        "ESC    : Quit game",
        "1,2,3  : Change level"
    ]

    y = TOP_BAR_HEIGHT + 52
    for c in controls:
        screen.blit(
            font_text.render(c, True, (210, 210, 210)),
            (sidebar_x + 16, y)
        )
        y += 22

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
            mx, my = pygame.mouse.get_pos()
            movement.handle_mouse_click(
                (mx, my - TOP_BAR_HEIGHT),
                grid,
                player_pos
            )

        if event.type == pygame.KEYDOWN:
            result = level_controller.game_difficulties(event, current_difficulty)
            
            if event.key == pygame.K_RETURN: # Confirm movement with 'Enter' key
                movement.confirm_move()
                if movement.path:
                    turn_state = PLAYER_MOVING
                    
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

    player_done = movement.is_moving
    player_pos = movement.update(player_pos)

    if player_done and not movement.is_moving:
        turn_state = GHOST_MOVING
        ghost_turn_start = pygame.time.get_ticks()

    GHOST_TURN_DELAY = 5400 # dalam milisekon (detik = t/1000)
    
    if turn_state == GHOST_MOVING:
        now = pygame.time.get_ticks()

        if now - ghost_turn_start >= GHOST_TURN_DELAY:
            # TODO: move ghost here later
            turn_state = PLAYER_PLANNING
            ghost_turn_start = None


    screen.fill((0,0,0))
    draw(grid, player_pos, ghost_pos, manuscripts_left, current_difficulty) # Additional 'current_difficulty' in the function's parameter
    movement.draw_path(screen, GAME_OFFSET_X, GAME_OFFSET_Y)
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()