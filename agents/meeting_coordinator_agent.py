"""
Meeting Coordinator Agent - Executive Boardroom Facilitator (Session 98)

The Meeting Coordinator Agent orchestrates collaborative sessions between executive agents
(CTO, COO) to discuss topics, share perspectives, and reach decisions.

Phase 1 Capabilities:
- Coordinate meetings between CTO and COO agents
- Collect perspectives from each participant
- Use GPT-5-mini to synthesize discussions
- Extract decisions and action items
- Store results in boardroom AISession

Phase 2 (Future):
- Support more agent participants
- Multi-round discussions
- Real-time collaboration
- Meeting minutes generation

Created: Session 98
"""

import logging
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

from django.contrib.auth import get_user_model
from openai import OpenAI

from agents.models import UnifiedAgentTemplate, AgentSpecialization
from agents.cto_agent import CTOAgent
from agents.coo_agent import COOAgent
from intelligence.shared_memory import AgentMemoryInterface

User = get_user_model()
logger = logging.getLogger(__name__)


class MeetingCoordinatorAgent:
    """
    Meeting Coordinator Agent - Facilitates executive boardroom discussions

    Phase 1: Simple one-round meetings between CTO and COO
    - Collects input from each participant
    - Synthesizes perspectives with GPT-5-mini
    - Extracts decisions and action items
    """

    def __init__(self, user: Optional[User] = None):
        """
        Initialize Meeting Coordinator Agent

        Args:
            user: Optional User instance for personalized meetings
        """
        self.user = user
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.memory = AgentMemoryInterface(agent_id='meeting_coordinator')
        self.template = self._get_or_create_template()

        logger.info(f"🏢 Meeting Coordinator initialized for user: {user.username if user else 'anonymous'}")

    def _get_or_create_template(self) -> UnifiedAgentTemplate:
        """Get or create the MeetingCoordinatorAgent template"""
        template, created = UnifiedAgentTemplate.objects.get_or_create(
            name='MeetingCoordinatorAgent',
            defaults={
                'display_name': 'Meeting Coordinator (Executive Boardroom)',
                'description': 'Facilitates collaborative sessions between executive agents (CTO, COO) for strategic discussions and decision-making.',
                'specialization': AgentSpecialization.BUSINESS,
                'capabilities': ['meeting_coordination', 'discussion_synthesis', 'decision_extraction'],
                'routing_keywords': ['meeting', 'boardroom', 'collaborate', 'discuss', 'executive session'],
                'system_prompt': 'You are the Meeting Coordinator for executive boardroom sessions.',
                'llm_provider': 'openai',
                'llm_model': 'gpt-5-mini',
                'metadata': {'phase': 'v1_simple_meetings'}
            }
        )

        if created:
            logger.info("✅ Created new MeetingCoordinatorAgent template")
        else:
            logger.debug(f"Using existing MeetingCoordinatorAgent template: {template.id}")

        return template

    def start_meeting(
        self,
        topic: str,
        project_id: Optional[str] = None,
        participants: List[str] = None
    ) -> Dict[str, Any]:
        """
        Start an executive boardroom meeting

        Args:
            topic: Meeting topic/agenda
            project_id: Optional project context
            participants: List of agent names (default: CTOAgent, COOAgent)

        Returns:
            Dict with meeting results:
            {
                'topic': str,
                'participants': List[str],
                'agent_responses': Dict[str, str],
                'summary': str,
                'decisions': List[str],
                'action_items': List[Dict],
                'status': str
            }
        """
        # Default participants: CTO + COO
        if participants is None:
            participants = ['CTOAgent', 'COOAgent']

        logger.info(f"🏢 Starting boardroom meeting on: {topic}")
        logger.info(f"👥 Participants: {', '.join(participants)}")

        try:
            # Phase 1: Collect perspectives from each participant
            agent_responses = {}

            # Session 100: Dynamic agent perspective collection
            for participant_name in participants:
                try:
                    # Get agent template
                    agent_template = UnifiedAgentTemplate.objects.get(name=participant_name)

                    # Generate perspective using GPT-5-mini with agent's system prompt
                    perspective_prompt = f"""
Topic for discussion: {topic}

You are {agent_template.display_name}. Based on your role and expertise:
{agent_template.system_prompt}

Provide your perspective on this topic in 2-3 sentences. Focus on:
- Your area of expertise
- Key considerations from your domain
- Specific recommendations
"""

                    response = self.client.chat.completions.create(
                        model="gpt-5-mini",
                        messages=[
                            {
                                "role": "system",
                                "content": agent_template.system_prompt or "You are an executive advisor."
                            },
                            {
                                "role": "user",
                                "content": perspective_prompt
                            }
                        ],
                        reasoning_effort="medium",
                        max_completion_tokens=500
                    )

                    agent_perspective = response.choices[0].message.content or ""
                    agent_responses[participant_name] = agent_perspective
                    logger.info(f"✅ Collected {participant_name} perspective ({len(agent_perspective)} chars)")

                except UnifiedAgentTemplate.DoesNotExist:
                    logger.warning(f"❌ Agent template not found: {participant_name}")
                    agent_responses[participant_name] = f"(Agent {participant_name} not available)"
                except Exception as e:
                    logger.error(f"❌ Error getting {participant_name} perspective: {str(e)}")
                    agent_responses[participant_name] = "(Error generating perspective)"

            # Phase 2: Synthesize with GPT-5-mini
            synthesis_prompt = f"""
You are synthesizing an executive boardroom meeting.

Topic: {topic}
Participants: {', '.join(participants)}

Agent Perspectives:
{json.dumps(agent_responses, indent=2)}

Synthesize this discussion and extract:
1. Meeting summary (key points discussed)
2. Decisions made (concrete decisions reached)
3. Action items (who does what, with priority)

Focus on:
- Strategic alignment between all executive perspectives (technical, operational, legal, marketing, product, finance, HR, strategy)
- Concrete next steps with clear ownership
- Risk mitigation across all domains
- Cross-functional collaboration opportunities
"""

            response = self.client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": synthesis_prompt
                    }
                ],
                reasoning_effort="high",
                max_completion_tokens=4000
            )

            # Get synthesis (plain text from reasoning model)
            synthesis = response.choices[0].message.content

            # Phase 3: Extract structured data from synthesis
            extraction_prompt = f"""
From this meeting synthesis, extract structured data:

{synthesis}

Return ONLY valid JSON with these exact keys:
{{
    "summary": "2-3 sentence meeting summary",
    "decisions": ["decision 1", "decision 2", ...],
    "action_items": [
        {{"task": "...", "owner": "CTO|COO", "priority": "high|medium|low"}},
        ...
    ]
}}
"""

            extraction_response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Use regular GPT-4o-mini for JSON extraction
                messages=[
                    {
                        "role": "user",
                        "content": extraction_prompt
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=2000
            )

            # Parse structured data
            extracted = json.loads(extraction_response.choices[0].message.content)

            # Combine results
            meeting_results = {
                'topic': topic,
                'project_id': project_id,
                'participants': participants,
                'agent_responses': agent_responses,
                'summary': extracted.get('summary', synthesis[:500]),
                'decisions': extracted.get('decisions', []),
                'action_items': extracted.get('action_items', []),
                'status': 'complete',
                'met_at': datetime.now().isoformat()
            }

            # Store in memory
            memory_key = f"boardroom_meeting_{topic.replace(' ', '_').lower()[:50]}"
            self.memory.remember(memory_key, meeting_results)

            logger.info(f"✅ Meeting complete: {len(meeting_results['decisions'])} decisions, {len(meeting_results['action_items'])} action items")

            return meeting_results

        except Exception as e:
            logger.error(f"❌ Meeting coordination failed: {str(e)}")
            import traceback
            traceback.print_exc()

            return {
                'topic': topic,
                'participants': participants,
                'agent_responses': {},
                'summary': '',
                'decisions': [],
                'action_items': [],
                'status': 'failed',
                'error': str(e)
            }

    def _get_system_prompt(self) -> str:
        """Get the Meeting Coordinator system prompt"""
        return """You are the Meeting Coordinator for executive boardroom sessions.

You facilitate strategic discussions between:
- CTO Agent (technical architecture, implementation)
- COO Agent (operations, planning, risk management)

Your role:
- Synthesize diverse perspectives into coherent insights
- Extract actionable decisions
- Identify clear action items with ownership
- Ensure strategic alignment

You prioritize:
- Clarity (clear decisions and action items)
- Alignment (technical + operational harmony)
- Actionability (concrete next steps)
- Risk awareness (identify potential blockers)

You are concise, strategic, and focused on outcomes."""
