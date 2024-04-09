from map_components import Graph
from map_components import Edge
from map_components import Node
from map_components import Schedule
from map_components import ScheduleRoute
from session_components import AStar
from session_components import User

from database_connector import databaseCursor
from database_connector import database        #TODO This might be slow.  Maybe we set a variable equal to dataBase cursor and another to dataBase

from datetime import datetime # This is ridiculous and I hate python

import time

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
        
        # Verify that account exists
        databaseCursor.execute('SELECT userID FROM Users WHERE username = %s;', (userInput,))
        userID = databaseCursor.fetchall()
        # Account found
        if userID:
            print("Account found!") 
            return User(str(userID[0][0]))
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
        newScheduleRouteID = addNewScheduleRouteToSchedule(newScheduleID, newScheduleRouteName, startNodeID, goalNodeID, newScheduleRouteStartTime, newScheduleRouteEndTime, avoidStairs, avoidSteepTerrain)
        
        # Ensure ScheduleRoute was created
        if newScheduleRouteID == -1:
            print("Could not create schedule route. Path not found.")
            return
        
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
  
## Returns a list of Schedules belonging to a given User
#param userID: the ID of the User to get the Schedules of
#returns a list of Schedules belonging to the given User 
def getUserSchedules(userID: str) -> list[Schedule]:
    # Get all schedules for this user
    databaseCursor.execute("SELECT scheduleID, scheduleName FROM Schedules WHERE userID = %s;", (activeUser.ID,))
    scheduleInfos = databaseCursor.fetchall()
    
    # Instantiate list to return
    schedules: list[Schedule] = []
    
    # Fill list via the schedule information we just acquired
    for scheduleInfo in scheduleInfos:
        newSchedule: Schedule = Schedule(scheduleInfo[0], scheduleInfo[1], getScheduleRoutesInSchedule(str(scheduleInfo[0])))
        schedules.append(newSchedule)
    
    # Return list
    return schedules
   
## Returns a list of ScheduleRoutes in a given Schedule
#param scheduleID: the ID of the Schedule to get the ScheduleRoutes of
#returns a list of ScheduleRoutes belonging to the given Schedule
def getScheduleRoutesInSchedule(scheduleID: str):
    # Get all ScheduleRoutes for this Schedule
    databaseCursor.execute("SELECT scheduleRouteID, scheduleID, scheduleRouteName, scheduleRouteStartTime, scheduleRouteEndTime FROM ScheduleRoutes WHERE scheduleID = %s;", (scheduleID,))
    scheduleRoutesInfos = databaseCursor.fetchall()
    
    # Instantiate list to return
    scheduleRoutes: list[ScheduleRoute] = []
    
    # Fill list via the ScheduleRoute information we just acquired
    for scheduleRouteInfo in scheduleRoutesInfos:
        newScheduleRoute: ScheduleRoute = ScheduleRoute(str(scheduleRouteInfo[0]), str(scheduleRouteInfo[1]), scheduleRouteInfo[2], 
                                                        scheduleRouteInfo[3],
                                                        scheduleRouteInfo[4],
                                                        getEdgesInScheduleRoute(scheduleRouteInfo[0]))
        scheduleRoutes.append(newScheduleRoute)
        
    # Return list
    return scheduleRoutes
    
## Returns a list of Edges in a given ScheduleRoute
#param scheduleRouteID: the ID of the ScheduleRoute to get the Edges of
#returns a list of Edges belonging to the given ScheduleRoute
def getEdgesInScheduleRoute(scheduleRouteID: str) -> list[Edge]:
    # Get all Edges for this ScheduleRoute
    databaseCursor.execute("SELECT edgeActualID, scheduleRouteID FROM Edges WHERE scheduleRouteID = %s;", (scheduleRouteID,))
    edgesInfos = databaseCursor.fetchall()
    
    # Instantiate list to return
    edges: list[Edge] = []
    
    # Fill list via the Edge information we just acquired
    for edgeInfo in edgesInfos:
        newEdge: Edge = Edge(str(edgeInfo[0]), scheduleRouteID=str(edgeInfo[1]))
        edges.append(newEdge)
        
    # Return list
    return edges
    
