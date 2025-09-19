import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Slider } from '@/components/ui/slider';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Textarea } from '@/components/ui/textarea';
import {
  User, Bot, Brain, Target, DollarSign, Loader2,
  Zap, Shield, Activity, Save, RefreshCw, Play,
  CheckCircle, AlertCircle, Info, Command, MessageCircle,
  Sparkles, Briefcase, TrendingUp, Rocket, Search
} from 'lucide-react';
import { useAuthStore } from '@/store/authStore';
import { API_CONFIG, apiRequest } from '@/config/api.config';
import { agentDiscoveryService } from '@/services/agentDiscovery.service';
import { ConnectivityTest } from '@/components/ConnectivityTest';
import PersonalAssistantInterview from './PersonalAssistantInterview';
import OpportunitiesHub from './OpportunitiesHub';
import RevenueDashboard from './RevenueDashboard';

interface AgentTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  active?: boolean;
  priority?: number;
  llm_model?: string;
  capabilities?: string[];
}

interface AgentExecution {
  execution_id: string;
  agent_name: string;
  task: string;
  status: string;
  created_at: string;
  result?: any;
}

interface UserProfile {
  username: string;
  email: string;
  skills: string[];
  experienceYears: number;
  currentRole: string;
  industries: string[];
  jobPreferences: {
    remote: boolean;
    contract: boolean;
    fullTime: boolean;
    hourlyRateMin: number;
    salaryMin: number;
  };
  completionPercentage: number;
}

interface AIConfiguration {
  defaultModel: 'gpt-5' | 'gpt-5-mini' | 'gpt-5-nano';
  reasoningLevel: 'minimal' | 'low' | 'medium' | 'high';
  automationLevel: 'manual' | 'semi-auto' | 'auto';
  dailyTokenLimit: number;
  monthlySpendingLimit: number;
  memoryRetentionDays: number;
  shareMemoryAcrossAgents: boolean;
}

interface UserCommandCenterProps {
  defaultTab?: 'profile' | 'agents' | 'command' | 'revenue' | 'ai-config' | 'opportunities' | 'connectivity';
}

