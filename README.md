Big Mart Product Sales Prediction Using Machine Learning

📌 Project Overview

This project predicts product sales in Big Mart stores using Machine Learning.
It analyzes product and store information from a dataset and predicts the expected sales of products.

A Flask-based web application is used to interact with the machine learning model, allowing users to add products, view analytics, and predict sales.

🎯 Objective

The main objective of this project is to build a system that can:

Predict future product sales

Help store managers analyze product performance

Provide insights using data analytics and forecasting

🛠 Technologies Used

Python

Machine Learning (Scikit-learn)

Flask (Web Framework)

HTML / CSS

SQLite Database

Pandas & NumPy

📂 Project Structure
bigmart_Final_Yr_Proj
│
├── app.py                  # Main Flask application
├── train_model.py          # Machine learning model training
├── createdb.py             # Database creation
├── productsdb.py           # Product database operations
├── usersdb.py              # User database operations
│
├── dataset/
│   └── train.csv           # Dataset used for training
│
├── model/
│   └── sales_model.pkl     # Trained machine learning model
│
├── database/
│   ├── products.db
│   └── users.db
│
├── templates/              # Frontend HTML pages
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── products.html
│   ├── add_product.html
│   ├── edit_product.html
│   ├── prediction.html
│   ├── forecast.html
│   ├── analytics.html
│   └── chatbot.html
│
└── insert_products.py
⚙️ How the Project Works

The dataset is used to train a machine learning model.

The trained model is saved as sales_model.pkl.

The Flask application loads this model.

Users interact with the system through the web interface.

When product details are entered, the system predicts the expected sales.

🚀 Features

User Login and Registration

Product Management System

Machine Learning Sales Prediction

Sales Forecasting

Analytics Dashboard

AI Chatbot Support

▶️ How to Run the Project

Clone the repository

git clone https://github.com/sameena-2004/Big-Mart-Product-Sales-Prediction-Using-Machine-Learning

Install required libraries

pip install flask pandas numpy scikit-learn

Run the application

python app.py

Open browser and go to

http://localhost:5000
📊 Dataset

The dataset used in this project contains product and store information such as:

Product type

Store details

Product weight

Visibility

Outlet type

Sales

This data is used to train the machine learning model.

📌 Future Improvements

Improve prediction accuracy

Deploy the application online

Add more advanced analytics

Use deep learning models

👩‍💻 Author
Pathan Sameena
Final Year Project
Big Mart Product Sales Prediction Using Machine Learning
