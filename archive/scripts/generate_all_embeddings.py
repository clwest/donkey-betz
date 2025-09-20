#!/usr/bin/env python
"""
Generate embeddings for all records that don't have them yet.
Processes in batches to avoid rate limits and memory issues.
"""

import os
import sys
import django
import time
import logging
from datetime import datetime

sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection, transaction
from core.encryption_service import get_encryption_service
import openai

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
BATCH_SIZE = 100  # Process 100 records at a time
RATE_LIMIT_DELAY = 1  # Seconds between batches
MODEL = "text-embedding-3-small"
MAX_RETRIES = 3

def get_openai_client():
    """Initialize OpenAI client"""
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment")
    return openai.OpenAI(api_key=api_key)

def create_embedding_with_retry(client, text, retries=MAX_RETRIES):
    """Create embedding with retry logic"""
    for attempt in range(retries):
        try:
            response = client.embeddings.create(
                input=text[:8000],  # Limit text length to avoid token limits
                model=MODEL
            )
            return response.data[0].embedding
        except Exception as e:
            if attempt < retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                logger.error(f"Failed to create embedding after {retries} attempts: {e}")
                return None

def process_batch(records, client, encryption_service):
    """Process a batch of records"""
    success_count = 0
    failed_ids = []
    
    with connection.cursor() as cursor:
        for record_id, content_text, content_type in records:
            try:
                # Decrypt content if needed
                if content_text:
                    decrypted_text = encryption_service.decrypt(content_text)
                    
                    if decrypted_text and len(decrypted_text.strip()) > 0:
                        # Create embedding
                        embedding = create_embedding_with_retry(client, decrypted_text)
                        
                        if embedding:
                            # Update record with embedding
                            cursor.execute("""
                                UPDATE unified_embeddings
                                SET embedding = %s,
                                    embedding_model = %s
                                WHERE id = %s
                            """, (embedding, MODEL, record_id))
                            success_count += 1
                        else:
                            failed_ids.append(record_id)
                    else:
                        logger.debug(f"Skipping record {record_id} - empty content after decryption")
                        failed_ids.append(record_id)
                else:
                    logger.debug(f"Skipping record {record_id} - no content")
                    failed_ids.append(record_id)
                    
            except Exception as e:
                logger.error(f"Error processing record {record_id}: {e}")
                failed_ids.append(record_id)
    
    return success_count, failed_ids

def generate_all_embeddings():
    """Main function to generate all missing embeddings"""
    
    print("=" * 60)
    print("GENERATING EMBEDDINGS FOR ALL RECORDS")
    print("=" * 60)
    
    # Initialize services
    client = get_openai_client()
    encryption_service = get_encryption_service()
    
    # Get total count of records needing embeddings
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*)
            FROM unified_embeddings
            WHERE embedding IS NULL
            AND content_text IS NOT NULL
            AND content_text != ''
        """)
        total_records = cursor.fetchone()[0]
    
    print(f"\nTotal records needing embeddings: {total_records}")
    
    if total_records == 0:
        print("No records need embeddings!")
        return
    
    # Process in batches
    processed = 0
    total_success = 0
    total_failed = []
    start_time = datetime.now()
    
    print(f"\nProcessing in batches of {BATCH_SIZE}...")
    print("-" * 40)
    
    while processed < total_records:
        with connection.cursor() as cursor:
            # Get next batch
            cursor.execute("""
                SELECT id, content_text, content_type
                FROM unified_embeddings
                WHERE embedding IS NULL
                AND content_text IS NOT NULL
                AND content_text != ''
                LIMIT %s
            """, (BATCH_SIZE,))
            
            batch = cursor.fetchall()
            
            if not batch:
                break
            
            batch_start = datetime.now()
            success, failed = process_batch(batch, client, encryption_service)
            batch_time = (datetime.now() - batch_start).total_seconds()
            
            # Update counters
            processed += len(batch)
            total_success += success
            total_failed.extend(failed)
            
            # Commit transaction
            connection.commit()
            
            # Progress update
            progress = (processed / total_records) * 100
            eta_seconds = ((datetime.now() - start_time).total_seconds() / processed) * (total_records - processed)
            eta_minutes = int(eta_seconds / 60)
            
            print(f"Batch {processed // BATCH_SIZE}: Processed {len(batch)} records in {batch_time:.1f}s")
            print(f"  Success: {success}/{len(batch)} | Total: {total_success}/{processed} ({progress:.1f}%)")
            print(f"  ETA: ~{eta_minutes} minutes remaining")
            
            # Rate limiting
            if processed < total_records:
                time.sleep(RATE_LIMIT_DELAY)
    
    # Final summary
    elapsed = (datetime.now() - start_time).total_seconds()
    print("\n" + "=" * 60)
    print("EMBEDDING GENERATION COMPLETE")
    print("=" * 60)
    print(f"\nResults:")
    print(f"  Total processed: {processed}")
    print(f"  Successful: {total_success}")
    print(f"  Failed: {len(total_failed)}")
    print(f"  Time elapsed: {elapsed/60:.1f} minutes")
    print(f"  Average: {elapsed/max(processed, 1):.2f} seconds/record")
    
    # Verify final counts
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(embedding) as has_embedding,
                COUNT(*) - COUNT(embedding) as missing_embedding
            FROM unified_embeddings
        """)
        final_stats = cursor.fetchone()
        
        print(f"\nFinal Database Statistics:")
        print(f"  Total records: {final_stats[0]}")
        print(f"  With embeddings: {final_stats[1]}")
        print(f"  Missing embeddings: {final_stats[2]}")
    
    if total_failed:
        print(f"\n⚠️  {len(total_failed)} records failed. IDs: {total_failed[:10]}...")
        print("   (These may have empty or invalid content)")

def main():
    """Entry point with error handling"""
    try:
        # Ask for confirmation
        print("\n⚠️  This will generate embeddings for ~46,695 records")
        print("   Estimated time: 30-60 minutes")
        print("   Estimated API calls: ~47,000")
        print("   Estimated cost: ~$0.50-$1.00")
        
        response = input("\nProceed? (yes/no): ")
        if response.lower() != 'yes':
            print("Cancelled.")
            return
        
        generate_all_embeddings()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
        print("Progress has been saved. Run again to continue.")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()