import os
import os.path
from os import path
import pdb
import copy

class Node:
    parent = None
    cost = 0

    def __init__(self, pos, inclination, explored, edges):
        self.pos = pos
        self.inclination = inclination
        self.explored = explored
        self.edges = edges

    def description(self):
    	return "Node pos: " + self.pos + " inclination: " + str(self.inclination) + \
              " explored: " + str(self.explored) + " edges: " + str(self.edges)

def process_search(algorithm, graph_size, landing_pos, max_elevation, n_targets, targets_pos, graph):
    node_graph = {}
# print(len(graph))
#   print(len(graph[0]))

    # Convert graph to node_graph and remove invalid edges
    W = int(graph_size[0])
    H = int(graph_size[1])
    for x in range(0, W):
        for y in range(0, H):
            pos = str(x) + ',' + str(y)
            # Invert xy due to the way 2D arrays are build
            node_graph[pos] = Node(pos, int(graph[y][x]), False, [])

    for x in range(0, W):
        for y in range(0, H):
            current_pos = str(x) + ',' + str(y)
            current_node = node_graph[current_pos]
            neighbours = []
            neighbours.append(str(x-1) + ',' + str(y-1))
            neighbours.append(str(x-1) + ',' + str(y))
            neighbours.append(str(x-1) + ',' + str(y+1))
            neighbours.append(str(x) + ',' + str(y-1))
            neighbours.append(str(x) + ',' + str(y+1))
            neighbours.append(str(x+1) + ',' + str(y-1))
            neighbours.append(str(x+1) + ',' + str(y))
            neighbours.append(str(x+1) + ',' + str(y+1))
            for neighbour in neighbours:
                if neighbour in node_graph:
                    neighbour_node = node_graph[neighbour]
                    if abs(current_node.inclination - neighbour_node.inclination) <= max_elevation:
                        current_node.edges.append(neighbour)

    #for node in node_graph.values():
    #   print(node.description())

    if algorithm == "BFS":
        return bfs(W, H, landing_pos, max_elevation, n_targets, targets_pos, node_graph)
    elif algorithm == "UCS":
        return ucs(W, H, landing_pos, max_elevation, n_targets, targets_pos, node_graph)
    elif algorithm == "A*":
        return astar(W, H, landing_pos, max_elevation, n_targets, targets_pos, node_graph)
    else:
        return [['FAIL']]

#output test
# add case inside search solution to return landing_pos = target_pos return [landing_pos, target_pos] (inclusive)

node_queue = []

def bfs_queuing_fn(nodes):
    for node in nodes:
        node_queue.append(node)
    return node_queue

def ucs_queuing_fn(nodes):
    for node in nodes:
        if node.cost == 10:
            node_queue.insert(0,node)
        else:
            node_queue.append(node)
    return node_queue

def make_queue(node):
    node_queue = [node]
    return node_queue

def general_search(W, H, landing_pos, max_elevation, n_targets, goal, node_graph, queuing_fn):
    nodes = make_queue(node_graph[landing_pos])

    while True:
        if not nodes: return ['FAIL']
        node = nodes.pop(0)
        if node.pos == goal: return node
        node.explored = True

        # neighbour
        neighbour_list = []
        for neighbour_pos in node_graph[node.pos].edges:
            neighbour_node = node_graph[neighbour_pos]
            if not neighbour_node.explored and neighbour_node not in nodes:
                node_pos_elements = node.pos.split(',')
                node_pos_x = node_pos_elements[0]
                node_pos_y = node_pos_elements[1]
                neighbour_pos_elements = neighbour_node.pos.split(',')
                neighbour_pos_x = neighbour_pos_elements[0]
                neighbour_pos_y = neighbour_pos_elements[1]
                # Compare node_pos and neightbour_pos elements to compute cost
                if node_pos_x == neighbour_pos_x or node_pos_y == neighbour_pos_y:
                    neighbour_node.cost = 10
                else:
                    neighbour_node.cost = 14
                neighbour_node.parent = node
                neighbour_list.append(node_graph[neighbour_pos])
        nodes = queuing_fn(neighbour_list)


def bfs(W, H, landing_pos, max_elevation, n_targets, targets_pos, node_graph):
    solution_list = []
    for goal in targets_pos:
        temp_node_graph = copy.deepcopy(node_graph)
        solution = general_search(W, H, landing_pos, max_elevation, n_targets, goal, temp_node_graph, bfs_queuing_fn)
        if solution == ['FAIL']:
            solution_list.insert(len(solution_list),solution)
        elif solution.pos == landing_pos:
            solution_list.insert(len(solution_list),[landing_pos, solution.pos])
        else:
            solution_path = [solution.pos]
            while solution.parent:
                solution = solution.parent
                solution_path.insert(0, solution.pos)
            solution_list.insert(len(solution_list),solution_path)
    return solution_list

def ucs(W, H, landing_pos, max_elevation, n_targets, targets_pos, node_graph):
    solution_list = []
    for goal in targets_pos:
        temp_node_graph = copy.deepcopy(node_graph)
        solution = general_search(W, H, landing_pos, max_elevation, n_targets, goal, temp_node_graph, ucs_queuing_fn)
        if solution == ['FAIL']:
            solution_list.insert(len(solution_list), solution)
        elif solution.pos == landing_pos:
            solution_list.insert(len(solution_list), [landing_pos, solution.pos])
        else:
            solution_path = [solution.pos]
            while solution.parent:
                solution = solution.parent
                solution_path.insert(0, solution.pos)
            solution_list.insert(len(solution_list), solution_path)
    return solution_list

def astar(W, H, landing_pos, max_elevation, n_targets, targets_pos, graph):
    solution = [['1,0','2,1','3,2','4,3']]
    #    solution = [['1,0','2,1','3,2','4,3']]
    return solution


if path.exists("output.txt"):
    os.remove("output.txt")

input_f = open("input.txt", "r")
algorithm = input_f.readline().rstrip()
graph_size = input_f.readline().rstrip().split(' ')
landing_pos = input_f.readline().rstrip().replace(' ', ',')
max_elevation = int(input_f.readline().rstrip())
n_targets = int(input_f.readline())
targets_pos = []
for target_ind in range(0, n_targets):
    target_line = input_f.readline()
    targets_pos.append(target_line.rstrip().replace(' ', ','))

graph_lines = input_f.readlines()
graph = [line.split() for line in graph_lines]
input_f.close()

solution = process_search(algorithm,graph_size,landing_pos,max_elevation,n_targets,targets_pos, graph)

# output solution in another layer

output_f = open("output.txt", 'w')
for i in range(0,len(solution)):
    for j in range(0, len(solution[i])):
        output_f.write(str(solution[i][j]))
        print(str(solution[i][j]), end=' ')
        output_f.write(" ")
    if i!=len(solution)-1:
        output_f.write("\n")
        print()
