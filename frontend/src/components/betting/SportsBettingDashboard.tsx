import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  ChartBarIcon, 
  ArrowTrendingUpIcon, 
  CurrencyDollarIcon,
  ExclamationTriangleIcon,
  FireIcon,
  ClockIcon,
  CheckCircleIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline';
import { useAgentOrchestraStore, useAgentOrchestraSelectors } from '../../store/agentOrchestraStore';
import type { BettingOpportunity } from '../../services/agent-orchestra.service';
import { toast } from 'sonner';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';

console.log('[SportsBettingDashboard] Module loaded');

interface SportsBettingDashboardProps {
  className?: string;
}

export const SportsBettingDashboard: React.FC<SportsBettingDashboardProps> = ({ className }) => {
  console.log('[SportsBettingDashboard] Component rendering...');
  
  const [selectedSport, setSelectedSport] = useState('all');
  const [analysisType, setAnalysisType] = useState('game');
  const [autoRefresh, setAutoRefresh] = useState(true);

  const {
    bettingOpportunities,
    toolsLoading,
    analyzeBetting,
    connectWebSocket,
    wsConnected
  } = useAgentOrchestraStore();

  const {
    isConnected
  } = useAgentOrchestraSelectors();
  
  console.log('[SportsBettingDashboard] State:', {
    selectedSport,
    analysisType,
    autoRefresh,
    bettingOpportunities,
    toolsLoading,
    wsConnected,
    isConnected
  });

  // Derived state for different opportunity types
  const liveBettingOpportunities = bettingOpportunities?.filter(op => op.bet_type?.toLowerCase().includes('live')) || [];
  const arbitrageOpportunities = bettingOpportunities?.filter(op => op.bet_type?.toLowerCase().includes('arbitrage')) || [];
  const highValueOpportunities = bettingOpportunities?.filter(op => op.edge_percentage >= 10) || [];
  const lowRiskOpportunities = bettingOpportunities?.filter(op => op.risk_level === 'low') || [];

  const sports = [
    { value: 'all', label: 'All Sports' },
    { value: 'nfl', label: 'NFL' },
    { value: 'nba', label: 'NBA' },
    { value: 'mlb', label: 'MLB' },
    { value: 'nhl', label: 'NHL' },
    { value: 'soccer', label: 'Soccer' },
    { value: 'tennis', label: 'Tennis' },
    { value: 'mma', label: 'MMA' }
  ];

  useEffect(() => {
    console.log('[SportsBettingDashboard] selectedSport changed:', selectedSport);
    if (selectedSport !== 'all') {
      console.log('[SportsBettingDashboard] Calling analyzeBetting for:', selectedSport);
      analyzeBetting(selectedSport)
        .then(result => console.log('[SportsBettingDashboard] analyzeBetting result:', result))
        .catch(error => console.error('[SportsBettingDashboard] analyzeBetting error:', error));
    }
  }, [selectedSport, analyzeBetting]);

  // Connect to WebSocket only once on component mount
  useEffect(() => {
    console.log('[SportsBettingDashboard] Mount effect - wsConnected:', wsConnected);
    if (!wsConnected) {
      // Add a small delay to ensure environment variables are loaded
      const timer = setTimeout(() => {
        console.log('[SportsBetting] Connecting to DBAO WebSocket...');
        connectWebSocket();
      }, 100);
      return () => clearTimeout(timer);
    }
  }, []);

  useEffect(() => {
    if (autoRefresh && selectedSport !== 'all') {
      const interval = setInterval(() => {
        analyzeBetting(selectedSport).catch(console.error);
      }, 30000); // Refresh every 30 seconds
      
      return () => clearInterval(interval);
    }
  }, [autoRefresh, selectedSport, analyzeBetting]);

  const handleAnalyzeSport = async () => {
    if (selectedSport === 'all') {
      toast.error('Please select a specific sport for analysis');
      return;
    }

    try {
      const opportunities = await analyzeBetting(selectedSport, undefined, analysisType);
      toast.success(`Analysis complete: ${opportunities.length} opportunities found`);
    } catch (error) {
      console.error('Analysis failed:', error);
    }
  };

  const getEdgeVariant = (edge: number) => {
    if (edge >= 10) return 'success';
    if (edge >= 5) return 'info';
    if (edge >= 2) return 'warning';
    return 'secondary';
  };

  const getRiskVariant = (risk: string) => {
    switch (risk) {
      case 'low': return 'success';
      case 'medium': return 'warning';
      case 'high': return 'error';
      default: return 'secondary';
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return 'text-green-400';
    if (confidence >= 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  console.log('[SportsBettingDashboard] Rendering component with:', {
    liveBettingOpportunities: liveBettingOpportunities.length,
    arbitrageOpportunities: arbitrageOpportunities.length,
    highValueOpportunities: highValueOpportunities.length,
    lowRiskOpportunities: lowRiskOpportunities.length,
    totalOpportunities: bettingOpportunities?.length || 0
  });

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <Card>
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-gray-100 flex items-center">
            <ChartBarIcon className="h-8 w-8 mr-3 text-green-400" />
            Sports Betting Intelligence
          </h1>
          <div className="flex items-center space-x-2">
            {isConnected ? (
              <div className="flex items-center text-green-400">
                <div className="h-2 w-2 bg-green-500 rounded-full mr-2 animate-pulse" />
                <span className="text-sm">Live Data</span>
              </div>
            ) : (
              <div className="flex items-center text-red-400">
                <div className="h-2 w-2 bg-red-500 rounded-full mr-2" />
                <span className="text-sm">Offline</span>
              </div>
            )}
          </div>
        </div>

        {/* Controls */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Sport
            </label>
            <select
              value={selectedSport}
              onChange={(e) => setSelectedSport(e.target.value)}
              className="w-full px-3 py-2 bg-dark-800 border border-dark-700 rounded-lg text-gray-100 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              {sports.map((sport) => (
                <option key={sport.value} value={sport.value}>
                  {sport.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Analysis Type
            </label>
            <select
              value={analysisType}
              onChange={(e) => setAnalysisType(e.target.value)}
              className="w-full px-3 py-2 bg-dark-800 border border-dark-700 rounded-lg text-gray-100 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="game">Game Analysis</option>
              <option value="prop">Prop Bets</option>
              <option value="arbitrage">Arbitrage</option>
              <option value="live">Live Betting</option>
            </select>
          </div>

          <div className="flex items-end">
            <Button
              onClick={handleAnalyzeSport}
              disabled={selectedSport === 'all'}
              loading={toolsLoading}
              variant="primary"
              className="w-full"
            >
              Analyze
            </Button>
          </div>

          <div className="flex items-center">
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                className="rounded border-dark-600 bg-dark-800 text-primary-500 focus:ring-primary-500"
              />
              <span className="text-sm text-gray-300">Auto Refresh</span>
            </label>
          </div>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="glass rounded-lg p-4 border border-green-500/20 bg-green-500/5">
            <div className="flex items-center">
              <ArrowTrendingUpIcon className="h-8 w-8 text-green-400" />
              <div className="ml-3">
                <p className="text-sm font-medium text-green-300">
                  High Value
                </p>
                <p className="text-lg font-semibold text-green-400">
                  {highValueOpportunities?.length || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="glass rounded-lg p-4 border border-blue-500/20 bg-blue-500/5">
            <div className="flex items-center">
              <CurrencyDollarIcon className="h-8 w-8 text-blue-400" />
              <div className="ml-3">
                <p className="text-sm font-medium text-blue-300">
                  Arbitrage
                </p>
                <p className="text-lg font-semibold text-blue-400">
                  {arbitrageOpportunities?.length || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="glass rounded-lg p-4 border border-yellow-500/20 bg-yellow-500/5">
            <div className="flex items-center">
              <FireIcon className="h-8 w-8 text-yellow-400" />
              <div className="ml-3">
                <p className="text-sm font-medium text-yellow-300">
                  Live Ops
                </p>
                <p className="text-lg font-semibold text-yellow-400">
                  {liveBettingOpportunities?.length || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="glass rounded-lg p-4 border border-purple-500/20 bg-purple-500/5">
            <div className="flex items-center">
              <CheckCircleIcon className="h-8 w-8 text-purple-400" />
              <div className="ml-3">
                <p className="text-sm font-medium text-purple-300">
                  Low Risk
                </p>
                <p className="text-lg font-semibold text-purple-400">
                  {lowRiskOpportunities?.length || 0}
                </p>
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Opportunities List */}
      {(bettingOpportunities?.length || 0) > 0 && (
        <Card>
          <h2 className="text-xl font-semibold text-gray-100 mb-4 flex items-center">
            <ArrowTrendingUpIcon className="h-6 w-6 mr-2 text-green-400" />
            Betting Opportunities
            <Badge variant="info" className="ml-2">
              {bettingOpportunities?.length || 0} found
            </Badge>
          </h2>
          
          <div className="space-y-4">
            {(bettingOpportunities || []).map((opportunity, index) => (
              <motion.div
                key={opportunity.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="glass border border-white/10 rounded-lg p-4 hover:border-primary-500/50 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="font-semibold text-gray-100">
                        {opportunity.game}
                      </h3>
                      <span className="text-sm text-gray-400 uppercase">
                        {opportunity.sport}
                      </span>
                      <Badge variant={getRiskVariant(opportunity.risk_level)} size="sm">
                        {opportunity.risk_level} risk
                      </Badge>
                    </div>
                    
                    <p className="text-sm text-gray-400 mb-3">
                      {opportunity.bet_type}
                    </p>
                    
                    <p className="text-sm text-gray-300 mb-3">
                      {opportunity.reasoning}
                    </p>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div className="flex items-center gap-2">
                        <span className="text-gray-400">Edge:</span>
                        <Badge variant={getEdgeVariant(opportunity.edge_percentage)} size="sm">
                          {opportunity.edge_percentage.toFixed(1)}%
                        </Badge>
                      </div>
                      <div>
                        <span className="text-gray-400">Confidence:</span>
                        <span className={`ml-1 font-semibold ${getConfidenceColor(opportunity.confidence)}`}>
                          {opportunity.confidence}%
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-400">Stake:</span>
                        <span className="ml-1 font-semibold text-green-400">
                          ${opportunity.suggested_stake}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-400">Odds:</span>
                        <span className="ml-1 font-semibold text-gray-100">
                          {opportunity.odds.current > 0 ? '+' : ''}{opportunity.odds.current}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex flex-col items-end space-y-2">
                    <Badge 
                      variant={
                        opportunity.recommendation === 'bet' ? 'success' :
                        opportunity.recommendation === 'avoid' ? 'error' : 'warning'
                      }
                    >
                      {opportunity.recommendation.toUpperCase()}
                    </Badge>
                    
                    <span className="text-xs text-gray-500">
                      {new Date(opportunity.created_at).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </Card>
      )}

      {/* Arbitrage Opportunities */}
      {(arbitrageOpportunities?.length || 0) > 0 && (
        <Card>
          <h2 className="text-xl font-semibold text-gray-100 mb-4 flex items-center">
            <CurrencyDollarIcon className="h-6 w-6 mr-2 text-blue-400" />
            Arbitrage Opportunities
            <Badge variant="info" className="ml-2">
              Risk-Free Profit
            </Badge>
          </h2>
          
          <div className="space-y-4">
            {(arbitrageOpportunities || []).map((opportunity, index) => (
              <motion.div
                key={opportunity.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="glass border border-blue-500/20 rounded-lg p-4 bg-blue-500/5"
              >
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-gray-100">
                    {opportunity.game}
                  </h3>
                  <div className="flex items-center space-x-2">
                    <Badge variant="success">
                      {opportunity.edge_percentage.toFixed(2)}% profit
                    </Badge>
                    <InformationCircleIcon className="h-5 w-5 text-blue-400" />
                  </div>
                </div>
                
                <p className="text-sm text-gray-300 mb-3">
                  {opportunity.reasoning}
                </p>
                
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div className="text-center p-2 bg-dark-800 border border-dark-700 rounded">
                    <div className="font-medium text-gray-300">Suggested Stake</div>
                    <div className="text-lg font-bold text-green-400">
                      ${opportunity.suggested_stake}
                    </div>
                  </div>
                  <div className="text-center p-2 bg-dark-800 border border-dark-700 rounded">
                    <div className="font-medium text-gray-300">Profit</div>
                    <div className="text-lg font-bold text-blue-400">
                      ${(opportunity.suggested_stake * opportunity.edge_percentage / 100).toFixed(2)}
                    </div>
                  </div>
                  <div className="text-center p-2 bg-dark-800 border border-dark-700 rounded">
                    <div className="font-medium text-gray-300">ROI</div>
                    <div className="text-lg font-bold text-green-400">
                      {opportunity.edge_percentage.toFixed(2)}%
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </Card>
      )}

      {/* No Opportunities Message */}
      {!toolsLoading && (bettingOpportunities?.length || 0) === 0 && (arbitrageOpportunities?.length || 0) === 0 && (
        <Card className="text-center py-8">
          <ExclamationTriangleIcon className="h-16 w-16 text-gray-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-100 mb-2">
            No Opportunities Found
          </h3>
          <p className="text-gray-400 mb-4">
            {selectedSport === 'all' 
              ? 'Select a specific sport to analyze betting opportunities'
              : `No profitable opportunities found for ${sports.find(s => s.value === selectedSport)?.label}`
            }
          </p>
          <Button
            onClick={() => selectedSport !== 'all' && analyzeBetting(selectedSport).catch(console.error)}
            variant="primary"
            disabled={selectedSport === 'all'}
          >
            Refresh Analysis
          </Button>
        </Card>
      )}
    </div>
  );
};