import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';
import {
  Zap, Shield, Lock, Unlock, AlertTriangle, CheckCircle,
  Clock, DollarSign, Settings, Activity, Target, Brain,
  Play, Pause, X, RefreshCw, ExternalLink, Eye,
  TrendingUp, TrendingDown, BarChart3, Gauge, AlertCircle, Info
} from 'lucide-react';

interface ExecutionRule {
  id: string;
  name: string;
  description: string;
  type: 'confidence_threshold' | 'risk_limit' | 'correlation_check' | 'time_window' | 'position_size';
  threshold: number;
  isActive: boolean;
  priority: 'low' | 'medium' | 'high' | 'critical';
  action: 'block' | 'require_approval' | 'reduce_size' | 'delay';
}

interface AutoExecution {
  id: string;
  decisionTitle: string;
  entity: string;
  domain: string;
  executionType: 'immediate' | 'scheduled' | 'conditional';
  conditions: {
    minConfidence: number;
    maxRisk: number;
    maxPosition: number;
    timeWindow: { start: string; end: string };
  };
  safeguards: {
    doubleConfirmation: boolean;
    maxDailyAmount: number;
    cooldownPeriod: number;
    stopLoss: number;
    takeProfitTarget?: number;
  };
  currentMetrics: {
    confidence: number;
    risk: number;
    positionSize: number;
    correlation: number;
  };
  status: 'pending' | 'approved' | 'queued' | 'executing' | 'completed' | 'failed' | 'cancelled';
  scheduledAt?: string;
  executedAt?: string;
  result?: {
    success: boolean;
    amount: number;
    price: number;
    fees: number;
    message: string;
  };
  approvals: {
    riskManager: boolean;
    portfolioManager: boolean;
    compliance: boolean;
  };
}

interface SystemSafeguards {
  globalKillSwitch: boolean;
  maxDailyRisk: number;
  maxPositionSize: number;
  requireApprovalAbove: number;
  emergencyStopLoss: number;
  maxExecutionsPerHour: number;
  whitelistedAssets: string[];
  blacklistedAssets: string[];
}

interface ExecutionMetrics {
  totalExecutions: number;
  successRate: number;
  avgExecutionTime: number;
  totalVolume: number;
  savedTime: string;
  riskPrevented: number;
}

