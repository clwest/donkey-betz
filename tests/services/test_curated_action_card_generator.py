"""Pure-function + mocked-LLM tests for the Session 1140 (A) action card generator.

DB-dependent paths (`generate_for_snapshot` against real
CuratedSignalSnapshot rows, `build_curated_actions_envelope` against
real CuratedSignalEntry rows) are exercised by live smoke against the
running stack — same pattern as `test_signal_curator_phase2.py`.

What's covered here:
- `_strip_fences`: bare JSON, fenced JSON, language-tagged fence
- `_normalize_card`: happy path, action_type coercion, step count
  bounds, step shape variants (str vs dict), missing title raises,
  priority normalization
- `_fallback_card`: shape sanity, includes cluster context
- `_build_user_prompt`: happy path, empty sample_signals, long-field
  truncation behavior
- `_llm_generate_card` with mocked OpenAI: happy path, network
  failure falls back, bad JSON falls back, empty title falls back
"""
from __future__ import annotations

import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from core.services.curated_action_card_generator import (
    DEFAULT_ACTION_TYPE,
    GENERATOR_MODEL,
    MAX_STEPS,
    MIN_STEPS,
    VALID_ACTION_TYPES,
    VALID_STEP_PRIORITIES,
    _build_user_prompt,
    _fallback_card,
    _llm_generate_card,
    _normalize_card,
    _strip_fences,
)


# ─── Fake SignalCluster ───────────────────────────────────────────────


def _fake_cluster(**overrides):
    base = dict(
        id=uuid4(),
        name="Spacex, Musk opportunity window",
        pattern_type="opportunity_window",
        strength=0.74,
        confidence=0.82,
        sample_signals=[
            {"headline": "Spacex launches X", "source": "spacenews.com"},
            {"headline": "Musk teases Y at Starbase", "source": "twitter.com"},
        ],
    )
    base.update(overrides)
    return SimpleNamespace(**base)


# ─── _strip_fences ────────────────────────────────────────────────────


class TestStripFences:
    def test_bare_json_unchanged(self):
        assert _strip_fences('{"a": 1}') == '{"a": 1}'

    def test_bare_json_strips_outer_whitespace(self):
        assert _strip_fences('  {"a": 1}  \n') == '{"a": 1}'

    def test_strips_unlabeled_fence(self):
        s = "```\n{\"a\": 1}\n```"
        assert _strip_fences(s) == '{"a": 1}'

    def test_strips_json_labeled_fence(self):
        s = "```json\n{\"a\": 1}\n```"
        assert _strip_fences(s) == '{"a": 1}'

    def test_empty_string(self):
        assert _strip_fences("") == ""


# ─── _normalize_card ──────────────────────────────────────────────────


