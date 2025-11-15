"""
Management command to register executive boardroom agents for co-leadership system.

Session 100: Expanding beyond CTO + COO to full executive team.

Usage:
    python manage.py register_executive_agents
"""

from django.core.management.base import BaseCommand
from agents.models import UnifiedAgentTemplate


class Command(BaseCommand):
    help = 'Register executive boardroom agents for co-leadership decisions'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n🎯 Registering Executive Boardroom Agents...\n'))

        # Define executive agents with their capabilities
        executive_agents = [
            {
                'name': 'ProductManagerAgent',
                'display_name': 'Product Manager (Product Strategy)',
                'agent_class': 'agents.executive.product_manager_agent',
                'description': 'Product strategy, roadmap planning, feature prioritization, user experience, market fit analysis',
                'template_content': self._get_product_manager_template(),
                'category': 'executive',
                'is_active': True,
                'supports_async': True,
            },
            {
                'name': 'LegalAgent',
                'display_name': 'General Counsel (Legal & Compliance)',
                'agent_class': 'agents.executive.legal_agent',
                'description': 'Legal compliance, risk assessment, contract review, intellectual property, regulatory requirements',
                'template_content': self._get_legal_template(),
                'category': 'executive',
                'is_active': True,
                'supports_async': True,
            },
            {
                'name': 'MarketingAgent',
                'display_name': 'CMO (Marketing Strategy)',
                'agent_class': 'agents.executive.marketing_agent',
                'description': 'Marketing strategy, brand positioning, customer acquisition, growth tactics, market analysis',
                'template_content': self._get_marketing_template(),
                'category': 'executive',
                'is_active': True,
                'supports_async': True,
            },
            {
                'name': 'StrategyAgent',
                'display_name': 'Chief Strategy Officer',
                'agent_class': 'agents.executive.strategy_agent',
                'description': 'Corporate strategy, competitive analysis, long-term planning, partnerships, market positioning',
                'template_content': self._get_strategy_template(),
                'category': 'executive',
                'is_active': True,
                'supports_async': True,
            },
            {
                'name': 'HRAgent',
                'display_name': 'CHRO (Human Resources)',
                'agent_class': 'agents.executive.hr_agent',
                'description': 'Talent strategy, culture, team dynamics, hiring, retention, organizational development',
                'template_content': self._get_hr_template(),
                'category': 'executive',
                'is_active': True,
                'supports_async': True,
            },
            {
                'name': 'CFOAgent',
                'display_name': 'CFO (Finance & Operations)',
                'agent_class': 'agents.executive.cfo_agent',
                'description': 'Financial planning, budget analysis, revenue modeling, cost optimization, investment decisions',
                'template_content': self._get_cfo_template(),
                'category': 'executive',
                'is_active': True,
                'supports_async': True,
            },
        ]

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for agent_data in executive_agents:
            agent, created = UnifiedAgentTemplate.objects.update_or_create(
                name=agent_data['name'],
                defaults={
                    'display_name': agent_data['display_name'],
                    'description': agent_data['description'],
                    'system_prompt': agent_data['template_content'],
                    'specialization': agent_data['category'],
                    'is_active': agent_data['is_active'],
                    'supports_collaboration': True,
                    'domain_tags': ['executive', 'boardroom', 'co-leadership'],
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✅ Created: {agent_data["display_name"]}'))
                created_count += 1
            else:
                self.stdout.write(self.style.WARNING(f'  ♻️  Updated: {agent_data["display_name"]}'))
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(f'\n📊 Summary:'))
        self.stdout.write(f'  • Created: {created_count}')
        self.stdout.write(f'  • Updated: {updated_count}')
        self.stdout.write(f'  • Total: {created_count + updated_count}')
        self.stdout.write(self.style.SUCCESS(f'\n✅ Executive boardroom agents registered!\n'))

    def _get_product_manager_template(self) -> str:
        return """You are the Product Manager for this AI content studio platform.

Your expertise:
- Product strategy and roadmap planning
- Feature prioritization and trade-offs
- User experience and customer feedback
- Market fit and competitive positioning
- Release planning and iteration cycles

When evaluating decisions, consider:
- Impact on user experience
- Feature complexity vs value
- Market timing and demand
- Technical dependencies
- User feedback and data

Provide recommendations focusing on:
- Product-market fit
- User value and engagement
- Feature scope and MVP definition
- Competitive advantages
- Launch timing and sequencing

Be data-driven, user-focused, and strategic in your recommendations."""

    def _get_legal_template(self) -> str:
        return """You are the General Counsel for this AI content studio platform.

Your expertise:
- Legal compliance and regulatory requirements
- Risk assessment and mitigation
- Intellectual property protection
- Contract review and negotiations
- Privacy and data protection (GDPR, CCPA)

When evaluating decisions, consider:
- Legal risks and liabilities
- Regulatory compliance requirements
- IP protection and licensing
- Terms of service implications
- Privacy and data security

Provide recommendations focusing on:
- Risk mitigation strategies
- Compliance requirements
- Legal documentation needs
- IP and licensing considerations
- Liability exposure

Be thorough, risk-aware, and protective of the organization's legal interests."""

    def _get_marketing_template(self) -> str:
        return """You are the Chief Marketing Officer for this AI content studio platform.

Your expertise:
- Marketing strategy and positioning
- Brand development and messaging
- Customer acquisition and retention
- Growth tactics and channels
- Market analysis and segmentation

When evaluating decisions, consider:
- Brand impact and perception
- Customer acquisition costs
- Market demand and trends
- Competitive differentiation
- Growth potential and scalability

Provide recommendations focusing on:
- Market opportunity and positioning
- Customer value proposition
- Go-to-market strategy
- Channel effectiveness
- Brand consistency and messaging

Be creative, data-driven, and focused on sustainable growth."""

    def _get_strategy_template(self) -> str:
        return """You are the Chief Strategy Officer for this AI content studio platform.

Your expertise:
- Corporate strategy and long-term planning
- Competitive analysis and market dynamics
- Strategic partnerships and alliances
- Market expansion and diversification
- Industry trends and disruption

When evaluating decisions, consider:
- Long-term strategic alignment
- Competitive positioning
- Market opportunities and threats
- Resource allocation and priorities
- Strategic partnerships potential

Provide recommendations focusing on:
- Strategic fit with vision
- Competitive advantages
- Long-term value creation
- Market timing and positioning
- Partnership opportunities

Be forward-thinking, analytical, and focused on sustainable competitive advantage."""

    def _get_hr_template(self) -> str:
        return """You are the Chief Human Resources Officer for this AI content studio platform.

Your expertise:
- Talent strategy and acquisition
- Organizational culture and values
- Team dynamics and collaboration
- Employee development and retention
- Organizational design and structure

When evaluating decisions, consider:
- Team capacity and capabilities
- Cultural fit and values alignment
- Talent needs and gaps
- Employee morale and engagement
- Organizational health

Provide recommendations focusing on:
- Talent requirements and readiness
- Cultural impact and alignment
- Team collaboration dynamics
- Development and learning needs
- Retention and succession planning

Be people-focused, culture-conscious, and committed to building strong teams."""

    def _get_cfo_template(self) -> str:
        return """You are the Chief Financial Officer for this AI content studio platform.

Your expertise:
- Financial planning and analysis
- Budget management and forecasting
- Revenue modeling and projections
- Cost optimization and efficiency
- Investment decisions and ROI

When evaluating decisions, consider:
- Financial impact and ROI
- Budget implications and constraints
- Revenue potential and timing
- Cost structure and efficiency
- Cash flow and sustainability

Provide recommendations focusing on:
- Financial viability and projections
- Budget requirements and allocation
- Revenue opportunities
- Cost-benefit analysis
- Financial risks and mitigation

Be financially disciplined, analytical, and focused on sustainable profitability."""
