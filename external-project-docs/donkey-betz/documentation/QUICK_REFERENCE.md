# PostgreSQL & PGVector Quick Reference

## Connection Info
```bash
# Direct PostgreSQL
PGPASSWORD=secure_password psql -h 127.0.0.1 -p 5432 -U moveyourazz_user -d moveyourazz_dev

# Via PGBouncer (connection pooling)
PGPASSWORD=secure_password psql -h 127.0.0.1 -p 6432 -U moveyourazz_user -d moveyourazz_dev
```

## Key Statistics at a Glance

| Metric | Value |
|--------|-------|
| **Total Tables** | 200+ |
| **Vector Tables** | 18 |
| **Vector Dimension** | 1536 |
| **Unified Memory Entries** | 123 |
| **Conversation Embeddings** | 85 |
| **Agent Templates** | 34 |
| **Agent Instances** | 44 |
| **Embedding Coverage** | 97.6% |
| **Vector Indexes** | 0 ⚠️ |

## Most Important Tables

### Memory & Embeddings
- `unified_memory_entries` - Main memory (123 entries, 120 with embeddings)
- `ai_partner_conversationembedding` - Conversations (85 entries)
- `learning_intelligence_symbolicmemoryanchor` - Learning patterns (8 entries)

### Agent System
- `agent_orchestra_agenttemplate` - Agent definitions (34 templates)
- `agent_orchestra_agentinstance` - Agent runs (44 instances)
- `agent_orchestra_agentresult` - Results (0 - needs attention!)

## Common Queries

### Check Memory Stats
```sql
SELECT COUNT(*) as total, 
       COUNT(embedding) as with_embedding 
FROM unified_memory_entries;
```

### List Agent Templates
```sql
SELECT name, description 
FROM agent_orchestra_agenttemplate 
ORDER BY name;
```

### Find Recent Conversations
```sql
SELECT chunk_text, importance_score, conversation_timestamp 
FROM ai_partner_conversationembedding 
ORDER BY conversation_timestamp DESC 
LIMIT 10;
```

### Check Vector Tables
```sql
SELECT table_name, column_name 
FROM information_schema.columns 
WHERE udt_name = 'vector';
```

## Critical Issues

1. **No Vector Indexes** - Similarity search using sequential scans
2. **Missing Agent Results** - 44 agents run but no results stored
3. **Empty BI Tables** - Legislative, government contract tables unused
4. **Legacy Memory** - 9 entries still in old system

## Quick Fixes Needed

```sql
-- Add vector index for similarity search
CREATE INDEX idx_unified_memory_embedding 
ON unified_memory_entries 
USING hnsw (embedding vector_cosine_ops);

-- Check entries without embeddings
SELECT id, content_type, created_at 
FROM unified_memory_entries 
WHERE embedding IS NULL;
```

## Memory System Overview

```
┌─────────────────────────┐
│   Unified Memory (123)  │ ← Primary System
└──────────┬──────────────┘
           │
    ┌──────┴───────┬─────────────┬──────────────┐
    │              │             │              │
┌───▼────┐  ┌─────▼──────┐  ┌──▼───┐  ┌───────▼────────┐
│Conv(102)│  │Learning(16)│  │Mem(3)│  │Other(2)        │
└─────────┘  └────────────┘  └──────┘  └────────────────┘

Separate Systems:
- Conversation Embeddings (85)
- Legacy Memory (9)
- Learning Anchors (8)
```

## Agent Distribution

**Top Agent Types:**
- Business & Financial (8 agents)
- Content & Communication (6 agents)
- Research & Analysis (5 agents)
- Technical & Development (4 agents)
- Market & Trading (4 agents)
- Other Specialized (7 agents)

---

*Quick reference for PostgreSQL and PGVector database - Last updated: August 10, 2025*