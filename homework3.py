import os.path
from os import path
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

def process_search(algorithm, W, H, landing_pos, max_elevation, n_targets, targets_pos, graph):
    node_graph = {}

    # Convert graph to node_graph and remove invalid edges
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

    solution_list = []
    for goal in targets_pos:
        node_graph_copy = copy.deepcopy(node_graph)
        if algorithm == "BFS":
            solution = general_search(algorithm, goal, node_graph_copy, bfs_queuing_fn, max_elevation)
        elif algorithm == "UCS":
            solution = general_search(algorithm, goal, node_graph_copy, ucs_queuing_fn, max_elevation)
        elif algorithm == "A*":
            solution = general_search(algorithm, goal, node_graph_copy, ucs_queuing_fn, max_elevation)
        else:
            solution = ['FAIL']

        if solution == ['FAIL']:
            solution_list.insert(len(solution_list), solution)
        elif type(solution) == Node and solution.pos == landing_pos:
            solution_list.insert(len(solution_list), [landing_pos, solution.pos])
        else:
            solution_path = [solution.pos]
            while solution.parent:
                solution = solution.parent
                solution_path.insert(0, solution.pos)
            solution_list.insert(len(solution_list), solution_path)
    return solution_list

# Queue methods

def make_queue(queue, node):
    queue = [node]
    return queue

def bfs_queuing_fn(queue, nodes):
    for node in nodes:
        queue.append(node)
    return queue

def ucs_queuing_fn(queue, nodes):
    for x in nodes:
        queue.append(x)
    queue.sort(key=sortCost)
    # print("queuing")
    # for y in queue:
    #     print(y.pos)
    #     print(y.cost)
    return queue

def sortCost(e):
    return e.cost

# Search methods

def general_search(algorithm, goal, node_graph, queuing_fn, max_elevation):
    queue = []
    nodes = make_queue(queue, node_graph[landing_pos])

    while True:
        if not nodes: return ['FAIL']
        node = nodes.pop(0)
        # print("pop: " + str(node.pos) + " value:" + str(node.inclination))
        if node.pos == goal: return node
        node.explored = True

        neighbour_list = []
        for neighbour_pos in node_graph[node.pos].edges:
            neighbour_node = node_graph[neighbour_pos]
            if not neighbour_node.explored and neighbour_node not in nodes:
                if algorithm == "UCS":
                    neighbour_node.cost = cost_function(False, node, neighbour_node)
                elif algorithm == "A*":
                    neighbour_node.cost = cost_function(True, node, neighbour_node) \
                                          + heuristic_function(node, neighbour_node, goal, max_elevation)
                neighbour_node.parent = node
                neighbour_list.append(node_graph[neighbour_pos])
        nodes = queuing_fn(queue, neighbour_list)

def cost_function(astar, node, neighbour_node):
    total_cost = 0
    node_pos_elements = node.pos.split(',')
    node_pos_x = node_pos_elements[0]
    node_pos_y = node_pos_elements[1]
    neighbour_pos_elements = neighbour_node.pos.split(',')
    neighbour_pos_x = neighbour_pos_elements[0]
    neighbour_pos_y = neighbour_pos_elements[1]
    # Compare node_pos and neightbour_pos elements to compute cost
    if node_pos_x == neighbour_pos_x or node_pos_y == neighbour_pos_y:
        total_cost = 10
    else:
        total_cost = 14
    if astar:
        total_cost += abs(node.inclination - neighbour_node.inclination)
    return total_cost

inclination_cost = 4

def heuristic_function(node, neighbour_node, goal, max_elevation):
    neighbour_pos_elements = neighbour_node.pos.split(',')
    neighbour_pos_x = int(neighbour_pos_elements[0])
    neighbour_pos_y = int(neighbour_pos_elements[1])
    goal_pos_elements = goal.split(',')
    goal_pos_x = int(goal_pos_elements[0])
    goal_pos_y = int(goal_pos_elements[1])
    diffX = abs(neighbour_pos_x - goal_pos_x)
    diffY = abs(neighbour_pos_y - goal_pos_y)
    node_pos_elements = node.pos.split(',')
    node_pos_x = int(node_pos_elements[0])
    node_pos_y = int(node_pos_elements[1])
    if node_pos_x == neighbour_pos_x or node_pos_y == neighbour_pos_y:
        return (diffX + diffY) * (max_elevation + inclination_cost + 1)
    else:
        return (diffX + diffY) * (max_elevation + 1)

# Input processing

input_f = open("input.txt", "r")
algorithm = input_f.readline().rstrip()
graph_size = input_f.readline().rstrip().split(' ')
W = int(graph_size[0])
H = int(graph_size[1])
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