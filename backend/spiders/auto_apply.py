"""
Auto-Application System
Phase 5: Activate Money-Making Pipeline - Intelligent Application Engine

This module implements automated application generation and submission
for high-scoring opportunities identified by the opportunity scorer.
"""

import logging
import json
import asyncio
import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import aiohttp
import hashlib
from django.conf import settings
import re
from .opportunity_scorer import OpportunityScorer

logger = logging.getLogger(__name__)


class ApplicationStatus(Enum):
    """Application lifecycle states"""
    PENDING = "pending"
    GENERATED = "generated"
    SUBMITTED = "submitted"
    RESPONDED = "responded"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"


class ProposalTemplate(Enum):
    """Different proposal approaches for A/B testing"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    DETAILED = "detailed"
    BRIEF = "brief"
    CREATIVE = "creative"
    TECHNICAL = "technical"


@dataclass
class UserProfile:
    """User profile for personalized applications"""
    name: str
    email: str
    skills: List[str]
    experience_years: int
    portfolio_url: Optional[str] = None
    resume_text: str = ""
    hourly_rate: float = 50.0
    availability: str = "full-time"
    timezone: str = "UTC"
    languages: List[str] = field(default_factory=lambda: ["English"])
    certifications: List[str] = field(default_factory=list)
    preferred_industries: List[str] = field(default_factory=list)
    bio: str = ""


@dataclass
class ApplicationRecord:
    """Track individual applications"""
    id: str
    opportunity_id: str
    user_id: str
    score: float
    template_used: ProposalTemplate
    generated_at: datetime
    submitted_at: Optional[datetime] = None
    status: ApplicationStatus = ApplicationStatus.PENDING
    proposal_text: str = ""
    response_received: Optional[str] = None
    feedback: Optional[str] = None
    revenue_potential: float = 0.0
    time_investment: float = 0.0
    success_probability: float = 0.0
    metadata: Dict = field(default_factory=dict)


class ProposalGenerator:
    """Generate tailored proposals using different templates"""

    def __init__(self):
        self.templates = {
            ProposalTemplate.PROFESSIONAL: self._professional_template,
            ProposalTemplate.CASUAL: self._casual_template,
            ProposalTemplate.DETAILED: self._detailed_template,
            ProposalTemplate.BRIEF: self._brief_template,
            ProposalTemplate.CREATIVE: self._creative_template,
            ProposalTemplate.TECHNICAL: self._technical_template,
        }

        self.skill_phrases = {
            'python': ['Python development', 'Python programming', 'Django/Flask experience'],
            'javascript': ['JavaScript expertise', 'Node.js development', 'React/Vue.js skills'],
            'design': ['UI/UX design', 'Creative design solutions', 'Visual design expertise'],
            'marketing': ['Digital marketing', 'Marketing strategy', 'Growth hacking'],
            'writing': ['Content creation', 'Technical writing', 'Copywriting skills'],
            'data': ['Data analysis', 'Machine learning', 'Statistical analysis'],
            'mobile': ['Mobile app development', 'iOS/Android experience', 'Cross-platform development'],
            'blockchain': ['Blockchain development', 'Smart contracts', 'DeFi experience'],
        }

    async def generate_proposal(
        self,
        opportunity: Dict,
        user_profile: UserProfile,
        template: ProposalTemplate
    ) -> str:
        """Generate a tailored proposal for an opportunity"""

        try:
            # Get template function
            template_func = self.templates.get(template, self._professional_template)

            # Generate proposal using selected template
            proposal = await template_func(opportunity, user_profile)

            # Add personalization
            proposal = await self._personalize_proposal(proposal, opportunity, user_profile)

            return proposal

        except Exception as e:
            logger.error(f"❌ Error generating proposal: {e}")
            return await self._fallback_template(opportunity, user_profile)

    async def _professional_template(self, opportunity: Dict, user_profile: UserProfile) -> str:
        """Professional, formal proposal template"""

        title = opportunity.get('title', 'Project')
        company = opportunity.get('company', 'your company')
        budget = opportunity.get('budget', 'your budget')

        relevant_skills = self._extract_relevant_skills(opportunity, user_profile)

        proposal = f"""Dear {company} team,

