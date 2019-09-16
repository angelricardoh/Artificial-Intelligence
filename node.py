class Node:
    def __init__(self, pos, inclination, explored, arcs):
        self.pos = pos
        self.inclination = inclination
        self.explored = explored
        self.arcs = arcs

    def description(self):
    	return "Node pos: " + self.pos + " inclination: " + str(self.inclination) + \
              " explored: " + str(self.explored) + " arcs: " + str(self.arcs)

n1 = Node("0,0", 67, False, ["0,1", "1,0"])
n2 = Node("0,1", 68, False, ["0,0"])
n3 = Node("1,0", 69, False, ["0,0", "1,1"])
n4 = Node("1,1", 70, False, ["1,0"])

thisdict = {}
thisdict["0,0"] = n1
thisdict["0,1"] = n2
thisdict["1,0"] = n3
thisdict["1,1"] = n4

print(len(thisdict))

print(thisdict.has_key("2,2"))

for x in thisdict.values():
    print(x.description())

print(thisdict["0,0"].description())

for y in thisdict.keys():
    print(y)
