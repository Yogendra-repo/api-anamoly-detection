import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

# Load dataset
data = pd.read_csv("dataset.csv")

# Features and label
X = data[["request_count", "payload_length", "special_char_count", "failed_attempts"]]
y = data["label"]

# Split into train and test (professional touch)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate model
y_pred = model.predict(X_test)
print("\nModel Evaluation:\n")
print(classification_report(y_test, y_pred))

# Save model
joblib.dump(model, "model.pkl")

print("\nModel trained successfully and saved as model.pkl")