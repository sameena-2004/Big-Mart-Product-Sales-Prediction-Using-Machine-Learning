import sqlite3

conn = sqlite3.connect("database/products.db")
cursor = conn.cursor()

cursor.execute("ALTER TABLE products ADD COLUMN user TEXT")

conn.commit()
conn.close()

print("User column added successfully")