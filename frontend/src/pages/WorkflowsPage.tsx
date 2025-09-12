import React, { useState, useEffect } from 'react';
import { Card } from '@/components/common/Card';
import { Button } from '@/components/common/Button';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select-proper';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  PlusIcon, 
  PlayIcon, 
  EyeIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  CpuChipIcon,
  ArrowPathIcon,
  DocumentTextIcon,
  ChartBarIcon,
  SparklesIcon
} from '@heroicons/react/24/outline';
import '../styles/gaming-theme.css';
import { workflowsService } from '@/services/workflows.service';
import { agentDiscoveryService } from '@/services/agentDiscovery.service';
import { toast } from 'sonner';

interface Workflow {
  id: string;
  name: string;
  description: string;
  agent_count: number;
  created_at: string;
  version: string;
}

interface WorkflowTemplate {
  name: string;
  description: string;
  agents: Array<{
    name: string;
    order: number;
    params?: Record<string, any>;
    input_from?: string | string[];
  }>;
  flow_config: {
    type: string;
    error_handling?: string;
    save_intermediate?: boolean;
    feedback_loops?: boolean;
    max_iterations?: number;
    merge_strategy?: string;
  };
}

interface Agent {
  id: string;
  name: string;
  description: string;
  capabilities: any[];
  specialization: string;
  status?: 'active' | 'inactive';
}

interface WorkflowExecution {
  id: string;
  workflow_name: string;
  status: 'running' | 'completed' | 'failed' | 'stopped';
  started_at: string;
  completed_at?: string;
  prompt?: string;
  result?: any;
  progress?: {
    current_step: number;
    total_steps: number;
    message: string;
  };
}

