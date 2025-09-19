import React, { useState, useEffect } from 'react';
import { Card } from '../common/Card';
import { Badge } from '../common/Badge';
import {
  Brain, TrendingUp, TrendingDown, AlertTriangle, Target,
  DollarSign, Users, Zap, Shield, Activity, ChevronRight
} from 'lucide-react';
import { getBookmakerAnalysis, getGameDetails } from '../../features/sports/api/sports';
import { toast } from 'sonner';

interface BookmakerAnalysisData {
  analysis: {
    line_prediction: any;
    sharp_money: any;
    true_odds: any;
    value_bets: any[];
    public_bias: any;
    closing_line_prediction: any;
    confidence_rating: number;
    key_factors: string[];
  };
  recommendations: any[];
  alerts: any[];
}

interface BookmakerAgentCardProps {
  gameId: string;
  onAnalysisUpdate?: (analysis: BookmakerAnalysisData) => void;
}

export function BookmakerAgentCard({ gameId, onAnalysisUpdate }: BookmakerAgentCardProps) {
  const [analysis, setAnalysis] = useState<BookmakerAnalysisData | null>(null);
  const [gameDetails, setGameDetails] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [expandedSection, setExpandedSection] = useState<string | null>('recommendations');

  useEffect(() => {
    const fetchAnalysis = async () => {
      try {
        console.log('🤖 [BookmakerAgent] Fetching analysis for game:', gameId);

        // Fetch both game details and bookmaker analysis
        const [detailsResult, analysisResult] = await Promise.all([
          getGameDetails(gameId),
          getBookmakerAnalysis(gameId)
        ]);

        console.log('✅ [BookmakerAgent] Got results:', { details: detailsResult, analysis: analysisResult });

        setGameDetails(detailsResult);
        setAnalysis(analysisResult);

        if (onAnalysisUpdate && analysisResult) {
          onAnalysisUpdate(analysisResult);
        }
      } catch (error) {
        console.error('❌ [BookmakerAgent] Failed to fetch analysis:', error);
        // Don't show error toast if it's just a 404 (game might not have analysis yet)
        if (!error?.message?.includes('404')) {
          toast.error('Failed to load AI analysis');
        }
      } finally {
        setLoading(false);
      }
    };

    if (gameId) {
      fetchAnalysis();
    }
  }, [gameId, onAnalysisUpdate]);

  if (loading) {
    return (
      <Card className="bg-card">
        <div className="bg-card"></div>
        <div className="p-6">
          <div className="flex items-center gap-3 mb-4">
            <Brain className="w-6 h-6 text-cyan-400 animate-pulse" />
            <h3 className="text-xl font-bold bg-card">VEGAS AI BOOKMAKER</h3>
          </div>
          <div className="text-center py-8 bg-card">
            <div className="bg-card w-12 h-12 mx-auto mb-4"></div>
            Analyzing odds patterns...
          </div>
        </div>
      </Card>
    );
  }

  if (!analysis) {
    return (
      <Card className="bg-card">
        <div className="bg-card"></div>
        <div className="p-6">
          <div className="flex items-center gap-3 mb-4">
            <Brain className="w-6 h-6 text-cyan-400" />
            <h3 className="text-xl font-bold bg-card">VEGAS AI BOOKMAKER</h3>
          </div>
          <div className="text-center py-8 bg-card">
            <AlertTriangle className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>AI analysis not available for this game yet</p>
          </div>
        </div>
      </Card>
    );
  }

  const { line_prediction, sharp_money, true_odds, value_bets, public_bias, closing_line_prediction, key_factors } = analysis.analysis;

  const renderSection = (id: string, title: string, icon: React.ReactNode, content: React.ReactNode) => {
    const isExpanded = expandedSection === id;

    return (
      <div className="border border-bg-card/30 rounded-lg overflow-hidden">
        <button
          onClick={() => setExpandedSection(isExpanded ? null : id)}
          className="w-full p-4 flex items-center justify-between hover:bg-bg-card/20 transition-all"
        >
          <div className="flex items-center gap-3">
            {icon}
            <span className="font-bold bg-card">{title}</span>
          </div>
          <ChevronRight className={`w-4 h-4 bg-card transition-transform ${isExpanded ? 'rotate-90' : ''}`} />
        </button>
        {isExpanded && (
          <div className="p-4 border-t border-bg-card/30 bg-bg-card/30">
            {content}
          </div>
        )}
      </div>
    );
  };

  return (
    <Card className="bg-card">
      <div className="bg-card"></div>
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6 pb-4 border-b border-bg-card">
          <div className="flex items-center gap-3">
            <Brain className="w-6 h-6 text-cyan-400" />
            <h3 className="text-xl font-bold bg-card">VEGAS AI BOOKMAKER</h3>
          </div>
          <div className="flex items-center gap-2">
            <div className="text-sm bg-card">Confidence:</div>
            <div className="flex items-center gap-1">
              {[...Array(5)].map((_, i) => (
                <div
                  key={i}
                  className={`w-2 h-4 rounded ${
                    i < Math.round((analysis.analysis.confidence_rating || 0) * 5)
                      ? 'bg-cyan-400'
                      : 'bg-bg-card'
                  }`}
                />
              ))}
            </div>
            <span className="text-sm font-bold bg-card ml-1">
              {((analysis.analysis.confidence_rating || 0) * 100).toFixed(0)}%
            </span>
          </div>
        </div>

        {/* Alerts */}
        {analysis.alerts && analysis.alerts.length > 0 && (
          <div className="mb-6 space-y-2">
            {analysis.alerts.map((alert, idx) => (
              <div
                key={idx}
                className={`p-3 rounded-lg border flex items-start gap-3 ${
                  alert.urgency === 'HIGH'
                    ? 'bg-red-500/10 border-red-500/30'
                    : 'bg-yellow-500/10 border-yellow-500/30'
                }`}
              >
                <AlertTriangle className={`w-4 h-4 mt-0.5 ${
                  alert.urgency === 'HIGH' ? 'text-red-500' : 'text-yellow-500'
                }`} />
                <div className="flex-1">
                  <div className="font-bold bg-card text-sm">{alert.type}</div>
                  <div className="text-xs bg-card mt-1">{alert.message}</div>
                  <div className="mt-2">
                    <Badge className="text-xs">{alert.action}</Badge>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Key Factors */}
        {key_factors && key_factors.length > 0 && (
          <div className="mb-6 p-4 bg-bg-card/30 rounded-lg border border-bg-card/30">
            <div className="flex items-center gap-2 mb-3">
              <Zap className="w-4 h-4 text-yellow-500" />
              <span className="font-bold bg-card text-sm">KEY FACTORS</span>
            </div>
            <div className="space-y-2">
              {key_factors.map((factor, idx) => (
                <div key={idx} className="flex items-start gap-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-cyan-400 mt-1.5"></div>
                  <span className="text-xs bg-card">{factor}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Main Sections */}
        <div className="space-y-3">
          {/* Top Recommendations */}
          {renderSection(
            'recommendations',
            'AI RECOMMENDATIONS',
            <Target className="w-4 h-4 text-green-500" />,
            <div className="space-y-3">
              {analysis.recommendations && analysis.recommendations.length > 0 ? (
                analysis.recommendations.map((rec, idx) => (
                  <div key={idx} className="p-3 bg-bg-card/50 rounded border border-bg-card/20">
                    <div className="flex items-center justify-between mb-2">
                      <Badge className={rec.priority === 'HIGH' ? 'bg-red-500/20 text-red-500' : 'bg-blue-500/20 text-blue-500'}>
                        {rec.priority} PRIORITY
                      </Badge>
                      <span className="text-sm font-bold bg-card">{rec.units} Units</span>
                    </div>
                    <div className="font-bold bg-card mb-1">
                      {rec.type} - {rec.pick}
                    </div>
                    <div className="text-xs bg-card">{rec.reasoning}</div>
                    <div className="mt-2 flex items-center gap-2">
                      <div className="text-xs bg-card">Confidence:</div>
                      <div className="flex-1 h-2 bg-bg-card rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-cyan-500 to-green-500"
                          style={{ width: `${(rec.confidence || 0) * 100}%` }}
                        />
                      </div>
                      <span className="text-xs font-bold bg-card">
                        {((rec.confidence || 0) * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-4 bg-card text-sm">
                  No specific recommendations at this time
                </div>
              )}
            </div>
          )}

          {/* Sharp vs Public Money */}
          {renderSection(
            'sharp_public',
            'SHARP VS PUBLIC',
            <Users className="w-4 h-4 text-purple-400" />,
            <div className="grid grid-cols-2 gap-4">
              <div className="p-3 bg-bg-card/50 rounded border border-bg-card/20">
                <div className="text-xs bg-card mb-2">SHARP MONEY</div>
                <div className="font-bold text-lg bg-card">
                  {sharp_money?.sharp_side || 'UNKNOWN'}
                </div>
                <div className="text-sm bg-card mt-1">
                  {(sharp_money?.sharp_probability * 100).toFixed(0)}% Confidence
                </div>
              </div>
              <div className="p-3 bg-bg-card/50 rounded border border-bg-card/20">
                <div className="text-xs bg-card mb-2">PUBLIC MONEY</div>
                <div className="font-bold text-lg bg-card">
                  {public_bias?.public_side || 'UNKNOWN'}
                </div>
                <div className="text-sm bg-card mt-1">
                  {public_bias?.public_percentage?.toFixed(0)}% of Bets
                </div>
              </div>
              {public_bias?.fade_opportunity && (
                <div className="col-span-2 p-3 bg-yellow-500/10 border border-yellow-500/30 rounded">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-yellow-500" />
                    <span className="text-sm font-bold text-yellow-500">FADE OPPORTUNITY DETECTED</span>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Line Movement Prediction */}
          {renderSection(
            'line_movement',
            'LINE MOVEMENT',
            <Activity className="w-4 h-4 text-blue-500" />,
            <div className="space-y-3">
              {line_prediction && (
                <>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="text-center p-3 bg-bg-card/50 rounded border border-bg-card/20">
                      <div className="text-xs bg-card mb-1">Current Line</div>
                      <div className="text-xl font-bold bg-card">
                        {line_prediction.current_line?.toFixed(1) || 'N/A'}
                      </div>
                    </div>
                    <div className="text-center p-3 bg-bg-card/50 rounded border border-bg-card/20">
                      <div className="text-xs bg-card mb-1">Predicted Close</div>
                      <div className="text-xl font-bold text-cyan-400">
                        {line_prediction.predicted_close?.toFixed(1) || 'N/A'}
                      </div>
                    </div>
                  </div>
                  <div className="p-3 bg-bg-card/50 rounded border border-bg-card/20">
                    <div className="flex items-center justify-between">
                      <span className="text-sm bg-card">Movement Direction:</span>
                      <div className="flex items-center gap-2">
                        {line_prediction.predicted_movement > 0 ? (
                          <TrendingUp className="w-4 h-4 text-green-500" />
                        ) : (
                          <TrendingDown className="w-4 h-4 text-red-500" />
                        )}
                        <span className="font-bold bg-card">
                          {line_prediction.direction}
                        </span>
                      </div>
                    </div>
                    <div className="text-xs bg-card mt-2">
                      {line_prediction.recommendation}
                    </div>
                  </div>
                </>
              )}
            </div>
          )}

          {/* Value Bets */}
          {renderSection(
            'value_bets',
            'VALUE BETS',
            <DollarSign className="w-4 h-4 text-green-500" />,
            <div className="space-y-2">
              {value_bets && value_bets.length > 0 ? (
                value_bets.slice(0, 3).map((bet, idx) => (
                  <div key={idx} className="p-3 bg-bg-card/50 rounded border border-bg-card/20">
                    <div className="flex items-center justify-between mb-2">
                      <Badge className="bg-green-500/20 text-green-500">{bet.type}</Badge>
                      <span className="text-sm font-bold text-green-500">
                        +{bet.expected_value || bet.edge}% Edge
                      </span>
                    </div>
                    <div className="font-bold bg-card text-sm mb-1">
                      {bet.team || bet.direction} @ {bet.book}
                    </div>
                    {bet.odds && (
                      <div className="text-xs bg-card">
                        Odds: {bet.odds > 0 ? '+' : ''}{bet.odds}
                      </div>
                    )}
                    {bet.confidence && (
                      <div className="mt-2">
                        <Badge className={`text-xs ${
                          bet.confidence === 'HIGH'
                            ? 'bg-green-500/20 text-green-500'
                            : 'bg-yellow-500/20 text-yellow-500'
                        }`}>
                          {bet.confidence} CONFIDENCE
                        </Badge>
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div className="text-center py-4 bg-card text-sm">
                  No value bets identified
                </div>
              )}
            </div>
          )}

          {/* True Odds */}
          {renderSection(
            'true_odds',
            'TRUE ODDS MODEL',
            <Shield className="w-4 h-4 text-cyan-400" />,
            <div className="space-y-3">
              {true_odds && (
                <>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-3 bg-bg-card/50 rounded border border-bg-card/20">
                      <div className="text-xs bg-card mb-2">Home Win Probability</div>
                      <div className="text-xl font-bold bg-card">
                        {(true_odds.true_odds?.home_win_probability * 100).toFixed(1)}%
                      </div>
                    </div>
                    <div className="p-3 bg-bg-card/50 rounded border border-bg-card/20">
                      <div className="text-xs bg-card mb-2">Away Win Probability</div>
                      <div className="text-xl font-bold bg-card">
                        {(true_odds.true_odds?.away_win_probability * 100).toFixed(1)}%
                      </div>
                    </div>
                  </div>
                  <div className="p-3 bg-bg-card/50 rounded border border-bg-card/20">
                    <div className="text-xs bg-card mb-2">Model Confidence</div>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-2 bg-bg-card rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-blue-500 to-cyan-500"
                          style={{ width: `${(true_odds.model_confidence || 0) * 100}%` }}
                        />
                      </div>
                      <span className="text-sm font-bold bg-card">
                        {((true_odds.model_confidence || 0) * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                </>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="mt-6 pt-4 border-t border-bg-card/30 flex items-center justify-between text-xs bg-card">
          <span>Powered by Vegas AI™</span>
          <span className="flex items-center gap-1">
            <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></div>
            LIVE ANALYSIS
          </span>
        </div>
      </div>
    </Card>
  );
}