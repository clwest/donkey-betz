"""
Django management command to wire all agents in the registry
"""

from django.core.management.base import BaseCommand
from agents.agent_wiring_system import UnifiedAgentWiringSystem


class Command(BaseCommand):
    help = 'Wire all agents in the unified platform registry'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n🔌 STARTING AGENT WIRING SYSTEM...'))
        self.stdout.write('=' * 60)

        # Initialize the wiring system
        wiring_system = UnifiedAgentWiringSystem()

        # Run the wiring process (now synchronous)
        results = wiring_system.wire_all_agents()

        # Display results
        self.stdout.write('\n' + results["summary"])

        # Show detailed statistics
        self.stdout.write('\n📊 DETAILED STATISTICS:')
        self.stdout.write(f'   • Total agents defined: {results["total_agents"]}')
        self.stdout.write(f'   • Successfully wired: {results["successfully_wired"]}')
        self.stdout.write(f'   • Connections created: {results["connections_created"]}')

        if results.get("verification"):
            verification = results["verification"]
            self.stdout.write(f'\n🔍 CONNECTION VERIFICATION:')
            self.stdout.write(f'   • Total connections: {verification["total_connections"]}')
            self.stdout.write(f'   • Verified: {verification["verified"]}')
            if verification["broken"]:
                self.stdout.write(f'   • Broken: {len(verification["broken"])}')

        if results.get("advisor_connections"):
            advisor_conn = results["advisor_connections"]
            self.stdout.write(f'\n🤝 ADVISOR CONNECTIONS:')
            self.stdout.write(f'   • Total advisors: {advisor_conn["total_advisors"]}')
            self.stdout.write(f'   • Connected agents: {len(advisor_conn["connected_agents"])}')
            self.stdout.write(f'   • Connections created: {advisor_conn["connections_created"]}')

        if results["failed"]:
            self.stdout.write(self.style.WARNING(f'\n⚠️  Failed agents: {", ".join(results["failed"])}'))

        # Final status
        success_rate = (results["successfully_wired"] / results["total_agents"]) * 100
        if success_rate == 100:
            self.stdout.write(self.style.SUCCESS('\n✅ ALL AGENTS SUCCESSFULLY WIRED!'))
        elif success_rate >= 80:
            self.stdout.write(self.style.SUCCESS(f'\n✅ SYSTEM OPERATIONAL ({success_rate:.1f}% agents wired)'))
        else:
            self.stdout.write(self.style.WARNING(f'\n⚠️  PARTIAL SUCCESS ({success_rate:.1f}% agents wired)'))

        self.stdout.write('=' * 60)
        self.stdout.write(self.style.SUCCESS('AGENT WIRING COMPLETE\n'))