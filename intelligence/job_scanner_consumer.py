"""
WebSocket consumer for Job Scanner functionality
"""
import json
import logging
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class JobScannerConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for Job Scanner with automated scanning capabilities"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scan_task = None
        self.scan_interval = 300  # Default 5 minutes
        self.auto_scan_enabled = False
        self.selected_jobs = []

    async def connect(self):
        """Handle WebSocket connection"""
        self.room_name = 'job_scanner'
        self.room_group_name = f'scanner_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"Job Scanner WebSocket connected: {self.channel_name}")

        # Send initial connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'status': 'connected',
            'message': 'Connected to Job Scanner',
            'auto_scan_enabled': self.auto_scan_enabled,
            'scan_interval': self.scan_interval
        }))

        # Send initial scan status
        await self.send_scan_status()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Cancel auto-scan if running
        if self.scan_task:
            self.scan_task.cancel()

        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"Job Scanner WebSocket disconnected: {self.channel_name}")

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'scan_jobs':
                # Manual scan trigger
                criteria = data.get('criteria', {})
                await self.scan_for_jobs(criteria)

            elif message_type == 'enable_auto_scan':
                # Enable automatic scanning
                interval = data.get('interval', 300)  # Default 5 minutes
                await self.enable_auto_scan(interval)

            elif message_type == 'disable_auto_scan':
                # Disable automatic scanning
                await self.disable_auto_scan()

            elif message_type == 'select_jobs':
                # User selected jobs for application
                job_ids = data.get('job_ids', [])
                await self.select_jobs_for_application(job_ids)

            elif message_type == 'apply_to_jobs':
                # Apply to selected jobs with agents
                job_ids = data.get('job_ids', [])
                await self.apply_to_jobs(job_ids)

            elif message_type == 'get_scan_history':
                # Get recent scan history
                await self.send_scan_history()

            elif message_type == 'get_application_status':
                # Get status of job applications
                await self.send_application_status()

            elif message_type == 'update_criteria':
                # Update scan criteria
                criteria = data.get('criteria', {})
                await self.update_scan_criteria(criteria)

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {text_data}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def scan_for_jobs(self, criteria: Dict) -> List[Dict]:
        """Execute job scanning with spiders"""
        try:
            # Update scan status
            await self.send(text_data=json.dumps({
                'type': 'scan_status',
                'status': 'scanning',
                'message': 'Deploying spider network for job discovery...'
            }))

            # Import and use the spider job bridge
            from intelligence.unified_spider_job_bridge import UnifiedSpiderJobBridge
            from backend.agents.intelligent_job_matcher import IntelligentJobMatcher

            bridge = UnifiedSpiderJobBridge()
            matcher = None
            try:
                matcher = IntelligentJobMatcher()
            except Exception as e:
                logger.warning(f"Intelligent matcher not available: {e}")

            # Default search criteria if none provided
            if not criteria:
                criteria = {
                    'keywords': ['python', 'AI', 'machine learning', 'remote', 'developer'],
                    'locations': ['remote', 'worldwide'],
                    'job_types': ['full-time', 'contract', 'freelance'],
                    'min_budget': 1000,
                    'experience_level': ['mid', 'senior']
                }

            # Deploy spider network
            deployment = await bridge.activate_spider_deployment(
                user_request="Find high-value job opportunities",
                search_criteria=criteria
            )

            # Get the collected jobs
            from django.core.cache import cache
            jobs = cache.get('unified_live_jobs', [])

            # Match agents to jobs if matcher available
            matched_jobs = []
            if matcher and jobs:
                for job in jobs[:20]:  # Process top 20 jobs
                    try:
                        match = await matcher.match_job_with_learning(job)
                        if match:
                            job['agent_match'] = match
                            matched_jobs.append(job)
                    except Exception as e:
                        logger.error(f"Matching failed for job: {e}")
                        # Add without agent match
                        matched_jobs.append(job)
            else:
                # Simple matching fallback
                matched_jobs = self._simple_match(jobs[:20])

            # Format jobs for frontend
            formatted_jobs = []
            for job in matched_jobs:
                formatted_job = {
                    'id': job.get('id', f"job_{len(formatted_jobs)}"),
                    'title': job.get('title', 'Unknown Title'),
                    'company': job.get('company', 'N/A'),
                    'location': job.get('location', 'N/A'),
                    'salary': job.get('budget', job.get('salary', 'N/A')),
                    'description': job.get('description', '')[:300],
                    'source': job.get('source', 'Spider Network'),
                    'url': job.get('url', '#'),
                    'tags': job.get('tags', []),
                    'posted_date': job.get('posted_date', datetime.now().isoformat()),
                    'agent_match': job.get('agent_match', None),
                    'match_score': job.get('agent_match', {}).get('confidence', 0) if job.get('agent_match') else 0
                }
                formatted_jobs.append(formatted_job)

            # Store scan results
            cache.set(f'scan_results_{self.channel_name}', formatted_jobs, 3600)

            # Send results to frontend
            await self.send(text_data=json.dumps({
                'type': 'scan_results',
                'jobs': formatted_jobs,
                'total_found': len(jobs),
                'deployment_id': deployment.get('deployment_id'),
                'sources': deployment.get('sources', []),
                'scan_time': datetime.now().isoformat()
            }))

            # Update scan status
            await self.send(text_data=json.dumps({
                'type': 'scan_status',
                'status': 'complete',
                'message': f'Found {len(formatted_jobs)} matching opportunities',
                'job_count': len(formatted_jobs)
            }))

            return formatted_jobs

        except Exception as e:
            logger.error(f"Error scanning for jobs: {e}")
            await self.send(text_data=json.dumps({
                'type': 'scan_status',
                'status': 'error',
                'message': f'Scan failed: {str(e)}'
            }))
            return []

    def _simple_match(self, jobs: List[Dict]) -> List[Dict]:
        """Simple fallback matching when ML matcher unavailable"""
        agent_specialties = {
            'Python Developer': ['python', 'django', 'flask', 'backend'],
            'AI Specialist': ['AI', 'machine learning', 'ML', 'neural', 'deep learning'],
            'Frontend Developer': ['react', 'vue', 'javascript', 'frontend', 'UI'],
            'Data Scientist': ['data', 'analysis', 'statistics', 'pandas', 'numpy'],
            'Content Creator': ['content', 'writing', 'blog', 'article', 'copy'],
            'DevOps Engineer': ['devops', 'aws', 'docker', 'kubernetes', 'CI/CD']
        }

        matched_jobs = []
        for job in jobs:
            job_text = f"{job.get('title', '')} {job.get('description', '')}".lower()

            best_agent = None
            best_score = 0

            for agent_name, keywords in agent_specialties.items():
                score = sum(1 for kw in keywords if kw.lower() in job_text)
                if score > best_score:
                    best_score = score
                    best_agent = agent_name

            if best_agent:
                job['agent_match'] = {
                    'agent': {'name': best_agent},
                    'confidence': min(0.9, best_score * 0.2),
                    'match_score': best_score / 10
                }

            matched_jobs.append(job)

        return matched_jobs

    async def enable_auto_scan(self, interval: int):
        """Enable automatic job scanning at specified interval"""
        try:
            self.scan_interval = max(60, interval)  # Minimum 1 minute
            self.auto_scan_enabled = True

            # Cancel existing task if any
            if self.scan_task:
                self.scan_task.cancel()

            # Start auto-scan task
            self.scan_task = asyncio.create_task(self._auto_scan_loop())

            await self.send(text_data=json.dumps({
                'type': 'auto_scan_enabled',
                'interval': self.scan_interval,
                'next_scan': (datetime.now() + timedelta(seconds=self.scan_interval)).isoformat()
            }))

            logger.info(f"Auto-scan enabled with interval: {self.scan_interval} seconds")

        except Exception as e:
            logger.error(f"Error enabling auto-scan: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Failed to enable auto-scan: {str(e)}'
            }))

    async def disable_auto_scan(self):
        """Disable automatic job scanning"""
        try:
            self.auto_scan_enabled = False

            if self.scan_task:
                self.scan_task.cancel()
                self.scan_task = None

            await self.send(text_data=json.dumps({
                'type': 'auto_scan_disabled',
                'message': 'Automatic scanning disabled'
            }))

            logger.info("Auto-scan disabled")

        except Exception as e:
            logger.error(f"Error disabling auto-scan: {e}")

    async def _auto_scan_loop(self):
        """Background task for automatic scanning"""
        while self.auto_scan_enabled:
            try:
                # Get stored criteria or use defaults
                from django.core.cache import cache
                criteria = cache.get(f'scan_criteria_{self.channel_name}', {})

                # Perform scan
                await self.scan_for_jobs(criteria)

                # Wait for next scan
                await asyncio.sleep(self.scan_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in auto-scan loop: {e}")
                await asyncio.sleep(self.scan_interval)

    async def select_jobs_for_application(self, job_ids: List[str]):
        """Mark jobs as selected for application"""
        try:
            from django.core.cache import cache

            # Get scan results
            scan_results = cache.get(f'scan_results_{self.channel_name}', [])

            # Filter selected jobs
            selected = [job for job in scan_results if job['id'] in job_ids]
            self.selected_jobs = selected

            # Store selection
            cache.set(f'selected_jobs_{self.channel_name}', selected, 3600)

            await self.send(text_data=json.dumps({
                'type': 'jobs_selected',
                'selected_count': len(selected),
                'job_ids': job_ids,
                'message': f'{len(selected)} jobs selected for application'
            }))

        except Exception as e:
            logger.error(f"Error selecting jobs: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Failed to select jobs: {str(e)}'
            }))

    async def apply_to_jobs(self, job_ids: List[str]):
        """Apply to selected jobs using matched agents"""
        try:
            from django.core.cache import cache

            # Get selected jobs
            selected_jobs = cache.get(f'selected_jobs_{self.channel_name}', [])
            if not selected_jobs:
                selected_jobs = self.selected_jobs

            # Filter to requested job IDs
            jobs_to_apply = [job for job in selected_jobs if job['id'] in job_ids]

            # Start application process
            await self.send(text_data=json.dumps({
                'type': 'application_started',
                'job_count': len(jobs_to_apply),
                'message': f'Starting application to {len(jobs_to_apply)} jobs...'
            }))

            # Apply to each job
            application_results = []
            for job in jobs_to_apply:
                try:
                    # Simulate agent application (would be real in production)
                    agent_name = job.get('agent_match', {}).get('agent', {}).get('name', 'Default Agent')

                    result = {
                        'job_id': job['id'],
                        'job_title': job['title'],
                        'agent': agent_name,
                        'status': 'submitted',
                        'submitted_at': datetime.now().isoformat(),
                        'application_id': f"app_{job['id']}_{datetime.now().timestamp()}"
                    }

                    application_results.append(result)

                    # Send progress update
                    await self.send(text_data=json.dumps({
                        'type': 'application_progress',
                        'completed': len(application_results),
                        'total': len(jobs_to_apply),
                        'current_job': job['title']
                    }))

                    # Small delay to simulate processing
                    await asyncio.sleep(0.5)

                except Exception as e:
                    logger.error(f"Error applying to job {job['id']}: {e}")
                    result = {
                        'job_id': job['id'],
                        'job_title': job['title'],
                        'status': 'failed',
                        'error': str(e)
                    }
                    application_results.append(result)

            # Store application results
            cache.set(f'application_results_{self.channel_name}', application_results, 86400)

            # Send completion
            await self.send(text_data=json.dumps({
                'type': 'application_complete',
                'results': application_results,
                'success_count': len([r for r in application_results if r['status'] == 'submitted']),
                'failed_count': len([r for r in application_results if r['status'] == 'failed'])
            }))

        except Exception as e:
            logger.error(f"Error applying to jobs: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Failed to apply to jobs: {str(e)}'
            }))

    async def send_scan_status(self):
        """Send current scan status"""
        try:
            from django.core.cache import cache

            # Get last scan info
            scan_results = cache.get(f'scan_results_{self.channel_name}', [])

            await self.send(text_data=json.dumps({
                'type': 'scan_status_update',
                'auto_scan_enabled': self.auto_scan_enabled,
                'scan_interval': self.scan_interval,
                'last_scan_job_count': len(scan_results),
                'selected_jobs_count': len(self.selected_jobs)
            }))

        except Exception as e:
            logger.error(f"Error sending scan status: {e}")

    async def send_scan_history(self):
        """Send recent scan history"""
        try:
            # In production, this would fetch from database
            history = [
                {
                    'scan_id': 'scan_001',
                    'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
                    'jobs_found': 45,
                    'jobs_selected': 5,
                    'jobs_applied': 5
                },
                {
                    'scan_id': 'scan_002',
                    'timestamp': (datetime.now() - timedelta(hours=6)).isoformat(),
                    'jobs_found': 38,
                    'jobs_selected': 3,
                    'jobs_applied': 3
                }
            ]

            await self.send(text_data=json.dumps({
                'type': 'scan_history',
                'history': history
            }))

        except Exception as e:
            logger.error(f"Error sending scan history: {e}")

    async def send_application_status(self):
        """Send status of job applications"""
        try:
            from django.core.cache import cache

            # Get application results
            results = cache.get(f'application_results_{self.channel_name}', [])

            await self.send(text_data=json.dumps({
                'type': 'application_status',
                'applications': results,
                'total_applications': len(results),
                'pending': len([r for r in results if r.get('status') == 'submitted']),
                'accepted': 0,  # Would track real responses
                'rejected': 0
            }))

        except Exception as e:
            logger.error(f"Error sending application status: {e}")

    async def update_scan_criteria(self, criteria: Dict):
        """Update and store scan criteria"""
        try:
            from django.core.cache import cache

            # Store criteria
            cache.set(f'scan_criteria_{self.channel_name}', criteria, 86400)

            await self.send(text_data=json.dumps({
                'type': 'criteria_updated',
                'criteria': criteria,
                'message': 'Scan criteria updated successfully'
            }))

            # If auto-scan is enabled, trigger immediate scan with new criteria
            if self.auto_scan_enabled:
                await self.scan_for_jobs(criteria)

        except Exception as e:
            logger.error(f"Error updating criteria: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Failed to update criteria: {str(e)}'
            }))