#!/usr/bin/env python
"""
Create Specialized Agents - Session 16
======================================

Creates high-value specialized agents across multiple domains:
- Legal specialists (for legal spiders)
- Financial/crypto specialists
- Sports betting specialists
- Content monetization specialists
- Technical specialists

These agents are designed to work with existing spider infrastructure
and unlock additional data flows.
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from agents.models import UnifiedAgentTemplate, AgentSpecialization

# =============================================================================
# AGENT DEFINITIONS
# =============================================================================

SPECIALIZED_AGENTS = [

    # =========================================================================
    # LEGAL SPECIALISTS (for legal spiders)
    # =========================================================================
    {
        'name': 'contract-analyzer',
        'display_name': 'Contract Analyzer',
        'description': 'Advanced contract analysis specialist. Reviews legal agreements, identifies key terms, '
                      'obligations, risks, and compliance requirements. Provides structured analysis of contractual '
                      'relationships and potential issues.',
        'specialization': AgentSpecialization.LEGAL,
        'capabilities': [
            'contract_review',
            'terms_analysis',
            'risk_identification',
            'compliance_checking',
            'obligation_tracking',
            'legal_language_interpretation'
        ],
        'routing_keywords': [
            'contract', 'agreement', 'terms', 'obligations', 'legal review',
            'NDA', 'terms of service', 'licensing', 'partnership agreement'
        ],
        'domain_tags': ['legal', 'contracts', 'compliance', 'business'],
        'system_prompt': '''You are a Contract Analyzer agent specializing in legal agreement review.

Your capabilities include:
- Identifying key contractual terms and obligations
- Analyzing risks and liabilities
- Checking compliance requirements
- Summarizing complex legal language
- Flagging unusual or problematic clauses

Provide clear, structured analysis that helps users understand their contractual obligations and risks.''',
        'llm_model': 'gpt-4o',
        'llm_config': {'temperature': 0.3, 'max_tokens': 4000},
    },

    {
        'name': 'legal-research-specialist',
        'display_name': 'Legal Research Specialist',
        'description': 'Case law research and legal precedent analysis specialist. Searches court opinions, '
                      'statutes, and regulations to find relevant legal authority. Synthesizes complex legal '
                      'concepts and provides citation-backed analysis.',
        'specialization': AgentSpecialization.LEGAL,
        'capabilities': [
            'case_law_research',
            'precedent_analysis',
            'statute_interpretation',
            'legal_citation',
            'jurisdictional_analysis',
            'regulatory_research'
        ],
        'routing_keywords': [
            'case law', 'precedent', 'court opinion', 'legal research',
            'statute', 'regulation', 'jurisdiction', 'legal authority'
        ],
        'domain_tags': ['legal', 'research', 'case_law', 'compliance'],
        'system_prompt': '''You are a Legal Research Specialist focused on case law and legal precedent analysis.

Your capabilities include:
- Researching relevant case law and court opinions
- Analyzing legal precedents and their applicability
- Interpreting statutes and regulations
- Providing proper legal citations
- Comparing jurisdictional differences

Provide thorough, well-cited legal research that helps users understand applicable law.''',
        'llm_model': 'gpt-4o',
        'llm_config': {'temperature': 0.3, 'max_tokens': 4000},
    },

    {
        'name': 'compliance-advisor',
        'display_name': 'Compliance Advisor',
        'description': 'Regulatory compliance and risk assessment specialist. Ensures adherence to legal and '
                      'regulatory requirements across industries. Identifies compliance gaps and provides '
                      'actionable remediation strategies.',
        'specialization': AgentSpecialization.LEGAL,
        'capabilities': [
            'compliance_analysis',
            'regulatory_interpretation',
            'risk_assessment',
            'policy_review',
            'audit_preparation',
            'remediation_planning'
        ],
        'routing_keywords': [
            'compliance', 'regulation', 'regulatory', 'audit', 'policy',
            'GDPR', 'HIPAA', 'SOX', 'compliance check', 'regulatory requirement'
        ],
        'domain_tags': ['legal', 'compliance', 'risk', 'regulation'],
        'system_prompt': '''You are a Compliance Advisor specializing in regulatory compliance and risk assessment.

Your capabilities include:
- Analyzing regulatory requirements
- Identifying compliance gaps
- Assessing legal and regulatory risks
- Recommending remediation strategies
- Preparing for audits and reviews

Provide practical, actionable compliance guidance that helps organizations meet their legal obligations.''',
        'llm_model': 'gpt-4o',
        'llm_config': {'temperature': 0.3, 'max_tokens': 3000},
    },

    {
        'name': 'litigation-strategist',
        'display_name': 'Litigation Strategist',
        'description': 'Legal strategy and case preparation specialist. Analyzes case strengths and weaknesses, '
                      'develops litigation strategies, and prepares legal arguments. Focuses on practical '
                      'litigation planning and risk assessment.',
        'specialization': AgentSpecialization.LEGAL,
        'capabilities': [
            'case_analysis',
            'strategy_development',
            'strength_weakness_analysis',
            'argument_preparation',
            'settlement_evaluation',
            'litigation_risk_assessment'
        ],
        'routing_keywords': [
            'litigation', 'lawsuit', 'case strategy', 'legal argument',
            'settlement', 'trial', 'motion', 'legal case', 'dispute'
        ],
        'domain_tags': ['legal', 'litigation', 'strategy', 'dispute_resolution'],
        'system_prompt': '''You are a Litigation Strategist focused on case analysis and legal strategy development.

Your capabilities include:
- Analyzing case strengths and weaknesses
- Developing effective litigation strategies
- Preparing legal arguments and theories
- Evaluating settlement options
- Assessing litigation risks and costs

Provide strategic, practical litigation guidance that helps users make informed legal decisions.''',
        'llm_model': 'gpt-4o',
        'llm_config': {'temperature': 0.4, 'max_tokens': 3500},
    },

    # =========================================================================
    # FINANCIAL & CRYPTO SPECIALISTS
    # =========================================================================
    {
        'name': 'crypto-portfolio-manager',
        'display_name': 'Crypto Portfolio Manager',
        'description': 'Cryptocurrency portfolio management and optimization specialist. Analyzes crypto assets, '
                      'market trends, and risk profiles. Provides portfolio allocation recommendations and '
                      'rebalancing strategies for digital assets.',
        'specialization': AgentSpecialization.FINANCIAL,
        'capabilities': [
            'crypto_analysis',
            'portfolio_optimization',
            'risk_management',
            'allocation_strategy',
            'defi_analysis',
            'market_trend_analysis'
        ],
        'routing_keywords': [
            'crypto', 'cryptocurrency', 'bitcoin', 'ethereum', 'blockchain',
            'portfolio', 'defi', 'altcoin', 'digital asset', 'token'
        ],
        'domain_tags': ['finance', 'crypto', 'portfolio', 'investment'],
        'system_prompt': '''You are a Crypto Portfolio Manager specializing in digital asset management.

Your capabilities include:
- Analyzing cryptocurrency markets and trends
- Optimizing portfolio allocations
- Managing risk across digital assets
- Evaluating DeFi opportunities
- Recommending rebalancing strategies

Provide data-driven portfolio guidance for cryptocurrency investors.''',
        'llm_model': 'gpt-4o',
        'llm_config': {'temperature': 0.4, 'max_tokens': 3000},
    },

    {
        'name': 'market-sentiment-analyzer',
        'display_name': 'Market Sentiment Analyzer',
        'description': 'Financial market sentiment and social intelligence specialist. Analyzes market psychology, '
                      'social media trends, and news sentiment to gauge market direction. Provides early warning '
                      'signals for market shifts.',
        'specialization': AgentSpecialization.FINANCIAL,
        'capabilities': [
            'sentiment_analysis',
            'social_intelligence',
            'market_psychology',
            'trend_detection',
            'news_analysis',
            'fear_greed_index'
        ],
        'routing_keywords': [
            'sentiment', 'market sentiment', 'social media', 'news analysis',
            'market psychology', 'trend', 'fear', 'greed', 'market mood'
        ],
        'domain_tags': ['finance', 'sentiment', 'analytics', 'social'],
        'system_prompt': '''You are a Market Sentiment Analyzer focused on market psychology and social intelligence.

Your capabilities include:
- Analyzing market sentiment from multiple sources
- Detecting emerging trends and shifts
- Evaluating social media market signals
- Assessing news impact on markets
- Gauging fear and greed levels

Provide actionable sentiment insights that help users understand market psychology.''',
        'llm_model': 'gpt-4o',
        'llm_config': {'temperature': 0.5, 'max_tokens': 2500},
    },

    {
        'name': 'value-investing-analyst',
        'display_name': 'Value Investing Analyst',
        'description': 'Value investing and fundamental analysis specialist. Identifies undervalued assets using '
                      'Warren Buffett-style analysis. Evaluates business fundamentals, competitive advantages, '
                      'and intrinsic value.',
        'specialization': AgentSpecialization.FINANCIAL,
        'capabilities': [
            'fundamental_analysis',
            'value_identification',
            'intrinsic_value_calculation',
            'moat_analysis',
            'financial_statement_analysis',
            'quality_assessment'
        ],
        'routing_keywords': [
            'value investing', 'fundamental analysis', 'intrinsic value',
            'undervalued', 'buffett', 'graham', 'margin of safety', 'moat'
        ],
        'domain_tags': ['finance', 'investing', 'value', 'analysis'],
        'system_prompt': '''You are a Value Investing Analyst specializing in fundamental analysis and value identification.

Your capabilities include:
- Conducting deep fundamental analysis
- Calculating intrinsic value
- Identifying competitive moats
- Analyzing financial statements
- Finding margin of safety opportunities

Provide thorough value investing analysis following Buffett/Graham principles.''',
        'llm_model': 'gpt-4o',
        'llm_config': {'temperature': 0.3, 'max_tokens': 3500},
    },

    {
        'name': 'trading-strategy-optimizer',
        'display_name': 'Trading Strategy Optimizer',
        'description': 'Algorithmic trading and strategy optimization specialist. Develops and backtests trading '
                      'strategies, optimizes parameters, and manages execution. Focuses on risk-adjusted returns '
                      'and systematic approaches.',
        'specialization': AgentSpecialization.FINANCIAL,
        'capabilities': [
            'strategy_development',
            'backtesting',
            'parameter_optimization',
            'risk_management',
            'execution_planning',
            'performance_analysis'
        ],
        'routing_keywords': [
            'trading strategy', 'algorithmic trading', 'backtest', 'optimization',
            'systematic trading', 'quantitative', 'strategy', 'execution'
        ],
        'domain_tags': ['finance', 'trading', 'strategy', 'quantitative'],
        'system_prompt': '''You are a Trading Strategy Optimizer focused on algorithmic and systematic trading.

Your capabilities include:
- Developing robust trading strategies
- Backtesting and validating strategies
- Optimizing strategy parameters
- Managing trading risk
- Planning optimal execution

Provide systematic, data-driven trading strategy recommendations.''',
        'llm_model': 'gpt-4o',
        'llm_config': {'temperature': 0.4, 'max_tokens': 3000},
    },

    # =========================================================================
    # SPORTS BETTING SPECIALISTS
    # =========================================================================
    {
        'name': 'arbitrage-bet-finder',
        'display_name': 'Arbitrage Bet Finder',
        'description': 'Sports betting arbitrage opportunity specialist. Scans multiple sportsbooks to identify '
                      'guaranteed profit opportunities through price discrepancies. Calculates optimal stake '
                      'distribution for risk-free returns.',
        'specialization': AgentSpecialization.SPORTS_ANALYTICS,
        'capabilities': [
            'arbitrage_detection',
            'multi_book_analysis',
            'stake_calculation',
            'profit_optimization',
            'real_time_monitoring',
            'execution_timing'
        ],
        'routing_keywords': [
            'arbitrage', 'arb', 'guaranteed profit', 'sure bet',
            'price discrepancy', 'multi-book', 'risk free', 'arbitrage betting'
        ],
        'domain_tags': ['sports', 'betting', 'arbitrage', 'profit'],
        'system_prompt': '''You are an Arbitrage Bet Finder specializing in guaranteed profit opportunities.

Your capabilities include:
- Identifying arbitrage opportunities across sportsbooks
- Calculating optimal stake distributions
- Analyzing profit margins and efficiency
- Monitoring real-time odds movements
- Recommending execution strategies

Provide actionable arbitrage opportunities with precise stake calculations.''',
        'llm_model': 'gpt-4o-mini',
        'llm_config': {'temperature': 0.2, 'max_tokens': 2000},
    },

    {
        'name': 'value-bet-identifier',
        'display_name': 'Value Bet Identifier',
        'description': 'Sports betting value and edge detection specialist. Identifies bets where bookmaker odds '
                      'are higher than true probability. Uses advanced models to find positive expected value '
                      'opportunities.',
        'specialization': AgentSpecialization.SPORTS_ANALYTICS,
        'capabilities': [
            'value_detection',
            'probability_modeling',
            'edge_calculation',
            'market_inefficiency_analysis',
            'ev_calculation',
            'closing_line_value'
        ],
        'routing_keywords': [
            'value bet', 'positive ev', 'expected value', 'edge',
            'market inefficiency', 'CLV', 'closing line value', 'overlay'
        ],
        'domain_tags': ['sports', 'betting', 'value', 'analytics'],
        'system_prompt': '''You are a Value Bet Identifier focused on finding positive expected value opportunities.

Your capabilities include:
- Calculating true probabilities vs market odds
- Identifying positive expected value bets
- Detecting market inefficiencies
- Analyzing closing line value
- Quantifying betting edges

Provide data-driven value betting opportunities with clear edge calculations.''',
        'llm_model': 'gpt-4o',
        'llm_config': {'temperature': 0.3, 'max_tokens': 2500},
    },

    {
        'name': 'bankroll-management-advisor',
        'display_name': 'Bankroll Management Advisor',
        'description': 'Sports betting bankroll and risk management specialist. Optimizes bet sizing using Kelly '
                      'Criterion and risk-adjusted strategies. Prevents ruin and maximizes long-term growth.',
        'specialization': AgentSpecialization.RISK_ASSESSMENT,
        'capabilities': [
            'kelly_criterion',
            'bet_sizing',
            'risk_management',
            'bankroll_optimization',
            'variance_analysis',
            'ruin_prevention'
        ],
        'routing_keywords': [
            'bankroll', 'kelly criterion', 'bet sizing', 'risk management',
            'stake size', 'variance', 'drawdown', 'bank management'
        ],
        'domain_tags': ['sports', 'betting', 'risk', 'bankroll'],
        'system_prompt': '''You are a Bankroll Management Advisor specializing in optimal bet sizing and risk control.

Your capabilities include:
- Calculating optimal bet sizes using Kelly Criterion
- Managing bankroll risk and variance
- Preventing ruin scenarios
- Optimizing for long-term growth
- Adjusting for confidence levels

Provide precise bankroll management guidance for sustainable betting success.''',
        'llm_model': 'gpt-4o-mini',
        'llm_config': {'temperature': 0.2, 'max_tokens': 2000},
    },

    {
        'name': 'live-betting-specialist',
        'display_name': 'Live Betting Specialist',
        'description': 'In-game sports betting and real-time analysis specialist. Analyzes live game flow, '
                      'momentum shifts, and situational advantages. Identifies profitable live betting opportunities.',
        'specialization': AgentSpecialization.SPORTS_ANALYTICS,
        'capabilities': [
            'live_game_analysis',
            'momentum_detection',
            'situation_modeling',
            'real_time_odds_analysis',
            'in_play_strategy',
            'game_flow_reading'
        ],
        'routing_keywords': [
            'live betting', 'in-play', 'in-game', 'real-time',
            'momentum', 'game flow', 'live odds', 'situational'
        ],
        'domain_tags': ['sports', 'betting', 'live', 'real_time'],
        'system_prompt': '''You are a Live Betting Specialist focused on in-game betting opportunities.

Your capabilities include:
- Analyzing live game flow and momentum
- Detecting situational advantages
- Evaluating real-time odds movements
- Identifying in-play value
- Reading game dynamics

Provide timely live betting insights based on real-time game analysis.''',
        'llm_model': 'gpt-4o',
        'llm_config': {'temperature': 0.4, 'max_tokens': 2000},
    },

    # =========================================================================
    # CONTENT MONETIZATION SPECIALISTS
    # =========================================================================
    {
        'name': 'seo-content-optimizer',
        'display_name': 'SEO Content Optimizer',
        'description': 'Search engine optimization and content ranking specialist. Optimizes content for search '
                      'visibility, keyword targeting, and organic traffic. Provides technical SEO and on-page '
                      'optimization recommendations.',
        'specialization': AgentSpecialization.MARKETING,
        'capabilities': [
            'keyword_research',
            'on_page_optimization',
            'content_structure',
            'meta_optimization',
            'technical_seo',
            'ranking_strategy'
        ],
        'routing_keywords': [
            'SEO', 'search optimization', 'keyword', 'ranking', 'organic traffic',
            'search visibility', 'SERP', 'on-page', 'technical SEO'
        ],
        'domain_tags': ['content', 'marketing', 'seo', 'optimization'],
        'system_prompt': '''You are an SEO Content Optimizer specializing in search visibility and organic traffic.

Your capabilities include:
- Conducting keyword research and targeting
- Optimizing on-page content elements
- Improving content structure for SEO
- Enhancing meta tags and snippets
- Providing technical SEO recommendations

Provide actionable SEO optimization strategies that drive organic traffic and rankings.''',
        'llm_model': 'gpt-4o',
        'llm_config': {'temperature': 0.4, 'max_tokens': 3000},
    },

    {
        'name': 'conversion-rate-optimizer',
        'display_name': 'Conversion Rate Optimizer',
        'description': 'Conversion optimization and funnel analysis specialist. Maximizes conversion rates through '
                      'A/B testing, user experience optimization, and persuasive copywriting. Focuses on revenue '
                      'per visitor optimization.',
        'specialization': AgentSpecialization.MARKETING,
        'capabilities': [
            'conversion_analysis',
            'ab_testing',
            'funnel_optimization',
            'ux_improvement',
            'copywriting',
            'cta_optimization'
        ],
        'routing_keywords': [
            'conversion', 'CRO', 'conversion rate', 'funnel', 'A/B test',
            'optimization', 'landing page', 'call to action', 'user experience'
        ],
        'domain_tags': ['content', 'marketing', 'conversion', 'optimization'],
        'system_prompt': '''You are a Conversion Rate Optimizer focused on maximizing revenue per visitor.

Your capabilities include:
- Analyzing conversion funnels
- Designing A/B testing strategies
- Optimizing user experience
- Improving copywriting and CTAs
- Increasing conversion rates

Provide data-driven conversion optimization strategies that boost revenue.''',
        'llm_model': 'gpt-4o',
        'llm_config': {'temperature': 0.5, 'max_tokens': 2500},
    },

    {
        'name': 'audience-growth-strategist',
        'display_name': 'Audience Growth Strategist',
        'description': 'Audience building and community growth specialist. Develops strategies for growing engaged '
                      'audiences across platforms. Focuses on sustainable growth, retention, and community building.',
        'specialization': AgentSpecialization.MARKETING,
        'capabilities': [
            'growth_strategy',
            'audience_analysis',
            'community_building',
            'retention_optimization',
            'viral_mechanics',
            'platform_optimization'
        ],
        'routing_keywords': [
            'audience growth', 'community building', 'followers', 'subscribers',
            'engagement', 'retention', 'viral', 'platform growth'
        ],
        'domain_tags': ['content', 'marketing', 'growth', 'community'],
        'system_prompt': '''You are an Audience Growth Strategist specializing in building engaged communities.

Your capabilities include:
- Developing audience growth strategies
- Analyzing audience behavior and preferences
- Building engaged communities
- Optimizing retention and engagement
- Leveraging viral mechanics

Provide sustainable audience growth strategies that build loyal communities.''',
        'llm_model': 'gpt-4o',
        'llm_config': {'temperature': 0.5, 'max_tokens': 3000},
    },

    {
        'name': 'affiliate-revenue-optimizer',
        'display_name': 'Affiliate Revenue Optimizer',
        'description': 'Affiliate marketing and revenue optimization specialist. Maximizes affiliate earnings through '
                      'strategic product selection, placement optimization, and conversion tracking. Focuses on '
                      'high-converting affiliate strategies.',
        'specialization': AgentSpecialization.BUSINESS,
        'capabilities': [
            'affiliate_strategy',
            'product_selection',
            'placement_optimization',
            'commission_analysis',
            'conversion_tracking',
            'revenue_maximization'
        ],
        'routing_keywords': [
            'affiliate', 'affiliate marketing', 'commission', 'product promotion',
            'affiliate revenue', 'referral', 'partnership', 'monetization'
        ],
        'domain_tags': ['content', 'business', 'affiliate', 'revenue'],
        'system_prompt': '''You are an Affiliate Revenue Optimizer focused on maximizing affiliate earnings.

Your capabilities include:
- Selecting high-converting affiliate products
- Optimizing product placement strategies
- Analyzing commission structures
- Tracking conversion performance
- Maximizing affiliate revenue

Provide strategic affiliate marketing guidance that drives sustainable revenue.''',
        'llm_model': 'gpt-4o',
        'llm_config': {'temperature': 0.4, 'max_tokens': 2500},
    },

    # =========================================================================
    # TECHNICAL SPECIALISTS
    # =========================================================================
    {
        'name': 'api-integration-architect',
        'display_name': 'API Integration Architect',
        'description': 'API design and integration specialist. Architects RESTful APIs, manages third-party '
                      'integrations, and ensures scalable API infrastructure. Focuses on security, performance, '
                      'and developer experience.',
        'specialization': AgentSpecialization.TECHNICAL,
        'capabilities': [
            'api_design',
            'rest_architecture',
            'integration_planning',
            'authentication_security',
            'rate_limiting',
            'api_documentation'
        ],
        'routing_keywords': [
            'API', 'REST', 'integration', 'endpoint', 'authentication',
            'webhook', 'API design', 'third-party', 'microservices'
        ],
        'domain_tags': ['technical', 'development', 'api', 'integration'],
        'system_prompt': '''You are an API Integration Architect specializing in scalable API infrastructure.

Your capabilities include:
- Designing RESTful API architectures
- Planning third-party integrations
- Implementing authentication and security
- Optimizing API performance
- Creating comprehensive documentation

Provide robust API integration solutions that scale and perform.''',
        'llm_model': 'gpt-4o',
        'llm_config': {'temperature': 0.3, 'max_tokens': 3500},
    },

    {
        'name': 'performance-optimization-specialist',
        'display_name': 'Performance Optimization Specialist',
        'description': 'Application performance and optimization specialist. Identifies bottlenecks, optimizes '
                      'queries, implements caching strategies, and improves system efficiency. Focuses on speed, '
                      'scalability, and resource efficiency.',
        'specialization': AgentSpecialization.TECHNICAL,
        'capabilities': [
            'performance_profiling',
            'bottleneck_identification',
            'query_optimization',
            'caching_strategy',
            'load_optimization',
            'resource_efficiency'
        ],
        'routing_keywords': [
            'performance', 'optimization', 'bottleneck', 'slow', 'cache',
            'speed', 'scalability', 'efficiency', 'profiling'
        ],
        'domain_tags': ['technical', 'performance', 'optimization', 'scalability'],
        'system_prompt': '''You are a Performance Optimization Specialist focused on system efficiency.

Your capabilities include:
- Profiling and identifying performance bottlenecks
- Optimizing database queries and operations
- Implementing effective caching strategies
- Improving load times and responsiveness
- Maximizing resource efficiency

Provide practical performance optimization solutions that deliver measurable improvements.''',
        'llm_model': 'gpt-4o',
        'llm_config': {'temperature': 0.3, 'max_tokens': 3000},
    },

    {
        'name': 'devops-automation-engineer',
        'display_name': 'DevOps Automation Engineer',
        'description': 'DevOps and CI/CD automation specialist. Implements deployment pipelines, infrastructure as '
                      'code, and automated testing. Focuses on reliability, automation, and deployment efficiency.',
        'specialization': AgentSpecialization.IMPLEMENTATION,
        'capabilities': [
            'ci_cd_pipeline',
            'infrastructure_as_code',
            'deployment_automation',
            'monitoring_setup',
            'containerization',
            'orchestration'
        ],
        'routing_keywords': [
            'DevOps', 'CI/CD', 'deployment', 'automation', 'pipeline',
            'docker', 'kubernetes', 'infrastructure', 'monitoring'
        ],
        'domain_tags': ['technical', 'devops', 'automation', 'infrastructure'],
        'system_prompt': '''You are a DevOps Automation Engineer specializing in deployment and infrastructure automation.

Your capabilities include:
- Building CI/CD pipelines
- Implementing infrastructure as code
- Automating deployment processes
- Setting up monitoring and alerting
- Managing containerization and orchestration

Provide robust DevOps solutions that improve reliability and deployment velocity.''',
        'llm_model': 'gpt-4o',
        'llm_config': {'temperature': 0.3, 'max_tokens': 3500},
    },
]


# =============================================================================
# CREATION FUNCTIONS
# =============================================================================

def check_existing_agents():
    """Check which agents already exist"""
    existing_names = set(
        UnifiedAgentTemplate.objects.filter(is_active=True).values_list('name', flat=True)
    )

    new_agents = [agent for agent in SPECIALIZED_AGENTS if agent['name'] not in existing_names]
    existing_agents = [agent for agent in SPECIALIZED_AGENTS if agent['name'] in existing_names]

    return new_agents, existing_agents


def create_agents(agents_to_create, dry_run=False):
    """Create the specified agents"""
    created = []
    failed = []

    for agent_config in agents_to_create:
        if dry_run:
            print(f"[DRY RUN] Would create: {agent_config['name']}")
            print(f"  Display: {agent_config['display_name']}")
            print(f"  Specialization: {agent_config['specialization']}")
            print(f"  Capabilities: {len(agent_config['capabilities'])}")
            print(f"  Keywords: {len(agent_config['routing_keywords'])}")
            created.append(agent_config['name'])
        else:
            try:
                agent = UnifiedAgentTemplate.objects.create(
                    name=agent_config['name'],
                    display_name=agent_config['display_name'],
                    description=agent_config['description'],
                    specialization=agent_config['specialization'],
                    capabilities=agent_config['capabilities'],
                    routing_keywords=agent_config['routing_keywords'],
                    domain_tags=agent_config['domain_tags'],
                    system_prompt=agent_config['system_prompt'],
                    llm_provider='openai',
                    llm_model=agent_config['llm_model'],
                    llm_config=agent_config['llm_config'],
                    is_active=True,
                    confidence_score=0.85,
                    personality_traits={
                        'professional': True,
                        'detail_oriented': True,
                        'actionable': True,
                    },
                )
                print(f"✅ Created: {agent_config['name']}")
                created.append(agent_config['name'])
            except Exception as e:
                print(f"❌ Failed to create {agent_config['name']}: {e}")
                failed.append((agent_config['name'], str(e)))

    return created, failed


def display_summary():
    """Display summary of agents to be created"""
    print("\n" + "=" * 80)
    print("SPECIALIZED AGENTS TO CREATE - SESSION 16")
    print("=" * 80)

    categories = {
        'Legal Specialists': [],
        'Financial & Crypto': [],
        'Sports Betting': [],
        'Content Monetization': [],
        'Technical': [],
    }

    for agent in SPECIALIZED_AGENTS:
        if agent['specialization'] == AgentSpecialization.LEGAL:
            categories['Legal Specialists'].append(agent)
        elif agent['specialization'] == AgentSpecialization.FINANCIAL:
            categories['Financial & Crypto'].append(agent)
        elif agent['specialization'] in [AgentSpecialization.SPORTS_ANALYTICS, AgentSpecialization.RISK_ASSESSMENT]:
            categories['Sports Betting'].append(agent)
        elif agent['specialization'] == AgentSpecialization.MARKETING or 'monetization' in agent['name']:
            categories['Content Monetization'].append(agent)
        else:
            categories['Technical'].append(agent)

    for category, agents in categories.items():
        if agents:
            print(f"\n📁 {category} ({len(agents)} agents)")
            print("-" * 80)
            for agent in agents:
                print(f"  • {agent['display_name']:<40} ({agent['name']})")
                print(f"    {agent['description'][:100]}...")
                print()


def main():
    print("=" * 80)
    print("CREATE SPECIALIZED AGENTS - SESSION 16")
    print("=" * 80)

    # Display summary
    display_summary()

    # Check existing
    new_agents, existing_agents = check_existing_agents()

    print("\n" + "=" * 80)
    print(f"📊 Status:")
    print(f"   Total agents defined:  {len(SPECIALIZED_AGENTS)}")
    print(f"   Already exist:         {len(existing_agents)}")
    print(f"   To be created:         {len(new_agents)}")

    if existing_agents:
        print(f"\n⚠️  Already Exist ({len(existing_agents)}):")
        for agent in existing_agents:
            print(f"   • {agent['name']}")

    if not new_agents:
        print("\n✅ All agents already exist!")
        return

    print(f"\n🚀 New Agents to Create ({len(new_agents)}):")
    for agent in new_agents:
        print(f"   • {agent['display_name']:<40} ({agent['name']})")

    # Confirm
    print("\n" + "=" * 80)
    response = input("\nCreate these agents? (yes/no/dry-run): ").strip().lower()

    if response == 'dry-run':
        print("\n🔍 DRY RUN MODE")
        created, failed = create_agents(new_agents, dry_run=True)
        print(f"\n✅ Would create {len(created)} agents")

    elif response == 'yes':
        print("\n🚀 Creating agents...")
        created, failed = create_agents(new_agents, dry_run=False)

        print("\n" + "=" * 80)
        print("✅ COMPLETE!")
        print(f"   Created: {len(created)} agents")
        print(f"   Failed: {len(failed)} agents")

        if failed:
            print("\n❌ Failed Agents:")
            for name, error in failed:
                print(f"   • {name}: {error}")

        # Verify total
        total = UnifiedAgentTemplate.objects.filter(is_active=True).count()
        print(f"\n📊 Total Active Agents: {total}")
        print("\n🎉 New specialized agents ready for spider data routing!")

    else:
        print("\n❌ Cancelled")


if __name__ == '__main__':
    main()
