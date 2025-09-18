import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Brain,
  Briefcase,
  FileText,
  CheckCircle,
  Clock,
  DollarSign,
  TrendingUp,
  Sparkles,
  Eye,
  Download,
  Target,
  Zap,
  Users,
  Activity,
  Bot
} from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

interface AIJob {
  id: string;
  title: string;
  platform: string;
  category: string;
  ai_score: number;
  success_probability: number;
  budget: number;
  estimated_hours: number;
  ai_tools: string[];
  status: 'new' | 'analyzed' | 'applied' | 'responded' | 'won';
  timestamp: string;
}

interface SpiderStatus {
  name: string;
  active: boolean;
  data_collected: number;
  last_update: string;
  category: string;
}

const AIJobTracker: React.FC = () => {
  const [jobs, setJobs] = useState<AIJob[]>([]);
  const [spiders, setSpiders] = useState<SpiderStatus[]>([]);
  const [stats, setStats] = useState({
    total_analyzed: 0,
    ai_suitable: 0,
    applications_sent: 0,
    potential_revenue: 0,
    avg_ai_score: 0,
    active_spiders: 0
  });
  const [loading, setLoading] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  // Load real data from API
  useEffect(() => {
    loadSpiderData();
    loadJobData();
  }, []);

  const loadSpiderData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/v1/intelligence/ai-jobs/spiders/`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (data.success && data.spiders) {
        setSpiders(data.spiders);
        setStats(prev => ({
          ...prev,
          active_spiders: data.active_spiders || data.spiders.filter(s => s.active).length
        }));
        console.log('✅ Loaded spider data from API:', data.spiders.length, 'spiders');
      } else {
        console.warn('⚠️ API returned unsuccessful response, using fallback data');
        loadFallbackSpiderData();
      }
    } catch (error) {
      console.error('❌ Error loading spider data:', error);
      loadFallbackSpiderData();
    } finally {
      setLoading(false);
    }
  };

  const loadJobData = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/intelligence/ai-jobs/jobs/`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (data.success && data.jobs) {
        setJobs(data.jobs);

        // Calculate stats from real job data
        const avgScore = data.jobs.length > 0
          ? data.jobs.reduce((sum, j) => sum + j.ai_score, 0) / data.jobs.length
          : 0;
        const potentialRevenue = data.jobs.reduce((sum, j) => sum + (j.budget || 0), 0);

        setStats(prev => ({
          ...prev,
          total_analyzed: data.jobs.length,
          ai_suitable: data.jobs.filter(j => j.ai_score > 0.7).length,
          applications_sent: data.jobs.filter(j => j.status === 'applied').length,
          potential_revenue: potentialRevenue,
          avg_ai_score: avgScore
        }));

        console.log('✅ Loaded job data from API:', data.jobs.length, 'jobs');
      } else {
        console.warn('⚠️ API returned unsuccessful response for jobs, using fallback data');
        loadFallbackJobData();
      }
    } catch (error) {
      console.error('❌ Error loading job data:', error);
      loadFallbackJobData();
    }
  };

  const loadFallbackSpiderData = () => {
    const fallbackSpiders: SpiderStatus[] = [
      { name: 'Financial Spider', active: true, data_collected: 156, last_update: '2 min ago', category: 'market' },
      { name: 'Guru Spider', active: true, data_collected: 89, last_update: '5 min ago', category: 'freelance' },
      { name: 'Toptal Spider', active: true, data_collected: 45, last_update: '8 min ago', category: 'freelance' },
      { name: 'RemoteOK Spider', active: true, data_collected: 112, last_update: '3 min ago', category: 'remote' },
      { name: 'Medium Spider', active: true, data_collected: 234, last_update: '1 min ago', category: 'content' },
      { name: 'Gumroad Spider', active: true, data_collected: 67, last_update: '12 min ago', category: 'products' },
      { name: 'News Harvester', active: true, data_collected: 445, last_update: 'just now', category: 'news' },
      { name: 'Market Data Spider', active: true, data_collected: 892, last_update: '30 sec ago', category: 'crypto' },
      { name: 'Innovation Spider', active: false, data_collected: 23, last_update: '1 hour ago', category: 'tech' },
      { name: 'Social Sentiment', active: true, data_collected: 567, last_update: '4 min ago', category: 'social' },
      { name: 'FlexJobs Spider', active: true, data_collected: 78, last_update: '6 min ago', category: 'remote' },
      { name: 'PeoplePerHour Spider', active: true, data_collected: 34, last_update: '15 min ago', category: 'freelance' },
      { name: '99Designs Spider', active: true, data_collected: 12, last_update: '20 min ago', category: 'design' },
    ];
    setSpiders(fallbackSpiders);
    setStats(prev => ({
      ...prev,
      active_spiders: fallbackSpiders.filter(s => s.active).length
    }));
    console.log('📋 Using fallback spider data');
  };

  const loadFallbackJobData = () => {
    const fallbackJobs: AIJob[] = [
      {
        id: 'job_001',
        title: 'AI Content Writer for Tech Blog',
        platform: 'Guru',
        category: 'content_writing',
        ai_score: 0.95,
        success_probability: 0.88,
        budget: 500,
        estimated_hours: 2,
        ai_tools: ['ChatGPT', 'Claude', 'Jasper'],
        status: 'applied',
        timestamp: new Date().toISOString()
      },
      {
        id: 'job_002',
        title: 'Python Data Analysis Automation',
        platform: 'Toptal',
        category: 'data_analysis',
        ai_score: 0.92,
        success_probability: 0.75,
        budget: 1500,
        estimated_hours: 5,
        ai_tools: ['Python', 'Pandas', 'ChatGPT'],
        status: 'analyzed',
        timestamp: new Date().toISOString()
      },
      {
        id: 'job_003',
        title: 'Chatbot Development with AI',
        platform: 'RemoteOK',
        category: 'code_generation',
        ai_score: 0.88,
        success_probability: 0.82,
        budget: 2500,
        estimated_hours: 8,
        ai_tools: ['ChatGPT API', 'Dialogflow', 'Python'],
        status: 'new',
        timestamp: new Date().toISOString()
      }
    ];
    setJobs(fallbackJobs);

    // Calculate stats from fallback data
    const avgScore = fallbackJobs.reduce((sum, j) => sum + j.ai_score, 0) / fallbackJobs.length;
    const potentialRevenue = fallbackJobs.reduce((sum, j) => sum + j.budget, 0);

    setStats(prev => ({
      ...prev,
      total_analyzed: fallbackJobs.length,
      ai_suitable: fallbackJobs.filter(j => j.ai_score > 0.7).length,
      applications_sent: fallbackJobs.filter(j => j.status === 'applied').length,
      potential_revenue: potentialRevenue,
      avg_ai_score: avgScore
    }));
    console.log('📋 Using fallback job data');
  };

  const activateAllSpiders = async () => {
    try {
      setLoading(true);
      console.log('🚀 Activating all spiders...');

      const response = await fetch(`${API_BASE_URL}/api/v1/intelligence/ai-jobs/start-spiders/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({})
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (data.success) {
        console.log('✅ Spiders activated successfully:', data.activated_spiders?.length || 0, 'spiders');

        // Refresh spider data after activation
        setTimeout(() => {
          loadSpiderData();
          loadJobData();
        }, 1000);

        return { success: true, message: data.message };
      } else {
        throw new Error(data.error || 'Failed to activate spiders');
      }
    } catch (error) {
      console.error('❌ Error activating spiders:', error);
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const applyToJob = async (jobId: string) => {
    try {
      setLoading(true);
      console.log('📝 Applying to job:', jobId);

      const response = await fetch(`${API_BASE_URL}/api/v1/intelligence/ai-jobs/apply/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ job_id: jobId })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (data.success) {
        console.log('✅ Application submitted successfully:', data.application_id);

        // Update job status to 'applied'
        setJobs(prev => prev.map(job =>
          job.id === jobId ? { ...job, status: 'applied' } : job
        ));

        // Update stats
        setStats(prev => ({
          ...prev,
          applications_sent: prev.applications_sent + 1
        }));

        return { success: true, applicationId: data.application_id };
      } else {
        throw new Error(data.error || 'Failed to submit application');
      }
    } catch (error) {
      console.error('❌ Error applying to job:', error);
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  // WebSocket connection for real-time updates
  useEffect(() => {
    const connectWebSocket = () => {
      const ws = new WebSocket(`${WS_BASE_URL}/ws/ai-jobs/`);

      ws.onopen = () => {
        console.log('AI Jobs WebSocket connected');
        setWsConnected(true);
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === 'new_job') {
          setJobs(prev => [data.job, ...prev].slice(0, 20)); // Keep last 20 jobs
        } else if (data.type === 'spider_update') {
          setSpiders(prev => prev.map(s =>
            s.name === data.spider.name ? data.spider : s
          ));
        } else if (data.type === 'stats_update') {
          setStats(data.stats);
        }
      };

      ws.onclose = () => {
        console.log('AI Jobs WebSocket disconnected');
        setWsConnected(false);
        // Reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
      };

      wsRef.current = ws;
    };

    // connectWebSocket(); // Uncomment when backend is ready

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const getCategoryColor = (category: string) => {
    const colors = {
      content_writing: 'bg-blue-500',
      data_analysis: 'bg-purple-500',
      code_generation: 'bg-green-500',
      virtual_assistant: 'bg-yellow-500',
      prompt_engineering: 'bg-pink-500',
      web_scraping: 'bg-orange-500',
      default: 'bg-gray-500'
    };
    return colors[category] || colors.default;
  };

  const getStatusBadge = (status: string) => {
    const badges = {
      new: <Badge className="bg-blue-100 text-blue-700">New</Badge>,
      analyzed: <Badge className="bg-yellow-100 text-yellow-700">Analyzed</Badge>,
      applied: <Badge className="bg-green-100 text-green-700">Applied</Badge>,
      responded: <Badge className="bg-purple-100 text-purple-700">Response</Badge>,
      won: <Badge className="bg-emerald-500 text-white">Won</Badge>
    };
    return badges[status] || badges.new;
  };

  return (
    <div className="space-y-6">
      {/* Header Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <Card className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Active Spiders</p>
                <p className="text-2xl font-bold">{stats.active_spiders}/13</p>
              </div>
              <Activity className="h-8 w-8 text-purple-500 animate-pulse" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Jobs Analyzed</p>
                <p className="text-2xl font-bold">{stats.total_analyzed}</p>
              </div>
              <Brain className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">AI Suitable</p>
                <p className="text-2xl font-bold">{stats.ai_suitable}</p>
              </div>
              <Target className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-yellow-50 to-yellow-100 dark:from-yellow-900/20 dark:to-yellow-800/20">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Applied</p>
                <p className="text-2xl font-bold">{stats.applications_sent}</p>
              </div>
              <Briefcase className="h-8 w-8 text-yellow-500" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-emerald-50 to-emerald-100 dark:from-emerald-900/20 dark:to-emerald-800/20">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Avg AI Score</p>
                <p className="text-2xl font-bold">{(stats.avg_ai_score * 100).toFixed(0)}%</p>
              </div>
              <Sparkles className="h-8 w-8 text-emerald-500" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-indigo-50 to-indigo-100 dark:from-indigo-900/20 dark:to-indigo-800/20">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Potential</p>
                <p className="text-2xl font-bold">${stats.potential_revenue}</p>
              </div>
              <DollarSign className="h-8 w-8 text-indigo-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Spider Status Grid */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Bot className="h-5 w-5" />
                Spider Army Status
              </CardTitle>
              <CardDescription>Real-time data collection from 13 specialized spiders</CardDescription>
            </div>
            <Button
              onClick={activateAllSpiders}
              disabled={loading}
              variant="outline"
              className="flex items-center gap-2"
            >
              <Activity className="h-4 w-4" />
              {loading ? 'Activating...' : 'Activate All Spiders'}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
            {spiders.map((spider) => (
              <div
                key={spider.name}
                className={`p-3 rounded-lg border ${
                  spider.active
                    ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
                    : 'bg-gray-50 dark:bg-gray-900/20 border-gray-200 dark:border-gray-800'
                }`}
              >
                <div className="flex items-start justify-between mb-1">
                  <div className="text-xs font-medium truncate">{spider.name}</div>
                  <div className={`w-2 h-2 rounded-full ${spider.active ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`} />
                </div>
                <div className="text-lg font-bold">{spider.data_collected}</div>
                <div className="text-xs text-gray-500">{spider.last_update}</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* AI Job Opportunities */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5" />
            AI-Suitable Job Opportunities
          </CardTitle>
          <CardDescription>
            Jobs analyzed and matched by our AI system for optimal success
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {jobs.map((job) => (
              <div key={job.id} className="p-4 rounded-lg border bg-card hover:shadow-lg transition-all">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold">{job.title}</h3>
                      {getStatusBadge(job.status)}
                    </div>
                    <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
                      <span className="flex items-center gap-1">
                        <Users className="h-3 w-3" />
                        {job.platform}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {job.estimated_hours}h
                      </span>
                      <span className="flex items-center gap-1">
                        <DollarSign className="h-3 w-3" />
                        ${job.budget}
                      </span>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-green-600">
                      {(job.ai_score * 100).toFixed(0)}%
                    </div>
                    <div className="text-xs text-gray-500">AI Score</div>
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Success Probability</span>
                    <div className="flex items-center gap-2">
                      <Progress value={job.success_probability * 100} className="w-24" />
                      <span className="text-sm font-medium">{(job.success_probability * 100).toFixed(0)}%</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 flex-wrap">
                    <Badge variant="outline" className={getCategoryColor(job.category)}>
                      {job.category.replace('_', ' ')}
                    </Badge>
                    {job.ai_tools.map((tool) => (
                      <Badge key={tool} variant="secondary" className="text-xs">
                        {tool}
                      </Badge>
                    ))}
                  </div>

                  {job.status === 'analyzed' && (
                    <div className="flex gap-2 mt-3">
                      <Button size="sm" className="flex-1">
                        <FileText className="h-4 w-4 mr-1" />
                        View Resume
                      </Button>
                      <Button size="sm" variant="outline" className="flex-1">
                        <Eye className="h-4 w-4 mr-1" />
                        View Proposal
                      </Button>
                      <Button
                        size="sm"
                        variant="default"
                        className="flex-1"
                        onClick={() => applyToJob(job.id)}
                        disabled={loading}
                      >
                        <Zap className="h-4 w-4 mr-1" />
                        {loading ? 'Applying...' : 'Apply Now'}
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          {jobs.length === 0 && (
            <Alert>
              <AlertDescription>
                No AI-suitable jobs found yet. Spiders are actively searching for opportunities...
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default AIJobTracker;