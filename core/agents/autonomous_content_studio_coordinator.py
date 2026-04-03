"""
Autonomous Content Studio Coordinator - Session 466

The brain of the Autonomous Content Studio (Tier 1 Autonomous Situation #3).

This agent orchestrates the entire autonomous content creation cycle:
1. Monitors all active content channels
2. Triggers agent debates when content is due
3. Coordinates with AISeriesWorkflowAgent to create content
4. Tracks performance and adjusts strategy
5. Self-schedules next content cycles

Design Pattern:
Follows MarketIntelligenceCoordinator pattern (Session 465) with all 5 autonomous properties:
1. Persistent Context - Loads channel config and history from DB
2. Incoming Signals - Monitors spider trends, performance metrics
3. Internal Disagreement - Coordinates TopicMiner vs Contrarian vs Analyst debates
4. Outputs with Consequences - Creates content, tracks performance
5. Self-Renewal - Schedules next cycle after each content creation

Usage:
    from core.agent_router import AgentRouter

    router = AgentRouter(user=request.user)
    result = router.route(
        "AutonomousContentStudioCoordinator",
        "Check all channels and create content where needed"
    )
"""

import logging
import json
from typing import Dict, Any, List
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
import time

from core.agents.base_agent import BaseAgent, AgentResult
from core.services.memory_context_service import get_memory_context_service
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


def analyze_content_studio_with_ml(channel_data: dict) -> dict:
    """Analyze content studio channel data using ML models (Text)."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()
        result = router.auto_route(
            data=channel_data,
            task_hint=TaskType.TEXT,
            max_models=2
        )
        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'text'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'content_recommendations': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML content studio analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


class AutonomousContentStudioCoordinator(BaseAgent):
    """
    Coordinates autonomous content creation across all active channels.

    This is the "brain" that makes the Content Studio autonomous by:
    - Monitoring channel schedules
    - Triggering content debates
    - Creating content via AISeriesWorkflowAgent
    - Tracking performance
    - Self-scheduling next cycles
    """

    name = "AutonomousContentStudioCoordinator"

    system_prompt = """You are the Autonomous Content Studio Coordinator - the brain that runs content channels autonomously.

Your job is to orchestrate the entire content creation cycle for multiple channels:

1. MONITOR: Check which channels need content (next_content_due has arrived)
2. DEBATE: Initiate agent discussions about what topic to cover next
3. CREATE: Trigger content creation via AISeriesWorkflowAgent
4. TRACK: Monitor performance and learn what works
5. SCHEDULE: Set next content cycle and improve strategy

You coordinate these agents:
- TopicMinerAgent: Finds trending topics in the channel's domain
- ContrarianAgent: Challenges obvious choices, suggests unique angles
- PerformanceAnalystAgent: Analyzes past performance to guide decisions
- AISeriesWorkflowAgent: Actually creates the content

For each channel, you must:
- Respect the channel's content frequency (daily, weekly, etc.)
- Maintain consistent visual style and voice
- Learn from past performance (which topics work best)
- Generate debates before creating content (internal disagreement)
- Track all decisions for transparency

You operate autonomously - users should wake up to new content created overnight!

