
import sqlite3

# Connect to the database
c = sqlite3.connect('database.sqlite3')

# Correct DELETE query
c.execute("DROP TABLE Delivery")

# Commit the changes
c.commit()

# Close the connection
c.close()
