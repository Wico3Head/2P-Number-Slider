from ai import Ai

ai = Ai(10, 3)
state = [[1, 2, 3],
         [4, 0, 6],
         [7, 5, 8]]

print(ai.getOptimalMove(state))