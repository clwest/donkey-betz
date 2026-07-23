"""Session 2898 Row B — integrity_null_spike_scan applicability rule.

Locks in the S2898 applicability filter on `DataIntegrityEngine.get_null_spike_scan`:
  - `processed_data` field is always skipped (verified dead field at HEAD 8709cb406:
    0/72 spiders with >=10 rows all-time ever populated it).
  - `embedding_text` field is skipped for (spider, data_type) pairs that have
    NEVER populated it historically; emitted for pairs that have.
  - `raw_data` field is never skipped (primary ingest payload).
  - Return dict exposes `applicability_skipped`, `applicability_skipped_by_field`,
    and `baseline_pairs_count` for operator visibility.
  - Each emitted spike carries an `applicability_reason` field (semantics-lock
    for future refactors — see Q3 edge case A).

Edge cases covered per Rigby SIGN S2898 Q3 (A–E):
  A. Mixed/partial historical population — pair with rare historical populate
     should still be applicable; all-null current window emits a spike.
  B. Low sample size — pair with total < 3 skipped by existing guard, and
     applicability_skipped does NOT double-count.
  C. Data_type migration mid-window — new (spider, typeNew) doesn't inherit
     applicability from (spider, typeOld).
  D. Empty historical baseline — degenerate case (no populated pairs) skips
     all embedding_text spikes without error.
  E. Query count — historical baseline query fires once per applicable field,
     not per (spider, data_type) pair.
"""

from django.test import TestCase

from core.models_unified_system import LegacySpiderData
from core.services.ops_autopilot.intelligence import DataIntegrityEngine


