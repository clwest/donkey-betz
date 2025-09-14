import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Label } from '@/components/ui/label';
import { Progress } from '@/components/ui/progress';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  ArrowLeft, Activity, Brain, Target, Shield,
  Clock, MapPin, AlertTriangle, Trophy, TrendingUp,
  Newspaper, PlayCircle, Database, BookOpen, Zap,
  RefreshCw, Wifi, Plus, Minus, X, DollarSign,
  BarChart3, Share2, Camera, Copy, CheckCircle,
  Bitcoin, LineChart, Home, Briefcase, Globe,
  Calculator, Settings, ChevronRight, AlertCircle
} from 'lucide-react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { formatDistanceToNow } from 'date-fns';
import { toast } from 'sonner';
import '../styles/gaming-theme.css';

// Import Intelligence Components
import { IntelligencePanel } from '../components/intelligence/IntelligencePanel';
import { MemorySearch } from '../components/intelligence/MemorySearch';
import { PatternLibrary } from '../components/intelligence/PatternLibrary';

import {
  getUniversalIntelligence,
  type DecisionContext,
  type IntelligenceResult
} from '../features/sports/api/sports';

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

interface DecisionData {
  id: string;
  domain: keyof typeof DOMAINS;
  title: string;
  subtitle: string;
  entity: string;
  description: string;
  status: 'pending' | 'analyzing' | 'ready' | 'executed';
  metrics: {
    primary: { label: string; value: string | number; change?: number };
    secondary: { label: string; value: string | number; change?: number };
    tertiary?: { label: string; value: string | number; change?: number };
  };
  liveData?: {
    isLive: boolean;
    currentValue?: number;
    lastUpdate?: string;
    stream?: any[];
  };
  contextData?: Record<string, any>;
  intelligence?: IntelligenceResult;
  timestamp: string;
}

interface ActionItem {
  id: string;
  name: string;
  value: number;
  confidence?: number;
  type: string;
  recommended?: boolean;
}

interface ExecutionSlipItem {
  action: ActionItem;
  stake: number;
  expectedReturn?: number;
}

// Mock data generator based on domain
const generateDecisionData = (decisionId: string, domain: keyof typeof DOMAINS): DecisionData => {
  const mockData: Record<keyof typeof DOMAINS, DecisionData> = {
    SPORTS_BETTING: {
      id: decisionId,
      domain: 'SPORTS_BETTING',
      title: 'Lakers @ Warriors',
      subtitle: 'NBA • Tonight 10:30 PM',
      entity: 'NBA_GAME_LAL_GSW',
      description: 'High-value NBA matchup with favorable spread movement',
      status: 'ready',
      metrics: {
        primary: { label: 'Spread', value: 'LAL +5.5', change: -1.5 },
        secondary: { label: 'Total', value: 'O/U 232.5', change: 2 },
        tertiary: { label: 'ML Odds', value: '+180/-220' }
      },
      liveData: {
        isLive: false,
        currentValue: 232.5,
        lastUpdate: new Date().toISOString()
      },
      timestamp: new Date().toISOString()
    },
    TRADING: {
      id: decisionId,
      domain: 'TRADING',
      title: 'NVDA - NVIDIA Corp',
      subtitle: 'NASDAQ • Earnings Tomorrow',
      entity: 'STOCK_NVDA',
      description: 'Pre-earnings momentum play with strong technical setup',
      status: 'ready',
      metrics: {
        primary: { label: 'Price', value: '$875.42', change: 12.5 },
        secondary: { label: 'IV Rank', value: '82%', change: 15 },
        tertiary: { label: 'Volume', value: '52.3M' }
      },
      liveData: {
        isLive: true,
        currentValue: 875.42,
        lastUpdate: new Date().toISOString()
      },
      timestamp: new Date().toISOString()
    },
    CRYPTO: {
      id: decisionId,
      domain: 'CRYPTO',
      title: 'BTC/USD',
      subtitle: 'Bitcoin • 24/7 Market',
      entity: 'CRYPTO_BTC_USD',
      description: 'Breakout pattern forming at key resistance level',
      status: 'analyzing',
      metrics: {
        primary: { label: 'Price', value: '$68,420', change: 2340 },
        secondary: { label: 'Volume', value: '$28.5B', change: 15 },
        tertiary: { label: 'RSI', value: '68' }
      },
      liveData: {
        isLive: true,
        currentValue: 68420,
        lastUpdate: new Date().toISOString()
      },
      timestamp: new Date().toISOString()
    },
    REAL_ESTATE: {
      id: decisionId,
      domain: 'REAL_ESTATE',
      title: '123 Main St, Austin TX',
      subtitle: '4BR/3BA • 2,850 sqft',
      entity: 'PROPERTY_AUSTIN_123',
      description: 'Undervalued property in high-growth tech corridor',
      status: 'pending',
      metrics: {
        primary: { label: 'List Price', value: '$625,000' },
        secondary: { label: 'Est. Value', value: '$680,000', change: 55000 },
        tertiary: { label: 'Cap Rate', value: '7.2%' }
      },
      timestamp: new Date().toISOString()
    },
    BUSINESS: {
      id: decisionId,
      domain: 'BUSINESS',
      title: 'Series B Funding Round',
      subtitle: 'SaaS Startup • AI/ML Platform',
      entity: 'INVEST_SERIES_B_AI',
      description: 'Early-stage investment opportunity in AI infrastructure',
      status: 'ready',
      metrics: {
        primary: { label: 'Valuation', value: '$150M' },
        secondary: { label: 'Revenue', value: '$12M ARR', change: 300 },
        tertiary: { label: 'Growth', value: '3x YoY' }
      },
      timestamp: new Date().toISOString()
    }
  };

  return mockData[domain] || mockData.SPORTS_BETTING;
};

