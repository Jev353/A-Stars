from __future__ import annotations
from datetime import datetime

### Represents a node within the graph
class Node():
    ## Constructor
    def __init__(self, id: str, xCoordinate: int, yCoordinate: int, altitude: float, edges: list[Edge] = []):
        self.id = id
        
        self.xCoordinate = xCoordinate
        self.yCoordinate = yCoordinate
        self.altitude = altitude
        self.edges = edges

    ## Returns whether or not this node is a building
    def isBuilding(self) -> bool:
        return isinstance(self, BuildingNode)
    
    def __str__(self):
        return "O"
    
### Represents a BuildingNode within the graph
class BuildingNode(Node):
    ## Constructor
    def __init__(self, id: str, xCoordinate: int, yCoordinate: int, altitude: float, edges: list[Edge], name: str, address: str):
        super().__init__(id, xCoordinate, yCoordinate, altitude, edges)
        self.name = name
        self.address = address
    
    ## Returns whether or not this node is a building
    def isBuilding(self) -> bool:
        super().isBuilding()

### Represents an edge within the graph
class Edge():
    ## Constructor
    def __init__(self, id: str, isStair: bool, nodes: list[Node] = []):
        # TODO: Decide how we'll estimate time of edge
        self.id = id
        
        if len(nodes) > 2:
            raise Exception("Edge <" + id + "> is trying to connect " + len(nodes) + " nodes")
        
        self.isStair = isStair
        self.nodes = nodes
        self.elevationChange = abs(nodes[0].altitude - nodes[1].altitude)
               
### Represents a route    
class Route():
    ## Constructor
    def __init__(self, startNodeID: str, endNodeID: str, avoidStairs: bool=False, avoidSteepTerrain: bool=False):
        ## TODO: This requires A*. We'll pass the startNodeID, endNodeID, and settings
        ## to A* and it'll return a list of nodes, which will be the route's "edges" var
        pass
        # edges = AStar.generateRoutePath(startNodeID, endNodeID, avoidStairs, avoidSteepTerrain)
        
### Represents a route that is specifically saved to a schedule
class ScheduleRoute(Route):
    ## Constructor
    def __init__(self, id: str, name: str, startTime: datetime, endTime: datetime, startNodeID: str, endNodeID: str, avoidStairs: bool=False, avoidSteepTerrain: bool=False):
        self.id = id
        
        ## TODO: This requires A*. We'll pass the startNodeID, endNodeID, and settings
        ## to A* and it'll return a list of nodes, which will be the route's "edges" var
        self.name = name
        self.startTime = startTime
        self.endTime = endTime
        # edges = AStar.generateRoutePath(startNodeID, endNodeID, avoidStairs, avoidSteepTerrain)
        
### Represents a schedule
class Schedule():
    ## Constructor
    def __init__(self, id: str, name: str, scheduleRoutes: list[ScheduleRoute]):
        self.id = id
        self.name = name
        self.scheduleRoutes = scheduleRoutes
        
    ## Adds the given ScheduleRoute to this Schedule's scheduleRoutes
    def addScheduleRoute(self, scheduleRoute: ScheduleRoute):
        self.scheduleRoutes.append(scheduleRoute)
        
### Represents a graph
class Graph():
    ## Constructor
    def __init__(self, width: int, height: int):
        self.nodes: list[list[Node]] = [[]] # 2D list of nodes
        self.width = width
        self.height = height
        
        # Initialize variables for node construction
        nodesMade: int = 0 # Used to increment node IDs
        
        # Iterate through nodes, placing a node at each index
        for y in range(height):
            for x in range(width):
                # Create new node
                newNode = Node(str(nodesMade), x, y, 0.0)
                
                # Add new node to list of nodes
                self.nodes[y].append(newNode)
                
                # Increment nodesMade counter
                nodesMade += 1
                
            self.nodes.append([])
        
        # Initialize variables for edge construction
        edgesMade: int = 0
        
        # Iterate through nodes and connect them all via edges
        for y in range(height):
            for x in range(width):
                # Connect current node to node below it, if not at bottom of graph
                if y < height - 1:
                    newVerticalEdge = Edge(str(edgesMade), False, [self.nodes[y][x], self.nodes[y+1][x]])
                    self.nodes[y][x].edges.append(newVerticalEdge)
                    self.nodes[y+1][x].edges.append(newVerticalEdge)
                    edgesMade += 1
                    
                # Connect current node to node to its right, if not at right edge of graph
                if x < width - 1:
                    newHorizontalEdge = Edge(str(edgesMade), False, [self.nodes[y][x], self.nodes[y][x+1]])
                    self.nodes[y][x].edges.append(newHorizontalEdge)
                    self.nodes[y][x+1].edges.append(newHorizontalEdge)
                    edgesMade += 1
            
    ## Gets the node at (xCoor, yCoor)
    def getNodeFromCoor(self, yCoor: int, xCoor: int):
        return self.nodes[yCoor][xCoor]
    
    ## Gets the node with id "nodeID"
    def getNodeFromID(self, nodeID: str):
        # Iterate through all nodes until node is found
        for y in range(self.height):
            for x in range(self.width):
                if self.nodes[y][x].id == nodeID:
                    return self.nodes[y][x]
                
        # If we've reached here, the node wasn't found. Return None
        return None
    
    ## Prints the graph to the console
    def printGraph(self, startNodeID: str = None, goalNodeID: str = None):
        # Iterate through graph, printing each node
        for y in range(self.height):
            for x in range(self.width):
                # Add "--" to represent edge if not at end of row
                if x < self.width - 1:
                    # Print node as S if start node
                    if startNodeID == self.nodes[y][x].id:
                        print("S", end='-')
                    # Print node as G if goal node
                    elif goalNodeID == self.nodes[y][x].id:
                        print("G", end='-')
                    # Print node as O if nothing special
                    else:
                        print("O", end='-')
                # Add newline if at end of row
                else:
                    # Print node as S if start node
                    if startNodeID == self.nodes[y][x].id:
                        print("S")
                    # Print node as G if goal node
                    elif goalNodeID == self.nodes[y][x].id:
                        print("G")
                    # Print node as O if nothing special
                    else:
                        print("O")