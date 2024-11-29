import sqlite3

# Connect to the database
c = sqlite3.connect('database.sqlite3')

# Correct CREATE TABLE query (comments removed)
c.execute("""
          
CREATE TABLE Notificationcourier (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    content TEXT NOT NULL  

);


""")

# Commit the changes
c.commit()

# Close the connection
c.close()
