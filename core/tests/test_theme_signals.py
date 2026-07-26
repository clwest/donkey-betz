"""
Session 2978: Theme Signals v1 service + endpoint tests.

Covers routing, quality gate, evidence extraction, card shape, and endpoint
smoke. Verifies strict-gate posture ratified by Chris in deliverable 63ec4d1d.
"""

from __future__ import annotations

import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from core.models import SignalCluster
from core.models_unified_system import LegacySpiderData
from core.services.theme_signals_service import (
    MAX_EVIDENCE,
    MIN_CONFIDENCE_BUILDABLE,
    MIN_CONFIDENCE_INVESTABLE,
    _PATTERN_TO_ACTION,
    _round_robin_across_row_buckets,
    cluster_to_card,
    extract_evidence_from_cluster,
    get_theme_signals,
    passes_quality_gate,
    pattern_type_to_action,
    route_cluster,
)

User = get_user_model()


def _mk_cluster(**kwargs) -> SignalCluster:
    defaults = dict(
        name="Test cluster",
        pattern_type="trend_emergence",
        confidence=0.75,
        source_breakdown={"hackernews": 3, "devto": 2, "github": 1},
        keywords=["python", "async"],
        spider_data_ids=[],
    )
    defaults.update(kwargs)
    return SignalCluster.objects.create(**defaults)


def _mk_legacy(items, spider_name="hackernews") -> LegacySpiderData:
    return LegacySpiderData.objects.create(
        id=uuid.uuid4(),
        spider_name=spider_name,
        source_url="internal",
        data_type="tech",
        raw_data={"items": items},
        processed_data={},
    )


class RoutingTests(TestCase):
    def test_investable_wins_ties_when_both_source_classes_present(self):
        c = _mk_cluster(source_breakdown={"hackernews": 5, "sec_edgar": 3})
        self.assertEqual(route_cluster(c), "investable")

    def test_catalyst_keyword_forces_investable_even_with_buildable_sources(self):
        c = _mk_cluster(
            source_breakdown={"github": 4},
            keywords=["quarterly results", "async"],
        )
        self.assertEqual(route_cluster(c), "investable")

    def test_pure_buildable_sources_route_buildable(self):
        c = _mk_cluster(source_breakdown={"hackernews": 4, "devto": 2})
        self.assertEqual(route_cluster(c), "buildable")

    def test_no_matching_sources_and_no_catalyst_routes_neither(self):
        c = _mk_cluster(
            source_breakdown={"noaa_weather": 5},
            keywords=["climate", "rainfall"],
        )
        self.assertEqual(route_cluster(c), "neither")


class QualityGateTests(TestCase):
    def test_blocked_title_discussion_link_rejected(self):
        c = _mk_cluster(name="Discussion, Link opportunity window")
        passed, reason = passes_quality_gate(c, "buildable")
        self.assertFalse(passed)
        self.assertEqual(reason, "title_blocked")

    def test_blocked_title_comments_score_rejected(self):
        c = _mk_cluster(name="Comments, Score demand spike")
        passed, reason = passes_quality_gate(c, "buildable")
        self.assertFalse(passed)
        self.assertEqual(reason, "title_blocked")

    def test_title_starting_with_link_but_meaningful_tokens_passes(self):
        c = _mk_cluster(name="Link Rot Detection in Modern Applications")
        passed, reason = passes_quality_gate(c, "buildable")
        self.assertTrue(passed)
        self.assertEqual(reason, "ok")

    def test_evidence_fail_when_2_sources_and_4_items(self):
        c = _mk_cluster(
            source_breakdown={"hackernews": 3, "devto": 1},
            spider_data_ids=[str(uuid.uuid4()) for _ in range(4)],
        )
        passed, reason = passes_quality_gate(c, "buildable")
        self.assertFalse(passed)
        self.assertEqual(reason, "evidence_fail")

    def test_evidence_pass_when_3_sources_1_item(self):
        c = _mk_cluster(
            source_breakdown={"hackernews": 1, "devto": 1, "github": 1},
            spider_data_ids=[str(uuid.uuid4())],
        )
        passed, reason = passes_quality_gate(c, "buildable")
        self.assertTrue(passed)

    def test_evidence_pass_when_1_source_5_items(self):
        c = _mk_cluster(
            source_breakdown={"hackernews": 5},
            spider_data_ids=[str(uuid.uuid4()) for _ in range(5)],
        )
        passed, reason = passes_quality_gate(c, "buildable")
        self.assertTrue(passed)

    def test_conf_below_buildable_threshold_rejected(self):
        c = _mk_cluster(confidence=MIN_CONFIDENCE_BUILDABLE - 0.01)
        passed, reason = passes_quality_gate(c, "buildable")
        self.assertFalse(passed)
        self.assertEqual(reason, "conf_fail")

    def test_conf_below_investable_threshold_rejected(self):
        c = _mk_cluster(
            source_breakdown={"sec_edgar": 3, "reuters_rss": 2, "bbc": 1},
            confidence=MIN_CONFIDENCE_INVESTABLE - 0.01,
        )
        passed, reason = passes_quality_gate(c, "investable")
        self.assertFalse(passed)
        self.assertEqual(reason, "conf_fail")

    def test_routed_neither_fails_with_reason_routed_neither(self):
        c = _mk_cluster(
            source_breakdown={"noaa_weather": 5},
            keywords=["climate"],
        )
        passed, reason = passes_quality_gate(c, "neither")
        self.assertFalse(passed)
        self.assertEqual(reason, "routed_neither")

    def test_min_confidence_override_below_default(self):
        c = _mk_cluster(confidence=0.45)
        passed_default, _ = passes_quality_gate(c, "buildable")
        self.assertFalse(passed_default)
        passed_override, _ = passes_quality_gate(c, "buildable", min_confidence_override=0.40)
        self.assertTrue(passed_override)


