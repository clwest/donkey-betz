"""
Contrarian Agent - Session 466

Part of Autonomous Content Studio debate system (Property #3: Internal Disagreement).

This agent challenges obvious/popular choices by:
1. Detecting oversaturated topics
2. Finding unique angles on trending topics
3. Suggesting contrarian/counterintuitive approaches
4. Warning about "everyone's doing this" topics

Works alongside:
- TopicMinerAgent (proposes trending topics)
- PerformanceAnalystAgent (provides data-driven insights)

The contrarian view prevents the channel from being just another copycat.
"""

import logging
from typing import Dict, Any, List
from django.utils import timezone
from datetime import timedelta

from core.agents.base_agent import BaseAgent, AgentResult
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


def analyze_contrarian_with_ml(content_data: dict) -> dict:
    """Analyze content for contrarian opportunities using ML models (Text)."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()

        # Use TEXT task type for sentiment/saturation analysis
        result = router.auto_route(
            data=content_data,
            task_hint=TaskType.TEXT,
            max_models=2
        )

        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'text'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'saturation_analysis': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML contrarian analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


class ContrarianAgent(BaseAgent):
    """
    Challenges obvious content choices and suggests unique angles.

    This agent argues AGAINST following the crowd:
    - "Everyone's covering this - we'll get lost in the noise"
    - "Too saturated - better to find a unique angle"
    - "This is obvious - let's do something different"
    """

    name = "ContrarianAgent"

    system_prompt = """You are the Contrarian Agent - you challenge obvious content choices.

Your job is to:
1. DETECT SATURATION - Identify when a topic is oversaturated
2. FIND UNIQUE ANGLES - Suggest contrarian approaches to trending topics
3. CHALLENGE GROUPTHINK - Question "everyone's doing this" logic
4. PROTECT DIFFERENTIATION - Keep the channel from being just another copycat

When TopicMinerAgent suggests a trending topic, you provide:
- Saturation analysis (how many others are covering this)
- Unique angle suggestions (contrarian approaches)
- Risk assessment (will we get lost in the noise?)
- Alternative topic recommendations (less obvious but valuable)

You typically argue AGAINST trendy topics because:
- Trending = saturated = hard to stand out
- First is better than best - we're often late to trends
- Unique angles create more memorable content
- Differentiation is more valuable than following

But you're not just negative - you suggest BETTER alternatives:
- Unique spins on trending topics
- Underserved niches within popular domains
- Contrarian takes that spark debate
- Topics that are rising (not yet saturated)

