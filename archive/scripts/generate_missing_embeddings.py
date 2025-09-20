#!/usr/bin/env python
"""
Generate embeddings for all documents that don't have them yet.
"""

import os
import sys
import django
from django.db import transaction

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from content.models import Document, DocumentEmbedding
from django.conf import settings
import openai

def generate_embeddings():
    """Generate embeddings for all documents without them."""
    
    # Check for OpenAI API key
    api_key = settings.AI_PROVIDERS.get('OPENAI_API_KEY')
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found in settings")
        return
    
    # Initialize OpenAI client
    client = openai.OpenAI(api_key=api_key)
    
    # Get documents without embeddings
    documents_without_embeddings = Document.objects.filter(
        embeddings__isnull=True
    ).distinct()
    
    count = documents_without_embeddings.count()
    
    if count == 0:
        print("✅ All documents already have embeddings!")
        return
    
    print(f"Found {count} documents without embeddings")
    print("-" * 50)
    
    success_count = 0
    error_count = 0
    
    for doc in documents_without_embeddings:
        try:
            print(f"\n📄 Processing: {doc.title}")
            
            # Get content for embedding
            content_parts = []
            
            # Add title
            content_parts.append(f"Title: {doc.title}")
            
            # Add description if available
            if doc.description:
                content_parts.append(f"Description: {doc.description}")
            
            # Add main content (use processed_content or raw_content)
            content_to_use = doc.processed_content if doc.processed_content else doc.raw_content
            if content_to_use:
                # Limit content length to avoid token limits
                content_parts.append(f"Content: {content_to_use[:3000]}")
            
            # Add tags if available
            if doc.tags and isinstance(doc.tags, list):
                content_parts.append(f"Tags: {', '.join(doc.tags)}")
            
            # Add category if available
            if doc.category:
                content_parts.append(f"Category: {doc.category}")
            
            # Combine all parts
            text_to_embed = "\n\n".join(content_parts)
            
            # Generate embedding using OpenAI
            print("  → Generating embedding...")
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text_to_embed
            )
            
            if response and response.data and len(response.data) > 0:
                embedding_vector = response.data[0].embedding
                
                # Create embedding record
                with transaction.atomic():
                    DocumentEmbedding.objects.create(
                        document=doc,
                        chunk_index=0,  # Single embedding per document
                        chunk_text=text_to_embed[:1000],  # Store first 1000 chars of embedded text
                        chunk_size=len(text_to_embed),
                        overlap_size=0,
                        embedding_vector=embedding_vector,
                        embedding_dimension=len(embedding_vector),
                        embedding_model=response.model,
                        context_before="",
                        context_after="",
                        embedding_cost=0.0,
                        metadata={
                            'model': response.model,
                            'usage': {
                                'prompt_tokens': response.usage.prompt_tokens,
                                'total_tokens': response.usage.total_tokens
                            },
                            'generated_from': 'migration_script',
                            'embedding_dimensions': len(embedding_vector)
                        }
                    )
                print(f"  ✅ Embedding created successfully (dimensions: {len(embedding_vector)})")
                success_count += 1
            else:
                print(f"  ❌ Failed to generate embedding: No embedding returned")
                error_count += 1
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            error_count += 1
    
    print("\n" + "=" * 50)
    print(f"✅ Successfully created embeddings: {success_count}")
    if error_count > 0:
        print(f"❌ Failed embeddings: {error_count}")
    
    # Verify final state
    total_docs = Document.objects.count()
    docs_with_embeddings = Document.objects.filter(embeddings__isnull=False).distinct().count()
    
    print(f"\n📊 Final Status:")
    print(f"  Total documents: {total_docs}")
    print(f"  Documents with embeddings: {docs_with_embeddings}")
    print(f"  Documents without embeddings: {total_docs - docs_with_embeddings}")

if __name__ == '__main__':
    try:
        generate_embeddings()
    except KeyboardInterrupt:
        print("\n\n⚠️ Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)