class TestNormalizeCard:
    @staticmethod
    def _valid_raw():
        return {
            "action_type": "pitch",
            "title": "Open a discovery call with two Spacex customers",
            "steps": [
                {"step": "Find Spacex enterprise sales leads on LinkedIn", "priority": "high"},
                {"step": "Send a 3-sentence cold DM", "priority": "high"},
                {"step": "Track responses in a sheet", "priority": "medium"},
            ],
            "outreach_draft": "Hey — I noticed you're working on X. Would love to compare notes.",
        }

    def test_happy_path(self):
        out = _normalize_card(self._valid_raw())
        assert out["action_type"] == "pitch"
        assert out["action_title"].startswith("Open a discovery call")
        assert len(out["action_steps"]) == 3
        assert all(s["priority"] in VALID_STEP_PRIORITIES for s in out["action_steps"])
        assert "Hey" in out["outreach_draft"]

    def test_action_type_coerces_to_default_on_unknown(self):
        raw = self._valid_raw()
        raw["action_type"] = "research"  # not in vocab
        out = _normalize_card(raw)
        assert out["action_type"] == DEFAULT_ACTION_TYPE

    def test_action_type_normalizes_case(self):
        raw = self._valid_raw()
        raw["action_type"] = "PITCH"
        out = _normalize_card(raw)
        assert out["action_type"] == "pitch"

    def test_missing_title_raises(self):
        raw = self._valid_raw()
        del raw["title"]
        with pytest.raises(ValueError, match="title is required"):
            _normalize_card(raw)

    def test_title_truncated_to_500(self):
        raw = self._valid_raw()
        raw["title"] = "X" * 800
        out = _normalize_card(raw)
        assert len(out["action_title"]) == 500

    def test_too_few_steps_raises(self):
        raw = self._valid_raw()
        raw["steps"] = [{"step": "just one", "priority": "high"}]
        with pytest.raises(ValueError, match="MIN_STEPS"):
            _normalize_card(raw)

    def test_too_many_steps_truncated(self):
        raw = self._valid_raw()
        raw["steps"] = [
            {"step": f"step {i}", "priority": "medium"} for i in range(MAX_STEPS + 3)
        ]
        out = _normalize_card(raw)
        assert len(out["action_steps"]) == MAX_STEPS

    def test_step_as_bare_string_normalized_to_dict(self):
        raw = self._valid_raw()
        raw["steps"] = ["plain string step", "another one", "and a third"]
        out = _normalize_card(raw)
        assert all(isinstance(s, dict) for s in out["action_steps"])
        assert all(s["priority"] == "medium" for s in out["action_steps"])

    def test_step_priority_coerced_to_medium_on_unknown(self):
        raw = self._valid_raw()
        raw["steps"][0]["priority"] = "urgent"  # not in vocab
        out = _normalize_card(raw)
        assert out["action_steps"][0]["priority"] == "medium"

    def test_empty_step_text_dropped(self):
        raw = self._valid_raw()
        raw["steps"].insert(0, {"step": "", "priority": "high"})
        out = _normalize_card(raw)
        # Should drop the empty + keep the valid ones (still ≥MIN_STEPS).
        assert all(s["step"] != "" for s in out["action_steps"])
        assert len(out["action_steps"]) >= MIN_STEPS

    def test_steps_not_list_raises(self):
        raw = self._valid_raw()
        raw["steps"] = "not a list"
        with pytest.raises(ValueError, match="steps must be a list"):
            _normalize_card(raw)

    def test_outreach_optional(self):
        raw = self._valid_raw()
        del raw["outreach_draft"]
        out = _normalize_card(raw)
        assert out["outreach_draft"] == ""

    def test_not_a_dict_raises(self):
        with pytest.raises(ValueError, match="expected JSON object"):
            _normalize_card(["not", "a", "dict"])


# ─── _fallback_card ───────────────────────────────────────────────────


class TestFallbackCard:
    def test_shape_is_valid(self):
        card = _fallback_card(_fake_cluster())
        # Same shape contract as a normalized real card.
        assert card["action_type"] in VALID_ACTION_TYPES
        assert isinstance(card["action_title"], str)
        assert len(card["action_steps"]) >= MIN_STEPS
        assert all("step" in s and "priority" in s for s in card["action_steps"])
        assert isinstance(card["outreach_draft"], str)

    def test_title_includes_cluster_name(self):
        card = _fallback_card(_fake_cluster(name="My Cool Cluster"))
        assert "My Cool Cluster" in card["action_title"]

    def test_title_truncated_when_cluster_name_huge(self):
        card = _fallback_card(_fake_cluster(name="X" * 1000))
        assert len(card["action_title"]) <= 500

    def test_includes_pattern_type_in_step(self):
        card = _fallback_card(_fake_cluster(pattern_type="demand_spike"))
        # First step references the (humanized) pattern type.
        assert "demand spike" in card["action_steps"][0]["step"]

    def test_default_action_type(self):
        card = _fallback_card(_fake_cluster())
        assert card["action_type"] == DEFAULT_ACTION_TYPE


# ─── _build_user_prompt ───────────────────────────────────────────────


class TestBuildUserPrompt:
    def test_happy_path_includes_required_fields(self):
        prompt = _build_user_prompt(_fake_cluster())
        assert "Spacex, Musk" in prompt
        assert "opportunity_window" in prompt
        assert "Strength: 0.74" in prompt
        assert "Sample evidence:" in prompt
        assert "spacenews.com" in prompt

    def test_no_sample_signals_renders_placeholder(self):
        prompt = _build_user_prompt(_fake_cluster(sample_signals=[]))
        assert "(no sample signals available)" in prompt

    def test_truncates_long_headlines(self):
        long_headline = "X" * 500
        prompt = _build_user_prompt(_fake_cluster(sample_signals=[
            {"headline": long_headline, "source": "test"},
        ]))
        # 200 cap on headlines.
        assert "X" * 500 not in prompt
        assert "X" * 200 in prompt

    def test_unnamed_cluster_renders_placeholder(self):
        prompt = _build_user_prompt(_fake_cluster(name=""))
        assert "(unnamed)" in prompt


