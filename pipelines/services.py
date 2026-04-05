"""
Creative Pipeline Execution Service

Session 109 - Creative Pipelines v1

Core orchestration logic for running pipeline templates.
"""

import logging
import json
from typing import Dict, List, Optional, Any
from django.conf import settings

from .models import CreativePipelineTemplate, CreativePipelineRun
from content.models import CreativeProject, AISession, ImageHistory
from content.image_generation import ImageGenerationService
from content import minifig_services
from openai import OpenAI

logger = logging.getLogger(__name__)


# ============================================================================
# TEMPLATE MANAGEMENT
# ============================================================================

def get_available_templates(user) -> List[CreativePipelineTemplate]:
    """
    Get list of active pipeline templates.

    For v1, all active templates are available to all users.
    Future: Filter by user permissions/subscription level.
    """
    return list(CreativePipelineTemplate.objects.filter(is_active=True))


# ============================================================================
# PIPELINE EXECUTION
# ============================================================================

def start_pipeline_run(
    user,
    template_slug: str,
    input_payload: Dict[str, Any],
    project_id: Optional[str] = None,
    session_id: Optional[str] = None
) -> CreativePipelineRun:
    """
    Start a new pipeline run.

    Creates the run record and dispatches to Celery for async execution.
    """
    # Validate template exists and is active
    try:
        template = CreativePipelineTemplate.objects.get(
            slug=template_slug,
            is_active=True
        )
    except CreativePipelineTemplate.DoesNotExist:
        raise ValueError(f"Template '{template_slug}' not found or inactive")

    # Validate optional project/session
    project = None
    session = None
    if project_id:
        try:
            project = CreativeProject.objects.get(id=project_id, user=user)
        except CreativeProject.DoesNotExist:
            raise ValueError(f"Project '{project_id}' not found")

    if session_id:
        try:
            session = AISession.objects.get(id=session_id, user=user)
        except AISession.DoesNotExist:
            raise ValueError(f"Session '{session_id}' not found")

    # Calculate total steps from template config
    total_steps = len(template.config.get('steps', []))

    # Create pipeline run
    run = CreativePipelineRun.objects.create(
        user=user,
        template=template,
        project=project,
        session=session,
        status='pending',
        total_steps=total_steps,
        input_payload=input_payload
    )

    run.append_log(f"Pipeline run created: {template.name}")
    run.append_log(f"Input: {json.dumps(input_payload, indent=2)}")

    # Dispatch to Celery for async execution
    from .tasks import run_pipeline_task
    run_pipeline_task.delay(str(run.id))
    run.append_log("Dispatched to background worker for execution")

    return run


def run_pipeline(run_id: str):
    """
    Execute a pipeline run.

    This is the core orchestrator called by Celery tasks.
    """
    try:
        run = CreativePipelineRun.objects.select_related('template', 'user').get(id=run_id)
    except CreativePipelineRun.DoesNotExist:
        logger.error(f"Pipeline run {run_id} not found")
        return

    run.mark_running()
    run.append_log("Starting pipeline execution")

    try:
        # Get template configuration
        template = run.template
        config = template.config
        steps = config.get('steps', [])

        run.append_log(f"Executing {len(steps)} steps...")

        # Execute each step
        for idx, step in enumerate(steps):
            step_num = idx + 1
            run.update_progress(step_num)
            run.append_log(f"\n--- Step {step_num}/{len(steps)}: {step['name']} ---")

            # Execute step based on type
            step_type = step.get('type')
            if step_type == 'gpt_expansion':
                execute_gpt_expansion_step(run, step)
            elif step_type == 'image_generation':
                execute_image_generation_step(run, step)
            elif step_type == 'save_assets':
                execute_save_assets_step(run, step)
            elif step_type == 'gpt_script':
                execute_gpt_script_step(run, step)
            elif step_type == 'video_creation':
                execute_video_creation_step(run, step)
            elif step_type == 'minifig_creation':
                execute_minifig_creation_step(run, step)
            else:
                raise ValueError(f"Unknown step type: {step_type}")

            run.append_log(f"✓ Step {step_num} completed successfully")

        # Mark as completed
        run.mark_completed()
        run.append_log("\n=== Pipeline completed successfully! ===")
        logger.info(f"Pipeline run {run_id} completed successfully")

    except Exception as e:
        error_msg = f"Pipeline failed: {str(e)}"
        logger.error(f"Pipeline run {run_id} failed: {e}", exc_info=True)
        run.mark_failed(error_msg)
        run.append_log(f"\n!!! ERROR: {error_msg}")


# ============================================================================
# STEP EXECUTORS
# ============================================================================

