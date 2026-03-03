#!/usr/bin/env python
"""
Live Learning Orchestrator
==========================
Orchestrates live learning demonstrations showing agents improving in real-time

Session 306: Added learning infrastructure hooks for cross-agent knowledge sharing.
Session 727: Migrated from agents/live_learning_orchestrator.py to core/services/live_learning_orchestrator.py
"""

import asyncio
import json
import logging
import os
import random
import redis
from datetime import datetime
from typing import Dict, List, Any
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Import our existing modules
from agents.real_code_generator import RealCodeGenerator
from intelligence.learning_verification import LearningVerificationSystem
from intelligence.multi_domain_learning import MultiDomainLearning
from intelligence.shared_memory import SharedMemorySystem

logger = logging.getLogger(__name__)


class LiveLearningLearningMixin:
    """
    Learning infrastructure mixin for LiveLearningOrchestrator.
    Session 306: Enables cross-agent knowledge sharing for learning orchestration.
    """

    _learning_loop_service = None
    _memory_service = None
    _agent_model = None

    @property
    def learning_loop_service(self):
        """Lazy-load LearningLoopService."""
        if self._learning_loop_service is None:
            try:
                from core.super_platform.learning_loop import get_learning_loop_service
                self._learning_loop_service = get_learning_loop_service(None)
            except ImportError:
                logger.debug("LearningLoopService not available")
                return None
        return self._learning_loop_service

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
                    name='LiveLearningOrchestrator',
                    defaults={
                        'agent_type': 'legacy',
                        'specialization': 'learning_orchestration',
                        'description': 'Orchestrates live learning demonstrations showing agents improving in real-time.',
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
        if not self.learning_loop_service:
            return None

        try:
            outcome_id = self.learning_loop_service.record_outcome(
                query_type='orchestration',
                query_text=task,
                execution_mode='agent',
                agents_used=['LiveLearningOrchestrator'],
                response=str(result)[:500],  # Truncate for storage
                execution_time_ms=result.get('execution_time_ms', 0),
                success=result.get('success', True),
                spider_data_used=spider_data_used,
                scifi_context_used=True,  # Learning orchestrator uses sci-fi features
                context=context or {}
            )
            return outcome_id
        except Exception as e:
            logger.warning(f"Failed to record learning outcome: {e}")
            return None

    def _create_execution_memory(
        self,
        result: Dict[str, Any],
        task: str,
        memory_type: str = "interaction",
        importance: float = 0.5
    ):
        """Create a memory from the orchestration execution."""
        if not self.memory_service or not self.agent_model:
            return None

        try:
            memory = self.memory_service.create_memory(
                agent=self.agent_model,
                title=f"Orchestration: {task[:50]}...",
                content=str(result)[:500],  # Truncate for storage
                memory_type=memory_type,
                valence="positive" if result.get('success', True) else "negative",
                importance_score=importance,
                source_type='agent_execution',
                tags=['learning_orchestration', 'live_demo', 'success' if result.get('success', True) else 'failure']
            )
            return memory
        except Exception as e:
            logger.warning(f"Failed to create execution memory: {e}")
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
                'learning_pattern': 'tool_discovery',
                'collaboration': 'content_idea',
                'improvement': 'market',
            }
            mapped_type = type_mapping.get(knowledge_type, 'tool_discovery')

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
            logger.warning(f"Failed to share knowledge: {e}")
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
                queryset = queryset.filter(knowledge_type=knowledge_type)

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
            logger.warning(f"Failed to get shared knowledge: {e}")
            return []


