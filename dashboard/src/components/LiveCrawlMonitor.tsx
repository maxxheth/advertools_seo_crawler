import React, { useState, useEffect } from 'react';

type LiveEvent = {
  type?: string;
  event?: string;
  message?: string;
  data?: unknown;
  [key: string]: unknown;
};

function LiveCrawlMonitor() {
  const [events, setEvents] = useState<LiveEvent[]>([]);
  const [isConnected, setIsConnected] = useState<boolean>(false);

  useEffect(() => {
    const wsUrl = process.env.WEBSOCKET_URL || 'ws://localhost:8765';
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      setIsConnected(true);
      addEvent({ type: 'connected', message: 'Connected to WebSocket server' });
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        addEvent(data as LiveEvent);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    ws.onerror = () => {
      setIsConnected(false);
    };

    ws.onclose = () => {
      setIsConnected(false);
    };

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, []);

  const addEvent = (event: LiveEvent) => {
    setEvents(prev => ([event, ...prev].slice(0, 50)));
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-gray-900">Live Monitor</h2>
        <div className="flex items-center">
          <div className={`w-3 h-3 rounded-full mr-2 ${isConnected ? 'bg-success' : 'bg-error'}`}></div>
          <span className="text-sm text-gray-500">{isConnected ? 'Connected' : 'Disconnected'}</span>
        </div>
      </div>

      <div className="space-y-2 max-h-96 overflow-y-auto bg-gray-50 p-4 rounded">
        {events.length > 0 ? (
          events.map((event, idx) => (
            <div key={idx} className="text-sm text-gray-600 font-mono">
              <span className="text-primary-600">[{event.event || event.type}]</span> {JSON.stringify(event.data || event.message)}
            </div>
          ))
        ) : (
          <p className="text-gray-400">Waiting for events...</p>
        )}
      </div>
    </div>
  );
}

export default LiveCrawlMonitor;
