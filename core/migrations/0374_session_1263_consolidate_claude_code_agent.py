"""Session 1263 — consolidate duplicate Claude Code Agent row.

Closes the duplicate-Agent-row hygiene gap surfaced by the
``[CLAUDE_CODE_AGENT_DUP]`` WARN that started firing on every dispatch
after S1262 PR #2752 landed the canonical-name resolver.

Two active ``Agent`` rows exist at audit time:

  * ``claude-code``  (canonical) — created 2026-06-23, actively used,
    9 AgentExecution rows including all S1262 dispatches
  * ``ClaudeCode``   (duplicate) — created 2026-06-21 16:28:58Z by
    ``deliverable_factory._synthesize_pa_receipt`` during an S1187
    Recon batch; frozen since 16:34:09Z. 7 AgentExecution +
    1 AgentDream + 4 AgentMemory historical references.

Canonical choice anchored in S1226 audit (deliverable
e2964e4a-08e9-4ff1-bc01-7fe3adb5a99c §1c):
  - ``claude-code`` matches the autonomous engineer's runtime source
    field (``claude_code_engineer.py`` writes ``source='claude-code'``)
  - Matches the Procfile worker name (``code-worker``) + the kebab-case
    naming convention used across the codebase
  - The S1226 migration 0365 already normalized
    ``Deliverable.agent_name`` strings using the same direction
  - ``core/services/deliverable_aliases.AGENT_NAME_ALIASES`` declares
    ``'ClaudeCode' → 'claude-code'`` as the canonical map

Strategy (one-way; reverse=noop per S1226 precedent at migration 0365):

  1. Resolve canonical + duplicate rows by name. Skip if duplicate
     doesn't exist (idempotent for fresh DBs / replays).
  2. Re-point all FK references from the duplicate to the canonical:
       * AgentExecution.agent      (7 rows at audit time)
       * AgentDream.agent          (1 row)
       * AgentMemory.agent         (4 rows)
  3. Normalize the string field
     ``AgentExecution.owner_agent='ClaudeCode' → 'claude-code'`` on the
     7 migrated rows so the row's FK and string-name stay internally
     consistent.
  4. **Defensive safety gate (Rigby S1263 SIGN-WITH-EDITS edit #1):**
     re-enumerate ALL reverse-FK relations on the Agent model and
     assert each is 0 BEFORE deleting the duplicate. If any non-zero,
     RAISE — the migration fails loudly rather than orphaning rows.
  5. Delete the duplicate Agent row.

Companion code-side fix in same PR (prevents future re-creation):
``core/services/deliverable_factory.py`` ``_synthesize_pa_receipt``
now canonicalizes ``agent_name`` via
``core.services.deliverable_aliases.canonicalize_agent_name`` before
``Agent.objects.get_or_create``. Two mgmt commands (``seed_agent_
initiative_affinities``, ``import_patent_disclosures``) updated to
write ``'claude-code'`` directly so the source string doesn't
re-propagate.

Why reverse=noop: canonicalization is one-way. Post-migration, all
historical AgentExecution rows under ``claude-code`` are
indistinguishable from rows that always pointed there. Manual recovery
would require querying audit history (CeleryTaskEvent, OpsRunEvent,
git log of the seeding scripts) — the migration itself can't undo this.
Same convention as migration 0365.
"""

from django.db import migrations


