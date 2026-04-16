"""
Session 1086 PR 3a: Q7 bypass enforcement test (initiative 2dcb79d7).

Rigby's design review (conversation pa-ada44848ca6b) explicitly flagged:

    "The key is: don't ship 'best effort' enforcement."

This test closes Q7 by locking in two guarantees:

1. **The files PR 3a explicitly patched** (``PR_3A_ENFORCED_BYPASS_FILES``)
   continue to have matching ``check_priority()`` calls paired with every
   ``agent.execute()`` call. A regression causes a hard failure.

2. **The files PR 3b is contracted to migrate next** (``PR_3B_PRIORITY_TARGETS``)
   are enumerated as ``xfail(strict=True)`` so CI fails the moment one
   gets patched without being moved out of the pending list. This
   forces PR 3b's author to acknowledge each migration explicitly.

## Scope limits — why this test is not comprehensive

A tight regex scan of ``core/`` + ``ai_core/`` reveals **67 files** with
``agent.execute()`` call patterns. Rigby and I (Session 1086 design
review) deliberately chose NOT to wire all 67 in PR 3a — that would be
a multi-day refactor and defeat the "safe plumbing" intent of the PR.

Instead, PR 3a patches the 2 highest-volume active Celery task files
(``tasks_content.py`` + ``tasks.py``) and locks them in. PR 3b picks up
the next 6 targets from Rigby's priority list (EPA + assistant layer),
and subsequent PRs migrate the remaining agent-to-agent delegation
patterns on an as-needed basis.

The :func:`test_inventory_stays_documented` test logs the full 67-file
inventory as a soft check and fails only if the inventory changes in
unexpected ways — it's documentation, not enforcement. See the design
review transcript in conversation ``pa-ada44848ca6b`` for the full
scope decision.
"""

import re
from pathlib import Path

import pytest

# Resolve repo root relative to this test file. Tests live at
# core/tests/test_priority_enforcement.py → parents[2] is the repo root.
REPO_ROOT = Path(__file__).resolve().parents[2]

# ── Files locked in by PR 3a ────────────────────────────────────────────

PR_3A_ENFORCED_BYPASS_FILES = [
    "core/tasks_content.py",
    "core/tasks.py",
]

# ── Files PR 3c will migrate next ──────────────────────────────────────
#
# Rigby's Session 1086 design review originally scoped these as PR 3b
# targets, but during PR 3b implementation the bypass inventory scan
# revealed that these 6 files contain **32 ``agent.execute()`` sites
# combined** — far more than the 12 originally estimated. Migrating all
# 32 inside PR 3b (which already ships the semaphore + telemetry fields
# + migration 0330) would risk indentation bugs on a PR that's already
# touching runtime scheduling behavior.
#
# PR 3b therefore ships throttling + telemetry WITHOUT the bypass
# migrations, and these 6 files are deferred to PR 3c. The xfail-strict
# markers still enforce ledger discipline: CI fails the moment any of
# these files gets patched without being moved out of the pending list.
#
# EPA legacy path is reachable in production via core/urls.py:2375,
# refactored assistant layer via UnifiedPAEntrypoint. Both need
# migration; the question is only when.

PR_3B_PRIORITY_TARGETS = [
    "core/epa_handlers_agents.py",
    "core/epa_handlers_tools.py",
    "core/epa_handlers_utility.py",
    "core/assistant/base.py",
    "core/assistant/audio_tools.py",
    "core/assistant/video_tools.py",
]


# ── Regex: tight pattern that only matches idiomatic ``agent.execute(`` ─
#
# ``\b`` word boundaries ensure we catch ``agent.execute(`` but NOT
# ``cursor.execute(`` (SQL), ``self.execute(`` (abstract method
# implementations inside BaseAgent subclasses), or ``some_agent.execute(``
# (because the underscore isn't a word boundary — ``\bagent\b`` requires
# the character before ``a`` to be a non-word char).

_EXECUTE_CALL_PATTERN = r"\bagent\.execute\("
_CHECK_PRIORITY_PATTERN = r"check_priority\("


def _count_in_file(file_path: Path, pattern: str) -> int:
    """Count occurrences of a regex pattern in a file. Returns 0 for
    missing files so the test fails loudly via the assert below rather
    than crashing on FileNotFoundError."""
    if not file_path.exists():
        return 0
    try:
        text = file_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return 0
    return len(re.findall(pattern, text))


# ── Tests ───────────────────────────────────────────────────────────────

