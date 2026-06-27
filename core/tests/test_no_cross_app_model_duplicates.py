"""Cat 2 regression canary — no cross-app duplicate Django model class names.

Session 1244 closed the Cat 2 audit by resolving all 9 cross-app class-name
duplicates (9 → 0). This test locks that win in place: any future PR that
re-introduces a duplicate model class name across apps fails CI fast.

A "cross-app duplicate" is when `apps.get_models()` registers TWO+ models
under the same `__name__` in different `_meta.app_label` values. This
caused real bugs in the audit:

- Different schemas hidden under one name (consumer reads from a 9-col
  table; writer writes to a 39-col table; consumer sees no data)
- Wrong-import bugs caught by pyright only after renaming (Cat 6
  Finding 6.X — `.create(template=..., priority=...)` on a model that
  doesn't have those fields)
- Migration drift (one variant has writers, the other doesn't)
- Audit confusion (which `AgentExecution` are we talking about?)

The regenerable check is fast (~10ms — pure registry inspection, no DB
hit), so it can run on every test invocation without slowing the suite.

If this test fails:
- Either the new duplicate was intentional → rename ONE side so the
  class names are distinct, OR delete the redundant one
- Or it's accidental → check that the new model belongs in the app
  you placed it under (Meta.app_label) and isn't shadowing an existing
  class

Reference: audit deliverable `86870fdd-e8d8-48d3-9760-4bea75ec10e3`
Finding 2.3 cross-app duplicate inventory + closure.

Run: `python manage.py test core.tests.test_no_cross_app_model_duplicates -v2`
"""

from collections import defaultdict

from django.apps import apps
from django.test import SimpleTestCase


class NoCrossAppModelDuplicatesTests(SimpleTestCase):
    """Regression guard — cross-app duplicate class-name count must stay 0."""

    def test_zero_cross_app_duplicate_class_names(self):
        """No two Django-registered models share the same class name."""
        by_name = defaultdict(list)
        for model in apps.get_models():
            by_name[model.__name__].append(model)

        duplicates = {
            name: classes
            for name, classes in by_name.items()
            if len(classes) > 1
        }

        if duplicates:
            lines = ["Cross-app duplicate Django model class names detected:"]
            for name in sorted(duplicates):
                lines.append(f"  {name}:")
                for m in duplicates[name]:
                    lines.append(
                        f"    - {m._meta.label} "
                        f"(module={m.__module__}, table={m._meta.db_table})"
                    )
            lines.append("")
            lines.append(
                "Rename ONE side (or delete the redundant variant) so class "
                "names are unique across all installed apps. See audit "
                "deliverable 86870fdd-… Finding 2.3 for the resolved-9 history."
            )
            self.fail("\n".join(lines))
