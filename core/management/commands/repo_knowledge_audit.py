"""
Repo Knowledge Audit Command

Session 786: Creates a single source of truth for document/embedding state.

Outputs:
- Total .md files in repo
- Total docs in Docs Index (_index.json)
- Total Document rows (by status, type, source)
- Total DocumentEmbedding rows
- Orphaned embeddings (parent doc missing)
- Sync status between Docs Index and Document model

Usage:
    python manage.py repo_knowledge_audit
    python manage.py repo_knowledge_audit --json
    python manage.py repo_knowledge_audit --output=audit_report.json
"""

import json
import os
from pathlib import Path
from collections import defaultdict
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Audit repo knowledge: markdown files, docs index, document models, embeddings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--json',
            action='store_true',
            help='Output as JSON only (no formatted text)'
        )
        parser.add_argument(
            '--output',
            type=str,
            help='Save JSON report to file'
        )

    def handle(self, *args, **options):
        report = self.run_audit()

        if options['json']:
            self.stdout.write(json.dumps(report, indent=2))
        else:
            self.print_formatted_report(report)

        if options['output']:
            with open(options['output'], 'w') as f:
                json.dump(report, f, indent=2)
            self.stdout.write(self.style.SUCCESS(f"\nReport saved to: {options['output']}"))

    def run_audit(self) -> dict:
        """Run the complete audit and return a report dict."""
        report = {
            'summary': {},
            'repo_markdown': {},
            'docs_index': {},
            'document_model': {},
            'embeddings': {},
            'sync_status': {},
            'recommendations': []
        }

        # 1. Repo Markdown Files
        repo_md = self.audit_repo_markdown()
        report['repo_markdown'] = repo_md
        report['summary']['repo_markdown_total'] = repo_md['total']

        # 2. Docs Index (_index.json)
        docs_index = self.audit_docs_index()
        report['docs_index'] = docs_index
        report['summary']['docs_index_total'] = docs_index['total']

        # 3. Document Model
        doc_model = self.audit_document_model()
        report['document_model'] = doc_model
        report['summary']['document_model_total'] = doc_model['total']

        # 4. DocumentEmbedding Model
        embeddings = self.audit_embeddings()
        report['embeddings'] = embeddings
        report['summary']['embeddings_total'] = embeddings['total']

        # 5. Sync Status
        sync = self.check_sync_status(docs_index, doc_model)
        report['sync_status'] = sync

        # 6. Generate Recommendations
        report['recommendations'] = self.generate_recommendations(report)

        return report

    def audit_repo_markdown(self) -> dict:
        """Count and categorize all .md files in the repo."""
        base_path = Path(settings.BASE_DIR)

        # Directories to exclude
        exclude_dirs = {'.venv', 'venv', 'venv_ml', 'node_modules', '__pycache__', '.git'}

        md_files = []
        for md_file in base_path.rglob('*.md'):
            # Skip excluded directories
            if any(excluded in md_file.parts for excluded in exclude_dirs):
                continue
            md_files.append(md_file)

        # Categorize by location
        categories = defaultdict(int)
        for f in md_files:
            rel_path = f.relative_to(base_path)
            parts = rel_path.parts

            if 'archive' in str(f).lower():
                categories['archive'] += 1
            elif 'external-project-docs' in parts:
                categories['external_project_docs'] += 1
            elif 'income_builder_outputs' in parts:
                categories['income_builder_outputs'] += 1
            elif 'docs/handoffs' in str(rel_path):
                categories['handoffs'] += 1
            elif 'docs' in parts:
                categories['docs_active'] += 1
            elif rel_path.name in ['CLAUDE.md', 'README.md', '00-START-NEXT-SESSION.md']:
                categories['root_files'] += 1
            else:
                categories['other'] += 1

        return {
            'total': len(md_files),
            'by_category': dict(categories),
            'base_path': str(base_path)
        }

    def audit_docs_index(self) -> dict:
        """Audit the Docs Index (_index.json)."""
        index_path = Path(settings.BASE_DIR) / 'docs' / '_index.json'

        if not index_path.exists():
            return {
                'total': 0,
                'exists': False,
                'error': 'docs/_index.json not found'
            }

        try:
            with open(index_path) as f:
                data = json.load(f)

            documents = data.get('documents', [])

            # Count by status
            by_status = defaultdict(int)
            by_subsystem = defaultdict(int)

            for doc in documents:
                status = doc.get('status', 'unknown')
                by_status[status] += 1

                subsystem = doc.get('subsystem', 'unknown')
                by_subsystem[subsystem] += 1

            return {
                'total': len(documents),
                'exists': True,
                'by_status': dict(by_status),
                'by_subsystem': dict(sorted(by_subsystem.items(), key=lambda x: -x[1])[:10]),
                'index_path': str(index_path)
            }
        except Exception as e:
            return {
                'total': 0,
                'exists': True,
                'error': str(e)
            }

    def audit_document_model(self) -> dict:
        """Audit the Document model in the database."""
        try:
            from content.models import Document, ContentStatus, DocumentType

            total = Document.objects.count()

            # By status
            by_status = {}
            for status_choice in ContentStatus.choices:
                status_code = status_choice[0]
                count = Document.objects.filter(status=status_code).count()
                if count > 0:
                    by_status[status_code] = count

            # By document type
            by_type = {}
            for type_choice in DocumentType.choices:
                type_code = type_choice[0]
                count = Document.objects.filter(document_type=type_code).count()
                if count > 0:
                    by_type[type_code] = count

            # By source
            by_source = {}
            sources = Document.objects.values_list('source', flat=True).distinct()
            for source in sources:
                if source:
                    count = Document.objects.filter(source=source).count()
                    by_source[source] = count

            # Sample documents
            samples = list(Document.objects.values('id', 'title', 'document_type', 'status', 'source')[:5])

            return {
                'total': total,
                'by_status': by_status,
                'by_type': by_type,
                'by_source': by_source,
                'samples': samples
            }
        except Exception as e:
            return {
                'total': 0,
                'error': str(e)
            }

    def audit_embeddings(self) -> dict:
        """Audit DocumentEmbedding model and check for orphans."""
        try:
            from content.models import DocumentEmbedding, Document

            total = DocumentEmbedding.objects.count()

            # By embedding model
            by_model = {}
            models = DocumentEmbedding.objects.values_list('embedding_model', flat=True).distinct()
            for model in models:
                if model:
                    count = DocumentEmbedding.objects.filter(embedding_model=model).count()
                    by_model[model] = count

            # Check for orphaned embeddings (no parent document)
            orphaned_null = DocumentEmbedding.objects.filter(document__isnull=True).count()

            # Documents with embeddings
            docs_with_embeddings = DocumentEmbedding.objects.values('document').distinct().count()

            # Total documents
            total_docs = Document.objects.count()

            # Documents WITHOUT embeddings
            doc_ids_with_embeddings = set(
                DocumentEmbedding.objects.values_list('document_id', flat=True).distinct()
            )
            docs_without_embeddings = Document.objects.exclude(id__in=doc_ids_with_embeddings).count()

            # Average chunks per document
            avg_chunks = total / docs_with_embeddings if docs_with_embeddings > 0 else 0

            return {
                'total': total,
                'by_model': by_model,
                'orphaned_null_document': orphaned_null,
                'documents_with_embeddings': docs_with_embeddings,
                'documents_without_embeddings': docs_without_embeddings,
                'avg_chunks_per_document': round(avg_chunks, 1)
            }
        except Exception as e:
            return {
                'total': 0,
                'error': str(e)
            }

    def check_sync_status(self, docs_index: dict, doc_model: dict) -> dict:
        """Check sync between Docs Index and Document model."""
        docs_index_total = docs_index.get('total', 0)
        doc_model_total = doc_model.get('total', 0)

        # Calculate what's missing
        if docs_index_total > 0 and doc_model_total == 0:
            status = 'docs_index_not_synced'
            message = f'{docs_index_total} docs in index, 0 in Document model - need to sync'
        elif docs_index_total == 0:
            status = 'no_docs_index'
            message = 'Docs Index not found or empty'
        elif docs_index_total == doc_model_total:
            status = 'synced'
            message = 'Docs Index and Document model are in sync'
        elif doc_model_total > docs_index_total:
            status = 'document_model_has_more'
            message = f'Document model has {doc_model_total - docs_index_total} extra entries'
        else:
            status = 'partial_sync'
            message = f'{doc_model_total}/{docs_index_total} docs synced ({round(doc_model_total/docs_index_total*100, 1)}%)'

        return {
            'status': status,
            'message': message,
            'docs_index_total': docs_index_total,
            'document_model_total': doc_model_total,
            'gap': docs_index_total - doc_model_total
        }

    def generate_recommendations(self, report: dict) -> list:
        """Generate actionable recommendations based on audit."""
        recommendations = []

        sync = report['sync_status']

        # Check for sync issues
        if sync['status'] == 'docs_index_not_synced':
            recommendations.append({
                'priority': 'HIGH',
                'issue': 'Docs Index not synced to Document model',
                'action': f"Run: python manage.py sync_docs_index_to_documents",
                'impact': f'{sync["docs_index_total"]} documents will be synced'
            })

        # Check for orphaned embeddings
        embeddings = report['embeddings']
        if embeddings.get('orphaned_null_document', 0) > 0:
            recommendations.append({
                'priority': 'MEDIUM',
                'issue': f'{embeddings["orphaned_null_document"]} orphaned embeddings (null document)',
                'action': 'Clean up orphaned embeddings',
                'impact': 'Reduces database bloat'
            })

        # Check for documents without embeddings
        if embeddings.get('documents_without_embeddings', 0) > 0:
            recommendations.append({
                'priority': 'MEDIUM',
                'issue': f'{embeddings["documents_without_embeddings"]} documents have no embeddings',
                'action': 'Run embedding generation for unembedded documents',
                'impact': 'Enables semantic search for these documents'
            })

        # Check for archive/external content ratio
        repo = report['repo_markdown']
        categories = repo.get('by_category', {})
        archive_count = categories.get('archive', 0) + categories.get('external_project_docs', 0)
        total = repo.get('total', 1)
        if archive_count / total > 0.3:
            recommendations.append({
                'priority': 'LOW',
                'issue': f'{round(archive_count/total*100)}% of markdown is archive/external content',
                'action': 'Consider excluding archive content from embedding',
                'impact': 'Improves retrieval quality, reduces costs'
            })

        if not recommendations:
            recommendations.append({
                'priority': 'INFO',
                'issue': 'No major issues found',
                'action': 'System is in good state',
                'impact': 'N/A'
            })

        return recommendations

    def print_formatted_report(self, report: dict):
        """Print a nicely formatted report."""
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(self.style.SUCCESS("  REPO KNOWLEDGE AUDIT REPORT"))
        self.stdout.write("=" * 70 + "\n")

        # Summary
        summary = report['summary']
        self.stdout.write(self.style.HTTP_INFO("SUMMARY"))
        self.stdout.write("-" * 40)
        self.stdout.write(f"  Repo Markdown Files:     {summary.get('repo_markdown_total', 0):,}")
        self.stdout.write(f"  Docs Index Documents:    {summary.get('docs_index_total', 0):,}")
        self.stdout.write(f"  Document Model Rows:     {summary.get('document_model_total', 0):,}")
        self.stdout.write(f"  DocumentEmbedding Rows:  {summary.get('embeddings_total', 0):,}")
        self.stdout.write("")

        # Repo Markdown Breakdown
        repo = report['repo_markdown']
        self.stdout.write(self.style.HTTP_INFO("REPO MARKDOWN BY CATEGORY"))
        self.stdout.write("-" * 40)
        for cat, count in sorted(repo.get('by_category', {}).items(), key=lambda x: -x[1]):
            self.stdout.write(f"  {cat:30} {count:,}")
        self.stdout.write("")

        # Docs Index
        docs_idx = report['docs_index']
        if docs_idx.get('exists'):
            self.stdout.write(self.style.HTTP_INFO("DOCS INDEX BY STATUS"))
            self.stdout.write("-" * 40)
            for status, count in docs_idx.get('by_status', {}).items():
                self.stdout.write(f"  {status:30} {count:,}")
        self.stdout.write("")

        # Document Model
        doc_model = report['document_model']
        if doc_model.get('total', 0) > 0:
            self.stdout.write(self.style.HTTP_INFO("DOCUMENT MODEL"))
            self.stdout.write("-" * 40)
            self.stdout.write(f"  Total:                   {doc_model['total']:,}")
            if doc_model.get('by_type'):
                self.stdout.write("  By Type:")
                for t, c in doc_model['by_type'].items():
                    self.stdout.write(f"    {t:28} {c:,}")
        self.stdout.write("")

        # Embeddings
        embeddings = report['embeddings']
        self.stdout.write(self.style.HTTP_INFO("EMBEDDINGS"))
        self.stdout.write("-" * 40)
        self.stdout.write(f"  Total Embeddings:        {embeddings.get('total', 0):,}")
        self.stdout.write(f"  Documents with Vectors:  {embeddings.get('documents_with_embeddings', 0):,}")
        self.stdout.write(f"  Orphaned (null doc):     {embeddings.get('orphaned_null_document', 0):,}")
        self.stdout.write(f"  Avg Chunks/Document:     {embeddings.get('avg_chunks_per_document', 0)}")
        self.stdout.write("")

        # Sync Status
        sync = report['sync_status']
        self.stdout.write(self.style.HTTP_INFO("SYNC STATUS"))
        self.stdout.write("-" * 40)
        status_style = self.style.SUCCESS if sync['status'] == 'synced' else self.style.WARNING
        self.stdout.write(f"  Status: {status_style(sync['status'].upper())}")
        self.stdout.write(f"  {sync['message']}")
        if sync['gap'] > 0:
            self.stdout.write(f"  Gap: {sync['gap']:,} documents need syncing")
        self.stdout.write("")

        # Recommendations
        self.stdout.write(self.style.HTTP_INFO("RECOMMENDATIONS"))
        self.stdout.write("-" * 40)
        for rec in report['recommendations']:
            priority = rec['priority']
            if priority == 'HIGH':
                style = self.style.ERROR
            elif priority == 'MEDIUM':
                style = self.style.WARNING
            else:
                style = self.style.SUCCESS
            self.stdout.write(f"  [{style(priority)}] {rec['issue']}")
            self.stdout.write(f"      Action: {rec['action']}")
        self.stdout.write("")

        self.stdout.write("=" * 70 + "\n")
