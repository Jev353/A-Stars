import mysql.connector

from map_components import Edge
from map_components import Node
from map_components import Graph
from session_components import Route
from session_components import ScheduleRoute
from session_components import Schedule
from session_components import AStar

from datetime import datetime

# Connect to database
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

### Functions for common database queries
## Returns a list of Schedules belonging to a given User
#param userID: the ID of the User to get the Schedules of
#returns a list of Schedules belonging to the given User 
def getUserSchedules(userID: str) -> list[Schedule]:
    global databaseCursor
    
    reconnect()
    
    # Get all schedules for this user
    databaseCursor.execute("SELECT scheduleID, scheduleName FROM Schedules WHERE userID = %s;", (userID,))
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
    global databaseCursor
    
    reconnect()
    
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
    global databaseCursor

    reconnect()

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
    global databaseCursor
    
    reconnect()
    
    # Verify that username is not taken
    databaseCursor.execute("SELECT username FROM Users WHERE username = %s;", (username,))
    duplicateName = databaseCursor.fetchall()
    
    if duplicateName:
        return -1
    # Enter user into database
    else:
        reconnect()
        
        databaseCursor.execute("INSERT INTO Users (username) VALUES (%s);", (username,))
        database.commit()
        return str(databaseCursor.lastrowid)
    
## Adds a new schedule to given user's account
#param userID: the ID of the User we're adding a Schedule to
#param scheduleName: the name of the Schedule we're adding
#returns -1 if the Schedule can't be created, and the ID (str) of the new Schedule otherwise
def addNewScheduleToUserAccount(userID: str, scheduleName: str):
    global databaseCursor
    
    # Ensure the user doesn't already have a schedule with that name
    if copyExists("Schedules", "scheduleName", userID, scheduleName):
        return -1
            
    reconnect()
            
    # Commit schedule
    databaseCursor.execute("INSERT INTO Schedules (userID, scheduleName) VALUES (%s, %s);", (userID, scheduleName))
    database.commit()
    
    # Return ID of the just created schedule
    return databaseCursor.lastrowid
    
## Adds a scheduleRoute to the given schedule
#param graph: the graph to use to generate the route
#param scheduleID: the ID of the schedule we're adding a ScheduleRoute to
#param scheduleRouteName: the user entered name of the new ScheduleRoute
#param startNodeID: the ID of the start node for this route
#param goalNodeID: the ID of the goal node for this route
#param startTime: the time the user needs to ARRIVE at their goa
#param endTime: the time the user's activity ends
#param avoidStairs: whether or not to avoid stairs
#param avoidSteepTerrain: whether or not to avoid steep terrain
#returns -1 if a route could not be found, and the ID (str) of the new ScheduleRoute otherwise
def addNewScheduleRouteToSchedule(graph: Graph, scheduleID: str, scheduleRouteName: str, startNodeID: str, goalNodeID: str, startTime: str, endTime: str, 
                                  avoidStairs: bool = False, avoidSteepTerrain: bool = False):
    global databaseCursor
    
    # Create AStar instance
    aStar = AStar()
    
    # Generate path
    pathEdgesIDs: list[str] = aStar.generateRoutePath(graph, startNodeID, goalNodeID, avoidStairs, avoidSteepTerrain)
    
    # Ensure path was found
    if pathEdgesIDs == None:
        return -1
    
    reconnect()
    
    # Commit new scheduleRoute
    databaseCursor.execute("INSERT INTO ScheduleRoutes (scheduleID, scheduleRouteName, scheduleRouteStartTime, scheduleRouteEndTime) VALUES (%s, %s, %s, %s);", (scheduleID, scheduleRouteName, datetime.strptime(startTime, '%H:%M'), datetime.strptime(endTime, '%H:%M')))
    database.commit()
    
    # Get the ID of the ScheduleRoute we just created
    newScheduleRouteID = databaseCursor.lastrowid
    
    # Commit the edges on the generated route
    for edgeID in pathEdgesIDs:
        reconnect() #TODO Move outside the loop?
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
    global databaseCursor
    
    reconnect()
    
    # Get all of the attribute values associated with this user
    databaseCursor.execute("SELECT * FROM `{}` WHERE userID = %s AND `{}` = %s;".format(table, attribute), (userID, newValue))
    duplicateValue = databaseCursor.fetchall()
    
    # If anything was returned from above query, then a copy exists
    if duplicateValue:
        return True
            
    # No copy exists, return False
    return False

def reconnect():
    global database
    global databaseCursor
    
    try:
        databaseCursor.execute("SELECT 1;")
    except:
        print("Reconnecting...")
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