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
  ExclamationTriangleIcon,
  TrashIcon,
  CheckIcon
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
  
  // Mission Archive management
  const [selectedInstanceIds, setSelectedInstanceIds] = useState<Set<string>>(new Set());
  const [isDeleting, setIsDeleting] = useState(false);

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
    wsConnecting,
    deleteInstance,
    deleteMultipleInstances
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

  // Mission Archive management functions
  const toggleInstanceSelection = (instanceId: string) => {
    const newSelection = new Set(selectedInstanceIds);
    if (newSelection.has(instanceId)) {
      newSelection.delete(instanceId);
    } else {
      newSelection.add(instanceId);
    }
    setSelectedInstanceIds(newSelection);
  };

  const selectAllInstances = () => {
    const allCompletedIds = new Set(recentInstances.map(instance => instance.id));
    setSelectedInstanceIds(allCompletedIds);
  };

  const clearSelection = () => {
    setSelectedInstanceIds(new Set());
  };

  const handleDeleteSelected = async () => {
    if (selectedInstanceIds.size === 0) return;
    
    setIsDeleting(true);
    try {
      const ids = Array.from(selectedInstanceIds);
      await deleteMultipleInstances(ids);
      setSelectedInstanceIds(new Set()); // Clear selection after successful delete
    } finally {
      setIsDeleting(false);
    }
  };

  const handleDeleteInstance = async (instanceId: string) => {
    setIsDeleting(true);
    try {
      await deleteInstance(instanceId);
      // Remove from selection if it was selected
      const newSelection = new Set(selectedInstanceIds);
      newSelection.delete(instanceId);
      setSelectedInstanceIds(newSelection);
    } finally {
      setIsDeleting(false);
    }
  };

  const getStatusIcon = (status: string, className: string = 'h-5 w-5') => {
    switch (status) {
      case 'processing':
      case 'running':
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
      case 'running':
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

  const InstanceCard: React.FC<{ 
    instance: AgentInstance; 
    showResult?: boolean;
    allowSelection?: boolean;
  }> = ({ 
    instance, 
    showResult = false,
    allowSelection = true
  }) => {
    const [expanded, setExpanded] = useState(false);
    const isSelected = selectedInstanceIds.has(instance.id);
    const canDelete = instance.status === 'completed' || instance.status === 'failed';
    
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
        whileHover={{ scale: 1.02 }}
        className="gaming-card relative overflow-hidden group cursor-pointer"
        style={{ marginBottom: '16px' }}
      >
        <div className="gaming-border-glow"></div>
        {/* Status-based top border */}
        <div className={`absolute top-0 left-0 w-full h-1 opacity-60 ${
          instance.status === 'completed' ? 'bg-gradient-to-r from-green-400 to-cyan-400' :
          instance.status === 'failed' ? 'bg-gradient-to-r from-red-400 to-pink-400' :
          (instance.status === 'processing' || instance.status === 'running') ? 'bg-gradient-to-r from-yellow-400 to-orange-400 animate-pulse' :
          'bg-gradient-to-r from-gray-400 to-gray-600'
        }`}></div>
        
        <div className="flex items-start justify-between">
          {/* Selection checkbox */}
          {allowSelection && canDelete && (
            <div className="flex-shrink-0 mr-3 mt-1">
              <button
                onClick={() => toggleInstanceSelection(instance.id)}
                disabled={isDeleting}
                className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-all duration-200 ${
                  isSelected
                    ? 'bg-cyan-400 border-cyan-400'
                    : 'border-gray-500 hover:border-cyan-400'
                } ${isDeleting ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                style={{
                  borderColor: isSelected ? 'var(--gaming-neon-cyan)' : 'var(--gaming-border)',
                  background: isSelected ? 'var(--gaming-neon-cyan)' : 'transparent'
                }}
              >
                {isSelected && (
                  <CheckIcon className="h-3 w-3" style={{ color: 'var(--gaming-bg-primary)' }} />
                )}
              </button>
            </div>
          )}
          
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-3 mb-3">
              <div className="relative">
                {getStatusIcon(instance.status, 'h-5 w-5')}
                {(instance.status === 'processing' || instance.status === 'running') && (
                  <div className="absolute inset-0 rounded-full bg-yellow-400/20 animate-ping"></div>
                )}
              </div>
              <h4 className="font-bold uppercase tracking-wide truncate" style={{
                color: 'var(--gaming-text-primary)',
                fontFamily: 'var(--font-mono)',
                fontSize: '14px'
              }}>
                {instance.template?.name || instance.name || 'UNKNOWN AGENT'}
              </h4>
              {instance.template?.specialization && (
                <div className="px-2 py-1 rounded text-xs font-bold uppercase tracking-wider" style={{
                  background: 'rgba(157, 78, 221, 0.2)',
                  border: '1px solid var(--gaming-neon-purple)',
                  color: 'var(--gaming-neon-purple)'
                }}>
                  {instance.template.specialization}
                </div>
              )}
            </div>
            
            <p className="text-sm line-clamp-2 mb-4" style={{ 
              color: 'var(--gaming-text-secondary)',
              fontFamily: 'var(--font-mono)'
            }}>
              {instance.task_description}
            </p>

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4 text-xs font-semibold" style={{
                color: 'var(--gaming-text-muted)',
                fontFamily: 'var(--font-mono)'
              }}>
                <span>{new Date(instance.created_at).toLocaleString()}</span>
                {instance.token_usage?.total_tokens && (
                  <span style={{ color: 'var(--gaming-neon-cyan)' }}>
                    {instance.token_usage.total_tokens.toLocaleString()} TOKENS
                  </span>
                )}
                {instance.execution_time_seconds > 0 && (
                  <span style={{ color: 'var(--gaming-neon-green)' }}>
                    {instance.execution_time_seconds.toFixed(1)}s
                  </span>
                )}
              </div>
              
              <div className="flex items-center space-x-2">
                <div className={`px-3 py-1 rounded-lg text-xs font-black uppercase tracking-wider ${
                  (instance.status === 'processing' || instance.status === 'running') ? 'animate-pulse' : ''
                }`} style={{
                  background: instance.status === 'completed' ? 'rgba(57, 255, 20, 0.2)' :
                             instance.status === 'failed' ? 'rgba(255, 20, 147, 0.2)' :
                             (instance.status === 'processing' || instance.status === 'running') ? 'rgba(255, 107, 0, 0.2)' :
                             'rgba(124, 124, 138, 0.2)',
                  border: `1px solid ${
                    instance.status === 'completed' ? 'var(--gaming-neon-green)' :
                    instance.status === 'failed' ? 'var(--gaming-neon-pink)' :
                    (instance.status === 'processing' || instance.status === 'running') ? 'var(--gaming-neon-orange)' :
                    'var(--gaming-neutral)'
                  }`,
                  color: instance.status === 'completed' ? 'var(--gaming-neon-green)' :
                         instance.status === 'failed' ? 'var(--gaming-neon-pink)' :
                         (instance.status === 'processing' || instance.status === 'running') ? 'var(--gaming-neon-orange)' :
                         'var(--gaming-neutral)',
                  boxShadow: instance.status === 'completed' ? '0 0 10px rgba(57, 255, 20, 0.3)' :
                            instance.status === 'failed' ? '0 0 10px rgba(255, 20, 147, 0.3)' :
                            (instance.status === 'processing' || instance.status === 'running') ? '0 0 10px rgba(255, 107, 0, 0.3)' :
                            'none'
                }}>
                  {instance.status}
                </div>
                
                {/* Individual delete button */}
                {canDelete && (
                  <button
                    onClick={() => handleDeleteInstance(instance.id)}
                    disabled={isDeleting}
                    className="p-1.5 rounded-lg transition-all duration-200 hover:scale-110"
                    style={{
                      background: 'rgba(255, 20, 147, 0.1)',
                      border: '1px solid var(--gaming-neon-pink)',
                      color: 'var(--gaming-neon-pink)',
                      opacity: isDeleting ? 0.5 : 1
                    }}
                    title="Delete this task"
                  >
                    <TrashIcon className="h-3 w-3" />
                  </button>
                )}
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
                      className="mt-2 p-3 rounded-lg border text-sm"
                      style={{
                        background: 'var(--gaming-bg-elevated)',
                        borderColor: 'var(--gaming-border)',
                        boxShadow: '0 0 10px rgba(0, 255, 255, 0.1)'
                      }}
                    >
                      <div className="max-h-48 overflow-y-auto">
                        {(() => {
                          // Handle different result formats
                          if (!instance.result) {
                            return (
                              <p className="italic" style={{ color: 'var(--gaming-text-muted)' }}>
                                No result available
                              </p>
                            );
                          }
                          
                          if (typeof instance.result === 'string') {
                            // Handle string results
                            if (!instance.result.trim()) {
                              return (
                                <p className="italic" style={{ color: 'var(--gaming-text-muted)' }}>
                                  Task completed with no output
                                </p>
                              );
                            }
                            
                            const maxLength = 500;
                            const truncated = instance.result.length > maxLength 
                              ? `${instance.result.substring(0, maxLength)}...` 
                              : instance.result;
                            
                            return (
                              <p className="whitespace-pre-wrap" style={{ 
                                color: 'var(--gaming-text-primary)',
                                fontFamily: 'var(--font-mono)',
                                fontSize: '12px',
                                lineHeight: '1.4'
                              }}>
                                {truncated}
                              </p>
                            );
                          }
                          
                          if (instance.result && typeof instance.result === 'object') {
                            // Handle DBAO-style result objects
                            const result = instance.result as any;
                            const hasOutput = result.output && result.output.trim();
                            const hasSuccess = result.success !== undefined;
                            const hasTokenUsage = result.token_usage?.total_tokens;
                            const hasExecutionTime = result.execution_time;
                            
                            return (
                              <div className="space-y-3">
                                {/* Main Content */}
                                {hasOutput ? (
                                  <div>
                                    <h5 className="text-xs font-bold uppercase mb-2" style={{ 
                                      color: 'var(--gaming-neon-green)' 
                                    }}>
                                      Agent Output:
                                    </h5>
                                    <p className="whitespace-pre-wrap" style={{ 
                                      color: 'var(--gaming-text-primary)',
                                      fontFamily: 'var(--font-mono)',
                                      fontSize: '12px',
                                      lineHeight: '1.4'
                                    }}>
                                      {result.output.length > 500 
                                        ? `${result.output.substring(0, 500)}...` 
                                        : result.output}
                                    </p>
                                  </div>
                                ) : (
                                  <div className="p-3 rounded-lg" style={{
                                    background: 'rgba(255, 107, 0, 0.1)',
                                    border: '1px solid var(--gaming-neon-orange)'
                                  }}>
                                    <div className="flex items-center gap-2 mb-2">
                                      <div className="w-2 h-2 rounded-full" style={{ 
                                        background: 'var(--gaming-neon-orange)' 
                                      }}></div>
                                      <span className="text-xs font-bold uppercase" style={{ 
                                        color: 'var(--gaming-neon-orange)' 
                                      }}>
                                        Empty Output
                                      </span>
                                    </div>
                                    <p className="text-xs" style={{ 
                                      color: 'var(--gaming-text-secondary)',
                                      fontFamily: 'var(--font-mono)'
                                    }}>
                                      {hasSuccess && result.success 
                                        ? 'Task completed successfully but produced no visible output'
                                        : 'Task execution may have failed or been interrupted'}
                                    </p>
                                  </div>
                                )}

                                {/* Execution Metrics */}
                                {(hasTokenUsage || hasExecutionTime || hasSuccess !== undefined) && (
                                  <div className="pt-2 border-t" style={{ borderColor: 'var(--gaming-border)' }}>
                                    <div className="flex items-center flex-wrap gap-4">
                                      {hasSuccess !== undefined && (
                                        <span className="text-xs flex items-center gap-1" style={{ 
                                          color: result.success ? 'var(--gaming-neon-green)' : 'var(--gaming-neon-pink)' 
                                        }}>
                                          <div className={`w-1.5 h-1.5 rounded-full ${
                                            result.success ? 'bg-green-400' : 'bg-red-400'
                                          }`}></div>
                                          {result.success ? 'SUCCESS' : 'FAILED'}
                                        </span>
                                      )}
                                      {hasTokenUsage && (
                                        <span className="text-xs" style={{ color: 'var(--gaming-neon-cyan)' }}>
                                          🔢 {result.token_usage.total_tokens.toLocaleString()} tokens
                                        </span>
                                      )}
                                      {hasExecutionTime && (
                                        <span className="text-xs" style={{ color: 'var(--gaming-neon-purple)' }}>
                                          ⏱️ {result.execution_time.toFixed(1)}s
                                        </span>
                                      )}
                                    </div>
                                  </div>
                                )}
                              </div>
                            );
                          }
                          
                          // Fallback for unknown object types
                          return (
                            <div className="space-y-2">
                              <h5 className="text-xs font-bold uppercase" style={{ 
                                color: 'var(--gaming-neon-purple)' 
                              }}>
                                Raw Result:
                              </h5>
                              <pre className="text-xs overflow-x-auto" style={{ 
                                color: 'var(--gaming-text-secondary)',
                                fontFamily: 'var(--font-mono)',
                                background: 'rgba(0, 0, 0, 0.3)',
                                padding: '8px',
                                borderRadius: '4px'
                              }}>
                                {JSON.stringify(instance.result, null, 2)}
                              </pre>
                            </div>
                          );
                        })()}
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
        </div>
        </div>
      </motion.div>
    );
  };

  return (
    <div className={`space-y-6 ${className}`} style={{ background: 'var(--gaming-bg-primary)' }}>
      {/* Execution Panel - Cyberpunk Command Interface */}
      <div className="gaming-card relative overflow-hidden">
        <div className="gaming-border-glow"></div>
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-cyan-500 via-purple-500 to-pink-500 opacity-70 animate-pulse"></div>
        
        <div className="flex items-center justify-between mb-6">
          <div className="relative">
            <h2 className="text-2xl font-black uppercase tracking-wider flex items-center" style={{
              color: 'var(--gaming-neon-cyan)',
              fontFamily: 'var(--font-mono)',
              textShadow: '0 0 20px rgba(0, 255, 255, 0.5)'
            }}>
              <div className="relative mr-4">
                <BoltIcon className="h-8 w-8" style={{ 
                  color: 'var(--gaming-neon-cyan)',
                  filter: 'drop-shadow(0 0 15px rgba(0, 255, 255, 0.8))'
                }} />
                <div className="absolute inset-0 rounded-full bg-cyan-400/20 animate-ping"></div>
              </div>
              AGENT CONTROL
            </h2>
            <div className="mt-1 text-sm font-semibold uppercase tracking-wider" style={{ 
              color: 'var(--gaming-neon-purple)',
              textShadow: '0 0 10px rgba(157, 78, 221, 0.5)'
            }}>
              Neural Network Interface
            </div>
          </div>
          
          <div className="flex items-center space-x-6">
            {/* Connection Status - Cyberpunk Style */}
            <div className="flex items-center space-x-3">
              {wsConnected ? (
                <div className="flex items-center">
                  <div className="relative mr-2">
                    <div className="h-3 w-3 rounded-full animate-pulse" style={{
                      background: 'var(--gaming-neon-green)',
                      boxShadow: '0 0 15px rgba(57, 255, 20, 0.8)'
                    }} />
                    <div className="absolute inset-0 rounded-full bg-green-400/30 animate-ping"></div>
                  </div>
                  <span className="text-sm font-bold uppercase tracking-wider" style={{ 
                    color: 'var(--gaming-neon-green)',
                    textShadow: '0 0 10px rgba(57, 255, 20, 0.5)'
                  }}>
                    NEURAL LINK ACTIVE
                  </span>
                </div>
              ) : wsConnecting ? (
                <div className="flex items-center">
                  <div className="mr-2" style={{ color: 'var(--gaming-neon-orange)' }}>
                    <LoadingSpinner size="sm" />
                  </div>
                  <span className="text-sm font-bold uppercase tracking-wider" style={{ 
                    color: 'var(--gaming-neon-orange)',
                    textShadow: '0 0 10px rgba(255, 107, 0, 0.5)'
                  }}>
                    ESTABLISHING LINK...
                  </span>
                </div>
              ) : (
                <div className="flex items-center">
                  <div className="h-3 w-3 rounded-full mr-2" style={{
                    background: 'var(--gaming-neon-pink)',
                    boxShadow: '0 0 15px rgba(255, 20, 147, 0.8)'
                  }} />
                  <span className="text-sm font-bold uppercase tracking-wider" style={{ 
                    color: 'var(--gaming-neon-pink)',
                    textShadow: '0 0 10px rgba(255, 20, 147, 0.5)'
                  }}>
                    LINK OFFLINE
                  </span>
                </div>
              )}
            </div>

            {/* Stats - Gaming Style */}
            <div className="flex items-center space-x-4">
              {runningInstances.length > 0 && (
                <div className="relative px-3 py-1 rounded-lg border" style={{
                  background: 'rgba(57, 255, 20, 0.1)',
                  borderColor: 'var(--gaming-neon-green)',
                  boxShadow: '0 0 10px rgba(57, 255, 20, 0.2)'
                }}>
                  <span className="text-xs font-bold uppercase tracking-wider" style={{ 
                    color: 'var(--gaming-neon-green)',
                    fontFamily: 'var(--font-mono)'
                  }}>
                    {runningInstances.length} ACTIVE
                  </span>
                </div>
              )}
              <div className="text-sm font-semibold" style={{ 
                color: 'var(--gaming-text-secondary)',
                fontFamily: 'var(--font-mono)'
              }}>
                TOTAL: {recentInstances.length.toString().padStart(3, '0')}
              </div>
            </div>
          </div>
        </div>

        {/* Task Input - Cyberpunk Interface */}
        <div className="space-y-4">
          <div className="relative">
            <label className="block text-sm font-bold uppercase tracking-wider mb-3" style={{
              color: 'var(--gaming-text-secondary)',
              fontFamily: 'var(--font-mono)'
            }}>
              Mission Parameters
            </label>
            <div className="relative">
              <textarea
                ref={taskInputRef}
                value={taskDescription}
                onChange={(e) => setTaskDescription(e.target.value)}
                placeholder="Input your mission objectives and parameters..."
                className="w-full px-4 py-3 rounded-lg resize-none min-h-[100px] transition-all duration-300 focus:outline-none"
                style={{
                  background: 'var(--gaming-bg-elevated)',
                  border: `2px solid ${taskDescription ? 'var(--gaming-neon-cyan)' : 'var(--gaming-border)'}`,
                  color: 'var(--gaming-text-primary)',
                  fontFamily: 'var(--font-mono)',
                  fontSize: '14px',
                  boxShadow: taskDescription ? '0 0 15px rgba(0, 255, 255, 0.2)' : 'none'
                }}
                onFocus={(e) => {
                  e.target.style.borderColor = 'var(--gaming-neon-cyan)';
                  e.target.style.boxShadow = '0 0 20px rgba(0, 255, 255, 0.3)';
                }}
                onBlur={(e) => {
                  if (!taskDescription) {
                    e.target.style.borderColor = 'var(--gaming-border)';
                    e.target.style.boxShadow = 'none';
                  }
                }}
                rows={3}
              />
              {/* Neon Border Animation */}
              <div className={`absolute inset-0 rounded-lg border-2 border-transparent transition-opacity duration-300 pointer-events-none ${
                taskDescription ? 'opacity-100' : 'opacity-0'
              }`} style={{
                background: 'linear-gradient(45deg, transparent, var(--gaming-neon-cyan), transparent)',
                animation: taskDescription ? 'border-flow 3s linear infinite' : 'none'
              }}></div>
            </div>
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

          {/* Execute Button - Cyberpunk Launch Sequence */}
          <div className="relative">
            <div className={`absolute inset-0 rounded-lg bg-gradient-to-r from-cyan-500 via-purple-500 to-pink-500 opacity-30 blur-sm transition-all duration-300 ${
              isExecuting ? 'animate-pulse scale-110' : 'scale-100'
            } ${!taskDescription.trim() || !selectedAgent ? 'opacity-10' : 'opacity-30'}`}></div>
            
            <Button
              onClick={handleExecute}
              disabled={isExecuting || !taskDescription.trim() || !selectedAgent}
              className="relative w-full py-4 text-lg font-black uppercase tracking-wider transition-all duration-300 hover:transform hover:scale-105"
              style={{
                background: isExecuting 
                  ? 'linear-gradient(45deg, var(--gaming-neon-green), var(--gaming-neon-cyan))'
                  : taskDescription.trim() && selectedAgent
                    ? 'var(--gaming-bg-secondary)'
                    : 'var(--gaming-bg-elevated)',
                border: `2px solid ${
                  isExecuting 
                    ? 'var(--gaming-neon-green)'
                    : taskDescription.trim() && selectedAgent
                      ? 'var(--gaming-neon-cyan)'
                      : 'var(--gaming-border)'
                }`,
                color: isExecuting 
                  ? 'var(--gaming-bg-primary)'
                  : taskDescription.trim() && selectedAgent
                    ? 'var(--gaming-neon-cyan)'
                    : 'var(--gaming-text-muted)',
                boxShadow: isExecuting 
                  ? '0 0 25px rgba(57, 255, 20, 0.6)'
                  : taskDescription.trim() && selectedAgent
                    ? '0 0 20px rgba(0, 255, 255, 0.3)'
                    : 'none',
                textShadow: isExecuting 
                  ? '0 0 10px rgba(10, 10, 15, 0.8)'
                  : taskDescription.trim() && selectedAgent
                    ? '0 0 10px rgba(0, 255, 255, 0.5)'
                    : 'none'
              }}
            >
              <div className="flex items-center justify-center gap-3">
                {isExecuting ? (
                  <>
                    <div className="animate-spin">
                      <LoadingSpinner size="sm" />
                    </div>
                    EXECUTING MISSION...
                  </>
                ) : (
                  <>
                    <PlayIcon className="h-6 w-6" style={{ 
                      filter: taskDescription.trim() && selectedAgent 
                        ? 'drop-shadow(0 0 8px rgba(0, 255, 255, 0.8))' 
                        : 'none'
                    }} />
                    INITIATE AGENT
                  </>
                )}
              </div>
            </Button>
          </div>
        </div>
      </div>

      {/* Results Section - Cyberpunk Mission Log */}
      <div className="gaming-card relative overflow-hidden">
        <div className="gaming-border-glow"></div>
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-purple-500 via-green-500 to-purple-500 opacity-60"></div>
        
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <DocumentTextIcon className="h-6 w-6" style={{ 
              color: 'var(--gaming-neon-purple)',
              filter: 'drop-shadow(0 0 10px rgba(157, 78, 221, 0.7))'
            }} />
            <h3 className="text-xl font-black uppercase tracking-wider" style={{
              color: 'var(--gaming-neon-purple)',
              fontFamily: 'var(--font-mono)',
              textShadow: '0 0 15px rgba(157, 78, 221, 0.5)'
            }}>
              Mission Archive
            </h3>
          </div>
          
          <div className="flex items-center space-x-3">
            {/* Bulk actions - only show if tasks are selected */}
            {selectedInstanceIds.size > 0 && (
              <div className="flex items-center space-x-2">
                <span className="text-xs font-bold uppercase tracking-wider" style={{ 
                  color: 'var(--gaming-neon-cyan)' 
                }}>
                  {selectedInstanceIds.size} SELECTED
                </span>
                <Button
                  onClick={handleDeleteSelected}
                  disabled={isDeleting}
                  className="text-xs font-bold uppercase tracking-wider px-3 py-1"
                  style={{
                    background: 'rgba(255, 20, 147, 0.2)',
                    border: '1px solid var(--gaming-neon-pink)',
                    color: 'var(--gaming-neon-pink)',
                    boxShadow: '0 0 10px rgba(255, 20, 147, 0.2)'
                  }}
                  icon={isDeleting ? <LoadingSpinner size="sm" /> : <TrashIcon className="h-3 w-3" />}
                >
                  {isDeleting ? 'DELETING...' : 'DELETE'}
                </Button>
                <Button
                  onClick={clearSelection}
                  variant="ghost"
                  className="text-xs px-2 py-1"
                  style={{ color: 'var(--gaming-text-muted)' }}
                >
                  CLEAR
                </Button>
              </div>
            )}
            
            {/* Select All / Archive controls */}
            {recentInstances.length > 0 && (
              <div className="flex items-center space-x-2">
                {selectedInstanceIds.size === 0 ? (
                  <Button
                    onClick={selectAllInstances}
                    variant="ghost"
                    className="text-xs px-2 py-1"
                    style={{ color: 'var(--gaming-neon-cyan)' }}
                  >
                    SELECT ALL
                  </Button>
                ) : selectedInstanceIds.size < recentInstances.length ? (
                  <Button
                    onClick={selectAllInstances}
                    variant="ghost"
                    className="text-xs px-2 py-1"
                    style={{ color: 'var(--gaming-neon-cyan)' }}
                  >
                    SELECT ALL
                  </Button>
                ) : null}
              </div>
            )}
            
            <div className="relative">
              <Button
                onClick={() => setShowResults(!showResults)}
                className="font-bold uppercase tracking-wider px-4 py-2"
                style={{
                  background: 'var(--gaming-bg-elevated)',
                  border: `2px solid var(--gaming-neon-purple)`,
                  color: 'var(--gaming-neon-purple)',
                  boxShadow: '0 0 10px rgba(157, 78, 221, 0.2)'
                }}
              >
                <div className="flex items-center gap-2">
                  {showResults ? <ChevronUpIcon className="h-4 w-4" /> : <ChevronDownIcon className="h-4 w-4" />}
                  {showResults ? 'COLLAPSE' : 'EXPAND'} 
                  <span className="px-2 py-1 rounded text-xs" style={{
                    background: 'rgba(157, 78, 221, 0.2)',
                    color: 'var(--gaming-neon-purple)',
                    fontFamily: 'var(--font-mono)'
                  }}>
                    {recentInstances.length.toString().padStart(2, '0')}
                  </span>
                </div>
              </Button>
            </div>
          </div>
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
                      <InstanceCard key={instance.id} instance={instance} allowSelection={false} />
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
      </div>
    </div>
  );
};