"""
Session 819: Audit Tracking Service

Parses audit markdown files, extracts findings, and manages remediation workflow.
Makes audits actionable by tracking status and enabling verification.
"""

import re
import os
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path

from django.utils import timezone
from django.utils.text import slugify
from django.db import transaction

logger = logging.getLogger(__name__)


class AuditTrackerService:
    """
    Service for parsing audits, tracking findings, and managing remediation.
    """

    # Patterns for extracting information from audit files
    TITLE_PATTERN = re.compile(r'^#\s+(.+)$', re.MULTILINE)
    DATE_PATTERN = re.compile(r'\*\*Date:\*\*\s*(.+?)(?:\n|$)', re.IGNORECASE)
    SESSION_PATTERN = re.compile(r'Session\s*(\d+)', re.IGNORECASE)
    PRIORITY_PATTERN = re.compile(r'\*\*Priority:\*\*\s*(P[0-3])', re.IGNORECASE)

    # Patterns for finding tables
    TABLE_ROW_PATTERN = re.compile(r'\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|')

    # Keywords that indicate findings
    FINDING_KEYWORDS = [
        'security gap', 'vulnerability', 'issue', 'problem', 'risk',
        'missing', 'no authentication', 'csrf exempt', 'unprotected',
        'inconsistent', 'critical gap', 'warning', 'error'
    ]

    # Priority keywords
    PRIORITY_KEYWORDS = {
        'P0': ['critical', 'security vulnerability', 'unprotected', 'no auth'],
        'P1': ['high priority', 'significant', 'important', 'should fix'],
        'P2': ['medium', 'moderate', 'nice to have'],
        'P3': ['low', 'minor', 'cosmetic'],
    }

    def __init__(self):
        self.docs_root = Path('docs')
        self.audits_dir = self.docs_root / 'audits'

    def parse_audit_file(self, file_path: str) -> Dict:
        """
        Parse a single audit markdown file and extract structured data.

        Returns:
            Dict with audit metadata and findings
        """
        from core.models_audit_tracking import AuditReport, AuditFinding

        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Audit file not found: {file_path}")

        content = path.read_text(encoding='utf-8')

        # Extract metadata
        title = self._extract_title(content) or path.stem
        audit_date = self._extract_date(content)
        session_num = self._extract_session(content)
        audit_type = self._determine_audit_type(file_path, title)
        summary = self._extract_summary(content)

        # Extract findings
        findings = self._extract_findings(content, title)

        return {
            'file_path': str(file_path),
            'title': title,
            'slug': slugify(title)[:255],
            'audit_type': audit_type,
            'session_number': session_num,
            'audit_date': audit_date,
            'executive_summary': summary,
            'raw_content': content,
            'findings': findings,
        }

    def _extract_title(self, content: str) -> Optional[str]:
        """Extract title from first H1 heading."""
        match = self.TITLE_PATTERN.search(content)
        if match:
            return match.group(1).strip()
        return None

    def _extract_date(self, content: str) -> Optional[datetime]:
        """Extract audit date."""
        match = self.DATE_PATTERN.search(content)
        if match:
            date_str = match.group(1).strip()
            # Try common formats
            for fmt in ['%B %d, %Y', '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']:
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue
        return None

    def _extract_session(self, content: str) -> Optional[int]:
        """Extract session number."""
        match = self.SESSION_PATTERN.search(content)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                pass
        return None

    def _extract_summary(self, content: str) -> str:
        """Extract executive summary section."""
        # Look for Executive Summary section
        summary_match = re.search(
            r'##\s*Executive Summary\s*\n+(.*?)(?=\n##|\Z)',
            content,
            re.IGNORECASE | re.DOTALL
        )
        if summary_match:
            return summary_match.group(1).strip()[:2000]
        return ''

    def _determine_audit_type(self, file_path: str, title: str) -> str:
        """Determine audit type from filename and title."""
        combined = (file_path + ' ' + title).lower()

        if 'security' in combined:
            return 'security'
        elif 'api' in combined:
            return 'api'
        elif 'integration' in combined:
            return 'integration'
        elif 'database' in combined or 'model' in combined:
            return 'database'
        elif 'performance' in combined:
            return 'performance'
        elif 'agent' in combined:
            return 'agent'
        elif 'session' in combined:
            return 'session'
        elif 'system' in combined:
            return 'system'
        return 'other'

    def _extract_findings(self, content: str, audit_title: str) -> List[Dict]:
        """
        Extract individual findings from audit content.

        Looks for:
        - Tables with Issue/Status columns
        - Bullet points with keywords
        - Numbered recommendations
        """
        findings = []

        # Method 1: Extract from tables
        table_findings = self._extract_table_findings(content)
        findings.extend(table_findings)

        # Method 2: Extract from "Recommendations" section
        rec_findings = self._extract_recommendations(content)
        findings.extend(rec_findings)

        # Method 3: Extract from "Issues Found" or "Gaps" sections
        gap_findings = self._extract_gap_findings(content)
        findings.extend(gap_findings)

        # Deduplicate by title similarity
        findings = self._deduplicate_findings(findings)

        return findings

    def _extract_table_findings(self, content: str) -> List[Dict]:
        """Extract findings from markdown tables."""
        findings = []

        # Find tables that look like they contain issues/findings
        # Look for tables with headers like Issue, Status, Priority, etc.
        table_pattern = re.compile(
            r'\|[^|]*(?:Issue|Problem|Gap|Risk|Finding|Warning)[^|]*\|.*?\n\|[-:| ]+\|(.*?)(?=\n\n|\n#|\Z)',
            re.IGNORECASE | re.DOTALL
        )

        for table_match in table_pattern.finditer(content):
            table_content = table_match.group(0)
            rows = table_content.strip().split('\n')

            # Skip header and separator rows
            data_rows = [r for r in rows[2:] if r.strip() and not r.strip().startswith('|--')]

            for row in data_rows:
                cells = [c.strip() for c in row.split('|') if c.strip()]
                if len(cells) >= 2:
                    title = cells[0]
                    # Skip empty or header-like rows
                    if title and title != '-' and not title.startswith('--'):
                        finding = {
                            'title': title[:255],
                            'description': ' | '.join(cells[1:]),
                            'priority': self._determine_priority(' '.join(cells)),
                            'category': self._determine_category(' '.join(cells)),
                            'raw_text': row,
                        }
                        findings.append(finding)

        return findings

    def _extract_recommendations(self, content: str) -> List[Dict]:
        """Extract findings from Recommendations section."""
        findings = []

        # Find Recommendations section
        rec_match = re.search(
            r'##\s*Recommendations?\s*\n+(.*?)(?=\n##|\Z)',
            content,
            re.IGNORECASE | re.DOTALL
        )

        if rec_match:
            rec_content = rec_match.group(1)

            # Look for numbered items with priority markers
            # Pattern: ### P0 - Critical or 1. **Title**
            item_pattern = re.compile(
                r'(?:###\s*(P[0-3])[^#\n]*\n+)?(?:\d+\.\s*\*\*([^*]+)\*\*\s*\n?(.*?)(?=\n\d+\.|\n###|\Z))',
                re.DOTALL
            )

            for match in item_pattern.finditer(rec_content):
                priority = match.group(1) or 'P2'
                title = match.group(2)
                description = match.group(3).strip() if match.group(3) else ''

                if title:
                    finding = {
                        'title': title.strip()[:255],
                        'description': description[:2000],
                        'priority': priority,
                        'category': self._determine_category(title + ' ' + description),
                        'recommendation': description,
                        'raw_text': match.group(0),
                    }
                    findings.append(finding)

        return findings

    def _extract_gap_findings(self, content: str) -> List[Dict]:
        """Extract findings from Gap Analysis or Issues sections."""
        findings = []

        # Find sections that contain gaps/issues
        section_patterns = [
            r'##\s*(?:Gap Analysis|Issues Found|What Needs Improvement|Problems|Warnings)\s*\n+(.*?)(?=\n##|\Z)',
            r'###\s*(?:Critical|High Priority|P0|P1)[^#\n]*\n+(.*?)(?=\n###|\n##|\Z)',
        ]

        for pattern in section_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE | re.DOTALL):
                section_content = match.group(1)

                # Extract bullet points
                bullet_pattern = re.compile(r'[-*]\s+\*?\*?([^*\n]+)\*?\*?\s*(?:\n\s+[-*].*)*', re.MULTILINE)

                for bullet in bullet_pattern.finditer(section_content):
                    title = bullet.group(1).strip()
                    if title and len(title) > 10:  # Skip very short items
                        finding = {
                            'title': title[:255],
                            'description': bullet.group(0).strip()[:2000],
                            'priority': self._determine_priority(title),
                            'category': self._determine_category(title),
                            'raw_text': bullet.group(0),
                        }
                        findings.append(finding)

        return findings

    def _determine_priority(self, text: str) -> str:
        """Determine priority based on keywords in text."""
        text_lower = text.lower()

        for priority, keywords in self.PRIORITY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return priority

        # Check for explicit priority markers
        if 'p0' in text_lower or 'critical' in text_lower:
            return 'P0'
        elif 'p1' in text_lower or 'high' in text_lower:
            return 'P1'
        elif 'p2' in text_lower or 'medium' in text_lower:
            return 'P2'

        return 'P2'  # Default

    def _determine_category(self, text: str) -> str:
        """Determine category based on text content."""
        text_lower = text.lower()

        categories = {
            'security': ['security', 'vulnerability', 'attack', 'exploit'],
            'authentication': ['auth', 'login', 'permission', 'csrf', 'token'],
            'performance': ['performance', 'speed', 'slow', 'latency', 'timeout'],
            'consistency': ['inconsistent', 'format', 'standard', 'pattern'],
            'documentation': ['documentation', 'docs', 'comment', 'readme'],
            'integration': ['integration', 'connect', 'interface', 'api'],
            'data_integrity': ['data', 'database', 'integrity', 'orphan'],
            'code_quality': ['code', 'refactor', 'duplicate', 'complexity'],
        }

        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return category

        return 'other'

    def _deduplicate_findings(self, findings: List[Dict]) -> List[Dict]:
        """Remove duplicate findings based on title similarity."""
        seen_titles = set()
        unique_findings = []

        for finding in findings:
            # Normalize title for comparison
            normalized = finding['title'].lower().strip()
            # Skip if too similar to existing
            if normalized not in seen_titles and len(normalized) > 5:
                seen_titles.add(normalized)
                unique_findings.append(finding)

        return unique_findings

    @transaction.atomic
    def import_audit(self, file_path: str) -> 'AuditReport':
        """
        Import an audit file into the database.

        Creates AuditReport and associated AuditFinding records.
        """
        from core.models_audit_tracking import AuditReport, AuditFinding

        # Parse the file
        data = self.parse_audit_file(file_path)

        # Create or update AuditReport
        report, created = AuditReport.objects.update_or_create(
            file_path=data['file_path'],
            defaults={
                'title': data['title'],
                'slug': data['slug'],
                'audit_type': data['audit_type'],
                'session_number': data['session_number'],
                'audit_date': data['audit_date'],
                'executive_summary': data['executive_summary'],
                'raw_content': data['raw_content'],
                'last_parsed_at': timezone.now(),
            }
        )

        action = "Created" if created else "Updated"
        logger.info(f"{action} audit report: {report.title}")

        # Clear existing findings if re-importing
        if not created:
            report.findings.all().delete()

        # Create findings
        for finding_data in data['findings']:
            AuditFinding.objects.create(
                audit_report=report,
                title=finding_data['title'],
                description=finding_data.get('description', ''),
                priority=finding_data.get('priority', 'P2'),
                category=finding_data.get('category', 'other'),
                recommendation=finding_data.get('recommendation', ''),
                raw_text=finding_data.get('raw_text', ''),
            )

        # Update stats
        report.update_stats()

        logger.info(f"Imported {len(data['findings'])} findings for {report.title}")

        return report

    def import_all_audits(self, dry_run: bool = False) -> Dict:
        """
        Import all audit files from docs/audits/ directory.

        Args:
            dry_run: If True, parse but don't save to database

        Returns:
            Summary of import operation
        """
        if not self.audits_dir.exists():
            raise FileNotFoundError(f"Audits directory not found: {self.audits_dir}")

        results = {
            'total_files': 0,
            'imported': 0,
            'failed': 0,
            'total_findings': 0,
            'by_priority': {'P0': 0, 'P1': 0, 'P2': 0, 'P3': 0},
            'errors': [],
        }

        for audit_file in self.audits_dir.glob('*.md'):
            # Skip index files
            if audit_file.name.lower() in ['index.md', 'readme.md']:
                continue

            results['total_files'] += 1

            try:
                if dry_run:
                    data = self.parse_audit_file(str(audit_file))
                    findings_count = len(data['findings'])
                    for f in data['findings']:
                        results['by_priority'][f.get('priority', 'P2')] += 1
                    results['total_findings'] += findings_count
                    logger.info(f"[DRY RUN] Would import: {data['title']} ({findings_count} findings)")
                else:
                    report = self.import_audit(str(audit_file))
                    results['total_findings'] += report.total_findings
                    results['by_priority']['P0'] += report.p0_findings
                    results['by_priority']['P1'] += report.p1_findings
                    results['by_priority']['P2'] += report.p2_findings

                results['imported'] += 1

            except Exception as e:
                results['failed'] += 1
                results['errors'].append({
                    'file': str(audit_file),
                    'error': str(e)
                })
                logger.error(f"Failed to import {audit_file}: {e}")

        return results

    def get_open_findings(
        self,
        priority: str = None,
        category: str = None,
        limit: int = 50
    ) -> List['AuditFinding']:
        """Get open findings, optionally filtered."""
        from core.models_audit_tracking import AuditFinding

        queryset = AuditFinding.objects.filter(status='open')

        if priority:
            queryset = queryset.filter(priority=priority)
        if category:
            queryset = queryset.filter(category=category)

        return list(queryset.select_related('audit_report')[:limit])

    def get_p0_findings(self) -> List['AuditFinding']:
        """Get all open P0 (critical) findings."""
        return self.get_open_findings(priority='P0', limit=100)

    def create_remediation_task(
        self,
        finding_id: str,
        title: str,
        description: str,
        agent_name: str = None
    ) -> 'AuditRemediationTask':
        """Create a remediation task for a finding."""
        from core.models_audit_tracking import AuditFinding, AuditRemediationTask

        finding = AuditFinding.objects.get(id=finding_id)

        task = AuditRemediationTask.objects.create(
            finding=finding,
            title=title,
            description=description,
        )

        if agent_name:
            task.assign_to_agent(agent_name)

        return task

    def verify_finding(
        self,
        finding_id: str,
        verification_type: str,
        command: str = ''
    ) -> 'AuditVerificationRun':
        """
        Run verification for a finding and record results.
        """
        from core.models_audit_tracking import AuditFinding, AuditVerificationRun

        finding = AuditFinding.objects.get(id=finding_id)

        # Run verification based on type
        passed = False
        result_summary = ''
        result_details = {}

        if verification_type == 'grep_check':
            passed, result_summary, result_details = self._run_grep_verification(finding)
        elif verification_type == 'api_test':
            passed, result_summary, result_details = self._run_api_verification(finding)
        elif verification_type == 'manual':
            # Manual verification - just record it
            passed = True
            result_summary = 'Manual verification required'

        # Create verification record
        verification = AuditVerificationRun.objects.create(
            finding=finding,
            verification_type=verification_type,
            verification_command=command,
            passed=passed,
            result_summary=result_summary,
            result_details=result_details,
        )

        # Update finding if passed
        if passed:
            finding.mark_verified(f"Verified via {verification_type}")

        return verification

    def _run_grep_verification(self, finding) -> Tuple[bool, str, Dict]:
        """Run grep-based verification for code-level findings."""
        # This would actually run grep commands to verify fixes
        # For now, return placeholder
        return False, 'Grep verification not yet implemented', {}

    def _run_api_verification(self, finding) -> Tuple[bool, str, Dict]:
        """Run API-based verification for endpoint findings."""
        # This would actually test API endpoints
        # For now, return placeholder
        return False, 'API verification not yet implemented', {}

    def get_finding_summary(self) -> Dict:
        """Get summary statistics of all findings."""
        from core.models_audit_tracking import AuditReport, AuditFinding

        total_reports = AuditReport.objects.count()
        total_findings = AuditFinding.objects.count()

        by_status = {}
        for status, _ in AuditFinding.STATUS_CHOICES:
            by_status[status] = AuditFinding.objects.filter(status=status).count()

        by_priority = {}
        for priority, _ in AuditFinding.PRIORITY_CHOICES:
            by_priority[priority] = AuditFinding.objects.filter(priority=priority).count()

        by_category = {}
        for category, _ in AuditFinding.CATEGORY_CHOICES:
            count = AuditFinding.objects.filter(category=category).count()
            if count > 0:
                by_category[category] = count

        return {
            'total_reports': total_reports,
            'total_findings': total_findings,
            'by_status': by_status,
            'by_priority': by_priority,
            'by_category': by_category,
            'open_p0': AuditFinding.objects.filter(status='open', priority='P0').count(),
            'open_p1': AuditFinding.objects.filter(status='open', priority='P1').count(),
        }
