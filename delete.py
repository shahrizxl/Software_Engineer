import sqlite3

# Connect to the database
c = sqlite3.connect('database.sqlite3')

# Correct CREATE TABLE query (comments removed)
c.execute("""
CREATE TABLE Notification (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    content TEXT NOT NULL,  
    FOREIGN KEY (customer_id) REFERENCES Customer(id)
);


""")

# Commit the changes
c.commit()

# Close the connection
c.close()
