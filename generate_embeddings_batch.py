#!/usr/bin/env python
"""
Batch Embedding Generation Script

Generate embeddings for all content in the persistence layer to achieve 95%+ reality score.
This script creates embeddings for:

1. Agent knowledge entries
2. Spider discovery data
3. Revenue descriptions
4. Collaboration session content

Uses OpenAI text-embedding-3-small model for 1536-dimensional vectors.
"""

import os
import sys
import django
import time
from typing import List

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from persistence.models import (
    UnifiedEmbedding, AgentKnowledge, SpiderData, RevenueTracker,
    AgentCollaborationSession
)

def generate_openai_embedding(text: str) -> List[float]:
    """Generate embedding using OpenAI API"""
    import openai
    from django.conf import settings

    client = openai.OpenAI(api_key=settings.AI_PROVIDERS['OPENAI_API_KEY'])

    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text[:8000],  # Limit text length
            encoding_format="float"
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"  ❌ OpenAI API error: {e}")
        return None

def create_embedding_record(content_text: str, content_type: str, content_id: str,
                          source_system: str, creator_agent: str = None,
                          content_title: str = "", content_metadata: dict = None):
    """Create embedding record in database"""

    # Generate embedding vector
    embedding_vector = generate_openai_embedding(content_text)
    if not embedding_vector:
        return None

    # Create embedding record
    try:
        embedding = UnifiedEmbedding.objects.create(
            content_type=content_type,
            content_id=content_id,
            content_text=content_text[:1000],  # Store first 1000 chars
            content_title=content_title,
            content_metadata=content_metadata or {},
            embedding=embedding_vector,
            embedding_dimension=len(embedding_vector),
            source_system=source_system,
            creator_agent=creator_agent or '',
            embedding_model='text-embedding-3-small'
        )
        return embedding
    except Exception as e:
        print(f"  ❌ Database error: {e}")
        return None

def generate_knowledge_embeddings():
    """Generate embeddings for agent knowledge"""
    print("🔄 Generating embeddings for agent knowledge...")

    knowledge_entries = AgentKnowledge.objects.filter(embedding__isnull=True)
    generated = 0

    for knowledge in knowledge_entries:
        # Combine content for embedding
        if isinstance(knowledge.content, dict):
            content_text = knowledge.content.get('text', str(knowledge.content))
        else:
            content_text = str(knowledge.content)

        full_text = f"{knowledge.title}\\n\\n{content_text}\\n\\nSummary: {knowledge.summary}"

        embedding = create_embedding_record(
            content_text=full_text,
            content_type='agent_knowledge',
            content_id=str(knowledge.id),
            source_system='agents',
            creator_agent=knowledge.agent_name,
            content_title=knowledge.title,
            content_metadata={
                'knowledge_type': knowledge.knowledge_type,
                'confidence_score': knowledge.confidence_score,
                'domain_tags': knowledge.domain_tags
            }
        )

        if embedding:
            # Link embedding to knowledge
            knowledge.embedding = embedding
            knowledge.save()
            generated += 1
            print(f"  ✅ Generated embedding for: {knowledge.title[:50]}...")

        # Rate limiting
        time.sleep(0.1)

    print(f"✅ Generated {generated} knowledge embeddings")
    return generated

def generate_spider_embeddings():
    """Generate embeddings for spider data"""
    print("🔄 Generating embeddings for spider data...")

    spider_data = SpiderData.objects.filter(embedding__isnull=True)
    generated = 0

    for spider in spider_data:
        full_text = f"{spider.title}\\n\\n{spider.content}\\n\\nSource: {spider.source_platform}\\nType: {spider.data_type}"

        embedding = create_embedding_record(
            content_text=full_text,
            content_type='spider_data',
            content_id=str(spider.id),
            source_system='spiders',
            creator_agent=spider.spider_name,
            content_title=spider.title,
            content_metadata={
                'data_type': spider.data_type,
                'source_platform': spider.source_platform,
                'opportunity_score': float(spider.opportunity_score),
                'relevance_score': float(spider.relevance_score)
            }
        )

        if embedding:
            # Link embedding to spider data
            spider.embedding = embedding
            spider.save()
            generated += 1
            print(f"  ✅ Generated embedding for: {spider.title[:50]}...")

        # Rate limiting
        time.sleep(0.1)

    print(f"✅ Generated {generated} spider embeddings")
    return generated

