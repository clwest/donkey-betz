"""
Session Management for Image Views
===================================

Extracted from views_image.py as part of Phase 3 Architecture Improvements (Task 3.2)

Session 186: Created during modular decomposition

Contains:
- get_or_create_session: Get existing or create new AISession
- update_session_transcript: Add message to session transcript
- get_image_by_number: Get image UUID from sequential number
- increment_session_counter: Increment session counters and trigger auto-project
- auto_create_project_from_session: Auto-create project from session
- save_to_history: Save image to ImageHistory database
"""

import os
import logging

from django.core.files.storage import default_storage
from django.utils import timezone
from PIL import Image as PILImage

logger = logging.getLogger(__name__)


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


def _generate_smart_project_name(title):
    """
    Generate a clean, professional project name from a verbose AI prompt.

    Transforms:
    - "Create three cartoon style logos for a mechanic shop" → "Mechanic Shop Logos"
    - "Generate social media posts for coffee brand" → "Coffee Brand Social Media"
    - "Make a modern website design" → "Modern Website Design"

    Algorithm:
    1. Remove common AI prompt prefixes
    2. Extract key subject nouns (last 3-5 important words)
    3. Remove filler words
    4. Title-case result
    5. Limit to 50 characters max
    """
    if not title:
        return "Untitled Project"

    # Step 1: Remove common AI prompt prefixes
    prefixes_to_remove = [
        'create a ', 'create three ', 'create ',
        'make a ', 'make three ', 'make ',
        'generate a ', 'generate three ', 'generate ',
        'design a ', 'design three ', 'design ',
        'build a ', 'build three ', 'build ',
        'draw a ', 'draw ', 'write a ', 'write '
    ]

    title_lower = title.lower()
    for prefix in prefixes_to_remove:
        if title_lower.startswith(prefix):
            title = title[len(prefix):]
            title_lower = title.lower()
            break

    # Step 2: Remove filler words and focus on meaningful content
    filler_words = {
        'a', 'an', 'the', 'some', 'for', 'with', 'about', 'using',
        'in', 'on', 'at', 'by', 'from', 'of', 'to', 'and', 'or', 'but',
        'style', 'styled', 'themed',  # Often redundant in project names
        'called', 'named'  # Session 122: Remove "called/named" from project names
    }

    words = title.split()
    meaningful_words = []
    for word in words:
        # Keep words that are:
        # - Not filler words
        # - OR are important content words (capitalized, numbers, etc.)
        clean_word = word.strip('.,!?;:').lower()
        if clean_word not in filler_words or word[0].isupper() or clean_word.isdigit():
            meaningful_words.append(word.strip('.,!?;:'))

    # Step 3: Smart truncation - keep last 3-5 meaningful words (usually the core subject)
    if len(meaningful_words) > 5:
        # For longer prompts, take last 4-5 words (usually contains the subject)
        meaningful_words = meaningful_words[-5:]
    elif len(meaningful_words) > 3:
        # For medium prompts, keep last 3-4 words
        meaningful_words = meaningful_words[-4:]

    # Step 4: Join and title-case
    project_name = ' '.join(meaningful_words)
    project_name = project_name.title()

    # Step 5: Limit length
    if len(project_name) > 50:
        project_name = project_name[:47] + '...'

    return project_name if project_name else "Untitled Project"


def auto_create_project_from_session(session):
    """
    Automatically create a CreativeProject from an AI session

    Session 96 Weekend Project: Auto-organize content into projects

    Args:
        session: AISession object with meaningful content
    """
    from content.models import CreativeProject, ImageHistory, VideoHistory

    if not session:
        return None

    # Session 117: FIXED - Skip only if has a REAL project (not Quick Starts placeholder)
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
        metadata={'auto_generated': True, 'source': 'ai_session'}
    )

    # Link session to project
    session.project = project
    session.auto_created_project = True
    session.save(update_fields=['project', 'auto_created_project'])

    # Session 97: Link all session content to the newly created project
    # Update all images from this session to belong to the project
    images_updated = ImageHistory.objects.filter(session=session).update(project=project)
    logger.info(f"📸 Linked {images_updated} images to project '{project.name}'")

    # Update all videos from this session to belong to the project
    videos_updated = VideoHistory.objects.filter(session=session).update(project=project)
    logger.info(f"🎬 Linked {videos_updated} videos to project '{project.name}'")

    logger.info(f"✨ Auto-created project '{project.name}' (ID: {project.id}) for session {session.session_id}")
    return project


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
        full_path = default_storage.path(file_path)
        try:
            with PILImage.open(full_path) as img:
                width, height = img.size
        except Exception as e:
            logger.warning(f"Could not read image dimensions: {e}")
            width, height = None, None

        try:
            file_size = os.path.getsize(full_path)
        except Exception as e:
            logger.warning(f"Could not read file size: {e}")
            file_size = None

        # Session 119: BUGFIX - Assign project if session already has one
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

        # Create history record
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
            seed=seed,
            session=session,
            project=image_project,
            workspace=get_active_workspace(user),
        )

        # Session 142: Track agent contribution
        try:
            from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
            agent = UnifiedAgentTemplate.objects.get(name='image-generation-agent')
            AgentContribution.objects.create(
                agent=agent,
                image=history,
                project=image_project,
                contribution_type='generation',
                task_description="Generated image using image-generation-agent",
                execution_time_seconds=0.0
            )
            logger.info(f"✅ Agent contribution tracked for image {history.id}")
        except Exception as e:
            logger.error(f"❌ Failed to create agent contribution: {e}")
            # Don't fail image creation if contribution tracking fails

        logger.info(f"✅ Saved to history: {image_type} - {history.filename} (ID: {history.id})")
        return history

    except Exception as e:
        logger.error(f"❌ Failed to save image history: {e}")
        # Don't fail the request if history save fails
        return None
