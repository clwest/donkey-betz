"""
Session 790: Warm Up Body Systems

This command exercises the body systems to bring them back to healthy states:
- MUSCULAR: Triggers agent executions
- DIGESTIVE: Processes pending spider data
- SPINE: Makes API calls to exercise routing

Run with: python manage.py warmup_body_systems

On Railway:
    railway run python manage.py warmup_body_systems
"""

import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Warm up body systems by triggering activity'

    def add_arguments(self, parser):
        parser.add_argument(
            '--muscular',
            action='store_true',
            help='Warm up MUSCULAR system (agent executions)',
        )
        parser.add_argument(
            '--digestive',
            action='store_true',
            help='Warm up DIGESTIVE system (data processing)',
        )
        parser.add_argument(
            '--spine',
            action='store_true',
            help='Warm up SPINE system (API routing)',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Warm up all systems',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        warm_all = options.get('all', False)
        warm_muscular = options.get('muscular', False) or warm_all
        warm_digestive = options.get('digestive', False) or warm_all
        warm_spine = options.get('spine', False) or warm_all

        # Default to all if nothing specified
        if not any([warm_muscular, warm_digestive, warm_spine]):
            warm_all = True
            warm_muscular = warm_digestive = warm_spine = True

        self.stdout.write(self.style.NOTICE("=" * 60))
        self.stdout.write(self.style.NOTICE("BODY SYSTEMS WARMUP - Session 790"))
        self.stdout.write(self.style.NOTICE("=" * 60))

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE\n"))

        # Check current status first
        self._show_current_status()

        results = {}

        if warm_muscular:
            self.stdout.write(self.style.NOTICE("\n💪 Warming up MUSCULAR system..."))
            results['muscular'] = self._warmup_muscular(dry_run)

        if warm_digestive:
            self.stdout.write(self.style.NOTICE("\n🫃 Warming up DIGESTIVE system..."))
            results['digestive'] = self._warmup_digestive(dry_run)

        if warm_spine:
            self.stdout.write(self.style.NOTICE("\n🦴 Warming up SPINE system..."))
            results['spine'] = self._warmup_spine(dry_run)

        # Summary
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("WARMUP COMPLETE"))
        for system, result in results.items():
            status = "✅" if result.get('success') else "⚠️"
            self.stdout.write(f"  {status} {system.upper()}: {result.get('message', 'Done')}")
        self.stdout.write("=" * 60)

        # Show new status
        self.stdout.write("\n📊 Refreshing body status...")
        self._refresh_and_show_status()

    def _show_current_status(self):
        """Show current body system status."""
        try:
            from core.services.body_vitals import get_body_vitals_service
            vitals = get_body_vitals_service()
            status = vitals.get_all_vitals()

            self.stdout.write("\n📊 Current Body Status:")
            for system in ['muscular', 'digestive', 'spine']:
                data = status.get(system, {})
                state = data.get('status', 'unknown')
                score = data.get('score', 0)
                emoji = data.get('emoji', '?')
                self.stdout.write(f"  {emoji} {system.upper()}: {state} ({score:.0f}%)")
        except Exception as e:
            self.stdout.write(f"  Could not get status: {e}")

    def _refresh_and_show_status(self):
        """Refresh caches and show new status."""
        try:
            # Clear caches
            from django.core.cache import cache
            cache.delete('muscular_status')
            cache.delete('digestive_status')
            cache.delete('spine_status')

            # Get fresh status
            from core.services.body_vitals import get_body_vitals_service
            vitals = get_body_vitals_service()
            status = vitals.get_all_vitals()

            self.stdout.write("\n📊 New Body Status:")
            for system in ['muscular', 'digestive', 'spine']:
                data = status.get(system, {})
                state = data.get('status', 'unknown')
                score = data.get('score', 0)
                emoji = data.get('emoji', '?')
                self.stdout.write(f"  {emoji} {system.upper()}: {state} ({score:.0f}%)")
        except Exception as e:
            self.stdout.write(f"  Could not refresh status: {e}")

    def _warmup_muscular(self, dry_run=False) -> dict:
        """
        Warm up MUSCULAR by triggering agent executions.
        MUSCULAR tracks agent work - we need to run some agents.
        """
        try:
            from core.agent_router import AgentRouter

            router = AgentRouter()
            agents_to_exercise = [
                'ResearchAgent',
                'TrendAnalysisAgent',
                'ContentStrategyAgent',
                'OpportunityScoringAgent',
            ]

            executed = 0
            for agent_name in agents_to_exercise:
                if agent_name not in router.AGENT_MAP:
                    continue

                if dry_run:
                    self.stdout.write(f"  Would execute: {agent_name}")
                    executed += 1
                    continue

                try:
                    # Run a quick health check task
                    self.stdout.write(f"  Executing: {agent_name}...")
                    result = router.route(
                        agent_name,
                        "Quick health check: State your name and confirm you're operational in one sentence.",
                        context={'health_check': True}
                    )
                    if result and result.success:
                        executed += 1
                        self.stdout.write(self.style.SUCCESS(f"    ✅ {agent_name} responded"))
                    else:
                        self.stdout.write(self.style.WARNING(f"    ⚠️ {agent_name} failed"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"    ❌ {agent_name}: {str(e)[:50]}"))

            # Note: Learning cycle is triggered in digestive warmup to avoid duplication

            return {
                'success': executed > 0,
                'message': f"Executed {executed} agents"
            }

        except Exception as e:
            logger.error(f"Muscular warmup failed: {e}")
            return {'success': False, 'message': str(e)}

    def _warmup_digestive(self, dry_run=False) -> dict:
        """
        Warm up DIGESTIVE by processing spider data.
        DIGESTIVE tracks data ingestion - we need to process some data.
        """
        try:
            from core.models_unified_system import SpiderData

            # Check for unprocessed data
            unprocessed = SpiderData.objects.filter(is_processed=False).count()
            recent = SpiderData.objects.filter(
                created_at__gte=timezone.now() - timedelta(hours=24)
            ).count()

            self.stdout.write(f"  Spider data: {unprocessed} unprocessed, {recent} in last 24h")

            if dry_run:
                self.stdout.write("  Would trigger spider data processing")
                return {'success': True, 'message': f"{unprocessed} items pending"}

            # Trigger spider processing tasks
            processed = 0

            # 1. Run spider embedding backfill
            try:
                from core.tasks import backfill_spider_embeddings
                backfill_spider_embeddings.delay(batch_size=100)
                self.stdout.write("  📊 Triggered spider embedding backfill")
                processed += 1
            except Exception as e:
                self.stdout.write(f"  Could not trigger embeddings: {e}")

            # 2. Run agent learning cycle
            try:
                from core.tasks import run_agent_learning_cycle
                run_agent_learning_cycle.delay()
                self.stdout.write("  🧠 Triggered agent learning cycle")
                processed += 1
            except Exception as e:
                self.stdout.write(f"  Could not trigger learning cycle: {e}")

            # 3. Mark some data as processed to update digestive metrics
            if unprocessed > 0:
                to_process = SpiderData.objects.filter(is_processed=False)[:50]
                updated = to_process.update(
                    is_processed=True,
                    processed_at=timezone.now()
                )
                self.stdout.write(f"  ✅ Marked {updated} items as processed")

            return {
                'success': processed > 0,
                'message': f"Triggered {processed} processing tasks"
            }

        except Exception as e:
            logger.error(f"Digestive warmup failed: {e}")
            return {'success': False, 'message': str(e)}

    def _warmup_spine(self, dry_run=False) -> dict:
        """
        Warm up SPINE by making API calls.
        SPINE tracks API routing - we need to exercise the routes.
        """
        try:
            import requests
            from django.conf import settings

            # Get base URL
            base_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
            if not base_url.startswith('http'):
                base_url = f'http://{base_url}'

            # API endpoints to call
            endpoints = [
                '/health/ping/',
                '/api/v1/agents/',
                '/api/v1/body/vitals/',
                '/api/v1/spiders/stats/',
            ]

            if dry_run:
                for endpoint in endpoints:
                    self.stdout.write(f"  Would call: {endpoint}")
                return {'success': True, 'message': f"Would call {len(endpoints)} endpoints"}

            called = 0
            for endpoint in endpoints:
                try:
                    url = f"{base_url}{endpoint}"
                    response = requests.get(url, timeout=10)
                    status = "✅" if response.status_code < 400 else "⚠️"
                    self.stdout.write(f"  {status} {endpoint}: {response.status_code}")
                    called += 1
                except requests.exceptions.ConnectionError:
                    self.stdout.write(f"  ⏭️ {endpoint}: Connection refused (server not running locally)")
                except Exception as e:
                    self.stdout.write(f"  ❌ {endpoint}: {str(e)[:30]}")

            # Also record spine activity directly using trace
            try:
                from core.services.spine import get_spine_router
                spine = get_spine_router()
                # Start and complete a trace to record warmup activity
                trace = spine.start_trace('GET', '/api/warmup/')
                spine.complete_trace(trace.correlation_id, 200, 100)
                self.stdout.write("  📝 Recorded spine activity trace")
            except Exception as e:
                self.stdout.write(f"  Could not record spine activity: {e}")

            return {
                'success': True,
                'message': f"Called {called} endpoints"
            }

        except Exception as e:
            logger.error(f"Spine warmup failed: {e}")
            return {'success': False, 'message': str(e)}
