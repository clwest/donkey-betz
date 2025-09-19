import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import {
  Bot, Brain, Activity, DollarSign, Loader2,
  Zap, Command, Play, Search, Rocket, CheckCircle
} from 'lucide-react';

interface AgentTemplate {
  id?: string;
  name: string;
  description?: string;
  category?: string;
  active?: boolean;
}

interface AgentExecution {
  execution_id: string;
  agent_name: string;
  task: string;
  status: string;
  created_at: string;
}

const SimpleCommandCenter: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [agents, setAgents] = useState<AgentTemplate[]>([]);
  const [selectedAgent, setSelectedAgent] = useState('');
  const [taskInput, setTaskInput] = useState('');
  const [taskPriority, setTaskPriority] = useState<'low' | 'medium' | 'high'>('medium');
  const [executions, setExecutions] = useState<AgentExecution[]>([]);
  const [executing, setExecuting] = useState(false);
  const [activeTab, setActiveTab] = useState('command');
  const [searchFilter, setSearchFilter] = useState('');
  const [testStatus, setTestStatus] = useState<'idle' | 'testing' | 'success' | 'error'>('idle');

  // Load agents on mount
  useEffect(() => {
    loadAgents();
    loadExecutions();
  }, []);

  const loadAgents = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('authToken') || '0fb2390dedd5cc47ec7e6a320e1477b31b7c0a97';
      const response = await fetch('/api/v1/agents/templates/?page_size=200', {
        headers: {
          'Authorization': `Token ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        const agentList = Array.isArray(data) ? data : (data.results || []);
        setAgents(agentList);
        console.log(`Loaded ${agentList.length} agents`);
      } else {
        console.error('Failed to load agents:', response.status);
      }
    } catch (error) {
      console.error('Error loading agents:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadExecutions = async () => {
    try {
      const token = localStorage.getItem('authToken') || '0fb2390dedd5cc47ec7e6a320e1477b31b7c0a97';
      const response = await fetch('/api/v1/agents/executions/?limit=10', {
        headers: {
          'Authorization': `Token ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        const execList = Array.isArray(data) ? data : (data.results || []);
        setExecutions(execList);
      }
    } catch (error) {
      console.error('Error loading executions:', error);
    }
  };

  const executeAgent = async () => {
    if (!selectedAgent || !taskInput.trim()) {
      alert('Please select an agent and enter a task');
      return;
    }

    setExecuting(true);
    try {
      const token = localStorage.getItem('authToken') || '0fb2390dedd5cc47ec7e6a320e1477b31b7c0a97';
      const response = await fetch('/api/v1/agents/execute/', {
        method: 'POST',
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          agent_name: selectedAgent,
          task: taskInput,
          priority: taskPriority
        })
      });

      if (response.ok) {
        const data = await response.json();
        alert(`Task submitted! ID: ${data.execution_id || 'pending'}`);
        setTaskInput('');
        loadExecutions(); // Reload executions
      } else {
        alert('Failed to execute task');
      }
    } catch (error) {
      console.error('Execution error:', error);
      alert('Error executing task');
    } finally {
      setExecuting(false);
    }
  };

  const testConnectivity = async () => {
    setTestStatus('testing');
    try {
      const token = localStorage.getItem('authToken') || '0fb2390dedd5cc47ec7e6a320e1477b31b7c0a97';
      const response = await fetch('/api/v1/agents/templates/?page_size=200', {
        headers: {
          'Authorization': `Token ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        const count = Array.isArray(data) ? data.length : (data.results?.length || 0);
        setTestStatus('success');
        alert(`✅ API Connected! Found ${count} agents`);
      } else {
        setTestStatus('error');
        alert(`❌ API Error: Status ${response.status}`);
      }
    } catch (error) {
      setTestStatus('error');
      alert('❌ Connection failed');
    }
  };

  const filteredAgents = agents.filter(agent => 
    agent.name.toLowerCase().includes(searchFilter.toLowerCase()) ||
    agent.description?.toLowerCase().includes(searchFilter.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <Command className="h-8 w-8" />
          Command Center (Simplified)
        </h1>
        <p className="text-muted-foreground">
          Control {agents.length} AI agents
        </p>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Total Agents</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{agents.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Executions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{executions.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Status</CardTitle>
          </CardHeader>
          <CardContent>
            <Badge variant="default">Active</Badge>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Quick Test</CardTitle>
          </CardHeader>
          <CardContent>
            <Button size="sm" onClick={testConnectivity} disabled={testStatus === 'testing'}>
              {testStatus === 'testing' ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Test API'}
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="command">Execute</TabsTrigger>
          <TabsTrigger value="agents">Browse Agents</TabsTrigger>
          <TabsTrigger value="history">History</TabsTrigger>
        </TabsList>

        {/* Execute Tab */}
        <TabsContent value="command" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Execute Agent Task</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {loading ? (
                <div className="flex justify-center py-4">
                  <Loader2 className="h-8 w-8 animate-spin" />
                </div>
              ) : (
                <>
                  <div className="grid gap-4 md:grid-cols-2">
                    <div>
                      <Label>Select Agent</Label>
                      <Select value={selectedAgent} onValueChange={setSelectedAgent}>
                        <SelectTrigger>
                          <SelectValue placeholder="Choose agent..." />
                        </SelectTrigger>
                        <SelectContent>
                          {agents.slice(0, 50)
                            .filter(agent => agent.name && agent.name.trim() !== '')
                            .map(agent => (
                            <SelectItem key={agent.name} value={agent.name}>
                              {agent.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label>Priority</Label>
                      <Select value={taskPriority} onValueChange={(v) => setTaskPriority(v as 'low' | 'medium' | 'high')}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="low">Low</SelectItem>
                          <SelectItem value="medium">Medium</SelectItem>
                          <SelectItem value="high">High</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div>
                    <Label>Task Description</Label>
                    <textarea
                      className="w-full p-2 border rounded-md"
                      rows={4}
                      placeholder="Describe the task..."
                      value={taskInput}
                      onChange={(e) => setTaskInput(e.target.value)}
                    />
                  </div>

                  <Button 
                    onClick={executeAgent} 
                    disabled={executing || !selectedAgent || !taskInput}
                    className="w-full"
                  >
                    {executing ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Executing...
                      </>
                    ) : (
                      <>
                        <Play className="mr-2 h-4 w-4" />
                        Execute Task
                      </>
                    )}
                  </Button>
                </>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Agents Tab */}
        <TabsContent value="agents" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Agent Library ({agents.length} agents)</CardTitle>
              <div className="mt-2">
                <Input
                  placeholder="Search agents..."
                  value={searchFilter}
                  onChange={(e) => setSearchFilter(e.target.value)}
                />
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid gap-2 md:grid-cols-2 lg:grid-cols-3 max-h-96 overflow-y-auto">
                {filteredAgents.map(agent => (
                  <Card key={agent.name} className="p-3">
                    <div className="font-medium">{agent.name}</div>
                    <div className="text-sm text-muted-foreground">
                      {agent.category || 'General'}
                    </div>
                    <Button 
                      size="sm" 
                      variant="outline" 
                      className="mt-2"
                      onClick={() => {
                        setSelectedAgent(agent.name);
                        setActiveTab('command');
                      }}
                    >
                      Use
                    </Button>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* History Tab */}
        <TabsContent value="history" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Execution History</CardTitle>
            </CardHeader>
            <CardContent>
              {executions.length === 0 ? (
                <p className="text-muted-foreground">No executions yet</p>
              ) : (
                <div className="space-y-2">
                  {executions.map(exec => (
                    <div key={exec.execution_id} className="p-3 border rounded">
                      <div className="flex justify-between items-start">
                        <div>
                          <div className="font-medium">{exec.agent_name}</div>
                          <div className="text-sm text-muted-foreground">{exec.task}</div>
                        </div>
                        <Badge>{exec.status}</Badge>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Alert */}
      <Alert>
        <Rocket className="h-4 w-4" />
        <AlertTitle>Quick Tip</AlertTitle>
        <AlertDescription>
          {agents.length > 0 
            ? `${agents.length} agents loaded and ready! Select one and enter a task to execute.`
            : 'Loading agents... If this persists, check your connection.'}
        </AlertDescription>
      </Alert>
    </div>
  );
};

export default SimpleCommandCenter;