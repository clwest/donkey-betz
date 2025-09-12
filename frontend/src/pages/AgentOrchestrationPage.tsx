/**
 * Agent Orchestra Page
 * AI-powered agent orchestration with comprehensive monitoring and analytics
 */

import React, { Suspense, useState, useEffect } from 'react';
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
    fetchInstances,
    connectWebSocket,
    healthStatus,
    fetchHealthStatus
  } = useAgentOrchestraStore();

  const {
    runningInstances,
    completedInstances,
    failedInstances,
    recentInstances
  } = useAgentOrchestraSelectors();

  // Fetch initial data when component mounts
  useEffect(() => {
    fetchHealthStatus();
    fetchAgents();
    fetchInstances();
  }, [fetchHealthStatus, fetchAgents, fetchInstances]);

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
    <div className="container mx-auto px-4 py-8" style={{ backgroundColor: 'var(--gaming-bg-primary)' }}>
      {/* Page Header - Cyberpunk Style */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div className="relative">
            <div className="absolute -inset-2 bg-gradient-to-r from-cyan-500/20 via-purple-500/20 to-cyan-500/20 rounded-lg blur opacity-30"></div>
            <div className="relative">
              <h1 className="text-4xl font-black text-white flex items-center uppercase tracking-wider" 
                  style={{ 
                    fontFamily: 'var(--font-mono)',
                    textShadow: '0 0 20px rgba(0, 255, 255, 0.5)',
                    color: 'var(--gaming-neon-cyan)'
                  }}>
                <CpuChipIcon className="h-10 w-10 mr-4" style={{ color: 'var(--gaming-neon-cyan)', filter: 'drop-shadow(0 0 10px rgba(0, 255, 255, 0.8))' }} />
                Agent Orchestra
              </h1>
              <p className="mt-3 text-lg font-semibold" 
                 style={{ 
                   color: 'var(--gaming-text-secondary)',
                   textShadow: '0 0 10px rgba(157, 78, 221, 0.3)'
                 }}>
                <span style={{ color: 'var(--gaming-neon-purple)' }}>CYBERPUNK</span> AI Command Center
              </p>
            </div>
          </div>

          {/* Connectivity Test Button - Gaming Style */}
          <div className="relative">
            <div className={`absolute -inset-1 bg-gradient-to-r from-cyan-500 to-purple-500 rounded-lg blur opacity-30 transition-opacity duration-300 ${testing ? 'animate-pulse' : ''}`}></div>
            <Button
              onClick={runConnectivityTest}
              disabled={testing}
              className="relative bg-gray-900 border-2 border-cyan-400 text-cyan-400 hover:bg-cyan-400/10 hover:shadow-cyan-400/50 transition-all duration-300 font-bold uppercase tracking-wider"
              style={{
                boxShadow: testing ? '0 0 20px rgba(0, 255, 255, 0.5)' : '0 0 10px rgba(0, 255, 255, 0.2)',
                background: 'var(--gaming-bg-secondary)',
                borderColor: 'var(--gaming-neon-cyan)',
                color: 'var(--gaming-neon-cyan)'
              }}
              icon={testing ? 
                <div className="animate-spin" style={{ color: 'var(--gaming-neon-cyan)' }}>
                  <LoadingSpinner size="sm" />
                </div> : 
                <ChartBarIcon className="h-4 w-4" style={{ color: 'var(--gaming-neon-cyan)' }} />
              }
            >
              {testing ? 'SCANNING...' : 'SYSTEM SCAN'}
            </Button>
          </div>
        </div>
      </div>

      {/* System Status Dashboard - Cyberpunk Command Center */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Agents Status - Gaming Card */}
        <div className="gaming-card relative overflow-hidden group">
          <div className="gaming-border-glow"></div>
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-cyan-500 via-purple-500 to-cyan-500 opacity-60"></div>
          <div className="flex items-center">
            <div className="relative">
              <CpuChipIcon className="h-10 w-10" style={{ 
                color: 'var(--gaming-neon-cyan)',
                filter: 'drop-shadow(0 0 10px rgba(0, 255, 255, 0.7))'
              }} />
              <div className="absolute inset-0 rounded-full bg-cyan-400/20 animate-ping"></div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-bold uppercase tracking-wider" style={{ color: 'var(--gaming-text-secondary)' }}>
                AI AGENTS
              </p>
              <p className="text-3xl font-black" style={{ 
                color: 'var(--gaming-neon-cyan)',
                fontFamily: 'var(--font-mono)',
                textShadow: '0 0 15px rgba(0, 255, 255, 0.5)'
              }}>
                {agentsLoading ? (
                  <span className="animate-pulse">...</span>
                ) : (
                  agents.length.toString().padStart(2, '0')
                )}
              </p>
            </div>
          </div>
          {agentsError && (
            <div className="mt-3 p-2 bg-red-500/10 border border-red-500/30 rounded-lg">
              <p className="text-xs font-semibold" style={{ color: 'var(--gaming-neon-pink)' }}>
                <ExclamationTriangleIcon className="h-3 w-3 inline mr-1" />
                {agentsError}
              </p>
            </div>
          )}
        </div>

        {/* Running Tasks - Gaming Card with Pulse */}
        <div className="gaming-card relative overflow-hidden group">
          <div className="gaming-border-glow"></div>
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-green-400 via-yellow-400 to-green-400 opacity-60 animate-pulse"></div>
          <div className="flex items-center">
            <div className="relative">
              <BoltIcon className="h-10 w-10" style={{ 
                color: 'var(--gaming-neon-green)',
                filter: 'drop-shadow(0 0 10px rgba(57, 255, 20, 0.7))'
              }} />
              {runningInstances.length > 0 && (
                <div className="absolute inset-0 rounded-full bg-green-400/20 animate-ping"></div>
              )}
            </div>
            <div className="ml-4">
              <p className="text-sm font-bold uppercase tracking-wider" style={{ color: 'var(--gaming-text-secondary)' }}>
                ACTIVE TASKS
              </p>
              <p className="text-3xl font-black" style={{ 
                color: 'var(--gaming-neon-green)',
                fontFamily: 'var(--font-mono)',
                textShadow: '0 0 15px rgba(57, 255, 20, 0.5)'
              }}>
                {runningInstances.length.toString().padStart(2, '0')}
              </p>
            </div>
          </div>
          <div className="mt-3 flex space-x-4 text-xs font-semibold">
            <span style={{ color: 'var(--gaming-neon-green)' }}>
              ✓ {completedInstances.length} COMPLETE
            </span>
            <span style={{ color: 'var(--gaming-neon-pink)' }}>
              ✗ {failedInstances.length} FAILED
            </span>
          </div>
        </div>

        {/* WebSocket Status - Gaming Card with Connection Animation */}
        <div className="gaming-card relative overflow-hidden group">
          <div className="gaming-border-glow"></div>
          <div className={`absolute top-0 left-0 w-full h-1 ${
            wsConnected 
              ? 'bg-gradient-to-r from-green-400 to-cyan-400 animate-pulse' 
              : 'bg-gradient-to-r from-red-400 to-pink-400'
          } opacity-60`}></div>
          <div className="flex items-center">
            <div className="relative w-10 h-10 rounded-full flex items-center justify-center" style={{
              background: wsConnected 
                ? 'radial-gradient(circle, rgba(57, 255, 20, 0.2) 0%, rgba(0, 255, 255, 0.1) 70%, transparent 100%)'
                : 'radial-gradient(circle, rgba(255, 20, 147, 0.2) 0%, rgba(255, 107, 0, 0.1) 70%, transparent 100%)'
            }}>
              <div className={`w-4 h-4 rounded-full ${
                wsConnected ? 'bg-green-400' : 'bg-red-400'
              } ${wsConnected ? 'animate-pulse' : ''}`} style={{
                boxShadow: wsConnected 
                  ? '0 0 15px rgba(57, 255, 20, 0.8)' 
                  : '0 0 15px rgba(255, 20, 147, 0.8)'
              }} />
            </div>
            <div className="ml-4">
              <p className="text-sm font-bold uppercase tracking-wider" style={{ color: 'var(--gaming-text-secondary)' }}>
                NEURAL LINK
              </p>
              <p className="text-lg font-black uppercase" style={{ 
                color: wsConnected ? 'var(--gaming-neon-green)' : 'var(--gaming-neon-pink)',
                fontFamily: 'var(--font-mono)',
                textShadow: wsConnected 
                  ? '0 0 10px rgba(57, 255, 20, 0.5)'
                  : '0 0 10px rgba(255, 20, 147, 0.5)'
              }}>
                {wsConnected ? 'ONLINE' : 'OFFLINE'}
              </p>
            </div>
          </div>
          {!wsConnected && (
            <div className="mt-3">
              <Button
                onClick={connectWebSocket}
                className="text-xs font-bold uppercase tracking-wider py-1 px-3"
                style={{
                  background: 'var(--gaming-bg-elevated)',
                  borderColor: 'var(--gaming-neon-pink)',
                  color: 'var(--gaming-neon-pink)',
                  boxShadow: '0 0 10px rgba(255, 20, 147, 0.3)'
                }}
              >
                RECONNECT
              </Button>
            </div>
          )}
        </div>

        {/* System Health - Gaming Card */}
        <div className="gaming-card relative overflow-hidden group">
          <div className="gaming-border-glow"></div>
          <div className={`absolute top-0 left-0 w-full h-1 ${
            healthStatus?.status === 'healthy'
              ? 'bg-gradient-to-r from-green-400 to-cyan-400'
              : 'bg-gradient-to-r from-red-400 to-orange-400'
          } opacity-60`}></div>
          <div className="flex items-center">
            <div className="relative">
              {healthStatus?.status === 'healthy' ? (
                <CheckCircleIcon className="h-10 w-10" style={{ 
                  color: 'var(--gaming-neon-green)',
                  filter: 'drop-shadow(0 0 10px rgba(57, 255, 20, 0.7))'
                }} />
              ) : (
                <ExclamationTriangleIcon className="h-10 w-10" style={{ 
                  color: 'var(--gaming-neon-pink)',
                  filter: 'drop-shadow(0 0 10px rgba(255, 20, 147, 0.7))'
                }} />
              )}
              {healthStatus?.status === 'healthy' && (
                <div className="absolute inset-0 rounded-full bg-green-400/20 animate-ping"></div>
              )}
            </div>
            <div className="ml-4">
              <p className="text-sm font-bold uppercase tracking-wider" style={{ color: 'var(--gaming-text-secondary)' }}>
                SYSTEM STATUS
              </p>
              <p className="text-lg font-black uppercase" style={{ 
                color: healthStatus?.status === 'healthy' ? 'var(--gaming-neon-green)' : 'var(--gaming-neon-pink)',
                fontFamily: 'var(--font-mono)',
                textShadow: healthStatus?.status === 'healthy'
                  ? '0 0 10px rgba(57, 255, 20, 0.5)'
                  : '0 0 10px rgba(255, 20, 147, 0.5)'
              }}>
                {healthStatus?.status || 'UNKNOWN'}
              </p>
            </div>
          </div>
          {healthStatus?.version && (
            <div className="mt-3">
              <p className="text-xs font-semibold" style={{ color: 'var(--gaming-text-muted)' }}>
                VERSION {healthStatus.version}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Connectivity Test Results - Cyberpunk Diagnostics */}
      {Object.keys(testResults).length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="gaming-card relative overflow-hidden">
            <div className="gaming-border-glow"></div>
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-purple-500 via-cyan-500 to-purple-500 opacity-60 animate-pulse"></div>
            
            <h3 className="text-xl font-black uppercase tracking-wider mb-6 flex items-center" style={{
              color: 'var(--gaming-neon-purple)',
              fontFamily: 'var(--font-mono)',
              textShadow: '0 0 15px rgba(157, 78, 221, 0.5)'
            }}>
              <InformationCircleIcon className="h-6 w-6 mr-3" style={{ 
                color: 'var(--gaming-neon-purple)',
                filter: 'drop-shadow(0 0 10px rgba(157, 78, 221, 0.7))'
              }} />
              SYSTEM DIAGNOSTICS
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(testResults).map(([key, value]) => {
                const isSuccess = typeof value === 'string' && value.includes('✅');
                const isWarning = typeof value === 'string' && value.includes('⚠️');
                const isError = typeof value === 'string' && value.includes('❌');
                
                return (
                  <div key={key} className="relative p-4 rounded-lg border transition-all duration-300 hover:transform hover:scale-105" style={{
                    background: 'var(--gaming-bg-elevated)',
                    borderColor: isSuccess ? 'var(--gaming-neon-green)' : 
                                isWarning ? 'var(--gaming-neon-orange)' : 
                                isError ? 'var(--gaming-neon-pink)' : 'var(--gaming-border)',
                    boxShadow: isSuccess ? '0 0 10px rgba(57, 255, 20, 0.2)' :
                              isWarning ? '0 0 10px rgba(255, 107, 0, 0.2)' :
                              isError ? '0 0 10px rgba(255, 20, 147, 0.2)' : 'none'
                  }}>
                    {/* Status Indicator */}
                    <div className="absolute top-2 right-2">
                      <div className={`w-2 h-2 rounded-full ${
                        isSuccess ? 'bg-green-400 animate-pulse' : 
                        isWarning ? 'bg-yellow-400' : 
                        isError ? 'bg-red-400' : 'bg-gray-400'
                      }`} style={{
                        boxShadow: isSuccess ? '0 0 8px rgba(57, 255, 20, 0.8)' :
                                  isWarning ? '0 0 8px rgba(255, 107, 0, 0.8)' :
                                  isError ? '0 0 8px rgba(255, 20, 147, 0.8)' : 'none'
                      }}></div>
                    </div>
                    
                    <div className="flex flex-col gap-2">
                      <span className="text-sm font-bold uppercase tracking-wider" style={{ 
                        color: 'var(--gaming-text-secondary)'
                      }}>
                        {key.replace(/([A-Z])/g, ' $1').trim()}
                      </span>
                      <span className="text-sm font-semibold" style={{ 
                        color: isSuccess ? 'var(--gaming-neon-green)' : 
                              isWarning ? 'var(--gaming-neon-orange)' : 
                              isError ? 'var(--gaming-neon-pink)' : 'var(--gaming-text-primary)',
                        fontFamily: 'var(--font-mono)'
                      }}>
                        {value}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
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