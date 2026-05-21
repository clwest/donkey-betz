---
title: Verifiable Facts — 24/7 Global AI
slug: facts
section: Facts
status: reference
audience: public-everyone
voice: factual
sources:
  - PLATFORM_INVENTORY.md (engine runtime inventory, regenerated 2026-05-21)
  - 24-7-ai-global/src/lib/products.ts (public taxonomy)
  - 247globalai.com (live marketing site)
updated: 2026-05-21
---

# Verifiable Facts — 24/7 Global AI

Every number and falsifiable claim cited anywhere in this corpus, with a source line.
The spokesperson reads this when defending a claim. If a number isn't here, the
spokesperson paraphrases ("dozens", "more than a hundred") rather than quoting.

## Facts table

| Claim | Source | Source date | Tier |
|---|---|---|---|
| 4 buyable products in the Suite | products.ts (`PRODUCTS` array) | 2026-05-20 | public-page-derived |
| 4 pillars: Intelligence, Automation, Innovation, Impact | products.ts (`PILLARS` array) | 2026-05-20 | public-page-derived |
| 3 Verticals: AI Content Studio, VehicleMatch, JobFlow | products.ts (`VERTICALS` array) | 2026-05-20 | public-page-derived |
| 10 Lab entries (engine works + OSS + founder-toolkit triplet + Wave 2 reveals) | products.ts (`LAB` array) | 2026-05-20 | public-page-derived |
| 5 Channels | products.ts (`CHANNELS` array) | 2026-05-20 | public-page-derived |
| Hero stats: 22 Works in Motion · 08 Live in Market · 03 Verticals · 10 Engine Works | products.ts (`STATS`) | 2026-05-20 | public-page-derived |
| 80 source watchers across 41 categories (The Network) | PLATFORM_INVENTORY.md § Spiders | 2026-05-21 | runtime-derived |
| 10 pattern types detected by signal clustering | PLATFORM_INVENTORY.md § Signal Intelligence | 2026-05-21 | runtime-derived |
| 30 advisors in The Council (16 named figures + 14 domain specialists) | products.ts (LAB[XIII] elevator) | 2026-05-20 | public-page-derived |
| Live intelligence wire at `/now` refreshed every 5 minutes (ISR) | 247globalai.com (live behavior) | 2026-05-20 | public-page-derived |
| Mentor Forge: Free → $99/mo | products.ts (PRODUCTS[0].pricing) | 2026-05-20 | public-page-derived |
| Pitch Deck Forge: Free → $79/mo | products.ts (PRODUCTS[1].pricing) | 2026-05-20 | public-page-derived |
| Contract Concierge: Free → $79/mo | products.ts (PRODUCTS[2].pricing) | 2026-05-20 | public-page-derived |
| Deal Flow Tracker: Free → $99/mo | products.ts (PRODUCTS[3].pricing) | 2026-05-20 | public-page-derived |
| context-kit installable via `pip install contextkit-ai` | products.ts (LAB[VIII].install) | 2026-05-20 | public-page-derived |
| Studio pivot to 24/7 Global AI brand: May 2026 | SESSION_1116 handoffs | 2026-05-20 | manually maintained |
| Tagline: "Always on. Always smart. Always global." | products.ts brand voice + 247globalai.com | 2026-05-20 | public-page-derived |
| Motto: "An Agentic AI Operating Partner" | memory/project_247_global_ai_brand_locked.md | 2026-05-20 | manually maintained |
| Studio domain: 247globalai.com (production, live) | live site + memory/project_247_global_ai_brand_locked.md | 2026-05-20 | public-page-derived |
| Live ledger of recent deliverables at `/shipped` | 247globalai.com/shipped | 2026-05-20 | public-page-derived |

## Source tiers

- **runtime-derived** — regenerable via `python manage.py generate_platform_inventory`.
  Trust until the command says otherwise. Re-verify whenever the engine ships meaningfully
  new capability.
- **public-page-derived** — visible on the marketing site or in `products.ts`. Trust
  until the page or file changes. Re-verify on every brand or pricing update.
- **manually maintained** — written once. Review on every corpus refresh.

## Refresh discipline

When the engine's runtime inventory regenerates, every `runtime-derived` row must be
re-verified and its `Source date` updated. When `products.ts` changes, every
`public-page-derived` row must be re-verified. The corpus is **not** considered fresh
unless this table is fresh.

## Off-limits

- Do not cite a number not in this table.
- Do not paraphrase a number from this table inaccurately — if the table says "80
  sources", the spokesperson says "eighty sources", not "around a hundred sources" and
  not "dozens of sources" either.
- If a row's `Source date` is more than 90 days old, the spokesperson paraphrases
  rather than quotes that row's number until it's re-verified.
- Do not invent additional facts even if they seem like they should be true — add them
  to this table first, with a citable source, then they can be quoted.
