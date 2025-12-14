"""
Stripe Webhook Views - Session 439

Handles Stripe webhook events for subscription management.
"""

import os
import json
import logging
import stripe
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)

# Stripe configuration
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Handle Stripe webhook events.

    Events handled:
    - customer.subscription.created
    - customer.subscription.updated
    - customer.subscription.deleted
    - checkout.session.completed
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    # Verify webhook signature
    try:
        if STRIPE_WEBHOOK_SECRET:
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
        else:
            # For development without webhook secret
            event = json.loads(payload)
            logger.warning("Processing webhook without signature verification (dev mode)")
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        return HttpResponse(status=400)

    # Handle the event
    event_type = event.get('type') if isinstance(event, dict) else event.type
    data = event.get('data', {}).get('object', {}) if isinstance(event, dict) else event.data.object

    logger.info(f"Received Stripe webhook: {event_type}")

    try:
        if event_type == 'customer.subscription.created':
            handle_subscription_created(data)
        elif event_type == 'customer.subscription.updated':
            handle_subscription_updated(data)
        elif event_type == 'customer.subscription.deleted':
            handle_subscription_deleted(data)
        elif event_type == 'checkout.session.completed':
            handle_checkout_completed(data)
        elif event_type == 'invoice.payment_succeeded':
            handle_payment_succeeded(data)
        elif event_type == 'invoice.payment_failed':
            handle_payment_failed(data)
        else:
            logger.info(f"Unhandled event type: {event_type}")

        return JsonResponse({'status': 'success'})

    except Exception as e:
        logger.error(f"Error processing webhook {event_type}: {e}")
        return JsonResponse({'error': str(e)}, status=500)


def handle_subscription_created(subscription):
    """Handle new subscription creation."""
    from core.services.stripe_subscription import stripe_subscription_service

    logger.info(f"Processing subscription.created: {subscription.get('id', subscription.id if hasattr(subscription, 'id') else 'unknown')}")

    # Convert dict to stripe object if needed
    if isinstance(subscription, dict):
        subscription = stripe.Subscription.construct_from(subscription, stripe.api_key)

    async_to_sync(stripe_subscription_service.handle_subscription_created)(subscription)


def handle_subscription_updated(subscription):
    """Handle subscription updates."""
    from core.services.stripe_subscription import stripe_subscription_service

    sub_id = subscription.get('id') if isinstance(subscription, dict) else subscription.id
    logger.info(f"Processing subscription.updated: {sub_id}")

    if isinstance(subscription, dict):
        subscription = stripe.Subscription.construct_from(subscription, stripe.api_key)

    async_to_sync(stripe_subscription_service.handle_subscription_updated)(subscription)


def handle_subscription_deleted(subscription):
    """Handle subscription cancellation."""
    from core.services.stripe_subscription import stripe_subscription_service

    sub_id = subscription.get('id') if isinstance(subscription, dict) else subscription.id
    logger.info(f"Processing subscription.deleted: {sub_id}")

    if isinstance(subscription, dict):
        subscription = stripe.Subscription.construct_from(subscription, stripe.api_key)

    async_to_sync(stripe_subscription_service.handle_subscription_deleted)(subscription)


def handle_checkout_completed(session):
    """Handle successful checkout session."""
    logger.info(f"Checkout completed: {session.get('id', 'unknown')}")

    # The subscription is created separately, but we can log/track this
    if session.get('mode') == 'subscription':
        subscription_id = session.get('subscription')
        customer_id = session.get('customer')
        logger.info(f"Subscription checkout: customer={customer_id}, subscription={subscription_id}")


def handle_payment_succeeded(invoice):
    """Handle successful payment."""
    customer_id = invoice.get('customer') if isinstance(invoice, dict) else invoice.customer
    amount = invoice.get('amount_paid', 0) if isinstance(invoice, dict) else invoice.amount_paid

    logger.info(f"Payment succeeded: customer={customer_id}, amount=${amount/100:.2f}")

    # Could trigger notifications here
    # e.g., send Discord DM thanking for payment


def handle_payment_failed(invoice):
    """Handle failed payment."""
    customer_id = invoice.get('customer') if isinstance(invoice, dict) else invoice.customer

    logger.warning(f"Payment failed: customer={customer_id}")

    # Could trigger notifications here
    # e.g., send Discord DM about payment issue


# API endpoint to check subscription status
@csrf_exempt
def subscription_status(request):
    """Get subscription status for authenticated user."""
    from core.services.stripe_subscription import get_subscription_info

    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    info = get_subscription_info(request.user)
    return JsonResponse(info)
