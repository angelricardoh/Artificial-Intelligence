class Node:
    def __init__(self, pos, inclination, explored, edges):
        self.pos = pos
        self.inclination = inclination
        self.explored = explored
        self.edges = edges

    def description(self):
    	return "Node pos: " + self.pos + " inclination: " + str(self.inclination) + \
              " explored: " + str(self.explored) + " edges: " + str(self.edges)

node_queue = []

def make_queue(node):
    node_queue = [node]
    return node_queue

def bfs_queuing_fn(nodes):
    for node in nodes:
        node_queue.append(node)
    return node_queue

n1 = Node("0,0", 67, False, ["0,1", "1,0"])
n2 = Node("0,1", 68, False, ["0,0"])
n3 = Node("1,0", 69, False, ["0,0", "1,1"])
n4 = Node("1,1", 70, False, ["1,0"])

print("Creating queue")
nodes = make_queue(n1)
print(nodes.pop(0).description())
node_list = [n2,n3,n4]
print("Queuing more nodes")
nodes = bfs_queuing_fn(node_list)
print(nodes.pop(0).description())
print(nodes.pop(0).description())
print(nodes.pop(0).description())
