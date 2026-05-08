import logging
logger = logging.getLogger(__name__)

"""
Management command to generate docs/INDEX.md and docs/_index.json automatically.

This ensures documentation index always reflects reality and never goes stale.

Usage:
    python manage.py build_docs_index
    python manage.py build_docs_index --dry-run  # Preview without writing
    python manage.py build_docs_index --json-only  # Only generate _index.json

Frontmatter Format (optional, for new docs):
    ---
    subsystems: [agents, spiders, body]
    decision_types: [bug_fix, feature, refactor, design]
    status: active|superseded|deprecated|draft
    see_also: [SESSION_123_FOO.md, ARCHITECTURE.md]
    supersedes: SESSION_100_OLD_FEATURE.md
    ---

Cross-Reference Graph:
    The index automatically detects document references:
    - Explicit links: [text](SESSION_123.md) or [text](docs/handoffs/FILE.md)
    - File mentions: SESSION_123_FOO.md, ARCHITECTURE.md
    - see_also frontmatter references

    Each document includes:
    - outbound_links: list of documents this file references
    - inbound_links_count: number of documents that reference this file
"""
import json
import os
import re
import yaml
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from typing import Optional

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Generate docs/INDEX.md and docs/_index.json by scanning all documentation files'

    # Document type inference from folder/filename
    DOC_TYPES = {
        'handoffs': 'handoff',
        'audits': 'audit',
        'designs': 'design',
        'roadmaps': 'roadmap',
        'architecture': 'architecture',
        'guides': 'guide',
        'apis': 'api',
        'features': 'feature',
        'plans': 'plan',
        'reports': 'report',
        'body': 'body_system',
        'current': 'guide',
        'archive': 'archive',
    }

    # Valid frontmatter fields
    FRONTMATTER_FIELDS = {
        'subsystems': list,
        'decision_types': list,
        'status': str,
        'see_also': list,
        'supersedes': str,
    }

    # Valid status values
    VALID_STATUSES = {'active', 'superseded', 'deprecated', 'draft'}

    # Valid decision types
    VALID_DECISION_TYPES = {
        'bug_fix', 'feature', 'refactor', 'design', 'audit',
        'documentation', 'performance', 'security', 'integration',
        'ui', 'api', 'database', 'infrastructure', 'cleanup'
    }

    # Valid subsystems
    VALID_SUBSYSTEMS = {
        'agents', 'spiders', 'body', 'heart', 'lungs', 'brain', 'spine',
        'circulatory', 'digestive', 'muscular', 'immune', 'skin',
        'frontend', 'backend', 'celery', 'database', 'api', 'websocket',
        'llm', 'memory', 'learning', 'scifi', 'discord', 'legal',
        'podcast', 'content', 'workflow', 'orchestration', 'integration'
    }

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview the generated files without writing',
        )
        parser.add_argument(
            '--json-only',
            action='store_true',
            help='Only generate _index.json, not INDEX.md',
        )

    def handle(self, *args, **options):
        base_dir = Path(settings.BASE_DIR)
        docs_dir = base_dir / 'docs'

        if not docs_dir.exists():
            self.stderr.write(self.style.ERROR(f'docs/ directory not found at {docs_dir}'))
            return

        # Gather all documentation with metadata
        doc_index = self._build_doc_index(docs_dir, base_dir)

        # Gather stats for INDEX.md
        stats = self._gather_stats(docs_dir, base_dir, doc_index)

        if options['dry_run']:
            self.stdout.write(self.style.WARNING('\n=== DRY RUN ===\n'))
            self.stdout.write(f'Would generate:')
            self.stdout.write(f'  - docs/_index.json ({len(doc_index["documents"])} documents)')
            if not options['json_only']:
                self.stdout.write(f'  - docs/INDEX.md')
            self.stdout.write(f'\nStatus summary:')
            for status, count in stats['status_counts'].items():
                self.stdout.write(f'  - {status}: {count}')

            # Graph summary
            graph = doc_index.get('graph', {})
            self.stdout.write(f'\nCross-Reference Graph:')
            self.stdout.write(f'  - Total links: {graph.get("total_links", 0)}')
            self.stdout.write(f'  - Orphan docs: {len(graph.get("orphan_docs", []))}')
            self.stdout.write(f'  - Broken links: {len(graph.get("broken_links", []))}')
            if graph.get('most_referenced'):
                self.stdout.write(f'  - Most referenced:')
                for ref in graph['most_referenced'][:5]:
                    self.stdout.write(f'      {ref["path"]} ({ref["count"]} refs)')
            if graph.get('broken_links'):
                self.stdout.write(f'  - Sample broken links:')
                for broken in graph['broken_links'][:3]:
                    self.stdout.write(f'      {broken["source"]} -> {broken["raw_ref"]}')

            self.stdout.write(f'\nSample JSON entry:')
            if doc_index['documents']:
                sample = doc_index['documents'][0]
                self.stdout.write(json.dumps(sample, indent=2, default=str))
        else:
            # Write _index.json
            json_path = docs_dir / '_index.json'
            with open(json_path, 'w') as f:
                json.dump(doc_index, f, indent=2, default=str)
            self.stdout.write(self.style.SUCCESS(f'Generated {json_path}'))
            self.stdout.write(f'  - Documents indexed: {len(doc_index["documents"])}')
            self.stdout.write(f'  - With frontmatter: {stats["with_frontmatter"]}')

            if not options['json_only']:
                # Write INDEX.md
                content = self._generate_index(stats, base_dir, doc_index)
                index_path = docs_dir / 'INDEX.md'
                with open(index_path, 'w') as f:
                    f.write(content)
                self.stdout.write(self.style.SUCCESS(f'Generated {index_path}'))
                self.stdout.write(f'  - Total docs: {stats["total_files"]}')
                self.stdout.write(f'  - Total lines: {stats["total_lines"]:,}')

            # Print status summary
            self.stdout.write(f'\nStatus Summary:')
            for status, count in sorted(stats['status_counts'].items()):
                self.stdout.write(f'  - {status}: {count}')

    def _build_doc_index(self, docs_dir: Path, base_dir: Path) -> dict:
        """Build comprehensive document index with metadata."""
        index = {
            'generated_at': datetime.now().isoformat(),
            'generator': 'build_docs_index',
            'version': '2.2',  # Updated: code block filtering, link context, broken links
            'documents': [],
            'by_type': defaultdict(list),
            'by_status': defaultdict(list),
            'by_subsystem': defaultdict(list),
            'by_session': {},
            'graph': {
                'total_links': 0,
                'most_referenced': [],
                'orphan_docs': [],
                'broken_links': [],
            },
        }

        # First pass: collect all document paths
        all_files = []
        for md_file in docs_dir.rglob('*.md'):
            if md_file.name.startswith('_'):
                continue
            all_files.append((md_file, False))

        # Add root-level docs
        for root_doc in ['CLAUDE.md', '00-START-NEXT-SESSION.md']:
            root_path = base_dir / root_doc
            if root_path.exists():
                all_files.append((root_path, True))

        # Build set of all canonical doc paths for link resolution
        all_doc_paths = set()
        path_to_file = {}  # Map canonical path to actual file
        for filepath, is_root in all_files:
            if is_root:
                canonical = filepath.name
            else:
                canonical = str(filepath.relative_to(base_dir))
            all_doc_paths.add(canonical)
            path_to_file[canonical] = filepath

        # Second pass: extract metadata and links
        all_broken_links = []
        for filepath, is_root in all_files:
            doc_meta = self._extract_doc_metadata(filepath, docs_dir, base_dir, is_root=is_root)

            # Extract outbound links (now returns tuple)
            outbound_links, broken_links = self._extract_links(filepath, all_doc_paths)

            # Track broken links with source
            for broken in broken_links:
                broken['source'] = doc_meta['path']
                all_broken_links.append(broken)

            # Add see_also from frontmatter
            if doc_meta.get('see_also'):
                existing_targets = {link['target'] for link in outbound_links}
                for see_also_ref in doc_meta['see_also']:
                    normalized = self._normalize_doc_path(see_also_ref, all_doc_paths)
                    if normalized and normalized not in existing_targets:
                        outbound_links.append({
                            'target': normalized,
                            'occurrences': 1,
                            'snippets': ['(from see_also frontmatter)']
                        })

            doc_meta['outbound_links'] = outbound_links
            doc_meta['inbound_links_count'] = 0  # Will be calculated in third pass

            index['documents'].append(doc_meta)

            # Index by type
            index['by_type'][doc_meta['type']].append(doc_meta['path'])

            # Index by status
            if doc_meta.get('status'):
                index['by_status'][doc_meta['status']].append(doc_meta['path'])

            # Index by subsystems
            for subsystem in doc_meta.get('subsystems', []):
                index['by_subsystem'][subsystem].append(doc_meta['path'])

            # Index by session
            if doc_meta.get('session'):
                index['by_session'][doc_meta['session']] = doc_meta['path']

        # Third pass: calculate inbound link counts
        inbound_counts = defaultdict(int)
        total_links = 0
        for doc in index['documents']:
            for link in doc.get('outbound_links', []):
                target = link['target'] if isinstance(link, dict) else link
                inbound_counts[target] += 1
                total_links += 1

        # Update documents with inbound counts
        for doc in index['documents']:
            doc['inbound_links_count'] = inbound_counts.get(doc['path'], 0)

        # Build graph summary
        index['graph']['total_links'] = total_links

        # Find most referenced documents
        docs_by_inbound = sorted(
            [(doc['path'], doc['inbound_links_count'], doc.get('title', ''))
             for doc in index['documents']],
            key=lambda x: x[1],
            reverse=True
        )
        index['graph']['most_referenced'] = [
            {'path': path, 'count': count, 'title': title}
            for path, count, title in docs_by_inbound[:20]
            if count > 0
        ]

        # Find orphan docs (no inbound or outbound links)
        orphans = [
            doc['path'] for doc in index['documents']
            if doc['inbound_links_count'] == 0 and len(doc.get('outbound_links', [])) == 0
        ]
        index['graph']['orphan_docs'] = orphans[:50]  # Limit to 50

        # Add broken links (deduplicated by raw_ref)
        seen_broken = set()
        unique_broken = []
        for broken in all_broken_links:
            key = f"{broken['source']}:{broken['raw_ref']}"
            if key not in seen_broken:
                seen_broken.add(key)
                unique_broken.append(broken)
        index['graph']['broken_links'] = unique_broken[:100]  # Limit to 100

        # Convert defaultdicts to regular dicts for JSON serialization
        index['by_type'] = dict(index['by_type'])
        index['by_status'] = dict(index['by_status'])
        index['by_subsystem'] = dict(index['by_subsystem'])

        # Sort documents by path
        index['documents'].sort(key=lambda x: x['path'])

        return index

    def _extract_doc_metadata(self, filepath: Path, docs_dir: Path, base_dir: Path, is_root: bool = False) -> dict:
        """Extract metadata from a document file."""
        stat = filepath.stat()

        # Basic metadata
        meta = {
            'path': str(filepath.relative_to(base_dir)),
            'filename': filepath.name,
            'folder': str(filepath.parent.relative_to(base_dir)) if not is_root else '',
            'lines': self._count_lines(filepath),
            'size_bytes': stat.st_size,
            'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
        }

        # Infer document type
        meta['type'] = self._infer_doc_type(filepath, docs_dir, is_root)

        # Extract session number if present
        session_match = re.search(r'SESSION_(\d+)', filepath.name)
        if session_match:
            meta['session'] = int(session_match.group(1))

        # Extract title from content
        meta['title'] = self._extract_title(filepath)

        # Parse frontmatter if present
        frontmatter = self._parse_frontmatter(filepath)
        if frontmatter:
            meta['has_frontmatter'] = True
            # Merge frontmatter fields
            for field in self.FRONTMATTER_FIELDS:
                if field in frontmatter:
                    meta[field] = frontmatter[field]
        else:
            meta['has_frontmatter'] = False

        # Infer subsystems from content if not in frontmatter
        if 'subsystems' not in meta:
            meta['subsystems'] = self._infer_subsystems(filepath, meta)

        # Default status for docs without frontmatter
        if 'status' not in meta:
            meta['status'] = self._infer_status(meta)

        return meta

    def _infer_doc_type(self, filepath: Path, docs_dir: Path, is_root: bool) -> str:
        """Infer document type from folder or filename."""
        if is_root:
            if 'CLAUDE' in filepath.name:
                return 'system_config'
            elif 'START' in filepath.name:
                return 'session_start'
            return 'root'

        # Check folder-based type
        try:
            rel_path = filepath.relative_to(docs_dir)
            parts = rel_path.parts
            if parts:
                folder = parts[0]
                if folder in self.DOC_TYPES:
                    return self.DOC_TYPES[folder]
        except ValueError:
            pass

        # Infer from filename
        name_lower = filepath.name.lower()
        if 'audit' in name_lower:
            return 'audit'
        elif 'session' in name_lower:
            return 'handoff'
        elif 'roadmap' in name_lower:
            return 'roadmap'
        elif 'design' in name_lower:
            return 'design'

        return 'documentation'

    def _extract_title(self, filepath: Path) -> str:
        """Extract title from first H1 heading in file."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                in_frontmatter = False
                for line in f:
                    # Skip frontmatter
                    if line.strip() == '---':
                        in_frontmatter = not in_frontmatter
                        continue
                    if in_frontmatter:
                        continue

                    # Look for H1
                    if line.startswith('# '):
                        return line[2:].strip()

                    # Stop after first 50 lines
                    if f.tell() > 5000:
                        break
        except Exception as _e:
            logger.warning(
                "build_docs_index._extract_title: swallowed (%s: %s) — degraded",
                type(_e).__name__, _e,
            )

        # Fallback to filename
        return filepath.stem.replace('_', ' ').replace('-', ' ')

    def _parse_frontmatter(self, filepath: Path) -> Optional[dict]:
        """Parse YAML frontmatter from document if present."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(2000)  # Only check first 2KB

            if not content.startswith('---'):
                return None

            # Find end of frontmatter
            end_match = re.search(r'\n---\s*\n', content[3:])
            if not end_match:
                return None

            frontmatter_text = content[3:end_match.start() + 3]

            try:
                data = yaml.safe_load(frontmatter_text)
                if not isinstance(data, dict):
                    return None

                # Validate and normalize fields
                validated = {}
                for field, expected_type in self.FRONTMATTER_FIELDS.items():
                    if field in data:
                        value = data[field]
                        if expected_type == list and isinstance(value, str):
                            value = [v.strip() for v in value.split(',')]
                        if isinstance(value, expected_type):
                            validated[field] = value

                # Validate status
                if 'status' in validated and validated['status'] not in self.VALID_STATUSES:
                    del validated['status']

                return validated if validated else None

            except yaml.YAMLError:
                return None

        except Exception as _e:
            logger.warning(
                "build_docs_index._parse_frontmatter: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return None

    def _infer_subsystems(self, filepath: Path, meta: dict) -> list:
        """Infer subsystems from filename and content."""
        subsystems = set()

        name_lower = filepath.name.lower()
        title_lower = meta.get('title', '').lower()
        combined = f"{name_lower} {title_lower}"

        # Check for subsystem mentions
        subsystem_keywords = {
            'agent': 'agents',
            'spider': 'spiders',
            'body': 'body',
            'heart': 'heart',
            'lung': 'lungs',
            'brain': 'brain',
            'spine': 'spine',
            'circulat': 'circulatory',
            'digest': 'digestive',
            'muscul': 'muscular',
            'immune': 'immune',
            'skin': 'skin',
            'frontend': 'frontend',
            'ui': 'frontend',
            'react': 'frontend',
            'backend': 'backend',
            'django': 'backend',
            'celery': 'celery',
            'database': 'database',
            'model': 'database',
            'api': 'api',
            'websocket': 'websocket',
            'llm': 'llm',
            'gpt': 'llm',
            'claude': 'llm',
            'memory': 'memory',
            'learning': 'learning',
            'scifi': 'scifi',
            'sci-fi': 'scifi',
            'discord': 'discord',
            'legal': 'legal',
            'podcast': 'podcast',
            'content': 'content',
            'workflow': 'workflow',
            'orchestrat': 'orchestration',
            'integrat': 'integration',
        }

        for keyword, subsystem in subsystem_keywords.items():
            if keyword in combined:
                subsystems.add(subsystem)

        return list(subsystems)

    def _infer_status(self, meta: dict) -> str:
        """Infer document status from metadata."""
        folder = meta.get('folder', '')

        # Archive folder = archived/superseded
        if 'archive' in folder:
            return 'superseded'

        # Very old docs might be superseded
        if meta.get('session'):
            session = meta['session']
            # Sessions older than 700 might be outdated (adjust threshold as needed)
            if session < 650:
                return 'superseded'

        return 'active'

    def _extract_links(self, filepath: Path, all_doc_paths: set) -> tuple:
        """
        Extract references to other documentation files.

        Returns:
            tuple: (outbound_links, broken_links)
                - outbound_links: list of dicts with target, occurrences, snippets
                - broken_links: list of dicts with raw_ref, reason
        """
        link_data = {}  # target -> {occurrences, snippets}
        broken_links = []

        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Strip fenced code blocks to avoid false positives
            content_no_code = self._strip_code_blocks(content)

            # Get own path for self-reference filtering
            try:
                own_path = str(filepath).split('unified-donkey-betz/')[-1]
            except Exception:
                own_path = filepath.name

            def add_link(raw_ref: str, snippet: str):
                """Helper to add a link with deduplication and snippet tracking."""
                normalized = self._normalize_doc_path(raw_ref, all_doc_paths)

                if normalized:
                    # Skip self-references
                    if normalized == own_path:
                        return

                    if normalized not in link_data:
                        link_data[normalized] = {'occurrences': 0, 'snippets': []}
                    link_data[normalized]['occurrences'] += 1
                    # Keep up to 3 snippets per target
                    if len(link_data[normalized]['snippets']) < 3 and snippet:
                        # Clean and truncate snippet
                        clean_snippet = snippet.strip()[:100]
                        if clean_snippet and clean_snippet not in link_data[normalized]['snippets']:
                            link_data[normalized]['snippets'].append(clean_snippet)
                else:
                    # Track as broken link if it looks like a real doc reference
                    if raw_ref.endswith('.md') and not raw_ref.startswith('http'):
                        broken_links.append({
                            'raw_ref': raw_ref,
                            'reason': 'not_found'
                        })

            # Pattern 1: Markdown links - [text](path/to/file.md)
            for match in re.finditer(r'\[([^\]]*)\]\(([^)]+\.md)\)', content_no_code):
                link_text, link_path = match.groups()
                # Get context around the match
                start = max(0, match.start() - 20)
                end = min(len(content_no_code), match.end() + 30)
                snippet = content_no_code[start:end].replace('\n', ' ')
                add_link(link_path, snippet)

            # Pattern 2: File mentions - SESSION_123_FOO.md or ARCHITECTURE.md
            for match in re.finditer(r'\b(SESSION_\d+[A-Z_]+\.md|[A-Z][A-Z0-9_]+\.md)\b', content_no_code):
                mention = match.group(1)
                start = max(0, match.start() - 20)
                end = min(len(content_no_code), match.end() + 30)
                snippet = content_no_code[start:end].replace('\n', ' ')
                add_link(mention, snippet)

            # Pattern 3: Explicit doc paths - docs/handoffs/FILE.md
            for match in re.finditer(r'(docs/[a-zA-Z0-9_/-]+\.md)', content_no_code):
                doc_path = match.group(1)
                start = max(0, match.start() - 20)
                end = min(len(content_no_code), match.end() + 30)
                snippet = content_no_code[start:end].replace('\n', ' ')
                add_link(doc_path, snippet)

        except Exception as _e:
            logger.warning(
                "build_docs_index._extract_links: swallowed (%s: %s) — degraded",
                type(_e).__name__, _e,
            )

        # Convert to list format
        outbound_links = [
            {
                'target': target,
                'occurrences': data['occurrences'],
                'snippets': data['snippets']
            }
            for target, data in sorted(link_data.items())
        ]

        return outbound_links, broken_links

    def _strip_code_blocks(self, content: str) -> str:
        """Remove fenced code blocks from content to avoid false link detection."""
        # Remove ```...``` blocks
        content = re.sub(r'```[\s\S]*?```', '', content)
        # Remove indented code blocks (4+ spaces at line start)
        content = re.sub(r'^(    |\t).*$', '', content, flags=re.MULTILINE)
        return content

    def _normalize_doc_path(self, link_path: str, all_doc_paths: set) -> Optional[str]:
        """Normalize a document reference to its canonical path."""
        # Clean up the path
        link_path = link_path.strip()

        # Remove leading ./ or ../
        while link_path.startswith('./') or link_path.startswith('../'):
            link_path = re.sub(r'^\.\.?/', '', link_path)

        # Try direct match
        if link_path in all_doc_paths:
            return link_path

        # Try with docs/ prefix
        if f'docs/{link_path}' in all_doc_paths:
            return f'docs/{link_path}'

        # Try just the filename in common locations
        filename = link_path.split('/')[-1]
        for doc_path in all_doc_paths:
            if doc_path.endswith(f'/{filename}') or doc_path == filename:
                return doc_path

        return None

    def _count_lines(self, filepath: Path) -> int:
        """Count lines in a file."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except Exception as _e:
            logger.warning(
                "build_docs_index._count_lines: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return 0

    def _gather_stats(self, docs_dir: Path, base_dir: Path, doc_index: dict) -> dict:
        """Gather statistics for INDEX.md generation."""
        stats = {
            'total_files': len(doc_index['documents']),
            'total_lines': sum(d['lines'] for d in doc_index['documents']),
            'folder_counts': defaultdict(int),
            'recent_files': [],
            'session_files': [],
            'top_level_docs': [],
            'subdirectories': [],
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'status_counts': defaultdict(int),
            'type_counts': defaultdict(int),
            'subsystem_counts': defaultdict(int),
            'with_frontmatter': 0,
            # Graph stats
            'graph': doc_index.get('graph', {}),
        }

        # Process documents from index
        for doc in doc_index['documents']:
            # Count by folder
            folder = doc['folder'].replace('docs/', '').split('/')[0] if doc['folder'] else 'root'
            stats['folder_counts'][folder] += 1

            # Count by status
            stats['status_counts'][doc.get('status', 'unknown')] += 1

            # Count by type
            stats['type_counts'][doc['type']] += 1

            # Count by subsystem
            for subsystem in doc.get('subsystems', []):
                stats['subsystem_counts'][subsystem] += 1

            # Count frontmatter
            if doc.get('has_frontmatter'):
                stats['with_frontmatter'] += 1

            # Track recent files
            if doc['folder'] and doc['folder'] != 'root':
                stats['recent_files'].append({
                    'name': doc['filename'],
                    'path': doc['path'],
                    'folder': folder,
                    'mtime': datetime.fromisoformat(doc['modified_at']),
                    'lines': doc['lines'],
                })

            # Track session files
            if doc.get('session'):
                stats['session_files'].append({
                    'session': doc['session'],
                    'name': doc['filename'],
                    'path': doc['path'],
                    'folder': folder,
                    'mtime': datetime.fromisoformat(doc['modified_at']),
                })

            # Track top-level docs
            if not doc['folder'] or doc['folder'] == 'docs':
                stats['top_level_docs'].append({
                    'name': doc['filename'],
                    'path': doc['path'],
                    'lines': doc['lines'],
                    'mtime': datetime.fromisoformat(doc['modified_at']),
                    'root': doc['folder'] == '',
                })

        # Get subdirectories
        for item in docs_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.') and not item.name.startswith('_'):
                stats['subdirectories'].append(item.name)

        # Sort
        stats['recent_files'].sort(key=lambda x: x['mtime'], reverse=True)
        stats['session_files'].sort(key=lambda x: x['session'], reverse=True)
        stats['folder_counts'] = dict(stats['folder_counts'])
        stats['status_counts'] = dict(stats['status_counts'])
        stats['type_counts'] = dict(stats['type_counts'])
        stats['subsystem_counts'] = dict(stats['subsystem_counts'])

        return stats

    def _extract_current_session(self, base_dir: Path) -> int:
        """Extract current session number from 00-START-NEXT-SESSION.md."""
        start_file = base_dir / '00-START-NEXT-SESSION.md'
        if start_file.exists():
            try:
                content = start_file.read_text()
                match = re.search(r'Session\s+(\d+)', content, re.IGNORECASE)
                if match:
                    return int(match.group(1))
            except Exception as _e:
                logger.warning(
                    "build_docs_index._extract_current_session: swallowed (%s: %s) — degraded",
                    type(_e).__name__, _e,
                )
        return 784

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
            except Exception as _e:
                logger.warning(
                    "build_docs_index._extract_platform_stats: swallowed (%s: %s) — degraded",
                    type(_e).__name__, _e,
                )

        return stats

    def _generate_index(self, stats: dict, base_dir: Path, doc_index: dict) -> str:
        """Generate the INDEX.md content."""
        current_session = self._extract_current_session(base_dir)
        platform_stats = self._extract_platform_stats(base_dir)

        lines = []

        # Machine-readable autogen marker (must be first line for grep/tooling)
        lines.append('<!-- DOC-AUTOGEN: generated by `python manage.py build_docs_index`; do not hand-edit. -->')
        lines.append('')

        # Header
        lines.append('# Unified Donkey Betz - Documentation Index')
        lines.append('')
        lines.append(f'**Generated:** {stats["generated_at"]}')
        lines.append(f'**Current Session:** {current_session}')
        lines.append(f'**Total Documentation:** {stats["total_files"]} files | {stats["total_lines"]:,} lines')
        lines.append('')
        lines.append('> This file is auto-generated by `python manage.py build_docs_index`')
        lines.append('> Machine-readable index: `docs/_index.json`')
        lines.append('')
        lines.append('---')
        lines.append('')

        # Document Status Summary (NEW)
        lines.append('## Document Status')
        lines.append('')
        lines.append('| Status | Count | Description |')
        lines.append('|--------|-------|-------------|')
        status_descriptions = {
            'active': 'Current, maintained documentation',
            'superseded': 'Replaced by newer documents',
            'deprecated': 'No longer recommended',
            'draft': 'Work in progress',
        }
        for status in ['active', 'superseded', 'deprecated', 'draft']:
            count = stats['status_counts'].get(status, 0)
            desc = status_descriptions.get(status, '')
            lines.append(f'| **{status}** | {count} | {desc} |')
        lines.append('')

        # Cross-Reference Graph Summary
        graph = stats.get('graph', {})
        if graph.get('most_referenced'):
            lines.append('## Cross-Reference Graph')
            lines.append('')
            lines.append(f'| Metric | Count |')
            lines.append(f'|--------|-------|')
            lines.append(f'| Total cross-references | {graph.get("total_links", 0):,} |')
            lines.append(f'| Orphan documents | {len(graph.get("orphan_docs", []))} |')
            lines.append(f'| Broken links | {len(graph.get("broken_links", []))} |')
            lines.append('')
            lines.append('### Most Referenced Documents')
            lines.append('')
            lines.append('| Document | References | Title |')
            lines.append('|----------|------------|-------|')
            for ref in graph['most_referenced'][:10]:
                path = ref['path']
                count = ref['count']
                title = ref.get('title', '')[:50]  # Truncate long titles
                lines.append(f'| `{path}` | {count} | {title} |')
            lines.append('')

            # Show broken links if any
            if graph.get('broken_links'):
                lines.append('### Broken Links (need fixing)')
                lines.append('')
                lines.append('| Source | Broken Reference |')
                lines.append('|--------|------------------|')
                for broken in graph['broken_links'][:10]:
                    source = broken.get('source', 'unknown')
                    raw_ref = broken.get('raw_ref', 'unknown')
                    lines.append(f'| `{source}` | `{raw_ref}` |')
                if len(graph['broken_links']) > 10:
                    lines.append(f'| ... | *({len(graph["broken_links"]) - 10} more)* |')
                lines.append('')

        # Core Entry Points
        lines.append('## Core Entry Points')
        lines.append('')
        lines.append('| File | Description | Lines |')
        lines.append('|------|-------------|-------|')
        lines.append('| `00-START-NEXT-SESSION.md` | **START HERE** - Current session priorities | - |')
        lines.append('| `CLAUDE.md` | System overview for AI agents | - |')
        lines.append('| `docs/INDEX.md` | This file - documentation map | - |')
        lines.append('| `docs/_index.json` | Machine-readable index with full metadata | - |')
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

        for sf in stats['session_files'][:20]:
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

        # Subsystem Coverage (NEW)
        lines.append('## Documentation by Subsystem')
        lines.append('')
        lines.append('| Subsystem | Docs | Description |')
        lines.append('|-----------|------|-------------|')

        subsystem_descriptions = {
            'agents': 'Agent architecture and implementations',
            'spiders': 'Data collection spiders',
            'body': 'Body system metaphor',
            'frontend': 'React UI components',
            'backend': 'Django backend',
            'database': 'Models and migrations',
            'api': 'API endpoints',
            'llm': 'LLM integrations',
            'memory': 'Memory and learning systems',
            'integration': 'Cross-system integration',
        }

        for subsystem in sorted(stats['subsystem_counts'].keys()):
            count = stats['subsystem_counts'][subsystem]
            desc = subsystem_descriptions.get(subsystem, '')
            lines.append(f'| {subsystem} | {count} | {desc} |')

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

        # Frontmatter Schema (NEW)
        lines.append('## Frontmatter Schema (Optional)')
        lines.append('')
        lines.append('New documents can include YAML frontmatter for richer metadata:')
        lines.append('')
        lines.append('```yaml')
        lines.append('---')
        lines.append('subsystems: [agents, frontend, api]')
        lines.append('decision_types: [feature, bug_fix]')
        lines.append('status: active  # active|superseded|deprecated|draft')
        lines.append('see_also: [SESSION_123_RELATED.md]')
        lines.append('supersedes: SESSION_100_OLD.md')
        lines.append('---')
        lines.append('```')
        lines.append('')
        lines.append(f'Documents with frontmatter: **{stats["with_frontmatter"]}** / {stats["total_files"]}')
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
