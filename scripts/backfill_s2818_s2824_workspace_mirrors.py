"""One-shot backfill: create workspace-mirror deliverables for S2818–S2824.

Post-S2824-close batch fix for a 7-session workspace-mirror gap in the
Phase-0.5 arc. Chris directive 2026-07-19 after Rigby joint SIGN
(pa-76cdab5df13e439b) cleared cycle-2. Per `feedback_pa_deliverables_tool_
flags_ratifications_as_diagnostic`, uses ORM-direct create to bypass the
`missing_initiative_id` diagnostic-flag path in `td_handlers_agents.py:2077`.

Run: `python manage.py shell -c "from scripts.backfill_s2818_s2824_workspace_mirrors import run; run()"`
or directly via `python scripts/backfill_s2818_s2824_workspace_mirrors.py`.

Idempotent: skips a session if a deliverable with the same title already exists.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Django bootstrap for direct-script mode.
if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    BASE_DIR = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(BASE_DIR))
    import django
    django.setup()


DONKEY_BETZ_WORKSPACE_ID = "b4503364-2573-4401-9e28-61a739e0ce50"


# (session, focus, envelope_filename_or_None, handoff_filename, pr_num, merge_sha)
SESSIONS = [
    (
        2818,
        "Discovery-layer pilot ship (PLATFORM_INVENTORY authority-boost)",
        "RATIFICATION_2026-07-18_s2818_platform_inventory_authority_boost_pilot.md",
        "SESSION_2818_DISCOVERY_LAYER_PILOT.md",
        3254,
        "2a01bc537",
    ),
    (
        2819,
        "Shape C query-intent gating",
        "RATIFICATION_2026-07-18_s2819_shape_c_intent_gating.md",
        "SESSION_2819_SHAPE_C_INTENT_GATING.md",
        3256,
        "87fef29d5",
    ),
    (
        2820,
        "Lexical pilot FEATURE COMPLETE (orientation-doc exclusion)",
        "RATIFICATION_2026-07-18_s2820_orientation_doc_exclusion_and_lexical_pilot_feature_complete.md",
        "SESSION_2820_ORIENTATION_DOC_EXCLUSION_LEXICAL_FEATURE_COMPLETE.md",
        3258,
        "b6d051dd1",
    ),
    (
        2821,
        "Semantic eval + routing-first pivot + Phase-0 methodology proposal",
        "RATIFICATION_2026-07-18_s2821_semantic_eval_routing_pivot_phase0_proposed.md",
        "SESSION_2821_SEMANTIC_RETRIEVAL_EVAL_ROUTING_PIVOT.md",
        3259,
        "9d89957ac",
    ),
    (
        2822,
        "Phase-0 executed + OPTION A-DUAL ratified + methodology-outcome primary",
        "RATIFICATION_2026-07-18_s2822_phase0_methodology_ratified_r1_r6.md",
        "SESSION_2822_PHASE0_EXECUTION_OPTION_A_DUAL.md",
        3260,
        "5695896f8",
    ),
    (
        2823,
        "Phase-0.5 arc opened + triple Chris D-verdict on B1+B3+B2 + build authorization",
        "RATIFICATION_2026-07-18_s2823_phase0_5_constitutional_package_b1_b2_b3.md",
        "SESSION_2823_PHASE0_5_ARC_OPEN_TRIPLE_D_RATIFIED.md",
        3261,
        "0c77f8086",
    ),
    (
        2824,
        "Phase-0.5 B2 router build shipped (advisory-only, flag-guarded)",
        # No envelope — S2823 envelope was frozen; S2824 executes it. The
        # implementation log is the authoritative S2824 governance artifact.
        None,
        "SESSION_2824_PHASE0_5_B2_BUILD_SHIPPED.md",
        3262,
        "3ee44778a",
    ),
]


def _read_envelope_head(path: Path, max_chars: int = 6000) -> str:
    if not path.exists():
        return "(envelope file not found on disk at backfill time)"
    text = path.read_text(encoding="utf-8")
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n… (truncated; see envelope file for full content)"


def _build_body(
    session: int,
    focus: str,
    envelope_filename: str | None,
    handoff_filename: str,
    pr_num: int,
    merge_sha: str,
) -> str:
    repo_root = Path(__file__).resolve().parent.parent
    envelope_path = (
        repo_root / "docs" / "research" / "implementation" / envelope_filename
        if envelope_filename
        else None
    )
    handoff_path = repo_root / "docs" / "handoffs" / handoff_filename

    envelope_ref = (
        f"`docs/research/implementation/{envelope_filename}`"
        if envelope_filename
        else "`docs/research/implementation/IMPLEMENTATION_LOG_2026-07-19_s2824_phase0_5_b2_build_shipped.md` (S2824 IMPLEMENTATION LOG — S2823 envelope frozen; execution status is a separate additive artifact)"
    )

    header = (
        f"**⚠️ BACKFILL NOTE:** This workspace deliverable is a RETROACTIVE "
        f"mirror of the S{session} ratification record. It was created "
        f"2026-07-19 in a batch backfill (S2818–S2824) after Chris "
        f"observed the workspace-mirror gap for the Phase-0.5 arc + "
        f"routed a joint SIGN through Rigby (pin `pa-76cdab5df13e439b`) "
        f"who cleared cycle-2 across Q1-Q6 (drift confirmed; Group 2700 "
        f"umbrella does not discharge per-session mirrors; ORM-direct "
        f"create via Path A per `feedback_pa_deliverables_tool_flags_"
        f"ratifications_as_diagnostic`). The temporal-truth pointer for "
        f"when this session's work was actually shipped is the merge SHA "
        f"below + the git commit timestamp on `main`. Do NOT interpret "
        f"the `created_at` on this Deliverable row as the session's "
        f"shipping timestamp — that is `git show {merge_sha}`.\n\n"
        f"---\n\n"
        f"# S{session} — {focus}\n\n"
        f"| Field | Value |\n"
        f"|---|---|\n"
        f"| Session | S{session} |\n"
        f"| Focus | {focus} |\n"
        f"| Handoff | `docs/handoffs/{handoff_filename}` |\n"
        f"| Envelope / governance artifact | {envelope_ref} |\n"
        f"| PR | #{pr_num} |\n"
        f"| Merge SHA | `{merge_sha}` |\n"
        f"| Workspace | Donkey Betz ({DONKEY_BETZ_WORKSPACE_ID}) |\n"
        f"| Backfill batch | S2818–S2824 workspace-mirror gap repair |\n"
        f"| Backfill date | 2026-07-19 |\n"
        f"| Rigby SIGN pin | `pa-76cdab5df13e439b` |\n\n"
    )

    if envelope_path is not None:
        envelope_body = _read_envelope_head(envelope_path)
        content = header + (
            f"## §1 Envelope content (mirror of `{envelope_filename}` at "
            f"backfill time)\n\n{envelope_body}\n"
        )
    else:
        content = header + (
            f"## §1 Implementation log content (S2824 has no separate "
            f"envelope — the S2823 constitutional package envelope was "
            f"frozen at its own merge per PLAYBOOK-6.10.9; S2824 executes "
            f"that package under Chris R7 build authorization. See the "
            f"S2824 implementation log file for the full R1-R7 → "
            f"implementation mapping.)\n\n"
        )

    footer = (
        f"\n\n---\n\n"
        f"## §2 Backfill provenance\n\n"
        f"- **Batch:** S2818–S2824 workspace-mirror gap repair\n"
        f"- **Trigger:** Chris asked 2026-07-19 whether workspace sync had drifted; evaluation confirmed 0 workspace deliverables existed for S2818–S2824\n"
        f"- **Joint SIGN pin:** `pa-76cdab5df13e439b`\n"
        f"- **Rigby verdicts (compact):** Q1 AGREE drift · Q2 DISAGREE Group 2700 umbrella does not discharge per-session mirrors · Q3 AGREE lean A full backfill · Q4 F-BLOCKING resolved (Path A ORM-direct) · Q5 AGREE single mirror per session · Q6 AGREE tag as BACKFILL\n"
        f"- **Chris D-verdict:** yes proceed (2026-07-19)\n"
        f"- **Create path:** ORM-direct `Deliverable.objects.create()` — bypasses `td_handlers_agents.py:2077` diagnostic-flag path per `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic`\n"
        f"- **Related deliverable:** Group 2700 /docs/ Restructuring — Canonical Summary (`37d6ca76-89c3-4966-8f4c-decc52ce8169`) — arc-level scope; this row is one of 7 per-session subordinates\n"
    )

    return content + footer


def run(dry_run: bool = False) -> list[dict]:
    from core.models_deliverables import Deliverable  # type: ignore
    from core.models_skin_layer import ProjectWorkspace

    workspace = ProjectWorkspace.objects.get(id=DONKEY_BETZ_WORKSPACE_ID)

    results: list[dict] = []
    for session, focus, envelope_filename, handoff_filename, pr_num, merge_sha in SESSIONS:
        title = (
            f"S{session} — {focus} — Ratification Record "
            f"(workspace backfill mirror)"
        )
        existing = Deliverable.objects.filter(title=title).first()
        if existing:
            results.append({
                "session": session,
                "status": "skipped_exists",
                "id": str(existing.id),
                "title": title,
            })
            print(f"[skip] S{session} — mirror already exists as {existing.id}")
            continue

        content = _build_body(
            session=session,
            focus=focus,
            envelope_filename=envelope_filename,
            handoff_filename=handoff_filename,
            pr_num=pr_num,
            merge_sha=merge_sha,
        )

        if dry_run:
            results.append({
                "session": session,
                "status": "dry_run",
                "title": title,
                "content_length": len(content),
            })
            print(f"[dry] S{session} — would create title={title!r} len={len(content)}")
            continue

        obj = Deliverable.objects.create(
            title=title,
            content=content,
            deliverable_type="ratification_record",
            category="governance",
            status="ready",
            agent_name="System",
            workspace=workspace,
            tags=["backfill", "phase-0-5", "ratification-record", f"s{session}"],
            metadata={
                "backfill": True,
                "backfill_reason": "workspace_mirror_gap_S2818_S2824",
                "backfill_date": "2026-07-19",
                "backfill_created_by": "claude-code",
                "backfill_session": "s2824-post-close",
                "source_envelope": envelope_filename,
                "source_handoff": handoff_filename,
                "source_pr": pr_num,
                "source_merge_sha": merge_sha,
                "sign_ratified_by": "rigby_pa-76cdab5df13e439b",
                "chris_d_verdict": "yes proceed 2026-07-19",
            },
            content_format="markdown",
            data_sensitivity="internal",
            quality_score=0.9,
            confidence_score=0.95,
            is_saved=True,
        )
        results.append({
            "session": session,
            "status": "created",
            "id": str(obj.id),
            "title": title,
        })
        print(f"[ok] S{session} — created {obj.id} title={title!r}")

    print()
    print("=" * 72)
    print("SUMMARY")
    print("=" * 72)
    created = sum(1 for r in results if r["status"] == "created")
    skipped = sum(1 for r in results if r["status"] == "skipped_exists")
    dry = sum(1 for r in results if r["status"] == "dry_run")
    print(f"  created:  {created}")
    print(f"  skipped:  {skipped} (already existed)")
    print(f"  dry_run:  {dry}")
    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    run(dry_run=args.dry_run)