def execute_gpt_expansion_step(run: CreativePipelineRun, step: Dict):
    """
    Execute GPT expansion step: Expand user idea into detailed prompts.
    """
    idea = run.input_payload.get('idea', '')
    if not idea:
        raise ValueError("No 'idea' provided in input payload")

    num_prompts = step.get('params', {}).get('num_prompts', 5)
    # Override with user input if provided
    num_prompts = run.input_payload.get('num_images', num_prompts)

    run.append_log(f"Expanding idea into {num_prompts} detailed prompts...")

    # Call GPT to expand idea
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    system_prompt = (
        f"You are a creative AI assistant helping to generate detailed image prompts. "
        f"The user will provide a creative idea, and you should expand it into "
        f"{num_prompts} distinct, detailed image generation prompts. "
        f"Each prompt should be vivid, specific, and optimized for AI image generation. "
        f"Return ONLY a JSON array of {num_prompts} strings, no other text."
    )

    user_prompt = f"Creative idea: {idea}\n\nGenerate {num_prompts} detailed image prompts:"

    # Session 876: Increased tokens for GPT-5-mini reasoning headroom
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_completion_tokens=4000,
        reasoning_effort="medium",
    )

    # Parse response
    content = response.choices[0].message.content.strip()
    try:
        # Try to parse as JSON array
        prompts = json.loads(content)
        if not isinstance(prompts, list):
            # If it's not a list, split by newlines
            prompts = [p.strip() for p in content.split('\n') if p.strip()]
    except json.JSONDecodeError:
        # Fallback: split by newlines
        prompts = [p.strip() for p in content.split('\n') if p.strip()]

    # Store prompts in output_payload
    output = run.output_payload
    output['prompts'] = prompts[:num_prompts]  # Ensure we don't exceed requested count
    run.output_payload = output
    run.save(update_fields=['output_payload'])

    run.append_log(f"Generated {len(output['prompts'])} prompts:")
    for i, prompt in enumerate(output['prompts'], 1):
        run.append_log(f"  {i}. {prompt[:80]}...")


def execute_image_generation_step(run: CreativePipelineRun, step: Dict):
    """
    Execute image generation step: Generate images from prompts.
    """
    prompts = run.output_payload.get('prompts', [])
    if not prompts:
        raise ValueError("No prompts available for image generation")

    run.append_log(f"Generating {len(prompts)} images...")

    # Get parameters
    params = step.get('params', {})
    aspect_ratio = params.get('aspect_ratio', '1:1')

    # Map aspect ratio to dimensions
    dimension_map = {
        '1:1': (1024, 1024),
        '16:9': (1344, 768),
        '9:16': (768, 1344)
    }
    width, height = dimension_map.get(aspect_ratio, (1024, 1024))

    # Generate each image
    image_service = ImageGenerationService()
    images = []
    for i, prompt in enumerate(prompts, 1):
        run.append_log(f"  Generating image {i}/{len(prompts)}...")

        try:
            # Use ImageGenerationService with Stability AI
            result = image_service.generate_image(
                prompt=prompt,
                provider='stability',
                size=f'{width}x{height}',
                num_images=1
            )

            if result.success and result.images:
                image_url = result.images[0]
                images.append({
                    'url': image_url,
                    'prompt': prompt,
                    'index': i
                })
                run.append_log(f"    ✓ Image {i} generated")
            else:
                run.append_log(f"    ⚠ Image {i} failed: {result.error_message}")

        except Exception as e:
            run.append_log(f"    ⚠ Image {i} failed: {str(e)}")

    # Store images in output_payload
    output = run.output_payload
    output['images'] = images
    run.output_payload = output
    run.save(update_fields=['output_payload'])

    run.append_log(f"Generated {len(images)} images successfully")


def execute_save_assets_step(run: CreativePipelineRun, step: Dict):
    """
    Execute save assets step: Save generated assets to session/project.
    """
    images = run.output_payload.get('images', [])
    if not images:
        run.append_log("No images to save")
        return

    run.append_log(f"Saving {len(images)} images to database...")

    # Create or get session
    session = run.session
    if not session:
        # Create a new session for this pipeline run
        session = AISession.objects.create(
            user=run.user,
            title=f"{run.template.name} - {run.created_at.strftime('%Y-%m-%d %H:%M')}",
            project=run.project
        )
        run.session = session
        run.save(update_fields=['session'])
        run.append_log(f"Created new session: {session.id}")

    # Save each image to ImageHistory
    saved_count = 0
    for img in images:
        try:
            from core.services.workspace_resolver import get_active_workspace
            ImageHistory.objects.create(
                user=run.user,
                file_path=img['url'],
                image_type='pipeline',
                prompt=img.get('prompt', ''),
                parameters={'pipeline_run_id': str(run.id), 'index': img.get('index')},
                session=session,
                workspace=get_active_workspace(run.user),
            )
            saved_count += 1
        except Exception as e:
            run.append_log(f"  ⚠ Failed to save image {img.get('index')}: {str(e)}")

    run.append_log(f"Saved {saved_count}/{len(images)} images to session {session.id}")


