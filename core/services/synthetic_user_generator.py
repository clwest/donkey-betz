# Session 862: Synthetic User Generator
# Creates diverse test personas to validate agent recommendations

import random
import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PersonaArchetype:
    """Definition of a persona archetype."""
    key: str
    name_template: str
    description: str
    defaults: Dict[str, Any]
    expected_recommendations: List[str]
    expected_agents: List[str]


# Core archetypes covering key user segments
PERSONA_ARCHETYPES = {
    'new_grad': PersonaArchetype(
        key='new_grad',
        name_template='{first_name} - New Graduate',
        description='Recent college graduate seeking first professional role',
        defaults={
            'age_bracket': '18-24',
            'income_bracket': 'under_25k',
            'experience_years': 0,
            'education_level': 'bachelors',
            'primary_goal': 'find_job',
            'timeline': 'immediate',
            'engagement_level': 'active',
            'decision_style': 'deliberate',
            'tech_comfort': 'advanced',
            'full_time': True,
            'remote_only': False,
        },
        expected_recommendations=['entry_level_jobs', 'skill_building', 'resume_help', 'interview_prep'],
        expected_agents=['Resume Optimizer AI', 'Interview Coach Pro', 'Job Application Automator', 'Career Path Strategist'],
    ),

    'career_pivoter': PersonaArchetype(
        key='career_pivoter',
        name_template='{first_name} - Career Changer',
        description='Experienced professional looking to switch industries or roles',
        defaults={
            'age_bracket': '35-44',
            'income_bracket': '75k_100k',
            'experience_years': 10,
            'education_level': 'bachelors',
            'primary_goal': 'career_change',
            'timeline': 'medium_term',
            'engagement_level': 'moderate',
            'decision_style': 'deliberate',
            'tech_comfort': 'intermediate',
            'full_time': True,
            'remote_only': True,
        },
        expected_recommendations=['transferable_skills', 'reskilling', 'industry_insights', 'networking'],
        expected_agents=['Career Path Strategist', 'Skill Gap Analyzer', 'Hidden Job Market Explorer', 'Salary Negotiation Expert'],
    ),

    'freelancer_starter': PersonaArchetype(
        key='freelancer_starter',
        name_template='{first_name} - Aspiring Freelancer',
        description='Employee wanting to transition to freelance/consulting',
        defaults={
            'age_bracket': '25-34',
            'income_bracket': '50k_75k',
            'experience_years': 5,
            'education_level': 'bachelors',
            'primary_goal': 'start_freelancing',
            'timeline': 'short_term',
            'engagement_level': 'active',
            'decision_style': 'deliberate',
            'tech_comfort': 'advanced',
            'contract_work': True,
            'full_time': False,
        },
        expected_recommendations=['freelance_platforms', 'rate_setting', 'client_acquisition', 'portfolio_building'],
        expected_agents=['Freelance Hunter', 'Income Builder Pro', 'Personal Brand Architect', 'Contract Negotiator'],
    ),

    'passive_income_seeker': PersonaArchetype(
        key='passive_income_seeker',
        name_template='{first_name} - Passive Income Builder',
        description='Looking to build income streams beyond primary job',
        defaults={
            'age_bracket': '35-44',
            'income_bracket': '100k_150k',
            'experience_years': 12,
            'education_level': 'masters',
            'primary_goal': 'build_passive_income',
            'timeline': 'long_term',
            'engagement_level': 'moderate',
            'decision_style': 'risk_averse',
            'tech_comfort': 'intermediate',
            'part_time': True,
        },
        expected_recommendations=['investment_opportunities', 'digital_products', 'content_monetization', 'side_businesses'],
        expected_agents=['Passive Income Architect', 'Revenue Stream Analyzer', 'Digital Product Strategist', 'Investment Opportunity Scout'],
    ),

    'executive_side_venture': PersonaArchetype(
        key='executive_side_venture',
        name_template='{first_name} - Executive Explorer',
        description='Senior executive exploring advisory/board roles or ventures',
        defaults={
            'age_bracket': '45-54',
            'income_bracket': 'over_200k',
            'experience_years': 20,
            'education_level': 'masters',
            'primary_goal': 'start_business',
            'timeline': 'exploratory',
            'engagement_level': 'passive',
            'decision_style': 'collaborative',
            'tech_comfort': 'intermediate',
            'hourly_rate_min': 500,
        },
        expected_recommendations=['board_positions', 'advisory_roles', 'angel_investing', 'executive_coaching'],
        expected_agents=['Strategic Planning Advisor', 'Business Growth Architect', 'Executive Network Builder', 'Investment Opportunity Scout'],
    ),

    'tech_upskiller': PersonaArchetype(
        key='tech_upskiller',
        name_template='{first_name} - Tech Upskiller',
        description='Professional wanting to add technical skills for career growth',
        defaults={
            'age_bracket': '25-34',
            'income_bracket': '50k_75k',
            'experience_years': 4,
            'education_level': 'bachelors',
            'primary_goal': 'learn_new_skills',
            'timeline': 'medium_term',
            'engagement_level': 'active',
            'decision_style': 'impulsive',
            'tech_comfort': 'intermediate',
        },
        expected_recommendations=['online_courses', 'bootcamps', 'certifications', 'project_ideas'],
        expected_agents=['Skill Gap Analyzer', 'Learning Path Designer', 'Career Path Strategist', 'Certification Advisor'],
    ),

    'work_life_balancer': PersonaArchetype(
        key='work_life_balancer',
        name_template='{first_name} - Work-Life Seeker',
        description='Professional prioritizing flexibility and work-life balance',
        defaults={
            'age_bracket': '35-44',
            'income_bracket': '75k_100k',
            'experience_years': 8,
            'education_level': 'bachelors',
            'primary_goal': 'work_life_balance',
            'timeline': 'short_term',
            'engagement_level': 'moderate',
            'decision_style': 'deliberate',
            'tech_comfort': 'advanced',
            'remote_only': True,
            'part_time': True,
            'constraints': {'requires_flexibility': True, 'has_caregiving_responsibilities': True},
        },
        expected_recommendations=['remote_jobs', 'flexible_roles', 'part_time_opportunities', 'async_work'],
        expected_agents=['Remote Work Specialist', 'Job Application Automator', 'Work-Life Balance Coach', 'Flexible Gig Finder'],
    ),

    'entrepreneur_builder': PersonaArchetype(
        key='entrepreneur_builder',
        name_template='{first_name} - Startup Builder',
        description='Aspiring or early-stage entrepreneur building a business',
        defaults={
            'age_bracket': '25-34',
            'income_bracket': '50k_75k',
            'experience_years': 6,
            'education_level': 'bachelors',
            'primary_goal': 'start_business',
            'timeline': 'medium_term',
            'engagement_level': 'power_user',
            'decision_style': 'impulsive',
            'tech_comfort': 'expert',
            'contract_work': True,
        },
        expected_recommendations=['startup_resources', 'funding_options', 'market_research', 'mvp_guidance'],
        expected_agents=['Business Model Designer', 'Startup Launch Advisor', 'Market Research Analyst', 'Pitch Deck Creator'],
    ),

    'income_maximizer': PersonaArchetype(
        key='income_maximizer',
        name_template='{first_name} - Income Maximizer',
        description='Professional focused on maximizing earning potential',
        defaults={
            'age_bracket': '25-34',
            'income_bracket': '75k_100k',
            'experience_years': 5,
            'education_level': 'bachelors',
            'primary_goal': 'increase_income',
            'timeline': 'short_term',
            'engagement_level': 'active',
            'decision_style': 'impulsive',
            'tech_comfort': 'advanced',
            'income_target': 150000,
        },
        expected_recommendations=['high_paying_jobs', 'salary_negotiation', 'side_gigs', 'skill_premiums'],
        expected_agents=['Salary Negotiation Expert', 'Income Builder Pro', 'High-Value Skill Advisor', 'Premium Job Finder'],
    ),

    'creative_professional': PersonaArchetype(
        key='creative_professional',
        name_template='{first_name} - Creative Pro',
        description='Designer, writer, or creative professional seeking opportunities',
        defaults={
            'age_bracket': '25-34',
            'income_bracket': '50k_75k',
            'experience_years': 5,
            'education_level': 'bachelors',
            'primary_goal': 'find_job',
            'timeline': 'short_term',
            'engagement_level': 'active',
            'decision_style': 'deliberate',
            'tech_comfort': 'advanced',
            'contract_work': True,
            'industries': ['Design', 'Marketing', 'Media'],
            'skills': ['Graphic Design', 'UI/UX', 'Content Creation', 'Branding'],
        },
        expected_recommendations=['creative_jobs', 'portfolio_tips', 'freelance_platforms', 'creative_communities'],
        expected_agents=['Creative Director AI', 'Personal Brand Architect', 'Freelance Hunter', 'Portfolio Optimizer'],
    ),

    'international_remote': PersonaArchetype(
        key='international_remote',
        name_template='{first_name} - Global Remote Worker',
        description='Professional seeking remote work from outside US',
        defaults={
            'age_bracket': '25-34',
            'income_bracket': '25k_50k',
            'experience_years': 4,
            'education_level': 'bachelors',
            'primary_goal': 'find_job',
            'timeline': 'immediate',
            'engagement_level': 'active',
            'decision_style': 'deliberate',
            'tech_comfort': 'advanced',
            'location': 'International',
            'remote_only': True,
            'constraints': {'timezone': 'flexible', 'visa_status': 'not_required'},
        },
        expected_recommendations=['global_remote_jobs', 'async_work', 'international_freelancing', 'timezone_friendly'],
        expected_agents=['Remote Work Specialist', 'Global Opportunity Finder', 'Freelance Hunter', 'Job Application Automator'],
    ),

    'returning_professional': PersonaArchetype(
        key='returning_professional',
        name_template='{first_name} - Returning Professional',
        description='Professional returning to workforce after career break',
        defaults={
            'age_bracket': '35-44',
            'income_bracket': '50k_75k',
            'experience_years': 8,
            'education_level': 'bachelors',
            'primary_goal': 'find_job',
            'timeline': 'medium_term',
            'engagement_level': 'moderate',
            'decision_style': 'risk_averse',
            'tech_comfort': 'intermediate',
            'context': {'career_gap': True, 'gap_reason': 'caregiving', 'gap_years': 3},
        },
        expected_recommendations=['returnship_programs', 'skill_refresh', 'confidence_building', 'networking'],
        expected_agents=['Career Path Strategist', 'Skill Gap Analyzer', 'Resume Optimizer AI', 'Interview Coach Pro'],
    ),

    'senior_tech_leader': PersonaArchetype(
        key='senior_tech_leader',
        name_template='{first_name} - Tech Leader',
        description='Senior engineer or tech lead seeking principal/director roles',
        defaults={
            'age_bracket': '35-44',
            'income_bracket': '150k_200k',
            'experience_years': 12,
            'education_level': 'masters',
            'primary_goal': 'find_job',
            'timeline': 'exploratory',
            'engagement_level': 'passive',
            'decision_style': 'deliberate',
            'tech_comfort': 'expert',
            'salary_min': 200000,
            'skills': ['System Design', 'Team Leadership', 'Architecture', 'Python', 'Cloud'],
            'industries': ['Technology', 'Fintech', 'AI/ML'],
        },
        expected_recommendations=['principal_roles', 'director_positions', 'tech_leadership', 'faang_opportunities'],
        expected_agents=['Hidden Job Market Explorer', 'Salary Negotiation Expert', 'Executive Network Builder', 'Premium Job Finder'],
    ),

    'gig_worker': PersonaArchetype(
        key='gig_worker',
        name_template='{first_name} - Gig Economy Worker',
        description='Multi-platform gig worker seeking to optimize income',
        defaults={
            'age_bracket': '25-34',
            'income_bracket': '25k_50k',
            'experience_years': 2,
            'education_level': 'some_college',
            'primary_goal': 'increase_income',
            'timeline': 'immediate',
            'engagement_level': 'power_user',
            'decision_style': 'impulsive',
            'tech_comfort': 'advanced',
            'contract_work': True,
            'full_time': False,
        },
        expected_recommendations=['gig_optimization', 'platform_comparison', 'income_stacking', 'tax_tips'],
        expected_agents=['Gig Economy Optimizer', 'Income Builder Pro', 'Multi-Platform Strategist', 'Revenue Stream Analyzer'],
    ),

    'mid_career_stuck': PersonaArchetype(
        key='mid_career_stuck',
        name_template='{first_name} - Career Plateau',
        description='Mid-career professional feeling stuck, seeking advancement',
        defaults={
            'age_bracket': '35-44',
            'income_bracket': '75k_100k',
            'experience_years': 10,
            'education_level': 'bachelors',
            'primary_goal': 'increase_income',
            'timeline': 'medium_term',
            'engagement_level': 'moderate',
            'decision_style': 'deliberate',
            'tech_comfort': 'intermediate',
            'context': {'feeling_stuck': True, 'wants_promotion': True},
        },
        expected_recommendations=['promotion_strategies', 'visibility_tips', 'skill_gaps', 'networking'],
        expected_agents=['Career Path Strategist', 'Salary Negotiation Expert', 'Personal Brand Architect', 'Skill Gap Analyzer'],
    ),
}

