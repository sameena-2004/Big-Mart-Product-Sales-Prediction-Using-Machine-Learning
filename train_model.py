import pandas as pd
import numpy as np
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score

# Load dataset
data = pd.read_csv("dataset/Train.csv")

# Handle missing values
data['Item_Weight'] = data['Item_Weight'].fillna(data['Item_Weight'].mean())
data['Outlet_Size'] = data['Outlet_Size'].fillna(data['Outlet_Size'].mode()[0])

# Fix fat content labels
data['Item_Fat_Content'] = data['Item_Fat_Content'].replace({
    'LF': 'Low Fat',
    'low fat': 'Low Fat',
    'reg': 'Regular'
})

# Feature engineering
data['Store_Age'] = 2024 - data['Outlet_Establishment_Year']

# Drop ID columns
data.drop(['Item_Identifier','Outlet_Identifier'], axis=1, inplace=True)

# One-hot encode categorical variables
data = pd.get_dummies(data)

# Features and target
X = data.drop("Item_Outlet_Sales", axis=1)
y = data["Item_Outlet_Sales"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
X, y, test_size=0.2, random_state=42
)

# Train model
model = RandomForestRegressor(
n_estimators=500,
max_depth=12,
random_state=42,
n_jobs=-1
)

model.fit(X_train, y_train)

# Predict
pred = model.predict(X_test)

score = r2_score(y_test, pred)

print("Model Accuracy:", score)

# Save model
os.makedirs("model", exist_ok=True)
joblib.dump(model, "model/model.pkl")

print("Model saved successfully!")