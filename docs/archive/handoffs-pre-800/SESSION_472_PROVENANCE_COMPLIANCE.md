# Session 472: Market Intelligence Architecture - Phase 5 (Provenance & Compliance)

**Date:** December 17, 2025
**Status:** COMPLETE

---

## Overview

Built a comprehensive data lineage and compliance tracking system for the Market Intelligence Platform. This enables full audit trails, cryptographic integrity verification, and configurable compliance rules.

---

## What Was Built

### 1. Database Models (4 new models in `core/models_unified_system.py`)

#### DataProvenance
Tracks lineage through the Market Intelligence pipeline with blockchain-style hash chains.

```python
class DataProvenance(models.Model):
    id = models.UUIDField(primary_key=True)
    entity_type = models.CharField(choices=[
        'spider_data', 'opportunity', 'scoring_result',
        'validation_request', 'validation_decision', 'opportunity_outcome'
    ])
    entity_id = models.CharField()

    # Lineage tracking
    parent = models.ForeignKey('self', null=True, related_name='children')
    root = models.ForeignKey('self', null=True, related_name='descendants')
    depth = models.PositiveIntegerField(default=0)

    # Source attribution
    source_type = models.CharField(choices=[
        'spider', 'api', 'user_input', 'ml_prediction',
        'human_review', 'system'
    ])
    source_name = models.CharField()

    # Cryptographic integrity
    content_hash = models.CharField(max_length=64)  # SHA-256
    previous_hash = models.CharField(max_length=64)  # Blockchain-style chain

    # Compliance
    compliance_status = models.CharField(choices=[
        'compliant', 'warning', 'violation', 'pending'
    ])
    metadata = models.JSONField()
```

#### AuditLog
Immutable append-only audit trail for all system actions.

```python
class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True)
    action_type = models.CharField(choices=[
        'spider_crawl', 'opportunity_created', 'ml_score',
        'validation_queued', 'validation_approved', 'validation_rejected',
        'outcome_recorded', 'model_trained', 'compliance_check',
        'compliance_remediated', 'data_export'
    ])
    actor_type = models.CharField(choices=['user', 'agent', 'system', 'scheduler'])
    actor_id = models.CharField()
    target_type = models.CharField()
    target_id = models.CharField()
    timestamp = models.DateTimeField(auto_now_add=True)
    context = models.JSONField()  # Before/after state
```

#### ComplianceCheck
Records results of compliance rule evaluations.

```python
class ComplianceCheck(models.Model):
    provenance = models.ForeignKey(DataProvenance, related_name='compliance_checks')
    check_type = models.CharField(choices=[
        'data_freshness', 'source_attribution', 'confidence_threshold',
        'human_review_required', 'audit_completeness'
    ])
    passed = models.BooleanField()
    severity = models.CharField(choices=['critical', 'high', 'medium', 'low'])
    details = models.JSONField()
    remediation_required = models.BooleanField()
    remediated_at = models.DateTimeField(null=True)
```

#### ComplianceRule
Configurable compliance rule definitions.

```python
class ComplianceRule(models.Model):
    name = models.CharField(unique=True)
    check_type = models.CharField()
    entity_types = ArrayField(models.CharField())  # Which entities this applies to
    severity = models.CharField()
    blocking = models.BooleanField()  # Prevents progression if failed
    config = models.JSONField()  # Rule-specific configuration
    is_active = models.BooleanField(default=True)
```

---

### 2. ProvenanceTracker Service (`core/services/provenance_tracker.py`)

**~600 lines** - Core provenance tracking implementation.

#### Main Class: ProvenanceTracker

```python
class ProvenanceTracker:
    def create_provenance(
        self,
        entity_type: str,
        entity_id: str,
        source_type: str,
        source_name: str,
        metadata: Dict = None,
        parent_provenance_id: str = None,
        user=None
    ) -> ProvenanceResult

    def get_lineage(
        self,
        entity_type: str,
        entity_id: str
    ) -> LineageResult

    def get_descendants(
        self,
        provenance_id: str,
        max_depth: int = None
    ) -> List[Dict]

    def verify_integrity(
        self,
        provenance_id: str
    ) -> Dict[str, Any]

    def get_audit_trail(
        self,
        entity_type: str = None,
        entity_id: str = None,
        action_type: str = None,
        limit: int = 100
    ) -> List[Dict]

    def get_compliance_summary(
        self,
        entity_type: str = None
    ) -> Dict[str, Any]
```

#### Convenience Functions

```python
def create_spider_data_provenance(spider_data_id, spider_name, record_count, ...)
def create_opportunity_provenance(opportunity_id, spider_data_provenance_id, ...)
def create_scoring_provenance(scoring_id, opportunity_provenance_id, ml_score, ...)
def create_validation_provenance(validation_id, scoring_provenance_id, decision, ...)
def create_outcome_provenance(outcome_id, validation_provenance_id, outcome_type, ...)

def get_provenance_tracker() -> ProvenanceTracker  # Singleton
```

---

### 3. API Endpoints (11 new endpoints in `core/views_provenance.py`)

#### Data Lineage

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/mi/lineage/<entity_type>/<entity_id>/` | GET | Get lineage chain |
| `/api/mi/provenance/<provenance_id>/` | GET | Get provenance detail |
| `/api/mi/provenance/<provenance_id>/descendants/` | GET | Get all descendants |
| `/api/mi/provenance/<provenance_id>/verify/` | GET | Verify integrity |

#### Audit Trail

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/mi/audit/trail/` | GET | Query audit logs with filters |

