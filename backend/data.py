"""
Enhanced Data Generation Script
Generates realistic CICIDS2017-like dataset for Isolation Forest training
Includes 17 advanced behavioral features mimicking real API traffic patterns
"""

import pandas as pd
import numpy as np

np.random.seed(42)

def generate_dataset():
    """Generate realistic API traffic dataset with advanced features"""
    
    num_normal = 2000
    num_attack = 500
    
    # ==================== NORMAL TRAFFIC ====================
    normal_data = {
        'ip_request_count': np.random.normal(50, 5, num_normal).astype(int),
        'payload_size': np.random.normal(150, 20, num_normal).astype(int),
        'special_char_count': np.random.normal(3, 1, num_normal).astype(int),
        'entropy': np.random.normal(3.5, 0.5, num_normal),
        'digit_ratio': np.random.normal(0.15, 0.05, num_normal),
        'uppercase_ratio': np.random.normal(0.1, 0.05, num_normal),
        'url_encoded_ratio': np.random.normal(0.02, 0.01, num_normal),
        'sql_keyword_count': np.random.normal(0.1, 0.3, num_normal).astype(int),
        'xss_keyword_count': np.random.normal(0, 0.1, num_normal).astype(int),
        'unique_special_chars': np.random.normal(4, 1, num_normal).astype(int),
        'avg_token_length': np.random.normal(6, 1, num_normal),
        'ip_failed_attempts': np.random.normal(0, 1, num_normal).astype(int),
        'endpoint_request_count': np.random.normal(40, 5, num_normal).astype(int),
        'endpoint_failed_attempts': np.random.normal(0, 0.5, num_normal).astype(int),
        'is_post': np.random.binomial(1, 0.5, num_normal),
        'is_put': np.random.binomial(1, 0.1, num_normal),
        'is_delete': np.random.binomial(1, 0.05, num_normal),
        'label': 'normal'
    }
    
    normal_df = pd.DataFrame(normal_data)
    # Ensure non-negative values
    for col in normal_df.columns:
        if col != 'label':
            normal_df[col] = normal_df[col].clip(lower=0)
    
    # ==================== ATTACK TRAFFIC ====================
    # SQL Injection patterns
    sql_injection = {
        'ip_request_count': np.random.normal(200, 30, num_attack//2).astype(int),
        'payload_size': np.random.normal(800, 100, num_attack//2).astype(int),
        'special_char_count': np.random.normal(40, 10, num_attack//2).astype(int),
        'entropy': np.random.normal(5.5, 0.8, num_attack//2),
        'digit_ratio': np.random.normal(0.3, 0.1, num_attack//2),
        'uppercase_ratio': np.random.normal(0.25, 0.1, num_attack//2),
        'url_encoded_ratio': np.random.normal(0.15, 0.05, num_attack//2),
        'sql_keyword_count': np.random.normal(5, 2, num_attack//2).astype(int),
        'xss_keyword_count': np.random.normal(0.5, 0.5, num_attack//2).astype(int),
        'unique_special_chars': np.random.normal(15, 3, num_attack//2).astype(int),
        'avg_token_length': np.random.normal(12, 3, num_attack//2),
        'ip_failed_attempts': np.random.normal(8, 3, num_attack//2).astype(int),
        'endpoint_request_count': np.random.normal(150, 30, num_attack//2).astype(int),
        'endpoint_failed_attempts': np.random.normal(5, 2, num_attack//2).astype(int),
        'is_post': np.random.binomial(1, 0.8, num_attack//2),
        'is_put': np.random.binomial(1, 0.3, num_attack//2),
        'is_delete': np.random.binomial(1, 0.2, num_attack//2),
        'label': 'attack'
    }
    
    # XSS patterns
    xss_attack = {
        'ip_request_count': np.random.normal(180, 25, num_attack//4).astype(int),
        'payload_size': np.random.normal(600, 80, num_attack//4).astype(int),
        'special_char_count': np.random.normal(35, 8, num_attack//4).astype(int),
        'entropy': np.random.normal(4.8, 0.7, num_attack//4),
        'digit_ratio': np.random.normal(0.25, 0.1, num_attack//4),
        'uppercase_ratio': np.random.normal(0.2, 0.08, num_attack//4),
        'url_encoded_ratio': np.random.normal(0.1, 0.04, num_attack//4),
        'sql_keyword_count': np.random.normal(0.5, 0.5, num_attack//4).astype(int),
        'xss_keyword_count': np.random.normal(8, 2, num_attack//4).astype(int),
        'unique_special_chars': np.random.normal(14, 3, num_attack//4).astype(int),
        'avg_token_length': np.random.normal(8, 2, num_attack//4),
        'ip_failed_attempts': np.random.normal(3, 2, num_attack//4).astype(int),
        'endpoint_request_count': np.random.normal(120, 25, num_attack//4).astype(int),
        'endpoint_failed_attempts': np.random.normal(2, 1, num_attack//4).astype(int),
        'is_post': np.random.binomial(1, 0.6, num_attack//4),
        'is_put': np.random.binomial(1, 0.2, num_attack//4),
        'is_delete': np.random.binomial(1, 0.1, num_attack//4),
        'label': 'attack'
    }
    
    # Brute force patterns
    brute_force = {
        'ip_request_count': np.random.normal(300, 50, num_attack//4).astype(int),
        'payload_size': np.random.normal(100, 20, num_attack//4).astype(int),
        'special_char_count': np.random.normal(5, 2, num_attack//4).astype(int),
        'entropy': np.random.normal(2.5, 0.5, num_attack//4),
        'digit_ratio': np.random.normal(0.2, 0.08, num_attack//4),
        'uppercase_ratio': np.random.normal(0.08, 0.05, num_attack//4),
        'url_encoded_ratio': np.random.normal(0.01, 0.01, num_attack//4),
        'sql_keyword_count': np.random.normal(0, 0.1, num_attack//4).astype(int),
        'xss_keyword_count': np.random.normal(0, 0.1, num_attack//4).astype(int),
        'unique_special_chars': np.random.normal(3, 1, num_attack//4).astype(int),
        'avg_token_length': np.random.normal(7, 1, num_attack//4),
        'ip_failed_attempts': np.random.normal(25, 5, num_attack//4).astype(int),
        'endpoint_request_count': np.random.normal(200, 40, num_attack//4).astype(int),
        'endpoint_failed_attempts': np.random.normal(20, 5, num_attack//4).astype(int),
        'is_post': np.random.binomial(1, 0.9, num_attack//4),
        'is_put': np.random.binomial(1, 0.05, num_attack//4),
        'is_delete': np.random.binomial(1, 0.02, num_attack//4),
        'label': 'attack'
    }
    
    sql_df = pd.DataFrame(sql_injection)
    xss_df = pd.DataFrame(xss_attack)
    brute_df = pd.DataFrame(brute_force)
    
    # Ensure non-negative values
    for df in [sql_df, xss_df, brute_df]:
        for col in df.columns:
            if col != 'label':
                df[col] = df[col].clip(lower=0)
    
    # Combine all data
    data = pd.concat([normal_df, sql_df, xss_df, brute_df], ignore_index=True)
    
    # Shuffle
    data = data.sample(frac=1).reset_index(drop=True)
    
    return data


if __name__ == "__main__":
    # Generate and save dataset
    data = generate_dataset()
    
    # Save to CSV
    data.to_csv("dataset.csv", index=False)
    
    print(f"✓ Dataset generated successfully!")
    print(f"  Total samples: {len(data)}")
    print(f"  Normal samples: {(data['label'] == 'normal').sum()}")
    print(f"  Attack samples: {(data['label'] == 'attack').sum()}")
    print(f"  Features: {', '.join(data.columns[:-1])}")
    print(f"  Shape: {data.shape}")
    print(f"\nFirst few rows:")
    print(data.head(10))