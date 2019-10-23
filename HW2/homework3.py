import os.path
from os import path
from enum import Enum
from timeit import default_timer as timer
import math

# Global variables

MAX_DEPTH = 2
CURRENT_DEPTH = MAX_DEPTH
BOARD_SIZE = 16
SINGLE_GAME = "SINGLE"
UTILITY_MIDDLE_POINT = -206
UTILITY_RANGE = 9
UTILITY_FIRST_THIRD_POINT = -258
UTILITY_SECOND_THIRD_POINT = -154

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
    heuristic_point = None

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
    pieces_in_camp = []

    if p.color == PlayerColor.WHITE:
        player_movable_pieces = [key for (key, value) in s.items() if value == 'W']
    else:
        player_movable_pieces = [key for (key, value) in s.items() if value == 'B']
    if p.color == PlayerColor.WHITE:
        player_movable_pieces.sort(reverse=False)

    for piece_location in player_movable_pieces:
        piece_pos_elements = piece_location.split(',')
        x = int(piece_pos_elements[0])
        y = int(piece_pos_elements[1])
        if p.color == PlayerColor.BLACK:
            if (x <= 4 and y == 0) or (x <= 4 and y <= 1) or (x <= 3 and y <= 2) or (x <= 2 and y <= 3) or (
                    x <= 1 and y <= 4):
                pieces_in_camp.append(piece_location)
        else:
            if (x >= 11 and y == 15) or (x >= 11 and y >= 14) or (x >= 12 and y >= 13) or (x >= 13 and y >= 12) or (
                    x >= 14 and y >= 11):
                pieces_in_camp.append(piece_location)

    # Only available pieces to move while their are in my camp
    valid_move_incamp = False
    if pieces_in_camp:
        for piece_location in pieces_in_camp:
            piece_pos_elements = piece_location.split(',')
            x = int(piece_pos_elements[0])
            y = int(piece_pos_elements[1])
            if p.color == PlayerColor.BLACK:
                if s[str(x + 1) + ',' + str(y)] == '.' or \
                        s[str(x + 1) + ',' + str(y + 1)] == '.' or s[str(x) + ',' + str(y + 1)] == '.':
                    valid_move_incamp = True
            else:
                if s[str(x - 1) + ',' + str(y)] == '.' or \
                        s[str(x - 1) + ',' + str(y - 1)] == '.' or s[str(x) + ',' + str(y - 1)] == '.':
                    valid_move_incamp = True
        if valid_move_incamp:
            player_movable_pieces = pieces_in_camp

    if game != SINGLE_GAME:
        # Remove pieces already in enemy corner
        if p.color == PlayerColor.WHITE:
            enemy_corner = ['0,0', '0,1', '1,0', '1,1', '0,2', '2,0', '2,1', '1,2', '0,3', '3,0', '2,2', '3,1', '1,3',
                            '4,0', '0,4', '3,2', '2,3', '1,4', '4,1']
        else:
            enemy_corner = ['15,15', '14,15', '15,14', '14,14', '13,15', '15,13', '13,14', '14,13', '12,15', '15,12',
                            '13,13', '12,14', '14,12', '11,15', '15,11', '12,13', '13,12', '11,14', '14,11']
        for i in range(0, len(enemy_corner) - 1):
            p.heuristic_point = enemy_corner[i]
            if enemy_corner[i] in player_movable_pieces:
                player_movable_pieces.remove(enemy_corner[i])
                p.heuristic_point = enemy_corner[i + 1]
            else:
                break

    # Iterate over pieces vs board
    for piece_location in player_movable_pieces:
        piece_pos_elements = piece_location.split(',')
        x = int(piece_pos_elements[0])
        y = int(piece_pos_elements[1])

        if piece_location in pieces_in_camp:
            if p.color == PlayerColor.WHITE:
                empty_space_array_check = [
                    str(x - 1) + ',' + str(y - 1),
                    str(x) + ',' + str(y - 1),
                    str(x - 1) + ',' + str(y)]
            else:
                empty_space_array_check = [
                    str(x + 1) + ',' + str(y + 1),
                    str(x) + ',' + str(y + 1),
                    str(x + 1) + ',' + str(y)]
        else:
            empty_space_array_check = [str(x - 1) + ',' + str(y + 1),
                                       str(x - 1) + ',' + str(y),
                                       str(x - 1) + ',' + str(y - 1),
                                       str(x) + ',' + str(y + 1),
                                       str(x) + ',' + str(y - 1),
                                       str(x + 1) + ',' + str(y - 1),
                                       str(x + 1) + ',' + str(y),
                                       str(x + 1) + ',' + str(y + 1)]

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

            if p.color == PlayerColor.WHITE:
                possible_pieces_pos_array = [str(x - 1) + ',' + str(y - 1),
                                             str(x - 1) + ',' + str(y),
                                             str(x - 1) + ',' + str(y + 1),
                                             str(x) + ',' + str(y - 1),
                                             str(x + 1) + ',' + str(y - 1)]
            else:
                possible_pieces_pos_array = [str(x - 1) + ',' + str(y + 1),
                                             str(x) + ',' + str(y + 1),
                                             str(x + 1) + ',' + str(y - 1),
                                             str(x + 1) + ',' + str(y),
                                             str(x + 1) + ',' + str(y + 1)]
            if p.color == PlayerColor.WHITE:
                possible_jump_pos_array = [str(x - 2) + ',' + str(y - 2),
                                           str(x - 2) + ',' + str(y),
                                           str(x - 2) + ',' + str(y + 2),
                                           str(x) + ',' + str(y - 2),
                                           str(x + 2) + ',' + str(y - 2)]
            else:
                possible_jump_pos_array = [str(x - 2) + ',' + str(y + 2),
                                           str(x) + ',' + str(y + 2),
                                           str(x + 2) + ',' + str(y - 2),
                                           str(x + 2) + ',' + str(y),
                                           str(x + 2) + ',' + str(y + 2)]

            for i in range(0, len(possible_pieces_pos_array)):
                possible_piece_pos = possible_pieces_pos_array[i]
                possible_jump_pos = possible_jump_pos_array[i]
                if s.get(possible_piece_pos) and s.get(possible_jump_pos) and s[possible_piece_pos] != '.' and s[
                    possible_jump_pos] == '.':
                    if possible_jump_pos not in current_action.moves and possible_jump_pos != current_action.original_pos:
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
    pieces_w = [key for (key, value) in s.items() if value == 'W']
    total_pieces = 0
    for piece in pieces_w:
        piece_pos_elements = piece.split(',')
        x = int(piece_pos_elements[0])
        y = int(piece_pos_elements[1])
        if (x <= 4 and y == 0) or (x <= 4 and y <= 1) or (x <= 3 and y <= 2) or (x <= 2 and y <= 3) or (
                x <= 1 and y <= 4):
            total_pieces += 1
    if total_pieces == 19:
        return True
    # pieces_b = [key for (key, value) in s.items() if value == 'B']
    # total_pieces = 0
    # for piece in pieces_b:
    #     piece_pos_elements = piece.split(',')
    #     x = int(piece_pos_elements[0])
    #     y = int(piece_pos_elements[1])
    #     if (x >= 11 and y == 15) or (x >= 11 and y >= 14) or (x >= 12 and y >= 13) or (x >= 13 and y >= 12) or (
    #             x >= 14 and y >= 11):
    #         total_pieces += 1
    # if total_pieces == 19:
    #     return True
    return False


