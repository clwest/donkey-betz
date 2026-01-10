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
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


def analyze_podcast_topic_with_ml(topic_data: dict) -> dict:
    """Analyze podcast topics using ML models (Text) for debate structure."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()
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
            'topic_analysis': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML podcast topic analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


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
            },
            # Session 653: NEW COMPOSABILITY TOOL - Run debates with ANY agents
            {
                "type": "function",
                "function": {
                    "name": "run_multi_agent_debate",
                    "description": "Run a real multi-agent debate with any agents from the system. Session 653 composability fix - enables cross-domain podcasts like 'BlockchainAuditCoordinator vs StockAuditCoordinator'.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "description": "The debate topic"
                            },
                            "participant_agents": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of agent names to participate (e.g., ['BlockchainAuditCoordinator', 'StockAuditCoordinator', 'CTOAgent'])"
                            },
                            "rounds": {
                                "type": "integer",
                                "description": "Number of debate rounds (default: 3)"
                            }
                        },
                        "required": ["topic", "participant_agents"]
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
        import time
        start_time = time.time()

        scifi_context = scifi_context or {}
        spider_context = spider_context or {}

        # Session 739: Store context for sub-agent calls
        self._current_spider_context = spider_context
        self._current_scifi_context = scifi_context

        # Session 736: Extract spider intelligence for real-time data
        spider_intel = self._extract_spider_intelligence(spider_context)
        if spider_intel['has_data']:
            logger.info(f"🕷️ {self.name} using spider intelligence: {len(spider_intel['trends'])} trends")

        # Session 735: Reset cost tracking for this execution
        self._reset_cost_tracking()

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

        # Session 735: Call synchronous execution (no async needed)
        result = self._execute_with_gpt(enhanced_task)

        # Update execution time
        execution_time_ms = int((time.time() - start_time) * 1000)
        result.execution_time_ms = execution_time_ms

        # Record learning outcome for collective intelligence
        try:
            self._record_learning_outcome(
                task=task,
                result=result,
                success=result.success if hasattr(result, 'success') else True,
                context={
                    'agent_type': self.__class__.__name__,
                    'execution_time_ms': execution_time_ms,
                }
            )
        except Exception as le:
            logger.warning(f"Failed to record learning outcome: {le}")

        return result

    def _execute_with_gpt(self, task: str) -> AgentResult:
        """Execute using GPT with tool calling."""
        # Build prompt combining system prompt and task
        prompt = f"{self.system_prompt}\n\nTask: {task}"

        try:
            # Session 735: Use inherited _call_openai for cost tracking
            # Temporarily set tools for this call
            original_tools = self.tools
            self.tools = self._get_available_tools()

            response = self._call_openai(prompt)

            # Restore original tools
            self.tools = original_tools

            tool_results = []

            # Process tool calls if any
            if response.get('tool_calls'):
                for tool_call in response['tool_calls']:
                    tool_name = tool_call.get('name', '')
                    args = tool_call.get('arguments', {})
                    result = self._handle_tool_call(tool_name, args)
                    tool_results.append(result)

            # Session 735: Use _make_result for automatic cost tracking
            return self._make_result(
                success=True,
                message=response.get('content') or "Podcast coordination complete",
                data={"tool_results": tool_results},
                tool_calls=tool_results
            )

        except Exception as e:
            logger.error(f"GPT execution failed: {e}")
            return self._make_result(
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

        # Session 653: New composability tool
        elif tool_name == "run_multi_agent_debate":
            return self._run_multi_agent_debate(
                arguments.get("topic", ""),
                arguments.get("participant_agents", []),
                arguments.get("rounds", 3)
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

    def _run_multi_agent_debate(
        self,
        topic: str,
        participant_agents: List[str],
        rounds: int = 3
    ) -> Dict[str, Any]:
        """
        Session 653 COMPOSABILITY FIX: Run a REAL multi-agent debate!

        This method actually calls the execute() method of each participating agent,
        enabling true cross-domain podcasts like:
        - "BlockchainAuditCoordinator vs StockAuditCoordinator on crypto regulation"
        - "LegalDocDrafterAgent vs CTOAgent on AI compliance"

        Each agent contributes their real expertise and knowledge to the debate.
        """
        from core.agent_router import AgentRouter

        logger.info(f"🎙️ [SESSION 653] Starting REAL multi-agent debate: {topic}")
        logger.info(f"🎙️ Participants: {participant_agents}")

        router = AgentRouter()
        transcript = []
        agents_loaded = []

        # Load all participant agents
        for agent_name in participant_agents:
            agent_class = router.AGENT_MAP.get(agent_name)
            if agent_class:
                try:
                    agent = agent_class(user=self.user)
                    agents_loaded.append({
                        'name': agent_name,
                        'agent': agent,
                        'role': self._infer_debate_role(agent_name)
                    })
                    logger.info(f"✅ Loaded {agent_name} as {agents_loaded[-1]['role']}")
                except Exception as e:
                    logger.warning(f"Failed to load {agent_name}: {e}")
            else:
                logger.warning(f"Agent {agent_name} not found in router")

        if len(agents_loaded) < 2:
            return {
                "success": False,
                "error": f"Need at least 2 agents for debate, only loaded {len(agents_loaded)}",
                "agents_requested": participant_agents,
                "agents_loaded": [a['name'] for a in agents_loaded]
            }

        # Run the debate rounds
        conversation_history = []

        for round_num in range(1, rounds + 1):
            logger.info(f"🎙️ Round {round_num}/{rounds}")

            for participant in agents_loaded:
                agent = participant['agent']
                agent_name = participant['name']
                role = participant['role']

                # Build the debate prompt with conversation history
                history_summary = "\n".join([
                    f"- {t['speaker']}: {t['text'][:200]}..."
                    for t in conversation_history[-6:]  # Last 6 turns
                ]) if conversation_history else "This is the opening round."

                debate_task = f"""You are participating in a podcast debate about: {topic}

