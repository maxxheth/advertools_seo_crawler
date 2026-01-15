import React, { useState, useEffect } from 'react';
import ReportSelector from './components/ReportSelector';
import LiveCrawlMonitor from './components/LiveCrawlMonitor';
import MetricsCard from './components/MetricsCard';

import './index.css';

function App() {
  const [selectedReport, setSelectedReport] = useState(null);
  const [reports, setReports] = useState([]);
  const [monitoring, setMonitoring] = useState(false);

  useEffect(() => {
    // Load available reports
    loadReports();

    // Setup WebSocket if watch mode is enabled
    const wsUrl = process.env.WEBSOCKET_URL || 'ws://localhost:8765';
    try {
      const ws = new WebSocket(wsUrl);
      
      ws.onopen = () => {
        console.log('Connected to WebSocket');
        setMonitoring(true);
      };
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('WebSocket message:', data);
      };
      
      ws.onerror = (error) => {
        console.log('WebSocket error (expected in dev):', error);
      };
      
      return () => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.close();
        }
      };
    } catch (error) {
      console.log('WebSocket connection not available');
    }
  }, []);

  const loadReports = async () => {
    try {
      const response = await fetch('/api/reports');
      const data = await response.json();
      setReports(data);
    } catch (error) {
      console.log('Could not load reports:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-3xl font-bold text-gray-900">Advertools Dashboard</h1>
          <p className="text-gray-500 mt-2">SEO Crawling & Analysis Reports</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Monitoring Status */}
        {monitoring && (
          <div className="mb-6">
            <LiveCrawlMonitor />
          </div>
        )}

        {/* Report Selector */}
        <div className="mb-6">
          <ReportSelector 
            reports={reports}
            selectedReport={selectedReport}
            onReportSelect={setSelectedReport}
            onRefresh={loadReports}
          />
        </div>

        {/* Metrics Grid */}
        {selectedReport ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries(selectedReport.metrics || {}).map(([key, value]) => (
              <MetricsCard key={key} title={key} value={value} />
            ))}
          </div>
        ) : (
          <div className="text-center text-gray-500 py-12">
            <p>Select a report to view metrics</p>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
