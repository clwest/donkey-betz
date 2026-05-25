# Session 399: Spider Data UI Implementation Plan

**Date:** December 8, 2025
**Goal:** Surface all spider-collected data and agent learnings in a beautiful, real-time UI
**Estimated Time:** 2-3 hours
**Option Selected:** Option C (Full Implementation)

---

## Executive Summary

The platform has been collecting rich data from 57 working spiders across 25+ categories, but this data is largely hidden in JSON blobs. This session will create a comprehensive data visualization layer that surfaces:

- 7,143 spider data records with actual article content
- 865 knowledge sources derived from spider data
- 168 knowledge transfers between agents
- Real-time updates as spiders crawl

---

## Current State Analysis

### Data Available (Not Displayed)

| Model | Records | Key Fields | Current Visibility |
|-------|---------|------------|-------------------|
| SpiderData | 7,143 | raw_data (items), embedding_text, spider_name, data_type | Only counts shown |
| AgentKnowledgeSource | 865 | title, summary, knowledge_type, confidence | Not visible |
| KnowledgeTransfer | 168 | from_agent, to_agent, transfer_summary | Not visible |
| AgentMemory | 73 | title, content, memory_type | Partially in Agents tab |

### Sample Data Structure (SpiderData.raw_data)

```python
# HackerNews spider
{
    "items": [
        {"title": "The universal weight subspace hypothesis", "score": 103, "url": "..."},
        {"title": "Kroger acknowledges robotics bet went too far", "score": 83, "url": "..."}
    ],
    "source": "hackernews",
    "fetched_at": "2025-12-08T..."
}

# CoinGecko spider
{
    "items": [
        {"symbol": "BTC", "current_price": 90038.00, "price_change_percentage_24h": -1.3},
        {"symbol": "ETH", "current_price": 3101.38, "price_change_percentage_24h": -0.5}
    ]
}

# RemoteOK spider
{
    "items": [
        {"position": "Customer Success Specialist", "company": "Modernizing Medicine",
         "salary_min": 50000, "salary_max": 70000, "tags": ["salesforce", "cloud"]}
    ]
}
```

### Existing UI Structure

```
Intelligence Tab
├── Trending (sub-tab) - Basic topic list
├── Markets (sub-tab) - Crypto prices
├── Opportunities (sub-tab) - Job listings
└── Spiders (sub-tab) - Network status
```

### Existing APIs

| Endpoint | Purpose | Status |
|----------|---------|--------|
| `/api/spider-intelligence/trends/` | Trending topics | Working |
| `/api/spider-intelligence/market/` | Crypto data | Working |
| `/api/spider-intelligence/jobs/` | Job listings | Working |
| `/api/spider-intelligence/search/` | Semantic search | Working |
| `/api/spider-intelligence/registry/` | Spider list | Working |
| `/api/spider-intelligence/test/` | Test individual spider | Working |

---

## Implementation Plan

### Phase 1: Data Feed Sub-Tab (30-40 minutes)

**Goal:** Create a browsable news feed showing actual spider data items

#### 1.1 New Template: `intel_data_feed.html`

Location: `ai_core/templates/components/panels/intelligence/intel_data_feed.html`

```html
<!-- Data Feed Sub-Tab -->
<div class="tab-pane fade" id="intel-data-feed" role="tabpanel">
    <!-- Category Pills -->
    <div class="d-flex flex-wrap gap-2 mb-4" id="feed-category-pills">
        <!-- Dynamically populated -->
    </div>

    <!-- Feed Container -->
    <div id="data-feed-container" style="max-height: 600px; overflow-y: auto;">
        <!-- Feed items rendered here -->
    </div>

    <!-- Load More -->
    <div class="text-center mt-3">
        <button class="btn btn-outline-warning" onclick="loadMoreFeedItems()">
            Load More
        </button>
    </div>
</div>
```

#### 1.2 New API Endpoint: `/api/spider-intelligence/feed/`

