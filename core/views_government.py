"""
Session 1015: Government & Legislation Hub API endpoint.

Surfaces legislation SpiderData for the GovernmentPage frontend.
"""
import logging

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models_unified_system import SpiderData

logger = logging.getLogger(__name__)


def _extract_bill(raw_data):
    """Extract bill dict from raw_data, handling nested spider-network envelope.

    SpiderData.raw_data can be:
    1. Flat bill data: {bill_number, title, ...}
    2. Spider-network envelope: {raw_data: {bill_number, title, ...}, ...}
    3. Celery bundle: {items: [{raw_data: {...}}, ...]}
    """
    if not isinstance(raw_data, dict):
        return None
    # Case 1: flat — bill_number at top level
    if raw_data.get('bill_number'):
        return raw_data
    # Case 2: spider-network envelope
    inner = raw_data.get('raw_data')
    if isinstance(inner, dict) and inner.get('bill_number'):
        return inner
    return None


def _extract_bills_from_row(item):
    """Extract one or more bills from a SpiderData row."""
    raw = item.raw_data if isinstance(item.raw_data, dict) else {}
    # Case 3: Celery bundle with items list
    items_list = raw.get('items', [])
    if isinstance(items_list, list) and items_list:
        bills = []
        for entry in items_list:
            bill = _extract_bill(entry) if isinstance(entry, dict) else None
            if bill:
                bills.append((bill, item))
        if bills:
            return bills
    # Cases 1 & 2: single bill per row
    bill = _extract_bill(raw)
    if bill:
        return [(bill, item)]
    return []


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def government_hub(request):
    """Consolidated hub — stats, top topics, recent bills."""
    try:
        qs = SpiderData.objects.filter(spider_name='legislation').order_by('-created_at')

        # Extract all bills from rows (handles flat, envelope, and bundle formats)
        all_bills = []
        for item in qs[:100]:
            all_bills.extend(_extract_bills_from_row(item))

        total_bills = len(all_bills)
        house_count = 0
        senate_count = 0
        status_breakdown = {}
        topic_counts = {}

        bills_list = []
        for raw, item in all_bills:
            bn = raw.get('bill_number', '')

            # Chamber detection from bill number prefix
            bn_upper = bn.upper().strip()
            if bn_upper.startswith(('HR', 'H.R', 'HB', 'HJR', 'HRES')):
                house_count += 1
            elif bn_upper.startswith(('S', 'SB', 'SJR', 'SRES')):
                senate_count += 1

            # Status
            status = raw.get('status', '')
            if status:
                status_breakdown[status] = status_breakdown.get(status, 0) + 1

            # Topics
            for t in raw.get('topics', []):
                topic_counts[t] = topic_counts.get(t, 0) + 1

            # Build bill card data (first 30 for display)
            if len(bills_list) < 30:
                sponsors = raw.get('sponsors', [])
                bills_list.append({
                    'id': str(item.id),
                    'bill_number': bn,
                    'title': raw.get('title', ''),
                    'description': raw.get('description', ''),
                    'plain_summary': raw.get('plain_summary', ''),
                    'status': status,
                    'state': raw.get('state', ''),
                    'last_action': raw.get('last_action', ''),
                    'last_action_date': raw.get('last_action_date', ''),
                    'sponsors': [
                        {'name': s.get('name', ''), 'party': s.get('party', '')}
                        for s in (sponsors[:5] if isinstance(sponsors, list) else [])
                    ],
                    'sponsor_count': raw.get('sponsor_count', 0),
                    'committee': raw.get('committee', ''),
                    'topics': raw.get('topics', []),
                    'url': raw.get('url', ''),
                    'congress_gov_url': raw.get('congress_gov_url', ''),
                    'created_at': item.created_at.isoformat() if item.created_at else None,
                })

        top_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:15]

        return Response({
            'success': True,
            'stats': {
                'total_bills': total_bills,
                'house_count': house_count,
                'senate_count': senate_count,
                'status_breakdown': status_breakdown,
            },
            'top_topics': [{'topic': t, 'count': c} for t, c in top_topics],
            'bills': bills_list,
        })

    except Exception as e:
        logger.error(f"Government hub error: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)
