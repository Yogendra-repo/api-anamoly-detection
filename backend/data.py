import pandas as pd
import numpy as np

np.random.seed(42)

# 200 normal samples
normal = pd.DataFrame({
    "request_count": np.random.normal(55, 5, 200).astype(int),
    "payload_length": np.random.normal(120, 10, 200).astype(int),
    "special_char_count": np.random.normal(2, 1, 200).astype(int),
    "failed_attempts": np.random.normal(0, 1, 200).astype(int),
    "label": "normal"
})

# 50 attack samples
attack = pd.DataFrame({
    "request_count": np.random.normal(300, 20, 50).astype(int),
    "payload_length": np.random.normal(900, 50, 50).astype(int),
    "special_char_count": np.random.normal(30, 5, 50).astype(int),
    "failed_attempts": np.random.normal(10, 3, 50).astype(int),
    "label": "attack"
})

data = pd.concat([normal, attack])
data.to_csv("dataset.csv", index=False)

print("250 row dataset created successfully!")