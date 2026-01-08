"""
Session 735: Sync Agent Tools from code definitions to database.

This command populates the AgentTool database table from the tool definitions
in core/assistant/tool_definitions.py, making them visible in the Tools tab.

Usage:
    python manage.py sync_agent_tools
"""

from django.core.management.base import BaseCommand
from core.assistant.tool_definitions import get_tool_definitions
from core.models.agents_registry.models import AgentTool


class Command(BaseCommand):
    help = 'Sync agent tools from code definitions to database'

    def handle(self, *args, **options):
        tools = get_tool_definitions()
        self.stdout.write(f'Found {len(tools)} tools in code definitions')

        created = 0
        updated = 0

        for tool in tools:
            # Get nested function definition (OpenAI function calling format)
            if 'function' in tool:
                func = tool['function']
                name = func.get('name', '')
                description = func.get('description', '')
            else:
                name = tool.get('name', '')
                description = tool.get('description', '')

            if not name:
                continue

            # Determine tool type from name
            tool_type = 'api'
            name_lower = name.lower()
            if 'workspace' in name_lower:
                tool_type = 'integration'
            elif 'analysis' in name_lower or 'ml_' in name_lower:
                tool_type = 'analysis'
            elif any(x in name_lower for x in ['content', 'video', 'image', 'audio', 'brand', 'character']):
                tool_type = 'content_generation'
            elif 'search' in name_lower:
                tool_type = 'data_processing'
            elif any(x in name_lower for x in ['alert', 'vital', 'budget', 'monitor']):
                tool_type = 'monitoring'
            elif any(x in name_lower for x in ['pipeline', 'orchestrat', 'workflow']):
                tool_type = 'integration'
            elif any(x in name_lower for x in ['revenue', 'opportunity', 'task']):
                tool_type = 'data_processing'

            obj, was_created = AgentTool.objects.update_or_create(
                name=name,
                defaults={
                    'display_name': name.replace('_', ' ').title(),
                    'description': description[:500] if description else '',
                    'tool_type': tool_type,
                    'is_active': True,
                }
            )

            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f'  Created: {name}'))
            else:
                updated += 1

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'Sync complete: {created} created, {updated} updated. '
            f'Total: {AgentTool.objects.count()} tools'
        ))