## Adds a new user to the database
#param username: the requested username
#returns -1 if the username is taken, and the new User's ID (as a string) if not
def addNewUser(username: str):
    # Verify that username is not taken
    databaseCursor.execute("SELECT username FROM Users WHERE username = %s;", (username,))
    duplicateName = databaseCursor.fetchall()
    
    if duplicateName:
        return -1
    # Enter user into database
    else:
        databaseCursor.execute("INSERT INTO Users (username) VALUES (%s);", (username,))
        database.commit()
        return str(databaseCursor.lastrowid)
    
## Adds a new schedule to given user's account
#param userID: the ID of the User we're adding a Schedule to
#param scheduleName: the name of the Schedule we're adding
#returns -1 if the Schedule can't be created, and the ID (str) of the new Schedule otherwise
def addNewScheduleToUserAccount(userID: str, scheduleName: str):
    # Ensure the user doesn't already have a schedule with that name
    if copyExists("Schedules", "scheduleName", userID, scheduleName):
        return -1
            
    # Commit schedule
    databaseCursor.execute("INSERT INTO Schedules (userID, scheduleName) VALUES (%s, %s);", (userID, scheduleName))
    database.commit()
    
    # Return ID of the just created schedule
    return databaseCursor.lastrowid
    
## Adds a scheduleRoute to the given schedule
#param scheduleID: the ID of the schedule we're adding a ScheduleRoute to
#param scheduleRouteName: the user entered name of the new ScheduleRoute
#param startNodeID: the ID of the start node for this route
#param goalNodeID: the ID of the goal node for this route
#param startTime: the time the user needs to ARRIVE at their goa
#param endTime: the time the user's activity ends
#param avoidStairs: whether or not to avoid stairs
#param avoidSteepTerrain: whether or not to avoid steep terrain
#returns -1 if a route could not be found, and the ID (str) of the new ScheduleRoute otherwise
def addNewScheduleRouteToSchedule(scheduleID: str, scheduleRouteName: str, startNodeID: str, goalNodeID: str, startTime: str, endTime: str, 
                                  avoidStairs: bool = False, avoidSteepTerrain: bool = False):
    # Generate path
    pathEdgesIDs: list[str] = aStar.generateRoutePath(graph, startNodeID, goalNodeID, avoidStairs, avoidSteepTerrain)
    
    # Ensure path was found
    if pathEdgesIDs == None:
        return -1
    
    # Commit new scheduleRoute
    databaseCursor.execute("INSERT INTO ScheduleRoutes (scheduleID, scheduleRouteName, scheduleRouteStartTime, scheduleRouteEndTime) VALUES (%s, %s, %s, %s);", (scheduleID, scheduleRouteName, datetime.strptime(startTime, '%H:%M'), datetime.strptime(endTime, '%H:%M')))
    database.commit()
    
    # Get the ID of the ScheduleRoute we just created
    newScheduleRouteID = databaseCursor.lastrowid
    
    # Commit the edges on the generated route
    for edgeID in pathEdgesIDs:
        databaseCursor.execute("INSERT INTO Edges (edgeActualID, scheduleRouteID) VALUES (%s, %s);", (edgeID, newScheduleRouteID))
        
    database.commit()
    
    return newScheduleRouteID
    
## Ensures that the value "newValue" is not already present as an "attribute" in table "table" associated with the user with "userId"
#param table: the table to check
#param attribute: the column to check in the table
#param userID: the ID of the user to check data for
#param newValue: the value to ensure doesn't exist in the table
#returns False if a copy does not exist, and True if one does exist
def copyExists(table: str, attribute: str, userID: str, newValue: str) -> bool:
    # Get all of the attribute values associated with this user
    databaseCursor.execute("SELECT * FROM `{}` WHERE userID = %s AND `{}` = %s;".format(table, attribute), (userID, newValue))
    duplicateValue = databaseCursor.fetchall()
    
    # If anything was returned from above query, then a copy exists
    if duplicateValue:
        return True
            
    # No copy exists, return False
    return False

main()