"""S2830 Step 1 — Smoke tests for the pointer-intent registry shape.

At Step 1 the mechanism classes are DORMANT (no search_embeddings
control-flow change). These tests verify the registry is well-formed:
protocol conformance, name uniqueness, drift_warn_prefix uniqueness,
and precedence ordering matches the current hardcoded
intent_gate_name precedence.

Ratified 2026-07-19 (S2830) via joint Claude+Rigby SIGN + Chris D-verdict.
Design: docs/research/discovery_layer/PHASE_0_5/POINTER_INTENT_REGISTRY_DESIGN.md
"""

from core.rag_integration import (
    INTENT_MECHANISMS,
    IntentMechanism,
    CountMechanism,
    SelfReferenceMechanism,
    LiteralFilenameMechanism,
)


def test_registry_is_nonempty_tuple():
    """Registry is a tuple of >= 1 mechanism instance."""
    assert isinstance(INTENT_MECHANISMS, tuple)
    assert len(INTENT_MECHANISMS) >= 1


def test_registry_ordering_matches_precedence():
    """Registry tuple order encodes intent_gate_name precedence.
    Current precedence (from search_embeddings :894-902):
      count > self_reference > literal_filename.
    Any registry re-ordering would silently change the precedence
    that search_embeddings hardcodes today — this test guards the
    invariant before Step 2 wires the registry into the composition
    loop.
    """
    names = [m.name for m in INTENT_MECHANISMS]
    assert names == ['count', 'self_reference', 'literal_filename'], (
        f"registry ordering broke precedence: got {names!r}, "
        "expected ['count', 'self_reference', 'literal_filename']"
    )


def test_all_mechanisms_implement_protocol():
    """Each registry entry is an IntentMechanism subclass and
    implements the required attributes + methods."""
    for mech in INTENT_MECHANISMS:
        assert isinstance(mech, IntentMechanism), (
            f"{type(mech).__name__} is not an IntentMechanism subclass"
        )
        # Required attributes
        assert mech.name, f"{type(mech).__name__}.name is empty"
        assert mech.drift_warn_prefix, (
            f"{type(mech).__name__}.drift_warn_prefix is empty"
        )
        # Required methods present (callable)
        for method_name in (
            'detect', 'injects_candidates', 'fetch_candidate_chunks',
            'bonus_and_diagnostics_for_row', 'default_diagnostic_fields',
            'canonical_target_paths', 'emit_drift_warn', 'emit_miss_log',
        ):
            assert callable(getattr(mech, method_name, None)), (
                f"{type(mech).__name__}.{method_name} not callable"
            )


def test_all_names_unique():
    """No two mechanisms share the same `name`. Duplicate names would
    break intent_gate_name precedence + registry dispatch."""
    names = [m.name for m in INTENT_MECHANISMS]
    assert len(names) == len(set(names)), (
        f"duplicate mechanism names in registry: {names!r}"
    )


def test_all_drift_warn_prefixes_unique():
    """No two mechanisms share the same drift_warn_prefix. Duplicates
    would collapse audit-trail attribution — a grep for
    [S2826_PATTERN_B_DRIFT] must match exactly one mechanism."""
    prefixes = [m.drift_warn_prefix for m in INTENT_MECHANISMS]
    assert len(prefixes) == len(set(prefixes)), (
        f"duplicate drift_warn_prefixes: {prefixes!r}"
    )


def test_default_fetch_returns_empty_list():
    """The base IntentMechanism.fetch_candidate_chunks returns []
    (Rigby SIGN Q2 refinement: non-injecting mechanisms inherit this;
    Pattern B does not override)."""
    # Pattern B is non-injecting and inherits the base default.
    count = CountMechanism()
    assert count.injects_candidates() is False
    # Registry MUST NOT call fetch on non-injecting mechanisms; if it
    # did (e.g. a Step-2 bug), the default no-op is a safe fallback.
    result = count.fetch_candidate_chunks(
        matches=True, base_qs=None, exclude_chunk_ids=set(),
        query_embedding=[],
    )
    assert result == []


