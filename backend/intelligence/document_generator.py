"""
Learning Document Generator
Automatically creates documents and insights from agent learning events
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
import json
import hashlib
from collections import defaultdict

# Import models
try:
    from .models import (
        AgentLearningEvent,
        LearningDocument,
        AgentKnowledgeBase,
        LearningInsight
    )
except ImportError:
    # Fallback for testing
    AgentLearningEvent = None
    LearningDocument = None
    AgentKnowledgeBase = None
    LearningInsight = None

# Import LLM integration
from core.llm_enforcer import get_llm_enforcer

logger = logging.getLogger(__name__)


@dataclass
class DocumentGenerationConfig:
    """Configuration for document generation"""
    min_events_for_document: int = 5
    min_confidence_threshold: float = 0.6
    document_types_enabled: List[str] = None
    max_content_length: int = 5000
    auto_generate_insights: bool = True
    embedding_enabled: bool = True

    def __post_init__(self):
        if self.document_types_enabled is None:
            self.document_types_enabled = [
                'insight', 'summary', 'analysis', 'recommendation'
            ]


class LearningDocumentGenerator:
    """Generates documents from agent learning events"""

    def __init__(self, config: DocumentGenerationConfig = None):
        self.config = config or DocumentGenerationConfig()
        self.llm_enforcer = get_llm_enforcer()
        self.generation_templates = self._initialize_templates()
        self.stats = {
            'documents_generated': 0,
            'insights_created': 0,
            'embeddings_generated': 0,
            'processing_time': 0.0
        }

    def _initialize_templates(self) -> Dict[str, str]:
        """Initialize document generation templates"""
        return {
            'insight': """
Based on the following learning events, generate an agent insight:

Agent: {agent_name} ({specialization})
Learning Events: {event_count}
Time Period: {time_period}

Key Data Points:
{key_data}

Generate a concise insight document that includes:
1. Main insight/discovery
2. Supporting evidence
3. Confidence level
4. Implications for future decisions

Format as a professional insight report.
""",

            'summary': """
Create a learning summary for the following agent activity:

Agent: {agent_name}
Period: {time_period}
Events Processed: {event_count}
Data Sources: {data_sources}

Learning Events Summary:
{events_summary}

Generate a comprehensive summary including:
1. What the agent learned
2. Key patterns identified
3. Performance metrics
4. Areas for improvement

Keep it concise but informative.
""",

            'analysis': """
Perform an analysis of the following agent learning data:

Agent: {agent_name} - {specialization}
Analysis Period: {time_period}
Data Points: {event_count}

Learning Data:
{learning_data}

Provide a detailed analysis covering:
1. Data quality assessment
2. Learning patterns identified
3. Anomalies or unusual findings
4. Confidence in conclusions
5. Recommendations for optimization

Be objective and data-driven in your analysis.
""",

            'recommendation': """
Based on the agent's learning history, provide strategic recommendations:

Agent: {agent_name}
Specialization: {specialization}
Learning Period: {time_period}
Events Analyzed: {event_count}

Key Learning Areas:
{learning_areas}

Recent Insights:
{recent_insights}

Generate actionable recommendations for:
1. Improving learning efficiency
2. Focusing on high-value data sources
3. Optimizing decision-making processes
4. Enhancing specialized capabilities

