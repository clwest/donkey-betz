"""
Import patent disclosure documents from docs/patents/ as Deliverable records.

Usage:
    python manage.py import_patent_disclosures
    python manage.py import_patent_disclosures --workspace "Unified Donkey Betz"
    python manage.py import_patent_disclosures --dry-run
"""

import os
import re
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils.text import slugify


# Metadata for each disclosure
DISCLOSURES = {
    'DISCLOSURE_A_EVIDENCE_GATED_BLOCKING.md': {
        'title': 'Disclosure A: Evidence-Gated Autonomous Blocking with Verification + Rollback',
        'workstream': 1,
        'tags': ['patent', 'ws1', 'ops-autopilot', 'blocking', 'verification', 'rollback'],
    },
    'DISCLOSURE_B_LAZY_TTL_MULTIPOINT_ENFORCEMENT.md': {
        'title': 'Disclosure B: Lazy TTL Auto-Expire Blocks with Multi-Point Enforcement',
        'workstream': 1,
        'tags': ['patent', 'ws1', 'ops-autopilot', 'ttl', 'enforcement'],
    },
    'DISCLOSURE_C_GRADUATED_REMEDIATION_LADDERS.md': {
        'title': 'Disclosure C: Graduated Remediation Ladders with Auto De-escalation + Budget/ROI',
        'workstream': 1,
        'tags': ['patent', 'ws1', 'ops-autopilot', 'remediation', 'budget', 'roi'],
    },
    'DISCLOSURE_D_CLAIMS_BASED_DELIBERATION.md': {
        'title': 'Disclosure D: Claims-Based Multi-Reviewer Content Deliberation',
        'workstream': 2,
        'tags': ['patent', 'ws2', 'content', 'deliberation', 'citations', 'review'],
    },
    'DISCLOSURE_E_PUBLISH_GATE_FINISHING_LOOP.md': {
        'title': 'Disclosure E: Four-Dimensional Publish Gate with Mythology Detection',
        'workstream': 2,
        'tags': ['patent', 'ws2', 'content', 'quality-gate', 'mythology', 'finishing-loop'],
    },
    'DISCLOSURE_F_STRUCTURED_DEBATE_DECISION_ENFORCEMENT.md': {
        'title': 'Disclosure F: Structured Multi-Agent Debate with Decision Enforcement',
        'workstream': 2,
        'tags': ['patent', 'ws2', 'debate', 'decision-enforcement', 'governance'],
    },
    'DISCLOSURE_G_SIGNAL_TO_INITIATIVE_PROVENANCE.md': {
        'title': 'Disclosure G: Signal-to-Initiative Provenance Pipeline',
        'workstream': 3,
        'tags': ['patent', 'ws3', 'signals', 'provenance', 'initiatives', 'pipeline'],
    },
    'DISCLOSURE_H_SIGNAL_CLUSTERING_PATTERN_DETECTION.md': {
        'title': 'Disclosure H: Multi-Source Signal Clustering with Pattern-Type Taxonomy',
        'workstream': 3,
        'tags': ['patent', 'ws3', 'signals', 'clustering', 'scoring', 'taxonomy'],
    },
    'DISCLOSURE_I_INITIATIVE_CIRCUIT_BREAKER.md': {
        'title': 'Disclosure I: Four-Gate Initiative Circuit Breaker with Jaccard Dedup',
        'workstream': 3,
        'tags': ['patent', 'ws3', 'initiatives', 'circuit-breaker', 'dedup'],
    },
    'DISCLOSURE_J_BUDGET_ENFORCEMENT_QROI.md': {
        'title': 'Disclosure J: Multi-Tier Budget Enforcement with QROI Throttling',
        'workstream': 4,
        'tags': ['patent', 'ws4', 'budget', 'qroi', 'throttling'],
    },
    'DISCLOSURE_K_BUDGET_AWARE_SCHEDULING.md': {
        'title': 'Disclosure K: Budget-Aware Task Scheduling with Knob-Based Downscoping',
        'workstream': 4,
        'tags': ['patent', 'ws4', 'scheduling', 'downscoping', 'attribution'],
    },
    'DISCLOSURE_L_SELF_TUNING_EXPERIMENTATION.md': {
        'title': 'Disclosure L: Self-Tuning Policy Framework with A/B Experimentation',
        'workstream': 4,
        'tags': ['patent', 'ws4', 'self-tuning', 'experimentation', 'arbitration'],
    },
}

