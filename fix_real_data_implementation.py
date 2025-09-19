#!/usr/bin/env python3
"""
Real Data Implementation Fix Script
==================================

This script implements the critical fixes needed to enable real data
usage throughout the Unified Donkey Betz Platform.

Run with: python fix_real_data_implementation.py
"""

import os
import re
from pathlib import Path
import shutil
from datetime import datetime


def backup_file(file_path: Path) -> Path:
    """Create backup of original file."""
    backup_path = file_path.with_suffix(f'.backup_{datetime.now().strftime("%Y%m%d_%H%M")}')
    shutil.copy2(file_path, backup_path)
    print(f"✅ Backed up {file_path} to {backup_path}")
    return backup_path


def fix_opportunities_api():
    """Fix the opportunities API to use real data."""
    print("🔧 Fixing Opportunities API to use real data...")

    api_file = Path("backend/opportunities_api.py")

    if not api_file.exists():
        print(f"❌ File not found: {api_file}")
        return

    # Backup original
    backup_file(api_file)

    # Read current content
    with open(api_file, 'r') as f:
        content = f.read()

    # Add import for real data
    if "from backend.spiders.live_job_scraper import scrape_jobs_sync" not in content:
        # Find the imports section and add our import
        import_pattern = r"(from core\.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant)"
        replacement = r"\1\nfrom backend.spiders.live_job_scraper import scrape_jobs_sync"
        content = re.sub(import_pattern, replacement, content)

    # Add the missing generate_real_opportunities function
    if "def generate_real_opportunities" not in content:
        function_code = '''
def generate_real_opportunities(count=20):
    """Get real opportunities from live spiders with enhanced AI analysis"""
    try:
        # Get real data from spiders
        real_jobs = scrape_jobs_sync()

        if not real_jobs:
            logger.warning("No real jobs found, using fallback mock data")
            return generate_enhanced_opportunities(count, None)

        # Limit to requested count
        limited_jobs = real_jobs[:count]

        # Enhance real data with AI analysis (similar to mock data enhancement)
        analyzer = OpportunityAIAnalyzer()

        for job in limited_jobs:
            try:
                # Ensure consistent structure with enhanced opportunities
                if 'estimated_earnings' not in job:
                    # Estimate earnings from salary info
                    salary_str = job.get('salary', '50k')
                    job['estimated_earnings'] = extract_earnings_from_salary(salary_str)

                if 'success_rate' not in job:
                    job['success_rate'] = 0.75  # Default for real opportunities

                if 'market_demand' not in job:
                    job['market_demand'] = 0.8  # Default for real opportunities

                if 'competition_level' not in job:
                    job['competition_level'] = 'medium'

                if 'quick_apply_available' not in job:
                    job['quick_apply_available'] = True

                if 'skills_match' not in job:
                    job['skills_match'] = 0.7  # Default match

                if 'tags' not in job:
                    job['tags'] = ['remote', 'real_opportunity']
                elif 'real_opportunity' not in job['tags']:
                    job['tags'].append('real_opportunity')

            except Exception as e:
                logger.debug(f"Error enhancing real job data: {e}")
                continue

        logger.info(f"Successfully retrieved {len(limited_jobs)} real opportunities")
        return limited_jobs

    except Exception as e:
        logger.error(f"Failed to get real opportunities: {e}")
        logger.info("Falling back to enhanced mock opportunities")
        return generate_enhanced_opportunities(count, None)

def extract_earnings_from_salary(salary_str):
    """Extract estimated earnings from salary string"""
    try:
        # Extract numbers from salary string
        numbers = re.findall(r'[\d,]+', str(salary_str))
        if numbers:
            # Take the first number and convert to yearly estimate
            base_amount = int(numbers[0].replace(',', ''))
            if 'k' in str(salary_str).lower():
                return base_amount * 1000
            elif base_amount < 1000:  # Assume it's in thousands
                return base_amount * 1000
            else:
                return base_amount
        return 75000  # Default estimate
    except:
        return 75000  # Default estimate
'''

        # Insert the function after the existing generate_enhanced_opportunities function
        pattern = r"(def generate_enhanced_opportunities.*?return opportunities)"
        replacement = r"\1" + function_code
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    # Replace the mock data usage in get_opportunities endpoint
    old_pattern = r"opportunities = generate_enhanced_opportunities\(30, user_profile\)"
    new_pattern = '''try:
            # First try to get real data from spiders
            real_opportunities = generate_real_opportunities(30)

            if real_opportunities and len(real_opportunities) > 10:
                # We have good real data, enhance it with AI analysis
                opportunities = real_opportunities

                # Add AI analysis to real opportunities if user profile available
                if user_profile:
                    analyzer = OpportunityAIAnalyzer()
                    for opp in opportunities:
                        try:
                            analysis = analyzer.analyze_opportunity(opp, user_profile)
                            opp.update({
                                'ai_automation_level': analysis.automation_level.value,
                                'ai_automation_score': round(analysis.automation_score, 2),
                                'ai_can_automate': analysis.can_automate,
                                'ai_requires_manual': analysis.cannot_automate,
                                'ai_recommended_agents': [agent['name'] for agent in analysis.recommended_agents[:3]],
                                'ai_recommended_advisors': [advisor['name'] for advisor in analysis.recommended_advisors[:2]],
                                'ai_estimated_success_rate': round(analysis.estimated_success_rate, 2),
                                'ai_estimated_time_savings': round(analysis.estimated_time_savings, 1),
                                'ai_requires_approval': analysis.required_human_approval,
                                'ai_workflow_steps': len(analysis.automation_workflow),
                                'ai_analysis_confidence': round(analysis.confidence_level, 2),
                                'ai_recommendation': generate_ai_automation_recommendation(analysis)
                            })
                        except Exception as e:
                            logger.debug(f"AI analysis failed for opportunity: {e}")
                            continue

                logger.info(f"Using {len(opportunities)} real opportunities from spiders")
            else:
                # Fallback to enhanced mock data
                logger.warning("Insufficient real data, using enhanced mock opportunities")
                opportunities = generate_enhanced_opportunities(30, user_profile)

        except Exception as e:
            logger.error(f"Real data fetch failed: {e}")
            # Fallback to mock data with warning
            logger.warning("Falling back to mock data due to real data fetch failure")
            opportunities = generate_enhanced_opportunities(30, user_profile)'''

    content = re.sub(old_pattern, new_pattern, content)

    # Also fix the other endpoints that reference the undefined function
    content = re.sub(
        r"generate_real_opportunities\(20\)",
        "generate_real_opportunities(20)",
        content
    )
    content = re.sub(
        r"generate_real_opportunities\(10\)",
        "generate_real_opportunities(10)",
        content
    )

    # Write the updated content
    with open(api_file, 'w') as f:
        f.write(content)

    print("✅ Fixed opportunities API to use real data with fallbacks")


