import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Crown,
  Zap,
  TrendingUp,
  Star,
  Check,
  X,
  AlertTriangle,
  CreditCard,
  Calendar,
  ArrowUp
} from 'lucide-react';
import { billingAPI } from '../../services/billing.api';
import { toast } from 'react-hot-toast';

interface PricingTier {
  id: number;
  name: string;
  tier_type: string;
  display_name: string;
  description: string;
  monthly_price: number;
  yearly_price: number;
  monthly_credits: number;
  features: Record<string, any>;
}

interface Subscription {
  tier: string;
  status: string;
  credits_remaining: number;
  credits_used: number;
  monthly_credits: number;
  current_period_end: string | null;
  cancel_at_period_end: boolean;
}

interface Props {
  subscription: Subscription;
  onUpdate: () => void;
}

const SubscriptionManager: React.FC<Props> = ({ subscription, onUpdate }) => {
  const [pricingTiers, setPricingTiers] = useState<PricingTier[]>([]);
  const [loading, setLoading] = useState(false);
  const [cancelDialogOpen, setCancelDialogOpen] = useState(false);
  const [upgradeDialogOpen, setUpgradeDialogOpen] = useState(false);
  const [selectedTier, setSelectedTier] = useState<PricingTier | null>(null);
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly');

  useEffect(() => {
    fetchPricingTiers();
  }, []);

  const fetchPricingTiers = async () => {
    try {
      const tiers = await billingAPI.getPricingTiers();
      setPricingTiers(tiers);
    } catch (error) {
      toast.error('Failed to load pricing tiers');
    }
  };

  const handleUpgrade = async (tier: PricingTier) => {
    try {
      setLoading(true);
      const checkoutData = await billingAPI.createCheckoutSession({
        type: 'subscription',
        tier_id: tier.id,
        billing_cycle: billingCycle
      });
      
      // Redirect to Stripe checkout
      window.location.href = checkoutData.checkout_url;
    } catch (error: any) {
      toast.error(error.message || 'Failed to start checkout process');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = async () => {
    try {
      setLoading(true);
      await billingAPI.cancelSubscription();
      toast.success('Subscription canceled successfully');
      setCancelDialogOpen(false);
      onUpdate();
    } catch (error: any) {
      toast.error(error.message || 'Failed to cancel subscription');
    } finally {
      setLoading(false);
    }
  };

  const handleReactivate = async () => {
    try {
      setLoading(true);
      await billingAPI.reactivateSubscription();
      toast.success('Subscription reactivated successfully');
      onUpdate();
    } catch (error: any) {
      toast.error(error.message || 'Failed to reactivate subscription');
    } finally {
      setLoading(false);
    }
  };

  const getTierIcon = (tierType: string) => {
    switch (tierType) {
      case 'free':
        return <Zap className="h-6 w-6 text-gray-500" />;
      case 'starter':
        return <TrendingUp className="h-6 w-6 text-blue-500" />;
      case 'professional':
        return <Crown className="h-6 w-6 text-purple-500" />;
      case 'enterprise':
        return <Star className="h-6 w-6 text-gold-500" />;
      default:
        return <Zap className="h-6 w-6" />;
    }
  };

  const getYearlySavings = (monthlyPrice: number, yearlyPrice: number) => {
    const monthlyCost = monthlyPrice * 12;
    const savings = monthlyCost - yearlyPrice;
    const percentage = (savings / monthlyCost) * 100;
    return { amount: savings, percentage: Math.round(percentage) };
  };

  const currentTier = pricingTiers.find(t => t.tier_type === subscription.tier.toLowerCase());
  const isFreePlan = subscription.tier.toLowerCase() === 'free';

  return (
    <div className="space-y-6">
      {/* Current Subscription */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {getTierIcon(subscription.tier.toLowerCase())}
              Current Subscription
            </div>
            <Badge variant={subscription.status === 'active' ? 'default' : 'secondary'}>
              {subscription.status}
            </Badge>
          </CardTitle>
          <CardDescription>
            Manage your current subscription plan
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h3 className="text-lg font-semibold">{subscription.tier} Plan</h3>
            <p className="text-muted-foreground">
              {subscription.monthly_credits.toLocaleString()} credits per month
            </p>
          </div>

          {subscription.current_period_end && (
            <div className="flex items-center gap-2 text-sm">
              <Calendar className="h-4 w-4" />
              <span>
                {subscription.cancel_at_period_end ? 'Cancels on' : 'Renews on'}{' '}
                {new Date(subscription.current_period_end).toLocaleDateString()}
              </span>
            </div>
          )}

          {subscription.cancel_at_period_end && (
            <Alert>
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                Your subscription will be canceled at the end of the current billing period.
                You'll continue to have access until then.
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
        <CardFooter className="flex gap-2">
          {!isFreePlan && subscription.status === 'active' && !subscription.cancel_at_period_end && (
            <Dialog open={cancelDialogOpen} onOpenChange={setCancelDialogOpen}>
              <DialogTrigger asChild>
                <Button variant="outline">Cancel Subscription</Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Cancel Subscription</DialogTitle>
                  <DialogDescription>
                    Are you sure you want to cancel your subscription? You'll continue to have access
                    until the end of your current billing period.
                  </DialogDescription>
                </DialogHeader>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setCancelDialogOpen(false)}>
                    Keep Subscription
                  </Button>
                  <Button 
                    variant="destructive" 
                    onClick={handleCancel}
                    disabled={loading}
                  >
                    Cancel Subscription
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          )}

          {subscription.cancel_at_period_end && (
            <Button onClick={handleReactivate} disabled={loading}>
              Reactivate Subscription
            </Button>
          )}

          <Dialog open={upgradeDialogOpen} onOpenChange={setUpgradeDialogOpen}>
            <DialogTrigger asChild>
              <Button className="flex items-center gap-2">
                <ArrowUp className="h-4 w-4" />
                {isFreePlan ? 'Upgrade Plan' : 'Change Plan'}
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>Choose Your Plan</DialogTitle>
                <DialogDescription>
                  Select the plan that best fits your needs
                </DialogDescription>
              </DialogHeader>
              
              <div className="space-y-4">
                {/* Billing Cycle Toggle */}
                <div className="flex items-center justify-center gap-4">
                  <span className={billingCycle === 'monthly' ? 'font-semibold' : 'text-muted-foreground'}>
                    Monthly
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setBillingCycle(billingCycle === 'monthly' ? 'yearly' : 'monthly')}
                  >
                    {billingCycle === 'monthly' ? 'Switch to Yearly' : 'Switch to Monthly'}
                  </Button>
                  <span className={billingCycle === 'yearly' ? 'font-semibold' : 'text-muted-foreground'}>
                    Yearly
                  </span>
                  {billingCycle === 'yearly' && (
                    <Badge variant="secondary">Save up to 20%</Badge>
                  )}
                </div>

                {/* Pricing Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {pricingTiers.map((tier) => {
                    const price = billingCycle === 'yearly' ? tier.yearly_price : tier.monthly_price;
                    const isCurrentTier = tier.tier_type === subscription.tier.toLowerCase();
                    const savings = getYearlySavings(tier.monthly_price, tier.yearly_price);

                    return (
                      <Card 
                        key={tier.id} 
                        className={`relative ${isCurrentTier ? 'ring-2 ring-blue-500' : ''}`}
                      >
                        {tier.tier_type === 'professional' && (
                          <Badge className="absolute -top-2 left-1/2 transform -translate-x-1/2">
                            Most Popular
                          </Badge>
                        )}
                        
                        <CardHeader className="text-center">
                          <div className="flex justify-center mb-2">
                            {getTierIcon(tier.tier_type)}
                          </div>
                          <CardTitle>{tier.display_name}</CardTitle>
                          <CardDescription>{tier.description}</CardDescription>
                          <div className="text-3xl font-bold">
                            ${price}
                            <span className="text-base font-normal text-muted-foreground">
                              /{billingCycle === 'yearly' ? 'year' : 'month'}
                            </span>
                          </div>
                          {billingCycle === 'yearly' && savings.amount > 0 && (
                            <p className="text-sm text-green-600">
                              Save ${savings.amount} ({savings.percentage}%)
                            </p>
                          )}
                        </CardHeader>

                        <CardContent className="space-y-2">
                          <div className="flex items-center gap-2">
                            <Check className="h-4 w-4 text-green-500" />
                            <span className="text-sm">
                              {tier.monthly_credits.toLocaleString()} credits/month
                            </span>
                          </div>
                          
                          {/* Feature list based on tier.features */}
                          {Object.entries(tier.features || {}).map(([feature, enabled]) => (
                            <div key={feature} className="flex items-center gap-2">
                              {enabled ? (
                                <Check className="h-4 w-4 text-green-500" />
                              ) : (
                                <X className="h-4 w-4 text-gray-400" />
                              )}
                              <span className={`text-sm ${enabled ? '' : 'text-muted-foreground'}`}>
                                {feature.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                              </span>
                            </div>
                          ))}
                        </CardContent>

                        <CardFooter>
                          {isCurrentTier ? (
                            <Button variant="outline" disabled className="w-full">
                              Current Plan
                            </Button>
                          ) : (
                            <Button
                              className="w-full"
                              onClick={() => {
                                setSelectedTier(tier);
                                handleUpgrade(tier);
                              }}
                              disabled={loading}
                            >
                              {tier.tier_type === 'free' ? 'Downgrade' : 'Upgrade'}
                            </Button>
                          )}
                        </CardFooter>
                      </Card>
                    );
                  })}
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </CardFooter>
      </Card>

      {/* Billing Portal */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CreditCard className="h-5 w-5" />
            Billing Management
          </CardTitle>
          <CardDescription>
            Manage your billing information, payment methods, and invoices
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-4">
            Access Stripe's secure billing portal to update your payment information,
            download invoices, and manage your subscription details.
          </p>
        </CardContent>
        <CardFooter>
          <Button
            variant="outline"
            onClick={async () => {
              try {
                setLoading(true);
                const { portal_url } = await billingAPI.createBillingPortalSession();
                window.open(portal_url, '_blank');
              } catch (error: any) {
                toast.error('Failed to open billing portal');
              } finally {
                setLoading(false);
              }
            }}
            disabled={loading || isFreePlan}
          >
            <CreditCard className="h-4 w-4 mr-2" />
            Open Billing Portal
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
};

export default SubscriptionManager;