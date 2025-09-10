#!/usr/bin/env python
"""
Populate test embeddings with sports and platform content
"""

import os
import sys
import django

sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
import openai
import json

def create_test_embeddings():
    """Create test embeddings for RAG demonstration"""
    
    print("Creating test embeddings for RAG...")
    
    # Test content about platform features
    test_content = [
        {
            "content_type": "knowledge_base",
            "content_text": "The Unified Donkey Betz platform provides comprehensive sports betting analytics including Kelly Criterion calculations for optimal bet sizing, expected value (EV) analysis, arbitrage opportunity detection, and real-time odds tracking across multiple sportsbooks.",
            "metadata": {"category": "sports_betting", "topic": "features"}
        },
        {
            "content_type": "knowledge_base", 
            "content_text": "Kelly Criterion formula: f* = (bp - q) / b, where f* is the fraction of bankroll to wager, b is the odds received on the wager, p is the probability of winning, and q is the probability of losing (1-p). The platform automatically calculates fractional Kelly (usually 25% of full Kelly) for safer bankroll management.",
            "metadata": {"category": "sports_betting", "topic": "kelly_criterion"}
        },
        {
            "content_type": "knowledge_base",
            "content_text": "The platform supports 87+ specialized AI agents for various tasks including odds scraping, line movement tracking, injury report analysis, weather impact assessment, and automated betting strategy execution. Agents can be orchestrated together for complex workflows.",
            "metadata": {"category": "agent_orchestration", "topic": "capabilities"}
        },
        {
            "content_type": "knowledge_base",
            "content_text": "RAG (Retrieval-Augmented Generation) system uses 73,000+ embeddings from unified knowledge base including sports analytics, betting strategies, agent documentation, and platform features. Vector similarity search with pgvector enables context-aware AI responses.",
            "metadata": {"category": "rag_system", "topic": "overview"}
        },
        {
            "content_type": "documentation",
            "content_text": "Security features include: Multi-factor authentication (MFA), Role-based access control (RBAC), API key management with rotation, AES-256 encryption for sensitive data, audit logging, GDPR compliance tools, secure WebSocket connections with JWT tokens, and automated security scanning.",
            "metadata": {"category": "security", "topic": "features"}
        }
    ]
    
    # Get OpenAI API key
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        print("❌ No OpenAI API key found")
        return
    
    client = openai.OpenAI(api_key=api_key)
    
    with connection.cursor() as cursor:
        for item in test_content:
            try:
                # Create embedding
                response = client.embeddings.create(
                    input=item["content_text"],
                    model="text-embedding-3-small"
                )
                embedding = response.data[0].embedding
                
                # Insert into database
                cursor.execute("""
                    INSERT INTO unified_embeddings 
                    (source_database, source_table, source_id, content_type, 
                     content_text, embedding, metadata, importance_score)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (source_database, source_table, source_id) 
                    DO UPDATE SET 
                        content_text = EXCLUDED.content_text,
                        embedding = EXCLUDED.embedding,
                        metadata = EXCLUDED.metadata
                """, (
                    'test_data',
                    'knowledge_base',
                    f"test_{item['metadata']['category']}_{item['metadata']['topic']}",
                    item['content_type'],
                    item['content_text'],
                    embedding,
                    json.dumps(item['metadata']),
                    0.9  # High importance for test data
                ))
                
                print(f"✅ Created embedding for {item['metadata']['category']}/{item['metadata']['topic']}")
                
            except Exception as e:
                print(f"❌ Failed to create embedding: {e}")
        
        # Commit changes
        connection.commit()
        
        # Verify
        cursor.execute("""
            SELECT COUNT(*) FROM unified_embeddings 
            WHERE source_database = 'test_data'
        """)
        count = cursor.fetchone()[0]
        print(f"\n✅ Total test embeddings created: {count}")

if __name__ == "__main__":
    create_test_embeddings()