---
originating_session: 1071
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 1071 — PA Platform-Wide Awareness + Control

**Date:** February 23, 2026
**PR:** #1442 (merged)
**Branch:** `feat/pa-platform-awareness`

---

## What Happened

Implemented all 7 parts of the PA Platform Awareness spec (originally authored by the PA itself in conversation `pa-644ceceec57b`). The PA can now enumerate all frontend routes, verify deployments, and generate media through a unified studio tool.

---

## Changes (14 files, 1452 insertions)

### Part 1: Frontend Capabilities Manifest
| File | Change |
|------|--------|
| `frontend/src/appManifest.ts` | 30 routes, 3 studio configs, 8 capability flags |
| `frontend/scripts/generate-manifest.mjs` | Postbuild script → `dist/__manifest.json` |
| `frontend/package.json` | `postbuild` hook |

### Part 2: RBAC-Filtered Manifest Endpoint
| File | Change |
|------|--------|
| `core/views_app_manifest.py` | `GET /api/app/manifest/` — filters routes by user role |
| `core/urls.py` | URL pattern before React catch-all |

### Part 3: UI Smoke Test Runner
| File | Change |
|------|--------|
| `core/management/commands/run_ui_smoke.py` | Playwright management command (dev/CI only) |

### Part 4: Deploy Verification
| File | Change |
|------|--------|
| `core/views_deploy_verify.py` | `POST /api/deploy/verify/` — 8 hardcoded endpoint checks |
| `core/management/commands/run_smoke_tests.py` | CLI wrapper for `railway run` / CI |

### Part 5: Unified Studio PA Tool
| File | Change |
|------|--------|
| `core/services/pa_tool_schemas.py` | `studio_tool` schema (5 actions) |
| `core/services/tool_dispatcher.py` | `_handle_studio` — delegates to existing agents, zero duplication |

### Part 6: PA Service Account
| File | Change |
|------|--------|
| `core/management/commands/setup_pa_service_account.py` | Creates `pa-service` user + DRF token |
| `Procfile` | Runs on every deploy (idempotent) |

### Part 7: Acceptance Tests
| File | Change |
|------|--------|
| `tests/test_platform_awareness.py` | 8 tests across 5 classes |

### PA Tool Details

**`platform_awareness_tool`** (5 actions):
- `get_manifest` — full manifest (routes, studios, capabilities)
- `list_routes` — filter by category/auth
- `check_route` — verify a specific route exists
- `system_overview` — summary counts
- `verify_deploy` — run 8 endpoint health checks (admin only)

**`studio_tool`** (5 actions):
- `generate_image` — delegates to ImageAgent
- `generate_video` — delegates to VideoAgent
- `generate_audio` — delegates to AudioAgent
- `job_status` — checks CeleryTaskEvent by task_id
- `list_jobs` — recent ImageHistory + VideoHistory + AudioHistory

---

## Key Numbers

| Metric | Value |
|--------|-------|
| PA tool schemas | 43 → **45** |
| PA tool handlers | 63 → **65** |
| Frontend routes in manifest | **30** |
| Studios configured | **3** (image, video, audio) |
| Capability flags | **8** |
| Deploy verification checks | **8** |
| Acceptance tests | **8** |

---

## Deploy Notes

- `setup_pa_service_account` runs automatically on every deploy via Procfile release command
- `__manifest.json` is generated at frontend build time — if frontend isn't rebuilt, backend falls back to hardcoded route list
- `deploy_verify` endpoint calls the platform's own endpoints via `requests` — needs the server to be fully up
- Playwright is NOT a production dependency — `run_ui_smoke` command lazy-imports it

---

## Not Done / Next Steps

- Verify all 8 deploy checks pass on Railway after deploy
- Test PA conversations: "What routes are available?", "Generate an image of a sunset"
- Run acceptance tests against Railway: `PA_SERVICE_TOKEN=... pytest tests/test_platform_awareness.py -v`
- Consider adding `__manifest.json` to Railway frontend build step
- 25+ other untested PA tools still pending validation
