"""
Newsletter subscription API endpoints for Operator Edge.
Public (no auth required) — used by the landing page signup form.
"""
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import IntegrityError
import json

from core.models_newsletter import NewsletterSubscriber

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def newsletter_subscribe(request):
    """Handle newsletter signup from the public landing page."""
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    email = data.get('email', '').strip().lower()
    if not email or '@' not in email or '.' not in email.split('@')[-1]:
        return JsonResponse({'error': 'Valid email required'}, status=400)

    name = data.get('name', '').strip()[:255]
    source = data.get('source', 'landing_page')[:100]
    utm_source = data.get('utm_source', '')[:100]
    utm_medium = data.get('utm_medium', '')[:100]
    utm_campaign = data.get('utm_campaign', '')[:100]
    referral_code = data.get('referral_code', '')[:100]

    try:
        subscriber, created = NewsletterSubscriber.objects.get_or_create(
            email=email,
            defaults={
                'name': name,
                'source': source,
                'utm_source': utm_source,
                'utm_medium': utm_medium,
                'utm_campaign': utm_campaign,
                'referral_code': referral_code,
            }
        )

        if not created and subscriber.unsubscribed_at:
            # Re-subscribe
            subscriber.unsubscribed_at = None
            subscriber.save(update_fields=['unsubscribed_at'])
            created = True

        logger.info(f"Newsletter {'signup' if created else 'existing'}: {email} via {source}")

        return JsonResponse({
            'success': True,
            'created': created,
            'message': 'Welcome to Operator Edge!' if created else 'You\'re already subscribed!',
        })

    except IntegrityError:
        return JsonResponse({
            'success': True,
            'created': False,
            'message': 'You\'re already subscribed!',
        })


@csrf_exempt
@require_http_methods(["GET"])
def newsletter_subscriber_count(request):
    """Public endpoint returning subscriber count for social proof."""
    count = NewsletterSubscriber.objects.filter(unsubscribed_at__isnull=True).count()
    return JsonResponse({'count': count})
