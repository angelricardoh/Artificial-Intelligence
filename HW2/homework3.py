import os.path
from os import path
import copy
from enum import Enum
import math
from timeit import default_timer as timer

# Global variables
MAX_DEPTH = 5
BOARD_SIZE = 16


def split(word):
    return list(word)


def Merge(dict1, dict2):
    res = {**dict1, **dict2}
    return res


class PlayerType(Enum):
    MAX = 0
    MIN = 1


class PlayerColor(Enum):
    WHITE = 0
    BLACK = 1


class Player():
    color = None
    playerType = None

    def __init__(self, color, playerType):
        self.color = color
        self.playerType = playerType


class ActionType(Enum):
    E = 0
    J = 1


class Action():
    utility_value = 0

    def __init__(self, action_type, moves, original_pos):
        self.action_type = action_type
        self.moves = moves
        self.original_pos = original_pos

    def description(self):
        description = "original pos: " + self.original_pos + " " + self.action_type.name + " "
        for move in self.moves:
            description += move + " "
        description = description[:-1]
        return description

def actions(s, p):
    actions = []
    # pieces_dict = [key for (key, value) in s.items() if value != '.']
    if p.color == PlayerColor.WHITE:
         pieces_dict = [key for (key, value) in s.items() if value == 'W']
    else:
         pieces_dict = [key for (key, value) in s.items() if value == 'B']

    # Iterate over pieces vs board
    for piece_location in pieces_dict:
        piece_pos_elements = piece_location.split(',')
        x = int(piece_pos_elements[0])
        y = int(piece_pos_elements[1])

        empty_space_array_check = [str(x - 1) + ',' + str(y - 1), str(x - 1) + ',' + str(y),
                                   str(x - 1) + ',' + str(y + 1),
                                   str(x) + ',' + str(y - 1), str(x) + ',' + str(y + 1), str(x + 1) + ',' + str(y - 1),
                                   str(x + 1) + ',' + str(y), str(x + 1) + ',' + str(y + 1)]
        for empty_space_pos in empty_space_array_check:
            if s.get(empty_space_pos) and s[empty_space_pos] == '.':
                action = Action(ActionType.E, [empty_space_pos], piece_location)
                actions.append(action)

        # Check possible jumps
        jumps_queue = []
        start_search = True
        current_action = Action(ActionType.J, [], piece_location)

        while jumps_queue or start_search:
            if not start_search:
                current_action = jumps_queue.pop()
                actions.append(current_action)

            if current_action.moves:
                # print("piece_pos_elements = " + current_action.moves[len(current_action.moves)-1])
                piece_pos_elements = current_action.moves[len(current_action.moves) - 1].split(',')  # last index
                x = int(piece_pos_elements[0])
                y = int(piece_pos_elements[1])

            start_search = False

            possible_pieces_pos_array = [str(x - 1) + ',' + str(y - 1),
                                         str(x - 1) + ',' + str(y),
                                         str(x - 1) + ',' + str(y + 1),
                                         str(x) + ',' + str(y - 1),
                                         str(x) + ',' + str(y + 1),
                                         str(x + 1) + ',' + str(y - 1),
                                         str(x + 1) + ',' + str(y),
                                         str(x + 1) + ',' + str(y + 1)]  # type: Action
            possible_jump_pos_array = [str(x - 2) + ',' + str(y - 2),
                                       str(x - 2) + ',' + str(y),
                                       str(x - 2) + ',' + str(y + 2),
                                       str(x) + ',' + str(y - 2),
                                       str(x) + ',' + str(y + 2),
                                       str(x + 2) + ',' + str(y - 2),
                                       str(x + 2) + ',' + str(y),
                                       str(x + 2) + ',' + str(y + 2)]  # type: Action

            for i in range(0, len(possible_pieces_pos_array)):
                possible_piece_pos = possible_pieces_pos_array[i]
                possible_jump_pos = possible_jump_pos_array[i]

                if s.get(possible_piece_pos) and s.get(possible_jump_pos) and s[possible_piece_pos] != '.' and s[
                    possible_jump_pos] == '.':
                    if possible_jump_pos not in current_action.moves and possible_jump_pos != current_action.original_pos:

                        # maybe I need to do a copy of current_action
                        new_action = Action(current_action.action_type, current_action.moves.copy(),
                                            current_action.original_pos)
                        new_action.moves.append(possible_jump_pos)
                        jumps_queue.append(new_action)

        for action in jumps_queue:
            actions.append(action)
    return actions


# a: Action
def result(s, a):
    new_state = s.copy()
    if a is None or not a.moves:
        return s
    original_pos = a.original_pos
    new_pos = a.moves[len(a.moves) - 1]
    new_state[new_pos] = new_state.pop(original_pos)
    new_state[original_pos] = '.'
    return new_state


def terminal_test(s):
    if ((s['0,0'] == 'W' and s['0,1'] == 'W' and s['0,2'] == 'W' and s['0,3'] == 'W' and s['0,4'] == 'W' and
         s['1,0'] == 'W' and s['1,1'] == 'W' and s['1,2'] == 'W' and s['1,3'] == 'W' and s['1,4'] == 'W' and
         s['2,0'] == 'W' and s['2,1'] == 'W' and s['2,2'] == 'W' and s['2,3'] == 'W' and
         s['3,0'] == 'W' and s['3,1'] == 'W' and s['3,2'] and
         s['4,0'] == 'W' and s['4,1'] == 'W') or
            (s['14,11'] == 'B' and s['15,11'] == 'B' and
             s['13,12'] == 'B' and s['14,12'] == 'B' and s['15,12'] == 'B' and
             s['12,13'] == 'B' and s['13,13'] == 'B' and s['14,13'] == 'B' and s['15,13'] == 'B' and
             s['11,14'] == 'B' and s['12,14'] == 'B' and s['13,14'] == 'B' and s['14,14'] == 'B' and s['15,14'] == 'B' and
             s['11,15'] == 'B' and s['12,15'] == 'B' and s['13,15'] == 'B' and s['14,15'] == 'B' and s['15,15'] == 'B')):
        return True
    return False


