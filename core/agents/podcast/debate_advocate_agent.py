"""
Debate Advocate Agent - Session 496

This agent argues FOR the debate topic with enthusiasm and evidence.
It researches the positive aspects, benefits, and success stories.

Works with:
- DebateSkepticAgent (argues AGAINST)
- ModeratorAgent (hosts discussion)
- PodcastCoordinatorAgent (orchestrates)
"""

import logging
from typing import Dict, Any, List
from django.utils import timezone
from datetime import timedelta

from core.agents.base_agent import BaseAgent, AgentResult
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


def analyze_advocate_position_with_ml(position_data: dict) -> dict:
    """Analyze advocate arguments using ML models (Text)."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()
        result = router.auto_route(
            data=position_data,
            task_hint=TaskType.TEXT,
            max_models=2
        )
        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'text'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'argument_analysis': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML advocate analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


class DebateAdvocateAgent(BaseAgent):
    """
    Argues FOR the debate topic with research and evidence.

    This agent is optimistic and finds the positive aspects:
    - Success stories and case studies
    - Benefits and opportunities
    - Innovation and progress
    - Expert endorsements
    """

    name = "DebateAdvocateAgent"

    system_prompt = """You are the Debate Advocate Agent - you argue FOR topics in podcast debates.

Your personality:
- Optimistic and enthusiastic
- Finds the silver lining in everything
- Uses compelling narratives and success stories
- Builds momentum with your arguments
- Acknowledges concerns but pivots to opportunities

Your argumentation style:
- Lead with benefits and opportunities
- Use real examples and case studies from research
- Reference expert opinions and studies that support the position
- Address counterarguments by reframing them
- Build to a compelling conclusion

When debating, you:
1. Research the positive aspects using spider data
2. Find success stories and case studies
3. Identify expert supporters
4. Build a compelling case with evidence
5. Deliver arguments with enthusiasm

Example phrases:
- "The data shows tremendous potential..."
- "Early adopters have already seen..."
- "Industry experts like [name] point out that..."
- "While there are challenges, the opportunity is..."
- "History has shown that similar innovations..."

Voice: Rachel (enthusiastic, warm) in podcast audio.

