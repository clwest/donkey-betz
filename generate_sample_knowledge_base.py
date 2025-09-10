#!/usr/bin/env python3
"""
Generate sample documents and embeddings for testing the RAG-enhanced assistant.
This will create a diverse knowledge base covering various platform capabilities.
"""

import os
import sys
import django
import json
from datetime import datetime
import uuid

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.append('/Users/donkeyking/development/unified-donkey-betz')
django.setup()

from django.contrib.auth import get_user_model
from content.models import Document, DocumentEmbedding, KnowledgeBase
from self_awareness.models import CodeEmbedding
from django.utils import timezone

User = get_user_model()


def create_sample_documents():
    """Create sample documents covering various platform capabilities"""
    
    print("\n📚 Creating Sample Knowledge Base Documents")
    print("=" * 60)
    
    # Get or create a user
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        user = User.objects.first()
    if not user:
        print("❌ No user found. Please create a user first.")
        return
    
    print(f"Using user: {user.username if hasattr(user, 'username') else user.email}")
    
    # Get or create knowledge base
    kb, created = KnowledgeBase.objects.get_or_create(
        name="Platform Documentation",
        owner=user,
        defaults={
            'description': "Comprehensive documentation for the Unified Donkey Betz Platform",
            'metadata': {'version': '1.0', 'category': 'documentation'}
        }
    )
    
    # Sample documents covering different aspects of the platform
    documents_data = [
        {
            'title': 'AI Agent Orchestration System Overview',
            'description': 'Complete guide to the 87+ specialized agents',
            'content': """
The Unified Donkey Betz Platform features an advanced AI Agent Orchestration System with over 87 specialized agents designed for various tasks:

**Core Agent Categories:**
1. Content Generation Agents - Create blog posts, social media content, video scripts
2. Code Analysis Agents - Analyze, optimize, and document code
3. Research Agents - Web scraping, data analysis, literature review
4. Business Intelligence Agents - Market analysis, competitor research, trend detection
5. Workflow Automation Agents - Task scheduling, process optimization, integration

**Key Features:**
- Multi-agent collaboration for complex tasks
- Automatic agent selection based on task requirements
- Real-time monitoring and performance metrics
- Scalable architecture supporting concurrent executions
- Integration with multiple LLM providers (OpenAI, Anthropic, Google)

**Agent Discovery:**
The platform uses intelligent routing to automatically select the best agent(s) for any given task.
Agents can work independently or collaborate on complex multi-step workflows.
            """,
            'document_type': 'documentation',
            'category': 'agents'
        },
        {
            'title': 'RAG System Architecture and Capabilities',
            'description': 'How the Retrieval-Augmented Generation system works',
            'content': """
The RAG (Retrieval-Augmented Generation) system enhances AI responses with relevant context from the knowledge base:

**Architecture Components:**
1. Document Ingestion Pipeline
   - Supports multiple file formats (PDF, Word, Markdown, HTML)
   - Automatic text extraction and processing
   - Metadata extraction and indexing

2. Embedding Generation
   - Uses state-of-the-art embedding models (text-embedding-ada-002)
   - Chunking strategies for optimal retrieval
   - Semantic similarity matching

3. Vector Database
   - PostgreSQL with pgvector extension
   - Efficient similarity search using HNSW indexes
   - Scalable to millions of embeddings

4. Retrieval Pipeline
   - Hybrid search combining semantic and keyword matching
   - Relevance scoring and ranking
   - Context window optimization

**Use Cases:**
- Question answering from documentation
- Code search and explanation
- Knowledge base queries
- Context-aware content generation
            """,
            'document_type': 'technical',
            'category': 'rag'
        },
        {
            'title': 'Multi-LLM Provider Integration',
            'description': 'Working with OpenAI, Anthropic, and Google AI',
            'content': """
The platform seamlessly integrates with multiple Large Language Model providers:

**Supported Providers:**
1. OpenAI
   - GPT-5-mini, GPT-4-turbo
   - DALL-E 3 for image generation
   - Whisper for speech-to-text

2. Anthropic
   - Claude 3 (Opus, Sonnet, Haiku)
   - Advanced reasoning capabilities
   - Strong safety features

3. Google AI
   - Gemini Pro, Gemini Ultra
   - Multimodal capabilities
   - Integration with Google services

**Smart Model Selection:**
- Automatic provider failover
- Cost-optimized model selection
- Task-specific model routing
- Performance monitoring and analytics

**Configuration:**
API keys are managed securely through environment variables.
The system automatically selects the best available provider based on task requirements and availability.
            """,
            'document_type': 'documentation',
            'category': 'ai-providers'
        },
        {
            'title': 'Content Generation Workflows',
            'description': 'Automated content creation pipelines',
            'content': """
Advanced content generation capabilities powered by AI:

**Content Types:**
1. Blog Posts
   - SEO-optimized articles
   - Research-backed content
   - Automatic formatting and structure

2. Social Media
   - Platform-specific optimization
   - Hashtag generation
   - Engagement optimization

3. Video Scripts
   - Scene descriptions
   - Dialogue generation
   - Shot recommendations

4. Marketing Copy
   - Product descriptions
   - Email campaigns
   - Landing page content

**Workflow Features:**
- Template-based generation
- Brand voice consistency
- Multi-language support
- A/B testing variations
- Content scheduling and publishing

**Quality Control:**
- Automated fact-checking
- Plagiarism detection
- Readability scoring
- SEO optimization
            """,
            'document_type': 'documentation',
            'category': 'content'
        },
        {
            'title': 'Self-Awareness and Code Understanding',
            'description': 'How the platform understands its own codebase',
            'content': """
The Self-Awareness module enables the platform to understand and analyze its own code:

**Capabilities:**
1. Code Analysis
   - Function and class documentation
   - Dependency mapping
   - Complexity analysis
   - Security vulnerability detection

2. Code Generation
   - Automatic code completion
   - Bug fix suggestions
   - Refactoring recommendations
   - Test generation

3. Architecture Understanding
   - Module relationships
   - API endpoint mapping
   - Database schema comprehension
   - Service dependencies

**Implementation:**
- AST (Abstract Syntax Tree) parsing
- Code embeddings for semantic search
- Pattern recognition
- Continuous learning from code changes

**Benefits:**
- Self-documenting codebase
- Automated maintenance
- Intelligent debugging
- Code quality improvements
            """,
            'document_type': 'technical',
            'category': 'self-awareness'
        },
        {
            'title': 'Workflow Automation Engine',
            'description': 'Building and managing automated workflows',
            'content': """
Create powerful automated workflows with the platform's orchestration engine:

**Workflow Components:**
1. Triggers
   - Time-based (cron schedules)
   - Event-based (webhooks, file uploads)
   - API calls
   - Manual execution

2. Actions
   - Agent execution
   - API integrations
   - Data transformations
   - Conditional logic

3. Flow Control
   - Sequential execution
   - Parallel processing
   - Conditional branching
   - Error handling and retries

**Example Workflows:**
- Daily content generation and publishing
- Data processing pipelines
- Customer onboarding automation
- Report generation and distribution

**Monitoring:**
- Real-time execution tracking
- Performance metrics
- Error logs and debugging
- Success/failure notifications
            """,
            'document_type': 'documentation',
            'category': 'workflows'
        },
        {
            'title': 'Analytics and Metrics Dashboard',
            'description': 'Platform performance and usage analytics',
            'content': """
Comprehensive analytics for monitoring platform performance:

**Key Metrics:**
1. Usage Analytics
   - API call volumes
   - Agent execution statistics
   - User activity patterns
   - Resource utilization

2. Performance Metrics
   - Response times
   - Success rates
   - Error rates
   - Throughput metrics

3. Cost Analytics
   - LLM token usage
   - API costs breakdown
   - Budget tracking
   - Cost optimization recommendations

4. Quality Metrics
   - Content quality scores
   - User satisfaction ratings
   - Task completion rates
   - Accuracy measurements

**Visualization:**
- Real-time dashboards
- Historical trends
- Comparative analysis
- Custom reports

**Data Export:**
- CSV/Excel exports
- API access to metrics
- Scheduled reports
- Integration with BI tools
            """,
            'document_type': 'documentation',
            'category': 'analytics'
        },
        {
            'title': 'Security and Compliance Features',
            'description': 'Platform security measures and compliance',
            'content': """
Enterprise-grade security and compliance features:

**Security Measures:**
1. Authentication & Authorization
   - Multi-factor authentication
   - Role-based access control
   - API key management
   - Session management

2. Data Protection
   - Encryption at rest and in transit
   - Secure key storage
   - Data anonymization
   - Backup and recovery

3. Audit & Compliance
   - Activity logging
   - Compliance reporting
   - Data retention policies
   - GDPR compliance tools

**Best Practices:**
- Regular security updates
- Vulnerability scanning
- Penetration testing
- Security training

**Integrations:**
- SSO providers
- Identity management systems
- Security monitoring tools
- Compliance platforms
            """,
            'document_type': 'documentation',
            'category': 'security'
        }
    ]
    
    # Create documents
    created_docs = []
    for doc_data in documents_data:
        content = doc_data.pop('content')
        category = doc_data.pop('category')
        
        doc, created = Document.objects.update_or_create(
            title=doc_data['title'],
            owner=user,
            defaults={
                **doc_data,
                'raw_content': content,
                'processed_content': content,
                'status': 'processed',
                'source': 'manual',
                'tags': [category, 'documentation', 'platform'],
                'category': category,
                'collection': kb.name,
                'metadata': {
                    'generated': True,
                    'timestamp': datetime.now().isoformat(),
                    'version': '1.0'
                },
                'word_count': len(content.split()),
                'language': 'en',
                'is_public': True
            }
        )
        
        if created:
            created_docs.append(doc)
            print(f"✅ Created: {doc.title}")
        else:
            print(f"📝 Updated: {doc.title}")
    
    print(f"\n✨ Created/Updated {len(documents_data)} documents")
    
    # Documents are already associated via collection field
    print(f"📚 Documents associated with knowledge base: {kb.name}")
    
    return created_docs


