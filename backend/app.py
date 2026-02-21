"""
AI-Powered API Security Anomaly Detection System
Production-grade Flask backend with hybrid detection (rule-based + ML-based)
Uses IsolationForest for unsupervised anomaly detection with advanced feature extraction
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import joblib
import json
import mysql.connector
import numpy as np
import csv
from datetime import datetime
from functools import wraps
import logging
import threading

# Import custom modules
from rule_detector import RuleDetector
from feature_extractor import FeatureExtractor

# ==================== FLASK CONFIGURATION ====================
app = Flask(__name__)
CORS(app)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== MODEL & SCALER LOADING ====================
try:
    model = joblib.load("model.pkl")
    scaler = joblib.load("scaler.pkl")
    
    with open("feature_names.json", "r") as f:
        feature_names = json.load(f)
    
    with open("model_metadata.json", "r") as f:
        model_metadata = json.load(f)
    
    logger.info("✓ Isolation Forest model loaded successfully")
    logger.info(f"✓ Features: {len(feature_names)}")
    logger.info(f"✓ Model ROC-AUC: {model_metadata.get('roc_auc_score', 'N/A')}")
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    model = None
    scaler = None

# ==================== MODULES INITIALIZATION ====================
rule_detector = RuleDetector()
feature_extractor = FeatureExtractor()

# ==================== DATABASE CONFIGURATION ====================
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Rashmika@143",  # 🔴 CHANGE THIS TO YOUR PASSWORD
    "database": "api_security"
}

def get_db_connection():
    """Get MySQL database connection"""
    conn = mysql.connector.connect(**DB_CONFIG)
    conn.database = 'api_security'
    return conn


# ==================== SETUP DATABASE SCHEMA ====================
DB_AVAILABLE = False

def setup_database():
    """Initialize database with required schema"""
    global DB_AVAILABLE
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # First, create database if not exists
        cursor.execute("CREATE DATABASE IF NOT EXISTS api_security")
        cursor.execute("USE api_security")
        
        # Drop existing tables to ensure fresh schema
        cursor.execute("DROP TABLE IF EXISTS detection_stats")
        cursor.execute("DROP TABLE IF EXISTS endpoint_baseline")
        cursor.execute("DROP TABLE IF EXISTS logs")
        
        # Create logs table with enhanced schema
        create_logs_table = """
        CREATE TABLE IF NOT EXISTS logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            ip_address VARCHAR(50) NOT NULL,
            endpoint VARCHAR(255) NOT NULL,
            method VARCHAR(10),
            payload_size INT,
            anomaly_score FLOAT,
            rule_flag BOOLEAN DEFAULT FALSE,
            rule_detection TEXT,
            ml_flag BOOLEAN DEFAULT FALSE,
            final_decision VARCHAR(20),
            attacks_count INT,
            failed_attempts INT,
            request_count INT,
            INDEX idx_ip (ip_address),
            INDEX idx_timestamp (timestamp),
            INDEX idx_endpoint (endpoint)
        )
        """
        
        # Create endpoint baseline table
        create_baseline_table = """
        CREATE TABLE IF NOT EXISTS endpoint_baseline (
            id INT AUTO_INCREMENT PRIMARY KEY,
            endpoint VARCHAR(255) UNIQUE,
            avg_payload_size FLOAT,
            avg_request_frequency FLOAT,
            avg_response_time FLOAT,
            normal_pattern_count INT,
            last_updated DATETIME,
            INDEX idx_endpoint (endpoint)
        )
        """
        
        # Create statistics table for dashboard
        create_stats_table = """
        CREATE TABLE IF NOT EXISTS detection_stats (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            total_requests INT,
            rule_detected INT,
            ml_detected INT,
            hybrid_detected INT,
            normal_requests INT,
            attack_percentage FLOAT,
            top_attacker_ip VARCHAR(50),
            INDEX idx_timestamp (timestamp)
        )
        """
        
        cursor.execute(create_logs_table)
        cursor.execute(create_baseline_table)
        cursor.execute(create_stats_table)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        DB_AVAILABLE = True
        logger.info("✓ Database schema initialized")
    except Exception as e:
        DB_AVAILABLE = False
        logger.warning(f"Database not available (non-critical): {e}")


# Initialize database on startup (non-blocking)
try:
    setup_database()
except Exception as e:
    logger.warning(f"Database initialization failed: {e}")


# ==================== UTILITY FUNCTIONS ====================
def normalize_features(raw_features):
    """Normalize raw features using fitted scaler"""
    feature_vector = np.array([[raw_features[name] for name in feature_names]])
    return scaler.transform(feature_vector)[0]

def store_prediction_async(ip_address, endpoint, method, payload, anomaly_score, rule_flag, attacks_detected, ml_flag, final_decision, request_data):
    """Store prediction in database in background thread"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO logs 
        (ip_address, endpoint, method, payload_size, anomaly_score, 
         rule_flag, rule_detection, ml_flag, final_decision, 
         attacks_count, failed_attempts, request_count)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(query, (
            ip_address,
            endpoint,
            method,
            len(payload),
            float(anomaly_score),
            int(rule_flag),
            ",".join(attacks_detected) if attacks_detected else None,
            int(ml_flag),
            final_decision,
            len(attacks_detected),
            request_data.get("failed_attempts", 0),
            request_data.get("request_count", 0)
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        logger.info(f"✓ Logged: {ip_address} -> {endpoint} ({final_decision})")
        
    except Exception as e:
        logger.error(f"DB error: {e}", exc_info=True)


# ==================== PREDICTION ENDPOINT ====================
@app.route("/predict", methods=["POST"])
def predict():
    """
    Main prediction endpoint for API security anomaly detection
    Implements hybrid detection: rule-based + ML-based
    """
    try:
        data = request.json
        
        # Extract request information
        ip_address = data.get("ip_address", request.remote_addr)
        endpoint = data.get("endpoint", "/")
        method = data.get("method", "GET")
        payload = data.get("payload", "")
        failed_attempt = data.get("failed_attempt", False)
        
        # Prepare request data for analysis
        request_data = {
            "ip_address": ip_address,
            "endpoint": endpoint,
            "method": method,
            "payload": payload,
            "uri": data.get("uri", ""),
            "query_string": data.get("query_string", ""),
            "failed_attempt": failed_attempt,
            "failed_attempts": data.get("failed_attempts", 0),
            "request_count": data.get("request_count", 0),
        }
        
        # ==================== RULE-BASED DETECTION ====================
        rule_flag, attacks_detected = rule_detector.scan_request(request_data)
        
        # ==================== FEATURE EXTRACTION ====================
        raw_features = feature_extractor.extract_features(request_data)
        
        # ==================== ML-BASED DETECTION ====================
        ml_flag = False
        anomaly_score = 0.0
        
        if model is not None and scaler is not None:
            try:
                # Normalize features
                normalized_features = normalize_features(raw_features)
                
                # Get anomaly score (negative = anomaly, positive = normal)
                anomaly_score = float(model.score_samples(normalized_features.reshape(1, -1))[0])
                
                # Prediction (-1 = anomaly, 1 = normal)
                prediction = model.predict(normalized_features.reshape(1, -1))[0]
                ml_flag = (prediction == -1)
                
            except Exception as e:
                logger.error(f"ML prediction error: {e}")
                ml_flag = False
        
        # ==================== FINAL DECISION (HYBRID) ====================
        # Rule-based flag takes priority (known attacks)
        # If rule detection fails, rely on ML anomaly score
        if rule_flag:
            final_decision = "ATTACK"
            confidence = 0.95
        elif ml_flag:
            final_decision = "ANOMALY"
            confidence = abs(anomaly_score) / 10  # Normalize score
        else:
            final_decision = "NORMAL"
            confidence = 1.0 - (abs(anomaly_score) / 10)
        
        confidence = max(0.0, min(1.0, confidence))
        
        # ==================== STORE IN DATABASE (ASYNC) ====================
        # Store prediction in background thread to avoid blocking
        thread = threading.Thread(
            target=store_prediction_async,
            args=(ip_address, endpoint, method, payload, anomaly_score, 
                  rule_flag, attacks_detected, ml_flag, final_decision, request_data),
            daemon=True
        )
        thread.start()
        
        # ==================== RESPONSE ====================
        return jsonify({
            "ip_address": ip_address,
            "endpoint": endpoint,
            "timestamp": datetime.now().isoformat(),
            "anomaly_score": round(anomaly_score, 4),
            "rule_flag": bool(rule_flag),
            "rule_detection": attacks_detected,
            "ml_flag": bool(ml_flag),
            "final_decision": final_decision,
            "confidence": round(confidence, 4),
            "features_extracted": len(raw_features)
        })
    
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({"error": str(e)}), 500


# ==================== STATISTICS ENDPOINT ====================
@app.route("/stats", methods=["GET"])
def stats():
    """Get comprehensive security statistics"""
    # Default response structure
    default_stats = {
        "total_requests": 0,
        "normal": 0,
        "detection": {
            "attack": 0,
            "anomaly": 0,
            "rule_based": 0,
            "ml_based": 0,
            "hybrid": 0
        },
        "attack_percentage": 0,
        "top_attacker_ip": "N/A",
        "top_attacker_count": 0,
        "top_endpoints": [],
        "avg_anomaly_score": 0,
        "db_status": "disconnected"
    }
    
    if not DB_AVAILABLE:
        default_stats["db_status"] = "database_unavailable"
        return jsonify(default_stats)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Total statistics
        cursor.execute("SELECT COUNT(*) as count FROM logs")
        result = cursor.fetchone()
        total_requests = result["count"] if result else 0
        
        cursor.execute("SELECT COUNT(*) as count FROM logs WHERE final_decision='NORMAL'")
        result = cursor.fetchone()
        normal_count = result["count"] if result else 0
        
        cursor.execute("SELECT COUNT(*) as count FROM logs WHERE final_decision='ATTACK'")
        result = cursor.fetchone()
        attack_count = result["count"] if result else 0
        
        cursor.execute("SELECT COUNT(*) as count FROM logs WHERE final_decision='ANOMALY'")
        result = cursor.fetchone()
        anomaly_count = result["count"] if result else 0
        
        # Rule-based vs ML-based detection
        cursor.execute("SELECT COUNT(*) as count FROM logs WHERE rule_flag=TRUE")
        result = cursor.fetchone()
        rule_detected = result["count"] if result else 0
        
        cursor.execute("SELECT COUNT(*) as count FROM logs WHERE ml_flag=TRUE")
        result = cursor.fetchone()
        ml_detected = result["count"] if result else 0
        
        cursor.execute("SELECT COUNT(*) as count FROM logs WHERE rule_flag=TRUE AND ml_flag=TRUE")
        result = cursor.fetchone()
        hybrid_detected = result["count"] if result else 0
        
        # Attack percentage
        attack_percentage = round((attack_count / total_requests) * 100, 2) if total_requests > 0 else 0
        
        # Top attacker IP
        cursor.execute("""
            SELECT ip_address, COUNT(*) as count
            FROM logs
            WHERE final_decision IN ('ATTACK', 'ANOMALY')
            GROUP BY ip_address
            ORDER BY count DESC
            LIMIT 1
        """)
        top_attacker = cursor.fetchone()
        top_ip = top_attacker["ip_address"] if top_attacker else "N/A"
        top_ip_count = top_attacker["count"] if top_attacker else 0
        
        # Top attacked endpoints
        cursor.execute("""
            SELECT endpoint, COUNT(*) as count
            FROM logs
            WHERE final_decision IN ('ATTACK', 'ANOMALY')
            GROUP BY endpoint
            ORDER BY count DESC
            LIMIT 5
        """)
        top_endpoints = cursor.fetchall()
        
        # Average anomaly score
        cursor.execute("SELECT AVG(anomaly_score) as avg_score FROM logs")
        result = cursor.fetchone()
        avg_score = result["avg_score"] if result else 0
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "total_requests": total_requests,
            "normal": normal_count,
            "detection": {
                "attack": attack_count,
                "anomaly": anomaly_count,
                "rule_based": rule_detected,
                "ml_based": ml_detected,
                "hybrid": hybrid_detected
            },
            "attack_percentage": attack_percentage,
            "top_attacker_ip": top_ip,
            "top_attacker_count": top_ip_count,
            "top_endpoints": [{"endpoint": e["endpoint"], "count": e["count"]} for e in top_endpoints],
            "avg_anomaly_score": round(float(avg_score) if avg_score else 0, 4),
            "db_status": "connected"
        })
    
    except Exception as e:
        logger.error(f"Stats error: {e}")
        default_stats["db_status"] = "error"
        return jsonify(default_stats)


