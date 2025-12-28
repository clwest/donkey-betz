"""
Job Application Agent - Actually applies to real jobs with user context
"""

import os
import json
import logging
import smtplib
import asyncio
from datetime import datetime
from typing import Dict, Any, List
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import aiohttp
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from .ai_enforced_base import AIEnforcedApplicationAgent
from .spider_data_mixin import SpiderDataMixin, IntelligenceData

logger = logging.getLogger(__name__)


class JobApplicationAgent(AIEnforcedApplicationAgent, SpiderDataMixin):
    """
    Agent that ACTUALLY applies to jobs with user context:
    - Submits applications via APIs
    - Sends email applications
    - Tracks application status
    - Manages follow-ups
    - Uses personalized user context for applications

    Enhanced with real-time spider intelligence for:
    - Job opportunity detection
    - Application timing optimization
    - Market trend analysis
    - Salary negotiation insights
    """

    def __init__(self, user=None):
        # Initialize both parent classes
        super().__init__(agent_name="JobApplicationAgent", user=user)
        SpiderDataMixin.__init__(self)

        # Setup spider data receiver for job intelligence
        self.setup_spider_data_receiver(
            agent_id='job_application_agent',
            agent_type='job_application',
            quality_threshold=0.85,
            custom_keywords=['job', 'hiring', 'remote', 'developer', 'contract', 'freelance', 'opportunity']
        )

        # Add intelligence callback
        self.add_intelligence_callback(self._on_job_intelligence_received)

        self.applications_sent = []
        self.email_config = {
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'email': os.getenv('APPLICATION_EMAIL'),
            'password': os.getenv('APPLICATION_EMAIL_PASSWORD')
        }
        self.session = None

    async def initialize(self):
        """Initialize HTTP session for API submissions"""
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def apply_to_job(self, opportunity: Dict[str, Any], applicant_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply to a specific job opportunity

        Args:
            opportunity: Job opportunity details
            applicant_info: Applicant's information (name, email, resume, etc.)

        Returns:
            Application result
        """
        await self.initialize()

        application_result = {
            'opportunity_id': opportunity.get('id', 'unknown'),
            'title': opportunity.get('title'),
            'company': opportunity.get('company'),
            'applied_at': datetime.now().isoformat(),
            'status': 'pending',
            'method': None
        }

        try:
            # Check if opportunity has API endpoint for applications
            if opportunity.get('api_apply_url'):
                result = await self._apply_via_api(opportunity, applicant_info)
                application_result.update(result)

            # Check if email application is possible
            elif opportunity.get('email_apply'):
                result = await self._apply_via_email(opportunity, applicant_info)
                application_result.update(result)

            # For platforms requiring web form submission
            elif opportunity.get('application_url'):
                result = await self._prepare_manual_application(opportunity, applicant_info)
                application_result.update(result)

            self.applications_sent.append(application_result)
            self._save_application_record(application_result)

            logger.info(f"✅ Applied to: {application_result['title']} at {application_result['company']}")

        except Exception as e:
            logger.error(f"❌ Failed to apply to {opportunity.get('title')}: {e}")
            application_result['status'] = 'failed'
            application_result['error'] = str(e)

        return application_result

    async def _apply_via_api(self, opportunity: Dict[str, Any], applicant_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit application via API

        Args:
            opportunity: Job details
            applicant_info: Applicant details

        Returns:
            API submission result
        """
        api_url = opportunity.get('api_apply_url')

        # Prepare application payload
        application_data = {
            'job_id': opportunity.get('id'),
            'applicant_name': applicant_info.get('name'),
            'applicant_email': applicant_info.get('email'),
            'cover_letter': self._generate_cover_letter(opportunity, applicant_info),
            'resume_url': applicant_info.get('resume_url'),
            'portfolio_url': applicant_info.get('portfolio_url'),
            'linkedin_url': applicant_info.get('linkedin_url'),
            'skills': applicant_info.get('skills', []),
            'years_experience': applicant_info.get('years_experience', 0),
            'availability': applicant_info.get('availability', 'immediate'),
            'expected_salary': applicant_info.get('expected_salary')
        }

        try:
            async with self.session.post(
                api_url,
                json=application_data,
                headers={'Content-Type': 'application/json'}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        'method': 'api',
                        'status': 'submitted',
                        'submission_id': result.get('application_id'),
                        'message': 'Application submitted successfully via API'
                    }
                else:
                    return {
                        'method': 'api',
                        'status': 'failed',
                        'error': f'API returned status {response.status}'
                    }

        except Exception as e:
            logger.error(f"API submission error: {e}")
            return {
                'method': 'api',
                'status': 'failed',
                'error': str(e)
            }

    async def _apply_via_email(self, opportunity: Dict[str, Any], applicant_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit application via email

        Args:
            opportunity: Job details
            applicant_info: Applicant details

        Returns:
            Email submission result
        """
        if not self.email_config['email'] or not self.email_config['password']:
            return {
                'method': 'email',
                'status': 'failed',
                'error': 'Email credentials not configured'
            }

        try:
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.email_config['email']
            msg['To'] = opportunity.get('email_apply', 'jobs@company.com')
            msg['Subject'] = f"Application for {opportunity.get('title')} - {applicant_info.get('name')}"

            # Generate and attach cover letter
            cover_letter = self._generate_cover_letter(opportunity, applicant_info)
            msg.attach(MIMEText(cover_letter, 'plain'))

            # Attach resume if available
            if applicant_info.get('resume_path'):
                self._attach_file(msg, applicant_info['resume_path'], 'resume.pdf')

            # Send email
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['email'], self.email_config['password'])
                server.send_message(msg)

            return {
                'method': 'email',
                'status': 'submitted',
                'email_sent_to': msg['To'],
                'message': 'Application sent via email'
            }

        except Exception as e:
            logger.error(f"Email submission error: {e}")
            return {
                'method': 'email',
                'status': 'failed',
                'error': str(e)
            }

    async def _prepare_manual_application(self, opportunity: Dict[str, Any], applicant_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare application for manual submission

        Args:
            opportunity: Job details
            applicant_info: Applicant details

        Returns:
            Preparation result with instructions
        """
        # Generate all application materials
        cover_letter = self._generate_cover_letter(opportunity, applicant_info)

        # Save application materials
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        app_folder = f"/tmp/applications/{timestamp}_{opportunity.get('company', 'unknown')}"
        os.makedirs(app_folder, exist_ok=True)

        # Save cover letter
        with open(f"{app_folder}/cover_letter.txt", 'w') as f:
            f.write(cover_letter)

        # Create application instructions
        instructions = f"""
        APPLICATION READY FOR MANUAL SUBMISSION

        Job: {opportunity.get('title')}
        Company: {opportunity.get('company')}
        URL: {opportunity.get('application_url')}

        Materials saved to: {app_folder}

        Steps to complete:
        1. Open the application URL
        2. Fill in the application form
        3. Copy the cover letter from cover_letter.txt
        4. Upload resume from your files
        5. Submit the application
        6. Update status in tracking system
        """

        with open(f"{app_folder}/instructions.txt", 'w') as f:
            f.write(instructions)

        return {
            'method': 'manual',
            'status': 'prepared',
            'application_folder': app_folder,
            'application_url': opportunity.get('application_url'),
            'message': 'Application prepared for manual submission',
            'instructions': instructions
        }

    def _generate_cover_letter(self, opportunity: Dict[str, Any], applicant_info: Dict[str, Any] = None) -> str:
        """
        Generate a REAL customized cover letter using AI with user context

        Args:
            opportunity: Job details
            applicant_info: Applicant details (optional, will use user context if available)

        Returns:
            Cover letter text
        """
        # Use user context if available, otherwise fall back to provided applicant_info
        if self.user_context:
            # Use the enhanced cover letter generation from the base class
            return self.generate_cover_letter(opportunity, applicant_info)
        else:
            # Fallback to the old method if no user context
            return self._generate_fallback_cover_letter(opportunity, applicant_info)

    def _generate_fallback_cover_letter(self, opportunity: Dict[str, Any], applicant_info: Dict[str, Any]) -> str:
        """Fallback cover letter generation without user context"""
        # Build context about the job and applicant
        context = f"""
Job Information:
- Title: {opportunity.get('title', 'Position')}
- Company: {opportunity.get('company', 'Company')}
- Description: {opportunity.get('description', 'No description')[:500]}
- Salary Range: {opportunity.get('salary', 'Not specified')}
- Location: {opportunity.get('location', 'Remote')}

Applicant Information:
- Name: {applicant_info.get('name', 'Professional')}
- Email: {applicant_info.get('email', '')}
- Years of Experience: {applicant_info.get('years_experience', '5+')}
- Key Skills: {', '.join(applicant_info.get('skills', ['Python', 'AI/ML', 'Full Stack'])[:5])}
- Availability: {applicant_info.get('availability', 'Immediate')}
- Expected Salary: ${applicant_info.get('expected_salary', 'Competitive')}
        """

        prompt = """
Generate a compelling, personalized cover letter for this job opportunity.

Requirements:
1. Address it to the hiring manager at the company
2. Show genuine enthusiasm for the specific role and company
3. Highlight relevant skills and experience that match the job
4. Include specific examples of achievements
5. Be unique and authentic - not generic
6. Professional but conversational tone
7. Around 300-400 words
8. End with a clear call to action

Make it sound human, engaging, and tailored specifically to this opportunity.
Do NOT use generic phrases or templates. Each cover letter should be unique.
        """

        try:
            # Use the enforced AI generation method
            return self.generate_ai_text(
                prompt=prompt,
                context=context,
                task_type="cover_letter",
                max_tokens=800,
                temperature=0.8,
                personalize=False  # Don't double-personalize
            )

        except Exception as e:
            logger.error(f"❌ Exception generating cover letter: {e}")
            # Return minimal fallback
            return f"""Dear Hiring Manager,

I am interested in the {opportunity.get('title', 'position')} role at {opportunity.get('company', 'your company')}.

My background in {', '.join(applicant_info.get('skills', ['technology'])[:2]) if applicant_info else 'technology'} makes me a strong candidate for this position.

I look forward to discussing this opportunity with you.

Best regards,
{applicant_info.get('name', 'Applicant') if applicant_info else 'Applicant'}"""

    def _attach_file(self, msg: MIMEMultipart, file_path: str, filename: str):
        """Attach a file to email message"""
        try:
            with open(file_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={filename}')
                msg.attach(part)
        except Exception as e:
            logger.error(f"Failed to attach file: {e}")

    def _save_application_record(self, application: Dict[str, Any]):
        """Save application record for tracking"""
        applications_file = '/tmp/applications_tracker.json'

        try:
            # Load existing applications
            if os.path.exists(applications_file):
                with open(applications_file, 'r') as f:
                    applications = json.load(f)
            else:
                applications = []

            # Add new application
            applications.append(application)

            # Save updated list
            with open(applications_file, 'w') as f:
                json.dump(applications, f, indent=2)

            logger.info(f"💾 Application record saved: {application['title']}")

        except Exception as e:
            logger.error(f"Failed to save application record: {e}")

    async def batch_apply(self, opportunities: List[Dict[str, Any]], applicant_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Apply to multiple opportunities

        Args:
            opportunities: List of job opportunities
            applicant_info: Applicant information

        Returns:
            List of application results
        """
        results = []

        for opportunity in opportunities:
            # Add delay to avoid rate limiting
            await asyncio.sleep(2)

            result = await self.apply_to_job(opportunity, applicant_info)
            results.append(result)

            logger.info(f"📄 Applied to {len(results)}/{len(opportunities)} jobs")

        return results

    async def execute(self, task_type: str = "apply", **kwargs) -> Dict[str, Any]:
        """
        Execute agent task (required by AIEnforcedAgent interface)

        Args:
            task_type: Type of task to execute
            **kwargs: Task parameters

        Returns:
            Task execution result
        """
        try:
            if task_type == "apply":
                opportunity = kwargs.get('opportunity', {})
                applicant_info = kwargs.get('applicant_info', {})
                return await self.apply_to_job(opportunity, applicant_info)

            elif task_type == "batch_apply":
                opportunities = kwargs.get('opportunities', [])
                applicant_info = kwargs.get('applicant_info', {})
                return await self.batch_apply(opportunities, applicant_info)

            elif task_type == "analyze_fit":
                opportunity = kwargs.get('opportunity', {})
                if self.user_context:
                    return self.analyze_job_fit(opportunity)
                else:
                    return {'error': 'User context required for job fit analysis'}

            elif task_type == "generate_cover_letter":
                opportunity = kwargs.get('opportunity', {})
                applicant_info = kwargs.get('applicant_info', {})
                cover_letter = self._generate_cover_letter(opportunity, applicant_info)
                return {
                    'success': True,
                    'cover_letter': cover_letter,
                    'agent': self.agent_name,
                    'stats': self.get_ai_usage_stats()
                }

            else:
                return {
                    'success': False,
                    'error': f'Unknown task type: {task_type}',
                    'available_tasks': ['apply', 'batch_apply', 'analyze_fit', 'generate_cover_letter']
                }

        except Exception as e:
            logger.error(f"Error executing {task_type}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'agent': self.agent_name
            }

    async def process_spider_intelligence(self, data: IntelligenceData) -> Dict[str, Any]:
        """Process spider intelligence for job application optimization"""
        try:
            content = data.content
            content_text = str(content).lower()

            # Analyze job intelligence
            job_insights = {
                'agent_id': 'job_application_agent',
                'data_type': data.data_type,
                'spider_id': data.spider_id,
                'quality_score': data.quality_score,
                'job_analysis': {
                    'platform_detected': None,
                    'job_opportunities': [],
                    'skill_requirements': [],
                    'salary_insights': {},
                    'urgency_indicators': []
                },
                'recommended_actions': [],
                'application_priority': 'normal',
                'processed_at': datetime.now().isoformat()
            }

            # Detect platform
            if 'toptal' in content_text:
                job_insights['job_analysis']['platform_detected'] = 'Toptal'
            elif 'guru' in content_text:
                job_insights['job_analysis']['platform_detected'] = 'Guru'
            elif 'peopleperhour' in content_text:
                job_insights['job_analysis']['platform_detected'] = 'PeoplePerHour'
            elif 'flexjobs' in content_text:
                job_insights['job_analysis']['platform_detected'] = 'FlexJobs'
            elif 'remoteok' in content_text:
                job_insights['job_analysis']['platform_detected'] = 'RemoteOK'

            # Analyze job opportunities
            job_keywords = ['hiring', 'job opening', 'position available', 'now hiring', 'apply now']
            if any(keyword in content_text for keyword in job_keywords):
                job_insights['job_analysis']['job_opportunities'].append({
                    'type': 'direct_opportunity',
                    'confidence': data.quality_score,
                    'source': data.spider_id
                })
                job_insights['recommended_actions'].append('Review and apply to new job opportunities')

            # Analyze skill requirements
            tech_skills = ['python', 'javascript', 'react', 'node.js', 'aws', 'docker', 'kubernetes']
            detected_skills = [skill for skill in tech_skills if skill in content_text]
            if detected_skills:
                job_insights['job_analysis']['skill_requirements'] = detected_skills
                job_insights['recommended_actions'].append('Highlight relevant skills in applications')

            # Analyze salary insights
            if any(term in content_text for term in ['salary', '$', 'hourly', 'rate', 'compensation']):
                job_insights['job_analysis']['salary_insights'] = {
                    'has_salary_data': True,
                    'market_analysis_needed': True
                }
                job_insights['recommended_actions'].append('Research market rates for salary negotiations')

            # Check urgency indicators
            urgent_keywords = ['urgent', 'immediate', 'asap', 'rush', 'deadline']
            if any(keyword in content_text for keyword in urgent_keywords):
                job_insights['job_analysis']['urgency_indicators'].append('urgent_hiring')
                job_insights['application_priority'] = 'high'
                job_insights['recommended_actions'].append('Prioritize immediate application')

            # Remote work opportunities
            if 'remote' in content_text or 'work from home' in content_text:
                job_insights['job_analysis']['job_opportunities'].append({
                    'type': 'remote_opportunity',
                    'confidence': data.quality_score,
                    'source': data.spider_id
                })
                job_insights['recommended_actions'].append('Apply for remote opportunities')

            logger.info(f"📊 Processed job intelligence: {len(job_insights['recommended_actions'])} actions identified")

            return job_insights

        except Exception as e:
            logger.error(f"Error processing job intelligence: {e}")
            return {'error': str(e), 'agent_id': 'job_application_agent'}

    async def _on_job_intelligence_received(self, data: IntelligenceData, result: Dict[str, Any]):
        """Callback when job intelligence is received"""
        try:
            # Store intelligence for application optimization
            if not hasattr(self, 'job_intelligence'):
                self.job_intelligence = []

            self.job_intelligence.append({
                'data': data,
                'result': result,
                'received_at': datetime.now()
            })

            # Keep only last 50 intelligence items
            if len(self.job_intelligence) > 50:
                self.job_intelligence = self.job_intelligence[-50:]

            # Take action on high-priority opportunities
            if result.get('application_priority') == 'high':
                logger.info(f"🚨 High-priority job intelligence received from {data.spider_id}")

                # Auto-execute recommended actions for high-priority items
                actions = result.get('recommended_actions', [])
                if actions:
                    logger.info(f"🎯 Auto-executing {len(actions)} high-priority job actions")
                    await self._execute_job_intelligence_actions(actions, result)

        except Exception as e:
            logger.error(f"Error in job intelligence callback: {e}")

    async def _execute_job_intelligence_actions(self, actions: List[str], intelligence_result: Dict[str, Any]):
        """Execute recommended actions from job intelligence analysis"""
        try:
            platform = intelligence_result.get('job_analysis', {}).get('platform_detected')

            for action in actions:
                if 'apply' in action.lower() and 'opportunity' in action.lower():
                    logger.info(f"🔧 Preparing application strategy for {platform or 'detected opportunities'}")

                elif 'skills' in action.lower():
                    skills = intelligence_result.get('job_analysis', {}).get('skill_requirements', [])
                    logger.info(f"🔧 Optimizing skill highlighting: {', '.join(skills)}")

                elif 'salary' in action.lower():
                    logger.info("🔧 Researching market rates for salary optimization")

                elif 'immediate' in action.lower() or 'prioritize' in action.lower():
                    logger.info("🔧 Prioritizing urgent application processing")

        except Exception as e:
            logger.error(f"Error executing job intelligence actions: {e}")

    def get_job_intelligence_summary(self) -> Dict[str, Any]:
        """Get summary of received job intelligence"""
        if not hasattr(self, 'job_intelligence') or not self.job_intelligence:
            return {
                'total_intelligence_items': 0,
                'summary': 'No job intelligence received yet'
            }

        # Analyze collected intelligence
        platform_opportunities = {}
        skill_demands = {}
        total_actions = 0
        high_priority_count = 0

        for item in self.job_intelligence:
            result = item['result']

            # Count platform opportunities
            platform = result.get('job_analysis', {}).get('platform_detected')
            if platform:
                platform_opportunities[platform] = platform_opportunities.get(platform, 0) + 1

            # Count skill requirements
            skills = result.get('job_analysis', {}).get('skill_requirements', [])
            for skill in skills:
                skill_demands[skill] = skill_demands.get(skill, 0) + 1

            # Count actions
            total_actions += len(result.get('recommended_actions', []))

            # Count high priority items
            if result.get('application_priority') == 'high':
                high_priority_count += 1

        return {
            'total_intelligence_items': len(self.job_intelligence),
            'platform_opportunities': platform_opportunities,
            'skill_demands': skill_demands,
            'total_recommended_actions': total_actions,
            'high_priority_items': high_priority_count,
            'spider_data_metrics': self.get_spider_data_metrics(),
            'last_intelligence_received': self.job_intelligence[-1]['received_at'].isoformat() if self.job_intelligence else None
        }

    async def close(self):
        """Close HTTP session and spider data receiver"""
        if self.session:
            await self.session.close()

        # Stop spider data receiver
        await self.stop_spider_data_receiver()


# Test the application agent
async def test_application_agent():
    """Test the job application agent"""
    agent = JobApplicationAgent()

    # Sample applicant info
    applicant = {
        'name': 'John Doe',
        'email': 'john@example.com',
        'skills': ['Python', 'AI', 'Web Development'],
        'years_experience': 5,
        'availability': 'immediate',
        'expected_salary': '80000-100000',
        'resume_url': 'https://example.com/resume.pdf',
        'portfolio_url': 'https://github.com/johndoe',
        'linkedin_url': 'https://linkedin.com/in/johndoe'
    }

    # Sample opportunity
    opportunity = {
        'id': 'job123',
        'title': 'Senior Python Developer',
        'company': 'TechCorp',
        'description': 'Looking for experienced Python developer...',
        'application_url': 'https://techcorp.com/apply',
        'email_apply': 'jobs@techcorp.com'
    }

    # Apply to job
    result = await agent.apply_to_job(opportunity, applicant)

    print(f"\n📮 Application Result:")
    print(f"Status: {result['status']}")
    print(f"Method: {result.get('method')}")
    print(f"Message: {result.get('message')}")

    await agent.close()


if __name__ == "__main__":
    asyncio.run(test_application_agent())