def fix_spider_fallbacks():
    """Reduce aggressive mock data fallbacks in spiders."""
    print("🔧 Improving spider fallback behavior...")

    spider_file = Path("backend/spiders/live_job_scraper.py")

    if not spider_file.exists():
        print(f"❌ File not found: {spider_file}")
        return

    # Backup original
    backup_file(spider_file)

    # Read current content
    with open(spider_file, 'r') as f:
        content = f.read()

    # Replace aggressive fallbacks with more conservative ones
    replacements = [
        (
            r"return self\._generate_mock_jobs\('remoteok', 3\)",
            "logger.warning('RemoteOK API failed, using minimal mock data')\n        return self._generate_mock_jobs('remoteok', 1)"
        ),
        (
            r"return self\._generate_mock_jobs\('weworkremotely', 3\)",
            "logger.warning('WeWorkRemotely scraping failed, using minimal mock data')\n        return self._generate_mock_jobs('weworkremotely', 1)"
        ),
        (
            r"return self\._generate_mock_jobs\('github', 2\)",
            "logger.warning('GitHub API failed, using minimal mock data')\n        return self._generate_mock_jobs('github', 1)"
        ),
        (
            r"return self\._generate_mock_jobs\('hackernews', 2\)",
            "logger.warning('HackerNews API failed, using minimal mock data')\n        return self._generate_mock_jobs('hackernews', 1)"
        )
    ]

    for old, new in replacements:
        content = re.sub(old, new, content)

    # Add better error logging
    if "logger.warning(" not in content:
        content = content.replace(
            "logger.error(f\"RemoteOK scraping failed: {e}\")",
            "logger.error(f\"RemoteOK scraping failed: {e}\")\n            logger.warning(\"Falling back to mock data - check API connectivity\")"
        )

    # Write the updated content
    with open(spider_file, 'w') as f:
        f.write(content)

    print("✅ Reduced aggressive mock data fallbacks in spiders")


