import sqlite3

conn = sqlite3.connect("database/products.db")
cursor = conn.cursor()

cursor.execute("""
ALTER TABLE products
ADD COLUMN stock INTEGER DEFAULT 0
""")

conn.commit()
conn.close()

print("Stock column added successfully")