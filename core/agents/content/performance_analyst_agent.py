"""
Performance Analyst Agent - Session 466

Part of Autonomous Content Studio debate system (Property #3: Internal Disagreement).

This agent uses historical performance data to guide content decisions:
1. Analyzes which topics performed well in the past
2. Identifies patterns in successful content
3. Predicts performance based on historical data
4. Provides confidence scores based on evidence

Works alongside:
- TopicMinerAgent (proposes trending topics)
- ContrarianAgent (suggests unique angles)

The data-driven view ensures decisions are based on what actually works.
"""

import logging
from typing import Dict, Any, List

from core.agents.base_agent import BaseAgent, AgentResult
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


def predict_performance_with_ml(performance_data: dict) -> dict:
    """Predict content performance using ML models (LSTM time series)."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()

        # Use TIME_SERIES task type for performance prediction
        result = router.auto_route(
            data=performance_data,
            task_hint=TaskType.TIME_SERIES,
            max_models=2
        )

        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'time_series'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'performance_prediction': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML performance prediction failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


class PerformanceAnalystAgent(BaseAgent):
    """
    Analyzes historical performance data to guide content decisions.

    This agent argues based on DATA:
    - "Our audience prefers X topics (70% higher engagement)"
    - "Similar topics got Y views on average"
    - "This topic type has Z% success rate"
    """

    name = "PerformanceAnalystAgent"

    system_prompt = """You are the Performance Analyst Agent - you analyze content performance data to guide decisions.

Your job is to:
1. ANALYZE HISTORY - What worked before for this channel/show
2. IDENTIFY PATTERNS - Which topic types perform best
3. PREDICT PERFORMANCE - Estimate how a proposed topic will do
4. PROVIDE CONFIDENCE - How sure are we based on data

WORKFLOW:
1. For PODCAST analysis:
   - Use list_podcast_shows to see what podcast shows exist
   - Use get_podcast_performance to analyze episode metrics
   - Focus on: listens, duration, topic patterns, debate quality

2. For CONTENT CHANNEL analysis:
   - Use list_available_channels to see what channels exist
   - If no channel_id provided, analyze the most active channel
   - Use get_topic_performance_history, get_success_patterns, predict_topic_performance

3. Compile findings into a detailed, structured report

You argue based on EVIDENCE, not opinions:
- "Topic X historically gets 30% more views"
- "Our top 5 videos all had Y characteristic"
- "Audience retention is 50% higher for Z format"
- "We have high confidence because we've tested this 10 times"

IMPORTANT: If you find NO DATA (zero episodes, zero metrics):
- Say so EXPLICITLY with a warning
- Explain what data is missing
- Recommend how to generate the data
- Do NOT generate stub/placeholder reports

