import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Rashmika@143",
    "database": "api_security"
}

def get_db_connection():
    """Get MySQL database connection"""
    conn = mysql.connector.connect(**DB_CONFIG)
    conn.database = 'api_security'
    return conn

# Test insertion
try:
    conn = get_db_connection()
    print(f"✓ Connected successfully")
    print(f"Connected database: {conn.database}")
    
    cursor = conn.cursor()
    
    query = """
    INSERT INTO logs 
    (ip_address, endpoint, method, payload_size, anomaly_score, 
     rule_flag, rule_detection, ml_flag, final_decision, 
     attacks_count, failed_attempts, request_count)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    cursor.execute(query, (
        '192.168.1.100',
        '/api/test',
        'GET',
        15,
        -0.5,
        1,
        'SQL_INJECTION',
        1,
        'ATTACK',
        1,
        0,
        1
    ))
    
    conn.commit()
    print("✓ Insertion successful")
    
    # Verify
    cursor.execute("SELECT COUNT(*) as cnt FROM logs")
    result = cursor.fetchone()
    print(f"Total rows now: {result[0]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