Location: `core/views_spider_dashboard.py`

```python
@api_view(['GET'])
def spider_data_feed(request):
    """
    Returns paginated spider data items for the data feed.

    Query params:
    - category: Filter by data_type (tech, news, financial, etc.)
    - source: Filter by spider_name
    - limit: Number of items (default 50)
    - offset: Pagination offset
    - sort: 'recent' or 'relevance'
    """
    category = request.GET.get('category', 'all')
    source = request.GET.get('source', 'all')
    limit = int(request.GET.get('limit', 50))
    offset = int(request.GET.get('offset', 0))

    queryset = SpiderData.objects.exclude(raw_data__isnull=True)

    if category != 'all':
        queryset = queryset.filter(data_type=category)
    if source != 'all':
        queryset = queryset.filter(spider_name=source)

    queryset = queryset.order_by('-created_at')[offset:offset+limit]

    items = []
    for sd in queryset:
        if sd.raw_data and 'items' in sd.raw_data:
            for item in sd.raw_data['items'][:10]:  # Max 10 items per record
                items.append({
                    'title': item.get('title') or item.get('position') or item.get('name'),
                    'url': item.get('url') or item.get('link'),
                    'source': sd.spider_name,
                    'category': sd.data_type,
                    'score': item.get('score') or item.get('points'),
                    'timestamp': sd.created_at.isoformat(),
                    'metadata': {
                        'company': item.get('company'),
                        'salary': f"${item.get('salary_min', 0):,} - ${item.get('salary_max', 0):,}" if item.get('salary_min') else None,
                        'tags': item.get('tags', []),
                        'price': item.get('current_price'),
                        'change': item.get('price_change_percentage_24h')
                    }
                })

    return JsonResponse({
        'status': 'success',
        'items': items,
        'total': len(items),
        'has_more': len(queryset) == limit
    })
```

#### 1.3 JavaScript: Feed Loading Functions

Location: `ai_core/templates/partials/js/spider_intelligence.html` (append)

