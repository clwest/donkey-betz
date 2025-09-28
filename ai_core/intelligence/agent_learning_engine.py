"""
Agent Learning Engine - Continuous Learning for 152 Agents
=========================================================

This module implements automatic agent learning from real-time spider data.
Each agent continuously learns and improves from intelligence signals.

Features:
- Real-time learning from 1,770+ spider signals
- Adaptive learning rates per agent specialization
- Knowledge base updates and skill improvement
- Performance tracking and optimization
- Multi-modal learning (text, data, patterns)
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Set, Callable
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, asdict, field
from collections import defaultdict
import redis.asyncio as redis
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class AgentLearningProfile:
    """Learning profile for an agent"""
    agent_id: str
    agent_name: str
    specialization: str
    learning_rate: float = 0.1
    curiosity_factor: float = 0.5  # How much to explore vs exploit
    confidence_threshold: float = 0.7
    knowledge_domains: Set[str] = field(default_factory=set)
    last_learning_update: Optional[datetime] = None
    total_signals_processed: int = 0
    learning_improvements: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class LearningUpdate:
    """Represents a learning update for an agent"""
    update_id: str
    agent_id: str
    source_signal_id: str
    learning_type: str  # 'knowledge_update', 'skill_improvement', 'pattern_recognition'
    content: Dict[str, Any]
    confidence: float
    timestamp: datetime
    expires_at: Optional[datetime] = None
    applied: bool = False


@dataclass
class AgentKnowledgeBase:
    """Knowledge base for an agent"""
    agent_id: str
    domain_knowledge: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    learned_patterns: List[Dict[str, Any]] = field(default_factory=list)
    skill_improvements: Dict[str, float] = field(default_factory=dict)  # skill -> improvement_score
    experience_log: List[Dict[str, Any]] = field(default_factory=list)
    last_updated: Optional[datetime] = None


class AgentLearningEngine:
    """
    Continuous learning engine for all 152 agents.
    Processes real-time spider intelligence and updates agent knowledge.
    """

    def __init__(self):
        self.agent_profiles: Dict[str, AgentLearningProfile] = {}
        self.agent_knowledge_bases: Dict[str, AgentKnowledgeBase] = {}
        self.redis_client: Optional[redis.Redis] = None
        self.learning_active = False
        self.learning_queues: Dict[str, asyncio.Queue] = {}

        # Learning statistics
        self.stats = {
            'total_learning_updates': 0,
            'agents_improved': 0,
            'knowledge_items_added': 0,
            'patterns_learned': 0,
            'skills_enhanced': 0
        }

        # Specialization-specific learning configurations
        self.specialization_configs = {
            'financial': {
                'learning_rate': 0.15,
                'curiosity_factor': 0.4,  # More exploitation-focused
                'key_domains': {'market_analysis', 'risk_assessment', 'portfolio_management'},
                'signal_filters': ['market_trend', 'price_alert', 'volume_spike'],
                'learning_focus': 'pattern_recognition'
            },
            'freelance': {
                'learning_rate': 0.12,
                'curiosity_factor': 0.6,  # More exploration for opportunities
                'key_domains': {'job_matching', 'skill_analysis', 'rate_optimization'},
                'signal_filters': ['job_opportunity', 'skill_demand', 'rate_trend'],
                'learning_focus': 'opportunity_detection'
            },
            'content': {
                'learning_rate': 0.18,
                'curiosity_factor': 0.7,  # High creativity exploration
                'key_domains': {'content_strategy', 'audience_building', 'monetization'},
                'signal_filters': ['content_trend', 'monetization_opportunity'],
                'learning_focus': 'trend_analysis'
            },
            'tech': {
                'learning_rate': 0.2,
                'curiosity_factor': 0.8,  # High exploration for innovation
                'key_domains': {'technology_scouting', 'innovation_tracking', 'patent_analysis'},
                'signal_filters': ['tech_breakthrough', 'patent_filed', 'research_published'],
                'learning_focus': 'innovation_tracking'
            },
            'general': {
                'learning_rate': 0.1,
                'curiosity_factor': 0.5,
                'key_domains': {'general_intelligence', 'cross_domain_synthesis'},
                'signal_filters': ['general_insight', 'cross_domain_pattern'],
                'learning_focus': 'knowledge_synthesis'
            }
        }

    async def initialize(self):
        """Initialize the learning engine"""
        try:
            # Setup Redis connection
            self.redis_client = await redis.from_url(
                'redis://localhost:6379/1',  # Use different DB for learning
                encoding='utf-8',
                decode_responses=True
            )
            await self.redis_client.ping()

            # Load agents and create learning profiles
            await self._load_agent_profiles()

            # Setup learning signal subscriptions
            await self._setup_learning_subscriptions()

            # Initialize agent knowledge bases
            await self._initialize_agent_knowledge_bases()

            self.learning_active = True
            logger.info(f"Agent learning engine initialized for {len(self.agent_profiles)} agents")

        except Exception as e:
            logger.error(f"Failed to initialize agent learning engine: {e}")
            raise

    async def _load_agent_profiles(self):
        """Load all agent profiles and create learning configurations"""
        try:
            # Import agent loader
            from ..agents.universal_agent_loader import get_all_agent_classes

            # Get all available agents
            agent_classes = get_all_agent_classes()
            logger.info(f"Loading learning profiles for {len(agent_classes)} agents")

            for agent_name, agent_class in agent_classes.items():
                # Determine specialization
                specialization = getattr(agent_class, 'specialization', 'general')
                if hasattr(agent_class, '__init__') and hasattr(agent_class, 'specialization'):
                    try:
                        temp_instance = agent_class()
                        specialization = getattr(temp_instance, 'specialization', 'general')
                    except:
                        pass

                # Get specialization config
                spec_config = self.specialization_configs.get(specialization, self.specialization_configs['general'])

                # Create learning profile
                profile = AgentLearningProfile(
                    agent_id=agent_name,
                    agent_name=agent_name,
                    specialization=specialization,
                    learning_rate=spec_config['learning_rate'],
                    curiosity_factor=spec_config['curiosity_factor'],
                    knowledge_domains=spec_config['key_domains'].copy()
                )

                self.agent_profiles[agent_name] = profile

                # Create learning queue
                self.learning_queues[agent_name] = asyncio.Queue(maxsize=100)

            logger.info(f"Created learning profiles for {len(self.agent_profiles)} agents")

        except Exception as e:
            logger.error(f"Error loading agent profiles: {e}")

    async def _setup_learning_subscriptions(self):
        """Setup Redis subscriptions for learning signals"""
        try:
            pubsub = self.redis_client.pubsub()

            # Subscribe to general learning signals
            await pubsub.subscribe('learning:signals:general')

            # Subscribe to category-specific signals
            categories = ['financial', 'freelance', 'content', 'tech', 'news', 'market', 'social', 'innovation']
            for category in categories:
                await pubsub.subscribe(f'learning:signals:{category}')

            # Subscribe to agent-specific signals
            for agent_id in self.agent_profiles.keys():
                await pubsub.subscribe(f'learning:signals:agent:{agent_id}')

            # Start signal processing task
            asyncio.create_task(self._process_learning_signals(pubsub))
            logger.info("Learning signal subscriptions established")

        except Exception as e:
            logger.error(f"Error setting up learning subscriptions: {e}")

    async def _initialize_agent_knowledge_bases(self):
        """Initialize knowledge bases for all agents"""
        try:
            for agent_id in self.agent_profiles.keys():
                # Try to load existing knowledge base
                knowledge_base = await self._load_agent_knowledge_base(agent_id)

                if not knowledge_base:
                    # Create new knowledge base
                    knowledge_base = AgentKnowledgeBase(
                        agent_id=agent_id,
                        last_updated=datetime.now(timezone.utc)
                    )

                self.agent_knowledge_bases[agent_id] = knowledge_base

            logger.info(f"Initialized knowledge bases for {len(self.agent_knowledge_bases)} agents")

        except Exception as e:
            logger.error(f"Error initializing agent knowledge bases: {e}")

    async def _load_agent_knowledge_base(self, agent_id: str) -> Optional[AgentKnowledgeBase]:
        """Load agent knowledge base from Redis"""
        try:
            key = f"agent:knowledge:{agent_id}"
            data = await self.redis_client.get(key)

            if data:
                kb_data = json.loads(data)
                return AgentKnowledgeBase(**kb_data)

            return None

        except Exception as e:
            logger.debug(f"Could not load knowledge base for {agent_id}: {e}")
            return None

    async def _save_agent_knowledge_base(self, knowledge_base: AgentKnowledgeBase):
        """Save agent knowledge base to Redis"""
        try:
            key = f"agent:knowledge:{knowledge_base.agent_id}"
            kb_data = asdict(knowledge_base)

            # Convert datetime objects to ISO strings
            if knowledge_base.last_updated:
                kb_data['last_updated'] = knowledge_base.last_updated.isoformat()

            await self.redis_client.setex(
                key,
                86400 * 7,  # 7 day TTL
                json.dumps(kb_data, default=str)
            )

        except Exception as e:
            logger.error(f"Error saving knowledge base for {knowledge_base.agent_id}: {e}")

    async def _process_learning_signals(self, pubsub):
        """Process incoming learning signals from Redis"""
        async for message in pubsub.listen():
            if message['type'] == 'message':
                try:
                    signal_data = json.loads(message['data'])

                    # Route signal to appropriate agents
                    await self._route_signal_to_agents(signal_data)

                except Exception as e:
                    logger.error(f"Error processing learning signal: {e}")

    async def _route_signal_to_agents(self, signal_data: Dict[str, Any]):
        """Route learning signal to relevant agents"""
        try:
            signal_category = signal_data.get('category', 'general')
            target_agents = signal_data.get('target_agents', [])

            # Route to specific target agents
            for agent_id in target_agents:
                if agent_id in self.learning_queues:
                    try:
                        await self.learning_queues[agent_id].put(signal_data)
                    except asyncio.QueueFull:
                        logger.warning(f"Learning queue full for agent {agent_id}")

            # Route to agents based on specialization
            for agent_id, profile in self.agent_profiles.items():
                if profile.specialization == signal_category or signal_category == 'general':
                    if agent_id not in target_agents:  # Avoid duplicates
                        try:
                            await self.learning_queues[agent_id].put(signal_data)
                        except asyncio.QueueFull:
                            logger.warning(f"Learning queue full for agent {agent_id}")

            # Start processing tasks for agents
            asyncio.create_task(self._process_agent_learning_queues())

        except Exception as e:
            logger.error(f"Error routing signal to agents: {e}")

    async def _process_agent_learning_queues(self):
        """Process learning queues for all agents"""
        if not self.learning_active:
            return

        tasks = []
        for agent_id in self.agent_profiles.keys():
            if not self.learning_queues[agent_id].empty():
                task = asyncio.create_task(self._process_agent_learning(agent_id))
                tasks.append(task)

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _process_agent_learning(self, agent_id: str):
        """Process learning for a specific agent"""
        try:
            profile = self.agent_profiles[agent_id]
            knowledge_base = self.agent_knowledge_bases[agent_id]
            learning_queue = self.learning_queues[agent_id]

            # Process up to 5 signals at once to avoid overwhelming
            processed_count = 0
            while not learning_queue.empty() and processed_count < 5:
                try:
                    signal_data = learning_queue.get_nowait()

                    # Determine if agent should learn from this signal
                    should_learn = self._should_agent_learn(profile, signal_data)

                    if should_learn:
                        learning_update = await self._generate_learning_update(profile, signal_data)

                        if learning_update:
                            await self._apply_learning_update(knowledge_base, learning_update)
                            profile.total_signals_processed += 1
                            self.stats['total_learning_updates'] += 1

                    processed_count += 1

                except asyncio.QueueEmpty:
                    break

            # Update profile
            profile.last_learning_update = datetime.now(timezone.utc)

            # Save knowledge base if updated
            if processed_count > 0:
                await self._save_agent_knowledge_base(knowledge_base)

        except Exception as e:
            logger.error(f"Error processing learning for agent {agent_id}: {e}")

    def _should_agent_learn(self, profile: AgentLearningProfile, signal_data: Dict[str, Any]) -> bool:
        """Determine if agent should learn from the signal"""
        try:
            # Check signal confidence against threshold
            signal_confidence = signal_data.get('confidence', 0.0)
            if signal_confidence < profile.confidence_threshold:
                return False

            # Check if signal is relevant to agent's specialization
            signal_category = signal_data.get('category', '')
            if profile.specialization not in ['general'] and signal_category != profile.specialization:
                # Allow some cross-domain learning based on curiosity factor
                if np.random.random() > profile.curiosity_factor:
                    return False

            # Check if signal type is relevant
            spec_config = self.specialization_configs.get(profile.specialization, self.specialization_configs['general'])
            signal_type = signal_data.get('signal_type', '')

            if signal_type in spec_config['signal_filters']:
                return True

            # Allow some exploration based on curiosity
            return np.random.random() < profile.curiosity_factor * 0.3

        except Exception as e:
            logger.error(f"Error determining if agent should learn: {e}")
            return False

    async def _generate_learning_update(self, profile: AgentLearningProfile, signal_data: Dict[str, Any]) -> Optional[LearningUpdate]:
        """Generate learning update from signal data"""
        try:
            signal_type = signal_data.get('signal_type', '')
            signal_content = signal_data.get('content', {})
            key_insights = signal_data.get('key_insights', [])
            actionable_items = signal_data.get('actionable_items', [])

            # Determine learning type based on signal and agent specialization
            learning_type = self._determine_learning_type(profile, signal_data)

            # Generate learning content
            learning_content = {}

            if learning_type == 'knowledge_update':
                learning_content = {
                    'new_knowledge': key_insights,
                    'domain': signal_data.get('category', 'general'),
                    'source_data': signal_content,
                    'confidence': signal_data.get('confidence', 0.0)
                }

            elif learning_type == 'skill_improvement':
                learning_content = {
                    'skill_area': self._identify_skill_area(signal_data, profile.specialization),
                    'improvement_data': actionable_items,
                    'practice_recommendations': self._generate_practice_recommendations(signal_data),
                    'performance_metrics': signal_data.get('trend_indicators', {})
                }

            elif learning_type == 'pattern_recognition':
                learning_content = {
                    'pattern_data': signal_data.get('trend_indicators', {}),
                    'pattern_type': signal_type,
                    'recognition_cues': key_insights,
                    'predictive_indicators': self._extract_predictive_indicators(signal_data)
                }

            # Create learning update
            learning_update = LearningUpdate(
                update_id=f"learning_{profile.agent_id}_{datetime.now().timestamp()}",
                agent_id=profile.agent_id,
                source_signal_id=signal_data.get('signal_id', 'unknown'),
                learning_type=learning_type,
                content=learning_content,
                confidence=signal_data.get('confidence', 0.0),
                timestamp=datetime.now(timezone.utc),
                expires_at=signal_data.get('expires_at')
            )

            return learning_update

        except Exception as e:
            logger.error(f"Error generating learning update: {e}")
            return None

    def _determine_learning_type(self, profile: AgentLearningProfile, signal_data: Dict[str, Any]) -> str:
        """Determine the type of learning for this signal"""
        signal_type = signal_data.get('signal_type', '')
        specialization = profile.specialization

        # Pattern recognition learning for trend-based signals
        if signal_type in ['market_trend', 'content_trend', 'tech_breakthrough']:
            return 'pattern_recognition'

        # Skill improvement for opportunity signals
        elif signal_type in ['job_opportunity', 'monetization_opportunity']:
            return 'skill_improvement'

        # Knowledge update for informational signals
        elif signal_type in ['breaking_news', 'research_published', 'patent_filed']:
            return 'knowledge_update'

        # Default based on specialization focus
        else:
            spec_config = self.specialization_configs.get(specialization, self.specialization_configs['general'])
            return spec_config['learning_focus']

    def _identify_skill_area(self, signal_data: Dict[str, Any], specialization: str) -> str:
        """Identify the skill area for improvement"""
        signal_type = signal_data.get('signal_type', '')
        content = signal_data.get('content', {})

        skill_mapping = {
            'financial': {
                'market_trend': 'market_analysis',
                'price_alert': 'risk_assessment',
                'volume_spike': 'pattern_recognition'
            },
            'freelance': {
                'job_opportunity': 'opportunity_identification',
                'skill_demand': 'skill_assessment',
                'rate_trend': 'pricing_optimization'
            },
            'content': {
                'content_trend': 'trend_analysis',
                'monetization_opportunity': 'monetization_strategy'
            },
            'tech': {
                'tech_breakthrough': 'innovation_assessment',
                'patent_filed': 'patent_analysis'
            }
        }

        return skill_mapping.get(specialization, {}).get(signal_type, 'general_analysis')

    def _generate_practice_recommendations(self, signal_data: Dict[str, Any]) -> List[str]:
        """Generate practice recommendations for skill improvement"""
        actionable_items = signal_data.get('actionable_items', [])
        recommendations = []

        for item in actionable_items[:3]:  # Top 3 items
            recommendations.append(f"Practice: {item}")

        # Add specialization-specific recommendations
        category = signal_data.get('category', '')
        if category == 'financial':
            recommendations.append("Analyze historical data patterns")
            recommendations.append("Study market correlation factors")
        elif category == 'freelance':
            recommendations.append("Research client needs and pain points")
            recommendations.append("Optimize proposal writing techniques")
        elif category == 'content':
            recommendations.append("Experiment with content formats")
            recommendations.append("Test audience engagement strategies")

        return recommendations[:5]

    def _extract_predictive_indicators(self, signal_data: Dict[str, Any]) -> List[str]:
        """Extract predictive indicators from signal data"""
        trend_indicators = signal_data.get('trend_indicators', {})
        indicators = []

        for key, value in trend_indicators.items():
            if isinstance(value, str):
                indicators.append(f"{key}: {value}")
            elif isinstance(value, (int, float)):
                indicators.append(f"{key}: {value}")

        return indicators[:5]

    async def _apply_learning_update(self, knowledge_base: AgentKnowledgeBase, learning_update: LearningUpdate):
        """Apply learning update to agent's knowledge base"""
        try:
            learning_type = learning_update.learning_type
            content = learning_update.content

            if learning_type == 'knowledge_update':
                # Add to domain knowledge
                domain = content.get('domain', 'general')
                if domain not in knowledge_base.domain_knowledge:
                    knowledge_base.domain_knowledge[domain] = []

                knowledge_item = {
                    'knowledge': content.get('new_knowledge', []),
                    'source': learning_update.source_signal_id,
                    'confidence': content.get('confidence', 0.0),
                    'timestamp': learning_update.timestamp.isoformat(),
                    'source_data': content.get('source_data', {})
                }

                knowledge_base.domain_knowledge[domain].append(knowledge_item)
                self.stats['knowledge_items_added'] += 1

            elif learning_type == 'skill_improvement':
                # Update skill improvements
                skill_area = content.get('skill_area', 'general')
                current_score = knowledge_base.skill_improvements.get(skill_area, 0.0)
                improvement = min(0.1, learning_update.confidence * 0.05)  # Gradual improvement

                knowledge_base.skill_improvements[skill_area] = current_score + improvement
                self.stats['skills_enhanced'] += 1

            elif learning_type == 'pattern_recognition':
                # Add learned pattern
                pattern = {
                    'pattern_type': content.get('pattern_type', 'unknown'),
                    'pattern_data': content.get('pattern_data', {}),
                    'recognition_cues': content.get('recognition_cues', []),
                    'predictive_indicators': content.get('predictive_indicators', []),
                    'learned_from': learning_update.source_signal_id,
                    'confidence': learning_update.confidence,
                    'timestamp': learning_update.timestamp.isoformat()
                }

                knowledge_base.learned_patterns.append(pattern)
                self.stats['patterns_learned'] += 1

            # Add to experience log
            experience_entry = {
                'learning_type': learning_type,
                'source_signal': learning_update.source_signal_id,
                'confidence': learning_update.confidence,
                'timestamp': learning_update.timestamp.isoformat(),
                'content_summary': str(content)[:200]  # Truncated summary
            }

            knowledge_base.experience_log.append(experience_entry)

            # Keep experience log manageable
            if len(knowledge_base.experience_log) > 1000:
                knowledge_base.experience_log = knowledge_base.experience_log[-500:]

            # Update timestamps
            knowledge_base.last_updated = learning_update.timestamp
            learning_update.applied = True

        except Exception as e:
            logger.error(f"Error applying learning update: {e}")

    async def get_agent_learning_status(self, agent_id: str) -> Dict[str, Any]:
        """Get learning status for a specific agent"""
        try:
            if agent_id not in self.agent_profiles:
                return {'error': 'Agent not found'}

            profile = self.agent_profiles[agent_id]
            knowledge_base = self.agent_knowledge_bases.get(agent_id)

            status = {
                'agent_id': agent_id,
                'specialization': profile.specialization,
                'learning_active': self.learning_active,
                'total_signals_processed': profile.total_signals_processed,
                'last_learning_update': profile.last_learning_update.isoformat() if profile.last_learning_update else None,
                'learning_rate': profile.learning_rate,
                'curiosity_factor': profile.curiosity_factor,
                'knowledge_domains': list(profile.knowledge_domains),
                'queue_size': self.learning_queues[agent_id].qsize() if agent_id in self.learning_queues else 0
            }

            if knowledge_base:
                status.update({
                    'knowledge_items': sum(len(items) for items in knowledge_base.domain_knowledge.values()),
                    'learned_patterns': len(knowledge_base.learned_patterns),
                    'skill_improvements': len(knowledge_base.skill_improvements),
                    'experience_entries': len(knowledge_base.experience_log),
                    'top_skills': dict(sorted(knowledge_base.skill_improvements.items(),
                                            key=lambda x: x[1], reverse=True)[:5])
                })

            return status

        except Exception as e:
            logger.error(f"Error getting agent learning status: {e}")
            return {'error': str(e)}

    async def get_learning_engine_status(self) -> Dict[str, Any]:
        """Get overall learning engine status"""
        return {
            'learning_active': self.learning_active,
            'agents_tracked': len(self.agent_profiles),
            'knowledge_bases_active': len(self.agent_knowledge_bases),
            'total_learning_updates': self.stats['total_learning_updates'],
            'agents_improved': self.stats['agents_improved'],
            'knowledge_items_added': self.stats['knowledge_items_added'],
            'patterns_learned': self.stats['patterns_learned'],
            'skills_enhanced': self.stats['skills_enhanced'],
            'average_queue_size': np.mean([q.qsize() for q in self.learning_queues.values()]) if self.learning_queues else 0,
            'specialization_distribution': {
                spec: len([p for p in self.agent_profiles.values() if p.specialization == spec])
                for spec in self.specialization_configs.keys()
            }
        }

    async def enhance_agent_with_learned_knowledge(self, agent_id: str, query_context: str = '') -> Dict[str, Any]:
        """Enhance agent execution with learned knowledge"""
        try:
            if agent_id not in self.agent_knowledge_bases:
                return {'enhancement': 'no_knowledge_base', 'data': {}}

            knowledge_base = self.agent_knowledge_bases[agent_id]
            profile = self.agent_profiles[agent_id]

            enhancement = {
                'agent_id': agent_id,
                'specialization': profile.specialization,
                'enhancement_timestamp': datetime.now(timezone.utc).isoformat(),
                'relevant_knowledge': [],
                'applicable_patterns': [],
                'skill_bonuses': {},
                'experience_insights': []
            }

            # Extract relevant knowledge for the query
            for domain, knowledge_items in knowledge_base.domain_knowledge.items():
                for item in knowledge_items[-5:]:  # Recent knowledge
                    if query_context.lower() in str(item).lower() or not query_context:
                        enhancement['relevant_knowledge'].append({
                            'domain': domain,
                            'knowledge': item.get('knowledge', []),
                            'confidence': item.get('confidence', 0.0)
                        })

            # Find applicable patterns
            for pattern in knowledge_base.learned_patterns[-10:]:  # Recent patterns
                if query_context.lower() in str(pattern).lower() or not query_context:
                    enhancement['applicable_patterns'].append({
                        'pattern_type': pattern.get('pattern_type', ''),
                        'cues': pattern.get('recognition_cues', []),
                        'indicators': pattern.get('predictive_indicators', []),
                        'confidence': pattern.get('confidence', 0.0)
                    })

            # Apply skill bonuses
            enhancement['skill_bonuses'] = knowledge_base.skill_improvements.copy()

            # Extract recent experience insights
            for exp in knowledge_base.experience_log[-5:]:  # Recent experience
                enhancement['experience_insights'].append({
                    'learning_type': exp.get('learning_type', ''),
                    'confidence': exp.get('confidence', 0.0),
                    'summary': exp.get('content_summary', '')
                })

            return enhancement

        except Exception as e:
            logger.error(f"Error enhancing agent with learned knowledge: {e}")
            return {'error': str(e)}

    async def cleanup(self):
        """Cleanup learning engine resources"""
        self.learning_active = False

        if self.redis_client:
            await self.redis_client.close()

        # Save all knowledge bases
        for knowledge_base in self.agent_knowledge_bases.values():
            await self._save_agent_knowledge_base(knowledge_base)


# Global learning engine instance
_learning_engine = None

def get_learning_engine() -> AgentLearningEngine:
    """Get or create the global learning engine instance"""
    global _learning_engine
    if _learning_engine is None:
        _learning_engine = AgentLearningEngine()
    return _learning_engine


# Convenience functions
async def start_agent_learning():
    """Start the agent learning engine"""
    engine = get_learning_engine()
    await engine.initialize()
    return engine


async def enhance_agent_execution(agent_id: str, context: str = '') -> Dict[str, Any]:
    """Enhance agent execution with learned knowledge"""
    engine = get_learning_engine()
    return await engine.enhance_agent_with_learned_knowledge(agent_id, context)


async def get_agent_learning_stats() -> Dict[str, Any]:
    """Get agent learning statistics"""
    engine = get_learning_engine()
    return await engine.get_learning_engine_status()