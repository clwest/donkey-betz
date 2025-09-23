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
    SpiderData
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
        """Build mapping of spider categories to agent names"""
        return {
            # Job spiders -> Job-related agents
            'job': [
                'Job Application Automator',
                'Resume Optimizer AI',
                'Interview Prep Coach',
                'Career Path Strategist',
                'Job Market Analyst',
                'Salary Negotiation Expert',
                'Career Development Coach'
            ],

            # Freelance spiders -> Freelance agents
            'freelance': [
                'Freelance Hunter',
                'Gig Economy Optimizer',
                'Client Relationship Manager',
                'Project Bid Writer',
                'Freelance Proposal Generator',
                'Freelance Rate Calculator'
            ],

            # Market spiders -> Market analysis agents
            'market': [
                'Market Research Analyst',
                'Competitive Intelligence',
                'Trend Predictor',
                'Price Optimization Engine',
                'Business Growth Architect',
                'Revenue Stream Analyzer',
                'Market Opportunity Scout'
            ],

            # Content spiders -> Content agents
            'content': [
                'Content Generator',
                'Blog Post Writer',
                'Social Media Manager',
                'Email Marketing Automator',
                'Content Strategy Planner',
                'Creative Director AI',
                'SEO Content Optimizer',
                'Video Script Writer',
                'Podcast Script Generator'
            ],

            # Finance spiders -> Finance agents
            'finance': [
                'Investment Portfolio Manager',
                'Financial Advisor Bot',
                'Expense Tracker Pro',
                'Tax Optimization Planner',
                'Retirement Planning Expert',
                'Passive Income Architect',
                'Budget Optimization Expert',
                'Crypto Investment Advisor',
                'Stock Analysis Expert'
            ],

            # Tech spiders -> Tech agents
            'tech': [
                'Code Generator',
                'Tech Stack Advisor',
                'Bug Hunter',
                'Performance Optimizer',
                'AI Model Trainer',
                'Deep Learning Specialist',
                'Data Scientist Pro',
                'Workflow Automation Expert',
                'API Development Expert',
                'DevOps Automation Specialist'
            ],

            # Lead spiders -> Sales agents
            'lead': [
                'Lead Generation Engine',
                'Sales Funnel Optimizer',
                'Customer Acquisition Specialist',
                'Conversion Rate Optimizer',
                'Digital Marketing Strategist',
                'Growth Hacker Pro',
                'B2B Sales Accelerator',
                'Customer Success Manager'
            ],

            # Investment spiders -> Investment agents
            'investment': [
                'Stock Market Predictor',
                'Crypto Trading Bot',
                'Portfolio Rebalancer',
                'Risk Assessment Analyzer',
                'Investment Strategy Advisor',
                'Options Trading Strategist',
                'Real Estate Investment Scout',
                'Forex Trading Assistant'
            ],

            # Research spiders -> Research agents
            'research': [
                'Research Assistant Pro',
                'Data Analyst Expert',
                'Insight Generator',
                'Research Report Writer',
                'Patent Research Assistant',
                'Academic Research Compiler',
                'Literature Review Assistant',
                'Predictive Analytics Engine'
            ],

            # Social spiders -> Social media agents
            'social': [
                'Social Media Influencer',
                'Community Manager Pro',
                'Engagement Optimizer',
                'Viral Content Creator',
                'Brand Ambassador Bot',
                'Social Media Analytics Expert',
                'Influencer Outreach Specialist'
            ]
        }

    def route_spider_data(self, spider_data: SpiderData) -> Dict[str, Any]:
        """
        Route spider data to appropriate agents for processing

        Args:
            spider_data: SpiderData model instance

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

            # Get agents for this category
            agent_names = self.routing_map.get(category, [])

            # Route to each relevant agent
            for agent_name in agent_names:
                try:
                    agent = Agent.objects.filter(name__icontains=agent_name).first()

                    if agent:
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
                    logger.error(f"Error routing to agent {agent_name}: {e}")
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
            'tech': ['tech', 'technology', 'code', 'software'],
            'lead': ['lead', 'sales', 'customer', 'prospect'],
            'investment': ['investment', 'stock', 'crypto', 'trading'],
            'research': ['research', 'academic', 'paper', 'journal'],
            'social': ['social', 'media', 'twitter', 'facebook']
        }

        for category, keywords in category_keywords.items():
            if any(keyword in spider_name_lower for keyword in keywords):
                return category

        return None

    def _create_agent_solution(self, agent: Agent, spider_data: SpiderData) -> Optional[AgentSolution]:
        """Create a solution based on spider data"""
        try:
            # Parse spider data
            data = spider_data.raw_data if isinstance(spider_data.raw_data, dict) else {}

            # Generate solution title and description
            title = f"Opportunity: {data.get('title', 'New Opportunity from Spider')}"
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

    def _create_learning_record(self, agent: Agent, spider_data: SpiderData, solution: AgentSolution):
        """Create a learning record for the agent"""
        try:
            learning = AgentLearning.objects.create(
                teacher_agent=agent,
                student_agent=agent,  # Self-learning from spider data
                solution=solution,
                learning_type='spider_intelligence',
                effectiveness_before=70.0,
                effectiveness_after=85.0
            )
            logger.info(f"Created learning record for agent {agent.name}")
            return learning

        except Exception as e:
            logger.error(f"Error creating learning record: {e}")
            return None

    def _generate_code_snippet(self, data: Dict[str, Any]) -> str:
        """Generate a code snippet based on spider data"""
        # Create a JSON representation of the opportunity
        snippet = f"""// Opportunity Data from Spider
const opportunity = {json.dumps(data, indent=2)};

// Process the opportunity
function processOpportunity(data) {{
    // Analyze opportunity
    const score = analyzeOpportunity(data);

    // Take action if score is high
    if (score > 0.7) {{
        applyToOpportunity(data);
        trackApplication(data);
    }}

    return score;
}}

// Execute
const result = processOpportunity(opportunity);
console.log('Opportunity processed with score:', result);"""

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
            unprocessed = SpiderData.objects.filter(
                is_processed=False
            ).order_by('-created_at')[:limit]

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
        stats = {
            'routing_map': {cat: len(agents) for cat, agents in self.routing_map.items()},
            'processing_stats': self.processing_stats,
            'total_spider_data': SpiderData.objects.count(),
            'unprocessed_data': SpiderData.objects.filter(is_processed=False).count(),
            'processed_data': SpiderData.objects.filter(is_processed=True).count(),
            'success_rate': 0
        }

        if self.processing_stats['total_routed'] > 0:
            stats['success_rate'] = (
                self.processing_stats['successful_processing'] /
                self.processing_stats['total_routed'] * 100
            )

        return stats