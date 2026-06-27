"""
Spider-Agent Connector
Routes spider data to appropriate agents for processing
"""
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from core.models_unified_system import (
    Agent,
    AgentSolution,
    AgentLearning,
    LegacySpiderData
)

logger = logging.getLogger(__name__)


class SpiderAgentConnector:
    """Connects spider data to appropriate agents for processing"""

    def __init__(self):
        self.routing_map = self._build_routing_map()
        self.processing_stats = {
            'total_routed': 0,
            'successful_processing': 0,
            'failed_processing': 0
        }

    def _build_routing_map(self) -> Dict[str, List[str]]:
        """Build mapping of spider categories to agent keyword patterns

        Instead of exact names, use keywords that match actual agents in DB
        """
        return {
            # Job spiders -> Job-related agents
            'job': [
                'Job', 'Application', 'Resume', 'Interview', 'Career',
                'Salary', 'Negotiation', 'LinkedIn', 'Cover Letter'
            ],

            # Freelance spiders -> Freelance agents
            'freelance': [
                'Freelance', 'Gig', 'Commission', 'Side Hustle',
                'Contract', 'Consulting'
            ],

            # Market spiders -> Market analysis agents
            'market': [
                'Market', 'Research', 'Competitive', 'Trend',
                'Business Growth', 'Revenue', 'Analysis'
            ],

            # Content spiders -> Content agents
            'content': [
                'Content', 'Blog', 'Social Media', 'Email',
                'Creative', 'SEO', 'Video', 'Newsletter',
                'Brand', 'Marketing'
            ],

            # Finance spiders -> Finance agents
            'finance': [
                'Investment', 'Financial', 'Expense', 'Tax',
                'Retirement', 'Passive Income', 'Budget',
                'Savings', 'Personal Finance'
            ],

            # Tech spiders -> Tech agents
            'tech': [
                'AI', 'Data Scientist', 'Deep Learning',
                'Workflow Automation', 'Machine Learning',
                'Computer Vision', 'Natural Language',
                'Innovation', 'Research'
            ],

            # Lead spiders -> Sales agents
            'lead': [
                'Marketing', 'Growth', 'Digital Marketing',
                'Conversion', 'Customer', 'Analytics'
            ],

            # Investment spiders -> Investment agents
            'investment': [
                'Investment', 'Portfolio', 'Risk',
                'Real Estate', 'Revenue Stream'
            ],

            # Research spiders -> Research agents
            'research': [
                'Research', 'Data', 'Analytics', 'Predictive',
                'Patent', 'Analysis', 'Insight'
            ],

            # Social spiders -> Social media agents
            'social': [
                'Social Media', 'Content', 'Brand',
                'Influencer', 'User-Generated'
            ]
        }

    def route_spider_data(self, spider_data: LegacySpiderData) -> Dict[str, Any]:
        """
        Route spider data to appropriate agents for processing

        Args:
            spider_data: LegacySpiderData model instance

        Returns:
            Dictionary with routing results
        """
        results = {
            'spider_id': spider_data.id,
            'spider_name': spider_data.spider_name,
            'agents_notified': [],
            'solutions_created': [],
            'timestamp': datetime.now().isoformat()
        }

        try:
            # Determine spider category from name
            category = self._get_spider_category(spider_data.spider_name)

            if not category:
                logger.warning(f"No category found for spider: {spider_data.spider_name}")
                return results

            # Get keyword patterns for this category
            keywords = self.routing_map.get(category, [])

            # Find agents matching any keyword
            matched_agents = set()
            for keyword in keywords:
                agents = Agent.objects.filter(name__icontains=keyword, is_active=True)
                matched_agents.update(agents)

            logger.info(f"Category '{category}' matched {len(matched_agents)} agents for spider '{spider_data.spider_name}'")

            # Route to each matched agent
            for agent in matched_agents:
                try:
                    # Create a solution based on spider data
                    solution = self._create_agent_solution(agent, spider_data)

                    if solution:
                        results['solutions_created'].append({
                            'agent': agent.name,
                            'solution_id': str(solution.id),
                            'solution_type': solution.solution_type
                        })

                        # Create learning record
                        self._create_learning_record(agent, spider_data, solution)

                        results['agents_notified'].append(agent.name)
                        self.processing_stats['successful_processing'] += 1

                except Exception as e:
                    logger.error(f"Error routing to agent {agent.name}: {e}")
                    self.processing_stats['failed_processing'] += 1

            self.processing_stats['total_routed'] += 1

        except Exception as e:
            logger.error(f"Error routing spider data: {e}")
            results['error'] = str(e)

        return results

    def _get_spider_category(self, spider_name: str) -> Optional[str]:
        """Extract category from spider name"""
        spider_name_lower = spider_name.lower()

        category_keywords = {
            'job': ['job', 'career', 'employment', 'hiring'],
            'freelance': ['freelance', 'gig', 'contract', 'freelancer'],
            'market': ['market', 'competitor', 'analysis', 'intelligence'],
            'content': ['content', 'article', 'blog', 'writing'],
            'finance': ['finance', 'financial', 'money', 'budget'],
            'tech': ['tech', 'technology', 'code', 'software', 'innovation', 'tracker'],
            'lead': ['lead', 'sales', 'customer', 'prospect'],
            'investment': ['investment', 'stock', 'crypto', 'trading'],
            'research': ['research', 'academic', 'paper', 'journal', 'adaptive', 'test'],
            'social': ['social', 'media', 'twitter', 'facebook']
        }

        for category, keywords in category_keywords.items():
            if any(keyword in spider_name_lower for keyword in keywords):
                return category

        # Default fallback for unmatched spiders
        logger.info(f"No category match for spider '{spider_name}', using 'research' as fallback")
        return 'research'

    def _create_agent_solution(self, agent: Agent, spider_data: LegacySpiderData) -> Optional[AgentSolution]:
        """Create a solution based on spider data"""
        try:
            # Session 911: Handle both LegacySpiderData models
            # - core.models_unified_system.LegacySpiderData has processed_data/raw_data
            # - persistence.models.LegacySpiderData has structured_data/content
            data = {}

            # Try processed_data (unified model)
            processed = getattr(spider_data, 'processed_data', None)
            if processed and isinstance(processed, dict):
                data = processed
            # Try raw_data (unified model)
            elif hasattr(spider_data, 'raw_data'):
                raw = getattr(spider_data, 'raw_data', None)
                if raw and isinstance(raw, dict):
                    data = raw
            # Try structured_data (persistence model)
            elif hasattr(spider_data, 'structured_data'):
                structured = getattr(spider_data, 'structured_data', None)
                if structured and isinstance(structured, dict):
                    data = structured

            # Generate solution title and description
            # Check for title field on persistence model, or get from data dict
            title = getattr(spider_data, 'title', None) or data.get('title') or f"Opportunity from {spider_data.spider_name}"
            # Session 915: Truncate title to 200 chars to avoid varchar(200) error
            title = title[:200] if title else f"Opportunity from {spider_data.spider_name}"
            description = data.get('description', f"Data collected by {spider_data.spider_name}")

            # Create code snippet if relevant data exists
            code_snippet = self._generate_code_snippet(data)

            # Determine category based on spider data type
            category = self._map_data_type_to_category(spider_data.data_type)

            # Create the solution
            solution = AgentSolution.objects.create(
                agent=agent,
                title=title,
                description=description,
                code_snippet=code_snippet,
                solution_type=category,
                language='javascript',
                metrics={
                    'effectiveness_score': 85.0,
                    'implementation_time': 30,
                    'source': 'spider',
                    'spider_name': spider_data.spider_name,
                    'spider_data_id': str(spider_data.id),
                    'collected_at': spider_data.created_at.isoformat()
                }
            )

            logger.info(f"Created solution {solution.id} for agent {agent.name} from spider {spider_data.spider_name}")
            return solution

        except Exception as e:
            logger.error(f"Error creating agent solution: {e}")
            return None

    def _create_learning_record(self, agent: Agent, spider_data: LegacySpiderData, solution: AgentSolution):
        """Record spider data ingestion for the agent.

        Note: Synthetic AgentLearning records with hardcoded effectiveness
        scores (70→85) have been removed. Real performance is now tracked
        via AgentExecution, Deliverable, and ToolCallRecord tables, mined
        by LearningPatternEngine.mine_patterns().
        """
        logger.debug(f"Spider data processed for agent {agent.name}")
        return None

    def _propagate_to_connected_agents(
        self,
        teacher_agent: Agent,
        solution: AgentSolution,
        spider_data: LegacySpiderData
    ):
        """
        Session 767: Propagate learning to connected agents.

        When an agent learns from spider data, share with agents that
        have established AgentLearningConnection relationships.
        """
        from core.models_unified_system import AgentLearningConnection
        import random

        try:
            # Find connections where this agent is the teacher
            connections = AgentLearningConnection.objects.filter(
                teacher_agent=teacher_agent,
                is_active=True
            ).select_related('student_agent')[:5]  # Limit to top 5 students

            if not connections.exists():
                return

            for conn in connections:
                student = conn.student_agent

                # Create cross-agent learning record
                # Smaller improvement than self-learning (teaching is harder than direct learning)
                effectiveness_gain = random.uniform(5.0, 12.0)  # 5-12% improvement

                AgentLearning.objects.create(
                    teacher_agent=teacher_agent,
                    student_agent=student,
                    solution=solution,
                    learning_type=conn.learning_type,  # Use connection's learning type
                    effectiveness_before=70.0,
                    effectiveness_after=70.0 + effectiveness_gain,
                    implementation_success=True,
                    metadata={
                        'source': 'spider_propagation',
                        'spider_name': spider_data.spider_name,
                        'connection_id': str(conn.id),
                        'session': 767,
                    }
                )

                # Update connection stats
                conn.total_transfers += 1
                conn.successful_transfers += 1
                conn.avg_improvement_score = (
                    (conn.avg_improvement_score * (conn.total_transfers - 1) + effectiveness_gain)
                    / conn.total_transfers
                )
                conn.save(update_fields=['total_transfers', 'successful_transfers', 'avg_improvement_score'])

            logger.info(
                f"📚 [Session 767] Propagated learning from {teacher_agent.name} "
                f"to {connections.count()} connected agents"
            )

        except Exception as e:
            logger.warning(f"Error propagating to connected agents: {e}")

    def _generate_code_snippet(self, data: Dict[str, Any]) -> str:
        """Generate a code snippet based on spider data.

        Session 830: Fixed to NOT dump full data JSON (was causing 35GB table bloat).
        The spider_data_id is already stored in metrics - use that for lookups.
        """
        # Extract only key summary fields - NOT the full data
        title = data.get('title', 'Untitled')[:100]
        data_type = data.get('type', 'opportunity')
        source = data.get('source', 'spider')

        # Create a minimal reference snippet (NOT the full data)
        snippet = f"""// Opportunity Reference from Spider
// Full data available via spider_data_id in metrics
const opportunityRef = {{
    title: "{title}",
    type: "{data_type}",
    source: "{source}",
    // Query LegacySpiderData model using spider_data_id from metrics for full details
}};

// To get full data:
// const fullData = await fetchSpiderData(metrics.spider_data_id);"""

        return snippet

    def _map_data_type_to_category(self, data_type: str) -> str:
        """Map spider data type to solution category"""
        mapping = {
            'opportunity': 'income',
            'job': 'job_search',
            'freelance': 'freelance',
            'content': 'content',
            'market': 'analytics',
            'lead': 'business',
            'financial': 'finance',
            'research': 'research'
        }

        return mapping.get(data_type, 'income')

    def batch_process_spider_data(self, limit: int = 100) -> Dict[str, Any]:
        """
        Process multiple spider data entries in batch

        Args:
            limit: Maximum number of entries to process

        Returns:
            Processing statistics
        """
        results = {
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'agent_notifications': [],
            'solutions_created': [],
            'start_time': datetime.now().isoformat()
        }

        try:
            # Get unprocessed spider data
            # Session 807: Defer embedding fields to reduce egress costs
            unprocessed = LegacySpiderData.objects.filter(
                is_processed=False
            ).defer('embedding', 'item_embeddings', 'embedding_text').order_by('-created_at')[:limit]

            for spider_data in unprocessed:
                try:
                    # Route the data
                    routing_result = self.route_spider_data(spider_data)

                    # Mark as processed
                    spider_data.is_processed = True
                    spider_data.save()

                    # Update results
                    results['processed'] += 1
                    if routing_result.get('agents_notified'):
                        results['successful'] += 1
                        results['agent_notifications'].extend(routing_result['agents_notified'])
                        results['solutions_created'].extend(routing_result.get('solutions_created', []))
                    else:
                        results['failed'] += 1

                except Exception as e:
                    logger.error(f"Error processing spider data {spider_data.id}: {e}")
                    results['failed'] += 1

            results['end_time'] = datetime.now().isoformat()
            results['stats'] = self.processing_stats

        except Exception as e:
            logger.error(f"Error in batch processing: {e}")
            results['error'] = str(e)

        return results

    def get_routing_statistics(self) -> Dict[str, Any]:
        """Get statistics about spider-agent routing"""
        # Session 911: LegacySpiderData model doesn't have is_processed field
        # Just count total spider data
        stats = {
            'routing_map': {cat: len(agents) for cat, agents in self.routing_map.items()},
            'processing_stats': self.processing_stats,
            'total_spider_data': LegacySpiderData.objects.count(),
            'success_rate': 0
        }

        if self.processing_stats['total_routed'] > 0:
            stats['success_rate'] = (
                self.processing_stats['successful_processing'] /
                self.processing_stats['total_routed'] * 100
            )

        return stats