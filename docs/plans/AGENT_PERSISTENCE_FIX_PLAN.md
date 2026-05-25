<!-- DOC-POINTER-V1 -->
> **⚠ HISTORICAL PLAN (Q4 2025 / Q1 2026 build phase).** Drafted during platform build-out; may be partially shipped, renamed in code, or quietly superseded. Preserved for historical reference, not current truth. For current truth see [`docs/INDEX.md`](../INDEX.md) + [`PLATFORM_INVENTORY.md`](../PLATFORM_INVENTORY.md) + the latest handoff. See [`docs/plans/INDEX.md`](INDEX.md) for directory scope.

# Agent Persistence Fix Plan - Session 861

**Problem:** 96% of ContentWriterAgent blogs were lost because content was only stored in ephemeral `AgentResult`. Investigation revealed ~45 agents have the same issue.

**Solution:** All content-creating agents must save to the `Deliverable` model.

---

## Phase 1: Base Infrastructure (PR #1)

### 1.1 Add `_save_to_deliverable()` to BaseAgent

Add a universal method to `core/agents/base_agent.py`:

```python
def _save_to_deliverable(
    self,
    title: str,
    content: str,
    deliverable_type: str,  # 'document', 'analysis', 'report', 'research', 'strategy', 'plan', 'script'
    category: str = '',
    tags: List[str] = None,
    content_format: str = 'markdown',
    metadata: Dict[str, Any] = None,
    user=None,
    trace_id: str = None,
) -> Optional['Deliverable']:
    """
    Session 861: Save agent output to Deliverable model for persistence.

    All content-creating agents should call this to ensure their output
    is not lost after the request completes.
    """
    try:
        from core.models_deliverables import Deliverable
        from django.utils.text import slugify
        import uuid

        # Generate unique slug
        base_slug = slugify(title[:100])
        unique_slug = f"{base_slug}-{uuid.uuid4().hex[:8]}"

        deliverable = Deliverable.objects.create(
            title=title,
            slug=unique_slug,
            deliverable_type=deliverable_type,
            category=category or self._get_agent_category(),
            tags=tags or [],
            agent_name=self.name,
            agent_task=self._context.get('task', '') if hasattr(self, '_context') else '',
            content=content,
            content_format=content_format,
            preview_content=content[:500] if content else '',
            metadata=metadata or {},
            user=user,
            trace_id=uuid.UUID(trace_id) if trace_id else None,
            status='ready',
        )

        logger.info(f"📦 Session 861: Saved Deliverable {deliverable.id} - {title[:50]}")
        return deliverable

    except Exception as e:
        logger.warning(f"Failed to save Deliverable: {e}")
        return None

def _get_agent_category(self) -> str:
    """Map agent to a category for Deliverables."""
    category_map = {
        'ContentWriter': 'Content',
        'Stock': 'Finance',
        'Bull': 'Finance',
        'Bear': 'Finance',
        'Market': 'Finance',
        'Legal': 'Legal',
        'Technical': 'Development',
        'Code': 'Development',
        'Research': 'Research',
        'Trend': 'Analysis',
        'Competitor': 'Business',
        'Brand': 'Marketing',
        'SEO': 'Marketing',
        'Podcast': 'Content',
        'Debate': 'Content',
        'Smart': 'Blockchain',
        'Whale': 'Blockchain',
    }
    for prefix, category in category_map.items():
        if prefix in self.name:
            return category
    return 'General'
```

---

## Phase 2: Content Creation Agents (PR #2)

### Priority: HIGH - These create primary content

| Agent | Content Type | Deliverable Type | Category |
|-------|--------------|------------------|----------|
| ContentWriterAgent | Blogs, articles | `document` | Content |
| TechnicalDocumentAgent | Tech docs, specs | `document` | Development |
| PodcastCoordinatorAgent | Scripts, transcripts | `script` | Content |
| LegalDocDrafterAgent | Legal documents | `document` | Legal |
| ResearchAgent | Research findings | `research` | Research |

### Implementation for each:

**ContentWriterAgent** (already fixed in Session 860 - verify using Deliverable)
```python
# In execute(), after generating content:
self._save_to_deliverable(
    title=content_title,
    content=full_content,
    deliverable_type='document',
    category='Content',
    tags=['blog', topic],
    metadata={'topic': topic, 'tone': tone, 'word_count': word_count}
)
```

