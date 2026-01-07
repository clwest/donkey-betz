"""
Session 706: DIGESTIVE Check Management Command

CLI command for checking digestive system (data ingestion & processing) health.
The data processing layer of the AI body - transforms raw data into intelligence.

Usage:
    python manage.py digestion_check                    # Full digestion check
    python manage.py digestion_check --json             # JSON output
    python manage.py digestion_check --routes           # List all ingestion routes
    python manage.py digestion_check --bottlenecks      # Show current bottlenecks
    python manage.py digestion_check --metabolism       # Show throughput metrics
    python manage.py digestion_check --watch            # Continuous monitoring (60s)
    python manage.py digestion_check --history          # Show digestion pulse history
    python manage.py digestion_check --stage intake     # Check specific stage

Output includes:
    - Overall digestion status (healthy/sluggish/bloated/blocked/starving)
    - Digestion score (0-100%)
    - Stage-by-stage breakdown (intake, processing, enrichment, routing)
    - Metabolism rates (items/minute)
    - Bottleneck detection
"""

import json
import time
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone


class Command(BaseCommand):
    help = 'Check DIGESTIVE (data ingestion & processing) system health'

    def add_arguments(self, parser):
        parser.add_argument(
            '--json',
            action='store_true',
            help='Output results as JSON'
        )
        parser.add_argument(
            '--routes',
            action='store_true',
            help='List all ingestion routes'
        )
        parser.add_argument(
            '--bottlenecks',
            action='store_true',
            help='Show current bottlenecks'
        )
        parser.add_argument(
            '--metabolism',
            action='store_true',
            help='Show throughput metrics'
        )
        parser.add_argument(
            '--history',
            action='store_true',
            help='Show digestion pulse history'
        )
        parser.add_argument(
            '--stage',
            type=str,
            choices=['intake', 'processing', 'enrichment', 'routing'],
            help='Check specific stage only'
        )
        parser.add_argument(
            '--watch',
            action='store_true',
            help='Continuous monitoring mode (60s interval)'
        )
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Lookback period in hours for history (default: 24)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force fresh check (ignore cache)'
        )

    def handle(self, *args, **options):
        from core.services.digestive import get_digestive_system

        digestive = get_digestive_system()

        if options['routes']:
            self._show_routes(digestive, options['json'])
        elif options['bottlenecks']:
            self._show_bottlenecks(digestive, options['json'])
        elif options['metabolism']:
            self._show_metabolism(digestive, options['json'])
        elif options['history']:
            self._show_history(digestive, options['hours'], options['json'])
        elif options['stage']:
            self._show_stage(digestive, options['stage'], options['json'])
        elif options['watch']:
            self._watch_mode(digestive, options['json'])
        else:
            self._full_check(digestive, options['force'], options['json'])

    def _full_check(self, digestive, force: bool, as_json: bool):
        """Run full digestion check."""
        result = digestive.digest(force=force)

        if as_json:
            self.stdout.write(json.dumps(result, indent=2, default=str))
            return

        # Header
        self.stdout.write('')
        self.stdout.write('=' * 60)
        self.stdout.write('  DIGESTIVE SYSTEM - Data Ingestion & Processing')
        self.stdout.write('  The Data Processing Layer of the AI Body')
        self.stdout.write('=' * 60)

        # Overall status
        status = result['overall_status']
        score = result['digestion_score']
        emoji = self._get_status_emoji(status)
        status_text = f"{status.upper():<12}"
        status_style = self._get_status_style(status)

        self.stdout.write(f'  Overall Status: {status_style(status_text)} {emoji}')
        self.stdout.write(f'  Digestion Score: {score:.1f}%')
        self.stdout.write(f'  Is Digesting: {"Yes" if result.get("is_digesting", True) else "No"}')
        self.stdout.write(f'  Check Duration: {result.get("check_duration_ms", 0):.0f}ms')
        self.stdout.write('')

        # Stage breakdown
        stages = result.get('stages', {})

        # Intake stage
        intake = stages.get('intake', {})
        self.stdout.write('  INTAKE Stage (Spider Data):')
        self.stdout.write('  ' + '-' * 40)
        intake_status = intake.get('status', 'unknown')
        intake_style = self._get_status_style(intake_status)
        self.stdout.write(f'  Status:          {intake_style(intake_status.upper())}')
        self.stdout.write(f'  Items (24h):     {intake.get("items_24h", 0)}')
        self.stdout.write(f'  Spiders:         {intake.get("spiders_executed", 0)}')
        self.stdout.write(f'  Success Rate:    {intake.get("success_rate", 0):.1f}%')
        self.stdout.write('')

        # Processing stage
        processing = stages.get('processing', {})
        self.stdout.write('  PROCESSING Stage (Queue & Transform):')
        self.stdout.write('  ' + '-' * 40)
        proc_status = processing.get('status', 'unknown')
        proc_style = self._get_status_style(proc_status)
        self.stdout.write(f'  Status:          {proc_style(proc_status.upper())}')
        queue_depth = processing.get('queue_depth', 0)
        if queue_depth > 100:
            self.stdout.write(self.style.WARNING(f'  Queue Depth:     {queue_depth}'))
        else:
            self.stdout.write(f'  Queue Depth:     {queue_depth}')
        self.stdout.write(f'  Throughput:      {processing.get("throughput", 0):.2f}/min')
        self.stdout.write(f'  Avg Latency:     {processing.get("avg_latency_ms", 0):.0f}ms')
        self.stdout.write('')

        # Enrichment stage
        enrichment = stages.get('enrichment', {})
        self.stdout.write('  ENRICHMENT Stage (Embeddings & Scoring):')
        self.stdout.write('  ' + '-' * 40)
        enrich_status = enrichment.get('status', 'unknown')
        enrich_style = self._get_status_style(enrich_status)
        self.stdout.write(f'  Status:          {enrich_style(enrich_status.upper())}')
        self.stdout.write(f'  Embeddings:      {enrichment.get("embeddings_generated", 0)}')
        coverage = enrichment.get('coverage', 0)
        if coverage < 50:
            self.stdout.write(self.style.WARNING(f'  Coverage:        {coverage:.1f}%'))
        else:
            self.stdout.write(f'  Coverage:        {coverage:.1f}%')
        self.stdout.write('')

        # Routing stage
        routing = stages.get('routing', {})
        self.stdout.write('  ROUTING Stage (Agent Distribution):')
        self.stdout.write('  ' + '-' * 40)
        route_status = routing.get('status', 'unknown')
        route_style = self._get_status_style(route_status)
        self.stdout.write(f'  Status:          {route_style(route_status.upper())}')
        self.stdout.write(f'  Items Routed:    {routing.get("items_routed", 0)}')
        self.stdout.write(f'  Items Filtered:  {routing.get("items_filtered", 0)}')
        self.stdout.write('')

        # Metabolism
        metabolism = result.get('metabolism', {})
        if metabolism:
            self.stdout.write('  METABOLISM (Throughput):')
            self.stdout.write('  ' + '-' * 40)
            self.stdout.write(f'  Intake Rate:     {metabolism.get("intake_rate", 0):.3f}/min')
            self.stdout.write(f'  Processing Rate: {metabolism.get("processing_rate", 0):.3f}/min')
            self.stdout.write(f'  Output Rate:     {metabolism.get("output_rate", 0):.3f}/min')
            self.stdout.write('')

        # Bottlenecks
        bottlenecks = result.get('bottlenecks', [])
        if bottlenecks:
            self.stdout.write('  BOTTLENECKS DETECTED:')
            self.stdout.write('  ' + '-' * 40)
            for b in bottlenecks:
                severity = b.get('severity', 'info')
                stage = b.get('stage', 'unknown')
                issue = b.get('issue', 'Unknown issue')
                style = self._get_severity_style(severity)
                self.stdout.write(f'  [{style(severity.upper())}] {stage}: {issue}')
            self.stdout.write('')

        self.stdout.write('=' * 60)
        self.stdout.write('')

    def _show_routes(self, digestive, as_json: bool):
        """List all ingestion routes."""
        routes = digestive.get_routes(active_only=False)

        if as_json:
            self.stdout.write(json.dumps(routes, indent=2, default=str))
            return

        self.stdout.write('')
        self.stdout.write('=' * 100)
        self.stdout.write('  DIGESTIVE Ingestion Routes')
        self.stdout.write('=' * 100)
        self.stdout.write('')
        self.stdout.write(f'  {"Name":<30} {"Type":<10} {"Stage":<12} {"Status":<10} {"Critical":<10}')
        self.stdout.write('  ' + '-' * 96)

        for r in routes:
            name = r.get('display_name', r.get('name', 'Unknown'))[:30]
            route_type = r.get('route_type', 'unknown')[:10]
            stage = r.get('stage', 'unknown')[:12]
            is_active = 'Active' if r.get('is_active', False) else 'Inactive'
            is_critical = 'Yes' if r.get('is_critical', False) else 'No'

            active_style = self.style.SUCCESS if r.get('is_active') else self.style.ERROR
            critical_style = self.style.WARNING if r.get('is_critical') else self.style.HTTP_INFO

            self.stdout.write(
                f'  {name:<30} {route_type:<10} {stage:<12} '
                f'{active_style(is_active):<10} {critical_style(is_critical):<10}'
            )

        self.stdout.write('')
        self.stdout.write(f'  Total: {len(routes)} routes')
        self.stdout.write('')

    def _show_bottlenecks(self, digestive, as_json: bool):
        """Show current bottlenecks."""
        # Get fresh data
        intake = digestive.check_intake()
        processing = digestive.check_processing()
        enrichment = digestive.check_enrichment()
        routing = digestive.check_routing()

        bottlenecks = digestive.detect_bottlenecks(
            intake, processing, enrichment, routing
        )

        if as_json:
            self.stdout.write(json.dumps(bottlenecks, indent=2, default=str))
            return

        self.stdout.write('')
        self.stdout.write('=' * 80)
        self.stdout.write('  DIGESTIVE Bottlenecks')
        self.stdout.write('=' * 80)
        self.stdout.write('')

        if not bottlenecks:
            self.stdout.write(self.style.SUCCESS('  No bottlenecks detected! System is digesting smoothly.'))
            self.stdout.write('')
            return

        # Group by severity
        critical = [b for b in bottlenecks if b.get('severity') == 'critical']
        warning = [b for b in bottlenecks if b.get('severity') == 'warning']
        info = [b for b in bottlenecks if b.get('severity') == 'info']

        if critical:
            self.stdout.write(self.style.ERROR('  CRITICAL:'))
            for b in critical:
                self.stdout.write(self.style.ERROR(f'    [{b["stage"]}] {b["issue"]}'))
            self.stdout.write('')

        if warning:
            self.stdout.write(self.style.WARNING('  WARNING:'))
            for b in warning:
                self.stdout.write(self.style.WARNING(f'    [{b["stage"]}] {b["issue"]}'))
            self.stdout.write('')

        if info:
            self.stdout.write('  INFO:')
            for b in info:
                self.stdout.write(f'    [{b["stage"]}] {b["issue"]}')
            self.stdout.write('')

        self.stdout.write(f'  Total: {len(bottlenecks)} bottlenecks ({len(critical)} critical, {len(warning)} warning)')
        self.stdout.write('')

    def _show_metabolism(self, digestive, as_json: bool):
        """Show throughput metrics."""
        metabolism = digestive.get_metabolism_rate()

        if as_json:
            self.stdout.write(json.dumps(metabolism, indent=2, default=str))
            return

        self.stdout.write('')
        self.stdout.write('=' * 60)
        self.stdout.write('  DIGESTIVE Metabolism (Throughput)')
        self.stdout.write('=' * 60)
        self.stdout.write('')

        intake = metabolism.get('intake_rate', 0)
        processing = metabolism.get('processing_rate', 0)
        output = metabolism.get('output_rate', 0)

        self.stdout.write('  Current Rates (items/minute):')
        self.stdout.write('  ' + '-' * 40)
        self.stdout.write(f'  Intake:          {intake:.3f}/min ({intake * 60:.1f}/hr)')
        self.stdout.write(f'  Processing:      {processing:.3f}/min ({processing * 60:.1f}/hr)')
        self.stdout.write(f'  Output:          {output:.3f}/min ({output * 60:.1f}/hr)')
        self.stdout.write('')

        # Check for imbalances
        self.stdout.write('  Balance Analysis:')
        self.stdout.write('  ' + '-' * 40)

        if intake > 0:
            efficiency = (output / intake) * 100
            self.stdout.write(f'  Efficiency:      {efficiency:.1f}%')

        if intake > processing * 1.5 and intake > 1:
            self.stdout.write(self.style.WARNING('  ⚠️  Backlog Risk: Intake exceeds processing'))
        elif processing > output * 2 and processing > 1:
            self.stdout.write(self.style.WARNING('  ⚠️  Routing Bottleneck: Processing > routing'))
        elif intake < 0.5 and output < 0.5:
            self.stdout.write(self.style.WARNING('  ⚠️  Low Activity: Check spider health'))
        else:
            self.stdout.write(self.style.SUCCESS('  ✓  Metabolism balanced'))

        self.stdout.write('')

    def _show_history(self, digestive, hours: int, as_json: bool):
        """Show digestion pulse history."""
        history = digestive.get_history(hours=hours, limit=50)

        if as_json:
            self.stdout.write(json.dumps(history, indent=2, default=str))
            return

        self.stdout.write('')
        self.stdout.write('=' * 90)
        self.stdout.write(f'  DIGESTIVE Pulse History (Last {hours} hours)')
        self.stdout.write('=' * 90)
        self.stdout.write('')

        if not history:
            self.stdout.write('  No digestion pulses recorded in this period.')
            self.stdout.write('')
            return

        self.stdout.write(f'  {"Timestamp":<20} {"Status":<12} {"Score":<8} {"Ingested":<10} {"Processed":<10} {"Pending":<10}')
        self.stdout.write('  ' + '-' * 86)

        for h in history[:30]:  # Limit to 30
            ts = str(h.get('recorded_at', ''))[:19] if h.get('recorded_at') else 'N/A'
            status = h.get('overall_status', 'unknown')
            score = h.get('digestion_score', 0)
            ingested = h.get('items_ingested_24h', 0)
            processed = h.get('items_processed_24h', 0)
            pending = h.get('items_pending', 0)

            status_style = self._get_status_style(status)
            self.stdout.write(
                f'  {ts:<20} {status_style(status):<12} {score:.1f}%    '
                f'{ingested:<10} {processed:<10} {pending:<10}'
            )

        self.stdout.write('')
        self.stdout.write(f'  Showing {min(30, len(history))} of {len(history)} pulses')
        self.stdout.write('')

    def _show_stage(self, digestive, stage: str, as_json: bool):
        """Check specific stage only."""
        if stage == 'intake':
            result = digestive.check_intake()
        elif stage == 'processing':
            result = digestive.check_processing()
        elif stage == 'enrichment':
            result = digestive.check_enrichment()
        elif stage == 'routing':
            result = digestive.check_routing()
        else:
            raise CommandError(f'Unknown stage: {stage}')

        if as_json:
            self.stdout.write(json.dumps(result, indent=2, default=str))
            return

        self.stdout.write('')
        self.stdout.write('=' * 60)
        self.stdout.write(f'  DIGESTIVE - {stage.upper()} Stage')
        self.stdout.write('=' * 60)
        self.stdout.write('')

        for key, value in result.items():
            if isinstance(value, float):
                self.stdout.write(f'  {key}: {value:.2f}')
            else:
                self.stdout.write(f'  {key}: {value}')

        self.stdout.write('')

    def _watch_mode(self, digestive, as_json: bool):
        """Continuous monitoring mode."""
        self.stdout.write('')
        self.stdout.write('DIGESTIVE Watch Mode - Press Ctrl+C to stop')
        self.stdout.write('Checking every 60 seconds...')
        self.stdout.write('')

        try:
            while True:
                result = digestive.digest(force=True)

                if as_json:
                    self.stdout.write(json.dumps({
                        'timestamp': result['timestamp'],
                        'status': result['overall_status'],
                        'digestion_score': result['digestion_score'],
                        'is_digesting': result.get('is_digesting', True),
                        'bottlenecks_count': len(result.get('bottlenecks', [])),
                    }))
                else:
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    status = result['overall_status']
                    score = result['digestion_score']
                    bottlenecks = len(result.get('bottlenecks', []))
                    emoji = self._get_status_emoji(status)

                    style = self._get_status_style(status)

                    self.stdout.write(
                        f'[{timestamp}] {emoji} {style(status.upper())} '
                        f'({score:.1f}%)'
                    )

                    if bottlenecks > 0:
                        self.stdout.write(self.style.WARNING(
                            f'           {bottlenecks} bottleneck(s) detected'
                        ))

                time.sleep(60)

        except KeyboardInterrupt:
            self.stdout.write('')
            self.stdout.write('Watch mode stopped.')
            self.stdout.write('')

    def _get_status_emoji(self, status: str) -> str:
        """Get emoji for status."""
        return {
            'healthy': '🟢',      # Green - normal
            'sluggish': '🟡',     # Yellow - slow
            'bloated': '🟠',      # Orange - backlog
            'blocked': '🔴',      # Red - stuck
            'starving': '⚪',     # White - no data
        }.get(status, '❓')

    def _get_status_style(self, status: str):
        """Get style function for status."""
        if status == 'healthy':
            return self.style.SUCCESS
        elif status == 'sluggish':
            return self.style.HTTP_INFO
        elif status == 'bloated':
            return self.style.WARNING
        elif status in ('blocked', 'starving'):
            return self.style.ERROR
        return self.style.HTTP_INFO

    def _get_severity_style(self, severity: str):
        """Get style function for severity."""
        if severity == 'critical':
            return self.style.ERROR
        elif severity == 'warning':
            return self.style.WARNING
        return self.style.HTTP_INFO
