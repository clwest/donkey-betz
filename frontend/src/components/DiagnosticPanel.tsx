import React, { useState, useEffect } from 'react';

interface DiagnosticData {
  timestamp: string;
  spider_system: any;
  income_builder: any;
  monetization_engine: any;
  websocket_consumers: any;
  cache_data: any;
  redis_data: any;
  database_stats: any;
  agent_registry: any;
  errors: string[];
  summary: {
    total_errors: number;
    systems_checked: number;
    systems_operational: number;
    reality_score: string;
    recommendations: any[];
  };
}

const DiagnosticPanel: React.FC = () => {
  const [diagnosticData, setDiagnosticData] = useState<DiagnosticData | null>(null);
  const [wsStatus, setWsStatus] = useState<string>('disconnected');
  const [wsMessages, setWsMessages] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('overview');

  // WebSocket connection
  const [ws, setWs] = useState<WebSocket | null>(null);

  // Fetch diagnostic data
  const fetchDiagnostics = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/api/diagnostics/');
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      setDiagnosticData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch diagnostics');
    } finally {
      setLoading(false);
    }
  };

  // Connect WebSocket
  const connectWebSocket = () => {
    if (ws) ws.close();

    const websocket = new WebSocket('ws://localhost:8000/ws/decision-command/');

    websocket.onopen = () => {
      setWsStatus('connected');
      console.log('WebSocket connected');
    };

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setWsMessages((prev) => [...prev.slice(-9), { timestamp: new Date().toISOString(), data }]);
    };

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
      setWsStatus('error');
    };

    websocket.onclose = () => {
      setWsStatus('disconnected');
    };

    setWs(websocket);
  };

  // Test WebSocket
  const testWebSocket = () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      const testMessage = {
        action: 'analyze_opportunities',
        profile: {
          skills: ['Python', 'Django', 'React'],
          skill_level: 'intermediate',
          available_hours: 20,
        },
      };
      ws.send(JSON.stringify(testMessage));
    }
  };

  // Test Spider Network
  const testSpiders = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/diagnostics/test-spiders/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          profile: {
            skills: ['Python', 'Django'],
            skill_level: 'intermediate',
            available_hours: 20,
          },
        }),
      });
      const data = await response.json();
      console.log('Spider test result:', data);
      alert(`Spider test: ${data.success ? 'Success' : 'Failed'}. Found ${data.opportunities_found || 0} opportunities`);
    } catch (err) {
      console.error('Spider test error:', err);
    }
  };

  // Test Income Builder
  const testIncomeBuilder = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/diagnostics/test-income-builder/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          skills: ['Python', 'Django'],
          skill_level: 'intermediate',
          available_hours: 20,
        }),
      });
      const data = await response.json();
      console.log('Income builder test result:', data);
      alert(`Income builder test: ${data.success ? 'Success' : 'Failed'}. Found ${data.opportunities_found || 0} opportunities`);
    } catch (err) {
      console.error('Income builder test error:', err);
    }
  };

  useEffect(() => {
    fetchDiagnostics();
    connectWebSocket();

    return () => {
      if (ws) ws.close();
    };
  }, []);

  const renderSystemStatus = (system: any, name: string) => {
    const isError = system?.status === 'error';
    const statusColor = isError ? 'text-red-500' : 'text-green-500';
    const statusIcon = isError ? '❌' : '✅';

    return (
      <div className="bg-gray-800 p-4 rounded-lg mb-4">
        <h3 className="text-lg font-bold mb-2 flex items-center">
          <span className={statusColor}>{statusIcon}</span>
          <span className="ml-2">{name}</span>
        </h3>
        {isError ? (
          <div className="text-red-400">
            <p>Error: {system.error}</p>
            {system.traceback && (
              <details className="mt-2">
                <summary className="cursor-pointer">View Traceback</summary>
                <pre className="text-xs mt-2 overflow-auto">{system.traceback}</pre>
              </details>
            )}
          </div>
        ) : (
          <div className="text-gray-300">
            <pre className="text-xs overflow-auto">{JSON.stringify(system, null, 2)}</pre>
          </div>
        )}
      </div>
    );
  };

  if (loading) return <div className="text-center p-8">Loading diagnostics...</div>;
  if (error) return <div className="text-red-500 p-8">Error: {error}</div>;
  if (!diagnosticData) return <div className="p-8">No diagnostic data available</div>;

  return (
    <div className="bg-gray-900 text-white min-h-screen p-4">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-6 text-cyan-400">🔧 System Diagnostic Panel</h1>

        {/* Control Buttons */}
        <div className="bg-gray-800 p-4 rounded-lg mb-6 flex gap-4 flex-wrap">
          <button
            onClick={fetchDiagnostics}
            className="bg-cyan-600 hover:bg-cyan-700 px-4 py-2 rounded transition"
          >
            Refresh Diagnostics
          </button>
          <button
            onClick={connectWebSocket}
            className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded transition"
          >
            Reconnect WebSocket
          </button>
          <button
            onClick={testWebSocket}
            disabled={wsStatus !== 'connected'}
            className={`${
              wsStatus === 'connected'
                ? 'bg-blue-600 hover:bg-blue-700'
                : 'bg-gray-600 cursor-not-allowed'
            } px-4 py-2 rounded transition`}
          >
            Test WebSocket Message
          </button>
          <button
            onClick={testSpiders}
            className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded transition"
          >
            Test Spiders
          </button>
          <button
            onClick={testIncomeBuilder}
            className="bg-yellow-600 hover:bg-yellow-700 px-4 py-2 rounded transition"
          >
            Test Income Builder
          </button>
        </div>

        {/* Summary Section */}
        <div className="bg-gray-800 p-6 rounded-lg mb-6">
          <h2 className="text-2xl font-bold mb-4 text-cyan-400">System Summary</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-gray-700 p-4 rounded">
              <div className="text-3xl font-bold text-cyan-400">{diagnosticData.summary.reality_score}</div>
              <div className="text-sm text-gray-400">Reality Score</div>
            </div>
            <div className="bg-gray-700 p-4 rounded">
              <div className="text-3xl font-bold text-green-400">{diagnosticData.summary.systems_operational}</div>
              <div className="text-sm text-gray-400">Systems Operational</div>
            </div>
            <div className="bg-gray-700 p-4 rounded">
              <div className="text-3xl font-bold text-red-400">{diagnosticData.summary.total_errors}</div>
              <div className="text-sm text-gray-400">Errors</div>
            </div>
            <div className="bg-gray-700 p-4 rounded">
              <div className={`text-3xl font-bold ${wsStatus === 'connected' ? 'text-green-400' : 'text-red-400'}`}>
                {wsStatus === 'connected' ? '✅' : '❌'}
              </div>
              <div className="text-sm text-gray-400">WebSocket</div>
            </div>
          </div>
        </div>

        {/* Recommendations */}
        {diagnosticData.summary.recommendations.length > 0 && (
          <div className="bg-red-900/30 border border-red-500 p-4 rounded-lg mb-6">
            <h3 className="text-xl font-bold mb-3 text-red-400">⚠️ Recommendations</h3>
            {diagnosticData.summary.recommendations.map((rec: any, idx: number) => (
              <div key={idx} className="mb-3 p-3 bg-gray-800 rounded">
                <div className="flex items-center mb-1">
                  <span
                    className={`px-2 py-1 rounded text-xs font-bold ${
                      rec.priority === 'CRITICAL'
                        ? 'bg-red-600'
                        : rec.priority === 'HIGH'
                        ? 'bg-orange-600'
                        : 'bg-yellow-600'
                    }`}
                  >
                    {rec.priority}
                  </span>
                  <span className="ml-3 font-semibold">{rec.issue}</span>
                </div>
                <div className="text-sm text-gray-400 mt-1">Fix: {rec.fix}</div>
              </div>
            ))}
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-2 mb-6">
          {['overview', 'spiders', 'websocket', 'data'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 rounded transition ${
                activeTab === tab
                  ? 'bg-cyan-600 text-white'
                  : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="bg-gray-800 p-6 rounded-lg">
          {activeTab === 'overview' && (
            <div>
              <h2 className="text-2xl font-bold mb-4 text-cyan-400">System Overview</h2>
              {renderSystemStatus(diagnosticData.spider_system, 'Spider System')}
              {renderSystemStatus(diagnosticData.income_builder, 'Income Builder')}
              {renderSystemStatus(diagnosticData.monetization_engine, 'Monetization Engine')}
              {renderSystemStatus(diagnosticData.database_stats, 'Database')}
              {renderSystemStatus(diagnosticData.redis_data, 'Redis')}
            </div>
          )}

          {activeTab === 'spiders' && (
            <div>
              <h2 className="text-2xl font-bold mb-4 text-cyan-400">Spider Network</h2>
              {renderSystemStatus(diagnosticData.spider_system, 'Spider Orchestrator')}
              {diagnosticData.spider_system?.sample_opportunities && (
                <div className="mt-4">
                  <h3 className="text-lg font-bold mb-2">Sample Opportunities</h3>
                  <pre className="text-xs overflow-auto bg-gray-700 p-4 rounded">
                    {JSON.stringify(diagnosticData.spider_system.sample_opportunities, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          )}

          {activeTab === 'websocket' && (
            <div>
              <h2 className="text-2xl font-bold mb-4 text-cyan-400">WebSocket Messages</h2>
              <div className="mb-4">
                <span
                  className={`px-3 py-1 rounded font-bold ${
                    wsStatus === 'connected'
                      ? 'bg-green-600'
                      : wsStatus === 'error'
                      ? 'bg-red-600'
                      : 'bg-gray-600'
                  }`}
                >
                  Status: {wsStatus}
                </span>
              </div>
              <div className="bg-gray-700 p-4 rounded max-h-96 overflow-y-auto">
                {wsMessages.length === 0 ? (
                  <p className="text-gray-400">No messages received yet. Click "Test WebSocket Message" to send one.</p>
                ) : (
                  wsMessages.map((msg, idx) => (
                    <div key={idx} className="mb-4 p-3 bg-gray-800 rounded">
                      <div className="text-xs text-gray-500 mb-1">{msg.timestamp}</div>
                      <pre className="text-xs overflow-auto">{JSON.stringify(msg.data, null, 2)}</pre>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {activeTab === 'data' && (
            <div>
              <h2 className="text-2xl font-bold mb-4 text-cyan-400">Raw Diagnostic Data</h2>
              <pre className="text-xs overflow-auto bg-gray-700 p-4 rounded max-h-96">
                {JSON.stringify(diagnosticData, null, 2)}
              </pre>
            </div>
          )}
        </div>

        {/* Errors Section */}
        {diagnosticData.errors.length > 0 && (
          <div className="mt-6 bg-red-900/30 border border-red-500 p-4 rounded-lg">
            <h3 className="text-xl font-bold mb-3 text-red-400">System Errors</h3>
            <ul className="list-disc list-inside text-red-300">
              {diagnosticData.errors.map((error, idx) => (
                <li key={idx} className="mb-1">
                  {error}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default DiagnosticPanel;