def test_injecting_mechanisms_report_true():
    """Pattern C + D report injects_candidates() → True; Pattern B → False."""
    assert CountMechanism().injects_candidates() is False
    assert SelfReferenceMechanism().injects_candidates() is True
    assert LiteralFilenameMechanism().injects_candidates() is True


def test_default_diagnostic_fields_cover_all_named_keys():
    """Each mechanism's default_diagnostic_fields() dict contains
    all the diagnostic keys the mechanism emits in
    bonus_and_diagnostics_for_row when the gate fires. Ensures
    schema stability across responses (Rigby SIGN Q1 refinement:
    diagnostic keys must be present with default values on inactive
    rows, otherwise consumers keying by literal name see KeyError)."""
    # Pattern B
    b_defaults = CountMechanism().default_diagnostic_fields()
    assert 'count_intent_bonus' in b_defaults
    assert b_defaults['count_intent_bonus'] == 0.0

    # Pattern C — 4 field keys per current search_embeddings diagnostic block
    c_defaults = SelfReferenceMechanism().default_diagnostic_fields()
    for key in ('self_ref_intent_bonus', 'self_ref_anchor_key',
                'self_ref_matched_pattern_index', 'self_ref_injected'):
        assert key in c_defaults, f"Pattern C default missing {key!r}"

    # Pattern D — 5 field keys
    d_defaults = LiteralFilenameMechanism().default_diagnostic_fields()
    for key in ('literal_filename_intent_bonus',
                'literal_filename_anchor_key',
                'literal_filename_matched_pattern_index',
                'literal_filename_gate_name',
                'literal_filename_injected'):
        assert key in d_defaults, f"Pattern D default missing {key!r}"


def test_canonical_target_paths_populated():
    """Each mechanism reports at least one canonical target path
    (empty set on a mechanism today would mean drift-WARN is
    permanently no-op — flag as design bug via test)."""
    for mech in INTENT_MECHANISMS:
        targets = mech.canonical_target_paths()
        assert isinstance(targets, set)
        assert len(targets) >= 1, (
            f"{type(mech).__name__}.canonical_target_paths() empty; "
            "drift-WARN would be silently disabled"
        )


def test_pattern_b_targets_match_bonus_map():
    """Pattern B's canonical targets are the keys of _COUNT_INTENT_BONUS.
    Guards accidental divergence between the bonus source-of-truth
    and the drift-WARN target set."""
    from core.rag_integration import _COUNT_INTENT_BONUS
    b = CountMechanism()
    assert b.canonical_target_paths() == set(_COUNT_INTENT_BONUS.keys())


def test_pattern_c_targets_match_anchor_values():
    """Pattern C's canonical targets are the file_paths in _SELF_REFERENCE_ANCHORS."""
    from core.rag_integration import _SELF_REFERENCE_ANCHORS
    c = SelfReferenceMechanism()
    assert c.canonical_target_paths() == set(_SELF_REFERENCE_ANCHORS.values())


def test_pattern_d_targets_match_anchor_values():
    """Pattern D's canonical targets are the file_paths in _LITERAL_FILENAME_ANCHORS."""
    from core.rag_integration import _LITERAL_FILENAME_ANCHORS
    d = LiteralFilenameMechanism()
    assert d.canonical_target_paths() == set(_LITERAL_FILENAME_ANCHORS.values())


def test_registry_dormant_at_step_1():
    """Meta-assertion: at Step 1 the registry does NOT change
    search_embeddings runtime behavior. This is asserted by the
    parity harness (tests/regression/rag_registry_parity/) capturing
    unchanged observable-branch behavior. This smoke test is a
    reminder that any Step-1 PR modifying search_embeddings control
    flow is out-of-scope and requires reclassification as Step 2."""
    # Structural check: search_embeddings signature unchanged.
    # (We can't assert the internal control flow via inspection
    # alone; the parity harness catches behavior drift.)
    from core.rag_integration import search_embeddings
    import inspect
    sig = inspect.signature(search_embeddings)
    assert 'query' in sig.parameters
    assert 'limit' in sig.parameters
    assert 'similarity_threshold' in sig.parameters
    assert 'authority_weighted' in sig.parameters
