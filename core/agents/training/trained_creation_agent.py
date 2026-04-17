"""
Trained Creation Agent - Clean Architecture
============================================

Session 280: Phase 3 - Agent Architecture Unification

This agent generates images using trained FLUX LoRA models.

Tools Available:
    - generate_with_model: Generate images using a trained character/style model

Usage:
    from core.agents.training import TrainedCreationAgent

    agent = TrainedCreationAgent(user=request.user)
    result = agent.execute(
        task="Generate an image of MYCHAR in a cyberpunk city",
        context={'character_model': 'mychar'},
        scifi_context={},
        spider_context={}
    )
"""

import logging
import time
import requests
from typing import Dict, Any, Optional

from django.conf import settings

from core.agents.base_agent import BaseAgent, AgentResult
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


def analyze_creation_prompt_with_ml(prompt_data: dict) -> dict:
    """Analyze creation prompts using ML models (Text)."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()
        result = router.auto_route(
            data=prompt_data,
            task_hint=TaskType.TEXT,
            max_models=2
        )
        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'text'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'prompt_analysis': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML creation prompt analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


class TrainedCreationAgent(BaseAgent):
    """
    Trained Creation Agent - LoRA Image Generation.

    This agent:
    1. Resolves trained character/style models
    2. Generates images using FLUX with LoRA weights
    3. Saves generated images to the database

    It CANNOT:
    - Train models (use CharacterTrainingAgent)
    - Edit images
    """

    name = "TrainedCreationAgent"

    system_prompt = """You are TrainedCreationAgent, the LoRA Generation Specialist.

Your job is to generate images using trained character/style models:
- Resolve character models by name, trigger word, or ID
- Generate images using FLUX with custom LoRA weights
- Support various generation parameters

Generation Parameters:
- lora_scale: Strength of LoRA effect (0.0-1.0, default 0.8)
- width/height: Image dimensions (default 1024x1024)
- num_outputs: Number of images (1-4)
- guidance_scale: Prompt adherence (1-20, default 3.5)

When given a task:
1. Identify the character model to use
2. Extract the prompt and parameters
3. Generate the image(s)
4. Return the results