```javascript
// Data Feed State
let feedState = {
    category: 'all',
    source: 'all',
    offset: 0,
    items: []
};

// Load Data Feed
async function loadDataFeed(reset = true) {
    if (reset) {
        feedState.offset = 0;
        feedState.items = [];
    }

    const container = document.getElementById('data-feed-container');
    if (reset) {
        container.innerHTML = '<p class="text-center"><span class="spinner-border spinner-border-sm"></span> Loading feed...</p>';
    }

    try {
        const params = new URLSearchParams({
            category: feedState.category,
            source: feedState.source,
            limit: 50,
            offset: feedState.offset
        });

        const response = await fetch(`/api/spider-intelligence/feed/?${params}`, {
            headers: { 'X-CSRFToken': getCsrfToken() }
        });
        const data = await response.json();

        if (data.status === 'success') {
            feedState.items = reset ? data.items : [...feedState.items, ...data.items];
            renderFeedItems(reset);
        }
    } catch (error) {
        console.error('Error loading feed:', error);
        container.innerHTML = '<p class="text-danger text-center">Failed to load feed</p>';
    }
}

// Render Feed Items
function renderFeedItems(reset) {
    const container = document.getElementById('data-feed-container');

    const html = feedState.items.map(item => `
        <div class="feed-item p-3 mb-2" style="background: rgba(255,255,255,0.03); border-radius: 8px; border-left: 3px solid ${getCategoryColor(item.category)};">
            <div class="d-flex justify-content-between align-items-start">
                <div style="flex: 1;">
                    <a href="${item.url || '#'}" target="_blank" class="text-light text-decoration-none fw-bold">
                        ${item.title || 'Untitled'}
                    </a>
                    ${item.metadata.company ? `<small class="text-muted d-block">${item.metadata.company}</small>` : ''}
                    ${item.metadata.salary ? `<small class="text-success d-block">${item.metadata.salary}</small>` : ''}
                    ${item.metadata.price ? `<small class="text-warning d-block">$${item.metadata.price.toLocaleString()} <span style="color: ${item.metadata.change >= 0 ? '#22c55e' : '#ef4444'}">(${item.metadata.change >= 0 ? '+' : ''}${item.metadata.change?.toFixed(2)}%)</span></small>` : ''}
                </div>
                <div class="text-end">
                    <span class="badge" style="background: ${getCategoryColor(item.category)}20; color: ${getCategoryColor(item.category)};">${item.source}</span>
                    ${item.score ? `<small class="text-muted d-block">${item.score} pts</small>` : ''}
                </div>
            </div>
            ${item.metadata.tags && item.metadata.tags.length > 0 ? `
                <div class="mt-2">
                    ${item.metadata.tags.slice(0, 5).map(t => `<span class="badge me-1" style="background: rgba(255,255,255,0.1); font-size: 10px;">${t}</span>`).join('')}
                </div>
            ` : ''}
        </div>
    `).join('');

    container.innerHTML = html || '<p class="text-muted text-center">No items found</p>';
}

// Category Colors
function getCategoryColor(category) {
    const colors = {
        tech: '#3b82f6',
        news: '#ec4899',
        financial: '#22c55e',
        jobs: '#f59e0b',
        creative: '#8b5cf6',
        legal: '#10b981',
        community: '#06b6d4',
        design: '#f472b6'
    };
    return colors[category] || '#6b7280';
}

// Filter by Category
function filterFeedByCategory(category) {
    feedState.category = category;
    loadDataFeed(true);

    // Update active pill
    document.querySelectorAll('#feed-category-pills .badge').forEach(el => {
        el.classList.remove('active');
        if (el.dataset.category === category) el.classList.add('active');
    });
}

// Load More
function loadMoreFeedItems() {
    feedState.offset += 50;
    loadDataFeed(false);
}
```

---

### Phase 2: Knowledge Integration Panel (30-40 minutes)

**Goal:** Show what agents have learned from spider data

#### 2.1 New Template: `intel_knowledge.html`

Location: `ai_core/templates/components/panels/intelligence/intel_knowledge.html`

```html
<!-- Knowledge Integration Sub-Tab -->
<div class="tab-pane fade" id="intel-knowledge" role="tabpanel">
    <div class="row">
        <!-- Knowledge Sources -->
        <div class="col-md-8">
            <div class="card" style="background: #1a1a1a; border: 1px solid rgba(139, 92, 246, 0.3);">
                <div class="card-header d-flex justify-content-between align-items-center" style="background: rgba(139, 92, 246, 0.1);">
                    <h5 class="mb-0" style="color: #a78bfa;">What Agents Have Learned</h5>
                    <span class="badge" style="background: #8b5cf6;" id="knowledge-count">0</span>
                </div>
                <div class="card-body" style="max-height: 500px; overflow-y: auto;">
                    <div id="knowledge-list">
                        <!-- Knowledge items loaded here -->
                    </div>
                </div>
            </div>
        </div>

        <!-- Knowledge Stats -->
        <div class="col-md-4">
            <div class="card mb-3" style="background: #1a1a1a; border: 1px solid rgba(34, 197, 94, 0.3);">
                <div class="card-header" style="background: rgba(34, 197, 94, 0.1);">
                    <h6 class="mb-0" style="color: #22c55e;">Knowledge by Type</h6>
                </div>
                <div class="card-body" id="knowledge-by-type">
                    <!-- Stats loaded here -->
                </div>
            </div>

            <div class="card" style="background: #1a1a1a; border: 1px solid rgba(249, 115, 22, 0.3);">
                <div class="card-header" style="background: rgba(249, 115, 22, 0.1);">
                    <h6 class="mb-0" style="color: #f97316;">Recent Transfers</h6>
                </div>
                <div class="card-body" id="recent-transfers">
                    <!-- Transfers loaded here -->
                </div>
            </div>
        </div>
    </div>
</div>
```

