import math
import tkinter as tk
from map_components import Node
from map_components import Edge
from map_components import Graph
from datetime import datetime

from queue import PriorityQueue

### Represents a route    
class Route():
    ## Constructor
    def __init__(self, startNodeID: str, endNodeID: str, avoidStairs: bool=False, avoidSteepTerrain: bool=False):
        ## TODO: This requires A*. We'll pass the startNodeID, endNodeID, and settings
        ## to A* which'll return a list of edges, which will become the self.edges var below
        # edges = AStar.generateRoutePath(startNodeID, endNodeID, avoidStairs, avoidSteepTerrain)
        pass
        
### Represents a route that is specifically saved to a schedule
class ScheduleRoute(Route):
    ## Constructor
    def __init__(self, ID: str, scheduleID: str, name: str, startTime: datetime, endTime: datetime, edges: list[Edge]):
        self.ID = ID
        self.scheduleID = scheduleID
        self.name = name
        self.startTime = startTime
        self.endTime = endTime
        self.edges = edges
        
### Represents a schedule
class Schedule():
    ## Constructor
    def __init__(self, ID: str, name: str, scheduleRoutes: list[ScheduleRoute]):
        self.ID = ID
        self.name = name
        self.scheduleRoutes = scheduleRoutes
        
    ## Adds the given ScheduleRoute to this Schedule's scheduleRoutes
    def addScheduleRoute(self, scheduleRoute: ScheduleRoute):
        self.scheduleRoutes.append(scheduleRoute)

### Used to generate routes via A*
class AStar():
    ## Constructor
    def __init__(self):
        pass
    
    ## Returns a list of edges which connect the startNode and endNode
    # avoidStairs: str = False, avoidSteepTerrain: str = False
    def generateRoutePath(self, graph: Graph, startNodeID: str, goalNodeID: str, avoidStairs: bool = False) -> list[str]:
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
            for currentEdge in currentNode.edges:
                # Go to next edge if currenteEdge is a stair and user wants to avoid stairs
                if currentEdge.isStair and avoidStairs:
                    continue
                # Go to next edge if currenteEdge is steep terrain and user wants to avoid steep terrain
                # if currentEdge.isSteepTerrain and avoidSteepTerrain:
                #     continue
                
                # Get neighbor that the current edge connects to
                neighbor: Node = currentEdge.getOtherNode(currentNode)
                
                # Goal found!!!
                if neighbor == goalNode:
                    # Set the neighbor (goal)'s parent as the current node's ID
                    neighbor.parentID = currentNode.ID
    
                    # Get and return the final path
                    return self.getPathFromGoalNode(neighbor)
                # Goal not found, bulding found
                elif neighbor.isBuilding:
                    # Can't go through building, just ignore
                    continue
                # Goal not found, normal buliding found
                else:
                    # Calculate fScore for current path to neighbor
                    tempGScore: float = currentNode.gScore + currentEdge.weight
                    # h score is set based on user selection, g and f will be different between each option
                    tempHScore: float = self.heuristics[choice.get()](startNode, goalNode)
                    # adds extra cost to the path if the user selects to avoid steepness
                    if choice.get() == "Easy Route":
                        elevation = abs(currentNode.altitude - neighbor.altitude)
                        tempGScore += elevation * 2
                    tempFScore: float = tempGScore + tempHScore
                    
                    # If neighbor has not been visited before OR our current pathing is faster
                    if neighbor.fScore == float("inf") or neighbor.fScore > tempFScore:
                        # Update neighbor scores and parent
                        neighbor.gScore = tempGScore
                        neighbor.hScore = tempHScore
                        neighbor.fScore = tempFScore
                        neighbor.parentID = currentNode.ID
                        
                        nodesToVisit.put((neighbor.fScore, neighbor))
        
        # Path was not found
        print("Path not found")
        return None
                    
    ## Returns the heuristic value of the given node for the path's goal node
    def heuristicFunction(self, node: Node, goalNode: Node) -> float:
        # Return Manhattan Distance
        # return (abs(node.xCoordinate - goalNode.xCoordinate) + abs(node.yCoordinate - goalNode.yCoordinate))
        # Return Euclidian Distance
        return math.sqrt((node.xCoordinate - goalNode.xCoordinate)**2 + (node.yCoordinate - goalNode.yCoordinate)**2)

    ## an extension of the heuristic function, giving the user the option to generate
    ## a path that's physically easier to travel, i.e., less rate of change in elevation
    def elevationHeuristic(self, node: Node, goalNode: Node) -> float:
        elevation = abs(node.altitude - goalNode.altitude)
        euclidean_distance = math.sqrt((node.xCoordinate - goalNode.xCoordinate) ** 2 + (node.yCoordinate - goalNode.yCoordinate) ** 2)
        return euclidean_distance + elevation * 2

    # table structure holding the two path generating heuristic options
    HEURISTIC = heuristicFunction
    heuristics = {"Standard Route": heuristicFunction, "Easy Route": elevationHeuristic}
    
    ## Returns list of edges that form found path
    def getPathFromGoalNode(self, goalNode: Node):
        # Initialize list of edge IDs
        edgeIDs : list[str] = []
        
        # Initialize currentNode as goalNode
        currentNode : Node = goalNode
        
        # Go through chain of parents
        while currentNode.ID != currentNode.parentID:
            # Get the edge that connects these two nodes
            for edge in currentNode.edges:
                if edge.getOtherNode(currentNode).ID == currentNode.parentID:
                    # Add edge ID to list
                    edgeIDs.append(edge.ID)
                    
                    # Update current node
                    currentNode = self.copyGraph.getNodeFromID(currentNode.parentID)
                    break
        
        # All edges have been added, since entire path has been traversed backwards
        return edgeIDs

# tkinter
# constructs a new window where the user is able to select a heuristic function
## ALERT: PROGRAM STOPS READING CODE AT THIS LINE
# not great style-wise, but it will work for now in testing
window = tk.Tk()
window.geometry("220x150")
window.title("Pathing Options")
choice = tk.StringVar(window)
pathing_options = [
    "Standard Route",
    "Easy Route",
]

choice_txt = tk.StringVar()
choice_label = tk.Label(window, textvariable=choice_txt)
choice_txt.set("Generation Type: ")
choice_label.pack()
# user selected function will be stored here, it defaults as standard, but user can change it
choice.set(pathing_options[0])

choice_select = tk.OptionMenu(window, choice, *pathing_options)
choice_select.pack()

def confirm_choice():
    window.destroy()


confirm_choice_button = tk.Button(window, text="Confirm Selection", command=confirm_choice)
confirm_choice_button.pack(side=tk.BOTTOM, pady=10)

window.mainloop()
                
### Represents a user
class User():
    ## Constructor
    def __init__(self, ID: str, schedules: list[Schedule] = None):
        self.ID = ID
        self.schedules = schedules