You generate with trained models - you do NOT train models (use CharacterTrainingAgent)."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "generate_with_model",
                "description": "Generate images using a trained character/style model",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "Text prompt for image generation"
                        },
                        "character_model": {
                            "type": "string",
                            "description": "Name, trigger word, or ID of the trained model"
                        },
                        "lora_scale": {
                            "type": "number",
                            "description": "Strength of LoRA effect (0.0-1.0)",
                            "default": 0.8
                        },
                        "width": {
                            "type": "integer",
                            "description": "Image width",
                            "default": 1024
                        },
                        "height": {
                            "type": "integer",
                            "description": "Image height",
                            "default": 1024
                        },
                        "num_outputs": {
                            "type": "integer",
                            "description": "Number of images to generate (1-4)",
                            "default": 1
                        },
                        "guidance_scale": {
                            "type": "number",
                            "description": "Prompt adherence (1-20)",
                            "default": 3.5
                        }
                    },
                    "required": ["prompt", "character_model"]
                }
            }
        }
    ]

    def __init__(self, user=None):
        """Initialize TrainedCreationAgent."""
        super().__init__(user=user)
        self.api_token = settings.EXTERNAL_API_KEYS.get('REPLICATE_API_KEY')

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """Execute trained image generation based on the task."""
        start_time = time.time()
        tool_calls_made = []

        # Session 736: Extract spider intelligence for real-time data
        spider_intel = self._extract_spider_intelligence(spider_context)
        if spider_intel['has_data']:
            logger.info(f"🕷️ {self.name} using spider intelligence")

        with self.time_travel_session("trained_creation", task, input_data=context):
            try:
                if not self._validate_task(task):
                    return AgentResult(
                        success=False,
                        error="Invalid or empty task",
                        agent_name=self.name
                    )

                self.record_decision(
                    decision_type="task_analysis",
                    action="Analyzing LoRA generation request",
                    reasoning=f"Received task: {task[:100]}",
                    alternatives=["generate_with_model"],
                    confidence=0.9
                )

                full_prompt = self._build_intelligent_prompt(task, scifi_context, spider_context)
                logger.info(f"TrainedCreationAgent executing: {task[:50]}...")

                gpt_response = self._call_openai(full_prompt)

                if gpt_response.get('tool_calls'):
                    for tool_call in gpt_response['tool_calls']:
                        tool_name = tool_call['name']
                        arguments = tool_call['arguments']

                        self.record_decision(
                            decision_type="tool_selection",
                            action=f"Calling {tool_name}",
                            reasoning=f"Generation parameters: {arguments}",
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
                        message="LoRA image generation completed",
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
                        title=f"Trained Creation: {task[:80]}",
                        content=self._render_agent_output_markdown(
                            task=task,
                            summary=result.message,
                            tool_calls=tool_calls_made,
                        ),
                        deliverable_type='image',
                        category='Trained Creation',
                        tags=['training', 'lora', 'image'],
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
                logger.error(f"TrainedCreationAgent error: {e}")
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
        """Execute a LoRA generation tool call."""
        if tool_name == "generate_with_model":
            return self._generate_with_model(
                prompt=arguments.get('prompt', ''),
                character_model=arguments.get('character_model', ''),
                lora_scale=arguments.get('lora_scale', 0.8),
                width=arguments.get('width', 1024),
                height=arguments.get('height', 1024),
                num_outputs=arguments.get('num_outputs', 1),
                guidance_scale=arguments.get('guidance_scale', 3.5)
            )

        return super()._execute_tool_call(tool_name, arguments)

    def _generate_with_model(
        self,
        prompt: str,
        character_model: str,
        lora_scale: float,
        width: int,
        height: int,
        num_outputs: int,
        guidance_scale: float
    ) -> Dict[str, Any]:
        """Generate images using a trained model."""
        logger.info(f"Generating with model: {character_model}")

        if not prompt:
            return {'success': False, 'error': 'Prompt is required'}

        if not character_model:
            return {'success': False, 'error': 'Character model is required'}

        try:
            # Resolve the character model
            model = self._resolve_character_model(character_model)
            if not model:
                return {
                    'success': False,
                    'error': f'Character model "{character_model}" not found or not completed training'
                }

            logger.info(f"Resolved model: {model.name} (version: {model.replicate_version_id})")

            # Create prediction
            prediction = self._create_prediction(
                prompt=prompt,
                version_id=model.replicate_version_id,
                width=width,
                height=height,
                num_outputs=num_outputs,
                guidance_scale=guidance_scale
            )

            if not prediction:
                return {'success': False, 'error': 'Failed to create prediction'}

            prediction_id = prediction.get('id')
            logger.info(f"Prediction created: {prediction_id}")

            # Poll for results
            result = self._poll_prediction(prediction_id)

            if not result or result.get('status') == 'failed':
                error_msg = result.get('error', 'Unknown error') if result else 'Polling failed'
                return {'success': False, 'error': f"Generation failed: {error_msg}"}

            image_urls = result.get('output', [])
            if not image_urls:
                return {'success': False, 'error': 'No images in output'}

            # Save images
            image_ids = self._save_images(image_urls, prompt, model)

            return {
                'success': True,
                'image_ids': image_ids,
                'image_count': len(image_ids),
                'model_used': model.name,
                'trigger_word': model.trigger_word,
                'message': f"Generated {len(image_ids)} image(s) using {model.name}"
            }

        except Exception as e:
            logger.error(f"Error generating with model: {e}")
            return {'success': False, 'error': str(e)}

    def _resolve_character_model(self, identifier: str):
        """Resolve character model by name, trigger word, or ID."""
        from content.models import CharacterModel

        try:
            # Try UUID
            model = CharacterModel.objects.get(id=identifier, user=self.user)
            if model.training_status == 'completed':
                return model
        except (ValueError, CharacterModel.DoesNotExist):
            pass

        # Try by name
        model = CharacterModel.objects.filter(
            name=identifier,
            user=self.user,
            training_status='completed'
        ).order_by('-created_at').first()
        if model:
            return model

        # Try by trigger word (normalized)
        normalized = identifier.upper().replace('-', '').replace('_', '').replace(' ', '')
        models = CharacterModel.objects.filter(
            user=self.user,
            training_status='completed'
        ).order_by('-created_at')

        for model in models:
            if model.trigger_word:
                norm_trigger = model.trigger_word.upper().replace('-', '').replace('_', '').replace(' ', '')
                if normalized == norm_trigger:
                    return model

        return None

    def _create_prediction(
        self,
        prompt: str,
        version_id: str,
        width: int,
        height: int,
        num_outputs: int,
        guidance_scale: float
    ) -> Optional[Dict[str, Any]]:
        """Create a Replicate prediction."""
        if not self.api_token:
            logger.error("REPLICATE_API_KEY not configured")
            return None

        headers = {
            "Authorization": f"Token {self.api_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "version": version_id,
            "input": {
                "prompt": prompt,
                "width": width,
                "height": height,
                "num_outputs": num_outputs,
                "num_inference_steps": 28,
                "guidance_scale": guidance_scale,
                "output_format": "png",
                "output_quality": 100
            }
        }

        try:
            response = requests.post(
                "https://api.replicate.com/v1/predictions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Replicate API error: {e}")
            return None

    def _poll_prediction(
        self,
        prediction_id: str,
        max_wait: int = 120,
        interval: int = 2
    ) -> Optional[Dict[str, Any]]:
        """Poll for prediction completion."""
        if not self.api_token:
            return None

        headers = {
            "Authorization": f"Token {self.api_token}",
            "Content-Type": "application/json"
        }

        url = f"https://api.replicate.com/v1/predictions/{prediction_id}"
        start = time.time()

        while (time.time() - start) < max_wait:
            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                prediction = response.json()

                status = prediction.get('status')
                if status == 'succeeded':
                    return prediction
                elif status in ['failed', 'canceled', 'cancelled']:
                    return prediction

                time.sleep(interval)

            except requests.exceptions.RequestException as e:
                logger.error(f"Polling error: {e}")
                return None

        return None

    def _save_images(self, urls: list, prompt: str, character_model) -> list:
        """Save generated images to database."""
        import uuid
        import os
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        from core.views_image import save_to_history

        image_ids = []
        for url in urls:
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()

                unique_id = uuid.uuid4()
                filename = f"lora-{unique_id}.png"
                file_path = os.path.join('generated', filename)

                content_file = ContentFile(response.content)
                saved_path = default_storage.save(file_path, content_file)

                history = save_to_history(
                    user=self.user,
                    file_path=saved_path,
                    image_type='generated',
                    prompt=prompt,
                    parameters={
                        'character_model': character_model.name,
                        'lora_version': character_model.replicate_version_id
                    },
                    model_used=character_model.replicate_model_name,
                    style='lora-trained',
                    agent_name='trained-creation-agent'
                )

                image_ids.append(str(history.id))

            except Exception as e:
                logger.error(f"Error saving image: {e}")
                continue

        return image_ids

    def _validate_task(self, task: str) -> bool:
        """Validate the task is appropriate for LoRA generation."""
        return bool(task and task.strip())
