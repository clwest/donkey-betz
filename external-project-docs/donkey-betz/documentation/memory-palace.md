# Memory Palace

## Overview
The Memory Palace is Donkey Betz's unified memory management system that integrates multiple memory sources, implements advanced embedding strategies, and provides semantic search capabilities across user conversations, reflections, documents, and imported knowledge.

## Architecture

### Memory Storage Patterns
The system implements two distinct embedding storage patterns:

#### Pattern 1: Direct Embedding (MemoryEntry)
```python
# Embeddings stored as JSON in main model
embedding = models.JSONField(null=True, blank=True)
```
- Used for: Reflections, user entries, imported content
- Simpler architecture for atomic memory units
- One embedding per memory entry

#### Pattern 2: Separate Embedding Model (ConversationMemory)
```python
# Embeddings in related model with pgvector
embedding = VectorField(dimensions=1536)
conversation = models.ForeignKey(ConversationMemory)
```
- Used for: AI conversations, long-form content
- Supports chunking (multiple embeddings per conversation)
- Rich metadata per chunk (topics, entities, sentiment)
- Optimized vector operations with pgvector

### Memory Types
```
Memory Palace
├── Reflection Memories (MemoryEntry)
│   ├── User reflections
│   ├── Walking companion notes
│   └── Business/technical insights
├── Conversation Memories (ConversationMemory)
│   ├── AI assistant conversations
│   ├── Multi-assistant tracking
│   └── Session organization
├── Document Memories (via Oracle)
│   ├── PDF embeddings
│   └── Document chunks
└── Knowledge Integration (UKF)
    ├── External knowledge
    └── Fallback search
```

## Current State
- **Total Memories**: Dynamic based on user activity
- **Embedding Coverage**: Tracked via embedding_status endpoint
- **Vector Dimensions**: 1536 (OpenAI standard)
- **Supported Formats**: Text, conversations, PDFs, markdown
- **Reality Engine**: Active fact vs fiction detection
- **Performance**: Sub-second semantic search

## Key Components

### Memory Models and Relationships

#### MemoryEntry
- **Core Fields**: event, embedding, source_type, confidence_score
- **Reality Engine**: fiction_indicators, verified status
- **Relationships**: User, MemoryChain, SymbolicAnchor

#### ConversationMemory + ConversationEmbedding
- **Conversation**: Full conversation with metadata
- **Embeddings**: Chunked, searchable segments
- **Metadata**: speaker, topics, entities, importance_score
- **Vector Storage**: pgvector VectorField

#### SymbolicAnchor
- **Purpose**: Persistent concepts across memories
- **Learning**: Links to learning intelligence
- **Relationships**: Many-to-many with memories

### Embedding Architecture

#### Generation Process
1. Content ingestion (text, conversation, document)
2. Chunking strategy (512 tokens, 50 overlap)
3. OpenAI embedding generation
4. Vector storage with metadata
5. Index optimization

#### Search Implementation
```python
# Hybrid search combining vector similarity and metadata
1. Vector similarity search (cosine distance)
2. Metadata filtering (date, type, source)
3. Reality Engine scoring
4. Result ranking and deduplication
```

### Reality Engine

#### Fact vs AI Content Distinction
- **source_type**: 'human_provided', 'ai_generated', 'system_import', 'verified_fact'
- **confidence_score**: 0.00 to 1.00 accuracy rating
- **fiction_indicators**: Count of detected fiction patterns
- **verified**: Boolean for fact-checked content

## API Endpoints

### Core Memory Operations
- `POST /api/memory/palace/semantic_search/` - Unified semantic search
- `GET /api/memory/palace/stats/` - Memory statistics
- `GET /api/memory/palace/knowledge_graph/` - Graph visualization data
- `GET /api/memory/palace/timeline/` - Chronological view
- `GET /api/memory/palace/insights/` - AI-generated patterns

