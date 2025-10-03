# Memory Palace API Architecture

## Overview
The Memory Palace system has a complex multi-layered API architecture with several overlapping systems providing memory, knowledge, and document management functionality. This document maps all endpoints and their relationships.

## Frontend Components → API Endpoints

### Memory Palace Dashboard (MemoryPalace.tsx)
- **Component**: MemoryPalace.tsx
- **API Calls**:
  - GET `/api/memory/stats/` → Returns total counts and categories
  - Uses `memoryService.getStats()` which tries multiple endpoints:
    1. `/api/memory/stats/` (primary)
    2. `/api/memory/unified/stats/` (fallback)
    3. `/api/memory/palace/stats/` (legacy fallback)

### Semantic Search (SemanticSearch.tsx)
- **Component**: SemanticSearch.tsx  
- **API Calls**:
  - Primary: `ukfService.search()` → POST `/api/ukf/search/`
  - Fallback: `memoryService.semanticSearch()` → POST `/api/memory/unified/search/`
  - Legacy: POST `/api/memory/palace/semantic_search/`

### Knowledge Graph (KnowledgeGraph.tsx)
- **Component**: KnowledgeGraph.tsx
- **API Calls**:
  - `memoryService.getMemoryGraph()` → GET `/api/memory/palace/knowledge_graph/`

### Document Manager (DocumentManager.tsx)
- **Component**: DocumentManager.tsx
- **API Calls**:
  - GET `/api/memory/documents/`
  - GET `/api/memory/documents/stats/`
  - GET `/api/memory/documents/recent/`
  - GET `/api/memory/documents/{id}/`

### Stats Breakdown Modal (StatsBreakdownModal.tsx)
- **Component**: StatsBreakdownModal.tsx
- **API Calls**:
  - GET `/api/memory/palace/stats_breakdown/?type={type}`
  - Calls different endpoints based on stat type:
    - `total_memories` → `/api/memory/entries/`
    - `documents` → `/api/memory/documents/`
    - `knowledge_nodes` → filters high-importance memories
    - `ai_insights` → filters by insight type

## Backend API Structure

### Primary Memory Endpoints (backend/memory/urls.py)

#### Dashboard APIs (Public Access)
```
/api/memory/stats/                    # Total counts, categories
/api/memory/recent/                   # Recent memories (last 5)
/api/memory/search-performance/       # Search metrics
/api/memory/palace/stats_breakdown/   # Detailed breakdown by type
```

#### Memory Entry CRUD (ViewSet)
```
/api/memory/entries/                  # List/Create memories
/api/memory/entries/{id}/             # Get/Update/Delete specific memory
/api/memory/entries/recent/           # Last 7 days
/api/memory/entries/unreflected/      # Memories without reflections
/api/memory/entries/{id}/reflect/     # Create reflection
/api/memory/entries/stats/            # User-specific stats
```

#### Memory Palace ViewSet
```
/api/memory/palace/semantic_search/   # Legacy semantic search
/api/memory/palace/stats/             # Legacy stats endpoint
/api/memory/palace/timeline/          # Memory timeline view
/api/memory/palace/knowledge_graph/   # Graph visualization data
/api/memory/palace/embedding_status/  # Embedding generation status
/api/memory/palace/generate_embeddings/ # Trigger embedding generation
```

#### Unified Search System
```
/api/memory/unified/search/           # Unified search across all sources
/api/memory/unified/stats/            # Unified statistics
/api/memory/unified/{id}/             # Get specific unified memory
```

#### Document System
```
/api/memory/documents/                # List documents
/api/memory/documents/stats/          # Document statistics
/api/memory/documents/recent/         # Recent documents
/api/memory/documents/{id}/           # Specific document
```

### Knowledge Base System (backend/knowledge_base/urls.py)
```
/api/knowledge-base/                  # List/Create knowledge entries
/api/knowledge-base/{id}/             # Get/Update/Delete entry
/api/knowledge-base/categories/       # Get all categories
/api/knowledge-base/recent/           # Recently accessed
/api/knowledge-base/{id}/mark_accessed/ # Track access
/api/knowledge-base/{id}/toggle_pin/  # Pin/unpin entry
/api/knowledge-base/{id}/archive/     # Archive entry
/api/knowledge-base/search/           # Search knowledge base
```

### UKF System (backend/ukf_system/urls.py)
```
/api/ukf/knowledge/                   # UKF knowledge search
/api/ukf/knowledge/search/            # Semantic search
/api/ukf/knowledge/suggestions/       # Search suggestions
```

## Data Models & Relationships

### Core Memory Models

