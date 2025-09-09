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

export default function WorkflowsPage() {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [templates, setTemplates] = useState<WorkflowTemplate[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [executing, setExecuting] = useState<string | null>(null);
  const [templateDialogOpen, setTemplateDialogOpen] = useState(false);

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
    loadData();
  }, []);

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
      
      toast.success('Workflow executed successfully');
      
      if (result.conversation_id) {
        console.log('Workflow conversation:', result.conversation_id);
      }
    } catch (error) {
      console.error('Error executing workflow:', error);
      toast.error('Failed to execute workflow');
    } finally {
      setExecuting(null);
    }
  };

  const handleUseTemplate = (template: WorkflowTemplate) => {
    setNewWorkflow({
      name: template.name,
      description: template.description,
      agents: template.agents,
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
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-white">Multi-Agent Workflows</h1>
          <p className="text-gray-400 mt-1">Orchestrate multiple agents for complex tasks</p>
        </div>
        
        <Dialog>
          <DialogTrigger asChild>
            <Button>
              <PlusIcon className="h-4 w-4" />
              Create Workflow
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto bg-dark-800 border-dark-700">
            <DialogHeader>
              <DialogTitle className="text-white">Create New Workflow</DialogTitle>
              <DialogDescription className="text-gray-400">
                Design a multi-agent workflow to handle complex tasks
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
                    {newWorkflow.agents.map((agent, index) => (
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
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Total Workflows</p>
              <p className="text-2xl font-bold text-white">{workflows.length}</p>
            </div>
            <CpuChipIcon className="h-8 w-8 text-primary-400" />
          </div>
        </Card>
        
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Templates</p>
              <p className="text-2xl font-bold text-purple-400">{templates.length}</p>
            </div>
            <DocumentTextIcon className="h-8 w-8 text-purple-400" />
          </div>
        </Card>
        
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Agents Available</p>
              <p className="text-2xl font-bold text-blue-400">{agents.length}</p>
            </div>
            <SparklesIcon className="h-8 w-8 text-blue-400" />
          </div>
        </Card>
        
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Executions</p>
              <p className="text-2xl font-bold text-green-400">0</p>
            </div>
            <ChartBarIcon className="h-8 w-8 text-green-400" />
          </div>
        </Card>
      </div>

      {/* Workflows List */}
      {workflows.length === 0 && templates.length === 0 ? (
        <Card>
          <div className="text-center py-12">
            <CpuChipIcon className="h-12 w-12 text-gray-600 mx-auto mb-3" />
            <p className="text-gray-400 mb-4">No Workflows or Templates</p>
            <p className="text-sm text-gray-500">Loading workflow templates...</p>
          </div>
        </Card>
      ) : workflows.length === 0 && templates.length > 0 ? (
        <div className="space-y-6">
          <Card>
            <div className="mb-4">
              <h3 className="text-lg font-semibold text-white">Available Templates</h3>
              <p className="text-sm text-gray-400 mt-1">Start with a pre-configured workflow template</p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
          </Card>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {workflows.map((workflow) => (
            <Card key={workflow.id} hover className="flex flex-col">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="font-semibold text-white">{workflow.name}</h3>
                  <p className="text-sm text-gray-400 mt-1">{workflow.description}</p>
                </div>
                <CpuChipIcon className="h-6 w-6 text-primary-400" />
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-gray-300 border-gray-600">
                      {workflow.agent_count} agents
                    </Badge>
                    <Badge variant="outline" className="text-gray-300 border-gray-600">
                      v{workflow.version}
                    </Badge>
                  </div>
                  <span className="text-xs text-gray-500">
                    {new Date(workflow.created_at).toLocaleDateString()}
                  </span>
                </div>
                
                <div className="flex gap-2">
                  <Dialog>
                    <DialogTrigger asChild>
                      <Button variant="secondary" size="sm" className="flex-1">
                        <PlayIcon className="h-4 w-4" />
                        Execute
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="bg-dark-800 border-dark-700">
                      <DialogHeader>
                        <DialogTitle className="text-white">Execute Workflow</DialogTitle>
                        <DialogDescription className="text-gray-400">
                          Provide initial input for {workflow.name}
                        </DialogDescription>
                      </DialogHeader>
                      
                      <div className="space-y-4">
                        <div>
                          <Label htmlFor="execute-prompt" className="text-gray-300">Initial Prompt</Label>
                          <textarea
                            id="execute-prompt"
                            value={executeForm.prompt}
                            onChange={(e) => setExecuteForm(prev => ({...prev, prompt: e.target.value}))}
                            placeholder="Enter your task description..."
                            rows={4}
                            className="w-full px-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                          />
                        </div>
                        
                        <Button
                          onClick={() => handleExecuteWorkflow(workflow.name, executeForm.prompt)}
                          disabled={executing === workflow.name}
                          className="w-full"
                        >
                          {executing === workflow.name ? (
                            <ArrowPathIcon className="h-4 w-4 animate-spin" />
                          ) : (
                            <PlayIcon className="h-4 w-4" />
                          )}
                          Execute Workflow
                        </Button>
                      </div>
                    </DialogContent>
                  </Dialog>
                  
                  <Button variant="ghost" size="sm">
                    <EyeIcon className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </Card>
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
                {newWorkflow.agents.map((agent, index) => (
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
    </div>
  );
}