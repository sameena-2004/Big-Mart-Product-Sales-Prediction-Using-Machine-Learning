import sqlite3

conn = sqlite3.connect("database/products.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
category TEXT,
price INTEGER
)
""")

products = [
("Milk","Dairy",250),
("Pepsi","Soft Drinks",180),
("Apple","Fruits",200),
("Chicken","Meat",350),
("Bread","Breads",120),
("Chips","Snack Foods",90)
]

cursor.executemany(
"INSERT INTO products(name,category,price) VALUES(?,?,?)",
products
)

conn.commit()
conn.close()