import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Separator } from '@/components/ui/separator';
import {
  Brain, Target, Shield, TrendingUp, Activity, Database,
  Globe, Zap, BarChart3, DollarSign, Home, Briefcase,
  Bitcoin, LineChart, Trophy, AlertTriangle, Clock,
  RefreshCw, Settings, Search, Filter, Grid3x3,
  BookOpen, Upload, Link, FileText, Image, Video,
  Star, ThumbsUp, ThumbsDown, MessageSquare,
  Beaker, BarChart,
  CheckCircle, AlertCircle, Info, TrendingDown,
  Calendar, Download, Plus, Minus, X, Edit3,
  Save, Share2, Copy, Eye, Trash2, Archive,
  Users, Sparkles
} from 'lucide-react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { toast } from 'sonner';

// Import existing intelligence components
import { IntelligencePanel } from '@/components/intelligence/IntelligencePanel';
import { MemorySearch } from '@/components/intelligence/MemorySearch';
import { PatternLibrary } from '@/components/intelligence/PatternLibrary';
import { PredictionEngine } from '@/components/intelligence/PredictionEngine';
import { OpportunityScanner } from '@/components/intelligence/OpportunityScanner';
import { RiskManager } from '@/components/intelligence/RiskManager';
import { CollaborativeDecision } from '@/components/intelligence/CollaborativeDecision';
import { OutcomePrediction } from '@/components/intelligence/OutcomePrediction';
import { AutoExecution } from '@/components/intelligence/AutoExecution';

// Import new real-time intelligence components
import { IntelligenceDashboard } from '@/components/intelligence/IntelligenceDashboard';
import { RealTimeIntelligencePanel } from '@/components/intelligence/RealTimeIntelligencePanel';
import { LiveOpportunityStream } from '@/components/intelligence/LiveOpportunityStream';

import {
  getUniversalIntelligence,
  searchMemory,
  getPatternLibrary,
  submitIntelligenceFeedback,
  type DecisionContext,
  type IntelligenceResult
} from '@/features/sports/api/sports';

import '../styles/gaming-theme.css';

// Domain configurations
const DOMAINS = {
  SPORTS_BETTING: {
    name: 'Sports Betting',
    icon: Trophy,
    color: 'text-green-500',
    bgColor: 'bg-green-500/10',
    borderColor: 'border-green-500/20',
    neonColor: 'gaming-neon-green'
  },
  TRADING: {
    name: 'Stock Trading',
    icon: LineChart,
    color: 'text-blue-500',
    bgColor: 'bg-blue-500/10',
    borderColor: 'border-blue-500/20',
    neonColor: 'gaming-neon-cyan'
  },
  CRYPTO: {
    name: 'Cryptocurrency',
    icon: Bitcoin,
    color: 'text-orange-500',
    bgColor: 'bg-orange-500/10',
    borderColor: 'border-orange-500/20',
    neonColor: 'gaming-neon-orange'
  },
  REAL_ESTATE: {
    name: 'Real Estate',
    icon: Home,
    color: 'text-purple-500',
    bgColor: 'bg-purple-500/10',
    borderColor: 'border-purple-500/20',
    neonColor: 'gaming-neon-purple'
  },
  BUSINESS: {
    name: 'Business Decisions',
    icon: Briefcase,
    color: 'text-indigo-500',
    bgColor: 'bg-indigo-500/10',
    borderColor: 'border-indigo-500/20',
    neonColor: 'gaming-neon-indigo'
  }
};

interface UniversalDecision {
  id: string;
  domain: keyof typeof DOMAINS;
  entity: string;
  description: string;
  timestamp: string;
  intelligence?: IntelligenceResult;
  status: 'pending' | 'analyzing' | 'ready' | 'executed';
  outcome?: 'success' | 'failure' | 'neutral';
  roi?: number;
}

interface PortfolioMetrics {
  totalValue: number;
  dailyChange: number;
  dailyChangePercent: number;
  winRate: number;
  activePositions: number;
  riskScore: number;
}

interface ResearchSource {
  id: string;
  title: string;
  url?: string;
  type: 'url' | 'pdf' | 'text' | 'video';
  status: 'pending' | 'processing' | 'completed' | 'error';
  content?: string;
  summary?: string;
}

interface DiagnosticResult {
  id: string;
  promptText: string;
  status: 'analyzing' | 'completed' | 'error';
  metrics: {
    tokenCount: number;
    readabilityScore: number;
    clarityScore: number;
    issues: string[];
  };
  suggestions: string[];
  timestamp: string;
}

