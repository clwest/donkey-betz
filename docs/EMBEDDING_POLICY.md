# Embedding Policy

## Scope
We maintain vector embeddings to power semantic search and “find similar” recommendations across:
- **Jobs & Applications** (personalization)
- **Internal Docs (RAG)**

## Models
- **User/Job personalization**: `text-embedding-3-small` (1536-d)  
- **Docs/RAG (local)**: `all-MiniLM-L6-v2` (384-d)

> Embedding models may be upgraded with equivalent or higher-quality replacements. Dimensions will be reflected in DB schema.

## Storage
- **Database**: PostgreSQL with **pgvector**
- **Schema**: `vector(1536)` for `UserEmbedding.embedding_vector`
- **Similarity**: Cosine distance (`<->`) for ANN search
- **Namespaces**: Separate collections per domain (jobs, docs, memory)

## Creation & Updates
- **Trigger**: On **successful job outcomes** (`offer_received` or `offer_accepted`) inside `JobApplication.update_status()`
- **What we embed**: Key non-sensitive text features (role title, seniority, skills, company attributes)
- **Refresh**: Recomputed on subsequent successes; optional nightly maintenance job if profile changes materially

## Recommendation Flow
1. Create/refresh `UserEmbedding` on success event
2. Query top-N similar jobs via cosine similarity
3. Re-rank with contextual signals (recency, platform fit) before display

## Cold Start
If no success embeddings exist, fall back to:
- Profile-derived keywords (skills, desired roles)
- Global trending/high-quality opportunities

## Privacy & Retention
- Embed **non-PII** features only; vectors are non-reversible
- Retention follows account data lifecycle and deletion requests