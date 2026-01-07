"""
Session 705: IMMUNE Check Management Command

CLI command for checking immune system (security & threat detection) health.
The defense layer of the AI body - detects and responds to threats.

Usage:
    python manage.py immune_check                    # Full immune scan
    python manage.py immune_check --json             # JSON output
    python manage.py immune_check --patterns         # List all threat patterns
    python manage.py immune_check --threats          # Show recent threats
    python manage.py immune_check --quarantine       # Show quarantine list
    python manage.py immune_check --watch            # Continuous monitoring (45s)
    python manage.py immune_check --categories       # Show category breakdown

Output includes:
    - Overall immune status (healthy/alert/fighting/overwhelmed/compromised)
    - Health score (0-100%)
    - Threat level (none/low/elevated/high/severe)
    - Active threats and 24h statistics
    - Quarantine counts
    - Integration status with SPINE/HEART
"""

import json
import time
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone


class Command(BaseCommand):
    help = 'Check IMMUNE (security & threat detection) system health'

    def add_arguments(self, parser):
        parser.add_argument(
            '--json',
            action='store_true',
            help='Output results as JSON'
        )
        parser.add_argument(
            '--patterns',
            action='store_true',
            help='List all threat patterns'
        )
        parser.add_argument(
            '--threats',
            action='store_true',
            help='Show recent threat events'
        )
        parser.add_argument(
            '--quarantine',
            action='store_true',
            help='Show quarantine list'
        )
        parser.add_argument(
            '--categories',
            action='store_true',
            help='Show category breakdown'
        )
        parser.add_argument(
            '--watch',
            action='store_true',
            help='Continuous monitoring mode (45s interval)'
        )
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Lookback period in hours for threats (default: 24)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force fresh scan (ignore cache)'
        )

    def handle(self, *args, **options):
        from core.services.immune import get_immune_system

        immune = get_immune_system()

        if options['patterns']:
            self._show_patterns(immune, options['json'])
        elif options['threats']:
            self._show_threats(immune, options['hours'], options['json'])
        elif options['quarantine']:
            self._show_quarantine(immune, options['json'])
        elif options['categories']:
            self._show_categories(immune, options['json'])
        elif options['watch']:
            self._watch_mode(immune, options['json'])
        else:
            self._full_scan(immune, options['force'], options['json'])

    def _full_scan(self, immune, force: bool, as_json: bool):
        """Run full immune system scan."""
        result = immune.scan(force=force)

        if as_json:
            self.stdout.write(json.dumps(result, indent=2, default=str))
            return

        # Header
        self.stdout.write('')
        self.stdout.write('=' * 60)
        self.stdout.write('  IMMUNE SYSTEM - Security & Threat Detection')
        self.stdout.write('  The Defense Layer of the AI Body')
        self.stdout.write('=' * 60)

        # Overall status
        status = result['overall_status']
        score = result['health_score']
        threat_level = result.get('threat_level', 'none')
        emoji = self._get_status_emoji(status)
        status_text = f"{status.upper():<12}"
        status_style = self._get_status_style(status)
        threat_style = self._get_threat_style(threat_level)

        self.stdout.write(f'  Overall Status: {status_style(status_text)} {emoji}')
        self.stdout.write(f'  Health Score: {score:.1f}%')
        self.stdout.write(f'  Threat Level: {threat_style(threat_level.upper())}')
        self.stdout.write(f'  Is Healthy: {"Yes" if result.get("is_healthy", True) else "No"}')
        self.stdout.write(f'  Scan Duration: {result.get("check_duration_ms", 0):.0f}ms')
        self.stdout.write('')

        # Threat statistics
        self.stdout.write('  Threat Statistics (24h):')
        self.stdout.write('  ' + '-' * 40)
        active = result.get('active_threats', 0)
        if active > 0:
            self.stdout.write(self.style.ERROR(f'  Active Threats:    {active}'))
        else:
            self.stdout.write(f'  Active Threats:    {active}')

        detected = result.get('threats_detected_24h', 0)
        if detected > 0:
            self.stdout.write(self.style.WARNING(f'  Detected (24h):    {detected}'))
        else:
            self.stdout.write(f'  Detected (24h):    {detected}')

        blocked = result.get('threats_blocked_24h', 0)
        if blocked > 0:
            self.stdout.write(self.style.SUCCESS(f'  Blocked (24h):     {blocked}'))
        else:
            self.stdout.write(f'  Blocked (24h):     {blocked}')

        self.stdout.write(f'  False Positives:   {result.get("false_positives_24h", 0)}')
        self.stdout.write('')

        # Quarantine status
        self.stdout.write('  Quarantine Status:')
        self.stdout.write('  ' + '-' * 40)
        total_q = result.get('total_quarantined', 0)
        if total_q > 0:
            self.stdout.write(self.style.WARNING(f'  Total Quarantined: {total_q}'))
        else:
            self.stdout.write(f'  Total Quarantined: {total_q}')
        self.stdout.write(f'  Quarantined IPs:   {result.get("quarantined_ips", 0)}')
        self.stdout.write(f'  Quarantined Users: {result.get("quarantined_users", 0)}')
        self.stdout.write('')

        # Pattern statistics
        self.stdout.write('  Pattern Statistics:')
        self.stdout.write('  ' + '-' * 40)
        self.stdout.write(f'  Active Patterns:   {result.get("active_patterns", 0)}')
        self.stdout.write(f'  Triggered (24h):   {result.get("patterns_triggered_24h", 0)}')
        self.stdout.write('')

        # Response metrics
        self.stdout.write('  Response Metrics:')
        self.stdout.write('  ' + '-' * 40)
        self.stdout.write(f'  Auto Responses:    {result.get("auto_responses_24h", 0)}')
        self.stdout.write(f'  Manual Responses:  {result.get("manual_responses_24h", 0)}')
        self.stdout.write(f'  Avg Response Time: {result.get("avg_response_time_ms", 0):.1f}ms')
        self.stdout.write('')

        # Category breakdown (if present)
        threats_by_cat = result.get('threats_by_category', {})
        if threats_by_cat:
            self.stdout.write('  Threats by Category:')
            self.stdout.write('  ' + '-' * 40)
            for category, count in sorted(threats_by_cat.items(), key=lambda x: x[1], reverse=True):
                if count > 0:
                    self.stdout.write(self.style.WARNING(f'  {category:<20} {count}'))
            self.stdout.write('')

        # Integration status
        self.stdout.write('  Integration Status:')
        self.stdout.write('  ' + '-' * 40)
        spine_status = "Connected" if result.get('spine_connected', False) else "Disconnected"
        heart_status = "Connected" if result.get('heart_connected', False) else "Disconnected"
        spine_style = self.style.SUCCESS if result.get('spine_connected') else self.style.WARNING
        heart_style = self.style.SUCCESS if result.get('heart_connected') else self.style.WARNING
        self.stdout.write(f'  SPINE:  {spine_style(spine_status)}')
        self.stdout.write(f'  HEART:  {heart_style(heart_status)}')

        self.stdout.write('=' * 60)
        self.stdout.write('')

    def _show_patterns(self, immune, as_json: bool):
        """List all threat patterns."""
        patterns = immune.get_patterns(active_only=False)

        if as_json:
            self.stdout.write(json.dumps(patterns, indent=2))
            return

        self.stdout.write('')
        self.stdout.write('=' * 90)
        self.stdout.write('  IMMUNE Threat Patterns')
        self.stdout.write('=' * 90)
        self.stdout.write('')
        self.stdout.write(f'  {"Name":<30} {"Category":<15} {"Severity":<10} {"Response":<12} {"Detections":<12}')
        self.stdout.write('  ' + '-' * 86)

        for p in patterns:
            severity = p.get('severity', 'medium')
            severity_style = self._get_severity_style(severity)
            detections = p.get('total_detections', 0)

            self.stdout.write(
                f'  {p["name"]:<30} {p["category"]:<15} {severity_style(severity):<10} '
                f'{p.get("response_action", "log"):<12} {detections:<12}'
            )

        self.stdout.write('')
        self.stdout.write(f'  Total: {len(patterns)} patterns')
        self.stdout.write('')

    def _show_threats(self, immune, hours: int, as_json: bool):
        """Show recent threat events."""
        threats = immune.get_recent_threats(hours=hours)

        if as_json:
            self.stdout.write(json.dumps(threats, indent=2, default=str))
            return

        self.stdout.write('')
        self.stdout.write('=' * 100)
        self.stdout.write(f'  Recent Threat Events (Last {hours} hours)')
        self.stdout.write('=' * 100)
        self.stdout.write('')

        if not threats:
            self.stdout.write('  No threats detected in this period.')
            self.stdout.write('')
            return

        self.stdout.write(f'  {"Timestamp":<20} {"Category":<15} {"Severity":<10} {"Source IP":<16} {"Status":<12}')
        self.stdout.write('  ' + '-' * 96)

        for t in threats[:50]:  # Limit to 50
            ts = str(t.get('detected_at', ''))[:19] if t.get('detected_at') else 'N/A'
            category = t.get('category', 'N/A')
            severity = t.get('severity', 'medium')
            source_ip = t.get('source_ip', 'N/A')[:16] if t.get('source_ip') else 'N/A'
            status = t.get('status', 'detected')

            severity_style = self._get_severity_style(severity)
            self.stdout.write(
                f'  {ts:<20} {category:<15} {severity_style(severity):<10} {source_ip:<16} {status:<12}'
            )

        self.stdout.write('')
        self.stdout.write(f'  Showing {min(50, len(threats))} of {len(threats)} threats')
        self.stdout.write('')

    def _show_quarantine(self, immune, as_json: bool):
        """Show quarantine list."""
        quarantine = immune.get_quarantine_list()

        if as_json:
            self.stdout.write(json.dumps(quarantine, indent=2, default=str))
            return

        self.stdout.write('')
        self.stdout.write('=' * 90)
        self.stdout.write('  Quarantine List')
        self.stdout.write('=' * 90)
        self.stdout.write('')

        if not quarantine:
            self.stdout.write('  No entities currently quarantined.')
            self.stdout.write('')
            return

        self.stdout.write(f'  {"Type":<12} {"Value":<25} {"Reason":<15} {"Permanent":<10} {"Blocked":<10}')
        self.stdout.write('  ' + '-' * 86)

        for q in quarantine:
            entity_type = q.get('entity_type', 'N/A')
            value = str(q.get('entity_value', 'N/A'))[:25]
            reason = q.get('reason', 'N/A')
            permanent = "Yes" if q.get('is_permanent') else "No"
            blocked = q.get('blocked_requests', 0)

            self.stdout.write(
                f'  {entity_type:<12} {value:<25} {reason:<15} {permanent:<10} {blocked:<10}'
            )

        self.stdout.write('')
        self.stdout.write(f'  Total: {len(quarantine)} quarantined entities')
        self.stdout.write('')

    def _show_categories(self, immune, as_json: bool):
        """Show category breakdown."""
        vitals = immune.get_vitals()
        threats_by_cat = vitals.get('threats_by_category', {})
        threats_by_sev = vitals.get('threats_by_severity', {})

        if as_json:
            self.stdout.write(json.dumps({
                'threats_by_category': threats_by_cat,
                'threats_by_severity': threats_by_sev
            }, indent=2))
            return

        self.stdout.write('')
        self.stdout.write('=' * 60)
        self.stdout.write('  IMMUNE Category Breakdown')
        self.stdout.write('=' * 60)
        self.stdout.write('')

        self.stdout.write('  Threats by Category:')
        self.stdout.write('  ' + '-' * 40)
        if threats_by_cat:
            for category, count in sorted(threats_by_cat.items(), key=lambda x: x[1], reverse=True):
                self.stdout.write(f'  {category:<25} {count}')
        else:
            self.stdout.write('  No threats recorded by category.')
        self.stdout.write('')

        self.stdout.write('  Threats by Severity:')
        self.stdout.write('  ' + '-' * 40)
        if threats_by_sev:
            severity_order = ['critical', 'high', 'medium', 'low', 'info']
            for severity in severity_order:
                if severity in threats_by_sev:
                    count = threats_by_sev[severity]
                    style = self._get_severity_style(severity)
                    self.stdout.write(f'  {style(severity):<25} {count}')
        else:
            self.stdout.write('  No threats recorded by severity.')
        self.stdout.write('')

    def _watch_mode(self, immune, as_json: bool):
        """Continuous monitoring mode."""
        self.stdout.write('')
        self.stdout.write('IMMUNE Watch Mode - Press Ctrl+C to stop')
        self.stdout.write('Scanning every 45 seconds...')
        self.stdout.write('')

        try:
            while True:
                result = immune.scan(force=True)

                if as_json:
                    self.stdout.write(json.dumps({
                        'timestamp': result['timestamp'],
                        'status': result['overall_status'],
                        'health_score': result['health_score'],
                        'threat_level': result.get('threat_level', 'none'),
                        'active_threats': result.get('active_threats', 0),
                    }))
                else:
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    status = result['overall_status']
                    score = result['health_score']
                    threat_level = result.get('threat_level', 'none')
                    active = result.get('active_threats', 0)
                    emoji = self._get_status_emoji(status)

                    style = self._get_status_style(status)
                    threat_style = self._get_threat_style(threat_level)

                    self.stdout.write(
                        f'[{timestamp}] {emoji} {style(status.upper())} '
                        f'({score:.1f}%) - Threat: {threat_style(threat_level.upper())}'
                    )

                    if active > 0:
                        self.stdout.write(self.style.ERROR(
                            f'           {active} ACTIVE THREATS!'
                        ))

                time.sleep(45)

        except KeyboardInterrupt:
            self.stdout.write('')
            self.stdout.write('Watch mode stopped.')
            self.stdout.write('')

    def _get_status_emoji(self, status: str) -> str:
        """Get emoji for status."""
        return {
            'healthy': '🛡️',      # Shield - protected
            'alert': '⚠️',        # Warning
            'fighting': '⚔️',     # Sword - active defense
            'overwhelmed': '🔥',  # Fire - under attack
            'compromised': '💀',  # Skull - critical
        }.get(status, '❓')

    def _get_status_style(self, status: str):
        """Get style function for status."""
        if status == 'healthy':
            return self.style.SUCCESS
        elif status in ('alert', 'fighting'):
            return self.style.WARNING
        elif status in ('overwhelmed', 'compromised'):
            return self.style.ERROR
        return self.style.HTTP_INFO

    def _get_threat_style(self, threat_level: str):
        """Get style function for threat level."""
        if threat_level == 'none':
            return self.style.SUCCESS
        elif threat_level == 'low':
            return self.style.HTTP_INFO
        elif threat_level == 'elevated':
            return self.style.WARNING
        elif threat_level in ('high', 'severe'):
            return self.style.ERROR
        return self.style.HTTP_INFO

    def _get_severity_style(self, severity: str):
        """Get style function for severity."""
        if severity == 'critical':
            return self.style.ERROR
        elif severity == 'high':
            return self.style.ERROR
        elif severity == 'medium':
            return self.style.WARNING
        elif severity == 'low':
            return self.style.HTTP_INFO
        return self.style.HTTP_INFO
