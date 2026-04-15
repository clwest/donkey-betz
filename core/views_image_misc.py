"""
Image views — misc functions.
"""

"""
Image Generation Views
Phase 2: Frontend Reality Fix - Image Generation

Handles image generation requests using:
- Stability AI (Stable Diffusion) - Primary
- Replicate API - Fallback

Created: September 30, 2025
"""

import os
import logging
import requests
import uuid
import json
import zipfile
import base64
from openai import OpenAI
from io import BytesIO
from datetime import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils import timezone  # Session 96 Weekend Project
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from PIL import Image as PILImage

# Phase 2 P1: Rate limiting for image operations
from core.decorators import rate_limit
# Phase 2 P1: Input validation
from core.validators import validate_prompt, sanitize_prompt, validate_uuid, validate_numeric_range
# Phase 2 P1: Safe error handling
# Session 487: Creator watermark integration
from core.services.watermark_integration import save_watermarked_image
# Session 769: Cost tracking for external APIs
from core.services.api_cost_config import calculate_stability_cost

# Session 1083 (Rigby audit): 5 undefined names — _generate_smart_project_name
# (from core.views_image_helpers), _enhance_prompt_rule_based (from
# core.views_image_edit), and ImageHistory (the content model).
from core.views_image_helpers import _generate_smart_project_name  # noqa: E402
from core.views_image_edit import _enhance_prompt_rule_based  # noqa: E402
from content.models import ImageHistory  # noqa: E402

logger = logging.getLogger(__name__)


# ========================================
# SESSION 794: SYSTEM USER FOR AUTONOMOUS OPERATIONS
# ========================================

from django.views.decorators.csrf import csrf_exempt


def auto_create_project_from_session(session):
    """
    Automatically create a CreativeProject from an AI session

    Session 96 Weekend Project: Auto-organize content into projects

    Args:
        session: AISession object with meaningful content
    """
    from content.models import CreativeProject

    if not session:
        return None

    # Session 117: FIXED - Skip only if has a REAL project (not Quick Starts placeholder)
    # Quick Starts is okay to replace with auto-created project
    has_real_project = session.project and not session.project.is_quick_starts
    if has_real_project or session.auto_created_project:
        return None

    # Determine project name from session title with smart extraction
    project_name = _generate_smart_project_name(session.title)

    # Determine project category based on session type and content
    category = 'branding'  # Default
    if session.session_type:
        category_map = {
            'logo_design': 'branding',
            'video_creation': 'marketing',
            'content_package': 'marketing',
            'branding': 'branding',
        }
        category = category_map.get(session.session_type, 'branding')
    elif session.total_videos > 0:
        category = 'marketing'

    # Generate project goal from first prompt
    goal = session.first_prompt if session.first_prompt else f"Auto-created from AI session: {session.title}"
    if len(goal) > 200:
        goal = goal[:197] + '...'

    # Create project
    project = CreativeProject.objects.create(
        user=session.user,
        name=project_name,
        category=category,
        goal=goal,
        status='active',
        metadata={'auto_generated': True, 'source': 'ai_session'}  # Mark as auto-created
    )

    # Link session to project
    session.project = project
    session.auto_created_project = True
    session.save(update_fields=['project', 'auto_created_project'])

    # Session 97: Link all session content to the newly created project
    from content.models import ImageHistory, VideoHistory

    # Update all images from this session to belong to the project
    images_updated = ImageHistory.objects.filter(session=session).update(project=project)
    logger.info(f"📸 Linked {images_updated} images to project '{project.name}'")

    # Update all videos from this session to belong to the project
    videos_updated = VideoHistory.objects.filter(session=session).update(project=project)
    logger.info(f"🎬 Linked {videos_updated} videos to project '{project.name}'")

    # Note: Audio doesn't have project field yet, skip for now

    logger.info(f"✨ Auto-created project '{project.name}' (ID: {project.id}) for session {session.session_id}")
    return project


# ========================================
# IMAGE HISTORY HELPER (Session 36: Feature 9)
# ========================================


def build_prompt_from_form(workflow_type, form_data, project=None):
    """
    Build prompt string from form data based on workflow type
    Session 63: GOAL-DRIVEN prompt builder - Vision comes FIRST!
    """
    # Session 63: If user provided a custom prompt, use it directly
    custom_prompt = form_data.get('customPrompt', '').strip()
    if custom_prompt:
        return custom_prompt

    if workflow_type == 'logo-creator':
        parts = []

        # Session 64: CORE VISUAL SUBJECT FIRST! AI commits to the subject in first few tokens.
        # If we say "Disco Dinosaur logo" first, AI generates disco (human dancer).
        # If we say "T-Rex dinosaur in disco style" first, AI generates T-Rex!
        details = form_data.get('additionalDetails', '')
        if details:
            parts.append(details)

        # Session 64: Style terms come SECOND to reinforce the subject
        logo_style = form_data.get('logoStyle', 'character-mascot')
        style_map = {
            'character-mascot': 'cool cartoon character mascot standing upright, anthropomorphic, DreamWorks animation style, expressive, detailed illustration, cinematic lighting, 4K resolution, professional quality',
            'vector': 'professional vector art, flat design, clean lines, minimalist, iconic symbol, modern, simple shapes',
            'illustrative': 'hand-drawn illustration style, artistic, detailed linework, creative, sketch-like quality, unique character',
            'minimalist': 'minimalist design, simple and clean, negative space, modern, geometric, essential elements only',
            'badge': 'badge design, emblem style, traditional, detailed ornamental, crest, vintage feel, professional seal',
            'geometric': 'geometric shapes, abstract patterns, angular design, modern, mathematical precision, structured'
        }
        style_terms = style_map.get(logo_style, style_map['character-mascot'])
        parts.append(style_terms)

        # Business name comes AFTER subject is clear
        business_name = form_data.get('businessName', '')
        if business_name:
            parts.append(f"for {business_name}")

        colors = form_data.get('colors', '')
        if colors:
            parts.append(f'color scheme: {colors}')

        # Session 63: Vision/Goal adds context but comes AFTER core subject
        if project and project.goal:
            parts.append(f"Brand vision: {project.goal.strip()}")

        industry = form_data.get('industry', '')
        if industry:
            industry_map = {
                'tech': 'technology company',
                'coffee': 'coffee shop',
                'fitness': 'fitness gym',
                'food': 'restaurant',
                'finance': 'financial services',
                'health': 'healthcare',
                'education': 'education',
                'retail': 'retail store',
                'creative': 'creative agency',
                'construction': 'construction company'
            }
            parts.append(industry_map.get(industry, industry))

        # Additional project context comes last
        if project and project.description:
            parts.append(project.description.strip())

        parts.append('logo design')

        return ', '.join(parts)

    elif workflow_type == 'portrait-enhancer':
        subject = form_data.get('subject', '')
        style = form_data.get('style', '')
        lighting = form_data.get('lighting', '')
        background = form_data.get('background', '')

        parts = [subject, 'professional portrait']

        if style:
            parts.append(style)

        if lighting:
            parts.append(f'{lighting}')

        if background:
            parts.append(f'{background} background')

        parts.extend(['high quality', '4K', 'sharp focus', 'professional photography'])

        return ', '.join(parts)

    elif workflow_type == 'social-media-pack':
        content = form_data.get('content', '')
        platform = form_data.get('platform', '')
        colors = form_data.get('colors', '')
        mood = form_data.get('mood', '')

        parts = [content]

        if mood:
            parts.append(mood)

        if colors:
            parts.append(f'colors: {colors}')

        if platform:
            parts.append(f'optimized for {platform}')

        parts.extend(['high quality', 'professional', 'eye-catching'])

        return ', '.join(parts)

    elif workflow_type == 'product-mockup':
        description = form_data.get('description', '')
        colors = form_data.get('colors', '')
        context = form_data.get('context', '')
        style = form_data.get('style', '')

        parts = [description]

        if colors:
            parts.append(colors)

        if context:
            context_map = {
                'studio': 'studio white background',
                'lifestyle': 'lifestyle in-use setting',
                'desk': 'on modern desk workspace',
                'outdoor': 'outdoor natural environment',
                'premium': 'luxury premium setting'
            }
            parts.append(context_map.get(context, context))

        if style:
            parts.append(style)

        parts.extend(['product photography', 'high quality', 'professional'])

        return ', '.join(parts)

    elif workflow_type == 'style-explorer':
        subject = form_data.get('subject', '')
        description = form_data.get('description', '')

        parts = [subject]

        if description:
            parts.append(description)

        return ', '.join(parts)

    return None


def calculate_project_stats(project_id, user):
    """
    Calculate comprehensive project statistics
    Session 146: Project Stats Header

    Args:
        project_id: UUID of the project
        user: User object for filtering

    Returns:
        Dict containing content counts, collaboration metrics, and timeline
    """
    from content.models import ImageHistory, VideoHistory, MiniFigAsset
    from core.models.agents_registry import AgentContribution
    from coleadership.models import CoLeadershipDecision
    from django.db.models import Sum, Max

    # Content counts
    images_count = ImageHistory.objects.filter(project_id=project_id, user=user).count()
    videos_count = VideoHistory.objects.filter(project_id=project_id, user=user).count()
    models_count = MiniFigAsset.objects.filter(project_id=project_id, user=user).count()

    # Agent stats (Session 147: Return list of agent names for dropdown)
    # Session 148 Fix: Get agent names, not UUIDs, for JSON serialization
    agent_contributions = AgentContribution.objects.filter(
        project_id=project_id
    ).select_related('agent').values('agent__name').distinct()

    # Create unique list by converting to set and back to list
    unique_agents_list = sorted(list(set([a['agent__name'] for a in agent_contributions if a['agent__name']])))
    unique_agents_count = len(unique_agents_list)

    total_execution_time = AgentContribution.objects.filter(
        project_id=project_id
    ).aggregate(total=Sum('execution_time_seconds'))['total'] or 0

    # Decision count (from Decision Timeline / Co-Leadership)
    decisions_count = CoLeadershipDecision.objects.filter(project_id=project_id).count()

    # Session 183: Workflow count (from WorkflowHistory)
    from content.models import WorkflowHistory
    workflows_count = WorkflowHistory.objects.filter(project_id=project_id, user=user).count()

    # Get project created_at
    from content.models import CreativeProject
    try:
        project = CreativeProject.objects.get(id=project_id, user=user)
        created_at = project.created_at
    except CreativeProject.DoesNotExist:
        created_at = None

    # Last active (most recent content creation)
    last_active_candidates = []

    image_latest = ImageHistory.objects.filter(
        project_id=project_id, user=user
    ).aggregate(latest=Max('created_at'))['latest']
    if image_latest:
        last_active_candidates.append(image_latest)

    video_latest = VideoHistory.objects.filter(
        project_id=project_id, user=user
    ).aggregate(latest=Max('created_at'))['latest']
    if video_latest:
        last_active_candidates.append(video_latest)

    model_latest = MiniFigAsset.objects.filter(
        project_id=project_id, user=user
    ).aggregate(latest=Max('created_at'))['latest']
    if model_latest:
        last_active_candidates.append(model_latest)

    last_active = max(last_active_candidates) if last_active_candidates else created_at

    return {
        'content': {
            'images': images_count,
            'videos': videos_count,
            'models': models_count,
            'total': images_count + videos_count + models_count
        },
        'collaboration': {
            'unique_agents': unique_agents_list,  # Session 147: List of agent names
            'unique_agents_count': unique_agents_count,  # Session 147: Count for stats display
            'decisions_count': decisions_count,
            'workflows_count': workflows_count,  # Session 183: Workflows completed
            'execution_time_seconds': int(total_execution_time)
        },
        'timeline': {
            'created_at': created_at.isoformat() if created_at else None,
            'last_active': last_active.isoformat() if last_active else None
        }
    }


