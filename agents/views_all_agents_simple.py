"""
Simple view to list all available agents without complex database queries
"""

# PARTIAL — Session 1113 review (Session 1111 PR-B/PR-E queue).
# Classification: built but not URL-mounted.
# Why: imported by `agents/urls_deployment.py`, which is itself dark
# (never `include()`-d). No active runtime caller.
# Decision pending: same as `agents/urls_deployment.py`.
# See: docs/handoffs/SESSION_1111_DEEPER_REVIEW_MAP.md

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


# Comprehensive list of all 152 agents
ALL_AGENTS = [
    # Core Business Agents
    {"id": "business_agent", "name": "Business Agent", "specialization": "Business strategy and planning"},
    {"id": "market_research_specialist", "name": "Market Research Specialist", "specialization": "Market analysis and insights"},
    {"id": "product_manager", "name": "Product Manager", "specialization": "Product strategy and roadmap"},
    {"id": "financial_analyst", "name": "Financial Analyst", "specialization": "Financial analysis and modeling"},
    {"id": "marketing_strategist", "name": "Marketing Strategist", "specialization": "Marketing campaigns and strategy"},
    {"id": "sales_specialist", "name": "Sales Specialist", "specialization": "Sales strategy and execution"},
    {"id": "brand_strategist", "name": "Brand Strategist", "specialization": "Brand identity and messaging"},
    {"id": "customer_success_manager", "name": "Customer Success Manager", "specialization": "Customer retention and satisfaction"},
    {"id": "operations_manager", "name": "Operations Manager", "specialization": "Operational efficiency and processes"},
    {"id": "hr_specialist", "name": "HR Specialist", "specialization": "Human resources and talent management"},

    # Technical Development Agents
    {"id": "ml_pipeline", "name": "ML Recommendation Engine", "specialization": "Machine learning architectures"},
    {"id": "database_architect", "name": "Database Architect", "specialization": "Database design and optimization"},
    {"id": "frontend_engineer", "name": "Frontend Engineer", "specialization": "User interface development"},
    {"id": "backend_engineer", "name": "Backend Engineer", "specialization": "Server-side development"},
    {"id": "fullstack_developer", "name": "Fullstack Developer", "specialization": "End-to-end development"},
    {"id": "api_gateway_architect", "name": "API Developer", "specialization": "API design and integration"},
    {"id": "mobile_developer", "name": "Mobile Developer", "specialization": "Mobile app development"},
    {"id": "ios_developer", "name": "iOS Developer", "specialization": "iOS app development"},
    {"id": "android_developer", "name": "Android Developer", "specialization": "Android app development"},
    {"id": "react_developer", "name": "React Developer", "specialization": "React.js development"},
    {"id": "vue_developer", "name": "Vue Developer", "specialization": "Vue.js development"},
    {"id": "angular_developer", "name": "Angular Developer", "specialization": "Angular development"},
    {"id": "python_developer", "name": "Python Developer", "specialization": "Python programming"},
    {"id": "javascript_developer", "name": "JavaScript Developer", "specialization": "JavaScript programming"},
    {"id": "typescript_developer", "name": "TypeScript Developer", "specialization": "TypeScript programming"},
    {"id": "java_developer", "name": "Java Developer", "specialization": "Java programming"},
    {"id": "csharp_developer", "name": "C# Developer", "specialization": "C# programming"},
    {"id": "go_developer", "name": "Go Developer", "specialization": "Go programming"},
    {"id": "rust_developer", "name": "Rust Developer", "specialization": "Rust programming"},
    {"id": "php_developer", "name": "PHP Developer", "specialization": "PHP programming"},

    # AI/ML Specialists
    {"id": "data_scientist", "name": "Data Scientist", "specialization": "Data analysis and modeling"},
    {"id": "ml_engineer", "name": "ML Engineer", "specialization": "Machine learning engineering"},
    {"id": "nlp_specialist", "name": "NLP Specialist", "specialization": "Natural language processing"},
    {"id": "computer_vision_expert", "name": "Computer Vision Expert", "specialization": "Image and video analysis"},
    {"id": "deep_learning_expert", "name": "Deep Learning Expert", "specialization": "Neural network architectures"},
    {"id": "reinforcement_learning_expert", "name": "Reinforcement Learning Expert", "specialization": "RL algorithms and agents"},
    {"id": "ai_ethicist", "name": "AI Ethicist", "specialization": "Ethical AI practices"},
    {"id": "ai_researcher", "name": "AI Researcher", "specialization": "AI research and development"},
    {"id": "prompt_engineer", "name": "Prompt Engineer", "specialization": "LLM prompt optimization"},
    {"id": "llm_specialist", "name": "LLM Specialist", "specialization": "Large language models"},

    # Infrastructure & DevOps
    {"id": "devops_engineer", "name": "DevOps Engineer", "specialization": "CI/CD and infrastructure"},
    {"id": "cloud_architect", "name": "Cloud Architect", "specialization": "Cloud infrastructure design"},
    {"id": "aws_specialist", "name": "AWS Specialist", "specialization": "Amazon Web Services"},
    {"id": "azure_specialist", "name": "Azure Specialist", "specialization": "Microsoft Azure"},
    {"id": "gcp_specialist", "name": "GCP Specialist", "specialization": "Google Cloud Platform"},
    {"id": "kubernetes_expert", "name": "Kubernetes Expert", "specialization": "Container orchestration"},
    {"id": "docker_specialist", "name": "Docker Specialist", "specialization": "Container technologies"},
    {"id": "terraform_expert", "name": "Terraform Expert", "specialization": "Infrastructure as code"},
    {"id": "site_reliability_engineer", "name": "Site Reliability Engineer", "specialization": "System reliability and uptime"},
    {"id": "network_engineer", "name": "Network Engineer", "specialization": "Network architecture and security"},

    # Security Specialists
    {"id": "security_specialist", "name": "Security Specialist", "specialization": "Application security"},
    {"id": "cybersecurity_expert", "name": "Cybersecurity Expert", "specialization": "Security threats and defense"},
    {"id": "penetration_tester", "name": "Penetration Tester", "specialization": "Security vulnerability testing"},
    {"id": "security_architect", "name": "Security Architect", "specialization": "Security system design"},
    {"id": "compliance_officer", "name": "Compliance Officer", "specialization": "Regulatory compliance"},
    {"id": "privacy_expert", "name": "Privacy Expert", "specialization": "Data privacy and GDPR"},

    # Design & UX
    {"id": "ux_designer", "name": "UX Designer", "specialization": "User experience design"},
    {"id": "ui_designer", "name": "UI Designer", "specialization": "User interface design"},
    {"id": "graphic_designer", "name": "Graphic Designer", "specialization": "Visual design and graphics"},
    {"id": "product_designer", "name": "Product Designer", "specialization": "Product design and prototyping"},
    {"id": "interaction_designer", "name": "Interaction Designer", "specialization": "Interactive design patterns"},
    {"id": "motion_designer", "name": "Motion Designer", "specialization": "Animation and motion graphics"},
    {"id": "3d_designer", "name": "3D Designer", "specialization": "3D modeling and rendering"},
    {"id": "ar_vr_designer", "name": "AR/VR Designer", "specialization": "Augmented and virtual reality"},

    # Content & Marketing
    {"id": "content_strategist", "name": "Content Strategist", "specialization": "Content planning and strategy"},
    {"id": "copywriter", "name": "Copywriter", "specialization": "Marketing and ad copy"},
    {"id": "technical_writer", "name": "Technical Writer", "specialization": "Technical documentation"},
    {"id": "seo_specialist", "name": "SEO Specialist", "specialization": "Search engine optimization"},
    {"id": "social_media_manager", "name": "Social Media Manager", "specialization": "Social media strategy"},
    {"id": "email_marketing_specialist", "name": "Email Marketing Specialist", "specialization": "Email campaigns"},
    {"id": "video_producer", "name": "Video Producer", "specialization": "Video content creation"},
    {"id": "podcast_producer", "name": "Podcast Producer", "specialization": "Podcast production"},

    # Blockchain & Web3
    {"id": "blockchain_developer", "name": "Blockchain Developer", "specialization": "Blockchain and smart contracts"},
    {"id": "solidity_developer", "name": "Solidity Developer", "specialization": "Ethereum smart contracts"},
    {"id": "web3_developer", "name": "Web3 Developer", "specialization": "Decentralized applications"},
    {"id": "defi_specialist", "name": "DeFi Specialist", "specialization": "Decentralized finance"},
    {"id": "nft_specialist", "name": "NFT Specialist", "specialization": "Non-fungible tokens"},
    {"id": "crypto_analyst", "name": "Crypto Analyst", "specialization": "Cryptocurrency analysis"},

    # Quality & Testing
    {"id": "qa_engineer", "name": "QA Engineer", "specialization": "Quality assurance"},
    {"id": "test_automation_engineer", "name": "Test Automation Engineer", "specialization": "Automated testing"},
    {"id": "performance_engineer", "name": "Performance Engineer", "specialization": "Performance optimization"},
    {"id": "load_testing_specialist", "name": "Load Testing Specialist", "specialization": "Load and stress testing"},
    {"id": "accessibility_specialist", "name": "Accessibility Specialist", "specialization": "Accessibility standards"},

    # Gaming & Entertainment
    {"id": "game_developer", "name": "Game Developer", "specialization": "Game development"},
    {"id": "unity_developer", "name": "Unity Developer", "specialization": "Unity game engine"},
    {"id": "unreal_developer", "name": "Unreal Developer", "specialization": "Unreal Engine"},
    {"id": "game_designer", "name": "Game Designer", "specialization": "Game mechanics and design"},
    {"id": "level_designer", "name": "Level Designer", "specialization": "Game level design"},

    # Data & Analytics
    {"id": "data_analyst", "name": "Data Analyst", "specialization": "Data analysis and insights"},
    {"id": "business_intelligence_analyst", "name": "BI Analyst", "specialization": "Business intelligence"},
    {"id": "data_engineer", "name": "Data Engineer", "specialization": "Data pipeline engineering"},
    {"id": "etl_specialist", "name": "ETL Specialist", "specialization": "Extract, transform, load"},
    {"id": "big_data_engineer", "name": "Big Data Engineer", "specialization": "Big data technologies"},

    # Sports Betting & Gambling
    {"id": "sports_betting_specialist", "name": "Sports Betting Specialist", "specialization": "Sports betting platforms"},
    {"id": "odds_calculation_expert", "name": "Odds Calculation Expert", "specialization": "Betting odds and probability"},
    {"id": "sportsbook_architect", "name": "Sportsbook Architect", "specialization": "Sportsbook platform design"},
    {"id": "live_betting_engineer", "name": "Live Betting Engineer", "specialization": "Real-time betting systems"},
    {"id": "prop_bet_specialist", "name": "Prop Bet Specialist", "specialization": "Proposition betting features"},
    {"id": "parlay_system_developer", "name": "Parlay System Developer", "specialization": "Parlay and accumulator bets"},
    {"id": "betting_analytics_expert", "name": "Betting Analytics Expert", "specialization": "Betting data analytics"},
    {"id": "sports_data_integration", "name": "Sports Data Integration Expert", "specialization": "Live sports data feeds"},
    {"id": "college_sports_specialist", "name": "College Sports Specialist", "specialization": "NCAA and college sports"},
    {"id": "betting_compliance_officer", "name": "Betting Compliance Officer", "specialization": "Gambling regulations"},
    {"id": "responsible_gaming_specialist", "name": "Responsible Gaming Specialist", "specialization": "Player protection features"},
    {"id": "betting_payment_processor", "name": "Betting Payment Processor", "specialization": "Betting payment systems"},
    {"id": "sports_statistician", "name": "Sports Statistician", "specialization": "Sports statistics and trends"},
    {"id": "betting_risk_manager", "name": "Betting Risk Manager", "specialization": "Betting risk management"},
    {"id": "handicapping_expert", "name": "Handicapping Expert", "specialization": "Sports handicapping systems"},

    # Specialized Domains
    {"id": "healthcare_specialist", "name": "Healthcare Specialist", "specialization": "Healthcare technology"},
    {"id": "fintech_specialist", "name": "FinTech Specialist", "specialization": "Financial technology"},
    {"id": "edtech_specialist", "name": "EdTech Specialist", "specialization": "Education technology"},
    {"id": "ecommerce_specialist", "name": "E-commerce Specialist", "specialization": "Online retail platforms"},
    {"id": "logistics_specialist", "name": "Logistics Specialist", "specialization": "Supply chain and logistics"},
    {"id": "real_estate_tech_specialist", "name": "PropTech Specialist", "specialization": "Real estate technology"},
    {"id": "legal_tech_specialist", "name": "LegalTech Specialist", "specialization": "Legal technology"},
    {"id": "agtech_specialist", "name": "AgTech Specialist", "specialization": "Agriculture technology"},

    # Research & Development
    {"id": "research_scientist", "name": "Research Scientist", "specialization": "Scientific research"},
    {"id": "quantum_computing_researcher", "name": "Quantum Computing Researcher", "specialization": "Quantum algorithms"},
    {"id": "bioinformatics_specialist", "name": "Bioinformatics Specialist", "specialization": "Biological data analysis"},
    {"id": "robotics_engineer", "name": "Robotics Engineer", "specialization": "Robotics and automation"},

    # Project Management
    {"id": "project_manager", "name": "Project Manager", "specialization": "Project planning and execution"},
    {"id": "scrum_master", "name": "Scrum Master", "specialization": "Agile methodology"},
    {"id": "agile_coach", "name": "Agile Coach", "specialization": "Agile transformation"},
    {"id": "program_manager", "name": "Program Manager", "specialization": "Program coordination"},

    # Support & Documentation
    {"id": "technical_support_engineer", "name": "Technical Support Engineer", "specialization": "Customer technical support"},
    {"id": "documentation_specialist", "name": "Documentation Specialist", "specialization": "Documentation management"},
    {"id": "training_specialist", "name": "Training Specialist", "specialization": "User training and education"},
    {"id": "implementation_consultant", "name": "Implementation Consultant", "specialization": "Solution implementation"},

    # Emerging Technologies
    {"id": "iot_specialist", "name": "IoT Specialist", "specialization": "Internet of Things"},
    {"id": "edge_computing_specialist", "name": "Edge Computing Specialist", "specialization": "Edge computing solutions"},
    {"id": "5g_specialist", "name": "5G Specialist", "specialization": "5G network technologies"},
    {"id": "metaverse_developer", "name": "Metaverse Developer", "specialization": "Metaverse experiences"},

    # Additional Specialists
    {"id": "automation_engineer", "name": "Automation Engineer", "specialization": "Process automation"},
    {"id": "integration_specialist", "name": "Integration Specialist", "specialization": "System integration"},
    {"id": "api_integration_specialist", "name": "API Integration Specialist", "specialization": "API integrations"},
    {"id": "middleware_specialist", "name": "Middleware Specialist", "specialization": "Middleware solutions"},
    {"id": "database_administrator", "name": "Database Administrator", "specialization": "Database management"},
    {"id": "system_administrator", "name": "System Administrator", "specialization": "System administration"},
    {"id": "linux_administrator", "name": "Linux Administrator", "specialization": "Linux systems"},
    {"id": "windows_administrator", "name": "Windows Administrator", "specialization": "Windows systems"},
    {"id": "virtualization_specialist", "name": "Virtualization Specialist", "specialization": "Virtual environments"},
    {"id": "storage_specialist", "name": "Storage Specialist", "specialization": "Data storage solutions"},
    {"id": "backup_recovery_specialist", "name": "Backup & Recovery Specialist", "specialization": "Backup strategies"},
    {"id": "disaster_recovery_specialist", "name": "Disaster Recovery Specialist", "specialization": "DR planning"},
    {"id": "monitoring_specialist", "name": "Monitoring Specialist", "specialization": "System monitoring"},
    {"id": "observability_engineer", "name": "Observability Engineer", "specialization": "System observability"},
    {"id": "release_manager", "name": "Release Manager", "specialization": "Release management"},
    {"id": "configuration_manager", "name": "Configuration Manager", "specialization": "Configuration management"},
    {"id": "change_management_specialist", "name": "Change Management Specialist", "specialization": "Change processes"},
    {"id": "incident_manager", "name": "Incident Manager", "specialization": "Incident response"},
    {"id": "problem_manager", "name": "Problem Manager", "specialization": "Problem resolution"},
    {"id": "service_desk_analyst", "name": "Service Desk Analyst", "specialization": "Service desk operations"},
    {"id": "vendor_manager", "name": "Vendor Manager", "specialization": "Vendor relationships"},
    {"id": "procurement_specialist", "name": "Procurement Specialist", "specialization": "Procurement processes"},
    {"id": "contract_specialist", "name": "Contract Specialist", "specialization": "Contract management"},
    {"id": "budget_analyst", "name": "Budget Analyst", "specialization": "Budget planning"},
    {"id": "cost_optimization_specialist", "name": "Cost Optimization Specialist", "specialization": "Cost reduction"},
]


@csrf_exempt
@require_http_methods(["GET"])
def list_all_agents_simple(request):
    """
    Return all 152 agents in a simple format
    """
    try:
        # Group by specialization
        categories = {}
        for agent in ALL_AGENTS:
            spec = agent['specialization']
            if spec not in categories:
                categories[spec] = []
            categories[spec].append(agent)

        return JsonResponse({
            'success': True,
            'total_agents': len(ALL_AGENTS),
            'agents': ALL_AGENTS,
            'categories': categories,
            'specializations': list(categories.keys()),
            'message': f'Retrieved {len(ALL_AGENTS)} agents'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)