import random
from settings import *

def causes_clump(grid, r, c):
    # cek tile apakah tembol
    def is_wall(nr, nc):
        if 0 <= nr < GRID and 0 <= nc < GRID:
            return grid[nr][nc] in [WALL, WALL_SEALED]
        return True # UPDATE: it wouldn't want to stick to wall

    # check directions clumping 2x2
    checks = [
        [(r-1, c), (r, c-1), (r-1, c-1)], # NW
        [(r-1, c), (r, c+1), (r-1, c+1)], # NE
        [(r+1, c), (r, c-1), (r+1, c-1)], # SW
        [(r+1, c), (r, c+1), (r+1, c+1)]  # SE
    ]

    for check in checks:
        if all(is_wall(nr, nc) for nr, nc in check):
            return True # Terdeteksi akan membentuk kotak 2x2!
            
    return False

# so there is a case where the
# sprite (player/ghost) spawned in a "chamber"
# that isolates them from playing
def is_map_valid(grid):
    walkable_tiles=[]
    for r in range(GRID):
        for c in range(GRID):
            # player bisa berjalan di Regular Floor, Sealed Floor, Manuscript
            if grid[r][c] in [FLOOR, SEALED_FLOOR, MANUSCRIPT, MANUSCRIPT_SEALED]: # NEW MANUSCRIPT_SEALED
                walkable_tiles.append((r, c))
    
    if not walkable_tiles:
        return False

    # inisiasi Flood Fill
    start_pos = walkable_tiles[0]
    queue = [start_pos]
    visited = {start_pos}
    count = 0

    while queue:
        r, c = queue.pop(0)
        count += 1

        # check 4 area (up, down, left, right)
        neighbors = [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]
        for nr, nc in neighbors:
            if 0 <= nr < GRID and 0 <= nc < GRID:
                
                if (nr, nc) not in visited and grid[nr][nc] in [FLOOR, SEALED_FLOOR, MANUSCRIPT, MANUSCRIPT_SEALED]: # NEW MANUSCRIPT_SEALED    
                    visited.add((nr, nc))
                    queue.append((nr, nc))
    return count == len(walkable_tiles)

# MAP GENERATOR
def generate_map(difficulty="EASY"):
    config = DIFFICULTY_SETTINGS[difficulty]

    # ADDITIONALS
    wall_min, wall_max = config["wall_range"]
    sealed_floors_count = config["sealed_floors"]
    wall_chance = config["wall_chance"]
    spawn_dist = config["spawn_dist"]

    while True:
    # insisiasi map structure dasar
        grid = [[FLOOR for _ in range(GRID)] for _ in range(GRID)]

    # random wall placement
        total_walls = random.randint(wall_min, wall_max) # update this to wall_min and wall_max
        placed = 0
        attempts = 0
        while placed < total_walls and attempts < 200:
            attempts += 1
            r = random.randint(0, GRID - 1)
            c = random.randint(0, GRID - 1)

            # menghindari sealed atau manuskrip terlalu awal

            # UPDATE: jika 70% WALL 30% SEALED_WALL
            if grid[r][c] == FLOOR:
                if causes_clump(grid, r, c):
                    continue
                rng = random.random()
                if rng < wall_chance: # CHANGED: config chance
                    grid[r][c] = WALL
                else:
                    grid[r][c] = WALL_SEALED
                placed += 1

    # NOTES: diubah, tidak ada minimal untuk sealed floor
    # menaruh 3 sealed floor secara random
        sealed_positions = []
        attempts = 0
        while len(sealed_positions) < sealed_floors_count and attempts < 200: # CHAMGED: config count
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
            if grid[r][c] == SEALED_FLOOR:              # NEW MANUSCRIPT_SEALED
                grid[r][c] = MANUSCRIPT_SEALED
                manuscript_positions.append((r, c))

        # UPDATE: sebelum menempatkan player, cek valid atau tidak mapnya,
        # sebelumnya diemplementasikan attempt menebak penempatan dengan looping 500x player di floor 
        if is_map_valid(grid):
            # checks out the safest spot, penetapannya di Regular Floor
            safe_spots = []
            for r in range(GRID):
                for c in range(GRID):
                    if grid[r][c] == FLOOR:
                        safe_spots.append((r,c))
            
            if len(safe_spots) >= 2:    # untuk spot Player & Ghost
                player_pos = random.choice(safe_spots)
                safe_spots.remove(player_pos)

                # UPDATE: change Ghost position, so that it doesn't necessarily near the Player
                random.shuffle(safe_spots)
                validate_ghost_found = False
                ghost_pos = None

                for potential_pos in safe_spots:
                    gr, gc = potential_pos
                    pr, pc = player_pos

                    # Manhattan distance (3 steps far)
                    dist = abs(gr - pr) + abs(gc - pc)
                    if (dist) < spawn_dist: continue    # CHANGED: config distance

                    neighbors = [(gr-1, gc), (gr+1, gc), (gr, gc-1), (gr, gc+1)]
                    # isn't isolated by the Sealed Floor
                    has_exit = False
                    for nr, nc in neighbors:
                        if 0 <= nr < GRID and 0 <= nc < GRID:
                            if grid[nr][nc] in [FLOOR, MANUSCRIPT]: # Jalan legal buat hantu
                                has_exit = True
                                break
                    # simpan kalo ketemu
                    if has_exit:
                        ghost_pos = potential_pos
                        validate_ghost_found = True # Tandai bahwa berhasil
                        break


                if validate_ghost_found:
                    return grid, player_pos, ghost_pos