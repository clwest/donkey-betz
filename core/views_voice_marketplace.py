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
from core.auth_middleware import token_auth_required
from django.db.models import Q, Sum

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

@token_auth_required
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


@token_auth_required
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


@token_auth_required
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


@token_auth_required
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

@token_auth_required
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

@token_auth_required
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

@token_auth_required
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


@token_auth_required
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

@token_auth_required
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

@token_auth_required
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


@token_auth_required
@csrf_exempt
@require_http_methods(["POST"])
def clone_voice_upload(request):
    """
    Clone a voice from an uploaded audio file via ElevenLabs IVC API.

    POST /api/voice-marketplace/clone/upload/

    Form Data:
    - audio: Audio file (WAV, MP3, M4A - max 10MB)
    - name: Display name for the cloned voice
    - description: Voice description (optional)
    - gender: male/female/neutral (optional, default neutral)
    - age_range: child/teen/young_adult/adult/senior (optional, default adult)
    - accent: Accent description (optional)
    - primary_use_case: narration/podcast/gaming/commercial/assistant/general (optional)
    - consent: Must be "true" - user confirms they own or have rights to this voice
    """
    import os
    import tempfile

    try:
        audio_file = request.FILES.get('audio')
        if not audio_file:
            return JsonResponse({
                'success': False,
                'error': 'Audio file is required. Upload a WAV, MP3, or M4A file.'
            }, status=400)

        # Validate consent
        consent = request.POST.get('consent', '').lower()
        if consent != 'true':
            return JsonResponse({
                'success': False,
                'error': 'You must confirm you own or have rights to clone this voice.'
            }, status=400)

        # Validate file size (10MB max for ElevenLabs)
        if audio_file.size > 10 * 1024 * 1024:
            return JsonResponse({
                'success': False,
                'error': 'Audio file too large. Maximum size is 10MB.'
            }, status=400)

        # Validate file type
        allowed_types = ['audio/wav', 'audio/mpeg', 'audio/mp3', 'audio/mp4',
                         'audio/x-wav', 'audio/x-m4a', 'audio/m4a', 'audio/ogg',
                         'audio/webm', 'audio/flac']
        content_type = audio_file.content_type or ''
        file_ext = os.path.splitext(audio_file.name)[1].lower()
        allowed_exts = ['.wav', '.mp3', '.m4a', '.ogg', '.webm', '.flac']

        if content_type not in allowed_types and file_ext not in allowed_exts:
            return JsonResponse({
                'success': False,
                'error': f'Unsupported audio format: {content_type or file_ext}. '
                         f'Supported: WAV, MP3, M4A, OGG, WebM, FLAC.'
            }, status=400)

        voice_name = request.POST.get('name', '').strip()
        if not voice_name:
            voice_name = f"{request.user.username}'s Voice"

        description = request.POST.get('description', '').strip()
        gender = request.POST.get('gender', 'neutral')
        age_range = request.POST.get('age_range', 'adult')
        accent = request.POST.get('accent', '')
        primary_use_case = request.POST.get('primary_use_case', 'general')

        # Create a VoiceCloneRequest to track the process
        clone_request = VoiceCloneRequest.objects.create(
            user=request.user,
            discord_user_id='',
            discord_guild_id='',
            discord_channel_id='',
            status='processing',
        )

        # Save uploaded file to temp location
        suffix = file_ext if file_ext else '.wav'
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            for chunk in audio_file.chunks():
                tmp.write(chunk)
            temp_path = tmp.name

        clone_request.audio_file_path = temp_path
        clone_request.save(update_fields=['audio_file_path', 'updated_at'])

        # Clone via ElevenLabs IVC API
        elevenlabs_key = os.getenv('ELEVENLABS_API_KEY') or os.getenv('ELEVEN_LABS_API')
        if not elevenlabs_key:
            clone_request.mark_failed('ElevenLabs API key not configured')
            return JsonResponse({
                'success': False,
                'error': 'Voice cloning service is not configured.'
            }, status=500)

        import httpx

        # Determine content type for upload
        ext_to_mime = {
            '.wav': 'audio/wav', '.mp3': 'audio/mpeg', '.m4a': 'audio/mp4',
            '.ogg': 'audio/ogg', '.webm': 'audio/webm', '.flac': 'audio/flac',
        }
        upload_content_type = ext_to_mime.get(suffix, content_type or 'audio/wav')

        with open(temp_path, 'rb') as f:
            file_content = f.read()

        clone_request.status = 'cloning'
        clone_request.save(update_fields=['status', 'updated_at'])

        data = {
            'name': voice_name,
            'remove_background_noise': 'true',
        }
        if description:
            data['description'] = description

        headers = {'xi-api-key': elevenlabs_key}
        files = [('files', (audio_file.name, file_content, upload_content_type))]

        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                'https://api.elevenlabs.io/v1/voices/add',
                data=data,
                files=files,
                headers=headers,
            )

        # Clean up temp file
        try:
            os.unlink(temp_path)
        except Exception:
            pass

        if response.status_code != 200:
            error_detail = response.text[:300]
            logger.error(f"ElevenLabs clone error: {response.status_code} - {error_detail}")
            clone_request.mark_failed(f'ElevenLabs API error ({response.status_code}): {error_detail}')
            return JsonResponse({
                'success': False,
                'error': f'Voice cloning failed: {error_detail}'
            }, status=500)

        result = response.json()
        elevenlabs_voice_id = result.get('voice_id')

        if not elevenlabs_voice_id:
            clone_request.mark_failed('No voice_id returned from ElevenLabs')
            return JsonResponse({
                'success': False,
                'error': 'Voice cloning succeeded but no voice ID was returned.'
            }, status=500)

        # Create VoiceProfile
        voice_profile = VoiceProfile.objects.create(
            owner=request.user,
            elevenlabs_voice_id=elevenlabs_voice_id,
            name=voice_name,
            description=description,
            gender=gender,
            age_range=age_range,
            accent=accent,
            language='English',
            primary_use_case=primary_use_case,
            creation_method='web_clone',
        )

        # Link clone request to voice profile
        clone_request.complete(voice_profile)

        logger.info(
            f"Voice cloned successfully: {voice_name} (ElevenLabs ID: {elevenlabs_voice_id}) "
            f"for user {request.user.username}"
        )

        return JsonResponse({
            'success': True,
            'voice_id': str(voice_profile.id),
            'elevenlabs_voice_id': elevenlabs_voice_id,
            'name': voice_name,
            'request_id': str(clone_request.id),
            'message': f'Voice "{voice_name}" cloned successfully!',
        })

    except Exception as e:
        logger.error(f"Error cloning voice: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@token_auth_required
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


# ==================== CATEGORIES & STATS ====================
# Session 745: Added missing endpoints for frontend

@csrf_exempt
@require_http_methods(["GET"])
def marketplace_categories(request):
    """
    Get all available voice categories/use cases.

    GET /api/voice-marketplace/categories/
    """
    try:
        # Get distinct categories from existing voices
        categories = list(VoiceProfile.objects.filter(
            is_public=True, is_active=True
        ).values_list('primary_use_case', flat=True).distinct())

        # Add standard categories if not present
        standard_categories = [
            'general', 'narration', 'podcast', 'gaming', 'character',
            'audiobook', 'commercial', 'documentary', 'educational'
        ]
        for cat in standard_categories:
            if cat not in categories:
                categories.append(cat)

        return JsonResponse({
            'success': True,
            'categories': sorted(categories),
        })

    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def marketplace_stats(request):
    """
    Get overall marketplace statistics.

    GET /api/voice-marketplace/stats/
    """
    try:
        from django.db.models import Avg, Count

        # Overall stats
        total_voices = VoiceProfile.objects.filter(is_active=True).count()
        published_voices = VoiceProfile.objects.filter(is_public=True, is_active=True).count()

        # Aggregate stats
        aggregates = VoiceProfile.objects.filter(is_public=True, is_active=True).aggregate(
            total_downloads=Sum('total_uses'),
            avg_rating=Avg('average_rating'),
            total_reviews=Count('reviews'),
        )

        return JsonResponse({
            'success': True,
            'total_voices': total_voices,
            'published_voices': published_voices,
            'total_downloads': aggregates['total_downloads'] or 0,
            'total_purchases': aggregates['total_downloads'] or 0,  # Same as downloads for now
            'average_rating': round(aggregates['avg_rating'] or 0, 2),
            'total_reviews': aggregates['total_reviews'] or 0,
        })

    except Exception as e:
        logger.error(f"Error getting marketplace stats: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def marketplace_purchases(request):
    """
    Get user's voice purchases.

    GET /api/voice-marketplace/purchases/

    Session 745: Added for frontend Purchases tab.
    """
    try:
        # Return empty list for anonymous users
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': True,
                'purchases': [],
                'total': 0,
            })

        # Get user's voice transactions (purchases)
        transactions = VoiceTransaction.objects.filter(
            buyer=request.user,
        ).select_related('voice').order_by('-created_at')

        purchases = []
        for txn in transactions:
            voice = txn.voice
            purchases.append({
                'id': str(txn.id),
                'voice_id': str(voice.id) if voice else None,
                'voice_name': voice.name if voice else 'Unknown',
                'voice_thumbnail': getattr(voice, 'preview_image_url', None) if voice else None,
                'amount': float(getattr(txn, 'amount', 0) or 0),
                'currency': getattr(txn, 'currency', 'USD'),
                'purchased_at': txn.created_at.isoformat(),
                'status': getattr(txn, 'status', 'completed'),
                'generations_remaining': None,
            })

        return JsonResponse({
            'success': True,
            'purchases': purchases,
            'total': len(purchases),
        })

    except Exception as e:
        logger.error(f"Error getting purchases: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
