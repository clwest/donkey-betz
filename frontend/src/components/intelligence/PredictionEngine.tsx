import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Clock, TrendingUp, Target, Zap, Brain, AlertTriangle,
  Calendar, Timer, Sparkles, Eye, Play, Pause, Settings
} from 'lucide-react';

interface OpportunityPrediction {
  id: string;
  domain: 'SPORTS_BETTING' | 'CRYPTO' | 'TRADING' | 'REAL_ESTATE' | 'BUSINESS';
  entity: string;
  prediction: string;
  confidence: number;
  timeHorizon: '1h' | '3h' | '6h' | '12h' | '24h' | '3d' | '7d';
  expectedROI: number;
  riskLevel: number;
  triggers: string[];
  currentPrice?: number;
  targetPrice?: number;
  probabilityBands: {
    optimistic: number;
    realistic: number;
    pessimistic: number;
  };
  historicalAccuracy: number;
  timestamp: string;
  status: 'monitoring' | 'triggered' | 'expired' | 'executed';
}

interface PredictionMetrics {
  totalPredictions: number;
  accuracy: number;
  profitablePredictions: number;
  avgTimeToTrigger: string;
  activeMonitors: number;
}

const DOMAIN_COLORS = {
  SPORTS_BETTING: 'text-green-500 bg-green-500/10',
  CRYPTO: 'text-orange-500 bg-orange-500/10',
  TRADING: 'text-blue-500 bg-blue-500/10',
  REAL_ESTATE: 'text-purple-500 bg-purple-500/10',
  BUSINESS: 'text-indigo-500 bg-indigo-500/10'
};

const TIME_HORIZON_LABELS = {
  '1h': '1 Hour',
  '3h': '3 Hours',
  '6h': '6 Hours',
  '12h': '12 Hours',
  '24h': '24 Hours',
  '3d': '3 Days',
  '7d': '7 Days'
};

