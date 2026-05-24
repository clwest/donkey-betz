"""Tests for the Session 1139 entity-token clusterer.

What's covered (pure-function — no DB):
- Entity-token extraction (basic + denylist + min-length + ALL-CAPS
  exclusion + hyphenated entities + cap per signal)
- _cluster_signals: duplicate-collapse (Tableau jobs), heterogeneity
  rejection (Trump+Hubble+NFL don't co-cluster), token-frequency
  throttle (one-off entity stays unclustered), per-pattern min size
  (opportunity_window needs 4, others 3), empty/degenerate inputs
- _generate_cluster_name: v1 entity-token rendering AND legacy back-compat

DB-dependent integration (the actual save path through
_create_signal_clusters + SignalCluster ORM + fleet emit) is parked
because local Postgres lacks pgvector (`$libdir/vector` error) which
blocks SpiderData queries — same parking pattern as
test_fleet_paid_interest.py + test_fleet_signals_phase1.py. Live
verification of the save path happens in Docker / production stack
where pgvector loads cleanly.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from core.services.signal_aggregation_service import SignalAggregationService


def _now():
    return datetime.now(timezone.utc)


def _mksig(text: str, *, spider: str = "test", keywords=None, kws_only=False):
    """Build a synthetic signal dict mirroring _extract_signals's output.

    keywords defaults to PATTERN_TYPE_KEYWORD-style noise so pattern
    detection has something to chew on; pass `kws_only=True` to force
    an entity-token-free signal (used by negative tests).
    """
    svc = SignalAggregationService()
    entity_tokens = set() if kws_only else svc._extract_entity_tokens(text)
    return {
        "spider_data_id": str(hash(text)),
        "spider_name": spider,
        "keywords": keywords or ["need", "want", "hiring", "position"],
        "topics": [],
        "entity_tokens": entity_tokens,
        "text_sample": text[:200],
        "created_at": _now(),
        "relevance_score": 75,
    }


# ─── Entity-token extraction ──────────────────────────────────────────


class TestExtractEntityTokens:
    def setup_method(self):
        self.svc = SignalAggregationService()

    def test_basic_capitalized_nouns_extracted(self):
        toks = self.svc._extract_entity_tokens(
            "Tesla announced its Cybertruck launch with Anthropic AI integration"
        )
        # 'Tesla', 'Cybertruck', 'Anthropic' should all survive.
        assert "tesla" in toks
        assert "cybertruck" in toks
        assert "anthropic" in toks

    def test_all_caps_acronyms_excluded(self):
        toks = self.svc._extract_entity_tokens(
            "FDA approves new drug from FBI investigation under DOJ scrutiny"
        )
        # ALL-CAPS acronyms must NOT be extracted (regex requires
        # lowercase tail).
        assert "fda" not in toks
        assert "fbi" not in toks
        assert "doj" not in toks

    def test_short_tokens_excluded(self):
        # Tokens shorter than MIN_ENTITY_TOKEN_LENGTH (4) drop out.
        toks = self.svc._extract_entity_tokens("Cat Dog Pig and Cow story")
        assert "cat" not in toks
        assert "dog" not in toks
        assert "pig" not in toks
        assert "cow" not in toks

    def test_news_boilerplate_denylisted(self):
        toks = self.svc._extract_entity_tokens(
            "Today Breaking news: New Report Update Live Watch Video"
        )
        # Every word here is in the denylist.
        assert toks == set()

    def test_hyphenated_entities_extracted(self):
        toks = self.svc._extract_entity_tokens(
            "The Anti-Corruption Commission released findings on Sky-Train scandal"
        )
        assert any("anti-corruption" in t for t in toks)
        assert any("sky-train" in t for t in toks)

    def test_camel_case_entities_extracted(self):
        toks = self.svc._extract_entity_tokens(
            "iPhone reviews compare OpenAI with Anthropic"
        )
        assert "iphone" in toks
        assert "openai" in toks
        assert "anthropic" in toks

    def test_per_signal_cap_enforced(self):
        # 20 distinct entity-shaped words → only
        # MAX_ENTITY_TOKENS_PER_SIGNAL (8) extracted. NATO alphabet
        # used because each word is a distinct ≥4-char capitalized
        # noun the regex catches cleanly.
        nato = [
            "Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot",
            "Golf", "Hotel", "India", "Juliet", "Kilo", "Lima",
            "Mike", "November", "Oscar", "Papa", "Quebec", "Romeo",
            "Sierra", "Tango",
        ]
        toks = self.svc._extract_entity_tokens(" ".join(nato))
        assert len(toks) == self.svc.MAX_ENTITY_TOKENS_PER_SIGNAL

    def test_empty_text_returns_empty_set(self):
        assert self.svc._extract_entity_tokens("") == set()
        assert self.svc._extract_entity_tokens(None) == set()  # type: ignore[arg-type]


# ─── Clusterer — happy-path collapses ─────────────────────────────────


class TestClusterSignalsCollapse:
    def setup_method(self):
        self.svc = SignalAggregationService()

    def test_duplicate_tableau_jobs_form_one_cluster(self):
        # Real-world scenario from the start-here doc: multiple
        # "Tableau Developer Remote Job" rows should collapse to ONE
        # cluster keyed on shared entity tokens, not multiple lookalike
        # rows keyed on "hiring"/"position"/etc.
        signals = [
            _mksig("Tableau Developer Remote Job at Acme Corporation"),
            _mksig("Tableau Developer position in Boston Massachusetts"),
            _mksig("Tableau Developer hiring at Beta Industries Boston"),
            _mksig("Tableau analyst openings Boston Massachusetts area"),
        ]
        clusters = self.svc._cluster_signals(signals)
        assert len(clusters) == 1
        key, members = next(iter(clusters.items()))
        assert "tableau" in key
        assert len(members) == 4

    def test_two_entity_topic_groups_stay_separate(self):
        # SpaceX-themed and Trump-Mobile-themed signals should form
        # two DIFFERENT clusters, not one lumped one.
        signals = [
            _mksig("SpaceX launches Starship test from Boca facility"),
            _mksig("SpaceX confirms Starship return profile from Boca"),
            _mksig("SpaceX Starship Boca facility expansion next year"),
            _mksig("Trump Mobile breach exposes Mobile customer data"),
            _mksig("Trump Mobile launches new Mobile service tier"),
            _mksig("Trump Mobile reports Mobile customer growth uptick"),
        ]
        clusters = self.svc._cluster_signals(signals)
        # Two distinct clusters, one per shared entity pair.
        assert len(clusters) == 2
        keys = list(clusters.keys())
        assert any("spacex" in k for k in keys)
        assert any("trump" in k for k in keys)
        # Each cluster should have exactly 3 signals.
        for members in clusters.values():
            assert len(members) == 3


# ─── Clusterer — heterogeneity rejection ──────────────────────────────


class TestClusterSignalsRejection:
    def setup_method(self):
        self.svc = SignalAggregationService()

    def test_heterogeneous_signals_do_not_co_cluster(self):
        # The pre-1139 failure mode: "Now opportunity window" mixing
        # Trump phone + Hubble + Ebola + NFL. With entity-token keying
        # and ≥2 shared tokens required, these unrelated stories must
        # produce ZERO clusters.
        signals = [
            _mksig("Trump phone confirms customer data exposure"),
            _mksig("Hubble captures Galaxy MACS distant image"),
            _mksig("Ebola vaccine candidate enters Phase trial"),
            _mksig("Cannes Festival awards Yuri rescue dog"),
            _mksig("Ducks NFL playoff bye contender outlook"),
        ]
        clusters = self.svc._cluster_signals(signals)
        # Each signal has only 1 entity token in common with any other
        # (mostly none). Result: no cluster formed.
        assert clusters == {}

    def test_one_off_capitalized_noun_does_not_form_cluster(self):
        # Window-frequency throttle (MIN_TOKEN_FREQUENCY_IN_WINDOW=2):
        # a single signal mentioning "Tableau" should not be clustered
        # even if no other signals share its tokens.
        signals = [
            _mksig("Tableau Developer Job at Acme Corp Remote"),
            _mksig("Random news about Distinct Topic and Another Subject"),
            _mksig("Other piece about Unique Matter and Separate Issue"),
        ]
        clusters = self.svc._cluster_signals(signals)
        # No shared tokens above the frequency threshold → no cluster.
        assert clusters == {}

    def test_signal_with_no_entity_tokens_excluded(self):
        # Signals from headlines that are 100% denylist (Today Breaking
        # New Update Live...) get an empty entity_tokens set and must
        # be excluded from clustering.
        signals = [
            _mksig("Tableau Developer position remote Acme Corp"),
            _mksig("Tableau Developer hiring Acme Corp role"),
            _mksig("Tableau Developer Acme Corp full remote position"),
            _mksig("Today Breaking New Update Live Video story", kws_only=True),
        ]
        clusters = self.svc._cluster_signals(signals)
        assert len(clusters) == 1
        members = next(iter(clusters.values()))
        # The all-denylist row is NOT in the cluster.
        assert len(members) == 3
        sample_texts = [m["text_sample"] for m in members]
        assert not any("Breaking" in t for t in sample_texts)


# ─── Per-pattern min cluster size ─────────────────────────────────────


class TestPerPatternMinSize:
    def setup_method(self):
        self.svc = SignalAggregationService()

    def test_opportunity_window_requires_four_signals(self):
        # opportunity_window is the noisiest pattern type (per Session
        # 1139 diagnosis); PER_PATTERN_MIN_CLUSTER_SIZE bumps it to 4.
        # 3 opportunity-flavored signals (each with ≥2 shared entity
        # tokens) → no cluster (below threshold).
        opportunity_kws = ["opportunity", "chance", "limited time"]
        signals = [
            _mksig("Tesla Cybertruck opportunity buyback Tesla chance window",
                   keywords=opportunity_kws),
            _mksig("Tesla Cybertruck limited opportunity Cybertruck buyback chance",
                   keywords=opportunity_kws),
            _mksig("Tesla Cybertruck buyback opportunity chance ends Tesla week",
                   keywords=opportunity_kws),
        ]
        # Confirm pattern detection is opportunity_window first.
        assert self.svc._detect_pattern_type(signals) == "opportunity_window"
        clusters = self.svc._cluster_signals(signals)
        # Min for opportunity_window is 4 — these 3 are below threshold.
        assert clusters == {}

    def test_opportunity_window_clusters_at_four(self):
        opportunity_kws = ["opportunity", "chance", "limited time"]
        signals = [
            _mksig("Tesla Cybertruck opportunity buyback Tesla chance window",
                   keywords=opportunity_kws),
            _mksig("Tesla Cybertruck limited opportunity Cybertruck buyback chance",
                   keywords=opportunity_kws),
            _mksig("Tesla Cybertruck buyback opportunity chance ends Tesla week",
                   keywords=opportunity_kws),
            _mksig("Tesla Cybertruck announces opportunity chance for Cybertruck shareholders",
                   keywords=opportunity_kws),
        ]
        clusters = self.svc._cluster_signals(signals)
        assert len(clusters) == 1
        assert len(next(iter(clusters.values()))) == 4

    def test_demand_spike_clusters_at_three(self):
        demand_kws = ["need", "want", "looking for"]
        signals = [
            _mksig("Need help with Tableau Developer position role",
                   keywords=demand_kws),
            _mksig("Want Tableau Developer role recommendations soon",
                   keywords=demand_kws),
            _mksig("Looking for Tableau Developer position now available",
                   keywords=demand_kws),
        ]
        # Pattern detection is keyword-driven; demand_spike default min=3.
        clusters = self.svc._cluster_signals(signals)
        assert len(clusters) == 1


# ─── Cluster naming ───────────────────────────────────────────────────


class TestGenerateClusterName:
    def setup_method(self):
        self.svc = SignalAggregationService()

    def test_v1_two_token_key_renders_as_csv(self):
        name = self.svc._generate_cluster_name(
            "tableau|developer", "skill_demand", ["tableau", "developer"]
        )
        # Tokens are sorted lexicographically by the clusterer, then
        # Title-cased in the name.
        assert name == "Tableau, Developer skill demand"

    def test_v1_hyphenated_entity_preserves_hyphen(self):
        name = self.svc._generate_cluster_name(
            "anti-corruption|commission", "trend_emergence", []
        )
        assert "Anti-Corruption" in name
        assert "emerging trend" in name

    def test_v1_caps_at_two_tokens(self):
        name = self.svc._generate_cluster_name(
            "alpha|beta|gamma", "demand_spike", []
        )
        # Only the first two tokens render — beyond that is noise.
        assert "Alpha" in name and "Beta" in name
        assert "Gamma" not in name

    def test_legacy_single_token_path_back_compat(self):
        # Pre-1139 callers / edge cases where the topic is a single
        # word (no pipe). Must still produce a non-empty name.
        name = self.svc._generate_cluster_name(
            "ai", "trend_emergence", ["ai"]
        )
        assert "Ai" in name
        assert "emerging trend" in name

    def test_kw_prefix_stripped_legacy_path(self):
        name = self.svc._generate_cluster_name(
            "kw:hiring", "skill_demand", []
        )
        assert "kw:" not in name
        assert "Hiring" in name


# ─── Degenerate inputs ────────────────────────────────────────────────


class TestDegenerate:
    def setup_method(self):
        self.svc = SignalAggregationService()

    def test_empty_signals_returns_empty(self):
        assert self.svc._cluster_signals([]) == {}

    def test_all_signals_below_token_threshold_returns_empty(self):
        signals = [
            _mksig("Today Breaking Update Live", kws_only=True),
            _mksig("New Report Story Watch", kws_only=True),
        ]
        assert self.svc._cluster_signals(signals) == {}


# ─── Signal-extraction wiring ─────────────────────────────────────────


class TestExtractSignalsWiring:
    """The `entity_tokens` field must appear on every signal dict."""

    def test_entity_tokens_field_present_on_extracted_signals(self):
        # Build a SpiderData-shaped stub with the minimum fields
        # _extract_text_from_spider_data + _extract_signals need.
        class _StubSD:
            def __init__(self, raw, name="test", relevance=50):
                from uuid import uuid4
                self.id = uuid4()
                self.spider_name = name
                self.raw_data = raw
                self.processed_data = {}
                self.embedding_text = ""
                self.created_at = _now()
                self.relevance_score = relevance

        svc = SignalAggregationService()
        stubs = [
            _StubSD({"title": "Tesla launches new Cybertruck variant"}),
        ]
        sigs = svc._extract_signals(stubs)  # type: ignore[arg-type]
        assert len(sigs) == 1
        assert "entity_tokens" in sigs[0]
        assert isinstance(sigs[0]["entity_tokens"], set)
        assert "tesla" in sigs[0]["entity_tokens"]
        assert "cybertruck" in sigs[0]["entity_tokens"]
