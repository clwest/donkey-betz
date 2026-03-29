"""
AssistantProfile — per-user PA configuration with role-based tool access.

Each user gets an AssistantProfile that controls:
- Which PA tools they can use (schema filtering)
- Custom system prompt additions
- Workspace scoping
- Role-based defaults

Roles:
- admin: full access to all 85+ tools
- vip_viewer: read-only subset (deliverable_tool, intelligence_tool search)
- customer: TBD (future)
"""

from django.conf import settings
from django.db import models
from django.contrib.postgres.fields import ArrayField

from core.models.base import UnifiedBaseModel


# Default tool sets per role
ROLE_TOOLS = {
    'admin': '__all__',  # Special marker — gets all tools
    'vip_viewer': [
        'deliverable_tool',
        'intelligence_tool',
        'newsletter_tool',
    ],
    'customer': [
        'deliverable_tool',
        'intelligence_tool',
        'newsletter_tool',
        'content_tool',
        'work_tool',
    ],
}

ROLE_CHOICES = [
    ('admin', 'Admin — full tool access'),
    ('vip_viewer', 'VIP Viewer — read-only workspace tools'),
    ('customer', 'Customer — standard tool access'),
]

# Default system prompt additions per role
ROLE_PROMPTS = {
    'admin': '',
    'vip_viewer': (
        'CRITICAL: You are speaking with a VIP demo viewer in a SCOPED workspace. '
        'This person was personally invited by Chris to preview specific deliverables. '
        '\n\nRULES (MUST follow):'
        '\n1. ONLY discuss the deliverables and content in their workspace. Use deliverable_tool to look up what is there.'
        '\n2. Do NOT mention or describe platform features they cannot access.'
        '\n3. Do NOT list navigation options, dashboards, or pages — they only have Home and Library.'
        '\n4. Do NOT discuss internal operations, other users, costs, infrastructure, API keys, or system errors.'
        '\n5. When asked "what can I do here", describe the DELIVERABLES in their workspace and offer to explain any of them in detail.'
        '\n6. If asked about pricing, business terms, or partnerships, say "Chris will follow up with you directly on that."'
        '\n7. Be warm, professional, and concise. You represent Chris and the Donkey Betz brand.'
        '\n8. If they ask about the technology, explain at a high level but do NOT expose specific agent names, counts, or internal architecture.'
    ),
    'customer': (
        'You are assisting a customer on the Donkey Betz platform. '
        'Help them with their workspace deliverables, content, and initiatives. '
        'Do not discuss internal platform operations or other customers.'
    ),
}


class AssistantProfile(UnifiedBaseModel):
    """Per-user PA configuration controlling tool access and behavior."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assistant_profile',
    )

    role = models.CharField(
        max_length=30,
        choices=ROLE_CHOICES,
        default='admin',
        help_text='Controls default tool access and system prompt',
    )

    # Tool access — if empty, falls back to ROLE_TOOLS[role]
    allowed_tools = ArrayField(
        models.CharField(max_length=80),
        default=list,
        blank=True,
        help_text='Explicit tool whitelist. Empty = use role defaults.',
    )

    # Custom system prompt prepended to PA instructions
    system_prompt_override = models.TextField(
        blank=True,
        default='',
        help_text='Custom system prompt added to PA instructions for this user',
    )

    # Workspace scoping — if set, PA only operates in this workspace context
    workspace = models.ForeignKey(
        'core.ProjectWorkspace',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='assistant_profiles',
        help_text='Scope PA to this workspace',
    )

    # Display name for the PA greeting
    display_name = models.CharField(
        max_length=200,
        blank=True,
        default='',
        help_text='Name used in PA greetings (e.g. "Patrick")',
    )

    class Meta:
        app_label = 'core'

    def __str__(self):
        return f"AssistantProfile({self.user.username}, role={self.role})"

    def get_allowed_tools(self):
        """Return the tool whitelist for this user.

        Priority: explicit allowed_tools > role defaults.
        Admin role returns None (meaning all tools).
        """
        if self.allowed_tools:
            return self.allowed_tools

        role_tools = ROLE_TOOLS.get(self.role, ROLE_TOOLS['customer'])
        if role_tools == '__all__':
            return None  # None = no filtering, all tools
        return list(role_tools)

    def get_system_prompt(self):
        """Return the system prompt override for this user.

        Priority: explicit system_prompt_override > role defaults.
        Also injects prospect profile content so the PA knows about the user.
        """
        base = self.system_prompt_override or ROLE_PROMPTS.get(self.role, '')

        # Inject prospect profile so PA knows about this person
        prospect_context = self._load_prospect_context()
        if prospect_context:
            base += f'\n\nABOUT THIS PERSON (use this to personalize your responses):\n{prospect_context}'

        return base

    def _load_prospect_context(self):
        """Load prospect profile content from the linked VIPInvite."""
        try:
            from core.models_vip_invite import VIPInvite
            invite = VIPInvite.objects.filter(
                redeemed_by=self.user,
                prospect_profile__isnull=False,
            ).select_related('prospect_profile').order_by('-redeemed_at').first()
            if invite and invite.prospect_profile:
                content = invite.prospect_profile.content or ''
                # Cap at 2000 chars to keep system prompt reasonable
                return content[:2000] if content else None
        except Exception:
            pass
        return None
