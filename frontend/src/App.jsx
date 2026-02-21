import { useEffect, useState } from "react";
import axios from "axios";
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

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement
);

function App() {
  const [stats, setStats] = useState({});
  const [logs, setLogs] = useState([]);

  const fetchData = async () => {
    const statsRes = await axios.get("http://127.0.0.1:5000/stats");
    const logsRes = await axios.get("http://127.0.0.1:5000/recent-logs");

    setStats(statsRes.data);
    setLogs(logsRes.data);
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const pieData = {
    labels: ["Normal", "Attack"],
    datasets: [
      {
        data: [stats.normal || 0, stats.attack || 0],
        backgroundColor: ["#36A2EB", "#FF6384"],
      },
    ],
  };

  const barData = {
    labels: ["Normal", "Attack"],
    datasets: [
      {
        label: "Request Count",
        data: [stats.normal || 0, stats.attack || 0],
        backgroundColor: ["#36A2EB", "#FF6384"],
      },
    ],
  };

  return (
    <div style={{ background: "#111827", color: "white", minHeight: "100vh", padding: "30px" }}>
      <h1>AI-Powered API Threat Monitoring Dashboard</h1>

      <div style={{ display: "flex", gap: "20px", marginTop: "20px" }}>
        <div className="card">Total Requests: {stats.total_requests}</div>
        <div className="card">Attack %: {stats.attack_percentage}%</div>
        <div className="card">Top Attacker: {stats.top_attacker_ip}</div>
      </div>

      <div style={{ display: "flex", marginTop: "40px", gap: "40px" }}>
        <div style={{ width: "400px" }}>
          <Pie data={pieData} />
        </div>
        <div style={{ width: "500px" }}>
          <Bar data={barData} />
        </div>
      </div>

      <h2 style={{ marginTop: "50px" }}>Recent Activity</h2>
      <table style={{ width: "100%", marginTop: "10px", borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th>IP</th>
            <th>Prediction</th>
            <th>Timestamp</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log, index) => (
            <tr key={index}>
              <td>{log.ip_address}</td>
              <td style={{ color: log.prediction === "attack" ? "red" : "lightgreen" }}>
                {log.prediction}
              </td>
              <td>{log.timestamp}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <div style={{ marginTop: "30px" }}>
        <a href="http://127.0.0.1:5000/download-report" style={{
          padding: "10px 20px",
          background: "#36A2EB",
          color: "white",
          textDecoration: "none"
        }}>
          Download Full Report
        </a>
      </div>

      <style>
        {`
        .card {
          background: #1f2937;
          padding: 20px;
          border-radius: 10px;
          font-size: 18px;
          flex: 1;
          text-align: center;
        }
        table, th, td {
          border: 1px solid #374151;
          padding: 10px;
        }
        `}
      </style>
    </div>
  );
}

export default App;