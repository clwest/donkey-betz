import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { billingApi } from '@/lib/api'
import { cn } from '@/lib/cn'
import {
  CreditCard,
  Receipt,
  Crown,
  Check,
  Plus,
  Trash2,
  Star,
  Loader2,
  ExternalLink,
  AlertTriangle,
  Calendar,
  DollarSign,
  Zap,
  Shield,
  Download,
} from 'lucide-react'

// Types
interface Subscription {
  id?: string
  status: 'active' | 'canceled' | 'past_due' | 'trialing' | 'incomplete' | 'none'
  plan_id?: string
  plan_name?: string
  price?: number
  interval?: 'month' | 'year'
  current_period_start?: string
  current_period_end?: string
  cancel_at_period_end?: boolean
  trial_end?: string
}

interface Plan {
  id: string
  name: string
  description?: string
  price: number
  interval: 'month' | 'year'
  features?: string[]
  is_popular?: boolean
  is_current?: boolean
}

interface PaymentMethod {
  id: string
  type: 'card' | 'bank_account' | 'paypal'
  brand?: string
  last4?: string
  exp_month?: number
  exp_year?: number
  is_default?: boolean
}

interface Invoice {
  id: string
  number?: string
  status: 'paid' | 'open' | 'draft' | 'void' | 'uncollectible'
  amount_due: number
  amount_paid?: number
  currency?: string
  created?: string
  due_date?: string
  pdf_url?: string
  description?: string
}

interface Usage {
  api_calls?: number
  api_limit?: number
  storage_used?: number
  storage_limit?: number
  tokens_used?: number
  tokens_limit?: number
}

type TabType = 'subscription' | 'payment-methods' | 'invoices' | 'usage'

