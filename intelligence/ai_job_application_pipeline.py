"""
AI Job Application Pipeline
============================
Connects spiders → job matcher → resume generator → application system
"""

import asyncio
import redis
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from .ai_job_matcher import AIJobMatcher
from .ai_resume_generator import AIResumeGenerator

logger = logging.getLogger(__name__)


class AIJobApplicationPipeline:
    """
    Automated pipeline for processing job opportunities and generating applications
    """

    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.job_matcher = AIJobMatcher()
        self.resume_generator = AIResumeGenerator()
        self.pubsub = self.redis_client.pubsub()

        # Track processed jobs to avoid duplicates
        self.processed_jobs = set()

        # Output directory for applications
        self.output_dir = Path("income_builder_outputs")
        self.output_dir.mkdir(exist_ok=True)

        # User profile (would come from database in production)
        self.user_profile = {
            "name": "AI Professional",
            "email": "ai.pro@example.com",
            "phone": "+1 (555) 123-4567",
            "location": "Remote | Worldwide",
            "years_experience": 3
        }

    async def start(self):
        """Start monitoring for job opportunities"""

        logger.info("🚀 Starting AI Job Application Pipeline")

        # Subscribe to job-related channels from spiders
        channels = [
            'intelligence:freelance_finder',
            'intelligence:job_application_agent',
            'intelligence:gig_economy_expert',
            'intelligence:contract_negotiator',
            'intelligence:remote_work_specialist',
            'intelligence:general:freelance_opportunity',
            'intelligence:general:remote_tech_job'
        ]

        self.pubsub.subscribe(channels)
        logger.info(f"📡 Subscribed to {len(channels)} job channels")

        # Process incoming jobs
        message_count = 0

        for message in self.pubsub.listen():
            if message['type'] == 'message':
                message_count += 1

                try:
                    data = json.loads(message['data'])
                    logger.info(f"📨 Received job opportunity #{message_count} from {message['channel']}")

                    await self.process_job_opportunity(data)

                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    continue

    async def process_job_opportunity(self, spider_data: Dict[str, Any]):
        """Process a job opportunity from spider data"""

        # Extract job information from spider data
        job_data = self.extract_job_data(spider_data)

        # Check if already processed
        job_id = job_data.get('id', f"job_{datetime.now().timestamp()}")
        if job_id in self.processed_jobs:
            logger.debug(f"Skipping duplicate job: {job_id}")
            return

        self.processed_jobs.add(job_id)

        # Analyze with AI Job Matcher
        logger.info(f"🔍 Analyzing job: {job_data.get('title', 'Unknown')}")
        match = self.job_matcher.analyze_job(job_data)

        if not match:
            logger.info("❌ Job not suitable for AI completion")
            return

        if match.ai_score < 0.7:
            logger.info(f"⚠️ AI score too low: {match.ai_score:.2%}")
            return

        logger.info(f"✅ Suitable job found! AI Score: {match.ai_score:.2%}, Category: {match.category.value}")

        # Generate application materials
        logger.info("📝 Generating application materials...")

        resume = self.resume_generator.generate_resume(
            user_profile=self.user_profile,
            job_category=match.category,
            job_requirements=match.required_skills
        )

        proposal = self.job_matcher.generate_proposal_template(match)

        cover_letter = self.resume_generator.generate_cover_letter(
            resume=resume,
            job_title=match.title,
            company="the hiring team"
        )

        # Save application materials
        self.save_application(match, resume, proposal, cover_letter)

        # Log success
        logger.info(f"""
🎉 APPLICATION GENERATED SUCCESSFULLY!
   Job: {match.title}
   Category: {match.category.value}
   AI Score: {match.ai_score:.2%}
   Success Probability: {match.success_probability:.2%}
   Estimated Time: {match.estimated_completion_time} hours
   Budget: ${match.budget if match.budget else 'Not specified'}

   Materials saved to: income_builder_outputs/application_{job_id}_*
""")

    def extract_job_data(self, spider_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract job data from spider intelligence format"""

        content = spider_data.get('content', {})
        metadata = spider_data.get('metadata', {})

        # Try to extract job information from various possible formats
        job_data = {
            'id': content.get('id') or metadata.get('id') or spider_data.get('spider_id', 'unknown'),
            'title': content.get('title') or content.get('job_title') or 'Job Opportunity',
            'description': content.get('description') or content.get('job_description') or '',
            'skills': content.get('skills') or content.get('required_skills') or [],
            'budget': content.get('budget') or content.get('price') or content.get('rate'),
            'client_history': content.get('client_history') or {},
            'url': content.get('url') or spider_data.get('source_url', ''),
            'platform': spider_data.get('spider_id', '').split('_')[0] if spider_data.get('spider_id') else 'unknown'
        }

        # Add any additional fields from content
        for key, value in content.items():
            if key not in job_data:
                job_data[key] = value

        return job_data

    def save_application(self, match, resume, proposal, cover_letter):
        """Save all application materials to files"""

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        job_id = match.job_id.replace('/', '_').replace(' ', '_')[:50]  # Sanitize for filename

        # Save resume
        resume_path = self.output_dir / f"application_{job_id}_resume_{timestamp}.txt"
        with open(resume_path, 'w') as f:
            f.write(self.resume_generator.format_resume_text(resume))

        # Save proposal
        proposal_path = self.output_dir / f"application_{job_id}_proposal_{timestamp}.txt"
        with open(proposal_path, 'w') as f:
            f.write(proposal)

        # Save cover letter
        cover_path = self.output_dir / f"application_{job_id}_cover_{timestamp}.txt"
        with open(cover_path, 'w') as f:
            f.write(cover_letter)

        # Save job details and match analysis
        details_path = self.output_dir / f"application_{job_id}_details_{timestamp}.json"
        with open(details_path, 'w') as f:
            json.dump({
                'job_id': match.job_id,
                'title': match.title,
                'category': match.category.value,
                'ai_score': match.ai_score,
                'success_probability': match.success_probability,
                'estimated_hours': match.estimated_completion_time,
                'budget': match.budget,
                'ai_tools': match.ai_tools_applicable,
                'approach': match.recommended_approach,
                'timestamp': timestamp
            }, f, indent=2)

        logger.info(f"💾 Application saved: {details_path.name}")


async def run_pipeline():
    """Run the AI job application pipeline"""

    pipeline = AIJobApplicationPipeline()

    try:
        await pipeline.start()
    except KeyboardInterrupt:
        logger.info("🛑 Pipeline stopped by user")
    except Exception as e:
        logger.error(f"Pipeline error: {e}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("""
    🤖 AI JOB APPLICATION PIPELINE
    ==============================

    This pipeline will:
    1. Monitor spider channels for job opportunities
    2. Analyze jobs for AI suitability
    3. Generate resumes and proposals automatically
    4. Save applications to income_builder_outputs/

    Press Ctrl+C to stop

    Starting in 3 seconds...
    """)

    asyncio.run(asyncio.sleep(3))
    asyncio.run(run_pipeline())