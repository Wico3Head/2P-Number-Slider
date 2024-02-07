import random
from setting import *

class Puzzle:
    def __init__(self, difficulty):
        self.game_won = False
        self.difficulty = difficulty

        self.state = [[0 for x in range(difficulty)] for y in range(difficulty)]
        current_number = 1
        for y in range(difficulty):
            for x in range(difficulty):
                if current_number == difficulty ** 2:
                    break
                self.state[y][x] = current_number
                current_number += 1

        for i in range(1000):
            self.move(random.choice(['up', 'down', 'left', 'right']))

    def move(self, direction):
        if not direction:
            return None, (None, None)
        
        for row in range(self.difficulty):
            for column in range(self.difficulty):
                element = self.state[row][column]
                if element == 0:
                    if direction == 'up':
                        if row == self.difficulty - 1:
                            return None, (None, None)
                        self.state[row][column] = self.state[row + 1][column]
                        self.state[row + 1][column] = 0
                        return 'up', (row, column)

                    elif direction == 'down':
                        if row == 0:
                            return None, (None, None)
                        self.state[row][column] = self.state[row - 1][column]
                        self.state[row - 1][column] = 0
                        return 'down', (row, column)

                    elif direction == 'left':
                        if column == self.difficulty - 1:
                            return None, (None, None)
                        self.state[row][column] = self.state[row][column + 1]
                        self.state[row][column + 1] = 0
                        return 'left', (row, column)

                    else: #right
                        if column == 0:
                            return None, (None, None)
                        self.state[row][column] = self.state[row][column - 1]
                        self.state[row][column - 1] = 0
                        return 'right', (row, column)

    def __str__(self):
        string = ""
        for row in self.state:
            for num in row:
                if num < 10:
                    string += f"{num}  "
                else:
                    string += f"{num} "
            string += "\n"
        return string

    def isSolved(self):
        counter = 1
        for row in range(self.difficulty):
            for column in range(self.difficulty):
                element = self.state[row][column]
                if element != counter:
                    self.game_won = False
                    return
                if counter == self.difficulty ** 2 - 1:
                    self.game_won = True
                    return
                
                counter += 1