from setting import *
from copy import deepcopy
from puzzle import Puzzle

class Ai:
    def __init__(self, move_explored: int, difficulty: int) -> None:
        self.__move_explored = move_explored
        self.__difficulty = difficulty

    def getOptimalMove(self, current_board_state: list[list[int]]) -> str:
        visited_states = [deepcopy(current_board_state)]
        initial_puzzle = Puzzle(self.__difficulty, False)
        initial_puzzle.setState(deepcopy(current_board_state))
        futures = [[initial_puzzle, []]]
        move_left = self.__move_explored

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
                            previous_move = None if move_left == self.__move_explored else move_list[-1]
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
                        if new_puzzle.isSolved():
                            return direction if move_left == self.__move_explored else move_list[0]
                        
                        new_move_list = deepcopy(move_list)
                        new_move_list.append(direction)
                        new_futures.append([deepcopy(new_puzzle), new_move_list])

            futures = deepcopy(new_futures)
            for puzzle, move_list in new_futures:
                visited_states.append(deepcopy(puzzle.getState()))

            move_left -= 1
        
        best_score = -1
        optimal_move = None
        print(futures)
        for puzzle, move_list in futures:
            if puzzle.isSolved():
                return move_left[0]
            
            score = self.getScore(puzzle.getState())
            if score > best_score:
                best_score = score
                optimal_move = move_left[0]

        return optimal_move

    def getScore(self, current_board_state: list[list[int]]) -> int:
        current_num = 1
        score = 0
        for row in range(self.__difficulty):
            for column in range(self.__difficulty):
                if current_board_state[row][column] == current_num:
                    score += 1
                else:
                    return score
                current_num += 1