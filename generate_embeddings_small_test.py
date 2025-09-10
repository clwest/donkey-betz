#!/usr/bin/env python
"""
Test embedding generation with a small batch before running the full script
"""

import os
import sys
import django

sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from core.encryption_service import get_encryption_service
import openai

def test_small_batch():
    """Test with just 5 records"""
    
    print("=" * 60)
    print("TESTING EMBEDDING GENERATION (5 records)")
    print("=" * 60)
    
    # Initialize services
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        print("❌ No OPENAI_API_KEY found")
        return
    
    client = openai.OpenAI(api_key=api_key)
    encryption_service = get_encryption_service()
    
    # Get 5 records without embeddings
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, content_text, content_type
            FROM unified_embeddings
            WHERE embedding IS NULL
            AND content_text IS NOT NULL
            AND content_text != ''
            LIMIT 5
        """)
        
        records = cursor.fetchall()
        
        if not records:
            print("No records found needing embeddings!")
            return
        
        print(f"\nProcessing {len(records)} test records...")
        
        success_count = 0
        for i, (record_id, content_text, content_type) in enumerate(records, 1):
            print(f"\n{i}. Processing record {record_id} (type: {content_type})")
            
            try:
                # Decrypt if needed
                decrypted = encryption_service.decrypt(content_text)
                
                if not decrypted or len(decrypted.strip()) == 0:
                    print(f"   ⚠️  Empty content after decryption")
                    continue
                
                print(f"   Content length: {len(decrypted)} chars")
                print(f"   Preview: {decrypted[:100]}...")
                
                # Create embedding
                response = client.embeddings.create(
                    input=decrypted[:8000],
                    model="text-embedding-3-small"
                )
                
                embedding = response.data[0].embedding
                print(f"   ✅ Embedding created ({len(embedding)} dimensions)")
                
                # Update database
                cursor.execute("""
                    UPDATE unified_embeddings
                    SET embedding = %s,
                        embedding_model = %s
                    WHERE id = %s
                """, (embedding, "text-embedding-3-small", record_id))
                
                connection.commit()
                success_count += 1
                print(f"   ✅ Saved to database")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print(f"\n" + "=" * 60)
        print(f"Test complete: {success_count}/{len(records)} successful")
        
        # Verify the updates
        cursor.execute("""
            SELECT COUNT(*) 
            FROM unified_embeddings 
            WHERE id IN %s AND embedding IS NOT NULL
        """, (tuple(r[0] for r in records),))
        
        verified = cursor.fetchone()[0]
        print(f"Verified in database: {verified} records have embeddings")

if __name__ == "__main__":
    test_small_batch()