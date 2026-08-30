"""
Management command to achieve 95%+ reality score across all platform components
"""

import asyncio
import json
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.platform_integration_service import platform_integration_service
from core.reality_check import system_reality_checker


class Command(BaseCommand):
    help = 'Achieve 95%+ reality score by integrating all platform components'

    def add_arguments(self, parser):
        parser.add_argument(
            '--component',
            type=str,
            help='Specific component to integrate (optional)',
            choices=[
                'income_builder', 'revenue_tracking', 'ml_pipeline',
                'neural_orchestra', 'decision_command', 'spider_network',
                'websocket_hub'
            ]
        )
        parser.add_argument(
            '--validate-only',
            action='store_true',
            help='Only run reality check validation without integration'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Starting Platform Integration for 95%+ Reality Score')
        )

        if options.get('validate_only'):
            self.run_reality_check()
        else:
            self.run_integration(options.get('component'))

    def run_reality_check(self):
        """Run reality check to see current state"""
        self.stdout.write('📊 Running Reality Check...')

        try:
            report = system_reality_checker.generate_reality_report()

            self.stdout.write(
                self.style.SUCCESS(
                    f'Current Reality Score: {report["overall_reality_score"]:.1%}'
                )
            )

            # Show component breakdown
            for component, data in report['components'].items():
                status_style = {
                    'real': self.style.SUCCESS,
                    'partial': self.style.WARNING,
                    'mock': self.style.NOTICE,
                    'broken': self.style.ERROR
                }.get(data['status'], self.style.NOTICE)

                self.stdout.write(
                    f"  {component}: {status_style(data['status'])} "
                    f"({data['confidence']:.1%})"
                )

            # Show critical issues
            if report['critical_issues']:
                self.stdout.write('\n🔴 Critical Issues:')
                for issue in report['critical_issues'][:5]:
                    self.stdout.write(f"  • {issue['component']}: {issue['issue']}")

            # Show recommendations
            if report['priority_recommendations']:
                self.stdout.write('\n💡 Priority Recommendations:')
                for rec in report['priority_recommendations']:
                    self.stdout.write(f"  • {rec}")

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Reality check failed: {e}')
            )

    def run_integration(self, specific_component=None):
        """Run platform integration"""
        self.stdout.write('🔧 Starting Platform Integration...')

        try:
            # Run integration
            if specific_component:
                result = asyncio.run(self.integrate_specific_component(specific_component))
            else:
                result = asyncio.run(platform_integration_service.achieve_95_percent_reality())

            # Show results
            self.stdout.write(
                self.style.SUCCESS(
                    f'Integration Complete! Reality Score: {result["overall_reality_score"]:.1%}'
                )
            )

            # Show component results
            for component, data in result['component_results'].items():
                if data['status'] == 'integrated':
                    style = self.style.SUCCESS
                    status_text = f"✅ {data['status']} ({data['reality_score']:.1%})"
                else:
                    style = self.style.ERROR
                    status_text = f"❌ {data['status']}"
                    if 'error' in data:
                        status_text += f" - {data['error']}"

                self.stdout.write(f"  {component}: {style(status_text)}")

            # Run final reality check
            self.stdout.write('\n📊 Final Reality Check...')
            final_report = system_reality_checker.generate_reality_report()

            self.stdout.write(
                self.style.SUCCESS(
                    f'Final Reality Score: {final_report["overall_reality_score"]:.1%}'
                )
            )

            if final_report["overall_reality_score"] >= 0.95:
                self.stdout.write(
                    self.style.SUCCESS('🎯 SUCCESS: 95%+ Reality Score Achieved!')
                )
            elif final_report["overall_reality_score"] >= 0.80:
                self.stdout.write(
                    self.style.WARNING('⚠️  PARTIAL: 80%+ Reality Score Achieved')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('❌ FAILED: Reality Score Below 80%')
                )

            # Save integration report
            report_file = f'/Users/donkeyking/Donkey_Betz/unified-donkey-betz/integration_report_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json'

            with open(report_file, 'w') as f:
                json.dump({
                    'integration_result': result,
                    'final_reality_report': final_report,
                    'timestamp': timezone.now().isoformat()
                }, f, indent=2)

            self.stdout.write(f'📄 Integration report saved: {report_file}')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Integration failed: {e}')
            )
            import traceback
            self.stdout.write(traceback.format_exc())

    async def integrate_specific_component(self, component):
        """Integrate a specific component"""
        integration_methods = {
            'income_builder': platform_integration_service.integrate_income_builder,
            'revenue_tracking': platform_integration_service.integrate_revenue_tracking,
            'ml_pipeline': platform_integration_service.integrate_ml_pipeline,
            'neural_orchestra': platform_integration_service.integrate_neural_orchestra,
            'decision_command': platform_integration_service.integrate_decision_command,
            'spider_network': platform_integration_service.integrate_spider_network,
            'websocket_hub': platform_integration_service.integrate_websocket_hub,
        }

        method = integration_methods.get(component)
        if not method:
            raise ValueError(f"Unknown component: {component}")

        result = await method()

        return {
            'overall_reality_score': result.get('reality_score', 0.0),
            'component_results': {component: result},
            'timestamp': timezone.now().isoformat(),
            'status': 'success' if result.get('status') == 'integrated' else 'failed'
        }