I am writing to express my strong interest in the "{title}" opportunity. With {user_profile.experience_years} years of professional experience and expertise in {', '.join(relevant_skills[:3])}, I am confident I can deliver exceptional results for your project.

**Why I'm the right fit:**
• Proven experience in {relevant_skills[0] if relevant_skills else 'relevant technologies'}
• {user_profile.experience_years}+ years of professional development experience
• Strong track record of delivering projects on time and within budget
• Excellent communication and project management skills

**My approach:**
1. Thorough analysis of your requirements
2. Detailed project timeline and milestones
3. Regular progress updates and communication
4. Quality assurance and testing
5. Post-delivery support and documentation

I would be delighted to discuss how my skills and experience align with your needs. I'm available for a brief call at your convenience to explore this opportunity further.

Best regards,
{user_profile.name}
{user_profile.email}
{user_profile.portfolio_url or ''}"""

        return proposal

    async def _casual_template(self, opportunity: Dict, user_profile: UserProfile) -> str:
        """Casual, friendly proposal template"""

        title = opportunity.get('title', 'project')
        relevant_skills = self._extract_relevant_skills(opportunity, user_profile)

        proposal = f"""Hi there! 👋

I came across your {title} posting and it looks like a perfect match for my skills! I've been working with {', '.join(relevant_skills[:2])} for about {user_profile.experience_years} years and I love tackling projects like this.

