"""
Session 701: HEART Service Management Command

Usage:
    python manage.py heart_check              # Run pulse, show status
    python manage.py heart_check --json       # Output as JSON
    python manage.py heart_check --watch      # Continuous monitoring (60s interval)
    python manage.py heart_check brain        # Check specific component
    python manage.py heart_check --history    # Show recent heartbeat history
"""

import json
import time
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'HEART Service - Check system health (the central heartbeat of the AI body)'

    def add_arguments(self, parser):
        parser.add_argument(
            'component',
            nargs='?',
            type=str,
            help='Specific component to check: brain, nervous_system, organs, sensory, skin, memory'
        )
        parser.add_argument(
            '--json',
            action='store_true',
            help='Output in JSON format'
        )
        parser.add_argument(
            '--watch',
            action='store_true',
            help='Continuous monitoring mode (runs every 60 seconds)'
        )
        parser.add_argument(
            '--history',
            action='store_true',
            help='Show recent heartbeat history'
        )
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Hours of history to show (default: 24)'
        )

    def handle(self, *args, **options):
        from core.services.heart import get_heart_monitor

        if options['history']:
            self._show_history(options)
            return

        if options['watch']:
            self._watch_mode(options)
            return

        component = options.get('component')
        if component:
            self._check_component(component, options)
        else:
            self._full_pulse(options)

    def _full_pulse(self, options):
        """Run full system pulse check."""
        from core.services.heart import get_heart_monitor
        heart = get_heart_monitor()

        self.stdout.write(self.style.HTTP_INFO('\n' + '=' * 60))
        self.stdout.write(self.style.HTTP_INFO('  HEART SERVICE - System Health Check'))
        self.stdout.write(self.style.HTTP_INFO('  The Central Heartbeat of the AI Body'))
        self.stdout.write(self.style.HTTP_INFO('=' * 60 + '\n'))

        pulse = heart.pulse()

        if options['json']:
            self.stdout.write(json.dumps(pulse, indent=2))
            return

        # Overall status
        status = pulse['overall_status'].upper()
        score = pulse['health_score']

        if status == 'HEALTHY':
            status_style = self.style.SUCCESS
        elif status == 'DEGRADED':
            status_style = self.style.WARNING
        else:
            status_style = self.style.ERROR

        self.stdout.write(f"  Overall Status: {status_style(f'{status} ({score:.1f}%)')}")
        self.stdout.write(f"  Components: {pulse['components_healthy']}/{pulse['components_checked']} healthy")
        self.stdout.write(f"  Check Duration: {pulse['check_duration_ms']}ms")
        self.stdout.write('')

        # Component details
        self.stdout.write(self.style.HTTP_INFO('  Components:'))
        self.stdout.write(self.style.HTTP_INFO('  ' + '-' * 56))

        for comp_id, comp in pulse['components'].items():
            comp_status = comp.get('status', 'unknown').upper()
            comp_name = comp.get('name', comp_id)
            response_ms = comp.get('response_time_ms', 0)

            if comp_status == 'HEALTHY':
                status_icon = self.style.SUCCESS('  [OK]')
            elif comp_status == 'DEGRADED':
                status_icon = self.style.WARNING('  [--]')
            else:
                status_icon = self.style.ERROR('  [!!]')

            self.stdout.write(f"{status_icon} {comp_name}")
            self.stdout.write(f"       Status: {comp_status} | Response: {response_ms}ms")

            # Show details
            details = comp.get('details', {})
            if details:
                detail_str = ', '.join(f"{k}: {v}" for k, v in details.items())
                self.stdout.write(f"       {detail_str}")

            # Show error if any
            if comp.get('error'):
                self.stdout.write(self.style.ERROR(f"       Error: {comp['error']}"))

            self.stdout.write('')

        self.stdout.write(self.style.HTTP_INFO('=' * 60 + '\n'))

        # Record the heartbeat
        heart.record_heartbeat(pulse)
        heart.alert_if_critical(pulse)

    def _check_component(self, component, options):
        """Check a specific component."""
        from core.services.heart import get_heart_monitor

        valid_components = ['brain', 'nervous_system', 'organs', 'sensory', 'skin', 'memory']

        if component not in valid_components:
            self.stderr.write(self.style.ERROR(
                f"Invalid component: {component}\n"
                f"Valid components: {', '.join(valid_components)}"
            ))
            return

        heart = get_heart_monitor()

        # Get the check method
        check_method = getattr(heart, f'check_{component}', None)
        if not check_method:
            self.stderr.write(self.style.ERROR(f"No check method for: {component}"))
            return

        self.stdout.write(self.style.HTTP_INFO(f'\n  Checking: {component}\n'))

        result = check_method()

        if options['json']:
            self.stdout.write(json.dumps(result, indent=2))
            return

        status = result.get('status', 'unknown').upper()
        if status == 'HEALTHY':
            status_style = self.style.SUCCESS
        elif status == 'DEGRADED':
            status_style = self.style.WARNING
        else:
            status_style = self.style.ERROR

        self.stdout.write(f"  Component: {result.get('name', component)}")
        self.stdout.write(f"  Status: {status_style(status)}")
        self.stdout.write(f"  Response Time: {result.get('response_time_ms', 0)}ms")

        if result.get('details'):
            self.stdout.write('\n  Details:')
            for key, value in result['details'].items():
                self.stdout.write(f"    {key}: {value}")

        if result.get('error'):
            self.stdout.write(self.style.ERROR(f"\n  Error: {result['error']}"))

        self.stdout.write('')

    def _watch_mode(self, options):
        """Continuous monitoring mode."""
        from core.services.heart import get_heart_monitor

        self.stdout.write(self.style.HTTP_INFO('\n  HEART Service Watch Mode'))
        self.stdout.write(self.style.HTTP_INFO('  Press Ctrl+C to stop\n'))

        heart = get_heart_monitor()

        try:
            while True:
                pulse = heart.pulse()

                status = pulse['overall_status'].upper()
                score = pulse['health_score']
                timestamp = pulse['timestamp'][:19]  # Trim to seconds

                if status == 'HEALTHY':
                    status_str = self.style.SUCCESS(f'{status} ({score:.1f}%)')
                elif status == 'DEGRADED':
                    status_str = self.style.WARNING(f'{status} ({score:.1f}%)')
                else:
                    status_str = self.style.ERROR(f'{status} ({score:.1f}%)')

                components = pulse['components']
                comp_summary = ' '.join(
                    self.style.SUCCESS(f'{c[:2].upper()}') if comp.get('is_healthy')
                    else self.style.ERROR(f'{c[:2].upper()}')
                    for c, comp in components.items()
                )

                self.stdout.write(f"  [{timestamp}] {status_str} | {comp_summary}")

                # Record and alert
                heart.record_heartbeat(pulse)
                heart.alert_if_critical(pulse)

                time.sleep(60)

        except KeyboardInterrupt:
            self.stdout.write(self.style.HTTP_INFO('\n  Watch mode stopped.\n'))

    def _show_history(self, options):
        """Show recent heartbeat history."""
        from core.services.heart import get_heart_monitor

        hours = options.get('hours', 24)
        heart = get_heart_monitor()
        history = heart.get_history(hours=hours, limit=50)

        if options['json']:
            self.stdout.write(json.dumps(history, indent=2))
            return

        self.stdout.write(self.style.HTTP_INFO(f'\n  HEART Service History (last {hours} hours)\n'))
        self.stdout.write(self.style.HTTP_INFO('  ' + '-' * 70))

        if not history:
            self.stdout.write('  No heartbeat records found.')
            return

        for hb in history:
            timestamp = hb['timestamp'][:19]
            status = hb['overall_status'].upper()
            score = hb['health_score']
            healthy = hb['components_healthy']
            checked = hb['components_checked']

            if status == 'HEALTHY':
                status_str = self.style.SUCCESS(f'{status:8}')
            elif status == 'DEGRADED':
                status_str = self.style.WARNING(f'{status:8}')
            else:
                status_str = self.style.ERROR(f'{status:8}')

            self.stdout.write(
                f"  {timestamp} | {status_str} | {score:5.1f}% | {healthy}/{checked} components"
            )

        self.stdout.write(self.style.HTTP_INFO('  ' + '-' * 70 + '\n'))
