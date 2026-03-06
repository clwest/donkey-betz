"""
Government & Legislation API endpoints.

Serves congress members, bills, and voting data from dedicated government models.
"""
import logging

from django.db.models import Count, Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from core.models_government import Bill, CongressMember, RollCallVote, VotePosition

logger = logging.getLogger(__name__)

# ─── Hub (overview stats) ────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([AllowAny])
def government_hub(request):
    """Consolidated hub -- stats, top topics, recent federal bills."""
    try:
        bills_qs = Bill.objects.filter(jurisdiction='federal')
        total = bills_qs.count()
        house = bills_qs.filter(chamber='house').count()
        senate = bills_qs.filter(chamber='senate').count()

        # Status breakdown
        status_breakdown = {}
        for row in bills_qs.exclude(status='').values('status').annotate(c=Count('id')):
            status_breakdown[row['status']] = row['c']

        # Topic counts (JSONField list)
        topic_counts: dict[str, int] = {}
        for topics in bills_qs.exclude(topics=[]).values_list('topics', flat=True)[:500]:
            for t in (topics or []):
                topic_counts[t] = topic_counts.get(t, 0) + 1
        top_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:15]

        # Recent bills
        recent = bills_qs.order_by('-updated_at')[:20]
        bills_list = [_bill_to_dict(b) for b in recent]

        # Member counts
        members_total = CongressMember.objects.filter(in_office=True).count()

        return Response({
            'success': True,
            'stats': {
                'total_bills': total,
                'house_count': house,
                'senate_count': senate,
                'members_count': members_total,
                'status_breakdown': status_breakdown,
            },
            'top_topics': [{'topic': t, 'count': c} for t, c in top_topics],
            'bills': bills_list,
        })
    except Exception as e:
        logger.error(f"Government hub error: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)


# ─── Bills ────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([AllowAny])
def bills_list(request):
    """Paginated, filterable bill listing."""
    try:
        qs = Bill.objects.filter(jurisdiction='federal')

        # Filters
        chamber = request.query_params.get('chamber')
        if chamber in ('house', 'senate'):
            qs = qs.filter(chamber=chamber)

        status = request.query_params.get('status')
        if status:
            qs = qs.filter(status__iexact=status)

        bill_type = request.query_params.get('bill_type')
        if bill_type:
            qs = qs.filter(bill_type__iexact=bill_type)

        search = request.query_params.get('q')
        if search:
            qs = qs.filter(
                Q(title__icontains=search)
                | Q(short_title__icontains=search)
                | Q(plain_summary__icontains=search)
            )

        topic = request.query_params.get('topic')
        if topic:
            qs = qs.filter(topics__contains=[topic])

        # Pagination
        page = int(request.query_params.get('page', 1))
        per_page = min(int(request.query_params.get('per_page', 30)), 100)
        total = qs.count()
        offset = (page - 1) * per_page

        bills = qs.order_by('-updated_at')[offset:offset + per_page]

        return Response({
            'bills': [_bill_to_dict(b) for b in bills],
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page,
        })
    except Exception as e:
        logger.error(f"Bills list error: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def bill_detail(request, bill_uid):
    """Single bill detail with sponsors and vote summary."""
    try:
        bill = Bill.objects.filter(bill_uid=bill_uid).first()
        if not bill:
            return Response({'error': 'Bill not found'}, status=404)

        data = _bill_to_dict(bill, full=True)

        # Include linked sponsors (M2M)
        sponsors_linked = []
        for m in bill.sponsors.all():
            sponsors_linked.append({
                'bioguide_id': m.bioguide_id,
                'name': m.full_name,
                'party': m.party,
                'state': m.state,
                'chamber': m.chamber,
                'photo_url': m.photo_url,
            })
        data['sponsors_linked'] = sponsors_linked

        # Include roll call summary
        roll_calls = []
        for rc in bill.roll_calls.order_by('-date')[:10]:
            roll_calls.append({
                'id': rc.id,
                'roll_number': rc.roll_number,
                'date': rc.date.isoformat() if rc.date else None,
                'question': rc.question,
                'result': rc.result,
                'yea_count': rc.yea_count,
                'nay_count': rc.nay_count,
                'chamber': rc.chamber,
            })
        data['roll_calls'] = roll_calls

        return Response(data)
    except Exception as e:
        logger.error(f"Bill detail error: {e}")
        return Response({'error': str(e)}, status=500)


# ─── Members ──────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([AllowAny])
def members_list(request):
    """List congress members with filters."""
    try:
        qs = CongressMember.objects.filter(in_office=True)

        state = request.query_params.get('state')
        if state:
            qs = qs.filter(state=state.upper())

        chamber = request.query_params.get('chamber')
        if chamber in ('house', 'senate'):
            qs = qs.filter(chamber=chamber)

        party = request.query_params.get('party')
        if party:
            qs = qs.filter(party__icontains=party)

        district = request.query_params.get('district')
        if district:
            qs = qs.filter(district=int(district))

        search = request.query_params.get('q')
        if search:
            qs = qs.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
            )

        members = qs.order_by('state', 'last_name')[:200]

        return Response({
            'members': [_member_to_dict(m) for m in members],
            'total': qs.count(),
        })
    except Exception as e:
        logger.error(f"Members list error: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def member_detail(request, bioguide_id):
    """Single member detail with voting record."""
    try:
        member = CongressMember.objects.filter(bioguide_id=bioguide_id).first()
        if not member:
            return Response({'error': 'Member not found'}, status=404)

        data = _member_to_dict(member)

        # Sponsored bills
        sponsored = member.sponsored_bills.order_by('-updated_at')[:20]
        data['sponsored_bills'] = [_bill_to_dict(b) for b in sponsored]

        # Recent votes
        positions = VotePosition.objects.filter(
            member=member
        ).select_related('roll_call', 'roll_call__bill').order_by('-roll_call__date')[:50]

        votes = []
        for vp in positions:
            rc = vp.roll_call
            votes.append({
                'position': vp.position,
                'date': rc.date.isoformat() if rc.date else None,
                'question': rc.question,
                'result': rc.result,
                'roll_number': rc.roll_number,
                'chamber': rc.chamber,
                'bill_uid': rc.bill.bill_uid if rc.bill else None,
                'bill_title': rc.bill.short_title if rc.bill else '',
            })
        data['votes'] = votes
        data['vote_count'] = VotePosition.objects.filter(member=member).count()

        return Response(data)
    except Exception as e:
        logger.error(f"Member detail error: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def states_list(request):
    """Return states that have members, for the state picker."""
    try:
        states = (
            CongressMember.objects
            .filter(in_office=True)
            .values('state')
            .annotate(count=Count('bioguide_id'))
            .order_by('state')
        )
        return Response({
            'states': [{'code': s['state'], 'count': s['count']} for s in states],
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def districts_list(request, state):
    """Return districts for a state (house only)."""
    try:
        districts = (
            CongressMember.objects
            .filter(in_office=True, state=state.upper(), chamber='house')
            .exclude(district__isnull=True)
            .values_list('district', flat=True)
            .order_by('district')
            .distinct()
        )
        return Response({
            'state': state.upper(),
            'districts': list(districts),
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)


# ─── Search (semantic) ────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([AllowAny])
def bill_search(request):
    """Semantic search over bill embeddings."""
    query = request.query_params.get('q', '').strip()
    if not query:
        return Response({'error': 'q parameter required'}, status=400)

    limit = min(int(request.query_params.get('limit', 10)), 50)

    try:
        from openai import OpenAI
        client = OpenAI()
        emb_resp = client.embeddings.create(input=[query], model="text-embedding-3-small")
        query_vec = emb_resp.data[0].embedding

        # pgvector cosine distance search
        from pgvector.django import CosineDistance
        results = (
            Bill.objects
            .filter(embedding__isnull=False)
            .annotate(distance=CosineDistance('embedding', query_vec))
            .order_by('distance')[:limit]
        )

        bills = []
        for b in results:
            d = _bill_to_dict(b)
            d['relevance'] = round(1 - b.distance, 4) if hasattr(b, 'distance') else None
            bills.append(d)

        return Response({'query': query, 'results': bills})
    except ImportError:
        # Fallback to text search if pgvector not available
        results = Bill.objects.filter(
            Q(title__icontains=query) | Q(plain_summary__icontains=query)
        )[:limit]
        return Response({'query': query, 'results': [_bill_to_dict(b) for b in results]})
    except Exception as e:
        logger.error(f"Bill search error: {e}")
        return Response({'error': str(e)}, status=500)


# ─── Helpers ──────────────────────────────────────────────────────────────

def _bill_to_dict(bill, full=False):
    d = {
        'id': bill.pk,
        'bill_uid': bill.bill_uid,
        'bill_number': f"{bill.bill_type}{bill.bill_number}" if bill.bill_type and bill.bill_number else bill.bill_uid,
        'title': bill.title,
        'short_title': bill.short_title,
        'description': bill.description,
        'status': bill.status,
        'chamber': bill.chamber,
        'introduced_date': bill.introduced_date.isoformat() if bill.introduced_date else None,
        'last_action': bill.last_action,
        'last_action_date': bill.last_action_date.isoformat() if bill.last_action_date else None,
        'topics': bill.topics or [],
        'sponsor_names': bill.sponsor_names or [],
        'congress_gov_url': bill.congress_gov_url,
        'source': bill.source,
        'updated_at': bill.updated_at.isoformat() if bill.updated_at else None,
    }
    if full:
        d['plain_summary'] = bill.plain_summary
        d['committee'] = bill.committee
        d['legiscan_url'] = bill.legiscan_url
        d['full_text_url'] = bill.full_text_url
        d['embedding_text'] = bill.embedding_text
    return d


def _member_to_dict(member):
    return {
        'bioguide_id': member.bioguide_id,
        'first_name': member.first_name,
        'last_name': member.last_name,
        'full_name': member.full_name,
        'party': member.party,
        'chamber': member.chamber,
        'state': member.state,
        'district': member.district,
        'photo_url': member.photo_url,
        'profile_url': member.profile_url,
        'leadership_role': member.leadership_role,
        'committees': member.committees or [],
    }
