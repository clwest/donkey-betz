/**
 * Agent Orchestra Page
 * AI-powered agent orchestration with comprehensive monitoring and analytics
 */

import React, { Suspense, useState } from 'react';
import { motion } from 'framer-motion';
import {
  CpuChipIcon,
  ChartBarIcon,
  BoltIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  InformationCircleIcon,
  PlayIcon
} from '@heroicons/react/24/outline';
import { AgentErrorBoundary, AgentLoadingFallback } from '../components/common/AgentErrorBoundary';
import { EnhancedAgentExecutionPanel } from '../components/agents/EnhancedAgentExecutionPanel';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { useAgentOrchestraStore, useAgentOrchestraSelectors } from '../store/agentOrchestraStore';
import { AgentOrchestraService } from '../services/agent-orchestra.service';
import { toast } from 'sonner';
import { Logger } from '../utils/logger';

export default function AgentOrchestrationPage() {
  const [testResults, setTestResults] = useState<Record<string, boolean | string>>({});
  const [testing, setTesting] = useState(false);

  const {
    agents,
    instances,
    agentsLoading,
    agentsError,
    wsConnected,
    fetchAgents,
    connectWebSocket,
    healthStatus
  } = useAgentOrchestraStore();

  const {
    runningInstances,
    completedInstances,
    failedInstances,
    recentInstances
  } = useAgentOrchestraSelectors();

  const runConnectivityTest = async () => {
    setTesting(true);
    const results: Record<string, boolean | string> = {};

    try {
      // Test API Health Check
      Logger.debug('DBAO Test', 'Testing health check endpoint');
      const health = await AgentOrchestraService.healthCheck();
      results.healthCheck = health ? `✅ ${health.status} (v${health.version})` : '❌ Failed';

      // Test Agents Endpoint
      Logger.debug('DBAO Test', 'Testing agents endpoint');
      const agentsList = await AgentOrchestraService.getAgents();
      results.agentsEndpoint = agentsList.length > 0 ? `✅ ${agentsList.length} agents loaded` : '⚠️ No agents found';

      // Test Agent Instances
      Logger.debug('DBAO Test', 'Testing instances endpoint');
      const instancesList = await AgentOrchestraService.getInstances();
      results.instancesEndpoint = `✅ ${instancesList.length} instances found`;

      // Test Agent Suggestions
      if (agentsList.length > 0) {
        Logger.debug('DBAO Test', 'Testing agent suggestions');
        const suggestions = await AgentOrchestraService.suggestAgent('Create a marketing plan for a fitness app');
        results.suggestions = suggestions.length > 0 ? `✅ ${suggestions.length} suggestions` : '⚠️ No suggestions';
      }

      // Test WebSocket Connection
      results.websocket = wsConnected ? '✅ Connected' : '❌ Disconnected';

      // Test Sports Betting Features
      try {
        Logger.debug('DBAO Test', 'Testing betting endpoints');
        const liveOps = await AgentOrchestraService.getLiveOpportunities();
        results.bettingEndpoints = `✅ ${liveOps.length} opportunities found`;
      } catch (error) {
        results.bettingEndpoints = '⚠️ Betting features unavailable';
      }

      setTestResults(results);
      toast.success('Connectivity test completed');

    } catch (error: any) {
      Logger.error('DBAO Test', { message: 'Connectivity test failed', error });
      results.error = `❌ ${error.message}`;
      setTestResults(results);
      toast.error('Connectivity test failed');
    } finally {
      setTesting(false);
    }
  };

  const handleInstanceCreate = (instance: any) => {
    Logger.debug('Agent Orchestration', `New instance created: ${instance.id}`);
    toast.success(`Agent task started: ${instance.template.name}`);
  };

  const handleInstanceUpdate = (instance: any) => {
    Logger.debug('Agent Orchestration', `Instance updated: ${instance.id} - ${instance.status}`);
    
    if (instance.status === 'completed') {
      toast.success(`Task completed: ${instance.template.name}`);
    } else if (instance.status === 'failed') {
      toast.error(`Task failed: ${instance.template.name}`);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Page Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground flex items-center">
              <CpuChipIcon className="h-8 w-8 mr-3 text-primary" />
              Agent Orchestra
            </h1>
            <p className="mt-2 text-muted-foreground">
              AI-powered agent orchestration with comprehensive monitoring and analytics
            </p>
          </div>

          {/* Connectivity Test Button */}
          <Button
            onClick={runConnectivityTest}
            disabled={testing}
            variant="secondary"
            icon={testing ? <LoadingSpinner size="sm" /> : <ChartBarIcon className="h-4 w-4" />}
          >
            {testing ? 'Testing...' : 'Test Connectivity'}
          </Button>
        </div>
      </div>

      {/* System Status Dashboard */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Agents Status */}
        <Card className="p-6">
          <div className="flex items-center">
            <CpuChipIcon className="h-8 w-8 text-primary" />
            <div className="ml-4">
              <p className="text-sm font-medium text-muted-foreground">Available Agents</p>
              <p className="text-2xl font-bold text-foreground">
                {agentsLoading ? '...' : agents.length}
              </p>
            </div>
          </div>
          {agentsError && (
            <p className="mt-2 text-xs text-red-400">
              <ExclamationTriangleIcon className="h-3 w-3 inline mr-1" />
              {agentsError}
            </p>
          )}
        </Card>

        {/* Running Tasks */}
        <Card className="p-6">
          <div className="flex items-center">
            <BoltIcon className="h-8 w-8 text-yellow-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-muted-foreground">Running Tasks</p>
              <p className="text-2xl font-bold text-foreground">{runningInstances.length}</p>
            </div>
          </div>
          <div className="mt-2 flex space-x-4 text-xs text-muted-foreground">
            <span>✅ {completedInstances.length} completed</span>
            <span>❌ {failedInstances.length} failed</span>
          </div>
        </Card>

        {/* WebSocket Status */}
        <Card className="p-6">
          <div className="flex items-center">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
              wsConnected ? 'bg-green-500/20' : 'bg-red-500/20'
            }`}>
              <div className={`w-3 h-3 rounded-full ${
                wsConnected ? 'bg-green-500' : 'bg-red-500'
              } ${wsConnected ? 'animate-pulse' : ''}`} />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-muted-foreground">Real-time Updates</p>
              <p className="text-sm font-bold text-foreground">
                {wsConnected ? 'Connected' : 'Disconnected'}
              </p>
            </div>
          </div>
          {!wsConnected && (
            <Button
              onClick={connectWebSocket}
              variant="ghost"
              size="sm"
              className="mt-2"
            >
              Reconnect
            </Button>
          )}
        </Card>

        {/* System Health */}
        <Card className="p-6">
          <div className="flex items-center">
            {healthStatus?.status === 'healthy' ? (
              <CheckCircleIcon className="h-8 w-8 text-green-500" />
            ) : (
              <ExclamationTriangleIcon className="h-8 w-8 text-red-500" />
            )}
            <div className="ml-4">
              <p className="text-sm font-medium text-muted-foreground">System Health</p>
              <p className="text-sm font-bold text-foreground">
                {healthStatus?.status || 'Unknown'}
              </p>
            </div>
          </div>
          {healthStatus?.version && (
            <p className="mt-2 text-xs text-muted-foreground">v{healthStatus.version}</p>
          )}
        </Card>
      </div>

      {/* Connectivity Test Results */}
      {Object.keys(testResults).length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center">
              <InformationCircleIcon className="h-5 w-5 mr-2 text-primary" />
              Connectivity Test Results
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(testResults).map(([key, value]) => (
                <div key={key} className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                  <span className="text-sm font-medium text-foreground capitalize">
                    {key.replace(/([A-Z])/g, ' $1').trim()}
                  </span>
                  <span className="text-sm text-muted-foreground">{value}</span>
                </div>
              ))}
            </div>
          </Card>
        </motion.div>
      )}

      {/* Main Agent Execution Panel */}
      <AgentErrorBoundary
        contextName="Agent Execution Panel"
        showDetails={import.meta.env.VITE_SHOW_ERROR_DETAILS === 'true'}
      >
        <Suspense fallback={<AgentLoadingFallback message="Loading agent execution interface..." />}>
          <EnhancedAgentExecutionPanel
            onInstanceCreate={handleInstanceCreate}
            onInstanceUpdate={handleInstanceUpdate}
          />
        </Suspense>
      </AgentErrorBoundary>

      {/* Footer */}
      <div className="mt-12 pt-8 border-t border-border">
        <div className="text-center">
          <p className="text-sm text-muted-foreground">
            Agent Orchestra - Built with comprehensive error handling and real-time updates
          </p>
          <div className="mt-2 flex items-center justify-center space-x-4 text-xs text-muted-foreground">
            <span>API: {import.meta.env.VITE_API_URL || 'http://localhost:8000/api'}</span>
            <span>•</span>
            <span>WebSocket: {import.meta.env.VITE_WS_URL || 'ws://localhost:8000'}</span>
            <span>•</span>
            <span>Environment: {import.meta.env.MODE}</span>
          </div>
        </div>
      </div>
    </div>
  );
}