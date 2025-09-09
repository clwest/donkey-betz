import { useState, useEffect } from 'react';
import { Card } from '../../../common/Card';
import { Badge } from '../../../common/Badge';
import { Button } from '../../../common/Button';
import { probeAPIHealth, probeCORSPreflight, type HealthProbeResult, type CORSProbeResult } from '../api/health';
import { useWSProbe } from '../api/useWSProbe';

interface ProbeRowProps {
  title: string;
  description: string;
  status: 'success' | 'error' | 'warning' | 'loading';
  message: string;
  hint?: string;
  responseTime?: number;
  actions?: React.ReactNode;
}

function ProbeRow({ title, description, status, message, hint, responseTime, actions }: ProbeRowProps) {
  const getBadgeVariant = (status: string) => {
    switch (status) {
      case 'success': return 'success';
      case 'error': return 'error';
      case 'warning': return 'warning';
      default: return 'info';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'success': return 'OK';
      case 'error': return 'FAIL';
      case 'warning': return 'WARN';
      case 'loading': return '...';
      default: return 'UNKNOWN';
    }
  };

  return (
    <div className="flex items-center justify-between py-4 border-b border-gray-800 last:border-b-0">
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-3 mb-1">
          <h3 className="text-sm font-medium text-gray-100">{title}</h3>
          <Badge variant={getBadgeVariant(status)} size="sm">
            {getStatusText(status)}
          </Badge>
          {responseTime && (
            <span className="text-xs text-gray-500">
              {responseTime}ms
            </span>
          )}
        </div>
        <p className="text-xs text-gray-400 mb-1">{description}</p>
        <p className={`text-sm ${
          status === 'error' ? 'text-red-400' : 
          status === 'warning' ? 'text-yellow-400' : 
          'text-gray-300'
        }`}>
          {message}
        </p>
        {hint && (
          <p className="text-xs text-blue-400 mt-1 italic">
            💡 {hint}
          </p>
        )}
      </div>
      
      {actions && (
        <div className="flex items-center gap-2 ml-4">
          {actions}
        </div>
      )}
    </div>
  );
}

export function ConnectivityPanel() {
  const [healthResult, setHealthResult] = useState<HealthProbeResult | null>(null);
  const [corsResult, setCorsResult] = useState<CORSProbeResult | null>(null);
  const [isProbing, setIsProbing] = useState(false);
  
  const wsProbe = useWSProbe();

  const runAPIProbes = async () => {
    setIsProbing(true);
    try {
      const [health, cors] = await Promise.all([
        probeAPIHealth(),
        probeCORSPreflight()
      ]);
      
      setHealthResult(health);
      setCorsResult(cors);
    } catch (error) {
      console.error('Error running probes:', error);
    } finally {
      setIsProbing(false);
    }
  };

  const runAllProbes = async () => {
    // Run API probes
    await runAPIProbes();
    
    // Connect WebSocket if not already connected
    if (wsProbe.result.status === 'disconnected') {
      wsProbe.connect();
    }
  };

  // Auto-run probes on component mount
  useEffect(() => {
    runAllProbes();
  }, []);

  const getHealthStatus = () => {
    if (isProbing) return 'loading';
    if (!healthResult) return 'error';
    return healthResult.success ? 'success' : 'error';
  };

  const getCorsStatus = () => {
    if (isProbing) return 'loading';
    if (!corsResult) return 'error';
    if (!corsResult.success) return 'error';
    return corsResult.xOrchestratorAllowed ? 'success' : 'warning';
  };

  const getWSStatus = () => {
    switch (wsProbe.result.status) {
      case 'connected': return wsProbe.result.success ? 'success' : 'warning';
      case 'connecting': return 'loading';
      case 'error': return 'error';
      default: return 'error';
    }
  };

  const getCorsHint = () => {
    if (!corsResult) return undefined;
    if (!corsResult.success) return 'CORS preflight request failed - check server configuration';
    if (!corsResult.xOrchestratorAllowed) return 'x-orchestrator header not in Access-Control-Allow-Headers';
    return undefined;
  };

  const getWSHint = () => {
    if (wsProbe.result.status === 'error') {
      return 'Check that WebSocket server is running and VITE_WS_URL is configured correctly';
    }
    if (wsProbe.result.status === 'disconnected') {
      return 'Click Connect to establish WebSocket connection';
    }
    return undefined;
  };

  return (
    <Card className="max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-gray-100 mb-1">
            Connectivity Panel
          </h2>
          <p className="text-sm text-gray-400">
            Monitor API health, CORS configuration, and WebSocket connectivity
          </p>
        </div>
        
        <Button
          onClick={runAllProbes}
          loading={isProbing}
          variant="secondary"
          size="sm"
        >
          Re-run Probes
        </Button>
      </div>

      <div className="space-y-0">
        <ProbeRow
          title="API Health"
          description="Basic connectivity to the backend API"
          status={getHealthStatus()}
          message={healthResult?.message || 'Checking API health...'}
          responseTime={healthResult?.responseTime}
        />

        <ProbeRow
          title="CORS Preflight"
          description="Cross-Origin Resource Sharing configuration"
          status={getCorsStatus()}
          message={corsResult?.message || 'Checking CORS preflight...'}
          hint={getCorsHint()}
          responseTime={corsResult?.responseTime}
        />

        <ProbeRow
          title="WebSocket"
          description="Real-time bidirectional communication"
          status={getWSStatus()}
          message={wsProbe.result.message}
          hint={getWSHint()}
          responseTime={wsProbe.result.responseTime}
          actions={
            <div className="flex gap-2">
              {wsProbe.result.status === 'connected' ? (
                <>
                  <Button
                    onClick={wsProbe.sendPing}
                    variant="ghost"
                    size="sm"
                  >
                    Ping
                  </Button>
                  <Button
                    onClick={wsProbe.disconnect}
                    variant="ghost"
                    size="sm"
                  >
                    Close
                  </Button>
                </>
              ) : (
                <>
                  <Button
                    onClick={wsProbe.connect}
                    variant="secondary"
                    size="sm"
                    disabled={wsProbe.result.status === 'connecting'}
                    loading={wsProbe.result.status === 'connecting'}
                  >
                    Connect
                  </Button>
                  {wsProbe.result.status === 'error' && (
                    <Button
                      onClick={wsProbe.reconnect}
                      variant="ghost"
                      size="sm"
                    >
                      Reconnect
                    </Button>
                  )}
                </>
              )}
            </div>
          }
        />
      </div>

      {/* Environment Information */}
      <div className="mt-6 pt-6 border-t border-gray-800">
        <h3 className="text-sm font-medium text-gray-100 mb-3">Environment Configuration</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div>
            <span className="text-gray-400">API URL:</span>
            <span className="ml-2 text-gray-300 font-mono">
              {import.meta.env.VITE_API_URL || 'http://localhost:8001/api'}
            </span>
          </div>
          <div>
            <span className="text-gray-400">WebSocket URL:</span>
            <span className="ml-2 text-gray-300 font-mono">
              {import.meta.env.VITE_WS_URL || 'ws://localhost:8001'}
            </span>
          </div>
          <div>
            <span className="text-gray-400">Current Origin:</span>
            <span className="ml-2 text-gray-300 font-mono">
              {window.location.origin}
            </span>
          </div>
          <div>
            <span className="text-gray-400">Last Updated:</span>
            <span className="ml-2 text-gray-300">
              {new Date().toLocaleTimeString()}
            </span>
          </div>
        </div>
      </div>
    </Card>
  );
}