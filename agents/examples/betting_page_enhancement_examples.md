# Betting Page Enhancer Agent - Implementation Examples

This document provides comprehensive examples of how the Betting Page Enhancer agent would transform the current `GameBettingPage.tsx` into a world-class betting analysis platform.

## Agent Overview

**Agent Name**: `betting-page-enhancer`  
**Specialization**: Sports Analytics & Betting Intelligence  
**Primary Role**: Transform basic betting interfaces into professional-grade analysis platforms

---

## Example 1: Interactive Weather Reports Enhancement

### Current Implementation
```tsx
// Basic weather display
<div className="flex items-center gap-1">
  <Cloud className="w-3 h-3" />
  <span>{gameDetails?.weather.condition} {gameDetails?.weather.temperature}°F</span>
</div>
```

### Enhanced Implementation (Agent Output)
```tsx
// Interactive weather widget with detailed analysis
<Card className="gaming-card weather-interactive">
  <div className="gaming-border-glow weather-glow"></div>
  <div className="p-4">
    <div className="flex items-center justify-between mb-3">
      <h4 className="font-bold gaming-text-primary flex items-center gap-2">
        <Cloud className="w-4 h-4" />
        Weather Impact Analysis
      </h4>
      <Badge variant="outline" className="text-xs">
        Impact: {weatherImpact.severity}
      </Badge>
    </div>
    
    <div className="space-y-3">
      {/* Current Conditions */}
      <div className="gaming-weather-current" onClick={() => setWeatherDetailView('current')}>
        <div className="flex items-center justify-between cursor-pointer">
          <div className="flex items-center gap-2">
            <WeatherIcon condition={weather.condition} className="w-5 h-5" />
            <span className="font-medium">{weather.condition}</span>
          </div>
          <span className="gaming-text-neon">{weather.temperature}°F</span>
        </div>
        <div className="text-xs gaming-text-secondary mt-1">
          Feels like {weather.feelsLike}°F • Humidity {weather.humidity}%
        </div>
      </div>

      {/* Wind Analysis */}
      <div className="gaming-weather-wind" onClick={() => setWeatherDetailView('wind')}>
        <div className="flex items-center justify-between cursor-pointer">
          <div className="flex items-center gap-2">
            <Wind className="w-4 h-4" />
            <span>Wind Impact</span>
          </div>
          <div className="text-right">
            <div className="gaming-text-neon">{weather.windSpeed} mph {weather.windDirection}</div>
            <div className="text-xs gaming-text-accent">
              {windImpact.passingEffect > 0 ? `+${windImpact.passingEffect}%` : `${windImpact.passingEffect}%`} passing
            </div>
          </div>
        </div>
      </div>

      {/* Betting Impact Summary */}
      <div className="gaming-status bg-gaming-neon-yellow/10 border-gaming-neon-yellow p-2">
        <div className="text-xs">
          <div className="font-medium">Betting Implications:</div>
          <ul className="mt-1 space-y-1">
            {weatherImpact.recommendations.map((rec, idx) => (
              <li key={idx} className="flex items-center gap-1">
                <ChevronRight className="w-3 h-3" />
                {rec}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  </div>

  {/* Detailed Weather Modal */}
  {weatherDetailView && (
    <WeatherDetailModal 
      view={weatherDetailView}
      weather={weather}
      impact={weatherImpact}
      onClose={() => setWeatherDetailView(null)}
    />
  )}
</Card>
```

---

## Example 2: Advanced Kelly Criterion Calculator

### Current Implementation
```tsx
// Basic Kelly calculation
const calculateKellyStake = (option: BettingOption, bankroll: number, winProb?: number) => {
  const prob = winProb || defaultWinProb;
  const kellyPercent = calculateKellyPercentage(option.odds, prob);
  const fractionalKelly = kellyPercent * kellyFraction / 100;
  return Math.round((fractionalKelly / 100) * bankroll);
};
```