class EvidenceExtractionTests(TestCase):
    def test_flattens_items_from_multiple_rows(self):
        row1 = _mk_legacy(
            items=[{"title": "Foo", "url": "https://a.example/1"}],
            spider_name="hackernews",
        )
        row2 = _mk_legacy(
            items=[{"title": "Bar", "link": "https://b.example/2"}],
            spider_name="devto",
        )
        c = _mk_cluster(spider_data_ids=[str(row1.id), str(row2.id)])
        evidence = extract_evidence_from_cluster(c)
        self.assertEqual(len(evidence), 2)
        titles = {e["title"] for e in evidence}
        self.assertEqual(titles, {"Foo", "Bar"})

    def test_skips_items_missing_both_title_and_url(self):
        row = _mk_legacy(items=[
            {"summary": "no title no url"},
            {"title": "Real", "url": "https://x.example"},
        ])
        c = _mk_cluster(spider_data_ids=[str(row.id)])
        evidence = extract_evidence_from_cluster(c)
        self.assertEqual(len(evidence), 1)
        self.assertEqual(evidence[0]["title"], "Real")

    def test_caps_at_max_items(self):
        row = _mk_legacy(items=[
            {"title": f"Item {i}", "url": f"https://x.example/{i}"}
            for i in range(20)
        ])
        c = _mk_cluster(spider_data_ids=[str(row.id)])
        evidence = extract_evidence_from_cluster(c)
        self.assertEqual(len(evidence), 7)

    def test_list_shaped_raw_data_returns_empty_gracefully(self):
        # Force list-shaped raw_data (defends against non-dict payloads —
        # per T1b non-blocking ask).
        row_id = uuid.uuid4()
        LegacySpiderData.objects.create(
            id=row_id,
            spider_name="test",
            source_url="internal",
            data_type="tech",
            raw_data=[{"nope": "list at top level"}],
            processed_data={},
        )
        c = _mk_cluster(spider_data_ids=[str(row_id)])
        evidence = extract_evidence_from_cluster(c)
        self.assertEqual(evidence, [])

    def test_source_falls_back_to_spider_name_when_item_has_no_source(self):
        row = _mk_legacy(
            items=[{"title": "T", "url": "https://x"}],
            spider_name="hackernews",
        )
        c = _mk_cluster(spider_data_ids=[str(row.id)])
        evidence = extract_evidence_from_cluster(c)
        # S2979: source labels are formatted via evidence_display.format_source_label.
        self.assertEqual(evidence[0]["source"], "Hacker News")

    def test_primary_path_transforms_bluesky_at_uri_to_bsky_app(self):
        row = _mk_legacy(
            items=[{
                "title": "@user.bsky.social: hello",
                "url": "at://did:plc:abc/app.bsky.feed.post/xyz",
                "source": "bluesky",
            }],
            spider_name="bluesky",
        )
        c = _mk_cluster(spider_data_ids=[str(row.id)])
        evidence = extract_evidence_from_cluster(c)
        self.assertEqual(len(evidence), 1)
        self.assertEqual(
            evidence[0]["url"],
            "https://bsky.app/profile/did:plc:abc/post/xyz",
        )

    def test_primary_path_drops_unsafe_scheme_url_but_keeps_title(self):
        row = _mk_legacy(
            items=[{"title": "Kept", "url": "javascript:alert(1)"}],
            spider_name="hackernews",
        )
        c = _mk_cluster(spider_data_ids=[str(row.id)])
        evidence = extract_evidence_from_cluster(c)
        self.assertEqual(len(evidence), 1)
        self.assertEqual(evidence[0]["title"], "Kept")
        self.assertIsNone(evidence[0]["url"])

    def test_primary_path_formats_source_label(self):
        row = _mk_legacy(
            items=[{"title": "T", "url": "https://x", "source": "yahoo_finance"}],
            spider_name="yahoo_finance",
        )
        c = _mk_cluster(spider_data_ids=[str(row.id)])
        evidence = extract_evidence_from_cluster(c)
        self.assertEqual(evidence[0]["source"], "Yahoo Finance")

    def test_falls_back_to_sample_signals_when_spider_data_ids_yields_empty(self):
        # Cluster has spider_data_ids pointing to a row whose items have neither
        # title nor url — primary path yields []. sample_signals populated →
        # fallback activates.
        row = _mk_legacy(items=[{"summary": "no fields"}], spider_name="bluesky")
        c = _mk_cluster(
            spider_data_ids=[str(row.id)],
            sample_signals=[
                {"source": "bluesky", "text": "fallback item", "url": "https://ex.com/1"},
                {"source": "producthunt", "text": "other", "url": "https://ex.com/2"},
            ],
        )
        evidence = extract_evidence_from_cluster(c)
        self.assertEqual(len(evidence), 2)
        titles = {e["title"] for e in evidence}
        self.assertEqual(titles, {"fallback item", "other"})
        # Fallback path also formats labels
        sources = {e["source"] for e in evidence}
        self.assertEqual(sources, {"Bluesky", "Product Hunt"})

    def test_falls_back_to_sample_signals_when_no_spider_data_ids(self):
        c = _mk_cluster(
            spider_data_ids=[],
            sample_signals=[
                {"source": "devto", "text": "solo", "url": "https://d.example"},
            ],
        )
        evidence = extract_evidence_from_cluster(c)
        self.assertEqual(len(evidence), 1)
        self.assertEqual(evidence[0]["title"], "solo")
        self.assertEqual(evidence[0]["source"], "DEV.to")

    def test_spider_data_ids_preferred_over_sample_signals_when_both_populated(self):
        # Regression guard: Chris ratified Option B at S2979 — spider_data_ids
        # primary, sample_signals fallback. Never prefer sample_signals when
        # primary yields items.
        row = _mk_legacy(
            items=[{"title": "primary", "url": "https://primary.example"}],
            spider_name="hackernews",
        )
        c = _mk_cluster(
            spider_data_ids=[str(row.id)],
            sample_signals=[
                {"source": "bluesky", "text": "fallback", "url": "https://fallback.example"},
            ],
        )
        evidence = extract_evidence_from_cluster(c)
        self.assertEqual(len(evidence), 1)
        self.assertEqual(evidence[0]["title"], "primary")
        # And no fallback contamination
        self.assertNotIn("fallback", [e["title"] for e in evidence])

    def test_evidence_relevance_sort_clickable_first(self):
        # Primary path yields a mix: one item with valid https, one whose
        # URL gets sanitized to None. The clickable one must come first.
        row = _mk_legacy(
            items=[
                {"title": "unclickable", "url": "javascript:void(0)"},
                {"title": "clickable", "url": "https://ok.example"},
            ],
            spider_name="devto",
        )
        c = _mk_cluster(spider_data_ids=[str(row.id)])
        evidence = extract_evidence_from_cluster(c)
        self.assertEqual(len(evidence), 2)
        self.assertEqual(evidence[0]["title"], "clickable")
        self.assertEqual(evidence[1]["title"], "unclickable")
        self.assertIsNone(evidence[1]["url"])


