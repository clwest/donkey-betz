"""
ConceptForge Domain Labs Configuration
======================================

Session 863: Config-first approach to domain labs.

Labs are NOT database tables - they're configuration that can be
adjusted without migrations. The DB only stores run outputs.

Each lab defines:
- Required agents for each stage
- Required persona agents for advisory input
- Tags that route content to this lab
- Quality gate overrides (if any)
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class StageConfig:
    """Configuration for a single pipeline stage."""
    agent_name: str  # Core agent that executes this stage
    persona_advisors: List[str] = field(default_factory=list)  # Persona agents for input
    advice_type: str = 'content_strategy'  # Type of advice to request
    timeout_seconds: int = 300  # Stage timeout
    optional: bool = False  # If True, pipeline continues even if stage fails


@dataclass
class LabConfig:
    """Configuration for a domain lab."""
    name: str
    description: str
    icon: str

    # Tags that route content to this lab
    routing_tags: List[str]

    # Stage configurations
    stages: Dict[str, StageConfig]

    # Quality gate (can be overridden per lab)
    min_quality_score: float = 0.80

    # Whether this lab is currently active
    is_active: bool = True


# =============================================================================
# DOMAIN LAB DEFINITIONS
# =============================================================================

DOMAIN_LABS: Dict[str, LabConfig] = {

    'legal': LabConfig(
        name='LegalLab',
        description='Legal technology, policy, and regulatory analysis',
        icon='⚖️',
        routing_tags=['legal', 'legal-tech', 'policy', 'regulation', 'compliance', 'family-law', 'court'],
        stages={
            'research': StageConfig(
                agent_name='ResearchAgent',
                persona_advisors=['Legal Document Reviewer', 'Trend Analysis Expert'],
                advice_type='trend_analysis',
            ),
            'debate': StageConfig(
                agent_name='ContentStudioDebateAgent',
                persona_advisors=[],  # Uses legendary advisors from panel
                advice_type='content_strategy',
            ),
            'feasibility': StageConfig(
                agent_name='SystemsArchitectAgent',
                persona_advisors=['AI Model Trainer', 'Data Scientist Pro'],
                advice_type='content_strategy',
            ),
            'risk': StageConfig(
                agent_name='RiskAnalysisAgent',
                persona_advisors=['Legal Document Reviewer', 'Contract Analyzer', 'Regulatory Compliance'],
                advice_type='quality_review',
            ),
            'market': StageConfig(
                agent_name='MarketIntelligenceAgent',
                persona_advisors=['Business Model Designer', 'Market Research Analyst'],
                advice_type='marketing_angle',
            ),
            'synthesis': StageConfig(
                agent_name='ThinkingAgent',
                persona_advisors=[],
                advice_type='content_strategy',
            ),
        },
    ),

    'market': LabConfig(
        name='MarketLab',
        description='Financial markets, investment, and trading analysis',
        icon='📈',
        routing_tags=['market', 'stocks', 'trading', 'investment', 'finance', 'crypto', 'defi'],
        stages={
            'research': StageConfig(
                agent_name='ResearchAgent',
                persona_advisors=['Market Research Analyst', 'Data Scientist Pro'],
                advice_type='trend_analysis',
            ),
            'debate': StageConfig(
                agent_name='ContentStudioDebateAgent',
                persona_advisors=[],
                advice_type='content_strategy',
            ),
            'feasibility': StageConfig(
                agent_name='SystemsArchitectAgent',
                persona_advisors=['Investment Portfolio Manager', 'Data Pipeline Builder'],
                advice_type='content_strategy',
            ),
            'risk': StageConfig(
                agent_name='RiskAnalysisAgent',
                persona_advisors=['Personal Finance Manager', 'Tax Strategy Advisor'],
                advice_type='quality_review',
            ),
            'market': StageConfig(
                agent_name='MarketIntelligenceAgent',
                persona_advisors=['Growth Hacker Pro', 'Business Model Designer'],
                advice_type='marketing_angle',
            ),
            'synthesis': StageConfig(
                agent_name='ThinkingAgent',
                persona_advisors=[],
                advice_type='content_strategy',
            ),
        },
    ),

    'tech': LabConfig(
        name='TechLab',
        description='Technology, AI/ML, and product development analysis',
        icon='🔧',
        routing_tags=['tech', 'ai', 'ml', 'product', 'software', 'saas', 'api', 'infrastructure'],
        stages={
            'research': StageConfig(
                agent_name='ResearchAgent',
                persona_advisors=['AI Model Trainer', 'Trend Analysis Expert'],
                advice_type='trend_analysis',
            ),
            'debate': StageConfig(
                agent_name='ContentStudioDebateAgent',
                persona_advisors=[],
                advice_type='content_strategy',
            ),
            'feasibility': StageConfig(
                agent_name='SystemsArchitectAgent',
                persona_advisors=['AI Model Trainer', 'Data Pipeline Builder', 'Predictive Analytics Engine'],
                advice_type='content_strategy',
            ),
            'risk': StageConfig(
                agent_name='RiskAnalysisAgent',
                persona_advisors=['AI Model Trainer', 'Data Scientist Pro'],
                advice_type='quality_review',
            ),
            'market': StageConfig(
                agent_name='MarketIntelligenceAgent',
                persona_advisors=['Growth Hacker Pro', 'Digital Marketing Strategist'],
                advice_type='marketing_angle',
            ),
            'synthesis': StageConfig(
                agent_name='ThinkingAgent',
                persona_advisors=[],
                advice_type='content_strategy',
            ),
        },
    ),

    'content': LabConfig(
        name='ContentLab',
        description='Content strategy, marketing, and media analysis',
        icon='📝',
        routing_tags=['content', 'marketing', 'media', 'social', 'blog', 'video', 'podcast'],
        stages={
            'research': StageConfig(
                agent_name='ResearchAgent',
                persona_advisors=['Content Strategy Planner', 'SEO Content Optimizer'],
                advice_type='trend_analysis',
            ),
            'debate': StageConfig(
                agent_name='ContentStudioDebateAgent',
                persona_advisors=[],
                advice_type='content_strategy',
            ),
            'feasibility': StageConfig(
                agent_name='SystemsArchitectAgent',
                persona_advisors=['Content Writer Pro', 'Video Script Writer'],
                advice_type='content_strategy',
            ),
            'risk': StageConfig(
                agent_name='RiskAnalysisAgent',
                persona_advisors=['Content Strategy Planner', 'Audience Engagement Specialist'],
                advice_type='quality_review',
            ),
            'market': StageConfig(
                agent_name='MarketIntelligenceAgent',
                persona_advisors=['Digital Marketing Strategist', 'Email Campaign Manager'],
                advice_type='marketing_angle',
            ),
            'synthesis': StageConfig(
                agent_name='ThinkingAgent',
                persona_advisors=[],
                advice_type='content_strategy',
            ),
        },
    ),

    'startup': LabConfig(
        name='StartupLab',
        description='Startup strategy, fundraising, and scaling analysis',
        icon='🚀',
        routing_tags=['startup', 'funding', 'venture', 'scale', 'growth', 'pitch', 'mvp'],
        stages={
            'research': StageConfig(
                agent_name='ResearchAgent',
                persona_advisors=['Startup Guru', 'Market Research Analyst'],
                advice_type='trend_analysis',
            ),
            'debate': StageConfig(
                agent_name='ContentStudioDebateAgent',
                persona_advisors=[],
                advice_type='content_strategy',
            ),
            'feasibility': StageConfig(
                agent_name='SystemsArchitectAgent',
                persona_advisors=['Business Model Designer', 'Innovation Strategy Planner'],
                advice_type='content_strategy',
            ),
            'risk': StageConfig(
                agent_name='RiskAnalysisAgent',
                persona_advisors=['Startup Guru', 'Market Entry Strategist'],
                advice_type='quality_review',
            ),
            'market': StageConfig(
                agent_name='MarketIntelligenceAgent',
                persona_advisors=['Growth Hacker Pro', 'Strategic Planning Advisor'],
                advice_type='marketing_angle',
            ),
            'synthesis': StageConfig(
                agent_name='ThinkingAgent',
                persona_advisors=[],
                advice_type='content_strategy',
            ),
        },
    ),

    'career': LabConfig(
        name='CareerLab',
        description='Career development, job market, and skills analysis',
        icon='💼',
        routing_tags=['career', 'jobs', 'skills', 'resume', 'interview', 'salary', 'remote'],
        stages={
            'research': StageConfig(
                agent_name='ResearchAgent',
                persona_advisors=['Career Path Strategist', 'Job Application Automator'],
                advice_type='trend_analysis',
            ),
            'debate': StageConfig(
                agent_name='ContentStudioDebateAgent',
                persona_advisors=[],
                advice_type='content_strategy',
            ),
            'feasibility': StageConfig(
                agent_name='SystemsArchitectAgent',
                persona_advisors=['Resume Optimizer AI', 'Interview Coach Pro'],
                advice_type='content_strategy',
            ),
            'risk': StageConfig(
                agent_name='RiskAnalysisAgent',
                persona_advisors=['Salary Negotiation Expert', 'Company Culture Analyzer'],
                advice_type='quality_review',
            ),
            'market': StageConfig(
                agent_name='MarketIntelligenceAgent',
                persona_advisors=['Hidden Job Market Explorer', 'Remote Work Specialist'],
                advice_type='marketing_angle',
            ),
            'synthesis': StageConfig(
                agent_name='ThinkingAgent',
                persona_advisors=[],
                advice_type='content_strategy',
            ),
        },
    ),
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_lab_config(domain: str) -> Optional[LabConfig]:
    """Get lab configuration by domain name."""
    return DOMAIN_LABS.get(domain)


def get_lab_for_tags(tags: List[str]) -> Optional[str]:
    """
    Determine which lab should handle content based on its tags.
    Returns the domain name (e.g., 'legal', 'market') or None.
    """
    if not tags:
        return None

    tags_lower = [t.lower() for t in tags]

    # Score each lab by tag matches
    scores = {}
    for domain, lab in DOMAIN_LABS.items():
        if not lab.is_active:
            continue

        matches = sum(1 for tag in tags_lower if tag in lab.routing_tags)
        if matches > 0:
            scores[domain] = matches

    if not scores:
        return None

    # Return domain with most tag matches
    return max(scores.keys(), key=lambda k: scores[k])


def get_all_active_labs() -> Dict[str, LabConfig]:
    """Get all active lab configurations."""
    return {k: v for k, v in DOMAIN_LABS.items() if v.is_active}


def get_stage_names() -> List[str]:
    """Get ordered list of stage names."""
    return ['research', 'debate', 'feasibility', 'risk', 'market', 'synthesis']