def cutoff_test(d):
    if d == CURRENT_DEPTH:
        return True
    return False


def utility(s):
    if MAX_player.heuristic_point:
        heuristic_point_elements = MAX_player.heuristic_point.split(',')
        final_x = int(heuristic_point_elements[0])
        final_y = int(heuristic_point_elements[1])
    else:
        if MAX_player.color == PlayerColor.WHITE:
            final_x = 0
            final_y = 0
        else:
            final_x = BOARD_SIZE - 1
            final_y = BOARD_SIZE - 1

    if MAX_player.color == PlayerColor.WHITE:
        total_distance_w = 0
        pieces_w = [key for (key, value) in s.items() if value == 'W']
        pieces_w.sort(reverse=True)

        for piece in pieces_w:
            piece_pos_elements = piece.split(',')
            x = int(piece_pos_elements[0])
            y = int(piece_pos_elements[1])
            total_distance_w += math.sqrt(pow(final_x - x, 2) + pow(final_y - y, 2))
        return -total_distance_w
    else:
        total_distance_b = 0
        pieces_b = [key for (key, value) in s.items() if value == 'B']
        pieces_b.sort(reverse=True)

        for piece in pieces_b:
            piece_pos_elements = piece.split(',')
            x = int(piece_pos_elements[0])
            y = int(piece_pos_elements[1])
            total_distance_b += math.sqrt(pow(final_x - x, 2) + pow(final_y - y, 2))
        return -total_distance_b


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
        utility_value = min_value_minimax(result(state, action), 1)
        if utility_value > max_utility:
            max_utility = utility_value
            max_utility_action = action
    return max_utility_action