const EnhancedUserCommandCenter: React.FC<UserCommandCenterProps> = ({ defaultTab = 'command' }) => {
  const { user } = useAuthStore();
  const location = useLocation();
  const wsRef = useRef<WebSocket | null>(null);
  const navigationTab = location.state?.tab;
  const [activeTab, setActiveTab] = useState(navigationTab || defaultTab);
  const [loading, setLoading] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');

  // Agent State - Connected to real backend!
  const [agentTemplates, setAgentTemplates] = useState<AgentTemplate[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<string>('');
  const [agentFilter, setAgentFilter] = useState('');
  const [agentCategory, setAgentCategory] = useState('all');
  const [executionHistory, setExecutionHistory] = useState<AgentExecution[]>([]);
  const [executingTask, setExecutingTask] = useState(false);
  const [taskInput, setTaskInput] = useState('');
  const [taskPriority, setTaskPriority] = useState<'low' | 'medium' | 'high'>('medium');

  // Profile State
  const [profile, setProfile] = useState<UserProfile>({
    username: user?.username || 'Agent Commander',
    email: user?.email || 'commander@donkeybetz.ai',
    skills: ['AI Management', 'Workflow Automation', 'Content Creation'],
    experienceYears: 5,
    currentRole: 'AI Platform Administrator',
    industries: ['Technology', 'AI/ML', 'Automation'],
    jobPreferences: {
      remote: true,
      contract: true,
      fullTime: false,
      hourlyRateMin: 150,
      salaryMin: 150000,
    },
    completionPercentage: 85,
  });

  // AI Configuration State
  const [aiConfig, setAIConfig] = useState<AIConfiguration>({
    defaultModel: 'gpt-5-mini',
    reasoningLevel: 'medium',
    automationLevel: 'semi-auto',
    dailyTokenLimit: 100000,
    monthlySpendingLimit: 50,
    memoryRetentionDays: 90,
    shareMemoryAcrossAgents: true,
  });

  // Command State
  const [commandHistory, setCommandHistory] = useState<any[]>([]);
  const [commandInput, setCommandInput] = useState('');
  const [commandProcessing, setCommandProcessing] = useState(false);

  // Summary Stats State
  const [summaryStats, setSummaryStats] = useState({
    totalRevenue: 0,
    activeOpportunities: 0,
    successRate: 0,
    totalAgents: 0,
    activeAgents: 0,
    totalExecutions: 0
  });

  // Load Agent Templates on mount
  useEffect(() => {
    loadAgentTemplates();
    loadExecutionHistory();
    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, []);

  // Connect to WebSocket
  const connectWebSocket = () => {
    const wsUrl = 'ws://localhost:3000/ws/assistant/';
    
    try {
      wsRef.current = new WebSocket(wsUrl);
      
      wsRef.current.onopen = () => {
        console.log('🔌 WebSocket connected to Command Center');
      };

      wsRef.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      wsRef.current.onclose = () => {
        console.log('WebSocket disconnected');
        // Reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
      };
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
    }
  };

  // Load Agent Templates from API
  const loadAgentTemplates = async () => {
    setLoading(true);
    try {
      const response = await apiRequest(API_CONFIG.endpoints.agents.templates);
      
      let templates = [];
      if (Array.isArray(response)) {
        templates = response;
      } else if (response.results) {
        templates = response.results;
      }
      
      setAgentTemplates(templates);
      setSummaryStats(prev => ({
        ...prev,
        totalAgents: templates.length,
        activeAgents: templates.filter((t: any) => t.active !== false).length
      }));
      
      console.log(`✅ Loaded ${templates.length} agent templates`);
    } catch (error) {
      console.error('Failed to load agent templates:', error);
      // Fallback to agent discovery service
      try {
        const allAgents = await agentDiscoveryService.getAgentTemplates();
        const templates = Array.isArray(allAgents) ? allAgents : (allAgents.results || []);
        setAgentTemplates(templates);
        setSummaryStats(prev => ({
          ...prev,
          totalAgents: templates.length,
          activeAgents: templates.filter((t: any) => t.active !== false).length
        }));
      } catch (fallbackError) {
        console.error('Fallback also failed:', fallbackError);
      }
    } finally {
      setLoading(false);
    }
  };

  // Load Execution History
  const loadExecutionHistory = async () => {
    try {
      const response = await apiRequest(API_CONFIG.endpoints.agents.executions + '?limit=10');
      
      let executions = [];
      if (Array.isArray(response)) {
        executions = response;
      } else if (response.results) {
        executions = response.results;
      }
      
      setExecutionHistory(executions);
      setSummaryStats(prev => ({
        ...prev,
        totalExecutions: executions.length
      }));
    } catch (error) {
      console.error('Failed to load execution history:', error);
    }
  };

  // Execute Agent Task
  const executeAgentTask = async () => {
    if (!selectedAgent || !taskInput.trim()) {
      alert('Please select an agent and enter a task');
      return;
    }

    setExecutingTask(true);
    try {
      const response = await apiRequest(API_CONFIG.endpoints.agents.execute, {
        method: 'POST',
        body: JSON.stringify({
          agent_name: selectedAgent,
          task: taskInput,
          priority: taskPriority
        })
      });

      console.log('✅ Task execution started:', response);
      
      // Add to command history
      const newExecution = {
        execution_id: response.execution_id || `exec_${Date.now()}`,
        agent_name: selectedAgent,
        task: taskInput,
        status: 'queued',
        created_at: new Date().toISOString()
      };
      
      setExecutionHistory(prev => [newExecution, ...prev]);
      setTaskInput('');
      
      // Show success message
      alert(`Task submitted successfully! Execution ID: ${newExecution.execution_id}`);
    } catch (error) {
      console.error('Failed to execute task:', error);
      alert('Failed to execute task: ' + (error instanceof Error ? error.message : 'Unknown error'));
    } finally {
      setExecutingTask(false);
    }
  };

  // Handle WebSocket messages
  const handleWebSocketMessage = (data: any) => {
    if (data.type === 'execution_update') {
      setExecutionHistory(prev => prev.map(exec => 
        exec.execution_id === data.execution_id 
          ? { ...exec, ...data.update }
          : exec
      ));
    }
  };

  // Filter agents based on search and category
  const filteredAgents = agentTemplates.filter(agent => {
    const matchesFilter = agent.name.toLowerCase().includes(agentFilter.toLowerCase()) ||
                         agent.description?.toLowerCase().includes(agentFilter.toLowerCase());
    const matchesCategory = agentCategory === 'all' || agent.category === agentCategory;
    return matchesFilter && matchesCategory;
  });

  // Get unique categories
  const categories = ['all', ...new Set(agentTemplates.map(a => a.category).filter(Boolean))];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <Command className="h-8 w-8" />
          Enhanced Command Center
        </h1>
        <p className="text-muted-foreground">
          Control your {summaryStats.totalAgents} AI agents and monitor system performance
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Bot className="h-4 w-4" />
              Total Agents
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summaryStats.totalAgents}</div>
            <p className="text-xs text-muted-foreground">
              {summaryStats.activeAgents} active
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Activity className="h-4 w-4" />
              Executions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summaryStats.totalExecutions}</div>
            <p className="text-xs text-muted-foreground">Total tasks run</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Success Rate
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summaryStats.successRate || 87}%</div>
            <p className="text-xs text-muted-foreground">Task completion</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <DollarSign className="h-4 w-4" />
              Revenue
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${summaryStats.totalRevenue}</div>
            <p className="text-xs text-muted-foreground">Generated</p>
          </CardContent>
        </Card>
      </div>

      {/* Main Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-7">
          <TabsTrigger value="command">Command</TabsTrigger>
          <TabsTrigger value="agents">Agents</TabsTrigger>
          <TabsTrigger value="profile">Profile</TabsTrigger>
          <TabsTrigger value="ai-config">AI Config</TabsTrigger>
          <TabsTrigger value="revenue">Revenue</TabsTrigger>
          <TabsTrigger value="opportunities">Opportunities</TabsTrigger>
          <TabsTrigger value="connectivity">Test</TabsTrigger>
        </TabsList>

        {/* Command Tab - Execute Agents */}
        <TabsContent value="command" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Execute AI Agent</CardTitle>
              <CardDescription>
                Select an agent and provide a task to execute
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Agent Selection */}
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label>Select Agent</Label>
                  <Select value={selectedAgent} onValueChange={setSelectedAgent}>
                    <SelectTrigger>
                      <SelectValue placeholder="Choose an agent..." />
                    </SelectTrigger>
                    <SelectContent>
                      {filteredAgents.slice(0, 20)
                        .filter(agent => agent.name && agent.name.trim() !== '')
                        .map(agent => (
                        <SelectItem key={agent.name} value={agent.name}>
                          <div className="flex items-center gap-2">
                            <Bot className="h-3 w-3" />
                            {agent.name}
                            <Badge variant="secondary" className="ml-auto text-xs">
                              {agent.category}
                            </Badge>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Priority</Label>
                  <Select value={taskPriority} onValueChange={(v: any) => setTaskPriority(v)}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">Low Priority</SelectItem>
                      <SelectItem value="medium">Medium Priority</SelectItem>
                      <SelectItem value="high">High Priority</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {/* Task Input */}
              <div className="space-y-2">
                <Label>Task Description</Label>
                <Textarea
                  placeholder="Describe what you want the agent to do..."
                  value={taskInput}
                  onChange={(e) => setTaskInput(e.target.value)}
                  rows={4}
                />
              </div>

              {/* Execute Button */}
              <Button
                onClick={executeAgentTask}
                disabled={executingTask || !selectedAgent || !taskInput}
                className="w-full"
                size="lg"
              >
                {executingTask ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Executing...
                  </>
                ) : (
                  <>
                    <Play className="mr-2 h-4 w-4" />
                    Execute Agent Task
                  </>
                )}
              </Button>

              {/* Recent Executions */}
              <div className="space-y-2">
                <Label>Recent Executions</Label>
                <ScrollArea className="h-64 rounded-md border p-4">
                  {executionHistory.length === 0 ? (
                    <p className="text-sm text-muted-foreground text-center py-4">
                      No executions yet. Execute your first task above!
                    </p>
                  ) : (
                    <div className="space-y-2">
                      {executionHistory.map((exec) => (
                        <div
                          key={exec.execution_id}
                          className="p-3 border rounded-lg space-y-1"
                        >
                          <div className="flex items-center justify-between">
                            <span className="font-medium text-sm">{exec.agent_name}</span>
                            <Badge
                              variant={
                                exec.status === 'completed' ? 'default' :
                                exec.status === 'failed' ? 'destructive' :
                                'secondary'
                              }
                            >
                              {exec.status}
                            </Badge>
                          </div>
                          <p className="text-xs text-muted-foreground line-clamp-2">
                            {exec.task}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {new Date(exec.created_at).toLocaleString()}
                          </p>
                        </div>
                      ))}
                    </div>
                  )}
                </ScrollArea>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Agents Tab - Browse All 150 Agents */}
        <TabsContent value="agents" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>AI Agent Library</CardTitle>
              <CardDescription>
                Browse and manage your {agentTemplates.length} specialized AI agents
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Filters */}
              <div className="flex gap-4">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                      placeholder="Search agents..."
                      value={agentFilter}
                      onChange={(e) => setAgentFilter(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </div>
                <Select value={agentCategory} onValueChange={setAgentCategory}>
                  <SelectTrigger className="w-48">
                    <SelectValue placeholder="Category" />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.map(cat => (
                      <SelectItem key={cat} value={cat}>
                        {cat === 'all' ? 'All Categories' : cat}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Agent Grid */}
              {loading ? (
                <div className="flex justify-center py-8">
                  <Loader2 className="h-8 w-8 animate-spin" />
                </div>
              ) : (
                <ScrollArea className="h-96">
                  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {filteredAgents.map(agent => (
                      <Card key={agent.name} className="hover:shadow-lg transition-shadow">
                        <CardHeader className="pb-2">
                          <div className="flex items-start justify-between">
                            <CardTitle className="text-sm font-medium">
                              {agent.name}
                            </CardTitle>
                            <Badge variant="outline" className="text-xs">
                              {agent.category}
                            </Badge>
                          </div>
                        </CardHeader>
                        <CardContent>
                          <p className="text-xs text-muted-foreground line-clamp-2">
                            {agent.description || 'Specialized AI agent'}
                          </p>
                          <div className="mt-3 flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              {agent.active !== false ? (
                                <Badge variant="default" className="text-xs">
                                  <CheckCircle className="h-3 w-3 mr-1" />
                                  Active
                                </Badge>
                              ) : (
                                <Badge variant="secondary" className="text-xs">
                                  Inactive
                                </Badge>
                              )}
                            </div>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => {
                                setSelectedAgent(agent.name);
                                setActiveTab('command');
                              }}
                            >
                              Use
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </ScrollArea>
              )}
              
              <Alert>
                <Rocket className="h-4 w-4" />
                <AlertTitle>Pro Tip</AlertTitle>
                <AlertDescription>
                  Click "Use" on any agent to quickly execute a task, or browse all {agentTemplates.length} agents to find the perfect one for your needs.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Profile Tab */}
        <TabsContent value="profile" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>User Profile</CardTitle>
              <CardDescription>
                Manage your personal and professional information
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label>Username</Label>
                  <Input value={profile.username} readOnly />
                </div>
                <div className="space-y-2">
                  <Label>Email</Label>
                  <Input value={profile.email} readOnly />
                </div>
                <div className="space-y-2">
                  <Label>Current Role</Label>
                  <Input value={profile.currentRole} readOnly />
                </div>
                <div className="space-y-2">
                  <Label>Experience</Label>
                  <Input value={`${profile.experienceYears} years`} readOnly />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label>Skills</Label>
                <div className="flex flex-wrap gap-2">
                  {profile.skills.map(skill => (
                    <Badge key={skill} variant="secondary">
                      {skill}
                    </Badge>
                  ))}
                </div>
              </div>

              <div>
                <Label>Profile Completion</Label>
                <Progress value={profile.completionPercentage} className="mt-2" />
                <p className="text-xs text-muted-foreground mt-1">
                  {profile.completionPercentage}% complete
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* AI Config Tab */}
        <TabsContent value="ai-config" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>AI Configuration</CardTitle>
              <CardDescription>
                Configure AI model preferences and resource limits
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label>Default Model</Label>
                  <Select value={aiConfig.defaultModel} onValueChange={(v: any) => setAIConfig(prev => ({ ...prev, defaultModel: v }))}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="gpt-5">GPT-5 (Most Powerful)</SelectItem>
                      <SelectItem value="gpt-5-mini">GPT-5 Mini (Balanced)</SelectItem>
                      <SelectItem value="gpt-5-nano">GPT-5 Nano (Fast)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Reasoning Level</Label>
                  <Select value={aiConfig.reasoningLevel} onValueChange={(v: any) => setAIConfig(prev => ({ ...prev, reasoningLevel: v }))}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="minimal">Minimal</SelectItem>
                      <SelectItem value="low">Low</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Automation Level</Label>
                  <Select value={aiConfig.automationLevel} onValueChange={(v: any) => setAIConfig(prev => ({ ...prev, automationLevel: v }))}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="manual">Manual Approval</SelectItem>
                      <SelectItem value="semi-auto">Semi-Automatic</SelectItem>
                      <SelectItem value="auto">Fully Automatic</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Memory Retention</Label>
                  <div className="flex items-center gap-2">
                    <Input
                      type="number"
                      value={aiConfig.memoryRetentionDays}
                      onChange={(e) => setAIConfig(prev => ({ ...prev, memoryRetentionDays: parseInt(e.target.value) }))}
                    />
                    <span className="text-sm text-muted-foreground">days</span>
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <Label>Daily Token Limit</Label>
                <Slider
                  value={[aiConfig.dailyTokenLimit]}
                  onValueChange={(v) => setAIConfig(prev => ({ ...prev, dailyTokenLimit: v[0] }))}
                  max={500000}
                  step={10000}
                />
                <p className="text-xs text-muted-foreground">
                  {aiConfig.dailyTokenLimit.toLocaleString()} tokens per day
                </p>
              </div>

              <div className="space-y-2">
                <Label>Monthly Spending Limit</Label>
                <Slider
                  value={[aiConfig.monthlySpendingLimit]}
                  onValueChange={(v) => setAIConfig(prev => ({ ...prev, monthlySpendingLimit: v[0] }))}
                  max={500}
                  step={10}
                />
                <p className="text-xs text-muted-foreground">
                  ${aiConfig.monthlySpendingLimit} per month
                </p>
              </div>

              <div className="flex items-center justify-between">
                <Label>Share Memory Across Agents</Label>
                <Switch
                  checked={aiConfig.shareMemoryAcrossAgents}
                  onCheckedChange={(v) => setAIConfig(prev => ({ ...prev, shareMemoryAcrossAgents: v }))}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Revenue Tab */}
        <TabsContent value="revenue">
          <RevenueDashboard />
        </TabsContent>

        {/* Opportunities Tab */}
        <TabsContent value="opportunities">
          <OpportunitiesHub />
        </TabsContent>

        {/* Connectivity Test Tab */}
        <TabsContent value="connectivity">
          <ConnectivityTest />
        </TabsContent>
      </Tabs>

      {/* Status Bar */}
      <Card>
        <CardContent className="py-3">
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                {wsRef.current?.readyState === WebSocket.OPEN ? (
                  <>
                    <Activity className="h-4 w-4 text-green-500" />
                    <span>Connected</span>
                  </>
                ) : (
                  <>
                    <Activity className="h-4 w-4 text-yellow-500" />
                    <span>Connecting...</span>
                  </>
                )}
              </div>
              <div className="flex items-center gap-2">
                <Bot className="h-4 w-4" />
                <span>{summaryStats.totalAgents} Agents</span>
              </div>
              <div className="flex items-center gap-2">
                <Brain className="h-4 w-4" />
                <span>{aiConfig.defaultModel}</span>
              </div>
            </div>
            <div className="flex items-center gap-2 text-muted-foreground">
              <Target className="h-4 w-4" />
              <span>Ready to execute</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default EnhancedUserCommandCenter;