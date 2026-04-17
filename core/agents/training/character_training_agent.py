"""
Character Training Agent - Clean Architecture
==============================================

Session 280: Phase 3 - Agent Architecture Unification

This agent handles character/style training using Replicate FLUX LoRA.

Tools Available:
    - create_character: Create a new character with training images
    - submit_training: Submit character for training
    - check_status: Check training status

Usage:
    from core.agents.training import CharacterTrainingAgent

    agent = CharacterTrainingAgent(user=request.user)
    result = agent.execute(
        task="Create a character called 'mychar' with these images",
        context={'name': 'mychar', 'trigger_word': 'MYCHAR'},
        scifi_context={},
        spider_context={}
    )
"""

import logging
import time
from typing import Dict, Any, List

from core.agents.base_agent import BaseAgent, AgentResult
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


def analyze_training_data_with_ml(training_data: dict) -> dict:
    """Analyze training data quality using ML models (Text + Clustering)."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()
        result = router.auto_route(
            data=training_data,
            task_hint=TaskType.TEXT,
            max_models=2
        )
        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'text'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'training_quality': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML training analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


class CharacterTrainingAgent(BaseAgent):
    """
    Character Training Agent - FLUX LoRA Training.

    This agent:
    1. Creates character models for training
    2. Submits training jobs to Replicate
    3. Monitors training status

    It CANNOT:
    - Generate images (use TrainedCreationAgent)
    - Edit images
    """

    name = "CharacterTrainingAgent"

    system_prompt = """You are CharacterTrainingAgent, the Character Training Specialist.

Your job is to help users train custom character/style models using FLUX LoRA:
- Validate training images (minimum 5-20 images required)
- Create training datasets
- Submit training jobs to Replicate
- Monitor training progress

Training Requirements:
- 5-20 high-quality training images
- Consistent subject/style across images
- Unique trigger word (e.g., 'MYCHAR' or 'MYSTYLE')
- Training takes ~20 minutes

When given a task:
1. Determine the operation needed (create, submit, check status)
2. Validate the parameters
3. Execute the appropriate operation
4. Report the result