def max_value_minimax(state, d):
    if terminal_test(state) or cutoff_test(d):
        return utility(state)
    value = float("-inf")
    for action in actions(state, MAX_player):
        value = max(value, min_value_minimax(result(state, action), d + 1))
    return value


def min_value_minimax(state, d):
    if terminal_test(state) or cutoff_test(d):
        return utility(state)
    value = float("inf")
    for action in actions(state, MIN_player):
        value = min(value, max_value_minimax(result(state, action), d + 1))
    return value


# Alpha-beta
def alpha_beta_search(state):
    next_actions = []  # type: List[Action]
    max_action = None
    value = max_value(state, float("-inf"), float("inf"), 0, next_actions)
    for action in next_actions:
        if value == action.utility_value:
            if max_action:
                utility(result(state, action)) > utility(result(state, max_action))
                max_action = action
            else:
                max_action = action
    return max_action


def max_value(state, alpha, beta, depth, next_actions=None):
    if terminal_test(state) or cutoff_test(depth):
        return utility(state)
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
    if terminal_test(state) or cutoff_test(depth):
        return utility(state)
    value = float("inf")
    for action in actions(state, MIN_player):
        value = min(value, max_value(result(state, action), alpha, beta, depth + 1))
        if value <= alpha:
            return value
        beta = min(beta, value)
    return value


input_f = open("input.txt", "r")
game = input_f.readline().rstrip()
color = input_f.readline().rstrip()
time = float(input_f.readline().rstrip())

MAX_player = Player(PlayerColor[color], PlayerType.MAX)
if MAX_player.color == PlayerColor.WHITE:
    MIN_player = Player(PlayerColor.BLACK, PlayerType.MIN)
else:
    MIN_player = Player(PlayerColor.WHITE, PlayerType.MIN)

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


# Calibration

calibration_ratio = 0
if path.exists("calibration.txt"):
    input_c = open("calibration.txt", "r")
    calibration_string = input_c.readline().rstrip()
    if calibration_string != '':
        calibration_ratio = float(calibration_string)
    input_c.close()

# Utility calculation

value_utility = utility(board_dict)
utility_lower_bound = UTILITY_MIDDLE_POINT - UTILITY_RANGE
utility_upper_bound = UTILITY_MIDDLE_POINT + UTILITY_RANGE

# Depth designation

if game == SINGLE_GAME:
    CURRENT_DEPTH = 1
else:
    if calibration_ratio:
        utility_lower_bound = UTILITY_MIDDLE_POINT - (UTILITY_RANGE * calibration_ratio)
        utility_upper_bound = UTILITY_MIDDLE_POINT + (UTILITY_RANGE * calibration_ratio)
    if value_utility >= utility_lower_bound and value_utility <= utility_upper_bound:
        CURRENT_DEPTH = 3
    else:
        CURRENT_DEPTH = 2

# Output processing

action_alphabeta = alpha_beta_search(board_dict)

if path.exists("output.txt"):
    os.remove("output.txt")

output_f = open("output.txt", 'w')

