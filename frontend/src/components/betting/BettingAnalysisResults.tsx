import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { Card } from '../common/Card';
import { Badge } from '../common/Badge';
import { Button } from '../common/Button';
import {
  ChartBarIcon,
  ArrowTrendingUpIcon as TrendingUpIcon,
  CalculatorIcon,
  DocumentTextIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  SparklesIcon,
  BoltIcon,
  ExclamationTriangleIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  CurrencyDollarIcon
} from '@heroicons/react/24/outline';
import { useAgentOrchestraStore } from '../../store/agentOrchestraStore';
import type { Game } from '../../features/sports/api/sports';

interface BettingAnalysisResultsProps {
  game: Game;
  className?: string;
}

interface AnalysisResult {
  id: string;
  type: 'team_analysis' | 'kelly_calculation' | 'risk_assessment' | 'market_analysis';
  agentName: string;
  timestamp: Date;
  status: 'pending' | 'running' | 'completed' | 'failed';
  content?: {
    summary?: string;
    winProbability?: number;
    recommendedBet?: {
      type: string;
      team: string;
      amount: number;
      percentage: number;
      expectedValue: number;
    };
    keyFactors?: string[];
    risks?: string[];
    opportunities?: string[];
    detailedAnalysis?: string;
    statistics?: Record<string, any>;
  };
  error?: string;
}

