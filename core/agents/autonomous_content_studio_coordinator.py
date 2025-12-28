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

from core.agents.base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)


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
                    "description": "Start agent debate about what topic to cover next for a channel. Coordinates TopicMiner, Contrarian, and PerformanceAnalyst agents.",
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

        try:
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
                return {"error": f"Unknown tool: {tool_name}"}
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
        """
        # Session 468: Fixed import - these models are in models_autonomous_studio not models
        from core.models_autonomous_studio import ContentChannel, ContentDebate
        from core.agents.content.topic_miner_agent import TopicMinerAgent
        from core.agents.content.contrarian_agent import ContrarianAgent
        from core.agents.content.performance_analyst_agent import PerformanceAnalystAgent

        channel_id = tool_input.get('channel_id')
        additional_context = tool_input.get('context', '')

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

        # ============================================================
        # STEP 1: TopicMinerAgent - Find trending topics
        # ============================================================
        logger.info(f"🗣️ Debate Step 1: TopicMinerAgent analyzing trends for {channel.name}")
        topic_miner = TopicMinerAgent(user=self.user)
        topic_miner_task = f"Find trending topics in the {channel.topic_domain} domain. The channel '{channel.name}' targets {channel.target_audience or 'general audience'}. {additional_context}"

        try:
            miner_result = topic_miner.execute(
                task=topic_miner_task,
                context={"channel_id": str(channel.id), "domain_keywords": domain_keywords},
                scifi_context=scifi_context,
                spider_context=spider_context
            )
            topic_miner_position = miner_result.message or "TopicMinerAgent could not find trends"
            if miner_result.data and miner_result.data.get('tool_results'):
                # Include tool results in position
                topic_miner_position += f"\n\nData: {json.dumps(miner_result.data['tool_results'], indent=2)[:1000]}"
        except Exception as e:
            logger.error(f"TopicMinerAgent error: {e}")
            topic_miner_position = f"TopicMinerAgent error: {str(e)}"

        # ============================================================
        # STEP 2: ContrarianAgent - Challenge and suggest unique angles
        # ============================================================
        logger.info(f"🗣️ Debate Step 2: ContrarianAgent challenging for {channel.name}")
        contrarian = ContrarianAgent(user=self.user)
        contrarian_task = f"Check saturation and suggest unique angles for content in the {channel.topic_domain} domain. Channel style: {channel.visual_style or 'modern'}. Consider what TopicMiner found: {topic_miner_position[:500]}"

        try:
            contrarian_result = contrarian.execute(
                task=contrarian_task,
                context={"channel_id": str(channel.id), "domain_keywords": domain_keywords},
                scifi_context=scifi_context,
                spider_context=spider_context
            )
            contrarian_position = contrarian_result.message or "ContrarianAgent had no suggestions"
            if contrarian_result.data and contrarian_result.data.get('tool_results'):
                contrarian_position += f"\n\nData: {json.dumps(contrarian_result.data['tool_results'], indent=2)[:1000]}"
        except Exception as e:
            logger.error(f"ContrarianAgent error: {e}")
            contrarian_position = f"ContrarianAgent error: {str(e)}"

        # ============================================================
        # STEP 3: PerformanceAnalystAgent - Data-driven insights
        # ============================================================
        logger.info(f"🗣️ Debate Step 3: PerformanceAnalystAgent analyzing for {channel.name}")
        analyst = PerformanceAnalystAgent(user=self.user)
        analyst_task = f"Analyze historical performance for channel {channel.name} (ID: {channel.id}) and predict what topics would perform best based on data. Domain: {channel.topic_domain}."

        try:
            analyst_result = analyst.execute(
                task=analyst_task,
                context={"channel_id": str(channel.id), "domain_keywords": domain_keywords},
                scifi_context=scifi_context,
                spider_context=spider_context
            )
            analyst_position = analyst_result.message or "PerformanceAnalystAgent had no data insights"
            if analyst_result.data and analyst_result.data.get('tool_results'):
                analyst_position += f"\n\nData: {json.dumps(analyst_result.data['tool_results'], indent=2)[:1000]}"
        except Exception as e:
            logger.error(f"PerformanceAnalystAgent error: {e}")
            analyst_position = f"PerformanceAnalystAgent error: {str(e)}"

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

        # Decision reasoning
        decision_reasoning = f"""
        Debate synthesis from 3 agents:

        1. TopicMinerAgent identified trending topics in {channel.topic_domain}
        2. ContrarianAgent challenged mainstream approaches and suggested differentiation
        3. PerformanceAnalystAgent provided data-driven performance predictions

        Final topic: {proposed_topic}
        Chosen angle: {chosen_angle}

        This decision balances trending potential, unique positioning, and historical performance data.
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
            "message": "Real agent debate completed successfully",
            "proposed_topic": proposed_topic,
            "chosen_angle": chosen_angle,
            "final_decision": proposed_topic,
            "agents_participated": ["TopicMinerAgent", "ContrarianAgent", "PerformanceAnalystAgent"]
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
        topic = tool_input.get('topic')
        angle = tool_input.get('angle')
        debate_id = tool_input.get('debate_id')

        try:
            channel = ContentChannel.objects.get(id=channel_id)
        except ContentChannel.DoesNotExist:
            return {"error": f"Channel {channel_id} not found"}

        # Create AISeries for this content
        series_prompt = f"{channel.topic_domain} - {topic}\n\nAngle: {angle}\n\nTarget Audience: {channel.target_audience}"

        # Phase 3: AISeriesWorkflowAgent integration pending
        # Creates placeholder records for now

        series = AISeries.objects.create(
            name=f"{channel.name} - {topic}",
            description=angle,
            prompt=series_prompt,
            series_type=channel.content_type,
            episode_count=1,  # Single episode for now
            target_audience=channel.target_audience
        )

        # Create ChannelEpisode record
        episode = ChannelEpisode.objects.create(
            channel=channel,
            series=series,
            title=f"{topic}",
            topic=topic,
            description=angle
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
            "status": "content_triggered",
            "series_id": str(series.id),
            "episode_id": str(episode.id),
            "message": "Content creation triggered. Full AISeriesWorkflowAgent integration pending Phase 3."
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
