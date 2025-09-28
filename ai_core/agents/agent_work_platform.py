"""
AI Agent Work Execution Platform
Matches categorized opportunities to capable AI agents and executes work automatically

This is where we turn the platform from "job board" to "money-making machine"
"""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from django.core.cache import cache
from django.utils import timezone
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class AgentCapability(Enum):
    """What types of work agents can actually execute"""
    CONTENT_WRITING = "content_writing"
    CODE_DEVELOPMENT = "code_development"
    DATA_ANALYSIS = "data_analysis"
    GRAPHIC_DESIGN = "graphic_design"
    SOCIAL_MEDIA = "social_media"
    EMAIL_MARKETING = "email_marketing"
    CUSTOMER_SUPPORT = "customer_support"
    RESEARCH = "research"
    TRANSLATION = "translation"
    TUTORING = "tutoring"
    VIRTUAL_ASSISTANCE = "virtual_assistance"
    COPYWRITING = "copywriting"
    SEO_OPTIMIZATION = "seo_optimization"
    LEAD_GENERATION = "lead_generation"
    DATA_ENTRY = "data_entry"

@dataclass
class AgentWorker:
    """An AI agent capable of executing specific types of work"""
    agent_id: str
    name: str
    capabilities: List[AgentCapability]
    hourly_rate: float  # What we can charge clients
    success_rate: float  # Historical success rate (0.0 - 1.0)
    concurrent_jobs: int  # How many jobs it can handle simultaneously
    specialties: List[str]  # Specific skills/tools
    availability_hours: int  # Hours per day available
    current_workload: int = 0  # Currently assigned jobs

@dataclass
class ExecutableJob:
    """A job opportunity that an agent can actually execute"""
    opportunity_id: str
    title: str
    description: str
    required_capabilities: List[AgentCapability]
    estimated_hours: float
    client_budget: float
    deadline: datetime
    complexity_level: str  # beginner, intermediate, advanced
    deliverables: List[str]
    assigned_agent: Optional[str] = None
    status: str = "available"  # available, assigned, in_progress, completed, failed
    revenue_potential: float = 0.0

@dataclass
class AgentWorkSession:
    """A work session where an agent executes a job"""
    session_id: str
    agent_id: str
    job_id: str
    start_time: datetime
    estimated_completion: datetime
    deliverables_path: str
    progress: float = 0.0  # 0.0 - 1.0
    status: str = "starting"  # starting, working, reviewing, completed, failed
    revenue_earned: float = 0.0


