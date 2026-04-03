"""
AI Series Workflow Agent - Session 445 + Session 449 Learning Loops

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

Session 449 Additions:
- Learning loops at each pipeline stage
- Style preset recommendations based on historical performance
- Voice selection optimization
- Automatic feedback collection after episode completion

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
import uuid
from typing import Dict, Any, List, Optional
from decimal import Decimal

from core.agents.base_agent import BaseAgent, AgentResult
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


def analyze_series_workflow_with_ml(series_data: dict) -> dict:
    """Analyze series workflow data using ML models (Text)."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()
        result = router.auto_route(
            data=series_data,
            task_hint=TaskType.TEXT,
            max_models=2
        )
        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'text'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'series_optimization': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML series workflow analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


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

USER UPLOADS (Session 451):
Users can upload their own videos and images to use in series:
- Use list_uploaded_content to see available uploaded media
- Use use_uploaded_content to assign uploaded videos/images to episodes
- Uploaded videos can replace AI-generated videos (usage: main_video)
- Uploaded images can serve as character or scene references (usage: character_reference, scene_reference)

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
                            "enum": [
                                "pixar", "disney", "dreamworks", "cartoon", "anime", "ghibli",
                                "south_park", "simpsons", "family_guy", "adventure_time",
                                "gravity_falls", "rick_and_morty", "looney_tunes", "bojack",
                                "chibi", "comic", "watercolor", "gouache", "3d_render"
                            ],
                            "description": "Visual style preset - MUST be one of the listed options. Use 'pixar' for 3D Pixar style, 'cartoon' for general animation, 'anime' for Japanese style, etc."
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
        },
        {
            "type": "function",
            "function": {
                "name": "use_uploaded_content",
                "description": "Use user-uploaded videos or images in the series instead of generating new content. This allows incorporating existing media into episodes.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content_type": {
                            "type": "string",
                            "enum": ["video", "image"],
                            "description": "Type of content to use"
                        },
                        "content_id": {
                            "type": "string",
                            "description": "ID of the uploaded video or image to use"
                        },
                        "episode_number": {
                            "type": "integer",
                            "description": "Episode number to use this content in (optional, applies to next generated episode if not specified)"
                        },
                        "usage": {
                            "type": "string",
                            "enum": ["background", "main_video", "character_reference", "scene_reference"],
                            "description": "How to use the uploaded content in the episode"
                        }
                    },
                    "required": ["content_type", "content_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_uploaded_content",
                "description": "List all user-uploaded videos and images available for use in the series",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content_type": {
                            "type": "string",
                            "enum": ["video", "image", "all"],
                            "description": "Filter by content type (default: all)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of items to return (default: 20)"
                        }
                    }
                }
            }
        }
    ]

    def __init__(self, user=None):
        super().__init__(user)
        self._router = None
        self._learning_service = None
        # Series state maintained across execute()
        self._series_config = {}
        self._style_config = {}
        self._characters = []
        self._episode_results = []
        self._series_id = None  # Track current series for DB updates
        # Session 451: Uploaded content for use in episodes
        # Format: {episode_number: {'video': content_info, 'image': content_info}}
        self._uploaded_content = {}

    @property
    def learning_service(self):
        """Lazy-load PipelineLearningService for feedback collection."""
        if self._learning_service is None:
            try:
                from core.services.pipeline_learning import get_pipeline_learning_service
                self._learning_service = get_pipeline_learning_service()
            except Exception as e:
                logger.warning(f"Could not load learning service: {e}")
        return self._learning_service

    @property
    def router(self):
        """Lazy-load AgentRouter for delegation."""
        if self._router is None:
            from core.agent_router import AgentRouter
            self._router = AgentRouter(user=self.user)
        return self._router

    def _call_agent_with_retry(
        self,
        agent_name: str,
        task: str,
        context: Dict[str, Any],
        max_retries: int = 3,
        base_delay: float = 2.0
    ) -> 'AgentResult':
        """
        Call an agent with retry logic and exponential backoff.

        Args:
            agent_name: Name of the agent to call (e.g., "ImageAgent")
            task: The task to perform
            context: Context dict for the agent
            max_retries: Maximum number of retry attempts (default 3)
            base_delay: Base delay in seconds between retries (default 2.0)

        Returns:
            AgentResult from the agent
        """
        last_result = None

        for attempt in range(1, max_retries + 1):
            logger.info(f"Calling {agent_name} (attempt {attempt}/{max_retries})")

            result = self.router.route(
                agent_name=agent_name,
                task=task,
                context=context
            )

            if result.success:
                if attempt > 1:
                    logger.info(f"{agent_name} succeeded on attempt {attempt}")
                return result

            last_result = result
            error_msg = result.error or "Unknown error"
            logger.warning(f"{agent_name} failed on attempt {attempt}: {error_msg}")

            # Don't sleep after the last attempt
            if attempt < max_retries:
                # Exponential backoff: 2s, 4s, 8s, etc.
                delay = base_delay * (2 ** (attempt - 1))
                logger.info(f"Retrying {agent_name} in {delay:.1f} seconds...")
                time.sleep(delay)

        logger.error(f"{agent_name} failed after {max_retries} attempts")
        return last_result

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
        scifi_context = scifi_context or {}
        spider_context = spider_context or {}

        # Session 529: Build intelligent prompt with full context
        self._intelligent_context = self._build_intelligent_prompt(task, scifi_context, spider_context)

        # Reset state for new series
        self._series_config = {}
        self._style_config = {}
        self._characters = []
        self._episode_results = []
        self._series_id = None

        with self.time_travel_session("ai_series_workflow", task, input_data=context):
            try:
                # Handle simple diagnostic/identification queries
                task_lower = task.lower()
                if any(keyword in task_lower for keyword in ['state your name', 'who are you', 'your capability', 'what can you do', 'introduce yourself']):
                    execution_time = int((time.time() - start_time) * 1000)
                    return AgentResult(
                        success=True,
                        message=f"I am {self.name}, a master orchestrator for multi-episode AI content series. One capability: I coordinate ResearchAgent, ImageAgent, VideoAgent, and AudioAgent through a 6-stage pipeline to create complete educational, entertainment, or marketing series with consistent characters, coherent story arcs, and unified visual style.",
                        data={'type': 'self_description', 'capabilities': ['research', 'planning', 'character_design', 'script_generation', 'voiceover', 'video_production']},
                        agent_name=self.name,
                        execution_time_ms=execution_time
                    )

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

            # If no user, return a mock series object for planning purposes
            if not self.user:
                logger.info("No user provided - returning conceptual series plan")
                # Return a simple object with required attributes for planning
                class ConceptualSeries:
                    def __init__(self, task, context):
                        import uuid
                        from datetime import datetime
                        self.id = str(uuid.uuid4())
                        self.name = task[:200]
                        self.description = task
                        self.episode_count = min(context.get('episode_count', 3), 5)
                        self.target_audience = context.get('target_audience', 'general audience')
                        self.is_conceptual = True
                        self.style_config = {}
                        self.character_profiles = []
                        self.status = 'planning'
                        self.generation_progress = 0
                        self.updated_at = datetime.now()

                    def save(self, *args, **kwargs):
                        """No-op save for conceptual series."""
                        pass

                    def refresh_from_db(self):
                        """No-op refresh for conceptual series."""
                        pass

                    def complete_generation(self):
                        """Mark conceptual series as complete."""
                        self.status = 'complete'
                        self.generation_progress = 100

                    def fail(self, error_message: str, stage: str = 'unknown'):
                        """Mark conceptual series as failed."""
                        self.status = 'failed'
                        self.error_message = error_message
                        self.failed_at_stage = stage

                return ConceptualSeries(task, context)

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

            # Session 451: User upload integration
            elif tool_name == "use_uploaded_content":
                return self._handle_use_uploaded_content(arguments)

            elif tool_name == "list_uploaded_content":
                return self._handle_list_uploaded_content(arguments)

            else:
                # Session 988: Fall through to BaseAgent for web_search + delegation
                return super()._execute_tool_call(tool_name, arguments)

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

    def _get_recommended_style(self) -> Dict[str, Any]:
        """Get recommended style based on learning from historical performance."""
        if not self.learning_service:
            return {'style_preset': 'pixar', 'source': 'default'}

        target_audience = self._series_config.get('target_audience', '')
        series_type = self._series_config.get('series_type', '')

        recommendation = self.learning_service.get_best_style_for_context(
            target_audience=target_audience,
            series_type=series_type,
            fallback='pixar'
        )

        if recommendation.get('source') == 'learned':
            logger.info(
                f"Learning recommended {recommendation['style_preset']} style "
                f"(rating: {recommendation['avg_rating']:.1f}/5, confidence: {recommendation['confidence']:.0%})"
            )
        return recommendation

    def _handle_lock_style(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle lock_style tool call - saves to AISeries.style_config.

        Session 449: Uses learning recommendations if no style specified.
        """
        # Check if style was explicitly provided
        explicit_style = arguments.get('style_preset')

        # If no explicit style, check learning recommendations
        if not explicit_style:
            recommendation = self._get_recommended_style()
            style_preset = recommendation.get('style_preset', 'pixar')
            recommendation_source = recommendation.get('source', 'default')
            logger.info(f"Using {recommendation_source} style recommendation: {style_preset}")
        else:
            style_preset = explicit_style
            recommendation_source = 'user_specified'

        color_palette = arguments.get('color_palette', ['#4ECDC4', '#FF6B6B', '#45B7D1'])
        art_direction = arguments.get('art_direction', 'friendly, colorful, professional')

        self._style_config = {
            'style_preset': style_preset,
            'color_palette': color_palette,
            'art_direction': art_direction,
            'recommendation_source': recommendation_source  # Track where recommendation came from
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

    # Session 451: User upload integration handlers

    def _handle_use_uploaded_content(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle use_uploaded_content tool call - associates uploaded media with an episode.

        This allows users to use their own uploaded videos/images in series episodes
        instead of AI-generated content.
        """
        content_type = arguments.get('content_type')  # 'video' or 'image'
        content_id = arguments.get('content_id')
        episode_number = arguments.get('episode_number', 0)  # 0 means apply to next episode
        usage = arguments.get('usage', 'main_video')

        if not content_type or not content_id:
            return {'success': False, 'error': 'content_type and content_id are required'}

        # Verify the content exists and belongs to the user
        content_info = None
        try:
            if content_type == 'video':
                from content.models import VideoHistory
                video = VideoHistory.objects.get(id=content_id, user=self.user)
                content_info = {
                    'id': str(video.id),
                    'type': 'video',
                    'filename': video.original_filename or video.title,
                    'url': video.video_url if hasattr(video, 'video_url') else None,
                    'file_path': video.video_file.url if video.video_file else None,
                    'duration': video.duration,
                    'resolution': f"{video.width}x{video.height}" if video.width else None,
                    'usage': usage
                }
            elif content_type == 'image':
                from content.models import ImageHistory
                image = ImageHistory.objects.get(id=content_id, user=self.user)
                content_info = {
                    'id': str(image.id),
                    'type': 'image',
                    'filename': image.original_filename or image.prompt[:50],
                    'url': image.image_url,
                    'file_path': image.original_file.url if image.original_file else None,
                    'size': f"{image.width}x{image.height}" if image.width else None,
                    'usage': usage
                }
            else:
                return {'success': False, 'error': f'Invalid content_type: {content_type}'}

        except Exception as e:
            logger.error(f"Failed to find uploaded content {content_id}: {e}")
            return {'success': False, 'error': f'Content not found: {content_id}'}

        # Store the content for use in episode generation
        if episode_number not in self._uploaded_content:
            self._uploaded_content[episode_number] = {}
        self._uploaded_content[episode_number][content_type] = content_info

        return {
            'success': True,
            'content': content_info,
            'episode_number': episode_number if episode_number > 0 else 'next',
            'message': f"Registered {content_type} '{content_info['filename']}' for episode {episode_number if episode_number > 0 else 'generation'}"
        }

    def _handle_list_uploaded_content(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle list_uploaded_content tool call - lists user's available uploaded media.
        """
        content_type = arguments.get('content_type', 'all')
        limit = arguments.get('limit', 20)

        results = {'videos': [], 'images': []}

        try:
            # Get uploaded videos
            if content_type in ('all', 'video'):
                from content.models import VideoHistory
                videos = VideoHistory.objects.filter(
                    user=self.user,
                    source_type='uploaded'
                ).order_by('-created_at')[:limit]

                for video in videos:
                    results['videos'].append({
                        'id': str(video.id),
                        'filename': video.original_filename or video.title,
                        'duration': video.duration,
                        'resolution': f"{video.width}x{video.height}" if video.width else None,
                        'created_at': video.created_at.isoformat() if video.created_at else None
                    })

            # Get uploaded images
            if content_type in ('all', 'image'):
                from content.models import ImageHistory
                images = ImageHistory.objects.filter(
                    user=self.user,
                    source_type='uploaded'
                ).order_by('-created_at')[:limit]

                for image in images:
                    results['images'].append({
                        'id': str(image.id),
                        'filename': image.original_filename or image.prompt[:50] if image.prompt else 'Untitled',
                        'size': f"{image.width}x{image.height}" if image.width else None,
                        'created_at': image.created_at.isoformat() if image.created_at else None
                    })

        except Exception as e:
            logger.error(f"Failed to list uploaded content: {e}")
            return {'success': False, 'error': str(e)}

        return {
            'success': True,
            'videos': results['videos'],
            'images': results['images'],
            'total_videos': len(results['videos']),
            'total_images': len(results['images']),
            'message': f"Found {len(results['videos'])} videos and {len(results['images'])} images"
        }

    def _get_uploaded_content(self, episode_number: int, content_type: str) -> Optional[Dict[str, Any]]:
        """
        Get uploaded content for a specific episode and content type.

        Checks both episode-specific registrations and fallback to episode 0 (global).
        """
        # Check episode-specific first
        if episode_number in self._uploaded_content:
            content = self._uploaded_content[episode_number].get(content_type)
            if content:
                return content

        # Fallback to global (episode 0)
        if 0 in self._uploaded_content:
            content = self._uploaded_content[0].get(content_type)
            if content:
                return content

        return None

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

        # 1. Generate character/scene images (check for uploads first - Session 451)
        character_result = None
        style_preset = self._style_config.get('style_preset', 'pixar')
        logger.info(f"Episode {episode_number}: self._characters = {len(self._characters)} characters, style={style_preset}")

        # Check for uploaded image to use as reference
        uploaded_image = self._get_uploaded_content(episode_number, 'image')
        if uploaded_image and uploaded_image.get('usage') in ('character_reference', 'scene_reference'):
            # Use uploaded image as reference
            logger.info(f"Using uploaded image reference for episode {episode_number}: {uploaded_image.get('filename')}")
            episode_result['assets']['images'] = [{
                'source': 'uploaded',
                'id': uploaded_image.get('id'),
                'url': uploaded_image.get('url') or uploaded_image.get('file_path'),
                'filename': uploaded_image.get('filename'),
                'usage': uploaded_image.get('usage')
            }]
            character_result = {
                'success': True,
                'source': 'uploaded',
                'images': episode_result['assets']['images'],
                'character': self._characters[0]['name'] if self._characters else 'reference'
            }

        elif self._characters:
            # Generate images (original behavior)
            main_character = self._characters[0]
            char_name = main_character.get('name', 'character')
            # Keep description short (max 100 chars) to avoid Stability AI 400 errors
            char_desc = main_character.get('description', '')[:100]
            scene_desc = synopsis[:80] if synopsis else title

            # Simple, focused prompt - let the style preset do the heavy lifting
            image_task = f"Create {char_name} in a {scene_desc} scene"
            logger.info(f"Generating images for {char_name} with style={style_preset}")

            # Use retry logic for ImageAgent - Stability AI can be flaky
            image_result = self._call_agent_with_retry(
                agent_name="ImageAgent",
                task=image_task,
                context={
                    'count': 2,
                    'style': style_preset,  # This maps to our 80+ built-in style presets
                    'series_episode': episode_number,
                    'character_hint': char_desc  # Optional hint, not in main prompt
                },
                max_retries=3,
                base_delay=2.0
            )

            if image_result and image_result.success:
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

        # 4. Generate video (check for uploaded content first - Session 451)
        video_result_data = None

        # Check if user has registered uploaded video for this episode
        uploaded_video = self._get_uploaded_content(episode_number, 'video')
        if uploaded_video:
            # Use uploaded video instead of generating
            logger.info(f"Using uploaded video for episode {episode_number}: {uploaded_video.get('filename')}")
            video_result_data = {
                'source': 'uploaded',
                'video_id': uploaded_video.get('id'),
                'filename': uploaded_video.get('filename'),
                'url': uploaded_video.get('url') or uploaded_video.get('file_path'),
                'duration': uploaded_video.get('duration'),
                'resolution': uploaded_video.get('resolution')
            }
            episode_result['assets']['video'] = video_result_data

        elif episode_result['assets'].get('images'):
            # Generate video from images (original behavior)
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

        # Session 449: Record automatic feedback for learning
        self._record_episode_feedback(
            episode_number=episode_number,
            episode_id=str(db_episode.id) if db_episode else None,
            episode_result=episode_result
        )

        return {
            'success': True,
            'episode_number': episode_number,
            'title': title,
            'episode_id': str(db_episode.id) if db_episode else None,
            'assets_generated': list(episode_result['assets'].keys()),
            'message': f"Generated episode {episode_number}: {title}"
        }

    def _record_episode_feedback(
        self,
        episode_number: int,
        episode_id: str,
        episode_result: Dict[str, Any]
    ):
        """Record automatic feedback for a completed episode (Session 449 Learning Loops)."""
        if not self.learning_service:
            return

        try:
            # Calculate automatic quality scores based on asset generation success
            assets = episode_result.get('assets', {})
            script = episode_result.get('script', '')

            # Script stage feedback (based on length and presence)
            if script:
                script_words = len(script.split())
                # Score based on target range (200-300 words is optimal)
                if 180 <= script_words <= 350:
                    script_rating = 4.5
                elif 100 <= script_words < 180 or 350 < script_words <= 500:
                    script_rating = 3.5
                else:
                    script_rating = 2.5

                self.learning_service.record_stage_feedback(
                    stage='script',
                    rating=script_rating,
                    context={
                        'series_type': self._series_config.get('series_type', ''),
                        'target_audience': self._series_config.get('target_audience', ''),
                        'word_count': script_words,
                        'arc_position': episode_result.get('arc_position', '')
                    },
                    series_id=self._series_id,
                    episode_id=episode_id,
                    feedback_type='automated',
                    comment=f"Automated: {script_words} words generated"
                )

            # Image stage feedback (based on success of image generation)
            if 'images' in assets and assets['images']:
                image_count = len(assets['images'])
                image_rating = 4.0 if image_count >= 2 else 3.5 if image_count == 1 else 2.0

                self.learning_service.record_stage_feedback(
                    stage='image',
                    rating=image_rating,
                    context={
                        'style_preset': self._style_config.get('style_preset', ''),
                        'target_audience': self._series_config.get('target_audience', ''),
                        'series_type': self._series_config.get('series_type', ''),
                        'image_count': image_count
                    },
                    series_id=self._series_id,
                    episode_id=episode_id,
                    feedback_type='automated',
                    comment=f"Automated: {image_count} images generated"
                )

            # Voice stage feedback
            if 'voice' in assets:
                self.learning_service.record_stage_feedback(
                    stage='voice',
                    rating=4.0,  # Successful voice generation
                    context={
                        'series_type': self._series_config.get('series_type', ''),
                        'target_audience': self._series_config.get('target_audience', ''),
                        'voice_style': self._characters[0].get('voice_style', '') if self._characters else ''
                    },
                    series_id=self._series_id,
                    episode_id=episode_id,
                    feedback_type='automated',
                    comment="Automated: Voice generated successfully"
                )

            # Video stage feedback
            if 'video' in assets:
                self.learning_service.record_stage_feedback(
                    stage='video',
                    rating=4.0,  # Successful video generation
                    context={
                        'style_preset': self._style_config.get('style_preset', ''),
                        'series_type': self._series_config.get('series_type', ''),
                        'target_audience': self._series_config.get('target_audience', '')
                    },
                    series_id=self._series_id,
                    episode_id=episode_id,
                    feedback_type='automated',
                    comment="Automated: Video generated successfully"
                )

            logger.info(f"Recorded learning feedback for episode {episode_number}")

        except Exception as e:
            logger.warning(f"Failed to record episode feedback: {e}")

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
                # Session 876: Increased tokens for GPT-5-mini reasoning headroom
                response = self.client.chat.completions.create(
                    model="gpt-5.2",
                    messages=[{"role": "user", "content": script_prompt}],
                    max_completion_tokens=4000
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
