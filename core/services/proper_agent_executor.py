"""
Proper Agent Executor for Real Agent Tasks
===========================================
This module ensures agents execute their actual specialized tasks using LLMs,
not just generate generic code templates.

Session 727: Migrated from agents/proper_agent_executor.py to core/services/proper_agent_executor.py
"""

import asyncio
import json
import logging
from typing import Dict, Any, List
from django.utils import timezone
from channels.layers import get_channel_layer

from core.models import GeneratedProject, GeneratedCode

logger = logging.getLogger(__name__)


class ProperAgentExecutor:
    """
    Executes agents to perform their actual specialized tasks.

    For example:
    - Business Agent: Analyzes business requirements and creates strategy
    - ML Recommendation Engine: Designs ML architecture
    - Database Architect: Designs database schema

    NOT just generating generic .py files!
    """

    def __init__(self):
        # Import ConcreteAgentExecutor from the actual location
        from ai_core.agents.concrete_executor import ConcreteAgentExecutor
        self.executor = ConcreteAgentExecutor()
        self.channel_layer = get_channel_layer()

        if hasattr(self.executor, 'agent_classes'):
            logger.info(f"✅ Initialized ProperAgentExecutor with {len(self.executor.agent_classes)} agents")
            logger.info(f"📋 Available agents: {sorted(list(self.executor.agent_classes.keys()))}")
        else:
            logger.error(f"❌ ConcreteAgentExecutor missing agent_classes attribute!")
            logger.error(f"Available attributes: {dir(self.executor)}")

    def _get_all_agent_tasks(self):
        """Get task definitions for all 157 agents"""
        return {
            # Core Business Agents
            "Business Agent": {
                "task": "business_analysis",
                "description": "Analyze business requirements and create strategic plan",
                "expected_output": "business_strategy"
            },
            "Market Research Specialist": {
                "task": "market_research",
                "description": "Research market trends and competitor analysis",
                "expected_output": "market_analysis"
            },
            "Product Manager": {
                "task": "product_strategy",
                "description": "Define product roadmap and requirements",
                "expected_output": "product_spec"
            },
            "Financial Analyst": {
                "task": "financial_modeling",
                "description": "Create financial models and projections",
                "expected_output": "financial_model"
            },
            "Marketing Strategist": {
                "task": "marketing_strategy",
                "description": "Develop comprehensive marketing strategy",
                "expected_output": "marketing_plan"
            },
            "Sales Specialist": {
                "task": "sales_strategy",
                "description": "Design sales processes and strategies",
                "expected_output": "sales_plan"
            },
            "Brand Strategist": {
                "task": "brand_strategy",
                "description": "Create brand identity and messaging",
                "expected_output": "brand_guide"
            },
            "Customer Success Manager": {
                "task": "customer_success",
                "description": "Design customer retention strategies",
                "expected_output": "customer_plan"
            },
            "Operations Manager": {
                "task": "operations_optimization",
                "description": "Optimize operational processes and efficiency",
                "expected_output": "operations_plan"
            },
            "HR Specialist": {
                "task": "hr_strategy",
                "description": "Design human resources and talent management",
                "expected_output": "hr_plan"
            },

            # Technical Development Agents
            "ML Recommendation Engine": {
                "task": "ml_architecture_design",
                "description": "Design machine learning recommendation system",
                "expected_output": "ml_architecture"
            },
            "Database Architect": {
                "task": "database_schema_design",
                "description": "Design optimal database schema",
                "expected_output": "database_schema"
            },
            "Frontend Engineer": {
                "task": "ui_design",
                "description": "Design user interface and user experience",
                "expected_output": "ui_specification"
            },
            "Backend Engineer": {
                "task": "backend_architecture",
                "description": "Design server-side architecture and APIs",
                "expected_output": "backend_spec"
            },
            "Fullstack Developer": {
                "task": "fullstack_design",
                "description": "Design end-to-end application architecture",
                "expected_output": "fullstack_spec"
            },
            "API Developer": {
                "task": "api_design",
                "description": "Design RESTful API architecture",
                "expected_output": "api_specification"
            },
            "Mobile Developer": {
                "task": "mobile_app_design",
                "description": "Design mobile application architecture",
                "expected_output": "mobile_spec"
            },
            "iOS Developer": {
                "task": "ios_app_design",
                "description": "Design iOS-specific application features",
                "expected_output": "ios_spec"
            },
            "Android Developer": {
                "task": "android_app_design",
                "description": "Design Android-specific application features",
                "expected_output": "android_spec"
            },
            "React Developer": {
                "task": "react_component_design",
                "description": "Design React.js component architecture",
                "expected_output": "react_spec"
            },
            "Vue Developer": {
                "task": "vue_component_design",
                "description": "Design Vue.js component architecture",
                "expected_output": "vue_spec"
            },
            "Angular Developer": {
                "task": "angular_component_design",
                "description": "Design Angular component architecture",
                "expected_output": "angular_spec"
            },
            "Python Developer": {
                "task": "python_architecture",
                "description": "Design Python application architecture",
                "expected_output": "python_spec"
            },
            "JavaScript Developer": {
                "task": "javascript_architecture",
                "description": "Design JavaScript application structure",
                "expected_output": "javascript_spec"
            },
            "TypeScript Developer": {
                "task": "typescript_architecture",
                "description": "Design TypeScript application structure",
                "expected_output": "typescript_spec"
            },
            "Java Developer": {
                "task": "java_architecture",
                "description": "Design Java application architecture",
                "expected_output": "java_spec"
            },
            "C# Developer": {
                "task": "csharp_architecture",
                "description": "Design C# application architecture",
                "expected_output": "csharp_spec"
            },
            "Go Developer": {
                "task": "go_architecture",
                "description": "Design Go application architecture",
                "expected_output": "go_spec"
            },
            "Rust Developer": {
                "task": "rust_architecture",
                "description": "Design Rust application architecture",
                "expected_output": "rust_spec"
            },
            "PHP Developer": {
                "task": "php_architecture",
                "description": "Design PHP application architecture",
                "expected_output": "php_spec"
            },

            # AI/ML Specialists
            "Data Scientist": {
                "task": "data_analysis",
                "description": "Perform comprehensive data analysis",
                "expected_output": "data_insights"
            },
            "ML Engineer": {
                "task": "ml_pipeline_design",
                "description": "Design machine learning pipeline architecture",
                "expected_output": "ml_pipeline_spec"
            },
            "NLP Specialist": {
                "task": "nlp_architecture",
                "description": "Design natural language processing solutions",
                "expected_output": "nlp_spec"
            },
            "Computer Vision Expert": {
                "task": "computer_vision_design",
                "description": "Design computer vision and image processing",
                "expected_output": "cv_spec"
            },
            "Deep Learning Expert": {
                "task": "deep_learning_architecture",
                "description": "Design neural network architectures",
                "expected_output": "dl_spec"
            },
            "Reinforcement Learning Expert": {
                "task": "rl_architecture",
                "description": "Design reinforcement learning systems",
                "expected_output": "rl_spec"
            },
            "AI Ethicist": {
                "task": "ai_ethics_review",
                "description": "Review AI systems for ethical considerations",
                "expected_output": "ethics_report"
            },
            "AI Researcher": {
                "task": "ai_research",
                "description": "Research and development of AI solutions",
                "expected_output": "research_findings"
            },
            "Prompt Engineer": {
                "task": "prompt_optimization",
                "description": "Optimize LLM prompts and interactions",
                "expected_output": "prompt_strategy"
            },
            "LLM Specialist": {
                "task": "llm_integration",
                "description": "Design large language model integrations",
                "expected_output": "llm_spec"
            },

            # Infrastructure & DevOps
            "DevOps Engineer": {
                "task": "devops_pipeline",
                "description": "Design CI/CD and deployment pipelines",
                "expected_output": "devops_spec"
            },
            "Cloud Architect": {
                "task": "cloud_infrastructure",
                "description": "Design cloud infrastructure architecture",
                "expected_output": "cloud_spec"
            },
            "AWS Specialist": {
                "task": "aws_architecture",
                "description": "Design Amazon Web Services infrastructure",
                "expected_output": "aws_spec"
            },
            "Azure Specialist": {
                "task": "azure_architecture",
                "description": "Design Microsoft Azure infrastructure",
                "expected_output": "azure_spec"
            },
            "GCP Specialist": {
                "task": "gcp_architecture",
                "description": "Design Google Cloud Platform infrastructure",
                "expected_output": "gcp_spec"
            },
            "Kubernetes Expert": {
                "task": "kubernetes_deployment",
                "description": "Design container orchestration with Kubernetes",
                "expected_output": "k8s_spec"
            },
            "Docker Specialist": {
                "task": "containerization",
                "description": "Design container architecture with Docker",
                "expected_output": "docker_spec"
            },
            "Terraform Expert": {
                "task": "infrastructure_as_code",
                "description": "Design infrastructure as code with Terraform",
                "expected_output": "terraform_spec"
            },
            "Site Reliability Engineer": {
                "task": "reliability_engineering",
                "description": "Design system reliability and monitoring",
                "expected_output": "sre_spec"
            },
            "Network Engineer": {
                "task": "network_architecture",
                "description": "Design network architecture and security",
                "expected_output": "network_spec"
            },

            # Security Specialists
            "Security Specialist": {
                "task": "security_assessment",
                "description": "Assess application security requirements",
                "expected_output": "security_plan"
            },
            "Cybersecurity Expert": {
                "task": "cybersecurity_strategy",
                "description": "Design comprehensive security defense strategy",
                "expected_output": "cybersecurity_plan"
            },
            "Penetration Tester": {
                "task": "penetration_testing",
                "description": "Design penetration testing methodology",
                "expected_output": "pentest_plan"
            },
            "Security Architect": {
                "task": "security_architecture",
                "description": "Design secure system architecture",
                "expected_output": "security_architecture"
            },
            "Compliance Officer": {
                "task": "compliance_review",
                "description": "Ensure regulatory compliance requirements",
                "expected_output": "compliance_report"
            },
            "Privacy Expert": {
                "task": "privacy_assessment",
                "description": "Assess data privacy and GDPR requirements",
                "expected_output": "privacy_plan"
            },

            # Design & UX
            "UX Designer": {
                "task": "ux_research_design",
                "description": "Design user experience and research strategy",
                "expected_output": "ux_spec"
            },
            "UI Designer": {
                "task": "ui_visual_design",
                "description": "Design user interface and visual elements",
                "expected_output": "ui_designs"
            },
            "Graphic Designer": {
                "task": "graphic_design",
                "description": "Create visual design and graphics",
                "expected_output": "design_assets"
            },
            "Product Designer": {
                "task": "product_design",
                "description": "Design product interface and interactions",
                "expected_output": "product_design_spec"
            },
            "Interaction Designer": {
                "task": "interaction_design",
                "description": "Design interactive behaviors and patterns",
                "expected_output": "interaction_spec"
            },
            "Motion Designer": {
                "task": "motion_design",
                "description": "Design animation and motion graphics",
                "expected_output": "motion_spec"
            },
            "3D Designer": {
                "task": "3d_modeling",
                "description": "Create 3D models and rendering specifications",
                "expected_output": "3d_spec"
            },
            "AR/VR Designer": {
                "task": "arvr_design",
                "description": "Design augmented and virtual reality experiences",
                "expected_output": "arvr_spec"
            },

            # Sports Betting & Gambling Specialists
            "Sports Betting Specialist": {
                "task": "betting_platform_design",
                "description": "Design sports betting platform architecture",
                "expected_output": "betting_platform_spec"
            },
            "Odds Calculation Expert": {
                "task": "odds_calculation",
                "description": "Design betting odds calculation algorithms",
                "expected_output": "odds_algorithm_spec"
            },
            "Sportsbook Architect": {
                "task": "sportsbook_design",
                "description": "Design sportsbook platform architecture",
                "expected_output": "sportsbook_spec"
            },
            "Live Betting Engineer": {
                "task": "live_betting_system",
                "description": "Design real-time betting system architecture",
                "expected_output": "live_betting_spec"
            },
            "Prop Bet Specialist": {
                "task": "proposition_betting",
                "description": "Design proposition betting features",
                "expected_output": "prop_bet_spec"
            },
            "Parlay System Developer": {
                "task": "parlay_system",
                "description": "Design parlay and accumulator betting system",
                "expected_output": "parlay_spec"
            },
            "Betting Analytics Expert": {
                "task": "betting_analytics",
                "description": "Design betting data analytics platform",
                "expected_output": "betting_analytics_spec"
            },
            "Sports Data Integration Expert": {
                "task": "sports_data_integration",
                "description": "Design live sports data feed integration",
                "expected_output": "sports_data_spec"
            },
            "College Sports Specialist": {
                "task": "college_sports_analysis",
                "description": "Analyze NCAA and college sports betting",
                "expected_output": "college_sports_spec"
            },
            "Betting Compliance Officer": {
                "task": "betting_compliance",
                "description": "Ensure gambling regulation compliance",
                "expected_output": "betting_compliance_report"
            },
            "Responsible Gaming Specialist": {
                "task": "responsible_gaming",
                "description": "Design player protection and safety features",
                "expected_output": "responsible_gaming_spec"
            },
            "Betting Payment Processor": {
                "task": "betting_payments",
                "description": "Design betting payment processing system",
                "expected_output": "payment_processing_spec"
            },
            "Sports Statistician": {
                "task": "sports_statistics",
                "description": "Analyze sports statistics and trends",
                "expected_output": "sports_stats_analysis"
            },
            "Betting Risk Manager": {
                "task": "betting_risk_management",
                "description": "Design betting risk management system",
                "expected_output": "risk_management_spec"
            },
            "Handicapping Expert": {
                "task": "handicapping_system",
                "description": "Design sports handicapping algorithms",
                "expected_output": "handicapping_spec"
            },

            # Content & Marketing
            "Content Strategist": {
                "task": "content_strategy",
                "description": "Plan content strategy and editorial calendar",
                "expected_output": "content_strategy_plan"
            },
            "Copywriter": {
                "task": "copywriting",
                "description": "Create marketing and advertising copy",
                "expected_output": "marketing_copy"
            },
            "Technical Writer": {
                "task": "technical_documentation",
                "description": "Create technical documentation and guides",
                "expected_output": "technical_docs"
            },
            "SEO Specialist": {
                "task": "seo_optimization",
                "description": "Optimize content for search engines",
                "expected_output": "seo_strategy"
            },
            "Social Media Manager": {
                "task": "social_media_strategy",
                "description": "Design social media marketing strategy",
                "expected_output": "social_media_plan"
            },
            "Email Marketing Specialist": {
                "task": "email_marketing",
                "description": "Design email marketing campaigns",
                "expected_output": "email_campaign_spec"
            },
            "Video Producer": {
                "task": "video_production",
                "description": "Plan video content and production",
                "expected_output": "video_production_plan"
            },
            "Podcast Producer": {
                "task": "podcast_production",
                "description": "Design podcast content and production",
                "expected_output": "podcast_production_plan"
            },

            # Blockchain & Web3
            "Blockchain Developer": {
                "task": "blockchain_architecture",
                "description": "Design blockchain and smart contract architecture",
                "expected_output": "blockchain_spec"
            },
            "Solidity Developer": {
                "task": "smart_contract_development",
                "description": "Design Ethereum smart contract architecture",
                "expected_output": "smart_contract_spec"
            },
            "Web3 Developer": {
                "task": "dapp_architecture",
                "description": "Design decentralized application architecture",
                "expected_output": "dapp_spec"
            },
            "DeFi Specialist": {
                "task": "defi_protocol_design",
                "description": "Design decentralized finance protocols",
                "expected_output": "defi_spec"
            },
            "NFT Specialist": {
                "task": "nft_platform_design",
                "description": "Design non-fungible token platform",
                "expected_output": "nft_spec"
            },
            "Crypto Analyst": {
                "task": "cryptocurrency_analysis",
                "description": "Analyze cryptocurrency markets and trends",
                "expected_output": "crypto_analysis"
            },

            # Quality & Testing
            "QA Engineer": {
                "task": "quality_assurance_plan",
                "description": "Design quality assurance testing strategy",
                "expected_output": "qa_plan"
            },
            "Test Automation Engineer": {
                "task": "test_automation",
                "description": "Design automated testing framework",
                "expected_output": "test_automation_spec"
            },
            "Performance Engineer": {
                "task": "performance_optimization",
                "description": "Design performance optimization strategy",
                "expected_output": "performance_plan"
            },
            "Load Testing Specialist": {
                "task": "load_testing",
                "description": "Design load and stress testing strategy",
                "expected_output": "load_testing_plan"
            },
            "Accessibility Specialist": {
                "task": "accessibility_compliance",
                "description": "Ensure accessibility standards compliance",
                "expected_output": "accessibility_plan"
            },

            # Gaming & Entertainment
            "Game Developer": {
                "task": "game_development",
                "description": "Design game mechanics and architecture",
                "expected_output": "game_design_spec"
            },
            "Unity Developer": {
                "task": "unity_development",
                "description": "Design Unity game engine architecture",
                "expected_output": "unity_spec"
            },
            "Unreal Developer": {
                "task": "unreal_development",
                "description": "Design Unreal Engine architecture",
                "expected_output": "unreal_spec"
            },
            "Game Designer": {
                "task": "game_design",
                "description": "Design game mechanics and user experience",
                "expected_output": "game_mechanics_spec"
            },
            "Level Designer": {
                "task": "level_design",
                "description": "Design game levels and environments",
                "expected_output": "level_design_spec"
            },

            # Data & Analytics
            "Data Analyst": {
                "task": "data_analysis_plan",
                "description": "Analyze data patterns and create insights",
                "expected_output": "data_analysis_report"
            },
            "BI Analyst": {
                "task": "business_intelligence",
                "description": "Design business intelligence dashboards",
                "expected_output": "bi_dashboard_spec"
            },
            "Data Engineer": {
                "task": "data_pipeline_design",
                "description": "Design data pipeline and ETL processes",
                "expected_output": "data_pipeline_spec"
            },
            "ETL Specialist": {
                "task": "etl_design",
                "description": "Design extract, transform, load processes",
                "expected_output": "etl_spec"
            },
            "Big Data Engineer": {
                "task": "big_data_architecture",
                "description": "Design big data processing architecture",
                "expected_output": "big_data_spec"
            },

            # Specialized Domains
            "Healthcare Specialist": {
                "task": "healthcare_system_design",
                "description": "Design healthcare technology solutions",
                "expected_output": "healthcare_spec"
            },
            "FinTech Specialist": {
                "task": "fintech_platform_design",
                "description": "Design financial technology platform",
                "expected_output": "fintech_spec"
            },
            "EdTech Specialist": {
                "task": "education_platform_design",
                "description": "Design education technology platform",
                "expected_output": "edtech_spec"
            },
            "E-commerce Specialist": {
                "task": "ecommerce_platform_design",
                "description": "Design online retail platform architecture",
                "expected_output": "ecommerce_spec"
            },
            "Logistics Specialist": {
                "task": "logistics_optimization",
                "description": "Design supply chain and logistics systems",
                "expected_output": "logistics_spec"
            },
            "PropTech Specialist": {
                "task": "real_estate_platform_design",
                "description": "Design real estate technology platform",
                "expected_output": "proptech_spec"
            },
            "LegalTech Specialist": {
                "task": "legal_platform_design",
                "description": "Design legal technology platform",
                "expected_output": "legaltech_spec"
            },
            "AgTech Specialist": {
                "task": "agriculture_platform_design",
                "description": "Design agriculture technology solutions",
                "expected_output": "agtech_spec"
            },

            # Research & Development
            "Research Scientist": {
                "task": "research_methodology",
                "description": "Design scientific research methodology",
                "expected_output": "research_plan"
            },
            "Quantum Computing Researcher": {
                "task": "quantum_algorithm_design",
                "description": "Research quantum computing algorithms",
                "expected_output": "quantum_spec"
            },
            "Bioinformatics Specialist": {
                "task": "bioinformatics_analysis",
                "description": "Analyze biological data and sequences",
                "expected_output": "bioinformatics_spec"
            },
            "Robotics Engineer": {
                "task": "robotics_system_design",
                "description": "Design robotics and automation systems",
                "expected_output": "robotics_spec"
            },

            # Project Management
            "Project Manager": {
                "task": "project_planning",
                "description": "Plan project timeline and resource allocation",
                "expected_output": "project_plan"
            },
            "Scrum Master": {
                "task": "agile_process_design",
                "description": "Design agile development processes",
                "expected_output": "agile_plan"
            },
            "Agile Coach": {
                "task": "agile_transformation",
                "description": "Guide agile transformation and practices",
                "expected_output": "transformation_plan"
            },
            "Program Manager": {
                "task": "program_coordination",
                "description": "Coordinate multiple projects and programs",
                "expected_output": "program_plan"
            },

            # Support & Documentation
            "Technical Support Engineer": {
                "task": "support_system_design",
                "description": "Design customer technical support systems",
                "expected_output": "support_plan"
            },
            "Documentation Specialist": {
                "task": "documentation_strategy",
                "description": "Design documentation management systems",
                "expected_output": "docs_strategy"
            },
            "Training Specialist": {
                "task": "training_program_design",
                "description": "Design user training and education programs",
                "expected_output": "training_plan"
            },
            "Implementation Consultant": {
                "task": "solution_implementation",
                "description": "Plan solution implementation strategy",
                "expected_output": "implementation_plan"
            },

            # Emerging Technologies
            "IoT Specialist": {
                "task": "iot_architecture",
                "description": "Design Internet of Things architecture",
                "expected_output": "iot_spec"
            },
            "Edge Computing Specialist": {
                "task": "edge_computing_design",
                "description": "Design edge computing solutions",
                "expected_output": "edge_computing_spec"
            },
            "5G Specialist": {
                "task": "5g_network_design",
                "description": "Design 5G network technology solutions",
                "expected_output": "5g_spec"
            },
            "Metaverse Developer": {
                "task": "metaverse_experience_design",
                "description": "Design metaverse experiences and platforms",
                "expected_output": "metaverse_spec"
            },

            # Additional System Specialists
            "Automation Engineer": {
                "task": "process_automation",
                "description": "Design process automation systems",
                "expected_output": "automation_spec"
            },
            "Integration Specialist": {
                "task": "system_integration",
                "description": "Design system integration architecture",
                "expected_output": "integration_spec"
            },
            "API Integration Specialist": {
                "task": "api_integration_design",
                "description": "Design API integration strategies",
                "expected_output": "api_integration_spec"
            },
            "Middleware Specialist": {
                "task": "middleware_design",
                "description": "Design middleware solutions and architecture",
                "expected_output": "middleware_spec"
            },
            "Database Administrator": {
                "task": "database_administration",
                "description": "Design database management and optimization",
                "expected_output": "db_admin_plan"
            },
            "System Administrator": {
                "task": "system_administration",
                "description": "Design system administration procedures",
                "expected_output": "sysadmin_plan"
            },
            "Linux Administrator": {
                "task": "linux_system_design",
                "description": "Design Linux system architecture",
                "expected_output": "linux_spec"
            },
            "Windows Administrator": {
                "task": "windows_system_design",
                "description": "Design Windows system architecture",
                "expected_output": "windows_spec"
            },
            "Virtualization Specialist": {
                "task": "virtualization_design",
                "description": "Design virtual environment architecture",
                "expected_output": "virtualization_spec"
            },
            "Storage Specialist": {
                "task": "storage_architecture",
                "description": "Design data storage solutions",
                "expected_output": "storage_spec"
            },
            "Backup & Recovery Specialist": {
                "task": "backup_strategy_design",
                "description": "Design backup and recovery strategies",
                "expected_output": "backup_plan"
            },
            "Disaster Recovery Specialist": {
                "task": "disaster_recovery_planning",
                "description": "Design disaster recovery procedures",
                "expected_output": "dr_plan"
            },
            "Monitoring Specialist": {
                "task": "monitoring_system_design",
                "description": "Design system monitoring infrastructure",
                "expected_output": "monitoring_spec"
            },
            "Observability Engineer": {
                "task": "observability_design",
                "description": "Design system observability and telemetry",
                "expected_output": "observability_spec"
            },
            "Release Manager": {
                "task": "release_management",
                "description": "Design release management processes",
                "expected_output": "release_plan"
            },
            "Configuration Manager": {
                "task": "configuration_management",
                "description": "Design configuration management systems",
                "expected_output": "config_management_spec"
            },
            "Change Management Specialist": {
                "task": "change_management",
                "description": "Design change management processes",
                "expected_output": "change_management_plan"
            },
            "Incident Manager": {
                "task": "incident_response_design",
                "description": "Design incident response procedures",
                "expected_output": "incident_response_plan"
            },
            "Problem Manager": {
                "task": "problem_resolution_design",
                "description": "Design problem resolution processes",
                "expected_output": "problem_management_plan"
            },
            "Service Desk Analyst": {
                "task": "service_desk_design",
                "description": "Design service desk operations",
                "expected_output": "service_desk_spec"
            },
            "Vendor Manager": {
                "task": "vendor_relationship_management",
                "description": "Design vendor relationship strategies",
                "expected_output": "vendor_management_plan"
            },
            "Procurement Specialist": {
                "task": "procurement_process_design",
                "description": "Design procurement processes and systems",
                "expected_output": "procurement_plan"
            },
            "Contract Specialist": {
                "task": "contract_management",
                "description": "Design contract management processes",
                "expected_output": "contract_management_spec"
            },
            "Budget Analyst": {
                "task": "budget_planning",
                "description": "Design budget planning and analysis",
                "expected_output": "budget_plan"
            },
            "Cost Optimization Specialist": {
                "task": "cost_reduction_analysis",
                "description": "Analyze and optimize operational costs",
                "expected_output": "cost_optimization_plan"
            }
        }

    async def execute_agent_task(self, agent_name: str, project: GeneratedProject, task_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an agent's actual specialized task.

        Args:
            agent_name: Name of the agent (e.g., "Business Agent")
            project: The project this task is for
            task_config: Configuration including project_type, requirements, etc.

        Returns:
            Dict containing the agent's actual output
        """

        # Map agent names to their actual tasks - ALL 157 AGENTS
        agent_tasks = self._get_all_agent_tasks()

        # Get the agent's specific task
        agent_config = agent_tasks.get(agent_name, {
            "task": "general_analysis",
            "description": f"Execute {agent_name} specialized task",
            "expected_output": "analysis_result"
        })

        # Build the actual task for the agent with full project context
        task = {
            "type": agent_config["task"],
            "description": agent_config["description"],
            "project_type": task_config.get("project_type", "general"),
            "project_description": task_config.get("project_description", ""),
            "key_features": task_config.get("key_features", []),
            "target_audience": task_config.get("target_audience", ""),
            "requirements": task_config.get("requirements", {}),
            "ml_features": task_config.get("ml_features", []),
            "context": {
                "project_name": project.name,
                "project_id": str(project.id),
                "project_details": project.description,
                "timestamp": str(timezone.now())
            },
            "questions": agent_config.get("questions", [])
        }

        try:
            logger.info(f"🎯 Executing {agent_name} for task: {agent_config['task']}")

            # Send WebSocket update that agent is starting
            await self.channel_layer.group_send(
                'ai_training',
                {
                    'type': 'broadcast_learning_update',
                    'data': {
                        'event': 'agent_starting',
                        'agent': agent_name,
                        'task': agent_config['task'],
                        'description': agent_config['description'],
                        'project_type': task_config.get('project_type', 'general'),
                        'timestamp': str(timezone.now())
                    }
                }
            )

            # Convert agent name to the format used in ConcreteAgentExecutor
            # "Business Agent" -> "business_agent"
            # "ML Recommendation Engine" -> "ml_recommendation_engine"
            executor_agent_name = agent_name.lower().replace(' ', '_')

            # Comprehensive name mappings for all 157 agents to ConcreteAgentExecutor
            # Based on actual registry contents from debug endpoint
            name_mappings = {
                # Core Business Agents (mapped to actual registry names)
                'business_agent': 'business_agent',  # Exists in registry
                'market_research_specialist': 'market_research_specialist',  # Exists in registry
                'product_manager': 'product_management_agent',  # Check if exists
                'financial_analyst': 'financial_analyst',  # Exists in registry
                'marketing_strategist': 'marketing_agent',  # Exists in registry
                'sales_specialist': 'sales_agent',  # Check if exists
                'brand_strategist': 'brand_guidelines_agent',  # Closest match in registry
                'customer_success_manager': 'customer_success_manager',
                'operations_manager': 'operations_manager',
                'hr_specialist': 'hr_specialist',

                # Technical Development Agents
                'ml_recommendation_engine': 'ml_pipeline',
                'database_architect': 'database_architect',
                'frontend_engineer': 'frontend_engineer',
                'backend_engineer': 'backend_engineer',
                'fullstack_developer': 'fullstack_developer',
                'api_developer': 'api_gateway_architect',
                'mobile_developer': 'mobile_developer',
                'ios_developer': 'ios_developer',
                'android_developer': 'android_developer',
                'react_developer': 'react_developer',
                'vue_developer': 'vue_developer',
                'angular_developer': 'angular_developer',
                'python_developer': 'python_developer',
                'javascript_developer': 'javascript_developer',
                'typescript_developer': 'typescript_developer',
                'java_developer': 'java_developer',
                'c#_developer': 'csharp_developer',
                'go_developer': 'go_developer',
                'rust_developer': 'rust_developer',
                'php_developer': 'php_developer',

                # AI/ML Specialists (mapped to actual registry names)
                'data_scientist': 'data_analyst',  # Exists in registry
                'ml_engineer': 'ml_pipeline',  # Exists in registry
                'nlp_specialist': 'rag_specialist',  # Closest match in registry
                'computer_vision_expert': 'image_video_pipeline',  # Closest match
                'deep_learning_expert': 'ml_pipeline',  # Use ML pipeline for now
                'reinforcement_learning_expert': 'ml_pipeline',  # Use ML pipeline for now
                'ai_ethicist': 'ai_ethicist',
                'ai_researcher': 'ai_researcher',
                'prompt_engineer': 'prompt_engineer',
                'llm_specialist': 'llm_specialist',

                # Infrastructure & DevOps
                'devops_engineer': 'devops_engineer',
                'cloud_architect': 'cloud_architect',
                'aws_specialist': 'aws_specialist',
                'azure_specialist': 'azure_specialist',
                'gcp_specialist': 'gcp_specialist',
                'kubernetes_expert': 'kubernetes_expert',
                'docker_specialist': 'docker_specialist',
                'terraform_expert': 'terraform_expert',
                'site_reliability_engineer': 'sre_engineer',
                'network_engineer': 'network_engineer',

                # Security Specialists
                'security_specialist': 'security_specialist',
                'cybersecurity_expert': 'cybersecurity_expert',
                'penetration_tester': 'penetration_tester',
                'security_architect': 'security_architect',
                'compliance_officer': 'compliance_officer',
                'privacy_expert': 'privacy_expert',

                # Design & UX
                'ux_designer': 'ux_designer',
                'ui_designer': 'ui_designer',
                'graphic_designer': 'graphic_designer',
                'product_designer': 'product_designer',
                'interaction_designer': 'interaction_designer',
                'motion_designer': 'motion_designer',
                '3d_designer': '3d_designer',
                'ar/vr_designer': 'arvr_designer',

                # Sports Betting Specialists
                'sports_betting_specialist': 'sports_betting_specialist',
                'odds_calculation_expert': 'odds_calculation_expert',
                'sportsbook_architect': 'sportsbook_architect',
                'live_betting_engineer': 'live_betting_engineer',
                'prop_bet_specialist': 'prop_bet_specialist',
                'parlay_system_developer': 'parlay_system_developer',
                'betting_analytics_expert': 'betting_analytics_expert',
                'sports_data_integration_expert': 'sports_data_integration_expert',
                'college_sports_specialist': 'college_sports_specialist',
                'betting_compliance_officer': 'betting_compliance_officer',
                'responsible_gaming_specialist': 'responsible_gaming_specialist',
                'betting_payment_processor': 'betting_payment_processor',
                'sports_statistician': 'sports_statistician',
                'betting_risk_manager': 'betting_risk_manager',
                'handicapping_expert': 'handicapping_expert',

                # Content & Marketing
                'content_strategist': 'content_strategist',
                'copywriter': 'copywriter',
                'technical_writer': 'technical_writer',
                'seo_specialist': 'seo_specialist',
                'social_media_manager': 'social_media_manager',
                'email_marketing_specialist': 'email_marketing_specialist',
                'video_producer': 'video_producer',
                'podcast_producer': 'podcast_producer',

                # Blockchain & Web3
                'blockchain_developer': 'blockchain_developer',
                'solidity_developer': 'solidity_developer',
                'web3_developer': 'web3_developer',
                'defi_specialist': 'defi_specialist',
                'nft_specialist': 'nft_specialist',
                'crypto_analyst': 'crypto_analyst',

                # Quality & Testing
                'qa_engineer': 'qa_engineer',
                'test_automation_engineer': 'test_automation_engineer',
                'performance_engineer': 'performance_engineer',
                'load_testing_specialist': 'load_testing_specialist',
                'accessibility_specialist': 'accessibility_specialist',

                # Gaming & Entertainment
                'game_developer': 'game_developer',
                'unity_developer': 'unity_developer',
                'unreal_developer': 'unreal_developer',
                'game_designer': 'game_designer',
                'level_designer': 'level_designer',

                # Data & Analytics
                'data_analyst': 'data_analyst',
                'bi_analyst': 'bi_analyst',
                'data_engineer': 'data_engineer',
                'etl_specialist': 'etl_specialist',
                'big_data_engineer': 'big_data_engineer',

                # Specialized Domains
                'healthcare_specialist': 'healthcare_specialist',
                'fintech_specialist': 'fintech_specialist',
                'edtech_specialist': 'edtech_specialist',
                'e-commerce_specialist': 'ecommerce_specialist',
                'logistics_specialist': 'logistics_specialist',
                'proptech_specialist': 'proptech_specialist',
                'legaltech_specialist': 'legaltech_specialist',
                'agtech_specialist': 'agtech_specialist',

                # Research & Development
                'research_scientist': 'research_scientist',
                'quantum_computing_researcher': 'quantum_computing_researcher',
                'bioinformatics_specialist': 'bioinformatics_specialist',
                'robotics_engineer': 'robotics_engineer',

                # Project Management
                'project_manager': 'project_manager',
                'scrum_master': 'scrum_master',
                'agile_coach': 'agile_coach',
                'program_manager': 'program_manager',

                # Support & Documentation
                'technical_support_engineer': 'technical_support_engineer',
                'documentation_specialist': 'documentation_specialist',
                'training_specialist': 'training_specialist',
                'implementation_consultant': 'implementation_consultant',

                # Emerging Technologies
                'iot_specialist': 'iot_specialist',
                'edge_computing_specialist': 'edge_computing_specialist',
                '5g_specialist': '5g_specialist',
                'metaverse_developer': 'metaverse_developer',

                # Additional System Specialists
                'automation_engineer': 'automation_engineer',
                'integration_specialist': 'integration_specialist',
                'api_integration_specialist': 'api_integration_specialist',
                'middleware_specialist': 'middleware_specialist',
                'database_administrator': 'database_administrator',
                'system_administrator': 'system_administrator',
                'linux_administrator': 'linux_administrator',
                'windows_administrator': 'windows_administrator',
                'virtualization_specialist': 'virtualization_specialist',
                'storage_specialist': 'storage_specialist',
                'backup_&_recovery_specialist': 'backup_recovery_specialist',
                'disaster_recovery_specialist': 'disaster_recovery_specialist',
                'monitoring_specialist': 'monitoring_specialist',
                'observability_engineer': 'observability_engineer',
                'release_manager': 'release_manager',
                'configuration_manager': 'configuration_manager',
                'change_management_specialist': 'change_management_specialist',
                'incident_manager': 'incident_manager',
                'problem_manager': 'problem_manager',
                'service_desk_analyst': 'service_desk_analyst',
                'vendor_manager': 'vendor_manager',
                'procurement_specialist': 'procurement_specialist',
                'contract_specialist': 'legal_agent',
                'budget_analyst': 'financial_analyst',
                'cost_optimization_specialist': 'financial_analyst',

                # Additional comprehensive mappings for failing agents
                '3d_designer': 'creative_design_agent',
                '5g_specialist': 'technical_agent',
                'ai_ethicist': 'legal_compliance_agent',
                'ai_researcher': 'research_agent',
                'api_developer': 'api_integrator',
                'api_gateway_architect': 'api_integrator',
                'api_integration_specialist': 'api_integrator',
                'ar/vr_designer': 'creative_design_agent',
                'arvr_designer': 'creative_design_agent',
                'aws_specialist': 'technical_agent',
                'accessibility_specialist': 'technical_agent',
                'agtech_specialist': 'technical_agent',
                'agile_coach': 'project_management_agent',
                'android_developer': 'technical_agent',
                'angular_developer': 'react_developer',
                'automation_engineer': 'technical_agent',
                'azure_specialist': 'technical_agent',
                'bi_analyst': 'data_analyst',
                'backend_engineer': 'technical_agent',
                'backup_recovery_specialist': 'technical_agent',
                'backup_&_recovery_specialist': 'technical_agent',
                'betting_analytics_expert': 'betting_analysis_specialist',
                'betting_compliance_officer': 'legal_compliance_agent',
                'betting_payment_processor': 'financial_agent',
                'betting_risk_manager': 'risk_assessment_agent',
                'big_data_engineer': 'data_analyst',
                'bioinformatics_specialist': 'data_analyst',
                'blockchain_developer': 'technical_agent',
                'c#_developer': 'technical_agent',
                'csharp_developer': 'technical_agent',
                'change_management_specialist': 'project_management_agent',
                'cloud_architect': 'technical_agent',
                'college_sports_specialist': 'sports_analytics_agent',
                'compliance_officer': 'legal_compliance_agent',
                'configuration_manager': 'technical_agent',
                'content_strategist': 'content_strategy_agent',
                'copywriter': 'content_creator',
                'crypto_analyst': 'financial_analyst',
                'customer_success_manager': 'business_agent',
                'cybersecurity_expert': 'security_auditor',
                'data_engineer': 'data_analyst',
                'database_administrator': 'database_optimizer',
                'database_architect': 'database_optimizer',
                'defi_specialist': 'financial_analyst',
                'disaster_recovery_specialist': 'technical_agent',
                'docker_specialist': 'technical_agent',
                'documentation_specialist': 'documentation_writer',
                'ecommerce_specialist': 'business_agent',
                'e-commerce_specialist': 'business_agent',
                'etl_specialist': 'data_analyst',
                'edtech_specialist': 'technical_agent',
                'edge_computing_specialist': 'technical_agent',
                'email_marketing_specialist': 'marketing_agent',
                'fintech_specialist': 'financial_agent',
                'frontend_engineer': 'react_developer',
                'fullstack_developer': 'react_developer',
                'gcp_specialist': 'technical_agent',
                'game_designer': 'creative_design_agent',
                'game_developer': 'technical_agent',
                'go_developer': 'technical_agent',
                'graphic_designer': 'creative_design_agent',
                'hr_specialist': 'business_agent',
                'handicapping_expert': 'sports_analytics_agent',
                'healthcare_specialist': 'technical_agent',
                'implementation_consultant': 'business_agent',
                'incident_manager': 'technical_agent',
                'integration_specialist': 'api_integrator',
                'interaction_designer': 'creative_design_agent',
                'iot_specialist': 'technical_agent',
                'java_developer': 'technical_agent',
                'javascript_developer': 'react_developer',
                'kubernetes_expert': 'technical_agent',
                'llm_specialist': 'prompt_engineer',
                'legaltech_specialist': 'legal_agent',
                'level_designer': 'creative_design_agent',
                'linux_administrator': 'technical_agent',
                'live_betting_engineer': 'live_betting_agent',
                'load_testing_specialist': 'technical_agent',
                'logistics_specialist': 'operations_agent',
                'metaverse_developer': 'technical_agent',
                'middleware_specialist': 'technical_agent',
                'mobile_developer': 'technical_agent',
                'monitoring_specialist': 'monitoring_dashboard',
                'motion_designer': 'creative_design_agent',
                'nft_specialist': 'technical_agent',
                'network_engineer': 'technical_agent',
                'observability_engineer': 'monitoring_dashboard',
                'odds_calculation_expert': 'odds_calculation_agent',
                'operations_manager': 'operations_agent',
                'php_developer': 'technical_agent',
                'parlay_system_developer': 'sports_analytics_agent',
                'penetration_tester': 'security_auditor',
                'performance_engineer': 'technical_agent',
                'podcast_producer': 'content_creator',
                'privacy_expert': 'legal_compliance_agent',
                'problem_manager': 'technical_agent',
                'procurement_specialist': 'business_agent',
                'product_designer': 'creative_design_agent',
                'product_manager': 'project_management_agent',
                'program_manager': 'project_management_agent',
                'project_manager': 'project_management_agent',
                'prop_bet_specialist': 'sports_analytics_agent',
                'proptech_specialist': 'technical_agent',
                'python_developer': 'technical_agent',
                'qa_engineer': 'technical_agent',
                'quantum_computing_researcher': 'research_agent',
                'release_manager': 'project_management_agent',
                'research_scientist': 'research_agent',
                'responsible_gaming_specialist': 'legal_compliance_agent',
                'robotics_engineer': 'technical_agent',
                'rust_developer': 'technical_agent',
                'seo_specialist': 'seo_specialist_agent',
                'sales_specialist': 'business_agent',
                'sales_agent': 'business_agent',
                'scrum_master': 'project_management_agent',
                'security_architect': 'security_auditor',
                'security_specialist': 'security_auditor',
                'service_desk_analyst': 'technical_agent',
                'site_reliability_engineer': 'technical_agent',
                'sre_engineer': 'technical_agent',
                'social_media_manager': 'marketing_agent',
                'solidity_developer': 'technical_agent',
                'sports_betting_specialist': 'sports_analytics_agent',
                'sports_data_integration_expert': 'sports_analytics_agent',
                'sports_statistician': 'sports_analytics_agent',
                'sportsbook_architect': 'sports_analytics_agent',
                'storage_specialist': 'technical_agent',
                'system_administrator': 'technical_agent',
                'technical_support_engineer': 'technical_agent',
                'technical_writer': 'documentation_writer',
                'terraform_expert': 'technical_agent',
                'test_automation_engineer': 'technical_agent',
                'training_specialist': 'business_agent',
                'typescript_developer': 'react_developer',
                'ui_designer': 'ui/ux_designer',
                'ux_designer': 'ui/ux_designer',
                'unity_developer': 'technical_agent',
                'unreal_developer': 'technical_agent',
                'vendor_manager': 'business_agent',
                'video_producer': 'content_creator',
                'virtualization_specialist': 'technical_agent',
                'vue_developer': 'react_developer',
                'web3_developer': 'technical_agent',
                'windows_administrator': 'technical_agent',
                'ios_developer': 'technical_agent'
            }

            if executor_agent_name in name_mappings:
                executor_agent_name = name_mappings[executor_agent_name]

            # Log the agent name being used
            logger.info(f"Using executor agent name: {executor_agent_name}")

            # Check if agent exists in the registry and provide detailed debugging
            if not hasattr(self.executor, 'agent_classes'):
                logger.error(f"❌ ConcreteAgentExecutor has no agent_classes attribute!")
                logger.error(f"Available executor attributes: {dir(self.executor)}")
                raise Exception(f"ConcreteAgentExecutor not properly initialized")

            if executor_agent_name not in self.executor.agent_classes:
                logger.error(f"❌ AGENT REGISTRY ISSUE: '{executor_agent_name}' not found!")
                logger.error(f"Original agent name: '{agent_name}'")
                logger.error(f"Mapped executor name: '{executor_agent_name}'")
                logger.error(f"Available agents in registry: {sorted(list(self.executor.agent_classes.keys()))}")

                # Send detailed error via WebSocket for debugging
                await self.channel_layer.group_send(
                    'ai_training',
                    {
                        'type': 'broadcast_learning_update',
                        'data': {
                            'event': 'agent_registry_error',
                            'agent': agent_name,
                            'executor_name': executor_agent_name,
                            'available_agents': sorted(list(self.executor.agent_classes.keys())),
                            'error': f"Agent '{executor_agent_name}' not found in registry with {len(self.executor.agent_classes)} agents",
                            'timestamp': str(timezone.now())
                        }
                    }
                )

                raise Exception(f"Agent '{executor_agent_name}' not found in registry with {len(self.executor.agent_classes)} agents")

            # Execute the agent using ConcreteAgentExecutor with proper task format
            logger.info(f"✅ Found agent in registry: {executor_agent_name}")
            executor_task = {
                'task_description': agent_config['description'],
                'input': task
            }

            result = await self.executor.execute_agent(executor_agent_name, executor_task)

            # Send WebSocket update about execution progress
            await self.channel_layer.group_send(
                'ai_training',
                {
                    'type': 'broadcast_learning_update',
                    'data': {
                        'event': 'agent_processing',
                        'agent': agent_name,
                        'task': agent_config['task'],
                        'status': 'completed' if result.get("success") else 'failed',
                        'timestamp': str(timezone.now())
                    }
                }
            )

            if result.get("success"):
                # Extract the actual output from the result
                # ConcreteAgentExecutor returns the result in 'result' field
                output = result.get("result", result.get("output", {}))

                # Store the result appropriately based on output type
                if agent_config["expected_output"] == "business_strategy":
                    # Store as a markdown document
                    content = self._format_business_strategy(output)
                    file_name = "business_strategy.md"

                elif agent_config["expected_output"] == "ml_architecture":
                    # Store as JSON specification
                    content = json.dumps(output, indent=2)
                    file_name = "ml_architecture.json"

                elif agent_config["expected_output"] == "database_schema":
                    # Store as SQL or JSON schema
                    content = self._format_database_schema(output)
                    file_name = "database_schema.sql"

                else:
                    # Default to JSON output
                    content = json.dumps(output, indent=2)
                    file_name = f"{agent_name.lower().replace(' ', '_')}_output.json"

                # Use sync_to_async for database operations
                from asgiref.sync import sync_to_async

                @sync_to_async
                def save_to_db():
                    return GeneratedCode.objects.create(
                        project=project,
                        filename=file_name,
                        file_path=f"ai_generated_projects/{project.name}/{file_name}",
                        content=content,
                        language='text' if file_name.endswith('.md') else 'json',
                        agent_creator=agent_name,
                        task_description=agent_config["description"],
                        is_latest=True,
                        execution_status='success'
                    )

                code_file = await save_to_db()

                # Calculate quality and complexity metrics based on output
                quality_score = self._calculate_quality_score(content, agent_config["expected_output"])
                complexity_score = self._calculate_complexity_score(content, agent_config["task"])

                # Send WebSocket update with completion details
                await self.channel_layer.group_send(
                    'ai_training',
                    {
                        'type': 'broadcast_learning_update',
                        'data': {
                            'event': 'agent_completed',
                            'agent': agent_name,
                            'task': agent_config['task'],
                            'file_created': file_name,
                            'content_length': len(content),
                            'output_type': agent_config["expected_output"],
                            'message': f"{agent_name} completed {agent_config['task']} - Created {file_name}",
                            'timestamp': str(timezone.now()),
                            'metrics': {
                                'lines_of_code': len(content.splitlines()) if content else 0,
                                'quality_score': quality_score,
                                'complexity_score': complexity_score,
                                'learning_progress': min(100, quality_score + (complexity_score * 0.3))
                            }
                        }
                    }
                )

                return {
                    "success": True,
                    "agent": agent_name,
                    "task": agent_config["task"],
                    "output": output,
                    "file_created": file_name,
                    "content_length": len(content)
                }
            else:
                logger.error(f"❌ Agent execution failed: {result.get('error')}")

                # Send WebSocket update for failure
                await self.channel_layer.group_send(
                    'ai_training',
                    {
                        'type': 'broadcast_learning_update',
                        'data': {
                            'event': 'agent_failed',
                            'agent': agent_name,
                            'task': agent_config['task'],
                            'error': result.get("error", "Unknown error"),
                            'message': f"{agent_name} failed: {result.get('error', 'Unknown error')}",
                            'timestamp': str(timezone.now())
                        }
                    }
                )

                return {
                    "success": False,
                    "agent": agent_name,
                    "error": result.get("error", "Unknown error")
                }

        except Exception as e:
            logger.error(f"❌ Error executing {agent_name}: {e}")

            # Send WebSocket update for exception
            await self.channel_layer.group_send(
                'ai_training',
                {
                    'type': 'broadcast_learning_update',
                    'data': {
                        'event': 'agent_error',
                        'agent': agent_name,
                        'error': str(e),
                        'message': f"{agent_name} encountered an error: {str(e)}",
                        'timestamp': str(timezone.now())
                    }
                }
            )

            return {
                "success": False,
                "agent": agent_name,
                "error": str(e)
            }

    def _format_business_strategy(self, output: Dict) -> str:
        """Format business strategy output as markdown"""
        md = f"# Business Strategy\n\n"
        md += f"Generated: {timezone.now()}\n\n"

        if isinstance(output, dict):
            for key, value in output.items():
                md += f"## {key.replace('_', ' ').title()}\n\n"
                if isinstance(value, list):
                    for item in value:
                        md += f"- {item}\n"
                else:
                    md += f"{value}\n"
                md += "\n"
        else:
            md += str(output)

        return md

    def _format_database_schema(self, output: Dict) -> str:
        """Format database schema as SQL"""
        sql = "-- Database Schema\n"
        sql += f"-- Generated: {timezone.now()}\n\n"

        if isinstance(output, dict):
            if "tables" in output:
                for table in output.get("tables", []):
                    sql += f"CREATE TABLE {table.get('name', 'unnamed')} (\n"
                    for column in table.get("columns", []):
                        sql += f"    {column},\n"
                    sql = sql.rstrip(",\n") + "\n);\n\n"
            else:
                sql += f"/* {json.dumps(output, indent=2)} */"
        else:
            sql += f"/* {str(output)} */"

        return sql

    def _calculate_quality_score(self, content: str, expected_output: str) -> float:
        """
        Calculate quality score based on content analysis.
        Returns a score between 0-100.
        """
        if not content:
            return 0.0

        base_score = 70.0  # Start with a good baseline

        # Content length bonus (more comprehensive = higher quality)
        length_factor = min(len(content) / 1000, 2.0)  # Cap at 2x bonus
        base_score += length_factor * 10

        # Structure bonus for different output types
        if expected_output == "business_strategy":
            if "##" in content and "- " in content:  # Has headings and lists
                base_score += 10
        elif expected_output == "ml_architecture":
            if "{" in content and "}" in content:  # JSON structure
                base_score += 10
        elif expected_output == "database_schema":
            if "CREATE TABLE" in content:  # SQL structure
                base_score += 15

        # Comprehensive content bonus
        if len(content.splitlines()) > 20:
            base_score += 5

        # Cap at 100
        return min(100.0, base_score)

    def _calculate_complexity_score(self, content: str, task_type: str) -> float:
        """
        Calculate complexity score based on task type and content.
        Returns a score between 0-100.
        """
        if not content:
            return 0.0

        base_complexity = 45.0  # Start with moderate complexity

        # Task-based complexity
        high_complexity_tasks = [
            "ml_architecture_design", "database_schema_design", "backend_architecture",
            "deep_learning_architecture", "cloud_infrastructure", "security_assessment"
        ]

        medium_complexity_tasks = [
            "business_analysis", "ui_design", "market_research", "content_strategy"
        ]

        if task_type in high_complexity_tasks:
            base_complexity += 25
        elif task_type in medium_complexity_tasks:
            base_complexity += 15
        else:
            base_complexity += 20

        # Content complexity indicators
        lines = len(content.splitlines())
        if lines > 50:
            base_complexity += 15
        elif lines > 20:
            base_complexity += 10

        # Technical depth indicators
        if any(term in content.lower() for term in ['algorithm', 'architecture', 'optimization', 'integration']):
            base_complexity += 10

        # Cap at 100
        return min(100.0, base_complexity)


def execute_agents_properly(agent_names: List[str], project: GeneratedProject, task_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Synchronous wrapper to execute agents properly.

    This ensures agents perform their actual specialized tasks,
    not just generate generic code files.
    """
    executor = ProperAgentExecutor()
    results = []

    # Run async execution in sync context
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        for agent_name in agent_names:
            result = loop.run_until_complete(
                executor.execute_agent_task(agent_name, project, task_config)
            )
            results.append(result)
            logger.info(f"✅ Executed {agent_name}: {result.get('task')} - Success: {result.get('success')}")
    finally:
        loop.close()

    return results