import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  CreditCard,
  Calendar,
  BarChart3,
  Settings,
  Crown,
  Zap,
  AlertTriangle,
  CheckCircle,
  TrendingUp
} from 'lucide-react';
import SubscriptionManager from './SubscriptionManager';
import UsageDashboard from './UsageDashboard';
import PaymentMethods from './PaymentMethods';
import InvoiceHistory from './InvoiceHistory';
import { billingAPI } from '../../services/billing.api';
import { useAuthStore } from '../../store/authStore';

interface BillingData {
  subscription: {
    tier: string;
    status: string;
    credits_remaining: number;
    credits_used: number;
    monthly_credits: number;
    current_period_end: string | null;
    cancel_at_period_end: boolean;
  };
  usage_stats: {
    total_credits_used: number;
    total_requests: number;
    usage_by_feature: Array<{
      feature_type: string;
      total_usage: number;
      request_count: number;
    }>;
  };
  recent_invoices: Array<{
    id: number;
    invoice_number: string;
    total_amount: number;
    status: string;
    created_at: string;
  }>;
}

const BillingDashboard: React.FC = () => {
  const [billingData, setBillingData] = useState<BillingData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('overview');
  const { user } = useAuthStore();

  useEffect(() => {
    fetchBillingData();
  }, []);

  const fetchBillingData = async () => {
    try {
      setLoading(true);
      const data = await billingAPI.getBillingSummary();
      setBillingData(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load billing data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !billingData) {
    return (
      <Alert className="m-4">
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>
          {error || 'Failed to load billing information'}
        </AlertDescription>
      </Alert>
    );
  }

  const { subscription, usage_stats, recent_invoices } = billingData;
  const usagePercentage = subscription.monthly_credits > 0 
    ? (subscription.credits_used / subscription.monthly_credits) * 100 
    : 0;

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      active: { variant: 'default' as const, icon: CheckCircle, text: 'Active' },
      free: { variant: 'secondary' as const, icon: Zap, text: 'Free Plan' },
      past_due: { variant: 'destructive' as const, icon: AlertTriangle, text: 'Past Due' },
      canceled: { variant: 'outline' as const, icon: AlertTriangle, text: 'Canceled' },
    };

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.active;
    const Icon = config.icon;

    return (
      <Badge variant={config.variant} className="flex items-center gap-1">
        <Icon className="h-3 w-3" />
        {config.text}
      </Badge>
    );
  };

  const getTierIcon = (tier: string) => {
    switch (tier.toLowerCase()) {
      case 'free':
        return <Zap className="h-5 w-5 text-gray-500" />;
      case 'starter':
        return <TrendingUp className="h-5 w-5 text-blue-500" />;
      case 'professional':
        return <Crown className="h-5 w-5 text-purple-500" />;
      case 'enterprise':
        return <Crown className="h-5 w-5 text-gold-500" />;
      default:
        return <Zap className="h-5 w-5" />;
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Billing & Usage</h1>
          <p className="text-muted-foreground">
            Manage your subscription, view usage, and track billing
          </p>
        </div>
        <div className="flex items-center gap-2">
          {getTierIcon(subscription.tier)}
          <span className="font-semibold">{subscription.tier}</span>
          {getStatusBadge(subscription.status)}
        </div>
      </div>

      {/* Quick Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Credits Remaining</p>
                <p className="text-2xl font-bold text-blue-600">
                  {subscription.credits_remaining.toLocaleString()}
                </p>
              </div>
              <Zap className="h-8 w-8 text-blue-500" />
            </div>
            <div className="mt-2">
              <Progress value={100 - usagePercentage} className="h-1" />
              <p className="text-xs text-muted-foreground mt-1">
                {subscription.monthly_credits.toLocaleString()} monthly limit
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Usage This Month</p>
                <p className="text-2xl font-bold">
                  {subscription.credits_used.toLocaleString()}
                </p>
              </div>
              <BarChart3 className="h-8 w-8 text-green-500" />
            </div>
            <div className="mt-2">
              <Progress value={usagePercentage} className="h-1" />
              <p className="text-xs text-muted-foreground mt-1">
                {usagePercentage.toFixed(1)}% of monthly limit
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">API Requests</p>
                <p className="text-2xl font-bold">
                  {usage_stats.total_requests.toLocaleString()}
                </p>
              </div>
              <TrendingUp className="h-8 w-8 text-purple-500" />
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Last 30 days
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Next Billing</p>
                <p className="text-sm font-semibold">
                  {subscription.current_period_end 
                    ? new Date(subscription.current_period_end).toLocaleDateString()
                    : 'N/A'
                  }
                </p>
              </div>
              <Calendar className="h-8 w-8 text-orange-500" />
            </div>
            {subscription.cancel_at_period_end && (
              <Badge variant="destructive" className="text-xs mt-2">
                Cancels at period end
              </Badge>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Usage Warning */}
      {usagePercentage > 80 && (
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            You've used {usagePercentage.toFixed(1)}% of your monthly credits. 
            Consider upgrading your plan to avoid interruptions.
          </AlertDescription>
        </Alert>
      )}

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="subscription">Subscription</TabsTrigger>
          <TabsTrigger value="usage">Usage</TabsTrigger>
          <TabsTrigger value="payment">Payment</TabsTrigger>
          <TabsTrigger value="invoices">Invoices</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Current Plan */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  {getTierIcon(subscription.tier)}
                  Current Plan
                </CardTitle>
                <CardDescription>
                  Your subscription details and benefits
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <p className="font-semibold text-lg">{subscription.tier} Plan</p>
                    <p className="text-sm text-muted-foreground">
                      {subscription.monthly_credits.toLocaleString()} credits per month
                    </p>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Credits Used</span>
                      <span>{subscription.credits_used.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Credits Remaining</span>
                      <span className="font-semibold text-blue-600">
                        {subscription.credits_remaining.toLocaleString()}
                      </span>
                    </div>
                    <Progress value={usagePercentage} className="h-2" />
                  </div>
                </div>
              </CardContent>
              <CardFooter>
                <Button 
                  onClick={() => setActiveTab('subscription')}
                  className="w-full"
                >
                  Manage Subscription
                </Button>
              </CardFooter>
            </Card>

            {/* Recent Activity */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Usage</CardTitle>
                <CardDescription>
                  Your top features by usage this month
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {usage_stats.usage_by_feature.slice(0, 5).map((feature, index) => (
                    <div key={feature.feature_type} className="flex justify-between items-center">
                      <div>
                        <p className="font-medium text-sm">
                          {feature.feature_type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {feature.request_count} requests
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold text-sm">
                          {feature.total_usage} credits
                        </p>
                        <div className="w-20 bg-gray-200 rounded-full h-1">
                          <div
                            className="bg-blue-500 h-1 rounded-full"
                            style={{
                              width: `${(feature.total_usage / Math.max(...usage_stats.usage_by_feature.map(f => f.total_usage))) * 100}%`
                            }}
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
              <CardFooter>
                <Button 
                  variant="outline" 
                  onClick={() => setActiveTab('usage')}
                  className="w-full"
                >
                  View Detailed Usage
                </Button>
              </CardFooter>
            </Card>
          </div>

          {/* Recent Invoices */}
          {recent_invoices.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Recent Invoices</CardTitle>
                <CardDescription>
                  Your latest billing history
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {recent_invoices.slice(0, 3).map((invoice) => (
                    <div key={invoice.id} className="flex justify-between items-center p-3 border rounded-lg">
                      <div>
                        <p className="font-medium">{invoice.invoice_number}</p>
                        <p className="text-sm text-muted-foreground">
                          {new Date(invoice.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold">${invoice.total_amount.toFixed(2)}</p>
                        <Badge 
                          variant={invoice.status === 'paid' ? 'default' : 'secondary'}
                          className="text-xs"
                        >
                          {invoice.status}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
              <CardFooter>
                <Button 
                  variant="outline" 
                  onClick={() => setActiveTab('invoices')}
                  className="w-full"
                >
                  View All Invoices
                </Button>
              </CardFooter>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="subscription">
          <SubscriptionManager 
            subscription={subscription} 
            onUpdate={fetchBillingData}
          />
        </TabsContent>

        <TabsContent value="usage">
          <UsageDashboard 
            usageStats={usage_stats ? { ...usage_stats, period_days: 30 } : undefined}
            subscription={subscription}
          />
        </TabsContent>

        <TabsContent value="payment">
          <PaymentMethods onUpdate={fetchBillingData} />
        </TabsContent>

        <TabsContent value="invoices">
          <InvoiceHistory invoices={recent_invoices} />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default BillingDashboard;