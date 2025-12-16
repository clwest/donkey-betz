"""
Voice Marketplace API Endpoints - Session 440

Provides REST API endpoints for the AI Pixar voice marketplace:
- Browse and search voices
- Create voices from ElevenLabs clones
- Purchase voice generations
- Manage owned voices
- Track earnings and transactions
"""

import logging
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg, Sum
from django.utils import timezone

from core.models import VoiceProfile, VoiceTransaction, VoiceReview, VoiceCloneRequest

logger = logging.getLogger(__name__)


# ==================== BROWSE & SEARCH ====================

@csrf_exempt
@require_http_methods(["GET"])
def marketplace_browse(request):
    """
    Browse public voices in the marketplace.

    GET /api/voice-marketplace/

    Query params:
    - gender: Filter by gender (male, female, neutral)
    - age_range: Filter by age range
    - use_case: Filter by use case
    - search: Search by name or description
    - sort: Sort by (rating, uses, price, newest)
    - limit: Number of results (default 20)
    - offset: Pagination offset
    """
    try:
        # Start with public, active voices
        voices = VoiceProfile.objects.filter(is_public=True, is_active=True)

        # Apply filters
        gender = request.GET.get('gender')
        if gender:
            voices = voices.filter(gender=gender)

        age_range = request.GET.get('age_range')
        if age_range:
            voices = voices.filter(age_range=age_range)

        use_case = request.GET.get('use_case')
        if use_case:
            voices = voices.filter(primary_use_case=use_case)

        search = request.GET.get('search')
        if search:
            voices = voices.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(accent__icontains=search)
            )

        # Apply sorting
        sort = request.GET.get('sort', 'rating')
        sort_map = {
            'rating': '-average_rating',
            'uses': '-total_uses',
            'price': 'price',
            'price_desc': '-price',
            'newest': '-created_at',
        }
        voices = voices.order_by('-is_featured', sort_map.get(sort, '-average_rating'))

        # Pagination
        limit = min(int(request.GET.get('limit', 20)), 100)
        offset = int(request.GET.get('offset', 0))
        total = voices.count()
        voices = voices[offset:offset + limit]

        # Format response
        voice_list = []
        for voice in voices:
            voice_list.append({
                'id': str(voice.id),
                'name': voice.name,
                'description': voice.description[:200] if voice.description else '',
                'gender': voice.gender,
                'age_range': voice.age_range,
                'accent': voice.accent,
                'language': voice.language,
                'style_tags': voice.style_tags,
                'use_case': voice.primary_use_case,
                'price': str(voice.price),
                'pricing_model': voice.pricing_model,
                'price_display': voice.get_price_display(),
                'sample_url': voice.sample_audio_url,
                'sample_duration': voice.sample_duration_seconds,
                'total_uses': voice.total_uses,
                'average_rating': round(voice.average_rating, 1),
                'rating_count': voice.rating_count,
                'is_featured': voice.is_featured,
                'is_verified': voice.is_verified,
                'owner': voice.owner.username,
            })

        return JsonResponse({
            'success': True,
            'voices': voice_list,
            'total': total,
            'limit': limit,
            'offset': offset,
        })

    except Exception as e:
        logger.error(f"Error browsing marketplace: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def voice_detail(request, voice_id):
    """
    Get detailed information about a voice.

    GET /api/voice-marketplace/<voice_id>/
    """
    try:
        voice = VoiceProfile.objects.get(id=voice_id, is_active=True)

        # Check access - public voices or owner can view
        if not voice.is_public and (not request.user.is_authenticated or voice.owner != request.user):
            return JsonResponse({'success': False, 'error': 'Voice not found'}, status=404)

        # Get recent reviews
        reviews = voice.reviews.filter(is_active=True).order_by('-created_at')[:5]
        review_list = []
        for review in reviews:
            review_list.append({
                'id': str(review.id),
                'rating': review.rating,
                'title': review.title,
                'text': review.review_text,
                'use_case': review.use_case,
                'reviewer': review.reviewer.username,
                'verified_purchase': review.is_verified_purchase,
                'created_at': review.created_at.isoformat(),
            })

        return JsonResponse({
            'success': True,
            'voice': {
                'id': str(voice.id),
                'name': voice.name,
                'description': voice.description,
                'gender': voice.gender,
                'age_range': voice.age_range,
                'accent': voice.accent,
                'language': voice.language,
                'style_tags': voice.style_tags,
                'use_case': voice.primary_use_case,
                'price': str(voice.price),
                'pricing_model': voice.pricing_model,
                'price_display': voice.get_price_display(),
                'sample_url': voice.sample_audio_url,
                'sample_text': voice.sample_text,
                'sample_duration': voice.sample_duration_seconds,
                'total_uses': voice.total_uses,
                'total_minutes': float(voice.total_minutes_generated),
                'average_rating': round(voice.average_rating, 2),
                'rating_count': voice.rating_count,
                'is_featured': voice.is_featured,
                'is_verified': voice.is_verified,
                'creation_method': voice.creation_method,
                'owner': voice.owner.username,
                'created_at': voice.created_at.isoformat(),
            },
            'reviews': review_list,
        })

    except VoiceProfile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Voice not found'}, status=404)
    except Exception as e:
        logger.error(f"Error getting voice detail: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ==================== MY VOICES ====================

@login_required
@require_http_methods(["GET"])
def my_voices(request):
    """
    Get the current user's owned voices.

    GET /api/voice-marketplace/my-voices/
    """
    try:
        voices = VoiceProfile.objects.filter(owner=request.user, is_active=True)

        voice_list = []
        for voice in voices:
            voice_list.append({
                'id': str(voice.id),
                'name': voice.name,
                'elevenlabs_voice_id': voice.elevenlabs_voice_id,
                'gender': voice.gender or 'neutral',
                'primary_use_case': voice.primary_use_case or 'general',
                'is_public': voice.is_public,
                'price': str(voice.price),
                'pricing_model': voice.pricing_model,
                'total_uses': voice.total_uses,
                'total_revenue': str(voice.total_revenue),
                'average_rating': round(voice.average_rating, 1),
                'rating_count': voice.rating_count,
                'creation_method': voice.creation_method,
                'created_at': voice.created_at.isoformat(),
            })

        return JsonResponse({
            'success': True,
            'voices': voice_list,
        })

    except Exception as e:
        logger.error(f"Error getting my voices: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def publish_voice(request, voice_id):
    """
    Make a voice public for sale in the marketplace.

    POST /api/voice-marketplace/<voice_id>/publish/
    """
    try:
        import json
        data = json.loads(request.body) if request.body else {}

        voice = VoiceProfile.objects.get(id=voice_id, owner=request.user)

        # Update marketplace settings
        voice.is_public = True
        voice.price = Decimal(str(data.get('price', '0.50')))
        voice.pricing_model = data.get('pricing_model', 'per_minute')
        voice.save()

        logger.info(f"Voice {voice.name} published to marketplace by {request.user.username}")

        return JsonResponse({
            'success': True,
            'message': f'Voice "{voice.name}" is now available in the marketplace!',
            'voice_id': str(voice.id),
        })

    except VoiceProfile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Voice not found'}, status=404)
    except Exception as e:
        logger.error(f"Error publishing voice: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def unpublish_voice(request, voice_id):
    """
    Remove a voice from the public marketplace.

    POST /api/voice-marketplace/<voice_id>/unpublish/
    """
    try:
        voice = VoiceProfile.objects.get(id=voice_id, owner=request.user)
        voice.is_public = False
        voice.save()

        return JsonResponse({
            'success': True,
            'message': f'Voice "{voice.name}" removed from marketplace.',
        })

    except VoiceProfile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Voice not found'}, status=404)
    except Exception as e:
        logger.error(f"Error unpublishing voice: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["PUT", "PATCH"])
def update_voice(request, voice_id):
    """
    Update voice settings (name, description, price, etc.).

    PUT/PATCH /api/voice-marketplace/<voice_id>/
    """
    try:
        import json
        data = json.loads(request.body) if request.body else {}

        voice = VoiceProfile.objects.get(id=voice_id, owner=request.user)

        # Update allowed fields
        if 'name' in data:
            voice.name = data['name']
        if 'description' in data:
            voice.description = data['description']
        if 'price' in data:
            voice.price = Decimal(str(data['price']))
        if 'pricing_model' in data:
            voice.pricing_model = data['pricing_model']
        if 'style_tags' in data:
            voice.style_tags = data['style_tags']
        if 'primary_use_case' in data:
            voice.primary_use_case = data['primary_use_case']

        voice.save()

        return JsonResponse({
            'success': True,
            'message': 'Voice updated successfully.',
        })

    except VoiceProfile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Voice not found'}, status=404)
    except Exception as e:
        logger.error(f"Error updating voice: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ==================== VOICE GENERATION ====================

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def generate_speech(request, voice_id):
    """
    Generate speech using a marketplace voice.

    POST /api/voice-marketplace/<voice_id>/generate/

    Body:
    - text: Text to convert to speech
    - content_type: What it's being used for
    - project_id: Optional project reference
    """
    try:
        import json
        import httpx
        import os

        data = json.loads(request.body)
        text = data.get('text', '').strip()

        if not text:
            return JsonResponse({'success': False, 'error': 'Text is required'}, status=400)

        if len(text) > 5000:
            return JsonResponse({'success': False, 'error': 'Text too long (max 5000 chars)'}, status=400)

        voice = VoiceProfile.objects.get(id=voice_id, is_active=True)

        # Check if user can access this voice
        if not voice.is_public and voice.owner != request.user:
            return JsonResponse({'success': False, 'error': 'Voice not available'}, status=403)

        # Generate with ElevenLabs
        elevenlabs_key = os.getenv('ELEVENLABS_API_KEY') or os.getenv('ELEVEN_LABS_API')
        if not elevenlabs_key:
            return JsonResponse({'success': False, 'error': 'ElevenLabs not configured'}, status=500)

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice.elevenlabs_voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": elevenlabs_key,
        }
        payload = {
            "text": text,
            "model_id": "eleven_turbo_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }

        with httpx.Client() as client:
            response = client.post(url, json=payload, headers=headers, timeout=60.0)

        if response.status_code != 200:
            logger.error(f"ElevenLabs error: {response.status_code} - {response.text}")
            return JsonResponse({'success': False, 'error': 'Voice generation failed'}, status=500)

        audio_data = response.content
        duration_seconds = len(audio_data) // 32000  # Rough estimate

        # Create transaction if not owner's own voice
        transaction = None
        if voice.owner != request.user:
            transaction = VoiceTransaction.create_transaction(
                voice=voice,
                buyer=request.user,
                text=text,
                duration_seconds=duration_seconds,
                content_type=data.get('content_type', 'other'),
                project_id=data.get('project_id'),
            )

        # Return audio as base64
        import base64
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')

        return JsonResponse({
            'success': True,
            'audio': audio_base64,
            'audio_format': 'audio/mpeg',
            'duration_seconds': duration_seconds,
            'text_length': len(text),
            'transaction_id': str(transaction.id) if transaction else None,
            'cost': str(transaction.gross_price) if transaction else '0.00',
        })

    except VoiceProfile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Voice not found'}, status=404)
    except Exception as e:
        logger.error(f"Error generating speech: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def preview_voice(request, voice_id):
    """
    Generate a free preview of a voice (limited to 50 chars).

    POST /api/voice-marketplace/<voice_id>/preview/

    Body:
    - text: Short text for preview (max 50 chars)
    """
    try:
        import json
        import httpx
        import os
        import base64

        data = json.loads(request.body)
        text = data.get('text', 'Hello, this is a preview of my voice.').strip()[:50]

        voice = VoiceProfile.objects.get(id=voice_id, is_public=True, is_active=True)

        elevenlabs_key = os.getenv('ELEVENLABS_API_KEY') or os.getenv('ELEVEN_LABS_API')
        if not elevenlabs_key:
            return JsonResponse({'success': False, 'error': 'ElevenLabs not configured'}, status=500)

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice.elevenlabs_voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": elevenlabs_key,
        }
        payload = {
            "text": text,
            "model_id": "eleven_turbo_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }

        with httpx.Client() as client:
            response = client.post(url, json=payload, headers=headers, timeout=30.0)

        if response.status_code != 200:
            return JsonResponse({'success': False, 'error': 'Preview failed'}, status=500)

        audio_base64 = base64.b64encode(response.content).decode('utf-8')

        return JsonResponse({
            'success': True,
            'audio': audio_base64,
            'audio_format': 'audio/mpeg',
            'text': text,
        })

    except VoiceProfile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Voice not found'}, status=404)
    except Exception as e:
        logger.error(f"Error previewing voice: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ==================== REVIEWS ====================

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def add_review(request, voice_id):
    """
    Add a review for a voice.

    POST /api/voice-marketplace/<voice_id>/reviews/
    """
    try:
        import json
        data = json.loads(request.body)

        voice = VoiceProfile.objects.get(id=voice_id)

        # Check if already reviewed
        if VoiceReview.objects.filter(voice=voice, reviewer=request.user).exists():
            return JsonResponse({'success': False, 'error': 'Already reviewed'}, status=400)

        review = VoiceReview.objects.create(
            voice=voice,
            reviewer=request.user,
            rating=int(data.get('rating', 5)),
            title=data.get('title', ''),
            review_text=data.get('text', ''),
            use_case=data.get('use_case', ''),
            clarity_rating=data.get('clarity_rating'),
            naturalness_rating=data.get('naturalness_rating'),
            consistency_rating=data.get('consistency_rating'),
        )

        return JsonResponse({
            'success': True,
            'review_id': str(review.id),
            'message': 'Review added successfully.',
        })

    except VoiceProfile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Voice not found'}, status=404)
    except Exception as e:
        logger.error(f"Error adding review: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ==================== EARNINGS & TRANSACTIONS ====================

@login_required
@require_http_methods(["GET"])
def earnings_summary(request):
    """
    Get earnings summary for the current user's voices.

    GET /api/voice-marketplace/earnings/
    """
    try:
        # Get all voices owned by user
        voices = VoiceProfile.objects.filter(owner=request.user, is_active=True)

        # Calculate totals
        total_revenue = voices.aggregate(total=Sum('total_revenue'))['total'] or Decimal('0')
        total_uses = voices.aggregate(total=Sum('total_uses'))['total'] or 0

        # Get recent transactions
        transactions = VoiceTransaction.objects.filter(
            voice__owner=request.user
        ).order_by('-created_at')[:20]

        transaction_list = []
        for tx in transactions:
            transaction_list.append({
                'id': str(tx.id),
                'voice_name': tx.voice.name,
                'buyer': tx.buyer.username,
                'gross_price': str(tx.gross_price),
                'owner_payout': str(tx.owner_payout),
                'payout_status': tx.payout_status,
                'text_length': tx.text_length,
                'duration': tx.audio_duration_seconds,
                'created_at': tx.created_at.isoformat(),
            })

        # Per-voice breakdown
        voice_breakdown = []
        for voice in voices:
            voice_breakdown.append({
                'id': str(voice.id),
                'name': voice.name,
                'total_revenue': str(voice.total_revenue),
                'total_uses': voice.total_uses,
                'is_public': voice.is_public,
            })

        return JsonResponse({
            'success': True,
            'total_revenue': str(total_revenue),
            'total_uses': total_uses,
            'voice_count': voices.count(),
            'voices': voice_breakdown,
            'recent_transactions': transaction_list,
        })

    except Exception as e:
        logger.error(f"Error getting earnings: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def transaction_history(request):
    """
    Get the user's purchase history.

    GET /api/voice-marketplace/transactions/
    """
    try:
        transactions = VoiceTransaction.objects.filter(
            buyer=request.user
        ).order_by('-created_at')[:50]

        transaction_list = []
        for tx in transactions:
            transaction_list.append({
                'id': str(tx.id),
                'voice_name': tx.voice.name,
                'voice_owner': tx.voice.owner.username,
                'gross_price': str(tx.gross_price),
                'text_length': tx.text_length,
                'duration': tx.audio_duration_seconds,
                'content_type': tx.content_type,
                'created_at': tx.created_at.isoformat(),
            })

        return JsonResponse({
            'success': True,
            'transactions': transaction_list,
        })

    except Exception as e:
        logger.error(f"Error getting transactions: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ==================== VOICE CLONING ====================

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def create_voice_from_elevenlabs(request):
    """
    Create a VoiceProfile from an existing ElevenLabs voice ID.

    POST /api/voice-marketplace/create/

    Body:
    - elevenlabs_voice_id: The ElevenLabs voice ID
    - name: Display name for the voice
    - description: Voice description
    - gender: male/female/neutral
    - age_range: Age range
    - creation_method: How it was created
    """
    try:
        import json
        data = json.loads(request.body)

        elevenlabs_voice_id = data.get('elevenlabs_voice_id')
        if not elevenlabs_voice_id:
            return JsonResponse({'success': False, 'error': 'elevenlabs_voice_id required'}, status=400)

        # Check if already exists
        if VoiceProfile.objects.filter(elevenlabs_voice_id=elevenlabs_voice_id).exists():
            return JsonResponse({'success': False, 'error': 'Voice already registered'}, status=400)

        voice = VoiceProfile.objects.create(
            owner=request.user,
            elevenlabs_voice_id=elevenlabs_voice_id,
            name=data.get('name', 'My Voice'),
            description=data.get('description', ''),
            gender=data.get('gender', 'neutral'),
            age_range=data.get('age_range', 'adult'),
            accent=data.get('accent', ''),
            language=data.get('language', 'English'),
            style_tags=data.get('style_tags', []),
            primary_use_case=data.get('primary_use_case', 'general'),
            creation_method=data.get('creation_method', 'web_clone'),
        )

        logger.info(f"Created voice profile {voice.name} for user {request.user.username}")

        return JsonResponse({
            'success': True,
            'voice_id': str(voice.id),
            'name': voice.name,
            'message': 'Voice profile created successfully!',
        })

    except Exception as e:
        logger.error(f"Error creating voice: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ==================== VOICE CLONE REQUESTS ====================

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def start_clone_request(request):
    """
    Start a voice clone request from Discord.

    POST /api/voice-marketplace/clone/start/
    """
    try:
        import json
        data = json.loads(request.body)

        clone_request = VoiceCloneRequest.objects.create(
            user=request.user,
            discord_user_id=data.get('discord_user_id', ''),
            discord_guild_id=data.get('discord_guild_id', ''),
            discord_channel_id=data.get('discord_channel_id', ''),
        )

        return JsonResponse({
            'success': True,
            'request_id': str(clone_request.id),
            'status': clone_request.status,
        })

    except Exception as e:
        logger.error(f"Error starting clone request: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def clone_request_status(request, request_id):
    """
    Get the status of a voice clone request.

    GET /api/voice-marketplace/clone/<request_id>/status/
    """
    try:
        clone_request = VoiceCloneRequest.objects.get(id=request_id, user=request.user)

        return JsonResponse({
            'success': True,
            'status': clone_request.status,
            'duration': clone_request.recording_duration_seconds,
            'voice_id': str(clone_request.voice_profile.id) if clone_request.voice_profile else None,
            'error': clone_request.error_message,
        })

    except VoiceCloneRequest.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Request not found'}, status=404)
    except Exception as e:
        logger.error(f"Error getting clone status: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
