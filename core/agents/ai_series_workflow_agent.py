"""
AI Series Workflow Agent - Session 445

Master orchestrator that creates complete AI content series by chaining
specialized agents through a 6-stage pipeline:

1. RESEARCH - Query spiders for trending topics and audience analysis
2. PLANNING - Create series outline, story arc, character profiles
3. CHARACTER - Generate consistent character visuals (ImageAgent)
4. SCRIPT - Generate episode scripts/narration (GPT)
5. VOICE - Generate voiceovers (AudioAgent)
6. VIDEO - Generate video content (VideoAgent)

Design Decisions:
- Series Types: educational, entertainment, marketing
- Episode Count: 1-5 per series
- Generation Mode: Sequential (for story continuity)

Usage:
    from core.agent_router import AgentRouter

    router = AgentRouter(user=request.user)
    result = router.route(
        "AISeriesWorkflowAgent",
        "Create an educational series about space for kids",
        context={'episode_count': 3, 'series_type': 'educational'}
    )
"""

import logging
import time
import json
import uuid
from typing import Dict, Any, List, Optional
from decimal import Decimal

from core.agents.base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)


def make_json_serializable(obj):
    """
    Convert an object to be JSON serializable.
    Handles UUIDs, Decimals, and nested structures.
    """
    if isinstance(obj, uuid.UUID):
        return str(obj)
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(make_json_serializable(item) for item in obj)
    return obj


