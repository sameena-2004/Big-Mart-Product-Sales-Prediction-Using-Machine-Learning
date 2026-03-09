from flask import Flask,render_template,request,redirect,session
import sqlite3
import requests
from groq import Groq
import joblib
import numpy as np

model = joblib.load("model/sales_model.pkl")



app = Flask(__name__)
app.secret_key="retailai"
client = Groq(api_key="YOUR_API_KEY")
# Database connection
def get_db():
    conn = sqlite3.connect("database/products.db")
    conn.row_factory = sqlite3.Row
    return conn
def get_category_data():

    conn = get_db()

    rows = conn.execute(
    "SELECT category, SUM(stock) as total_stock FROM products GROUP BY category"
    ).fetchall()

    conn.close()

    labels = []
    values = []

    for r in rows:
        labels.append(r["category"])
        values.append(r["total_stock"])

    return labels, values
# Detect low stock products
def get_low_stock_products():

    conn = get_db()

    user = session["user"]

    products = conn.execute(
        "SELECT * FROM products WHERE stock < 20 AND user=?",
        (user,)
    ).fetchall()

    conn.close()

    return products
# Retail analytics from product database
def get_category_sales():

    conn = get_db()

    user = session["user"]

    data = conn.execute(
        "SELECT category, SUM(stock) as total_stock FROM products WHERE user=? GROUP BY category",
        (user,)
    ).fetchall()

    conn.close()

    labels = []
    values = []

    for row in data:
        labels.append(row["category"])
        values.append(row["total_stock"])

    return labels, values
def recommend_restock(stock):

    try:

        if stock <= 5:
            return 100

        elif stock <= 10:
            return 80

        elif stock <= 20:
            return 50

        else:
            return 0

    except:
        return 50

@app.route("/",methods=["GET","POST"])
def login():

    if request.method=="POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database/users.db")
        conn.row_factory = sqlite3.Row

        user = conn.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username,password)
        ).fetchone()

        conn.close()

        if user:

            session["user"] = user["username"]
            session["shop"] = user["shop_name"]

            return redirect("/dashboard")

    return render_template("login.html")
@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]
        shop_name = request.form["shop_name"]
        shop_location = request.form["shop_location"]

        conn = sqlite3.connect("database/users.db")

        conn.execute(
        "INSERT INTO users(username,password,shop_name,shop_location) VALUES (?,?,?,?)",
        (username,password,shop_name,shop_location)
        )

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("register.html")

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/")

    low_stock_products = get_low_stock_products()

    conn = get_db()

    total_products = conn.execute(
    "SELECT COUNT(*) FROM products WHERE user=?",
    (session["user"],)
).fetchone()[0]

    conn.close()

    labels, values = get_category_sales()

    return render_template(
    "dashboard.html",
    top_products=labels,
    low_products=labels,
    low_stock_products=low_stock_products,
    recommend_restock=recommend_restock,
    total_products=total_products
)

@app.route("/products")
def products():

    if "user" not in session:
        return redirect("/")

    conn=get_db()
    user = session["user"]

    products = conn.execute(
    "SELECT * FROM products WHERE user=?",
    (user,)
    ).fetchall()
    conn.close()

    return render_template("products.html",products=products)


@app.route("/prediction")
def prediction():

    if "user" not in session:
        return redirect("/")

    return render_template("prediction.html")


@app.route("/predict", methods=["POST"])
def predict():

    name = request.form.get("name","Product")

    try:

        price = float(request.form.get("price",0))
        stock = float(request.form.get("stock",0))

        # example features for trained model
        weight = 10
        visibility = 0.05

        features = np.array([[weight, visibility, price]])

        try:
            prediction = model.predict(features)
            demand = int(prediction[0] / 10)
        except:
            demand = int((price * 1.2) + (80 - stock))

        if demand < 10:
            demand = 10

        result = demand

    except Exception as e:
        print(e)
        result = "Prediction error"

    return render_template(
        "prediction.html",
        prediction_text=f"Predicted Monthly Demand for {name}: {result} units"
    )