#### 2.2 New API Endpoint: `/api/spider-intelligence/knowledge/`

Location: `core/views_spider_dashboard.py`

```python
@api_view(['GET'])
def spider_knowledge(request):
    """
    Returns knowledge sources derived from spider data.
    """
    from core.models_unified_system import AgentKnowledgeSource, KnowledgeTransfer

    limit = int(request.GET.get('limit', 50))
    knowledge_type = request.GET.get('type', 'all')

    queryset = AgentKnowledgeSource.objects.all()
    if knowledge_type != 'all':
        queryset = queryset.filter(knowledge_type=knowledge_type)

    sources = queryset.order_by('-first_discovered_at')[:limit]

    # Get type breakdown
    type_counts = AgentKnowledgeSource.objects.values('knowledge_type').annotate(
        count=Count('id')
    ).order_by('-count')

    # Get recent transfers
    transfers = KnowledgeTransfer.objects.select_related(
        'source_knowledge', 'connection__from_agent', 'connection__to_agent'
    ).order_by('-created_at')[:10]

    return JsonResponse({
        'status': 'success',
        'knowledge': [{
            'id': k.id,
            'title': k.title,
            'summary': k.summary,
            'type': k.knowledge_type,
            'confidence': k.confidence_score,
            'data_points': k.data_points_count,
            'spider_sources': k.source_spider_names or [],
            'discovered_at': k.first_discovered_at.isoformat() if k.first_discovered_at else None
        } for k in sources],
        'type_counts': list(type_counts),
        'transfers': [{
            'from': t.connection.from_agent.name if t.connection else 'Unknown',
            'to': t.connection.to_agent.name if t.connection else 'Unknown',
            'knowledge': t.source_knowledge.title if t.source_knowledge else 'Unknown',
            'summary': t.transfer_summary,
            'useful': t.was_useful
        } for t in transfers],
        'total': AgentKnowledgeSource.objects.count()
    })
```

#### 2.3 JavaScript: Knowledge Loading Functions

```javascript
// Load Knowledge Sources
async function loadKnowledgeSources() {
    const container = document.getElementById('knowledge-list');
    const typeContainer = document.getElementById('knowledge-by-type');
    const transfersContainer = document.getElementById('recent-transfers');

    try {
        const response = await fetch('/api/spider-intelligence/knowledge/', {
            headers: { 'X-CSRFToken': getCsrfToken() }
        });
        const data = await response.json();

        if (data.status === 'success') {
            // Update count
            document.getElementById('knowledge-count').textContent = data.total;

            // Render knowledge list
            container.innerHTML = data.knowledge.map(k => `
                <div class="p-3 mb-2" style="background: rgba(139, 92, 246, 0.1); border-radius: 8px;">
                    <div class="d-flex justify-content-between">
                        <strong class="text-light">${k.title}</strong>
                        <span class="badge" style="background: rgba(139, 92, 246, 0.3);">${k.type}</span>
                    </div>
                    <p class="text-muted small mb-1">${k.summary || 'No summary'}</p>
                    <div class="d-flex gap-3">
                        <small class="text-muted">Confidence: ${(k.confidence * 100).toFixed(0)}%</small>
                        <small class="text-muted">Data points: ${k.data_points}</small>
                    </div>
                    ${k.spider_sources.length > 0 ? `
                        <div class="mt-1">
                            ${k.spider_sources.map(s => `<span class="badge me-1" style="background: rgba(249, 115, 22, 0.2); font-size: 9px;">${s}</span>`).join('')}
                        </div>
                    ` : ''}
                </div>
            `).join('') || '<p class="text-muted">No knowledge sources found</p>';

            // Render type counts
            typeContainer.innerHTML = data.type_counts.map(tc => `
                <div class="d-flex justify-content-between mb-2">
                    <span class="text-light">${tc.knowledge_type}</span>
                    <span class="badge bg-secondary">${tc.count}</span>
                </div>
            `).join('');

            // Render transfers
            transfersContainer.innerHTML = data.transfers.map(t => `
                <div class="p-2 mb-2" style="background: rgba(249, 115, 22, 0.1); border-radius: 4px; font-size: 12px;">
                    <div class="text-light">${t.from} → ${t.to}</div>
                    <small class="text-muted">${t.knowledge}</small>
                </div>
            `).join('') || '<p class="text-muted small">No transfers yet</p>';
        }
    } catch (error) {
        console.error('Error loading knowledge:', error);
    }
}
```

