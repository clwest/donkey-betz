"""
Session 703: CIRCULATORY SYSTEM Management Command

CLI tool for monitoring data flow health - the circulation of the AI body.
Checks Redis queues, Celery tasks, WebSocket channels, and event streams.

Usage:
    python manage.py circulation_check                  # Full circulation check
    python manage.py circulation_check --json           # JSON output
    python manage.py circulation_check --routes         # List all routes
    python manage.py circulation_check --bottlenecks    # Show bottlenecks only
    python manage.py circulation_check --velocity       # Show flow velocity
    python manage.py circulation_check --watch          # Continuous monitoring (30s)
    python manage.py circulation_check --history        # Show pulse history
    python manage.py circulation_check --route celery_default  # Specific route
"""

import json
import time
import sys
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = 'Check data flow health - the CIRCULATORY SYSTEM of the AI body'

    def add_arguments(self, parser):
        parser.add_argument(
            '--json',
            action='store_true',
            help='Output in JSON format'
        )
        parser.add_argument(
            '--routes',
            action='store_true',
            help='List all monitored routes'
        )
        parser.add_argument(
            '--bottlenecks',
            action='store_true',
            help='Show current bottlenecks only'
        )
        parser.add_argument(
            '--velocity',
            action='store_true',
            help='Show flow velocity metrics'
        )
        parser.add_argument(
            '--watch',
            action='store_true',
            help='Continuous monitoring mode (30s interval)'
        )
        parser.add_argument(
            '--history',
            action='store_true',
            help='Show circulation pulse history'
        )
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Hours of history to show (default: 24)'
        )
        parser.add_argument(
            '--route',
            type=str,
            help='Check specific route by name'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Limit history records (default: 50)'
        )

    def handle(self, *args, **options):
        from core.services.circulatory import get_circulatory_system
        from core.models_circulatory import FlowRoute, CirculationPulse, FlowStatus

        circulatory = get_circulatory_system()

        if options['json']:
            self.output_json(circulatory, options)
        elif options['routes']:
            self.list_routes()
        elif options['bottlenecks']:
            self.show_bottlenecks(circulatory)
        elif options['velocity']:
            self.show_velocity(circulatory, options.get('hours', 1))
        elif options['history']:
            self.show_history(options.get('hours', 24), options.get('limit', 50))
        elif options['route']:
            self.check_specific_route(circulatory, options['route'])
        elif options['watch']:
            self.watch_mode(circulatory)
        else:
            self.full_check(circulatory)

    def output_json(self, circulatory, options):
        """Output in JSON format."""
        result = circulatory.circulate()
        self.stdout.write(json.dumps(result, indent=2, default=str))

    def list_routes(self):
        """List all monitored routes."""
        from core.models_circulatory import FlowRoute, FlowStatus

        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('  CIRCULATORY SYSTEM - Monitored Flow Routes'))
        self.stdout.write(self.style.SUCCESS('  The Blood Vessels of the AI Body'))
        self.stdout.write('=' * 70)

        routes = FlowRoute.objects.filter(is_active=True).order_by('route_type', 'name')

        current_type = None
        for route in routes:
            if route.route_type != current_type:
                current_type = route.route_type
                self.stdout.write(f'\n  {route.get_route_type_display().upper()}')
                self.stdout.write('  ' + '-' * 50)

            # Get status
            try:
                status = route.current_status
                emoji = status.get_status_display_emoji()
                score = f"{status.health_score:.0f}%"
                state = status.status.upper()
            except FlowStatus.DoesNotExist:
                emoji = '❓'
                score = 'N/A'
                state = 'UNKNOWN'

            critical_badge = ' [CRITICAL]' if route.is_critical else ''
            self.stdout.write(
                f"  {emoji} {route.display_name or route.name:<35} "
                f"{state:<10} {score:>5}{critical_badge}"
            )

        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(f'  Total Routes: {routes.count()}\n')

    def show_bottlenecks(self, circulatory):
        """Show current bottlenecks."""
        bottlenecks = circulatory.detect_bottlenecks()

        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.WARNING('  CIRCULATORY SYSTEM - Bottlenecks Detected'))
        self.stdout.write('=' * 70)

        if not bottlenecks:
            self.stdout.write(self.style.SUCCESS('\n  No bottlenecks detected - Flow is healthy!\n'))
            return

        for b in bottlenecks:
            severity = b.get('severity', 'info')
            if severity == 'critical':
                style = self.style.ERROR
                icon = '🚫'
            elif severity == 'warning':
                style = self.style.WARNING
                icon = '⚠️'
            else:
                style = self.style.NOTICE
                icon = 'ℹ️'

            self.stdout.write(style(
                f"\n  {icon} {b['route']}"
            ))
            self.stdout.write(f"     Issue: {b['issue']}")
            self.stdout.write(f"     Severity: {severity.upper()}")
            if b.get('recommendation'):
                self.stdout.write(f"     Recommendation: {b['recommendation']}")

        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(f'  Total Bottlenecks: {len(bottlenecks)}\n')

    def show_velocity(self, circulatory, hours):
        """Show flow velocity metrics."""
        velocity = circulatory.get_flow_velocity(hours=hours)

        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS(f'  CIRCULATORY SYSTEM - Flow Velocity (Last {hours}h)'))
        self.stdout.write('=' * 70)

        self.stdout.write(f"\n  Total Throughput:   {velocity.get('total_throughput', 0):.2f} items/sec")
        self.stdout.write(f"  Average Latency:    {velocity.get('avg_latency_ms', 0):.0f}ms")
        self.stdout.write(f"  Peak Throughput:    {velocity.get('peak_throughput', 0):.2f} items/sec")
        self.stdout.write(f"  Peak Latency:       {velocity.get('peak_latency_ms', 0):.0f}ms")
        self.stdout.write(f"  Total Items:        {velocity.get('total_items', 0):,}")
        self.stdout.write(f"  Check Count:        {velocity.get('check_count', 0)}")

        # Trend indicators
        trend = velocity.get('trend', {})
        if trend:
            throughput_trend = trend.get('throughput_trend', 'stable')
            latency_trend = trend.get('latency_trend', 'stable')
            self.stdout.write(f"\n  Throughput Trend:   {throughput_trend}")
            self.stdout.write(f"  Latency Trend:      {latency_trend}")

        self.stdout.write('\n' + '=' * 70 + '\n')

    def show_history(self, hours, limit):
        """Show circulation pulse history."""
        from core.models_circulatory import CirculationPulse
        from datetime import timedelta

        since = timezone.now() - timedelta(hours=hours)
        pulses = CirculationPulse.objects.filter(
            recorded_at__gte=since
        ).order_by('-recorded_at')[:limit]

        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS(f'  CIRCULATORY SYSTEM - Pulse History (Last {hours}h)'))
        self.stdout.write('=' * 70)

        if not pulses:
            self.stdout.write(self.style.WARNING('\n  No pulse history found.\n'))
            return

        self.stdout.write('\n  Timestamp             Status      Flow    Routes  Bottlenecks')
        self.stdout.write('  ' + '-' * 60)

        for pulse in pulses:
            status_style = self._get_status_style(pulse.overall_status)
            status_text = f"{pulse.overall_status.upper():<10}"
            self.stdout.write(
                f"  {pulse.recorded_at.strftime('%Y-%m-%d %H:%M:%S')}  "
                f"{status_style(status_text)}  "
                f"{pulse.flow_score:>5.1f}%  "
                f"{pulse.routes_healthy}/{pulse.total_routes_checked}     "
                f"{pulse.bottleneck_count}"
            )

        # Summary
        avg_score = sum(p.flow_score for p in pulses) / len(pulses) if pulses else 0
        blocked_count = sum(1 for p in pulses if p.overall_status == 'blocked')

        self.stdout.write('\n  ' + '-' * 60)
        self.stdout.write(f"  Average Flow Score: {avg_score:.1f}%")
        self.stdout.write(f"  Blocked Events: {blocked_count}")
        self.stdout.write(f"  Records Shown: {len(pulses)}")
        self.stdout.write('\n' + '=' * 70 + '\n')

    def check_specific_route(self, circulatory, route_name):
        """Check a specific route."""
        from core.models_circulatory import FlowRoute, FlowStatus

        try:
            route = FlowRoute.objects.get(name=route_name)
        except FlowRoute.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'\nRoute not found: {route_name}'))
            self.stdout.write('Use --routes to list available routes.\n')
            return

        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS(f'  CIRCULATORY SYSTEM - Route: {route.display_name}'))
        self.stdout.write('=' * 70)

        self.stdout.write(f'\n  Name:        {route.name}')
        self.stdout.write(f'  Type:        {route.get_route_type_display()}')
        self.stdout.write(f'  Identifier:  {route.identifier}')
        self.stdout.write(f'  Max Depth:   {route.max_depth}')
        self.stdout.write(f'  Max Latency: {route.max_latency_ms}ms')
        self.stdout.write(f'  Critical:    {"Yes" if route.is_critical else "No"}')
        if route.description:
            self.stdout.write(f'  Description: {route.description}')

        # Get current status
        try:
            status = route.current_status
            status_style = self._get_status_style(status.status)

            self.stdout.write('\n  Current Status:')
            self.stdout.write('  ' + '-' * 30)
            self.stdout.write(f'  {status.get_status_display_emoji()} Status: {status_style(status.status.upper())}')
            self.stdout.write(f'  Health Score:    {status.health_score:.1f}%')
            self.stdout.write(f'  Current Depth:   {status.current_depth}')
            self.stdout.write(f'  Throughput:      {status.current_throughput:.2f}/sec')
            self.stdout.write(f'  Latency:         {status.current_latency_ms:.0f}ms')

            if status.active_workers > 0:
                self.stdout.write(f'\n  Workers:')
                self.stdout.write(f'    Active Workers:  {status.active_workers}')
                self.stdout.write(f'    Active Tasks:    {status.active_tasks}')
                self.stdout.write(f'    Reserved Tasks:  {status.reserved_tasks}')

            self.stdout.write(f'\n  24h Metrics:')
            self.stdout.write(f'    Items Processed: {status.items_processed_24h:,}')
            self.stdout.write(f'    Errors:          {status.errors_24h}')
            self.stdout.write(f'    Avg Latency:     {status.avg_latency_24h_ms:.0f}ms')
            self.stdout.write(f'    Peak Depth:      {status.peak_depth_24h}')

            if status.last_check:
                self.stdout.write(f'\n  Last Check: {status.last_check.strftime("%Y-%m-%d %H:%M:%S")}')

        except FlowStatus.DoesNotExist:
            self.stdout.write(self.style.WARNING('\n  No status data available for this route.\n'))

        self.stdout.write('\n' + '=' * 70 + '\n')

    def watch_mode(self, circulatory):
        """Continuous monitoring mode."""
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('  CIRCULATORY SYSTEM - Watch Mode'))
        self.stdout.write(self.style.SUCCESS('  Press Ctrl+C to stop'))
        self.stdout.write('=' * 70 + '\n')

        try:
            while True:
                result = circulatory.circulate()

                # Clear line and show status
                status_style = self._get_status_style(result['overall_status'])
                timestamp = timezone.now().strftime('%H:%M:%S')
                status_text = f"{result['overall_status'].upper():<10}"

                status_line = (
                    f"  [{timestamp}] "
                    f"{status_style(status_text)} "
                    f"Flow: {result['flow_score']:.1f}% | "
                    f"Routes: {result['routes_healthy']}/{result['routes_checked']} | "
                    f"Bottlenecks: {result['bottleneck_count']} | "
                    f"Items: {result.get('flow_metrics', {}).get('total_items_in_transit', 0):,}"
                )
                self.stdout.write(status_line)

                # Show bottlenecks if any
                for b in result.get('bottlenecks', [])[:3]:
                    self.stdout.write(self.style.WARNING(f"    ⚠️  {b['route']}: {b['issue']}"))

                time.sleep(30)

        except KeyboardInterrupt:
            self.stdout.write('\n\n' + self.style.SUCCESS('  Watch mode stopped.\n'))

    def full_check(self, circulatory):
        """Run full circulation check with formatted output."""
        result = circulatory.circulate()

        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('  CIRCULATORY SYSTEM - Data Flow Health Check'))
        self.stdout.write(self.style.SUCCESS('  The Blood Flow of the AI Body'))
        self.stdout.write('=' * 70)

        # Overall status
        status_style = self._get_status_style(result['overall_status'])
        emoji = self._get_status_emoji(result['overall_status'])

        self.stdout.write(f"\n  {emoji} Overall Status: {status_style(result['overall_status'].upper())}")
        self.stdout.write(f"  Flow Score: {result['flow_score']:.1f}%")
        self.stdout.write(f"  Is Flowing: {'Yes' if result['is_flowing'] else 'No'}")
        self.stdout.write(f"  Check Duration: {result.get('check_duration_ms', 0)}ms")

        # Route summary
        self.stdout.write('\n  Route Summary:')
        self.stdout.write('  ' + '-' * 40)
        self.stdout.write(f"  Total Routes:   {result['routes_checked']}")
        self.stdout.write(f"  Healthy:        {result['routes_healthy']}")
        self.stdout.write(f"  Slow:           {result.get('routes_slow', 0)}")
        self.stdout.write(f"  Congested:      {result.get('routes_congested', 0)}")
        self.stdout.write(f"  Blocked:        {result.get('routes_blocked', 0)}")

        # Flow metrics
        flow = result.get('flow_metrics', {})
        self.stdout.write('\n  Flow Metrics:')
        self.stdout.write('  ' + '-' * 40)
        self.stdout.write(f"  Items in Transit:  {flow.get('total_items_in_transit', 0):,}")
        self.stdout.write(f"  Total Throughput:  {flow.get('total_throughput', 0):.2f} items/sec")
        self.stdout.write(f"  Avg Latency:       {flow.get('avg_latency_ms', 0):.0f}ms")
        self.stdout.write(f"  Max Latency:       {flow.get('max_latency_ms', 0):.0f}ms")

        # Route details
        routes = result.get('routes', {})
        if routes:
            self.stdout.write('\n  Route Details:')
            self.stdout.write('  ' + '-' * 60)
            for name, route_data in routes.items():
                r_emoji = self._get_status_emoji(route_data.get('status', 'unknown'))
                r_status = route_data.get('status', 'unknown').upper()
                depth = route_data.get('current_depth', 0)
                throughput = route_data.get('throughput', 0)
                latency = route_data.get('latency_ms', 0)
                self.stdout.write(
                    f"  {r_emoji} {name:<25} {r_status:<10} "
                    f"D:{depth:<6} T:{throughput:>6.1f}/s  L:{latency:>5.0f}ms"
                )

        # Bottlenecks
        bottlenecks = result.get('bottlenecks', [])
        if bottlenecks:
            self.stdout.write('\n  ' + self.style.WARNING('Bottlenecks Detected:'))
            self.stdout.write('  ' + '-' * 60)
            for b in bottlenecks:
                severity = b.get('severity', 'info')
                if severity == 'critical':
                    icon = '🚫'
                elif severity == 'warning':
                    icon = '⚠️'
                else:
                    icon = 'ℹ️'
                self.stdout.write(f"  {icon} {b['route']}: {b['issue']}")

        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(f"  Timestamp: {result['timestamp']}")
        self.stdout.write('=' * 70 + '\n')

    def _get_status_style(self, status):
        """Get Django style for status."""
        if status == 'flowing':
            return self.style.SUCCESS
        elif status == 'slow':
            return self.style.NOTICE
        elif status == 'congested':
            return self.style.WARNING
        elif status == 'blocked':
            return self.style.ERROR
        return lambda x: x

    def _get_status_emoji(self, status):
        """Get emoji for status."""
        return {
            'flowing': '🩸',
            'slow': '🐌',
            'congested': '⚠️',
            'blocked': '🚫',
        }.get(status, '❓')
