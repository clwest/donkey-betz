# 🌟 Universal Knowledge Format (UKF)
**One Format to Rule Them All**

## 🎯 The Vision

**Every piece of information in Chris's universe follows ONE format:**
- User ↔ Assistant conversations
- Assistant ↔ Agent communications  
- Agent ↔ Agent messages
- ChatGPT/Claude exports
- Markdown files, PDFs, videos, audio
- Future data types not yet imagined

**ONE search interface. IDENTICAL results. ZERO knowledge silos.**

## 📐 UKF Core Structure

Every knowledge entry follows this EXACT structure:

```json
{
  "ukf_version": "1.0",
  "id": "globally_unique_id",
  "type": "conversation|document|media|thought|communication",
  
  "content": {
    "raw": "original content/transcript/text",
    "processed": "cleaned/formatted version", 
    "summary": "AI-generated summary",
    "chunks": ["semantic chunks for retrieval"],
    "embeddings": [1536]
  },
  
  "participants": {
    "sender": {
      "id": "chris|assistant|agent_name",
      "type": "human|ai_assistant|ai_agent",
      "model": "gpt-4|claude|human|agent_type"
    },
    "receiver": {
      "id": "recipient_id", 
      "type": "human|ai_assistant|ai_agent",
      "model": "model_info_if_ai"
    },
    "observers": ["any other participants"]
  },
  
  "temporal": {
    "created_at": "2023-03-15T02:47:23Z",
    "modified_at": "2023-03-15T03:15:00Z", 
    "ingested_at": "2025-07-12T10:30:00Z",
    "original_date_context": "3am debugging session"
  },
  
  "source": {
    "platform": "move_that_ass|chatgpt|claude|markdown|pdf|url",
    "format": "chat|markdown|pdf|html|video|audio",
    "location": "file://|https://|memory://",
    "project": "project_name",
    "session_id": "conversation_thread_id"
  },
  
  "classification": {
    "primary_type": "conversation|documentation|solution|idea|question",
    "categories": ["debugging", "architecture", "planning"],
    "tags": ["redis", "deployment", "mythology"], 
    "importance": "critical|high|normal|low",
    "success_status": "succeeded|failed|partial|ongoing|unknown"
  },
  
  "context": {
    "trigger": "what initiated this",
    "goal": "what was trying to achieve", 
    "outcome": "what happened",
    "mood": "frustrated|excited|curious|determined",
    "environment": "development|production|research"
  },
  
  "relationships": {
    "parent_id": "conversation or document this came from",
    "child_ids": ["resulting entries"],
    "related_ids": ["related but not direct lineage"],
    "references": ["external URLs, papers, docs"],
    "evolution_chain": ["previous versions of this idea"]
  },
  
  "search_optimization": {
    "keywords": ["extracted", "important", "terms"],
    "entities": {
      "people": ["Chris", "Claude"],
      "technologies": ["Redis", "React"],
      "concepts": ["mythology", "deployment"]
    },
    "search_text": "denormalized searchable text"
  },
  
  "ai_processing": {
    "embedding_model": "text-embedding-3-large",
    "embedding_date": "2025-07-12",
    "processing_notes": "any special handling",
    "quality_score": 0.95
  },
  
  "access_metrics": {
    "times_accessed": 0,
    "last_accessed": null,
    "usefulness_score": null,
    "access_pattern": []
  }
}
```

## 🔄 Conversion Rules

### 1. User ↔ Assistant Conversations
- `sender`: user (chris)
- `receiver`: assistant  
- `type`: conversation
- Preserve full context and thinking chains

### 2. Assistant ↔ Agent Communications
- `sender`: assistant
- `receiver`: specific agent
- `type`: communication
- Include task context and orchestration details

### 3. Agent ↔ Agent Messages  
- `sender`/`receiver`: both agents
- `type`: communication
- Preserve coordination context and data sharing

### 4. ChatGPT/Claude Exports
- Parse `conversations.json` 
- Split into individual exchanges
- Preserve "thinking" sections
- Extract dates from metadata

### 5. Markdown Files
- `type`: document
- Extract creation/modification dates
- Preserve file path as context
- Auto-categorize based on content

### 6. External Documents (PDF/URL/Video)
- Extract text/transcripts
- Preserve source URL
- Generate summaries
- Create searchable chunks

## 🔍 Universal Search Interface

**EVERY system uses the SAME query interface:**

```python
class UniversalKnowledgeSearch:
    def search(
        query: str,
        filters: {
            "type": ["conversation", "document"],
            "participants": ["chris", "assistant"], 
            "date_range": {"from": date, "to": date},
            "categories": ["debugging"],
            "project": "move_that_ass"
        }
    ) -> List[UKFEntry]:
        # Same results across ALL systems
```

## ✅ Guarantees

- **✅ Identical Results**: Same query = same results across all systems
- **✅ Complete History**: Every interaction is captured
- **✅ Rich Context**: Never lose why/when/how  
- **✅ Forward Compatible**: New data types fit the format
- **✅ Temporal Integrity**: Real dates, not ingestion dates

## 🎯 Success Criteria

✅ **One search finds everything**  
✅ **Chris asks "when did I mention Redis?" - gets results from markdown, chats, agent communications**  
✅ **Agents can see user conversations**  
✅ **Assistant knows what agents discussed**  
✅ **100% temporal accuracy**  
✅ **Zero knowledge silos**

## 🚀 The Promise

**"One Format, One Truth, Universal Access"**

Every piece of knowledge in Chris's universe follows the same structure, searchable by any system, returning identical results. No more confusion about where information lives or what format it's in.

This creates a TRUE universal system where EVERYTHING is in one format, searchable by ANYONE (Assistant, Agents, You), with IDENTICAL results! 🎯