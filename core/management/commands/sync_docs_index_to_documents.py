"""
Sync Docs Index to Document Model

Session 786: Syncs documents from docs/_index.json to the Document model.

This enables:
- Embedding generation for curated documentation
- Semantic search across the knowledge base
- Proper scoping (curated vs uncurated)

Usage:
    python manage.py sync_docs_index_to_documents
    python manage.py sync_docs_index_to_documents --dry-run
    python manage.py sync_docs_index_to_documents --active-only
    python manage.py sync_docs_index_to_documents --embed
"""

import json
import hashlib
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone

from content.models import Document, DocumentType, ContentStatus, ContentSource


# Map docs index types to DocumentType
TYPE_MAPPING = {
    'session_start': DocumentType.MARKDOWN,
    'handoff': DocumentType.MARKDOWN,
    'audit': DocumentType.MARKDOWN,
    'guide': DocumentType.MARKDOWN,
    'index': DocumentType.MARKDOWN,
    'readme': DocumentType.MARKDOWN,
    'api': DocumentType.MARKDOWN,
    'architecture': DocumentType.MARKDOWN,
    'feature': DocumentType.MARKDOWN,
    'report': DocumentType.MARKDOWN,
    'plan': DocumentType.MARKDOWN,
    'reference': DocumentType.MARKDOWN,
    'changelog': DocumentType.MARKDOWN,
    'unknown': DocumentType.MARKDOWN,
}

# Map docs index status to ContentStatus
STATUS_MAPPING = {
    'active': ContentStatus.PROCESSED,
    'superseded': ContentStatus.ARCHIVED,
    'deprecated': ContentStatus.ARCHIVED,
    'draft': ContentStatus.PENDING,
}