export function AutoExecution() {
  const [executions, setExecutions] = useState<AutoExecution[]>([]);
  const [executionRules, setExecutionRules] = useState<ExecutionRule[]>([]);
  const [safeguards, setSafeguards] = useState<SystemSafeguards>({
    globalKillSwitch: false,
    maxDailyRisk: 0.05,
    maxPositionSize: 0.25,
    requireApprovalAbove: 10000,
    emergencyStopLoss: 0.15,
    maxExecutionsPerHour: 10,
    whitelistedAssets: ['BTC', 'ETH', 'NVDA', 'TSLA'],
    blacklistedAssets: ['MEME', 'SHIB']
  });
  const [metrics, setMetrics] = useState<ExecutionMetrics>({
    totalExecutions: 247,
    successRate: 0.91,
    avgExecutionTime: 2.3,
    totalVolume: 2450000,
    savedTime: '180h 45m',
    riskPrevented: 45000
  });
  const [selectedTab, setSelectedTab] = useState('queue');
  const [showSettings, setShowSettings] = useState(false);

  useEffect(() => {
    // Mock execution rules
    const mockRules: ExecutionRule[] = [
      {
        id: 'rule_001',
        name: 'Minimum Confidence Threshold',
        description: 'Only execute decisions with 80%+ confidence',
        type: 'confidence_threshold',
        threshold: 0.80,
        isActive: true,
        priority: 'high',
        action: 'block'
      },
      {
        id: 'rule_002',
        name: 'Maximum Risk Limit',
        description: 'Block executions exceeding 30% risk score',
        type: 'risk_limit',
        threshold: 0.30,
        isActive: true,
        priority: 'critical',
        action: 'block'
      },
      {
        id: 'rule_003',
        name: 'Position Size Limit',
        description: 'Require approval for positions >20% of portfolio',
        type: 'position_size',
        threshold: 0.20,
        isActive: true,
        priority: 'high',
        action: 'require_approval'
      },
      {
        id: 'rule_004',
        name: 'Trading Hours Only',
        description: 'Only execute during market hours',
        type: 'time_window',
        threshold: 1,
        isActive: true,
        priority: 'medium',
        action: 'delay'
      },
      {
        id: 'rule_005',
        name: 'Correlation Check',
        description: 'Reduce size if portfolio correlation >70%',
        type: 'correlation_check',
        threshold: 0.70,
        isActive: true,
        priority: 'medium',
        action: 'reduce_size'
      }
    ];

    // Mock auto executions
    const mockExecutions: AutoExecution[] = [
      {
        id: 'exec_001',
        decisionTitle: 'BTC Buy Signal - 3% Allocation',
        entity: 'Bitcoin',
        domain: 'CRYPTO',
        executionType: 'conditional',
        conditions: {
          minConfidence: 0.85,
          maxRisk: 0.25,
          maxPosition: 0.20,
          timeWindow: { start: '09:00', end: '16:00' }
        },
        safeguards: {
          doubleConfirmation: false,
          maxDailyAmount: 50000,
          cooldownPeriod: 60,
          stopLoss: 0.08,
          takeProfitTarget: 0.15
        },
        currentMetrics: {
          confidence: 0.87,
          risk: 0.23,
          positionSize: 0.18,
          correlation: 0.65
        },
        status: 'queued',
        scheduledAt: new Date(Date.now() + 15 * 60 * 1000).toISOString(),
        approvals: {
          riskManager: true,
          portfolioManager: true,
          compliance: false
        }
      },
      {
        id: 'exec_002',
        decisionTitle: 'NVDA Options Hedge',
        entity: 'NVIDIA',
        domain: 'TRADING',
        executionType: 'immediate',
        conditions: {
          minConfidence: 0.75,
          maxRisk: 0.35,
          maxPosition: 0.15,
          timeWindow: { start: '09:30', end: '16:00' }
        },
        safeguards: {
          doubleConfirmation: true,
          maxDailyAmount: 25000,
          cooldownPeriod: 30,
          stopLoss: 0.12
        },
        currentMetrics: {
          confidence: 0.76,
          risk: 0.34,
          positionSize: 0.12,
          correlation: 0.42
        },
        status: 'approved',
        approvals: {
          riskManager: true,
          portfolioManager: true,
          compliance: true
        }
      },
      {
        id: 'exec_003',
        decisionTitle: 'Lakers Spread Bet',
        entity: 'Lakers vs Warriors',
        domain: 'SPORTS_BETTING',
        executionType: 'scheduled',
        conditions: {
          minConfidence: 0.90,
          maxRisk: 0.15,
          maxPosition: 0.05,
          timeWindow: { start: '18:00', end: '19:00' }
        },
        safeguards: {
          doubleConfirmation: false,
          maxDailyAmount: 5000,
          cooldownPeriod: 0,
          stopLoss: 1.0
        },
        currentMetrics: {
          confidence: 0.92,
          risk: 0.14,
          positionSize: 0.04,
          correlation: 0.08
        },
        status: 'pending',
        scheduledAt: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString(),
        approvals: {
          riskManager: false,
          portfolioManager: false,
          compliance: false
        }
      }
    ];

    setExecutionRules(mockRules);
    setExecutions(mockExecutions);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-500';
      case 'approved': return 'bg-blue-500';
      case 'queued': return 'bg-purple-500';
      case 'executing': return 'bg-orange-500 animate-pulse';
      case 'completed': return 'bg-green-500';
      case 'failed': return 'bg-red-500';
      case 'cancelled': return 'bg-muted/50';
      default: return 'bg-muted/50';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'text-red-500';
      case 'high': return 'text-orange-500';
      case 'medium': return 'text-yellow-500';
      case 'low': return 'text-green-500';
      default: return 'text-muted-foreground';
    }
  };

  const getActionIcon = (action: string) => {
    switch (action) {
      case 'block': return <X className="h-4 w-4 text-red-500" />;
      case 'require_approval': return <Lock className="h-4 w-4 text-yellow-500" />;
      case 'reduce_size': return <TrendingDown className="h-4 w-4 text-blue-500" />;
      case 'delay': return <Clock className="h-4 w-4 text-purple-500" />;
      default: return <Info className="h-4 w-4 text-muted-foreground" />;
    }
  };

  const toggleRule = (ruleId: string) => {
    setExecutionRules(prev =>
      prev.map(rule =>
        rule.id === ruleId ? { ...rule, isActive: !rule.isActive } : rule
      )
    );
  };

  const executeNow = (executionId: string) => {
    setExecutions(prev =>
      prev.map(exec =>
        exec.id === executionId
          ? {
              ...exec,
              status: 'executing',
              executedAt: new Date().toISOString()
            }
          : exec
      )
    );

    // Simulate execution completion after 3 seconds
    setTimeout(() => {
      setExecutions(prev =>
        prev.map(exec =>
          exec.id === executionId
            ? {
                ...exec,
                status: 'completed',
                result: {
                  success: true,
                  amount: 15000,
                  price: 65200,
                  fees: 45,
                  message: 'Execution completed successfully'
                }
              }
            : exec
        )
      );
    }, 3000);
  };

  const cancelExecution = (executionId: string) => {
    setExecutions(prev =>
      prev.map(exec =>
        exec.id === executionId ? { ...exec, status: 'cancelled' } : exec
      )
    );
  };

  const getTimeRemaining = (scheduledAt: string) => {
    const now = new Date().getTime();
    const scheduled = new Date(scheduledAt).getTime();
    const diff = scheduled - now;

    if (diff <= 0) return 'Now';

    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold bg-gradient-to-r from-orange-400 to-red-500 bg-clip-text text-transparent">
            Automated Execution System
          </h2>
          <p className="text-muted-foreground text-sm mt-1">
            Execute decisions while you sleep - with comprehensive safeguards
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant="outline" className="px-3 py-1">
            <div className={`w-2 h-2 rounded-full ${safeguards.globalKillSwitch ? 'bg-red-500' : 'bg-green-500 animate-pulse'} mr-2`} />
            {safeguards.globalKillSwitch ? 'DISABLED' : 'ACTIVE'}
          </Badge>
          <Switch
            checked={!safeguards.globalKillSwitch}
            onCheckedChange={(checked) => setSafeguards(prev => ({ ...prev, globalKillSwitch: !checked }))}
          />
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowSettings(!showSettings)}
          >
            <Settings className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Kill Switch Warning */}
      {safeguards.globalKillSwitch && (
        <Alert className="border-red-500/50 bg-red-500/5">
          <AlertTriangle className="h-4 w-4 text-red-500" />
          <AlertDescription className="text-red-500">
            <strong>GLOBAL KILL SWITCH ACTIVATED!</strong> All automated executions are disabled.
            Enable the system above to resume automated trading.
          </AlertDescription>
        </Alert>
      )}

      {/* System Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
        <Card className="bg-card">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Executions</span>
              <Zap className="h-4 w-4 text-orange-500" />
            </div>
            <p className="text-2xl font-bold mt-2">{metrics.totalExecutions}</p>
            <p className="text-sm text-muted-foreground mt-1">Total</p>
          </CardContent>
        </Card>

        <Card className="bg-card">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Success Rate</span>
              <CheckCircle className="h-4 w-4 text-green-500" />
            </div>
            <p className="text-2xl font-bold mt-2 text-green-500">
              {(metrics.successRate * 100).toFixed(0)}%
            </p>
            <Progress value={metrics.successRate * 100} className="mt-2 h-1" />
          </CardContent>
        </Card>

        <Card className="bg-card">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Avg Speed</span>
              <Activity className="h-4 w-4 text-blue-500" />
            </div>
            <p className="text-2xl font-bold mt-2 text-blue-500">
              {metrics.avgExecutionTime}s
            </p>
            <p className="text-sm text-muted-foreground mt-1">Execution</p>
          </CardContent>
        </Card>

        <Card className="bg-card">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Volume</span>
              <DollarSign className="h-4 w-4 text-purple-500" />
            </div>
            <p className="text-2xl font-bold mt-2 text-purple-500">
              ${(metrics.totalVolume / 1000000).toFixed(1)}M
            </p>
            <p className="text-sm text-muted-foreground mt-1">Total</p>
          </CardContent>
        </Card>

        <Card className="bg-card">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Time Saved</span>
              <Clock className="h-4 w-4 text-yellow-500" />
            </div>
            <p className="text-2xl font-bold mt-2 text-yellow-500">
              {metrics.savedTime}
            </p>
            <p className="text-sm text-muted-foreground mt-1">Manual work</p>
          </CardContent>
        </Card>

        <Card className="bg-card">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Risk Prevented</span>
              <Shield className="h-4 w-4 text-green-500" />
            </div>
            <p className="text-2xl font-bold mt-2 text-green-500">
              ${metrics.riskPrevented.toLocaleString()}
            </p>
            <p className="text-sm text-muted-foreground mt-1">By safeguards</p>
          </CardContent>
        </Card>
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <Card className="bg-card border-orange-500/20">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              System Safeguards
            </CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div>
                <Label>Max Daily Risk (%)</Label>
                <Slider
                  value={[safeguards.maxDailyRisk * 100]}
                  onValueChange={(value) => setSafeguards(prev => ({ ...prev, maxDailyRisk: value[0] / 100 }))}
                  max={20}
                  min={1}
                  step={0.5}
                  className="mt-2"
                />
                <p className="text-sm text-muted-foreground mt-1">{(safeguards.maxDailyRisk * 100).toFixed(1)}% max daily portfolio risk</p>
              </div>
              <div>
                <Label>Max Position Size (%)</Label>
                <Slider
                  value={[safeguards.maxPositionSize * 100]}
                  onValueChange={(value) => setSafeguards(prev => ({ ...prev, maxPositionSize: value[0] / 100 }))}
                  max={50}
                  min={5}
                  step={1}
                  className="mt-2"
                />
                <p className="text-sm text-muted-foreground mt-1">{(safeguards.maxPositionSize * 100).toFixed(0)}% max single position</p>
              </div>
              <div>
                <Label>Emergency Stop Loss (%)</Label>
                <Slider
                  value={[safeguards.emergencyStopLoss * 100]}
                  onValueChange={(value) => setSafeguards(prev => ({ ...prev, emergencyStopLoss: value[0] / 100 }))}
                  max={30}
                  min={5}
                  step={1}
                  className="mt-2"
                />
                <p className="text-sm text-muted-foreground mt-1">{(safeguards.emergencyStopLoss * 100).toFixed(0)}% emergency stop</p>
              </div>
            </div>
            <div className="space-y-4">
              <div>
                <Label>Approval Threshold ($)</Label>
                <Slider
                  value={[safeguards.requireApprovalAbove]}
                  onValueChange={(value) => setSafeguards(prev => ({ ...prev, requireApprovalAbove: value[0] }))}
                  max={100000}
                  min={1000}
                  step={1000}
                  className="mt-2"
                />
                <p className="text-sm text-muted-foreground mt-1">${safeguards.requireApprovalAbove.toLocaleString()} requires approval</p>
              </div>
              <div>
                <Label>Max Executions/Hour</Label>
                <Slider
                  value={[safeguards.maxExecutionsPerHour]}
                  onValueChange={(value) => setSafeguards(prev => ({ ...prev, maxExecutionsPerHour: value[0] }))}
                  max={50}
                  min={1}
                  step={1}
                  className="mt-2"
                />
                <p className="text-sm text-muted-foreground mt-1">{safeguards.maxExecutionsPerHour} max per hour</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <Tabs value={selectedTab} onValueChange={setSelectedTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="queue">Execution Queue</TabsTrigger>
          <TabsTrigger value="rules">Safeguard Rules</TabsTrigger>
          <TabsTrigger value="history">Execution History</TabsTrigger>
        </TabsList>

        {/* Execution Queue Tab */}
        <TabsContent value="queue" className="space-y-4">
          {executions.filter(exec => ['pending', 'approved', 'queued', 'executing'].includes(exec.status)).map(execution => (
            <Card key={execution.id} className="bg-card">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="font-semibold">{execution.decisionTitle}</h3>
                      <Badge className={`${getStatusColor(execution.status)} text-foreground`}>
                        {execution.status.toUpperCase()}
                      </Badge>
                      <Badge variant="outline" className="text-xs">
                        {execution.domain}
                      </Badge>
                      <Badge variant="outline" className="text-xs capitalize">
                        {execution.executionType}
                      </Badge>
                    </div>
                    <p className="text-muted-foreground text-sm">{execution.entity}</p>
                  </div>
                  {execution.scheduledAt && (
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Clock className="h-4 w-4" />
                      {execution.status === 'executing' ? 'Executing...' : getTimeRemaining(execution.scheduledAt)}
                    </div>
                  )}
                </div>
              </CardHeader>

              <CardContent className="space-y-4">
                {/* Current Metrics vs Conditions */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  <div className="bg-card rounded-lg p-2">
                    <p className="text-xs text-muted-foreground">Confidence</p>
                    <p className={`font-bold ${execution.currentMetrics.confidence >= execution.conditions.minConfidence ? 'text-green-500' : 'text-red-500'}`}>
                      {(execution.currentMetrics.confidence * 100).toFixed(0)}%
                    </p>
                    <p className="text-xs text-muted-foreground">Min: {(execution.conditions.minConfidence * 100).toFixed(0)}%</p>
                  </div>
                  <div className="bg-card rounded-lg p-2">
                    <p className="text-xs text-muted-foreground">Risk</p>
                    <p className={`font-bold ${execution.currentMetrics.risk <= execution.conditions.maxRisk ? 'text-green-500' : 'text-red-500'}`}>
                      {(execution.currentMetrics.risk * 100).toFixed(0)}%
                    </p>
                    <p className="text-xs text-muted-foreground">Max: {(execution.conditions.maxRisk * 100).toFixed(0)}%</p>
                  </div>
                  <div className="bg-card rounded-lg p-2">
                    <p className="text-xs text-muted-foreground">Position</p>
                    <p className={`font-bold ${execution.currentMetrics.positionSize <= execution.conditions.maxPosition ? 'text-green-500' : 'text-red-500'}`}>
                      {(execution.currentMetrics.positionSize * 100).toFixed(1)}%
                    </p>
                    <p className="text-xs text-muted-foreground">Max: {(execution.conditions.maxPosition * 100).toFixed(0)}%</p>
                  </div>
                  <div className="bg-card rounded-lg p-2">
                    <p className="text-xs text-muted-foreground">Correlation</p>
                    <p className={`font-bold ${execution.currentMetrics.correlation <= 0.7 ? 'text-green-500' : 'text-yellow-500'}`}>
                      {(execution.currentMetrics.correlation * 100).toFixed(0)}%
                    </p>
                    <p className="text-xs text-muted-foreground">Portfolio</p>
                  </div>
                </div>

                {/* Safeguards */}
                <div className="bg-card rounded-lg p-3">
                  <h4 className="font-medium mb-2">Active Safeguards</h4>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div className="flex items-center gap-2">
                      {execution.safeguards.doubleConfirmation ? <CheckCircle className="h-3 w-3 text-green-500" /> : <X className="h-3 w-3 text-muted-foreground" />}
                      <span>Double Confirmation</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Shield className="h-3 w-3 text-blue-500" />
                      <span>Stop Loss: {(execution.safeguards.stopLoss * 100).toFixed(0)}%</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <DollarSign className="h-3 w-3 text-yellow-500" />
                      <span>Daily Max: ${execution.safeguards.maxDailyAmount.toLocaleString()}</span>
                    </div>
                    {execution.safeguards.takeProfitTarget && (
                      <div className="flex items-center gap-2">
                        <Target className="h-3 w-3 text-green-500" />
                        <span>Take Profit: {(execution.safeguards.takeProfitTarget * 100).toFixed(0)}%</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Approvals */}
                <div>
                  <h4 className="font-medium mb-2">Approvals</h4>
                  <div className="grid grid-cols-3 gap-2">
                    <div className={`flex items-center gap-2 p-2 rounded ${execution.approvals.riskManager ? 'bg-green-500/10' : 'bg-red-500/10'}`}>
                      {execution.approvals.riskManager ? <CheckCircle className="h-4 w-4 text-green-500" /> : <X className="h-4 w-4 text-red-500" />}
                      <span className="text-sm">Risk Manager</span>
                    </div>
                    <div className={`flex items-center gap-2 p-2 rounded ${execution.approvals.portfolioManager ? 'bg-green-500/10' : 'bg-red-500/10'}`}>
                      {execution.approvals.portfolioManager ? <CheckCircle className="h-4 w-4 text-green-500" /> : <X className="h-4 w-4 text-red-500" />}
                      <span className="text-sm">Portfolio Mgr</span>
                    </div>
                    <div className={`flex items-center gap-2 p-2 rounded ${execution.approvals.compliance ? 'bg-green-500/10' : 'bg-red-500/10'}`}>
                      {execution.approvals.compliance ? <CheckCircle className="h-4 w-4 text-green-500" /> : <X className="h-4 w-4 text-red-500" />}
                      <span className="text-sm">Compliance</span>
                    </div>
                  </div>
                </div>

                {/* Execution Result */}
                {execution.result && (
                  <Alert className={execution.result.success ? 'border-green-500/50 bg-green-500/5' : 'border-red-500/50 bg-red-500/5'}>
                    {execution.result.success ? <CheckCircle className="h-4 w-4 text-green-500" /> : <AlertCircle className="h-4 w-4 text-red-500" />}
                    <AlertDescription>
                      <strong>{execution.result.success ? 'SUCCESS:' : 'FAILED:'}</strong> {execution.result.message}
                      {execution.result.success && (
                        <div className="mt-2 grid grid-cols-3 gap-2 text-sm">
                          <span>Amount: ${execution.result.amount.toLocaleString()}</span>
                          <span>Price: ${execution.result.price.toLocaleString()}</span>
                          <span>Fees: ${execution.result.fees}</span>
                        </div>
                      )}
                    </AlertDescription>
                  </Alert>
                )}

                {/* Actions */}
                <div className="flex gap-2 pt-2 border-t border-gray-700">
                  {execution.status === 'approved' && (
                    <Button
                      size="sm"
                      onClick={() => executeNow(execution.id)}
                      disabled={safeguards.globalKillSwitch}
                    >
                      <Zap className="h-4 w-4 mr-2" />
                      Execute Now
                    </Button>
                  )}
                  {execution.status === 'executing' && (
                    <Button size="sm" disabled>
                      <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                      Executing...
                    </Button>
                  )}
                  {['pending', 'approved', 'queued'].includes(execution.status) && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => cancelExecution(execution.id)}
                    >
                      <X className="h-4 w-4 mr-2" />
                      Cancel
                    </Button>
                  )}
                  <Button size="sm" variant="outline">
                    <Eye className="h-4 w-4 mr-2" />
                    Details
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}

          {executions.filter(exec => ['pending', 'approved', 'queued', 'executing'].includes(exec.status)).length === 0 && (
            <Card className="bg-card">
              <CardContent className="text-center py-12">
                <Zap className="h-12 w-12 mx-auto mb-4 text-muted-foreground opacity-50" />
                <h3 className="text-lg font-semibold mb-2">No Pending Executions</h3>
                <p className="text-muted-foreground">
                  Automated executions will appear here when conditions are met.
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Safeguard Rules Tab */}
        <TabsContent value="rules" className="space-y-4">
          {executionRules.map(rule => (
            <Card key={rule.id} className="bg-card">
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-semibold flex items-center gap-2">
                        {getActionIcon(rule.action)}
                        {rule.name}
                      </h3>
                      <div className="flex items-center gap-2">
                        <Badge className={getPriorityColor(rule.priority)}>
                          {rule.priority.toUpperCase()}
                        </Badge>
                        <Switch
                          checked={rule.isActive}
                          onCheckedChange={() => toggleRule(rule.id)}
                        />
                        {rule.isActive ? <Lock className="h-4 w-4 text-green-500" /> : <Unlock className="h-4 w-4 text-muted-foreground" />}
                      </div>
                    </div>

                    <p className="text-sm text-muted-foreground mb-3">{rule.description}</p>

                    <div className="grid grid-cols-3 gap-4">
                      <div>
                        <p className="text-xs text-muted-foreground">Type</p>
                        <Badge variant="outline" className="text-xs capitalize">
                          {rule.type.replace('_', ' ')}
                        </Badge>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Threshold</p>
                        <p className="font-bold">
                          {rule.type.includes('threshold') || rule.type.includes('limit') || rule.type.includes('check') ?
                            `${(rule.threshold * 100).toFixed(0)}%` :
                            rule.threshold.toString()
                          }
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Action</p>
                        <Badge variant="outline" className="text-xs capitalize">
                          {rule.action.replace('_', ' ')}
                        </Badge>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        {/* History Tab */}
        <TabsContent value="history" className="space-y-4">
          {executions.filter(exec => ['completed', 'failed', 'cancelled'].includes(exec.status)).map(execution => (
            <Card key={execution.id} className="bg-card">
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="font-semibold">{execution.decisionTitle}</h3>
                      <Badge className={`${getStatusColor(execution.status)} text-foreground`}>
                        {execution.status.toUpperCase()}
                      </Badge>
                      <Badge variant="outline" className="text-xs">
                        {execution.domain}
                      </Badge>
                    </div>
                    <p className="text-muted-foreground text-sm">{execution.entity}</p>
                  </div>
                  <div className="text-right text-sm text-muted-foreground">
                    {execution.executedAt && new Date(execution.executedAt).toLocaleString()}
                  </div>
                </div>

                {execution.result && (
                  <div className="mt-3 p-3 bg-card rounded-lg">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
                      <div>
                        <p className="text-muted-foreground">Result</p>
                        <p className={`font-bold ${execution.result.success ? 'text-green-500' : 'text-red-500'}`}>
                          {execution.result.success ? 'Success' : 'Failed'}
                        </p>
                      </div>
                      {execution.result.success && (
                        <>
                          <div>
                            <p className="text-muted-foreground">Amount</p>
                            <p className="font-bold">${execution.result.amount.toLocaleString()}</p>
                          </div>
                          <div>
                            <p className="text-muted-foreground">Price</p>
                            <p className="font-bold">${execution.result.price.toLocaleString()}</p>
                          </div>
                          <div>
                            <p className="text-muted-foreground">Fees</p>
                            <p className="font-bold">${execution.result.fees}</p>
                          </div>
                        </>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground mt-2">{execution.result.message}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}

          {executions.filter(exec => ['completed', 'failed', 'cancelled'].includes(exec.status)).length === 0 && (
            <Card className="bg-card">
              <CardContent className="text-center py-12">
                <BarChart3 className="h-12 w-12 mx-auto mb-4 text-muted-foreground opacity-50" />
                <h3 className="text-lg font-semibold mb-2">No Execution History</h3>
                <p className="text-muted-foreground">
                  Completed executions will appear here for review and analysis.
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}