Provide specific, measurable recommendations.
"""
        }

    async def generate_documents_for_agent(self, agent_id: str, time_window_hours: int = 24) -> List[Dict[str, Any]]:
        """Generate documents for a specific agent based on recent learning"""
        start_time = datetime.now()

        try:
            # Get recent learning events
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=time_window_hours)

            if AgentLearningEvent:
                events = AgentLearningEvent.objects.filter(
                    agent_id=agent_id,
                    timestamp__gte=cutoff_time,
                    confidence_score__gte=self.config.min_confidence_threshold
                ).order_by('-timestamp')[:50]  # Limit to recent 50 events

                if len(events) < self.config.min_events_for_document:
                    logger.info(f"Insufficient events ({len(events)}) for agent {agent_id}")
                    return []

                # Group events by type for better analysis
                events_by_type = defaultdict(list)
                for event in events:
                    events_by_type[event.signal_type].append(event)

                generated_docs = []

                # Generate different types of documents
                for doc_type in self.config.document_types_enabled:
                    if doc_type == 'insight' and len(events) >= 5:
                        doc = await self._generate_insight_document(agent_id, events, events_by_type)
                        if doc:
                            generated_docs.append(doc)

                    elif doc_type == 'summary' and len(events) >= 3:
                        doc = await self._generate_summary_document(agent_id, events, events_by_type)
                        if doc:
                            generated_docs.append(doc)

                    elif doc_type == 'analysis' and len(events) >= 7:
                        doc = await self._generate_analysis_document(agent_id, events, events_by_type)
                        if doc:
                            generated_docs.append(doc)

                    elif doc_type == 'recommendation' and len(events) >= 10:
                        doc = await self._generate_recommendation_document(agent_id, events, events_by_type)
                        if doc:
                            generated_docs.append(doc)

                # Update stats
                self.stats['documents_generated'] += len(generated_docs)
                self.stats['processing_time'] += (datetime.now() - start_time).total_seconds()

                logger.info(f"Generated {len(generated_docs)} documents for agent {agent_id}")
                return generated_docs

        except Exception as e:
            logger.error(f"Error generating documents for agent {agent_id}: {e}")
            return []

        return []

    async def _generate_insight_document(self, agent_id: str, events: List, events_by_type: Dict) -> Optional[Dict]:
        """Generate an insight document from learning events"""
        try:
            # Get agent info
            first_event = events[0]
            agent_name = first_event.agent_name
            specialization = first_event.agent_specialization

            # Prepare key data points
            key_data = []
            for signal_type, type_events in events_by_type.items():
                avg_confidence = sum(e.confidence_score for e in type_events) / len(type_events)
                key_data.append(f"- {signal_type}: {len(type_events)} events, avg confidence: {avg_confidence:.2f}")

            # Calculate time period
            time_period = f"{events[-1].timestamp.strftime('%Y-%m-%d')} to {events[0].timestamp.strftime('%Y-%m-%d')}"

            # Generate prompt
            prompt = self.generation_templates['insight'].format(
                agent_name=agent_name,
                specialization=specialization,
                event_count=len(events),
                time_period=time_period,
                key_data='\n'.join(key_data)
            )

            # Generate content using LLM
            result = self.llm_enforcer.enforce_real_ai(
                prompt=prompt,
                agent_name=f"DocumentGenerator_{agent_id}",
                task_type="document_generation",
                max_tokens=1500,
                temperature=0.3
            )

            if result.get('success'):
                # Create document record
                if LearningDocument:
                    doc = LearningDocument.objects.create(
                        title=f"{agent_name} Learning Insights - {datetime.now().strftime('%Y-%m-%d')}",
                        document_type='insight',
                        agent_id=agent_id,
                        agent_name=agent_name,
                        content=result['response'],
                        summary=result['response'][:500] + "..." if len(result['response']) > 500 else result['response'],
                        confidence_level=sum(e.confidence_score for e in events) / len(events),
                        event_count=len(events),
                        word_count=len(result['response'].split())
                    )

                    # Link source events
                    doc.source_events.set(events)

                    return {
                        'document_id': str(doc.document_id),
                        'type': 'insight',
                        'title': doc.title,
                        'content': doc.content,
                        'agent_id': agent_id
                    }

        except Exception as e:
            logger.error(f"Error generating insight document: {e}")

        return None

    async def _generate_summary_document(self, agent_id: str, events: List, events_by_type: Dict) -> Optional[Dict]:
        """Generate a summary document"""
        try:
            first_event = events[0]
            agent_name = first_event.agent_name

            # Create events summary
            events_summary = []
            for signal_type, type_events in events_by_type.items():
                sources = set(e.source_api for e in type_events)
                events_summary.append(f"- {signal_type}: {len(type_events)} events from {', '.join(sources)}")

            time_period = f"{events[-1].timestamp.strftime('%Y-%m-%d')} to {events[0].timestamp.strftime('%Y-%m-%d')}"
            data_sources = list(set(e.source_api for e in events))

            prompt = self.generation_templates['summary'].format(
                agent_name=agent_name,
                time_period=time_period,
                event_count=len(events),
                data_sources=', '.join(data_sources),
                events_summary='\n'.join(events_summary)
            )

            result = self.llm_enforcer.enforce_real_ai(
                prompt=prompt,
                agent_name=f"DocumentGenerator_{agent_id}",
                task_type="document_generation",
                max_tokens=1200
            )

            if result.get('success') and LearningDocument:
                doc = LearningDocument.objects.create(
                    title=f"{agent_name} Learning Summary - {datetime.now().strftime('%Y-%m-%d')}",
                    document_type='summary',
                    agent_id=agent_id,
                    agent_name=agent_name,
                    content=result['response'],
                    summary=result['response'][:300] + "..." if len(result['response']) > 300 else result['response'],
                    confidence_level=sum(e.confidence_score for e in events) / len(events),
                    event_count=len(events),
                    word_count=len(result['response'].split())
                )

                doc.source_events.set(events)

                return {
                    'document_id': str(doc.document_id),
                    'type': 'summary',
                    'title': doc.title,
                    'content': doc.content,
                    'agent_id': agent_id
                }

        except Exception as e:
            logger.error(f"Error generating summary document: {e}")

        return None

    async def _generate_analysis_document(self, agent_id: str, events: List, events_by_type: Dict) -> Optional[Dict]:
        """Generate an analysis document"""
        try:
            first_event = events[0]
            agent_name = first_event.agent_name
            specialization = first_event.agent_specialization

            # Prepare detailed learning data
            learning_data = []
            for signal_type, type_events in events_by_type.items():
                avg_quality = sum(e.quality_score for e in type_events) / len(type_events)
                avg_confidence = sum(e.confidence_score for e in type_events) / len(type_events)
                sources = list(set(e.source_api for e in type_events))

                learning_data.append(f"""
