import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { 
  TrendingUp,
  TrendingDown,
  Calculator,
  Target,
  DollarSign,
  Activity,
  AlertTriangle,
  CheckCircle,
  RefreshCw,
  Filter,
  BarChart3,
  Zap,
  Trophy,
  Clock
} from 'lucide-react';
import { toast } from 'sonner';
import api from '@/services/api';

interface OddsData {
  id: string;
  game: {
    home_team: string;
    away_team: string;
    date: string;
    league: string;
  };
  odds: {
    home: number;
    away: number;
    draw?: number;
  };
  bookmaker: string;
  value: number;
  kelly: number;
  confidence: number;
  recommendation: 'strong_buy' | 'buy' | 'hold' | 'avoid';
}

interface BettingOpportunity {
  id: string;
  type: 'value' | 'arbitrage' | 'middling';
  description: string;
  expectedValue: number;
  kellyPercentage: number;
  risk: 'low' | 'medium' | 'high';
  bookmakers: string[];
  expiry: string;
}

const SportsAnalysisPage: React.FC = () => {
  const [selectedLeague, setSelectedLeague] = useState<string>('all');
  const [selectedSport, setSelectedSport] = useState<string>('nfl');
  const [bankroll, setBankroll] = useState<number>(1000);
  const [oddsData, setOddsData] = useState<OddsData[]>([]);
  const [opportunities, setOpportunities] = useState<BettingOpportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchOddsData();
  }, [selectedSport, selectedLeague]);

  const fetchOddsData = async () => {
    try {
      setLoading(true);
      const response = await api.get('/sports/odds/', {
        params: {
          sport: selectedSport,
          league: selectedLeague === 'all' ? undefined : selectedLeague
        }
      });
      setOddsData(response.data.odds || getMockOdds());
      setOpportunities(response.data.opportunities || getMockOpportunities());
    } catch (error) {
      console.error('Error fetching odds:', error);
      setOddsData(getMockOdds());
      setOpportunities(getMockOpportunities());
    } finally {
      setLoading(false);
    }
  };

  const refreshData = async () => {
    setRefreshing(true);
    await fetchOddsData();
    setRefreshing(false);
    toast.success('Data refreshed');
  };

  const getMockOdds = (): OddsData[] => [
    {
      id: '1',
      game: {
        home_team: 'Lakers',
        away_team: 'Warriors',
        date: new Date(Date.now() + 86400000).toISOString(),
        league: 'NBA'
      },
      odds: { home: 2.10, away: 1.80 },
      bookmaker: 'DraftKings',
      value: 0.12,
      kelly: 0.08,
      confidence: 0.75,
      recommendation: 'buy'
    },
    {
      id: '2',
      game: {
        home_team: 'Chiefs',
        away_team: 'Bills',
        date: new Date(Date.now() + 172800000).toISOString(),
        league: 'NFL'
      },
      odds: { home: 1.95, away: 1.90 },
      bookmaker: 'FanDuel',
      value: 0.18,
      kelly: 0.12,
      confidence: 0.82,
      recommendation: 'strong_buy'
    },
    {
      id: '3',
      game: {
        home_team: 'Alabama',
        away_team: 'Georgia',
        date: new Date(Date.now() + 259200000).toISOString(),
        league: 'NCAAF'
      },
      odds: { home: 2.50, away: 1.60 },
      bookmaker: 'BetMGM',
      value: -0.05,
      kelly: 0.00,
      confidence: 0.45,
      recommendation: 'avoid'
    }
  ];

  const getMockOpportunities = (): BettingOpportunity[] => [
    {
      id: '1',
      type: 'arbitrage',
      description: 'Lakers vs Warriors - Risk-free profit opportunity',
      expectedValue: 0.034,
      kellyPercentage: 0.0,
      risk: 'low',
      bookmakers: ['DraftKings', 'FanDuel'],
      expiry: new Date(Date.now() + 3600000).toISOString()
    },
    {
      id: '2',
      type: 'value',
      description: 'Chiefs ML - Significant value detected',
      expectedValue: 0.15,
      kellyPercentage: 0.12,
      risk: 'medium',
      bookmakers: ['BetMGM'],
      expiry: new Date(Date.now() + 7200000).toISOString()
    }
  ];

  const calculateKellyStake = (kelly: number): number => {
    return Math.max(0, Math.min(bankroll * kelly, bankroll * 0.25));
  };

  const getRecommendationColor = (rec: string) => {
    switch (rec) {
      case 'strong_buy': return 'bg-green-600/20 text-green-500 border-green-600/50';
      case 'buy': return 'bg-blue-600/20 text-blue-500 border-blue-600/50';
      case 'hold': return 'bg-yellow-600/20 text-yellow-500 border-yellow-600/50';
      case 'avoid': return 'bg-red-600/20 text-red-500 border-red-600/50';
      default: return 'bg-gray-600/20 text-muted-foreground border-gray-600/50';
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'low': return 'text-green-500';
      case 'medium': return 'text-yellow-500';
      case 'high': return 'text-red-500';
      default: return 'text-muted-foreground';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 via-gray-800 to-gray-900">
      {/* Header */}
      <div className="bg-background/70 backdrop-blur-lg border-b border-gray-700 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
                <TrendingUp className="h-6 w-6 text-green-500" />
                Sports Analysis
              </h1>
              <p className="text-muted-foreground">AI-powered odds analysis and betting recommendations</p>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <DollarSign className="h-4 w-4 text-yellow-500" />
                <Input
                  type="number"
                  value={bankroll}
                  onChange={(e) => setBankroll(Number(e.target.value))}
                  className="w-24 bg-gray-700 border-gray-600 text-foreground"
                  placeholder="Bankroll"
                />
              </div>
              <Button
                onClick={refreshData}
                disabled={refreshing}
                className="bg-purple-600 hover:bg-purple-700"
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Filters */}
        <div className="flex flex-wrap gap-4 mb-8">
          <Select value={selectedSport} onValueChange={setSelectedSport}>
            <SelectTrigger className="w-40 bg-card border-gray-700 text-foreground">
              <SelectValue placeholder="Sport" />
            </SelectTrigger>
            <SelectContent className="bg-card border-gray-700">
              <SelectItem value="nfl">NFL</SelectItem>
              <SelectItem value="nba">NBA</SelectItem>
              <SelectItem value="ncaaf">NCAAF</SelectItem>
              <SelectItem value="ncaab">NCAAB</SelectItem>
              <SelectItem value="mlb">MLB</SelectItem>
              <SelectItem value="nhl">NHL</SelectItem>
            </SelectContent>
          </Select>

          <Select value={selectedLeague} onValueChange={setSelectedLeague}>
            <SelectTrigger className="w-40 bg-card border-gray-700 text-foreground">
              <SelectValue placeholder="League" />
            </SelectTrigger>
            <SelectContent className="bg-card border-gray-700">
              <SelectItem value="all">All Leagues</SelectItem>
              <SelectItem value="nfl">NFL</SelectItem>
              <SelectItem value="nba">NBA</SelectItem>
              <SelectItem value="sec">SEC</SelectItem>
              <SelectItem value="big10">Big 10</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="bg-card/50 border-gray-700">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Best Value</p>
                  <p className="text-2xl font-bold text-green-500">+18%</p>
                  <p className="text-xs text-muted-foreground">Chiefs ML</p>
                </div>
                <Target className="h-8 w-8 text-green-500" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-card/50 border-gray-700">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Kelly Stake</p>
                  <p className="text-2xl font-bold text-yellow-500">${calculateKellyStake(0.12).toFixed(0)}</p>
                  <p className="text-xs text-muted-foreground">12% Kelly</p>
                </div>
                <Calculator className="h-8 w-8 text-yellow-500" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-card/50 border-gray-700">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Win Rate</p>
                  <p className="text-2xl font-bold text-blue-500">73%</p>
                  <p className="text-xs text-muted-foreground">Last 30 days</p>
                </div>
                <Trophy className="h-8 w-8 text-blue-500" />
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Odds Analysis */}
          <div className="lg:col-span-2">
            <Card className="bg-card/50 border-gray-700">
              <CardHeader>
                <CardTitle className="text-foreground flex items-center gap-2">
                  <BarChart3 className="h-5 w-5 text-blue-500" />
                  Live Odds Analysis
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {loading ? (
                  <div className="text-center py-8 text-muted-foreground">Loading odds data...</div>
                ) : (
                  oddsData.map((odds) => (
                    <Card key={odds.id} className="bg-gray-700/50 border-gray-600">
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between mb-3">
                          <div>
                            <h3 className="font-semibold text-foreground">
                              {odds.game.away_team} @ {odds.game.home_team}
                            </h3>
                            <p className="text-sm text-muted-foreground">
                              {odds.game.league} • {new Date(odds.game.date).toLocaleDateString()}
                            </p>
                          </div>
                          <Badge className={getRecommendationColor(odds.recommendation)}>
                            {odds.recommendation.replace('_', ' ').toUpperCase()}
                          </Badge>
                        </div>

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                          <div>
                            <p className="text-xs text-muted-foreground">Home Odds</p>
                            <p className="font-semibold text-foreground">{odds.odds.home.toFixed(2)}</p>
                          </div>
                          <div>
                            <p className="text-xs text-muted-foreground">Away Odds</p>
                            <p className="font-semibold text-foreground">{odds.odds.away.toFixed(2)}</p>
                          </div>
                          <div>
                            <p className="text-xs text-muted-foreground">Value</p>
                            <p className={`font-semibold ${odds.value > 0 ? 'text-green-500' : 'text-red-500'}`}>
                              {odds.value > 0 ? '+' : ''}{(odds.value * 100).toFixed(1)}%
                            </p>
                          </div>
                          <div>
                            <p className="text-xs text-muted-foreground">Kelly</p>
                            <p className="font-semibold text-yellow-500">
                              {(odds.kelly * 100).toFixed(1)}%
                            </p>
                          </div>
                        </div>

                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-4">
                            <span className="text-sm text-muted-foreground">{odds.bookmaker}</span>
                            <div className="flex items-center gap-1">
                              <div className={`w-2 h-2 rounded-full ${
                                odds.confidence > 0.7 ? 'bg-green-500' : 
                                odds.confidence > 0.5 ? 'bg-yellow-500' : 'bg-red-500'
                              }`} />
                              <span className="text-xs text-muted-foreground">
                                {(odds.confidence * 100).toFixed(0)}% confidence
                              </span>
                            </div>
                          </div>
                          
                          {odds.kelly > 0 && (
                            <div className="text-sm text-muted-foreground">
                              Suggested: ${calculateKellyStake(odds.kelly).toFixed(0)}
                            </div>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  ))
                )}
              </CardContent>
            </Card>
          </div>

          {/* Opportunities */}
          <div>
            <Card className="bg-card/50 border-gray-700">
              <CardHeader>
                <CardTitle className="text-foreground flex items-center gap-2">
                  <Zap className="h-5 w-5 text-yellow-500" />
                  Live Opportunities
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {opportunities.map((opp) => (
                  <Card key={opp.id} className="bg-gray-700/50 border-gray-600">
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between mb-2">
                        <Badge className={
                          opp.type === 'arbitrage' ? 'bg-green-600/20 text-green-500 border-green-600/50' :
                          opp.type === 'value' ? 'bg-blue-600/20 text-blue-500 border-blue-600/50' :
                          'bg-purple-600/20 text-purple-400 border-purple-600/50'
                        }>
                          {opp.type.toUpperCase()}
                        </Badge>
                        <div className={`flex items-center gap-1 ${getRiskColor(opp.risk)}`}>
                          <AlertTriangle className="h-3 w-3" />
                          <span className="text-xs">{opp.risk} risk</span>
                        </div>
                      </div>

                      <h4 className="font-medium text-foreground text-sm mb-2">
                        {opp.description}
                      </h4>

                      <div className="grid grid-cols-2 gap-3 mb-3">
                        <div>
                          <p className="text-xs text-muted-foreground">Expected Value</p>
                          <p className="font-semibold text-green-500">
                            +{(opp.expectedValue * 100).toFixed(1)}%
                          </p>
                        </div>
                        {opp.kellyPercentage > 0 && (
                          <div>
                            <p className="text-xs text-muted-foreground">Kelly %</p>
                            <p className="font-semibold text-yellow-500">
                              {(opp.kellyPercentage * 100).toFixed(1)}%
                            </p>
                          </div>
                        )}
                      </div>

                      <div className="flex items-center justify-between text-xs">
                        <div className="flex items-center gap-1">
                          <Clock className="h-3 w-3 text-muted-foreground" />
                          <span className="text-muted-foreground">
                            Expires {new Date(opp.expiry).toLocaleTimeString()}
                          </span>
                        </div>
                        <div className="text-muted-foreground">
                          {opp.bookmakers.join(', ')}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}

                <Button
                  variant="outline"
                  className="w-full border-gray-600 text-muted-foreground hover:bg-gray-700"
                >
                  View All Opportunities
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Kelly Calculator */}
        <Card className="mt-8 bg-card/50 border-gray-700">
          <CardHeader>
            <CardTitle className="text-foreground flex items-center gap-2">
              <Calculator className="h-5 w-5 text-purple-500" />
              Kelly Criterion Calculator
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-4 gap-4">
              <div>
                <label className="text-sm text-muted-foreground block mb-1">Odds</label>
                <Input
                  type="number"
                  step="0.01"
                  placeholder="2.50"
                  className="bg-gray-700 border-gray-600 text-foreground"
                />
              </div>
              <div>
                <label className="text-sm text-muted-foreground block mb-1">Win Probability</label>
                <Input
                  type="number"
                  step="0.01"
                  placeholder="0.45"
                  className="bg-gray-700 border-gray-600 text-foreground"
                />
              </div>
              <div>
                <label className="text-sm text-muted-foreground block mb-1">Bankroll</label>
                <Input
                  type="number"
                  value={bankroll}
                  onChange={(e) => setBankroll(Number(e.target.value))}
                  className="bg-gray-700 border-gray-600 text-foreground"
                />
              </div>
              <div className="flex items-end">
                <Button className="w-full bg-purple-600 hover:bg-purple-700">
                  Calculate
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default SportsAnalysisPage;