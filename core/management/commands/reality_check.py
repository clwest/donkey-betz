"""
Django Management Command for System Reality Checking
===================================================

This management command provides CLI access to the System Reality Self-Awareness Engine.
It allows administrators to check platform reality status, generate reports,
and monitor system health from the command line.

Usage:
    python manage.py reality_check --all
    python manage.py reality_check --component income_builder
    python manage.py reality_check --report --output /path/to/report.json
    python manage.py reality_check --trace --flow opportunity_pipeline
    python manage.py reality_check --dashboard --open
"""

import json
import os
import webbrowser
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.conf import settings

from core.reality_check import system_reality_checker, ComponentType
from core.data_flow_tracer import data_flow_tracer, FlowType
from core.truth_dashboard import truth_dashboard


class Command(BaseCommand):
    """Django management command for reality checking"""

    help = 'Check platform reality status and generate reports'

    def add_arguments(self, parser):
        """Add command line arguments"""
        parser.add_argument(
            '--all',
            action='store_true',
            help='Check all components'
        )

        parser.add_argument(
            '--component',
            type=str,
            help='Check specific component (e.g., income_builder, database)'
        )

        parser.add_argument(
            '--report',
            action='store_true',
            help='Generate comprehensive reality report'
        )

        parser.add_argument(
            '--dashboard',
            action='store_true',
            help='Generate truth dashboard'
        )

        parser.add_argument(
            '--trace',
            action='store_true',
            help='Test data flow tracing'
        )

        parser.add_argument(
            '--flow',
            type=str,
            choices=['opportunity_pipeline', 'revenue_pipeline', 'websocket_pipeline'],
            help='Specific flow to trace'
        )

        parser.add_argument(
            '--output',
            type=str,
            help='Output file path for reports'
        )

        parser.add_argument(
            '--format',
            type=str,
            choices=['json', 'text', 'html'],
            default='text',
            help='Output format'
        )

        parser.add_argument(
            '--open',
            action='store_true',
            help='Open HTML reports in browser'
        )

        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Verbose output with details'
        )

    def handle(self, *args, **options):
        """Handle the command"""
        self.verbosity = options.get('verbosity', 1)
        self.verbose = options.get('verbose', False)

        if options['all']:
            self.check_all_components(options)
        elif options['component']:
            self.check_component(options['component'], options)
        elif options['report']:
            self.generate_report(options)
        elif options['dashboard']:
            self.generate_dashboard(options)
        elif options['trace']:
            self.test_tracing(options)
        else:
            self.print_help()

    def check_all_components(self, options):
        """Check all platform components"""
        self.stdout.write(self.style.SUCCESS("🎯 Checking All Platform Components"))
        self.stdout.write("=" * 50)

        try:
            results = system_reality_checker.check_all_components()

            # Summary statistics
            total_components = len(results)
            real_count = sum(1 for status in results.values() if status.status.value == 'real')
            partial_count = sum(1 for status in results.values() if status.status.value == 'partial')
            mock_count = sum(1 for status in results.values() if status.status.value == 'mock')
            broken_count = sum(1 for status in results.values() if status.status.value == 'broken')

            # Overall score
            overall_confidence = sum(status.confidence for status in results.values()) / total_components

            self.stdout.write(f"\n📊 Summary:")
            self.stdout.write(f"   Total Components: {total_components}")
            self.stdout.write(f"   Real: {real_count} | Partial: {partial_count} | Mock: {mock_count} | Broken: {broken_count}")
            self.stdout.write(f"   Overall Confidence: {overall_confidence:.1%}")

            # Component details
            self.stdout.write(f"\n🔍 Component Details:")
            for component_type, status in results.items():
                icon = self._get_status_icon(status.status.value)
                confidence_bar = self._get_confidence_bar(status.confidence)

                self.stdout.write(f"   {icon} {component_type.value:<20} {confidence_bar} {status.confidence:.1%}")

                if self.verbose:
                    if status.issues_found:
                        for issue in status.issues_found[:2]:  # Show top 2 issues
                            self.stdout.write(f"     ⚠️  {issue}")
                    if status.recommendations:
                        for rec in status.recommendations[:1]:  # Show top recommendation
                            self.stdout.write(f"     💡 {rec}")

            # Output to file if requested
            if options.get('output'):
                self._save_results(results, options)

        except Exception as e:
            raise CommandError(f"Error checking components: {str(e)}")

    def check_component(self, component_name, options):
        """Check a specific component"""
        self.stdout.write(self.style.SUCCESS(f"🔍 Checking Component: {component_name}"))
        self.stdout.write("=" * 50)

        try:
            # Find component type
            component_type = None
            for ct in ComponentType:
                if ct.value == component_name.lower():
                    component_type = ct
                    break

            if not component_type:
                raise CommandError(f"Unknown component: {component_name}")

            # Check component
            checker_method = system_reality_checker.component_checkers.get(component_type)
            if not checker_method:
                raise CommandError(f"No checker available for: {component_name}")

            status = checker_method()

            # Display results
            icon = self._get_status_icon(status.status.value)
            self.stdout.write(f"\n{icon} Status: {status.status.value.upper()}")
            self.stdout.write(f"📊 Confidence: {status.confidence:.1%}")
            self.stdout.write(f"🔍 Checks Performed: {len(status.checks_performed)}")

            if status.details:
                self.stdout.write(f"\n📋 Details:")
                for key, value in status.details.items():
                    self.stdout.write(f"   {key}: {value}")

            if status.issues_found:
                self.stdout.write(f"\n⚠️  Issues Found ({len(status.issues_found)}):")
                for issue in status.issues_found:
                    self.stdout.write(f"   • {issue}")

            if status.recommendations:
                self.stdout.write(f"\n💡 Recommendations ({len(status.recommendations)}):")
                for rec in status.recommendations:
                    self.stdout.write(f"   • {rec}")

        except Exception as e:
            raise CommandError(f"Error checking component {component_name}: {str(e)}")

    def generate_report(self, options):
        """Generate comprehensive reality report"""
        self.stdout.write(self.style.SUCCESS("📊 Generating Reality Report"))
        self.stdout.write("=" * 50)

        try:
            report = system_reality_checker.generate_reality_report()

            # Display summary
            self.stdout.write(f"\n🎯 Platform Reality Score: {report['overall_reality_score']:.1%}")
            self.stdout.write(f"📈 Status: {report['overall_status'].replace('_', ' ').title()}")

            summary = report['summary']
            self.stdout.write(f"\n📊 Summary:")
            self.stdout.write(f"   Components: {summary['total_components']}")
            self.stdout.write(f"   Real: {summary['real_components']}")
            self.stdout.write(f"   Partial: {summary['partial_components']}")
            self.stdout.write(f"   Mock: {summary['mock_components']}")
            self.stdout.write(f"   Broken: {summary['broken_components']}")
            self.stdout.write(f"   Issues: {summary['total_issues']}")
            self.stdout.write(f"   Recommendations: {summary['total_recommendations']}")

            # Critical issues
            if report['critical_issues']:
                self.stdout.write(f"\n🚨 Critical Issues:")
                for issue in report['critical_issues'][:5]:  # Top 5
                    self.stdout.write(f"   • {issue['component']}: {issue['issue']}")

            # Priority recommendations
            if report['priority_recommendations']:
                self.stdout.write(f"\n🎯 Priority Actions:")
                for rec in report['priority_recommendations'][:5]:  # Top 5
                    self.stdout.write(f"   • {rec}")

            # Save report if requested
            if options.get('output'):
                output_path = options['output']
                with open(output_path, 'w') as f:
                    json.dump(report, f, indent=2, default=str)
                self.stdout.write(f"\n💾 Report saved to: {output_path}")

        except Exception as e:
            raise CommandError(f"Error generating report: {str(e)}")

    def generate_dashboard(self, options):
        """Generate truth dashboard"""
        self.stdout.write(self.style.SUCCESS("📈 Generating Truth Dashboard"))
        self.stdout.write("=" * 50)

        try:
            if options.get('format') == 'html':
                # Generate HTML dashboard
                html_content = truth_dashboard.generate_html_report()

                output_path = options.get('output', 'truth_dashboard.html')
                with open(output_path, 'w') as f:
                    f.write(html_content)

                self.stdout.write(f"💾 HTML dashboard saved to: {output_path}")

                if options.get('open'):
                    webbrowser.open(f'file://{os.path.abspath(output_path)}')
                    self.stdout.write("🌐 Dashboard opened in browser")
            else:
                # Generate JSON dashboard
                dashboard_data = truth_dashboard.generate_dashboard_data()

                # Display summary
                health = dashboard_data['overall_health']
                self.stdout.write(f"\n🎯 Platform Health: {health['status'].upper()} ({health['score']:.1%})")
                self.stdout.write(f"💬 {health['message']}")

                # Component map summary
                component_map = dashboard_data['component_map']
                self.stdout.write(f"\n📊 Component Status:")
                for component in component_map[:10]:  # Top 10
                    icon = component['icon']
                    name = component['name']
                    status = component['status']
                    self.stdout.write(f"   {icon} {name:<25} {status}")

                # Save JSON if requested
                if options.get('output'):
                    output_path = options['output']
                    with open(output_path, 'w') as f:
                        json.dump(dashboard_data, f, indent=2, default=str)
                    self.stdout.write(f"\n💾 Dashboard data saved to: {output_path}")

        except Exception as e:
            raise CommandError(f"Error generating dashboard: {str(e)}")

    def test_tracing(self, options):
        """Test data flow tracing"""
        self.stdout.write(self.style.SUCCESS("🔍 Testing Data Flow Tracing"))
        self.stdout.write("=" * 50)

        try:
            flow_type_str = options.get('flow', 'opportunity_pipeline')

            # Map string to enum
            flow_type_map = {
                'opportunity_pipeline': FlowType.OPPORTUNITY_PIPELINE,
                'revenue_pipeline': FlowType.REVENUE_PIPELINE,
                'websocket_pipeline': FlowType.WEBSOCKET_PIPELINE
            }

            flow_type = flow_type_map.get(flow_type_str)
            if not flow_type:
                raise CommandError(f"Unknown flow type: {flow_type_str}")

            self.stdout.write(f"\n🔄 Tracing {flow_type_str}...")

            # Test trace based on flow type
            if flow_type == FlowType.OPPORTUNITY_PIPELINE:
                test_data = {
                    'id': 'cli_test_001',
                    'title': 'CLI Test Opportunity',
                    'platform': 'test'
                }
                trace_id = data_flow_tracer.trace_opportunity_pipeline(test_data)

            elif flow_type == FlowType.REVENUE_PIPELINE:
                test_data = {
                    'id': 'cli_revenue_001',
                    'opportunity_id': 'test_opp',
                    'amount': 250.0
                }
                trace_id = data_flow_tracer.trace_revenue_pipeline(test_data)

            else:  # WebSocket pipeline
                test_data = {
                    'type': 'cli_test',
                    'data': {'key': 'value'}
                }
                trace_id = data_flow_tracer.trace_websocket_pipeline(test_data, 'income_builder')

            # Get completed trace
            completed_trace = data_flow_tracer.get_trace_by_id(trace_id)

            if completed_trace:
                self.stdout.write(f"✅ Trace completed successfully!")
                self.stdout.write(f"   Trace ID: {trace_id}")
                self.stdout.write(f"   Success: {completed_trace.success}")
                self.stdout.write(f"   Processing Time: {completed_trace.total_processing_time_ms:.1f}ms")
                self.stdout.write(f"   Stages: {len(completed_trace.trace_points)}")

                if self.verbose:
                    self.stdout.write(f"\n📋 Trace Points:")
                    for point in completed_trace.trace_points:
                        status_icon = "✅" if point.success else "❌"
                        self.stdout.write(f"   {status_icon} {point.stage.value} @ {point.component} ({point.processing_time_ms:.1f}ms)")

                if completed_trace.issues:
                    self.stdout.write(f"\n⚠️  Issues:")
                    for issue in completed_trace.issues:
                        self.stdout.write(f"   • {issue}")

            # Get pipeline health
            health = data_flow_tracer.get_pipeline_health(flow_type)
            if health['status'] != 'no_data':
                self.stdout.write(f"\n📊 Pipeline Health: {health['status']}")
                if 'metrics' in health:
                    metrics = health['metrics']
                    self.stdout.write(f"   Success Rate: {metrics['success_rate']:.1%}")
                    self.stdout.write(f"   Total Traces: {metrics['total_traces']}")

        except Exception as e:
            raise CommandError(f"Error testing tracing: {str(e)}")

    def print_help(self):
        """Print usage help"""
        self.stdout.write(self.style.SUCCESS("🎯 System Reality Self-Awareness Engine"))
        self.stdout.write("=" * 50)
        self.stdout.write("\nUsage examples:")
        self.stdout.write("  python manage.py reality_check --all")
        self.stdout.write("  python manage.py reality_check --component income_builder")
        self.stdout.write("  python manage.py reality_check --report --output report.json")
        self.stdout.write("  python manage.py reality_check --dashboard --format html --open")
        self.stdout.write("  python manage.py reality_check --trace --flow opportunity_pipeline")
        self.stdout.write("\nFor detailed help: python manage.py reality_check --help")

    def _get_status_icon(self, status):
        """Get emoji icon for status"""
        icons = {
            'real': '✅',
            'partial': '⚠️',
            'mock': '🎭',
            'broken': '❌',
            'unknown': '❓'
        }
        return icons.get(status, '❓')

    def _get_confidence_bar(self, confidence):
        """Get ASCII confidence bar"""
        bar_length = 10
        filled = int(confidence * bar_length)
        bar = '█' * filled + '░' * (bar_length - filled)
        return f"[{bar}]"

    def _save_results(self, results, options):
        """Save results to file"""
        output_path = options['output']
        format_type = options.get('format', 'json')

        if format_type == 'json':
            # Convert to serializable format
            serializable_results = {}
            for component_type, status in results.items():
                serializable_results[component_type.value] = {
                    'status': status.status.value,
                    'confidence': status.confidence,
                    'details': status.details,
                    'checks_performed': status.checks_performed,
                    'issues_found': status.issues_found,
                    'recommendations': status.recommendations,
                    'last_checked': status.last_checked.isoformat()
                }

            with open(output_path, 'w') as f:
                json.dump(serializable_results, f, indent=2)

        elif format_type == 'text':
            with open(output_path, 'w') as f:
                f.write("System Reality Check Results\n")
                f.write("=" * 30 + "\n\n")

                for component_type, status in results.items():
                    f.write(f"{component_type.value}: {status.status.value} ({status.confidence:.1%})\n")
                    if status.issues_found:
                        f.write(f"  Issues: {', '.join(status.issues_found[:2])}\n")
                    f.write("\n")

        self.stdout.write(f"💾 Results saved to: {output_path}")