import sqlite3

# Connect to the database
c = sqlite3.connect('database.sqlite3')

# Correct CREATE TABLE query (comments removed)
c.execute("""
          
CREATE TABLE Notification (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    customer_id INTEGER,          
    content VARCHAR(1500),  
    FOREIGN KEY (customer_id) REFERENCES customer(id) ON DELETE CASCADE

);


""")

# Commit the changes
c.commit()

# Close the connection
c.close()