---

### Phase 3: Visual Timeline (20-30 minutes)

**Goal:** Show when data was collected with visual timeline

#### 3.1 New Template: `intel_timeline.html`

Location: `ai_core/templates/components/panels/intelligence/intel_timeline.html`

```html
<!-- Timeline Sub-Tab -->
<div class="tab-pane fade" id="intel-timeline" role="tabpanel">
    <div class="card" style="background: #1a1a1a; border: 1px solid rgba(6, 182, 212, 0.3);">
        <div class="card-header d-flex justify-content-between align-items-center" style="background: rgba(6, 182, 212, 0.1);">
            <h5 class="mb-0" style="color: #22d3ee;">Data Collection Timeline</h5>
            <div>
                <button class="btn btn-sm me-2" onclick="setTimelineRange('24h')" style="background: rgba(6, 182, 212, 0.2); color: #67e8f9;">24h</button>
                <button class="btn btn-sm me-2" onclick="setTimelineRange('7d')" style="background: rgba(6, 182, 212, 0.2); color: #67e8f9;">7d</button>
                <button class="btn btn-sm" onclick="setTimelineRange('30d')" style="background: rgba(6, 182, 212, 0.2); color: #67e8f9;">30d</button>
            </div>
        </div>
        <div class="card-body">
            <!-- Timeline Chart -->
            <div id="timeline-chart" style="height: 200px; margin-bottom: 20px;">
                <!-- SVG chart rendered here -->
            </div>

            <!-- Source Freshness Grid -->
            <h6 class="text-light mb-3">Source Freshness</h6>
            <div id="freshness-grid" class="row">
                <!-- Grid items loaded here -->
            </div>
        </div>
    </div>
</div>
```

#### 3.2 New API Endpoint: `/api/spider-intelligence/timeline/`

```python
@api_view(['GET'])
def spider_timeline(request):
    """
    Returns data collection timeline and source freshness.
    """
    from django.db.models.functions import TruncHour, TruncDay
    from django.utils import timezone
    from datetime import timedelta

    range_param = request.GET.get('range', '24h')

    if range_param == '24h':
        since = timezone.now() - timedelta(hours=24)
        trunc_fn = TruncHour
    elif range_param == '7d':
        since = timezone.now() - timedelta(days=7)
        trunc_fn = TruncDay
    else:
        since = timezone.now() - timedelta(days=30)
        trunc_fn = TruncDay

    # Get collection timeline
    timeline = SpiderData.objects.filter(
        created_at__gte=since
    ).annotate(
        period=trunc_fn('created_at')
    ).values('period').annotate(
        count=Count('id')
    ).order_by('period')

    # Get source freshness
    freshness = SpiderData.objects.values('spider_name').annotate(
        last_update=Max('created_at'),
        total_records=Count('id')
    ).order_by('-last_update')

    return JsonResponse({
        'status': 'success',
        'timeline': [{
            'period': t['period'].isoformat(),
            'count': t['count']
        } for t in timeline],
        'freshness': [{
            'source': f['spider_name'],
            'last_update': f['last_update'].isoformat() if f['last_update'] else None,
            'total': f['total_records'],
            'age_minutes': (timezone.now() - f['last_update']).total_seconds() / 60 if f['last_update'] else None
        } for f in freshness]
    })
```

