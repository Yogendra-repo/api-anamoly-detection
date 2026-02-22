import { useEffect, useState } from "react";
import axios from "axios";
import { GeoHeatmap } from "./GeoHeatmap";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement
} from "chart.js";
import { Pie, Bar } from "react-chartjs-2";
import "./App.css";

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement
);

function App() {
  const [stats, setStats] = useState({
    total_requests: 0,
    normal: 0,
    detection: { attack: 0, anomaly: 0, rule_based: 0, ml_based: 0, hybrid: 0 },
    attack_percentage: 0,
    top_attacker_ip: "N/A",
    top_attacker_count: 0,
    top_endpoints: [],
    avg_anomaly_score: 0,
    db_status: "disconnected"
  });

  const [logs, setLogs] = useState([]);
  const [endpoints, setEndpoints] = useState([]);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [geoAttacks, setGeoAttacks] = useState([]);

  const fetchData = async () => {
    try {
      const [statsRes, logsRes, endpointsRes, geoRes] = await Promise.all([
        axios.get("http://127.0.0.1:5000/stats"),
        axios.get("http://127.0.0.1:5000/recent-logs"),
        axios.get("http://127.0.0.1:5000/endpoint-analytics"),
        axios.get("http://127.0.0.1:5000/geo-attacks").catch(() => ({ data: [] }))
      ]);
      
      setStats(statsRes.data);
      setLogs(logsRes.data || []);
      setEndpoints(endpointsRes.data || []);
      
      const geoData = geoRes.data || [];
      console.log(`[GEO-DEBUG] Received ${geoData.length} locations from backend`);
      if (geoData.length > 0) {
        console.log(`[GEO-DEBUG] Cities: ${geoData.map(g => g.city).join(", ")}`);
        console.log(`[GEO-DEBUG] Sample location:`, geoData[0]);
      }
      setGeoAttacks(geoData);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  useEffect(() => {
    fetchData();
    if (!autoRefresh) return;
    
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, [autoRefresh]);

  // Detection breakdown pie chart
  const detectionPieData = {
    labels: ["Rule-Based", "ML-Based", "Hybrid"],
    datasets: [
      {
        data: [
          stats.detection.rule_based,
          stats.detection.ml_based,
          stats.detection.hybrid
        ],
        backgroundColor: ["#FF9999", "#66BB6A", "#42A5F5"],
        borderColor: ["#FF6B6B", "#4CAF50", "#1E88E5"],
        borderWidth: 2
      }
    ]
  };

  // Decision breakdown pie chart
  const decisionPieData = {
    labels: ["NORMAL", "ATTACK", "ANOMALY"],
    datasets: [
      {
        data: [
          stats.normal,
          stats.detection.attack,
          stats.detection.anomaly
        ],
        backgroundColor: ["#36A2EB", "#FF6384", "#FFCE56"],
        borderColor: ["#1E88E5", "#E53935", "#F57C00"],
        borderWidth: 2
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        position: "bottom",
        labels: { color: "#E0E0E0", font: { size: 12 } }
      }
    }
  };

  const getDecisionColor = (decision) => {
    switch (decision) {
      case "ATTACK":
        return "#ff4757";
      case "ANOMALY":
        return "#ffa502";
      default:
        return "#2ed573";
    }
  };

  const getDecisionBgColor = (decision) => {
    switch (decision) {
      case "ATTACK":
        return "rgba(255, 71, 87, 0.1)";
      case "ANOMALY":
        return "rgba(255, 165, 2, 0.1)";
      default:
        return "rgba(46, 213, 115, 0.1)";
    }
  };

  const getRiskLevel = (percentage) => {
    if (percentage >= 50) return "🔴 CRITICAL";
    if (percentage >= 30) return "🟠 HIGH";
    if (percentage >= 10) return "🟡 MEDIUM";
    return "🟢 LOW";
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-left">
          <h1>🛡️ API Security Dashboard</h1>
          <p className="subtitle">Real-time Threat Detection & Monitoring</p>
        </div>
        <div className="header-right">
          <button
            className={`refresh-btn ${autoRefresh ? "active" : ""}`}
            onClick={() => setAutoRefresh(!autoRefresh)}
            title={autoRefresh ? "Auto-refresh ON" : "Auto-refresh OFF"}
          >
            {autoRefresh ? "🔄 Auto-Refresh ON" : "⏸️ Auto-Refresh OFF"}
          </button>
          <button
            className="refresh-btn manual"
            onClick={fetchData}
            title="Manual refresh"
          >
            🔃 Refresh Now
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        {/* Metrics Cards */}
        <section className="metrics-section">
          <div className="metric-card">
            <div className="metric-icon">📊</div>
            <div className="metric-content">
              <p className="metric-label">Total Requests</p>
              <p className="metric-value">{stats.total_requests}</p>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon">⚠️</div>
            <div className="metric-content">
              <p className="metric-label">Attack Percentage</p>
              <p className="metric-value">{stats.attack_percentage.toFixed(2)}%</p>
              <p className="metric-risk">{getRiskLevel(stats.attack_percentage)}</p>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon">🎯</div>
            <div className="metric-content">
              <p className="metric-label">Top Attacker IP</p>
              <p className="metric-value metric-ip">{stats.top_attacker_ip}</p>
              <p className="metric-count">{stats.top_attacker_count} requests</p>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon">📈</div>
            <div className="metric-content">
              <p className="metric-label">Avg Anomaly Score</p>
              <p className="metric-value">{stats.avg_anomaly_score.toFixed(4)}</p>
              <p className="metric-info">ML Confidence</p>
            </div>
          </div>
        </section>

        {/* Charts Section */}
        <section className="charts-section">
          <div className="chart-container full-width">
            <h2>🌍 Global Attack Heatmap</h2>
            <div style={{fontSize: "12px", color: "#999", marginBottom: "10px", padding: "10px", backgroundColor: "#1a1a1a", borderRadius: "4px"}}>
              📍 Locations on map: <strong>{geoAttacks.length}</strong>
              {geoAttacks.length > 0 && <div style={{marginTop: "5px"}}>Cities: {geoAttacks.map(g => `${g.city}(${g.primary_decision[0]})`).join(", ")}</div>}
            </div>
            <GeoHeatmap attacks={geoAttacks} />
          </div>
          <div className="chart-container">
            <h2>Detection Method Breakdown</h2>
            <Pie data={detectionPieData} options={chartOptions} />
          </div>
          <div className="chart-container">
            <h2>Request Decision Distribution</h2>
            <Pie data={decisionPieData} options={chartOptions} />
          </div>
        </section>

        {/* Detection Counters */}
        <section className="counters-section">
          <div className="counter-box rule-based">
            <div className="counter-header">Rule-Based Detections</div>
            <div className="counter-value">{stats.detection.rule_based}</div>
            <div className="counter-bar">
              <div className="counter-fill" style={{width: `${Math.min(100, (stats.detection.rule_based / Math.max(1, stats.detection.rule_based + stats.detection.ml_based)) * 100)}%`}}></div>
            </div>
          </div>

          <div className="counter-box ml-based">
            <div className="counter-header">ML-Based Detections</div>
            <div className="counter-value">{stats.detection.ml_based}</div>
            <div className="counter-bar">
              <div className="counter-fill" style={{width: `${Math.min(100, (stats.detection.ml_based / Math.max(1, stats.detection.rule_based + stats.detection.ml_based)) * 100)}%`}}></div>
            </div>
          </div>

          <div className="counter-box hybrid">
            <div className="counter-header">Hybrid Detections</div>
            <div className="counter-value">{stats.detection.hybrid}</div>
          </div>

          <div className="counter-box attack">
            <div className="counter-header">🚨 Total Attacks</div>
            <div className="counter-value attack-count">{stats.detection.attack}</div>
          </div>

          <div className="counter-box anomaly">
            <div className="counter-header">⚠️ Total Anomalies</div>
            <div className="counter-value anomaly-count">{stats.detection.anomaly}</div>
          </div>
        </section>

        {/* Activity Log */}
        <section className="activity-section">
          <h2>Recent Activity Log</h2>
          <div className="activity-table">
            <div className="table-header">
              <div className="col col-ip">IP Address</div>
              <div className="col col-endpoint">Endpoint</div>
              <div className="col col-decision">Decision</div>
              <div className="col col-score">Anomaly Score</div>
              <div className="col col-flags">Flags</div>
              <div className="col col-count">Detections</div>
              <div className="col col-time">Time</div>
            </div>
            {logs.length > 0 ? (
              logs.map((log, idx) => (
                <div
                  key={idx}
                  className="table-row"
                  style={{borderLeft: `4px solid ${getDecisionColor(log.final_decision)}`}}
                >
                  <div className="col col-ip">{log.ip_address}</div>
                  <div className="col col-endpoint">{log.endpoint}</div>
                  <div
                    className="col col-decision"
                    style={{
                      backgroundColor: getDecisionBgColor(log.final_decision),
                      color: getDecisionColor(log.final_decision),
                      fontWeight: "600"
                    }}
                  >
                    {log.final_decision}
                  </div>
                  <div className="col col-score">{log.anomaly_score.toFixed(4)}</div>
                  <div className="col col-flags">
                    {log.rule_flag && <span className="flag rule">R</span>}
                    {log.ml_flag && <span className="flag ml">M</span>}
                  </div>
                  <div className="col col-count">{log.attacks_count}</div>
                  <div className="col col-time">
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              ))
            ) : (
              <div className="table-row empty">
                <p>No activity logged yet</p>
              </div>
            )}
          </div>
        </section>

        {/* Endpoint Analytics */}
        <section className="endpoints-section">
          <h2>Endpoint Analytics</h2>
          <div className="endpoints-grid">
            {endpoints.slice(0, 4).map((ep, idx) => (
              <div key={idx} className="endpoint-card">
                <div className="endpoint-name">{ep.endpoint}</div>
                <div className="endpoint-stats">
                  <div className="stat">
                    <span className="stat-label">Total</span>
                    <span className="stat-value">{ep.total_requests}</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Attacks</span>
                    <span className="stat-value attack">{ep.attacks}</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Anomalies</span>
                    <span className="stat-value anomaly">{ep.anomalies}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Download Report Button */}
        <section className="report-section">
          <button
            className="report-btn"
            onClick={() => window.location.href = "http://127.0.0.1:5000/download-report"}
          >
            📥 Download Security Report (CSV)
          </button>
        </section>
      </main>

      {/* Footer */}
      <footer className="footer">
        <p>Database Status: <span className={`status ${stats.db_status}`}>{stats.db_status}</span></p>
        <p>Last Updated: {new Date().toLocaleTimeString()}</p>
      </footer>
    </div>
  );
}

export default App;