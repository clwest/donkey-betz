# Knowledge Systems

## Overview
The Knowledge Systems in Donkey Betz form a comprehensive multi-layered architecture for storing, indexing, and retrieving information. The system integrates UKF (Universal Knowledge Format) with 2,200+ documents, entity recognition, document embeddings, and advanced search capabilities to provide accurate, contextual knowledge to agents and users.

## Architecture

### Knowledge System Layers
```
Knowledge Systems
├── Universal Knowledge Format (UKF)
│   ├── 2,200+ Documents
│   ├── SQLite Database (12MB)
│   ├── Full-Text Search
│   └── Vector Embeddings
├── Memory Palace Integration
│   ├── Document Memories
│   ├── Conversation Knowledge
│   ├── Reflection Knowledge
│   └── Hybrid Search
├── Entity Registry & Recognition
│   ├── Hardcoded Entities
│   ├── Context Rules
│   ├── Fact Verification
│   └── Relationship Mapping
├── Oracle System
│   ├── Codebase Oracle
│   ├── RAG-Powered Queries
│   ├── Code Embeddings
│   └── Intent Classification
└── Search & Retrieval
    ├── Universal Search Interface
    ├── Multi-Source Ranking
    ├── Redis Caching
    └── Performance Optimization
```

### Data Flow
1. **Document Ingestion** → Processing → Embedding → Storage
2. **User Query** → Intent Classification → Knowledge Retrieval → Context Building
3. **Agent Request** → Entity Verification → Knowledge Search → Response Enhancement

## Current State
- **Total Documents**: 2,200+ in UKF system
- **File Inventory**: 566 markdown files (5.6MB)
- **Database Size**: 12MB SQLite with full-text search
- **Embedding Dimensions**: 1536 (OpenAI standard)
- **Search Performance**: Sub-second with Redis caching
- **Entity Coverage**: Hardcoded entities with context rules

## Key Components

### UKF (2,200+ Documents)

#### Document Model Structure
```python
MarkdownDocument
    ├── file_path, title, content
    ├── category, tags[], participants[]
    ├── projects[], importance_score
    ├── quality_metrics (clarity, completeness)
    ├── metadata (JSON)
    └── word_count, last_modified

MarkdownEmbedding
    ├── document (FK)
    ├── embedding (vector[1536])
    ├── chunk_text, chunk_index
    └── embedding_model
```

#### Document Processing Pipeline
1. **Discovery**: File system scanning
2. **Analysis**: Content structure, entities, topics
3. **Chunking**: 512 tokens with 50 token overlap
4. **Embedding**: OpenAI text-embedding-3-small
5. **Storage**: SQLite + pgvector hybrid
6. **Indexing**: Full-text + vector indexes

### Embedding Coverage and Statistics

#### Coverage Tracking
- **Real-time Status**: `/api/memory/palace/embedding_status/`
- **Progress Monitoring**: Batch processing status
- **Quality Metrics**: Embedding validation
- **Performance Analytics**: Processing rates

#### Embedding Patterns
Two distinct storage patterns for different use cases:
1. **Direct Storage** (UKF): Vector embeddings in separate model
2. **Hybrid Storage** (Memory): JSON + pgvector combinations

### Search Capabilities

#### Universal Search Interface
```python
# Query classification and routing
Intent Types:
- implementation: "How does X work?"
- debugging: "Why is X failing?"
- architecture: "How is X structured?"
- search: "Find information about X"

Filtering Options:
- types[], participants[], dates
- categories[], tags[], projects[]
- importance (1-10), clarity scores
```

#### Multi-Source Ranking
1. **BM25 Full-Text**: Keyword relevance
2. **Vector Similarity**: Semantic matching
3. **Recency Boost**: Newer content priority
4. **Importance Score**: Quality-based ranking
5. **Usage Analytics**: Click-through boosting

### Integration with Agents

#### Knowledge Access Flow
```python
# Agent knowledge request
1. Query Intent Detection
2. Entity Registry Check
3. Multi-Source Search (UKF + Memory + Code)
4. Result Ranking and Filtering
5. Context Building
6. Mythology Validation
7. Response Enhancement
```

