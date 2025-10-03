# Memory Palace + Research Intelligence Integration Plan

## Overview
Connect Memory Palace's knowledge management with Research Intelligence's data discovery capabilities.

## Integration Opportunities

### 1. Save Research Results to Memory Palace
**What**: Add "Save to Memory" button on research results
**How**:
- Add endpoint: `POST /api/memory/palace/save-research/`
- Save research results as MemoryEntry with metadata
- Tag with search query and source type
- Link related research results

### 2. Search Memory Palace from Research Intelligence
**What**: Include Memory Palace results in research searches
**How**:
- Modify Research Intelligence to query Memory Palace API
- Display personal memories alongside public data
- Show "From Your Memory" badge on results

### 3. Auto-Document Research Sessions
**What**: Automatically save research sessions as memories
**How**:
- Track research queries and viewed results
- Create ConversationMemory entries for research sessions
- Build knowledge graph of research topics

### 4. Enhanced Document Processing
**What**: Research documents auto-added to Memory Palace
**How**:
- SEC filings, news articles → Memory Palace documents
- Auto-extract key insights and entities
- Cross-reference with existing memories

### 5. Unified Search Interface
**What**: Single search bar for both systems
**How**:
- Combine Memory Palace semantic search with Research Intelligence
- Unified results with clear source indicators
- Relevance scoring across both systems

## Implementation Priority

### Phase 1: Save Research to Memory (Quick Win)
1. Add save button to ResultsGrid.tsx
2. Create save-research endpoint
3. Show success notification

### Phase 2: Unified Search
1. Modify Research Intelligence search to include Memory API
2. Update results display to show memory results
3. Add filtering for memory vs public data

### Phase 3: Auto-Documentation
1. Add research session tracking
2. Background job to process sessions
3. Auto-generate insights

## Key Files to Modify

### Backend:
- `/backend/memory/views_memory_palace.py` - Add save-research endpoint
- `/backend/agent_orchestra/services/research_intelligence_service.py` - Include memory search

### Frontend:
- `/donkey-betz-frontend/src/features/research-intelligence/components/ResultsGrid.tsx` - Add save button
- `/donkey-betz-frontend/src/features/research-intelligence/hooks/useResearchIntelligence.ts` - Include memory results
- Create new `useMemoryIntegration.ts` hook

## Benefits
1. **Personal Knowledge Base**: Research becomes part of your memory
2. **Context Awareness**: Future searches know what you've researched
3. **Knowledge Building**: Connect research with personal insights
4. **Time Travel**: "What was that article I found last month?"
5. **Cross-Pollination**: Memory Palace insights enhance research