#### 3.3 JavaScript: Timeline Rendering

```javascript
// Timeline state
let timelineRange = '24h';

// Load Timeline Data
async function loadTimeline() {
    try {
        const response = await fetch(`/api/spider-intelligence/timeline/?range=${timelineRange}`, {
            headers: { 'X-CSRFToken': getCsrfToken() }
        });
        const data = await response.json();

        if (data.status === 'success') {
            renderTimelineChart(data.timeline);
            renderFreshnessGrid(data.freshness);
        }
    } catch (error) {
        console.error('Error loading timeline:', error);
    }
}

// Render Simple Bar Chart (CSS-based, no library needed)
function renderTimelineChart(timeline) {
    const container = document.getElementById('timeline-chart');
    const maxCount = Math.max(...timeline.map(t => t.count), 1);

    container.innerHTML = `
        <div class="d-flex align-items-end justify-content-between" style="height: 180px; padding: 0 10px;">
            ${timeline.map(t => {
                const height = (t.count / maxCount) * 160;
                const date = new Date(t.period);
                const label = timelineRange === '24h'
                    ? date.getHours() + ':00'
                    : date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
                return `
                    <div class="text-center" style="flex: 1; max-width: 40px;">
                        <div style="height: ${height}px; background: linear-gradient(180deg, #06b6d4 0%, #0891b2 100%); border-radius: 4px 4px 0 0; margin: 0 2px;" title="${t.count} items"></div>
                        <small class="text-muted" style="font-size: 9px;">${label}</small>
                    </div>
                `;
            }).join('')}
        </div>
    `;
}

// Render Freshness Grid
function renderFreshnessGrid(freshness) {
    const container = document.getElementById('freshness-grid');

    container.innerHTML = freshness.slice(0, 20).map(f => {
        let color = '#22c55e'; // Green = fresh
        let status = 'Fresh';

        if (f.age_minutes > 60 * 24) {
            color = '#ef4444'; // Red = stale
            status = 'Stale';
        } else if (f.age_minutes > 60 * 6) {
            color = '#f59e0b'; // Yellow = aging
            status = 'Aging';
        }

        const ageText = f.age_minutes < 60
            ? `${Math.round(f.age_minutes)}m ago`
            : f.age_minutes < 60 * 24
                ? `${Math.round(f.age_minutes / 60)}h ago`
                : `${Math.round(f.age_minutes / 60 / 24)}d ago`;

        return `
            <div class="col-md-3 col-sm-4 col-6 mb-2">
                <div class="p-2 text-center" style="background: ${color}20; border: 1px solid ${color}40; border-radius: 8px;">
                    <div class="text-light small">${f.source}</div>
                    <div style="color: ${color}; font-size: 11px;">${ageText}</div>
                    <small class="text-muted">${f.total} records</small>
                </div>
            </div>
        `;
    }).join('');
}

// Set Timeline Range
function setTimelineRange(range) {
    timelineRange = range;
    loadTimeline();
}
```

---

### Phase 4: Real-Time Updates (20-30 minutes)

**Goal:** Push new data to UI as spiders crawl

#### 4.1 WebSocket Integration

The WebSocket infrastructure already exists. We need to:

1. **Emit events when spiders complete** (in `core/tasks.py`)
2. **Listen for events in frontend** (in JS)

#### 4.2 Backend: Emit Spider Events

Location: `core/tasks.py` (modify `run_spider_task`)

```python
# Add to run_spider_task after successful spider execution
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def emit_spider_update(spider_name, items_count, category):
    """Emit real-time update when spider completes."""
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'spider_intelligence',
        {
            'type': 'spider_update',
            'spider': spider_name,
            'items': items_count,
            'category': category,
            'timestamp': timezone.now().isoformat()
        }
    )
```

#### 4.3 Frontend: Listen for Updates

