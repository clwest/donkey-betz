# Section 3: Memory & Knowledge Systems
**Agent Name: Memory Architecture Reviewer**

## Scope Overview
This section covers the sophisticated memory and knowledge management systems that enable the platform to learn, remember, and retrieve information intelligently.

### Primary Directories:
- `backend/memory/` - Memory Palace implementation
- `backend/ukf_system/` - Universal Knowledge Framework
- `backend/knowledge_base/` - Knowledge storage and retrieval
- `backend/api/ukf_memory/` - Memory API layer

## Analysis Instructions for Claude Code Agent

### 1. Memory Palace Architecture
**Investigate:**
- `backend/memory/models/` - Memory, ConversationMemory, DocumentMemory
- `backend/memory/services/memory_service.py` - Core memory operations
- `backend/memory/services/conversation_memory_service.py` - Conversation storage

**Key Questions:**
- How are memories structured and stored?
- What types of memories exist?
- How is memory deduplication handled?
- What is the memory retention policy?

### 2. Universal Knowledge Framework (UKF)
**Investigate:**
- `backend/ukf_system/models/` - KnowledgeNode, KnowledgeRelation
- `backend/ukf_system/services/ukf_service.py` - UKF operations
- `backend/ukf_system/graph/` - Knowledge graph implementation

**Key Questions:**
- How is knowledge represented in the graph?
- What relationships exist between nodes?
- How is the knowledge graph queried?
- What is the graph update strategy?

### 3. Embedding Generation & Vector Search
**Investigate:**
- `backend/memory/services/embedding_service.py` - Embedding generation
- `backend/memory/services/vector_search_service.py` - Similarity search
- `backend/memory/utils/chunking_strategy.py` - Text chunking
- Database: pgvector extension usage

**Key Questions:**
- Which embedding model is used?
- How are documents chunked?
- What is the vector dimension?
- How is similarity calculated?

### 4. Memory Search & Retrieval
**Investigate:**
- `backend/ukf_system/services/unified_memory_search.py` - Unified search
- `backend/memory/services/semantic_search.py` - Semantic search
- `backend/memory/services/hybrid_search.py` - Hybrid search strategies

**Key Questions:**
- How are search queries processed?
- What ranking algorithms are used?
- How are results filtered and scored?
- What is the search performance?

### 5. Document Ingestion & Processing
**Investigate:**
- `backend/memory/services/document_processor.py` - Document processing
- `backend/memory/services/markdown_ingestion_service.py` - Markdown ingestion
- `backend/api/ukf_memory/views/document_views.py` - Upload endpoints

**Key Questions:**
- What document formats are supported?
- How are documents parsed and chunked?
- How is metadata extracted?
- What is the ingestion pipeline?

### 6. Memory Sharing & Integration
**Investigate:**
- `backend/memory/services/memory_sharing_service.py` - Cross-component sharing
- `backend/agent_orchestra/utils/memory_integration.py` - Agent memory access
- `backend/ai_partner/utils/memory_context.py` - AI context retrieval

**Key Questions:**
- How do different components access memory?
- What are the access control mechanisms?
- How is memory context provided to agents?
- What are the integration patterns?

### 7. Knowledge Base Management
**Investigate:**
- `backend/knowledge_base/models/` - Knowledge models
- `backend/knowledge_base/services/` - Knowledge services
- `backend/knowledge_base/admin.py` - Admin interface

**Key Questions:**
- How is structured knowledge stored?
- What knowledge taxonomies exist?
- How is knowledge validated?
- What are the update mechanisms?

### 8. Fiction Detection & Data Quality
**Investigate:**
- `backend/memory/services/fiction_detection_service.py` - Fiction detection
- `backend/memory/services/source_attribution_service.py` - Source tracking
- `backend/memory/utils/confidence_scoring.py` - Confidence metrics

**Key Questions:**
- How is fictional content detected?
- What confidence scoring is used?
- How are sources attributed?
- What quality controls exist?

### 9. Performance & Scalability
**Investigate:**
- `backend/memory/services/cache_service.py` - Memory caching
- `backend/memory/services/batch_processor.py` - Batch operations
- `backend/memory/monitoring/` - Performance monitoring

**Key Questions:**
- What caching strategies are used?
- How are batch operations handled?
- What are the performance metrics?
- How does the system scale?

### 10. Privacy & Security
**Investigate:**
- `backend/memory/services/privacy_filter_service.py` - Privacy filtering
- `backend/memory/models/user_memory_permissions.py` - Access control
- `backend/security/memory_encryption.py` - Encryption

**Key Questions:**
- How is user data isolated?
- What privacy filters exist?
- How is sensitive data handled?
- What encryption is used?

## Critical Files to Review
1. `backend/ukf_system/services/unified_memory_search.py` - Core search functionality
2. `backend/memory/services/embedding_service.py` - Vector embedding logic
3. `backend/memory/models/memory.py` - Core memory model
4. `backend/memory/services/fiction_detection_service.py` - Reality Engine fix
5. `backend/memory/management/commands/ingest_markdown.py` - Bulk ingestion

## Memory System Components
1. **ConversationMemory** - Chat history storage
2. **DocumentMemory** - Uploaded document storage
3. **AgentMemory** - Agent execution results
4. **ResearchMemory** - Research findings
5. **UserFactMemory** - Learned user facts
6. **SystemMemory** - System-wide knowledge

## Expected Outputs from Analysis
1. Memory architecture diagram
2. Data flow through the system
3. Search algorithm documentation
4. Performance benchmarks
5. Storage requirements analysis
6. Privacy compliance report
7. Integration point mapping
8. Embedding coverage statistics

## Special Considerations
- The "Reality Engine" phenomenon and fiction detection
- Memory deduplication strategies
- Token costs for embedding generation
- Vector index optimization
- Memory retention and cleanup policies
- GDPR compliance for memory storage
- Cross-user memory isolation
- The 45,944 memories currently in the system