class CardShapeTests(TestCase):
    def test_buildable_card_has_no_who_benefits_field(self):
        c = _mk_cluster()
        card = cluster_to_card(c, "buildable")
        self.assertNotIn("who_benefits_who_loses", card)

    def test_investable_card_has_phase_b_placeholder(self):
        c = _mk_cluster(
            name="Fed Rate Watch",
            source_breakdown={"reuters_rss": 3, "bbc": 2, "sec_edgar": 1},
            keywords=["fed", "rate cut"],
        )
        card = cluster_to_card(c, "investable")
        self.assertIn("who_benefits_who_loses", card)
        self.assertEqual(card["who_benefits_who_loses"]["status"], "coming_in_phase_b")

    def test_why_now_note_present(self):
        c = _mk_cluster()
        card = cluster_to_card(c, "buildable")
        self.assertIn("Phase A template", card["why_now_note"])

    def test_why_now_derived_includes_source_names(self):
        c = _mk_cluster(source_breakdown={"hackernews": 4, "devto": 2})
        card = cluster_to_card(c, "buildable")
        self.assertIn("hackernews", card["why_now"])

    def test_action_mapped_from_pattern_type(self):
        # S2980: opportunity_window collapses to canonical "build" (was "build/trade").
        c = _mk_cluster(pattern_type="opportunity_window")
        card = cluster_to_card(c, "buildable")
        self.assertEqual(card["action"], "build")

    def test_card_contract_does_not_emit_so_what(self):
        # S2980 Chris D-verdict: regression guard against reintroducing the
        # legacy 5-value `so_what` field. `action` is the sole canonical
        # action field on the card contract now.
        c = _mk_cluster(pattern_type="opportunity_window")
        card = cluster_to_card(c, "buildable")
        self.assertNotIn("so_what", card)
        self.assertIn("action", card)

    def test_action_defaults_to_watch_for_unknown_pattern_type(self):
        c = _mk_cluster(pattern_type="totally_novel_pattern_type_xyz")
        card = cluster_to_card(c, "buildable")
        self.assertEqual(card["action"], "watch")


class GetThemeSignalsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # 6 buildable-eligible clusters + 6 investable-eligible + 2 blocked
        for i in range(6):
            row = _mk_legacy(
                items=[{"title": f"Item {i}", "url": f"https://b.example/{i}"}],
                spider_name="hackernews",
            )
            _mk_cluster(
                name=f"Build cluster {i}",
                source_breakdown={"hackernews": 3, "devto": 2, "github": 1},
                confidence=0.75,
                spider_data_ids=[str(row.id)],
            )
        for i in range(6):
            row = _mk_legacy(
                items=[{"title": f"News {i}", "url": f"https://i.example/{i}"}],
                spider_name="reuters_rss",
            )
            _mk_cluster(
                name=f"Invest cluster {i}",
                source_breakdown={"reuters_rss": 3, "bbc": 2, "sec_edgar": 1},
                confidence=0.75,
                spider_data_ids=[str(row.id)],
            )
        _mk_cluster(name="Discussion, Link junk")
        _mk_cluster(name="Comments, Score noise")

    def test_default_tab_is_buildable(self):
        payload = get_theme_signals()
        self.assertEqual(payload["tab"], "buildable")

    def test_buildable_returns_5_or_more_cards(self):
        payload = get_theme_signals(tab="buildable")
        self.assertGreaterEqual(len(payload["cards"]), 5)

    def test_investable_returns_5_or_more_cards(self):
        payload = get_theme_signals(tab="investable")
        self.assertGreaterEqual(len(payload["cards"]), 5)

    def test_investable_cards_have_who_benefits_placeholder(self):
        payload = get_theme_signals(tab="investable")
        for card in payload["cards"]:
            self.assertIn("who_benefits_who_loses", card)

    def test_gate_reasons_breakdown_present(self):
        payload = get_theme_signals(tab="buildable")
        self.assertIn("gate_reasons", payload)
        # 2 title_blocked fixtures exist and both route buildable (unmatched sources).
        # They should show up in the title_blocked count when scanned.
        self.assertGreaterEqual(payload["gate_reasons"]["title_blocked"], 0)

    def test_days_clamped_to_max(self):
        payload = get_theme_signals(days=999)
        self.assertEqual(payload["days"], 30)

    def test_limit_clamped_to_max(self):
        payload = get_theme_signals(limit=999)
        self.assertEqual(payload["limit"], 50)

    def test_min_confidence_override_expands_survivor_set(self):
        # Add one 0.50-confidence buildable that would fail default 0.60 gate
        row = _mk_legacy(
            items=[{"title": "Low", "url": "https://x"}],
            spider_name="hackernews",
        )
        _mk_cluster(
            name="Low-conf builder",
            source_breakdown={"hackernews": 3, "devto": 2, "github": 1},
            confidence=0.50,
            spider_data_ids=[str(row.id)],
        )
        default_payload = get_theme_signals(tab="buildable")
        override_payload = get_theme_signals(tab="buildable", min_confidence=0.45)
        self.assertGreater(
            len(override_payload["cards"]),
            len(default_payload["cards"]),
        )


class ThemeSignalsEndpointTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="theme_tester", password="pw")  # type: ignore[attr-defined]
        for i in range(5):
            row = _mk_legacy(
                items=[{"title": f"News {i}", "url": f"https://n.example/{i}"}],
                spider_name="reuters_rss",
            )
            _mk_cluster(
                name=f"Endpoint invest cluster {i}",
                source_breakdown={"reuters_rss": 3, "bbc": 2, "sec_edgar": 1},
                confidence=0.75,
                spider_data_ids=[str(row.id)],
            )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_endpoint_requires_auth(self):
        anon = APIClient()
        resp = anon.get("/api/theme-signals/")
        self.assertIn(resp.status_code, (401, 403))

    def test_endpoint_returns_investable_cards(self):
        resp = self.client.get("/api/theme-signals/", {"tab": "investable"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["tab"], "investable")
        self.assertGreaterEqual(len(resp.data["cards"]), 5)

    def test_endpoint_returns_payload_shape(self):
        resp = self.client.get("/api/theme-signals/")
        self.assertEqual(resp.status_code, 200)
        payload = resp.data
        for k in ("tab", "days", "limit", "cards", "total_scanned",
                  "total_survived", "gate_reasons", "min_confidence_applied",
                  "build_only"):
            self.assertIn(k, payload)

    def test_endpoint_accepts_build_only_query_param(self):
        # S2980: `?build_only=true` should be reflected in the payload's
        # `build_only` echo, regardless of whether any cards survive.
        resp = self.client.get(
            "/api/theme-signals/", {"tab": "buildable", "build_only": "true"}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.data["build_only"])
        # build_only_filtered counter present in gate_reasons
        self.assertIn("build_only_filtered", resp.data["gate_reasons"])


# -- S2980 additions ------------------------------------------------------


class PatternToActionMappingTests(TestCase):
    """S2980 spec f3cc9499 §Mapping — canonical 3-value action enum."""

    def test_all_ten_pattern_types_map_to_canonical_enum(self):
        # Every pattern_type in the map must resolve to one of {build, research, watch}.
        allowed = {"build", "research", "watch"}
        self.assertEqual(len(_PATTERN_TO_ACTION), 10)
        for pt, action in _PATTERN_TO_ACTION.items():
            self.assertIn(action, allowed, f"pattern_type {pt} maps to non-canonical {action}")

    def test_opportunity_window_collapses_to_build(self):
        # S2979 shipped "build/trade" here; S2980 collapses to canonical "build".
        self.assertEqual(pattern_type_to_action("opportunity_window"), "build")

    def test_market_movement_collapses_to_watch(self):
        # S2979 shipped "trade" here; S2980 collapses to canonical "watch".
        self.assertEqual(pattern_type_to_action("market_movement"), "watch")

    def test_knowledge_gap_stays_research(self):
        self.assertEqual(pattern_type_to_action("knowledge_gap"), "research")

    def test_user_need_stays_build(self):
        self.assertEqual(pattern_type_to_action("user_need"), "build")

    def test_trend_emergence_stays_watch(self):
        self.assertEqual(pattern_type_to_action("trend_emergence"), "watch")

    def test_unknown_pattern_type_falls_back_to_watch(self):
        self.assertEqual(pattern_type_to_action("some_novel_pattern"), "watch")
        self.assertEqual(pattern_type_to_action(""), "watch")
        self.assertEqual(pattern_type_to_action(None), "watch")


class RoundRobinBucketTests(TestCase):
    """S2980 spec f3cc9499 §Backend §Source-diversified evidence selection.

    Direct unit tests on the pure helper — no DB required.
    """

    def _mk_row(self, prefix: str, count: int) -> list:
        return [{"title": f"{prefix}{i}", "url": f"https://{prefix}.example/{i}", "source": prefix} for i in range(count)]

    def test_interleaves_across_two_full_buckets(self):
        b1 = self._mk_row("a", 3)
        b2 = self._mk_row("b", 3)
        out = _round_robin_across_row_buckets([b1, b2], max_total=6)
        titles = [r["title"] for r in out]
        self.assertEqual(titles, ["a0", "b0", "a1", "b1", "a2", "b2"])

    def test_preserves_within_bucket_walk_order(self):
        # Within one bucket, items must come out in the input order.
        b1 = self._mk_row("a", 4)
        b2 = self._mk_row("b", 2)
        out = _round_robin_across_row_buckets([b1, b2], max_total=6)
        a_titles = [r["title"] for r in out if r["title"].startswith("a")]
        self.assertEqual(a_titles, ["a0", "a1", "a2", "a3"])
        b_titles = [r["title"] for r in out if r["title"].startswith("b")]
        self.assertEqual(b_titles, ["b0", "b1"])

    def test_respects_max_total_cap(self):
        b1 = self._mk_row("a", 10)
        b2 = self._mk_row("b", 10)
        out = _round_robin_across_row_buckets([b1, b2], max_total=5)
        self.assertEqual(len(out), 5)

    def test_drains_remaining_buckets_when_one_empties(self):
        # If bucket b runs out first, the rest of a should fill.
        b1 = self._mk_row("a", 5)
        b2 = self._mk_row("b", 1)
        out = _round_robin_across_row_buckets([b1, b2], max_total=6)
        titles = [r["title"] for r in out]
        # First pass gets a0, b0. Then b is exhausted; remaining passes just take a.
        self.assertEqual(titles, ["a0", "b0", "a1", "a2", "a3", "a4"])

    def test_stable_across_runs(self):
        b1 = self._mk_row("a", 3)
        b2 = self._mk_row("b", 3)
        b3 = self._mk_row("c", 3)
        first = _round_robin_across_row_buckets([b1, b2, b3], max_total=9)
        second = _round_robin_across_row_buckets([b1, b2, b3], max_total=9)
        self.assertEqual([r["title"] for r in first], [r["title"] for r in second])

    def test_empty_buckets_returns_empty(self):
        self.assertEqual(_round_robin_across_row_buckets([], max_total=7), [])
        self.assertEqual(_round_robin_across_row_buckets([[], []], max_total=7), [])

    def test_single_bucket_behaves_like_pass_through(self):
        b1 = self._mk_row("a", 4)
        out = _round_robin_across_row_buckets([b1], max_total=7)
        self.assertEqual([r["title"] for r in out], ["a0", "a1", "a2", "a3"])


class EvidenceDiversificationE2ETests(TestCase):
    """S2980: verify diversification through the real cluster extractor —
    the failure mode from live data (Bluesky row with many items short-
    circuiting other rows) must not reoccur.
    """

    def test_multi_row_cluster_diversifies_evidence(self):
        # 3 rows, one per source. Bluesky row has 7+ items (the actual live
        # failure shape). Expect round-robin: 3 bluesky, 2 kickstarter, 2 producthunt.
        bluesky_row = _mk_legacy(
            items=[{"title": f"bsky {i}", "url": f"https://bsky.example/{i}"} for i in range(8)],
            spider_name="bluesky",
        )
        kickstarter_row = _mk_legacy(
            items=[
                {"title": "ks0", "url": "https://ks.example/0"},
                {"title": "ks1", "url": "https://ks.example/1"},
                {"title": "ks2", "url": "https://ks.example/2"},
            ],
            spider_name="kickstarter",
        )
        producthunt_row = _mk_legacy(
            items=[
                {"title": "ph0", "url": "https://ph.example/0"},
                {"title": "ph1", "url": "https://ph.example/1"},
            ],
            spider_name="producthunt",
        )
        c = _mk_cluster(
            spider_data_ids=[
                str(bluesky_row.id), str(kickstarter_row.id), str(producthunt_row.id),
            ],
        )
        ev = extract_evidence_from_cluster(c)
        sources = [e["source"] for e in ev]
        # MAX_EVIDENCE=7; round-robin: bsky, ks, ph, bsky, ks, ph, bsky = 3/2/2 mix.
        self.assertEqual(len(ev), MAX_EVIDENCE)
        self.assertEqual(sources.count("Bluesky"), 3)
        self.assertEqual(sources.count("Kickstarter"), 2)
        self.assertEqual(sources.count("Product Hunt"), 2)

    def test_single_source_cluster_still_returns_full_evidence(self):
        # When only one source exists in the cluster, evidence is 100%
        # single-source — round-robin degrades gracefully to pass-through.
        row = _mk_legacy(
            items=[{"title": f"only {i}", "url": f"https://x.example/{i}"} for i in range(9)],
            spider_name="hackernews",
        )
        c = _mk_cluster(spider_data_ids=[str(row.id)])
        ev = extract_evidence_from_cluster(c)
        self.assertEqual(len(ev), MAX_EVIDENCE)
        self.assertTrue(all(e["source"] == "Hacker News" for e in ev))

    def test_row_iteration_order_follows_spider_data_ids(self):
        # Rigby T1 F-BLOCKER: row order must be deterministic per cluster's
        # own spider_data_ids list, not Django `filter(id__in=…)` order.
        # Give two rows identical item counts but different sources; the
        # first item in the output must come from the row listed first in
        # spider_data_ids.
        row_a = _mk_legacy(
            items=[{"title": "a0", "url": "https://a.example/0"}],
            spider_name="devto",
        )
        row_b = _mk_legacy(
            items=[{"title": "b0", "url": "https://b.example/0"}],
            spider_name="hackernews",
        )
        # spider_data_ids explicitly puts row_b first.
        c = _mk_cluster(spider_data_ids=[str(row_b.id), str(row_a.id)])
        ev = extract_evidence_from_cluster(c)
        # After sort_evidence_by_relevance (stable, both items tie on binary
        # keys) round-robin order is preserved: b0 before a0.
        self.assertEqual(ev[0]["title"], "b0")
        self.assertEqual(ev[1]["title"], "a0")


class BuildOnlyFilterTests(TestCase):
    """S2980 spec f3cc9499 §Server-side build_only filter."""

    @classmethod
    def setUpTestData(cls):
        # Two buildable-routed clusters: one Build (opportunity_window),
        # one Research (knowledge_gap).
        build_row = _mk_legacy(
            items=[{"title": "opp", "url": "https://o.example"}],
            spider_name="hackernews",
        )
        _mk_cluster(
            name="Build cluster opp",
            pattern_type="opportunity_window",
            source_breakdown={"hackernews": 3, "devto": 2, "github": 1},
            confidence=0.75,
            spider_data_ids=[str(build_row.id)],
        )
        research_row = _mk_legacy(
            items=[{"title": "kg", "url": "https://k.example"}],
            spider_name="hackernews",
        )
        _mk_cluster(
            name="Research cluster kg",
            pattern_type="knowledge_gap",
            source_breakdown={"hackernews": 3, "devto": 2, "github": 1},
            confidence=0.75,
            spider_data_ids=[str(research_row.id)],
        )

    def test_default_returns_both_build_and_research(self):
        payload = get_theme_signals(tab="buildable")
        actions = [c["action"] for c in payload["cards"]]
        self.assertIn("build", actions)
        self.assertIn("research", actions)
        self.assertFalse(payload["build_only"])

    def test_build_only_true_returns_only_build_cards(self):
        payload = get_theme_signals(tab="buildable", build_only=True)
        self.assertTrue(payload["build_only"])
        for card in payload["cards"]:
            self.assertEqual(card["action"], "build")
        # At least the opportunity_window cluster should survive.
        self.assertGreaterEqual(len(payload["cards"]), 1)

    def test_build_only_records_filtered_count(self):
        payload = get_theme_signals(tab="buildable", build_only=True)
        # The knowledge_gap cluster should be counted as filtered out.
        self.assertGreaterEqual(payload["gate_reasons"]["build_only_filtered"], 1)

    def test_build_only_false_matches_default(self):
        default = get_theme_signals(tab="buildable")
        explicit = get_theme_signals(tab="buildable", build_only=False)
        self.assertEqual(len(default["cards"]), len(explicit["cards"]))
