"""
Image views — workflow functions.
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
from core.services.openai_client_factory import get_openai_client
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

# Session 1083 (Rigby audit): build_prompt_from_form and
# generate_image_with_stability were referenced 6 times in this file
# but never imported. Every image-workflow dispatch path was throwing
# NameError at one of these lookups.
from core.views_image_misc import build_prompt_from_form  # noqa: E402
from core.views_image_generate import generate_image_with_stability  # noqa: E402

logger = logging.getLogger(__name__)


# ========================================
# SESSION 794: SYSTEM USER FOR AUTONOMOUS OPERATIONS
# ========================================

from django.views.decorators.csrf import csrf_exempt


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_workflow_to_project(request, project_id):
    """
    Add a workflow to a project
    Session 60: Phase C.1.2 - Project Management API

    POST /api/projects/<uuid:project_id>/workflows/
    Body:
        {
            "workflow_history_id": "uuid",
            "order": 0 (optional),
            "notes": "Main logo design" (optional)
        }

    Returns:
        {
            "success": true,
            "project_workflow": { ... }
        }
    """
    try:
        from content.models import CreativeProject, ProjectWorkflow, WorkflowHistory

        # Session 60: Using UUID for project lookup
        project = CreativeProject.objects.get(id=project_id, user=request.user)

        workflow_history_id = request.data.get('workflow_history_id')
        if not workflow_history_id:
            return Response({
                'error': 'workflow_history_id is required'
            }, status=400)

        # Session 60: Using UUID for workflow lookup
        workflow_history = WorkflowHistory.objects.get(
            id=workflow_history_id,
            user=request.user
        )

        # Check if already in project
        existing = ProjectWorkflow.objects.filter(
            project=project,
            workflow_history=workflow_history
        ).exists()

        if existing:
            return Response({
                'error': 'Workflow already in this project'
            }, status=400)

        # Get order (default to end of list)
        order = request.data.get('order')
        if order is None:
            # Add to end
            max_order = project.workflows.count()
            order = max_order

        notes = request.data.get('notes', '')

        # Create link
        project_workflow = ProjectWorkflow.objects.create(
            project=project,
            workflow_history=workflow_history,
            order=order,
            notes=notes
        )

        logger.info(f"✅ Added workflow '{workflow_history.workflow_name}' to project '{project.name}'")

        return Response({
            'success': True,
            'project_workflow': {
                'id': str(project_workflow.id),
                'project_id': str(project.id),
                'workflow_history_id': str(workflow_history.id),
                'workflow_name': workflow_history.workflow_name,
                'order': project_workflow.order,
                'notes': project_workflow.notes,
                'added_at': project_workflow.added_at.isoformat()
            }
        }, status=201)

    except CreativeProject.DoesNotExist:
        return Response({
            'error': 'Project not found'
        }, status=404)
    except WorkflowHistory.DoesNotExist:
        return Response({
            'error': 'Workflow not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error adding workflow to project: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_workflow_execution(request, workflow_id):
    """
    Update workflow history record when workflow completes
    Session 57: Phase B.2 - Workflow History & Favorites

    Expected JSON:
    {
        "status": "completed" | "failed",
        "execution_time": 12.5,  // seconds
        "result_images": ["url1", "url2"],  // For completed
        "error_message": "Error details"  // For failed
    }
    """
    try:
        from content.models import WorkflowHistory

        workflow = WorkflowHistory.objects.get(
            id=workflow_id,
            user=request.user
        )

        status = request.data.get('status', '').strip().lower()
        execution_time = float(request.data.get('execution_time', 0))

        if status == 'completed':
            result_images = request.data.get('result_images', [])
            workflow.mark_completed(execution_time, result_images)
            logger.info(f"✅ Completed workflow execution: {workflow.id} ({workflow.workflow_name}) - {len(result_images)} results")

        elif status == 'failed':
            error_message = request.data.get('error_message', 'Unknown error')
            workflow.mark_failed(error_message)
            workflow.execution_time = execution_time
            workflow.save(update_fields=['execution_time'])
            logger.error(f"❌ Failed workflow execution: {workflow.id} ({workflow.workflow_name}) - {error_message}")

        else:
            return Response({
                'error': 'status must be "completed" or "failed"'
            }, status=400)

        return Response({
            'success': True,
            'workflow_history_id': workflow.id,
            'status': workflow.status
        })

    except WorkflowHistory.DoesNotExist:
        return Response({
            'error': 'Workflow not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error completing workflow execution: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


# =============================================================================
# SESSION 60: PHASE C.1.2 - PROJECT MANAGEMENT API ENDPOINTS
# =============================================================================


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_workflow_favorite(request, favorite_id):
    """
    Delete a workflow favorite
    Session 57: Phase B.2 - Workflow History & Favorites
    """
    try:
        from content.models import WorkflowFavorite

        favorite = WorkflowFavorite.objects.get(
            id=favorite_id,
            user=request.user
        )

        workflow_id = favorite.workflow_history.id
        favorite.delete()

        # Check if workflow has any other favorites
        from content.models import WorkflowHistory
        workflow = WorkflowHistory.objects.get(id=workflow_id)
        has_other_favorites = WorkflowFavorite.objects.filter(
            workflow_history=workflow
        ).exists()

        # Unmark workflow as favorite if no other favorites exist
        if not has_other_favorites and workflow.is_favorite:
            workflow.is_favorite = False
            workflow.save(update_fields=['is_favorite'])

        return Response({
            'success': True,
            'favorite_id': favorite_id
        })

    except WorkflowFavorite.DoesNotExist:
        return Response({
            'error': 'Favorite not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error deleting favorite: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def execute_workflow_for_project(request):
    """
    Session 63: Execute workflow and link results to project
    Endpoint: /api/workflows/execute-for-project/
    """
    try:
        project_id = request.data.get('project_id')
        workflow_type = request.data.get('workflow_type')
        form_data = request.data.get('form_data')

        if not all([project_id, workflow_type, form_data]):
            return Response({
                'success': False,
                'error': 'Missing required fields: project_id, workflow_type, form_data'
            }, status=400)

        # Verify project exists and belongs to user
        from content.models import CreativeProject
        try:
            project = CreativeProject.objects.get(id=project_id, user=request.user)
        except CreativeProject.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Project not found'
            }, status=404)

        logger.info(f"🎨 Executing {workflow_type} for project: {project.name}")

        # Session 63: Build prompt from form data AND PROJECT GOAL!
        prompt = build_prompt_from_form(workflow_type, form_data, project)

        if not prompt:
            return Response({
                'success': False,
                'error': f'Could not build prompt for workflow type: {workflow_type}'
            }, status=400)

        logger.info(f"📝 Built prompt: {prompt}")

        # Execute workflow based on type
        results = []
        error_messages = []  # Session 64: Collect error messages for debugging

        if workflow_type == 'logo-creator':
            # Session 64: Choose model based on logo style - SDXL for character mascots, Core for flat logos
            logo_style = form_data.get('logoStyle', 'character-mascot')
            model = 'sdxl' if logo_style == 'character-mascot' else 'core'

            # Session 64: Truncate prompt if too long (SDXL limit is 2000 chars)
            if len(prompt) > 2000:
                logger.warning(f"⚠️ Prompt too long ({len(prompt)} chars), truncating intelligently")

                # Session 64: Intelligent truncation - prioritize CRITICAL keywords
                # GPT-5 puts clothing in the middle, which gets cut by naive truncation!

                # Extract sentences with critical keywords (clothing, accessories, key features)
                import re
                critical_keywords = ['WEARING', 'DRESSED', 'PLATFORM', 'necklace', 'pants', 'shoes',
                                   'outfit', 'clothing', 'accessory', 'bell-bottom', 'disco ball']

                # Split into sentences
                sentences = re.split(r'[.!?]\s+', prompt)

                # Categorize sentences
                critical_sentences = []
                normal_sentences = []

                for sent in sentences:
                    if any(keyword.lower() in sent.lower() for keyword in critical_keywords):
                        critical_sentences.append(sent)
                    else:
                        normal_sentences.append(sent)

                # Build truncated prompt: critical details + as many normal details as fit
                prompt_parts = []
                char_count = 0

                # Always include critical sentences (clothing!)
                for sent in critical_sentences:
                    if char_count + len(sent) + 2 < 1900:  # Leave room for period
                        prompt_parts.append(sent)
                        char_count += len(sent) + 2

                # Add normal sentences until we hit limit
                for sent in normal_sentences:
                    if char_count + len(sent) + 2 < 1950:
                        prompt_parts.append(sent)
                        char_count += len(sent) + 2
                    else:
                        break

                prompt = '. '.join(prompt_parts) + '.'
                logger.info(f"📝 Intelligently truncated to {len(prompt)} chars, kept {len(critical_sentences)} critical sentences")
                logger.info(f"📝 Truncated prompt: {prompt[:200]}...")

            # Generate 1 logo (style already included in prompt by build_prompt_from_form)
            # Session 64: Pass empty string as style since prompt already contains style terms
            result = generate_image_with_stability(
                prompt=prompt,
                model=model,
                style='',  # Use empty string to avoid applying additional style preset (prompt has style terms already)
                user=request.user
            )
            if result and result.get('success'):
                results.append(result)
            elif result and result.get('error'):
                error_messages.append(f"Logo generation failed: {result.get('error')}")
            else:
                error_messages.append("Logo generation returned no result")

        elif workflow_type == 'portrait-enhancer':
            # Generate 1 high-quality portrait
            result = generate_image_with_stability(
                prompt=prompt,
                model='sd3',
                style='photographic',
                user=request.user
            )
            if result and result.get('success'):
                results.append(result)

        elif workflow_type == 'style-explorer':
            # Generate 5 images in different styles
            styles = ['photographic', 'digital-art', 'cinematic', 'anime', 'fantasy-art']
            for style in styles:
                result = generate_image_with_stability(
                    prompt=prompt,
                    model='sdxl',
                    style=style,
                    user=request.user
                )
                if result and result.get('success'):
                    results.append(result)

        elif workflow_type == 'social-media-pack':
            # Generate 3 optimized images
            for i in range(3):
                result = generate_image_with_stability(
                    prompt=prompt,
                    model='sdxl',
                    style='photographic',
                    user=request.user
                )
                if result and result.get('success'):
                    results.append(result)

        elif workflow_type == 'product-mockup':
            # Generate 1 product visualization
            result = generate_image_with_stability(
                prompt=prompt,
                model='ultra',
                style='photographic',
                user=request.user
            )
            if result and result.get('success'):
                results.append(result)

        elif workflow_type == 'creative-upscale':
            # Note: This requires an existing image - handle separately
            return Response({
                'success': False,
                'error': 'Creative Upscale requires selecting an existing image first'
            }, status=400)

        # Link all generated images to the project
        if results:
            from content.models import ImageHistory
            linked_count = 0

            for result in results:
                if result.get('image_id'):
                    try:
                        image = ImageHistory.objects.get(id=result['image_id'], user=request.user)
                        image.project = project
                        image.save()
                        linked_count += 1
                        logger.info(f"✅ Linked image {image.id} to project {project.name}")
                    except ImageHistory.DoesNotExist:
                        logger.warning(f"⚠️ Image {result['image_id']} not found")

            logger.info(f"🎉 Successfully generated and linked {linked_count} assets to project {project.name}")

            return Response({
                'success': True,
                'count': linked_count,
                'message': f'Generated {linked_count} assets for {project.name}'
            })
        else:
            # Session 64: Include actual error messages for debugging
            error_detail = 'No images were generated'
            if error_messages:
                error_detail += ': ' + '; '.join(error_messages)

            return Response({
                'success': False,
                'error': error_detail
            }, status=500)

    except Exception as e:
        logger.error(f"❌ Error executing workflow for project: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@api_view(['POST'])
def execute_workflow_step(request):
    """
    Execute a single workflow step by routing to the appropriate operation.

    Expected JSON request body:
    {
        "operation": "upscale_fast" | "upscale_conservative" | "upscale_creative" |
                     "remove_background" | "recolor" | "erase" | "inpaint" |
                     "outpaint" | "sketch" | "structure" | "generate",
        "inputImageUrl": "url_to_image" (required for all except generate),
        "config": {
            // Operation-specific parameters
            "prompt": "...",           // for generate, recolor, inpaint, outpaint, sketch, structure
            "search_prompt": "...",    // for recolor
            "select_prompt": "...",    // for recolor
            "creativity": 0.5,         // for outpaint
            "direction": "up",         // for outpaint
            "control_strength": 0.7,   // for sketch, structure
            // ... etc
        }
    }

    Returns: {success: true, imageUrl: "url_to_result_image"}
    """
    try:
        # Parse JSON request (DRF already parses request.body for us)
        data = request.data
        operation = (data.get('operation') or '').strip().lower()
        input_image_url = (data.get('inputImageUrl') or '').strip()
        config = data.get('config', {})

        logger.info(f"🎭 Workflow step execution: {operation}")

        # Validate operation
        valid_operations = [
            'upscale_fast', 'upscale_conservative', 'upscale_creative',
            'remove_background', 'recolor', 'erase', 'inpaint', 'outpaint',
            'sketch', 'structure', 'generate'
        ]

        if operation not in valid_operations:
            return JsonResponse({
                'success': False,
                'error': f'Invalid operation: {operation}'
            }, status=400)

        # Download input image if URL provided (all operations except generate need this)
        image_file = None
        if input_image_url and operation != 'generate':
            try:
                # Download image from URL
                if input_image_url.startswith('http'):
                    img_response = requests.get(input_image_url, timeout=10)
                    img_response.raise_for_status()
                    image_data = img_response.content
                elif input_image_url.startswith('/media/'):
                    # Local file - read from filesystem
                    local_path = os.path.join(settings.MEDIA_ROOT, input_image_url.replace('/media/', ''))
                    with open(local_path, 'rb') as f:
                        image_data = f.read()
                elif input_image_url.startswith('data:image'):
                    # Data URI - extract base64 data
                    if 'base64,' in input_image_url:
                        base64_data = input_image_url.split('base64,')[1]
                        image_data = base64.b64decode(base64_data)
                    else:
                        return JsonResponse({
                            'success': False,
                            'error': 'Invalid data URI format'
                        }, status=400)
                else:
                    return JsonResponse({
                        'success': False,
                        'error': 'Invalid image URL format'
                    }, status=400)

                # Check and resize if needed (Stability AI limits: 10MiB file size, 1,048,576 pixels)
                # Note: Different operations have different limits, using most conservative (1024x1024)
                from PIL import Image
                import io

                max_size_bytes = 10 * 1024 * 1024  # 10MiB
                max_pixels = 1_048_576  # 1024x1024 (most conservative limit across all operations)

                # Open image to check dimensions
                img = Image.open(io.BytesIO(image_data))
                width, height = img.size
                total_pixels = width * height

                logger.info(f"📏 Original image: {width}x{height} = {total_pixels:,} pixels, {len(image_data):,} bytes")

                # Check if we need to resize due to pixel count
                needs_resize = False
                if total_pixels > max_pixels:
                    # Calculate scale factor to fit within pixel limit
                    scale_factor = (max_pixels / total_pixels) ** 0.5
                    new_width = int(width * scale_factor)
                    new_height = int(height * scale_factor)

                    logger.info(f"⚠️ Too many pixels ({total_pixels:,}), resizing to {new_width}x{new_height}")

                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    needs_resize = True

                # Check if we need to resize due to file size
                if needs_resize or len(image_data) > max_size_bytes:
                    logger.info(f"⚠️ Optimizing image size...")

                    # Save with optimization
                    quality = 85
                    img_bytes = io.BytesIO()
                    img.save(img_bytes, format='PNG', optimize=True, quality=quality)
                    image_data = img_bytes.getvalue()

                    # If still too large, reduce quality iteratively
                    while len(image_data) > max_size_bytes and quality > 60:
                        quality -= 10
                        img_bytes = io.BytesIO()
                        img.save(img_bytes, format='PNG', optimize=True, quality=quality)
                        image_data = img_bytes.getvalue()

                    logger.info(f"✅ Optimized image to {len(image_data):,} bytes (quality={quality})")

                # Create a file-like object
                from django.core.files.uploadedfile import InMemoryUploadedFile

                image_io = io.BytesIO(image_data)
                image_file = InMemoryUploadedFile(
                    image_io,
                    field_name='image',
                    name=f'workflow_input_{uuid.uuid4().hex[:8]}.png',
                    content_type='image/png',
                    size=len(image_data),
                    charset=None
                )

                logger.info(f"✅ Downloaded input image: {len(image_data):,} bytes")

            except Exception as e:
                logger.error(f"❌ Failed to download input image: {e}")
                return JsonResponse({
                    'success': False,
                    'error': f'Failed to download input image: {str(e)}'
                }, status=500)

        # Route to appropriate operation
        if operation == 'upscale_fast':
            # Call Stability AI directly
            try:
                from PIL import Image
                img = Image.open(image_file)

                # Call API
                stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
                url = 'https://api.stability.ai/v2beta/stable-image/upscale/fast'

                # Prepare image data
                import io
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)

                files = {'image': ('image.png', img_bytes.read(), 'image/png')}
                data = {'output_format': 'png'}
                headers = {'Authorization': f'Bearer {stability_key}', 'Accept': 'image/*'}

                response = requests.post(url, headers=headers, files=files, data=data)

                if response.status_code == 200:
                    filename = f'upscaled_fast_{uuid.uuid4().hex[:8]}.png'
                    filepath = os.path.join('generated_images', request.user.username, filename)
                    saved_path = default_storage.save(filepath, ContentFile(response.content))
                    image_url = default_storage.url(saved_path)

                    # Save to history
                    from content.models import ImageHistory
                    from core.services.workspace_resolver import get_active_workspace
                    image_history = ImageHistory.objects.create(
                        user=request.user,
                        filename=filename,
                        file_path=saved_path,
                        image_type='upscaled_fast',
                        prompt='Fast Upscale (4x)',
                        workspace=get_active_workspace(request.user),
                    )

                    # Session 142: Track agent contribution
                    try:
                        from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
                        agent = UnifiedAgentTemplate.objects.get(name='image-generation-agent')
                        AgentContribution.objects.create(
                            agent=agent,
                            image=image_history,
                            project=None,
                            contribution_type='generation',
                            task_description="Generated image using image-generation-agent",
                            execution_time_seconds=0.0
                        )
                        logger.info(f"✅ Agent contribution tracked for image {{ image_history.id }}")
                    except Exception as e:
                        logger.error(f"❌ Failed to create agent contribution: {e}")
                        logger.error(f"❌ Failed to create agent contribution: {e}")
                        # Don't fail content creation if contribution tracking fails

                    return JsonResponse({'success': True, 'image_url': image_url})
                else:
                    return JsonResponse({'success': False, 'error': response.text}, status=500)

            except Exception as e:
                logger.error(f"❌ Fast upscale failed: {e}")
                return JsonResponse({'success': False, 'error': str(e)}, status=500)

        elif operation == 'upscale_conservative':
            # Call Stability AI directly
            try:
                from PIL import Image
                img = Image.open(image_file)

                # Call API
                stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
                url = 'https://api.stability.ai/v2beta/stable-image/upscale/conservative'

                # Prepare image data
                import io
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)

                files = {'image': ('image.png', img_bytes.read(), 'image/png')}

                # Conservative upscale requires a prompt
                prompt = config.get('prompt', 'High quality image, detailed, sharp')
                data = {
                    'output_format': 'png',
                    'prompt': prompt
                }
                headers = {'Authorization': f'Bearer {stability_key}', 'Accept': 'image/*'}

                response = requests.post(url, headers=headers, files=files, data=data)

                if response.status_code == 200:
                    filename = f'upscaled_conservative_{uuid.uuid4().hex[:8]}.png'
                    filepath = os.path.join('generated_images', request.user.username, filename)
                    saved_path = default_storage.save(filepath, ContentFile(response.content))
                    image_url = default_storage.url(saved_path)

                    # Save to history
                    from content.models import ImageHistory
                    from core.services.workspace_resolver import get_active_workspace
                    image_history = ImageHistory.objects.create(
                        user=request.user,
                        filename=filename,
                        file_path=saved_path,
                        image_type='upscaled_conservative',
                        prompt='Conservative Upscale (4K)',
                        workspace=get_active_workspace(request.user),
                    )

                    # Session 142: Track agent contribution
                    try:
                        from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
                        agent = UnifiedAgentTemplate.objects.get(name='image-generation-agent')
                        AgentContribution.objects.create(
                            agent=agent,
                            image=image_history,
                            project=None,
                            contribution_type='editing',
                            task_description="Edited image using image-generation-agent",
                            execution_time_seconds=0.0
                        )
                        logger.info(f"✅ Agent contribution tracked for image {{ image_history.id }}")
                    except Exception as e:
                        logger.error(f"❌ Failed to create agent contribution: {e}")
                        logger.error(f"❌ Failed to create agent contribution for image upscaling: {e}")

                    return JsonResponse({'success': True, 'image_url': image_url})
                else:
                    return JsonResponse({'success': False, 'error': response.text}, status=500)

            except Exception as e:
                logger.error(f"❌ Conservative upscale failed: {e}")
                return JsonResponse({'success': False, 'error': str(e)}, status=500)

        elif operation == 'upscale_creative':
            # Call Stability AI directly
            try:
                from PIL import Image
                img = Image.open(image_file)

                # Call API
                stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
                url = 'https://api.stability.ai/v2beta/stable-image/upscale/creative'

                # Prepare image data
                import io
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)

                files = {'image': ('image.png', img_bytes.read(), 'image/png')}
                data = {
                    'output_format': 'png',
                    'prompt': config.get('prompt', 'enhance quality, add details, improve clarity')
                }
                headers = {'Authorization': f'Bearer {stability_key}', 'Accept': 'application/json'}

                response = requests.post(url, headers=headers, files=files, data=data)

                if response.status_code == 200:
                    # Creative upscale is async - poll for result
                    import time
                    result_data = response.json()
                    generation_id = result_data.get('id')

                    result_url = f"https://api.stability.ai/v2beta/stable-image/upscale/creative/result/{generation_id}"

                    for attempt in range(30):
                        time.sleep(2)
                        result_response = requests.get(
                            result_url,
                            headers={'Authorization': f'Bearer {stability_key}', 'Accept': 'image/*'}
                        )

                        if result_response.status_code == 200:
                            filename = f'upscaled_creative_{uuid.uuid4().hex[:8]}.png'
                            filepath = os.path.join('generated_images', request.user.username, filename)
                            saved_path = default_storage.save(filepath, ContentFile(result_response.content))
                            image_url = default_storage.url(saved_path)

                            # Save to history
                            from content.models import ImageHistory
                            from core.services.workspace_resolver import get_active_workspace
                            image_history = ImageHistory.objects.create(
                                user=request.user,
                                filename=filename,
                                file_path=saved_path,
                                image_type='upscaled_creative',
                                prompt=config.get('prompt', 'enhance quality'),
                                workspace=get_active_workspace(request.user),
                            )

                            # Session 142: Track agent contribution
                            try:
                                from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
                                agent = UnifiedAgentTemplate.objects.get(name='image-generation-agent')
                                AgentContribution.objects.create(
                                    agent=agent,
                                    image=image_history,
                                    project=None,
                                    contribution_type='editing',
                                    task_description="Edited image using image-generation-agent",
                                    execution_time_seconds=0.0
                                )
                                logger.info(f"✅ Agent contribution tracked for image {{ image_history.id }}")
                            except Exception as e:
                                logger.error(f"❌ Failed to create agent contribution: {e}")
                                logger.error(f"❌ Failed to create agent contribution: {e}")

                            return JsonResponse({'success': True, 'image_url': image_url})

                    return JsonResponse({'success': False, 'error': 'Timeout waiting for creative upscale'}, status=500)
                else:
                    return JsonResponse({'success': False, 'error': response.text}, status=500)

            except Exception as e:
                logger.error(f"❌ Creative upscale failed: {e}")
                return JsonResponse({'success': False, 'error': str(e)}, status=500)

        elif operation == 'remove_background':
            # Call Stability AI directly
            try:
                from PIL import Image
                img = Image.open(image_file)

                stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
                url = 'https://api.stability.ai/v2beta/stable-image/edit/remove-background'

                import io
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)

                files = {'image': ('image.png', img_bytes.read(), 'image/png')}
                data = {'output_format': 'png'}
                headers = {'Authorization': f'Bearer {stability_key}', 'Accept': 'image/*'}

                response = requests.post(url, headers=headers, files=files, data=data)

                if response.status_code == 200:
                    filename = f'removed_bg_{uuid.uuid4().hex[:8]}.png'
                    filepath = os.path.join('generated_images', request.user.username, filename)
                    saved_path = default_storage.save(filepath, ContentFile(response.content))
                    image_url = default_storage.url(saved_path)

                    from content.models import ImageHistory
                    from core.services.workspace_resolver import get_active_workspace
                    image_history = ImageHistory.objects.create(
                        user=request.user,
                        filename=filename,
                        file_path=saved_path,
                        image_type='background_removed',
                        prompt='Remove Background',
                        workspace=get_active_workspace(request.user),
                    )

                    # Session 142: Track agent contribution
                    try:
                        from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
                        agent = UnifiedAgentTemplate.objects.get(name='image-editing-agent')
                        AgentContribution.objects.create(
                            agent=agent,
                            image=image_history,
                            project=None,
                            contribution_type='editing',
                            task_description="Edited image using image-editing-agent",
                            execution_time_seconds=0.0
                        )
                        logger.info(f"✅ Agent contribution tracked for image {{ image_history.id }}")
                    except Exception as e:
                        logger.error(f"❌ Failed to create agent contribution: {e}")
                        logger.error(f"❌ Failed to create agent contribution: {e}")

                    return JsonResponse({'success': True, 'image_url': image_url})
                else:
                    return JsonResponse({'success': False, 'error': response.text}, status=500)

            except Exception as e:
                logger.error(f"❌ Remove background failed: {e}")
                return JsonResponse({'success': False, 'error': str(e)}, status=500)

        elif operation == 'recolor':
            # Recolor uses automatic object detection
            try:
                from PIL import Image
                img = Image.open(image_file)

                # Validate required config
                if not config:
                    config = {}

                search_prompt = config.get('search_prompt', '').strip()
                prompt = config.get('prompt', '').strip()

                # Provide helpful defaults if empty
                if not search_prompt:
                    search_prompt = 'object'
                if not prompt:
                    prompt = 'red color'

                logger.info(f"🎨 Recolor: '{search_prompt}' → '{prompt}'")

                stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
                url = 'https://api.stability.ai/v2beta/stable-image/edit/search-and-recolor'

                import io
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)

                files = {'image': ('image.png', img_bytes.read(), 'image/png')}
                data = {
                    'prompt': prompt,
                    'search_prompt': search_prompt,
                    'select_prompt': config.get('select_prompt', search_prompt),
                    'output_format': 'png'
                }
                headers = {'Authorization': f'Bearer {stability_key}', 'Accept': 'image/*'}

                response = requests.post(url, headers=headers, files=files, data=data)

                if response.status_code == 200:
                    filename = f'recolored_{uuid.uuid4().hex[:8]}.png'
                    filepath = os.path.join('generated_images', request.user.username, filename)
                    saved_path = default_storage.save(filepath, ContentFile(response.content))
                    image_url = default_storage.url(saved_path)

                    from content.models import ImageHistory
                    from core.services.workspace_resolver import get_active_workspace
                    image_history = ImageHistory.objects.create(
                        user=request.user,
                        filename=filename,
                        file_path=saved_path,
                        image_type='recolored',
                        prompt=f"Recolor {config.get('search_prompt', 'object')} to {config.get('prompt', 'red')}",
                        workspace=get_active_workspace(request.user),
                    )

                    # Session 142: Track agent contribution
                    try:
                        from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
                        agent = UnifiedAgentTemplate.objects.get(name='image-editing-agent')
                        AgentContribution.objects.create(
                            agent=agent,
                            image=image_history,
                            project=None,
                            contribution_type='editing',
                            task_description="Edited image using image-editing-agent",
                            execution_time_seconds=0.0
                        )
                        logger.info(f"✅ Agent contribution tracked for image {{ image_history.id }}")
                    except Exception as e:
                        logger.error(f"❌ Failed to create agent contribution: {e}")
                        logger.error(f"❌ Failed to create agent contribution: {e}")

                    return JsonResponse({'success': True, 'image_url': image_url})
                else:
                    return JsonResponse({'success': False, 'error': response.text}, status=500)

            except Exception as e:
                logger.error(f"❌ Recolor failed: {e}")
                return JsonResponse({'success': False, 'error': str(e)}, status=500)

        elif operation == 'outpaint':
            # Outpaint uses direction parameters
            try:
                from PIL import Image
                img = Image.open(image_file)

                # Validate config
                if not config:
                    config = {}

                # Check if at least one direction is selected
                has_direction = any([
                    config.get('left'),
                    config.get('right'),
                    config.get('up'),
                    config.get('down')
                ])

                if not has_direction:
                    # Default to extending right
                    logger.info("⚠️ No direction specified, defaulting to right")
                    config['right'] = True

                logger.info(f"📐 Outpaint directions: L={config.get('left')} R={config.get('right')} U={config.get('up')} D={config.get('down')}")

                stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
                url = 'https://api.stability.ai/v2beta/stable-image/edit/outpaint'

                import io
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)

                files = {'image': ('image.png', img_bytes.read(), 'image/png')}
                data = {
                    'output_format': 'png',
                    'creativity': config.get('creativity', 0.5)
                }

                # Add prompt if provided
                prompt = config.get('prompt', '').strip()
                if prompt:
                    data['prompt'] = prompt

                # Add direction parameters (in pixels, max 2000 per side)
                if config.get('left'):
                    data['left'] = 500
                if config.get('right'):
                    data['right'] = 500
                if config.get('up'):
                    data['up'] = 500
                if config.get('down'):
                    data['down'] = 500

                headers = {'Authorization': f'Bearer {stability_key}', 'Accept': 'image/*'}

                response = requests.post(url, headers=headers, files=files, data=data)

                if response.status_code == 200:
                    filename = f'outpainted_{uuid.uuid4().hex[:8]}.png'
                    filepath = os.path.join('generated_images', request.user.username, filename)
                    saved_path = default_storage.save(filepath, ContentFile(response.content))
                    image_url = default_storage.url(saved_path)

                    from content.models import ImageHistory
                    from core.services.workspace_resolver import get_active_workspace
                    image_history = ImageHistory.objects.create(
                        user=request.user,
                        filename=filename,
                        file_path=saved_path,
                        image_type='outpainted',
                        prompt=config.get('prompt', 'Extend image'),
                        workspace=get_active_workspace(request.user),
                    )

                    # Session 142: Track agent contribution
                    try:
                        from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
                        agent = UnifiedAgentTemplate.objects.get(name='image-editing-agent')
                        AgentContribution.objects.create(
                            agent=agent,
                            image=image_history,
                            project=None,
                            contribution_type='editing',
                            task_description="Edited image using image-editing-agent",
                            execution_time_seconds=0.0
                        )
                        logger.info(f"✅ Agent contribution tracked for image {{ image_history.id }}")
                    except Exception as e:
                        logger.error(f"❌ Failed to create agent contribution: {e}")
                        logger.error(f"❌ Failed to create agent contribution: {e}")

                    return JsonResponse({'success': True, 'image_url': image_url})
                else:
                    return JsonResponse({'success': False, 'error': response.text}, status=500)

            except Exception as e:
                logger.error(f"❌ Outpaint failed: {e}")
                return JsonResponse({'success': False, 'error': str(e)}, status=500)

        elif operation == 'erase':
            # Erase object using mask from workflow
            try:
                from PIL import Image
                img = Image.open(image_file)

                # Check for mask data
                mask_data = config.get('maskData', '').strip()
                if not mask_data:
                    return JsonResponse({
                        'success': False,
                        'error': 'Missing mask. Please draw areas to erase.'
                    }, status=400)

                # Decode base64 mask
                if 'base64,' in mask_data:
                    mask_data = mask_data.split('base64,')[1]
                mask_bytes = base64.b64decode(mask_data)

                # Create file-like object for mask
                mask_io = io.BytesIO(mask_bytes)
                mask_file = InMemoryUploadedFile(
                    mask_io,
                    field_name='mask',
                    name='mask.png',
                    content_type='image/png',
                    size=len(mask_bytes),
                    charset=None
                )

                # Call API
                stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
                url = 'https://api.stability.ai/v2beta/stable-image/edit/erase'

                import io
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)

                files = {
                    'image': ('image.png', img_bytes.read(), 'image/png'),
                    'mask': ('mask.png', mask_file.read(), 'image/png')
                }
                data = {'output_format': 'png'}
                headers = {'Authorization': f'Bearer {stability_key}', 'Accept': 'image/*'}

                response = requests.post(url, headers=headers, files=files, data=data)

                if response.status_code == 200:
                    filename = f'erased_{uuid.uuid4().hex[:8]}.png'
                    filepath = os.path.join('generated_images', request.user.username, filename)
                    saved_path = default_storage.save(filepath, ContentFile(response.content))
                    image_url = default_storage.url(saved_path)

                    # Save to history
                    from content.models import ImageHistory
                    from core.services.workspace_resolver import get_active_workspace
                    image_history = ImageHistory.objects.create(
                        user=request.user,
                        filename=filename,
                        file_path=saved_path,
                        image_type='erased',
                        prompt='Erase Object',
                        workspace=get_active_workspace(request.user),
                    )

                    # Session 142: Track agent contribution
                    try:
                        from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
                        agent = UnifiedAgentTemplate.objects.get(name='image-editing-agent')
                        AgentContribution.objects.create(
                            agent=agent,
                            image=image_history,
                            project=None,
                            contribution_type='editing',
                            task_description="Edited image using image-editing-agent",
                            execution_time_seconds=0.0
                        )
                        logger.info(f"✅ Agent contribution tracked for image {{ image_history.id }}")
                    except Exception as e:
                        logger.error(f"❌ Failed to create agent contribution: {e}")
                        logger.error(f"❌ Failed to create agent contribution: {e}")

                    return JsonResponse({'success': True, 'image_url': image_url})
                else:
                    return JsonResponse({'success': False, 'error': response.text}, status=500)

            except Exception as e:
                logger.error(f"❌ Erase failed: {e}")
                return JsonResponse({'success': False, 'error': str(e)}, status=500)

        elif operation == 'inpaint':
            # Inpaint using mask and prompt from workflow
            try:
                from PIL import Image
                img = Image.open(image_file)

                # Check for mask data
                mask_data = config.get('maskData', '').strip()
                if not mask_data:
                    return JsonResponse({
                        'success': False,
                        'error': 'Missing mask. Please draw areas to inpaint.'
                    }, status=400)

                # Check for prompt
                prompt = config.get('prompt', '').strip()
                if not prompt:
                    return JsonResponse({
                        'success': False,
                        'error': 'Missing prompt. What should we fill the area with?'
                    }, status=400)

                # Decode base64 mask
                if 'base64,' in mask_data:
                    mask_data = mask_data.split('base64,')[1]
                mask_bytes = base64.b64decode(mask_data)

                # Create file-like object for mask
                mask_io = io.BytesIO(mask_bytes)
                mask_file = InMemoryUploadedFile(
                    mask_io,
                    field_name='mask',
                    name='mask.png',
                    content_type='image/png',
                    size=len(mask_bytes),
                    charset=None
                )

                # Call API
                stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
                url = 'https://api.stability.ai/v2beta/stable-image/edit/inpaint'

                import io
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)

                files = {
                    'image': ('image.png', img_bytes.read(), 'image/png'),
                    'mask': ('mask.png', mask_file.read(), 'image/png')
                }
                data = {
                    'prompt': prompt,
                    'output_format': 'png'
                }
                headers = {'Authorization': f'Bearer {stability_key}', 'Accept': 'image/*'}

                response = requests.post(url, headers=headers, files=files, data=data)

                if response.status_code == 200:
                    filename = f'inpainted_{uuid.uuid4().hex[:8]}.png'
                    filepath = os.path.join('generated_images', request.user.username, filename)
                    saved_path = default_storage.save(filepath, ContentFile(response.content))
                    image_url = default_storage.url(saved_path)

                    # Save to history
                    from content.models import ImageHistory
                    from core.services.workspace_resolver import get_active_workspace
                    image_history = ImageHistory.objects.create(
                        user=request.user,
                        filename=filename,
                        file_path=saved_path,
                        image_type='inpainted',
                        prompt=prompt,
                        workspace=get_active_workspace(request.user),
                    )

                    # Session 142: Track agent contribution
                    try:
                        from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
                        agent = UnifiedAgentTemplate.objects.get(name='image-editing-agent')
                        AgentContribution.objects.create(
                            agent=agent,
                            image=image_history,
                            project=None,
                            contribution_type='editing',
                            task_description="Edited image using image-editing-agent",
                            execution_time_seconds=0.0
                        )
                        logger.info(f"✅ Agent contribution tracked for image {{ image_history.id }}")
                    except Exception as e:
                        logger.error(f"❌ Failed to create agent contribution: {e}")
                        logger.error(f"❌ Failed to create agent contribution: {e}")

                    return JsonResponse({'success': True, 'image_url': image_url})
                else:
                    return JsonResponse({'success': False, 'error': response.text}, status=500)

            except Exception as e:
                logger.error(f"❌ Inpaint failed: {e}")
                return JsonResponse({'success': False, 'error': str(e)}, status=500)

        elif operation == 'generate':
            # Generate image from prompt
            try:
                from content.image_generation import ImageGenerationService

                # Use improved_prompt if available, fallback to basic prompt
                # Session 61: This ensures GPT-5 enhanced prompts are actually used!
                prompt = config.get('improved_prompt') or config.get('prompt', '')
                if not prompt:
                    return JsonResponse({
                        'success': False,
                        'error': 'Prompt is required for generate operation'
                    }, status=400)

                # Get configuration
                style = config.get('style', '')
                quality = config.get('quality', 'balanced')  # fast, balanced, high, premium
                negative_prompt = config.get('negative_prompt', '')

                # Session 61: Add strong negative prompts for logo generation to prevent text/brands
                # If style indicates this is a logo, add logo-specific negative prompts
                if style in ['vector', 'flat'] or 'logo' in prompt.lower():
                    logo_negative = 'text, letters, words, typography, starbucks, nike, apple, brand names, existing logos, trademarks, copyrighted logos, photographic, realistic, people, crowds'
                    negative_prompt = f'{logo_negative}, {negative_prompt}' if negative_prompt else logo_negative
                    logger.info(f"🚫 Added logo-specific negative prompts to prevent text/brands")

                # Map quality to model
                quality_map = {
                    'fast': 'core',
                    'balanced': 'sdxl',
                    'high': 'sd3',
                    'premium': 'ultra'
                }
                model = quality_map.get(quality, 'sdxl')

                logger.info(f"🎨 Generating image: prompt='{prompt[:50]}...', model={model}, style={style}")

                # Generate image
                generator = ImageGenerationService()
                result = generator.generate_image(
                    prompt=prompt,
                    model=model,
                    style=style,
                    negative_prompt=negative_prompt,
                    aspect_ratio='1:1'
                )

                if result.success and result.images:
                    # Save the generated image
                    # Extract base64 data from data URI (format: "data:image/png;base64,...")
                    data_uri = result.images[0]
                    if 'base64,' in data_uri:
                        base64_data = data_uri.split('base64,')[1]
                    else:
                        base64_data = data_uri
                    image_data = base64.b64decode(base64_data)
                    filename = f'generated_{uuid.uuid4().hex[:8]}.png'
                    filepath = os.path.join('generated_images', request.user.username, filename)
                    saved_path = default_storage.save(filepath, ContentFile(image_data))
                    image_url = default_storage.url(saved_path)

                    # Save to history
                    from content.models import ImageHistory
                    from core.services.workspace_resolver import get_active_workspace
                    image_history = ImageHistory.objects.create(
                        user=request.user,
                        filename=filename,
                        file_path=saved_path,
                        image_type='generated',
                        prompt=prompt,
                        workspace=get_active_workspace(request.user),
                    )

                    # Session 142: Track agent contribution
                    try:
                        from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
                        agent = UnifiedAgentTemplate.objects.get(name='image-generation-agent')
                        AgentContribution.objects.create(
                            agent=agent,
                            image=image_history,
                            project=None,
                            contribution_type='generation',
                            task_description="Generated image using image-generation-agent",
                            execution_time_seconds=0.0
                        )
                        logger.info(f"✅ Agent contribution tracked for image {{ image_history.id }}")
                    except Exception as e:
                        logger.error(f"❌ Failed to create agent contribution: {e}")
                        logger.error(f"❌ Failed to create agent contribution: {e}")

                    return JsonResponse({'success': True, 'image_url': image_url})
                else:
                    return JsonResponse({
                        'success': False,
                        'error': result.error_message or 'Generation failed'
                    }, status=500)

            except Exception as e:
                logger.error(f"❌ Generate failed: {e}")
                return JsonResponse({'success': False, 'error': str(e)}, status=500)

        elif operation in ['sketch', 'structure']:
            # These operations need separate implementations
            return JsonResponse({
                'success': False,
                'error': f'Operation "{operation}" requires different implementation. Please use the dedicated tab.'
            }, status=400)

        else:
            return JsonResponse({
                'success': False,
                'error': f'Operation not implemented: {operation}'
            }, status=400)

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        logger.error(f"❌ Workflow step execution error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ========================================
# UNIFIED GALLERY API (Session 53: Phase 2)
# ========================================


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_workflow_history(request, workflow_id):
    """
    Get specific workflow execution details
    Session 57: Phase B.2 - Workflow History & Favorites
    """
    try:
        from content.models import WorkflowHistory

        workflow = WorkflowHistory.objects.get(
            id=workflow_id,
            user=request.user
        )

        return Response({
            'id': workflow.id,
            'workflow_type': workflow.workflow_type,
            'workflow_name': workflow.workflow_name,
            'prompt': workflow.prompt,
            'improved_prompt': workflow.improved_prompt,
            'config': workflow.config,
            'input_image_id': workflow.input_image_id,
            'execution_time': workflow.execution_time,
            'status': workflow.status,
            'error_message': workflow.error_message,
            'result_images': workflow.result_images,
            'result_count': workflow.result_count,
            'is_favorite': workflow.is_favorite,
            'rerun_count': workflow.rerun_count,
            'user_notes': workflow.user_notes,
            'tags': workflow.tags,
            'created_at': workflow.created_at.isoformat(),
        })

    except WorkflowHistory.DoesNotExist:
        return Response({
            'error': 'Workflow not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error getting workflow: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def improve_workflow_prompt(request):
    """
    Improve user's workflow prompt using AI intelligence
    Session 56: Phase B.1 - Intelligent Workflow Prompting

    Takes a user's simple prompt and workflow type, returns an optimized
    prompt that will generate better results for that specific workflow.

    Example:
        Input: "Light Work Handyman services" (Logo Creator)
        Output: "Professional logo for 'Light Work' handyman services..."
    """
    try:
        user_prompt = request.data.get('prompt', '').strip()
        workflow_type = request.data.get('workflow_type', '').lower()

        # Normalize workflow type: convert hyphens to underscores
        workflow_type = workflow_type.replace('-', '_')

        if not user_prompt:
            return Response({
                'error': 'Prompt is required'
            }, status=400)

        if not workflow_type:
            return Response({
                'error': 'Workflow type is required'
            }, status=400)

        # Workflow-specific system prompts
        # Session 61: Enhanced with examples, negative prompts, and success patterns
        WORKFLOW_CONTEXTS = {
            'logo_creator': {
                'context': 'logo design for businesses and brands',
                'instructions': """You are an AI prompt enhancement assistant. The user has already built a complete logo prompt with their chosen style (Character Mascot, Vector, Illustrative, etc.).