export function DecisionDetailPage() {
  const { decisionId, domain } = useParams<{ decisionId: string; domain: string }>();
  const navigate = useNavigate();

  const [decisionData, setDecisionData] = useState<DecisionData | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeView, setActiveView] = useState('dashboard');
  const [executionSlip, setExecutionSlip] = useState<ExecutionSlipItem[]>([]);
  const [bankroll, setBankroll] = useState(50000);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [intelligence, setIntelligence] = useState<IntelligenceResult | null>(null);

  const selectedDomain = (domain as keyof typeof DOMAINS) || 'SPORTS_BETTING';
  const domainConfig = DOMAINS[selectedDomain];
  const DomainIcon = domainConfig.icon;

  // WebSocket for live updates
  const { isConnected, sendMessage } = useWebSocket({
    url: '/ws/decisions/',
    onOpen: () => {
      if (decisionId) {
        sendMessage({
          type: 'subscribe_decision',
          decision_id: decisionId,
          domain: selectedDomain
        });
      }
    },
    onMessage: (data: any) => {
      if (data.type === 'decision_updated' && data.decision_id === decisionId) {
        fetchDecisionData();
      }
    }
  });

  const fetchDecisionData = async () => {
    setLoading(true);
    try {
      // Mock data for now - in production this would fetch from API
      const data = generateDecisionData(decisionId || 'mock-id', selectedDomain);
      setDecisionData(data);

      // Fetch intelligence if not already loaded
      if (!intelligence) {
        const context: DecisionContext = {
          domain: selectedDomain,
          entity_id: decisionId || 'mock-id',
          data_points: data.contextData || {},
          risk_level: 0.5,
          time_horizon: 'medium'
        };

        const intelligenceResult = await getUniversalIntelligence(context);
        setIntelligence(intelligenceResult);
      }
    } catch (error) {
      console.error('Failed to fetch decision data:', error);
      toast.error('Failed to load decision data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDecisionData();

    const interval = setInterval(() => {
      if (autoRefresh) {
        fetchDecisionData();
      }
    }, 30000);

    return () => clearInterval(interval);
  }, [decisionId, selectedDomain, autoRefresh]);

  const addToExecutionSlip = (action: ActionItem, stake: number) => {
    const newItem: ExecutionSlipItem = {
      action,
      stake,
      expectedReturn: stake * (action.value / 100)
    };
    setExecutionSlip([...executionSlip, newItem]);
    toast.success(`Added ${action.name} to execution slip`);
  };

  const removeFromExecutionSlip = (index: number) => {
    setExecutionSlip(executionSlip.filter((_, i) => i !== index));
  };

  const getTotalStake = () => {
    return executionSlip.reduce((sum, item) => sum + item.stake, 0);
  };

  const getTotalExpectedReturn = () => {
    return executionSlip.reduce((sum, item) => sum + (item.expectedReturn || 0), 0);
  };

  if (loading && !decisionData) {
    return (
      <div className="min-h-screen gaming-theme flex items-center justify-center">
        <div className="text-center">
          <Brain className="h-12 w-12 text-blue-500 animate-pulse mx-auto mb-4" />
          <p className="text-lg gaming-text-primary">Analyzing decision...</p>
        </div>
      </div>
    );
  }

  if (!decisionData) {
    return (
      <div className="min-h-screen gaming-theme">
        <div className="p-6">
          <Button onClick={() => navigate('/command-center')} variant="ghost">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Command Center
          </Button>
          <div className="gaming-card p-16 text-center">
            <h3 className="text-2xl font-bold gaming-text-primary mb-4">Decision Not Found</h3>
            <p className="gaming-text-secondary">Unable to load decision data</p>
          </div>
        </div>
      </div>
    );
  }

  const isLive = decisionData.liveData?.isLive || false;

  return (
    <div className="min-h-screen gaming-theme">
      <div className="max-w-[1920px] mx-auto">

        {/* Header Strip */}
        <div className="border-b border-gaming-border bg-gaming-background/95 backdrop-blur sticky top-0 z-50">
          <div className="px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Button
                  onClick={() => navigate('/command-center')}
                  variant="ghost"
                  size="sm"
                  className="gaming-text-secondary hover:gaming-text-primary"
                >
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Command Center
                </Button>

                <Separator orientation="vertical" className="h-6" />

                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg ${domainConfig.bgColor}`}>
                    <DomainIcon className={`h-5 w-5 ${domainConfig.color}`} />
                  </div>
                  <div>
                    <h1 className="text-lg font-bold gaming-text-primary">
                      {decisionData.title}
                    </h1>
                    <div className="text-sm gaming-text-secondary">
                      {decisionData.subtitle}
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-4">
                <Badge className={`${domainConfig.bgColor} ${domainConfig.color}`}>
                  {domainConfig.name}
                </Badge>

                {isLive && (
                  <div className="flex items-center gap-2 px-3 py-1 bg-red-500/20 border border-red-500/50 rounded-full">
                    <div className="w-2 h-2 bg-red-400 rounded-full animate-pulse"></div>
                    <span className="text-sm font-medium text-red-400">LIVE</span>
                  </div>
                )}

                {isConnected && (
                  <div className="flex items-center gap-2 gaming-text-accent">
                    <Wifi className="w-4 h-4" />
                    <span className="text-sm">Connected</span>
                  </div>
                )}

                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setAutoRefresh(!autoRefresh)}
                  className={autoRefresh ? 'gaming-text-neon' : 'gaming-text-secondary'}
                >
                  <RefreshCw className={`w-4 h-4 mr-2 ${autoRefresh ? 'animate-spin' : ''}`} />
                  {autoRefresh ? 'Auto' : 'Manual'}
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-12 gap-6 p-6 min-h-screen">

          {/* Left Sidebar - Navigation & Quick Stats */}
          <div className="col-span-2 space-y-4">

            {/* Navigation */}
            <Card className="gaming-card">
              <div className="gaming-border-glow"></div>
              <CardContent className="p-4">
                <div className="space-y-2">
                  {[
                    { id: 'dashboard', icon: Activity, label: 'Dashboard' },
                    { id: 'execution', icon: Target, label: 'Execution' },
                    { id: 'intelligence', icon: Brain, label: 'Intelligence' },
                    { id: 'patterns', icon: BookOpen, label: 'Patterns' },
                    { id: 'memory', icon: Database, label: 'Memory' },
                    { id: 'live', icon: PlayCircle, label: 'Live Data' },
                  ].map((item) => (
                    <button
                      key={item.id}
                      onClick={() => setActiveView(item.id)}
                      className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-all ${
                        activeView === item.id
                          ? `bg-${domainConfig.neonColor}/20 border border-${domainConfig.neonColor}/50 gaming-text-neon`
                          : 'hover:bg-gaming-bg-secondary/30 gaming-text-secondary hover:gaming-text-primary'
                      }`}
                    >
                      <item.icon className="w-4 h-4" />
                      <span className="text-sm font-medium">{item.label}</span>
                    </button>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Quick Decision Status */}
            <Card className="gaming-card">
              <div className="gaming-border-glow"></div>
              <CardContent className="p-4">
                <div className="text-center">
                  <div className="text-xs gaming-text-secondary mb-2">DECISION STATUS</div>

                  <Badge
                    className={`mb-3 ${
                      decisionData.status === 'ready' ? 'bg-green-500' :
                      decisionData.status === 'analyzing' ? 'bg-blue-500 animate-pulse' :
                      decisionData.status === 'executed' ? 'bg-gray-500' :
                      'bg-yellow-500'
                    }`}
                  >
                    {decisionData.status.toUpperCase()}
                  </Badge>

                  {decisionData.metrics.primary && (
                    <div>
                      <div className="text-xs gaming-text-secondary mb-1">
                        {decisionData.metrics.primary.label}
                      </div>
                      <div className="text-xl font-bold gaming-text-neon">
                        {decisionData.metrics.primary.value}
                      </div>
                      {decisionData.metrics.primary.change && (
                        <div className={`text-xs mt-1 ${
                          decisionData.metrics.primary.change > 0 ? 'text-green-500' : 'text-red-500'
                        }`}>
                          {decisionData.metrics.primary.change > 0 ? '+' : ''}
                          {decisionData.metrics.primary.change}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Key Metrics */}
            <Card className="gaming-card">
              <div className="gaming-border-glow"></div>
              <CardContent className="p-4 space-y-3">
                {decisionData.metrics.secondary && (
                  <div>
                    <div className="text-xs gaming-text-secondary">
                      {decisionData.metrics.secondary.label}
                    </div>
                    <div className="text-lg font-bold gaming-text-primary">
                      {decisionData.metrics.secondary.value}
                    </div>
                    {decisionData.metrics.secondary.change && (
                      <div className={`text-xs ${
                        decisionData.metrics.secondary.change > 0 ? 'text-green-500' : 'text-red-500'
                      }`}>
                        {decisionData.metrics.secondary.change > 0 ? '+' : ''}
                        {decisionData.metrics.secondary.change}
                      </div>
                    )}
                  </div>
                )}

                {decisionData.metrics.tertiary && (
                  <div>
                    <div className="text-xs gaming-text-secondary">
                      {decisionData.metrics.tertiary.label}
                    </div>
                    <div className="text-lg font-bold gaming-text-primary">
                      {decisionData.metrics.tertiary.value}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Center Content - Main View */}
          <div className="col-span-8">
            {activeView === 'dashboard' && (
              <div className="space-y-6">
                {/* Intelligence Overview */}
                <IntelligencePanel
                  gameId={decisionId || 'mock-id'}
                  gameData={decisionData}
                  onDecision={(result) => setIntelligence(result)}
                />

                {/* Decision Analysis */}
                <Card className="gaming-card">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Brain className="h-5 w-5 text-blue-500" />
                      Decision Analysis
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <p className="text-sm gaming-text-secondary">
                      {decisionData.description}
                    </p>

                    {intelligence && (
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label>Recommended Action</Label>
                          <Badge variant="outline" className="text-sm">
                            {intelligence.primary_action}
                          </Badge>
                        </div>
                        <div className="space-y-2">
                          <Label>Confidence Level</Label>
                          <div className="flex items-center gap-2">
                            <Progress value={intelligence.confidence * 100} className="flex-1" />
                            <span className="text-sm font-bold">
                              {(intelligence.confidence * 100).toFixed(0)}%
                            </span>
                          </div>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Live Data Stream */}
                {isLive && (
                  <Card className="gaming-card">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Activity className="h-5 w-5 text-green-500 animate-pulse" />
                        Live Data Stream
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="h-64 bg-dark-800 rounded-lg p-4">
                        {/* Placeholder for live chart */}
                        <div className="flex items-center justify-center h-full">
                          <p className="text-gray-400">Live data visualization</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            )}

            {activeView === 'execution' && (
              <div className="space-y-6">
                <Card className="gaming-card">
                  <CardHeader>
                    <CardTitle>Execution Options</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {/* Mock execution options based on domain */}
                      {[
                        { id: '1', name: 'Primary Action', value: 110, confidence: 0.82, type: 'primary', recommended: true },
                        { id: '2', name: 'Alternative A', value: 105, confidence: 0.68, type: 'alternative' },
                        { id: '3', name: 'Alternative B', value: 95, confidence: 0.55, type: 'alternative' },
                        { id: '4', name: 'Hedge Position', value: -50, confidence: 0.75, type: 'hedge' },
                      ].map((option) => (
                        <div key={option.id} className="border border-gaming-border rounded-lg p-4">
                          <div className="flex items-center justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-2">
                                <h4 className="font-medium">{option.name}</h4>
                                {option.recommended && (
                                  <Badge className="bg-green-500/20 text-green-500">
                                    Recommended
                                  </Badge>
                                )}
                              </div>
                              <div className="flex items-center gap-4 mt-2 text-sm">
                                <span className="gaming-text-secondary">
                                  Expected: {option.value > 0 ? '+' : ''}{option.value}%
                                </span>
                                <span className="gaming-text-secondary">
                                  Confidence: {(option.confidence * 100).toFixed(0)}%
                                </span>
                              </div>
                            </div>
                            <div className="flex items-center gap-2">
                              <Input
                                type="number"
                                placeholder="Stake"
                                className="w-24"
                                id={`stake-${option.id}`}
                              />
                              <Button
                                size="sm"
                                onClick={() => {
                                  const stakeInput = document.getElementById(`stake-${option.id}`) as HTMLInputElement;
                                  const stake = parseFloat(stakeInput?.value || '0');
                                  if (stake > 0) {
                                    addToExecutionSlip(option as ActionItem, stake);
                                  }
                                }}
                              >
                                <Plus className="h-4 w-4" />
                              </Button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {activeView === 'intelligence' && (
              <div className="space-y-6">
                <IntelligencePanel
                  gameId={decisionId || 'mock-id'}
                  gameData={decisionData}
                  onDecision={(result) => setIntelligence(result)}
                />
              </div>
            )}

            {activeView === 'patterns' && (
              <PatternLibrary
                domain={selectedDomain}
                onPatternSelect={(pattern) => console.log('Selected pattern:', pattern)}
              />
            )}

            {activeView === 'memory' && (
              <MemorySearch
                domain={selectedDomain}
                entityId={decisionId}
                onMemorySelect={(memory) => console.log('Selected memory:', memory)}
              />
            )}

            {activeView === 'live' && (
              <Card className="gaming-card">
                <CardHeader>
                  <CardTitle>Live Data Feed</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <Alert>
                      <AlertCircle className="h-4 w-4" />
                      <AlertDescription>
                        Real-time data streaming for {domainConfig.name}
                      </AlertDescription>
                    </Alert>
                    <div className="h-96 bg-dark-800 rounded-lg p-4">
                      <p className="text-center text-gray-400 mt-32">
                        Live data visualization would appear here
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Right Sidebar - Execution Slip */}
          <div className="col-span-2 space-y-4">
            <Card className="gaming-card">
              <div className="gaming-border-glow"></div>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm flex items-center justify-between">
                  <span>Execution Slip</span>
                  <Badge variant="outline">{executionSlip.length}</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {executionSlip.length === 0 ? (
                  <div className="text-center py-8">
                    <Target className="h-8 w-8 mx-auto mb-2 text-gray-500" />
                    <p className="text-sm text-gray-400">No actions selected</p>
                  </div>
                ) : (
                  <>
                    {executionSlip.map((item, index) => (
                      <div key={index} className="border border-gaming-border rounded-lg p-3">
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <p className="text-sm font-medium">{item.action.name}</p>
                            <p className="text-xs text-gray-400">
                              Expected: {item.action.value > 0 ? '+' : ''}{item.action.value}%
                            </p>
                          </div>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => removeFromExecutionSlip(index)}
                          >
                            <X className="h-3 w-3" />
                          </Button>
                        </div>
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-400">Stake:</span>
                          <span className="font-bold">${item.stake.toLocaleString()}</span>
                        </div>
                        {item.expectedReturn && (
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-gray-400">Expected:</span>
                            <span className="text-green-500">
                              ${item.expectedReturn.toLocaleString()}
                            </span>
                          </div>
                        )}
                      </div>
                    ))}

                    <Separator />

                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-400">Total Stake:</span>
                        <span className="font-bold">${getTotalStake().toLocaleString()}</span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-400">Expected Return:</span>
                        <span className="text-green-500 font-bold">
                          ${getTotalExpectedReturn().toLocaleString()}
                        </span>
                      </div>
                    </div>

                    <Button className="w-full" size="sm">
                      <Zap className="h-4 w-4 mr-2" />
                      Execute All
                    </Button>
                  </>
                )}
              </CardContent>
            </Card>

            {/* Portfolio Summary */}
            <Card className="gaming-card">
              <div className="gaming-border-glow"></div>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm">Portfolio</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <div className="text-xs text-gray-400">Available</div>
                  <div className="text-xl font-bold gaming-text-neon">
                    ${bankroll.toLocaleString()}
                  </div>
                </div>
                <div>
                  <div className="text-xs text-gray-400">Kelly Suggestion</div>
                  <div className="text-lg font-bold text-green-500">
                    ${(bankroll * 0.025).toLocaleString()}
                  </div>
                </div>
                <div>
                  <div className="text-xs text-gray-400">Risk Level</div>
                  <Progress value={42} className="mt-1" />
                </div>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card className="gaming-card">
              <div className="gaming-border-glow"></div>
              <CardContent className="p-4 space-y-2">
                <Button variant="outline" size="sm" className="w-full">
                  <Calculator className="h-4 w-4 mr-2" />
                  Kelly Calculator
                </Button>
                <Button variant="outline" size="sm" className="w-full">
                  <Share2 className="h-4 w-4 mr-2" />
                  Share Analysis
                </Button>
                <Button variant="outline" size="sm" className="w-full">
                  <Settings className="h-4 w-4 mr-2" />
                  Risk Settings
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}