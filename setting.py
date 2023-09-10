import os, pygame
pygame.init()

SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 750

WHITE = (255, 255, 255)
GREY = (100, 100, 100)
BLACK = (0, 0, 0)

LOCAL_DIR = os.path.dirname(__file__)

big_font = pygame.font.Font(os.path.join(LOCAL_DIR, 'Assets/pixel.ttf'), 70)
small_font = pygame.font.Font(os.path.join(LOCAL_DIR, 'Assets/pixel.ttf'), 40)

opposites = {
    'up': 'down',
    'down': 'up',
    'left': 'right',
    'right': 'left'
}

directions = {
    0: 'up',
    1: 'down',
    2: 'left',
    3: 'right'
}

MOVES_LOOK_AHEAD = 12