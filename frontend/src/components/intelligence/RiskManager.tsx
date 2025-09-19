import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Shield, AlertTriangle, TrendingDown, DollarSign,
  Activity, BarChart3, Settings, Bell, Target,
  Gauge, Zap, Clock, RefreshCw, X, CheckCircle,
  AlertCircle, Minus, Plus, Lock, Unlock
} from 'lucide-react';

interface RiskMetrics {
  overallRisk: number;
  portfolioValue: number;
  dailyVaR: number; // Value at Risk
  maxDrawdown: number;
  sharpeRatio: number;
  correlation: number;
  leverage: number;
  liquidityRisk: number;
}

interface PositionRisk {
  id: string;
  entity: string;
  domain: 'SPORTS_BETTING' | 'CRYPTO' | 'TRADING' | 'REAL_ESTATE' | 'BUSINESS';
  currentValue: number;
  unrealizedPnL: number;
  riskScore: number;
  correlation: number;
  timeDecay: number;
  stopLoss?: number;
  takeProfitTarget?: number;
  positionSize: number;
  maxSize: number;
  alerts: string[];
  status: 'healthy' | 'warning' | 'critical';
}

interface RiskRule {
  id: string;
  name: string;
  description: string;
  type: 'position_size' | 'correlation' | 'drawdown' | 'var' | 'concentration';
  threshold: number;
  currentValue: number;
  action: 'alert' | 'reduce' | 'close' | 'block';
  isActive: boolean;
  triggered: boolean;
  lastTriggered?: string;
}

interface AutoAction {
  id: string;
  type: 'stop_loss' | 'take_profit' | 'position_resize' | 'hedge_add' | 'correlation_reduce';
  entityId: string;
  description: string;
  triggerValue: number;
  currentValue: number;
  status: 'pending' | 'executed' | 'cancelled';
  executedAt?: string;
  result?: string;
}

const DOMAIN_COLORS = {
  SPORTS_BETTING: 'bg-green-500/10 text-green-500',
  CRYPTO: 'bg-orange-500/10 text-orange-500',
  TRADING: 'bg-blue-500/10 text-blue-500',
  REAL_ESTATE: 'bg-purple-500/10 text-purple-500',
  BUSINESS: 'bg-indigo-500/10 text-indigo-500'
};