**TechnicalDocumentAgent**
```python
# In execute(), after generating document:
self._save_to_deliverable(
    title=doc_title,
    content=document_content,
    deliverable_type='document',
    category='Development',
    tags=['technical', doc_type],
    metadata={'document_type': doc_type, 'version': version}
)
```

**PodcastCoordinatorAgent**
```python
# In execute(), after generating script:
self._save_to_deliverable(
    title=f"Podcast Script: {topic}",
    content=script_content,
    deliverable_type='script',
    category='Content',
    tags=['podcast', 'script'],
    metadata={'format': 'debate', 'participants': participants}
)
```

**LegalDocDrafterAgent**
```python
# In execute(), after generating document:
self._save_to_deliverable(
    title=document_title,
    content=legal_content,
    deliverable_type='document',
    category='Legal',
    tags=['legal', doc_type],
    metadata={'document_type': doc_type, 'jurisdiction': jurisdiction}
)
```

**ResearchAgent**
```python
# In execute(), after generating research:
self._save_to_deliverable(
    title=f"Research: {query}",
    content=research_findings,
    deliverable_type='research',
    category='Research',
    tags=['research', topic],
    metadata={'sources': sources, 'query': query}
)
```

---

## Phase 3: Analysis Agents (PR #3)

### Priority: HIGH - These create valuable analysis

| Agent | Content Type | Deliverable Type | Category |
|-------|--------------|------------------|----------|
| StockAnalystAgent | Stock analysis | `analysis` | Finance |
| BullCaseAgent | Bull thesis | `analysis` | Finance |
| BearCaseAgent | Bear thesis | `analysis` | Finance |
| TrendAnalysisAgent | Trend analysis | `analysis` | Analysis |
| MarketIntelligenceAgent | Market insights | `analysis` | Finance |
| OpportunityScoringAgent | Opportunity scores | `analysis` | Business |
| CompetitorAnalysisAgent | Competitor intel | `analysis` | Business |
| SmartContractAuditorAgent | Audit reports | `report` | Blockchain |

### Implementation Pattern:
```python
# In execute(), after generating analysis:
self._save_to_deliverable(
    title=f"{self.name}: {symbol or topic}",
    content=analysis_content,
    deliverable_type='analysis',
    category='Finance',  # or appropriate category
    tags=['analysis', symbol] if symbol else ['analysis'],
    metadata={'symbol': symbol, 'analysis_type': analysis_type}
)
```

---

## Phase 4: Strategy Agents (PR #4)

### Priority: MEDIUM - Strategic recommendations

| Agent | Content Type | Deliverable Type | Category |
|-------|--------------|------------------|----------|
| ContentStrategyAgent | Content strategy | `strategy` | Marketing |
| MarketingStrategyAgent | Marketing plans | `strategy` | Marketing |
| BrandStrategyAgent | Brand strategy | `strategy` | Marketing |
| BrandIdentityAgent | Brand guidelines | `strategy` | Marketing |
| SEOOptimizerAgent | SEO recommendations | `strategy` | Marketing |
| SocialMediaAgent | Social strategy | `strategy` | Marketing |

### Implementation Pattern:
```python
# In execute(), after generating strategy:
self._save_to_deliverable(
    title=f"Strategy: {topic or brand}",
    content=strategy_content,
    deliverable_type='strategy',
    category='Marketing',
    tags=['strategy', strategy_type],
    metadata={'strategy_type': strategy_type, 'target': target}
)
```

---

## Phase 5: Debate/Podcast Agents (PR #5)

### Priority: MEDIUM - Debate content preservation

| Agent | Content Type | Deliverable Type | Category |
|-------|--------------|------------------|----------|
| DebateAdvocateAgent | Advocate arguments | `script` | Content |
| DebateSkepticAgent | Skeptic arguments | `script` | Content |
| ModeratorAgent | Moderation/summary | `script` | Content |

### Implementation Pattern:
```python
# In execute(), after generating arguments:
self._save_to_deliverable(
    title=f"Debate {role}: {topic}",
    content=argument_content,
    deliverable_type='script',
    category='Content',
    tags=['debate', role.lower()],
    metadata={'role': role, 'topic': topic, 'round': round_number}
)
```

---

## Phase 6: Narrative Agents (PR #6)

### Priority: MEDIUM - Narrative analysis

| Agent | Content Type | Deliverable Type | Category |
|-------|--------------|------------------|----------|
| CulturalImpactAgent | Impact analysis | `analysis` | Analysis |
| NarrativeHistorianAgent | Historical analysis | `analysis` | Analysis |
| TrendBreakDetectorAgent | Trend detection | `analysis` | Analysis |