class AISeriesWorkflowAgent(BaseAgent):
    """
    Master orchestrator for multi-episode AI content series.

    Coordinates multiple specialized agents to create complete content
    series with:
    - Consistent characters across episodes
    - Coherent story arcs
    - Unified visual style
    - Sequential episode generation
    """

    name = "AISeriesWorkflowAgent"

    system_prompt = """You are the AI Series Workflow Agent - a master orchestrator that creates complete multi-episode content series.

Your job is to coordinate specialized agents to create professional content series:
- Educational series (tutorials, explainers, how-tos)
- Entertainment series (cartoons, stories, shorts)
- Marketing series (ad campaigns, brand stories)

For each series you:
1. Research the topic and audience using the ResearchAgent
2. Plan the story arc and episode structure
3. Create consistent character designs using ImageAgent
4. Generate scripts for each episode
5. Create voiceovers using AudioAgent
6. Produce video content using VideoAgent
7. Package everything for delivery

You MUST maintain consistency across all episodes:
- Same characters with consistent visual appearance
- Coherent story progression
- Unified visual style
- Consistent voice/tone

When delegating to agents, provide detailed context including:
- Series theme and target audience
- Character descriptions (locked style)
- Episode-specific requirements
- Prior episode context for continuity

Available agents to delegate to:
- ResearchAgent: Web search and spider network queries
- ImageAgent: Image generation (characters, thumbnails, scenes)
- VideoAgent: Video generation and animation
- AudioAgent: Voice generation and sound effects
- ContentStrategyAgent: Content planning and strategy
"""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "delegate_to_agent",
                "description": "Delegate a subtask to a specialist agent. Use this to orchestrate the series creation pipeline.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "agent_name": {
                            "type": "string",
                            "enum": [
                                "ResearchAgent",
                                "ImageAgent",
                                "VideoAgent",
                                "AudioAgent",
                                "ContentStrategyAgent"
                            ],
                            "description": "The specialist agent to delegate to"
                        },
                        "task": {
                            "type": "string",
                            "description": "The specific task for the agent to perform"
                        },
                        "context": {
                            "type": "object",
                            "description": "Additional context (style, character details, episode info)",
                            "default": {}
                        }
                    },
                    "required": ["agent_name", "task"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "plan_series",
                "description": "Plan the overall series structure including episode arcs and character profiles",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "series_theme": {
                            "type": "string",
                            "description": "Main theme/topic of the series"
                        },
                        "episode_count": {
                            "type": "integer",
                            "description": "Number of episodes (1-5)",
                            "minimum": 1,
                            "maximum": 5
                        },
                        "series_type": {
                            "type": "string",
                            "enum": ["educational", "entertainment", "marketing"],
                            "description": "Type of content series"
                        },
                        "target_audience": {
                            "type": "string",
                            "description": "Target audience description"
                        }
                    },
                    "required": ["series_theme", "episode_count", "series_type"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "lock_style",
                "description": "Lock the visual style for consistency across all episodes",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "style_preset": {
                            "type": "string",
                            "description": "Visual style preset (pixar, anime, corporate, etc.)"
                        },
                        "color_palette": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of hex colors for the series palette"
                        },
                        "art_direction": {
                            "type": "string",
                            "description": "Art direction notes (friendly, dark, minimalist, etc.)"
                        }
                    },
                    "required": ["style_preset"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "define_character",
                "description": "Define a character for consistent generation across episodes",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Character name"
                        },
                        "role": {
                            "type": "string",
                            "enum": ["main", "supporting", "recurring", "guest"],
                            "description": "Character's role in the series"
                        },
                        "description": {
                            "type": "string",
                            "description": "Detailed character description for image generation"
                        },
                        "personality": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Personality traits"
                        },
                        "voice_style": {
                            "type": "string",
                            "description": "Voice style for TTS (friendly, authoritative, etc.)"
                        }
                    },
                    "required": ["name", "role", "description"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "generate_episode",
                "description": "Generate a complete episode with all assets",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "episode_number": {
                            "type": "integer",
                            "description": "Episode number in the series"
                        },
                        "title": {
                            "type": "string",
                            "description": "Episode title"
                        },
                        "synopsis": {
                            "type": "string",
                            "description": "Episode synopsis/summary"
                        },
                        "arc_position": {
                            "type": "string",
                            "enum": ["intro", "rising", "climax", "falling", "conclusion"],
                            "description": "Position in story arc"
                        }
                    },
                    "required": ["episode_number", "title", "synopsis"]
                }
            }
        }
    ]

    def __init__(self, user=None):
        super().__init__(user)
        self._router = None
        # Series state maintained across execute()
        self._series_config = {}
        self._style_config = {}
        self._characters = []
        self._episode_results = []
        self._series_id = None  # Track current series for DB updates

    @property
    def router(self):
        """Lazy-load AgentRouter for delegation."""
        if self._router is None:
            from core.agent_router import AgentRouter
            self._router = AgentRouter(user=self.user)
        return self._router

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """
        Execute series creation workflow.

        This orchestrates the complete series generation:
        1. Parse series requirements
        2. Research phase
        3. Planning phase (story arc, characters)
        4. For each episode: character → script → voice → video → package
        5. Return complete series

        Args:
            task: Series creation request (e.g., "Create educational series about space")
            context: Contains series_type, episode_count, target_audience
            scifi_context: Mood, evolution, memory context
            spider_context: Trends, market data

        Returns:
            AgentResult with series data and all episode results
        """
        start_time = time.time()

        # Reset state for new series
        self._series_config = {}
        self._style_config = {}
        self._characters = []
        self._episode_results = []
        self._series_id = None

        with self.time_travel_session("ai_series_workflow", task, input_data=context):
            try:
                # Validate task
                if not self._validate_task(task):
                    return AgentResult(
                        success=False,
                        error="Invalid task: Please provide a series creation request",
                        agent_name=self.name
                    )

                # Extract configuration from context
                episode_count = min(context.get('episode_count', 3), 5)  # Max 5
                series_type = context.get('series_type', 'educational')
                target_audience = context.get('target_audience', 'general audience')

                self._series_config = {
                    'episode_count': episode_count,
                    'series_type': series_type,
                    'target_audience': target_audience,
                    'prompt': task
                }

                # Create the series in database
                series = self._create_series_record(task, context)
                if not series:
                    return AgentResult(
                        success=False,
                        error="Failed to create series record",
                        agent_name=self.name
                    )

                # Track series ID for database updates in tool handlers
                self._series_id = str(series.id)

                # Build prompt with all context
                full_prompt = self._build_prompt_with_mythology_guard(
                    task, scifi_context, spider_context
                )

                # Add series-specific instructions
                full_prompt += f"""

## Series Configuration
- Series Type: {series_type}
- Episode Count: {episode_count}
- Target Audience: {target_audience}

## Instructions (FOLLOW ALL STEPS - DO NOT STOP EARLY)
1. First, use delegate_to_agent to research the topic with ResearchAgent
2. Then use plan_series to create the series structure
3. Use lock_style to define the visual style
4. Use define_character for each main character (at least 1)
5. **CRITICAL: You MUST call generate_episode for EACH episode from 1 to {episode_count}**
   - Call generate_episode with episode_number=1, then episode_number=2, etc.
   - Do NOT stop until you have called generate_episode for ALL {episode_count} episodes
   - Each generate_episode call creates the script, images, voice, and video

**IMPORTANT: The task is NOT complete until you have called generate_episode {episode_count} times.**

Start by researching the topic to understand trends and audience preferences.
"""

                # Execute GPT orchestration loop
                conversation_history = []
                max_iterations = 10  # More iterations for series workflow
                workflow_results = []

                for iteration in range(max_iterations):
                    # Add previous results context
                    if workflow_results:
                        context_str = "\n\nPrevious Steps:\n"
                        for wr in workflow_results[-5:]:  # Last 5 results
                            context_str += f"- {wr.get('tool', 'unknown')}: {wr.get('summary', '')[:100]}\n"
                        iteration_prompt = full_prompt + context_str
                    else:
                        iteration_prompt = full_prompt

                    gpt_response = self._call_openai(iteration_prompt, conversation_history)

                    # Check if GPT is done
                    if not gpt_response.get('tool_calls'):
                        # GPT finished - break loop
                        break

                    # Process tool calls
                    for tool_call in gpt_response.get('tool_calls', []):
                        tool_name = tool_call.get('name')
                        arguments = tool_call.get('arguments', {})

                        self.record_decision(
                            decision_type="series_tool_call",
                            action=f"Calling {tool_name}",
                            reasoning=f"Arguments: {str(arguments)[:100]}",
                            confidence=0.9
                        )

                        result = self._execute_tool_call(tool_name, arguments)
                        workflow_results.append({
                            'tool': tool_name,
                            'arguments': arguments,
                            'result': result,
                            'summary': str(result)[:200] if result else 'No result'
                        })

                        # Add tool result to conversation
                        conversation_history.append({
                            "role": "assistant",
                            "content": f"Tool {tool_name} result: {str(result)[:500]}"
                        })

                    # Update series progress
                    if series:
                        series.generation_progress = min(
                            int((iteration / max_iterations) * 100),
                            99
                        )
                        series.save(update_fields=['generation_progress', 'updated_at'])

                # Complete the series only if episodes were actually generated
                if series:
                    generated_count = len(self._episode_results)
                    expected_count = episode_count
                    if generated_count >= expected_count:
                        series.complete_generation()
                        logger.info(f"Series completed: {generated_count}/{expected_count} episodes generated")
                    else:
                        logger.warning(f"Series incomplete: only {generated_count}/{expected_count} episodes generated")
                        # Don't mark complete - keep in generating status

                # Build final result
                execution_time = int((time.time() - start_time) * 1000)

                result = AgentResult(
                    success=True,
                    message=f"Created {series_type} series with {len(self._episode_results)} episodes",
                    data={
                        'series_id': str(series.id) if series else None,
                        'series_name': series.name if series else task[:50],
                        'series_type': series_type,
                        'episode_count': len(self._episode_results),
                        'episodes': self._episode_results,
                        'style_config': self._style_config,
                        'characters': self._characters,
                        'workflow_results': workflow_results
                    },
                    agent_name=self.name,
                    execution_time_ms=execution_time,
                    tool_calls=[{
                        'name': wr.get('tool'),
                        'arguments': wr.get('arguments')
                    } for wr in workflow_results],
                    decisions_made=self._tt_decision_count
                )

                # Record learning outcome
                self._record_learning_outcome(
                    result, task, context,
                    spider_data_used=bool(spider_context),
                    scifi_context_used=bool(scifi_context)
                )

                # Share knowledge about successful series
                if result.success:
                    self._share_knowledge(
                        knowledge_type='content_idea',
                        title=f"Successful {series_type} series: {task[:50]}",
                        knowledge_value={
                            'series_type': series_type,
                            'episode_count': len(self._episode_results),
                            'style': self._style_config,
                            'characters': len(self._characters)
                        },
                        confidence=0.8
                    )

                return result

            except Exception as e:
                logger.error(f"AISeriesWorkflowAgent error: {e}", exc_info=True)

                # Mark series as failed
                try:
                    if 'series' in locals() and series:
                        series.fail(str(e), 'execute')
                except Exception:
                    pass

                return AgentResult(
                    success=False,
                    error=str(e),
                    agent_name=self.name,
                    execution_time_ms=int((time.time() - start_time) * 1000)
                )

    def _create_series_record(self, task: str, context: Dict[str, Any]) -> Optional[Any]:
        """Get existing series or create AISeries record in database."""
        try:
            from core.models_ai_series import AISeries, SeriesType

            # Check if series_id was passed in context (from Celery task)
            existing_series_id = context.get('series_id')
            if existing_series_id:
                try:
                    series = AISeries.objects.get(id=existing_series_id)
                    logger.info(f"Using existing AISeries: {series.id}")
                    return series
                except AISeries.DoesNotExist:
                    logger.warning(f"Series {existing_series_id} not found, creating new one")

            # Map series type
            type_mapping = {
                'educational': SeriesType.EDUCATIONAL,
                'entertainment': SeriesType.ENTERTAINMENT,
                'marketing': SeriesType.MARKETING
            }
            series_type = type_mapping.get(
                context.get('series_type', 'educational'),
                SeriesType.EDUCATIONAL
            )

            series = AISeries.objects.create(
                name=task[:200],
                description=task,
                prompt=task,
                series_type=series_type,
                episode_count=min(context.get('episode_count', 3), 5),
                target_audience=context.get('target_audience', 'general audience'),
                created_by=self.user
            )

            logger.info(f"Created AISeries: {series.id}")
            return series

        except Exception as e:
            logger.error(f"Failed to create series record: {e}")
            return None

    def _execute_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a tool call for the series workflow.

        Handles both internal tools (plan_series, lock_style, define_character)
        and delegation tools (delegate_to_agent).
        """
        try:
            if tool_name == "delegate_to_agent":
                return self._handle_delegation(arguments)

            elif tool_name == "plan_series":
                return self._handle_plan_series(arguments)

            elif tool_name == "lock_style":
                return self._handle_lock_style(arguments)

            elif tool_name == "define_character":
                return self._handle_define_character(arguments)

            elif tool_name == "generate_episode":
                return self._handle_generate_episode(arguments)

            else:
                return {"error": f"Unknown tool: {tool_name}"}

        except Exception as e:
            logger.error(f"Tool execution error ({tool_name}): {e}")
            return {"error": str(e)}

    def _handle_delegation(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle delegate_to_agent tool call."""
        agent_name = arguments.get('agent_name')
        subtask = arguments.get('task')
        subtask_context = arguments.get('context', {})

        # Add series context to subtask
        subtask_context['series_config'] = self._series_config
        subtask_context['style_config'] = self._style_config
        subtask_context['characters'] = self._characters

        try:
            result = self.router.route(
                agent_name=agent_name,
                task=subtask,
                context=subtask_context
            )

            return {
                'agent': agent_name,
                'success': result.success,
                'message': result.message,
                'data': result.data
            }

        except Exception as e:
            logger.error(f"Delegation to {agent_name} failed: {e}")
            return {'agent': agent_name, 'success': False, 'error': str(e)}

    def _handle_plan_series(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle plan_series tool call."""
        series_theme = arguments.get('series_theme')
        episode_count = arguments.get('episode_count', 3)
        series_type = arguments.get('series_type', 'educational')
        target_audience = arguments.get('target_audience', 'general audience')

        # Generate episode outlines based on arc
        arc_positions = self._get_arc_positions(episode_count)

        episodes = []
        for i, arc_pos in enumerate(arc_positions, 1):
            episodes.append({
                'episode_number': i,
                'arc_position': arc_pos,
                'title': f"Episode {i}: {arc_pos.title()} - {series_theme}",
                'synopsis': f"Episode focusing on {arc_pos} of the {series_theme} story"
            })

        self._series_config.update({
            'series_theme': series_theme,
            'episode_count': episode_count,
            'series_type': series_type,
            'target_audience': target_audience,
            'episodes': episodes
        })

        return {
            'success': True,
            'series_theme': series_theme,
            'episode_count': episode_count,
            'episodes': episodes,
            'message': f"Planned {episode_count}-episode {series_type} series"
        }

    def _handle_lock_style(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle lock_style tool call - saves to AISeries.style_config."""
        style_preset = arguments.get('style_preset', 'pixar')
        color_palette = arguments.get('color_palette', ['#4ECDC4', '#FF6B6B', '#45B7D1'])
        art_direction = arguments.get('art_direction', 'friendly, colorful, professional')

        self._style_config = {
            'style_preset': style_preset,
            'color_palette': color_palette,
            'art_direction': art_direction
        }

        # Save to database
        if self._series_id:
            try:
                from core.models_ai_series import AISeries
                series = AISeries.objects.get(id=self._series_id)
                series.style_config = self._style_config
                series.save(update_fields=['style_config', 'updated_at'])
                logger.info(f"Saved style_config to series {self._series_id}: {style_preset}")
            except Exception as e:
                logger.error(f"Failed to save style_config: {e}")

        return {
            'success': True,
            'style_config': self._style_config,
            'message': f"Locked style: {style_preset} with {len(color_palette)} colors"
        }

    def _handle_define_character(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle define_character tool call - creates SeriesCharacter record."""
        character = {
            'name': arguments.get('name'),
            'role': arguments.get('role', 'main'),
            'description': arguments.get('description'),
            'personality': arguments.get('personality', []),
            'voice_style': arguments.get('voice_style', 'friendly')
        }

        self._characters.append(character)
        db_character_id = None

        # Create SeriesCharacter record in database
        if self._series_id:
            try:
                from core.models_ai_series import AISeries, SeriesCharacter
                series = AISeries.objects.get(id=self._series_id)

                db_character = SeriesCharacter.objects.create(
                    series=series,
                    name=character['name'],
                    role=character['role'],
                    description=character['description'],
                    personality_traits=character['personality'],  # Model uses personality_traits
                    voice_name=character['voice_style']  # Map voice_style to voice_name
                )
                db_character_id = str(db_character.id)
                logger.info(f"Created SeriesCharacter {db_character_id}: {character['name']}")
            except Exception as e:
                logger.error(f"Failed to create SeriesCharacter: {e}")

        return {
            'success': True,
            'character': character,
            'character_id': db_character_id,
            'total_characters': len(self._characters),
            'message': f"Defined character: {character['name']} ({character['role']})"
        }

    def _handle_generate_episode(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle generate_episode tool call - creates/updates SeriesEpisode record.

        Orchestrates the full episode generation:
        1. Generate character images (ImageAgent)
        2. Generate script
        3. Generate voiceover (AudioAgent)
        4. Generate video (VideoAgent)
        5. Save all results to SeriesEpisode in database
        """
        episode_number = arguments.get('episode_number', 1)
        title = arguments.get('title', f'Episode {episode_number}')
        synopsis = arguments.get('synopsis', '')
        arc_position = arguments.get('arc_position', 'intro')

        episode_result = {
            'episode_number': episode_number,
            'title': title,
            'synopsis': synopsis,
            'arc_position': arc_position,
            'assets': {}
        }

        # Get or create the SeriesEpisode record
        db_episode = None
        if self._series_id:
            try:
                from core.models_ai_series import AISeries, SeriesEpisode, EpisodeStatus
                series = AISeries.objects.get(id=self._series_id)

                # Get or create episode (episodes created on series creation)
                db_episode, created = SeriesEpisode.objects.get_or_create(
                    series=series,
                    episode_number=episode_number,
                    defaults={
                        'title': title,
                        'synopsis': synopsis,
                        'arc_position': arc_position
                    }
                )

                # Update episode info and start generation
                db_episode.title = title
                db_episode.synopsis = synopsis
                db_episode.arc_position = arc_position
                db_episode.status = EpisodeStatus.GENERATING
                db_episode.save(update_fields=['title', 'synopsis', 'arc_position', 'status', 'updated_at'])
                db_episode.start_generation()
                logger.info(f"Started generating episode {episode_number}: {title}")
            except Exception as e:
                logger.error(f"Failed to get/create SeriesEpisode: {e}")

        # 1. Generate character/scene images
        character_result = None
        if self._characters:
            main_character = self._characters[0]
            image_task = f"Create a scene for '{title}' featuring {main_character['name']}: {main_character['description']}. Style: {self._style_config.get('style_preset', 'pixar')}. Scene: {synopsis[:100]}"

            image_result = self.router.route(
                agent_name="ImageAgent",
                task=image_task,
                context={
                    'count': 2,
                    'style': self._style_config.get('style_preset', 'pixar'),
                    'series_episode': episode_number
                }
            )

            if image_result.success:
                episode_result['assets']['images'] = image_result.data.get('images', [])
                character_result = {
                    'success': True,
                    'images': image_result.data.get('images', []),
                    'character': main_character['name']
                }

        # 2. Generate script (using GPT directly)
        script = self._generate_episode_script(title, synopsis, arc_position)
        logger.info(f"Script generation returned: {len(script) if script else 0} chars")
        episode_result['script'] = script
        script_result = {'script': script, 'word_count': len(script.split()) if script else 0}

        # 3. Generate voiceover
        voice_result_data = None
        if script:
            # Take first 500 chars for voice preview
            voice_text = script[:500] if len(script) > 500 else script
            voice_task = f"Generate voiceover for episode '{title}': {voice_text}"

            voice_result = self.router.route(
                agent_name="AudioAgent",
                task=voice_task,
                context={
                    'voice_style': self._characters[0].get('voice_style', 'friendly') if self._characters else 'friendly'
                }
            )

            if voice_result.success:
                episode_result['assets']['voice'] = voice_result.data
                voice_result_data = voice_result.data

        # 4. Generate video (if we have images)
        video_result_data = None
        if episode_result['assets'].get('images'):
            first_image = episode_result['assets']['images'][0]
            image_id = first_image.get('id') if isinstance(first_image, dict) else None

            if image_id:
                video_task = f"Animate the scene for episode '{title}' - create a 6 second video"
                video_result = self.router.route(
                    agent_name="VideoAgent",
                    task=video_task,
                    context={
                        'image_id': str(image_id),
                        'duration': 6
                    }
                )

                if video_result.success:
                    episode_result['assets']['video'] = video_result.data
                    video_result_data = video_result.data

        # Store episode result in memory
        self._episode_results.append(episode_result)

        # Save all results to database
        if db_episode:
            try:
                db_episode.script = script or ''
                # Convert results to be JSON serializable (handles UUIDs, Decimals, etc.)
                db_episode.script_result = make_json_serializable(script_result)
                db_episode.character_result = make_json_serializable(character_result)
                db_episode.voice_result = make_json_serializable(voice_result_data)
                db_episode.video_result = make_json_serializable(video_result_data)
                # IMPORTANT: Save all fields BEFORE calling complete_generation()
                # complete_generation() only saves status fields, not content fields
                db_episode.save(update_fields=[
                    'script', 'script_result', 'character_result',
                    'voice_result', 'video_result', 'updated_at'
                ])
                db_episode.complete_generation()  # Sets status to COMPLETE
                logger.info(f"Saved episode {episode_number} to database: script={len(script or '')} chars, character_result={bool(character_result)}")
            except Exception as e:
                logger.error(f"Failed to save episode to database: {e}")
                if db_episode:
                    try:
                        db_episode.fail(str(e), 'save')
                    except Exception:
                        pass

        return {
            'success': True,
            'episode_number': episode_number,
            'title': title,
            'episode_id': str(db_episode.id) if db_episode else None,
            'assets_generated': list(episode_result['assets'].keys()),
            'message': f"Generated episode {episode_number}: {title}"
        }

    def _generate_episode_script(
        self,
        title: str,
        synopsis: str,
        arc_position: str,
        max_retries: int = 3
    ) -> str:
        """Generate a script for the episode using GPT with retry logic."""
        logger.info(f"Generating script for: {title}")

        script_prompt = f"""Write a short script/narration for an episode titled "{title}".

Synopsis: {synopsis}
Story Arc Position: {arc_position}
Series Type: {self._series_config.get('series_type', 'educational')}
Target Audience: {self._series_config.get('target_audience', 'general audience')}

Write a 200-300 word script that:
1. Fits the {arc_position} position in the story arc
2. Is appropriate for the target audience
3. Is engaging and informative
4. Could be used as voiceover narration

Script:"""

        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model="gpt-5-mini",
                    messages=[{"role": "user", "content": script_prompt}],
                    max_completion_tokens=1000
                )

                content = response.choices[0].message.content or ""
                logger.info(f"GPT script response (attempt {attempt + 1}): {len(content)} chars")

                # Validate we got actual content (at least 50 chars for a real script)
                if len(content.strip()) >= 50:
                    return content
                else:
                    logger.warning(f"Empty/short script response on attempt {attempt + 1}, retrying...")
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(1)  # Brief pause before retry

            except Exception as e:
                logger.error(f"Script generation error (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(1)

        # All retries failed - return fallback
        logger.error(f"All {max_retries} script generation attempts failed, using fallback")
        return f"Welcome to {title}. {synopsis}"

    def _get_arc_positions(self, episode_count: int) -> List[str]:
        """Get story arc positions based on episode count."""
        if episode_count == 1:
            return ['intro']
        elif episode_count == 2:
            return ['intro', 'conclusion']
        elif episode_count == 3:
            return ['intro', 'climax', 'conclusion']
        elif episode_count == 4:
            return ['intro', 'rising', 'climax', 'conclusion']
        else:  # 5 episodes
            return ['intro', 'rising', 'climax', 'falling', 'conclusion']


# Factory function
def get_ai_series_workflow_agent(user=None) -> AISeriesWorkflowAgent:
    """Get an AISeriesWorkflowAgent instance."""
    return AISeriesWorkflowAgent(user=user)