### Enhanced Implementation (Agent Output)
```tsx
// Advanced Kelly calculator with multiple strategies
interface KellyStrategy {
  name: string;
  multiplier: number;
  description: string;
  riskLevel: 'conservative' | 'moderate' | 'aggressive';
}

const kellyStrategies: KellyStrategy[] = [
  { name: 'Quarter Kelly', multiplier: 0.25, description: 'Conservative approach, reduces volatility', riskLevel: 'conservative' },
  { name: 'Half Kelly', multiplier: 0.5, description: 'Balanced growth and risk', riskLevel: 'moderate' },
  { name: 'Full Kelly', multiplier: 1.0, description: 'Maximum growth rate, higher volatility', riskLevel: 'aggressive' },
  { name: 'Kelly+', multiplier: 1.25, description: 'Aggressive growth for high-confidence bets', riskLevel: 'aggressive' }
];

const AdvancedKellyCalculator = () => {
  const [selectedStrategy, setSelectedStrategy] = useState<KellyStrategy>(kellyStrategies[0]);
  const [customWinProb, setCustomWinProb] = useState<number>(defaultWinProb);
  const [kellyResults, setKellyResults] = useState<KellyCalculationResult[]>([]);
  const [portfolioAnalysis, setPortfolioAnalysis] = useState<PortfolioAnalysis | null>(null);

  const calculateAdvancedKelly = (option: BettingOption) => {
    const impliedProb = calculateImpliedProbability(option.odds);
    const edge = customWinProb - impliedProb;
    const kellyPercentage = calculateKellyPercentage(option.odds, customWinProb);
    const adjustedKelly = kellyPercentage * selectedStrategy.multiplier;
    const recommendedStake = (adjustedKelly / 100) * bankroll;
    
    const expectedValue = calculateExpectedValue(option.odds, customWinProb);
    const varianceRisk = calculateVarianceRisk(option.odds, customWinProb, recommendedStake);
    const riskOfRuin = calculateRiskOfRuin(bankroll, recommendedStake, edge);

    return {
      edge,
      kellyPercentage,
      adjustedKelly,
      recommendedStake,
      expectedValue,
      varianceRisk,
      riskOfRuin,
      confidence: getConfidenceLevel(edge, impliedProb)
    };
  };

  return (
    <Card className="gaming-card kelly-advanced">
      <div className="gaming-border-glow"></div>
      <div className="p-6">
        <h3 className="text-lg font-bold gaming-text-primary mb-6 flex items-center gap-2">
          <Calculator className="w-5 h-5 animate-pulse" />
          Advanced Kelly Calculator
        </h3>

        {/* Strategy Selection */}
        <div className="mb-6">
          <label className="block gaming-text-secondary text-sm mb-3">Betting Strategy</label>
          <div className="grid grid-cols-2 gap-2">
            {kellyStrategies.map(strategy => (
              <button
                key={strategy.name}
                onClick={() => setSelectedStrategy(strategy)}
                className={`p-3 rounded text-xs transition-all ${
                  selectedStrategy.name === strategy.name 
                    ? 'gaming-btn-active' 
                    : 'gaming-card border border-gaming-border hover:border-gaming-neon-cyan'
                }`}
              >
                <div className="font-bold">{strategy.name}</div>
                <div className="text-xs gaming-text-secondary mt-1">{strategy.description}</div>
                <Badge 
                  variant={strategy.riskLevel === 'conservative' ? 'outline' : 
                          strategy.riskLevel === 'moderate' ? 'secondary' : 'destructive'}
                  className="text-xs mt-1"
                >
                  {strategy.riskLevel}
                </Badge>
              </button>
            ))}
          </div>
        </div>

        {/* Win Probability Input */}
        <div className="mb-6">
          <label className="block gaming-text-secondary text-sm mb-2">
            True Win Probability ({(customWinProb * 100).toFixed(1)}%)
          </label>
          <input
            type="range"
            min="0.35"
            max="0.75"
            step="0.01"
            value={customWinProb}
            onChange={(e) => setCustomWinProb(Number(e.target.value))}
            className="w-full accent-cyan-500 mb-2"
          />
          <div className="flex justify-between text-xs gaming-text-secondary">
            <span>35% (Underdog)</span>
            <span>55% (Even)</span>
            <span>75% (Favorite)</span>
          </div>
        </div>

        {/* Kelly Results for Current Bet */}
        {selectedOption && (
          <div className="mb-6">
            <h4 className="font-medium gaming-text-primary mb-3">Analysis: {selectedOption.name}</h4>
            <div className="gaming-card border border-gaming-border p-4">
              <div className="grid grid-cols-3 gap-4 text-xs">
                <div className="text-center">
                  <div className="gaming-text-secondary">Kelly %</div>
                  <div className="font-bold text-lg gaming-text-neon">
                    {kellyResult.adjustedKelly.toFixed(1)}%
                  </div>
                </div>
                <div className="text-center">
                  <div className="gaming-text-secondary">Stake</div>
                  <div className="font-bold text-lg gaming-text-primary">
                    ${kellyResult.recommendedStake.toFixed(0)}
                  </div>
                </div>
                <div className="text-center">
                  <div className="gaming-text-secondary">Edge</div>
                  <div className={`font-bold text-lg ${kellyResult.edge > 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {(kellyResult.edge * 100).toFixed(1)}%
                  </div>
                </div>
              </div>
              
              <div className="mt-4 pt-4 border-t border-gaming-border">
                <div className="grid grid-cols-2 gap-4 text-xs">
                  <div>
                    <span className="gaming-text-secondary">Expected Value: </span>
                    <span className={kellyResult.expectedValue > 0 ? 'text-green-400' : 'text-red-400'}>
                      {kellyResult.expectedValue > 0 ? '+' : ''}{kellyResult.expectedValue.toFixed(1)}%
                    </span>
                  </div>
                  <div>
                    <span className="gaming-text-secondary">Risk of Ruin: </span>
                    <span className={kellyResult.riskOfRuin < 5 ? 'text-green-400' : kellyResult.riskOfRuin < 15 ? 'text-yellow-400' : 'text-red-400'}>
                      {kellyResult.riskOfRuin.toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Portfolio Analysis */}
        <div className="mb-4">
          <h4 className="font-medium gaming-text-primary mb-3">Portfolio Risk Analysis</h4>
          <div className="gaming-card border border-gaming-border p-4">
            <div className="grid grid-cols-2 gap-4 text-xs">
              <div>
                <div className="gaming-text-secondary mb-2">Current Allocation</div>
                <div className="space-y-1">
                  <div className="flex justify-between">
                    <span>Total Staked:</span>
                    <span className="font-bold">${totalStaked}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>% of Bankroll:</span>
                    <span className={`font-bold ${(totalStaked/bankroll) > 0.15 ? 'text-red-400' : 'text-green-400'}`}>
                      {((totalStaked/bankroll) * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
              <div>
                <div className="gaming-text-secondary mb-2">Risk Metrics</div>
                <div className="space-y-1">
                  <div className="flex justify-between">
                    <span>Portfolio Kelly:</span>
                    <span className="font-bold">{portfolioKelly.toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Max Drawdown:</span>
                    <span className="font-bold text-red-400">{maxDrawdown.toFixed(1)}%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
};
```

---

## Example 3: Clickable Injury Reports with Impact Analysis

### Current Implementation
```tsx
// Basic injury list
{gameDetails?.injuries.map((injury, idx) => (
  <div key={idx} className="gaming-status text-xs p-2">
    <div className="flex items-center gap-2 mb-1">
      <Badge variant={injury.status === 'Out' ? 'destructive' : 'secondary'}>
        {injury.status}
      </Badge>
      <span className="font-medium">{injury.player}</span>
    </div>
    <div className="gaming-text-secondary">
      {injury.injury} • {injury.team}
    </div>
  </div>
))}
```

### Enhanced Implementation (Agent Output)
```tsx
// Interactive injury analysis with detailed impact ratings
interface InjuryImpact {
  player: string;
  position: string;
  status: InjuryStatus;
  injury: string;
  team: string;
  impactRating: number; // 1-10 scale
  replacementQuality: number; // 1-10 scale
  historicalData: PlayerHistoricalData;
  bettingImplications: BettingImplication[];
  recoveryTimeline: string;
  gameTimeDecision: boolean;
}

const InteractiveInjuryReport = () => {
  const [selectedInjury, setSelectedInjury] = useState<InjuryImpact | null>(null);
  const [injuryFilter, setInjuryFilter] = useState<'all' | 'high-impact' | 'questionable'>('all');

  const getImpactColor = (rating: number) => {
    if (rating >= 8) return 'text-red-500 bg-red-500/20';
    if (rating >= 6) return 'text-orange-500 bg-orange-500/20';
    if (rating >= 4) return 'text-yellow-500 bg-yellow-500/20';
    return 'text-green-500 bg-green-500/20';
  };

  const filteredInjuries = injuries.filter(injury => {
    if (injuryFilter === 'high-impact') return injury.impactRating >= 7;
    if (injuryFilter === 'questionable') return injury.status === 'Questionable';
    return true;
  });

  return (
    <Card className="gaming-card">
      <div className="gaming-border-glow"></div>
      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold gaming-text-primary flex items-center gap-2">
            <AlertTriangle className="w-5 h-5" />
            Injury Impact Analysis
          </h3>
          
          {/* Filter Tabs */}
          <div className="flex gap-1">
            {[
              { key: 'all', label: 'All', count: injuries.length },
              { key: 'high-impact', label: 'High Impact', count: injuries.filter(i => i.impactRating >= 7).length },
              { key: 'questionable', label: 'Game Time', count: injuries.filter(i => i.status === 'Questionable').length }
            ].map(filter => (
              <button
                key={filter.key}
                onClick={() => setInjuryFilter(filter.key as any)}
                className={`px-3 py-1 rounded text-xs transition-all ${
                  injuryFilter === filter.key 
                    ? 'bg-cyan-500 text-black font-bold' 
                    : 'bg-gray-700 gaming-text-secondary hover:bg-gray-600'
                }`}
              >
                {filter.label} ({filter.count})
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-3 max-h-80 overflow-y-auto">
          {filteredInjuries.map((injury, idx) => (
            <div 
              key={idx}
              className={`gaming-card cursor-pointer transition-all border ${
                selectedInjury?.player === injury.player 
                  ? 'border-gaming-neon-cyan' 
                  : 'border-gaming-border hover:border-gaming-accent'
              }`}
              onClick={() => setSelectedInjury(injury)}
            >
              <div className="p-3">
                {/* Header Row */}
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Badge 
                      variant={
                        injury.status === 'Out' ? 'destructive' :
                        injury.status === 'Doubtful' ? 'destructive' :
                        injury.status === 'Questionable' ? 'secondary' : 
                        'outline'
                      } 
                      className="text-xs"
                    >
                      {injury.status}
                    </Badge>
                    <span className="font-bold gaming-text-primary">{injury.player}</span>
                    <Badge variant="outline" className="text-xs">
                      {injury.position}
                    </Badge>
                  </div>
                  
                  {/* Impact Rating */}
                  <div className={`px-2 py-1 rounded text-xs font-bold ${getImpactColor(injury.impactRating)}`}>
                    Impact: {injury.impactRating}/10
                  </div>
                </div>

                {/* Injury Details */}
                <div className="flex items-center justify-between text-xs">
                  <span className="gaming-text-secondary">
                    {injury.injury} • {injury.team}
                  </span>
                  {injury.gameTimeDecision && (
                    <Badge variant="outline" className="text-xs animate-pulse">
                      Game Time Decision
                    </Badge>
                  )}
                </div>

                {/* Quick Impact Summary */}
                <div className="mt-2 pt-2 border-t border-gaming-border">
                  <div className="grid grid-cols-2 gap-4 text-xs">
                    <div>
                      <span className="gaming-text-secondary">Replacement: </span>
                      <span className={`font-bold ${
                        injury.replacementQuality >= 7 ? 'text-green-400' :
                        injury.replacementQuality >= 5 ? 'text-yellow-400' : 'text-red-400'
                      }`}>
                        {injury.replacementQuality}/10
                      </span>
                    </div>
                    <div>
                      <span className="gaming-text-secondary">Recovery: </span>
                      <span className="font-bold gaming-text-primary">{injury.recoveryTimeline}</span>
                    </div>
                  </div>
                </div>

                {/* Betting Implications Preview */}
                {injury.bettingImplications.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-gaming-border">
                    <div className="text-xs gaming-text-accent">
                      💡 {injury.bettingImplications[0].description}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Detailed Injury Modal */}
      {selectedInjury && (
        <InjuryDetailModal 
          injury={selectedInjury}
          onClose={() => setSelectedInjury(null)}
        />
      )}
    </Card>
  );
};

// Detailed injury analysis modal
const InjuryDetailModal = ({ injury, onClose }: { injury: InjuryImpact; onClose: () => void }) => (
  <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80">
    <div className="gaming-card max-w-2xl w-full max-h-[90vh] overflow-y-auto">
      <div className="gaming-border-glow"></div>
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-bold gaming-text-primary">{injury.player}</h2>
            <div className="flex items-center gap-2 mt-1">
              <Badge variant="outline">{injury.position}</Badge>
              <Badge variant="outline">{injury.team}</Badge>
            </div>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        </div>

        {/* Injury Details */}
        <div className="space-y-6">
          {/* Current Status */}
          <div className="gaming-card border border-gaming-border p-4">
            <h3 className="font-bold gaming-text-primary mb-3">Current Status</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="gaming-text-secondary text-sm">Status</div>
                <Badge className="mt-1">{injury.status}</Badge>
              </div>
              <div>
                <div className="gaming-text-secondary text-sm">Injury</div>
                <div className="font-medium gaming-text-primary">{injury.injury}</div>
              </div>
              <div>
                <div className="gaming-text-secondary text-sm">Impact Rating</div>
                <div className={`font-bold text-lg ${getImpactColor(injury.impactRating)}`}>
                  {injury.impactRating}/10
                </div>
              </div>
              <div>
                <div className="gaming-text-secondary text-sm">Recovery Timeline</div>
                <div className="font-medium gaming-text-primary">{injury.recoveryTimeline}</div>
              </div>
            </div>
          </div>

          {/* Historical Performance */}
          <div className="gaming-card border border-gaming-border p-4">
            <h3 className="font-bold gaming-text-primary mb-3">Historical Performance</h3>
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div className="text-center">
                <div className="gaming-text-secondary">Season Stats</div>
                <div className="font-bold gaming-text-primary mt-1">
                  {injury.historicalData.seasonStats}
                </div>
              </div>
              <div className="text-center">
                <div className="gaming-text-secondary">Injury History</div>
                <div className="font-bold gaming-text-primary mt-1">
                  {injury.historicalData.previousInjuries} injuries
                </div>
              </div>
              <div className="text-center">
                <div className="gaming-text-secondary">Games Missed</div>
                <div className="font-bold gaming-text-primary mt-1">
                  {injury.historicalData.gamesMissed} games
                </div>
              </div>
            </div>
          </div>

          {/* Betting Implications */}
          <div className="gaming-card border border-gaming-border p-4">
            <h3 className="font-bold gaming-text-primary mb-3">Betting Implications</h3>
            <div className="space-y-2">
              {injury.bettingImplications.map((implication, idx) => (
                <div key={idx} className="flex items-start gap-2 p-2 bg-gaming-accent/10 rounded">
                  <div className={`w-2 h-2 rounded-full mt-2 ${
                    implication.impact === 'positive' ? 'bg-green-400' :
                    implication.impact === 'negative' ? 'bg-red-400' : 'bg-yellow-400'
                  }`}></div>
                  <div className="flex-1">
                    <div className="font-medium gaming-text-primary text-sm">
                      {implication.market}
                    </div>
                    <div className="gaming-text-secondary text-xs mt-1">
                      {implication.description}
                    </div>
                    {implication.recommendation && (
                      <div className="gaming-text-accent text-xs mt-1 font-medium">
                        💡 {implication.recommendation}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
);
```

---

## Example 4: Real-time Data Integration with WebSocket

### Enhanced Implementation (Agent Output)
```tsx
// Real-time data integration with WebSocket streaming
interface RealTimeDataHook {
  odds: LiveOdds[];
  games: LiveGame[];
  lineMovements: LineMovement[];
  alerts: BettingAlert[];
  connectionStatus: 'connected' | 'connecting' | 'disconnected';
}

const useRealTimeBettingData = (gameId: string): RealTimeDataHook => {
  const [odds, setOdds] = useState<LiveOdds[]>([]);
  const [games, setGames] = useState<LiveGame[]>([]);
  const [lineMovements, setLineMovements] = useState<LineMovement[]>([]);
  const [alerts, setAlerts] = useState<BettingAlert[]>([]);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'connecting' | 'disconnected'>('connecting');

  useEffect(() => {
    const ws = new WebSocket(`${process.env.VITE_WS_URL}/ws/betting/${gameId}/`);
    
    ws.onopen = () => {
      setConnectionStatus('connected');
      console.log('🔗 Real-time betting data connected');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      switch (data.type) {
        case 'odds_update':
          setOdds(prevOdds => {
            const newOdds = [...prevOdds];
            const existingIndex = newOdds.findIndex(o => o.market_id === data.odds.market_id);
            if (existingIndex >= 0) {
              newOdds[existingIndex] = { ...newOdds[existingIndex], ...data.odds };
            } else {
              newOdds.push(data.odds);
            }
            return newOdds;
          });
          
          // Track line movement
          if (data.previous_odds) {
            const movement: LineMovement = {
              market_id: data.odds.market_id,
              timestamp: new Date(),
              previous_odds: data.previous_odds,
              new_odds: data.odds.odds,
              movement_size: Math.abs(data.odds.odds - data.previous_odds),
              direction: data.odds.odds > data.previous_odds ? 'up' : 'down'
            };
            setLineMovements(prev => [movement, ...prev.slice(0, 49)]); // Keep last 50 movements
          }
          break;
          
        case 'game_update':
          setGames(prevGames => {
            const newGames = [...prevGames];
            const existingIndex = newGames.findIndex(g => g.id === data.game.id);
            if (existingIndex >= 0) {
              newGames[existingIndex] = { ...newGames[existingIndex], ...data.game };
            } else {
              newGames.push(data.game);
            }
            return newGames;
          });
          break;
          
        case 'betting_alert':
          setAlerts(prev => [data.alert, ...prev.slice(0, 9)]); // Keep last 10 alerts
          
          // Show toast notification for high-priority alerts
          if (data.alert.priority === 'high') {
            toast.success(data.alert.message, {
              description: data.alert.description,
              duration: 5000,
            });
          }
          break;
      }
    };

    ws.onclose = () => {
      setConnectionStatus('disconnected');
      console.log('❌ Real-time betting data disconnected');
    };

    ws.onerror = (error) => {
      console.error('🚨 WebSocket error:', error);
      setConnectionStatus('disconnected');
    };

    return () => {
      ws.close();
    };
  }, [gameId]);

  return { odds, games, lineMovements, alerts, connectionStatus };
};

// Real-time line movement tracker component
const LineMovementTracker = ({ gameId }: { gameId: string }) => {
  const { lineMovements, connectionStatus } = useRealTimeBettingData(gameId);
  const [selectedMarket, setSelectedMarket] = useState<string | null>(null);

  const getMovementColor = (direction: 'up' | 'down') => {
    return direction === 'up' ? 'text-green-400' : 'text-red-400';
  };

  const getMovementIcon = (direction: 'up' | 'down') => {
    return direction === 'up' ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />;
  };

  return (
    <Card className="gaming-card">
      <div className="gaming-border-glow"></div>
      <div className="p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-bold gaming-text-primary flex items-center gap-2">
            <Activity className="w-4 h-4" />
            Line Movement Tracker
          </h3>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${
              connectionStatus === 'connected' ? 'bg-green-500' :
              connectionStatus === 'connecting' ? 'bg-yellow-500 animate-pulse' : 'bg-red-500'
            }`}></div>
            <span className="text-xs gaming-text-secondary capitalize">{connectionStatus}</span>
          </div>
        </div>

        <div className="space-y-2 max-h-60 overflow-y-auto">
          {lineMovements.length === 0 ? (
            <div className="text-center py-6 gaming-text-secondary">
              <Activity className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">Waiting for line movements...</p>
            </div>
          ) : (
            lineMovements.map((movement, idx) => (
              <div 
                key={idx}
                className="gaming-card border border-gaming-border p-3 cursor-pointer hover:border-gaming-accent transition-all"
                onClick={() => setSelectedMarket(movement.market_id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className={getMovementColor(movement.direction)}>
                      {getMovementIcon(movement.direction)}
                    </div>
                    <span className="font-medium gaming-text-primary text-sm">
                      {movement.market_name || `Market ${movement.market_id.slice(0, 8)}`}
                    </span>
                  </div>
                  <div className="text-right">
                    <div className={`font-bold text-sm ${getMovementColor(movement.direction)}`}>
                      {movement.previous_odds > 0 ? '+' : ''}{movement.previous_odds} → {movement.new_odds > 0 ? '+' : ''}{movement.new_odds}
                    </div>
                    <div className="text-xs gaming-text-secondary">
                      {formatDistanceToNow(movement.timestamp, { addSuffix: true })}
                    </div>
                  </div>
                </div>
                
                {movement.movement_size >= 10 && (
                  <div className="mt-2 pt-2 border-t border-gaming-border">
                    <Badge variant="outline" className="text-xs">
                      🚨 Significant Movement: {movement.movement_size} points
                    </Badge>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </Card>
  );
};
```

---

## Example 5: Agent Integration Dashboard

### Enhanced Implementation (Agent Output)
```tsx
// Agent selector integration for betting page
const BettingAgentIntegration = ({ gameId, currentGame }: { gameId: string; currentGame: Game }) => {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [agentExecution, setAgentExecution] = useState<AgentExecution | null>(null);
  const [availableAgents, setAvailableAgents] = useState<UnifiedAgentTemplate[]>([]);

  // Fetch relevant agents for betting analysis
  useEffect(() => {
    const fetchRelevantAgents = async () => {
      try {
        const response = await fetch('/api/agents/find-for-task/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Token ${localStorage.getItem('authToken')}`
          },
          body: JSON.stringify({
            task_description: `Analyze betting opportunities for ${currentGame.away_team_name} vs ${currentGame.home_team_name}`,
            required_capabilities: ['sports_analytics', 'betting_analysis', 'odds_calculation'],
            specialization: 'sports-analytics',
            limit: 8
          })
        });
        
        const agents = await response.json();
        setAvailableAgents(agents);
      } catch (error) {
        console.error('Failed to fetch betting agents:', error);
      }
    };

    if (currentGame) {
      fetchRelevantAgents();
    }
  }, [currentGame]);

  const executeAgent = async (agentName: string, taskDescription: string) => {
    try {
      const response = await fetch('/api/agents/execute/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Token ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify({
          agent_name: agentName,
          task_description: taskDescription,
          context: {
            game_id: gameId,
            game_data: currentGame,
            betting_context: 'game_betting_page'
          }
        })
      });
      
      const execution = await response.json();
      setAgentExecution(execution);
      setSelectedAgent(agentName);
      
      toast.success(`🤖 ${agentName} analysis started`, {
        description: 'Real-time analysis will appear below'
      });
    } catch (error) {
      console.error('Failed to execute agent:', error);
      toast.error('Failed to start agent analysis');
    }
  };

  return (
    <Card className="gaming-card">
      <div className="gaming-border-glow"></div>
      <div className="p-6">
        <h3 className="text-lg font-bold gaming-text-primary mb-4 flex items-center gap-2">
          <Bot className="w-5 h-5" />
          AI Betting Analysis
        </h3>

        {/* Available Agents */}
        <div className="mb-6">
          <div className="grid grid-cols-2 gap-3">
            {availableAgents.slice(0, 6).map(agent => (
              <button
                key={agent.name}
                onClick={() => executeAgent(agent.name, `Provide comprehensive betting analysis for ${currentGame.away_team_name} vs ${currentGame.home_team_name}`)}
                className={`gaming-card border p-3 text-left transition-all hover:border-gaming-neon-cyan ${
                  selectedAgent === agent.name ? 'border-gaming-neon-green' : 'border-gaming-border'
                }`}
              >
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-2 h-2 rounded-full bg-cyan-400"></div>
                  <span className="font-bold gaming-text-primary text-sm">{agent.display_name}</span>
                </div>
                <div className="text-xs gaming-text-secondary mb-2">
                  {agent.description.slice(0, 80)}...
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="text-xs">
                    {agent.specialization.replace('-', ' ')}
                  </Badge>
                  <div className="text-xs gaming-text-accent">
                    ⭐ {(agent.confidence_score * 100).toFixed(0)}%
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Agent Execution Results */}
        {agentExecution && (
          <div className="gaming-card border border-gaming-border p-4">
            <div className="flex items-center justify-between mb-3">
              <h4 className="font-bold gaming-text-primary">
                {availableAgents.find(a => a.name === selectedAgent)?.display_name} Analysis
              </h4>
              <Badge variant="outline" className={`text-xs ${
                agentExecution.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                agentExecution.status === 'running' ? 'bg-yellow-500/20 text-yellow-400 animate-pulse' :
                agentExecution.status === 'failed' ? 'bg-red-500/20 text-red-400' :
                'bg-gray-500/20 text-gray-400'
              }`}>
                {agentExecution.status}
              </Badge>
            </div>

            {agentExecution.status === 'running' && (
              <div className="mb-4">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-4 h-4 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin"></div>
                  <span className="text-sm gaming-text-primary">{agentExecution.current_step || 'Analyzing...'}</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-cyan-500 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${agentExecution.progress_percentage}%` }}
                  ></div>
                </div>
              </div>
            )}

            {agentExecution.status === 'completed' && agentExecution.result && (
              <div className="space-y-4">
                {/* Analysis Summary */}
                {agentExecution.result.summary && (
                  <div className="gaming-card border border-gaming-accent/30 p-3">
                    <h5 className="font-bold gaming-text-primary mb-2">Key Insights</h5>
                    <div className="gaming-text-secondary text-sm">
                      {agentExecution.result.summary}
                    </div>
                  </div>
                )}

                {/* Betting Recommendations */}
                {agentExecution.result.recommendations && (
                  <div className="space-y-2">
                    <h5 className="font-bold gaming-text-primary">Recommendations</h5>
                    {agentExecution.result.recommendations.map((rec: any, idx: number) => (
                      <div key={idx} className="gaming-card border border-gaming-border p-3">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium gaming-text-primary">{rec.market}</span>
                          <Badge variant={rec.confidence >= 0.8 ? 'default' : rec.confidence >= 0.6 ? 'secondary' : 'outline'}>
                            {(rec.confidence * 100).toFixed(0)}% confidence
                          </Badge>
                        </div>
                        <div className="text-sm gaming-text-secondary mb-2">
                          {rec.reasoning}
                        </div>
                        {rec.suggested_stake && (
                          <div className="text-xs gaming-text-accent">
                            💰 Suggested stake: ${rec.suggested_stake}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {agentExecution.status === 'failed' && (
              <div className="gaming-status bg-red-500/20 border-red-500 text-red-400 p-3">
                <div className="font-bold mb-1">Analysis Failed</div>
                <div className="text-sm">{agentExecution.error_message}</div>
              </div>
            )}
          </div>
        )}

        {/* Quick Actions */}
        <div className="mt-4 pt-4 border-t border-gaming-border">
          <div className="text-xs gaming-text-secondary mb-2">Quick Analysis</div>
          <div className="flex gap-2 flex-wrap">
            {[
              { label: 'Weather Impact', task: 'weather analysis' },
              { label: 'Injury Analysis', task: 'injury impact assessment' },
              { label: 'Value Bets', task: 'find value betting opportunities' },
              { label: 'Line Shopping', task: 'compare odds across sportsbooks' }
            ].map(action => (
              <button
                key={action.label}
                onClick={() => executeAgent('betting-page-enhancer', `Perform ${action.task} for ${currentGame.away_team_name} vs ${currentGame.home_team_name}`)}
                className="px-3 py-1 bg-gaming-accent/20 hover:bg-gaming-accent/30 rounded text-xs gaming-text-accent transition-all"
              >
                {action.label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </Card>
  );
};
```

---

## Summary

The Betting Page Enhancer agent would transform your current `GameBettingPage.tsx` from a basic betting interface into a comprehensive, professional-grade betting analysis platform with:

### Key Enhancements:

1. **Interactive Weather Reports** - Clickable, detailed weather analysis with betting implications
2. **Advanced Kelly Calculator** - Multiple strategies, risk analysis, portfolio management
3. **Clickable Injury Reports** - Detailed impact analysis, historical data, betting implications
4. **Real-time Data Integration** - WebSocket streaming, line movement tracking, live alerts
5. **Agent Integration** - Direct access to AI betting analysis from within the page
6. **Professional UI/UX** - Gaming-themed, responsive, institutional-quality interface

### Technical Implementation:
- Modular React/TypeScript components
- Django backend API enhancements
- WebSocket real-time data streaming
- Database optimizations for betting data
- Comprehensive testing and documentation

The agent would provide step-by-step implementation guidance, ensuring each enhancement integrates seamlessly with your existing codebase while maintaining your gaming theme and user experience standards.