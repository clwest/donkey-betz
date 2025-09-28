#!/usr/bin/env python3
"""
Deploy Expanded Spider Army - Test Script
=========================================

This script deploys and tests the expanded spider army with 50+ specialized spiders.
"""

import asyncio
import sys
import os
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ai_core.spiders.spider_army_orchestrator import SpiderArmyOrchestrator, SpiderTarget
from ai_core.spiders.spider_registry import spider_registry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_spider_registry():
    """Test the spider registry functionality"""
    print("🕷️  Testing Spider Registry...")

    # Get registry status
    spider_list = spider_registry.list_spiders()
    spider_count = spider_registry.get_spider_count()

    print(f"📊 Total spider types registered: {spider_count['total']}")
    print(f"🎯 Active implementations: {spider_count['active']}")
    print(f"📝 Placeholder spiders: {spider_count['total'] - spider_count['active']}")
    print(f"📂 Categories: {spider_count['by_category']}")

    # Test spider creation for each category
    test_targets = [SpiderTarget("https://example.com", rate_limit=1.0)]
    test_subscribers = ["test_agent"]
    redis_config = {'host': 'localhost', 'port': 6379, 'db': 0}

    print("\n🧪 Testing spider instantiation...")

    successful_creations = 0
    failed_creations = 0

    for spider_name, spider_info in spider_list.items():
        try:
            spider_instance = spider_registry.create_spider_instance(
                spider_name, f"test_{spider_name}", test_targets, test_subscribers, redis_config
            )
            if spider_instance:
                successful_creations += 1
                print(f"✅ {spider_name}: {spider_info['class']}")
            else:
                failed_creations += 1
                print(f"❌ {spider_name}: Failed to create")
        except Exception as e:
            failed_creations += 1
            print(f"⚠️  {spider_name}: {str(e)[:50]}...")

    print(f"\n📈 Creation Results:")
    print(f"✅ Successful: {successful_creations}")
    print(f"❌ Failed: {failed_creations}")
    print(f"📊 Success Rate: {(successful_creations/spider_count['total']*100):.1f}%")

    return successful_creations >= spider_count['active']


async def test_spider_army_orchestrator():
    """Test the Spider Army Orchestrator with expanded spiders"""
    print("\n🏗️  Testing Spider Army Orchestrator...")

    # Create orchestrator instance
    orchestrator = SpiderArmyOrchestrator()

    # Get expanded army status
    status = orchestrator.get_expanded_spider_army_status()

    print(f"🕷️  Spider Army Expansion Status:")
    print(f"   Total Spider Types: {status['spider_army_expansion']['total_spider_types']}")
    print(f"   Active Implementations: {status['spider_army_expansion']['active_implementations']}")
    print(f"   Placeholder Spiders: {status['spider_army_expansion']['placeholder_spiders']}")
    print(f"   Categories: {status['spider_army_expansion']['categories']}")
    print(f"   Expansion Complete: {status['expansion_complete']}")
    print(f"   Reality Score: {status['reality_score']:.1f}%")

    # Test creating spiders by name
    print("\n🧪 Testing spider creation by name...")

    test_targets = [SpiderTarget("https://test.com", rate_limit=1.0)]
    test_subscribers = ["test_agent"]

    test_spiders = ['toptal', 'guru', 'medium', 'gumroad', 'flexjobs']

    for spider_name in test_spiders:
        try:
            spider = await orchestrator.create_spider_by_name(
                spider_name, f"test_{spider_name}", test_targets, test_subscribers
            )
            if spider:
                print(f"✅ Created {spider_name} spider: {spider.__class__.__name__}")
            else:
                print(f"❌ Failed to create {spider_name} spider")
        except Exception as e:
            print(f"⚠️  Error creating {spider_name}: {str(e)[:50]}...")

    return status['expansion_complete'] and status['reality_score'] >= 95.0


