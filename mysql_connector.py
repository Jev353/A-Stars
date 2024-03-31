import mysql.connector

# Connect to database
dataBase = mysql.connector.connect(
    host="localhost",
    port="3307",
    user="root",
    passwd="SuperSecret@#5@",
    database="walkease"
)

# Get cursor for database
databaseCursor = dataBase.cursor(buffered=True)