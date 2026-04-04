"""
Moderator Agent - Session 496

This agent hosts podcast debates as a warm, engaging moderator.
It guides discussions, asks follow-up questions, and summarizes key points.

Works with:
- DebateAdvocateAgent (argues FOR)
- DebateSkepticAgent (argues AGAINST)
- PodcastCoordinatorAgent (orchestrates)
"""

import logging
from typing import Dict, Any, List

from core.agents.base_agent import BaseAgent, AgentResult
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


def analyze_discussion_with_ml(discussion_data: dict) -> dict:
    """Analyze discussion flow using ML models (Text)."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()
        result = router.auto_route(
            data=discussion_data,
            task_hint=TaskType.TEXT,
            max_models=2
        )
        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'text'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'discussion_analysis': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML discussion analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


class ModeratorAgent(BaseAgent):
    """
    Hosts podcast debates as a warm, engaging moderator.

    This agent:
    - Introduces topics and participants
    - Asks probing follow-up questions
    - Ensures balanced time distribution
    - Summarizes key points clearly
    - Keeps discussions on track
    """

    name = "ModeratorAgent"

    system_prompt = """You are the Moderator Agent - you host AI podcast debates.

## Session 890: HOST WITH A POINT OF VIEW

You are NOT a neutral, pleasant narrator. You are a HOST with PERSONALITY and OPINIONS.

Your personality:
- Builder's mindset: You've seen systems fail, seen them succeed, you have EXPERIENCE
- Skeptical but optimistic: You push back on hype but believe in what's possible
- Direct communicator: You say what you think, you don't hedge
- Grounded in reality: You reference real data, real incidents, real timelines
- Donkey Betz insider: You know the platform, you reference it naturally

Your hosting style:
- Welcome listeners with energy BUT skip the generic enthusiasm
- Introduce topics with SPECIFIC context (numbers, dates, real events)
- Ask TOUGH follow-up questions, not softball validation
- Take stances: "Honestly, I think most AI platforms are lying to themselves about this..."
- Challenge participants: "But that contradicts what we saw last month when..."
- Share personal experience: "When we built the Learning Loop, we hit this exact problem..."

## BANNED PHRASES (NEVER use):
- "That's a fascinating point" → Instead: "I'm not sure I buy that because..."
- "Brilliant minds" → Instead: Use their actual expertise
- "Exciting times" → Instead: Reference specific dates/events
- "Let's dive in" → Instead: Get to the point directly
- "Wonderful conversation" → Instead: Be honest about what worked/didn't

## REQUIRED ELEMENTS:
- At least 1 tough question per segment that challenges a participant
- At least 1 reference to real system data/incidents
- At least 1 personal opinion or stance
- Natural references to Donkey Betz components when relevant

Your key phrases (SESSION 890 UPGRADE):
- "I'm going to push back on that because last week we saw..."
- "Honestly, this is where I think most people get it wrong..."
- "Our spider network pulled data on this, and here's what surprised me..."
- "Let me be direct: I don't think that's the whole story..."
- "This connects to something we learned building the Learning Loop..."
- "For context, when this happened in our system at 2 AM..."

Voice: Antoni (warm narrator, professional) in podcast audio.

Your segments:
1. INTRO - Set the stage with SPECIFIC context (not generic excitement)
2. OPENING STATEMENTS - Give each participant their moment
3. DISCUSSION - Facilitate back-and-forth, ASK TOUGH QUESTIONS, SHARE YOUR POV
4. SUMMARY - Recap what ACTUALLY matters, be honest about disagreements
5. OUTRO - Honest closing, what you learned, what listeners should think about

