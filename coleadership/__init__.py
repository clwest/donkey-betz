"""
AI-Human Co-Leadership Module - Session 99

This module implements the AI-Human Co-Leadership layer where:
- AI agents can support/raise concerns/oppose decisions
- Humans can override AI recommendations
- We log AI recommendation vs human choice
- We track outcomes later
- We support a playful "I told you so" engine

Philosophy:
- AI and human as EQUAL COLLABORATORS with different roles
- AI is advisory, not authoritative
- Human is ultimate decision-maker
- Both learn from outcomes together

Created: Session 99
"""

default_app_config = 'coleadership.apps.CoLeadershipConfig'
