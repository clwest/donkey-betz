"""
Advisor Registry System - Domain Expert Advisory Network

This module provides a specialized registry for domain expert advisors that work
alongside agents to provide deep expertise, strategic guidance, and decision support.
Unlike agents which execute tasks, advisors provide consultation, analysis, and recommendations.

Features:
- 25+ specialized domain advisors
- Expertise-based routing and consultation
- Advisory session management
- Integration with agent workflows
- Performance tracking and recommendations
"""

import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class AdvisorDomain(Enum):
    """Domain specializations for advisors"""
    # Financial & Investment
    FINANCIAL_PLANNING = "financial_planning"
    INVESTMENT_STRATEGY = "investment_strategy"
    RISK_MANAGEMENT = "risk_management"
    CRYPTO_ANALYSIS = "crypto_analysis"
    OPTIONS_TRADING = "options_trading"

    # Business & Entrepreneurship
    BUSINESS_STRATEGY = "business_strategy"
    STARTUP_CONSULTING = "startup_consulting"
    MARKETING_STRATEGY = "marketing_strategy"
    SALES_OPTIMIZATION = "sales_optimization"
    OPERATIONS_MANAGEMENT = "operations_management"

    # Technology & Innovation
    TECHNICAL_ARCHITECTURE = "technical_architecture"
    AI_ML_STRATEGY = "ai_ml_strategy"
    PRODUCT_DEVELOPMENT = "product_development"
    DATA_STRATEGY = "data_strategy"
    CYBERSECURITY = "cybersecurity"

    # Legal & Compliance
    LEGAL_COUNSEL = "legal_counsel"
    REGULATORY_COMPLIANCE = "regulatory_compliance"
    INTELLECTUAL_PROPERTY = "intellectual_property"

    # Specialized Domains
    SPORTS_ANALYTICS = "sports_analytics"
    REAL_ESTATE = "real_estate"
    HEALTHCARE_STRATEGY = "healthcare_strategy"
    EDUCATION_STRATEGY = "education_strategy"
    CONTENT_STRATEGY = "content_strategy"

    # Personal Development
    CAREER_COACHING = "career_coaching"
    LEADERSHIP_DEVELOPMENT = "leadership_development"
    NEGOTIATION_STRATEGY = "negotiation_strategy"


class AdvisorExpertiseLevel(Enum):
    """Advisor expertise levels"""
    SPECIALIST = "specialist"      # 3-7 years experience
    EXPERT = "expert"             # 7-15 years experience
    MASTER = "master"             # 15+ years experience
    LEGEND = "legend"             # Industry pioneers/recognized authorities


@dataclass
class AdvisorProfile:
    """Comprehensive advisor profile"""
    id: str
    name: str
    title: str
    domain: AdvisorDomain
    expertise_level: AdvisorExpertiseLevel
    specializations: List[str]
    years_experience: int

    # Advisory capabilities
    consultation_types: List[str]  # ["strategy", "analysis", "review", "planning"]
    decision_frameworks: List[str]  # Methodologies they use
    typical_engagement_duration: str  # "30min", "1hour", "ongoing"

    # Background & credentials
    background: str
    key_achievements: List[str]
    certifications: List[str]
    languages: List[str] = field(default_factory=lambda: ["English"])

    # Performance metrics
    satisfaction_rating: float = 0.0
    total_consultations: int = 0
    success_rate: float = 0.0
    response_time_hours: float = 24.0

    # Availability & preferences
    availability_hours: Dict[str, List[str]] = field(default_factory=dict)  # "monday": ["9-17"]
    preferred_communication: List[str] = field(default_factory=lambda: ["chat", "video"])
    consultation_fee: Optional[float] = None  # Per hour, None for internal advisors

    # Integration settings
    integrates_with_agents: bool = True
    preferred_agent_types: List[str] = field(default_factory=list)
    workflow_templates: List[str] = field(default_factory=list)


@dataclass
class AdvisorConsultation:
    """Advisory consultation session"""
    id: str
    advisor_id: str
    user_id: str
    topic: str
    domain: AdvisorDomain

    # Session details
    consultation_type: str  # "strategy", "review", "analysis", "decision_support"
    status: str  # "requested", "scheduled", "in_progress", "completed", "cancelled"
    scheduled_time: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Content
    initial_request: str = ""
    advisor_notes: str = ""
    recommendations: List[str] = field(default_factory=list)
    action_items: List[str] = field(default_factory=list)
    follow_up_needed: bool = False

    # Outcomes
    satisfaction_score: Optional[int] = None  # 1-10
    implementation_status: str = "pending"  # "pending", "in_progress", "completed"
    measurable_outcomes: Dict[str, Any] = field(default_factory=dict)


