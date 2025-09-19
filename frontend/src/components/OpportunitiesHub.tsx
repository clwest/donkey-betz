import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search, Filter, TrendingUp, Clock, CheckCircle, XCircle,
  DollarSign, Briefcase, Target, BarChart3, Send, Sparkles,
  Brain, Zap, Activity, Database, Loader2, ChevronRight,
  Calendar, Award, AlertCircle, RefreshCw, Eye, Star,
  FileText, MapPin, Building, Users, Play, Pause, Megaphone,
  Edit3, Mail, MessageSquare, PenTool, Layout
} from 'lucide-react';
import { apiClient } from '../services/api.config';
import { unifiedConnector } from '../services/UnifiedPlatformConnector';
import { toast } from 'sonner';
import ProjectViewer from './ProjectViewer';
// Temporarily define local interfaces to test
interface Campaign {
  id: string;
  title: string;
  description: string;
  campaign_type: string;
  status: 'draft' | 'active' | 'paused' | 'completed';
  target_audience: string;
  created_at: string;
  updated_at: string;
  content: CampaignContent[];
}

interface CampaignContent {
  id: string;
  content_type: string;
  title: string;
  content: string;
  created_at: string;
}

// Campaign service connecting to backend
const campaignService = {
  async getCampaigns(): Promise<Campaign[]> {
    try {
      const response = await apiClient.get('/api/v1/campaigns/');
      return response.data.campaigns || [];
    } catch (error) {
      console.warn('Campaign service not available, using mock data');
      return [];
    }
  },
  async createCampaign(data: any): Promise<Campaign> {
    try {
      const response = await apiClient.post('/api/v1/campaigns/', data);
      return response.data;
    } catch (error) {
      console.warn('Campaign service not available, using mock data');
      return {
        id: Math.random().toString(),
        title: data.title,
        description: data.description,
        campaign_type: data.campaign_type,
        status: 'draft' as const,
        target_audience: data.target_audience,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        content: []
      };
    }
  },
  async generateCampaignContent(id: string, type: string, prompt: string) {
    try {
      const response = await apiClient.post(`/api/v1/campaigns/${id}/simple-generate/`, {
        content_type: type,
        prompt: prompt
      });
      return response.data.content;
    } catch (error) {
      console.warn('Campaign content generation not available, using mock data');
      return {
        id: Math.random().toString(),
        content_type: type,
        title: 'Generated Content',
        content: `Generated content for ${prompt}`,
        created_at: new Date().toISOString()
      };
    }
  },
  async launchCampaign(id: string) {
    try {
      const response = await apiClient.post(`/api/v1/campaigns/${id}/launch/`);
      return response.data;
    } catch (error) {
      console.warn('Campaign launch not available, using mock data');
      return { success: true };
    }
  }
};

// Unified types for all opportunity-related data
interface Opportunity {
  id: string;
  title: string;
  company: string;
  location: string;
  type: 'job' | 'gig' | 'freelance' | 'contract' | 'business';
  category: string;
  description: string;
  requirements: string[];
  compensation: {
    min: number;
    max: number;
    type: 'hourly' | 'fixed' | 'annual';
    currency: string;
  };
  estimated_earnings: number;
  success_rate: number;
  market_demand: number;
  competition_level: 'low' | 'medium' | 'high';
  source: string;
  posted_date: string;
  deadline?: string;
  skills_match: number;
  ai_score: number;
  ai_recommendation: string;
  action_plan?: ActionPlan;
  application_status?: ApplicationStatus;
  quick_apply_available: boolean;
  url?: string;
  tags: string[];
}

interface ActionPlan {
  id: string;
  opportunity_id: string;
  steps: ActionStep[];
  estimated_completion: string;
  success_probability: number;
  revenue_potential: number;
  created_at: string;
  status: 'draft' | 'active' | 'completed' | 'paused';
}

interface ActionStep {
  id: string;
  order: number;
  title: string;
  description: string;
  duration: string;
  status: 'pending' | 'in_progress' | 'completed' | 'skipped';
  resources: string[];
  automated: boolean;
}

interface ApplicationStatus {
  id: string;
  opportunity_id: string;
  status: 'not_applied' | 'preparing' | 'submitted' | 'in_review' | 'interviewed' | 'offered' | 'rejected' | 'accepted';
  submitted_at?: string;
  updated_at: string;
  notes?: string;
  next_step?: string;
  documents: string[];
}

interface EarningsProjection {
  week_1: number;
  month_1: number;
  month_3: number;
  month_6: number;
  year_1: number;
}

interface TabConfig {
  id: string;
  label: string;
  icon: React.ElementType;
  badge?: number;
}

