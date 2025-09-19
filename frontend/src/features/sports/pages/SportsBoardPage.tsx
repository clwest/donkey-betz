/**
 * Enhanced Sports Board Page - Multi-Sport Support
 * 
 * Now supporting ALL major sports with real data from:
 * - ESPN Hidden API (free, comprehensive)
 * - TheSportsDB.com (free, community-driven) 
 * - The Odds API (free tier for betting odds)
 * 
 * Supports: NFL, NBA, MLB, NHL, Soccer, MMA, Tennis, Golf, Boxing, College Football,
 * College Basketball, and more!
 */

import { useState, useEffect } from 'react';
import { Card } from '../../../components/common/Card';
import { Button } from '../../../components/common/Button';
import { Badge } from '../../../components/common/Badge';
import { toast } from 'sonner';
import { 
  ArrowLeft, 
  TrendingUp, 
  Activity, 
  Calendar, 
  Star,
  Zap,
  RefreshCw
} from 'lucide-react';
import MultiSportsDashboard from '../components/MultiSportsDashboard';

export function SportsBoardPage() {
  const [view, setView] = useState<'modern' | 'features'>('modern');

  // Add gaming theme to body
  useEffect(() => {
    document.body.classList.add('bg-card');
    return () => {
      document.body.classList.remove('bg-card');
    };
  }, []);

  const renderFeaturesInfo = () => (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold text-gradient">
          🎯 DONKEY BETZ COMMAND CENTER
        </h1>
        <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
          Real-time sports data and betting odds across all major leagues - 
          powered by free, open-source APIs as a complete replacement for Polygon.io
        </p>
      </div>

      {/* Data Sources */}
      <Card>
        <div className="p-6 border-b border-border">
          <div className="flex items-center space-x-2">
            <Zap className="w-5 h-5 text-yellow-500" />
            <span className="text-lg font-semibold text-foreground">Free Data Sources</span>
          </div>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <Badge variant="secondary">ESPN Hidden API</Badge>
                <span className="text-green-500 text-sm font-medium">FREE</span>
              </div>
              <p className="text-sm text-muted-foreground">
                Comprehensive sports data including scores, schedules, team info, and live game data
              </p>
              <div className="text-xs text-muted-foreground">
                • NFL, NBA, MLB, NHL, College Sports<br/>
                • Soccer, Tennis, Golf<br/>
                • Live scores and schedules
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <Badge variant="secondary">TheSportsDB</Badge>
                <span className="text-green-500 text-sm font-medium">FREE</span>
              </div>
              <p className="text-sm text-muted-foreground">
                Community-driven sports database with extensive historical data and team information
              </p>
              <div className="text-xs text-muted-foreground">
                • Team logos and info<br/>
                • Historical statistics<br/>
                • League structures
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <Badge variant="secondary">The Odds API</Badge>
                <span className="text-blue-500 text-sm font-medium">FREE TIER</span>
              </div>
              <p className="text-sm text-muted-foreground">
                Live betting odds from major sportsbooks for optimal betting opportunities
              </p>
              <div className="text-xs text-muted-foreground">
                • Moneylines, spreads, totals<br/>
                • Multiple sportsbooks<br/>
                • Real-time odds updates
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Supported Sports */}
      <Card>
        <div className="p-6 border-b border-border">
          <div className="flex items-center space-x-2">
            <Star className="w-5 h-5 text-purple-400" />
            <span className="text-lg font-semibold text-foreground">Supported Sports</span>
          </div>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {[
              { sport: 'NFL', emoji: '🏈', desc: 'National Football League' },
              { sport: 'NBA', emoji: '🏀', desc: 'National Basketball Assoc.' },
              { sport: 'MLB', emoji: '⚾', desc: 'Major League Baseball' },
              { sport: 'NHL', emoji: '🏒', desc: 'National Hockey League' },
              { sport: 'NCAAF', emoji: '🏈', desc: 'College Football' },
              { sport: 'NCAAB', emoji: '🏀', desc: 'College Basketball' },
              { sport: 'Soccer', emoji: '⚽', desc: 'Premier League, MLS' },
              { sport: 'MMA', emoji: '🥊', desc: 'Mixed Martial Arts' },
              { sport: 'Tennis', emoji: '🎾', desc: 'ATP/WTA Tours' },
              { sport: 'Golf', emoji: '⛳', desc: 'PGA Tour' },
              { sport: 'Boxing', emoji: '🥊', desc: 'Professional Boxing' },
              { sport: 'Esports', emoji: '🎮', desc: 'Competitive Gaming' },
            ].map((item, index) => (
              <div key={index} className="text-center p-3 rounded-lg border border-border hover:border-primary-500/50 transition-colors">
                <div className="text-2xl mb-1">{item.emoji}</div>
                <div className="font-medium text-sm text-foreground">{item.sport}</div>
                <div className="text-xs text-muted-foreground">{item.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </Card>

      {/* Features */}
      <Card>
        <div className="p-6 border-b border-border">
          <div className="flex items-center space-x-2">
            <Activity className="w-5 h-5 text-green-500" />
            <span className="text-lg font-semibold text-foreground">Key Features</span>
          </div>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h4 className="font-semibold text-foreground">Live Sports Data</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>• Real-time scores and game status</li>
                <li>• Live betting odds from multiple books</li>
                <li>• Automatic data synchronization</li>
                <li>• Weather data for outdoor sports</li>
              </ul>
            </div>
            
            <div className="space-y-4">
              <h4 className="font-semibold text-foreground">Advanced Analytics</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>• Kelly Criterion bet sizing</li>
                <li>• Expected value calculations</li>
                <li>• Arbitrage opportunity detection</li>
                <li>• Bankroll management tools</li>
              </ul>
            </div>

            <div className="space-y-4">
              <h4 className="font-semibold text-foreground">Multi-Sport Coverage</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>• All major US professional leagues</li>
                <li>• College football and basketball</li>
                <li>• International soccer leagues</li>
                <li>• Combat sports (MMA, Boxing)</li>
              </ul>
            </div>

            <div className="space-y-4">
              <h4 className="font-semibold text-foreground">Free Data Sources</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>• No expensive API subscriptions</li>
                <li>• Open-source and community-driven</li>
                <li>• Reliable backup providers</li>
                <li>• Automatic failover system</li>
              </ul>
            </div>
          </div>
        </div>
      </Card>

      {/* Get Started */}
      <Card className="border-green-500/30 bg-green-500/10">
        <div className="p-6">
          <div className="text-center space-y-4">
            <h3 className="text-lg font-semibold text-green-300">
              Ready to explore multi-sport betting?
            </h3>
            <p className="text-green-500">
              Access real-time data across all major sports leagues with no subscription fees
            </p>
            <Button 
              onClick={() => setView('modern')}
              variant="primary"
            >
              <Activity className="w-4 h-4 mr-2" />
              Launch Sports Dashboard
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );

  return (
    <div className="space-y-6">
        {view === 'features' ? (
          <>
            {/* Back Button */}
            <div className="mb-6">
              <Button
                variant="ghost"
                onClick={() => setView('modern')}
                className="mb-4"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Dashboard
              </Button>
            </div>

            {renderFeaturesInfo()}
          </>
        ) : (
          <>
            {/* Gaming Header */}
            <div className="bg-card relative overflow-hidden mb-8">
              <div className="bg-card"></div>
              
              {/* Cyberpunk background pattern */}
              <div className="absolute inset-0 opacity-10">
                <div className="w-full h-full" style={{backgroundImage: 'linear-gradient(45deg, transparent 40%, hsl(var(--muted)) 50%, transparent 60%)', backgroundSize: '20px 20px'}}></div>
              </div>
              
              <div className="relative flex items-center justify-between p-8">
                <div className="space-y-4">
                  <div className="flex items-center gap-4">
                    <div className="w-16 h-16 bg-card border-bg-card flex items-center justify-center">
                      <Activity className="w-8 h-8 bg-card" />
                    </div>
                    <h1 className="text-5xl font-black bg-card text-shadow-lg">
                      SPORTS <span className="bg-card">BETTING</span> HUB
                    </h1>
                  </div>
                  
                  <p className="bg-card text-xl font-bold font-mono">
                    [MULTI-SPORT ARENA] &gt;&gt; FREE OPEN-SOURCE APIs
                  </p>
                  
                  {/* Gaming Data Sources Indicators */}
                  <div className="flex items-center gap-4">
                    <div className="bg-card bg-card">
                      <Zap className="w-4 h-4" />
                      ESPN API
                      <div className="bg-card"></div>
                    </div>
                    
                    <div className="bg-card bg-bg-card/20 border-bg-card text-bg-card">
                      <Star className="w-4 h-4" />
                      THESPORTSDB
                    </div>
                    
                    <div className="bg-card bg-bg-card/20 border-bg-card text-bg-card">
                      <TrendingUp className="w-4 h-4" />
                      ODDS API
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center gap-4">
                  <Button
                    variant="outline"
                    onClick={() => setView('features')}
                    className="bg-card px-6 py-3 text-lg"
                  >
                    <Star className="w-5 h-5 mr-3" />
                    FEATURES & INFO
                  </Button>
                </div>
              </div>
            </div>

            {/* Multi-Sport Dashboard */}
            <MultiSportsDashboard />
          </>
        )}
      </div>
    );
}