# ─── _llm_generate_card with mocked OpenAI ────────────────────────────


def _mock_openai_response(content: str) -> MagicMock:
    """Build a MagicMock that mimics openai.types.ChatCompletion."""
    msg = MagicMock()
    msg.content = content
    choice = MagicMock()
    choice.message = msg
    resp = MagicMock()
    resp.choices = [choice]
    return resp


def _patch_openai(response=None, raises: Exception | None = None):
    """Patch get_openai_client to return a client whose chat.completions.create
    returns `response` or raises `raises`."""
    fake_client = MagicMock()
    if raises is not None:
        fake_client.chat.completions.create.side_effect = raises
    else:
        fake_client.chat.completions.create.return_value = response
    return patch(
        "core.services.openai_client_factory.get_openai_client",
        return_value=fake_client,
    )


class TestLlmGenerateCard:
    def test_happy_path_returns_normalized_card(self):
        raw = json.dumps({
            "action_type": "investigate",
            "title": "Validate Spacex enterprise interest",
            "steps": [
                {"step": "Identify 3 paying customers", "priority": "high"},
                {"step": "Read their Q4 earnings calls", "priority": "medium"},
                {"step": "Synthesize into a 1-pager", "priority": "medium"},
            ],
            "outreach_draft": "",
        })
        with _patch_openai(_mock_openai_response(raw)):
            card, label = _llm_generate_card(_fake_cluster())
        assert label == GENERATOR_MODEL
        assert card["action_type"] == "investigate"
        assert len(card["action_steps"]) == 3

    def test_handles_fenced_json(self):
        raw = "```json\n" + json.dumps({
            "action_type": "build",
            "title": "Build a Spacex API wrapper",
            "steps": [
                {"step": "Skim the Spacex public API docs", "priority": "high"},
                {"step": "Sketch a Python wrapper", "priority": "medium"},
                {"step": "Publish to PyPI", "priority": "low"},
            ],
        }) + "\n```"
        with _patch_openai(_mock_openai_response(raw)):
            card, label = _llm_generate_card(_fake_cluster())
        assert label == GENERATOR_MODEL
        assert card["action_type"] == "build"

    def test_network_failure_falls_back(self):
        with _patch_openai(raises=RuntimeError("openai api down")):
            card, label = _llm_generate_card(_fake_cluster())
        assert label == "fallback_placeholder"
        assert card["action_type"] == DEFAULT_ACTION_TYPE

    def test_invalid_json_falls_back(self):
        with _patch_openai(_mock_openai_response("not json at all")):
            card, label = _llm_generate_card(_fake_cluster())
        assert label == "fallback_placeholder"

    def test_missing_title_falls_back(self):
        raw = json.dumps({
            "action_type": "pitch",
            "steps": [
                {"step": "a", "priority": "high"},
                {"step": "b", "priority": "high"},
            ],
        })
        with _patch_openai(_mock_openai_response(raw)):
            card, label = _llm_generate_card(_fake_cluster())
        assert label == "fallback_placeholder"

    def test_too_few_steps_falls_back(self):
        raw = json.dumps({
            "action_type": "pitch",
            "title": "ok",
            "steps": [{"step": "just one", "priority": "high"}],
        })
        with _patch_openai(_mock_openai_response(raw)):
            card, label = _llm_generate_card(_fake_cluster())
        assert label == "fallback_placeholder"

    def test_empty_response_falls_back(self):
        # gpt-5-mini reasoning tokens consumed the budget without
        # emitting any output — most common failure mode in practice
        # (caught us during Session 1140 smoke). Code emits a distinct
        # warning so this can be triaged from logs.
        with _patch_openai(_mock_openai_response("")):
            card, label = _llm_generate_card(_fake_cluster())
        assert label == "fallback_placeholder"

    def test_whitespace_only_response_falls_back(self):
        with _patch_openai(_mock_openai_response("   \n\t   ")):
            card, label = _llm_generate_card(_fake_cluster())
        assert label == "fallback_placeholder"
