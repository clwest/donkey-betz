"""
Session 258: Agent Predictions / Prophecies API Views

Agents make predictions about trends, opportunities, and future events.
System tracks accuracy over time to build trust in agent insights.
"""

import json
import logging
import uuid
from datetime import timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Count

from .models_unified_system import (
    Agent,
    AgentPrediction,
    PredictionStats,
    PredictionComment,
    PredictionFollowUp,
    AgentDream,
)

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET"])
def predictions_overview(request):
    """
    GET /api/predictions/

    Get overview of all predictions across all agents.
    """
    try:
        # Overall stats
        predictions = AgentPrediction.objects.all()
        total = predictions.count()
        pending = predictions.filter(status='pending').count()
        verified_true = predictions.filter(status='verified_true').count()
        verified_false = predictions.filter(status='verified_false').count()
        partially_true = predictions.filter(status='partially_true').count()

        # Calculate overall accuracy
        verified_count = verified_true + verified_false + partially_true
        overall_accuracy = verified_true / verified_count if verified_count > 0 else 0

        # Get agents with predictions
        agents_with_predictions = predictions.values('agent').distinct().count()

        # Featured predictions
        featured = predictions.filter(is_featured=True).order_by('-created_at')[:5]
        featured_list = [p.to_dict() for p in featured]

        # Recent predictions
        recent = predictions.order_by('-created_at')[:10]
        recent_list = [p.to_dict() for p in recent]

        # Upcoming deadlines
        now = timezone.now()
        upcoming = predictions.filter(
            status='pending',
            deadline__gte=now,
            deadline__lte=now + timedelta(days=30)
        ).order_by('deadline')[:10]
        upcoming_list = [p.to_dict() for p in upcoming]

        # Category breakdown
        category_stats = predictions.values('category').annotate(
            count=Count('id')
        ).order_by('-count')

        # Top predictors (by accuracy)
        top_predictors = PredictionStats.objects.filter(
            verified_predictions__gte=3
        ).order_by('-overall_accuracy')[:5]
        top_list = [{
            'agent_id': str(s.agent.id),
            'agent_name': s.agent.name,
            'accuracy': s.overall_accuracy,
            'predictions': s.total_predictions,
            'tier': s.get_accuracy_tier(),
            'emoji': s.get_tier_emoji(),
        } for s in top_predictors]

        return JsonResponse({
            'success': True,
            'stats': {
                'total_predictions': total,
                'pending': pending,
                'verified_true': verified_true,
                'verified_false': verified_false,
                'partially_true': partially_true,
                'overall_accuracy': round(overall_accuracy, 2),
                'agents_with_predictions': agents_with_predictions,
            },
            'category_breakdown': list(category_stats),
            'featured': featured_list,
            'recent': recent_list,
            'upcoming_deadlines': upcoming_list,
            'top_predictors': top_list,
        })

    except Exception as e:
        logger.error(f"Error in predictions_overview: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def agent_predictions(request, agent_id):
    """
    GET /api/predictions/agent/<agent_id>/
    - Get all predictions for a specific agent

    POST /api/predictions/agent/<agent_id>/
    - Create a new prediction for an agent (or generate one via AI)
    """
    try:
        agent = Agent.objects.get(id=agent_id)
    except Agent.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Agent not found'}, status=404)

    if request.method == 'GET':
        # Get filter parameters
        status = request.GET.get('status')
        category = request.GET.get('category')
        limit = int(request.GET.get('limit', 20))

        predictions = AgentPrediction.objects.filter(agent=agent)

        if status:
            predictions = predictions.filter(status=status)
        if category:
            predictions = predictions.filter(category=category)

        predictions = predictions.order_by('-created_at')[:limit]

        # Get agent's prediction stats
        stats, _ = PredictionStats.objects.get_or_create(agent=agent)

        return JsonResponse({
            'success': True,
            'agent': {
                'id': str(agent.id),
                'name': agent.name,
            },
            'stats': {
                'total': stats.total_predictions,
                'pending': stats.pending_predictions,
                'verified': stats.verified_predictions,
                'accuracy': stats.overall_accuracy,
                'tier': stats.get_accuracy_tier(),
                'tier_emoji': stats.get_tier_emoji(),
                'current_streak': stats.current_streak,
                'best_streak': stats.best_streak,
            },
            'predictions': [p.to_dict() for p in predictions],
        })

    elif request.method == 'POST':
        # Create new prediction
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

        # If auto_generate is True, use AI to generate prediction
        if data.get('auto_generate'):
            prediction = generate_agent_prediction(agent, data.get('context', {}))
            if prediction:
                return JsonResponse({
                    'success': True,
                    'message': 'Prediction generated',
                    'prediction': prediction.to_dict(),
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Failed to generate prediction'
                }, status=500)

        # Manual prediction creation
        title = data.get('title')
        prediction_text = data.get('prediction')

        if not title or not prediction_text:
            return JsonResponse({
                'success': False,
                'error': 'Title and prediction are required'
            }, status=400)

        # Calculate deadline from timeframe
        timeframe = data.get('timeframe', 'quarter')
        deadline = calculate_deadline(timeframe)

        prediction = AgentPrediction.objects.create(
            agent=agent,
            title=title,
            prediction=prediction_text,
            category=data.get('category', 'general'),
            tags=data.get('tags', []),
            source=data.get('source', 'external'),
            source_reference=data.get('source_reference', {}),
            confidence=data.get('confidence', 0.7),
            timeframe=timeframe,
            deadline=deadline,
        )

        # Update agent stats
        stats, _ = PredictionStats.objects.get_or_create(agent=agent)
        stats.update_stats()

        return JsonResponse({
            'success': True,
            'message': 'Prediction created',
            'prediction': prediction.to_dict(),
        })


@csrf_exempt
@require_http_methods(["GET", "PATCH", "DELETE"])
def prediction_detail(request, prediction_id):
    """
    GET /api/predictions/<prediction_id>/
    - Get prediction details

    PATCH /api/predictions/<prediction_id>/
    - Update prediction (e.g., mark as featured)

    DELETE /api/predictions/<prediction_id>/
    - Delete prediction
    """
    try:
        prediction = AgentPrediction.objects.get(id=prediction_id)
    except AgentPrediction.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Prediction not found'}, status=404)

    if request.method == 'GET':
        # Increment view count
        prediction.views += 1
        prediction.save(update_fields=['views'])

        # Get comments
        comments = PredictionComment.objects.filter(prediction=prediction)
        comments_list = [{
            'id': str(c.id),
            'author_type': c.author_type,
            'author_name': c.user.username if c.user else (c.agent.name if c.agent else 'Unknown'),
            'content': c.content,
            'sentiment': c.sentiment,
            'created_at': c.created_at.isoformat(),
        } for c in comments]

        # Get follow-ups
        follow_ups = PredictionFollowUp.objects.filter(original=prediction)
        follow_ups_list = [{
            'id': str(f.id),
            'relationship': f.relationship,
            'follow_up_prediction': f.follow_up.to_dict(),
            'explanation': f.explanation,
        } for f in follow_ups]

        return JsonResponse({
            'success': True,
            'prediction': prediction.to_dict(),
            'comments': comments_list,
            'follow_ups': follow_ups_list,
        })

    elif request.method == 'PATCH':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

        # Update allowed fields
        if 'is_featured' in data:
            prediction.is_featured = data['is_featured']
        if 'tags' in data:
            prediction.tags = data['tags']

        prediction.save()

        return JsonResponse({
            'success': True,
            'prediction': prediction.to_dict(),
        })

    elif request.method == 'DELETE':
        agent = prediction.agent
        prediction.delete()

        # Update stats
        stats, _ = PredictionStats.objects.get_or_create(agent=agent)
        stats.update_stats()

        return JsonResponse({
            'success': True,
            'message': 'Prediction deleted',
        })


@csrf_exempt
@require_http_methods(["POST"])
def verify_prediction(request, prediction_id):
    """
    POST /api/predictions/<prediction_id>/verify/

    Verify a prediction outcome (true, false, partial).
    """
    try:
        prediction = AgentPrediction.objects.get(id=prediction_id)
    except AgentPrediction.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Prediction not found'}, status=404)

    if prediction.status != 'pending':
        return JsonResponse({
            'success': False,
            'error': f'Prediction already verified as {prediction.status}'
        }, status=400)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

    outcome = data.get('outcome')  # 'true', 'false', 'partial'
    if outcome not in ['true', 'false', 'partial']:
        return JsonResponse({
            'success': False,
            'error': 'Outcome must be true, false, or partial'
        }, status=400)

    success = prediction.verify(
        outcome=outcome,
        notes=data.get('notes', ''),
        evidence=data.get('evidence'),
        verified_by='user',
        accuracy=data.get('accuracy', 0.5) if outcome == 'partial' else None,
    )

    if success:
        return JsonResponse({
            'success': True,
            'message': f'Prediction verified as {outcome}',
            'prediction': prediction.to_dict(),
        })
    else:
        return JsonResponse({
            'success': False,
            'error': 'Failed to verify prediction'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def upvote_prediction(request, prediction_id):
    """
    POST /api/predictions/<prediction_id>/upvote/

    Upvote a prediction.
    """
    try:
        prediction = AgentPrediction.objects.get(id=prediction_id)
    except AgentPrediction.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Prediction not found'}, status=404)

    prediction.upvotes += 1
    prediction.save(update_fields=['upvotes'])

    return JsonResponse({
        'success': True,
        'upvotes': prediction.upvotes,
    })


@csrf_exempt
@require_http_methods(["POST"])
def add_comment(request, prediction_id):
    """
    POST /api/predictions/<prediction_id>/comment/

    Add a comment to a prediction.
    """
    try:
        prediction = AgentPrediction.objects.get(id=prediction_id)
    except AgentPrediction.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Prediction not found'}, status=404)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

    content = data.get('content')
    if not content:
        return JsonResponse({'success': False, 'error': 'Content required'}, status=400)

    comment = PredictionComment.objects.create(
        prediction=prediction,
        author_type='user',
        user=request.user if request.user.is_authenticated else None,
        content=content,
        sentiment=data.get('sentiment', 'neutral'),
    )

    return JsonResponse({
        'success': True,
        'comment': {
            'id': str(comment.id),
            'content': comment.content,
            'sentiment': comment.sentiment,
            'created_at': comment.created_at.isoformat(),
        },
    })


@csrf_exempt
@require_http_methods(["GET"])
def prediction_leaderboard(request):
    """
    GET /api/predictions/leaderboard/

    Get agent prediction accuracy leaderboard.
    """
    try:
        # Filter for agents with enough predictions
        min_predictions = int(request.GET.get('min_predictions', 3))

        stats = PredictionStats.objects.filter(
            verified_predictions__gte=min_predictions
        ).order_by('-overall_accuracy', '-total_predictions')

        leaderboard = []
        for rank, s in enumerate(stats, 1):
            leaderboard.append({
                'rank': rank,
                'agent_id': str(s.agent.id),
                'agent_name': s.agent.name,
                'total_predictions': s.total_predictions,
                'verified_predictions': s.verified_predictions,
                'accuracy': round(s.overall_accuracy, 2),
                'weighted_accuracy': round(s.weighted_accuracy, 2),
                'tier': s.get_accuracy_tier(),
                'tier_emoji': s.get_tier_emoji(),
                'current_streak': s.current_streak,
                'best_streak': s.best_streak,
                'category_accuracy': s.category_accuracy,
            })

        return JsonResponse({
            'success': True,
            'leaderboard': leaderboard,
            'min_predictions_required': min_predictions,
        })

    except Exception as e:
        logger.error(f"Error in prediction_leaderboard: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def generate_predictions_from_dreams(request):
    """
    POST /api/predictions/generate-from-dreams/

    Convert agent dreams (especially 'prediction' type) into formal predictions.
    """
    try:
        data = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        data = {}

    agent_id = data.get('agent_id')
    limit = data.get('limit', 10)

    # Get prediction-type dreams that haven't been converted
    # Note: We get existing dream IDs from predictions and filter them out
    existing_dream_ids = set()
    for pred in AgentPrediction.objects.filter(source='dream'):
        if pred.source_reference and 'dream_id' in pred.source_reference:
            existing_dream_ids.add(pred.source_reference['dream_id'])

    dreams_query = AgentDream.objects.filter(
        dream_type='prediction'
    ).exclude(
        id__in=[uuid.UUID(did) for did in existing_dream_ids if did]
    )

    if agent_id:
        dreams_query = dreams_query.filter(agent_id=agent_id)

    dreams = dreams_query.order_by('-dreamed_at')[:limit]

    created_predictions = []

    for dream in dreams:
        # Session 692: Calculate confidence from dream scores instead of hardcoding 0.6
        # Weight: 40% vividness, 30% creativity, 30% actionability
        vividness = getattr(dream, 'vividness_score', 0.7) or 0.7
        creativity = getattr(dream, 'creativity_score', 0.7) or 0.7
        actionability = getattr(dream, 'actionability_score', 0.5) or 0.5

        # Calculate weighted confidence (0.4-0.95 range)
        raw_confidence = (vividness * 0.4) + (creativity * 0.3) + (actionability * 0.3)
        # Scale to 0.4-0.95 range (never too low, never certain)
        confidence = 0.4 + (raw_confidence * 0.55)
        confidence = round(min(0.95, max(0.4, confidence)), 2)

        # Create prediction from dream
        prediction = AgentPrediction.objects.create(
            agent=dream.agent,
            title=dream.title[:200],
            prediction=dream.content,
            category=map_dream_to_category(dream),
            tags=dream.related_topics if dream.related_topics else [],
            source='dream',
            source_reference={'dream_id': str(dream.id)},
            confidence=confidence,  # Session 692: Dynamic confidence from dream scores
            timeframe='quarter',
            deadline=timezone.now() + timedelta(days=90),
        )
        created_predictions.append(prediction.to_dict())

        # Update agent stats
        stats, _ = PredictionStats.objects.get_or_create(agent=dream.agent)
        stats.update_stats()

    return JsonResponse({
        'success': True,
        'message': f'Created {len(created_predictions)} predictions from dreams',
        'predictions': created_predictions,
    })


@csrf_exempt
@require_http_methods(["POST"])
def expire_old_predictions(request):
    """
    POST /api/predictions/expire-old/

    Mark predictions past their deadline as expired.
    (Should be called by Celery Beat periodically)
    """
    try:
        now = timezone.now()

        # Find pending predictions past deadline
        expired = AgentPrediction.objects.filter(
            status='pending',
            deadline__lt=now
        )

        count = expired.count()
        expired.update(status='expired')

        # Update all affected agent stats
        agent_ids = expired.values_list('agent_id', flat=True).distinct()
        for agent_id in agent_ids:
            try:
                stats = PredictionStats.objects.get(agent_id=agent_id)
                stats.update_stats()
            except PredictionStats.DoesNotExist:
                pass

        return JsonResponse({
            'success': True,
            'message': f'Marked {count} predictions as expired',
        })

    except Exception as e:
        logger.error(f"Error in expire_old_predictions: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def calculate_deadline(timeframe):
    """Calculate deadline from timeframe string."""
    now = timezone.now()
    timeframe_days = {
        'week': 7,
        'month': 30,
        'quarter': 90,
        'half_year': 180,
        'year': 365,
        'long_term': 730,  # 2 years
    }
    days = timeframe_days.get(timeframe, 90)
    return now + timedelta(days=days)


def map_dream_to_category(dream):
    """Map dream content to prediction category."""
    content = (dream.title + ' ' + dream.content).lower()

    if any(word in content for word in ['trend', 'trending', 'popular']):
        return 'trend'
    elif any(word in content for word in ['market', 'industry', 'business', 'growth']):
        return 'market'
    elif any(word in content for word in ['technology', 'tech', 'ai', 'software']):
        return 'technology'
    elif any(word in content for word in ['design', 'style', 'creative', 'art']):
        return 'creative'
    elif any(word in content for word in ['opportunity', 'demand', 'need']):
        return 'opportunity'
    elif any(word in content for word in ['user', 'people', 'behavior', 'preference']):
        return 'user_behavior'
    elif any(word in content for word in ['season', 'summer', 'winter', 'spring', 'fall']):
        return 'seasonal'
    elif any(word in content for word in ['competitor', 'competition', 'rival']):
        return 'competition'
    else:
        return 'general'


def generate_agent_prediction(agent, context=None):
    """
    Use GPT-4o-mini to generate a prediction based on agent's specialization.
    """
    from core.services.openai_client_factory import get_openai_client
    import os

    try:
        client = get_openai_client(api_key=os.environ.get('OPENAI_API_KEY'))

        # Get agent's recent memories and dreams for context
        from .models_unified_system import AgentMemory

        # Session 810: Defer embedding fields to reduce egress costs
        recent_memories = AgentMemory.objects.defer('embedding').filter(
            agent=agent
        ).order_by('-importance', '-created_at')[:5]

        memory_context = "\n".join([
            f"- {m.content[:200]}" for m in recent_memories
        ]) if recent_memories else "No recent memories."

        recent_dreams = AgentDream.objects.filter(
            agent=agent
        ).order_by('-created_at')[:3]

        dream_context = "\n".join([
            f"- {d.title}: {d.content[:150]}" for d in recent_dreams
        ]) if recent_dreams else "No recent dreams."

        prompt = f"""You are {agent.name}, an AI agent specializing in {agent.specialization or 'general tasks'}.

Based on your knowledge, recent memories, and observations, make a specific, verifiable prediction about something that will happen in the next 1-3 months.

Your Recent Memories:
{memory_context}

Your Recent Dreams/Thoughts:
{dream_context}

Additional Context: {json.dumps(context) if context else 'None'}

Generate a prediction in the following JSON format:
{{
    "title": "Short, catchy prediction title (max 200 chars)",
    "prediction": "Detailed prediction statement explaining what you predict will happen and why",
    "category": "One of: trend, market, technology, creative, opportunity, user_behavior, seasonal, competition, general",
    "confidence": 0.7,  // Your confidence level 0.0-1.0
    "timeframe": "quarter",  // week, month, quarter, half_year, year, long_term
    "tags": ["tag1", "tag2"]  // Relevant keywords
}}

Make your prediction specific enough to be verifiable. Avoid vague statements."""

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": "You are an AI agent making predictions. Respond only with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=500,
        )

        result = json.loads(response.choices[0].message.content)

        # Create the prediction
        prediction = AgentPrediction.objects.create(
            agent=agent,
            title=result.get('title', 'AI Generated Prediction')[:200],
            prediction=result.get('prediction', ''),
            category=result.get('category', 'general'),
            tags=result.get('tags', []),
            source='intuition',
            source_reference={'auto_generated': True},
            confidence=min(1.0, max(0.0, result.get('confidence', 0.7))),
            timeframe=result.get('timeframe', 'quarter'),
            deadline=calculate_deadline(result.get('timeframe', 'quarter')),
        )

        # Update stats
        stats, _ = PredictionStats.objects.get_or_create(agent=agent)
        stats.update_stats()

        return prediction

    except Exception as e:
        logger.error(f"Error generating prediction: {e}")
        return None
