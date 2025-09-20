#!/usr/bin/env python
"""
Start Background Document Isolation
Launches the background isolation process to gradually tag remaining documents
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from batch_tag_documents import DocumentClassifier, verify_tagging
import logging
import threading
import time
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BackgroundIsolator:
    """Background document isolation that runs in a separate thread"""
    
    def __init__(self, batch_size=25, delay_seconds=2):
        self.batch_size = batch_size
        self.delay_seconds = delay_seconds
        self.running = False
        self.thread = None
        self.stats = {
            'personal': 0,
            'system': 0,
            'agent_memory': 0,
            'public': 0,
            'errors': 0,
            'total_processed': 0
        }
    
    def start(self):
        """Start the background isolation process"""
        if self.running:
            logger.warning("Background isolation is already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_isolation, daemon=True)
        self.thread.start()
        logger.info("🚀 Background document isolation started")
    
    def stop(self):
        """Stop the background isolation process"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=30)
        logger.info("⏹️  Background document isolation stopped")
    
    def get_status(self):
        """Get current status"""
        return {
            'running': self.running,
            'stats': self.stats.copy(),
            'timestamp': datetime.now().isoformat()
        }
    
    def _run_isolation(self):
        """Main isolation loop that runs in background"""
        from content.models import Document, DocumentEmbedding
        from django.db import transaction
        from django.db.models import Q
        
        classifier = DocumentClassifier()
        logger.info(f"Starting background isolation with batch_size={self.batch_size}, delay={self.delay_seconds}s")
        
        while self.running:
            try:
                # Get next batch of untagged documents
                untagged_query = Document.objects.exclude(
                    metadata__has_key='namespace'
                )
                
                batch = list(untagged_query[:self.batch_size])
                
                if not batch:
                    logger.info("✅ No more documents to process - isolation complete!")
                    self.running = False
                    break
                
                # Process batch
                batch_start = time.time()
                
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
                                'tagged_by': 'background_isolator',
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
                            
                            self.stats[namespace] += 1
                            self.stats['total_processed'] += 1
                            
                        except Exception as e:
                            logger.error(f"Error processing document {doc.id}: {e}")
                            self.stats['errors'] += 1
                            self.stats['total_processed'] += 1
                
                batch_time = time.time() - batch_start
                remaining = untagged_query.count() - len(batch)
                
                # Log progress every few batches
                if self.stats['total_processed'] % (self.batch_size * 5) == 0:
                    logger.info(f"📊 Progress: {self.stats['total_processed']} processed, ~{remaining} remaining")
                    logger.info(f"   Distribution: {dict((k,v) for k,v in self.stats.items() if k != 'total_processed')}")
                    logger.info(f"   Rate: {len(batch)/batch_time:.1f} docs/sec")
                
                # Sleep to avoid overwhelming the database
                if self.running:
                    time.sleep(self.delay_seconds)
                
            except Exception as e:
                logger.error(f"Background isolation error: {e}")
                time.sleep(10)  # Wait longer on error
        
        logger.info("🏁 Background isolation thread finished")

def main():
    """Main function to control background isolation"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Background document isolation')
    parser.add_argument('--batch-size', type=int, default=25,
                       help='Documents per batch (default: 25)')
    parser.add_argument('--delay', type=int, default=2,
                       help='Delay between batches in seconds (default: 2)')
    parser.add_argument('--status-only', action='store_true',
                       help='Just check current status')
    parser.add_argument('--verify-only', action='store_true',
                       help='Just verify current tagging')
    
    args = parser.parse_args()
    
    if args.verify_only:
        logger.info("🔍 Checking current isolation status...")
        verify_tagging()
        return
    
    if args.status_only:
        logger.info("📊 Current isolation status:")
        verify_tagging()
        return
    
    # Start background isolation
    isolator = BackgroundIsolator(
        batch_size=args.batch_size,
        delay_seconds=args.delay
    )
    
    try:
        # Check current status first
        logger.info("🔍 Checking current status before starting...")
        verify_tagging()
        
        # Start isolation
        isolator.start()
        
        # Keep main thread alive and show periodic updates
        while isolator.running:
            time.sleep(30)  # Update every 30 seconds
            status = isolator.get_status()
            if status['stats']['total_processed'] > 0:
                logger.info(f"🔄 Background isolation running - processed {status['stats']['total_processed']}")
        
        # Final status
        logger.info("🎉 Background isolation completed!")
        final_status = isolator.get_status()
        logger.info(f"Final stats: {final_status['stats']}")
        
        # Verify final result
        logger.info("🔍 Final verification:")
        verify_tagging()
        
    except KeyboardInterrupt:
        logger.info("⚠️  Received interrupt signal - stopping gracefully...")
        isolator.stop()
        logger.info("✅ Stopped successfully")
    except Exception as e:
        logger.error(f"❌ Background isolation failed: {e}")
        isolator.stop()

if __name__ == '__main__':
    main()