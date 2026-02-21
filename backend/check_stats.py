import time
import requests
import json

time.sleep(2)  # Wait for async threads to complete inserts

response = requests.get('http://127.0.0.1:5000/stats')
print('Status Code:', response.status_code)
stats = response.json()
print('\nDashboard Statistics:')
print(f"  Total Requests: {stats['total_requests']}")
print(f"  NORMAL: {stats['normal']}")
print(f"  ATTACK: {stats['detection']['attack']}")
print(f"  ANOMALY: {stats['detection']['anomaly']}")
print(f"  Attack %: {stats['attack_percentage']}%")
print(f"  Top Attacker: {stats['top_attacker_ip']}")
print(f"  Rule-based Detections: {stats['detection']['rule_based']}")
print(f"  ML-based Detections: {stats['detection']['ml_based']}")
print(f"  Avg Anomaly Score: {stats['avg_anomaly_score']}")
