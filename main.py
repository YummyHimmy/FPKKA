import pygame
import os
import random
import math
import sys
from settings import *
from ghost_movements import astar
GHOST_MAX_STEPS = 3
GHOST_MOVING = 2
GAME_OVER = 3
ghost_path = []
ghost_step_index = 0
ghost_last_move_time = 0

GHOST_STEP_DELAY = 120  # ms, atur sesuai rasa (lebih kecil = lebih cepat)
import map
import level_controller # imports the difficulties setting
from movement import Controller # import player control
import movement

from home_screen import HomeScreen  # Import the home screen
import time
# Initialize game and window display
pygame.init()
screen = pygame.display.set_mode((
    WIDTH + SIDEBAR_WIDTH,
    HEIGHT + TOP_BAR_HEIGHT
))

pygame.display.set_caption("EXORCIZE")
clock = pygame.time.Clock()

# Load the home screen
home_screen = HomeScreen(WIDTH + SIDEBAR_WIDTH, HEIGHT + TOP_BAR_HEIGHT)

# Run home screen and get selected difficulty
selected_difficulty = home_screen.run(screen)
pygame.event.clear()
if selected_difficulty is None:
    # User quit from home screen
    pygame.quit()
    sys.exit()

# Set the selected difficulty
current_difficulty = selected_difficulty
grid, player_pos, ghost_pos = map.generate_map(current_difficulty)

# Initialize movement controller AFTER home screen
movement = Controller()

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

# The assets
player_sprites = {
    "UP": load_asset("Avatar\Avatar_Up.png"),
    "DOWN": load_asset("Avatar\Avatar_Down.png"),
    "LEFT": load_asset("Avatar\Avatar_Left.png"),
    "RIGHT": load_asset("Avatar\Avatar_Right.png"),

    "UP_LEFT": load_asset("Avatar\Avatar_Up_Left.png"),
    "UP_RIGHT": load_asset("Avatar\Avatar_Up_Right.png"),
    "DOWN_LEFT": load_asset("Avatar\Avatar_Down_Left.png"),
    "DOWN_RIGHT": load_asset("Avatar\Avatar_Down_Right.png"),
}

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
if ghost_img is None:
    ghost_img = solid_surface((200, 60, 140))
for k, v in player_sprites.items():
    if v is None:
        player_sprites[k] = solid_surface((60, 140, 220))


# DRAW THE GAME TO THE WINDOW
# Additional variable in the parameter 'curr_diff'
movement.pixel_x = player_pos[1] * TILE_SIZE
movement.pixel_y = player_pos[0] * TILE_SIZE

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
    player_img = player_sprites.get(movement.direction, player_sprites["DOWN"])
    y_offset = int(2 * math.sin(movement.animation)) if movement.is_moving else 0
    screen.blit(player_img, (
        int(movement.pixel_x) + GAME_OFFSET_X,
        int(movement.pixel_y) + GAME_OFFSET_Y + y_offset
    ))

    gr, gc = ghost_pos
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
    elif turn_state == GAME_OVER:
        state = "GAME OVER"
        state_color = (200, 80, 80)

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
        #"R      : Regenerate map",
        "ESC    : Quit game",
        "M  : Main Menu"
    ]

    # tampilin timer
    if start_time is not None:
        total_time = int(time.time() - start_time)
        minutes = total_time // 60
        seconds = total_time % 60
        timer_str = f"{minutes:02d}:{seconds:02d}"
        timer_font = pygame.font.SysFont("consolas", 35, bold=True)
        screen.blit(
            timer_font.render(f"Time: {timer_str}", True, (200, 200, 200)),
            (sidebar_x + 28, y + 10)  
        )


    y = TOP_BAR_HEIGHT + 52
    for c in controls:
        screen.blit(
            font_text.render(c, True, (210, 210, 210)),
            (sidebar_x + 16, y)
        )
        y += 22

