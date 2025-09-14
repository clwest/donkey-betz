import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';
import { Slider } from '@/components/ui/slider';
import { Label } from '@/components/ui/label';
import {
  Target, TrendingUp, TrendingDown, BarChart3, Gauge,
  Calendar, DollarSign, Percent, Activity, AlertTriangle,
  CheckCircle, Clock, Zap, Brain, Settings, Sparkles,
  ChevronRight, ChevronDown, ChevronUp, Info
} from 'lucide-react';

interface OutcomePrediction {
  id: string;
  decisionTitle: string;
  entity: string;
  domain: string;
  timeHorizon: '1d' | '7d' | '30d' | '90d' | '1y';
  scenarios: {
    optimistic: OutcomeScenario;
    realistic: OutcomeScenario;
    pessimistic: OutcomeScenario;
  };
  confidenceIntervals: {
    '95%': { lower: number; upper: number };
    '90%': { lower: number; upper: number };
    '68%': { lower: number; upper: number };
  };
  monteCarloRuns: number;
  volatility: number;
  correlation: number;
  historicalAccuracy: number;
  keyFactors: Factor[];
  riskMetrics: RiskMetrics;
}

interface OutcomeScenario {
  probability: number;
  roi: number;
  portfolioImpact: number;
  timeToTarget: number;
  description: string;
  keyDrivers: string[];
}

interface Factor {
  name: string;
  impact: number; // -1 to 1
  probability: number;
  description: string;
  category: 'market' | 'technical' | 'fundamental' | 'sentiment';
}

interface RiskMetrics {
  maxDrawdown: number;
  sharpeRatio: number;
  valueAtRisk: number;
  expectedShortfall: number;
  probabilityOfLoss: number;
}

interface SimulationSettings {
  runs: number;
  timeHorizon: string;
  portfolioSize: number;
  riskTolerance: number;
}

const TIME_HORIZONS = {
  '1d': '1 Day',
  '7d': '7 Days',
  '30d': '30 Days',
  '90d': '90 Days',
  '1y': '1 Year'
};

const SCENARIO_COLORS = {
  optimistic: 'text-green-500 bg-green-500/10',
  realistic: 'text-blue-500 bg-blue-500/10',
  pessimistic: 'text-red-500 bg-red-500/10'
};

