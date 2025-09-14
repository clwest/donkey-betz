import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import {
  Radar, Zap, Target, DollarSign, AlertTriangle,
  TrendingUp, Activity, Sparkles, Filter, Settings,
  Play, Pause, Volume2, VolumeX, Bell, BellOff,
  ChevronRight, ExternalLink, Timer, Signal
} from 'lucide-react';
import { useWebSocket } from '@/hooks/useWebSocket';

interface MarketOpportunity {
  id: string;
  type: 'arbitrage' | 'value_bet' | 'hedge' | 'momentum' | 'pattern_break';
  domain: 'SPORTS_BETTING' | 'CRYPTO' | 'TRADING' | 'REAL_ESTATE' | 'BUSINESS';
  entity: string;
  description: string;
  edge: number; // Expected edge percentage
  confidence: number;
  profitPotential: number; // Dollar amount
  riskLevel: number;
  timeWindow: number; // Minutes until opportunity expires
  requiredCapital: number;
  liquidityScore: number;
  historicalWinRate: number;
  marketData: {
    currentPrice?: number;
    targetPrice?: number;
    volume24h?: number;
    volatility?: number;
  };
  triggers: string[];
  exchanges?: string[];
  timestamp: string;
  status: 'active' | 'closing' | 'expired' | 'executed';
  alertLevel: 'low' | 'medium' | 'high' | 'critical';
}

interface ScannerSettings {
  isActive: boolean;
  minEdge: number;
  minConfidence: number;
  maxRisk: number;
  enabledDomains: string[];
  enabledTypes: string[];
  audioAlerts: boolean;
  pushNotifications: boolean;
  scanInterval: number; // seconds
}

interface ScannerMetrics {
  totalScanned: number;
  opportunitiesFound: number;
  avgEdge: number;
  executionRate: number;
  profitGenerated: number;
}

const OPPORTUNITY_TYPES = {
  arbitrage: { name: 'Arbitrage', color: 'text-green-500', icon: Target },
  value_bet: { name: 'Value Bet', color: 'text-blue-500', icon: TrendingUp },
  hedge: { name: 'Hedge', color: 'text-yellow-500', icon: AlertTriangle },
  momentum: { name: 'Momentum', color: 'text-purple-500', icon: Activity },
  pattern_break: { name: 'Pattern Break', color: 'text-pink-500', icon: Sparkles }
};

const DOMAIN_COLORS = {
  SPORTS_BETTING: 'bg-green-500/10 text-green-500',
  CRYPTO: 'bg-orange-500/10 text-orange-500',
  TRADING: 'bg-blue-500/10 text-blue-500',
  REAL_ESTATE: 'bg-purple-500/10 text-purple-500',
  BUSINESS: 'bg-indigo-500/10 text-indigo-500'
};

