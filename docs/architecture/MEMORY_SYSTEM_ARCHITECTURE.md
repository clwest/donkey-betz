<!-- DOC-POINTER-V2 (Session 1145) -->
> **Status:** Superseded
> **Deprecated:** Session 1145 (2026-05-25)
> **Current canon:** [`docs/PLATFORM_INVENTORY.md`](../PLATFORM_INVENTORY.md) (runtime counts) + [`docs/topics/personal-assistant.md`](../topics/personal-assistant.md) (PA enrichment + search_docs tool) + [`docs/00-START-HERE/DOC_LIFECYCLE.md`](../00-START-HERE/DOC_LIFECYCLE.md) (current truth rules).
> **Change reason:** Session 178 snapshot of a memory/embedding reality that has materially changed: pgvector blocker closed Session 1140 (#2172), Document table now carries 852 docs / 14149 chunks (Session 1142), `search_docs` PA tool live, frontend moved from `ai_image_studio.html` to React.
> **Preserved because:** documents the pre-pgvector style-memory + RAG-dormant snapshot; useful as build-history record for the memory subsystem's evolution. Do NOT cite for current state.

# Memory & Learning System Architecture

**Document Created:** November 24, 2025 - Session 178
**Purpose:** Complete map of memory flow, what's active, what's dormant, and how to connect everything

---

## Executive Summary

| Component | Status | Records | Usage |
|-----------|--------|---------|-------|
| **StyleMemory** | ACTIVE | 3 | User ratings (love/like/dislike) |
| **StylePattern** | ACTIVE | 6 | Detected preferences |
| **UserMemoryContext** | ACTIVE | 6 | General memory storage |
| **DocumentEmbedding** | DORMANT | 0 | RAG system - not connected |
| **UnifiedEmbedding** | DORMANT | 0 | Cross-system knowledge - not used |
| **UserEmbedding** | DORMANT | 0 | Profile embeddings - not used |
| **PGVector** | INSTALLED | - | Extension ready, using JSONB instead |

**Current Learning:** Working but minimal - 3 interactions → 6 patterns → injected into prompts
**Opportunity:** Full RAG + vector similarity search infrastructure is built but not connected

---

## Part 1: Current Rating Interaction Data Flow

### Visual Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     USER RATES CONTENT (👍❤️👎)                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ FRONTEND: ai_image_studio.html                                          │
│                                                                          │
│   function rateContent(contentId, interactionType) {                    │
│     fetch('/api/v1/style-memory/', {                                    │
│       method: 'POST',                                                   │
│       body: JSON.stringify({                                            │
│         content_id: contentId,                                          │
│         interaction_type: 'love' | 'like' | 'dislike',                  │
│         project_id: currentProjectId,  // Session 172                   │
│         prompt: originalPrompt,                                         │
│         model_used: 'stability-ai-ultra'                                │
│       })                                                                │
│     })                                                                  │
│   }                                                                     │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ BACKEND: style_memory/views.py - capture_interaction()                  │
│                                                                          │
│   @api_view(['POST'])                                                   │
│   def capture_interaction(request):                                     │
│       # 1. Create StyleMemory record                                    │
│       style_memory = StyleMemory.objects.create(                        │
│           user=user,                                                    │
│           project_id=project_id,                                        │
│           content_id=content_id,                                        │
│           interaction_type='love',                                      │
│           prompt=prompt,                                                │
│           style_elements=['minimalist', 'bold'],  # ⚠️ HARDCODED!      │
│           color_palette=['#FF6B6B', '#4ECDC4']    # ⚠️ HARDCODED!      │
│       )                                                                 │
│                                                                         │
│       # 2. Update patterns                                              │
│       _update_patterns(user, style_memory)                              │
│                                                                         │
│       # 3. Generate suggestions                                         │
│       _generate_suggestions(user)                                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
┌──────────────────────┐ ┌──────────────────┐ ┌──────────────────────┐
│ TABLE: StyleMemory   │ │ TABLE:           │ │ TABLE:               │
│                      │ │ StylePattern     │ │ StyleSuggestion      │
│ - user_id            │ │                  │ │                      │
│ - content_id         │ │ - pattern_type   │ │ - title              │
│ - interaction_type   │ │ - pattern_value  │ │ - prompt_template    │
│ - project_id         │ │ - confidence     │ │ - confidence         │
│ - prompt             │ │ - frequency      │ │ - status             │
│ - recipe (JSONB)     │ │ - last_seen      │ │ - based_on_patterns  │
│ - style_elements[]   │ └──────────────────┘ └──────────────────────┘
│ - color_palette[]    │           │
└──────────────────────┘           │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ PATTERN UPDATE: _update_patterns()                                      │
│                                                                          │
│   for element in style_memory.style_elements:                           │
│       pattern, created = StylePattern.objects.get_or_create(            │
│           user=user,                                                    │
│           pattern_type='style',                                         │
│           pattern_value=element                                         │
│       )                                                                 │
│       pattern.frequency += 1                                            │
│       pattern.confidence = min(0.95, confidence + 0.05)                 │
│       pattern.related_memories.add(style_memory)                        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ NEXT GENERATION: Style preferences injected into AI prompt             │
│                                                                          │
│ EnhancedPersonalAIAssistant._get_style_preferences_context():           │
│                                                                          │
│   total = StyleMemory.objects.filter(user=user).count()                 │
│   loved = StyleMemory.filter(interaction_type='love').count()           │
│   patterns = StylePattern.objects.filter(user=user)                     │
│                                                                          │
│   return f'''                                                           │
│   Style Learning (based on {total} ratings: {loved} loved):             │
│   - Preferred style: {patterns.style}                                   │
│   - Preferred color: {patterns.color}                                   │
│   '''                                                                   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ GPT SYSTEM PROMPT (receives learned preferences)                        │
│                                                                          │
│   You are an AI assistant for content creation.                         │
│                                                                          │
│   Style Learning (based on 3 ratings: 1 loved, 2 liked):                │
│   - Preferred style: minimalist, bold, contemporary                     │
│   - Preferred color: #FF6B6B, #4ECDC4, #45B7D1                          │
│                                                                          │
│   Generate content that aligns with user's demonstrated preferences.    │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Part 2: Current Issues Found

### Issue 1: Hardcoded Style Elements

**Location:** `style_memory/views.py:66-67`

```python
# CURRENT (BROKEN):
style_elements=['minimalist', 'bold', 'contemporary'],  # Always same!
color_palette=['#FF6B6B', '#4ECDC4', '#45B7D1']          # Always same!
```

**Problem:** Every rating stores the same style elements regardless of the actual content.

**Fix Required:** Extract actual style elements from the image metadata or prompt.

### Issue 2: No Embedding Generation

**Status:** RAGSystem class exists but never called. No content gets embedded.

### Issue 3: PGVector Unused

**Status:** Extension installed, but vectors stored as JSONB arrays (slow similarity search).

---

## Part 3: Dormant Systems - What's Built But Not Connected

### A. RAG System (`content/embeddings.py`)

```python
# BUILT BUT UNUSED:
class RAGSystem:
    async def process_document_for_rag(document, embedding_model):
        # 1. Chunk document
        chunks = self.text_splitter.split_text(content)

        # 2. Generate embeddings for each chunk
        for chunk in chunks:
            embedding = await self.embedding_manager.generate_embedding(chunk)

            # 3. Store in DocumentEmbedding (JSONB, not pgvector!)
            DocumentEmbedding.objects.create(
                document=document,
                chunk_text=chunk,
                embedding_vector=embedding  # Stored as JSON array
            )

    async def semantic_search(query, knowledge_base, top_k=5):
        # 1. Embed query
        query_embedding = await self.embedding_manager.generate_embedding(query)

        # 2. Manual similarity calculation (SLOW - should use pgvector)
        all_embeddings = DocumentEmbedding.objects.filter(...)
        similarities = []
        for emb in all_embeddings:
            sim = cosine_similarity(query_embedding, emb.embedding_vector)
            similarities.append((emb, sim))

        # 3. Return top results
        return sorted(similarities, key=lambda x: -x[1])[:top_k]
```

### B. Embedding Providers (Ready but unused)

```python
# FOUR PROVIDERS IMPLEMENTED:
class OpenAIEmbeddingProvider:       # text-embedding-3-small/large
class SentenceTransformerProvider:   # all-MiniLM-L6-v2 (local, free!)
class CohereEmbeddingProvider:       # embed-english-v3.0
class LocalEmbeddingProvider:        # Custom local models

# All have:
# - generate_embedding(text) -> List[float]
# - calculate_similarity(emb1, emb2) -> float
```

### C. UnifiedEmbedding (`persistence/models.py`)

```python
# DESIGNED FOR CROSS-SYSTEM KNOWLEDGE:
class UnifiedEmbedding:
    content_type = 'image' | 'video' | 'agent_action' | 'spider_data'
    content_id = UUID
    content_text = TEXT
    embedding = JSONB  # Should be pgvector!
    importance_score = FLOAT
    source_system = 'agent' | 'system' | 'spider' | 'user'
    creator_agent = VARCHAR
    tags = ARRAY
```

### D. UserEmbedding (`core/models.py`)

```python
# DESIGNED FOR PROFILE UNDERSTANDING:
class UserEmbedding:
    user = FK
    content = TEXT  # What's being embedded
    content_type = 'interaction' | 'preference' | 'goal' | 'skill'
    embedding_vector = JSONB
    confidence_score = FLOAT
    usage_count = INT
```

---

## Part 4: Activation Plan

### Phase 1: Fix Current Learning (2 hours)

#### 1.1 Extract Real Style Elements from Content

```python
# NEW: style_memory/style_extractor.py

class StyleExtractor:
    """Extract actual style elements from images/prompts"""

    def extract_from_prompt(self, prompt: str) -> dict:
        """Use GPT to extract style elements from prompt"""
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "system",
                "content": "Extract style elements from this image generation prompt. Return JSON with: style_elements (list), colors (list of hex), mood (string), composition (string)"
            }, {
                "role": "user",
                "content": prompt
            }],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)

    def extract_from_image(self, image_path: str) -> dict:
        """Use vision model to analyze image style"""
        # Could use GPT-4 Vision or local model
        pass
```

#### 1.2 Update capture_interaction to Use Real Data

```python
# MODIFIED: style_memory/views.py

def capture_interaction(request):
    # ... existing code ...

    # NEW: Extract actual style from prompt
    extractor = StyleExtractor()
    if prompt:
        style_data = extractor.extract_from_prompt(prompt)
        style_elements = style_data.get('style_elements', [])
        color_palette = style_data.get('colors', [])
    else:
        style_elements = []
        color_palette = []

    style_memory = StyleMemory.objects.create(
        # ... other fields ...
        style_elements=style_elements,  # NOW REAL!
        color_palette=color_palette      # NOW REAL!
    )
```

### Phase 2: Activate Embeddings (4 hours)

#### 2.1 Upgrade to Native PGVector

```python
# NEW: content/models.py

from pgvector.django import VectorField

class DocumentEmbedding(UnifiedBaseModel):
    # CHANGE FROM:
    # embedding_vector = models.JSONField()

    # CHANGE TO:
    embedding_vector = VectorField(dimensions=1536)  # OpenAI small

    class Meta:
        indexes = [
            # HNSW index for fast similarity search
            HnswIndex(
                name='embedding_hnsw_idx',
                fields=['embedding_vector'],
                m=16,
                ef_construction=64,
                opclasses=['vector_cosine_ops']
            )
        ]
```

#### 2.2 Migration

```bash
# Generate migration
python manage.py makemigrations content --name upgrade_to_pgvector

# Migration file will need manual edit:
from pgvector.django import VectorExtension

class Migration(migrations.Migration):
    operations = [
        VectorExtension(),  # Ensure extension exists
        migrations.AlterField(
            model_name='documentembedding',
            name='embedding_vector',
            field=VectorField(dimensions=1536),
        ),
    ]
```

#### 2.3 Native Similarity Search

```python
# UPGRADED: content/embeddings.py

from pgvector.django import L2Distance, CosineDistance

class RAGSystem:
    def semantic_search(self, query: str, top_k: int = 5):
        # Generate query embedding
        query_embedding = self.embedding_manager.generate_embedding(query)

        # NATIVE PGVECTOR SEARCH (100x faster!)
        results = DocumentEmbedding.objects.annotate(
            distance=CosineDistance('embedding_vector', query_embedding)
        ).order_by('distance')[:top_k]

        return results
```

### Phase 3: Connect Style Learning to Embeddings (3 hours)

#### 3.1 Embed User Preferences

```python
# NEW: style_memory/embedding_integration.py

class StyleEmbeddingService:
    """Connect style learning to vector embeddings"""

    def __init__(self):
        self.embedding_provider = OpenAIEmbeddingProvider()

    def embed_user_preference(self, user, style_memory):
        """Create searchable embedding for user preference"""
        # Build text representation
        text = f"""
        User preference: {style_memory.interaction_type}
        Content: {style_memory.prompt}
        Style: {', '.join(style_memory.style_elements)}
        Colors: {', '.join(style_memory.color_palette)}
        """

        # Generate embedding
        embedding = self.embedding_provider.generate_embedding(text)

        # Store in UserEmbedding
        UserEmbedding.objects.create(
            user=user,
            content=text,
            content_type='preference',
            embedding_vector=embedding,
            confidence_score=0.8
        )

    def find_similar_preferences(self, user, query: str, top_k: int = 5):
        """Find past preferences similar to current request"""
        query_embedding = self.embedding_provider.generate_embedding(query)

        return UserEmbedding.objects.filter(
            user=user,
            content_type='preference'
        ).annotate(
            distance=CosineDistance('embedding_vector', query_embedding)
        ).order_by('distance')[:top_k]
```

#### 3.2 Enhanced Style Context with Semantic Search

```python
# UPGRADED: core/personal_ai_assistant_enhanced.py

def _get_style_preferences_context(self):
    """Get style context using both patterns AND semantic search"""

    # EXISTING: Pattern-based preferences
    patterns = StylePattern.objects.filter(user=self.user)
    pattern_context = self._format_patterns(patterns)

    # NEW: Semantic search for relevant past preferences
    if hasattr(self, 'current_prompt') and self.current_prompt:
        style_service = StyleEmbeddingService()
        similar_prefs = style_service.find_similar_preferences(
            self.user,
            self.current_prompt,
            top_k=3
        )

        semantic_context = "\n".join([
            f"- Similar past preference: {pref.content[:100]}..."
            for pref in similar_prefs
        ])
    else:
        semantic_context = ""

    return f"""
    {pattern_context}

    Semantically Similar Past Preferences:
    {semantic_context}
    """
```

### Phase 4: Cross-System Knowledge (Future)

```python
# FUTURE: Connect agents to shared knowledge

class AgentKnowledgeSharing:
    """Enable agents to learn from each other"""

    def share_learning(self, source_agent: str, learning: dict):
        """Store agent learning in UnifiedEmbedding"""
        text = f"Agent {source_agent} learned: {learning['insight']}"
        embedding = generate_embedding(text)

        UnifiedEmbedding.objects.create(
            content_type='agent_learning',
            content_text=text,
            embedding=embedding,
            source_system='agent',
            creator_agent=source_agent,
            importance_score=learning.get('confidence', 0.5)
        )

    def query_collective_knowledge(self, agent: str, query: str):
        """Search all agent learnings for relevant knowledge"""
        return UnifiedEmbedding.objects.annotate(
            distance=CosineDistance('embedding', query_embedding)
        ).order_by('distance')[:10]
```

---

## Part 5: Implementation Priority

### Immediate (Session 179) - 2 hours
1. **Fix hardcoded style elements** - Use GPT to extract real styles
2. **Test with real ratings** - Verify patterns update correctly

### Short-term (Session 180-181) - 4 hours
3. **Upgrade to native pgvector** - Migration + index creation
4. **Implement semantic search** - Replace manual similarity calc

### Medium-term (Session 182-183) - 4 hours
5. **Embed user preferences** - Connect StyleMemory → UserEmbedding
6. **Enhanced style context** - Use semantic search in AI prompts

### Long-term (Future Sessions) - 8 hours
7. **Cross-agent learning** - UnifiedEmbedding for shared knowledge
8. **RAG for documents** - Full document processing pipeline
9. **Automatic pattern detection** - ML-based clustering

---

## Part 6: Files to Modify

| File | Changes Needed | Priority |
|------|----------------|----------|
| `style_memory/views.py` | Extract real style elements | P0 |
| `style_memory/style_extractor.py` | NEW - Style extraction service | P0 |
| `content/models.py` | Upgrade to VectorField | P1 |
| `content/embeddings.py` | Use native pgvector search | P1 |
| `core/personal_ai_assistant_enhanced.py` | Add semantic preference search | P2 |
| `style_memory/embedding_integration.py` | NEW - Connect styles to embeddings | P2 |

---

## Part 7: Expected Outcomes

### After Phase 1 (Fix Current)
- Style patterns reflect ACTUAL user preferences
- Learning becomes meaningful (not hardcoded)
- AI generations better match user taste

### After Phase 2 (Activate Embeddings)
- 100x faster similarity search
- Native vector indexing
- Scalable to millions of embeddings

### After Phase 3 (Connect Systems)
- "Find content similar to what I loved before"
- Semantic understanding of preferences
- Context-aware style recommendations

### After Phase 4 (Cross-System)
- Agents share knowledge
- Collective intelligence
- Platform-wide learning

---

## Summary

**Current State:** Learning system works but with hardcoded data and no vector search.

**Built But Not Used:**
- RAG system with 4 embedding providers
- PGVector extension installed
- UserEmbedding, UnifiedEmbedding models
- Cross-agent knowledge infrastructure

**Path Forward:**
1. Fix hardcoded styles (2 hours)
2. Activate pgvector (4 hours)
3. Connect embeddings to learning (3 hours)
4. Enable cross-system knowledge (8 hours future)

**Total to Activate Everything:** ~17 hours across 5-6 sessions

---

**Document Created:** November 24, 2025 - Session 178
**Next Action:** Fix hardcoded style elements in `style_memory/views.py`
