# 🧠 Memory System Documentation - AI Content Studio

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Installation & Setup](#installation--setup)
4. [Core Components](#core-components)
5. [API Reference](#api-reference)
6. [Integration Guide](#integration-guide)
7. [Frontend Usage](#frontend-usage)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)
10. [Performance Optimization](#performance-optimization)

## Overview

The AI Content Studio Memory System is a sophisticated vector-based contextual storage and retrieval system that enhances content generation with relevant historical context. It uses OpenAI embeddings and vector similarity search to provide intelligent context to all content generation features.

### Key Features
- **Vector-based similarity search** using OpenAI embeddings (1536 dimensions)
- **Dual database support** - PostgreSQL with pgvector (production) and SQLite (development)
- **Automatic context enrichment** for all content generation
- **User-isolated memory spaces** for privacy and personalization
- **Real-time memory search** with relevance scoring
- **Automatic memory creation** from generated content
- **Metadata support** for rich contextual information

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (studio.html)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Memory Panel │  │ Search UI    │  │ Stats Display│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (/api/memory/)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   /search/   │  │   /store/    │  │   /stats/    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                Memory Service (services.py)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Embeddings  │  │Vector Search │  │   Storage    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Database Layer                            │
│  ┌──────────────────────┐    ┌──────────────────────┐      │
│  │  PostgreSQL+pgvector │    │  SQLite (dev mode)   │      │
│  │  - Vector indexes    │    │  - JSON embeddings   │      │
│  │  - HNSW optimization │    │  - Importance sort   │      │
│  └──────────────────────┘    └──────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Database Schema

```python
class Memory(models.Model):
    user = ForeignKey(User)           # User isolation
    content_text = TextField()         # Original content
    embedding = VectorField(1536)      # OpenAI embeddings
    metadata = JSONField()             # Flexible context data
    importance_score = FloatField()    # Relevance scoring (0-1)
    created_at = DateTimeField()       # Timestamp
```

## Installation & Setup

### Prerequisites

1. **OpenAI API Key** for embedding generation:
```bash
export OPENAI_API_KEY="sk-..."
```

2. **For Production (PostgreSQL)**:
```bash
# Install PostgreSQL and pgvector extension
sudo apt-get install postgresql postgresql-contrib
sudo -u postgres psql -c "CREATE EXTENSION vector;"

# Install Python dependencies
pip install pgvector==0.2.5 psycopg2-binary==2.9.9
```

3. **For Development (SQLite)**:
```bash
# No additional setup required - SQLite is included
# System automatically falls back to JSON storage
```

### Database Migration

```bash
# Apply memory system migrations
python manage.py migrate memory

# For production with pgvector
python manage.py migrate memory --database=postgresql
```

### Environment Configuration

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql' if os.getenv('USE_POSTGRES') else 'django.db.backends.sqlite3',
        # ... other settings
    }
}

# Enable vector extension for PostgreSQL
if 'postgresql' in DATABASES['default']['ENGINE']:
    DATABASES['default']['OPTIONS'] = {
        'options': '-c shared_preload_libraries=vector'
    }
```

## Core Components

### 1. Memory Service (`backend/memory/services.py`)

The central service managing all memory operations:

```python
class MemoryService:
    def __init__(self):
        self.client = OpenAI()
        
    def generate_embedding(self, text):
        """Generate OpenAI embeddings for text"""
        # Uses text-embedding-3-small model
        # Returns 1536-dimensional vector
        
    def store_memory(self, user, content, importance=0.5, metadata=None):
        """Store content with embeddings in memory"""
        # Generates embeddings
        # Creates Memory object
        # Handles both PostgreSQL and SQLite
        
    def search_memories(self, user, query, limit=5):
        """Vector similarity search for relevant memories"""
        # Generates query embedding
        # Performs cosine similarity search
        # Returns ranked results with scores
```

### 2. Content Generator Integration (`backend/content/generators.py`)

Automatic memory enrichment in content generation:

```python
class ContentGenerator:
    def generate_content(self, user, prompt, content_type):
        # 1. Search relevant memories
        memories = self.memory_service.search_memories(user, prompt, limit=5)
        
        # 2. Enrich prompt with context
        context = self._format_memory_context(memories[:3])
        enriched_prompt = f"{prompt}\n\nContext:\n{context}"
        
        # 3. Generate content with GPT-4
        response = self._generate_with_context(enriched_prompt)
        
        # 4. Store result as new memory
        self.memory_service.store_memory(
            user=user,
            content=response,
            importance=0.6,
            metadata={'type': content_type}
        )
        
        return response
```

### 3. Vector Search Implementation

**PostgreSQL with pgvector**:
```python
# True vector similarity using pgvector
from pgvector.django import CosineDistance

memories = Memory.objects.filter(user=user).annotate(
    similarity=1 - CosineDistance('embedding', query_embedding)
).order_by('-similarity')[:limit]
```

**SQLite Fallback**:
```python
# Importance-based ranking for development
memories = Memory.objects.filter(
    user=user
).order_by('-importance_score', '-created_at')[:limit]
```

## API Reference

### 1. Search Memories
**Endpoint**: `POST /api/memory/search/`

**Request**:
```json
{
    "query": "AI content generation techniques",
    "limit": 5
}
```

**Response**:
```json
{
    "results": [
        {
            "id": 123,
            "content": "Advanced prompt engineering for GPT-4...",
            "similarity": 0.92,
            "metadata": {
                "type": "blog_post",
                "content_id": 456
            },
            "created_at": "2025-01-29T10:30:00Z"
        }
    ],
    "count": 5
}
```

### 2. Store Memory
**Endpoint**: `POST /api/memory/store/`

**Request**:
```json
{
    "content": "Important information about customer preferences...",
    "importance": 0.8,
    "metadata": {
        "source": "user_feedback",
        "category": "preferences"
    }
}
```

**Response**:
```json
{
    "success": true,
    "memory": {
        "id": 789,
        "content": "Important information about customer preferences...",
        "importance": 0.8,
        "created_at": "2025-01-29T11:00:00Z"
    }
}
```

### 3. Memory Statistics
**Endpoint**: `GET /api/memory/stats/`

**Response**:
```json
{
    "total_memories": 1234,
    "recent_memories": [
        {
            "id": 890,
            "content_preview": "Latest blog post about AI trends...",
            "created_at": "2025-01-29T10:45:00Z"
        }
    ],
    "memory_by_type": {
        "blog_post": 456,
        "social_media": 321,
        "generated_text": 457
    }
}
```

## Integration Guide

### Adding Memory to New Features

1. **Import Memory Service**:
```python
from memory.services import MemoryService

class YourFeatureGenerator:
    def __init__(self):
        self.memory_service = MemoryService()
```

2. **Search for Context**:
```python
def generate_with_memory(self, user, prompt):
    # Search relevant memories
    memories = self.memory_service.search_memories(
        user=user, 
        query=prompt, 
        limit=5
    )
    
    # Format context
    context = "\n".join([m['content'][:200] for m in memories[:3]])
    
    # Use in generation
    enhanced_prompt = f"{prompt}\n\nRelevant context:\n{context}"
```

3. **Store Generated Content**:
```python
def save_to_memory(self, user, content, content_type):
    self.memory_service.store_memory(
        user=user,
        content=content,
        importance=0.7,
        metadata={
            'type': content_type,
            'timestamp': datetime.now().isoformat()
        }
    )
```

### Campaign Mode Integration

```python
# backend/api/views_campaign.py
def generate_campaign_content(request, campaign_id):
    # Get campaign context from memory
    campaign_memories = memory_service.search_memories(
        user=request.user,
        query=f"campaign {campaign.name} {campaign.target_audience}",
        limit=10
    )
    
    # Use memories to maintain consistency
    context = format_campaign_context(campaign_memories)
    
    # Generate content with context
    for channel in campaign.channels:
        content = generate_channel_content(channel, context)
        
        # Store each piece as memory
        memory_service.store_memory(
            user=request.user,
            content=content,
            importance=0.8,
            metadata={
                'campaign_id': campaign_id,
                'channel': channel
            }
        )
```

## Frontend Usage

### JavaScript Implementation

```javascript
// frontend/studio.html

// Search memories
async function searchMemories(query) {
    const response = await fetch('/api/memory/search/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Token ${authToken}`
        },
        body: JSON.stringify({ query, limit: 5 })
    });
    
    const data = await response.json();
    displayMemoryResults(data.results);
}

// Auto-save to memory
async function autoSaveToMemory(content, importance = 0.5) {
    if (!document.getElementById('autoSaveMemory').checked) return;
    
    await fetch('/api/memory/store/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Token ${authToken}`
        },
        body: JSON.stringify({
            content,
            importance,
            metadata: { source: 'studio_generation' }
        })
    });
}