@app.route("/analytics")
def analytics():

    if "user" not in session:
        return redirect("/")

    labels, values = get_category_sales()

    top10_labels = labels[:10]
    top10_values = values[:10]

    return render_template(
        "analytics.html",
        labels=labels,
        values=values,
        top10_labels=top10_labels,
        top10_values=top10_values
    )
@app.route("/forecast")
def forecast():

    if "user" not in session:
        return redirect("/")

    conn = get_db()

    products = conn.execute(
        "SELECT * FROM products WHERE user=?",
        (session["user"],)
    ).fetchall()

    conn.close()

    forecast_results = []

    for p in products:

        try:

            category = p["category"].lower()
            price = float(p["price"])
            stock = float(p["stock"])

            category_factor = {
                "snacks":1.5,
                "dairy":1.3,
                "beverages":1.4,
                "grocery":1.2,
                "household":1.0
            }

            factor = category_factor.get(category,1)

            features = np.array([[10, 0.05, price]])

            try:
                prediction = model.predict(features)
                demand = int(prediction[0] / 10)
            except:
                demand = int((price * 1.2) + (80 - stock))

            if demand < 10:
                demand = 10

            restock = max(demand - stock, 0)
            if demand < 10:
                demand = 10

            restock = max(demand - stock,0)

        except:
            demand = 30
            restock = 20

        forecast_results.append({
            "name":p["name"],
            "stock":stock,
            "demand":demand,
            "restock":restock
        })

    return render_template(
        "forecast.html",
        forecast_results=forecast_results
    )


@app.route("/chatbot")
def chatbot():

    if "user" not in session:
        return redirect("/")

    return render_template("chatbot.html")


@app.route("/chat", methods=["POST"])
def chat():

    user_message = request.json.get("message")

    try:

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": """
You are RetailAI, a professional retail business assistant similar to AI assistants used by Amazon and Flipkart.

Your role is to help shop owners understand and use this retail analytics application.

You can guide users about:
* Inventory management
* Product demand forecasting
* Sales analytics
* Restocking recommendations
* Understanding dashboard insights

