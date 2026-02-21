"""
Feature Extraction Module
Extracts advanced behavioral features from API requests for ML-based anomaly detection
"""

import math
import re
from typing import Dict, Tuple
from collections import defaultdict

class FeatureExtractor:
    def __init__(self):
        self.ip_request_counts = defaultdict(int)
        self.ip_failed_attempts = defaultdict(int)
        self.endpoint_request_counts = defaultdict(int)
        self.endpoint_failed_attempts = defaultdict(int)
        
    def extract_features(self, request_data: Dict) -> Dict:
        """
        Extract all behavioral features from a request
        
        Args:
            request_data: Request metadata dict
            
        Returns:
            Dict with all extracted features
        """
        
        ip_address = request_data.get("ip_address", "unknown")
        endpoint = request_data.get("endpoint", "/")
        payload = request_data.get("payload", "")
        method = request_data.get("method", "GET")
        
        # Basic payload features
        payload_size = len(payload)
        special_char_count = self._count_special_chars(payload)
        entropy = self._calculate_entropy(payload)
        
        # Character distribution features
        digit_ratio = self._count_digits_ratio(payload)
        uppercase_ratio = self._count_uppercase_ratio(payload)
        url_encoded_ratio = self._count_url_encoded_ratio(payload)
        
        # SQL/XSS keyword features
        sql_keyword_count = self._count_sql_keywords(payload)
        xss_keyword_count = self._count_xss_keywords(payload)
        
        # Request behavior features
        unique_special_chars = len(set(c for c in payload if not c.isalnum() and c != ' '))
        average_token_length = self._calculate_avg_token_length(payload)
        
        # IP-based features
        ip_request_count = self.ip_request_counts[ip_address]
        ip_failed_attempts = self.ip_failed_attempts[ip_address]
        
        # Endpoint-based features
        endpoint_request_count = self.endpoint_request_counts[endpoint]
        endpoint_failed_attempts = self.endpoint_failed_attempts[endpoint]
        
        # HTTP method features
        is_post = 1 if method == "POST" else 0
        is_put = 1 if method == "PUT" else 0
        is_delete = 1 if method == "DELETE" else 0
        
        # Update request counts for future requests
        self.ip_request_counts[ip_address] += 1
        self.endpoint_request_counts[endpoint] += 1
        
        if request_data.get("failed_attempt", False):
            self.ip_failed_attempts[ip_address] += 1
            self.endpoint_failed_attempts[endpoint] += 1
        
        # Feature vector (normalized)
        features = {
            'ip_request_count': ip_request_count,
            'payload_size': payload_size,
            'special_char_count': special_char_count,
            'entropy': entropy,
            'digit_ratio': digit_ratio,
            'uppercase_ratio': uppercase_ratio,
            'url_encoded_ratio': url_encoded_ratio,
            'sql_keyword_count': sql_keyword_count,
            'xss_keyword_count': xss_keyword_count,
            'unique_special_chars': unique_special_chars,
            'avg_token_length': average_token_length,
            'ip_failed_attempts': ip_failed_attempts,
            'endpoint_request_count': endpoint_request_count,
            'endpoint_failed_attempts': endpoint_failed_attempts,
            'is_post': is_post,
            'is_put': is_put,
            'is_delete': is_delete,
        }
        
        return features
    
    def _count_special_chars(self, text: str) -> int:
        """Count special characters in text"""
        special_chars = r"[!@#$%^&*()_+\-=\[\]{};:'\",.<>?/\\|~`]"
        return len(re.findall(special_chars, text))
    
    def _calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of text - measures randomness"""
        if not text:
            return 0
        
        frequencies = defaultdict(int)
        for char in text:
            frequencies[char] += 1
        
        entropy = 0
        text_len = len(text)
        for freq in frequencies.values():
            p = freq / text_len
            entropy -= p * math.log2(p)
        
        return entropy
    
    def _count_digits_ratio(self, text: str) -> float:
        """Calculate ratio of digits in text"""
        if not text:
            return 0
        digit_count = sum(1 for c in text if c.isdigit())
        return digit_count / len(text)
    
    def _count_uppercase_ratio(self, text: str) -> float:
        """Calculate ratio of uppercase letters"""
        if not text:
            return 0
        upper_count = sum(1 for c in text if c.isupper())
        return upper_count / len(text)
    
    def _count_url_encoded_ratio(self, text: str) -> float:
        """Calculate ratio of URL-encoded characters"""
        if not text:
            return 0
        encoded_count = len(re.findall(r'%[0-9A-Fa-f]{2}', text))
        return encoded_count / (len(text) / 3) if len(text) > 0 else 0
    
    def _count_sql_keywords(self, text: str) -> int:
        """Count SQL injection keywords"""
        sql_keywords = [
            r'\bSELECT\b', r'\bUNION\b', r'\bORDER\bBY\b', r'\bDROP\b',
            r'\bUPDATE\b', r'\bDELETE\b', r'\bINSERT\b', r'\bEXEC\b',
            r'\bHAVING\b'
        ]
        count = 0
        for keyword in sql_keywords:
            count += len(re.findall(keyword, text, re.IGNORECASE))
        return count
    
    def _count_xss_keywords(self, text: str) -> int:
        """Count XSS attack keywords"""
        xss_keywords = [
            r'<script', r'javascript:', r'onerror=', r'onload=',
            r'<iframe', r'<img', r'<svg'
        ]
        count = 0
        for keyword in xss_keywords:
            count += len(re.findall(keyword, text, re.IGNORECASE))
        return count
    
    def _calculate_avg_token_length(self, text: str) -> float:
        """Calculate average token length"""
        tokens = re.findall(r'\w+', text)
        if not tokens:
            return 0
        return sum(len(token) for token in tokens) / len(tokens)
    
    def reset_counters(self):
        """Reset all IP and endpoint counters"""
        self.ip_request_counts.clear()
        self.ip_failed_attempts.clear()
        self.endpoint_request_counts.clear()
        self.endpoint_failed_attempts.clear()


if __name__ == "__main__":
    # Test the extractor
    extractor = FeatureExtractor()
    
    test_requests = [
        {
            "ip_address": "192.168.1.1",
            "endpoint": "/api/users",
            "payload": "username=john&password=pass123",
            "method": "POST",
            "failed_attempt": False
        },
        {
            "ip_address": "192.168.1.2",
            "endpoint": "/api/search",
            "payload": "q=' OR 1=1 --",
            "method": "GET",
            "failed_attempt": False
        },
        {
            "ip_address": "192.168.1.3",
            "endpoint": "/api/upload",
            "payload": "<script>alert('xss')</script>",
            "method": "POST",
            "failed_attempt": False
        },
    ]
    
    for req in test_requests:
        features = extractor.extract_features(req)
        print(f"\nRequest from {req['ip_address']}")
        for key, value in features.items():
            print(f"  {key}: {value:.4f}" if isinstance(value, float) else f"  {key}: {value}")
