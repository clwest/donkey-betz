"""
Stripe Billing Views - Session 869

Real implementations replacing frontend stubs for Stripe billing endpoints.
Uses StripeSubscriptionService and EnhancedUserProfile for subscription management.
"""

import os
import logging
import stripe
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)

# Stripe configuration
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
STRIPE_CONFIGURED = bool(STRIPE_SECRET_KEY)

if STRIPE_CONFIGURED:
    stripe.api_key = STRIPE_SECRET_KEY


def get_user_profile(user):
    """Get or create user's EnhancedUserProfile."""
    from core.models import EnhancedUserProfile
    profile, _ = EnhancedUserProfile.objects.get_or_create(user=user)
    return profile


def stripe_not_configured_response():
    """Return standard response when Stripe is not configured."""
    return Response({
        'configured': False,
        'message': 'Stripe billing is not configured. Contact support to enable subscriptions.',
    }, status=503)


# =============================================================================
# SUBSCRIPTION PLANS
# =============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def stripe_plans(request):
    """
    GET /api/stripe/plans/ - Available subscription plans

    Returns pricing plans with features. Uses Stripe Products/Prices if configured,
    otherwise returns default plan configuration.
    """
    # Default plans (used even without Stripe for display purposes)
    default_plans = [
        {
            'id': 'free',
            'name': 'Free',
            'price': 0,
            'interval': 'month',
            'features': [
                'Basic access to AI agents',
                '5 agent calls per day',
                'Community support',
            ],
            'stripe_price_id': None,
        },
        {
            'id': 'pro',
            'name': 'Pro',
            'price': 29,
            'interval': 'month',
            'features': [
                'Unlimited agent calls',
                'Priority support',
                'API access',
                'Advanced analytics',
                'Custom workflows',
            ],
            'stripe_price_id': os.getenv('STRIPE_PRO_PRICE_ID'),
        },
        {
            'id': 'enterprise',
            'name': 'Enterprise',
            'price': 99,
            'interval': 'month',
            'features': [
                'Everything in Pro',
                'Custom integrations',
                'Dedicated support',
                'Team collaboration',
                'SLA guarantees',
            ],
            'stripe_price_id': os.getenv('STRIPE_ENTERPRISE_PRICE_ID'),
        },
    ]

    return Response({
        'plans': default_plans,
        'stripe_configured': STRIPE_CONFIGURED,
    })


