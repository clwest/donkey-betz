"""
Decision Extractor Service
Session 323: Boardroom Decisions

Extracts structured decisions from agent conversation conclusions.
Uses GPT to parse the conclusion text into structured format.
"""

import logging
from typing import Optional, Dict, Any
from openai import OpenAI

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = """
Analyze this agent conversation conclusion and extract a structured decision summary.

CONVERSATION TOPIC: {topic}
PARTICIPANTS: {participants}
CONCLUSION:
{conclusion}

Extract the following in JSON format:
{{
    "decision_type": "policy|architecture|pipeline|product|experiment|guideline",
    "impact_area": "prompting|memory|image|video|audio|workflow|agents|security|infrastructure|product",
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

Rules:
- key_insights should be 3-5 actionable bullet points
- recommended_stance should be definitive, not wishy-washy
- If no clear decision emerged, return {{"skip": true, "reason": "explanation"}}
- Be concise but complete
"""


class DecisionExtractor:
    """Extracts structured decisions from conversation conclusions."""

    def __init__(self):
        self.client = OpenAI()

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
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You extract structured decisions from agent discussions. Return valid JSON only."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=1000,
                temperature=0.3
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
        Extract and create an AgentDecisionSummary from a conversation.

        Returns the created summary, or None if extraction failed.
        """
        from core.models_unified_system import AgentDecisionSummary

        # Check if decision already exists for this conversation
        if AgentDecisionSummary.objects.filter(conversation=conversation).exists():
            logger.debug(f"Decision already exists for conversation {conversation.id}")
            return None

        extracted = self.extract_decision(conversation)
        if not extracted:
            return None

        try:
            summary = AgentDecisionSummary.objects.create(
                conversation=conversation,
                topic=extracted.get('topic', conversation.topic),
                decision_type=extracted.get('decision_type', 'guideline'),
                impact_area=extracted.get('impact_area', 'agents'),
                key_insights=extracted.get('key_insights', []),
                recommended_stance=extracted.get('recommended_stance', ''),
                suggested_feature=extracted.get('suggested_feature', ''),
                rationale=extracted.get('rationale', ''),
                participants=extracted.get('participants', []),
            )

            logger.info(f"Created decision summary: {summary}")
            return summary

        except Exception as e:
            logger.error(f"Error creating decision summary: {e}")
            return None


# Singleton instance
_extractor_instance = None


def get_decision_extractor() -> DecisionExtractor:
    """Get singleton decision extractor instance."""
    global _extractor_instance
    if _extractor_instance is None:
        _extractor_instance = DecisionExtractor()
    return _extractor_instance
