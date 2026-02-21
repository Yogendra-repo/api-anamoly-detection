from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import joblib
import mysql.connector
import numpy as np
import csv

app = Flask(__name__)
CORS(app)

model = joblib.load("model.pkl")

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Rashmika@143",  # 🔴 CHANGE THIS
        database="api_security"
    )

# =========================
# PREDICT ENDPOINT
# =========================
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.json

        features = np.array([[
            data["request_count"],
            data["payload_length"],
            data["special_char_count"],
            data["failed_attempts"]
        ]])

        prediction = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]
        confidence = float(max(probabilities))

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO logs 
        (ip_address, request_count, payload_length, special_char_count, failed_attempts, prediction)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        cursor.execute(query, (
            data.get("ip_address", "unknown"),
            data["request_count"],
            data["payload_length"],
            data["special_char_count"],
            data["failed_attempts"],
            prediction
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "prediction": prediction,
            "confidence": round(confidence, 2)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================
# STATS ENDPOINT
# =========================
@app.route("/stats", methods=["GET"])
def stats():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM logs")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM logs WHERE prediction='normal'")
    normal = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM logs WHERE prediction='attack'")
    attack = cursor.fetchone()[0]

    attack_percentage = round((attack / total) * 100, 2) if total > 0 else 0

    cursor.execute("""
        SELECT ip_address, COUNT(*) as count
        FROM logs
        GROUP BY ip_address
        ORDER BY count DESC
        LIMIT 1
    """)
    top_attacker = cursor.fetchone()
    top_ip = top_attacker[0] if top_attacker else "N/A"

    cursor.close()
    conn.close()

    return jsonify({
        "total_requests": total,
        "normal": normal,
        "attack": attack,
        "attack_percentage": attack_percentage,
        "top_attacker_ip": top_ip
    })


# =========================
# RECENT LOGS
# =========================
@app.route("/recent-logs", methods=["GET"])
def recent_logs():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT ip_address, prediction, timestamp
        FROM logs
        ORDER BY timestamp DESC
        LIMIT 10
    """)

    logs = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(logs)


# =========================
# DOWNLOAD REPORT
# =========================
@app.route("/download-report", methods=["GET"])
def download_report():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM logs")
    rows = cursor.fetchall()

    filename = "report.csv"

    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "id", "ip_address", "request_count",
            "payload_length", "special_char_count",
            "failed_attempts", "prediction", "timestamp"
        ])
        writer.writerows(rows)

    cursor.close()
    conn.close()

    return send_file(filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)