def draw_game_over():
    popup_width, popup_height = WIDTH // 2, HEIGHT // 4
    popup = pygame.Surface((popup_width, popup_height), pygame.SRCALPHA)
    popup.fill((40, 10, 10, 230))

    font_big = pygame.font.SysFont("consolas", 42, bold=True)
    font_small = pygame.font.SysFont("consolas", 20)

    text = font_big.render("GAME OVER", True, (240, 100, 100))
    hint = font_small.render("Press M to return to menu", True, (220, 200, 200))

    popup.blit(text, text.get_rect(center=(popup_width//2, popup_height//2 - 10)))
    popup.blit(hint, hint.get_rect(center=(popup_width//2, popup_height//2 + 30)))

    screen.blit(
        popup,
        ((WIDTH - popup_width)//2, (HEIGHT - popup_height)//2)
    )


# MAIN
# menghitung sisa dari manuscript yang belum diambil
manuscripts_left = sum(1 for r in range(GRID) for c in range(GRID) if grid[r][c] in [MANUSCRIPT, MANUSCRIPT_SEALED])
start_time = time.time() # Mulai timer
# berjalannya game
running = True
while running:
    for event in pygame.event.get():
        
        if event.type == pygame.QUIT:
            running = False

        if turn_state == GAME_OVER:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    home_screen = HomeScreen(WIDTH + SIDEBAR_WIDTH, HEIGHT + TOP_BAR_HEIGHT)
                    selected_difficulty = home_screen.run(screen)
                    if selected_difficulty:
                        current_difficulty = selected_difficulty
                        grid, player_pos, ghost_pos = map.generate_map(current_difficulty)
                        turn_state = PLAYER_PLANNING # Agar selalu player jalan pertama
                        ghost_turn_start = None
                        player_done = False 
                        start_time = time.time()
                        movement.reset_path()
                        movement.is_moving = False
                        movement.animation = 0
                        movement.direction = "DOWN"
                        movement.pixel_x = player_pos[1] * TILE_SIZE
                        movement.pixel_y = player_pos[0] * TILE_SIZE

                        manuscripts_left = sum(
                            1 for r in range(GRID) for c in range(GRID)
                            if grid[r][c] in [MANUSCRIPT, MANUSCRIPT_SEALED]
                        )

                        turn_state = PLAYER_PLANNING
            continue

        # ---------------- MOVEMENT INPUT ----------------
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and turn_state == PLAYER_PLANNING:
            mx, my = pygame.mouse.get_pos()
            movement.handle_mouse_click(
                (mx, my - TOP_BAR_HEIGHT),
                grid,
                player_pos
            )

        if event.type == pygame.KEYDOWN:
            result = level_controller.game_difficulties(event, current_difficulty)
            # Confirm movement with 'Enter' key
            if event.key == pygame.K_RETURN and turn_state == PLAYER_PLANNING: 
                movement.confirm_move()
                if movement.path:
                    turn_state = PLAYER_MOVING
                    
            if event.key == pygame.K_z: # Reset dot placement with 'z' key
                movement.reset_path()
            
            if event.key == pygame.K_m:  # Return to menu with 'm' key
                # Restart home screen
                home_screen = HomeScreen(WIDTH + SIDEBAR_WIDTH, HEIGHT + TOP_BAR_HEIGHT)
                selected_difficulty = home_screen.run(screen)
                if selected_difficulty:
                    current_difficulty = selected_difficulty
                    grid, player_pos, ghost_pos = map.generate_map(current_difficulty)
                    movement.reset_path()
                    movement.is_moving = False
                    movement.animation = 0
                    movement.direction = "DOWN"

                    # FIX #1: SYNC VISUALS AFTER MENU RESET
                    # # snaps sprite to new logic position
                    movement.pixel_x = player_pos[1] * TILE_SIZE
                    movement.pixel_y = player_pos[0] * TILE_SIZE

                    manuscripts_left = sum(1 for r in range(GRID) for c in range(GRID) if grid[r][c] in [MANUSCRIPT, MANUSCRIPT_SEALED])

            
            if not result['running']:
                running = False
                
            if result['regen']:
                movement.path.clear()
                movement.is_moving = False  
                movement.animation = 0
                movement.direction = "DOWN"              
                current_difficulty = result['difficulty']
                grid, player_pos, ghost_pos = map.generate_map(current_difficulty)
                ghost_turn_start = None
                player_done = False 
                turn_state = PLAYER_PLANNING
                start_time = time.time()
                # FIX #2: SYNC VISUALS AFTER REGEN (R/1/2/3)
                # snaps sprite to new logic position
                movement.pixel_x = player_pos[1] * TILE_SIZE
                movement.pixel_y = player_pos[0] * TILE_SIZE

                # UPDATE: there was a bug of which was just counting manuscript in Regular Floor
                manuscripts_left = sum(1 for r in range(GRID) for c in range(GRID) if grid[r][c] in [MANUSCRIPT, MANUSCRIPT_SEALED])

        


    player_done = movement.is_moving
    player_pos = movement.update(player_pos)

    pr, pc = player_pos # pr = player row; pc = player column. Posisinya

    if grid[pr][pc] == MANUSCRIPT:
        grid[pr][pc] =FLOOR
        manuscripts_left -= 1

    elif grid[pr][pc] == MANUSCRIPT_SEALED:
        grid[pr][pc] = SEALED_FLOOR
        manuscripts_left -= 1
    
    if manuscripts_left <= 0:
        total_time = time.time() - start_time
        minutes = int(total_time // 60)
        seconds = int(total_time % 60)
        time_str = f"{minutes}m {seconds}s"
        # Munculin pop up You Win
        popup_width, popup_height = WIDTH // 2, HEIGHT // 3  
        popup_surface = pygame.Surface((popup_width, popup_height), pygame.SRCALPHA)
        popup_surface.fill((30, 30, 40, 230))
        win_font = pygame.font.SysFont("Consolas", 36, bold=True)
        win_text = win_font.render("You Win!", True, (220, 180, 240))
        win_rect = win_text.get_rect(center=(popup_width//2, popup_height//3))
        popup_surface.blit(win_text, win_rect)

        time_font = pygame.font.SysFont("Consolas", 24, bold=True)
        time_text = time_font.render(f"Time spent: {time_str}", True, (200, 200, 200))
        time_rect = time_text.get_rect(center=(popup_width//2, 2 * popup_height//3))
        popup_surface.blit(time_text, time_rect)
        screen.blit(popup_surface, ((WIDTH - popup_width)//2, (HEIGHT - popup_height)//2))
        
        draw(grid, player_pos, ghost_pos, manuscripts_left, current_difficulty)
        movement.draw_path(screen, GAME_OFFSET_X, GAME_OFFSET_Y)


        if turn_state == GAME_OVER:
            draw_game_over()
        

        pygame.display.flip()
        pygame.time.delay(2000)

        #Balik ke homescreen
        home_screen = HomeScreen(WIDTH + SIDEBAR_WIDTH, HEIGHT + TOP_BAR_HEIGHT)
        selected_difficulty = home_screen.run(screen)
        if selected_difficulty:
            current_difficulty = selected_difficulty
            grid, player_pos, ghost_pos = map.generate_map(current_difficulty)
            start_time = time.time()
            ghost_turn_start = None
            turn_state = PLAYER_PLANNING
            player_done = False 
            movement.reset_path()
            movement.is_moving = False
            movement.animation = 0
            movement.direction = "DOWN"
            movement.pixel_x = player_pos[1] * TILE_SIZE
            movement.pixel_y = player_pos[0] * TILE_SIZE

            manuscripts_left = sum(1 for r in range(GRID) for c in range(GRID) if grid[r][c] in [MANUSCRIPT, MANUSCRIPT_SEALED])

        else:
            running = False #player berenti

    if player_done and not movement.is_moving:
        turn_state = GHOST_MOVING
        ghost_turn_start = pygame.time.get_ticks()

        # HITUNG PATH SEKALI
        full_path = astar(grid, ghost_pos, player_pos)
        if full_path:
            ghost_path = full_path[:GHOST_MAX_STEPS]
        else:
            ghost_path = []

        ghost_step_index = 0
        ghost_last_move_time = pygame.time.get_ticks()

    GHOST_TURN_DELAY = 540  # 0.54 detik dulu biar keliatan

    if turn_state == GHOST_MOVING:
        now = pygame.time.get_ticks()

        if ghost_step_index < len(ghost_path):
            if now - ghost_last_move_time >= GHOST_STEP_DELAY:
                ghost_pos = ghost_path[ghost_step_index]
                ghost_step_index += 1
                ghost_last_move_time = now

                if ghost_pos == player_pos:
                    turn_state = GAME_OVER
        else:
            # Ghost selesai bergerak
            turn_state = PLAYER_PLANNING
            ghost_path = []
        

    screen.fill((0,0,0))
    draw(grid, player_pos, ghost_pos, manuscripts_left, current_difficulty)
    movement.draw_path(screen, GAME_OFFSET_X, GAME_OFFSET_Y)
    if turn_state == GAME_OVER:
        draw_game_over()
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
