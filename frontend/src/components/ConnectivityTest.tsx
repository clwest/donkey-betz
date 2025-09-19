import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { CheckCircle, XCircle, Loader2, RefreshCw, Wifi, WifiOff, AlertCircle } from 'lucide-react';
import { API_CONFIG, apiRequest } from '@/config/api.config';

interface TestResult {
  name: string;
  endpoint: string;
  status: 'pending' | 'testing' | 'success' | 'error';
  message?: string;
  data?: any;
  responseTime?: number;
}

export function ConnectivityTest() {
  const [testResults, setTestResults] = useState<TestResult[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [overallStatus, setOverallStatus] = useState<'idle' | 'running' | 'success' | 'partial' | 'failed'>('idle');
  const [wsStatus, setWsStatus] = useState<'disconnected' | 'connecting' | 'connected' | 'error'>('disconnected');

  // Define all tests
  const tests: Omit<TestResult, 'status' | 'responseTime'>[] = [
    {
      name: 'Root API',
      endpoint: '/api/',
      message: 'Testing API base connectivity'
    },
    {
      name: 'API v1',
      endpoint: '/api/v1/',
      message: 'Testing v1 API endpoint'
    },
    {
      name: 'Agent Templates',
      endpoint: API_CONFIG.endpoints.agents.templates,
      message: 'Loading 150 agent templates'
    },
    {
      name: 'Agent Execute (OPTIONS)',
      endpoint: API_CONFIG.endpoints.agents.execute,
      message: 'Testing agent execution endpoint'
    },
    {
      name: 'Agent Executions',
      endpoint: API_CONFIG.endpoints.agents.executions,
      message: 'Fetching execution history'
    },
    {
      name: 'Health Check',
      endpoint: '/api/v1/health/',
      message: 'Checking system health'
    }
  ];

  const runTests = async () => {
    setIsRunning(true);
    setOverallStatus('running');
    
    // Initialize all tests as pending
    const initialResults = tests.map(test => ({
      ...test,
      status: 'pending' as const
    }));
    setTestResults(initialResults);

    let successCount = 0;
    let errorCount = 0;

    // Run tests sequentially
    for (let i = 0; i < tests.length; i++) {
      const test = tests[i];
      
      // Update status to testing
      setTestResults(prev => prev.map((t, idx) => 
        idx === i ? { ...t, status: 'testing' } : t
      ));

      const startTime = Date.now();
      
      try {
        // Special handling for execute endpoint (expects POST)
        let response;
        if (test.endpoint.includes('execute')) {
          // Test with OPTIONS first to check CORS
          response = await fetch(`${API_CONFIG.BASE_URL}${test.endpoint}`, {
            method: 'OPTIONS',
            headers: {
              'Authorization': `Token ${API_CONFIG.AUTH_TOKEN}`
            }
          });
          
          // Mark as success if OPTIONS works (even if 405 for wrong method)
          const success = response.ok || response.status === 405;
          
          setTestResults(prev => prev.map((t, idx) => 
            idx === i ? { 
              ...t, 
              status: success ? 'success' : 'error',
              message: success ? `Endpoint available (Status: ${response.status})` : `Failed: ${response.statusText}`,
              responseTime: Date.now() - startTime
            } : t
          ));
          
          if (success) successCount++;
          else errorCount++;
        } else {
          // Normal GET request
          response = await apiRequest(test.endpoint, { method: 'GET' });
          
          setTestResults(prev => prev.map((t, idx) => 
            idx === i ? { 
              ...t, 
              status: 'success',
              message: 'Connection successful',
              data: response,
              responseTime: Date.now() - startTime
            } : t
          ));
          
          successCount++;
        }
      } catch (error) {
        errorCount++;
        setTestResults(prev => prev.map((t, idx) => 
          idx === i ? { 
            ...t, 
            status: 'error',
            message: error instanceof Error ? error.message : 'Unknown error',
            responseTime: Date.now() - startTime
          } : t
        ));
      }

      // Small delay between tests
      await new Promise(resolve => setTimeout(resolve, 100));
    }

    // Determine overall status
    if (errorCount === 0) {
      setOverallStatus('success');
    } else if (successCount > 0) {
      setOverallStatus('partial');
    } else {
      setOverallStatus('failed');
    }
    
    setIsRunning(false);
  };

  // Test WebSocket connection
  const testWebSocket = () => {
    setWsStatus('connecting');
    
    try {
      const ws = new WebSocket(`${API_CONFIG.WS_URL}/ws/assistant/`);
      
      ws.onopen = () => {
        console.log('WebSocket connected');
        setWsStatus('connected');
        
        // Send test message
        ws.send(JSON.stringify({ type: 'ping' }));
        
        // Close after 2 seconds
        setTimeout(() => {
          ws.close();
        }, 2000);
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setWsStatus('error');
      };
      
      ws.onclose = () => {
        console.log('WebSocket closed');
        if (wsStatus !== 'error') {
          setWsStatus('disconnected');
        }
      };
      
      ws.onmessage = (event) => {
        console.log('WebSocket message:', event.data);
      };
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      setWsStatus('error');
    }
  };

  // Auto-run tests on mount
  useEffect(() => {
    runTests();
    testWebSocket();
  }, []);

  const getStatusIcon = (status: TestResult['status']) => {
    switch (status) {
      case 'pending':
        return <AlertCircle className="h-4 w-4 text-muted-foreground" />;
      case 'testing':
        return <Loader2 className="h-4 w-4 animate-spin text-blue-500" />;
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'error':
        return <XCircle className="h-4 w-4 text-red-500" />;
    }
  };

  const getOverallStatusBadge = () => {
    switch (overallStatus) {
      case 'idle':
        return <Badge variant="secondary">Not Started</Badge>;
      case 'running':
        return <Badge variant="default" className="animate-pulse">Testing...</Badge>;
      case 'success':
        return <Badge variant="default" className="bg-green-500">All Tests Passed</Badge>;
      case 'partial':
        return <Badge variant="default" className="bg-yellow-500">Partial Success</Badge>;
      case 'failed':
        return <Badge variant="destructive">Connection Failed</Badge>;
    }
  };

  const getWsStatusBadge = () => {
    switch (wsStatus) {
      case 'disconnected':
        return <Badge variant="secondary"><WifiOff className="h-3 w-3 mr-1" />Disconnected</Badge>;
      case 'connecting':
        return <Badge variant="default" className="animate-pulse"><Wifi className="h-3 w-3 mr-1" />Connecting...</Badge>;
      case 'connected':
        return <Badge variant="default" className="bg-green-500"><Wifi className="h-3 w-3 mr-1" />Connected</Badge>;
      case 'error':
        return <Badge variant="destructive"><WifiOff className="h-3 w-3 mr-1" />Error</Badge>;
    }
  };

  const successCount = testResults.filter(t => t.status === 'success').length;
  const errorCount = testResults.filter(t => t.status === 'error').length;

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle>🔌 API Connectivity Test</CardTitle>
            <div className="flex gap-2">
              {getOverallStatusBadge()}
              {getWsStatusBadge()}
              <Button 
                onClick={() => {
                  runTests();
                  testWebSocket();
                }}
                disabled={isRunning}
                size="sm"
              >
                {isRunning ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <RefreshCw className="h-4 w-4" />
                )}
                Retest
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {/* Configuration Info */}
          <div className="mb-6 p-4 bg-muted rounded-lg">
            <h4 className="font-medium mb-2">Current Configuration:</h4>
            <div className="space-y-1 text-sm font-mono">
              <div>API Base: {API_CONFIG.BASE_URL}</div>
              <div>WebSocket: {API_CONFIG.WS_URL}</div>
              <div>Auth Token: {API_CONFIG.AUTH_TOKEN.substring(0, 20)}...</div>
            </div>
          </div>

          {/* Test Results */}
          <div className="space-y-2">
            {testResults.map((test, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center gap-3">
                  {getStatusIcon(test.status)}
                  <div>
                    <div className="font-medium">{test.name}</div>
                    <div className="text-sm text-muted-foreground">
                      {test.endpoint}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm">
                    {test.status === 'success' && test.responseTime && (
                      <span className="text-green-600">{test.responseTime}ms</span>
                    )}
                    {test.status === 'error' && (
                      <span className="text-red-600">{test.message}</span>
                    )}
                    {test.status === 'testing' && (
                      <span className="text-blue-600">Testing...</span>
                    )}
                  </div>
                  {test.data && test.endpoint.includes('templates') && (
                    <div className="text-xs text-muted-foreground">
                      {Array.isArray(test.data) ? test.data.length : test.data.results?.length || 0} items
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Summary */}
          {overallStatus !== 'idle' && overallStatus !== 'running' && (
            <Alert className="mt-4">
              <AlertDescription>
                <div className="flex justify-between items-center">
                  <span>
                    Test Complete: {successCount} passed, {errorCount} failed
                  </span>
                  {overallStatus === 'success' && (
                    <span className="text-green-600 font-medium">
                      ✅ All systems operational!
                    </span>
                  )}
                  {overallStatus === 'partial' && (
                    <span className="text-yellow-600 font-medium">
                      ⚠️ Some endpoints need attention
                    </span>
                  )}
                </div>
              </AlertDescription>
            </Alert>
          )}

          {/* Agent Templates Info */}
          {testResults.find(t => t.endpoint.includes('templates') && t.status === 'success')?.data && (
            <Alert className="mt-4">
              <AlertDescription>
                <div className="space-y-1">
                  <div className="font-medium">🤖 Agent Templates Loaded Successfully!</div>
                  <div className="text-sm">
                    Found {Array.isArray(testResults.find(t => t.endpoint.includes('templates'))?.data) 
                      ? testResults.find(t => t.endpoint.includes('templates'))?.data.length 
                      : testResults.find(t => t.endpoint.includes('templates'))?.data?.results?.length || 0} agent templates ready for execution.
                  </div>
                </div>
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>
    </div>
  );
}