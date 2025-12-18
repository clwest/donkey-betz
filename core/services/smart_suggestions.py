"""
Smart Suggestions Service - Session 482

Generates contextual follow-up suggestions based on:
- What action was just performed
- The type of content/output generated
- User's conversation context
- Related capabilities available

Examples:
- After research: "Would you like me to create content based on this?"
- After image: "Would you like variations or turn this into a video?"
- After video: "Would you like to add music or voice narration?"
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Suggestion:
    """A follow-up suggestion."""
    text: str
    action_type: str  # 'create', 'modify', 'research', 'export', etc.
    priority: int  # 1-10, higher is more relevant
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class SmartSuggestionsService:
    """
    Service to generate contextual follow-up suggestions.

    Tracks the last action and provides relevant next steps
    based on the action type and output.
    """

    # Suggestion templates by action type
    SUGGESTION_TEMPLATES = {
        'research': [
            Suggestion(
                text="Would you like me to create content based on this research?",
                action_type='create',
                priority=9,
                metadata={'next_action': 'content_creation'}
            ),
            Suggestion(
                text="Should I generate a visual summary or infographic?",
                action_type='create',
                priority=8,
                metadata={'next_action': 'image_generation'}
            ),
            Suggestion(
                text="Would you like me to dive deeper into any of these topics?",
                action_type='research',
                priority=7,
                metadata={'next_action': 'more_research'}
            ),
            Suggestion(
                text="Should I save this research to a project for future reference?",
                action_type='export',
                priority=6,
                metadata={'next_action': 'save_project'}
            ),
        ],
        'image_generation': [
            Suggestion(
                text="Would you like me to create variations of this image?",
                action_type='modify',
                priority=9,
                metadata={'next_action': 'create_variations'}
            ),
            Suggestion(
                text="Should I upscale this image to higher resolution?",
                action_type='modify',
                priority=8,
                metadata={'next_action': 'upscale'}
            ),
            Suggestion(
                text="Would you like to turn this into a video?",
                action_type='create',
                priority=8,
                metadata={'next_action': 'image_to_video'}
            ),
            Suggestion(
                text="Should I remove the background for use as a logo/sticker?",
                action_type='modify',
                priority=7,
                metadata={'next_action': 'remove_background'}
            ),
            Suggestion(
                text="Would you like more images in different styles?",
                action_type='create',
                priority=6,
                metadata={'next_action': 'more_images'}
            ),
        ],
        'video_generation': [
            Suggestion(
                text="Would you like me to add voice narration to this video?",
                action_type='modify',
                priority=9,
                metadata={'next_action': 'add_voiceover'}
            ),
            Suggestion(
                text="Should I add background music?",
                action_type='modify',
                priority=8,
                metadata={'next_action': 'add_music'}
            ),
            Suggestion(
                text="Would you like to extend or modify the video?",
                action_type='modify',
                priority=7,
                metadata={'next_action': 'extend_video'}
            ),
            Suggestion(
                text="Should I create a thumbnail for this video?",
                action_type='create',
                priority=7,
                metadata={'next_action': 'create_thumbnail'}
            ),
        ],
        'audio_generation': [
            Suggestion(
                text="Would you like to use this audio in a video?",
                action_type='create',
                priority=9,
                metadata={'next_action': 'audio_to_video'}
            ),
            Suggestion(
                text="Should I generate more variations with different voices?",
                action_type='create',
                priority=8,
                metadata={'next_action': 'voice_variations'}
            ),
        ],
        'competitor_analysis': [
            Suggestion(
                text="Would you like me to create a brand strategy based on this analysis?",
                action_type='research',
                priority=9,
                metadata={'next_action': 'brand_strategy'}
            ),
            Suggestion(
                text="Should I develop a marketing strategy to differentiate from competitors?",
                action_type='research',
                priority=8,
                metadata={'next_action': 'marketing_strategy'}
            ),
            Suggestion(
                text="Would you like customer personas based on this market analysis?",
                action_type='research',
                priority=7,
                metadata={'next_action': 'customer_research'}
            ),
        ],
        'customer_research': [
            Suggestion(
                text="Should I create content tailored to these customer personas?",
                action_type='create',
                priority=9,
                metadata={'next_action': 'targeted_content'}
            ),
            Suggestion(
                text="Would you like marketing messages for each customer segment?",
                action_type='create',
                priority=8,
                metadata={'next_action': 'segment_messaging'}
            ),
        ],
        'brand_strategy': [
            Suggestion(
                text="Should I create visual brand assets (logo, colors, typography)?",
                action_type='create',
                priority=9,
                metadata={'next_action': 'brand_visuals'}
            ),
            Suggestion(
                text="Would you like a content strategy aligned with this brand?",
                action_type='research',
                priority=8,
                metadata={'next_action': 'content_strategy'}
            ),
        ],
        'job_search': [
            Suggestion(
                text="Would you like me to help optimize your resume for these roles?",
                action_type='create',
                priority=9,
                metadata={'next_action': 'resume_optimization'}
            ),
            Suggestion(
                text="Should I draft cover letters for the top matches?",
                action_type='create',
                priority=8,
                metadata={'next_action': 'cover_letter'}
            ),
            Suggestion(
                text="Would you like interview prep tips for these positions?",
                action_type='research',
                priority=7,
                metadata={'next_action': 'interview_prep'}
            ),
        ],
        'legal_analysis': [
            Suggestion(
                text="Would you like me to draft a response document?",
                action_type='create',
                priority=9,
                metadata={'next_action': 'draft_response'}
            ),
            Suggestion(
                text="Should I create an evidence checklist?",
                action_type='create',
                priority=8,
                metadata={'next_action': 'evidence_checklist'}
            ),
            Suggestion(
                text="Would you like a timeline of key events?",
                action_type='create',
                priority=7,
                metadata={'next_action': 'create_timeline'}
            ),
        ],
    }

    def __init__(self):
        self.last_action: Optional[Dict[str, Any]] = None
        self.action_history: List[Dict[str, Any]] = []

    def record_action(
        self,
        action_type: str,
        output: Any = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record an action that was performed.

        Args:
            action_type: Type of action (research, image_generation, etc.)
            output: The output/result of the action
            metadata: Additional context about the action
        """
        action = {
            'type': action_type,
            'output': output,
            'metadata': metadata or {},
            'timestamp': datetime.now()
        }
        self.last_action = action
        self.action_history.append(action)

        # Keep history manageable
        if len(self.action_history) > 50:
            self.action_history = self.action_history[-50:]

        logger.debug(f"📝 Recorded action: {action_type}")

    def get_suggestions(
        self,
        limit: int = 3,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Suggestion]:
        """
        Get follow-up suggestions based on last action.

        Args:
            limit: Maximum number of suggestions to return
            context: Optional additional context

        Returns:
            List of relevant suggestions
        """
        if not self.last_action:
            return []

        action_type = self.last_action.get('type', '')

        # Get base suggestions for this action type
        suggestions = self.SUGGESTION_TEMPLATES.get(action_type, [])

        # Filter and sort by priority
        filtered = []
        for s in suggestions:
            # Could add context-based filtering here
            filtered.append(s)

        # Sort by priority (highest first) and limit
        filtered.sort(key=lambda x: x.priority, reverse=True)
        return filtered[:limit]

    def format_for_response(
        self,
        suggestions: List[Suggestion]
    ) -> str:
        """
        Format suggestions for inclusion in AI response.

        Args:
            suggestions: List of suggestions to format

        Returns:
            Formatted string for response
        """
        if not suggestions:
            return ""

        lines = ["\n\n---\n**What would you like to do next?**"]
        for i, s in enumerate(suggestions, 1):
            lines.append(f"- {s.text}")

        return "\n".join(lines)

    def get_quick_actions(self) -> List[Dict[str, str]]:
        """
        Get quick action buttons for the frontend.

        Returns:
            List of {label, action} dicts for UI buttons
        """
        suggestions = self.get_suggestions(limit=3)

        actions = []
        for s in suggestions:
            actions.append({
                'label': s.text.replace('Would you like me to ', '').replace('Should I ', '').rstrip('?'),
                'action': s.metadata.get('next_action', ''),
                'type': s.action_type
            })

        return actions

    def detect_action_from_response(
        self,
        response: str,
        tool_calls: Optional[List[Dict]] = None
    ) -> Optional[str]:
        """
        Detect what type of action was performed based on response/tool calls.

        Args:
            response: The AI response text
            tool_calls: Any tool calls that were made

        Returns:
            Detected action type or None
        """
        # Check tool calls first (most reliable)
        if tool_calls:
            for tc in tool_calls:
                name = tc.get('name', '')
                if 'image_generation' in name or 'image_creation' in name:
                    return 'image_generation'
                elif 'video' in name:
                    return 'video_generation'
                elif 'audio' in name or 'voice' in name:
                    return 'audio_generation'
                elif 'research' in name:
                    return 'research'
                elif 'competitor' in name:
                    return 'competitor_analysis'
                elif 'customer' in name:
                    return 'customer_research'
                elif 'brand' in name:
                    return 'brand_strategy'
                elif 'job' in name or 'opportunity' in name:
                    return 'job_search'
                elif 'legal' in name or 'motion' in name:
                    return 'legal_analysis'

        # Fall back to response content analysis
        response_lower = response.lower()
        if 'generated image' in response_lower or 'created image' in response_lower:
            return 'image_generation'
        elif 'generated video' in response_lower or 'created video' in response_lower:
            return 'video_generation'
        elif 'research' in response_lower or 'analysis' in response_lower:
            return 'research'

        return None


# Singleton instance per user session
_services: Dict[str, SmartSuggestionsService] = {}


def get_smart_suggestions_service(session_id: str = 'default') -> SmartSuggestionsService:
    """Get or create a smart suggestions service for a session."""
    if session_id not in _services:
        _services[session_id] = SmartSuggestionsService()
    return _services[session_id]


def clear_suggestions_service(session_id: str = 'default') -> None:
    """Clear a session's suggestions service."""
    if session_id in _services:
        del _services[session_id]
