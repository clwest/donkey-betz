/**
 * Orchestra Panel Component
 * 
 * A comprehensive dashboard for Agent Orchestra featuring:
 * - System health monitoring with shadcn/ui components
 * - Real-time WebSocket status and control
 * - Agent execution interface
 * - Instance tracking and management
 */

import React, { useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  CpuChipIcon,
  ChartBarIcon,
  BoltIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  PlayIcon,
  StopIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';

import { Card } from '../../../components/common/Card';
import { Button } from '../../../components/common/Button';
import { Badge } from '../../../components/common/Badge';
import { LoadingSpinner } from '../../../components/common/LoadingSpinner';

import { useOrchestraStore, useOrchestraWS } from '../store/orchestra.store';
import { toast } from 'sonner';

interface OrchestraPanelProps {
  className?: string;
  onInstanceCreate?: (instance: any) => void;
  onInstanceUpdate?: (instance: any) => void;
}

export const OrchestraPanel: React.FC<OrchestraPanelProps> = ({
  className,
  onInstanceCreate,
  onInstanceUpdate
}) => {
  const {
    health,
    healthLoading,
    agents,
    agentsLoading,
    agentsError,
    instances,
    instancesLoading,
    instancesError,
    checkHealth,
    fetchAgents,
    fetchInstances,
    executeAgentTask
  } = useOrchestraStore();

  const {
    state: wsState,
    lastPing,
    lastPong,
    connect: connectWS,
    disconnect: disconnectWS,
    ping: sendPing,
    isConnected,
    isConnecting
  } = useOrchestraWS();

  // Load initial data and connect WebSocket on mount
  useEffect(() => {
    checkHealth();
    fetchAgents();
    fetchInstances();
    connectWS();

    return () => {
      disconnectWS();
    };
  }, [checkHealth, fetchAgents, fetchInstances, connectWS, disconnectWS]);

  // Set up ping interval when connected
  useEffect(() => {
    if (isConnected) {
      const interval = setInterval(() => {
        sendPing();
      }, 30000); // Ping every 30 seconds

      return () => clearInterval(interval);
    }
  }, [isConnected, sendPing]);

  // Handle instance events
  useEffect(() => {
    if (instances.length > 0) {
      const latestInstance = instances[0];
      onInstanceUpdate?.(latestInstance);
    }
  }, [instances, onInstanceUpdate]);

  const handleTestExecution = async () => {
    try {
      const instance = await executeAgentTask(
        'creative', // Use 'creative' which is a valid agent type
        'Test the Agent Orchestra system connectivity and functionality',
        { test: true }
      );
      onInstanceCreate?.(instance);
    } catch (error) {
      console.error('Test execution failed:', error);
    }
  };

  const getHealthStatusIcon = () => {
    if (healthLoading) return <LoadingSpinner size="sm" />;
    
    switch (health?.status) {
      case 'healthy':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'degraded':
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />;
      case 'unhealthy':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />;
      default:
        return <ExclamationTriangleIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const getWsStatusBadge = () => {
    switch (wsState) {
      case 'open':
        return <Badge variant="success" size="sm">Connected</Badge>;
      case 'connecting':
        return <Badge variant="warning" size="sm">Connecting</Badge>;
      case 'closed':
        return <Badge variant="secondary" size="sm">Disconnected</Badge>;
      case 'error':
        return <Badge variant="error" size="sm">Error</Badge>;
      default:
        return <Badge variant="secondary" size="sm">Idle</Badge>;
    }
  };

  const runningInstances = instances.filter(i => i.status === 'processing');
  const completedInstances = instances.filter(i => i.status === 'completed');
  const failedInstances = instances.filter(i => i.status === 'failed');

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-foreground flex items-center">
              <CpuChipIcon className="h-8 w-8 mr-3 text-primary" />
              Agent Orchestra
            </h1>
            <p className="text-muted-foreground mt-1">
              AI-powered agent orchestration with real-time monitoring
            </p>
          </div>

          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                checkHealth();
                fetchAgents();
                fetchInstances();
              }}
              disabled={healthLoading || agentsLoading || instancesLoading}
            >
              <ArrowPathIcon className="h-4 w-4 mr-1" />
              Refresh
            </Button>
            
            <Button
              variant="default"
              size="sm"
              onClick={handleTestExecution}
              disabled={agentsLoading || !agents.length}
            >
              <PlayIcon className="h-4 w-4 mr-1" />
              Test
            </Button>
          </div>
        </div>

        {/* System Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Health Status */}
          <Card className="p-4">
            <div className="flex items-center">
              {getHealthStatusIcon()}
              <div className="ml-3">
                <p className="text-sm font-medium text-muted-foreground">System Health</p>
                <p className="text-lg font-bold text-foreground">
                  {health?.status || 'Unknown'}
                </p>
              </div>
            </div>
            {health?.version && (
              <p className="mt-2 text-xs text-muted-foreground">v{health.version}</p>
            )}
          </Card>

          {/* Available Agents */}
          <Card className="p-4">
            <div className="flex items-center">
              <CpuChipIcon className="h-5 w-5 text-primary" />
              <div className="ml-3">
                <p className="text-sm font-medium text-muted-foreground">Available Agents</p>
                <p className="text-lg font-bold text-foreground">
                  {agentsLoading ? '...' : agents.length}
                </p>
              </div>
            </div>
            {agentsError && (
              <p className="mt-2 text-xs text-red-400">{agentsError}</p>
            )}
          </Card>

          {/* Running Tasks */}
          <Card className="p-4">
            <div className="flex items-center">
              <BoltIcon className="h-5 w-5 text-yellow-500" />
              <div className="ml-3">
                <p className="text-sm font-medium text-muted-foreground">Running Tasks</p>
                <p className="text-lg font-bold text-foreground">{runningInstances.length}</p>
              </div>
            </div>
            <div className="mt-2 flex space-x-4 text-xs text-muted-foreground">
              <span>✅ {completedInstances.length} completed</span>
              <span>❌ {failedInstances.length} failed</span>
            </div>
          </Card>

          {/* WebSocket Status */}
          <Card className="p-4">
            <div className="flex items-center">
              <div className={`w-5 h-5 rounded-full flex items-center justify-center ${
                isConnected ? 'bg-green-500/20' : 'bg-red-500/20'
              }`}>
                <div className={`w-2 h-2 rounded-full ${
                  isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'
                }`} />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-muted-foreground">Real-time</p>
                <div className="flex items-center space-x-2">
                  {getWsStatusBadge()}
                </div>
              </div>
            </div>
            <div className="mt-2 flex space-x-2">
              {isConnected ? (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={disconnectWS}
                >
                  <StopIcon className="h-3 w-3 mr-1" />
                  Disconnect
                </Button>
              ) : (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={connectWS}
                  disabled={isConnecting}
                >
                  <PlayIcon className="h-3 w-3 mr-1" />
                  Connect
                </Button>
              )}
            </div>
          </Card>
        </div>
      </Card>

      {/* WebSocket Debug Info */}
      {isConnected && (lastPing || lastPong) && (
        <Card className="p-4">
          <h3 className="text-sm font-medium text-foreground mb-2">WebSocket Debug</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            {lastPing && (
              <div>
                <span className="text-muted-foreground">Last Ping:</span>
                <span className="ml-2 font-mono text-foreground">
                  {lastPing.toLocaleTimeString()}
                </span>
              </div>
            )}
            {lastPong && (
              <div>
                <span className="text-muted-foreground">Last Pong:</span>
                <span className="ml-2 font-mono text-foreground">
                  {lastPong.toLocaleTimeString()}
                </span>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Recent Instances */}
      {instances.length > 0 && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center">
            <ChartBarIcon className="h-5 w-5 mr-2 text-primary" />
            Recent Instances
            <Badge variant="info" className="ml-2">
              {instances.length}
            </Badge>
          </h3>
          
          <div className="space-y-3">
            {instances.slice(0, 5).map((instance, index) => (
              <motion.div
                key={instance.id || `instance-${index}`}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-center justify-between p-3 bg-muted/50 rounded-lg"
              >
                <div className="flex-1">
                  <div className="flex items-center space-x-3">
                    <code className="text-xs bg-background px-2 py-1 rounded">
                      {instance.id ? instance.id.slice(0, 8) : 'unknown'}...
                    </code>
                    <Badge 
                      variant={
                        instance.status === 'completed' ? 'success' :
                        instance.status === 'failed' ? 'error' :
                        instance.status === 'processing' ? 'warning' : 'secondary'
                      }
                      size="sm"
                    >
                      {instance.status}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground mt-1 truncate">
                    {instance.task_description}
                  </p>
                </div>
                
                <div className="text-xs text-muted-foreground">
                  {new Date(instance.created_at).toLocaleTimeString()}
                </div>
              </motion.div>
            ))}
          </div>
        </Card>
      )}

      {/* Error States */}
      {(agentsError || instancesError) && (
        <Card className="p-6 border-red-500/20 bg-red-500/5">
          <h3 className="text-lg font-semibold text-red-400 mb-2 flex items-center">
            <ExclamationTriangleIcon className="h-5 w-5 mr-2" />
            Errors
          </h3>
          <div className="space-y-2 text-sm text-red-300">
            {agentsError && <p>Agents: {agentsError}</p>}
            {instancesError && <p>Instances: {instancesError}</p>}
          </div>
        </Card>
      )}
    </div>
  );
};