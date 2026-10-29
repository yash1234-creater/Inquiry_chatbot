import sqlite3

connection = sqlite3.connect("leads.db")

rows = connection.execute(
    "SELECT * FROM leads"
).fetchall()

for row in rows:
    print(row)

connection.close()