Your role in this debate: {role}
Current round: {round_num} of {rounds}

Previous discussion:
{history_summary}

Provide your perspective in 2-4 sentences. Be direct, engaging, and draw on your expertise.
{"Make a strong opening statement." if round_num == 1 and not conversation_history else "Respond to the previous points and advance the discussion."}
{"Summarize your key position for the conclusion." if round_num == rounds else ""}"""

                try:
                    # Session 739: Pass spider_context to sub-agents for real intelligence
                    result = agent.execute(
                        task=debate_task,
                        context={'debate_topic': topic, 'round': round_num},
                        scifi_context=getattr(self, '_current_scifi_context', {}),
                        spider_context=getattr(self, '_current_spider_context', {})
                    )

                    turn_text = result.message if result.success else f"{agent_name} declined to comment."

                    turn = {
                        'round': round_num,
                        'speaker': agent_name,
                        'role': role,
                        'text': turn_text,
                        'generated_by': 'real_agent'
                    }
                    transcript.append(turn)
                    conversation_history.append(turn)

                    logger.info(f"✅ {agent_name}: {turn_text[:100]}...")

                except Exception as e:
                    logger.error(f"Error getting response from {agent_name}: {e}")
                    transcript.append({
                        'round': round_num,
                        'speaker': agent_name,
                        'role': role,
                        'text': f"[{agent_name} encountered an error: {str(e)[:50]}]",
                        'generated_by': 'error'
                    })

        # Convert transcript to podcast script format
        script = self._transcript_to_script(topic, transcript, agents_loaded)

        logger.info(f"🎙️ [SESSION 653] Multi-agent debate complete: {len(transcript)} turns")

        return {
            "success": True,
            "topic": topic,
            "participants": [a['name'] for a in agents_loaded],
            "participant_roles": {a['name']: a['role'] for a in agents_loaded},
            "rounds": rounds,
            "transcript": transcript,
            "script": script,
            "total_turns": len(transcript),
            "is_cross_domain": True,
            "generated_by": "real_multi_agent_debate"
        }

    def _infer_debate_role(self, agent_name: str) -> str:
        """Infer a debate role based on agent name."""
        name_lower = agent_name.lower()

        if any(x in name_lower for x in ['coordinator', 'moderator', 'orchestrator']):
            return 'MODERATOR'
        elif any(x in name_lower for x in ['bull', 'advocate', 'optimist']):
            return 'ADVOCATE'
        elif any(x in name_lower for x in ['bear', 'skeptic', 'contrarian', 'critic']):
            return 'SKEPTIC'
        elif any(x in name_lower for x in ['analyst', 'research', 'data']):
            return 'ANALYST'
        else:
            return 'EXPERT'

    def _transcript_to_script(
        self,
        topic: str,
        transcript: List[Dict[str, Any]],
        participants: List[Dict[str, Any]]
    ) -> str:
        """Convert debate transcript to podcast script format."""
        participant_names = [p['name'] for p in participants]

        script = f"""# Cross-Domain AI Debate: {topic}

[INTRO MUSIC - 5 seconds]

HOST: Welcome to AI Debates! Today we have a special cross-domain discussion featuring {', '.join(participant_names)}.
Our topic: {topic}

Let's hear from our participants!

"""
        current_round = 0
        for turn in transcript:
            if turn['round'] != current_round:
                current_round = turn['round']
                script += f"\n[ROUND {current_round}]\n\n"

            script += f"{turn['speaker']} ({turn['role']}): {turn['text']}\n\n"

        script += """[OUTRO]

HOST: That was a fascinating debate! Thank you to all our participants for their unique perspectives.

[OUTRO MUSIC - 5 seconds]
"""
        return script

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
