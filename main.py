from map_components import Edge
from map_components import Node
from map_components import Graph
from session_components import Route
from session_components import ScheduleRoute
from session_components import Schedule
from session_components import AStar
from session_components import User

from database_connector import *

import time
from math import atan2, degrees

import pygame
from assets import *

graph = Graph(20, 20)
aStar = AStar()
activeUser: User

# Initialize PyGame
pygame.init()

# Initialize screen
windowWidth: int = 2000
windowHeight: int = 828
screen = pygame.display.set_mode((windowWidth, windowHeight))

# Initialize storage for UI Nodes
clickableNodes: list[ClickableNode] = []

def main():
    # Displays the screen, including the Nodes
    resetScreen()
    
    # Initialize list of selected nodes
    selectedNodes: list[ClickableNode] = []
    routeDisplayed = False
    
    keepRunning = True
    while (keepRunning):
        # If 2 nodes have been selected, generate and display a route between them
        if (len(selectedNodes) == 2 and not routeDisplayed):
            generateAndDisplayRoute(selectedNodes[0], selectedNodes[1])
            routeDisplayed = True
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keepRunning = False
                
            # Handle node clicking
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Iterate through all nodes, checking which one was clicked
                for node in clickableNodes:
                    if node.clickRect.collidepoint(event.pos):
                        # If this is the third node clicked, then reset the route and selectedNodes
                        if (len(selectedNodes) >= 2):
                            selectedNodes.clear()
                            routeDisplayed = False
                            resetScreen()
                        
                        # Update the node's color to purple
                        pygame.draw.circle(node.surface, "purple", (node.radius, node.radius), node.radius)
                        
                        # Draw the new purple node to the screen
                        screen.blit(node.surface, 
                                   (node.x - node.surface.get_width()/2, 
                                    node.y - node.surface.get_height()/2))
                        
                        # Mark the node as selected
                        selectedNodes.append(node)
                        
                        # Don't check any more nodes
                        break
                
                # Update the screen
                pygame.display.update()
                        
    pygame.quit()
    
    # Initialize active user object
    global activeUser
    activeUser = loginMenu()
    
    mainMenu()

# Resets the screen to how it looked upon boot
def resetScreen(displayEdges: bool = False):
    # Copy the non-ADA to the screen
    screen.blit(mapNoADAImage, (0,0))
    
    # Display all nodes
    displayAllNodes()
    
    # Only display edges if requested
    if displayEdges:
        displayAllEdges()
        
    # Update the window
    pygame.display.update()

# Display a default visual representation of all nodes
def displayAllNodes():
    # Create a UI Node for each node in the graph
    for node in graph.nodes:
        newClickableNode = ClickableNode(node.ID, int(node.xCoordinate), int(node.yCoordinate))
        clickableNodes.append(newClickableNode)
        
        # Copy the new ClickableNode to the screen
        screen.blit(newClickableNode.surface, 
                    (newClickableNode.x - newClickableNode.surface.get_width()/2, 
                     newClickableNode.y - newClickableNode.surface.get_height()/2))
        
    # Update the window
    pygame.display.update()

# Display a visual representation of all edges
def displayAllEdges():
    # Draw lines representing edges for each node
    for edge in graph.edges:
        # Initialize leftmost and rightmost node variables
        leftmostNode: Node
        rightmostNode: Node
        
        # Get the leftmost node 
        if (int(edge.nodes[0].xCoordinate) <= int(edge.nodes[1].xCoordinate)):
            leftmostNode = edge.nodes[0]
            rightmostNode = edge.nodes[1]
        else:
            leftmostNode = edge.nodes[1]
            rightmostNode = edge.nodes[0]
        
        pygame.draw.line(screen, "green", 
                         (int(leftmostNode.xCoordinate), int(leftmostNode.yCoordinate)), 
                         (int(rightmostNode.xCoordinate), int(rightmostNode.yCoordinate)), 
                         3)        
    
    # Update the window
    pygame.display.update()

