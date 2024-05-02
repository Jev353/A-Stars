import mysql.connector

from session_components import User

# Connect to database
database = mysql.connector.connect(
    host="srv872.hstgr.io",
    port="3306",
    user="u425992461_WalkEaseRoot",
    passwd="",
    database="u425992461_WalkEase",
    connection_timeout=3600
)

# Get cursor for database
databaseCursor = database.cursor(buffered=True)

# Update max execution time to 10 seconds
databaseCursor.execute("SET SESSION MAX_STATEMENT_TIME=10000")

### Functions for common database queries
## Returns a User object if an account is found with the given username
#param username: the username to check the database for
#returns a User object coorelating to the given username, or None if the username wasn't found in the database
def getUserFromUsername(username: str) -> User:
    reconnect()
    
    # Verify that account exists
    databaseCursor.execute('SELECT userID FROM Users WHERE username = %s;', (username,))
    userID = databaseCursor.fetchall()
    
    # Account found
    if userID:
        return User(str(userID[0][0]))
    # Account not found
    else:
        return None
    
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
    
## Runs a no-op to test connection, and then reconnects if necessary
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
            passwd="",
            database="u425992461_WalkEase",
            connection_timeout=3600
        )

        # Get cursor for database
        databaseCursor = database.cursor(buffered=True)

        # Update max execution time to 10 seconds
        databaseCursor.execute("SET SESSION MAX_STATEMENT_TIME=10000")