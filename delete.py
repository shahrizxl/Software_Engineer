import sqlite3

# Connect to the database
c = sqlite3.connect('database.sqlite3')

# Correct CREATE TABLE query (comments removed)
c.execute("""
          
CREATE TABLE purchaseditem (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    customer_id INTEGER NOT NULL,          
    product_id INTEGER NOT NULL,          
    totalprice FLOAT NOT NULL,            
    quantity INTEGER NOT NULL,             
    refund_status VARCHAR(50) DEFAULT 'Pending',
    delivery_status VARCHAR(50) DEFAULT 'Pending',
    refund_reason VARCHAR(100),  
    FOREIGN KEY (customer_id) REFERENCES customer(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE CASCADE
);


""")

# Commit the changes
c.commit()

# Close the connection
c.close()
