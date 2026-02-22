import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import '../styles/StatisticsPanel.css';

const StatisticsPanel = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchStats = async () => {
    const result = await apiService.getStats();
    if (result.success) {
      setStats(result.data);
    }
    setLoading(false);
  };

  if (loading) return <div className="stats-panel"><p>Loading statistics...</p></div>;
  if (!stats) return <div className="stats-panel"><p>No statistics available</p></div>;

  return (
    <div className="stats-panel">
      <h3>System Statistics</h3>
      <div className="stats-grid">
        <div className="stat-card">
          <span className="stat-value">{stats.total_queries || 0}</span>
          <span className="stat-label">Total Queries</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{stats.papers_found || 0}</span>
          <span className="stat-label">Papers Found</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{stats.code_snippets || 0}</span>
          <span className="stat-label">Code Snippets</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{stats.avg_response_time?.toFixed(2) || 0}s</span>
          <span className="stat-label">Avg Response Time</span>
        </div>
      </div>
    </div>
  );
};

export default StatisticsPanel;
