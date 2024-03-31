from __future__ import annotations
from datetime import datetime
from copy import deepcopy

### Represents a node within the graph
class Node():
    ## Constructor
    def __init__(self, id: str, xCoordinate: int, yCoordinate: int, altitude: float):
        self.id = id
        
        self.xCoordinate = xCoordinate
        self.yCoordinate = yCoordinate
        self.altitude = altitude
        self.edges = []
        
        self.gScore = float("inf") # Weight cost from start node to this node
        self.hScore = 0            # Heuristic
        self.fScore = float("inf") # gScore + hScore
        
        self.parentID = self.id # The ID of the "parent" of this node. The parent represents the node
                                # which comes before this node on a given A* path
                                
        self.isBuilding = False
    
    ## Turns this node into a building
    def makeBuilding(self) -> None:
        self.isBuilding = True
        
    ## Overrides less than or equal to
    def __le__(self, other):
        return self.fScore <= other.fScore
    
    ## Overrides less than
    def __lt__(self, other):
        return self.fScore < other.fScore
    
### Represents a BuildingNode within the graph
#class BuildingNode(Node):
#    ## Constructor
#    def __init__(self, id: str, xCoordinate: int, yCoordinate: int, altitude: float, name: str, address: str):
#        super().__init__(id, xCoordinate, yCoordinate, altitude)
#        self.name = name
#        self.address = address
#   
#    ## Returns whether or not this node is a building
#    def isBuilding(self) -> bool:
#       return True

### Represents an edge within the graph
class Edge():
    ## Constructor
    def __init__(self, id: str, weight: int, nodes: list[Node] = [], isStair: bool = False, isSteepTerrain: bool = False):
        # TODO: Decide how we'll estimate time of edge
        self.id = id
        self.weight = weight
        
        if len(nodes) > 2:
            raise Exception("Edge <" + id + "> is trying to connect " + len(nodes) + " nodes")
        
        self.isStair = isStair
        self.isSteepTerrain = isSteepTerrain
        self.nodes = nodes
        self.elevationChange = abs(nodes[0].altitude - nodes[1].altitude)
        
    # Given a node that this edge connects to, returns the other node that this edge connects to
    def getOtherNode(self, firstNode: Node) -> Node:
        # Ensure the given node is connected to this edge
        if firstNode in self.nodes:
            # Return the node that is not the given node
            for node in self.nodes:
                if node != firstNode:
                    return node
            # If we got here, then somehow the edge is linked to the same node twice
            raise Exception("Edge <" + self.id + "> connects node <" + firstNode.id + "> to itself.")
        else:
            raise Exception("Node <" + firstNode.id + "> is not linked to edge <" + self.id + ">")
               
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
    def __init__(self, width: int, height: int, copy: bool = False, nodesToCopy: list[list[Node]] = None):
        self.nodes: list[list[Node]] = [[]] # 2D list of nodes
        self.edges: list[Edge] = [] # List of edges
        self.width = width
        self.height = height
        
        # If this is requesting a copy, then copy all the nodes in nodesToCopy instead of initializing new ones
        if (copy):
            # [:] applies to all element in list, so make a list of copies of rows in self.nodes
            self.nodes = [row[:] for row in nodesToCopy]
            return
            
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
                    # Make all edges connecting row 9 to row 10, barring the middle one, stairs
                    if y == 9 and x != 9:
                        newVerticalEdge = Edge(str(edgesMade), 1, [self.nodes[y][x], self.nodes[y+1][x]], isStair = True, isSteepTerrain = False)
                        self.nodes[y][x].edges.append(newVerticalEdge)
                        self.nodes[y+1][x].edges.append(newVerticalEdge)
                        self.edges.append(newVerticalEdge)
                        edgesMade += 1
                    # Make all edges connecting row 14 to row 15, barring the rightmost one, steep terrain
                    elif y == 14 and x != 19:
                        newVerticalEdge = Edge(str(edgesMade), 1, [self.nodes[y][x], self.nodes[y+1][x]], isStair = False, isSteepTerrain = True)
                        self.nodes[y][x].edges.append(newVerticalEdge)
                        self.nodes[y+1][x].edges.append(newVerticalEdge)
                        self.edges.append(newVerticalEdge)
                        edgesMade += 1
                    # Make all other nodes neither steep terrain nor stairs
                    else:
                        newVerticalEdge = Edge(str(edgesMade), 1, [self.nodes[y][x], self.nodes[y+1][x]], isStair = False, isSteepTerrain = False)
                        self.nodes[y][x].edges.append(newVerticalEdge)
                        self.nodes[y+1][x].edges.append(newVerticalEdge)
                        self.edges.append(newVerticalEdge)
                        edgesMade += 1
                    
                # Connect current node to node to its right, if not at right edge of graph
                if x < width - 1:
                    newHorizontalEdge = Edge(str(edgesMade), 1, [self.nodes[y][x], self.nodes[y][x+1]], isStair = False, isSteepTerrain = False)
                    self.nodes[y][x].edges.append(newHorizontalEdge)
                    self.nodes[y][x+1].edges.append(newHorizontalEdge)
                    self.edges.append(newHorizontalEdge)
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
    
    ## Gets the edge with id "edgeID"
    def getEdgeFromID(self, edgeID: str):
        for edge in self.edges:
            if edge.id == edgeID:
                return edge
    
    ## Prints the graph to the console
    def printGraph(self, startNodeID: str = None, goalNodeID: str = None, pathEdgesIDs: list[str] = None):
        # Initialize pathNodes list
        pathNodeIDs: list[Node] = []
        
        # If list of edge IDs was passed, get the nodes that those edges connect
        if pathEdgesIDs != None:
            for edgeID in pathEdgesIDs:
                edge = self.getEdgeFromID(edgeID)
                
                for node in edge.nodes:
                    pathNodeIDs.append(node.id)
            # If there are no edges on the path, then the start node and goal node must be the same
            if len(pathEdgesIDs) == 0:
                print("Start node and goal node are the same!")
                
        
        # Iterate through graph, printing each node
        for y in range(self.height):
            for x in range(self.width):
                # Print node as S if start node
                if startNodeID == self.nodes[y][x].id:
                    print("S", end='')
                # Print node as G if goal node
                elif goalNodeID == self.nodes[y][x].id:
                    print("G", end='')
                # print node as B if building node
                elif self.nodes[y][x].isBuilding:
                    print("B", end='')
                # Print node as X if on path
                elif self.nodes[y][x].id in pathNodeIDs:
                    print("X", end='')
                # Print node as O if nothing special
                else:
                    print("O", end='')
                    
                # Add "--" to represent edge if not at end of row
                if x < self.width - 1:
                    print("-", end='')
                # Add newline if at end of row
                else:
                    print()
                    
        
    # Creates a deepcopy of this graph
    def getDeepCopy(self) -> Graph:
        return Graph(self.width, self.height, True, self.nodes)
        