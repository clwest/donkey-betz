/**
 * Decision Command Center - Enhanced UI
 *
 * Primary command interface for all AI-powered decision making, including
 * the new AI Income Builder for users starting from $0.
 */

import React, { useState, useEffect } from 'react';
import {
  Brain,
  TrendingUp,
  DollarSign,
  Rocket,
  Users,
  Target,
  BookOpen,
  Briefcase,
  Code,
  PenTool,
  Video,
  Gift,
  Zap,
  Award,
  ChevronRight,
  Clock,
  Star,
  AlertCircle,
  CheckCircle
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useWebSocket } from '@/hooks/useWebSocket';
import { motion, AnimatePresence } from 'framer-motion';

interface IncomeOpportunity {
  id: string;
  title: string;
  stream_type: string;
  potential_monthly: string;
  time_to_income: string;
  difficulty: string;
  score: number;
  match_reasons: string[];
  action_steps: string[];
}

interface UserProfile {
  current_balance: number;
  skill_level: string;
  available_hours: number;
  active_streams: string[];
  total_earned: number;
}

interface EarningsProjection {
  week_1: number;
  month_1: number;
  month_3: number;
  month_6: number;
  year_1: number;
}

const DecisionCommand: React.FC = () => {
  const [activeMode, setActiveMode] = useState<'income' | 'invest' | 'both'>('income');
  const [userProfile, setUserProfile] = useState<UserProfile>({
    current_balance: 0,
    skill_level: 'beginner',
    available_hours: 10,
    active_streams: [],
    total_earned: 0
  });
  const [opportunities, setOpportunities] = useState<IncomeOpportunity[]>([]);
  const [selectedOpportunity, setSelectedOpportunity] = useState<IncomeOpportunity | null>(null);
  const [projections, setProjections] = useState<EarningsProjection | null>(null);
  const [loading, setLoading] = useState(false);

  const { sendMessage, lastMessage } = useWebSocket({
    url: '/ws/decision/',
    onMessage: (data) => {
      console.log('Decision Command received:', data);
      if (data.type === 'opportunities_analysis') {
        setOpportunities(data.top_opportunities || []);
        setProjections(data.earnings_projection || null);
      }
    }
  });

  useEffect(() => {
    // Load user opportunities on mount
    analyzeOpportunities();
  }, []);

  useEffect(() => {
    if (lastMessage) {
      try {
        const data = typeof lastMessage === 'string' ? JSON.parse(lastMessage) : lastMessage;
        if (data.type === 'opportunities_analysis') {
          setOpportunities(data.top_opportunities || []);
          setProjections(data.earnings_projection || null);
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    }
  }, [lastMessage]);

  const analyzeOpportunities = async () => {
    setLoading(true);
    sendMessage(JSON.stringify({
      action: 'analyze_opportunities',
      profile: userProfile
    }));
    setLoading(false);
  };

  const getIconForStream = (streamType: string) => {
    const icons: { [key: string]: React.ReactNode } = {
      'content_creation': <PenTool className="w-5 h-5" />,
      'freelance_services': <Briefcase className="w-5 h-5" />,
      'ai_automation': <Zap className="w-5 h-5" />,
      'digital_products': <Gift className="w-5 h-5" />,
      'consulting': <Users className="w-5 h-5" />,
      'prompt_engineering': <Code className="w-5 h-5" />,
      'ai_tutoring': <BookOpen className="w-5 h-5" />,
      'micro_saas': <Rocket className="w-5 h-5" />
    };
    return icons[streamType] || <DollarSign className="w-5 h-5" />;
  };

  const getDifficultyColor = (difficulty: string) => {
    const colors: { [key: string]: string } = {
      'beginner': 'bg-green-500',
      'intermediate': 'bg-yellow-500',
      'advanced': 'bg-orange-500',
      'expert': 'bg-red-500'
    };
    return colors[difficulty] || 'bg-gray-500';
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Brain className="w-8 h-8 text-purple-600" />
            Decision Command Center
          </h1>
          <p className="text-gray-600 mt-1">
            Your AI-powered path from $0 to financial freedom
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant={activeMode === 'income' ? 'default' : 'outline'}
            onClick={() => setActiveMode('income')}
          >
            Build Income
          </Button>
          <Button
            variant={activeMode === 'invest' ? 'default' : 'outline'}
            onClick={() => setActiveMode('invest')}
          >
            Invest & Trade
          </Button>
          <Button
            variant={activeMode === 'both' ? 'default' : 'outline'}
            onClick={() => setActiveMode('both')}
          >
            Both
          </Button>
        </div>
      </div>

      {/* Zero to Hero Alert */}
      {userProfile.current_balance === 0 && (
        <Alert className="border-purple-200 bg-purple-50">
          <Rocket className="w-4 h-4" />
          <AlertDescription>
            <strong>Zero to Hero Mode Active!</strong> We've identified opportunities
            that require $0 investment. You can start earning today with just your time and effort.
          </AlertDescription>
        </Alert>
      )}

      {/* Main Dashboard */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Profile & Stats */}
        <div className="space-y-4">
          {/* User Profile Card */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Your Profile</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Current Balance</span>
                <span className="font-bold text-lg">${userProfile.current_balance}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Total Earned</span>
                <span className="font-bold text-green-600">
                  ${userProfile.total_earned}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Skill Level</span>
                <Badge>{userProfile.skill_level}</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Hours/Week</span>
                <span>{userProfile.available_hours}h</span>
              </div>
              {userProfile.active_streams.length > 0 && (
                <div>
                  <span className="text-sm text-gray-600">Active Streams</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {userProfile.active_streams.map(stream => (
                      <Badge key={stream} variant="secondary" className="text-xs">
                        {stream}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Earnings Projection */}
          {projections && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-green-600" />
                  Earnings Projection
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Week 1</span>
                    <span className="font-medium">${projections.week_1}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Month 1</span>
                    <span className="font-medium">${projections.month_1}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Month 3</span>
                    <span className="font-medium text-green-600">
                      ${projections.month_3}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Month 6</span>
                    <span className="font-bold text-green-600">
                      ${projections.month_6}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm border-t pt-2">
                    <span>Year 1</span>
                    <span className="font-bold text-lg text-green-600">
                      ${projections.year_1}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Middle Column - Opportunities */}
        <div className="lg:col-span-2 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>AI-Matched Opportunities</CardTitle>
              <p className="text-sm text-gray-600">
                Personalized income streams based on your profile
              </p>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {opportunities.map((opp, index) => (
                  <motion.div
                    key={opp.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                  >
                    <Card
                      className={`cursor-pointer transition-all hover:shadow-lg ${
                        selectedOpportunity?.id === opp.id ? 'ring-2 ring-purple-500' : ''
                      }`}
                      onClick={() => setSelectedOpportunity(opp)}
                    >
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              {getIconForStream(opp.stream_type)}
                              <h3 className="font-semibold">{opp.title}</h3>
                              <Badge
                                className={`${getDifficultyColor(opp.difficulty)} text-white`}
                              >
                                {opp.difficulty}
                              </Badge>
                            </div>

                            <div className="mt-2 grid grid-cols-3 gap-4 text-sm">
                              <div>
                                <span className="text-gray-500">Potential</span>
                                <p className="font-medium">{opp.potential_monthly}/mo</p>
                              </div>
                              <div>
                                <span className="text-gray-500">Time to Income</span>
                                <p className="font-medium">{opp.time_to_income}</p>
                              </div>
                              <div>
                                <span className="text-gray-500">Match Score</span>
                                <p className="font-medium">{(opp.score * 100).toFixed(0)}%</p>
                              </div>
                            </div>

                            <div className="mt-3">
                              <p className="text-sm text-gray-600 mb-1">Why this matches:</p>
                              <div className="flex flex-wrap gap-1">
                                {opp.match_reasons.map((reason, i) => (
                                  <Badge key={i} variant="outline" className="text-xs">
                                    <CheckCircle className="w-3 h-3 mr-1" />
                                    {reason}
                                  </Badge>
                                ))}
                              </div>
                            </div>

                            {selectedOpportunity?.id === opp.id && (
                              <motion.div
                                initial={{ height: 0, opacity: 0 }}
                                animate={{ height: 'auto', opacity: 1 }}
                                className="mt-4 pt-4 border-t"
                              >
                                <h4 className="font-medium mb-2">Quick Start Steps:</h4>
                                <ol className="space-y-1">
                                  {opp.action_steps.slice(0, 3).map((step, i) => (
                                    <li key={i} className="text-sm flex items-start gap-2">
                                      <span className="font-medium text-purple-600">
                                        {i + 1}.
                                      </span>
                                      <span>{step}</span>
                                    </li>
                                  ))}
                                </ol>
                                <Button className="mt-3 w-full" size="sm">
                                  Start This Opportunity
                                  <ChevronRight className="w-4 h-4 ml-1" />
                                </Button>
                              </motion.div>
                            )}
                          </div>

                          <div className="ml-4">
                            <div className="relative w-16 h-16">
                              <svg className="w-16 h-16 transform -rotate-90">
                                <circle
                                  cx="32"
                                  cy="32"
                                  r="28"
                                  stroke="currentColor"
                                  strokeWidth="4"
                                  fill="none"
                                  className="text-gray-200"
                                />
                                <circle
                                  cx="32"
                                  cy="32"
                                  r="28"
                                  stroke="currentColor"
                                  strokeWidth="4"
                                  fill="none"
                                  strokeDasharray={`${opp.score * 176} 176`}
                                  className="text-purple-600"
                                />
                              </svg>
                              <div className="absolute inset-0 flex items-center justify-center">
                                <span className="text-sm font-bold">
                                  {(opp.score * 100).toFixed(0)}%
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                ))}
              </div>

              {opportunities.length === 0 && !loading && (
                <div className="text-center py-8">
                  <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                  <p className="text-gray-600">
                    Click "Analyze Opportunities" to get personalized recommendations
                  </p>
                  <Button onClick={analyzeOpportunities} className="mt-3">
                    Analyze Opportunities
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Success Path Timeline */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="w-5 h-5" />
                Your Success Path
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="relative">
                <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-200"></div>
                <div className="space-y-6">
                  {[
                    {
                      week: 'Week 1',
                      title: 'Quick Start',
                      tasks: ['Set up accounts', 'Build portfolio', 'First applications'],
                      expected: 'First responses'
                    },
                    {
                      week: 'Month 1',
                      title: 'Build Foundation',
                      tasks: ['Complete first project', 'Get testimonials', 'Refine offering'],
                      expected: '$100-500 earned'
                    },
                    {
                      week: 'Month 2-3',
                      title: 'Scale Up',
                      tasks: ['Raise rates 20%', 'Add income stream', 'Automate tasks'],
                      expected: '$500-1500/month'
                    },
                    {
                      week: 'Month 4-6',
                      title: 'Optimize',
                      tasks: ['Premium services', 'Digital products', 'Build audience'],
                      expected: '$1500-3000/month'
                    }
                  ].map((phase, index) => (
                    <div key={index} className="relative flex items-start gap-4">
                      <div className={`
                        w-16 h-16 rounded-full flex items-center justify-center
                        ${index === 0 ? 'bg-purple-600 text-white' : 'bg-gray-100'}
                      `}>
                        <Clock className="w-6 h-6" />
                      </div>
                      <div className="flex-1">
                        <h4 className="font-semibold">{phase.week}: {phase.title}</h4>
                        <ul className="mt-1 space-y-1">
                          {phase.tasks.map((task, i) => (
                            <li key={i} className="text-sm text-gray-600">
                              • {task}
                            </li>
                          ))}
                        </ul>
                        <Badge variant="outline" className="mt-2">
                          {phase.expected}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Investment Mode (when balance > 0) */}
      {(activeMode === 'invest' || activeMode === 'both') && userProfile.current_balance > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Investment Opportunities</CardTitle>
            <p className="text-sm text-gray-600">
              Now that you have capital, let's make it grow
            </p>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card className="border-green-200">
                <CardContent className="p-4">
                  <h3 className="font-semibold">Stocks & ETFs</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    Start with index funds, minimal risk
                  </p>
                  <Button size="sm" className="mt-3 w-full">
                    Explore Stocks
                  </Button>
                </CardContent>
              </Card>
              <Card className="border-blue-200">
                <CardContent className="p-4">
                  <h3 className="font-semibold">Crypto DCA</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    Dollar-cost average into BTC/ETH
                  </p>
                  <Button size="sm" className="mt-3 w-full">
                    Start DCA
                  </Button>
                </CardContent>
              </Card>
              <Card className="border-purple-200">
                <CardContent className="p-4">
                  <h3 className="font-semibold">AI Trading</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    Let AI manage a portion of portfolio
                  </p>
                  <Button size="sm" className="mt-3 w-full">
                    Enable AI Trading
                  </Button>
                </CardContent>
              </Card>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default DecisionCommand;