from map_components import Node
from map_components import Edge
from map_components import Schedule
from map_components import Graph

from queue import PriorityQueue

### Used to access and retrieve database information
class DatabaseAccessor():
    ## Constructor
    def __init__(self, accessKey: str):
        ## TODO: Login to database
        pass
    
    ##### NOTE: I have not added functions such as "getNodes" and "getEdges", as I believe
    ##### we should store that stuff on the webpage itself, perhaps via Json, since
    ##### otherwise we'll have to load an entire database table whenever we load the page
    
    ## Returns a list of user schedules
    def getUserSchedules(self, userID: str):
        ## TODO Something like: SELECT schedule FROM users WHERE id=userID
        pass
    
    ## Returns a list of routes within a given schedule
    def getRoutesInSchedule(self, scheduleID: str):
        ## TODO Something like: SELECT route FROM routes WHERE scheduleID=scheduleID
        pass
    
    ## Returns a bool indicating whether or not the given login information is valid
    def verifyLogin(self, username: str, password: str):
        ## TODO: Idk this is someone else's job
        pass

### Used to generate routes via A*
class AStar():
    ## Constructor
    def __init__(self):
        pass
    
    ## Returns a list of edges(?) which connect the startNode and endNode
    def generateRoutePath(self, graph: Graph, startNodeID: str, goalNodeID: str, avoidStairs: str=False, avoidSteepTerrain: str=False) -> list[Edge]:
        # Return empty list if goal is start 
        if startNodeID == goalNodeID:
            return []
        
        # Create a copy of the graph for use in finding path
        # (copy is needed so parent values get reset)
        self.copyGraph = graph.getDeepCopy()
        
        # Get nodes from nodeIDs
        startNode: Node = self.copyGraph.getNodeFromID(startNodeID)
        goalNode: Node = self.copyGraph.getNodeFromID(goalNodeID)
        
        # Initialize startNode
        startNode.gScore = 0.0
        startNode.hScore = self.heuristicFunction(startNode, goalNode)
        startNode.fScore = 0.0
        
        # Initialize list of visited nodes
        visitedNodes = []
        
        # Initialize queue of nodes to visit
        nodesToVisit: PriorityQueue = PriorityQueue()
        
        # Place the start node on the min queue
        nodesToVisit.put((0, startNode))
        
        # Go until there are no more nodes to visit
        while not nodesToVisit.empty():
            # Get node with lowest F score
            currentNode: Node = nodesToVisit.get()[1]
            
            # Mark currentNode as visited
            visitedNodes.append(currentNode)
            
            # Iterate through edges
            for edge in currentNode.edges:
                # Get neighbor that the current edge connects to
                neighbor: Node = edge.getOtherNode(currentNode)
                
                # Goal found!!!
                if neighbor == goalNode:
                    # Set the neighbor (goal)'s parent as the current node's id
                    neighbor.parentID = currentNode.id
    
                    # Get and return the final path
                    return self.getPathFromGoalNode(neighbor)
                # Goal not found, bulding found
                elif neighbor.isBuilding:
                    # Can't go through building, just ignore
                    continue
                # Goal not found, normal buliding found
                else:
                    # Calculate fScore for current path to neighbor
                    tempGScore: float = currentNode.gScore + edge.weight
                    tempHScore: float = self.heuristicFunction(neighbor, goalNode)
                    tempFScore: float = tempGScore + tempHScore
                    
                    # If neighbor has not been visited before OR our current pathing is faster
                    if neighbor.fScore == float("inf") or neighbor.fScore > tempFScore:
                        # Update neighbor scores and parent
                        neighbor.gScore = tempGScore
                        neighbor.hScore = tempHScore
                        neighbor.fScore = tempFScore
                        neighbor.parentID = currentNode.id
                        
                        nodesToVisit.put((neighbor.fScore, neighbor))
        
        # Path was not found
        print("Path not found")
        return
                    
    ## Returns the heuristic value of the given node for the path's goal node
    def heuristicFunction(self, node: Node, goalNode: Node) -> float:
        # Return Manhattan Distance
        return (abs(node.xCoordinate - goalNode.xCoordinate) + abs(node.yCoordinate - goalNode.yCoordinate))
                    
        # Return Euclidian Distance (likely better for final implementation, as others are best for grids)
        # return math.sqrt((node.xCoordinate - goalNode.xCoordinate)**2 + (node.yCoordinate - goalNode.yCoordinate)**2)
    
    ## Returns list of edges that form found path
    def getPathFromGoalNode(self, goalNode: Node):
        # Initialize edge list
        edges : list[Edge] = []
        
        # Initialize currentNode as goalNode
        currentNode : Node = goalNode
        
        # Go through chain of parents
        while currentNode.id != currentNode.parentID:
            # Get the edge that connects these two nodes
            for edge in currentNode.edges:
                if edge.getOtherNode(currentNode).id == currentNode.parentID:
                    # Add edge to list
                    edges.append(edge)
                    
                    # Update current node
                    currentNode = self.copyGraph.getNodeFromID(currentNode.parentID)
                    break
        
        # All edges have been added, since entire path has been traversed backwards
        return edges
                

### Represents a user
class User():
    ## Constructor
    def __init__(self, id: str, schedules: list[Schedule]):
        self.id = id
        self.schedules = schedules