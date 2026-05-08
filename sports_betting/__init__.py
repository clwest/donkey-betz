# ARCHIVE-CANDIDATE — Session 1113 review (Session 1111 PR-C queue).
# Classification: planned Django app, never wired up.
# Why: `sports_betting` is NOT in `core.settings.INSTALLED_APPS`. The only
# external importer is `ai_core/routing.py:8`, which itself is not the
# active routing entry — `core/asgi.py` uses `core.routing.websocket_urlpatterns`,
# not `ai_core.routing`. `models.py` is empty stub, `views.py` returns
# hardcoded mock data, no migrations were ever produced for this app.
# The active sports surface lives in `sports/` (a separate, real app).
# Note: the `sports_betting_*` strings that appear in
# `core/migrations/0019_*` and `core/migrations/0254_*` are
# learning-domain enum values, not Django app references — they are
# independent of this directory.
# Decision pending: Rigby/Chris call on whether this app is "future
# surface to revive" or "abandoned experiment to archive." Untouched
# until then.
# See: docs/handoffs/SESSION_1111_DEEPER_REVIEW_MAP.md
