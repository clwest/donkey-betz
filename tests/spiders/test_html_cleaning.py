#!/usr/bin/env python3
"""
Test HTML cleaning function
"""
import sys
import os
import django

# Django setup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from ai_core.spiders.freelance_opportunity_spider import FreelanceOpportunitySpider

def test_html_cleaning():
    """Test the HTML cleaning with problematic text"""

    spider = FreelanceOpportunitySpider()

    # Test cases with problematic HTML
    test_cases = [
        {
            'name': 'HTML entities',
            'input': "If you&apos;re a passionate communicator who&rsquo;s ready to grow",
            'expected_fixes': ['apostrophes', 'quotes']
        },
        {
            'name': 'HTML tags + entities',
            'input': '<p>We&apos;re looking for someone who&nbsp;can help us <strong>grow</strong>!</p>',
            'expected_fixes': ['HTML tags', 'entities', 'non-breaking spaces']
        },
        {
            'name': 'Complex HTML',
            'input': '<h2>About Us</h2><p><strong>Company&trade;</strong> is looking for &quot;talented&quot; developers&#8230;</p>',
            'expected_fixes': ['headers', 'quotes', 'ellipsis', 'trademark']
        }
    ]

    print("🧪 TESTING HTML CLEANING FUNCTION")
    print("=" * 50)

    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test['name']}")
        print(f"Input:  {test['input']}")

        cleaned = spider._clean_html_description(test['input'])
        print(f"Output: {cleaned}")

        # Check if common issues are fixed
        issues = []
        if '&' in cleaned and ';' in cleaned:
            issues.append("Still contains HTML entities")
        if '<' in cleaned and '>' in cleaned:
            issues.append("Still contains HTML tags")
        if 'apos' in cleaned or 'rsquo' in cleaned or 'quot' in cleaned:
            issues.append("Still contains entity names")

        if issues:
            print(f"❌ Issues: {', '.join(issues)}")
        else:
            print("✅ Clean!")

    print("\n" + "=" * 50)
    print("🎯 TESTING REAL PROBLEMATIC EXAMPLE:")

    # Test the actual problematic text from the job
    real_example = """Imagine waking up each day excited for work, knowing your words, support, and ideas help shape the futures of design learners across the globe. If you&apos;re a passionate communicator who thrives in both structured systems and creative writing and who is curious about how great design improves lives, then we have an exhilarating opportunity for you at the IxDF (Interaction Design Foundation)! We&apos;re now looking for an Admin and Support Specialist who&apos;s also ready to gr..."""

    print("Real example input:")
    print(real_example[:100] + "...")

    cleaned_real = spider._clean_html_description(real_example)
    print("\nCleaned output:")
    print(cleaned_real[:100] + "...")

    # Check for improvements
    print(f"\n📊 Analysis:")
    print(f"Original apostrophes: {real_example.count('&apos;')}")
    print(f"Cleaned apostrophes: {cleaned_real.count('&apos;')}")
    print(f"Proper apostrophes: {cleaned_real.count(chr(39))}")  # Regular apostrophe

    if '&apos;' not in cleaned_real:
        print("✅ SUCCESS: HTML entities removed!")
    else:
        print("❌ FAILED: Still contains HTML entities")

if __name__ == "__main__":
    test_html_cleaning()