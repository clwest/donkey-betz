/**
 * Mythology Dashboard Page
 * Main dashboard for mythology review system with overview stats and management
 */
import React, { useState, useEffect } from 'react';
import { AlertTriangle, Flag, Clock, CheckCircle, TrendingUp, Users } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { Button } from '../../../components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../../components/ui/tabs';
import { Alert, AlertDescription } from '../../../components/ui/alert';
import { toast } from 'sonner';

import { 
  useMythologyStats, 
  useNotifications, 
  useRecentEvents,
  useMythologyWebSocket,
  useMarkAllNotificationsRead,
  type AlertNotification,
  type MythologyEvent 
} from '../api/mythology';
import { FlaggedContentTable } from '../components/FlaggedContentTable';
import { ReviewModal } from '../components/ReviewModal';
import { AlertNotifications } from '../components/AlertNotifications';
import { UserReportButton } from '../components/UserReportButton';

export const MythologyDashboard: React.FC = () => {
  const [selectedContentId, setSelectedContentId] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState('overview');

  // API hooks
  const { data: stats, isLoading: statsLoading, error: statsError } = useMythologyStats();
  const { data: notifications, isLoading: notificationsLoading } = useNotifications({ unread_only: true });
  const { data: recentEvents, isLoading: eventsLoading } = useRecentEvents({ limit: 20 });
  const markAllReadMutation = useMarkAllNotificationsRead();

  // WebSocket for real-time notifications
  const { connectWebSocket } = useMythologyWebSocket((notification: AlertNotification) => {
    // Show toast for new notifications
    toast.info(notification.title, {
      description: notification.message,
      action: notification.content_id ? {
        label: 'Review',
        onClick: () => setSelectedContentId(notification.content_id!),
      } : undefined,
    });
  });

  useEffect(() => {
    // Connect to WebSocket for real-time updates
    const ws = connectWebSocket();
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, []); // Empty dependency array to prevent reconnections

  // Handle review modal close
  const handleReviewClose = () => {
    setSelectedContentId(null);
  };

  // Handle mark all notifications as read
  const handleMarkAllRead = () => {
    markAllReadMutation.mutate();
  };

  // Priority color mapping
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'bg-red-500';
      case 'high': return 'bg-orange-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-green-500';
      default: return 'bg-gray-500';
    }
  };

  // Gaming-themed stats cards data
  const statsCards = [
    {
      title: 'FLAGGED CONTENT ITEMS',
      value: stats?.total_flagged || 0,
      icon: Flag,
      description: 'Content items flagged for verification',
      color: 'text-cyan-400',
      bgGlow: 'shadow-cyan-500/50',
    },
    {
      title: 'VERIFICATION QUEUE',
      value: (recentEvents && Array.isArray(recentEvents)) ? recentEvents.length : 0,
      icon: Clock,
      description: 'Content pending verification review',
      color: 'text-yellow-400',
      bgGlow: 'shadow-yellow-500/50',
    },
    {
      title: 'HIGH-PRIORITY ITEMS',
      value: stats?.high_priority || 0,
      icon: AlertTriangle,
      description: 'Critical content requiring immediate review',
      color: 'text-red-400',
      bgGlow: 'shadow-red-500/50',
    },
    {
      title: 'VERIFIED TODAY',
      value: stats?.resolved_today || 0,
      icon: CheckCircle,
      description: 'Content items verified and processed',
      color: 'text-green-400',
      bgGlow: 'shadow-green-500/50',
    },
  ];

  if (statsError) {
    return (
      <div className="p-6">
        <Alert className="border-red-200 bg-red-50">
          <AlertTriangle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-800">
            Failed to load mythology dashboard. Please check your connection and try again.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold tracking-tight uppercase text-cyan-400 glow-text-sm animate-pulse-glow">
            RAG CONTENT VERIFICATION
          </h1>
          <p className="text-purple-400 text-lg font-mono">
            {'>>>'} HALLUCINATION PREVENTION SYSTEM • CONTENT INTEGRITY MONITOR ACTIVE
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <UserReportButton />
          {notifications && notifications.length > 0 && (
            <Button 
              variant="outline" 
              size="sm"
              onClick={handleMarkAllRead}
              disabled={markAllReadMutation.isPending}
            >
              Mark All Read ({notifications.length})
            </Button>
          )}
        </div>
      </div>

      {/* Real-time Notifications */}
      <AlertNotifications />

      {/* Gaming Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {statsCards.map((card, index) => (
          <Card key={index} className={`bg-gray-900/80 border-2 border-purple-800/50 hover:border-cyan-400/80 hover:shadow-lg transition-all duration-300 ${card.bgGlow}`}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className={`text-sm font-mono uppercase tracking-wider ${card.color}`}>
                {card.title}
              </CardTitle>
              <card.icon className={`h-5 w-5 ${card.color} animate-pulse`} />
            </CardHeader>
            <CardContent>
              <div className={`text-3xl font-bold font-mono ${card.color} glow-text-sm`}>
                {statsLoading ? (
                  <div className="h-8 w-16 bg-gray-800/50 animate-pulse rounded border border-purple-700/50" />
                ) : (
                  card.value.toLocaleString()
                )}
              </div>
              <p className="text-xs text-purple-300 font-mono mt-2">
                {card.description}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Neural Performance Analytics */}
      {stats && (
        <div className="grid gap-4 md:grid-cols-2">
          <Card className="bg-gray-900/80 border-2 border-green-800/50 hover:border-green-400/80 hover:shadow-lg hover:shadow-green-500/30 transition-all duration-300">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <TrendingUp className="h-5 w-5 text-green-400 animate-pulse" />
                <span className="text-green-400 font-mono uppercase tracking-wider">VERIFICATION PROCESSING STATS</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-purple-300 font-mono">AVG REVIEW TIME</span>
                <Badge className="bg-green-900/50 text-green-400 border border-green-400/50 font-mono">
                  {stats.avg_review_time ? `${stats.avg_review_time.toFixed(1)}h` : 'N/A'}
                </Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-purple-300 font-mono">FALSE POSITIVE RATE</span>
                <Badge 
                  className={`font-mono border ${stats.false_positive_rate < 0.1 ? "bg-green-900/50 text-green-400 border-green-400/50" : "bg-red-900/50 text-red-400 border-red-400/50"}`}
                >
                  {stats.false_positive_rate ? `${(stats.false_positive_rate * 100).toFixed(1)}%` : 'N/A'}
                </Badge>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gray-900/80 border-2 border-cyan-800/50 hover:border-cyan-400/80 hover:shadow-lg hover:shadow-cyan-500/30 transition-all duration-300">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Users className="h-5 w-5 text-cyan-400 animate-pulse" />
                <span className="text-cyan-400 font-mono uppercase tracking-wider">CONTENT INTEGRITY</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-purple-300 font-mono">QUEUE STATUS</span>
                <Badge 
                  className={`font-mono border ${stats.pending_review < 50 ? "bg-green-900/50 text-green-400 border-green-400/50" : stats.pending_review < 100 ? "bg-yellow-900/50 text-yellow-400 border-yellow-400/50" : "bg-red-900/50 text-red-400 border-red-400/50"}`}
                >
                  {stats.pending_review < 50 ? 'OPTIMAL' : stats.pending_review < 100 ? 'MODERATE' : 'CRITICAL'}
                </Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-purple-300 font-mono">HIGH-PRIORITY ITEMS</span>
                <Badge className={`font-mono border ${stats.high_priority === 0 ? "bg-green-900/50 text-green-400 border-green-400/50" : "bg-red-900/50 text-red-400 border-red-400/50"}`}>
                  {stats.high_priority === 0 ? 'NONE' : `${stats.high_priority} PENDING`}
                </Badge>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Gaming Navigation Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="bg-gray-900/80 border border-purple-800/50">
          <TabsTrigger value="overview" className="data-[state=active]:bg-cyan-900/50 data-[state=active]:text-cyan-400 text-purple-300 font-mono uppercase tracking-wider">OVERVIEW</TabsTrigger>
          <TabsTrigger value="pending" className="data-[state=active]:bg-yellow-900/50 data-[state=active]:text-yellow-400 text-purple-300 font-mono uppercase tracking-wider">
            VERIFICATION QUEUE
            {recentEvents && Array.isArray(recentEvents) && recentEvents.length > 0 ? (
              <Badge className="ml-2 bg-yellow-900/50 text-yellow-400 border border-yellow-400/50 font-mono animate-pulse">
                {recentEvents.length}
              </Badge>
            ) : null}
          </TabsTrigger>
          <TabsTrigger value="high-priority" className="data-[state=active]:bg-red-900/50 data-[state=active]:text-red-400 text-purple-300 font-mono uppercase tracking-wider">
            HIGH-PRIORITY
            {stats?.high_priority ? (
              <Badge className="ml-2 bg-red-900/50 text-red-400 border border-red-400/50 font-mono animate-pulse glow-sm">
                {stats.high_priority}
              </Badge>
            ) : null}
          </TabsTrigger>
          <TabsTrigger value="resolved" className="data-[state=active]:bg-green-900/50 data-[state=active]:text-green-400 text-purple-300 font-mono uppercase tracking-wider">VERIFIED</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <Card className="bg-gray-900/80 border-2 border-cyan-800/50 hover:border-cyan-400/80 hover:shadow-lg hover:shadow-cyan-500/30 transition-all duration-300">
            <CardHeader>
              <CardTitle className="text-cyan-400 font-mono uppercase tracking-wider">RECENT VERIFICATION ACTIVITY</CardTitle>
              <CardDescription className="text-purple-300 font-mono">
                {'>>>'} Latest content verification and review activity
              </CardDescription>
            </CardHeader>
            <CardContent>
              <FlaggedContentTable 
                filters={{}}
                onReviewClick={setSelectedContentId}
                compact={false}
              />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="pending">
          <Card className="bg-gray-900/80 border-2 border-yellow-800/50 hover:border-yellow-400/80 hover:shadow-lg hover:shadow-yellow-500/30 transition-all duration-300">
            <CardHeader>
              <CardTitle className="text-yellow-400 font-mono uppercase tracking-wider">CONTENT VERIFICATION QUEUE</CardTitle>
              <CardDescription className="text-purple-300 font-mono">
                {'>>>'} Content items awaiting verification review
              </CardDescription>
            </CardHeader>
            <CardContent>
              {eventsLoading ? (
                <div className="space-y-3">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="h-16 bg-gray-800/50 animate-pulse rounded border border-purple-700/50" />
                  ))}
                </div>
              ) : !recentEvents || !Array.isArray(recentEvents) || recentEvents.length === 0 ? (
                <div className="text-center py-8">
                  <div className="text-purple-400 font-mono text-lg">NO PENDING REVIEWS</div>
                  <div className="text-purple-300/60 font-mono text-sm mt-2">Content verification queue is clear</div>
                </div>
              ) : (
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {(recentEvents || []).map((event: MythologyEvent) => (
                    <div 
                      key={event.id} 
                      className="bg-gray-800/50 border border-purple-700/50 rounded p-4 hover:border-yellow-400/50 transition-all duration-200"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-3">
                          <Badge 
                            className={`font-mono text-xs ${
                              event.risk_level >= 0.8 ? 'bg-red-900/50 text-red-400 border-red-400/50' :
                              event.risk_level >= 0.5 ? 'bg-yellow-900/50 text-yellow-400 border-yellow-400/50' :
                              'bg-green-900/50 text-green-400 border-green-400/50'
                            }`}
                          >
                            RISK: {(event.risk_level * 100).toFixed(0)}%
                          </Badge>
                          <Badge className="bg-cyan-900/50 text-cyan-400 border-cyan-400/50 font-mono text-xs">
                            {event.event_type.toUpperCase()}
                          </Badge>
                          {event.was_prevented && (
                            <Badge className="bg-green-900/50 text-green-400 border-green-400/50 font-mono text-xs animate-pulse">
                              PREVENTED
                            </Badge>
                          )}
                        </div>
                        <div className="text-xs text-purple-400 font-mono">
                          {new Date(event.created_at).toLocaleString()}
                        </div>
                      </div>
                      
                      <div className="text-sm text-purple-200 font-mono mb-2">
                        {event.content_preview}
                      </div>
                      
                      {event.patterns_detected.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-2">
                          {event.patterns_detected.map((pattern, idx) => (
                            <Badge 
                              key={idx} 
                              className="bg-purple-900/50 text-purple-300 border-purple-400/30 font-mono text-xs"
                            >
                              {pattern}
                            </Badge>
                          ))}
                        </div>
                      )}
                      
                      <div className="flex items-center justify-between mt-3 pt-2 border-t border-purple-700/30">
                        <div className="text-xs text-purple-400 font-mono">
                          Confidence: {(event.confidence_score * 100).toFixed(1)}%
                        </div>
                        {event.prevention_method && (
                          <div className="text-xs text-green-400 font-mono">
                            Method: {event.prevention_method}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="high-priority">
          <Card className="bg-gray-900/80 border-2 border-red-800/50 hover:border-red-400/80 hover:shadow-lg hover:shadow-red-500/30 transition-all duration-300">
            <CardHeader>
              <CardTitle className="text-red-400 font-mono uppercase tracking-wider animate-pulse">HIGH-PRIORITY CONTENT</CardTitle>
              <CardDescription className="text-purple-300 font-mono">
                {'>>>'} Critical content items requiring immediate verification
              </CardDescription>
            </CardHeader>
            <CardContent>
              <FlaggedContentTable 
                filters={{ priority: 'high,critical' }}
                onReviewClick={setSelectedContentId}
              />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="resolved">
          <Card className="bg-gray-900/80 border-2 border-green-800/50 hover:border-green-400/80 hover:shadow-lg hover:shadow-green-500/30 transition-all duration-300">
            <CardHeader>
              <CardTitle className="text-green-400 font-mono uppercase tracking-wider">VERIFIED CONTENT</CardTitle>
              <CardDescription className="text-purple-300 font-mono">
                {'>>>'} Successfully verified and processed content items
              </CardDescription>
            </CardHeader>
            <CardContent>
              <FlaggedContentTable 
                filters={{ status: 'resolved' }}
                onReviewClick={setSelectedContentId}
                showReviewDetails={true}
              />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Review Modal */}
      {selectedContentId && (
        <ReviewModal 
          contentId={selectedContentId}
          onClose={handleReviewClose}
        />
      )}
    </div>
  );
};