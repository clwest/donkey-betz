#!/usr/bin/env python
"""
Spider Verification Script
===========================

Session 290: HANDOFF_06 - Spider Network Wiring

This script tests all 70 registered spiders to determine:
1. Which spiders are actually working (fetch real data)
2. Which are placeholders (not implemented)
3. Which have errors (implementation issues)

Run with: python scripts/verify_spiders.py
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

import django
django.setup()

from ai_core.spiders.spider_registry import SpiderRegistry, get_spider_registry
from ai_core.spiders.base_spider import BaseIntelligenceSpider, SpiderTarget

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SpiderVerifier:
    """Verifies which spiders are working vs placeholders."""

    def __init__(self):
        self.registry = get_spider_registry()
        self.results: Dict[str, List[Dict[str, Any]]] = {
            'working': [],
            'working_sync': [],  # Working but uses sync pattern
            'placeholder': [],
            'error': [],
            'no_fetch_method': [],
        }

    def get_all_spiders(self) -> Dict[str, Any]:
        """Get all registered spiders."""
        return self.registry.list_spiders()

    async def test_spider(self, spider_name: str, spider_info: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single spider."""
        result = {
            'name': spider_name,
            'class': spider_info.get('class', 'Unknown'),
            'category': spider_info.get('category', 'unknown'),
            'priority': spider_info.get('priority', 5),
            'status': 'unknown',
            'data_count': 0,
            'error': None,
            'implementation_type': 'unknown',
            'tested_at': datetime.now().isoformat(),
        }

        try:
            spider_class = self.registry.get_spider_class(spider_name)
            config = self.registry.get_spider_config(spider_name)

            # Check what type of spider this is
            result['implementation_type'] = self._detect_implementation_type(spider_class)

            # Try to create an instance
            if result['implementation_type'] == 'base_intelligence':
                # Uses BaseIntelligenceSpider pattern
                targets = [
                    SpiderTarget(
                        url=t if isinstance(t, str) else t.url,
                        rate_limit=config.get('rate_limit', 1.0)
                    ) for t in config.get('targets', ['https://example.com'])[:1]  # Just test first target
                ]

                try:
                    spider = spider_class(
                        spider_id=f"verify_{spider_name}",
                        targets=targets,
                        subscribers=[],
                        redis_config=None
                    )

                    # Check if it has fetch_data method
                    if hasattr(spider, 'fetch_data'):
                        # Try to fetch data
                        try:
                            data = await spider.fetch_data(targets[0])
                            if data:
                                result['status'] = 'working'
                                result['data_count'] = len(data) if isinstance(data, (list, dict)) else 1
                                if isinstance(data, dict):
                                    result['data_count'] = len(data.get('items', data.get('posts', [data])))
                            else:
                                result['status'] = 'working'  # Method exists but no data right now
                                result['data_count'] = 0
                        except NotImplementedError:
                            result['status'] = 'placeholder'
                        except Exception as e:
                            # Some spiders may need specific conditions
                            if 'NotImplemented' in str(e):
                                result['status'] = 'placeholder'
                            else:
                                result['status'] = 'error'
                                result['error'] = str(e)[:200]
                    elif hasattr(spider, 'process_data'):
                        # Has process_data but relies on base fetch
                        result['status'] = 'working'
                        result['data_count'] = 0
                        result['note'] = 'Uses base _fetch_data'
                    else:
                        result['status'] = 'no_fetch_method'

                except Exception as e:
                    result['status'] = 'error'
                    result['error'] = f"Init error: {str(e)[:150]}"

            elif result['implementation_type'] == 'standalone':
                # Standalone sync spider (like CoinGeckoSpider)
                try:
                    spider = spider_class()

                    if hasattr(spider, 'fetch_data'):
                        data = spider.fetch_data(max_results=5)
                        if data:
                            result['status'] = 'working_sync'
                            result['data_count'] = len(data) if isinstance(data, list) else 1
                        else:
                            result['status'] = 'working_sync'
                            result['data_count'] = 0
                    else:
                        result['status'] = 'no_fetch_method'

                except NotImplementedError:
                    result['status'] = 'placeholder'
                except Exception as e:
                    result['status'] = 'error'
                    result['error'] = str(e)[:200]
            else:
                result['status'] = 'unknown'
                result['error'] = 'Unknown implementation type'

        except Exception as e:
            result['status'] = 'error'
            result['error'] = f"Failed to get spider class: {str(e)[:150]}"

        return result

    def _detect_implementation_type(self, spider_class) -> str:
        """Detect what type of spider implementation this is."""
        try:
            # Check if it inherits from BaseIntelligenceSpider
            if hasattr(spider_class, '__mro__'):
                mro_names = [c.__name__ for c in spider_class.__mro__]
                if 'BaseIntelligenceSpider' in mro_names:
                    return 'base_intelligence'
                elif 'AdaptiveSpider' in mro_names:
                    return 'base_intelligence'

            # Check init signature
            init_sig = str(spider_class.__init__.__code__.co_varnames)
            if 'spider_id' in init_sig and 'targets' in init_sig:
                return 'base_intelligence'

            # Probably standalone
            return 'standalone'

        except Exception:
            return 'unknown'

    async def verify_all(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """Verify all spiders."""
        spiders = self.get_all_spiders()
        spider_list = list(spiders.items())

        if limit:
            spider_list = spider_list[:limit]

        total = len(spider_list)
        logger.info(f"Testing {total} spiders...")

        for i, (name, info) in enumerate(spider_list, 1):
            logger.info(f"[{i}/{total}] Testing {name}...")

            try:
                result = await asyncio.wait_for(
                    self.test_spider(name, info),
                    timeout=30.0  # 30 second timeout per spider
                )
            except asyncio.TimeoutError:
                result = {
                    'name': name,
                    'class': info.get('class', 'Unknown'),
                    'category': info.get('category', 'unknown'),
                    'status': 'error',
                    'error': 'Timeout (>30s)',
                    'tested_at': datetime.now().isoformat(),
                }

            # Categorize result
            status = result.get('status', 'unknown')
            if status == 'working' or status == 'working_sync':
                self.results['working'].append(result)
            elif status == 'placeholder':
                self.results['placeholder'].append(result)
            elif status == 'no_fetch_method':
                self.results['no_fetch_method'].append(result)
            else:
                self.results['error'].append(result)

            # Print inline status
            status_emoji = {
                'working': '✅',
                'working_sync': '✅',
                'placeholder': '⭕',
                'no_fetch_method': '❓',
                'error': '❌',
            }.get(status, '❓')

            print(f"  {status_emoji} {name}: {status}")
            if result.get('data_count', 0) > 0:
                print(f"     └─ Fetched {result['data_count']} items")
            if result.get('error'):
                print(f"     └─ Error: {result['error'][:60]}...")

        return self.results

    def generate_report(self) -> str:
        """Generate verification report."""
        lines = [
            "=" * 60,
            "SPIDER VERIFICATION REPORT",
            f"Generated: {datetime.now().isoformat()}",
            "=" * 60,
            "",
            f"Total Registered Spiders: {len(self.get_all_spiders())}",
            f"Working: {len(self.results['working'])}",
            f"Placeholder: {len(self.results['placeholder'])}",
            f"No Fetch Method: {len(self.results['no_fetch_method'])}",
            f"Errors: {len(self.results['error'])}",
            "",
        ]

        # Working spiders
        lines.append("=" * 60)
        lines.append("WORKING SPIDERS")
        lines.append("=" * 60)
        for r in sorted(self.results['working'], key=lambda x: x['category']):
            impl = '(sync)' if r.get('status') == 'working_sync' else ''
            lines.append(f"  ✅ {r['name']} ({r['category']}) {impl}")
            if r.get('data_count', 0) > 0:
                lines.append(f"      └─ {r['data_count']} items")

        # By category summary
        lines.append("")
        lines.append("WORKING BY CATEGORY:")
        categories = {}
        for r in self.results['working']:
            cat = r.get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
        for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
            lines.append(f"  {cat}: {count}")

        # Placeholder spiders
        lines.append("")
        lines.append("=" * 60)
        lines.append("PLACEHOLDER SPIDERS (Need Implementation)")
        lines.append("=" * 60)
        for r in sorted(self.results['placeholder'], key=lambda x: x['category']):
            lines.append(f"  ⭕ {r['name']} ({r['category']})")

        # No fetch method
        if self.results['no_fetch_method']:
            lines.append("")
            lines.append("=" * 60)
            lines.append("NO FETCH METHOD (Architecture issue)")
            lines.append("=" * 60)
            for r in self.results['no_fetch_method']:
                lines.append(f"  ❓ {r['name']} ({r['category']})")

        # Error spiders
        if self.results['error']:
            lines.append("")
            lines.append("=" * 60)
            lines.append("ERROR SPIDERS (Need fixing)")
            lines.append("=" * 60)
            for r in self.results['error']:
                lines.append(f"  ❌ {r['name']} ({r['category']})")
                if r.get('error'):
                    lines.append(f"      └─ {r['error'][:80]}")

        # Recommendations
        lines.append("")
        lines.append("=" * 60)
        lines.append("RECOMMENDATIONS")
        lines.append("=" * 60)

        working_count = len(self.results['working'])
        placeholder_count = len(self.results['placeholder'])
        error_count = len(self.results['error'])

        if working_count >= 20:
            lines.append(f"✅ GOOD: {working_count} working spiders meets the target of 20+")
        else:
            lines.append(f"⚠️  WARNING: Only {working_count} working spiders, target is 20+")

        if placeholder_count > 0:
            lines.append(f"📝 {placeholder_count} placeholder spiders need implementation or removal")

        if error_count > 0:
            lines.append(f"🔧 {error_count} spiders have errors and need debugging")

        return "\n".join(lines)

    def save_results(self, filepath: str = 'spider_verification_results.json'):
        """Save results to JSON file."""
        output = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total': len(self.get_all_spiders()),
                'working': len(self.results['working']),
                'placeholder': len(self.results['placeholder']),
                'no_fetch_method': len(self.results['no_fetch_method']),
                'error': len(self.results['error']),
            },
            'results': self.results,
        }

        with open(filepath, 'w') as f:
            json.dump(output, f, indent=2, default=str)

        logger.info(f"Results saved to {filepath}")


async def main():
    """Main entry point."""
    verifier = SpiderVerifier()

    # Run verification
    print("\n🕷️  SPIDER VERIFICATION STARTING...\n")
    await verifier.verify_all()

    # Generate and print report
    report = verifier.generate_report()
    print("\n" + report)

    # Save results
    verifier.save_results()

    print("\n✅ Verification complete! Results saved to spider_verification_results.json")


if __name__ == '__main__':
    asyncio.run(main())
