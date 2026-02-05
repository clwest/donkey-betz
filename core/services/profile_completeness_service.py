"""
Session 930: Profile Completeness Service

Identifies gaps in user profiles and generates natural language
prompts to help users fill in missing information.
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from django.utils import timezone

logger = logging.getLogger(__name__)


@dataclass
class ProfileGap:
    """Represents a missing profile field"""
    category: str
    field_name: str
    display_name: str
    priority: int  # 1=high, 2=medium, 3=low
    prompt_question: str


class ProfileCompletenessService:
    """
    Session 930: Analyze user profiles for completeness and generate
    prompts to help users fill in missing information.
    """

    # Define required fields by category with their prompts
    PROFILE_FIELDS = {
        'basic': [
            ('display_name', 'Display Name', 1, "What would you like me to call you?"),
            ('occupation', 'Occupation', 2, "What's your current occupation or role?"),
            ('bio', 'Bio', 3, "Can you tell me a bit about yourself?"),
        ],
        'skills': [
            ('skills', 'Skills', 1, "What are your key skills? (e.g., Python, marketing, design)"),
        ],
        'career': [
            ('current_title', 'Job Title', 2, "What's your current job title?"),
            ('years_experience', 'Years of Experience', 2, "How many years of professional experience do you have?"),
            ('desired_salary', 'Salary Expectations', 2, "What's your target salary range?"),
            ('remote_preference', 'Work Location', 2, "Do you prefer remote, hybrid, or on-site work?"),
        ],
        'goals': [
            ('long_term_goals', 'Long-term Goals', 1, "What are your main long-term goals? (career, financial, personal)"),
            ('quarterly_objectives', 'Current Objectives', 2, "What are you trying to accomplish this quarter?"),
        ],
        'preferences': [
            ('communication_style', 'Communication Style', 3, "How do you prefer to communicate? (formal, casual, brief, detailed)"),
            ('risk_tolerance', 'Risk Tolerance', 2, "How would you describe your risk tolerance? (conservative, moderate, aggressive)"),
            ('learning_style', 'Learning Style', 3, "How do you prefer to learn new things? (reading, videos, hands-on)"),
        ],
        'financial': [
            ('investment_goals', 'Investment Goals', 2, "What are your investment goals?"),
        ],
    }

    # Category weights for scoring
    CATEGORY_WEIGHTS = {
        'basic': 0.20,
        'skills': 0.20,
        'career': 0.20,
        'goals': 0.20,
        'preferences': 0.10,
        'financial': 0.10,
    }

    def __init__(self):
        self._cache = {}

    def get_completeness_score(self, user) -> float:
        """
        Calculate profile completeness score (0-1).

        Returns weighted average based on filled fields.
        """
        filled, total = self._count_filled_fields(user)
        if total == 0:
            return 0.0

        # Calculate weighted score by category
        category_scores = {}
        for category, fields in self.PROFILE_FIELDS.items():
            filled_in_cat = sum(1 for f in fields if self._is_field_filled(user, f[0]))
            category_scores[category] = filled_in_cat / len(fields) if fields else 0

        # Apply weights
        weighted_score = sum(
            score * self.CATEGORY_WEIGHTS.get(cat, 0.1)
            for cat, score in category_scores.items()
        )

        return round(weighted_score, 2)

    def get_profile_gaps(self, user) -> Dict[str, List[ProfileGap]]:
        """
        Get all missing profile fields organized by category.

        Returns dict of category -> list of ProfileGap objects.
        """
        gaps = {}

        for category, fields in self.PROFILE_FIELDS.items():
            category_gaps = []
            for field_name, display_name, priority, prompt in fields:
                if not self._is_field_filled(user, field_name):
                    category_gaps.append(ProfileGap(
                        category=category,
                        field_name=field_name,
                        display_name=display_name,
                        priority=priority,
                        prompt_question=prompt,
                    ))
            if category_gaps:
                gaps[category] = category_gaps

        return gaps

    def get_next_question(self, user) -> Optional[ProfileGap]:
        """
        Get the highest priority unfilled field to prompt user about.

        Returns ProfileGap for the most important missing field,
        or None if profile is complete.
        """
        gaps = self.get_profile_gaps(user)
        if not gaps:
            return None

        # Flatten and sort by priority
        all_gaps = []
        for category_gaps in gaps.values():
            all_gaps.extend(category_gaps)

        # Sort by priority (lower number = higher priority)
        all_gaps.sort(key=lambda g: g.priority)

        # Check if we've recently prompted for this field
        recent_prompts = self._get_recent_prompts(user)
        for gap in all_gaps:
            if gap.field_name not in recent_prompts:
                return gap

        # If all have been prompted recently, return highest priority anyway
        return all_gaps[0] if all_gaps else None

    def get_contextual_prompt(self, user, context: str = None) -> Optional[str]:
        """
        Generate a natural language prompt based on context.

        If context is provided (e.g., "user is looking for jobs"),
        prioritize relevant fields.
        """
        gaps = self.get_profile_gaps(user)
        if not gaps:
            return None

        # Context-aware prioritization
        if context:
            context_lower = context.lower()
            if any(w in context_lower for w in ['job', 'career', 'work', 'salary']):
                priority_categories = ['career', 'skills']
            elif any(w in context_lower for w in ['invest', 'money', 'financial', 'stock']):
                priority_categories = ['financial', 'goals']
            elif any(w in context_lower for w in ['learn', 'skill', 'course']):
                priority_categories = ['skills', 'preferences']
            else:
                priority_categories = ['basic', 'goals']

            # Find first gap in priority categories
            for cat in priority_categories:
                if cat in gaps:
                    gap = gaps[cat][0]
                    return self._format_conversational_prompt(gap, context)

        # Default: highest priority gap
        next_gap = self.get_next_question(user)
        if next_gap:
            return self._format_conversational_prompt(next_gap, context)

        return None

    def record_prompt(self, user, field_name: str, prompt_text: str) -> None:
        """Record that we prompted user about a field."""
        from core.models_user_learning import ProfileCompletionPrompt

        ProfileCompletionPrompt.objects.create(
            user=user,
            field_category=self._get_field_category(field_name),
            field_name=field_name,
            prompt_text=prompt_text,
        )

    def record_response(self, user, field_name: str, value: str, completed: bool = True) -> None:
        """Record user's response to a profile prompt."""
        from core.models_user_learning import ProfileCompletionPrompt

        # Update most recent prompt for this field
        prompt = ProfileCompletionPrompt.objects.filter(
            user=user,
            field_name=field_name,
            was_completed=False,
            was_dismissed=False,
        ).order_by('-prompted_at').first()

        if prompt:
            prompt.was_completed = completed
            prompt.was_dismissed = not completed
            prompt.response_value = value
            prompt.responded_at = timezone.now()
            prompt.save()

    def get_completion_stats(self, user) -> Dict:
        """Get detailed completion statistics."""
        gaps = self.get_profile_gaps(user)
        filled, total = self._count_filled_fields(user)

        return {
            'score': self.get_completeness_score(user),
            'filled_fields': filled,
            'total_fields': total,
            'percentage': round(filled / total * 100, 1) if total > 0 else 0,
            'gaps_by_category': {
                cat: [g.field_name for g in gap_list]
                for cat, gap_list in gaps.items()
            },
            'priority_gaps': [
                g.field_name for g in sorted(
                    [gap for gaps in gaps.values() for gap in gaps],
                    key=lambda x: x.priority
                )[:5]
            ],
        }

    # -------------------------------------------------------------------------
    # Private helper methods
    # -------------------------------------------------------------------------

    def _is_field_filled(self, user, field_name: str) -> bool:
        """Check if a profile field has a value."""
        # Check UserProfile
        if hasattr(user, 'profile'):
            val = getattr(user.profile, field_name, None)
            if val and str(val).strip():
                return True

        # Check ExtendedUserProfile
        if hasattr(user, 'extended_profile'):
            val = getattr(user.extended_profile, field_name, None)
            if val and str(val).strip():
                return True

        # Check EnhancedUserProfile
        if hasattr(user, 'enhanced_profile'):
            val = getattr(user.enhanced_profile, field_name, None)
            if val and str(val).strip():
                return True

        # Special handling for JSON fields
        if field_name in ['skills', 'long_term_goals', 'quarterly_objectives']:
            for profile_attr in ['profile', 'extended_profile', 'enhanced_profile']:
                if hasattr(user, profile_attr):
                    profile = getattr(user, profile_attr)
                    val = getattr(profile, field_name, None)
                    if val and isinstance(val, (list, dict)) and len(val) > 0:
                        return True

        return False

    def _count_filled_fields(self, user) -> Tuple[int, int]:
        """Count filled fields vs total fields."""
        total = sum(len(fields) for fields in self.PROFILE_FIELDS.values())
        filled = sum(
            1 for fields in self.PROFILE_FIELDS.values()
            for field in fields
            if self._is_field_filled(user, field[0])
        )
        return filled, total

    def _get_recent_prompts(self, user, days: int = 7) -> set:
        """Get fields we've prompted about recently."""
        from core.models_user_learning import ProfileCompletionPrompt
        from datetime import timedelta

        cutoff = timezone.now() - timedelta(days=days)
        recent = ProfileCompletionPrompt.objects.filter(
            user=user,
            prompted_at__gte=cutoff,
        ).values_list('field_name', flat=True)

        return set(recent)

    def _get_field_category(self, field_name: str) -> str:
        """Get category for a field name."""
        for category, fields in self.PROFILE_FIELDS.items():
            for field in fields:
                if field[0] == field_name:
                    return category
        return 'unknown'

    def _format_conversational_prompt(self, gap: ProfileGap, context: str = None) -> str:
        """Format a gap into a conversational prompt."""
        base = gap.prompt_question

        # Add context-aware framing
        if context:
            context_lower = context.lower()
            if 'job' in context_lower and gap.category == 'career':
                return f"To help with your job search, {base.lower()}"
            elif 'invest' in context_lower and gap.category == 'financial':
                return f"For personalized investment advice, {base.lower()}"

        # Add friendly framing based on category
        frames = {
            'basic': f"I'd like to get to know you better. {base}",
            'skills': f"To better match opportunities to you, {base.lower()}",
            'career': f"For career-related recommendations, {base.lower()}",
            'goals': f"To help you achieve your objectives, {base.lower()}",
            'preferences': f"To personalize your experience, {base.lower()}",
            'financial': f"For financial insights, {base.lower()}",
        }

        return frames.get(gap.category, base)


# Singleton instance
_profile_completeness_service = None


def get_profile_completeness_service() -> ProfileCompletenessService:
    """Get singleton instance of ProfileCompletenessService."""
    global _profile_completeness_service
    if _profile_completeness_service is None:
        _profile_completeness_service = ProfileCompletenessService()
    return _profile_completeness_service
