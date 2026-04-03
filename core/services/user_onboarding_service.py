"""
User Onboarding Service
========================

Detects first-time users and provides onboarding experience:
- Welcome DM from Rigby
- Pinned "Getting Started" deliverable
- Guided tour suggestions

Auto-triggered on first login or can be called manually.

Usage:
    from core.services.user_onboarding_service import onboard_new_user, is_first_login

    if is_first_login(user):
        onboard_new_user(user)
"""

import logging
from typing import Optional

from django.contrib.auth import get_user_model
from django.utils import timezone

logger = logging.getLogger(__name__)

User = get_user_model()

# Users that should never be onboarded (system accounts)
SKIP_USERNAMES = frozenset([
    'pa-service', 'system', 'system_learning', 'system_autonomous',
])

# The welcome message from Rigby
WELCOME_MESSAGE = """Welcome to Donkey Betz! I'm Rigby, your AI assistant.

Here's how to get started:
1. Head to the **Command Center** (home page) — that's where we chat
2. Try asking me: "Rigby, what can you do?" or "Show me the platform overview"
3. Check out the **Workspace** tab to see active projects
4. Click **Messages** in the sidebar to see team messages

A few things I can help with:
- Research any topic using 80+ data spiders
- Create content (newsletters, blogs, reports)
- Run business workspaces (Newsletter Studio, LeadGen, Research)
- Answer questions about the platform and its capabilities

There's a pinned "Getting Started" guide in the Donkey Betz workspace with more details.

Looking forward to working with you!"""


def is_first_login(user) -> bool:
    """Check if this is a user's first meaningful interaction with the platform."""
    if not user or not user.is_authenticated:
        return False
    if user.username in SKIP_USERNAMES:
        return False
    if user.username.startswith('vip_'):
        return False

    # Check if user has ever received an onboarding DM
    from core.models_messaging import DirectMessage
    has_onboarding = DirectMessage.objects.filter(
        thread__threadparticipant__user=user,
        metadata__onboarding=True,
    ).exists()

    if has_onboarding:
        return False

    # Check if user has any PA conversations (has used the platform before)
    from core.models import ChatConversation
    has_conversations = ChatConversation.objects.filter(user=user).exists()

    # First login = no onboarding DM and no conversations
    return not has_conversations


def onboard_new_user(user, sent_by_user=None) -> dict:
    """
    Send onboarding welcome to a new user.

    Creates a welcome DM from Rigby and returns status.
    sent_by_user: the admin/owner who triggers the onboarding (defaults to first superuser)
    """
    if not user or not user.is_authenticated:
        return {'success': False, 'error': 'Invalid user'}

    if user.username in SKIP_USERNAMES:
        return {'success': False, 'error': 'System account — skip onboarding'}

    from core.models_messaging import MessageThread, ThreadParticipant, DirectMessage

    # Find the sender (platform owner or first superuser)
    if not sent_by_user:
        sent_by_user = User.objects.filter(is_superuser=True).exclude(
            username__in=SKIP_USERNAMES
        ).first()

    if not sent_by_user:
        return {'success': False, 'error': 'No admin user found to send welcome'}

    # Don't send duplicate onboarding
    existing = DirectMessage.objects.filter(
        thread__threadparticipant__user=user,
        metadata__onboarding=True,
    ).exists()
    if existing:
        return {'success': False, 'error': 'User already onboarded'}

    # Create welcome DM thread
    display_name = user.first_name or user.username
    thread = MessageThread.objects.create(
        thread_type='rigby_routed',
        subject=f'Welcome to Donkey Betz, {display_name}!',
        metadata={'routed_by': 'rigby', 'type': 'onboarding'},
    )
    ThreadParticipant.objects.create(thread=thread, user=sent_by_user)
    ThreadParticipant.objects.create(thread=thread, user=user)

    DirectMessage.objects.create(
        thread=thread,
        sender=sent_by_user,
        body=WELCOME_MESSAGE,
        sender_type='rigby',
        metadata={'onboarding': True, 'routed_by': 'rigby'},
    )

    logger.info("Onboarded user %s (thread %s)", user.username, thread.id)

    return {
        'success': True,
        'user': user.username,
        'thread_id': str(thread.id),
        'message': f'Welcome DM sent to {display_name}',
    }


def onboard_to_workspace(user, workspace, role='viewer') -> dict:
    """
    Onboard a user to a specific workspace.

    Sends a workspace-specific welcome with summary of what's been done,
    key deliverables, and their role.
    """
    from core.models_deliverables import Deliverable
    from core.models_messaging import MessageThread, ThreadParticipant, DirectMessage

    # Get workspace deliverable count and recent items
    deliverables = Deliverable.objects.filter(workspace=workspace)
    total = deliverables.count()
    recent = deliverables.order_by('-created_at')[:5]
    recent_titles = [d.title[:60] for d in recent]

    # Get workspace config if it exists
    config = getattr(workspace, 'config', None)
    template_name = config.template.name if config and config.template else 'Custom'

    # Build workspace welcome message
    display_name = user.first_name or user.username
    workspace_msg = f"""You've been added to the **{workspace.name}** workspace!

**Type:** {template_name}
**Your role:** {role.title()}
**Deliverables:** {total} items

"""
    if recent_titles:
        workspace_msg += "**Recent work:**\n"
        for title in recent_titles:
            workspace_msg += f"- {title}\n"
        workspace_msg += "\n"

    workspace_msg += f"""To explore this workspace:
- Say "Rigby, show me the {workspace.name} workspace overview"
- Or navigate to the Workspace tab and click the Dashboard link

As a **{role}**, you can """

    if role == 'owner':
        workspace_msg += "manage everything — pipeline, agents, deliverables, and team members."
    elif role == 'editor':
        workspace_msg += "create and edit deliverables, run the pipeline, and suggest changes."
    elif role == 'reviewer':
        workspace_msg += "review deliverables, suggest changes, and approve/reject items."
    else:
        workspace_msg += "view all deliverables and ask Rigby about the workspace."

    # Find workspace owner to send from
    owner = User.objects.filter(
        project_workspaces=workspace
    ).first() or User.objects.filter(is_superuser=True).first()

    if not owner:
        return {'success': False, 'error': 'No workspace owner found'}

    # Create DM
    thread = MessageThread.objects.create(
        thread_type='rigby_routed',
        subject=f'Welcome to {workspace.name}',
        metadata={'routed_by': 'rigby', 'type': 'workspace_onboarding', 'workspace_id': str(workspace.id)},
    )
    ThreadParticipant.objects.create(thread=thread, user=owner)
    if user.id != owner.id:
        ThreadParticipant.objects.create(thread=thread, user=user)

    DirectMessage.objects.create(
        thread=thread,
        sender=owner,
        body=workspace_msg,
        sender_type='rigby',
        metadata={'onboarding': True, 'workspace_onboarding': True, 'workspace_id': str(workspace.id)},
    )

    logger.info("Onboarded %s to workspace %s (role=%s)", user.username, workspace.name, role)

    return {
        'success': True,
        'user': user.username,
        'workspace': workspace.name,
        'role': role,
        'thread_id': str(thread.id),
    }
