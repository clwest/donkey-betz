"""
Creation Agent - Session 134

Specialized agent for standard image generation using Stability AI.
Wraps the existing gallery_generate view for consistent agent-based architecture.

Architecture:
    AI Assistant (detects intent) → Creation Agent → gallery_generate view → Stability AI API

Session 306: Added learning infrastructure hooks for cross-agent knowledge sharing.
"""

import logging
import json
from typing import Dict, Any, Optional, List
from django.contrib.auth import get_user_model
from django.test import RequestFactory

User = get_user_model()
logger = logging.getLogger(__name__)


class CreationLearningMixin:
    """
    Learning infrastructure mixin for CreationAgent.
    Session 306: Enables cross-agent knowledge sharing.
    """

    _learning_loop = None
    _memory_service = None
    _agent_model = None

    @property
    def learning_loop(self):
        """Lazy-load LearningLoopService."""
        if self._learning_loop is None:
            try:
                from core.super_platform.learning_loop import get_learning_loop_service
                self._learning_loop = get_learning_loop_service(self.user)
            except ImportError:
                logger.debug("LearningLoopService not available")
                return None
        return self._learning_loop

    @property
    def memory_service(self):
        """Lazy-load MemoryEmbeddingService."""
        if self._memory_service is None:
            try:
                from core.services.memory_embedding_service import get_memory_embedding_service
                self._memory_service = get_memory_embedding_service()
            except ImportError:
                logger.debug("MemoryEmbeddingService not available")
                return None
        return self._memory_service

    @property
    def agent_model(self):
        """Lazy-load or create Agent model instance."""
        if self._agent_model is None:
            try:
                from core.models_unified_system import Agent
                self._agent_model, _ = Agent.objects.get_or_create(
                    name=self.agent_name,
                    defaults={
                        'agent_type': 'standalone',
                        'specialization': 'image_generation',
                        'description': 'Specialized agent for standard image generation via Stability AI.',
                        'is_active': True,
                    }
                )
            except ImportError:
                logger.debug("Agent model not available")
                return None
        return self._agent_model

    def _record_learning_outcome(
        self,
        result: Dict[str, Any],
        task: str,
        context: Dict[str, Any] = None,
        spider_data_used: bool = False
    ):
        """Record execution outcome for XP and pattern learning."""
        if not self.learning_loop:
            return None

        try:
            outcome_id = self.learning_loop.record_outcome(
                query_type='create',
                query_text=task,
                execution_mode='agent',
                agents_used=[self.agent_name],
                response=result.get('message', ''),
                execution_time_ms=result.get('execution_time_ms', 0),
                success=result.get('success', False),
                spider_data_used=spider_data_used,
                scifi_context_used=False,
                context=context or {}
            )
            return outcome_id
        except Exception as e:
            logger.debug(f"Failed to record learning outcome: {e}")
            return None

    def _create_execution_memory(
        self,
        result: Dict[str, Any],
        task: str,
        memory_type: str = "interaction",
        importance: float = 0.5
    ):
        """Create a memory from the interaction."""
        if not self.memory_service or not self.agent_model:
            return None

        try:
            memory = self.memory_service.create_memory(
                agent=self.agent_model,
                title=f"{self.agent_name}: {task[:50]}...",
                content=result.get('message', ''),
                memory_type=memory_type,
                valence="positive" if result.get('success') else "negative",
                importance_score=importance,
                source_type='agent_execution',
                tags=['image_generation', 'creation', 'success' if result.get('success') else 'failure']
            )
            return memory
        except Exception as e:
            logger.debug(f"Failed to create execution memory: {e}")
            return None

    def _share_knowledge(
        self,
        knowledge_type: str,
        title: str,
        knowledge_value: Dict[str, Any],
        confidence: float = 0.8
    ):
        """Share learned knowledge for cross-agent learning."""
        if not self.agent_model:
            return None

        try:
            from core.models_unified_system import AgentKnowledgeSource

            type_mapping = {
                'technique': 'tool_discovery',
                'style': 'content_idea',
                'prompt': 'content_idea',
            }
            mapped_type = type_mapping.get(knowledge_type, 'content_idea')

            knowledge, created = AgentKnowledgeSource.objects.update_or_create(
                agent=self.agent_model,
                title=title,
                knowledge_type=mapped_type,
                defaults={
                    'summary': json.dumps(knowledge_value),
                    'confidence_score': confidence,
                    'is_active': True,
                }
            )
            return knowledge
        except Exception as e:
            logger.debug(f"Failed to share knowledge: {e}")
            return None

    def _get_shared_knowledge(
        self,
        knowledge_type: str = None,
        title_contains: str = None,
        from_agents: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve knowledge from other agents."""
        try:
            from core.models_unified_system import AgentKnowledgeSource

            queryset = AgentKnowledgeSource.objects.filter(is_active=True)

            if knowledge_type:
                type_mapping = {
                    'technique': 'tool_discovery',
                    'style': 'content_idea',
                    'prompt': 'content_idea',
                }
                mapped_type = type_mapping.get(knowledge_type, knowledge_type)
                queryset = queryset.filter(knowledge_type=mapped_type)

            if title_contains:
                queryset = queryset.filter(title__icontains=title_contains)

            if from_agents:
                queryset = queryset.filter(agent__name__in=from_agents)

            if self.agent_model:
                queryset = queryset.exclude(agent=self.agent_model)

            return [
                {
                    'source_agent': ks.agent.name,
                    'title': ks.title,
                    'type': ks.knowledge_type,
                    'value': json.loads(ks.summary) if ks.summary else {},
                    'confidence': ks.confidence_score,
                }
                for ks in queryset.order_by('-confidence_score')[:10]
            ]
        except Exception as e:
            logger.debug(f"Failed to get shared knowledge: {e}")
            return []


class CreationAgent(CreationLearningMixin):
    """
    Specialized agent for standard image generation via Stability AI.

    Responsibilities:
        - Generate images using Stability AI models
        - Handle quality presets (fast, balanced, high, premium)
        - Support style presets (69 available!)
        - Associate generated images with projects
        - Track agent contributions

    Session 306: Now includes learning infrastructure for cross-agent knowledge sharing.
    """

    def __init__(self, user: User, project_id: Optional[str] = None):
        """
        Initialize Creation Agent.

        Args:
            user: User requesting image generation
            project_id: Optional project ID to associate result with
        """
        self.user = user
        self.project_id = project_id
        self.agent_name = "Creation Agent"
        # Initialize learning mixin attributes
        self._learning_loop = None
        self._memory_service = None
        self._agent_model = None

    def execute(
        self,
        prompt: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute standard image generation.

        Args:
            prompt: Text description of the image to generate
            **kwargs: Additional generation parameters
                - size: Image size (default: '1024x1024')
                - style: Visual style preset
                - negative_prompt: What to avoid
                - num_images: Number of images (default: 1)
                - quality: 'fast', 'balanced', 'high', 'premium'

        Returns:
            Dict with success status and generation results
        """
        logger.info(f"🚀🚀🚀 CREATION AGENT EXECUTE CALLED")
        logger.info(f"🤖 {self.agent_name} starting image generation")
        logger.info(f"   User: {self.user.username}")
        logger.info(f"   Prompt: {prompt[:80]}...")
        logger.info(f"   Project ID: {self.project_id or 'None'}")
        logger.info(f"   Kwargs: {kwargs}")

        try:
            # Extract parameters
            size = kwargs.get('size', '1024x1024')
            style = kwargs.get('style', 'photorealistic')
            negative_prompt = kwargs.get('negative_prompt', None)
            num_images = kwargs.get('num_images', 1)
            quality = kwargs.get('quality', 'balanced')
            session_id = kwargs.get('session_id')

            # Parse size into width/height
            if 'x' in size:
                width, height = map(int, size.split('x'))
            else:
                width = height = int(size)

            logger.info(f"🚀 Generating {num_images} image(s) with quality: {quality}")

            # Call gallery_generate view using RequestFactory
            factory = RequestFactory()
            request_data = {
                'prompt': prompt,
                'width': width,
                'height': height,
                'num_images': num_images,
                'quality': quality,
                'style': style,
                'agent_name': self.agent_name  # Session 137: Pass agent name for attribution
            }

            if negative_prompt:
                request_data['negative_prompt'] = negative_prompt
            if self.project_id:
                request_data['project_id'] = self.project_id
            if session_id:
                request_data['session_id'] = session_id

            request = factory.post('/api/gallery/generate/',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
            request.user = self.user
            request._dont_enforce_csrf_checks = True

            # Call the view
            from core.views_image import gallery_generate
            response = gallery_generate(request)

            # Session 137: Add detailed error logging
            logger.info(f"📦 gallery_generate response status: {response.status_code}")
            logger.info(f"📦 gallery_generate response type: {type(response)}")

            # Parse response
            if hasattr(response, 'data'):
                result = response.data
                logger.info(f"📦 Response data: {result}")
            else:
                logger.error(f"❌ Response has no 'data' attribute! Response: {response}")
                logger.error(f"❌ Response content: {getattr(response, 'content', 'No content')}")
                raise Exception(f"gallery_generate returned invalid response: {response}")

            if result.get('success'):
                image_ids = [img['id'] for img in result.get('images', [])]
                logger.info(f"✅ {self.agent_name} completed successfully!")
                logger.info(f"   Generated: {len(image_ids)} image(s)")

                success_result = {
                    'success': True,
                    'message': f"✨ Generated {len(image_ids)} image(s). Check your project gallery!",
                    'image_ids': image_ids
                }

                # Session 306: Learning Infrastructure Hooks
                task = f"Generate image: {prompt[:80]}..."

                # Record learning outcome
                self._record_learning_outcome(
                    result=success_result,
                    task=task,
                    context={
                        'style': style,
                        'size': size,
                        'quality': quality,
                        'num_images': num_images,
                    }
                )

                # Create memory of successful generation
                self._create_execution_memory(
                    result=success_result,
                    task=task,
                    memory_type="success",
                    importance=0.6
                )

                # Share successful style/prompt combinations
                self._share_knowledge(
                    knowledge_type='style',
                    title=f"Style works: {style} for {prompt[:50]}",
                    knowledge_value={
                        'prompt_snippet': prompt[:100],
                        'style': style,
                        'size': size,
                        'quality': quality,
                        'images_generated': len(image_ids),
                    },
                    confidence=0.75
                )

                return success_result
            else:
                error_msg = result.get('error', 'Image generation failed')
                logger.error(f"❌ {self.agent_name} generation failed: {error_msg}")

                error_result = {
                    'success': False,
                    'error': error_msg
                }

                # Session 306: Record failed outcome for learning
                self._record_learning_outcome(
                    result=error_result,
                    task=f"Generate image: {prompt[:80]}...",
                    context={'error': error_msg, 'style': style}
                )

                return error_result

        except Exception as e:
            logger.error(f"❌ {self.agent_name} failed: {str(e)}", exc_info=True)

            error_result = {
                'success': False,
                'error': str(e)
            }

            # Session 306: Record exception for learning
            self._record_learning_outcome(
                result=error_result,
                task=f"Generate image: {prompt[:80]}...",
                context={'exception': str(e)}
            )

            return error_result
