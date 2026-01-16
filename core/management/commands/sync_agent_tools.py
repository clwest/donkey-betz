"""
Session 735: Sync Agent Tools from code definitions to database.
Session 761: Filter to only sync utility tools (not agent wrappers).

This command populates the AgentTool database table from the tool definitions
in core/assistant/tool_definitions.py, making them visible in the Tools tab.

Only syncs UTILITY tools - tools that provide actual functionality.
Agent wrappers (tools that just call agents) are excluded since agents
are already shown in the Directory tab.

Usage:
    python manage.py sync_agent_tools
"""

from django.core.management.base import BaseCommand
from core.assistant.tool_definitions import get_tool_definitions
from core.models.agents_registry.models import AgentTool


class Command(BaseCommand):
    help = 'Sync utility tools from code definitions to database (excludes agent wrappers)'

    def is_agent_wrapper(self, name: str) -> bool:
        """
        Session 761: Determine if a tool is just an agent wrapper.
        Agent wrappers are excluded since agents are shown in the Directory tab.
        """
        # Tools ending with _agent are agent wrappers
        if name.endswith('_agent'):
            return True
        # universal_agent_tool is also an agent wrapper
        if name == 'universal_agent_tool':
            return True
        return False

    def handle(self, *args, **options):
        tools = get_tool_definitions()
        self.stdout.write(f'Found {len(tools)} total tools in code definitions')

        created = 0
        updated = 0
        skipped = 0

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

            # Session 761: Skip agent wrappers
            if self.is_agent_wrapper(name):
                skipped += 1
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

        # Session 761: Clean up any existing agent wrappers in the database
        agent_wrapper_names = [
            name for name in AgentTool.objects.values_list('name', flat=True)
            if self.is_agent_wrapper(name)
        ]
        if agent_wrapper_names:
            deleted_count = AgentTool.objects.filter(name__in=agent_wrapper_names).delete()[0]
            self.stdout.write(self.style.WARNING(
                f'  Cleaned up {deleted_count} agent wrappers from database'
            ))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'Sync complete: {created} created, {updated} updated, {skipped} agent wrappers skipped. '
            f'Total utility tools: {AgentTool.objects.count()}'
        ))