```javascript
// Connect to Spider Intelligence WebSocket
function connectSpiderWebSocket() {
    const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/spider-intelligence/`;
    const ws = new WebSocket(wsUrl);

    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);

        if (data.type === 'spider_update') {
            // Show toast notification
            showSpiderUpdateToast(data);

            // Refresh current view if on Intelligence tab
            if (document.getElementById('trending').classList.contains('active')) {
                // Soft refresh - prepend new items instead of full reload
                prependFeedItems(data);
            }
        }
    };

    ws.onclose = function() {
        // Reconnect after 5 seconds
        setTimeout(connectSpiderWebSocket, 5000);
    };
}

// Show Update Toast
function showSpiderUpdateToast(data) {
    const toast = document.createElement('div');
    toast.className = 'position-fixed bottom-0 end-0 p-3';
    toast.style.zIndex = '9999';
    toast.innerHTML = `
        <div class="toast show" style="background: rgba(34, 197, 94, 0.9);">
            <div class="toast-body text-white">
                <strong>${data.spider}</strong> collected ${data.items} new items
            </div>
        </div>
    `;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    connectSpiderWebSocket();
});
```

---

### Phase 5: Navigation Updates (10 minutes)

#### 5.1 Update Intelligence Sub-Tabs

Location: `ai_core/templates/components/panels/intelligence_panel.html`

Add new sub-tabs to the navigation:

```html
<ul class="nav nav-pills mb-4" id="intel-subtabs" role="tablist">
    <!-- Existing tabs -->
    <li class="nav-item" role="presentation">
        <button class="nav-link active" id="intel-trending-tab" ...>Trending</button>
    </li>
    <li class="nav-item" role="presentation">
        <button class="nav-link" id="intel-markets-tab" ...>Markets</button>
    </li>
    <li class="nav-item" role="presentation">
        <button class="nav-link" id="intel-opportunities-tab" ...>Opportunities</button>
    </li>

    <!-- NEW TABS -->
    <li class="nav-item" role="presentation">
        <button class="nav-link" id="intel-feed-tab" data-bs-toggle="pill" data-bs-target="#intel-data-feed" type="button" role="tab" style="color: #3b82f6;">
            📰 Data Feed
        </button>
    </li>
    <li class="nav-item" role="presentation">
        <button class="nav-link" id="intel-knowledge-tab" data-bs-toggle="pill" data-bs-target="#intel-knowledge" type="button" role="tab" style="color: #8b5cf6;">
            🧠 Knowledge
        </button>
    </li>
    <li class="nav-item" role="presentation">
        <button class="nav-link" id="intel-timeline-tab" data-bs-toggle="pill" data-bs-target="#intel-timeline" type="button" role="tab" style="color: #06b6d4;">
            📊 Timeline
        </button>
    </li>

    <!-- Existing spider tab -->
    <li class="nav-item" role="presentation">
        <button class="nav-link" id="intel-spiders-tab" ...>Spiders</button>
    </li>
</ul>
```

#### 5.2 Include New Templates

```html
<div class="tab-content" id="intel-subtabs-content">
    {% include "components/panels/intelligence/intel_trending.html" %}
    {% include "components/panels/intelligence/intel_markets.html" %}
    {% include "components/panels/intelligence/intel_opportunities.html" %}
    {% include "components/panels/intelligence/intel_data_feed.html" %}      <!-- NEW -->
    {% include "components/panels/intelligence/intel_knowledge.html" %}       <!-- NEW -->
    {% include "components/panels/intelligence/intel_timeline.html" %}        <!-- NEW -->
    {% include "components/panels/intelligence/intel_spiders.html" %}
