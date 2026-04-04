"""
Topic Miner Agent - Session 466

Part of Autonomous Content Studio debate system (Property #3: Internal Disagreement).

This agent finds trending topics in a channel's domain by:
1. Querying spider network for recent trends
2. Analyzing what's gaining traction
3. Identifying gaps and opportunities
4. Scoring topic potential

Works alongside:
- ContrarianAgent (challenges recommendations)
- PerformanceAnalystAgent (provides data-driven insights)

The debate creates better content decisions than any single agent alone.
"""

import logging
from typing import Dict, Any, List
from django.utils import timezone
from datetime import timedelta

from core.agents.base_agent import BaseAgent, AgentResult
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


def analyze_topics_with_ml(topic_data: dict) -> dict:
    """Analyze trending topics using ML models (Text)."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()

        # Use TEXT task type for topic analysis
        result = router.auto_route(
            data=topic_data,
            task_hint=TaskType.TEXT,
            max_models=2
        )

        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'text'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'topic_clusters': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML topic analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


class TopicMinerAgent(BaseAgent):
    """
    Finds trending topics for content channels by analyzing spider data.

    This agent argues FOR trending/popular topics:
    - "This is trending NOW - we should cover it"
    - "High search volume, lots of engagement"
    - "Competitors are covering this - we need to also"
    """

    name = "TopicMinerAgent"

    system_prompt = """You are the Topic Miner Agent - you find trending topics for content creation.

Your job is to analyze spider data and identify topics that are:
1. TRENDING - gaining attention right now
2. RELEVANT - match the channel's domain/audience
3. HIGH POTENTIAL - likely to get views and engagement

You use these sources:
- Spider network data (tech news, social trends, etc.)
- Search trends and keyword data
- Competitor content analysis
- Social media signals

When making recommendations, you provide:
- Topic name and description
- Why it's trending (data/evidence)
- Estimated potential (views, engagement)
- Urgency score (how time-sensitive)

You typically argue FOR popular/trending topics because:
- Trending = proven interest = likely views
- Following trends = riding the wave
- People are searching for this NOW