async def test_spider_data_processing():
    """Test spider data processing capabilities"""
    print("\n🔬 Testing Spider Data Processing...")

    # Test data for different spider types
    test_data = {
        'toptal': {
            'content': '<h1>Senior Python Developer</h1><div class="budget">$75/hour</div><div class="skills">Python, Django, React</div>',
            'url': 'https://toptal.com/jobs/12345'
        },
        'medium': {
            'content': '<h1>How to Build AI Apps</h1><div class="claps">1,234 claps</div><div class="partner-program">Member-only</div>',
            'url': 'https://medium.com/article/ai-apps'
        },
        'gumroad': {
            'content': '<h1>React Component Library</h1><div class="price">$49</div><div class="sales">234 sales</div>',
            'url': 'https://gumroad.com/product/react-library'
        }
    }

    redis_config = {'host': 'localhost', 'port': 6379, 'db': 0}
    test_targets = [SpiderTarget("https://test.com", rate_limit=1.0)]
    test_subscribers = ["test_agent"]

    processing_results = []

    for spider_name, data in test_data.items():
        try:
            spider = spider_registry.create_spider_instance(
                spider_name, f"test_{spider_name}", test_targets, test_subscribers, redis_config
            )

            if spider and hasattr(spider, 'process_data'):
                target = SpiderTarget(data['url'], rate_limit=1.0)
                result = await spider.process_data(data, target)

                if result:
                    processing_results.append({
                        'spider': spider_name,
                        'success': True,
                        'data_type': result.data_type,
                        'quality_score': result.quality_score,
                        'tags': len(result.relevance_tags)
                    })
                    print(f"✅ {spider_name}: Processed data successfully (Quality: {result.quality_score:.2f})")
                else:
                    processing_results.append({'spider': spider_name, 'success': False})
                    print(f"❌ {spider_name}: Failed to process data")
            else:
                print(f"⚠️  {spider_name}: No process_data method available")

        except Exception as e:
            print(f"⚠️  {spider_name}: Processing error - {str(e)[:50]}...")
            processing_results.append({'spider': spider_name, 'success': False, 'error': str(e)})

    successful_processing = sum(1 for r in processing_results if r.get('success'))
    print(f"\n📊 Data Processing Results:")
    print(f"✅ Successful: {successful_processing}/{len(test_data)}")
    print(f"📈 Processing Rate: {(successful_processing/len(test_data)*100):.1f}%")

    return successful_processing >= len(test_data) * 0.8  # 80% success rate


async def generate_deployment_report():
    """Generate comprehensive deployment report"""
    print("\n📋 Generating Deployment Report...")

    registry_stats = spider_registry.get_spider_count()
    spider_list = spider_registry.list_spiders()

    report = {
        'deployment_timestamp': asyncio.get_event_loop().time(),
        'spider_army_status': {
            'total_spider_types': registry_stats['total'],
            'active_implementations': registry_stats['active'],
            'placeholder_count': registry_stats['total'] - registry_stats['active'],
            'categories': registry_stats['by_category'],
            'expansion_target_met': registry_stats['total'] >= 50,
            'reality_score': min(95.0, (registry_stats['active'] / 50) * 100)
        },
        'spider_details': spider_list,
        'deployment_success': registry_stats['total'] >= 50 and registry_stats['active'] >= 15
    }

    # Save report
    report_file = project_root / 'spider_army_deployment_report.json'
    import json
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)

    print(f"📄 Report saved to: {report_file}")

    return report


async def main():
    """Main deployment and testing function"""
    print("🚀 Spider Army Expansion Deployment Started")
    print("=" * 60)

    # Test phases
    test_results = []

    # Phase 1: Test Spider Registry
    registry_success = await test_spider_registry()
    test_results.append(('Spider Registry', registry_success))

    # Phase 2: Test Army Orchestrator
    orchestrator_success = await test_spider_army_orchestrator()
    test_results.append(('Army Orchestrator', orchestrator_success))

    # Phase 3: Test Data Processing
    processing_success = await test_spider_data_processing()
    test_results.append(('Data Processing', processing_success))

    # Phase 4: Generate Report
    report = await generate_deployment_report()

    # Final Results
    print("\n" + "=" * 60)
    print("🎯 SPIDER ARMY EXPANSION RESULTS")
    print("=" * 60)

    for test_name, success in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:20} {status}")

    overall_success = all(result[1] for result in test_results)

    print(f"\n🕷️  Total Spider Types: {report['spider_army_status']['total_spider_types']}")
    print(f"🎯 Active Implementations: {report['spider_army_status']['active_implementations']}")
    print(f"📊 Reality Score: {report['spider_army_status']['reality_score']:.1f}%")
    print(f"🏆 Expansion Target Met: {report['spider_army_status']['expansion_target_met']}")

    print(f"\n🚀 OVERALL DEPLOYMENT: {'✅ SUCCESS' if overall_success else '❌ FAILED'}")

    if overall_success and report['spider_army_status']['reality_score'] >= 95.0:
        print("\n🎉 SPIDER ARMY EXPANSION COMPLETE!")
        print("🕷️  50+ Specialized spiders ready for deployment")
        print("🔥 95%+ Reality score achieved")
        print("⚡ Intelligence gathering capacity massively expanded")
        return 0
    else:
        print("\n⚠️  Spider Army expansion needs attention")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Deployment failed with error: {e}")
        sys.exit(1)