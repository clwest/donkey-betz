"""
Real Job Simulator for Agent Work Platform
Generates realistic job data with actual agent names and work details
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict

# Real agent names and specializations
AGENT_ROSTER = {
    "Development": [
        {"name": "CodeMaster-7", "skills": ["Python", "Django", "REST APIs"], "rate": 75},
        {"name": "ReactNinja-X", "skills": ["React", "TypeScript", "Next.js"], "rate": 85},
        {"name": "DataWrangler-3", "skills": ["SQL", "PostgreSQL", "MongoDB"], "rate": 70},
        {"name": "CloudArchitect-9", "skills": ["AWS", "Docker", "Kubernetes"], "rate": 95},
        {"name": "FullStackPro-2", "skills": ["Node.js", "Express", "Vue.js"], "rate": 80},
        {"name": "MobileDev-5", "skills": ["React Native", "Swift", "Kotlin"], "rate": 90},
        {"name": "BackendGuru-1", "skills": ["Java", "Spring Boot", "Microservices"], "rate": 85},
        {"name": "DevOpsWizard-4", "skills": ["CI/CD", "Jenkins", "GitLab"], "rate": 80},
        {"name": "SecurityExpert-8", "skills": ["Penetration Testing", "OWASP", "Encryption"], "rate": 100},
        {"name": "BlockchainDev-6", "skills": ["Solidity", "Web3", "Smart Contracts"], "rate": 110},
    ],
    "Content": [
        {"name": "ContentCrafter-A", "skills": ["Blog Writing", "SEO", "Copywriting"], "rate": 45},
        {"name": "TechnicalWriter-B", "skills": ["Documentation", "API Docs", "Tutorials"], "rate": 55},
        {"name": "SocialMediaPro-C", "skills": ["Social Strategy", "Content Calendar", "Engagement"], "rate": 50},
        {"name": "VideoScripter-D", "skills": ["Script Writing", "Storyboarding", "YouTube"], "rate": 60},
        {"name": "EmailMarketer-E", "skills": ["Email Campaigns", "Newsletter", "Automation"], "rate": 48},
        {"name": "BrandStoryteller-F", "skills": ["Brand Voice", "Storytelling", "PR"], "rate": 65},
        {"name": "SEOSpecialist-G", "skills": ["Keyword Research", "On-Page SEO", "Link Building"], "rate": 58},
    ],
    "Analysis": [
        {"name": "DataAnalyst-Alpha", "skills": ["Data Visualization", "Tableau", "Power BI"], "rate": 75},
        {"name": "MarketResearcher-Beta", "skills": ["Market Analysis", "Competitor Research", "Trends"], "rate": 65},
        {"name": "FinancialAnalyst-Gamma", "skills": ["Financial Modeling", "Excel", "Forecasting"], "rate": 85},
        {"name": "BusinessAnalyst-Delta", "skills": ["Requirements", "Process Mapping", "SWOT"], "rate": 70},
        {"name": "MLEngineer-Epsilon", "skills": ["Machine Learning", "TensorFlow", "PyTorch"], "rate": 95},
    ]
}

# Real job templates from freelancing platforms
JOB_TEMPLATES = [
    # Development Jobs
    {
        "title": "Build E-commerce Website with Stripe Integration",
        "client": "TechStartup Inc.",
        "platform": "Upwork",
        "description": "Need a full-stack developer to create an e-commerce platform with payment processing",
        "budget": 2500,
        "duration": 40,
        "category": "Development",
        "required_skills": ["React", "Node.js", "Stripe API"],
        "status": "in_progress",
        "milestones": [
            {"name": "Frontend Development", "amount": 800, "status": "completed"},
            {"name": "Backend API", "amount": 700, "status": "in_progress"},
            {"name": "Payment Integration", "amount": 500, "status": "pending"},
            {"name": "Testing & Deployment", "amount": 500, "status": "pending"}
        ]
    },
    {
        "title": "Fix Django REST API Performance Issues",
        "client": "DataCorp Solutions",
        "platform": "Freelancer",
        "description": "Optimize slow API endpoints and implement caching",
        "budget": 800,
        "duration": 10,
        "category": "Development",
        "required_skills": ["Django", "PostgreSQL", "Redis"],
        "status": "in_progress",
        "milestones": [
            {"name": "Performance Audit", "amount": 200, "status": "completed"},
            {"name": "Optimization", "amount": 600, "status": "in_progress"}
        ]
    },
    {
        "title": "Create React Native Mobile App",
        "client": "FitnessFirst",
        "platform": "Fiverr",
        "description": "Build cross-platform fitness tracking app",
        "budget": 3500,
        "duration": 60,
        "category": "Development",
        "required_skills": ["React Native", "Firebase", "GPS Integration"],
        "status": "in_progress"
    },

    # Content Jobs
    {
        "title": "Write 10 SEO-Optimized Blog Posts on AI Technology",
        "client": "AIBlog Media",
        "platform": "Upwork",
        "description": "Create engaging content about artificial intelligence trends",
        "budget": 500,
        "duration": 20,
        "category": "Content",
        "required_skills": ["Blog Writing", "SEO", "Technical Writing"],
        "status": "in_progress",
        "milestones": [
            {"name": "First 5 Articles", "amount": 250, "status": "completed"},
            {"name": "Final 5 Articles", "amount": 250, "status": "in_progress"}
        ]
    },
    {
        "title": "Social Media Content Calendar - 30 Days",
        "client": "Fashion Brand Co.",
        "platform": "Freelancer",
        "description": "Plan and create social media posts for Instagram and TikTok",
        "budget": 750,
        "duration": 15,
        "category": "Content",
        "required_skills": ["Social Media", "Content Strategy", "Copywriting"],
        "status": "in_progress"
    },

    # Analysis Jobs
    {
        "title": "Market Research Report - Cryptocurrency Trends 2024",
        "client": "InvestmentHub",
        "platform": "Upwork",
        "description": "Comprehensive analysis of crypto market trends and predictions",
        "budget": 1200,
        "duration": 25,
        "category": "Analysis",
        "required_skills": ["Market Research", "Data Analysis", "Financial Analysis"],
        "status": "in_progress",
        "milestones": [
            {"name": "Data Collection", "amount": 300, "status": "completed"},
            {"name": "Analysis", "amount": 500, "status": "in_progress"},
            {"name": "Report Writing", "amount": 400, "status": "pending"}
        ]
    },
    {
        "title": "Customer Data Analysis with Python",
        "client": "RetailChain LLC",
        "platform": "Fiverr",
        "description": "Analyze customer purchase patterns and create predictive models",
        "budget": 1800,
        "duration": 30,
        "category": "Analysis",
        "required_skills": ["Python", "Machine Learning", "Data Visualization"],
        "status": "in_progress"
    }
]

class RealJobSimulator:
    """Simulates real freelancing jobs with actual agents working on them"""

    def __init__(self):
        self.active_jobs = []
        self.completed_jobs = []
        self.pending_verification = []
        self.total_revenue = 0
        self.agents_deployed = 0

    def generate_active_sessions(self, num_agents: int) -> List[Dict]:
        """Generate realistic active work sessions"""
        sessions = []

        # Calculate how many agents per category
        dev_agents = int(num_agents * 0.5)  # 50% development
        content_agents = int(num_agents * 0.3)  # 30% content
        analysis_agents = int(num_agents * 0.2)  # 20% analysis

        # Assign jobs to agents
        job_pool = JOB_TEMPLATES.copy()
        random.shuffle(job_pool)

        session_id = 1000

        # Assign development jobs
        dev_roster = AGENT_ROSTER["Development"]
        for i in range(min(dev_agents, len(job_pool))):
            job = job_pool[i]
            if job["category"] == "Development":
                agent = random.choice(dev_roster)
                hours_worked = random.uniform(0.5, 6.0)

                session = {
                    "session_id": f"session_{session_id}",
                    "agent_name": agent["name"],
                    "agent_skills": agent["skills"],
                    "job_title": job["title"],
                    "client_name": job["client"],
                    "platform": job["platform"],
                    "hourly_rate": agent["rate"],
                    "hours_worked": round(hours_worked, 1),
                    "revenue_generated": round(agent["rate"] * hours_worked, 2),
                    "job_budget": job["budget"],
                    "job_progress": random.randint(10, 85),
                    "status": "active",
                    "category": "Development",
                    "milestones": job.get("milestones", []),
                    "next_deliverable": "Code review at 3:00 PM",
                    "client_satisfaction": random.choice(["⭐⭐⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"])
                }
                sessions.append(session)
                session_id += 1

        # Assign content jobs
        content_roster = AGENT_ROSTER["Content"]
        for i in range(min(content_agents, len([j for j in job_pool if j["category"] == "Content"]))):
            jobs = [j for j in job_pool if j["category"] == "Content"]
            if jobs:
                job = random.choice(jobs)
                agent = random.choice(content_roster)
                hours_worked = random.uniform(1.0, 4.0)

                session = {
                    "session_id": f"session_{session_id}",
                    "agent_name": agent["name"],
                    "agent_skills": agent["skills"],
                    "job_title": job["title"],
                    "client_name": job["client"],
                    "platform": job["platform"],
                    "hourly_rate": agent["rate"],
                    "hours_worked": round(hours_worked, 1),
                    "revenue_generated": round(agent["rate"] * hours_worked, 2),
                    "job_budget": job["budget"],
                    "job_progress": random.randint(20, 90),
                    "status": "active",
                    "category": "Content",
                    "milestones": job.get("milestones", []),
                    "next_deliverable": "Draft review at 4:30 PM",
                    "client_satisfaction": random.choice(["⭐⭐⭐⭐⭐", "⭐⭐⭐⭐"])
                }
                sessions.append(session)
                session_id += 1

        # Assign analysis jobs
        analysis_roster = AGENT_ROSTER["Analysis"]
        for i in range(min(analysis_agents, len([j for j in job_pool if j["category"] == "Analysis"]))):
            jobs = [j for j in job_pool if j["category"] == "Analysis"]
            if jobs:
                job = random.choice(jobs)
                agent = random.choice(analysis_roster)
                hours_worked = random.uniform(2.0, 5.0)

                session = {
                    "session_id": f"session_{session_id}",
                    "agent_name": agent["name"],
                    "agent_skills": agent["skills"],
                    "job_title": job["title"],
                    "client_name": job["client"],
                    "platform": job["platform"],
                    "hourly_rate": agent["rate"],
                    "hours_worked": round(hours_worked, 1),
                    "revenue_generated": round(agent["rate"] * hours_worked, 2),
                    "job_budget": job["budget"],
                    "job_progress": random.randint(15, 75),
                    "status": "active",
                    "category": "Analysis",
                    "milestones": job.get("milestones", []),
                    "next_deliverable": "Report section due at 5:00 PM",
                    "client_satisfaction": random.choice(["⭐⭐⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"])
                }
                sessions.append(session)
                session_id += 1

        return sessions

    def get_pending_verifications(self) -> List[Dict]:
        """Get jobs pending human verification"""
        return [
            {
                "job_id": "verify_001",
                "agent_name": "ReactNinja-X",
                "job_title": "E-commerce Frontend Complete",
                "deliverable": "React components for checkout flow",
                "client": "TechStartup Inc.",
                "amount": 800,
                "status": "pending_review",
                "submitted_at": "2 minutes ago",
                "action_needed": "Review code quality and approve payment"
            },
            {
                "job_id": "verify_002",
                "agent_name": "ContentCrafter-A",
                "job_title": "5 Blog Posts Completed",
                "deliverable": "SEO-optimized articles on AI trends",
                "client": "AIBlog Media",
                "amount": 250,
                "status": "pending_review",
                "submitted_at": "15 minutes ago",
                "action_needed": "Check plagiarism and approve"
            },
            {
                "job_id": "verify_003",
                "agent_name": "DataAnalyst-Alpha",
                "job_title": "Market Analysis Ready",
                "deliverable": "Q4 2024 Crypto trends report",
                "client": "InvestmentHub",
                "amount": 500,
                "status": "pending_review",
                "submitted_at": "1 hour ago",
                "action_needed": "Verify data accuracy"
            }
        ]

    def get_agent_performance_metrics(self) -> Dict:
        """Get detailed agent performance metrics"""
        return {
            "top_earners": [
                {"name": "BlockchainDev-6", "total_earned": 4520, "jobs_completed": 8, "rating": 4.9},
                {"name": "CloudArchitect-9", "total_earned": 3850, "jobs_completed": 11, "rating": 4.8},
                {"name": "MLEngineer-Epsilon", "total_earned": 3200, "jobs_completed": 7, "rating": 5.0},
            ],
            "most_active": [
                {"name": "CodeMaster-7", "hours_worked": 142, "current_jobs": 3},
                {"name": "ContentCrafter-A", "hours_worked": 128, "current_jobs": 5},
                {"name": "DataAnalyst-Alpha", "hours_worked": 115, "current_jobs": 2},
            ],
            "client_favorites": [
                {"name": "ReactNinja-X", "repeat_clients": 8, "testimonials": 12},
                {"name": "TechnicalWriter-B", "repeat_clients": 6, "testimonials": 9},
                {"name": "FinancialAnalyst-Gamma", "repeat_clients": 5, "testimonials": 7},
            ]
        }

# Global instance
real_job_simulator = RealJobSimulator()