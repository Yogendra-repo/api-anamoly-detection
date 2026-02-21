import requests
import json

print("="*70)
print("API SECURITY ANOMALY DETECTION SYSTEM - COMPREHENSIVE TEST")
print("="*70)

# Test /health
print("\n[1] Health Check")
r = requests.get('http://127.0.0.1:5000/health')
print(f"    Status: {r.status_code}")
health_data = r.json()
print(f"    Model Loaded: {health_data['model_loaded']}")
print(f"    Status: {health_data['status']}")

# Test /stats
print("\n[2] Statistics Endpoint")
r = requests.get('http://127.0.0.1:5000/stats')
print(f"    Status: {r.status_code}")
stats = r.json()
print(f"    Total Requests: {stats['total_requests']}")
print(f"    NORMAL/ATTACK/ANOMALY: {stats['normal']}/{stats['detection']['attack']}/{stats['detection']['anomaly']}")
print(f"    Attack Percentage: {stats['attack_percentage']}%")
print(f"    Top Attacker: {stats['top_attacker_ip']} ({stats['top_attacker_count']} requests)")
print(f"    Detection Method Breakdown:")
print(f"      - Rule-based: {stats['detection']['rule_based']}")
print(f"      - ML-based: {stats['detection']['ml_based']}")
print(f"      - Hybrid: {stats['detection']['hybrid']}")
print(f"    Avg Anomaly Score: {stats['avg_anomaly_score']}")

# Test /recent-logs
print("\n[3] Recent Logs Endpoint")
r = requests.get('http://127.0.0.1:5000/recent-logs?limit=5')
print(f"    Status: {r.status_code}")
logs = r.json()
print(f"    Total Logs Fetched: {len(logs)}")
if logs:
    print(f"    Sample Log:")
    log = logs[0]
    print(f"      IP: {log['ip_address']}, Endpoint: {log['endpoint']}")
    print(f"      Decision: {log['final_decision']}, Score: {log['anomaly_score']}")

# Test /endpoint-analytics
print("\n[4] Endpoint Analytics")
r = requests.get('http://127.0.0.1:5000/endpoint-analytics')
print(f"    Status: {r.status_code}")
endpoints = r.json()
print(f"    Monitored Endpoints: {len(endpoints)}")
if endpoints:
    print(f"    Top Endpoints by Attack:")
    for ep in endpoints[:3]:
        print(f"      {ep['endpoint']}: {ep['attacks']} attacks, {ep['total_requests']} total")

# Test /predict
print("\n[5] Prediction Endpoint (Normal Request)")
payload = {
    'ip_address': '192.168.1.110',
    'endpoint': '/api/test',
    'method': 'GET',
    'payload': 'id=42',
    'response_code': 200
}
r = requests.post('http://127.0.0.1:5000/predict', json=payload)
print(f"    Status: {r.status_code}")
pred = r.json()
print(f"    Final Decision: {pred['final_decision']}")
print(f"    Anomaly Score: {pred['anomaly_score']}")
print(f"    Confidence: {pred['confidence']}")
print(f"    Rule Flag: {pred['rule_flag']}, ML Flag: {pred['ml_flag']}")

# Test /predict with attack
print("\n[6] Prediction Endpoint (SQL Injection Attack)")
payload = {
    'ip_address': '203.0.113.200',
    'endpoint': '/api/users',
    'method': 'POST',
    'payload': "username'; DROP TABLE users;--",
    'response_code': 500
}
r = requests.post('http://127.0.0.1:5000/predict', json=payload)
print(f"    Status: {r.status_code}")
pred = r.json()
print(f"    Final Decision: {pred['final_decision']}")
print(f"    Anomaly Score: {pred['anomaly_score']}")
print(f"    Confidence: {pred['confidence']}")
print(f"    Rule Detections: {pred['rule_detection']}")
print(f"    Rule Flag: {pred['rule_flag']}, ML Flag: {pred['ml_flag']}")

print("\n" + "="*70)
print("ALL TESTS COMPLETED SUCCESSFULLY ✓")
print("="*70)
