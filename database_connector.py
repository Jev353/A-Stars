import mysql.connector

# Connect to database
database = mysql.connector.connect(
    host="localhost",
    port="3307",
    user="root",
    passwd="SuperSecret@#5@",
    database="walkease"
)

# Get cursor for database
databaseCursor = database.cursor(buffered=True)

### Functions for common database queries
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