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
  Lock,
  AlertTriangle,
  Gift,
  Zap,
  Award,
  ChevronRight,
  Clock,
  Star,
  AlertCircle,
  CheckCircle,
  Trash2
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
  score?: number;
  match_reasons?: string[];
  action_steps?: string[];
  // Real opportunity fields
  company?: string;
  url?: string;
  salary_range?: string;
  is_real?: boolean;
  is_mock?: boolean;
  value?: number;
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
  const [aiInsights, setAiInsights] = useState<any[]>([]);
  const [hasRealData, setHasRealData] = useState(false);

  const { sendMessage, lastMessage, isConnected } = useWebSocket({
    url: '/ws/decision-command/',
    onMessage: (data) => {
      console.log('Decision Command received from unified hub:', data);
      if (data.type === 'opportunities_analysis') {
        setOpportunities(data.top_opportunities || []);
        setProjections(data.earnings_projection || null);
        setLoading(false);
      } else if (data.type === 'decision_update') {
        // Handle decision updates - but don't overwrite real opportunities
        console.log('Decision updates:', data.decisions);
        if (data.decisions && data.decisions.length > 0 && !hasRealData) {
          // Only use mock data if we don't have real opportunities
          const convertedOpportunities = data.decisions.map((decision: any) => ({
            id: decision.id,
            title: decision.title,
            stream_type: decision.category || 'ai_automation',
            description: decision.description,
            time_to_income: decision.timeframe || '1-2 weeks',
            potential_monthly: decision.potential || '$1,000-$5,000',
            difficulty: decision.priority === 'high' ? 'beginner' : decision.priority === 'medium' ? 'intermediate' : 'advanced',
            success_probability: decision.confidence || 75,
            required_skills: decision.requirements || [],
            resources_needed: decision.resources || [],
            is_mock: true // Mark as mock data
          }));
          setOpportunities(convertedOpportunities);
          setLoading(false);
        }
        if (data.ai_insights) {
          // Store AI insights for display
          setAiInsights(data.ai_insights);
        }
      } else if (data.type === 'opportunities_data') {
        // Handle opportunities data from execution
        console.log('📊 Received opportunities data from execution:', data.data);

        if (data.data) {
          // Convert real opportunities to Decision Command format
          const realOpportunities = data.data.jobs?.map((job: any) => ({
            id: job.id || Math.random().toString(36).substr(2, 9),
            title: job.title,
            stream_type: 'employment',
            description: job.description?.substring(0, 200) + '...',
            company: job.company,
            url: job.url,
            source: job.source || 'Unknown', // Add source field
            time_to_income: job.salary_max > 100000 ? '2-4 weeks' : job.salary_max > 60000 ? '1-3 weeks' : '1-2 weeks',
            potential_monthly: `$${Math.floor((job.salary_max || 60000) / 12)}`,
            difficulty: job.salary_max > 100000 ? 'advanced' : job.salary_max > 60000 ? 'intermediate' : 'beginner',
            success_probability: job.salary_max > 100000 ? 60 : job.salary_max > 60000 ? 70 : 85,
            required_skills: job.tags || [],
            resources_needed: ['Resume', 'Portfolio'],
            salary_range: job.salary ? job.salary : `$${job.salary_min?.toLocaleString()}-$${job.salary_max?.toLocaleString()}`,
            score: (job.salary_max > 100000 ? 0.6 : job.salary_max > 60000 ? 0.7 : 0.85),
            is_real: true
          })) || [];

          // Add any created content as opportunities
          const contentOpportunities = data.data.content?.map((content: any) => ({
            id: content.id,
            title: content.title || 'Content for Sale',
            stream_type: 'content_sales',
            description: `${content.type} - ${content.word_count} words. Ready to list on marketplaces for immediate sale.`,
            time_to_income: 'Immediate',
            potential_monthly: `$${content.value}`,
            difficulty: 'beginner',
            success_probability: 90,
            required_skills: ['Content Marketing'],
            resources_needed: ['Sales Platform'],
            value: content.value,
            score: 0.9,
            is_real: true
          })) || [];

          const allOpportunities = [...realOpportunities, ...contentOpportunities];
          if (allOpportunities.length > 0) {
            console.log('✅ Setting real opportunities from WebSocket:', allOpportunities);
            setOpportunities(allOpportunities);
            setHasRealData(true);
            setLoading(false);
          }
        }
      } else if (data.type === 'connection') {
        console.log('Decision Command connected to bridge');
        setLoading(false);
      }
    },
    onOpen: () => {
      console.log('Decision Command connected to WebSocket');

      // Request initial data with action trigger to ensure we get data
      sendMessage({ type: 'get_data', component: 'decision_command' });
      sendMessage({ action: 'analyze_opportunities' });
      sendMessage({ type: 'get_opportunities' });
      console.log('📤 Sent data requests with action triggers on connection');
    }
  });

  useEffect(() => {
    // Load user opportunities on mount
    console.log('🚀 DecisionCommand mounting, fetching real opportunities...');
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

  const handleDeleteOpportunity = async (oppId: string, event: React.MouseEvent) => {
    event.stopPropagation(); // Prevent card selection

    console.log('🗑️ Deleting opportunity:', oppId);

    // Remove from local state immediately for UI responsiveness
    setOpportunities(prevOpps => prevOpps.filter(opp => opp.id !== oppId));

    // Clear selection if deleted item was selected
    if (selectedOpportunity?.id === oppId) {
      setSelectedOpportunity(null);
    }

    // Send delete message to backend via WebSocket
    sendMessage(JSON.stringify({
      action: 'delete_opportunity',
      opportunity_id: oppId
    }));

    // Also try to delete via API if it's a real opportunity
    try {
      const response = await fetch(`/api/opportunities/${oppId}/`, {
        method: 'DELETE',
      });

      if (response.ok) {
        console.log('✅ Opportunity deleted from backend');
      }
    } catch (error) {
      console.error('Error deleting opportunity from API:', error);
    }
  };

  const analyzeOpportunities = async () => {
    setLoading(true);
    setHasRealData(false); // Reset to allow new data
    setOpportunities([]); // Clear old opportunities
    console.log('🔍 analyzeOpportunities called - fetching from API...');

    // First try to fetch real opportunities from the API
    try {
      console.log('📡 Fetching from /api/opportunities/...');
      const response = await fetch('/api/opportunities/');
      console.log('📡 API Response status:', response.status);

      if (response.ok) {
        const data = await response.json();
        console.log('📡 API Response data:', data);

        if (data.success && data.data) {
          console.log('📊 Loaded real opportunities from API:', data.data);

          // Convert real opportunities to Decision Command format
          const realOpportunities = data.data.jobs?.map((job: any) => ({
            id: job.id || Math.random().toString(36).substr(2, 9),
            title: job.title,
            stream_type: 'employment',
            description: job.description?.substring(0, 200) + '...',
            company: job.company,
            url: job.url,
            source: job.source || 'Unknown', // Add source field
            time_to_income: job.salary_max > 100000 ? '2-4 weeks' : job.salary_max > 60000 ? '1-3 weeks' : '1-2 weeks',
            potential_monthly: `$${Math.floor((job.salary_max || 60000) / 12)}`,
            difficulty: job.salary_max > 100000 ? 'advanced' : job.salary_max > 60000 ? 'intermediate' : 'beginner',
            success_probability: job.salary_max > 100000 ? 60 : job.salary_max > 60000 ? 70 : 85,
            required_skills: job.tags || [],
            resources_needed: ['Resume', 'Portfolio'],
            salary_range: job.salary ? job.salary : `$${job.salary_min?.toLocaleString()}-$${job.salary_max?.toLocaleString()}`,
            score: (job.salary_max > 100000 ? 0.6 : job.salary_max > 60000 ? 0.7 : 0.85),
            is_real: true
          })) || [];

          // Add any created content as opportunities
          const contentOpportunities = data.data.content?.map((content: any) => ({
            id: content.id,
            title: content.title || 'Content for Sale',
            stream_type: 'content_sales',
            description: `${content.type} - ${content.word_count} words. Ready to list on marketplaces for immediate sale.`,
            time_to_income: 'Immediate',
            potential_monthly: `$${content.value}`,
            difficulty: 'beginner',
            success_probability: 90,
            required_skills: ['Content Marketing'],
            resources_needed: ['Sales Platform'],
            value: content.value,
            score: 0.9,
            is_real: true
          })) || [];

          const allOpportunities = [...realOpportunities, ...contentOpportunities];
          if (allOpportunities.length > 0) {
            console.log('✅ Setting real opportunities:', allOpportunities);
            setOpportunities(allOpportunities);
            setHasRealData(true);
            setLoading(false);
            return;
          }
        }
      }
    } catch (error) {
      console.error('Error fetching real opportunities:', error);
    }

    // Fallback to WebSocket request
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
          {(activeMode === 'income' || activeMode === 'both') && (
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
                              {opp.is_real && <Badge className="bg-green-600 text-white">REAL</Badge>}
                              <Badge
                                className={`${getDifficultyColor(opp.difficulty)} text-white`}
                              >
                                {opp.difficulty}
                              </Badge>
                            </div>

                            {opp.company && (
                              <p className="text-sm text-gray-500 mt-1">at {opp.company}</p>
                            )}

                            {opp.salary_range && (
                              <p className="text-sm font-semibold text-green-600 mt-1">{opp.salary_range}/year</p>
                            )}

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
                                <span className="text-gray-500">Success Rate</span>
                                <p className="font-medium">{opp.success_probability || 75}%</p>
                              </div>
                            </div>

                            {opp.required_skills && opp.required_skills.length > 0 && (
                              <div className="mt-3">
                                <p className="text-sm text-gray-600 mb-1">Required Skills:</p>
                                <div className="flex flex-wrap gap-1">
                                  {opp.required_skills.map((skill, i) => (
                                    <Badge key={i} variant="outline" className="text-xs">
                                      <CheckCircle className="w-3 h-3 mr-1" />
                                      {skill}
                                    </Badge>
                                  ))}
                                </div>
                              </div>
                            )}

                            {selectedOpportunity?.id === opp.id && (
                              <motion.div
                                initial={{ height: 0, opacity: 0 }}
                                animate={{ height: 'auto', opacity: 1 }}
                                className="mt-4 pt-4 border-t"
                              >
                                <h4 className="font-medium mb-2">Quick Start Steps:</h4>
                                <ol className="space-y-1">
                                  {(opp.action_steps || ['View opportunity', 'Prepare application', 'Submit']).slice(0, 3).map((step, i) => (
                                    <li key={i} className="text-sm flex items-start gap-2">
                                      <span className="font-medium text-purple-600">
                                        {i + 1}.
                                      </span>
                                      <span>{step}</span>
                                    </li>
                                  ))}
                                </ol>
                                <Button
                                  className="mt-3 w-full"
                                  size="sm"
                                  onClick={() => {
                                    if (opp.url) {
                                      // Open real job URL in new tab
                                      window.open(opp.url, '_blank');
                                    } else if (opp.stream_type === 'content_sales') {
                                      // Navigate to Revenue Dashboard to list content
                                      console.log('📝 Navigating to list content:', opp.title);
                                      window.location.href = '/revenue-dashboard';
                                    } else {
                                      console.log('Starting opportunity:', opp.title);
                                    }
                                  }}
                                >
                                  {opp.url ? 'Apply Now' : opp.stream_type === 'content_sales' ? 'List for Sale' : 'Start This Opportunity'}
                                  <ChevronRight className="w-4 h-4 ml-1" />
                                </Button>
                              </motion.div>
                            )}
                          </div>

                          <div className="ml-4 flex items-start gap-2">
                            <Button
                              variant="ghost"
                              size="icon"
                              className="text-red-500 hover:bg-red-50"
                              onClick={(e) => handleDeleteOpportunity(opp.id, e)}
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
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
                                  strokeDasharray={`${(opp.score || 0.75) * 176} 176`}
                                  className="text-purple-600"
                                />
                              </svg>
                              <div className="absolute inset-0 flex items-center justify-center">
                                <span className="text-sm font-bold">
                                  {((opp.score || 0.75) * 100).toFixed(0)}%
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
          )}

          {/* Success Path Timeline - show in all modes */}
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

      {/* Investment Mode */}
      {(activeMode === 'invest' || activeMode === 'both') && (
        <Card>
          <CardHeader>
            <CardTitle>Investment Opportunities</CardTitle>
            <p className="text-sm text-gray-600">
              {userProfile.current_balance > 0
                ? "Now that you have capital, let's make it grow"
                : "Start learning about investing while you build your income"
              }
            </p>
          </CardHeader>
          <CardContent>
            {userProfile.current_balance > 0 ? (
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
            ) : (
              <div className="space-y-4">
                <Alert className="border-yellow-200 bg-yellow-50">
                  <AlertTriangle className="w-4 h-4" />
                  <AlertDescription>
                    <strong>Build income first!</strong> Start earning with the opportunities above,
                    then unlock investment features once you have capital to invest.
                  </AlertDescription>
                </Alert>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 opacity-50">
                  <Card className="border-gray-200">
                    <CardContent className="p-4">
                      <Lock className="w-5 h-5 mb-2 text-gray-400" />
                      <h3 className="font-semibold text-gray-600">Stocks & ETFs</h3>
                      <p className="text-sm text-gray-500 mt-1">
                        Unlocks at $100+ balance
                      </p>
                    </CardContent>
                  </Card>
                  <Card className="border-gray-200">
                    <CardContent className="p-4">
                      <Lock className="w-5 h-5 mb-2 text-gray-400" />
                      <h3 className="font-semibold text-gray-600">Crypto DCA</h3>
                      <p className="text-sm text-gray-500 mt-1">
                        Unlocks at $50+ balance
                      </p>
                    </CardContent>
                  </Card>
                  <Card className="border-gray-200">
                    <CardContent className="p-4">
                      <Lock className="w-5 h-5 mb-2 text-gray-400" />
                      <h3 className="font-semibold text-gray-600">AI Trading</h3>
                      <p className="text-sm text-gray-500 mt-1">
                        Unlocks at $500+ balance
                      </p>
                    </CardContent>
                  </Card>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default DecisionCommand;