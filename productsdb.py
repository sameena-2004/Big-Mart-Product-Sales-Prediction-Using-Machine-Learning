
import sqlite3

conn = sqlite3.connect("database/products.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
category TEXT,
price INTEGER,
stock INTEGER
)
""")

conn.commit()
conn.close()

print("Products table updated")
