import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  PlayIcon, 
  StopIcon, 
  ClockIcon, 
  CheckCircleIcon, 
  XCircleIcon,
  CpuChipIcon,
  BoltIcon,
  UserIcon
} from '@heroicons/react/24/outline';
import { useAgentOrchestraStore, useAgentOrchestraSelectors } from '../../store/agentOrchestraStore';
import type { Agent, AgentInstance } from '../../services/agent-orchestra.service';
import { toast } from 'sonner';

interface AgentExecutionPanelProps {
  className?: string;
}

export const AgentExecutionPanel: React.FC<AgentExecutionPanelProps> = ({ className }) => {
  const [taskDescription, setTaskDescription] = useState('');
  const [selectedAgentType, setSelectedAgentType] = useState('');
  const [isExecuting, setIsExecuting] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [parameters, setParameters] = useState<Record<string, any>>({});

  const {
    agents,
    instances,
    agentsLoading,
    fetchAgents,
    executeAgent,
    suggestAgents,
    connectWebSocket,
    wsConnected
  } = useAgentOrchestraStore();

  const {
    runningInstances,
    completedInstances,
    recentInstances
  } = useAgentOrchestraSelectors();

  useEffect(() => {
    fetchAgents();
    if (!wsConnected) {
      connectWebSocket();
    }
  }, []);

  const handleExecute = async () => {
    if (!taskDescription.trim()) {
      toast.error('Please enter a task description');
      return;
    }

    if (!selectedAgentType) {
      toast.error('Please select an agent type');
      return;
    }

    setIsExecuting(true);
    try {
      await executeAgent(selectedAgentType, taskDescription, parameters);
      setTaskDescription('');
      setParameters({});
      toast.success('Agent execution started successfully');
    } catch (error) {
      console.error('Execution failed:', error);
    } finally {
      setIsExecuting(false);
    }
  };

  const handleSuggestAgents = async () => {
    if (!taskDescription.trim()) {
      toast.error('Please enter a task description to get suggestions');
      return;
    }

    try {
      const suggestions = await suggestAgents(taskDescription);
      if (suggestions.length > 0) {
        setSelectedAgentType(suggestions[0].specialization);
        toast.success(`Suggested: ${suggestions[0].name}`);
      } else {
        toast.info('No specific agent suggestions found');
      }
    } catch (error) {
      console.error('Failed to get suggestions:', error);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'processing':
        return <ClockIcon className="h-5 w-5 text-yellow-500 animate-spin" />;
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'failed':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      default:
        return <ClockIcon className="h-5 w-5 text-muted-foreground" />;
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
      default:
        return 'bg-muted/10 text-gray-800 border-border';
    }
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Execution Panel */}
      <div className="bg-white rounded-xl border border-border p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900 flex items-center">
            <BoltIcon className="h-6 w-6 mr-2 text-blue-600" />
            Agent Execution
          </h2>
          <div className="flex items-center space-x-2">
            {wsConnected ? (
              <div className="flex items-center text-green-600">
                <div className="h-2 w-2 bg-green-500 rounded-full mr-2 animate-pulse" />
                <span className="text-sm">Live Updates</span>
              </div>
            ) : (
              <div className="flex items-center text-red-600">
                <div className="h-2 w-2 bg-red-500 rounded-full mr-2" />
                <span className="text-sm">Disconnected</span>
              </div>
            )}
          </div>
        </div>

        {/* Task Input */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Task Description
            </label>
            <textarea
              value={taskDescription}
              onChange={(e) => setTaskDescription(e.target.value)}
              placeholder="Describe what you want the agent to do..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              rows={4}
            />
          </div>

          <div className="flex space-x-4">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Agent Type
              </label>
              <select
                value={selectedAgentType}
                onChange={(e) => setSelectedAgentType(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Select an agent...</option>
                {agents.map((agent) => (
                  <option key={agent.id} value={agent.specialization}>
                    {agent.name} - {agent.specialization}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex items-end">
              <button
                onClick={handleSuggestAgents}
                disabled={!taskDescription.trim()}
                className="px-4 py-3 bg-purple-600 text-foreground rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <CpuChipIcon className="h-5 w-5" />
              </button>
            </div>
          </div>

          {/* Advanced Parameters */}
          <div>
            <button
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="text-sm text-blue-600 hover:text-blue-700"
            >
              {showAdvanced ? 'Hide' : 'Show'} Advanced Parameters
            </button>
            <AnimatePresence>
              {showAdvanced && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="mt-4 p-4 bg-muted/5 rounded-lg"
                >
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Max Tokens
                      </label>
                      <input
                        type="number"
                        value={parameters.max_tokens || ''}
                        onChange={(e) => setParameters({...parameters, max_tokens: parseInt(e.target.value)})}
                        className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                        placeholder="2000"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Temperature
                      </label>
                      <input
                        type="number"
                        step="0.1"
                        min="0"
                        max="2"
                        value={parameters.temperature || ''}
                        onChange={(e) => setParameters({...parameters, temperature: parseFloat(e.target.value)})}
                        className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                        placeholder="0.7"
                      />
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Execute Button */}
          <button
            onClick={handleExecute}
            disabled={isExecuting || !taskDescription.trim() || !selectedAgentType}
            className="w-full py-3 bg-blue-600 text-foreground rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
          >
            {isExecuting ? (
              <>
                <StopIcon className="h-5 w-5 mr-2 animate-pulse" />
                Executing...
              </>
            ) : (
              <>
                <PlayIcon className="h-5 w-5 mr-2" />
                Execute Agent
              </>
            )}
          </button>
        </div>
      </div>

      {/* Running Instances */}
      {runningInstances.length > 0 && (
        <div className="bg-white rounded-xl border border-border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Running Tasks ({runningInstances.length})
          </h3>
          <div className="space-y-3">
            {runningInstances.map((instance) => (
              <motion.div
                key={instance.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center justify-between p-4 bg-yellow-50 border border-yellow-200 rounded-lg"
              >
                <div className="flex items-center space-x-3">
                  {getStatusIcon(instance.status)}
                  <div>
                    <p className="font-medium text-gray-900">
                      {instance.template.name}
                    </p>
                    <p className="text-sm text-gray-600 truncate max-w-md">
                      {instance.task_description}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(instance.status)}`}>
                    {instance.status}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {new Date(instance.created_at).toLocaleTimeString()}
                  </span>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Results */}
      <div className="bg-white rounded-xl border border-border p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Recent Tasks
        </h3>
        {recentInstances.length > 0 ? (
          <div className="space-y-3">
            {recentInstances.map((instance) => (
              <div
                key={instance.id}
                className="flex items-center justify-between p-4 bg-muted/5 rounded-lg hover:bg-muted/10 transition-colors cursor-pointer"
              >
                <div className="flex items-center space-x-3">
                  {getStatusIcon(instance.status)}
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <p className="font-medium text-gray-900">
                        {instance.template.name}
                      </p>
                      <span className="text-xs text-muted-foreground">
                        {instance.template.specialization}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 truncate max-w-md">
                      {instance.task_description}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  {instance.tokens_used > 0 && (
                    <span className="text-xs text-muted-foreground">
                      {instance.tokens_used.toLocaleString()} tokens
                    </span>
                  )}
                  <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(instance.status)}`}>
                    {instance.status}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {new Date(instance.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <UserIcon className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-muted-foreground">No recent agent executions</p>
            <p className="text-sm text-muted-foreground mt-1">
              Execute your first agent to see results here
            </p>
          </div>
        )}
      </div>
    </div>
  );
};