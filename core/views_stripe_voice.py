"""
Stripe Voice Checkout API Endpoints - Session 450

Provides REST API endpoints for Stripe payment processing:
- Create checkout sessions for voice purchases
- Handle Stripe webhooks
- Check payment status
"""

import json
import logging
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from core.services.stripe_voice_payments import get_stripe_voice_service

logger = logging.getLogger(__name__)


# ==================== CHECKOUT ====================

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def create_checkout(request):
    """
    Create a Stripe Checkout session for voice purchase.

    POST /api/voice-checkout/create/

    Body:
    {
        "voice_id": "uuid",
        "text_length": 500,           // Number of characters
        "duration_estimate": 60,      // Optional: estimated seconds
        "content_type": "animated_series",  // Optional
        "success_url": "...",         // Optional: override default
        "cancel_url": "..."           // Optional: override default
    }

    Response:
    {
        "success": true,
        "checkout_url": "https://checkout.stripe.com/...",
        "session_id": "cs_...",
        "price": 2.50,
        "price_display": "$2.50"
    }
    """
    try:
        data = json.loads(request.body) if request.body else {}

        voice_id = data.get('voice_id')
        text_length = data.get('text_length')

        if not voice_id:
            return JsonResponse({
                'success': False,
                'error': 'Missing required field: voice_id'
            }, status=400)

        if not text_length or int(text_length) < 1:
            return JsonResponse({
                'success': False,
                'error': 'Missing or invalid text_length (minimum 1)'
            }, status=400)

        service = get_stripe_voice_service()
        result = service.create_checkout_session(
            voice_id=voice_id,
            buyer=request.user,
            text_length=int(text_length),
            duration_estimate=data.get('duration_estimate'),
            content_type=data.get('content_type', 'other'),
            success_url=data.get('success_url'),
            cancel_url=data.get('cancel_url'),
        )

        if result:
            return JsonResponse({
                'success': True,
                'checkout_url': result['url'],
                'session_id': result['session_id'],
                'voice_name': result['voice_name'],
                'price': result['price'],
                'price_display': result['price_display'],
                'text_length': result['text_length'],
                'duration_estimate': result['duration_estimate'],
                'simulated': result.get('simulated', False),
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Failed to create checkout session'
            }, status=500)

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON body'
        }, status=400)
    except Exception as e:
        logger.error(f"Error creating checkout: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@login_required
@require_http_methods(["GET", "POST"])
def price_estimate(request):
    """
    Get price estimate for a voice purchase without creating a session.

    GET /api/voice-checkout/price/?voice_id=...&text_length=500

    POST /api/voice-checkout/price/
    {
        "voice_id": "uuid",
        "text_length": 500
    }

    Response:
    {
        "success": true,
        "voice_name": "DonkeyKing's Voice",
        "pricing_model": "per_minute",
        "gross_price": 2.50,
        "platform_fee": 0.75,
        "owner_payout": 1.75,
        "price_display": "$2.50"
    }
    """
    try:
        if request.method == 'POST':
            data = json.loads(request.body) if request.body else {}
            voice_id = data.get('voice_id')
            text_length = data.get('text_length')
        else:
            voice_id = request.GET.get('voice_id')
            text_length = request.GET.get('text_length')

        if not voice_id or not text_length:
            return JsonResponse({
                'success': False,
                'error': 'Missing voice_id or text_length'
            }, status=400)

        service = get_stripe_voice_service()
        result = service.get_voice_price_estimate(
            voice_id=voice_id,
            text_length=int(text_length)
        )

        if result:
            return JsonResponse({
                'success': True,
                **result
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Voice not found or price calculation failed'
            }, status=404)

    except Exception as e:
        logger.error(f"Error getting price estimate: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ==================== WEBHOOK ====================

@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    """
    Handle Stripe webhook events.

    POST /api/voice-checkout/webhook/

    This endpoint receives events from Stripe when:
    - checkout.session.completed: Payment successful
    - payment_intent.succeeded: Payment captured
    - payment_intent.payment_failed: Payment failed

    The endpoint verifies the webhook signature and processes the event.
    """
    try:
        payload = request.body
        signature = request.META.get('HTTP_STRIPE_SIGNATURE', '')

        service = get_stripe_voice_service()
        result = service.handle_webhook(payload, signature)

        if result.get('success'):
            return HttpResponse(status=200)
        else:
            logger.error(f"Webhook error: {result.get('error')}")
            return HttpResponse(status=400)

    except Exception as e:
        logger.error(f"Webhook exception: {e}")
        return HttpResponse(status=500)


# ==================== STATUS ====================

@login_required
@require_http_methods(["GET"])
def checkout_status(request, session_id):
    """
    Check the status of a checkout session.

    GET /api/voice-checkout/status/<session_id>/

    Response:
    {
        "success": true,
        "status": "complete",
        "payment_status": "paid",
        "amount_total": 250,  // cents
        "currency": "usd"
    }
    """
    try:
        service = get_stripe_voice_service()
        result = service.get_checkout_status(session_id)

        if result:
            return JsonResponse({
                'success': True,
                **result
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Session not found'
            }, status=404)

    except Exception as e:
        logger.error(f"Error getting checkout status: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ==================== SUCCESS/CANCEL PAGES ====================

@login_required
def checkout_success(request):
    """
    Success page after completing payment.

    GET /voice-checkout/success/?session_id=cs_...

    Renders a success page with order details.
    """
    session_id = request.GET.get('session_id', '')

    # Get session details if available
    service = get_stripe_voice_service()
    session_info = service.get_checkout_status(session_id) if session_id else None

    context = {
        'session_id': session_id,
        'session_info': session_info,
        'success': True,
    }

    # Return JSON for API requests
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({
            'success': True,
            'message': 'Payment successful',
            'session_id': session_id,
            'details': session_info,
        })

    # For now, return simple JSON (web UI can be added later)
    return JsonResponse({
        'success': True,
        'message': 'Payment successful! Your voice generation credits have been added.',
        'session_id': session_id,
        'next_step': 'You can now generate audio using this voice.',
    })


def checkout_cancel(request):
    """
    Cancel page when user cancels payment.

    GET /voice-checkout/cancel/
    """
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({
            'success': False,
            'message': 'Payment cancelled',
        })

    return JsonResponse({
        'success': False,
        'message': 'Payment was cancelled. No charges were made.',
        'next_step': 'Return to the voice marketplace to try again.',
    })


# ==================== SIMULATE (Testing) ====================

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def simulate_purchase(request):
    """
    Simulate a voice purchase for testing when Stripe is not configured.

    POST /api/voice-checkout/simulate/

    Body:
    {
        "voice_id": "uuid",
        "text_length": 500,
        "text": "The actual text to generate...",  // Optional
        "content_type": "animated_series"
    }

    Response:
    {
        "success": true,
        "transaction_id": "uuid",
        "voice_name": "DonkeyKing's Voice",
        "price": 2.50,
        "simulated": true
    }
    """
    try:
        data = json.loads(request.body) if request.body else {}

        voice_id = data.get('voice_id')
        text_length = data.get('text_length')

        if not voice_id or not text_length:
            return JsonResponse({
                'success': False,
                'error': 'Missing voice_id or text_length'
            }, status=400)

        service = get_stripe_voice_service()
        result = service.simulate_purchase(
            voice_id=voice_id,
            buyer=request.user,
            text_length=int(text_length),
            text=data.get('text', ''),
            content_type=data.get('content_type', 'other'),
        )

        if result:
            return JsonResponse(result)
        else:
            return JsonResponse({
                'success': False,
                'error': 'Simulation failed'
            }, status=500)

    except Exception as e:
        logger.error(f"Error simulating purchase: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
