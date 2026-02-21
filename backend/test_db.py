import mysql.connector
import json

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Rashmika@143',
    database='api_security'
)

cursor = conn.cursor(dictionary=True)

# Test basic counts
cursor.execute("SELECT COUNT(*) as count FROM logs")
total = cursor.fetchone()

cursor.execute("SELECT COUNT(*) as count FROM logs WHERE final_decision='NORMAL'")
normal = cursor.fetchone()

cursor.execute("SELECT COUNT(*) as count FROM logs WHERE final_decision='ATTACK'")
attack = cursor.fetchone()

cursor.execute("SELECT COUNT(*) as count FROM logs WHERE final_decision='ANOMALY'")
anomaly = cursor.fetchone()

cursor.execute("SELECT COUNT(*) as count FROM logs WHERE rule_flag=1")
rule_detected = cursor.fetchone()

cursor.execute("SELECT COUNT(*) as count FROM logs WHERE ml_flag=1")
ml_detected = cursor.fetchone()

cursor.execute("""
    SELECT ip_address, COUNT(*) as count
    FROM logs
    WHERE final_decision IN ('ATTACK', 'ANOMALY')
    GROUP BY ip_address
    ORDER BY count DESC
    LIMIT 1
""")
top_attacker = cursor.fetchone()

cursor.execute("SELECT AVG(anomaly_score) as avg_score FROM logs")
avg_score = cursor.fetchone()

print("Database Statistics:")
print(f"Total requests: {total['count']}")
print(f"Normal: {normal['count']}")
print(f"Attack: {attack['count']}")
print(f"Anomaly: {anomaly['count']}")
print(f"Rule-based detected: {rule_detected['count']}")
print(f"ML-based detected: {ml_detected['count']}")
print(f"Top attacker: {top_attacker}")
print(f"Avg anomaly score: {avg_score['avg_score']}")

cursor.close()
conn.close()
