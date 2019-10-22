import os.path
from os import path
from enum import Enum
from timeit import default_timer as timer
import math

MAX_DEPTH = 2
CURRENT_DEPTH = MAX_DEPTH
BOARD_SIZE = 16
SINGLE_GAME = "SINGLE"

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
         pieces_dict = [key for (key, value) in s.items() if value == 'W']
    else:
         pieces_dict = [key for (key, value) in s.items() if value == 'B']

    for piece_location in pieces_dict:
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
                if s[str(x + 1) + ',' + str(y)] == '.' or s[str(x + 1) + ',' + str(y + 1)] == '.' or s[str(x) + ',' + str(y + 1)] == '.':
                    valid_move_incamp = True
            else:
                if s[str(x - 1) + ',' + str(y)] == '.' or s[str(x - 1) + ',' + str(y - 1)] == '.' or s[str(x) + ',' + str(y - 1)] == '.':
                    valid_move_incamp = True
        if valid_move_incamp:
            pieces_dict = pieces_in_camp

    if game != SINGLE_GAME:
        # Remove pieces already in corner
        if p.color == PlayerColor.WHITE:
            p.heuristic_point = '0,0'
            if s['0,0'] == 'W':
                pieces_dict.remove('0,0')
                p.heuristic_point = '0,1'
                if s['0,1'] == 'W':
                    pieces_dict.remove('0,1')
                    p.heuristic_point = '1,0'
                    if s['1,0'] == 'W':
                        pieces_dict.remove('1,0')
                        p.heuristic_point = '1,1'
                        if s['1,1'] == 'W':
                            pieces_dict.remove('1,1')
                            p.heuristic_point = '0,2'
                            if s['0,2'] == 'W':
                                pieces_dict.remove('0,2')
                                p.heuristic_point = '2,0'
                                if s['2,0'] == 'W':
                                    pieces_dict.remove('2,0')
                                    p.heuristic_point = '2,1'
                                    if s['2,1'] == 'W':
                                        pieces_dict.remove('2,1')
                                        p.heuristic_point = '1,2'
                                        if s['1,2'] == 'W':
                                            pieces_dict.remove('1,2')
                                            p.heuristic_point = '0,3'
                                            if s['0,3'] == 'W':
                                                pieces_dict.remove('0,3')
                                                p.heuristic_point = '3,0'
                                                if s['3,0'] == 'W':
                                                    pieces_dict.remove('3,0')
                                                    p.heuristic_point = '2,2'
                                                    if s['2,2'] == 'W':
                                                        pieces_dict.remove('2,2')
                                                        p.heuristic_point = '3,1'
                                                        if s['3,1'] == 'W':
                                                            pieces_dict.remove('3,1')
                                                            p.heuristic_point = '1,3'
                                                            if s['1,3'] == 'W':
                                                                pieces_dict.remove('1,3')
                                                                p.heuristic_point = '4,0'
                                                                if s['4,0'] == 'W':
                                                                    pieces_dict.remove('4,0')
                                                                    p.heuristic_point = '0,4'
                                                                    if s['0,4'] == 'W':
                                                                        pieces_dict.remove('0,4')
                                                                        p.heuristic_point = '3,2'
                                                                        if s['3,2'] == 'W':
                                                                            pieces_dict.remove('3,2')
                                                                            p.heuristic_point = '2,3'
                                                                            if s['2,3'] == 'W':
                                                                                pieces_dict.remove('2,3')
                                                                                p.heuristic_point = '1,4'
                                                                                if s['1,4'] == 'W':
                                                                                    pieces_dict.remove('1,4')
                                                                                    p.heuristic_point = '4,1'

        else:
            p.heuristic_point = '15,15'
            if s['15,15'] == 'B':
                pieces_dict.remove('15,15')
                p.heuristic_point = '14,15'
                if s['14,15'] == 'B':
                    pieces_dict.remove('14,15')
                    p.heuristic_point = '14,15'
                    if s['15,14'] == 'B':
                        pieces_dict.remove('15,14')
                        p.heuristic_point = '14,14'
                        if s['14,14'] == 'B':
                            pieces_dict.remove('14,14')
                            p.heuristic_point = '13,15'
                            if s['13,15'] == 'B':
                                pieces_dict.remove('13,15')
                                p.heuristic_point = '15,13'
                                if s['15,13'] == 'B':
                                    pieces_dict.remove('15,13')
                                    p.heuristic_point = '13,14'
                                    if s['13,14'] == 'B':
                                        pieces_dict.remove('13,14')
                                        p.heuristic_point = '14,13'
                                        if s['14,13'] == 'B':
                                            pieces_dict.remove('14,13')
                                            p.heuristic_point = '12,15'
                                            if s['12,15'] == 'B':
                                                pieces_dict.remove('12,15')
                                                p.heuristic_point = '15,12'
                                                if s['15,12'] == 'B':
                                                    pieces_dict.remove('15,12')
                                                    p.heuristic_point = '13,13'
                                                    if s['13,13'] == 'B':
                                                        pieces_dict.remove('13,13')
                                                        p.heuristic_point = '12,14'
                                                        if s['12,14'] == 'B':
                                                            pieces_dict.remove('12,14')
                                                            p.heuristic_point = '14,12'
                                                            if s['14,12'] == 'B':
                                                                pieces_dict.remove('14,12')
                                                                p.heuristic_point = '11,15'
                                                                if s['11,15'] == 'B':
                                                                    pieces_dict.remove('11,15')
                                                                    p.heuristic_point = '15,11'
                                                                    if s['15,11'] == 'B':
                                                                        pieces_dict.remove('15,11')
                                                                        p.heuristic_point = '12,13'
                                                                        if s['12,13'] == 'B':
                                                                            pieces_dict.remove('12,13')
                                                                            p.heuristic_point = '13,12'
                                                                            if s['13,12'] == 'B':
                                                                                pieces_dict.remove('13,12')
                                                                                p.heuristic_point = '11,14'
                                                                                if s['11,14'] == 'B':
                                                                                    pieces_dict.remove('11,14')
                                                                                    p.heuristic_point = '14,11'

    # Iterate over pieces vs board
    for piece_location in pieces_dict:
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
            empty_space_array_check = [str(x - 1) + ',' + str(y - 1), str(x - 1) + ',' + str(y),
                                       str(x - 1) + ',' + str(y + 1),
                                       str(x) + ',' + str(y - 1), str(x) + ',' + str(y + 1),
                                       str(x + 1) + ',' + str(y - 1),
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
                                         str(x + 1) + ',' + str(y + 1)]  # type: [String]
            possible_jump_pos_array = [str(x - 2) + ',' + str(y - 2),
                                       str(x - 2) + ',' + str(y),
                                       str(x - 2) + ',' + str(y + 2),
                                       str(x) + ',' + str(y - 2),
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
    pieces_b = [key for (key, value) in s.items() if value == 'B']
    total_pieces = 0
    for piece in pieces_b:
        piece_pos_elements = piece.split(',')
        x = int(piece_pos_elements[0])
        y = int(piece_pos_elements[1])
        if (x >= 11 and y == 15) or (x >= 11 and y >= 14) or (x >= 12 and y >= 13) or (x >= 13 and y >= 12) or (
                x >= 14 and y >= 11):
            total_pieces += 1
    if total_pieces == 19:
        return True
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

        for piece in pieces_w:
            piece_pos_elements = piece.split(',')
            x = int(piece_pos_elements[0])
            y = int(piece_pos_elements[1])
            total_distance_w += math.sqrt(pow(final_x - x, 2) + pow(final_y - y, 2))
            # total_distance_w += abs(final_x - x) + abs(final_y - y)
        return -total_distance_w
    else:
        total_distance_b = 0
        pieces_b = [key for (key, value) in s.items() if value == 'B']

        for piece in pieces_b:
            piece_pos_elements = piece.split(',')
            x = int(piece_pos_elements[0])
            y = int(piece_pos_elements[1])
            total_distance_b += math.sqrt(pow(final_x - x, 2) + pow(final_y - y, 2))
            # total_distance_b += abs(final_x - x) + abs(final_y - y)
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


def max_value(state, alpha, beta, depth, next_actions = None):
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

start = timer()
game = "GAME"

MAX_player = Player(PlayerColor.BLACK, PlayerType.MAX)
if MAX_player.color == PlayerColor.WHITE:
    MIN_player = Player(PlayerColor.BLACK, PlayerType.MIN)
else:
    MIN_player = Player(PlayerColor.WHITE, PlayerType.MIN)

# Bidimensional array or dictionary
board_lines = ['....WW..........\n',
               '.....B..........\n',
               '..WW............\n',
               '...BB.B.........\n',
               'W.W.............\n',
               '..B.BBBB........\n',
               '.....B..........\n',
               '.....B..WW......\n',
               '.........B.B....\n',
               '.......W..W.....\n',
               '.........W.BBWW.\n',
               '..........WWW...\n',
               '.........W.W.BB.\n',
               '..........W.....\n',
               '..........B..B..\n',
               '................']
board_graph = [[0 for x in range(BOARD_SIZE)] for y in range(BOARD_SIZE)]

board = [[0 for x in range(BOARD_SIZE)] for y in range(BOARD_SIZE)]

board_dict = {}

i = 0
for line in board_lines:
    board_graph[i] = list(line.rstrip())
    i += 1

for i in range(0, BOARD_SIZE):
    for j in range(0, BOARD_SIZE):
        pos = pos = str(i) + ',' + str(j)
        board_dict[pos] = board_graph[j][i]

if path.exists("calibration.txt"):
     os.remove("calibration.txt")
output_f = open("calibration.txt", 'w')

CURRENT_DEPTH = 2

start_first_iter = timer()

action_alphabeta = alpha_beta_search(board_dict)

end_first_iter = timer()

start_second_iter = timer()

action_alphabeta = alpha_beta_search(board_dict)

end_second_iter = timer()

start_third_iter = timer()

action_alphabeta = alpha_beta_search(board_dict)

end_third_iter = timer()

average_time = ((end_first_iter - start_first_iter) + (end_second_iter - start_second_iter) + (end_third_iter - start_third_iter)) / 3
ratio = 45.47 / average_time

print(average_time)
print(ratio)

output_f.write(str(ratio) + "\n")
output_f.close()




