"""
Rule-Based Detection Module
Detects known attack patterns using pattern matching and heuristics
"""

import re
from typing import Dict, Tuple

class RuleDetector:
    def __init__(self):
        # SQL Injection keywords and patterns
        self.sql_keywords = {
            "SELECT", "INSERT", "UPDATE", "DELETE", "DROP", "CREATE",
            "ALTER", "EXEC", "EXECUTE", "UNION", "ORDER BY", "HAVING",
            "GROUP BY", "WHERE", "OR", "AND", "IF", "CASE", "CAST",
            "CONVERT", "SCRIPT"
        }
        
        # SQL Injection patterns
        self.sql_patterns = [
            r"(\bOR\b\s+1\s*=\s*1)",  # OR 1=1
            r"(\bOR\b\s+['\"]?['\"]?\s*=\s*['\"]?['\"]+\s*\bOR\b\s*1\s*=\s*1)",  # OR ""=""
            r"(;?\s*DROP\s+TABLE)",  # DROP TABLE
            r"(UNION.*SELECT)",  # UNION SELECT
            r"(--\s|#\s|\/\*.*\*\/)",  # SQL comments
        ]
        
        # XSS patterns
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",  # Script tags
            r"javascript:",  # JavaScript URI
            r"on\w+\s*=",  # Event handlers (onerror=, onload=, etc.)
            r"<iframe[^>]*>",  # IFrame injection
            r"<img[^>]*onerror",  # Image onerror
            r"<svg[^>]*onload",  # SVG onload
            r"<body[^>]*onload",  # Body onload
        ]
        
        # Command Injection patterns
        self.cmd_patterns = [
            r"(\||&&|;|`|$\()",  # Shell operators
            r"(cat|ls|rm|mv|cp|chmod|bash|sh|cmd|powershell)",  # Commands
        ]
        
        # Path Traversal patterns
        self.path_patterns = [
            r"(\.\./|\.\.\\)",  # Directory traversal
            r"(%2e%2f|%5c)",  # Encoded traversal
        ]
        
        # Brute force detection thresholds
        self.failed_login_threshold = 5  # More than 5 failed attempts
        self.high_request_rate_threshold = 100  # Requests per minute
        
    def detect_sql_injection(self, payload: str) -> Tuple[bool, str]:
        """Detect SQL injection attacks"""
        payload_upper = payload.upper()
        
        # Check for SQL keywords
        keyword_count = 0
        for keyword in self.sql_keywords:
            if keyword in payload_upper:
                keyword_count += 1
        
        if keyword_count > 2:
            return True, f"SQL_INJECTION (found {keyword_count} keywords)"
        
        # Check for SQL patterns
        for pattern in self.sql_patterns:
            if re.search(pattern, payload, re.IGNORECASE):
                return True, f"SQL_INJECTION (pattern matched)"
        
        return False, ""
    
    def detect_xss(self, payload: str) -> Tuple[bool, str]:
        """Detect XSS (Cross-Site Scripting) attacks"""
        for pattern in self.xss_patterns:
            if re.search(pattern, payload, re.IGNORECASE):
                return True, "XSS_INJECTION"
        
        return False, ""
    
    def detect_command_injection(self, payload: str) -> Tuple[bool, str]:
        """Detect command injection attacks"""
        for pattern in self.cmd_patterns:
            if re.search(pattern, payload, re.IGNORECASE):
                return True, "COMMAND_INJECTION"
        
        return False, ""
    
    def detect_path_traversal(self, payload: str) -> Tuple[bool, str]:
        """Detect path traversal attacks"""
        for pattern in self.path_patterns:
            if re.search(pattern, payload, re.IGNORECASE):
                return True, "PATH_TRAVERSAL"
        
        return False, ""
    
    def detect_brute_force(self, failed_attempts: int) -> Tuple[bool, str]:
        """Detect brute force attacks based on failed login attempts"""
        if failed_attempts >= self.failed_login_threshold:
            return True, f"BRUTE_FORCE ({failed_attempts} failed attempts)"
        
        return False, ""
    
    def detect_high_request_rate(self, request_count: int) -> Tuple[bool, str]:
        """Detect abnormally high request rates (DDoS indicator)"""
        if request_count > self.high_request_rate_threshold:
            return True, f"SLOW_DDoS ({request_count} requests)"
        
        return False, ""
    
    def scan_request(self, request_data: Dict) -> Tuple[bool, list]:
        """
        Scan request for all types of attacks
        
        Args:
            request_data: Dict containing request metadata
            
        Returns:
            Tuple of (is_malicious, list_of_attacks)
        """
        attacks_detected = []
        
        # Get payload from request (might be in body, query params, or headers)
        payload = request_data.get("payload", "")
        uri = request_data.get("uri", "")
        query_string = request_data.get("query_string", "")
        full_request = payload + uri + query_string
        
        # Check SQL Injection
        sql_flag, sql_msg = self.detect_sql_injection(full_request)
        if sql_flag:
            attacks_detected.append(sql_msg)
        
        # Check XSS
        xss_flag, xss_msg = self.detect_xss(full_request)
        if xss_flag:
            attacks_detected.append(xss_msg)
        
        # Check Command Injection
        cmd_flag, cmd_msg = self.detect_command_injection(full_request)
        if cmd_flag:
            attacks_detected.append(cmd_msg)
        
        # Check Path Traversal
        path_flag, path_msg = self.detect_path_traversal(full_request)
        if path_flag:
            attacks_detected.append(path_msg)
        
        # Check Brute Force
        failed_attempts = request_data.get("failed_attempts", 0)
        brute_flag, brute_msg = self.detect_brute_force(failed_attempts)
        if brute_flag:
            attacks_detected.append(brute_msg)
        
        # Check High Request Rate
        request_count = request_data.get("request_count", 0)
        rate_flag, rate_msg = self.detect_high_request_rate(request_count)
        if rate_flag:
            attacks_detected.append(rate_msg)
        
        is_malicious = len(attacks_detected) > 0
        
        return is_malicious, attacks_detected


if __name__ == "__main__":
    # Test the detector
    detector = RuleDetector()
    
    # Test SQL Injection
    test_cases = [
        {"payload": "' OR 1=1 --", "description": "SQL Injection test"},
        {"payload": "<script>alert('XSS')</script>", "description": "XSS test"},
        {"payload": "normal_request", "description": "Normal request"},
    ]
    
    for test in test_cases:
        is_malicious, attacks = detector.scan_request(test)
        print(f"\n{test['description']}")
        print(f"Payload: {test['payload']}")
        print(f"Malicious: {is_malicious}")
        print(f"Attacks: {attacks}")