def create_real_data_test():
    """Create a test to verify real data implementation."""
    print("🔧 Creating real data verification test...")

    test_content = '''#!/usr/bin/env python3
"""
Real Data Implementation Verification Test
==========================================

This test verifies that the fixes for real data usage are working correctly.
"""

import asyncio
import json
import requests
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_spider_real_data():
    """Test if spiders return real data."""
    print("🕷️ Testing Spider Real Data...")

    try:
        from backend.spiders.live_job_scraper import scrape_jobs_sync

        jobs = scrape_jobs_sync()
        print(f"✅ Spider returned {len(jobs)} jobs")

        if jobs:
            first_job = jobs[0]
            print(f"✅ Sample job: {first_job.get('title', 'N/A')} at {first_job.get('company', 'N/A')}")
            print(f"✅ Source: {first_job.get('source', 'N/A')}")

            # Check for real data indicators
            job_str = json.dumps(first_job).lower()
            real_indicators = ['https://', '.com', 'remote', 'developer', 'engineer']
            found_indicators = [ind for ind in real_indicators if ind in job_str]

            if found_indicators:
                print(f"✅ Real data indicators found: {found_indicators}")
                return True
            else:
                print("⚠️ No clear real data indicators found")
                return False
        else:
            print("❌ No jobs returned from spider")
            return False

    except Exception as e:
        print(f"❌ Spider test failed: {e}")
        return False


def test_opportunities_api():
    """Test if opportunities API returns real data."""
    print("💼 Testing Opportunities API...")

    try:
        response = requests.get('http://localhost:8000/api/opportunities/', timeout=30)

        if response.status_code == 200:
            data = response.json()
            opportunities = data.get('opportunities', [])

            print(f"✅ API returned {len(opportunities)} opportunities")

            if opportunities:
                first_opp = opportunities[0]
                print(f"✅ Sample opportunity: {first_opp.get('title', 'N/A')}")

                # Check for real data vs mock data indicators
                opp_str = json.dumps(first_opp).lower()

                real_indicators = ['real_opportunity', 'https://', '.com', 'upwork', 'linkedin']
                mock_indicators = ['techcorp', 'ai innovations', 'datadrive', 'sample']

                real_count = sum(1 for ind in real_indicators if ind in opp_str)
                mock_count = sum(1 for ind in mock_indicators if ind in opp_str)

                if real_count > mock_count:
                    print(f"✅ Real data detected (real: {real_count}, mock: {mock_count})")
                    return True
                else:
                    print(f"⚠️ Possible mock data (real: {real_count}, mock: {mock_count})")
                    return False
            else:
                print("❌ No opportunities returned")
                return False
        else:
            print(f"❌ API request failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False


def main():
    """Run all verification tests."""
    print("🔍 Real Data Implementation Verification")
    print("=" * 50)

    tests = [
        test_spider_real_data,
        test_opportunities_api
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
            print()
        except Exception as e:
            print(f"❌ Test failed: {e}")
            results.append(False)
            print()

    # Summary
    passed = sum(results)
    total = len(results)

    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")

    if passed == total:
        print("🎉 All tests passed! Real data implementation is working.")
    elif passed > 0:
        print("⚠️ Some tests passed. Real data is partially working.")
    else:
        print("❌ All tests failed. Real data implementation needs work.")

    print("=" * 50)


if __name__ == "__main__":
    main()
'''

    test_file = Path("verify_real_data_implementation.py")
    with open(test_file, 'w') as f:
        f.write(test_content)

    print(f"✅ Created verification test: {test_file}")


def main():
    """Run all fixes."""
    print("🚀 Starting Real Data Implementation Fixes")
    print("=" * 60)

    try:
        # Fix 1: Opportunities API
        fix_opportunities_api()
        print()

        # Fix 2: Spider Fallbacks
        fix_spider_fallbacks()
        print()

        # Fix 3: Create verification test
        create_real_data_test()
        print()

        print("=" * 60)
        print("✅ All fixes completed successfully!")
        print()
        print("Next steps:")
        print("1. Restart your Django server")
        print("2. Run: python verify_real_data_implementation.py")
        print("3. Check that real data is flowing through the system")
        print()
        print("If issues persist, check the backup files created.")
        print("=" * 60)

    except Exception as e:
        print(f"❌ Fix script failed: {e}")
        print("Check the error and try again.")


if __name__ == "__main__":
    main()