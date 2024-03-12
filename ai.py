from setting import *
from copy import deepcopy
from puzzle import Puzzle

class Ai:
    def __init__(self, move_explored: int, difficulty: int) -> None:
        # initialise attributes
        self.__move_explored = move_explored
        self.__difficulty = difficulty

    def getOptimalMove(self, current_board_state: list[list[int]], ai_prev_move: str) -> str:
        # manual checking whether the second and third layers are solved
        if self.__difficulty == 4:
            second_layer_solved = self.secondLayerSolved(current_board_state)
            third_layer_solved = self.thirdLayerSolved(current_board_state)

        # 4x4 Third layer solved strategy
        if self.__difficulty == 4:
            if third_layer_solved:
                flag = True
                current_num = 13
                zero_position = None
                for x in range(4):
                    num = current_board_state[3][x]
                    if num == current_num:
                        current_num += 1
                    elif num == 0:
                        zero_position = x
                    else:
                        flag = False

                if flag:
                    return ['left' for _ in range(3 - zero_position)]
                
                move_list = ['right' for _ in range(zero_position)]
                slide_third_layer_moves = ['down', 'left', 'left', 'left', 'up', 'right', 'right', 'right', 'down', 'left', 'left']
                unslide_third_layer_moves = [opposites[move] for move in slide_third_layer_moves]
                unslide_third_layer_moves.reverse()
                move_list += slide_third_layer_moves

                for x in range(4):
                    num = current_board_state[3][x]
                    if num != 0:
                        left_most_tile = num
                        break

                if left_most_tile == 14:
                    move_list += ['left', 'up', 'right', 'down']
                else:
                    move_list += ['up', 'left', 'down', 'right']

                move_list += unslide_third_layer_moves
                return move_list
        
        # normal strategy
        visited_states = [deepcopy(current_board_state)]
        initial_puzzle = Puzzle(self.__difficulty, False)
        initial_puzzle.setState(deepcopy(current_board_state))
        futures = [[initial_puzzle, []]]
        move_left = self.__move_explored

        # The 12-tile problem strategy
        if self.__difficulty == 4:
            if second_layer_solved:
                zero_position = None
                left_most_tile = None
                for x in range(4):
                    num = current_board_state[3][3 - x]
                    if num == 0:
                        zero_position = 3 - x
                    else:
                        left_most_tile = num

                if left_most_tile == 12 and zero_position:
                    move_list = ['right' for _ in range(zero_position)]
                    slide_third_layer_moves = ['down', 'left', 'left']
                    unslide_third_layer_moves = [opposites[move] for move in slide_third_layer_moves]
                    unslide_third_layer_moves.reverse()

                    move_list += slide_third_layer_moves
                    move_list += ['up', 'right', 'down', 'left', 'up', 'left', 'down', 'right', 'right', 'up', 'left', 'down']
                    move_list += unslide_third_layer_moves
                    return move_list

        # look ahead
        while move_left != 0:
            new_futures = []
            for puzzle, move_list in futures:
                directions = []
                game_state = puzzle.getState()

                flag = False
                for row in range(self.__difficulty):
                    if flag:
                        break
                    for column in range(self.__difficulty):
                        if game_state[row][column] == 0:
                            flag = True
                            previous_move = ai_prev_move if move_left == self.__move_explored else move_list[-1]
                            if row != self.__difficulty - 1 and previous_move != opposites['up']: 
                                directions.append('up')
                            
                            if row != 0 and previous_move != opposites["down"]:
                                directions.append('down')

                            if column != self.__difficulty - 1 and previous_move != opposites['left']:
                                directions.append('left')

                            if column != 0 and previous_move != opposites['right']:
                                directions.append('right')
                            break

                for direction in directions:
                    new_puzzle = deepcopy(puzzle)
                    new_puzzle.move(direction)
                    if new_puzzle.getState() not in visited_states:
                        new_move_list = deepcopy(move_list)
                        new_move_list.append(direction)
                        if self.__difficulty == 3:
                            if new_puzzle.isSolved():
                                return new_move_list
                        else:
                            if self.thirdLayerSolved(new_puzzle.getState()):
                                return new_move_list
                        
                        new_futures.append([deepcopy(new_puzzle), new_move_list])

            futures = deepcopy(new_futures)
            for puzzle, move_list in new_futures:
                visited_states.append(deepcopy(puzzle.getState()))

            move_left -= 1
        
        # check the best board state
        best_score = -1
        optimal_move_set = None
        for puzzle, move_list in futures:
            if self.__difficulty == 3:
                if puzzle.isSolved():
                    return move_list
            else:
                if self.thirdLayerSolved(puzzle.getState()):
                    return move_list
            
            score = self.getScore(puzzle.getState())
            if score > best_score:
                best_score = score
                optimal_move_set = deepcopy(move_list)

        return optimal_move_set
    
    # check that the second layer of the puzzle is solved
    def secondLayerSolved(self, board: list[list[int]]) -> bool:
        counter = 1
        for row in range(self.__difficulty):
            for column in range(self.__difficulty):
                element = board[row][column]
                if element != counter:
                    return False
                if counter == self.__difficulty * 2:
                    return True
                
                counter += 1

    # check that the third layer of the puzzle is solved
    def thirdLayerSolved(self, board: list[list[int]]) -> bool:
        counter = 1
        for row in range(self.__difficulty):
            for column in range(self.__difficulty):
                element = board[row][column]
                if element != counter:
                    return False
                if counter == self.__difficulty * 3:
                    return True
                
                counter += 1

    # evaluate how good a board state is
    def getScore(self, current_board_state: list[list[int]]) -> float:
        current_num = 1
        score = 0
        for row in range(self.__difficulty):
            for column in range(self.__difficulty):
                if current_board_state[row][column] == current_num:
                    score += 1
                else:
                    for y in range(self.__difficulty):
                        for x in range(self.__difficulty):
                            num = current_board_state[y][x]
                            if num == current_num:
                                score += 0.75 * (2 * (self.__difficulty - 1) - abs(row - y) - abs(column - x))/ (2 * (self.__difficulty - 1))
                            elif num == 0:
                                score += 0.25 * (2 * (self.__difficulty - 1) - abs(row - y) - abs(column - x))/ (2 * (self.__difficulty - 1))
                    return score

                current_num += 1