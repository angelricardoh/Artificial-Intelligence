import os.path
from os import path
import copy
import math

# Input processing


input_f = open("input.txt", "r")
game = input_f.readline().rstrip()
color = input_f.readline().rstrip()
time = int(input_f.readline().rstrip())
# Bidimensional array or dictionary
while checkers_line = input_f.readline():
    targets_pos.append(checkers_line.rstrip().replace(' ', ','))

graph_lines = input_f.readlines()
graph = [line.split() for line in graph_lines]
input_f.close()

# Search

solution = process_search(algorithm,W,H,landing_pos,max_elevation,n_targets,targets_pos, graph)

# Output processing

if path.exists("output.txt"):
    os.remove("output.txt")

output_f = open("output.txt", 'w')
for i in range(0,len(solution)):
    for j in range(0, len(solution[i])):
        output_f.write(str(solution[i][j]))
        if j != len(solution[i]) - 1:
            output_f.write(" ")
        # print(str(solution[i][j]), end=' ')
    if i!=len(solution)-1:
        output_f.write("\n")
        # print()