export function BettingAnalysisResults({ game, className }: BettingAnalysisResultsProps) {
  const [expandedResults, setExpandedResults] = useState<Set<string>>(new Set());
  const [analysisResults, setAnalysisResults] = useState<AnalysisResult[]>([]);
  
  const { instances, selectedInstance } = useAgentOrchestraStore();
  
  // Filter instances for this specific game - memoized to prevent infinite loops
  const gameInstances = useMemo(() => 
    instances.filter(instance => 
      instance.parameters?.game_id === game.id
    ), [instances, game.id]);

  const parseAnalysisContent = useCallback((result: string, agentType: string): any => {
    // Enhanced parsing logic for different agent types
    const content: any = {};
    
    // Extract win probability
    const probMatch = result.match(/(\d+(?:\.\d+)?)[%\s]*(?:win|probability|chance)/i);
    if (probMatch) {
      content.winProbability = parseFloat(probMatch[1]);
    }
    
    // Extract Kelly recommendation
    const kellyMatch = result.match(/kelly[^:]*:\s*(\d+(?:\.\d+)?)[%\s]*(?:of bankroll)?/i);
    if (kellyMatch) {
      content.recommendedBet = {
        type: 'Kelly Criterion',
        team: game.home_team_name,
        percentage: parseFloat(kellyMatch[1]),
        amount: parseFloat(kellyMatch[1]) * 10, // Assuming $1000 bankroll
        expectedValue: 0
      };
    }
    
    // Extract bet amount recommendation
    const betMatch = result.match(/(?:recommend|suggest|bet)[^$]*\$(\d+(?:\.\d+)?)/i);
    if (betMatch && content.recommendedBet) {
      content.recommendedBet.amount = parseFloat(betMatch[1]);
    }
    
    // Extract key factors (bullet points or numbered lists)
    const factors = result.match(/(?:•|\d+\.|-)[\s]*([^\n]+)/g);
    if (factors) {
      content.keyFactors = factors.map(f => f.replace(/^[•\d+.\-\s]+/, '').trim());
    }
    
    // Set summary
    content.summary = result.substring(0, 200) + (result.length > 200 ? '...' : '');
    content.detailedAnalysis = result;
    
    return content;
  }, [game.home_team_name]);

  useEffect(() => {
    // Convert agent instances to analysis results
    const results: AnalysisResult[] = gameInstances.map(instance => {
      // Parse the result based on the agent type
      let parsedContent: any = {};
      
      if (instance.result) {
        try {
          if (typeof instance.result === 'string') {
            // Try to extract structured data from string result
            parsedContent = parseAnalysisContent(instance.result, instance.template?.name || '');
          } else if (typeof instance.result === 'object') {
            const result = instance.result as any;
            if (result.output) {
              parsedContent = parseAnalysisContent(result.output, instance.template?.name || '');
            } else {
              parsedContent = result;
            }
          }
        } catch (error) {
          console.error('Failed to parse agent result:', error);
        }
      }
      
      return {
        id: instance.id,
        type: determineAnalysisType(instance.template?.name || instance.template_name || ''),
        agentName: instance.template?.name || instance.template_name || 'Unknown Agent',
        timestamp: new Date(instance.created_at),
        status: instance.status,
        content: parsedContent,
        error: instance.error_message
      };
    });
    
    setAnalysisResults(results);
  }, [gameInstances, parseAnalysisContent]);

  const determineAnalysisType = (agentType: string): AnalysisResult['type'] => {
    const type = agentType.toLowerCase();
    if (type.includes('kelly') || type.includes('calculation')) return 'kelly_calculation';
    if (type.includes('risk')) return 'risk_assessment';
    if (type.includes('market')) return 'market_analysis';
    return 'team_analysis';
  };

  const toggleExpanded = (resultId: string) => {
    const newExpanded = new Set(expandedResults);
    if (newExpanded.has(resultId)) {
      newExpanded.delete(resultId);
    } else {
      newExpanded.add(resultId);
    }
    setExpandedResults(newExpanded);
  };

  const getTypeIcon = (type: AnalysisResult['type']) => {
    switch (type) {
      case 'team_analysis':
        return <ChartBarIcon className="w-5 h-5" />;
      case 'kelly_calculation':
        return <CalculatorIcon className="w-5 h-5" />;
      case 'risk_assessment':
        return <ExclamationTriangleIcon className="w-5 h-5" />;
      case 'market_analysis':
        return <TrendingUpIcon className="w-5 h-5" />;
    }
  };

  const getTypeColor = (type: AnalysisResult['type']) => {
    switch (type) {
      case 'team_analysis':
        return 'text-cyan-400 border-cyan-400/30 bg-cyan-400/5';
      case 'kelly_calculation':
        return 'text-green-500 border-green-400/30 bg-green-400/5';
      case 'risk_assessment':
        return 'text-orange-400 border-orange-400/30 bg-orange-400/5';
      case 'market_analysis':
        return 'text-purple-400 border-purple-400/30 bg-purple-400/5';
    }
  };

  const getStatusIcon = (status: AnalysisResult['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon className="w-4 h-4 text-green-500" />;
      case 'running':
        return <ClockIcon className="w-4 h-4 text-yellow-500 animate-spin" />;
      case 'failed':
        return <XCircleIcon className="w-4 h-4 text-red-500" />;
      default:
        return <ClockIcon className="w-4 h-4 text-muted-foreground" />;
    }
  };

  if (analysisResults.length === 0) {
    return (
      <Card className={`bg-card ${className}`}>
        <div className="bg-card"></div>
        <div className="p-6">
          <h3 className="text-lg font-bold bg-card mb-4 flex items-center gap-2 border-b border-bg-card pb-3">
            <SparklesIcon className="w-5 h-5 text-yellow-500" />
            AI ANALYSIS RESULTS
          </h3>
          <div className="text-center py-8 bg-card">
            <BoltIcon className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p className="text-sm mb-2">No analysis results yet</p>
            <p className="text-xs bg-card">
              Click "Analyze Teams" or "Kelly Analysis" to generate insights
            </p>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <Card className={`bg-card ${className}`}>
      <div className="bg-card"></div>
      <div className="p-6">
        <h3 className="text-lg font-bold bg-card mb-6 flex items-center gap-2 border-b border-bg-card pb-3">
          <SparklesIcon className="w-5 h-5 text-yellow-500" />
          AI ANALYSIS RESULTS
          <Badge className="ml-auto bg-card text-xs">
            {analysisResults.filter(r => r.status === 'completed').length} COMPLETED
          </Badge>
        </h3>

        <div className="space-y-4 max-h-[600px] overflow-y-auto">
          {analysisResults.map(result => (
            <div
              key={result.id}
              className={`bg-card border-2 p-4 transition-all duration-300 ${getTypeColor(result.type)}`}
            >
              {/* Result Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-2">
                    {getTypeIcon(result.type)}
                    <div>
                      <div className="font-bold bg-card text-sm">
                        {result.agentName}
                      </div>
                      <div className="bg-card text-xs">
                        {result.timestamp.toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                  {getStatusIcon(result.status)}
                </div>
                
                <Button
                  onClick={() => toggleExpanded(result.id)}
                  variant="ghost"
                  size="sm"
                  className="bg-card p-1"
                >
                  {expandedResults.has(result.id) ? (
                    <ChevronUpIcon className="w-4 h-4" />
                  ) : (
                    <ChevronDownIcon className="w-4 h-4" />
                  )}
                </Button>
              </div>

              {/* Result Summary */}
              {result.status === 'completed' && result.content && (
                <div className="space-y-3">
                  {/* Key Metrics */}
                  {(result.content.winProbability || result.content.recommendedBet) && (
                    <div className="grid grid-cols-2 gap-3">
                      {result.content.winProbability && (
                        <div className="bg-card p-3 border border-bg-card/30">
                          <div className="text-xs bg-card mb-1">WIN PROBABILITY</div>
                          <div className="text-xl font-bold bg-card flex items-center gap-2">
                            {result.content.winProbability}%
                            {result.content.winProbability > 50 ? (
                              <ArrowTrendingUpIcon className="w-4 h-4 text-green-500" />
                            ) : (
                              <ArrowTrendingDownIcon className="w-4 h-4 text-red-500" />
                            )}
                          </div>
                        </div>
                      )}
                      
                      {result.content.recommendedBet && (
                        <div className="bg-card p-3 border border-bg-card/30">
                          <div className="text-xs bg-card mb-1">RECOMMENDED BET</div>
                          <div className="text-xl font-bold text-cyan-400 flex items-center gap-2">
                            ${result.content.recommendedBet.amount.toFixed(0)}
                            <span className="text-xs bg-card">
                              ({result.content.recommendedBet.percentage.toFixed(1)}%)
                            </span>
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Summary Text */}
                  <div className="bg-card text-sm">
                    {result.content.summary}
                  </div>

                  {/* Expanded Details */}
                  {expandedResults.has(result.id) && (
                    <div className="mt-4 pt-4 border-t border-bg-card/30 space-y-3">
                      {/* Key Factors */}
                      {result.content.keyFactors && result.content.keyFactors.length > 0 && (
                        <div>
                          <div className="text-xs font-bold bg-card mb-2">KEY FACTORS</div>
                          <div className="space-y-1">
                            {result.content.keyFactors.map((factor, idx) => (
                              <div key={idx} className="flex items-start gap-2">
                                <div className="w-1.5 h-1.5 rounded-full bg-cyan-400 mt-1.5 flex-shrink-0"></div>
                                <div className="bg-card text-xs">{factor}</div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Detailed Analysis */}
                      {result.content.detailedAnalysis && (
                        <div>
                          <div className="text-xs font-bold bg-card mb-2">FULL ANALYSIS</div>
                          <div className="bg-card p-3 border border-bg-card/20 max-h-64 overflow-y-auto">
                            <pre className="bg-card text-xs whitespace-pre-wrap font-mono">
                              {result.content.detailedAnalysis}
                            </pre>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* Running Status */}
              {result.status === 'running' && (
                <div className="flex items-center gap-2 bg-card text-sm">
                  <div className="bg-card w-4 h-4"></div>
                  <span>Analyzing {game.away_team_name} vs {game.home_team_name}...</span>
                </div>
              )}

              {/* Error State */}
              {result.status === 'failed' && (
                <div className="text-red-500 text-sm">
                  {result.error || 'Analysis failed'}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Analysis Summary Footer */}
        <div className="mt-4 pt-4 border-t border-bg-card/30 flex items-center justify-between text-xs bg-card">
          <span>🔬 ADVANCED AI ANALYSIS</span>
          <span className="flex items-center gap-1">
            <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></div>
            REAL-TIME UPDATES
          </span>
        </div>
      </div>
    </Card>
  );
}