"""
Complete Agent Ecosystem API Endpoints

Session 90 - All 7 agents exposed via REST API

This file provides REST API access to the complete agent ecosystem:
1. CreativeDirectorAgent (in views_creative_director.py)
2. TemplateManagerAgent
3. VersionControlAgent
4. BrandStyleAgent
5. ReferenceLibraryAgent
6. EditingOrchestratorAgent
7. IterationAgent
8. WorkflowCoordinatorAgent (master orchestrator)
"""

import json
import logging

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from ai_core.agents.template_manager_agent import TemplateManagerAgent
from ai_core.agents.version_control_agent import VersionControlAgent
from ai_core.agents.brand_style_agent import BrandStyleAgent
from ai_core.agents.reference_library_agent import ReferenceLibraryAgent
# Session 206: EditingOrchestratorAgent was merged into ImageAgent in Phase 1
# Using ImageAgent as replacement for editing orchestration
from core.agents import ImageAgent as EditingOrchestratorAgent
from ai_core.agents.iteration_agent import IterationAgent
from ai_core.agents.workflow_coordinator_agent import WorkflowCoordinatorAgent

logger = logging.getLogger(__name__)


# ========================================
# TEMPLATE MANAGER ENDPOINTS
# ========================================

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def save_as_template(request) -> JsonResponse:
    """
    Save image as reusable template.

    POST /api/agents/templates/save/
    Body: {"image_id": 123, "template_name": "Alpine Coffee Logo", "tags": ["logo", "coffee"], "notes": "Perfect!"}
    """
    try:
        data = json.loads(request.body)
        agent = TemplateManagerAgent(user=request.user)

        result = agent.save_as_template(
            image_id=data.get('image_id'),
            template_name=data.get('template_name'),
            tags=data.get('tags', []),
            notes=data.get('notes', '')
        )

        return JsonResponse(result)

    except Exception as e:
        logger.error(f"Save template error: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def generate_from_template(request) -> JsonResponse:
    """
    Generate new content from template.

    POST /api/agents/templates/generate/
    Body: {"template_id": "template_abc123", "prompt_override": "...", "variation_seed_offset": 0}
    """
    try:
        data = json.loads(request.body)
        agent = TemplateManagerAgent(user=request.user)

        result = agent.generate_from_template(
            template_id=data.get('template_id'),
            prompt_override=data.get('prompt_override'),
            variation_seed_offset=data.get('variation_seed_offset', 0)
        )

        return JsonResponse(result)

    except Exception as e:
        logger.error(f"Generate from template error: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def list_templates(request) -> JsonResponse:
    """
    List all templates.

    GET /api/agents/templates/?tags=logo,coffee
    """
    try:
        tags = request.GET.get('tags', '').split(',') if request.GET.get('tags') else None
        agent = TemplateManagerAgent(user=request.user)

        templates = agent.list_templates(tags=tags)

        return JsonResponse({
            'success': True,
            'templates': templates,
            'count': len(templates)
        })

    except Exception as e:
        logger.error(f"List templates error: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_template(request, template_id: str) -> JsonResponse:
    """
    Delete a template.

    DELETE /api/agents/templates/{template_id}/
    """
    try:
        agent = TemplateManagerAgent(user=request.user)
        result = agent.delete_template(template_id)

        return JsonResponse(result)

    except Exception as e:
        logger.error(f"Delete template error: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ========================================
# VERSION CONTROL ENDPOINTS
# ========================================

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def track_generation(request) -> JsonResponse:
    """
    Track generation in version control.

    POST /api/agents/versions/track/
    Body: {"image_id": 123, "parent_version_id": "version_abc", "project_id": "proj_123"}
    """
    try:
        data = json.loads(request.body)
        agent = VersionControlAgent(user=request.user)

        result = agent.track_generation(
            image_id=data.get('image_id'),
            parent_version_id=data.get('parent_version_id'),
            project_id=data.get('project_id')
        )

        return JsonResponse(result)

    except Exception as e:
        logger.error(f"Track generation error: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def rate_version(request) -> JsonResponse:
    """
    Rate a version.

    POST /api/agents/versions/rate/
    Body: {"version_id": "version_abc", "rating": 5, "notes": "Perfect!"}
    """
    try:
        data = json.loads(request.body)
        agent = VersionControlAgent(user=request.user)

        result = agent.rate_version(
            version_id=data.get('version_id'),
            rating=data.get('rating'),
            notes=data.get('notes', '')
        )

        return JsonResponse(result)

    except Exception as e:
        logger.error(f"Rate version error: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def list_versions(request) -> JsonResponse:
    """
    List versions.

    GET /api/agents/versions/?project_id=proj_123&min_rating=5&limit=50
    """
    try:
        agent = VersionControlAgent(user=request.user)

        project_id = request.GET.get('project_id')
        min_rating = int(request.GET.get('min_rating')) if request.GET.get('min_rating') else None
        limit = int(request.GET.get('limit', 50))

        versions = agent.list_versions(
            project_id=project_id,
            min_rating=min_rating,
            limit=limit
        )

        return JsonResponse({
            'success': True,
            'versions': versions,
            'count': len(versions)
        })

    except Exception as e:
        logger.error(f"List versions error: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def get_perfect_versions(request) -> JsonResponse:
    """
    Get all 5-star versions.

    GET /api/agents/versions/perfect/
    """
    try:
        agent = VersionControlAgent(user=request.user)
        versions = agent.get_perfect_versions()

        return JsonResponse({
            'success': True,
            'versions': versions,
            'count': len(versions)
        })

    except Exception as e:
        logger.error(f"Get perfect versions error: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ========================================
# BRAND STYLE ENDPOINTS
# ========================================

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def create_brand_style(request) -> JsonResponse:
    """
    Create brand style.

    POST /api/agents/brand-styles/create/
    Body: {"brand_name": "Alpine Coffee", "image_ids": [1,2,3,4,5], "trigger_word": "ALPINE_BRAND", "description": "..."}
    """
    try:
        data = json.loads(request.body)
        agent = BrandStyleAgent(user=request.user)

        result = agent.create_brand_style(
            brand_name=data.get('brand_name'),
            image_ids=data.get('image_ids', []),
            trigger_word=data.get('trigger_word'),
            description=data.get('description', '')
        )

        return JsonResponse(result)

    except Exception as e:
        logger.error(f"Create brand style error: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def submit_brand_training(request) -> JsonResponse:
    """
    Submit brand style for training.

    POST /api/agents/brand-styles/{character_id}/train/
    """
    try:
        data = json.loads(request.body)
        agent = BrandStyleAgent(user=request.user)

        result = agent.submit_training(
            character_id=data.get('character_id')
        )

        return JsonResponse(result)

    except Exception as e:
        logger.error(f"Submit brand training error: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def check_brand_training_status(request, character_id: int) -> JsonResponse:
    """
    Check brand training status.

    GET /api/agents/brand-styles/{character_id}/status/
    """
    try:
        agent = BrandStyleAgent(user=request.user)
        result = agent.check_training_status(character_id)

        return JsonResponse(result)

    except Exception as e:
        logger.error(f"Check training status error: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def list_brand_styles(request) -> JsonResponse:
    """
    List brand styles.

    GET /api/agents/brand-styles/?include_training=true
    """
    try:
        agent = BrandStyleAgent(user=request.user)
        include_training = request.GET.get('include_training', 'false').lower() == 'true'

        styles = agent.list_brand_styles(include_training=include_training)

        return JsonResponse({
            'success': True,
            'brand_styles': styles,
            'count': len(styles)
        })

    except Exception as e:
        logger.error(f"List brand styles error: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ========================================
# REFERENCE LIBRARY ENDPOINTS
# ========================================

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def add_reference(request) -> JsonResponse:
    """
    Add reference to library.

    POST /api/agents/references/add/
    Body: {"name": "Logo Style", "image_id": 123, "tags": ["logo"], "notes": "..."}
    """
    try:
        data = json.loads(request.body)
        agent = ReferenceLibraryAgent(user=request.user)

        result = agent.add_reference(
            name=data.get('name'),
            image_id=data.get('image_id'),
            tags=data.get('tags', []),
            notes=data.get('notes', '')
        )

        return JsonResponse(result)

    except Exception as e:
        logger.error(f"Add reference error: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def list_references(request) -> JsonResponse:
    """
    List references.

    GET /api/agents/references/?tags=logo,coffee
    """
    try:
        tags = request.GET.get('tags', '').split(',') if request.GET.get('tags') else None
        agent = ReferenceLibraryAgent(user=request.user)

        references = agent.list_references(tags=tags)

        return JsonResponse({
            'success': True,
            'references': references,
            'count': len(references)
        })

    except Exception as e:
        logger.error(f"List references error: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_reference(request, reference_id: str) -> JsonResponse:
    """
    Delete reference.

    DELETE /api/agents/references/{reference_id}/
    """
    try:
        agent = ReferenceLibraryAgent(user=request.user)
        result = agent.delete_reference(reference_id)

        return JsonResponse(result)

    except Exception as e:
        logger.error(f"Delete reference error: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ========================================
# EDITING ORCHESTRATOR ENDPOINTS
# ========================================

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def execute_single_edit(request) -> JsonResponse:
    """
    Execute single editing operation.

    POST /api/agents/editing/execute/
    Body: {"image_id": 123, "operation": "inpaint", "parameters": {...}}
    """
    try:
        data = json.loads(request.body)
        agent = EditingOrchestratorAgent(user=request.user)

        result = agent.execute_single_edit(
            image_id=data.get('image_id'),
            operation=data.get('operation'),
            parameters=data.get('parameters', {})
        )

        return JsonResponse(result)

    except Exception as e:
        logger.error(f"Execute edit error: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def create_editing_workflow(request) -> JsonResponse:
    """
    Create multi-step editing workflow.

    POST /api/agents/editing/workflow/
    Body: {"workflow_name": "...", "source_image_id": 123, "steps": [...]}
    """
    try:
        data = json.loads(request.body)
        agent = EditingOrchestratorAgent(user=request.user)

        result = agent.create_editing_workflow(
            workflow_name=data.get('workflow_name'),
            source_image_id=data.get('source_image_id'),
            steps=data.get('steps', [])
        )

        return JsonResponse(result)

    except Exception as e:
        logger.error(f"Create editing workflow error: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def execute_editing_workflow(request) -> JsonResponse:
    """
    Execute editing workflow.

    POST /api/agents/editing/workflow/execute/
    Body: {"workflow_id": "workflow_abc"}
    """
    try:
        data = json.loads(request.body)
        agent = EditingOrchestratorAgent(user=request.user)

        result = agent.execute_workflow(data.get('workflow_id'))

        return JsonResponse(result)

    except Exception as e:
        logger.error(f"Execute workflow error: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ========================================
# ITERATION AGENT ENDPOINTS
# ========================================

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def refine_image(request) -> JsonResponse:
    """
    Refine image with natural language.

    POST /api/agents/iteration/refine/
    Body: {"image_id": 123, "refinement_request": "Make the text bigger and darker"}
    """
    try:
        data = json.loads(request.body)
        agent = IterationAgent(user=request.user)

        result = agent.refine_image(
            image_id=data.get('image_id'),
            refinement_request=data.get('refinement_request')
        )

        return JsonResponse(result)

    except Exception as e:
        logger.error(f"Refine image error: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ========================================
# WORKFLOW COORDINATOR ENDPOINTS
# ========================================

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def execute_workflow_generate_with_options(request) -> JsonResponse:
    """
    Execute "Generate with Options" workflow.

    POST /api/agents/workflows/generate-with-options/
    Body: {"prompt": "...", "count": 3, "style": "...", "model": "..."}
    """
    try:
        data = json.loads(request.body)
        agent = WorkflowCoordinatorAgent(user=request.user)

        result = agent.execute_generate_with_options_workflow(
            prompt=data.get('prompt'),
            count=data.get('count', 3),
            style=data.get('style'),
            model=data.get('model')
        )

        return JsonResponse(result)

    except Exception as e:
        logger.error(f"Execute generate workflow error: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def execute_workflow_save_as_template(request) -> JsonResponse:
    """
    Execute "Save as Template" workflow.

    POST /api/agents/workflows/save-as-template/
    Body: {"image_id": 123, "template_name": "...", "tags": [...], "also_add_to_references": true}
    """
    try:
        data = json.loads(request.body)
        agent = WorkflowCoordinatorAgent(user=request.user)

        result = agent.execute_save_as_template_workflow(
            image_id=data.get('image_id'),
            template_name=data.get('template_name'),
            tags=data.get('tags', []),
            also_add_to_references=data.get('also_add_to_references', True)
        )

        return JsonResponse(result)

    except Exception as e:
        logger.error(f"Execute save template workflow error: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def execute_workflow_train_brand_style(request) -> JsonResponse:
    """
    Execute "Train Brand Style" workflow.

    POST /api/agents/workflows/train-brand-style/
    Body: {"brand_name": "...", "image_ids": [...], "auto_submit": false}
    """
    try:
        data = json.loads(request.body)
        agent = WorkflowCoordinatorAgent(user=request.user)

        result = agent.execute_train_brand_style_workflow(
            brand_name=data.get('brand_name'),
            image_ids=data.get('image_ids', []),
            auto_submit=data.get('auto_submit', False)
        )

        return JsonResponse(result)

    except Exception as e:
        logger.error(f"Execute brand training workflow error: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def execute_workflow_refine_and_perfect(request) -> JsonResponse:
    """
    Execute "Refine and Perfect" workflow.

    POST /api/agents/workflows/refine-and-perfect/
    Body: {"image_id": 123, "refinement_request": "...", "save_as_template": false, "template_name": "..."}
    """
    try:
        data = json.loads(request.body)
        agent = WorkflowCoordinatorAgent(user=request.user)

        result = agent.execute_refine_and_perfect_workflow(
            image_id=data.get('image_id'),
            refinement_request=data.get('refinement_request'),
            save_as_template=data.get('save_as_template', False),
            template_name=data.get('template_name')
        )

        return JsonResponse(result)

    except Exception as e:
        logger.error(f"Execute refine workflow error: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def get_ecosystem_status(request) -> JsonResponse:
    """
    Get complete ecosystem status.

    GET /api/agents/status/
    """
    try:
        agent = WorkflowCoordinatorAgent(user=request.user)
        status = agent.get_state_summary()

        return JsonResponse({
            'success': True,
            'ecosystem': status
        })

    except Exception as e:
        logger.error(f"Get ecosystem status error: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