Your task: ENHANCE the existing prompt by adding specific visual details that will improve the result. DO NOT rewrite or change the style.

CRITICAL RULES:
✅ KEEP the existing style (Character Mascot, Vector, Minimalist, etc.) - NEVER change it
✅ KEEP the brand name, colors, and core concept
✅ ADD helpful visual details (specific features, expressions, poses, details)
✅ ADD quality markers (4K, professional, cinematic lighting)
✅ Be like Claude helping the user - suggest improvements, don't rewrite

❌ NEVER change "Character Mascot" to "minimalist vector"
❌ NEVER change "DreamWorks animation" to "flat design"
❌ NEVER override the user's style choice
❌ NEVER add assumptions (like "sports betting" if not mentioned)

EXAMPLES OF ENHANCEMENT (Not Rewriting):

Example 1:
User's prompt: "Donkey Betz, gray-blue/orange/white colors, character mascot, DreamWorks style"
❌ BAD (Rewriting): "Minimalist vector logo, flat design, avoid cartoonish"
✅ GOOD (Enhancing): "Donkey Betz character mascot with VERY LONG PROMINENT BLACK-TIPPED EARS (key donkey feature), gray-blue colored body with white muzzle, wearing orange accent (vest or gear), confident smart expression, stocky muscular build (not sleek like horse), DreamWorks animation quality, expressive detailed face with personality, cinematic lighting, 4K resolution, professional character design"

