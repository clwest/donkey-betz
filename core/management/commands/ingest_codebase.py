"""
Django management command to ingest codebase into embeddings
"""

from django.core.management.base import BaseCommand
from core.codebase_awareness import codebase_awareness
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Ingest the codebase into embeddings for self-awareness'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-ingestion of all files'
        )
    
    def handle(self, *args, **options):
        force_update = options.get('force', False)
        
        self.stdout.write("Starting codebase ingestion...")
        if force_update:
            self.stdout.write(self.style.WARNING("Force update enabled - all files will be re-processed"))
        
        try:
            stats = codebase_awareness.ingest_codebase(force_update=force_update)
            
            self.stdout.write(self.style.SUCCESS("\n✅ Codebase ingestion complete!"))
            self.stdout.write(f"Files processed: {stats['files_processed']}")
            self.stdout.write(f"Files skipped: {stats['files_skipped']}")
            self.stdout.write(f"Files updated: {stats['files_updated']}")
            self.stdout.write(f"Embeddings created: {stats['embeddings_created']}")
            
            if stats['errors'] > 0:
                self.stdout.write(self.style.WARNING(f"Errors encountered: {stats['errors']}"))
            
            # Test search
            self.stdout.write("\n🔍 Testing code search...")
            results = codebase_awareness.search_code("conversation memory save", limit=3)
            
            if results:
                self.stdout.write(self.style.SUCCESS(f"Found {len(results)} relevant code components:"))
                for result in results:
                    self.stdout.write(f"  - {result['component']} in {result['file']} (similarity: {result['similarity']:.2f})")
            else:
                self.stdout.write("No search results found")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
            raise