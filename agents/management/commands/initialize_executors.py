"""
Django Management Command: Initialize Agent Executors

This command initializes the agent executor system, registers all executors,
and provides management capabilities for the execution infrastructure.

Usage:
    python manage.py initialize_executors
    python manage.py initialize_executors --register-all
    python manage.py initialize_executors --test-execution
    python manage.py initialize_executors --status
"""

import asyncio
import json
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from pathlib import Path

from agents.executor_registry import (
    executor_system,
    initialize_all_agent_executors,
    get_execution_statistics,
    system_health_check,
    execute_agent_by_name
)
from agents.models import UnifiedAgentTemplate, AgentExecution


class Command(BaseCommand):
    help = 'Initialize and manage agent executors'

    def add_arguments(self, parser):
        parser.add_argument(
            '--register-all',
            action='store_true',
            help='Register executors for all database agents'
        )
        parser.add_argument(
            '--test-execution',
            action='store_true',
            help='Run test execution for core agents'
        )
        parser.add_argument(
            '--status',
            action='store_true',
            help='Show executor system status'
        )
        parser.add_argument(
            '--stats',
            action='store_true',
            help='Show execution statistics'
        )
        parser.add_argument(
            '--health-check',
            action='store_true',
            help='Run comprehensive health check'
        )

    def handle(self, *args, **options):
        """Handle command execution"""

        self.stdout.write(
            self.style.SUCCESS('🚀 Agent Executor Management System')
        )
        self.stdout.write('=' * 50)

        try:
            # Default action: register all executors
            if not any([
                options['register_all'],
                options['test_execution'],
                options['status'],
                options['stats'],
                options['health_check']
            ]):
                options['register_all'] = True
                options['status'] = True

            if options['register_all']:
                self.register_all_executors()

            if options['status']:
                self.show_status()

            if options['stats']:
                self.show_statistics()

            if options['health_check']:
                self.run_health_check()

            if options['test_execution']:
                self.run_test_execution()

        except Exception as e:
            raise CommandError(f'Command failed: {e}')

    def register_all_executors(self):
        """Register executors for all agents"""

        self.stdout.write(
            self.style.WARNING('📝 Registering agent executors...')
        )

        try:
            # Run async registration
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(initialize_all_agent_executors())

            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Registration complete: '
                    f'{result.get("registered", 0)} registered, '
                    f'{result.get("skipped", 0)} skipped, '
                    f'{result.get("total_executors", 0)} total executors'
                )
            )

            # Show registered executors
            registered = executor_system.executor_registry.list_executors()
            if registered:
                self.stdout.write('\n📋 Registered Executors:')
                for i, executor_name in enumerate(registered, 1):
                    self.stdout.write(f'  {i}. {executor_name}')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Registration failed: {e}')
            )

    def show_status(self):
        """Show executor system status"""

        self.stdout.write('\n' + self.style.WARNING('📊 System Status'))
        self.stdout.write('-' * 30)

        try:
            # Get system statistics
            stats = get_execution_statistics()

            # System overview
            system_stats = stats.get('system_stats', {})
            self.stdout.write(f"Total Executions: {system_stats.get('total_executions', 0)}")
            self.stdout.write(f"Successful: {system_stats.get('successful_executions', 0)}")
            self.stdout.write(f"Failed: {system_stats.get('failed_executions', 0)}")
            self.stdout.write(f"Success Rate: {system_stats.get('success_rate', 0):.1%}")
            self.stdout.write(f"Registered Executors: {system_stats.get('registered_executors', 0)}")

            # Database statistics
            total_agents = UnifiedAgentTemplate.objects.filter(is_active=True).count()
            recent_executions = AgentExecution.objects.filter(
                created_at__gte=timezone.now() - timezone.timedelta(hours=24)
            ).count()

            self.stdout.write(f"Active DB Agents: {total_agents}")
            self.stdout.write(f"Recent Executions (24h): {recent_executions}")

            # Executor capabilities
            core_agents = ['income_builder', 'content_creator', 'payment_processor']
            self.stdout.write('\n🔧 Core Agent Status:')
            for agent_name in core_agents:
                executor = executor_system.executor_registry.get_executor(agent_name)
                status = "✅ Ready" if executor else "❌ Not Ready"
                self.stdout.write(f"  {agent_name}: {status}")

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Status check failed: {e}')
            )

    def show_statistics(self):
        """Show detailed execution statistics"""

        self.stdout.write('\n' + self.style.WARNING('📈 Execution Statistics'))
        self.stdout.write('-' * 35)

        try:
            stats = get_execution_statistics()

            # Registry statistics
            registry_stats = stats.get('registry_stats', {})
            if registry_stats:
                self.stdout.write(f"Registry Total Executions: {registry_stats.get('total_executions', 0)}")
                self.stdout.write(f"Registry Success Rate: {registry_stats.get('success_rate', 0):.1%}")
                self.stdout.write(f"Registry Total Cost: ${registry_stats.get('total_cost', 0):.2f}")

            # Individual executor performance
            executors_data = registry_stats.get('executors', {})
            if executors_data:
                self.stdout.write('\n🎯 Individual Executor Performance:')
                for name, data in executors_data.items():
                    self.stdout.write(f"  {name}:")
                    self.stdout.write(f"    Executions: {data.get('total_executions', 0)}")
                    self.stdout.write(f"    Success Rate: {data.get('success_rate', 0):.1%}")
                    self.stdout.write(f"    Avg Time: {data.get('avg_execution_time_ms', 0):.0f}ms")
                    self.stdout.write(f"    Total Cost: ${data.get('total_cost', 0):.2f}")

            # Recent executions from database
            recent_executions = AgentExecution.objects.filter(
                created_at__gte=timezone.now() - timezone.timedelta(hours=24)
            ).order_by('-created_at')[:5]

            if recent_executions:
                self.stdout.write('\n📋 Recent Executions (Last 24h):')
                for execution in recent_executions:
                    status_color = self.style.SUCCESS if execution.status == 'completed' else self.style.ERROR
                    self.stdout.write(
                        f"  {execution.execution_id}: "
                        f"{status_color(execution.status)} "
                        f"({execution.template.name}) "
                        f"${execution.total_cost:.2f}"
                    )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Statistics failed: {e}')
            )

    def run_health_check(self):
        """Run comprehensive health check"""

        self.stdout.write('\n' + self.style.WARNING('🏥 Health Check'))
        self.stdout.write('-' * 25)

        try:
            # Run async health check
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            health_result = loop.run_until_complete(system_health_check())

            # Display results
            if health_result.get('status') == 'healthy':
                self.stdout.write(
                    self.style.SUCCESS('✅ System Status: HEALTHY')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('❌ System Status: UNHEALTHY')
                )
                if 'error' in health_result:
                    self.stdout.write(f'Error: {health_result["error"]}')

            # Detailed health information
            self.stdout.write(f"Registered Executors: {health_result.get('registered_executors', 0)}")
            self.stdout.write(f"DB Agents: {health_result.get('db_agents', 0)}")
            self.stdout.write(f"Total Executions: {health_result.get('total_executions', 0)}")
            self.stdout.write(f"Success Rate: {health_result.get('success_rate', 0):.1%}")

            # Core executor status
            core_status = health_result.get('core_executor_status', {})
            if core_status:
                self.stdout.write('\n🔧 Core Executors:')
                for name, available in core_status.items():
                    status = self.style.SUCCESS('✅') if available else self.style.ERROR('❌')
                    self.stdout.write(f"  {name}: {status}")

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Health check failed: {e}')
            )

    def run_test_execution(self):
        """Run test execution for core agents"""

        self.stdout.write('\n' + self.style.WARNING('🧪 Test Execution'))
        self.stdout.write('-' * 25)

        test_cases = [
            ('income_builder', {
                'task_type': 'analyze_opportunities',
                'user_profile': {
                    'id': 'management_test_user',
                    'skills': ['python', 'ai'],
                    'skill_level': 'intermediate'
                }
            }),
            ('content_creator', {
                'content_type': 'blog_post',
                'topic': 'Management command test',
                'word_count': 300
            }),
            ('payment_processor', {
                'task_type': 'create_invoice',
                'amount': 100.0,
                'client_info': {'name': 'Test Client'}
            })
        ]

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            for agent_name, task_data in test_cases:
                self.stdout.write(f'\n🔄 Testing {agent_name}...')

                try:
                    result = loop.run_until_complete(
                        execute_agent_by_name(agent_name, task_data, user_id='management_test')
                    )

                    if result.status.value == 'completed':
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'  ✅ Success: {len(result.files_created)} files, '
                                f'${result.total_cost:.2f} cost, '
                                f'{result.execution_time_ms}ms'
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR(
                                f'  ❌ Failed: {result.error_message}'
                            )
                        )

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'  ❌ Exception: {e}')
                    )

            self.stdout.write(
                self.style.SUCCESS('\n✅ Test execution completed')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Test execution failed: {e}')
            )

    def handle_output_directory(self):
        """Ensure output directories exist"""

        output_dirs = [
            Path('agent_outputs'),
            Path('income_builder_outputs'),
            Path('content_outputs'),
            Path('payment_outputs')
        ]

        for dir_path in output_dirs:
            dir_path.mkdir(exist_ok=True)

        self.stdout.write('📁 Output directories configured')

    def cleanup_old_executions(self, days=30):
        """Clean up old execution records"""

        cutoff_date = timezone.now() - timezone.timedelta(days=days)

        old_executions = AgentExecution.objects.filter(
            created_at__lt=cutoff_date,
            status__in=['completed', 'failed']
        )

        count = old_executions.count()
        if count > 0:
            old_executions.delete()
            self.stdout.write(
                self.style.SUCCESS(f'🧹 Cleaned up {count} old execution records')
            )
        else:
            self.stdout.write('🧹 No old executions to clean up')

    def export_statistics(self, output_file=None):
        """Export statistics to JSON file"""

        if not output_file:
            output_file = f"executor_stats_{timezone.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            stats = get_execution_statistics()

            # Add database statistics
            db_stats = {
                'total_templates': UnifiedAgentTemplate.objects.count(),
                'active_templates': UnifiedAgentTemplate.objects.filter(is_active=True).count(),
                'total_executions': AgentExecution.objects.count(),
                'recent_executions': AgentExecution.objects.filter(
                    created_at__gte=timezone.now() - timezone.timedelta(hours=24)
                ).count(),
                'export_timestamp': timezone.now().isoformat()
            }

            stats['database_stats'] = db_stats

            # Write to file
            output_path = Path(output_file)
            with open(output_path, 'w') as f:
                json.dump(stats, f, indent=2, default=str)

            self.stdout.write(
                self.style.SUCCESS(f'📊 Statistics exported to {output_path}')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Export failed: {e}')
            )