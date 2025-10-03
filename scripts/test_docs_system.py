#!/usr/bin/env python3
"""
Documentation System Validation Tests

This script validates that the /docs/ system successfully maintains context
and enables seamless handoffs between Claude sessions.

Test Categories:
1. Documentation Completeness - All required files exist
2. Session Continuity - Handoffs and reports are complete
3. Content Quality - Key information is present
4. Navigation - Links and structure are valid

Usage:
    python scripts/test_docs_system.py
    python scripts/test_docs_system.py --verbose
    python scripts/test_docs_system.py --json
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Tuple


class DocSystemTester:
    """Test suite for documentation system validation"""

    def __init__(self, base_dir: str = None, verbose: bool = False):
        if base_dir is None:
            # Assume we're in scripts/ directory
            self.base_dir = Path(__file__).parent.parent
        else:
            self.base_dir = Path(base_dir)

        self.docs_dir = self.base_dir / 'docs'
        self.verbose = verbose
        self.results = {
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'tests': []
        }

    def log(self, message: str, level: str = 'INFO'):
        """Log message if verbose mode enabled"""
        if self.verbose or level in ['ERROR', 'WARNING']:
            prefix = {
                'INFO': '✓',
                'WARNING': '⚠',
                'ERROR': '✗',
                'SUCCESS': '✅'
            }.get(level, '•')
            print(f"{prefix} {message}")

    def record_test(self, name: str, passed: bool, message: str = "", details: str = ""):
        """Record test result"""
        self.results['tests'].append({
            'name': name,
            'passed': passed,
            'message': message,
            'details': details
        })

        if passed:
            self.results['passed'] += 1
            self.log(f"{name}: PASSED - {message}", 'SUCCESS')
        else:
            self.results['failed'] += 1
            self.log(f"{name}: FAILED - {message}", 'ERROR')
            if details and self.verbose:
                self.log(f"  Details: {details}", 'INFO')

    def test_index_exists(self) -> Tuple[bool, str]:
        """Test 1: Verify INDEX.md exists and is recent"""
        index_path = self.docs_dir / 'INDEX.md'

        if not index_path.exists():
            return False, "INDEX.md not found"

        # Check if updated recently (within 7 days)
        mod_time = datetime.fromtimestamp(index_path.stat().st_mtime)
        days_old = (datetime.now() - mod_time).days

        if days_old > 7:
            return False, f"INDEX.md is {days_old} days old (should be updated weekly)"

        # Check file size (should be substantial)
        size = index_path.stat().st_size
        if size < 1000:
            return False, f"INDEX.md is only {size} bytes (suspiciously small)"

        return True, f"INDEX.md exists and is {days_old} days old ({size} bytes)"

    def test_session_start_guides(self) -> Tuple[bool, str]:
        """Test 2: Verify session start guides exist"""
        pattern = re.compile(r'00-START-SESSION-\d+\.md')
        start_files = [f for f in os.listdir(self.docs_dir) if pattern.match(f)]

        if len(start_files) < 5:
            return False, f"Only {len(start_files)} session start guides found (expected many)"

        # Check for Session 26 specifically (most recent)
        session_26 = self.docs_dir / '00-START-SESSION-26.md'
        if not session_26.exists():
            return False, "00-START-SESSION-26.md not found (most recent session)"

        return True, f"Found {len(start_files)} session start guides including Session 26"

    def test_handoff_letters(self) -> Tuple[bool, str]:
        """Test 3: Verify handoff letters exist"""
        letters_dir = self.docs_dir / 'letters'

        if not letters_dir.exists():
            return False, "letters/ directory not found"

        letters = list(letters_dir.glob('LETTER_TO_FUTURE_CLAUDE_SESSION_*.md'))

        if len(letters) < 2:
            return False, f"Only {len(letters)} handoff letters found (expected multiple)"

        # Check for recent session letters (25, 26)
        session_25 = letters_dir / 'LETTER_TO_FUTURE_CLAUDE_SESSION_25.md'
        session_26 = letters_dir / 'LETTER_TO_FUTURE_CLAUDE_SESSION_26.md'

        recent_found = sum([session_25.exists(), session_26.exists()])

        return True, f"Found {len(letters)} handoff letters ({recent_found}/2 recent sessions)"

    def test_session_reports_structure(self) -> Tuple[bool, str]:
        """Test 4: Verify session-reports/ structure"""
        reports_dir = self.docs_dir / 'session-reports'

        if not reports_dir.exists():
            return False, "session-reports/ directory not found"

        # Check for date-based subdirectories
        date_dirs = [d for d in os.listdir(reports_dir) if re.match(r'\d{4}-\d{2}-\d{2}', d)]

        if len(date_dirs) < 2:
            return False, f"Only {len(date_dirs)} dated report folders (expected multiple)"

        # Check today's folder
        today = datetime.now().strftime('%Y-%m-%d')
        today_dir = reports_dir / today

        if today_dir.exists():
            report_count = len(list(today_dir.glob('*.md')))
            return True, f"Found {len(date_dirs)} dated folders with {report_count} reports today"
        else:
            return True, f"Found {len(date_dirs)} dated folders (no reports today yet)"

    def test_required_folders(self) -> Tuple[bool, str]:
        """Test 5: Verify required folder structure"""
        required_folders = [
            'letters',
            'session-reports',
            'audits',
            'guides',
            'capabilities',
            'architecture'
        ]

        missing = []
        for folder in required_folders:
            if not (self.docs_dir / folder).exists():
                missing.append(folder)

        if missing:
            return False, f"Missing folders: {', '.join(missing)}"

        return True, f"All {len(required_folders)} required folders exist"

    def test_index_content_quality(self) -> Tuple[bool, str]:
        """Test 6: Verify INDEX.md contains required sections"""
        index_path = self.docs_dir / 'INDEX.md'

        if not index_path.exists():
            return False, "INDEX.md not found"

        with open(index_path, 'r') as f:
            content = f.read()

        required_sections = [
            'Quick Navigation',
            'Session Reports',
            'Architecture Documentation',
            'Feature Documentation',
            'Guides'
        ]

        missing_sections = []
        for section in required_sections:
            if section not in content:
                missing_sections.append(section)

        if missing_sections:
            return False, f"Missing sections: {', '.join(missing_sections)}"

        # Check for key information
        has_urls = 'localhost:8000' in content
        has_commands = 'make start' in content or 'make stop' in content

        quality_score = sum([has_urls, has_commands])

        if quality_score < 2:
            return False, "INDEX.md missing key information (URLs, commands)"

        return True, f"INDEX.md contains all {len(required_sections)} required sections + key info"

    def test_session_26_start_guide_content(self) -> Tuple[bool, str]:
        """Test 7: Verify Session 26 start guide has essential content"""
        start_guide = self.docs_dir / '00-START-SESSION-26.md'

        if not start_guide.exists():
            return False, "00-START-SESSION-26.md not found"

        with open(start_guide, 'r') as f:
            content = f.read()

        # Check for essential information
        checks = {
            'system_status': 'System Status' in content or 'STATUS' in content,
            'achievements': 'Achievement' in content or 'Complete' in content,
            'known_issues': 'Known Issue' in content or 'Issue' in content,
            'file_paths': 'core/' in content or '/core/' in content,
            'commands': 'make start' in content or 'make stop' in content,
        }

        passed_checks = sum(checks.values())
        total_checks = len(checks)

        if passed_checks < 4:
            failed = [k for k, v in checks.items() if not v]
            return False, f"Missing essential content: {', '.join(failed)}"

        return True, f"Contains {passed_checks}/{total_checks} essential content elements"

    def test_no_broken_internal_links(self) -> Tuple[bool, str]:
        """Test 8: Check for broken internal markdown links in INDEX.md"""
        index_path = self.docs_dir / 'INDEX.md'

        if not index_path.exists():
            return False, "INDEX.md not found"

        with open(index_path, 'r') as f:
            content = f.read()

        # Find all markdown links [text](path)
        link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        links = link_pattern.findall(content)

        broken_links = []
        for text, link in links:
            # Skip external links
            if link.startswith('http'):
                continue

            # Handle anchor links
            if link.startswith('#'):
                continue

            # Resolve relative path
            target = (self.docs_dir / link).resolve()

            if not target.exists():
                broken_links.append((text, link))

        if broken_links:
            details = '\n'.join([f"  - [{text}]({link})" for text, link in broken_links[:5]])
            return False, f"{len(broken_links)} broken links found:\n{details}"

        return True, f"All {len([l for l in links if not l[1].startswith('http') and not l[1].startswith('#')])} internal links valid"

    def test_recent_session_reports(self) -> Tuple[bool, str]:
        """Test 9: Verify recent sessions have reports"""
        reports_dir = self.docs_dir / 'session-reports'

        if not reports_dir.exists():
            return False, "session-reports/ directory not found"

        # Check last 7 days for reports
        today = datetime.now()
        recent_reports = []

        for i in range(7):
            date = today - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            date_dir = reports_dir / date_str

            if date_dir.exists():
                report_count = len(list(date_dir.glob('*.md')))
                if report_count > 0:
                    recent_reports.append((date_str, report_count))

        if not recent_reports:
            return False, "No session reports in last 7 days"

        total_reports = sum([count for _, count in recent_reports])

        return True, f"{len(recent_reports)} days with reports ({total_reports} total reports in last week)"

    def test_capabilities_documentation(self) -> Tuple[bool, str]:
        """Test 10: Verify capabilities are documented"""
        capabilities_dir = self.docs_dir / 'capabilities'

        if not capabilities_dir.exists():
            return False, "capabilities/ directory not found"

        capability_folders = [d for d in os.listdir(capabilities_dir)
                            if os.path.isdir(capabilities_dir / d)]

        if len(capability_folders) < 5:
            return False, f"Only {len(capability_folders)} capability folders (expected at least 5)"

        # Check for README files in capability folders
        readme_count = 0
        for folder in capability_folders:
            readme = capabilities_dir / folder / 'README.md'
            if readme.exists():
                readme_count += 1

        coverage = (readme_count / len(capability_folders)) * 100 if capability_folders else 0

        if coverage < 50:
            return False, f"Only {coverage:.0f}% of capabilities have documentation"

        return True, f"{len(capability_folders)} capabilities documented ({coverage:.0f}% have READMEs)"

    def run_all_tests(self) -> Dict:
        """Run all documentation tests"""
        print("\n" + "="*70)
        print("📚 Documentation System Validation Tests")
        print("="*70 + "\n")

        tests = [
            ("INDEX.md Exists", self.test_index_exists),
            ("Session Start Guides", self.test_session_start_guides),
            ("Handoff Letters", self.test_handoff_letters),
            ("Session Reports Structure", self.test_session_reports_structure),
            ("Required Folders", self.test_required_folders),
            ("INDEX.md Content Quality", self.test_index_content_quality),
            ("Session 26 Start Guide", self.test_session_26_start_guide_content),
            ("Internal Links", self.test_no_broken_internal_links),
            ("Recent Session Reports", self.test_recent_session_reports),
            ("Capabilities Documentation", self.test_capabilities_documentation),
        ]

        for name, test_func in tests:
            try:
                passed, message = test_func()
                self.record_test(name, passed, message)
            except Exception as e:
                self.record_test(name, False, f"Test error: {str(e)}")

        return self.results

    def print_summary(self):
        """Print test summary"""
        total = self.results['passed'] + self.results['failed']
        pass_rate = (self.results['passed'] / total * 100) if total > 0 else 0

        print("\n" + "="*70)
        print("📊 Test Summary")
        print("="*70)
        print(f"✅ Passed:  {self.results['passed']}/{total} ({pass_rate:.1f}%)")
        print(f"✗ Failed:  {self.results['failed']}/{total}")
        print("="*70 + "\n")

        if self.results['failed'] == 0:
            print("🎉 ALL TESTS PASSED - Documentation system is excellent!")
            print("✅ Context maintenance system is working perfectly.")
            return 0
        else:
            print("⚠️  Some tests failed - documentation system needs attention.")
            print("\nFailed tests:")
            for test in self.results['tests']:
                if not test['passed']:
                    print(f"  ✗ {test['name']}: {test['message']}")
            return 1


def main():
    """Main test runner"""
    import argparse

    parser = argparse.ArgumentParser(description='Test documentation system')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    parser.add_argument('--json', '-j', action='store_true',
                       help='Output results as JSON')
    parser.add_argument('--base-dir', '-d', type=str,
                       help='Base directory (default: auto-detect)')

    args = parser.parse_args()

    tester = DocSystemTester(base_dir=args.base_dir, verbose=args.verbose)
    results = tester.run_all_tests()

    if args.json:
        print(json.dumps(results, indent=2))
        return 0 if results['failed'] == 0 else 1
    else:
        return tester.print_summary()


if __name__ == '__main__':
    sys.exit(main())
