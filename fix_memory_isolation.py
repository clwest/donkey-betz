#!/usr/bin/env python
"""
CRITICAL FIX: Isolate personal memories from system RAG
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from content.models import Document, DocumentEmbedding
from django.db import transaction
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def isolate_personal_memories():
    """
    Mark all personal documents and their embeddings
    """
    logger.info("🔒 Starting memory isolation")
    
    with transaction.atomic():
        # Find personal documents
        personal_docs = Document.objects.filter(
            title__icontains='personal'
        ) | Document.objects.filter(
            title__icontains='private'
        ) | Document.objects.filter(
            title__icontains='my knowledge'
        )
        
        personal_count = personal_docs.count()
        logger.info(f"Found {personal_count} personal documents")
        
        # Update documents
        for doc in personal_docs:
            if not doc.metadata:
                doc.metadata = {}
            
            doc.metadata['namespace'] = 'personal'
            doc.metadata['is_private'] = True
            doc.metadata['searchable_by_agents'] = False
            doc.save()
            
            # Update associated embeddings
            embeddings = DocumentEmbedding.objects.filter(document=doc)
            for emb in embeddings:
                if not emb.metadata:
                    emb.metadata = {}
                emb.metadata['namespace'] = 'personal'
                emb.metadata['is_private'] = True
                emb.save()
            
            logger.info(f"  Isolated: {doc.title[:50]}")
        
        # Mark system documents
        system_docs = Document.objects.exclude(
            id__in=personal_docs.values_list('id', flat=True)
        )[:1000]  # Do first 1000
        
        for doc in system_docs:
            if not doc.metadata:
                doc.metadata = {}
            if 'namespace' not in doc.metadata:
                doc.metadata['namespace'] = 'system'
                doc.metadata['searchable_by_agents'] = True
                doc.save()
                
                # Update embeddings
                embeddings = DocumentEmbedding.objects.filter(document=doc)
                for emb in embeddings:
                    if not emb.metadata:
                        emb.metadata = {}
                    emb.metadata['namespace'] = 'system'
                    emb.save()
        
        logger.info(f"✅ Isolated {personal_count} personal memories")
        logger.info(f"✅ Marked {len(system_docs)} system documents")
        
        return personal_count


def verify_isolation():
    """
    Verify memories are properly isolated
    """
    personal = Document.objects.filter(metadata__namespace='personal').count()
    system = Document.objects.filter(metadata__namespace='system').count()
    untagged = Document.objects.exclude(
        metadata__has_key='namespace'
    ).count()
    
    print(f"\n📊 Memory Isolation Status:")
    print(f"  Personal (isolated): {personal}")
    print(f"  System (accessible): {system}")
    print(f"  Untagged: {untagged}")
    
    if untagged > 0:
        print(f"  ⚠️  {untagged} documents still need tagging")
    else:
        print("  ✅ All documents properly tagged")
    
    # Check embeddings
    personal_emb = DocumentEmbedding.objects.filter(
        metadata__namespace='personal'
    ).count()
    system_emb = DocumentEmbedding.objects.filter(
        metadata__namespace='system'
    ).count()
    
    print(f"\n📊 Embedding Isolation Status:")
    print(f"  Personal embeddings: {personal_emb}")
    print(f"  System embeddings: {system_emb}")
    
    return personal > 0 and untagged == 0


if __name__ == '__main__':
    print("🚨 EMERGENCY MEMORY ISOLATION")
    print("=" * 60)
    
    # Isolate memories
    isolated = isolate_personal_memories()
    
    # Verify
    is_secure = verify_isolation()
    
    if is_secure:
        print("\n✅ MEMORY ISOLATION COMPLETE - SYSTEM SECURE")
    else:
        print("\n⚠️  MEMORY ISOLATION PARTIAL - MANUAL REVIEW NEEDED")
    
    print("=" * 60)