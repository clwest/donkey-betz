import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Brain, Target, Zap, TrendingUp, Activity, AlertTriangle,
  CheckCircle, DollarSign, Clock, Signal, Sparkles,
  Eye, ArrowRight, BarChart3, Shield
} from 'lucide-react';
import { useWebSocket } from '@/hooks/useWebSocket';

interface SkynetStatus {
  skynet_status: string;
  intelligence_engine: string;
  live_opportunities: number;
  live_predictions: number;
  scan_interval: number;
  last_update: string;
  features: Record<string, boolean>;
}

interface IntelligenceOpportunity {
  id: string;
  type: string;
  domain: string;
  entity: string;
  description: string;
  edge: number;
  confidence: number;
  profit_potential: number;
  time_window: number;
  timestamp: string;
  status: string;
}

interface IntelligencePrediction {
  id: string;
  domain: string;
  prediction_type: string;
  entity: string;
  prediction: string;
  confidence: number;
  expected_outcome: string;
  time_horizon: string;
  timestamp: string;
}

export function RealTimeIntelligencePanel() {
  const [skynetStatus, setSkynetStatus] = useState<SkynetStatus | null>(null);
  const [opportunities, setOpportunities] = useState<IntelligenceOpportunity[]>([]);
  const [predictions, setPredictions] = useState<IntelligencePrediction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Connect to Command Center WebSocket for real-time intelligence updates
  const { isConnected, sendMessage } = useWebSocket({
    url: '/ws/command-center/',
    onMessage: (data) => {
      console.log('🧠 Intelligence update received:', data);

      if (data.type === 'connection_established') {
        setSkynetStatus({
          skynet_status: data.data.skynet_status || 'ONLINE',
          intelligence_engine: data.data.intelligence_status || 'ACTIVE',
          live_opportunities: data.data.live_opportunities || 0,
          live_predictions: data.data.live_predictions || 0,
          scan_interval: 5000,
          last_update: data.data.timestamp,
          features: data.data.features || {}
        });
        setLoading(false);
      } else if (data.type === 'intelligence_update') {
        const updateData = data.data;

        if (updateData.type === 'new_opportunity' || updateData.opportunity) {
          const opportunity = updateData.opportunity || updateData;
          setOpportunities(prev => [opportunity, ...prev.slice(0, 4)]); // Keep latest 5
        }

        if (updateData.type === 'new_prediction' || updateData.prediction) {
          const prediction = updateData.prediction || updateData;
          setPredictions(prev => [prediction, ...prev.slice(0, 4)]); // Keep latest 5
        }
      }
    },
    onOpen: () => {
      console.log('🧠 Connected to Intelligence Engine');
      // Request initial data
      sendMessage({ type: 'request_intelligence', domain: 'ALL' });
    },
    onError: (error) => {
      console.error('🧠 Intelligence connection error:', error);
      setError('Failed to connect to Intelligence Engine');
    }
  });

  // Fetch initial Skynet status
  useEffect(() => {
    const fetchSkynetStatus = async () => {
      try {
        const response = await fetch('/api/v1/intelligence/skynet/status/');
        if (response.ok) {
          const status = await response.json();
          setSkynetStatus(status);
        } else {
          throw new Error('Failed to fetch Skynet status');
        }
      } catch (err) {
        console.error('Error fetching Skynet status:', err);
        setError('Failed to connect to Skynet');
      } finally {
        setLoading(false);
      }
    };

    if (!isConnected) {
      fetchSkynetStatus();
    }
  }, [isConnected]);

  const getStatusColor = (status: string) => {
    switch (status.toUpperCase()) {
      case 'ONLINE':
      case 'OPERATIONAL':
      case 'ACTIVE':
        return 'text-green-500';
      case 'INITIALIZING':
      case 'BOOTING':
        return 'text-yellow-500';
      case 'OFFLINE':
      case 'ERROR':
        return 'text-red-500';
      default:
        return 'text-muted-foreground';
    }
  };

  const getOpportunityIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'arbitrage':
        return <Target className="h-4 w-4" />;
      case 'value':
        return <TrendingUp className="h-4 w-4" />;
      case 'prediction':
        return <Brain className="h-4 w-4" />;
      default:
        return <Sparkles className="h-4 w-4" />;
    }
  };

  if (loading) {
    return (
      <Card className="bg-card">
        <CardContent className="p-6">
          <div className="flex flex-col items-center justify-center space-y-4">
            <Brain className="h-12 w-12 text-blue-500 animate-pulse" />
            <p className="text-lg">Initializing Skynet Intelligence Engine...</p>
            <Progress value={33} className="w-full max-w-xs" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error && !skynetStatus) {
    return (
      <Alert variant="destructive">
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      {/* Skynet Status Header */}
      <Card className="bg-card border-blue-500/30 bg-gradient-to-r from-blue-900/10 to-purple-900/10">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Brain className="h-6 w-6 text-blue-500" />
              <span className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent">
                SKYNET INTELLIGENCE ENGINE
              </span>
            </div>
            <div className="flex items-center gap-2">
              <Signal className={`h-5 w-5 ${isConnected ? 'text-green-500' : 'text-red-500'}`} />
              <Badge
                className={`${getStatusColor(skynetStatus?.skynet_status || 'OFFLINE')} bg-black/50 border-current`}
              >
                {skynetStatus?.skynet_status || 'OFFLINE'}
              </Badge>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="flex items-center justify-center mb-2">
                <Target className="h-5 w-5 text-green-500" />
              </div>
              <p className="text-2xl font-bold text-green-500">
                {skynetStatus?.live_opportunities || 0}
              </p>
              <p className="text-sm text-muted-foreground">Live Opportunities</p>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center mb-2">
                <Sparkles className="h-5 w-5 text-purple-500" />
              </div>
              <p className="text-2xl font-bold text-purple-500">
                {skynetStatus?.live_predictions || 0}
              </p>
              <p className="text-sm text-muted-foreground">Active Predictions</p>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center mb-2">
                <Activity className="h-5 w-5 text-blue-500" />
              </div>
              <p className="text-2xl font-bold text-blue-500">
                {skynetStatus?.intelligence_engine === 'ACTIVE' ? '102' : '0'}
              </p>
              <p className="text-sm text-muted-foreground">Active Agents</p>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center mb-2">
                <Clock className="h-5 w-5 text-yellow-500" />
              </div>
              <p className="text-2xl font-bold text-yellow-500">
                {skynetStatus?.scan_interval ? `${skynetStatus.scan_interval/1000}s` : '5s'}
              </p>
              <p className="text-sm text-muted-foreground">Scan Interval</p>
            </div>
          </div>

          {skynetStatus?.last_update && (
            <div className="text-center text-xs text-muted-foreground">
              Last Update: {new Date(skynetStatus.last_update).toLocaleString()}
            </div>
          )}
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Live Opportunities */}
        <Card className="bg-card border-green-500/30">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5 text-green-500" />
              Live Market Opportunities
              {opportunities.length > 0 && (
                <Badge className="bg-green-500 text-foreground ml-auto">
                  {opportunities.length}
                </Badge>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {opportunities.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <Target className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p>No live opportunities detected</p>
                <p className="text-xs">Intelligence engine scanning...</p>
              </div>
            ) : (
              opportunities.map((opp, index) => (
                <div key={`${opp.id}-${index}`} className="rounded-lg border border-gray-700/50 p-3 bg-gradient-to-r from-green-900/10 to-transparent">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      {getOpportunityIcon(opp.type)}
                      <span className="font-medium text-sm">{opp.entity || opp.description}</span>
                    </div>
                    <Badge variant="outline" className="text-xs">
                      {opp.domain}
                    </Badge>
                  </div>

                  <div className="grid grid-cols-3 gap-2 text-xs">
                    <div>
                      <span className="text-muted-foreground">Edge:</span>
                      <p className="font-bold text-green-500">{opp.edge}%</p>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Confidence:</span>
                      <p className="font-bold">{(opp.confidence * 100).toFixed(0)}%</p>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Profit:</span>
                      <p className="font-bold text-green-500">${opp.profit_potential}</p>
                    </div>
                  </div>

                  {opp.time_window && (
                    <div className="flex items-center justify-between mt-2 pt-2 border-t border-gray-700/50">
                      <div className="flex items-center gap-1 text-xs text-muted-foreground">
                        <Clock className="h-3 w-3" />
                        {opp.time_window}s window
                      </div>
                      <Button size="sm" variant="outline" className="h-6 text-xs">
                        <Eye className="h-3 w-3 mr-1" />
                        View
                      </Button>
                    </div>
                  )}
                </div>
              ))
            )}
          </CardContent>
        </Card>

        {/* Live Predictions */}
        <Card className="bg-card border-purple-500/30">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-purple-500" />
              AI Predictions
              {predictions.length > 0 && (
                <Badge className="bg-purple-500 text-foreground ml-auto">
                  {predictions.length}
                </Badge>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {predictions.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <Sparkles className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p>No active predictions</p>
                <p className="text-xs">AI models analyzing...</p>
              </div>
            ) : (
              predictions.map((pred, index) => (
                <div key={`${pred.id}-${index}`} className="rounded-lg border border-gray-700/50 p-3 bg-gradient-to-r from-purple-900/10 to-transparent">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Brain className="h-4 w-4 text-purple-500" />
                      <span className="font-medium text-sm">{pred.entity}</span>
                    </div>
                    <Badge variant="outline" className="text-xs">
                      {pred.domain}
                    </Badge>
                  </div>

                  <p className="text-sm text-muted-foreground mb-2">{pred.prediction}</p>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="text-xs">
                        <span className="text-muted-foreground">Confidence:</span>
                        <span className="ml-1 font-bold text-purple-500">
                          {(pred.confidence * 100).toFixed(0)}%
                        </span>
                      </div>
                      <div className="text-xs">
                        <span className="text-muted-foreground">Horizon:</span>
                        <span className="ml-1 font-bold">
                          {pred.time_horizon}
                        </span>
                      </div>
                    </div>
                    <Button size="sm" variant="outline" className="h-6 text-xs">
                      <ArrowRight className="h-3 w-3 mr-1" />
                      Analyze
                    </Button>
                  </div>
                </div>
              ))
            )}
          </CardContent>
        </Card>
      </div>

      {/* Intelligence Features Status */}
      {skynetStatus?.features && (
        <Card className="bg-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-blue-500" />
              Intelligence Systems Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {Object.entries(skynetStatus.features).map(([feature, active]) => (
                <div key={feature} className="flex items-center justify-between p-2 rounded border border-gray-700/50">
                  <span className="text-sm capitalize">
                    {feature.replace(/_/g, ' ')}
                  </span>
                  <div className="flex items-center gap-1">
                    {active ? (
                      <CheckCircle className="h-4 w-4 text-green-500" />
                    ) : (
                      <AlertTriangle className="h-4 w-4 text-red-500" />
                    )}
                    <span className={`text-xs ${active ? 'text-green-500' : 'text-red-500'}`}>
                      {active ? 'Online' : 'Offline'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}