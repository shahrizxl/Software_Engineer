import sqlite3

# Connect to the database
c = sqlite3.connect('database.sqlite3')

# Correct CREATE TABLE query (comments removed)
c.execute("""
    CREATE TABLE IF NOT EXISTS Delivery (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        delivery_status TEXT DEFAULT 'Pending',
        expected_delivery_date TEXT DEFAULT 'TBA',
        address TEXT NOT NULL
    );
""")

# Commit the changes
c.commit()

# Close the connection
c.close()
