"""
Session 704: SPINE Check Management Command

CLI command for checking spine (central API router) health.
The backbone of the AI body - monitors API route patterns and health.

Usage:
    python manage.py spine_check                    # Full alignment check
    python manage.py spine_check --json             # JSON output
    python manage.py spine_check --patterns         # List all patterns
    python manage.py spine_check --categories       # Show category breakdown
    python manage.py spine_check --pattern /api/agents/  # Specific pattern
    python manage.py spine_check --watch            # Continuous monitoring (60s)
    python manage.py spine_check --history          # Show alignment history

Output includes:
    - Overall spine status (aligned/strained/compressed/injured)
    - Health score (0-100%)
    - Pattern health breakdown by category
    - Integration status with HEART/LUNGS/CIRCULATORY
    - Routing status (blocked, rate-limited, fallbacks)
"""

import json
import time
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone


class Command(BaseCommand):
    help = 'Check SPINE (central API router) health and alignment'

    def add_arguments(self, parser):
        parser.add_argument(
            '--json',
            action='store_true',
            help='Output results as JSON'
        )
        parser.add_argument(
            '--patterns',
            action='store_true',
            help='List all route patterns'
        )
        parser.add_argument(
            '--categories',
            action='store_true',
            help='Show category health breakdown'
        )
        parser.add_argument(
            '--pattern',
            type=str,
            help='Check specific route pattern'
        )
        parser.add_argument(
            '--can-route',
            type=str,
            dest='can_route',
            help='Check if path can be routed'
        )
        parser.add_argument(
            '--watch',
            action='store_true',
            help='Continuous monitoring mode (60s interval)'
        )
        parser.add_argument(
            '--history',
            action='store_true',
            help='Show alignment history'
        )
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='History lookback period in hours (default: 24)'
        )

    def handle(self, *args, **options):
        from core.services.spine import get_spine_router

        spine = get_spine_router()

        if options['patterns']:
            self._show_patterns(spine, options['json'])
        elif options['categories']:
            self._show_categories(spine, options['json'])
        elif options['pattern']:
            self._check_pattern(spine, options['pattern'], options['json'])
        elif options['can_route']:
            self._check_can_route(spine, options['can_route'], options['json'])
        elif options['history']:
            self._show_history(spine, options['hours'], options['json'])
        elif options['watch']:
            self._watch_mode(spine, options['json'])
        else:
            self._full_check(spine, options['json'])

    def _full_check(self, spine, as_json: bool):
        """Run full spine alignment check."""
        result = spine.align()

        if as_json:
            self.stdout.write(json.dumps(result, indent=2, default=str))
            return

        # Header
        self.stdout.write('')
        self.stdout.write('=' * 60)
        self.stdout.write('  SPINE - Central API Router Health Check')
        self.stdout.write('  The Backbone of the AI Body')
        self.stdout.write('=' * 60)

        # Overall status
        status = result['overall_status']
        score = result['health_score']
        emoji = self._get_status_emoji(status)
        status_text = f"{status.upper():<12}"
        status_style = self._get_status_style(status)

        self.stdout.write(f'  Overall Status: {status_style(status_text)} {emoji}')
        self.stdout.write(f'  Health Score: {score:.1f}%')
        self.stdout.write(f'  Is Aligned: {"Yes" if result["is_aligned"] else "No"}')
        self.stdout.write(f'  Check Duration: {result["check_duration_ms"]:.0f}ms')
        self.stdout.write('')

        # Pattern summary
        self.stdout.write('  Pattern Summary:')
        self.stdout.write('  ' + '-' * 40)
        self.stdout.write(f'  Total Patterns:   {result["total_patterns"]}')
        self.stdout.write(self.style.SUCCESS(f'  Healthy:          {result["healthy_patterns"]}'))
        if result['degraded_patterns'] > 0:
            self.stdout.write(self.style.WARNING(f'  Degraded:         {result["degraded_patterns"]}'))
        else:
            self.stdout.write(f'  Degraded:         {result["degraded_patterns"]}')
        if result['failed_patterns'] > 0:
            self.stdout.write(self.style.ERROR(f'  Failed:           {result["failed_patterns"]}'))
        else:
            self.stdout.write(f'  Failed:           {result["failed_patterns"]}')
        self.stdout.write('')

        # Routing status
        routing = result['routing']
        self.stdout.write('  Routing Status:')
        self.stdout.write('  ' + '-' * 40)
        if routing['routes_blocked'] > 0:
            self.stdout.write(self.style.ERROR(f'  Routes Blocked:   {routing["routes_blocked"]}'))
        else:
            self.stdout.write(f'  Routes Blocked:   {routing["routes_blocked"]}')
        if routing['routes_rate_limited'] > 0:
            self.stdout.write(self.style.WARNING(f'  Rate Limited:     {routing["routes_rate_limited"]}'))
        else:
            self.stdout.write(f'  Rate Limited:     {routing["routes_rate_limited"]}')
        self.stdout.write(f'  Fallbacks Active: {routing["fallbacks_active"]}')
        self.stdout.write('')

        # Integration status
        integrations = result['integrations']
        self.stdout.write('  Integration Status:')
        self.stdout.write('  ' + '-' * 40)

        heart = integrations.get('heart', {})
        heart_status = heart.get('status', 'unknown')
        heart_style = self.style.SUCCESS if heart.get('is_healthy') else self.style.WARNING
        self.stdout.write(f'  HEART:        {heart_style(heart_status)}')

        lungs = integrations.get('lungs', {})
        lungs_status = lungs.get('status', 'unknown')
        lungs_style = self.style.SUCCESS if lungs.get('is_healthy') else self.style.WARNING
        self.stdout.write(f'  LUNGS:        {lungs_style(lungs_status)}')

        circulatory = integrations.get('circulatory', {})
        circ_status = circulatory.get('status', 'unknown')
        circ_style = self.style.SUCCESS if circulatory.get('is_flowing') else self.style.WARNING
        self.stdout.write(f'  CIRCULATORY:  {circ_style(circ_status)}')
        self.stdout.write('')

        # Category breakdown
        category_health = result.get('category_health', {})
        if category_health:
            self.stdout.write('  Category Health:')
            self.stdout.write('  ' + '-' * 40)
            for category, data in sorted(category_health.items()):
                cat_score = data.get('health_score', 0)
                count = data.get('pattern_count', 0)
                style = self._get_score_style(cat_score)
                self.stdout.write(f'  {category:<15} {style(f"{cat_score:>5.1f}%")} ({count} patterns)')
            self.stdout.write('')

        # Request metrics
        metrics = result.get('metrics', {})
        if metrics:
            self.stdout.write('  Request Metrics:')
            self.stdout.write('  ' + '-' * 40)
            self.stdout.write(f'  Total Requests:  {metrics.get("total_requests", 0):,}')
            error_rate = metrics.get('error_rate', 0)
            if error_rate > 0.05:
                self.stdout.write(self.style.ERROR(f'  Error Rate:      {error_rate:.2%}'))
            elif error_rate > 0.01:
                self.stdout.write(self.style.WARNING(f'  Error Rate:      {error_rate:.2%}'))
            else:
                self.stdout.write(f'  Error Rate:      {error_rate:.2%}')
            self.stdout.write(f'  Avg Latency:     {metrics.get("avg_latency_ms", 0):.1f}ms')

        self.stdout.write('=' * 60)
        self.stdout.write('')

    def _show_patterns(self, spine, as_json: bool):
        """List all route patterns."""
        patterns = spine.get_patterns(active_only=False)

        if as_json:
            self.stdout.write(json.dumps(patterns, indent=2))
            return

        self.stdout.write('')
        self.stdout.write('=' * 80)
        self.stdout.write('  SPINE Route Patterns')
        self.stdout.write('=' * 80)
        self.stdout.write('')
        self.stdout.write(f'  {"Pattern":<30} {"Category":<12} {"Priority":<10} {"Active":<8} {"Monitored":<10}')
        self.stdout.write('  ' + '-' * 76)

        for p in patterns:
            active = "Yes" if p['is_active'] else "No"
            monitored = "Yes" if p['is_monitored'] else "No"
            active_style = self.style.SUCCESS if p['is_active'] else self.style.ERROR
            self.stdout.write(
                f'  {p["pattern"]:<30} {p["category"]:<12} {p["priority"]:<10} '
                f'{active_style(active):<8} {monitored:<10}'
            )

        self.stdout.write('')
        self.stdout.write(f'  Total: {len(patterns)} patterns')
        self.stdout.write('')

    def _show_categories(self, spine, as_json: bool):
        """Show category breakdown."""
        vitals = spine.get_vitals()
        category_health = vitals.get('category_health', {})

        if as_json:
            self.stdout.write(json.dumps(category_health, indent=2))
            return

        self.stdout.write('')
        self.stdout.write('=' * 60)
        self.stdout.write('  SPINE Category Health')
        self.stdout.write('=' * 60)
        self.stdout.write('')
        self.stdout.write(f'  {"Category":<20} {"Health Score":<15} {"Patterns":<10}')
        self.stdout.write('  ' + '-' * 50)

        for category, data in sorted(category_health.items()):
            score = data.get('health_score', 0)
            count = data.get('pattern_count', 0)
            style = self._get_score_style(score)
            self.stdout.write(f'  {category:<20} {style(f"{score:>6.1f}%"):<15} {count:<10}')

        self.stdout.write('')

    def _check_pattern(self, spine, pattern_path: str, as_json: bool):
        """Check specific route pattern."""
        metrics = spine.get_route_metrics(pattern_path)

        if as_json:
            self.stdout.write(json.dumps(metrics, indent=2))
            return

        if 'error' in metrics:
            self.stdout.write(self.style.ERROR(f'Error: {metrics["error"]}'))
            return

        self.stdout.write('')
        self.stdout.write('=' * 60)
        self.stdout.write(f'  Pattern: {metrics.get("pattern", pattern_path)}')
        self.stdout.write('=' * 60)
        self.stdout.write('')
        self.stdout.write(f'  Display Name: {metrics.get("display_name", "N/A")}')
        self.stdout.write(f'  Category:     {metrics.get("category", "N/A")}')
        self.stdout.write(f'  Priority:     {metrics.get("priority", "N/A")}')
        self.stdout.write(f'  Period:       Last {metrics.get("period_hours", 24)} hours')
        self.stdout.write('')

        m = metrics.get('metrics', {})
        self.stdout.write('  Metrics:')
        self.stdout.write('  ' + '-' * 40)
        self.stdout.write(f'  Total Requests:     {m.get("total_requests", 0):,}')
        self.stdout.write(f'  Successful:         {m.get("successful_requests", 0):,}')
        self.stdout.write(f'  Failed:             {m.get("failed_requests", 0):,}')
        self.stdout.write(f'  Success Rate:       {m.get("success_rate", 1.0):.2%}')
        self.stdout.write(f'  Avg Latency:        {m.get("avg_latency_ms", 0):.1f}ms')
        self.stdout.write(f'  P95 Latency:        {m.get("p95_latency_ms", 0):.1f}ms')
        self.stdout.write(f'  Avg Health Score:   {m.get("avg_health_score", 100):.1f}%')
        self.stdout.write('')

        t = metrics.get('thresholds', {})
        self.stdout.write('  Thresholds:')
        self.stdout.write('  ' + '-' * 40)
        self.stdout.write(f'  Max Latency:        {t.get("max_latency_ms", 0)}ms')
        self.stdout.write(f'  Max Error Rate:     {t.get("max_error_rate", 0.05):.2%}')
        self.stdout.write(f'  Min Availability:   {t.get("min_availability", 0.95):.2%}')
        self.stdout.write('')

    def _check_can_route(self, spine, path: str, as_json: bool):
        """Check if path can be routed."""
        can_route, reason = spine.can_route(path)

        if as_json:
            self.stdout.write(json.dumps({
                'path': path,
                'can_route': can_route,
                'reason': reason
            }, indent=2))
            return

        self.stdout.write('')
        self.stdout.write(f'  Path: {path}')
        if can_route:
            self.stdout.write(self.style.SUCCESS(f'  Can Route: Yes'))
        else:
            self.stdout.write(self.style.ERROR(f'  Can Route: No'))
        self.stdout.write(f'  Reason: {reason}')
        self.stdout.write('')

    def _show_history(self, spine, hours: int, as_json: bool):
        """Show alignment history."""
        history = spine.get_history(hours=hours)

        if as_json:
            self.stdout.write(json.dumps(history, indent=2))
            return

        self.stdout.write('')
        self.stdout.write('=' * 80)
        self.stdout.write(f'  SPINE Alignment History (Last {hours} hours)')
        self.stdout.write('=' * 80)
        self.stdout.write('')

        if not history:
            self.stdout.write('  No history records found.')
            return

        self.stdout.write(f'  {"Timestamp":<24} {"Pattern":<25} {"Score":<8} {"Healthy":<8} {"Requests":<10}')
        self.stdout.write('  ' + '-' * 78)

        for h in history[:50]:  # Limit to 50 records
            ts = h.get('timestamp', '')[:19]
            pattern = h.get('pattern', 'N/A')[:25]
            score = h.get('health_score', 0)
            healthy = "Yes" if h.get('is_healthy') else "No"
            requests = h.get('total_requests', 0)

            style = self._get_score_style(score)
            self.stdout.write(f'  {ts:<24} {pattern:<25} {style(f"{score:>5.1f}%")} {healthy:<8} {requests:<10}')

        self.stdout.write('')
        self.stdout.write(f'  Showing {min(50, len(history))} of {len(history)} records')
        self.stdout.write('')

    def _watch_mode(self, spine, as_json: bool):
        """Continuous monitoring mode."""
        self.stdout.write('')
        self.stdout.write('SPINE Watch Mode - Press Ctrl+C to stop')
        self.stdout.write('Checking every 60 seconds...')
        self.stdout.write('')

        try:
            while True:
                result = spine.align()

                if as_json:
                    self.stdout.write(json.dumps({
                        'timestamp': result['timestamp'],
                        'status': result['overall_status'],
                        'health_score': result['health_score'],
                        'healthy': result['healthy_patterns'],
                        'total': result['total_patterns'],
                    }))
                else:
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    status = result['overall_status']
                    score = result['health_score']
                    healthy = result['healthy_patterns']
                    total = result['total_patterns']
                    emoji = self._get_status_emoji(status)

                    style = self._get_status_style(status)
                    status_text = f"{status.upper()}"

                    self.stdout.write(
                        f'[{timestamp}] {emoji} {style(status_text)} '
                        f'({score:.1f}%) - {healthy}/{total} healthy'
                    )

                    # Show any issues
                    if result['failed_patterns'] > 0:
                        self.stdout.write(self.style.ERROR(
                            f'           {result["failed_patterns"]} patterns FAILING!'
                        ))
                    if result['routing']['routes_blocked'] > 0:
                        self.stdout.write(self.style.WARNING(
                            f'           {result["routing"]["routes_blocked"]} routes blocked'
                        ))

                time.sleep(60)

        except KeyboardInterrupt:
            self.stdout.write('')
            self.stdout.write('Watch mode stopped.')

    def _get_status_emoji(self, status: str) -> str:
        """Get emoji for status."""
        return {
            'aligned': '🦴',
            'strained': '⚡',
            'compressed': '🔧',
            'injured': '🚨',
        }.get(status, '❓')

    def _get_status_style(self, status: str):
        """Get style function for status."""
        if status == 'aligned':
            return self.style.SUCCESS
        elif status == 'strained':
            return self.style.WARNING
        elif status in ('compressed', 'injured'):
            return self.style.ERROR
        return lambda x: x

    def _get_score_style(self, score: float):
        """Get style function for health score."""
        if score >= 90:
            return self.style.SUCCESS
        elif score >= 70:
            return self.style.WARNING
        else:
            return self.style.ERROR
