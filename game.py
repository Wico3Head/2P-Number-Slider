import pygame, os, random
from setting import *

class Game:
    def __init__(self, width, height, window, position=(0, 0)):
        self.width = width
        self.height = height
        self.window = window
        self.position = position
        self.moves = 0

        self.animating = False
        self.animation_frames = None
        self.animating_piece_coordinate = None
        self.animating_piece = None
        self.animating_direction = None
        self.accumulated_movement = 0

        self.state = [[1, 2, 3],
                      [4, 5, 6],
                      [7, 8, 0]]
        
        self.textures = {
            1: pygame.transform.scale(pygame.image.load(os.path.join(LOCAL_DIR, 'Assets/Tile1.png')), (width/3, height/3)),
            2: pygame.transform.scale(pygame.image.load(os.path.join(LOCAL_DIR, 'Assets/Tile2.png')), (width/3, height/3)),
            3: pygame.transform.scale(pygame.image.load(os.path.join(LOCAL_DIR, 'Assets/Tile3.png')), (width/3, height/3)),
            4: pygame.transform.scale(pygame.image.load(os.path.join(LOCAL_DIR, 'Assets/Tile4.png')), (width/3, height/3)),
            5: pygame.transform.scale(pygame.image.load(os.path.join(LOCAL_DIR, 'Assets/Tile5.png')), (width/3, height/3)),
            6: pygame.transform.scale(pygame.image.load(os.path.join(LOCAL_DIR, 'Assets/Tile6.png')), (width/3, height/3)),
            7: pygame.transform.scale(pygame.image.load(os.path.join(LOCAL_DIR, 'Assets/Tile7.png')), (width/3, height/3)),
            8: pygame.transform.scale(pygame.image.load(os.path.join(LOCAL_DIR, 'Assets/Tile8.png')), (width/3, height/3)),
            'board': pygame.transform.scale(pygame.image.load(os.path.join(LOCAL_DIR, 'Assets/boardBackground.png')), (width, height)),
        }
        self.game_won = False

        self.finished_backgrond = pygame.Surface((width, height))
        self.finished_backgrond.set_alpha(150)
        self.finished_backgrond.fill(BLACK)
        self.finished_msg = big_font.render('Puzzle Solved!', False, WHITE)
        self.finished_msg_rect = self.finished_msg.get_rect(center=(self.position[0] + width/2, self.position[1] + height/2 - 25))
        self.won_msg = big_font.render('You Won!', False, WHITE)
        self.won_msg_rect = self.won_msg.get_rect(center=(self.position[0] + width/2, self.position[1] + height/2 - 25))
        self.lost_msg = big_font.render('Tough Luck!', False, WHITE)
        self.lost_msg_rect = self.lost_msg.get_rect(center=(self.position[0] + width/2, self.position[1] + height/2 - 25))
        self.vs_restart_msg = small_font.render('click on me to start another race!', False, WHITE)
        self.vs_restart_msg_rect = self.vs_restart_msg.get_rect(center=(self.position[0] + width/2, self.position[1] + height/2 + 25))
        self.restart_msg = small_font.render('click on me to restart the game!', False, WHITE)
        self.restart_msg_rect = self.restart_msg.get_rect(center=(self.position[0] + width/2, self.position[1] + height/2 + 25))

        for i in range(1000):
            self.move(random.choice(['up', 'down', 'left', 'right']))

        self.start_time = pygame.time.get_ticks()
        self.moves = 0

    def move(self, direction):
        if not direction:
            return False

        self.moves += 1
        for row in range(3):
            for column in range(3):
                element = self.state[row][column]
                if element == 0:
                    if direction == 'up':
                        if row == 2:
                            return False
                        self.state[row][column] = self.state[row + 1][column]
                        self.state[row + 1][column] = 0
                        
                        self.animating_piece_coordinate = [self.position[0] + column * self.width / 3, self.position[1] + (row + 1) * self.height/3]
                        self.animating_direction = (0, -1)
                        self.animating_piece = self.state[row][column]
                        self.isFinished()
                        return True

                    elif direction == 'down':
                        if row == 0:
                            return False
                        self.state[row][column] = self.state[row - 1][column]
                        self.state[row - 1][column] = 0
                        
                        self.animating_piece_coordinate = [self.position[0] + column * self.width / 3, self.position[1] + (row - 1) * self.height/3]
                        self.animating_direction = (0, 1)
                        self.animating_piece = self.state[row][column]
                        self.isFinished()
                        return True

                    elif direction == 'left':
                        if column == 2:
                            return False
                        self.state[row][column] = self.state[row][column + 1]
                        self.state[row][column + 1] = 0
                        
                        self.animating_piece_coordinate = [self.position[0] + (column + 1) * self.width / 3, self.position[1] + row * self.height/3]
                        self.animating_direction = (-1, 0)
                        self.animating_piece = self.state[row][column]
                        self.isFinished()
                        return True

                    else: #right
                        if column == 0:
                            return False
                        self.state[row][column] = self.state[row][column - 1]
                        self.state[row][column - 1] = 0
                        
                        self.animating_piece_coordinate = [self.position[0] + (column - 1) * self.width / 3, self.position[1] + row * self.height/3]
                        self.animating_direction = (1, 0)
                        self.animating_piece = self.state[row][column]
                        self.isFinished()
                        return True

    def isFinished(self):
        counter = 1
        for row in range(3):
            for column in range(3):
                element = self.state[row][column]
                if element != counter:
                    self.game_won = False
                    return
                if counter == 8:
                    self.game_won = True
                    return
                
                counter += 1

    def draw(self):
        self.window.blit(self.textures['board'], self.position)
        for row in range(3):
            for column in range(3):
                element = self.state[row][column]
                if element == 0:
                    continue
                texture = self.textures[element]
                coordinate = (self.position[0] + column * self.width / 3, self.position[1] + row * self.height/3)
                self.window.blit(texture, coordinate)

    def animate(self):
        self.window.blit(self.textures['board'], self.position)
        for row in range(3):
            for column in range(3):
                element = self.state[row][column]
                if element == 0 or element == self.animating_piece:
                    continue
                texture = self.textures[self.state[row][column]]
                coordinate = (self.position[0] + column * self.width / 3, self.position[1] + row * self.height/3)
                self.window.blit(texture, coordinate)

        movement = self.width / 3 / self.animation_frames
        self.accumulated_movement += movement
        if self.accumulated_movement < self.width / 3:
            self.animating_piece_coordinate = [self.animating_piece_coordinate[0] + movement * self.animating_direction[0], 
                                               self.animating_piece_coordinate[1] + movement * self.animating_direction[1]]
            self.window.blit(self.textures[self.animating_piece], self.animating_piece_coordinate)
        else:
            self.draw()
            self.animating = False
        

    def displayEndCard(self):
        self.window.blit(self.finished_backgrond, self.position)
        self.window.blit(self.finished_msg, self.finished_msg_rect)
        self.window.blit(self.restart_msg, self.restart_msg_rect)

    def displayWonMessage(self):
        self.window.blit(self.finished_backgrond, self.position)
        self.window.blit(self.won_msg, self.won_msg_rect)
        self.window.blit(self.vs_restart_msg, self.vs_restart_msg_rect)

    def displayLostMessage(self):
        self.window.blit(self.finished_backgrond, self.position)
        self.window.blit(self.lost_msg, self.lost_msg_rect)
        self.window.blit(self.vs_restart_msg, self.vs_restart_msg_rect)

    def update(self, direction, animation_frames):
        if direction != None:
            if not self.animating:
                moved = self.move(direction)
                if not moved or animation_frames == 0:
                    self.draw()
                    return
                
                self.animating = True
                self.accumulated_movement = 0
                self.animation_frames = animation_frames

            self.animate()
        else:
            self.draw() if not self.animating else self.animate()