### Represents a node within the graph
class Node():
    ## Constructor
    def __init__(self, id, xCoordinate, yCoordinate, altitude, edges):
        self.id = id
        self.xCoordinate = xCoordinate
        self.yCoordinate = yCoordinate
        self.altitude = altitude
        self.edges = edges

    ## Returns whether or not this node is a building
    def isBuilding(self):
        return isinstance(self, BuildingNode)
    
### Represents a BuildingNode within the graph
class BuildingNode(Node):
    ## Constructor
    def __init__(self, id, xCoordinate, yCoordinate, altitude, edges, name, address):
        super().__init__(id, xCoordinate, yCoordinate, altitude, edges)
        self.name = name
        self.address = address
    
    ## Returns whether or not this node is a building
    def isBuilding(self):
        super().isBuilding()

### Represents an edge within the graph
class Edge():
    ## Constructor
    def __init__(self, isStair, nodes):
        # TODO: Decide how we'll estimate time of edge
        self.isStair = isStair
        self.nodes = nodes
        self.elevationChange = abs(nodes[0].altitude - nodes[1].altitude)