class LiveLearningOrchestrator(LiveLearningLearningMixin):
    """
    Orchestrates live learning demonstration.
    Shows agents getting progressively better at tasks.

    Session 306: Added learning infrastructure for cross-agent knowledge sharing.
    """

    def __init__(self):
        self.redis = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'), decode_responses=True)
        self.learning_system = LearningVerificationSystem()
        self.domain_learning = MultiDomainLearning()
        self.shared_memory = SharedMemorySystem()
        self.channel_layer = get_channel_layer()
        self.agents = {}
        self.iteration = 0
        self.improvements_made = []
        # Initialize learning mixin attributes
        self._learning_loop_service = None
        self._memory_service = None
        self._agent_model = None

    async def start_learning_loop(self, project_type='ecommerce', agents=None):
        """
        Main learning loop that shows continuous improvement
        """
        logger.info(f"Starting live learning loop for {project_type}")

        if not agents:
            agents = ['Business Agent', 'ML Recommendation Engine', 'Database Architect']

        # Initialize agents
        for agent_name in agents:
            self.agents[agent_name] = {
                'iterations': 0,
                'quality_score': 70,  # Start at 70%
                'complexity_score': 50,
                'lines_generated': 0,
                'improvements': []
            }

        while True:
            self.iteration += 1
            logger.info(f"Learning Iteration {self.iteration}")

            # 1. Generate improved code
            for agent_name in agents:
                code_result = await self.generate_improved_code(agent_name, project_type)

                if code_result:
                    # 2. Analyze and learn from the code
                    insights = await self.analyze_code(agent_name, code_result)

                    # 3. Share knowledge between agents
                    if insights:
                        await self.share_knowledge(agent_name, insights)

            # 4. Agent collaboration event
            if self.iteration % 3 == 0:  # Every 3rd iteration
                await self.trigger_collaboration(agents)

            # 5. Broadcast overall progress
            await self.broadcast_progress()

            # 6. Wait before next iteration
            await asyncio.sleep(30)  # Every 30 seconds

            # Stop after 10 iterations for demo
            if self.iteration >= 10:
                logger.info("Learning demonstration complete")
                break

    async def generate_improved_code(self, agent_name: str, project_type: str) -> Dict:
        """
        Generate progressively better code with each iteration
        """
        agent_data = self.agents[agent_name]
        agent_data['iterations'] += 1

        # Define improvements for each iteration
        improvement_stages = {
            1: {
                'focus': 'basic_implementation',
                'description': 'Basic structure and functionality',
                'quality_boost': 5,
                'complexity_boost': 10
            },
            2: {
                'focus': 'add_error_handling',
                'description': 'Added comprehensive error handling',
                'quality_boost': 10,
                'complexity_boost': 5
            },
            3: {
                'focus': 'optimize_performance',
                'description': 'Performance optimizations applied',
                'quality_boost': 8,
                'complexity_boost': 12
            },
            4: {
                'focus': 'add_caching',
                'description': 'Implemented intelligent caching',
                'quality_boost': 7,
                'complexity_boost': 8
            },
            5: {
                'focus': 'implement_scaling',
                'description': 'Added scalability features',
                'quality_boost': 6,
                'complexity_boost': 15
            }
        }

        # Get current stage
        stage_num = (agent_data['iterations'] - 1) % 5 + 1
        stage = improvement_stages[stage_num]

        logger.info(f"{agent_name}: Applying {stage['focus']}")

        try:
            # Generate code using real code generator
            generator = RealCodeGenerator()
            code_result = generator.generate_code_by_agent(
                agent_name,
                project_type,
                ml_features=['personalization', 'recommendations'] if 'ML' in agent_name else []
            )

            # Simulate improvement
            agent_data['quality_score'] = min(100, agent_data['quality_score'] + stage['quality_boost'])
            agent_data['complexity_score'] = min(100, agent_data['complexity_score'] + stage['complexity_boost'])
            agent_data['lines_generated'] += len(code_result['code'].splitlines())
            agent_data['improvements'].append(stage['description'])

            # Store improvement in Redis
            self.redis.hset(f'agent:{agent_name}:improvement:{self.iteration}', mapping={
                'stage': stage['focus'],
                'quality': agent_data['quality_score'],
                'complexity': agent_data['complexity_score'],
                'lines': len(code_result['code'].splitlines()),
                'timestamp': datetime.now().isoformat()
            })

            # Track in shared memory
            self.shared_memory.store_memory(
                'agent',
                agent_name,
                'code_improvement',
                {
                    'iteration': self.iteration,
                    'improvement': stage['description'],
                    'metrics': {
                        'quality': agent_data['quality_score'],
                        'complexity': agent_data['complexity_score']
                    }
                }
            )

            # Broadcast code evolution
            await self.broadcast_code_evolution(
                agent_name,
                self.iteration,
                stage['description'],
                agent_data
            )

            return {
                'code': code_result['code'],
                'filename': code_result['filename'],
                'improvement': stage['description'],
                'metrics': {
                    'quality': agent_data['quality_score'],
                    'complexity': agent_data['complexity_score'],
                    'lines': len(code_result['code'].splitlines())
                }
            }

        except Exception as e:
            logger.error(f"Error generating code for {agent_name}: {e}")
            return None

    async def analyze_code(self, agent_name: str, code_result: Dict) -> Dict:
        """
        Analyze generated code and extract learning insights
        """
        insights = {
            'patterns_discovered': [],
            'optimizations_found': [],
            'errors_avoided': []
        }

        # Simulate analysis and learning
        code_lines = code_result['code'].splitlines()

        # Pattern discovery
        if 'class' in code_result['code']:
            insights['patterns_discovered'].append('Object-oriented design improves maintainability')
        if 'async def' in code_result['code']:
            insights['patterns_discovered'].append('Async operations improve performance')
        if 'cache' in code_result['code'].lower():
            insights['patterns_discovered'].append('Caching reduces API calls by 60%')

        # Optimization discovery
        if len(code_lines) > 100:
            insights['optimizations_found'].append('Modular design with functions under 50 lines')
        if 'try:' in code_result['code']:
            insights['optimizations_found'].append('Error handling prevents crashes')

        # Security improvements
        if 'validate' in code_result['code'].lower():
            insights['errors_avoided'].append('Input validation prevents injection attacks')
        if 'sanitize' in code_result['code'].lower():
            insights['errors_avoided'].append('Data sanitization improves security')

        # Store insights in domain learning system
        if insights['patterns_discovered']:
            self.domain_learning.learn_platform_optimization(
                agent_name,
                'code_generation',
                {
                    'type': 'pattern_discovery',
                    'tactic': insights['patterns_discovered'][0],
                    'implementation': f"Applied in iteration {self.iteration}",
                    'expected_outcome': 'Improved code quality',
                    'confidence': 0.8
                }
            )

        return insights

    async def share_knowledge(self, agent_name: str, insights: Dict):
        """
        Share knowledge between agents for collaborative learning
        """
        # Combine all insights
        all_insights = []
        for category, items in insights.items():
            all_insights.extend(items)

        if not all_insights:
            return

        # Select a random insight to share
        shared_insight = random.choice(all_insights)

        # Store in shared memory for other agents
        self.shared_memory.share_experience(
            'agent',
            agent_name,
            {
                'insight': shared_insight,
                'iteration': self.iteration,
                'category': 'code_improvement'
            }
        )

        # Broadcast knowledge sharing event
        await self.broadcast_agent_collaboration(
            [agent_name],
            {'insight': shared_insight, 'impact': 'High'}
        )

        logger.info(f"{agent_name} shared: {shared_insight}")

    async def trigger_collaboration(self, agents: List[str]):
        """
        Trigger collaboration between agents
        """
        if len(agents) < 2:
            return

        # Select two random agents to collaborate
        agent1, agent2 = random.sample(agents, 2)

        # Simulate knowledge exchange
        knowledge_exchanged = {
            'pattern_discovered': f'{agent1} teaches {agent2} about efficient caching strategies',
            'optimization_shared': 'Batch processing reduces API calls by 40%',
            'best_practice': 'Use connection pooling for database operations'
        }

        # Add knowledge edge in shared memory
        self.shared_memory.add_knowledge_edge(
            f'agent/{agent1}',
            f'agent/{agent2}',
            'teaches',
            strength=0.8
        )

        # Broadcast collaboration
        await self.broadcast_agent_collaboration(
            [agent1, agent2],
            knowledge_exchanged
        )

        logger.info(f"Collaboration: {agent1} <-> {agent2}")

        # Session 306: Learning Infrastructure - Share collaboration knowledge
        self._share_knowledge(
            knowledge_type='collaboration',
            title=f"Collaboration: {agent1} <-> {agent2}",
            knowledge_value={
                'agents': [agent1, agent2],
                'knowledge_exchanged': knowledge_exchanged,
                'iteration': self.iteration,
            },
            confidence=0.85
        )

    async def broadcast_progress(self):
        """
        Broadcast overall learning progress
        """
        # Calculate aggregate metrics
        total_quality = sum(a['quality_score'] for a in self.agents.values()) / len(self.agents)
        total_complexity = sum(a['complexity_score'] for a in self.agents.values()) / len(self.agents)
        total_lines = sum(a['lines_generated'] for a in self.agents.values())
        total_improvements = sum(len(a['improvements']) for a in self.agents.values())

        progress_data = {
            'iteration': self.iteration,
            'average_quality': round(total_quality, 2),
            'average_complexity': round(total_complexity, 2),
            'total_lines': total_lines,
            'total_improvements': total_improvements,
            'agents_active': len(self.agents),
            'timestamp': datetime.now().isoformat()
        }

        # Store in Redis
        self.redis.hset('learning:progress:latest', mapping={
            k: str(v) for k, v in progress_data.items()
        })

        # Broadcast via WebSocket
        async_to_sync(self.channel_layer.group_send)(
            'ai_training',
            {
                'type': 'broadcast_learning_update',
                'data': {
                    'agent': 'System',
                    'event': 'progress_update',
                    'metrics': progress_data
                }
            }
        )

        logger.info(f"Progress: Quality={total_quality:.1f}% Complexity={total_complexity:.1f}%")

        # Session 306: Learning Infrastructure Hooks
        self._record_learning_outcome(
            result={
                'success': True,
                'average_quality': round(total_quality, 2),
                'total_improvements': total_improvements,
            },
            task=f"Learning iteration {self.iteration}",
            context={
                'iteration': self.iteration,
                'agents_active': len(self.agents),
                'total_lines': total_lines,
            }
        )

        # Create memory for significant progress milestones
        if self.iteration % 5 == 0 or total_quality >= 90:
            self._create_execution_memory(
                result=progress_data,
                task=f"Milestone: iteration {self.iteration}",
                memory_type="success",
                importance=0.75 if total_quality >= 90 else 0.6
            )

        # Share learning patterns when quality is high
        if total_quality >= 85:
            self._share_knowledge(
                knowledge_type='learning_pattern',
                title=f"High-quality learning: {total_quality:.1f}%",
                knowledge_value={
                    'average_quality': round(total_quality, 2),
                    'average_complexity': round(total_complexity, 2),
                    'total_lines': total_lines,
                    'agents_active': len(self.agents),
                    'iteration': self.iteration,
                },
                confidence=total_quality / 100
            )

    async def broadcast_code_evolution(self, agent_name: str, version: int, improvement: str, metrics: Dict):
        """
        Broadcast code evolution event
        """
        async_to_sync(self.channel_layer.group_send)(
            'ai_training',
            {
                'type': 'broadcast_code_evolution',
                'agent': agent_name,
                'version': version,
                'improvements': improvement,
                'metrics': {
                    'quality': metrics['quality_score'],
                    'complexity': metrics['complexity_score'],
                    'lines': metrics['lines_generated']
                }
            }
        )

    async def broadcast_agent_collaboration(self, agents: List[str], knowledge: Dict):
        """
        Broadcast agent collaboration event
        """
        async_to_sync(self.channel_layer.group_send)(
            'ai_training',
            {
                'type': 'broadcast_agent_collaboration',
                'agents': agents,
                'knowledge': knowledge,
                'timestamp': datetime.now().isoformat()
            }
        )


def run_live_learning_demo():
    """
    Run the live learning demonstration
    """
    orchestrator = LiveLearningOrchestrator()

    # Run the async loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(
            orchestrator.start_learning_loop(
                project_type='ecommerce',
                agents=['Business Agent', 'ML Recommendation Engine', 'Database Architect']
            )
        )
    except KeyboardInterrupt:
        print("\n⚠️ Learning loop interrupted")
    finally:
        loop.close()


if __name__ == '__main__':
    run_live_learning_demo()