"""
Podcast Coordinator Agent - Session 496

The main orchestrator for AI podcast generation. This agent:
1. Takes a topic and assigns perspectives to debate agents
2. Coordinates the research phase (each agent researches independently)
3. Manages the structured debate (back-and-forth arguments)
4. Transforms the debate into a polished podcast script
5. Optionally generates audio with ElevenLabs

This creates podcasts like "AI Debates Weekly" where 3-4 AI agents
discuss trending topics with actual research and different perspectives.
"""

import logging
import json
from typing import Dict, Any, List
from django.utils import timezone

from core.agents.base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)


class PodcastCoordinatorAgent(BaseAgent):
    """
    Orchestrates the entire podcast creation process.

    This is the "director" agent that:
    - Analyzes the debate topic and creates a balanced question
    - Assigns roles (Advocate, Skeptic, Analyst, Host)
    - Coordinates research and debate phases
    - Produces the final podcast script
    """

    name = "PodcastCoordinatorAgent"

    system_prompt = """You are the Podcast Coordinator Agent - you orchestrate AI podcast creation.

Your job is to take a topic and coordinate a multi-agent debate that becomes a podcast episode.

## Your Workflow

1. **Topic Analysis**
   - Analyze the user's topic
   - Create a balanced debate question (e.g., "Should AI be regulated?" not "Why AI is bad")
   - Identify 2-3 key perspectives to explore

2. **Perspective Assignment**
   - Advocate: Argues FOR the topic with enthusiasm and evidence
   - Skeptic: Challenges assumptions, plays devil's advocate
   - Analyst: Neutral data-driven perspective with statistics
   - Host/Moderator: Guides discussion, asks follow-ups, summarizes

3. **Script Generation**
   - Transform debate transcript into podcast script format
   - Add intro, transitions, and outro
   - Include speaker labels for different voices

## Script Format

Your scripts should use this format:

```
[INTRO - 5 seconds music fade]

HOST: Welcome to AI Debates! Today we're tackling the question: [DEBATE QUESTION]

[SEGMENT 1: Opening Statements]

ADVOCATE: [Their opening position with evidence]

SKEPTIC: [Counter-position with evidence]

ANALYST: [Data-driven neutral perspective]

[SEGMENT 2: Deep Dive]
...

[OUTRO]
HOST: That's all for today...
```

## Voice Assignments
- HOST: Antoni (warm, professional narrator)
- ADVOCATE: Rachel (enthusiastic, optimistic)
- SKEPTIC: Clyde (authoritative, critical)
- ANALYST: Paul (calm, data-driven)

CRITICAL: When creating scripts, maintain clear speaker labels for TTS generation.
"""

    description = "Orchestrates multi-agent podcast creation with debates"

    def _get_available_tools(self) -> List[Dict[str, Any]]:
        """Define GPT tools for podcast coordination."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "create_debate_structure",
                    "description": "Create the structure for a podcast debate with perspectives and questions.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "description": "The main topic to debate"
                            },
                            "debate_question": {
                                "type": "string",
                                "description": "A balanced yes/no or either-or question for the debate"
                            },
                            "perspectives": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of 2-4 perspectives to explore"
                            },
                            "key_questions": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Key questions to address during the debate"
                            }
                        },
                        "required": ["topic", "debate_question", "perspectives"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_podcast_script",
                    "description": "Generate the final podcast script from debate transcript.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "episode_title": {
                                "type": "string",
                                "description": "Title for this podcast episode"
                            },
                            "intro": {
                                "type": "string",
                                "description": "Opening introduction by the host"
                            },
                            "segments": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "segment_name": {"type": "string"},
                                        "dialogue": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "speaker": {"type": "string"},
                                                    "text": {"type": "string"}
                                                }
                                            }
                                        }
                                    }
                                },
                                "description": "Podcast segments with dialogue"
                            },
                            "outro": {
                                "type": "string",
                                "description": "Closing remarks by the host"
                            },
                            "show_notes": {
                                "type": "string",
                                "description": "Episode description and key points"
                            }
                        },
                        "required": ["episode_title", "intro", "segments", "outro"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "assign_voices",
                    "description": "Assign ElevenLabs voices to each podcast participant.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "voice_assignments": {
                                "type": "object",
                                "description": "Map of role to ElevenLabs voice ID",
                                "additionalProperties": {"type": "string"}
                            }
                        },
                        "required": ["voice_assignments"]
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
        """Execute the podcast coordination task."""
        import asyncio

        scifi_context = scifi_context or {}
        spider_context = spider_context or {}

        # Session 529: Build intelligent prompt with full context
        self._intelligent_context = self._build_intelligent_prompt(task, scifi_context, spider_context)

        # Build enhanced prompt with context
        enhanced_task = f"""
Task: {task}

Context: {json.dumps(context, default=str) if context else 'None'}