You're the voice of reason - neither blindly trendy nor contrarian, just data-driven.
Always use tools to get real performance data. Never make up statistics."""

    description = "Analyzes historical performance to guide content decisions"

    def _get_available_tools(self) -> List[Dict[str, Any]]:
        """Define GPT tools for performance analysis"""
        return [
            # Session 851: Podcast-specific tools
            {
                "type": "function",
                "function": {
                    "name": "get_podcast_performance",
                    "description": "Get performance analytics for podcast episodes. Use this when analyzing podcast content performance.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "show_id": {
                                "type": "string",
                                "description": "UUID of the podcast show (optional - returns all if not provided)"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of episodes to analyze (default: 10)"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_podcast_shows",
                    "description": "List all podcast shows in the system with their episode counts and listen stats.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_available_channels",
                    "description": "List all available content channels in the system. Use this first if no channel_id is provided to discover what channels exist.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of channels to return (default: 10)"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_topic_performance_history",
                    "description": "Get historical performance data for topics similar to the proposed one. Shows what worked before.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "channel_id": {
                                "type": "string",
                                "description": "UUID of the content channel"
                            },
                            "topic_keywords": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Keywords to match against historical topics"
                            }
                        },
                        "required": ["channel_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "predict_topic_performance",
                    "description": "Predict how a topic will perform based on historical data and patterns.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "channel_id": {
                                "type": "string",
                                "description": "UUID of the content channel"
                            },
                            "topic": {
                                "type": "string",
                                "description": "Topic to predict performance for"
                            }
                        },
                        "required": ["channel_id", "topic"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_success_patterns",
                    "description": "Identify patterns in the channel's most successful content (what makes content work).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "channel_id": {
                                "type": "string",
                                "description": "UUID of the content channel"
                            },
                            "top_n": {
                                "type": "integer",
                                "description": "How many top episodes to analyze (default: 10)"
                            }
                        },
                        "required": ["channel_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate_confidence_score",
                    "description": "Calculate confidence score for a recommendation based on amount of supporting data.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "channel_id": {
                                "type": "string",
                                "description": "UUID of the content channel"
                            },
                            "topic": {
                                "type": "string",
                                "description": "Topic to calculate confidence for"
                            }
                        },
                        "required": ["channel_id", "topic"]
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
        Execute performance analysis based on historical data.

        Args:
            task: User's request (e.g., "Predict performance for this topic")
            context: Additional context (channel_id, topic, etc.)
            scifi_context: Mood, memory, evolution context
            spider_context: Trends from spider network

        Returns:
            AgentResult with performance predictions
        """
        import time

        start_time = time.time()
        tool_calls_made = []

        # Session 750: Time Travel integration
        with self.time_travel_session("performance_analysis", task, input_data=context):
            self.record_decision(
                decision_type="analysis",
                action="Starting performance analysis",
                reasoning=f"Processing task: {task[:100] if task else 'No task specified'}",
                alternatives=["Skip analysis", "Defer to human", "Consult other agents"],
                confidence=0.8
            )

            # Session 736: Extract spider intelligence for real-time data
            spider_intel = self._extract_spider_intelligence(spider_context)
            if spider_intel['has_data']:
                logger.info(f"🕷️ {self.name} using spider intelligence")

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

                    # Synthesize tool results into actual analysis
                    analysis = self._synthesize_tool_results(tool_calls_made, tool_results, task)
                    message = analysis or response.get('content') or "Performance analysis complete"

                    execution_time_ms = int((time.time() - start_time) * 1000)
                    result = AgentResult(
                        success=True,
                        message=message,
                        data={"tool_results": tool_results, "full_text": message},
                        agent_name=self.name,
                        execution_time_ms=execution_time_ms,
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
                                'execution_time_ms': execution_time_ms,
                                'tools_used': [tc['name'] for tc in tool_calls_made],
                                'analyses_performed': len(tool_results),
                            }
                        )
                    except Exception as e:
                        logger.warning(f"Failed to record learning outcome: {e}")

                    if len(message) > 100:
                        self._save_to_deliverable(
                            title=f"Performance Analysis: {task[:80]}",
                            content=message,
                            deliverable_type='analysis',
                            category='Performance Analysis',
                            tags=['performance', 'content'],
                            metadata={'task': task[:200]},
                        )

                    return result
                else:
                    # No tools called, return content
                    execution_time_ms = int((time.time() - start_time) * 1000)
                    result = AgentResult(
                        success=True,
                        message=response.get('content') or 'No response',
                        agent_name=self.name,
                        execution_time_ms=execution_time_ms
                    )

                    # Record learning outcome
                    try:
                        self._record_learning_outcome(
                            task=task,
                            result=result,
                            success=True,
                            context={
                                'agent_type': self.__class__.__name__,
                                'execution_time_ms': execution_time_ms,
                            }
                        )
                    except Exception as e:
                        logger.warning(f"Failed to record learning outcome: {e}")

                    return result

            except Exception as e:
                logger.error(f"PerformanceAnalystAgent execution error: {e}")
                execution_time_ms = int((time.time() - start_time) * 1000)
                result = AgentResult(
                    success=False,
                    error=str(e),
                    agent_name=self.name,
                    execution_time_ms=execution_time_ms
                )

                # Record failed learning outcome
                try:
                    self._record_learning_outcome(
                        task=task,
                        result=result,
                        success=False,
                        context={
                            'agent_type': self.__class__.__name__,
                            'execution_time_ms': execution_time_ms,
                            'error': str(e),
                        }
                    )
                except Exception as le:
                    logger.warning(f"Failed to record learning outcome: {le}")

                return result

    def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool and return results"""
        try:
            # Session 851: Podcast-specific tools
            if tool_name == "get_podcast_performance":
                return self._get_podcast_performance(tool_input)
            elif tool_name == "list_podcast_shows":
                return self._list_podcast_shows(tool_input)
            elif tool_name == "list_available_channels":
                return self._list_available_channels(tool_input)
            elif tool_name == "get_topic_performance_history":
                return self._get_topic_performance_history(tool_input)
            elif tool_name == "predict_topic_performance":
                return self._predict_topic_performance(tool_input)
            elif tool_name == "get_success_patterns":
                return self._get_success_patterns(tool_input)
            elif tool_name == "calculate_confidence_score":
                return self._calculate_confidence_score(tool_input)
            else:
                # Session 1002C: Fall through to BaseAgent for web_search, spider_query, delegation
                return super()._execute_tool_call(tool_name, tool_input)
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}", exc_info=True)
            return {"error": str(e)}

    # =========================================================================
    # TOOL IMPLEMENTATIONS
    # =========================================================================

    # -------------------------------------------------------------------------
    # Session 851: Podcast-specific tools
    # -------------------------------------------------------------------------

    def _list_podcast_shows(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """List all podcast shows with their stats."""
        from core.models_podcast_studio import PodcastShow, PodcastEpisode

        shows = PodcastShow.objects.all().order_by('-episode_count')

        if not shows.exists():
            # Check if there are orphaned episodes without shows
            orphaned_episodes = PodcastEpisode.objects.filter(show__isnull=True)
            orphaned_count = orphaned_episodes.count()

            if orphaned_count > 0:
                logger.warning(f"⚠️ Found {orphaned_count} podcast episodes without shows!")
                return {
                    "shows_found": 0,
                    "warning": f"{orphaned_count} podcast episodes exist but have no associated show",
                    "orphaned_episodes": [
                        {
                            "id": str(ep.id),
                            "title": ep.title,
                            "topic": ep.topic,
                            "status": ep.status,
                            "listen_count": ep.listen_count,
                        }
                        for ep in orphaned_episodes[:10]
                    ],
                    "recommendation": "Create a PodcastShow and link these episodes to it"
                }

            return {
                "shows_found": 0,
                "message": "No podcast shows found in the system",
                "shows": []
            }

        show_list = []
        for show in shows:
            # Get episode stats
            episodes = PodcastEpisode.objects.filter(show=show)
            completed_episodes = episodes.filter(status='complete')
            total_listens = sum(ep.listen_count for ep in completed_episodes)

            show_list.append({
                "id": str(show.id),
                "name": show.name,
                "format": show.format,
                "episode_count": show.episode_count,
                "completed_episodes": completed_episodes.count(),
                "total_listens": total_listens,
                "avg_listens": total_listens / max(completed_episodes.count(), 1),
            })

        return {
            "shows_found": len(show_list),
            "shows": show_list,
        }

    def _get_podcast_performance(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Get performance analytics for podcast episodes."""
        from core.models_podcast_studio import PodcastShow, PodcastEpisode, PodcastDebate

        show_id = tool_input.get('show_id')
        limit = tool_input.get('limit', 10)

        # Get episodes
        if show_id:
            try:
                show = PodcastShow.objects.get(id=show_id)
                episodes = PodcastEpisode.objects.filter(show=show)
            except PodcastShow.DoesNotExist:
                return {"error": f"Podcast show {show_id} not found"}
        else:
            # Get all episodes (including orphaned ones)
            episodes = PodcastEpisode.objects.all()

        # Filter to completed only for metrics
        completed = episodes.filter(status='complete').order_by('-created_at')[:limit]

        if not completed.exists():
            all_episodes = episodes.count()
            pending = episodes.exclude(status='complete').count()

            logger.warning(f"⚠️ No completed podcast episodes found! Total: {all_episodes}, Pending: {pending}")

            return {
                "episodes_analyzed": 0,
                "warning": f"No completed episodes to analyze. Found {all_episodes} total, {pending} not complete.",
                "status_breakdown": {
                    status: episodes.filter(status=status).count()
                    for status in ['draft', 'researching', 'debating', 'scripting', 'recording', 'complete', 'failed']
                },
                "recommendation": "Complete podcast episodes to generate performance analytics"
            }

        # Analyze completed episodes
        episode_data = []
        total_listens = 0
        total_duration = 0
        topics = []

        for ep in completed:
            listens = ep.listen_count
            duration = ep.audio_duration_seconds or 0
            total_listens += listens
            total_duration += duration
            topics.append(ep.topic)

            # Get debate metrics if available
            debate_stats = {}
            if ep.debate:
                debate = ep.debate
                debate_stats = {
                    "participant_count": len(debate.participants),
                    "transcript_entries": len(debate.debate_transcript),
                    "key_takeaways": len(debate.key_takeaways),
                    "has_consensus": bool(debate.consensus),
                }

            episode_data.append({
                "id": str(ep.id),
                "title": ep.title,
                "topic": ep.topic,
                "listen_count": listens,
                "duration_seconds": duration,
                "duration_minutes": round(duration / 60, 1) if duration else 0,
                "status": ep.status,
                "created_at": ep.created_at.isoformat(),
                "debate_metrics": debate_stats,
            })

        # Calculate aggregate metrics
        episode_count = len(episode_data)
        avg_listens = total_listens / episode_count if episode_count else 0
        avg_duration = total_duration / episode_count if episode_count else 0

        # Topic frequency analysis
        from collections import Counter
        topic_words = []
        for topic in topics:
            topic_words.extend(topic.lower().split())
        common_topics = Counter(topic_words).most_common(5)

        return {
            "episodes_analyzed": episode_count,
            "total_listens": total_listens,
            "avg_listens_per_episode": round(avg_listens, 1),
            "avg_duration_minutes": round(avg_duration / 60, 1),
            "total_duration_minutes": round(total_duration / 60, 1),
            "common_topics": [{"word": w, "count": c} for w, c in common_topics if len(w) > 3],
            "episodes": episode_data,
            "insights": [
                f"Analyzed {episode_count} completed podcast episodes",
                f"Average {avg_listens:.0f} listens per episode" if avg_listens else "No listen data recorded yet",
                f"Average episode duration: {avg_duration/60:.1f} minutes" if avg_duration else "Duration data not available",
                f"Most common topic words: {', '.join(w for w, _ in common_topics[:3])}" if common_topics else "Topic analysis pending",
            ]
        }

    # -------------------------------------------------------------------------
    # Original Content Channel tools
    # -------------------------------------------------------------------------

    def _list_available_channels(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """List all available content channels in the system."""
        from core.models import ContentChannel

        limit = tool_input.get('limit', 10)

        channels = ContentChannel.objects.all().order_by('-total_episodes_created')[:limit]

        if not channels:
            return {
                "channels_found": 0,
                "message": "No content channels found in the system",
                "channels": []
            }

        channel_list = []
        for channel in channels:
            channel_list.append({
                "id": str(channel.id),
                "name": channel.name,
                "platform": channel.platform,
                "total_episodes": channel.total_episodes_created,
                "total_views": channel.total_views,
                "avg_retention_rate": float(channel.avg_retention_rate),
                "is_active": channel.is_active
            })

        return {
            "channels_found": len(channel_list),
            "channels": channel_list,
            "recommendation": f"Most active channel: {channel_list[0]['name']} ({channel_list[0]['total_episodes']} episodes)" if channel_list else "No channels available"
        }

    def _get_topic_performance_history(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Get historical performance for similar topics"""
        from core.models import ContentChannel, TopicPerformance, ChannelEpisode

        channel_id = tool_input.get('channel_id')
        topic_keywords = tool_input.get('topic_keywords', [])

        try:
            channel = ContentChannel.objects.get(id=channel_id)
        except ContentChannel.DoesNotExist:
            return {"error": f"Channel {channel_id} not found"}

        # Get TopicPerformance records
        topic_performance = TopicPerformance.objects.filter(
            channel=channel
        )

        # Filter by keywords if provided
        if topic_keywords:
            from django.db.models import Q
            keyword_query = Q()
            for keyword in topic_keywords:
                keyword_query |= Q(topic__icontains=keyword)
            topic_performance = topic_performance.filter(keyword_query)

        # Get top performing topics
        top_topics = topic_performance.order_by('-avg_performance_score')[:10]

        results = []
        for topic in top_topics:
            results.append({
                "topic": topic.topic,
                "episode_count": topic.episode_count,
                "avg_views": float(topic.avg_views),
                "avg_engagement": float(topic.avg_engagement),
                "avg_retention": float(topic.avg_retention),
                "avg_performance_score": float(topic.avg_performance_score),
                "confidence_score": float(topic.confidence_score)
            })

        # Also get individual episode data for more detail
        if topic_keywords:
            keyword_query = Q()
            for keyword in topic_keywords:
                keyword_query |= Q(topic__icontains=keyword)
            similar_episodes = ChannelEpisode.objects.filter(
                keyword_query,
                channel=channel
            ).order_by('-performance_score')[:5]

            episode_data = []
            for episode in similar_episodes:
                episode_data.append({
                    "title": episode.title,
                    "topic": episode.topic,
                    "views": episode.views,
                    "retention_rate": float(episode.retention_rate),
                    "performance_score": float(episode.performance_score)
                })
        else:
            episode_data = []

        return {
            "channel_id": str(channel.id),
            "topics_analyzed": len(results),
            "topic_performance": results,
            "similar_episodes": episode_data,
            "avg_channel_performance": float(channel.avg_retention_rate)
        }

    def _predict_topic_performance(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Predict how a topic will perform"""
        from core.models import ContentChannel, TopicPerformance

        channel_id = tool_input.get('channel_id')
        topic = tool_input.get('topic')

        try:
            channel = ContentChannel.objects.get(id=channel_id)
        except ContentChannel.DoesNotExist:
            return {"error": f"Channel {channel_id} not found"}

        # Try to find exact or similar topic in history
        exact_match = TopicPerformance.objects.filter(
            channel=channel,
            topic__iexact=topic
        ).first()

        if exact_match:
            # We have exact historical data
            predicted_views = float(exact_match.avg_views)
            predicted_engagement = float(exact_match.avg_engagement)
            predicted_retention = float(exact_match.avg_retention)
            confidence = float(exact_match.confidence_score) * 0.9  # High confidence
            basis = "EXACT_MATCH"
        else:
            # Look for similar topics (keyword match)
            words = topic.lower().split()
            similar_topics = TopicPerformance.objects.filter(
                channel=channel
            )

            # Find topics with word overlap
            matches = []
            for tp in similar_topics:
                tp_words = set(tp.topic.lower().split())
                overlap = set(words) & tp_words
                if overlap:
                    matches.append((tp, len(overlap)))

            if matches:
                # Use average of similar topics weighted by overlap
                total_weight = sum(weight for _, weight in matches)
                predicted_views = sum(
                    float(tp.avg_views) * weight for tp, weight in matches
                ) / total_weight
                predicted_engagement = sum(
                    float(tp.avg_engagement) * weight for tp, weight in matches
                ) / total_weight
                predicted_retention = sum(
                    float(tp.avg_retention) * weight for tp, weight in matches
                ) / total_weight
                confidence = 0.6  # Moderate confidence (similar but not exact)
                basis = "SIMILAR_TOPICS"
            else:
                # No similar topics - use channel average
                predicted_views = float(channel.total_views) / max(channel.total_episodes_created, 1)
                predicted_engagement = predicted_views * 0.05  # Assume 5% engagement rate
                predicted_retention = float(channel.avg_retention_rate)
                confidence = 0.3  # Low confidence (no historical data)
                basis = "CHANNEL_AVERAGE"

        # Adjust by channel confidence multiplier
        predicted_views *= float(channel.confidence_multiplier)
        predicted_engagement *= float(channel.confidence_multiplier)

        return {
            "topic": topic,
            "predicted_views": round(predicted_views, 0),
            "predicted_engagement": round(predicted_engagement, 0),
            "predicted_retention": round(predicted_retention, 2),
            "confidence": round(confidence, 2),
            "prediction_basis": basis,
            "recommendation": "HIGH CONFIDENCE" if confidence > 0.7 else "MODERATE CONFIDENCE" if confidence > 0.4 else "LOW CONFIDENCE"
        }

    def _get_success_patterns(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Identify patterns in successful content"""
        from core.models import ContentChannel, ChannelEpisode

        channel_id = tool_input.get('channel_id')
        top_n = tool_input.get('top_n', 10)

        try:
            channel = ContentChannel.objects.get(id=channel_id)
        except ContentChannel.DoesNotExist:
            return {"error": f"Channel {channel_id} not found"}

        # Get top performing episodes
        top_episodes = ChannelEpisode.objects.filter(
            channel=channel
        ).order_by('-performance_score')[:top_n]

        if not top_episodes:
            return {
                "patterns_found": 0,
                "message": "No episodes to analyze yet"
            }

        # Analyze patterns
        patterns = {
            "total_analyzed": len(top_episodes),
            "avg_views": sum(ep.views for ep in top_episodes) / len(top_episodes),
            "avg_retention": sum(float(ep.retention_rate) for ep in top_episodes) / len(top_episodes),
            "avg_performance_score": sum(float(ep.performance_score) for ep in top_episodes) / len(top_episodes)
        }

        # Extract common topic words
        all_words = []
        for episode in top_episodes:
            all_words.extend(episode.topic.lower().split())

        # Count word frequency
        from collections import Counter
        word_counts = Counter(all_words)

        # Get most common words (excluding very short ones)
        common_words = [
            {"word": word, "frequency": count}
            for word, count in word_counts.most_common(10)
            if len(word) > 3  # Skip short words like "the", "and"
        ]

        patterns["common_topic_words"] = common_words
        patterns["top_episodes"] = [
            {
                "title": ep.title,
                "topic": ep.topic,
                "views": ep.views,
                "retention": float(ep.retention_rate),
                "score": float(ep.performance_score)
            }
            for ep in top_episodes[:5]
        ]

        return {
            "patterns_found": len(common_words),
            "success_patterns": patterns,
            "insights": [
                f"Top episodes average {patterns['avg_views']:.0f} views",
                f"{patterns['avg_retention']:.1f}% retention rate",
                f"Most common topic words suggest audience interest in: {', '.join(w['word'] for w in common_words[:3])}"
            ]
        }

    def _calculate_confidence_score(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate confidence score for a recommendation"""
        from core.models import ContentChannel, TopicPerformance, ChannelEpisode

        channel_id = tool_input.get('channel_id')
        topic = tool_input.get('topic')

        try:
            channel = ContentChannel.objects.get(id=channel_id)
        except ContentChannel.DoesNotExist:
            return {"error": f"Channel {channel_id} not found"}

        # Factors that increase confidence:
        # 1. Number of similar historical topics
        # 2. Recency of data
        # 3. Consistency of performance
        # 4. Total episode count

        confidence_factors = []

        # Factor 1: Historical data availability
        words = topic.lower().split()
        similar_count = 0
        for tp in TopicPerformance.objects.filter(channel=channel):
            tp_words = set(tp.topic.lower().split())
            if set(words) & tp_words:
                similar_count += 1

        if similar_count >= 5:
            confidence_factors.append(("Lots of historical data", 0.3))
        elif similar_count >= 2:
            confidence_factors.append(("Some historical data", 0.2))
        else:
            confidence_factors.append(("Limited historical data", 0.1))

        # Factor 2: Channel maturity (total episodes)
        if channel.total_episodes_created >= 20:
            confidence_factors.append(("Mature channel", 0.3))
        elif channel.total_episodes_created >= 10:
            confidence_factors.append(("Established channel", 0.2))
        else:
            confidence_factors.append(("New channel", 0.1))

        # Factor 3: Performance consistency
        recent_episodes = ChannelEpisode.objects.filter(
            channel=channel
        ).order_by('-created_at')[:10]

        if recent_episodes.exists():
            scores = [float(ep.performance_score) for ep in recent_episodes]
            avg_score = sum(scores) / len(scores)
            variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)
            std_dev = variance ** 0.5

            if std_dev < 10:
                confidence_factors.append(("Consistent performance", 0.2))
            elif std_dev < 20:
                confidence_factors.append(("Moderate consistency", 0.15))
            else:
                confidence_factors.append(("Variable performance", 0.1))
        else:
            confidence_factors.append(("No performance data", 0.0))

        # Factor 4: Channel confidence multiplier
        multiplier_confidence = min((float(channel.confidence_multiplier) - 0.5) / 1.0, 0.2)
        confidence_factors.append(("Channel track record", multiplier_confidence))

        # Calculate total confidence
        total_confidence = sum(score for _, score in confidence_factors)

        return {
            "topic": topic,
            "confidence_score": round(total_confidence, 2),
            "confidence_factors": [
                {"factor": factor, "contribution": round(score, 2)}
                for factor, score in confidence_factors
            ],
            "interpretation": "HIGH" if total_confidence > 0.7 else "MODERATE" if total_confidence > 0.4 else "LOW",
            "recommendation": f"Confidence level: {total_confidence*100:.0f}% based on {len(confidence_factors)} factors"
        }