export default function BillingPage() {
  const [activeTab, setActiveTab] = useState<TabType>('subscription')
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null)
  const queryClient = useQueryClient()

  // Queries
  const { data: subscriptionData, isLoading: loadingSubscription } = useQuery({
    queryKey: ['billing-subscription'],
    queryFn: () => billingApi.subscriptionStatus(),
  })

  const { data: plansData, isLoading: loadingPlans } = useQuery({
    queryKey: ['billing-plans'],
    queryFn: () => billingApi.subscriptionPlans(),
    enabled: activeTab === 'subscription',
  })

  const { data: paymentMethodsData, isLoading: loadingPaymentMethods } = useQuery({
    queryKey: ['billing-payment-methods'],
    queryFn: () => billingApi.paymentMethods(),
    enabled: activeTab === 'payment-methods',
  })

  const { data: invoicesData, isLoading: loadingInvoices } = useQuery({
    queryKey: ['billing-invoices'],
    queryFn: () => billingApi.invoices({ limit: 20 }),
    enabled: activeTab === 'invoices',
  })

  const { data: upcomingData } = useQuery({
    queryKey: ['billing-upcoming'],
    queryFn: () => billingApi.upcomingInvoice(),
    enabled: activeTab === 'invoices',
  })

  const { data: usageData, isLoading: loadingUsage } = useQuery({
    queryKey: ['billing-usage'],
    queryFn: () => billingApi.usage(),
    enabled: activeTab === 'usage',
  })

  // Mutations
  const subscribeMutation = useMutation({
    mutationFn: (planId: string) => billingApi.subscribe({ plan_id: planId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['billing-subscription'] })
      setSelectedPlan(null)
    },
  })

  const cancelMutation = useMutation({
    mutationFn: () => billingApi.cancelSubscription(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['billing-subscription'] })
    },
  })

  const resumeMutation = useMutation({
    mutationFn: () => billingApi.resumeSubscription(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['billing-subscription'] })
    },
  })

  const removePaymentMethodMutation = useMutation({
    mutationFn: (id: string) => billingApi.removePaymentMethod(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['billing-payment-methods'] })
    },
  })

  const setDefaultMutation = useMutation({
    mutationFn: (id: string) => billingApi.setDefaultPaymentMethod(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['billing-payment-methods'] })
    },
  })

  const billingPortalMutation = useMutation({
    mutationFn: () => billingApi.billingPortal(),
    onSuccess: (data) => {
      if (data?.data?.url) {
        window.open(data.data.url, '_blank')
      }
    },
  })

  // Data extraction
  const subscription: Subscription = subscriptionData?.data || { status: 'none' }
  const rawPlans = plansData?.data?.plans || plansData?.data
  const plans: Plan[] = Array.isArray(rawPlans) ? rawPlans : []
  const rawPaymentMethods = paymentMethodsData?.data?.payment_methods || paymentMethodsData?.data
  const paymentMethods: PaymentMethod[] = Array.isArray(rawPaymentMethods) ? rawPaymentMethods : []
  const rawInvoices = invoicesData?.data?.invoices || invoicesData?.data
  const invoices: Invoice[] = Array.isArray(rawInvoices) ? rawInvoices : []
  const upcoming: Invoice | null = upcomingData?.data || null
  const usage: Usage = usageData?.data || {}

  const tabs = [
    { id: 'subscription' as TabType, label: 'Subscription', icon: Crown },
    { id: 'payment-methods' as TabType, label: 'Payment Methods', icon: CreditCard },
    { id: 'invoices' as TabType, label: 'Invoices', icon: Receipt },
    { id: 'usage' as TabType, label: 'Usage', icon: Zap },
  ]

  const formatCurrency = (amount?: number, currency = 'USD') => {
    if (amount === undefined || amount === null) return '$0.00'
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency,
    }).format(amount / 100) // Stripe amounts are in cents
  }

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return '—'
    return new Date(dateStr).toLocaleDateString()
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
      case 'trialing':
      case 'paid':
        return 'text-accent-green'
      case 'past_due':
      case 'incomplete':
      case 'open':
        return 'text-yellow-400'
      case 'canceled':
      case 'void':
      case 'uncollectible':
        return 'text-red-400'
      default:
        return 'text-gray-400'
    }
  }

  const getCardBrandIcon = (_brand?: string) => {
    // In a real app, you'd use brand-specific icons
    return <CreditCard className="h-6 w-6" />
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-yellow-500/20">
            <CreditCard className="h-6 w-6 text-yellow-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">Billing & Subscription</h1>
            <p className="text-gray-400">Manage your subscription and payment methods</p>
          </div>
        </div>

        <button
          onClick={() => billingPortalMutation.mutate()}
          disabled={billingPortalMutation.isPending}
          className="btn-secondary flex items-center gap-2"
        >
          <ExternalLink className="h-4 w-4" />
          Stripe Portal
        </button>
      </div>

      {/* Current Plan Banner */}
      {subscription.status !== 'none' && (
        <div className={cn(
          'card p-4 flex items-center justify-between',
          subscription.status === 'active' && 'border-accent-green/30',
          subscription.cancel_at_period_end && 'border-yellow-500/30'
        )}>
          <div className="flex items-center gap-4">
            <div className={cn(
              'p-3 rounded-lg',
              subscription.status === 'active' ? 'bg-accent-green/20' : 'bg-yellow-500/20'
            )}>
              <Crown className={cn(
                'h-6 w-6',
                subscription.status === 'active' ? 'text-accent-green' : 'text-yellow-400'
              )} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-semibold">{subscription.plan_name || 'Current Plan'}</h3>
                <span className={cn('text-xs px-2 py-0.5 rounded capitalize', getStatusColor(subscription.status))}>
                  {subscription.status}
                </span>
              </div>
              <p className="text-sm text-gray-400">
                {subscription.cancel_at_period_end ? (
                  <>Cancels on {formatDate(subscription.current_period_end)}</>
                ) : (
                  <>Renews on {formatDate(subscription.current_period_end)}</>
                )}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="text-right">
              <p className="text-2xl font-bold">
                {formatCurrency(subscription.price)}
                <span className="text-sm text-gray-400">/{subscription.interval || 'mo'}</span>
              </p>
            </div>
            {subscription.cancel_at_period_end ? (
              <button
                onClick={() => resumeMutation.mutate()}
                disabled={resumeMutation.isPending}
                className="btn-primary"
              >
                Resume
              </button>
            ) : (
              <button
                onClick={() => cancelMutation.mutate()}
                disabled={cancelMutation.isPending}
                className="btn-secondary text-red-400 hover:text-red-300"
              >
                Cancel
              </button>
            )}
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-2 border-b border-dark-border pb-2">
        {tabs.map((tab) => {
          const Icon = tab.icon
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                'flex items-center gap-2 px-4 py-2 rounded-t-lg transition-colors',
                activeTab === tab.id
                  ? 'bg-dark-card text-white border-b-2 border-primary-500'
                  : 'text-gray-400 hover:text-white hover:bg-dark-card/50'
              )}
            >
              <Icon className="h-4 w-4" />
              <span>{tab.label}</span>
            </button>
          )
        })}
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        {/* Subscription Tab */}
        {activeTab === 'subscription' && (
          <div className="space-y-6">
            <h2 className="text-lg font-semibold">Available Plans</h2>

            {loadingPlans || loadingSubscription ? (
              <div className="flex justify-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
              </div>
            ) : plans.length === 0 ? (
              <div className="text-center py-12">
                <Crown className="h-12 w-12 text-gray-600 mx-auto mb-3" />
                <p className="text-gray-400">No plans available</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {plans.map((plan) => (
                  <div
                    key={plan.id}
                    className={cn(
                      'card p-6 relative',
                      plan.is_popular && 'border-primary-500',
                      plan.is_current && 'border-accent-green'
                    )}
                  >
                    {plan.is_popular && (
                      <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                        <span className="px-3 py-1 text-xs rounded-full bg-primary-600">
                          Most Popular
                        </span>
                      </div>
                    )}
                    {plan.is_current && (
                      <div className="absolute -top-3 right-4">
                        <span className="px-3 py-1 text-xs rounded-full bg-accent-green text-black">
                          Current
                        </span>
                      </div>
                    )}

                    <h3 className="text-xl font-bold mb-2">{plan.name}</h3>
                    {plan.description && (
                      <p className="text-sm text-gray-400 mb-4">{plan.description}</p>
                    )}

                    <div className="mb-6">
                      <span className="text-4xl font-bold">{formatCurrency(plan.price)}</span>
                      <span className="text-gray-400">/{plan.interval}</span>
                    </div>

                    {plan.features && plan.features.length > 0 && (
                      <ul className="space-y-2 mb-6">
                        {plan.features.map((feature, idx) => (
                          <li key={idx} className="flex items-center gap-2 text-sm">
                            <Check className="h-4 w-4 text-accent-green" />
                            <span>{feature}</span>
                          </li>
                        ))}
                      </ul>
                    )}

                    <button
                      onClick={() => {
                        setSelectedPlan(plan.id)
                        subscribeMutation.mutate(plan.id)
                      }}
                      disabled={plan.is_current || subscribeMutation.isPending}
                      className={cn(
                        'w-full py-2 rounded transition-colors',
                        plan.is_current
                          ? 'bg-dark-bg text-gray-500 cursor-not-allowed'
                          : plan.is_popular
                          ? 'btn-primary'
                          : 'btn-secondary'
                      )}
                    >
                      {plan.is_current ? 'Current Plan' : selectedPlan === plan.id && subscribeMutation.isPending ? 'Processing...' : 'Select Plan'}
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Payment Methods Tab */}
        {activeTab === 'payment-methods' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">Payment Methods</h2>
              <button className="btn-primary flex items-center gap-2">
                <Plus className="h-4 w-4" />
                Add Payment Method
              </button>
            </div>

            {loadingPaymentMethods ? (
              <div className="flex justify-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
              </div>
            ) : paymentMethods.length === 0 ? (
              <div className="text-center py-12">
                <CreditCard className="h-12 w-12 text-gray-600 mx-auto mb-3" />
                <p className="text-gray-400">No payment methods on file</p>
                <p className="text-sm text-gray-500 mb-4">Add a card to manage your subscription</p>
                <button className="btn-primary">Add Payment Method</button>
              </div>
            ) : (
              <div className="space-y-3">
                {paymentMethods.map((method) => (
                  <div key={method.id} className="card p-4 flex items-center gap-4">
                    <div className="p-3 rounded-lg bg-dark-bg">
                      {getCardBrandIcon(method.brand)}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium capitalize">{method.brand || method.type}</span>
                        {method.is_default && (
                          <span className="px-2 py-0.5 text-xs rounded bg-primary-600">Default</span>
                        )}
                      </div>
                      <p className="text-sm text-gray-400">
                        •••• {method.last4}
                        {method.exp_month && method.exp_year && (
                          <> • Expires {method.exp_month}/{method.exp_year}</>
                        )}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      {!method.is_default && (
                        <button
                          onClick={() => setDefaultMutation.mutate(method.id)}
                          disabled={setDefaultMutation.isPending}
                          className="p-2 rounded hover:bg-dark-bg text-gray-400 hover:text-white"
                          title="Set as default"
                        >
                          <Star className="h-4 w-4" />
                        </button>
                      )}
                      <button
                        onClick={() => removePaymentMethodMutation.mutate(method.id)}
                        disabled={removePaymentMethodMutation.isPending || method.is_default}
                        className={cn(
                          'p-2 rounded hover:bg-dark-bg',
                          method.is_default ? 'text-gray-600' : 'text-red-400'
                        )}
                        title={method.is_default ? 'Cannot remove default' : 'Remove'}
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Invoices Tab */}
        {activeTab === 'invoices' && (
          <div className="space-y-6">
            {/* Upcoming Invoice */}
            {upcoming && (
              <div className="card p-4 border-blue-500/30">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-blue-500/20">
                      <Calendar className="h-5 w-5 text-blue-400" />
                    </div>
                    <div>
                      <h3 className="font-medium">Upcoming Invoice</h3>
                      <p className="text-sm text-gray-400">
                        Due {formatDate(upcoming.due_date)}
                      </p>
                    </div>
                  </div>
                  <span className="text-xl font-bold">
                    {formatCurrency(upcoming.amount_due, upcoming.currency)}
                  </span>
                </div>
              </div>
            )}

            <h2 className="text-lg font-semibold">Invoice History</h2>

            {loadingInvoices ? (
              <div className="flex justify-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
              </div>
            ) : invoices.length === 0 ? (
              <div className="text-center py-12">
                <Receipt className="h-12 w-12 text-gray-600 mx-auto mb-3" />
                <p className="text-gray-400">No invoices yet</p>
              </div>
            ) : (
              <div className="card overflow-hidden">
                <table className="w-full">
                  <thead className="bg-dark-bg">
                    <tr>
                      <th className="text-left p-4 text-sm font-medium text-gray-400">Invoice</th>
                      <th className="text-left p-4 text-sm font-medium text-gray-400">Date</th>
                      <th className="text-left p-4 text-sm font-medium text-gray-400">Amount</th>
                      <th className="text-left p-4 text-sm font-medium text-gray-400">Status</th>
                      <th className="text-right p-4 text-sm font-medium text-gray-400">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-dark-border">
                    {invoices.map((invoice) => (
                      <tr key={invoice.id} className="hover:bg-dark-bg/50">
                        <td className="p-4">
                          <span className="font-medium">{invoice.number || invoice.id}</span>
                        </td>
                        <td className="p-4 text-gray-400">
                          {formatDate(invoice.created)}
                        </td>
                        <td className="p-4 font-medium">
                          {formatCurrency(invoice.amount_due, invoice.currency)}
                        </td>
                        <td className="p-4">
                          <span className={cn(
                            'px-2 py-1 text-xs rounded capitalize',
                            getStatusColor(invoice.status),
                            invoice.status === 'paid' && 'bg-accent-green/20',
                            invoice.status === 'open' && 'bg-yellow-500/20',
                            invoice.status === 'void' && 'bg-gray-500/20'
                          )}>
                            {invoice.status}
                          </span>
                        </td>
                        <td className="p-4 text-right">
                          {invoice.pdf_url && (
                            <a
                              href={invoice.pdf_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="p-2 rounded hover:bg-dark-bg inline-flex"
                              title="Download PDF"
                            >
                              <Download className="h-4 w-4" />
                            </a>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* Usage Tab */}
        {activeTab === 'usage' && (
          <div className="space-y-6">
            <h2 className="text-lg font-semibold">Current Usage</h2>

            {loadingUsage ? (
              <div className="flex justify-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* API Calls */}
                <div className="card p-6">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="p-2 rounded-lg bg-blue-500/20">
                      <Zap className="h-5 w-5 text-blue-400" />
                    </div>
                    <h3 className="font-medium">API Calls</h3>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Used</span>
                      <span>{(usage.api_calls || 0).toLocaleString()} / {(usage.api_limit || 0).toLocaleString()}</span>
                    </div>
                    <div className="h-2 bg-dark-bg rounded-full overflow-hidden">
                      <div
                        className="h-full bg-blue-500 rounded-full"
                        style={{ width: `${usage.api_limit ? (usage.api_calls || 0) / usage.api_limit * 100 : 0}%` }}
                      />
                    </div>
                  </div>
                </div>

                {/* Storage */}
                <div className="card p-6">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="p-2 rounded-lg bg-purple-500/20">
                      <Shield className="h-5 w-5 text-purple-400" />
                    </div>
                    <h3 className="font-medium">Storage</h3>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Used</span>
                      <span>{((usage.storage_used || 0) / 1024 / 1024 / 1024).toFixed(2)} GB / {((usage.storage_limit || 0) / 1024 / 1024 / 1024).toFixed(0)} GB</span>
                    </div>
                    <div className="h-2 bg-dark-bg rounded-full overflow-hidden">
                      <div
                        className="h-full bg-purple-500 rounded-full"
                        style={{ width: `${usage.storage_limit ? (usage.storage_used || 0) / usage.storage_limit * 100 : 0}%` }}
                      />
                    </div>
                  </div>
                </div>

                {/* Tokens */}
                <div className="card p-6">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="p-2 rounded-lg bg-accent-green/20">
                      <DollarSign className="h-5 w-5 text-accent-green" />
                    </div>
                    <h3 className="font-medium">AI Tokens</h3>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Used</span>
                      <span>{((usage.tokens_used || 0) / 1000).toFixed(1)}K / {((usage.tokens_limit || 0) / 1000).toFixed(0)}K</span>
                    </div>
                    <div className="h-2 bg-dark-bg rounded-full overflow-hidden">
                      <div
                        className="h-full bg-accent-green rounded-full"
                        style={{ width: `${usage.tokens_limit ? (usage.tokens_used || 0) / usage.tokens_limit * 100 : 0}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Usage Warning */}
            {usage.api_limit && usage.api_calls && usage.api_calls / usage.api_limit > 0.8 && (
              <div className="card p-4 border-yellow-500/30 flex items-center gap-3">
                <AlertTriangle className="h-5 w-5 text-yellow-400" />
                <div>
                  <p className="font-medium text-yellow-400">Approaching API Limit</p>
                  <p className="text-sm text-gray-400">You've used {Math.round(usage.api_calls / usage.api_limit * 100)}% of your API calls. Consider upgrading your plan.</p>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