class AdvisorRegistry:
    """
    Centralized registry for domain expert advisors.

    Manages advisor profiles, consultation scheduling, and integration
    with the agent system for comprehensive decision support.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.advisors: Dict[str, AdvisorProfile] = {}
        self.consultations: Dict[str, AdvisorConsultation] = {}
        self._initialize_advisor_network()

    def _initialize_advisor_network(self):
        """Initialize the comprehensive advisor network.

        Session 1142 rename: all advisor identities are functional, not
        named after real people. The ``id`` field is preserved (it is an
        internal routing handle used by ``advisor_context_builder``,
        seeding scripts, and persisted ``AdvisorConsultation`` rows).
        Human-facing fields (``name``, ``background``, ``key_achievements``,
        ``certifications``) describe capability anchors and do not claim
        to BE any real-world person or institution.
        """
        advisors_data = [
            # Financial & Investment Advisors
            {
                "id": "financial_strategist",
                "name": "Senior Financial Strategist",
                "title": "Senior Financial Strategist",
                "domain": AdvisorDomain.FINANCIAL_PLANNING,
                "expertise_level": AdvisorExpertiseLevel.EXPERT,
                "specializations": ["wealth_building", "retirement_planning", "tax_optimization"],
                "years_experience": 12,
                "consultation_types": ["strategy", "analysis", "planning"],
                "decision_frameworks": ["goal_based_planning", "risk_assessment", "monte_carlo_analysis"],
                "typical_engagement_duration": "1hour",
                "background": "Senior wealth-management practitioner with a track record across high-net-worth financial planning, retirement modeling, and tax-aware portfolio construction.",
                "key_achievements": ["Multi-hundred-million AUM oversight", "Sustained double-digit annualized client returns"],
                "certifications": ["CFA", "CFP", "CAIA"]
            },

            {
                "id": "crypto_expert",
                "name": "Blockchain & Crypto Strategist",
                "title": "Blockchain & Crypto Strategist",
                "domain": AdvisorDomain.CRYPTO_ANALYSIS,
                "expertise_level": AdvisorExpertiseLevel.MASTER,
                "specializations": ["defi_protocols", "nft_markets", "crypto_trading", "blockchain_tech"],
                "years_experience": 8,
                "consultation_types": ["analysis", "strategy", "review"],
                "decision_frameworks": ["fundamental_analysis", "technical_analysis", "on_chain_metrics"],
                "typical_engagement_duration": "45min",
                "background": "Long-tenured crypto market participant with hands-on experience building a DeFi protocol and operating a crypto-focused fund.",
                "key_achievements": ["Outsized returns on early-stage crypto allocations", "Built and shipped a DeFi protocol at scale"],
                "certifications": ["CBCP", "Blockchain Council Certified"]
            },

            {
                "id": "options_master",
                "name": "Options Trading Master",
                "title": "Options Trading Master",
                "domain": AdvisorDomain.OPTIONS_TRADING,
                "expertise_level": AdvisorExpertiseLevel.LEGEND,
                "specializations": ["volatility_trading", "risk_management", "exotic_options", "market_making"],
                "years_experience": 18,
                "consultation_types": ["strategy", "analysis", "risk_review"],
                "decision_frameworks": ["black_scholes", "volatility_modeling", "greeks_analysis"],
                "typical_engagement_duration": "1hour",
                "background": "Former head of options at a major proprietary trading firm; pioneered volatility-based strategies and proprietary modeling.",
                "key_achievements": ["Consistently profitable across 15+ years", "Developed proprietary volatility models"],
                "certifications": ["CMT", "Options Institute Graduate"]
            },

            # Business & Strategy Advisors
            {
                "id": "business_strategist",
                "name": "Strategic Business Advisor",
                "title": "Strategic Business Advisor",
                "domain": AdvisorDomain.BUSINESS_STRATEGY,
                "expertise_level": AdvisorExpertiseLevel.EXPERT,
                "specializations": ["growth_strategy", "market_expansion", "competitive_analysis", "m&a"],
                "years_experience": 14,
                "consultation_types": ["strategy", "planning", "review"],
                "decision_frameworks": ["porter_five_forces", "blue_ocean", "lean_startup"],
                "typical_engagement_duration": "1.5hour",
                "background": "Former partner at a top-tier strategy consulting firm; advised dozens of startups through unicorn-stage scaling.",
                "key_achievements": ["20+ successful exits across portfolio", "Built three companies from zero to nine-figure revenue"],
                "certifications": ["MBA from a top-tier business school", "Certified Management Consultant"]
            },

            {
                "id": "startup_guru",
                "name": "Startup & Venture Advisor",
                "title": "Startup & Venture Advisor",
                "domain": AdvisorDomain.STARTUP_CONSULTING,
                "expertise_level": AdvisorExpertiseLevel.MASTER,
                "specializations": ["product_market_fit", "fundraising", "team_building", "scaling"],
                "years_experience": 16,
                "consultation_types": ["strategy", "review", "planning"],
                "decision_frameworks": ["lean_canvas", "jobs_to_be_done", "growth_accounting"],
                "typical_engagement_duration": "1hour",
                "background": "Three-time founder with successful exits; active angel investor across 50+ early-stage companies.",
                "key_achievements": ["Built a unicorn-scale company", "50+ early-stage startup investments"],
                "certifications": ["Executive education in board governance", "Fellowship-level startup ecosystem program"]
            },

            # Technology Advisors
            {
                "id": "tech_architect",
                "name": "Chief Technology Architect",
                "title": "Chief Technology Architect",
                "domain": AdvisorDomain.TECHNICAL_ARCHITECTURE,
                "expertise_level": AdvisorExpertiseLevel.MASTER,
                "specializations": ["system_design", "scalability", "cloud_architecture", "ai_integration"],
                "years_experience": 15,
                "consultation_types": ["architecture_review", "strategy", "technical_planning"],
                "decision_frameworks": ["domain_driven_design", "microservices", "cloud_native"],
                "typical_engagement_duration": "2hour",
                "background": "Former senior architect at hyperscale cloud and consumer-hardware companies; built systems serving billions of users.",
                "key_achievements": ["Scaled production systems to 10B+ requests/day", "Led organizations of 200+ engineers"],
                "certifications": ["Hyperscaler solutions-architect certification", "Multi-cloud architect certification"]
            },

            {
                "id": "ai_strategist",
                "name": "AI & Machine Learning Strategist",
                "title": "AI & Machine Learning Strategist",
                "domain": AdvisorDomain.AI_ML_STRATEGY,
                "expertise_level": AdvisorExpertiseLevel.LEGEND,
                "specializations": ["deep_learning", "nlp", "computer_vision", "ml_ops"],
                "years_experience": 12,
                "consultation_types": ["strategy", "technical_review", "research_guidance"],
                "decision_frameworks": ["ai_readiness_assessment", "ml_lifecycle", "ethical_ai"],
                "typical_engagement_duration": "1.5hour",
                "background": "Former research scientist at a leading AI lab; doctorate in computer science with an extensive peer-reviewed publication record.",
                "key_achievements": ["Contributed to transformer-architecture advances", "Built AI systems generating nine-figure value"],
                "certifications": ["PhD Computer Science", "AI Ethics Certificate"]
            },

            # Specialized Domain Advisors
            {
                "id": "sports_analytics_expert",
                "name": "Sports Analytics & Betting Expert",
                "title": "Sports Analytics & Betting Expert",
                "domain": AdvisorDomain.SPORTS_ANALYTICS,
                "expertise_level": AdvisorExpertiseLevel.MASTER,
                "specializations": ["predictive_modeling", "player_analysis", "betting_strategies", "data_science"],
                "years_experience": 10,
                "consultation_types": ["analysis", "strategy", "model_review"],
                "decision_frameworks": ["sabermetrics", "expected_value", "kelly_criterion"],
                "typical_engagement_duration": "45min",
                "background": "Former analytics director for a professional basketball franchise; built winning betting models used by major syndicates.",
                "key_achievements": ["15% ROI sustained across 8+ years of betting", "Multiple high-confidence upset calls"],
                "certifications": ["Sports Analytics Certificate", "Statistics PhD"]
            },

            {
                "id": "real_estate_mogul",
                "name": "Real Estate Investment Strategist",
                "title": "Real Estate Investment Strategist",
                "domain": AdvisorDomain.REAL_ESTATE,
                "expertise_level": AdvisorExpertiseLevel.LEGEND,
                "specializations": ["investment_analysis", "market_timing", "commercial_real_estate", "reits"],
                "years_experience": 25,
                "consultation_types": ["investment_analysis", "strategy", "market_review"],
                "decision_frameworks": ["dcf_analysis", "cap_rate_analysis", "market_cycle_timing"],
                "typical_engagement_duration": "1hour",
                "background": "Built a multi-billion-dollar commercial real estate portfolio across three full market cycles.",
                "key_achievements": ["20% annualized returns sustained across 25 years", "No losing years across full holding period"],
                "certifications": ["CCIM", "Real Estate License", "MBA from a top-tier business school"]
            },

            # Legal & Compliance
            {
                "id": "legal_counsel",
                "name": "Corporate Legal Strategist",
                "title": "Corporate Legal Strategist",
                "domain": AdvisorDomain.LEGAL_COUNSEL,
                "expertise_level": AdvisorExpertiseLevel.EXPERT,
                "specializations": ["corporate_law", "securities_law", "contract_negotiation", "risk_mitigation"],
                "years_experience": 13,
                "consultation_types": ["legal_review", "risk_assessment", "strategy"],
                "decision_frameworks": ["legal_risk_matrix", "compliance_framework", "contract_analysis"],
                "typical_engagement_duration": "1hour",
                "background": "Partner at a top-tier law firm specializing in technology and finance sectors.",
                "key_achievements": ["Led $10B+ M&A transactions", "Unbroken successful-case record on major matters"],
                "certifications": ["JD from a top-tier law school", "Multi-state bar admission"]
            },

            # Personal Development
            {
                "id": "career_coach",
                "name": "Executive Career Strategist",
                "title": "Executive Career Strategist",
                "domain": AdvisorDomain.CAREER_COACHING,
                "expertise_level": AdvisorExpertiseLevel.MASTER,
                "specializations": ["executive_coaching", "leadership_development", "career_transitions", "negotiation"],
                "years_experience": 18,
                "consultation_types": ["coaching", "strategy", "development_planning"],
                "decision_frameworks": ["strengths_finder", "360_feedback", "career_pathing"],
                "typical_engagement_duration": "1hour",
                "background": "Former Fortune-500 CHRO; coached 100+ executives into C-suite roles.",
                "key_achievements": ["95% promotion success rate across coached executives", "Average ~40% salary increase across transitions"],
                "certifications": ["PhD Psychology", "ICF Master Coach", "SHRM-SCP"]
            },

            # Additional Legendary Advisors (named-figure IDs preserved for
            # routing back-compat; identities now functional, no real-world
            # name or institutional name-drops in user-facing fields)

            # Investment Legends
            {
                "id": "warren_buffett_advisor",
                "name": "Value Investing Strategist",
                "title": "Value Investing Strategist",
                "domain": AdvisorDomain.INVESTMENT_STRATEGY,
                "expertise_level": AdvisorExpertiseLevel.LEGEND,
                "specializations": ["value_investing", "long_term_strategy", "fundamental_analysis", "moats"],
                "years_experience": 60,
                "consultation_types": ["strategy", "analysis", "portfolio_review"],
                "decision_frameworks": ["intrinsic_value", "margin_of_safety", "circle_of_competence"],
                "typical_engagement_duration": "2hour",
                "background": "Long-running value-investing practice anchored in intrinsic-value analysis, margin-of-safety discipline, and circle-of-competence selection.",
                "key_achievements": ["Multi-decade compounding returns at portfolio scale", "Lifetime case studies in patient capital allocation"],
                "certifications": ["Multi-decade applied track record"]
            },

            {
                "id": "cathie_wood_advisor",
                "name": "Innovation Investment Strategist",
                "title": "Innovation Investment Strategist",
                "domain": AdvisorDomain.INVESTMENT_STRATEGY,
                "expertise_level": AdvisorExpertiseLevel.LEGEND,
                "specializations": ["disruptive_innovation", "growth_investing", "tech_stocks", "genomics"],
                "years_experience": 40,
                "consultation_types": ["strategy", "trend_analysis", "innovation_scouting"],
                "decision_frameworks": ["disruptive_innovation_theory", "wright_s_law", "convergence_analysis"],
                "typical_engagement_duration": "1.5hour",
                "background": "Thematic growth-investing practice focused on disruptive innovation across genomics, AI, robotics, and digital assets.",
                "key_achievements": ["Pioneered actively-managed innovation ETFs", "Early-conviction allocations to category-defining tech"],
                "certifications": ["CFA Charter", "Finance degree from a top-tier program"]
            },

            {
                "id": "ray_dalio_advisor",
                "name": "Macro Economic Strategist",
                "title": "Macro Economic Strategist",
                "domain": AdvisorDomain.RISK_MANAGEMENT,
                "expertise_level": AdvisorExpertiseLevel.LEGEND,
                "specializations": ["macro_economics", "risk_parity", "principles", "debt_cycles"],
                "years_experience": 45,
                "consultation_types": ["strategy", "risk_analysis", "economic_outlook"],
                "decision_frameworks": ["principles_based", "all_weather_portfolio", "economic_machine"],
                "typical_engagement_duration": "2hour",
                "background": "Decades of macro hedge-fund strategy: risk-parity portfolio construction, debt-cycle analysis, principles-based decisioning.",
                "key_achievements": ["Built one of the world's largest macro hedge funds", "Pioneered all-weather portfolio construction", "Called the 2008 global financial crisis"],
                "certifications": ["MBA from a top-tier business school", "CFA"]
            },

            # Tech Titans
            {
                "id": "elon_musk_advisor",
                "name": "First-Principles Engineering Advisor",
                "title": "First-Principles Engineering Advisor",
                "domain": AdvisorDomain.PRODUCT_DEVELOPMENT,
                "expertise_level": AdvisorExpertiseLevel.LEGEND,
                "specializations": ["first_principles", "exponential_thinking", "space_tech", "ai_future"],
                "years_experience": 25,
                "consultation_types": ["innovation_strategy", "product_vision", "scaling"],
                "decision_frameworks": ["first_principles_thinking", "exponential_growth", "vertical_integration"],
                "typical_engagement_duration": "1hour",
                "background": "Cross-industry product engineering anchored in first-principles thinking, exponential-growth planning, and vertical integration.",
                "key_achievements": ["Built multiple $100B+ companies across electric vehicles, aerospace, and AI", "Drove category-defining cost-curve improvements"],
                "certifications": ["Physics undergraduate training", "Self-taught engineering practice"]
            },

            {
                "id": "sam_altman_advisor",
                "name": "AI & Startup Strategy Expert",
                "title": "AI & Startup Strategy Expert",
                "domain": AdvisorDomain.AI_ML_STRATEGY,
                "expertise_level": AdvisorExpertiseLevel.LEGEND,
                "specializations": ["artificial_intelligence", "startup_scaling", "product_strategy", "agi"],
                "years_experience": 15,
                "consultation_types": ["ai_strategy", "startup_advice", "scaling"],
                "decision_frameworks": ["power_law_returns", "network_effects", "platform_thinking"],
                "typical_engagement_duration": "1hour",
                "background": "Combined leadership of a leading AI research lab with deep startup-accelerator experience; covers AI strategy, scaling, and platform thinking.",
                "key_achievements": ["Led an AI lab to deploy a category-defining consumer product", "Scaled a startup accelerator past 1000+ companies"],
                "certifications": ["Computer science training at a top-tier university", "Top startup-accelerator alumnus"]
            },

            # Marketing & Sales Legends
            {
                "id": "gary_vaynerchuk_advisor",
                "name": "Digital Marketing & Brand Strategist",
                "title": "Digital Marketing & Brand Strategist",
                "domain": AdvisorDomain.MARKETING_STRATEGY,
                "expertise_level": AdvisorExpertiseLevel.LEGEND,
                "specializations": ["social_media", "brand_building", "content_marketing", "web3"],
                "years_experience": 20,
                "consultation_types": ["marketing_strategy", "brand_development", "content_planning"],
                "decision_frameworks": ["jab_jab_right_hook", "day_trading_attention", "brand_storytelling"],
                "typical_engagement_duration": "1hour",
                "background": "Two decades of brand-building practice combining digital marketing, content strategy, and emerging-platform dynamics.",
                "key_achievements": ["Built a $200M digital agency", "Scaled a niche e-commerce business to nine-figure revenue", "Early operator in NFT and creator-economy markets"],
                "certifications": ["Multi-decade applied marketing practice"]
            },

            {
                "id": "grant_cardone_advisor",
                "name": "Sales & Real Estate Strategist",
                "title": "Sales & Real Estate Strategist",
                "domain": AdvisorDomain.SALES_OPTIMIZATION,
                "expertise_level": AdvisorExpertiseLevel.LEGEND,
                "specializations": ["sales_training", "real_estate", "10x_thinking", "closing_deals"],
                "years_experience": 30,
                "consultation_types": ["sales_strategy", "negotiation", "scaling"],
                "decision_frameworks": ["10x_rule", "aggressive_expansion", "massive_action"],
                "typical_engagement_duration": "1.5hour",
                "background": "Three decades of high-volume sales training plus large-scale commercial real estate operations.",
                "key_achievements": ["Multi-billion AUM commercial real estate portfolio", "Bestselling sales-strategy author", "Built a sales-training franchise at scale"],
                "certifications": ["Multi-decade applied sales practice", "Certified sales trainer"]
            },

            # Sports & Analytics
            {
                "id": "billy_beane_advisor",
                "name": "Sports Analytics Pioneer",
                "title": "Sports Analytics Pioneer",
                "domain": AdvisorDomain.SPORTS_ANALYTICS,
                "expertise_level": AdvisorExpertiseLevel.LEGEND,
                "specializations": ["sabermetrics", "value_finding", "data_driven_decisions", "moneyball"],
                "years_experience": 30,
                "consultation_types": ["analytics_strategy", "value_optimization", "team_building"],
                "decision_frameworks": ["moneyball", "statistical_arbitrage", "ops_optimization"],
                "typical_engagement_duration": "1.5hour",
                "background": "Pioneer of statistics-driven sports management; brought sabermetric value-finding into mainstream team operations.",
                "key_achievements": ["Long playoff appearances on a minimum-budget roster", "Established a winning paradigm later copied across the league"],
                "certifications": ["Top-tier university degree", "Multi-decade professional baseball operations experience"]
            },

            {
                "id": "haralabos_voulgaris_advisor",
                "name": "Sports Betting Quant",
                "title": "Sports Betting Quant",
                "domain": AdvisorDomain.SPORTS_ANALYTICS,
                "expertise_level": AdvisorExpertiseLevel.LEGEND,
                "specializations": ["nba_analytics", "sports_betting", "predictive_modeling", "live_betting"],
                "years_experience": 20,
                "consultation_types": ["betting_strategy", "model_development", "bankroll_management"],
                "decision_frameworks": ["expected_value", "regression_models", "live_adjustments"],
                "typical_engagement_duration": "1hour",
                "background": "Two decades of professional sports betting combined with quantitative analytics work for a top-tier NBA franchise.",
                "key_achievements": ["Multi-million dollar career betting profits", "Director of Quantitative R&D for a professional basketball team"],
                "certifications": ["Self-taught", "Multi-decade documented track record"]
            },

            # Content & Media
            {
                "id": "mr_beast_advisor",
                "name": "Creator Economy Strategist",
                "title": "Creator Economy Strategist",
                "domain": AdvisorDomain.CONTENT_STRATEGY,
                "expertise_level": AdvisorExpertiseLevel.LEGEND,
                "specializations": ["viral_content", "youtube_optimization", "retention_hacking", "scaling_content"],
                "years_experience": 10,
                "consultation_types": ["content_strategy", "viral_planning", "team_scaling"],
                "decision_frameworks": ["retention_optimization", "thumbnail_testing", "viral_mechanics"],
                "typical_engagement_duration": "1hour",
                "background": "Top-tier creator-economy operator; viral content design, retention optimization, and creator-team scaling.",
                "key_achievements": ["Built one of the largest video-platform channels", "Nine-figure annual creator-economy revenue", "Adjacent consumer-brand businesses launched off creator base"],
                "certifications": ["Self-taught", "Multi-year applied viral-content practice"]
            },

            # Negotiation & Leadership
            {
                "id": "chris_voss_advisor",
                "name": "Master Negotiation Specialist",
                "title": "Master Negotiation Specialist",
                "domain": AdvisorDomain.NEGOTIATION_STRATEGY,
                "expertise_level": AdvisorExpertiseLevel.LEGEND,
                "specializations": ["tactical_empathy", "negotiation", "crisis_management", "deal_making"],
                "years_experience": 24,
                "consultation_types": ["negotiation_strategy", "conflict_resolution", "deal_structuring"],
                "decision_frameworks": ["tactical_empathy", "mirroring", "calibrated_questions"],
                "typical_engagement_duration": "1.5hour",
                "background": "Former federal hostage negotiator; developed tactical-empathy and calibrated-question frameworks now standard in high-stakes deal-making.",
                "key_achievements": ["24 years of high-stakes federal negotiation experience", "International crisis-resolution case work", "Authored a defining negotiation reference"],
                "certifications": ["Federal hostage-negotiation training", "Top-tier law school negotiation coursework"]
            },

            # Healthcare & Biotech
            {
                "id": "dr_peter_attia_advisor",
                "name": "Longevity & Healthcare Strategist",
                "title": "Longevity & Healthcare Strategist",
                "domain": AdvisorDomain.HEALTHCARE_STRATEGY,
                "expertise_level": AdvisorExpertiseLevel.LEGEND,
                "specializations": ["longevity", "preventive_medicine", "biotech_investing", "health_optimization"],
                "years_experience": 20,
                "consultation_types": ["health_strategy", "biotech_analysis", "wellness_planning"],
                "decision_frameworks": ["evidence_based_medicine", "risk_stratification", "longevity_protocols"],
                "typical_engagement_duration": "1.5hour",
                "background": "Top-tier medical training combined with longevity research; advisor to biotech investors and healthcare-strategy teams.",
                "key_achievements": ["Leading practitioner in longevity protocols", "Founded a specialty medical practice", "Frequent biotech and health-strategy advisor"],
                "certifications": ["MD from a top-tier medical school", "Residency at a top-tier teaching hospital"]
            },

            # Cybersecurity
            {
                "id": "kevin_mitnick_advisor",
                "name": "Cybersecurity Operations Expert",
                "title": "Cybersecurity Operations Expert",
                "domain": AdvisorDomain.CYBERSECURITY,
                "expertise_level": AdvisorExpertiseLevel.LEGEND,
                "specializations": ["penetration_testing", "social_engineering", "security_architecture", "ethical_hacking"],
                "years_experience": 30,
                "consultation_types": ["security_audit", "vulnerability_assessment", "security_strategy"],
                "decision_frameworks": ["zero_trust", "defense_in_depth", "social_engineering_defense"],
                "typical_engagement_duration": "2hour",
                "background": "Former offensive-security practitioner turned long-tenured security consultant; specializes in penetration testing, social-engineering defense, and security architecture.",
                "key_achievements": ["Founded a security-consulting practice still operating today", "Long-standing reference voice in offensive-security training"],
                "certifications": ["Self-taught", "Multi-decade real-world security practice"]
            },

            # Education & Learning
            {
                "id": "sal_khan_advisor",
                "name": "Education Technology Pioneer",
                "title": "Education Technology Pioneer",
                "domain": AdvisorDomain.EDUCATION_STRATEGY,
                "expertise_level": AdvisorExpertiseLevel.LEGEND,
                "specializations": ["edtech", "personalized_learning", "online_education", "ai_tutoring"],
                "years_experience": 15,
                "consultation_types": ["education_strategy", "platform_development", "content_design"],
                "decision_frameworks": ["mastery_learning", "personalization", "gamification"],
                "typical_engagement_duration": "1hour",
                "background": "Founder-builder of a large global online learning platform; expert in mastery learning, AI tutoring, and education-platform design.",
                "key_achievements": ["Reached 100M+ students globally", "Built a foundational free-education platform", "Early operator in AI-tutoring product design"],
                "certifications": ["EECS degree from a top-tier engineering school", "MBA from a top-tier business school"]
            },

            # ── Session 1115: 5 advisors added to fill domains the routing
            # layer (advisor_context_builder.py) was already targeting but
            # had no advisor for. Each maps to one of the previously-orphan
            # AdvisorDomain enum values. See docs/AUDIT_FINDINGS.md #4.

            # Operations & Execution
            {
                "id": "tim_cook_advisor",
                "name": "Operations & Supply-Chain Strategist",
                "title": "Operations & Supply-Chain Strategist",
                "domain": AdvisorDomain.OPERATIONS_MANAGEMENT,
                "expertise_level": AdvisorExpertiseLevel.LEGEND,
                "specializations": ["supply_chain", "operational_excellence", "global_logistics", "scaling_operations"],
                "years_experience": 35,
                "consultation_types": ["operations_review", "scale_planning", "process_optimization"],
                "decision_frameworks": ["just_in_time", "lean_operations", "vertical_integration"],
                "typical_engagement_duration": "1.5hour",
                "background": "Chief executive at a global consumer-hardware company after rebuilding its supply chain to enable category-defining product launches.",
                "key_achievements": ["Scaled a global hardware company to multi-trillion market cap", "Built one of the world's most efficient supply chains", "Operational backbone for billions of device shipments"],
                "certifications": ["MBA from a top-tier business school", "Industrial Engineering undergraduate degree"]
            },

            # Data & Analytics
            {
                "id": "andrew_ng_advisor",
                "name": "Data Strategy & ML Practitioner",
                "title": "Data Strategy & ML Practitioner",
                "domain": AdvisorDomain.DATA_STRATEGY,
                "expertise_level": AdvisorExpertiseLevel.LEGEND,
                "specializations": ["data_centric_ai", "ml_strategy", "enterprise_data", "applied_ai"],
                "years_experience": 25,
                "consultation_types": ["data_strategy", "ml_roadmap", "model_review"],
                "decision_frameworks": ["data_centric_ai", "ml_yearning_principles", "minimum_viable_model"],
                "typical_engagement_duration": "1hour",
                "background": "Long-standing bridge between academic ML research and applied data strategy at scale; co-founded a major AI research lab and a leading online education platform; founded an applied-AI consultancy.",
                "key_achievements": ["Co-founded a major AI research lab", "Co-founded a leading online education platform", "Authored a defining ML practitioner reference", "Trained millions of ML practitioners globally"],
                "certifications": ["PhD Computer Science from a top-tier university", "MEng EECS", "Undergraduate degree from a top-tier engineering school"]
            },

            # Legal — Intellectual Property
            {
                "id": "ip_counsel_advisor",
                "name": "Senior Intellectual Property Counsel",
                "title": "Senior Intellectual Property Counsel",
                "domain": AdvisorDomain.INTELLECTUAL_PROPERTY,
                "expertise_level": AdvisorExpertiseLevel.MASTER,
                "specializations": ["patent_strategy", "trade_secret_protection", "trademark_portfolios", "ip_litigation"],
                "years_experience": 17,
                "consultation_types": ["ip_review", "portfolio_strategy", "infringement_assessment"],
                "decision_frameworks": ["claim_charting", "freedom_to_operate", "portfolio_valuation"],
                "typical_engagement_duration": "1hour",
                "background": "Former IP partner at a top-tier tech firm; advises platforms on patent strategy, trade-secret hygiene, and trademark portfolios; consumes legal-spider feeds (findlaw / courtlistener / justia) tagged `intellectual_property` for opposition / freedom-to-operate signals.",
                "key_achievements": ["Built 200+ patent portfolios", "Saved clients $50M+ in licensing exposure", "Lead counsel on 12 successful patent-defense actions"],
                "certifications": ["JD from a top-tier law school", "USPTO Registration", "AIPLA Fellow"]
            },

            # Leadership Development
            {
                "id": "leadership_dev_advisor",
                "name": "Executive Leadership Coach",
                "title": "Executive Leadership Coach",
                "domain": AdvisorDomain.LEADERSHIP_DEVELOPMENT,
                "expertise_level": AdvisorExpertiseLevel.MASTER,
                "specializations": ["executive_presence", "high_performance_teams", "transitions_to_leadership", "leader_as_coach"],
                "years_experience": 22,
                "consultation_types": ["leadership_coaching", "team_design", "succession_planning"],
                "decision_frameworks": ["leadership_circle_profile", "situational_leadership", "deliberate_practice"],
                "typical_engagement_duration": "1hour",
                "background": "Two-decade leadership-development practitioner. Pairs with the `career_coaching` advisor (which already lists leadership_development as a specialization) so `career` and `personal` task routing has a dedicated leadership match instead of falling through.",
                "key_achievements": ["Coached 60+ first-time CEOs into role", "Developed three Fortune-500 leadership-pipeline programs", "Built a leadership-assessment battery used by 10+ companies"],
                "certifications": ["ICF Master Certified Coach", "Hogan Assessment Certified", "Leadership Circle Profile Certified"]
            },

            # Regulatory Compliance
            {
                "id": "compliance_advisor",
                "name": "Regulatory & Compliance Strategist",
                "title": "Regulatory & Compliance Strategist",
                "domain": AdvisorDomain.REGULATORY_COMPLIANCE,
                "expertise_level": AdvisorExpertiseLevel.MASTER,
                "specializations": ["sec_compliance", "data_protection_gdpr_ccpa", "ai_governance", "financial_reporting"],
                "years_experience": 19,
                "consultation_types": ["compliance_audit", "policy_review", "regulator_engagement"],
                "decision_frameworks": ["three_lines_of_defense", "risk_based_compliance", "control_mapping"],
                "typical_engagement_duration": "1.5hour",
                "background": "Former Chief Compliance Officer at a publicly-traded fintech; routinely engages with SEC / FINRA on disclosure matters; partners with the `legal_counsel` advisor on legal tasks where the regulatory angle is the dominant risk.",
                "key_achievements": ["Zero material findings across 6 SEC examinations", "Built a GDPR program covering 12M users", "Authored an internal AI-governance framework now adopted across the parent group"],
                "certifications": ["JD from a top-tier law school", "CRCM", "CIPP/E", "FINRA Series 7/24"]
            }
        ]

        # Initialize advisor profiles
        for advisor_data in advisors_data:
            advisor = AdvisorProfile(
                id=advisor_data["id"],
                name=advisor_data["name"],
                title=advisor_data["title"],
                domain=advisor_data["domain"],
                expertise_level=advisor_data["expertise_level"],
                specializations=advisor_data["specializations"],
                years_experience=advisor_data["years_experience"],
                consultation_types=advisor_data["consultation_types"],
                decision_frameworks=advisor_data["decision_frameworks"],
                typical_engagement_duration=advisor_data["typical_engagement_duration"],
                background=advisor_data["background"],
                key_achievements=advisor_data["key_achievements"],
                certifications=advisor_data["certifications"],

                # Set reasonable defaults for other fields
                satisfaction_rating=4.7,  # High default rating
                total_consultations=50,   # Experienced
                success_rate=0.89,        # High success rate
                response_time_hours=6.0,  # Fast response

                availability_hours={
                    "monday": ["9-17"], "tuesday": ["9-17"], "wednesday": ["9-17"],
                    "thursday": ["9-17"], "friday": ["9-17"]
                },
                preferred_communication=["chat", "video", "email"],
                integrates_with_agents=True,
                preferred_agent_types=["research", "analysis", "planning"]
            )

            self.advisors[advisor.id] = advisor

        self.logger.info(f"Initialized advisor network with {len(self.advisors)} advisors")

    def get_advisor(self, advisor_id: str) -> Optional[AdvisorProfile]:
        """Get advisor by ID"""
        return self.advisors.get(advisor_id)

    def list_advisors(self,
                     domain: Optional[AdvisorDomain] = None,
                     expertise_level: Optional[AdvisorExpertiseLevel] = None,
                     specializations: Optional[List[str]] = None) -> List[AdvisorProfile]:
        """List advisors with optional filters"""
        advisors = list(self.advisors.values())

        if domain:
            advisors = [a for a in advisors if a.domain == domain]

        if expertise_level:
            advisors = [a for a in advisors if a.expertise_level == expertise_level]

        if specializations:
            advisors = [
                a for a in advisors
                if any(spec in a.specializations for spec in specializations)
            ]

        # Sort by expertise level and satisfaction rating
        expertise_order = {
            AdvisorExpertiseLevel.LEGEND: 4,
            AdvisorExpertiseLevel.MASTER: 3,
            AdvisorExpertiseLevel.EXPERT: 2,
            AdvisorExpertiseLevel.SPECIALIST: 1
        }

        advisors.sort(
            key=lambda a: (expertise_order[a.expertise_level], a.satisfaction_rating),
            reverse=True
        )

        return advisors

    def find_best_advisor(self,
                         consultation_topic: str,
                         domain: Optional[AdvisorDomain] = None,
                         required_specializations: Optional[List[str]] = None) -> Optional[AdvisorProfile]:
        """Find the best advisor for a specific consultation"""
        try:
            advisors = self.list_advisors(domain=domain, specializations=required_specializations)

            if not advisors:
                return None

            # Score advisors based on relevance
            scored_advisors = []
            topic_lower = consultation_topic.lower()

            for advisor in advisors:
                score = 0.0

                # Specialization match
                for spec in advisor.specializations:
                    if spec.replace('_', ' ') in topic_lower:
                        score += 10.0

                # Domain relevance
                if domain and advisor.domain == domain:
                    score += 15.0

                # Experience bonus
                experience_bonus = min(advisor.years_experience / 20, 1.0) * 5.0
                score += experience_bonus

                # Performance bonus
                score += advisor.satisfaction_rating * 2
                score += advisor.success_rate * 3

                # Response time bonus (faster = better)
                response_bonus = max(0, (48 - advisor.response_time_hours) / 48 * 2)
                score += response_bonus

                scored_advisors.append((advisor, score))

            # Sort by score and return best match
            scored_advisors.sort(key=lambda x: x[1], reverse=True)
            best_advisor = scored_advisors[0][0]

            self.logger.info(
                f"Selected advisor '{best_advisor.name}' "
                f"(score: {scored_advisors[0][1]:.2f}) for consultation on: {consultation_topic}"
            )

            return best_advisor

        except Exception as e:
            self.logger.error(f"Error finding best advisor: {e}")
            return None

    def request_consultation(self,
                           advisor_id: str,
                           user_id: str,
                           topic: str,
                           consultation_type: str = "strategy",
                           initial_request: str = "") -> Optional[str]:
        """Request a consultation with an advisor"""
        try:
            advisor = self.get_advisor(advisor_id)
            if not advisor:
                self.logger.error(f"Advisor {advisor_id} not found")
                return None

            consultation_id = f"consult_{advisor_id}_{user_id}_{int(datetime.now().timestamp())}"

            consultation = AdvisorConsultation(
                id=consultation_id,
                advisor_id=advisor_id,
                user_id=user_id,
                topic=topic,
                domain=advisor.domain,
                consultation_type=consultation_type,
                status="requested",
                initial_request=initial_request
            )

            self.consultations[consultation_id] = consultation

            self.logger.info(
                f"Requested consultation {consultation_id} with advisor {advisor.name}"
            )

            return consultation_id

        except Exception as e:
            self.logger.error(f"Failed to request consultation: {e}")
            return None

    def get_consultation(self, consultation_id: str) -> Optional[AdvisorConsultation]:
        """Get consultation by ID"""
        return self.consultations.get(consultation_id)

    def complete_consultation(self,
                            consultation_id: str,
                            recommendations: List[str],
                            action_items: List[str],
                            advisor_notes: str = "") -> bool:
        """Complete a consultation with recommendations"""
        try:
            consultation = self.get_consultation(consultation_id)
            if not consultation:
                return False

            consultation.status = "completed"
            consultation.completed_at = datetime.now()
            consultation.recommendations = recommendations
            consultation.action_items = action_items
            consultation.advisor_notes = advisor_notes

            # Update advisor metrics
            advisor = self.get_advisor(consultation.advisor_id)
            if advisor:
                advisor.total_consultations += 1

            self.logger.info(f"Completed consultation {consultation_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to complete consultation: {e}")
            return False

    def get_advisor_recommendations(self,
                                  topic: str,
                                  context: Dict[str, Any]) -> Dict[str, Any]:
        """Get AI-powered advisor recommendations based on topic and context"""
        try:
            # Find relevant advisors
            relevant_advisors = []

            topic_lower = topic.lower()
            context_str = str(context).lower()
            combined_text = f"{topic_lower} {context_str}"

            # Match advisors to topic
            for advisor in self.advisors.values():
                relevance_score = 0

                # Check specializations
                for spec in advisor.specializations:
                    if spec.replace('_', ' ') in combined_text:
                        relevance_score += 2

                # Check decision frameworks
                for framework in advisor.decision_frameworks:
                    if framework.replace('_', ' ') in combined_text:
                        relevance_score += 1

                if relevance_score > 0:
                    relevant_advisors.append({
                        'advisor': advisor,
                        'relevance_score': relevance_score
                    })

            # Sort by relevance and expertise
            relevant_advisors.sort(
                key=lambda x: (x['relevance_score'], x['advisor'].satisfaction_rating),
                reverse=True
            )

            # Return top recommendations
            recommendations = []
            for item in relevant_advisors[:5]:  # Top 5
                advisor = item['advisor']
                recommendations.append({
                    'advisor_id': advisor.id,
                    'name': advisor.name,
                    'title': advisor.title,
                    'domain': advisor.domain.value,
                    'expertise_level': advisor.expertise_level.value,
                    'specializations': advisor.specializations,
                    'satisfaction_rating': advisor.satisfaction_rating,
                    'typical_duration': advisor.typical_engagement_duration,
                    'relevance_score': item['relevance_score']
                })

            return {
                'topic': topic,
                'total_advisors_available': len(self.advisors),
                'relevant_advisors': len(relevant_advisors),
                'recommendations': recommendations,
                'suggested_consultation_type': self._suggest_consultation_type(topic)
            }

        except Exception as e:
            self.logger.error(f"Error getting advisor recommendations: {e}")
            return {'error': str(e)}

    def _suggest_consultation_type(self, topic: str) -> str:
        """Suggest consultation type based on topic"""
        topic_lower = topic.lower()

        if any(word in topic_lower for word in ['strategy', 'plan', 'direction']):
            return 'strategy'
        elif any(word in topic_lower for word in ['analyze', 'review', 'assess']):
            return 'analysis'
        elif any(word in topic_lower for word in ['decide', 'choose', 'option']):
            return 'decision_support'
        else:
            return 'strategy'  # Default

    def get_registry_stats(self) -> Dict[str, Any]:
        """Get comprehensive advisor registry statistics"""
        try:
            # Basic counts
            total_advisors = len(self.advisors)
            total_consultations = len(self.consultations)

            # Domain distribution
            domain_counts = {}
            expertise_counts = {}

            for advisor in self.advisors.values():
                domain = advisor.domain.value
                expertise = advisor.expertise_level.value

                domain_counts[domain] = domain_counts.get(domain, 0) + 1
                expertise_counts[expertise] = expertise_counts.get(expertise, 0) + 1

            # Calculate averages
            avg_satisfaction = sum(a.satisfaction_rating for a in self.advisors.values()) / total_advisors
            avg_success_rate = sum(a.success_rate for a in self.advisors.values()) / total_advisors
            avg_response_time = sum(a.response_time_hours for a in self.advisors.values()) / total_advisors

            # Consultation status counts
            consultation_statuses = {}
            for consultation in self.consultations.values():
                status = consultation.status
                consultation_statuses[status] = consultation_statuses.get(status, 0) + 1

            return {
                'total_advisors': total_advisors,
                'total_consultations': total_consultations,
                'domain_distribution': domain_counts,
                'expertise_distribution': expertise_counts,
                'avg_satisfaction_rating': round(avg_satisfaction, 2),
                'avg_success_rate': round(avg_success_rate, 2),
                'avg_response_time_hours': round(avg_response_time, 1),
                'consultation_statuses': consultation_statuses,
                'top_domains': sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            }

        except Exception as e:
            self.logger.error(f"Error calculating registry stats: {e}")
            return {'error': str(e)}


# Global advisor registry instance
_advisor_registry_instance = None

def get_advisor_registry() -> AdvisorRegistry:
    """Get the global advisor registry instance"""
    global _advisor_registry_instance
    if _advisor_registry_instance is None:
        _advisor_registry_instance = AdvisorRegistry()
    return _advisor_registry_instance


# Convenience functions
def get_advisor(advisor_id: str) -> Optional[AdvisorProfile]:
    """Get advisor by ID (convenience function)"""
    return get_advisor_registry().get_advisor(advisor_id)


def list_advisors(domain: AdvisorDomain = None) -> List[AdvisorProfile]:
    """List advisors (convenience function)"""
    return get_advisor_registry().list_advisors(domain=domain)


def find_best_advisor(topic: str, domain: AdvisorDomain = None) -> Optional[AdvisorProfile]:
    """Find best advisor for topic (convenience function)"""
    return get_advisor_registry().find_best_advisor(topic, domain=domain)


def request_consultation(advisor_id: str, user_id: str, topic: str, request: str = "") -> Optional[str]:
    """Request consultation (convenience function)"""
    return get_advisor_registry().request_consultation(advisor_id, user_id, topic, initial_request=request)


# Initialize the global registry
advisor_registry = get_advisor_registry()