CRITICAL: Use tools to check actual saturation data. Don't just assume."""

    description = "Challenges obvious choices and suggests unique angles"

    def _get_available_tools(self) -> List[Dict[str, Any]]:
        """Define GPT tools for contrarian analysis"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "check_topic_saturation",
                    "description": "Check how saturated a topic is by counting mentions in spider data. High saturation = everyone's covering it.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "description": "Topic to check for saturation"
                            },
                            "days_back": {
                                "type": "integer",
                                "description": "How many days to analyze (default: 14)"
                            }
                        },
                        "required": ["topic"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "suggest_unique_angles",
                    "description": "Suggest unique/contrarian angles on a trending topic that would differentiate the content.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "description": "The trending topic to find unique angles for"
                            },
                            "channel_style": {
                                "type": "string",
                                "description": "Channel's style/voice to match angles to"
                            }
                        },
                        "required": ["topic"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "find_rising_topics",
                    "description": "Find topics that are RISING (getting more mentions) but not yet saturated. Better opportunity than already-trending topics.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "domain_keywords": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Channel's domain keywords"
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
        Execute contrarian analysis to challenge popular topics.

        Args:
            task: User's request (e.g., "Check if this topic is oversaturated")
            context: Additional context (topics to check, etc.)
            scifi_context: Mood, memory, evolution context
            spider_context: Trends from spider network

        Returns:
            AgentResult with contrarian insights
        """
        import time

        start_time = time.time()
        tool_calls_made = []

        # Search strategy now handled universally by BaseAgent._enhance_task_with_queries()

        # Session 750: Time Travel integration
        with self.time_travel_session("contrarian_analysis", task, input_data=context):
            self.record_decision(
                decision_type="analysis",
                action="Starting contrarian analysis",
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
                        tool_result = self._execute_tool(tool_name, tool_input)
                        tool_results.append(tool_result)

                    # Feed tool results BACK to GPT for synthesis/analysis
                    import json
                    tool_summary = []
                    for tc, tr in zip(tool_calls_made, tool_results):
                        tool_summary.append(
                            f"Tool: {tc['name']}\nInput: {json.dumps(tc['input'], default=str)[:200]}\n"
                            f"Result: {json.dumps(tr, default=str)[:500]}"
                        )
                    synthesis_prompt = (
                        f"You called these tools and got these results:\n\n"
                        f"{'---'.join(tool_summary)}\n\n"
                        f"Now provide your CONTRARIAN ANALYSIS based on this data. "
                        f"Do NOT repeat the raw tool output. Instead:\n"
                        f"1. What does the data tell us about saturation?\n"
                        f"2. What unique angles should we take?\n"
                        f"3. What's your recommendation?\n"
                        f"Be specific and actionable."
                    )
                    synthesis_response = self._call_openai(synthesis_prompt)
                    analysis_text = synthesis_response.get('content') or "Contrarian analysis complete"

                    execution_time_ms = int((time.time() - start_time) * 1000)
                    result = AgentResult(
                        success=True,
                        message=analysis_text,
                        data={"tool_results": tool_results, "full_text": analysis_text},
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

                    # Persist analysis to Deliverable (only real analysis, not tool dumps)
                    if len(analysis_text) > 100:
                        self._save_to_deliverable(
                            title=f"Contrarian Analysis: {task[:80]}",
                            content=analysis_text,
                            deliverable_type='analysis',
                            category='Contrarian Analysis',
                            tags=['contrarian', 'content'],
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
                logger.error(f"ContrarianAgent execution error: {e}")
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
            if tool_name == "check_topic_saturation":
                return self._check_topic_saturation(tool_input)
            elif tool_name == "suggest_unique_angles":
                return self._suggest_unique_angles(tool_input)
            elif tool_name == "find_rising_topics":
                return self._find_rising_topics(tool_input)
            else:
                # Session 1002C: Fall through to BaseAgent for web_search, spider_query, delegation
                return super()._execute_tool_call(tool_name, tool_input)
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}", exc_info=True)
            return {"error": str(e)}

    # =========================================================================
    # TOOL IMPLEMENTATIONS
    # =========================================================================

    def _check_topic_saturation(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Check how saturated a topic is in recent content"""
        from core.models import SpiderData

        topic = tool_input.get('topic')
        days_back = tool_input.get('days_back', 14)

        # Count mentions over time periods
        now = timezone.now()

        # Last 3 days
        recent_count = SpiderData.objects.filter(
            embedding_text__icontains=topic,
            created_at__gte=now - timedelta(days=3)
        ).count()

        # Previous 3 days (for comparison)
        previous_count = SpiderData.objects.filter(
            embedding_text__icontains=topic,
            created_at__gte=now - timedelta(days=6),
            created_at__lt=now - timedelta(days=3)
        ).count()

        # Total in period
        total_count = SpiderData.objects.filter(
            embedding_text__icontains=topic,
            created_at__gte=now - timedelta(days=days_back)
        ).count()

        # Calculate saturation metrics
        # High saturation = lots of mentions
        saturation_level = "LOW"
        if total_count > 50:
            saturation_level = "CRITICAL"
        elif total_count > 20:
            saturation_level = "HIGH"
        elif total_count > 10:
            saturation_level = "MODERATE"

        # Trend direction
        if recent_count > previous_count * 1.5:
            trend = "ACCELERATING"
        elif recent_count < previous_count * 0.5:
            trend = "DECLINING"
        else:
            trend = "STABLE"

        # Recommendation
        if saturation_level in ["HIGH", "CRITICAL"]:
            recommendation = "AVOID - Too saturated, hard to stand out"
        elif saturation_level == "MODERATE" and trend == "ACCELERATING":
            recommendation = "UNIQUE ANGLE REQUIRED - Popular but could work with differentiation"
        else:
            recommendation = "ACCEPTABLE - Not oversaturated"

        return {
            "topic": topic,
            "saturation_level": saturation_level,
            "total_mentions": total_count,
            "recent_mentions_3d": recent_count,
            "previous_mentions_3d": previous_count,
            "trend": trend,
            "recommendation": recommendation
        }

    def _suggest_unique_angles(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest unique/contrarian angles on a topic"""
        topic = tool_input.get('topic')
        channel_style = tool_input.get('channel_style', 'educational')

        # Generate contrarian angle suggestions
        # This is a simple implementation - could be enhanced with GPT for more creative angles
        angles = []

        # Angle 1: Opposite perspective
        angles.append({
            "angle": f"Why {topic} might be overrated",
            "reasoning": "Contrarian take that challenges the hype",
            "differentiation": "Most coverage is positive - negative/balanced view stands out"
        })

        # Angle 2: Beginner/advanced split
        if 'beginner' in topic.lower() or 'intro' in topic.lower():
            angles.append({
                "angle": f"Advanced {topic.replace('beginner', '').replace('intro to', '').strip()} techniques",
                "reasoning": "Most content targets beginners - serve the underserved advanced audience",
                "differentiation": "Less competition at advanced level"
            })
        else:
            angles.append({
                "angle": f"{topic} explained like you're 5",
                "reasoning": "Most content is too complex - make it accessible",
                "differentiation": "Extreme simplification is rare and valuable"
            })

        # Angle 3: Practical/theoretical split
        angles.append({
            "angle": f"Real-world {topic} case study (not theory)",
            "reasoning": "Most coverage is theoretical - show actual implementation",
            "differentiation": "Case studies are more valuable and less common"
        })

        # Angle 4: Historical/future
        angles.append({
            "angle": f"What {topic} will look like in 5 years",
            "reasoning": "Most coverage is present-focused - look ahead",
            "differentiation": "Future predictions spark more engagement"
        })

        # Angle 5: Behind the scenes
        angles.append({
            "angle": f"How {topic} actually works (technical deep-dive)",
            "reasoning": "Surface-level coverage is common - go deeper",
            "differentiation": "Technical depth attracts different audience"
        })

        return {
            "topic": topic,
            "angles_suggested": len(angles),
            "unique_angles": angles,
            "message": f"Generated {len(angles)} contrarian angles to differentiate from mainstream coverage"
        }

    def _find_rising_topics(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Find topics that are rising but not yet saturated"""
        from core.models import SpiderData
        from django.db.models import Q

        domain_keywords = tool_input.get('domain_keywords', [])

        # Compare two time periods to detect rising topics
        now = timezone.now()

        # Recent period (last 3 days)
        recent_start = now - timedelta(days=3)

        # Previous period (4-7 days ago)
        previous_start = now - timedelta(days=7)
        previous_end = now - timedelta(days=4)

        # Build domain query
        keyword_query = Q()
        for keyword in domain_keywords:
            keyword_query |= Q(embedding_text__icontains=keyword)

        # Get items from both periods
        recent_items = SpiderData.objects.filter(
            keyword_query,
            created_at__gte=recent_start
        )

        previous_items = SpiderData.objects.filter(
            keyword_query,
            created_at__gte=previous_start,
            created_at__lt=previous_end
        )

        # Extract topics (simple: split embedding_text into 2-word phrases)
        def extract_topics(items):
            topics = {}
            for item in items:
                text = item.embedding_text or ''
                words = text.split()
                for i in range(len(words) - 1):
                    phrase = f"{words[i]} {words[i+1]}"
                    if len(phrase) > 5:
                        topics[phrase] = topics.get(phrase, 0) + 1
            return topics

        recent_topics = extract_topics(recent_items)
        previous_topics = extract_topics(previous_items)

        # Find topics that are rising (more mentions in recent vs previous)
        rising = []
        for topic, recent_count in recent_topics.items():
            previous_count = previous_topics.get(topic, 0)

            # Must have at least 2 recent mentions
            if recent_count < 2:
                continue

            # Calculate growth
            if previous_count == 0:
                growth_rate = "NEW"
                growth_pct = None
            else:
                growth_pct = ((recent_count - previous_count) / previous_count) * 100
                if growth_pct > 100:
                    growth_rate = "RAPID"
                elif growth_pct > 50:
                    growth_rate = "FAST"
                elif growth_pct > 0:
                    growth_rate = "GROWING"
                else:
                    continue  # Not rising

            # Only include if rising AND not yet saturated (< 10 recent mentions)
            if recent_count < 10:
                rising.append({
                    "topic": topic,
                    "recent_mentions": recent_count,
                    "previous_mentions": previous_count,
                    "growth_rate": growth_rate,
                    "growth_pct": round(growth_pct, 1) if growth_pct else None,
                    "saturation": "LOW" if recent_count < 5 else "MODERATE"
                })

        # Sort by growth and recency
        rising.sort(key=lambda x: (x['growth_rate'] == "RAPID", x['recent_mentions']), reverse=True)

        return {
            "rising_topics_found": len(rising),
            "rising_topics": rising[:10],
            "message": f"Found {len(rising)} rising topics (growing but not saturated)"
        }
