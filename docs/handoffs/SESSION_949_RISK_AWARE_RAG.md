---
originating_session: 949
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 949 - Risk-Aware RAG Implementation

**Date:** February 6, 2026
**Focus:** Risk-Aware RAG - Dual-Channel Retrieval with Risk Re-Ranking
**PRs:** #920, #921, #922

---

## Summary

Implemented a complete risk-aware RAG system based on ChatGPT analysis of retrieval gaps. The system now ensures critical docs, incident reports, and audit findings are never missed during retrieval, even when semantic similarity is low.

---

## Phase 1 (P0): Document Risk Fields + Audit Linking

**PR #920**

### Changes to `content/models.py`
Added risk-aware fields to Document model:
```python
RISK_LEVEL_CHOICES = [
    ('critical', 'Critical - Must always retrieve'),
    ('high', 'High - Boost in retrieval'),
    ('medium', 'Medium - Standard retrieval'),
    ('low', 'Low - May be skipped under budget pressure'),
]

DOCUMENT_CLASS_CHOICES = [
    ('reference', 'Reference Documentation'),
    ('postmortem', 'Incident Postmortem'),
    ('incident_report', 'Incident Report'),
    ('constraint', 'Constraint/Policy Document'),
    ('security', 'Security Advisory'),
    ('architecture', 'Architecture Decision'),
    ('runbook', 'Operational Runbook'),
    ('changelog', 'Changelog/Release Notes'),
]

is_critical = models.BooleanField(default=False, db_index=True)
risk_level = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES, default='medium')
document_class = models.CharField(max_length=30, choices=DOCUMENT_CLASS_CHOICES, default='reference')
incident_date = models.DateTimeField(null=True, blank=True)
retrieval_boost = models.FloatField(default=1.0)
```

### Changes to `core/models_audit_tracking.py`
Added FK to link findings to documents:
```python
linked_document = models.ForeignKey(
    'content.Document',
    null=True, blank=True,
    on_delete=models.SET_NULL,
    related_name='audit_findings',
    help_text="Document describing or related to this finding"
)
```

### New File: `core/management/commands/classify_docs_for_rag.py`
Management command to auto-classify existing docs:
- Pattern matching for critical docs (CLAUDE.md, GOVERNANCE.md, etc.)
- Pattern matching for document classes (postmortem, incident, security, constraint)
- Keyword detection for high-risk content

Usage:
```bash
python manage.py classify_docs_for_rag
python manage.py classify_docs_for_rag --dry-run  # Preview changes
```

### Changes to `core/services/scoped_retrieval.py`
Added dual-channel retrieval methods:
- `get_critical_docs()` - Always-include critical documents
- `get_incident_docs()` - Recent incident reports/postmortems
- `get_audit_findings_context()` - Open P0/P1 audit findings
- `dual_channel_search()` - Combines semantic + critical + incident channels

---

## Phase 2 (P1): RESERVED Budget Tier + Agent Router Integration

**PR #921**

### Changes to `core/services/context_budget_manager.py`
Added RESERVED priority level:
```python
class SectionPriority(Enum):
    CRITICAL = 1  # Never truncate, never skip
    RESERVED = 2  # Session 949: Protected risk-aware docs
    HIGH = 3      # Truncate if needed, never skip
    MEDIUM = 4    # Truncate or skip if budget exceeded
    LOW = 5       # Skip first when budget is tight
```

Added reserved budget sections:
```python
'critical_docs': SectionConfig(SectionPriority.RESERVED, 300),
'incident_docs': SectionConfig(SectionPriority.RESERVED, 200),
'audit_findings': SectionConfig(SectionPriority.RESERVED, 150),
```

Updated `enforce_budget()` to never cut RESERVED sections.

### Changes to `core/agent_router.py`
Added `_get_risk_aware_context()` method that:
- Calls `dual_channel_search()` from scoped_retrieval
- Formats critical docs, incidents, and findings as text
- Returns structured context for injection

Updated both `gather_context_for_agent()` and `route()` to:
- Call `_get_risk_aware_context()`
- Merge risk_context into spider_context
- Log risk context injection

---

## Phase 3 (P2): Risk-Aware Re-Ranking

**PR #922**

### Changes to `core/services/scoped_retrieval.py`

Added configurable boost values:
```python
risk_level_boosts = {
    'critical': 0.25,  # +25% boost
    'high': 0.15,      # +15% boost
    'medium': 0.0,     # No boost
    'low': -0.05,      # Slight penalty
}
document_class_boosts = {
    'postmortem': 0.20,       # +20% boost
    'incident_report': 0.15,  # +15% boost
    'security': 0.15,         # +15% boost
    'constraint': 0.10,       # +10% boost
    'architecture': 0.05,     # +5% boost
    'runbook': 0.05,          # +5% boost
    'changelog': 0.0,
    'reference': 0.0,
}
critical_doc_boost = 0.30  # is_critical=True gets +30%
```

Added new methods:
- `_calculate_risk_boost()` - Per-result boost calculation
- `_apply_risk_reranking()` - Re-sort by boosted scores
- `search_by_document_class()` - Filter by document class
- `get_postmortems()` - Convenience method
- `get_incident_reports()` - Convenience method
- `get_security_advisories()` - Convenience method
- `get_constraint_docs()` - Convenience method
- `get_high_risk_docs()` - Convenience method

Updated `_semantic_search()` and `_keyword_search()` to:
- Fetch 2x results when re-ranking enabled
- Include risk metadata (is_critical, risk_level, document_class)
- Apply risk-aware re-ranking before returning

---

## Key Files Modified

| File | Purpose |
|------|---------|
| `content/models.py` | Added risk fields to Document model |
| `core/models_audit_tracking.py` | Added linked_document FK |
| `core/services/scoped_retrieval.py` | Dual-channel + re-ranking |
| `core/services/context_budget_manager.py` | RESERVED priority tier |
| `core/agent_router.py` | Risk context injection |
| `core/management/commands/classify_docs_for_rag.py` | **NEW** - Auto-classification |

---

## How It Works

1. **Document Classification**: Documents have `is_critical`, `risk_level`, and `document_class` fields
2. **Dual-Channel Retrieval**: Semantic search + critical docs + incident docs + audit findings
3. **Reserved Budget**: Critical/incident docs protected from token truncation
4. **Risk Re-Ranking**: Postmortems and incident reports rank higher even with lower similarity
5. **Agent Context**: All agents receive risk context in spider_context

---

## Testing

```bash
# Classify existing docs
python manage.py classify_docs_for_rag --dry-run

# Test dual-channel search
python manage.py shell
>>> from core.services.scoped_retrieval import get_scoped_retrieval_service
>>> service = get_scoped_retrieval_service()
>>> results = service.dual_channel_search("database migration")
>>> print(f"Critical: {len(results['critical_docs'])}")
>>> print(f"Incidents: {len(results['incident_docs'])}")
>>> print(f"Findings: {len(results['audit_findings'])}")

# Test document class filtering
>>> postmortems = service.get_postmortems()
>>> print(f"Found {len(postmortems)} postmortems")
```

---

## Future Enhancements

- Add incident_date tracking for time-based incident retrieval
- Create UI for marking documents as critical
- Add learning from which critical docs are actually used
- Consider query-specific boost adjustments
