import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Brain, Target, Shield, TrendingUp, Activity, Database,
  Globe, Zap, BarChart3, DollarSign, Home, Briefcase,
  Bitcoin, LineChart, Trophy, AlertTriangle, Clock,
  RefreshCw, Settings, Search, Filter, Grid3x3
} from 'lucide-react';
import { IntelligencePanel } from '@/components/intelligence/IntelligencePanel';
import { MemorySearch } from '@/components/intelligence/MemorySearch';
import { PatternLibrary } from '@/components/intelligence/PatternLibrary';
import { useWebSocket } from '@/hooks/useWebSocket';
import {
  getUniversalIntelligence,
  type DecisionContext,
  type IntelligenceResult
} from '@/features/sports/api/sports';

// Domain configurations
const DOMAINS = {
  SPORTS_BETTING: {
    name: 'Sports Betting',
    icon: Trophy,
    color: 'text-green-500',
    bgColor: 'bg-green-500/10',
    borderColor: 'border-green-500/20'
  },
  TRADING: {
    name: 'Stock Trading',
    icon: LineChart,
    color: 'text-blue-500',
    bgColor: 'bg-blue-500/10',
    borderColor: 'border-blue-500/20'
  },
  CRYPTO: {
    name: 'Cryptocurrency',
    icon: Bitcoin,
    color: 'text-orange-500',
    bgColor: 'bg-orange-500/10',
    borderColor: 'border-orange-500/20'
  },
  REAL_ESTATE: {
    name: 'Real Estate',
    icon: Home,
    color: 'text-purple-500',
    bgColor: 'bg-purple-500/10',
    borderColor: 'border-purple-500/20'
  },
  BUSINESS: {
    name: 'Business Decisions',
    icon: Briefcase,
    color: 'text-indigo-500',
    bgColor: 'bg-indigo-500/10',
    borderColor: 'border-indigo-500/20'
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

export function CommandCenter() {
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
  const [loading, setLoading] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  // WebSocket for real-time updates
  const { isConnected } = useWebSocket({
    url: '/ws/intelligence/',
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

    // Update status to analyzing
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

      updateDecision({
        ...decision,
        intelligence,
        status: 'ready'
      });
    } catch (error) {
      console.error('Analysis failed:', error);
    } finally {
      setLoading(false);
    }
  };

  // Mock data for demonstration
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
    setDecisions(mockDecisions);
  }, []);

  const getStatusColor = (status: UniversalDecision['status']) => {
    switch (status) {
      case 'pending': return 'bg-yellow-500';
      case 'analyzing': return 'bg-blue-500 animate-pulse';
      case 'ready': return 'bg-green-500';
      case 'executed': return 'bg-muted/50';
      default: return 'bg-muted/50';
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
            <p className="text-muted-foreground mt-2">
              AI-powered decision intelligence across all domains
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
          <Card className="bg-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Portfolio Value</span>
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

          <Card className="bg-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Win Rate</span>
                <Trophy className="h-4 w-4 text-yellow-500" />
              </div>
              <p className="text-2xl font-bold mt-2">
                {(portfolio.winRate * 100).toFixed(0)}%
              </p>
              <Progress value={portfolio.winRate * 100} className="mt-2 h-1" />
            </CardContent>
          </Card>

          <Card className="bg-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Active Positions</span>
                <Activity className="h-4 w-4 text-blue-500" />
              </div>
              <p className="text-2xl font-bold mt-2">{portfolio.activePositions}</p>
              <p className="text-sm text-muted-foreground mt-1">Across 5 domains</p>
            </CardContent>
          </Card>

          <Card className="bg-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Risk Score</span>
                <Shield className="h-4 w-4 text-orange-500" />
              </div>
              <p className={`text-2xl font-bold mt-2 ${getRiskColor(portfolio.riskScore)}`}>
                {(portfolio.riskScore * 100).toFixed(0)}%
              </p>
              <Progress value={portfolio.riskScore * 100} className="mt-2 h-1" />
            </CardContent>
          </Card>

          <Card className="bg-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Pattern Matches</span>
                <Brain className="h-4 w-4 text-purple-500" />
              </div>
              <p className="text-2xl font-bold mt-2">247</p>
              <p className="text-sm text-muted-foreground mt-1">This week</p>
            </CardContent>
          </Card>

          <Card className="bg-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Agent Consensus</span>
                <Zap className="h-4 w-4 text-yellow-500" />
              </div>
              <p className="text-2xl font-bold mt-2">82%</p>
              <p className="text-sm text-green-500 mt-1">Strong Signal</p>
            </CardContent>
          </Card>
        </div>

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
      </div>

      {/* Main Content */}
      <Tabs defaultValue="decisions" className="space-y-6">
        <TabsList className="grid grid-cols-4 w-full max-w-2xl">
          <TabsTrigger value="decisions">Active Decisions</TabsTrigger>
          <TabsTrigger value="intelligence">Intelligence Hub</TabsTrigger>
          <TabsTrigger value="patterns">Pattern Analysis</TabsTrigger>
          <TabsTrigger value="portfolio">Portfolio</TabsTrigger>
        </TabsList>

        <TabsContent value="decisions" className="space-y-6">
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

          {/* Decisions Grid/List */}
          <div className={viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4' : 'space-y-4'}>
            {decisions.filter(d => selectedDomain === 'SPORTS_BETTING' || d.domain === selectedDomain).map(decision => {
              const domainConfig = DOMAINS[decision.domain];
              const Icon = domainConfig.icon;

              return (
                <Card key={decision.id} className={`bg-card border ${domainConfig.borderColor}`}>
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-2">
                        <div className={`p-2 rounded-lg ${domainConfig.bgColor}`}>
                          <Icon className={`h-5 w-5 ${domainConfig.color}`} />
                        </div>
                        <div>
                          <h3 className="font-semibold">{decision.entity}</h3>
                          <p className="text-xs text-muted-foreground">{domainConfig.name}</p>
                        </div>
                      </div>
                      <Badge className={`${getStatusColor(decision.status)} text-foreground`}>
                        {decision.status}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <p className="text-sm text-muted-foreground">{decision.description}</p>

                    {decision.intelligence && (
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-muted-foreground">Action</span>
                          <Badge variant="outline">
                            {decision.intelligence.primary_action}
                          </Badge>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-muted-foreground">Confidence</span>
                          <span className="text-sm font-bold">
                            {(decision.intelligence.confidence * 100).toFixed(0)}%
                          </span>
                        </div>
                        <Progress value={decision.intelligence.confidence * 100} className="h-1" />

                        {decision.intelligence.position_sizing && (
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-muted-foreground">Recommended</span>
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
                          <p className="text-xs text-muted-foreground mt-1">Analyzing...</p>
                        </div>
                      )}
                    </div>

                    {decision.outcome && (
                      <div className="pt-3 border-t border-gray-700">
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-muted-foreground">Outcome</span>
                          <Badge
                            variant={decision.outcome === 'success' ? 'default' : 'destructive'}
                          >
                            {decision.outcome}
                          </Badge>
                        </div>
                        {decision.roi && (
                          <p className={`text-sm mt-1 ${decision.roi > 0 ? 'text-green-500' : 'text-red-500'}`}>
                            ROI: {decision.roi > 0 ? '+' : ''}{decision.roi.toFixed(2)}%
                          </p>
                        )}
                      </div>
                    )}
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </TabsContent>

        <TabsContent value="intelligence" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <h2 className="text-xl font-semibold mb-4">Universal Intelligence Analysis</h2>
              <Alert className="mb-4">
                <Brain className="h-4 w-4" />
                <AlertDescription>
                  102 specialized agents analyzing patterns across all domains in real-time
                </AlertDescription>
              </Alert>
              {/* Placeholder for intelligence panel */}
              <Card className="bg-card">
                <CardContent className="p-6">
                  <p className="text-center text-muted-foreground">
                    Select a decision to analyze with Universal Intelligence
                  </p>
                </CardContent>
              </Card>
            </div>
            <div>
              <h2 className="text-xl font-semibold mb-4">Memory Search</h2>
              <MemorySearch domain={selectedDomain} />
            </div>
          </div>
        </TabsContent>

        <TabsContent value="patterns" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <h2 className="text-xl font-semibold mb-4">Cross-Domain Patterns</h2>
              <PatternLibrary domain={selectedDomain} />
            </div>
            <div>
              <h2 className="text-xl font-semibold mb-4">Pattern Visualization</h2>
              <Card className="bg-card">
                <CardContent className="p-6">
                  <div className="space-y-4">
                    {/* Pattern correlation matrix */}
                    <div className="grid grid-cols-5 gap-2">
                      {Object.keys(DOMAINS).map(domain1 => (
                        <div key={domain1} className="space-y-2">
                          {Object.keys(DOMAINS).map(domain2 => {
                            const correlation = Math.random();
                            return (
                              <div
                                key={`${domain1}-${domain2}`}
                                className="h-12 rounded flex items-center justify-center text-xs"
                                style={{
                                  backgroundColor: `rgba(59, 130, 246, ${correlation})`,
                                }}
                              >
                                {(correlation * 100).toFixed(0)}%
                              </div>
                            );
                          })}
                        </div>
                      ))}
                    </div>
                    <p className="text-sm text-center text-muted-foreground mt-4">
                      Pattern correlation matrix across domains
                    </p>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="portfolio" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <h2 className="text-xl font-semibold mb-4">Portfolio Allocation</h2>
              <Card className="bg-card">
                <CardContent className="p-6">
                  <div className="space-y-4">
                    {Object.entries(DOMAINS).map(([key, config]) => {
                      const allocation = Math.random() * 30 + 10;
                      const Icon = config.icon;
                      return (
                        <div key={key} className="space-y-2">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <Icon className={`h-4 w-4 ${config.color}`} />
                              <span className="font-medium">{config.name}</span>
                            </div>
                            <span className="text-sm font-bold">
                              {allocation.toFixed(1)}%
                            </span>
                          </div>
                          <Progress value={allocation} className="h-2" />
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>
            </div>
            <div>
              <h2 className="text-xl font-semibold mb-4">Risk Management</h2>
              <Card className="bg-card">
                <CardContent className="p-6 space-y-4">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Kelly Allocation</span>
                      <span className="font-bold">2.8%</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Max Drawdown</span>
                      <span className="font-bold text-red-500">-12.4%</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Sharpe Ratio</span>
                      <span className="font-bold text-green-500">2.31</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Value at Risk</span>
                      <span className="font-bold">$3,200</span>
                    </div>
                  </div>
                  <Button className="w-full" variant="outline">
                    <Shield className="h-4 w-4 mr-2" />
                    Adjust Risk Parameters
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}