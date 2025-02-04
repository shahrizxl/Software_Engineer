import sqlite3

c = sqlite3.connect('database.sqlite3')

cursor = c.cursor()

cursor.execute("""
    delete from Sales where type="Subtract"


""")


c.commit()

c.close()

print("Data inserted successfully!")
