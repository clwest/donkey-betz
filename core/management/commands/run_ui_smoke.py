"""
import logging
logger = logging.getLogger(__name__)

Management command: run UI smoke tests with Playwright (dev/CI only).

Requires ``playwright`` to be installed (``pip install playwright && playwright install chromium``).
NOT a production dependency.

Usage:
    python manage.py run_ui_smoke --token <DRF-token>
    python manage.py run_ui_smoke --base-url http://localhost:8000 --token <token> --routes / /governance /boardroom
"""

import json
import os

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Run UI smoke tests against frontend routes using Playwright'

    def add_arguments(self, parser):
        parser.add_argument(
            '--base-url',
            default='http://localhost:8000',
            help='Base URL of the running app',
        )
        parser.add_argument(
            '--token',
            required=True,
            help='DRF auth token (injected into localStorage for auth)',
        )
        parser.add_argument(
            '--routes',
            nargs='*',
            default=None,
            help='Specific routes to test (default: all from manifest)',
        )
        parser.add_argument(
            '--screenshot-dir',
            default='/tmp/ui-smoke-screenshots',
            help='Directory for screenshots',
        )

    def handle(self, *args, **options):
        # Lazy import — Playwright is not a production dependency
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            self.stderr.write(self.style.ERROR(
                'playwright is not installed. Run:\n'
                '  pip install playwright && playwright install chromium'
            ))
            return

        base_url = options['base_url'].rstrip('/')
        token = options['token']
        screenshot_dir = options['screenshot_dir']
        os.makedirs(screenshot_dir, exist_ok=True)

        # Determine routes to test
        routes = options.get('routes')
        if not routes:
            routes = self._load_routes_from_manifest(base_url)

        self.stdout.write(f'Testing {len(routes)} routes against {base_url}')

        results = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={'width': 1280, 'height': 720})
            page = context.new_page()

            # Inject auth token into localStorage (matches Zustand persist key)
            page.goto(f'{base_url}/login')
            page.evaluate(f"""() => {{
                const state = {{
                    state: {{
                        token: '{token}',
                        isAuthenticated: true,
                        user: {{ username: 'smoke-test' }}
                    }},
                    version: 0
                }};
                localStorage.setItem('auth-storage', JSON.stringify(state));
            }}""")

            console_errors = []
            page.on('console', lambda msg: console_errors.append(msg.text) if msg.type == 'error' else None)

            for route in routes:
                console_errors.clear()
                url = f'{base_url}{route}'
                status = 'PASS'
                detail = ''

                try:
                    response = page.goto(url, wait_until='networkidle', timeout=15000)
                    http_status = response.status if response else 0

                    if http_status >= 400:
                        status = 'FAIL'
                        detail = f'HTTP {http_status}'
                    elif console_errors:
                        status = 'WARN'
                        detail = f'{len(console_errors)} console error(s)'

                    # Screenshot
                    safe_name = route.strip('/').replace('/', '_') or 'root'
                    screenshot_path = os.path.join(screenshot_dir, f'{safe_name}.png')
                    page.screenshot(path=screenshot_path)

                except Exception as exc:
                    status = 'FAIL'
                    detail = str(exc)[:200]

                results.append({
                    'route': route,
                    'status': status,
                    'detail': detail,
                })

                style = {
                    'PASS': self.style.SUCCESS,
                    'WARN': self.style.WARNING,
                    'FAIL': self.style.ERROR,
                }.get(status, self.style.NOTICE)
                self.stdout.write(style(f'  [{status}] {route} {detail}'))

            browser.close()

        passed = sum(1 for r in results if r['status'] == 'PASS')
        total = len(results)
        summary = f'\n{passed}/{total} routes passed'
        if passed == total:
            self.stdout.write(self.style.SUCCESS(summary))
        else:
            self.stdout.write(self.style.WARNING(summary))

        self.stdout.write(f'Screenshots saved to {screenshot_dir}')

    def _load_routes_from_manifest(self, base_url: str) -> list:
        """Load routes from __manifest.json or fall back to hardcoded list."""
        manifest_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            'frontend', 'dist', '__manifest.json',
        )

        if os.path.isfile(manifest_path):
            try:
                with open(manifest_path) as f:
                    data = json.load(f)
                routes = [r['path'] for r in data.get('routes', [])
                          if r.get('authRequired', True) and ':' not in r.get('path', '')]
                if routes:
                    return routes
            except Exception as _e:
                logger.warning(
                    "run_ui_smoke._load_routes_from_manifest: swallowed (%s: %s) — degraded",
                    type(_e).__name__, _e,
                )

        return [
            '/', '/dashboard', '/workspace', '/boardroom', '/governance',
            '/platform', '/agents', '/intelligence', '/content', '/betting',
            '/stocks', '/image-studio', '/video-studio', '/advisors',
            '/analytics', '/documents', '/settings', '/profile',
        ]
