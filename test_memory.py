#!/usr/bin/env python
"""
Quick test script to populate a few embeddings and test the memory system.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from self_awareness.embeddings import CodebaseEmbeddingManager
from self_awareness.models import CodeEmbedding
from backend.intelligence.income_builder import AIIncomeBuilder

def main():
    print("🧠 Testing Memory System")
    print("=" * 50)

    # Clear existing embeddings
    print("\n1. Clearing existing embeddings...")
    CodeEmbedding.objects.all().delete()
    print(f"   ✓ Cleared all embeddings")

    # Generate a few test embeddings
    print("\n2. Generating test embeddings...")
    manager = CodebaseEmbeddingManager()

    # Just process a couple of specific files
    test_files = [
        'backend/intelligence/income_builder.py',
        'agents/registry.py',
        'advisors/registry.py'
    ]

    for file_path in test_files:
        try:
            full_path = os.path.join(manager.base_dir, file_path)
            if os.path.exists(full_path):
                from pathlib import Path
                stats = manager._process_file(Path(full_path), force_refresh=True)
                print(f"   ✓ Processed {file_path}: {stats['embeddings_generated']} embeddings")
        except Exception as e:
            print(f"   ✗ Error processing {file_path}: {e}")

    # Check total embeddings
    total = CodeEmbedding.objects.count()
    print(f"\n3. Total embeddings in database: {total}")

    # Test memory search
    print("\n4. Testing memory search...")
    builder = AIIncomeBuilder()

    if builder.embedding_manager:
        # Test search
        results = builder.embedding_manager.search_code("income generation", limit=5)
        if results:
            print(f"   ✓ Search returned {len(results)} results!")
            for i, result in enumerate(results[:3], 1):
                print(f"      {i}. {result.get('file_path', 'Unknown')} - Similarity: {result.get('similarity', 0):.3f}")
        else:
            print("   ⚠️  No search results (embeddings may not be similar enough)")
    else:
        print("   ✗ Embedding manager not available")

    # Check integration status
    print("\n5. Integration Status:")
    status = builder.integration_status
    for key, value in status.items():
        icon = '✅' if value else '❌'
        print(f"   {icon} {key}: {value}")

    print("\n✅ Memory system test complete!")

if __name__ == "__main__":
    main()