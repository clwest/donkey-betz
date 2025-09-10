#!/usr/bin/env python
"""
Test the migrated encryption service with encrypted embeddings
"""

import os
import sys
import django

sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from core.encryption_service import get_encryption_service
from core.rag_integration import search_embeddings, get_rag_context

def test_encryption_migration():
    """Test the encryption migration"""
    
    print("=" * 60)
    print("Testing Encryption Migration from donkey_betz")
    print("=" * 60)
    
    # Get encryption service
    service = get_encryption_service()
    
    print("\n1. Testing Encryption Service:")
    print(f"   Primary cipher available: {service.cipher is not None}")
    print(f"   Backup cipher available: {service.backup_cipher is not None}")
    
    # Test with sample encrypted content from database
    with connection.cursor() as cursor:
        # Get some encrypted embeddings
        cursor.execute("""
            SELECT content_text 
            FROM unified_embeddings 
            WHERE content_text LIKE 'gAAAAA%' 
            LIMIT 5
        """)
        encrypted_samples = cursor.fetchall()
        
        print(f"\n2. Found {len(encrypted_samples)} encrypted embeddings to test")
        
        successful_decryptions = 0
        for i, (encrypted_text,) in enumerate(encrypted_samples, 1):
            try:
                decrypted = service.decrypt(encrypted_text)
                if decrypted and decrypted != encrypted_text:
                    successful_decryptions += 1
                    print(f"   ✓ Sample {i}: Successfully decrypted ({len(decrypted)} chars)")
                    print(f"     Preview: {decrypted[:100]}...")
                else:
                    print(f"   ✗ Sample {i}: Failed to decrypt")
            except Exception as e:
                print(f"   ✗ Sample {i}: Error - {e}")
        
        print(f"\n   Successfully decrypted: {successful_decryptions}/{len(encrypted_samples)}")
        
        # Test RAG with encrypted content
        print("\n3. Testing RAG with Encrypted Content:")
        
        # Get count of searchable embeddings now
        cursor.execute("""
            SELECT COUNT(*) 
            FROM unified_embeddings 
            WHERE embedding IS NOT NULL
        """)
        total_with_embeddings = cursor.fetchone()[0]
        
        print(f"   Total embeddings available: {total_with_embeddings}")
        
        # Test search
        test_query = "sports betting analytics Kelly Criterion"
        print(f"\n4. Testing RAG search for: '{test_query}'")
        
        results = search_embeddings(test_query, limit=5, similarity_threshold=0.2)
        
        print(f"   Found {len(results)} results")
        
        encrypted_count = 0
        for i, doc in enumerate(results, 1):
            # Check if this was originally encrypted
            cursor.execute("""
                SELECT content_text LIKE 'gAAAAA%%' as is_encrypted
                FROM unified_embeddings 
                WHERE id = %s
            """, [doc['id']])
            
            is_encrypted = cursor.fetchone()
            if is_encrypted and is_encrypted[0]:
                encrypted_count += 1
                print(f"\n   Result {i} (was encrypted):")
            else:
                print(f"\n   Result {i}:")
            
            print(f"     Type: {doc['content_type']}")
            print(f"     Similarity: {doc['similarity_score']:.3f}")
            print(f"     Content: {doc['content'][:150]}...")
        
        if encrypted_count > 0:
            print(f"\n   ✅ Successfully decrypted and searched {encrypted_count} encrypted embeddings!")
        
        # Test full RAG context
        print("\n5. Testing Full RAG Context Generation:")
        context = get_rag_context(test_query)
        
        if context['has_context']:
            print(f"   ✅ RAG context generated")
            print(f"   - Documents used: {len(context['documents'])}")
            print(f"   - Context length: {len(context['context_text'])} chars")
            print(f"   - Preview: {context['context_text'][:200]}...")
        else:
            print("   ⚠️  No RAG context generated")

if __name__ == "__main__":
    test_encryption_migration()