@pytest.mark.parametrize("file_path", PR_3A_ENFORCED_BYPASS_FILES)
def test_pr3a_enforced_bypass_files_have_matching_priority_checks(file_path: str):
    """
    Every ``agent.execute()`` call in PR 3a's enforced files must be
    paired with a ``check_priority()`` call in the same file. This
    locks the PR 3a patches in place and causes a loud failure if
    anyone adds a new bypass to these files without the enforcement
    helper.
    """
    path = REPO_ROOT / file_path
    assert path.exists(), (
        f"Enforced bypass file missing: {file_path}. "
        f"Either fix the path or remove from PR_3A_ENFORCED_BYPASS_FILES."
    )

    execute_count = _count_in_file(path, _EXECUTE_CALL_PATTERN)
    check_count = _count_in_file(path, _CHECK_PRIORITY_PATTERN)

    assert check_count >= execute_count, (
        f"{file_path}: {execute_count} agent.execute() calls but only "
        f"{check_count} check_priority() calls. Each execute() must be "
        f"paired with a check_priority() call in the same file. "
        f"See core/services/priority/enforce.py for the helper API."
    )


@pytest.mark.xfail(
    strict=True,
    reason=(
        "PR 3a deferred these bypass files to PR 3b per Rigby's "
        "scope decision. xfail(strict=True) inverts the assertion so "
        "CI fails the moment one gets patched without being moved out "
        "of PR_3B_PRIORITY_TARGETS — forcing the PR 3b author to "
        "acknowledge the migration explicitly in the ledger."
    ),
)
@pytest.mark.parametrize("file_path", PR_3B_PRIORITY_TARGETS)
def test_pr3b_priority_targets_will_be_fixed(file_path: str):
    """
    These files are the highest-priority PR 3b migration targets.
    The test is expected to xfail today — when PR 3b patches a file,
    move it from PR_3B_PRIORITY_TARGETS to PR_3A_ENFORCED_BYPASS_FILES.
    """
    path = REPO_ROOT / file_path
    if not path.exists():
        pytest.skip(f"{file_path} no longer exists (may have been deleted)")

    execute_count = _count_in_file(path, _EXECUTE_CALL_PATTERN)
    check_count = _count_in_file(path, _CHECK_PRIORITY_PATTERN)

    assert check_count >= execute_count, (
        f"{file_path}: {execute_count} execute() calls, {check_count} checks"
    )


# ── Informational inventory test (never fails) ─────────────────────────

# Current full inventory as of PR 3a. Kept here as a ledger — if the
# scan finds a NEW file not in this list, the test prints a warning but
# does not fail. PR 3b and later PRs update this list as they migrate.
#
# The point: give future PR authors a canonical starting place when
# they pick up migration work, without making CI red for bypass files
# that have existed since before this initiative started.

PR_3A_KNOWN_BYPASS_INVENTORY = frozenset({
    # PR 3a enforced (also in PR_3A_ENFORCED_BYPASS_FILES)
    "core/tasks_content.py",
    "core/tasks.py",
    # PR 3b priority targets (also in PR_3B_PRIORITY_TARGETS)
    "core/epa_handlers_agents.py",
    "core/epa_handlers_tools.py",
    "core/epa_handlers_utility.py",
    "core/assistant/base.py",
    "core/assistant/audio_tools.py",
    "core/assistant/video_tools.py",
    # Lower priority — agent-to-agent delegation patterns inside
    # agent class implementations. Many are docstring examples or
    # internal helpers that may not need priority enforcement.
    "ai_core/agents/ai_enforced_base.py",
    "ai_core/agents/concrete_executor.py",
    "core/agent_execution_wrapper.py",
    "core/agents/analysis/__init__.py",
    "core/agents/analysis/market_intelligence_agent.py",
    "core/agents/analysis/opportunity_scoring_agent.py",
    "core/agents/analysis/trend_analysis_agent.py",
    "core/agents/autonomous_content_studio_coordinator.py",
    "core/agents/campaign_orchestrator_agent.py",
    "core/agents/content_executor_agent.py",
    "core/agents/content_writer_agent.py",
    "core/agents/decision_enforcer_agent.py",
    "core/agents/distribution_agent.py",
    "core/agents/dynamic_persona_agent.py",
    "core/agents/editor_agent.py",
    "core/agents/executive/__init__.py",
    "core/agents/executive/coo_agent.py",
    "core/agents/executive/creative_director_agent.py",
    "core/agents/executive/cto_agent.py",
    "core/agents/executive/meeting_coordinator_agent.py",
    "core/agents/image_agent.py",
    "core/agents/opportunity_pipeline_agent.py",
    "core/agents/podcast/podcast_coordinator_agent.py",
    "core/agents/security/__init__.py",
    "core/agents/security/content_audit_agent.py",
    "core/agents/security/memory_isolation_agent.py",
    "core/agents/stocks/market_intelligence_coordinator.py",
    "core/agents/stocks/stock_audit_coordinator.py",
    "core/agents/strategy/__init__.py",
    "core/agents/strategy/brand_identity_agent.py",
    "core/agents/strategy/content_strategy_agent.py",
    "core/agents/strategy/seo_optimizer_agent.py",
    "core/agents/strategy/social_media_agent.py",
    "core/agents/technical_document_agent.py",
    "core/agents/training/__init__.py",
    "core/agents/training/character_training_agent.py",
    "core/agents/training/trained_creation_agent.py",
    "core/agents/workflow_orchestration_agent.py",
    "core/conversation_orchestrator.py",
    "core/management/commands/backfill_voice_scores.py",
    "core/management/commands/test_agent_scenarios.py",
    "core/management/commands/write_self_blog.py",
    "core/personal_ai_orchestrator.py",
    "core/personal_assistant_agent_integration.py",
    "core/services/autonomous_action_executor.py",
    "core/services/content_deliberation_runner.py",
    "core/services/context_tracing.py",
    "core/services/discord_bot.py",
    "core/services/implementation_executor.py",
    "core/services/real_code_generator.py",
    "core/services/sports_betting_coordinator.py",
    "core/services/workflow_builder.py",
    "core/services/workflow_orchestration_agent.py",
    "core/tasks_agents.py",
    "core/tasks_initiatives.py",
    "core/tasks_misc.py",
    "core/tasks_ops.py",
    "core/views_image_tools.py",
    "core/views_legal.py",
    "core/views_odds_sports.py",
})


