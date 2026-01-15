"""
Test All 73 Agents - Session 757

Runs a quick diagnostic on every agent to verify they're working and returning data.
"""

from django.core.management.base import BaseCommand
from core.agent_router import AgentRouter
import time
import sys


class Command(BaseCommand):
    help = 'Test all 73 agents and report their status'

    def add_arguments(self, parser):
        parser.add_argument(
            '--quick',
            action='store_true',
            help='Quick test with simple prompt'
        )
        parser.add_argument(
            '--agent',
            type=str,
            help='Test only a specific agent'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit number of agents to test'
        )

    def handle(self, *args, **options):
        router = AgentRouter()
        agent_names = sorted(router.AGENT_MAP.keys())

        if options['agent']:
            agent_names = [options['agent']]
        elif options['limit']:
            agent_names = agent_names[:options['limit']]

        self.stdout.write(self.style.NOTICE("=" * 70))
        self.stdout.write(self.style.NOTICE(f"Testing {len(agent_names)} Agents"))
        self.stdout.write(self.style.NOTICE("=" * 70))
        self.stdout.write("")

        prompt = "State your name and one capability in one sentence." if options['quick'] else \
                 "Perform a brief self-diagnostic: state your name, primary function, and confirm you're operational."

        results = {
            'success': [],
            'short_response': [],
            'error': []
        }

        for i, name in enumerate(agent_names, 1):
            self.stdout.write(f"[{i}/{len(agent_names)}] Testing {name}...")
            sys.stdout.flush()

            start = time.time()
            try:
                result = router.route(name, prompt)
                elapsed = time.time() - start

                msg = result.message if result.message else ''
                msg_len = len(msg)

                # Categorize result
                if not result.success:
                    results['error'].append({
                        'name': name,
                        'error': 'Agent returned success=False',
                        'message': msg[:100]
                    })
                    self.stdout.write(self.style.ERROR(f"  ❌ FAILED (success=False)"))
                elif msg_len < 50:
                    results['short_response'].append({
                        'name': name,
                        'length': msg_len,
                        'message': msg
                    })
                    self.stdout.write(self.style.WARNING(f"  ⚠️ SHORT RESPONSE ({msg_len} chars)"))
                else:
                    results['success'].append({
                        'name': name,
                        'length': msg_len,
                        'time': elapsed,
                        'preview': msg[:80]
                    })
                    self.stdout.write(self.style.SUCCESS(f"  ✅ OK ({msg_len} chars, {elapsed:.1f}s)"))

                # Show preview
                preview = msg[:100].replace('\n', ' ') if msg else 'No response'
                self.stdout.write(f"     {preview}...")

            except Exception as e:
                elapsed = time.time() - start
                results['error'].append({
                    'name': name,
                    'error': str(e)[:200]
                })
                self.stdout.write(self.style.ERROR(f"  ❌ EXCEPTION: {str(e)[:60]}"))

            self.stdout.write("")

        # Summary
        self.stdout.write("")
        self.stdout.write(self.style.NOTICE("=" * 70))
        self.stdout.write(self.style.NOTICE("SUMMARY"))
        self.stdout.write(self.style.NOTICE("=" * 70))
        self.stdout.write(self.style.SUCCESS(f"✅ SUCCESS: {len(results['success'])} agents"))
        self.stdout.write(self.style.WARNING(f"⚠️ SHORT RESPONSE: {len(results['short_response'])} agents"))
        self.stdout.write(self.style.ERROR(f"❌ ERROR: {len(results['error'])} agents"))

        if results['error']:
            self.stdout.write("")
            self.stdout.write(self.style.ERROR("Failed Agents:"))
            for r in results['error']:
                self.stdout.write(f"  - {r['name']}: {r['error'][:60]}")

        if results['short_response']:
            self.stdout.write("")
            self.stdout.write(self.style.WARNING("Short Response Agents:"))
            for r in results['short_response']:
                self.stdout.write(f"  - {r['name']}: {r['length']} chars - {r['message'][:50]}")

        # Calculate success rate
        total = len(agent_names)
        success_rate = (len(results['success']) / total * 100) if total > 0 else 0
        self.stdout.write("")
        self.stdout.write(f"Success Rate: {success_rate:.1f}%")
