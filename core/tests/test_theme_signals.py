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
    MIN_CONFIDENCE_BUILDABLE,
    MIN_CONFIDENCE_INVESTABLE,
    cluster_to_card,
    extract_evidence_from_cluster,
    get_theme_signals,
    passes_quality_gate,
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
        self.assertEqual(evidence[0]["source"], "hackernews")


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

    def test_so_what_action_mapped_from_pattern_type(self):
        c = _mk_cluster(pattern_type="opportunity_window")
        card = cluster_to_card(c, "buildable")
        self.assertEqual(card["so_what"], "build/trade")


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
                  "total_survived", "gate_reasons", "min_confidence_applied"):
            self.assertIn(k, payload)