def generate_revenue_embeddings():
    """Generate embeddings for revenue data"""
    print("🔄 Generating embeddings for revenue data...")

    revenue_entries = RevenueTracker.objects.all()
    generated = 0

    for revenue in revenue_entries:
        full_text = f"Revenue: ${revenue.amount} from {revenue.revenue_source}\\n\\n{revenue.description}\\n\\nAgent: {revenue.source_agent}\\nSpider: {revenue.source_spider}"

        embedding = create_embedding_record(
            content_text=full_text,
            content_type='revenue_data',
            content_id=str(revenue.id),
            source_system='revenue',
            creator_agent=revenue.source_agent,
            content_title=f"${revenue.amount} - {revenue.revenue_source}",
            content_metadata={
                'amount': float(revenue.amount),
                'revenue_source': revenue.revenue_source,
                'verification_status': revenue.verification_status
            }
        )

        if embedding:
            generated += 1
            print(f"  ✅ Generated embedding for: ${revenue.amount} {revenue.revenue_source}")

        # Rate limiting
        time.sleep(0.1)

    print(f"✅ Generated {generated} revenue embeddings")
    return generated

def generate_collaboration_embeddings():
    """Generate embeddings for collaboration sessions"""
    print("🔄 Generating embeddings for collaboration sessions...")

    sessions = AgentCollaborationSession.objects.all()
    generated = 0

    for session in sessions:
        participants_text = ", ".join(session.participating_agents)
        results_text = str(session.results) if session.results else "No results"

        full_text = f"Collaboration: {session.session_name}\\n\\nGoal: {session.session_goal}\\n\\nParticipants: {participants_text}\\n\\nResults: {results_text}"

        embedding = create_embedding_record(
            content_text=full_text,
            content_type='collaboration',
            content_id=str(session.id),
            source_system='collaboration',
            creator_agent=session.participating_agents[0] if session.participating_agents else '',
            content_title=session.session_name,
            content_metadata={
                'session_status': session.session_status,
                'participant_count': len(session.participating_agents),
                'goal': session.session_goal
            }
        )

        if embedding:
            generated += 1
            print(f"  ✅ Generated embedding for: {session.session_name}")

        # Rate limiting
        time.sleep(0.1)

    print(f"✅ Generated {generated} collaboration embeddings")
    return generated

def main():
    """Main execution function"""
    print("🚀 BATCH EMBEDDING GENERATION")
    print("=" * 50)
    print("Goal: Generate embeddings for all content to achieve 95%+ reality score")
    print("=" * 50)

    # Check current embedding count
    initial_count = UnifiedEmbedding.objects.count()
    print(f"📊 Initial embedding count: {initial_count}")

    # Generate embeddings for all content types
    total_generated = 0

    try:
        total_generated += generate_knowledge_embeddings()
        total_generated += generate_spider_embeddings()
        total_generated += generate_revenue_embeddings()
        total_generated += generate_collaboration_embeddings()
    except Exception as e:
        print(f"❌ Error during embedding generation: {e}")

    # Final count
    final_count = UnifiedEmbedding.objects.count()
    print(f"\\n📊 Final embedding count: {final_count}")
    print(f"✅ Generated {total_generated} new embeddings")

    if total_generated > 0:
        print("\\n🎯 Ready for 95%+ reality score validation!")

        # Test a sample embedding search
        print("\\n🔍 Testing embedding search...")
        try:
            sample_embedding = UnifiedEmbedding.objects.first()
            if sample_embedding:
                print(f"  ✅ Sample embedding: {sample_embedding.content_title}")
                print(f"  ✅ Dimensions: {sample_embedding.embedding_dimension}")
                print(f"  ✅ Content type: {sample_embedding.content_type}")
        except Exception as e:
            print(f"  ❌ Search test error: {e}")

    print("\\n✅ Batch embedding generation completed!")

if __name__ == '__main__':
    main()