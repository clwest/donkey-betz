"""
Session 949: Auto-classify documents for Risk-Aware RAG

Scans documents and automatically sets:
- is_critical: For governance, architecture, mission-critical docs
- document_class: Based on filename patterns and content
- risk_level: Based on document type and content

Usage:
    python manage.py classify_docs_for_rag
    python manage.py classify_docs_for_rag --dry-run  # Preview changes
"""

import re
from django.core.management.base import BaseCommand
from django.db import transaction
from content.models import Document, ContentStatus


class Command(BaseCommand):
    help = 'Auto-classify documents for risk-aware RAG retrieval'

    # Patterns for critical docs (always retrieve)
    CRITICAL_PATTERNS = [
        r'CLAUDE\.md',
        r'00-START-NEXT-SESSION\.md',
        r'GOVERNANCE\.md',
        r'MISSIONS\.md',
        r'ARCHITECTURE\.md',
        r'API_PATH_POLICY\.md',
        r'DATABASE_MODEL_REFERENCE\.md',
        r'USER_FEEDBACK_QUEUE\.md',
    ]

    # Patterns for document classes
    CLASS_PATTERNS = {
        'postmortem': [
            r'postmortem',
            r'post-mortem',
            r'incident.*report',
            r'outage.*report',
        ],
        'incident_report': [
            r'incident',
            r'outage',
            r'failure.*report',
            r'error.*report',
        ],
        'security': [
            r'security.*advisory',
            r'vulnerability',
            r'CVE-',
            r'security.*audit',
        ],
        'constraint': [
            r'policy',
            r'governance',
            r'compliance',
            r'rules',
            r'guidelines',
            r'constraints',
        ],
        'architecture': [
            r'architecture',
            r'design.*doc',
            r'ADR-',  # Architecture Decision Records
            r'technical.*spec',
        ],
        'runbook': [
            r'runbook',
            r'playbook',
            r'operations.*guide',
            r'troubleshooting',
        ],
        'changelog': [
            r'changelog',
            r'release.*notes',
            r'version.*history',
        ],
    }

    # Keywords that indicate high risk level
    HIGH_RISK_KEYWORDS = [
        'critical', 'security', 'production', 'outage', 'incident',
        'vulnerability', 'exploit', 'failure', 'breaking', 'urgent',
        'postmortem', 'P0', 'P1', 'emergency',
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without saving',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        self.stdout.write(self.style.NOTICE(
            f"{'[DRY RUN] ' if dry_run else ''}Classifying documents for risk-aware RAG..."
        ))

        docs = Document.objects.filter(status=ContentStatus.PROCESSED)
        total = docs.count()

        stats = {
            'critical': 0,
            'high_risk': 0,
            'postmortem': 0,
            'incident_report': 0,
            'security': 0,
            'constraint': 0,
            'architecture': 0,
            'runbook': 0,
            'changelog': 0,
        }

        with transaction.atomic():
            for doc in docs:
                changed = False
                title_lower = doc.title.lower()
                path_lower = doc.file_path.lower() if doc.file_path else ''
                content_lower = (doc.processed_content or '')[:5000].lower()

                # Check if critical
                for pattern in self.CRITICAL_PATTERNS:
                    if re.search(pattern, doc.file_path or '', re.IGNORECASE):
                        if not doc.is_critical:
                            doc.is_critical = True
                            doc.risk_level = 'critical'
                            stats['critical'] += 1
                            changed = True
                            self.stdout.write(f"  CRITICAL: {doc.title}")
                        break

                # Classify document type
                for doc_class, patterns in self.CLASS_PATTERNS.items():
                    for pattern in patterns:
                        if (re.search(pattern, title_lower) or
                            re.search(pattern, path_lower) or
                            re.search(pattern, content_lower)):
                            if doc.document_class != doc_class:
                                doc.document_class = doc_class
                                stats[doc_class] += 1
                                changed = True
                                self.stdout.write(f"  {doc_class.upper()}: {doc.title}")
                            break
                    else:
                        continue
                    break

                # Check for high risk keywords
                if doc.risk_level == 'medium':  # Only upgrade, don't downgrade
                    for keyword in self.HIGH_RISK_KEYWORDS:
                        if keyword in content_lower or keyword in title_lower:
                            doc.risk_level = 'high'
                            stats['high_risk'] += 1
                            changed = True
                            break

                # Set retrieval boost based on risk level
                if doc.risk_level == 'critical':
                    doc.retrieval_boost = 2.0
                elif doc.risk_level == 'high':
                    doc.retrieval_boost = 1.5
                elif doc.document_class in ['postmortem', 'incident_report', 'security']:
                    doc.retrieval_boost = 1.5

                if changed and not dry_run:
                    doc.save(update_fields=[
                        'is_critical', 'document_class', 'risk_level', 'retrieval_boost'
                    ])

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f"{'[DRY RUN] Would classify' if dry_run else 'Classified'} {total} documents:"
        ))
        for key, count in stats.items():
            if count > 0:
                self.stdout.write(f"  - {key}: {count}")
