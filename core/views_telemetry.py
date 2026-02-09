"""
Session 971b: Lightweight page-view telemetry.

Writes route / tab / subtab visit counters to Django cache (Redis).
No database model needed — just Redis hash increments.

Keys:
  page_views:{YYYY-MM-DD}:{route}          += 1
  page_tabs:{YYYY-MM-DD}:{tab}:{subtab}    += 1   (only when tab is present)

Counters expire after 90 days automatically.
"""

import json
import logging
from datetime import date

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)

COUNTER_TTL = 90 * 86400  # 90 days in seconds


@csrf_exempt
@require_http_methods(["POST"])
def page_view_api(request):
    """Record a page view. Returns 204 on success, 204 on failure (never blocks UI)."""
    try:
        body = json.loads(request.body)
        route = body.get('route', '').strip()
        if not route:
            return JsonResponse({}, status=204)

        tab = body.get('tab', '').strip() or None
        subtab = body.get('subtab', '').strip() or None

        today = date.today().isoformat()

        try:
            from django.core.cache import cache

            # Increment route counter
            route_key = f'page_views:{today}:{route}'
            current = cache.get(route_key, 0)
            cache.set(route_key, current + 1, COUNTER_TTL)

            # Increment tab counter if present
            if tab:
                subtab_part = f':{subtab}' if subtab else ''
                tab_key = f'page_tabs:{today}:{tab}{subtab_part}'
                current_tab = cache.get(tab_key, 0)
                cache.set(tab_key, current_tab + 1, COUNTER_TTL)

        except Exception:
            # Cache unavailable — silently ignore
            logger.debug("Telemetry: cache unavailable, skipping")

    except Exception:
        # Bad JSON or anything else — return 204, never error
        pass

    return JsonResponse({}, status=204)
