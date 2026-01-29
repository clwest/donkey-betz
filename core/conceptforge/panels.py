"""
ConceptForge Advisor Panels Configuration
==========================================

Session 863: Advisor panel selection and configuration.

Legendary Advisors act as CONSTRAINTS, not authors:
- Provide debate positions (pro/con)
- Offer risk framing
- Give business lens
- Cast final verdict votes

Core agents do the actual writing with citations and structure.

Panels are snapshotted per run for:
- Reproducibility
- Comparison ("same blog, different panel")
- Audit trail
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import random


@dataclass
class AdvisorProfile:
    """Profile of a legendary advisor for panel assignment."""
    name: str
    title: str
    domain: str
    influence_score: int  # 0-100
    stance_tendency: str  # 'bullish', 'bearish', 'neutral', 'contrarian'
    key_frameworks: List[str] = field(default_factory=list)
    debate_style: str = 'analytical'  # 'analytical', 'passionate', 'pragmatic', 'philosophical'


# =============================================================================
# LEGENDARY ADVISOR PROFILES (for debate positioning)
# =============================================================================

LEGENDARY_ADVISORS: Dict[str, AdvisorProfile] = {
    'warren_buffett': AdvisorProfile(
        name='Warren Buffett',
        title='Investment Guru',
        domain='investment',
        influence_score=98,
        stance_tendency='bullish',
        key_frameworks=['intrinsic_value', 'margin_of_safety', 'circle_of_competence'],
        debate_style='pragmatic',
    ),
    'ray_dalio': AdvisorProfile(
        name='Ray Dalio',
        title='Hedge Fund Titan',
        domain='investment',
        influence_score=96,
        stance_tendency='neutral',
        key_frameworks=['principles', 'radical_transparency', 'believability_weighted'],
        debate_style='analytical',
    ),
    'cathie_wood': AdvisorProfile(
        name='Cathie Wood',
        title='Innovation Investor',
        domain='investment',
        influence_score=94,
        stance_tendency='bullish',
        key_frameworks=['disruptive_innovation', 'convergence', 'exponential_growth'],
        debate_style='passionate',
    ),
    'peter_thiel': AdvisorProfile(
        name='Peter Thiel',
        title='Contrarian Thinker',
        domain='startup',
        influence_score=94,
        stance_tendency='contrarian',
        key_frameworks=['zero_to_one', 'monopoly_theory', 'definite_optimism'],
        debate_style='philosophical',
    ),
    'elon_musk': AdvisorProfile(
        name='Elon Musk',
        title='Tech Visionary',
        domain='tech',
        influence_score=97,
        stance_tendency='bullish',
        key_frameworks=['first_principles', 'rapid_iteration', 'ambitious_goals'],
        debate_style='passionate',
    ),
    'george_soros': AdvisorProfile(
        name='George Soros',
        title='Market Wizard',
        domain='investment',
        influence_score=93,
        stance_tendency='bearish',
        key_frameworks=['reflexivity', 'boom_bust_cycles', 'fallibility'],
        debate_style='analytical',
    ),
    'jeff_bezos': AdvisorProfile(
        name='Jeff Bezos',
        title='E-commerce Pioneer',
        domain='business',
        influence_score=96,
        stance_tendency='bullish',
        key_frameworks=['customer_obsession', 'long_term_thinking', 'day_one_mentality'],
        debate_style='pragmatic',
    ),
    'steve_jobs': AdvisorProfile(
        name='Steve Jobs',
        title='Product Genius',
        domain='creative',
        influence_score=98,
        stance_tendency='bullish',
        key_frameworks=['simplicity', 'design_thinking', 'reality_distortion'],
        debate_style='passionate',
    ),
    'mark_cuban': AdvisorProfile(
        name='Mark Cuban',
        title='Shark Tank Star',
        domain='startup',
        influence_score=91,
        stance_tendency='neutral',
        key_frameworks=['hustle', 'customer_validation', 'sales_focus'],
        debate_style='pragmatic',
    ),
    'gary_vaynerchuk': AdvisorProfile(
        name='Gary Vaynerchuk',
        title='Digital Marketing Pioneer',
        domain='marketing',
        influence_score=92,
        stance_tendency='bullish',
        key_frameworks=['attention_economy', 'content_is_king', 'hustle'],
        debate_style='passionate',
    ),
    'seth_godin': AdvisorProfile(
        name='Seth Godin',
        title='Marketing Philosopher',
        domain='marketing',
        influence_score=91,
        stance_tendency='neutral',
        key_frameworks=['permission_marketing', 'purple_cow', 'tribes'],
        debate_style='philosophical',
    ),
    'richard_branson': AdvisorProfile(
        name='Richard Branson',
        title='Serial Entrepreneur',
        domain='startup',
        influence_score=93,
        stance_tendency='bullish',
        key_frameworks=['brand_extension', 'disruption', 'people_first'],
        debate_style='passionate',
    ),
    'christine_lagarde': AdvisorProfile(
        name='Christine Lagarde',
        title='Central Banking Expert',
        domain='finance',
        influence_score=90,
        stance_tendency='neutral',
        key_frameworks=['monetary_policy', 'financial_stability', 'global_coordination'],
        debate_style='analytical',
    ),
    'jamie_dimon': AdvisorProfile(
        name='Jamie Dimon',
        title='Banking Leader',
        domain='finance',
        influence_score=91,
        stance_tendency='neutral',
        key_frameworks=['risk_management', 'scale_economics', 'fortress_balance_sheet'],
        debate_style='pragmatic',
    ),
    'tim_ferriss': AdvisorProfile(
        name='Tim Ferriss',
        title='Lifestyle Designer',
        domain='personal',
        influence_score=90,
        stance_tendency='contrarian',
        key_frameworks=['80_20_rule', 'minimum_effective_dose', 'fear_setting'],
        debate_style='analytical',
    ),
    'simon_sinek': AdvisorProfile(
        name='Simon Sinek',
        title='Leadership Expert',
        domain='business',
        influence_score=89,
        stance_tendency='neutral',
        key_frameworks=['start_with_why', 'infinite_game', 'leaders_eat_last'],
        debate_style='philosophical',
    ),
    'yuval_harari': AdvisorProfile(
        name='Yuval Noah Harari',
        title='Future Thinker',
        domain='research',
        influence_score=90,
        stance_tendency='bearish',
        key_frameworks=['cognitive_revolution', 'dataism', 'human_obsolescence'],
        debate_style='philosophical',
    ),
    'reid_hoffman': AdvisorProfile(
        name='Reid Hoffman',
        title='Network Philosopher',
        domain='startup',
        influence_score=90,
        stance_tendency='bullish',
        key_frameworks=['blitzscaling', 'network_effects', 'alliance_strategy'],
        debate_style='analytical',
    ),
}


# =============================================================================
# DOMAIN-SPECIFIC ADVISOR POOLS
# =============================================================================

@dataclass
class PanelPool:
    """Pool of advisors available for a domain lab."""
    required: List[str]  # Must include these advisors
    optional: List[str]  # Can include 0-2 of these
    debate_pairs: List[Tuple[str, str]]  # Bull vs Bear pairs for debate stage


ADVISOR_PANELS: Dict[str, PanelPool] = {
    'legal': PanelPool(
        required=['warren_buffett', 'peter_thiel'],  # Risk/opportunity perspective
        optional=['jamie_dimon', 'christine_lagarde', 'simon_sinek'],
        debate_pairs=[
            ('warren_buffett', 'george_soros'),  # Optimist vs skeptic on legal tech
            ('jeff_bezos', 'yuval_harari'),  # Progress vs caution
        ],
    ),
    'market': PanelPool(
        required=['warren_buffett', 'ray_dalio'],
        optional=['cathie_wood', 'george_soros', 'peter_thiel'],
        debate_pairs=[
            ('cathie_wood', 'warren_buffett'),  # Growth vs value
            ('ray_dalio', 'george_soros'),  # Systematic vs discretionary
        ],
    ),
    'tech': PanelPool(
        required=['elon_musk', 'peter_thiel'],
        optional=['jeff_bezos', 'reid_hoffman', 'yuval_harari'],
        debate_pairs=[
            ('elon_musk', 'yuval_harari'),  # Optimist vs cautionary
            ('peter_thiel', 'cathie_wood'),  # Contrarian vs momentum
        ],
    ),
    'content': PanelPool(
        required=['gary_vaynerchuk', 'seth_godin'],
        optional=['steve_jobs', 'richard_branson', 'tim_ferriss'],
        debate_pairs=[
            ('gary_vaynerchuk', 'seth_godin'),  # Volume vs quality
            ('steve_jobs', 'mark_cuban'),  # Design vs sales focus
        ],
    ),
    'startup': PanelPool(
        required=['mark_cuban', 'reid_hoffman'],
        optional=['richard_branson', 'peter_thiel', 'tim_ferriss'],
        debate_pairs=[
            ('richard_branson', 'peter_thiel'),  # Brand builder vs contrarian
            ('mark_cuban', 'reid_hoffman'),  # Hustle vs scale
        ],
    ),
    'career': PanelPool(
        required=['tim_ferriss', 'simon_sinek'],
        optional=['gary_vaynerchuk', 'reid_hoffman', 'mark_cuban'],
        debate_pairs=[
            ('tim_ferriss', 'gary_vaynerchuk'),  # Lifestyle vs hustle
            ('simon_sinek', 'mark_cuban'),  # Purpose vs profit
        ],
    ),
}


# =============================================================================
# PANEL SELECTION FUNCTIONS
# =============================================================================

def select_panel_for_domain(
    domain: str,
    include_optional: int = 1,
    seed: Optional[int] = None
) -> Dict:
    """
    Select an advisor panel for a domain lab.

    Returns a snapshot dict that should be stored with the run for reproducibility.

    Args:
        domain: Domain name (e.g., 'legal', 'market')
        include_optional: Number of optional advisors to include (0-2)
        seed: Random seed for reproducible selection

    Returns:
        Dict with panel configuration snapshot
    """
    pool = ADVISOR_PANELS.get(domain)
    if not pool:
        # Default panel for unknown domains
        return {
            'domain': domain,
            'advisors': ['warren_buffett', 'peter_thiel'],
            'debate_pair': ('warren_buffett', 'peter_thiel'),
            'profiles': {
                'warren_buffett': _profile_to_dict(LEGENDARY_ADVISORS['warren_buffett']),
                'peter_thiel': _profile_to_dict(LEGENDARY_ADVISORS['peter_thiel']),
            }
        }

    if seed is not None:
        random.seed(seed)

    # Start with required advisors
    selected = list(pool.required)

    # Add optional advisors
    if include_optional > 0 and pool.optional:
        optional_count = min(include_optional, len(pool.optional))
        selected.extend(random.sample(pool.optional, optional_count))

    # Select debate pair
    debate_pair = random.choice(pool.debate_pairs) if pool.debate_pairs else None

    # Build profiles dict
    profiles = {}
    for advisor_key in selected:
        if advisor_key in LEGENDARY_ADVISORS:
            profiles[advisor_key] = _profile_to_dict(LEGENDARY_ADVISORS[advisor_key])

    return {
        'domain': domain,
        'advisors': selected,
        'debate_pair': debate_pair,
        'profiles': profiles,
    }


def _profile_to_dict(profile: AdvisorProfile) -> Dict:
    """Convert AdvisorProfile to serializable dict."""
    return {
        'name': profile.name,
        'title': profile.title,
        'domain': profile.domain,
        'influence_score': profile.influence_score,
        'stance_tendency': profile.stance_tendency,
        'key_frameworks': profile.key_frameworks,
        'debate_style': profile.debate_style,
    }


def get_debate_positions(panel_snapshot: Dict) -> Dict:
    """
    Get debate positions for a panel.

    Returns dict with 'pro' and 'con' advisor assignments.
    """
    debate_pair = panel_snapshot.get('debate_pair')
    if not debate_pair:
        return {'pro': None, 'con': None}

    profiles = panel_snapshot.get('profiles', {})
    pro_key, con_key = debate_pair

    pro_profile = profiles.get(pro_key, {})
    con_profile = profiles.get(con_key, {})

    return {
        'pro': {
            'key': pro_key,
            'name': pro_profile.get('name', pro_key),
            'frameworks': pro_profile.get('key_frameworks', []),
            'style': pro_profile.get('debate_style', 'analytical'),
        },
        'con': {
            'key': con_key,
            'name': con_profile.get('name', con_key),
            'frameworks': con_profile.get('key_frameworks', []),
            'style': con_profile.get('debate_style', 'analytical'),
        },
    }


def get_advisor_wisdom(advisor_key: str) -> Dict:
    """Get wisdom and frameworks for an advisor."""
    profile = LEGENDARY_ADVISORS.get(advisor_key)
    if not profile:
        return {}

    return {
        'name': profile.name,
        'title': profile.title,
        'frameworks': profile.key_frameworks,
        'stance': profile.stance_tendency,
        'style': profile.debate_style,
    }