class Command(BaseCommand):
    help = 'Sync documents from docs/_index.json to the Document model'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be synced without making changes'
        )
        parser.add_argument(
            '--active-only',
            action='store_true',
            help='Only sync active (non-superseded) documents'
        )
        parser.add_argument(
            '--embed',
            action='store_true',
            help='Generate embeddings after syncing'
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit number of documents to sync (for testing)'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        active_only = options['active_only']
        limit = options.get('limit')

        # Load docs index
        index_path = Path(settings.BASE_DIR) / 'docs' / '_index.json'
        if not index_path.exists():
            self.stderr.write(self.style.ERROR('docs/_index.json not found'))
            return

        with open(index_path) as f:
            data = json.load(f)

        documents = data.get('documents', [])
        self.stdout.write(f"Found {len(documents)} documents in Docs Index")

        # Filter by status if requested
        if active_only:
            documents = [d for d in documents if d.get('status') == 'active']
            self.stdout.write(f"Filtered to {len(documents)} active documents")

        # Apply limit if specified
        if limit:
            documents = documents[:limit]
            self.stdout.write(f"Limited to {limit} documents")

        # Track stats
        stats = {
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0
        }

        base_path = Path(settings.BASE_DIR)

        # Get or create system user for document ownership
        from django.contrib.auth import get_user_model
        User = get_user_model()
        system_user, _ = User.objects.get_or_create(
            username='system',
            defaults={'email': 'system@localhost', 'is_active': False}
        )

        for idx, doc_data in enumerate(documents):
            try:
                result = self.sync_document(doc_data, base_path, dry_run, system_user)
                stats[result] += 1

                # Progress indicator
                if (idx + 1) % 100 == 0:
                    self.stdout.write(f"  Processed {idx + 1}/{len(documents)}...")

            except Exception as e:
                stats['errors'] += 1
                self.stderr.write(self.style.ERROR(f"Error syncing {doc_data.get('path')}: {e}"))

        # Print summary
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS("SYNC COMPLETE" if not dry_run else "DRY RUN COMPLETE"))
        self.stdout.write("=" * 50)
        self.stdout.write(f"  Created:  {stats['created']}")
        self.stdout.write(f"  Updated:  {stats['updated']}")
        self.stdout.write(f"  Skipped:  {stats['skipped']}")
        self.stdout.write(f"  Errors:   {stats['errors']}")

        # Embed if requested
        if options['embed'] and not dry_run and stats['created'] > 0:
            self.stdout.write("\nGenerating embeddings...")
            self.generate_embeddings()

    # =========================================================================
    # Session 1234 D9 — type-aware retrieval enrichment helpers
    # =========================================================================
    #
    # The doc-drift investigation at Session 1234 close showed that the
    # Document table flattens everything to (document_type='markdown',
    # category='', tags=[], document_class='reference', is_pinned=False).
    # Retrieval surfaces (kb_tool, core.rag_integration) had no per-row
    # differentiator beyond title text, so a superseded 2025 handoff
    # competed equally with a current 2026 spec in semantic search.
    #
    # The fields below are all live on the existing Document model and
    # cost nothing to populate at sync time. They give downstream
    # retrieval real filter axes:
    #   category       → folder-grained filter ('handoffs', 'specs', …)
    #   tags           → subsystems list for secondary filter / facets
    #   document_class → semantic type ('handoff', 'spec', 'narrative', …)
    #   is_pinned      → "always prefer in retrieval" for active narratives/
    #                    specs/indexes — the docs Chris/Rigby cite by name
    #   retrieval_boost → ranking weight; pinned active ≫ default ≫ stale

    _PINNED_TYPES = frozenset({
        'narrative', 'spec', 'index', 'guide', 'architecture',
    })

    _STATUS_BOOST = {
        'active': 1.5,
        'draft': 0.8,
        'processed': 1.0,
        'superseded': 0.4,
        'archived': 0.3,
    }

    def _enrichment_fields(self, doc_data: dict) -> dict:
        """Return the type-aware fields to write on create + update.

        Centralized so the existing-update path (which silently dropped
        these pre-D9) and the create path emit the same enrichment.
        """
        folder = (doc_data.get('folder') or '').strip()
        idx_type = (doc_data.get('type') or '').strip().lower() or 'reference'
        idx_status = (doc_data.get('status') or '').strip().lower() or 'active'

        # category: folder basename without leading 'docs/' — e.g. 'handoffs',
        # 'specs', 'narratives', 'topics', 'audits'. Root-level docs (CLAUDE.md,
        # README.md) get the file's own basename for a stable category.
        if folder.startswith('docs/'):
            category = folder[len('docs/'):].split('/', 1)[0] or 'root'
        elif folder == 'docs':
            category = 'root'
        elif folder:
            category = folder.split('/', 1)[0]
        else:
            category = 'root'

        # tags: subsystems list + a 'session-N' tag if the path is a handoff
        tags = list(doc_data.get('subsystems') or [])
        path = doc_data.get('path', '')
        if 'handoffs/SESSION_' in path:
            import re as _re
            m = _re.search(r'SESSION_(\d+)', path)
            if m:
                tags.append(f'session-{m.group(1)}')

        # is_pinned: active narrative/spec/index/guide/architecture docs.
        # These are the docs Rigby should ALWAYS prefer when relevant —
        # not handoffs (those are session-specific history) and not audits
        # (those age out).
        is_pinned = (idx_status == 'active' and idx_type in self._PINNED_TYPES)

        # retrieval_boost: status × pinned. Pinned gets a flat multiplier
        # over the status floor.
        boost = self._STATUS_BOOST.get(idx_status, 1.0)
        if is_pinned:
            boost = max(boost, 1.5)

        return {
            'category': category,
            'tags': tags,
            'document_class': idx_type,
            'is_pinned': is_pinned,
            'retrieval_boost': boost,
        }

    def sync_document(self, doc_data: dict, base_path: Path, dry_run: bool, owner) -> str:
        """Sync a single document from index to Document model."""
        path = doc_data.get('path', '')

        # Paths in _index.json are relative to repo root
        # Some start with 'docs/' and some don't (CLAUDE.md, README.md, etc.)
        file_path = base_path / path

        # Check if file exists
        if not file_path.exists():
            return 'skipped'

        # Read file content
        try:
            content = file_path.read_text(errors='ignore')
        except Exception:
            return 'errors'

        # Generate content hash for deduplication
        content_hash = hashlib.sha256(content.encode()).hexdigest()

        # Session 1234 D9: shared enrichment fields for both create + update.
        enrich = self._enrichment_fields(doc_data)

        # Check if document already exists (use path as-is from index)
        existing = Document.objects.filter(
            file_path=path
        ).first()

        if existing:
            # Check if content changed
            if existing.content_hash == content_hash:
                return 'skipped'
            else:
                # Update existing document
                if not dry_run:
                    existing.raw_content = content
                    existing.processed_content = content
                    existing.content_hash = content_hash
                    existing.word_count = len(content.split())
                    existing.file_size = doc_data.get('size_bytes', 0)
                    # Session 1234 D9: also refresh enrichment fields on
                    # content change. Pre-D9 these silently stayed at the
                    # row's first-sync values forever.
                    existing.category = enrich['category']
                    existing.tags = enrich['tags']
                    existing.document_class = enrich['document_class']
                    existing.is_pinned = enrich['is_pinned']
                    existing.retrieval_boost = enrich['retrieval_boost']
                    existing.updated_at = timezone.now()
                    existing.save()
                return 'updated'

        # Create new document
        if dry_run:
            return 'created'

        doc_type = TYPE_MAPPING.get(doc_data.get('type', 'unknown'), DocumentType.MARKDOWN)
        doc_status = STATUS_MAPPING.get(doc_data.get('status', 'active'), ContentStatus.PROCESSED)

        # Build metadata
        metadata = {
            'docs_index_type': doc_data.get('type'),
            'docs_index_status': doc_data.get('status'),
            'subsystems': doc_data.get('subsystems', []),
            'folder': doc_data.get('folder', ''),
            'inbound_links_count': doc_data.get('inbound_links_count', 0),
            'outbound_links': doc_data.get('outbound_links', []),
            'has_frontmatter': doc_data.get('has_frontmatter', False),
            'scope': 'docs_index',  # Mark as curated
        }

        Document.objects.create(
            title=doc_data.get('title', path),
            description=f"Synced from {path}",
            document_type=doc_type,
            file_path=path,
            original_filename=doc_data.get('filename', ''),
            file_size=doc_data.get('size_bytes', 0),
            mime_type='text/markdown',
            raw_content=content,
            processed_content=content,
            content_hash=content_hash,
            status=doc_status,
            source=ContentSource.IMPORTED,
            language='en',
            word_count=len(content.split()),
            extracted_metadata=metadata,
            owner=owner,
            # Session 1234 D9 — type-aware retrieval enrichment
            category=enrich['category'],
            tags=enrich['tags'],
            document_class=enrich['document_class'],
            is_pinned=enrich['is_pinned'],
            retrieval_boost=enrich['retrieval_boost'],
        )

        return 'created'

    def generate_embeddings(self):
        """Generate embeddings for newly synced documents."""
        try:
            from core.services.embedding_service import EmbeddingService
            from content.models import DocumentEmbedding, EmbeddingModel

            service = EmbeddingService()

            # Get documents without embeddings
            docs_with_embeddings = DocumentEmbedding.objects.values_list('document_id', flat=True).distinct()
            docs_needing_embeddings = Document.objects.exclude(id__in=docs_with_embeddings)

            count = docs_needing_embeddings.count()
            self.stdout.write(f"Found {count} documents needing embeddings")

            for idx, doc in enumerate(docs_needing_embeddings):
                try:
                    # Chunk the content
                    chunks = self.chunk_content(doc.processed_content)

                    for chunk_idx, chunk in enumerate(chunks):
                        # Generate embedding
                        embedding = service.create_embedding(
                            text=chunk,
                            model='text-embedding-3-small',
                            agent_name='docs_index_sync'
                        )

                        if embedding and embedding.embedding:
                            from content.embeddings import _derive_source_type
                            DocumentEmbedding.objects.create(
                                document=doc,
                                chunk_text=chunk,
                                chunk_size=len(chunk),
                                chunk_index=chunk_idx,
                                embedding_vector=embedding.embedding,
                                embedding_dimension=len(embedding.embedding),
                                embedding_model=EmbeddingModel.OPENAI_SMALL,
                                source_type=_derive_source_type(doc),
                                ingested_via='sync_docs',
                            )

                    if (idx + 1) % 10 == 0:
                        self.stdout.write(f"  Embedded {idx + 1}/{count} documents...")

                except Exception as e:
                    self.stderr.write(f"Error embedding doc {doc.id}: {e}")

            self.stdout.write(self.style.SUCCESS(f"Embedding complete!"))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Embedding failed: {e}"))

    def chunk_content(self, content: str, chunk_size: int = 1000, overlap: int = 200) -> list:
        """Split content into overlapping chunks."""
        if len(content) <= chunk_size:
            return [content]

        chunks = []
        start = 0

        while start < len(content):
            end = start + chunk_size

            # Try to break at sentence or paragraph boundary
            if end < len(content):
                # Look for paragraph break
                para_break = content.rfind('\n\n', start, end)
                if para_break > start + chunk_size // 2:
                    end = para_break + 2
                else:
                    # Look for sentence break
                    sentence_break = content.rfind('. ', start, end)
                    if sentence_break > start + chunk_size // 2:
                        end = sentence_break + 2

            chunks.append(content[start:end].strip())
            start = end - overlap

        return chunks
