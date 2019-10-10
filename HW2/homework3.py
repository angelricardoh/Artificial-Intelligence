import os.path
from os import path
import copy
import math
from enum import Enum

def split(word):
    return list(word)

def terminal_test(s):
    if s == s0:
        return False

    if ((s['0,0'] != '.' and s['0,1'] != '.' and s['0,2'] != '.' and s['0,3'] != '.' and s['0,4'] != '.' and
         s['1,0'] != '.' and s['1,1'] != '.' and s['1,2'] != '.' and s['1,3'] != '.' and s['1,4'] != '.' and
         s['2,0'] != '.' and s['2,1'] != '.' and s['2,2'] != '.' and s['2,3'] != '.' and
         s['3,0'] != '.' and s['3,1'] != '.' and s['3,2'] and
         s['4,0'] != '.' and s['4,1'] != '.') or
            (s['14,11'] != '.' and s['15,11'] != '.' and
             s['13,12'] != '.' and s['14,12'] != '.' and s['15,12'] != '.' and
             s['12,13'] != '.' and s['13,13'] != '.' and s['14,13'] != '.' and s['15,13'] != '.' and
             s['11,14'] != '.' and s['12,14'] != '.' and s['13,14'] != '.' and s['14,14'] != '.' and s[
                 '15,14'] != '.' and
             s['11,15'] != '.' and s['12,15'] != '.' and s['13,15'] != '.' and s['14,15'] != '.' and s[
                 '15,15'] != '.')):
        return True
    return False

class Player(Enum):
    MAX = 0
    MIN = 1

player = Player.MAX

def player(s):
    return player

class ActionType(Enum):
    E = 0
    J = 1

class Action():
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

def actions(s):

    actions = []

    # Iterate over pieces vs board
    for key in pieces_dict:
        piece_pos_elements = key.split(',')
        x = int(piece_pos_elements[0])
        y = int(piece_pos_elements[1])

        empty_space_array_check = [str(x-1) + ',' + str(y-1), str(x-1) + ',' + str(y), str(x-1) + ',' + str(y+1),
                                   str(x) + ',' + str(y-1), str(x) + ',' + str(y+1), str(x+1) + ',' + str(y-1),
                                   str(x+1) + ',' + str(y), str(x+1) + ',' + str(y+1)]
        for empty_space_pos in empty_space_array_check:
            if s.get(empty_space_pos) and s[empty_space_pos] == '.':
                action = Action(ActionType.E, [empty_space_pos], key)
                actions.append(action)

        # Check possible jumps
        jumps_queue = []
        start_search = True
        current_action = Action(ActionType.J, [], key)

        while jumps_queue or start_search:
            if not start_search:
                current_action = jumps_queue.pop()
                actions.append(current_action)

            print(len(current_action.moves))
            if current_action.moves:
                print("piece_pos_elements = " + current_action.moves[len(current_action.moves)-1])
                piece_pos_elements = current_action.moves[len(current_action.moves)-1].split(',') # last index
                x = int(piece_pos_elements[0])
                y = int(piece_pos_elements[1])

            start_search = False

            possible_pieces_pos_array = [str(x-1) + ',' + str(y-1),
                                         str(x-1) + ',' + str(y),
                                         str(x-1) + ',' + str(y+1),
                                         str(x) + ',' + str(y-1),
                                         str(x) + ',' + str(y+1),
                                         str(x+1) + ',' + str(y-1),
                                         str(x+1) + ',' + str(y),
                                         str(x+1) + ',' + str(y+1)] # type: Action
            possible_jump_pos_array = [str(x-2) + ',' + str(y-2),
                                       str(x-2) + ',' + str(y),
                                       str(x-2) + ',' + str(y+2),
                                       str(x) + ',' + str(y-2),
                                       str(x) + ',' + str(y+2),
                                       str(x+2) + ',' + str(y-2),
                                       str(x+2) + ',' + str(y),
                                       str(x+2) + ',' + str(y+2)] # type: Action

            for i in range(0, len(possible_pieces_pos_array)):
                possible_piece_pos = possible_pieces_pos_array[i]
                possible_jump_pos = possible_jump_pos_array[i]
                print(str(x) + " " + str(y))
                print(current_action.description())
                print(possible_piece_pos)
                print(possible_jump_pos)
                if s.get(possible_piece_pos) and s.get(possible_jump_pos) and s[possible_piece_pos] != '.' and s[possible_jump_pos] == '.':
                    if possible_jump_pos not in current_action.moves and possible_jump_pos != current_action.original_pos:
                        print("entered")
                        # maybe I need to do a copy of current_action
                        new_action = Action(current_action.action_type, current_action.moves.copy(), current_action.original_pos)
                        new_action.moves.append(possible_jump_pos)
                        jumps_queue.append(new_action)

        for action in jumps_queue:
            actions.append(action)
    return actions


# Input processing

input_f = open("input.txt", "r")
game = input_f.readline().rstrip()
color = input_f.readline().rstrip()
time = float(input_f.readline().rstrip())
print(game)
print(color)
print(time)

# Bidimensional array or dictionary
board_lines = input_f.readlines()
board_size = 16
board_graph = [[0 for x in range(board_size)] for y in range(board_size)]
board = [[0 for x in range(board_size)] for y in range(board_size)]
input_f.close()

board_dict = {}
pieces_dict = {}

i = 0
for line in board_lines:
    board_graph[i] = list(line.rstrip())
    print(board_graph[i])
    i+=1

for i in range(0, board_size):
    for j in range(0, board_size):
        pos = pos = str(i) + ',' + str(j)
        board_dict[pos] = board_graph[j][i]
        if board_graph[j][i] != '.':
            pieces_dict[pos] = board_graph[j][i]


#for item in pieces_dict.items():
#    print(item)

s0 = board_dict.copy()
print(board_dict['1,5'])
actions = actions(s0)
print(len(actions))
for item in actions:
    if item.action_type == ActionType.J:
        print(item.description())

#print(terminal_test(board_dict))


# print(len(board))
# first_line = board
# print(len(first_line))
#
# for x in range(0, board_size):
#     print(list(board[x]))
#     for y in range(0, board_size):
#         pos = str(x) + ',' + str(y)
#         # print(str(x) + " " + str(y))
#         print(chr(board[y][x]))
#         board_graph[y][x] = board[y][x]
# print(board_graph)

# Search


# Output processing