You train models - you do NOT generate images with them (use TrainedCreationAgent)."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "create_character",
                "description": "Create a new character/style model for training",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name for the character model"
                        },
                        "trigger_word": {
                            "type": "string",
                            "description": "Trigger word to invoke the character (e.g., 'MYCHAR')"
                        },
                        "description": {
                            "type": "string",
                            "description": "Description of the character/style"
                        },
                        "image_urls": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "URLs of training images (5-20 required)"
                        },
                        "training_steps": {
                            "type": "integer",
                            "description": "Number of training steps",
                            "default": 1000
                        },
                        "auto_submit": {
                            "type": "boolean",
                            "description": "Automatically submit for training",
                            "default": False
                        }
                    },
                    "required": ["name", "trigger_word"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "submit_training",
                "description": "Submit a character for training on Replicate",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_id": {
                            "type": "string",
                            "description": "UUID of the character to train"
                        }
                    },
                    "required": ["character_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "check_status",
                "description": "Check training status for a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_id": {
                            "type": "string",
                            "description": "UUID of the character to check"
                        }
                    },
                    "required": ["character_id"]
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
        """Execute character training based on the task."""
        start_time = time.time()
        tool_calls_made = []

        # Session 736: Extract spider intelligence for real-time data
        spider_intel = self._extract_spider_intelligence(spider_context)
        if spider_intel['has_data']:
            logger.info(f"🕷️ {self.name} using spider intelligence")

        with self.time_travel_session("character_training", task, input_data=context):
            try:
                if not self._validate_task(task):
                    return AgentResult(
                        success=False,
                        error="Invalid or empty task",
                        agent_name=self.name
                    )

                self.record_decision(
                    decision_type="task_analysis",
                    action="Analyzing training request",
                    reasoning=f"Received task: {task[:100]}",
                    alternatives=["create_character", "submit_training", "check_status"],
                    confidence=0.9
                )

                full_prompt = self._build_intelligent_prompt(task, scifi_context, spider_context)
                logger.info(f"CharacterTrainingAgent executing: {task[:50]}...")

                gpt_response = self._call_openai(full_prompt)

                if gpt_response.get('tool_calls'):
                    for tool_call in gpt_response['tool_calls']:
                        tool_name = tool_call['name']
                        arguments = tool_call['arguments']

                        self.record_decision(
                            decision_type="tool_selection",
                            action=f"Calling {tool_name}",
                            reasoning=f"Training operation: {arguments}",
                            alternatives=[],
                            confidence=0.95
                        )

                        tool_result = self._execute_tool_call(tool_name, arguments)
                        tool_calls_made.append({
                            'tool': tool_name,
                            'arguments': arguments,
                            'result': tool_result
                        })

                        self.mark_decision_outcome(
                            success=tool_result.get('success', False),
                            result_summary=str(tool_result)[:100]
                        )

                    execution_time = int((time.time() - start_time) * 1000)

                    result = AgentResult(
                        success=True,
                        message="Character training operation completed",
                        data={
                            'task': task,
                            'tool_results': tool_calls_made,
                        },
                        agent_name=self.name,
                        execution_time_ms=execution_time,
                        decisions_made=self._tt_decision_count,
                        tool_calls=tool_calls_made
                    )

                    # Session 1006: Persist output to Deliverable
                    # Session 1092: render with shared helper for gate passing.
                    self._save_to_deliverable(
                        title=f"Character Training: {task[:80]}",
                        content=self._render_agent_output_markdown(
                            task=task,
                            summary=result.message,
                            tool_calls=tool_calls_made,
                        ),
                        deliverable_type='training',
                        category='Character Training',
                        tags=['training', 'character'],
                        metadata={'task': task[:200]},
                    )

                    # Session 380: Learning hooks for collective intelligence
                    self._record_learning_outcome(
                        result=result,
                        task=task,
                        context=context,
                        spider_data_used=bool(spider_context),
                        scifi_context_used=bool(scifi_context)
                    )
                    self._create_execution_memory(
                        result=result,
                        task=task,
                        memory_type="success",
                        importance=0.7
                    )

                    return result

                else:
                    result = AgentResult(
                        success=True,
                        message=gpt_response.get('content', ''),
                        data={'type': 'conversation'},
                        agent_name=self.name,
                        execution_time_ms=int((time.time() - start_time) * 1000)
                    )

                    # Session 380: Learning hooks for collective intelligence
                    self._record_learning_outcome(
                        result=result,
                        task=task,
                        context=context,
                        spider_data_used=bool(spider_context),
                        scifi_context_used=bool(scifi_context)
                    )
                    self._create_execution_memory(
                        result=result,
                        task=task,
                        memory_type="success",
                        importance=0.6
                    )

                    return result

            except Exception as e:
                logger.error(f"CharacterTrainingAgent error: {e}")
                result = AgentResult(
                    success=False,
                    error=str(e),
                    agent_name=self.name,
                    execution_time_ms=int((time.time() - start_time) * 1000)
                )

                # Session 380: Learning hooks for collective intelligence (failures too)
                self._record_learning_outcome(
                    result=result,
                    task=task,
                    context=context,
                    spider_data_used=bool(spider_context),
                    scifi_context_used=bool(scifi_context)
                )
                self._create_execution_memory(
                    result=result,
                    task=task,
                    memory_type="failure",
                    importance=0.8
                )

                return result

    def _execute_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a character training tool call."""
        if tool_name == "create_character":
            return self._create_character(
                name=arguments.get('name', ''),
                trigger_word=arguments.get('trigger_word', ''),
                description=arguments.get('description', ''),
                image_urls=arguments.get('image_urls', []),
                training_steps=arguments.get('training_steps', 1000),
                auto_submit=arguments.get('auto_submit', False)
            )

        elif tool_name == "submit_training":
            return self._submit_training(
                character_id=arguments.get('character_id', '')
            )

        elif tool_name == "check_status":
            return self._check_status(
                character_id=arguments.get('character_id', '')
            )

        return super()._execute_tool_call(tool_name, arguments)

    def _create_character(
        self,
        name: str,
        trigger_word: str,
        description: str,
        image_urls: List[str],
        training_steps: int,
        auto_submit: bool
    ) -> Dict[str, Any]:
        """Create a new character model."""
        logger.info(f"Creating character: {name}")

        if not name or not trigger_word:
            return {
                'success': False,
                'error': 'Name and trigger_word are required'
            }

        if len(image_urls) < 5:
            return {
                'success': False,
                'error': 'At least 5 training images are required'
            }

        try:
            from content.models import CharacterModel

            # Create the character model
            character = CharacterModel.objects.create(
                user=self.user,
                name=name,
                trigger_word=trigger_word.upper(),
                description=description,
                training_status='preparing',
                training_steps=training_steps,
            )

            logger.info(f"Created character: {character.id}")

            return {
                'success': True,
                'character_id': str(character.id),
                'name': character.name,
                'trigger_word': character.trigger_word,
                'status': character.training_status,
                'message': f"Character '{name}' created. Submit for training when ready."
            }

        except Exception as e:
            logger.error(f"Error creating character: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _submit_training(self, character_id: str) -> Dict[str, Any]:
        """Submit character for training."""
        logger.info(f"Submitting character {character_id} for training")

        try:
            from content.models import CharacterModel
            from content.character_training import submit_training_job

            character = CharacterModel.objects.get(id=character_id, user=self.user)
            result = submit_training_job(character)

            if result.get('success'):
                return {
                    'success': True,
                    'character_id': str(character.id),
                    'training_id': result.get('training_id'),
                    'status': result.get('status'),
                    'estimated_time_minutes': result.get('estimated_time', 20),
                    'message': f"Training submitted for '{character.name}'"
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Training submission failed')
                }

        except Exception as e:
            logger.error(f"Error submitting training: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _check_status(self, character_id: str) -> Dict[str, Any]:
        """Check training status."""
        logger.info(f"Checking status for character {character_id}")

        try:
            from content.models import CharacterModel
            from content.character_training import update_training_status

            character = CharacterModel.objects.get(id=character_id, user=self.user)
            result = update_training_status(character)

            status_messages = {
                'preparing': 'Preparing training data...',
                'pending': 'Queued for training...',
                'processing': 'Training in progress...',
                'completed': 'Training completed! Model ready to use.',
                'failed': 'Training failed.',
                'cancelled': 'Training cancelled.'
            }

            return {
                'success': True,
                'character_id': str(character.id),
                'name': character.name,
                'status': character.training_status,
                'trigger_word': character.trigger_word,
                'message': status_messages.get(character.training_status, 'Unknown status'),
                'ready_to_use': character.training_status == 'completed'
            }

        except Exception as e:
            logger.error(f"Error checking status: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _validate_task(self, task: str) -> bool:
        """Validate the task is appropriate for character training."""
        return bool(task and task.strip())
