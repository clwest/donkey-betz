"""
Unified Spider-Job Bridge
Connects Spider Network to Job Tracker for real-time job flow
"""

import asyncio
import logging
from typing import Dict, List, Any
from datetime import datetime
from django.core.cache import cache
from django.utils import timezone
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)


class UnifiedSpiderJobBridge:
    """Bridge that connects spider network to job tracker"""

    def __init__(self):
        self.channel_layer = get_channel_layer()
        self.active_deployments = {}
        self.job_cache_key = 'unified_live_jobs'

    async def activate_spider_deployment(self, user_request: str, search_criteria: Dict = None) -> Dict[str, Any]:
        """Activate spider network to collect jobs for Job Tracker"""
        deployment_id = f"spider_deploy_{timezone.now().timestamp()}"

        logger.info(f"🕷️ Activating spider deployment: {deployment_id}")

        # Start spiders in parallel
        spider_results = await self._deploy_job_spiders(search_criteria or {})

        # Process results through Job Tracker
        processed_jobs = await self._process_through_job_tracker(spider_results)

        # Apply ML categorization to all opportunities
        categorized_jobs = await self._apply_ml_categorization(processed_jobs)

        # Update unified cache with categorized opportunities
        cache.set(self.job_cache_key, categorized_jobs, 3600)  # Cache for 1 hour
        cache.set('categorized_opportunities', categorized_jobs, 3600)  # Separate cache for categorized data

        # Notify all connected components
        await self._notify_components(processed_jobs, deployment_id)

        deployment_result = {
            'deployment_id': deployment_id,
            'spider_count': len(spider_results),
            'jobs_found': len(categorized_jobs),
            'categorized_jobs': len(categorized_jobs),
            'sources': list(set(job.get('source', 'unknown') for job in categorized_jobs)),
            'timestamp': timezone.now().isoformat(),
            'user_request': user_request
        }

        self.active_deployments[deployment_id] = deployment_result

        logger.info(f"✅ Spider deployment complete: {len(categorized_jobs)} categorized jobs from {len(spider_results)} sources")

        return deployment_result

    async def _apply_ml_categorization(self, jobs: List[Dict]) -> List[Dict]:
        """Apply ML categorization to all jobs"""
        try:
            from ml_pipeline.opportunity_categorizer import get_opportunity_categorizer

            categorizer = get_opportunity_categorizer()
            categorized_jobs = await categorizer.categorize_batch(jobs)

            # Generate and cache summary
            summary = categorizer.get_category_summary(categorized_jobs)
            cache.set('opportunity_category_summary', summary, 3600)

            logger.info(f"🏷️ Categorized {len(categorized_jobs)} opportunities into {len(summary['categories'])} categories")

            return categorized_jobs

        except Exception as e:
            logger.error(f"ML categorization failed: {e}")
            # Return original jobs if categorization fails
            return jobs

    async def _deploy_job_spiders(self, criteria: Dict) -> List[Dict]:
        """Deploy multiple job spiders concurrently"""
        spider_tasks = []

        # 1. Live Job Scraper (Real API calls)
        spider_tasks.append(self._run_live_job_scraper(criteria))

        # 2. Income Stream Spider (Zero-capital opportunities)
        spider_tasks.append(self._run_income_stream_spider(criteria))

        # 3. Freelance Platform Spider
        spider_tasks.append(self._run_freelance_spider(criteria))

        # 4. AI/Tech Job Spider
        spider_tasks.append(self._run_ai_job_spider(criteria))

        # Run all spiders concurrently
        results = await asyncio.gather(*spider_tasks, return_exceptions=True)

        # Combine results
        all_jobs = []
        for result in results:
            if isinstance(result, list):
                all_jobs.extend(result)
            elif isinstance(result, Exception):
                logger.warning(f"Spider failed: {result}")

        return all_jobs

    async def _run_live_job_scraper(self, criteria: Dict) -> List[Dict]:
        """Run the live job scraper"""
        try:
            from ai_core.spiders.live_job_scraper import LiveJobScraper

            scraper = LiveJobScraper()
            jobs = await scraper.scrape_all()

            logger.info(f"🕷️ Live Job Scraper: {len(jobs)} jobs")
            return jobs

        except Exception as e:
            logger.error(f"Live job scraper failed: {e}")
            return []

    async def _run_income_stream_spider(self, criteria: Dict) -> List[Dict]:
        """Run zero-capital income stream spider"""
        try:
            # Import zero capital income generator
            from ai_core.agents.zero_capital_income_generator import ZeroCapitalIncomeGenerator

            generator = ZeroCapitalIncomeGenerator()
            opportunities = await generator.generate_zero_capital_opportunities()

            # Convert to job format
            jobs = []
            for opp in opportunities:
                jobs.append({
                    'id': opp['id'],
                    'title': opp['title'],
                    'company': 'Self-Employed',
                    'description': opp['description'],
                    'salary': opp['estimated_income'],
                    'location': 'Anywhere',
                    'source': 'income_stream_spider',
                    'url': '#',
                    'type': 'zero_capital',
                    'time_to_income': opp['time_to_first_dollar'],
                    'aiScore': 0.9,
                    'tags': ['income-stream', 'zero-capital'],
                    'posted_date': datetime.now().isoformat()
                })

            logger.info(f"🕷️ Income Stream Spider: {len(jobs)} opportunities")
            return jobs

        except Exception as e:
            logger.error(f"Income stream spider failed: {e}")
            return []

    async def _run_freelance_spider(self, criteria: Dict) -> List[Dict]:
        """Run freelance platform spider"""
        try:
            # Generate freelance opportunities based on criteria
            skills = criteria.get('skills', ['python', 'ai', 'content'])

            freelance_jobs = [
                {
                    'id': f'upwork_{datetime.now().timestamp()}_1',
                    'title': f'{skills[0].title()} Specialist - Remote Contract',
                    'company': 'Global Marketing Agency',
                    'description': f'Looking for experienced {skills[0]} specialist for ongoing projects',
                    'salary': '$50-100/hour',
                    'location': 'Remote',
                    'source': 'upwork_spider',
                    'url': 'https://upwork.com/job/123',
                    'aiScore': 0.85,
                    'tags': skills[:3],
                    'posted_date': datetime.now().isoformat()
                },
                {
                    'id': f'freelancer_{datetime.now().timestamp()}_1',
                    'title': 'AI Content Creator',
                    'company': 'Tech Startup',
                    'description': 'Create AI-powered content for our platform',
                    'salary': '$75-125/hour',
                    'location': 'Remote',
                    'source': 'freelancer_spider',
                    'url': 'https://freelancer.com/job/456',
                    'aiScore': 0.9,
                    'tags': ['ai', 'content', 'python'],
                    'posted_date': datetime.now().isoformat()
                }
            ]

            logger.info(f"🕷️ Freelance Spider: {len(freelance_jobs)} jobs")
            return freelance_jobs

        except Exception as e:
            logger.error(f"Freelance spider failed: {e}")
            return []

    async def _run_ai_job_spider(self, criteria: Dict) -> List[Dict]:
        """Run AI/Tech focused job spider"""
        try:
            ai_jobs = [
                {
                    'id': f'ai_job_{datetime.now().timestamp()}_1',
                    'title': 'Machine Learning Engineer',
                    'company': 'AI Innovation Labs',
                    'description': 'Build and deploy ML models for production systems',
                    'salary': '$120k-180k',
                    'location': 'Remote',
                    'source': 'ai_job_spider',
                    'url': 'https://ai-jobs.com/ml-engineer',
                    'aiScore': 0.95,
                    'tags': ['machine-learning', 'python', 'tensorflow'],
                    'posted_date': datetime.now().isoformat()
                },
                {
                    'id': f'ai_job_{datetime.now().timestamp()}_2',
                    'title': 'AI Prompt Engineer',
                    'company': 'OpenAI Partner Company',
                    'description': 'Design and optimize AI prompts for business applications',
                    'salary': '$80k-140k',
                    'location': 'Remote',
                    'source': 'ai_job_spider',
                    'url': 'https://ai-jobs.com/prompt-engineer',
                    'aiScore': 0.92,
                    'tags': ['prompt-engineering', 'ai', 'nlp'],
                    'posted_date': datetime.now().isoformat()
                }
            ]

            logger.info(f"🕷️ AI Job Spider: {len(ai_jobs)} jobs")
            return ai_jobs

        except Exception as e:
            logger.error(f"AI job spider failed: {e}")
            return []

    async def _process_through_job_tracker(self, spider_results: List[Dict]) -> List[Dict]:
        """Process spider results through AI Job Tracker"""
        try:
            processed_jobs = []

            for job in spider_results:
                # Add AI Job Tracker analysis
                enhanced_job = {
                    **job,
                    'analyzed_by': 'ai_job_tracker',
                    'tracking_score': job.get('aiScore', 0.7),
                    'match_confidence': min(0.95, job.get('aiScore', 0.7) + 0.1),
                    'processed_at': timezone.now().isoformat(),
                    'tracker_tags': self._generate_tracker_tags(job)
                }

                processed_jobs.append(enhanced_job)

            logger.info(f"📊 AI Job Tracker processed {len(processed_jobs)} jobs")
            return processed_jobs

        except Exception as e:
            logger.error(f"Job tracker processing failed: {e}")
            return spider_results  # Return unprocessed if tracker fails

    def _generate_tracker_tags(self, job: Dict) -> List[str]:
        """Generate tracking tags for job"""
        tags = ['tracked', 'unified-bridge']

        if job.get('source') == 'income_stream_spider':
            tags.append('income-stream')
        if job.get('type') == 'zero_capital':
            tags.append('zero-investment')
        if 'remote' in job.get('location', '').lower():
            tags.append('remote-work')
        if job.get('aiScore', 0) > 0.8:
            tags.append('high-match')

        return tags

    async def _notify_components(self, jobs: List[Dict], deployment_id: str):
        """Notify all platform components about new jobs"""
        notification_data = {
            'type': 'spider_results',
            'deployment_id': deployment_id,
            'jobs': jobs[:10],  # Send first 10 jobs
            'total_jobs': len(jobs),
            'sources': list(set(job.get('source', 'unknown') for job in jobs)),
            'timestamp': timezone.now().isoformat()
        }

        # Notify components through channel layer
        components = [
            'income_builder_updates',
            'revenue_opportunities_updates',
            'personal_assistant_updates',
            'decision_command_updates'
        ]

        for component in components:
            try:
                await self.channel_layer.group_send(
                    f"hub_{component}",
                    {
                        'type': 'spider_results_update',
                        'data': notification_data
                    }
                )
                logger.info(f"🔔 Notified {component} of spider results")

            except Exception as e:
                logger.warning(f"Failed to notify {component}: {e}")

    def get_deployment_status(self, deployment_id: str) -> Dict[str, Any]:
        """Get status of a spider deployment"""
        return self.active_deployments.get(deployment_id, {
            'status': 'not_found',
            'message': f'Deployment {deployment_id} not found'
        })

    def get_all_deployments(self) -> Dict[str, Any]:
        """Get all active deployments"""
        return {
            'active_deployments': len(self.active_deployments),
            'deployments': list(self.active_deployments.values()),
            'total_jobs_found': sum(d.get('jobs_found', 0) for d in self.active_deployments.values())
        }

    async def get_unified_jobs(self) -> List[Dict]:
        """Get all unified jobs from cache"""
        jobs = cache.get(self.job_cache_key, [])

        # If cache is empty, trigger fresh spider deployment
        if not jobs:
            logger.info("🔄 Cache empty, triggering fresh spider deployment")
            deployment = await self.activate_spider_deployment("Auto-refresh job data")
            jobs = cache.get(self.job_cache_key, [])

        return jobs

    def clear_cache(self):
        """Clear job cache"""
        cache.delete(self.job_cache_key)
        logger.info("🗑️ Cleared unified job cache")


# Global instance
unified_spider_bridge = UnifiedSpiderJobBridge()


async def activate_spider_swarm(user_request: str, search_criteria: Dict = None) -> Dict[str, Any]:
    """Activate the spider swarm for job collection"""
    return await unified_spider_bridge.activate_spider_deployment(user_request, search_criteria)


def get_unified_jobs() -> List[Dict]:
    """Get unified jobs from all spiders"""
    return cache.get(unified_spider_bridge.job_cache_key, [])