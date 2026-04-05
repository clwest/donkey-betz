"""
Canonical PA Identity — single source of truth for all PA data saves.

Consolidates 6 prior variants:
  PersonalAssistant, PersonalAssistantAgent, UnifiedPA,
  personal_assistant, PA, human_pa

Import and use this constant anywhere the PA saves data:
    from core.services.pa_identity import PA_IDENTITY
"""

PA_IDENTITY = 'PersonalAssistant'

# All historical variants — use for backward-compatible queries
PA_IDENTITY_VARIANTS = frozenset([
    'PersonalAssistant',
    'PersonalAssistantAgent',
    'UnifiedPA',
    'personal_assistant',
    'PA',
    'human_pa',
])
