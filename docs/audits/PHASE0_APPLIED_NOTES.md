# Phase 0: Connectors Only - Applied Notes

**Session:** 960
**Date:** February 7, 2026
**Status:** Complete - All 22 tests passing

---

## Summary

Phase 0 adds lightweight connectors between existing subsystems without new
Django models, migrations, or rewrites. All changes are additive and
backward-compatible.

---

## Files Changed

| File | Phase | Changes |
|------|-------|---------|
| `core/agents/report_schemas.py` | 0.1, 0.3 | Added `source_type` + `content_hash` to `SourceInfo`; enriched `Claim` with `claim_id`, `source_ids`, `challenged_by`, `status`; `build_provenance()` accepts `internal_sources` (SourceInfo or dict) |
| `core/agents/base_agent.py` | 0.2 | Added `_docs_consumed` list to `__init__`, `get_docs_consumed()` method, instrumented `_read_doc()` with SHA-256 hashing and deduplication |
| `core/conversation_orchestrator.py` | 0.5 | Added fallback auto-trigger for `DecisionEnforcerAgent` when debate/planning/critique has no `decision_summary` (uses last 3 messages) |
| `core/services/unified_pa_entrypoint.py` | 0.6 | Added `strategic_memory` to `reasoning` intent enrichment; wired `LearningPatternEngine.get_patterns_for_agent()` into `_enrich_tool_result()`; added `STRATEGIC MEMORY` section label |
| `core/services/artifact_envelope.py` | 0.A-B | **NEW FILE** - `AgentOutputEnvelope` dataclass, `build_envelope()`, `validate_envelope()` with CitationGateService integration |
| `core/services/publish_gate.py` | 0.C | Added `_check_envelope()` method; integrated into `apply_to_blog()` to validate envelope if present in blog metadata |
| `core/tests/test_phase0_connectors.py` | 0.D | **NEW FILE** - 22 tests covering all Phase 0 connectors |

### No Changes Needed (Already Existed)

| File | Phase | Why |
|------|-------|-----|
| `core/contracts/research_contract.py` | 0.4 | Already has `to_dict()` at line 213 |
| `core/contracts/synthesis_contract.py` | 0.4 | Already has `to_dict()` at line 230 |
| `core/contracts/execution_mandate.py` | 0.4 | Already has `to_dict()` at line 242 |

---

## How to Test

```bash
# Run all Phase 0 tests
DJANGO_SETTINGS_MODULE=core.settings python -m pytest core/tests/test_phase0_connectors.py -v

# Quick smoke test - imports work
python -c "from core.services.artifact_envelope import build_envelope, validate_envelope; print('OK')"

# Verify contract round-trips
python -c "
from core.contracts.research_contract import ResearchContract, ResearchStatus
c = ResearchContract(goal='test', status=ResearchStatus.IN_PROGRESS, owner='x', confidence=0.5, confidence_reason='y')
print(c.to_dict()['goal'])
"
```

---

## Phase Details

### Phase 0.1: Extend Report Schemas
- `SourceInfo` now has `source_type` (internal_doc | external_api | spider_data | agent_memory | learning_pattern | user_input) and `content_hash` (SHA-256)
- `Claim` now has `claim_id`, `source_ids` (refs to sources), `challenged_by` (claim_ids), `status` (uncontested | challenged | refuted | verified)
- `to_markdown_block()` shows `[source_type]` tags for non-default sources

### Phase 0.2: Track Internal Doc Reads
- `BaseAgent.__init__` now initializes `self._docs_consumed = []`
- `BaseAgent.get_docs_consumed()` returns a copy of tracked docs
- `BaseAgent._read_doc()` appends a dict with `name`, `source_type`, `content_hash`, `record_count`, `freshness_hours`
- Deduplication by path + content hash prevents duplicate entries

### Phase 0.3: Merge Internal Doc Refs Into Provenance
- `build_provenance()` accepts `internal_sources` parameter
- Handles both `SourceInfo` objects and plain dicts (from `get_docs_consumed()`)
- Adds validation note: `"{N} internal doc(s) referenced"`

### Phase 0.4: Contract Serialization
- Already existed. All three contracts have `to_dict()` returning JSON-serializable dicts.
- Tests confirm round-trip serialization works.

### Phase 0.5: Auto-trigger DecisionEnforcer
- When `ENABLE_DECISION_ENFORCEMENT` is True and conversation_type is `debate`, `planning`, or `critique`, but no `decision_summary` was extracted:
  - Builds a fallback summary with the topic
  - Calls `_enforce_decision()` with last 3 messages
  - Logs as `[Session 960] Fallback decision enforced`
- Wrapped in try/except; failure doesn't affect conversation output

### Phase 0.6: Strategic Memory Enrichment
- Added `strategic_memory` to `INTENT_ENRICHMENT_MAP['reasoning']`
- Added `strategic_memory: 400` to `ENRICHMENT_CAPS`
- In `_enrich_tool_result()`, calls `get_learning_pattern_engine().get_patterns_for_agent('personal_assistant', message)`
- Extracts summary + best_practices into `STRATEGIC MEMORY` section
- Protected by `try/except ImportError` + outer exception handler

### Phase 0.A-B: AgentOutputEnvelope + Citation Validation
- New `core/services/artifact_envelope.py` with:
  - `AgentOutputEnvelope` dataclass (envelope_id, agent_name, content_hash, claims, internal_refs, paragraph_citations, citation_score, validation_passed)
  - `build_envelope()` - creates envelope with auto-generated claim IDs
  - `validate_envelope()` - validates claims, citation ratio, refuted claims; wires to CitationGateService
  - `from_dict()` for round-trip reconstruction

### Phase 0.C: PublishGate Integration
- Added `_check_envelope()` to `PublishGate` class
- Checks `blog.metadata.get('envelope')` for envelope data
- Validates via `validate_envelope()` and appends results to gate notes
- Non-blocking: if no envelope or validation fails, original gate behavior unchanged

### Phase 0.D: Tests
- 22 tests across 5 test classes
- `TestSourceInfoExtensions` (4 tests): source_type, content_hash, claim extensions
- `TestBuildProvenanceWithInternalSources` (3 tests): SourceInfo objects, dicts, no sources
- `TestContractSerialization` (3 tests): all 3 contracts round-trip
- `TestAgentOutputEnvelope` (9 tests): build, hash, round-trip, validation scenarios
- `TestDocReadTracking` (3 tests): init, tracking, deduplication

---

## Backward Compatibility

All changes are additive:
- New fields have defaults (source_type="external_api", content_hash=None, status="uncontested")
- `build_provenance()` internal_sources defaults to None
- `_check_envelope()` is a no-op when blog has no envelope metadata
- DecisionEnforcer fallback only fires for eligible conversation types with no existing summary
- Strategic memory enrichment silently skips if LearningPatternEngine is unavailable
