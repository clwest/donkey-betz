# Refactor Gotchas

> Central reference for non-obvious footguns encountered during the
> Session 1115 code-health work. Read this before adding a new Celery
> task, learning bridge, signal handler, or audit detector. Each entry
> tells you the problem, the fix that worked, and how to detect it
> programmatically next time.

---

## 1. BSD grep doesn't understand `\w`

**Symptom:** Your detector regex works in Python `re` but the
`subprocess.run(['grep', '-rEn', ...])` invocation returns zero hits.

**Root cause:** macOS ships BSD grep, which uses POSIX ERE. POSIX ERE
does not recognize `\w` (or `\d`, `\s`, `\b`) shorthand. Linux ships
GNU grep, which does — so CI environments may hide this bug locally.

**Fix:** Use explicit POSIX character classes:

```python
# WRONG — silently returns nothing on macOS
subprocess.run(['grep', '-rEn', r'\w+\.delay\(', ...])

# RIGHT — works on both BSD and GNU grep
subprocess.run(['grep', '-rEn', r'[[:alnum:]_]+\.delay\(', ...])
```

Python's `re` module is fine with `\w` — only the grep invocation needs
the workaround.

**Detect next time:** If a new detector returns zero matches but you
*know* the pattern exists, run the raw grep command in your terminal
and check whether it's actually finding rows.

**Surfaced in:** Session 1115 batch-2 (`build_celery_audit.py` generic
string-literal scan).

---

## 2. Function name vs registered task name mismatch

**Symptom:** Your Celery task has a `.delay()` caller but the audit
still flags it as orphan.

**Root cause:** When you decorate a task with `@shared_task(name='X.Y')`,
the **registered** task name is `X.Y` but the **Python function** name
stays whatever you wrote after `def`. The orphan detector greps for
`function_name.delay(...)` but cross-references against the registered
short-name (last segment of `X.Y`). When they differ, the match fails.

**Example from `core/tasks.py`:**

```python
@shared_task(name='narrative_drift.trigger_content_from_shift')
def trigger_content_from_narrative_shift(shift_id: str):
    ...
```

- Registered short-name: `trigger_content_from_shift`
- Python function name: `trigger_content_from_narrative_shift`

A caller that uses `trigger_content_from_narrative_shift.delay(...)`
matches the function name, but the detector is looking for callers of
`trigger_content_from_shift` (the registered short-name). Result:
false orphan.

**Fix:** Either rename the function to match the registered name, or
use `current_app.send_task(canonical_name, args=[...])` instead of the
attribute-style `.delay()`. The string-literal scan picks up the
`send_task('canonical_name')` form automatically.

```python
# This is how the NarrativeShift signal handler dispatches
from celery import current_app
current_app.send_task(
    'narrative_drift.trigger_content_from_shift',
    args=[str(instance.id)],
)
```

**Detect next time:** When wiring a new signal handler for an
existing task, check whether the task has a custom `name=` decorator
arg. If it does, use `send_task(canonical_name)` to avoid the mismatch.

**Surfaced in:** Session 1115 batch-7 (signal wiring for
`trigger_content_from_shift`).

---

## 3. `core/models/` package shadows `core/models.py` catch-all

**Symptom:** `@receiver(post_save, sender='core.MyModel')` fails at
startup with `signals.E001: app 'core' doesn't provide model 'mymodel'`,
even though the model has `class Meta: app_label = 'core'` and lives in
a file like `core/models_my_stuff.py`.

**Root cause:** Python prefers package directories over single-file
modules. The repo has BOTH:

- `core/models/` — a package directory with `__init__.py`
- `core/models.py` — a module file

When Django does `import core.models`, it gets the **package**
(`core/models/__init__.py`), not the file. The file `core/models.py`
exists and contains catch-all imports like `from .models_narrative_drift
import *`, but those imports **never run** during Django startup
because the file is shadowed by the package.

Models in `core/models_*.py` files are only loaded into Django's app
registry if something explicitly imports them. Catch-all imports in
`core/models.py` don't count.

**Fix:** Import the model class directly in your signal-binding code,
then use `post_save.connect()` with the imported class as sender —
**not** the lazy string-sender form.

```python
# WRONG — fails because the model isn't auto-registered
@receiver(post_save, sender='core.NarrativeShift')
def on_narrative_shift_created(sender, instance, created, **kwargs):
    ...

# RIGHT — explicit import forces registration, then connect()
from core.models_narrative_drift import NarrativeShift
post_save.connect(
    on_narrative_shift_created,
    sender=NarrativeShift,
    dispatch_uid='document_processing_signals.on_narrative_shift_created',
)
```

The `dispatch_uid` is important — without it, the connection can fire
twice if the module gets imported twice during startup (which happens
in some test/runserver paths).

**Detect next time:** When wiring a signal for a model from a
`core/models_*.py` file (not the package), run a quick check:

```python
from django.apps import apps
apps.get_model('core', 'MyModel')  # raises LookupError if not registered
```

If it raises, you need the explicit-import approach.

**Surfaced in:** Session 1115 batch-7 (NarrativeShift signal wiring in
`document_processing_signals.py`).

---

## 4. Verifier baseline must move in lockstep with detector logic

**Symptom:** You improve the orphan detector to catch more callers,
the audit doc shows fewer orphans, but the verifier still reports
drift (or vice versa).

**Root cause:** The verifier (`_celery_orphan_count_baseline` in
`core/services/doc_claim_verification.py`) has its own copy of the
detection logic that mirrors `build_celery_audit.py`. Each time the
audit's detector picks up a new caller pattern, the verifier's logic
needs the same update **plus** the `baseline = N` constant.

**Fix:** Treat the verifier mirror and the audit detector as a single
unit. Any PR that changes one must change the other:

1. Edit `core/management/commands/build_celery_audit.py` to add the
   new caller-path detection.
2. Mirror the same logic in `_celery_orphan_count_baseline` (search
   for the comment marker like `# Session 1115 batch-N`).
3. Regenerate: `python manage.py build_celery_audit`.
4. Update `baseline = N` to match the new orphan count.
5. Verify drift: `python manage.py verify_doc_claims --only-drift`.

The same pattern applies to other verifier claims that track a count
or set (`learning_bridges_inherit_base`, etc.).

**Detect next time:** If `build_celery_audit` says N orphans but
`verify_doc_claims` reports a different number, you have a detector/
verifier mirror drift. Run a diff between the two grep patterns.

**Surfaced in:** Multiple batches across Session 1115 (the verifier
and detector evolved together as new caller-path scans landed).

---

## Quick reference

| Problem | Fix | Detect via |
|---|---|---|
| BSD grep returns nothing | Use `[[:alnum:]_]` not `\w` in grep regex | Run grep manually in terminal |
| Task flagged orphan despite caller | Function name ≠ registered name — use `send_task(canonical_name)` | Check for `@shared_task(name='...')` decorator arg |
| Signal sender lazy-string fails | Import model class directly + `post_save.connect()` | `apps.get_model('app', 'Model')` raises LookupError |
| Verifier and audit doc disagree | Mirror detector logic in `_celery_orphan_count_baseline` | Diff the two grep patterns |

---

*Established Session 1115. Append new gotchas as they're discovered.
Each entry should have: Symptom, Root cause, Fix (with code), Detect
next time, and Surfaced in.*