class NullSpikeApplicabilityTests(TestCase):
    """S2898 Row B — per-field applicability policy shapes."""

    def _mk(self, spider, data_type, raw=None, processed=None, embedding=None):
        return LegacySpiderData.objects.create(
            spider_name=spider,
            source_url='http://example.test',
            data_type=data_type,
            raw_data=raw if raw is not None else {'ok': True},
            processed_data=processed if processed is not None else {},
            embedding_text=embedding if embedding is not None else '',
        )

    def test_processed_data_always_skipped(self):
        """FIELD_APPLICABILITY.processed_data = 'never' → no spike ever emitted."""
        for _ in range(5):
            self._mk('spider_a', 'news', processed={})  # all empty

        scan = DataIntegrityEngine().get_null_spike_scan(hours=24)

        proc_spikes = [s for s in scan['spikes'] if s['field'] == 'processed_data']
        self.assertEqual(proc_spikes, [], "processed_data must never emit spikes")
        self.assertGreaterEqual(scan['applicability_skipped_by_field'].get('processed_data', 0), 1)

    def test_embedding_text_skipped_when_historically_empty(self):
        """Pair never populated embedding_text → skipped, no spike."""
        for _ in range(5):
            self._mk('spider_new', 'news', embedding='')  # never populated ever

        scan = DataIntegrityEngine().get_null_spike_scan(hours=24)

        emb_spikes = [s for s in scan['spikes'] if s['field'] == 'embedding_text']
        pair_spikes = [s for s in emb_spikes if s['spider'] == 'spider_new']
        self.assertEqual(pair_spikes, [],
                         "spider_new never populated embedding_text — no spike expected")
        self.assertGreaterEqual(scan['applicability_skipped_by_field'].get('embedding_text', 0), 1)

    def test_embedding_text_emitted_when_historically_populated_but_currently_null(self):
        """Edge case A — pair populated historically → emit spike on current all-null window."""
        # Historical populate (any row with non-empty embedding_text counts)
        self._mk('spider_hist', 'news', embedding='historical value')
        # Current window: 5 rows all with empty embedding
        for _ in range(5):
            self._mk('spider_hist', 'news', embedding='')

        scan = DataIntegrityEngine().get_null_spike_scan(hours=24)

        emb_pair = [s for s in scan['spikes']
                    if s['field'] == 'embedding_text' and s['spider'] == 'spider_hist']
        self.assertEqual(len(emb_pair), 1, "should emit exactly one spike for this pair")
        self.assertEqual(emb_pair[0]['applicability_reason'], 'historical_populated')
        self.assertGreater(emb_pair[0]['null_rate'], 0.3)

    def test_raw_data_never_skipped(self):
        """FIELD_APPLICABILITY.raw_data = 'always' → spike emitted on all-null."""
        for _ in range(5):
            self._mk('spider_raw', 'news', raw={})  # empty raw_data

        scan = DataIntegrityEngine().get_null_spike_scan(hours=24)

        raw_pair = [s for s in scan['spikes']
                    if s['field'] == 'raw_data' and s['spider'] == 'spider_raw']
        self.assertEqual(len(raw_pair), 1)
        self.assertEqual(raw_pair[0]['applicability_reason'], 'always')

    def test_applicability_count_in_return_and_no_double_count_for_low_sample(self):
        """Edge case B — total < 3 skipped by sample guard BEFORE applicability
        check; skipped counter must NOT increment for these rows."""
        # Only 2 rows for spider_small — should be skipped entirely by existing
        # `if total < 3: continue` guard, not counted in applicability_skipped.
        for _ in range(2):
            self._mk('spider_small', 'news', processed={})
        # And 5 rows for spider_normal to give applicability something to skip
        for _ in range(5):
            self._mk('spider_normal', 'news', processed={})

        scan = DataIntegrityEngine().get_null_spike_scan(hours=24)

        # spider_normal contributes 1 to processed_data skip (always) and 1 to
        # embedding_text skip (never populated). spider_small contributes 0.
        proc_skipped = scan['applicability_skipped_by_field'].get('processed_data', 0)
        emb_skipped = scan['applicability_skipped_by_field'].get('embedding_text', 0)
        # spider_small should NOT show up in either skip counter
        self.assertEqual(proc_skipped, 1,
                         "processed_data skip must count only sample-passing pairs")
        self.assertEqual(emb_skipped, 1,
                         "embedding_text skip must count only sample-passing pairs")
        self.assertEqual(
            scan['applicability_skipped'],
            proc_skipped + emb_skipped,
            "applicability_skipped is the sum of per-field skip counts",
        )

    def test_data_type_migration_does_not_leak_applicability(self):
        """Edge case C — (spider, typeNew) doesn't inherit applicability from
        (spider, typeOld). Baseline is (spider, data_type)-scoped, not spider-scoped."""
        # Old data_type populated historically
        self._mk('spider_mig', 'type_old', embedding='old populate')
        # New data_type: 5 rows in current window, all empty, never populated
        for _ in range(5):
            self._mk('spider_mig', 'type_new', embedding='')

        scan = DataIntegrityEngine().get_null_spike_scan(hours=24)

        new_pair_spikes = [
            s for s in scan['spikes']
            if s['field'] == 'embedding_text'
            and s['spider'] == 'spider_mig'
            and s['data_type'] == 'type_new'
        ]
        self.assertEqual(new_pair_spikes, [],
                         "(spider_mig, type_new) must not inherit applicability from type_old")

    def test_empty_historical_baseline_skips_all_embedding_spikes(self):
        """Edge case D — no rows in DB have populated embedding_text at all;
        baseline query returns empty set; all embedding spikes skipped without error."""
        # 5 rows for a spider with empty embedding — and no historical baseline anywhere
        for _ in range(5):
            self._mk('spider_fresh', 'news', embedding='')

        scan = DataIntegrityEngine().get_null_spike_scan(hours=24)

        self.assertEqual(scan['baseline_pairs_count'].get('embedding_text', -1), 0,
                         "baseline_pairs_count should be exactly 0 in degenerate case")
        emb_spikes = [s for s in scan['spikes'] if s['field'] == 'embedding_text']
        self.assertEqual(emb_spikes, [],
                         "all embedding_text spikes should be skipped when baseline is empty")

    def test_query_count_is_bounded(self):
        """Edge case E — historical baseline queries fire once per HISTORICAL_BASELINE
        field, not once per (spider, data_type) pair. Prevents accidental
        per-pair baseline query regression."""
        # Populate 5 distinct (spider, data_type) pairs, each with 5 rows
        for i in range(5):
            for _ in range(5):
                self._mk(f'spider_{i}', f'type_{i}', embedding='')

        # 1 baseline query (embedding_text is the only HISTORICAL_BASELINE field)
        # + 1 main aggregate query in get_null_spike_scan
        # + any Django auth/tenant middleware queries the test harness adds
        # Assert the baseline part scales O(1) in fields, not O(N) in pairs.
        engine = DataIntegrityEngine()
        with self.assertNumQueries(2):
            engine.get_null_spike_scan(hours=24)


