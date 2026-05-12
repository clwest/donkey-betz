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
        """Initialize the comprehensive advisor network"""
        advisors_data = [
            # Financial & Investment Advisors
            {
                "id": "financial_strategist",
                "name": "Sarah Chen",
                "title": "Senior Financial Strategist",
                "domain": AdvisorDomain.FINANCIAL_PLANNING,
                "expertise_level": AdvisorExpertiseLevel.EXPERT,
                "specializations": ["wealth_building", "retirement_planning", "tax_optimization"],
                "years_experience": 12,
                "consultation_types": ["strategy", "analysis", "planning"],
                "decision_frameworks": ["goal_based_planning", "risk_assessment", "monte_carlo_analysis"],
                "typical_engagement_duration": "1hour",
                "background": "Former Goldman Sachs VP, specialized in high-net-worth financial planning",
                "key_achievements": ["Managed $500M in client assets", "20% average annual returns"],
                "certifications": ["CFA", "CFP", "CAIA"]
            },

            {
                "id": "crypto_expert",
                "name": "Marcus Rodriguez",
                "title": "Blockchain & Crypto Strategist",
                "domain": AdvisorDomain.CRYPTO_ANALYSIS,
                "expertise_level": AdvisorExpertiseLevel.MASTER,
                "specializations": ["defi_protocols", "nft_markets", "crypto_trading", "blockchain_tech"],
                "years_experience": 8,
                "consultation_types": ["analysis", "strategy", "review"],
                "decision_frameworks": ["fundamental_analysis", "technical_analysis", "on_chain_metrics"],
                "typical_engagement_duration": "45min",
                "background": "Early Bitcoin adopter, founded successful DeFi protocol, crypto fund manager",
                "key_achievements": ["500x returns on early investments", "Built $100M DeFi protocol"],
                "certifications": ["CBCP", "Blockchain Council Certified"]
            },

            {
                "id": "options_master",
                "name": "Jennifer Park",
                "title": "Options Trading Master",
                "domain": AdvisorDomain.OPTIONS_TRADING,
                "expertise_level": AdvisorExpertiseLevel.LEGEND,
                "specializations": ["volatility_trading", "risk_management", "exotic_options", "market_making"],
                "years_experience": 18,
                "consultation_types": ["strategy", "analysis", "risk_review"],
                "decision_frameworks": ["black_scholes", "volatility_modeling", "greeks_analysis"],
                "typical_engagement_duration": "1hour",
                "background": "Former head of options at major prop trading firm, pioneered volatility strategies",
                "key_achievements": ["Consistently profitable for 15 years", "Developed proprietary vol models"],
                "certifications": ["CMT", "Options Institute Graduate"]
            },

            # Business & Strategy Advisors
            {
                "id": "business_strategist",
                "name": "David Kim",
                "title": "Strategic Business Advisor",
                "domain": AdvisorDomain.BUSINESS_STRATEGY,
                "expertise_level": AdvisorExpertiseLevel.EXPERT,
                "specializations": ["growth_strategy", "market_expansion", "competitive_analysis", "m&a"],
                "years_experience": 14,
                "consultation_types": ["strategy", "planning", "review"],
                "decision_frameworks": ["porter_five_forces", "blue_ocean", "lean_startup"],
                "typical_engagement_duration": "1.5hour",
                "background": "Ex-McKinsey partner, helped scale 50+ startups to unicorn status",
                "key_achievements": ["20+ successful exits", "Built 3 companies from 0 to $100M"],
                "certifications": ["MBA Harvard", "Certified Management Consultant"]
            },

            {
                "id": "startup_guru",
                "name": "Lisa Thompson",
                "title": "Startup & Venture Advisor",
                "domain": AdvisorDomain.STARTUP_CONSULTING,
                "expertise_level": AdvisorExpertiseLevel.MASTER,
                "specializations": ["product_market_fit", "fundraising", "team_building", "scaling"],
                "years_experience": 16,
                "consultation_types": ["strategy", "review", "planning"],
                "decision_frameworks": ["lean_canvas", "jobs_to_be_done", "growth_accounting"],
                "typical_engagement_duration": "1hour",
                "background": "Serial entrepreneur, 3 exits, active angel investor and advisor",
                "key_achievements": ["Built $1B company", "50+ startup investments"],
                "certifications": ["Stanford Director Program", "Kauffman Fellows"]
            },

            # Technology Advisors
            {
                "id": "tech_architect",
                "name": "Alex Chen",
                "title": "Chief Technology Architect",
                "domain": AdvisorDomain.TECHNICAL_ARCHITECTURE,
                "expertise_level": AdvisorExpertiseLevel.MASTER,
                "specializations": ["system_design", "scalability", "cloud_architecture", "ai_integration"],
                "years_experience": 15,
                "consultation_types": ["architecture_review", "strategy", "technical_planning"],
                "decision_frameworks": ["domain_driven_design", "microservices", "cloud_native"],
                "typical_engagement_duration": "2hour",
                "background": "Ex-Google/Apple architect, built systems serving billions of users",
                "key_achievements": ["Scaled systems to 10B+ requests/day", "Led 200+ engineer teams"],
                "certifications": ["AWS Solutions Architect", "Google Cloud Architect"]
            },

            {
                "id": "ai_strategist",
                "name": "Dr. Priya Patel",
                "title": "AI & Machine Learning Strategist",
                "domain": AdvisorDomain.AI_ML_STRATEGY,
                "expertise_level": AdvisorExpertiseLevel.LEGEND,
                "specializations": ["deep_learning", "nlp", "computer_vision", "ml_ops"],
                "years_experience": 12,
                "consultation_types": ["strategy", "technical_review", "research_guidance"],
                "decision_frameworks": ["ai_readiness_assessment", "ml_lifecycle", "ethical_ai"],
                "typical_engagement_duration": "1.5hour",
                "background": "Former OpenAI researcher, PhD from Stanford, published 50+ papers",
                "key_achievements": ["Breakthrough in transformer architecture", "Built AI that generated $1B value"],
                "certifications": ["PhD Computer Science", "AI Ethics Certificate"]
            },

            # Specialized Domain Advisors
            {
                "id": "sports_analytics_expert",
                "name": "Mike Johnson",
                "title": "Sports Analytics & Betting Expert",
                "domain": AdvisorDomain.SPORTS_ANALYTICS,
                "expertise_level": AdvisorExpertiseLevel.MASTER,
                "specializations": ["predictive_modeling", "player_analysis", "betting_strategies", "data_science"],
                "years_experience": 10,
                "consultation_types": ["analysis", "strategy", "model_review"],
                "decision_frameworks": ["sabermetrics", "expected_value", "kelly_criterion"],
                "typical_engagement_duration": "45min",
                "background": "Former NBA analytics director, built winning betting models for major syndicates",
                "key_achievements": ["15% ROI over 8 years", "Predicted 3 major upsets"],
                "certifications": ["Sports Analytics Certificate", "Statistics PhD"]
            },

            {
                "id": "real_estate_mogul",
                "name": "Robert Wilson",
                "title": "Real Estate Investment Strategist",
                "domain": AdvisorDomain.REAL_ESTATE,
                "expertise_level": AdvisorExpertiseLevel.LEGEND,
                "specializations": ["investment_analysis", "market_timing", "commercial_real_estate", "reits"],
                "years_experience": 25,
                "consultation_types": ["investment_analysis", "strategy", "market_review"],
                "decision_frameworks": ["dcf_analysis", "cap_rate_analysis", "market_cycle_timing"],
                "typical_engagement_duration": "1hour",
                "background": "Built $2B real estate portfolio, survived 3 market cycles profitably",
                "key_achievements": ["20% annual returns for 25 years", "Never had losing year"],
                "certifications": ["CCIM", "Real Estate License", "MBA Wharton"]
            },

            # Legal & Compliance
            {
                "id": "legal_counsel",
                "name": "Amanda Davis",
                "title": "Corporate Legal Strategist",
                "domain": AdvisorDomain.LEGAL_COUNSEL,
                "expertise_level": AdvisorExpertiseLevel.EXPERT,
                "specializations": ["corporate_law", "securities_law", "contract_negotiation", "risk_mitigation"],
                "years_experience": 13,
                "consultation_types": ["legal_review", "risk_assessment", "strategy"],
                "decision_frameworks": ["legal_risk_matrix", "compliance_framework", "contract_analysis"],
                "typical_engagement_duration": "1hour",
                "background": "Partner at top law firm, specialized in tech/finance sectors",
                "key_achievements": ["Led $10B M&A deals", "Never lost a major case"],
                "certifications": ["JD Harvard Law", "Bar Admission NY/CA"]
            },

            # Personal Development
            {
                "id": "career_coach",
                "name": "Dr. Maria Gonzalez",
                "title": "Executive Career Strategist",
                "domain": AdvisorDomain.CAREER_COACHING,
                "expertise_level": AdvisorExpertiseLevel.MASTER,
                "specializations": ["executive_coaching", "leadership_development", "career_transitions", "negotiation"],
                "years_experience": 18,
                "consultation_types": ["coaching", "strategy", "development_planning"],
                "decision_frameworks": ["strengths_finder", "360_feedback", "career_pathing"],
                "typical_engagement_duration": "1hour",
                "background": "Former Fortune 500 CHRO, coached 100+ executives to C-suite",
                "key_achievements": ["95% promotion success rate", "Avg 40% salary increases"],
                "certifications": ["PhD Psychology", "ICF Master Coach", "SHRM-SCP"]
            },

            # Additional Legendary Advisors (14 more to reach 25 total)

            # Investment Legends
            {
                "id": "warren_buffett_advisor",
                "name": "Warren Buffett (AI Model)",
                "title": "Value Investing Legend",
                "domain": AdvisorDomain.INVESTMENT_STRATEGY,
                "expertise_level": AdvisorExpertiseLevel.LEGEND,
                "specializations": ["value_investing", "long_term_strategy", "fundamental_analysis", "moats"],
                "years_experience": 60,
                "consultation_types": ["strategy", "analysis", "portfolio_review"],
                "decision_frameworks": ["intrinsic_value", "margin_of_safety", "circle_of_competence"],
                "typical_engagement_duration": "2hour",
                "background": "Oracle of Omaha, Berkshire Hathaway CEO, legendary value investor",
                "key_achievements": ["20% annual returns for 50+ years", "$100B+ net worth"],
                "certifications": ["Columbia Business School", "60 years proven track record"]
            },

            {
                "id": "cathie_wood_advisor",
                "name": "Cathie Wood (AI Model)",
                "title": "Innovation Investment Strategist",
                "domain": AdvisorDomain.INVESTMENT_STRATEGY,
                "expertise_level": AdvisorExpertiseLevel.LEGEND,
                "specializations": ["disruptive_innovation", "growth_investing", "tech_stocks", "genomics"],
                "years_experience": 40,
                "consultation_types": ["strategy", "trend_analysis", "innovation_scouting"],
                "decision_frameworks": ["disruptive_innovation_theory", "wright_s_law", "convergence_analysis"],
                "typical_engagement_duration": "1.5hour",
                "background": "ARK Invest founder, pioneer in thematic investing",
                "key_achievements": ["Founded ARK Invest", "Early Tesla investor", "Innovation ETFs"],
                "certifications": ["USC Finance", "CFA Charter holder"]
            },

            {
                "id": "ray_dalio_advisor",
                "name": "Ray Dalio (AI Model)",
                "title": "Macro Economic Strategist",
                "domain": AdvisorDomain.RISK_MANAGEMENT,
                "expertise_level": AdvisorExpertiseLevel.LEGEND,
                "specializations": ["macro_economics", "risk_parity", "principles", "debt_cycles"],
                "years_experience": 45,
                "consultation_types": ["strategy", "risk_analysis", "economic_outlook"],
                "decision_frameworks": ["principles_based", "all_weather_portfolio", "economic_machine"],
                "typical_engagement_duration": "2hour",
                "background": "Bridgewater Associates founder, largest hedge fund in the world",
                "key_achievements": ["Built $150B hedge fund", "Predicted 2008 crisis", "All Weather strategy"],
                "certifications": ["Harvard MBA", "CFA"]
            },

            # Tech Titans
            {
                "id": "elon_musk_advisor",
                "name": "Elon Musk (AI Model)",
                "title": "Tech Innovation Visionary",
                "domain": AdvisorDomain.PRODUCT_DEVELOPMENT,
                "expertise_level": AdvisorExpertiseLevel.LEGEND,
                "specializations": ["first_principles", "exponential_thinking", "space_tech", "ai_future"],
                "years_experience": 25,
                "consultation_types": ["innovation_strategy", "product_vision", "scaling"],
                "decision_frameworks": ["first_principles_thinking", "exponential_growth", "vertical_integration"],
                "typical_engagement_duration": "1hour",
                "background": "Tesla, SpaceX, Neuralink founder, serial entrepreneur",
                "key_achievements": ["Built multiple $100B+ companies", "Revolutionized EVs and space"],
                "certifications": ["Physics degree", "Self-taught engineering"]
            },

            {
                "id": "sam_altman_advisor",
                "name": "Sam Altman (AI Model)",
                "title": "AI & Startup Strategy Expert",
                "domain": AdvisorDomain.AI_ML_STRATEGY,
                "expertise_level": AdvisorExpertiseLevel.LEGEND,
                "specializations": ["artificial_intelligence", "startup_scaling", "product_strategy", "agi"],
                "years_experience": 15,
                "consultation_types": ["ai_strategy", "startup_advice", "scaling"],
                "decision_frameworks": ["power_law_returns", "network_effects", "platform_thinking"],
                "typical_engagement_duration": "1hour",
                "background": "OpenAI CEO, former Y Combinator President",
                "key_achievements": ["Led OpenAI to ChatGPT", "Scaled YC to 1000+ companies"],
                "certifications": ["Stanford CS", "Y Combinator"]
            },

            # Marketing & Sales Legends
            {
                "id": "gary_vaynerchuk_advisor",
                "name": "Gary Vaynerchuk (AI Model)",
                "title": "Digital Marketing & Brand Expert",
                "domain": AdvisorDomain.MARKETING_STRATEGY,
                "expertise_level": AdvisorExpertiseLevel.LEGEND,
                "specializations": ["social_media", "brand_building", "content_marketing", "web3"],
                "years_experience": 20,
                "consultation_types": ["marketing_strategy", "brand_development", "content_planning"],
                "decision_frameworks": ["jab_jab_right_hook", "day_trading_attention", "brand_storytelling"],
                "typical_engagement_duration": "1hour",
                "background": "VaynerMedia CEO, serial entrepreneur, social media pioneer",
                "key_achievements": ["Built $200M agency", "Wine Library $60M", "NFT pioneer"],
                "certifications": ["Mount Ida College", "Self-made expertise"]
            },

            {
                "id": "grant_cardone_advisor",
                "name": "Grant Cardone (AI Model)",
                "title": "Sales & Real Estate Mogul",
                "domain": AdvisorDomain.SALES_OPTIMIZATION,
                "expertise_level": AdvisorExpertiseLevel.LEGEND,
                "specializations": ["sales_training", "real_estate", "10x_thinking", "closing_deals"],
                "years_experience": 30,
                "consultation_types": ["sales_strategy", "negotiation", "scaling"],
                "decision_frameworks": ["10x_rule", "aggressive_expansion", "massive_action"],
                "typical_engagement_duration": "1.5hour",
                "background": "Cardone Capital CEO, $4B real estate portfolio",
                "key_achievements": ["$4B AUM", "Bestselling author", "Sales training empire"],
                "certifications": ["McNeese State University", "Certified sales trainer"]
            },

            # Sports & Analytics
            {
                "id": "billy_beane_advisor",
                "name": "Billy Beane (AI Model)",
                "title": "Sports Analytics Pioneer",
                "domain": AdvisorDomain.SPORTS_ANALYTICS,
                "expertise_level": AdvisorExpertiseLevel.LEGEND,
                "specializations": ["sabermetrics", "value_finding", "data_driven_decisions", "moneyball"],
                "years_experience": 30,
                "consultation_types": ["analytics_strategy", "value_optimization", "team_building"],
                "decision_frameworks": ["moneyball", "statistical_arbitrage", "ops_optimization"],
                "typical_engagement_duration": "1.5hour",
                "background": "Oakland A's GM, Moneyball pioneer, revolutionized baseball",
                "key_achievements": ["20-game win streak", "Playoff appearances on minimum budget"],
                "certifications": ["UC San Diego", "MLB experience"]
            },

            {
                "id": "haralabos_voulgaris_advisor",
                "name": "Haralabos Voulgaris (AI Model)",
                "title": "Sports Betting Analytics Expert",
                "domain": AdvisorDomain.SPORTS_ANALYTICS,
                "expertise_level": AdvisorExpertiseLevel.LEGEND,
                "specializations": ["nba_analytics", "sports_betting", "predictive_modeling", "live_betting"],
                "years_experience": 20,
                "consultation_types": ["betting_strategy", "model_development", "bankroll_management"],
                "decision_frameworks": ["expected_value", "regression_models", "live_adjustments"],
                "typical_engagement_duration": "1hour",
                "background": "Professional sports bettor, Dallas Mavericks Director of Quantitative R&D",
                "key_achievements": ["Millions in betting profits", "NBA team analytics director"],
                "certifications": ["Self-taught", "Proven track record"]
            },

            # Content & Media
            {
                "id": "mr_beast_advisor",
                "name": "MrBeast (AI Model)",
                "title": "Content Creation & Viral Strategy",
                "domain": AdvisorDomain.CONTENT_STRATEGY,
                "expertise_level": AdvisorExpertiseLevel.LEGEND,
                "specializations": ["viral_content", "youtube_optimization", "retention_hacking", "scaling_content"],
                "years_experience": 10,
                "consultation_types": ["content_strategy", "viral_planning", "team_scaling"],
                "decision_frameworks": ["retention_optimization", "thumbnail_testing", "viral_mechanics"],
                "typical_engagement_duration": "1hour",
                "background": "YouTube's biggest creator, 200M+ subscribers, content empire",
                "key_achievements": ["Fastest growing channel", "$100M+ revenue", "Beast Burger"],
                "certifications": ["Self-taught", "YouTube pioneer"]
            },

            # Negotiation & Leadership
            {
                "id": "chris_voss_advisor",
                "name": "Chris Voss (AI Model)",
                "title": "Master Negotiator & FBI Lead",
                "domain": AdvisorDomain.NEGOTIATION_STRATEGY,
                "expertise_level": AdvisorExpertiseLevel.LEGEND,
                "specializations": ["tactical_empathy", "negotiation", "crisis_management", "deal_making"],
                "years_experience": 24,
                "consultation_types": ["negotiation_strategy", "conflict_resolution", "deal_structuring"],
                "decision_frameworks": ["tactical_empathy", "mirroring", "calibrated_questions"],
                "typical_engagement_duration": "1.5hour",
                "background": "Former FBI hostage negotiator, Black Swan Group founder",
                "key_achievements": ["24 years FBI", "International kidnapping cases", "Never Split the Difference"],
                "certifications": ["FBI Training", "Harvard Law negotiation"]
            },

            # Healthcare & Biotech
            {
                "id": "dr_peter_attia_advisor",
                "name": "Dr. Peter Attia (AI Model)",
                "title": "Longevity & Healthcare Strategy",
                "domain": AdvisorDomain.HEALTHCARE_STRATEGY,
                "expertise_level": AdvisorExpertiseLevel.LEGEND,
                "specializations": ["longevity", "preventive_medicine", "biotech_investing", "health_optimization"],
                "years_experience": 20,
                "consultation_types": ["health_strategy", "biotech_analysis", "wellness_planning"],
                "decision_frameworks": ["evidence_based_medicine", "risk_stratification", "longevity_protocols"],
                "typical_engagement_duration": "1.5hour",
                "background": "Stanford/Johns Hopkins trained, longevity expert, biotech advisor",
                "key_achievements": ["Leading longevity researcher", "Attia Medical PC founder"],
                "certifications": ["MD Stanford", "Johns Hopkins residency"]
            },

            # Cybersecurity
            {
                "id": "kevin_mitnick_advisor",
                "name": "Kevin Mitnick (AI Model)",
                "title": "Cybersecurity & Hacking Expert",
                "domain": AdvisorDomain.CYBERSECURITY,
                "expertise_level": AdvisorExpertiseLevel.LEGEND,
                "specializations": ["penetration_testing", "social_engineering", "security_architecture", "ethical_hacking"],
                "years_experience": 30,
                "consultation_types": ["security_audit", "vulnerability_assessment", "security_strategy"],
                "decision_frameworks": ["zero_trust", "defense_in_depth", "social_engineering_defense"],
                "typical_engagement_duration": "2hour",
                "background": "World's most famous hacker turned security consultant",
                "key_achievements": ["FBI most wanted", "Mitnick Security founder", "Security pioneer"],
                "certifications": ["Self-taught", "Real-world experience"]
            },

            # Education & Learning
            {
                "id": "sal_khan_advisor",
                "name": "Sal Khan (AI Model)",
                "title": "Education Technology Pioneer",
                "domain": AdvisorDomain.EDUCATION_STRATEGY,
                "expertise_level": AdvisorExpertiseLevel.LEGEND,
                "specializations": ["edtech", "personalized_learning", "online_education", "ai_tutoring"],
                "years_experience": 15,
                "consultation_types": ["education_strategy", "platform_development", "content_design"],
                "decision_frameworks": ["mastery_learning", "personalization", "gamification"],
                "typical_engagement_duration": "1hour",
                "background": "Khan Academy founder, revolutionized online education",
                "key_achievements": ["100M+ students taught", "Khan Academy platform", "AI education pioneer"],
                "certifications": ["MIT EECS", "Harvard MBA"]
            },

            # ── Session 1115: 5 advisors added to fill domains the routing
            # layer (advisor_context_builder.py) was already targeting but
            # had no advisor for. Each maps to one of the previously-orphan
            # AdvisorDomain enum values. See docs/AUDIT_FINDINGS.md #4.

            # Operations & Execution
            {
                "id": "tim_cook_advisor",
                "name": "Tim Cook (AI Model)",
                "title": "Operations & Supply-Chain Strategist",
                "domain": AdvisorDomain.OPERATIONS_MANAGEMENT,
                "expertise_level": AdvisorExpertiseLevel.LEGEND,
                "specializations": ["supply_chain", "operational_excellence", "global_logistics", "scaling_operations"],
                "years_experience": 35,
                "consultation_types": ["operations_review", "scale_planning", "process_optimization"],
                "decision_frameworks": ["just_in_time", "lean_operations", "vertical_integration"],
                "typical_engagement_duration": "1.5hour",
                "background": "Apple CEO; before that, Apple COO who rebuilt the supply chain that made the iPhone era possible",
                "key_achievements": ["Scaled Apple to $3T market cap", "Built world's most efficient supply chain", "Operational backbone of >2B device shipments"],
                "certifications": ["Duke Fuqua MBA", "Auburn Industrial Engineering"]
            },

            # Data & Analytics
            {
                "id": "andrew_ng_advisor",
                "name": "Andrew Ng (AI Model)",
                "title": "Data Strategy & ML Practitioner",
                "domain": AdvisorDomain.DATA_STRATEGY,
                "expertise_level": AdvisorExpertiseLevel.LEGEND,
                "specializations": ["data_centric_ai", "ml_strategy", "enterprise_data", "applied_ai"],
                "years_experience": 25,
                "consultation_types": ["data_strategy", "ml_roadmap", "model_review"],
                "decision_frameworks": ["data_centric_ai", "ml_yearning_principles", "minimum_viable_model"],
                "typical_engagement_duration": "1hour",
                "background": "Stanford CS faculty, Google Brain founder, Coursera co-founder, Landing AI founder — long-standing bridge between academic ML research and applied data strategy at scale",
                "key_achievements": ["Co-founded Google Brain", "Co-founded Coursera", "Authored Machine Learning Yearning", "Trained millions of ML practitioners globally"],
                "certifications": ["Stanford PhD CS", "MIT MEng EECS", "UC Berkeley BS"]
            },

            # Legal — Intellectual Property
            {
                "id": "ip_counsel_advisor",
                "name": "Priya Raman",
                "title": "Senior Intellectual Property Counsel",
                "domain": AdvisorDomain.INTELLECTUAL_PROPERTY,
                "expertise_level": AdvisorExpertiseLevel.MASTER,
                "specializations": ["patent_strategy", "trade_secret_protection", "trademark_portfolios", "ip_litigation"],
                "years_experience": 17,
                "consultation_types": ["ip_review", "portfolio_strategy", "infringement_assessment"],
                "decision_frameworks": ["claim_charting", "freedom_to_operate", "portfolio_valuation"],
                "typical_engagement_duration": "1hour",
                "background": "Former IP partner at top-tier tech firm; advises platforms on patent strategy, trade-secret hygiene, and trademark portfolios; consumes legal-spider feeds (findlaw / courtlistener / justia) tagged `intellectual_property` for opposition / freedom-to-operate signals",
                "key_achievements": ["Built 200+ patent portfolios", "Saved clients $50M in licensing exposure", "Lead counsel on 12 successful patent-defense actions"],
                "certifications": ["JD Berkeley Law", "USPTO Reg #", "AIPLA Fellow"]
            },

            # Leadership Development
            {
                "id": "leadership_dev_advisor",
                "name": "Marcus Whitfield",
                "title": "Executive Leadership Coach",
                "domain": AdvisorDomain.LEADERSHIP_DEVELOPMENT,
                "expertise_level": AdvisorExpertiseLevel.MASTER,
                "specializations": ["executive_presence", "high_performance_teams", "transitions_to_leadership", "leader_as_coach"],
                "years_experience": 22,
                "consultation_types": ["leadership_coaching", "team_design", "succession_planning"],
                "decision_frameworks": ["leadership_circle_profile", "situational_leadership", "deliberate_practice"],
                "typical_engagement_duration": "1hour",
                "background": "Two-decade leadership-development practitioner. Pairs with `career_coaching` advisor Dr. Maria Gonzalez (who already lists leadership_development as a specialization) so `career` and `personal` task routing has a dedicated leadership match instead of falling through.",
                "key_achievements": ["Coached 60+ first-time CEOs into role", "Developed three Fortune-500 leadership-pipeline programs", "Built leadership-assessment battery used by 10+ companies"],
                "certifications": ["ICF Master Certified Coach", "Hogan Assessment Certified", "Leadership Circle Profile Certified"]
            },

            # Regulatory Compliance
            {
                "id": "compliance_advisor",
                "name": "Eleanor Park",
                "title": "Regulatory & Compliance Strategist",
                "domain": AdvisorDomain.REGULATORY_COMPLIANCE,
                "expertise_level": AdvisorExpertiseLevel.MASTER,
                "specializations": ["sec_compliance", "data_protection_gdpr_ccpa", "ai_governance", "financial_reporting"],
                "years_experience": 19,
                "consultation_types": ["compliance_audit", "policy_review", "regulator_engagement"],
                "decision_frameworks": ["three_lines_of_defense", "risk_based_compliance", "control_mapping"],
                "typical_engagement_duration": "1.5hour",
                "background": "Former Chief Compliance Officer at a publicly-traded fintech; routinely engages with SEC / FINRA on disclosure matters; partners with `legal_counsel` (Amanda Davis) on legal tasks where the regulatory angle is the dominant risk",
                "key_achievements": ["Zero material findings across 6 SEC examinations", "Built GDPR program covering 12M users", "Authored internal AI-governance framework now adopted across the parent group"],
                "certifications": ["JD NYU Law", "CRCM", "CIPP/E", "FINRA Series 7/24"]
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