// Enrich prompt with memory context
function enrichPromptWithMemory(originalPrompt, memories) {
    const context = memories
        .slice(0, 3)
        .map(m => m.content.substring(0, 200))
        .join('\n\n');
    
    return `${originalPrompt}\n\nRelevant context from memory:\n${context}`;
}
```

### UI Components

```html
<!-- Memory Panel in studio.html -->
<div class="memory-panel bg-gray-800 rounded-lg p-4">
    <h3 class="text-lg font-bold mb-4">Memory System</h3>
    
    <!-- Search Interface -->
    <div class="memory-search mb-4">
        <input type="text" id="memorySearchInput" 
               placeholder="Search memories..." 
               class="w-full px-3 py-2 bg-gray-700 rounded">
        <button onclick="searchMemories()" 
                class="mt-2 px-4 py-2 bg-blue-600 rounded">
            Search
        </button>
    </div>
    
    <!-- Memory Results -->
    <div id="memoryResults" class="space-y-2">
        <!-- Results displayed here -->
    </div>
    
    <!-- Auto-save Toggle -->
    <div class="mt-4">
        <label class="flex items-center">
            <input type="checkbox" id="autoSaveMemory" checked>
            <span class="ml-2">Auto-save to memory</span>
        </label>
    </div>
    
    <!-- Memory Stats -->
    <div class="mt-4 text-sm text-gray-400">
        <span id="memoryCount">0</span> memories stored
    </div>
