import requests
import random
import time

URL = "http://127.0.0.1:5000/predict"

def generate_normal():
    return {
        "request_count": random.randint(40, 70),
        "payload_length": random.randint(100, 150),
        "special_char_count": random.randint(0, 3),
        "failed_attempts": random.randint(0, 1),
        "ip_address": f"192.168.1.{random.randint(1, 100)}"
    }

def generate_attack():
    return {
        "request_count": random.randint(250, 350),
        "payload_length": random.randint(800, 1000),
        "special_char_count": random.randint(20, 40),
        "failed_attempts": random.randint(5, 15),
        "ip_address": f"10.0.0.{random.randint(1, 100)}"
    }

num_requests = int(input("Enter number of API requests to generate: "))

for i in range(num_requests):
    if random.random() < 0.7:
        data = generate_normal()
    else:
        data = generate_attack()

    response = requests.post(URL, json=data)
    print(f"Request {i+1}: {response.json()}")

    time.sleep(0.2)

print("Traffic generation completed!")