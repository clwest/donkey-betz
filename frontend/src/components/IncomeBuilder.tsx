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
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    fetchOpportunities();
    fetchRevenueData();
    // Load saved action plans from localStorage
    const savedPlans = localStorage.getItem('incomeBuilderActionPlans');
    if (savedPlans) {
      try {
        setActionPlans(JSON.parse(savedPlans));
      } catch (e) {
        console.error('Error loading saved action plans:', e);
      }
    }

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
            // Update local plans with backend status
            const updatedPlans = actionPlans.map(localPlan => {
              const backendPlan = data.plans.find((bp: any) => bp.id === localPlan.backend_id);
              if (backendPlan) {
                console.log(`📋 Backend plan for ${localPlan.backend_id}:`, backendPlan);
                console.log('📁 Results:', backendPlan.results);

                if (backendPlan.status === 'completed' && backendPlan.results) {
                  console.log('✅ Plan completed with results:', {
                    files: backendPlan.results.files_created,
                    status: backendPlan.results.status,
                    message: backendPlan.results.message
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
          }
        } catch (error) {
          console.error('Error polling plan status:', error);
        }
      }
    }, 5000); // Poll every 5 seconds

    return () => clearInterval(pollInterval);
  }, [actionPlans]);

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
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="opportunities">Opportunities</TabsTrigger>
          <TabsTrigger value="action-plans">My Action Plans</TabsTrigger>
          <TabsTrigger value="quick-start">Quick Start</TabsTrigger>
          <TabsTrigger value="automation">Automation</TabsTrigger>
        </TabsList>

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

        {/* Action Plans Tab */}
        <TabsContent value="action-plans" className="space-y-4">
          {actionPlans.length === 0 ? (
            <Card>
              <CardContent className="text-center py-8">
                <p className="text-gray-500 mb-4">No action plans created yet.</p>
                <p className="text-sm text-gray-400">Select an opportunity and click "Get Action Plan" to create your first plan.</p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {actionPlans.map((plan, index) => (
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
                                {plan.results.files_created.map((file: string, idx: number) => {
                                  const filename = file.split('/').pop() || file;
                                  return (
                                    <div key={idx} className="flex items-center justify-between">
                                      <span className="text-sm text-gray-700">{filename}</span>
                                      <Button
                                        size="sm"
                                        variant="outline"
                                        className="text-xs gap-1"
                                        onClick={() => setViewingFile(filename)}
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

        {/* Quick Start Tab */}
        <TabsContent value="quick-start" className="space-y-4">
          <Alert className="border-green-200 bg-green-50">
            <Rocket className="h-4 w-4" />
            <AlertDescription>
              <strong>Your Quick Start Path to $1000/month:</strong>
              <ol className="mt-2 space-y-1 list-decimal list-inside">
                <li>Start with Content Writing (1-3 days to first income)</li>
                <li>Add Social Media Management (Week 1)</li>
                <li>Launch Digital Templates (Week 2)</li>
                <li>Scale with AI Automation (Month 1)</li>
              </ol>
            </AlertDescription>
          </Alert>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Week 1 Goals</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  <li className="flex items-center gap-2">
                    <Target className="h-4 w-4 text-blue-600" />
                    Create profiles on 3 platforms
                  </li>
                  <li className="flex items-center gap-2">
                    <Target className="h-4 w-4 text-blue-600" />
                    Complete 5 sample projects
                  </li>
                  <li className="flex items-center gap-2">
                    <Target className="h-4 w-4 text-blue-600" />
                    Apply to 50 opportunities
                  </li>
                  <li className="flex items-center gap-2">
                    <Target className="h-4 w-4 text-blue-600" />
                    Earn first $100
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Month 1 Targets</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  <li className="flex items-center gap-2">
                    <TrendingUp className="h-4 w-4 text-green-600" />
                    3 active income streams
                  </li>
                  <li className="flex items-center gap-2">
                    <TrendingUp className="h-4 w-4 text-green-600" />
                    $500+ monthly revenue
                  </li>
                  <li className="flex items-center gap-2">
                    <TrendingUp className="h-4 w-4 text-green-600" />
                    5+ positive reviews
                  </li>
                  <li className="flex items-center gap-2">
                    <TrendingUp className="h-4 w-4 text-green-600" />
                    2 recurring clients
                  </li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Automation Tab */}
        <TabsContent value="automation" className="space-y-4">
          <Alert className="border-purple-200 bg-purple-50">
            <Zap className="h-4 w-4" />
            <AlertDescription>
              <strong>Automated Income Potential: $200-950/day</strong>
              <p className="mt-1">Set up once, earn continuously with AI automation</p>
            </AlertDescription>
          </Alert>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Blog Automation</CardTitle>
                <CardDescription>3 posts/day across platforms</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <p className="text-2xl font-bold text-green-600">$50-200/day</p>
                  <p className="text-sm text-gray-600">AdSense + Affiliates + Sponsored</p>
                  <Button className="w-full" variant="outline">Setup Automation</Button>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Social Media Automation</CardTitle>
                <CardDescription>10 posts/day automated</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <p className="text-2xl font-bold text-blue-600">$30-150/day</p>
                  <p className="text-sm text-gray-600">Sponsored + Affiliate Marketing</p>
                  <Button className="w-full" variant="outline">Setup Automation</Button>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Video Scripts</CardTitle>
                <CardDescription>5 scripts/day for creators</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <p className="text-2xl font-bold text-purple-600">$100-500/day</p>
                  <p className="text-sm text-gray-600">Direct Sales + Subscriptions</p>
                  <Button className="w-full" variant="outline">Setup Automation</Button>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Digital Templates</CardTitle>
                <CardDescription>10 new templates/week</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <p className="text-2xl font-bold text-indigo-600">$20-100/day</p>
                  <p className="text-sm text-gray-600">Etsy + Gumroad + Creative Market</p>
                  <Button className="w-full" variant="outline">Setup Automation</Button>
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