CRITICAL: Use research tools to find real evidence. Never fabricate statistics or quotes."""

    description = "Argues FOR debate topics with research and enthusiasm"

    def _get_available_tools(self) -> List[Dict[str, Any]]:
        """Define GPT tools for research and argumentation."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "research_positive_aspects",
                    "description": "Research the positive aspects, benefits, and success stories for a topic.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "description": "The topic to research"
                            },
                            "focus_areas": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Specific areas to focus on (e.g., 'economic benefits', 'innovation')"
                            }
                        },
                        "required": ["topic"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "build_argument",
                    "description": "Build a structured argument for a position with evidence.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "main_thesis": {
                                "type": "string",
                                "description": "The main point you're arguing"
                            },
                            "supporting_points": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Evidence and examples supporting the thesis"
                            },
                            "counterargument_response": {
                                "type": "string",
                                "description": "How to address the main counterargument"
                            },
                            "conclusion": {
                                "type": "string",
                                "description": "Compelling conclusion statement"
                            }
                        },
                        "required": ["main_thesis", "supporting_points"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_debate_statements",
                    "description": "Generate specific statements for the podcast debate.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "opening_statement": {
                                "type": "string",
                                "description": "60-second opening statement"
                            },
                            "key_points": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "3-5 key points to make during debate"
                            },
                            "rebuttals": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Prepared rebuttals to likely counterarguments"
                            },
                            "closing_statement": {
                                "type": "string",
                                "description": "Powerful closing statement"
                            }
                        },
                        "required": ["opening_statement", "key_points"]
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
        """Execute the debate advocate task."""
        import time
        start_time = time.time()
        tool_calls_made = []

        # Session 750: Time Travel integration
        with self.time_travel_session("debate_advocacy", task, input_data=context):
            self.record_decision(
                decision_type="analysis",
                action="Starting debate advocacy",
                reasoning=f"Processing task: {task[:100] if task else 'No task specified'}",
                alternatives=["Skip advocacy", "Defer to human", "Consult other agents"],
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
                        result = self._handle_tool_call(tool_name, tool_input)
                        tool_results.append(result)

                    # Synthesize tool results into advocacy argument
                    analysis = self._synthesize_tool_results(tool_calls_made, tool_results, task)
                    content = analysis or response.get('content') or "Advocacy argument prepared"

                    execution_time_ms = int((time.time() - start_time) * 1000)
                    result = AgentResult(
                        success=True,
                        message=content,
                        data={"tool_results": tool_results, "role": "ADVOCATE", "voice_id": "Rachel", "full_text": content},
                        agent_name=self.name,
                        execution_time_ms=execution_time_ms,
                        tool_calls=tool_calls_made
                    )

                    if len(content) > 100:
                        self._save_to_deliverable(
                            title=f"Debate Advocacy: {task[:50]}",
                            content=content,
                            deliverable_type='script',
                            category='Content',
                            tags=['debate', 'advocacy', 'podcast', 'script'],
                            content_format='markdown',
                            metadata={'task': task, 'role': 'ADVOCATE'},
                        )
                else:
                    # No tools called, return content directly
                    execution_time_ms = int((time.time() - start_time) * 1000)
                    content = response.get('content') or 'No response'
                    result = AgentResult(
                        success=True,
                        message=content,
                        data={"role": "ADVOCATE", "voice_id": "Rachel"},
                        agent_name=self.name,
                        execution_time_ms=execution_time_ms
                    )

                    # Session 861: Persist script to Deliverable
                    if content and content != 'No response':
                        self._save_to_deliverable(
                            title=f"Debate Advocacy: {task[:50]}",
                            content=content,
                            deliverable_type='script',
                            category='Content',
                            tags=['debate', 'advocacy', 'podcast', 'script'],
                            content_format='markdown',
                            metadata={'task': task, 'role': 'ADVOCATE'},
                        )

                # Record learning outcome for collective intelligence
                try:
                    self._record_learning_outcome(
                        task=task,
                        result=result,
                        success=True,
                        context={
                            'agent_type': self.__class__.__name__,
                            'role': 'ADVOCATE',
                            'execution_time_ms': execution_time_ms,
                        }
                    )
                except Exception as le:
                    logger.warning(f"Failed to record learning outcome: {le}")

                return result

            except Exception as e:
                logger.error(f"DebateAdvocateAgent error: {e}")
                execution_time_ms = int((time.time() - start_time) * 1000)
                result = AgentResult(
                    success=False,
                    error=str(e),
                    agent_name=self.name,
                    execution_time_ms=execution_time_ms
                )

                try:
                    self._record_learning_outcome(
                        task=task,
                        result=result,
                        success=False,
                        context={'agent_type': self.__class__.__name__, 'error': str(e)}
                    )
                except Exception as le:
                    logger.warning(f"Failed to record learning outcome: {le}")

            return result

    def _handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Handle tool calls for debate advocacy."""

        if tool_name == "research_positive_aspects":
            return self._research_positive_aspects(
                arguments.get("topic", ""),
                arguments.get("focus_areas", [])
            )

        elif tool_name == "build_argument":
            return self._build_argument(
                arguments.get("main_thesis", ""),
                arguments.get("supporting_points", []),
                arguments.get("counterargument_response", ""),
                arguments.get("conclusion", "")
            )

        elif tool_name == "generate_debate_statements":
            return self._generate_debate_statements(
                arguments.get("opening_statement", ""),
                arguments.get("key_points", []),
                arguments.get("rebuttals", []),
                arguments.get("closing_statement", "")
            )

        # Session 1002C: Fall through to BaseAgent for web_search, spider_query, delegation
        return super()._execute_tool_call(tool_name, arguments)

    def _research_positive_aspects(
        self,
        topic: str,
        focus_areas: List[str]
    ) -> Dict[str, Any]:
        """Research positive aspects of a topic using spider data."""
        from core.models_unified_system import SpiderData

        # Query spider data for positive content
        keywords = [topic] + focus_areas + ["benefits", "success", "innovation", "growth"]
        keyword_query = " | ".join(keywords)

        recent_date = timezone.now() - timedelta(days=30)

        try:
            spider_results = SpiderData.objects.filter(
                created_at__gte=recent_date,
                embedding_text__icontains=topic,
            )[:10]

            research_findings = []
            for result in spider_results:
                raw = result.raw_data if isinstance(result.raw_data, dict) else {}
                research_findings.append({
                    "title": raw.get('title', result.spider_name),
                    "source": result.source_url,
                    "summary": (result.embedding_text or "")[:200],
                    "url": result.source_url,
                })

        except Exception as e:
            logger.error(f"Error researching topic: {e}")
            research_findings = []

        return {
            "topic": topic,
            "focus_areas": focus_areas,
            "research_findings": research_findings,
            "research_summary": f"Found {len(research_findings)} relevant sources for positive aspects of {topic}",
            "suggested_angles": [
                "Economic benefits and job creation",
                "Innovation and technological advancement",
                "Quality of life improvements",
                "Competitive advantage",
                "Early success stories"
            ]
        }

    def _build_argument(
        self,
        main_thesis: str,
        supporting_points: List[str],
        counterargument_response: str,
        conclusion: str
    ) -> Dict[str, Any]:
        """Build a structured argument."""
        return {
            "argument_structure": {
                "thesis": main_thesis,
                "evidence": supporting_points,
                "counterargument_handling": counterargument_response or "Acknowledge the concern but highlight how benefits outweigh risks",
                "conclusion": conclusion or f"In conclusion, {main_thesis.lower()}"
            },
            "argument_strength": "strong" if len(supporting_points) >= 3 else "moderate",
            "debate_ready": True
        }

    def _generate_debate_statements(
        self,
        opening_statement: str,
        key_points: List[str],
        rebuttals: List[str],
        closing_statement: str
    ) -> Dict[str, Any]:
        """Generate statements for the podcast debate."""
        return {
            "role": "ADVOCATE",
            "voice_id": "Rachel",
            "statements": {
                "opening": opening_statement,
                "key_points": key_points,
                "rebuttals": rebuttals or [
                    "While I understand that concern, the evidence suggests...",
                    "That's a valid point, but we should also consider...",
                    "History has shown that similar innovations..."
                ],
                "closing": closing_statement
            },
            "speaking_style": "enthusiastic, uses metaphors, builds momentum",
            "word_count_estimate": len(opening_statement.split()) + sum(len(p.split()) for p in key_points)
        }

    async def prepare_for_debate(
        self,
        topic: str,
        debate_question: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Prepare research and arguments for a debate.

        Returns structured arguments ready for the podcast.
        """

        # Execute the agent with the debate preparation task
        result = await self.execute(
            f"""Prepare to argue FOR this debate topic: "{topic}"

            Debate question: {debate_question}

            Your task:
            1. Research the positive aspects of this topic
            2. Build a compelling argument with evidence
            3. Generate debate statements (opening, key points, rebuttals, closing)

            Be enthusiastic but use real evidence. Focus on benefits, opportunities, and success stories.
            """
        )

        if result.success:
            # Compile the preparation results
            preparation = {
                "role": "advocate",
                "topic": topic,
                "position": "FOR",
                "voice_id": "Rachel",
                "research": [],
                "arguments": {},
                "statements": {}
            }

            # Extract tool results
            for tool_result in result.tool_results:
                if "research_findings" in tool_result:
                    preparation["research"] = tool_result["research_findings"]
                elif "argument_structure" in tool_result:
                    preparation["arguments"] = tool_result["argument_structure"]
                elif "statements" in tool_result:
                    preparation["statements"] = tool_result["statements"]

            return {
                "success": True,
                "preparation": preparation
            }

        return {
            "success": False,
            "error": result.content
        }