EXECUTIVE_SUMMARIES = {
    'EXECUTIVE_SUMMARY.md': {
        'title': 'Executive Summary: Workstream #1 — Ops Autopilot',
        'workstream': 1,
        'tags': ['patent', 'ws1', 'executive-summary'],
    },
    'EXECUTIVE_SUMMARY_WS2.md': {
        'title': 'Executive Summary: Workstream #2 — Content/Decision Safety',
        'workstream': 2,
        'tags': ['patent', 'ws2', 'executive-summary'],
    },
    'EXECUTIVE_SUMMARY_WS3.md': {
        'title': 'Executive Summary: Workstream #3 — Signal Intelligence',
        'workstream': 3,
        'tags': ['patent', 'ws3', 'executive-summary'],
    },
    'EXECUTIVE_SUMMARY_WS4.md': {
        'title': 'Executive Summary: Workstream #4 — Budget/Scheduling',
        'workstream': 4,
        'tags': ['patent', 'ws4', 'executive-summary'],
    },
}

WS_NAMES = {
    1: 'Ops Autopilot',
    2: 'Content/Decision Safety',
    3: 'Signal Intelligence',
    4: 'Budget/Scheduling',
}


class Command(BaseCommand):
    help = 'Import patent disclosure documents from docs/patents/ as Deliverable records'

    def add_arguments(self, parser):
        parser.add_argument(
            '--workspace', type=str, default='Unified Donkey Betz',
            help='Workspace name to link deliverables to',
        )
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Show what would be created without creating',
        )
        parser.add_argument(
            '--force', action='store_true',
            help='Overwrite existing deliverables with same slug',
        )

    def handle(self, *args, **options):
        from core.models_deliverables import Deliverable
        from core.models_skin_layer import ProjectWorkspace

        workspace_name = options['workspace']
        dry_run = options['dry_run']
        force = options['force']

        patents_dir = Path(__file__).resolve().parents[3] / 'docs' / 'patents'
        if not patents_dir.exists():
            self.stderr.write(self.style.ERROR(f'Patents directory not found: {patents_dir}'))
            return

        # Find workspace
        workspace = None
        try:
            workspace = ProjectWorkspace.objects.filter(name__icontains=workspace_name).first()
            if workspace:
                self.stdout.write(f'Linking to workspace: {workspace.name} ({workspace.id})')
            else:
                self.stdout.write(self.style.WARNING(f'Workspace "{workspace_name}" not found — creating without workspace link'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Workspace lookup failed: {e}'))

        all_docs = {**DISCLOSURES, **EXECUTIVE_SUMMARIES}
        created = 0
        updated = 0
        skipped = 0

        for filename, meta in all_docs.items():
            filepath = patents_dir / filename
            if not filepath.exists():
                self.stdout.write(self.style.WARNING(f'  SKIP: {filename} not found'))
                skipped += 1
                continue

            content = filepath.read_text(encoding='utf-8')
            word_count = len(content.split())
            is_exec_summary = 'executive-summary' in meta['tags']
            ws_num = meta['workstream']

            slug = slugify(f"patent-{filename.replace('.md', '').lower()}")[:280]

            # Build preview (first 500 chars after frontmatter)
            preview = content[:500].replace('#', '').strip()

            if dry_run:
                self.stdout.write(f'  DRY-RUN: Would create "{meta["title"]}" ({word_count} words)')
                created += 1
                continue

            defaults = {
                'title': meta['title'],
                'deliverable_type': 'document',
                'category': f'Patent — WS{ws_num}: {WS_NAMES[ws_num]}',
                'tags': meta['tags'],
                'content': content,
                'content_format': 'markdown',
                'preview_content': preview,
                'agent_name': 'ClaudeCode',
                'agent_task': f'Patent Workstream #{ws_num} disclosure',
                'quality_score': 0.95,
                'confidence_score': 0.90,
                'status': 'completed',
                'data_sensitivity': 'confidential',
                'is_pinned': True,
                'workspace': workspace,
            }

            existing = Deliverable.objects.filter(slug=slug).first()
            if existing and not force:
                self.stdout.write(f'  EXISTS: {meta["title"]} (use --force to overwrite)')
                skipped += 1
                continue

            if existing and force:
                for key, val in defaults.items():
                    setattr(existing, key, val)
                existing.save()
                self.stdout.write(self.style.SUCCESS(f'  UPDATED: {meta["title"]}'))
                updated += 1
            else:
                Deliverable.objects.create(slug=slug, **defaults)
                self.stdout.write(self.style.SUCCESS(f'  CREATED: {meta["title"]}'))
                created += 1

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'Done: {created} created, {updated} updated, {skipped} skipped'
        ))
