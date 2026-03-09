import sqlite3

conn = sqlite3.connect("database/products.db")

cursor = conn.cursor()

products = [
("Milk","Dairy",250),
("Pepsi","Soft Drinks",180),
("Apple","Fruits",200),
("Chicken","Meat",350),
("Bread","Breads",120),
("Chips","Snack Foods",90)
]

cursor.executemany(
"INSERT INTO products(name,category,price) VALUES (?,?,?)",
products
)

conn.commit()
conn.close()

print("Products inserted")