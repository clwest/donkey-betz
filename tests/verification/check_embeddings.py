# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python3
"""
Script to check what content is stored in the embeddings
"""

import os
import sys
import django
import json
from collections import Counter, defaultdict

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.append('/Users/donkeyking/development/unified-donkey-betz')
django.setup()

from django.db.models import Count, Avg, Max, Min
from content.models import Document, DocumentEmbedding
from self_awareness.models import CodeEmbedding


def check_document_embeddings():
    """Check what's stored in document embeddings"""
    print("\n" + "="*80)
    print("📚 DOCUMENT EMBEDDINGS ANALYSIS")
    print("="*80)
    
    # Total counts
    total_docs = Document.objects.count()
    total_embeddings = DocumentEmbedding.objects.count()
    
    print(f"\n📊 Overall Statistics:")
    print(f"   Total Documents: {total_docs:,}")
    print(f"   Total Embeddings: {total_embeddings:,}")
    
    if total_embeddings > 0:
        avg_embeddings_per_doc = total_embeddings / max(total_docs, 1)
        print(f"   Average Embeddings per Document: {avg_embeddings_per_doc:.1f}")
    
    # Document types
    print(f"\n📁 Document Types:")
    doc_types = Document.objects.values('document_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    if doc_types:
        for dt in doc_types[:10]:  # Top 10 types
            print(f"   • {dt['document_type'] or 'unspecified'}: {dt['count']:,} documents")
    else:
        print("   No documents found")
    
    # Sample document content
    print(f"\n📝 Sample Documents (first 10):")
    sample_docs = Document.objects.all()[:10]
    
    if sample_docs:
        for doc in sample_docs:
            title = doc.title[:60] + "..." if len(doc.title) > 60 else doc.title
            description = doc.description[:100] + "..." if doc.description and len(doc.description) > 100 else (doc.description or "No description")
            print(f"\n   📄 Title: {title}")
            print(f"      Type: {doc.document_type or 'unspecified'}")
            print(f"      Description: {description}")
            if doc.file_path:
                print(f"      File: {doc.file_path}")
            
            # Check embeddings for this document
            doc_embeddings = DocumentEmbedding.objects.filter(document=doc).count()
            if doc_embeddings > 0:
                sample_embedding = DocumentEmbedding.objects.filter(document=doc).first()
                print(f"      Embeddings: {doc_embeddings} chunks")
                print(f"      Model: {sample_embedding.embedding_model}")
                print(f"      Dimension: {sample_embedding.embedding_dimension}")
                print(f"      Sample Chunk: {sample_embedding.chunk_text[:100]}...")
    else:
        print("   No documents found in database")
    
    # Embedding models used
    print(f"\n🤖 Embedding Models Used:")
    models_used = DocumentEmbedding.objects.values('embedding_model').annotate(
        count=Count('id'),
        avg_dimension=Avg('embedding_dimension')
    ).order_by('-count')
    
    if models_used:
        for model in models_used:
            print(f"   • {model['embedding_model']}: {model['count']:,} embeddings")
            print(f"     Dimension: {model['avg_dimension']:.0f}")
    else:
        print("   No embedding models found")
    
    # Chunk statistics
    print(f"\n📊 Chunk Statistics:")
    chunk_stats = DocumentEmbedding.objects.aggregate(
        avg_chunk_size=Avg('chunk_size'),
        max_chunk_size=Max('chunk_size'),
        min_chunk_size=Min('chunk_size'),
        total_chunks=Count('id')
    )
    
    if chunk_stats['total_chunks'] > 0:
        print(f"   Average Chunk Size: {chunk_stats['avg_chunk_size']:.0f} characters")
        print(f"   Max Chunk Size: {chunk_stats['max_chunk_size']:,} characters")
        print(f"   Min Chunk Size: {chunk_stats['min_chunk_size']:,} characters")
        print(f"   Total Chunks: {chunk_stats['total_chunks']:,}")
    
    # Search for specific content patterns
    print(f"\n🔍 Content Pattern Analysis:")
    
    # Sample some embedding chunks to analyze content
    sample_chunks = DocumentEmbedding.objects.values_list('chunk_text', flat=True)[:1000]
    
    if sample_chunks:
        content_patterns = {
            'Code': 0,
            'Documentation': 0,
            'API': 0,
            'Sports/Betting': 0,
            'AI/ML': 0,
            'Tutorial': 0,
            'Research': 0,
            'News': 0,
            'Technical': 0,
            'Business': 0
        }
        
        keywords = {
            'Code': ['function', 'class', 'def', 'import', 'return', 'if', 'for', 'while'],
            'Documentation': ['documentation', 'docs', 'readme', 'guide', 'manual'],
            'API': ['api', 'endpoint', 'request', 'response', 'rest', 'graphql'],
            'Sports/Betting': ['sports', 'betting', 'odds', 'game', 'team', 'player', 'score'],
            'AI/ML': ['ai', 'ml', 'machine learning', 'neural', 'model', 'training', 'embedding'],
            'Tutorial': ['tutorial', 'how to', 'step by step', 'learn', 'example'],
            'Research': ['research', 'study', 'analysis', 'findings', 'methodology'],
            'News': ['news', 'article', 'report', 'update', 'announcement'],
            'Technical': ['technical', 'system', 'architecture', 'design', 'implementation'],
            'Business': ['business', 'strategy', 'market', 'customer', 'revenue']
        }
        
        for chunk in sample_chunks:
            chunk_lower = chunk.lower()
            for pattern, pattern_keywords in keywords.items():
                if any(keyword in chunk_lower for keyword in pattern_keywords):
                    content_patterns[pattern] += 1
        
        print("   Content Categories Found (from sample of 1000 chunks):")
        sorted_patterns = sorted(content_patterns.items(), key=lambda x: x[1], reverse=True)
        for pattern, count in sorted_patterns:
            if count > 0:
                percentage = (count / len(ample_chunks)) * 100
                print(f"   • {pattern}: {count} chunks ({percentage:.1f}%)")
    else:
        print("   No embedding chunks available for analysis")


def check_code_embeddings():
    """Check what's stored in code embeddings"""
    print("\n" + "="*80)
    print("💻 CODE EMBEDDINGS ANALYSIS")
    print("="*80)
    
    total_code_embeddings = CodeEmbedding.objects.count()
    print(f"\n📊 Code Embeddings Statistics:")
    print(f"   Total Code Embeddings: {total_code_embeddings:,}")
    
    if total_code_embeddings > 0:
        # File types
        print(f"\n📁 File Types Embedded:")
        file_types = CodeEmbedding.objects.values('file_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        for ft in file_types[:10]:
            print(f"   • {ft['file_type'] or 'unknown'}: {ft['count']:,} embeddings")
        
        # Sample code embeddings
        print(f"\n💾 Sample Code Files (first 10):")
        sample_code = CodeEmbedding.objects.all()[:10]
        
        for code in sample_code:
            print(f"\n   📄 File: {code.file_path}")
            print(f"      Type: {code.file_type}")
            print(f"      Function: {code.function_name or 'N/A'}")
            print(f"      Class: {code.class_name or 'N/A'}")
            if code.code_snippet:
                snippet = code.code_snippet[:100] + "..." if len(code.code_snippet) > 100 else code.code_snippet
                print(f"      Code Preview: {snippet}")
        
        # Analyze code patterns
        print(f"\n🔍 Code Pattern Analysis:")
        
        # Count by programming constructs
        functions = CodeEmbedding.objects.filter(function_name__isnull=False).count()
        classes = CodeEmbedding.objects.filter(class_name__isnull=False).count()
        modules = CodeEmbedding.objects.values('module_path').distinct().count()
        
        print(f"   • Functions embedded: {functions:,}")
        print(f"   • Classes embedded: {classes:,}")
        print(f"   • Unique modules: {modules:,}")
        
        # Top modules
        print(f"\n📦 Top Modules:")
        top_modules = CodeEmbedding.objects.values('module_path').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        for module in top_modules:
            if module['module_path']:
                print(f"   • {module['module_path']}: {module['count']:,} embeddings")
    else:
        print("   No code embeddings found in database")


def analyze_embedding_sources():
    """Analyze the sources of embeddings"""
    print("\n" + "="*80)
    print("🔍 EMBEDDING SOURCE ANALYSIS")
    print("="*80)
    
    # Check for documents with metadata
    docs_with_metadata = Document.objects.exclude(metadata__isnull=True).exclude(metadata={})
    
    if docs_with_metadata.exists():
        print(f"\n📋 Documents with Metadata: {docs_with_metadata.count():,}")
        
        # Analyze metadata patterns
        metadata_keys = defaultdict(int)
        metadata_sources = defaultdict(int)
        
        for doc in docs_with_metadata[:100]:  # Sample first 100
            if doc.metadata:
                for key in doc.metadata.keys():
                    metadata_keys[key] += 1
                
                # Check for source information
                if 'source' in doc.metadata:
                    metadata_sources[doc.metadata['source']] += 1
                elif 'url' in doc.metadata:
                    metadata_sources['web'] += 1
                elif 'file_path' in doc.metadata:
                    metadata_sources['file'] += 1
        
        print("\n   Common Metadata Fields:")
        for key, count in sorted(metadata_keys.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   • {key}: {count} documents")
        
        if metadata_sources:
            print("\n   Document Sources:")
            for source, count in sorted(metadata_sources.items(), key=lambda x: x[1], reverse=True):
                print(f"   • {source}: {count} documents")
    
    # Check document creation dates to understand when content was added
    print(f"\n📅 Content Timeline:")
    
    oldest_doc = Document.objects.order_by('created_at').first()
    newest_doc = Document.objects.order_by('-created_at').first()
    
    if oldest_doc and newest_doc:
        print(f"   Oldest Document: {oldest_doc.created_at.strftime('%Y-%m-%d %H:%M')}")
        print(f"   Newest Document: {newest_doc.created_at.strftime('%Y-%m-%d %H:%M')}")
        
        # Documents by date
        from django.db.models.functions import TruncDate
        docs_by_date = Document.objects.annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('-date')[:10]
        
        if docs_by_date:
            print("\n   Recent Activity (documents created):")
            for entry in docs_by_date:
                if entry['date']:
                    print(f"   • {entry['date'].strftime('%Y-%m-%d')}: {entry['count']:,} documents")


def main():
    """Main function to check all embeddings"""
    print("\n" + "="*80)
    print("🔍 CHECKING EMBEDDING CONTENT IN UNIFIED AI PLATFORM")
    print("="*80)
    
    try:
        # Check document embeddings
        check_document_embeddings()
        
        # Check code embeddings
        check_code_embeddings()
        
        # Analyze sources
        analyze_embedding_sources()
        
        print("\n" + "="*80)
        print("✅ EMBEDDING ANALYSIS COMPLETE")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()