Respond professionally, clearly, and concisely.
Avoid slang or casual language.
Provide helpful retail suggestions whenever possible.
Keep responses concise and under 80 words.
"""
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )

        reply = response.choices[0].message.content

    except Exception as e:
        print(e)
        reply = "AI assistant unavailable."

    return {"reply": reply}

@app.route("/add_product", methods=["GET","POST"])
def add_product():

    if request.method=="POST":

        name=request.form["name"]
        category=request.form["category"]
        price=request.form["price"]
        stock=request.form.get("stock",0)

        conn=get_db()

        user = session["user"]

        conn.execute(
    "INSERT INTO products(user,name,category,price,stock) VALUES (?,?,?,?,?)",
        (user,name,category,price,stock)
        )

        conn.commit()
        conn.close()

        return redirect("/products")

    return render_template("add_product.html")

@app.route("/edit_product/<int:id>", methods=["GET","POST"])
def edit_product(id):

    conn=get_db()

    if request.method=="POST":

        name=request.form["name"]
        category=request.form["category"]
        price=request.form["price"]
        stock=request.form["stock"]

        conn.execute(
        "UPDATE products SET name=?,category=?,price=?,stock=? WHERE id=?",
        (name,category,price,stock,id)
        )

        conn.commit()
        conn.close()

        return redirect("/products")

    product = conn.execute(
"SELECT * FROM products WHERE id=? AND user=?",
(id,session["user"])
).fetchone()

    conn.close()

    return render_template("edit_product.html",product=product)
@app.route("/delete_product/<int:id>")
def delete_product(id):

    conn=get_db()

    conn.execute(
"DELETE FROM products WHERE id=? AND user=?",
(id,session["user"])
)

    conn.commit()
    conn.close()

    return redirect("/products")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__=="__main__":
    app.run(debug=True)
from flask import Flask,render_template,request,redirect,session
import sqlite3
import requests
from groq import Groq
import joblib
import numpy as np

model = joblib.load("model/sales_model.pkl")



app = Flask(__name__)
app.secret_key="retailai"
client = Groq(api_key="YOUR_API_KEY")
# Database connection
def get_db():
    conn = sqlite3.connect("database/products.db")
    conn.row_factory = sqlite3.Row
    return conn
def get_category_data():

    conn = get_db()

    rows = conn.execute(
    "SELECT category, SUM(stock) as total_stock FROM products GROUP BY category"
    ).fetchall()

    conn.close()

    labels = []
    values = []

    for r in rows:
        labels.append(r["category"])
        values.append(r["total_stock"])

    return labels, values
# Detect low stock products
def get_low_stock_products():

    conn = get_db()

    user = session["user"]

    products = conn.execute(
        "SELECT * FROM products WHERE stock < 20 AND user=?",
        (user,)
    ).fetchall()

    conn.close()

    return products
# Retail analytics from product database
def get_category_sales():

    conn = get_db()

    user = session["user"]

    data = conn.execute(
        "SELECT category, SUM(stock) as total_stock FROM products WHERE user=? GROUP BY category",
        (user,)
    ).fetchall()

    conn.close()

    labels = []
    values = []

    for row in data:
        labels.append(row["category"])
        values.append(row["total_stock"])

    return labels, values
def recommend_restock(stock):

    try:

        if stock <= 5:
            return 100

        elif stock <= 10:
            return 80

        elif stock <= 20:
            return 50

        else:
            return 0

    except:
        return 50

@app.route("/",methods=["GET","POST"])
def login():

    if request.method=="POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database/users.db")
        conn.row_factory = sqlite3.Row

        user = conn.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username,password)
        ).fetchone()

        conn.close()

        if user:

            session["user"] = user["username"]
            session["shop"] = user["shop_name"]

            return redirect("/dashboard")

    return render_template("login.html")
@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]
        shop_name = request.form["shop_name"]
        shop_location = request.form["shop_location"]

        conn = sqlite3.connect("database/users.db")

        conn.execute(
        "INSERT INTO users(username,password,shop_name,shop_location) VALUES (?,?,?,?)",
        (username,password,shop_name,shop_location)
        )

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("register.html")

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/")

    low_stock_products = get_low_stock_products()

    conn = get_db()

    total_products = conn.execute(
    "SELECT COUNT(*) FROM products WHERE user=?",
    (session["user"],)
).fetchone()[0]

    conn.close()

    labels, values = get_category_sales()

    return render_template(
    "dashboard.html",
    top_products=labels,
    low_products=labels,
    low_stock_products=low_stock_products,
    recommend_restock=recommend_restock,
    total_products=total_products
)

@app.route("/products")
def products():

    if "user" not in session:
        return redirect("/")

    conn=get_db()
    user = session["user"]

    products = conn.execute(
    "SELECT * FROM products WHERE user=?",
    (user,)
    ).fetchall()
    conn.close()

    return render_template("products.html",products=products)


@app.route("/prediction")
def prediction():

    if "user" not in session:
        return redirect("/")

    return render_template("prediction.html")


@app.route("/predict", methods=["POST"])
def predict():

    name = request.form.get("name","Product")

    try:

        price = float(request.form.get("price",0))
        stock = float(request.form.get("stock",0))

        # example features for trained model
        weight = 10
        visibility = 0.05

        features = np.array([[weight, visibility, price]])

        try:
            prediction = model.predict(features)
            demand = int(prediction[0] / 10)
        except:
            demand = int((price * 1.2) + (80 - stock))

        if demand < 10:
            demand = 10

        result = demand

    except Exception as e:
        print(e)
        result = "Prediction error"

    return render_template(
        "prediction.html",
        prediction_text=f"Predicted Monthly Demand for {name}: {result} units"
    )
@app.route("/analytics")
def analytics():

    if "user" not in session:
        return redirect("/")

    labels, values = get_category_sales()

    top10_labels = labels[:10]
    top10_values = values[:10]

    return render_template(
        "analytics.html",
        labels=labels,
        values=values,
        top10_labels=top10_labels,
        top10_values=top10_values
    )
@app.route("/forecast")
def forecast():

    if "user" not in session:
        return redirect("/")

    conn = get_db()

    products = conn.execute(
        "SELECT * FROM products WHERE user=?",
        (session["user"],)
    ).fetchall()

    conn.close()

    forecast_results = []

    for p in products:

        try:

            category = p["category"].lower()
            price = float(p["price"])
            stock = float(p["stock"])

            category_factor = {
                "snacks":1.5,
                "dairy":1.3,
                "beverages":1.4,
                "grocery":1.2,
                "household":1.0
            }

            factor = category_factor.get(category,1)

            features = np.array([[10, 0.05, price]])

            try:
                prediction = model.predict(features)
                demand = int(prediction[0] / 10)
            except:
                demand = int((price * 1.2) + (80 - stock))

            if demand < 10:
                demand = 10

            restock = max(demand - stock, 0)
            if demand < 10:
                demand = 10

            restock = max(demand - stock,0)

        except:
            demand = 30
            restock = 20

        forecast_results.append({
            "name":p["name"],
            "stock":stock,
            "demand":demand,
            "restock":restock
        })

    return render_template(
        "forecast.html",
        forecast_results=forecast_results
    )


@app.route("/chatbot")
def chatbot():

    if "user" not in session:
        return redirect("/")

    return render_template("chatbot.html")


@app.route("/chat", methods=["POST"])
def chat():

    user_message = request.json.get("message")

    try:

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": """
You are RetailAI, a professional retail business assistant similar to AI assistants used by Amazon and Flipkart.

