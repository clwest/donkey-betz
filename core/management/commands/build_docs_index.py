"""
Management command to generate docs/INDEX.md automatically.

This ensures INDEX.md always reflects reality and never goes stale.

Usage:
    python manage.py build_docs_index
    python manage.py build_docs_index --dry-run  # Preview without writing
"""
import os
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Generate docs/INDEX.md by scanning all documentation files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview the generated INDEX.md without writing to file',
        )

    def handle(self, *args, **options):
        base_dir = Path(settings.BASE_DIR)
        docs_dir = base_dir / 'docs'

        if not docs_dir.exists():
            self.stderr.write(self.style.ERROR(f'docs/ directory not found at {docs_dir}'))
            return

        # Gather all documentation statistics
        stats = self._gather_stats(docs_dir, base_dir)

        # Generate the INDEX.md content
        content = self._generate_index(stats, base_dir)

        if options['dry_run']:
            self.stdout.write(self.style.WARNING('\n=== DRY RUN - Preview of INDEX.md ===\n'))
            self.stdout.write(content)
            self.stdout.write(self.style.WARNING('\n=== END PREVIEW ==='))
        else:
            index_path = docs_dir / 'INDEX.md'
            with open(index_path, 'w') as f:
                f.write(content)
            self.stdout.write(self.style.SUCCESS(f'Generated {index_path}'))
            self.stdout.write(f'  - Total docs: {stats["total_files"]}')
            self.stdout.write(f'  - Total lines: {stats["total_lines"]:,}')
            self.stdout.write(f'  - Handoffs: {stats["folder_counts"].get("handoffs", 0)}')
            self.stdout.write(f'  - Audits: {stats["folder_counts"].get("audits", 0)}')

    def _gather_stats(self, docs_dir: Path, base_dir: Path) -> dict:
        """Scan docs directory and gather statistics."""
        stats = {
            'total_files': 0,
            'total_lines': 0,
            'folder_counts': {},
            'recent_files': [],
            'session_files': [],
            'top_level_docs': [],
            'subdirectories': [],
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
        }

        # Scan docs directory
        for item in docs_dir.iterdir():
            if item.is_file() and item.suffix == '.md':
                stats['top_level_docs'].append({
                    'name': item.name,
                    'path': str(item.relative_to(base_dir)),
                    'size': item.stat().st_size,
                    'mtime': datetime.fromtimestamp(item.stat().st_mtime),
                    'lines': self._count_lines(item),
                })
                stats['total_files'] += 1
                stats['total_lines'] += stats['top_level_docs'][-1]['lines']
            elif item.is_dir() and not item.name.startswith('.'):
                stats['subdirectories'].append(item.name)
                folder_files = list(item.rglob('*.md'))
                stats['folder_counts'][item.name] = len(folder_files)
                stats['total_files'] += len(folder_files)

                for f in folder_files:
                    lines = self._count_lines(f)
                    stats['total_lines'] += lines

                    # Track recent files
                    mtime = datetime.fromtimestamp(f.stat().st_mtime)
                    stats['recent_files'].append({
                        'name': f.name,
                        'path': str(f.relative_to(base_dir)),
                        'folder': item.name,
                        'mtime': mtime,
                        'lines': lines,
                    })

                    # Extract session number if present
                    session_match = re.search(r'SESSION_(\d+)', f.name)
                    if session_match:
                        stats['session_files'].append({
                            'session': int(session_match.group(1)),
                            'name': f.name,
                            'path': str(f.relative_to(base_dir)),
                            'folder': item.name,
                            'mtime': mtime,
                        })

        # Sort recent files by modification time
        stats['recent_files'].sort(key=lambda x: x['mtime'], reverse=True)

        # Sort session files by session number
        stats['session_files'].sort(key=lambda x: x['session'], reverse=True)

        # Also check for key files outside docs/
        key_files = ['CLAUDE.md', '00-START-NEXT-SESSION.md']
        for kf in key_files:
            kf_path = base_dir / kf
            if kf_path.exists():
                lines = self._count_lines(kf_path)
                stats['top_level_docs'].insert(0, {
                    'name': kf,
                    'path': kf,
                    'size': kf_path.stat().st_size,
                    'mtime': datetime.fromtimestamp(kf_path.stat().st_mtime),
                    'lines': lines,
                    'root': True,
                })
                stats['total_files'] += 1
                stats['total_lines'] += lines

        return stats

    def _count_lines(self, filepath: Path) -> int:
        """Count lines in a file."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except Exception:
            return 0

    def _extract_current_session(self, base_dir: Path) -> int:
        """Extract current session number from 00-START-NEXT-SESSION.md."""
        start_file = base_dir / '00-START-NEXT-SESSION.md'
        if start_file.exists():
            try:
                content = start_file.read_text()
                match = re.search(r'Session\s+(\d+)', content, re.IGNORECASE)
                if match:
                    return int(match.group(1))
            except Exception:
                pass
        return 784  # Default fallback

    def _extract_platform_stats(self, base_dir: Path) -> dict:
        """Extract platform statistics from CLAUDE.md."""
        claude_file = base_dir / 'CLAUDE.md'
        stats = {
            'agents': 74,
            'spiders': 77,
            'spiders_working': 72,
            'services': 114,
            'celery_tasks': 139,
            'database_models': '364+',
            'frontend_pages': 44,
            'body_systems': 9,
            'scifi_features': 14,
            'llm_providers': 6,
            'advisors': 25,
            'integration_score': '95%',
        }

        if claude_file.exists():
            try:
                content = claude_file.read_text()

                # Extract numbers from CLAUDE.md
                patterns = {
                    'agents': r'\*\*Agents\*\*\s*\|\s*(\d+)',
                    'spiders': r'\*\*Spiders\*\*\s*\|\s*(\d+)',
                    'services': r'\*\*Services\*\*\s*\|\s*(\d+)',
                    'celery_tasks': r'\*\*Celery Tasks\*\*\s*\|\s*(\d+)',
                    'frontend_pages': r'\*\*Frontend Pages\*\*\s*\|\s*(\d+)',
                    'body_systems': r'\*\*Body Systems\*\*\s*\|\s*(\d+)',
                    'scifi_features': r'\*\*Sci-Fi Features\*\*\s*\|\s*(\d+)',
                    'advisors': r'\*\*Advisors\*\*\s*\|\s*(\d+)',
                }

                for key, pattern in patterns.items():
                    match = re.search(pattern, content)
                    if match:
                        stats[key] = int(match.group(1))

            except Exception:
                pass

        return stats

    def _generate_index(self, stats: dict, base_dir: Path) -> str:
        """Generate the INDEX.md content."""
        current_session = self._extract_current_session(base_dir)
        platform_stats = self._extract_platform_stats(base_dir)

        lines = []

        # Header
        lines.append('# Unified Donkey Betz - Documentation Index')
        lines.append('')
        lines.append(f'**Generated:** {stats["generated_at"]}')
        lines.append(f'**Current Session:** {current_session}')
        lines.append(f'**Total Documentation:** {stats["total_files"]} files | {stats["total_lines"]:,} lines')
        lines.append('')
        lines.append('> This file is auto-generated by `python manage.py build_docs_index`')
        lines.append('')
        lines.append('---')
        lines.append('')

        # Core Entry Points
        lines.append('## Core Entry Points')
        lines.append('')
        lines.append('| File | Description | Lines |')
        lines.append('|------|-------------|-------|')
        lines.append('| `00-START-NEXT-SESSION.md` | **START HERE** - Current session priorities | - |')
        lines.append('| `CLAUDE.md` | System overview for AI agents | - |')
        lines.append('| `docs/INDEX.md` | This file - documentation map | - |')
        lines.append('')

        # Platform Statistics
        lines.append('## Platform Statistics')
        lines.append('')
        lines.append('| Component | Count |')
        lines.append('|-----------|-------|')
        lines.append(f'| Agents | {platform_stats["agents"]} |')
        lines.append(f'| Spiders | {platform_stats["spiders"]} ({platform_stats["spiders_working"]} working) |')
        lines.append(f'| Services | {platform_stats["services"]} |')
        lines.append(f'| Celery Tasks | {platform_stats["celery_tasks"]} |')
        lines.append(f'| Database Models | {platform_stats["database_models"]} |')
        lines.append(f'| Frontend Pages | {platform_stats["frontend_pages"]} |')
        lines.append(f'| Body Systems | {platform_stats["body_systems"]} |')
        lines.append(f'| Sci-Fi Features | {platform_stats["scifi_features"]} |')
        lines.append(f'| LLM Providers | {platform_stats["llm_providers"]} |')
        lines.append(f'| Advisors | {platform_stats["advisors"]} |')
        lines.append(f'| Integration Score | {platform_stats["integration_score"]} |')
        lines.append('')

        # Documentation by Folder
        lines.append('## Documentation by Folder')
        lines.append('')
        lines.append('| Folder | Files | Description |')
        lines.append('|--------|-------|-------------|')

        folder_descriptions = {
            'handoffs': 'Session handoff documents - decisions, changes, lessons learned',
            'audits': 'System audits - reality checks and gap analysis',
            'designs': 'Design documents - architectural intent and proposals',
            'roadmaps': 'Roadmaps - future plans and integration phases',
            'body': 'Body system documentation',
            'current': 'Current system guides',
            'apis': 'External API documentation',
            'guides': 'How-to guides',
            'architecture': 'Architecture deep-dives',
            'features': 'Feature documentation',
            'archive': 'Archived/historical documentation',
            'reports': 'Generated reports',
            'code-review': 'Code review documentation',
            'plans': 'Implementation plans',
            'pre-launch': 'Pre-launch checklists',
            'agents': 'Agent-specific documentation',
            'workflows': 'Workflow documentation',
            'integrations': 'Integration documentation',
        }

        for folder in sorted(stats['subdirectories']):
            count = stats['folder_counts'].get(folder, 0)
            desc = folder_descriptions.get(folder, '')
            lines.append(f'| `docs/{folder}/` | {count} | {desc} |')

        lines.append('')

        # Top-Level Documents
        lines.append('## Top-Level Documents')
        lines.append('')
        lines.append('| Document | Lines | Last Modified |')
        lines.append('|----------|-------|---------------|')

        for doc in sorted(stats['top_level_docs'], key=lambda x: x['name']):
            if not doc.get('root'):
                mtime_str = doc['mtime'].strftime('%Y-%m-%d')
                lines.append(f'| [{doc["name"]}]({doc["name"]}) | {doc["lines"]:,} | {mtime_str} |')

        lines.append('')

        # Recent Sessions
        lines.append('## Recent Sessions')
        lines.append('')
        lines.append('| Session | Document | Folder | Modified |')
        lines.append('|---------|----------|--------|----------|')

        for sf in stats['session_files'][:20]:  # Last 20 sessions
            mtime_str = sf['mtime'].strftime('%Y-%m-%d')
            lines.append(f'| {sf["session"]} | {sf["name"]} | {sf["folder"]} | {mtime_str} |')

        lines.append('')

        # Recently Modified Files
        lines.append('## Recently Modified (Last 10)')
        lines.append('')
        lines.append('| File | Folder | Lines | Modified |')
        lines.append('|------|--------|-------|----------|')

        for rf in stats['recent_files'][:10]:
            mtime_str = rf['mtime'].strftime('%Y-%m-%d %H:%M')
            lines.append(f'| {rf["name"]} | {rf["folder"]} | {rf["lines"]:,} | {mtime_str} |')

        lines.append('')

        # Key Documents by Category
        lines.append('## Key Documents by Category')
        lines.append('')

        categories = {
            'System Overview': [
                ('ARCHITECTURE.md', 'System layers, data flow, component relationships'),
                ('CAPABILITIES.md', 'Full feature list'),
                ('SYSTEM_OVERVIEW.md', 'High-level system description'),
            ],
            'Components': [
                ('AGENTS.md', '74 agents + capabilities + routing'),
                ('SPIDERS.md', '77 spiders, data collection'),
                ('SERVICES.md', '114 services across the platform'),
                ('SCIFI_FEATURES.md', '14 advanced AI features'),
            ],
            'Database & Models': [
                ('DATABASE_MODEL_REFERENCE.md', 'Which DB table for what'),
                ('MODELS.md', 'Model documentation'),
            ],
            'Operations': [
                ('DEPLOYMENT_GUIDE.md', 'Deployment instructions'),
                ('DEPLOYMENT_QUICKREF.md', 'Quick deployment reference'),
                ('ERROR_TRACKING.md', 'Error tracking document'),
            ],
            'Memory & Learning': [
                ('MEMORY_SAFETY_CLASSIFICATION.md', 'Memory safety system'),
                ('KNOWLEDGE_PIPELINE.md', 'Spider -> Embeddings -> Agent Learning'),
            ],
            'UI & Frontend': [
                ('UI_COMPREHENSIVE_AUDIT.md', '44 pages, 55+ APIs audit'),
                ('WORKSPACE_USER_GUIDE.md', 'SKIN Layer workspace guide'),
            ],
        }

        for category, docs in categories.items():
            lines.append(f'### {category}')
            lines.append('')
            lines.append('| Document | Description |')
            lines.append('|----------|-------------|')
            for doc_name, description in docs:
                lines.append(f'| [{doc_name}]({doc_name}) | {description} |')
            lines.append('')

        # Documentation Philosophy
        lines.append('## Documentation as Institutional Memory')
        lines.append('')
        lines.append('This documentation serves as a **Cognitive Build Ledger** - a complete longitudinal record of the system\'s evolution:')
        lines.append('')
        lines.append(f'- **{stats["folder_counts"].get("handoffs", 0)} session handoffs** preserve decisions, bugs, fixes, and lessons learned')
        lines.append(f'- **{stats["folder_counts"].get("audits", 0)} audits** document system reality vs. expectations')
        lines.append('- **Design docs** capture architectural intent and the "why"')
        lines.append('- Any AI agent can resume work without loss of context')
        lines.append('')
        lines.append('**Philosophy:** Document while thinking, not after building.')
        lines.append('')

        # Quick Start
        lines.append('---')
        lines.append('')
        lines.append('## Quick Start')
        lines.append('')
        lines.append('```bash')
        lines.append('# 1. Read current session context')
        lines.append('cat 00-START-NEXT-SESSION.md')
        lines.append('')
        lines.append('# 2. Start platform')
        lines.append('make start && make celery')
        lines.append('')
        lines.append('# 3. Access UI')
        lines.append('open http://localhost:8000/ai-studio/')
        lines.append('')
        lines.append('# 4. Regenerate this index')
        lines.append('python manage.py build_docs_index')
        lines.append('```')
        lines.append('')

        # Footer
        lines.append('---')
        lines.append('')
        lines.append('**Always read `00-START-NEXT-SESSION.md` first - it has the current priorities!**')
        lines.append('')

        return '\n'.join(lines)