# First names for generating personas
FIRST_NAMES = [
    'Alex', 'Jordan', 'Taylor', 'Morgan', 'Casey', 'Riley', 'Quinn', 'Avery',
    'Cameron', 'Dakota', 'Skyler', 'Reese', 'Finley', 'Charlie', 'Jamie', 'Drew',
    'Sage', 'Phoenix', 'River', 'Blake', 'Hayden', 'Rowan', 'Kendall', 'Parker',
    'Maria', 'James', 'Wei', 'Priya', 'Omar', 'Yuki', 'Olga', 'Carlos',
]

# Skill pools by category
SKILL_POOLS = {
    'tech': ['Python', 'JavaScript', 'SQL', 'AWS', 'Docker', 'React', 'Node.js', 'Machine Learning', 'Data Analysis', 'Kubernetes'],
    'business': ['Project Management', 'Strategic Planning', 'Business Development', 'Sales', 'Marketing', 'Finance', 'Operations', 'Leadership'],
    'creative': ['Graphic Design', 'UI/UX', 'Video Editing', 'Content Writing', 'Photography', 'Branding', 'Animation', 'Illustration'],
    'data': ['Data Science', 'Statistics', 'Tableau', 'Power BI', 'Excel', 'R', 'Pandas', 'SQL', 'Data Visualization'],
    'soft': ['Communication', 'Team Leadership', 'Problem Solving', 'Critical Thinking', 'Collaboration', 'Adaptability'],
}


