import mysql.connector

# Connect to MySQL server
mydb = mysql.connector.connect(
   host="localhost",
   
   user='root',
   password='yes'
)

# Create a cursor object
my_cursor = mydb.cursor()

# Create the database if it doesn't exist
my_cursor.execute("CREATE DATABASE IF NOT EXISTS our_users")

# Show all databases to confirm the creation
my_cursor.execute("SHOW DATABASES")

# Print all the databases
for db in my_cursor:
    print(db)

# Close the cursor and connection
my_cursor.close()
mydb.close()