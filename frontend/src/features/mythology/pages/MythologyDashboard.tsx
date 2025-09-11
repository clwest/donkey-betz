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
  useMythologyWebSocket,
  useMarkAllNotificationsRead,
  type AlertNotification 
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

  // Stats cards data
  const statsCards = [
    {
      title: 'Total Flagged Content',
      value: stats?.total_flagged || 0,
      icon: Flag,
      description: 'Content items flagged for review',
      color: 'text-blue-600',
    },
    {
      title: 'Pending Reviews',
      value: stats?.pending_review || 0,
      icon: Clock,
      description: 'Items awaiting moderation',
      color: 'text-yellow-600',
    },
    {
      title: 'High Priority',
      value: stats?.high_priority || 0,
      icon: AlertTriangle,
      description: 'Critical items requiring immediate attention',
      color: 'text-red-600',
    },
    {
      title: 'Resolved Today',
      value: stats?.resolved_today || 0,
      icon: CheckCircle,
      description: 'Items resolved in the last 24 hours',
      color: 'text-green-600',
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
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Mythology Review Dashboard</h1>
          <p className="text-muted-foreground">
            Monitor and manage content flagged for review
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

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {statsCards.map((card, index) => (
          <Card key={index}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {card.title}
              </CardTitle>
              <card.icon className={`h-4 w-4 ${card.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {statsLoading ? (
                  <div className="h-8 w-16 bg-gray-200 animate-pulse rounded" />
                ) : (
                  card.value.toLocaleString()
                )}
              </div>
              <p className="text-xs text-muted-foreground">
                {card.description}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Performance Metrics */}
      {stats && (
        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <TrendingUp className="h-5 w-5 text-green-600" />
                <span>Review Performance</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Average Review Time</span>
                <Badge variant="outline">
                  {stats.avg_review_time ? `${stats.avg_review_time.toFixed(1)}h` : 'N/A'}
                </Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">False Positive Rate</span>
                <Badge 
                  variant={stats.false_positive_rate < 0.1 ? "default" : "destructive"}
                >
                  {stats.false_positive_rate ? `${(stats.false_positive_rate * 100).toFixed(1)}%` : 'N/A'}
                </Badge>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Users className="h-5 w-5 text-blue-600" />
                <span>System Health</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Review Queue Status</span>
                <Badge 
                  variant={stats.pending_review < 50 ? "default" : stats.pending_review < 100 ? "secondary" : "destructive"}
                >
                  {stats.pending_review < 50 ? 'Healthy' : stats.pending_review < 100 ? 'Moderate' : 'High Load'}
                </Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Critical Items</span>
                <Badge variant={stats.high_priority === 0 ? "default" : "destructive"}>
                  {stats.high_priority === 0 ? 'None' : `${stats.high_priority} Pending`}
                </Badge>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="pending">
            Pending Review
            {stats?.pending_review ? (
              <Badge variant="secondary" className="ml-2">
                {stats.pending_review}
              </Badge>
            ) : null}
          </TabsTrigger>
          <TabsTrigger value="high-priority">
            High Priority
            {stats?.high_priority ? (
              <Badge variant="destructive" className="ml-2">
                {stats.high_priority}
              </Badge>
            ) : null}
          </TabsTrigger>
          <TabsTrigger value="resolved">Resolved</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
              <CardDescription>
                Latest flagged content requiring attention
              </CardDescription>
            </CardHeader>
            <CardContent>
              <FlaggedContentTable 
                filters={{ limit: 10 }}
                onReviewClick={setSelectedContentId}
                compact={true}
              />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="pending">
          <Card>
            <CardHeader>
              <CardTitle>Pending Reviews</CardTitle>
              <CardDescription>
                Content items awaiting moderation review
              </CardDescription>
            </CardHeader>
            <CardContent>
              <FlaggedContentTable 
                filters={{ status: 'pending' }}
                onReviewClick={setSelectedContentId}
              />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="high-priority">
          <Card>
            <CardHeader>
              <CardTitle>High Priority Items</CardTitle>
              <CardDescription>
                Critical content requiring immediate attention
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
          <Card>
            <CardHeader>
              <CardTitle>Resolved Items</CardTitle>
              <CardDescription>
                Recently reviewed and resolved content
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