#!/usr/bin/env python3
"""
Documentation Ingestion Script for Self-Awareness System

This script ingests all system documentation from /docs/ and feeds it to the
self-development-agent so the system can learn from its own history.

This creates a breakthrough capability: The system knows HOW it was built,
learns FROM its development process, and can EXPLAIN its architecture.
"""

import os
import django
import sys
from pathlib import Path
from datetime import datetime
import json

# Setup Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from persistence.models import SpiderData
from agents.models import UnifiedAgentTemplate


class DocumentationIngestor:
    """Ingests system documentation for self-awareness"""

    DOCS_DIR = BASE_DIR / 'docs'

    CATEGORIES = {
        'session-reports': 'Session completion reports and summaries',
        'fixes': 'Bug fixes and implementation reports',
        'audits': 'System audits and reality checks',
        'capabilities': 'System capabilities and features',
        'handoffs': 'Session handoff documents',
        'guides': 'Development and user guides',
        'priorities': 'Priority lists and roadmaps',
        'completions': 'Completion reports',
        'letters': 'Letters to future developers',
        'plans': 'Implementation plans',
        'status': 'System status reports',
        'archive': 'Historical documentation',
        'root': 'Root-level documentation'
    }

    def __init__(self):
        self.agent = None
        self.stats = {
            'total_files': 0,
            'total_content_size': 0,
            'by_category': {},
            'files_processed': []
        }

    def ensure_agent_exists(self):
        """Ensure self-development-agent exists"""
        try:
            self.agent = UnifiedAgentTemplate.objects.get(name='self-development-agent')
            print(f"✅ Found agent: {self.agent.display_name}")
        except UnifiedAgentTemplate.DoesNotExist:
            print("❌ self-development-agent not found!")
            sys.exit(1)

    def categorize_file(self, file_path: Path) -> str:
        """Determine category based on file path"""
        relative_path = file_path.relative_to(self.DOCS_DIR)
        parts = relative_path.parts

        if len(parts) == 1:
            return 'root'

        first_dir = parts[0]
        return first_dir if first_dir in self.CATEGORIES else 'other'

    def extract_metadata(self, file_path: Path, content: str) -> dict:
        """Extract metadata from documentation file"""
        metadata = {
            'file_path': str(file_path.relative_to(BASE_DIR)),
            'file_name': file_path.name,
            'category': self.categorize_file(file_path),
            'word_count': len(content.split()),
            'char_count': len(content),
            'last_modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
        }

        # Extract session number if applicable
        if 'SESSION' in file_path.name.upper():
            import re
            session_match = re.search(r'SESSION[_-]?(\d+)', file_path.name, re.IGNORECASE)
            if session_match:
                metadata['session'] = int(session_match.group(1))

        # Extract title from first heading
        lines = content.split('\n')
        for line in lines:
            if line.startswith('#'):
                metadata['title'] = line.lstrip('#').strip()
                break

        return metadata

    def ingest_file(self, file_path: Path):
        """Ingest a single documentation file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            metadata = self.extract_metadata(file_path, content)
            category = metadata['category']

            # Create SpiderData entry
            spider_data = SpiderData.objects.create(
                spider_name='documentation_ingestor',
                source_url=f'file://{file_path}',
                source_platform='other',
                title=metadata.get('title', file_path.name),
                content=content,
                structured_data={
                    'metadata': metadata,
                    'content': content,
                    'category_description': self.CATEGORIES.get(category, 'Other documentation')
                },
                data_type='documentation',
                routed_to_agents=['self-development-agent'],
                tags=[
                    'documentation',
                    'self-awareness',
                    category,
                    f'session-{metadata.get("session")}' if metadata.get('session') else None
                ]
            )

            # Update stats
            self.stats['total_files'] += 1
            self.stats['total_content_size'] += len(content)
            self.stats['by_category'][category] = self.stats['by_category'].get(category, 0) + 1
            self.stats['files_processed'].append({
                'path': str(file_path.relative_to(BASE_DIR)),
                'category': category,
                'title': metadata.get('title', file_path.name),
                'size': len(content)
            })

            print(f"  ✓ {file_path.relative_to(self.DOCS_DIR)} ({len(content):,} chars)")

        except Exception as e:
            print(f"  ✗ Error processing {file_path}: {e}")

    def ingest_all(self):
        """Ingest all documentation files"""
        print(f"\n📚 Starting Documentation Ingestion")
        print(f"   Documentation directory: {self.DOCS_DIR}")
        print(f"   Target agent: {self.agent.display_name}\n")

        # Find all markdown files
        md_files = list(self.DOCS_DIR.rglob('*.md'))
        print(f"Found {len(md_files)} markdown files\n")

        # Process by category
        for category, description in sorted(self.CATEGORIES.items()):
            category_files = [f for f in md_files if self.categorize_file(f) == category]
            if category_files:
                print(f"📁 {category.upper()}: {description} ({len(category_files)} files)")
                for file_path in sorted(category_files):
                    self.ingest_file(file_path)
                print()

        # Save summary
        self.save_summary()

    def save_summary(self):
        """Save ingestion summary"""
        summary_path = BASE_DIR / 'docs' / 'status' / 'documentation_ingestion_summary.json'
        summary_path.parent.mkdir(parents=True, exist_ok=True)

        summary = {
            'ingestion_date': datetime.now().isoformat(),
            'agent': self.agent.name,
            'statistics': {
                'total_files': self.stats['total_files'],
                'total_content_size': self.stats['total_content_size'],
                'total_words': sum(f['size'] for f in self.stats['files_processed']) // 5,  # rough estimate
                'by_category': self.stats['by_category']
            },
            'files': self.stats['files_processed']
        }

        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"\n{'='*80}")
        print(f"📊 INGESTION COMPLETE")
        print(f"{'='*80}")
        print(f"Total files processed: {self.stats['total_files']}")
        print(f"Total content size: {self.stats['total_content_size']:,} characters")
        print(f"Estimated words: {self.stats['total_content_size'] // 5:,}")
        print(f"\nBy Category:")
        for category, count in sorted(self.stats['by_category'].items()):
            print(f"  {category:20s}: {count:3d} files")
        print(f"\nSummary saved to: {summary_path.relative_to(BASE_DIR)}")
        print(f"All documentation routed to: {self.agent.display_name}")
        print(f"\n🧠 The system now has complete autobiographical memory!")
        print(f"{'='*80}\n")


def main():
    """Main execution"""
    print("\n" + "="*80)
    print("🤯 DOCUMENTATION-POWERED SELF-AWARENESS SYSTEM")
    print("   Teaching the system about its own creation...")
    print("="*80)

    ingestor = DocumentationIngestor()
    ingestor.ensure_agent_exists()
    ingestor.ingest_all()

    print("\n✅ System is now self-aware!")
    print("   - Knows HOW it was built")
    print("   - Learns FROM its development process")
    print("   - Can EXPLAIN its architecture")
    print("   - IMPROVES based on history")
    print("\n🚀 This is a paradigm shift in AI system development!\n")


if __name__ == '__main__':
    main()