# =============================================================================
# PAYMENT METHODS
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stripe_payment_methods(request):
    """
    GET /api/stripe/payment-methods/ - User's payment methods
    """
    if not STRIPE_CONFIGURED:
        return stripe_not_configured_response()

    profile = get_user_profile(request.user)

    if not profile.stripe_customer_id:
        return Response({
            'payment_methods': [],
            'default_payment_method': None,
        })

    try:
        # Get payment methods from Stripe
        payment_methods = stripe.PaymentMethod.list(
            customer=profile.stripe_customer_id,
            type='card',
        )

        # Get default payment method
        customer = stripe.Customer.retrieve(profile.stripe_customer_id)
        default_pm = customer.invoice_settings.default_payment_method

        methods = []
        for pm in payment_methods.data:
            methods.append({
                'id': pm.id,
                'type': pm.type,
                'card': {
                    'brand': pm.card.brand,
                    'last4': pm.card.last4,
                    'exp_month': pm.card.exp_month,
                    'exp_year': pm.card.exp_year,
                },
                'is_default': pm.id == default_pm,
                'created': pm.created,
            })

        return Response({
            'payment_methods': methods,
            'default_payment_method': default_pm,
        })

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error getting payment methods: {e}")
        return Response({'error': str(e)}, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stripe_add_payment_method(request):
    """
    POST /api/stripe/payment-methods/ - Add payment method

    Expects: { "payment_method_id": "pm_xxx" } from Stripe.js
    """
    if not STRIPE_CONFIGURED:
        return stripe_not_configured_response()

    payment_method_id = request.data.get('payment_method_id')
    if not payment_method_id:
        return Response({'error': 'payment_method_id required'}, status=400)

    profile = get_user_profile(request.user)

    try:
        # Create customer if doesn't exist
        if not profile.stripe_customer_id:
            customer = stripe.Customer.create(
                email=request.user.email,
                name=request.user.get_full_name() or request.user.username,
                metadata={'user_id': str(request.user.id)},
            )
            profile.stripe_customer_id = customer.id
            profile.save(update_fields=['stripe_customer_id'])

        # Attach payment method to customer
        stripe.PaymentMethod.attach(
            payment_method_id,
            customer=profile.stripe_customer_id,
        )

        # Set as default if no default exists
        customer = stripe.Customer.retrieve(profile.stripe_customer_id)
        if not customer.invoice_settings.default_payment_method:
            stripe.Customer.modify(
                profile.stripe_customer_id,
                invoice_settings={'default_payment_method': payment_method_id},
            )

        return Response({
            'success': True,
            'message': 'Payment method added successfully',
            'payment_method_id': payment_method_id,
        })

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error adding payment method: {e}")
        return Response({'error': str(e)}, status=400)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def stripe_remove_payment_method(request, payment_method_id):
    """
    DELETE /api/stripe/payment-methods/<id>/ - Remove payment method
    """
    if not STRIPE_CONFIGURED:
        return stripe_not_configured_response()

    profile = get_user_profile(request.user)

    if not profile.stripe_customer_id:
        return Response({'error': 'No customer record found'}, status=400)

    try:
        # Verify payment method belongs to this customer
        pm = stripe.PaymentMethod.retrieve(payment_method_id)
        if pm.customer != profile.stripe_customer_id:
            return Response({'error': 'Payment method not found'}, status=404)

        # Detach payment method
        stripe.PaymentMethod.detach(payment_method_id)

        return Response({
            'success': True,
            'message': 'Payment method removed',
        })

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error removing payment method: {e}")
        return Response({'error': str(e)}, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stripe_set_default_payment_method(request, payment_method_id):
    """
    POST /api/stripe/payment-methods/<id>/default/ - Set default payment method
    """
    if not STRIPE_CONFIGURED:
        return stripe_not_configured_response()

    profile = get_user_profile(request.user)

    if not profile.stripe_customer_id:
        return Response({'error': 'No customer record found'}, status=400)

    try:
        stripe.Customer.modify(
            profile.stripe_customer_id,
            invoice_settings={'default_payment_method': payment_method_id},
        )

        return Response({
            'success': True,
            'message': 'Default payment method updated',
        })

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error setting default: {e}")
        return Response({'error': str(e)}, status=400)


# =============================================================================
# INVOICES
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stripe_invoices(request):
    """
    GET /api/stripe/invoices/ - User's invoices
    """
    if not STRIPE_CONFIGURED:
        return stripe_not_configured_response()

    profile = get_user_profile(request.user)

    if not profile.stripe_customer_id:
        return Response({'invoices': [], 'has_more': False})

    try:
        invoices = stripe.Invoice.list(
            customer=profile.stripe_customer_id,
            limit=20,
        )

        invoice_list = []
        for inv in invoices.data:
            invoice_list.append({
                'id': inv.id,
                'number': inv.number,
                'status': inv.status,
                'amount_due': inv.amount_due / 100,  # Convert from cents
                'amount_paid': inv.amount_paid / 100,
                'currency': inv.currency,
                'created': inv.created,
                'due_date': inv.due_date,
                'pdf_url': inv.invoice_pdf,
                'hosted_invoice_url': inv.hosted_invoice_url,
            })

        return Response({
            'invoices': invoice_list,
            'has_more': invoices.has_more,
        })

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error getting invoices: {e}")
        return Response({'error': str(e)}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stripe_invoice_detail(request, invoice_id):
    """
    GET /api/stripe/invoices/<id>/ - Invoice detail
    """
    if not STRIPE_CONFIGURED:
        return stripe_not_configured_response()

    profile = get_user_profile(request.user)

    try:
        invoice = stripe.Invoice.retrieve(invoice_id)

        # Verify invoice belongs to this customer
        if invoice.customer != profile.stripe_customer_id:
            return Response({'error': 'Invoice not found'}, status=404)

        return Response({
            'id': invoice.id,
            'number': invoice.number,
            'status': invoice.status,
            'amount_due': invoice.amount_due / 100,
            'amount_paid': invoice.amount_paid / 100,
            'currency': invoice.currency,
            'created': invoice.created,
            'due_date': invoice.due_date,
            'pdf_url': invoice.invoice_pdf,
            'hosted_invoice_url': invoice.hosted_invoice_url,
            'lines': [
                {
                    'description': line.description,
                    'amount': line.amount / 100,
                    'quantity': line.quantity,
                }
                for line in invoice.lines.data
            ],
        })

    except stripe.error.InvalidRequestError:
        return Response({'error': 'Invoice not found'}, status=404)
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error getting invoice: {e}")
        return Response({'error': str(e)}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stripe_upcoming_invoice(request):
    """
    GET /api/stripe/upcoming-invoice/ - Preview next invoice
    """
    if not STRIPE_CONFIGURED:
        return stripe_not_configured_response()

    profile = get_user_profile(request.user)

    if not profile.stripe_customer_id or not profile.stripe_subscription_id:
        return Response({'upcoming_invoice': None, 'message': 'No active subscription'})

    try:
        upcoming = stripe.Invoice.upcoming(customer=profile.stripe_customer_id)

        return Response({
            'upcoming_invoice': {
                'amount_due': upcoming.amount_due / 100,
                'currency': upcoming.currency,
                'next_payment_date': upcoming.next_payment_attempt,
                'lines': [
                    {
                        'description': line.description,
                        'amount': line.amount / 100,
                    }
                    for line in upcoming.lines.data
                ],
            }
        })

    except stripe.error.InvalidRequestError:
        return Response({'upcoming_invoice': None, 'message': 'No upcoming invoice'})
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error getting upcoming invoice: {e}")
        return Response({'error': str(e)}, status=400)


# =============================================================================
# USAGE METRICS
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stripe_usage(request):
    """
    GET /api/stripe/usage/ - Current usage metrics

    Returns usage data from our database (not Stripe usage-based billing).
    """
    from core.models import AgentExecution
    from django.db.models import Count

    profile = get_user_profile(request.user)

    # Get current billing period (start of month to now)
    now = timezone.now()
    period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Count agent calls this period
    agent_calls = AgentExecution.objects.filter(
        user=request.user,
        created_at__gte=period_start,
    ).count()

    # Get tier limits
    tier_limits = {
        'free': {'agent_calls': 5, 'api_requests': 100},
        'pro': {'agent_calls': -1, 'api_requests': -1},  # -1 = unlimited
        'enterprise': {'agent_calls': -1, 'api_requests': -1},
    }
    limits = tier_limits.get(profile.subscription_tier, tier_limits['free'])

    return Response({
        'usage': {
            'agent_calls': agent_calls,
            'agent_calls_limit': limits['agent_calls'],
            'api_requests': 0,  # TODO: Track API requests
            'api_requests_limit': limits['api_requests'],
            'storage_mb': 0,  # TODO: Track storage
            'period_start': period_start.isoformat(),
            'period_end': None,  # Ongoing
        },
        'tier': profile.subscription_tier,
    })


# =============================================================================
# SUBSCRIPTION MANAGEMENT
# =============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stripe_subscribe(request):
    """
    POST /api/stripe/subscribe/ - Subscribe to a plan

    Expects: { "plan_id": "pro" or "enterprise", "success_url": "...", "cancel_url": "..." }
    """
    if not STRIPE_CONFIGURED:
        return stripe_not_configured_response()

    plan_id = request.data.get('plan_id')
    success_url = request.data.get('success_url', request.build_absolute_uri('/billing/success'))
    cancel_url = request.data.get('cancel_url', request.build_absolute_uri('/billing/cancel'))

    if not plan_id or plan_id not in ['pro', 'enterprise']:
        return Response({'error': 'Invalid plan_id. Must be "pro" or "enterprise"'}, status=400)

    # Get price ID from environment
    price_id = os.getenv(f'STRIPE_{plan_id.upper()}_PRICE_ID')
    if not price_id:
        return Response({'error': f'Price not configured for plan: {plan_id}'}, status=400)

    try:
        from core.services.stripe_subscription import stripe_subscription_service

        checkout_url = async_to_sync(stripe_subscription_service.create_checkout_session)(
            user=request.user,
            price_id=price_id,
            success_url=success_url,
            cancel_url=cancel_url,
        )

        return Response({
            'success': True,
            'checkout_url': checkout_url,
        })

    except Exception as e:
        logger.error(f"Error creating checkout session: {e}")
        return Response({'error': str(e)}, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stripe_cancel_subscription(request):
    """
    POST /api/stripe/cancel-subscription/ - Cancel subscription

    Optional: { "at_period_end": true } to cancel at end of period (default)
    """
    if not STRIPE_CONFIGURED:
        return stripe_not_configured_response()

    at_period_end = request.data.get('at_period_end', True)

    try:
        from core.services.stripe_subscription import stripe_subscription_service

        success = async_to_sync(stripe_subscription_service.cancel_subscription)(
            user=request.user,
            at_period_end=at_period_end,
        )

        if success:
            return Response({
                'success': True,
                'message': 'Subscription will be cancelled at the end of the billing period' if at_period_end else 'Subscription cancelled immediately',
            })
        else:
            return Response({'error': 'No active subscription found'}, status=400)

    except Exception as e:
        logger.error(f"Error cancelling subscription: {e}")
        return Response({'error': str(e)}, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stripe_resume_subscription(request):
    """
    POST /api/stripe/resume-subscription/ - Resume cancelled subscription
    """
    if not STRIPE_CONFIGURED:
        return stripe_not_configured_response()

    profile = get_user_profile(request.user)

    if not profile.stripe_subscription_id:
        return Response({'error': 'No subscription found'}, status=400)

    try:
        # Remove cancel_at_period_end
        subscription = stripe.Subscription.modify(
            profile.stripe_subscription_id,
            cancel_at_period_end=False,
        )

        # Update profile
        profile.subscription_status = 'active'
        profile.subscription_ends_at = None
        profile.save(update_fields=['subscription_status', 'subscription_ends_at'])

        return Response({
            'success': True,
            'message': 'Subscription resumed',
        })

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error resuming subscription: {e}")
        return Response({'error': str(e)}, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stripe_billing_portal(request):
    """
    POST /api/stripe/billing-portal/ - Get Stripe billing portal URL
    """
    if not STRIPE_CONFIGURED:
        return stripe_not_configured_response()

    return_url = request.data.get('return_url', request.build_absolute_uri('/'))

    try:
        from core.services.stripe_subscription import stripe_subscription_service

        portal_url = async_to_sync(stripe_subscription_service.get_billing_portal_url)(
            user=request.user,
            return_url=return_url,
        )

        if portal_url:
            return Response({
                'success': True,
                'url': portal_url,
            })
        else:
            return Response({'error': 'Could not create billing portal session'}, status=400)

    except Exception as e:
        logger.error(f"Error creating billing portal: {e}")
        return Response({'error': str(e)}, status=400)
