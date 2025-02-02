import sqlite3

c = sqlite3.connect('database.sqlite3')

cursor = c.cursor()

cursor.execute("""
    CREATE TABLE Feedback (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    ph TEXT NOT NULL,
    content TEXT NOT NULL,
    date DATE NOT NULL DEFAULT (date('now'))
);

""")


c.commit()

c.close()

print("Data inserted successfully!")