#### Universal Agent Capabilities
- **Memory Palace**: Personal and conversation knowledge
- **UKF Access**: Universal knowledge documents
- **Entity Verification**: Prevent hallucinations
- **Code Oracle**: Technical implementation knowledge
- **Search APIs**: External knowledge integration

## API Endpoints

### Knowledge Search
- `POST /api/memory/palace/semantic_search/` - Unified semantic search
- `GET /api/ukf/documents/` - UKF document management
- `GET /api/ukf/search/` - UKF-specific search
- `POST /api/codebase-oracle/query/` - Code knowledge queries

### Embedding Management
- `GET /api/memory/palace/embedding_status/` - Coverage statistics
- `POST /api/memory/palace/generate_embeddings/` - Batch generation
- `GET /api/ukf/embeddings/status/` - UKF embedding status

### Entity System
- `GET /api/knowledge-base/entities/` - Entity registry
- `POST /api/knowledge-base/verify-entity/` - Entity verification
- `GET /api/knowledge-base/relationships/` - Entity relationships

## Database Models

### UKF System Schema
```sql
-- Core document storage
CREATE TABLE markdown_documents (
    id INTEGER PRIMARY KEY,
    file_path TEXT UNIQUE,
    title TEXT,
    content TEXT,
    category TEXT,
    importance_score REAL,
    word_count INTEGER,
    last_modified TIMESTAMP
);

-- Vector embeddings
CREATE TABLE markdown_embeddings (
    id INTEGER PRIMARY KEY,
    document_id INTEGER REFERENCES markdown_documents(id),
    embedding vector(1536),
    chunk_text TEXT,
    chunk_index INTEGER
);

-- Full-text search index
CREATE VIRTUAL TABLE documents_fts USING fts5(
    title, content, category, tags
);
```

### Knowledge Integration Models
```python
DocumentIdea
    ├── document (FK → MarkdownDocument)
    ├── idea_text, context
    ├── relevance_score
    └── evolution_stage

DocumentSolution
    ├── document (FK → MarkdownDocument)
    ├── problem_statement
    ├── solution_approach
    ├── outcome, effectiveness_score
    └── implementation_notes

DocumentRelationship
    ├── source_document (FK)
    ├── target_document (FK)
    ├── relationship_type
    ├── strength_score
    └── context_description
```

## Integration Points

### Internal Systems
- **Memory Palace**: Unified search with UKF fallback
- **Agent Orchestra**: Knowledge context for all agents
- **Learning Intelligence**: Pattern extraction from knowledge
- **Mythology Lab**: Fact verification and hallucination prevention
- **Entity Registry**: Consistent entity interpretation

### External Integrations
- **OpenAI**: Embedding generation
- **PostgreSQL + pgvector**: Vector storage and search
- **SQLite**: UKF document storage with FTS
- **Redis**: Search result caching
- **File System**: Document ingestion and monitoring

## Known Issues
- UKF document count discrepancy (2,200+ claimed vs 566 found)
- Embedding coverage inconsistencies between systems
- Search result ranking could prioritize relevance better
- Entity registry is mostly hardcoded, needs dynamic expansion

## Future Enhancements
- Automated entity extraction from documents
- Real-time document indexing and updates
- Cross-system embedding synchronization
- Advanced query understanding with NLP
- Knowledge graph visualization
- Collaborative knowledge editing
- Multi-language document support

## Code Examples

### Universal Search Query
```python
# POST /api/memory/palace/semantic_search/
{
    "query": "How does authentication work in the system?",
    "filters": {
        "types": ["implementation", "documentation"],
        "categories": ["backend", "security"],
        "min_importance": 7
    },
    "limit": 10,
    "include_code": true
}
```

### Entity Verification
```python
# POST /api/knowledge-base/verify-entity/
{
    "entity": "Donkey Betz",
    "context": "fitness platform development",
    "confidence_threshold": 0.8
}
# Returns verified facts and prevents hallucinations
```

### Knowledge Statistics
```python
# GET /api/knowledge-base/stats/
{
    "total_documents": 2200,
    "embedding_coverage": "94.2%",
    "search_indexes": {
        "full_text": "active",
        "vector": "active",
        "entity": "active"
    },
    "cache_performance": {
        "hit_rate": "87.3%",
        "avg_response_time": "142ms"
    }
}
```