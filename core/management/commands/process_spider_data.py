"""
Process unprocessed spider data and route to appropriate agents
"""
from django.core.management.base import BaseCommand
from core.models_unified_system import SpiderData, Agent, AgentSolution
from intelligence.spider_agent_connector import SpiderAgentConnector
import json
from datetime import datetime


class Command(BaseCommand):
    help = 'Process unprocessed spider data'

    def handle(self, *args, **kwargs):
        self.stdout.write('🕷️ Processing unprocessed spider data...\n')

        # Initialize connector
        connector = SpiderAgentConnector()

        # Get all unprocessed data
        unprocessed = SpiderData.objects.filter(is_processed=False)
        total = unprocessed.count()

        self.stdout.write(f'Found {total} unprocessed items\n')

        processed_count = 0
        error_count = 0

        for spider_data in unprocessed:
            try:
                self.stdout.write(f'\nProcessing: {spider_data.spider_name} - {spider_data.data_type}')

                # Route to agents
                result = connector.route_spider_data(spider_data)

                # Mark as processed
                spider_data.is_processed = True
                spider_data.save()

                processed_count += 1

                if result.get('agents_notified'):
                    self.stdout.write(f'  ✅ Routed to: {", ".join(result["agents_notified"])}')
                    self.stdout.write(f'  📝 Solutions created: {len(result.get("solutions_created", []))}')
                else:
                    self.stdout.write('  ⚠️ No agents matched for this data')

            except Exception as e:
                error_count += 1
                self.stdout.write(f'  ❌ Error: {str(e)}')

        self.stdout.write(f'\n\n✅ Processing Complete!')
        self.stdout.write(f'  Processed: {processed_count}/{total}')
        self.stdout.write(f'  Errors: {error_count}')

        # Show current status
        remaining = SpiderData.objects.filter(is_processed=False).count()
        self.stdout.write(f'  Remaining unprocessed: {remaining}\n')