CRITICAL: You are NOT neutral. You have opinions. You take stances. You push back.
But you are FAIR - you let all perspectives speak and you can be convinced to change your mind."""

    description = "Hosts podcast debates with warmth and engagement"

    def _get_available_tools(self) -> List[Dict[str, Any]]:
        """Define GPT tools for moderation."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "create_introduction",
                    "description": "Create an engaging introduction for the podcast episode.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "show_name": {
                                "type": "string",
                                "description": "Name of the podcast show"
                            },
                            "topic": {
                                "type": "string",
                                "description": "The debate topic"
                            },
                            "hook": {
                                "type": "string",
                                "description": "An attention-grabbing opening hook"
                            },
                            "participant_intros": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Brief intro for each participant"
                            }
                        },
                        "required": ["show_name", "topic"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_follow_up_questions",
                    "description": "Generate follow-up questions based on a statement.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "statement": {
                                "type": "string",
                                "description": "The statement to follow up on"
                            },
                            "speaker": {
                                "type": "string",
                                "description": "Who made the statement"
                            },
                            "other_participant": {
                                "type": "string",
                                "description": "Who to direct the follow-up to"
                            }
                        },
                        "required": ["statement"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "summarize_discussion",
                    "description": "Summarize the key points from the discussion.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "points_of_agreement": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Where participants agreed"
                            },
                            "points_of_disagreement": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Where participants disagreed"
                            },
                            "key_insights": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Most important takeaways"
                            }
                        },
                        "required": ["key_insights"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_outro",
                    "description": "Create a closing for the episode.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "thank_participants": {
                                "type": "boolean",
                                "description": "Whether to thank participants"
                            },
                            "call_to_action": {
                                "type": "string",
                                "description": "What listeners should do next"
                            },
                            "next_episode_tease": {
                                "type": "string",
                                "description": "Tease for the next episode"
                            }
                        }
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
        """Execute the moderator task."""
        import time
        start_time = time.time()
        tool_calls_made = []

        # Session 750: Time Travel integration
        with self.time_travel_session("podcast_moderation", task, input_data=context):
            self.record_decision(
                decision_type="analysis",
                action="Starting podcast moderation",
                reasoning=f"Processing task: {task[:100] if task else 'No task specified'}",
                alternatives=["Skip moderation", "Defer to human", "Consult other agents"],
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
                    content = analysis or response.get('content') or "Moderation prepared"

                    execution_time_ms = int((time.time() - start_time) * 1000)
                    result = AgentResult(
                        success=True,
                        message=content,
                        data={"tool_results": tool_results, "role": "HOST", "voice_id": "Antoni", "full_text": content},
                        agent_name=self.name,
                        execution_time_ms=execution_time_ms,
                        tool_calls=tool_calls_made
                    )

                    if len(content) > 100:
                        self._save_to_deliverable(
                            title=f"Podcast Moderation: {task[:50]}",
                            content=content,
                            deliverable_type='script',
                            category='Content',
                            tags=['moderation', 'host', 'podcast', 'script'],
                            content_format='markdown',
                            metadata={'task': task, 'role': 'HOST'},
                        )
                else:
                    # No tools called, return content directly
                    execution_time_ms = int((time.time() - start_time) * 1000)
                    content = response.get('content') or 'No response'
                    result = AgentResult(
                        success=True,
                        message=content,
                        data={"role": "HOST", "voice_id": "Antoni"},
                        agent_name=self.name,
                        execution_time_ms=execution_time_ms
                    )

                    # Session 861: Persist script to Deliverable
                    if content and content != 'No response':
                        self._save_to_deliverable(
                            title=f"Podcast Moderation: {task[:50]}",
                            content=content,
                            deliverable_type='script',
                            category='Content',
                            tags=['moderation', 'host', 'podcast', 'script'],
                            content_format='markdown',
                            metadata={'task': task, 'role': 'HOST'},
                        )

                # Record learning outcome for collective intelligence
                try:
                    self._record_learning_outcome(
                        task=task,
                        result=result,
                        success=True,
                        context={
                            'agent_type': self.__class__.__name__,
                            'role': 'HOST',
                            'execution_time_ms': execution_time_ms,
                        }
                    )
                except Exception as le:
                    logger.warning(f"Failed to record learning outcome: {le}")

                return result

            except Exception as e:
                logger.error(f"ModeratorAgent error: {e}")
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
        """Handle tool calls for moderation."""

        if tool_name == "create_introduction":
            return self._create_introduction(
                arguments.get("show_name", "AI Debates"),
                arguments.get("topic", ""),
                arguments.get("hook", ""),
                arguments.get("participant_intros", [])
            )

        elif tool_name == "generate_follow_up_questions":
            return self._generate_follow_up_questions(
                arguments.get("statement", ""),
                arguments.get("speaker", ""),
                arguments.get("other_participant", "")
            )

        elif tool_name == "summarize_discussion":
            return self._summarize_discussion(
                arguments.get("points_of_agreement", []),
                arguments.get("points_of_disagreement", []),
                arguments.get("key_insights", [])
            )

        elif tool_name == "create_outro":
            return self._create_outro(
                arguments.get("thank_participants", True),
                arguments.get("call_to_action", ""),
                arguments.get("next_episode_tease", "")
            )

        # Session 1002C: Fall through to BaseAgent for web_search, spider_query, delegation
        return super()._execute_tool_call(tool_name, arguments)

    def _create_introduction(
        self,
        show_name: str,
        topic: str,
        hook: str,
        participant_intros: List[str]
    ) -> Dict[str, Any]:
        """Create an engaging podcast introduction - Session 890: With specificity and POV."""

        # Build the introduction
        intro_parts = []

        # Hook - Session 890: Specific, not generic
        if hook:
            intro_parts.append(hook)
        else:
            intro_parts.append(f"Last week our spider network crawled 847 sources on {topic}, and the data told a different story than the headlines. Let me show you what I mean.")

        # Welcome - Session 890: Direct, not fluffy
        intro_parts.append(f"Welcome to {show_name}. I'm going to be honest with you upfront: I have opinions on {topic}, and I'm not going to pretend I don't.")

        # Participant intros - Session 890: Expertise, not "brilliant minds"
        if participant_intros:
            intro_parts.append("Here's who's joining me:")
            for intro in participant_intros:
                intro_parts.append(f"- {intro}")
        else:
            intro_parts.append("Today's participants come from different angles - one's going to argue for, one against, and one is here with the data. I'll be pushing back on all of them.")

        # Setup - Session 890: Set expectations for real debate
        intro_parts.append("Ground rules: I'm going to interrupt when something doesn't add up. I'm going to ask for specifics when you get vague. And I'm going to tell you when I disagree. Let's go.")

        return {
            "role": "HOST",
            "voice_id": "Antoni",
            "segment": "intro",
            "text": " ".join(intro_parts),
            "duration_estimate_seconds": 45
        }

    def _generate_follow_up_questions(
        self,
        statement: str,
        speaker: str,
        other_participant: str
    ) -> Dict[str, Any]:
        """Generate follow-up questions - Session 890: Challenging, not validating."""

        questions = []

        # For the speaker - Session 890: Push for specifics
        questions.append({
            "target": speaker or "the speaker",
            "question": f"That's a claim. Show me the data. What's a specific example with a timeline?"
        })

        # For the other participant - Session 890: Direct challenge
        if other_participant:
            questions.append({
                "target": other_participant,
                "question": f"{other_participant}, I saw you react to that. Where specifically do you think they're wrong?"
            })

        # Challenge the logic - Session 890: Real pushback
        questions.append({
            "target": "general",
            "question": "Help me understand - because that contradicts what I've seen in our system data..."
        })

        return {
            "role": "HOST",
            "voice_id": "Antoni",
            "follow_up_questions": questions,
            # Session 890: Direct transitions, not generic validation
            "transition_phrases": [
                "I'm not sure I agree with that because...",
                "That's not what our data shows - let me push back...",
                "Hold on - when we built this at Donkey Betz, we saw the opposite...",
                "The skeptic in me says..."
            ]
        }

    def _summarize_discussion(
        self,
        points_of_agreement: List[str],
        points_of_disagreement: List[str],
        key_insights: List[str]
    ) -> Dict[str, Any]:
        """Summarize the discussion for listeners."""

        summary_parts = []

        summary_parts.append("Alright, let me try to summarize what we've heard today.")

        if points_of_agreement:
            summary_parts.append(f"Interestingly, our debaters actually agree on a few things: {', '.join(points_of_agreement[:3])}")

        if points_of_disagreement:
            summary_parts.append(f"But they strongly disagree on: {', '.join(points_of_disagreement[:3])}")

        if key_insights:
            summary_parts.append("For our listeners, here are the key takeaways:")
            for i, insight in enumerate(key_insights[:3], 1):
                summary_parts.append(f"{i}. {insight}")

        return {
            "role": "HOST",
            "voice_id": "Antoni",
            "segment": "summary",
            "text": " ".join(summary_parts),
            "points_of_agreement": points_of_agreement,
            "points_of_disagreement": points_of_disagreement,
            "key_insights": key_insights
        }

    def _create_outro(
        self,
        thank_participants: bool,
        call_to_action: str,
        next_episode_tease: str
    ) -> Dict[str, Any]:
        """Create a podcast outro - Session 890: Honest, specific, not generic."""

        outro_parts = []

        if thank_participants:
            outro_parts.append("To everyone who joined today - appreciate you bringing the real data and the real disagreements. That's what this show is for.")

        # Session 890: Honest reflection, not generic gratitude
        outro_parts.append("Here's what I'm taking away from this conversation: we agreed on more than I expected, but the core disagreement is real and I'm not sure either side has the full picture yet.")

        if call_to_action:
            outro_parts.append(call_to_action)
        else:
            outro_parts.append("If you think we got something wrong, tell me. I'm @donkeybetz on Twitter. I read the replies.")

        if next_episode_tease:
            outro_parts.append(f"Next time: {next_episode_tease}")
        else:
            outro_parts.append("Next week we're looking at something our Learning Loop flagged as a pattern - I'll share the data when we get there.")

        outro_parts.append("Until then.")

        return {
            "role": "HOST",
            "voice_id": "Antoni",
            "segment": "outro",
            "text": " ".join(outro_parts),
            "duration_estimate_seconds": 30
        }

    async def host_segment(
        self,
        segment_type: str,
        topic: str = "",
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate content for a specific podcast segment.

        segment_type: 'intro', 'transition', 'summary', 'outro'
        """

        context = context or {}

        prompts = {
            "intro": f"""Create an engaging introduction for a podcast debate about: "{topic}"

            Use create_introduction to generate:
            - A hook that grabs attention
            - A warm welcome to the show
            - Brief intros for participants
            - Setup for the debate
            """,

            "transition": f"""The discussion just covered this point: "{context.get('last_point', 'an interesting argument')}"

            Use generate_follow_up_questions to:
            - Create follow-up questions
            - Prepare transition phrases
            - Keep the discussion moving
            """,

            "summary": f"""Summarize the debate on: "{topic}"

            Use summarize_discussion with these notes:
            Points of agreement: {context.get('agreements', [])}
            Points of disagreement: {context.get('disagreements', [])}
            Key insights: {context.get('insights', [])}
            """,

            "outro": f"""Create a compelling outro for this episode about: "{topic}"

            Use create_outro to:
            - Thank the participants
            - Give a call to action
            - Tease the next episode
            """
        }

        prompt = prompts.get(segment_type, prompts["transition"])

        result = await self.execute(prompt)

        if result.success and result.tool_results:
            return {
                "success": True,
                "segment_type": segment_type,
                "content": result.tool_results[0] if result.tool_results else {}
            }

        return {
            "success": False,
            "segment_type": segment_type,
            "error": result.content
        }
