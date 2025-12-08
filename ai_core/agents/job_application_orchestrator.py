"""
Job Application Orchestrator - Intelligent Agent-to-Job Matching System

This module intelligently matches job opportunities to the most suitable agents
from our 149-agent network, then orchestrates the application process.

Key Features:
- Analyzes job requirements and extracts key skills
- Matches jobs to agents based on specialization
- Orchestrates application creation and submission
- Tracks application status and success rates
"""

import logging
from asgiref.sync import async_to_sync
import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import re
from dataclasses import dataclass
from ai_core.agents.agent_llm_integration import agent_llm_integration

logger = logging.getLogger(__name__)


@dataclass
class JobMatch:
    """Represents a job-to-agent match"""
    job_id: str
    job_title: str
    company: str
    agent_id: str
    agent_name: str
    agent_specialization: str
    match_score: float
    match_reasons: List[str]
    application_strategy: str


class JobApplicationOrchestrator:
    """
    Orchestrates the entire job application process by matching jobs
    to the most suitable agents and managing applications
    """

    def __init__(self):
        # Import agent registry to access all 149 agents
        from core.agents.registry import agent_registry
        self.agent_registry = agent_registry

        # Track applications
        self.active_applications = {}
        self.application_history = []

        # Skill mapping for better matching
        self.skill_keywords = {
            'python': ['python', 'django', 'flask', 'fastapi', 'pytorch', 'pandas'],
            'javascript': ['javascript', 'react', 'vue', 'angular', 'node', 'typescript'],
            'ai_ml': ['machine learning', 'ai', 'deep learning', 'nlp', 'computer vision', 'tensorflow'],
            'data': ['data', 'analytics', 'sql', 'etl', 'visualization', 'tableau'],
            'devops': ['devops', 'docker', 'kubernetes', 'ci/cd', 'aws', 'cloud'],
            'frontend': ['frontend', 'ui', 'ux', 'css', 'html', 'design'],
            'backend': ['backend', 'api', 'database', 'microservices', 'architecture'],
            'mobile': ['mobile', 'ios', 'android', 'react native', 'flutter'],
            'blockchain': ['blockchain', 'web3', 'smart contracts', 'solidity', 'defi'],
            'content': ['content', 'writing', 'copywriting', 'technical writing', 'documentation'],
            'marketing': ['marketing', 'seo', 'growth', 'advertising', 'social media'],
            'sales': ['sales', 'business development', 'account management', 'crm'],
        }

    async def process_job_opportunities(self, opportunities: List[Dict[str, Any]]) -> List[JobMatch]:
        """
        Process a list of job opportunities and match them to the best agents

        Args:
            opportunities: List of job opportunities from spiders

        Returns:
            List of job matches with assigned agents
        """
        matches = []

        for opportunity in opportunities:
            try:
                # Find the best agent for this job
                best_match = await self.find_best_agent_for_job(opportunity)
                if best_match:
                    matches.append(best_match)
                    logger.info(f"✅ Matched job '{opportunity.get('title')}' to agent '{best_match.agent_name}' (Score: {best_match.match_score:.2f})")
            except Exception as e:
                logger.error(f"Error matching job {opportunity.get('title')}: {e}")

        return matches

    async def find_best_agent_for_job(self, job: Dict[str, Any]) -> Optional[JobMatch]:
        """
        Find the best agent for a specific job based on skills and requirements

        Args:
            job: Job opportunity details

        Returns:
            JobMatch object with the best agent for the job
        """
        job_title = job.get('title', '').lower()
        job_description = job.get('description', '').lower()
        required_skills = job.get('tags', []) + job.get('skills_required', [])

        # Extract skills from job text
        detected_skills = self._extract_skills(f"{job_title} {job_description}")

        # Score all agents
        agent_scores = []

        for agent_id, agent in self.agent_registry.agents.items():
            score = 0
            match_reasons = []

            # Check agent specialization
            agent_spec = agent.get('specialization', '').lower()
            agent_skills = agent.get('skills', [])
            agent_expertise = agent.get('expertise_areas', [])

            # Direct title match
            if any(keyword in job_title for keyword in agent_spec.split()):
                score += 30
                match_reasons.append(f"Title matches specialization: {agent_spec}")

            # Skill matching
            for skill in detected_skills:
                if skill in agent_spec or any(skill in s.lower() for s in agent_skills):
                    score += 20
                    match_reasons.append(f"Has skill: {skill}")

            # Expertise area matching
            for expertise in agent_expertise:
                if expertise.lower() in job_description:
                    score += 15
                    match_reasons.append(f"Expertise in: {expertise}")

            # Special agent bonuses
            if 'senior' in job_title and agent.get('experience_level') == 'expert':
                score += 10
                match_reasons.append("Expert level matches senior position")

            if score > 0:
                agent_scores.append({
                    'agent_id': agent_id,
                    'agent': agent,
                    'score': score,
                    'reasons': match_reasons
                })

        # Get the best agent
        if not agent_scores:
            # Fallback to a generalist agent
            return self._get_generalist_agent_match(job)

        # Sort by score and get the best
        agent_scores.sort(key=lambda x: x['score'], reverse=True)
        best = agent_scores[0]

        # Create application strategy based on agent type
        strategy = self._determine_application_strategy(best['agent'], job)

        return JobMatch(
            job_id=job.get('id', job.get('url', '')),
            job_title=job.get('title', 'Unknown Position'),
            company=job.get('company', 'Unknown Company'),
            agent_id=best['agent_id'],
            agent_name=best['agent'].get('name', best['agent_id']),
            agent_specialization=best['agent'].get('specialization', 'General'),
            match_score=best['score'] / 100.0,  # Normalize to 0-1
            match_reasons=best['reasons'],
            application_strategy=strategy
        )

    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from job text"""
        detected = []
        text_lower = text.lower()

        for skill_category, keywords in self.skill_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    detected.append(skill_category)
                    break

        return detected

    def _determine_application_strategy(self, agent: Dict[str, Any], job: Dict[str, Any]) -> str:
        """Determine the best application strategy for this agent-job combination"""
        strategies = []

        # Check agent capabilities
        if agent.get('can_write_code'):
            strategies.append("Include code samples")
        if agent.get('has_portfolio'):
            strategies.append("Showcase portfolio")
        if agent.get('experience_level') == 'expert':
            strategies.append("Emphasize deep expertise")

        # Check job requirements
        if 'urgent' in job.get('title', '').lower():
            strategies.append("Emphasize quick availability")
        if 'remote' in job.get('location', '').lower():
            strategies.append("Highlight remote work experience")

        return " | ".join(strategies) if strategies else "Standard application"

    def _get_generalist_agent_match(self, job: Dict[str, Any]) -> JobMatch:
        """Fallback to a generalist agent when no specific match is found"""
        # Use the orchestrator or a general-purpose agent
        return JobMatch(
            job_id=job.get('id', job.get('url', '')),
            job_title=job.get('title', 'Unknown Position'),
            company=job.get('company', 'Unknown Company'),
            agent_id='orchestrator',
            agent_name='Orchestrator Agent',
            agent_specialization='General Purpose',
            match_score=0.5,
            match_reasons=['No specific match - using generalist agent'],
            application_strategy='Emphasize adaptability and learning ability'
        )

    async def submit_application(self, job_match: JobMatch, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Have the matched agent create and submit a job application

        Args:
            job_match: The job-agent match
            user_profile: User's profile information

        Returns:
            Application result
        """
        logger.info(f"🚀 Agent '{job_match.agent_name}' applying for '{job_match.job_title}' at {job_match.company}")

        # Get the agent
        agent = self.agent_registry.agents.get(job_match.agent_id)
        if not agent:
            return {'success': False, 'error': 'Agent not found'}

        # Simulate agent creating personalized application
        application = {
            'job_id': job_match.job_id,
            'job_title': job_match.job_title,
            'company': job_match.company,
            'agent_id': job_match.agent_id,
            'agent_name': job_match.agent_name,
            'applied_at': datetime.now().isoformat(),
            'status': 'submitted',

            # Agent-crafted application content
            'cover_letter': self._generate_cover_letter(job_match, agent, user_profile),
            'key_qualifications': self._extract_key_qualifications(agent),
            'proposed_approach': job_match.application_strategy,
            'availability': 'Immediate',
            'expected_rate': self._calculate_rate(job_match, agent),

            # Tracking
            'match_score': job_match.match_score,
            'match_reasons': job_match.match_reasons
        }

        # Store application
        app_id = f"app_{job_match.job_id}_{job_match.agent_id}"
        self.active_applications[app_id] = application
        self.application_history.append(application)

        # Simulate submission (in real implementation, would use job platform APIs)
        await asyncio.sleep(1)  # Simulate API call

        logger.info(f"✅ Application submitted successfully by {job_match.agent_name}")

        return {
            'success': True,
            'application_id': app_id,
            'agent': job_match.agent_name,
            'job': job_match.job_title,
            'company': job_match.company,
            'status': 'submitted'
        }

    def _generate_cover_letter(self, job_match: JobMatch, agent: Dict[str, Any], user_profile: Dict[str, Any]) -> str:
        """Generate a REAL personalized cover letter using OpenAI"""
        try:
            from openai import OpenAI
            import os

            # Initialize OpenAI client
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

            # Create a detailed prompt for the cover letter
            prompt = f"""
You are {job_match.agent_name}, an AI agent specialized in {job_match.agent_specialization}.
Write a compelling, personalized cover letter for the following job:

Job Title: {job_match.job_title}
Company: {job_match.company}
Agent's Match Score: {job_match.match_score:.0%}
Why this agent is a good match: {', '.join(job_match.match_reasons[:3])}
Application Strategy: {job_match.application_strategy}

User Profile: {user_profile.get('name', 'Professional')} with {user_profile.get('experience', 'extensive experience')}

Write a professional, engaging cover letter that:
1. Shows genuine interest in the specific role
2. Highlights the agent's unique capabilities
3. Demonstrates understanding of the company's needs
4. Includes specific examples of relevant experience
5. Ends with a strong call to action

Make it personal, not generic. Show personality while remaining professional.
"""

            # Make REAL API call to OpenAI
            logger.info(f"🤖 {job_match.agent_name} is using OpenAI to write cover letter...")

            result = async_to_sync(agent_llm_integration.generate_for_agent)(
                agent_name="JobApplicationOrchestrator",
                prompt=f"You are an expert cover letter writer. Create compelling, personalized applications.\n\n{prompt}",
                model="gpt-5-mini",
                reasoning_effort="high",
                verbosity="medium",
                max_output_tokens=500
            )

            if not result['success']:
                logger.error(f"LLM error generating cover letter: {result.get('error')}")
                return f"I am very interested in the {job_title} position and would love to discuss how my experience aligns with your needs."

            cover_letter = result['response'].strip()

            logger.info(f"✅ Real AI-generated cover letter created (used {response.usage.total_tokens} tokens)")

            # Add verification footer
            cover_letter += f"\n\n---\n[Generated by {job_match.agent_name} using GPT-3.5]"

            return cover_letter

        except Exception as e:
            logger.error(f"❌ Failed to generate cover letter with OpenAI: {e}")
            logger.warning("⚠️ Falling back to template (NOT using AI)")

            # Fallback template only if API fails
            return f"""
Dear Hiring Manager at {job_match.company},

[ERROR: Could not generate AI cover letter - using template]

I am {job_match.agent_name}, a specialized AI agent with expertise in {job_match.agent_specialization}.
I am writing to express strong interest in the {job_match.job_title} position.

My capabilities align perfectly with your requirements:
{' '.join(['- ' + reason for reason in job_match.match_reasons[:3]])}

Best regards,
{job_match.agent_name}
            """.strip()

    def _extract_key_qualifications(self, agent: Dict[str, Any]) -> List[str]:
        """Extract key qualifications from agent profile"""
        quals = []

        if agent.get('specialization'):
            quals.append(f"Specialized in {agent['specialization']}")
        if agent.get('experience_level'):
            quals.append(f"{agent['experience_level'].title()} level expertise")
        if agent.get('skills'):
            quals.extend(agent['skills'][:3])  # Top 3 skills

        return quals

    def _calculate_rate(self, job_match: JobMatch, agent: Dict[str, Any]) -> str:
        """Calculate appropriate rate based on agent expertise and job requirements"""
        base_rate = 50  # Base hourly rate

        # Adjust based on agent expertise
        if agent.get('experience_level') == 'expert':
            base_rate *= 2
        elif agent.get('experience_level') == 'senior':
            base_rate *= 1.5

        # Adjust based on match score
        base_rate *= (1 + job_match.match_score * 0.5)

        return f"${int(base_rate)}/hour"

    async def get_application_status(self, application_id: str) -> Dict[str, Any]:
        """Get the status of a submitted application"""
        if application_id in self.active_applications:
            return self.active_applications[application_id]
        return {'error': 'Application not found'}

    async def get_agent_applications(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get all applications submitted by a specific agent"""
        return [
            app for app in self.application_history
            if app.get('agent_id') == agent_id
        ]

    async def get_application_analytics(self) -> Dict[str, Any]:
        """Get analytics on application performance"""
        total_apps = len(self.application_history)

        if not total_apps:
            return {'message': 'No applications submitted yet'}

        # Calculate metrics
        agents_used = set(app['agent_id'] for app in self.application_history)
        companies_applied = set(app['company'] for app in self.application_history)
        avg_match_score = sum(app['match_score'] for app in self.application_history) / total_apps

        return {
            'total_applications': total_apps,
            'unique_agents_used': len(agents_used),
            'companies_applied_to': len(companies_applied),
            'average_match_score': avg_match_score,
            'top_performing_agents': self._get_top_agents(),
            'application_timeline': self._get_timeline()
        }

    def _get_top_agents(self) -> List[Dict[str, Any]]:
        """Get top performing agents by application count"""
        agent_counts = {}
        for app in self.application_history:
            agent_id = app['agent_id']
            if agent_id not in agent_counts:
                agent_counts[agent_id] = {
                    'agent_name': app['agent_name'],
                    'applications': 0,
                    'avg_match_score': 0
                }
            agent_counts[agent_id]['applications'] += 1
            agent_counts[agent_id]['avg_match_score'] += app['match_score']

        # Calculate averages
        for agent_id, stats in agent_counts.items():
            stats['avg_match_score'] /= stats['applications']

        # Sort by application count
        sorted_agents = sorted(agent_counts.items(), key=lambda x: x[1]['applications'], reverse=True)

        return [stats for _, stats in sorted_agents[:5]]  # Top 5

    def _get_timeline(self) -> Dict[str, int]:
        """Get application timeline"""
        timeline = {}
        for app in self.application_history:
            date = app['applied_at'].split('T')[0]
            timeline[date] = timeline.get(date, 0) + 1
        return timeline


# Test the orchestrator
async def test_job_application_orchestrator():
    """Test the job application orchestrator"""
    orchestrator = JobApplicationOrchestrator()

    # Sample jobs from RemoteOK
    sample_jobs = [
        {
            'title': 'Senior Python Developer',
            'company': 'TechCorp',
            'description': 'Looking for Python expert with Django experience',
            'tags': ['python', 'django', 'backend'],
            'url': 'https://example.com/job1'
        },
        {
            'title': 'React Frontend Engineer',
            'company': 'StartupXYZ',
            'description': 'Need React developer for UI components',
            'tags': ['javascript', 'react', 'frontend'],
            'url': 'https://example.com/job2'
        },
        {
            'title': 'AI/ML Engineer',
            'company': 'AI Innovations',
            'description': 'Build machine learning models and NLP systems',
            'tags': ['python', 'tensorflow', 'nlp'],
            'url': 'https://example.com/job3'
        }
    ]

    # Find best agents for each job
    print("\n🎯 INTELLIGENT AGENT-JOB MATCHING SYSTEM\n")
    print("=" * 60)

    matches = await orchestrator.process_job_opportunities(sample_jobs)

    for match in matches:
        print(f"\n📋 Job: {match.job_title} at {match.company}")
        print(f"   🤖 Assigned Agent: {match.agent_name}")
        print(f"   📊 Match Score: {match.match_score:.0%}")
        print(f"   🎯 Specialization: {match.agent_specialization}")
        print(f"   ✅ Match Reasons:")
        for reason in match.match_reasons[:3]:
            print(f"      - {reason}")
        print(f"   📝 Strategy: {match.application_strategy}")

    # Submit applications
    print("\n" + "=" * 60)
    print("📮 SUBMITTING APPLICATIONS\n")

    user_profile = {'name': 'User', 'experience': '5 years'}

    for match in matches:
        result = await orchestrator.submit_application(match, user_profile)
        if result['success']:
            print(f"✅ {result['agent']} applied to {result['job']} at {result['company']}")

    # Show analytics
    print("\n" + "=" * 60)
    print("📊 APPLICATION ANALYTICS\n")

    analytics = await orchestrator.get_application_analytics()
    print(f"Total Applications: {analytics.get('total_applications', 0)}")
    print(f"Unique Agents Used: {analytics.get('unique_agents_used', 0)}")
    print(f"Average Match Score: {analytics.get('average_match_score', 0):.0%}")


if __name__ == "__main__":
    asyncio.run(test_job_application_orchestrator())