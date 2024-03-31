from map_components import Graph
from map_components import Edge
from map_components import Node
from session_components import AStar

from mysql_connector import databaseCursor

import time

def main():
    # Get graph dimensions
    width = int(input("Enter graph width: "))
    height = int(input("Enter graph height: "))
    
    # Get start node coordinates
    startX = int(input("Enter x coordinate of start node (0 indexed): "))
    startY = int(input("Enter y coordinate of start node (0 indexed): "))
    
    # Get goal node coordinates
    goalX = int(input("Enter x coordinate of goal node (0 indexed): "))
    goalY = int(input("Enter y coordinate of goal node (0 indexed): "))
    
    # Create graph
    newGraph: Graph = Graph(width, height)
    
    # Get start node and goal node
    startNode: Node = newGraph.getNodeFromCoor(startY, startX)
    goalNode: Node = newGraph.getNodeFromCoor(goalY, goalX)
    
    # Get node IDs
    startNodeID = startNode.id
    goalNodeID = goalNode.id
    
    # Print graph
    newGraph.printGraph(startNodeID=startNodeID, goalNodeID=goalNodeID)
    
    # Set nodes to buildings, if desired
    while (True):
        userInput = input("Enter the x coordinate of a building node (zero indexed), or enter N to continue to pathfinding: ")
        
        # Read input
        if userInput == "N": # User wants to continue to pathfinding
            break
        else: # User wants to turn a node into a building
            newBuildingXCoordinate = int(userInput)
            userInput = input("Enter the y coordinate of a building node (zero indexed), or enter N to continue to pathfinding: ")
            # Read input
            if userInput == "N": # User wants to continue to pathfinding
                break
            else:  # User wants to turn a node into a building
                newBuildingYCoordinate = int(userInput)
                
                # Turn node at given coordinates into building
                newGraph.nodes[newBuildingYCoordinate][newBuildingXCoordinate].makeBuilding()
        
        # Print graph with new building node
        newGraph.printGraph(startNodeID=startNodeID, goalNodeID=goalNodeID)

    # Create AStar instance
    aStar = AStar()
    
    # Record time before route generation
    start_time = time.perf_counter()
    
    pathEdges: list[Edge] = aStar.generateRoutePath(newGraph, startNodeID, goalNodeID)
    
    # Record time taken to generate route
    pathGenerateTime = time.perf_counter() - start_time
    
    # Print the graph with the path
    newGraph.printGraph(startNodeID=startNodeID, goalNodeID=goalNodeID, pathEdges=pathEdges)
    
    # Print the time taken to generate the route
    print("--- %s seconds ---" % (pathGenerateTime))

main()