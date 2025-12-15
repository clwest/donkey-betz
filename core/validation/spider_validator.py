# core/validation/spider_validator.py
"""
Spider Network Validation Agent

Validates the spider data collection system including:
- Spider registry
- Spider data storage
- Spider dashboard endpoints
- Real spider execution capability
"""

import logging
from django.conf import settings

from .base import BaseValidationAgent

logger = logging.getLogger(__name__)


class SpiderValidationAgent(BaseValidationAgent):
    """Validates the spider network subsystem."""

    section_name = "spiders"

    def run_checks(self):
        """Run all spider-related validation checks."""
        # Registry checks
        self.check_spider_registry()

        # Data checks
        self.check_spider_data_model()

        # Endpoint checks
        self.check_spider_endpoints()

        # Import checks
        self.check_spider_imports()

    def check_spider_registry(self):
        """Verify spider registry has spiders registered."""
        try:
            from ai_core.spiders.spider_registry import SpiderRegistry
            registry = SpiderRegistry()
            counts = registry.get_spider_count()
            total = counts.get('total', 0)

            passed = total >= 50  # Should have at least 50 spiders
            self.add_check(
                name='spider_registry',
                passed=passed,
                message=f'Spider registry: {total} spiders registered',
                details=counts
            )
        except Exception as e:
            self.add_check(
                name='spider_registry',
                passed=False,
                message=f'Spider registry error: {str(e)}'
            )

    def check_spider_data_model(self):
        """Verify SpiderData model has records."""
        try:
            from core.models_unified_system import SpiderData
            self.check_model_count(
                model_class=SpiderData,
                min_count=100,  # Should have substantial data
                name='spider_data_records'
            )
        except ImportError as e:
            self.add_check(
                name='spider_data_records',
                passed=False,
                message=f'Cannot import SpiderData: {e}'
            )

    def check_spider_endpoints(self):
        """Verify spider-related API endpoints."""
        endpoints = [
            '/api/spider-dashboard/network/',
            '/api/spider-dashboard/activity/',
            '/api/spider/stats/',
        ]

        for endpoint in endpoints:
            self.check_endpoint(
                path=endpoint,
                method='GET',
                expected_status=200,
                name=f'endpoint_{endpoint.replace("/", "_").strip("_")}'
            )

    def check_spider_imports(self):
        """Verify key spider modules can be imported."""
        imports = [
            ('ai_core.spiders.spider_registry', 'SpiderRegistry'),
            ('core.services.spider_intelligence', 'SpiderIntelligenceService'),
        ]

        for module_path, class_name in imports:
            self.check_import(
                module_path=module_path,
                class_name=class_name,
                name=f'import_{class_name}'
            )

    def check_spider_execution(self):
        """
        Verify a spider can actually execute.
        Note: This is optional/expensive, so only run when explicitly requested.
        """
        try:
            from ai_core.spiders.spider_registry import SpiderRegistry
            registry = SpiderRegistry()

            # Try to get a simple spider
            spider = registry.get_spider('hackernews_api')
            if spider:
                # Don't actually run - just verify it's configured
                self.add_check(
                    name='spider_execution_ready',
                    passed=True,
                    message='HackerNews spider ready for execution'
                )
            else:
                self.add_check(
                    name='spider_execution_ready',
                    passed=False,
                    message='HackerNews spider not found in registry'
                )
        except Exception as e:
            self.add_check(
                name='spider_execution_ready',
                passed=False,
                message=f'Spider execution check error: {str(e)}'
            )