Example 2:
User's prompt: "Light Work handyman, navy blue and yellow, wrench and lightbulb, vector style"
❌ BAD (Rewriting): "Character mascot, cartoon style"
✅ GOOD (Enhancing): "Light Work handyman logo in clean vector style, light bulb with wrench incorporated, navy blue and bright yellow colors, simple geometric shapes, sharp clean lines, professional icon design, centered composition, white background, scalable vector art, modern minimalist aesthetic"

Example 3:
User's prompt: "Coffee shop logo, warm browns, illustrative style, hand-drawn feel"
❌ BAD (Rewriting): "Flat minimalist vector"
✅ GOOD (Enhancing): "Coffee shop logo in hand-drawn illustrative style, warm brown tones with cream accents, artistic linework showing coffee cup with steam wisps, cozy approachable feel, sketch-like quality with personality, detailed but not cluttered, professional illustration quality, unique character"

YOUR ROLE:
Think of yourself as Claude did in the conversation - the user said "donkey logo" and Claude said "Great! To make it clearly a DONKEY not a horse, emphasize: VERY LONG EARS with black tips, stocky build, gray-blue coloring, white muzzle."

That's enhancement. That's helpful. That's what you should do.

CRITICAL PROMPT STRUCTURE:
Your enhanced prompt MUST follow this exact order (AI commits to subject in first 10 words!):