if action_alphabeta:
    output_f.write(action_alphabeta.action_type.name + " " + action_alphabeta.original_pos + " " + action_alphabeta.moves[0])
    # print(action_alphabeta.action_type.name + " " + action_alphabeta.original_pos + " " + action_alphabeta.moves[0])
    if action_alphabeta.action_type.name == 'J':
        for i in range(0, len(action_alphabeta.moves) - 1):
            output_f.write('\n')
            # print(action_alphabeta.action_type.name + " " + action_alphabeta.moves[i] + " " + action_alphabeta.moves[i+1])
            output_f.write(action_alphabeta.action_type.name + " " + action_alphabeta.moves[i] + " " + action_alphabeta.moves[i+1])

output_f.close()

# printState(result(board_dict, action_alphabeta))

######################
# Tests              #
######################

# Test against similar agent x times

# print("utility_lower_bound = " + str(utility_lower_bound))
# print("utility_upper_bound = " + str(utility_upper_bound))
#
# total_time_player_two = 0
# total_time_player_one = 0
# i = 0
# longest_action = -1
# longest_state_performed = None
# while True:
#     i += 1
#     # print("Agent One iteration: " + str(i))
#     start_time_player_one = timer()
#
#     value_utility = utility(board_dict)
#     # print(value_utility)
#     if value_utility >= utility_lower_bound and value_utility <= utility_upper_bound:
#         print("depth 3")
#         CURRENT_DEPTH = 3
#     else:
#         CURRENT_DEPTH = 2
#
#     action_minimax = alpha_beta_search(board_dict)
#     s1 = result(board_dict, action_minimax)
#     # printState(s1)
#
#     end_time_player_one = timer()
#     total_time_player_one += end_time_player_one - start_time_player_one
#     if end_time_player_one - start_time_player_one > longest_action:
#         longest_action = total_time_player_one
#         longest_state_performed = board_dict
#     # print("total current iteration player one " + str(end_time_player_one - start_time_player_one) + " seg")
#     if total_time_player_one > 300:
#         break
#
#     if terminal_test(s1):
#         # printState(s1)
#         print("total of iterations " + str(i))
#         break
#
#     MAX_player = None
#     MIN_player = None
#     # MAX_player = Player(PlayerColor.WHITE, PlayerType.MAX)
#     # MIN_player = Player(PlayerColor.BLACK, PlayerType.MIN)
#     MAX_player = Player(PlayerColor.BLACK, PlayerType.MAX)
#     MIN_player = Player(PlayerColor.WHITE, PlayerType.MIN)
#
#     # print("Agent Two iteration: " + str(i))
#     start_time_player_two = timer()
#
#     value_utility = utility(s1)
#     # print(value_utility)
#     CURRENT_DEPTH = 2
#
#     action_alphabeta = alpha_beta_search(s1)
#     s2 = result(s1, action_alphabeta)
#
#     if terminal_test(s2):
#         # printState(s2)
#         print("total of iterations " + str(i))
#         break
#
#     # printState(s2)
#     board_dict = s2
#
#     end_time_player_two = timer()
#     total_time_player_two += end_time_player_two - start_time_player_two
#
#     # if terminal_test(s1):
#     #     break
#
#     # print("total current iteration player two " + str(end_time_player_two - start_time_player_two) + " seg")
#
#     MAX_player = None
#     MIN_player = None
#     # MAX_player = Player(PlayerColor.BLACK, PlayerType.MAX)
#     # MIN_player = Player(PlayerColor.WHITE, PlayerType.MIN)
#     MAX_player = Player(PlayerColor.WHITE, PlayerType.MAX)
#     MIN_player = Player(PlayerColor.BLACK, PlayerType.MIN)
# print("total play time player one " + str(total_time_player_one) + " seg")
# print("longest action = " + str(longest_action))
# print("longest state performed = ")
# printState(longest_state_performed)

# Test state

# printState(board_dict)
# print("----------------")
# print("Alphabeta")
# print("----------------")
# action_alphabeta = alpha_beta_search(board_dict)
# s1 = result(board_dict, action_alphabeta)
# printState(s1)
# end = timer()
# print(str(end - start) + " seg")

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
