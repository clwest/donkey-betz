import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import FileViewer from './FileViewer';
import {
  DollarSign,
  TrendingUp,
  Clock,
  Target,
  Zap,
  CheckCircle,
  ArrowRight,
  Sparkles,
  Trophy,
  Rocket,
  Download,
  Wifi,
  WifiOff,
  Eye,
  FileText
} from 'lucide-react';

// Use API configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

interface Opportunity {
  id: string;
  title: string;
  stream_type: string;
  description: string;
  time_to_income: string;
  potential_monthly: string;
  difficulty: string;
  initial_investment: number;
  success_rate: number;
  market_demand: number;
  required_skills: string[];
  action_steps: string[];
  resources: Array<{ name: string; url: string }>;
}

interface RevenueData {
  current_metrics: {
    total_revenue: number;
    monthly_revenue: number;
    weekly_revenue: number;
    daily_revenue: number;
  };
  by_category: {
    content: number;
    ai_services: number;
    digital_products: number;
    trading: number;
    freelancing: number;
  };
  projections: {
    monthly: number;
    yearly: number;
  };
}

export default function IncomeBuilder() {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [selectedOpportunity, setSelectedOpportunity] = useState<Opportunity | null>(null);
  const [revenueData, setRevenueData] = useState<RevenueData | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('opportunities');
  const [actionPlans, setActionPlans] = useState<any[]>([]);
  const [wsConnected, setWsConnected] = useState(false);
  const [viewingFile, setViewingFile] = useState<string | null>(null);
  const [activeAutomations, setActiveAutomations] = useState<any[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    fetchOpportunities();
    fetchRevenueData();
    loadActionPlansFromBackend();

    // Connect to WebSocket for real-time updates
    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const connectWebSocket = () => {
    try {
      const ws = new WebSocket(`${WS_BASE_URL}/ws/income-builder/`);

      ws.onopen = () => {
        console.log('✅ WebSocket connected for Income Builder');
        setWsConnected(true);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleWebSocketMessage(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setWsConnected(false);
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setWsConnected(false);
        // Attempt to reconnect after 5 seconds
        setTimeout(connectWebSocket, 5000);
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Error connecting to WebSocket:', error);
      setWsConnected(false);
    }
  };

  const handleWebSocketMessage = (data: any) => {
    if (data.type === 'action_plan_update') {
      // Update specific action plan
      setActionPlans(prev => prev.map(plan =>
        plan.backend_id === data.plan_id
          ? {
              ...plan,
              status: data.status,
              progress: data.progress,
              current_step: data.current_step,
              execution_logs: data.execution_logs,
              results: data.results || plan.results,
              completed_at: data.completed_at
            }
          : plan
      ));
    } else if (data.type === 'new_opportunity') {
      // Add new opportunity
      setOpportunities(prev => [...prev, data.opportunity]);
    }
  };

  // Poll for action plan status updates
  useEffect(() => {
    const pollInterval = setInterval(async () => {
      // Check if any plans are in progress
      const inProgressPlans = actionPlans.filter(p => p.status === 'in_progress' && p.backend_id);

      if (inProgressPlans.length > 0) {
        try {
          const response = await fetch('http://localhost:8000/api/v1/intelligence/income-builder/execute/');
          const data = await response.json();

          console.log('📊 Polling response:', data);

          if (data.success && data.plans) {
            let hasNewlyCompleted = false;

            // Update local plans with backend status
            const updatedPlans = actionPlans.map(localPlan => {
              const backendPlan = data.plans.find((bp: any) => bp.id === localPlan.backend_id);
              if (backendPlan) {
                console.log(`📋 Backend plan for ${localPlan.backend_id}:`, backendPlan);
                console.log('📁 Results:', backendPlan.results);

                // Check if this plan just completed
                if (localPlan.status !== 'completed' && backendPlan.status === 'completed') {
                  hasNewlyCompleted = true;
                  console.log('✅ Plan just completed with results:', {
                    files: backendPlan.results?.files_created,
                    status: backendPlan.results?.status,
                    message: backendPlan.results?.message
                  });
                }

                return {
                  ...localPlan,
                  status: backendPlan.status,
                  progress: backendPlan.progress,
                  current_step: backendPlan.current_step,
                  execution_logs: backendPlan.execution_logs,
                  completed_at: backendPlan.completed_at,
                  results: backendPlan.results || {},
                  steps: backendPlan.steps || localPlan.steps,
                  resources: backendPlan.resources || localPlan.resources
                };
              }
              return localPlan;
            });

            setActionPlans(updatedPlans);
            localStorage.setItem('incomeBuilderActionPlans', JSON.stringify(updatedPlans));

            // Save to backend
            saveActionPlansToBackend(updatedPlans);

            // Auto-switch to completed tab when a plan finishes
            if (hasNewlyCompleted) {
              setActiveTab('completed-plans');
            }
          }
        } catch (error) {
          console.error('Error polling plan status:', error);
        }
      }
    }, 5000); // Poll every 5 seconds

    return () => clearInterval(pollInterval);
  }, [actionPlans]);

  const analyzePlanForAutomation = async (plan: any) => {
    try {
      const planContent = await fetch(`${API_BASE_URL}${plan.file_path}`).then(r => r.text());

      const response = await fetch('http://localhost:5001/api/income-builder/analyze-plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plan_content: planContent })
      });

      const analysis = await response.json();

      // Update plan with analysis
      const updatedPlans = actionPlans.map(p =>
        p.id === plan.id ? { ...p, automation_analysis: analysis } : p
      );
      setActionPlans(updatedPlans);
      localStorage.setItem('incomeBuilderActionPlans', JSON.stringify(updatedPlans));

    } catch (error) {
      console.error('Error analyzing plan:', error);
    }
  };

  const executePlanAutomation = async (plan: any) => {
    try {
      const response = await fetch('http://localhost:5001/api/income-builder/process-plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          plan_file: plan.file_path.replace('/static/', 'income_builder_outputs/'),
          auto_execute: true
        })
      });

      const result = await response.json();

      if (result.execution_id) {
        // Track active automation
        setActiveAutomations(prev => [...prev, {
          execution_id: result.execution_id,
          plan_type: plan.opportunity_title,
          started_at: new Date().toISOString(),
          status: 'running'
        }]);

        // Start monitoring execution
        monitorAutomationExecution(result.execution_id);
      }
    } catch (error) {
      console.error('Error executing automation:', error);
    }
  };

  const monitorAutomationExecution = async (executionId: string) => {
    const checkStatus = async () => {
      try {
        const response = await fetch(`http://localhost:5001/api/income-builder/execution-status/${executionId}`);
        const status = await response.json();

        setActiveAutomations(prev => prev.map(a =>
          a.execution_id === executionId
            ? { ...a, ...status }
            : a
        ));

        // Continue monitoring if still running
        if (status.progress?.pending > 0 || status.progress?.in_progress > 0) {
          setTimeout(() => checkStatus(), 5000);
        } else {
          // Mark as completed
          setActiveAutomations(prev => prev.map(a =>
            a.execution_id === executionId
              ? { ...a, status: 'completed' }
              : a
          ));
        }
      } catch (error) {
        console.error('Error monitoring execution:', error);
      }
    };

    checkStatus();
  };

  const fetchOpportunities = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/v1/intelligence/income-builder/`);
      const data = await response.json();
      if (data.success) {
        setOpportunities(data.opportunities);
      }
    } catch (error) {
      console.error('Error fetching opportunities:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchRevenueData = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/v1/monetization/opportunities/`);
      const data = await response.json();
      if (data.success) {
        setRevenueData(data.dashboard);
      }
    } catch (error) {
      console.error('Error fetching revenue data:', error);
    }
  };

  const loadActionPlansFromBackend = async () => {
    try {
      // First try to load from backend
      const response = await fetch(`${API_BASE_URL}/v1/intelligence/income-builder/plans/`, {
        credentials: 'include' // Include cookies for session handling
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success && data.plans && data.plans.length > 0) {
          console.log('📂 Loaded', data.plans.length, 'plans from backend');
          setActionPlans(data.plans);

          // Check if we should show completed tab
          const completedCount = data.plans.filter((p: any) => p.status === 'completed').length;
          const inProgressCount = data.plans.filter((p: any) => p.status === 'in_progress').length;

          if (completedCount > 0 && inProgressCount === 0) {
            setActiveTab('completed-plans');
          }

          // Also save to localStorage as backup
          localStorage.setItem('incomeBuilderActionPlans', JSON.stringify(data.plans));
          return;
        }
      }
    } catch (error) {
      console.error('Error loading plans from backend:', error);
    }

    // Fallback to localStorage if backend fails or has no data
    const savedPlans = localStorage.getItem('incomeBuilderActionPlans');
    if (savedPlans) {
      try {
        const parsedPlans = JSON.parse(savedPlans);
        setActionPlans(parsedPlans);

        // If there are completed plans and user hasn't created new ones, show completed tab
        const completedCount = parsedPlans.filter((p: any) => p.status === 'completed').length;
        const inProgressCount = parsedPlans.filter((p: any) => p.status === 'in_progress').length;

        if (completedCount > 0 && inProgressCount === 0) {
          setActiveTab('completed-plans');
        }

        // Try to sync localStorage plans to backend
        if (parsedPlans.length > 0) {
          saveActionPlansToBackend(parsedPlans);
        }
      } catch (e) {
        console.error('Error loading saved action plans:', e);
      }
    }
  };

  const saveActionPlansToBackend = async (plans: any[]) => {
    try {
      const response = await fetch(`${API_BASE_URL}/v1/intelligence/income-builder/plans/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Include cookies for session handling
        body: JSON.stringify({ plans })
      });

      if (response.ok) {
        const data = await response.json();
        console.log('💾 Saved', data.saved_plans?.length || 0, 'plans to backend');
      }
    } catch (error) {
      console.error('Error saving plans to backend:', error);
    }
  };

  const createActionPlan = async (opportunityId: string) => {
    try {
      console.log('🎯 Creating action plan for opportunity:', opportunityId);

      const response = await fetch(`${API_BASE_URL}/v1/intelligence/income-builder/action-plan/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ opportunity_id: opportunityId })
      });
      const data = await response.json();

      console.log('📝 Action plan response:', data);

      if (data.success && data.action_plan) {
        // Add opportunity title to the action plan
        const opportunity = opportunities.find(o => o.id === opportunityId);
        const planWithTitle = {
          ...data.action_plan,
          opportunity_title: opportunity?.title || 'Unknown Opportunity',
          opportunity_id: opportunityId,
          created_at: new Date().toISOString()
        };

        console.log('💾 Storing action plan:', planWithTitle);

        // Store the action plan locally
        const updatedPlans = [...actionPlans, planWithTitle];
        setActionPlans(updatedPlans);

        // Save to localStorage
        localStorage.setItem('incomeBuilderActionPlans', JSON.stringify(updatedPlans));

        // Save to backend
        saveActionPlansToBackend(updatedPlans);

        // Switch to the action plans tab
        setActiveTab('action-plans');

        // Select the opportunity
        if (opportunity) {
          setSelectedOpportunity(opportunity);
        }
      }
    } catch (error) {
      console.error('Error creating action plan:', error);
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch(difficulty.toLowerCase()) {
      case 'beginner': return 'bg-green-500';
      case 'intermediate': return 'bg-yellow-500';
      case 'advanced': return 'bg-orange-500';
      case 'expert': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          AI Income Builder
        </h1>
        <p className="text-lg text-gray-600">Start earning from $0 with AI-powered opportunities</p>
      </div>

      {/* Revenue Overview */}
      {revenueData && (
        <Card className=" bg-slate-800">
          <CardHeader  >
            <CardTitle className="flex items-center gap-2">
              <Trophy className="h-6 w-6 text-yellow-500" />
              Your Revenue Dashboard
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center">
                <p className="text-sm text-gray-600">Daily Revenue</p>
                <p className="text-2xl font-bold text-green-600">
                  ${revenueData.current_metrics.daily_revenue.toFixed(2)}
                </p>
              </div>
              <div className="text-center">
                <p className="text-sm text-gray-600">Monthly Revenue</p>
                <p className="text-2xl font-bold text-blue-600">
                  ${revenueData.current_metrics.monthly_revenue.toFixed(2)}
                </p>
              </div>
              <div className="text-center">
                <p className="text-sm text-gray-600">Projected Monthly</p>
                <p className="text-2xl font-bold text-purple-600">
                  ${revenueData.projections.monthly.toFixed(2)}
                </p>
              </div>
              <div className="text-center">
                <p className="text-sm text-gray-600">Projected Yearly</p>
                <p className="text-2xl font-bold text-indigo-600">
                  ${revenueData.projections.yearly.toFixed(2)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* WebSocket Connection Status */}
      <div className="flex justify-end mb-2">
        <Badge variant={wsConnected ? "default" : "secondary"} className="flex items-center gap-1">
          {wsConnected ? <Wifi className="h-3 w-3" /> : <WifiOff className="h-3 w-3" />}
          {wsConnected ? 'Live Updates' : 'Reconnecting...'}
        </Badge>
      </div>

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="opportunities">Opportunities</TabsTrigger>
          <TabsTrigger value="action-plans">
            My Action Plans
            {actionPlans.filter(p => p.status === 'in_progress').length > 0 && (
              <Badge className="ml-2 bg-blue-500 text-white text-xs">
                {actionPlans.filter(p => p.status === 'in_progress').length}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="completed-plans" className="relative">
            <span className="flex items-center gap-2">
              <Trophy className="h-4 w-4 text-yellow-500" />
              Completed
              {actionPlans.filter(p => p.status === 'completed').length > 0 && (
                <Badge className="bg-green-500 text-white text-xs">
                  {actionPlans.filter(p => p.status === 'completed').length}
                </Badge>
              )}
            </span>
          </TabsTrigger>
          <TabsTrigger value="quick-start">Quick Start</TabsTrigger>
          <TabsTrigger value="automation">Automation</TabsTrigger>
        </TabsList>

        {/* Automation Tab - NEW */}
        <TabsContent value="automation" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="h-5 w-5 text-yellow-500" />
                Automated Task Execution
              </CardTitle>
              <CardDescription>
                Your Income Builder plans can now be automatically executed by our 102+ agent network
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Automation Overview */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card className="border-2 border-blue-200">
                  <CardContent className="pt-6">
                    <div className="flex items-center gap-2 mb-2">
                      <Target className="h-5 w-5 text-blue-500" />
                      <p className="font-semibold">Task Extraction</p>
                    </div>
                    <p className="text-sm text-gray-600">
                      Plans automatically parsed into 10-15 actionable tasks
                    </p>
                  </CardContent>
                </Card>
                <Card className="border-2 border-purple-200">
                  <CardContent className="pt-6">
                    <div className="flex items-center gap-2 mb-2">
                      <Rocket className="h-5 w-5 text-purple-500" />
                      <p className="font-semibold">Agent Delegation</p>
                    </div>
                    <p className="text-sm text-gray-600">
                      Tasks routed to specialized agents for execution
                    </p>
                  </CardContent>
                </Card>
                <Card className="border-2 border-green-200">
                  <CardContent className="pt-6">
                    <div className="flex items-center gap-2 mb-2">
                      <CheckCircle className="h-5 w-5 text-green-500" />
                      <p className="font-semibold">Real Results</p>
                    </div>
                    <p className="text-sm text-gray-600">
                      Actual deliverables created automatically
                    </p>
                  </CardContent>
                </Card>
              </div>

              {/* Plans with Automation */}
              <div className="space-y-4">
                <h3 className="font-semibold">Automation-Ready Plans</h3>
                {actionPlans.filter(p => p.status === 'completed' && p.file_path).map((plan, index) => (
                  <Card key={index} className="border-l-4 border-l-green-500">
                    <CardHeader>
                      <div className="flex justify-between items-center">
                        <div>
                          <CardTitle className="text-lg">{plan.opportunity_title}</CardTitle>
                          <CardDescription>Completed: {new Date(plan.completed_at || Date.now()).toLocaleDateString()}</CardDescription>
                        </div>
                        <div className="flex gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => analyzePlanForAutomation(plan)}
                          >
                            <Target className="h-4 w-4 mr-1" />
                            Analyze Tasks
                          </Button>
                          <Button
                            variant="default"
                            size="sm"
                            onClick={() => executePlanAutomation(plan)}
                            className="bg-gradient-to-r from-purple-600 to-blue-600"
                          >
                            <Zap className="h-4 w-4 mr-1" />
                            Auto-Execute
                          </Button>
                        </div>
                      </div>
                    </CardHeader>
                    {plan.automation_analysis && (
                      <CardContent>
                        <div className="bg-gray-50 rounded-lg p-4 space-y-3">
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                            <div>
                              <p className="text-gray-600">Total Tasks</p>
                              <p className="font-bold text-lg">{plan.automation_analysis.total_tasks}</p>
                            </div>
                            <div>
                              <p className="text-gray-600">Agents Required</p>
                              <p className="font-bold text-lg">{plan.automation_analysis.agents_required?.length || 0}</p>
                            </div>
                            <div>
                              <p className="text-gray-600">Priority Tasks</p>
                              <p className="font-bold text-lg">{plan.automation_analysis.priority_tasks?.length || 0}</p>
                            </div>
                            <div>
                              <p className="text-gray-600">Phases</p>
                              <p className="font-bold text-lg">{Object.keys(plan.automation_analysis.phases || {}).length}</p>
                            </div>
                          </div>

                          {plan.automation_analysis.priority_tasks && (
                            <div>
                              <p className="font-semibold text-sm mb-2">Top Priority Tasks:</p>
                              <div className="space-y-1">
                                {plan.automation_analysis.priority_tasks.slice(0, 3).map((task: any, i: number) => (
                                  <div key={i} className="flex items-center gap-2 text-sm">
                                    <Badge variant="outline" className="text-xs">
                                      {task.agent}
                                    </Badge>
                                    <span>{task.title}</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </CardContent>
                    )}
                  </Card>
                ))}

                {actionPlans.filter(p => p.status === 'completed' && p.file_path).length === 0 && (
                  <Alert>
                    <AlertDescription>
                      Complete an action plan to unlock automation capabilities.
                      Once you have a completed plan, you can automatically execute it across our agent network.
                    </AlertDescription>
                  </Alert>
                )}
              </div>

              {/* Active Automations */}
              {activeAutomations.length > 0 && (
                <div className="space-y-4">
                  <h3 className="font-semibold">Active Automations</h3>
                  {activeAutomations.map((automation, index) => (
                    <Card key={index} className="border-2 border-blue-500">
                      <CardHeader>
                        <div className="flex justify-between items-center">
                          <CardTitle className="text-lg">{automation.plan_type}</CardTitle>
                          <Badge className="bg-blue-500">
                            <Zap className="h-3 w-3 mr-1" />
                            Running
                          </Badge>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2">
                          <div className="flex justify-between text-sm">
                            <span>Execution Progress</span>
                            <span>{automation.progress?.completion_percentage?.toFixed(0) || 0}%</span>
                          </div>
                          <Progress value={automation.progress?.completion_percentage || 0} className="h-2" />

                          <div className="grid grid-cols-3 gap-2 text-sm mt-3">
                            <div className="text-center">
                              <p className="text-gray-600">Completed</p>
                              <p className="font-bold">{automation.progress?.completed || 0}</p>
                            </div>
                            <div className="text-center">
                              <p className="text-gray-600">In Progress</p>
                              <p className="font-bold">{automation.progress?.in_progress || 0}</p>
                            </div>
                            <div className="text-center">
                              <p className="text-gray-600">Pending</p>
                              <p className="font-bold">{automation.progress?.pending || 0}</p>
                            </div>
                          </div>

                          {automation.current_tasks && automation.current_tasks.length > 0 && (
                            <div className="mt-3 p-2 bg-blue-50 rounded">
                              <p className="text-xs font-semibold mb-1">Currently Executing:</p>
                              <p className="text-xs">{automation.current_tasks[0]}</p>
                            </div>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Opportunities Tab */}
        <TabsContent value="opportunities" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {opportunities.map((opp) => (
              <Card
                key={opp.id}
                className="hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => setSelectedOpportunity(opp)}
              >
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <CardTitle className="text-lg">{opp.title}</CardTitle>
                    <Badge className={getDifficultyColor(opp.difficulty)}>
                      {opp.difficulty}
                    </Badge>
                  </div>
                  <CardDescription>{opp.description}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1">
                      <DollarSign className="h-4 w-4 text-green-600" />
                      <span className="font-semibold">{opp.potential_monthly}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Clock className="h-4 w-4 text-blue-600" />
                      <span className="text-sm">{opp.time_to_income}</span>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Success Rate</span>
                      <span>{(opp.success_rate * 100).toFixed(0)}%</span>
                    </div>
                    <Progress value={opp.success_rate * 100} className="h-2" />
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Market Demand</span>
                      <span>{(opp.market_demand * 100).toFixed(0)}%</span>
                    </div>
                    <Progress value={opp.market_demand * 100} className="h-2" />
                  </div>

                  {opp.initial_investment === 0 && (
                    <Badge variant="outline" className="w-full justify-center bg-green-50">
                      <Sparkles className="h-3 w-3 mr-1" />
                      Zero Investment Required
                    </Badge>
                  )}

                  <Button
                    className="w-full"
                    onClick={(e) => {
                      e.stopPropagation();
                      createActionPlan(opp.id);
                    }}
                  >
                    Get Action Plan
                    <ArrowRight className="h-4 w-4 ml-2" />
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Selected Opportunity Details */}
          {selectedOpportunity && (
            <Card className="mt-6 border-2 border-purple-200">
              <CardHeader>
                <CardTitle>{selectedOpportunity.title} - Detailed Plan</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h3 className="font-semibold mb-2">Required Skills:</h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedOpportunity.required_skills.map((skill, i) => (
                      <Badge key={i} variant="secondary">{skill}</Badge>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="font-semibold mb-2">Action Steps:</h3>
                  <ol className="space-y-2">
                    {selectedOpportunity.action_steps.map((step, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />
                        <span>{step}</span>
                      </li>
                    ))}
                  </ol>
                </div>

                <div>
                  <h3 className="font-semibold mb-2">Resources:</h3>
                  <div className="space-y-2">
                    {selectedOpportunity.resources.map((resource, i) => (
                      <a
                        key={i}
                        href={`https://${resource.url}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block p-2 rounded bg-blue-50 hover:bg-blue-100 transition-colors"
                      >
                        {resource.name} →
                      </a>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Action Plans Tab - Only show non-completed plans */}
        <TabsContent value="action-plans" className="space-y-4">
          {actionPlans.filter(p => p.status !== 'completed').length === 0 ? (
            <Card>
              <CardContent className="text-center py-8">
                <p className="text-gray-500 mb-4">No active action plans.</p>
                <p className="text-sm text-gray-400">Select an opportunity and click "Get Action Plan" to create a new plan.</p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold">Active Action Plans</h3>
                <Badge variant="outline">
                  {actionPlans.filter(p => p.status === 'in_progress').length} in progress
                </Badge>
              </div>
              {actionPlans.filter(p => p.status !== 'completed').map((plan, index) => (
                <Card key={index} className={plan.status === 'in_progress' ? 'border-blue-500' : ''}>
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle>{plan.opportunity_title || 'Action Plan'}</CardTitle>
                        <CardDescription>
                          Created: {new Date(plan.created_at || Date.now()).toLocaleDateString()}
                          {plan.started_at && ` • Started: ${new Date(plan.started_at).toLocaleDateString()}`}
                        </CardDescription>
                      </div>
                      {plan.status && (
                        <Badge
                          variant={plan.status === 'in_progress' ? 'default' : plan.status === 'completed' ? 'secondary' : 'outline'}
                          className={
                            plan.status === 'in_progress' ? 'bg-blue-500' :
                            plan.status === 'completed' ? 'bg-green-500' : ''
                          }
                        >
                          {plan.status === 'in_progress' ? 'In Progress' :
                           plan.status === 'completed' ? 'Completed' : 'Not Started'}
                        </Badge>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {plan.steps && (
                      <div>
                        <h4 className="font-semibold mb-2">Action Steps:</h4>
                        <ol className="list-decimal list-inside space-y-2">
                          {plan.steps.map((step: string, stepIndex: number) => (
                            <li
                              key={stepIndex}
                              className={`text-sm ${
                                plan.current_step && stepIndex < plan.current_step
                                  ? 'text-green-600 line-through'
                                  : stepIndex === plan.current_step - 1
                                  ? 'text-blue-600 font-semibold'
                                  : 'text-gray-600'
                              }`}
                            >
                              {step}
                              {plan.current_step && stepIndex < plan.current_step && (
                                <CheckCircle className="inline-block ml-2 h-3 w-3 text-green-600" />
                              )}
                            </li>
                          ))}
                        </ol>
                      </div>
                    )}

                    {plan.status === 'in_progress' && plan.progress !== undefined && (
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>Execution Progress</span>
                          <span>{plan.progress}%</span>
                        </div>
                        <Progress value={plan.progress} className="h-2" />
                      </div>
                    )}

                    {plan.execution_logs && plan.execution_logs.length > 0 && (
                      <div className="mt-4 p-3 bg-gray-50 rounded-md">
                        <h4 className="font-semibold text-sm mb-2">Execution Logs:</h4>
                        <div className="space-y-1 max-h-32 overflow-y-auto">
                          {plan.execution_logs.slice(-5).map((log: any, lIndex: number) => (
                            <div key={lIndex} className="text-xs">
                              <span className="text-gray-500">{new Date(log.timestamp).toLocaleTimeString()}</span>
                              <span className={`ml-2 ${
                                log.level === 'error' ? 'text-red-600' :
                                log.level === 'success' ? 'text-green-600' :
                                'text-gray-700'
                              }`}>
                                {log.message}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {plan.status === 'completed' && plan.results && Object.keys(plan.results).length > 0 && (
                      <div className="mt-4 p-4 bg-green-50 rounded-md">
                        <h4 className="font-semibold text-sm mb-2 text-green-800">🎉 Generated Results:</h4>
                        <div className="space-y-3">
                          {/* Display file paths if present */}
                          {plan.results.files_created && plan.results.files_created.length > 0 && (
                            <div className="border-l-2 border-green-400 pl-3">
                              <h5 className="text-xs font-semibold text-green-700 mb-1">📁 Files Created:</h5>
                              <div className="space-y-2">
                                {plan.results.files_created.map((file: string | any, idx: number) => {
                                  const filepath = typeof file === 'string' ? file : String(file);
                                  const filename = filepath.split('/').pop() || filepath;
                                  return (
                                    <div key={idx} className="flex items-center justify-between">
                                      <span className="text-sm text-gray-700">{filename}</span>
                                      <Button
                                        size="sm"
                                        variant="outline"
                                        className="text-xs gap-1"
                                        onClick={() => {
                                          // Extract just the filename from the path
                                          const filename = filepath.startsWith('income_builder_outputs/')
                                            ? filepath.replace('income_builder_outputs/', '')
                                            : filepath;
                                          setViewingFile(filename);
                                        }}
                                      >
                                        <Eye className="h-3 w-3" />
                                        View
                                      </Button>
                                    </div>
                                  );
                                })}
                              </div>
                            </div>
                          )}

                          {/* Display ML score if present */}
                          {plan.results.ml_score && (
                            <div className="border-l-2 border-green-400 pl-3">
                              <h5 className="text-xs font-semibold text-green-700 mb-1">🤖 ML Analysis Score:</h5>
                              <p className="text-sm text-gray-700">{(plan.results.ml_score * 100).toFixed(1)}% Success Probability</p>
                            </div>
                          )}

                          {/* Display other results */}
                          {Object.entries(plan.results).map(([key, value]: [string, any]) => {
                            if (key === 'files_created' || key === 'ml_score') return null;
                            return (
                              <div key={key} className="border-l-2 border-green-400 pl-3">
                                <h5 className="text-xs font-semibold text-green-700 mb-1">
                                  {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:
                                </h5>
                                <p className="text-sm text-gray-700 whitespace-pre-wrap">
                                  {typeof value === 'string' ? value.substring(0, 300) : JSON.stringify(value, null, 2).substring(0, 300)}
                                  {(typeof value === 'string' ? value : JSON.stringify(value)).length > 300 && '...'}
                                </p>
                              </div>
                            );
                          })}
                        </div>
                        <Button
                          size="sm"
                          variant="outline"
                          className="mt-3"
                          onClick={() => {
                            // Download results as formatted document
                            let content = `Income Builder Action Plan Results\n`;
                            content += `=====================================\n\n`;
                            content += `Opportunity: ${plan.opportunity_title}\n`;
                            content += `Completed: ${new Date(plan.completed_at || Date.now()).toLocaleString()}\n\n`;

                            if (plan.results.files_created) {
                              content += `Files Created:\n`;
                              plan.results.files_created.forEach((file: string) => {
                                content += `  - ${file}\n`;
                              });
                              content += `\n`;
                            }

                            content += `Full Results:\n`;
                            content += JSON.stringify(plan.results, null, 2);

                            const blob = new Blob([content], { type: 'text/plain' });
                            const url = URL.createObjectURL(blob);
                            const a = document.createElement('a');
                            a.href = url;
                            a.download = `${plan.opportunity_title.replace(/\s+/g, '_')}_results.txt`;
                            a.click();
                          }}
                        >
                          <Download className="mr-2 h-4 w-4" />
                          Download Full Results
                        </Button>
                      </div>
                    )}

                    {plan.timeline && (
                      <div>
                        <h4 className="font-semibold mb-2">Timeline:</h4>
                        <p className="text-sm text-gray-600">{plan.timeline}</p>
                      </div>
                    )}

                    {plan.expected_outcome && (
                      <div>
                        <h4 className="font-semibold mb-2">Expected Outcome:</h4>
                        <p className="text-sm text-gray-600">{plan.expected_outcome}</p>
                      </div>
                    )}

                    {/* Show additional details when expanded */}
                    {plan.expanded && (
                      <div className="mt-4 pt-4 border-t space-y-4">
                        {plan.resources && plan.resources.length > 0 && (
                          <div>
                            <h4 className="font-semibold mb-2">Resources:</h4>
                            <ul className="list-disc list-inside space-y-1">
                              {plan.resources.map((resource: any, rIndex: number) => (
                                <li key={rIndex} className="text-sm text-gray-600">
                                  {resource.name ? (
                                    <a
                                      href={resource.url?.startsWith('http') ? resource.url : `https://${resource.url}`}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      className="text-blue-600 hover:underline"
                                    >
                                      {resource.name}
                                    </a>
                                  ) : resource}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {plan.tips && (
                          <div>
                            <h4 className="font-semibold mb-2">Pro Tips:</h4>
                            <p className="text-sm text-gray-600">{plan.tips}</p>
                          </div>
                        )}

                        {plan.notes && (
                          <div>
                            <h4 className="font-semibold mb-2">Notes:</h4>
                            <p className="text-sm text-gray-600">{plan.notes}</p>
                          </div>
                        )}
                      </div>
                    )}

                    <div className="flex gap-2 pt-4">
                      <Button
                        size="sm"
                        onClick={async () => {
                          try {
                            console.log('🚀 Starting plan execution for:', plan.opportunity_title);
                            console.log('📋 Plan data:', plan);

                            // Find the opportunity
                            const opportunity = opportunities.find(o => o.id === plan.opportunity_id);

                            // Call backend API to save and execute the plan
                            const response = await fetch('http://localhost:8000/api/v1/intelligence/income-builder/execute/', {
                              method: 'POST',
                              headers: {
                                'Content-Type': 'application/json',
                              },
                              body: JSON.stringify({
                                plan: plan,
                                opportunity: opportunity || { id: plan.opportunity_id, title: plan.opportunity_title }
                              })
                            });

                            const data = await response.json();
                            console.log('🔄 Execute response:', data);

                            if (data.success) {
                              // Update local state with backend plan ID
                              const updatedPlans = actionPlans.map((p, i) =>
                                i === index ? {
                                  ...p,
                                  status: 'in_progress',
                                  started_at: new Date().toISOString(),
                                  backend_id: data.plan_id,
                                  celery_task_id: data.celery_task_id
                                } : p
                              );
                              setActionPlans(updatedPlans);
                              localStorage.setItem('incomeBuilderActionPlans', JSON.stringify(updatedPlans));

                              // Show success message
                              console.log(`✅ Action plan launched! ID: ${data.plan_id}`);

                              // Switch to opportunities tab
                              if (opportunity) {
                                setSelectedOpportunity(opportunity);
                                setActiveTab('opportunities');
                              }
                            } else {
                              console.error('Failed to launch plan:', data.error);
                              alert(`Failed to launch plan: ${data.error}`);
                            }
                          } catch (error) {
                            console.error('Error launching plan:', error);
                            alert('Error launching plan. Check console for details.');
                          }
                        }}
                        disabled={plan.status === 'in_progress' || plan.status === 'completed'}
                      >
                        <CheckCircle className="mr-2 h-4 w-4" />
                        {plan.status === 'in_progress' ? 'In Progress' : plan.status === 'completed' ? 'Completed' : 'Start Plan'}
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => {
                          // Expand/collapse plan details
                          const updatedPlans = actionPlans.map((p, i) =>
                            i === index ? { ...p, expanded: !p.expanded } : p
                          );
                          setActionPlans(updatedPlans);
                        }}
                      >
                        {plan.expanded ? 'Hide Details' : 'View Details'}
                      </Button>
                      {plan.expanded && (
                        <Button
                          size="sm"
                          variant="outline"
                          className="text-red-600 hover:text-red-700"
                          onClick={() => {
                            if (confirm('Are you sure you want to delete this action plan?')) {
                              const updatedPlans = actionPlans.filter((_, i) => i !== index);
                              setActionPlans(updatedPlans);
                              localStorage.setItem('incomeBuilderActionPlans', JSON.stringify(updatedPlans));
                            }
                          }}
                        >
                          Delete Plan
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        {/* Completed Plans Tab - Show only completed plans */}
        <TabsContent value="completed-plans" className="space-y-4">
          <div className="mb-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <Trophy className="h-8 w-8 text-yellow-500" />
                <div>
                  <h2 className="text-2xl font-bold text-white">Completed Action Plans</h2>
                  <p className="text-gray-400">Your successful income generation achievements</p>
                </div>
              </div>
              {actionPlans.filter(p => p.status === 'completed').length > 0 && (
                <Card className="bg-slate-800 border-green-500/30">
                  <CardContent className="p-4">
                    <div className="text-center">
                      <p className="text-3xl font-bold text-green-400">
                        {actionPlans.filter(p => p.status === 'completed').length}
                      </p>
                      <p className="text-sm text-green-300">Plans Completed</p>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>

          {actionPlans.filter(p => p.status === 'completed').length === 0 ? (
            <Card className="bg-slate-800 border-slate-700">
              <CardContent className="text-center py-12">
                <Trophy className="h-16 w-16 mx-auto text-gray-600 mb-4" />
                <p className="text-gray-300 mb-2 text-lg">No completed plans yet</p>
                <p className="text-sm text-gray-500">Complete your first action plan to see it here!</p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-6">
              {/* Success Summary Card */}
              <Card className="bg-slate-800 border-cyan-500/30">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-white">
                    <CheckCircle className="h-6 w-6 text-cyan-400" />
                    Success Summary
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="text-center">
                      <p className="text-sm text-gray-400">Total Completed</p>
                      <p className="text-2xl font-bold text-green-400">
                        {actionPlans.filter(p => p.status === 'completed').length}
                      </p>
                    </div>
                    <div className="text-center">
                      <p className="text-sm text-gray-400">Files Generated</p>
                      <p className="text-2xl font-bold text-cyan-400">
                        {actionPlans.filter(p => p.status === 'completed')
                          .reduce((total, plan) => total + (plan.results?.files_created?.length || 0), 0)}
                      </p>
                    </div>
                    <div className="text-center">
                      <p className="text-sm text-gray-400">Success Rate</p>
                      <p className="text-2xl font-bold text-purple-400">
                        {((actionPlans.filter(p => p.status === 'completed').length /
                          Math.max(actionPlans.length, 1)) * 100).toFixed(0)}%
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Completed Plans List */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {actionPlans.filter(p => p.status === 'completed').map((plan, index) => (
                  <Card key={index} className="bg-slate-800 border-green-500/30 hover:border-green-400/50 transition-all">
                    <CardHeader className="bg-slate-900/50">
                      <div className="flex justify-between items-start">
                        <div>
                          <CardTitle className="flex items-center gap-2 text-white">
                            <CheckCircle className="h-5 w-5 text-green-400" />
                            {plan.opportunity_title || 'Completed Plan'}
                          </CardTitle>
                          <CardDescription className="text-gray-400">
                            Completed: {plan.completed_at ?
                              new Date(plan.completed_at).toLocaleDateString() :
                              'Recently'}
                          </CardDescription>
                        </div>
                        <Badge className="bg-green-600/20 text-green-400 border-green-500/50">
                          <CheckCircle className="h-3 w-3 mr-1" />
                          Complete
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent className="pt-4">
                      {/* Results Summary */}
                      {plan.results && Object.keys(plan.results).length > 0 && (
                        <div className="space-y-3">
                          {/* Files Created */}
                          {plan.results.files_created && plan.results.files_created.length > 0 && (
                            <div className="bg-slate-900/50 rounded-lg p-3 border border-cyan-500/20">
                              <h5 className="text-sm font-semibold text-cyan-400 mb-2 flex items-center gap-1">
                                <FileText className="h-4 w-4" />
                                Generated Files ({plan.results.files_created.length})
                              </h5>
                              <div className="space-y-1">
                                {plan.results.files_created.slice(0, 3).map((file: string | any, idx: number) => {
                                  const filepath = typeof file === 'string' ? file : String(file);
                                  const filename = filepath.split('/').pop() || filepath;
                                  return (
                                    <div key={idx} className="flex items-center justify-between">
                                      <span className="text-sm text-gray-300 truncate">📄 {filename}</span>
                                      <Button
                                        size="sm"
                                        variant="ghost"
                                        className="text-xs h-6 px-2"
                                        onClick={() => {
                                          const cleanFilename = filepath.startsWith('income_builder_outputs/')
                                            ? filepath.replace('income_builder_outputs/', '')
                                            : filepath;
                                          setViewingFile(cleanFilename);
                                        }}
                                      >
                                        <Eye className="h-3 w-3" />
                                      </Button>
                                    </div>
                                  );
                                })}
                                {plan.results.files_created.length > 3 && (
                                  <p className="text-xs text-gray-500">
                                    +{plan.results.files_created.length - 3} more files
                                  </p>
                                )}
                              </div>
                            </div>
                          )}

                          {/* ML Score */}
                          {plan.results.ml_score && (
                            <div className="bg-slate-900/50 rounded-lg p-3 border border-purple-500/20">
                              <h5 className="text-sm font-semibold text-purple-400 mb-1">
                                🤖 AI Success Score
                              </h5>
                              <div className="flex items-center gap-2">
                                <Progress
                                  value={plan.results.ml_score * 100}
                                  className="h-2 flex-1 bg-slate-700"
                                />
                                <span className="text-sm font-bold text-purple-400">
                                  {(plan.results.ml_score * 100).toFixed(0)}%
                                </span>
                              </div>
                            </div>
                          )}

                          {/* Action Buttons */}
                          <div className="flex gap-2 pt-2">
                            <Button
                              size="sm"
                              variant="outline"
                              className="flex-1"
                              onClick={() => {
                                // Expand to show full details
                                const updatedPlans = actionPlans.map((p, i) =>
                                  p === plan ? { ...p, expanded: !p.expanded } : p
                                );
                                setActionPlans(updatedPlans);
                                localStorage.setItem('incomeBuilderActionPlans', JSON.stringify(updatedPlans));
                              }}
                            >
                              {plan.expanded ? 'Hide' : 'View'} Details
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              className="flex-1"
                              onClick={() => {
                                // Download results
                                let content = `Income Builder - Completed Action Plan\n`;
                                content += `========================================\n\n`;
                                content += `Opportunity: ${plan.opportunity_title}\n`;
                                content += `Completed: ${new Date(plan.completed_at || Date.now()).toLocaleString()}\n\n`;

                                if (plan.results.files_created) {
                                  content += `Generated Files:\n`;
                                  plan.results.files_created.forEach((file: string) => {
                                    content += `  ✓ ${file}\n`;
                                  });
                                  content += `\n`;
                                }

                                if (plan.results.ml_score) {
                                  content += `AI Success Score: ${(plan.results.ml_score * 100).toFixed(1)}%\n\n`;
                                }

                                content += `Full Results:\n`;
                                content += JSON.stringify(plan.results, null, 2);

                                const blob = new Blob([content], { type: 'text/plain' });
                                const url = URL.createObjectURL(blob);
                                const a = document.createElement('a');
                                a.href = url;
                                a.download = `${plan.opportunity_title.replace(/\s+/g, '_')}_completed.txt`;
                                a.click();
                              }}
                            >
                              <Download className="h-3 w-3 mr-1" />
                              Export
                            </Button>
                          </div>
                        </div>
                      )}

                      {/* Expanded Details */}
                      {plan.expanded && (
                        <div className="mt-4 pt-4 border-t space-y-3">
                          {plan.steps && (
                            <div>
                              <h5 className="text-sm font-semibold mb-2">Completed Steps:</h5>
                              <ol className="list-decimal list-inside space-y-1">
                                {plan.steps.map((step: string, idx: number) => (
                                  <li key={idx} className="text-sm text-green-600">
                                    <CheckCircle className="inline-block ml-1 h-3 w-3" />
                                    <span className="ml-1 text-gray-700">{step}</span>
                                  </li>
                                ))}
                              </ol>
                            </div>
                          )}

                          {plan.execution_logs && plan.execution_logs.length > 0 && (
                            <div>
                              <h5 className="text-sm font-semibold mb-2">Execution History:</h5>
                              <div className="bg-gray-50 rounded p-2 max-h-32 overflow-y-auto">
                                {plan.execution_logs.map((log: any, idx: number) => (
                                  <div key={idx} className="text-xs">
                                    <span className="text-gray-500">
                                      {new Date(log.timestamp).toLocaleTimeString()}
                                    </span>
                                    <span className={`ml-2 ${
                                      log.level === 'success' ? 'text-green-600' : 'text-gray-600'
                                    }`}>
                                      {log.message}
                                    </span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </TabsContent>

        {/* Quick Start Tab */}
        <TabsContent value="quick-start" className="space-y-4">
          <Alert className="border-cyan-500/30 bg-slate-800">
            <Rocket className="h-4 w-4 text-cyan-400" />
            <AlertDescription className="text-gray-300">
              <strong className="text-white">Your Quick Start Path to $1000/month:</strong>
              <ol className="mt-2 space-y-1 list-decimal list-inside text-gray-400">
                <li>Start with Content Writing (1-3 days to first income)</li>
                <li>Add Social Media Management (Week 1)</li>
                <li>Launch Digital Templates (Week 2)</li>
                <li>Scale with AI Automation (Month 1)</li>
              </ol>
            </AlertDescription>
          </Alert>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">Week 1 Goals</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  <li className="flex items-center gap-2 text-gray-300">
                    <Target className="h-4 w-4 text-cyan-400" />
                    Create profiles on 3 platforms
                  </li>
                  <li className="flex items-center gap-2 text-gray-300">
                    <Target className="h-4 w-4 text-cyan-400" />
                    Complete 5 sample projects
                  </li>
                  <li className="flex items-center gap-2 text-gray-300">
                    <Target className="h-4 w-4 text-cyan-400" />
                    Apply to 50 opportunities
                  </li>
                  <li className="flex items-center gap-2 text-gray-300">
                    <Target className="h-4 w-4 text-cyan-400" />
                    Earn first $100
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">Month 1 Targets</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  <li className="flex items-center gap-2 text-gray-300">
                    <TrendingUp className="h-4 w-4 text-green-400" />
                    3 active income streams
                  </li>
                  <li className="flex items-center gap-2 text-gray-300">
                    <TrendingUp className="h-4 w-4 text-green-400" />
                    $500+ monthly revenue
                  </li>
                  <li className="flex items-center gap-2 text-gray-300">
                    <TrendingUp className="h-4 w-4 text-green-400" />
                    5+ positive reviews
                  </li>
                  <li className="flex items-center gap-2 text-gray-300">
                    <TrendingUp className="h-4 w-4 text-green-400" />
                    2 recurring clients
                  </li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Automation Tab */}
        <TabsContent value="automation" className="space-y-4">
          <Alert className="border-purple-500/30 bg-slate-800">
            <Zap className="h-4 w-4 text-purple-400" />
            <AlertDescription className="text-gray-300">
              <strong className="text-white">Automated Income Potential: $200-950/day</strong>
              <p className="mt-1 text-gray-400">Set up once, earn continuously with AI automation</p>
            </AlertDescription>
          </Alert>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card className="bg-slate-800 border-slate-700 hover:border-cyan-500/30 transition-all">
              <CardHeader>
                <CardTitle className="text-white">Blog Automation</CardTitle>
                <CardDescription className="text-gray-400">3 posts/day across platforms</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <p className="text-2xl font-bold text-green-400">$50-200/day</p>
                  <p className="text-sm text-gray-500">AdSense + Affiliates + Sponsored</p>
                  <Button className="w-full bg-slate-700 hover:bg-slate-600 border-cyan-500/30" variant="outline">
                    Setup Automation
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-slate-800 border-slate-700 hover:border-cyan-500/30 transition-all">
              <CardHeader>
                <CardTitle className="text-white">Social Media Automation</CardTitle>
                <CardDescription className="text-gray-400">10 posts/day automated</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <p className="text-2xl font-bold text-cyan-400">$30-150/day</p>
                  <p className="text-sm text-gray-500">Sponsored + Affiliate Marketing</p>
                  <Button className="w-full bg-slate-700 hover:bg-slate-600 border-cyan-500/30" variant="outline">
                    Setup Automation
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-slate-800 border-slate-700 hover:border-purple-500/30 transition-all">
              <CardHeader>
                <CardTitle className="text-white">Video Scripts</CardTitle>
                <CardDescription className="text-gray-400">5 scripts/day for creators</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <p className="text-2xl font-bold text-purple-400">$100-500/day</p>
                  <p className="text-sm text-gray-500">Direct Sales + Subscriptions</p>
                  <Button className="w-full bg-slate-700 hover:bg-slate-600 border-purple-500/30" variant="outline">
                    Setup Automation
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-slate-800 border-slate-700 hover:border-indigo-500/30 transition-all">
              <CardHeader>
                <CardTitle className="text-white">Digital Templates</CardTitle>
                <CardDescription className="text-gray-400">10 new templates/week</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <p className="text-2xl font-bold text-indigo-400">$20-100/day</p>
                  <p className="text-sm text-gray-500">Etsy + Gumroad + Creative Market</p>
                  <Button className="w-full bg-slate-700 hover:bg-slate-600 border-indigo-500/30" variant="outline">
                    Setup Automation
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* File Viewer Modal */}
      {viewingFile && (
        <FileViewer
          filename={viewingFile}
          onClose={() => setViewingFile(null)}
        />
      )}
    </div>
  );
}