#### Compliance

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/mi/compliance/summary/` | GET | Compliance statistics |
| `/api/mi/compliance/rules/` | GET | Active compliance rules |
| `/api/mi/compliance/issues/` | GET | Outstanding issues |
| `/api/mi/compliance/<check_id>/remediate/` | POST | Mark issue remediated |

#### Statistics

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/mi/provenance/stats/` | GET | Overall statistics |

---

### 4. Service Integrations

#### Scoring Dispatcher (`core/services/scoring_dispatcher.py`)
- Added `_create_scoring_provenance()` helper function
- Calls provenance creation after realtime scoring
- Calls provenance creation after batch scoring

#### HITL Validation (`core/services/hitl_validation.py`)
- Added `_create_validation_provenance()` helper function
- Calls provenance creation after human decisions
- Calls provenance creation after auto-approve/reject decisions

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     DATA LINEAGE PIPELINE                            │
└─────────────────────────────────────────────────────────────────────┘

Spider Data → Opportunity → Scoring → Validation → Decision → Outcome
    │              │            │           │           │          │
    ▼              ▼            ▼           ▼           ▼          ▼
┌───────────────────────────────────────────────────────────────────┐
│                    DataProvenance Records                          │
│  depth=0       depth=1      depth=2      depth=3     depth=4      │
│  parent=null   parent=↑     parent=↑     parent=↑    parent=↑     │
│  root=self     root=↑       root=↑       root=↑      root=↑       │
└───────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────────────┐
│                       AuditLog Entries                             │
│  spider_crawl → opportunity_created → ml_score → validation_*     │
└───────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────────────┐
│                     ComplianceCheck Records                        │
│  data_freshness │ source_attribution │ confidence_threshold       │
└───────────────────────────────────────────────────────────────────┘
```

---

## Cryptographic Integrity

### Content Hash
Each provenance record has a SHA-256 hash of its content:
```python
content_hash = hashlib.sha256(json.dumps({
    'entity_type': entity_type,
    'entity_id': entity_id,
    'source_type': source_type,
    'source_name': source_name,
    'metadata': metadata,
    'timestamp': timestamp,
}).encode()).hexdigest()
```

### Chain Hash (Blockchain-style)
Each record includes the parent's content hash:
```python
previous_hash = parent.content_hash if parent else '0' * 64
```

### Integrity Verification
Verify the entire chain hasn't been tampered with:
```python
result = tracker.verify_integrity(provenance_id)
# Returns: {'valid': True, 'records_checked': 4, 'issues': []}
```

---

## Compliance Rules

Default compliance rules that can be configured:

| Rule | Entity Types | Severity | Description |
|------|--------------|----------|-------------|
| Data Freshness | spider_data | warning | Data > 24 hours old |
| Source Attribution | all | high | Missing source name |
| Confidence Threshold | scoring_result | medium | Confidence < 50% |
| Human Review Required | validation_decision | critical | Auto-decision for high-value |

---

## Testing

```bash
# Test Provenance System
DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python -c "
import django; django.setup()
from core.models_unified_system import DataProvenance, AuditLog
from core.services.provenance_tracker import get_provenance_tracker, create_spider_data_provenance

# Create test provenance
result = create_spider_data_provenance(
    spider_data_id='test_123',
    spider_name='test_spider',
    record_count=10
)
print(f'Created: {result.provenance_id}')

# Verify
tracker = get_provenance_tracker()
integrity = tracker.verify_integrity(str(result.provenance_id))
print(f'Valid: {integrity[\"valid\"]}')
"
```

---

## Files Changed/Created

### Created
- `core/migrations/0104_session_472_provenance_compliance.py` - Migration
- `docs/handoffs/SESSION_472_PROVENANCE_COMPLIANCE.md` - This file

### Modified
- `core/models_unified_system.py` - Added 4 provenance models (~660 lines)
- `core/services/provenance_tracker.py` - Added tracker service (~600 lines)
- `core/views_provenance.py` - Added 11 MI provenance endpoints (~630 lines)
- `core/urls.py` - Added MI provenance URL routes
- `core/services/scoring_dispatcher.py` - Added provenance integration
- `core/services/hitl_validation.py` - Added provenance integration
- `00-START-NEXT-SESSION.md` - Updated for Session 473

---

## Phase 5 Complete!

Market Intelligence Platform: **5 of 6 phases complete**
- ✅ Phase 1: ML Scoring Engine (XGBoost + SHAP)
- ✅ Phase 2: Scoring Dispatcher (Realtime + Batch)
- ✅ Phase 3: HITL Validation (Auto-approve/reject + Queue)
- ✅ Phase 4: Event Bus (Redis Streams)
- ✅ Phase 5: Provenance & Compliance
- ⏳ Phase 6: ROI Metrics

---

## Next Steps (Session 473 Options)

1. **Phase 6: ROI Metrics** - Revenue attribution, conversion tracking
2. **Content Studio Linkage** - Connect provenance to content generation
3. **Narrative Integration** - Track narrative shift provenance
4. **Full Pipeline Test** - End-to-end provenance tracking test
