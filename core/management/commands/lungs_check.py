"""
Session 702: LUNGS Service Management Command

Usage:
    python manage.py lungs_check              # Run breathing check, show status
    python manage.py lungs_check --json       # Output as JSON
    python manage.py lungs_check --oxygen     # Show just oxygen levels
    python manage.py lungs_check --forecast   # Show spending forecast
    python manage.py lungs_check --watch      # Continuous monitoring (15m interval)
    python manage.py lungs_check --history    # Show breath cycle history
    python manage.py lungs_check --provider openai   # Check specific provider
    python manage.py lungs_check --budgets    # List all budgets
"""

import json
import time
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'LUNGS Service - Check resource and capacity status (the breathing of the AI body)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--json',
            action='store_true',
            help='Output in JSON format'
        )
        parser.add_argument(
            '--oxygen',
            action='store_true',
            help='Show only oxygen levels (budget remaining %)'
        )
        parser.add_argument(
            '--forecast',
            action='store_true',
            help='Show spending forecast'
        )
        parser.add_argument(
            '--watch',
            action='store_true',
            help='Continuous monitoring mode (runs every 15 minutes)'
        )
        parser.add_argument(
            '--history',
            action='store_true',
            help='Show recent breath cycle history'
        )
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Hours of history to show (default: 24)'
        )
        parser.add_argument(
            '--provider',
            type=str,
            help='Check specific provider (e.g., openai, anthropic)'
        )
        parser.add_argument(
            '--agent',
            type=str,
            help='Check specific agent (e.g., ResearchAgent)'
        )
        parser.add_argument(
            '--budgets',
            action='store_true',
            help='List all budget configurations'
        )
        parser.add_argument(
            '--velocity',
            action='store_true',
            help='Show spending velocity (cost/tokens per hour)'
        )

    def handle(self, *args, **options):
        from core.services.lungs import get_lungs_monitor

        if options['budgets']:
            self._list_budgets(options)
            return

        if options['history']:
            self._show_history(options)
            return

        if options['watch']:
            self._watch_mode(options)
            return

        if options['oxygen']:
            self._show_oxygen_levels(options)
            return

        if options['forecast']:
            self._show_forecast(options)
            return

        if options['velocity']:
            self._show_velocity(options)
            return

        if options['provider'] or options['agent']:
            self._check_specific(options)
        else:
            self._full_breathe(options)

    def _full_breathe(self, options):
        """Run full breathing check."""
        from core.services.lungs import get_lungs_monitor
        lungs = get_lungs_monitor()

        self.stdout.write(self.style.HTTP_INFO('\n' + '=' * 60))
        self.stdout.write(self.style.HTTP_INFO('  LUNGS SERVICE - Resource & Capacity Check'))
        self.stdout.write(self.style.HTTP_INFO('  The Breathing of the AI Body'))
        self.stdout.write(self.style.HTTP_INFO('=' * 60 + '\n'))

        result = lungs.breathe()

        if options['json']:
            self.stdout.write(json.dumps(result, indent=2, default=str))
            return

        # Overall status
        status = result['overall_status'].upper()
        oxygen = result['oxygen_level']

        if status == 'NORMAL':
            status_style = self.style.SUCCESS
        elif status == 'ELEVATED':
            status_style = self.style.WARNING
        else:
            status_style = self.style.ERROR

        self.stdout.write(f"  Overall Status: {status_style(f'{status} (O2: {oxygen:.1f}%)')}")
        self.stdout.write(f"  Respiratory Rate: {result['respiratory_rate']:.1f} calls/min")
        self.stdout.write(f"  Budgets Checked: {result['budgets_checked']}")
        self.stdout.write(f"  Can Breathe: {'Yes' if result['can_breathe'] else 'NO!'}")
        self.stdout.write(f"  Check Duration: {result['check_duration_ms']}ms")
        self.stdout.write('')

        # System budget
        system = result['breathing_metrics'].get('system', {})
        if system:
            self.stdout.write(self.style.HTTP_INFO('  System Budget:'))
            self.stdout.write(self.style.HTTP_INFO('  ' + '-' * 56))
            self._print_budget_status(system)

        # Provider budgets
        providers = result['breathing_metrics'].get('providers', {})
        if providers:
            self.stdout.write(self.style.HTTP_INFO('\n  Provider Budgets:'))
            self.stdout.write(self.style.HTTP_INFO('  ' + '-' * 56))
            for provider_name, provider_data in providers.items():
                self.stdout.write(f"  {provider_name.upper()}:")
                self._print_budget_status(provider_data, indent=4)

        # Alerts
        if result.get('alerts'):
            self.stdout.write(self.style.WARNING('\n  Alerts:'))
            for alert in result['alerts']:
                if alert['type'] == 'warning':
                    self.stdout.write(self.style.WARNING(f"    [WARN] {alert['message']}"))
                elif alert['type'] == 'critical':
                    self.stdout.write(self.style.ERROR(f"    [CRIT] {alert['message']}"))

        self.stdout.write(self.style.HTTP_INFO('\n' + '=' * 60 + '\n'))

    def _print_budget_status(self, data, indent=2):
        """Print budget status with formatting."""
        prefix = ' ' * indent
        oxygen = data.get('oxygen_level', 100)

        if oxygen >= 80:
            oxygen_style = self.style.SUCCESS
        elif oxygen >= 50:
            oxygen_style = self.style.WARNING
        else:
            oxygen_style = self.style.ERROR

        self.stdout.write(f"{prefix}  O2 Level: {oxygen_style(f'{oxygen:.1f}%')}")
        self.stdout.write(f"{prefix}  Status: {data.get('status', 'unknown').upper()}")
        self.stdout.write(f"{prefix}  Cost Today: ${data.get('cost_incurred', 0):.4f}")
        self.stdout.write(f"{prefix}  Tokens Used: {data.get('tokens_used', 0):,}")
        self.stdout.write(f"{prefix}  Calls: {data.get('call_count', 0)}")

        if data.get('limit'):
            self.stdout.write(f"{prefix}  Limit: ${data['limit']:.2f}")
        if data.get('remaining') is not None:
            self.stdout.write(f"{prefix}  Remaining: ${data['remaining']:.2f}")
        if data.get('projected_end') is not None:
            projected = data['projected_end']
            pace_indicator = self.style.ERROR(' (EXCEEDS!)') if data.get('on_pace_to_exceed') else ''
            self.stdout.write(f"{prefix}  Projected EOD: ${projected:.2f}{pace_indicator}")

    def _show_oxygen_levels(self, options):
        """Show only oxygen levels."""
        from core.models_lungs import RespiratoryStatus

        self.stdout.write(self.style.HTTP_INFO('\n  LUNGS Service - Oxygen Levels\n'))
        self.stdout.write(self.style.HTTP_INFO('  ' + '-' * 50))

        for status in RespiratoryStatus.objects.all().order_by('component'):
            oxygen = status.oxygen_level

            if oxygen >= 80:
                bar_style = self.style.SUCCESS
                indicator = '[OK]'
            elif oxygen >= 50:
                bar_style = self.style.WARNING
                indicator = '[--]'
            else:
                bar_style = self.style.ERROR
                indicator = '[!!]'

            # Create visual bar
            bar_len = int(oxygen / 5)
            bar = '█' * bar_len + '░' * (20 - bar_len)

            self.stdout.write(
                f"  {bar_style(indicator)} {status.display_name:20} {bar_style(bar)} {oxygen:5.1f}%"
            )

        self.stdout.write(self.style.HTTP_INFO('  ' + '-' * 50 + '\n'))

    def _show_forecast(self, options):
        """Show spending forecast."""
        from core.models_lungs import Budget
        from core.services.lungs import get_lungs_monitor

        lungs = get_lungs_monitor()

        self.stdout.write(self.style.HTTP_INFO('\n  LUNGS Service - Spending Forecast\n'))
        self.stdout.write(self.style.HTTP_INFO('  ' + '-' * 60))

        # Get velocity
        velocity = lungs.get_spending_velocity(hours=24)
        self.stdout.write(f"\n  Last 24h Velocity:")
        self.stdout.write(f"    Cost/Hour: ${velocity['cost_per_hour']:.4f}")
        self.stdout.write(f"    Tokens/Hour: {velocity['tokens_per_hour']:,.0f}")
        self.stdout.write(f"    Calls/Hour: {velocity['calls_per_hour']:.1f}")
        self.stdout.write(f"    Total Cost: ${velocity['total_cost']:.2f}")

        # Get forecasts for each budget
        self.stdout.write(f"\n  Budget Forecasts:")
        for budget in Budget.objects.filter(is_active=True):
            forecast = lungs.forecast_end_of_period(budget)

            if forecast['on_pace_to_exceed']:
                status_style = self.style.ERROR
                indicator = '[EXCEEDS]'
            else:
                status_style = self.style.SUCCESS
                indicator = '[OK]'

            self.stdout.write(f"\n    {budget.name}:")
            self.stdout.write(f"      Limit: ${float(budget.cost_limit or 0):.2f}")
            self.stdout.write(f"      Projected: ${forecast['projected_cost']:.2f}")
            self.stdout.write(f"      Status: {status_style(indicator)}")
            self.stdout.write(f"      Confidence: {forecast['confidence']*100:.0f}%")
            self.stdout.write(f"      Period Elapsed: {forecast['period_elapsed_percent']:.1f}%")

        self.stdout.write(self.style.HTTP_INFO('\n  ' + '-' * 60 + '\n'))

    def _show_velocity(self, options):
        """Show spending velocity."""
        from core.services.lungs import get_lungs_monitor

        lungs = get_lungs_monitor()

        if options['json']:
            velocity = lungs.get_spending_velocity(hours=24)
            self.stdout.write(json.dumps(velocity, indent=2))
            return

        self.stdout.write(self.style.HTTP_INFO('\n  LUNGS Service - Spending Velocity\n'))

        for hours in [1, 6, 24]:
            velocity = lungs.get_spending_velocity(hours=hours)
            self.stdout.write(f"  Last {hours}h:")
            self.stdout.write(f"    Total Cost: ${velocity['total_cost']:.4f}")
            self.stdout.write(f"    Cost/Hour: ${velocity['cost_per_hour']:.4f}")
            self.stdout.write(f"    Calls: {velocity['total_calls']}")
            self.stdout.write('')

    def _list_budgets(self, options):
        """List all budget configurations."""
        from core.models_lungs import Budget

        budgets = Budget.objects.all().order_by('scope', 'name')

        if options['json']:
            budget_list = [
                {
                    'id': str(b.id),
                    'name': b.name,
                    'scope': b.scope,
                    'scope_identifier': b.scope_identifier,
                    'period': b.period,
                    'cost_limit': float(b.cost_limit) if b.cost_limit else None,
                    'token_limit': b.token_limit,
                    'warning_threshold': b.warning_threshold,
                    'critical_threshold': b.critical_threshold,
                    'is_active': b.is_active,
                    'enforce_hard_limit': b.enforce_hard_limit,
                }
                for b in budgets
            ]
            self.stdout.write(json.dumps(budget_list, indent=2))
            return

        self.stdout.write(self.style.HTTP_INFO('\n  LUNGS Service - Budget Configurations\n'))
        self.stdout.write(self.style.HTTP_INFO('  ' + '-' * 70))

        for budget in budgets:
            active = self.style.SUCCESS('[ACTIVE]') if budget.is_active else self.style.WARNING('[INACTIVE]')
            hard = ' [HARD LIMIT]' if budget.enforce_hard_limit else ''

            self.stdout.write(f"\n  {budget.name} {active}{hard}")
            self.stdout.write(f"    Scope: {budget.scope}{'/' + budget.scope_identifier if budget.scope_identifier else ''}")
            self.stdout.write(f"    Period: {budget.period}")
            if budget.cost_limit:
                self.stdout.write(f"    Cost Limit: ${float(budget.cost_limit):.2f}")
            if budget.token_limit:
                self.stdout.write(f"    Token Limit: {budget.token_limit:,}")
            self.stdout.write(f"    Warning: {budget.warning_threshold*100:.0f}% | Critical: {budget.critical_threshold*100:.0f}%")

        self.stdout.write(self.style.HTTP_INFO('\n  ' + '-' * 70 + '\n'))

    def _check_specific(self, options):
        """Check specific provider or agent."""
        from core.services.lungs import get_lungs_monitor

        lungs = get_lungs_monitor()

        if options['provider']:
            scope = 'provider'
            identifier = options['provider']
        else:
            scope = 'agent'
            identifier = options['agent']

        oxygen = lungs.check_oxygen_level(scope, identifier)

        if options['json']:
            self.stdout.write(json.dumps({
                'scope': scope,
                'identifier': identifier,
                'oxygen_level': oxygen,
            }, indent=2))
            return

        self.stdout.write(self.style.HTTP_INFO(f'\n  Checking: {scope}/{identifier}\n'))

        if oxygen >= 80:
            status_style = self.style.SUCCESS
        elif oxygen >= 50:
            status_style = self.style.WARNING
        else:
            status_style = self.style.ERROR

        self.stdout.write(f"  Oxygen Level: {status_style(f'{oxygen:.1f}%')}")
        self.stdout.write('')

    def _show_history(self, options):
        """Show breath cycle history."""
        from core.services.lungs import get_lungs_monitor

        hours = options.get('hours', 24)
        lungs = get_lungs_monitor()
        history = lungs.get_history(hours=hours, limit=50)

        if options['json']:
            self.stdout.write(json.dumps(history, indent=2))
            return

        self.stdout.write(self.style.HTTP_INFO(f'\n  LUNGS Service History (last {hours} hours)\n'))
        self.stdout.write(self.style.HTTP_INFO('  ' + '-' * 80))

        if not history:
            self.stdout.write('  No breath cycle records found.')
            return

        for record in history:
            timestamp = record['recorded_at'][:19]
            oxygen = record['oxygen_level']
            cost = record['cost_incurred']

            if oxygen >= 80:
                status_style = self.style.SUCCESS
            elif oxygen >= 50:
                status_style = self.style.WARNING
            else:
                status_style = self.style.ERROR

            self.stdout.write(
                f"  {timestamp} | {record['scope']:25} | "
                f"O2: {status_style(f'{oxygen:5.1f}%')} | "
                f"${cost:.4f} | {record['call_count']} calls"
            )

        self.stdout.write(self.style.HTTP_INFO('  ' + '-' * 80 + '\n'))

    def _watch_mode(self, options):
        """Continuous monitoring mode."""
        from core.services.lungs import get_lungs_monitor

        self.stdout.write(self.style.HTTP_INFO('\n  LUNGS Service Watch Mode'))
        self.stdout.write(self.style.HTTP_INFO('  Press Ctrl+C to stop\n'))

        lungs = get_lungs_monitor()

        try:
            while True:
                result = lungs.breathe()

                status = result['overall_status'].upper()
                oxygen = result['oxygen_level']
                timestamp = result['timestamp'][:19]

                if status == 'NORMAL':
                    status_str = self.style.SUCCESS(f'{status} (O2: {oxygen:.1f}%)')
                elif status == 'ELEVATED':
                    status_str = self.style.WARNING(f'{status} (O2: {oxygen:.1f}%)')
                else:
                    status_str = self.style.ERROR(f'{status} (O2: {oxygen:.1f}%)')

                # Show provider summary
                providers = result['breathing_metrics'].get('providers', {})
                provider_summary = ' '.join(
                    self.style.SUCCESS(f'{p[:3].upper()}') if data.get('oxygen_level', 100) >= 80
                    else self.style.WARNING(f'{p[:3].upper()}') if data.get('oxygen_level', 100) >= 50
                    else self.style.ERROR(f'{p[:3].upper()}')
                    for p, data in providers.items()
                )

                self.stdout.write(f"  [{timestamp}] {status_str} | {provider_summary}")

                time.sleep(60 * 15)  # 15 minutes

        except KeyboardInterrupt:
            self.stdout.write(self.style.HTTP_INFO('\n  Watch mode stopped.\n'))
