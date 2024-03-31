from map_components import Graph
from map_components import Edge
from map_components import Node
from session_components import AStar
from session_components import User

from database_connector import databaseCursor
from database_connector import database        #TODO This might be slow.  Maybe we set a variable equal to dataBase cursor and another to dataBase

import time

def main():
    # Initialize active user object
    activeUser : User = loginMenu()
    # Get user decision
    print("1: Generate A* path")
    print("2: Create schedule")
    print("3: Load schedule")
    userInput = input("Enter menu option: ")
    
    if (userInput == "1"):
        while True:
            basicPathfindingMenu()
    elif (userInput == "2"):
        pass
    elif (userInput == "3"):
        pass
    else:
        print("Invalid input.")
        exit()

## Startup menu for logging in. Returns a User representing the logged in user
def loginMenu() -> User:
    # Prompt for login or register
    userInput = input("Enter L to login, and R to register: ").upper()
    
    # Register new user
    if userInput == "R":
        # Prompt for desired username
        userInput = input("Please enter new username: ")
        
        # Verify that username is not taken
        duplicateName = databaseCursor.execute("SELECT username FROM users WHERE username = %s;", (userInput,))
        if duplicateName:
            print("This username is taken, and I can't be bothered to make this a loop. Goodbye!")
            exit()
        # Enter user into database
        else:
            databaseCursor.execute("INSERT INTO users (username) VALUES (%s);", (userInput,))
            database.commit()
            print("Account Created!")
            return User(databaseCursor.lastrowid)
    # Login to existing account
    elif userInput == "L":
        # Prompt for username
        userInput = input("Please enter your username: ")
        
        # Verify that account exists
        databaseCursor.execute('SELECT userID FROM users WHERE username = %s;', (userInput,))
        userID = databaseCursor.fetchall()
        # Account found
        if userID:
            print("Account found!") 
            return User(userID[0][0])
        # Account not found
        else:
            print("Account not found. Crashing.")
            exit()
    # Neither input 'L' nor 'R'. Crash
    else:
        print("Invalid input. Crashing out of disrespect.")
        exit()

## Prompts for a graph, start and goal nodes, and building nodes, then displays a route
def basicPathfindingMenu() -> None:
    # Get start node coordinates
    startX = int(input("Enter x coordinate of start node (0 indexed, 20x20): "))
    startY = int(input("Enter y coordinate of start node (0 indexed, 20x20): "))
    
    # Get goal node coordinates
    goalX = int(input("Enter x coordinate of goal node (0 indexed, 20x20): "))
    goalY = int(input("Enter y coordinate of goal node (0 indexed, 20x20): "))
    
    # Create graph
    newGraph: Graph = Graph(20, 20)
    
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