</div>
```

---

## File Changes Summary

### New Files to Create

| File | Purpose |
|------|---------|
| `ai_core/templates/components/panels/intelligence/intel_data_feed.html` | Data feed browsing UI |
| `ai_core/templates/components/panels/intelligence/intel_knowledge.html` | Knowledge integration UI |
| `ai_core/templates/components/panels/intelligence/intel_timeline.html` | Visual timeline UI |

### Files to Modify

| File | Changes |
|------|---------|
| `core/views_spider_dashboard.py` | Add 3 new API endpoints |
| `core/urls.py` | Add URL routes for new endpoints |
| `ai_core/templates/components/panels/intelligence_panel.html` | Add new sub-tabs |
| `ai_core/templates/partials/js/spider_intelligence.html` | Add JS functions |
| `core/tasks.py` | Add WebSocket emit for real-time updates |

---

## Testing Plan

### API Testing
```bash
# Test feed endpoint
curl http://localhost:8000/api/spider-intelligence/feed/?category=tech&limit=10

# Test knowledge endpoint
curl http://localhost:8000/api/spider-intelligence/knowledge/

# Test timeline endpoint
curl http://localhost:8000/api/spider-intelligence/timeline/?range=24h
```

### UI Testing
1. Navigate to Intelligence tab
2. Click each new sub-tab (Data Feed, Knowledge, Timeline)
3. Test category filtering on Data Feed
4. Verify timeline chart renders
5. Check freshness grid colors (green/yellow/red)
6. Verify real-time toast notifications when spider runs

---

## Success Criteria

- [x] Data Feed shows actual article headlines with clickable links
- [x] Category filtering works (tech, news, financial, etc.)
- [x] Knowledge panel shows 865 knowledge sources
- [x] Knowledge transfers displayed (168 transfers)
- [x] Timeline chart visualizes collection patterns
- [x] Freshness grid shows source health
- [x] Real-time toasts appear when spiders complete
- [x] All new APIs return valid JSON

---

## Notes

- **Skipping Legal spiders** - User has separate plans for legal features
- **No external charting library** - Using CSS-based charts for simplicity
- **WebSocket reuse** - Leveraging existing infrastructure
- **Mobile responsive** - All new components use Bootstrap grid

---

*Document created for Session 399 by Claude + Human collaboration*

---

## Implementation Status (Updated Dec 8, 2025)

### Completed
- **Phase 1: Data Feed** - Created `intel_data_feed.html` and API endpoint
- **Phase 2: Knowledge Panel** - Created `intel_knowledge.html` and API endpoint
- **Phase 3: Timeline** - Created `intel_timeline.html` and API endpoint
- **Phase 5: Navigation** - Added 3 new sub-tabs to Intelligence panel

### API Endpoints Created
| Endpoint | Status | Description |
|----------|--------|-------------|
| `/api/spider-intelligence/feed/` | Working | Paginated data items from all spiders |
| `/api/spider-intelligence/knowledge/` | Working | Knowledge sources and transfers |
| `/api/spider-intelligence/timeline/` | Working | Collection timeline and freshness |

### Files Modified
- `core/views_spider_intelligence.py` - Added 3 new view functions
- `core/urls.py` - Added 3 new URL patterns
- `ai_core/templates/components/panels/intelligence_panel.html` - Added sub-tab navigation
- `ai_core/templates/partials/js/spider_intelligence.html` - Added JS functions

### Files Created
- `ai_core/templates/components/panels/intelligence/intel_data_feed.html`
- `ai_core/templates/components/panels/intelligence/intel_knowledge.html`
- `ai_core/templates/components/panels/intelligence/intel_timeline.html`

### Bug Fixed
- Knowledge API had wrong field names (`from_agent`/`to_agent` should be `teacher_agent`/`student_agent`)

### Phase 4 Complete (Added Later)
- **WebSocket Consumer**: `SpiderIntelligenceConsumer` in `ai_core/intelligence/consumers.py`
- **WebSocket Route**: `/ws/spider-intelligence/` in `ai_core/intelligence/routing.py`
- **Redis Publish**: Added to `run_spider_network()` in `core/tasks.py`
- **JavaScript**: WebSocket connection + toast notifications in `spider_intelligence.html`

All phases complete!
