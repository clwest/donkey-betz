"""
ops_verify — on-demand ops verification (same checks as ops_control_loop).

Usage:
    python manage.py ops_verify
    python manage.py ops_verify --env railway_prod
    python manage.py ops_verify --env local
"""

import json
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Run ops verification checks (deploy_verify, pa_tools_smoke, DB, error summary)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--env', default='railway_prod',
            help='Environment to test against (railway_prod or local)',
        )
        parser.add_argument(
            '--json', action='store_true', dest='output_json',
            help='Output results as JSON',
        )

    def handle(self, *args, **options):
        from core.tools.http_smoke_test import run_smoke_test
        from django.utils import timezone
        from datetime import timedelta

        env = options['env']
        results = {}
        failures = []

        # 1. deploy_verify
        self.stdout.write('Running deploy_verify...')
        try:
            dv = run_smoke_test({'suite': 'deploy_verify', 'environment': env})
            results['deploy_verify'] = {
                'ok': dv.get('ok', False),
                'passed': dv.get('passed', 0),
                'failed': dv.get('failed', 0),
            }
            if not dv.get('ok'):
                failures.append(f"deploy_verify: {dv.get('failed', '?')} checks failed")
                self._print_step('deploy_verify', False, dv)
            else:
                self._print_step('deploy_verify', True, dv)
        except Exception as e:
            results['deploy_verify'] = {'ok': False, 'error': str(e)[:200]}
            failures.append(f"deploy_verify: {e}")
            self._print_step('deploy_verify', False, {'error': str(e)[:200]})

        # 2. pa_tools_smoke
        self.stdout.write('Running pa_tools_smoke...')
        try:
            pts = run_smoke_test({'suite': 'pa_tools_smoke', 'environment': env})
            results['pa_tools_smoke'] = {
                'ok': pts.get('ok', False),
                'passed': pts.get('passed', 0),
                'failed': pts.get('failed', 0),
            }
            if not pts.get('ok'):
                failures.append(f"pa_tools_smoke: {pts.get('failed', '?')} checks failed")
                self._print_step('pa_tools_smoke', False, pts)
            else:
                self._print_step('pa_tools_smoke', True, pts)
        except Exception as e:
            results['pa_tools_smoke'] = {'ok': False, 'error': str(e)[:200]}
            failures.append(f"pa_tools_smoke: {e}")
            self._print_step('pa_tools_smoke', False, {'error': str(e)[:200]})

        # 3. DB health
        self.stdout.write('Checking DB health...')
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            results['db_health'] = {'ok': True}
            self._print_step('db_health', True)
        except Exception as e:
            results['db_health'] = {'ok': False, 'error': str(e)[:200]}
            failures.append(f"db_health: {e}")
            self._print_step('db_health', False, {'error': str(e)[:200]})

        # 4. Error summary (24h)
        self.stdout.write('Checking error summary...')
        try:
            from core.models_celery_telemetry import CeleryTaskEvent
            cutoff = timezone.now() - timedelta(hours=24)
            error_count = CeleryTaskEvent.objects.filter(
                status='FAILURE', started_at__gte=cutoff,
            ).count()
            ok = error_count < 50
            results['error_summary'] = {'ok': ok, 'errors_24h': error_count}
            if not ok:
                failures.append(f"error_summary: {error_count} task failures in 24h")
            self._print_step('error_summary', ok, {'errors_24h': error_count})
        except Exception as e:
            results['error_summary'] = {'ok': False, 'error': str(e)[:200]}
            failures.append(f"error_summary: {e}")
            self._print_step('error_summary', False, {'error': str(e)[:200]})

        # Summary
        all_ok = len(failures) == 0

        if options['output_json']:
            self.stdout.write(json.dumps({
                'ok': all_ok, 'results': results, 'failures': failures,
            }, indent=2))
        else:
            self.stdout.write('')
            if all_ok:
                self.stdout.write(self.style.SUCCESS('ALL CHECKS PASSED'))
            else:
                self.stdout.write(self.style.ERROR(
                    f'FAILED — {len(failures)} check(s):'
                ))
                for f in failures:
                    self.stdout.write(self.style.ERROR(f'  - {f}'))

    def _print_step(self, name, ok, detail=None):
        marker = self.style.SUCCESS('PASS') if ok else self.style.ERROR('FAIL')
        msg = f'  [{marker}] {name}'
        if detail and not ok:
            err = detail.get('error', '')
            failed = detail.get('failed', '')
            if err:
                msg += f' — {err}'
            elif failed:
                msg += f' — {failed} failed'
        self.stdout.write(msg)