def control_sketch(request):
    """
    Convert a sketch into a refined image using Stability AI Control Sketch.

    Expected request: Form data with:
    - 'image': sketch image file (can be hand-drawn or canvas generated)
    - 'prompt': text description of desired result
    - 'control_strength': float 0-1 (how much to follow sketch, default 0.7)
    - 'negative_prompt': optional negative prompt

    Returns: {success: true, image_url: 'url_to_generated_image'}
    """
    try:
        # Validate inputs
        if 'image' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No sketch image provided'
            }, status=400)

        sketch_file = request.FILES['image']
        prompt = request.POST.get('prompt', '').strip()
        control_strength = float(request.POST.get('control_strength', 0.7))
        negative_prompt = request.POST.get('negative_prompt', '').strip()

        if not prompt:
            return JsonResponse({
                'success': False,
                'error': 'Prompt is required'
            }, status=400)

        # Get API key
        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')

        if not stability_key:
            return JsonResponse({
                'success': False,
                'error': 'Stability AI API key not configured'
            }, status=500)

        logger.info(f"🎨 Control Sketch request: {prompt} (strength: {control_strength})")

        # Call Stability AI control/sketch endpoint
        url = "https://api.stability.ai/v2beta/stable-image/control/sketch"

        files = {
            'image': (sketch_file.name, sketch_file.read(), sketch_file.content_type or 'image/png')
        }

        data = {
            'prompt': prompt,
            'control_strength': control_strength,
            'output_format': 'png'
        }

        if negative_prompt:
            data['negative_prompt'] = negative_prompt

        headers = {
            'Authorization': f'Bearer {stability_key}',
            'Accept': 'image/*'
        }

        response = requests.post(url, headers=headers, files=files, data=data)

        if response.status_code == 200:
            # Save the generated image
            filename = f'sketch_control_{uuid.uuid4().hex[:8]}.png'
            filepath = os.path.join('generated_images', filename)

            saved_path = default_storage.save(filepath, ContentFile(response.content))
            image_url = default_storage.url(saved_path)

            logger.info(f"✅ Sketch control complete - saved to {saved_path}")

            # Save to history
            save_to_history(
                user=request.user,
                file_path=saved_path,
                image_type='sketch_control',
                prompt=prompt,
                parameters={
                    'operation': 'control_sketch',
                    'control_strength': control_strength,
                    'negative_prompt': negative_prompt
                }
            )

            return JsonResponse({
                'success': True,
                'image_url': image_url
            })
        else:
            error_msg = response.text
            logger.error(f"❌ Stability AI error: {error_msg}")
            return JsonResponse({
                'success': False,
                'error': f'Stability AI error: {error_msg}'
            }, status=500)

    except Exception as e:
        logger.error(f"❌ Control sketch error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def control_structure(request):
    """
    Transform an image while maintaining its structure using Stability AI Control Structure.

    Expected request: Form data with:
    - 'image': reference image file (structure will be preserved)
    - 'prompt': text description of desired style/transformation
    - 'control_strength': float 0-1 (how much to follow structure, default 0.7)
    - 'negative_prompt': optional negative prompt

    Returns: {success: true, image_url: 'url_to_generated_image'}
    """
    try:
        # Validate inputs
        if 'image' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No reference image provided'
            }, status=400)

        ref_image = request.FILES['image']
        prompt = request.POST.get('prompt', '').strip()
        control_strength = float(request.POST.get('control_strength', 0.7))
        negative_prompt = request.POST.get('negative_prompt', '').strip()

        if not prompt:
            return JsonResponse({
                'success': False,
                'error': 'Prompt is required'
            }, status=400)

        # Get API key
        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')

        if not stability_key:
            return JsonResponse({
                'success': False,
                'error': 'Stability AI API key not configured'
            }, status=500)

        logger.info(f"🏗️ Control Structure request: {prompt} (strength: {control_strength})")

        # Call Stability AI control/structure endpoint
        url = "https://api.stability.ai/v2beta/stable-image/control/structure"

        files = {
            'image': (ref_image.name, ref_image.read(), ref_image.content_type or 'image/png')
        }

        data = {
            'prompt': prompt,
            'control_strength': control_strength,
            'output_format': 'png'
        }

        if negative_prompt:
            data['negative_prompt'] = negative_prompt

        headers = {
            'Authorization': f'Bearer {stability_key}',
            'Accept': 'image/*'
        }

        response = requests.post(url, headers=headers, files=files, data=data)

        if response.status_code == 200:
            # Save the generated image
            filename = f'structure_control_{uuid.uuid4().hex[:8]}.png'
            filepath = os.path.join('generated_images', filename)

            saved_path = default_storage.save(filepath, ContentFile(response.content))
            image_url = default_storage.url(saved_path)

            logger.info(f"✅ Structure control complete - saved to {saved_path}")

            # Save to history
            save_to_history(
                user=request.user,
                file_path=saved_path,
                image_type='structure_control',
                prompt=prompt,
                parameters={
                    'operation': 'control_structure',
                    'control_strength': control_strength,
                    'negative_prompt': negative_prompt
                }
            )

            return JsonResponse({
                'success': True,
                'image_url': image_url
            })
        else:
            error_msg = response.text
            logger.error(f"❌ Stability AI error: {error_msg}")
            return JsonResponse({
                'success': False,
                'error': f'Stability AI error: {error_msg}'
            }, status=500)

    except Exception as e:
        logger.error(f"❌ Control structure error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def control_unified(request):
    """
    Session 199: Unified control endpoint for all Stability AI control types.
    Supports: sketch, structure, style

    Expected request: Form data with:
    - 'image': control image file
    - 'prompt': text description of desired result
    - 'control_type': 'sketch' | 'structure' | 'style'
    - 'control_strength': float 0-1 (default 0.7)
    - 'project_id': optional project ID for association
    - 'source_image_id': optional source image ID

    Returns: {success: true, image_url: '...', image_id: '...', sequential_number: N}
    """
    try:
        if 'image' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No control image provided'
            }, status=400)

        image_file = request.FILES['image']
        prompt = request.POST.get('prompt', '').strip()
        control_type = request.POST.get('control_type', 'structure').strip().lower()
        control_strength = float(request.POST.get('control_strength', 0.7))
        project_id = request.POST.get('project_id')
        source_image_id = request.POST.get('source_image_id')

        if not prompt:
            return JsonResponse({
                'success': False,
                'error': 'Prompt is required'
            }, status=400)

        # Validate control type
        valid_types = ['sketch', 'structure', 'style']
        if control_type not in valid_types:
            return JsonResponse({
                'success': False,
                'error': f'Invalid control type: {control_type}. Must be one of: {", ".join(valid_types)}'
            }, status=400)

        # Get API key
        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')

        if not stability_key:
            return JsonResponse({
                'success': False,
                'error': 'Stability AI API key not configured'
            }, status=500)

        logger.info(f"🎛️ Control {control_type} request - prompt: {prompt}, strength: {control_strength}, project: {project_id}")

        # Select the appropriate API endpoint
        url = f"https://api.stability.ai/v2beta/stable-image/control/{control_type}"

        files = {
            'image': (image_file.name, image_file.read(), image_file.content_type or 'image/png')
        }

        data = {
            'prompt': prompt,
            'control_strength': control_strength,
            'output_format': 'png'
        }

        headers = {
            'Authorization': f'Bearer {stability_key}',
            'Accept': 'image/*'
        }

        logger.info(f"📤 Calling Stability AI {control_type} control endpoint...")
        response = requests.post(url, headers=headers, files=files, data=data, timeout=60)
        logger.info(f"📥 Response status: {response.status_code}, size: {len(response.content)} bytes")

        if response.status_code == 200:
            # Save with proper user folder structure
            filename = f'{control_type}_control_{uuid.uuid4().hex[:8]}.png'
            filepath = os.path.join('generated_images', request.user.username, filename)
            saved_path = default_storage.save(filepath, ContentFile(response.content))
            image_url = default_storage.url(saved_path)

            logger.info(f"✅ Control {control_type} complete - saved to {saved_path}")

            # Get project and source image for proper association
            from content.models import ImageHistory, CreativeProject
            project = None
            source_image = None

            if project_id:
                try:
                    project = CreativeProject.objects.get(id=project_id, user=request.user)
                except CreativeProject.DoesNotExist:
                    pass

            if source_image_id:
                try:
                    source_image = ImageHistory.objects.get(id=source_image_id, user=request.user)
                    if not project and source_image.project:
                        project = source_image.project
                except ImageHistory.DoesNotExist:
                    pass

            # Create ImageHistory record with project association
            from core.services.workspace_resolver import get_active_workspace
            new_image = ImageHistory.objects.create(
                user=request.user,
                prompt=f"Control {control_type}: {prompt} (from #{source_image.get_sequential_number() if source_image else 'unknown'})",
                file_path=saved_path,
                filename=filename,
                model_used=f'stability-control-{control_type}',
                image_type=f'{control_type}_control',
                project=project,
                session=source_image.session if source_image else None,
                workspace=get_active_workspace(request.user),
            )

            logger.info(f"✅ Created ImageHistory: {new_image.id}, project: {project.id if project else 'none'}")

            return JsonResponse({
                'success': True,
                'image_url': image_url,
                'image_id': str(new_image.id),
                'sequential_number': new_image.get_sequential_number()
            })
        else:
            error_msg = response.text
            logger.error(f"❌ Stability AI {control_type} control error: {error_msg}")
            return JsonResponse({
                'success': False,
                'error': f'Stability AI error: {error_msg}'
            }, status=500)

    except Exception as e:
        logger.error(f"❌ Control unified error: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ========================================
# WORKFLOW EXECUTION (Session 41: Real API Integration)
# ========================================


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_project(request):
    """
    Create a new creative project
    Session 60: Phase C.1.2 - Project Management API

    POST /api/projects/
    Body:
        {
            "name": "Brand Launch Campaign",
            "description": "Complete brand identity for new startup",
            "goal": "Create professional brand assets",
            "deadline": "2025-12-31T23:59:59Z" (optional),
            "category": "Branding" (optional),
            "tags": ["logo", "branding", "social"] (optional)
        }

    Returns:
        {
            "success": true,
            "project": { ... project data ... }
        }
    """
    try:
        # Session 324: Use unified PartnershipProject model
        from core.models_partnership import PartnershipProject
        from django.utils.dateparse import parse_datetime

        # Validate required fields
        name = request.data.get('name', '').strip()
        description = request.data.get('description', '').strip()
        goal = request.data.get('goal', '').strip()

        if not name:
            return Response({
                'error': 'Project name is required'
            }, status=400)

        # Goal is optional for unified model (backward compatible)
        # if not goal:
        #     return Response({
        #         'error': 'Project goal is required'
        #     }, status=400)

        # Optional fields
        deadline_str = request.data.get('deadline')
        deadline = None
        if deadline_str:
            deadline = parse_datetime(deadline_str)

        category = request.data.get('category', '')
        colors = request.data.get('colors', '')  # Session 63: Professional agency intake field
        tags = request.data.get('tags', [])
        project_type = request.data.get('project_type', 'content_creation')

        # Session 324: Create project using unified PartnershipProject model
        project = PartnershipProject.objects.create(
            user=request.user,
            project_name=name,  # PartnershipProject uses project_name
            description=description,
            goal=goal,
            deadline=deadline,
            category=category,
            colors=colors,
            tags=tags,
            project_type=project_type,
            status='planning'
        )

        logger.info(f"✅ Created project '{name}' for user {request.user.username}")

        return Response({
            'success': True,
            'project': {
                'id': str(project.id),
                'name': project.name,
                'description': project.description,
                'goal': project.goal,
                'status': project.status,
                'category': project.category,
                'colors': project.colors,  # Session 63: Professional agency intake field
                'tags': project.tags,
                'deadline': project.deadline.isoformat() if project.deadline else None,
                'total_workflows': project.total_workflows,
                'completed_workflows': project.completed_workflows,
                'progress_percentage': project.progress_percentage,
                'created_at': project.created_at.isoformat()
            }
        }, status=201)

    except Exception as e:
        logger.error(f"❌ Error creating project: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@rate_limit('image_processing')  # Phase 2 P1: Rate limit image operations (20 requests/min)
def create_variations_view(request):
    """
    Create variations of an existing image using structure control.
    Accepts JSON: {image_id: uuid, count: int (default 3), prompt: str (optional), project_id: uuid (optional)}
    Note: @login_required removed to support internal RequestFactory calls from agents
    """
    try:
        # Manual authentication check for web requests
        if not request.user or not request.user.is_authenticated:
            logger.warning(f"⚠️ Unauthenticated request to create_variations_view")

        logger.info(f"🎨 create_variations_view called - user: {request.user}, authenticated: {request.user.is_authenticated}")

        data = json.loads(request.body)
        image_id = data.get('image_id')
        count = data.get('count', 3)
        variation_prompt = data.get('prompt', 'creative variation')
        project_id = data.get('project_id')

        logger.info(f"🎨 Params: image_id={image_id}, count={count}, prompt={variation_prompt}")

        if not image_id:
            return JsonResponse({'success': False, 'error': 'image_id required'}, status=400)

        # Get the image from history
        from content.models import ImageHistory, CreativeProject
        try:
            image = ImageHistory.objects.get(id=image_id, user=request.user)
            logger.info(f"✅ Found image: {image.id}")
        except ImageHistory.DoesNotExist:
            logger.error(f"❌ Image not found: {image_id} for user {request.user}")
            return JsonResponse({'success': False, 'error': 'Image not found'}, status=404)

        seq_num = image.get_sequential_number()
        logger.info(f"🎨 Creating {count} variations of image {image_id} (sequential #{seq_num})")

        # Get image data (handle both data URIs and file paths)
        if image.file_path.startswith('data:'):
            image_data = base64.b64decode(image.file_path.split(',')[1])
        else:
            file_full_path = os.path.join(settings.MEDIA_ROOT, image.file_path)
            with open(file_full_path, 'rb') as f:
                image_data = f.read()

        # Get API key
        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
        if not stability_key:
            return JsonResponse({'success': False, 'error': 'Stability AI API key not configured'}, status=500)

        # Get project if provided
        project = None
        if project_id:
            try:
                project = CreativeProject.objects.get(id=project_id, user=request.user)
            except CreativeProject.DoesNotExist:
                pass

        # Create variations using structure control
        url = "https://api.stability.ai/v2beta/stable-image/control/structure"
        created_images = []

        for i in range(count):
            # Vary the control strength slightly for each variation
            control_strength = 0.6 + (i * 0.05)  # 0.6, 0.65, 0.7, etc.

            files = {'image': image_data}
            data_params = {
                'prompt': variation_prompt,
                'control_strength': min(control_strength, 0.9),
                'output_format': 'png'
            }

            headers = {
                "Authorization": f"Bearer {stability_key}",
                "Accept": "image/*"
            }

            api_response = requests.post(url, headers=headers, files=files, data=data_params, timeout=60)

            if api_response.status_code == 200:
                # Save the variation to disk (not as data URI!)
                result_image_data = api_response.content

                # Create unique filename and save to disk
                filename = f'variation_{i+1}_{uuid.uuid4().hex[:8]}.png'
                filepath = os.path.join('generated_images', request.user.username, filename)
                saved_path = default_storage.save(filepath, ContentFile(result_image_data))
                image_url = default_storage.url(saved_path)

                from core.services.workspace_resolver import get_active_workspace
                new_image = ImageHistory.objects.create(
                    user=request.user,
                    prompt=f"Variation {i+1} of image #{seq_num}",
                    file_path=saved_path,  # Save FILE PATH, not data URI!
                    filename=filename,
                    model_used="stability-structure-control",
                    project=project,
                    workspace=get_active_workspace(request.user),
                )

                # Session 142: Track agent contribution
                try:
                    from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
                    agent = UnifiedAgentTemplate.objects.get(name='image-generation-agent')
                    AgentContribution.objects.create(
                        agent=agent,
                        image=new_image,
                        project=project,
                        contribution_type='generation',
                        task_description="Generated image using image-generation-agent",
                        execution_time_seconds=0.0
                    )
                    logger.info(f"✅ Agent contribution tracked for image {{ new_image.id }}")
                except Exception as e:
                    logger.error(f"❌ Failed to create agent contribution: {e}")
                    logger.error(f"❌ Failed to create agent contribution: {e}")

                created_images.append({
                    'image_id': str(new_image.id),
                    'image_url': image_url,  # Return actual URL, not data URI
                    'sequential_number': new_image.get_sequential_number()
                })
                logger.info(f"✅ Created variation {i+1}/{count}: {new_image.id} → {saved_path}")
            else:
                error_detail = api_response.text
                logger.error(f"❌ Variation {i+1} failed (status {api_response.status_code}): {error_detail}")

        if not created_images:
            # Return detailed error message with first failure reason
            error_msg = 'Failed to create any variations - check server logs for API error details'
            return JsonResponse({'success': False, 'error': error_msg}, status=500)

        return JsonResponse({
            'success': True,
            'count': len(created_images),
            'images': created_images
        })

    except Exception as e:
        logger.error(f"❌ Create variations error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_image(request, image_id):
    """
    Delete an image from history.

    Also deletes the actual file from storage.

    Session 489: Now tracks implicit learning signals (negative signal).
    """
    try:
        from content.models import ImageHistory

        image = ImageHistory.objects.get(id=image_id, user=request.user)

        # Session 489: Track implicit learning signal BEFORE deleting
        # (need the image data for style/model info)
        try:
            from core.services.implicit_learning import get_learning_service
            learning = get_learning_service()
            learning.track_delete(
                user_id=request.user.id,
                content_id=str(image_id),
                style=image.style or None,
                model=image.model_used or None
            )
        except Exception as learn_error:
            logger.debug(f"Implicit learning tracking failed (non-fatal): {learn_error}")

        # Delete file from storage
        try:
            if default_storage.exists(image.file_path):
                default_storage.delete(image.file_path)
            if image.thumbnail and default_storage.exists(image.thumbnail):
                default_storage.delete(image.thumbnail)
        except Exception as e:
            logger.warning(f"⚠️ Could not delete files for image {image_id}: {e}")

        # Delete database record
        image.delete()

        logger.info(f"🗑️ Deleted image {image_id} for {request.user.username}")

        return Response({
            'success': True,
            'message': 'Image deleted successfully'
        })

    except ImageHistory.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Image not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Delete image error: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


# ========================================
# BATCH DOWNLOAD (Session 37: Feature 10)
# ========================================


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_project(request, project_id):
    """
    Delete a project
    Session 60: Phase C.1.2 - Project Management API

    DELETE /api/projects/<uuid:project_id>/

    Returns:
        {
            "success": true,
            "message": "Project deleted successfully"
        }
    """
    try:
        from content.models import CreativeProject

        # Session 60: Using UUID for project lookup
        project = CreativeProject.objects.get(id=project_id, user=request.user)

        project_name = project.name
        project.delete()

        logger.info(f"✅ Deleted project '{project_name}' for user {request.user.username}")

        return Response({
            'success': True,
            'message': f"Project '{project_name}' deleted successfully"
        })

    except CreativeProject.DoesNotExist:
        return Response({
            'error': 'Project not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error deleting project: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_session(request, session_id):
    """
    Delete an AI session and optionally its associated content
    Session 97: Delete session functionality

    Query parameters:
    - delete_content: 'true' to also delete images/videos/audio from this session
    """
    try:
        from content.models import AISession, ImageHistory, VideoHistory

        # Get the session
        try:
            session = AISession.objects.get(session_id=session_id, user=request.user)
        except AISession.DoesNotExist:
            return Response({
                'error': 'Session not found'
            }, status=404)

        # Check if user wants to delete content too
        delete_content = request.query_params.get('delete_content', 'false').lower() == 'true'

        session_title = session.title or 'Untitled Session'
        content_counts = {
            'images': session.total_images,
            'videos': session.total_videos,
            'audio': session.total_audio
        }

        if delete_content:
            # Delete all content from this session
            images_deleted = ImageHistory.objects.filter(session=session).delete()[0]
            videos_deleted = VideoHistory.objects.filter(session=session).delete()[0]
            # Audio would go here when implemented

            logger.info(f"🗑️ Deleted session '{session_title}' and its content: {images_deleted} images, {videos_deleted} videos")
        else:
            # Just unlink content from session (keep content, remove session reference)
            ImageHistory.objects.filter(session=session).update(session=None)
            VideoHistory.objects.filter(session=session).update(session=None)

            logger.info(f"🗑️ Deleted session '{session_title}', content preserved")

        # Delete the session itself
        session.delete()

        return Response({
            'success': True,
            'message': f"Session '{session_title}' deleted successfully",
            'content_deleted': delete_content,
            'content_counts': content_counts
        })

    except Exception as e:
        logger.error(f"❌ Delete session error: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@csrf_exempt
@api_view(['POST'])
def erase_object(request):
    """
    Erase objects from image using Stability AI erase endpoint.
    Requires: image file, mask (drawn areas to erase)
    Optional: project_id, source_image_id for proper association
    Session 198: Updated to support project association and proper image history
    """
    try:
        if 'image' not in request.FILES or 'mask' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'Missing image or mask file'
            }, status=400)

        image_file = request.FILES['image']
        mask_file = request.FILES['mask']
        project_id = request.POST.get('project_id')
        source_image_id = request.POST.get('source_image_id')

        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')

        if not stability_key:
            return JsonResponse({
                'success': False,
                'error': 'Stability AI API key not configured'
            }, status=500)

        logger.info(f"🖌️ Erase request - project: {project_id}, source_image: {source_image_id}")

        url = "https://api.stability.ai/v2beta/stable-image/edit/erase"

        files = {
            'image': (image_file.name, image_file.read(), image_file.content_type),
            'mask': (mask_file.name, mask_file.read(), mask_file.content_type)
        }

        data = {'output_format': 'png'}

        headers = {
            'Authorization': f'Bearer {stability_key}',
            'Accept': 'image/*'
        }

        logger.info(f"📤 Calling Stability AI erase endpoint...")
        response = requests.post(url, headers=headers, files=files, data=data, timeout=60)
        logger.info(f"📥 Response status: {response.status_code}, size: {len(response.content)} bytes")

        if response.status_code == 200:
            # Session 198: Save with proper user folder structure
            filename = f'erased_{uuid.uuid4().hex[:8]}.png'
            filepath = os.path.join('generated_images', request.user.username, filename)
            saved_path = default_storage.save(filepath, ContentFile(response.content))
            image_url = default_storage.url(saved_path)

            logger.info(f"✅ Erase complete - saved to {saved_path}")

            # Session 198: Get project and source image for proper association
            from content.models import ImageHistory, CreativeProject
            project = None
            source_image = None

            if project_id:
                try:
                    project = CreativeProject.objects.get(id=project_id, user=request.user)
                except CreativeProject.DoesNotExist:
                    pass

            if source_image_id:
                try:
                    source_image = ImageHistory.objects.get(id=source_image_id, user=request.user)
                    # Inherit project from source if not specified
                    if not project and source_image.project:
                        project = source_image.project
                except ImageHistory.DoesNotExist:
                    pass

            # Create ImageHistory record with project association
            from core.services.workspace_resolver import get_active_workspace
            new_image = ImageHistory.objects.create(
                user=request.user,
                prompt=f"Erased from image #{source_image.get_sequential_number() if source_image else 'unknown'}",
                file_path=saved_path,
                filename=filename,
                model_used='stability-erase',
                image_type='erased',
                project=project,
                session=source_image.session if source_image else None,
                workspace=get_active_workspace(request.user),
            )

            logger.info(f"✅ Created ImageHistory: {new_image.id}, project: {project.id if project else 'none'}")

            return JsonResponse({
                'success': True,
                'image_url': image_url,
                'image_id': str(new_image.id),
                'sequential_number': new_image.get_sequential_number()
            })
        else:
            error_msg = response.text
            logger.error(f"❌ Stability AI erase error: {error_msg}")
            return JsonResponse({
                'success': False,
                'error': f'Stability AI error: {error_msg}'
            }, status=500)

    except Exception as e:
        logger.error(f"❌ Erase error: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_project_csv(request, project_id):
    """
    Export project statistics as CSV
    Session 148: Project Export

    GET /api/projects/<uuid:project_id>/export/csv/

    Returns: CSV file with stats and agent contributions
    """
    import io
    import csv
    from django.http import HttpResponse
    from content.models import CreativeProject, ImageHistory, VideoHistory, MiniFigAsset
    from core.models.agents_registry import AgentContribution
    from collections import defaultdict

    try:
        project = CreativeProject.objects.get(id=project_id, user=request.user)

        # Create CSV buffer
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)

        # Header
        writer.writerow(['Project Export - AI Content Studio'])
        writer.writerow([])
        writer.writerow(['Project Information'])
        writer.writerow(['Name', project.name])
        writer.writerow(['Description', project.description or ''])
        writer.writerow(['Created', project.created_at.strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow([])

        # Content summary
        writer.writerow(['Content Summary'])
        writer.writerow(['Content Type', 'Count'])
        images_count = ImageHistory.objects.filter(project_id=project_id, user=request.user).count()
        videos_count = VideoHistory.objects.filter(project_id=project_id, user=request.user).count()
        models_count = MiniFigAsset.objects.filter(project_id=project_id, user=request.user).count()
        writer.writerow(['Images', images_count])
        writer.writerow(['Videos', videos_count])
        writer.writerow(['3D Models', models_count])
        writer.writerow(['Total', images_count + videos_count + models_count])
        writer.writerow([])

        # Agent contributions
        writer.writerow(['Agent Contributions'])
        writer.writerow(['Agent', 'Images', 'Videos', '3D Models', 'Total', 'Execution Time (s)'])
        contributions = AgentContribution.objects.filter(project_id=project_id)

        # Group by agent
        agent_stats = defaultdict(lambda: {'images': 0, 'videos': 0, 'models': 0, 'time': 0})

        for contrib in contributions:
            agent = contrib.agent.name if contrib.agent else 'Unknown'
            if contrib.image_id:
                agent_stats[agent]['images'] += 1
            if contrib.video_id:
                agent_stats[agent]['videos'] += 1
            if contrib.minifig_asset_id:
                agent_stats[agent]['models'] += 1
            agent_stats[agent]['time'] += contrib.execution_time_seconds or 0

        for agent, stats in sorted(agent_stats.items()):
            total_contributions = stats['images'] + stats['videos'] + stats['models']
            writer.writerow([
                agent,
                stats['images'],
                stats['videos'],
                stats['models'],
                total_contributions,
                round(stats['time'], 2)
            ])

        writer.writerow([])
        writer.writerow(['Export Date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])

        # Prepare response
        csv_buffer.seek(0)
        response = HttpResponse(csv_buffer.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{project.name.replace(" ", "_")}_stats.csv"'

        logger.info(f"✅ Project exported as CSV: {project.name}")
        return response

    except CreativeProject.DoesNotExist:
        logger.error(f"❌ Project not found: {project_id}")
        return HttpResponse('Project not found', status=404)
    except Exception as e:
        logger.error(f"❌ Export CSV error: {str(e)}")
        import traceback
        traceback.print_exc()
        return HttpResponse(f'Export failed: {str(e)}', status=500)


# ========================================
# SESSION 151: ADVANCED IMAGE EDITING SUITE
# ========================================
# Note: search_and_replace_view already exists at line 11735
# Adding creative_upscale_view as new capability


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_project_pdf(request, project_id):
    """
    Export project as professional PDF portfolio
    Session 148: Project Export

    GET /api/projects/<uuid:project_id>/export/pdf/

    Returns: Binary PDF file with images, stats, and timeline
    """
    import io
    from datetime import datetime
    from django.http import HttpResponse
    from content.models import CreativeProject, ImageHistory, VideoHistory, MiniFigAsset
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, PageBreak, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors

    try:
        project = CreativeProject.objects.get(id=project_id, user=request.user)
        stats = calculate_project_stats(project_id, request.user)

        # Create PDF buffer
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, spaceAfter=30)
        heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=16, spaceAfter=12)

        # Build PDF content
        story = []

        # Title page
        story.append(Paragraph(project.name, title_style))
        if project.description:
            story.append(Paragraph(project.description, styles['Normal']))
        story.append(Spacer(1, 0.5*inch))

        # Stats section
        story.append(Paragraph('Project Statistics', heading_style))

        stats_data = [
            ['Metric', 'Value'],
            ['Images', str(stats['content']['images'])],
            ['Videos', str(stats['content']['videos'])],
            ['3D Models', str(stats['content']['models'])],
            ['Total Assets', str(stats['content']['total'])],
            ['Unique Agents', str(stats['collaboration']['unique_agents_count'])],
            ['Execution Time', f"{stats['collaboration']['execution_time_seconds']} seconds"],
            ['Decisions Made', str(stats['collaboration']['decisions_count'])],
        ]

        stats_table = Table(stats_data, colWidths=[3*inch, 3*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(stats_table)
        story.append(Spacer(1, 0.3*inch))

        # Agent list
        if stats['collaboration']['unique_agents']:
            story.append(Paragraph('Contributing Agents', heading_style))
            agents_text = ', '.join(stats['collaboration']['unique_agents'])
            story.append(Paragraph(agents_text, styles['Normal']))
            story.append(Spacer(1, 0.3*inch))

        story.append(PageBreak())

        # Images section
        images = ImageHistory.objects.filter(project_id=project_id, user=request.user)
        if images:
            story.append(Paragraph('Image Gallery', heading_style))
            for img in images:
                if img.file_path and not img.file_path.startswith('data:') and os.path.exists(img.file_path):
                    try:
                        # Add image
                        rl_img = RLImage(img.file_path, width=4*inch, height=4*inch, kind='proportional')
                        story.append(rl_img)

                        # Add caption
                        caption = f"<b>Image #{img.get_sequential_number()}</b>: {img.prompt or 'No prompt'}"
                        story.append(Paragraph(caption, styles['Normal']))
                        story.append(Spacer(1, 0.3*inch))
                    except Exception as e:
                        logger.warning(f"Couldn't add image to PDF: {e}")

        # Videos section
        videos = VideoHistory.objects.filter(project_id=project_id, user=request.user)
        if videos:
            story.append(PageBreak())
            story.append(Paragraph('Video Gallery', heading_style))
            for vid in videos:
                video_info = f"""
                <b>Video #{vid.get_sequential_number()}</b><br/>
                Prompt: {vid.prompt or 'No prompt'}<br/>
                Status: {vid.status}
                """
                story.append(Paragraph(video_info, styles['Normal']))
                story.append(Spacer(1, 0.2*inch))

        # 3D Models section
        models = MiniFigAsset.objects.filter(project_id=project_id, user=request.user)
        if models:
            story.append(PageBreak())
            story.append(Paragraph('3D Models', heading_style))
            for model in models:
                model_info = f"""
                <b>Model #{model.get_sequential_number() if hasattr(model, 'get_sequential_number') else 'N/A'}</b><br/>
                Status: {model.status}
                """
                story.append(Paragraph(model_info, styles['Normal']))
                story.append(Spacer(1, 0.2*inch))

        # Footer
        story.append(PageBreak())
        story.append(Paragraph('Generated by AI Content Studio', styles['Normal']))
        story.append(Paragraph(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))

        # Build PDF
        doc.build(story)

        # Prepare response
        pdf_buffer.seek(0)
        response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{project.name.replace(" ", "_")}_portfolio.pdf"'

        logger.info(f"✅ Project exported as PDF: {project.name}")
        return response

    except CreativeProject.DoesNotExist:
        logger.error(f"❌ Project not found: {project_id}")
        return HttpResponse('Project not found', status=404)
    except Exception as e:
        logger.error(f"❌ Export PDF error: {str(e)}")
        import traceback
        traceback.print_exc()
        return HttpResponse(f'Export failed: {str(e)}', status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_project_zip(request, project_id):
    """
    Export complete project as ZIP archive
    Session 148: Project Export

    GET /api/projects/<uuid:project_id>/export/zip/

    Returns: Binary ZIP file with all assets + metadata.json + README.txt
    """
    import io
    import json
    from zipfile import ZipFile
    from pathlib import Path
    from datetime import datetime
    from django.http import HttpResponse
    from content.models import CreativeProject, ImageHistory, VideoHistory, MiniFigAsset

    try:
        # Get project
        project = CreativeProject.objects.get(id=project_id, user=request.user)

        # Get all content
        images = ImageHistory.objects.filter(project_id=project_id, user=request.user)
        videos = VideoHistory.objects.filter(project_id=project_id, user=request.user)
        models = MiniFigAsset.objects.filter(project_id=project_id, user=request.user)

        # Get stats
        stats = calculate_project_stats(project_id, request.user)

        # Create in-memory ZIP
        zip_buffer = io.BytesIO()

        with ZipFile(zip_buffer, 'w') as zip_file:
            # Add metadata.json
            metadata = {
                'project': {
                    'id': str(project.id),
                    'name': project.name,
                    'description': project.description or '',
                    'created_at': project.created_at.isoformat(),
                },
                'stats': stats,
                'exported_at': datetime.now().isoformat(),
                'exported_by': request.user.email
            }
            zip_file.writestr('metadata.json', json.dumps(metadata, indent=2))

            # Add README
            readme = f"""# {project.name}

{project.description or 'No description provided'}

## Contents
- Images: {len(images)}
- Videos: {len(videos)}
- 3D Models: {len(models)}

## Statistics
- Total Assets: {stats['content']['total']}
- Unique Agents: {stats['collaboration']['unique_agents_count']}
- Total Execution Time: {stats['collaboration']['execution_time_seconds']} seconds
- Decisions Made: {stats['collaboration']['decisions_count']}

## Timeline
- Created: {stats['timeline']['created_at']}
- Last Active: {stats['timeline']['last_active']}

## Exported
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Generated by AI Content Studio
https://github.com/anthropics/unified-donkey-betz
"""
            zip_file.writestr('README.txt', readme)

            # Add images
            for i, img in enumerate(images):
                if img.file_path and not img.file_path.startswith('data:'):
                    file_path = img.file_path
                    if os.path.exists(file_path):
                        zip_file.write(file_path, f'images/image-{i+1}{Path(file_path).suffix}')

            # Add videos
            for i, vid in enumerate(videos):
                if vid.video_url and not vid.video_url.startswith('http'):
                    # Local file
                    if os.path.exists(vid.video_url):
                        zip_file.write(vid.video_url, f'videos/video-{i+1}.mp4')

            # Add 3D models
            for i, model in enumerate(models):
                if model.three_d_file and os.path.exists(model.three_d_file):
                    zip_file.write(model.three_d_file, f'models-3d/model-{i+1}.glb')

        # Prepare response
        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer.read(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{project.name.replace(" ", "_")}.zip"'

        logger.info(f"✅ Project exported as ZIP: {project.name}")
        return response

    except CreativeProject.DoesNotExist:
        logger.error(f"❌ Project not found: {project_id}")
        return HttpResponse('Project not found', status=404)
    except Exception as e:
        logger.error(f"❌ Export ZIP error: {str(e)}")
        import traceback
        traceback.print_exc()
        return HttpResponse(f'Export failed: {str(e)}', status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_featured_examples(request):
    """
    Get curated featured examples for the Examples Gallery
    Session 56: Phase A Task 2
    Returns diverse, high-quality images showcasing platform capabilities
    """
    try:
        from content.models import ImageHistory

        # Get diverse examples - ONLY generated images (Session 56: Bug fix)
        # Edited images (upscale, remove bg, etc.) have operation names as prompts,
        # not useful for "Try This Prompt" feature
        examples = []

        # Strategy: Get up to 12 recent generated images with variety
        # Prioritize diverse models and styles to showcase platform capabilities
        # Session 94: Filter out data URI images (they're too large for JSON response)
        examples = ImageHistory.objects.filter(
            user=request.user,
            image_type='generated'  # ONLY show generated images!
        ).exclude(
            file_path__startswith='data:'  # Exclude base64 data URIs
        ).order_by('-created_at')[:12]

        # Format response
        formatted_examples = []
        for img in examples:
            # Session 94: Additional safety check - skip if file_path is data URI or too long
            if not img.file_path or img.file_path.startswith('data:') or len(img.file_path) > 500:
                continue

            formatted_examples.append({
                'id': str(img.id),
                'url': img.file_path if img.file_path.startswith('http') else f'/media/{img.file_path}',
                'prompt': img.prompt or f'{img.image_type.replace("_", " ").title()}',
                'image_type': img.image_type,
                'model_used': img.model_used or 'sdxl',
                'style': img.style or '',
                'created_at': img.created_at.isoformat()
            })

        logger.info(f"✨ Returning {len(formatted_examples)} featured examples")
        return Response({
            'examples': formatted_examples,
            'count': len(formatted_examples)
        })

    except Exception as e:
        logger.error(f"❌ Error loading featured examples: {str(e)}")
        return Response({
            'error': str(e),
            'examples': []
        }, status=500)


# ========================================
# INTELLIGENT PROMPT IMPROVEMENT (Session 56: Phase B.1)
# ========================================


def get_image_by_number(user, image_number):
    """
    Get image UUID from sequential number

    Session 96 Weekend Project: Hybrid Image ID system
    Allows AI Assistant to understand "Use image 12" commands

    Args:
        user: User object
        image_number: Sequential number (1-based)

    Returns:
        ImageHistory object or None
    """
    from content.models import ImageHistory

    try:
        # Get all user's images ordered by creation date
        images = ImageHistory.objects.filter(user=user).order_by('created_at')

        # Sequential numbers are 1-based, list indices are 0-based
        if image_number < 1:
            return None

        # Get the image at position (image_number - 1)
        if image_number <= images.count():
            return images[image_number - 1]

        return None

    except Exception as e:
        logger.error(f"❌ Error getting image by number: {e}")
        return None


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_meeting_details(request, meeting_key):
    """
    Get full details of a specific executive meeting.

    Session 100: Part 11 - Returns complete meeting data:
    - All executive perspectives
    - Full summary
    - All decisions
    - All action items with ownership
    - Participant info
    """
    try:
        from intelligence.shared_memory import redis_client

        # Get meeting data from Redis
        data = redis_client.get(meeting_key)

        if not data:
            return Response({
                'success': False,
                'error': 'Meeting not found'
            }, status=404)

        meeting_wrapper = json.loads(data)
        # Meeting data is inside the 'content' field
        meeting = meeting_wrapper.get('content', meeting_wrapper)

        logger.info(f"✅ Retrieved meeting details: {meeting.get('topic')}")

        return Response({
            'success': True,
            'meeting': meeting
        })

    except Exception as e:
        logger.error(f"❌ Error getting meeting details: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': 'Failed to retrieve meeting details',
            'details': str(e)
        }, status=500)


# ========================================
# SESSION 125: Image Editing Wrappers (Accept image_id)
# ========================================


def get_or_create_session(user, session_id=None, first_prompt=None, project_id=None):
    """
    Get existing session or create new one for AI Assistant conversations

    Args:
        user: User object
        session_id: UUID of existing session (optional)
        first_prompt: First user message in conversation (for new sessions)
        project_id: UUID of project to associate with (Session 97)

    Returns:
        AISession object
    """
    from content.models import AISession, CreativeProject
    import uuid as uuid_lib

    if session_id:
        # Try to get existing session
        try:
            if isinstance(session_id, str):
                session_id = uuid_lib.UUID(session_id)
            session = AISession.objects.get(session_id=session_id, user=user, is_active=True)
            logger.info(f"📝 Retrieved existing session: {session.session_id}")
            return session
        except AISession.DoesNotExist:
            logger.warning(f"⚠️ Session {session_id} not found, creating new one")

    # Session 97: Get project if provided, or default to Quick Starts
    project = None
    if project_id:
        try:
            if isinstance(project_id, str):
                project_id = uuid_lib.UUID(project_id)
            project = CreativeProject.objects.get(id=project_id, user=user)
            logger.info(f"📁 Linking new session to project: {project.name}")
        except CreativeProject.DoesNotExist:
            logger.warning(f"⚠️ Project {project_id} not found")

    # Fall back to Quick Starts if no project specified
    if not project:
        project = CreativeProject.objects.filter(user=user, is_quick_starts=True).first()
        if project:
            logger.info(f"⚡ Using Quick Starts project for session")

    # Create new session
    # Generate title from first prompt (take first 50 chars or use generic)
    if first_prompt:
        title = first_prompt[:50] + ('...' if len(first_prompt) > 50 else '')
    else:
        title = f"AI Session {timezone.now().strftime('%Y-%m-%d %H:%M')}"

    session = AISession.objects.create(
        user=user,
        title=title,
        first_prompt=first_prompt or '',
        conversation_transcript=[],
        project=project,
        is_active=True
    )

    logger.info(f"✨ Created new session: {session.session_id} - '{title}'")
    return session


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_project(request, project_id):
    """
    Get detailed information about a specific project
    Session 60: Phase C.1.2 - Project Management API
    Session 146: Added stats field with comprehensive project metrics

    GET /api/projects/<uuid:project_id>/

    Returns:
        {
            "project": {
                ... project data ...,
                "stats": {
                    "content": {"images": 42, "videos": 15, "models": 3},
                    "collaboration": {"unique_agents": 3, "decisions_count": 5, "execution_time_seconds": 9000},
                    "timeline": {"created_at": "...", "last_active": "..."}
                },
                "workflows": [
                    {
                        "id": "uuid",
                        "workflow_name": "Logo Creator",
                        "workflow_type": "logo_creator",
                        "status": "completed",
                        "order": 0,
                        "notes": "Main logo design",
                        "created_at": "...",
                        "result_count": 3
                    }
                ]
            }
        }
    """
    try:
        from content.models import CreativeProject

        # Session 60: Using UUID for project lookup
        project = CreativeProject.objects.get(id=project_id, user=request.user)

        # Get all workflows in this project
        workflows_data = []
        for pw in project.workflows.all():
            workflows_data.append({
                'id': str(pw.id),
                'workflow_history_id': str(pw.workflow_history.id),
                'workflow_name': pw.workflow_history.workflow_name,
                'workflow_type': pw.workflow_history.workflow_type,
                'status': pw.workflow_history.status,
                'order': pw.order,
                'notes': pw.notes,
                'added_at': pw.added_at.isoformat(),
                'result_count': pw.workflow_history.result_count,
                'execution_time': pw.workflow_history.execution_time
            })

        # Session 146: Calculate comprehensive project stats
        stats = calculate_project_stats(project_id, request.user)

        project_data = {
            'id': str(project.id),
            'name': project.name,
            'description': project.description,
            'goal': project.goal,
            'status': project.status,
            'category': project.category,
            'colors': project.colors,  # Session 63: Professional agency intake field
            'tags': project.tags,
            'deadline': project.deadline.isoformat() if project.deadline else None,
            'total_workflows': project.total_workflows,
            'completed_workflows': project.completed_workflows,
            'progress_percentage': project.progress_percentage,
            'is_overdue': project.is_overdue,
            'is_shared': project.is_shared,
            'created_at': project.created_at.isoformat(),
            'updated_at': project.updated_at.isoformat(),
            'stats': stats,  # Session 146: Project Stats Header
            'metadata': project.metadata,  # Session 201: Rich workflow data (research links, agent recommendations)
            'workflows': workflows_data
        }

        return Response({'project': project_data})

    except CreativeProject.DoesNotExist:
        return Response({
            'error': 'Project not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error getting project: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_project_sessions(request, project_id):
    """
    Get all AI sessions associated with a specific project
    Session 97: Option 3 - Session Browser in Projects Tab

    Returns sessions with their content counts and last activity
    """
    try:
        from content.models import AISession, ImageHistory, VideoHistory, CreativeProject

        # Verify project exists and belongs to user
        try:
            project = CreativeProject.objects.get(id=project_id, user=request.user)
        except CreativeProject.DoesNotExist:
            return Response({
                'error': 'Project not found'
            }, status=404)

        # Get all sessions that have content linked to this project
        # This includes sessions where images/videos were added to the project
        image_session_ids = ImageHistory.objects.filter(
            user=request.user,
            project_id=project_id
        ).values_list('session_id', flat=True).distinct()

        video_session_ids = VideoHistory.objects.filter(
            user=request.user,
            project_id=project_id
        ).values_list('session_id', flat=True).distinct()

        # Combine session IDs
        session_ids = set(list(image_session_ids) + list(video_session_ids))

        # Remove None values (content without sessions)
        session_ids.discard(None)

        # Get session objects
        sessions = AISession.objects.filter(
            id__in=session_ids,
            user=request.user
        ).order_by('-updated_at')

        # Format sessions
        sessions_data = []
        for session in sessions:
            # Count content in this project from this session
            project_images = ImageHistory.objects.filter(
                session=session,
                project_id=project_id
            ).count()

            project_videos = VideoHistory.objects.filter(
                session=session,
                project_id=project_id
            ).count()

            sessions_data.append({
                'session_id': str(session.session_id),
                'title': session.title or 'Untitled Session',
                'created_at': session.created_at.isoformat(),
                'last_activity': session.updated_at.isoformat(),
                'total_images': session.total_images,
                'total_videos': session.total_videos,
                'total_audio': session.total_audio,
                'project_images': project_images,  # Images from this session in this project
                'project_videos': project_videos,  # Videos from this session in this project
                'has_project': session.project_id is not None,
                'conversation_length': len(session.conversation_transcript or '[]')
            })

        return Response({
            'success': True,
            'project': {
                'id': str(project.id),
                'name': project.name
            },
            'sessions': sessions_data,
            'total_sessions': len(sessions_data)
        })

    except Exception as e:
        logger.error(f"❌ Get project sessions error: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_session_analytics(request):
    """
    Get comprehensive analytics about user's AI sessions
    Session 97: Option 4 - Session Analytics Dashboard

    Returns:
    - Most used prompts/keywords
    - Content type distribution
    - Average session duration
    - Most productive sessions
    - Style preferences
    - Time-based activity patterns
    """
    try:
        from content.models import AISession, ImageHistory, VideoHistory
        from collections import Counter

        user = request.user

        # Get all sessions
        sessions = AISession.objects.filter(user=user)
        total_sessions = sessions.count()

        if total_sessions == 0:
            return Response({
                'success': True,
                'total_sessions': 0,
                'message': 'No sessions yet'
            })

        # Content type distribution
        total_images = sum(s.total_images for s in sessions)
        total_videos = sum(s.total_videos for s in sessions)
        total_audio = sum(s.total_audio for s in sessions)
        total_content = total_images + total_videos + total_audio

        # Sessions with projects
        sessions_with_projects = sessions.filter(project__isnull=False).count()

        # Most productive sessions (by total content)
        most_productive = []
        for session in sessions.order_by('-total_images', '-total_videos', '-total_audio')[:5]:
            content_count = session.total_images + session.total_videos + session.total_audio
            if content_count > 0:
                most_productive.append({
                    'session_id': str(session.session_id),
                    'title': session.title or 'Untitled Session',
                    'total_content': content_count,
                    'images': session.total_images,
                    'videos': session.total_videos,
                    'audio': session.total_audio,
                    'created_at': session.created_at.isoformat()
                })

        # Average content per session
        avg_images = total_images / total_sessions if total_sessions > 0 else 0
        avg_videos = total_videos / total_sessions if total_sessions > 0 else 0
        avg_audio = total_audio / total_sessions if total_sessions > 0 else 0

        # Most common styles (from ImageHistory)
        style_counter = Counter()
        for img in ImageHistory.objects.filter(user=user).exclude(style__isnull=True).exclude(style=''):
            if img.style:
                style_counter[img.style] += 1

        top_styles = [{'style': style, 'count': count} for style, count in style_counter.most_common(10)]

        # Most common models
        model_counter = Counter()
        for img in ImageHistory.objects.filter(user=user).exclude(model_used__isnull=True).exclude(model_used=''):
            if img.model_used:
                model_counter[img.model_used] += 1

        top_models = [{'model': model, 'count': count} for model, count in model_counter.most_common(5)]

        # Activity by day of week
        activity_by_day = {
            'Monday': 0, 'Tuesday': 0, 'Wednesday': 0, 'Thursday': 0,
            'Friday': 0, 'Saturday': 0, 'Sunday': 0
        }
        for session in sessions:
            day_name = session.created_at.strftime('%A')
            activity_by_day[day_name] += 1

        # Recent activity (last 7 days)
        from datetime import timedelta
        from django.utils import timezone
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_sessions = sessions.filter(created_at__gte=seven_days_ago).count()
        recent_content = ImageHistory.objects.filter(
            user=user,
            created_at__gte=seven_days_ago
        ).count() + VideoHistory.objects.filter(
            user=user,
            created_at__gte=seven_days_ago
        ).count()

        # Most common prompt keywords (extract from session titles)
        keyword_counter = Counter()
        for session in sessions:
            if session.title:
                # Simple keyword extraction (split by common words)
                words = session.title.lower().split()
                # Filter out common words
                stop_words = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during'}
                keywords = [w for w in words if w not in stop_words and len(w) > 3]
                keyword_counter.update(keywords)

        top_keywords = [{'keyword': kw, 'count': count} for kw, count in keyword_counter.most_common(15)]

        return Response({
            'success': True,
            'overview': {
                'total_sessions': total_sessions,
                'total_content': total_content,
                'total_images': total_images,
                'total_videos': total_videos,
                'total_audio': total_audio,
                'sessions_with_projects': sessions_with_projects,
                'avg_images_per_session': round(avg_images, 2),
                'avg_videos_per_session': round(avg_videos, 2),
                'avg_audio_per_session': round(avg_audio, 2)
            },
            'content_distribution': {
                'images_percentage': round((total_images / total_content * 100) if total_content > 0 else 0, 1),
                'videos_percentage': round((total_videos / total_content * 100) if total_content > 0 else 0, 1),
                'audio_percentage': round((total_audio / total_content * 100) if total_content > 0 else 0, 1)
            },
            'most_productive_sessions': most_productive,
            'style_preferences': top_styles,
            'model_usage': top_models,
            'activity_by_day': activity_by_day,
            'recent_activity': {
                'sessions_last_7_days': recent_sessions,
                'content_last_7_days': recent_content
            },
            'top_keywords': top_keywords
        })

    except Exception as e:
        logger.error(f"❌ Get session analytics error: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_session_assets(request, session_id):
    """
    Get all assets (images and videos) for a specific session
    Session 101: Project Browser - Mobile Flutter App

    GET /api/v1/sessions/<session_id>/assets/

    Returns:
    {
        "success": true,
        "session": {
            "session_id": "uuid",
            "title": "...",
            "created_at": "..."
        },
        "images": [
            {
                "id": "uuid",
                "file_path": "...",
                "prompt": "...",
                "created_at": "...",
                "model_used": "...",
                "style": "..."
            }
        ],
        "videos": [
            {
                "id": "uuid",
                "file_path": "...",
                "prompt": "...",
                "created_at": "...",
                "model_used": "...",
                "duration": 5
            }
        ],
        "total_images": 10,
        "total_videos": 3
    }
    """
    try:
        from content.models import AISession, ImageHistory, VideoHistory

        # Verify session exists and belongs to user
        try:
            session = AISession.objects.get(id=session_id, user=request.user)
        except AISession.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Session not found'
            }, status=404)

        # Get all images for this session
        images = ImageHistory.objects.filter(
            session=session,
            user=request.user
        ).order_by('-created_at')

        images_data = []
        for img in images:
            images_data.append({
                'id': str(img.id),
                'file_path': img.file_path,
                'prompt': img.prompt,
                'created_at': img.created_at.isoformat(),
                'model_used': img.model_used,
                'style': img.style if hasattr(img, 'style') else None,
                'image_type': img.image_type if hasattr(img, 'image_type') else 'generated',
            })

        # Get all videos for this session
        videos = VideoHistory.objects.filter(
            session=session,
            user=request.user
        ).order_by('-created_at')

        videos_data = []
        for vid in videos:
            videos_data.append({
                'id': str(vid.id),
                'file_path': vid.file_path,
                'prompt': vid.prompt,
                'created_at': vid.created_at.isoformat(),
                'model_used': vid.model_used if hasattr(vid, 'model_used') else 'runway',
                'duration': vid.duration if hasattr(vid, 'duration') else None,
                'status': vid.status if hasattr(vid, 'status') else 'completed',
            })

        return Response({
            'success': True,
            'session': {
                'session_id': str(session.session_id),
                'title': session.title or 'Untitled Session',
                'created_at': session.created_at.isoformat(),
                'session_type': session.session_type if hasattr(session, 'session_type') else 'default',
            },
            'images': images_data,
            'videos': videos_data,
            'total_images': len(images_data),
            'total_videos': len(videos_data),
        })

    except Exception as e:
        logger.error(f"❌ Get session assets error: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


def get_system_user():
    """
    Get or create a system user for autonomous/Celery operations.

    Session 794: When agents execute autonomously (via Celery tasks),
    there's no authenticated user. This function provides a system user
    so that generated content (images, videos, etc.) can still be saved
    to history and tracked properly.

    Returns:
        User: The system user for autonomous operations
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()

    system_user, created = User.objects.get_or_create(
        username='system_autonomous',
        defaults={
            'email': 'system@autonomous.internal',
            'is_active': True,
            'first_name': 'System',
            'last_name': 'Autonomous',
        }
    )

    if created:
        logger.info("🤖 Created system_autonomous user for autonomous operations")

    return system_user


# ========================================
# SESSION MANAGEMENT HELPERS (Session 96: Weekend Project)
# ========================================


def get_user_preferences(user):
    """
    Analyze user's workflow history to identify patterns and preferences
    Session 59: Phase B.4 - Memory System Integration

    Returns a dictionary with:
    - favorite_workflow: Most frequently used workflow type
    - favorite_styles: List of most commonly used styles
    - successful_prompts: Prompts from favorited workflows
    - total_workflows: Total number of workflows executed
    - workflow_patterns: Common workflow sequences
    - recent_activity: Last 5 workflows for context
    """
    from content.models import WorkflowHistory, WorkflowFavorite
    from collections import Counter

    # Get all workflow history for this user
    history = WorkflowHistory.objects.filter(
        user=user,
        status='completed'  # Only count successful executions
    ).order_by('-created_at')

    total_count = history.count()

    if total_count == 0:
        return {
            'has_history': False,
            'total_workflows': 0,
            'message': 'No workflow history yet - start creating to build your preferences!'
        }

    # Analyze workflow type preferences
    workflow_counts = Counter(h.workflow_type for h in history)
    favorite_workflow = workflow_counts.most_common(1)[0] if workflow_counts else None

    # Analyze style preferences from config JSON
    style_usage = Counter()
    model_usage = Counter()

    for h in history:
        if h.config:
            # Check for style in first step (usually generate)
            steps = h.config.get('steps', [])
            if steps and len(steps) > 0:
                first_step = steps[0]
                if isinstance(first_step, dict):
                    step_config = first_step.get('config', {})
                    if 'style' in step_config:
                        style_usage[step_config['style']] += 1
                    if 'model' in step_config:
                        model_usage[step_config['model']] += 1

    favorite_styles = [style for style, count in style_usage.most_common(3)]
    favorite_models = [model for model, count in model_usage.most_common(2)]

    # Find successful patterns (favorited workflows)
    favorites = WorkflowFavorite.objects.filter(user=user).select_related('workflow_history')
    successful_prompts = []

    for fav in favorites[:5]:  # Top 5 favorites
        wf = fav.workflow_history
        if wf.improved_prompt:
            successful_prompts.append({
                'workflow_type': wf.workflow_type,
                'prompt': wf.improved_prompt,
                'use_count': fav.use_count
            })
        elif wf.prompt:
            successful_prompts.append({
                'workflow_type': wf.workflow_type,
                'prompt': wf.prompt,
                'use_count': fav.use_count
            })

    # Analyze workflow sequences (what user does after what)
    recent_workflows = list(history[:20])  # Last 20 for pattern detection
    sequences = []

    for i in range(len(recent_workflows) - 1):
        sequences.append({
            'from': recent_workflows[i].workflow_type,
            'to': recent_workflows[i+1].workflow_type
        })

    sequence_counts = Counter(f"{seq['from']}->{seq['to']}" for seq in sequences)
    common_patterns = [pattern for pattern, count in sequence_counts.most_common(3) if count >= 2]

    # Recent activity for context
    recent_activity = [{
        'workflow_type': h.workflow_type,
        'workflow_name': h.workflow_name,
        'created_at': h.created_at.isoformat(),
        'execution_time': h.execution_time,
        'result_count': h.result_count
    } for h in recent_workflows[:5]]

    return {
        'has_history': True,
        'total_workflows': total_count,
        'favorite_workflow': {
            'type': favorite_workflow[0],
            'count': favorite_workflow[1],
            'percentage': round((favorite_workflow[1] / total_count) * 100, 1)
        } if favorite_workflow else None,
        'favorite_styles': favorite_styles,
        'favorite_models': favorite_models,
        'successful_prompts': successful_prompts,
        'common_patterns': common_patterns,
        'recent_activity': recent_activity,
        'favorites_count': favorites.count()
    }


# ========================================
# AI ASSISTANT CHAT (Session 58: Phase B.3)
# ========================================


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_preferences_api(request):
    """
    Get user preferences and patterns from workflow history
    Session 59: Phase B.4 - Memory System Integration

    Returns user's favorite workflows, styles, patterns, and recent activity
    for smart defaults and personalized recommendations.

    Example response:
    {
        "has_history": true,
        "favorite_workflow": {"type": "logo_creator", "count": 15, "percentage": 45.5},
        "favorite_styles": ["vector", "minimalist", "photographic"],
        "successful_prompts": [...],
        "common_patterns": ["logo_creator->creative_upscale"]
    }
    """
    try:
        preferences = get_user_preferences(request.user)
        return Response(preferences)
    except Exception as e:
        logger.error(f"❌ Error fetching user preferences: {str(e)}")
        return Response({
            'has_history': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def image_history(request):
    """
    Retrieve user's image history for gallery display.

    Query parameters:
    - image_type: Filter by type (generated, erased, inpainted, upscaled_fast, etc.)
    - model_used: Filter by model (core, sdxl, sd3, ultra)
    - style: Filter by style preset
    - is_favorite: Filter favorites (true/false)
    - sort_by: Sort field (created_at, view_count, download_count) - default: -created_at
    - limit: Max results (default: 50)
    - offset: Pagination offset (default: 0)

    Returns:
    {
        "success": true,
        "images": [
            {
                "id": 123,
                "filename": "image.png",
                "url": "/media/...",
                "thumbnail_url": "/media/...",
                "image_type": "generated",
                "prompt": "...",
                "model_used": "sdxl",
                "style": "pixar",
                "width": 1024,
                "height": 1024,
                "created_at": "2025-11-03T...",
                "is_favorite": false,
                "view_count": 5,
                "download_count": 2,
                "has_children": true  // has edits
            }
        ],
        "total": 245,
        "limit": 50,
        "offset": 0
    }
    """
    try:
        from content.models import ImageHistory, CreativeProject

        user = request.user

        # Session 293: Check if filtering by project_id
        # If project_id is provided, show ALL images in that project (if user has access)
        # This allows seeing images created by workflow engine which may use a different user context
        project_id = request.query_params.get('project_id') or request.query_params.get('project')
        logger.info(f"📸 image_history: user={user.username}, project_id={project_id}")

        if project_id:
            # Verify user has access to this project (owns it or is a collaborator)
            try:
                project = CreativeProject.objects.get(id=project_id)
                logger.info(f"📸 Found project: {project.name}, owner={project.user_id}")
                # Allow access if user owns the project (single-user app)
                if project.user != user:
                    # Check if this is a shared/public project or user is collaborator
                    # For now, allow read access to all projects (since it's a single-user app)
                    logger.info(f"📸 User {user.id} accessing project owned by {project.user_id}")
            except CreativeProject.DoesNotExist:
                logger.warning(f"📸 Project not found: {project_id}")
                return Response({
                    'success': False,
                    'error': 'Project not found'
                }, status=404)

            # Get ALL images in this project, not just user's images
            # Session 293: DON'T exclude data: URIs for project queries - needed for Creative Toolbox
            # The dropdown only shows metadata (id, prompt), not the actual image data
            queryset = ImageHistory.objects.filter(project_id=project_id).select_related(
                'project', 'session'
            ).prefetch_related('child_images')
            logger.info(f"📸 Query for project {project_id}: {queryset.count()} images found")
        else:
            # No project filter - show only user's own images
            # Session 94: Exclude data URI images (too large for JSON response)
            # Phase 2 P1: Use select_related/prefetch_related to avoid N+1 queries
            queryset = ImageHistory.objects.filter(user=user).exclude(
                file_path__startswith='data:'
            ).select_related('project', 'session').prefetch_related('child_images')

        # Apply filters
        image_type = request.query_params.get('image_type')
        if image_type:
            queryset = queryset.filter(image_type=image_type)

        model_used = request.query_params.get('model_used')
        if model_used:
            queryset = queryset.filter(model_used=model_used)

        style = request.query_params.get('style')
        if style:
            queryset = queryset.filter(style=style)

        is_favorite = request.query_params.get('is_favorite')
        if is_favorite is not None:
            queryset = queryset.filter(is_favorite=is_favorite.lower() == 'true')

        # Get total count
        total = queryset.count()

        # Apply sorting
        sort_by = request.query_params.get('sort_by', '-created_at')
        queryset = queryset.order_by(sort_by)

        # Apply pagination
        limit = int(request.query_params.get('limit', 50))
        offset = int(request.query_params.get('offset', 0))

        queryset = queryset[offset:offset + limit]

        # Build response
        images = []
        for img in queryset:
            # Session 293: For data URIs, don't include the huge base64 in response
            # Just include a placeholder URL - frontend can fetch individual images if needed
            url = img.get_full_url()
            thumbnail_url = img.get_thumbnail_url()

            # Truncate data URIs to prevent huge responses
            if url and url.startswith('data:'):
                url = f"/api/images/{img.id}/view/"  # Use API endpoint instead
            if thumbnail_url and thumbnail_url.startswith('data:'):
                thumbnail_url = f"/api/images/{img.id}/thumbnail/"

            images.append({
                'id': img.id,
                'sequential_number': img.get_sequential_number(),  # Session 96: Hybrid ID system
                'seed': img.seed,  # Session 95: For reproducibility
                'filename': img.filename,
                'url': url,
                'thumbnail_url': thumbnail_url,
                'image_type': img.image_type,
                'prompt': img.prompt,
                'model_used': img.model_used,
                'style': img.style,
                'width': img.image_width,
                'height': img.image_height,
                'file_size': img.file_size_bytes,
                'created_at': img.created_at.isoformat(),
                'is_favorite': img.is_favorite,
                'view_count': img.view_count,
                'download_count': img.download_count,
                'has_children': img.child_images.exists(),
                'user_notes': img.user_notes,
                'tags': img.tags
            })

        logger.info(f"📊 Gallery request: returned {len(images)}/{total} images for {user.username}")

        return Response({
            'success': True,
            'images': images,
            'total': total,
            'limit': limit,
            'offset': offset
        })

    except Exception as e:
        logger.error(f"❌ Image history error: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


def increment_session_counter(session, content_type):
    """
    Increment session content counter and trigger auto-project creation if needed

    Args:
        session: AISession object
        content_type: 'image', 'video', or 'audio'

    Returns:
        dict: Project creation info if project was auto-created, None otherwise
    """
    if not session:
        return None

    if content_type == 'image':
        session.total_images += 1
        session.save(update_fields=['total_images'])
    elif content_type == 'video':
        session.total_videos += 1
        session.save(update_fields=['total_videos'])
    elif content_type == 'audio':
        session.total_audio += 1
        session.save(update_fields=['total_audio'])

    logger.info(f"📊 Session {session.session_id}: Updated {content_type} counter")

    # Session 96 Weekend Project: Auto-create project if meaningful content created
    # Trigger when: 3+ images OR 1+ video OR 2+ audio files
    should_create_project = (
        session.total_images >= 3 or
        session.total_videos >= 1 or
        session.total_audio >= 2
    )

    # Session 117: FIXED - Also auto-create if session is using Quick Starts placeholder
    # Quick Starts is just a fallback, not a real user project
    has_real_project = session.project and not session.project.is_quick_starts

    if should_create_project and not has_real_project and not session.auto_created_project:
        logger.info(f"🎯 Auto-creating project for session {session.session_id}")
        project = auto_create_project_from_session(session)
        if project:
            # Session 96: Return project info for frontend notification
            return {
                'project_created': True,
                'project_id': project.id,
                'project_name': project.name
            }

    return None


@csrf_exempt
@api_view(['POST'])
def inpaint_image(request):
    """
    Inpaint (regenerate) areas of image using Stability AI inpaint endpoint.
    Requires: image file, mask (areas to regenerate), prompt (what to generate)
    Optional: project_id, source_image_id for proper association
    Session 199: Updated to support project association and proper image history (like erase)
    """
    try:
        if 'image' not in request.FILES or 'mask' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'Missing image or mask file'
            }, status=400)

        prompt = request.POST.get('prompt', '').strip()
        if not prompt:
            return JsonResponse({
                'success': False,
                'error': 'Missing prompt'
            }, status=400)

        image_file = request.FILES['image']
        mask_file = request.FILES['mask']
        project_id = request.POST.get('project_id')
        source_image_id = request.POST.get('source_image_id')

        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')

        if not stability_key:
            return JsonResponse({
                'success': False,
                'error': 'Stability AI API key not configured'
            }, status=500)

        logger.info(f"🎨 Inpaint request - prompt: {prompt}, project: {project_id}, source_image: {source_image_id}")

        url = "https://api.stability.ai/v2beta/stable-image/edit/inpaint"

        files = {
            'image': (image_file.name, image_file.read(), image_file.content_type),
            'mask': (mask_file.name, mask_file.read(), mask_file.content_type)
        }

        data = {
            'prompt': prompt,
            'output_format': 'png'
        }

        headers = {
            'Authorization': f'Bearer {stability_key}',
            'Accept': 'image/*'
        }

        logger.info(f"📤 Calling Stability AI inpaint endpoint...")
        response = requests.post(url, headers=headers, files=files, data=data, timeout=60)
        logger.info(f"📥 Response status: {response.status_code}, size: {len(response.content)} bytes")

        if response.status_code == 200:
            # Session 199: Save with proper user folder structure
            filename = f'inpainted_{uuid.uuid4().hex[:8]}.png'
            filepath = os.path.join('generated_images', request.user.username, filename)
            saved_path = default_storage.save(filepath, ContentFile(response.content))
            image_url = default_storage.url(saved_path)

            logger.info(f"✅ Inpaint complete - saved to {saved_path}")

            # Session 199: Get project and source image for proper association
            from content.models import ImageHistory, CreativeProject
            project = None
            source_image = None

            if project_id:
                try:
                    project = CreativeProject.objects.get(id=project_id, user=request.user)
                except CreativeProject.DoesNotExist:
                    pass

            if source_image_id:
                try:
                    source_image = ImageHistory.objects.get(id=source_image_id, user=request.user)
                    # Inherit project from source if not specified
                    if not project and source_image.project:
                        project = source_image.project
                except ImageHistory.DoesNotExist:
                    pass

            # Create ImageHistory record with project association
            from core.services.workspace_resolver import get_active_workspace
            new_image = ImageHistory.objects.create(
                user=request.user,
                prompt=f"Inpainted: {prompt} (from #{source_image.get_sequential_number() if source_image else 'unknown'})",
                file_path=saved_path,
                filename=filename,
                model_used='stability-inpaint',
                image_type='inpainted',
                project=project,
                session=source_image.session if source_image else None,
                workspace=get_active_workspace(request.user),
            )

            logger.info(f"✅ Created ImageHistory: {new_image.id}, project: {project.id if project else 'none'}")

            return JsonResponse({
                'success': True,
                'image_url': image_url,
                'image_id': str(new_image.id),
                'sequential_number': new_image.get_sequential_number()
            })
        else:
            error_msg = response.text
            logger.error(f"❌ Stability AI inpaint error: {error_msg}")
            return JsonResponse({
                'success': False,
                'error': f'Stability AI error: {error_msg}'
            }, status=500)

    except Exception as e:
        logger.error(f"❌ Inpaint error: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_executive_meetings(request):
    """
    List all executive boardroom meetings for the current user.

    Session 100: Part 11 - Leadership Dashboard with Meeting History

    Returns list of meetings with summary info:
    - Meeting topic
    - Participants
    - Date/time
    - Summary
    - Decision count
    - Action item count
    """
    try:
        from intelligence.shared_memory import redis_client

        # Scan for all meeting keys in meeting_coordinator's memory
        # Keys are stored in db=2 with pattern: shared_memory:agent:meeting_coordinator:boardroom_meeting_*
        pattern = "shared_memory:agent:meeting_coordinator:boardroom_meeting_*"
        cursor = 0
        meetings = []

        while True:
            cursor, keys = redis_client.scan(cursor, match=pattern, count=100)

            for key in keys:
                try:
                    # Get meeting data
                    data = redis_client.get(key)
                    if data:
                        meeting_wrapper = json.loads(data)
                        # Meeting data is inside the 'content' field
                        meeting = meeting_wrapper.get('content', meeting_wrapper)

                        # Extract summary info
                        meetings.append({
                            'key': key.decode('utf-8') if isinstance(key, bytes) else key,
                            'topic': meeting.get('topic', 'Untitled Meeting'),
                            'participants': meeting.get('participants', []),
                            'met_at': meeting.get('met_at'),
                            'summary': meeting.get('summary', '')[:200],  # First 200 chars
                            'decision_count': len(meeting.get('decisions', [])),
                            'action_item_count': len(meeting.get('action_items', [])),
                            'project_id': meeting.get('project_id')
                        })
                except Exception as e:
                    logger.error(f"Error parsing meeting {key}: {str(e)}")
                    continue

            if cursor == 0:
                break

        # Sort by date (newest first)
        meetings.sort(key=lambda x: x.get('met_at', ''), reverse=True)

        logger.info(f"✅ Retrieved {len(meetings)} executive meetings for user {request.user.username}")

        return Response({
            'success': True,
            'meetings': meetings,
            'total': len(meetings)
        })

    except Exception as e:
        logger.error(f"❌ Error listing executive meetings: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': 'Failed to retrieve meetings',
            'details': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def list_projects(request):
    """
    List all creative projects for current user
    Session 60: Phase C.1.2 - Project Management API
    Session 350: Changed to AllowAny, made user-aware for session auth

    GET /api/projects/

    Returns:
        {
            "projects": [
                {
                    "id": "uuid",
                    "name": "Brand Launch Campaign",
                    "description": "...",
                    "goal": "...",
                    "status": "in_progress",
                    "category": "Branding",
                    "deadline": "2025-12-31T23:59:59Z",
                    "total_workflows": 5,
                    "completed_workflows": 2,
                    "progress_percentage": 40,
                    "is_overdue": false,
                    "created_at": "2025-11-06T12:00:00Z",
                    "updated_at": "2025-11-06T14:00:00Z"
                }
            ]
        }
    """
    try:
        from content.models import CreativeProject

        # Session 350: Support both authenticated and anonymous users
        if request.user.is_authenticated:
            projects = CreativeProject.objects.filter(user=request.user).order_by('-created_at')
        else:
            # Anonymous users get empty list (no shared projects to show)
            projects = CreativeProject.objects.none()

        project_data = []
        for project in projects:
            project_data.append({
                'id': str(project.id),
                'name': project.name,
                'sequential_number': project.get_sequential_number(),  # Session 117: Sequential ID
                'description': project.description,
                'goal': project.goal,
                'status': project.status,
                'category': project.category,
                'colors': project.colors,  # Session 63: Professional agency intake field
                'tags': project.tags,
                'deadline': project.deadline.isoformat() if project.deadline else None,
                'total_workflows': project.total_workflows,
                'completed_workflows': project.completed_workflows,
                'progress_percentage': project.progress_percentage,
                'is_overdue': project.is_overdue,
                'is_shared': project.is_shared,
                'is_quick_starts': project.is_quick_starts,  # Session 97: Quick Starts flag
                'last_activity': project.updated_at.isoformat(),  # Session 97: For sorting
                'created_at': project.created_at.isoformat(),
                'updated_at': project.updated_at.isoformat()
            })

        logger.info(f"✅ Loaded {len(project_data)} projects for user {request.user.username}")

        return Response({'projects': project_data})

    except Exception as e:
        logger.error(f"❌ Error listing projects: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_sessions(request):
    """
    List all AI sessions for the current user with filtering and sorting
    Session 97: Session Management UI - List View

    Query parameters:
    - sort: 'newest' (default), 'oldest', 'most_content', 'alphabetical'
    - project_filter: 'all' (default), 'with_project', 'no_project'
    - content_filter: 'all' (default), 'images', 'videos', 'audio'

    Returns:
    {
        "sessions": [
            {
                "session_id": "uuid",
                "title": "Session title",
                "created_at": "timestamp",
                "updated_at": "timestamp",
                "total_images": 5,
                "total_videos": 2,
                "total_audio": 1,
                "project": {
                    "id": "uuid",
                    "name": "Project name"
                } or null,
                "first_prompt": "Original user request"
            },
            ...
        ],
        "stats": {
            "total_sessions": 10,
            "total_images": 45,
            "total_videos": 12,
            "total_audio": 5,
            "sessions_with_projects": 6
        }
    }
    """
    try:
        from content.models import AISession

        user = request.user

        # Get query parameters
        sort_by = request.query_params.get('sort', 'newest')
        project_filter = request.query_params.get('project_filter', 'all')
        content_filter = request.query_params.get('content_filter', 'all')

        # Base queryset
        queryset = AISession.objects.filter(user=user)

        # Apply project filter
        if project_filter == 'with_project':
            queryset = queryset.filter(project__isnull=False)
        elif project_filter == 'no_project':
            queryset = queryset.filter(project__isnull=True)

        # Apply content filter
        if content_filter == 'images':
            queryset = queryset.filter(total_images__gt=0)
        elif content_filter == 'videos':
            queryset = queryset.filter(total_videos__gt=0)
        elif content_filter == 'audio':
            queryset = queryset.filter(total_audio__gt=0)

        # Apply sorting
        if sort_by == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort_by == 'oldest':
            queryset = queryset.order_by('created_at')
        elif sort_by == 'most_content':
            # Sort by total content (images + videos + audio) descending
            from django.db.models import F
            queryset = queryset.annotate(
                total_content=F('total_images') + F('total_videos') + F('total_audio')
            ).order_by('-total_content')
        elif sort_by == 'alphabetical':
            queryset = queryset.order_by('title')

        # Format sessions
        sessions_data = []
        for session in queryset:
            session_data = {
                'session_id': str(session.session_id),
                'title': session.title,
                'created_at': session.created_at.isoformat() if session.created_at else None,
                'updated_at': session.updated_at.isoformat() if session.updated_at else None,
                'total_images': session.total_images,
                'total_videos': session.total_videos,
                'total_audio': session.total_audio,
                'first_prompt': session.first_prompt or '',
                'project': None
            }

            # Include project info if linked
            if session.project:
                session_data['project'] = {
                    'id': str(session.project.id),
                    'name': session.project.name
                }

            sessions_data.append(session_data)

        # Calculate stats
        all_sessions = AISession.objects.filter(user=user)
        stats = {
            'total_sessions': all_sessions.count(),
            'total_images': sum(s.total_images for s in all_sessions),
            'total_videos': sum(s.total_videos for s in all_sessions),
            'total_audio': sum(s.total_audio for s in all_sessions),
            'sessions_with_projects': all_sessions.filter(project__isnull=False).count()
        }

        response_data = {
            'sessions': sessions_data,
            'stats': stats
        }

        logger.info(f"📊 List sessions: {len(sessions_data)} sessions returned for user {user.username}")
        return Response(response_data)

    except Exception as e:
        logger.error(f"❌ List sessions error: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def optimize_image_prompt(request):
    """
    Optimize an image generation prompt using the Intelligent Prompting System
    
    Takes a simple prompt like "donkey walking a dog" and a style like "pixar"
    and returns an enhanced, detailed prompt for better image generation.
    
    Expected request body:
    {
        "prompt": "donkey walking a dog",
        "style": "pixar",
        "quality": "balanced"
    }
    
    Returns:
    {
        "success": true,
        "original_prompt": "donkey walking a dog",
        "enhanced_prompt": "A professional animated donkey character walking a friendly dog...",
        "negative_prompt": "...",
        "optimization_notes": "Added lighting details, anatomical specifications..."
    }
    """
    try:
        user = request.user
        data = request.data
        
        original_prompt = data.get('prompt', '').strip()
        style = data.get('style', '')
        quality = data.get('quality', 'balanced')
        
        if not original_prompt:
            return Response({
                'success': False,
                'error': 'Prompt is required'
            }, status=400)
        
        logger.info(f"🎨 Optimizing prompt for {user.username}: '{original_prompt}' (style: {style})")
        
        # Build style-specific guidance
        style_guidance_map = {
            'pixar': 'Pixar-style 3D animation with expressive characters, smooth rendering, professional lighting',
            'disney': 'Disney animated style with vibrant colors, magical atmosphere, professional quality',
            'studio-ghibli': 'Studio Ghibli hand-drawn animation style, detailed backgrounds, atmospheric lighting',
            'dreamworks': 'DreamWorks animation style with dynamic poses, cinematic composition',
            'cinematic': 'Cinematic photography with dramatic lighting, professional composition, 8K quality',
            'photographic': 'Professional photography, crystal clear focus, proper exposure, realistic details',
            'anime': 'Anime art style with clean lines, vibrant colors, dynamic composition',
            'digital-art': 'Digital art style, highly detailed, professional quality, trending on ArtStation',
        }

        style_guidance = style_guidance_map.get(style.lower()) if style else None

        # Use the Intelligent Prompting System
        from content.ai_providers import AIProviderManager

        # Create a specialized optimization request for image generation
        # Build style instruction conditionally
        style_instruction = ""
        if style and style_guidance:
            style_instruction = f"3. Apply style-specific enhancements: {style_guidance}\n"

        optimization_request = f"""Enhance this image generation prompt for Stability AI:

Original Prompt: "{original_prompt}"
Style: {style or 'natural (no specific style)'}
Quality Level: {quality}

ENHANCEMENT REQUIREMENTS:
1. Keep the core concept from the original prompt
2. Add specific details about:
   - Character/subject anatomy (specify "two legs", "two arms", "perfect anatomy" for characters)
   - Lighting (golden hour, cinematic lighting, volumetric lighting, etc.)
   - Composition (hero shot, wide angle, close-up, etc.)
   - Quality markers (8K, professional, crystal clear, highly detailed)
   - Environment/background details
{style_instruction}{"3" if not style_instruction else "4"}. Avoid vague terms - be specific and descriptive
{"4" if not style_instruction else "5"}. Keep the enhanced prompt under 200 words

Return ONLY the enhanced prompt text, no explanations or formatting."""
        
        # Use AI to enhance the prompt
        ai_manager = AIProviderManager()
        try:
            response = ai_manager.generate_completion(
                prompt=optimization_request,
                provider='anthropic',  # Use Claude for prompt optimization
                model='claude-3-5-sonnet-20241022',
                max_tokens=500,
                temperature=0.7
            )
            
            enhanced_prompt = response.get('content', '').strip()
            
            # If AI fails, use rule-based enhancement as fallback
            if not enhanced_prompt or len(enhanced_prompt) < 20:
                enhanced_prompt = _enhance_prompt_rule_based(original_prompt, style, style_guidance)
            
        except Exception as e:
            logger.warning(f"AI optimization failed, using rule-based fallback: {e}")
            enhanced_prompt = _enhance_prompt_rule_based(original_prompt, style, style_guidance)
        
        # Generate style-specific negative prompt
        negative_prompt = "blurry, low quality, distorted, deformed, extra limbs, extra fingers, extra legs, bad anatomy, disfigured, mutated, ugly, poorly drawn, bad proportions, gross proportions"
        
        if style in ['pixar', 'disney', 'studio-ghibli', 'dreamworks', 'anime']:
            negative_prompt += ", realistic, photograph, 3D render"
        elif style in ['photographic', 'cinematic']:
            negative_prompt += ", cartoon, anime, illustrated, painting, drawing"
        
        logger.info(f"✅ Prompt optimized: {len(original_prompt)} → {len(enhanced_prompt)} chars")
        
        return Response({
            'success': True,
            'original_prompt': original_prompt,
            'enhanced_prompt': enhanced_prompt,
            'negative_prompt': negative_prompt,
            'style': style,
            'quality': quality,
            'optimization_method': 'ai_enhanced'
        })
        
    except Exception as e:
        logger.error(f"❌ Prompt optimization error: {e}")
        return Response({
            'success': False,
            'error': str(e),
            'fallback_prompt': data.get('prompt', '')
        }, status=500)


@csrf_exempt
@api_view(['POST'])
def outpaint_image(request):
    """
    Outpaint (extend) image beyond edges using Stability AI outpaint endpoint.
    Session 64: Now supports multiple directions in one call!
    Requires: image file, directions (comma-separated: left,right,up,down), pixels, prompt
    """
    try:
        if 'image' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'Missing image file'
            }, status=400)

        prompt = request.POST.get('prompt', '').strip()
        directions_str = request.POST.get('directions', '').strip().lower()  # Session 64: Changed from 'direction' to 'directions'
        pixels_str = request.POST.get('pixels', '').strip()

        if not all([prompt, directions_str, pixels_str]):
            return JsonResponse({
                'success': False,
                'error': 'Missing prompt, directions, or pixels'
            }, status=400)

        try:
            pixels = int(pixels_str)
        except ValueError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid pixels value'
            }, status=400)

        # Session 64: Parse multiple directions (comma-separated)
        directions = [d.strip() for d in directions_str.split(',') if d.strip()]

        if not directions:
            return JsonResponse({
                'success': False,
                'error': 'No directions specified'
            }, status=400)

        # Validate all directions
        valid_directions = ['left', 'right', 'up', 'down']
        for direction in directions:
            if direction not in valid_directions:
                return JsonResponse({
                    'success': False,
                    'error': f'Invalid direction: {direction} (must be left/right/up/down)'
                }, status=400)

        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')

        if not stability_key:
            return JsonResponse({
                'success': False,
                'error': 'Stability AI API key not configured'
            }, status=500)

        logger.info(f"📐 Multi-direction outpaint: {', '.join(directions)} by {pixels}px each - {prompt}")

        # Session 64: Sequential outpainting - each uses result from previous
        current_image_data = request.FILES['image'].read()
        current_filename = request.FILES['image'].name

        url = "https://api.stability.ai/v2beta/stable-image/edit/outpaint"
        headers = {
            'Authorization': f'Bearer {stability_key}',
            'Accept': 'image/*'
        }

        # Process each direction sequentially
        for i, direction in enumerate(directions):
            logger.info(f"  📐 Step {i+1}/{len(directions)}: Extending {direction}...")

            files = {
                'image': (current_filename, current_image_data, 'image/png')
            }

            data = {
                'prompt': prompt,
                direction: pixels,  # e.g., 'left': 500
                'output_format': 'png'
            }

            response = requests.post(url, headers=headers, files=files, data=data)

            if response.status_code != 200:
                error_msg = response.text
                logger.error(f"❌ Stability AI outpaint error on {direction}: {error_msg}")
                return JsonResponse({
                    'success': False,
                    'error': f'Outpaint failed on {direction}: {error_msg}'
                }, status=500)

            # Use this result as input for next direction
            current_image_data = response.content
            logger.info(f"  ✅ {direction.capitalize()} extension complete")

        # Save final result
        filename = f'outpainted_{"_".join(directions)}_{uuid.uuid4().hex[:8]}.png'
        filepath = os.path.join('generated_images', filename)
        saved_path = default_storage.save(filepath, ContentFile(current_image_data))
        image_url = default_storage.url(saved_path)

        logger.info(f"✅ Multi-direction outpaint complete - saved to {saved_path}")

        # Save to history (Session 36: Feature 9)
        save_to_history(
            user=request.user,
            file_path=saved_path,
            image_type='outpainted',
            prompt=prompt,
            parameters={
                'operation': 'outpaint',
                'directions': directions,  # Session 64: Save as list
                'pixels': pixels,
                'prompt': prompt
            }
        )

        return JsonResponse({
            'success': True,
            'image_url': image_url,
            'directions_completed': directions  # Session 64: Let frontend know what was done
        })

    except Exception as e:
        logger.error(f"❌ Outpaint error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ========================================
# IMAGE HISTORY / GALLERY (Feature 9)
# ========================================


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def promote_session_to_project(request, session_id):
    """
    Promote a Quick Starts session to its own standalone project
    Session 98: Quick Starts Promotion Feature

    Request body:
    {
        "project_name": "My New Project",
        "description": "Optional description",
        "category": "Optional category"
    }

    Returns:
    {
        "success": true,
        "project": {
            "id": "uuid",
            "name": "Project name",
            ...
        },
        "session": {
            "session_id": "uuid",
            "new_project_id": "uuid"
        },
        "content_moved": {
            "images": 5,
            "videos": 2
        }
    }
    """
    try:
        from content.models import AISession, ImageHistory, VideoHistory, CreativeProject
        import json

        # Get the session
        try:
            session = AISession.objects.get(session_id=session_id, user=request.user)
        except AISession.DoesNotExist:
            return Response({
                'error': 'Session not found or you do not have permission to access it'
            }, status=404)

        # Verify this session is in Quick Starts project
        quick_starts = None
        if session.project:
            quick_starts = session.project
            if not quick_starts.is_quick_starts:
                return Response({
                    'error': 'This session is not in Quick Starts. Only Quick Starts sessions can be promoted.'
                }, status=400)
        else:
            # Session has no project - this shouldn't happen, but allow it
            logger.warning(f"⚠️ Session {session_id} has no project, proceeding with promotion anyway")

        # Get request data
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            data = {}

        project_name = data.get('project_name', '').strip()
        if not project_name:
            # Auto-generate name from session title or first prompt
            project_name = session.title or session.first_prompt or f"Session {session.session_id[:8]}"
            # Clean up the name
            project_name = project_name[:100]  # Limit length

        description = data.get('description', '').strip()
        category = data.get('category', '').strip()

        # Create new standalone project
        new_project = CreativeProject.objects.create(
            user=request.user,
            name=project_name,
            description=description or f"Promoted from Quick Starts session: {session.title or 'Untitled'}",
            category=category or 'general',
            status='in_progress',
            is_quick_starts=False  # NOT a Quick Starts project
        )

        logger.info(f"📁 Created new project: {new_project.name} (ID: {new_project.id})")

        # Move session to new project
        old_project_id = session.project_id
        session.project = new_project
        session.save()

        # Move all content from this session to the new project
        images_moved = ImageHistory.objects.filter(
            session=session,
            user=request.user
        ).update(project=new_project)

        videos_moved = VideoHistory.objects.filter(
            session=session,
            user=request.user
        ).update(project=new_project)

        logger.info(f"✅ Promoted session {session_id} to project '{new_project.name}'")
        logger.info(f"   Moved {images_moved} images and {videos_moved} videos")

        return Response({
            'success': True,
            'message': f"Session promoted to project '{new_project.name}'",
            'project': {
                'id': str(new_project.id),
                'name': new_project.name,
                'description': new_project.description,
                'category': new_project.category,
                'status': new_project.status
            },
            'session': {
                'session_id': str(session.session_id),
                'title': session.title,
                'old_project_id': str(old_project_id) if old_project_id else None,
                'new_project_id': str(new_project.id)
            },
            'content_moved': {
                'images': images_moved,
                'videos': videos_moved
            }
        })

    except Exception as e:
        logger.error(f"❌ Promote session to project error: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'error': str(e)
        }, status=500)


def save_to_history(user, file_path, image_type, prompt='', parameters=None,
                    model_used='', style='', parent_image=None, seed=None, session=None, project=None):
    """
    Helper function to save image to ImageHistory database.

    Args:
        user: User object
        file_path: Path to saved image file
        image_type: Type of image (generated, erased, inpainted, etc.)
        prompt: Prompt used for generation/editing
        parameters: Dict of parameters used
        model_used: Model name (core, sdxl, sd3, ultra)
        style: Style preset name
        parent_image: Parent ImageHistory object if this is an edit
        seed: Random seed used for generation (for reproducibility) - Session 95
        session: AISession object linking to conversation (Session 96 Weekend Project)
        project: CreativeProject object to associate with (Session 124)
    """
    try:
        from content.models import ImageHistory

        # Get image dimensions and file size
        width, height, file_size = None, None, None
        if file_path.startswith('http'):
            # Cloud-stored image (Cloudinary URL) — download to read metadata
            try:
                import requests as _req
                resp = _req.get(file_path, timeout=10)
                if resp.status_code == 200:
                    from io import BytesIO
                    with PILImage.open(BytesIO(resp.content)) as img:
                        width, height = img.size
                    file_size = len(resp.content)
            except Exception as e:
                logger.warning(f"Could not read cloud image metadata: {e}")
        else:
            try:
                full_path = default_storage.path(file_path)
                with PILImage.open(full_path) as img:
                    width, height = img.size
                file_size = os.path.getsize(full_path)
            except Exception as e:
                logger.warning(f"Could not read image metadata: {e}")

        # Session 119: BUGFIX - Assign project if session already has one
        # When resuming a session with existing project, images need to be linked immediately
        # Session 124: Also support direct project parameter
        image_project = None
        if project:
            # Direct project parameter takes precedence (Session 124)
            image_project = project
            logger.info(f"📁 Assigning image to project (direct): {project.name}")
        elif session and session.project:
            # Fall back to session's project (Session 119)
            image_project = session.project
            logger.info(f"📁 Assigning image to project (from session): {session.project.name}")

        # Session 752: Get the image generation agent for tracking
        image_agent = None
        try:
            from core.models.agents_registry import UnifiedAgentTemplate
            image_agent = UnifiedAgentTemplate.objects.get(name='image-generation-agent')
        except Exception as e:
            logger.warning(f"Could not find image-generation-agent: {e}")

        # Create history record
        # Session 752: Now includes agent field for proper contribution tracking
        from core.services.workspace_resolver import get_active_workspace
        history = ImageHistory.objects.create(
            user=user,
            filename=os.path.basename(file_path),
            file_path=file_path,
            image_type=image_type,
            prompt=prompt,
            parameters=parameters or {},
            model_used=model_used,
            style=style,
            image_width=width,
            image_height=height,
            file_size_bytes=file_size,
            parent_image=parent_image,
            seed=seed,  # Session 95: Save seed for reproducibility
            session=session,  # Session 96 Weekend Project: Link to AI conversation
            project=image_project,  # Session 119: BUGFIX - Assign project if session has one
            agent=image_agent,  # Session 752: Set agent for contribution tracking
            workspace=get_active_workspace(user),
        )

        # Session 142/752: Track agent contribution
        # Session 752: Project is now optional - track contributions even without project
        if image_agent:
            try:
                from core.models.agents_registry import AgentContribution
                AgentContribution.objects.create(
                    agent=image_agent,
                    image=history,
                    project=image_project,  # Can be None now (Session 752)
                    contribution_type='generation',
                    task_description=f"Generated {image_type} image using {model_used}",
                    execution_time_seconds=0.0
                )
                logger.info(f"✅ Agent contribution tracked for image {history.id}")
            except Exception as e:
                logger.error(f"❌ Failed to create agent contribution: {e}")
        else:
            logger.debug("Skipping contribution tracking: no agent found")

        logger.info(f"✅ Saved to history: {image_type} - {history.filename} (ID: {history.id})")

        # Session 430: Auto-deliver to Discord if user has linked account
        try:
            from core.services.discord_notifications import discord_notify
            # Build the full image URL
            if history.image_url:
                image_url = history.image_url
                if image_url.startswith('/media/'):
                    image_url = f"http://localhost:8000{image_url}"
                elif not image_url.startswith('http'):
                    image_url = f"http://localhost:8000/media/{image_url}"

                # Deliver to Discord (gallery channel + DM if linked)
                discord_notify.deliver_image_to_user(
                    user=user,
                    image_url=image_url,
                    prompt=prompt or 'No prompt',
                    image_id=history.id,
                    model=model_used or 'Unknown'
                )
        except Exception as discord_error:
            logger.warning(f"Discord delivery failed (non-fatal): {discord_error}")
            # Don't fail image creation if Discord delivery fails

        return history

    except Exception as e:
        logger.error(f"❌ Failed to save image history: {e}")
        # Don't fail the request if history save fails
        return None


from django.views.decorators.csrf import csrf_exempt


@login_required
@rate_limit('image_processing')  # Phase 2 P1: Rate limit image operations (20 requests/min)
def search_and_replace_view(request):
    """
    Search and replace objects in an image (erase functionality).
    Accepts JSON: {image_id: uuid, search_prompt: str, replace_prompt: str (optional), project_id: uuid (optional)}
    """
    try:
        data = json.loads(request.body)
        image_id = data.get('image_id')
        search_prompt = data.get('search_prompt')
        replace_prompt = data.get('replace_prompt', '')  # Empty means remove/erase
        project_id = data.get('project_id')

        if not image_id or not search_prompt:
            return JsonResponse({'success': False, 'error': 'image_id and search_prompt required'}, status=400)

        # Get the image from history
        from content.models import ImageHistory, CreativeProject
        try:
            image = ImageHistory.objects.get(id=image_id, user=request.user)
        except ImageHistory.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Image not found'}, status=404)

        seq_num = image.get_sequential_number()
        action = "Erasing" if not replace_prompt else "Replacing"
        logger.info(f"🎯 {action} '{search_prompt}' in image {image_id} (sequential #{seq_num})")
        logger.info(f"   Replace prompt: '{replace_prompt if replace_prompt else '(seamless blend - text removal mode)'}'")  # Session 197: Debug logging

        # Get image data (handle both data URIs and file paths)
        if image.file_path.startswith('data:'):
            image_data = base64.b64decode(image.file_path.split(',')[1])
        else:
            file_full_path = os.path.join(settings.MEDIA_ROOT, image.file_path)
            with open(file_full_path, 'rb') as f:
                image_data = f.read()

        # Get API key
        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
        if not stability_key:
            return JsonResponse({'success': False, 'error': 'Stability AI API key not configured'}, status=500)

        # Call Stability AI search-and-replace API
        url = "https://api.stability.ai/v2beta/stable-image/edit/search-and-replace"

        files = {'image': image_data}

        # Session 197/198: Improved text removal logic
        # When removing text (no replace_prompt), use a smarter replacement that preserves the image
        # Session 198 v2: "seamless continuation" creates weird shapes on graphics/logos
        # Using a more aggressive removal prompt that works better for both photos and graphics
        if not replace_prompt:
            # For text removal, tell the API to remove completely and fill with background
            effective_prompt = "nothing, empty space, blank area, remove completely"
        else:
            effective_prompt = replace_prompt

        data_params = {
            'search_prompt': search_prompt,
            'prompt': effective_prompt,
            'output_format': 'png'
        }

        headers = {
            "Authorization": f"Bearer {stability_key}",
            "Accept": "image/*"
        }

        api_response = requests.post(url, headers=headers, files=files, data=data_params, timeout=60)

        if api_response.status_code != 200:
            logger.error(f"❌ Stability AI search-and-replace failed: {api_response.text}")
            return JsonResponse({'success': False, 'error': f'Search and replace failed: {api_response.text}'}, status=500)

        # Save the result image to file (NOT as data URI!)
        result_image_data = api_response.content

        # Generate unique filename and save to disk
        filename = f'search_replace_{uuid.uuid4().hex[:8]}.png'
        filepath = os.path.join('generated_images', request.user.username, filename)
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        saved_path = default_storage.save(filepath, ContentFile(result_image_data))
        image_url = default_storage.url(saved_path)

        logger.info(f"✅ Saved search-and-replace result: {saved_path}")

        # Create new image history entry
        project = None
        if project_id:
            try:
                project = CreativeProject.objects.get(id=project_id, user=request.user)
            except CreativeProject.DoesNotExist:
                pass

        prompt_desc = f"Removed '{search_prompt}'" if not replace_prompt else f"Replaced '{search_prompt}' with '{replace_prompt}'"
        from core.services.workspace_resolver import get_active_workspace
        new_image = ImageHistory.objects.create(
            user=request.user,
            prompt=f"{prompt_desc} from image #{seq_num}",
            file_path=saved_path,  # Save FILE PATH, not data URI!
            filename=filename,
            model_used="stability-search-replace",
            project=project,
            workspace=get_active_workspace(request.user),
        )

        # Session 142: Track agent contribution
        try:
            from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
            agent = UnifiedAgentTemplate.objects.get(name='image-editing-agent')
            AgentContribution.objects.create(
                agent=agent,
                image=new_image,
                project=project,
                contribution_type='editing',
                task_description="Edited image using image-editing-agent",
                execution_time_seconds=0.0
            )
            logger.info(f"✅ Agent contribution tracked for image {{ new_image.id }}")
        except Exception as e:
            logger.error(f"❌ Failed to create agent contribution: {e}")
            logger.error(f"❌ Failed to create agent contribution: {e}")

        logger.info(f"✅ Search and replace successful: {new_image.id}")

        return JsonResponse({
            'success': True,
            'image_id': str(new_image.id),
            'image_url': new_image.file_path,
            'sequential_number': new_image.get_sequential_number()
        })

    except Exception as e:
        logger.error(f"❌ Search and replace error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def serve_image(request, image_id):
    """
    Session 293: Serve an image by its UUID.
    Returns the image data (handles both file-based and data URI images).
    """
    from content.models import ImageHistory
    from django.http import HttpResponse
    import base64

    try:
        image = ImageHistory.objects.get(id=image_id)

        # Check if user has access (owns it or it's in a project they can access)
        # For now, allow access if user is authenticated

        if image.file_path.startswith('data:'):
            # Parse data URI: data:image/png;base64,XXXXXX
            try:
                header, encoded = image.file_path.split(',', 1)
                # Extract mime type: data:image/png;base64 -> image/png
                mime_type = header.split(':')[1].split(';')[0]
                image_data = base64.b64decode(encoded)
                return HttpResponse(image_data, content_type=mime_type)
            except Exception as e:
                logger.error(f"Failed to parse data URI: {e}")
                return Response({'error': 'Invalid image data'}, status=500)
        else:
            # File-based image - redirect to actual URL
            from django.shortcuts import redirect
            from django.core.files.storage import default_storage
            return redirect(default_storage.url(image.file_path))

    except ImageHistory.DoesNotExist:
        return Response({'error': 'Image not found'}, status=404)
    except Exception as e:
        logger.error(f"Error serving image {image_id}: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def test_image_generation(request):
    """
    Test endpoint to verify image generation is configured
    """
    stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
    replicate_key = os.getenv('REPLICATE_API_KEY') or settings.AI_PROVIDERS.get('REPLICATE_API_KEY')

    return Response({
        'success': True,
        'image_generation_configured': bool(stability_key or replicate_key),
        'providers': {
            'stability': {
                'configured': bool(stability_key),
                'status': 'ready' if stability_key else 'missing_api_key'
            },
            'replicate': {
                'configured': bool(replicate_key),
                'status': 'ready' if replicate_key else 'missing_api_key'
            }
        },
        'message': 'Image generation is ready' if (stability_key or replicate_key) else 'Configure API keys to enable image generation'
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_favorite(request, image_id):
    """
    Toggle favorite status for an image.

    Returns updated favorite status.

    Session 489: Now tracks implicit learning signals.
    """
    try:
        from content.models import ImageHistory

        image = ImageHistory.objects.get(id=image_id, user=request.user)
        image.is_favorite = not image.is_favorite
        image.save(update_fields=['is_favorite'])

        logger.info(f"⭐ Toggled favorite for image {image_id}: {image.is_favorite}")

        # Session 489: Track implicit learning signal
        try:
            from core.services.implicit_learning import get_learning_service
            learning = get_learning_service()
            if image.is_favorite:
                # Favoriting = positive signal
                learning.track_favorite(
                    user_id=request.user.id,
                    content_id=str(image_id),
                    style=image.style or None,
                    model=image.model_used or None
                )
            # Note: unfavoriting doesn't generate a negative signal (neutral action)
        except Exception as learn_error:
            logger.debug(f"Implicit learning tracking failed (non-fatal): {learn_error}")

        return Response({
            'success': True,
            'is_favorite': image.is_favorite
        })

    except ImageHistory.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Image not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Toggle favorite error: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def track_image_view(request, image_id):
    """
    Track when a user views an image in fullsize.

    URL: POST /api/images/view/<uuid>/
    """
    try:
        image = ImageHistory.objects.get(id=image_id, user=request.user)
        image.view_count += 1
        image.save(update_fields=['view_count'])

        logger.info(f"✅ Image view tracked: {image_id} (total: {image.view_count})")

        return Response({
            'success': True,
            'view_count': image.view_count
        })
    except ImageHistory.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Image not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Track image view error: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def transcribe_audio(request):
    """
    Transcribe audio using OpenAI Whisper API
    Session 64: Voice input for AI Assistant

    Accepts audio file and returns transcribed text.
    User can then edit the text before sending to assistant.

    Example:
        Input: Audio blob (webm/mp4/wav)
        Output: {"text": "I want to create a logo but I'm not sure what prompt to use"}
    """
    try:
        # Get audio file from request
        audio_file = request.FILES.get('audio')

        if not audio_file:
            return Response({
                'error': 'No audio file provided'
            }, status=400)

        logger.info(f"🎤 Transcribing audio for {request.user.username} ({audio_file.size} bytes)")

        # Call OpenAI Whisper API
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        # Session 81: Convert Django InMemoryUploadedFile to BytesIO for OpenAI SDK
        # OpenAI SDK doesn't accept Django's file object directly
        from io import BytesIO
        audio_file.seek(0)
        audio_bytes = audio_file.read()
        audio_file_like = BytesIO(audio_bytes)

        # Session 124: Use the actual file extension from the uploaded file
        # This ensures OpenAI Whisper gets the correct format hint
        audio_file_like.name = audio_file.name or "recording.webm"
        logger.info(f"🎤 Audio file: {audio_file_like.name} ({len(audio_bytes)} bytes)")

        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file_like,
            language="en"  # Can be removed to auto-detect
        )

        transcribed_text = transcript.text.strip()
        logger.info(f"✅ Transcribed: '{transcribed_text[:100]}...'")

        return Response({
            'text': transcribed_text,
            'success': True
        })

    except Exception as e:
        logger.error(f"❌ Error transcribing audio: {str(e)}")
        return Response({
            'error': 'Failed to transcribe audio. Please try again!',
            'details': str(e) if settings.DEBUG else None
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unified_toggle_favorite(request):
    """
    Toggle favorite status for any media type (image, video, audio).

    Expects JSON: {
        "id": "uuid",
        "type": "image" | "video" | "audio"
    }

    Returns: {
        "success": true,
        "is_favorite": true/false
    }
    """
    try:
        from content.models import ImageHistory, VideoHistory

        item_id = request.data.get('id')
        item_type = request.data.get('type')

        if not item_id or not item_type:
            return Response({
                'success': False,
                'error': 'Missing id or type'
            }, status=400)

        # Toggle favorite based on type
        if item_type == 'image':
            try:
                item = ImageHistory.objects.get(id=item_id, user=request.user)
                item.is_favorite = not item.is_favorite
                item.save()

                logger.info(f"{'⭐' if item.is_favorite else '☆'} Image {item_id} favorite: {item.is_favorite}")

                return Response({
                    'success': True,
                    'is_favorite': item.is_favorite
                })

            except ImageHistory.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Image not found'
                }, status=404)

        elif item_type == 'video':
            try:
                item = VideoHistory.objects.get(id=item_id, user=request.user)
                item.is_favorite = not item.is_favorite
                item.save()

                logger.info(f"{'⭐' if item.is_favorite else '☆'} Video {item_id} favorite: {item.is_favorite}")

                return Response({
                    'success': True,
                    'is_favorite': item.is_favorite
                })

            except VideoHistory.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Video not found'
                }, status=404)

        else:
            return Response({
                'success': False,
                'error': f'Unsupported type: {item_type}'
            }, status=400)

    except Exception as e:
        logger.error(f"❌ Unified toggle favorite error: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_project(request, project_id):
    """
    Update an existing project
    Session 60: Phase C.1.2 - Project Management API

    PUT/PATCH /api/projects/<uuid:project_id>/
    Body:
        {
            "name": "Updated Name" (optional),
            "description": "..." (optional),
            "goal": "..." (optional),
            "status": "in_progress" (optional),
            "deadline": "..." (optional),
            "category": "..." (optional),
            "tags": [...] (optional)
        }

    Returns:
        {
            "success": true,
            "project": { ... updated project data ... }
        }
    """
    try:
        from content.models import CreativeProject
        from django.utils.dateparse import parse_datetime

        # Session 60: Using UUID for project lookup
        project = CreativeProject.objects.get(id=project_id, user=request.user)

        # Update fields if provided
        if 'name' in request.data:
            project.name = request.data['name'].strip()

        if 'description' in request.data:
            project.description = request.data['description'].strip()

        if 'goal' in request.data:
            project.goal = request.data['goal'].strip()

        if 'status' in request.data:
            status = request.data['status']
            valid_statuses = ['planning', 'in_progress', 'review', 'completed', 'archived']
            if status in valid_statuses:
                project.status = status

        if 'deadline' in request.data:
            deadline_str = request.data['deadline']
            if deadline_str:
                project.deadline = parse_datetime(deadline_str)
            else:
                project.deadline = None

        if 'category' in request.data:
            project.category = request.data['category']

        if 'colors' in request.data:  # Session 63: Professional agency intake field
            project.colors = request.data['colors']

        if 'tags' in request.data:
            project.tags = request.data['tags']

        project.save()

        logger.info(f"✅ Updated project '{project.name}' for user {request.user.username}")

        return Response({
            'success': True,
            'project': {
                'id': str(project.id),
                'name': project.name,
                'description': project.description,
                'goal': project.goal,
                'status': project.status,
                'category': project.category,
                'colors': project.colors,  # Session 63: Professional agency intake field
                'tags': project.tags,
                'deadline': project.deadline.isoformat() if project.deadline else None,
                'progress_percentage': project.progress_percentage,
                'updated_at': project.updated_at.isoformat()
            }
        })

    except CreativeProject.DoesNotExist:
        return Response({
            'error': 'Project not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error updating project: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


def update_session_transcript(session, role, content):
    """
    Add message to session conversation transcript

    Args:
        session: AISession object
        role: 'user' or 'assistant'
        content: Message content
    """
    if not session:
        return

    session.conversation_transcript.append({
        'role': role,
        'content': content,
        'timestamp': timezone.now().isoformat()
    })
    session.save(update_fields=['conversation_transcript'])


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_image(request):
    """
    Session 197: Upload an image file to a project.

    Request (multipart/form-data):
    - image: File upload
    - project_id: UUID of the project
    - description: Optional description/prompt

    Returns:
    {
        "success": true,
        "image_id": "uuid",
        "sequential_number": 42,
        "url": "/media/..."
    }
    """
    try:
        from content.models import ImageHistory
        from projects.models import CreativeProject
        import uuid as uuid_lib
        from PIL import Image
        import io

        # Get the uploaded file
        image_file = request.FILES.get('image')
        if not image_file:
            return Response({'success': False, 'error': 'No image file provided'}, status=400)

        # Get project
        project_id = request.data.get('project_id')
        project = None
        if project_id:
            try:
                if isinstance(project_id, str):
                    project_id = uuid_lib.UUID(project_id)
                project = CreativeProject.objects.get(id=project_id, user=request.user)
            except CreativeProject.DoesNotExist:
                return Response({'success': False, 'error': 'Project not found'}, status=404)

        # Get description
        description = request.data.get('description', '') or request.data.get('prompt', 'Uploaded image')

        # Read image and get dimensions
        image_data = image_file.read()
        img = Image.open(io.BytesIO(image_data))
        width, height = img.size

        # Generate unique filename
        ext = image_file.name.split('.')[-1].lower() if '.' in image_file.name else 'png'
        if ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
            ext = 'png'
        filename = f"uploaded_{uuid_lib.uuid4().hex[:12]}.{ext}"

        # Save to media directory
        import os
        from django.conf import settings

        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploaded_images')
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(image_data)

        # Create ImageHistory record
        relative_path = f"uploaded_images/{filename}"

        from core.services.workspace_resolver import get_active_workspace
        image_record = ImageHistory.objects.create(
            user=request.user,
            filename=filename,
            file_path=relative_path,
            image_type='uploaded',
            prompt=description,
            parameters={},
            model_used='upload',
            image_width=width,
            image_height=height,
            file_size_bytes=len(image_data),
            project=project,
            workspace=get_active_workspace(request.user),
        )

        logger.info(f"📤 Image uploaded: {filename} (ID: {image_record.id})")

        return Response({
            'success': True,
            'image_id': str(image_record.id),
            'sequential_number': image_record.get_sequential_number(),
            'url': image_record.get_full_url(),
            'filename': filename
        })

    except Exception as e:
        logger.error(f"❌ Image upload error: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