def execute_gpt_script_step(run: CreativePipelineRun, step: Dict):
    """
    Execute GPT script generation step: Create script and shot list.
    """
    idea = run.input_payload.get('idea', '')
    if not idea:
        raise ValueError("No 'idea' provided in input payload")

    duration = run.input_payload.get('duration', 30)
    run.append_log(f"Generating {duration}s video script...")

    # Call GPT to create script
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    system_prompt = (
        f"You are a professional video scriptwriter. Create a compelling {duration}-second promo video script "
        f"with a shot list. Return a JSON object with 'script' (the narration text) and 'shots' "
        f"(array of 6-8 visual scene descriptions for keyframes)."
    )

    user_prompt = f"Promo concept: {idea}\n\nCreate a {duration}s video script with shot list:"

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_completion_tokens=800,
        reasoning_effort="medium",
    )

    # Parse response
    content = response.choices[0].message.content.strip()
    try:
        script_data = json.loads(content)
    except json.JSONDecodeError:
        # Fallback: use raw content as script
        script_data = {'script': content, 'shots': []}

    # Store in output_payload
    output = run.output_payload
    output['script'] = script_data.get('script', '')
    output['prompts'] = script_data.get('shots', [])  # Reuse prompts key for shot descriptions
    run.output_payload = output
    run.save(update_fields=['output_payload'])

    run.append_log(f"Generated script ({len(output['script'])} chars)")
    run.append_log(f"Generated {len(output['prompts'])} shot descriptions")


def execute_video_creation_step(run: CreativePipelineRun, step: Dict):
    """
    Execute video creation step: Create video from keyframes.

    For v1: Log placeholder - actual video assembly will be implemented
    when we integrate with render pipeline or video AI endpoints.
    """
    images = run.output_payload.get('images', [])
    if not images:
        raise ValueError("No keyframe images available for video creation")

    run.append_log(f"Creating video from {len(images)} keyframes...")

    # TODO: Implement actual video creation
    # Options:
    # 1. Use Runway ML API to animate keyframes
    # 2. Create RenderJob with session assets
    # 3. Use ffmpeg slideshow (simplest for v1)

    # For v1, just mark as placeholder
    output = run.output_payload
    output['video_url'] = f"placeholder_video_{run.id}.mp4"
    output['video_status'] = 'placeholder'
    run.output_payload = output
    run.save(update_fields=['output_payload'])

    run.append_log("⚠ Video creation is placeholder in v1")
    run.append_log(f"TODO: Implement video assembly from {len(images)} keyframes")


def execute_minifig_creation_step(run: CreativePipelineRun, step: Dict):
    """
    Execute mini-fig creation step: Turn images into 3D printable assets.

    Session 111 - MiniFig Pipeline v1

    For v1: Creates placeholder 3D files immediately with completed status.
    For v2+: TODO - Dispatch to external 3D generation service with async processing.
    """
    # Get parameters from step config and input_payload
    image_asset_ids = run.input_payload.get('image_asset_ids', [])
    style = run.input_payload.get('style', step.get('params', {}).get('style', 'toy'))
    scale = run.input_payload.get('scale', step.get('params', {}).get('scale', 'medium'))

    if not image_asset_ids:
        raise ValueError("No image_asset_ids provided in input_payload")

    if len(image_asset_ids) > 4:
        raise ValueError(f"Maximum 4 images allowed, got {len(image_asset_ids)}")

    run.append_log(f"Creating mini-figs from {len(image_asset_ids)} images...")
    run.append_log(f"Parameters: style={style}, scale={scale}")

    # Call service layer to create MiniFigAssets
    try:
        created_minifigs = minifig_services.create_minifig_asset_from_images(
            user=run.user,
            image_asset_ids=image_asset_ids,
            pipeline_run=run,
            provider='placeholder',  # v1: always placeholder
            style=style,
            scale=scale
        )

        # Store minifig IDs in output_payload
        output = run.output_payload
        output['minifig_asset_ids'] = [str(mf.id) for mf in created_minifigs]
        output['minifig_count'] = len(created_minifigs)
        output['minifigs'] = [
            {
                'id': str(mf.id),
                'title': mf.title,
                'three_d_file': mf.three_d_file,
                'preview_image_url': mf.preview_image_url,
                'status': mf.status,
            }
            for mf in created_minifigs
        ]
        run.output_payload = output
        run.save(update_fields=['output_payload'])

        run.append_log(f"✓ Created {len(created_minifigs)} mini-fig assets:")
        for mf in created_minifigs:
            run.append_log(f"  - {mf.title} ({mf.id})")
            run.append_log(f"    3D File: {mf.three_d_file}")

        # v1 Note
        run.append_log("")
        run.append_log("📦 v1 Note: Using placeholder 3D files")
        run.append_log("TODO v2+: Integrate with real 3D generation service")

    except ValueError as e:
        # Validation errors from service layer
        raise ValueError(f"MiniFig creation failed: {str(e)}")
    except Exception as e:
        # Unexpected errors
        logger.error(f"MiniFig creation error: {e}", exc_info=True)
        raise RuntimeError(f"MiniFig creation failed: {str(e)}")