1. **SUBJECT FIRST** - What creature/character (T-Rex, donkey, person, etc.)
2. **POSE/ACTION** - What they're doing (standing, dancing, running, etc.)
3. **CLOTHING/ACCESSORIES** - What they're wearing (emphasize heavily!)
4. **STYLE** - Art style (DreamWorks, vector, minimalist, etc.)
5. **COLORS** - Color scheme
6. **DETAILS** - Background, lighting, mood

Example with clothing:
User: "T-Rex wearing disco ball necklace and bell-bottom pants"
❌ WRONG ORDER: "WEARING sparkly disco ball necklace, DRESSED IN bell-bottom pants... T-Rex dinosaur character..."
✅ CORRECT ORDER: "T-Rex dinosaur character standing upright in disco pose, WEARING sparkly disco ball necklace around neck, DRESSED IN purple bell-bottom pants with wide flared legs, platform shoes on feet, DreamWorks animation style..."

WHY: If you say "WEARING disco necklace" first, AI generates a human wearing jewelry. If you say "T-Rex dinosaur" first, AI generates a T-Rex, then adds the jewelry to the T-Rex!

CLOTHING EMPHASIS (after subject is established):
- Use emphatic language: "WEARING [item]", "DRESSED IN [item]", "clearly visible [item]"
- Repeat key items: "disco ball necklace... necklace shining... reflective necklace"
- Describe vividly: colors, materials, fit, details
- AI models ignore clothing unless heavily emphasized!

