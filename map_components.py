from __future__ import annotations
from copy import deepcopy
import csv
import os

### Represents a node within the graph
class Node():
    ## Constructor
    def __init__(self, ID: str, xCoordinate: int, yCoordinate: int, altitude: float):
        self.ID = ID
        
        self.xCoordinate = xCoordinate
        self.yCoordinate = yCoordinate
        self.altitude = altitude
        self.edges = []
        
        self.gScore = float("inf") # Weight cost from start node to this node
        self.hScore = 0            # Heuristic
        self.fScore = float("inf") # gScore + hScore
        
        self.parentID = self.ID # The ID of the "parent" of this node. The parent represents the node
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
#    def __init__(self, ID: str, xCoordinate: int, yCoordinate: int, altitude: float, name: str, address: str):
#        super().__init__(ID, xCoordinate, yCoordinate, altitude)
#        self.name = name
#        self.address = address
#   
#    ## Returns whether or not this node is a building
#    def isBuilding(self) -> bool:
#       return True

### Represents an edge within the graph
class Edge():
    ## Constructor
    def __init__(self, ID: str, scheduleRouteID: str = "", weight: int = 1, nodes: list[Node] = [], isStair: bool = False, isSteepTerrain: bool = False):
        # TODO: Decide how we'll estimate time of edge
        self.ID = ID
        self.scheduleRouteID = scheduleRouteID
        self.weight = weight
        
        if len(nodes) > 2:
            raise Exception("Edge <" + ID + "> is trying to connect " + len(nodes) + " nodes")
        
        self.isStair = isStair
        self.isSteepTerrain = isSteepTerrain
        self.nodes = nodes
        
    # Given a node that this edge connects to, returns the other node that this edge connects to
    def getOtherNode(self, firstNode: Node) -> Node:
        # Ensure the given node is connected to this edge
        if firstNode in self.nodes:
            # Return the node that is not the given node
            for node in self.nodes:
                if node != firstNode:
                    return node
            # If we got here, then somehow the edge is linked to the same node twice
            raise Exception("Edge <" + self.ID + "> connects node <" + firstNode.ID + "> to itself.")
        else:
            raise Exception("Node <" + firstNode.ID + "> is not linked to edge <" + self.ID + ">")
                  
### Represents a graph
class Graph():
    ## Constructor
    def __init__(self, width: int, height: int, copy: bool = False, nodesToCopy: list[Node] = None, edgesToCopy: list[Edge] = None):
        self.nodes: list[Node] = [] # List of nodes
        self.edges: list[Edge] = [] # List of edges
        self.width = width
        self.height = height # TODO Delete in constructor header and here
        
        # If this is requesting a copy, then copy all the nodes in nodesToCopy instead of initializing new ones
        if (copy):
            # [:] applies to all element in list, so make a list of copies of rows in self.nodes
            self.nodes = nodesToCopy[:]
            self.edges = edgesToCopy[:]
            return
        
        # Open NodeData.csv
        with open("backend\\NodeData.csv", mode='r') as file:
            # Read all bytes from NodeData.csv
            nodeDataFile = csv.reader(file)
            
            # Iterate through all lines except the first (the first is just a header)
            for currentLine in nodeDataFile:
                # Skip the first line
                if (nodeDataFile.line_num == 1):
                    continue
                
                currentNodeID = currentLine[0]
                currentNodeX = currentLine[1]
                currentNodeY = currentLine[2]
                currentNodeElevation = currentLine[3]
                
                # Create a new node with the read information and add to this graph
                newNode = Node(currentNodeID, currentNodeX, currentNodeY, currentNodeElevation)
                self.nodes.append(newNode)
                
        
        # Initialize variables for edge construction
        edgesMade: int = 0
        
        # Read through the file again to connect the created nodes
        with open("backend\\NodeData.csv", mode='r') as file:
            # Read all bytes from NodeData.csv
            nodeDataFile = csv.reader(file)
            
            # Iterate through all lines except the first (the first is just a header)
            for currentLine in nodeDataFile:
                # Skip the first line
                if (nodeDataFile.line_num == 1):
                    continue
                
                # Get the Node that the CurrentLine is associated with
                currentNode: Node = self.getNodeFromID(currentLine[0])
                
                # Get the entries for connected nodes
                connectedNodes = currentLine[4:]
                
                # Iterate through the connected nodes
                for nodeID in connectedNodes:
                    # Skip empty characters and commas
                    if (nodeID == '' or nodeID == ","):
                        continue
                    
                    # Get the node to connect
                    otherNode: Node = self.getNodeFromID(nodeID)
                    
                    # Instantiate skip variable
                    skipThisID = False
                    
                    # Ensure the nodes aren't already connected
                    for edge in currentNode.edges:
                        if otherNode in edge.nodes:
                            skipThisID = True
                            break
                    
                    # If the nodes aren't connected already, then create an edge
                    if not skipThisID:
                        newEdge: Edge = Edge(str(edgesMade), nodes=[currentNode, otherNode])
                        
                        currentNode.edges.append(newEdge)
                        otherNode.edges.append(newEdge)
                        
                        self.edges.append(newEdge)
                        
                        edgesMade += 1
    
    ## Gets the node with ID "nodeID"
    def getNodeFromID(self, nodeID: str) -> Node:
        # Iterate through all nodes until node is found
        for node in self.nodes:
            if node.ID == nodeID:
                return node
                
        # If we've reached here, the node wasn't found. Return None
        return None
    
    ## Gets the edge with ID "edgeID"
    def getEdgeFromID(self, edgeID: str) -> Edge:
        for edge in self.edges:
            if edge.ID == edgeID:
                return edge
    
    ## Prints the graph to the console
    def printGraph(self, startNodeID: str = None, goalNodeID: str = None, pathEdgesIDs: list[str] = None) -> None:
        # Initialize pathNodes list
        pathNodeIDs: list[Node] = []
        
        # If list of edge IDs was passed, get the nodes that those edges connect
        if pathEdgesIDs != None:
            for edgeID in pathEdgesIDs:
                edge = self.getEdgeFromID(edgeID)
                
                for node in edge.nodes:
                    pathNodeIDs.append(node.ID)
            # If there are no edges on the path, then the start node and goal node must be the same
            if len(pathEdgesIDs) == 0:
                print("Start node and goal node are the same!")
                
        
        # Iterate through graph, printing each node
        for y in range(self.height):
            for x in range(self.width):
                # Print node as S if start node
                if startNodeID == self.nodes[y][x].ID:
                    print("S", end='')
                # Print node as G if goal node
                elif goalNodeID == self.nodes[y][x].ID:
                    print("G", end='')
                # print node as B if building node
                elif self.nodes[y][x].isBuilding:
                    print("B", end='')
                # Print node as X if on path
                elif self.nodes[y][x].ID in pathNodeIDs:
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
        return Graph(self.width, self.height, True, self.nodes, self.edges)
        