</div>
```

## Best Practices

### 1. Content Chunking
```python
# Break large content into manageable chunks
def chunk_content_for_memory(content, chunk_size=1000):
    chunks = []
    for i in range(0, len(content), chunk_size):
        chunk = content[i:i+chunk_size]
        chunks.append({
            'content': chunk,
            'metadata': {'chunk_index': i // chunk_size}
        })
    return chunks
```

### 2. Importance Scoring
```python
# Calculate dynamic importance based on content characteristics
def calculate_importance(content, user_interaction=False):
    base_score = 0.5
    
    # Increase for user interactions
    if user_interaction:
        base_score += 0.2
    
    # Increase for longer, detailed content
    if len(content) > 1000:
        base_score += 0.1
    
    # Increase for content with keywords
    important_keywords = ['key', 'important', 'critical', 'must']
    if any(keyword in content.lower() for keyword in important_keywords):
        base_score += 0.1
    
    return min(base_score, 1.0)
```

### 3. Memory Cleanup
```python
# Periodic cleanup of old, low-importance memories
def cleanup_old_memories(user, days_old=90, importance_threshold=0.3):
    cutoff_date = timezone.now() - timedelta(days=days_old)
    
    Memory.objects.filter(
        user=user,
        created_at__lt=cutoff_date,
        importance_score__lt=importance_threshold
    ).delete()
```

### 4. Context Window Management
```python
# Manage context size for API limits
def optimize_context_for_generation(memories, max_tokens=2000):
    context_parts = []
    current_tokens = 0
    
    for memory in memories:
        memory_tokens = len(memory['content']) // 4  # Rough token estimate
        if current_tokens + memory_tokens > max_tokens:
            break
        
        context_parts.append(memory['content'][:500])
        current_tokens += memory_tokens
    
    return '\n\n'.join(context_parts)
```

## Troubleshooting

### Common Issues and Solutions

#### 1. **Vector Search Not Working in Development**
**Issue**: SQLite doesn't support vector operations
**Solution**: System automatically falls back to importance-based sorting
```python
# Check database type in services.py
if 'postgresql' in connection.settings_dict['ENGINE']:
    # Use vector search
else:
    # Use fallback sorting
```

#### 2. **Embedding Generation Failures**
**Issue**: OpenAI API errors or rate limits
**Solution**: Implement retry logic with exponential backoff
```python
@retry(tries=3, delay=1, backoff=2)
def generate_embedding_with_retry(text):
    return memory_service.generate_embedding(text)
```

#### 3. **Memory Search Returns Irrelevant Results**
**Issue**: Poor similarity scores
**Solution**: Adjust search parameters and filtering
```python
# Filter by minimum similarity threshold
memories = Memory.objects.annotate(
    similarity=1 - CosineDistance('embedding', query_embedding)
).filter(similarity__gte=0.7)  # Minimum 70% similarity
```

#### 4. **High Memory Usage with Large Datasets**
**Issue**: Loading too many embeddings into memory
**Solution**: Use pagination and streaming
```python
# Paginate memory queries
from django.core.paginator import Paginator

memories = Memory.objects.filter(user=user)
paginator = Paginator(memories, 100)  # 100 items per page
```

## Performance Optimization

### 1. Index Optimization (PostgreSQL)

```sql
-- HNSW index for fast vector search
CREATE INDEX memories_embedding_hnsw_idx 
ON memory_memory 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- B-tree indexes for filtering
CREATE INDEX memories_user_created_idx 
ON memory_memory(user_id, created_at DESC);

CREATE INDEX memories_importance_idx 
ON memory_memory(importance_score DESC);
```

### 2. Query Optimization

```python
# Efficient batch embedding generation
def batch_generate_embeddings(texts, batch_size=20):
    embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        batch_embeddings = openai.embeddings.create(
            model="text-embedding-3-small",
            input=batch
        )
        embeddings.extend(batch_embeddings.data)
    return embeddings
```

### 3. Caching Strategy

```python
from django.core.cache import cache

def cached_memory_search(user_id, query, limit=5):
    cache_key = f"memory_search:{user_id}:{hash(query)}:{limit}"
    
    # Check cache first
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    
    # Perform search
    result = memory_service.search_memories(user_id, query, limit)
    
    # Cache for 5 minutes
    cache.set(cache_key, result, 300)
    
    return result
```

### 4. Async Processing

```python
from celery import shared_task

@shared_task
def async_store_memory(user_id, content, importance, metadata):
    """Store memory asynchronously to avoid blocking"""
    user = User.objects.get(id=user_id)
    memory_service = MemoryService()
    memory_service.store_memory(user, content, importance, metadata)
```

## Memory System Metrics

### Monitoring Queries

```sql
-- Memory usage by user
SELECT 
    user_id, 
    COUNT(*) as memory_count,
    AVG(importance_score) as avg_importance,
    MAX(created_at) as last_memory
FROM memory_memory
GROUP BY user_id;

-- Memory growth over time
SELECT 
    DATE(created_at) as date,
    COUNT(*) as memories_created
FROM memory_memory
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Most similar memories (PostgreSQL)
SELECT 
    m1.id, 
    m2.id,
    1 - (m1.embedding <=> m2.embedding) as similarity
FROM memory_memory m1, memory_memory m2
WHERE m1.id < m2.id
ORDER BY similarity DESC
LIMIT 10;
```

## Future Enhancements

### Planned Features

1. **Memory Decay Algorithm**
   - Automatic importance reduction over time
   - Reinforcement through repeated access

2. **Semantic Clustering**
   - Group related memories automatically
   - Topic extraction and categorization

3. **Cross-User Memory Sharing**
   - Team memories for collaborative projects
   - Public memory marketplace

4. **Advanced Metadata Queries**
   - Search by metadata fields
   - Complex filtering and aggregation

5. **Memory Compression**
   - Summarization of old memories
   - Hierarchical memory structures

6. **Multi-Modal Memories**
   - Image embeddings with CLIP
   - Audio transcription and embedding

---

## Quick Reference

### Essential Commands

```bash
# Check memory system status
python manage.py shell
>>> from memory.models import Memory
>>> Memory.objects.count()

# Generate embeddings for existing content
python manage.py generate_embeddings --user=all

# Cleanup old memories
python manage.py cleanup_memories --days=90 --importance=0.3

# Rebuild vector indexes (PostgreSQL)
python manage.py dbshell
=> REINDEX INDEX memories_embedding_hnsw_idx;
```

### Configuration Variables

```python
# settings.py
MEMORY_EMBEDDING_MODEL = "text-embedding-3-small"
MEMORY_EMBEDDING_DIMENSIONS = 1536
MEMORY_SEARCH_LIMIT_DEFAULT = 5
MEMORY_CONTEXT_MAX_TOKENS = 2000
MEMORY_AUTO_SAVE_ENABLED = True
MEMORY_IMPORTANCE_DEFAULT = 0.5
```

---

*Last Updated: January 29, 2025*
*Version: 1.0.0*
*AI Content Studio Memory System Documentation*