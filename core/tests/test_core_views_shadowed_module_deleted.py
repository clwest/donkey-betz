"""Session 1237 P2.b — core/views.py shadowed-dead-code deletion guard.

Pre-deletion `core/views.py` was a 1,457-line module file containing
30 functions that were ALL ALSO present in `core/views/main.py` (the
package's main module). Python's package resolution rule made
`core/views/` (package, with `__init__.py`) win over `core/views.py`
(module file), so the entire 1,457-line file was unreachable —
shadowed dead code.

The `__init__.py` comment confirmed the intent dated back to Session
728: "Original platform views (from core/views.py, now in main.py)".
At that conversion the package was created + functions moved to
`main.py`, but `core/views.py` was kept around as dead artifact —
exactly the kind of dead-code-archeology debt the Session 1235-1236
P5#3 audit was created to eliminate.

Audit evidence captured at deletion time:
- Set diff of function names between core/views.py and
  core/views/main.py returned EMPTY in both directions (every name
  in core/views.py is in main.py, and vice versa)
- `find_spec('core.views')` resolved to the package `__init__.py`,
  NOT the module file (confirming shadowing)
- `from core.views import <fn>` works post-deletion (1797 URL
  patterns still resolve)
- No bypass importers (importlib.import_module / runpy / direct
  module loaders) anywhere in the codebase

Per Chris's evidence threshold ("I do remember when we started that
... forgot all about doing it") which applied to PR #2643 + #2650 —
this is the same shape at larger scale.

Run::

    python manage.py test core.tests.test_core_views_shadowed_module_deleted -v 2 --keepdb
"""

import importlib.util
from pathlib import Path

from django.test import TestCase


REPO_ROOT = Path(__file__).resolve().parent.parent.parent


class CoreViewsShadowedModuleDeletionTests(TestCase):
    """Guards against restoration of the deleted shadowed module."""

    def test_core_views_module_file_does_not_exist(self):
        """The file `core/views.py` was deleted. Note: `core.views`
        STILL resolves — to the PACKAGE at `core/views/__init__.py`.
        This test confirms the FILE absence, not the namespace absence."""
        module_file = REPO_ROOT / 'core' / 'views.py'
        self.assertFalse(
            module_file.exists(),
            "core/views.py reappeared after Session 1237 P2.b "
            "deletion. The file was a 1,457-line shadowed duplicate "
            "of core/views/main.py (every function name appeared in "
            "both files). If you need to add NEW functions, put them "
            "in core/views/main.py or another module under the "
            "core/views/ package — adding them to a re-created "
            "core/views.py would be unreachable due to Python "
            "package resolution rules.",
        )

    def test_core_views_namespace_still_resolves_to_package(self):
        """`from core.views import X` should still work — the package
        at core/views/__init__.py re-exports the same names that were
        in the deleted module."""
        spec = importlib.util.find_spec('core.views')
        self.assertIsNotNone(spec)
        self.assertTrue(
            spec.origin.endswith('__init__.py'),
            f"core.views should resolve to the package "
            f"__init__.py, got: {spec.origin}",
        )

    def test_canonical_views_still_importable_from_package(self):
        """Sample import-check for functions that were in both the
        deleted file and the live package. If deletion broke the
        package's re-export chain, this fails."""
        from core.views import (  # noqa: F401
            platform_info, health_check, blog_list,
            prompting_settings, execute_agent, agents_discovery_stats,
            llm_chat,
        )

    def test_url_resolver_still_loads_post_deletion(self):
        """The full URL resolver must build cleanly after deletion —
        catches any import chain that depended on the shadowed file."""
        from django.urls import get_resolver
        resolver = get_resolver()
        url_count = sum(1 for _ in resolver.url_patterns)
        # Sanity floor: post-deletion should still have ~1700+ top-level
        # patterns (current count: 1797). A drop to e.g. 200 would
        # indicate the URL conf failed to load.
        self.assertGreater(
            url_count, 1000,
            f"URL resolver loaded only {url_count} top-level patterns "
            "after core/views.py deletion. Expected ~1797. "
            "Likely the deletion broke a URL conf import chain.",
        )