Your role is to help shop owners understand and use this retail analytics application.

You can guide users about:
* Inventory management
* Product demand forecasting
* Sales analytics
* Restocking recommendations
* Understanding dashboard insights

Respond professionally, clearly, and concisely.
Avoid slang or casual language.
Provide helpful retail suggestions whenever possible.
Keep responses concise and under 80 words.
"""
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )

        reply = response.choices[0].message.content

    except Exception as e:
        print(e)
        reply = "AI assistant unavailable."

    return {"reply": reply}

@app.route("/add_product", methods=["GET","POST"])
def add_product():

    if request.method=="POST":

        name=request.form["name"]
        category=request.form["category"]
        price=request.form["price"]
        stock=request.form.get("stock",0)

        conn=get_db()

        user = session["user"]

        conn.execute(
    "INSERT INTO products(user,name,category,price,stock) VALUES (?,?,?,?,?)",
        (user,name,category,price,stock)
        )

        conn.commit()
        conn.close()

        return redirect("/products")

    return render_template("add_product.html")

@app.route("/edit_product/<int:id>", methods=["GET","POST"])
def edit_product(id):

    conn=get_db()

    if request.method=="POST":

        name=request.form["name"]
        category=request.form["category"]
        price=request.form["price"]
        stock=request.form["stock"]

        conn.execute(
        "UPDATE products SET name=?,category=?,price=?,stock=? WHERE id=?",
        (name,category,price,stock,id)
        )

        conn.commit()
        conn.close()

        return redirect("/products")

    product = conn.execute(
"SELECT * FROM products WHERE id=? AND user=?",
(id,session["user"])
).fetchone()

    conn.close()

    return render_template("edit_product.html",product=product)
@app.route("/delete_product/<int:id>")
def delete_product(id):

    conn=get_db()

    conn.execute(
"DELETE FROM products WHERE id=? AND user=?",
(id,session["user"])
)

    conn.commit()
    conn.close()

    return redirect("/products")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__=="__main__":
    app.run(debug=True)