# ==================== RECENT LOGS ENDPOINT ====================
@app.route("/recent-logs", methods=["GET"])
def recent_logs():
    """Get recent API logs with anomaly details"""
    limit = request.args.get("limit", 20, type=int)
    
    if not DB_AVAILABLE:
        return jsonify([])
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT id, timestamp, ip_address, endpoint, method, 
                   anomaly_score, rule_flag, rule_detection, 
                   ml_flag, final_decision, attacks_count
            FROM logs
            ORDER BY timestamp DESC
            LIMIT %s
        """
        
        cursor.execute(query, (limit,))
        logs = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Format logs for frontend
        formatted_logs = []
        for log in logs:
            formatted_logs.append({
                "id": log["id"],
                "timestamp": str(log["timestamp"]),
                "ip_address": log["ip_address"],
                "endpoint": log["endpoint"],
                "method": log["method"],
                "anomaly_score": round(float(log["anomaly_score"]) if log["anomaly_score"] else 0, 4),
                "rule_flag": log["rule_flag"],
                "rule_detection": log["rule_detection"],
                "ml_flag": log["ml_flag"],
                "final_decision": log["final_decision"],
                "attacks_count": log["attacks_count"] or 0
            })
        
        return jsonify(formatted_logs)
    
    except Exception as e:
        logger.error(f"Recent logs error: {e}")
        return jsonify([])


# ==================== ENDPOINT DETAILS ====================
@app.route("/endpoint-analytics", methods=["GET"])
def endpoint_analytics():
    """Get analytics for specific endpoints"""
    if not DB_AVAILABLE:
        return jsonify([])
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get stats per endpoint
        query = """
            SELECT endpoint, COUNT(*) as total_requests,
                   SUM(CASE WHEN final_decision='ATTACK' THEN 1 ELSE 0 END) as attacks,
                   SUM(CASE WHEN final_decision='ANOMALY' THEN 1 ELSE 0 END) as anomalies,
                   AVG(anomaly_score) as avg_anomaly_score
            FROM logs
            GROUP BY endpoint
            ORDER BY attacks DESC
            LIMIT 10
        """
        
        cursor.execute(query)
        endpoints = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        formatted_endpoints = []
        for ep in endpoints:
            total = ep["total_requests"]
            attacks = ep["attacks"] or 0
            anomalies = ep["anomalies"] or 0
            attack_rate = round(((attacks + anomalies) / total * 100), 2) if total > 0 else 0
            
            formatted_endpoints.append({
                "endpoint": ep["endpoint"],
                "total_requests": total,
                "attacks": attacks,
                "anomalies": anomalies,
                "attack_rate": attack_rate,
                "avg_anomaly_score": round(float(ep["avg_anomaly_score"]) if ep["avg_anomaly_score"] else 0, 4)
            })
        
        return jsonify(formatted_endpoints)
    
    except Exception as e:
        logger.error(f"Endpoint analytics error: {e}")
        return jsonify([])


# ==================== DOWNLOAD REPORT ====================
@app.route("/download-report", methods=["GET"])
def download_report():
    """Download comprehensive security report as CSV"""
    if not DB_AVAILABLE:
        return jsonify({"error": "Database not available for report generation"}), 503
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT id, timestamp, ip_address, endpoint, method, 
                   payload_size, anomaly_score, rule_flag, rule_detection, 
                   ml_flag, final_decision, attacks_count, failed_attempts
            FROM logs
            ORDER BY timestamp DESC
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        filename = f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([
                "ID", "Timestamp", "IP Address", "Endpoint", "Method",
                "Payload Size", "Anomaly Score", "Rule Flag", "Rule Detection",
                "ML Flag", "Final Decision", "Attacks Count", "Failed Attempts"
            ])

            # Format rows: ensure timestamp is string and booleans are serializable
            formatted_rows = []
            for r in rows:
                # r expected: (id, timestamp, ip_address, endpoint, method, payload_size, anomaly_score, rule_flag, rule_detection, ml_flag, final_decision, attacks_count, failed_attempts)
                row_list = list(r)
                ts = row_list[1]
                if ts is None:
                    row_list[1] = ""
                else:
                    try:
                        # handle datetime objects
                        row_list[1] = ts.isoformat(sep=' ')
                    except Exception:
                        row_list[1] = str(ts)

                # Normalize boolean-like fields to integers for CSV compatibility
                try:
                    row_list[7] = int(row_list[7]) if row_list[7] is not None else 0
                except Exception:
                    row_list[7] = 1 if str(row_list[7]).lower() in ("true", "1") else 0

                try:
                    row_list[9] = int(row_list[9]) if row_list[9] is not None else 0
                except Exception:
                    row_list[9] = 1 if str(row_list[9]).lower() in ("true", "1") else 0

                formatted_rows.append(row_list)

            writer.writerows(formatted_rows)
        
        cursor.close()
        conn.close()
        
        return send_file(filename, as_attachment=True, mimetype="text/csv")
    
    except Exception as e:
        logger.error(f"Report download error: {e}")
        return jsonify({"error": "Failed to generate report"}), 500


# ==================== HEALTH CHECK ====================
@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "model_loaded": model is not None,
        "timestamp": datetime.now().isoformat()
    })


# ==================== MAIN ====================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("API Security Anomaly Detection System")
    print("="*60)
    print("✓ Hybrid Detection (Rule-Based + ML-Based)")
    print("✓ Isolation Forest Model")
    print("✓ 17 Advanced Behavioral Features")
    print("✓ Production-Grade Architecture")
    print("\nStarting Flask server on http://127.0.0.1:5000")
    print("="*60 + "\n")
    
    app.run(debug=False, port=5000)