### Embedding Management
- `GET /api/memory/palace/embedding_status/` - Coverage statistics
- `POST /api/memory/palace/generate_embeddings/` - Batch generation

### Advanced Features
- `POST /api/memory/palace/import_markdown/` - Markdown ingestion
- `GET /api/memory/palace/search_history/` - User search patterns
- `POST /api/memory/palace/verify_fact/` - Fact checking

## Database Models

### Core Schema
```sql
-- MemoryEntry with JSON embedding
CREATE TABLE memory_memoryentry (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES auth_user(id),
    event TEXT,
    embedding JSONB,
    source_type VARCHAR(50),
    confidence_score DECIMAL(3,2),
    fiction_indicators INTEGER,
    created_at TIMESTAMP
);

-- ConversationEmbedding with pgvector
CREATE TABLE ai_partner_conversationembedding (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES ai_partner_conversationmemory(id),
    embedding vector(1536),
    chunk_text TEXT,
    topics JSONB,
    entities JSONB,
    importance_score DECIMAL(3,2)
);

-- Indexes for performance
CREATE INDEX idx_memory_embedding ON memory_memoryentry USING GIN (embedding);
CREATE INDEX idx_conv_embedding_vector ON ai_partner_conversationembedding 
    USING ivfflat (embedding vector_cosine_ops);
```

## Integration Points

### Internal Systems
- **Agent Orchestra**: Provides context for agent tasks
- **Learning Intelligence**: Extracts patterns for improvement
- **Mythology Lab**: Validates memories for accuracy
- **Knowledge Base**: Entity extraction and linking
- **AI Partner**: Stores conversation history

### External Integrations
- **OpenAI**: Embedding generation (text-embedding-3-small)
- **PostgreSQL + pgvector**: Vector storage and search
- **Redis**: Caching layer for frequent searches
- **UKF Bridge**: Universal Knowledge Format integration

## Known Issues

### Embedding Status Inconsistency
```python
# Current issue with different counting methods
MemoryEntry: embedding__isnull=False
ConversationMemory: embeddings__isnull=False  # checks related model
```
This causes inconsistent reporting in embedding coverage statistics.

### Architecture Inconsistencies
- Two different embedding storage patterns (JSON vs pgvector)
- Lack of unified search interface across patterns
- Missing deduplication for imported memories
- Embedding generation not automated for new entries

### Performance Bottlenecks
- Large memory searches can be slow without caching
- Embedding generation is synchronous for small batches
- Knowledge graph generation doesn't scale well

## Future Enhancements

### Technical Improvements
- Migrate all embeddings to pgvector for consistency
- Implement Redis caching for search results
- Add automatic embedding generation on memory creation
- Enhance deduplication algorithms
- Optimize chunk size for better search relevance

### Feature Additions
- Multi-modal memories (images, audio)
- Memory version control and history
- Collaborative memory spaces
- Advanced Reality Engine with source verification
- Memory decay and reinforcement algorithms
- Cross-user memory networks (privacy-preserved)

## Code Examples

### Semantic Search
```python
# POST /api/memory/palace/semantic_search/
{
    "query": "business strategies for AI startups",
    "filters": {
        "source_type": ["human_provided", "verified_fact"],
        "date_range": "last_30_days",
        "min_confidence": 0.7
    },
    "limit": 10
}
```

### Embedding Generation
```python
# POST /api/memory/palace/generate_embeddings/
{
    "batch_size": 100,
    "memory_types": ["reflection", "conversation"],
    "force_regenerate": false
}
```

### Memory Statistics
```python
# GET /api/memory/palace/stats/
{
    "total_memories": {
        "reflections": 1543,
        "conversations": 892,
        "documents": 156
    },
    "embedding_coverage": {
        "reflections": "87.3%",
        "conversations": "94.2%"
    },
    "token_usage": {
        "total": 2847593,
        "estimated_cost": "$1.42"
    },
    "knowledge_nodes": 342,
    "ai_insights": 67
}
```