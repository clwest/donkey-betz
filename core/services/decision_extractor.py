"""
Decision Extractor Service
Session 323: Boardroom Decisions (original)
Session 412: Updated to support both AgentConversation and HiveMindSession
Session 551: Added topic-based deduplication to prevent duplicate decisions

Extracts structured decisions from agent conversation conclusions.
Uses GPT-5-mini to parse the conclusion text into structured format.

This supports BOTH:
- AgentConversation (legacy, ~2,899 records)
- HiveMindSession (new, session_mode='conversation')

The extracted decisions can be promoted to canonical policies
that influence future agent behavior.
"""

import logging
import re
from datetime import timedelta
from typing import Optional, Dict, Any, Union
from django.utils import timezone
from openai import OpenAI

logger = logging.getLogger(__name__)


def normalize_topic(topic: str) -> str:
    """
    Normalize a topic string for comparison.
    Session 551: Used for topic-based deduplication.
    """
    if not topic:
        return ''
    # Remove common prefixes: [Learned], Discussion:, etc.
    normalized = re.sub(r'\[Learned\]\s*', '', topic).strip()
    normalized = re.sub(r'^Discussion:\s*', '', normalized, flags=re.IGNORECASE).strip()
    # Lowercase and remove special chars
    normalized = normalized.lower()
    normalized = re.sub(r'[^a-z0-9\s]', '', normalized).strip()
    # Collapse multiple spaces
    normalized = re.sub(r'\s+', ' ', normalized)
    return normalized


# Session 586: Noise filter patterns
# These topics are too generic to warrant Boardroom decisions
NOISE_TOPICS = {
    'ai',
    'learned',
    'discussion',
    'panel',
    'general',
    'update',
    'misc',
    'other',
    'test',
    'debug',
}


def is_noise_topic(topic: str) -> bool:
    """
    Session 586: Filter out noise topics that shouldn't become Boardroom decisions.

    Returns True if the topic is noise and should be filtered out.

    Noise criteria:
    1. Normalized topic is too short (< 5 chars)
    2. Normalized topic is a known noise word
    3. Topic is just prefixes with no substance
    """
    if not topic:
        return True

    normalized = normalize_topic(topic)

    # Too short after normalization
    if len(normalized) < 5:
        logger.debug(f"Noise filter: topic too short after normalization: '{topic}' -> '{normalized}'")
        return True

    # Known noise words
    if normalized in NOISE_TOPICS:
        logger.debug(f"Noise filter: topic matches noise word: '{topic}' -> '{normalized}'")
        return True

    # Just a single common word
    words = normalized.split()
    if len(words) == 1 and normalized in {'ai', 'ml', 'api', 'ui', 'ux', 'db', 'test'}:
        logger.debug(f"Noise filter: single generic word: '{topic}'")
        return True

    return False

EXTRACTION_PROMPT = """
Analyze this agent conversation conclusion and extract a structured decision summary.

CONVERSATION TOPIC: {topic}
PARTICIPANTS: {participants}
CONCLUSION:
{conclusion}

Extract the following in JSON format:
{{
    "decision_type": "policy|architecture|pipeline|product|experiment|guideline",
    "impact_area": "prompting|memory|image|video|audio|workflow|agents|security|infrastructure|product|legal|research|spider",
    "key_insights": ["insight 1", "insight 2", "insight 3"],
    "recommended_stance": "The main policy or decision in 1-2 sentences",
    "suggested_feature": "Optional: specific feature or implementation suggestion",
    "rationale": "Why this decision makes sense in 1-2 sentences"
}}

DECISION TYPE GUIDE:
- policy: Rules for how agents or systems should behave
- architecture: Technical design decisions about system structure
- pipeline: Workflow or data processing decisions
- product: User-facing feature recommendations
- experiment: Ideas worth testing but not yet established
- guideline: Best practices or recommendations

IMPACT AREA GUIDE:
- prompting: Prompt engineering techniques and strategies
- memory: Agent memory, storage, and persistence
- image: Image generation and editing
- video: Video generation and editing
- audio: Audio/speech generation
- workflow: Multi-step workflows and orchestration
- agents: Agent behavior and collaboration
- security: Privacy, security, and access control
- infrastructure: Technical infrastructure and systems
- product: Product features and user experience
- legal: Legal assistant and document drafting
- research: Research and analysis features
- spider: Web scraping and data collection

Rules:
- key_insights should be 3-5 actionable bullet points
- recommended_stance should be definitive, not wishy-washy
- If no clear decision emerged, return {{"skip": true, "reason": "explanation"}}
- Be concise but complete
"""