class SyntheticUserGenerator:
    """Generates synthetic user profiles for testing agent recommendations."""

    def __init__(self):
        self.archetypes = PERSONA_ARCHETYPES
        self.first_names = FIRST_NAMES
        self.skill_pools = SKILL_POOLS

    def get_available_archetypes(self) -> List[str]:
        """Get list of available archetype keys."""
        return list(self.archetypes.keys())

    def get_archetype_info(self, archetype_key: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific archetype."""
        archetype = self.archetypes.get(archetype_key)
        if not archetype:
            return None
        return {
            'key': archetype.key,
            'description': archetype.description,
            'expected_recommendations': archetype.expected_recommendations,
            'expected_agents': archetype.expected_agents,
        }

    def generate_profile(
        self,
        archetype_key: str,
        name: Optional[str] = None,
        variations: Optional[Dict[str, Any]] = None,
        seed: Optional[int] = None,
    ):
        """Generate a synthetic user profile based on an archetype."""
        from core.models_synthetic_users import SyntheticUserProfile

        archetype = self.archetypes.get(archetype_key)
        if not archetype:
            raise ValueError(f"Unknown archetype: {archetype_key}")

        if seed is not None:
            random.seed(seed)

        if not name:
            first_name = random.choice(self.first_names)
            name = archetype.name_template.format(first_name=first_name)

        profile_data = {
            'name': name,
            'archetype': archetype_key,
            'description': archetype.description,
            'expected_recommendations': archetype.expected_recommendations,
            'expected_agents': archetype.expected_agents,
            'created_by': 'generator',
            'generation_seed': str(seed) if seed else '',
            **archetype.defaults,
        }

        if variations:
            profile_data.update(variations)

        if 'skills' not in profile_data or not profile_data['skills']:
            profile_data['skills'] = self._generate_skills(archetype_key)

        if 'industries' not in profile_data or not profile_data['industries']:
            profile_data['industries'] = self._generate_industries(archetype_key)

        if not profile_data.get('occupation'):
            profile_data['occupation'] = self._generate_occupation(archetype_key, profile_data.get('skills', []))

        return SyntheticUserProfile(**profile_data)

    def generate_all_archetypes(self, save: bool = False) -> list:
        """Generate one profile for each archetype."""
        profiles = []
        for archetype_key in self.archetypes.keys():
            profile = self.generate_profile(archetype_key, seed=hash(archetype_key) % 10000)
            if save:
                profile.save()
                logger.info(f"Created synthetic user: {profile.name}")
            profiles.append(profile)
        return profiles

    def generate_variations(self, archetype_key: str, count: int = 5, save: bool = False) -> list:
        """Generate multiple variations of an archetype."""
        profiles = []
        for i in range(count):
            seed = hash(f"{archetype_key}_{i}") % 10000
            profile = self.generate_profile(
                archetype_key,
                seed=seed,
                variations=self._generate_random_variations(archetype_key, seed)
            )
            if save:
                profile.save()
                logger.info(f"Created synthetic user variation: {profile.name}")
            profiles.append(profile)
        return profiles

    def _generate_skills(self, archetype_key: str) -> List[str]:
        """Generate relevant skills for an archetype."""
        skill_categories = {
            'new_grad': ['tech', 'soft'],
            'career_pivoter': ['business', 'soft'],
            'freelancer_starter': ['tech', 'business'],
            'passive_income_seeker': ['business', 'data'],
            'executive_side_venture': ['business', 'soft'],
            'tech_upskiller': ['tech', 'data'],
            'work_life_balancer': ['business', 'soft'],
            'entrepreneur_builder': ['tech', 'business'],
            'income_maximizer': ['tech', 'business'],
            'creative_professional': ['creative', 'soft'],
            'international_remote': ['tech', 'soft'],
            'returning_professional': ['business', 'soft'],
            'senior_tech_leader': ['tech', 'business'],
            'gig_worker': ['tech', 'soft'],
            'mid_career_stuck': ['business', 'soft'],
        }

        categories = skill_categories.get(archetype_key, ['business', 'soft'])
        skills = []
        for cat in categories:
            pool = self.skill_pools.get(cat, [])
            skills.extend(random.sample(pool, min(3, len(pool))))
        return skills[:6]

    def _generate_industries(self, archetype_key: str) -> List[str]:
        """Generate relevant industries for an archetype."""
        industry_pools = {
            'tech': ['Technology', 'Software', 'Fintech', 'AI/ML', 'SaaS'],
            'business': ['Consulting', 'Finance', 'Professional Services', 'Healthcare'],
            'creative': ['Design', 'Marketing', 'Media', 'Entertainment', 'Advertising'],
            'general': ['Retail', 'Education', 'Manufacturing', 'Real Estate'],
        }

        archetype_industries = {
            'new_grad': ['tech', 'general'],
            'career_pivoter': ['business', 'tech'],
            'senior_tech_leader': ['tech'],
            'creative_professional': ['creative'],
        }

        pools = archetype_industries.get(archetype_key, ['general', 'business'])
        industries = []
        for pool in pools:
            industries.extend(random.sample(industry_pools.get(pool, []), min(2, len(industry_pools.get(pool, [])))))
        return industries[:3]

    def _generate_occupation(self, archetype_key: str, skills: List[str]) -> str:
        """Generate a plausible occupation based on archetype and skills."""
        occupation_templates = {
            'new_grad': ['Junior {skill} Developer', 'Entry-Level Analyst', 'Associate'],
            'career_pivoter': ['Former {industry} Professional', 'Transitioning Professional'],
            'freelancer_starter': ['{skill} Consultant', 'Independent {skill} Specialist'],
            'senior_tech_leader': ['Senior {skill} Engineer', 'Tech Lead', 'Staff Engineer'],
            'creative_professional': ['{skill} Designer', 'Creative Professional'],
        }

        templates = occupation_templates.get(archetype_key, ['Professional'])
        template = random.choice(templates)
        skill = skills[0] if skills else 'Software'
        return template.format(skill=skill, industry='Tech')

    def _generate_random_variations(self, archetype_key: str, seed: int) -> Dict[str, Any]:
        """Generate random variations for a profile."""
        random.seed(seed)
        variations = {}

        if random.random() < 0.3:
            age_brackets = ['18-24', '25-34', '35-44', '45-54']
            variations['age_bracket'] = random.choice(age_brackets)

        if random.random() < 0.3:
            income_brackets = ['25k_50k', '50k_75k', '75k_100k', '100k_150k']
            variations['income_bracket'] = random.choice(income_brackets)

        if random.random() < 0.3:
            variations['experience_years'] = random.randint(0, 15)

        if random.random() < 0.2:
            variations['engagement_level'] = random.choice(['passive', 'moderate', 'active', 'power_user'])

        return variations


def generate_test_personas(save: bool = True) -> list:
    """Generate all standard test personas."""
    generator = SyntheticUserGenerator()
    return generator.generate_all_archetypes(save=save)


def get_persona_summary() -> Dict[str, Any]:
    """Get a summary of available personas and their purposes."""
    generator = SyntheticUserGenerator()
    summary = {
        'total_archetypes': len(generator.archetypes),
        'archetypes': {}
    }
    for key in generator.archetypes:
        info = generator.get_archetype_info(key)
        summary['archetypes'][key] = {
            'description': info['description'],
            'tests': info['expected_recommendations'],
        }
    return summary
