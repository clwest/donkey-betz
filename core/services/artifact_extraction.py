"""
Session 555 - Phase A: Artifact Extraction Service

Extracts actionable artifacts from completed agent conversations:
- Proposals
- Experiments
- Risks
- Data/Pipeline specs
- Open questions
- Action items
- Key insights
"""

import json
import logging
import time
from typing import List, Optional, Dict, Any

from django.db import transaction
from django.utils import timezone

from openai import OpenAI

logger = logging.getLogger(__name__)


class ArtifactExtractionService:
    """
    Extracts actionable artifacts from completed agent conversations.
    Uses GPT-5-mini for intelligent extraction.
    """

    # Executive agents carry more weight
    EXECUTIVE_AGENTS = {'CTOAgent', 'COOAgent', 'CEOAgent', 'CreativeDirectorAgent'}

    # Artifact types and their base importance
    TYPE_IMPORTANCE = {
        'risk': 0.8,        # Risks are critical to address
        'proposal': 0.7,    # Proposals need decisions
        'experiment': 0.7,  # Experiments are actionable
        'question': 0.6,    # Questions need answers
        'action_item': 0.6, # Action items are concrete
        'data_spec': 0.5,   # Technical specs are informational
        'insight': 0.4,     # Insights are nice-to-know
    }

    def __init__(self):
        self.client = OpenAI()

    def extract_from_conversation(self, conversation_id: str) -> List[Any]:
        """
        Main extraction method. Called when a conversation completes.

        Returns list of extracted ExtractedArtifact objects.
        """
        from core.models import AgentConversation, Agent
        from core.models_conversation_artifacts import ExtractedArtifact, ArtifactExtractionLog

        start_time = time.time()

        try:
            conversation = AgentConversation.objects.select_related('initiator').get(id=conversation_id)
        except AgentConversation.DoesNotExist:
            logger.warning(f"Conversation {conversation_id} not found")
            return []

        # Session 943: Skip automated brainstorming conversations - they generate
        # thousands of hypothetical artifacts that are not actionable items
        # requiring human review. The value is in the conversation conclusions,
        # not in individual artifact records.
        topic = conversation.topic or ''
        if topic.startswith('Discussion:') or topic.startswith('Panel:'):
            logger.debug(f"Skipping extraction for automated conversation {conversation_id}: {topic[:50]}")
            return []

        # Check if already extracted
        if conversation.extracted_artifacts.exists():
            logger.info(f"Conversation {conversation_id} already has artifacts, skipping")
            return list(conversation.extracted_artifacts.all())

        # Get conversation content
        conversation_text = self._format_conversation(conversation)

        if not conversation_text or len(conversation_text) < 100:
            logger.info(f"Conversation {conversation_id} too short for extraction")
            ArtifactExtractionLog.objects.create(
                conversation=conversation,
                status='skipped',
                error_message='Conversation too short'
            )
            return []

        # Call LLM for extraction
        try:
            extraction_result = self._call_extraction_llm(conversation_text)
        except Exception as e:
            logger.error(f"LLM extraction failed for {conversation_id}: {e}")
            ArtifactExtractionLog.objects.create(
                conversation=conversation,
                status='failed',
                error_message=str(e)
            )
            return []

        if not extraction_result:
            logger.info(f"No artifacts found in conversation {conversation_id}")
            ArtifactExtractionLog.objects.create(
                conversation=conversation,
                status='success',
                artifacts_found=0,
                extraction_time_ms=int((time.time() - start_time) * 1000)
            )
            return []

        # Create artifacts
        artifacts = []
        agent_cache = {}

        with transaction.atomic():
            for item in extraction_result:
                try:
                    # Look up source agent
                    source_agent_name = item.get('source_agent', '')
                    source_agent = None
                    if source_agent_name:
                        if source_agent_name not in agent_cache:
                            agent_cache[source_agent_name] = Agent.objects.filter(
                                name__icontains=source_agent_name.replace('Agent', '')
                            ).first()
                        source_agent = agent_cache.get(source_agent_name)

                    # Calculate scores
                    importance = self._score_importance(item, source_agent)
                    urgency = self._score_urgency(item)

                    artifact = ExtractedArtifact.objects.create(
                        conversation=conversation,
                        artifact_type=item.get('type', 'insight'),
                        title=item.get('title', 'Untitled')[:200],
                        description=item.get('description', ''),
                        source_agent=source_agent,
                        source_message_index=item.get('message_index'),
                        details=item.get('details', {}),
                        importance_score=importance,
                        urgency_score=urgency,
                        confidence_score=item.get('confidence', 0.7),
                    )
                    artifacts.append(artifact)
                except Exception as e:
                    logger.warning(f"Failed to create artifact: {e}")
                    continue

            # Log extraction
            ArtifactExtractionLog.objects.create(
                conversation=conversation,
                status='success',
                artifacts_found=len(artifacts),
                extraction_time_ms=int((time.time() - start_time) * 1000),
                raw_response={'artifacts': extraction_result}
            )

        logger.info(f"Extracted {len(artifacts)} artifacts from conversation {conversation_id}")
        return artifacts

    def _format_conversation(self, conversation) -> str:
        """Format conversation for LLM analysis."""
        # messages is a RelatedManager, use .all() to query
        messages = conversation.messages.all().order_by('sequence_number')[:30]
        if not messages.exists():
            return ""

        lines = [f"Topic: {conversation.topic or 'General Discussion'}"]
        lines.append(f"Participants: {conversation.initiator.name if conversation.initiator else 'Unknown'}")

        for i, msg in enumerate(messages):
            agent_name = msg.agent.name if msg.agent else 'Unknown'
            content = (msg.content or '')[:500]  # Truncate long messages
            lines.append(f"[{i+1}] {agent_name}: {content}")

        return "\n".join(lines)

    def _call_extraction_llm(self, conversation_text: str) -> Optional[List[Dict[str, Any]]]:
        """
        Use GPT-5-mini to identify artifacts in conversation.
        """
        prompt = f"""Analyze this agent conversation and extract actionable artifacts.

CONVERSATION:
{conversation_text}

For each artifact found, provide:
1. type: proposal | experiment | risk | data_spec | question | action_item | insight
2. title: Short title (max 100 chars)
3. description: Full description
4. source_agent: Which agent proposed this
5. details: Structured details specific to type
6. confidence: How confident you are this is a real artifact (0.0-1.0)

ARTIFACT TYPE DEFINITIONS:
- proposal: A concrete suggestion to do something ("We should do X")
- experiment: A testable hypothesis ("Test X vs Y to see which performs better")
- risk: A concern or warning about something ("Risk: X could happen")
- data_spec: A technical specification or data pipeline design
- question: Something needing human decision ("We need to decide X")
- action_item: A concrete next step someone needs to do
- insight: An important observation or discovery

ONLY extract artifacts that are:
- Specific and actionable
- Actually proposed in the conversation (not implied)
- Significant enough to warrant human attention

Return as JSON array. If no artifacts found, return empty array [].

Example format:
[
  {{
    "type": "experiment",
    "title": "A/B test pricing tiers",
    "description": "Run 4-week experiment comparing $9/$19/$49 pricing tiers",
    "source_agent": "BrandIdentityAgent",
    "details": {{
      "hypothesis": "Mid-tier ($19) will have highest conversion",
      "metrics": ["conversion_rate", "revenue_per_visitor"],
      "duration": "4 weeks"
    }},
    "confidence": 0.9
  }},
  {{
    "type": "risk",
    "title": "Sample size insufficient for conclusions",
    "description": "Current data sample is too small for statistical significance",
    "source_agent": "COOAgent",
    "details": {{
      "severity": "high",
      "likelihood": "confirmed",
      "mitigation": "Expand sample to 500+ items"
    }},
    "confidence": 0.85
  }}
]

JSON array only, no other text:"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-5.2",
                messages=[
                    {"role": "system", "content": "You are an artifact extraction specialist. Extract actionable items from agent conversations. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                # GPT-5-mini is a reasoning model - needs extra tokens for reasoning + output
                max_completion_tokens=8000
            )

            content = response.choices[0].message.content.strip()

            # Parse JSON
            try:
                result = json.loads(content)
                # Handle both array and object with 'artifacts' key
                if isinstance(result, list):
                    return result
                elif isinstance(result, dict) and 'artifacts' in result:
                    return result['artifacts']
                elif isinstance(result, dict):
                    # Single artifact
                    return [result] if result.get('type') else []
                return []
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse extraction JSON: {e}")
                return []

        except Exception as e:
            logger.error(f"GPT extraction call failed: {e}")
            raise

    def _score_importance(self, artifact: Dict, source_agent: Optional[Any]) -> float:
        """
        Score artifact importance based on:
        - Type importance (risks > proposals > insights)
        - Agent seniority (executives > regular agents)
        """
        # Base score from type
        artifact_type = artifact.get('type', 'insight')
        base_score = self.TYPE_IMPORTANCE.get(artifact_type, 0.5)

        # Boost for executive agents
        if source_agent:
            agent_name = source_agent.name if hasattr(source_agent, 'name') else str(source_agent)
            if any(exec_name in agent_name for exec_name in self.EXECUTIVE_AGENTS):
                base_score = min(1.0, base_score + 0.15)

        # Boost for high severity risks
        details = artifact.get('details', {})
        if artifact_type == 'risk' and details.get('severity') == 'high':
            base_score = min(1.0, base_score + 0.1)

        return round(base_score, 2)

    def _score_urgency(self, artifact: Dict) -> float:
        """
        Score artifact urgency.
        """
        artifact_type = artifact.get('type', 'insight')
        details = artifact.get('details', {})

        # Default urgency by type
        urgency_map = {
            'risk': 0.7,
            'action_item': 0.6,
            'question': 0.5,
            'proposal': 0.4,
            'experiment': 0.4,
            'data_spec': 0.3,
            'insight': 0.2,
        }

        urgency = urgency_map.get(artifact_type, 0.5)

        # Boost for high likelihood risks
        if artifact_type == 'risk' and details.get('likelihood') == 'confirmed':
            urgency = min(1.0, urgency + 0.2)

        return round(urgency, 2)

    def batch_extract(self, hours_back: int = 24) -> Dict[str, Any]:
        """
        Process conversations from last N hours that haven't been extracted.
        """
        from core.models import AgentConversation

        cutoff = timezone.now() - timezone.timedelta(hours=hours_back)

        # Get conversations without artifacts
        # Note: status is 'concluded' not 'completed'
        conversations = AgentConversation.objects.filter(
            started_at__gte=cutoff,
            status='concluded'
        ).exclude(
            artifacts__isnull=False
        ).order_by('-started_at')[:50]  # Limit to 50 per batch

        results = {
            'processed': 0,
            'artifacts_total': 0,
            'errors': 0,
            'by_type': {}
        }

        for conv in conversations:
            try:
                artifacts = self.extract_from_conversation(str(conv.id))
                results['processed'] += 1
                results['artifacts_total'] += len(artifacts)

                for a in artifacts:
                    t = a.artifact_type
                    results['by_type'][t] = results['by_type'].get(t, 0) + 1

            except Exception as e:
                logger.error(f"Failed to extract from {conv.id}: {e}")
                results['errors'] += 1

        return results


# Singleton instance
extraction_service = ArtifactExtractionService()