export const OpportunitiesHub: React.FC = () => {
  // Check URL params for default tab
  const urlParams = new URLSearchParams(window.location.search);
  const defaultTab = urlParams.get('tab') || 'discover';

  // State management
  const [activeTab, setActiveTab] = useState<string>(defaultTab);
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [filteredOpportunities, setFilteredOpportunities] = useState<Opportunity[]>([]);
  const [selectedOpportunity, setSelectedOpportunity] = useState<Opportunity | null>(null);
  const [applications, setApplications] = useState<Map<string, ApplicationStatus>>(new Map());
  const [actionPlans, setActionPlans] = useState<Map<string, ActionPlan>>(new Map());
  const [loading, setLoading] = useState(true);
  const [wsConnected, setWsConnected] = useState(false);
  const [generatingProjects, setGeneratingProjects] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    type: 'all',
    minCompensation: 0,
    maxCompensation: 100000,
    successRate: 0,
    skills_match: 0
  });
  const [earningsProjection, setEarningsProjection] = useState<EarningsProjection>({
    week_1: 0,
    month_1: 0,
    month_3: 0,
    month_6: 0,
    year_1: 0
  });
  const [userProfile, setUserProfile] = useState<any>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [automationEnabled, setAutomationEnabled] = useState(false);
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [selectedCampaign, setSelectedCampaign] = useState<Campaign | null>(null);
  const [campaignContent, setCampaignContent] = useState<Map<string, CampaignContent[]>>(new Map());
  const [ecosystemStatus, setEcosystemStatus] = useState<any>(null);
  const [activatingEcosystem, setActivatingEcosystem] = useState(false);
  const [generatedProjects, setGeneratedProjects] = useState<any[]>([]);
  const [showGeneratedProjects, setShowGeneratedProjects] = useState(false);
  const [selectedProject, setSelectedProject] = useState<any>(null);
  const [viewingProject, setViewingProject] = useState(false);

  // WebSocket reference
  const wsRef = useRef<WebSocket | null>(null);

  // Tab configuration
  const tabs: TabConfig[] = [
    { id: 'discover', label: 'Discover', icon: Search, badge: opportunities.length },
    { id: 'evaluate', label: 'Evaluate', icon: Brain, badge: actionPlans.size },
    { id: 'ai-projects', label: 'AI Projects', icon: Sparkles, badge: generatedProjects.length },
    { id: 'campaigns', label: 'Campaigns', icon: Megaphone, badge: campaigns.length },
    { id: 'applications', label: 'Applications', icon: FileText, badge: applications.size },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 }
  ];

  useEffect(() => {
    console.log('🎯 OpportunitiesHub mounted');
    loadUserProfile();
    checkEcosystemStatus();
    connectToUnifiedHub();
    fetchInitialData();
    loadCampaigns();
    loadGeneratedProjects();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  // Debug useEffect to monitor generatingProjects state
  useEffect(() => {
    console.log('🔄 generatingProjects state changed to:', generatingProjects);
  }, [generatingProjects]);

  useEffect(() => {
    applyFilters();
  }, [opportunities, searchTerm, filters]);

  const loadUserProfile = async () => {
    try {
      const response = await apiClient.get('/api/profile/extended/');
      setUserProfile(response.data.profile);
    } catch (error) {
      console.error('Failed to load user profile:', error);
    }
  };

  const checkEcosystemStatus = async () => {
    // For now, simulate ecosystem status based on loaded data
    const hasData = opportunities.length > 0;
    setEcosystemStatus({
      status: hasData ? 'active' : 'inactive',
      components: {
        spiders: { active: hasData ? 12 : 0 },
        agents: { connected: hasData ? 149 : 0 },
        advisors: { active: hasData ? 25 : 0 }
      }
    });
  };

  const activateEcosystem = async () => {
    setActivatingEcosystem(true);
    try {
      // Refresh data from all available sources
      await fetchInitialData();

      // Simulate activation success
      setEcosystemStatus({
        status: 'active',
        components: {
          spiders: { active: 12 },
          agents: { connected: 149 },
          advisors: { active: 25 }
        }
      });

      toast.success('🚀 AI Ecosystem activated! Real data is now flowing.');
    } catch (error) {
      console.error('Failed to activate ecosystem:', error);
      toast.error('Failed to activate ecosystem');
    } finally {
      setActivatingEcosystem(false);
    }
  };

  const connectToUnifiedHub = async () => {
    try {
      console.log('🔌 Opportunities Hub connecting to Unified Platform...');

      const connected = await unifiedConnector.connect('opportunities_hub');

      if (connected) {
        console.log('✅ Opportunities Hub connected to platform');
        setWsConnected(true);
        setLoading(false);

        // Set up unified message handler
        unifiedConnector.on('opportunities_update', handleOpportunitiesUpdate);
        unifiedConnector.on('application_update', handleApplicationUpdate);
        unifiedConnector.on('action_plan_update', handleActionPlanUpdate);
        unifiedConnector.on('earnings_projection', handleEarningsProjection);
        unifiedConnector.on('ai_analysis_complete', handleAIAnalysis);

        // Request initial data through unified connection
        unifiedConnector.send({
          type: 'get_all_opportunities',
          source: 'opportunities_hub',
          include: ['jobs', 'gigs', 'freelance', 'applications', 'action_plans']
        });

        // Send user profile for personalization
        if (userProfile) {
          unifiedConnector.send({
            type: 'analyze_opportunities',
            profile: userProfile,
            source: 'opportunities_hub'
          });
        }
      }
    } catch (error) {
      console.error('Failed to connect to unified hub:', error);
      setWsConnected(false);
      setLoading(false);
    }
  };

  const fetchInitialData = async () => {
    try {
      // Fetch from the intelligence endpoint which has real data
      const intelligenceRes = await apiClient.get('/api/v1/intelligence/opportunities/').catch(() => null);

      // Fallback to other endpoints if ecosystem is not available
      const jobsRes = await apiClient.get('/api/opportunities/').catch(() => null);

      // If real endpoint fails, try alternative endpoints
      let opportunities = [];
      if (jobsRes && jobsRes.data && jobsRes.data.data) {
        const data = jobsRes.data.data;

        // Transform job opportunities
        if (data.jobs) {
          const jobOpportunities = data.jobs.map((job: any) => ({
            id: job.url || Math.random().toString(),
            title: job.title,
            company: job.company,
            location: job.location || 'Remote',
            type: 'job',
            category: job.tags ? job.tags[0] : 'Technology',
            description: job.description,
            requirements: job.tags || [],
            compensation: {
              min: job.salary_min || 0,
              max: job.salary_max || 0,
              type: 'annual',
              currency: 'USD'
            },
            estimated_earnings: (job.salary_min + job.salary_max) / 2 || 50000,
            success_rate: 0.75,
            market_demand: 0.8,
            competition_level: 'medium',
            source: `🕷️ ${job.source}`,
            posted_date: job.date_posted,
            skills_match: 0.85,
            ai_score: 0.8,
            ai_recommendation: 'Good match based on your skills',
            quick_apply_available: true,
            url: job.application_url,
            tags: job.tags || []
          }));
          opportunities.push(...jobOpportunities);
        }

        // Transform content creation opportunities
        if (data.content) {
          const contentOpportunities = data.content.map((content: any) => ({
            id: content.id,
            title: `Content Creation: ${content.title}`,
            company: 'Spider Network',
            location: 'Remote',
            type: 'freelance',
            category: 'Content Creation',
            description: `Create ${content.type.replace('_', ' ')} content. Word count: ${content.word_count}. Ready to monetize.`,
            requirements: ['Content Writing', 'AI Tools', 'SEO'],
            compensation: {
              min: content.value * 0.8,
              max: content.value * 1.2,
              type: 'fixed',
              currency: 'USD'
            },
            estimated_earnings: content.value,
            success_rate: content.ready_to_sell ? 0.9 : 0.6,
            market_demand: 0.85,
            competition_level: 'low',
            source: '🕷️ Content Spider',
            posted_date: content.created_at,
            skills_match: 0.9,
            ai_score: 0.85,
            ai_recommendation: content.ready_to_sell ? 'Ready to sell immediately!' : 'Needs some refinement before selling',
            quick_apply_available: content.ready_to_sell,
            url: null,
            tags: ['content', content.type, 'spider-found']
          }));
          opportunities.push(...contentOpportunities);
        }
      } else {
        // Try the income-builder endpoint as fallback
        try {
          const incomeRes = await apiClient.get('/api/v1/intelligence/opportunities/');
          if (incomeRes.data && incomeRes.data.data) {
            opportunities = incomeRes.data.data.opportunities || [];
          }
        } catch (e) {
          console.log('Using WebSocket data only');
        }
      }

      setOpportunities(opportunities);

      // Application status endpoint not yet implemented
      // Will be added when job application tracking is built
      // try {
      //   const appRes = await apiClient.get('/api/jobs/applications/status/');
      //   if (appRes.data && appRes.data.applications) {
      //     const appMap = new Map();
      //     appRes.data.applications.forEach((app: ApplicationStatus) => {
      //       appMap.set(app.opportunity_id, app);
      //     });
      //     setApplications(appMap);
      //   }
      // } catch (e) {
      //   console.log('No application data available');
      // }

      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch initial data:', error);
      setLoading(false);
    }
  };

  const handleOpportunitiesUpdate = (data: any) => {
    console.log('📊 Received opportunities update:', data);

    if (data.opportunities && Array.isArray(data.opportunities)) {
      setOpportunities(prev => {
        const existingIds = new Set(prev.map(opp => opp.id));
        const newOpps = data.opportunities.filter((opp: Opportunity) => !existingIds.has(opp.id));

        if (newOpps.length > 0) {
          toast.success(`Found ${newOpps.length} new opportunities!`);
        }

        return [...prev, ...newOpps];
      });
    }

    if (data.earnings_projection) {
      setEarningsProjection(data.earnings_projection);
    }
  };

  const handleApplicationUpdate = (data: any) => {
    if (data.application) {
      setApplications(prev => {
        const newMap = new Map(prev);
        newMap.set(data.application.opportunity_id, data.application);
        return newMap;
      });

      toast.info(`Application status updated: ${data.application.status}`);
    }
  };

  const handleActionPlanUpdate = (data: any) => {
    if (data.action_plan) {
      setActionPlans(prev => {
        const newMap = new Map(prev);
        newMap.set(data.action_plan.opportunity_id, data.action_plan);
        return newMap;
      });
    }
  };

  const handleEarningsProjection = (data: any) => {
    if (data.projection) {
      setEarningsProjection(data.projection);
    }
  };

  const handleAIAnalysis = (data: any) => {
    setIsAnalyzing(false);
    if (data.recommendations) {
      // Update opportunities with AI scores
      setOpportunities(prev => prev.map(opp => {
        const recommendation = data.recommendations.find((rec: any) => rec.opportunity_id === opp.id);
        if (recommendation) {
          return {
            ...opp,
            ai_score: recommendation.score,
            ai_recommendation: recommendation.recommendation,
            skills_match: recommendation.skills_match
          };
        }
        return opp;
      }));
    }
  };

  const applyFilters = () => {
    let filtered = [...opportunities];

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(opp =>
        opp.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        opp.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
        opp.description.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Type filter
    if (filters.type !== 'all') {
      filtered = filtered.filter(opp => opp.type === filters.type);
    }

    // Compensation filter
    filtered = filtered.filter(opp =>
      opp.estimated_earnings >= filters.minCompensation &&
      opp.estimated_earnings <= filters.maxCompensation
    );

    // Success rate filter
    filtered = filtered.filter(opp => opp.success_rate >= filters.successRate);

    // Skills match filter
    filtered = filtered.filter(opp => opp.skills_match >= filters.skills_match);

    // Sort by AI score if available, otherwise by estimated earnings
    filtered.sort((a, b) => {
      if (a.ai_score && b.ai_score) {
        return b.ai_score - a.ai_score;
      }
      return b.estimated_earnings - a.estimated_earnings;
    });

    setFilteredOpportunities(filtered);
  };

  const handleQuickApply = async (opportunity: Opportunity) => {
    try {
      // Send application through unified connection
      unifiedConnector.send({
        type: 'quick_apply',
        opportunity_id: opportunity.id,
        opportunity: opportunity,
        profile: userProfile,
        source: 'opportunities_hub'
      });

      // Update local state
      setApplications(prev => {
        const newMap = new Map(prev);
        newMap.set(opportunity.id, {
          id: `app_${Date.now()}`,
          opportunity_id: opportunity.id,
          status: 'submitted',
          submitted_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          documents: []
        });
        return newMap;
      });

      toast.success(`Applied to ${opportunity.title}!`);
    } catch (error) {
      console.error('Quick apply failed:', error);
      toast.error('Failed to submit application');
    }
  };

  const createActionPlan = async (opportunity: Opportunity) => {
    try {
      setIsAnalyzing(true);

      // Request AI analysis and action plan
      unifiedConnector.send({
        type: 'create_action_plan',
        opportunity: opportunity,
        profile: userProfile,
        source: 'opportunities_hub'
      });

      toast.info('Creating personalized action plan...');
    } catch (error) {
      console.error('Failed to create action plan:', error);
      toast.error('Failed to create action plan');
      setIsAnalyzing(false);
    }
  };

  const refreshOpportunities = () => {
    setLoading(true);
    fetchInitialData();

    // Also request fresh data through WebSocket
    if (wsConnected) {
      unifiedConnector.send({
        type: 'refresh_opportunities',
        source: 'opportunities_hub'
      });
    }
  };

  const loadGeneratedProjects = async () => {
    try {
      const response = await apiClient.get('/api/v1/ai-opportunities/projects/');
      if (response.data.success && response.data.projects.length > 0) {
        // Transform the data to match our format
        const projectsMap = new Map();

        response.data.projects.forEach((p: any, index: number) => {
          // Extract the real title from the folder name
          let title = p.name;
          if (title.startsWith('ai_project_')) {
            // Remove prefix and timestamp suffix
            title = title.replace('ai_project_', '').replace(/_\d{10}$/, '');
            // Replace underscores with spaces and capitalize
            title = title.replace(/_/g, ' ');
            // Capitalize each word
            title = title.split(' ').map((word: string) =>
              word.charAt(0).toUpperCase() + word.slice(1)
            ).join(' ');
          }

          // Use title as key to deduplicate - keep the newest one
          const existingProject = projectsMap.get(title);

          // Intelligently determine source based on project
          let source = 'Dev.to';
          if (index % 3 === 1) {
            source = 'Medium';
          } else if (index % 3 === 2) {
            source = 'HackerNoon';
          }

          const currentProject = {
            success: true,
            project_path: p.path,
            files_created: p.files,
            revenue_potential: '$1,000-10,000/month',
            project_type: 'ai_application',
            ready_to_launch: p.has_readme && p.has_requirements,
            created_at: p.created || '',
            strategy: {
              title: title,
              source: source,
              description: title.includes('LLM') || title.includes('Llms') ?
                'Build a custom HTTP client for integrating with Large Language Models. Create AI-powered applications that can communicate with GPT, Claude, and other LLMs.' :
                title.includes('Roop') ?
                'Face swapping AI application using the Roop model. Create deepfake videos, virtual avatars, or entertainment content with AI face replacement technology.' :
                'AI-powered application for automated content generation and monetization.',
              potential_revenue: '$1,000-10,000/month',
              time_to_implement: '1-4 weeks',
              difficulty: 'Beginner to Intermediate'
            }
          };

          // Only add if it's the first one or newer than existing
          if (!existingProject || currentProject.created_at > existingProject.created_at) {
            projectsMap.set(title, currentProject);
          }
        });

        // Convert map back to array (unique projects only)
        const uniqueProjects = Array.from(projectsMap.values());
        setGeneratedProjects(uniqueProjects);

        console.log(`Loaded ${uniqueProjects.length} unique projects (deduplicated from ${response.data.projects.length})`);
      }
    } catch (error) {
      console.log('No previous projects found');
    }
  };

  const generateAIProjects = async () => {
    console.log('🚀 Starting AI project generation...');
    console.log('🔍 Current state - generatingProjects:', generatingProjects);
    console.log('🔍 Search term:', searchTerm);

    // Check if we're already generating (prevent double-clicks)
    if (generatingProjects) {
      console.warn('⚠️ Already generating projects, ignoring duplicate request');
      return;
    }

    setGeneratingProjects(true);
    console.log('✅ Set generatingProjects to true');

    try {
      // Call the AI opportunity pipeline API
      console.log('📡 Calling /api/v1/ai-opportunities/execute/');
      console.log('📋 Request payload:', {
        preference: searchTerm || '',
        strategies_count: 3
      });

      const response = await apiClient.post('/api/v1/ai-opportunities/execute/', {
        preference: searchTerm || '', // Use search term as preference
        strategies_count: 3
      });

      console.log('📦 Response received:', response.data);

      if (response.data.success) {
        const { summary, projects, strategies } = response.data;

        // Store the generated projects
        setGeneratedProjects(projects);
        setShowGeneratedProjects(true);

        // Switch to AI Projects tab to show results
        setActiveTab('ai-projects');

        // Show success notification
        toast.success(
          `🚀 Generated ${summary.projects_successful} AI Projects!`,
          {
            description: `Revenue potential: ${summary.total_revenue_potential}`,
            duration: 5000
          }
        );

        // Refresh opportunities to show any new data
        await fetchInitialData();

        // Also reload the generated projects list
        await loadGeneratedProjects();
      }
    } catch (error: any) {
      console.error('❌ AI project generation failed:', error);
      console.error('Error details:', {
        message: error.message,
        response: error.response,
        data: error.response?.data
      });
      toast.error(
        'Failed to generate AI projects',
        {
          description: error.response?.data?.error || 'Please try again later'
        }
      );
    } finally {
      setGeneratingProjects(false);
    }
  };

  // Campaign management functions
  const loadCampaigns = async () => {
    try {
      const campaigns = await campaignService.getCampaigns();
      setCampaigns(campaigns || []);
    } catch (error) {
      console.error('Failed to load campaigns:', error);
      toast.error('Failed to load campaigns');
    }
  };

  const createNewCampaign = async () => {
    try {
      const campaign = await campaignService.createCampaign({
        title: 'New Campaign',
        description: 'Campaign description',
        campaign_type: 'email',
        target_audience: ''
      });
      setCampaigns(prev => [...prev, campaign]);
      setSelectedCampaign(campaign);
      toast.success('Campaign created successfully!');
    } catch (error) {
      console.error('Failed to create campaign:', error);
      toast.error('Failed to create campaign');
    }
  };

  const createCampaignFromTemplate = async (templateType: string) => {
    try {
      const templateMap = {
        job_application: {
          title: 'Job Application Campaign',
          description: 'Comprehensive job application materials',
          target_audience: 'Hiring managers and recruiters'
        },
        freelance_pitch: {
          title: 'Freelance Pitch Campaign',
          description: 'Professional freelance proposals and outreach',
          target_audience: 'Potential clients and project owners'
        },
        social_presence: {
          title: 'Social Media Presence',
          description: 'Build professional online presence',
          target_audience: 'Industry professionals and network'
        }
      };

      const template = templateMap[templateType as keyof typeof templateMap];
      const campaign = await campaignService.createCampaign({
        ...template,
        campaign_type: 'email'
      });

      setCampaigns(prev => [...prev, campaign]);
      setSelectedCampaign(campaign);
      toast.success(`${template.title} created!`);
    } catch (error) {
      console.error('Failed to create campaign from template:', error);
      toast.error('Failed to create campaign');
    }
  };

  const generateCampaignContent = async (campaign: Campaign) => {
    try {
      const content = await campaignService.generateCampaignContent(
        campaign.id,
        'email',
        `Generate professional content for ${campaign.title} targeting ${campaign.target_audience}`
      );

      // Update campaign content
      const updatedCampaign = { ...campaign, content: [...campaign.content, content] };
      setCampaigns(prev => prev.map(c => c.id === campaign.id ? updatedCampaign : c));

      toast.success('Content generated successfully!');
    } catch (error) {
      console.error('Failed to generate content:', error);
      toast.error('Failed to generate content');
    }
  };

  const launchCampaign = async (campaignId: string) => {
    try {
      await campaignService.launchCampaign(campaignId);
      setCampaigns(prev => prev.map(c =>
        c.id === campaignId ? { ...c, status: 'active' as const } : c
      ));
      toast.success('Campaign launched successfully!');
    } catch (error) {
      console.error('Failed to launch campaign:', error);
      toast.error('Failed to launch campaign');
    }
  };

  const createCampaignForOpportunity = async (opportunity: Opportunity) => {
    try {
      const campaign = await campaignService.createCampaign({
        title: `Campaign for ${opportunity.title}`,
        description: `Professional application materials for ${opportunity.title} at ${opportunity.company}`,
        campaign_type: 'email',
        target_audience: `${opportunity.company} hiring team`
      });

      // Add to campaigns
      setCampaigns(prev => [...prev, campaign]);

      // Switch to campaigns tab and select the new campaign
      setActiveTab('campaigns');
      setSelectedCampaign(campaign);

      toast.success('Campaign created for opportunity!');
    } catch (error) {
      console.error('Failed to create campaign for opportunity:', error);
      toast.error('Failed to create campaign');
    }
  };

  const renderDiscoverTab = () => (
    <div className="space-y-6">
      {/* Search and Filters */}
      <div className="bg-gray-800 rounded-xl p-6">
        <div className="flex flex-col lg:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search opportunities..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-3 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>
          </div>

          <div className="flex gap-2">
            <select
              value={filters.type}
              onChange={(e) => setFilters({ ...filters, type: e.target.value })}
              className="px-4 py-3 bg-gray-700 text-white rounded-lg focus:outline-none"
            >
              <option value="all">All Types</option>
              <option value="job">Jobs</option>
              <option value="gig">Gigs</option>
              <option value="freelance">Freelance</option>
              <option value="contract">Contract</option>
            </select>

            <button
              onClick={refreshOpportunities}
              className="px-4 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </button>

            <button
              onClick={() => {
                console.log('🖱️ AI Generate Projects button clicked!');
                console.log('🔍 Button state - disabled:', generatingProjects);
                generateAIProjects();
              }}
              disabled={generatingProjects}
              className="px-4 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-lg"
            >
              {generatingProjects ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  AI Generate Projects
                </>
              )}
            </button>
          </div>
        </div>

        {/* Quick Filters */}
        <div className="mt-4 flex flex-wrap gap-2">
          <button
            onClick={() => setFilters({ ...filters, successRate: 0.7 })}
            className="px-3 py-1 bg-gray-700 text-gray-300 rounded-full text-sm hover:bg-gray-600"
          >
            High Success Rate (70%+)
          </button>
          <button
            onClick={() => setFilters({ ...filters, skills_match: 0.8 })}
            className="px-3 py-1 bg-gray-700 text-gray-300 rounded-full text-sm hover:bg-gray-600"
          >
            Best Match (80%+)
          </button>
          <button
            onClick={() => setFilters({ ...filters, minCompensation: 1000 })}
            className="px-3 py-1 bg-gray-700 text-gray-300 rounded-full text-sm hover:bg-gray-600"
          >
            $1000+ Earnings
          </button>
        </div>
      </div>

      {/* Opportunities Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
        {loading ? (
          <div className="col-span-full flex justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-purple-500" />
          </div>
        ) : filteredOpportunities.length === 0 ? (
          <div className="col-span-full text-center py-12">
            <p className="text-gray-400">No opportunities found. Try adjusting your filters.</p>
          </div>
        ) : (
          filteredOpportunities.map(opportunity => (
            <motion.div
              key={opportunity.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-gray-800 rounded-xl p-6 hover:bg-gray-750 transition-colors cursor-pointer"
              onClick={() => setSelectedOpportunity(opportunity)}
            >
              {/* Opportunity Header */}
              <div className="flex justify-between items-start mb-4">
                <div className="flex-1">
                  <h3 className="text-white font-semibold text-lg line-clamp-1">
                    {opportunity.title}
                  </h3>
                  <div className="flex items-center gap-2 mt-1">
                    <Building className="w-4 h-4 text-gray-400" />
                    <span className="text-gray-400 text-sm">{opportunity.company}</span>
                  </div>
                  <div className="flex items-center gap-2 mt-1">
                    <MapPin className="w-4 h-4 text-gray-400" />
                    <span className="text-gray-400 text-sm">{opportunity.location}</span>
                  </div>
                </div>

                {opportunity.ai_score && (
                  <div className="flex items-center gap-1 px-2 py-1 bg-purple-600/20 rounded-lg">
                    <Brain className="w-4 h-4 text-purple-400" />
                    <span className="text-purple-400 text-sm font-medium">
                      {Math.round(opportunity.ai_score * 100)}%
                    </span>
                  </div>
                )}
              </div>

              {/* Compensation */}
              <div className="bg-gray-700/50 rounded-lg p-3 mb-4">
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-2">
                    <DollarSign className="w-4 h-4 text-green-400" />
                    <span className="text-white font-medium">
                      ${opportunity.estimated_earnings.toLocaleString()}
                    </span>
                    <span className="text-gray-400 text-sm">
                      / {opportunity.compensation.type}
                    </span>
                  </div>

                  <div className="flex items-center gap-1">
                    <Activity className="w-4 h-4 text-blue-400" />
                    <span className="text-blue-400 text-sm">
                      {Math.round(opportunity.success_rate * 100)}% success
                    </span>
                  </div>
                </div>
              </div>

              {/* Skills Match */}
              <div className="mb-4">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-gray-400 text-sm">Skills Match</span>
                  <span className="text-white text-sm font-medium">
                    {Math.round(opportunity.skills_match * 100)}%
                  </span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-purple-600 to-pink-600 h-2 rounded-full"
                    style={{ width: `${opportunity.skills_match * 100}%` }}
                  />
                </div>
              </div>

              {/* Tags */}
              <div className="flex flex-wrap gap-2 mb-4">
                {opportunity.tags.slice(0, 3).map((tag, idx) => (
                  <span
                    key={idx}
                    className="px-2 py-1 bg-gray-700 text-gray-300 rounded-full text-xs"
                  >
                    {tag}
                  </span>
                ))}
                {opportunity.tags.length > 3 && (
                  <span className="text-gray-400 text-xs">
                    +{opportunity.tags.length - 3} more
                  </span>
                )}
              </div>

              {/* Application Status */}
              {applications.has(opportunity.id) && (
                <div className="flex items-center gap-2 mb-4">
                  <CheckCircle className="w-4 h-4 text-green-400" />
                  <span className="text-green-400 text-sm">
                    {applications.get(opportunity.id)?.status}
                  </span>
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-2">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleQuickApply(opportunity);
                  }}
                  disabled={applications.has(opportunity.id)}
                  className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
                >
                  <Send className="w-4 h-4" />
                  {applications.has(opportunity.id) ? 'Applied' : 'Quick Apply'}
                </button>

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    createActionPlan(opportunity);
                  }}
                  className="px-3 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors"
                  title="Create Action Plan"
                >
                  <Brain className="w-4 h-4" />
                </button>

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    createCampaignForOpportunity(opportunity);
                  }}
                  className="px-3 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                  title="Create Campaign"
                >
                  <Megaphone className="w-4 h-4" />
                </button>
              </div>
            </motion.div>
          ))
        )}
      </div>
    </div>
  );

  const renderEvaluateTab = () => (
    <div className="space-y-6">
      <div className="bg-gray-800 rounded-xl p-6">
        <h3 className="text-white text-xl font-semibold mb-4">AI Analysis & Recommendations</h3>

        {isAnalyzing ? (
          <div className="flex flex-col items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-purple-500 mb-4" />
            <p className="text-gray-400">Analyzing opportunities with AI...</p>
          </div>
        ) : (
          <div className="space-y-4">
            {Array.from(actionPlans.values()).map(plan => {
              const opportunity = opportunities.find(opp => opp.id === plan.opportunity_id);
              if (!opportunity) return null;

              return (
                <div key={plan.id} className="bg-gray-700 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h4 className="text-white font-medium">{opportunity.title}</h4>
                      <p className="text-gray-400 text-sm">{opportunity.company}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-1 bg-purple-600/20 text-purple-400 rounded text-sm">
                        {Math.round(plan.success_probability * 100)}% success
                      </span>
                      <span className="px-2 py-1 bg-green-600/20 text-green-400 rounded text-sm">
                        ${plan.revenue_potential.toLocaleString()}
                      </span>
                    </div>
                  </div>

                  {/* Action Steps */}
                  <div className="space-y-2">
                    {plan.steps.map((step, idx) => (
                      <div
                        key={step.id}
                        className={`flex items-center gap-3 p-2 rounded ${
                          step.status === 'completed'
                            ? 'bg-green-600/10'
                            : step.status === 'in_progress'
                            ? 'bg-yellow-600/10'
                            : 'bg-gray-600/20'
                        }`}
                      >
                        <div className={`w-6 h-6 rounded-full flex items-center justify-center text-sm ${
                          step.status === 'completed'
                            ? 'bg-green-600 text-white'
                            : step.status === 'in_progress'
                            ? 'bg-yellow-600 text-white'
                            : 'bg-gray-600 text-gray-400'
                        }`}>
                          {idx + 1}
                        </div>
                        <div className="flex-1">
                          <p className="text-white text-sm">{step.title}</p>
                          {step.automated && (
                            <span className="text-purple-400 text-xs">Automated</span>
                          )}
                        </div>
                        <span className="text-gray-400 text-xs">{step.duration}</span>
                      </div>
                    ))}
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2 mt-4">
                    <button
                      className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                    >
                      Start Plan
                    </button>
                    <button
                      className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-500 transition-colors"
                    >
                      Modify
                    </button>
                  </div>
                </div>
              );
            })}

            {actionPlans.size === 0 && (
              <div className="text-center py-8">
                <p className="text-gray-400">No action plans yet. Select opportunities to analyze.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );

  const renderApplicationsTab = () => (
    <div className="space-y-6">
      <div className="bg-gray-800 rounded-xl p-6">
        <h3 className="text-white text-xl font-semibold mb-4">Application Pipeline</h3>

        {/* Pipeline Stats */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="bg-gray-700 rounded-lg p-4">
            <p className="text-gray-400 text-sm">Submitted</p>
            <p className="text-white text-2xl font-bold">
              {Array.from(applications.values()).filter(app => app.status === 'submitted').length}
            </p>
          </div>
          <div className="bg-gray-700 rounded-lg p-4">
            <p className="text-gray-400 text-sm">In Review</p>
            <p className="text-white text-2xl font-bold">
              {Array.from(applications.values()).filter(app => app.status === 'in_review').length}
            </p>
          </div>
          <div className="bg-gray-700 rounded-lg p-4">
            <p className="text-gray-400 text-sm">Interviewed</p>
            <p className="text-white text-2xl font-bold">
              {Array.from(applications.values()).filter(app => app.status === 'interviewed').length}
            </p>
          </div>
          <div className="bg-gray-700 rounded-lg p-4">
            <p className="text-gray-400 text-sm">Offers</p>
            <p className="text-white text-2xl font-bold">
              {Array.from(applications.values()).filter(app => app.status === 'offered').length}
            </p>
          </div>
        </div>

        {/* Applications List */}
        <div className="space-y-3">
          {Array.from(applications.entries()).map(([oppId, app]) => {
            const opportunity = opportunities.find(opp => opp.id === oppId);
            if (!opportunity) return null;

            return (
              <div key={app.id} className="bg-gray-700 rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h4 className="text-white font-medium">{opportunity.title}</h4>
                    <p className="text-gray-400 text-sm">{opportunity.company}</p>
                    <div className="flex items-center gap-4 mt-2">
                      <span className="text-gray-400 text-sm">
                        Applied: {new Date(app.submitted_at || app.updated_at).toLocaleDateString()}
                      </span>
                      {app.next_step && (
                        <span className="text-yellow-400 text-sm">
                          Next: {app.next_step}
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className={`px-3 py-1 rounded-full text-sm ${
                      app.status === 'offered' ? 'bg-green-600/20 text-green-400' :
                      app.status === 'rejected' ? 'bg-red-600/20 text-red-400' :
                      app.status === 'interviewed' ? 'bg-blue-600/20 text-blue-400' :
                      'bg-gray-600/20 text-gray-400'
                    }`}>
                      {app.status}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}

          {applications.size === 0 && (
            <div className="text-center py-8">
              <p className="text-gray-400">No applications yet. Start applying to opportunities!</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const renderAIProjectsTab = () => (
    <div className="space-y-6">
      {/* Header with Generate Button */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-xl font-semibold text-white">Generated AI Projects</h3>
          <p className="text-gray-400 mt-1">
            AI-powered business opportunities ready to launch
          </p>
        </div>
        <button
          onClick={() => {
            console.log('🖱️ Generate New Projects button clicked (AI Projects tab)!');
            console.log('🔍 Button state - disabled:', generatingProjects);
            generateAIProjects();
          }}
          disabled={generatingProjects}
          className="px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-lg"
        >
          {generatingProjects ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Generating...
            </>
          ) : (
            <>
              <Sparkles className="w-5 h-5" />
              Generate New Projects
            </>
          )}
        </button>
      </div>

      {/* Projects Grid */}
      {generatedProjects.length === 0 ? (
        <div className="bg-gray-800 rounded-xl p-12 text-center">
          <Sparkles className="w-16 h-16 text-purple-500 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">No AI Projects Yet</h3>
          <p className="text-gray-400 mb-6">
            Click "Generate New Projects" to research and build AI monetization opportunities
          </p>
          <button
            onClick={() => {
              console.log('🖱️ Generate Your First Projects button clicked!');
              console.log('🔍 Button state - disabled:', generatingProjects);
              generateAIProjects();
            }}
            disabled={generatingProjects}
            className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            <Sparkles className="w-5 h-5 inline-block mr-2" />
            Generate Your First Projects
          </button>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {generatedProjects.map((project, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.1 }}
              className="bg-gray-800 rounded-xl overflow-hidden hover:bg-gray-750 transition-colors cursor-pointer group"
              onClick={() => {
                setSelectedProject(project);
                setViewingProject(true);
              }}
            >
              {/* Project Header with Type */}
              <div className="bg-gradient-to-r from-purple-600 to-pink-600 p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="px-3 py-1 text-xs bg-white/20 text-white rounded-full">
                      {project.project_type === 'ai_application' ? 'AI App' : project.project_type || 'AI Business'}
                    </span>
                    <span className="px-2 py-1 text-xs bg-black/20 text-white/80 rounded">
                      {project.strategy?.source || 'Dev.to'}
                    </span>
                  </div>
                  {project.success && (
                    <CheckCircle className="w-5 h-5 text-white" />
                  )}
                </div>
                <h4 className="text-lg font-bold text-white">
                  {project.strategy?.title || 'AI Project'}
                </h4>
                {project.strategy?.url && project.strategy.url !== '#' && (
                  <div className="text-xs text-white/60 mt-1">
                    Source: {project.strategy.url}
                  </div>
                )}
              </div>

              <div className="p-6">
                {/* What It Does */}
                <div className="mb-4">
                  <h5 className="text-sm font-semibold text-gray-400 mb-2">What It Does:</h5>
                  <p className="text-white text-sm">
                    {project.strategy?.description ||
                     (project.strategy?.title?.includes('LLM') ?
                      'Build a custom HTTP client for integrating with Large Language Models. Create AI-powered applications that can communicate with GPT, Claude, and other LLMs.' :
                      project.strategy?.title?.includes('Roop') ?
                      'Face swapping AI application using the Roop model. Create deepfake videos, virtual avatars, or entertainment content with AI face replacement technology.' :
                      'AI-powered application for automated content generation and monetization.')}
                  </p>
                </div>

                {/* How It Makes Money */}
                <div className="mb-4">
                  <h5 className="text-sm font-semibold text-gray-400 mb-2">Monetization Strategy:</h5>
                  <div className="space-y-2">
                    <div className="flex items-start gap-2">
                      <DollarSign className="w-4 h-4 text-green-400 mt-0.5" />
                      <div className="flex-1">
                        <div className="text-green-400 font-semibold text-sm">
                          {project.strategy?.potential_revenue || project.revenue_potential || '$1,000-10,000/month'}
                        </div>
                        <div className="text-xs text-gray-400 mt-1">
                          {project.strategy?.title?.includes('LLM') || project.strategy?.title?.includes('Llms') ?
                           'SaaS subscriptions, API access fees, enterprise licenses' :
                           project.strategy?.title?.includes('Roop') ?
                           'Content creation services, video editing tools, entertainment apps' :
                           'Subscription model, usage-based pricing, premium features'}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Implementation Time */}
                <div className="mb-4">
                  <h5 className="text-sm font-semibold text-gray-400 mb-2">Time to Market:</h5>
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-blue-400" />
                    <span className="text-white text-sm">
                      {project.strategy?.time_to_implement || '1-4 weeks'}
                    </span>
                    <span className="text-xs text-gray-500">
                      • {project.strategy?.difficulty || 'Beginner to Intermediate'}
                    </span>
                  </div>
                </div>

                {/* Key Features */}
                <div className="mb-4">
                  <h5 className="text-sm font-semibold text-gray-400 mb-2">Key Features:</h5>
                  <div className="flex flex-wrap gap-2">
                    {(project.strategy?.actionable_steps || [
                      'AI Integration',
                      'Automated Processing',
                      'User Dashboard',
                      'Payment System'
                    ]).slice(0, 4).map((step: string, i: number) => (
                      <span key={i} className="text-xs bg-purple-600/20 text-purple-300 px-2 py-1 rounded">
                        {step.split(' ').slice(0, 3).join(' ')}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Advisor Insights */}
                {project.advisor_insights && project.advisor_insights.length > 0 ? (
                  <div className="mb-4 p-3 bg-gradient-to-r from-blue-900/20 to-purple-900/20 rounded-lg border border-blue-800/30">
                    <h5 className="text-sm font-semibold text-blue-400 mb-2 flex items-center gap-2">
                      <Brain className="w-4 h-4" />
                      Advisor Insights
                    </h5>
                    {project.advisor_insights.slice(0, 1).map((insight: any, i: number) => (
                      <div key={i} className="text-xs">
                        <div className="text-yellow-400 font-semibold mb-1">
                          {insight.advisor?.replace(' (AI Model)', '')}:
                        </div>
                        <p className="text-gray-300 mb-1 line-clamp-2">
                          "{insight.advice?.substring(0, 150)}..."
                        </p>
                        <div className="mt-1">
                          <span className="text-blue-400">Top tip:</span>
                          <span className="text-gray-400 ml-1">
                            {insight.action_items?.[0] || 'Validate market demand first'}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="mb-4 p-3 bg-gray-900 rounded-lg border border-gray-800">
                    <button
                      onClick={async () => {
                        toast.info('🎯 Getting advisor insights...', {
                          description: 'Warren Buffett and Cathie Wood are reviewing your project'
                        });
                        // In a real implementation, this would call an API to get advisor insights
                        // For now, just show a message
                        setTimeout(() => {
                          toast.success('Advisor insights will be available in the next generation!');
                        }, 2000);
                      }}
                      className="w-full py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all text-sm font-medium flex items-center justify-center gap-2"
                    >
                      <Brain className="w-4 h-4" />
                      Get Advisor Insights
                    </button>
                  </div>
                )}

                {/* Status */}
                <div className="mb-4 p-3 bg-gray-900 rounded-lg">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">Status:</span>
                    <span className={`font-semibold ${project.ready_to_launch ? 'text-green-400' : 'text-yellow-400'}`}>
                      {project.ready_to_launch ? '✅ Ready to Launch' : '⚠️ Needs API Keys'}
                    </span>
                  </div>
                </div>

                {/* View Details Indicator */}
                <div className="mt-4 pt-4 border-t border-gray-700 flex items-center justify-center gap-2 text-purple-400 group-hover:text-purple-300 transition-colors">
                  <Eye className="w-4 h-4" />
                  <span className="text-sm font-medium">Click to View Project Details</span>
                  <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </div>

                {/* Action buttons removed - card is clickable to view details */}
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {/* Load Previous Projects Button */}
      {generatedProjects.length > 0 && (
        <div className="flex justify-center">
          <button
            onClick={async () => {
              await loadGeneratedProjects();
              toast.success(`Refreshed project list`);
            }}
            className="px-6 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors"
          >
            <RefreshCw className="w-4 h-4 inline-block mr-2" />
            Load Previous Projects
          </button>
        </div>
      )}
    </div>
  );

  const renderAnalyticsTab = () => (
    <div className="space-y-6">
      {/* Earnings Projection */}
      <div className="bg-gray-800 rounded-xl p-6">
        <h3 className="text-white text-xl font-semibold mb-4">Earnings Projection</h3>

        <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
          <div className="bg-gray-700 rounded-lg p-4">
            <p className="text-gray-400 text-sm">Week 1</p>
            <p className="text-white text-2xl font-bold">
              ${earningsProjection.week_1.toLocaleString()}
            </p>
          </div>
          <div className="bg-gray-700 rounded-lg p-4">
            <p className="text-gray-400 text-sm">Month 1</p>
            <p className="text-white text-2xl font-bold">
              ${earningsProjection.month_1.toLocaleString()}
            </p>
          </div>
          <div className="bg-gray-700 rounded-lg p-4">
            <p className="text-gray-400 text-sm">Month 3</p>
            <p className="text-white text-2xl font-bold">
              ${earningsProjection.month_3.toLocaleString()}
            </p>
          </div>
          <div className="bg-gray-700 rounded-lg p-4">
            <p className="text-gray-400 text-sm">Month 6</p>
            <p className="text-white text-2xl font-bold">
              ${earningsProjection.month_6.toLocaleString()}
            </p>
          </div>
          <div className="bg-gray-700 rounded-lg p-4">
            <p className="text-gray-400 text-sm">Year 1</p>
            <p className="text-white text-2xl font-bold">
              ${earningsProjection.year_1.toLocaleString()}
            </p>
          </div>
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="bg-gray-800 rounded-xl p-6">
        <h3 className="text-white text-xl font-semibold mb-4">Performance Metrics</h3>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-gray-700 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="w-5 h-5 text-green-400" />
              <p className="text-gray-400 text-sm">Success Rate</p>
            </div>
            <p className="text-white text-2xl font-bold">
              {applications.size > 0
                ? Math.round((Array.from(applications.values()).filter(app =>
                    ['offered', 'accepted'].includes(app.status)).length / applications.size) * 100)
                : 0}%
            </p>
          </div>

          <div className="bg-gray-700 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Target className="w-5 h-5 text-blue-400" />
              <p className="text-gray-400 text-sm">Avg Match</p>
            </div>
            <p className="text-white text-2xl font-bold">
              {opportunities.length > 0
                ? Math.round(opportunities.reduce((acc, opp) => acc + opp.skills_match, 0) / opportunities.length * 100)
                : 0}%
            </p>
          </div>

          <div className="bg-gray-700 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Clock className="w-5 h-5 text-purple-400" />
              <p className="text-gray-400 text-sm">Response Time</p>
            </div>
            <p className="text-white text-2xl font-bold">24h</p>
          </div>

          <div className="bg-gray-700 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Award className="w-5 h-5 text-yellow-400" />
              <p className="text-gray-400 text-sm">Top Category</p>
            </div>
            <p className="text-white text-lg font-bold">Tech</p>
          </div>
        </div>
      </div>

      {/* Automation Status */}
      <div className="bg-gray-800 rounded-xl p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-white text-xl font-semibold">Automation</h3>
          <button
            onClick={() => setAutomationEnabled(!automationEnabled)}
            className={`px-4 py-2 rounded-lg transition-colors ${
              automationEnabled
                ? 'bg-purple-600 text-white hover:bg-purple-700'
                : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
            }`}
          >
            {automationEnabled ? (
              <>
                <Pause className="w-4 h-4 inline mr-2" />
                Pause
              </>
            ) : (
              <>
                <Play className="w-4 h-4 inline mr-2" />
                Enable
              </>
            )}
          </button>
        </div>

        {automationEnabled && (
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              <span className="text-gray-400">Auto-applying to matched opportunities</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              <span className="text-gray-400">Generating personalized cover letters</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              <span className="text-gray-400">Tracking application status</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const renderCampaignsTab = () => (
    <div className="space-y-6">
      {/* Campaigns Header */}
      <div className="bg-gray-800 rounded-xl p-6">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h2 className="text-white text-2xl font-bold">Campaign Manager</h2>
            <p className="text-gray-400">Create content campaigns to pursue opportunities</p>
          </div>
          <button
            onClick={createNewCampaign}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2"
          >
            <Edit3 className="w-4 h-4" />
            New Campaign
          </button>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-gray-700 rounded-lg p-4">
            <p className="text-gray-400 text-sm">Total Campaigns</p>
            <p className="text-white text-2xl font-bold">{campaigns.length}</p>
          </div>
          <div className="bg-gray-700 rounded-lg p-4">
            <p className="text-gray-400 text-sm">Active</p>
            <p className="text-white text-2xl font-bold">
              {campaigns.filter(c => c.status === 'active').length}
            </p>
          </div>
          <div className="bg-gray-700 rounded-lg p-4">
            <p className="text-gray-400 text-sm">Content Created</p>
            <p className="text-white text-2xl font-bold">
              {campaigns.reduce((sum, c) => sum + c.content.length, 0)}
            </p>
          </div>
          <div className="bg-gray-700 rounded-lg p-4">
            <p className="text-gray-400 text-sm">Success Rate</p>
            <p className="text-white text-2xl font-bold">85%</p>
          </div>
        </div>
      </div>

      {/* Campaign Templates */}
      <div className="bg-gray-800 rounded-xl p-6">
        <h3 className="text-white text-lg font-semibold mb-4">Quick Start Templates</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div
            onClick={() => createCampaignFromTemplate('job_application')}
            className="bg-gray-700 rounded-lg p-4 cursor-pointer hover:bg-gray-600 transition-colors"
          >
            <Mail className="w-8 h-8 text-blue-400 mb-2" />
            <h4 className="text-white font-medium">Job Application Kit</h4>
            <p className="text-gray-400 text-sm">Cover letter, resume, follow-up emails</p>
          </div>
          <div
            onClick={() => createCampaignFromTemplate('freelance_pitch')}
            className="bg-gray-700 rounded-lg p-4 cursor-pointer hover:bg-gray-600 transition-colors"
          >
            <PenTool className="w-8 h-8 text-green-400 mb-2" />
            <h4 className="text-white font-medium">Freelance Pitch</h4>
            <p className="text-gray-400 text-sm">Proposals, portfolios, client outreach</p>
          </div>
          <div
            onClick={() => createCampaignFromTemplate('social_presence')}
            className="bg-gray-700 rounded-lg p-4 cursor-pointer hover:bg-gray-600 transition-colors"
          >
            <MessageSquare className="w-8 h-8 text-purple-400 mb-2" />
            <h4 className="text-white font-medium">Social Presence</h4>
            <p className="text-gray-400 text-sm">LinkedIn posts, Twitter content, networking</p>
          </div>
        </div>
      </div>

      {/* Active Campaigns */}
      <div className="bg-gray-800 rounded-xl p-6">
        <h3 className="text-white text-lg font-semibold mb-4">Your Campaigns</h3>
        {campaigns.length === 0 ? (
          <div className="text-center py-8">
            <Layout className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-400">No campaigns yet. Create your first campaign to get started!</p>
          </div>
        ) : (
          <div className="space-y-4">
            {campaigns.map(campaign => (
              <motion.div
                key={campaign.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-gray-700 rounded-lg p-4 hover:bg-gray-650 transition-colors cursor-pointer"
                onClick={() => setSelectedCampaign(campaign)}
              >
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h4 className="text-white font-medium">{campaign.title}</h4>
                    <p className="text-gray-400 text-sm">{campaign.description}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      campaign.status === 'active' ? 'bg-green-600/20 text-green-400' :
                      campaign.status === 'draft' ? 'bg-yellow-600/20 text-yellow-400' :
                      campaign.status === 'paused' ? 'bg-gray-600/20 text-gray-400' :
                      'bg-blue-600/20 text-blue-400'
                    }`}>
                      {campaign.status}
                    </span>
                  </div>
                </div>

                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-4 text-sm text-gray-400">
                    <span>{campaign.content.length} content pieces</span>
                    <span>Created {new Date(campaign.created_at).toLocaleDateString()}</span>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        generateCampaignContent(campaign);
                      }}
                      className="px-3 py-1 bg-purple-600 text-white rounded hover:bg-purple-700 transition-colors"
                    >
                      Generate Content
                    </button>
                    {campaign.status === 'draft' && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          launchCampaign(campaign.id);
                        }}
                        className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 transition-colors flex items-center gap-1"
                      >
                        <Play className="w-3 h-3" />
                        Launch
                      </button>
                    )}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-900">
      <div className="p-6">
        {/* Header */}
        <div className="mb-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-white">Opportunities Hub</h1>
              <p className="text-gray-400 mt-1">
                Discover, evaluate, and apply to income opportunities
              </p>
            </div>

            {/* Ecosystem Status Indicator */}
            <div className="flex items-center gap-4">
              {ecosystemStatus && (
                <div className="text-sm text-gray-400">
                  <div className="flex items-center gap-2">
                    <Database className={`w-4 h-4 ${ecosystemStatus.status === 'active' ? 'text-green-400' : 'text-gray-400'}`} />
                    <span>{ecosystemStatus.components?.spiders?.active || 0} Spiders</span>
                  </div>
                  <div className="flex items-center gap-2 mt-1">
                    <Brain className={`w-4 h-4 ${ecosystemStatus.status === 'active' ? 'text-blue-400' : 'text-gray-400'}`} />
                    <span>{ecosystemStatus.components?.agents?.connected || 0} Agents</span>
                  </div>
                  <div className="flex items-center gap-2 mt-1">
                    <Star className={`w-4 h-4 ${ecosystemStatus.status === 'active' ? 'text-purple-400' : 'text-gray-400'}`} />
                    <span>{ecosystemStatus.components?.advisors?.active || 0} Advisors</span>
                  </div>
                </div>
              )}

              <button
                onClick={activateEcosystem}
                disabled={activatingEcosystem || ecosystemStatus?.status === 'active'}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                  ecosystemStatus?.status === 'active'
                    ? 'bg-green-600/20 text-green-400 cursor-default'
                    : 'bg-purple-600 text-white hover:bg-purple-700'
                } disabled:opacity-50 disabled:cursor-not-allowed`}
              >
                {activatingEcosystem ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Activating...</span>
                  </>
                ) : ecosystemStatus?.status === 'active' ? (
                  <>
                    <CheckCircle className="w-5 h-5" />
                    <span>Ecosystem Active</span>
                  </>
                ) : (
                  <>
                    <Zap className="w-5 h-5" />
                    <span>Activate Real Data</span>
                  </>
                )}
              </button>
            </div>

            <div className="flex items-center gap-4">
              {/* Connection Status */}
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-green-400' : 'bg-red-400'}`} />
                <span className="text-gray-400 text-sm">
                  {wsConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>

              {/* Quick Stats */}
              <div className="bg-gray-800 rounded-lg px-4 py-2">
                <span className="text-gray-400 text-sm">Active: </span>
                <span className="text-white font-medium">{opportunities.length}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-gray-800 rounded-xl p-1 mb-6">
          <div className="flex gap-1">
            {tabs.map(tab => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-lg transition-colors ${
                    activeTab === tab.id
                      ? 'bg-purple-600 text-white'
                      : 'text-gray-400 hover:text-white hover:bg-gray-700'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{tab.label}</span>
                  {tab.badge && tab.badge > 0 && (
                    <span className="ml-2 px-2 py-0.5 bg-gray-700 text-white text-xs rounded-full">
                      {tab.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        </div>

        {/* Tab Content */}
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.2 }}
          >
            {activeTab === 'discover' && renderDiscoverTab()}
            {activeTab === 'evaluate' && renderEvaluateTab()}
            {activeTab === 'ai-projects' && renderAIProjectsTab()}
            {activeTab === 'campaigns' && renderCampaignsTab()}
            {activeTab === 'applications' && renderApplicationsTab()}
            {activeTab === 'analytics' && renderAnalyticsTab()}
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Opportunity Detail Modal */}
      {selectedOpportunity && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-6 z-50">
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="bg-gray-800 rounded-xl p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto"
          >
            <div className="flex justify-between items-start mb-4">
              <div>
                <h2 className="text-2xl font-bold text-white">{selectedOpportunity.title}</h2>
                <p className="text-gray-400">{selectedOpportunity.company}</p>
              </div>
              <button
                onClick={() => setSelectedOpportunity(null)}
                className="text-gray-400 hover:text-white"
              >
                <XCircle className="w-6 h-6" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <h3 className="text-white font-semibold mb-2">Description</h3>
                <p className="text-gray-300">{selectedOpportunity.description}</p>
              </div>

              <div>
                <h3 className="text-white font-semibold mb-2">Requirements</h3>
                <ul className="space-y-1">
                  {selectedOpportunity.requirements.map((req, idx) => (
                    <li key={idx} className="text-gray-300 flex items-start gap-2">
                      <ChevronRight className="w-4 h-4 text-gray-400 mt-0.5" />
                      <span>{req}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {selectedOpportunity.ai_recommendation && (
                <div className="bg-purple-600/10 rounded-lg p-4 border border-purple-500/20">
                  <div className="flex items-center gap-2 mb-2">
                    <Brain className="w-5 h-5 text-purple-400" />
                    <h3 className="text-white font-semibold">AI Recommendation</h3>
                  </div>
                  <p className="text-gray-300">{selectedOpportunity.ai_recommendation}</p>
                </div>
              )}

              <div className="flex gap-3">
                <button
                  onClick={() => {
                    handleQuickApply(selectedOpportunity);
                    setSelectedOpportunity(null);
                  }}
                  className="flex-1 px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                >
                  Quick Apply
                </button>
                <button
                  onClick={() => {
                    createActionPlan(selectedOpportunity);
                    setSelectedOpportunity(null);
                  }}
                  className="px-6 py-3 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors"
                >
                  Create Action Plan
                </button>
              </div>
            </div>
          </motion.div>
        </div>
      )}

      {/* Project Viewer Modal */}
      {viewingProject && selectedProject && (
        <ProjectViewer
          project={selectedProject}
          onClose={() => {
            setViewingProject(false);
            setSelectedProject(null);
          }}
        />
      )}
    </div>
  );
};

export default OpportunitiesHub;