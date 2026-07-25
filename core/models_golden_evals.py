"""
Session 2964: Golden Evals validator harness — persistence model.

Companion doc: docs/research/platform/S2963_GOLDEN_EVALS_ARC_CLOSE.md

Records one row per (yaml, prompt) execution when the ``run_golden_evals``
management command runs. Provides the persistence side of the harness so
S2965+ can build a pass-rate drift dashboard on top of these rows without
inventing a separate observability substrate.

Kept as a satellite module in ``core`` (parallel to
``core/models_tool_calls.py``) rather than a new Django app — S2964 PR-1
foundation scope keeps INSTALLED_APPS untouched while the harness shape is
still binding to canon_v2 items.
"""

import uuid

from django.db import models


class GoldenEvalRun(models.Model):
    """One (yaml, prompt) execution result inside a Golden Evals run.

    A single management-command invocation groups many rows via ``run_id``
    so the drift dashboard can query one cohort at a time.

    canon_v2 mapping (per S2963 arc-close ratification):
        - ``substrate_type`` + ``primary_row_id`` + ``evidence_ledger_refs``
          + ``finalized_at`` + ``latency_ms`` mirror the ``EvalRunContext``
          shape defined at canon_v2 Item 6. When a prompt runs, the
          per-substrate adapter yields an ``EvalRunContext`` and this row
          serializes it.
        - ``substrate_type`` is validated at write-time against
          ``core.services.golden_evals.context.KNOWN_SUBSTRATES`` (per the
          zoom-out guardrail Rigby surfaced at S2964 T1 SIGN: stringly-typed
          coupling is the biggest architectural risk this foundation must
          preempt).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    run_id = models.UUIDField(
        db_index=True,
        help_text=(
            "Groups all rows produced by one ``run_golden_evals`` invocation. "
            "Drift dashboards cohort-query on this."
        ),
    )

    yaml_path = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Relative path to the evals/tier1/*.yaml file that produced this row.",
    )
    prompt_id = models.CharField(
        max_length=255,
        db_index=True,
        help_text="``prompts[*].id`` from the YAML (e.g., 'rigby_happy_01_constitution_authoring_initiatives_intent').",
    )
    substrate_type = models.CharField(
        max_length=64,
        db_index=True,
        help_text=(
            "One of ``core.services.golden_evals.context.KNOWN_SUBSTRATES`` "
            "(currently 'agent_execution' or 'chat_conversation'). Validated "
            "at write-time by the harness."
        ),
    )
    primary_row_id = models.CharField(
        max_length=64,
        blank=True,
        help_text=(
            "Substrate-native PK for the row the adapter observed. Blank when "
            "the harness ran in ``--dry-run`` mode and no substrate row was "
            "produced (skeleton dispatch)."
        ),
    )

    evidence_ledger_refs = models.JSONField(
        default=list,
        blank=True,
        help_text=(
            "List of substrate refs the adapter identified as evidence "
            "(ToolCallRecord IDs, LLMCallLog IDs, related deliverable_factory "
            "rows, etc). Shape:"
            " [{'kind': 'tool_call_record', 'id': '...'}, ...]."
        ),
    )

    passed = models.BooleanField(
        null=True, blank=True,
        db_index=True,
        help_text=(
            "True/False after acceptance-criteria runners execute; NULL "
            "when the row was produced in ``--dry-run`` mode (skeleton "
            "dispatch, no validation yet)."
        ),
    )
    failure_reasons = models.JSONField(
        default=list,
        blank=True,
        help_text=(
            "List of {predicate, detail} dicts for each acceptance-criteria "
            "predicate that failed. Empty when ``passed=True`` or "
            "``passed=NULL``."
        ),
    )

    finalized_at = models.DateTimeField(
        null=True, blank=True,
        help_text=(
            "Substrate finalization timestamp (per canon_v2 Item 6). NULL "
            "when the substrate row is still in a mutable phase (e.g., "
            "ChatConversation pre-response) — the adapter surfaces this so "
            "validators can defer or skip mid-flight rows."
        ),
    )
    latency_ms = models.IntegerField(
        null=True, blank=True,
        help_text=(
            "Opt-in latency evidence per canon_v2 Item 3. Only populated when "
            "the slice YAML declares latency as an evidence dimension."
        ),
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        app_label = 'core'
        db_table = 'core_golden_eval_run'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['run_id', 'yaml_path']),
            models.Index(fields=['yaml_path', 'prompt_id']),
            models.Index(fields=['substrate_type', 'passed']),
        ]

    def __str__(self):
        status = 'DRY' if self.passed is None else ('PASS' if self.passed else 'FAIL')
        return f"[{status}] {self.yaml_path}::{self.prompt_id} ({self.substrate_type})"
