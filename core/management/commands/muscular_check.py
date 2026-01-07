"""
Session 707: MUSCULAR Check Management Command

CLI command for checking muscular system (agent work execution) health.
The work execution layer of the AI body - monitors agent strength and performance.

Usage:
    python manage.py muscular_check                    # Full muscular check
    python manage.py muscular_check --json             # JSON output
    python manage.py muscular_check --groups           # List all muscle groups
    python manage.py muscular_check --weak             # Show weak muscles only
    python manage.py muscular_check --overworked       # Show overworked muscles
    python manage.py muscular_check --watch            # Continuous monitoring (90s)
    python manage.py muscular_check --history          # Show muscular pulse history
    python manage.py muscular_check --group creation   # Check specific group

Output includes:
    - Overall muscular status (strong/fit/fatigued/strained/paralyzed)
    - Strength score (0-100%)
    - Per-group breakdown
    - Weak and overworked agent detection
"""

import json
import time
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone


class Command(BaseCommand):
    help = 'Check MUSCULAR (agent work execution) system health'

    def add_arguments(self, parser):
        parser.add_argument(
            '--json',
            action='store_true',
            help='Output results as JSON'
        )
        parser.add_argument(
            '--groups',
            action='store_true',
            help='List all muscle groups'
        )
        parser.add_argument(
            '--weak',
            action='store_true',
            help='Show weak muscles (low success rate)'
        )
        parser.add_argument(
            '--overworked',
            action='store_true',
            help='Show overworked muscles (high execution count)'
        )
        parser.add_argument(
            '--history',
            action='store_true',
            help='Show muscular pulse history'
        )
        parser.add_argument(
            '--group',
            type=str,
            help='Check specific muscle group (e.g., creation, research, development)'
        )
        parser.add_argument(
            '--watch',
            action='store_true',
            help='Continuous monitoring mode (90s interval)'
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
        from core.services.muscular import get_muscular_system

        muscular = get_muscular_system()

        if options['groups']:
            self._show_groups(muscular, options['json'])
        elif options['weak']:
            self._show_weak(muscular, options['json'])
        elif options['overworked']:
            self._show_overworked(muscular, options['json'])
        elif options['history']:
            self._show_history(muscular, options['hours'], options['json'])
        elif options['group']:
            self._show_group(muscular, options['group'], options['json'])
        elif options['watch']:
            self._watch_mode(muscular, options['json'])
        else:
            self._full_check(muscular, options['force'], options['json'])

    def _full_check(self, muscular, force: bool, as_json: bool):
        """Run full muscular check."""
        result = muscular.flex(force=force)

        if as_json:
            self.stdout.write(json.dumps(result, indent=2, default=str))
            return

        # Header
        self.stdout.write('')
        self.stdout.write('=' * 60)
        self.stdout.write('  MUSCULAR SYSTEM - Agent Work Execution')
        self.stdout.write('  The Work Execution Layer of the AI Body')
        self.stdout.write('=' * 60)

        # Overall status
        status = result['overall_status']
        score = result['strength_score']
        emoji = self._get_status_emoji(status)
        status_text = f"{status.upper():<12}"
        status_style = self._get_status_style(status)

        self.stdout.write(f'  Overall Status: {status_style(status_text)} {emoji}')
        self.stdout.write(f'  Strength Score: {score:.1f}%')
        self.stdout.write(f'  Is Strong: {"Yes" if result.get("is_strong", True) else "No"}')
        self.stdout.write(f'  Check Duration: {result.get("check_duration_ms", 0):.0f}ms')
        self.stdout.write('')

        # Execution summary
        exec_summary = result.get('execution_summary', {})
        self.stdout.write('  EXECUTION SUMMARY (24h):')
        self.stdout.write('  ' + '-' * 40)
        self.stdout.write(f'  Total Executions:    {exec_summary.get("total_24h", 0):,}')
        self.stdout.write(f'  Successful:          {exec_summary.get("successful_24h", 0):,}')
        self.stdout.write(f'  Failed:              {exec_summary.get("failed_24h", 0):,}')
        success_rate = exec_summary.get('success_rate', 100)
        if success_rate < 80:
            self.stdout.write(self.style.WARNING(f'  Success Rate:        {success_rate:.1f}%'))
        else:
            self.stdout.write(f'  Success Rate:        {success_rate:.1f}%')
        self.stdout.write(f'  Avg Execution Time:  {exec_summary.get("avg_execution_time_ms", 0):.0f}ms')
        self.stdout.write(f'  Total Tokens:        {exec_summary.get("total_tokens_24h", 0):,}')
        self.stdout.write(f'  Total Cost:          ${exec_summary.get("total_cost_24h", 0):.4f}')
        self.stdout.write('')

        # Agent summary
        agent_summary = result.get('agent_summary', {})
        self.stdout.write('  AGENT SUMMARY:')
        self.stdout.write('  ' + '-' * 40)
        self.stdout.write(f'  Total Agents:        {agent_summary.get("total_agents", 0)}')
        self.stdout.write(f'  Active Agents:       {agent_summary.get("active_agents", 0)}')
        self.stdout.write(f'  Idle Agents:         {agent_summary.get("idle_agents", 0)}')
        fatigued = agent_summary.get('fatigued_agents', 0)
        if fatigued > 0:
            self.stdout.write(self.style.WARNING(f'  Fatigued Agents:     {fatigued}'))
        else:
            self.stdout.write(f'  Fatigued Agents:     {fatigued}')
        strained = agent_summary.get('strained_agents', 0)
        if strained > 0:
            self.stdout.write(self.style.ERROR(f'  Strained Agents:     {strained}'))
        else:
            self.stdout.write(f'  Strained Agents:     {strained}')
        self.stdout.write('')

        # Groups summary
        groups_summary = result.get('groups_summary', {})
        self.stdout.write('  MUSCLE GROUPS:')
        self.stdout.write('  ' + '-' * 40)
        self.stdout.write(f'  Groups Checked:      {groups_summary.get("checked", 0)}')
        self.stdout.write(f'  Strong:              {groups_summary.get("strong", 0)}')
        self.stdout.write(f'  Fit:                 {groups_summary.get("fit", 0)}')
        self.stdout.write(f'  Fatigued:            {groups_summary.get("fatigued", 0)}')
        self.stdout.write(f'  Strained:            {groups_summary.get("strained", 0)}')
        self.stdout.write(f'  Paralyzed:           {groups_summary.get("paralyzed", 0)}')
        self.stdout.write('')

        # Per-group breakdown
        groups = result.get('groups', {})
        if groups:
            self.stdout.write('  GROUP BREAKDOWN:')
            self.stdout.write('  ' + '-' * 40)
            for category, data in groups.items():
                grp_status = data.get('status', 'unknown')
                grp_style = self._get_status_style(grp_status)
                grp_emoji = self._get_status_emoji(grp_status)
                status_display = grp_status.upper().ljust(10)
                self.stdout.write(
                    f'  {category:<15} {grp_style(status_display)} {grp_emoji} '
                    f'({data.get("executions_24h", 0):,} exec, {data.get("success_rate", 0):.1f}%)'
                )
            self.stdout.write('')

        # Weak muscles
        weak = result.get('weak_muscles', [])
        if weak:
            self.stdout.write('  WEAK MUSCLES DETECTED:')
            self.stdout.write('  ' + '-' * 40)
            for w in weak[:5]:
                self.stdout.write(self.style.WARNING(
                    f'  [{w.get("severity", "warning").upper()}] {w.get("agent", "?")} - '
                    f'{w.get("success_rate", 0):.1f}% success rate'
                ))
            if len(weak) > 5:
                self.stdout.write(f'  ... and {len(weak) - 5} more')
            self.stdout.write('')

        # Overworked muscles
        overworked = result.get('overworked_muscles', [])
        if overworked:
            self.stdout.write('  OVERWORKED MUSCLES DETECTED:')
            self.stdout.write('  ' + '-' * 40)
            for o in overworked[:5]:
                self.stdout.write(self.style.WARNING(
                    f'  [{o.get("severity", "warning").upper()}] {o.get("agent", "?")} - '
                    f'{o.get("executions_24h", 0):,} executions'
                ))
            if len(overworked) > 5:
                self.stdout.write(f'  ... and {len(overworked) - 5} more')
            self.stdout.write('')

        # Footer
        self.stdout.write('=' * 60)
        self.stdout.write('')

    def _show_groups(self, muscular, as_json: bool):
        """Show all muscle groups."""
        groups = muscular.get_groups()

        if as_json:
            self.stdout.write(json.dumps(groups, indent=2, default=str))
            return

        self.stdout.write('')
        self.stdout.write('=' * 60)
        self.stdout.write('  MUSCLE GROUPS')
        self.stdout.write('=' * 60)
        self.stdout.write('')

        for group in groups:
            critical_tag = ' [CRITICAL]' if group.get('is_critical') else ''
            self.stdout.write(f'  {group.get("display_name", group.get("name"))}{critical_tag}')
            self.stdout.write(f'    Category: {group.get("category")}')
            self.stdout.write(f'    Agents ({group.get("agent_count", 0)}): {", ".join(group.get("agents", [])[:5])}...')
            self.stdout.write(f'    Target Success Rate: {group.get("target_success_rate", 90)}%')
            self.stdout.write(f'    Max Daily Executions: {group.get("max_daily_executions", 1000)}')
            self.stdout.write('')

        self.stdout.write(f'  Total: {len(groups)} muscle groups')
        self.stdout.write('')

    def _show_weak(self, muscular, as_json: bool):
        """Show weak muscles."""
        weak = muscular.detect_weak_muscles()

        if as_json:
            self.stdout.write(json.dumps(weak, indent=2, default=str))
            return

        self.stdout.write('')
        self.stdout.write('=' * 60)
        self.stdout.write('  WEAK MUSCLES (Low Success Rate)')
        self.stdout.write('=' * 60)
        self.stdout.write('')

        if not weak:
            self.stdout.write(self.style.SUCCESS('  No weak muscles detected!'))
            self.stdout.write('')
            return

        for w in weak:
            severity = w.get('severity', 'warning')
            style = self.style.ERROR if severity == 'critical' else self.style.WARNING
            self.stdout.write(style(
                f'  [{severity.upper()}] {w.get("agent", "?")}'
            ))
            self.stdout.write(f'    Success Rate: {w.get("success_rate", 0):.1f}%')
            self.stdout.write(f'    Executions (24h): {w.get("executions_24h", 0)}')
            self.stdout.write(f'    Failed (24h): {w.get("failed_24h", 0)}')
            self.stdout.write(f'    Issue: {w.get("issue", "?")}')
            self.stdout.write('')

        self.stdout.write(f'  Total: {len(weak)} weak muscles')
        self.stdout.write('')

    def _show_overworked(self, muscular, as_json: bool):
        """Show overworked muscles."""
        overworked = muscular.detect_overworked_muscles()

        if as_json:
            self.stdout.write(json.dumps(overworked, indent=2, default=str))
            return

        self.stdout.write('')
        self.stdout.write('=' * 60)
        self.stdout.write('  OVERWORKED MUSCLES (High Execution Count)')
        self.stdout.write('=' * 60)
        self.stdout.write('')

        if not overworked:
            self.stdout.write(self.style.SUCCESS('  No overworked muscles detected!'))
            self.stdout.write('')
            return

        for o in overworked:
            severity = o.get('severity', 'warning')
            style = self.style.ERROR if severity == 'critical' else self.style.WARNING
            self.stdout.write(style(
                f'  [{severity.upper()}] {o.get("agent", "?")}'
            ))
            self.stdout.write(f'    Executions (24h): {o.get("executions_24h", 0):,}')
            self.stdout.write(f'    Max Daily: {o.get("max_daily", 500)}')
            self.stdout.write(f'    Tokens Used: {o.get("tokens_used", 0):,}')
            self.stdout.write(f'    Cost: ${o.get("cost", 0):.4f}')
            self.stdout.write(f'    Issue: {o.get("issue", "?")}')
            self.stdout.write('')

        self.stdout.write(f'  Total: {len(overworked)} overworked muscles')
        self.stdout.write('')

    def _show_history(self, muscular, hours: int, as_json: bool):
        """Show muscular pulse history."""
        history = muscular.get_history(hours=hours)

        if as_json:
            self.stdout.write(json.dumps(history, indent=2, default=str))
            return

        self.stdout.write('')
        self.stdout.write('=' * 60)
        self.stdout.write(f'  MUSCULAR PULSE HISTORY (Last {hours}h)')
        self.stdout.write('=' * 60)
        self.stdout.write('')

        if not history:
            self.stdout.write('  No pulse records found.')
            self.stdout.write('')
            return

        for pulse in history[:20]:
            status = pulse.get('status', 'unknown')
            emoji = self._get_status_emoji(status)
            style = self._get_status_style(status)
            ts = pulse.get('timestamp', '?')[:19]
            status_display = status.upper().ljust(10)
            self.stdout.write(
                f'  {ts} - {style(status_display)} {emoji} '
                f'(Strength: {pulse.get("strength_score", 0):.1f}%, '
                f'Active: {pulse.get("active_agents", 0)})'
            )

        if len(history) > 20:
            self.stdout.write(f'  ... and {len(history) - 20} more records')

        self.stdout.write('')
        self.stdout.write(f'  Total: {len(history)} pulse records')
        self.stdout.write('')

    def _show_group(self, muscular, group_name: str, as_json: bool):
        """Show specific muscle group."""
        result = muscular.check_muscle_group(group_name)

        if as_json:
            self.stdout.write(json.dumps(result, indent=2, default=str))
            return

        if 'error' in result:
            self.stdout.write(self.style.ERROR(f'  Error: {result["error"]}'))
            return

        self.stdout.write('')
        self.stdout.write('=' * 60)
        self.stdout.write(f'  MUSCLE GROUP: {group_name.upper()}')
        self.stdout.write('=' * 60)
        self.stdout.write('')

        status = result.get('status', 'unknown')
        emoji = self._get_status_emoji(status)
        style = self._get_status_style(status)

        self.stdout.write(f'  Status: {style(status.upper())} {emoji}')
        self.stdout.write(f'  Strength Score: {result.get("strength_score", 0):.1f}%')
        self.stdout.write(f'  Fatigue Level: {result.get("fatigue_level", 0):.1f}%')
        self.stdout.write(f'  Strain Level: {result.get("strain_level", 0):.1f}%')
        self.stdout.write('')

        self.stdout.write('  EXECUTION STATS (24h):')
        self.stdout.write('  ' + '-' * 40)
        self.stdout.write(f'  Total Executions: {result.get("executions", 0):,}')
        self.stdout.write(f'  Successful: {result.get("successful", 0):,}')
        self.stdout.write(f'  Failed: {result.get("failed", 0):,}')
        self.stdout.write(f'  Success Rate: {result.get("success_rate", 0):.1f}%')
        self.stdout.write(f'  Avg Time: {result.get("avg_time_ms", 0):.0f}ms')
        self.stdout.write(f'  Total Tokens: {result.get("total_tokens", 0):,}')
        self.stdout.write(f'  Total Cost: ${result.get("total_cost", 0):.4f}')
        self.stdout.write('')

        self.stdout.write('  AGENTS:')
        self.stdout.write('  ' + '-' * 40)
        self.stdout.write(f'  Total: {result.get("total_agents", 0)}')
        self.stdout.write(f'  Active: {result.get("active_agents", 0)}')
        self.stdout.write(f'  Idle: {result.get("idle_agents", 0)}')
        self.stdout.write('')

        weak = result.get('weak_agents', [])
        if weak:
            self.stdout.write('  WEAK AGENTS:')
            for w in weak:
                self.stdout.write(self.style.WARNING(
                    f'    - {w.get("agent")}: {w.get("success_rate", 0):.1f}% success'
                ))
            self.stdout.write('')

        overworked = result.get('overworked_agents', [])
        if overworked:
            self.stdout.write('  OVERWORKED AGENTS:')
            for o in overworked:
                self.stdout.write(self.style.WARNING(
                    f'    - {o.get("agent")}: {o.get("executions", 0)} executions'
                ))
            self.stdout.write('')

    def _watch_mode(self, muscular, as_json: bool):
        """Continuous monitoring mode."""
        self.stdout.write('')
        self.stdout.write('MUSCULAR SYSTEM - Watch Mode (90s interval)')
        self.stdout.write('Press Ctrl+C to stop')
        self.stdout.write('')

        try:
            while True:
                result = muscular.flex(force=True)

                if as_json:
                    self.stdout.write(json.dumps(result, indent=2, default=str))
                else:
                    status = result['overall_status']
                    score = result['strength_score']
                    emoji = self._get_status_emoji(status)
                    exec_summary = result.get('execution_summary', {})
                    agent_summary = result.get('agent_summary', {})

                    timestamp = datetime.now().strftime('%H:%M:%S')
                    self.stdout.write(
                        f'[{timestamp}] {emoji} {status.upper()} (Strength: {score:.1f}%) | '
                        f'Exec: {exec_summary.get("total_24h", 0):,} | '
                        f'Active: {agent_summary.get("active_agents", 0)}/{agent_summary.get("total_agents", 0)} | '
                        f'Rate: {exec_summary.get("success_rate", 0):.1f}%'
                    )

                time.sleep(90)
        except KeyboardInterrupt:
            self.stdout.write('')
            self.stdout.write('Watch mode stopped.')

    def _get_status_emoji(self, status: str) -> str:
        """Get emoji for status."""
        return {
            'strong': '💪',
            'fit': '🏃',
            'fatigued': '😓',
            'strained': '🥵',
            'paralyzed': '🦽',
        }.get(status, '❓')

    def _get_status_style(self, status: str):
        """Get style function for status."""
        if status in ('strong', 'fit'):
            return self.style.SUCCESS
        elif status in ('fatigued',):
            return self.style.WARNING
        elif status in ('strained', 'paralyzed'):
            return self.style.ERROR
        return lambda x: x