# Generates a route between the two nodes via AStar and displays it
def generateAndDisplayRoute(firstNode: ClickableNode, secondNode: ClickableNode):
    global graph
    
    # Get the backend nodes that the UI nodes represent
    backendFirstNode = graph.getNodeFromID(firstNode.ID)
    backendSecondNode = graph.getNodeFromID(secondNode.ID)
    
    # Get a route between the two nodes
    routeEdgeIDs = aStar.generateRoutePath(graph, backendFirstNode.ID, backendSecondNode.ID)
    
    # Display route via edges
    for edgeID in routeEdgeIDs:
        edge = graph.getEdgeFromID(edgeID)
        
        # Initialize leftmost and rightmost node variables
        leftmostNode: Node
        rightmostNode: Node
        
        # Get the leftmost node 
        if (int(edge.nodes[0].xCoordinate) <= int(edge.nodes[1].xCoordinate)):
            leftmostNode = edge.nodes[0]
            rightmostNode = edge.nodes[1]
        else:
            leftmostNode = edge.nodes[1]
            rightmostNode = edge.nodes[0]
        
        pygame.draw.line(screen, "blue", 
                         (int(leftmostNode.xCoordinate), int(leftmostNode.yCoordinate)), 
                         (int(rightmostNode.xCoordinate), int(rightmostNode.yCoordinate)), 
                         3)
        
    # Reset graph due to issues with deep copy
    graph = Graph(20, 20)
        
    pygame.display.update()

def mainMenu():
    while(True):
        # Get user decision
        print("1: Generate A* path")
        print("2: Create schedule")
        print("3: Load schedule")
        userInput = input("Enter menu option: ")
        
        if (userInput == "1"):
            basicPathfindingMenu(activeUser)
        elif (userInput == "2"):
            createScheduleMenu(activeUser)
        elif (userInput == "3"):
            loadScheduleMenu(activeUser)
        else:
            print("Invalid input.")
            exit()

## Startup menu for logging in. Returns a User representing the logged in user
def loginMenu() -> User:
    global database
    global databaseCursor
    
    # Prompt for login or register
    userInput = input("Enter L to login, and R to register: ").upper()
    
    # Register new user
    if userInput == "R":
        # Prompt for desired username
        newUsername = input("Please enter new username: ")
        newUserID = addNewUser(newUsername)
        
        if newUserID == -1:
            print("Username is taken.")
            exit()
        else:
            return User(newUserID)
        
    # Login to existing account
    elif userInput == "L":
        # Prompt for username
        userInput = input("Please enter your username: ")
        
        user = getUserFromUsername(userInput)
        
        # Account found
        if user != None:
            print("Account found!") 
            return user
        # Account not found
        else:
            print("Account not found. Crashing.")
            exit()
    # Neither input 'L' nor 'R'. Crash
    else:
        print("Invalid input. Crashing out of disrespect.")
        exit()

## Prompts for schedule information and adds a new schedule to the database
def createScheduleMenu(activeUser: User) -> None:
    
    global databaseCursor
    global database
    
    # Prompt for name
    newScheduleName = input("Please enter the schedule's name: ")
    
    # Attempt to make new Schedule
    newScheduleID = addNewScheduleToUserAccount(activeUser.ID, newScheduleName)
    
    # Ensure Schedule was created successfully
    if newScheduleID == -1:
        print("Schedule name is taken")
        return
    
    # Print success message
    print("Schedule created!")
    
    # Add new ScheduleRoutes until the user breaks
    while (True):
        # Prompt for new ScheduleRoute name
        newScheduleRouteName = input("Please enter the name of a ScheduleRoute to add to this schedule (or N to stop adding routes): ")
        if (newScheduleRouteName == "N" or newScheduleRouteName == "n"):
            break
        
        reconnect()
        
        # Ensure Schedule doesn't already have a ScheduleRoute with the chosen name
        databaseCursor.execute("SELECT * FROM ScheduleRoutes WHERE scheduleID = %s AND scheduleRouteName = %s;", (newScheduleID, newScheduleRouteName))
        duplicateValue = databaseCursor.fetchall()
        
        # If anything was returned from above query, then a copy exists
        if duplicateValue:
            print("Name already used for this schedule.")
            continue
        
        # Prompt for start time, end time
        newScheduleRouteStartTime = input("Please enter a start time for this route (hh:mm): ")
        newScheduleRouteEndTime = input("Please enter an end time for this route (hh:mm): ")
        
        # Prompt for start position of new route
        startNodeID = input("Enter ID of start node: ")
        
        # Prompt for end position of new route
        goalNodeID = input("Enter ID of goal node: ")
        
        # Initialize filter variables
        avoidStairs: bool = False
        avoidSteepTerrain: bool = False

        # Prompt user for stair avoidance option
        userInput = input("Enter 'Y' to avoid stairs, or 'N' to use stairs: ").upper()
        if userInput == "Y":
            avoidStairs = True
        
        # Prompt user for steep terrain avoidance option
        userInput = input("Enter 'Y' to avoid steep terrain, or 'N' to use steep terrain: ").upper()
        if userInput == "Y":
            avoidSteepTerrain = True
        
        # Attempt to add new ScheduleRoute to Schedule
        newScheduleRouteID = addNewScheduleRouteToSchedule(graph, newScheduleID, newScheduleRouteName, startNodeID, goalNodeID, newScheduleRouteStartTime, newScheduleRouteEndTime, avoidStairs, avoidSteepTerrain)
        
        # Ensure ScheduleRoute was created
        while newScheduleRouteID == -1:
            try:
                # Reconnect, try again
                database = mysql.connector.connect(
                    host="srv872.hstgr.io",
                    port="3306",
                    user="u425992461_WalkEaseRoot",
                    passwd="<>UnH^ackable@@@6",
                    database="u425992461_WalkEase",
                    connection_timeout=3600
                )

                # Get cursor for database
                databaseCursor = database.cursor(buffered=True)

                # Update max execution time to 10 seconds
                databaseCursor.execute("SET SESSION MAX_STATEMENT_TIME=10000")
                
                newScheduleRouteID = addNewScheduleRouteToSchedule(graph, newScheduleID, newScheduleRouteName, startNodeID, goalNodeID, newScheduleRouteStartTime, newScheduleRouteEndTime, avoidStairs, avoidSteepTerrain)
            except:
                continue
        
        # Success message
        print("Route created!")
    
