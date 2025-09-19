import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Target, TrendingUp, Clock, DollarSign, AlertTriangle,
  Zap, Activity, RefreshCw, Filter, Settings,
  ArrowUp, ArrowDown, Eye, ExternalLink
} from 'lucide-react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { motion, AnimatePresence } from 'framer-motion';

interface OpportunityData {
  id: string;
  type: 'arbitrage' | 'value' | 'prediction' | 'pattern';
  domain: 'SPORTS_BETTING' | 'CRYPTO' | 'TRADING' | 'REAL_ESTATE';
  entity: string;
  description: string;
  edge: number;
  confidence: number;
  profit_potential: number;
  time_window: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  timestamp: string;
  status: 'active' | 'expired' | 'executed';
  metadata?: Record<string, any>;
}

interface ScannerSettings {
  domains: string[];
  minEdge: number;
  minConfidence: number;
  riskTolerance: string;
  autoRefresh: boolean;
}

const DOMAIN_COLORS = {
  SPORTS_BETTING: 'border-green-500/50 bg-green-900/10',
  CRYPTO: 'border-orange-500/50 bg-orange-900/10',
  TRADING: 'border-blue-500/50 bg-blue-900/10',
  REAL_ESTATE: 'border-purple-500/50 bg-purple-900/10'
};

const DOMAIN_ICONS = {
  SPORTS_BETTING: '🏈',
  CRYPTO: '₿',
  TRADING: '📈',
  REAL_ESTATE: '🏠'
};

