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
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
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
  DollarSign,
  Users,
  TrendingUp,
  CreditCard,
  Calendar,
  Activity,
  Crown,
  Zap,
  Star
} from 'lucide-react';
import { billingAPI } from '../../services/billing.api';
import { toast } from 'react-hot-toast';

interface AdminDashboardData {
  revenue_stats: {
    active_subscriptions: number;
    subscription_revenue: number;
    credit_revenue: number;
    total_revenue: number;
    total_credits_consumed: number;
    total_api_requests: number;
    period_days: number;
  };
  tier_distribution: Array<{
    pricing_tier__tier_type: string;
    pricing_tier__display_name: string;
    user_count: number;
  }>;
  period_days: number;
}

interface AdminUser {
  id: number;
  username: string;
  email: string;
  date_joined: string;
  last_login: string | null;
  subscription_status: string;
  tier: string;
  credits_remaining: number;
  current_period_end: string | null;
}

const RevenueDashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<AdminDashboardData | null>(null);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState('30');
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchDashboardData();
    fetchUsers();
  }, [selectedPeriod]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const data = await billingAPI.getAdminDashboard(parseInt(selectedPeriod));
      setDashboardData(data);
    } catch (error) {
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    try {
      const userData = await billingAPI.getAdminUsers();
      setUsers(userData);
    } catch (error) {
      toast.error('Failed to load user data');
    }
  };

  const getTierIcon = (tierType: string) => {
    switch (tierType) {
      case 'free':
        return <Zap className="h-4 w-4 text-muted-foreground" />;
      case 'starter':
        return <TrendingUp className="h-4 w-4 text-blue-500" />;
      case 'professional':
        return <Crown className="h-4 w-4 text-purple-500" />;
      case 'enterprise':
        return <Star className="h-4 w-4 text-gold-500" />;
      default:
        return <Zap className="h-4 w-4" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      active: { variant: 'default' as const, text: 'Active' },
      free: { variant: 'secondary' as const, text: 'Free' },
      past_due: { variant: 'destructive' as const, text: 'Past Due' },
      canceled: { variant: 'outline' as const, text: 'Canceled' },
      trialing: { variant: 'default' as const, text: 'Trial' },
    };

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.active;
    return <Badge variant={config.variant}>{config.text}</Badge>;
  };

  if (loading || !dashboardData) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const { revenue_stats, tier_distribution } = dashboardData;

  // Prepare chart data
  const tierChartData = tier_distribution.map(tier => ({
    name: tier.pricing_tier__display_name,
    users: tier.user_count,
    percentage: (tier.user_count / tier_distribution.reduce((sum, t) => sum + t.user_count, 0)) * 100
  }));

  const revenueBreakdown = [
    {
      name: 'Subscriptions',
      value: revenue_stats.subscription_revenue,
      color: '#3b82f6'
    },
    {
      name: 'Credits',
      value: revenue_stats.credit_revenue,
      color: '#10b981'
    }
  ];

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Revenue Dashboard</h1>
          <p className="text-muted-foreground">
            Monitor subscription revenue and user analytics
          </p>
        </div>
        <div className="flex items-center gap-4">
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
      </div>

      {/* Revenue Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Revenue</p>
                <p className="text-2xl font-bold text-green-600">
                  {formatCurrency(revenue_stats.total_revenue)}
                </p>
              </div>
              <DollarSign className="h-8 w-8 text-green-500" />
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
                <p className="text-sm text-muted-foreground">Active Subscriptions</p>
                <p className="text-2xl font-bold">
                  {revenue_stats.active_subscriptions.toLocaleString()}
                </p>
              </div>
              <Users className="h-8 w-8 text-blue-500" />
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Paying customers
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Subscription Revenue</p>
                <p className="text-2xl font-bold text-blue-600">
                  {formatCurrency(revenue_stats.subscription_revenue)}
                </p>
              </div>
              <CreditCard className="h-8 w-8 text-blue-500" />
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              {((revenue_stats.subscription_revenue / revenue_stats.total_revenue) * 100).toFixed(1)}% of total
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Credit Revenue</p>
                <p className="text-2xl font-bold text-purple-600">
                  {formatCurrency(revenue_stats.credit_revenue)}
                </p>
              </div>
              <Zap className="h-8 w-8 text-purple-500" />
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              {((revenue_stats.credit_revenue / revenue_stats.total_revenue) * 100).toFixed(1)}% of total
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Usage Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Credits Consumed</p>
                <p className="text-2xl font-bold">
                  {revenue_stats.total_credits_consumed.toLocaleString()}
                </p>
              </div>
              <Activity className="h-8 w-8 text-orange-500" />
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Platform usage
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">API Requests</p>
                <p className="text-2xl font-bold">
                  {revenue_stats.total_api_requests.toLocaleString()}
                </p>
              </div>
              <TrendingUp className="h-8 w-8 text-indigo-500" />
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              {Math.round(revenue_stats.total_api_requests / parseInt(selectedPeriod))} per day avg
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Revenue Breakdown */}
        <Card>
          <CardHeader>
            <CardTitle>Revenue Breakdown</CardTitle>
            <CardDescription>
              Revenue sources for the last {selectedPeriod} days
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={revenueBreakdown}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {revenueBreakdown.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => [formatCurrency(Number(value)), 'Revenue']} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* User Distribution by Tier */}
        <Card>
          <CardHeader>
            <CardTitle>User Distribution</CardTitle>
            <CardDescription>
              Users across different pricing tiers
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={tierChartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="users" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Tier Statistics */}
      <Card>
        <CardHeader>
          <CardTitle>Tier Statistics</CardTitle>
          <CardDescription>
            Detailed breakdown of users by pricing tier
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {tier_distribution.map((tier) => (
              <div key={tier.pricing_tier__tier_type} className="p-4 border rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  {getTierIcon(tier.pricing_tier__tier_type)}
                  <h3 className="font-semibold">{tier.pricing_tier__display_name}</h3>
                </div>
                <p className="text-2xl font-bold">{tier.user_count}</p>
                <p className="text-sm text-muted-foreground">
                  {((tier.user_count / tier_distribution.reduce((sum, t) => sum + t.user_count, 0)) * 100).toFixed(1)}% of users
                </p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* User Management Table */}
      <Card>
        <CardHeader>
          <CardTitle>User Management</CardTitle>
          <CardDescription>
            Recent user activity and subscription status
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>User</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Tier</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Credits</TableHead>
                  <TableHead>Joined</TableHead>
                  <TableHead>Last Login</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {users.slice(0, 20).map((user) => (
                  <TableRow key={user.id}>
                    <TableCell className="font-medium">
                      {user.username}
                    </TableCell>
                    <TableCell className="text-sm">
                      {user.email}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        {getTierIcon(user.tier.toLowerCase())}
                        <span className="capitalize">{user.tier}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      {getStatusBadge(user.subscription_status)}
                    </TableCell>
                    <TableCell>
                      {user.credits_remaining.toLocaleString()}
                    </TableCell>
                    <TableCell className="text-sm">
                      {new Date(user.date_joined).toLocaleDateString()}
                    </TableCell>
                    <TableCell className="text-sm">
                      {user.last_login 
                        ? new Date(user.last_login).toLocaleDateString()
                        : 'Never'
                      }
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
          {users.length > 20 && (
            <div className="mt-4 text-center">
              <p className="text-sm text-muted-foreground">
                Showing first 20 users of {users.length} total
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default RevenueDashboard;