def create_code_embeddings():
    """Create sample code embeddings for self-awareness"""
    
    print("\n💻 Creating Sample Code Embeddings")
    print("=" * 60)
    
    code_samples = [
        {
            'file_path': 'agents/models.py',
            'file_type': 'python',
            'class_name': 'UnifiedAgentTemplate',
            'function_name': 'execute',
            'code_snippet': """
def execute(self, input_data):
    '''Execute the agent with given input data'''
    try:
        # Validate input
        validated_data = self.validate_input(input_data)
        
        # Process with AI
        result = self.ai_processor.process(validated_data)
        
        # Return formatted output
        return self.format_output(result)
    except Exception as e:
        logger.error(f"Agent execution failed: {str(e)}")
        raise
            """,
            'complexity_score': 0.7,
            'importance_score': 0.9,
            'dependencies': ['logging', 'typing'],
            'imports': ['from typing import Dict, Any', 'import logging']
        },
        {
            'file_path': 'content/services.py',
            'file_type': 'python',
            'class_name': 'ContentGenerator',
            'function_name': 'generate_blog_post',
            'code_snippet': """
def generate_blog_post(self, topic, style='informative', length=1000):
    '''Generate a blog post on the given topic'''
    prompt = self.build_blog_prompt(topic, style, length)
    
    response = self.llm_provider.generate(
        prompt=prompt,
        max_tokens=length,
        temperature=0.7
    )
    
    return self.format_blog_post(response)
            """,
            'complexity_score': 0.5,
            'importance_score': 0.8,
            'dependencies': [],
            'imports': []
        }
    ]
    
    created_count = 0
    for sample in code_samples:
        emb, created = CodeEmbedding.objects.update_or_create(
            file_path=sample['file_path'],
            function_name=sample.get('function_name'),
            defaults=sample
        )
        if created:
            created_count += 1
            print(f"✅ Created code embedding: {sample['file_path']} - {sample.get('function_name', sample.get('class_name'))}")
    
    print(f"\n✨ Created {created_count} code embeddings")


def main():
    """Main execution"""
    print("\n🚀 GENERATING SAMPLE KNOWLEDGE BASE")
    print("=" * 60)
    
    # Create sample documents
    docs = create_sample_documents()
    
    # Create code embeddings
    create_code_embeddings()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 GENERATION COMPLETE")
    print("=" * 60)
    
    from content.models import Document, DocumentEmbedding
    from self_awareness.models import CodeEmbedding
    
    total_docs = Document.objects.count()
    total_doc_embeddings = DocumentEmbedding.objects.count()
    total_code_embeddings = CodeEmbedding.objects.count()
    
    print(f"""
✅ Knowledge Base Status:
   • Documents: {total_docs}
   • Document Embeddings: {total_doc_embeddings}
   • Code Embeddings: {total_code_embeddings}
   
🎯 Next Steps:
   1. Test the assistant at http://localhost:8000/api/assistant/chat/
   2. Try queries like:
      - "Tell me about the agent orchestration system"
      - "How does RAG work in this platform?"
      - "What AI providers are supported?"
      - "Explain the workflow automation features"
   
   3. The assistant will now search through the knowledge base to provide informed responses!
""")


if __name__ == "__main__":
    main()