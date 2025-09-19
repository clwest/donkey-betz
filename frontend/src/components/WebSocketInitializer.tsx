/**
 * WebSocket Initializer Component
 * Place this at the root of your React app to ensure WebSockets connect properly
 */

import React, { useEffect, useState } from 'react';
import { initializeWebSockets, reconnectAllWebSockets } from '../services/websocket-manager';

interface WebSocketInitializerProps {
  children: React.ReactNode;
  showStatus?: boolean;
}

export const WebSocketInitializer: React.FC<WebSocketInitializerProps> = ({ 
  children, 
  showStatus = true 
}) => {
  const [isReady, setIsReady] = useState(false);
  const [isConnecting, setIsConnecting] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);

  useEffect(() => {
    let mounted = true;
    let retryTimeout: NodeJS.Timeout;

    const checkBackendAndConnect = async () => {
      try {
        // First, check if backend is ready
        const healthResponse = await fetch('http://localhost:8000/api/v1/health/', {
          method: 'GET',
        });

        if (!healthResponse.ok) {
          throw new Error(`Backend not ready: ${healthResponse.status}`);
        }

        const healthData = await healthResponse.json();
        console.log('Backend health:', healthData);

        // If WebSocket is not ready on backend, wait a bit
        if (!healthData.websocket_ready) {
          console.log('WebSocket not ready on backend, waiting...');
          throw new Error('WebSocket not ready on backend');
        }

        // Backend is ready, initialize WebSockets
        console.log('Backend ready, initializing WebSockets...');
        await initializeWebSockets();
        
        if (mounted) {
          setIsReady(true);
          setIsConnecting(false);
          setError(null);
          console.log('✅ WebSockets initialized successfully');
        }
      } catch (err: any) {
        console.error('WebSocket initialization error:', err);
        
        if (mounted) {
          setError(err.message);
          setRetryCount(prev => prev + 1);
          
          // Retry with exponential backoff
          const delay = Math.min(1000 * Math.pow(1.5, retryCount), 10000);
          console.log(`Retrying in ${delay}ms... (attempt ${retryCount + 1})`);
          
          retryTimeout = setTimeout(() => {
            if (mounted && retryCount < 10) {
              checkBackendAndConnect();
            } else if (mounted) {
              setIsConnecting(false);
              setError('Failed to connect after 10 attempts');
            }
          }, delay);
        }
      }
    };

    // Start the connection process
    checkBackendAndConnect();

    // Set up visibility change handler to reconnect when tab becomes visible
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible' && isReady) {
        console.log('Tab became visible, checking WebSocket connections...');
        reconnectAllWebSockets().catch(console.error);
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    // Set up online/offline handlers
    const handleOnline = () => {
      console.log('Network online, reconnecting WebSockets...');
      if (isReady) {
        reconnectAllWebSockets().catch(console.error);
      } else {
        checkBackendAndConnect();
      }
    };

    const handleOffline = () => {
      console.log('Network offline');
      setError('Network connection lost');
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      mounted = false;
      clearTimeout(retryTimeout);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []); // Only run once on mount

  // Manual retry function
  const handleRetry = () => {
    setIsConnecting(true);
    setError(null);
    setRetryCount(0);
    window.location.reload(); // Simple solution - reload the page
  };

  // Show loading state while connecting
  if (isConnecting && showStatus) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-muted/5 dark:bg-background">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-700 dark:text-muted-foreground mb-2">
            Connecting to Backend...
          </h2>
          <p className="text-sm text-muted-foreground dark:text-muted-foreground">
            Attempt {retryCount + 1}
          </p>
        </div>
      </div>
    );
  }

  // Show error state if failed to connect
  if (error && !isConnecting && showStatus) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-muted/5 dark:bg-background">
        <div className="text-center max-w-md">
          <div className="text-red-500 mb-4">
            <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-700 dark:text-muted-foreground mb-2">
            Connection Failed
          </h2>
          <p className="text-sm text-muted-foreground dark:text-muted-foreground mb-4">
            {error}
          </p>
          <button
            onClick={handleRetry}
            className="px-4 py-2 bg-blue-500 text-foreground rounded hover:bg-blue-600 transition-colors"
          >
            Retry Connection
          </button>
          <p className="text-xs text-muted-foreground mt-4">
            Make sure the backend is running: make unified-dev
          </p>
        </div>
      </div>
    );
  }

  // Render children when ready
  return <>{children}</>;
};

// Export a higher-order component for wrapping the entire app
export const withWebSocketInitializer = <P extends object>(
  Component: React.ComponentType<P>,
  showStatus: boolean = true
): React.FC<P> => {
  return (props: P) => (
    <WebSocketInitializer showStatus={showStatus}>
      <Component {...props} />
    </WebSocketInitializer>
  );
};

// Status indicator component (optional, can be placed anywhere in the app)
export const WebSocketStatusIndicator: React.FC = () => {
  const [status, setStatus] = useState<'connecting' | 'connected' | 'disconnected'>('connecting');

  useEffect(() => {
    // This would connect to your WebSocket manager to get real status
    // For now, just a simple implementation
    const checkStatus = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/health/');
        if (response.ok) {
          const data = await response.json();
          setStatus(data.websocket_ready ? 'connected' : 'disconnected');
        } else {
          setStatus('disconnected');
        }
      } catch {
        setStatus('disconnected');
      }
    };

    checkStatus();
    const interval = setInterval(checkStatus, 5000);

    return () => clearInterval(interval);
  }, []);

  const statusColors = {
    connecting: 'bg-yellow-500',
    connected: 'bg-green-500',
    disconnected: 'bg-red-500'
  };

  return (
    <div className="fixed bottom-4 left-4 flex items-center space-x-2 bg-white dark:bg-card rounded-lg shadow-lg px-3 py-2">
      <div className={`w-2 h-2 rounded-full ${statusColors[status]} animate-pulse`} />
      <span className="text-xs text-gray-600 dark:text-muted-foreground">
        WebSocket: {status}
      </span>
    </div>
  );
};