class DecisionExtractor:
    """Extracts structured decisions from conversation conclusions."""

    # Session 551: Deduplication window - skip if same topic was decided within this period
    DEDUP_HOURS = 24

    def __init__(self):
        self.client = OpenAI()

    def _has_recent_decision_for_topic(self, topic: str) -> bool:
        """
        Check if a decision was recently made for a similar topic.
        Session 551: Prevents duplicate decisions from different conversations.

        Args:
            topic: The topic to check

        Returns:
            True if a recent decision exists for this topic
        """
        from core.models_unified_system import AgentDecisionSummary

        normalized = normalize_topic(topic)
        if not normalized or len(normalized) < 6:
            return False

        cutoff = timezone.now() - timedelta(hours=self.DEDUP_HOURS)

        # Check existing decisions within the window
        recent_decisions = AgentDecisionSummary.objects.filter(
            created_at__gte=cutoff
        ).values_list('topic', flat=True)

        for existing_topic in recent_decisions:
            if normalize_topic(existing_topic) == normalized:
                logger.info(f"Session 551: Skipping duplicate decision for topic '{topic[:50]}...' - similar decision exists within {self.DEDUP_HOURS}h")
                return True

        return False

    def extract_decision(
        self,
        conversation
    ) -> Optional[Dict[str, Any]]:
        """
        Extract a decision from a conversation's conclusion.

        Args:
            conversation: AgentConversation instance

        Returns:
            Dict with decision fields, or None if no clear decision
        """
        if not conversation.conclusion:
            logger.debug(f"No conclusion for conversation {conversation.id}")
            return None

        # Skip empty or trivial conclusions
        conclusion_text = conversation.conclusion.strip()
        if len(conclusion_text) < 50:
            logger.debug(f"Conclusion too short for conversation {conversation.id}")
            return None

        # Get participant names
        participants = [p.name for p in conversation.participants.all()]
        if conversation.initiator and conversation.initiator.name not in participants:
            participants.insert(0, conversation.initiator.name)

        prompt = EXTRACTION_PROMPT.format(
            topic=conversation.topic,
            participants=', '.join(participants),
            conclusion=conclusion_text
        )

        try:
            # Session 338: Use gpt-5-mini for cost efficiency
            # Note: reasoning models don't support temperature parameter
            response = self.client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You extract structured decisions from agent discussions. Return valid JSON only."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_completion_tokens=2000,  # For reasoning + JSON output
            )

            import json
            result = json.loads(response.choices[0].message.content)

            # Check if GPT decided to skip
            if result.get('skip'):
                logger.debug(f"No clear decision in conversation {conversation.id}: {result.get('reason')}")
                return None

            # Validate required fields
            if not result.get('recommended_stance'):
                logger.debug(f"No recommended stance in conversation {conversation.id}")
                return None

            # Add participants
            result['participants'] = participants
            result['topic'] = conversation.topic

            return result

        except Exception as e:
            logger.error(f"Error extracting decision from conversation {conversation.id}: {e}")
            return None

    def create_decision_from_conversation(self, conversation) -> Optional['AgentDecisionSummary']:
        """
        Extract and create an AgentDecisionSummary from a legacy AgentConversation.

        Args:
            conversation: AgentConversation instance

        Returns:
            The created AgentDecisionSummary, or None if extraction failed.
        """
        from core.models_unified_system import AgentDecisionSummary

        # Check if decision already exists for this conversation
        if AgentDecisionSummary.objects.filter(conversation=conversation).exists():
            logger.debug(f"Decision already exists for conversation {conversation.id}")
            return None

        # Session 551: Check for recent decision on same topic (topic-based dedup)
        if self._has_recent_decision_for_topic(conversation.topic):
            return None

        # Session 586: Filter out noise topics
        if is_noise_topic(conversation.topic):
            logger.debug(f"Skipping noise topic for conversation {conversation.id}: {conversation.topic}")
            return None

        extracted = self.extract_decision(conversation)
        if not extracted:
            return None

        try:
            summary = AgentDecisionSummary.objects.create(
                conversation=conversation,  # Legacy link
                hive_session=None,
                topic=extracted.get('topic', conversation.topic),
                decision_type=extracted.get('decision_type', 'guideline'),
                impact_area=extracted.get('impact_area', 'agents'),
                key_insights=extracted.get('key_insights', []),
                recommended_stance=extracted.get('recommended_stance', ''),
                suggested_feature=extracted.get('suggested_feature', ''),
                rationale=extracted.get('rationale', ''),
                participants=extracted.get('participants', []),
            )

            logger.info(f"Created decision summary from AgentConversation: {summary}")
            return summary

        except Exception as e:
            logger.error(f"Error creating decision summary from AgentConversation: {e}")
            return None

    def extract_decision_from_hive_session(
        self,
        session
    ) -> Optional[Dict[str, Any]]:
        """
        Extract a decision from a HiveMindSession's conclusion.

        Args:
            session: HiveMindSession instance

        Returns:
            Dict with decision fields, or None if no clear decision
        """
        # HiveMindSession uses `synthesis` field for conclusions
        conclusion = session.synthesis

        if not conclusion:
            logger.debug(f"No conclusion for HiveMindSession {session.id}")
            return None

        # Skip empty or trivial conclusions
        conclusion_text = conclusion.strip()
        if len(conclusion_text) < 50:
            logger.debug(f"Conclusion too short for HiveMindSession {session.id}")
            return None

        # Get participant names from the session
        # participant_ids is a JSONField with list of agent UUIDs
        from core.models_unified_system import Agent
        participants = []
        if session.participant_ids:
            agents = Agent.objects.filter(id__in=session.participant_ids)
            participants = list(agents.values_list('name', flat=True))

        # Use conversation_topic for conversation mode, question for hive_mind mode
        topic = session.conversation_topic or session.question or 'Unknown Topic'

        prompt = EXTRACTION_PROMPT.format(
            topic=topic,
            participants=', '.join(participants) if participants else 'Unknown',
            conclusion=conclusion_text
        )

        try:
            response = self.client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You extract structured decisions from agent discussions. Return valid JSON only."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_completion_tokens=2000,
            )

            import json
            result = json.loads(response.choices[0].message.content)

            # Check if GPT decided to skip
            if result.get('skip'):
                logger.debug(f"No clear decision in HiveMindSession {session.id}: {result.get('reason')}")
                return None

            # Validate required fields
            if not result.get('recommended_stance'):
                logger.debug(f"No recommended stance in HiveMindSession {session.id}")
                return None

            # Add participants and topic
            result['participants'] = participants
            result['topic'] = topic

            return result

        except Exception as e:
            logger.error(f"Error extracting decision from HiveMindSession {session.id}: {e}")
            return None

    def create_decision_from_hive_session(self, session) -> Optional['AgentDecisionSummary']:
        """
        Extract and create an AgentDecisionSummary from a HiveMindSession.

        Args:
            session: HiveMindSession instance (should have session_mode='conversation')

        Returns:
            The created AgentDecisionSummary, or None if extraction failed
        """
        from core.models_unified_system import AgentDecisionSummary

        # Check if decision already exists for this session
        if AgentDecisionSummary.objects.filter(hive_session=session).exists():
            logger.debug(f"Decision already exists for HiveMindSession {session.id}")
            return None

        # Use conversation_topic for conversation mode, question for hive_mind mode
        fallback_topic = session.conversation_topic or session.question or 'Unknown Topic'

        # Session 551: Check for recent decision on same topic (topic-based dedup)
        if self._has_recent_decision_for_topic(fallback_topic):
            return None

        # Session 586: Filter out noise topics
        if is_noise_topic(fallback_topic):
            logger.debug(f"Skipping noise topic for HiveMindSession {session.id}: {fallback_topic}")
            return None

        extracted = self.extract_decision_from_hive_session(session)
        if not extracted:
            return None

        try:
            summary = AgentDecisionSummary.objects.create(
                conversation=None,  # No legacy link
                hive_session=session,  # New link
                topic=extracted.get('topic', fallback_topic),
                decision_type=extracted.get('decision_type', 'guideline'),
                impact_area=extracted.get('impact_area', 'agents'),
                key_insights=extracted.get('key_insights', []),
                recommended_stance=extracted.get('recommended_stance', ''),
                suggested_feature=extracted.get('suggested_feature', ''),
                rationale=extracted.get('rationale', ''),
                participants=extracted.get('participants', []),
            )

            logger.info(f"Created decision summary from HiveMindSession: {summary}")
            return summary

        except Exception as e:
            logger.error(f"Error creating decision summary from HiveMindSession: {e}")
            return None

    def create_decision_from_any(
        self,
        source: Union['AgentConversation', 'HiveMindSession']
    ) -> Optional['AgentDecisionSummary']:
        """
        Create a decision from either conversation type.

        Args:
            source: Either an AgentConversation or HiveMindSession

        Returns:
            The created AgentDecisionSummary, or None if extraction failed
        """
        # Check which type we have
        model_name = source.__class__.__name__

        if model_name == 'AgentConversation':
            return self.create_decision_from_conversation(source)
        elif model_name == 'HiveMindSession':
            return self.create_decision_from_hive_session(source)
        else:
            logger.error(f"Unknown source type: {model_name}")
            return None


# Singleton instance
_extractor_instance = None


def get_decision_extractor() -> DecisionExtractor:
    """Get singleton decision extractor instance."""
    global _extractor_instance
    if _extractor_instance is None:
        _extractor_instance = DecisionExtractor()
    return _extractor_instance
