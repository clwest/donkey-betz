"""
Decision Extractor Service
Session 323: Boardroom Decisions (original)
Session 412: Updated to support both AgentConversation and HiveMindSession
Session 551: Added topic-based deduplication to prevent duplicate decisions
Session 593: Auto-create Pilot Readiness Gates for safety-sensitive decisions

Extracts structured decisions from agent conversation conclusions.
Uses GPT-5-mini to parse the conclusion text into structured format.

This supports BOTH:
- AgentConversation (legacy, ~2,899 records)
- HiveMindSession (new, session_mode='conversation')

The extracted decisions can be promoted to canonical policies
that influence future agent behavior.

Session 593: Safety-sensitive decisions now automatically get Pilot Readiness Gates:
- impact_area='security' → HIGH risk gate (6-item checklist)
- decision_type='policy' → MEDIUM risk gate (3-item checklist)
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
                model="gpt-5.2",
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

            # Session 593: Auto-create Pilot Readiness Gate for safety-sensitive decisions
            auto_create_gate_for_decision(summary)

            # Session 849: Auto-create Initiative if decision has a suggested feature
            auto_link_initiative_for_decision(summary)

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
                model="gpt-5.2",
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

            # Session 593: Auto-create Pilot Readiness Gate for safety-sensitive decisions
            auto_create_gate_for_decision(summary)

            # Session 849: Auto-create Initiative if decision has a suggested feature
            auto_link_initiative_for_decision(summary)

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


# =============================================================================
# Session 593: Auto-Gate Creation for Safety-Sensitive Decisions
# =============================================================================

def determine_gate_risk_level(decision) -> Optional[str]:
    """
    Session 593: Determine if a decision needs a Pilot Readiness Gate and at what risk level.
    Session 617: Expanded criteria to include more decision types.

    Rules:
    - impact_area='security' → 'high' risk (6-item safety checklist)
    - impact_area='infrastructure' → 'high' risk
    - decision_type='policy' → 'medium' risk (3-item checklist)
    - decision_type='architecture' → 'medium' risk
    - decision_type='guideline' → 'medium' risk
    - decision_type='experiment' → 'low' risk (fast-track checklist)
    - decision_type='product' → 'low' risk
    - decision_type='pipeline' → 'low' risk
    - decision_type='research' → 'low' risk
    - Otherwise → None (no gate needed)

    Args:
        decision: AgentDecisionSummary instance

    Returns:
        Risk level string ('high', 'medium', 'low') or None if no gate needed
    """
    # HIGH risk: Security and infrastructure decisions
    if decision.impact_area in ('security', 'infrastructure'):
        logger.info(f"Session 617: Decision '{decision.topic[:50]}...' has impact_area='{decision.impact_area}' → HIGH risk gate")
        return 'high'

    # MEDIUM risk: Policy, architecture, guideline decisions
    if decision.decision_type in ('policy', 'architecture', 'guideline'):
        logger.info(f"Session 617: Decision '{decision.topic[:50]}...' has decision_type='{decision.decision_type}' → MEDIUM risk gate")
        return 'medium'

    # LOW risk: Experiment, product, pipeline, research decisions
    if decision.decision_type in ('experiment', 'product', 'pipeline', 'research'):
        logger.info(f"Session 617: Decision '{decision.topic[:50]}...' has decision_type='{decision.decision_type}' → LOW risk gate")
        return 'low'

    # No gate needed for other decisions (discussion, dream_promotion, etc.)
    return None


def auto_create_gate_for_decision(decision) -> Optional['PilotReadinessGate']:
    """
    Session 593: Automatically create a Pilot Readiness Gate for safety-sensitive decisions.

    This is called after a decision is created. It checks if the decision meets
    the criteria for requiring a gate (security impact or policy type) and
    creates one if needed.

    Args:
        decision: AgentDecisionSummary instance

    Returns:
        The created PilotReadinessGate, or None if no gate was needed/created
    """
    from core.models_pilot_readiness import PilotReadinessGate

    # Check if gate already exists for this decision
    if hasattr(decision, 'readiness_gate'):
        try:
            existing = decision.readiness_gate
            logger.debug(f"Session 593: Gate already exists for decision {decision.id}")
            return existing
        except PilotReadinessGate.DoesNotExist:
            pass

    # Determine if this decision needs a gate
    risk_level = determine_gate_risk_level(decision)

    if not risk_level:
        logger.debug(f"Session 593: No gate needed for decision '{decision.topic[:50]}...' (type={decision.decision_type}, area={decision.impact_area})")
        return None

    try:
        gate = PilotReadinessGate.create_for_decision(decision, risk_level=risk_level)
        logger.info(f"Session 593: Auto-created {risk_level.upper()} risk gate for decision '{decision.topic[:50]}...' → gate {gate.id}")
        return gate
    except Exception as e:
        logger.error(f"Session 593: Failed to create gate for decision {decision.id}: {e}")
        return None


# =============================================================================
# Session 849: Auto-Initiative Creation for Decisions with Proposed Features
# =============================================================================


def _is_valid_initiative_name(name: str) -> bool:
    """
    Session 954: Validate that a name is suitable for an initiative.

    Prevents junk initiative creation by checking for:
    - Too short (< 10 chars)
    - Starts with lowercase (sentence fragment)
    - Starts with junk patterns
    - Contains certain marker patterns

    Returns:
        True if the name is valid for an initiative
    """
    if not name or len(name.strip()) < 10:
        return False

    name = name.strip()

    # Check for lowercase start (sentence fragment)
    if name[0].islower():
        return False

    # Check for junk patterns
    junk_starts = [
        'driven ',
        'plan ',
        'of-',
        'analysis ',
        'Auto-created',
        "A '",
        "An '",
        'stage ',
        'type/',
        'offs,',
        'that ',
        'which ',
        'to ',
        'for ',
        'with ',
        'from ',
        'and ',
        'the ',
    ]
    name_lower = name.lower()
    for pattern in junk_starts:
        if name_lower.startswith(pattern.lower()):
            return False

    # Check for junk contains patterns
    junk_contains = [
        '[Learned]',
        '[Synthesis]',
        'Feature name:',
    ]
    for pattern in junk_contains:
        if pattern.lower() in name_lower:
            return False

    # Must start with a capital letter or number
    if not (name[0].isupper() or name[0].isdigit()):
        return False

    return True


def auto_link_initiative_for_decision(decision) -> Optional['Initiative']:
    """
    Session 849: Auto-create and link an Initiative when a decision has a suggested_feature.

    ChatGPT feedback: "When a Learning has Proposed Feature, auto-create/link an Initiative"

    This creates the crucial link:
    Conversation → Decision (with suggested_feature) → Initiative → Stage 1 doc

    Args:
        decision: AgentDecisionSummary instance

    Returns:
        The created/linked Initiative, or None if no feature was suggested
    """
    # Only create initiative if there's a suggested feature
    if not decision.suggested_feature or len(decision.suggested_feature.strip()) < 10:
        logger.debug(f"Session 849: No suggested_feature for decision '{decision.topic[:50]}...'")
        return None

    # Skip if already linked to an initiative
    if decision.initiative_id:
        logger.debug(f"Session 849: Decision already linked to Initiative {decision.initiative_id}")
        return decision.initiative

    try:
        from core.services.initiative_integration_service import get_initiative_integration_service
        from core.models_document_registry import Initiative

        service = get_initiative_integration_service()

        # Extract feature name from suggested_feature
        # Format: "Name: X" or just use the first line
        feature_text = decision.suggested_feature.strip()
        feature_name = feature_text.split('\n')[0]

        # Try to extract name if it follows "Name: X" pattern
        if 'Name:' in feature_name:
            feature_name = feature_name.split('Name:')[1].strip()
        elif '-' in feature_name:
            # Handle "- Name: X" bullet format
            feature_name = feature_name.split('-', 1)[1].strip()
            if 'Name:' in feature_name:
                feature_name = feature_name.split('Name:')[1].strip()

        # Fallback to topic if feature name extraction failed
        if not feature_name or len(feature_name) < 3:
            feature_name = decision.topic

        # Session 865: Truncate feature name to fit Initiative.name max_length (200)
        # Leave room for normalization in the service
        if len(feature_name) > 150:
            feature_name = feature_name[:147] + '...'

        # Session 954: Validate feature name is a proper title before creating initiative
        # Prevents junk initiatives from being created with fragment names
        if not _is_valid_initiative_name(feature_name):
            logger.debug(f"Session 954: Skipping initiative creation - invalid name: '{feature_name[:50]}...'")
            return None

        # Create/get the initiative
        # Session 994: InitiativeCreationBlocked is raised if circuit breaker is tripped
        from core.services.initiative_integration_service import InitiativeCreationBlocked
        try:
            initiative, created = service.get_or_create_initiative(
                topic=feature_name,
                description=f"Auto-created from conversation decision.\n\nSuggested Feature:\n{feature_text}\n\nRationale:\n{decision.rationale}",
                source_decision_id=str(decision.id),
                created_by="DecisionExtractor"
            )
        except InitiativeCreationBlocked:
            logger.info(f"Session 994: Circuit breaker blocked initiative for decision '{decision.topic[:50]}...'")
            return None

        # Link the decision to the initiative
        decision.initiative = initiative
        decision.artifact_type = 'learning'  # Mark as learning since it proposes a feature
        decision.save(update_fields=['initiative', 'artifact_type'])

        if created:
            logger.info(f"Session 849: Created Initiative '{initiative.name}' from decision '{decision.topic[:50]}...'")
        else:
            logger.info(f"Session 849: Linked decision to existing Initiative '{initiative.name}'")

        return initiative

    except Exception as e:
        logger.error(f"Session 849: Failed to create Initiative for decision {decision.id}: {e}")
        return None


def batch_create_gates_for_existing_decisions(dry_run: bool = True, limit: int = None) -> Dict[str, Any]:
    """
    Session 593: Batch create Pilot Readiness Gates for existing decisions that qualify.
    Session 617: Expanded to handle all risk levels (high, medium, low).

    This retroactively creates gates for decisions that were made before the
    auto-gate feature was implemented.

    Args:
        dry_run: If True, only count what would be created. If False, create gates.
        limit: Optional limit on number of gates to create (useful for large batches)

    Returns:
        Dict with counts and results by risk level
    """
    from core.models_unified_system import AgentDecisionSummary
    from core.models_pilot_readiness import PilotReadinessGate
    from django.db.models import Q

    results = {
        'dry_run': dry_run,
        'high_count': 0,
        'medium_count': 0,
        'low_count': 0,
        'gates_created': 0,
        'skipped': 0,
        'errors': []
    }

    # Get existing gate decision IDs to avoid duplicates
    existing_gate_ids = set(PilotReadinessGate.objects.values_list('decision_id', flat=True))

    # HIGH risk: security, infrastructure impact areas
    high_decisions = AgentDecisionSummary.objects.filter(
        impact_area__in=['security', 'infrastructure']
    ).exclude(id__in=existing_gate_ids)
    results['high_count'] = high_decisions.count()

    # MEDIUM risk: policy, architecture, guideline types (exclude high risk areas)
    medium_decisions = AgentDecisionSummary.objects.filter(
        decision_type__in=['policy', 'architecture', 'guideline']
    ).exclude(
        impact_area__in=['security', 'infrastructure']
    ).exclude(id__in=existing_gate_ids)
    results['medium_count'] = medium_decisions.count()

    # LOW risk: experiment, product, pipeline, research types (exclude higher risk)
    low_decisions = AgentDecisionSummary.objects.filter(
        decision_type__in=['experiment', 'product', 'pipeline', 'research']
    ).exclude(
        impact_area__in=['security', 'infrastructure']
    ).exclude(
        decision_type__in=['policy', 'architecture', 'guideline']
    ).exclude(id__in=existing_gate_ids)
    results['low_count'] = low_decisions.count()

    total_eligible = results['high_count'] + results['medium_count'] + results['low_count']
    logger.info(f"Session 617 Batch: Found {total_eligible} decisions needing gates")
    logger.info(f"  HIGH: {results['high_count']}, MEDIUM: {results['medium_count']}, LOW: {results['low_count']}")

    if dry_run:
        return results

    # Process gates with optional limit
    gates_to_create = limit if limit else total_eligible

    # HIGH risk gates
    for decision in high_decisions:
        if results['gates_created'] >= gates_to_create:
            results['skipped'] = total_eligible - results['gates_created']
            break
        try:
            PilotReadinessGate.create_for_decision(decision, risk_level='high')
            results['gates_created'] += 1
            logger.info(f"  Created HIGH gate for: {decision.topic[:50]}...")
        except Exception as e:
            results['errors'].append(f"HIGH gate failed for {decision.id}: {e}")

    # MEDIUM risk gates
    for decision in medium_decisions:
        if results['gates_created'] >= gates_to_create:
            results['skipped'] = total_eligible - results['gates_created']
            break
        try:
            PilotReadinessGate.create_for_decision(decision, risk_level='medium')
            results['gates_created'] += 1
            logger.info(f"  Created MEDIUM gate for: {decision.topic[:50]}...")
        except Exception as e:
            results['errors'].append(f"MEDIUM gate failed for {decision.id}: {e}")

    # LOW risk gates
    for decision in low_decisions:
        if results['gates_created'] >= gates_to_create:
            results['skipped'] = total_eligible - results['gates_created']
            break
        try:
            PilotReadinessGate.create_for_decision(decision, risk_level='low')
            results['gates_created'] += 1
            logger.info(f"  Created LOW gate for: {decision.topic[:50]}...")
        except Exception as e:
            results['errors'].append(f"LOW gate failed for {decision.id}: {e}")

    logger.info(f"Session 617 Batch: Complete - {results['gates_created']}/{total_eligible} gates created")

    return results