CRITICAL: Always use tools to get real spider data. Never make up trends or fake statistics."""

    description = "Finds trending topics by analyzing spider network data"

    def _get_available_tools(self) -> List[Dict[str, Any]]:
        """Define GPT tools for topic mining"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "query_spider_trends",
                    "description": "Query spider network for trending topics in a specific domain. Returns recent spider data filtered by keywords.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "domain_keywords": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Keywords defining the content domain (e.g., ['AI', 'machine learning', 'technology'])"
                            },
                            "days_back": {
                                "type": "integer",
                                "description": "How many days to look back (default: 7)"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results (default: 20)"
                            }
                        },
                        "required": ["domain_keywords"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "score_topic_potential",
                    "description": "Score a topic's potential based on trend momentum, search volume, and relevance.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "description": "Topic to score"
                            },
                            "domain_keywords": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Channel's domain keywords for relevance scoring"
                            }
                        },
                        "required": ["topic", "domain_keywords"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "detect_trending_gaps",
                    "description": "Find trending topics that competitors haven't covered yet (opportunity gaps).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "domain_keywords": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Channel's domain keywords"
                            },
                            "covered_topics": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Topics the channel has already covered"
                            }
                        },
                        "required": ["domain_keywords"]
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
        Execute topic mining to find trending content opportunities.

        Args:
            task: User's request (e.g., "Find trending AI topics")
            context: Additional context (domain keywords, etc.)
            scifi_context: Mood, memory, evolution context
            spider_context: Trends from spider network

        Returns:
            AgentResult with trending topics
        """
        import time

        start_time = time.time()
        tool_calls_made = []

        # Search strategy now handled universally by BaseAgent._enhance_task_with_queries()

        # Session 750: Time Travel integration
        with self.time_travel_session("topic_mining", task, input_data=context):
            self.record_decision(
                decision_type="analysis",
                action="Starting topic mining",
                reasoning=f"Processing task: {task[:100] if task else 'No task specified'}",
                alternatives=["Skip mining", "Defer to human", "Consult other agents"],
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
                    message = analysis or response.get('content') or "Topic mining complete"

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
                                'trends_found': len(tool_results),
                            }
                        )
                    except Exception as e:
                        logger.warning(f"Failed to record learning outcome: {e}")

                    # Persist synthesized analysis to Deliverable
                    if len(message) > 100:
                        self._save_to_deliverable(
                            title=f"Topic Mining: {task[:80]}",
                            content=message,
                            deliverable_type='analysis',
                            category='Topic Mining',
                            tags=['topics', 'content'],
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
                logger.error(f"TopicMinerAgent execution error: {e}")
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
            if tool_name == "query_spider_trends":
                return self._query_spider_trends(tool_input)
            elif tool_name == "score_topic_potential":
                return self._score_topic_potential(tool_input)
            elif tool_name == "detect_trending_gaps":
                return self._detect_trending_gaps(tool_input)
            else:
                # Session 1002C: Fall through to BaseAgent for web_search, spider_query, delegation
                return super()._execute_tool_call(tool_name, tool_input)
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}", exc_info=True)
            return {"error": str(e)}

    # =========================================================================
    # TOOL IMPLEMENTATIONS
    # =========================================================================

    def _query_spider_trends(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Query spider network for trending topics"""
        from core.models import SpiderData

        domain_keywords = tool_input.get('domain_keywords', [])
        days_back = tool_input.get('days_back', 7)
        limit = tool_input.get('limit', 20)

        # Query spider data from last N days
        since_date = timezone.now() - timedelta(days=days_back)

        # Build query - search for any domain keyword in embedding_text
        query = SpiderData.objects.filter(
            created_at__gte=since_date
        )

        # Filter by keywords (case-insensitive search in embedding_text)
        if domain_keywords:
            from django.db.models import Q
            keyword_query = Q()
            for keyword in domain_keywords:
                keyword_query |= Q(embedding_text__icontains=keyword)
            query = query.filter(keyword_query)

        # Get most recent results
        results = query.order_by('-created_at')[:limit]

        trends = []
        for item in results:
            raw = item.raw_data if isinstance(item.raw_data, dict) else {}
            trends.append({
                "title": raw.get('title', item.spider_name),
                "source": item.source_url,
                "url": item.source_url,
                "discovered_at": item.created_at.isoformat(),
                "content_preview": (item.embedding_text or "")[:200],
            })

        return {
            "trends_found": len(trends),
            "days_searched": days_back,
            "domain_keywords": domain_keywords,
            "trends": trends
        }

    def _score_topic_potential(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Score a topic's potential based on various factors"""
        from core.models import SpiderData

        topic = tool_input.get('topic')
        domain_keywords = tool_input.get('domain_keywords', [])

        # Count mentions in spider data (last 7 days)
        since_date = timezone.now() - timedelta(days=7)
        mention_count = SpiderData.objects.filter(
            embedding_text__icontains=topic,
            created_at__gte=since_date
        ).count()

        # Calculate scores
        # Mention frequency score (0-100)
        mention_score = min(mention_count * 10, 100)

        # Recency score (0-100) - higher if mentioned in last 24 hours
        recent_count = SpiderData.objects.filter(
            embedding_text__icontains=topic,
            created_at__gte=timezone.now() - timedelta(days=1)
        ).count()
        recency_score = min(recent_count * 20, 100)

        # Relevance score (0-100) - how well topic matches domain
        relevance_score = 50  # Base score
        for keyword in domain_keywords:
            if keyword.lower() in topic.lower():
                relevance_score += 15
        relevance_score = min(relevance_score, 100)

        # Overall potential score (weighted average)
        potential_score = (
            mention_score * 0.4 +
            recency_score * 0.3 +
            relevance_score * 0.3
        )

        return {
            "topic": topic,
            "potential_score": round(potential_score, 2),
            "mention_count": mention_count,
            "recent_mentions": recent_count,
            "mention_score": round(mention_score, 2),
            "recency_score": round(recency_score, 2),
            "relevance_score": round(relevance_score, 2),
            "recommendation": "HIGH POTENTIAL" if potential_score > 60 else "MODERATE POTENTIAL" if potential_score > 30 else "LOW POTENTIAL"
        }

    def _detect_trending_gaps(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Find trending topics not yet covered"""
        from core.models import SpiderData

        domain_keywords = tool_input.get('domain_keywords', [])
        covered_topics = tool_input.get('covered_topics', [])

        # Get recent trending topics
        since_date = timezone.now() - timedelta(days=7)

        # Build query for domain keywords
        from django.db.models import Q
        keyword_query = Q()
        for keyword in domain_keywords:
            keyword_query |= Q(embedding_text__icontains=keyword)

        recent_items = SpiderData.objects.filter(
            keyword_query,
            created_at__gte=since_date
        ).order_by('-created_at')[:50]

        # Extract potential topics from embedding text
        topics = {}
        for item in recent_items:
            # Simple topic extraction - split text into words and find 2-3 word phrases
            text = item.embedding_text or ''
            words = text.split()
            for i in range(len(words) - 1):
                # Get 2-word phrase
                phrase = f"{words[i]} {words[i+1]}"
                if len(phrase) > 5:  # Skip very short phrases
                    topics[phrase] = topics.get(phrase, 0) + 1

        # Filter out covered topics
        uncovered_topics = []
        for topic, count in topics.items():
            # Skip if already covered
            if any(covered.lower() in topic.lower() for covered in covered_topics):
                continue
            # Skip if very low mention count
            if count < 2:
                continue
            uncovered_topics.append({
                "topic": topic,
                "mention_count": count
            })

        # Sort by mention count
        uncovered_topics.sort(key=lambda x: x['mention_count'], reverse=True)

        return {
            "gaps_found": len(uncovered_topics),
            "top_gaps": uncovered_topics[:10],
            "message": f"Found {len(uncovered_topics)} trending topics not yet covered"
        }