export function LiveOpportunityStream() {
  const [opportunities, setOpportunities] = useState<OpportunityData[]>([]);
  const [scannerStatus, setScannerStatus] = useState('initializing');
  const [settings, setSettings] = useState<ScannerSettings>({
    domains: ['SPORTS_BETTING', 'CRYPTO', 'TRADING'],
    minEdge: 2.0,
    minConfidence: 0.7,
    riskTolerance: 'MEDIUM',
    autoRefresh: true
  });
  const [isScanning, setIsScanning] = useState(false);

  // Connect to Opportunity Scanner WebSocket
  const { isConnected, sendMessage } = useWebSocket({
    url: '/ws/opportunity-scanner/',
    onMessage: (data) => {
      console.log('📡 Opportunity Scanner update:', data);

      if (data.type === 'connection_established') {
        setScannerStatus('active');
        setIsScanning(true);
      } else if (data.type === 'new_opportunity') {
        const opportunity = data.data;
        setOpportunities(prev => {
          // Avoid duplicates
          const exists = prev.some(opp => opp.id === opportunity.id);
          if (!exists) {
            return [opportunity, ...prev.slice(0, 19)]; // Keep latest 20
          }
          return prev;
        });
      } else if (data.type === 'opportunity_update') {
        const updatedOpp = data.data;
        setOpportunities(prev =>
          prev.map(opp => opp.id === updatedOpp.id ? { ...opp, ...updatedOpp } : opp)
        );
      } else if (data.type === 'scanner_status') {
        setScannerStatus(data.data.scanning ? 'active' : 'paused');
      }
    },
    onOpen: () => {
      // Request initial opportunities
      sendMessage({ type: 'request_opportunities' });
    },
    reconnectInterval: 5000
  });

  // Auto-refresh opportunities
  useEffect(() => {
    if (!settings.autoRefresh || !isConnected) return;

    const interval = setInterval(() => {
      sendMessage({ type: 'request_opportunities' });
    }, 10000); // Refresh every 10 seconds

    return () => clearInterval(interval);
  }, [settings.autoRefresh, isConnected, sendMessage]);

  const updateSettings = (newSettings: Partial<ScannerSettings>) => {
    const updatedSettings = { ...settings, ...newSettings };
    setSettings(updatedSettings);
    sendMessage({ type: 'update_settings', settings: updatedSettings });
  };

  const getOpportunityIcon = (type: string) => {
    switch (type) {
      case 'arbitrage': return <Target className="h-4 w-4" />;
      case 'value': return <TrendingUp className="h-4 w-4" />;
      case 'prediction': return <Zap className="h-4 w-4" />;
      case 'pattern': return <Activity className="h-4 w-4" />;
      default: return <Target className="h-4 w-4" />;
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'LOW': return 'text-green-500 border-green-500/30';
      case 'MEDIUM': return 'text-yellow-500 border-yellow-500/30';
      case 'HIGH': return 'text-red-500 border-red-500/30';
      default: return 'text-muted-foreground border-gray-500/30';
    }
  };

  const getEdgeColor = (edge: number) => {
    if (edge >= 5) return 'text-green-500';
    if (edge >= 3) return 'text-yellow-500';
    return 'text-orange-500';
  };

  const filteredOpportunities = opportunities.filter(opp => {
    return opp.edge >= settings.minEdge &&
           opp.confidence >= settings.minConfidence &&
           settings.domains.includes(opp.domain);
  });

  return (
    <div className="space-y-6">
      {/* Scanner Status & Controls */}
      <Card className="bg-card border-blue-500/30">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Activity className={`h-5 w-5 ${isScanning ? 'text-green-500 animate-pulse' : 'text-muted-foreground'}`} />
              Live Opportunity Scanner
              <Badge className={`${isConnected ? 'bg-green-500' : 'bg-red-500'} text-foreground`}>
                {isConnected ? 'ONLINE' : 'OFFLINE'}
              </Badge>
            </div>
            <div className="flex items-center gap-2">
              <Button
                size="sm"
                variant="outline"
                onClick={() => sendMessage({ type: 'request_opportunities' })}
                disabled={!isConnected}
              >
                <RefreshCw className="h-4 w-4" />
              </Button>
              <Button size="sm" variant="outline">
                <Settings className="h-4 w-4" />
              </Button>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-500">{filteredOpportunities.length}</p>
              <p className="text-sm text-muted-foreground">Active Opportunities</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-500">
                {filteredOpportunities.length > 0 ?
                  Math.max(...filteredOpportunities.map(o => o.edge)).toFixed(1) : '0.0'}%
              </p>
              <p className="text-sm text-muted-foreground">Max Edge</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-500">
                ${filteredOpportunities.reduce((sum, opp) => sum + opp.profit_potential, 0).toLocaleString()}
              </p>
              <p className="text-sm text-muted-foreground">Total Profit Potential</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-yellow-500">
                {filteredOpportunities.length > 0 ?
                  Math.min(...filteredOpportunities.map(o => o.time_window)) : 0}s
              </p>
              <p className="text-sm text-muted-foreground">Min Time Window</p>
            </div>
          </div>

          {/* Quick Filters */}
          <div className="flex items-center gap-2 text-sm">
            <Filter className="h-4 w-4 text-muted-foreground" />
            <span className="text-muted-foreground">Filters:</span>
            {settings.domains.map(domain => (
              <Badge key={domain} variant="outline" className="text-xs">
                {DOMAIN_ICONS[domain as keyof typeof DOMAIN_ICONS]} {domain.replace('_', ' ')}
              </Badge>
            ))}
            <Badge variant="outline" className="text-xs">
              Edge ≥ {settings.minEdge}%
            </Badge>
            <Badge variant="outline" className="text-xs">
              Confidence ≥ {(settings.minConfidence * 100).toFixed(0)}%
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Live Opportunities Stream */}
      <Card className="bg-card">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Target className="h-5 w-5 text-green-500" />
              Live Opportunities
              {filteredOpportunities.length > 0 && (
                <Badge className="bg-green-500 text-foreground">
                  {filteredOpportunities.length}
                </Badge>
              )}
            </div>
            <Button
              size="sm"
              variant={settings.autoRefresh ? "default" : "outline"}
              onClick={() => updateSettings({ autoRefresh: !settings.autoRefresh })}
            >
              Auto Refresh {settings.autoRefresh ? 'ON' : 'OFF'}
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <AnimatePresence>
            {filteredOpportunities.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground">
                <Target className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p className="text-lg mb-2">No opportunities match current filters</p>
                <p className="text-sm">Scanner is actively monitoring {settings.domains.length} domains...</p>
              </div>
            ) : (
              <div className="space-y-3">
                {filteredOpportunities.map((opportunity, index) => (
                  <motion.div
                    key={opportunity.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    transition={{ duration: 0.3, delay: index * 0.05 }}
                    className={`rounded-lg border p-4 ${DOMAIN_COLORS[opportunity.domain]} hover:scale-[1.02] transition-transform cursor-pointer`}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <div className="flex items-center gap-2">
                          {getOpportunityIcon(opportunity.type)}
                          <span className="font-semibold">{opportunity.entity}</span>
                        </div>
                        <Badge variant="outline" className="text-xs">
                          {DOMAIN_ICONS[opportunity.domain]} {opportunity.type.toUpperCase()}
                        </Badge>
                      </div>
                      <Badge className={getRiskColor(opportunity.risk_level)} variant="outline">
                        {opportunity.risk_level} RISK
                      </Badge>
                    </div>

                    <p className="text-sm text-muted-foreground mb-3">{opportunity.description}</p>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
                      <div>
                        <div className="flex items-center gap-1 mb-1">
                          <TrendingUp className="h-3 w-3 text-muted-foreground" />
                          <span className="text-xs text-muted-foreground">Edge</span>
                        </div>
                        <p className={`font-bold text-lg ${getEdgeColor(opportunity.edge)}`}>
                          {opportunity.edge.toFixed(1)}%
                        </p>
                      </div>
                      <div>
                        <div className="flex items-center gap-1 mb-1">
                          <Target className="h-3 w-3 text-muted-foreground" />
                          <span className="text-xs text-muted-foreground">Confidence</span>
                        </div>
                        <p className="font-bold text-lg">
                          {(opportunity.confidence * 100).toFixed(0)}%
                        </p>
                      </div>
                      <div>
                        <div className="flex items-center gap-1 mb-1">
                          <DollarSign className="h-3 w-3 text-muted-foreground" />
                          <span className="text-xs text-muted-foreground">Profit Potential</span>
                        </div>
                        <p className="font-bold text-lg text-green-500">
                          ${opportunity.profit_potential.toLocaleString()}
                        </p>
                      </div>
                      <div>
                        <div className="flex items-center gap-1 mb-1">
                          <Clock className="h-3 w-3 text-muted-foreground" />
                          <span className="text-xs text-muted-foreground">Time Window</span>
                        </div>
                        <p className="font-bold text-lg text-yellow-500">
                          {opportunity.time_window}s
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center justify-between pt-3 border-t border-gray-700/50">
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <span>Created {new Date(opportunity.timestamp).toLocaleTimeString()}</span>
                        {opportunity.status === 'active' && (
                          <Badge className="bg-green-500/20 text-green-500 border-green-500/30">
                            ACTIVE
                          </Badge>
                        )}
                      </div>
                      <div className="flex items-center gap-2">
                        <Button size="sm" variant="outline">
                          <Eye className="h-3 w-3 mr-1" />
                          Analyze
                        </Button>
                        <Button size="sm" variant="default" className="bg-green-600 hover:bg-green-700">
                          <ExternalLink className="h-3 w-3 mr-1" />
                          Execute
                        </Button>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </AnimatePresence>
        </CardContent>
      </Card>

      {/* Status Alerts */}
      {!isConnected && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            Opportunity Scanner is offline. Reconnecting...
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
}