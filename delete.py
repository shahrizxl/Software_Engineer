import sqlite3

# Connect to the database
c = sqlite3.connect('database.sqlite3')

# Correct DELETE query
c.execute("DELETE FROM customer WHERE id = '040805100671'")

# Commit the changes
c.commit()

# Close the connection
c.close()

#
