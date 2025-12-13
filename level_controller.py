import pygame

def game_difficulties(event, curr_difficulty):
    """"
    takes the input of number (1,2,3)
    to the difficulty (easy,medium,hard)

    regen, boolean to regenerate map
    running, is the game still running
    """

    result = {
        'difficulty': curr_difficulty,
        'regen': False,
        'running': True
    }

    if event.key == pygame.K_1:
        result['difficulty'] = "EASY"
        result['regen'] = True
    elif event.key == pygame.K_2:
        result['difficulty'] = "MEDIUM"
        result['regen'] = True
    elif event.key == pygame.K_3:
        result['difficulty'] = "HARD"
        result['regen'] = True
    
    # Cek tombol fungsi (Regen & Quit)
    elif event.key == pygame.K_r:
        result['regen'] = True
    elif event.key == pygame.K_ESCAPE:
        result['running'] = False
        
    return result