Signal Type: {signal_type}
- Events: {len(type_events)}
- Average Quality: {avg_quality:.3f}
- Average Confidence: {avg_confidence:.3f}
- Data Sources: {', '.join(sources)}
""")

            time_period = f"{events[-1].timestamp.strftime('%Y-%m-%d')} to {events[0].timestamp.strftime('%Y-%m-%d')}"

            prompt = self.generation_templates['analysis'].format(
                agent_name=agent_name,
                specialization=specialization,
                time_period=time_period,
                event_count=len(events),
                learning_data='\n'.join(learning_data)
            )

            result = self.llm_enforcer.enforce_real_ai(
                prompt=prompt,
                agent_name=f"DocumentGenerator_{agent_id}",
                task_type="document_generation",
                max_tokens=2000,
                temperature=0.2  # Lower temperature for analysis
            )

            if result.get('success') and LearningDocument:
                doc = LearningDocument.objects.create(
                    title=f"{agent_name} Learning Analysis - {datetime.now().strftime('%Y-%m-%d')}",
                    document_type='analysis',
                    agent_id=agent_id,
                    agent_name=agent_name,
                    content=result['response'],
                    summary=result['response'][:400] + "..." if len(result['response']) > 400 else result['response'],
                    confidence_level=sum(e.confidence_score for e in events) / len(events),
                    event_count=len(events),
                    word_count=len(result['response'].split())
                )

                doc.source_events.set(events)

                return {
                    'document_id': str(doc.document_id),
                    'type': 'analysis',
                    'title': doc.title,
                    'content': doc.content,
                    'agent_id': agent_id
                }

        except Exception as e:
            logger.error(f"Error generating analysis document: {e}")

        return None

    async def _generate_recommendation_document(self, agent_id: str, events: List, events_by_type: Dict) -> Optional[Dict]:
        """Generate a recommendation document"""
        try:
            first_event = events[0]
            agent_name = first_event.agent_name
            specialization = first_event.agent_specialization

            # Identify learning areas
            learning_areas = []
            for signal_type, type_events in events_by_type.items():
                performance = sum(e.confidence_score * e.quality_score for e in type_events) / len(type_events)
                learning_areas.append(f"- {signal_type}: {performance:.2f} performance score")

            # Get recent insights from other documents
            recent_insights = ["Analyze patterns from recent learning events", "Focus on high-confidence signals"]

            time_period = f"{events[-1].timestamp.strftime('%Y-%m-%d')} to {events[0].timestamp.strftime('%Y-%m-%d')}"

            prompt = self.generation_templates['recommendation'].format(
                agent_name=agent_name,
                specialization=specialization,
                time_period=time_period,
                event_count=len(events),
                learning_areas='\n'.join(learning_areas),
                recent_insights='\n'.join(recent_insights)
            )

            result = self.llm_enforcer.enforce_real_ai(
                prompt=prompt,
                agent_name=f"DocumentGenerator_{agent_id}",
                task_type="document_generation",
                max_tokens=1800
            )

            if result.get('success') and LearningDocument:
                doc = LearningDocument.objects.create(
                    title=f"{agent_name} Strategic Recommendations - {datetime.now().strftime('%Y-%m-%d')}",
                    document_type='recommendation',
                    agent_id=agent_id,
                    agent_name=agent_name,
                    content=result['response'],
                    summary=result['response'][:350] + "..." if len(result['response']) > 350 else result['response'],
                    confidence_level=sum(e.confidence_score for e in events) / len(events),
                    event_count=len(events),
                    word_count=len(result['response'].split())
                )

                doc.source_events.set(events)

                return {
                    'document_id': str(doc.document_id),
                    'type': 'recommendation',
                    'title': doc.title,
                    'content': doc.content,
                    'agent_id': agent_id
                }

        except Exception as e:
            logger.error(f"Error generating recommendation document: {e}")

        return None

    async def generate_cross_agent_insights(self, agent_ids: List[str], time_window_hours: int = 24) -> List[Dict]:
        """Generate insights that span multiple agents"""
        insights = []

        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=time_window_hours)

            if AgentLearningEvent:
                # Get events from all specified agents
                events = AgentLearningEvent.objects.filter(
                    agent_id__in=agent_ids,
                    timestamp__gte=cutoff_time,
                    confidence_score__gte=self.config.min_confidence_threshold
                ).order_by('-timestamp')

                if len(events) >= 10:  # Need substantial data for cross-agent insights
                    # Group by signal types across agents
                    cross_patterns = defaultdict(lambda: defaultdict(list))
                    for event in events:
                        cross_patterns[event.signal_type][event.agent_id].append(event)

                    # Generate insights for patterns that appear across multiple agents
                    for signal_type, agent_events in cross_patterns.items():
                        if len(agent_events) >= 2:  # At least 2 agents involved
                            insight = await self._generate_cross_agent_insight(signal_type, agent_events, events)
                            if insight:
                                insights.append(insight)

                self.stats['insights_created'] += len(insights)

        except Exception as e:
            logger.error(f"Error generating cross-agent insights: {e}")

        return insights

    async def _generate_cross_agent_insight(self, signal_type: str, agent_events: Dict, all_events: List) -> Optional[Dict]:
        """Generate insight from cross-agent patterns"""
        try:
            # Prepare cross-agent analysis
            agents_data = []
            for agent_id, events in agent_events.items():
                avg_confidence = sum(e.confidence_score for e in events) / len(events)
                agents_data.append(f"- {agent_id}: {len(events)} events, confidence: {avg_confidence:.2f}")

            prompt = f"""
