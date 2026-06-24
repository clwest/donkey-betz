"""Session 1226 P1 — canonicalize agent_name aliases on core_deliverables.

Closes the agent-name fragmentation finding (F2) from the Rigby+Claude
verifier-loop deliverables audit (deliverable e2964e4a-08e9-4ff1-bc01-7fe3adb5a99c,
Part 4 §4.5 quick-win #2).

Two case/separator variants are normalized:

  'rigby'      → 'Rigby'        (1 row at audit time — case variant)
  'ClaudeCode' → 'claude-code'  (17 rows at audit time — case + separator variant)

Canonical choices anchored in the audit (§1c reasoning):

  - 'Rigby' wins because 101/102 existing rows already use that spelling.
  - 'claude-code' wins because it matches the autonomous engineer's runtime
    source field (`claude_code_engineer.py:501` sets source='claude-code'),
    the Procfile worker name (`code-worker`), and the feedback-memory file
    naming convention. The 17 'ClaudeCode' rows are older artifacts that
    pre-date the runtime convention.

Materially affects rankings: 'claude-code' rises from #14 to #4 in the
top-agent leaderboard after this migration applies (audit Part 2 §2d).

Reverse: noop. Canonicalization is one-way — the migration can't tell
which post-migration 'Rigby' rows came from 'rigby' vs which were always
'Rigby'. Same for 'claude-code'. Manual recovery would require
querying audit history.

Companion deferred work (not in this migration):
  - Apply alias-map normalization on WRITE in deliverable_factory.py so
    new variants can't be introduced. Tracked as Session 1226 audit §4.4
    P1 'Enforcement' bullet — separate PR.
"""

from django.db import migrations


# Alias map: source → canonical. Lowercase keys are NOT used here because
# we're matching the exact stored variants surfaced by the audit, not a
# general case-insensitive sweep. If a future audit finds more variants
# (e.g. 'RIGBY' all-caps), add a row here.
_ALIAS_MAP = {
    'rigby': 'Rigby',
    'ClaudeCode': 'claude-code',
}


def canonicalize_agent_names(apps, schema_editor):
    """Apply the alias map. Logs counts so the operator sees what happened."""
    Deliverable = apps.get_model('core', 'Deliverable')

    total_changed = 0
    for source, canonical in _ALIAS_MAP.items():
        n = Deliverable.objects.filter(agent_name=source).count()
        if n == 0:
            print(f"  [0365] agent_name {source!r}: 0 rows — already canonical or already migrated. Skipping.")
            continue
        Deliverable.objects.filter(agent_name=source).update(agent_name=canonical)
        print(f"  [0365] agent_name {source!r} → {canonical!r}: {n} rows updated.")
        total_changed += n

    print(f"  [0365] Total rows changed: {total_changed}")


def noop_reverse(apps, schema_editor):
    """Reverse is noop — canonicalization is one-way. See module docstring."""
    print(
        "  [0365] Reverse migration is a noop. Canonicalization cannot be "
        "automatically undone — post-migration rows under the canonical name "
        "are indistinguishable from rows that were already canonical."
    )


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0364_session_1222_b2_beat_task_decisions'),
    ]

    operations = [
        migrations.RunPython(canonicalize_agent_names, reverse_code=noop_reverse),
    ]
