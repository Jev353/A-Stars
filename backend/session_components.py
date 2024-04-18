from map_components import Node
from map_components import Edge
from map_components import Schedule

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
    def generateRoutePath(self, startNodeID: str, endNodeID: str, avoidStairs: str=False, avoidSteepTerrain: str=False):
        ## TODO: A buncha nonsense
        pass

### Represents a user
class User():
    ## Constructor
    def __init__(self, id: str, schedules: list[Schedule]):
        self.id = id
        self.schedules = schedules