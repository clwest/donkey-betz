import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Activity,
  DollarSign,
  Users,
  TrendingUp,
  FileCode,
  Twitter,
  Linkedin,
  Facebook,
  Star,
  CheckCircle,
  Clock,
  Code,
  MessageSquare,
  Eye,
  Heart,
  Share2,
  Download,
  ExternalLink
} from 'lucide-react';

interface AgentDeliverable {
  id: string;
  agentName: string;
  jobTitle: string;
  type: string;
  files: string[];
  status: 'in_progress' | 'completed' | 'delivered';
  createdAt: string;
  clientRating?: number;
  revenue?: number;
}

interface SocialPost {
  id: string;
  platform: 'twitter' | 'linkedin' | 'facebook';
  content: string;
  engagement: {
    likes: number;
    shares: number;
    comments: number;
    views: number;
  };
  timestamp: string;
}

interface SystemMetrics {
  day: number;
  totalRevenue: number;
  activeAgents: number;
  completedJobs: number;
  pendingJobs: number;
  clientSatisfaction: number;
  socialReach: number;
}

const AutonomousSystemDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [systemRunning, setSystemRunning] = useState(false);
  const [currentDay, setCurrentDay] = useState(0);
  const [metrics, setMetrics] = useState<SystemMetrics>({
    day: 0,
    totalRevenue: 0,
    activeAgents: 0,
    completedJobs: 0,
    pendingJobs: 0,
    clientSatisfaction: 0,
    socialReach: 0
  });
  const [deliverables, setDeliverables] = useState<AgentDeliverable[]>([]);
  const [socialPosts, setSocialPosts] = useState<SocialPost[]>([]);
  const [liveActivities, setLiveActivities] = useState<any[]>([]);

  // For now, we'll use a simple WebSocket connection
  const [messages, setMessages] = useState<any[]>([]);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    if (messages.length > 0) {
      const lastMessage = messages[messages.length - 1];

      if (lastMessage.type === 'metrics_update') {
        setMetrics(lastMessage.data);
        setCurrentDay(lastMessage.data.day);
      } else if (lastMessage.type === 'deliverable_created') {
        setDeliverables(prev => [lastMessage.data, ...prev].slice(0, 50));
      } else if (lastMessage.type === 'social_post') {
        setSocialPosts(prev => [lastMessage.data, ...prev].slice(0, 20));
      } else if (lastMessage.type === 'agent_activity') {
        setLiveActivities(prev => [lastMessage.data, ...prev].slice(0, 10));
      }
    }
  }, [messages]);

  const startAutonomousSystem = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/autonomous-system/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
        },
        credentials: 'include',
        body: JSON.stringify({ days: 30 })
      });

      if (response.ok) {
        setSystemRunning(true);
      }
    } catch (error) {
      console.error('Failed to start autonomous system:', error);
    }
  };

  const formatRevenue = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const getPlatformIcon = (platform: string) => {
    switch (platform) {
      case 'twitter': return <Twitter className="w-4 h-4" />;
      case 'linkedin': return <Linkedin className="w-4 h-4" />;
      case 'facebook': return <Facebook className="w-4 h-4" />;
      default: return null;
    }
  };

  return (
    <div className="w-full max-w-7xl mx-auto p-4 space-y-4">
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle className="text-2xl">30-Day Autonomous Revenue System</CardTitle>
              <CardDescription>
                AI agents finding work, completing tasks, and generating revenue autonomously
              </CardDescription>
            </div>
            <div className="flex items-center gap-4">
              {connected && (
                <Badge variant="outline" className="gap-1">
                  <Activity className="w-3 h-3 text-green-500" />
                  Live
                </Badge>
              )}
              {!systemRunning ? (
                <Button onClick={startAutonomousSystem} size="lg">
                  Start 30-Day Run
                </Button>
              ) : (
                <div className="text-center">
                  <div className="text-sm text-gray-500">Day</div>
                  <div className="text-2xl font-bold">{currentDay}/30</div>
                </div>
              )}
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <DollarSign className="w-4 h-4" />
              Total Revenue
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {formatRevenue(metrics.totalRevenue)}
            </div>
            <Progress value={(metrics.totalRevenue / 50000) * 100} className="mt-2" />
            <p className="text-xs text-gray-500 mt-1">Goal: $50,000</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Users className="w-4 h-4" />
              Active Agents
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.activeAgents}</div>
            <p className="text-xs text-gray-500 mt-1">Working on jobs</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <CheckCircle className="w-4 h-4" />
              Completed Jobs
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.completedJobs}</div>
            <p className="text-xs text-gray-500 mt-1">
              {metrics.pendingJobs} pending
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Star className="w-4 h-4" />
              Client Satisfaction
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {metrics.clientSatisfaction.toFixed(1)}/5.0
            </div>
            <div className="flex gap-1 mt-1">
              {[1, 2, 3, 4, 5].map((star) => (
                <Star
                  key={star}
                  className={`w-3 h-3 ${
                    star <= metrics.clientSatisfaction
                      ? 'fill-yellow-400 text-yellow-400'
                      : 'text-gray-300'
                  }`}
                />
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Live Activity</TabsTrigger>
          <TabsTrigger value="deliverables">Deliverables</TabsTrigger>
          <TabsTrigger value="social">Social Media</TabsTrigger>
          <TabsTrigger value="testimonials">Testimonials</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        {/* Live Activity */}
        <TabsContent value="overview" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Real-Time Agent Activity</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {liveActivities.length === 0 ? (
                <p className="text-gray-500">Waiting for agent activity...</p>
              ) : (
                liveActivities.map((activity, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                        <Code className="w-5 h-5 text-blue-600" />
                      </div>
                      <div>
                        <p className="font-medium">{activity.agentName}</p>
                        <p className="text-sm text-gray-600">{activity.action}</p>
                        <p className="text-xs text-gray-400">{activity.timestamp}</p>
                      </div>
                    </div>
                    <Badge variant={activity.status === 'working' ? 'default' : 'success'}>
                      {activity.status}
                    </Badge>
                  </div>
                ))
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Deliverables */}
        <TabsContent value="deliverables" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Agent Deliverables & Code</CardTitle>
              <CardDescription>Real code and files created by our agents</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {deliverables.map((deliverable) => (
                  <Card key={deliverable.id} className="p-4">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <Badge>{deliverable.type}</Badge>
                          <span className="font-medium">{deliverable.agentName}</span>
                          {deliverable.clientRating && (
                            <div className="flex items-center gap-1">
                              {[...Array(5)].map((_, i) => (
                                <Star
                                  key={i}
                                  className={`w-3 h-3 ${
                                    i < deliverable.clientRating!
                                      ? 'fill-yellow-400 text-yellow-400'
                                      : 'text-gray-300'
                                  }`}
                                />
                              ))}
                            </div>
                          )}
                        </div>
                        <h4 className="font-medium mb-2">{deliverable.jobTitle}</h4>
                        <div className="space-y-1">
                          {deliverable.files.map((file, idx) => (
                            <div key={idx} className="flex items-center gap-2 text-sm">
                              <FileCode className="w-4 h-4 text-gray-400" />
                              <span className="font-mono text-xs">{file}</span>
                              <Button variant="ghost" size="sm" className="h-6 px-2">
                                <Eye className="w-3 h-3 mr-1" />
                                View
                              </Button>
                              <Button variant="ghost" size="sm" className="h-6 px-2">
                                <Download className="w-3 h-3 mr-1" />
                                Download
                              </Button>
                            </div>
                          ))}
                        </div>
                      </div>
                      <div className="text-right">
                        {deliverable.revenue && (
                          <p className="text-lg font-bold text-green-600">
                            {formatRevenue(deliverable.revenue)}
                          </p>
                        )}
                        <Badge
                          variant={
                            deliverable.status === 'completed'
                              ? 'success'
                              : deliverable.status === 'delivered'
                              ? 'default'
                              : 'secondary'
                          }
                        >
                          {deliverable.status}
                        </Badge>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Social Media */}
        <TabsContent value="social" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Social Media Marketing</CardTitle>
              <CardDescription>AI-generated posts promoting our services</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4">
                {socialPosts.map((post) => (
                  <Card key={post.id} className="p-4">
                    <div className="flex items-start gap-3">
                      <div className="mt-1">{getPlatformIcon(post.platform)}</div>
                      <div className="flex-1">
                        <p className="text-sm whitespace-pre-wrap">{post.content}</p>
                        <div className="flex items-center gap-4 mt-3 text-sm text-gray-500">
                          <span className="flex items-center gap-1">
                            <Eye className="w-4 h-4" />
                            {post.engagement.views.toLocaleString()}
                          </span>
                          <span className="flex items-center gap-1">
                            <Heart className="w-4 h-4" />
                            {post.engagement.likes.toLocaleString()}
                          </span>
                          <span className="flex items-center gap-1">
                            <Share2 className="w-4 h-4" />
                            {post.engagement.shares.toLocaleString()}
                          </span>
                          <span className="flex items-center gap-1">
                            <MessageSquare className="w-4 h-4" />
                            {post.engagement.comments.toLocaleString()}
                          </span>
                        </div>
                      </div>
                      <Button variant="ghost" size="sm">
                        <ExternalLink className="w-4 h-4" />
                      </Button>
                    </div>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Testimonials */}
        <TabsContent value="testimonials" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Client Testimonials</CardTitle>
              <CardDescription>Real feedback from satisfied clients</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Testimonials will be populated from WebSocket */}
                <Alert>
                  <AlertDescription>
                    Client testimonials will appear here as jobs are completed and reviewed.
                  </AlertDescription>
                </Alert>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Analytics */}
        <TabsContent value="analytics" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Revenue Trend</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center text-gray-400">
                  Revenue chart will display here
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Agent Performance</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center text-gray-400">
                  Agent performance metrics will display here
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AutonomousSystemDashboard;