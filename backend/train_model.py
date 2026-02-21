"""
Enhanced Model Training Script
Trains an Isolation Forest model for unsupervised anomaly detection
Uses CICIDS2017-like dataset with 17 advanced behavioral features
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
import joblib
import json

# Load dataset
print("Loading dataset...")
data = pd.read_csv("dataset.csv")

print(f"Dataset shape: {data.shape}")
print(f"Label distribution:\n{data['label'].value_counts()}")

# Separate features and labels
X = data.drop('label', axis=1)
y = data['label']

# Convert labels to numerical (1 for attack, 0 for normal)
y_binary = (y == 'attack').astype(int)

print(f"\nFeatures: {list(X.columns)}")
print(f"Feature count: {len(X.columns)}")

# Standardize features (important for Isolation Forest)
print("\nStandardizing features...")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Split data for evaluation
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y_binary, test_size=0.2, random_state=42, stratify=y_binary
)

print(f"\nTraining set size: {len(X_train)}")
print(f"Test set size: {len(X_test)}")

# Train Isolation Forest
print("\nTraining Isolation Forest model...")
print("This may take a minute...")

iso_forest = IsolationForest(
    contamination=0.2,  # 20% of samples expected to be anomalies
    random_state=42,
    n_estimators=100,
    n_jobs=-1  # Use all available cores
)

iso_forest.fit(X_train)

# Make predictions
print("\nMaking predictions on test set...")
train_pred = iso_forest.predict(X_train)
test_pred = iso_forest.predict(X_test)

# Get anomaly scores (negative = anomaly, positive = normal)
train_scores = iso_forest.score_samples(X_train)
test_scores = iso_forest.score_samples(X_test)

# Convert predictions to binary (1 for anomaly, 0 for normal)
train_pred_binary = (train_pred == -1).astype(int)
test_pred_binary = (test_pred == -1).astype(int)

# Evaluation metrics
print("\n" + "="*60)
print("MODEL EVALUATION")
print("="*60)

print("\nTraining Set Performance:")
print(f"Accuracy: {(train_pred_binary == y_train).mean():.4f}")
print(f"Total anomalies detected: {train_pred_binary.sum()}")
print(f"Total normal samples: {(train_pred_binary == 0).sum()}")

print("\nTest Set Performance:")
print(f"Accuracy: {(test_pred_binary == y_test).mean():.4f}")
print(f"Total anomalies detected: {test_pred_binary.sum()}")
print(f"Total normal samples: {(test_pred_binary == 0).sum()}")

print("\nDetailed Classification Report (Test Set):")
print(classification_report(y_test, test_pred_binary, target_names=['Normal', 'Anomaly']))

print("\nConfusion Matrix (Test Set):")
cm = confusion_matrix(y_test, test_pred_binary)
print(f"True Negatives: {cm[0,0]}")
print(f"False Positives: {cm[0,1]}")
print(f"False Negatives: {cm[1,0]}")
print(f"True Positives: {cm[1,1]}")

# ROC-AUC score (using anomaly scores)
roc_score = roc_auc_score(y_test, -test_scores)
print(f"\nROC-AUC Score: {roc_score:.4f}")

# Save models
print("\n" + "="*60)
print("SAVING MODELS")
print("="*60)

joblib.dump(iso_forest, "model.pkl")
joblib.dump(scaler, "scaler.pkl")
print("✓ Isolation Forest model saved as model.pkl")
print("✓ Feature scaler saved as scaler.pkl")

# Save feature names for reference
feature_names = list(X.columns)
with open("feature_names.json", "w") as f:
    json.dump(feature_names, f)
print("✓ Feature names saved as feature_names.json")

# Save model metadata
metadata = {
    "model_type": "IsolationForest",
    "contamination": 0.2,
    "n_estimators": 100,
    "features": feature_names,
    "n_features": len(feature_names),
    "training_samples": len(X_train),
    "test_samples": len(X_test),
    "normal_samples": (y_binary == 0).sum(),
    "attack_samples": (y_binary == 1).sum(),
    "roc_auc_score": float(roc_score),
    "test_accuracy": float((test_pred_binary == y_test).mean())
}

with open("model_metadata.json", "w") as f:
  json.dump(metadata, f, indent=2, default=int)
print("✓ Model metadata saved as model_metadata.json")

print("\n" + "="*60)
print("TRAINING COMPLETE!")
print("="*60)
print(f"\nModel is ready for deployment!")
print(f"ROC-AUC Score: {roc_score:.4f}")
print(f"Test Accuracy: {(test_pred_binary == y_test).mean():.4f}")
