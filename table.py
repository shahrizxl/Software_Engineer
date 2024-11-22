
import sqlite3

# Connect to the database
c = sqlite3.connect('database.sqlite3')

# Correct DELETE query
c.execute("CREATE TABLE Feedback (id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,email TEXT NOT NULL UNIQUE,ph TEXT NOT NULL UNIQUE,content TEXT NOT NULL);")

# Commit the changes
c.commit()

# Close the connection
c.close()