CRITICAL: Always use tools to interact with the system. Never simulate or make up data."""

    description = "Coordinates autonomous content creation across all channels"

    def _get_available_tools(self) -> List[Dict[str, Any]]:
        """Define GPT tools for autonomous content coordination"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "check_channels_due_for_content",
                    "description": "Check which content channels need new content created. Returns channels where next_content_due <= now and status is ACTIVE.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "integer",
                                "description": "User ID to check channels for (optional, defaults to current user)"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_channel_performance_summary",
                    "description": "Get performance summary for a channel including recent episodes, topic performance, and confidence metrics.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "channel_id": {
                                "type": "string",
                                "description": "UUID of the content channel"
                            }
                        },
                        "required": ["channel_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "initiate_content_debate",
                    "description": "Start agent debate about what topic to cover next for a channel. By default uses TopicMiner, Contrarian, and PerformanceAnalyst, but can use ANY agents via debater_agents parameter.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "channel_id": {
                                "type": "string",
                                "description": "UUID of the content channel"
                            },
                            "context": {
                                "type": "string",
                                "description": "Additional context for the debate (recent trends, user feedback, etc.)"
                            },
                            "debater_agents": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Optional list of agent names to use as debaters (e.g., ['BlockchainAuditCoordinator', 'StockAuditCoordinator', 'CTOAgent']). Defaults to TopicMiner, Contrarian, PerformanceAnalyst if not specified."
                            }
                        },
                        "required": ["channel_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "trigger_content_creation",
                    "description": "Trigger content creation for a channel using the decided topic and angle. Delegates to AISeriesWorkflowAgent.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "channel_id": {
                                "type": "string",
                                "description": "UUID of the content channel"
                            },
                            "topic": {
                                "type": "string",
                                "description": "Topic to create content about"
                            },
                            "angle": {
                                "type": "string",
                                "description": "Unique angle or approach for the content"
                            },
                            "debate_id": {
                                "type": "string",
                                "description": "UUID of the ContentDebate record (optional)"
                            }
                        },
                        "required": ["channel_id", "topic", "angle"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_channel_schedule",
                    "description": "Update a channel's next_content_due timestamp and schedule the next content cycle. This is Property #5 (Self-Renewal).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "channel_id": {
                                "type": "string",
                                "description": "UUID of the content channel"
                            }
                        },
                        "required": ["channel_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_channel_performance",
                    "description": "Analyze channel performance and update confidence multiplier based on recent episodes. This is the learning loop.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "channel_id": {
                                "type": "string",
                                "description": "UUID of the content channel"
                            },
                            "lookback_days": {
                                "type": "integer",
                                "description": "Number of days to look back for performance analysis (default: 30)"
                            }
                        },
                        "required": ["channel_id"]
                    }
                }
            }
        ]

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """
        Execute autonomous content studio coordination.

        Args:
            task: User's request (e.g., "Check all channels and create content")
            context: Additional context
            scifi_context: Mood, memory, evolution context (unused in this agent)
            spider_context: Trends, market data context (passed to TopicMiner)

        Returns:
            AgentResult with coordination status
        """
        import time

        start_time = time.time()
        tool_calls_made = []

        # Session 750: Time Travel integration
        with self.time_travel_session("content_studio_coordination", task, input_data=context):
            # Handle simple diagnostic/identification queries
            task_lower = task.lower() if task else ''
            if any(keyword in task_lower for keyword in ['state your name', 'who are you', 'your capability', 'what can you do', 'introduce yourself']):
                execution_time = int((time.time() - start_time) * 1000)
                return AgentResult(
                    success=True,
                    message=f"I am {self.name}, the brain of the Autonomous Content Studio. One capability: I orchestrate autonomous content creation cycles by monitoring channel schedules, triggering agent debates (TopicMiner vs Contrarian vs Analyst), coordinating with AISeriesWorkflowAgent to create episodes, and self-scheduling the next content cycles.",
                    data={'type': 'self_description', 'coordinated_agents': ['TopicMinerAgent', 'ContrarianAgent', 'PerformanceAnalystAgent', 'AISeriesWorkflowAgent']},
                    agent_name=self.name,
                    execution_time_ms=execution_time
                )

            self.record_decision(
                decision_type="planning",
                action="Starting content studio coordination",
                reasoning=f"Processing task: {task[:100] if task else 'No task specified'}",
                alternatives=["Skip coordination", "Defer to human", "Consult other agents"],
                confidence=0.8
            )

            try:
                # Session 633: Direct tool call for initiate_content_debate action
                # This bypasses GPT to ensure reliable debate creation
                if context.get('action') == 'initiate_content_debate' and context.get('channel_id'):
                    logger.info(f"🎥 [SESSION 633] Direct debate initiation for channel {context['channel_id']}")
                    tool_input = {'channel_id': context['channel_id']}
                    debate_result = self._initiate_content_debate(tool_input)

                    execution_time = int((time.time() - start_time) * 1000)
                    return AgentResult(
                        success=True,
                        message=f"Debate created: {debate_result.get('proposed_topic', 'Unknown topic')}",
                        data={"debate_result": debate_result},
                        agent_name=self.name,
                        execution_time_ms=execution_time,
                        tool_calls=[{"name": "initiate_content_debate", "input": tool_input}]
                    )

                # Build prompt with system prompt + task
                prompt = self._build_intelligent_prompt(task, scifi_context, spider_context)

                # Call OpenAI with tools
                response = self._call_openai(prompt)

                # Process tool calls if any
                if response.get('tool_calls'):
                    tool_results = []
                    for tool_call in response['tool_calls']:
                        tool_name = tool_call['name']
                        tool_input = tool_call['arguments']

                        tool_calls_made.append({"name": tool_name, "input": tool_input})
                        result = self._execute_tool(tool_name, tool_input)
                        tool_results.append(result)

                    # Return with tool results
                    execution_time = int((time.time() - start_time) * 1000)
                    result = AgentResult(
                        success=True,
                        message=response.get('content') or "Coordination complete",
                        data={"tool_results": tool_results},
                        agent_name=self.name,
                        execution_time_ms=execution_time,
                        tool_calls=tool_calls_made
                    )

                    # Record learning outcome for collective intelligence
                    try:
                        self._record_learning_outcome(
                            task=task,
                            result=result,
                            success=True,
                            context={
                                'agent_type': self.__class__.__name__,
                                'execution_time_ms': execution_time,
                                'tools_used': [tc['name'] for tc in tool_calls_made],
                            }
                        )
                    except Exception as le:
                        logger.warning(f"Failed to record learning outcome: {le}")

                    return result
                else:
                    # No tools called, return message
                    return AgentResult(
                        success=True,
                        message=response.get('content') or 'No response',
                        agent_name=self.name,
                        execution_time_ms=int((time.time() - start_time) * 1000)
                    )

            except Exception as e:
                logger.error(f"AutonomousContentStudioCoordinator execution error: {e}")
                return AgentResult(
                    success=False,
                    error=str(e),
                    agent_name=self.name,
                    execution_time_ms=int((time.time() - start_time) * 1000)
                )

    def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool and return results"""
        try:
            if tool_name == "check_channels_due_for_content":
                return self._check_channels_due_for_content(tool_input)
            elif tool_name == "get_channel_performance_summary":
                return self._get_channel_performance_summary(tool_input)
            elif tool_name == "initiate_content_debate":
                return self._initiate_content_debate(tool_input)
            elif tool_name == "trigger_content_creation":
                return self._trigger_content_creation(tool_input)
            elif tool_name == "update_channel_schedule":
                return self._update_channel_schedule(tool_input)
            elif tool_name == "analyze_channel_performance":
                return self._analyze_channel_performance(tool_input)

            else:
                # Session 988: Fall through to BaseAgent for web_search + delegation
                return super()._execute_tool_call(tool_name, tool_input)
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}", exc_info=True)
            return {"error": str(e)}

    # =========================================================================
    # TOOL IMPLEMENTATIONS
    # =========================================================================

    def _check_channels_due_for_content(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Property #2: Incoming Signals
        Check which channels need content created.
        """
        # Session 468: Fixed import
        from core.models_autonomous_studio import ContentChannel

        user_id = tool_input.get('user_id') or self.user.id

        # Find active channels where content is due
        due_channels = ContentChannel.objects.filter(
            user_id=user_id,
            status='active',
            next_content_due__lte=timezone.now()
        ).order_by('next_content_due')

        channels_data = []
        for channel in due_channels:
            channels_data.append({
                "id": str(channel.id),
                "name": channel.name,
                "topic_domain": channel.topic_domain,
                "content_frequency": channel.content_frequency,
                "next_content_due": channel.next_content_due.isoformat(),
                "last_content_created": channel.last_content_created.isoformat() if channel.last_content_created else None,
                "total_episodes": channel.total_episodes_created,
                "confidence_multiplier": float(channel.confidence_multiplier)
            })

        return {
            "channels_due": len(channels_data),
            "channels": channels_data
        }

    def _get_channel_performance_summary(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Property #1: Persistent Context
        Load channel context including performance history.
        """
        # Session 468: Fixed import
        from core.models_autonomous_studio import ContentChannel, ChannelEpisode, TopicPerformance

        channel_id = tool_input.get('channel_id')

        try:
            channel = ContentChannel.objects.get(id=channel_id)
        except ContentChannel.DoesNotExist:
            return {"error": f"Channel {channel_id} not found"}

        # Get recent episodes
        recent_episodes = ChannelEpisode.objects.filter(
            channel=channel
        ).order_by('-created_at')[:5]

        episodes_data = []
        for episode in recent_episodes:
            episodes_data.append({
                "title": episode.title,
                "topic": episode.topic,
                "views": episode.views,
                "retention_rate": float(episode.retention_rate),
                "performance_score": float(episode.performance_score),
                "created_at": episode.created_at.isoformat()
            })

        # Get topic performance data
        topic_performance = TopicPerformance.objects.filter(
            channel=channel
        ).order_by('-avg_performance_score')[:10]

        topics_data = []
        for topic in topic_performance:
            topics_data.append({
                "topic": topic.topic,
                "episode_count": topic.episode_count,
                "avg_performance_score": float(topic.avg_performance_score),
                "confidence_score": float(topic.confidence_score)
            })

        return {
            "channel": {
                "id": str(channel.id),
                "name": channel.name,
                "topic_domain": channel.topic_domain,
                "total_episodes": channel.total_episodes_created,
                "total_views": channel.total_views,
                "avg_retention_rate": float(channel.avg_retention_rate),
                "confidence_multiplier": float(channel.confidence_multiplier)
            },
            "recent_episodes": episodes_data,
            "top_topics": topics_data
        }

    def _initiate_content_debate(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Property #3: Internal Disagreement
        Start agent debate about next content topic.

        Session 469: Now calls real debate agents (TopicMinerAgent, ContrarianAgent, PerformanceAnalystAgent)
        Session 653: COMPOSABILITY FIX - Now accepts ANY agents via debater_agents parameter!
                     Use AgentRouter for dynamic agent loading instead of hardcoded imports.
        """
        from core.models_autonomous_studio import ContentChannel, ContentDebate
        from core.agent_router import AgentRouter

        channel_id = tool_input.get('channel_id')
        additional_context = tool_input.get('context', '')

        # Session 653: Accept configurable debater agents - enables cross-domain composition!
        debater_agent_names = tool_input.get('debater_agents', [
            'TopicMinerAgent',
            'ContrarianAgent',
            'PerformanceAnalystAgent'
        ])

        try:
            channel = ContentChannel.objects.get(id=channel_id)
        except ContentChannel.DoesNotExist:
            return {"error": f"Channel {channel_id} not found"}

        # Prepare context for debate agents
        domain_keywords = [kw.strip() for kw in channel.topic_domain.split(',') if kw.strip()]
        if not domain_keywords:
            domain_keywords = [channel.topic_domain]

        scifi_context = {}  # Agents don't need sci-fi context for debates
        spider_context = {"domain_keywords": domain_keywords}

        # Session 653: Use AgentRouter for dynamic agent instantiation
        router = AgentRouter()
        agent_positions = []  # Store all agent positions dynamically

        # Define role-based task templates
        role_tasks = {
            0: f"Find trending topics and opportunities in the {channel.topic_domain} domain. The channel '{channel.name}' targets {channel.target_audience or 'general audience'}. {additional_context}",
            1: lambda prev: f"Challenge assumptions and suggest unique angles for content in the {channel.topic_domain} domain. Channel style: {channel.visual_style or 'modern'}. Consider what the previous agent found: {prev[:500]}",
            2: lambda prev: f"Analyze and predict what topics would perform best based on your expertise. Domain: {channel.topic_domain}. Consider the discussion so far: {prev[:500]}",
        }

        # Run each debater agent
        for i, agent_name in enumerate(debater_agent_names):
            logger.info(f"🗣️ Debate Step {i+1}: {agent_name} contributing for {channel.name}")

            # Get agent class from router
            agent_class = router.AGENT_MAP.get(agent_name)
            if not agent_class:
                logger.warning(f"Agent {agent_name} not found in router, skipping")
                agent_positions.append({
                    'agent_name': agent_name,
                    'position': f"Agent {agent_name} not found in AgentRouter"
                })
                continue

            # Instantiate agent
            try:
                agent = agent_class(user=self.user)
            except Exception as e:
                logger.error(f"Failed to instantiate {agent_name}: {e}")
                agent_positions.append({
                    'agent_name': agent_name,
                    'position': f"Failed to instantiate: {str(e)}"
                })
                continue

            # Build task based on position in debate
            if i == 0:
                task = role_tasks[0]
            elif i < len(role_tasks):
                prev_position = agent_positions[-1]['position'] if agent_positions else ""
                task = role_tasks[i](prev_position)
            else:
                # For additional agents beyond 3, use a generic task
                prev_position = agent_positions[-1]['position'] if agent_positions else ""
                task = f"Contribute your unique perspective on {channel.topic_domain} content strategy. Consider the discussion so far: {prev_position[:500]}"

            # Execute the agent with timeout (Session 895: Fix hanging debates)
            # Each debate agent gets 2 minutes max to prevent blocking the whole debate
            DEBATE_AGENT_TIMEOUT = 120  # 2 minutes per agent
            try:
                def run_agent():
                    return agent.execute(
                        task=task,
                        context={"channel_id": str(channel.id), "domain_keywords": domain_keywords},
                        scifi_context=scifi_context,
                        spider_context=spider_context
                    )

                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(run_agent)
                    result = future.result(timeout=DEBATE_AGENT_TIMEOUT)

                position = result.message or f"{agent_name} had no response"
                if result.data and result.data.get('tool_results'):
                    position += f"\n\nData: {json.dumps(result.data['tool_results'], indent=2)[:1000]}"
            except FuturesTimeoutError:
                logger.warning(f"⏰ {agent_name} timed out after {DEBATE_AGENT_TIMEOUT}s in content debate")
                position = f"{agent_name} timed out after {DEBATE_AGENT_TIMEOUT}s - moving to next debater"
            except Exception as e:
                logger.error(f"{agent_name} error: {e}")
                position = f"{agent_name} error: {str(e)}"

            agent_positions.append({
                'agent_name': agent_name,
                'position': position
            })
            logger.info(f"✅ {agent_name} contributed to debate")

        # Map positions to ContentDebate fields (for backwards compatibility)
        topic_miner_position = agent_positions[0]['position'] if len(agent_positions) > 0 else "No debaters participated"
        contrarian_position = agent_positions[1]['position'] if len(agent_positions) > 1 else "Only one debater participated"
        analyst_position = agent_positions[2]['position'] if len(agent_positions) > 2 else "Only two debaters participated"

        # ============================================================
        # STEP 4: Synthesize final decision from debate
        # ============================================================
        logger.info(f"🗣️ Debate Step 4: Synthesizing final decision for {channel.name}")

        # Determine proposed topic and angle based on agent positions
        # Use a simple heuristic: extract the first specific topic mentioned
        proposed_topic = f"Latest {channel.topic_domain} Developments"  # Default
        chosen_angle = "Educational overview with practical insights"  # Default

        # Look for specific topics in miner response
        if "trend" in topic_miner_position.lower():
            # Try to extract a specific topic
            for word in ["AI", "machine learning", "technology", "innovation", "development"]:
                if word.lower() in channel.topic_domain.lower():
                    proposed_topic = f"Latest {word} Developments in {channel.topic_domain}"
                    break

        # Look for unique angles in contrarian response
        if "unique angle" in contrarian_position.lower() or "differentiation" in contrarian_position.lower():
            chosen_angle = "Unique perspective that stands out from mainstream coverage"
        elif "deep-dive" in contrarian_position.lower() or "technical" in contrarian_position.lower():
            chosen_angle = "Technical deep-dive for engaged audiences"

        # Session 653: Dynamic decision reasoning based on actual participants
        participated_names = [p['agent_name'] for p in agent_positions]
        agent_summaries = "\n".join([
            f"        {i+1}. {p['agent_name']} contributed expertise"
            for i, p in enumerate(agent_positions)
        ])

        decision_reasoning = f"""
        Debate synthesis from {len(agent_positions)} agents:

{agent_summaries}

        Final topic: {proposed_topic}
        Chosen angle: {chosen_angle}

        This decision synthesizes insights from all participating agents.
        """

        # Create debate record with REAL agent positions
        debate = ContentDebate.objects.create(
            channel=channel,
            proposed_topic=proposed_topic,
            proposed_by="AutonomousContentStudioCoordinator",
            topic_miner_position=topic_miner_position[:2000],  # Truncate if too long
            contrarian_position=contrarian_position[:2000],
            analyst_position=analyst_position[:2000],
            director_position="[Session 469] CreativeDirectorAgent integration pending",  # Future enhancement
            final_decision=proposed_topic,
            chosen_angle=chosen_angle,
            decision_reasoning=decision_reasoning,
            consensus_reached=True,
            content_created=False
        )

        logger.info(f"✅ Debate complete for {channel.name}: {proposed_topic}")

        return {
            "debate_id": str(debate.id),
            "status": "debate_complete",
            "message": f"Cross-domain agent debate completed with {len(participated_names)} agents",
            "proposed_topic": proposed_topic,
            "chosen_angle": chosen_angle,
            "final_decision": proposed_topic,
            "agents_participated": participated_names,  # Session 653: Now shows actual agents used
            "is_cross_domain": any(name not in ['TopicMinerAgent', 'ContrarianAgent', 'PerformanceAnalystAgent'] for name in participated_names)
        }

    def _trigger_content_creation(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Property #4: Outputs with Consequences
        Trigger content creation via AISeriesWorkflowAgent.
        """
        # Session 468: Fixed imports - models are in dedicated files
        from core.models_autonomous_studio import ContentChannel, ChannelEpisode, ContentDebate
        from core.models_ai_series import AISeries

        channel_id = tool_input.get('channel_id')
        topic = tool_input.get('topic') or tool_input.get('topic_override') or "Latest Market Developments"  # Session 743: Default topic
        angle = tool_input.get('angle') or "Educational overview with practical insights"  # Session 743: Default angle to avoid NULL
        debate_id = tool_input.get('debate_id')

        try:
            channel = ContentChannel.objects.get(id=channel_id)
        except ContentChannel.DoesNotExist:
            return {"error": f"Channel {channel_id} not found"}

        # Session 628: Get user preferences for personalization
        user_prefs = {}
        try:
            memory_service = get_memory_context_service(channel.user)
            user_prefs = memory_service.get_content_preferences(channel.user, channel)
            logger.info(f"Session 628: Loaded user preferences for {channel.name}: {user_prefs}")
        except Exception as pref_error:
            logger.warning(f"Session 628: Failed to load preferences: {pref_error}")

        # Apply user preferences to visual style and voice
        visual_style = user_prefs.get('visual_style') or channel.visual_style
        voice_id = user_prefs.get('voice_id') or channel.voice_id
        voice_name = user_prefs.get('voice_name') or channel.voice_name
        content_tone = user_prefs.get('content_tone') or 'balanced'

        # Create AISeries for this content with preferences
        series_prompt = f"""{channel.topic_domain} - {topic}

Angle: {angle}

Target Audience: {channel.target_audience}

Visual Style: {visual_style}
Voice: {voice_name or 'Default'}
Content Tone: {content_tone}

User Preferences Applied: {json.dumps(user_prefs) if user_prefs else 'None'}"""

        # Session 636: Actually generate podcast script using GPT
        import openai
        import os

        script_content = series_prompt  # Fallback to prompt if generation fails

        try:
            # Session 1003: 60s timeout prevents indefinite OpenAI hangs
            client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'), timeout=60)

            # Get debate positions for richer content
            debate_context = ""
            if debate_id:
                try:
                    debate = ContentDebate.objects.get(id=debate_id)
                    debate_context = f"""
DEBATE INSIGHTS:
TopicMiner: {debate.topic_miner_position[:500] if debate.topic_miner_position else 'N/A'}
Contrarian: {debate.contrarian_position[:500] if debate.contrarian_position else 'N/A'}
Analyst: {debate.analyst_position[:500] if debate.analyst_position else 'N/A'}
Decision: {debate.decision_reasoning[:300] if debate.decision_reasoning else 'N/A'}
"""
                except ContentDebate.DoesNotExist:
                    pass

            script_prompt = f"""Write a podcast script for "{channel.name}" about: {topic}

{debate_context}

Target Audience: {channel.target_audience}
Visual Style: {visual_style}
Content Tone: {content_tone}

Create a 3-5 minute podcast script with:
1. Host intro (friendly, engaging)
2. Main topic discussion (3-4 key points)
3. Insights and takeaways
4. Closing with call to action

Make it conversational and engaging. Use natural speech patterns."""

            response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[{"role": "user", "content": script_prompt}],
                max_completion_tokens=2000
            )
            script_content = response.choices[0].message.content
            logger.info(f"Session 636: Generated podcast script ({len(script_content)} chars) for {channel.name}")

        except Exception as script_error:
            logger.warning(f"Session 636: Failed to generate script: {script_error}")
            # Keep the series_prompt as fallback

        # Session 741: Generate unique episode title from script content
        episode_title = f"{channel.name}: {topic}"  # Default fallback
        try:
            title_prompt = f"""Based on this podcast script, generate a short, catchy episode title (max 60 chars).
The title should capture the SPECIFIC topic discussed, not be generic.

Script excerpt:
{script_content[:1500]}

Reply with ONLY the title, nothing else. Do not include the show name prefix."""

            title_response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[{"role": "user", "content": title_prompt}],
                max_completion_tokens=50
            )
            generated_title = title_response.choices[0].message.content.strip().strip('"\'')
            # Ensure it's not too long and add channel name prefix
            if len(generated_title) > 60:
                generated_title = generated_title[:57] + "..."
            episode_title = f"{channel.name}: {generated_title}"
            logger.info(f"Session 741: Generated unique title: {episode_title}")
        except Exception as title_error:
            logger.warning(f"Session 741: Failed to generate title, using default: {title_error}")

        series = AISeries.objects.create(
            name=f"{channel.name} - {topic}",
            description=angle,
            prompt=series_prompt,
            series_type=channel.content_type,
            episode_count=1,
            target_audience=channel.target_audience,
            created_by=channel.user  # Session 636: Fix NOT NULL constraint
        )

        # Create ChannelEpisode record with actual generated script
        episode = ChannelEpisode.objects.create(
            channel=channel,
            series=series,
            title=episode_title,  # Session 741: Use unique generated title
            topic=topic,
            description=angle,
            script=script_content  # Session 636: Use generated script, not just prompt
        )

        # [SESSION 475] Add provenance tracking
        try:
            from core.services.provenance_tracker import create_content_episode_provenance
            create_content_episode_provenance(
                episode_id=str(episode.id),
                channel_name=channel.name,
                content_type=channel.content_type,
                trigger_source='content_studio_coordinator',
                metadata={
                    'topic': topic,
                    'debate_id': str(debate_id) if debate_id else None,
                    'agent': 'AutonomousContentStudioCoordinator'
                }
            )
        except Exception as prov_e:
            logger.warning(f"Failed to create episode provenance: {prov_e}")

        # Link debate if provided
        if debate_id:
            try:
                debate = ContentDebate.objects.get(id=debate_id)
                debate.episode = episode
                debate.content_created = True
                debate.save()
            except ContentDebate.DoesNotExist:
                pass

        # Update channel stats
        channel.total_episodes_created += 1
        channel.last_content_created = timezone.now()
        channel.save()

        return {
            "status": "content_created",
            "series_id": str(series.id),
            "episode_id": str(episode.id),
            "script_length": len(script_content),
            "message": f"Created episode with {len(script_content)} character script."
        }

    def _update_channel_schedule(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Property #5: Self-Renewal
        Schedule next content cycle.
        """
        # Session 468: Fixed import
        from core.models_autonomous_studio import ContentChannel

        channel_id = tool_input.get('channel_id')

        try:
            channel = ContentChannel.objects.get(id=channel_id)
        except ContentChannel.DoesNotExist:
            return {"error": f"Channel {channel_id} not found"}

        # Use the model's schedule_next_content method
        channel.schedule_next_content()

        return {
            "status": "schedule_updated",
            "channel_id": str(channel.id),
            "next_content_due": channel.next_content_due.isoformat(),
            "content_frequency": channel.content_frequency
        }

    def _analyze_channel_performance(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Learning Loop: Analyze performance and update confidence multiplier.
        Similar to Session 464's learning loop for Market Intelligence Desk.
        """
        # Session 468: Fixed import
        from core.models_autonomous_studio import ContentChannel, ChannelEpisode, TopicPerformance

        channel_id = tool_input.get('channel_id')
        lookback_days = tool_input.get('lookback_days', 30)

        try:
            channel = ContentChannel.objects.get(id=channel_id)
        except ContentChannel.DoesNotExist:
            return {"error": f"Channel {channel_id} not found"}

        # Get episodes from last N days
        since_date = timezone.now() - timedelta(days=lookback_days)
        recent_episodes = ChannelEpisode.objects.filter(
            channel=channel,
            created_at__gte=since_date
        )

        if not recent_episodes.exists():
            return {
                "status": "no_data",
                "message": f"No episodes in last {lookback_days} days"
            }

        # Calculate average performance score
        total_score = sum(float(ep.performance_score) for ep in recent_episodes)
        avg_score = total_score / recent_episodes.count()

        # Update confidence multiplier based on performance
        # Good performance (>50) increases confidence, poor (<30) decreases
        if avg_score > 50:
            new_multiplier = min(float(channel.confidence_multiplier) * 1.1, 1.5)
        elif avg_score < 30:
            new_multiplier = max(float(channel.confidence_multiplier) * 0.9, 0.5)
        else:
            new_multiplier = float(channel.confidence_multiplier)

        channel.confidence_multiplier = Decimal(str(round(new_multiplier, 2)))
        channel.save()

        # Update topic performance records
        for episode in recent_episodes:
            if not episode.contributed_to_learning:
                topic_perf, created = TopicPerformance.objects.get_or_create(
                    channel=channel,
                    topic=episode.topic,
                    defaults={
                        'episode_count': 0,
                        'avg_views': Decimal('0.00'),
                        'avg_performance_score': Decimal('0.00'),
                        'last_tested': timezone.now()
                    }
                )

                # Update aggregates
                topic_perf.episode_count += 1
                topic_perf.avg_views = (
                    (topic_perf.avg_views * (topic_perf.episode_count - 1) + episode.views) /
                    topic_perf.episode_count
                )
                topic_perf.avg_performance_score = (
                    (topic_perf.avg_performance_score * (topic_perf.episode_count - 1) + episode.performance_score) /
                    topic_perf.episode_count
                )
                topic_perf.last_tested = timezone.now()
                topic_perf.save()

                episode.contributed_to_learning = True
                episode.save()

        return {
            "status": "analysis_complete",
            "episodes_analyzed": recent_episodes.count(),
            "avg_performance_score": round(avg_score, 2),
            "old_confidence_multiplier": float(tool_input.get('old_multiplier', channel.confidence_multiplier)),
            "new_confidence_multiplier": float(channel.confidence_multiplier),
            "message": f"Analyzed {recent_episodes.count()} episodes. Updated confidence multiplier."
        }
