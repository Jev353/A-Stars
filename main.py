from map_components import Graph
from map_components import Edge
from map_components import Node
from session_components import AStar
import session_components 

def main():
    # Get graph dimensions
    width = int(input("Enter graph width: "))
    height = int(input("Enter graph height: "))
    
    newGraph = Graph(width, height)
    newGraph.printGraph()
    
    # Get start node coordinates
    startX = int(input("Enter x coordinate of start node (0 indexed): "))
    startY = int(input("Enter y coordinate of start node (0 indexed): "))
    
    # Get goal node coordinates
    goalX = int(input("Enter x coordinate of goal node (0 indexed): "))
    goalY = int(input("Enter y coordinate of goal node (0 indexed): "))
    
    # Get start node and goal node
    startNode: Node = newGraph.getNodeFromCoor(startY, startX)
    goalNode: Node = newGraph.getNodeFromCoor(goalY, goalX)
    
    # Get node IDs
    startNodeID = startNode.id
    goalNodeID = goalNode.id
    
    aStar = AStar()
    
    pathEdges: list[Edge] = aStar.generateRoutePath(newGraph, startNodeID, goalNodeID)
    
    newGraph.printGraph(startNodeID=startNodeID, goalNodeID=goalNodeID, pathEdges=pathEdges)
    

main()