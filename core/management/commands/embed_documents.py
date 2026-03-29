"""
Management command to trigger document embedding for specific documents.

Usage:
    python manage.py embed_documents <document_id> [<document_id> ...]
    python manage.py embed_documents --all-unembedded
    python manage.py embed_documents --type youtube
"""

from django.core.management.base import BaseCommand
from content.models import Document, DocumentEmbedding


class Command(BaseCommand):
    help = 'Generate embeddings for specified documents'

    def add_arguments(self, parser):
        parser.add_argument('document_ids', nargs='*', help='Document UUIDs to embed')
        parser.add_argument('--all-unembedded', action='store_true', help='Embed all documents with no embeddings')
        parser.add_argument('--type', help='Filter by document_type (e.g., youtube)')
        parser.add_argument('--model', default='openai_small', help='Embedding model (default: openai_small)')
        parser.add_argument('--async', dest='use_async', action='store_true', help='Dispatch via Celery instead of running sync')

    def handle(self, *args, **options):
        model = options['model']
        doc_ids = options['document_ids']

        if options['all_unembedded'] or options['type']:
            qs = Document.objects.all()
            if options['type']:
                qs = qs.filter(document_type=options['type'])
            # Find documents with no embeddings
            embedded_ids = DocumentEmbedding.objects.values_list('document_id', flat=True).distinct()
            qs = qs.exclude(id__in=embedded_ids).filter(raw_content__gt='')
            doc_ids = list(qs.values_list('id', flat=True))
            self.stdout.write(f"Found {len(doc_ids)} unembedded documents")

        if not doc_ids:
            self.stdout.write(self.style.WARNING('No documents to process'))
            return

        for doc_id in doc_ids:
            try:
                doc = Document.objects.get(id=doc_id)
            except Document.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Document {doc_id} not found'))
                continue

            content_len = len(doc.raw_content or '')
            self.stdout.write(f"Processing: {doc.title} ({content_len} chars)")

            if options['use_async']:
                from core.tasks import generate_document_embeddings
                task = generate_document_embeddings.delay(str(doc_id), model)
                self.stdout.write(self.style.SUCCESS(f"  Dispatched Celery task: {task.id}"))
            else:
                from content.embeddings import RAGSystem
                from content.models import EmbeddingModel
                model_map = {
                    'openai_small': EmbeddingModel.OPENAI_SMALL,
                    'openai_large': EmbeddingModel.OPENAI_LARGE,
                }
                rag = RAGSystem()
                model_enum = model_map.get(model, EmbeddingModel.OPENAI_SMALL)
                success = rag.process_document_for_rag_sync(doc, model_enum)
                chunks = DocumentEmbedding.objects.filter(document=doc).count()
                if success:
                    self.stdout.write(self.style.SUCCESS(f"  Embedded: {chunks} chunks"))
                else:
                    self.stdout.write(self.style.ERROR(f"  Failed to embed"))
