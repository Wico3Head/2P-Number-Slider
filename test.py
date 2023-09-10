import numpy
from simpliedGame import SimplifiedGame
from setting import *
from copy import deepcopy

def flatten_array(arr):
    flattened = []
    for item in arr:
        if isinstance(item, list):
            flattened.extend(flatten_array(item))
        else:
            flattened.append(item)
    return flattened  

visited_states = []

def getFutures(game, moves, move_left):
    visited_states.append(deepcopy(game.state))
    if move_left == 0:
        return game
    
    games = [SimplifiedGame(deepcopy(game.state), moves-move_left+1, 2 if moves - move_left == 0 else game.initial_direction, direction='left'),
             SimplifiedGame(deepcopy(game.state), moves-move_left+1, 3 if moves - move_left == 0 else game.initial_direction, direction='right'),
             SimplifiedGame(deepcopy(game.state), moves-move_left+1, 0 if moves - move_left == 0 else game.initial_direction, direction='up'),
             SimplifiedGame(deepcopy(game.state), moves-move_left+1, 1 if moves - move_left == 0 else game.initial_direction, direction='down')]
    
    return [getFutures(moved_game, moves, move_left-1) for moved_game in filter(lambda g: g.move_possible and g.state not in visited_states, games)]

def minimax(state, moves):
    global visited_states
    visited_states.clear()

    game = SimplifiedGame(state, 0, None)
    futures = flatten_array(getFutures(game, moves, moves))
    print(len(futures))
    best_game = game
    for future_game in futures:
        if future_game.game_won:
            if best_game.game_won:
                if best_game.move_done > future_game.move_done:
                    best_game = future_game
            else:
                best_game = future_game
        elif not best_game.game_won:
            if future_game.score > best_game.score:
                best_game = future_game

    return best_game.initial_direction

game_state = [[1, 2, 6],
              [3, 8, 4],
              [5, 0, 7]]

for i in range(100):
    if minimax(game_state, MOVES_LOOK_AHEAD) == None:
        print('what')