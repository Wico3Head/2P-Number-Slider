from setting import *
from puzzle import Puzzle
import pygame, random

class DisplayPuzzle(Puzzle):
    def __init__(self, difficulty, size, window, position):
        super().__init__(difficulty)
        self.size = size
        self.window = window
        self.position = position

        self.previous_demo_move = None

        self.animating = False
        self.animation_frames = None
        self.animating_piece_coordinate = None
        self.animating_piece = None
        self.animating_direction = None
        self.accumulated_movement = 0

        self.tile_size = (1 - PUZZLE_BORDER_SIZE) * self.size / self.difficulty
        self.tile_offset = PUZZLE_BORDER_SIZE / 2 * self.size
        self.textures = {
            1: pygame.transform.scale(pygame.image.load(os.path.join(LOCAL_DIR, 'Assets/Tile1.png')), (self.tile_size, self.tile_size)),
            2: pygame.transform.scale(pygame.image.load(os.path.join(LOCAL_DIR, 'Assets/Tile2.png')), (self.tile_size, self.tile_size)),
            3: pygame.transform.scale(pygame.image.load(os.path.join(LOCAL_DIR, 'Assets/Tile3.png')), (self.tile_size, self.tile_size)),
            4: pygame.transform.scale(pygame.image.load(os.path.join(LOCAL_DIR, 'Assets/Tile4.png')), (self.tile_size, self.tile_size)),
            5: pygame.transform.scale(pygame.image.load(os.path.join(LOCAL_DIR, 'Assets/Tile5.png')), (self.tile_size, self.tile_size)),
            6: pygame.transform.scale(pygame.image.load(os.path.join(LOCAL_DIR, 'Assets/Tile6.png')), (self.tile_size, self.tile_size)),
            7: pygame.transform.scale(pygame.image.load(os.path.join(LOCAL_DIR, 'Assets/Tile7.png')), (self.tile_size, self.tile_size)),
            8: pygame.transform.scale(pygame.image.load(os.path.join(LOCAL_DIR, 'Assets/Tile8.png')), (self.tile_size, self.tile_size)),
            9: pygame.transform.scale(pygame.image.load(os.path.join(LOCAL_DIR, 'Assets/Tile9.png')), (self.tile_size, self.tile_size)),
            10: pygame.transform.scale(pygame.image.load(os.path.join(LOCAL_DIR, 'Assets/Tile10.png')), (self.tile_size, self.tile_size)),
            11: pygame.transform.scale(pygame.image.load(os.path.join(LOCAL_DIR, 'Assets/Tile11.png')), (self.tile_size, self.tile_size)),
            12: pygame.transform.scale(pygame.image.load(os.path.join(LOCAL_DIR, 'Assets/Tile12.png')), (self.tile_size, self.tile_size)),
            13: pygame.transform.scale(pygame.image.load(os.path.join(LOCAL_DIR, 'Assets/Tile13.png')), (self.tile_size, self.tile_size)),
            14: pygame.transform.scale(pygame.image.load(os.path.join(LOCAL_DIR, 'Assets/Tile14.png')), (self.tile_size, self.tile_size)),
            15: pygame.transform.scale(pygame.image.load(os.path.join(LOCAL_DIR, 'Assets/Tile15.png')), (self.tile_size, self.tile_size)),
            16: pygame.transform.scale(pygame.image.load(os.path.join(LOCAL_DIR, 'Assets/Tile16.png')), (self.tile_size, self.tile_size)),
            17: pygame.transform.scale(pygame.image.load(os.path.join(LOCAL_DIR, 'Assets/Tile17.png')), (self.tile_size, self.tile_size)),
            18: pygame.transform.scale(pygame.image.load(os.path.join(LOCAL_DIR, 'Assets/Tile18.png')), (self.tile_size, self.tile_size)),
            19: pygame.transform.scale(pygame.image.load(os.path.join(LOCAL_DIR, 'Assets/Tile19.png')), (self.tile_size, self.tile_size)),
            20: pygame.transform.scale(pygame.image.load(os.path.join(LOCAL_DIR, 'Assets/Tile20.png')), (self.tile_size, self.tile_size)),
            21: pygame.transform.scale(pygame.image.load(os.path.join(LOCAL_DIR, 'Assets/Tile21.png')), (self.tile_size, self.tile_size)),
            22: pygame.transform.scale(pygame.image.load(os.path.join(LOCAL_DIR, 'Assets/Tile22.png')), (self.tile_size, self.tile_size)),
            23: pygame.transform.scale(pygame.image.load(os.path.join(LOCAL_DIR, 'Assets/Tile23.png')), (self.tile_size, self.tile_size)),
            24: pygame.transform.scale(pygame.image.load(os.path.join(LOCAL_DIR, 'Assets/Tile24.png')), (self.tile_size, self.tile_size)),
            'board': pygame.transform.scale(pygame.image.load(os.path.join(LOCAL_DIR, 'Assets/boardBackground.png')), (self.size, self.size)),
        }

        self.finished_backgrond = pygame.Surface((self.size, self.size))
        self.finished_backgrond.set_alpha(150)
        self.finished_backgrond.fill(BLACK)
        self.finished_msg = big_font.render('Puzzle Solved!', False, WHITE)
        self.finished_msg_rect = self.finished_msg.get_rect(center=(self.position[0] + self.size/2, self.position[1] + self.size/2 - 25))
        self.won_msg = big_font.render('You Won!', False, WHITE)
        self.won_msg_rect = self.won_msg.get_rect(center=(self.position[0] + self.size/2, self.position[1] + self.size/2 - 25))
        self.lost_msg = big_font.render('Tough Luck!', False, WHITE)
        self.lost_msg_rect = self.lost_msg.get_rect(center=(self.position[0] + self.size/2, self.position[1] + self.size/2 - 25))
        self.vs_restart_msg = small_font.render('click on me to start another race!', False, WHITE)
        self.vs_restart_msg_rect = self.vs_restart_msg.get_rect(center=(self.position[0] + self.size/2, self.position[1] + self.size/2 + 25))
        self.restart_msg = small_font.render('click on me to restart the game!', False, WHITE)
        self.restart_msg_rect = self.restart_msg.get_rect(center=(self.position[0] + self.size/2, self.position[1] + self.size/2 + 25))

    def displayMove(self, direction):
        direction_moved, (row, column) = self.move(direction)
        if not direction_moved:
            return False

        self.isSolved()
        if direction == 'up':            
            self.animating_piece_coordinate = [self.position[0] + self.tile_offset + column * self.tile_size, self.position[1] + self.tile_offset + (row + 1) * self.tile_size]
            self.animating_direction = (0, -1)
            self.animating_piece = self.state[row][column]
            return True

        elif direction == 'down':
            self.animating_piece_coordinate = [self.position[0] + self.tile_offset + column * self.tile_size, self.position[1] + self.tile_offset + (row - 1) * self.tile_size]
            self.animating_direction = (0, 1)
            self.animating_piece = self.state[row][column]
            return True

        elif direction == 'left':  
            self.animating_piece_coordinate = [self.position[0] + self.tile_offset + (column + 1) * self.tile_size, self.position[1] + self.tile_offset + row * self.tile_size]
            self.animating_direction = (-1, 0)
            self.animating_piece = self.state[row][column]
            return True

        else: #right
            self.animating_piece_coordinate = [self.position[0] + self.tile_offset + (column - 1) * self.tile_size, self.position[1] + self.tile_offset + row * self.tile_size]
            self.animating_direction = (1, 0)
            self.animating_piece = self.state[row][column]
            return True

    def draw(self):
        self.window.blit(self.textures['board'], self.position)
        for row in range(self.difficulty):
            for column in range(self.difficulty):
                element = self.state[row][column]
                if element == 0:
                    continue
                texture = self.textures[element]
                coordinate = (self.position[0] + self.tile_offset + column * self.tile_size, self.position[1] + self.tile_offset + row * self.tile_size)
                self.window.blit(texture, coordinate)

    def animate(self):
        self.window.blit(self.textures['board'], self.position)
        for row in range(self.difficulty):
            for column in range(self.difficulty):
                element = self.state[row][column]
                if element == 0 or element == self.animating_piece:
                    continue
                texture = self.textures[self.state[row][column]]
                coordinate = (self.position[0] + self.tile_offset + column * self.tile_size, self.position[1]+ self.tile_offset + row * self.tile_size)
                self.window.blit(texture, coordinate)

        movement = self.tile_size / self.animation_frames
        self.accumulated_movement += movement
        if self.accumulated_movement < self.tile_size:
            self.animating_piece_coordinate = [self.animating_piece_coordinate[0] + movement * self.animating_direction[0], 
                                               self.animating_piece_coordinate[1] + movement * self.animating_direction[1]]
            self.window.blit(self.textures[self.animating_piece], self.animating_piece_coordinate)
        else:
            self.draw()
            self.animating = False

    def update(self, direction, animation_frames):
        if direction != None:
            if not self.animating:
                moved = self.displayMove(direction)
                if not moved or animation_frames == 0:
                    self.draw()
                    return
                
                self.animating = True
                self.accumulated_movement = 0
                self.animation_frames = animation_frames

            self.animate()
        else:
            self.draw() if not self.animating else self.animate()

    def getDemoMove(self):
        choices = []
        flag = False
        for row in range(self.difficulty):
            if flag:
                break
            for column in range(self.difficulty):
                if self.state[row][column] == 0:
                    flag = True
                    if row != self.difficulty - 1 and self.previous_demo_move != opposites['up']: 
                        choices.append('up')
                    
                    if row != 0 and self.previous_demo_move != opposites["down"]:
                        choices.append('down')

                    if column != self.difficulty - 1 and self.previous_demo_move != opposites['left']:
                        choices.append('left')

                    if column != 0 and self.previous_demo_move != opposites['right']:
                        choices.append('right')
                    break

        new_demo_move = random.choice(choices)
        self.previous_demo_move = new_demo_move
        return new_demo_move