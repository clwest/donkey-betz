"""
Django Management Command for System Reality Check
===================================================

Session 624: Comprehensive verification that all autonomous systems
are functioning as designed.

Usage:
    python manage.py system_reality_check                    # Quick summary
    python manage.py system_reality_check --verbose          # Detailed output
    python manage.py system_reality_check --output report    # Generate docs/SYSTEM_REALITY_CHECK.md
    python manage.py system_reality_check --fail-on-error    # Exit 1 if issues (for CI/CD)
    python manage.py system_reality_check --lookback 24      # Check last 24 hours
"""

import sys
import json
from datetime import datetime
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django management command for system reality checking"""

    help = 'Verify all autonomous systems are functioning as designed'

    def add_arguments(self, parser):
        """Add command line arguments"""
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed per-system output'
        )
        parser.add_argument(
            '--output',
            type=str,
            choices=['report', 'json'],
            help='Generate output: "report" for docs/SYSTEM_REALITY_CHECK.md, "json" for JSON'
        )
        parser.add_argument(
            '--fail-on-error',
            action='store_true',
            help='Exit with code 1 if any system is critical (for CI/CD)'
        )
        parser.add_argument(
            '--lookback',
            type=int,
            default=6,
            help='Hours to look back for activity (default: 6)'
        )

    def handle(self, *args, **options):
        """Main command handler"""
        self.verbose = options['verbose']
        self.output = options['output']
        self.fail_on_error = options['fail_on_error']
        self.lookback = options['lookback']

        self.stdout.write(self.style.SUCCESS(
            "\n" + "=" * 70 +
            "\n  SYSTEM REALITY CHECK - Session 624" +
            "\n" + "=" * 70
        ))

        # Run the checker
        from core.services.system_reality_checker import SystemRealityChecker
        checker = SystemRealityChecker(lookback_hours=self.lookback)
        results = checker.run()

        # Display results
        self.display_results(results)

        # Generate output if requested
        if self.output == 'report':
            self.generate_markdown_report(results)
        elif self.output == 'json':
            self.generate_json_output(results)

        # Exit with error code if requested and issues found
        if self.fail_on_error and results['overall_status'] == 'critical':
            sys.exit(1)

    def get_status_icon(self, status):
        """Get icon for status"""
        if status == 'healthy':
            return ''
        elif status == 'warning':
            return ''
        return ''

    def get_score_style(self, score):
        """Get style for score display"""
        if score >= 70:
            return self.style.SUCCESS
        elif score >= 50:
            return self.style.WARNING
        return self.style.ERROR

    def display_results(self, results):
        """Display reality check results"""
        # Overall score
        score = results['overall_score']
        status = results['overall_status']
        status_icon = self.get_status_icon(status)

        self.stdout.write(f"\n  OVERALL REALITY SCORE: {self.get_score_style(score)(f'{score}%')} {status_icon}")
        self.stdout.write(f"  Lookback Period: {results['lookback_hours']} hours")
        self.stdout.write(f"  Timestamp: {results['timestamp'][:19]}")

        # Systems table
        self.stdout.write("\n" + "-" * 70)

        # Header
        self.stdout.write(
            f"  {'System':<22} {'Score':>6}  {'Status':<10} {'Details'}"
        )
        self.stdout.write("-" * 70)

        for system in results['systems']:
            name = system['name']
            sys_score = system['score']
            sys_status = system['status']
            message = system['message']
            icon = self.get_status_icon(sys_status)

            score_str = self.get_score_style(sys_score)(f"{sys_score:>3}%")
            self.stdout.write(f"  {name:<22} {score_str}  {icon:<10} {message}")

            # Show verbose details
            if self.verbose and system.get('metrics'):
                for key, value in system['metrics'].items():
                    self.stdout.write(f"      {key}: {value}")

        self.stdout.write("-" * 70)

        # Summary
        summary = results['summary']
        healthy_count = summary['healthy']
        warning_count = summary['warning']
        critical_count = summary['critical']
        self.stdout.write(f"\n  Summary: {self.style.SUCCESS(f'{healthy_count} healthy')}, "
                         f"{self.style.WARNING(f'{warning_count} warning')}, "
                         f"{self.style.ERROR(f'{critical_count} critical')}")

        # Issues
        if results['issues']:
            self.stdout.write(f"\n  ISSUES REQUIRING ATTENTION:")
            for i, issue in enumerate(results['issues'][:10], 1):
                self.stdout.write(self.style.WARNING(f"    {i}. {issue}"))
            if len(results['issues']) > 10:
                self.stdout.write(f"    ... and {len(results['issues']) - 10} more")

        self.stdout.write("\n" + "=" * 70 + "\n")

    def generate_markdown_report(self, results):
        """Generate docs/SYSTEM_REALITY_CHECK.md"""
        report_path = 'docs/SYSTEM_REALITY_CHECK.md'

        status_emoji = {
            'healthy': '',
            'warning': '',
            'critical': ''
        }

        content = f"""# System Reality Check Report

**Generated:** {results['timestamp'][:19]}
**Status:** {status_emoji.get(results['overall_status'], '')} {results['overall_status'].upper()}
**Overall Score:** {results['overall_score']}%
**Lookback Period:** {results['lookback_hours']} hours

---

## Summary

| Metric | Count |
|--------|-------|
| Healthy Systems | {results['summary']['healthy']} |
| Warning Systems | {results['summary']['warning']} |
| Critical Systems | {results['summary']['critical']} |

---

## System Status

| System | Score | Status | Details |
|--------|-------|--------|---------|
"""
        for system in results['systems']:
            icon = status_emoji.get(system['status'], '')
            content += f"| {system['name']} | {system['score']}% | {icon} {system['status']} | {system['message']} |\n"

        if results['issues']:
            content += """
---

## Issues Requiring Attention

"""
            for i, issue in enumerate(results['issues'], 1):
                content += f"{i}. {issue}\n"

        content += """
---

## System Metrics

"""
        for system in results['systems']:
            content += f"### {system['name']}\n\n"
            if system.get('metrics'):
                content += "| Metric | Value |\n|--------|-------|\n"
                for key, value in system['metrics'].items():
                    content += f"| {key} | {value} |\n"
            content += "\n"

        content += f"""---

## How to Use This Report

```bash
# Quick health check
python manage.py system_reality_check

# Detailed output
python manage.py system_reality_check --verbose

# Check longer period
python manage.py system_reality_check --lookback 24

# CI/CD mode (exit 1 on critical issues)
python manage.py system_reality_check --fail-on-error

# Regenerate this report
python manage.py system_reality_check --output report
```

---

*Generated by `system_reality_check` management command (Session 624)*
"""

        with open(report_path, 'w') as f:
            f.write(content)

        self.stdout.write(self.style.SUCCESS(f"\n  Report generated: {report_path}"))

    def generate_json_output(self, results):
        """Output results as JSON"""
        print(json.dumps(results, indent=2, default=str))