## Prompts for schedule decision, route decision, and then prints a representation of that Route
def loadScheduleMenu(activeUser: User):
    # Get all schedules for this user
    schedules : list[Schedule] = getUserSchedules(activeUser.ID)
    
    # Display menu of all schedules this user has
    for i in range(0, len(schedules)):
        print(str(i + 1) + ": " + schedules[i].name)
        
    # Prompt user for Schedule choice
    scheduleIndex = int(input("Enter number of schedule to load: ")) - 1
    
    selectedSchedule = schedules[scheduleIndex]
    
    # Display menu of all ScheduleRoutes this schedule has
    for i in range(0, len(schedules[scheduleIndex].scheduleRoutes)):
        print(str(i + 1) + ": " + selectedSchedule.scheduleRoutes[i].name)
        
    # Prompt user for ScheduleRoute choice
    scheduleRouteIndex = int(input("Enter number of route to load: ")) - 1
    
    selectedScheduleRoute = selectedSchedule.scheduleRoutes[scheduleRouteIndex]
    
    # Get all edges in the selected ScheduleRoute
    edgeIDs : list[Edge] = []
    for edge in selectedScheduleRoute.edges:
        edgeIDs.append(edge.ID)
    
    # Print route
    graph.printGraph(pathEdgesIDs=edgeIDs)
        
## Prompts for a graph, start and goal nodes, and building nodes, then displays a route
def basicPathfindingMenu(activeUser: User) -> None:
    # Prompt for start position of new route
    startNodeID = input("Enter ID of start node: ")
        
    # Prompt for end position of new route
    goalNodeID = input("Enter ID of goal node: ")
    
    # Create graph
    newGraph: Graph = Graph(20, 20)
    
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

    # Initialize filter variables
    avoidStairs: bool = False
    avoidSteepTerrain: bool = False

    # Prompt user for stair avoidance option
    userInput = input("Enter 'Y' to avoid stairs, or 'N' to use stairs: ").upper()
    if userInput == "Y":
        avoidStairs = True
    
    # Prompt user for steep terrain avoidance option
    userInput = input("Enter 'Y' to avoid steep terrain, or 'N' to use steep terrain: ").upper()
    if userInput == "Y":
        avoidSteepTerrain = True
    
    # Create AStar instance
    aStar = AStar()
    
    # Record time before route generation
    start_time = time.perf_counter()
    
    pathEdgesIDs: list[str] = aStar.generateRoutePath(newGraph, startNodeID, goalNodeID, avoidStairs, avoidSteepTerrain)
    
    # Record time taken to generate route
    pathGenerateTime = time.perf_counter() - start_time
    
    # Print the graph with the path
    newGraph.printGraph(startNodeID=startNodeID, goalNodeID=goalNodeID, pathEdgesIDs=pathEdgesIDs)
    
    # Print the time taken to generate the route
    print("--- %s seconds ---" % (pathGenerateTime))
  
main()