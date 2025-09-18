import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { toast } from 'sonner';
import {
  Bot,
  Activity,
  Briefcase,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  Loader2,
  TrendingUp
} from 'lucide-react';

interface Spider {
  id: string;
  name: string;
  status: 'active' | 'inactive';
  target: string;
  dataCollected: number;
}

interface Job {
  id: string;
  title: string;
  company: string;
  aiScore: number;
  budget: string;
  status: 'new' | 'applying' | 'applied';
}

export default function AIJobTrackerPage() {
  const [spiders, setSpiders] = useState<Spider[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    activeSpiders: 0,
    jobsAnalyzed: 0,
    aiSuitable: 0,
    applicationsGenerated: 0
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);

    // Load spider status
    try {
      const spiderRes = await fetch('http://localhost:8000/api/v1/intelligence/ai-jobs/spiders/', {
        credentials: 'include'
      });
      const spiderData = await spiderRes.json();
      if (spiderData.success) {
        setSpiders(spiderData.spiders);
      }
    } catch (error) {
      console.error('Error loading spiders:', error);
      // Use mock data if API fails
      setSpiders([
        { id: 'guru_spider', name: 'Guru.com Spider', status: 'active', target: 'guru.com', dataCollected: 42 },
        { id: 'toptal_spider', name: 'Toptal Spider', status: 'active', target: 'toptal.com', dataCollected: 38 },
        { id: 'remoteok_spider', name: 'RemoteOK Spider', status: 'active', target: 'remoteok.com', dataCollected: 55 },
        { id: 'market_analyzer', name: 'Market Analyzer', status: 'inactive', target: 'marketwatch.com', dataCollected: 0 },
        { id: 'tech_news_monitor', name: 'Tech News Monitor', status: 'active', target: 'techcrunch.com', dataCollected: 23 },
        { id: 'crypto_tracker', name: 'Crypto Tracker', status: 'inactive', target: 'coinmarketcap.com', dataCollected: 0 },
        { id: 'ai_news_aggregator', name: 'AI News Aggregator', status: 'active', target: 'ai-news.com', dataCollected: 19 },
        { id: 'startup_monitor', name: 'Startup Monitor', status: 'inactive', target: 'producthunt.com', dataCollected: 0 },
        { id: 'github_trending', name: 'GitHub Trending', status: 'inactive', target: 'github.com', dataCollected: 0 },
        { id: 'freelance_finder', name: 'Freelance Finder', status: 'inactive', target: 'upwork.com', dataCollected: 0 },
        { id: 'remote_work_specialist', name: 'Remote Work Specialist', status: 'inactive', target: 'weworkremotely.com', dataCollected: 0 },
        { id: 'gig_economy_expert', name: 'Gig Economy Expert', status: 'inactive', target: 'fiverr.com', dataCollected: 0 },
        { id: 'job_application_agent', name: 'Job Application Agent', status: 'inactive', target: 'linkedin.com', dataCollected: 0 }
      ]);
    }

    // Load jobs
    try {
      const jobRes = await fetch('http://localhost:8000/api/v1/intelligence/ai-jobs/jobs/', {
        credentials: 'include'
      });
      const jobData = await jobRes.json();
      if (jobData.success) {
        setJobs(jobData.jobs || []);
        setStats(jobData.stats || {
          activeSpiders: 0,
          jobsAnalyzed: 0,
          aiSuitable: 0,
          applicationsGenerated: 0
        });
      }
    } catch (error) {
      console.error('Error loading jobs:', error);
      // Use mock data if API fails
      setJobs([
        { id: '1', title: 'AI Content Writer for Tech Blog', company: 'TechStartup Inc', aiScore: 0.95, budget: '$500-1000', status: 'new' },
        { id: '2', title: 'ChatGPT Prompt Engineer', company: 'AI Agency', aiScore: 0.92, budget: '$2000-3000', status: 'applied' },
        { id: '3', title: 'AI Training Data Annotator', company: 'ML Corp', aiScore: 0.88, budget: '$30/hour', status: 'new' }
      ]);
      setStats({
        activeSpiders: 5,
        jobsAnalyzed: 3,
        aiSuitable: 3,
        applicationsGenerated: 2
      });
    }

    setLoading(false);
  };

  const startSpiders = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/intelligence/ai-jobs/start-spiders/', {
        method: 'POST',
        credentials: 'include'
      });
      const data = await res.json();
      if (data.success) {
        setTimeout(loadData, 1000);
      }
    } catch (error) {
      console.error('Error starting spiders:', error);
    }
  };

  const applyToJob = async (jobId: string) => {
    try {
      // Update UI to show applying state
      setJobs(prev => prev.map(job =>
        job.id === jobId ? { ...job, status: 'applying' } : job
      ));

      toast.info('Generating personalized application...');

      console.log('Applying to job:', jobId);
      const requestBody = { job_id: jobId };
      console.log('Request body:', requestBody);

      const res = await fetch('http://localhost:8000/api/v1/intelligence/ai-jobs/apply/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(requestBody)
      });

      console.log('Response status:', res.status);

      if (!res.ok) {
        const errorText = await res.text();
        console.error('Error response:', errorText);
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const data = await res.json();
      console.log('Response data:', data);

      if (data.success) {
        // Find the job to get its title
        const job = jobs.find(j => j.id === jobId);
        const jobTitle = job ? job.title : 'the position';
        console.log('Job found:', job);

        // Update job status to applied
        setJobs(prev => prev.map(job =>
          job.id === jobId ? { ...job, status: 'applied' } : job
        ));

        // Show success message with details
        if (data.result?.personalized) {
          const matchScore = data.result.match_score || 0;
          toast.success(
            `Successfully applied to ${jobTitle}! ` +
            `Match score: ${(matchScore * 100).toFixed(0)}%`
          );
          console.log('Personalized application with match score:', matchScore);
        } else {
          toast.success(`Applied to ${jobTitle}!`);
          console.log('Standard application completed');
        }

        // Log additional details if available
        if (data.result) {
          console.log('Application result:', data.result);
        }

        // Refresh data after a short delay
        setTimeout(loadData, 2000);
      } else {
        console.error('Application failed:', data.message);
        throw new Error(data.message || 'Application failed');
      }
    } catch (error) {
      console.error('Error applying to job:', error);

      // Reset job status on error
      setJobs(prev => prev.map(job =>
        job.id === jobId ? { ...job, status: 'new' } : job
      ));

      toast.error(`Failed to apply: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-900">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-purple-500 mx-auto mb-4" />
          <p className="text-white">Loading AI Job Tracker...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-500 mb-4">
            AI Job Tracker
          </h1>
          <p className="text-gray-400 text-lg">13 Spiders • Real-time Job Matching • Automated Applications</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-gray-400">Active Spiders</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-400">{stats?.activeSpiders || 0}/13</div>
              <Progress value={((stats?.activeSpiders || 0) / 13) * 100} className="mt-2 h-2" />
            </CardContent>
          </Card>

          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-gray-400">Jobs Analyzed</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-blue-400">{stats?.jobsAnalyzed || 0}</div>
              <p className="text-xs text-gray-500 mt-2">Last 24 hours</p>
            </CardContent>
          </Card>

          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-gray-400">AI Suitable</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-purple-400">{stats?.aiSuitable || 0}</div>
              <p className="text-xs text-gray-500 mt-2">&gt;70% score</p>
            </CardContent>
          </Card>

          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-gray-400">Applications</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-pink-400">{stats?.applicationsGenerated || 0}</div>
              <p className="text-xs text-gray-500 mt-2">Generated</p>
            </CardContent>
          </Card>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-4 mb-8 justify-center">
          <Button
            onClick={startSpiders}
            size="lg"
            className="bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700"
          >
            <Activity className="mr-2 h-5 w-5" />
            Activate All Spiders
          </Button>
          <Button
            onClick={loadData}
            size="lg"
            variant="outline"
            className="border-gray-600 text-white hover:bg-gray-800"
          >
            <RefreshCw className="mr-2 h-5 w-5" />
            Refresh Data
          </Button>
        </div>

        {/* Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Spider Status */}
          <div>
            <h2 className="text-2xl font-bold text-white mb-4 flex items-center">
              <Bot className="mr-2 h-6 w-6 text-purple-400" />
              Spider Network Status
            </h2>
            <div className="grid grid-cols-1 gap-3">
              {spiders.map((spider, index) => (
                <Card key={`spider-${spider.id}-${index}`} className="bg-gray-800/30 border-gray-700">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className={`h-3 w-3 rounded-full ${
                          spider.status === 'active' ? 'bg-green-500 animate-pulse' : 'bg-gray-500'
                        }`} />
                        <div>
                          <p className="text-white font-medium">{spider.name}</p>
                          <p className="text-xs text-gray-400">{spider.target}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        {spider.status === 'active' ? (
                          <Badge className="bg-green-500/20 text-green-400 border-green-500/50">
                            {spider.dataCollected} collected
                          </Badge>
                        ) : (
                          <Badge variant="secondary">Inactive</Badge>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* AI Jobs */}
          <div>
            <h2 className="text-2xl font-bold text-white mb-4 flex items-center">
              <Briefcase className="mr-2 h-6 w-6 text-blue-400" />
              AI-Matched Opportunities
            </h2>
            <div className="space-y-4">
              {jobs.length === 0 ? (
                <Card className="bg-gray-800/30 border-gray-700">
                  <CardContent className="p-8 text-center">
                    <AlertCircle className="h-12 w-12 text-gray-500 mx-auto mb-4" />
                    <p className="text-gray-400">No jobs analyzed yet. Activate spiders to start collecting opportunities.</p>
                  </CardContent>
                </Card>
              ) : (
                jobs.map((job, index) => (
                  <Card key={`job-${job.id}-${index}`} className="bg-gray-800/30 border-gray-700">
                    <CardContent className="p-6">
                      <div className="flex justify-between items-start mb-3">
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold text-white mb-1">{job.title}</h3>
                          <p className="text-sm text-gray-400">{job.company}</p>
                        </div>
                        <Badge className={`${
                          job.status === 'applied'
                            ? 'bg-green-500/20 text-green-400'
                            : job.status === 'applying'
                            ? 'bg-yellow-500/20 text-yellow-400'
                            : 'bg-blue-500/20 text-blue-400'
                        }`}>
                          {job.status === 'applied' ? 'Applied' : job.status === 'applying' ? 'Applying...' : 'New'}
                        </Badge>
                      </div>

                      <div className="flex items-center gap-4 mb-4">
                        <div className="flex items-center gap-2">
                          <TrendingUp className="h-4 w-4 text-purple-400" />
                          <span className="text-sm text-white">AI Score: {(job.aiScore * 100).toFixed(0)}%</span>
                        </div>
                        <div className="text-sm text-gray-400">{job.budget}</div>
                      </div>

                      <div className="flex items-center justify-between">
                        <Progress value={job.aiScore * 100} className="flex-1 mr-4 h-2" />
                        <Button
                          onClick={() => applyToJob(job.id)}
                          size="sm"
                          disabled={job.status !== 'new'}
                          className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
                        >
                          {job.status === 'applied' ? (
                            <span className="flex items-center">
                              <CheckCircle className="mr-2 h-4 w-4" />
                              Applied
                            </span>
                          ) : job.status === 'applying' ? (
                            <span className="flex items-center">
                              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                              Applying...
                            </span>
                          ) : (
                            'Apply Now'
                          )}
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}