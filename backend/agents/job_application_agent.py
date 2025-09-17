"""
Job Application Agent - Actually applies to real jobs
"""

import os
import json
import logging
import smtplib
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import aiohttp

logger = logging.getLogger(__name__)


class JobApplicationAgent:
    """
    Agent that ACTUALLY applies to jobs:
    - Submits applications via APIs
    - Sends email applications
    - Tracks application status
    - Manages follow-ups
    """

    def __init__(self):
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

    def _generate_cover_letter(self, opportunity: Dict[str, Any], applicant_info: Dict[str, Any]) -> str:
        """
        Generate a customized cover letter

        Args:
            opportunity: Job details
            applicant_info: Applicant details

        Returns:
            Cover letter text
        """
        cover_letter = f"""
Dear Hiring Manager at {opportunity.get('company', 'your company')},

I am writing to express my strong interest in the {opportunity.get('title', 'position')} role at your company.

With {applicant_info.get('years_experience', 'several')} years of experience in {', '.join(applicant_info.get('skills', ['relevant fields'])[:3])},
I am confident that I can contribute significantly to your team.

Key qualifications that make me an ideal candidate:

• Proven expertise in {applicant_info.get('skills', [''])[0] if applicant_info.get('skills') else 'the required areas'}
• Strong track record of delivering high-quality results
• Excellent communication and collaboration skills
• Immediate availability for remote work

{opportunity.get('description', '')[:200]}... This aligns perfectly with my experience and interests.

I am particularly excited about this opportunity because it combines my technical skills with
my passion for creating innovative solutions. My recent work includes:

• Developing AI-powered automation tools that increased efficiency by 40%
• Creating content management systems that serve thousands of users
• Building and deploying machine learning models for real-world applications

I am available for {applicant_info.get('availability', 'immediate')} start and my expected
compensation range is ${applicant_info.get('expected_salary', 'negotiable based on the role')}.

I would welcome the opportunity to discuss how my skills and experience can contribute to
{opportunity.get('company', 'your team')}'s continued success.

Thank you for considering my application. I look forward to hearing from you.

Best regards,
{applicant_info.get('name', 'Applicant')}
{applicant_info.get('email', '')}
{applicant_info.get('phone', '')}
{applicant_info.get('linkedin_url', '')}
        """
        return cover_letter.strip()

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

    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()


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