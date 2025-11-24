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
from intelligence.shared_memory import AgentMemoryInterface, redis_client

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

            # Session 175: Get memory context BEFORE generating perspectives
            # This makes agents personalized and informed by past decisions
            memory_context = self._get_context_for_agents(topic, project_id)
            logger.info(f"🧠 Memory context gathered: {len(memory_context)} chars")

            # Session 100: Dynamic agent perspective collection
            for participant_name in participants:
                try:
                    # Get agent template
                    agent_template = UnifiedAgentTemplate.objects.get(name=participant_name)

                    # Generate perspective using GPT-5-mini with agent's system prompt
                    # Session 175: Now includes memory context for personalized responses
                    perspective_prompt = f"""
Topic for discussion: {topic}

RELEVANT CONTEXT FROM MEMORY:
{memory_context}

You are {agent_template.display_name}. Based on your role and expertise:
{agent_template.system_prompt}

Provide your perspective on this topic in 2-3 sentences. Focus on:
- Your area of expertise
- Key considerations from your domain
- Specific recommendations

IMPORTANT: Reference the context above when relevant. If past decisions apply, mention them.
If user preferences are noted, factor them into your recommendation.
"""

                    # Session 173: Use gpt-4o-mini for faster, more reliable responses
                    response = self.client.chat.completions.create(
                        model="gpt-4o-mini",
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
                        max_tokens=300,
                        temperature=0.7
                    )

                    agent_perspective = response.choices[0].message.content or ""

                    # Session 173: Handle empty responses
                    if not agent_perspective.strip():
                        agent_perspective = f"I'd need more context to give a solid opinion on this. What specific aspect concerns you most?"
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

    def _get_context_for_agents(self, topic: str, project_id: Optional[str] = None) -> str:
        """
        Gather all relevant context from memory systems for informed agent perspectives.

        Session 175: Integrates Boardroom with Memory System so agents give
        personalized, context-aware recommendations.

        Args:
            topic: The meeting topic
            project_id: Optional project context

        Returns:
            Context string to inject into agent prompts
        """
        context_parts = []

        # 1. Past boardroom decisions from Redis
        try:
            past_meetings = []
            pattern = f"{self.memory.memory.memory_prefix}agent:meeting_coordinator:boardroom_*"
            meeting_keys = redis_client.keys(pattern)

            for key in meeting_keys[:10]:  # Last 10 meetings max
                data = redis_client.get(key)
                if data:
                    meeting = json.loads(data)
                    content = meeting.get('content', {})
                    if isinstance(content, dict):
                        past_meetings.append({
                            'topic': content.get('topic', 'Unknown'),
                            'decisions': content.get('decisions', []),
                            'date': meeting.get('timestamp', '')[:10]  # Just the date
                        })

            if past_meetings:
                # Sort by timestamp descending and take last 3
                past_meetings = sorted(past_meetings, key=lambda x: x.get('date', ''), reverse=True)[:3]
                context_parts.append("PAST BOARDROOM DECISIONS:")
                for m in past_meetings:
                    decisions_str = ', '.join(m.get('decisions', [])[:2])  # First 2 decisions
                    if decisions_str:
                        context_parts.append(f"  - {m['topic']}: {decisions_str}")
                    else:
                        context_parts.append(f"  - {m['topic']}: (discussed)")
        except Exception as e:
            logger.warning(f"Could not retrieve past meetings: {e}")

        # 2. User's style preferences from StyleMemory
        if self.user:
            try:
                from style_memory.models import StyleMemory

                # Get recent likes/loves
                positive_interactions = StyleMemory.objects.filter(
                    user=self.user,
                    interaction_type__in=['like', 'love', 'rate_5', 'rate_4']
                ).order_by('-created_at')[:15]

                # Get recent dislikes
                negative_interactions = StyleMemory.objects.filter(
                    user=self.user,
                    interaction_type__in=['dislike', 'rate_1', 'rate_2']
                ).order_by('-created_at')[:5]

                if positive_interactions.exists() or negative_interactions.exists():
                    context_parts.append("\nUSER STYLE PREFERENCES:")

                    if positive_interactions:
                        # Extract style elements user likes
                        liked_styles = set()
                        for interaction in positive_interactions:
                            if interaction.style_elements:
                                liked_styles.update(interaction.style_elements[:3])
                        if liked_styles:
                            context_parts.append(f"  - Prefers: {', '.join(list(liked_styles)[:5])}")
                        else:
                            context_parts.append(f"  - Has {positive_interactions.count()} liked/loved items")

                    if negative_interactions:
                        disliked_styles = set()
                        for interaction in negative_interactions:
                            if interaction.style_elements:
                                disliked_styles.update(interaction.style_elements[:3])
                        if disliked_styles:
                            context_parts.append(f"  - Dislikes: {', '.join(list(disliked_styles)[:5])}")
                        else:
                            context_parts.append(f"  - Has {negative_interactions.count()} disliked items")

            except Exception as e:
                logger.warning(f"Could not retrieve style preferences: {e}")

        # 3. Project context if project_id provided
        if project_id:
            try:
                from content.models import Project
                project = Project.objects.get(id=project_id)
                context_parts.append(f"\nPROJECT CONTEXT:")
                context_parts.append(f"  - Name: {project.name}")
                if project.description:
                    context_parts.append(f"  - Description: {project.description[:100]}...")
                context_parts.append(f"  - Images: {project.images.count()}")
                context_parts.append(f"  - Videos: {project.videos.count()}")
            except Exception as e:
                logger.debug(f"Could not retrieve project context: {e}")

        # 4. Get global context from memory system
        try:
            global_context = self.memory.memory.get_global_context()
            active_agents = len(global_context.get('agents', {}))
            if active_agents > 0:
                context_parts.append(f"\nSYSTEM STATE: {active_agents} agents currently active")
        except Exception as e:
            logger.debug(f"Could not get global context: {e}")

        if context_parts:
            return "\n".join(context_parts)
        else:
            return "No prior context available - this appears to be a new discussion topic."