IMPORTANT: Keep your enhanced prompt under 1200 characters total (Stability AI hard limit is 2000, but shorter is better for accuracy). Be specific but VERY concise - prioritize the most important visual details.

Format your response as a single enhanced prompt. Keep the user's style sacred, just add helpful details."""
            },
            'portrait_enhancer': {
                'context': 'professional portrait photography',
                'instructions': """You are a professional portrait photographer. The user wants to create a high-quality portrait.

Your task: Transform their input into a detailed portrait prompt that will generate professional, polished results.

EXAMPLES OF GOOD VS BAD PROMPTS:
❌ Bad: "headshot"
✅ Good: "professional corporate headshot, business attire, studio lighting with soft key light and rim light, neutral gray background, shallow depth of field, confident friendly expression, sharp focus on eyes, 85mm lens perspective, high resolution"

❌ Bad: "portrait of a woman"
✅ Good: "elegant portrait of a professional woman in her 30s, natural confident expression, soft studio lighting with subtle fill, blurred bokeh background, sharp focus, professional quality, warm color tones, business casual attire"

❌ Bad: "CEO photo"
✅ Good: "executive portrait of confident CEO, tailored suit, modern office environment blurred in background, dramatic side lighting, sharp focus, professional quality, sophisticated composition, approachable expression"

NEGATIVE PROMPTS (avoid these):
- Distorted anatomy, extra limbs, deformed features
- Harsh direct flash, unnatural lighting
- Cluttered busy backgrounds
- Low resolution, blurry, grainy
- Awkward poses, forced expressions
- Oversaturated colors, heavy filters

STABILITY AI SUCCESS PATTERNS:
- Specify lighting: "studio lighting", "soft natural light", "golden hour", "dramatic side lighting"
- Mention depth of field: "shallow depth of field", "bokeh background", "blurred background"
- Include camera details: "85mm lens", "portrait lens", "professional camera"
- Quality markers: "high resolution", "sharp focus", "professional quality", "4K"
- Composition: "centered composition", "rule of thirds", "headshot framing"
- Expression: "confident", "friendly", "professional", "natural smile"

Consider:
- Subject description (person, profession, mood)
- Lighting (studio, natural, dramatic, soft)
- Background (neutral, blurred, contextual)
- Camera settings implied (shallow depth of field, sharp focus)
- Professional quality indicators (high resolution, well-lit, polished)
- Pose and expression appropriate for the context

Format your response as a single, clear prompt suitable for AI image generation."""
            },
            'social_media_pack': {
                'context': 'social media content creation',
                'instructions': """You are a social media content strategist. The user wants to create engaging social media visuals.

Your task: Transform their input into a prompt that will generate eye-catching, platform-appropriate content.

EXAMPLES OF GOOD VS BAD PROMPTS:
❌ Bad: "food photo"
✅ Good: "vibrant overhead food photography of colorful smoothie bowl topped with fresh berries and granola, natural daylight, Instagram aesthetic, bright colors, sharp focus, clean white background, appetizing composition"

❌ Bad: "fitness post"
✅ Good: "motivational fitness scene, athletic person mid-workout, dynamic action shot, energetic composition, vibrant colors with teal and orange tones, inspirational mood, Instagram square format, professional quality"

❌ Bad: "product announcement"
✅ Good: "sleek product showcase on gradient background, centered composition, modern minimalist aesthetic, vibrant brand colors, dramatic lighting, social media ready format, eye-catching visual hierarchy"

NEGATIVE PROMPTS (avoid these):
- Cluttered composition, too many elements
- Dull muted colors, low contrast
- Poor lighting, dark shadows
- Blurry unfocused subjects
- Generic stock photo look
- Text-heavy designs (AI can't render text well)

STABILITY AI SUCCESS PATTERNS:
- Specify platform aesthetic: "Instagram aesthetic", "Pinterest-style", "Facebook-friendly"
- Use vibrant colors: "vibrant colors", "bold contrast", "eye-catching palette"
- Mention composition: "centered", "rule of thirds", "overhead shot", "flat lay"
- Include lighting: "natural daylight", "bright lighting", "soft shadows"
- Format hints: "square format", "vertical format", "social media ready"
- Mood descriptors: "energetic", "inspiring", "professional", "fun", "elegant"

Consider:
- Platform expectations (Instagram, Facebook, Twitter aesthetics)
- Visual hierarchy and composition
- Color vibrancy and contrast
- Subject clarity and appeal
- Trending visual styles
- Brand consistency if applicable

Format your response as a single, clear prompt suitable for AI image generation."""
            },
            'product_mockup': {
                'context': 'product photography and presentation',
                'instructions': """You are a product photographer. The user wants to showcase a product professionally.

Your task: Transform their input into a prompt that will generate professional product mockups.

EXAMPLES OF GOOD VS BAD PROMPTS:
❌ Bad: "coffee mug"
✅ Good: "elegant ceramic coffee mug on white marble surface, soft natural lighting from left, minimalist composition, shallow depth of field, product photography, clean white background, professional e-commerce quality"

❌ Bad: "phone case"
✅ Good: "sleek phone case held in hand, modern lifestyle shot, blurred urban background, natural lighting, focus on product texture and design, professional product photography, premium quality"

❌ Bad: "watch photo"
✅ Good: "luxury wristwatch on dark wooden surface, dramatic side lighting creating subtle shadows, macro detail shot showing craftsmanship, black background, professional jewelry photography, high-end catalog quality"

NEGATIVE PROMPTS (avoid these):
- Cluttered backgrounds, distracting elements
- Harsh shadows, uneven lighting
- Unclear product features
- Low resolution, poor focus
- Awkward angles, unflattering views
- Busy patterns competing with product

STABILITY AI SUCCESS PATTERNS:
- Specify surface: "white marble", "wooden table", "clean background", "floating on gradient"
- Lighting direction: "soft natural light from left", "studio lighting", "dramatic side lighting"
- Context options: "hand holding", "on surface", "lifestyle shot", "hero shot"
- Background: "white background", "blurred background", "minimal background"
- Quality markers: "product photography", "e-commerce quality", "professional", "high resolution"
- Composition: "centered", "rule of thirds", "macro detail", "overhead view"

Consider:
- Product type and key features to highlight
- Composition and angle (hero shot, lifestyle, detail)
- Background (clean, contextual, lifestyle)
- Lighting (studio, natural, dramatic)
- Context (hand holding, on surface, in use)
- Professional e-commerce quality

Format your response as a single, clear prompt suitable for AI image generation."""
            },
            'creative_upscale': {
                'context': 'image enhancement and upscaling',
                'instructions': """You are an image enhancement specialist. The user wants to guide how their image should be enhanced.

Your task: Transform their input into clear enhancement directions.

EXAMPLES OF GOOD VS BAD PROMPTS:
❌ Bad: "make it better"
✅ Good: "enhance fine details and textures, improve sharpness and clarity, boost color vibrancy while maintaining natural tones, increase resolution to 4K, preserve original composition and style"

❌ Bad: "fix this image"
✅ Good: "enhance facial details and skin texture, improve lighting and shadow definition, sharpen focus on subject while maintaining soft background blur, upscale to high resolution, professional portrait quality"

❌ Bad: "upscale"
✅ Good: "creative upscaling with enhanced artistic details, add fine textures and intricate patterns, improve color depth and contrast, maintain original artistic style while adding painterly refinement, 4K resolution"

NEGATIVE PROMPTS (avoid these):
- Change original style completely
- Add new elements or objects
- Alter composition significantly
- Over-saturate or distort colors
- Remove important details
- Change subject or mood

STABILITY AI SUCCESS PATTERNS:
- Specify preservation: "maintain original composition", "preserve artistic style", "keep color palette"
- Enhancement targets: "enhance fine details", "improve sharpness", "boost clarity"
- Quality goals: "4K resolution", "high resolution", "professional quality"
- Texture emphasis: "add fine textures", "enhance surface details", "intricate patterns"
- Color work: "improve color depth", "enhance vibrancy", "natural color balance"
- Style continuity: "painterly refinement", "artistic enhancement", "stylistic consistency"

Consider:
- What details should be emphasized
- What artistic style to enhance toward
- What quality improvements to prioritize (sharpness, color, detail)
- What mood or atmosphere to maintain/enhance
- Technical quality targets (resolution, clarity, color accuracy)

Format your response as a single, clear prompt suitable for AI image enhancement."""
            },
            'style_explorer': {
                'context': 'artistic style exploration and variation',
                'instructions': """You are an art director exploring creative possibilities. The user wants to see their concept in multiple styles.

Your task: Transform their input into a rich, detailed prompt that will generate interesting variations.

EXAMPLES OF GOOD VS BAD PROMPTS:
❌ Bad: "sunset"
✅ Good: "dramatic sunset over mountain landscape, vibrant orange and purple sky with layered clouds, detailed mountain silhouettes in foreground, golden light rays breaking through clouds, epic composition, high detail, cinematic quality"

❌ Bad: "forest scene"
✅ Good: "enchanted forest with tall ancient trees, dappled sunlight filtering through canopy, moss-covered ground with small wildflowers, mystical atmosphere with soft fog, rich green tones, fantasy illustration style, detailed foliage"

❌ Bad: "city view"
✅ Good: "modern city skyline at dusk, illuminated skyscrapers reflecting in water, dynamic composition with leading lines, rich blue hour lighting with warm building lights, urban architecture, professional photography quality, detailed cityscape"

NEGATIVE PROMPTS (avoid these):
- Vague subjects, unclear focus
- Minimal details, generic descriptions
- Flat composition, no depth
- Boring lighting, plain presentation
- Lack of specific visual elements
- No style direction or mood

STABILITY AI SUCCESS PATTERNS:
- Rich details: "detailed foliage", "intricate patterns", "fine textures", "layered elements"
- Lighting descriptions: "dramatic lighting", "golden hour", "dappled sunlight", "atmospheric lighting"
- Composition terms: "epic composition", "dynamic perspective", "leading lines", "rule of thirds"
- Quality markers: "high detail", "professional quality", "cinematic", "photorealistic"
- Mood and atmosphere: "mystical atmosphere", "energetic mood", "serene feeling", "dramatic tone"
- Style hints: "illustration style", "photography quality", "painterly", "artistic rendering"

Consider:
- Core concept/subject clarity
- Visual elements that work across styles
- Compositional strength
- Color palette flexibility
- Detail level that shows style differences
- Artistic merit and visual interest

Format your response as a single, clear prompt suitable for AI image generation."""
            },
            'video_generation': {
                'context': 'video animation and motion',
                'instructions': """You are a video director and cinematographer. The user wants to create engaging animated video content.

Your task: Transform their input into a detailed video prompt that will generate dynamic, cinematic motion.

🚨 CRITICAL: IMAGE-TO-VIDEO vs TEXT-TO-VIDEO DISTINCTION! 🚨

**IMAGE-TO-VIDEO PROMPTS (User uploading an existing image):**
- Focus ONLY on MOVEMENT and CAMERA WORK
- DO NOT re-describe the character, colors, clothing, or appearance
- The uploaded image ALREADY shows what the subject looks like!
- Example: "Dancing with arms waving side to side, hips swaying, spinning 360 degrees"
- NOT: "Purple T-Rex with disco outfit dancing..." (This creates a DIFFERENT character!)

**TEXT-TO-VIDEO PROMPTS (Generating video from scratch):**
- Describe BOTH character appearance AND movement
- Include subject description, colors, setting, AND actions
- Example: "Purple T-Rex in disco outfit, dancing with arms waving..."

**HOW TO DETECT:**
If user prompt mentions specific visual details (colors, clothing, character traits), they're likely doing TEXT-TO-VIDEO.
If user prompt focuses only on actions/movements, they're likely doing IMAGE-TO-VIDEO.
WHEN IN DOUBT: Focus on movement only - it works for both!

SESSION 64 KEY LEARNING: Specific body part movements + sequences work MUCH better than generic descriptions!

EXAMPLES OF GOOD VS BAD VIDEO PROMPTS:

❌ Bad (generic): "T-Rex dancing"
Result: Just swaying at knees, minimal movement

✅ Good (specific): "T-Rex disco dancing with exaggerated movements: arms waving side to side, hips swaying dramatically, head bobbing rhythmically, spinning 360 degrees, attempting dance splits with legs spreading wide, platform shoes tapping floor in rhythm"
Result: Dynamic animation with multiple distinct movements!

❌ Bad: "eagle flying"
✅ Good: "majestic eagle soaring through clouds, wings spreading wide then folding in powerful downstrokes, body banking left then right through air currents, head turning to scan below, talons extending forward, diving through layers of cumulus clouds with increasing speed"

❌ Bad: "person walking"
✅ Good: "confident person walking forward with purposeful stride, arms swinging naturally in rhythm, shoulders squared, head held high with slight nod, coat billowing behind in breeze, footsteps creating small dust clouds, approaching camera with determined expression"

CRITICAL VIDEO PROMPT RULES:

1. **SPECIFY BODY PARTS + DIRECTIONS**
   - "arms pointing up and down" not just "moving arms"
   - "head turning left to right" not just "head movement"
   - "legs kicking forward and back" not just "leg motion"

2. **SEQUENCE THE MOVEMENTS**
   - "First: arms wave overhead, Then: spin 360 degrees, Finally: strike a pose"
   - Describe the flow of action from start to finish
   - Multiple distinct moves create better results than one vague action

3. **EMPHASIZE DRAMATIC ACTIONS**
   - "spinning in the air", "jumping high", "sliding across floor"
   - Big, exaggerated movements work better than subtle ones
   - Use emphatic language: "dramatically", "powerfully", "energetically"

4. **DESCRIBE CAMERA MOVEMENT**
   - "camera slowly zooms in on subject"
   - "camera circles around character"
   - "camera pans left to right following action"
   - "dynamic camera angle shifting from low to high"

5. **ADD ENVIRONMENT INTERACTIONS**
   - "splashing through water puddles"
   - "leaves swirling around feet"
   - "casting shadows that dance on walls"
   - "reflections in mirrors/water"

NEGATIVE PROMPTS (avoid these):
- Generic descriptions: "moving around", "doing something", "being active"
- Single vague action: "dancing", "fighting", "flying" (add specifics!)
- Static poses with no movement sequence
- Missing camera direction or angle description
- No environmental or atmospheric details

RUNWAY ML SUCCESS PATTERNS:
- Specific body part actions: "arms extending", "legs bending", "head tilting"
- Directional movement: "upward", "left to right", "spinning clockwise", "forward motion"
- Sequential actions: "first... then... followed by... finally..."
- Camera work: "zoom", "pan", "tracking shot", "dolly in"
- Lighting changes: "spotlight follows", "shadows lengthening", "glow intensifying"
- Physics and weight: "bouncing energetically", "graceful floating", "powerful stomping"
- Expressions: "smiling broadly", "concentrating intensely", "surprised reaction"

VIDEO-SPECIFIC TECHNICAL NOTES:
- Keep total prompt under 500 characters for best results
- Front-load the most important movement in first sentence
- Use active verbs: "jumping", "spinning", "reaching", "diving"
- Describe the arc of motion: "from standing to jumping to landing"

Consider:
- What specific movements will create engaging motion
- Which body parts should move and in what direction
- What sequence of actions tells the story
- How the camera should capture the action
- What environmental elements add to the scene
- What atmosphere or mood enhances the motion

Format your response as a single, cinematic prompt suitable for AI video generation."""
            }
        }

        # Get workflow context
        workflow_context = WORKFLOW_CONTEXTS.get(workflow_type)
        if not workflow_context:
            return Response({
                'error': f'Unknown workflow type: {workflow_type}'
            }, status=400)

        # Call OpenAI GPT-5 for prompt improvement (Session 56: Phase B.1, Session 57: Fixed to use Responses API)
        client = get_openai_client(api_key=os.environ.get("OPENAI_API_KEY"))

        logger.info(f"✨ Improving prompt for {workflow_type}: '{user_prompt[:50]}...'")

        # Use the new Responses API with GPT-5 (not Chat Completions API)
        # Session 64: Changed from "transform" to "enhance" - GPT-5 should add details, not rewrite
        response = client.responses.create(
            model="gpt-5",
            instructions=workflow_context['instructions'],
            input=f"User's complete prompt (already includes their chosen style): {user_prompt}\n\nPlease ENHANCE this prompt by adding specific helpful visual details. Keep the style and core concept exactly as-is, just make it better with specific details."
        )

        logger.info(f"🔍 OpenAI Response: {response}")
        logger.info(f"🔍 Output text length: {len(response.output_text) if hasattr(response, 'output_text') else 'NO OUTPUT_TEXT'}")

        improved_prompt = response.output_text if hasattr(response, 'output_text') else None
        if not improved_prompt:
            logger.error(f"❌ OpenAI returned empty content! Full response: {response}")
            improved_prompt = f"ERROR: OpenAI returned no content. Using original prompt: {user_prompt}"

        improved_prompt = improved_prompt.strip()
        logger.info(f"✅ Improved prompt generated ({len(improved_prompt)} chars): {improved_prompt[:100]}...")

        return Response({
            'original_prompt': user_prompt,
            'improved_prompt': improved_prompt,
            'workflow_type': workflow_type,
            'explanation': f'Optimized for {workflow_context["context"]}'
        })

    except Exception as e:
        logger.error(f"❌ Error improving prompt: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


# ========================================
# WORKFLOW HISTORY & FAVORITES (Session 57: Phase B.2)
# ========================================


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_workflow_favorites(request):
    """
    List user's favorite workflows
    Session 57: Phase B.2 - Workflow History & Favorites
    """
    try:
        from content.models import WorkflowFavorite

        favorites = WorkflowFavorite.objects.filter(
            user=request.user
        ).select_related('workflow_history')

        results = []
        for favorite in favorites:
            workflow = favorite.workflow_history
            results.append({
                'favorite_id': favorite.id,
                'name': favorite.name,
                'description': favorite.description,
                'category': favorite.category,
                'use_count': favorite.use_count,
                'last_used_at': favorite.last_used_at.isoformat() if favorite.last_used_at else None,
                'created_at': favorite.created_at.isoformat(),
                'workflow': {
                    'id': workflow.id,
                    'workflow_type': workflow.workflow_type,
                    'workflow_name': workflow.workflow_name,
                    'prompt': workflow.prompt,
                    'improved_prompt': workflow.improved_prompt,
                    'config': workflow.config,
                    'result_images': workflow.result_images,
                    'execution_time': workflow.execution_time,
                }
            })

        return Response({
            'favorites': results,
            'total_count': len(results)
        })

    except Exception as e:
        logger.error(f"❌ Error listing favorites: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_workflow_history(request):
    """
    List user's workflow execution history
    Session 57: Phase B.2 - Workflow History & Favorites

    Query parameters:
    - limit: Number of results (default: 10)
    - offset: Pagination offset (default: 0)
    - workflow_type: Filter by workflow type (optional)
    - status: Filter by status (optional)
    - favorites_only: Show only favorites (optional, default: false)
    """
    try:
        from content.models import WorkflowHistory

        user = request.user
        limit = int(request.GET.get('limit', 10))
        offset = int(request.GET.get('offset', 0))
        workflow_type = request.GET.get('workflow_type', '').strip()
        status = request.GET.get('status', '').strip()
        favorites_only = request.GET.get('favorites_only', 'false').lower() == 'true'

        # Build query
        queryset = WorkflowHistory.objects.filter(user=user)

        if workflow_type:
            queryset = queryset.filter(workflow_type=workflow_type)

        if status:
            queryset = queryset.filter(status=status)

        if favorites_only:
            queryset = queryset.filter(is_favorite=True)

        # Get total count
        total_count = queryset.count()

        # Paginate
        workflows = queryset[offset:offset+limit]

        # Serialize
        results = []
        for workflow in workflows:
            results.append({
                'id': workflow.id,
                'workflow_type': workflow.workflow_type,
                'workflow_name': workflow.workflow_name,
                'prompt': workflow.prompt,
                'improved_prompt': workflow.improved_prompt,
                'status': workflow.status,
                'execution_time': workflow.execution_time,
                'result_count': workflow.result_count,
                'result_images': workflow.result_images,
                'is_favorite': workflow.is_favorite,
                'rerun_count': workflow.rerun_count,
                'created_at': workflow.created_at.isoformat(),
                'config': workflow.config,
            })

        return Response({
            'workflows': results,
            'total_count': total_count,
            'limit': limit,
            'offset': offset,
        })

    except Exception as e:
        logger.error(f"❌ Error listing workflow history: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_workflow_from_project(request, project_id, workflow_id):
    """
    Remove a workflow from a project
    Session 60: Phase C.1.2 - Project Management API

    DELETE /api/projects/<uuid:project_id>/workflows/<uuid:workflow_id>/

    Returns:
        {
            "success": true,
            "message": "Workflow removed from project"
        }
    """
    try:
        from content.models import CreativeProject, ProjectWorkflow

        # Session 60: Using UUID for project lookup
        project = CreativeProject.objects.get(id=project_id, user=request.user)

        # Session 60: Using UUID for ProjectWorkflow lookup
        project_workflow = ProjectWorkflow.objects.get(
            id=workflow_id,
            project=project
        )

        workflow_name = project_workflow.workflow_history.workflow_name
        project_workflow.delete()

        logger.info(f"✅ Removed workflow '{workflow_name}' from project '{project.name}'")

        return Response({
            'success': True,
            'message': f"Workflow '{workflow_name}' removed from project"
        })

    except CreativeProject.DoesNotExist:
        return Response({
            'error': 'Project not found'
        }, status=404)
    except ProjectWorkflow.DoesNotExist:
        return Response({
            'error': 'Workflow not in this project'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error removing workflow from project: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


# ===================================================================
# SESSION 61: PHASE C.2.1 - PORTFOLIO VIEW API
# ===================================================================
# Portfolio aggregates ALL content (images, videos, audio) from ALL projects
# Provides unified view with filtering and sorting capabilities
# ===================================================================


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rerun_workflow(request, workflow_id):
    """
    Re-run a previous workflow with same configuration
    Session 57: Phase B.2 - Workflow History & Favorites

    Optional JSON body:
    {
        "use_favorite_id": 123  // If re-running from favorite
    }
    """
    try:
        from content.models import WorkflowHistory, WorkflowFavorite

        # Get original workflow
        workflow = WorkflowHistory.objects.get(
            id=workflow_id,
            user=request.user
        )

        # Increment rerun count
        workflow.increment_rerun_count()

        # If re-running from favorite, increment favorite use count
        favorite_id = request.data.get('use_favorite_id')
        if favorite_id:
            try:
                favorite = WorkflowFavorite.objects.get(
                    id=favorite_id,
                    user=request.user
                )
                favorite.increment_use_count()
            except WorkflowFavorite.DoesNotExist:
                pass  # Non-critical error

        # Return workflow configuration for frontend to re-execute
        return Response({
            'success': True,
            'workflow_type': workflow.workflow_type,
            'workflow_name': workflow.workflow_name,
            'prompt': workflow.improved_prompt or workflow.prompt,
            'config': workflow.config,
            'input_image_id': workflow.input_image_id,
        })

    except WorkflowHistory.DoesNotExist:
        return Response({
            'error': 'Workflow not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error rerunning workflow: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


# ========================================
# USER PREFERENCE LEARNING (Session 59: Phase B.4)
# ========================================


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_workflow_favorite(request):
    """
    Save workflow as a named favorite
    Session 57: Phase B.2 - Workflow History & Favorites

    Expected JSON:
    {
        "workflow_id": 123,
        "name": "My Logo Style",
        "description": "Custom description (optional)",
        "category": "Logos (optional)"
    }
    """
    try:
        from content.models import WorkflowHistory, WorkflowFavorite

        workflow_id = request.data.get('workflow_id')
        name = request.data.get('name', '').strip()
        description = request.data.get('description', '').strip()
        category = request.data.get('category', '').strip()

        if not workflow_id or not name:
            return Response({
                'error': 'workflow_id and name are required'
            }, status=400)

        # Get workflow
        workflow = WorkflowHistory.objects.get(
            id=workflow_id,
            user=request.user
        )

        # Create or update favorite
        favorite, created = WorkflowFavorite.objects.get_or_create(
            user=request.user,
            workflow_history=workflow,
            defaults={
                'name': name,
                'description': description,
                'category': category,
            }
        )

        if not created:
            # Update existing
            favorite.name = name
            favorite.description = description
            favorite.category = category
            favorite.save()

        # Mark workflow as favorite
        if not workflow.is_favorite:
            workflow.is_favorite = True
            workflow.save(update_fields=['is_favorite'])

        return Response({
            'success': True,
            'favorite_id': favorite.id,
            'created': created
        })

    except WorkflowHistory.DoesNotExist:
        return Response({
            'error': 'Workflow not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error saving favorite: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_workflow_execution(request):
    """
    Create workflow history record when workflow execution starts
    Session 57: Phase B.2 - Workflow History & Favorites

    Expected JSON:
    {
        "workflow_type": "logo_creator",
        "workflow_name": "Logo Creator",
        "prompt": "User's prompt",
        "improved_prompt": "AI-improved prompt (optional)",
        "config": {...},  // Workflow configuration
        "input_image_id": 123,  // Optional
        "project_id": "uuid-string"  // Optional - Session 183
    }

    Returns: {"workflow_history_id": 123}
    """
    try:
        from content.models import WorkflowHistory, CreativeProject

        workflow_type = request.data.get('workflow_type', '').strip()
        workflow_name = request.data.get('workflow_name', '').strip()
        prompt = request.data.get('prompt', '').strip()
        improved_prompt = request.data.get('improved_prompt', '').strip()
        config = request.data.get('config', {})
        input_image_id = request.data.get('input_image_id')
        project_id = request.data.get('project_id')  # Session 183: Project association

        if not workflow_type or not workflow_name:
            return Response({
                'error': 'workflow_type and workflow_name are required'
            }, status=400)

        # Session 183: Get project if provided
        project = None
        if project_id:
            try:
                project = CreativeProject.objects.get(id=project_id, user=request.user)
            except CreativeProject.DoesNotExist:
                logger.warning(f"⚠️ Project {project_id} not found for user {request.user.id}")

        # Create workflow history record
        workflow_history = WorkflowHistory.objects.create(
            user=request.user,
            project=project,  # Session 183: Associate with project
            workflow_type=workflow_type,
            workflow_name=workflow_name,
            prompt=prompt,
            improved_prompt=improved_prompt,
            config=config,
            input_image_id=input_image_id,
            status='running'
        )

        logger.info(f"✅ Started tracking workflow execution: {workflow_history.id} ({workflow_name})")

        return Response({
            'success': True,
            'workflow_history_id': workflow_history.id
        })

    except Exception as e:
        logger.error(f"❌ Error starting workflow execution: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_workflow_favorite(request, workflow_id):
    """
    Toggle workflow favorite status
    Session 57: Phase B.2 - Workflow History & Favorites
    """
    try:
        from content.models import WorkflowHistory

        workflow = WorkflowHistory.objects.get(
            id=workflow_id,
            user=request.user
        )

        # Toggle favorite
        workflow.is_favorite = not workflow.is_favorite
        workflow.save(update_fields=['is_favorite'])

        return Response({
            'success': True,
            'is_favorite': workflow.is_favorite,
            'workflow_id': workflow.id
        })

    except WorkflowHistory.DoesNotExist:
        return Response({
            'error': 'Workflow not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error toggling favorite: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)