export function OutcomePrediction() {
  const [predictions, setPredictions] = useState<OutcomePrediction[]>([]);
  const [selectedPrediction, setSelectedPrediction] = useState<string | null>(null);
  const [simulationSettings, setSimulationSettings] = useState<SimulationSettings>({
    runs: 10000,
    timeHorizon: '30d',
    portfolioSize: 100000,
    riskTolerance: 0.5
  });
  const [showSettings, setShowSettings] = useState(false);
  const [selectedTab, setSelectedTab] = useState('overview');

  useEffect(() => {
    // Mock prediction data
    const mockPredictions: OutcomePrediction[] = [
      {
        id: 'pred_001',
        decisionTitle: 'BTC Position - 25% Allocation',
        entity: 'Bitcoin (BTC)',
        domain: 'CRYPTO',
        timeHorizon: '30d',
        scenarios: {
          optimistic: {
            probability: 0.25,
            roi: 0.28,
            portfolioImpact: 0.07,
            timeToTarget: 18,
            description: 'Strong institutional adoption, regulatory clarity drives momentum',
            keyDrivers: ['ETF inflows', 'Regulatory approval', 'Institutional adoption']
          },
          realistic: {
            probability: 0.50,
            roi: 0.12,
            portfolioImpact: 0.03,
            timeToTarget: 25,
            description: 'Steady growth following market trends and technical patterns',
            keyDrivers: ['Technical breakout', 'Market correlation', 'Volume confirmation']
          },
          pessimistic: {
            probability: 0.25,
            roi: -0.15,
            portfolioImpact: -0.0375,
            timeToTarget: 0,
            description: 'Market correction, regulatory concerns, or macro headwinds',
            keyDrivers: ['Regulatory crackdown', 'Market sell-off', 'Liquidity concerns']
          }
        },
        confidenceIntervals: {
          '95%': { lower: -0.22, upper: 0.35 },
          '90%': { lower: -0.18, upper: 0.31 },
          '68%': { lower: -0.08, upper: 0.24 }
        },
        monteCarloRuns: 50000,
        volatility: 0.65,
        correlation: 0.42,
        historicalAccuracy: 0.73,
        keyFactors: [
          {
            name: 'Market Sentiment',
            impact: 0.8,
            probability: 0.65,
            description: 'Overall crypto market sentiment and institutional interest',
            category: 'sentiment'
          },
          {
            name: 'Regulatory Environment',
            impact: 0.9,
            probability: 0.45,
            description: 'Government policies and regulatory clarity',
            category: 'fundamental'
          },
          {
            name: 'Technical Indicators',
            impact: 0.6,
            probability: 0.78,
            description: 'RSI, MACD, and support/resistance levels',
            category: 'technical'
          },
          {
            name: 'Whale Activity',
            impact: 0.7,
            probability: 0.55,
            description: 'Large holder accumulation and distribution patterns',
            category: 'market'
          }
        ],
        riskMetrics: {
          maxDrawdown: 0.28,
          sharpeRatio: 1.45,
          valueAtRisk: 0.12,
          expectedShortfall: 0.18,
          probabilityOfLoss: 0.35
        }
      },
      {
        id: 'pred_002',
        decisionTitle: 'NVDA Options Strategy',
        entity: 'NVIDIA Corporation',
        domain: 'TRADING',
        timeHorizon: '7d',
        scenarios: {
          optimistic: {
            probability: 0.30,
            roi: 0.45,
            portfolioImpact: 0.09,
            timeToTarget: 5,
            description: 'Earnings beat expectations, AI sector momentum continues',
            keyDrivers: ['Earnings surprise', 'AI demand', 'Guidance raise']
          },
          realistic: {
            probability: 0.45,
            roi: 0.18,
            portfolioImpact: 0.036,
            timeToTarget: 6,
            description: 'Meet expectations, moderate price appreciation',
            keyDrivers: ['In-line earnings', 'Sector rotation', 'Options decay']
          },
          pessimistic: {
            probability: 0.25,
            roi: -0.32,
            portfolioImpact: -0.064,
            timeToTarget: 0,
            description: 'Earnings miss or guidance cut, sector weakness',
            keyDrivers: ['Earnings miss', 'Margin pressure', 'Competition concerns']
          }
        },
        confidenceIntervals: {
          '95%': { lower: -0.42, upper: 0.58 },
          '90%': { lower: -0.35, upper: 0.52 },
          '68%': { lower: -0.15, upper: 0.35 }
        },
        monteCarloRuns: 25000,
        volatility: 0.45,
        correlation: 0.68,
        historicalAccuracy: 0.71,
        keyFactors: [
          {
            name: 'Earnings Results',
            impact: 0.95,
            probability: 0.85,
            description: 'Quarterly earnings vs consensus estimates',
            category: 'fundamental'
          },
          {
            name: 'AI Sector Momentum',
            impact: 0.75,
            probability: 0.70,
            description: 'Overall AI and semiconductor sector performance',
            category: 'market'
          },
          {
            name: 'Options Greeks',
            impact: 0.6,
            probability: 0.90,
            description: 'Time decay, volatility changes, and delta hedging',
            category: 'technical'
          }
        ],
        riskMetrics: {
          maxDrawdown: 0.35,
          sharpeRatio: 2.15,
          valueAtRisk: 0.18,
          expectedShortfall: 0.25,
          probabilityOfLoss: 0.40
        }
      }
    ];

    setPredictions(mockPredictions);
    if (mockPredictions.length > 0) {
      setSelectedPrediction(mockPredictions[0].id);
    }
  }, []);

  const selectedPred = predictions.find(p => p.id === selectedPrediction);

  const getScenarioIcon = (scenario: 'optimistic' | 'realistic' | 'pessimistic') => {
    switch (scenario) {
      case 'optimistic': return <TrendingUp className="h-4 w-4 text-green-500" />;
      case 'realistic': return <Activity className="h-4 w-4 text-blue-500" />;
      case 'pessimistic': return <TrendingDown className="h-4 w-4 text-red-500" />;
    }
  };

  const getFactorColor = (impact: number) => {
    if (impact > 0.7) return 'text-green-500';
    if (impact > 0.4) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'market': return <BarChart3 className="h-3 w-3" />;
      case 'technical': return <Activity className="h-3 w-3" />;
      case 'fundamental': return <Target className="h-3 w-3" />;
      case 'sentiment': return <Brain className="h-3 w-3" />;
      default: return <Info className="h-3 w-3" />;
    }
  };

  if (!selectedPred) {
    return (
      <Card className="gaming-card">
        <CardContent className="text-center py-12">
          <Brain className="h-12 w-12 mx-auto mb-4 text-gray-500 opacity-50" />
          <p className="text-gray-400">No prediction data available</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            Decision Outcome Prediction
          </h2>
          <p className="text-gray-400 text-sm mt-1">
            Monte Carlo simulations with confidence intervals for decision outcomes
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant="outline" className="px-3 py-1">
            <Sparkles className="h-4 w-4 mr-2" />
            {selectedPred.monteCarloRuns.toLocaleString()} simulations
          </Badge>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowSettings(!showSettings)}
          >
            <Settings className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Decision Selector */}
      <div className="flex gap-2 flex-wrap">
        {predictions.map(pred => (
          <Button
            key={pred.id}
            variant={selectedPrediction === pred.id ? 'default' : 'outline'}
            size="sm"
            onClick={() => setSelectedPrediction(pred.id)}
          >
            {pred.decisionTitle}
          </Button>
        ))}
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <Card className="gaming-card border-blue-500/20">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              Simulation Settings
            </CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div>
                <Label>Monte Carlo Runs</Label>
                <Slider
                  value={[simulationSettings.runs]}
                  onValueChange={(value) => setSimulationSettings(prev => ({ ...prev, runs: value[0] }))}
                  max={100000}
                  min={1000}
                  step={1000}
                  className="mt-2"
                />
                <p className="text-sm text-gray-400 mt-1">{simulationSettings.runs.toLocaleString()} simulations</p>
              </div>
              <div>
                <Label>Portfolio Size</Label>
                <Slider
                  value={[simulationSettings.portfolioSize]}
                  onValueChange={(value) => setSimulationSettings(prev => ({ ...prev, portfolioSize: value[0] }))}
                  max={1000000}
                  min={10000}
                  step={10000}
                  className="mt-2"
                />
                <p className="text-sm text-gray-400 mt-1">${simulationSettings.portfolioSize.toLocaleString()}</p>
              </div>
            </div>
            <div className="space-y-4">
              <div>
                <Label>Risk Tolerance</Label>
                <Slider
                  value={[simulationSettings.riskTolerance * 100]}
                  onValueChange={(value) => setSimulationSettings(prev => ({ ...prev, riskTolerance: value[0] / 100 }))}
                  max={100}
                  min={10}
                  step={5}
                  className="mt-2"
                />
                <p className="text-sm text-gray-400 mt-1">{(simulationSettings.riskTolerance * 100).toFixed(0)}% risk tolerance</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <Tabs value={selectedTab} onValueChange={setSelectedTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="scenarios">Scenarios</TabsTrigger>
          <TabsTrigger value="confidence">Confidence Intervals</TabsTrigger>
          <TabsTrigger value="factors">Key Factors</TabsTrigger>
          <TabsTrigger value="risk">Risk Analysis</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Prediction Summary */}
            <Card className="gaming-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="h-5 w-5" />
                  {selectedPred.decisionTitle}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-400">Entity</p>
                    <p className="font-bold">{selectedPred.entity}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Domain</p>
                    <Badge variant="outline">{selectedPred.domain}</Badge>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Time Horizon</p>
                    <p className="font-bold">{TIME_HORIZONS[selectedPred.timeHorizon]}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Historical Accuracy</p>
                    <p className="font-bold text-blue-500">
                      {(selectedPred.historicalAccuracy * 100).toFixed(0)}%
                    </p>
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">Volatility</span>
                    <span className="font-bold">{(selectedPred.volatility * 100).toFixed(0)}%</span>
                  </div>
                  <Progress value={selectedPred.volatility * 100} className="h-2" />
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">Market Correlation</span>
                    <span className="font-bold">{(selectedPred.correlation * 100).toFixed(0)}%</span>
                  </div>
                  <Progress value={selectedPred.correlation * 100} className="h-2" />
                </div>
              </CardContent>
            </Card>

            {/* Expected Outcomes */}
            <Card className="gaming-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  Expected Outcomes
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {Object.entries(selectedPred.scenarios).map(([scenario, data]) => (
                  <div key={scenario} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {getScenarioIcon(scenario as any)}
                        <span className="font-medium capitalize">{scenario}</span>
                        <Badge variant="outline" className="text-xs">
                          {(data.probability * 100).toFixed(0)}%
                        </Badge>
                      </div>
                      <div className="text-right">
                        <p className={`font-bold ${data.roi >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                          {data.roi >= 0 ? '+' : ''}{(data.roi * 100).toFixed(1)}%
                        </p>
                        <p className="text-xs text-gray-400">
                          {data.timeToTarget > 0 ? `${data.timeToTarget}d` : 'N/A'}
                        </p>
                      </div>
                    </div>
                    <Progress value={data.probability * 100} className="h-1" />
                  </div>
                ))}

                <Separator />

                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">Expected ROI</span>
                    <span className="font-bold text-blue-500">
                      +{((
                        selectedPred.scenarios.optimistic.roi * selectedPred.scenarios.optimistic.probability +
                        selectedPred.scenarios.realistic.roi * selectedPred.scenarios.realistic.probability +
                        selectedPred.scenarios.pessimistic.roi * selectedPred.scenarios.pessimistic.probability
                      ) * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">Portfolio Impact</span>
                    <span className="font-bold">
                      {((
                        selectedPred.scenarios.optimistic.portfolioImpact * selectedPred.scenarios.optimistic.probability +
                        selectedPred.scenarios.realistic.portfolioImpact * selectedPred.scenarios.realistic.probability +
                        selectedPred.scenarios.pessimistic.portfolioImpact * selectedPred.scenarios.pessimistic.probability
                      ) * 100).toFixed(2)}%
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Scenarios Tab */}
        <TabsContent value="scenarios" className="space-y-4">
          {Object.entries(selectedPred.scenarios).map(([scenario, data]) => (
            <Card key={scenario} className={`gaming-card border-l-4 ${
              scenario === 'optimistic' ? 'border-green-500' :
              scenario === 'realistic' ? 'border-blue-500' :
              'border-red-500'
            }`}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {getScenarioIcon(scenario as any)}
                    <h3 className="text-lg font-semibold capitalize">{scenario} Scenario</h3>
                    <Badge className={SCENARIO_COLORS[scenario as keyof typeof SCENARIO_COLORS]}>
                      {(data.probability * 100).toFixed(0)}% Probability
                    </Badge>
                  </div>
                  <div className="text-right">
                    <p className={`text-2xl font-bold ${data.roi >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                      {data.roi >= 0 ? '+' : ''}{(data.roi * 100).toFixed(1)}%
                    </p>
                    <p className="text-sm text-gray-400">Expected ROI</p>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-gray-300">{data.description}</p>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-dark-800 rounded-lg p-3">
                    <p className="text-sm text-gray-400">Portfolio Impact</p>
                    <p className={`text-lg font-bold ${data.portfolioImpact >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                      {data.portfolioImpact >= 0 ? '+' : ''}{(data.portfolioImpact * 100).toFixed(2)}%
                    </p>
                  </div>
                  <div className="bg-dark-800 rounded-lg p-3">
                    <p className="text-sm text-gray-400">Time to Target</p>
                    <p className="text-lg font-bold">
                      {data.timeToTarget > 0 ? `${data.timeToTarget} days` : 'Not applicable'}
                    </p>
                  </div>
                  <div className="bg-dark-800 rounded-lg p-3">
                    <p className="text-sm text-gray-400">Dollar Impact</p>
                    <p className={`text-lg font-bold ${data.portfolioImpact >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                      {data.portfolioImpact >= 0 ? '+' : ''}${(data.portfolioImpact * simulationSettings.portfolioSize).toLocaleString()}
                    </p>
                  </div>
                </div>

                <div>
                  <p className="text-sm font-medium mb-2">Key Drivers:</p>
                  <div className="flex flex-wrap gap-2">
                    {data.keyDrivers.map((driver, index) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {driver}
                      </Badge>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        {/* Confidence Intervals Tab */}
        <TabsContent value="confidence" className="space-y-6">
          <Card className="gaming-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Gauge className="h-5 w-5" />
                Statistical Confidence Intervals
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {Object.entries(selectedPred.confidenceIntervals).map(([level, interval]) => (
                <div key={level} className="space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold">{level} Confidence Interval</h3>
                    <Badge variant="outline">
                      {(interval.lower * 100).toFixed(1)}% to {(interval.upper * 100).toFixed(1)}%
                    </Badge>
                  </div>

                  <div className="relative bg-dark-800 rounded-lg p-4">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm text-red-400">
                        Loss: {(Math.abs(interval.lower) * 100).toFixed(1)}%
                      </span>
                      <span className="text-sm text-gray-400">0%</span>
                      <span className="text-sm text-green-400">
                        Gain: {(interval.upper * 100).toFixed(1)}%
                      </span>
                    </div>

                    <div className="relative h-6 bg-gray-700 rounded-full overflow-hidden">
                      <div
                        className="absolute h-full bg-gradient-to-r from-red-500 via-yellow-500 to-green-500 opacity-60"
                        style={{
                          left: `${Math.max(0, (interval.lower + 0.5) * 100)}%`,
                          right: `${Math.max(0, (0.5 - interval.upper) * 100)}%`
                        }}
                      />
                      <div className="absolute left-1/2 top-0 w-0.5 h-full bg-white transform -translate-x-0.5" />
                    </div>

                    <p className="text-xs text-gray-400 mt-2">
                      There is a {level} probability that the outcome will fall within this range
                    </p>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="text-center">
                      <p className="text-sm text-gray-400">Dollar Range (Lower)</p>
                      <p className="text-lg font-bold text-red-400">
                        ${(interval.lower * simulationSettings.portfolioSize).toLocaleString()}
                      </p>
                    </div>
                    <div className="text-center">
                      <p className="text-sm text-gray-400">Dollar Range (Upper)</p>
                      <p className="text-lg font-bold text-green-400">
                        +${(interval.upper * simulationSettings.portfolioSize).toLocaleString()}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Key Factors Tab */}
        <TabsContent value="factors" className="space-y-4">
          {selectedPred.keyFactors.map(factor => (
            <Card key={factor.name} className="gaming-card">
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      {getCategoryIcon(factor.category)}
                      <h3 className="font-semibold">{factor.name}</h3>
                      <Badge variant="outline" className="text-xs capitalize">
                        {factor.category}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-400 mb-3">{factor.description}</p>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-sm text-gray-400">Impact Score</span>
                          <span className={`font-bold ${getFactorColor(factor.impact)}`}>
                            {(factor.impact * 100).toFixed(0)}%
                          </span>
                        </div>
                        <Progress value={factor.impact * 100} className="h-2" />
                      </div>
                      <div>
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-sm text-gray-400">Probability</span>
                          <span className="font-bold text-blue-500">
                            {(factor.probability * 100).toFixed(0)}%
                          </span>
                        </div>
                        <Progress value={factor.probability * 100} className="h-2" />
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        {/* Risk Analysis Tab */}
        <TabsContent value="risk" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <Card className="gaming-card">
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-400">Max Drawdown</span>
                  <TrendingDown className="h-4 w-4 text-red-500" />
                </div>
                <p className="text-2xl font-bold text-red-500">
                  -{(selectedPred.riskMetrics.maxDrawdown * 100).toFixed(1)}%
                </p>
                <p className="text-sm text-gray-400 mt-1">Worst case scenario</p>
              </CardContent>
            </Card>

            <Card className="gaming-card">
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-400">Sharpe Ratio</span>
                  <Activity className="h-4 w-4 text-blue-500" />
                </div>
                <p className="text-2xl font-bold text-blue-500">
                  {selectedPred.riskMetrics.sharpeRatio.toFixed(2)}
                </p>
                <p className="text-sm text-gray-400 mt-1">Risk-adjusted return</p>
              </CardContent>
            </Card>

            <Card className="gaming-card">
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-400">Value at Risk</span>
                  <AlertTriangle className="h-4 w-4 text-yellow-500" />
                </div>
                <p className="text-2xl font-bold text-yellow-500">
                  -{(selectedPred.riskMetrics.valueAtRisk * 100).toFixed(1)}%
                </p>
                <p className="text-sm text-gray-400 mt-1">95% confidence, 1-day</p>
              </CardContent>
            </Card>

            <Card className="gaming-card">
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-400">Expected Shortfall</span>
                  <TrendingDown className="h-4 w-4 text-red-500" />
                </div>
                <p className="text-2xl font-bold text-red-500">
                  -{(selectedPred.riskMetrics.expectedShortfall * 100).toFixed(1)}%
                </p>
                <p className="text-sm text-gray-400 mt-1">Conditional VaR</p>
              </CardContent>
            </Card>

            <Card className="gaming-card">
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-400">Loss Probability</span>
                  <Percent className="h-4 w-4 text-orange-500" />
                </div>
                <p className="text-2xl font-bold text-orange-500">
                  {(selectedPred.riskMetrics.probabilityOfLoss * 100).toFixed(0)}%
                </p>
                <Progress value={selectedPred.riskMetrics.probabilityOfLoss * 100} className="mt-2 h-1" />
              </CardContent>
            </Card>

            <Card className="gaming-card">
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-400">Simulation Runs</span>
                  <Sparkles className="h-4 w-4 text-purple-500" />
                </div>
                <p className="text-2xl font-bold text-purple-500">
                  {(selectedPred.monteCarloRuns / 1000).toFixed(0)}K
                </p>
                <p className="text-sm text-gray-400 mt-1">Monte Carlo</p>
              </CardContent>
            </Card>
          </div>

          <Alert>
            <Info className="h-4 w-4" />
            <AlertDescription>
              Risk metrics are based on {selectedPred.monteCarloRuns.toLocaleString()} Monte Carlo simulations
              using historical volatility and correlation data. Past performance does not guarantee future results.
            </AlertDescription>
          </Alert>
        </TabsContent>
      </Tabs>
    </div>
  );
}