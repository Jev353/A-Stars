from map_components import Graph
import session_components 

def main():
    newGraph = Graph(5, 5)
    newGraph.printGraph()
    
    # Get start node coordinates
    startX = int(input("Enter x coordinate of start node: "))
    startY = int(input("Enter y coordinate of start node: "))
    
    # Get goal node coordinates
    goalX = int(input("Enter x coordinate of goal node: "))
    goalY = int(input("Enter y coordinate of goal node: "))
    
    # Get start node and goal node
    startNode = newGraph.getNodeFromCoor(startY, startX)
    goalNode = newGraph.getNodeFromCoor(goalY, goalX)
    
    # Get node IDs
    startNodeID = startNode.id
    goalNodeID = goalNode.id
    
    newGraph.printGraph(startNodeID=startNodeID, goalNodeID=goalNodeID)
    

main()