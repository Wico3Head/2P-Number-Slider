from math import sqrt

class SimplifiedGame:
    def __init__(self, state, move_done, initial_direction, direction=None):
        self.state = state
        self.move_possible = False
        self.move_done = move_done
        self.game_won = False
        self.score = 0
        self.initial_direction = initial_direction
        if direction != None:
            self.move(direction)

    def move(self, direction):
        for row in range(3):
            for column in range(3):
                element = self.state[row][column]
                if element == 0:
                    if direction == 'up':
                        if row == 2:
                            return
                        self.state[row][column] = self.state[row + 1][column]
                        self.state[row + 1][column] = 0
                        self.move_possible = True
                        if self.isFinished():
                            self.game_won = True
                        else:
                            self.evalScore()
                        return

                    elif direction == 'down':
                        if row == 0:
                            return
                        self.state[row][column] = self.state[row - 1][column]
                        self.state[row - 1][column] = 0
                        self.move_possible = True
                        if self.isFinished():
                            self.game_won = True
                        else:
                            self.evalScore()
                        return

                    elif direction == 'left':
                        if column == 2:
                            return
                        self.state[row][column] = self.state[row][column + 1]
                        self.state[row][column + 1] = 0
                        self.move_possible = True
                        if self.isFinished():
                            self.game_won = True
                        else:
                            self.evalScore()
                        return

                    else: #right
                        if column == 0:
                            return
                        self.state[row][column] = self.state[row][column - 1]
                        self.state[row][column - 1] = 0
                        self.move_possible = True
                        if self.isFinished():
                            self.game_won = True
                        else:
                            self.evalScore()
                        return

    def isFinished(self):
        counter = 1
        for row in range(3):
            for column in range(3):
                element = self.state[row][column]
                if element != counter:
                    return False
                if counter == 8:
                    return True
                
                counter += 1

    def evalScore(self):
        counter = 1
        flag = False
        for row in range(3):
            for col in range(3):
                if not flag:
                    if self.state[row][col] == counter:
                        self.score += 100
                    else:
                        flag = True

        end_position = ((0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1))
        for row in range(3):
            for col in range(3):
                element = self.state[row][col]
                if element >= counter and element != 0:
                    self.score += 1 / (sqrt((row - end_position[element - 1][0])**2 + (col - end_position[element - 1][1])**2) + 1) * 10