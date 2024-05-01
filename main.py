from map_components import Edge
from map_components import Node
from map_components import Graph
from session_components import Route
from session_components import ScheduleRoute
from session_components import Schedule
from session_components import AStar
from session_components import User

from database_connector import *

from datetime import datetime # This is ridiculous and I hate python

import time

import pygame

graph = Graph(20, 20)
aStar = AStar()
activeUser: User

def main():
    # Initialize active user object
    global activeUser
    activeUser = loginMenu()
    
    mainMenu()

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