export function PredictionEngine() {
  const [predictions, setPredictions] = useState<OpportunityPrediction[]>([]);
  const [metrics, setMetrics] = useState<PredictionMetrics>({
    totalPredictions: 247,
    accuracy: 0.73,
    profitablePredictions: 182,
    avgTimeToTrigger: '4h 23m',
    activeMonitors: 47
  });
  const [isMonitoring, setIsMonitoring] = useState(true);
  const [selectedTimeHorizon, setSelectedTimeHorizon] = useState<string>('all');

  useEffect(() => {
    // Mock prediction data - in real implementation, this would come from AI analysis
    const mockPredictions: OpportunityPrediction[] = [
      {
        id: 'pred_001',
        domain: 'SPORTS_BETTING',
        entity: 'Lakers vs Warriors',
        prediction: 'Lakers spread will move from -2.5 to +1.5 after injury news at 6PM EST',
        confidence: 0.87,
        timeHorizon: '3h',
        expectedROI: 0.23,
        riskLevel: 0.31,
        triggers: ['Injury report release', 'Line movement >3 points', 'Volume spike'],
        currentPrice: -2.5,
        targetPrice: 1.5,
        probabilityBands: {
          optimistic: 0.92,
          realistic: 0.87,
          pessimistic: 0.73
        },
        historicalAccuracy: 0.82,
        timestamp: new Date(Date.now() + 3 * 60 * 60 * 1000).toISOString(),
        status: 'monitoring'
      },
      {
        id: 'pred_002',
        domain: 'CRYPTO',
        entity: 'BTC/USD',
        prediction: 'Bitcoin will breakout above $67,500 resistance within 12 hours based on whale accumulation patterns',
        confidence: 0.78,
        timeHorizon: '12h',
        expectedROI: 0.15,
        riskLevel: 0.45,
        triggers: ['Whale accumulation >500 BTC', 'RSI divergence', 'Volume confirmation'],
        currentPrice: 65200,
        targetPrice: 69500,
        probabilityBands: {
          optimistic: 0.85,
          realistic: 0.78,
          pessimistic: 0.64
        },
        historicalAccuracy: 0.71,
        timestamp: new Date(Date.now() + 12 * 60 * 60 * 1000).toISOString(),
        status: 'monitoring'
      },
      {
        id: 'pred_003',
        domain: 'TRADING',
        entity: 'NVDA',
        prediction: 'NVIDIA will hit $920 before earnings (3 days) with 83% confidence due to AI sector momentum',
        confidence: 0.83,
        timeHorizon: '3d',
        expectedROI: 0.28,
        riskLevel: 0.38,
        triggers: ['AI sector rotation', 'Options flow bullish', 'Analyst upgrades'],
        currentPrice: 847,
        targetPrice: 920,
        probabilityBands: {
          optimistic: 0.91,
          realistic: 0.83,
          pessimistic: 0.67
        },
        historicalAccuracy: 0.79,
        timestamp: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString(),
        status: 'monitoring'
      },
      {
        id: 'pred_004',
        domain: 'REAL_ESTATE',
        entity: 'Austin Market - District 5',
        prediction: 'Zillow estimates will adjust +8% in District 5 after infrastructure announcement next week',
        confidence: 0.69,
        timeHorizon: '7d',
        expectedROI: 0.12,
        riskLevel: 0.25,
        triggers: ['Infrastructure vote passage', 'Zoning committee approval', 'Developer interest'],
        probabilityBands: {
          optimistic: 0.78,
          realistic: 0.69,
          pessimistic: 0.52
        },
        historicalAccuracy: 0.68,
        timestamp: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
        status: 'monitoring'
      }
    ];

    setPredictions(mockPredictions);
  }, []);

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-500';
    if (confidence >= 0.6) return 'text-yellow-500';
    return 'text-orange-500';
  };

  const getRiskColor = (risk: number) => {
    if (risk <= 0.3) return 'text-green-500';
    if (risk <= 0.6) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getROIColor = (roi: number) => {
    if (roi >= 0.2) return 'text-green-500';
    if (roi >= 0.1) return 'text-blue-500';
    return 'text-muted-foreground';
  };

  const getTimeRemaining = (timestamp: string) => {
    const now = new Date().getTime();
    const target = new Date(timestamp).getTime();
    const diff = target - now;

    if (diff <= 0) return 'Expired';

    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

    if (hours > 24) {
      const days = Math.floor(hours / 24);
      return `${days}d ${hours % 24}h`;
    }

    return `${hours}h ${minutes}m`;
  };

  const filteredPredictions = predictions.filter(pred =>
    selectedTimeHorizon === 'all' || pred.timeHorizon === selectedTimeHorizon
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-500 bg-clip-text text-transparent">
            AI Prediction Engine
          </h2>
          <p className="text-muted-foreground text-sm mt-1">
            Predicting opportunities before they happen across all domains
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant="outline" className="px-3 py-1">
            <div className={`w-2 h-2 rounded-full ${isMonitoring ? 'bg-green-500 animate-pulse' : 'bg-muted/50'} mr-2`} />
            {isMonitoring ? 'Monitoring' : 'Paused'}
          </Badge>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsMonitoring(!isMonitoring)}
          >
            {isMonitoring ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
          </Button>
          <Button variant="outline" size="sm">
            <Settings className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Metrics Overview */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card className="bg-card">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Predictions</span>
              <Eye className="h-4 w-4 text-purple-500" />
            </div>
            <p className="text-2xl font-bold mt-2">{metrics.totalPredictions}</p>
            <p className="text-sm text-muted-foreground mt-1">All time</p>
          </CardContent>
        </Card>

        <Card className="bg-card">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Accuracy</span>
              <Target className="h-4 w-4 text-green-500" />
            </div>
            <p className="text-2xl font-bold mt-2 text-green-500">
              {(metrics.accuracy * 100).toFixed(0)}%
            </p>
            <Progress value={metrics.accuracy * 100} className="mt-2 h-1" />
          </CardContent>
        </Card>

        <Card className="bg-card">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Profitable</span>
              <TrendingUp className="h-4 w-4 text-blue-500" />
            </div>
            <p className="text-2xl font-bold mt-2">{metrics.profitablePredictions}</p>
            <p className="text-sm text-muted-foreground mt-1">Total wins</p>
          </CardContent>
        </Card>

        <Card className="bg-card">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Avg Time</span>
              <Timer className="h-4 w-4 text-yellow-500" />
            </div>
            <p className="text-2xl font-bold mt-2">{metrics.avgTimeToTrigger}</p>
            <p className="text-sm text-muted-foreground mt-1">To trigger</p>
          </CardContent>
        </Card>

        <Card className="bg-card">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Active</span>
              <Sparkles className="h-4 w-4 text-pink-500" />
            </div>
            <p className="text-2xl font-bold mt-2">{metrics.activeMonitors}</p>
            <p className="text-sm text-muted-foreground mt-1">Monitoring</p>
          </CardContent>
        </Card>
      </div>

      {/* Time Horizon Filter */}
      <div className="flex items-center gap-2">
        <span className="text-sm text-muted-foreground">Time Horizon:</span>
        <Button
          variant={selectedTimeHorizon === 'all' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setSelectedTimeHorizon('all')}
        >
          All
        </Button>
        {Object.entries(TIME_HORIZON_LABELS).map(([key, label]) => (
          <Button
            key={key}
            variant={selectedTimeHorizon === key ? 'default' : 'outline'}
            size="sm"
            onClick={() => setSelectedTimeHorizon(key)}
          >
            {label}
          </Button>
        ))}
      </div>

      {/* Alert for High Confidence Predictions */}
      {predictions.some(p => p.confidence >= 0.85 && p.status === 'monitoring') && (
        <Alert>
          <Brain className="h-4 w-4" />
          <AlertDescription>
            {predictions.filter(p => p.confidence >= 0.85 && p.status === 'monitoring').length} high-confidence predictions (85%+) are actively monitored
          </AlertDescription>
        </Alert>
      )}

      {/* Predictions Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {filteredPredictions.map(prediction => (
          <Card key={prediction.id} className="bg-card border border-purple-500/20">
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-2">
                  <Badge className={DOMAIN_COLORS[prediction.domain]}>
                    {prediction.domain.replace('_', ' ')}
                  </Badge>
                  <Badge variant="outline" className="text-xs">
                    {TIME_HORIZON_LABELS[prediction.timeHorizon]}
                  </Badge>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm text-muted-foreground">
                    {getTimeRemaining(prediction.timestamp)}
                  </span>
                </div>
              </div>
              <CardTitle className="text-lg">{prediction.entity}</CardTitle>
            </CardHeader>

            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground leading-relaxed">
                {prediction.prediction}
              </p>

              {/* Key Metrics */}
              <div className="grid grid-cols-3 gap-3 text-sm">
                <div className="text-center">
                  <p className="text-muted-foreground">Confidence</p>
                  <p className={`font-bold ${getConfidenceColor(prediction.confidence)}`}>
                    {(prediction.confidence * 100).toFixed(0)}%
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-muted-foreground">Expected ROI</p>
                  <p className={`font-bold ${getROIColor(prediction.expectedROI)}`}>
                    +{(prediction.expectedROI * 100).toFixed(1)}%
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-muted-foreground">Risk Level</p>
                  <p className={`font-bold ${getRiskColor(prediction.riskLevel)}`}>
                    {(prediction.riskLevel * 100).toFixed(0)}%
                  </p>
                </div>
              </div>

              {/* Progress Bars */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground">Confidence Level</span>
                  <span className="text-muted-foreground">{(prediction.confidence * 100).toFixed(0)}%</span>
                </div>
                <Progress value={prediction.confidence * 100} className="h-1" />
              </div>

              {/* Price Targets (if available) */}
              {prediction.currentPrice && prediction.targetPrice && (
                <div className="bg-card rounded-lg p-3">
                  <div className="flex items-center justify-between text-sm">
                    <div>
                      <p className="text-muted-foreground">Current</p>
                      <p className="font-bold">{prediction.currentPrice}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-muted-foreground">Target</p>
                      <p className="font-bold text-green-500">{prediction.targetPrice}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-muted-foreground">Move</p>
                      <p className="font-bold text-blue-500">
                        {((prediction.targetPrice - prediction.currentPrice) / prediction.currentPrice * 100).toFixed(1)}%
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Probability Bands */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground">Probability Bands</span>
                  <span className="text-muted-foreground">Historical: {(prediction.historicalAccuracy * 100).toFixed(0)}%</span>
                </div>
                <div className="grid grid-cols-3 gap-2 text-xs">
                  <div className="text-center">
                    <p className="text-green-500">Optimistic</p>
                    <p className="font-bold">{(prediction.probabilityBands.optimistic * 100).toFixed(0)}%</p>
                  </div>
                  <div className="text-center">
                    <p className="text-blue-500">Realistic</p>
                    <p className="font-bold">{(prediction.probabilityBands.realistic * 100).toFixed(0)}%</p>
                  </div>
                  <div className="text-center">
                    <p className="text-orange-400">Pessimistic</p>
                    <p className="font-bold">{(prediction.probabilityBands.pessimistic * 100).toFixed(0)}%</p>
                  </div>
                </div>
              </div>

              {/* Triggers */}
              <div>
                <p className="text-xs text-muted-foreground mb-2">Key Triggers:</p>
                <div className="flex flex-wrap gap-1">
                  {prediction.triggers.map((trigger, index) => (
                    <Badge key={index} variant="outline" className="text-xs">
                      {trigger}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-2 pt-2">
                <Button size="sm" className="flex-1">
                  <Zap className="h-4 w-4 mr-2" />
                  Monitor
                </Button>
                <Button size="sm" variant="outline" className="flex-1">
                  <Target className="h-4 w-4 mr-2" />
                  Details
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredPredictions.length === 0 && (
        <Card className="bg-card">
          <CardContent className="text-center py-12">
            <Brain className="h-12 w-12 mx-auto mb-4 text-purple-500 opacity-50" />
            <h3 className="text-lg font-semibold mb-2">No Predictions for Selected Time Horizon</h3>
            <p className="text-muted-foreground">
              AI agents are continuously analyzing patterns. New predictions will appear here.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}