class BaselineLookbackCapTests(TestCase):
    """S2899 Phase 2 (Ledger Row #29) — per-field baseline lookback cap.

    Locks in the shape of `FIELD_BASELINE_LOOKBACK_DAYS`:
      - default `None` preserves S2898 Phase 1 all-time semantics unchanged.
      - int N restricts the HISTORICAL_BASELINE baseline query to rows created
        in the last N days, letting stale populates decay out of the baseline.
      - `baseline_lookback_days` in the return dict surfaces the active setting
        per HISTORICAL_BASELINE field for operator visibility.
    """

    def _mk(self, spider, data_type, raw=None, processed=None, embedding=None):
        return LegacySpiderData.objects.create(
            spider_name=spider,
            source_url='http://example.test',
            data_type=data_type,
            raw_data=raw if raw is not None else {'ok': True},
            processed_data=processed if processed is not None else {},
            embedding_text=embedding if embedding is not None else '',
        )

    def _backdate(self, row, days_ago):
        """Set created_at N days in the past (bypasses auto_now_add)."""
        from django.utils import timezone as tz
        from datetime import timedelta
        LegacySpiderData.objects.filter(pk=row.pk).update(
            created_at=tz.now() - timedelta(days=days_ago),
        )

    def test_default_none_preserves_all_time_baseline_semantics(self):
        """Row #29: default `None` on class must behave identically to S2898 Phase 1."""
        # Historical populate 100 days ago (would fall outside a 30d cap)
        old = self._mk('spider_old', 'news', embedding='historical value')
        self._backdate(old, days_ago=100)
        # Current window: 5 rows all with empty embedding
        for _ in range(5):
            self._mk('spider_old', 'news', embedding='')

        scan = DataIntegrityEngine().get_null_spike_scan(hours=24)

        emb_pair = [s for s in scan['spikes']
                    if s['field'] == 'embedding_text' and s['spider'] == 'spider_old']
        self.assertEqual(len(emb_pair), 1,
                         "default None baseline must still see the 100d-old populate")
        self.assertEqual(emb_pair[0]['applicability_reason'], 'historical_populated')
        # And the return dict surfaces the setting
        self.assertIn('baseline_lookback_days', scan)
        self.assertEqual(scan['baseline_lookback_days'].get('embedding_text'), None)

    def test_lookback_cap_excludes_stale_populates(self):
        """Row #29: 30d cap must skip a pair whose only populate is 100d old."""
        # Same setup as above — pair's only populate is 100 days ago
        old = self._mk('spider_stale', 'news', embedding='historical value')
        self._backdate(old, days_ago=100)
        for _ in range(5):
            self._mk('spider_stale', 'news', embedding='')

        engine = DataIntegrityEngine()
        # Instance-level override — mirrors how an operator would tune the cap
        engine.FIELD_BASELINE_LOOKBACK_DAYS = {'embedding_text': 30}
        scan = engine.get_null_spike_scan(hours=24)

        emb_pair = [s for s in scan['spikes']
                    if s['field'] == 'embedding_text' and s['spider'] == 'spider_stale']
        self.assertEqual(emb_pair, [],
                         "30d cap must exclude the 100d-old populate from the baseline")
        # And the pair now shows up in the skip counter
        self.assertGreaterEqual(
            scan['applicability_skipped_by_field'].get('embedding_text', 0), 1,
        )
        # Return dict reflects the active cap
        self.assertEqual(scan['baseline_lookback_days'].get('embedding_text'), 30)

    def test_lookback_cap_keeps_recent_populates_in_baseline(self):
        """Row #29: 30d cap must preserve pairs with populates inside the window."""
        # Populate 10 days ago — inside a 30d cap
        recent = self._mk('spider_recent', 'news', embedding='recent value')
        self._backdate(recent, days_ago=10)
        # Current-window empties trigger the spike
        for _ in range(5):
            self._mk('spider_recent', 'news', embedding='')

        engine = DataIntegrityEngine()
        engine.FIELD_BASELINE_LOOKBACK_DAYS = {'embedding_text': 30}
        scan = engine.get_null_spike_scan(hours=24)

        emb_pair = [s for s in scan['spikes']
                    if s['field'] == 'embedding_text' and s['spider'] == 'spider_recent']
        self.assertEqual(len(emb_pair), 1,
                         "10d-old populate must remain inside a 30d cap")
        self.assertEqual(emb_pair[0]['applicability_reason'], 'historical_populated')
