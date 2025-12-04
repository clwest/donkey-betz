"""
Test Scenarios for Business Research Agents
============================================

Session 334: Comprehensive test scenarios to push the CompetitorAnalysisAgent
and CustomerResearchAgent to their limits with realistic business contexts.

These scenarios cover diverse industries, company sizes, and complexity levels
to thoroughly test the agent ecosystem.

Usage:
    from core.testing.test_scenarios import TEST_SCENARIOS, get_scenario, get_scenarios_by_industry
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class Industry(Enum):
    """Industry categories for test scenarios."""
    AI_TECH = "ai_tech"
    SAAS = "saas"
    ECOMMERCE = "ecommerce"
    FOOD_BEVERAGE = "food_beverage"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    FINANCE = "finance"
    CREATIVE = "creative"
    MANUFACTURING = "manufacturing"
    REAL_ESTATE = "real_estate"
    FITNESS = "fitness"
    MEDIA = "media"
    SUSTAINABILITY = "sustainability"
    LEGAL = "legal"
    TRAVEL = "travel"


class Complexity(Enum):
    """Complexity level of the competitive landscape."""
    LOW = "low"        # Few competitors, simple market
    MEDIUM = "medium"  # Moderate competition
    HIGH = "high"      # Many competitors, complex dynamics


class CompanySize(Enum):
    """Company size categories."""
    SOLO = "solo"           # 1 person
    MICRO = "micro"         # 2-10
    SMALL = "small"         # 11-50
    MEDIUM = "medium"       # 51-200
    LARGE = "large"         # 201-1000
    ENTERPRISE = "enterprise"  # 1000+


@dataclass
class TestScenario:
    """A complete test scenario for business research agents."""

    # Basic Info
    id: str
    name: str
    industry: Industry
    complexity: Complexity
    company_size: CompanySize

    # Company Details
    company_name: str
    company_description: str
    location: str
    founded_year: int

    # Business Context
    business_model: str
    target_market: str
    unique_value_proposition: str
    current_challenges: List[str]

    # Test Queries
    competitor_analysis_query: str
    customer_research_query: str
    market_analysis_query: str

    # Expected Results (for validation)
    expected_competitors: List[str]
    expected_pain_points: List[str]
    expected_customer_segments: List[str]
    target_subreddits: List[str]

    # Metadata
    tags: List[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert scenario to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "industry": self.industry.value,
            "complexity": self.complexity.value,
            "company_size": self.company_size.value,
            "company_name": self.company_name,
            "company_description": self.company_description,
            "location": self.location,
            "founded_year": self.founded_year,
            "business_model": self.business_model,
            "target_market": self.target_market,
            "unique_value_proposition": self.unique_value_proposition,
            "current_challenges": self.current_challenges,
            "competitor_analysis_query": self.competitor_analysis_query,
            "customer_research_query": self.customer_research_query,
            "market_analysis_query": self.market_analysis_query,
            "expected_competitors": self.expected_competitors,
            "expected_pain_points": self.expected_pain_points,
            "expected_customer_segments": self.expected_customer_segments,
            "target_subreddits": self.target_subreddits,
            "tags": self.tags,
            "notes": self.notes,
        }


# =============================================================================
# TEST SCENARIOS
# =============================================================================

TEST_SCENARIOS: List[TestScenario] = [

    # =========================================================================
    # AI & TECH SCENARIOS
    # =========================================================================

    TestScenario(
        id="ai-podcast-tools",
        name="AI Podcast Production Platform",
        industry=Industry.AI_TECH,
        complexity=Complexity.HIGH,
        company_size=CompanySize.SMALL,
        company_name="PodcastAI Pro",
        company_description="AI-powered platform for podcast creators that automates editing, generates transcripts, creates clips, and handles distribution",
        location="Austin, TX",
        founded_year=2024,
        business_model="SaaS subscription ($29-199/month)",
        target_market="Independent podcasters, podcast networks, and content creators",
        unique_value_proposition="One-click AI editing that reduces production time from hours to minutes",
        current_challenges=[
            "Competing against well-funded players like Descript",
            "Building trust with creators who are skeptical of AI quality",
            "Balancing automation with creative control",
        ],
        competitor_analysis_query="Analyze competitors in AI podcast editing, transcription, and clip generation tools. Include Descript, Opus Clip, Podcastle, Riverside, and emerging startups.",
        customer_research_query="Research pain points of podcast creators with current editing software. What frustrates them about their workflow? What features are they asking for?",
        market_analysis_query="Analyze the podcast tools market - size, growth trends, and opportunities for AI-native solutions",
        expected_competitors=["Descript", "Opus Clip", "Podcastle", "Riverside", "Adobe Podcast", "Auphonic", "Cleanvoice"],
        expected_pain_points=["editing takes too long", "transcription accuracy", "filler word removal", "audio quality issues", "clip creation manual work"],
        expected_customer_segments=["Solo podcasters", "Podcast networks", "Video-first creators repurposing to audio"],
        target_subreddits=["podcasting", "podcasts", "audioengineering", "Audiomemes", "VoiceActing"],
        tags=["ai", "audio", "creator-economy", "saas"],
    ),

    TestScenario(
        id="ai-writing-assistant",
        name="AI Writing Assistant for Marketers",
        industry=Industry.AI_TECH,
        complexity=Complexity.HIGH,
        company_size=CompanySize.MEDIUM,
        company_name="CopyGenius",
        company_description="AI writing assistant specialized for marketing teams - generates ad copy, email campaigns, landing pages, and social media content",
        location="San Francisco, CA",
        founded_year=2023,
        business_model="SaaS with usage-based pricing ($49-499/month)",
        target_market="Marketing teams at SMBs and agencies",
        unique_value_proposition="Brand voice training - learns your company's style and maintains consistency across all content",
        current_challenges=[
            "Jasper and Copy.ai have massive market share",
            "ChatGPT commoditizing basic writing features",
            "Proving ROI to marketing leaders",
        ],
        competitor_analysis_query="Analyze competitors in AI writing and copywriting tools for marketing teams. Compare Jasper, Copy.ai, Writer, Writesonic, and others.",
        customer_research_query="Research what marketing teams struggle with when using AI writing tools. What makes them abandon tools? What features are must-haves?",
        market_analysis_query="Analyze the AI copywriting market - is it saturated? Where are the gaps?",
        expected_competitors=["Jasper", "Copy.ai", "Writer", "Writesonic", "Rytr", "Anyword", "Persado"],
        expected_pain_points=["generic output", "brand voice inconsistency", "fact-checking needed", "team collaboration", "too many tools"],
        expected_customer_segments=["Marketing managers", "Content teams", "Agency copywriters", "Solo marketers"],
        target_subreddits=["marketing", "copywriting", "digital_marketing", "PPC", "content_marketing"],
        tags=["ai", "marketing", "saas", "content"],
    ),

    TestScenario(
        id="ai-code-review",
        name="AI Code Review Platform",
        industry=Industry.AI_TECH,
        complexity=Complexity.HIGH,
        company_size=CompanySize.SMALL,
        company_name="CodeSensei",
        company_description="AI-powered code review tool that integrates with GitHub/GitLab to automatically review PRs, suggest improvements, and catch bugs",
        location="Seattle, WA",
        founded_year=2024,
        business_model="SaaS per-seat pricing ($15-50/developer/month)",
        target_market="Engineering teams at tech companies",
        unique_value_proposition="Context-aware reviews that understand your codebase architecture and coding standards",
        current_challenges=[
            "GitHub Copilot expanding into code review",
            "Security and IP concerns with sending code to AI",
            "Integration complexity with existing CI/CD",
        ],
        competitor_analysis_query="Analyze competitors in AI code review and code quality tools. Include GitHub Copilot, Codacy, SonarQube, DeepCode, and Sourcery.",
        customer_research_query="Research developer pain points with code review processes. What slows them down? What do they wish automated code review could do?",
        market_analysis_query="Analyze the developer tools market for AI-assisted code quality",
        expected_competitors=["GitHub Copilot", "Codacy", "SonarQube", "DeepCode", "Sourcery", "CodeClimate", "Snyk"],
        expected_pain_points=["slow review cycles", "inconsistent feedback", "missing context", "too many false positives", "security blind spots"],
        expected_customer_segments=["Engineering leads", "DevOps teams", "Security-conscious enterprises"],
        target_subreddits=["programming", "webdev", "devops", "softwaredevelopment", "learnprogramming"],
        tags=["ai", "developer-tools", "saas", "devops"],
    ),

    # =========================================================================
    # SAAS SCENARIOS
    # =========================================================================

    TestScenario(
        id="invoicing-freelancers",
        name="Invoicing Platform for Freelancers",
        industry=Industry.SAAS,
        complexity=Complexity.MEDIUM,
        company_size=CompanySize.MICRO,
        company_name="FreelanceFlow",
        company_description="Simple invoicing and payment tracking for freelancers and solopreneurs - send invoices, track payments, manage clients",
        location="Denver, CO",
        founded_year=2024,
        business_model="Freemium SaaS ($0-29/month)",
        target_market="Freelance designers, developers, writers, and consultants",
        unique_value_proposition="Built specifically for solo freelancers - no enterprise bloat, just what you need",
        current_challenges=[
            "FreshBooks and Wave dominate the market",
            "Stripe and PayPal adding invoicing features",
            "Price sensitivity of freelancer market",
        ],
        competitor_analysis_query="Analyze competitors in invoicing and billing software for freelancers. Compare FreshBooks, Wave, Bonsai, HoneyBook, and simpler tools.",
        customer_research_query="Research freelancer pain points with invoicing and getting paid. What features are missing? What frustrates them about current tools?",
        market_analysis_query="Analyze the freelancer tools market - invoicing segment specifically",
        expected_competitors=["FreshBooks", "Wave", "Bonsai", "HoneyBook", "AND.CO", "Harvest", "Zoho Invoice"],
        expected_pain_points=["late payments", "chasing invoices", "complex pricing", "too many features", "payment processing fees"],
        expected_customer_segments=["Freelance developers", "Freelance designers", "Consultants", "Coaches"],
        target_subreddits=["freelance", "Upwork", "freelanceWriters", "DesignJobs", "consulting"],
        tags=["saas", "freelance", "fintech", "productivity"],
    ),

    TestScenario(
        id="project-management-agencies",
        name="Project Management for Creative Agencies",
        industry=Industry.SAAS,
        complexity=Complexity.MEDIUM,
        company_size=CompanySize.SMALL,
        company_name="AgencyOS",
        company_description="Project management platform built for creative agencies - client collaboration, time tracking, resource planning, and profitability tracking",
        location="Brooklyn, NY",
        founded_year=2023,
        business_model="SaaS subscription ($99-499/month based on team size)",
        target_market="Creative agencies, design studios, and marketing agencies with 5-50 employees",
        unique_value_proposition="Built by agency owners for agency owners - tracks what actually matters: client happiness and project profitability",
        current_challenges=[
            "Monday.com and Asana are versatile alternatives",
            "Agencies resistant to switching from spreadsheets",
            "Need to prove ROI quickly",
        ],
        competitor_analysis_query="Analyze competitors in project management tools for creative agencies. Compare Monday.com, Asana, Teamwork, Productive.io, and agency-specific tools.",
        customer_research_query="Research what creative agency owners struggle with in project management. What do they track? What falls through the cracks?",
        market_analysis_query="Analyze the agency project management market - what's different about agency needs?",
        expected_competitors=["Monday.com", "Asana", "Teamwork", "Productive.io", "Wrike", "Float", "Harvest Forecast"],
        expected_pain_points=["scope creep", "resource allocation", "profitability visibility", "client communication", "time tracking adoption"],
        expected_customer_segments=["Agency owners", "Project managers", "Creative directors", "Operations managers"],
        target_subreddits=["agencies", "marketing", "graphic_design", "web_design", "Entrepreneur"],
        tags=["saas", "agency", "project-management", "productivity"],
    ),

    # =========================================================================
    # E-COMMERCE SCENARIOS
    # =========================================================================

    TestScenario(
        id="dtc-sustainable-apparel",
        name="Sustainable Apparel DTC Brand",
        industry=Industry.ECOMMERCE,
        complexity=Complexity.MEDIUM,
        company_size=CompanySize.SMALL,
        company_name="EcoThreads",
        company_description="Direct-to-consumer sustainable clothing brand using recycled materials and ethical manufacturing",
        location="Portland, OR",
        founded_year=2022,
        business_model="E-commerce DTC with 60% gross margins",
        target_market="Environmentally conscious millennials and Gen Z, ages 25-40",
        unique_value_proposition="Full supply chain transparency - track every garment from recycled material to your closet",
        current_challenges=[
            "Rising customer acquisition costs",
            "Competing with fast fashion on price",
            "Proving sustainability claims authentically",
        ],
        competitor_analysis_query="Analyze competitors in sustainable and eco-friendly apparel. Compare Patagonia, Everlane, Reformation, Allbirds, and indie sustainable brands.",
        customer_research_query="Research what sustainable fashion consumers care about. How do they evaluate sustainability claims? What makes them buy or not buy?",
        market_analysis_query="Analyze the sustainable fashion market - growth, consumer trends, and greenwashing concerns",
        expected_competitors=["Patagonia", "Everlane", "Reformation", "Allbirds", "Pact", "Tentree", "Girlfriend Collective"],
        expected_pain_points=["greenwashing skepticism", "higher prices", "limited styles", "durability concerns", "sizing inconsistency"],
        expected_customer_segments=["Eco-conscious millennials", "Minimalists", "Outdoor enthusiasts", "Ethical shoppers"],
        target_subreddits=["sustainability", "ethicalfashion", "zerowaste", "BuyItForLife", "femalefashionadvice"],
        tags=["ecommerce", "dtc", "sustainability", "fashion"],
    ),

    TestScenario(
        id="pet-supplements",
        name="Premium Pet Supplements Brand",
        industry=Industry.ECOMMERCE,
        complexity=Complexity.MEDIUM,
        company_size=CompanySize.MICRO,
        company_name="PupVitality",
        company_description="Premium supplements for dogs - joint health, digestion, skin & coat, made with human-grade ingredients",
        location="Boulder, CO",
        founded_year=2023,
        business_model="Subscription e-commerce with 70% LTV/CAC",
        target_market="Health-conscious dog owners who spend premium on pet care",
        unique_value_proposition="Vet-formulated with clinical dosing - not just sprinkles of ingredients for marketing",
        current_challenges=[
            "Amazon flooded with cheap alternatives",
            "Building trust for ingestible products",
            "Subscription fatigue among consumers",
        ],
        competitor_analysis_query="Analyze competitors in dog supplements and pet wellness. Compare Zesty Paws, PetHonesty, NutraVet, and premium brands.",
        customer_research_query="Research dog owner pain points with pet supplements. What are they skeptical about? What would make them trust a new brand?",
        market_analysis_query="Analyze the pet supplements market - trends in premiumization and health-conscious pet parents",
        expected_competitors=["Zesty Paws", "PetHonesty", "Nutramax", "VetriScience", "Native Pet", "The Honest Kitchen"],
        expected_pain_points=["unclear ingredients", "no visible results", "dogs won't eat them", "too many pills", "vet skepticism"],
        expected_customer_segments=["Health-conscious pet parents", "Senior dog owners", "Dog sport enthusiasts"],
        target_subreddits=["dogs", "DogFood", "dogcare", "Pets", "AskVet"],
        tags=["ecommerce", "pets", "health", "subscription"],
    ),

    # =========================================================================
    # FOOD & BEVERAGE SCENARIOS
    # =========================================================================

    TestScenario(
        id="specialty-coffee-chain",
        name="Specialty Coffee Chain",
        industry=Industry.FOOD_BEVERAGE,
        complexity=Complexity.MEDIUM,
        company_size=CompanySize.SMALL,
        company_name="Third Wave Roasters",
        company_description="Specialty coffee roaster and cafe chain focused on single-origin beans and transparent sourcing",
        location="Denver, CO",
        founded_year=2019,
        business_model="Retail cafes (5 locations) + wholesale to restaurants + e-commerce beans",
        target_market="Coffee enthusiasts, remote workers, specialty coffee drinkers ages 25-45",
        unique_value_proposition="Farm-direct relationships with transparent pricing to farmers",
        current_challenges=[
            "Starbucks Reserve competing in specialty",
            "Rising rent and labor costs",
            "Scaling quality across locations",
        ],
        competitor_analysis_query="Analyze competitors in specialty coffee in Denver. Compare local roasters, regional chains, and Starbucks Reserve approach.",
        customer_research_query="Research what specialty coffee drinkers value in a coffee shop. What makes them regulars? What drives them away?",
        market_analysis_query="Analyze the specialty coffee market - third wave trends and post-pandemic café culture",
        expected_competitors=["Starbucks Reserve", "Blue Bottle", "Intelligentsia", "Huckleberry Roasters", "Corvus Coffee"],
        expected_pain_points=["inconsistent quality", "pretentious atmosphere", "slow service", "high prices", "limited food options"],
        expected_customer_segments=["Coffee connoisseurs", "Remote workers", "Brunch crowds", "Commuters"],
        target_subreddits=["Coffee", "espresso", "roasting", "Denver", "cafe"],
        tags=["food-bev", "retail", "local-business", "coffee"],
    ),

    TestScenario(
        id="meal-prep-delivery",
        name="Athlete Meal Prep Delivery",
        industry=Industry.FOOD_BEVERAGE,
        complexity=Complexity.MEDIUM,
        company_size=CompanySize.SMALL,
        company_name="FuelPro Meals",
        company_description="Meal prep delivery service for athletes and fitness enthusiasts - macro-balanced, performance-optimized meals",
        location="Phoenix, AZ",
        founded_year=2022,
        business_model="Weekly subscription meal delivery ($12-18 per meal)",
        target_market="Competitive athletes, CrossFit enthusiasts, bodybuilders, and busy fitness-focused professionals",
        unique_value_proposition="Meals designed by sports nutritionists with customizable macros for specific training goals",
        current_challenges=[
            "Competing with national players like Factor and Trifecta",
            "Cold chain logistics for fresh meals",
            "Customer churn after reaching fitness goals",
        ],
        competitor_analysis_query="Analyze competitors in athlete and fitness meal prep delivery. Compare Factor, Trifecta, Freshly, and local meal prep companies.",
        customer_research_query="Research what athletes and fitness enthusiasts want from meal prep services. What makes them stick vs churn?",
        market_analysis_query="Analyze the meal prep delivery market - is it oversaturated? What segments are underserved?",
        expected_competitors=["Factor", "Trifecta", "Freshly", "Territory Foods", "Snap Kitchen", "Icon Meals"],
        expected_pain_points=["boring flavors", "portion sizes", "delivery reliability", "macro accuracy", "price per meal"],
        expected_customer_segments=["CrossFit athletes", "Bodybuilders", "Busy professionals", "Weight loss focused"],
        target_subreddits=["MealPrepSunday", "fitness", "bodybuilding", "crossfit", "nutrition"],
        tags=["food-bev", "fitness", "subscription", "delivery"],
    ),

    # =========================================================================
    # HEALTHCARE SCENARIOS
    # =========================================================================

    TestScenario(
        id="telehealth-mental-health",
        name="Telehealth Mental Health Platform",
        industry=Industry.HEALTHCARE,
        complexity=Complexity.HIGH,
        company_size=CompanySize.MEDIUM,
        company_name="MindBridge Health",
        company_description="Telehealth platform connecting patients with licensed therapists for video, phone, and chat therapy sessions",
        location="Boston, MA",
        founded_year=2021,
        business_model="B2C subscriptions + B2B employer partnerships",
        target_market="Adults seeking mental health support, especially those with insurance coverage",
        unique_value_proposition="Insurance-first approach - we handle the billing so patients pay only their copay",
        current_challenges=[
            "BetterHelp and Talkspace have massive brand awareness",
            "Therapist supply constraints",
            "Insurance reimbursement complexity",
        ],
        competitor_analysis_query="Analyze competitors in telehealth therapy and mental health platforms. Compare BetterHelp, Talkspace, Cerebral, Headway, and Alma.",
        customer_research_query="Research what people look for when choosing online therapy. What are their concerns? What makes them trust a platform?",
        market_analysis_query="Analyze the digital mental health market - growth post-pandemic and insurance adoption trends",
        expected_competitors=["BetterHelp", "Talkspace", "Cerebral", "Headway", "Alma", "Lyra Health", "Spring Health"],
        expected_pain_points=["therapist matching", "insurance confusion", "high costs", "waitlists", "impersonal experience"],
        expected_customer_segments=["Anxiety/depression patients", "Working professionals", "Students", "HR benefits managers"],
        target_subreddits=["therapy", "mentalhealth", "anxiety", "depression", "TalkTherapy"],
        tags=["healthcare", "telehealth", "mental-health", "saas"],
    ),

    # =========================================================================
    # EDUCATION SCENARIOS
    # =========================================================================

    TestScenario(
        id="coding-bootcamp",
        name="AI/ML Coding Bootcamp",
        industry=Industry.EDUCATION,
        complexity=Complexity.HIGH,
        company_size=CompanySize.SMALL,
        company_name="MLPath Academy",
        company_description="Online bootcamp teaching practical AI/ML skills with project-based curriculum and career services",
        location="Remote-first (HQ: Austin, TX)",
        founded_year=2023,
        business_model="Cohort-based bootcamp ($8,000-15,000) with ISA option",
        target_market="Career changers and developers looking to break into AI/ML",
        unique_value_proposition="Learn by building real AI products - not just theory. Graduate with a portfolio of deployed ML projects.",
        current_challenges=[
            "Free resources like fast.ai and Coursera",
            "Proving job placement success",
            "AI changing faster than curriculum",
        ],
        competitor_analysis_query="Analyze competitors in AI/ML bootcamps and education. Compare General Assembly, Springboard, DataCamp, fast.ai, and university programs.",
        customer_research_query="Research what people considering AI/ML bootcamps are looking for. What scares them? What would convince them to enroll?",
        market_analysis_query="Analyze the AI education market - who is paying for AI training and why?",
        expected_competitors=["General Assembly", "Springboard", "DataCamp", "Coursera", "Udacity", "fast.ai", "DeepLearning.AI"],
        expected_pain_points=["job placement uncertainty", "cost justification", "time commitment", "outdated curriculum", "too theoretical"],
        expected_customer_segments=["Career changers", "Software developers upskilling", "Data analysts", "Recent graduates"],
        target_subreddits=["learnmachinelearning", "MachineLearning", "cscareerquestions", "datascience", "learnprogramming"],
        tags=["education", "ai", "bootcamp", "career"],
    ),

    # =========================================================================
    # FINANCE SCENARIOS
    # =========================================================================

    TestScenario(
        id="crypto-tax-software",
        name="Crypto Tax Software",
        industry=Industry.FINANCE,
        complexity=Complexity.HIGH,
        company_size=CompanySize.SMALL,
        company_name="CryptoTaxPro",
        company_description="Automated cryptocurrency tax reporting software that connects to exchanges and wallets to generate IRS-compliant reports",
        location="Miami, FL",
        founded_year=2021,
        business_model="Annual subscription ($49-299 based on transaction volume)",
        target_market="Crypto traders, DeFi users, and NFT collectors needing tax compliance",
        unique_value_proposition="Full DeFi support - handles yield farming, liquidity pools, and complex transactions that other tools miss",
        current_challenges=[
            "CoinTracker and Koinly are established leaders",
            "Constantly changing DeFi protocols",
            "IRS guidance keeps evolving",
        ],
        competitor_analysis_query="Analyze competitors in cryptocurrency tax software. Compare CoinTracker, Koinly, TaxBit, CryptoTrader.Tax, and ZenLedger.",
        customer_research_query="Research crypto trader pain points with tax reporting. What do they struggle with? What features are missing from current tools?",
        market_analysis_query="Analyze the crypto tax software market - growth with IRS enforcement and DeFi complexity",
        expected_competitors=["CoinTracker", "Koinly", "TaxBit", "TokenTax", "ZenLedger", "CryptoTrader.Tax"],
        expected_pain_points=["DeFi tracking", "exchange API issues", "cost basis accuracy", "too complex", "missing transactions"],
        expected_customer_segments=["Active traders", "DeFi farmers", "NFT collectors", "CPAs serving crypto clients"],
        target_subreddits=["CryptoCurrency", "defi", "CryptoTax", "tax", "Bitcoin"],
        tags=["fintech", "crypto", "tax", "saas"],
    ),

    # =========================================================================
    # CREATIVE SCENARIOS
    # =========================================================================

    TestScenario(
        id="video-production-agency",
        name="Corporate Video Production Agency",
        industry=Industry.CREATIVE,
        complexity=Complexity.LOW,
        company_size=CompanySize.MICRO,
        company_name="FrameStory Studios",
        company_description="Video production agency specializing in corporate brand videos, product demos, and internal communications",
        location="Chicago, IL",
        founded_year=2020,
        business_model="Project-based pricing ($5,000-50,000 per video)",
        target_market="B2B companies needing professional video content for marketing and internal use",
        unique_value_proposition="Fast turnaround with remote-first production - concept to delivery in 2-3 weeks",
        current_challenges=[
            "Race to the bottom on pricing from freelancers",
            "AI video tools threatening simpler projects",
            "Building recurring revenue vs one-off projects",
        ],
        competitor_analysis_query="Analyze competitors in corporate video production. Compare traditional agencies, freelance videographers, and AI video tools.",
        customer_research_query="Research what marketing managers look for when hiring video production. What makes a good vs bad experience?",
        market_analysis_query="Analyze the corporate video production market - impact of AI tools and remote work on demand",
        expected_competitors=["Local agencies", "Upwork freelancers", "Fiverr", "Loom", "Synthesia", "HeyGen"],
        expected_pain_points=["budget unpredictability", "revision hell", "slow turnaround", "quality inconsistency", "communication gaps"],
        expected_customer_segments=["Marketing directors", "HR teams", "Sales enablement", "Product marketing"],
        target_subreddits=["videography", "Filmmakers", "marketing", "corporatevideo", "VideoEditing"],
        tags=["creative", "agency", "video", "b2b"],
    ),

    # =========================================================================
    # SUSTAINABILITY SCENARIOS
    # =========================================================================

    TestScenario(
        id="carbon-tracking-saas",
        name="Carbon Footprint Tracking for SMBs",
        industry=Industry.SUSTAINABILITY,
        complexity=Complexity.MEDIUM,
        company_size=CompanySize.SMALL,
        company_name="CarbonLens",
        company_description="SaaS platform helping small and medium businesses track, reduce, and offset their carbon footprint with automated data collection",
        location="San Francisco, CA",
        founded_year=2022,
        business_model="SaaS subscription ($199-999/month based on company size)",
        target_market="SMBs with sustainability goals, especially B Corps and purpose-driven companies",
        unique_value_proposition="Automated carbon tracking from existing business tools - no manual data entry",
        current_challenges=[
            "Enterprise tools like Watershed are moving downmarket",
            "SMBs don't know where to start with carbon tracking",
            "Regulatory requirements still unclear for smaller companies",
        ],
        competitor_analysis_query="Analyze competitors in carbon tracking and sustainability software. Compare Watershed, Persefoni, Greenly, and SMB-focused tools.",
        customer_research_query="Research what SMB owners think about carbon tracking. What motivates them? What barriers stop them from starting?",
        market_analysis_query="Analyze the carbon accounting software market - is there room for SMB-focused players?",
        expected_competitors=["Watershed", "Persefoni", "Greenly", "Normative", "Sweep", "Plan A"],
        expected_pain_points=["too complex", "expensive enterprise tools", "manual data collection", "unclear ROI", "greenwashing concerns"],
        expected_customer_segments=["B Corps", "Sustainability officers", "Small business owners", "Purpose-driven startups"],
        target_subreddits=["sustainability", "smallbusiness", "Entrepreneur", "climatechange", "ZeroWaste"],
        tags=["sustainability", "saas", "smb", "climate"],
    ),

    # =========================================================================
    # REAL ESTATE SCENARIOS
    # =========================================================================

    TestScenario(
        id="proptech-rental-platform",
        name="Rental Property Management Platform",
        industry=Industry.REAL_ESTATE,
        complexity=Complexity.MEDIUM,
        company_size=CompanySize.SMALL,
        company_name="LandlordHQ",
        company_description="All-in-one platform for small landlords - tenant screening, rent collection, maintenance requests, and accounting",
        location="Atlanta, GA",
        founded_year=2022,
        business_model="SaaS subscription ($12-49/property/month)",
        target_market="Individual landlords and small property managers with 1-50 units",
        unique_value_proposition="Built for landlords who manage their own properties - no property manager jargon or enterprise features",
        current_challenges=[
            "Buildium and AppFolio dominating the market",
            "Landlords using spreadsheets are hard to convert",
            "Venmo/Zelle making rent collection 'good enough'",
        ],
        competitor_analysis_query="Analyze competitors in rental property management software. Compare Buildium, AppFolio, TenantCloud, Avail, and Cozy (now Apartments.com).",
        customer_research_query="Research small landlord pain points with property management. What do they use now? Why do they resist software?",
        market_analysis_query="Analyze the property management software market for small landlords specifically",
        expected_competitors=["Buildium", "AppFolio", "TenantCloud", "Avail", "RentRedi", "Stessa", "Landlord Studio"],
        expected_pain_points=["too complex", "expensive per unit", "tenant screening costs", "late rent chasing", "maintenance coordination"],
        expected_customer_segments=["Accidental landlords", "Small investors", "House hackers", "Self-managing landlords"],
        target_subreddits=["realestateinvesting", "Landlord", "RealEstate", "personalfinance", "FIRE"],
        tags=["proptech", "saas", "real-estate", "smb"],
    ),

    # =========================================================================
    # FITNESS SCENARIOS
    # =========================================================================

    TestScenario(
        id="fitness-coaching-platform",
        name="Online Fitness Coaching Platform",
        industry=Industry.FITNESS,
        complexity=Complexity.MEDIUM,
        company_size=CompanySize.SMALL,
        company_name="CoachSync",
        company_description="Platform for personal trainers to deliver online coaching - workout programming, nutrition tracking, client communication, and payments",
        location="Los Angeles, CA",
        founded_year=2023,
        business_model="SaaS for coaches ($29-149/month) with payment processing fees",
        target_market="Personal trainers and fitness coaches transitioning to online or hybrid coaching",
        unique_value_proposition="White-label mobile app so coaches deliver a branded experience without coding",
        current_challenges=[
            "Trainerize and TrueCoach are established",
            "Coaches resistant to monthly software costs",
            "Social media making coaches think they can DIY",
        ],
        competitor_analysis_query="Analyze competitors in online personal training software. Compare Trainerize, TrueCoach, PTDistinction, and newer platforms.",
        customer_research_query="Research what personal trainers struggle with in online coaching. What tools do they wish they had?",
        market_analysis_query="Analyze the online fitness coaching market - growth trends and coach economics",
        expected_competitors=["Trainerize", "TrueCoach", "PTDistinction", "Exercise.com", "Everfit", "FitSW"],
        expected_pain_points=["client accountability", "nutrition tracking", "payment collection", "programming time", "client communication scattered"],
        expected_customer_segments=["Gym personal trainers going online", "Online-only coaches", "Fitness influencers", "Gym owners"],
        target_subreddits=["personaltraining", "fitness", "weightroom", "bodybuilding", "Entrepreneur"],
        tags=["fitness", "saas", "creator-economy", "coaching"],
    ),

    # =========================================================================
    # LEGAL SCENARIOS
    # =========================================================================

    TestScenario(
        id="legal-document-automation",
        name="Legal Document Automation for Startups",
        industry=Industry.LEGAL,
        complexity=Complexity.HIGH,
        company_size=CompanySize.SMALL,
        company_name="LegalForge",
        company_description="AI-powered legal document generation and management for startups - incorporation, contracts, equity, and compliance",
        location="Palo Alto, CA",
        founded_year=2023,
        business_model="SaaS subscription ($49-299/month) + document generation credits",
        target_market="Early-stage startups and their lawyers",
        unique_value_proposition="YC-standard documents with AI customization - launch legally in hours, not weeks",
        current_challenges=[
            "Clerky and Stripe Atlas have strong startup networks",
            "Lawyers skeptical of AI legal tools",
            "Liability concerns with automated documents",
        ],
        competitor_analysis_query="Analyze competitors in legal tech for startups. Compare Clerky, Stripe Atlas, LegalZoom, and startup-focused legal automation tools.",
        customer_research_query="Research startup founder pain points with legal work. What do they procrastinate on? What scares them about legal?",
        market_analysis_query="Analyze the legal tech market for startups - where are the gaps?",
        expected_competitors=["Clerky", "Stripe Atlas", "LegalZoom", "Ironclad", "DocuSign", "Juro", "Precisely"],
        expected_pain_points=["expensive lawyers", "confusing legal jargon", "slow turnaround", "not knowing what they need", "cap table mess"],
        expected_customer_segments=["First-time founders", "Serial entrepreneurs", "Startup lawyers", "Accelerator programs"],
        target_subreddits=["startups", "Entrepreneur", "legaladvice", "smallbusiness", "venturecapital"],
        tags=["legal-tech", "saas", "startups", "ai"],
    ),
]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_scenario(scenario_id: str) -> Optional[TestScenario]:
    """Get a specific scenario by ID."""
    for scenario in TEST_SCENARIOS:
        if scenario.id == scenario_id:
            return scenario
    return None


def get_scenarios_by_industry(industry: Industry) -> List[TestScenario]:
    """Get all scenarios for a specific industry."""
    return [s for s in TEST_SCENARIOS if s.industry == industry]


def get_scenarios_by_complexity(complexity: Complexity) -> List[TestScenario]:
    """Get all scenarios of a specific complexity level."""
    return [s for s in TEST_SCENARIOS if s.complexity == complexity]


def get_scenarios_by_tag(tag: str) -> List[TestScenario]:
    """Get all scenarios with a specific tag."""
    return [s for s in TEST_SCENARIOS if tag in s.tags]


def get_all_industries() -> List[str]:
    """Get list of all unique industries in scenarios."""
    return list(set(s.industry.value for s in TEST_SCENARIOS))


def get_scenario_summary() -> Dict[str, Any]:
    """Get a summary of all available scenarios."""
    return {
        "total_scenarios": len(TEST_SCENARIOS),
        "industries": get_all_industries(),
        "complexity_breakdown": {
            "low": len(get_scenarios_by_complexity(Complexity.LOW)),
            "medium": len(get_scenarios_by_complexity(Complexity.MEDIUM)),
            "high": len(get_scenarios_by_complexity(Complexity.HIGH)),
        },
        "scenarios": [
            {"id": s.id, "name": s.name, "industry": s.industry.value}
            for s in TEST_SCENARIOS
        ]
    }
