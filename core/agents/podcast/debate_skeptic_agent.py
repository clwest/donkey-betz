"""
Debate Skeptic Agent - Session 496

This agent argues AGAINST or challenges the debate topic.
It researches the risks, concerns, and potential problems.

Works with:
- DebateAdvocateAgent (argues FOR)
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


def analyze_skeptic_position_with_ml(position_data: dict) -> dict:
    """Analyze skeptic arguments using ML models (Text)."""
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
            'counterargument_analysis': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML skeptic analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


class DebateSkepticAgent(BaseAgent):
    """
    Challenges the debate topic and argues AGAINST with evidence.

    This agent is critical but fair:
    - Questions assumptions
    - Highlights risks and concerns
    - Demands evidence
    - Plays devil's advocate effectively
    """

    name = "DebateSkepticAgent"

    system_prompt = """You are the Debate Skeptic Agent - you challenge ideas and argue AGAINST in podcast debates.

Your personality:
- Critical thinker who questions assumptions
- Not negative, but rigorous and thorough
- Asks tough questions and demands evidence
- Plays devil's advocate effectively
- Measured and thoughtful in delivery

Your argumentation style:
- Lead with questions and challenges
- Point out risks, costs, and unintended consequences
- Reference failures, cautionary tales, and concerns
- Demand concrete evidence from the other side
- Offer balanced critique, not just negativity

When debating, you:
1. Research the risks and concerns using spider data
2. Find failures, problems, and cautionary examples
3. Identify legitimate expert concerns
4. Build a rigorous critical case
5. Deliver arguments with authority

Example phrases:
- "But have we considered the risks of..."
- "The data also shows concerning trends in..."
- "Critics like [name] have pointed out that..."
- "History is full of examples where similar..."
- "Let's look at what happened when..."

Voice: Clyde (authoritative, deep) in podcast audio.

