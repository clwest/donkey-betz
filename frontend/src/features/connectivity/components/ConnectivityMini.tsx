/**
 * Connectivity Mini Component
 * 
 * A compact component for testing WebSocket and API connectivity
 * Provides quick health checks and connection testing
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  CheckCircleIcon,
  ExclamationTriangleIcon,
  XCircleIcon,
  ArrowPathIcon,
  SignalIcon
} from '@heroicons/react/24/outline';

import { Card } from '../../../components/common/Card';
import { Button } from '../../../components/common/Button';
import { Badge } from '../../../components/common/Badge';
import { LoadingSpinner } from '../../../components/common/LoadingSpinner';

import { connectWS } from '../../../lib/ws/client';
import { orchHealth } from '../../agent-orchestra/api/orchestra';
import { convertAmericanToDecimal } from '../../odds/api/odds';

interface ConnectivityResult {
  service: string;
  status: 'success' | 'warning' | 'error' | 'testing';
  message: string;
  url?: string;
  latency?: number;
}

export const ConnectivityMini: React.FC = () => {
  const [results, setResults] = useState<ConnectivityResult[]>([]);
  const [testing, setTesting] = useState(false);

  const runConnectivityTests = async () => {
    setTesting(true);
    const testResults: ConnectivityResult[] = [];

    // Test 1: Orchestra Health Check
    try {
      const start = Date.now();
      const health = await orchHealth();
      const latency = Date.now() - start;
      
      if (health?.status === 'healthy') {
        testResults.push({
          service: 'Orchestra API',
          status: 'success',
          message: `Healthy (v${health.version || 'unknown'})`,
          url: import.meta.env.VITE_API_URL,
          latency
        });
      } else {
        testResults.push({
          service: 'Orchestra API',
          status: 'warning',
          message: health?.status || 'Unknown status',
          url: import.meta.env.VITE_API_URL
        });
      }
    } catch (error) {
      testResults.push({
        service: 'Orchestra API',
        status: 'error',
        message: error instanceof Error ? error.message : 'Connection failed',
        url: import.meta.env.VITE_API_URL
      });
    }

    // Test 2: DBAO API (Odds)
    try {
      const start = Date.now();
      await convertAmericanToDecimal(110);
      const latency = Date.now() - start;
      
      testResults.push({
        service: 'DBAO API',
        status: 'success',
        message: 'Odds conversion successful',
        url: import.meta.env.VITE_DBAO_API_URL,
        latency
      });
    } catch (error) {
      testResults.push({
        service: 'DBAO API',
        status: 'error',
        message: error instanceof Error ? error.message : 'Connection failed',
        url: import.meta.env.VITE_DBAO_API_URL
      });
    }

    // Test 3: WebSocket Connection
    try {
      const wsPromise = new Promise<ConnectivityResult>((resolve) => {
        const start = Date.now();
        let resolved = false;

        const wsClient = connectWS({
          base: import.meta.env.VITE_WS_URL || 'ws://localhost:8001',
          path: '/ws/assistant/',
          onOpen: () => {
            if (!resolved) {
              resolved = true;
              const latency = Date.now() - start;
              resolve({
                service: 'WebSocket',
                status: 'success',
                message: 'Connection established',
                url: `${import.meta.env.VITE_WS_URL}/ws/assistant/`,
                latency
              });
              wsClient.close();
            }
          },
          onError: () => {
            if (!resolved) {
              resolved = true;
              resolve({
                service: 'WebSocket',
                status: 'error',
                message: 'Connection failed',
                url: `${import.meta.env.VITE_WS_URL}/ws/assistant/`
              });
            }
          }
        });

        // Timeout after 5 seconds
        setTimeout(() => {
          if (!resolved) {
            resolved = true;
            resolve({
              service: 'WebSocket',
              status: 'error',
              message: 'Connection timeout',
              url: `${import.meta.env.VITE_WS_URL}/ws/assistant/`
            });
            wsClient.close();
          }
        }, 5000);
      });

      const wsResult = await wsPromise;
      testResults.push(wsResult);
    } catch (error) {
      testResults.push({
        service: 'WebSocket',
        status: 'error',
        message: 'Test failed',
        url: `${import.meta.env.VITE_WS_URL}/ws/assistant/`
      });
    }

    setResults(testResults);
    setTesting(false);
  };

  // Run tests on mount
  useEffect(() => {
    runConnectivityTests();
  }, []);

  const getStatusIcon = (status: ConnectivityResult['status']) => {
    switch (status) {
      case 'success':
        return <CheckCircleIcon className="h-4 w-4 text-green-500" />;
      case 'warning':
        return <ExclamationTriangleIcon className="h-4 w-4 text-yellow-500" />;
      case 'error':
        return <XCircleIcon className="h-4 w-4 text-red-500" />;
      case 'testing':
        return <LoadingSpinner size="sm" />;
    }
  };

  const getStatusVariant = (status: ConnectivityResult['status']) => {
    switch (status) {
      case 'success':
        return 'success';
      case 'warning':
        return 'warning';
      case 'error':
        return 'error';
      case 'testing':
        return 'secondary';
    }
  };

  return (
    <Card className="p-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <SignalIcon className="h-5 w-5 text-primary" />
          <h3 className="text-lg font-semibold text-foreground">Connectivity Status</h3>
        </div>
        
        <Button
          variant="outline"
          size="sm"
          onClick={runConnectivityTests}
          disabled={testing}
        >
          {testing ? (
            <LoadingSpinner size="sm" />
          ) : (
            <ArrowPathIcon className="h-4 w-4" />
          )}
          {testing ? 'Testing...' : 'Refresh'}
        </Button>
      </div>

      <div className="space-y-3">
        {results.length === 0 && !testing ? (
          <div className="text-center py-4 text-muted-foreground">
            <p>Click "Refresh" to test connectivity</p>
          </div>
        ) : (
          results.map((result, index) => (
            <motion.div
              key={result.service}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="flex items-center justify-between p-3 bg-muted/30 rounded-lg"
            >
              <div className="flex items-center space-x-3">
                {getStatusIcon(result.status)}
                <div>
                  <p className="text-sm font-medium text-foreground">{result.service}</p>
                  <p className="text-xs text-muted-foreground">{result.message}</p>
                  {result.url && (
                    <p className="text-xs text-muted-foreground font-mono truncate max-w-48">
                      {result.url}
                    </p>
                  )}
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                {result.latency && (
                  <span className="text-xs text-muted-foreground">
                    {result.latency}ms
                  </span>
                )}
                <Badge variant={getStatusVariant(result.status)} size="sm">
                  {result.status}
                </Badge>
              </div>
            </motion.div>
          ))
        )}
      </div>

      <div className="mt-4 pt-4 border-t border-border">
        <div className="grid grid-cols-3 gap-4 text-xs text-muted-foreground">
          <div>
            <span className="font-medium">API:</span>
            <span className="ml-1 font-mono">
              {import.meta.env.VITE_API_URL}
            </span>
          </div>
          <div>
            <span className="font-medium">DBAO:</span>
            <span className="ml-1 font-mono">
              {import.meta.env.VITE_DBAO_API_URL}
            </span>
          </div>
          <div>
            <span className="font-medium">WS:</span>
            <span className="ml-1 font-mono">
              {import.meta.env.VITE_WS_URL}
            </span>
          </div>
        </div>
      </div>
    </Card>
  );
};