#### MemoryEntry (memory.models)
- Core memory storage for reflections and memories
- Fields: event, emotion, importance, type, tags
- Relations: user, parent_memory, anchor, chains
- Embeddings stored in JSON field

#### ConversationMemory (ai_partner.models)
- Stores AI conversation history
- Fields: message_content, topics_discussed, insights_shared
- Separate from MemoryEntry but searchable together

#### KnowledgeDocument (ukf_system.models)
- Document storage for imported knowledge
- Fields: title, content, summary, document_hash
- Has chunks for embedding and retrieval

#### KnowledgeEntry (knowledge_base.models)
- User-created knowledge base entries
- Fields: title, content, category, tags
- Supports pinning, archiving, access tracking

### Data Flow Examples

#### Creating a Memory
1. User action in UI
2. POST `/api/memory/entries/` or `/api/memory/palace/create/`
3. Creates MemoryEntry with user association
4. Triggers async embedding generation if enabled
5. Updates knowledge graph connections
6. Returns created memory to UI

#### Searching Memories
1. Search query in UI (SemanticSearch component)
2. Primary: POST `/api/ukf/search/` (UKF universal search)
3. Falls back to: POST `/api/memory/unified/search/`
4. Aggregates results from:
   - MemoryEntry (reflections)
   - ConversationMemory (AI chats)
   - KnowledgeDocument (imported docs)
   - KnowledgeEntry (user knowledge base)
5. Returns unified, relevance-scored results

#### Stats Aggregation
1. MemoryPalace dashboard loads
2. GET `/api/memory/stats/`
3. Aggregates counts from:
   - Total active MemoryEntry records
   - Knowledge nodes (high-importance memories)
   - Recent documents (last 7 days)
   - Unique categories from all memories
4. Caches results for 5 minutes

## API Redundancy & Overlap

### Multiple Search Endpoints
- `/api/memory/palace/semantic_search/` (legacy)
- `/api/memory/unified/search/` (current)
- `/api/ukf/knowledge/search/` (UKF system)
- `/api/knowledge-base/search/` (knowledge base)

### Multiple Stats Endpoints
- `/api/memory/stats/` (public dashboard)
- `/api/memory/entries/stats/` (user-specific)
- `/api/memory/palace/stats/` (legacy)
- `/api/memory/unified/stats/` (unified system)

### Overlapping Data Sources
- MemoryEntry: User reflections and memories
- ConversationMemory: AI conversation history
- KnowledgeDocument: Imported documents (UKF)
- KnowledgeEntry: User knowledge base
- MarkdownDocument: Legacy markdown imports

## Recommendations

### 1. Consolidate Search Endpoints
Create a single search endpoint that intelligently routes to appropriate backends:
```python
/api/memory/search/v2/
- Accepts: query, filters, sources[]
- Returns: unified results with source attribution
- Handles: memories, conversations, documents, knowledge
```

### 2. Unified Stats Endpoint
Merge all stats endpoints into one comprehensive endpoint:
```python
/api/memory/stats/v2/
- Returns all dashboard metrics
- Includes breakdown by source
- Single cache layer
```

### 3. Simplify Data Models
Consider merging similar models:
- Merge KnowledgeDocument and MarkdownDocument
- Create unified "Memory" model with type field
- Use single embedding table for all content types

### 4. Clear API Naming Convention
```
/api/memory/v2/
  /search         # Universal search
  /stats          # All statistics
  /entries        # CRUD operations
  /graph          # Knowledge graph
  /documents      # Document management
  /embeddings     # Embedding operations
```

### 5. Single Entry Point Pattern
Create an aggregation endpoint for initial dashboard load:
```python
GET /api/memory/v2/dashboard/
Returns: {
  stats: { ... },
  recent_memories: [ ... ],
  categories: [ ... ],
  search_performance: { ... }
}
```

## Performance Optimizations

### Current Optimizations
- 5-minute caching on stats endpoints
- Batch loading with prefetch_related
- Pagination on list endpoints
- Async embedding generation

### Recommended Optimizations
1. GraphQL endpoint for flexible data fetching
2. Redis caching layer for frequently accessed data
3. Elasticsearch for semantic search operations
4. Database views for complex aggregations
5. WebSocket subscriptions for real-time updates

## Security Considerations

### Current State
- Most endpoints require authentication (IsAuthenticated)
- Dashboard stats endpoints are public (AllowAny)
- User data properly filtered by request.user

### Recommendations
1. Add rate limiting to public endpoints
2. Implement field-level permissions
3. Add audit logging for sensitive operations
4. Consider read-only API keys for dashboard