export function RiskManager() {
  const [riskMetrics, setRiskMetrics] = useState<RiskMetrics>({
    overallRisk: 0.42,
    portfolioValue: 87340,
    dailyVaR: 2840,
    maxDrawdown: 0.08,
    sharpeRatio: 1.67,
    correlation: 0.73,
    leverage: 1.24,
    liquidityRisk: 0.31
  });

  const [positions, setPositions] = useState<PositionRisk[]>([]);
  const [riskRules, setRiskRules] = useState<RiskRule[]>([]);
  const [autoActions, setAutoActions] = useState<AutoAction[]>([]);
  const [isAutoRiskEnabled, setIsAutoRiskEnabled] = useState(true);
  const [selectedTab, setSelectedTab] = useState('overview');

  useEffect(() => {
    // Mock position data
    const mockPositions: PositionRisk[] = [
      {
        id: 'pos_001',
        entity: 'BTC/USD Position',
        domain: 'CRYPTO',
        currentValue: 25000,
        unrealizedPnL: 2340,
        riskScore: 0.67,
        correlation: 0.82,
        timeDecay: 0.15,
        stopLoss: 62000,
        takeProfitTarget: 72000,
        positionSize: 0.38,
        maxSize: 0.25,
        alerts: ['Position size exceeds limit', 'High correlation with ETH position'],
        status: 'critical'
      },
      {
        id: 'pos_002',
        entity: 'NVDA Options',
        domain: 'TRADING',
        currentValue: 18500,
        unrealizedPnL: -1200,
        riskScore: 0.54,
        correlation: 0.31,
        timeDecay: 0.08,
        stopLoss: 820,
        positionSize: 0.21,
        maxSize: 0.30,
        alerts: ['Theta decay accelerating'],
        status: 'warning'
      },
      {
        id: 'pos_003',
        entity: 'Lakers ML Bet',
        domain: 'SPORTS_BETTING',
        currentValue: 5000,
        unrealizedPnL: 0,
        riskScore: 0.23,
        correlation: 0.05,
        timeDecay: 0.95,
        positionSize: 0.06,
        maxSize: 0.10,
        alerts: [],
        status: 'healthy'
      }
    ];

    // Mock risk rules
    const mockRiskRules: RiskRule[] = [
      {
        id: 'rule_001',
        name: 'Position Size Limit',
        description: 'No single position should exceed 25% of portfolio',
        type: 'position_size',
        threshold: 0.25,
        currentValue: 0.38,
        action: 'reduce',
        isActive: true,
        triggered: true,
        lastTriggered: new Date().toISOString()
      },
      {
        id: 'rule_002',
        name: 'Portfolio Correlation',
        description: 'Keep crypto positions correlation below 70%',
        type: 'correlation',
        threshold: 0.70,
        currentValue: 0.82,
        action: 'alert',
        isActive: true,
        triggered: true
      },
      {
        id: 'rule_003',
        name: 'Daily VaR Limit',
        description: 'Daily Value at Risk should not exceed $3,000',
        type: 'var',
        threshold: 3000,
        currentValue: 2840,
        action: 'block',
        isActive: true,
        triggered: false
      },
      {
        id: 'rule_004',
        name: 'Max Drawdown Protection',
        description: 'Maximum drawdown should not exceed 12%',
        type: 'drawdown',
        threshold: 0.12,
        currentValue: 0.08,
        action: 'close',
        isActive: true,
        triggered: false
      }
    ];

    // Mock auto actions
    const mockAutoActions: AutoAction[] = [
      {
        id: 'action_001',
        type: 'position_resize',
        entityId: 'pos_001',
        description: 'Reduce BTC position from 38% to 25% of portfolio',
        triggerValue: 0.25,
        currentValue: 0.38,
        status: 'pending'
      },
      {
        id: 'action_002',
        type: 'stop_loss',
        entityId: 'pos_002',
        description: 'Execute stop loss on NVDA options at $820',
        triggerValue: 820,
        currentValue: 847,
        status: 'pending'
      }
    ];

    setPositions(mockPositions);
    setRiskRules(mockRiskRules);
    setAutoActions(mockAutoActions);
  }, []);

  const getRiskColor = (risk: number) => {
    if (risk <= 0.3) return 'text-green-500';
    if (risk <= 0.6) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'bg-green-500';
      case 'warning': return 'bg-yellow-500';
      case 'critical': return 'bg-red-500';
      default: return 'bg-muted/50';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return CheckCircle;
      case 'warning': return AlertTriangle;
      case 'critical': return AlertCircle;
      default: return CheckCircle;
    }
  };

  const executeAutoAction = (actionId: string) => {
    setAutoActions(prev =>
      prev.map(action =>
        action.id === actionId
          ? { ...action, status: 'executed', executedAt: new Date().toISOString(), result: 'Success' }
          : action
      )
    );
  };

  const cancelAutoAction = (actionId: string) => {
    setAutoActions(prev =>
      prev.map(action =>
        action.id === actionId
          ? { ...action, status: 'cancelled' }
          : action
      )
    );
  };

  const toggleRiskRule = (ruleId: string) => {
    setRiskRules(prev =>
      prev.map(rule =>
        rule.id === ruleId
          ? { ...rule, isActive: !rule.isActive }
          : rule
      )
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold bg-gradient-to-r from-red-400 to-yellow-500 bg-clip-text text-transparent">
            Automated Risk Management
          </h2>
          <p className="text-muted-foreground text-sm mt-1">
            Portfolio-aware position sizing and automated risk controls
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant="outline" className="px-3 py-1">
            <div className={`w-2 h-2 rounded-full ${isAutoRiskEnabled ? 'bg-green-500 animate-pulse' : 'bg-muted/50'} mr-2`} />
            {isAutoRiskEnabled ? 'Auto Risk ON' : 'Manual Mode'}
          </Badge>
          <Switch
            checked={isAutoRiskEnabled}
            onCheckedChange={setIsAutoRiskEnabled}
          />
          <Button variant="outline" size="sm">
            <Settings className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Critical Alerts */}
      {riskRules.some(rule => rule.triggered && rule.isActive) && (
        <Alert className="border-red-500/50 bg-red-500/5">
          <AlertTriangle className="h-4 w-4 text-red-500" />
          <AlertDescription className="text-red-500">
            <strong>RISK RULES TRIGGERED!</strong> {' '}
            {riskRules.filter(rule => rule.triggered && rule.isActive).length} risk management rules require attention.
          </AlertDescription>
        </Alert>
      )}

      <Tabs value={selectedTab} onValueChange={setSelectedTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">Risk Overview</TabsTrigger>
          <TabsTrigger value="positions">Positions</TabsTrigger>
          <TabsTrigger value="rules">Risk Rules</TabsTrigger>
          <TabsTrigger value="actions">Auto Actions</TabsTrigger>
        </TabsList>

        {/* Risk Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          {/* Risk Metrics Grid */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="bg-card">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Overall Risk</span>
                  <Gauge className="h-4 w-4 text-orange-500" />
                </div>
                <p className={`text-2xl font-bold mt-2 ${getRiskColor(riskMetrics.overallRisk)}`}>
                  {(riskMetrics.overallRisk * 100).toFixed(0)}%
                </p>
                <Progress value={riskMetrics.overallRisk * 100} className="mt-2 h-1" />
              </CardContent>
            </Card>

            <Card className="bg-card">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Daily VaR</span>
                  <TrendingDown className="h-4 w-4 text-red-500" />
                </div>
                <p className="text-2xl font-bold mt-2 text-red-500">
                  ${riskMetrics.dailyVaR.toLocaleString()}
                </p>
                <p className="text-sm text-muted-foreground mt-1">95% confidence</p>
              </CardContent>
            </Card>

            <Card className="bg-card">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Correlation</span>
                  <Activity className="h-4 w-4 text-yellow-500" />
                </div>
                <p className={`text-2xl font-bold mt-2 ${riskMetrics.correlation > 0.7 ? 'text-red-500' : 'text-green-500'}`}>
                  {(riskMetrics.correlation * 100).toFixed(0)}%
                </p>
                <p className="text-sm text-muted-foreground mt-1">Avg position</p>
              </CardContent>
            </Card>

            <Card className="bg-card">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Sharpe Ratio</span>
                  <BarChart3 className="h-4 w-4 text-blue-500" />
                </div>
                <p className="text-2xl font-bold mt-2 text-blue-500">
                  {riskMetrics.sharpeRatio.toFixed(2)}
                </p>
                <p className="text-sm text-muted-foreground mt-1">Risk-adjusted</p>
              </CardContent>
            </Card>
          </div>

          {/* Risk Distribution Chart */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="bg-card">
              <CardHeader>
                <CardTitle>Position Risk Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {positions.map(position => (
                    <div key={position.id} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Badge className={`text-xs ${DOMAIN_COLORS[position.domain]}`}>
                            {position.entity}
                          </Badge>
                          <span className="text-sm text-muted-foreground">
                            {(position.positionSize * 100).toFixed(1)}%
                          </span>
                        </div>
                        <span className={`text-sm font-bold ${getRiskColor(position.riskScore)}`}>
                          Risk: {(position.riskScore * 100).toFixed(0)}%
                        </span>
                      </div>
                      <Progress value={position.positionSize * 100} className="h-2" />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card className="bg-card">
              <CardHeader>
                <CardTitle>Risk Metrics Breakdown</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-muted-foreground">Max Drawdown</span>
                      <span className="text-sm font-bold text-red-500">
                        {(riskMetrics.maxDrawdown * 100).toFixed(1)}%
                      </span>
                    </div>
                    <Progress value={riskMetrics.maxDrawdown * 100} className="h-2" />
                  </div>

                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-muted-foreground">Leverage</span>
                      <span className="text-sm font-bold text-blue-500">
                        {riskMetrics.leverage.toFixed(2)}x
                      </span>
                    </div>
                    <Progress value={(riskMetrics.leverage / 3) * 100} className="h-2" />
                  </div>

                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-muted-foreground">Liquidity Risk</span>
                      <span className="text-sm font-bold text-yellow-500">
                        {(riskMetrics.liquidityRisk * 100).toFixed(0)}%
                      </span>
                    </div>
                    <Progress value={riskMetrics.liquidityRisk * 100} className="h-2" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Positions Tab */}
        <TabsContent value="positions" className="space-y-4">
          {positions.map(position => {
            const StatusIcon = getStatusIcon(position.status);

            return (
              <Card key={position.id} className="bg-card">
                <CardContent className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3 flex-1">
                      <div className={`w-1 h-20 rounded-full ${getStatusColor(position.status)}`} />

                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <StatusIcon className={`h-4 w-4 ${
                              position.status === 'healthy' ? 'text-green-500' :
                              position.status === 'warning' ? 'text-yellow-500' :
                              'text-red-500'
                            }`} />
                            <h3 className="font-semibold">{position.entity}</h3>
                            <Badge className={`text-xs ${DOMAIN_COLORS[position.domain]}`}>
                              {position.domain.replace('_', ' ')}
                            </Badge>
                          </div>
                          <Badge className={`${getStatusColor(position.status)} text-foreground`}>
                            {position.status}
                          </Badge>
                        </div>

                        <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-3">
                          <div className="text-center">
                            <p className="text-xs text-muted-foreground">Value</p>
                            <p className="font-bold">${position.currentValue.toLocaleString()}</p>
                          </div>
                          <div className="text-center">
                            <p className="text-xs text-muted-foreground">P&L</p>
                            <p className={`font-bold ${position.unrealizedPnL >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                              {position.unrealizedPnL >= 0 ? '+' : ''}${position.unrealizedPnL.toLocaleString()}
                            </p>
                          </div>
                          <div className="text-center">
                            <p className="text-xs text-muted-foreground">Size</p>
                            <p className={`font-bold ${position.positionSize > position.maxSize ? 'text-red-500' : 'text-green-500'}`}>
                              {(position.positionSize * 100).toFixed(1)}%
                            </p>
                          </div>
                          <div className="text-center">
                            <p className="text-xs text-muted-foreground">Risk</p>
                            <p className={`font-bold ${getRiskColor(position.riskScore)}`}>
                              {(position.riskScore * 100).toFixed(0)}%
                            </p>
                          </div>
                          <div className="text-center">
                            <p className="text-xs text-muted-foreground">Correlation</p>
                            <p className={`font-bold ${position.correlation > 0.7 ? 'text-red-500' : 'text-green-500'}`}>
                              {(position.correlation * 100).toFixed(0)}%
                            </p>
                          </div>
                        </div>

                        {/* Stop Loss & Take Profit */}
                        {(position.stopLoss || position.takeProfitTarget) && (
                          <div className="bg-card rounded-lg p-2 mb-3">
                            <div className="grid grid-cols-2 gap-3 text-xs">
                              {position.stopLoss && (
                                <div>
                                  <p className="text-muted-foreground">Stop Loss</p>
                                  <p className="font-bold text-red-500">${position.stopLoss.toLocaleString()}</p>
                                </div>
                              )}
                              {position.takeProfitTarget && (
                                <div>
                                  <p className="text-muted-foreground">Take Profit</p>
                                  <p className="font-bold text-green-500">${position.takeProfitTarget.toLocaleString()}</p>
                                </div>
                              )}
                            </div>
                          </div>
                        )}

                        {/* Alerts */}
                        {position.alerts.length > 0 && (
                          <div className="flex flex-wrap gap-1">
                            {position.alerts.map((alert, index) => (
                              <Badge key={index} variant="destructive" className="text-xs">
                                <Bell className="h-3 w-3 mr-1" />
                                {alert}
                              </Badge>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="flex flex-col gap-2 ml-4">
                      <Button size="sm" variant="outline">
                        <Target className="h-3 w-3 mr-1" />
                        Adjust
                      </Button>
                      {position.status === 'critical' && (
                        <Button size="sm" variant="destructive">
                          <X className="h-3 w-3 mr-1" />
                          Close
                        </Button>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </TabsContent>

        {/* Risk Rules Tab */}
        <TabsContent value="rules" className="space-y-4">
          {riskRules.map(rule => (
            <Card key={rule.id} className={`bg-card ${rule.triggered ? 'border-red-500/50' : ''}`}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-semibold flex items-center gap-2">
                        {rule.triggered && <AlertTriangle className="h-4 w-4 text-red-500" />}
                        {rule.name}
                      </h3>
                      <div className="flex items-center gap-2">
                        <Badge variant={rule.triggered ? 'destructive' : 'outline'}>
                          {rule.triggered ? 'TRIGGERED' : 'OK'}
                        </Badge>
                        <Switch
                          checked={rule.isActive}
                          onCheckedChange={() => toggleRiskRule(rule.id)}
                        />
                        {rule.isActive ? <Lock className="h-4 w-4 text-green-500" /> : <Unlock className="h-4 w-4 text-muted-foreground" />}
                      </div>
                    </div>

                    <p className="text-sm text-muted-foreground mb-3">{rule.description}</p>

                    <div className="grid grid-cols-3 gap-4">
                      <div>
                        <p className="text-xs text-muted-foreground">Threshold</p>
                        <p className="font-bold">
                          {rule.type === 'var' ? '$' : ''}{rule.threshold.toLocaleString()}{rule.type !== 'var' ? '%' : ''}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Current</p>
                        <p className={`font-bold ${rule.triggered ? 'text-red-500' : 'text-green-500'}`}>
                          {rule.type === 'var' ? '$' : ''}{rule.currentValue.toLocaleString()}{rule.type !== 'var' ? '%' : ''}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Action</p>
                        <Badge variant="outline" className="text-xs">
                          {rule.action.toUpperCase()}
                        </Badge>
                      </div>
                    </div>

                    {rule.triggered && rule.lastTriggered && (
                      <p className="text-xs text-red-500 mt-2">
                        Last triggered: {new Date(rule.lastTriggered).toLocaleString()}
                      </p>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        {/* Auto Actions Tab */}
        <TabsContent value="actions" className="space-y-4">
          {autoActions.map(action => (
            <Card key={action.id} className="bg-card">
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Zap className="h-4 w-4 text-yellow-500" />
                        <h3 className="font-semibold capitalize">
                          {action.type.replace('_', ' ')}
                        </h3>
                      </div>
                      <Badge className={`${
                        action.status === 'pending' ? 'bg-yellow-500' :
                        action.status === 'executed' ? 'bg-green-500' :
                        'bg-muted/50'
                      } text-foreground`}>
                        {action.status}
                      </Badge>
                    </div>

                    <p className="text-sm text-muted-foreground mb-3">{action.description}</p>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-xs text-muted-foreground">Trigger Value</p>
                        <p className="font-bold">{action.triggerValue.toLocaleString()}</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Current Value</p>
                        <p className="font-bold">{action.currentValue.toLocaleString()}</p>
                      </div>
                    </div>

                    {action.executedAt && (
                      <p className="text-xs text-green-500 mt-2">
                        Executed: {new Date(action.executedAt).toLocaleString()} - {action.result}
                      </p>
                    )}
                  </div>

                  {action.status === 'pending' && (
                    <div className="flex gap-2 ml-4">
                      <Button
                        size="sm"
                        onClick={() => executeAutoAction(action.id)}
                      >
                        <CheckCircle className="h-3 w-3 mr-1" />
                        Execute
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => cancelAutoAction(action.id)}
                      >
                        <X className="h-3 w-3 mr-1" />
                        Cancel
                      </Button>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}

          {autoActions.filter(a => a.status === 'pending').length === 0 && (
            <Card className="bg-card">
              <CardContent className="text-center py-8">
                <Shield className="h-8 w-8 mx-auto mb-2 text-green-500" />
                <p className="text-muted-foreground">No pending auto actions. Risk management is operating normally.</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}