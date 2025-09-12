#!/usr/bin/env python
"""
Batch Document Tagging Script - Tags all remaining documents with appropriate namespaces
Part of Memory Isolation Security Implementation
"""

import os
import sys
import django
import time
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from content.models import Document, DocumentEmbedding
from django.db import transaction
from django.db.models import Q
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DocumentClassifier:
    """
    Intelligent document classifier for namespace assignment
    """
    
    # Keywords that indicate personal content
    PERSONAL_INDICATORS = [
        'personal', 'private', 'my knowledge', 'remember',
        'diary', 'journal', 'secret', 'confidential',
        'my notes', 'todo', 'reminder', 'password'
    ]
    
    # Keywords that indicate agent-specific content
    AGENT_INDICATORS = [
        'agent execution', 'agent log', 'execution history',
        'agent performance', 'learning outcome', 'agent metric'
    ]
    
    # Keywords that indicate system documentation
    SYSTEM_INDICATORS = [
        'documentation', 'api', 'readme', 'guide', 'tutorial',
        'reference', 'specification', 'architecture', 'design',
        'implementation', 'code', 'function', 'class', 'method'
    ]
    
    def classify_document(self, doc: Document) -> str:
        """
        Classify a document into appropriate namespace
        """
        # Check title and content
        title_lower = (doc.title or '').lower()
        content_lower = (doc.raw_content or '')[:1000].lower()  # Check first 1000 chars
        combined = f"{title_lower} {content_lower}"
        
        # Check for personal indicators
        for indicator in self.PERSONAL_INDICATORS:
            if indicator in combined:
                return 'personal'
        
        # Check source metadata
        if doc.metadata:
            source = doc.metadata.get('source', '').lower()
            if 'personal' in source or 'user' in source:
                return 'personal'
        
        # Check for agent indicators
        for indicator in self.AGENT_INDICATORS:
            if indicator in combined:
                return 'agent_memory'
        
        # Check for system indicators
        for indicator in self.SYSTEM_INDICATORS:
            if indicator in combined:
                return 'system'
        
        # Check file paths for code
        if doc.file_path:
            path_lower = doc.file_path.lower()
            if any(ext in path_lower for ext in ['.py', '.js', '.tsx', '.ts', '.html', '.css']):
                return 'system'
            if 'test' in path_lower or 'spec' in path_lower:
                return 'system'
        
        # Default to system for safety (not personal)
        return 'system'


def batch_tag_documents(batch_size: int = 100, max_documents: int = None):
    """
    Tag documents in batches with progress tracking
    """
    classifier = DocumentClassifier()
    
    # Get untagged documents
    untagged_query = Document.objects.exclude(
        metadata__has_key='namespace'
    )
    
    total_untagged = untagged_query.count()
    logger.info(f"Found {total_untagged} untagged documents")
    
    if total_untagged == 0:
        logger.info("No untagged documents found!")
        return
    
    # Limit processing if specified
    if max_documents:
        total_to_process = min(total_untagged, max_documents)
    else:
        total_to_process = total_untagged
    
    logger.info(f"Will process {total_to_process} documents in batches of {batch_size}")
    
    # Statistics
    stats = {
        'personal': 0,
        'system': 0,
        'agent_memory': 0,
        'public': 0,
        'errors': 0
    }
    
    processed = 0
    start_time = time.time()
    
    # Process in batches
    while processed < total_to_process:
        batch_start = time.time()
        
        # Get next batch
        batch = untagged_query[:batch_size]
        
        if not batch:
            break
        
        with transaction.atomic():
            for doc in batch:
                try:
                    # Classify document
                    namespace = classifier.classify_document(doc)
                    
                    # Update metadata
                    if not doc.metadata:
                        doc.metadata = {}
                    
                    doc.metadata.update({
                        'namespace': namespace,
                        'tagged_at': datetime.now().isoformat(),
                        'tagged_by': 'batch_tag_documents',
                        'searchable_by_agents': namespace != 'personal',
                        'is_private': namespace == 'personal'
                    })
                    
                    doc.save()
                    
                    # Update associated embeddings
                    embeddings = DocumentEmbedding.objects.filter(document=doc)
                    for emb in embeddings:
                        if not emb.metadata:
                            emb.metadata = {}
                        emb.metadata.update({
                            'namespace': namespace,
                            'is_private': namespace == 'personal'
                        })
                        emb.save()
                    
                    stats[namespace] += 1
                    processed += 1
                    
                except Exception as e:
                    logger.error(f"Error processing document {doc.id}: {e}")
                    stats['errors'] += 1
                    processed += 1
        
        # Progress update
        batch_time = time.time() - batch_start
        total_time = time.time() - start_time
        rate = processed / total_time if total_time > 0 else 0
        eta = (total_to_process - processed) / rate if rate > 0 else 0
        
        logger.info(f"Progress: {processed}/{total_to_process} "
                   f"({processed*100/total_to_process:.1f}%) "
                   f"Rate: {rate:.1f} docs/sec "
                   f"ETA: {eta:.0f}s")
        
        # Show distribution
        if processed % 500 == 0:
            logger.info(f"Distribution: {stats}")
    
    # Final report
    total_time = time.time() - start_time
    logger.info("=" * 60)
    logger.info("BATCH TAGGING COMPLETE")
    logger.info(f"Processed: {processed} documents in {total_time:.1f} seconds")
    logger.info(f"Rate: {processed/total_time:.1f} documents/second")
    logger.info("Final distribution:")
    for namespace, count in stats.items():
        if namespace != 'errors':
            percentage = (count / processed * 100) if processed > 0 else 0
            logger.info(f"  {namespace}: {count} ({percentage:.1f}%)")
    if stats['errors'] > 0:
        logger.warning(f"  Errors: {stats['errors']}")
    logger.info("=" * 60)
    
    return stats


def verify_tagging():
    """
    Verify tagging results
    """
    logger.info("\nVERIFYING TAGGING RESULTS")
    logger.info("=" * 60)
    
    total = Document.objects.count()
    
    namespaces = ['personal', 'system', 'agent_memory', 'public']
    
    for namespace in namespaces:
        count = Document.objects.filter(metadata__namespace=namespace).count()
        percentage = (count / total * 100) if total > 0 else 0
        logger.info(f"{namespace:15} : {count:6} ({percentage:5.1f}%)")
    
    untagged = Document.objects.exclude(metadata__has_key='namespace').count()
    untagged_pct = (untagged / total * 100) if total > 0 else 0
    logger.info(f"{'Untagged':15} : {untagged:6} ({untagged_pct:5.1f}%)")
    logger.info(f"{'TOTAL':15} : {total:6}")
    
    if untagged == 0:
        logger.info("\n✅ ALL DOCUMENTS TAGGED!")
    else:
        logger.warning(f"\n⚠️  {untagged} documents still need tagging")
    
    return untagged == 0


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Batch tag documents with namespaces')
    parser.add_argument('--batch-size', type=int, default=100,
                       help='Number of documents per batch (default: 100)')
    parser.add_argument('--max-documents', type=int, default=None,
                       help='Maximum documents to process (default: all)')
    parser.add_argument('--verify-only', action='store_true',
                       help='Only verify current tagging status')
    
    args = parser.parse_args()
    
    if args.verify_only:
        verify_tagging()
    else:
        logger.info("STARTING BATCH DOCUMENT TAGGING")
        logger.info("=" * 60)
        stats = batch_tag_documents(
            batch_size=args.batch_size,
            max_documents=args.max_documents
        )
        
        # Verify after tagging
        verify_tagging()