export function OpportunityScanner() {
  const [opportunities, setOpportunities] = useState<MarketOpportunity[]>([]);
  const [settings, setSettings] = useState<ScannerSettings>({
    isActive: true,
    minEdge: 2.0,
    minConfidence: 0.6,
    maxRisk: 0.5,
    enabledDomains: ['SPORTS_BETTING', 'CRYPTO', 'TRADING'],
    enabledTypes: ['arbitrage', 'value_bet', 'momentum'],
    audioAlerts: true,
    pushNotifications: true,
    scanInterval: 30
  });
  const [metrics, setMetrics] = useState<ScannerMetrics>({
    totalScanned: 15420,
    opportunitiesFound: 247,
    avgEdge: 4.2,
    executionRate: 0.68,
    profitGenerated: 12340
  });
  const [filter, setFilter] = useState<string>('all');
  const [showSettings, setShowSettings] = useState(false);
  const audioRef = useRef<HTMLAudioElement>(null);

  // WebSocket for real-time opportunities
  const { isConnected } = useWebSocket({
    url: '/ws/opportunity-scanner/',
    onMessage: (data: any) => {
      if (data.type === 'new_opportunity') {
        handleNewOpportunity(data.opportunity);
      } else if (data.type === 'opportunity_update') {
        updateOpportunity(data.opportunity);
      } else if (data.type === 'metrics_update') {
        setMetrics(data.metrics);
      }
    }
  });

  const handleNewOpportunity = (opportunity: MarketOpportunity) => {
    setOpportunities(prev => [opportunity, ...prev.slice(0, 49)]); // Keep last 50

    // Play alert sound for high-value opportunities
    if (opportunity.alertLevel === 'critical' && settings.audioAlerts && audioRef.current) {
      audioRef.current.play().catch(() => {}); // Ignore errors
    }

    // Show browser notification
    if (settings.pushNotifications && opportunity.alertLevel !== 'low') {
      if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(`${opportunity.type.toUpperCase()}: ${opportunity.entity}`, {
          body: `${opportunity.edge.toFixed(1)}% edge - $${opportunity.profitPotential.toLocaleString()} potential`,
          icon: '/icon-192x192.png'
        });
      }
    }
  };

  const updateOpportunity = (updatedOpp: MarketOpportunity) => {
    setOpportunities(prev =>
      prev.map(opp => opp.id === updatedOpp.id ? updatedOpp : opp)
    );
  };

  const getTimeRemaining = (timeWindow: number) => {
    if (timeWindow <= 0) return 'Expired';
    if (timeWindow < 60) return `${timeWindow}m`;
    const hours = Math.floor(timeWindow / 60);
    const minutes = timeWindow % 60;
    return `${hours}h ${minutes}m`;
  };

  const getAlertColor = (level: string) => {
    switch (level) {
      case 'critical': return 'bg-red-500 animate-pulse';
      case 'high': return 'bg-orange-500';
      case 'medium': return 'bg-yellow-500';
      default: return 'bg-blue-500';
    }
  };

  const getEdgeColor = (edge: number) => {
    if (edge >= 10) return 'text-green-400';
    if (edge >= 5) return 'text-green-500';
    if (edge >= 2) return 'text-blue-500';
    return 'text-gray-400';
  };

  const filteredOpportunities = opportunities.filter(opp => {
    if (filter === 'all') return true;
    if (filter === 'high-edge') return opp.edge >= 5;
    if (filter === 'low-risk') return opp.riskLevel <= 0.3;
    if (filter === 'arbitrage') return opp.type === 'arbitrage';
    return opp.domain === filter;
  });

  // Mock data initialization
  useEffect(() => {
    const mockOpportunities: MarketOpportunity[] = [
      {
        id: 'opp_001',
        type: 'arbitrage',
        domain: 'SPORTS_BETTING',
        entity: 'Lakers vs Warriors - ML',
        description: 'Arbitrage opportunity across 3 sportsbooks with 4.2% guaranteed profit',
        edge: 4.2,
        confidence: 0.98,
        profitPotential: 420,
        riskLevel: 0.02,
        timeWindow: 47,
        requiredCapital: 10000,
        liquidityScore: 0.95,
        historicalWinRate: 1.0,
        marketData: {
          currentPrice: -110,
          targetPrice: -105,
          volume24h: 250000
        },
        triggers: ['Line discrepancy', 'High liquidity', 'Stable odds'],
        exchanges: ['DraftKings', 'FanDuel', 'BetMGM'],
        timestamp: new Date().toISOString(),
        status: 'active',
        alertLevel: 'high'
      },
      {
        id: 'opp_002',
        type: 'momentum',
        domain: 'CRYPTO',
        entity: 'BTC/USD',
        description: 'Momentum breakout with whale accumulation pattern - 89% historical win rate',
        edge: 12.5,
        confidence: 0.87,
        profitPotential: 3750,
        riskLevel: 0.35,
        timeWindow: 23,
        requiredCapital: 30000,
        liquidityScore: 0.88,
        historicalWinRate: 0.89,
        marketData: {
          currentPrice: 65200,
          targetPrice: 73400,
          volume24h: 28000000,
          volatility: 0.032
        },
        triggers: ['Whale accumulation', 'RSI divergence', 'Volume spike'],
        exchanges: ['Binance', 'Coinbase', 'Kraken'],
        timestamp: new Date().toISOString(),
        status: 'active',
        alertLevel: 'critical'
      },
      {
        id: 'opp_003',
        type: 'value_bet',
        domain: 'TRADING',
        entity: 'NVDA Options Chain',
        description: 'Implied volatility mispricing in weekly calls - expected 15% edge',
        edge: 15.2,
        confidence: 0.73,
        profitPotential: 2280,
        riskLevel: 0.42,
        timeWindow: 156,
        requiredCapital: 15000,
        liquidityScore: 0.76,
        historicalWinRate: 0.71,
        marketData: {
          currentPrice: 847,
          targetPrice: 920,
          volume24h: 45000000
        },
        triggers: ['IV crush expected', 'Earnings momentum', 'Options flow'],
        exchanges: ['TD Ameritrade', 'E*TRADE', 'Interactive Brokers'],
        timestamp: new Date().toISOString(),
        status: 'active',
        alertLevel: 'high'
      }
    ];

    setOpportunities(mockOpportunities);
  }, []);

  // Request notification permission on mount
  useEffect(() => {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold bg-gradient-to-r from-green-400 to-blue-500 bg-clip-text text-transparent">
            Real-Time Opportunity Scanner
          </h2>
          <p className="text-gray-400 text-sm mt-1">
            AI continuously scanning ALL markets for profitable opportunities
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant="outline" className="px-3 py-1">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'} mr-2`} />
            {isConnected ? 'Live Scanning' : 'Disconnected'}
          </Badge>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setSettings(prev => ({ ...prev, isActive: !prev.isActive }))}
          >
            {settings.isActive ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowSettings(!showSettings)}
          >
            <Settings className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Scanner Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card className="gaming-card">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400">Scanned</span>
              <Radar className="h-4 w-4 text-blue-500" />
            </div>
            <p className="text-2xl font-bold mt-2">{metrics.totalScanned.toLocaleString()}</p>
            <p className="text-sm text-gray-400 mt-1">Total markets</p>
          </CardContent>
        </Card>

        <Card className="gaming-card">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400">Found</span>
              <Target className="h-4 w-4 text-green-500" />
            </div>
            <p className="text-2xl font-bold mt-2">{metrics.opportunitiesFound}</p>
            <p className="text-sm text-gray-400 mt-1">Opportunities</p>
          </CardContent>
        </Card>

        <Card className="gaming-card">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400">Avg Edge</span>
              <TrendingUp className="h-4 w-4 text-purple-500" />
            </div>
            <p className="text-2xl font-bold mt-2 text-purple-500">
              {metrics.avgEdge.toFixed(1)}%
            </p>
            <p className="text-sm text-gray-400 mt-1">Expected</p>
          </CardContent>
        </Card>

        <Card className="gaming-card">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400">Execution</span>
              <Activity className="h-4 w-4 text-yellow-500" />
            </div>
            <p className="text-2xl font-bold mt-2">
              {(metrics.executionRate * 100).toFixed(0)}%
            </p>
            <Progress value={metrics.executionRate * 100} className="mt-2 h-1" />
          </CardContent>
        </Card>

        <Card className="gaming-card">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400">Profit</span>
              <DollarSign className="h-4 w-4 text-green-500" />
            </div>
            <p className="text-2xl font-bold mt-2 text-green-500">
              ${metrics.profitGenerated.toLocaleString()}
            </p>
            <p className="text-sm text-gray-400 mt-1">Generated</p>
          </CardContent>
        </Card>
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <Card className="gaming-card border-blue-500/20">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              Scanner Settings
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div>
                  <Label>Minimum Edge (%)</Label>
                  <Slider
                    value={[settings.minEdge]}
                    onValueChange={(value) => setSettings(prev => ({ ...prev, minEdge: value[0] }))}
                    max={20}
                    min={0.5}
                    step={0.5}
                    className="mt-2"
                  />
                  <p className="text-sm text-gray-400 mt-1">{settings.minEdge}% minimum edge</p>
                </div>

                <div>
                  <Label>Minimum Confidence</Label>
                  <Slider
                    value={[settings.minConfidence * 100]}
                    onValueChange={(value) => setSettings(prev => ({ ...prev, minConfidence: value[0] / 100 }))}
                    max={100}
                    min={30}
                    step={5}
                    className="mt-2"
                  />
                  <p className="text-sm text-gray-400 mt-1">{(settings.minConfidence * 100).toFixed(0)}% confidence</p>
                </div>

                <div>
                  <Label>Maximum Risk</Label>
                  <Slider
                    value={[settings.maxRisk * 100]}
                    onValueChange={(value) => setSettings(prev => ({ ...prev, maxRisk: value[0] / 100 }))}
                    max={100}
                    min={10}
                    step={5}
                    className="mt-2"
                  />
                  <p className="text-sm text-gray-400 mt-1">{(settings.maxRisk * 100).toFixed(0)}% maximum risk</p>
                </div>
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <Label htmlFor="audio-alerts">Audio Alerts</Label>
                  <div className="flex items-center gap-2">
                    <Switch
                      id="audio-alerts"
                      checked={settings.audioAlerts}
                      onCheckedChange={(checked) => setSettings(prev => ({ ...prev, audioAlerts: checked }))}
                    />
                    {settings.audioAlerts ? <Volume2 className="h-4 w-4 text-green-500" /> : <VolumeX className="h-4 w-4 text-gray-400" />}
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <Label htmlFor="push-notifications">Push Notifications</Label>
                  <div className="flex items-center gap-2">
                    <Switch
                      id="push-notifications"
                      checked={settings.pushNotifications}
                      onCheckedChange={(checked) => setSettings(prev => ({ ...prev, pushNotifications: checked }))}
                    />
                    {settings.pushNotifications ? <Bell className="h-4 w-4 text-green-500" /> : <BellOff className="h-4 w-4 text-gray-400" />}
                  </div>
                </div>

                <div>
                  <Label>Scan Interval (seconds)</Label>
                  <Slider
                    value={[settings.scanInterval]}
                    onValueChange={(value) => setSettings(prev => ({ ...prev, scanInterval: value[0] }))}
                    max={300}
                    min={5}
                    step={5}
                    className="mt-2"
                  />
                  <p className="text-sm text-gray-400 mt-1">Scan every {settings.scanInterval}s</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Filters */}
      <div className="flex items-center gap-2 flex-wrap">
        <Filter className="h-4 w-4 text-gray-400" />
        <Button
          variant={filter === 'all' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setFilter('all')}
        >
          All
        </Button>
        <Button
          variant={filter === 'high-edge' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setFilter('high-edge')}
        >
          High Edge (5%+)
        </Button>
        <Button
          variant={filter === 'low-risk' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setFilter('low-risk')}
        >
          Low Risk
        </Button>
        <Button
          variant={filter === 'arbitrage' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setFilter('arbitrage')}
        >
          Arbitrage
        </Button>
        {Object.keys(DOMAIN_COLORS).map(domain => (
          <Button
            key={domain}
            variant={filter === domain ? 'default' : 'outline'}
            size="sm"
            onClick={() => setFilter(domain)}
          >
            {domain.replace('_', ' ')}
          </Button>
        ))}
      </div>

      {/* High-Priority Alert */}
      {opportunities.some(opp => opp.alertLevel === 'critical' && opp.status === 'active') && (
        <Alert className="border-red-500/50 bg-red-500/5">
          <AlertTriangle className="h-4 w-4 text-red-500" />
          <AlertDescription className="text-red-400">
            <strong>CRITICAL OPPORTUNITIES DETECTED!</strong> {' '}
            {opportunities.filter(opp => opp.alertLevel === 'critical' && opp.status === 'active').length} high-value opportunities require immediate attention.
          </AlertDescription>
        </Alert>
      )}

      {/* Opportunities List */}
      <div className="space-y-3">
        {filteredOpportunities.map(opportunity => {
          const TypeIcon = OPPORTUNITY_TYPES[opportunity.type]?.icon || Target;

          return (
            <Card key={opportunity.id} className="gaming-card hover:border-blue-500/50 transition-colors">
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3 flex-1">
                    {/* Alert Level Indicator */}
                    <div className={`w-1 h-16 rounded-full ${getAlertColor(opportunity.alertLevel)}`} />

                    <div className="flex-1">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <TypeIcon className={`h-4 w-4 ${OPPORTUNITY_TYPES[opportunity.type]?.color}`} />
                          <Badge variant="outline" className="text-xs">
                            {OPPORTUNITY_TYPES[opportunity.type]?.name}
                          </Badge>
                          <Badge className={`text-xs ${DOMAIN_COLORS[opportunity.domain]}`}>
                            {opportunity.domain.replace('_', ' ')}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-2 text-sm text-gray-400">
                          <Timer className="h-3 w-3" />
                          {getTimeRemaining(opportunity.timeWindow)}
                        </div>
                      </div>

                      <h3 className="font-semibold mb-1">{opportunity.entity}</h3>
                      <p className="text-sm text-gray-300 mb-3">{opportunity.description}</p>

                      {/* Key Metrics */}
                      <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-3">
                        <div className="text-center">
                          <p className="text-xs text-gray-400">Edge</p>
                          <p className={`font-bold ${getEdgeColor(opportunity.edge)}`}>
                            {opportunity.edge.toFixed(1)}%
                          </p>
                        </div>
                        <div className="text-center">
                          <p className="text-xs text-gray-400">Profit</p>
                          <p className="font-bold text-green-500">
                            ${opportunity.profitPotential.toLocaleString()}
                          </p>
                        </div>
                        <div className="text-center">
                          <p className="text-xs text-gray-400">Confidence</p>
                          <p className="font-bold text-blue-500">
                            {(opportunity.confidence * 100).toFixed(0)}%
                          </p>
                        </div>
                        <div className="text-center">
                          <p className="text-xs text-gray-400">Risk</p>
                          <p className={`font-bold ${opportunity.riskLevel <= 0.3 ? 'text-green-500' : opportunity.riskLevel <= 0.6 ? 'text-yellow-500' : 'text-red-500'}`}>
                            {(opportunity.riskLevel * 100).toFixed(0)}%
                          </p>
                        </div>
                        <div className="text-center">
                          <p className="text-xs text-gray-400">Capital</p>
                          <p className="font-bold text-gray-300">
                            ${(opportunity.requiredCapital / 1000).toFixed(0)}K
                          </p>
                        </div>
                      </div>

                      {/* Progress Bars */}
                      <div className="grid grid-cols-2 gap-4 mb-3">
                        <div>
                          <div className="flex items-center justify-between text-xs mb-1">
                            <span className="text-gray-400">Confidence</span>
                            <span className="text-gray-300">{(opportunity.confidence * 100).toFixed(0)}%</span>
                          </div>
                          <Progress value={opportunity.confidence * 100} className="h-1" />
                        </div>
                        <div>
                          <div className="flex items-center justify-between text-xs mb-1">
                            <span className="text-gray-400">Liquidity</span>
                            <span className="text-gray-300">{(opportunity.liquidityScore * 100).toFixed(0)}%</span>
                          </div>
                          <Progress value={opportunity.liquidityScore * 100} className="h-1" />
                        </div>
                      </div>

                      {/* Market Data */}
                      {opportunity.marketData.currentPrice && (
                        <div className="bg-dark-800 rounded-lg p-2 mb-3">
                          <div className="grid grid-cols-3 gap-3 text-xs">
                            <div>
                              <p className="text-gray-400">Current</p>
                              <p className="font-bold">{opportunity.marketData.currentPrice.toLocaleString()}</p>
                            </div>
                            <div>
                              <p className="text-gray-400">Target</p>
                              <p className="font-bold text-green-500">
                                {opportunity.marketData.targetPrice?.toLocaleString()}
                              </p>
                            </div>
                            <div>
                              <p className="text-gray-400">24h Volume</p>
                              <p className="font-bold">
                                ${(opportunity.marketData.volume24h! / 1000000).toFixed(1)}M
                              </p>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Triggers */}
                      <div className="flex flex-wrap gap-1 mb-3">
                        {opportunity.triggers.slice(0, 3).map((trigger, index) => (
                          <Badge key={index} variant="outline" className="text-xs">
                            {trigger}
                          </Badge>
                        ))}
                        {opportunity.triggers.length > 3 && (
                          <Badge variant="outline" className="text-xs">
                            +{opportunity.triggers.length - 3} more
                          </Badge>
                        )}
                      </div>

                      {/* Exchanges */}
                      {opportunity.exchanges && (
                        <div className="text-xs text-gray-400 mb-3">
                          <span>Available on: {opportunity.exchanges.join(', ')}</span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex flex-col gap-2 ml-4">
                    <Button size="sm" className="whitespace-nowrap">
                      <Zap className="h-3 w-3 mr-1" />
                      Execute
                    </Button>
                    <Button size="sm" variant="outline" className="whitespace-nowrap">
                      <ExternalLink className="h-3 w-3 mr-1" />
                      Details
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {filteredOpportunities.length === 0 && (
        <Card className="gaming-card">
          <CardContent className="text-center py-12">
            <Radar className="h-12 w-12 mx-auto mb-4 text-blue-500 opacity-50" />
            <h3 className="text-lg font-semibold mb-2">No Opportunities Found</h3>
            <p className="text-gray-400">
              Scanner is actively monitoring markets. New opportunities will appear here in real-time.
            </p>
          </CardContent>
        </Card>
      )}

      {/* Hidden audio element for alerts */}
      <audio ref={audioRef} preload="auto">
        <source src="/alert-sound.mp3" type="audio/mpeg" />
      </audio>
    </div>
  );
}