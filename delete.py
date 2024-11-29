import sqlite3

# Connect to the database
c = sqlite3.connect('database.sqlite3')

# Correct CREATE TABLE query (comments removed)
c.execute("""
CREATE TABLE Delivery (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    delivery_status TEXT DEFAULT 'Pending',
    expected_delivery_date TEXT DEFAULT 'TBA',
    address TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES Customer(id)
);

""")

# Commit the changes
c.commit()

# Close the connection
c.close()