Analyze this cross-agent learning pattern:

Signal Type: {signal_type}
Agents Involved: {len(agent_events)}
Total Events: {sum(len(events) for events in agent_events.values())}

Agent Performance:
{chr(10).join(agents_data)}

Identify:
1. Common patterns across agents
2. Performance differences
3. Collaborative opportunities
4. System-wide insights

Generate a strategic cross-agent insight.
"""

            result = self.llm_enforcer.enforce_real_ai(
                prompt=prompt,
                agent_name="CrossAgentAnalyzer",
                task_type="insight_generation",
                max_tokens=1000
            )

            if result.get('success') and LearningInsight:
                insight = LearningInsight.objects.create(
                    title=f"Cross-Agent Pattern: {signal_type}",
                    insight_type='pattern',
                    description=result['response'],
                    contributing_agents=list(agent_events.keys()),
                    confidence_score=0.8,
                    impact_score=0.7,
                    urgency_level='medium'
                )

                # Link to source events
                relevant_events = [e for events in agent_events.values() for e in events]
                insight.source_events.set(relevant_events[:20])  # Limit for performance

                return {
                    'insight_id': str(insight.insight_id),
                    'title': insight.title,
                    'description': insight.description,
                    'agents_involved': len(agent_events),
                    'confidence': insight.confidence_score
                }

        except Exception as e:
            logger.error(f"Error generating cross-agent insight: {e}")

        return None

    def get_generation_stats(self) -> Dict[str, Any]:
        """Get document generation statistics"""
        return self.stats.copy()

    async def cleanup_old_documents(self, days_to_keep: int = 30):
        """Clean up old documents to prevent database bloat"""
        if LearningDocument:
            cutoff = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
            deleted = LearningDocument.objects.filter(created_at__lt=cutoff).delete()
            logger.info(f"Cleaned up {deleted[0]} old documents")


# Global instance
document_generator = LearningDocumentGenerator()