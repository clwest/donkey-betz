import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import { useAgentOrchestraStore, useAgentOrchestraSelectors } from '../../store/agentOrchestraStore';
import { toast } from 'sonner';

export function PokerVloggerPanel() {
  const [handDescription, setHandDescription] = useState('');
  const [potSize, setPotSize] = useState(100);
  const [betSize, setBetSize] = useState(25);
  const [winProbability, setWinProbability] = useState(0.6);
  const [bankroll, setBankroll] = useState(5000);

  const {
    calculateOdds,
    analyzeBetting,
    executeAgent,
  } = useAgentOrchestraStore();

  const {
    oddsCalculations,
    bettingOpportunities,
    toolsLoading,
    toolsError,
  } = useAgentOrchestraSelectors();

  const handleCalculatePotOdds = async () => {
    try {
      const callAmount = betSize;
      const totalPot = potSize + betSize;
      const potOdds = callAmount / totalPot;
      const americanOdds = potOdds < 0.5 ? Math.round((1/potOdds - 1) * 100) : -Math.round(100 / (1/potOdds - 1));

      await calculateOdds({
        american_odds: americanOdds,
        win_probability: winProbability,
        bankroll: bankroll,
        kelly_fraction: 0.25, // Conservative Kelly for poker
      }, 'poker-hand');

      toast.success('Pot odds calculated for poker hand!');
    } catch (error) {
      toast.error('Failed to calculate pot odds');
    }
  };

  const handleAnalyzeHand = async () => {
    try {
      const opportunities = await analyzeBetting('poker', handDescription);
      toast.success(`Found ${opportunities.length} betting opportunities`);
    } catch (error) {
      toast.error('Failed to analyze poker hand');
    }
  };

  const handleGenerateVlog = async () => {
    if (!handDescription.trim()) {
      toast.error('Please describe the poker hand first');
      return;
    }

    const potOddsCalc = oddsCalculations['poker-hand'];
    const context = `
Hand Description: ${handDescription}
Pot Size: $${potSize}
Bet to Call: $${betSize}
Estimated Win Probability: ${(winProbability * 100).toFixed(1)}%
${potOddsCalc ? `
Pot Odds Analysis:
- Decimal Odds: ${potOddsCalc.decimal.toFixed(2)}
- Implied Probability: ${(potOddsCalc.implied_probability * 100).toFixed(1)}%
- Expected Value: ${potOddsCalc.ev_percentage.toFixed(1)}%
- Kelly Recommendation: ${(potOddsCalc.kelly_percentage * 100).toFixed(1)}% of bankroll
- Recommended Bet: $${potOddsCalc.recommended_stake.toFixed(2)}
` : ''}
`;

    try {
      const instance = await executeAgent(
        'poker-vlogger', 
        `Create an engaging poker vlog script analyzing this hand with proper odds calculations and strategic insights: ${context}`,
        {
          include_odds_analysis: true,
          target_length: 'medium',
          style: 'educational_entertaining'
        }
      );
      
      toast.success('Poker vlog generation started!');
    } catch (error) {
      toast.error('Failed to start poker vlog generation');
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            🎰 Poker Vlogger Agent with Odds Tools
            <Badge variant="info" size="sm">Orchestra Integration</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Hand Description</label>
              <Textarea
                value={handDescription}
                onChange={(e) => setHandDescription(e.target.value)}
                placeholder="Describe the poker hand situation (position, cards, action, etc.)"
                rows={3}
              />
            </div>
            
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-sm font-medium mb-1">Pot Size ($)</label>
                  <Input
                    type="number"
                    value={potSize}
                    onChange={(e) => setPotSize(Number(e.target.value))}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Bet to Call ($)</label>
                  <Input
                    type="number"
                    value={betSize}
                    onChange={(e) => setBetSize(Number(e.target.value))}
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-sm font-medium mb-1">Win Probability</label>
                  <Input
                    type="number"
                    step="0.01"
                    min="0"
                    max="1"
                    value={winProbability}
                    onChange={(e) => setWinProbability(Number(e.target.value))}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Bankroll ($)</label>
                  <Input
                    type="number"
                    value={bankroll}
                    onChange={(e) => setBankroll(Number(e.target.value))}
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="flex gap-2 flex-wrap">
            <Button 
              onClick={handleCalculatePotOdds} 
              disabled={toolsLoading}
              variant="secondary"
            >
              📊 Calculate Pot Odds
            </Button>
            
            <Button 
              onClick={handleAnalyzeHand} 
              disabled={toolsLoading}
              variant="secondary"
            >
              🎯 Analyze Hand
            </Button>
            
            <Button 
              onClick={handleGenerateVlog} 
              disabled={toolsLoading || !handDescription.trim()}
            >
              🎬 Generate Vlog Script
            </Button>
          </div>

          {toolsError && (
            <div className="text-red-500 text-sm bg-red-900/20 p-2 rounded">
              Error: {toolsError}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Odds Calculation Results */}
      {oddsCalculations['poker-hand'] && (
        <Card>
          <CardHeader>
            <CardTitle>Pot Odds Analysis</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <div className="text-sm text-muted-foreground">Decimal Odds</div>
                <div className="text-xl font-semibold">
                  {oddsCalculations['poker-hand'].decimal.toFixed(2)}
                </div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">Implied Probability</div>
                <div className="text-xl font-semibold">
                  {(oddsCalculations['poker-hand'].implied_probability * 100).toFixed(1)}%
                </div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">Expected Value</div>
                <div className={`text-xl font-semibold ${
                  oddsCalculations['poker-hand'].ev_percentage > 0 ? 'text-green-500' : 'text-red-500'
                }`}>
                  {oddsCalculations['poker-hand'].ev_percentage > 0 ? '+' : ''}
                  {oddsCalculations['poker-hand'].ev_percentage.toFixed(1)}%
                </div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">Kelly Recommendation</div>
                <div className="text-xl font-semibold">
                  ${oddsCalculations['poker-hand'].recommended_stake.toFixed(2)}
                </div>
              </div>
            </div>

            {oddsCalculations['poker-hand'].warnings.length > 0 && (
              <div className="mt-4 space-y-2">
                <div className="text-sm font-medium text-yellow-500">Warnings:</div>
                {oddsCalculations['poker-hand'].warnings.map((warning, index) => (
                  <Badge key={index} variant="warning" size="sm">
                    {warning}
                  </Badge>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Betting Opportunities */}
      {bettingOpportunities.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Strategic Opportunities</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {bettingOpportunities.map((opportunity) => (
                <div key={opportunity.id} className="border border-border rounded-lg p-3">
                  <div className="flex items-center justify-between mb-2">
                    <div className="font-medium">{opportunity.game}</div>
                    <Badge 
                      variant={opportunity.recommendation === 'bet' ? 'success' : 'warning'}
                      size="sm"
                    >
                      {opportunity.recommendation}
                    </Badge>
                  </div>
                  <div className="text-sm text-muted-foreground mb-2">
                    {opportunity.reasoning}
                  </div>
                  <div className="flex gap-4 text-sm">
                    <span>Edge: {opportunity.edge_percentage.toFixed(1)}%</span>
                    <span>Confidence: {(opportunity.confidence * 100).toFixed(0)}%</span>
                    <span>Suggested: ${opportunity.suggested_stake}</span>
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