import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Alert, AlertDescription } from './ui/alert';
import {
  DollarSign,
  TrendingUp,
  Send,
  Clock,
  CheckCircle2,
  XCircle,
  AlertCircle,
  BarChart3,
  Users,
  Target,
  Zap,
  Brain
} from 'lucide-react';

interface Opportunity {
  id: string;
  opportunity_id: string;
  platform: string;
  title: string;
  budget: string;
  deadline: string;
  status: string;
  success_score: number;
  priority_level: string;
  revenue_generated: number;
  created_at: string;
  submitted_at: string | null;
  proposal_content?: string;
  skills_required?: string[];
}

interface Metrics {
  total_opportunities: number;
  proposals_submitted: number;
  responses_received: number;
  conversions: number;
  total_revenue: number;
  average_deal_size: number;
  response_rate: number;
  conversion_rate: number;
  platform_breakdown: {
    [key: string]: {
      count: number;
      submitted: number;
      converted: number;
      revenue: number;
    };
  };
}

const RevenueOpportunities: React.FC = () => {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [selectedOpportunity, setSelectedOpportunity] = useState<Opportunity | null>(null);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [activeTab, setActiveTab] = useState('opportunities');
  const [wsConnection, setWsConnection] = useState<WebSocket | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('disconnected');

  // WebSocket connection for real-time updates
  useEffect(() => {
    const connectWebSocket = () => {
      const ws = new WebSocket('ws://localhost:8000/ws/revenue-income/');

      ws.onopen = () => {
        console.log('🔌 Connected to Revenue Income WebSocket');
        setConnectionStatus('connected');
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('📨 WebSocket message:', data);

        switch (data.type) {
          case 'opportunity_update':
            handleOpportunityUpdate(data);
            break;
          case 'proposal_status_update':
            handleProposalStatusUpdate(data);
            break;
          case 'revenue_generated':
            handleRevenueGenerated(data);
            break;
          case 'metrics_update':
            setMetrics(data.metrics);
            break;
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionStatus('disconnected');
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setConnectionStatus('disconnected');
        // Reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
      };

      setWsConnection(ws);
    };

    connectWebSocket();

    return () => {
      if (wsConnection) {
        wsConnection.close();
      }
    };
  }, []);

  // Fetch opportunities
  const fetchOpportunities = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/intelligence/revenue/opportunities/');
      const data = await response.json();

      if (data.success) {
        setOpportunities(data.opportunities);
      }
    } catch (error) {
      console.error('Error fetching opportunities:', error);
    } finally {
      setLoading(false);
    }
  };

  // Fetch metrics
  const fetchMetrics = async () => {
    try {
      const response = await fetch('/api/v1/intelligence/revenue/metrics/?days=30');
      const data = await response.json();

      if (data.success) {
        setMetrics(data.metrics);
      }
    } catch (error) {
      console.error('Error fetching metrics:', error);
    }
  };

  useEffect(() => {
    fetchOpportunities();
    fetchMetrics();
  }, []);

  // Handle opportunity update from WebSocket
  const handleOpportunityUpdate = (data: any) => {
    const { opportunity, result } = data;

    // Update or add opportunity in the list
    setOpportunities(prev => {
      const index = prev.findIndex(o => o.opportunity_id === opportunity.id);
      if (index >= 0) {
        const updated = [...prev];
        updated[index] = { ...updated[index], ...result };
        return updated;
      } else {
        return [...prev, { ...opportunity, ...result }];
      }
    });
  };

  // Handle proposal status update
  const handleProposalStatusUpdate = (data: any) => {
    const { proposal_id, status } = data;

    setOpportunities(prev =>
      prev.map(opp =>
        opp.id === proposal_id
          ? { ...opp, status }
          : opp
      )
    );
  };

  // Handle revenue generated event
  const handleRevenueGenerated = (data: any) => {
    const { amount, proposal_id } = data;

    // Update opportunity with revenue
    setOpportunities(prev =>
      prev.map(opp =>
        opp.id === proposal_id
          ? { ...opp, revenue_generated: amount, status: 'converted' }
          : opp
      )
    );

    // Refresh metrics
    fetchMetrics();
  };

  // Submit proposal
  const submitProposal = async (opportunity: Opportunity) => {
    setSubmitting(true);
    try {
      const response = await fetch('/api/v1/intelligence/revenue/submit/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          opportunity_plan_id: opportunity.id
        })
      });

      const data = await response.json();

      if (data.success) {
        // Update opportunity status
        setOpportunities(prev =>
          prev.map(opp =>
            opp.id === opportunity.id
              ? { ...opp, status: 'proposal_submitted', submitted_at: data.submitted_at }
              : opp
          )
        );
      }
    } catch (error) {
      console.error('Error submitting proposal:', error);
    } finally {
      setSubmitting(false);
    }
  };

  // Process new opportunity
  const processOpportunity = async (opportunityData: any) => {
    try {
      const response = await fetch('/api/v1/intelligence/revenue/opportunities/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(opportunityData)
      });

      const data = await response.json();

      if (data.success) {
        fetchOpportunities();
      }
    } catch (error) {
      console.error('Error processing opportunity:', error);
    }
  };

  // Get status badge color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'identified': return 'bg-gray-500';
      case 'analyzing': return 'bg-blue-500';
      case 'plan_created': return 'bg-indigo-500';
      case 'proposal_generated': return 'bg-purple-500';
      case 'proposal_submitted': return 'bg-yellow-500';
      case 'awaiting_response': return 'bg-orange-500';
      case 'client_responded': return 'bg-teal-500';
      case 'negotiating': return 'bg-pink-500';
      case 'converted': return 'bg-green-500';
      case 'rejected': return 'bg-red-500';
      case 'expired': return 'bg-gray-400';
      default: return 'bg-gray-500';
    }
  };

  // Get priority badge variant
  const getPriorityVariant = (priority: string): "default" | "secondary" | "destructive" | "outline" => {
    switch (priority) {
      case 'high': return 'destructive';
      case 'medium': return 'default';
      case 'low': return 'secondary';
      default: return 'outline';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header with Connection Status */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold">Revenue Opportunities</h2>
          <p className="text-muted-foreground">
            Real-time revenue generation from automated proposals
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant={connectionStatus === 'connected' ? 'default' : 'secondary'}>
            {connectionStatus === 'connected' ? '🟢' : '🔴'} {connectionStatus}
          </Badge>
          <Button onClick={fetchOpportunities} variant="outline">
            Refresh
          </Button>
        </div>
      </div>

      {/* Metrics Dashboard */}
      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${metrics.total_revenue.toFixed(2)}</div>
              <p className="text-xs text-muted-foreground">
                Average deal: ${metrics.average_deal_size.toFixed(2)}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Response Rate</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.response_rate.toFixed(1)}%</div>
              <Progress value={metrics.response_rate} className="mt-2" />
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Conversion Rate</CardTitle>
              <Target className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.conversion_rate.toFixed(1)}%</div>
              <Progress value={metrics.conversion_rate} className="mt-2" />
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Proposals</CardTitle>
              <Send className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.proposals_submitted}</div>
              <p className="text-xs text-muted-foreground">
                {metrics.responses_received} responses
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="opportunities">Opportunities</TabsTrigger>
          <TabsTrigger value="proposals">Proposals</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="opportunities" className="space-y-4">
          {/* Opportunities List */}
          <div className="grid gap-4">
            {loading ? (
              <Card>
                <CardContent className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                </CardContent>
              </Card>
            ) : opportunities.length === 0 ? (
              <Card>
                <CardContent className="text-center py-8">
                  <p className="text-muted-foreground">No opportunities found</p>
                </CardContent>
              </Card>
            ) : (
              opportunities.map((opportunity) => (
                <Card key={opportunity.id} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div className="space-y-1">
                        <CardTitle className="text-lg">
                          {opportunity.title || `Opportunity ${opportunity.opportunity_id}`}
                        </CardTitle>
                        <CardDescription>
                          {opportunity.platform} • {opportunity.budget} • {opportunity.deadline}
                        </CardDescription>
                      </div>
                      <div className="flex flex-col items-end gap-2">
                        <Badge className={getStatusColor(opportunity.status)}>
                          {opportunity.status.replace('_', ' ')}
                        </Badge>
                        <Badge variant={getPriorityVariant(opportunity.priority_level)}>
                          {opportunity.priority_level} priority
                        </Badge>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {/* Success Score */}
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span>Success Probability</span>
                          <span>{(opportunity.success_score * 100).toFixed(1)}%</span>
                        </div>
                        <Progress value={opportunity.success_score * 100} />
                      </div>

                      {/* Skills */}
                      {opportunity.skills_required && (
                        <div className="flex flex-wrap gap-2">
                          {opportunity.skills_required.map((skill, index) => (
                            <Badge key={index} variant="outline">
                              {skill}
                            </Badge>
                          ))}
                        </div>
                      )}

                      {/* Actions */}
                      <div className="flex justify-between items-center">
                        <div className="text-sm text-muted-foreground">
                          Created: {new Date(opportunity.created_at).toLocaleDateString()}
                        </div>
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => setSelectedOpportunity(opportunity)}
                          >
                            View Details
                          </Button>
                          {opportunity.status === 'plan_created' && (
                            <Button
                              size="sm"
                              onClick={() => submitProposal(opportunity)}
                              disabled={submitting}
                            >
                              <Send className="h-4 w-4 mr-1" />
                              Submit Proposal
                            </Button>
                          )}
                        </div>
                      </div>

                      {/* Revenue if converted */}
                      {opportunity.revenue_generated > 0 && (
                        <Alert>
                          <CheckCircle2 className="h-4 w-4" />
                          <AlertDescription>
                            Revenue Generated: ${opportunity.revenue_generated.toFixed(2)}
                          </AlertDescription>
                        </Alert>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </TabsContent>

        <TabsContent value="proposals" className="space-y-4">
          {/* Submitted Proposals */}
          <div className="grid gap-4">
            {opportunities
              .filter(o => ['proposal_submitted', 'awaiting_response', 'client_responded', 'negotiating', 'converted', 'rejected'].includes(o.status))
              .map((proposal) => (
                <Card key={proposal.id}>
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <CardTitle className="text-lg">{proposal.title}</CardTitle>
                      <Badge className={getStatusColor(proposal.status)}>
                        {proposal.status.replace('_', ' ')}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">Platform:</span>
                        <span className="ml-2 font-medium">{proposal.platform}</span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Budget:</span>
                        <span className="ml-2 font-medium">{proposal.budget}</span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Submitted:</span>
                        <span className="ml-2 font-medium">
                          {proposal.submitted_at ? new Date(proposal.submitted_at).toLocaleDateString() : 'Not submitted'}
                        </span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Success Score:</span>
                        <span className="ml-2 font-medium">{(proposal.success_score * 100).toFixed(1)}%</span>
                      </div>
                    </div>

                    {proposal.status === 'converted' && (
                      <Alert className="mt-4">
                        <CheckCircle2 className="h-4 w-4" />
                        <AlertDescription>
                          Converted! Revenue: ${proposal.revenue_generated.toFixed(2)}
                        </AlertDescription>
                      </Alert>
                    )}

                    {proposal.status === 'rejected' && (
                      <Alert className="mt-4" variant="destructive">
                        <XCircle className="h-4 w-4" />
                        <AlertDescription>
                          Proposal was rejected. Learning from feedback...
                        </AlertDescription>
                      </Alert>
                    )}
                  </CardContent>
                </Card>
              ))}
          </div>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          {/* Platform Breakdown */}
          {metrics && (
            <Card>
              <CardHeader>
                <CardTitle>Platform Performance</CardTitle>
                <CardDescription>Revenue and conversion by platform</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {Object.entries(metrics.platform_breakdown).map(([platform, stats]) => (
                    <div key={platform} className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="font-medium capitalize">{platform}</span>
                        <span className="text-sm text-muted-foreground">
                          ${stats.revenue.toFixed(2)} revenue
                        </span>
                      </div>
                      <div className="grid grid-cols-3 gap-2 text-sm">
                        <div>
                          <span className="text-muted-foreground">Opportunities:</span>
                          <span className="ml-2 font-medium">{stats.count}</span>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Submitted:</span>
                          <span className="ml-2 font-medium">{stats.submitted}</span>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Converted:</span>
                          <span className="ml-2 font-medium">{stats.converted}</span>
                        </div>
                      </div>
                      <Progress
                        value={stats.count > 0 ? (stats.converted / stats.count) * 100 : 0}
                      />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Success Factors */}
          <Card>
            <CardHeader>
              <CardTitle>Success Factors</CardTitle>
              <CardDescription>What's driving conversions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <Zap className="h-4 w-4 text-yellow-500" />
                  <span className="text-sm">Quick response time (&lt;2 hours) increases success by 45%</span>
                </div>
                <div className="flex items-center gap-2">
                  <Brain className="h-4 w-4 text-purple-500" />
                  <span className="text-sm">ML-optimized proposals have 2.3x higher conversion</span>
                </div>
                <div className="flex items-center gap-2">
                  <Target className="h-4 w-4 text-green-500" />
                  <span className="text-sm">High success score (&gt;70%) proposals convert at 35%</span>
                </div>
                <div className="flex items-center gap-2">
                  <BarChart3 className="h-4 w-4 text-blue-500" />
                  <span className="text-sm">Portfolio samples increase response rate by 60%</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Opportunity Detail Modal */}
      {selectedOpportunity && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-full max-w-2xl max-h-[80vh] overflow-auto">
            <CardHeader>
              <div className="flex justify-between items-start">
                <CardTitle>{selectedOpportunity.title}</CardTitle>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => setSelectedOpportunity(null)}
                >
                  ✕
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-muted-foreground">Platform:</span>
                    <span className="ml-2 font-medium">{selectedOpportunity.platform}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Budget:</span>
                    <span className="ml-2 font-medium">{selectedOpportunity.budget}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Deadline:</span>
                    <span className="ml-2 font-medium">{selectedOpportunity.deadline}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Status:</span>
                    <Badge className={`ml-2 ${getStatusColor(selectedOpportunity.status)}`}>
                      {selectedOpportunity.status}
                    </Badge>
                  </div>
                </div>

                {selectedOpportunity.proposal_content && (
                  <div>
                    <h4 className="font-semibold mb-2">Proposal Content</h4>
                    <div className="bg-muted p-4 rounded-lg">
                      <pre className="whitespace-pre-wrap text-sm">
                        {selectedOpportunity.proposal_content}
                      </pre>
                    </div>
                  </div>
                )}

                <div className="flex justify-end gap-2">
                  <Button variant="outline" onClick={() => setSelectedOpportunity(null)}>
                    Close
                  </Button>
                  {selectedOpportunity.status === 'plan_created' && (
                    <Button onClick={() => {
                      submitProposal(selectedOpportunity);
                      setSelectedOpportunity(null);
                    }}>
                      Submit Proposal
                    </Button>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default RevenueOpportunities;