interface FeedbackData {
  id: string;
  type: string;
  rating: number;
  comment: string;
  timestamp: string;
  contentType: 'text' | 'image' | 'video' | 'decision';
  outcome?: 'success' | 'failure' | 'neutral';
}

export function UnifiedCommandCenter() {
  const navigate = useNavigate();

  // Main state
  const [activeMainTab, setActiveMainTab] = useState('dashboard');
  const [selectedDomain, setSelectedDomain] = useState<keyof typeof DOMAINS>('SPORTS_BETTING');
  const [decisions, setDecisions] = useState<UniversalDecision[]>([]);
  const [portfolio, setPortfolio] = useState<PortfolioMetrics>({
    totalValue: 50000,
    dailyChange: 2340,
    dailyChangePercent: 4.92,
    winRate: 0.68,
    activePositions: 12,
    riskScore: 0.42
  });

  // Intelligence Hub state
  const [intelligenceTab, setIntelligenceTab] = useState('analysis');
  const [universalAnalysis, setUniversalAnalysis] = useState<IntelligenceResult | null>(null);
  const [memoryResults, setMemoryResults] = useState<any[]>([]);
  const [patterns, setPatterns] = useState<any[]>([]);

  // Knowledge Center state
  const [knowledgeTab, setKnowledgeTab] = useState('sources');
  const [researchSources, setResearchSources] = useState<ResearchSource[]>([]);
  const [knowledgeBase, setKnowledgeBase] = useState<any[]>([]);
  const [factChecks, setFactChecks] = useState<any[]>([]);

  // Analytics & Diagnostics state
  const [diagnosticsTab, setDiagnosticsTab] = useState('dashboard');
  const [diagnosticResults, setDiagnosticResults] = useState<DiagnosticResult[]>([]);
  const [systemMetrics, setSystemMetrics] = useState<any>({
    totalAnalyses: 1247,
    avgTokens: 1842,
    avgClarity: 0.73,
    activePrompts: 42
  });

  // Feedback & Learning state
  const [feedbackTab, setFeedbackTab] = useState('analytics');
  const [feedbackData, setFeedbackData] = useState<FeedbackData[]>([]);
  const [feedbackAnalytics, setFeedbackAnalytics] = useState<any>({
    totalFeedback: 3247,
    avgRating: 4.2,
    positiveRate: 0.78,
    improvementTrends: []
  });

  const [loading, setLoading] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  // WebSocket for real-time updates
  const { isConnected } = useWebSocket({
    url: '/ws/command-center/',
    onMessage: (data: any) => {
      if (data.type === 'decision_update') {
        updateDecision(data.decision);
      } else if (data.type === 'portfolio_update') {
        setPortfolio(data.portfolio);
      }
    }
  });

  const updateDecision = (updatedDecision: UniversalDecision) => {
    setDecisions(prev => prev.map(d =>
      d.id === updatedDecision.id ? updatedDecision : d
    ));
  };

  const analyzeDecision = async (decision: UniversalDecision) => {
    setLoading(true);
    updateDecision({ ...decision, status: 'analyzing' });

    try {
      const context: DecisionContext = {
        domain: decision.domain,
        entity_id: decision.id,
        data_points: {
          entity: decision.entity,
          description: decision.description,
          timestamp: decision.timestamp
        },
        risk_level: 0.5,
        time_horizon: 'medium'
      };

      const intelligence = await getUniversalIntelligence(context);
      updateDecision({ ...decision, intelligence, status: 'ready' });
      setUniversalAnalysis(intelligence);
    } catch (error) {
      console.error('Analysis failed:', error);
    } finally {
      setLoading(false);
    }
  };

  // Mock data initialization
  useEffect(() => {
    const mockDecisions: UniversalDecision[] = [
      {
        id: 'dec_001',
        domain: 'SPORTS_BETTING',
        entity: 'Lakers vs Warriors',
        description: 'NBA game with favorable spread movement',
        timestamp: new Date().toISOString(),
        status: 'ready'
      },
      {
        id: 'dec_002',
        domain: 'CRYPTO',
        entity: 'BTC/USD',
        description: 'Breakout pattern forming at key resistance',
        timestamp: new Date().toISOString(),
        status: 'pending'
      },
      {
        id: 'dec_003',
        domain: 'TRADING',
        entity: 'NVDA',
        description: 'Earnings momentum play with options',
        timestamp: new Date().toISOString(),
        status: 'analyzing'
      },
      {
        id: 'dec_004',
        domain: 'REAL_ESTATE',
        entity: '123 Main St, Austin TX',
        description: 'Undervalued property in growth area',
        timestamp: new Date().toISOString(),
        status: 'ready'
      }
    ];

    // Mock research sources
    const mockSources: ResearchSource[] = [
      {
        id: 'src_001',
        title: 'Sports Betting Analytics Research',
        url: 'https://example.com/research1',
        type: 'pdf',
        status: 'completed',
        summary: 'Comprehensive analysis of betting patterns'
      },
      {
        id: 'src_002',
        title: 'Market Analysis Video',
        type: 'video',
        status: 'processing',
      }
    ];

    // Mock diagnostic results
    const mockDiagnostics: DiagnosticResult[] = [
      {
        id: 'diag_001',
        promptText: 'Analyze this sports betting decision...',
        status: 'completed',
        metrics: {
          tokenCount: 1247,
          readabilityScore: 0.82,
          clarityScore: 0.76,
          issues: ['Verbose instructions', 'Ambiguous context']
        },
        suggestions: ['Reduce token count by 20%', 'Add specific examples'],
        timestamp: new Date().toISOString()
      }
    ];

    // Mock feedback data
    const mockFeedback: FeedbackData[] = [
      {
        id: 'fb_001',
        type: 'decision_outcome',
        rating: 4,
        comment: 'Good analysis, helped make profitable decision',
        timestamp: new Date().toISOString(),
        contentType: 'decision',
        outcome: 'success'
      }
    ];

    setDecisions(mockDecisions);
    setResearchSources(mockSources);
    setDiagnosticResults(mockDiagnostics);
    setFeedbackData(mockFeedback);
  }, []);

  const getStatusColor = (status: UniversalDecision['status']) => {
    switch (status) {
      case 'pending': return 'bg-yellow-500';
      case 'analyzing': return 'bg-blue-500 animate-pulse';
      case 'ready': return 'bg-green-500';
      case 'executed': return 'bg-gray-500';
      default: return 'bg-gray-500';
    }
  };

  const getRiskColor = (risk: number) => {
    if (risk < 0.3) return 'text-green-500';
    if (risk < 0.6) return 'text-yellow-500';
    return 'text-red-500';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-dark-950 via-dark-900 to-dark-950 p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent">
              Universal Decision Command Center
            </h1>
            <p className="text-gray-400 mt-2">
              AI-powered decision intelligence, research, analytics, and learning
            </p>
          </div>
          <div className="flex items-center gap-4">
            <Badge variant="outline" className="px-3 py-1">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'} mr-2 animate-pulse`} />
              {isConnected ? 'Live' : 'Offline'}
            </Badge>
            <Button variant="outline" size="icon">
              <Settings className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Portfolio Overview */}
        <div className="grid grid-cols-1 md:grid-cols-6 gap-4 mb-6">
          <Card className="gaming-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-400">Portfolio Value</span>
                <DollarSign className="h-4 w-4 text-green-500" />
              </div>
              <p className="text-2xl font-bold mt-2">
                ${portfolio.totalValue.toLocaleString()}
              </p>
              <p className={`text-sm mt-1 ${portfolio.dailyChange >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                {portfolio.dailyChange >= 0 ? '+' : ''}{portfolio.dailyChangePercent.toFixed(2)}%
              </p>
            </CardContent>
          </Card>

          <Card className="gaming-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-400">Win Rate</span>
                <Trophy className="h-4 w-4 text-yellow-500" />
              </div>
              <p className="text-2xl font-bold mt-2">
                {(portfolio.winRate * 100).toFixed(0)}%
              </p>
              <Progress value={portfolio.winRate * 100} className="mt-2 h-1" />
            </CardContent>
          </Card>

          <Card className="gaming-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-400">Active Positions</span>
                <Activity className="h-4 w-4 text-blue-500" />
              </div>
              <p className="text-2xl font-bold mt-2">{portfolio.activePositions}</p>
              <p className="text-sm text-gray-400 mt-1">Across 5 domains</p>
            </CardContent>
          </Card>

          <Card className="gaming-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-400">Risk Score</span>
                <Shield className="h-4 w-4 text-orange-500" />
              </div>
              <p className={`text-2xl font-bold mt-2 ${getRiskColor(portfolio.riskScore)}`}>
                {(portfolio.riskScore * 100).toFixed(0)}%
              </p>
              <Progress value={portfolio.riskScore * 100} className="mt-2 h-1" />
            </CardContent>
          </Card>

          <Card className="gaming-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-400">Research Sources</span>
                <BookOpen className="h-4 w-4 text-purple-500" />
              </div>
              <p className="text-2xl font-bold mt-2">{researchSources.length}</p>
              <p className="text-sm text-gray-400 mt-1">Active sources</p>
            </CardContent>
          </Card>

          <Card className="gaming-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-400">Agent Consensus</span>
                <Zap className="h-4 w-4 text-yellow-500" />
              </div>
              <p className="text-2xl font-bold mt-2">82%</p>
              <p className="text-sm text-green-500 mt-1">Strong Signal</p>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Main Content */}
      <Tabs value={activeMainTab} onValueChange={setActiveMainTab} className="space-y-6">
        <TabsList className="grid grid-cols-5 lg:grid-cols-10 w-full max-w-7xl">
          <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
          <TabsTrigger value="decisions">Decisions</TabsTrigger>
          <TabsTrigger value="intelligence">Intelligence</TabsTrigger>
          <TabsTrigger value="prediction">Prediction</TabsTrigger>
          <TabsTrigger value="scanner">Scanner</TabsTrigger>
          <TabsTrigger value="risk">Risk</TabsTrigger>
          <TabsTrigger value="collaborate">Collaborate</TabsTrigger>
          <TabsTrigger value="outcomes">Outcomes</TabsTrigger>
          <TabsTrigger value="execute">Execute</TabsTrigger>
          <TabsTrigger value="knowledge">Knowledge</TabsTrigger>
        </TabsList>

        {/* Dashboard Tab */}
        <TabsContent value="dashboard" className="space-y-6">
          {/* Live Intelligence Stream */}
          <Alert className="border-blue-500/50 bg-gradient-to-r from-blue-900/20 to-purple-900/20">
            <Brain className="h-4 w-4" />
            <AlertDescription>
              <span className="font-bold text-blue-400">SKYNET INTELLIGENCE ACTIVE:</span> Real-time market analysis across {Object.keys(DOMAINS).length} domains with 102 specialized agents
            </AlertDescription>
          </Alert>

          <RealTimeIntelligencePanel />

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Recent Decisions */}
            <Card className="gaming-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="h-5 w-5 text-blue-500" />
                  Recent Decisions
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {decisions.slice(0, 3).map(decision => {
                    const domainConfig = DOMAINS[decision.domain];
                    const Icon = domainConfig.icon;

                    return (
                      <div key={decision.id} className="flex items-center justify-between p-3 border border-gray-700 rounded-lg">
                        <div className="flex items-center gap-3">
                          <Icon className={`h-5 w-5 ${domainConfig.color}`} />
                          <div>
                            <p className="font-medium">{decision.entity}</p>
                            <p className="text-sm text-gray-400">{domainConfig.name}</p>
                          </div>
                        </div>
                        <Badge className={`${getStatusColor(decision.status)} text-white`}>
                          {decision.status}
                        </Badge>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>

            {/* Live Opportunity Preview */}
            <Card className="gaming-card border-green-500/30 bg-gradient-to-br from-green-900/10 to-transparent">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Zap className="h-5 w-5 text-green-500" />
                  Live Opportunities
                  <Badge className="bg-green-500 text-white ml-auto">LIVE</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 border border-green-700/50 rounded-lg bg-green-900/10">
                    <div className="flex items-center gap-3">
                      <Target className="h-4 w-4 text-green-500" />
                      <div>
                        <p className="font-medium text-sm">NBA Arbitrage</p>
                        <p className="text-xs text-gray-400">Lakers vs Warriors</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-bold text-green-500">+4.2%</p>
                      <p className="text-xs text-gray-400">85% conf</p>
                    </div>
                  </div>
                  <div className="flex items-center justify-between p-3 border border-blue-700/50 rounded-lg bg-blue-900/10">
                    <div className="flex items-center gap-3">
                      <TrendingUp className="h-4 w-4 text-blue-500" />
                      <div>
                        <p className="font-medium text-sm">Crypto Pattern</p>
                        <p className="text-xs text-gray-400">BTC Ascending Triangle</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-bold text-blue-500">+3.8%</p>
                      <p className="text-xs text-gray-400">72% conf</p>
                    </div>
                  </div>
                  <Button
                    size="sm"
                    className="w-full"
                    onClick={() => setActiveMainTab('scanner')}
                  >
                    View All Opportunities
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3">
            <Button
              variant="outline"
              className="h-20 flex-col gap-1"
              onClick={() => setActiveMainTab('decisions')}
            >
              <Target className="h-5 w-5" />
              <span className="text-xs">Decisions</span>
            </Button>
            <Button
              variant="outline"
              className="h-20 flex-col gap-1"
              onClick={() => setActiveMainTab('intelligence')}
            >
              <Brain className="h-5 w-5" />
              <span className="text-xs">Intelligence</span>
            </Button>
            <Button
              variant="outline"
              className="h-20 flex-col gap-1 bg-gradient-to-br from-purple-500/10 to-pink-500/10 border-purple-500/30"
              onClick={() => setActiveMainTab('prediction')}
            >
              <Sparkles className="h-5 w-5 text-purple-500" />
              <span className="text-xs">Predictions</span>
            </Button>
            <Button
              variant="outline"
              className="h-20 flex-col gap-1 bg-gradient-to-br from-green-500/10 to-blue-500/10 border-green-500/30"
              onClick={() => setActiveMainTab('scanner')}
            >
              <Zap className="h-5 w-5 text-green-500" />
              <span className="text-xs">Scanner</span>
            </Button>
            <Button
              variant="outline"
              className="h-20 flex-col gap-1 bg-gradient-to-br from-red-500/10 to-yellow-500/10 border-red-500/30"
              onClick={() => setActiveMainTab('risk')}
            >
              <Shield className="h-5 w-5 text-red-500" />
              <span className="text-xs">Risk</span>
            </Button>
            <Button
              variant="outline"
              className="h-20 flex-col gap-1 bg-gradient-to-br from-blue-500/10 to-green-500/10 border-blue-500/30"
              onClick={() => setActiveMainTab('collaborate')}
            >
              <Users className="h-5 w-5 text-blue-500" />
              <span className="text-xs">Collaborate</span>
            </Button>
            <Button
              variant="outline"
              className="h-20 flex-col gap-1 bg-gradient-to-br from-yellow-500/10 to-orange-500/10 border-yellow-500/30"
              onClick={() => setActiveMainTab('outcomes')}
            >
              <BarChart3 className="h-5 w-5 text-yellow-500" />
              <span className="text-xs">Outcomes</span>
            </Button>
            <Button
              variant="outline"
              className="h-20 flex-col gap-1 bg-gradient-to-br from-orange-500/10 to-red-500/10 border-orange-500/30"
              onClick={() => setActiveMainTab('execute')}
            >
              <Zap className="h-5 w-5 text-orange-500" />
              <span className="text-xs">Execute</span>
            </Button>
          </div>
        </TabsContent>

        {/* Active Decisions Tab */}
        <TabsContent value="decisions" className="space-y-6">
          {/* Domain Selector */}
          <div className="flex items-center gap-2 mb-6">
            {Object.entries(DOMAINS).map(([key, config]) => {
              const Icon = config.icon;
              return (
                <Button
                  key={key}
                  variant={selectedDomain === key ? 'default' : 'outline'}
                  className={`${selectedDomain === key ? config.bgColor : ''}`}
                  onClick={() => setSelectedDomain(key as keyof typeof DOMAINS)}
                >
                  <Icon className={`h-4 w-4 mr-2 ${config.color}`} />
                  {config.name}
                </Button>
              );
            })}
          </div>

          {/* View Toggle */}
          <div className="flex justify-between items-center">
            <div className="flex gap-2">
              <Button variant="outline" size="sm">
                <Filter className="h-4 w-4 mr-2" />
                Filter
              </Button>
              <Button variant="outline" size="sm">
                <Search className="h-4 w-4 mr-2" />
                Search
              </Button>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
            >
              <Grid3x3 className="h-4 w-4" />
            </Button>
          </div>

          {/* Decisions Grid */}
          <div className={viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4' : 'space-y-4'}>
            {decisions.filter(d => selectedDomain === 'SPORTS_BETTING' || d.domain === selectedDomain).map(decision => {
              const domainConfig = DOMAINS[decision.domain];
              const Icon = domainConfig.icon;

              return (
                <Card key={decision.id} className={`gaming-card border ${domainConfig.borderColor}`}>
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-2">
                        <div className={`p-2 rounded-lg ${domainConfig.bgColor}`}>
                          <Icon className={`h-5 w-5 ${domainConfig.color}`} />
                        </div>
                        <div>
                          <h3 className="font-semibold">{decision.entity}</h3>
                          <p className="text-xs text-gray-400">{domainConfig.name}</p>
                        </div>
                      </div>
                      <Badge className={`${getStatusColor(decision.status)} text-white`}>
                        {decision.status}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <p className="text-sm text-gray-300">{decision.description}</p>

                    {decision.intelligence && (
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-gray-400">Action</span>
                          <Badge variant="outline">
                            {decision.intelligence.primary_action}
                          </Badge>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-gray-400">Confidence</span>
                          <span className="text-sm font-bold">
                            {(decision.intelligence.confidence * 100).toFixed(0)}%
                          </span>
                        </div>
                        <Progress value={decision.intelligence.confidence * 100} className="h-1" />

                        {decision.intelligence.position_sizing && (
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-gray-400">Recommended</span>
                            <span className="font-bold text-green-500">
                              ${decision.intelligence.position_sizing.recommended_stake}
                            </span>
                          </div>
                        )}
                      </div>
                    )}

                    <div className="flex gap-2">
                      {decision.status === 'pending' && (
                        <Button
                          size="sm"
                          className="flex-1"
                          onClick={() => analyzeDecision(decision)}
                          disabled={loading}
                        >
                          <Brain className="h-4 w-4 mr-2" />
                          Analyze
                        </Button>
                      )}
                      {decision.status === 'ready' && (
                        <>
                          <Button size="sm" variant="default" className="flex-1">
                            <Zap className="h-4 w-4 mr-2" />
                            Execute
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            className="flex-1"
                            onClick={() => navigate(`/decision/${decision.domain}/${decision.id}`)}
                          >
                            <Target className="h-4 w-4 mr-2" />
                            Details
                          </Button>
                        </>
                      )}
                      {decision.status === 'analyzing' && (
                        <div className="flex-1 text-center">
                          <RefreshCw className="h-4 w-4 animate-spin mx-auto" />
                          <p className="text-xs text-gray-400 mt-1">Analyzing...</p>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </TabsContent>

        {/* Intelligence Hub Tab */}
        <TabsContent value="intelligence" className="space-y-6">
          <RealTimeIntelligencePanel />
        </TabsContent>

        {/* Prediction Engine Tab */}
        <TabsContent value="prediction" className="space-y-6">
          <PredictionEngine />
        </TabsContent>

        {/* Opportunity Scanner Tab */}
        <TabsContent value="scanner" className="space-y-6">
          <LiveOpportunityStream />
        </TabsContent>

        {/* Risk Management Tab */}
        <TabsContent value="risk" className="space-y-6">
          <RiskManager />
        </TabsContent>

        {/* Collaborative Decision Tab */}
        <TabsContent value="collaborate" className="space-y-6">
          <CollaborativeDecision />
        </TabsContent>

        {/* Outcome Prediction Tab */}
        <TabsContent value="outcomes" className="space-y-6">
          <OutcomePrediction />
        </TabsContent>

        {/* Auto Execution Tab */}
        <TabsContent value="execute" className="space-y-6">
          <AutoExecution />
        </TabsContent>

        {/* Knowledge Center Tab */}
        <TabsContent value="knowledge" className="space-y-6">
          <Tabs value={knowledgeTab} onValueChange={setKnowledgeTab}>
            <TabsList>
              <TabsTrigger value="sources">Research Sources</TabsTrigger>
              <TabsTrigger value="knowledge-base">Knowledge Base</TabsTrigger>
              <TabsTrigger value="fact-checker">Fact Checker</TabsTrigger>
              <TabsTrigger value="library">Document Library</TabsTrigger>
            </TabsList>

            <TabsContent value="sources" className="space-y-6">
              <div className="flex justify-between items-center">
                <h3 className="text-xl font-semibold">Research Sources</h3>
                <div className="flex gap-2">
                  <Button size="sm">
                    <Plus className="h-4 w-4 mr-2" />
                    Add URL
                  </Button>
                  <Button size="sm">
                    <Upload className="h-4 w-4 mr-2" />
                    Upload File
                  </Button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {researchSources.map(source => (
                  <Card key={source.id} className="gaming-card">
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center gap-2">
                          {source.type === 'url' && <Link className="h-4 w-4 text-blue-500" />}
                          {source.type === 'pdf' && <FileText className="h-4 w-4 text-red-500" />}
                          {source.type === 'video' && <Video className="h-4 w-4 text-purple-500" />}
                          <span className="text-sm font-medium">{source.type.toUpperCase()}</span>
                        </div>
                        <Badge
                          className={`${
                            source.status === 'completed' ? 'bg-green-500' :
                            source.status === 'processing' ? 'bg-blue-500 animate-pulse' :
                            source.status === 'error' ? 'bg-red-500' :
                            'bg-yellow-500'
                          } text-white`}
                        >
                          {source.status}
                        </Badge>
                      </div>

                      <h4 className="font-medium mb-2">{source.title}</h4>
                      {source.url && (
                        <p className="text-xs text-gray-400 mb-2 truncate">{source.url}</p>
                      )}
                      {source.summary && (
                        <p className="text-sm text-gray-300">{source.summary}</p>
                      )}

                      <div className="flex gap-2 mt-3">
                        <Button size="sm" variant="outline">
                          <Eye className="h-3 w-3 mr-1" />
                          View
                        </Button>
                        <Button size="sm" variant="outline">
                          <Edit3 className="h-3 w-3 mr-1" />
                          Edit
                        </Button>
                        <Button size="sm" variant="outline">
                          <Trash2 className="h-3 w-3 mr-1" />
                          Remove
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </TabsContent>

            <TabsContent value="knowledge-base" className="space-y-6">
              <Card className="gaming-card">
                <CardHeader>
                  <CardTitle>Knowledge Base</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex gap-2">
                      <Input placeholder="Search knowledge base..." className="flex-1" />
                      <Button>
                        <Search className="h-4 w-4" />
                      </Button>
                    </div>

                    <div className="text-center py-12 text-gray-400">
                      <Database className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>Knowledge base entries will appear here</p>
                      <Button className="mt-4">
                        <Plus className="h-4 w-4 mr-2" />
                        Add Knowledge Entry
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="fact-checker" className="space-y-6">
              <Card className="gaming-card">
                <CardHeader>
                  <CardTitle>Fact Checker</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <Textarea
                      placeholder="Enter statement or claim to fact-check..."
                      className="min-h-32"
                    />
                    <Button className="w-full">
                      <CheckCircle className="h-4 w-4 mr-2" />
                      Verify Facts
                    </Button>

                    <div className="text-center py-12 text-gray-400">
                      <Shield className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>Fact check results will appear here</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="library" className="space-y-6">
              <Card className="gaming-card">
                <CardHeader>
                  <CardTitle>Document Library</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-12 text-gray-400">
                    <Archive className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>Document library will appear here</p>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </TabsContent>

        {/* Analytics & Diagnostics Tab */}
        <TabsContent value="analytics" className="space-y-6">
          <Tabs value={diagnosticsTab} onValueChange={setDiagnosticsTab}>
            <TabsList>
              <TabsTrigger value="dashboard">System Dashboard</TabsTrigger>
              <TabsTrigger value="diagnostics">AI Diagnostics</TabsTrigger>
              <TabsTrigger value="performance">Performance</TabsTrigger>
              <TabsTrigger value="optimization">Optimization</TabsTrigger>
            </TabsList>

            <TabsContent value="dashboard" className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card className="gaming-card">
                  <CardContent className="p-4 text-center">
                    <Beaker className="h-8 w-8 mx-auto mb-2 text-blue-500" />
                    <p className="text-2xl font-bold">{systemMetrics.totalAnalyses}</p>
                    <p className="text-sm text-gray-400">Total Analyses</p>
                  </CardContent>
                </Card>

                <Card className="gaming-card">
                  <CardContent className="p-4 text-center">
                    <FileText className="h-8 w-8 mx-auto mb-2 text-green-500" />
                    <p className="text-2xl font-bold">{systemMetrics.avgTokens}</p>
                    <p className="text-sm text-gray-400">Avg Tokens</p>
                  </CardContent>
                </Card>

                <Card className="gaming-card">
                  <CardContent className="p-4 text-center">
                    <CheckCircle className="h-8 w-8 mx-auto mb-2 text-yellow-500" />
                    <p className="text-2xl font-bold">{(systemMetrics.avgClarity * 100).toFixed(0)}%</p>
                    <p className="text-sm text-gray-400">Avg Clarity</p>
                  </CardContent>
                </Card>

                <Card className="gaming-card">
                  <CardContent className="p-4 text-center">
                    <Activity className="h-8 w-8 mx-auto mb-2 text-purple-500" />
                    <p className="text-2xl font-bold">{systemMetrics.activePrompts}</p>
                    <p className="text-sm text-gray-400">Active Prompts</p>
                  </CardContent>
                </Card>
              </div>

              <Card className="gaming-card">
                <CardHeader>
                  <CardTitle>Recent Diagnostic Results</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {diagnosticResults.map(result => (
                      <div key={result.id} className="border border-gray-700 rounded-lg p-3">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium text-sm">Prompt Analysis</span>
                          <Badge className={`${
                            result.status === 'completed' ? 'bg-green-500' :
                            result.status === 'analyzing' ? 'bg-blue-500 animate-pulse' :
                            'bg-red-500'
                          } text-white`}>
                            {result.status}
                          </Badge>
                        </div>
                        <p className="text-sm text-gray-300 mb-2 truncate">
                          {result.promptText}
                        </p>
                        <div className="grid grid-cols-3 gap-2 text-xs">
                          <div>
                            <span className="text-gray-400">Tokens:</span> {result.metrics.tokenCount}
                          </div>
                          <div>
                            <span className="text-gray-400">Clarity:</span> {(result.metrics.clarityScore * 100).toFixed(0)}%
                          </div>
                          <div>
                            <span className="text-gray-400">Issues:</span> {result.metrics.issues.length}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="diagnostics" className="space-y-6">
              <Card className="gaming-card">
                <CardHeader>
                  <CardTitle>Prompt Analyzer</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <Textarea
                      placeholder="Paste your prompt here for analysis..."
                      className="min-h-32"
                    />
                    <Button className="w-full">
                      <Beaker className="h-4 w-4 mr-2" />
                      Analyze Prompt
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="performance" className="space-y-6">
              <Card className="gaming-card">
                <CardHeader>
                  <CardTitle>Performance Metrics</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-64 bg-dark-800 rounded-lg p-4 flex items-center justify-center">
                    <p className="text-gray-400">Performance charts will appear here</p>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="optimization" className="space-y-6">
              <Card className="gaming-card">
                <CardHeader>
                  <CardTitle>Optimization Recommendations</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-12 text-gray-400">
                    <TrendingUp className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>Optimization suggestions will appear here</p>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </TabsContent>

        {/* Feedback & Learning Tab */}
        <TabsContent value="feedback" className="space-y-6">
          <Tabs value={feedbackTab} onValueChange={setFeedbackTab}>
            <TabsList>
              <TabsTrigger value="analytics">Feedback Analytics</TabsTrigger>
              <TabsTrigger value="history">Decision History</TabsTrigger>
              <TabsTrigger value="learning">Learning Insights</TabsTrigger>
              <TabsTrigger value="improvement">Improvement Tracking</TabsTrigger>
            </TabsList>

            <TabsContent value="analytics" className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card className="gaming-card">
                  <CardContent className="p-4 text-center">
                    <MessageSquare className="h-8 w-8 mx-auto mb-2 text-blue-500" />
                    <p className="text-2xl font-bold">{feedbackAnalytics.totalFeedback}</p>
                    <p className="text-sm text-gray-400">Total Feedback</p>
                  </CardContent>
                </Card>

                <Card className="gaming-card">
                  <CardContent className="p-4 text-center">
                    <Star className="h-8 w-8 mx-auto mb-2 text-yellow-500" />
                    <p className="text-2xl font-bold">{feedbackAnalytics.avgRating.toFixed(1)}</p>
                    <p className="text-sm text-gray-400">Avg Rating</p>
                  </CardContent>
                </Card>

                <Card className="gaming-card">
                  <CardContent className="p-4 text-center">
                    <ThumbsUp className="h-8 w-8 mx-auto mb-2 text-green-500" />
                    <p className="text-2xl font-bold">{(feedbackAnalytics.positiveRate * 100).toFixed(0)}%</p>
                    <p className="text-sm text-gray-400">Positive Rate</p>
                  </CardContent>
                </Card>

                <Card className="gaming-card">
                  <CardContent className="p-4 text-center">
                    <TrendingUp className="h-8 w-8 mx-auto mb-2 text-purple-500" />
                    <p className="text-2xl font-bold">+12%</p>
                    <p className="text-sm text-gray-400">Improvement</p>
                  </CardContent>
                </Card>
              </div>

              <Card className="gaming-card">
                <CardHeader>
                  <CardTitle>Recent Feedback</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {feedbackData.map(feedback => (
                      <div key={feedback.id} className="border border-gray-700 rounded-lg p-3">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <Badge variant="outline">{feedback.contentType}</Badge>
                            <div className="flex">
                              {[...Array(5)].map((_, i) => (
                                <Star
                                  key={i}
                                  className={`h-3 w-3 ${
                                    i < feedback.rating ? 'text-yellow-500 fill-current' : 'text-gray-400'
                                  }`}
                                />
                              ))}
                            </div>
                          </div>
                          {feedback.outcome && (
                            <Badge className={`${
                              feedback.outcome === 'success' ? 'bg-green-500' :
                              feedback.outcome === 'failure' ? 'bg-red-500' :
                              'bg-yellow-500'
                            } text-white`}>
                              {feedback.outcome}
                            </Badge>
                          )}
                        </div>
                        <p className="text-sm text-gray-300">{feedback.comment}</p>
                        <p className="text-xs text-gray-400 mt-1">
                          {new Date(feedback.timestamp).toLocaleDateString()}
                        </p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="history" className="space-y-6">
              <Card className="gaming-card">
                <CardHeader>
                  <CardTitle>Decision Outcome History</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-12 text-gray-400">
                    <Clock className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>Decision history will appear here</p>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="learning" className="space-y-6">
              <Card className="gaming-card">
                <CardHeader>
                  <CardTitle>Learning Insights</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-12 text-gray-400">
                    <Brain className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>Learning insights will appear here</p>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="improvement" className="space-y-6">
              <Card className="gaming-card">
                <CardHeader>
                  <CardTitle>Improvement Tracking</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-12 text-gray-400">
                    <TrendingUp className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>Improvement metrics will appear here</p>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </TabsContent>
      </Tabs>
    </div>
  );
}