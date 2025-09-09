import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Legend
} from 'recharts';
import {
  Image,
  Type,
  Video,
  Mic,
  Zap,
  TrendingUp,
  Calendar,
  Activity
} from 'lucide-react';
import { billingAPI } from '../../services/billing.api';

interface UsageStats {
  total_credits_used: number;
  total_requests: number;
  usage_by_feature: Array<{
    feature_type: string;
    total_usage: number;
    request_count: number;
    avg_processing_time?: number;
  }>;
  period_days: number;
}

interface Subscription {
  tier: string;
  status: string;
  credits_remaining: number;
  credits_used: number;
  monthly_credits: number;
}

interface UsageRecord {
  id: number;
  feature_type: string;
  credits_consumed: number;
  api_endpoint: string;
  status: string;
  created_at: string;
}

interface Props {
  usageStats: UsageStats;
  subscription: Subscription;
}

const UsageDashboard: React.FC<Props> = ({ usageStats, subscription }) => {
  const [selectedPeriod, setSelectedPeriod] = useState('30');
  const [usageHistory, setUsageHistory] = useState<UsageRecord[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchUsageHistory();
  }, [selectedPeriod]);

  const fetchUsageHistory = async () => {
    try {
      setLoading(true);
      const data = await billingAPI.getUsageHistory({
        days: parseInt(selectedPeriod)
      });
      setUsageHistory(data.results || []);
    } catch (error) {
      console.error('Failed to fetch usage history:', error);
    } finally {
      setLoading(false);
    }
  };

  const getFeatureIcon = (featureType: string) => {
    switch (featureType) {
      case 'image_generation':
        return <Image className="h-4 w-4" />;
      case 'text_generation':
        return <Type className="h-4 w-4" />;
      case 'video_generation':
        return <Video className="h-4 w-4" />;
      case 'voice_transcription':
      case 'voice_generation':
        return <Mic className="h-4 w-4" />;
      default:
        return <Zap className="h-4 w-4" />;
    }
  };

  const getFeatureColor = (featureType: string) => {
    const colors = {
      image_generation: '#3b82f6', // blue
      text_generation: '#10b981', // emerald
      video_generation: '#8b5cf6', // violet
      voice_transcription: '#f59e0b', // amber
      voice_generation: '#ef4444', // red
      image_editing: '#06b6d4', // cyan
      batch_processing: '#84cc16', // lime
      api_call: '#6b7280' // gray
    };
    return colors[featureType as keyof typeof colors] || '#6b7280';
  };

  // Prepare data for charts
  const pieChartData = usageStats.usage_by_feature.map(feature => ({
    name: feature.feature_type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
    value: feature.total_usage,
    color: getFeatureColor(feature.feature_type)
  }));

  const barChartData = usageStats.usage_by_feature.map(feature => ({
    name: feature.feature_type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
    credits: feature.total_usage,
    requests: feature.request_count,
    avgTime: feature.avg_processing_time || 0
  }));

  // Calculate usage percentage
  const usagePercentage = subscription.monthly_credits > 0 
    ? (subscription.credits_used / subscription.monthly_credits) * 100 
    : 0;

  return (
    <div className="space-y-6">
      {/* Period Selection */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Usage Analytics</h2>
          <p className="text-muted-foreground">
            Track your API usage and credit consumption
          </p>
        </div>
        <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
          <SelectTrigger className="w-40">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="7">Last 7 days</SelectItem>
            <SelectItem value="30">Last 30 days</SelectItem>
            <SelectItem value="90">Last 90 days</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Credits</p>
                <p className="text-2xl font-bold">
                  {usageStats.total_credits_used.toLocaleString()}
                </p>
              </div>
              <TrendingUp className="h-8 w-8 text-blue-500" />
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Last {selectedPeriod} days
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">API Requests</p>
                <p className="text-2xl font-bold">
                  {usageStats.total_requests.toLocaleString()}
                </p>
              </div>
              <Activity className="h-8 w-8 text-green-500" />
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              {Math.round(usageStats.total_requests / parseInt(selectedPeriod))} per day avg
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Credits/Request</p>
                <p className="text-2xl font-bold">
                  {usageStats.total_requests > 0 
                    ? (usageStats.total_credits_used / usageStats.total_requests).toFixed(1)
                    : '0'
                  }
                </p>
              </div>
              <Zap className="h-8 w-8 text-purple-500" />
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Average efficiency
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Monthly Usage</p>
                <p className="text-2xl font-bold text-blue-600">
                  {usagePercentage.toFixed(1)}%
                </p>
              </div>
              <Calendar className="h-8 w-8 text-orange-500" />
            </div>
            <div className="mt-2">
              <Progress value={usagePercentage} className="h-1" />
              <p className="text-xs text-muted-foreground mt-1">
                {subscription.credits_remaining.toLocaleString()} remaining
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Usage by Feature - Bar Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Credits by Feature</CardTitle>
            <CardDescription>
              Credit consumption breakdown by feature type
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={barChartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="name" 
                  angle={-45}
                  textAnchor="end"
                  height={80}
                  fontSize={12}
                />
                <YAxis />
                <Tooltip />
                <Bar dataKey="credits" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Usage Distribution - Pie Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Usage Distribution</CardTitle>
            <CardDescription>
              Percentage breakdown of credit usage
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieChartData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {pieChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => [`${value} credits`, 'Usage']} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Feature Details */}
      <Card>
        <CardHeader>
          <CardTitle>Feature Usage Details</CardTitle>
          <CardDescription>
            Detailed breakdown of usage by feature
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {usageStats.usage_by_feature.map((feature) => {
              const percentage = usageStats.total_credits_used > 0 
                ? (feature.total_usage / usageStats.total_credits_used) * 100 
                : 0;
              
              return (
                <div key={feature.feature_type} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      {getFeatureIcon(feature.feature_type)}
                      <div>
                        <p className="font-medium">
                          {feature.feature_type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </p>
                        <p className="text-sm text-muted-foreground">
                          {feature.request_count} requests
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold">
                        {feature.total_usage.toLocaleString()} credits
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {percentage.toFixed(1)}% of total
                      </p>
                    </div>
                  </div>
                  <Progress 
                    value={percentage} 
                    className="h-2"
                    style={{
                      backgroundColor: `${getFeatureColor(feature.feature_type)}20`
                    }}
                  />
                  <div className="grid grid-cols-3 gap-4 text-xs text-muted-foreground">
                    <div>
                      Avg: {(feature.total_usage / feature.request_count).toFixed(1)} credits/request
                    </div>
                    {feature.avg_processing_time && (
                      <div>
                        Avg time: {feature.avg_processing_time.toFixed(0)}ms
                      </div>
                    )}
                    <div>
                      Usage rate: {((feature.request_count / parseInt(selectedPeriod)) * 7).toFixed(1)}/week
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Recent Usage Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>
            Your latest API usage and credit consumption
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center h-32">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {usageHistory.slice(0, 20).map((record) => (
                <div key={record.id} className="flex items-center justify-between p-2 border rounded">
                  <div className="flex items-center gap-3">
                    {getFeatureIcon(record.feature_type)}
                    <div>
                      <p className="font-medium text-sm">
                        {record.feature_type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {new Date(record.created_at).toLocaleString()}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge 
                      variant={record.status === 'success' ? 'default' : 'destructive'}
                      className="text-xs"
                    >
                      {record.status}
                    </Badge>
                    <span className="text-sm font-medium">
                      {record.credits_consumed} credits
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default UsageDashboard;