Here's what I bring to the table:
• {user_profile.experience_years} years hands-on experience
• Strong background in {relevant_skills[0] if relevant_skills else 'development'}
• Always deliver on time (seriously, I'm a bit obsessed with deadlines 😄)
• Great communication - I'll keep you in the loop every step of the way

I'm really excited about the possibility of working together on this. Would love to hop on a quick call to chat about your vision and see how I can help make it happen!

Cheers,
{user_profile.name}
{user_profile.email}"""

        return proposal

    async def _detailed_template(self, opportunity: Dict, user_profile: UserProfile) -> str:
        """Comprehensive, detailed proposal template"""

        title = opportunity.get('title', 'Project')
        description = opportunity.get('description', '')[:200]
        relevant_skills = self._extract_relevant_skills(opportunity, user_profile)

        proposal = f"""Subject: Comprehensive Proposal for {title}

Dear Hiring Manager,

I have carefully reviewed your {title} requirements and am excited to present a detailed proposal outlining how I can contribute to your project's success.

**PROJECT UNDERSTANDING:**
Based on your description: "{description}...", I understand you need a solution that combines technical expertise with strategic thinking.

**RELEVANT EXPERIENCE:**
• {user_profile.experience_years}+ years in {relevant_skills[0] if relevant_skills else 'development'}
• Completed 50+ similar projects with 98% client satisfaction
• Expertise in: {', '.join(relevant_skills)}
• Industry experience: {', '.join(user_profile.preferred_industries[:2]) if user_profile.preferred_industries else 'Multiple industries'}

**DETAILED APPROACH:**

Phase 1: Analysis & Planning (Week 1)
- Requirements gathering and stakeholder interviews
- Technical architecture design
- Project roadmap and timeline creation
- Risk assessment and mitigation strategies

Phase 2: Development & Implementation (Weeks 2-4)
- Core functionality development
- Integration with existing systems
- Quality assurance and testing
- Performance optimization

Phase 3: Deployment & Support (Week 5)
- Production deployment
- User training and documentation
- Post-launch monitoring and support
- Performance metrics and reporting

**DELIVERABLES:**
✓ Fully functional solution meeting all requirements
✓ Comprehensive documentation
✓ Source code with comments
✓ Testing suite and quality reports
✓ 30-day post-launch support

**INVESTMENT:**
Based on project scope, I estimate ${user_profile.hourly_rate}/hour for approximately 120-150 hours of work.

**WHY CHOOSE ME:**
• Proven track record with measurable results
• Transparent communication and regular updates
• Agile methodology with flexible adaptation
• Long-term partnership approach

I would welcome the opportunity to discuss this proposal in detail and answer any questions you may have.

Best regards,
{user_profile.name}
Senior {relevant_skills[0] if relevant_skills else 'Developer'}
{user_profile.email}
{user_profile.portfolio_url or ''}"""

        return proposal

    async def _brief_template(self, opportunity: Dict, user_profile: UserProfile) -> str:
        """Short, concise proposal template"""

        title = opportunity.get('title', 'project')
        relevant_skills = self._extract_relevant_skills(opportunity, user_profile)

        proposal = f"""Hi,

Perfect timing on your {title} post! I specialize in exactly what you need.

Quick overview:
• {user_profile.experience_years} years experience in {relevant_skills[0] if relevant_skills else 'development'}
• Available to start immediately
• ${user_profile.hourly_rate}/hour
• 100% delivery rate on similar projects

Let's chat about making this happen quickly and efficiently.

{user_profile.name}
{user_profile.email}"""

        return proposal

    async def _creative_template(self, opportunity: Dict, user_profile: UserProfile) -> str:
        """Creative, engaging proposal template"""

        title = opportunity.get('title', 'project')
        relevant_skills = self._extract_relevant_skills(opportunity, user_profile)

        creative_openers = [
            "🚀 Ready to transform your vision into reality?",
            "💡 Your project just found its perfect match!",
            "⚡ Let's create something amazing together!",
            "🎯 Spotted your project - it's exactly my specialty!",
        ]

        opener = random.choice(creative_openers)

        proposal = f"""{opener}

Your {title} caught my eye because it's the perfect blend of challenge and creativity - exactly what gets me excited about development!

🔥 What makes me different:
• {user_profile.experience_years} years turning complex ideas into elegant solutions
• Obsessed with {relevant_skills[0] if relevant_skills else 'clean code'} and user experience
• I don't just code - I craft digital experiences
• Previous clients call me "the developer who actually listens" 😊

🎨 My process is part science, part art:
1. Deep dive into your vision
2. Sketch out innovative solutions
3. Build with precision and passion
4. Polish until it sparkles
5. Launch and celebrate! 🎉

Ready to turn your project into something extraordinary? I'm already brainstorming ideas!

Let's make magic happen,
{user_profile.name} ✨
{user_profile.email}"""

        return proposal

    async def _technical_template(self, opportunity: Dict, user_profile: UserProfile) -> str:
        """Technical, specification-focused proposal template"""

        title = opportunity.get('title', 'Project')
        relevant_skills = self._extract_relevant_skills(opportunity, user_profile)

        proposal = f"""Technical Proposal: {title}

**TECHNICAL QUALIFICATIONS:**
• Programming Languages: {', '.join(relevant_skills[:4])}
• Experience: {user_profile.experience_years} years in software development
• Architecture: Microservices, RESTful APIs, Database Design
• DevOps: CI/CD, Docker, Cloud Platforms (AWS/GCP/Azure)

**TECHNICAL APPROACH:**

1. **System Architecture**
   - Scalable, modular design patterns
   - Database optimization and indexing strategies
   - API design following RESTful principles
   - Security best practices implementation

2. **Development Stack**
   - Frontend: Modern frameworks (React/Vue.js/Angular)
   - Backend: {relevant_skills[0] if 'python' in str(relevant_skills).lower() else 'Node.js/Python/Java'}
   - Database: PostgreSQL/MongoDB based on requirements
   - Cache Layer: Redis for performance optimization

3. **Quality Assurance**
   - Test-Driven Development (TDD)
   - Unit testing coverage >90%
   - Integration testing suite
   - Performance testing and optimization

4. **Deployment & Monitoring**
   - Containerized deployment with Docker
   - Automated CI/CD pipeline
   - Application monitoring and logging
   - Error tracking and alerting

**PERFORMANCE METRICS:**
• Page load times: <2 seconds
• API response times: <100ms
• Uptime guarantee: 99.9%
• Code coverage: >90%

**TIMELINE:**
Estimated 6-8 weeks for full implementation including testing and deployment.

**RATE:** ${user_profile.hourly_rate}/hour

Looking forward to discussing technical specifications in detail.

{user_profile.name}
Senior Software Engineer
{user_profile.email}"""

        return proposal

    async def _fallback_template(self, opportunity: Dict, user_profile: UserProfile) -> str:
        """Simple fallback template if others fail"""

        title = opportunity.get('title', 'project')

        return f"""Hello,

I'm interested in your {title} opportunity. With {user_profile.experience_years} years of experience, I believe I can deliver exactly what you're looking for.

I'd be happy to discuss the project details and how I can contribute to its success.

Best regards,
{user_profile.name}
{user_profile.email}"""

    def _extract_relevant_skills(self, opportunity: Dict, user_profile: UserProfile) -> List[str]:
        """Extract skills relevant to the opportunity"""

        opp_text = f"{opportunity.get('title', '')} {opportunity.get('description', '')}".lower()
        relevant = []

        # Match user skills to opportunity keywords
        for skill in user_profile.skills:
            if skill.lower() in opp_text:
                relevant.append(skill)

        # Add skill phrases that match
        for skill_key, phrases in self.skill_phrases.items():
            if skill_key in opp_text:
                relevant.extend([p for p in phrases if p not in relevant])

        return relevant[:5]  # Return top 5 relevant skills

    async def _personalize_proposal(
        self,
        proposal: str,
        opportunity: Dict,
        user_profile: UserProfile
    ) -> str:
        """Add personalized touches to the proposal"""

        # Add portfolio link if available
        if user_profile.portfolio_url and 'portfolio' not in proposal.lower():
            proposal += f"\n\nPortfolio: {user_profile.portfolio_url}"

        # Add relevant certifications
        if user_profile.certifications:
            cert_text = f"\nCertifications: {', '.join(user_profile.certifications[:3])}"
            proposal += cert_text

        return proposal


class AutoApplicationSystem:
    """Main auto-application system orchestrator"""

    def __init__(self):
        self.opportunity_scorer = OpportunityScorer()
        self.proposal_generator = ProposalGenerator()

        # Application tracking
        self.applications: Dict[str, ApplicationRecord] = {}
        self.user_profiles: Dict[str, UserProfile] = {}

        # A/B testing configuration
        self.ab_test_groups = {
            'group_a': [ProposalTemplate.PROFESSIONAL, ProposalTemplate.DETAILED],
            'group_b': [ProposalTemplate.CASUAL, ProposalTemplate.BRIEF],
            'group_c': [ProposalTemplate.CREATIVE, ProposalTemplate.TECHNICAL],
        }

        # Statistics tracking
        self.stats = {
            'total_applications': 0,
            'submitted_applications': 0,
            'responses_received': 0,
            'accepted_applications': 0,
            'total_revenue': 0.0,
            'avg_response_time': 0.0,
            'success_rate': 0.0,
            'template_performance': {}
        }

        logger.info("🤖 Auto-Application System initialized")

    async def register_user(self, user_id: str, profile_data: Dict) -> bool:
        """Register a user profile for auto-applications"""

        try:
            profile = UserProfile(
                name=profile_data.get('name', 'User'),
                email=profile_data.get('email', ''),
                skills=profile_data.get('skills', []),
                experience_years=profile_data.get('experience_years', 1),
                portfolio_url=profile_data.get('portfolio_url'),
                resume_text=profile_data.get('resume_text', ''),
                hourly_rate=profile_data.get('hourly_rate', 50.0),
                availability=profile_data.get('availability', 'full-time'),
                timezone=profile_data.get('timezone', 'UTC'),
                languages=profile_data.get('languages', ['English']),
                certifications=profile_data.get('certifications', []),
                preferred_industries=profile_data.get('preferred_industries', []),
                bio=profile_data.get('bio', '')
            )

            self.user_profiles[user_id] = profile
            logger.info(f"✅ User profile registered: {user_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Error registering user profile: {e}")
            return False

    async def process_opportunities(
        self,
        opportunities: List[Dict],
        user_id: str,
        min_score: float = 7.0,
        max_applications: int = 10
    ) -> List[ApplicationRecord]:
        """Process opportunities and create applications for high-scoring ones"""

        if user_id not in self.user_profiles:
            logger.error(f"❌ User profile not found: {user_id}")
            return []

        user_profile = self.user_profiles[user_id]
        applications_created = []

        try:
            # Score all opportunities
            scored_opportunities = []
            for opp in opportunities:
                scored_opp = await self.opportunity_scorer.score_opportunity(opp, user_profile.__dict__)

                # Convert OpportunityScore to dict format
                score_data = {
                    'total_score': scored_opp.total_score,
                    'score_breakdown': scored_opp.scores,
                    'skill_match_details': {'skill_match': scored_opp.skill_match},
                    'revenue_estimate': scored_opp.estimated_revenue,
                    'time_investment': scored_opp.time_investment,
                    'success_probability': scored_opp.success_probability,
                    'recommendation': scored_opp.recommendation
                }

                scored_opportunities.append((opp, score_data))

            # Sort by score (descending)
            scored_opportunities.sort(key=lambda x: x[1]['total_score'], reverse=True)

            # Process top opportunities
            processed_count = 0
            for opportunity, score_data in scored_opportunities:

                if processed_count >= max_applications:
                    break

                if score_data['total_score'] >= min_score:

                    # Create application
                    application = await self._create_application(
                        opportunity,
                        user_id,
                        user_profile,
                        score_data
                    )

                    if application:
                        applications_created.append(application)
                        processed_count += 1

                        logger.info(f"🎯 Created application for '{opportunity.get('title')}' "
                                   f"(Score: {score_data['total_score']:.1f})")

            logger.info(f"📝 Created {len(applications_created)} applications for user {user_id}")
            return applications_created

        except Exception as e:
            logger.error(f"❌ Error processing opportunities: {e}")
            return []

    async def _create_application(
        self,
        opportunity: Dict,
        user_id: str,
        user_profile: UserProfile,
        score_data: Dict
    ) -> Optional[ApplicationRecord]:
        """Create an individual application record"""

        try:
            # Generate unique application ID
            app_id = self._generate_application_id(opportunity, user_id)

            # Select template for A/B testing
            template = await self._select_template(opportunity, user_profile)

            # Generate proposal
            proposal_text = await self.proposal_generator.generate_proposal(
                opportunity,
                user_profile,
                template
            )

            # Create application record
            application = ApplicationRecord(
                id=app_id,
                opportunity_id=opportunity.get('id', str(hash(str(opportunity)))),
                user_id=user_id,
                score=score_data['total_score'],
                template_used=template,
                generated_at=datetime.now(),
                proposal_text=proposal_text,
                revenue_potential=score_data.get('revenue_estimate', 0.0),
                time_investment=score_data.get('time_investment', 0.0),
                success_probability=score_data.get('success_probability', 0.0),
                metadata={
                    'opportunity_type': opportunity.get('type', 'unknown'),
                    'score_breakdown': score_data,
                    'keywords_matched': score_data.get('skill_match_details', {}),
                }
            )

            # Store application
            self.applications[app_id] = application
            self.stats['total_applications'] += 1

            return application

        except Exception as e:
            logger.error(f"❌ Error creating application: {e}")
            return None

    async def _select_template(self, opportunity: Dict, user_profile: UserProfile) -> ProposalTemplate:
        """Select proposal template for A/B testing"""

        # Hash user_id + opportunity to ensure consistent group assignment
        hash_input = f"{user_profile.email}_{opportunity.get('id', str(hash(str(opportunity))))}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)

        # Assign to A/B test group
        group_key = ['group_a', 'group_b', 'group_c'][hash_value % 3]
        template_options = self.ab_test_groups[group_key]

        # Select template from group
        template = template_options[hash_value % len(template_options)]

        return template

    def _generate_application_id(self, opportunity: Dict, user_id: str) -> str:
        """Generate unique application ID"""

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        opp_hash = hashlib.md5(str(opportunity).encode()).hexdigest()[:8]
        user_hash = hashlib.md5(user_id.encode()).hexdigest()[:4]

        return f"app_{timestamp}_{opp_hash}_{user_hash}"

    async def submit_applications(self, application_ids: List[str]) -> Dict[str, bool]:
        """Submit generated applications (simulation for now)"""

        results = {}

        for app_id in application_ids:
            if app_id not in self.applications:
                results[app_id] = False
                continue

            application = self.applications[app_id]

            try:
                # Simulate submission (replace with real API calls)
                success = await self._simulate_submission(application)

                if success:
                    application.status = ApplicationStatus.SUBMITTED
                    application.submitted_at = datetime.now()
                    self.stats['submitted_applications'] += 1
                    logger.info(f"✅ Submitted application: {app_id}")
                else:
                    logger.warning(f"⚠️ Failed to submit application: {app_id}")

                results[app_id] = success

            except Exception as e:
                logger.error(f"❌ Error submitting application {app_id}: {e}")
                results[app_id] = False

        return results

    async def _simulate_submission(self, application: ApplicationRecord) -> bool:
        """Simulate application submission (replace with real implementation)"""

        # Simulate network delay
        await asyncio.sleep(random.uniform(0.5, 2.0))

        # Simulate success/failure (90% success rate for simulation)
        return random.random() > 0.1

    async def track_responses(self) -> Dict[str, Any]:
        """Track and analyze application responses"""

        response_summary = {
            'total_responses': 0,
            'positive_responses': 0,
            'negative_responses': 0,
            'pending_responses': 0,
            'avg_response_time_hours': 0.0,
            'template_performance': {},
            'recent_activity': []
        }

        try:
            # Simulate checking for responses
            for app_id, application in self.applications.items():

                if application.status == ApplicationStatus.SUBMITTED:
                    # Simulate receiving responses (20% chance per check)
                    if random.random() < 0.2:
                        await self._simulate_response(application)

                # Count responses
                if application.status in [ApplicationStatus.RESPONDED, ApplicationStatus.ACCEPTED, ApplicationStatus.REJECTED]:
                    response_summary['total_responses'] += 1

                    if application.status in [ApplicationStatus.RESPONDED, ApplicationStatus.ACCEPTED]:
                        response_summary['positive_responses'] += 1
                    else:
                        response_summary['negative_responses'] += 1
                else:
                    response_summary['pending_responses'] += 1

            # Calculate template performance
            template_stats = {}
            for application in self.applications.values():
                template = application.template_used.value
                if template not in template_stats:
                    template_stats[template] = {'sent': 0, 'responses': 0, 'accepted': 0}

                template_stats[template]['sent'] += 1

                if application.status in [ApplicationStatus.RESPONDED, ApplicationStatus.ACCEPTED, ApplicationStatus.REJECTED]:
                    template_stats[template]['responses'] += 1

                if application.status == ApplicationStatus.ACCEPTED:
                    template_stats[template]['accepted'] += 1

            # Calculate performance metrics
            for template, stats in template_stats.items():
                if stats['sent'] > 0:
                    response_rate = (stats['responses'] / stats['sent']) * 100
                    acceptance_rate = (stats['accepted'] / stats['sent']) * 100

                    response_summary['template_performance'][template] = {
                        'response_rate': response_rate,
                        'acceptance_rate': acceptance_rate,
                        'total_sent': stats['sent']
                    }

            return response_summary

        except Exception as e:
            logger.error(f"❌ Error tracking responses: {e}")
            return response_summary

    async def _simulate_response(self, application: ApplicationRecord):
        """Simulate receiving a response to an application"""

        # Simulate different response types
        response_types = [
            (ApplicationStatus.ACCEPTED, "Great proposal! When can you start?"),
            (ApplicationStatus.RESPONDED, "Interesting approach. Let's discuss further."),
            (ApplicationStatus.REJECTED, "Thank you for your proposal, but we've chosen another candidate."),
        ]

        weights = [0.15, 0.35, 0.5]  # 15% accepted, 35% interested, 50% rejected
        status, response = random.choices(response_types, weights=weights)[0]

        application.status = status
        application.response_received = response

        # Update stats
        self.stats['responses_received'] += 1
        if status == ApplicationStatus.ACCEPTED:
            self.stats['accepted_applications'] += 1
            self.stats['total_revenue'] += application.revenue_potential

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""

        # Calculate success rate
        if self.stats['submitted_applications'] > 0:
            self.stats['success_rate'] = (self.stats['accepted_applications'] / self.stats['submitted_applications']) * 100

        return {
            'applications': {
                'total_created': self.stats['total_applications'],
                'total_submitted': self.stats['submitted_applications'],
                'responses_received': self.stats['responses_received'],
                'accepted': self.stats['accepted_applications'],
                'success_rate': self.stats['success_rate']
            },
            'revenue': {
                'total_potential': self.stats['total_revenue'],
                'avg_per_application': self.stats['total_revenue'] / max(self.stats['accepted_applications'], 1)
            },
            'active_users': len(self.user_profiles),
            'pending_applications': len([a for a in self.applications.values() if a.status == ApplicationStatus.PENDING]),
            'template_performance': self.stats.get('template_performance', {})
        }

    async def optimize_templates(self) -> Dict[str, Any]:
        """Analyze and optimize proposal templates based on performance"""

        optimization_report = {
            'best_performing_template': None,
            'worst_performing_template': None,
            'recommendations': [],
            'performance_analysis': {}
        }

        try:
            # Get current performance data
            response_data = await self.track_responses()
            template_performance = response_data.get('template_performance', {})

            if not template_performance:
                optimization_report['recommendations'].append("Not enough data for optimization yet")
                return optimization_report

            # Find best and worst performers
            best_template = max(template_performance.items(), key=lambda x: x[1]['acceptance_rate'])
            worst_template = min(template_performance.items(), key=lambda x: x[1]['acceptance_rate'])

            optimization_report['best_performing_template'] = {
                'template': best_template[0],
                'acceptance_rate': best_template[1]['acceptance_rate'],
                'response_rate': best_template[1]['response_rate']
            }

            optimization_report['worst_performing_template'] = {
                'template': worst_template[0],
                'acceptance_rate': worst_template[1]['acceptance_rate'],
                'response_rate': worst_template[1]['response_rate']
            }

            # Generate recommendations
            if best_template[1]['acceptance_rate'] > worst_template[1]['acceptance_rate'] * 2:
                optimization_report['recommendations'].append(
                    f"Consider using {best_template[0]} template more frequently - "
                    f"it has {best_template[1]['acceptance_rate']:.1f}% acceptance rate"
                )

            optimization_report['performance_analysis'] = template_performance

            return optimization_report

        except Exception as e:
            logger.error(f"❌ Error optimizing templates: {e}")
            optimization_report['recommendations'].append("Error occurred during optimization analysis")
            return optimization_report


# Singleton instance
auto_application_system = AutoApplicationSystem()


# Public API functions
async def register_user_profile(user_id: str, profile_data: Dict) -> bool:
    """Register a user profile for auto-applications"""
    return await auto_application_system.register_user(user_id, profile_data)


async def process_user_opportunities(
    opportunities: List[Dict],
    user_id: str,
    min_score: float = 7.0,
    max_applications: int = 10
) -> List[ApplicationRecord]:
    """Process opportunities and create applications"""
    return await auto_application_system.process_opportunities(
        opportunities, user_id, min_score, max_applications
    )


async def submit_user_applications(application_ids: List[str]) -> Dict[str, bool]:
    """Submit generated applications"""
    return await auto_application_system.submit_applications(application_ids)


async def get_application_responses() -> Dict[str, Any]:
    """Get application response tracking data"""
    return await auto_application_system.track_responses()


def get_auto_application_stats() -> Dict[str, Any]:
    """Get auto-application system statistics"""
    return auto_application_system.get_statistics()


async def optimize_proposal_templates() -> Dict[str, Any]:
    """Optimize proposal templates based on performance"""
    return await auto_application_system.optimize_templates()