def consolidate_claude_code_agent(apps, schema_editor):
    """Re-point FK references from ClaudeCode → claude-code, then delete dup."""
    Agent = apps.get_model('core', 'Agent')
    AgentExecution = apps.get_model('core', 'AgentExecution')
    AgentDream = apps.get_model('core', 'AgentDream')
    AgentMemory = apps.get_model('core', 'AgentMemory')

    canonical = Agent.objects.filter(name='claude-code').first()
    duplicate = Agent.objects.filter(name='ClaudeCode').first()

    if duplicate is None:
        print("  [0374] no 'ClaudeCode' Agent row — already consolidated or never existed. Skipping.")
        return

    if canonical is None:
        # Defensive: if canonical doesn't exist (unlikely but possible on
        # a fresh DB before any claude_code_engineer_task dispatch), rename
        # the duplicate to the canonical name in-place. No data migration
        # needed because there's nothing to merge.
        duplicate.name = 'claude-code'
        duplicate.save(update_fields=['name'])
        print("  [0374] no 'claude-code' Agent row existed — renamed 'ClaudeCode' → 'claude-code' in-place.")
        return

    print(
        f"  [0374] canonical='claude-code' (id={canonical.id}); "
        f"duplicate='ClaudeCode' (id={duplicate.id})"
    )

    # 1. AgentExecution.agent FK
    n_exec = AgentExecution.objects.filter(agent=duplicate).update(agent=canonical)
    print(f"  [0374] AgentExecution.agent: {n_exec} rows repointed")

    # 2. AgentExecution.owner_agent string field (companion to the FK)
    n_owner = AgentExecution.objects.filter(
        owner_agent='ClaudeCode'
    ).update(owner_agent='claude-code')
    print(f"  [0374] AgentExecution.owner_agent string: {n_owner} rows normalized")

    # 3. AgentDream.agent FK
    n_dream = AgentDream.objects.filter(agent=duplicate).update(agent=canonical)
    print(f"  [0374] AgentDream.agent: {n_dream} rows repointed")

    # 4. AgentMemory.agent FK
    n_mem = AgentMemory.objects.filter(agent=duplicate).update(agent=canonical)
    print(f"  [0374] AgentMemory.agent: {n_mem} rows repointed")

    # 5. Defensive safety gate (Rigby SIGN-WITH-EDITS edit #1).
    # Re-enumerate ALL reverse-FK relations on the Agent model via Django
    # introspection — not just the 3 we expect — and assert each is 0
    # before deleting the duplicate row. Catches surprises from any model
    # we didn't account for (cached configs, learning bridges, etc.).
    remaining = []
    for rel in Agent._meta.related_objects:
        try:
            accessor = rel.get_accessor_name()
            count = getattr(duplicate, accessor).count()
            if count > 0:
                remaining.append(
                    f"{rel.field.model.__name__}.{rel.field.name}={count}"
                )
        except Exception as exc:  # pragma: no cover — defensive
            # OneToOne reverse accessors raise DoesNotExist on access; that
            # is the no-row case and is fine. Other exceptions log + skip.
            if 'has no' not in str(exc):
                print(f"  [0374] WARN reverse-FK probe failed: {exc}")

    if remaining:
        raise RuntimeError(
            f"[0374] ABORT — duplicate Agent row 'ClaudeCode' still has "
            f"reverse-FK references after migration: {remaining}. "
            f"Refusing to delete to avoid orphaning history. "
            f"Investigate the unaccounted relation, extend this "
            f"migration to repoint it, and re-run."
        )

    # 6. Delete the duplicate row. Safe — all FKs repointed + gate passed.
    duplicate_id = duplicate.id
    duplicate.delete()
    print(f"  [0374] deleted duplicate Agent row id={duplicate_id}")


def noop_reverse(apps, schema_editor):
    """Reverse is noop — canonicalization is one-way per migration 0365.

    Post-migration ``claude-code`` rows from the duplicate are
    indistinguishable from rows that were always under that name.
    Manual recovery would require querying audit history.
    """
    print(
        "  [0374] Reverse migration is a noop. Agent row consolidation "
        "cannot be automatically undone — post-migration claude-code "
        "rows are indistinguishable from rows that were always there. "
        "See module docstring."
    )


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0373_session_1258_flip_morning_brief_beat_task'),
    ]

    operations = [
        migrations.RunPython(
            consolidate_claude_code_agent,
            reverse_code=noop_reverse,
        ),
    ]
