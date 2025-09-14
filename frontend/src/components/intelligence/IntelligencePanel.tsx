import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Brain, Target, Shield, TrendingUp, Users, Activity,
  AlertTriangle, CheckCircle, Clock, Zap, Database,
  Search, BookOpen, RefreshCw, ChevronRight
} from 'lucide-react';
import {
  getUniversalIntelligence,
  type DecisionContext,
  type IntelligenceResult
} from '@/features/sports/api/sports';

interface IntelligencePanelProps {
  gameId: string;
  gameData: any;
  onDecision?: (decision: IntelligenceResult) => void;
}

export function IntelligencePanel({ gameId, gameData, onDecision }: IntelligencePanelProps) {
  const [loading, setLoading] = useState(false);
  const [intelligence, setIntelligence] = useState<IntelligenceResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const analyzeGame = async () => {
    setLoading(true);
    setError(null);

    try {
      const context: DecisionContext = {
        domain: 'SPORTS_BETTING',
        entity_id: gameId,
        data_points: {
          home_team: gameData.game.home_team_name,
          away_team: gameData.game.away_team_name,
          spread: gameData.odds?.spread || 0,
          total: gameData.odds?.total || 0,
          moneyline_home: gameData.odds?.moneyline_home || 0,
          moneyline_away: gameData.odds?.moneyline_away || 0,
          weather: gameData.weather,
          injuries: gameData.injuries,
          venue: gameData.game.venue_name
        },
        risk_level: 0.6,
        time_horizon: 'single_game'
      };

      const result = await getUniversalIntelligence(context);
      setIntelligence(result);

      if (onDecision) {
        onDecision(result);
      }
    } catch (err) {
      console.error('Intelligence analysis failed:', err);
      setError('Failed to analyze game. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (gameId && gameData) {
      analyzeGame();
    }
  }, [gameId]);

  const getActionColor = (action: string) => {
    switch (action) {
      case 'STRONG_EXECUTE': return 'bg-green-500';
      case 'EXECUTE': return 'bg-green-400';
      case 'WAIT': return 'bg-yellow-500';
      case 'AVOID': return 'bg-red-400';
      case 'STRONG_AVOID': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getSquadronName = (key: string) => {
    const names: Record<string, string> = {
      alpha_squadron: 'Alpha (Market Analysis)',
      bravo_squadron: 'Bravo (Sentiment)',
      charlie_squadron: 'Charlie (Patterns)',
      delta_squadron: 'Delta (Risk)',
      echo_squadron: 'Echo (Execution)'
    };
    return names[key] || key;
  };

  if (loading && !intelligence) {
    return (
      <Card className="gaming-card">
        <CardContent className="p-6">
          <div className="flex flex-col items-center justify-center space-y-4">
            <Brain className="h-12 w-12 text-blue-500 animate-pulse" />
            <p className="text-lg">Analyzing with 102 specialized agents...</p>
            <Progress value={33} className="w-full max-w-xs" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  if (!intelligence) {
    return (
      <Card className="gaming-card">
        <CardContent className="p-6">
          <Button onClick={analyzeGame} className="w-full">
            <Brain className="mr-2 h-4 w-4" />
            Activate Universal Intelligence
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="gaming-card">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-blue-500" />
            Universal Intelligence Analysis
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={analyzeGame}
            disabled={loading}
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          </Button>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Primary Decision */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Primary Action</span>
            <Badge className={`${getActionColor(intelligence.primary_action)} text-white`}>
              {intelligence.primary_action.replace('_', ' ')}
            </Badge>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <div className="flex justify-between text-sm mb-1">
                <span>Confidence</span>
                <span>{(intelligence.confidence * 100).toFixed(1)}%</span>
              </div>
              <Progress value={intelligence.confidence * 100} />
            </div>
          </div>
        </div>

        {/* Position Sizing */}
        <div className="rounded-lg bg-muted p-4 space-y-2">
          <div className="flex items-center gap-2 mb-2">
            <Target className="h-4 w-4 text-green-500" />
            <span className="font-medium">Position Sizing</span>
          </div>
          <div className="grid grid-cols-3 gap-2 text-sm">
            <div>
              <span className="text-muted-foreground">Kelly %</span>
              <p className="font-bold">{(intelligence.position_sizing.kelly_percentage * 100).toFixed(2)}%</p>
            </div>
            <div>
              <span className="text-muted-foreground">Recommended</span>
              <p className="font-bold">${intelligence.position_sizing.recommended_stake}</p>
            </div>
            <div>
              <span className="text-muted-foreground">Max Exposure</span>
              <p className="font-bold">${intelligence.position_sizing.max_exposure}</p>
            </div>
          </div>
        </div>

        {/* Squadron Consensus */}
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <Users className="h-4 w-4 text-blue-500" />
            <span className="font-medium">Squadron Consensus</span>
          </div>
          {Object.entries(intelligence.agent_consensus).map(([squadron, consensus]) => (
            <div key={squadron} className="space-y-1">
              <div className="flex justify-between text-sm">
                <span>{getSquadronName(squadron)}</span>
                <span>{(consensus * 100).toFixed(0)}%</span>
              </div>
              <Progress value={consensus * 100} className="h-2" />
            </div>
          ))}
        </div>

        {/* Risk Assessment */}
        <div className="rounded-lg bg-muted p-4 space-y-2">
          <div className="flex items-center gap-2 mb-2">
            <Shield className="h-4 w-4 text-yellow-500" />
            <span className="font-medium">Risk Assessment</span>
          </div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm">Overall Risk</span>
            <div className="flex items-center gap-2">
              <Progress value={intelligence.risk_assessment.overall_risk * 100} className="w-20 h-2" />
              <span className="text-sm font-bold">
                {(intelligence.risk_assessment.overall_risk * 100).toFixed(0)}%
              </span>
            </div>
          </div>
          {intelligence.risk_assessment.risk_factors.length > 0 && (
            <div className="space-y-1">
              <span className="text-xs text-muted-foreground">Risk Factors:</span>
              {intelligence.risk_assessment.risk_factors.slice(0, 3).map((factor, idx) => (
                <div key={idx} className="flex items-start gap-1">
                  <AlertTriangle className="h-3 w-3 text-yellow-500 mt-0.5" />
                  <span className="text-xs">{factor}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Cross-Domain Patterns */}
        {intelligence.cross_domain_patterns.length > 0 && (
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <Activity className="h-4 w-4 text-purple-500" />
              <span className="font-medium">Cross-Domain Patterns Detected</span>
            </div>
            {intelligence.cross_domain_patterns.slice(0, 2).map((pattern, idx) => (
              <div key={idx} className="rounded-lg border p-3 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-medium text-sm">{pattern.pattern_name}</span>
                  <Badge variant="outline">
                    {(pattern.historical_success_rate * 100).toFixed(0)}% Success
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground">{pattern.description}</p>
                <div className="flex items-center gap-2">
                  <Progress value={pattern.confidence * 100} className="flex-1 h-1" />
                  <span className="text-xs">{(pattern.confidence * 100).toFixed(0)}% confidence</span>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Similar Scenarios */}
        {intelligence.similar_scenarios.length > 0 && (
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <Database className="h-4 w-4 text-indigo-500" />
              <span className="font-medium">Similar Historical Scenarios</span>
            </div>
            <div className="space-y-2">
              {intelligence.similar_scenarios.slice(0, 3).map((scenario, idx) => (
                <div key={idx} className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-xs">
                      {scenario.domain}
                    </Badge>
                    <span className="text-xs text-muted-foreground">
                      {new Date(scenario.timestamp).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`text-xs font-medium ${
                      scenario.outcome === 'SUCCESS' ? 'text-green-500' : 'text-red-500'
                    }`}>
                      {scenario.outcome}
                    </span>
                    <Badge variant="secondary" className="text-xs">
                      {(scenario.similarity * 100).toFixed(0)}% match
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Execution Plan */}
        {intelligence.execution_plan && intelligence.execution_plan.length > 0 && (
          <div className="rounded-lg bg-muted p-4 space-y-2">
            <div className="flex items-center gap-2 mb-2">
              <Zap className="h-4 w-4 text-yellow-500" />
              <span className="font-medium">Recommended Execution Plan</span>
            </div>
            <div className="space-y-2">
              {intelligence.execution_plan.map((step, idx) => (
                <div key={idx} className="flex items-start gap-2">
                  <ChevronRight className="h-3 w-3 text-muted-foreground mt-0.5" />
                  <span className="text-sm">{step}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}