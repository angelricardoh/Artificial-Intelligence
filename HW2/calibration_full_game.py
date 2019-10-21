import os.path
from os import path
from enum import Enum
from timeit import default_timer as timer
from homework3 import PlayerColor
from homework3 import Player
from homework3 import PlayerType
from homework3 import BOARD_SIZE
from homework3 import alpha_beta_search
from homework3 import result
from homework3 import printState
from homework3 import utility
from homework3 import terminal_test

# Global variables

MAX_DEPTH = 2
CURRENT_DEPTH = MAX_DEPTH
SINGLE_GAME = "SINGLE"


start = timer()
game = "GAME"

MAX_player = Player(PlayerColor.BLACK, PlayerType.MAX)
if MAX_player.color == PlayerColor.WHITE:
    MIN_player = Player(PlayerColor.BLACK, PlayerType.MIN)
else:
    MIN_player = Player(PlayerColor.WHITE, PlayerType.MIN)

# Bidimensional array or dictionary
board_lines = ['BBBBB...........\n',
               'BBBBB...........\n',
               'BBBB............\n',
               'BBB.............\n',
               'BB..............\n',
               '................\n',
               '................\n',
               '................\n',
               '................\n',
               '................\n',
               '..............WW\n',
               '.............WWW\n',
               '............WWWW\n',
               '...........WWWWW\n',
               '...........WWWWW']
board_graph = [[0 for x in range(BOARD_SIZE)] for y in range(BOARD_SIZE)]

board = [[0 for x in range(BOARD_SIZE)] for y in range(BOARD_SIZE)]

board_dict = {}
print(board_lines)

i = 0
for line in board_lines:
    board_graph[i] = list(line.rstrip())
    i += 1

for i in range(0, BOARD_SIZE):
    for j in range(0, BOARD_SIZE):
        pos = pos = str(i) + ',' + str(j)
        board_dict[pos] = board_graph[j][i]

# Test against similar agent
total_time_w = 0
total_time_b = 0
i = 0
while True:
    i += 1
    print("BLACK " + str(i))
    start_ind_b = timer()
    
    value_utility = utility(board_dict)
    print(value_utility)
    
    if value_utility <= -360 or value_utility >= -212:
        CURRENT_DEPTH = 1
    else:
        CURRENT_DEPTH = 1
    
    action_minimax = alpha_beta_search(board_dict)
    s1 = result(board_dict, action_minimax)
    printState(s1)
    
    end_ind_b = timer()
    total_time_b += end_ind_b - start_ind_b
    # if total_time_b > 310:
    #     break
    
    if terminal_test(s1):
        break
    print("total current iteration b " + str(end_ind_b - start_ind_b) + " seg")
    
    MAX_player = None
    MIN_player = None
    MAX_player = Player(PlayerColor.WHITE, PlayerType.MAX)
    MIN_player = Player(PlayerColor.BLACK, PlayerType.MIN)
    
    
    print("WHITE " + str(i))
    start_ind_w = timer()
    
    value_utility = utility(s1)
    print(value_utility)
    if value_utility <= -360 or value_utility >= -212:
        CURRENT_DEPTH = 1
    else:
        CURRENT_DEPTH = 1

    action_alphabeta = alpha_beta_search(s1)
    s2 = result(s1, action_alphabeta)
    printState(s2)
    board_dict = s2

    end_ind_w = timer()
    total_time_w += end_ind_w - start_ind_w
    # if total_time_w > 310:
    #     break
    if terminal_test(s1):
        break
    print("total current iteration w " + str(end_ind_w - start_ind_w) + " seg")
    
    MAX_player = None
    MIN_player = None
    MAX_player = Player(PlayerColor.BLACK, PlayerType.MAX)
    MIN_player = Player(PlayerColor.WHITE, PlayerType.MIN)

print("total time b " + str(total_time_b) + " seg")
print("total time w " + str(total_time_w) + " seg")


