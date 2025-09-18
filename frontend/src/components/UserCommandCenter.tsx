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
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Slider } from '@/components/ui/slider';
import {
  User, Bot, Brain, Target, DollarSign,
  Zap, Shield, Activity, Save, RefreshCw,
  CheckCircle, AlertCircle, Info, Command, MessageCircle,
  Sparkles, Briefcase, TrendingUp
} from 'lucide-react';
import { useAuthStore } from '@/store/authStore';
import { apiClient } from '@/services/api.config';
import PersonalAssistantInterview from './PersonalAssistantInterview';
import OpportunitiesHub from './OpportunitiesHub';
import RevenueDashboard from './RevenueDashboard';

interface UserProfile {
  // Basic Info
  username: string;
  email: string;

  // Professional Profile
  skills: string[];
  experienceYears: number;
  currentRole: string;
  industries: string[];

  // Work Preferences
  jobPreferences: {
    remote: boolean;
    contract: boolean;
    fullTime: boolean;
    hourlyRateMin: number;
    salaryMin: number;
  };

  // Documents
  resumeId?: string;
  portfolioUrl?: string;
  linkedinUrl?: string;
  githubUrl?: string;

  // Profile Completion
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

interface AgentAssignment {
  agentName: string;
  agentType: string;
  customModel?: string;
  canExecuteActions: boolean;
  dailyActionLimit: number;
  tasksCompleted: number;
  successRate: number;
  lastActive: string;
}

interface CommandResult {
  success: boolean;
  message: string;
  data?: any;
}

interface UserCommandCenterProps {
  defaultTab?: 'profile' | 'opportunities' | 'revenue' | 'ai-config' | 'agents' | 'command';
}

const UserCommandCenter: React.FC<UserCommandCenterProps> = ({ defaultTab = 'profile' }) => {
  const { user } = useAuthStore();
  const location = useLocation();
  const wsRef = useRef<WebSocket | null>(null);
  const navigationTab = location.state?.tab;
  const [activeTab, setActiveTab] = useState(navigationTab || defaultTab);
  const [loading, setLoading] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');
  const [showInterview, setShowInterview] = useState(false);
  const [interviewCompleted, setInterviewCompleted] = useState(false);

  // Profile State
  const [profile, setProfile] = useState<UserProfile>({
    username: user?.username || '',
    email: user?.email || '',
    skills: [],
    experienceYears: 0,
    currentRole: '',
    industries: [],
    jobPreferences: {
      remote: true,
      contract: true,
      fullTime: false,
      hourlyRateMin: 100,
      salaryMin: 120000,
    },
    completionPercentage: 0,
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

  // Agent Assignments State
  const [agents, setAgents] = useState<AgentAssignment[]>([]);
  const [selectedAgents, setSelectedAgents] = useState<string[]>([]);

  // Command State
  const [commandHistory, setCommandHistory] = useState<any[]>([]);
  const [commandInput, setCommandInput] = useState('');
  const [commandProcessing, setCommandProcessing] = useState(false);

  // Skills input
  const [newSkill, setNewSkill] = useState('');

  // Summary Stats State
  const [summaryStats, setSummaryStats] = useState({
    totalRevenue: 0,
    activeOpportunities: 0,
    successRate: 0,
    activeAgents: 0
  });

  // Initialize WebSocket connection
  useEffect(() => {
    if (!wsRef.current) {
      // Use development backend WebSocket URL
      const isDev = import.meta.env.MODE !== 'production';
      const wsUrl = isDev ? 'ws://localhost:8000/ws/command-center/' :
        (window.location.protocol === 'https:' ? 'wss:' : 'ws:') + '//' + window.location.host + '/ws/command-center/';
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        console.log('Command Center WebSocket connected');
        loadUserData();
      };

      wsRef.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    }

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, []);

  // Load user data
  const loadUserData = async () => {
    setLoading(true);
    try {
      // Load stats from public API (no auth required)
      const statsResponse = await fetch('/api/public/system-stats/');
      let statsData = null;
      if (statsResponse.ok) {
        statsData = await statsResponse.json();
      }

      // Try to load authenticated user data
      try {
        const [profileRes, aiConfigRes, agentsRes, revenueRes] = await Promise.all([
          apiClient.get('/api/profile/extended/').catch(() => ({ data: null })),
          apiClient.get('/api/ai/configuration/').catch(() => ({ data: null })),
          apiClient.get('/api/agents/assigned/').catch(() => ({ data: [] })),
          apiClient.get('/api/v1/ecosystem/revenue/').catch(() => ({ data: [] })),
        ]);

        if (profileRes.data) {
          setProfile({
            ...profileRes.data,
            skills: profileRes.data.skills || [],
            industries: profileRes.data.industries || [],
            jobPreferences: profileRes.data.jobPreferences || {
              remote: true,
              contract: true,
              fullTime: false,
              hourlyRateMin: 100,
              salaryMin: 120000,
            }
          });
        }
        if (aiConfigRes.data) {
          setAIConfig({
            defaultModel: aiConfigRes.data.defaultModel || 'gpt-5-mini',
            reasoningLevel: aiConfigRes.data.reasoningLevel || 'medium',
            automationLevel: aiConfigRes.data.automationLevel || 'semi-auto',
            dailyTokenLimit: aiConfigRes.data.dailyTokenLimit || 100000,
            monthlySpendingLimit: aiConfigRes.data.monthlySpendingLimit || 50,
            memoryRetentionDays: aiConfigRes.data.memoryRetentionDays || 90,
            shareMemoryAcrossAgents: aiConfigRes.data.shareMemoryAcrossAgents ?? true,
          });
        }
        if (agentsRes.data && Array.isArray(agentsRes.data)) {
          setAgents(agentsRes.data);
          setSelectedAgents(agentsRes.data.map((a: AgentAssignment) => a.agentName));
        }

        // Calculate actual revenue and success rate
        let totalRevenue = 0;
        let successRate = 0;
        if (revenueRes.data && Array.isArray(revenueRes.data)) {
          totalRevenue = revenueRes.data
            .filter((r: any) => r.status === 'completed')
            .reduce((sum: number, r: any) => sum + parseFloat(r.amount || 0), 0);

          // Calculate success rate based on completed revenue entries
          const completedCount = revenueRes.data.filter((r: any) => r.status === 'completed').length;
          const totalOpportunities = statsData?.system_overview?.active_opportunities || 0;
          successRate = totalOpportunities > 0 ? Math.round((completedCount / (totalOpportunities + completedCount)) * 100) : 0;
        }

        // Update summary stats with real data
        if (statsData) {
          setSummaryStats({
            totalRevenue,
            activeOpportunities: statsData.system_overview.active_opportunities || 0,
            successRate,
            activeAgents: statsData.system_overview.total_agents || 0
          });
        }
      } catch (authError) {
        console.log('User not authenticated, using public data only');

        // Update summary stats from public API only (no revenue data)
        if (statsData) {
          setSummaryStats({
            totalRevenue: 0, // No access to user revenue data
            activeOpportunities: statsData.system_overview.active_opportunities || 0,
            successRate: 0, // No access to user success data
            activeAgents: statsData.system_overview.total_agents || 0
          });
        }
      }
    } catch (error) {
      console.error('Failed to load data:', error);
      // Set fallback data with zeros since we can't access real data
      setSummaryStats({
        totalRevenue: 0,
        activeOpportunities: 0,
        successRate: 0,
        activeAgents: 0
      });
    } finally {
      setLoading(false);
    }
  };

  // Handle WebSocket messages
  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'PROFILE_UPDATED':
        setProfile(prev => ({ ...prev, ...data.payload }));
        break;
      case 'AI_CONFIG_UPDATED':
        setAIConfig(prev => ({ ...prev, ...data.payload }));
        break;
      case 'AGENT_STATUS':
        updateAgentStatus(data.payload);
        break;
      case 'COMMAND_RESULT':
        handleCommandResult(data.payload);
        break;
      case 'STATS_UPDATE':
        setSummaryStats(prev => ({ ...prev, ...data.payload }));
        break;
      case 'REVENUE_UPDATE':
        setSummaryStats(prev => ({ ...prev, totalRevenue: data.payload.total }));
        break;
      case 'OPPORTUNITIES_UPDATE':
        setSummaryStats(prev => ({ ...prev, activeOpportunities: data.payload.count }));
        break;
    }
  };

  // Send command through WebSocket
  const sendCommand = (type: string, payload: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type,
        payload,
        timestamp: Date.now(),
        userId: user?.id,
      }));
    }
  };

  // Profile Management Functions
  const updateProfile = async () => {
    setSaveStatus('saving');
    try {
      await apiClient.put('/api/profile/extended/', profile);
      sendCommand('PROFILE_UPDATE', profile);
      setSaveStatus('saved');
      setTimeout(() => setSaveStatus('idle'), 3000);
    } catch (error) {
      console.error('Failed to update profile:', error);
      setSaveStatus('error');
    }
  };

  const addSkill = () => {
    if (newSkill && !profile.skills.includes(newSkill)) {
      const updatedSkills = [...profile.skills, newSkill];
      setProfile(prev => ({ ...prev, skills: updatedSkills }));
      setNewSkill('');
      sendCommand('PROFILE_UPDATE', { skills: updatedSkills });
    }
  };

  const removeSkill = (skill: string) => {
    const updatedSkills = (profile.skills || []).filter(s => s !== skill);
    setProfile(prev => ({ ...prev, skills: updatedSkills }));
    sendCommand('PROFILE_UPDATE', { skills: updatedSkills });
  };

  // AI Configuration Functions
  const updateAIConfig = async () => {
    setSaveStatus('saving');
    try {
      await apiClient.post('/api/ai/configure/', aiConfig);
      sendCommand('AI_CONFIG', aiConfig);
      setSaveStatus('saved');
      setTimeout(() => setSaveStatus('idle'), 3000);
    } catch (error) {
      console.error('Failed to update AI config:', error);
      setSaveStatus('error');
    }
  };

  const getModelCost = (model: string) => {
    const costs = {
      'gpt-5': { input: 1.25, output: 10.0, description: 'Maximum intelligence' },
      'gpt-5-mini': { input: 0.25, output: 2.0, description: 'Balanced performance' },
      'gpt-5-nano': { input: 0.05, output: 0.40, description: 'Fast & economical' },
    };
    return costs[model as keyof typeof costs];
  };

  // Agent Management Functions
  const toggleAgent = async (agentName: string) => {
    const isSelected = selectedAgents.includes(agentName);
    if (isSelected) {
      setSelectedAgents(prev => prev.filter(a => a !== agentName));
      setSummaryStats(prev => ({ ...prev, activeAgents: prev.activeAgents - 1 }));
      await apiClient.delete(`/api/agents/${agentName}/`);
      sendCommand('AGENT_CONTROL', { agent_id: agentName, action: 'stop' });
    } else {
      setSelectedAgents(prev => [...prev, agentName]);
      setSummaryStats(prev => ({ ...prev, activeAgents: prev.activeAgents + 1 }));
      await apiClient.post('/api/agents/assign/', { agent_name: agentName });
      sendCommand('AGENT_CONTROL', { agent_id: agentName, action: 'start' });
    }
  };

  const updateAgentStatus = (agentData: any) => {
    setAgents(prev => (prev || []).map(agent =>
      agent.agentName === agentData.agentName
        ? { ...agent, ...agentData }
        : agent
    ));
  };

  // Command Execution Functions
  const executeCommand = async () => {
    if (!commandInput.trim()) return;

    setCommandProcessing(true);
    const command = {
      input: commandInput,
      context: {
        profile: profile,
        aiConfig: aiConfig,
        activeAgents: selectedAgents,
      },
    };

    try {
      const response = await apiClient.post('/api/commands/execute/', command);
      handleCommandResult(response.data);
      setCommandInput('');
    } catch (error) {
      console.error('Command execution failed:', error);
    } finally {
      setCommandProcessing(false);
    }
  };

  const handleCommandResult = (result: CommandResult) => {
    setCommandHistory(prev => [{
      timestamp: new Date().toISOString(),
      ...result,
    }, ...prev.slice(0, 9)]);
  };

  // Calculate profile completion
  useEffect(() => {
    const fields = [
      profile.skills.length > 0,
      profile.experienceYears > 0,
      profile.currentRole !== '',
      profile.industries.length > 0,
      profile.resumeId !== undefined,
    ];
    const completion = (fields.filter(Boolean).length / fields.length) * 100;
    setProfile(prev => ({ ...prev, completionPercentage: completion }));
  }, [profile.skills, profile.experienceYears, profile.currentRole, profile.industries, profile.resumeId]);

  return (
    <div className="w-full max-w-6xl mx-auto p-4 space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Command className="h-8 w-8 text-primary" />
              <div>
                <CardTitle className="text-2xl">Unified Command Center</CardTitle>
                <CardDescription>
                  Complete control hub for profile, opportunities, revenue, AI, and agents
                </CardDescription>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant={profile.completionPercentage === 100 ? 'default' : 'secondary'}>
                Profile {profile.completionPercentage}% Complete
              </Badge>
              {saveStatus === 'saving' && <RefreshCw className="h-4 w-4 animate-spin" />}
              {saveStatus === 'saved' && <CheckCircle className="h-4 w-4 text-green-500" />}
              {saveStatus === 'error' && <AlertCircle className="h-4 w-4 text-red-500" />}
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Summary Stats Bar */}
      <div className="grid grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Total Revenue</p>
              <p className="text-2xl font-bold">${summaryStats.totalRevenue.toFixed(2)}</p>
            </div>
            <DollarSign className="h-8 w-8 text-green-500" />
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Active Opportunities</p>
              <p className="text-2xl font-bold">{summaryStats.activeOpportunities}</p>
            </div>
            <Briefcase className="h-8 w-8 text-blue-500" />
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Success Rate</p>
              <p className="text-2xl font-bold">{summaryStats.successRate}%</p>
            </div>
            <TrendingUp className="h-8 w-8 text-purple-500" />
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Active Agents</p>
              <p className="text-2xl font-bold">{summaryStats.activeAgents}</p>
            </div>
            <Bot className="h-8 w-8 text-orange-500" />
          </div>
        </Card>
      </div>

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="profile" className="flex items-center gap-2">
            <User className="h-4 w-4" />
            Profile
          </TabsTrigger>
          <TabsTrigger value="opportunities" className="flex items-center gap-2">
            <Briefcase className="h-4 w-4" />
            Opportunities
          </TabsTrigger>
          <TabsTrigger value="revenue" className="flex items-center gap-2">
            <DollarSign className="h-4 w-4" />
            Revenue
          </TabsTrigger>
          <TabsTrigger value="ai-config" className="flex items-center gap-2">
            <Brain className="h-4 w-4" />
            AI Config
          </TabsTrigger>
          <TabsTrigger value="agents" className="flex items-center gap-2">
            <Bot className="h-4 w-4" />
            Agents
          </TabsTrigger>
          <TabsTrigger value="command" className="flex items-center gap-2">
            <Zap className="h-4 w-4" />
            Command
          </TabsTrigger>
        </TabsList>

        {/* Profile Tab */}
        <TabsContent value="profile" className="space-y-4">
          {/* Interview Onboarding Card */}
          {!interviewCompleted && profile.completionPercentage < 50 && (
            <Card className="border-2 border-primary/20 bg-primary/5">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Sparkles className="h-6 w-6 text-primary" />
                    <div>
                      <CardTitle className="text-lg">Get Personalized AI Assistance</CardTitle>
                      <CardDescription>
                        Let me learn about you in just 8-10 minutes to unlock personalized income opportunities
                      </CardDescription>
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-4">
                  <Button
                    onClick={() => setShowInterview(true)}
                    className="flex items-center gap-2"
                    size="lg"
                  >
                    <MessageCircle className="h-4 w-4" />
                    Start Interview
                  </Button>
                  <span className="text-sm text-muted-foreground">
                    Quick interview to understand your skills and goals
                  </span>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Completed Interview Success Card */}
          {interviewCompleted && (
            <Alert className="border-green-500/50 bg-green-500/10">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <AlertDescription className="ml-2">
                Interview completed! Your AI Assistant now has a deep understanding of your skills and goals.
              </AlertDescription>
            </Alert>
          )}

          <Card>
            <CardHeader>
              <CardTitle>Professional Profile</CardTitle>
              <Progress value={profile.completionPercentage} className="mt-2" />
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Skills Section */}
              <div className="space-y-2">
                <Label>Skills</Label>
                <div className="flex gap-2">
                  <Input
                    placeholder="Add a skill..."
                    value={newSkill}
                    onChange={(e) => setNewSkill(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && addSkill()}
                  />
                  <Button onClick={addSkill} size="sm">Add</Button>
                </div>
                <div className="flex flex-wrap gap-2 mt-2">
                  {(profile.skills || []).map(skill => (
                    <div
                      key={skill}
                      className="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-secondary text-secondary-foreground cursor-pointer hover:bg-secondary/80"
                      onClick={() => removeSkill(skill)}
                    >
                      <span className="text-sm">{skill}</span>
                      <span className="text-sm">×</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Experience Section */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Years of Experience</Label>
                  <Input
                    type="number"
                    value={profile.experienceYears || ''}
                    onChange={(e) => setProfile(prev => ({
                      ...prev,
                      experienceYears: parseInt(e.target.value) || 0
                    }))}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Current Role</Label>
                  <Input
                    value={profile.currentRole || ''}
                    onChange={(e) => setProfile(prev => ({
                      ...prev,
                      currentRole: e.target.value
                    }))}
                    placeholder="e.g., Senior Developer"
                  />
                </div>
              </div>

              {/* Work Preferences */}
              <div className="space-y-2">
                <Label>Work Preferences</Label>
                <div className="space-y-3 p-4 border rounded-lg">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="remote">Remote Work</Label>
                    <Switch
                      id="remote"
                      checked={profile.jobPreferences?.remote || false}
                      onCheckedChange={(checked) => setProfile(prev => ({
                        ...prev,
                        jobPreferences: { ...(prev.jobPreferences || {}), remote: checked }
                      }))}
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <Label htmlFor="contract">Contract Work</Label>
                    <Switch
                      id="contract"
                      checked={profile.jobPreferences?.contract || false}
                      onCheckedChange={(checked) => setProfile(prev => ({
                        ...prev,
                        jobPreferences: { ...(prev.jobPreferences || {}), contract: checked }
                      }))}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Minimum Hourly Rate: ${profile.jobPreferences?.hourlyRateMin || 100}</Label>
                    <Slider
                      value={[profile.jobPreferences?.hourlyRateMin || 100]}
                      onValueChange={([value]) => setProfile(prev => ({
                        ...prev,
                        jobPreferences: { ...(prev.jobPreferences || {}), hourlyRateMin: value }
                      }))}
                      min={50}
                      max={500}
                      step={10}
                    />
                  </div>
                </div>
              </div>

              {/* Links Section */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>LinkedIn URL</Label>
                  <Input
                    type="url"
                    value={profile.linkedinUrl || ''}
                    onChange={(e) => setProfile(prev => ({
                      ...prev,
                      linkedinUrl: e.target.value
                    }))}
                    placeholder="https://linkedin.com/in/..."
                  />
                </div>
                <div className="space-y-2">
                  <Label>GitHub URL</Label>
                  <Input
                    type="url"
                    value={profile.githubUrl || ''}
                    onChange={(e) => setProfile(prev => ({
                      ...prev,
                      githubUrl: e.target.value
                    }))}
                    placeholder="https://github.com/..."
                  />
                </div>
              </div>

              <Button onClick={updateProfile} className="w-full">
                <Save className="h-4 w-4 mr-2" />
                Save Profile
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* AI Configuration Tab */}
        <TabsContent value="ai-config" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>AI Configuration</CardTitle>
              <CardDescription>
                Configure how AI agents work for you
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Model Selection */}
              <div className="space-y-2">
                <Label>Default AI Model</Label>
                <Select
                  value={aiConfig.defaultModel || 'gpt-5-mini'}
                  onValueChange={(value: any) => setAIConfig(prev => ({
                    ...prev,
                    defaultModel: value
                  }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="gpt-5-nano">
                      GPT-5 Nano - Fast & Economical ($0.05/$0.40 per 1K tokens)
                    </SelectItem>
                    <SelectItem value="gpt-5-mini">
                      GPT-5 Mini - Balanced ($0.25/$2.00 per 1K tokens)
                    </SelectItem>
                    <SelectItem value="gpt-5">
                      GPT-5 - Maximum Intelligence ($1.25/$10.00 per 1K tokens)
                    </SelectItem>
                  </SelectContent>
                </Select>
                {aiConfig.defaultModel && (
                  <Alert>
                    <Info className="h-4 w-4" />
                    <AlertDescription>
                      {getModelCost(aiConfig.defaultModel)?.description}
                    </AlertDescription>
                  </Alert>
                )}
              </div>

              {/* Reasoning Level */}
              <div className="space-y-2">
                <Label>Reasoning Level</Label>
                <Select
                  value={aiConfig.reasoningLevel || 'medium'}
                  onValueChange={(value: any) => setAIConfig(prev => ({
                    ...prev,
                    reasoningLevel: value
                  }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="minimal">Minimal - Quick responses</SelectItem>
                    <SelectItem value="low">Low - Basic reasoning</SelectItem>
                    <SelectItem value="medium">Medium - Standard analysis</SelectItem>
                    <SelectItem value="high">High - Deep reasoning</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Automation Level */}
              <div className="space-y-2">
                <Label>Automation Level</Label>
                <Select
                  value={aiConfig.automationLevel || 'semi-auto'}
                  onValueChange={(value: any) => setAIConfig(prev => ({
                    ...prev,
                    automationLevel: value
                  }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="manual">Manual - I approve everything</SelectItem>
                    <SelectItem value="semi-auto">Semi-Auto - Notify me of actions</SelectItem>
                    <SelectItem value="auto">Auto - Act on my behalf</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Cost Controls */}
              <div className="space-y-4 p-4 border rounded-lg">
                <h4 className="font-medium flex items-center gap-2">
                  <DollarSign className="h-4 w-4" />
                  Cost Controls
                </h4>
                <div className="space-y-2">
                  <Label>
                    Daily Token Limit: {(aiConfig.dailyTokenLimit || 100000).toLocaleString()} tokens
                  </Label>
                  <Slider
                    value={[aiConfig.dailyTokenLimit || 100000]}
                    onValueChange={([value]) => setAIConfig(prev => ({
                      ...prev,
                      dailyTokenLimit: value
                    }))}
                    min={10000}
                    max={1000000}
                    step={10000}
                  />
                </div>
                <div className="space-y-2">
                  <Label>
                    Monthly Spending Limit: ${aiConfig.monthlySpendingLimit || 50}
                  </Label>
                  <Slider
                    value={[aiConfig.monthlySpendingLimit || 50]}
                    onValueChange={([value]) => setAIConfig(prev => ({
                      ...prev,
                      monthlySpendingLimit: value
                    }))}
                    min={10}
                    max={500}
                    step={10}
                  />
                </div>
              </div>

              {/* Memory Settings */}
              <div className="space-y-3 p-4 border rounded-lg">
                <h4 className="font-medium flex items-center gap-2">
                  <Shield className="h-4 w-4" />
                  Memory & Privacy
                </h4>
                <div className="flex items-center justify-between">
                  <Label htmlFor="share-memory">Share Memory Across Agents</Label>
                  <Switch
                    id="share-memory"
                    checked={aiConfig.shareMemoryAcrossAgents}
                    onCheckedChange={(checked) => setAIConfig(prev => ({
                      ...prev,
                      shareMemoryAcrossAgents: checked
                    }))}
                  />
                </div>
                <div className="space-y-2">
                  <Label>
                    Memory Retention: {aiConfig.memoryRetentionDays || 90} days
                  </Label>
                  <Slider
                    value={[aiConfig.memoryRetentionDays || 90]}
                    onValueChange={([value]) => setAIConfig(prev => ({
                      ...prev,
                      memoryRetentionDays: value
                    }))}
                    min={7}
                    max={365}
                    step={7}
                  />
                </div>
              </div>

              <Button onClick={updateAIConfig} className="w-full">
                <Save className="h-4 w-4 mr-2" />
                Save AI Configuration
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Agents Tab */}
        <TabsContent value="agents" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Agent Management</CardTitle>
              <CardDescription>
                Configure your AI agents and their capabilities
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {Array.isArray(agents) ? agents.map(agent => (
                  <div
                    key={agent.agentName}
                    className="flex items-center justify-between p-4 border rounded-lg"
                  >
                    <div className="flex items-center gap-3">
                      <Switch
                        checked={selectedAgents.includes(agent.agentName)}
                        onCheckedChange={() => toggleAgent(agent.agentName)}
                      />
                      <div>
                        <div className="font-medium">{agent.agentName}</div>
                        <div className="text-sm text-muted-foreground">
                          Type: {agent.agentType} | Tasks: {agent.tasksCompleted}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant={agent.successRate > 0.7 ? 'default' : 'secondary'}>
                        {(agent.successRate * 100).toFixed(0)}% Success
                      </Badge>
                      <Activity className="h-4 w-4 text-muted-foreground" />
                    </div>
                  </div>
                )) : (
                  <div className="text-center py-4 text-muted-foreground">
                    No agents available
                  </div>
                )}
              </div>

              {/* Available Agents */}
              <div className="mt-6 p-4 border-2 border-dashed rounded-lg">
                <h4 className="font-medium mb-2">Available Agent Types</h4>
                <div className="grid grid-cols-3 gap-2 text-sm">
                  <Badge variant="outline">Income Builder</Badge>
                  <Badge variant="outline">Career Advisor</Badge>
                  <Badge variant="outline">Skill Matcher</Badge>
                  <Badge variant="outline">Resume Optimizer</Badge>
                  <Badge variant="outline">Interview Prep</Badge>
                  <Badge variant="outline">Salary Negotiator</Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Opportunities Tab */}
        <TabsContent value="opportunities" className="space-y-4">
          <OpportunitiesHub />
        </TabsContent>

        {/* Revenue Tab */}
        <TabsContent value="revenue" className="space-y-4">
          <RevenueDashboard />
        </TabsContent>

        {/* Command Tab */}
        <TabsContent value="command" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Command Execution</CardTitle>
              <CardDescription>
                Direct control interface for system commands
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Command Input */}
              <div className="space-y-2">
                <Label>Enter Command</Label>
                <div className="flex gap-2">
                  <Input
                    placeholder="e.g., Find Python jobs paying over $150/hr..."
                    value={commandInput}
                    onChange={(e) => setCommandInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && executeCommand()}
                    disabled={commandProcessing}
                  />
                  <Button
                    onClick={executeCommand}
                    disabled={commandProcessing || !commandInput.trim()}
                  >
                    {commandProcessing ? (
                      <RefreshCw className="h-4 w-4 animate-spin" />
                    ) : (
                      <Zap className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </div>

              {/* Quick Commands */}
              <div className="space-y-2">
                <Label>Quick Commands</Label>
                <div className="grid grid-cols-2 gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setCommandInput('Find opportunities matching my skills');
                      executeCommand();
                    }}
                  >
                    Find Matching Jobs
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setCommandInput('Analyze my profile completeness');
                      executeCommand();
                    }}
                  >
                    Analyze Profile
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setCommandInput('Optimize my agent assignments');
                      executeCommand();
                    }}
                  >
                    Optimize Agents
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setCommandInput('Generate income report');
                      executeCommand();
                    }}
                  >
                    Income Report
                  </Button>
                </div>
              </div>

              {/* Command History */}
              <div className="space-y-2">
                <Label>Recent Commands</Label>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {commandHistory.map((cmd, idx) => (
                    <div
                      key={idx}
                      className={`p-3 border rounded-lg text-sm ${
                        cmd.success ? 'border-green-200' : 'border-red-200'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-medium">{cmd.message}</span>
                        <span className="text-xs text-muted-foreground">
                          {new Date(cmd.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                      {cmd.data && (
                        <div className="text-xs text-muted-foreground mt-1">
                          {JSON.stringify(cmd.data).substring(0, 100)}...
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Status Bar */}
      <Card>
        <CardContent className="py-3">
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <Activity className="h-4 w-4 text-green-500" />
                <span>System Active</span>
              </div>
              <div className="flex items-center gap-2">
                <Bot className="h-4 w-4" />
                <span>{selectedAgents.length} Agents</span>
              </div>
              <div className="flex items-center gap-2">
                <Brain className="h-4 w-4" />
                <span>{aiConfig.defaultModel}</span>
              </div>
            </div>
            <div className="flex items-center gap-2 text-muted-foreground">
              <Target className="h-4 w-4" />
              <span>Profile {profile.completionPercentage}%</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Personal Assistant Interview Modal */}
      <PersonalAssistantInterview
        isOpen={showInterview}
        onClose={() => setShowInterview(false)}
        onComplete={(profile) => {
          console.log('Interview completed with profile:', profile);
          setInterviewCompleted(true);
          setShowInterview(false);

          // Update profile with interview data
          if (profile.name) {
            setProfile(prev => ({
              ...prev,
              username: profile.name,
            }));
          }
          if (profile.all_skills) {
            setProfile(prev => ({
              ...prev,
              skills: profile.all_skills,
            }));
          }
          if (profile.professional_background) {
            setProfile(prev => ({
              ...prev,
              currentRole: profile.professional_background.split(',')[0] || prev.currentRole,
            }));
          }

          // Save interview results
          updateProfile();
        }}
      />
    </div>
  );
};

export default UserCommandCenter;