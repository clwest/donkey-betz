"""
Django management command to generate embeddings for the entire codebase.

This command scans the codebase and creates searchable embeddings for all code files,
enabling the memory system to provide context-aware insights and suggestions.
"""

import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from self_awareness.embeddings import CodebaseEmbeddingManager

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Generate embeddings for the entire codebase to enable memory system search'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force regeneration of all embeddings (ignore existing ones)',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit the number of files to process (for testing)',
        )

    def handle(self, *args, **options):
        force_refresh = options.get('force', False)
        limit = options.get('limit')

        self.stdout.write(
            self.style.SUCCESS('🧠 Starting codebase embedding generation...')
        )

        if force_refresh:
            self.stdout.write(
                self.style.WARNING('⚠️  Force refresh enabled - regenerating all embeddings')
            )

        try:
            # Initialize the embedding manager
            manager = CodebaseEmbeddingManager()

            # Display some info about what will be processed
            self.stdout.write(
                self.style.SUCCESS(f'📁 Base directory: {manager.base_dir}')
            )
            self.stdout.write(
                self.style.SUCCESS(f'🤖 Using embedding model: {manager.embedding_model}')
            )

            # Start the embedding process
            start_time = timezone.now()
            self.stdout.write(
                self.style.SUCCESS('⏳ Processing files... (this may take a few minutes)')
            )

            # Generate embeddings with limit if specified
            if limit:
                # For testing, just process a few files manually
                from self_awareness.models import CodeEmbedding
                import os

                code_files = manager._get_code_files()[:limit]
                self.stdout.write(
                    self.style.SUCCESS(f'📁 Processing {limit} files out of {len(manager._get_code_files())} total')
                )

                stats = {
                    'files_processed': 0,
                    'chunks_created': 0,
                    'embeddings_generated': 0,
                    'errors': 0,
                    'skipped': 0
                }

                for file_path in code_files:
                    try:
                        file_stats = manager._process_file(file_path, force_refresh)
                        stats['files_processed'] += 1
                        stats['chunks_created'] += file_stats['chunks_created']
                        stats['embeddings_generated'] += file_stats['embeddings_generated']
                        stats['skipped'] += file_stats['skipped']

                        self.stdout.write(f"   ✓ Processed: {file_path.name}")

                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f"   ✗ Error processing {file_path.name}: {e}")
                        )
                        stats['errors'] += 1

                result = {
                    'status': 'completed',
                    'stats': stats
                }
            else:
                # Full codebase embedding
                result = manager.embed_entire_codebase(force_refresh=force_refresh)

            # Display results
            end_time = timezone.now()
            duration = (end_time - start_time).total_seconds()

            if result['status'] == 'completed':
                stats = result['stats']
                self.stdout.write(
                    self.style.SUCCESS(
                        f"\n✅ Embedding generation completed successfully in {duration:.2f} seconds!"
                    )
                )
                self.stdout.write(
                    self.style.SUCCESS(f"📊 Statistics:")
                )
                self.stdout.write(f"   - Files processed: {stats['files_processed']}")
                self.stdout.write(f"   - Chunks created: {stats['chunks_created']}")
                self.stdout.write(f"   - Embeddings generated: {stats['embeddings_generated']}")
                self.stdout.write(f"   - Files skipped: {stats['skipped']}")
                self.stdout.write(f"   - Errors: {stats['errors']}")

                if stats['embeddings_generated'] > 0:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"\n🎉 Memory system is now ready with {stats['embeddings_generated']} searchable embeddings!"
                        )
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            "💡 The AI can now search through your codebase for context-aware insights."
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            "\n⚠️  No embeddings were generated. Check if there are code files to process."
                        )
                    )

            else:
                self.stdout.write(
                    self.style.ERROR(
                        f"❌ Embedding generation failed: {result.get('error', 'Unknown error')}"
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error generating embeddings: {str(e)}')
            )
            logger.exception("Failed to generate embeddings")
            raise

        # Final summary
        try:
            from self_awareness.models import CodeEmbedding
            total_count = CodeEmbedding.objects.count()
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n📚 Total embeddings in database: {total_count}"
                )
            )
        except Exception as e:
            logger.warning(f"Could not count embeddings: {e}")