### Implementation Pattern:
```python
# In execute(), after generating analysis:
self._save_to_deliverable(
    title=f"Narrative Analysis: {topic}",
    content=narrative_content,
    deliverable_type='analysis',
    category='Analysis',
    tags=['narrative', 'analysis'],
    metadata={'narrative_type': narrative_type}
)
```

---

## Phase 7: Business Research Agents (PR #7)

### Priority: MEDIUM - Business research

| Agent | Content Type | Deliverable Type | Category |
|-------|--------------|------------------|----------|
| CustomerResearchAgent | Customer insights | `research` | Business |
| BaseBusinessResearchAgent | Business research | `research` | Business |

### Implementation Pattern:
```python
# In execute(), after generating research:
self._save_to_deliverable(
    title=f"Business Research: {topic}",
    content=research_content,
    deliverable_type='research',
    category='Business',
    tags=['research', 'business'],
    metadata={'research_type': research_type}
)
```

---

## Phase 8: Blockchain Agents (PR #8)

### Priority: MEDIUM - Blockchain analysis

| Agent | Content Type | Deliverable Type | Category |
|-------|--------------|------------------|----------|
| ExploitDetectorAgent | Exploit analysis | `report` | Blockchain |
| WhaleWatcherAgent | Whale movements | `analysis` | Blockchain |
| TransactionMonitorAgent | Transaction analysis | `analysis` | Blockchain |

### Implementation Pattern:
```python
# In execute(), after generating analysis:
self._save_to_deliverable(
    title=f"Blockchain Analysis: {topic}",
    content=analysis_content,
    deliverable_type='analysis',
    category='Blockchain',
    tags=['blockchain', analysis_type],
    metadata={'chain': chain, 'addresses': addresses}
)
```

---

## Phase 9: Stock/Market Agents (PR #9)

### Priority: HIGH - Valuable market analysis

| Agent | Content Type | Deliverable Type | Category |
|-------|--------------|------------------|----------|
| SignalScannerAgent | Trading signals | `analysis` | Finance |
| MarketAnomalyDetectorAgent | Anomaly detection | `analysis` | Finance |
| InstitutionalWatcherAgent | Institutional moves | `analysis` | Finance |
| MarketMovementMonitorAgent | Market movements | `analysis` | Finance |

### Implementation Pattern:
```python
# In execute(), after generating signals/analysis:
self._save_to_deliverable(
    title=f"Market Signal: {signal_type}",
    content=analysis_content,
    deliverable_type='analysis',
    category='Finance',
    tags=['market', 'signal', symbol] if symbol else ['market', 'signal'],
    metadata={'signal_type': signal_type, 'symbols': symbols}
)
```

---

## Phase 10: Prediction/Betting Agents (PR #10)

### Priority: MEDIUM - Prediction preservation

| Agent | Content Type | Deliverable Type | Category |
|-------|--------------|------------------|----------|
| BookmakerAgent | Betting analysis | `analysis` | Betting |
| SportsOddsAnalyst | Odds analysis | `analysis` | Betting |
| PredictionMarketAnalyst | Prediction analysis | `analysis` | Betting |
| ArbitrageDetector | Arbitrage opportunities | `analysis` | Betting |

### Implementation Pattern:
```python
# In execute(), after generating analysis:
self._save_to_deliverable(
    title=f"Prediction Analysis: {event}",
    content=prediction_content,
    deliverable_type='analysis',
    category='Betting',
    tags=['prediction', 'betting'],
    metadata={'event': event, 'odds': odds}
)
```

---

## Phase 11: Development Agents (PR #11)

### Priority: MEDIUM - Code/dev outputs (some already persist via file system)

| Agent | Content Type | Deliverable Type | Category | Notes |
|-------|--------------|------------------|----------|-------|
| CodeGeneratorAgent | Generated code | `code` | Development | Uses SKIN layer for files |
| CodeReviewAgent | Code reviews | `report` | Development | Reviews as reports |
| DevOpsAgent | DevOps scripts | `code` | Development | Infrastructure code |
| FullStackDeveloperAgent | Full stack code | `code` | Development | Uses SKIN layer |

### Implementation Pattern:
```python
# For agents that generate code reviews/reports:
self._save_to_deliverable(
    title=f"Code Review: {file_or_project}",
    content=review_content,
    deliverable_type='report',
    category='Development',
    tags=['code-review', language],
    metadata={'files_reviewed': files, 'issues_found': issue_count}
)
```

