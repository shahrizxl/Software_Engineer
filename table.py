
import sqlite3

# Connect to the database
c = sqlite3.connect('database.sqlite3')

# Correct DELETE query
c.execute("CREATE TABLE Cart ( id INTEGER PRIMARY KEY, customer_id STRING NOT NULL, product_id INTEGER NOT NULL, quantity INTEGER NOT NULL, date_added DATETIME DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (customer_id) REFERENCES Customer (id) , FOREIGN KEY (product_id) REFERENCES Product (id) );")

# Commit the changes
c.commit()

# Close the connection
c.close()
