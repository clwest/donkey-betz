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

logger = logging.getLogger(__name__)


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

Your personality:
- Warm and engaging podcast host
- Curious and genuinely interested
- Fair to all perspectives
- Great at summarizing complex points
- Keeps discussions lively but focused

Your hosting style:
- Welcome listeners with energy
- Introduce topics with context
- Ask great follow-up questions
- Ensure each participant gets fair time
- Bridge between different perspectives
- Summarize key points for listeners

Your key phrases:
- "Welcome to [Show Name]! Today we're tackling..."
- "That's a fascinating point. [Name], what do you think?"
- "Let me make sure I understand..."
- "You both seem to agree on... but differ on..."
- "For our listeners, the key takeaway here is..."
- "Before we move on, let's summarize..."

Voice: Antoni (warm narrator, professional) in podcast audio.

Your segments:
1. INTRO - Set the stage, introduce topic and guests
2. OPENING STATEMENTS - Give each participant their moment
3. DISCUSSION - Facilitate back-and-forth, ask follow-ups
4. SUMMARY - Recap key points and areas of agreement/disagreement
5. OUTRO - Thank participants, tease next episode, call to action

CRITICAL: Stay neutral. Your job is to facilitate, not to take sides."""

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

        try:
            # Build prompt with system prompt + task
            prompt = self._build_prompt(task, scifi_context, spider_context)

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

                execution_time_ms = int((time.time() - start_time) * 1000)
                result = AgentResult(
                    success=True,
                    message=response.get('content') or "Moderation prepared",
                    data={"tool_results": tool_results, "role": "HOST", "voice_id": "Antoni"},
                    agent_name=self.name,
                    execution_time_ms=execution_time_ms,
                    tool_calls=tool_calls_made
                )
            else:
                # No tools called, return content directly
                execution_time_ms = int((time.time() - start_time) * 1000)
                result = AgentResult(
                    success=True,
                    message=response.get('content') or 'No response',
                    data={"role": "HOST", "voice_id": "Antoni"},
                    agent_name=self.name,
                    execution_time_ms=execution_time_ms
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

        return {"error": f"Unknown tool: {tool_name}"}

    def _create_introduction(
        self,
        show_name: str,
        topic: str,
        hook: str,
        participant_intros: List[str]
    ) -> Dict[str, Any]:
        """Create an engaging podcast introduction."""

        # Build the introduction
        intro_parts = []

        # Hook
        if hook:
            intro_parts.append(hook)
        else:
            intro_parts.append(f"What if everything you thought you knew about {topic} was about to change?")

        # Welcome
        intro_parts.append(f"Welcome to {show_name}! I'm your host, and today we're diving deep into a topic that's sparking debates everywhere: {topic}.")

        # Participant intros
        if participant_intros:
            intro_parts.append("Joining me today are some brilliant minds with very different perspectives:")
            for intro in participant_intros:
                intro_parts.append(f"- {intro}")
        else:
            intro_parts.append("I've got some passionate debaters ready to duke it out on this topic.")

        # Setup
        intro_parts.append("Let's get started with opening statements. Remember, we're here to explore ideas, challenge assumptions, and maybe - just maybe - find some common ground.")

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
        """Generate follow-up questions based on a statement."""

        questions = []

        # For the speaker
        questions.append({
            "target": speaker or "the speaker",
            "question": f"Can you give us a concrete example of that?"
        })

        # For the other participant
        if other_participant:
            questions.append({
                "target": other_participant,
                "question": f"{other_participant}, I'm curious - how do you respond to that point?"
            })

        # Clarifying question
        questions.append({
            "target": "general",
            "question": "Let me make sure our listeners understand - you're saying that..."
        })

        return {
            "role": "HOST",
            "voice_id": "Antoni",
            "follow_up_questions": questions,
            "transition_phrases": [
                "That's a fascinating point.",
                "I want to dig deeper on that.",
                "Let me push back a little here.",
                "Our listeners might be wondering..."
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
        """Create a podcast outro."""

        outro_parts = []

        if thank_participants:
            outro_parts.append("I want to thank our brilliant debaters for joining us today. This was a fantastic discussion!")

        outro_parts.append("And thank YOU for listening. If you enjoyed this episode, please subscribe and leave a review.")

        if call_to_action:
            outro_parts.append(call_to_action)
        else:
            outro_parts.append("Share your thoughts in the comments - who do you think made the stronger argument?")

        if next_episode_tease:
            outro_parts.append(f"Next time on the show: {next_episode_tease}")
        else:
            outro_parts.append("Next time, we'll be tackling another controversial topic that's sure to spark debate.")

        outro_parts.append("Until then, keep questioning, keep learning, and keep debating!")

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
