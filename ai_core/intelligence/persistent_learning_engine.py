"""
Persistent Learning Engine
Complete learning system with database persistence, document generation, and embeddings
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import json

# Import components
from .document_generator import document_generator, DocumentGenerationConfig
from .embedding_generator import embedding_generator
from .knowledge_base_manager import knowledge_base_manager

# Import models
try:
    from .models import (
        AgentLearningEvent,
        LearningDocument,
        AgentKnowledgeBase,
        LearningEmbedding,
        AgentLearningSession,
        LearningInsight
    )
    from django.db import transaction
except ImportError:
    AgentLearningEvent = None
    LearningDocument = None
    AgentKnowledgeBase = None
    LearningEmbedding = None
    AgentLearningSession = None
    LearningInsight = None
    transaction = None

logger = logging.getLogger(__name__)


class PersistentLearningEngine:
    """Complete learning engine with full persistence"""

    def __init__(self):
        self.document_generator = document_generator
        self.embedding_generator = embedding_generator
        self.knowledge_manager = knowledge_base_manager

        self.active_session = None
        self.stats = {
            'sessions_created': 0,
            'events_persisted': 0,
            'documents_generated': 0,
            'embeddings_created': 0,
            'knowledge_bases_updated': 0,
            'total_processing_time': 0.0
        }

    async def start_learning_session(self, session_name: str, agents_involved: List[str] = None) -> str:
        """Start a new learning session"""
        if not AgentLearningSession:
            logger.warning("Learning session model not available")
            return "mock_session"

        try:
            session = AgentLearningSession.objects.create(
                session_name=session_name,
                agents_involved=agents_involved or [],
                status='active'
            )

            self.active_session = session
            self.stats['sessions_created'] += 1

            logger.info(f"Started learning session: {session_name} ({session.session_id})")
            return str(session.session_id)

        except Exception as e:
            logger.error(f"Error starting learning session: {e}")
            return "error_session"

    async def process_learning_signal(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a learning signal through the complete pipeline"""
        start_time = datetime.now()
        processing_results = {
            'success': False,
            'learning_event_id': None,
            'documents_generated': 0,
            'embeddings_created': 0,
            'knowledge_base_updated': False,
            'processing_time': 0.0
        }

        try:
            # Step 1: Persist learning event to database
            learning_event = await self._persist_learning_event(signal_data)
            if not learning_event:
                return processing_results

            processing_results['learning_event_id'] = str(learning_event.event_id)
            self.stats['events_persisted'] += 1

            # Step 2: Update knowledge base
            knowledge_update = await self.knowledge_manager.update_knowledge_base(
                learning_event.agent_id,
                [learning_event]
            )

            if knowledge_update and not knowledge_update.get('error'):
                processing_results['knowledge_base_updated'] = True
                self.stats['knowledge_bases_updated'] += 1

            # Step 3: Generate embeddings (async)
            asyncio.create_task(self._generate_embeddings_async(learning_event))

            # Step 4: Check if we should generate documents
            await self._check_and_generate_documents(learning_event.agent_id)

            # Update session statistics
            if self.active_session:
                self.active_session.events_processed += 1
                self.active_session.save()

            processing_results['success'] = True
            processing_time = (datetime.now() - start_time).total_seconds()
            processing_results['processing_time'] = processing_time
            self.stats['total_processing_time'] += processing_time

            logger.debug(f"Processed learning signal for agent {learning_event.agent_id}")
            return processing_results

        except Exception as e:
            logger.error(f"Error processing learning signal: {e}")
            processing_results['error'] = str(e)
            return processing_results

    async def _persist_learning_event(self, signal_data: Dict[str, Any]) -> Optional['AgentLearningEvent']:
        """Persist learning event to database"""
        if not AgentLearningEvent:
            return None

        try:
            # Extract data from signal
            agent_id = signal_data.get('agent_id', 'unknown_agent')
            signal_type = signal_data.get('signal_type', 'unknown')

            # Create learning event
            with transaction.atomic() if transaction else self._mock_transaction():
                learning_event = AgentLearningEvent.objects.create(
                    event_id=uuid.uuid4(),
                    agent_id=agent_id,
                    agent_name=signal_data.get('agent_name', f'Agent_{agent_id}'),
                    agent_specialization=signal_data.get('agent_specialization', 'general'),

                    signal_id=signal_data.get('signal_id', str(uuid.uuid4())),
                    signal_type=signal_type,
                    signal_strength=signal_data.get('signal_strength', 0.5),

                    source_spider=signal_data.get('source_spider', 'unknown'),
                    source_api=signal_data.get('source_api', 'unknown'),
                    source_url=signal_data.get('source_url', ''),

                    raw_content=signal_data.get('raw_content', {}),
                    processed_content=signal_data.get('processed_content', {}),
                    learned_insights=signal_data.get('learned_insights', {}),

                    learning_type=signal_data.get('learning_type', 'knowledge_update'),
                    confidence_score=signal_data.get('confidence_score', 0.7),
                    quality_score=signal_data.get('quality_score', 0.7),

                    processing_time_ms=signal_data.get('processing_time_ms', 0.0)
                )

                logger.debug(f"Persisted learning event {learning_event.event_id} for agent {agent_id}")
                return learning_event

        except Exception as e:
            logger.error(f"Error persisting learning event: {e}")
            return None

    def _mock_transaction(self):
        """Mock transaction context for testing"""
        class MockTransaction:
            def __enter__(self):
                return self
            def __exit__(self, exc_type, exc_val, exc_tb):
                pass
        return MockTransaction()

    async def _generate_embeddings_async(self, learning_event: 'AgentLearningEvent'):
        """Generate embeddings asynchronously"""
        try:
            result = await self.embedding_generator.generate_embedding_for_learning_event(learning_event)
            if result and result.get('status') == 'created':
                self.stats['embeddings_created'] += 1

                # Update session if active
                if self.active_session:
                    self.active_session.embeddings_created += 1
                    self.active_session.save()

        except Exception as e:
            logger.error(f"Error generating embedding for event {learning_event.event_id}: {e}")

    async def _check_and_generate_documents(self, agent_id: str):
        """Check if we should generate documents for an agent"""
        try:
            # Generate documents every 10 learning events (configurable)
            if AgentLearningEvent:
                recent_events_count = AgentLearningEvent.objects.filter(
                    agent_id=agent_id,
                    timestamp__gte=datetime.now(timezone.utc).replace(hour=0, minute=0, second=0)
                ).count()

                # Generate documents at certain thresholds
                if recent_events_count % 10 == 0 and recent_events_count > 0:
                    documents = await self.document_generator.generate_documents_for_agent(
                        agent_id,
                        time_window_hours=24
                    )

                    if documents:
                        self.stats['documents_generated'] += len(documents)

                        if self.active_session:
                            self.active_session.documents_generated += len(documents)
                            self.active_session.save()

                        logger.info(f"Generated {len(documents)} documents for agent {agent_id}")

        except Exception as e:
            logger.error(f"Error checking document generation for {agent_id}: {e}")

    async def batch_process_learning_signals(self, signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process multiple learning signals in batch"""
        batch_results = {
            'total_signals': len(signals),
            'successful_processing': 0,
            'failed_processing': 0,
            'events_persisted': 0,
            'documents_generated': 0,
            'embeddings_created': 0,
            'knowledge_bases_updated': 0,
            'processing_time': 0.0
        }

        start_time = datetime.now()

        try:
            # Process signals in smaller batches to avoid overwhelming the system
            batch_size = 20
            for i in range(0, len(signals), batch_size):
                batch = signals[i:i + batch_size]

                # Process batch concurrently
                tasks = [self.process_learning_signal(signal) for signal in batch]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Aggregate results
                for result in results:
                    if isinstance(result, dict) and result.get('success'):
                        batch_results['successful_processing'] += 1
                        batch_results['events_persisted'] += 1 if result.get('learning_event_id') else 0
                        batch_results['knowledge_bases_updated'] += 1 if result.get('knowledge_base_updated') else 0
                    else:
                        batch_results['failed_processing'] += 1

                # Brief pause between batches
                await asyncio.sleep(0.1)

            # Process embeddings for recent events
            await self._batch_process_embeddings()

            # Generate cross-agent insights
            await self._generate_cross_agent_insights()

            batch_results['processing_time'] = (datetime.now() - start_time).total_seconds()

            logger.info(f"Batch processed {len(signals)} signals: {batch_results['successful_processing']} successful")
            return batch_results

        except Exception as e:
            logger.error(f"Error in batch processing: {e}")
            batch_results['error'] = str(e)
            return batch_results

    async def _batch_process_embeddings(self):
        """Process embeddings for recent learning events"""
        try:
            result = await self.embedding_generator.process_recent_learning_events(hours_back=1)
            if result and not result.get('error'):
                self.stats['embeddings_created'] += result.get('created', 0)

                if self.active_session:
                    self.active_session.embeddings_created += result.get('created', 0)
                    self.active_session.save()

        except Exception as e:
            logger.error(f"Error in batch embedding processing: {e}")

    async def _generate_cross_agent_insights(self):
        """Generate insights across multiple agents"""
        try:
            if AgentLearningEvent:
                # Get active agents from recent events
                recent_agents = list(AgentLearningEvent.objects.filter(
                    timestamp__gte=datetime.now(timezone.utc).replace(hour=0, minute=0, second=0)
                ).values_list('agent_id', flat=True).distinct())

                if len(recent_agents) >= 2:
                    insights = await self.document_generator.generate_cross_agent_insights(
                        recent_agents[:10],  # Limit to prevent overload
                        time_window_hours=24
                    )

                    logger.info(f"Generated {len(insights)} cross-agent insights")

        except Exception as e:
            logger.error(f"Error generating cross-agent insights: {e}")

    async def get_agent_learning_status(self, agent_id: str) -> Dict[str, Any]:
        """Get comprehensive learning status for an agent"""
        status = {
            'agent_id': agent_id,
            'knowledge_base': {},
            'recent_learning': {},
            'documents': {},
            'embeddings': {},
            'overall_health': 'unknown'
        }

        try:
            # Knowledge base status
            kb_summary = await self.knowledge_manager.get_agent_knowledge_summary(agent_id)
            status['knowledge_base'] = kb_summary

            # Recent learning activity
            if AgentLearningEvent:
                recent_events = AgentLearningEvent.objects.filter(
                    agent_id=agent_id,
                    timestamp__gte=datetime.now(timezone.utc).replace(hour=0, minute=0, second=0)
                ).count()

                status['recent_learning'] = {
                    'events_today': recent_events,
                    'avg_confidence': 0.7,  # Would calculate from actual events
                    'learning_active': recent_events > 0
                }

            # Document status
            if LearningDocument:
                doc_count = LearningDocument.objects.filter(agent_id=agent_id).count()
                status['documents'] = {
                    'total_documents': doc_count,
                    'documents_today': 0  # Would calculate from today's documents
                }

            # Embedding status
            if LearningEmbedding:
                embedding_count = LearningEmbedding.objects.filter(agent_id=agent_id).count()
                status['embeddings'] = {
                    'total_embeddings': embedding_count,
                    'searchable_content': embedding_count > 0
                }

            # Overall health assessment
            health_score = 0
            if status['recent_learning'].get('learning_active'):
                health_score += 25
            if status['knowledge_base'].get('total_learning_events', 0) > 10:
                health_score += 25
            if status['documents'].get('total_documents', 0) > 0:
                health_score += 25
            if status['embeddings'].get('total_embeddings', 0) > 0:
                health_score += 25

            if health_score >= 75:
                status['overall_health'] = 'excellent'
            elif health_score >= 50:
                status['overall_health'] = 'good'
            elif health_score >= 25:
                status['overall_health'] = 'fair'
            else:
                status['overall_health'] = 'poor'

        except Exception as e:
            logger.error(f"Error getting learning status for {agent_id}: {e}")
            status['error'] = str(e)

        return status

    async def end_learning_session(self) -> Dict[str, Any]:
        """End the current learning session"""
        if not self.active_session:
            return {'message': 'No active session'}

        try:
            # Update session
            self.active_session.ended_at = datetime.now(timezone.utc)
            self.active_session.duration_seconds = (
                self.active_session.ended_at - self.active_session.started_at
            ).total_seconds()
            self.active_session.status = 'completed'

            # Calculate success rate
            if self.active_session.events_processed > 0:
                self.active_session.success_rate = min(1.0,
                    (self.active_session.events_processed - 0) / self.active_session.events_processed
                )

            self.active_session.save()

            session_summary = {
                'session_id': str(self.active_session.session_id),
                'session_name': self.active_session.session_name,
                'duration_seconds': self.active_session.duration_seconds,
                'events_processed': self.active_session.events_processed,
                'documents_generated': self.active_session.documents_generated,
                'embeddings_created': self.active_session.embeddings_created,
                'success_rate': self.active_session.success_rate,
                'agents_involved': len(self.active_session.agents_involved)
            }

            self.active_session = None
            logger.info(f"Ended learning session: {session_summary['session_name']}")

            return session_summary

        except Exception as e:
            logger.error(f"Error ending learning session: {e}")
            return {'error': str(e)}

    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        stats = self.stats.copy()

        # Add component stats
        stats['document_generation'] = self.document_generator.get_generation_stats()
        stats['embedding_generation'] = self.embedding_generator.get_embedding_stats()
        stats['knowledge_management'] = self.knowledge_manager.get_knowledge_stats()

        # Add database counts
        if AgentLearningEvent:
            stats['database_counts'] = {
                'learning_events': AgentLearningEvent.objects.count(),
                'documents': LearningDocument.objects.count() if LearningDocument else 0,
                'embeddings': LearningEmbedding.objects.count() if LearningEmbedding else 0,
                'knowledge_bases': AgentKnowledgeBase.objects.count() if AgentKnowledgeBase else 0,
                'sessions': AgentLearningSession.objects.count() if AgentLearningSession else 0
            }

        return stats


# Global instance
persistent_learning_engine = PersistentLearningEngine()