CRITICAL: Use research tools to find real evidence. Never fabricate statistics or quotes.
Be critical but fair - acknowledge valid points from the other side."""

    description = "Challenges debate topics with critical analysis and evidence"

    def _get_available_tools(self) -> List[Dict[str, Any]]:
        """Define GPT tools for research and critical analysis."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "research_concerns",
                    "description": "Research the risks, concerns, and potential problems with a topic.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "description": "The topic to research critically"
                            },
                            "concern_areas": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Specific areas of concern (e.g., 'ethical issues', 'economic risks')"
                            }
                        },
                        "required": ["topic"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "build_critique",
                    "description": "Build a structured critique with evidence.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "main_concern": {
                                "type": "string",
                                "description": "The main concern or criticism"
                            },
                            "supporting_evidence": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Evidence supporting the concern"
                            },
                            "questions_to_ask": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Tough questions for the advocate"
                            },
                            "fair_acknowledgment": {
                                "type": "string",
                                "description": "What you acknowledge is valid about the other side"
                            }
                        },
                        "required": ["main_concern", "supporting_evidence"]
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
                            "key_concerns": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "3-5 key concerns to raise during debate"
                            },
                            "tough_questions": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Probing questions for the advocate"
                            },
                            "closing_statement": {
                                "type": "string",
                                "description": "Measured closing statement"
                            }
                        },
                        "required": ["opening_statement", "key_concerns"]
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
        """Execute the debate skeptic task."""
        import time
        start_time = time.time()
        tool_calls_made = []

        # Session 750: Time Travel integration
        with self.time_travel_session("debate_skepticism", task, input_data=context):
            self.record_decision(
                decision_type="analysis",
                action="Starting debate skepticism",
                reasoning=f"Processing task: {task[:100] if task else 'No task specified'}",
                alternatives=["Skip skepticism", "Defer to human", "Consult other agents"],
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

                    analysis = self._synthesize_tool_results(tool_calls_made, tool_results, task)
                    content = analysis or response.get('content') or "Skeptic argument prepared"

                    execution_time_ms = int((time.time() - start_time) * 1000)
                    result = AgentResult(
                        success=True,
                        message=content,
                        data={"tool_results": tool_results, "role": "SKEPTIC", "voice_id": "Clyde", "full_text": content},
                        agent_name=self.name,
                        execution_time_ms=execution_time_ms,
                        tool_calls=tool_calls_made
                    )

                    if len(content) > 100:
                        self._save_to_deliverable(
                            title=f"Debate Skepticism: {task[:50]}",
                            content=content,
                            deliverable_type='script',
                            category='Content',
                            tags=['debate', 'skeptic', 'podcast', 'script'],
                            content_format='markdown',
                            metadata={'task': task, 'role': 'SKEPTIC'},
                        )
                else:
                    # No tools called, return content directly
                    execution_time_ms = int((time.time() - start_time) * 1000)
                    content = response.get('content') or 'No response'
                    result = AgentResult(
                        success=True,
                        message=content,
                        data={"role": "SKEPTIC", "voice_id": "Clyde"},
                        agent_name=self.name,
                        execution_time_ms=execution_time_ms
                    )

                    # Session 861: Persist script to Deliverable
                    if content and content != 'No response':
                        self._save_to_deliverable(
                            title=f"Debate Skepticism: {task[:50]}",
                            content=content,
                            deliverable_type='script',
                            category='Content',
                            tags=['debate', 'skeptic', 'podcast', 'script'],
                            content_format='markdown',
                            metadata={'task': task, 'role': 'SKEPTIC'},
                        )

                # Record learning outcome for collective intelligence
                try:
                    self._record_learning_outcome(
                        task=task,
                        result=result,
                        success=True,
                        context={
                            'agent_type': self.__class__.__name__,
                            'role': 'SKEPTIC',
                            'execution_time_ms': execution_time_ms,
                        }
                    )
                except Exception as le:
                    logger.warning(f"Failed to record learning outcome: {le}")

                return result

            except Exception as e:
                logger.error(f"DebateSkepticAgent error: {e}")
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
        """Handle tool calls for skeptical analysis."""

        if tool_name == "research_concerns":
            return self._research_concerns(
                arguments.get("topic", ""),
                arguments.get("concern_areas", [])
            )

        elif tool_name == "build_critique":
            return self._build_critique(
                arguments.get("main_concern", ""),
                arguments.get("supporting_evidence", []),
                arguments.get("questions_to_ask", []),
                arguments.get("fair_acknowledgment", "")
            )

        elif tool_name == "generate_debate_statements":
            return self._generate_debate_statements(
                arguments.get("opening_statement", ""),
                arguments.get("key_concerns", []),
                arguments.get("tough_questions", []),
                arguments.get("closing_statement", "")
            )

        # Session 1002C: Fall through to BaseAgent for web_search, spider_query, delegation
        return super()._execute_tool_call(tool_name, arguments)

    def _research_concerns(
        self,
        topic: str,
        concern_areas: List[str]
    ) -> Dict[str, Any]:
        """Research concerns and risks about a topic."""
        from core.models_unified_system import SpiderData

        # Query spider data for critical content
        keywords = [topic] + concern_areas + ["risks", "concerns", "problems", "criticism", "failure"]

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
            logger.error(f"Error researching concerns: {e}")
            research_findings = []

        return {
            "topic": topic,
            "concern_areas": concern_areas,
            "research_findings": research_findings,
            "research_summary": f"Found {len(research_findings)} relevant sources for concerns about {topic}",
            "suggested_concerns": [
                "Unintended consequences and side effects",
                "Economic costs and who bears them",
                "Ethical implications and fairness",
                "Historical failures of similar approaches",
                "Expert warnings and cautionary voices"
            ]
        }

    def _build_critique(
        self,
        main_concern: str,
        supporting_evidence: List[str],
        questions_to_ask: List[str],
        fair_acknowledgment: str
    ) -> Dict[str, Any]:
        """Build a structured critique."""
        return {
            "critique_structure": {
                "main_concern": main_concern,
                "evidence": supporting_evidence,
                "probing_questions": questions_to_ask or [
                    "What evidence do you have for that claim?",
                    "Have you considered the costs and who pays them?",
                    "What happens if this goes wrong?"
                ],
                "fair_acknowledgment": fair_acknowledgment or "I acknowledge there may be some benefits, but we must weigh them against..."
            },
            "critique_strength": "strong" if len(supporting_evidence) >= 3 else "moderate",
            "debate_ready": True
        }

    def _generate_debate_statements(
        self,
        opening_statement: str,
        key_concerns: List[str],
        tough_questions: List[str],
        closing_statement: str
    ) -> Dict[str, Any]:
        """Generate statements for the podcast debate."""
        return {
            "role": "SKEPTIC",
            "voice_id": "Clyde",
            "statements": {
                "opening": opening_statement,
                "key_concerns": key_concerns,
                "tough_questions": tough_questions or [
                    "What's the evidence for that claim?",
                    "Have we considered who bears the costs?",
                    "What are the unintended consequences?"
                ],
                "closing": closing_statement
            },
            "speaking_style": "measured, probing, uses rhetorical questions",
            "word_count_estimate": len(opening_statement.split()) + sum(len(c.split()) for c in key_concerns)
        }

    async def prepare_for_debate(
        self,
        topic: str,
        debate_question: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Prepare research and arguments for a debate.

        Returns structured critique ready for the podcast.
        """

        # Execute the agent with the debate preparation task
        result = await self.execute(
            f"""Prepare to challenge and argue AGAINST this debate topic: "{topic}"

            Debate question: {debate_question}

            Your task:
            1. Research the risks and concerns about this topic
            2. Build a rigorous critique with evidence
            3. Generate debate statements (opening, key concerns, tough questions, closing)

            Be critical but fair. Focus on risks, costs, and unintended consequences.
            Acknowledge valid points from the other side while still making your case.
            """
        )

        if result.success:
            # Compile the preparation results
            preparation = {
                "role": "skeptic",
                "topic": topic,
                "position": "AGAINST",
                "voice_id": "Clyde",
                "research": [],
                "critique": {},
                "statements": {}
            }

            # Extract tool results
            for tool_result in result.tool_results:
                if "research_findings" in tool_result:
                    preparation["research"] = tool_result["research_findings"]
                elif "critique_structure" in tool_result:
                    preparation["critique"] = tool_result["critique_structure"]
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
