import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  PlayIcon,
  StopIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  ArrowPathIcon,
  BoltIcon,
  CpuChipIcon,
  EyeIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  DocumentTextIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { useAgentOrchestraStore, useAgentOrchestraSelectors } from '../../store/agentOrchestraStore';
import { AgentSelector } from './AgentSelector';
import type { Agent, AgentInstance } from '../../services/agent-orchestra.service';
import { toast } from 'sonner';
import { Logger } from '../../utils/logger';

interface EnhancedAgentExecutionPanelProps {
  className?: string;
  onInstanceCreate?: (instance: AgentInstance) => void;
  onInstanceUpdate?: (instance: AgentInstance) => void;
}

export const EnhancedAgentExecutionPanel: React.FC<EnhancedAgentExecutionPanelProps> = ({
  className = '',
  onInstanceCreate,
  onInstanceUpdate
}) => {
  const [taskDescription, setTaskDescription] = useState('');
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [showResults, setShowResults] = useState(true);
  const [parameters, setParameters] = useState({
    max_tokens: 2000,
    temperature: 0.7,
    use_cache: true,
    priority: 'normal' as 'low' | 'normal' | 'high'
  });

  const taskInputRef = useRef<HTMLTextAreaElement>(null);

  const {
    agents,
    agentsLoading,
    agentsError,
    fetchAgents,
    executeAgent,
    suggestAgents,
    connectWebSocket,
    wsConnected,
    wsConnecting
  } = useAgentOrchestraStore();

  const {
    runningInstances,
    completedInstances,
    failedInstances,
    recentInstances
  } = useAgentOrchestraSelectors();

  useEffect(() => {
    fetchAgents();
    if (!wsConnected && !wsConnecting) {
      connectWebSocket();
    }
  }, [fetchAgents, connectWebSocket, wsConnected, wsConnecting]);

  // Auto-resize textarea
  useEffect(() => {
    if (taskInputRef.current) {
      taskInputRef.current.style.height = 'auto';
      taskInputRef.current.style.height = `${taskInputRef.current.scrollHeight}px`;
    }
  }, [taskDescription]);

  const handleExecute = async () => {
    if (!taskDescription.trim()) {
      toast.error('Please enter a task description');
      taskInputRef.current?.focus();
      return;
    }

    if (!selectedAgent) {
      toast.error('Please select an agent');
      return;
    }

    setIsExecuting(true);
    try {
      Logger.api('Agent Execution', `Starting task with ${selectedAgent.name}`);
      
      const instance = await executeAgent(
        selectedAgent.specialization,
        taskDescription,
        parameters
      );

      // Clear form
      setTaskDescription('');
      setSelectedAgent(null);
      setParameters({
        max_tokens: 2000,
        temperature: 0.7,
        use_cache: true,
        priority: 'normal'
      });

      onInstanceCreate?.(instance);
      
      Logger.debug('Agent Execution', `Task started successfully: ${instance.id}`);
      
    } catch (error) {
      Logger.error('Agent Execution', { message: 'Execution failed', error });
      toast.error('Failed to start agent execution. Please try again.');
    } finally {
      setIsExecuting(false);
    }
  };

  const handleSuggestAgents = async (taskDesc: string): Promise<Agent[]> => {
    try {
      const suggestions = await suggestAgents(taskDesc);
      if (suggestions.length > 0) {
        toast.success(`Found ${suggestions.length} agent suggestions`);
      } else {
        toast.info('No specific agent suggestions found');
      }
      return suggestions;
    } catch (error) {
      Logger.error('Agent Suggestions', { message: 'Failed to get suggestions', error });
      return [];
    }
  };

  const getStatusIcon = (status: string, className: string = 'h-5 w-5') => {
    switch (status) {
      case 'processing':
        return <ArrowPathIcon className={`${className} text-yellow-500 animate-spin`} />;
      case 'completed':
        return <CheckCircleIcon className={`${className} text-green-500`} />;
      case 'failed':
        return <XCircleIcon className={`${className} text-red-500`} />;
      case 'pending':
        return <ClockIcon className={`${className} text-gray-400`} />;
      default:
        return <ClockIcon className={`${className} text-gray-400`} />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'processing':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'failed':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'pending':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const InstanceCard: React.FC<{ instance: AgentInstance; showResult?: boolean }> = ({ 
    instance, 
    showResult = false 
  }) => {
    const [expanded, setExpanded] = useState(false);
    
    useEffect(() => {
      if (instance.status === 'completed' || instance.status === 'failed') {
        onInstanceUpdate?.(instance);
      }
    }, [instance.status, instance]);

    return (
      <motion.div
        layout
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
      >
        <Card className="p-4 hover">
          <div className="flex items-start justify-between">
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-2 mb-2">
                {getStatusIcon(instance.status, 'h-4 w-4')}
                <h4 className="font-medium text-foreground truncate">
                  {instance.template?.name || instance.name || 'Unknown Agent'}
                </h4>
                {instance.template?.specialization && (
                  <Badge variant="secondary" size="sm">
                    {instance.template.specialization}
                  </Badge>
                )}
              </div>
              
              <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
                {instance.task_description}
              </p>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4 text-xs text-muted-foreground">
                  <span>{new Date(instance.created_at).toLocaleString()}</span>
                  {instance.tokens_used > 0 && (
                    <span>{instance.tokens_used.toLocaleString()} tokens</span>
                  )}
                  {instance.execution_time > 0 && (
                    <span>{(instance.execution_time / 1000).toFixed(1)}s</span>
                  )}
                </div>
                
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
            </div>
          </div>

            {/* Result Preview */}
            {(instance.status === 'completed' && instance.result) && (
              <div className="mt-3">
                <Button
                  onClick={() => setExpanded(!expanded)}
                  variant="ghost"
                  size="sm"
                  className="h-auto p-1 text-xs"
                  icon={<EyeIcon className="h-3 w-3" />}
                >
                  {expanded ? 'Hide Result' : 'Show Result'}
                  {expanded ? (
                    <ChevronUpIcon className="h-3 w-3 ml-1" />
                  ) : (
                    <ChevronDownIcon className="h-3 w-3 ml-1" />
                  )}
                </Button>
                
                <AnimatePresence>
                  {expanded && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      className="mt-2 p-3 bg-muted/50 rounded-lg border border-border text-sm"
                    >
                      <div className="max-h-32 overflow-y-auto">
                        {typeof instance.result === 'string' ? (
                          <p className="whitespace-pre-wrap text-foreground">{instance.result}</p>
                        ) : (
                          <pre className="text-xs text-muted-foreground">
                            {JSON.stringify(instance.result, null, 2)}
                          </pre>
                        )}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            )}

          {/* Error Message */}
          {instance.status === 'failed' && instance.error_message && (
            <div className="mt-3 p-2 bg-red-500/10 border border-red-500/20 rounded-lg text-xs text-red-400">
              <ExclamationTriangleIcon className="h-3 w-3 inline mr-1" />
              {instance.error_message}
            </div>
          )}
        </Card>
      </motion.div>
    );
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Execution Panel */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-foreground flex items-center">
            <BoltIcon className="h-6 w-6 mr-2 text-primary" />
            Agent Execution
          </h2>
          <div className="flex items-center space-x-4">
            {/* Connection Status */}
            <div className="flex items-center space-x-2">
              {wsConnected ? (
                <div className="flex items-center text-green-500">
                  <div className="h-2 w-2 bg-green-500 rounded-full mr-2 animate-pulse" />
                  <span className="text-sm">Live Updates</span>
                </div>
              ) : wsConnecting ? (
                <div className="flex items-center text-yellow-500">
                  <LoadingSpinner size="sm" className="mr-2" />
                  <span className="text-sm">Connecting...</span>
                </div>
              ) : (
                <div className="flex items-center text-red-500">
                  <div className="h-2 w-2 bg-red-500 rounded-full mr-2" />
                  <span className="text-sm">Disconnected</span>
                </div>
              )}
            </div>

            {/* Stats */}
            <div className="text-sm text-muted-foreground">
              {runningInstances.length > 0 && (
                <Badge variant="warning" className="mr-2">
                  {runningInstances.length} running
                </Badge>
              )}
              <span>
                {recentInstances.length} total
              </span>
            </div>
          </div>
        </div>

        {/* Task Input */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Task Description
            </label>
            <textarea
              ref={taskInputRef}
              value={taskDescription}
              onChange={(e) => setTaskDescription(e.target.value)}
              placeholder="Describe what you want the agent to do..."
              className="w-full px-4 py-3 border border-border rounded-lg bg-background text-foreground focus:ring-2 focus:ring-primary focus:border-transparent resize-none min-h-[100px]"
              rows={3}
            />
          </div>

          {/* Agent Selection */}
          <AgentSelector
            agents={agents}
            selectedAgent={selectedAgent}
            onAgentSelect={setSelectedAgent}
            loading={agentsLoading}
            error={agentsError}
            taskDescription={taskDescription}
            onSuggestAgents={handleSuggestAgents}
            compact
          />

          {/* Advanced Parameters */}
          <div>
            <Button
              onClick={() => setShowAdvanced(!showAdvanced)}
              variant="ghost"
              size="sm"
              className="text-primary hover:text-primary/80"
              icon={showAdvanced ? <ChevronUpIcon className="h-4 w-4" /> : <ChevronDownIcon className="h-4 w-4" />}
            >
              {showAdvanced ? 'Hide' : 'Show'} Advanced Parameters
            </Button>
            
            <AnimatePresence>
              {showAdvanced && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="mt-4 p-4 bg-muted/30 rounded-lg"
                >
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-foreground mb-1">
                        Max Tokens
                      </label>
                      <input
                        type="number"
                        min="100"
                        max="8000"
                        value={parameters.max_tokens}
                        onChange={(e) => setParameters({...parameters, max_tokens: parseInt(e.target.value) || 2000})}
                        className="w-full px-3 py-2 border border-border bg-background text-foreground rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-foreground mb-1">
                        Temperature
                      </label>
                      <input
                        type="number"
                        step="0.1"
                        min="0"
                        max="2"
                        value={parameters.temperature}
                        onChange={(e) => setParameters({...parameters, temperature: parseFloat(e.target.value) || 0.7})}
                        className="w-full px-3 py-2 border border-border bg-background text-foreground rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-foreground mb-1">
                        Priority
                      </label>
                      <select
                        value={parameters.priority}
                        onChange={(e) => setParameters({...parameters, priority: e.target.value as 'low' | 'normal' | 'high'})}
                        className="w-full px-3 py-2 border border-border bg-background text-foreground rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                      >
                        <option value="low">Low</option>
                        <option value="normal">Normal</option>
                        <option value="high">High</option>
                      </select>
                    </div>

                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        id="use_cache"
                        checked={parameters.use_cache}
                        onChange={(e) => setParameters({...parameters, use_cache: e.target.checked})}
                        className="rounded border-border text-primary focus:ring-primary"
                      />
                      <label htmlFor="use_cache" className="ml-2 text-sm text-foreground">
                        Use Cache
                      </label>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Execute Button */}
          <Button
            onClick={handleExecute}
            disabled={isExecuting || !taskDescription.trim() || !selectedAgent}
            className="w-full"
            size="lg"
            loading={isExecuting}
            icon={!isExecuting ? <PlayIcon className="h-5 w-5" /> : undefined}
          >
            {isExecuting ? 'Starting Execution...' : 'Execute Agent'}
          </Button>
        </div>
      </Card>

      {/* Results Section */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-foreground">
            Execution Results
          </h3>
          <Button
            onClick={() => setShowResults(!showResults)}
            variant="ghost"
            size="sm"
            icon={showResults ? <ChevronUpIcon className="h-4 w-4" /> : <ChevronDownIcon className="h-4 w-4" />}
          >
            {showResults ? 'Hide' : 'Show'} ({recentInstances.length})
          </Button>
        </div>

        <AnimatePresence>
          {showResults && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-4"
            >
              {/* Running Tasks */}
              {runningInstances.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-yellow-600 mb-3 flex items-center">
                    <LoadingSpinner size="sm" className="mr-2" />
                    Running Tasks ({runningInstances.length})
                  </h4>
                  <div className="space-y-3">
                    {runningInstances.map((instance) => (
                      <InstanceCard key={instance.id} instance={instance} />
                    ))}
                  </div>
                </div>
              )}

              {/* Recent Completed/Failed */}
              {recentInstances.length > 0 ? (
                <div>
                  <h4 className="text-sm font-medium text-foreground mb-3 flex items-center">
                    <DocumentTextIcon className="h-4 w-4 mr-1" />
                    Recent Tasks
                  </h4>
                  <div className="space-y-3">
                    {recentInstances.slice(0, 10).map((instance) => (
                      <InstanceCard key={instance.id} instance={instance} showResult />
                    ))}
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <CpuChipIcon className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">No agent executions yet</p>
                  <p className="text-sm text-muted-foreground mt-1">
                    Execute your first agent to see results here
                  </p>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </Card>
    </div>
  );
};