Create a structured podcast debate with:
1. A balanced debate question
2. Clear perspectives for participants
3. Key discussion questions
"""

        # Call the parent's GPT-based execution
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        async def _run():
            return await self._execute_with_gpt(enhanced_task)

        result = loop.run_until_complete(_run())

        # Record learning outcome for collective intelligence
        try:
            self._record_learning_outcome(
                task=task,
                result=result,
                success=result.success if hasattr(result, 'success') else True,
                context={
                    'agent_type': self.__class__.__name__,
                    'execution_time_ms': result.execution_time_ms if hasattr(result, 'execution_time_ms') else 0,
                }
            )
        except Exception as le:
            logger.warning(f"Failed to record learning outcome: {le}")

        return result

    async def _execute_with_gpt(self, task: str) -> AgentResult:
        """Execute using GPT with tool calling."""
        from openai import OpenAI
        import os

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": task}
        ]

        try:
            response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=messages,
                tools=self._get_available_tools(),
                tool_choice="auto",
                max_completion_tokens=4000
            )

            message = response.choices[0].message
            tool_results = []

            # Process tool calls if any
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    try:
                        args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        args = {}

                    result = self._handle_tool_call(tool_name, args)
                    tool_results.append(result)

            return AgentResult(
                success=True,
                message=message.content or "Podcast coordination complete",
                data={"tool_results": tool_results},
                tool_calls=tool_results
            )

        except Exception as e:
            logger.error(f"GPT execution failed: {e}")
            return AgentResult(
                success=False,
                message=f"Error: {str(e)}",
                error=str(e)
            )

    def _handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Handle tool calls for podcast coordination."""

        if tool_name == "create_debate_structure":
            return self._create_debate_structure(
                arguments.get("topic", ""),
                arguments.get("debate_question", ""),
                arguments.get("perspectives", []),
                arguments.get("key_questions", [])
            )

        elif tool_name == "generate_podcast_script":
            return self._generate_podcast_script(
                arguments.get("episode_title", ""),
                arguments.get("intro", ""),
                arguments.get("segments", []),
                arguments.get("outro", ""),
                arguments.get("show_notes", "")
            )

        elif tool_name == "assign_voices":
            return self._assign_voices(
                arguments.get("voice_assignments", {})
            )

        return {"error": f"Unknown tool: {tool_name}"}

    def _create_debate_structure(
        self,
        topic: str,
        debate_question: str,
        perspectives: List[str],
        key_questions: List[str]
    ) -> Dict[str, Any]:
        """Create the structure for a podcast debate."""

        # Default voice assignments based on role
        voice_map = {
            "host": "Antoni",
            "advocate": "Rachel",
            "skeptic": "Clyde",
            "analyst": "Paul",
            "expert": "Drew"
        }

        # Build participants structure
        participants = []
        roles = ["advocate", "skeptic", "analyst"]

        for i, perspective in enumerate(perspectives[:3]):
            role = roles[i] if i < len(roles) else "expert"
            participants.append({
                "perspective": perspective,
                "role": role,
                "voice_id": voice_map.get(role, "Antoni")
            })

        # Always add a host
        participants.insert(0, {
            "perspective": "Moderator - guides discussion",
            "role": "host",
            "voice_id": "Antoni"
        })

        structure = {
            "topic": topic,
            "debate_question": debate_question,
            "participants": participants,
            "key_questions": key_questions or [
                f"What are the main benefits?",
                f"What are the main risks?",
                f"What does the data show?",
                f"What should we do about it?"
            ],
            "format": {
                "intro": "Host introduces topic (30 seconds)",
                "opening_statements": "Each participant states position (60 seconds each)",
                "discussion": "Back and forth debate (5-10 minutes)",
                "summary": "Host summarizes key points (60 seconds)",
                "outro": "Closing and call to action (30 seconds)"
            },
            "estimated_duration_minutes": 10
        }

        logger.info(f"Created debate structure for topic: {topic}")
        return structure

    def _generate_podcast_script(
        self,
        episode_title: str,
        intro: str,
        segments: List[Dict[str, Any]],
        outro: str,
        show_notes: str
    ) -> Dict[str, Any]:
        """Generate the final podcast script."""

        # Build script segments with proper formatting
        script_segments = []

        # Add intro segment
        script_segments.append({
            "segment_type": "intro",
            "speaker": "HOST",
            "voice_id": "Antoni",
            "text": intro
        })

        # Process each segment
        for segment in segments:
            segment_name = segment.get("segment_name", "Discussion")
            dialogue = segment.get("dialogue", [])

            # Add segment marker
            script_segments.append({
                "segment_type": "marker",
                "text": f"[SEGMENT: {segment_name}]"
            })

            # Add dialogue entries
            for entry in dialogue:
                speaker = entry.get("speaker", "HOST").upper()
                text = entry.get("text", "")

                # Map speaker to voice
                voice_map = {
                    "HOST": "Antoni",
                    "ADVOCATE": "Rachel",
                    "SKEPTIC": "Clyde",
                    "ANALYST": "Paul",
                    "EXPERT": "Drew"
                }

                script_segments.append({
                    "segment_type": "dialogue",
                    "speaker": speaker,
                    "voice_id": voice_map.get(speaker, "Antoni"),
                    "text": text
                })

        # Add outro segment
        script_segments.append({
            "segment_type": "outro",
            "speaker": "HOST",
            "voice_id": "Antoni",
            "text": outro
        })

        # Build full script text
        full_script = f"# {episode_title}\n\n"
        full_script += "[INTRO MUSIC - 5 seconds]\n\n"

        for seg in script_segments:
            if seg.get("segment_type") == "marker":
                full_script += f"\n{seg['text']}\n\n"
            elif seg.get("speaker"):
                full_script += f"{seg['speaker']}: {seg['text']}\n\n"

        full_script += "[OUTRO MUSIC - 5 seconds]"

        result = {
            "episode_title": episode_title,
            "script": full_script,
            "script_segments": script_segments,
            "show_notes": show_notes or f"In this episode, we debate: {episode_title}",
            "estimated_duration_seconds": len(script_segments) * 30  # Rough estimate
        }

        logger.info(f"Generated podcast script: {episode_title} ({len(script_segments)} segments)")
        return result

    def _assign_voices(self, voice_assignments: Dict[str, str]) -> Dict[str, Any]:
        """Assign ElevenLabs voices to participants."""

        # Default voice options
        available_voices = {
            "Antoni": "Warm narrator, professional",
            "Rachel": "Enthusiastic, warm",
            "Clyde": "Authoritative, deep",
            "Paul": "Calm, conversational",
            "Drew": "Confident, clear",
            "Aria": "Expressive, dynamic",
            "Dave": "Friendly, approachable",
            "Sarah": "Soft, thoughtful",
            "Josh": "Energetic, young"
        }

        # Validate and return assignments
        validated = {}
        for role, voice in voice_assignments.items():
            if voice in available_voices:
                validated[role] = {
                    "voice_id": voice,
                    "description": available_voices[voice]
                }
            else:
                validated[role] = {
                    "voice_id": "Antoni",
                    "description": "Default (voice not found)"
                }

        return {
            "voice_assignments": validated,
            "available_voices": list(available_voices.keys())
        }

    async def create_podcast_episode(
        self,
        topic: str,
        user_id: int,
        format_type: str = "debate",
        participant_count: int = 3,
        generate_audio: bool = False
    ) -> Dict[str, Any]:
        """
        Main entry point: Create a complete podcast episode.

        This orchestrates the full workflow:
        1. Create debate structure
        2. Have agents research their positions
        3. Run the structured debate
        4. Generate podcast script
        5. Optionally generate audio
        """
        from core.models import PodcastEpisode, PodcastDebate
        from django.contrib.auth import get_user_model

        User = get_user_model()

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return {"error": f"User {user_id} not found"}

        # Step 1: Create the episode and debate records
        debate = PodcastDebate.objects.create(
            topic=topic[:200],
            topic_question=f"Should we embrace {topic}? What are the implications?",
            status="pending"
        )

        episode = PodcastEpisode.objects.create(
            user=user,
            title=f"Debate: {topic}",
            topic=topic[:200],
            debate=debate,
            status="researching",
            generation_config={
                "format": format_type,
                "participant_count": participant_count,
                "generate_audio": generate_audio
            }
        )

        logger.info(f"Created podcast episode {episode.id} for topic: {topic}")

        # Step 2: Create debate structure using our tools
        result = await self.execute(
            f"""Create a podcast debate structure for this topic: "{topic}"

            Generate:
            1. A balanced debate question
            2. {participant_count} different perspectives to explore
            3. Key questions to address

            Use the create_debate_structure tool."""
        )

        if result.success and result.tool_results:
            # Store debate structure
            for tool_result in result.tool_results:
                if "participants" in tool_result:
                    debate.participants = tool_result.get("participants", [])
                    debate.topic_question = tool_result.get("debate_question", debate.topic_question)
                    debate.save()

        # Step 3: Generate podcast script
        episode.status = "scripting"
        episode.progress_percent = 50
        episode.save()

        script_result = await self.execute(
            f"""Now generate a complete podcast script for the debate on "{topic}".

            Use these participants and their perspectives:
            {json.dumps(debate.participants, indent=2)}

            Create an engaging 10-minute podcast episode with:
            - An exciting intro
            - Opening statements from each participant
            - A lively debate with back-and-forth
            - A summary and key takeaways
            - A compelling outro

            Use the generate_podcast_script tool."""
        )

        if script_result.success and script_result.tool_results:
            for tool_result in script_result.tool_results:
                if "script" in tool_result:
                    episode.script = tool_result.get("script", "")
                    episode.script_segments = tool_result.get("script_segments", [])
                    episode.show_notes = tool_result.get("show_notes", "")
                    episode.save()

        # Step 4: Mark as complete (audio generation would be separate)
        episode.status = "complete"
        episode.progress_percent = 100
        episode.published_at = timezone.now()
        episode.save()

        debate.status = "complete"
        debate.completed_at = timezone.now()
        debate.save()

        logger.info(f"Completed podcast episode {episode.id}")

        return {
            "success": True,
            "episode_id": str(episode.id),
            "debate_id": str(debate.id),
            "title": episode.title,
            "status": episode.status,
            "script_preview": episode.script[:500] if episode.script else "",
            "segment_count": len(episode.script_segments)
        }