def cutoff_test(s, d):
    if d == MAX_DEPTH:
        return True
    return False


def utility(s, p):
    pieces_w = [key for (key, value) in s.items() if value == 'W']
    pieces_b = [key for (key, value) in s.items() if value == 'B']

    total_distance_w = 0
    total_distance_b = 0
    for piece in pieces_w:
        piece_pos_elements = piece.split(',')
        x = int(piece_pos_elements[0])
        y = int(piece_pos_elements[1])
    #    total_distance_w += math.sqrt(pow(x, 2) + pow(y, 2))
        total_distance_w += x + y
    for piece in pieces_b:
        piece_pos_elements = piece.split(',')
        x = int(piece_pos_elements[0])
        y = int(piece_pos_elements[1])
    #    total_distance_b += math.sqrt(pow(15 - x, 2) + pow(15 - y, 2))
        total_distance_b += abs(x - 15) + abs(y - 15)

    if p.color == PlayerColor.WHITE:
        return (1 / total_distance_w)  # - (1 / total_distance_b)
    else:
        return (1 / total_distance_b)  # - (1 / total_distance_w)


def printState(s):
    for i in range(0, BOARD_SIZE):
        for j in range(0, BOARD_SIZE):
            print(s[str(j) + "," + str(i)], end='')
        print()


# Minimax

def minimax_decision(state):
    max_utility = float("-inf")

    possible_actions = actions(state, MAX_player)
    for action in possible_actions:
        # utility_value = utility(result(state,action), MAX_player)

        utility_value = min_value_minimax(result(state, action), 1)
        if utility_value > max_utility:
            max_utility = utility_value
            max_utility_action = action
    return max_utility_action


def max_value_minimax(state, d):
    if terminal_test(state) or cutoff_test(state, d):
        return utility(state, MAX_player)
    value = float("-inf")
    for action in actions(state, MAX_player):
        value = max(value, min_value_minimax(result(state, action), d + 1))
    return value


def min_value_minimax(state, d):
    if terminal_test(state) or cutoff_test(state, d):
        return utility(state, MAX_player)
    value = float("inf")
    for action in actions(state, MIN_player):
        value = min(value, max_value_minimax(result(state, action), d + 1))
    return value


# Alpha-beta
def alpha_beta_search(state):
    next_actions = []
    value = max_value(state, float("-inf"), float("inf"), 0, next_actions)
    for action in next_actions:
        if value == action.utility_value:
            return action


def max_value(state, alpha, beta, depth, next_actions = None):
    if terminal_test(state) or cutoff_test(state, depth):
        return utility(state, MAX_player)
    value = float("-inf")

    for action in actions(state, MAX_player):
        utility_value = min_value(result(state, action), alpha, beta, depth + 1)

        value = max(value, utility_value)
        if depth == 0:
            action.utility_value = utility_value
            next_actions.append(action)
        if value >= beta:
            return value
        alpha = max(alpha, value)
    return value



def min_value(state, alpha, beta, depth):
    if terminal_test(state) or cutoff_test(state, depth):
        return utility(state, MAX_player)
    value = float("inf")
    for action in actions(state, MIN_player):
        value = min(value, max_value(result(state, action), alpha, beta, depth + 1))
        if value <= alpha:
            return value
        beta = min(beta, value)
    return value


start = timer()
input_f = open("input.txt", "r")
game = input_f.readline().rstrip()
color = input_f.readline().rstrip()
time = float(input_f.readline().rstrip())

MAX_player = Player(PlayerColor[color], PlayerType.MAX)
if MAX_player.color == PlayerColor.WHITE:
    MIN_player = Player(PlayerColor.BLACK, PlayerType.MIN)
else:
    MIN_player = Player(PlayerColor.WHITE, PlayerType.MIN)

# print(game)
# print(color)
# print(time)

# Bidimensional array or dictionary
board_lines = input_f.readlines()
board_graph = [[0 for x in range(BOARD_SIZE)] for y in range(BOARD_SIZE)]
board = [[0 for x in range(BOARD_SIZE)] for y in range(BOARD_SIZE)]
input_f.close()

board_dict = {}

i = 0
for line in board_lines:
    board_graph[i] = list(line.rstrip())
    i += 1

for i in range(0, BOARD_SIZE):
    for j in range(0, BOARD_SIZE):
        pos = pos = str(i) + ',' + str(j)
        board_dict[pos] = board_graph[j][i]

MAX_DEPTH = 3

# printState(board_dict)

# print("----------------")
# print("Minimax")
# print("----------------")
# action_minimax = minimax_decision(s0)
# s1 = result(s0, action_minimax)
# printState(s1)

# print("----------------")
# print("Alphabeta")
# print("----------------")
action_alphabeta = alpha_beta_search(board_dict)
s1 = result(board_dict, action_alphabeta)
# printState(s1)

end = timer()
print(str(end - start) + " seg")

# Output processing


# Tests

# Test available actions
# actions = actions(s0)
# Print available actions
# for item in actions:
#     if item.action_type == ActionType.J:
#         print(item.description())

# Test MAX_player utility
# print(utility(s0, MAX_player))

# Test result action
# print(actions[0])
# s1 = result(s0, actions[0])
# printState(s1)