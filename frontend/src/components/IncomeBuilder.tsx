import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
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
  FileText,
  FileSpreadsheet,
  FileJson,
  File,
  Users
} from 'lucide-react';

// Use API configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

// Import unified connector
import { unifiedConnector } from '../services/UnifiedPlatformConnector';

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
  const [automationWorkflows, setAutomationWorkflows] = useState<any[]>([]);
  const [settingUpAutomation, setSettingUpAutomation] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    console.log('🚀 IncomeBuilder component mounted, fetching data...');

    fetchOpportunities();
    fetchRevenueData();
    loadActionPlansFromBackend();
    fetchAutomationWorkflows();

    // Connect to Unified Platform for all WebSocket communication
    connectToPlatform();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  // Debug: Monitor opportunities state changes
  useEffect(() => {
    console.log('📋 Opportunities state updated:', opportunities.length, 'items', opportunities);
  }, [opportunities]);

  // Debug: Monitor revenue data state changes
  useEffect(() => {
    console.log('💳 Revenue data state updated:', revenueData);
  }, [revenueData]);

  // Direct WebSocket connection removed - now using UnifiedPlatformConnector
  // This prevents duplicate connections and consolidates all WebSocket communication

  const connectToPlatform = async () => {
    try {
      console.log('🔌 Income Builder connecting to Unified Platform...');

      const connected = await unifiedConnector.connect('income_builder');

      if (connected) {
        console.log('✅ Income Builder connected to platform');
        setWsConnected(true);
        setLoading(false); // Stop loading when connected

        // Set up platform message handlers
        unifiedConnector.connectIncomeBuilder((data) => {
          console.log('📨 Platform data received:', data);
          handlePlatformMessage(data);
        });

        // Request initial opportunities through platform
        unifiedConnector.send({
          type: 'get_opportunities',
          source: 'income_builder'
        });

        // Also trigger analyze_opportunities with a default profile
        const defaultProfile = {
          id: 'user_' + Date.now(),
          skills: ['python', 'ai', 'automation', 'content writing', 'data analysis'],
          skill_level: 'intermediate',
          current_balance: 0,
          available_hours: 20
        };
        unifiedConnector.send({
          type: 'analyze_opportunities',
          profile: defaultProfile,
          source: 'income_builder'
        });
        console.log('📤 Sent analyze_opportunities request with profile');
      }
    } catch (error) {
      console.error('Failed to connect to platform:', error);
      setWsConnected(false);
    }
  };

  const handlePlatformMessage = (data: any) => {
    console.log('🎯 Income Builder processing platform message:', data);

    // Handle opportunities from unified platform
    if (data.top_opportunities && data.top_opportunities.length > 0) {
      console.log(`✅ Received ${data.top_opportunities.length} unified opportunities`);

      // Merge with existing opportunities (avoiding duplicates)
      setOpportunities(prevOpps => {
        const existingIds = new Set(prevOpps.map(opp => opp.id));
        const newOpps = data.top_opportunities.filter((opp: any) => !existingIds.has(opp.id));

        if (newOpps.length > 0) {
          console.log(`🔄 Adding ${newOpps.length} new opportunities from platform`);
          return [...prevOpps, ...newOpps];
        }
        return prevOpps;
      });
    }

    // Handle revenue data from platform
    if (data.revenue || data.metrics) {
      const platformRevenue = data.revenue || data.metrics;
      setRevenueData(prev => ({
        ...prev,
        ...platformRevenue
      }));
    }
  };

  const handleWebSocketMessage = (data: any) => {
    console.log('📨 Income Builder received WS message:', data);

    if (data.type === 'opportunities_analysis') {
      // Handle the opportunities_analysis message type from backend
      if (data.top_opportunities && data.top_opportunities.length > 0) {
        console.log(`✅ Received ${data.top_opportunities.length} opportunities from analysis`);
        setOpportunities(data.top_opportunities);
        setLoading(false);

        // Log additional data
        if (data.source) {
          console.log(`📋 Data source: ${data.source}, Real data: ${data.is_real}, Job count: ${data.job_count || 0}`);
        }
        if (data.earnings_projection) {
          console.log('💰 Earnings projection:', data.earnings_projection);
        }
      } else {
        console.log('⚠️ Received empty opportunities in analysis');
      }
    } else if (data.type === 'opportunities_update' && data.opportunities) {
      // Only update if we're getting more opportunities or if we have none
      setOpportunities(prev => {
        if (prev.length === 0 || data.opportunities.length >= prev.length) {
          console.log(`✅ Updating opportunities: ${prev.length} → ${data.opportunities.length}`);
          return data.opportunities;
        } else {
          console.log(`⚠️ Skipping WebSocket update: current ${prev.length} > incoming ${data.opportunities.length}`);
          return prev;
        }
      });
      setLoading(false);

      // Log source for debugging
      if (data.source) {
        console.log(`📋 Opportunities source: ${data.source} (${data.opportunities.length} items)`);
        if (data.reddit_count) {
          console.log(`🔥 Enhanced with ${data.reddit_count} Reddit opportunities`);
        }
      }
    } else if (data.type === 'reddit_opportunities' && data.opportunities) {
      // Legacy handler - replace non-reddit opportunities and add reddit ones
      setOpportunities(prev => [...data.opportunities, ...prev.filter(o => !o.id.startsWith('reddit_'))]);
      setLoading(false);
    } else if (data.type === 'revenue_update' && data.revenue) {
      // Update revenue data
      setRevenueData(data.revenue);
    } else if (data.type === 'action_plan_update') {
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
    } else if (data.type === 'automation_update' && data.automations) {
      // Update active automations
      setActiveAutomations(data.automations);
    } else if (data.type === 'advisor_review_complete') {
      // Handle advisor review completion
      console.log('🎓 Advisor review received:', data.advisor_review);
      console.log('📋 Current actionPlans:', actionPlans.length, 'plans');
      console.log('🔍 Looking for plan_id:', data.plan_id);

      // First try to get plans from localStorage if current state is empty
      let plansToUpdate = actionPlans;
      if (actionPlans.length === 0) {
        const stored = localStorage.getItem('incomeBuilderActionPlans');
        if (stored) {
          plansToUpdate = JSON.parse(stored);
          console.log('📂 Retrieved', plansToUpdate.length, 'plans from localStorage');
        }
      }

      // Update action plan with advisor review
      const updatedPlans = plansToUpdate.map(plan =>
        (plan.backend_id === data.plan_id || plan.id === data.plan_id)
          ? {
              ...plan,
              status: 'reviewed',
              advisor_review: data.advisor_review,
              team: data.team,
              execution_stages: data.stages
            }
          : plan
      );

      // Always save even if we didn't find the exact plan
      if (updatedPlans.length > 0) {
        savePlans(updatedPlans);
      } else {
        console.warn('⚠️ No plans to update with advisor review');
      }

      // Show notification about advisor review
      if (data.advisor_review) {
        console.log(`✅ Advisor ${data.advisor_review.advisor} reviewed plan with ${data.advisor_review.success_probability || 0.75}% success probability`);
      }
    } else if (data.type === 'advisor_recommendation') {
      // Handle advisor recommendation for opportunity
      console.log('💡 Advisor recommendation:', data.recommendation);

      // Store recommendation for display
      setSelectedOpportunity(prev => {
        if (prev && prev.title === data.opportunity) {
          return {
            ...prev,
            advisor_recommendation: data.recommendation
          };
        }
        return prev;
      });
    } else if (data.type === 'team_status') {
      // Handle team status update
      console.log('👥 Team status:', data.team);

      // Update action plan with team status
      setActionPlans(prev => prev.map(plan => {
        if (plan.team && plan.team.id === data.team_id) {
          return {
            ...plan,
            team: {
              ...plan.team,
              ...data.team
            }
          };
        }
        return plan;
      }));
    }
  };

  // Poll for action plan status updates
  useEffect(() => {
    const pollInterval = setInterval(async () => {
      // Check if any plans are in progress
      const inProgressPlans = actionPlans.filter(p => p.status === 'in_progress' && p.backend_id);

      if (inProgressPlans.length > 0) {
        try {
          const response = await fetch(`${API_BASE_URL}/v1/intelligence/income-builder/execute/`);
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

            savePlans(updatedPlans);

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
    }, 30000); // Poll every 30 seconds to avoid rate limiting

    return () => clearInterval(pollInterval);
  }, [actionPlans]);

  const analyzePlanForAutomation = async (plan: any) => {
    try {
      const planContent = await fetch(`${API_BASE_URL}${plan.file_path}`).then(r => r.text());

      const response = await fetch(`${API_BASE_URL}/v1/intelligence/income-builder/analyze-plan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plan_content: planContent })
      });

      const analysis = await response.json();

      // Update plan with analysis
      const updatedPlans = actionPlans.map(p =>
        p.id === plan.id ? { ...p, automation_analysis: analysis } : p
      );
      savePlans(updatedPlans);

    } catch (error) {
      console.error('Error analyzing plan:', error);
    }
  };

  const executePlanAutomation = async (plan: any) => {
    try {
      const response = await fetch(`${API_BASE_URL}/v1/intelligence/income-builder/process-plan`, {
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
        const response = await fetch(`${API_BASE_URL}/v1/intelligence/income-builder/execution-status/${executionId}`);
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
      // Fetch REAL opportunities from the new endpoint
      console.log('🔍 Fetching REAL opportunities from:', `${API_BASE_URL}/api/v1/intelligence/real-income-builder/`);
      const response = await fetch(`${API_BASE_URL}/api/v1/intelligence/real-income-builder/`);
      const data = await response.json();
      console.log('📊 REAL opportunities data received:', data);
      if (data.success) {
        console.log('✅ Setting REAL opportunities:', data.opportunities);
        setOpportunities(data.opportunities);

        // Also update revenue data if provided
        if (data.revenue) {
          console.log('💰 Updating revenue data from opportunities');
          setRevenueData(data.revenue);
        }
      }
    } catch (error) {
      console.error('❌ Error fetching real opportunities:', error);
      // Fallback to old endpoint if new one fails
      try {
        console.log('🔄 Trying fallback endpoint...');
        const fallbackResponse = await fetch(`${API_BASE_URL}/api/v1/intelligence/income-builder/`);
        const fallbackData = await fallbackResponse.json();
        if (fallbackData.success) {
          setOpportunities(fallbackData.opportunities);
        }
      } catch (fallbackError) {
        console.error('❌ Fallback also failed:', fallbackError);
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchRevenueData = async () => {
    try {
      console.log('💰 Fetching revenue data from:', `${API_BASE_URL}/v1/monetization/opportunities/`);
      const response = await fetch(`${API_BASE_URL}/v1/monetization/opportunities/`);
      const data = await response.json();
      console.log('💵 Revenue data received:', data);
      if (data.success) {
        console.log('✅ Setting revenue dashboard:', data.dashboard);
        setRevenueData(data.dashboard);
      }
    } catch (error) {
      console.error('❌ Error fetching revenue data:', error);
    }
  };

  const fetchAutomationWorkflows = async () => {
    try {
      console.log('🤖 Fetching automation workflows...');
      const response = await fetch(`${API_BASE_URL}/v1/intelligence/automation/workflows/`);
      const data = await response.json();
      console.log('🔧 Automation workflows received:', data);
      if (data.success) {
        setAutomationWorkflows(data.workflows);
      }
    } catch (error) {
      console.error('❌ Error fetching automation workflows:', error);
    }
  };

  const setupAutomationWorkflow = async (workflowType: string) => {
    try {
      setSettingUpAutomation(workflowType);
      console.log(`🚀 Setting up ${workflowType} automation workflow...`);

      const response = await fetch(`${API_BASE_URL}/v1/intelligence/automation/setup/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ workflow_type: workflowType })
      });

      const result = await response.json();
      console.log('🎯 Automation setup result:', result);

      if (result.success) {
        alert(`✅ ${result.workflow} automation is now set up and ready to generate income!`);

        // Add to active automations
        setActiveAutomations(prev => [...prev, {
          workflow_type: workflowType,
          workflow_name: result.workflow,
          plan_id: result.plan_id,
          setup_result: result.setup_result,
          status: 'setup_complete',
          setup_at: new Date().toISOString()
        }]);

        // Refresh automation workflows to show updated status
        fetchAutomationWorkflows();
      } else {
        alert(`❌ Failed to set up ${workflowType} automation: ${result.error}`);
      }
    } catch (error) {
      console.error('Error setting up automation:', error);
      alert('Error setting up automation. Check console for details.');
    } finally {
      setSettingUpAutomation(null);
    }
  };

  const executeQuickStart = async () => {
    try {
      setSettingUpAutomation('quick_start');
      console.log('🚀 Executing Quick Start setup...');

      const response = await fetch(`${API_BASE_URL}/v1/intelligence/automation/quick-start/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      const result = await response.json();
      console.log('🎯 Quick Start result:', result);

      if (result.success) {
        alert(`🚀 Quick Start launched! Your path to $1000/month is now active with Blog + Social Media automation. Check the "My Action Plans" tab to monitor progress.`);

        // Add all quick start workflows to active automations
        result.workflows_setup.forEach((workflowType: string) => {
          setActiveAutomations(prev => [...prev, {
            workflow_type: workflowType,
            workflow_name: workflowType.replace('_', ' '),
            plan_id: result.plan_id,
            status: 'quick_start_complete',
            setup_at: new Date().toISOString()
          }]);
        });

        // Switch to action plans tab to see the new Quick Start plan
        setActiveTab('action-plans');
      } else {
        alert(`❌ Quick Start failed: ${result.error}`);
      }
    } catch (error) {
      console.error('Error executing Quick Start:', error);
      alert('Error executing Quick Start. Check console for details.');
    } finally {
      setSettingUpAutomation(null);
    }
  };

  const loadActionPlansFromBackend = async () => {
    let plansLoaded = false;

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

          // Save to localStorage as backup
          localStorage.setItem('incomeBuilderActionPlans', JSON.stringify(data.plans));
          plansLoaded = true;
        }
      }
    } catch (error) {
      console.error('Error loading plans from backend:', error);
    }

    // If no backend plans, try localStorage
    if (!plansLoaded) {
      try {
        const localPlans = localStorage.getItem('incomeBuilderActionPlans');
        if (localPlans) {
          const parsedPlans = JSON.parse(localPlans);
          console.log('💾 Loaded', parsedPlans.length, 'plans from localStorage');
          setActionPlans(parsedPlans);

          // Check if we should show completed tab
          const completedCount = parsedPlans.filter((p: any) => p.status === 'completed').length;
          const inProgressCount = parsedPlans.filter((p: any) => p.status === 'in_progress').length;

          if (completedCount > 0 && inProgressCount === 0) {
            setActiveTab('completed-plans');
          }
          plansLoaded = true;
        }
      } catch (error) {
        console.error('Error loading from localStorage:', error);
      }
    }

    // If still no plans, start fresh
    if (!plansLoaded) {
      console.log('📋 No saved plans available, starting with empty state');
      setActionPlans([]);
    }
  };

  // Helper function to save plans to both localStorage and backend
  const savePlans = (plans: any[]) => {
    // Save to localStorage immediately
    localStorage.setItem('incomeBuilderActionPlans', JSON.stringify(plans));
    console.log('💾 Saved', plans.length, 'plans to localStorage');

    // Update state
    setActionPlans(plans);

    // Try to save to backend (async, non-blocking)
    saveActionPlansToBackend(plans);
  };

  const saveActionPlansToBackend = async (plans: any[]) => {
    // Try to save to backend but don't block UI
    console.log('📤 Attempting to save plans to backend...');
    return;
  };

  const saveActionPlansToBackend_disabled = async (plans: any[]) => {
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
        savePlans(updatedPlans);

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
      default: return 'bg-muted/50';
    }
  };

  // Export functions for multiple formats
  const exportAsJSON = (plan: any, type: string = 'full') => {
    const filename = `${plan.opportunity_title.replace(/\s+/g, '_')}_${type}.json`;
    const data = JSON.stringify(plan, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  const exportAsCSV = (plan: any) => {
    let csv = 'Field,Value\n';
    csv += `"Opportunity","${plan.opportunity_title}"\n`;
    csv += `"Status","${plan.status}"\n`;
    csv += `"Progress","${plan.progress}%"\n`;
    csv += `"Created","${new Date(plan.created_at).toLocaleString()}"\n`;

    if (plan.completed_at) {
      csv += `"Completed","${new Date(plan.completed_at).toLocaleString()}"\n`;
    }

    if (plan.steps?.length > 0) {
      csv += `"Total Steps","${plan.steps.length}"\n`;
      plan.steps.forEach((step: any, i: number) => {
        csv += `"Step ${i+1}","${step.description}"\n`;
      });
    }

    if (plan.results?.files_created?.length > 0) {
      csv += `"Files Created","${plan.results.files_created.length}"\n`;
      plan.results.files_created.forEach((file: string, i: number) => {
        csv += `"File ${i+1}","${file}"\n`;
      });
    }

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${plan.opportunity_title.replace(/\s+/g, '_')}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const exportAsMarkdown = (plan: any) => {
    let md = `# ${plan.opportunity_title}\n\n`;
    md += `**Status:** ${plan.status}\n`;
    md += `**Progress:** ${plan.progress}%\n`;
    md += `**Created:** ${new Date(plan.created_at).toLocaleString()}\n`;

    if (plan.completed_at) {
      md += `**Completed:** ${new Date(plan.completed_at).toLocaleString()}\n`;
    }

    md += '\n## Action Steps\n\n';
    if (plan.steps?.length > 0) {
      plan.steps.forEach((step: any, i: number) => {
        md += `${i+1}. ${step.description}\n`;
        if (step.status === 'completed') {
          md += `   - ✅ Completed\n`;
        }
      });
    }

    if (plan.results?.files_created?.length > 0) {
      md += '\n## Generated Files\n\n';
      plan.results.files_created.forEach((file: string) => {
        md += `- ${file}\n`;
      });
    }

    if (plan.timeline) {
      md += `\n## Timeline\n${plan.timeline}\n`;
    }

    if (plan.expected_outcome) {
      md += `\n## Expected Outcome\n${plan.expected_outcome}\n`;
    }

    const blob = new Blob([md], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${plan.opportunity_title.replace(/\s+/g, '_')}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const exportAsPDF = (plan: any) => {
    // Create HTML content for PDF
    const html = `
      <!DOCTYPE html>
      <html>
      <head>
        <title>${plan.opportunity_title}</title>
        <style>
          body { font-family: Arial, sans-serif; padding: 20px; }
          h1 { color: #2563eb; }
          h2 { color: #3b82f6; margin-top: 20px; }
          .meta { color: #666; margin: 10px 0; }
          .step { margin: 10px 0; padding: 10px; background: #f5f5f5; border-radius: 5px; }
          .completed { background: #d1fae5; }
          .file { margin: 5px 0; padding: 5px 10px; background: #e0e7ff; border-radius: 3px; }
        </style>
      </head>
      <body>
        <h1>${plan.opportunity_title}</h1>
        <div class="meta">Status: ${plan.status} | Progress: ${plan.progress}%</div>
        <div class="meta">Created: ${new Date(plan.created_at).toLocaleString()}</div>
        ${plan.completed_at ? `<div class="meta">Completed: ${new Date(plan.completed_at).toLocaleString()}</div>` : ''}

        <h2>Action Steps</h2>
        ${plan.steps?.map((step: any, i: number) => `
          <div class="step ${step.status === 'completed' ? 'completed' : ''}">
            ${i+1}. ${step.description}
            ${step.status === 'completed' ? ' ✓' : ''}
          </div>
        `).join('') || '<p>No steps defined</p>'}

        ${plan.results?.files_created?.length > 0 ? `
          <h2>Generated Files</h2>
          ${plan.results.files_created.map((file: string) => `
            <div class="file">${file}</div>
          `).join('')}
        ` : ''}

        ${plan.timeline ? `<h2>Timeline</h2><p>${plan.timeline}</p>` : ''}
        ${plan.expected_outcome ? `<h2>Expected Outcome</h2><p>${plan.expected_outcome}</p>` : ''}
      </body>
      </html>
    `;

    // Open in new window for printing to PDF
    const printWindow = window.open('', '_blank');
    if (printWindow) {
      printWindow.document.write(html);
      printWindow.document.close();
      printWindow.print();
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
              <Badge className="ml-2 bg-blue-500 text-foreground text-xs">
                {actionPlans.filter(p => p.status === 'in_progress').length}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="completed-plans" className="relative">
            <span className="flex items-center gap-2">
              <Trophy className="h-4 w-4 text-yellow-500" />
              Completed
              {actionPlans.filter(p => p.status === 'completed' || p.status === 'under_review' || p.status === 'reviewed').length > 0 && (
                <Badge className="bg-green-500 text-foreground text-xs">
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
                        <div className="bg-muted/5 rounded-lg p-4 space-y-3">
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

                {selectedOpportunity.resources && selectedOpportunity.resources.length > 0 && (
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
                )}
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Action Plans Tab - Only show non-completed plans */}
        <TabsContent value="action-plans" className="space-y-4">
          {actionPlans.filter(p => p.status !== 'completed').length === 0 ? (
            <Card>
              <CardContent className="text-center py-8">
                <p className="text-muted-foreground mb-4">No active action plans.</p>
                <p className="text-sm text-muted-foreground">Select an opportunity and click "Get Action Plan" to create a new plan.</p>
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
              {actionPlans.filter(p => p.status !== 'completed').map((plan, index) => {
                console.log(`📋 Rendering plan ${index}:`, {
                  title: plan.opportunity_title,
                  status: plan.status,
                  hasAdvisorReview: !!plan.advisor_review,
                  backend_id: plan.backend_id
                });
                return (
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
                      <div className="mt-4 p-3 bg-muted/5 rounded-md">
                        <h4 className="font-semibold text-sm mb-2">Execution Logs:</h4>
                        <div className="space-y-1 max-h-32 overflow-y-auto">
                          {plan.execution_logs.slice(-5).map((log: any, lIndex: number) => (
                            <div key={lIndex} className="text-xs">
                              <span className="text-muted-foreground">{new Date(log.timestamp).toLocaleTimeString()}</span>
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

                    {/* Advisor Review Section */}
                    {plan.advisor_review && (
                      <div className="mt-4 p-4 bg-purple-50 rounded-md border border-purple-200">
                        <h4 className="font-semibold text-sm mb-3 text-purple-800 flex items-center">
                          <Sparkles className="h-4 w-4 mr-2" />
                          Advisor Review by {plan.advisor_review.advisor}
                        </h4>

                        <div className="space-y-3">
                          {/* Success Probability */}
                          {plan.advisor_review.success_probability && (
                            <div className="flex items-center justify-between">
                              <span className="text-sm text-gray-600">Success Probability</span>
                              <Badge variant="secondary" className="bg-green-100">
                                {(plan.advisor_review.success_probability * 100).toFixed(0)}%
                              </Badge>
                            </div>
                          )}

                          {/* Budget Estimate */}
                          {plan.advisor_review.budget_estimate && (
                            <div className="flex items-center justify-between">
                              <span className="text-sm text-gray-600">Budget Required</span>
                              <span className="font-semibold">${plan.advisor_review.budget_estimate.toLocaleString()}</span>
                            </div>
                          )}

                          {/* Timeline Adjustment */}
                          {plan.advisor_review.timeline_adjustment && (
                            <div className="p-2 bg-yellow-50 rounded text-sm">
                              <Clock className="h-3 w-3 inline-block mr-1" />
                              {plan.advisor_review.timeline_adjustment}
                            </div>
                          )}

                          {/* Immediate Actions */}
                          {plan.advisor_review.immediate_actions && plan.advisor_review.immediate_actions.length > 0 && (
                            <div>
                              <h5 className="text-xs font-semibold text-purple-700 mb-1">Immediate Actions:</h5>
                              <ul className="space-y-1">
                                {plan.advisor_review.immediate_actions.slice(0, 3).map((action: string, idx: number) => (
                                  <li key={idx} className="text-xs text-gray-700 flex items-start">
                                    <ArrowRight className="h-3 w-3 mr-1 mt-0.5 text-purple-500" />
                                    {action}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {/* Success Metrics */}
                          {plan.advisor_review.success_metrics && plan.advisor_review.success_metrics.length > 0 && (
                            <div>
                              <h5 className="text-xs font-semibold text-purple-700 mb-1">Success Metrics:</h5>
                              <div className="flex flex-wrap gap-2">
                                {plan.advisor_review.success_metrics.slice(0, 3).map((metric: string, idx: number) => (
                                  <Badge key={idx} variant="outline" className="text-xs">
                                    <Target className="h-3 w-3 mr-1" />
                                    {metric}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Team Formation Section */}
                    {plan.team && (
                      <div className="mt-4 p-4 bg-blue-50 rounded-md border border-blue-200">
                        <h4 className="font-semibold text-sm mb-3 text-blue-800 flex items-center">
                          <Rocket className="h-4 w-4 mr-2" />
                          Execution Team: {plan.team.id}
                        </h4>

                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-gray-600">Lead Agent</span>
                            <Badge variant="default">{plan.team.lead}</Badge>
                          </div>

                          {plan.team.core_agents && plan.team.core_agents.length > 0 && (
                            <div>
                              <span className="text-xs text-gray-600">Core Agents:</span>
                              <div className="flex flex-wrap gap-1 mt-1">
                                {plan.team.core_agents.slice(0, 5).map((agent: string, idx: number) => (
                                  <Badge key={idx} variant="outline" className="text-xs">
                                    {agent}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                          )}

                          {plan.team.phases && (
                            <div className="flex items-center justify-between">
                              <span className="text-sm text-gray-600">Execution Phases</span>
                              <span className="font-semibold">{plan.team.phases} phases</span>
                            </div>
                          )}
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
                                {plan.results.files_created
                                  .flat() // Flatten nested arrays
                                  .filter((file: any) => typeof file === 'string' && file.length > 0)
                                  .map((file: string, idx: number) => {
                                    const filepath = file;
                                    const filename = filepath.split('/').pop() || filepath;

                                    // Extract the actual file path
                                    // Files are stored in subdirectories but the database might not have the full path
                                    let viewPath = filepath;

                                    // Remove the income_builder_outputs prefix if present
                                    if (filepath.startsWith('income_builder_outputs/')) {
                                      viewPath = filepath.replace('income_builder_outputs/', '');
                                    }

                                    // If the path doesn't include a directory, add it based on the plan type
                                    if (!viewPath.includes('/')) {
                                      // Map plan titles to their directory names
                                      if (plan.opportunity_title?.includes('Social Media')) {
                                        viewPath = `AI Social Media Management/${viewPath}`;
                                      } else if (plan.opportunity_title?.includes('Content Writing')) {
                                        viewPath = `AI-Assisted Content Writing/${viewPath}`;
                                      } else if (plan.opportunity_title?.includes('Digital Templates')) {
                                        viewPath = `AI-Generated Digital Templates/${viewPath}`;
                                      } else if (plan.opportunity_title?.includes('Online Tutoring')) {
                                        viewPath = `AI-Enhanced Online Tutoring/${viewPath}`;
                                      }
                                    }

                                    return (
                                      <div key={idx} className="flex items-center justify-between">
                                        <span className="text-sm text-gray-700" title={filepath}>{filename}</span>
                                        <Button
                                          size="sm"
                                          variant="outline"
                                          className="text-xs gap-1"
                                          onClick={() => {
                                            console.log('Viewing file:', viewPath);
                                            setViewingFile(viewPath);
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
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button
                              size="sm"
                              variant="outline"
                              className="mt-3"
                            >
                              <Download className="mr-2 h-4 w-4" />
                              Export Results
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => exportAsPDF(plan)}>
                              <File className="mr-2 h-4 w-4" />
                              Export as PDF
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => exportAsMarkdown(plan)}>
                              <FileText className="mr-2 h-4 w-4" />
                              Export as Markdown
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => exportAsCSV(plan)}>
                              <FileSpreadsheet className="mr-2 h-4 w-4" />
                              Export as CSV
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => exportAsJSON(plan)}>
                              <FileJson className="mr-2 h-4 w-4" />
                              Export as JSON
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
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
                            const response = await fetch(`${API_BASE_URL}/v1/intelligence/income-builder/execute/`, {
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
                              // localStorage.setItem('incomeBuilderActionPlans', JSON.stringify(updatedPlans));

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
                      {/* Request Advisor Review Button - Always show if no review yet */}
                      {!plan.advisor_review && plan.status !== 'in_progress' && (
                        <Button
                          size="sm"
                          variant="default"
                          className="bg-purple-600 hover:bg-purple-700 text-foreground"
                          onClick={async () => {
                            console.log('📚 Requesting advisor review for plan:', plan.opportunity_title);

                            // Prepare plan data
                            const planData = {
                              id: plan.backend_id || `local_${Date.now()}`,
                              opportunity_title: plan.opportunity_title,
                              timeline: plan.timeline || '4 weeks',
                              steps: plan.steps || [],
                              resources: plan.resources || [],
                              status: plan.status || 'created'
                            };

                            console.log('📤 Sending plan for advisor review:', planData);

                            // Try WebSocket first
                            if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
                              wsRef.current.send(JSON.stringify({
                                type: 'request_advisor_review',
                                plan_id: planData.id,
                                plan_data: planData
                              }));

                              // Update UI to show review is pending
                              const updatedPlans = actionPlans.map((p, i) =>
                                i === index ? { ...p, status: 'under_review', advisor_review_pending: true } : p
                              );
                              savePlans(updatedPlans);

                              console.log('✅ Advisor review requested via WebSocket');

                              // Redirect to Neural Orchestra to see the advisor review and team formation
                              setTimeout(() => {
                                window.location.href = '/neural-orchestra?plan=' + (plan.backend_id || plan.id);
                              }, 1000);
                            } else {
                              // Fallback: Try direct API call
                              console.log('⚠️ WebSocket not connected, trying API call...');

                              try {
                                const response = await fetch(`${API_BASE_URL}/v1/intelligence/advisor-review/`, {
                                  method: 'POST',
                                  headers: { 'Content-Type': 'application/json' },
                                  body: JSON.stringify(planData)
                                });

                                if (response.ok) {
                                  const result = await response.json();
                                  console.log('✅ Advisor review received:', result);

                                  // Update plan with review
                                  const updatedPlans = actionPlans.map((p, i) =>
                                    i === index ? {
                                      ...p,
                                      advisor_review: result.advisor_review,
                                      team: result.team,
                                      status: 'reviewed'
                                    } : p
                                  );
                                  savePlans(updatedPlans);

                                  // Redirect to Neural Orchestra to see the advisor review and team formation
                                  setTimeout(() => {
                                    window.location.href = '/neural-orchestra?plan=' + (plan.backend_id || plan.id);
                                  }, 1000);
                                } else {
                                  alert('Failed to get advisor review. Please try again.');
                                }
                              } catch (error) {
                                console.error('Error getting advisor review:', error);
                                alert('Error connecting to advisor system. Please check console.');
                              }
                            }
                          }}
                        >
                          <Sparkles className="mr-2 h-4 w-4" />
                          Get Advisor Review
                        </Button>
                      )}

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
                          onClick={async () => {
                            if (confirm('Are you sure you want to delete this action plan?')) {
                              const updatedPlans = actionPlans.filter((_, i) => i !== index);

                              if (updatedPlans.length > 0) {
                                savePlans(updatedPlans);
                              } else {
                                // Clear everything if no plans left
                                setActionPlans([]);
                                localStorage.removeItem('incomeBuilderActionPlans');
                              }

                              console.log(`🗑️ Deleted action plan. Remaining: ${updatedPlans.length}`);
                            }
                          }}
                        >
                          Delete Plan
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              );})}
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
                  <h2 className="text-2xl font-bold text-foreground">Completed Action Plans</h2>
                  <p className="text-muted-foreground">Your successful income generation achievements</p>
                </div>
              </div>
              {actionPlans.filter(p => p.status === 'completed' || p.status === 'under_review' || p.status === 'reviewed').length > 0 && (
                <Card className="bg-slate-800 border-green-500/30">
                  <CardContent className="p-4">
                    <div className="text-center">
                      <p className="text-3xl font-bold text-green-500">
                        {actionPlans.filter(p => p.status === 'completed' || p.status === 'under_review' || p.status === 'reviewed').length}
                      </p>
                      <p className="text-sm text-green-300">Plans Completed</p>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>

          {actionPlans.filter(p => p.status === 'completed' || p.status === 'under_review' || p.status === 'reviewed').length === 0 ? (
            <Card className="bg-slate-800 border-slate-700">
              <CardContent className="text-center py-12">
                <Trophy className="h-16 w-16 mx-auto text-gray-600 mb-4" />
                <p className="text-muted-foreground mb-2 text-lg">No completed plans yet</p>
                <p className="text-sm text-muted-foreground">Complete your first action plan to see it here!</p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-6">
              {/* Success Summary Card */}
              <Card className="bg-slate-800 border-cyan-500/30">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-foreground">
                    <CheckCircle className="h-6 w-6 text-cyan-400" />
                    Success Summary
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="text-center">
                      <p className="text-sm text-muted-foreground">Total Completed</p>
                      <p className="text-2xl font-bold text-green-500">
                        {actionPlans.filter(p => p.status === 'completed' || p.status === 'under_review' || p.status === 'reviewed').length}
                      </p>
                    </div>
                    <div className="text-center">
                      <p className="text-sm text-muted-foreground">Files Generated</p>
                      <p className="text-2xl font-bold text-cyan-400">
                        {actionPlans.filter(p => p.status === 'completed' || p.status === 'under_review' || p.status === 'reviewed')
                          .reduce((total, plan) => total + (plan.results?.files_created?.length || 0), 0)}
                      </p>
                    </div>
                    <div className="text-center">
                      <p className="text-sm text-muted-foreground">Success Rate</p>
                      <p className="text-2xl font-bold text-purple-400">
                        {((actionPlans.filter(p => p.status === 'completed' || p.status === 'under_review' || p.status === 'reviewed').length /
                          Math.max(actionPlans.length, 1)) * 100).toFixed(0)}%
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Completed Plans List */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {actionPlans.filter(p => p.status === 'completed' || p.status === 'under_review' || p.status === 'reviewed').map((plan, index) => (
                  <Card key={index} className="bg-slate-800 border-green-500/30 hover:border-green-400/50 transition-all">
                    <CardHeader className="bg-slate-900/50">
                      <div className="flex justify-between items-start">
                        <div>
                          <CardTitle className="flex items-center gap-2 text-foreground">
                            <CheckCircle className="h-5 w-5 text-green-500" />
                            {plan.opportunity_title || 'Completed Plan'}
                          </CardTitle>
                          <CardDescription className="text-muted-foreground">
                            Completed: {plan.completed_at ?
                              new Date(plan.completed_at).toLocaleDateString() :
                              'Recently'}
                          </CardDescription>
                        </div>
                        <Badge className={
                          plan.status === 'under_review' ? "bg-purple-600/20 text-purple-400 border-purple-500/50" :
                          plan.status === 'reviewed' ? "bg-indigo-600/20 text-indigo-400 border-indigo-500/50" :
                          "bg-green-600/20 text-green-500 border-green-500/50"
                        }>
                          {plan.status === 'under_review' ? (
                            <>
                              <Sparkles className="h-3 w-3 mr-1" />
                              Under Review
                            </>
                          ) : plan.status === 'reviewed' ? (
                            <>
                              <Users className="h-3 w-3 mr-1" />
                              Reviewed
                            </>
                          ) : (
                            <>
                              <CheckCircle className="h-3 w-3 mr-1" />
                              Complete
                            </>
                          )}
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
                                {plan.results.files_created
                                  .flat() // Flatten nested arrays
                                  .filter((file: any) => typeof file === 'string' && file.length > 0)
                                  .slice(0, 5)
                                  .map((file: string, idx: number) => {
                                    const filepath = file;
                                    const filename = filepath.split('/').pop() || filepath;

                                    // Extract the actual file path
                                    // Files are stored in subdirectories but the database might not have the full path
                                    let viewPath = filepath;

                                    // Remove the income_builder_outputs prefix if present
                                    if (filepath.startsWith('income_builder_outputs/')) {
                                      viewPath = filepath.replace('income_builder_outputs/', '');
                                    }

                                    // If the path doesn't include a directory, add it based on the plan type
                                    if (!viewPath.includes('/')) {
                                      // Map plan titles to their directory names
                                      if (plan.opportunity_title?.includes('Social Media')) {
                                        viewPath = `AI Social Media Management/${viewPath}`;
                                      } else if (plan.opportunity_title?.includes('Content Writing')) {
                                        viewPath = `AI-Assisted Content Writing/${viewPath}`;
                                      } else if (plan.opportunity_title?.includes('Digital Templates')) {
                                        viewPath = `AI-Generated Digital Templates/${viewPath}`;
                                      } else if (plan.opportunity_title?.includes('Online Tutoring')) {
                                        viewPath = `AI-Enhanced Online Tutoring/${viewPath}`;
                                      }
                                    }

                                    return (
                                      <div key={idx} className="flex items-center justify-between">
                                        <span className="text-sm text-muted-foreground truncate" title={filepath}>
                                          📄 {filename}
                                        </span>
                                        <Button
                                          size="sm"
                                          variant="ghost"
                                          className="text-xs h-6 px-2 hover:bg-cyan-500/20"
                                          onClick={() => {
                                            console.log('Viewing file:', viewPath);
                                            setViewingFile(viewPath);
                                          }}
                                        >
                                          <Eye className="h-3 w-3" />
                                        </Button>
                                      </div>
                                    );
                                  })}
                                {plan.results.files_created.length > 3 && (
                                  <p className="text-xs text-muted-foreground">
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
                                // localStorage.setItem('incomeBuilderActionPlans', JSON.stringify(updatedPlans));
                              }}
                            >
                              {plan.expanded ? 'Hide' : 'View'} Details
                            </Button>
                            {/* Request Advisor Review Button for completed plans */}
                            {!plan.advisor_review && (
                              <Button
                                size="sm"
                                variant="default"
                                className="bg-purple-600 hover:bg-purple-700 text-foreground flex-1"
                                onClick={async () => {
                                  console.log('📚 Requesting advisor review for completed plan:', plan.opportunity_title);

                                  // Find the actual index in the full actionPlans array
                                  const actualIndex = actionPlans.findIndex(p => p === plan);

                                  // Prepare plan data
                                  const planData = {
                                    id: plan.backend_id || `local_${Date.now()}`,
                                    opportunity_title: plan.opportunity_title,
                                    status: plan.status,
                                    steps: plan.steps || [],
                                    resources: plan.resources || [],
                                    results: plan.results || {},
                                    created_at: plan.created_at,
                                    completed_at: plan.completed_at,
                                    execution_logs: plan.execution_logs || []
                                  };

                                  // Try WebSocket first
                                  if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
                                    wsRef.current.send(JSON.stringify({
                                      type: 'request_advisor_review',
                                      plan_id: planData.id,
                                      plan_data: planData
                                    }));

                                    // Update UI to show review is pending
                                    const updatedPlans = actionPlans.map((p, i) =>
                                      i === actualIndex ? { ...p, status: 'under_review', advisor_review_pending: true } : p
                                    );
                                    savePlans(updatedPlans);

                                    console.log('✅ Advisor review requested via WebSocket');

                                    // Make sure plans are saved before redirect
                                    localStorage.setItem('incomeBuilderActionPlans', JSON.stringify(updatedPlans));
                                    console.log('💾 Saved plans before redirect');

                                    // Redirect to Neural Orchestra to see the advisor review and team formation
                                    setTimeout(() => {
                                      window.location.href = '/neural-orchestra?plan=' + planData.id;
                                    }, 1000);
                                  } else {
                                    // Fallback to API
                                    console.log('⚠️ WebSocket not available, using API fallback');

                                    try {
                                      const response = await fetch(`${API_BASE_URL}/v1/intelligence/advisor-review/`, {
                                        method: 'POST',
                                        headers: {
                                          'Content-Type': 'application/json',
                                        },
                                        body: JSON.stringify(planData)
                                      });

                                      const result = await response.json();

                                      if (result.success) {
                                        console.log('✅ Advisor review received:', result);

                                        // Update plan with advisor review
                                        const updatedPlans = actionPlans.map((p, i) =>
                                          i === actualIndex ? {
                                            ...p,
                                            advisor_review: result.advisor_review,
                                            team: result.team,
                                            status: 'reviewed'
                                          } : p
                                        );
                                        savePlans(updatedPlans);

                                        // Redirect to Neural Orchestra to see the advisor review and team formation
                                        setTimeout(() => {
                                          window.location.href = '/neural-orchestra?plan=' + planData.id;
                                        }, 1000);
                                      }
                                    } catch (error) {
                                      console.error('Error requesting advisor review:', error);
                                    }
                                  }
                                }}
                              >
                                <Sparkles className="mr-1 h-3 w-3" />
                                Get Advisor Review
                              </Button>
                            )}
                            <DropdownMenu>
                              <DropdownMenuTrigger asChild>
                                <Button
                                  size="sm"
                                  variant="outline"
                                  className="flex-1"
                                >
                                  <Download className="h-3 w-3 mr-1" />
                                  Export
                                </Button>
                              </DropdownMenuTrigger>
                              <DropdownMenuContent align="end">
                                <DropdownMenuItem onClick={() => exportAsPDF(plan)}>
                                  <File className="mr-2 h-4 w-4" />
                                  PDF
                                </DropdownMenuItem>
                                <DropdownMenuItem onClick={() => exportAsMarkdown(plan)}>
                                  <FileText className="mr-2 h-4 w-4" />
                                  Markdown
                                </DropdownMenuItem>
                                <DropdownMenuItem onClick={() => exportAsCSV(plan)}>
                                  <FileSpreadsheet className="mr-2 h-4 w-4" />
                                  CSV
                                </DropdownMenuItem>
                                <DropdownMenuItem onClick={() => exportAsJSON(plan)}>
                                  <FileJson className="mr-2 h-4 w-4" />
                                  JSON
                                </DropdownMenuItem>
                              </DropdownMenuContent>
                            </DropdownMenu>
                          </div>
                        </div>
                      )}

                      {/* Advisor Review Section */}
                      {plan.advisor_review && (
                        <div className="mt-4 p-4 bg-purple-50 rounded-md border border-purple-200">
                          <h4 className="font-semibold text-sm mb-3 text-purple-800 flex items-center">
                            <Sparkles className="h-4 w-4 mr-2" />
                            Advisor Review by {plan.advisor_review.advisor}
                          </h4>

                          <div className="space-y-3">
                            {/* Success Probability */}
                            {plan.advisor_review.success_probability && (
                              <div className="flex items-center justify-between">
                                <span className="text-sm text-gray-600">Success Probability</span>
                                <Badge variant="secondary" className="bg-green-100">
                                  {(plan.advisor_review.success_probability * 100).toFixed(0)}%
                                </Badge>
                              </div>
                            )}

                            {/* Budget Estimate */}
                            {plan.advisor_review.budget_estimate && (
                              <div className="flex items-center justify-between">
                                <span className="text-sm text-gray-600">Budget Required</span>
                                <span className="font-semibold">${plan.advisor_review.budget_estimate.toLocaleString()}</span>
                              </div>
                            )}

                            {/* Timeline Adjustment */}
                            {plan.advisor_review.timeline_adjustment && (
                              <div className="p-2 bg-yellow-50 rounded text-sm">
                                <Clock className="h-3 w-3 inline-block mr-1" />
                                {plan.advisor_review.timeline_adjustment}
                              </div>
                            )}

                            {/* Immediate Actions */}
                            {plan.advisor_review.immediate_actions && plan.advisor_review.immediate_actions.length > 0 && (
                              <div>
                                <h5 className="text-xs font-semibold text-purple-700 mb-1">Immediate Actions:</h5>
                                <ul className="space-y-1">
                                  {plan.advisor_review.immediate_actions.slice(0, 3).map((action: string, idx: number) => (
                                    <li key={idx} className="text-xs text-gray-700 flex items-start">
                                      <ArrowRight className="h-3 w-3 mr-1 mt-0.5 text-purple-500" />
                                      {action}
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            {/* Success Metrics */}
                            {plan.advisor_review.success_metrics && plan.advisor_review.success_metrics.length > 0 && (
                              <div>
                                <h5 className="text-xs font-semibold text-purple-700 mb-1">Success Metrics:</h5>
                                <div className="flex flex-wrap gap-2">
                                  {plan.advisor_review.success_metrics.slice(0, 3).map((metric: string, idx: number) => (
                                    <Badge key={idx} variant="outline" className="text-xs">
                                      <Target className="h-3 w-3 mr-1" />
                                      {metric}
                                    </Badge>
                                  ))}
                                </div>
                              </div>
                            )}
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
                              <div className="bg-muted/5 rounded p-2 max-h-32 overflow-y-auto">
                                {plan.execution_logs.map((log: any, idx: number) => (
                                  <div key={idx} className="text-xs">
                                    <span className="text-muted-foreground">
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
            <AlertDescription className="text-muted-foreground">
              <strong className="text-foreground">Your Quick Start Path to $1000/month:</strong>
              <ol className="mt-2 space-y-1 list-decimal list-inside text-muted-foreground">
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
                <CardTitle className="text-foreground">Week 1 Goals</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  <li className="flex items-center gap-2 text-muted-foreground">
                    <Target className="h-4 w-4 text-cyan-400" />
                    Create profiles on 3 platforms
                  </li>
                  <li className="flex items-center gap-2 text-muted-foreground">
                    <Target className="h-4 w-4 text-cyan-400" />
                    Complete 5 sample projects
                  </li>
                  <li className="flex items-center gap-2 text-muted-foreground">
                    <Target className="h-4 w-4 text-cyan-400" />
                    Apply to 50 opportunities
                  </li>
                  <li className="flex items-center gap-2 text-muted-foreground">
                    <Target className="h-4 w-4 text-cyan-400" />
                    Earn first $100
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <CardTitle className="text-foreground">Month 1 Targets</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  <li className="flex items-center gap-2 text-muted-foreground">
                    <TrendingUp className="h-4 w-4 text-green-500" />
                    3 active income streams
                  </li>
                  <li className="flex items-center gap-2 text-muted-foreground">
                    <TrendingUp className="h-4 w-4 text-green-500" />
                    $500+ monthly revenue
                  </li>
                  <li className="flex items-center gap-2 text-muted-foreground">
                    <TrendingUp className="h-4 w-4 text-green-500" />
                    5+ positive reviews
                  </li>
                  <li className="flex items-center gap-2 text-muted-foreground">
                    <TrendingUp className="h-4 w-4 text-green-500" />
                    2 recurring clients
                  </li>
                </ul>
              </CardContent>
            </Card>
          </div>

          {/* Quick Start Action Button */}
          <Card className="bg-gradient-to-r from-cyan-600 to-purple-600 border-0">
            <CardHeader className="text-center">
              <CardTitle className="text-foreground text-xl">Ready to Start Earning?</CardTitle>
              <CardDescription className="text-foreground">
                Set up all 4 automation workflows for your path to $1000/month
              </CardDescription>
            </CardHeader>
            <CardContent className="text-center">
              <Button
                size="lg"
                className="bg-white text-purple-600 hover:bg-muted/10 font-bold px-8 py-3"
                onClick={executeQuickStart}
                disabled={settingUpAutomation === 'quick_start'}
              >
                {settingUpAutomation === 'quick_start' ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-600 mr-2"></div>
                    Setting Up Your Income Machine...
                  </>
                ) : (
                  <>
                    <Rocket className="h-5 w-5 mr-2" />
                    Execute Quick Start Setup
                  </>
                )}
              </Button>
              <p className="text-sm text-foreground mt-2">
                This will set up Blog + Social Media automation to get you started!
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Automation Tab */}
        <TabsContent value="automation" className="space-y-4">
          <Alert className="border-purple-500/30 bg-slate-800">
            <Zap className="h-4 w-4 text-purple-400" />
            <AlertDescription className="text-muted-foreground">
              <strong className="text-foreground">Automated Income Potential: $200-950/day</strong>
              <p className="mt-1 text-muted-foreground">Set up once, earn continuously with AI automation</p>
            </AlertDescription>
          </Alert>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card className="bg-slate-800 border-slate-700 hover:border-cyan-500/30 transition-all">
              <CardHeader>
                <CardTitle className="text-foreground">Blog Automation</CardTitle>
                <CardDescription className="text-muted-foreground">3 posts/day across platforms</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <p className="text-2xl font-bold text-green-500">$50-200/day</p>
                  <p className="text-sm text-muted-foreground">AdSense + Affiliates + Sponsored</p>
                  <Button
                    className="w-full bg-slate-700 hover:bg-slate-600 border-cyan-500/30"
                    variant="outline"
                    onClick={() => setupAutomationWorkflow('blog')}
                    disabled={settingUpAutomation === 'blog'}
                  >
                    {settingUpAutomation === 'blog' ? 'Setting Up...' : 'Setup Automation'}
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-slate-800 border-slate-700 hover:border-cyan-500/30 transition-all">
              <CardHeader>
                <CardTitle className="text-foreground">Social Media Automation</CardTitle>
                <CardDescription className="text-muted-foreground">10 posts/day automated</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <p className="text-2xl font-bold text-cyan-400">$30-150/day</p>
                  <p className="text-sm text-muted-foreground">Sponsored + Affiliate Marketing</p>
                  <Button
                    className="w-full bg-slate-700 hover:bg-slate-600 border-cyan-500/30"
                    variant="outline"
                    onClick={() => setupAutomationWorkflow('social_media')}
                    disabled={settingUpAutomation === 'social_media'}
                  >
                    {settingUpAutomation === 'social_media' ? 'Setting Up...' : 'Setup Automation'}
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-slate-800 border-slate-700 hover:border-purple-500/30 transition-all">
              <CardHeader>
                <CardTitle className="text-foreground">Video Scripts</CardTitle>
                <CardDescription className="text-muted-foreground">5 scripts/day for creators</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <p className="text-2xl font-bold text-purple-400">$100-500/day</p>
                  <p className="text-sm text-muted-foreground">Direct Sales + Subscriptions</p>
                  <Button
                    className="w-full bg-slate-700 hover:bg-slate-600 border-purple-500/30"
                    variant="outline"
                    onClick={() => setupAutomationWorkflow('video_scripts')}
                    disabled={settingUpAutomation === 'video_scripts'}
                  >
                    {settingUpAutomation === 'video_scripts' ? 'Setting Up...' : 'Setup Automation'}
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-slate-800 border-slate-700 hover:border-indigo-500/30 transition-all">
              <CardHeader>
                <CardTitle className="text-foreground">Digital Templates</CardTitle>
                <CardDescription className="text-muted-foreground">10 new templates/week</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <p className="text-2xl font-bold text-indigo-400">$20-100/day</p>
                  <p className="text-sm text-muted-foreground">Etsy + Gumroad + Creative Market</p>
                  <Button
                    className="w-full bg-slate-700 hover:bg-slate-600 border-indigo-500/30"
                    variant="outline"
                    onClick={() => setupAutomationWorkflow('digital_templates')}
                    disabled={settingUpAutomation === 'digital_templates'}
                  >
                    {settingUpAutomation === 'digital_templates' ? 'Setting Up...' : 'Setup Automation'}
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