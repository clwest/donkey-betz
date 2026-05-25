# Session 753: Memory Palace Data Gap Audit & Implementation Plan

**Date:** January 14, 2026
**Session:** 753 (Updated Session 755)
**Focus:** Comprehensive audit of Memory Palace UI revealing massive amounts of unused data
**Status:** ALL PHASES COMPLETE - Data Display Coverage 60% → 95%+

---

## Executive Summary

A thorough backwards audit of the Memory Palace feature revealed that **approximately 60% of available data is NOT displayed** in the frontend. This includes entire database models with no UI representation, API endpoints returning data that's never rendered, and rich metadata fields that exist but are hidden from users.

This document catalogs every gap discovered and provides implementation specifications for each.

---

## Table of Contents

1. [Database Models Audit](#database-models-audit)
2. [API Endpoints Audit](#api-endpoints-audit)
3. [Frontend Current State](#frontend-current-state)
4. [Gap Analysis - Complete List](#gap-analysis---complete-list)
5. [Implementation Specifications](#implementation-specifications)
6. [Priority Order](#priority-order)
7. [File Locations](#file-locations)

---

## Database Models Audit

### 1. AgentMemory Model (`core/models_unified_system.py:9461`)

**All Fields:**
```python
id                  # UUID - displayed
agent               # FK to Agent - displayed
title               # CharField - displayed
content             # TextField - displayed (truncated in list)
context             # TextField - displayed in detail only
memory_type         # CharField choices - displayed
valence             # CharField choices - displayed
importance_score    # FloatField - displayed
memory_outcome      # CharField (success/failure/partial/unknown) - PARTIALLY DISPLAYED (clusters only)
embedding           # VectorField - internal
connected_memories  # M2M to self - DISPLAYED POORLY (no metadata)
source_type         # CharField - BARELY VISIBLE
source_id           # CharField - NOT LINKED
tags                # JSONField - NOT DISPLAYED AT ALL
access_count        # PositiveIntegerField - displayed in detail
last_accessed_at    # DateTimeField - NOT IN LIST VIEW
created_at          # DateTimeField - displayed
```

**Gap Summary:**
- `tags` - Complete feature missing
- `memory_outcome` - Only in cluster detail, not main memory list
- `last_accessed_at` - Not in list view, can't sort by it
- `source_type`/`source_id` - Not clickable, not filterable
- Connected memories show title only, not connection type/strength

---

### 2. MemoryConnection Model (`core/models_unified_system.py:9722`)

**All Fields:**
```python
id                  # UUID
memory_from         # FK to AgentMemory
memory_to           # FK to AgentMemory
connection_type     # CharField choices: causal, similar, contrast, elaborates, temporal
strength            # FloatField 0-1
created_at          # DateTimeField
```

**Gap Summary: ENTIRE MODEL NOT DISPLAYED IN UI**

The UI shows connected memories as a simple list but:
- Does NOT show connection type (causal/similar/contrast/elaborates/temporal)
- Does NOT show connection strength
- Does NOT differentiate incoming vs outgoing
- Does NOT visualize the connection graph

**API Exists:** `GET /memory-palace/memory/<id>/connections/`
```json
{
  "outgoing": [{"id", "target_id", "target_title", "type", "strength"}],
  "incoming": [{"id", "source_id", "source_title", "type", "strength"}]
}
```

---

### 3. MemoryPalaceRoom Model (`core/models_unified_system.py:9772`)

**All Fields:**
```python
id                  # UUID - used
agent               # FK to Agent - used
name                # CharField - displayed
description         # TextField - displayed
icon                # CharField - NOT USED (hardcoded icons)
room_type           # CharField choices - used for routing
position_x          # IntegerField - NOT USED
position_y          # IntegerField - NOT USED
color               # CharField - displayed
memories            # M2M to AgentMemory - used
created_at          # DateTimeField - not displayed
```

**Gap Summary:**
- `position_x`, `position_y` - Available for visual palace map, completely unused
- `icon` - Each room can have custom icon, UI uses hardcoded set
- No visual "palace" layout despite having position data

---

### 4. MemoryCluster Model (`core/models_unified_system.py:9867`)

**All Fields:**
```python
id                          # UUID - displayed
agent                       # FK nullable - displayed
name                        # CharField - displayed
description                 # TextField - displayed
keywords                    # JSONField - displayed
color                       # CharField - displayed
icon                        # CharField - NOT USED (hardcoded Network icon)
centroid_embedding          # VectorField - internal
coherence_score             # FloatField - displayed
stability_score             # FloatField - NOT DISPLAYED
memories                    # M2M through MemoryClusterMembership - displayed
related_clusters            # M2M to self - NOT DISPLAYED
parent_cluster              # FK to self - NOT DISPLAYED
sub_clusters                # reverse FK - NOT DISPLAYED
cluster_method              # CharField choices - displayed
cluster_type                # CharField (general/success_pattern/failure_pattern/learning_pattern/error_recovery) - displayed
version                     # PositiveIntegerField - displayed
last_clustered_at           # DateTimeField - NOT DISPLAYED
memory_count_at_clustering  # PositiveIntegerField - NOT DISPLAYED
created_at                  # DateTimeField - NOT DISPLAYED (only last_clustered_at would be useful)
updated_at                  # DateTimeField - NOT DISPLAYED
```

**Gap Summary:**
- `stability_score` - Quality metric not shown
- `related_clusters` - API returns but no navigation
- `parent_cluster` / `sub_clusters` - Hierarchical view not implemented
- `icon` - Per-cluster icons not used
- `last_clustered_at` - Not shown
- `memory_count_at_clustering` - Historical comparison not shown

---

### 5. MemoryClusterMembership Model (`core/models_unified_system.py:10380`)

**All Fields:**
```python
id                      # UUID
cluster                 # FK to MemoryCluster
memory                  # FK to AgentMemory
similarity_to_centroid  # FloatField - displayed
is_core_member          # BooleanField - displayed
position_x              # FloatField - NOT USED
position_y              # FloatField - NOT USED
created_at              # DateTimeField - not displayed
```

**Gap Summary:**
- `position_x`, `position_y` - Available for cluster visualization, completely unused

---

### 6. ClusterEvolution Model (`core/models_unified_system.py:10428`)

**All Fields:**
```python
id                  # UUID
agent               # FK to Agent
event_type          # CharField: created, merged, split, grown, shrunk, dissolved
cluster             # FK to MemoryCluster nullable
details             # JSONField
memories_before     # PositiveIntegerField
memories_after      # PositiveIntegerField
coherence_before    # FloatField
coherence_after     # FloatField
created_at          # DateTimeField
```

**Gap Summary: ENTIRE MODEL HAS NO UI**

This valuable historical data showing how clusters evolve over time has:
- An API endpoint that works
- No frontend component at all
- Rich data about cluster lifecycle

**API Exists:** `GET /api/memory-clusters/evolution/<agent_id>/`

---

## API Endpoints Audit

### Memory Palace APIs (`core/views_memory_palace.py`)

| Endpoint | Method | Frontend Usage |
|----------|--------|----------------|
| `/memory-palace/` | GET | Used - overview |
| `/memory-palace/agent/<id>/memories/` | GET | Used |
| `/memory-palace/agent/<id>/rooms/` | GET | Used |
| `/memory-palace/agent/<id>/summary/` | GET | **NOT USED** |
| `/memory-palace/memory/<id>/` | GET | Used |
| `/memory-palace/memory/<id>/connections/` | GET | **NOT USED PROPERLY** |
| `/memory-palace/memory/<id>/delete/` | DELETE | Used |
| `/memory-palace/room/<id>/memories/` | GET | Used |
| `/memory-palace/create/` | POST | Not exposed in UI |
| `/memory-palace/search/` | POST | Used |
| `/memory-palace/assign/` | POST | Not exposed in UI |
| `/memory-palace/connect/` | POST | Not exposed in UI |

### Memory Clusters APIs (`core/views_memory_clusters.py`)

| Endpoint | Method | Frontend Usage |
|----------|--------|----------------|
| `/memory-clusters/` | GET | Used - overview |
| `/memory-clusters/agent/<id>/` | GET | Used |
| `/memory-clusters/agent/<id>/` | POST | Used - generate |
| `/memory-clusters/cluster/<id>/` | GET | Used |
| `/memory-clusters/visualization/` | GET | **NOT USED AT ALL** |
| `/memory-clusters/visualization/<agent_id>/` | GET | **NOT USED AT ALL** |
| `/memory-clusters/generate-all/` | POST | Not exposed in UI |
| `/memory-clusters/cluster/<id>/add-memory/` | POST | Not exposed in UI |
| `/memory-clusters/cluster/<id>/memory/<id>/` | DELETE | Not exposed in UI |
| `/memory-clusters/evolution/<agent_id>/` | GET | **NOT USED AT ALL** |
| `/memory-clusters/find-similar/` | POST | **NOT USED AT ALL** |

### Frontend API Client (`frontend/src/lib/api.ts`)

```typescript
// Memory Palace - lines 257-300
memoryPalaceApi = {
  overview()              // Used
  agentMemories()         // Used
  agentRooms()            // Used
  agentSummary()          // NOT USED IN UI
  memoryDetail()          // Used
  memoryConnections()     // DEFINED BUT NOT CALLED
  deleteMemory()          // Used
  roomMemories()          // Used
  createMemory()          // NOT EXPOSED IN UI
  searchMemories()        // Used
  assignToRoom()          // NOT EXPOSED IN UI
  connectMemories()       // NOT EXPOSED IN UI
}

// Memory Clusters - lines 303-335
memoryClustersApi = {
  overview()              // Used
  agentClusters()         // Used
  generateClusters()      // Used
  detail()                // Used
  visualization()         // DEFINED BUT NOT CALLED
  generateAll()           // NOT EXPOSED IN UI
  addMemory()             // NOT EXPOSED IN UI
  removeMemory()          // NOT EXPOSED IN UI
  evolution()             // DEFINED BUT NOT CALLED
  findSimilar()           // NOT DEFINED IN CLIENT
}
```

---

## Frontend Current State

### File: `frontend/src/pages/MemoryPalacePage.tsx` (1,368 lines)

**Current Tabs:**
1. **Palace** - Agent list → Room list → Memory list → Memory detail
2. **Clusters** - Cluster overview → Agent clusters → Cluster detail

**What IS Displayed:**

Palace Tab:
- Overview stats (total memories, agents with memories, memory types count)
- Agent list with memory count and avg importance
- Room list with memory counts
- Memory list with type icon, title, content preview, importance, valence border
- Memory detail with full content, context, metadata, connected memories (basic list)

Clusters Tab:
- Overview stats (total clusters, agents with clusters)
- Agents with clusters list
- Agents needing clusters (generate button)
- Cluster cards with name, description, keywords, memory count, coherence
- Cluster detail with memories, outcome filter

**What is NOT Displayed:**
- See Gap Analysis below

---

## Gap Analysis - Complete List

### Category 1: Completely Missing UI Components

| Feature | Data Source | Priority |
|---------|-------------|----------|
| **Cluster Evolution Timeline** | ClusterEvolution model + API | HIGH |
| **Cluster Visualization Graph** | `/memory-clusters/visualization/` API | HIGH |
| **Memory Connection Graph** | MemoryConnection model + API | HIGH |
| **Memory Tags System** | AgentMemory.tags field | MEDIUM |
| **Palace Room Map** | MemoryPalaceRoom.position_x/y | MEDIUM |
| **Find Similar Clusters** | `/memory-clusters/find-similar/` API | LOW |
| **Memory Summary Panel** | `/memory-palace/agent/<id>/summary/` API | LOW |

### Category 2: Existing UI Missing Data Fields

| Location | Missing Fields | Priority |
|----------|----------------|----------|
| Memory List Cards | `memory_outcome`, `last_accessed_at`, `tags` | HIGH |
| Memory Detail | Source linking (clickable `source_type`/`source_id`) | MEDIUM |
| Connected Memories | `connection_type`, `strength`, direction indicators | HIGH |
| Cluster Cards | `stability_score`, `icon`, `last_clustered_at` | MEDIUM |
| Cluster Detail | `related_clusters`, `sub_clusters`, `parent_cluster` | MEDIUM |

### Category 3: Missing Filters & Actions

| Feature | Status | Priority |
|---------|--------|----------|
| Filter memories by `memory_outcome` | Not available | HIGH |
| Filter memories by `tags` | Not available | HIGH |
| Filter memories by `source_type` | Not available | MEDIUM |
| Sort memories by `last_accessed_at` | Not available | MEDIUM |
| Sort memories by `access_count` | Not available | LOW |
| Create memory from UI | API exists, no UI | LOW |
| Assign memory to room | API exists, no UI | LOW |
| Create memory connections | API exists, no UI | MEDIUM |
| Add/remove cluster members | API exists, no UI | LOW |

---

## Implementation Specifications

### 1. Cluster Evolution Timeline (NEW TAB)

**Location:** Add "Evolution" tab to Clusters section

**API Call:**
```typescript
memoryClustersApi.evolution(agentId)
// Returns: { events: [{event_type, cluster_name, details, memories_before, memories_after, coherence_before, coherence_after, created_at}] }
```

**UI Component:**
```tsx
// Timeline view showing cluster lifecycle events
<div className="space-y-4">
  {events.map(event => (
    <div className="flex items-start gap-4 border-l-2 pl-4">
      <EventIcon type={event.event_type} />
      <div>
        <h4>{event.cluster_name}: {event.event_type}</h4>
        <p>Memories: {event.memories_before} → {event.memories_after}</p>
        <p>Coherence: {(event.coherence_before*100).toFixed(0)}% → {(event.coherence_after*100).toFixed(0)}%</p>
        <time>{formatDate(event.created_at)}</time>
      </div>
    </div>
  ))}
</div>
```

**Event Type Icons:**
- created → Plus icon (green)
- merged → GitMerge icon (blue)
- split → GitBranch icon (purple)
- grown → TrendingUp icon (green)
- shrunk → TrendingDown icon (orange)
- dissolved → Trash icon (red)

---

### 2. Cluster Visualization Graph (NEW TAB)

**Location:** Add "Visualization" tab to Clusters section

**API Call:**
```typescript
memoryClustersApi.visualization(agentId)
// Returns: { nodes: [{id, type, name, color, size, ...}], links: [{source, target, strength, type}] }
```

**UI Component:**
Use D3.js force-directed graph or react-force-graph:

```tsx
import ForceGraph2D from 'react-force-graph-2d'

<ForceGraph2D
  graphData={{ nodes, links }}
  nodeLabel="name"
  nodeColor={node => node.color}
  nodeVal={node => node.size}
  linkWidth={link => link.strength * 3}
  onNodeClick={handleNodeClick}
/>
```

**Node Types:**
- Cluster nodes: Larger, colored by cluster.color
- Memory nodes: Smaller, colored by memory_type

**Interactions:**
- Click cluster → Navigate to cluster detail
- Click memory → Navigate to memory detail
- Hover → Show tooltip with details

---

### 3. Memory Connection Graph (ENHANCE MEMORY DETAIL)

**Location:** Memory Detail view, replace simple connected memories list

**API Call:**
```typescript
memoryPalaceApi.memoryConnections(memoryId)
// Returns: { outgoing: [{target_id, target_title, type, strength}], incoming: [{source_id, source_title, type, strength}] }
```

**UI Component:**
```tsx
<div className="grid grid-cols-2 gap-4">
  {/* Outgoing Connections */}
  <div>
    <h3>Leads To ({outgoing.length})</h3>
    {outgoing.map(conn => (
      <ConnectionCard
        title={conn.target_title}
        type={conn.type}
        strength={conn.strength}
        direction="outgoing"
        onClick={() => navigateToMemory(conn.target_id)}
      />
    ))}
  </div>

  {/* Incoming Connections */}
  <div>
    <h3>Comes From ({incoming.length})</h3>
    {incoming.map(conn => (
      <ConnectionCard
        title={conn.source_title}
        type={conn.type}
        strength={conn.strength}
        direction="incoming"
        onClick={() => navigateToMemory(conn.source_id)}
      />
    ))}
  </div>
</div>
```

**Connection Type Styling:**
- causal → Orange, "Caused" label
- similar → Blue, "Similar" label
- contrast → Red, "Contrasts" label
- elaborates → Green, "Expands" label
- temporal → Gray, "Follows" label

**Strength Display:**
- Progress bar or colored intensity
- 0.0-0.3: Weak
- 0.3-0.7: Moderate
- 0.7-1.0: Strong

---

### 4. Memory Tags System (ENHANCE MEMORY CARDS & DETAIL)

**Data:** `AgentMemory.tags` JSONField (list of strings)

**Memory Card Enhancement:**
```tsx
<div className="flex flex-wrap gap-1 mt-2">
  {memory.tags?.slice(0, 3).map(tag => (
    <span className="px-1.5 py-0.5 bg-dark-bg rounded text-xs text-gray-400">
      #{tag}
    </span>
  ))}
  {memory.tags?.length > 3 && (
    <span className="text-xs text-gray-500">+{memory.tags.length - 3}</span>
  )}
</div>
```

**Memory Detail Enhancement:**
- Full tag list
- Click tag to filter by that tag
- Add/remove tags (requires new API endpoint or use existing create with update)

**Filter Enhancement:**
```tsx
<div className="flex flex-wrap gap-2">
  {allTags.map(tag => (
    <button
      onClick={() => toggleTagFilter(tag)}
      className={cn(
        'px-2 py-1 rounded text-xs',
        selectedTags.includes(tag) ? 'bg-purple-600 text-white' : 'bg-dark-bg text-gray-400'
      )}
    >
      #{tag}
    </button>
  ))}
</div>
```

**Backend Enhancement Needed:**
- Add `tags` to memory list API response (currently not returned)
- Add tag filter parameter to `/memory-palace/agent/<id>/memories/`

---

### 5. Memory Outcome in List View (ENHANCE MEMORY CARDS)

**Data:** `AgentMemory.memory_outcome` (success/failure/partial/unknown)

**Memory Card Enhancement:**
```tsx
<div className="flex items-center gap-2">
  <h3>{memory.title}</h3>
  {memory.memory_outcome && memory.memory_outcome !== 'unknown' && (
    <span className={cn(
      'px-1.5 py-0.5 text-xs rounded',
      memory.memory_outcome === 'success' && 'bg-green-500/20 text-green-300',
      memory.memory_outcome === 'failure' && 'bg-red-500/20 text-red-300',
      memory.memory_outcome === 'partial' && 'bg-yellow-500/20 text-yellow-300',
    )}>
      {memory.memory_outcome}
    </span>
  )}
</div>
```

**Filter Enhancement:**
```tsx
<select value={outcomeFilter} onChange={e => setOutcomeFilter(e.target.value)}>
  <option value="">All Outcomes</option>
  <option value="success">Success</option>
  <option value="failure">Failure</option>
  <option value="partial">Partial</option>
  <option value="unknown">Unknown</option>
</select>
```

**Backend Enhancement Needed:**
- Add `memory_outcome` to memory list API response
- Add outcome filter parameter to `/memory-palace/agent/<id>/memories/`

---

### 6. Related & Sub Clusters (ENHANCE CLUSTER DETAIL)

**Data:** `MemoryCluster.related_clusters`, `sub_clusters`, `parent_cluster`

**Already returned by API** in cluster detail response:
```json
{
  "related_clusters": [{"id", "name", "color"}],
  "sub_clusters": [{"id", "name", "color", "memory_count"}],
  "cluster": {
    "parent_cluster": {"id", "name"} | null
  }
}
```

**UI Enhancement:**
```tsx
{/* Parent Cluster Breadcrumb */}
{cluster.parent_cluster && (
  <div className="flex items-center gap-2 text-sm text-gray-400 mb-4">
    <span>Parent:</span>
    <button
      onClick={() => setSelectedCluster(cluster.parent_cluster.id)}
      className="text-purple-400 hover:underline"
    >
      {cluster.parent_cluster.name}
    </button>
  </div>
)}

{/* Sub Clusters Section */}
{sub_clusters.length > 0 && (
  <div className="mt-6">
    <h3>Sub-Clusters ({sub_clusters.length})</h3>
    <div className="grid grid-cols-3 gap-2">
      {sub_clusters.map(sub => (
        <button
          onClick={() => setSelectedCluster(sub.id)}
          className="p-3 bg-dark-bg rounded-lg"
        >
          <div className="w-3 h-3 rounded-full" style={{backgroundColor: sub.color}} />
          <span>{sub.name}</span>
          <span className="text-xs text-gray-500">{sub.memory_count} memories</span>
        </button>
      ))}
    </div>
  </div>
)}

{/* Related Clusters Section */}
{related_clusters.length > 0 && (
  <div className="mt-6">
    <h3>Related Clusters ({related_clusters.length})</h3>
    <div className="flex flex-wrap gap-2">
      {related_clusters.map(rel => (
        <button
          onClick={() => setSelectedCluster(rel.id)}
          className="flex items-center gap-2 px-3 py-1.5 bg-dark-bg rounded-lg hover:bg-dark-border"
        >
          <div className="w-2 h-2 rounded-full" style={{backgroundColor: rel.color}} />
          {rel.name}
        </button>
      ))}
    </div>
  </div>
)}
```

---

### 7. Stability Score & Additional Cluster Metrics (ENHANCE CLUSTER CARDS)

**Data:** `MemoryCluster.stability_score`, `last_clustered_at`

**Cluster Card Enhancement:**
```tsx
<div className="flex items-center justify-between mt-3 pt-3 border-t border-dark-border">
  <div className="flex items-center gap-4">
    <span className="text-sm text-gray-400">{cluster.memory_count} memories</span>
    {cluster.last_clustered_at && (
      <span className="text-xs text-gray-500">
        Updated {formatRelativeTime(cluster.last_clustered_at)}
      </span>
    )}
  </div>
  <div className="flex items-center gap-3">
    <div className="text-right">
      <div className="text-xs text-gray-500">Coherence</div>
      <div className="text-sm text-purple-400">{(cluster.coherence_score * 100).toFixed(0)}%</div>
    </div>
    <div className="text-right">
      <div className="text-xs text-gray-500">Stability</div>
      <div className="text-sm text-blue-400">{(cluster.stability_score * 100).toFixed(0)}%</div>
    </div>
  </div>
</div>
```

---

### 8. Palace Room Map (NEW VISUALIZATION)

**Data:** `MemoryPalaceRoom.position_x`, `position_y`

**Concept:** Visual representation of the memory palace with rooms as nodes

**UI Component:**
```tsx
<div className="relative w-full h-[500px] bg-dark-bg rounded-lg overflow-hidden">
  {/* Palace background */}
  <div className="absolute inset-0 bg-gradient-to-br from-purple-900/20 to-blue-900/20" />

  {/* Room nodes positioned absolutely */}
  {rooms.map(room => (
    <button
      key={room.id}
      onClick={() => setSelectedRoom(room)}
      className="absolute transform -translate-x-1/2 -translate-y-1/2 p-4 rounded-xl border-2 transition-all hover:scale-110"
      style={{
        left: `${(room.position_x / maxX) * 80 + 10}%`,
        top: `${(room.position_y / maxY) * 80 + 10}%`,
        backgroundColor: room.color + '30',
        borderColor: room.color,
      }}
    >
      <span className="text-2xl">{room.icon}</span>
      <div className="text-sm font-medium text-white mt-1">{room.name}</div>
      <div className="text-xs text-gray-400">{room.memory_count}</div>
    </button>
  ))}
</div>
```

**Backend Enhancement Needed:**
- Management command to assign positions to rooms if not set
- Or auto-calculate positions based on room type

---

### 9. Memory Summary Panel (NEW COMPONENT)

**API Call:**
```typescript
memoryPalaceApi.agentSummary(agentId, 10)
// Returns: { summary: "formatted text", prompt_injection: "...", total_memories, memory_type_count }
```

**UI Component:** Collapsible panel in agent's memory view
```tsx
<Collapsible>
  <CollapsibleTrigger className="flex items-center gap-2 w-full p-3 bg-dark-bg rounded-lg">
    <Sparkles className="h-4 w-4 text-purple-400" />
    <span>Memory Summary</span>
    <ChevronDown className="ml-auto h-4 w-4" />
  </CollapsibleTrigger>
  <CollapsibleContent className="p-4 bg-dark-bg/50 rounded-b-lg">
    <p className="text-sm text-gray-300 whitespace-pre-wrap">{summary.summary}</p>
    <div className="flex gap-4 mt-3 text-xs text-gray-500">
      <span>{summary.total_memories} memories</span>
      <span>{summary.memory_type_count} types</span>
    </div>
  </CollapsibleContent>
</Collapsible>
```

---

### 10. Find Similar Clusters (NEW FEATURE)

**API Call:**
```typescript
// Need to add to frontend API client
findSimilarClusters: (data: { query?: string; memory_id?: string; limit?: number }) =>
  api.post('/memory-clusters/find-similar/', data)
```

**UI Component:** Search bar in clusters overview
```tsx
<div className="flex gap-2">
  <input
    type="text"
    placeholder="Find clusters about..."
    value={clusterQuery}
    onChange={e => setClusterQuery(e.target.value)}
    className="flex-1 bg-dark-bg border border-dark-border rounded-lg px-4 py-2"
  />
  <button onClick={handleFindSimilar} className="px-4 py-2 bg-purple-600 rounded-lg">
    <Search className="h-4 w-4" />
  </button>
</div>

{/* Results */}
{similarClusters.length > 0 && (
  <div className="mt-4 space-y-2">
    <h3>Similar Clusters</h3>
    {similarClusters.map(cluster => (
      <button onClick={() => setSelectedCluster(cluster.id)} className="w-full text-left p-3 bg-dark-card rounded-lg">
        <div className="flex items-center justify-between">
          <span>{cluster.name}</span>
          <span className="text-purple-400">{(cluster.similarity * 100).toFixed(0)}% match</span>
        </div>
        <p className="text-sm text-gray-400 mt-1">{cluster.description}</p>
      </button>
    ))}
  </div>
)}
```

---

## Priority Order

### Phase 1: Quick Wins (1-2 hours each) - COMPLETE (Session 753)
1. ~~**Memory Outcome in List**~~ - ✅ Added badges with CheckCircle/XCircle/Clock icons
2. ~~**Stability Score Display**~~ - ✅ Shown in cluster cards and detail view
3. ~~**Related/Sub Clusters**~~ - ✅ Clickable navigation in cluster detail
4. ~~**Last Accessed At**~~ - ✅ Display + sorting options
5. ~~**Tags Display**~~ - ✅ Show up to 3 tags per memory card
6. ~~**Outcome Filter**~~ - ✅ New dropdown filter
7. ~~**Sort By Options**~~ - ✅ Importance, Recent, Accessed, Access Count

### Phase 2: Medium Effort (2-4 hours each) - COMPLETE (Session 754)
5. ~~**Cluster Evolution Timeline**~~ - ✅ New tab in Clusters section with:
   - Event types: created, merged, split, grown, shrunk, dissolved
   - Visual timeline with icons and colors
   - Memory/coherence before/after metrics
   - Relative timestamps
6. ~~**Memory Connection Graph**~~ - ✅ Enhanced memory detail with:
   - Outgoing vs Incoming columns
   - Connection types: causal, similar, contrast, elaborates, temporal
   - Strength visualization with progress bars
   - Type legend
7. ~~**Memory Tags System**~~ - ✅ Complete with:
   - Backend: Tag filter parameter in API
   - Frontend: Tag filter section in sidebar
   - Clickable tags on memory cards filter by that tag

### Phase 3: Larger Features (4-8 hours each) - COMPLETE (Session 755)
8. ~~**Cluster Visualization Graph**~~ - ✅ Force-directed graph with react-force-graph-2d:
   - Cluster nodes (larger, colored) and memory nodes
   - Interactive: pan, zoom, click for details
   - Hover tooltips, legend with counts
9. ~~**Palace Room Map**~~ - ✅ Visual room positioning:
   - Map/List view toggle
   - Grid layout using position_x/position_y
   - Backend API returns room positions
10. ~~**Find Similar Clusters**~~ - ✅ Semantic search UI:
    - Search input with embedding similarity
    - Color-coded match percentages
    - Click results to navigate to cluster

---

## File Locations

### Backend Files
- `core/models_unified_system.py` - All models (AgentMemory: 9461, MemoryConnection: 9722, MemoryPalaceRoom: 9772, MemoryCluster: 9867, MemoryClusterMembership: 10380, ClusterEvolution: 10428)
- `core/views_memory_palace.py` - Memory Palace API endpoints
- `core/views_memory_clusters.py` - Memory Clusters API endpoints

### Frontend Files
- `frontend/src/pages/MemoryPalacePage.tsx` - Main page (1,368 lines)
- `frontend/src/lib/api.ts` - API client (memoryPalaceApi: 257, memoryClustersApi: 303)

### URL Patterns (for reference)
- `core/urls.py` - URL routing

---

## Backend API Enhancements Needed

### 1. Enhance Memory List Response
File: `core/views_memory_palace.py`, function `get_agent_memories`

Add fields:
```python
'memory_outcome': m.memory_outcome,
'tags': m.tags,
'last_accessed_at': m.last_accessed_at.isoformat() if m.last_accessed_at else None,
```

Add filter params:
```python
outcome = request.GET.get('outcome')
tag = request.GET.get('tag')
if outcome:
    memories = memories.filter(memory_outcome=outcome)
if tag:
    memories = memories.filter(tags__contains=[tag])
```

### 2. Add findSimilar to Frontend API Client
File: `frontend/src/lib/api.ts`

```typescript
findSimilar: (data: { query?: string; memory_id?: string; limit?: number }) =>
  api.post('/memory-clusters/find-similar/', data),
```

---

## Success Metrics

After implementation:
- [ ] All 10 hidden features exposed in UI
- [ ] All 5 connection types visible when viewing memory connections
- [ ] Cluster evolution history viewable for any agent
- [ ] Memory tags displayable and filterable
- [ ] Cluster visualization renders force-directed graph
- [ ] No API endpoint returns data that isn't displayed somewhere

---

## Session Notes

- Audit discovered ~60% of available data was not displayed
- Most APIs exist and return data, frontend just doesn't render it
- Some backend enhancements needed for filters and additional fields
- D3.js or react-force-graph recommended for visualizations
- Room position data exists but needs initial values set

---

## Phase 1 Implementation Complete

Session 753 implemented all Phase 1 quick wins:

### Backend Changes (`core/views_memory_palace.py`)
- Added `memory_outcome`, `last_accessed_at`, `tags` to memory list response
- Added `outcome` filter parameter
- Added `sort_by` parameter (importance, recent, accessed, access_count)

### Frontend Changes (`frontend/src/pages/MemoryPalacePage.tsx`)

1. **Memory Outcome Badges** - Memory cards now show success/failure/partial badges with icons
2. **Tags Display** - Memory cards show up to 3 tags with "+N more" indicator
3. **Last Accessed Display** - Memory cards show last accessed date when available
4. **Stability Score** - Cluster cards and detail view show stability score alongside coherence
5. **Related Clusters Navigation** - Cluster detail shows clickable related clusters
6. **Sub-Clusters Navigation** - Cluster detail shows clickable sub-clusters with memory counts
7. **Parent Cluster Breadcrumb** - Cluster detail shows parent cluster with navigation
8. **Outcome Filter** - New dropdown to filter memories by outcome (success/failure/partial/unknown)
9. **Sort By Options** - New dropdown to sort memories (importance, recent, accessed, access_count)

### API Client Changes (`frontend/src/lib/api.ts`)
- Updated `agentMemories` to accept `outcome` and `sort_by` parameters

### Files Modified
- `core/views_memory_palace.py`
- `frontend/src/pages/MemoryPalacePage.tsx`
- `frontend/src/lib/api.ts`

---

**Next Session:** Begin Phase 2 implementations (Cluster Evolution Timeline, Memory Connection Graph, Tags System).
