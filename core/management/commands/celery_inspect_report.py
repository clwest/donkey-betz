"""
Django management command to inspect Celery workers and generate a report.
Session 830: CLI helper to verify worker queues without guessing from UI.

Usage:
    python manage.py celery_inspect_report
    python manage.py celery_inspect_report --json-only
    python manage.py celery_inspect_report --timeout 10
"""

import json
import os
import subprocess
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Inspects Celery workers and generates a report of active queues, ping status, and stats'

    def add_arguments(self, parser):
        parser.add_argument(
            '--json-only',
            action='store_true',
            help='Only output JSON file, skip human-readable output'
        )
        parser.add_argument(
            '--timeout',
            type=int,
            default=5,
            help='Timeout in seconds for each inspect command (default: 5)'
        )
        parser.add_argument(
            '--output-dir',
            type=str,
            default='docs/ops',
            help='Directory to save JSON output (default: docs/ops)'
        )

    def handle(self, *args, **options):
        json_only = options['json_only']
        timeout = options['timeout']
        output_dir = options['output_dir']

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        report = {
            'generated_at': datetime.now().isoformat(),
            'timeout_seconds': timeout,
            'commands': {},
            'summary': {},
            'errors': []
        }

        if not json_only:
            self.stdout.write(self.style.HTTP_INFO('\n' + '=' * 60))
            self.stdout.write(self.style.HTTP_INFO('CELERY WORKER INSPECTION REPORT'))
            self.stdout.write(self.style.HTTP_INFO('=' * 60 + '\n'))

        # Run inspect commands
        commands = [
            ('ping', 'celery -A core inspect ping'),
            ('active_queues', 'celery -A core inspect active_queues'),
            ('stats', 'celery -A core inspect stats'),
            ('active', 'celery -A core inspect active'),
            ('registered', 'celery -A core inspect registered'),
        ]

        for name, cmd in commands:
            if not json_only:
                self.stdout.write(f'\n--- {name.upper()} ---')

            try:
                result = subprocess.run(
                    cmd.split(),
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=settings.BASE_DIR
                )

                if result.returncode == 0:
                    output = result.stdout.strip()
                    report['commands'][name] = {
                        'success': True,
                        'output': output,
                        'error': None
                    }
                    if not json_only:
                        self.stdout.write(self.style.SUCCESS(output[:2000]))  # Truncate for readability
                        if len(output) > 2000:
                            self.stdout.write(f'... (truncated, {len(output)} chars total)')
                else:
                    error_msg = result.stderr.strip() or 'Command failed with no stderr'
                    report['commands'][name] = {
                        'success': False,
                        'output': None,
                        'error': error_msg
                    }
                    report['errors'].append(f'{name}: {error_msg}')
                    if not json_only:
                        self.stdout.write(self.style.ERROR(f'Error: {error_msg}'))

            except subprocess.TimeoutExpired:
                msg = f'Timeout after {timeout}s'
                report['commands'][name] = {
                    'success': False,
                    'output': None,
                    'error': msg
                }
                report['errors'].append(f'{name}: {msg}')
                if not json_only:
                    self.stdout.write(self.style.WARNING(f'Timeout after {timeout}s'))

            except FileNotFoundError:
                msg = 'celery command not found - is Celery installed?'
                report['commands'][name] = {
                    'success': False,
                    'output': None,
                    'error': msg
                }
                report['errors'].append(f'{name}: {msg}')
                if not json_only:
                    self.stdout.write(self.style.ERROR(msg))
                break  # No point continuing if celery isn't installed

            except Exception as e:
                msg = str(e)
                report['commands'][name] = {
                    'success': False,
                    'output': None,
                    'error': msg
                }
                report['errors'].append(f'{name}: {msg}')
                if not json_only:
                    self.stdout.write(self.style.ERROR(f'Exception: {msg}'))

        # Generate summary
        report['summary'] = self._generate_summary(report)

        if not json_only:
            self.stdout.write('\n' + '=' * 60)
            self.stdout.write(self.style.HTTP_INFO('SUMMARY'))
            self.stdout.write('=' * 60)
            self._print_summary(report['summary'])

        # Save JSON report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_path = os.path.join(output_dir, f'celery_inspect_{timestamp}.json')

        with open(json_path, 'w') as f:
            json.dump(report, f, indent=2)

        if not json_only:
            self.stdout.write(f'\n{self.style.SUCCESS("JSON report saved to:")} {json_path}')

        # Exit with error code if no workers found
        if not report['summary'].get('workers_found', False):
            if not json_only:
                self.stdout.write(self.style.WARNING(
                    '\nNo workers responding. This could mean:\n'
                    '  1. No Celery workers are running\n'
                    '  2. Redis/broker is not accessible\n'
                    '  3. Workers are on a different broker URL\n'
                    '\nTry starting a worker with: celery -A core worker -l info'
                ))
            return

        self.stdout.write(self.style.SUCCESS('\nInspection complete!'))

    def _generate_summary(self, report):
        """Extract key information from the inspect results."""
        summary = {
            'workers_found': False,
            'worker_count': 0,
            'workers': [],
            'total_queues': set(),
            'queue_by_worker': {}
        }

        # Parse ping results
        ping_result = report['commands'].get('ping', {})
        if ping_result.get('success'):
            output = ping_result.get('output', '')
            # Count workers from ping output (lines with "celery@" or worker names)
            workers = [line.strip() for line in output.split('\n')
                      if 'celery@' in line or ('ok' in line.lower() and '->' in line)]
            summary['workers_found'] = len(workers) > 0
            summary['worker_count'] = len(workers)

        # Parse active_queues results
        queues_result = report['commands'].get('active_queues', {})
        if queues_result.get('success'):
            output = queues_result.get('output', '')
            # Parse queue assignments
            current_worker = None
            for line in output.split('\n'):
                line = line.strip()
                if line.startswith('->') and 'celery@' in line:
                    # Extract worker name
                    current_worker = line.replace('->', '').strip().rstrip(':')
                    summary['workers'].append(current_worker)
                    summary['queue_by_worker'][current_worker] = []
                elif current_worker and 'exchange' in line.lower():
                    # This line contains queue info
                    # Format is usually: * {name: 'queuename', exchange: ...}
                    if "name'" in line or 'name"' in line:
                        # Extract queue name
                        import re
                        match = re.search(r"name['\"]:\s*['\"]([^'\"]+)['\"]", line)
                        if match:
                            queue_name = match.group(1)
                            summary['queue_by_worker'][current_worker].append(queue_name)
                            summary['total_queues'].add(queue_name)

        # Convert set to list for JSON serialization
        summary['total_queues'] = list(summary['total_queues'])

        return summary

    def _print_summary(self, summary):
        """Print human-readable summary."""
        if summary.get('workers_found'):
            self.stdout.write(self.style.SUCCESS(
                f"\nWorkers found: {summary['worker_count']}"
            ))

            for worker in summary.get('workers', []):
                queues = summary.get('queue_by_worker', {}).get(worker, [])
                queue_str = ', '.join(queues) if queues else '(unknown)'
                self.stdout.write(f"  {worker}: {queue_str}")

            if summary.get('total_queues'):
                self.stdout.write(f"\nTotal unique queues: {', '.join(summary['total_queues'])}")
        else:
            self.stdout.write(self.style.WARNING('\nNo workers found!'))
