/**
 * Billing API Service
 * Handles all billing and subscription related API calls
 */

import { apiClient } from './api.config';

export interface PricingTier {
  id: number;
  name: string;
  tier_type: string;
  display_name: string;
  description: string;
  monthly_price: number;
  yearly_price: number;
  monthly_credits: number;
  api_calls_per_hour: number;
  max_concurrent_requests: number;
  storage_limit_gb: number;
  features: Record<string, any>;
  is_active: boolean;
}

export interface Subscription {
  id: number;
  pricing_tier: PricingTier;
  status: string;
  billing_cycle: string;
  start_date: string;
  current_period_start: string;
  current_period_end: string;
  cancel_at_period_end: boolean;
  canceled_at: string | null;
  trial_end: string | null;
  credits_used_this_period: number;
  credits_remaining: number;
  last_usage_reset: string;
  feature_limits: Array<{
    feature_type: string;
    credits_per_use: number;
    hourly_limit: number;
    daily_limit: number;
    monthly_limit: number;
    is_enabled: boolean;
  }>;
  created_at: string;
  updated_at: string;
  is_active: boolean;
  days_until_renewal: number;
  usage_percentage: number;
}

export interface UsageRecord {
  id: number;
  feature_type: string;
  credits_consumed: number;
  api_endpoint: string;
  request_method: string;
  status: string;
  processing_time_ms: number | null;
  estimated_cost: number;
  created_at: string;
}

export interface Invoice {
  id: number;
  invoice_number: string;
  subtotal: number;
  tax_amount: number;
  total_amount: number;
  currency: string;
  status: string;
  period_start: string;
  period_end: string;
  due_date: string;
  paid_at: string | null;
  line_items: Array<{
    description: string;
    amount: number;
    quantity: number;
  }>;
  created_at: string;
  is_overdue: boolean;
}

export interface PaymentMethod {
  id: number;
  type: string;
  is_default: boolean;
  card_brand: string;
  card_last_4: string;
  card_exp_month: number;
  card_exp_year: number;
  display_name: string;
  is_active: boolean;
  created_at: string;
}

export interface BillingSummary {
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
      avg_processing_time?: number;
    }>;
    period_days: number;
  };
  recent_invoices: Invoice[];
}

export interface CheckoutSessionRequest {
  type: 'subscription' | 'credits';
  tier_id?: number;
  billing_cycle?: 'monthly' | 'yearly';
  credits?: number;
}

export interface CheckoutSessionResponse {
  checkout_url: string;
  session_id: string;
}

class BillingAPI {
  // Pricing and Plans
  async getPricingTiers(): Promise<PricingTier[]> {
    const response = await apiClient.get('/api/v1/billing/pricing/');
    return response.data;
  }

  // Subscription Management
  async getSubscription(): Promise<Subscription> {
    const response = await apiClient.get('/api/v1/billing/subscription/');
    return response.data;
  }

  async createCheckoutSession(request: CheckoutSessionRequest): Promise<CheckoutSessionResponse> {
    const response = await apiClient.post('/api/v1/billing/checkout/', request);
    return response.data;
  }

  async cancelSubscription(cancelImmediately: boolean = false): Promise<{ message: string; subscription: Subscription }> {
    const response = await apiClient.post('/api/v1/billing/subscription/cancel/', {
      cancel_immediately: cancelImmediately
    });
    return response.data;
  }

  async reactivateSubscription(): Promise<{ message: string; subscription: Subscription }> {
    const response = await apiClient.post('/api/v1/billing/subscription/reactivate/');
    return response.data;
  }

  async createBillingPortalSession(): Promise<{ portal_url: string }> {
    const response = await apiClient.post('/api/v1/billing/portal/');
    return response.data;
  }

  // Usage and Analytics
  async getUsageHistory(params: { 
    feature_type?: string; 
    days?: number; 
    page?: number; 
    page_size?: number; 
  } = {}): Promise<{
    count: number;
    next: string | null;
    previous: string | null;
    results: UsageRecord[];
  }> {
    const response = await apiClient.get('/api/v1/billing/usage/', { params });
    return response.data;
  }

  async getBillingSummary(): Promise<BillingSummary> {
    const response = await apiClient.get('/api/v1/billing/summary/');
    return response.data;
  }

  // Invoice Management
  async getInvoices(): Promise<Invoice[]> {
    const response = await apiClient.get('/api/v1/billing/invoices/');
    return response.data;
  }

  async downloadInvoice(invoiceId: number): Promise<Blob> {
    const response = await apiClient.get(`/api/v1/billing/invoices/${invoiceId}/download/`, {
      responseType: 'blob'
    });
    return response.data;
  }

  // Payment Methods
  async getPaymentMethods(): Promise<PaymentMethod[]> {
    const response = await apiClient.get('/api/v1/billing/payment-methods/');
    return response.data;
  }

  async addPaymentMethod(paymentMethodData: {
    stripe_payment_method_id: string;
    is_default?: boolean;
  }): Promise<PaymentMethod> {
    const response = await apiClient.post('/api/v1/billing/payment-methods/', paymentMethodData);
    return response.data;
  }

  async deletePaymentMethod(paymentMethodId: number): Promise<void> {
    await apiClient.delete(`/api/v1/billing/payment-methods/${paymentMethodId}/`);
  }

  async setDefaultPaymentMethod(paymentMethodId: number): Promise<PaymentMethod> {
    const response = await apiClient.patch(`/api/v1/billing/payment-methods/${paymentMethodId}/`, {
      is_default: true
    });
    return response.data;
  }

  // Credits
  async purchaseCredits(data: {
    credits: number;
    payment_method_id: string;
  }): Promise<{
    message: string;
    credits_purchased: number;
    amount_paid: number;
    transaction_id: number;
  }> {
    const response = await apiClient.post('/api/v1/billing/credits/purchase/', data);
    return response.data;
  }

  // Admin endpoints (for admin users)
  async getAdminDashboard(days: number = 30): Promise<{
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
  }> {
    const response = await apiClient.get('/api/v1/billing/admin/dashboard/', {
      params: { days }
    });
    return response.data;
  }

  async getAdminUsers(): Promise<Array<{
    id: number;
    username: string;
    email: string;
    date_joined: string;
    last_login: string | null;
    subscription_status: string;
    tier: string;
    credits_remaining: number;
    current_period_end: string | null;
  }>> {
    const response = await apiClient.get('/api/v1/billing/admin/users/');
    return response.data;
  }
}

export const billingAPI = new BillingAPI();