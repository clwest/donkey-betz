import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
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
  ChartBarIcon
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

export function WorkflowsPage() {
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

      // Extract and log each data piece
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
      
      // Navigate to conversation or show results
      if (result.conversation_id) {
        // Could navigate to chat page with conversation_id
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
        type: template.flow_config.type as 'sequential' | 'parallel',
        error_handling: (template.flow_config.error_handling || 'stop') as 'stop' | 'continue',
        save_intermediate: template.flow_config.save_intermediate ?? true
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
        <ArrowPathIcon className="h-8 w-8 animate-spin text-primary-500" />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gradient">Multi-Agent Workflows</h1>
          <p className="text-gray-400 mt-2">Orchestrate multiple agents for complex tasks</p>
        </div>
        
        <Dialog>
          <DialogTrigger asChild>
            <Button className="bg-gradient-primary">
              <PlusIcon className="h-4 w-4 mr-2" />
              Create Workflow
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Create New Workflow</DialogTitle>
              <DialogDescription>
                Design a multi-agent workflow to handle complex tasks
              </DialogDescription>
            </DialogHeader>
            
            <Tabs defaultValue="design" className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="design">Design</TabsTrigger>
                <TabsTrigger value="templates">Templates</TabsTrigger>
              </TabsList>
              
              <TabsContent value="design" className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="workflow-name">Workflow Name</Label>
                    <Input
                      id="workflow-name"
                      value={newWorkflow.name}
                      onChange={(e) => setNewWorkflow(prev => ({...prev, name: e.target.value}))}
                      placeholder="My Custom Workflow"
                    />
                  </div>
                  <div>
                    <Label htmlFor="flow-type">Flow Type</Label>
                    <Select
                      value={newWorkflow.flow_config.type}
                      onValueChange={(value) => setNewWorkflow(prev => ({
                        ...prev,
                        flow_config: {...prev.flow_config, type: value}
                      }))}
                    >
                      <SelectTrigger>
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
                  <Label htmlFor="workflow-description">Description</Label>
                  <Textarea
                    id="workflow-description"
                    value={newWorkflow.description}
                    onChange={(e) => setNewWorkflow(prev => ({...prev, description: e.target.value}))}
                    placeholder="Describe what this workflow does..."
                    rows={3}
                  />
                </div>
                
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <Label>Agents</Label>
                    <Button variant="outline" size="sm" onClick={addAgentToWorkflow}>
                      <PlusIcon className="h-4 w-4 mr-1" />
                      Add Agent
                    </Button>
                  </div>
                  
                  <div className="space-y-3 max-h-60 overflow-y-auto">
                    {newWorkflow.agents.map((agent, index) => (
                      <Card key={index} className="p-3">
                        <div className="grid grid-cols-3 gap-3 items-center">
                          <div>
                            <Label className="text-xs">Agent</Label>
                            <Select
                              value={agent.name}
                              onValueChange={(value) => updateWorkflowAgent(index, 'name', value)}
                            >
                              <SelectTrigger className="h-8">
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
                            <Label className="text-xs">Order</Label>
                            <Input
                              type="number"
                              value={agent.order}
                              onChange={(e) => updateWorkflowAgent(index, 'order', parseInt(e.target.value))}
                              className="h-8"
                              min={1}
                            />
                          </div>
                          
                          <div className="flex justify-end">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => removeAgentFromWorkflow(index)}
                              className="text-red-500 hover:text-red-400"
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
                    className="bg-gradient-primary"
                  >
                    {creating ? (
                      <ArrowPathIcon className="h-4 w-4 animate-spin mr-2" />
                    ) : (
                      <CheckCircleIcon className="h-4 w-4 mr-2" />
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
                            <Badge variant="outline">{template.agents.length} agents</Badge>
                            <Badge variant="outline">{template.flow_config.type}</Badge>
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

      {/* Workflows List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {workflows.map((workflow) => (
          <Card key={workflow.id} className="glass-dark border-white/10">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-white">{workflow.name}</CardTitle>
                  <CardDescription>{workflow.description}</CardDescription>
                </div>
                <CpuChipIcon className="h-6 w-6 text-primary-400" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <Badge variant="outline">{workflow.agent_count} agents</Badge>
                  <Badge variant="outline">v{workflow.version}</Badge>
                </div>
                <span className="text-xs text-gray-500">
                  {new Date(workflow.created_at).toLocaleDateString()}
                </span>
              </div>
              
              <div className="flex gap-2">
                <Dialog>
                  <DialogTrigger asChild>
                    <Button variant="outline" size="sm" className="flex-1">
                      <PlayIcon className="h-4 w-4 mr-1" />
                      Execute
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Execute Workflow</DialogTitle>
                      <DialogDescription>
                        Provide initial input for {workflow.name}
                      </DialogDescription>
                    </DialogHeader>
                    
                    <div className="space-y-4">
                      <div>
                        <Label htmlFor="execute-prompt">Initial Prompt</Label>
                        <Textarea
                          id="execute-prompt"
                          value={executeForm.prompt}
                          onChange={(e) => setExecuteForm(prev => ({...prev, prompt: e.target.value}))}
                          placeholder="Enter your task description..."
                          rows={4}
                        />
                      </div>
                      
                      <Button
                        onClick={() => handleExecuteWorkflow(workflow.name, executeForm.prompt)}
                        disabled={executing === workflow.name}
                        className="w-full bg-gradient-primary"
                      >
                        {executing === workflow.name ? (
                          <ArrowPathIcon className="h-4 w-4 animate-spin mr-2" />
                        ) : (
                          <PlayIcon className="h-4 w-4 mr-2" />
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
            </CardContent>
          </Card>
        ))}
      </div>

      {workflows.length === 0 && templates.length > 0 && (
        <div className="space-y-6">
          {/* Show templates when no workflows exist */}
          <Card className="glass-dark border-white/10">
            <CardHeader>
              <CardTitle className="text-white">Available Templates</CardTitle>
              <CardDescription>Start with a pre-configured workflow template</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {templates.map((template, index) => (
                  <Card key={index} className="p-4 border-white/10">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="font-semibold text-white">{template.name}</h3>
                        <p className="text-sm text-gray-400 mt-1">{template.description}</p>
                        <div className="flex items-center gap-2 mt-2">
                          <Badge variant="outline">{template.agents.length} agents</Badge>
                          <Badge variant="outline">{template.flow_config.type}</Badge>
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
            </CardContent>
          </Card>
        </div>
      )}

      {/* Template Dialog - controlled by templateDialogOpen state */}
      <Dialog open={templateDialogOpen} onOpenChange={setTemplateDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Create Workflow from Template</DialogTitle>
            <DialogDescription>
              Customize your workflow based on the selected template
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="template-workflow-name">Workflow Name</Label>
                <Input
                  id="template-workflow-name"
                  value={newWorkflow.name}
                  onChange={(e) => setNewWorkflow(prev => ({...prev, name: e.target.value}))}
                  placeholder="My Custom Workflow"
                />
              </div>
              <div>
                <Label htmlFor="template-flow-type">Flow Type</Label>
                <Select
                  value={newWorkflow.flow_config.type}
                  onValueChange={(value) => setNewWorkflow(prev => ({
                    ...prev,
                    flow_config: {...prev.flow_config, type: value}
                  }))}
                >
                  <SelectTrigger>
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
              <Label htmlFor="template-workflow-description">Description</Label>
              <Textarea
                id="template-workflow-description"
                value={newWorkflow.description}
                onChange={(e) => setNewWorkflow(prev => ({...prev, description: e.target.value}))}
                placeholder="Describe what this workflow does..."
                rows={3}
              />
            </div>
            
            <div>
              <div className="flex items-center justify-between mb-3">
                <Label>Agents</Label>
                <Button variant="outline" size="sm" onClick={addAgentToWorkflow}>
                  <PlusIcon className="h-4 w-4 mr-1" />
                  Add Agent
                </Button>
              </div>
              
              <div className="space-y-3 max-h-60 overflow-y-auto">
                {newWorkflow.agents.map((agent, index) => (
                  <Card key={index} className="p-3">
                    <div className="grid grid-cols-3 gap-3 items-center">
                      <div>
                        <Label className="text-xs">Agent</Label>
                        <Select
                          value={agent.name}
                          onValueChange={(value) => updateWorkflowAgent(index, 'name', value)}
                        >
                          <SelectTrigger className="h-8">
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
                        <Label className="text-xs">Order</Label>
                        <Input
                          type="number"
                          value={agent.order}
                          onChange={(e) => updateWorkflowAgent(index, 'order', parseInt(e.target.value))}
                          className="h-8"
                          min={1}
                        />
                      </div>
                      
                      <div className="flex justify-end">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeAgentFromWorkflow(index)}
                          className="text-red-500 hover:text-red-400"
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
                className="bg-gradient-primary"
              >
                {creating ? (
                  <ArrowPathIcon className="h-4 w-4 animate-spin mr-2" />
                ) : (
                  <CheckCircleIcon className="h-4 w-4 mr-2" />
                )}
                Create Workflow
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {workflows.length === 0 && templates.length === 0 && (
        <Card className="glass-dark border-white/10 text-center py-12">
          <CardContent>
            <CpuChipIcon className="h-12 w-12 text-gray-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-white mb-2">No Workflows or Templates</h3>
            <p className="text-gray-400">Loading workflow templates...</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}