def test_inventory_ledger_stays_in_sync():
    """
    Informational scan — prints the full bypass inventory and warns
    (but does not fail) if new files are added. The ledger in
    ``PR_3A_KNOWN_BYPASS_INVENTORY`` should be updated in the same PR
    that adds a new bypass.

    This test is the one Rigby asked for: 'a test that fails if any
    task executes an agent without a priority decision recorded' — but
    relaxed to a warning so PR 3a can ship without triggering
    migrations for files that were never in its scope.
    """
    found = set()

    for scan_root in ["core", "ai_core"]:
        root_path = REPO_ROOT / scan_root
        if not root_path.exists():
            continue
        for py_file in root_path.rglob("*.py"):
            rel = py_file.relative_to(REPO_ROOT).as_posix()
            # Skip the priority package itself (defines check_priority)
            # and the test file (which contains patterns in string literals).
            if rel.startswith("core/services/priority/"):
                continue
            if rel.endswith("test_priority_enforcement.py"):
                continue
            # Skip agent_router.py — it IS the route() implementation and
            # calls check_priority itself, not a bypass caller.
            if rel == "core/agent_router.py":
                continue
            try:
                text = py_file.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            if re.search(_EXECUTE_CALL_PATTERN, text):
                found.add(rel)

    new_files = found - PR_3A_KNOWN_BYPASS_INVENTORY
    removed_files = PR_3A_KNOWN_BYPASS_INVENTORY - found

    if new_files:
        print(
            f"\n[priority-enforcement] WARNING: {len(new_files)} new bypass files "
            f"found that are not in PR_3A_KNOWN_BYPASS_INVENTORY:"
        )
        for f in sorted(new_files):
            print(f"  + {f}")
        print(
            "  Update the ledger in core/tests/test_priority_enforcement.py "
            "and add check_priority() calls if this is a new bypass path."
        )

    if removed_files:
        print(
            f"\n[priority-enforcement] INFO: {len(removed_files)} files in the "
            f"ledger no longer match the scan:"
        )
        for f in sorted(removed_files):
            print(f"  - {f}")
        print(
            "  This is usually good — either the file was migrated or deleted. "
            "Remove from PR_3A_KNOWN_BYPASS_INVENTORY."
        )

    # Strict on additions (Rigby's Session 1086 PR 3a review refinement):
    # legacy bypasses are grandfathered into the baseline, but ANY new bypass
    # file must be triaged and explicitly moved into Bucket A (strict
    # enforcement), Bucket B (xfail-strict PR 3b target), or added to this
    # baseline with a deliberate ledger update. Zero-tolerance on additions
    # is the core of "not best-effort" enforcement going forward.
    assert not new_files, (
        f"New agent.execute() bypass files not in PR_3A_KNOWN_BYPASS_INVENTORY: "
        f"{sorted(new_files)}. Each new bypass must be EITHER:\n"
        f"  (A) added to PR_3A_ENFORCED_BYPASS_FILES with matching "
        f"check_priority() calls in the file, OR\n"
        f"  (B) added to PR_3B_PRIORITY_TARGETS if it should be migrated "
        f"in the next PR, OR\n"
        f"  (C) added to PR_3A_KNOWN_BYPASS_INVENTORY as a deliberate "
        f"grandfathered baseline entry.\n"
        f"See core/services/priority/enforce.py for the helper API."
    )