export default function WorkflowsPage() {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [templates, setTemplates] = useState<WorkflowTemplate[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [executing, setExecuting] = useState<string | null>(null);
  const [templateDialogOpen, setTemplateDialogOpen] = useState(false);
  const [executions, setExecutions] = useState<WorkflowExecution[]>([]);
  const [selectedExecution, setSelectedExecution] = useState<WorkflowExecution | null>(null);
  const [executionDialogOpen, setExecutionDialogOpen] = useState(false);

  // Create workflow form state
  const [newWorkflow, setNewWorkflow] = useState({
    name: '',
    description: '',
    agents: [] as Array<{name: string; order: number; params?: Record<string, any>}>,
    flow_config: {
      type: 'sequential',
      error_handling: 'stop',
      save_intermediate: true
    }
  });

  // Execute workflow form state
  const [executeForm, setExecuteForm] = useState({
    workflow_name: '',
    prompt: '',
    params: {}
  });

  useEffect(() => {
    // Add gaming theme to body
    document.body.classList.add('gaming-theme');
    
    loadData();
    loadExecutionHistory();
    
    // Poll for updates on running executions every 5 seconds
    const interval = setInterval(() => {
      updateRunningExecutions();
    }, 5000);
    
    return () => {
      document.body.classList.remove('gaming-theme');
      clearInterval(interval);
    };
  }, []);

  const loadExecutionHistory = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/workflows/history/', {
        headers: {
          'Authorization': `Token ${localStorage.getItem('auth_token') || '993f8273f70877e23b5c7d2f92ed30562a089fe3'}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        const mappedExecutions: WorkflowExecution[] = data.executions.map((exec: any) => ({
          id: exec.execution_id,
          workflow_name: exec.workflow_name,
          status: exec.status,
          started_at: exec.started_at,
          completed_at: exec.completed_at,
          prompt: exec.prompt,
          progress: exec.progress
        }));
        setExecutions(mappedExecutions);
        console.log('Loaded execution history:', mappedExecutions);
      }
    } catch (error) {
      console.error('Error loading execution history:', error);
    }
  };

  const loadData = async () => {
    try {
      const [workflowsData, templatesData, agentsData] = await Promise.all([
        workflowsService.listWorkflows(),
        workflowsService.getWorkflowTemplates(),
        agentDiscoveryService.discoverAllAgents()
      ]);

      console.log('WorkflowsPage API responses:', { workflowsData, templatesData, agentsData });

      const extractedWorkflows = workflowsData?.workflows || [];
      const extractedTemplates = templatesData?.templates || [];  
      const extractedAgents = agentsData?.agents || [];

      console.log('WorkflowsPage extracted data:', { 
        workflows: extractedWorkflows.length,
        templates: extractedTemplates.length,  
        agents: extractedAgents.length
      });

      setWorkflows(extractedWorkflows);
      setTemplates(extractedTemplates);
      setAgents(extractedAgents);

      console.log('WorkflowsPage state updated');
    } catch (error) {
      console.error('Error loading workflow data:', error);
      toast.error('Failed to load workflow data');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateWorkflow = async () => {
    if (!newWorkflow.name || newWorkflow.agents.length === 0) {
      toast.error('Please provide a name and at least one agent');
      return;
    }

    setCreating(true);
    try {
      await workflowsService.createWorkflow(newWorkflow);
      toast.success('Workflow created successfully');
      setNewWorkflow({
        name: '',
        description: '',
        agents: [],
        flow_config: {
          type: 'sequential' as 'sequential' | 'parallel',
          error_handling: 'stop' as 'stop' | 'continue',
          save_intermediate: true
        }
      });
      loadData();
    } catch (error) {
      console.error('Error creating workflow:', error);
      toast.error('Failed to create workflow');
    } finally {
      setCreating(false);
    }
  };

  const handleExecuteWorkflow = async (workflowName: string, prompt: string = '') => {
    setExecuting(workflowName);
    try {
      const result = await workflowsService.executeWorkflow({
        workflow_name: workflowName,
        prompt: prompt || executeForm.prompt,
        params: executeForm.params
      });
      
      // Add to executions tracking
      const newExecution: WorkflowExecution = {
        id: result.conversation_id || result.execution_result?.execution_id || '',
        workflow_name: workflowName,
        status: 'running',
        started_at: new Date().toISOString(),
        prompt: prompt || executeForm.prompt
      };
      
      setExecutions(prev => [newExecution, ...prev]);
      
      toast.success(`Workflow "${workflowName}" started! Execution ID: ${newExecution.id.slice(0, 8)}...`);
      
      // Simulate completion after 5 seconds (in production, this would poll for real status)
      setTimeout(() => {
        setExecutions(prev => prev.map(exec => 
          exec.id === newExecution.id 
            ? { ...exec, status: 'completed' as const }
            : exec
        ));
        toast.success(`Workflow "${workflowName}" completed!`);
        // Reload history to get latest data
        loadExecutionHistory();
      }, 5000);
      
    } catch (error) {
      console.error('Error executing workflow:', error);
      toast.error('Failed to execute workflow');
    } finally {
      setExecuting(null);
    }
  };

  const handleViewExecution = (execution: WorkflowExecution) => {
    setSelectedExecution(execution);
    setExecutionDialogOpen(true);
  };

  const handleStopExecution = async (executionId: string) => {
    try {
      // Update local state
      setExecutions(prev => prev.map(exec => 
        exec.id === executionId 
          ? { ...exec, status: 'stopped' as const }
          : exec
      ));
      
      toast.success('Workflow execution stopped');
      
      // In production, this would call an API to actually stop the execution
      // await workflowsService.stopExecution(executionId);
    } catch (error) {
      console.error('Error stopping execution:', error);
      toast.error('Failed to stop execution');
    }
  };

  const updateRunningExecutions = async () => {
    try {
      // Get all running executions
      const runningExecutions = executions.filter(exec => exec.status === 'running');
      
      if (runningExecutions.length === 0) {
        return; // No running executions to update
      }

      // Poll status for each running execution
      const updatedExecutions = await Promise.all(
        runningExecutions.map(async (execution) => {
          try {
            const response = await fetch(`${API_BASE}/workflows/status/${execution.id}/`, {
              headers: {
                'Authorization': `Token ${authToken}`,
                'Content-Type': 'application/json'
              }
            });

            if (response.ok) {
              const statusData = await response.json();
              return {
                ...execution,
                status: statusData.status as 'running' | 'completed' | 'failed',
                progress: statusData.progress,
                result: statusData.result,
                completed_at: statusData.completed_at
              };
            }
          } catch (error) {
            console.error(`Error updating execution ${execution.id}:`, error);
          }
          return execution; // Return unchanged if error
        })
      );

      // Update state with new execution data
      setExecutions(prev => prev.map(exec => {
        const updated = updatedExecutions.find(updated => updated.id === exec.id);
        return updated || exec;
      }));

      // Show completion notifications for newly completed workflows
      updatedExecutions.forEach(execution => {
        const oldExecution = executions.find(e => e.id === execution.id);
        if (oldExecution?.status === 'running' && execution.status === 'completed') {
          toast.success(`Workflow "${execution.workflow_name}" completed!`);
        }
      });

    } catch (error) {
      console.error('Error updating running executions:', error);
    }
  };

  const handleUseTemplate = (template: WorkflowTemplate) => {
    setNewWorkflow({
      name: template.name,
      description: template.description,
      agents: template.agents || [],
      flow_config: {
        type: (template.flow_config?.type || 'sequential') as 'sequential' | 'parallel',
        error_handling: (template.flow_config?.error_handling || 'stop') as 'stop' | 'continue',
        save_intermediate: template.flow_config?.save_intermediate ?? true
      }
    });
    setTemplateDialogOpen(true);
  };

  const addAgentToWorkflow = () => {
    setNewWorkflow(prev => ({
      ...prev,
      agents: [
        ...prev.agents,
        {
          name: '',
          order: prev.agents.length + 1,
          params: {}
        }
      ]
    }));
  };

  const removeAgentFromWorkflow = (index: number) => {
    setNewWorkflow(prev => ({
      ...prev,
      agents: prev.agents.filter((_, i) => i !== index)
    }));
  };

  const updateWorkflowAgent = (index: number, field: string, value: any) => {
    setNewWorkflow(prev => ({
      ...prev,
      agents: prev.agents.map((agent, i) => 
        i === index ? { ...agent, [field]: value } : agent
      )
    }));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Gaming Header */}
      <div className="gaming-card relative overflow-hidden mb-8">
        <div className="gaming-border-glow"></div>
        
        {/* Cyberpunk background pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="w-full h-full" style={{backgroundImage: 'linear-gradient(45deg, transparent 40%, var(--gaming-neon-cyan) 50%, transparent 60%)', backgroundSize: '20px 20px'}}></div>
        </div>
        
        <div className="relative flex items-center justify-between p-8">
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 gaming-card border-gaming-neon-cyan flex items-center justify-center">
                <CpuChipIcon className="w-8 h-8 gaming-text-neon" />
              </div>
              <h1 className="text-5xl font-black gaming-text-primary text-shadow-lg">
                MULTI-AGENT <span className="gaming-text-neon">NEURAL</span> MATRIX
              </h1>
            </div>
            
            <p className="gaming-text-secondary text-xl font-bold font-mono">
              [ORCHESTRATING PARALLEL AGENT PROTOCOLS] &gt;&gt; NEURAL WORKFLOW MATRIX
            </p>
            
            {/* Gaming Status Indicators */}
            <div className="flex items-center gap-4">
              <div className="gaming-status gaming-status-live">
                <div className="gaming-pulse-dot"></div>
                <ArrowPathIcon className="w-4 h-4" />
                AGENTS ONLINE
              </div>
              
              <div className="gaming-status bg-gaming-neon-cyan/20 border-gaming-neon-cyan text-gaming-neon-cyan">
                <CpuChipIcon className="w-4 h-4" />
                NEURAL SYNC
              </div>
              
              <div className="gaming-status bg-gaming-neon-purple/20 border-gaming-neon-purple text-gaming-neon-purple">
                <ChartBarIcon className="w-4 h-4" />
                WORKFLOW MATRIX
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            <Button 
              onClick={() => setTemplateDialogOpen(true)}
              className="gaming-btn-active px-8 py-4 text-lg">
              <PlusIcon className="h-5 w-5 mr-3" />
              INITIATE NEURAL MATRIX
            </Button>
          </div>
        </div>
      </div>

      <Dialog open={templateDialogOpen} onOpenChange={setTemplateDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto gaming-card border-gaming-neon-cyan">
            <DialogHeader>
              <DialogTitle className="text-white text-2xl font-bold gaming-text-primary">
                <CpuChipIcon className="w-6 h-6 mr-2 gaming-text-neon inline" />
                NEURAL MATRIX ARCHITECT
              </DialogTitle>
              <DialogDescription className="gaming-text-secondary font-mono">
                &gt;&gt; DESIGN MULTI-AGENT WORKFLOW PROTOCOLS FOR NEURAL COORDINATION
              </DialogDescription>
            </DialogHeader>
            
            <Tabs defaultValue="design" className="w-full">
              <TabsList className="grid w-full grid-cols-2 bg-dark-700">
                <TabsTrigger value="design">Design</TabsTrigger>
                <TabsTrigger value="templates">Templates</TabsTrigger>
              </TabsList>
              
              <TabsContent value="design" className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="workflow-name" className="text-gray-300">Workflow Name</Label>
                    <input
                      id="workflow-name"
                      type="text"
                      value={newWorkflow.name}
                      onChange={(e) => setNewWorkflow(prev => ({...prev, name: e.target.value}))}
                      placeholder="My Custom Workflow"
                      className="w-full px-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                  <div>
                    <Label htmlFor="flow-type" className="text-gray-300">Flow Type</Label>
                    <Select
                      value={newWorkflow.flow_config.type}
                      onValueChange={(value) => setNewWorkflow(prev => ({
                        ...prev,
                        flow_config: {...prev.flow_config, type: value}
                      }))}
                    >
                      <SelectTrigger className="bg-dark-700 border-dark-600 text-white">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="sequential">Sequential</SelectItem>
                        <SelectItem value="parallel">Parallel</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                
                <div>
                  <Label htmlFor="workflow-description" className="text-gray-300">Description</Label>
                  <textarea
                    id="workflow-description"
                    value={newWorkflow.description}
                    onChange={(e) => setNewWorkflow(prev => ({...prev, description: e.target.value}))}
                    placeholder="Describe what this workflow does..."
                    rows={3}
                    className="w-full px-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <Label className="text-gray-300">Agents</Label>
                    <Button variant="outline" size="sm" onClick={addAgentToWorkflow}>
                      <PlusIcon className="h-4 w-4" />
                      Add Agent
                    </Button>
                  </div>
                  
                  <div className="space-y-3 max-h-60 overflow-y-auto">
                    {(newWorkflow.agents || []).map((agent, index) => (
                      <Card key={index} className="p-3">
                        <div className="grid grid-cols-3 gap-3 items-center">
                          <div>
                            <Label className="text-xs text-gray-400">Agent</Label>
                            <Select
                              value={agent.name}
                              onValueChange={(value) => updateWorkflowAgent(index, 'name', value)}
                            >
                              <SelectTrigger className="h-8 bg-dark-700 border-dark-600 text-white">
                                <SelectValue placeholder="Select agent" />
                              </SelectTrigger>
                              <SelectContent>
                                {agents.map((a) => (
                                  <SelectItem key={a.name} value={a.name}>
                                    {a.name}
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          </div>
                          
                          <div>
                            <Label className="text-xs text-gray-400">Order</Label>
                            <input
                              type="number"
                              value={agent.order}
                              onChange={(e) => updateWorkflowAgent(index, 'order', parseInt(e.target.value))}
                              className="w-full px-2 py-1 bg-dark-700 border border-dark-600 rounded text-white h-8"
                              min={1}
                            />
                          </div>
                          
                          <div className="flex justify-end">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => removeAgentFromWorkflow(index)}
                              className="text-red-400 hover:text-red-300"
                            >
                              <XCircleIcon className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </Card>
                    ))}
                  </div>
                </div>
                
                <div className="flex justify-end">
                  <Button 
                    onClick={handleCreateWorkflow}
                    disabled={creating}
                  >
                    {creating ? (
                      <ArrowPathIcon className="h-4 w-4 animate-spin" />
                    ) : (
                      <CheckCircleIcon className="h-4 w-4" />
                    )}
                    Create Workflow
                  </Button>
                </div>
              </TabsContent>
              
              <TabsContent value="templates" className="space-y-4">
                <div className="grid grid-cols-1 gap-4 max-h-96 overflow-y-auto">
                  {templates.map((template, index) => (
                    <Card key={index} className="p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="font-semibold text-white">{template.name}</h3>
                          <p className="text-sm text-gray-400 mt-1">{template.description}</p>
                          <div className="flex items-center gap-2 mt-2">
                            <Badge variant="outline" className="text-gray-300 border-gray-600">
                              {template.agents?.length || 0} agents
                            </Badge>
                            <Badge variant="outline" className="text-gray-300 border-gray-600">
                              {template.flow_config?.type || 'sequential'}
                            </Badge>
                          </div>
                        </div>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleUseTemplate(template)}
                        >
                          Use Template
                        </Button>
                      </div>
                    </Card>
                  ))}
                </div>
              </TabsContent>
            </Tabs>
          </DialogContent>
        </Dialog>
      

      {/* Neural Matrix Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="gaming-card gaming-hover-lift">
          <div className="gaming-border-glow"></div>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs gaming-text-secondary font-mono uppercase tracking-wide">ACTIVE NEURAL MATRICES</p>
              <p className="text-3xl font-black gaming-text-neon font-mono">{workflows.length}</p>
            </div>
            <div className="w-12 h-12 gaming-card border-gaming-neon-cyan flex items-center justify-center">
              <CpuChipIcon className="h-6 w-6 gaming-text-neon" />
            </div>
          </div>
        </div>
        
        <div className="gaming-card gaming-hover-lift">
          <div className="gaming-border-glow"></div>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs gaming-text-secondary font-mono uppercase tracking-wide">PROTOCOL TEMPLATES</p>
              <p className="text-3xl font-black text-gaming-neon-purple font-mono">{templates.length}</p>
            </div>
            <div className="w-12 h-12 gaming-card border-gaming-neon-purple flex items-center justify-center">
              <DocumentTextIcon className="h-6 w-6 text-gaming-neon-purple" />
            </div>
          </div>
        </div>
        
        <div className="gaming-card gaming-hover-lift">
          <div className="gaming-border-glow"></div>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs gaming-text-secondary font-mono uppercase tracking-wide">NEURAL AGENTS</p>
              <p className="text-3xl font-black gaming-text-neon font-mono">{agents.length}</p>
            </div>
            <div className="w-12 h-12 gaming-card border-gaming-neon-cyan flex items-center justify-center">
              <SparklesIcon className="h-6 w-6 gaming-text-neon" />
            </div>
          </div>
        </div>
        
        <div className="gaming-card gaming-hover-lift">
          <div className="gaming-border-glow"></div>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs gaming-text-secondary font-mono uppercase tracking-wide">MATRIX EXECUTIONS</p>
              <p className="text-3xl font-black gaming-text-matrix font-mono">{executions.length}</p>
            </div>
            <div className="w-12 h-12 gaming-card border-gaming-neon-green flex items-center justify-center">
              <ChartBarIcon className="h-6 w-6 gaming-text-matrix" />
            </div>
          </div>
        </div>
      </div>

      {/* Matrix Execution History */}
      {executions.length > 0 && (
        <div className="gaming-card">
          <div className="gaming-border-glow"></div>
          <div className="mb-6">
            <div className="flex items-center gap-3 mb-2">
              <ChartBarIcon className="w-6 h-6 gaming-text-neon" />
              <h3 className="text-2xl font-black gaming-text-primary">NEURAL MATRIX EXECUTIONS</h3>
            </div>
            <p className="gaming-text-secondary font-mono">&gt;&gt; REAL-TIME EXECUTION STATUS MONITORING</p>
          </div>
          <div className="space-y-3 max-h-60 overflow-y-auto">
            {executions.map((execution) => (
              <div key={execution.id} className="gaming-card flex items-center justify-between p-4 gaming-hover-lift">
                <div className="flex items-center gap-4">
                  {execution.status === 'running' ? (
                    <div className="gaming-status gaming-status-live">
                      <div className="gaming-pulse-dot"></div>
                      <ArrowPathIcon className="h-4 w-4 animate-spin" />
                    </div>
                  ) : execution.status === 'completed' ? (
                    <div className="gaming-status bg-gaming-neon-green/20 border-gaming-neon-green text-gaming-neon-green">
                      <CheckCircleIcon className="h-4 w-4" />
                    </div>
                  ) : execution.status === 'failed' ? (
                    <div className="gaming-status bg-gaming-neon-pink/20 border-gaming-neon-pink text-gaming-neon-pink">
                      <XCircleIcon className="h-4 w-4" />
                    </div>
                  ) : (
                    <div className="gaming-status">
                      <ClockIcon className="h-4 w-4" />
                    </div>
                  )}
                  <div>
                    <p className="font-bold gaming-text-primary text-sm uppercase tracking-wide">{execution.workflow_name}</p>
                    <p className="text-xs gaming-text-secondary font-mono">
                      MATRIX_ID: {execution.id.slice(0, 8)}... | INITIATED: {new Date(execution.started_at).toLocaleTimeString()}
                    </p>
                    {execution.prompt && (
                      <p className="text-xs gaming-text-muted mt-1 font-mono">INPUT: {execution.prompt.slice(0, 50)}...</p>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="gaming-status font-mono text-xs">
                    {execution.status.toUpperCase()}
                  </div>
                  
                  <div className="flex gap-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleViewExecution(execution)}
                      className="gaming-hover-glow p-2"
                    >
                      <EyeIcon className="h-4 w-4 gaming-text-neon" />
                    </Button>
                    
                    {execution.status === 'running' && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleStopExecution(execution.id)}
                        className="gaming-hover-glow p-2"
                      >
                        <XCircleIcon className="h-4 w-4 gaming-text-danger" />
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Neural Matrix Roster */}
      {workflows.length === 0 && templates.length === 0 ? (
        <div className="gaming-card text-center py-16">
          <div className="gaming-border-glow"></div>
          <div className="w-16 h-16 gaming-card border-gaming-neon-cyan mx-auto mb-6 flex items-center justify-center">
            <CpuChipIcon className="h-8 w-8 gaming-text-neon" />
          </div>
          <h3 className="gaming-text-primary text-xl font-bold mb-2">NEURAL MATRIX OFFLINE</h3>
          <p className="gaming-text-secondary font-mono mb-4">&gt;&gt; NO ACTIVE WORKFLOW PROTOCOLS DETECTED</p>
          <p className="gaming-text-muted text-sm font-mono">SCANNING FOR NEURAL TEMPLATES...</p>
        </div>
      ) : workflows.length === 0 && templates.length > 0 ? (
        <div className="space-y-6">
          <div className="gaming-card">
            <div className="gaming-border-glow"></div>
            <div className="mb-6">
              <div className="flex items-center gap-3 mb-2">
                <DocumentTextIcon className="w-6 h-6 text-gaming-neon-purple" />
                <h3 className="text-2xl font-black gaming-text-primary">NEURAL PROTOCOL TEMPLATES</h3>
              </div>
              <p className="gaming-text-secondary font-mono">&gt;&gt; PRE-CONFIGURED MISSION PROTOCOLS FOR INSTANT DEPLOYMENT</p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {templates.map((template, index) => (
                <div key={index} className="gaming-card gaming-hover-lift">
                  <div className="gaming-border-glow"></div>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-bold gaming-text-primary text-sm uppercase tracking-wide mb-2">{template.name}</h3>
                      <p className="gaming-text-secondary text-xs font-mono mb-3">{template.description}</p>
                      <div className="flex items-center gap-2 mt-2">
                        <div className="gaming-status text-xs">
                          <SparklesIcon className="w-3 h-3" />
                          {template.agents?.length || 0} AGENTS
                        </div>
                        <div className="gaming-status text-xs">
                          <CpuChipIcon className="w-3 h-3" />
                          {(template.flow_config?.type || 'sequential').toUpperCase()}
                        </div>
                      </div>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleUseTemplate(template)}
                      className="gaming-btn-active"
                    >
                      DEPLOY
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {workflows.map((workflow) => (
            <div key={workflow.id} className="gaming-card gaming-hover-lift flex flex-col">
              <div className="gaming-border-glow"></div>
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="font-bold gaming-text-primary text-sm uppercase tracking-wide">{workflow.name}</h3>
                  <p className="gaming-text-secondary text-xs font-mono mt-1">{workflow.description}</p>
                </div>
                <div className="w-10 h-10 gaming-card border-gaming-neon-cyan flex items-center justify-center">
                  <CpuChipIcon className="h-5 w-5 gaming-text-neon" />
                </div>
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <div className="gaming-status text-xs">
                      <SparklesIcon className="w-3 h-3" />
                      {workflow.agent_count} AGENTS
                    </div>
                    <div className="gaming-status text-xs">
                      <DocumentTextIcon className="w-3 h-3" />
                      v{workflow.version}
                    </div>
                  </div>
                  <span className="text-xs gaming-text-muted font-mono">
                    {new Date(workflow.created_at).toLocaleDateString()}
                  </span>
                </div>
                
                <div className="flex gap-2">
                  <Dialog>
                    <DialogTrigger asChild>
                      <Button variant="secondary" size="sm" className="flex-1 gaming-btn-active">
                        <PlayIcon className="h-4 w-4 mr-2" />
                        EXECUTE MATRIX
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="gaming-card border-gaming-neon-cyan">
                      <DialogHeader>
                        <DialogTitle className="gaming-text-primary text-xl font-bold">
                          <PlayIcon className="w-5 h-5 mr-2 gaming-text-neon inline" />
                          EXECUTE NEURAL MATRIX
                        </DialogTitle>
                        <DialogDescription className="gaming-text-secondary font-mono">
                          &gt;&gt; INITIATE NEURAL PROTOCOL: {workflow.name.toUpperCase()}
                        </DialogDescription>
                      </DialogHeader>
                      
                      <div className="space-y-6">
                        <div>
                          <Label htmlFor="execute-prompt" className="gaming-text-secondary font-mono text-sm">NEURAL INPUT PROMPT</Label>
                          <textarea
                            id="execute-prompt"
                            value={executeForm.prompt}
                            onChange={(e) => setExecuteForm(prev => ({...prev, prompt: e.target.value}))}
                            placeholder=">> ENTER MISSION PARAMETERS AND OBJECTIVES..."
                            rows={4}
                            className="w-full px-4 py-3 mt-2 gaming-card border-gaming-neon-cyan gaming-text-primary font-mono text-sm focus:outline-none focus:border-gaming-neon-cyan focus:shadow-gaming-glow-primary"
                          />
                        </div>
                        
                        <Button
                          onClick={() => handleExecuteWorkflow(workflow.name, executeForm.prompt)}
                          disabled={executing === workflow.name}
                          className="w-full gaming-btn-active py-3 text-lg"
                        >
                          {executing === workflow.name ? (
                            <ArrowPathIcon className="h-5 w-5 animate-spin mr-3" />
                          ) : (
                            <PlayIcon className="h-5 w-5 mr-3" />
                          )}
                          INITIATE NEURAL EXECUTION
                        </Button>
                      </div>
                    </DialogContent>
                  </Dialog>
                  
                  <Button variant="ghost" size="sm" className="gaming-hover-glow p-2">
                    <EyeIcon className="h-4 w-4 gaming-text-neon" />
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Template Dialog - controlled by templateDialogOpen state */}
      <Dialog open={templateDialogOpen} onOpenChange={setTemplateDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto bg-dark-800 border-dark-700">
          <DialogHeader>
            <DialogTitle className="text-white">Create Workflow from Template</DialogTitle>
            <DialogDescription className="text-gray-400">
              Customize your workflow based on the selected template
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="template-workflow-name" className="text-gray-300">Workflow Name</Label>
                <input
                  id="template-workflow-name"
                  type="text"
                  value={newWorkflow.name}
                  onChange={(e) => setNewWorkflow(prev => ({...prev, name: e.target.value}))}
                  placeholder="My Custom Workflow"
                  className="w-full px-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div>
                <Label htmlFor="template-flow-type" className="text-gray-300">Flow Type</Label>
                <Select
                  value={newWorkflow.flow_config.type}
                  onValueChange={(value) => setNewWorkflow(prev => ({
                    ...prev,
                    flow_config: {...prev.flow_config, type: value}
                  }))}
                >
                  <SelectTrigger className="bg-dark-700 border-dark-600 text-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="sequential">Sequential</SelectItem>
                    <SelectItem value="parallel">Parallel</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <div>
              <Label htmlFor="template-workflow-description" className="text-gray-300">Description</Label>
              <textarea
                id="template-workflow-description"
                value={newWorkflow.description}
                onChange={(e) => setNewWorkflow(prev => ({...prev, description: e.target.value}))}
                placeholder="Describe what this workflow does..."
                rows={3}
                className="w-full px-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            
            <div>
              <div className="flex items-center justify-between mb-3">
                <Label className="text-gray-300">Agents</Label>
                <Button variant="outline" size="sm" onClick={addAgentToWorkflow}>
                  <PlusIcon className="h-4 w-4" />
                  Add Agent
                </Button>
              </div>
              
              <div className="space-y-3 max-h-60 overflow-y-auto">
                {(newWorkflow.agents || []).map((agent, index) => (
                  <Card key={index} className="p-3">
                    <div className="grid grid-cols-3 gap-3 items-center">
                      <div>
                        <Label className="text-xs text-gray-400">Agent</Label>
                        <Select
                          value={agent.name}
                          onValueChange={(value) => updateWorkflowAgent(index, 'name', value)}
                        >
                          <SelectTrigger className="h-8 bg-dark-700 border-dark-600 text-white">
                            <SelectValue placeholder="Select agent" />
                          </SelectTrigger>
                          <SelectContent>
                            {agents.map((a) => (
                              <SelectItem key={a.id} value={a.id}>
                                {a.name}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      
                      <div>
                        <Label className="text-xs text-gray-400">Order</Label>
                        <input
                          type="number"
                          value={agent.order}
                          onChange={(e) => updateWorkflowAgent(index, 'order', parseInt(e.target.value))}
                          className="w-full px-2 py-1 bg-dark-700 border border-dark-600 rounded text-white h-8"
                          min={1}
                        />
                      </div>
                      
                      <div className="flex justify-end">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeAgentFromWorkflow(index)}
                          className="text-red-400 hover:text-red-300"
                        >
                          <XCircleIcon className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </div>
            
            <div className="flex justify-end gap-2">
              <Button 
                variant="outline"
                onClick={() => setTemplateDialogOpen(false)}
              >
                Cancel
              </Button>
              <Button 
                onClick={async () => {
                  await handleCreateWorkflow();
                  setTemplateDialogOpen(false);
                }}
                disabled={creating}
              >
                {creating ? (
                  <ArrowPathIcon className="h-4 w-4 animate-spin" />
                ) : (
                  <CheckCircleIcon className="h-4 w-4" />
                )}
                Create Workflow
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Execution Details Dialog */}
      <Dialog open={executionDialogOpen} onOpenChange={setExecutionDialogOpen}>
        <DialogContent className="max-w-2xl bg-dark-800 border-dark-700">
          <DialogHeader>
            <DialogTitle className="text-white">Workflow Execution Details</DialogTitle>
            <DialogDescription className="text-gray-400">
              View detailed information about this workflow execution
            </DialogDescription>
          </DialogHeader>
          
          {selectedExecution && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-gray-400">Workflow</Label>
                  <p className="text-white font-medium">{selectedExecution.workflow_name}</p>
                </div>
                <div>
                  <Label className="text-gray-400">Status</Label>
                  <Badge 
                    variant={
                      selectedExecution.status === 'running' ? 'default' : 
                      selectedExecution.status === 'completed' ? 'outline' : 
                      selectedExecution.status === 'stopped' ? 'secondary' :
                      'destructive'
                    }
                    className={
                      selectedExecution.status === 'running' ? 'bg-blue-500' :
                      selectedExecution.status === 'completed' ? 'text-green-400 border-green-400' :
                      selectedExecution.status === 'stopped' ? 'text-gray-400 border-gray-400' :
                      ''
                    }
                  >
                    {selectedExecution.status}
                  </Badge>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-gray-400">Started</Label>
                  <p className="text-white text-sm">
                    {new Date(selectedExecution.started_at).toLocaleString()}
                  </p>
                </div>
                {selectedExecution.completed_at && (
                  <div>
                    <Label className="text-gray-400">Completed</Label>
                    <p className="text-white text-sm">
                      {new Date(selectedExecution.completed_at).toLocaleString()}
                    </p>
                  </div>
                )}
              </div>
              
              <div>
                <Label className="text-gray-400">Execution ID</Label>
                <p className="text-white font-mono text-sm bg-dark-700 p-2 rounded">
                  {selectedExecution.id}
                </p>
              </div>
              
              {selectedExecution.prompt && (
                <div>
                  <Label className="text-gray-400">Input Prompt</Label>
                  <p className="text-white text-sm bg-dark-700 p-3 rounded">
                    {selectedExecution.prompt}
                  </p>
                </div>
              )}
              
              {selectedExecution.progress && (
                <div>
                  <Label className="text-gray-400">Progress</Label>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">
                        Step {selectedExecution.progress.current_step} of {selectedExecution.progress.total_steps}
                      </span>
                      <span className="text-white">
                        {Math.round((selectedExecution.progress.current_step / selectedExecution.progress.total_steps) * 100)}%
                      </span>
                    </div>
                    <div className="w-full bg-dark-700 rounded-full h-2">
                      <div 
                        className="bg-primary-500 h-2 rounded-full transition-all"
                        style={{ 
                          width: `${(selectedExecution.progress.current_step / selectedExecution.progress.total_steps) * 100}%` 
                        }}
                      />
                    </div>
                    <p className="text-sm text-gray-400">{selectedExecution.progress.message}</p>
                  </div>
                </div>
              )}
              
              {selectedExecution.result && (
                <div>
                  <Label className="text-gray-400">Results</Label>
                  <pre className="text-white text-sm bg-dark-700 p-3 rounded overflow-x-auto">
                    {JSON.stringify(selectedExecution.result, null, 2)}
                  </pre>
                </div>
              )}
              
              <div className="flex justify-end gap-2">
                {selectedExecution.status === 'running' && (
                  <Button
                    variant="destructive"
                    onClick={() => {
                      handleStopExecution(selectedExecution.id);
                      setExecutionDialogOpen(false);
                    }}
                  >
                    <XCircleIcon className="h-4 w-4" />
                    Stop Execution
                  </Button>
                )}
                <Button
                  variant="outline"
                  onClick={() => setExecutionDialogOpen(false)}
                >
                  Close
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}