---

## Phase 12: Executive Agents (PR #12)

### Priority: LOW - Executive summaries

| Agent | Content Type | Deliverable Type | Category |
|-------|--------------|------------------|----------|
| CTOAgent | Technical decisions | `report` | Executive |
| COOAgent | Operations reports | `report` | Executive |
| CreativeDirectorAgent | Creative direction | `strategy` | Executive |
| MeetingCoordinatorAgent | Meeting notes | `document` | Executive |

### Implementation Pattern:
```python
# In execute(), after generating report:
self._save_to_deliverable(
    title=f"Executive Report: {topic}",
    content=report_content,
    deliverable_type='report',
    category='Executive',
    tags=['executive', report_type],
    metadata={'department': department}
)
```

---

## Phase 13: Remaining Agents (PR #13)

### Priority: LOW - Miscellaneous

| Agent | Content Type | Deliverable Type | Category |
|-------|--------------|------------------|----------|
| ThinkingAgent | Reasoning traces | `analysis` | Analysis |
| PlatformAuditAgent | Audit reports | `report` | Operations |
| SystemIntelligenceAgent | System analysis | `report` | Operations |
| OpportunityPipelineAgent | Opportunities | `analysis` | Business |

---

## Summary: 74 Agents Categorized

| Phase | Agent Count | Priority | Deliverable Type |
|-------|-------------|----------|------------------|
| 1 | 0 (base infra) | CRITICAL | - |
| 2 | 5 | HIGH | document, research, script |
| 3 | 8 | HIGH | analysis, report |
| 4 | 6 | MEDIUM | strategy |
| 5 | 3 | MEDIUM | script |
| 6 | 3 | MEDIUM | analysis |
| 7 | 2 | MEDIUM | research |
| 8 | 3 | MEDIUM | analysis, report |
| 9 | 4 | HIGH | analysis |
| 10 | 4 | MEDIUM | analysis |
| 11 | 4 | MEDIUM | code, report |
| 12 | 4 | LOW | report, strategy, document |
| 13 | 4 | LOW | analysis, report |

**Total: 50 content-creating agents need persistence fixes**

---

## Agents That Already Have Good Persistence

| Agent | Model Used | Status |
|-------|------------|--------|
| ContentWriterAgent | SelfBlog (Session 860) | ✅ FIXED |
| CampaignOrchestratorAgent | CampaignDeliverable | ✅ OK |
| InitiativeAgent | Initiative/Stage/Document | ✅ OK |
| AudioAgent | AudioHistory | ✅ OK |
| ImageAgent | External service (Stability AI) | ⚠️ External |
| VideoAgent | External service (Runway) | ⚠️ External |
| ThreeDAgent | External service | ⚠️ External |

---

## Implementation Order

1. **Phase 1** - Add base infrastructure (Day 1)
2. **Phase 2 + 3 + 9** - HIGH priority content/analysis agents (Day 1-2)
3. **Phase 4-8** - MEDIUM priority agents (Day 2-3)
4. **Phase 10-13** - LOW priority agents (Day 3-4)

---

## Testing Strategy

1. **Unit test**: Call each agent and verify Deliverable created
2. **Integration test**: Full conversation → verify Deliverable persists
3. **Production audit**: After deploy, run audit script to compare AgentMemory vs Deliverable counts

---

## Audit Script (Post-Implementation)

```python
# scripts/audit_agent_persistence.py
from core.models_unified_system import AgentMemory
from core.models_deliverables import Deliverable

# Compare counts by agent
agents = AgentMemory.objects.values('agent__name').annotate(
    memory_count=Count('id')
)

for agent in agents:
    name = agent['agent__name']
    memories = agent['memory_count']
    deliverables = Deliverable.objects.filter(agent_name=name).count()

    if memories > deliverables:
        print(f"⚠️ {name}: {memories} memories, {deliverables} deliverables (POSSIBLE LOSS)")
    else:
        print(f"✅ {name}: {memories} memories, {deliverables} deliverables")
```

---

## Success Metrics

| Metric | Before | Target |
|--------|--------|--------|
| Content persistence rate | ~4% | 100% |
| Lost blogs | 111 | 0 |
| Lost analyses | Unknown (many) | 0 |
| Deliverables per agent execution | ~0 | 1+ |

---

**Created:** Session 861
**Author:** Claude Code
**Status:** Ready for Implementation