class AgentWorkPlatform:
    """Platform that matches opportunities to agents and executes work for revenue"""

    def __init__(self):
        self.available_agents = self._initialize_agent_workforce()
        self.active_sessions = {}
        self.completed_jobs = []
        self.total_revenue = 0.0

    def _initialize_agent_workforce(self) -> List[AgentWorker]:
        """Initialize our AI workforce with their capabilities"""
        return [
            # Content Creation Agents
            AgentWorker(
                agent_id="content_specialist",
                name="Content Creation Specialist",
                capabilities=[AgentCapability.CONTENT_WRITING, AgentCapability.COPYWRITING, AgentCapability.SEO_OPTIMIZATION],
                hourly_rate=45.0,
                success_rate=0.92,
                concurrent_jobs=3,
                specialties=["blog posts", "articles", "web copy", "social media", "email campaigns"],
                availability_hours=16
            ),

            # Development Agents
            AgentWorker(
                agent_id="python_developer",
                name="Python Development Agent",
                capabilities=[AgentCapability.CODE_DEVELOPMENT, AgentCapability.DATA_ANALYSIS],
                hourly_rate=75.0,
                success_rate=0.88,
                concurrent_jobs=2,
                specialties=["Python", "Django", "API development", "data analysis", "automation"],
                availability_hours=12
            ),

            AgentWorker(
                agent_id="web_developer",
                name="Web Development Agent",
                capabilities=[AgentCapability.CODE_DEVELOPMENT],
                hourly_rate=65.0,
                success_rate=0.85,
                concurrent_jobs=2,
                specialties=["React", "JavaScript", "HTML/CSS", "responsive design"],
                availability_hours=14
            ),

            # Data & Research Agents
            AgentWorker(
                agent_id="data_analyst",
                name="Data Analysis Agent",
                capabilities=[AgentCapability.DATA_ANALYSIS, AgentCapability.RESEARCH],
                hourly_rate=55.0,
                success_rate=0.90,
                concurrent_jobs=4,
                specialties=["Excel", "Python pandas", "data visualization", "market research"],
                availability_hours=18
            ),

            # Creative Agents
            AgentWorker(
                agent_id="graphic_designer",
                name="Graphic Design Agent",
                capabilities=[AgentCapability.GRAPHIC_DESIGN],
                hourly_rate=50.0,
                success_rate=0.87,
                concurrent_jobs=3,
                specialties=["logos", "social media graphics", "presentations", "infographics"],
                availability_hours=12
            ),

            # Marketing Agents
            AgentWorker(
                agent_id="social_media_manager",
                name="Social Media Management Agent",
                capabilities=[AgentCapability.SOCIAL_MEDIA, AgentCapability.CONTENT_WRITING],
                hourly_rate=35.0,
                success_rate=0.91,
                concurrent_jobs=5,
                specialties=["Instagram", "Twitter", "LinkedIn", "content calendars", "engagement"],
                availability_hours=20
            ),

            AgentWorker(
                agent_id="email_marketer",
                name="Email Marketing Agent",
                capabilities=[AgentCapability.EMAIL_MARKETING, AgentCapability.COPYWRITING],
                hourly_rate=40.0,
                success_rate=0.89,
                concurrent_jobs=4,
                specialties=["email campaigns", "newsletters", "automation", "A/B testing"],
                availability_hours=16
            ),

            # Support & Admin Agents
            AgentWorker(
                agent_id="virtual_assistant",
                name="Virtual Assistant Agent",
                capabilities=[AgentCapability.VIRTUAL_ASSISTANCE, AgentCapability.DATA_ENTRY, AgentCapability.CUSTOMER_SUPPORT],
                hourly_rate=25.0,
                success_rate=0.94,
                concurrent_jobs=6,
                specialties=["scheduling", "email management", "data entry", "customer service"],
                availability_hours=22
            ),

            AgentWorker(
                agent_id="research_specialist",
                name="Research Specialist Agent",
                capabilities=[AgentCapability.RESEARCH, AgentCapability.DATA_ENTRY],
                hourly_rate=30.0,
                success_rate=0.93,
                concurrent_jobs=5,
                specialties=["market research", "competitor analysis", "lead generation"],
                availability_hours=20
            ),

            # Specialized Agents
            AgentWorker(
                agent_id="translator",
                name="Translation Agent",
                capabilities=[AgentCapability.TRANSLATION],
                hourly_rate=35.0,
                success_rate=0.86,
                concurrent_jobs=3,
                specialties=["English", "Spanish", "French", "document translation"],
                availability_hours=18
            ),

            AgentWorker(
                agent_id="tutor_agent",
                name="Online Tutoring Agent",
                capabilities=[AgentCapability.TUTORING],
                hourly_rate=40.0,
                success_rate=0.88,
                concurrent_jobs=2,
                specialties=["Python programming", "data science", "math", "personalized learning"],
                availability_hours=10
            )
        ]

    async def analyze_opportunity_for_agent_execution(self, opportunity: Dict) -> Optional[ExecutableJob]:
        """Analyze if an opportunity can be executed by our agents"""
        try:
            # Extract key information
            title = opportunity.get('title', '').lower()
            description = opportunity.get('description', '').lower()
            category = opportunity.get('category', {})
            financial = opportunity.get('financial', {})

            # Determine required capabilities based on content analysis
            required_capabilities = []

            # Content writing detection
            content_keywords = ['content', 'writing', 'blog', 'article', 'copywriting', 'copy', 'social media']
            if any(keyword in title or keyword in description for keyword in content_keywords):
                required_capabilities.append(AgentCapability.CONTENT_WRITING)

            # Development detection
            dev_keywords = ['developer', 'programming', 'python', 'javascript', 'react', 'django', 'api', 'web dev']
            if any(keyword in title or keyword in description for keyword in dev_keywords):
                required_capabilities.append(AgentCapability.CODE_DEVELOPMENT)

            # Data analysis detection
            data_keywords = ['data', 'analysis', 'excel', 'research', 'analytics', 'reporting']
            if any(keyword in title or keyword in description for keyword in data_keywords):
                required_capabilities.append(AgentCapability.DATA_ANALYSIS)

            # Design detection
            design_keywords = ['design', 'graphic', 'logo', 'visual', 'creative', 'illustration']
            if any(keyword in title or keyword in description for keyword in design_keywords):
                required_capabilities.append(AgentCapability.GRAPHIC_DESIGN)

            # Marketing detection
            marketing_keywords = ['marketing', 'social media', 'email', 'campaign', 'promotion']
            if any(keyword in title or keyword in description for keyword in marketing_keywords):
                if 'email' in title or 'email' in description:
                    required_capabilities.append(AgentCapability.EMAIL_MARKETING)
                if 'social' in title or 'social' in description:
                    required_capabilities.append(AgentCapability.SOCIAL_MEDIA)

            # Virtual assistance detection
            va_keywords = ['virtual assistant', 'admin', 'data entry', 'support', 'customer service']
            if any(keyword in title or keyword in description for keyword in va_keywords):
                required_capabilities.append(AgentCapability.VIRTUAL_ASSISTANCE)

            # Research detection
            research_keywords = ['research', 'analysis', 'market research', 'competitor', 'lead generation']
            if any(keyword in title or keyword in description for keyword in research_keywords):
                required_capabilities.append(AgentCapability.RESEARCH)

            # Translation detection
            translation_keywords = ['translation', 'translate', 'language', 'multilingual']
            if any(keyword in title or keyword in description for keyword in translation_keywords):
                required_capabilities.append(AgentCapability.TRANSLATION)

            # Tutoring detection
            tutoring_keywords = ['tutor', 'teach', 'education', 'training', 'lesson']
            if any(keyword in title or keyword in description for keyword in tutoring_keywords):
                required_capabilities.append(AgentCapability.TUTORING)

            # Skip if no matching capabilities
            if not required_capabilities:
                return None

            # Estimate complexity and hours
            complexity_level = "intermediate"
            estimated_hours = 8.0  # Default

            if any(word in description for word in ['senior', 'expert', 'advanced', 'complex']):
                complexity_level = "advanced"
                estimated_hours = 20.0
            elif any(word in description for word in ['simple', 'basic', 'easy', 'entry']):
                complexity_level = "beginner"
                estimated_hours = 4.0

            # Extract budget
            budget_max = financial.get('budget_max', 0)
            budget_min = financial.get('budget_min', 0)
            client_budget = budget_max if budget_max > 0 else budget_min

            # Set deadline (default 1 week from now)
            deadline = timezone.now() + timedelta(days=7)

            # Generate deliverables based on capabilities
            deliverables = []
            if AgentCapability.CONTENT_WRITING in required_capabilities:
                deliverables.extend(["Written content", "SEO optimization", "Revisions"])
            if AgentCapability.CODE_DEVELOPMENT in required_capabilities:
                deliverables.extend(["Source code", "Documentation", "Testing"])
            if AgentCapability.GRAPHIC_DESIGN in required_capabilities:
                deliverables.extend(["Design files", "Multiple formats", "Source files"])

            if not deliverables:
                deliverables = ["Completed work", "Documentation", "Revisions"]

            executable_job = ExecutableJob(
                opportunity_id=opportunity.get('id', ''),
                title=opportunity.get('title', ''),
                description=opportunity.get('description', ''),
                required_capabilities=required_capabilities,
                estimated_hours=estimated_hours,
                client_budget=client_budget,
                deadline=deadline,
                complexity_level=complexity_level,
                deliverables=deliverables,
                revenue_potential=client_budget * 0.8  # 80% of client budget as our take
            )

            logger.info(f"✅ Created executable job: {executable_job.title}")
            logger.info(f"   💰 Revenue potential: ${executable_job.revenue_potential}")
            logger.info(f"   🤖 Required capabilities: {[cap.value for cap in required_capabilities]}")

            return executable_job

        except Exception as e:
            logger.error(f"Error analyzing opportunity for agent execution: {e}")
            return None

    def find_best_agent_for_job(self, job: ExecutableJob) -> Optional[AgentWorker]:
        """Find the best available agent to execute a job"""
        try:
            suitable_agents = []

            for agent in self.available_agents:
                # Check if agent has required capabilities
                has_required_capabilities = any(
                    capability in agent.capabilities
                    for capability in job.required_capabilities
                )

                if not has_required_capabilities:
                    continue

                # Check availability
                if agent.current_workload >= agent.concurrent_jobs:
                    continue

                # Calculate match score
                capability_match = len(set(job.required_capabilities) & set(agent.capabilities)) / len(job.required_capabilities)
                success_score = agent.success_rate
                availability_score = (agent.concurrent_jobs - agent.current_workload) / agent.concurrent_jobs

                match_score = (capability_match * 0.5) + (success_score * 0.3) + (availability_score * 0.2)

                suitable_agents.append((agent, match_score))

            if not suitable_agents:
                return None

            # Return the best match
            best_agent, best_score = max(suitable_agents, key=lambda x: x[1])

            logger.info(f"🎯 Best agent for '{job.title}': {best_agent.name} (score: {best_score:.2f})")

            return best_agent

        except Exception as e:
            logger.error(f"Error finding best agent for job: {e}")
            return None

    async def assign_job_to_agent(self, job: ExecutableJob, agent: AgentWorker) -> Optional[AgentWorkSession]:
        """Assign a job to an agent and start execution"""
        try:
            session_id = f"session_{timezone.now().timestamp()}"

            # Update agent workload
            agent.current_workload += 1

            # Calculate completion time based on estimated hours
            completion_time = timezone.now() + timedelta(hours=job.estimated_hours)

            # Create work session
            session = AgentWorkSession(
                session_id=session_id,
                agent_id=agent.agent_id,
                job_id=job.opportunity_id,
                start_time=timezone.now(),
                estimated_completion=completion_time,
                deliverables_path=f"/work_output/{session_id}/",
                progress=0.0,
                status="starting",
                revenue_earned=0.0
            )

            # Update job status
            job.assigned_agent = agent.agent_id
            job.status = "assigned"

            # Store session
            self.active_sessions[session_id] = session

            logger.info(f"🚀 Assigned job '{job.title}' to agent '{agent.name}'")
            logger.info(f"   📅 Expected completion: {completion_time}")
            logger.info(f"   💰 Potential revenue: ${job.revenue_potential}")

            # Start the work execution
            await self._execute_work_session(session, job, agent)

            return session

        except Exception as e:
            logger.error(f"Error assigning job to agent: {e}")
            return None

    async def _execute_work_session(self, session: AgentWorkSession, job: ExecutableJob, agent: AgentWorker):
        """Simulate agent executing work (in real implementation, this would call actual agent APIs)"""
        try:
            logger.info(f"🔄 Starting work execution for session {session.session_id}")

            # Update session status
            session.status = "working"
            session.progress = 0.1

            # Simulate work phases
            work_phases = [
                ("Planning and setup", 0.2),
                ("Initial work", 0.4),
                ("Development/creation", 0.7),
                ("Review and refinement", 0.9),
                ("Final delivery", 1.0)
            ]

            for phase_name, target_progress in work_phases:
                logger.info(f"   📋 {phase_name} ({target_progress*100:.0f}%)")

                # Simulate work time (in real implementation, this would be actual agent work)
                await asyncio.sleep(2)  # Shortened for demo

                session.progress = target_progress

                # Cache progress updates
                cache.set(f"work_session_{session.session_id}", asdict(session), 3600)

            # Complete the work
            session.status = "completed"
            session.progress = 1.0
            session.revenue_earned = job.revenue_potential

            # Update job status
            job.status = "completed"

            # Update agent availability
            agent.current_workload -= 1

            # Track revenue
            self.total_revenue += session.revenue_earned
            self.completed_jobs.append(job)

            # Remove from active sessions
            if session.session_id in self.active_sessions:
                del self.active_sessions[session.session_id]

            logger.info(f"✅ Work session completed!")
            logger.info(f"   💰 Revenue earned: ${session.revenue_earned}")
            logger.info(f"   📊 Total platform revenue: ${self.total_revenue}")

        except Exception as e:
            logger.error(f"Error executing work session: {e}")
            session.status = "failed"
            agent.current_workload -= 1

    async def process_opportunities_for_agent_execution(self) -> Dict[str, Any]:
        """Main function: Process categorized opportunities and assign to agents for execution"""
        try:
            logger.info("🚀 Starting Agent Work Platform processing...")

            # Get categorized opportunities from cache
            opportunities = cache.get('categorized_opportunities', [])

            if not opportunities:
                logger.warning("No categorized opportunities found in cache")
                return {
                    'success': False,
                    'message': 'No opportunities available for processing'
                }

            executable_jobs = []
            assigned_sessions = []

            # Analyze each opportunity for agent execution
            for opportunity in opportunities[:10]:  # Process first 10 for demo
                executable_job = await self.analyze_opportunity_for_agent_execution(opportunity)

                if executable_job:
                    executable_jobs.append(executable_job)

                    # Find and assign agent
                    best_agent = self.find_best_agent_for_job(executable_job)

                    if best_agent:
                        session = await self.assign_job_to_agent(executable_job, best_agent)
                        if session:
                            assigned_sessions.append(session)

            # Cache results
            cache.set('executable_jobs', [asdict(job) for job in executable_jobs], 3600)
            cache.set('active_work_sessions', [asdict(session) for session in assigned_sessions], 3600)
            cache.set('platform_total_revenue', self.total_revenue, 3600)

            result = {
                'success': True,
                'opportunities_analyzed': len(opportunities),
                'executable_jobs_created': len(executable_jobs),
                'jobs_assigned_to_agents': len(assigned_sessions),
                'potential_revenue': sum(job.revenue_potential for job in executable_jobs),
                'agents_working': len(assigned_sessions),
                'total_platform_revenue': self.total_revenue,
                'active_sessions': [asdict(session) for session in assigned_sessions]
            }

            logger.info(f"🎯 Agent Work Platform Results:")
            logger.info(f"   📊 {len(executable_jobs)} executable jobs created")
            logger.info(f"   🤖 {len(assigned_sessions)} agents assigned and working")
            logger.info(f"   💰 ${sum(job.revenue_potential for job in executable_jobs):,.2f} potential revenue")

            return result

        except Exception as e:
            logger.error(f"Error processing opportunities for agent execution: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_platform_status(self) -> Dict[str, Any]:
        """Get current platform status and metrics"""
        try:
            active_sessions = list(self.active_sessions.values())

            # Calculate agent utilization
            total_capacity = sum(agent.concurrent_jobs * agent.availability_hours for agent in self.available_agents)
            current_workload = sum(agent.current_workload * agent.availability_hours for agent in self.available_agents)
            utilization_rate = (current_workload / total_capacity) if total_capacity > 0 else 0

            return {
                'total_agents': len(self.available_agents),
                'agents_working': len([agent for agent in self.available_agents if agent.current_workload > 0]),
                'active_work_sessions': len(active_sessions),
                'completed_jobs': len(self.completed_jobs),
                'total_revenue': self.total_revenue,
                'agent_utilization_rate': utilization_rate,
                'daily_revenue_potential': sum(
                    agent.hourly_rate * agent.availability_hours * agent.concurrent_jobs
                    for agent in self.available_agents
                ),
                'agent_breakdown': [
                    {
                        'name': agent.name,
                        'capabilities': [cap.value for cap in agent.capabilities],
                        'hourly_rate': agent.hourly_rate,
                        'current_workload': agent.current_workload,
                        'max_concurrent': agent.concurrent_jobs,
                        'availability_hours': agent.availability_hours
                    }
                    for agent in self.available_agents
                ]
            }

        except Exception as e:
            logger.error(f"Error getting platform status: {e}")
            return {'error': str(e)}


# Global platform instance
agent_work_platform = AgentWorkPlatform()

async def activate_agent_work_platform() -> Dict[str, Any]:
    """Activate the agent work platform to start making money"""
    return await agent_work_platform.process_opportunities_for_agent_execution()

def get_agent_work_platform_status() -> Dict[str, Any]:
    """Get agent work platform status"""
    return agent_work_platform.get_platform_status()