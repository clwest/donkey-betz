# 24/7 Global AI — Live Intelligence Panel — Architecture Sketch

**Date:** 2026-05-20
**Author:** Claude Code, Session 1116
**Status:** Sketch — pre-implementation. ~3-5 hours of work.
**Companion:** [`24_7_GLOBAL_AI_APP_ATLAS.md`](24_7_GLOBAL_AI_APP_ATLAS.md) § C.5 item #1

---

## A. Goal (one paragraph)

Add a `/now` route to **247globalai.com** that displays live signal clusters from u-d-b — "what 24/7 Global AI has noticed in the last 24 hours." The marketing site stops being a static brochure and starts being *evidence that the platform is actually a 24/7 global AI*. Read-only. Cached. No per-user LLM cost. No user accounts required to view.

---

## B. Architecture (single diagram)

```
┌─────────────────────────┐         ┌────────────────────────────────────┐
│ 247globalai.com         │         │ unified-donkey-betz                │
│ (Next.js on Vercel)     │         │ (Django on Railway)                │
│                         │         │                                    │
│  /now (server comp)     │ ──HTTP──▶ GET /api/public/intelligence/now/  │
│    │                    │  token   │   header: X-Intel-Token=...       │
│    │ next: { revalidate │          │                                    │
│    │   : 300 }          │          │ ┌──────────────────────────────┐  │
│    │                    │ ◀───JSON─│ │ PublicIntelligenceView       │  │
│    ▼                    │  payload │ │ (rest_framework, AllowAny    │  │
│  Render cards           │  ~10 KB  │ │  + custom HeaderTokenAuth)   │  │
│  (gold/ink/cream theme) │          │ └──────────────────────────────┘  │
│                         │          │              │                    │
│                         │          │              ▼                    │
│                         │          │  SignalCluster.objects            │
│                         │          │    .filter(status='active',       │
│                         │          │            detected_at__gte=24h)  │
│                         │          │    .order_by('-strength')[:20]    │
│                         │          │                                    │
│                         │          │  Already populated by             │
│                         │          │  SignalAggregationService          │
│                         │          │  (running on celery-beat)         │
└─────────────────────────┘         └────────────────────────────────────┘
        ▲                                      │
        │ ISR cache hit (≤5 min old)           │ Single DB query
        │ 288 origin fetches/day max           │ ~5-50 ms
        │                                      │
   Public visitors                       Existing infra
```

**Why this shape:**
- **Server-component fetch + ISR** = visitors don't see the API token, u-d-b doesn't serve anonymous traffic, and origin requests are capped at ~288/day no matter how many visitors hit `/now`.
- **Token auth, not "public endpoint"** = if Chris ever wants to rate-limit / rotate / kill the panel, it's one env var change.
- **Read-only slice on existing data** = no new pipelines. The signal clusters are already being computed by `SignalAggregationService` for u-d-b's own internal use.

---

## C. u-d-b side — new public-read endpoint

### C.1 New view

**File:** `core/views_public_intelligence.py` *(new ~60 lines)*

```python
"""
Public-read intelligence endpoint for marketing surfaces (247globalai.com).

Exposes a curated, anonymized slice of SignalCluster. Token-gated via a
shared secret (env: PUBLIC_INTEL_TOKEN) so we can rotate without code change.
NEVER exposes spider_data_ids, raw URLs, or sample_signals — those can
contain scraped excerpts and PII.
"""
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status, throttling
from rest_framework.authentication import BaseAuthentication, exceptions

from core.models_signal_intelligence import SignalCluster
from ai_core.spiders.spider_registry import SPIDER_REGISTRY  # for count


class PublicIntelTokenAuth(BaseAuthentication):
    """Header X-Intel-Token matched against settings.PUBLIC_INTEL_TOKEN."""

    def authenticate(self, request):
        token = request.META.get('HTTP_X_INTEL_TOKEN', '')
        expected = getattr(settings, 'PUBLIC_INTEL_TOKEN', '')
        if not expected:
            raise exceptions.AuthenticationFailed('Endpoint disabled (no token configured)')
        if token != expected:
            raise exceptions.AuthenticationFailed('Invalid intel token')
        # No user identity — token authorizes the route, not a user
        return (None, None)


class PublicIntelThrottle(throttling.SimpleRateThrottle):
    """30 reqs / min per source IP. Generous because Next.js ISR collapses traffic."""
    scope = 'public_intel'
    rate = '30/min'

    def get_cache_key(self, request, view):
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request),
        }


def _public_cluster_dict(c: SignalCluster) -> dict:
    """Hand-shape the JSON. Never serialize internal IDs or raw signal text."""
    return {
        'id': str(c.id),
        'name': c.name,
        'pattern_type': c.pattern_type,
        'pattern_label': c.get_pattern_type_display(),
        'strength': round(c.strength or 0.0, 2),
        'novelty': round(c.novelty or 0.0, 2),
        'confidence': round(c.confidence or 0.0, 2),
        'urgency': round(c.urgency or 0.0, 2),
        'detected_at': c.detected_at.isoformat() if c.detected_at else None,
        # source_breakdown is a count-only dict ({'reddit': 6, 'bluesky': 12})
        # — safe to surface; no URLs/excerpts in there.
        'source_breakdown': c.source_breakdown or {},
        # Keywords: cap to 6, truncate to 40 chars each — defense in depth.
        'keywords': [k[:40] for k in (c.keywords or [])[:6]],
    }


class PublicIntelligenceNowView(APIView):
    """
    GET /api/public/intelligence/now/

    Returns up to 20 recent active SignalClusters + aggregate counters.
    Cache lifetime: ~5 min upstream (Next.js ISR enforces).
    """
    permission_classes = [AllowAny]
    authentication_classes = [PublicIntelTokenAuth]
    throttle_classes = [PublicIntelThrottle]

    def get(self, request):
        window_start = timezone.now() - timedelta(hours=24)

        qs = (
            SignalCluster.objects
            .filter(status='active', detected_at__gte=window_start)
            .order_by('-strength', '-detected_at')
        )
        top = list(qs[:20])

        # Aggregate stats for the editorial caption strip
        total_24h = qs.count()
        # Pattern type tally
        type_counts = {}
        for c in qs:
            type_counts[c.pattern_type] = type_counts.get(c.pattern_type, 0) + 1
        top_patterns = sorted(type_counts.items(), key=lambda kv: -kv[1])[:3]

        payload = {
            'as_of': timezone.now().isoformat(),
            'window_hours': 24,
            'stats': {
                'total_signals_24h': total_24h,
                'top_patterns': [
                    {'type': t, 'label': dict(SignalCluster.PATTERN_TYPE_CHOICES).get(t, t), 'count': n}
                    for t, n in top_patterns
                ],
                'sources_watched': len(SPIDER_REGISTRY),  # 80 today
            },
            'clusters': [_public_cluster_dict(c) for c in top],
        }
        return Response(payload, status=status.HTTP_200_OK)
```

### C.2 URL wiring

**File:** `core/urls.py` *(one new line in the `urlpatterns` block)*

```python
from core.views_public_intelligence import PublicIntelligenceNowView

urlpatterns += [
    path('api/public/intelligence/now/', PublicIntelligenceNowView.as_view(),
         name='public-intel-now'),
]
```

### C.3 CORS — let 247globalai.com origin in

**File:** `core/settings.py` *(amend existing CORS section)*

The site is **server-side fetched** from Next.js, so CORS technically doesn't matter (the request goes from Vercel's edge to Railway, not from a browser). But if you ever want a client-side variant (e.g., live polling on the home page), you'll want:

```python
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',') if ...
# Add: https://247globalai.com, https://www.247globalai.com,
#      https://24-7-ai-global.vercel.app (preview deployments)
```

For Phase 1 (server-side only): **no CORS change needed**. Keep it locked.

### C.4 Environment variable

**Railway env (production):**
```
PUBLIC_INTEL_TOKEN=<random 32-char string, generate with `openssl rand -hex 16`>
```

**Same value on Vercel for 24-7-ai-global:**
```
UDB_API_URL=https://donkey-betz-platform-production.up.railway.app
UDB_PUBLIC_INTEL_TOKEN=<same value>
```

If `PUBLIC_INTEL_TOKEN` is unset on u-d-b's side, the endpoint **rejects every request** — a default-off safety. The `_public_cluster_dict` whitelist + token gate is the entire security surface.

### C.5 Test

**File:** `core/tests/test_public_intel_endpoint.py` *(new ~40 lines)*

```python
import json
from datetime import timedelta
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from core.models_signal_intelligence import SignalCluster


@override_settings(PUBLIC_INTEL_TOKEN='test-token-abc')
class PublicIntelligenceNowViewTests(TestCase):

    def setUp(self):
        SignalCluster.objects.create(
            name='Test demand spike', pattern_type='demand_spike',
            status='active', strength=0.9, confidence=0.8,
            source_breakdown={'reddit': 12}, keywords=['ai', 'agents'],
        )

    def test_token_required(self):
        resp = self.client.get('/api/public/intelligence/now/')
        self.assertEqual(resp.status_code, 401)

    def test_valid_token_returns_payload(self):
        resp = self.client.get(
            '/api/public/intelligence/now/',
            HTTP_X_INTEL_TOKEN='test-token-abc',
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('clusters', data)
        self.assertIn('stats', data)
        # Forbidden internal fields must not leak
        for c in data['clusters']:
            self.assertNotIn('spider_data_ids', c)
            self.assertNotIn('sample_signals', c)

    def test_disabled_when_no_token_configured(self):
        with override_settings(PUBLIC_INTEL_TOKEN=''):
            resp = self.client.get(
                '/api/public/intelligence/now/',
                HTTP_X_INTEL_TOKEN='whatever',
            )
            self.assertEqual(resp.status_code, 401)
```

**u-d-b side total:** ~150 LOC across 3 files. **Effort: ~1.5 hours including review.**

---

## D. 24-7-ai-global side — new route + components

### D.1 Server-fetch wrapper

**File:** `src/lib/intel.ts` *(new ~50 lines)*

```typescript
// Server-side fetch + type contract for the live intel feed.
// Cached via Next.js ISR — origin requests capped at ~288/day.

export type IntelCluster = {
  id: string;
  name: string;
  pattern_type: string;
  pattern_label: string;
  strength: number;
  novelty: number;
  confidence: number;
  urgency: number;
  detected_at: string | null;
  source_breakdown: Record<string, number>;
  keywords: string[];
};

export type IntelPayload = {
  as_of: string;
  window_hours: number;
  stats: {
    total_signals_24h: number;
    top_patterns: { type: string; label: string; count: number }[];
    sources_watched: number;
  };
  clusters: IntelCluster[];
};

const REVALIDATE_SECONDS = 300; // 5-minute ISR

export async function fetchLiveIntelligence(): Promise<IntelPayload | null> {
  const base = process.env.UDB_API_URL;
  const token = process.env.UDB_PUBLIC_INTEL_TOKEN;
  if (!base || !token) {
    console.warn('[intel] UDB_API_URL or UDB_PUBLIC_INTEL_TOKEN not set');
    return null;
  }

  try {
    const res = await fetch(`${base}/api/public/intelligence/now/`, {
      headers: { 'X-Intel-Token': token },
      next: { revalidate: REVALIDATE_SECONDS },
    });
    if (!res.ok) {
      console.warn(`[intel] u-d-b returned ${res.status}`);
      return null;
    }
    return (await res.json()) as IntelPayload;
  } catch (e) {
    console.warn('[intel] fetch failed:', e);
    return null;
  }
}
```

### D.2 The `/now` page

**File:** `src/app/now/page.tsx` *(new ~80 lines)*

```tsx
import { SiteHeader } from '@/components/SiteHeader';
import { SiteFooter } from '@/components/SiteFooter';
import { fetchLiveIntelligence } from '@/lib/intel';
import { ClusterCard } from '@/components/intel/ClusterCard';
import { IntelStatsStrip } from '@/components/intel/IntelStatsStrip';
import { AllQuietPanel } from '@/components/intel/AllQuietPanel';

export const revalidate = 300; // 5 min — matches fetch ISR

export const metadata = {
  title: 'Now — 24/7 Global AI',
  description:
    'Live signals across 80 sources, clustered by 24/7 Global AI in the last 24 hours.',
};

export default async function NowPage() {
  const intel = await fetchLiveIntelligence();

  return (
    <main className="relative isolate overflow-hidden bg-ink text-cream noise min-h-screen">
      <SiteHeader />

      <section className="mx-auto max-w-[1400px] px-6 pt-16 pb-24 lg:px-10 lg:pt-24">
        <div className="flex items-center gap-3 font-mono text-[10.5px] uppercase tracking-[0.34em] text-gold">
          <span className="h-px w-12 bg-gold/60" />
          Live Intelligence · Last 24h
        </div>

        <h1 className="mt-8 font-display text-[clamp(2.5rem,6vw,5rem)] font-medium leading-[0.96] tracking-[-0.02em]">
          <span className="block">What we&apos;ve</span>
          <span className="block italic gold-text">noticed.</span>
        </h1>

        <p className="mt-8 max-w-2xl text-[17px] leading-relaxed text-mist">
          24/7 Global AI watches {intel?.stats.sources_watched ?? 80} sources
          across markets, news, science, legal, social, and code. Below: the
          patterns we&apos;ve clustered in the last 24 hours. No commentary, no
          spin — just the signals, as they came in.
        </p>

        {intel ? (
          <>
            <IntelStatsStrip stats={intel.stats} asOf={intel.as_of} />

            <div className="mt-16 grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-3">
              {intel.clusters.map((c) => (
                <ClusterCard key={c.id} cluster={c} />
              ))}
            </div>

            {intel.clusters.length === 0 && <AllQuietPanel />}
          </>
        ) : (
          <AllQuietPanel
            reason="The wire is dark for a moment. Refresh in a few minutes."
          />
        )}
      </section>

      <SiteFooter />
    </main>
  );
}
```

### D.3 Components

Three small editorial components matching the existing site aesthetic:

**`src/components/intel/IntelStatsStrip.tsx`** (~40 lines)
- Three big-number stats: total signals 24h, top pattern, sources watched
- Editorial caption line: "As of {asOf}, watching {sources_watched} sources."

**`src/components/intel/ClusterCard.tsx`** (~60 lines)
- Pattern label as small uppercase mono header (matches site's `font-mono text-[10.5px]` style)
- Cluster name as display-font heading
- Strength + confidence as ring/bar viz (use existing gold/ink palette)
- Source breakdown as inline chips: `reddit · 12   bluesky · 6`
- Keywords as italic mist-tone
- Subtle "detected {relative time}" line

**`src/components/intel/AllQuietPanel.tsx`** (~25 lines)
- Editorial "all quiet" state. Same gold/ink aesthetic.
- "All quiet on the wire. The system is watching {sources_watched} sources right now."

**24-7-ai-global side total:** ~250 LOC across 5 files. **Effort: ~2-3 hours including styling.**

### D.4 Navigation entry

**File:** `src/components/SiteHeader.tsx` *(add one nav item)*

Add `<a href="/now">Now</a>` (or "Live" / "Intelligence") to the existing top nav.

---

## E. Failure modes

| Mode | What happens | Visitor sees |
|---|---|---|
| u-d-b down (Railway outage) | `fetchLiveIntelligence` returns `null` | `AllQuietPanel` with "The wire is dark for a moment." |
| u-d-b returns empty queryset (no active clusters in 24h) | Payload returns `clusters: []` | `AllQuietPanel` with "All quiet" message |
| u-d-b returns malformed JSON | Parse error caught, returns `null` | Same as outage |
| Wrong/missing token | u-d-b returns 401, caller logs and shows "wire is dark" | Visitor sees `AllQuietPanel` (graceful) |
| Vercel ISR cache stale > 5 min but fetch slow | Next.js serves stale-while-revalidate | Visitor sees last-cached snapshot |
| Rate limit hit (>30/min from same IP) | u-d-b returns 429 | Same as outage |

**No failure mode breaks the page.** Worst case is the "all quiet" panel, which is on-brand and recoverable.

---

## F. Cost & rate envelope

| Resource | Per-visit cost | Per-day max |
|---|---|---|
| u-d-b LLM tokens | $0 | $0 — no LLM in the path |
| u-d-b DB queries | 1 query per ISR miss | ~288/day (5-min revalidate × 24h) |
| u-d-b CPU | ~5-50 ms per query | trivial |
| Vercel function executions | 1 per ISR miss | ~288/day (well under free tier) |
| Vercel bandwidth | ~10-15 KB per visitor | bounded by visitor count |
| ElevenLabs / Runway / Stability | $0 | $0 — no media in the path |

**The expensive surface (LLM, media APIs) is not in this path.** This is what makes it a Phase-0-free quick win — none of the COST_SURVIVAL_AUDIT blockers apply.

---

## G. Open decisions (small, decide during build)

1. **Page route name** — `/now`, `/live`, `/intelligence`, `/wire`, `/signals`? My pick: `/now` (matches editorial tone of "Plate 01 · The proprietor of 24/7 Global AI").

2. **Filter for cluster cleanliness.** Some pattern types might be ugly or off-brand for the public page (e.g., `knowledge_gap` could read as a weakness signal). Two options:
   - Show all 10 pattern types as-is (authentic, raw).
   - Whitelist only 4-5 "marketable" patterns (`demand_spike`, `trend_emergence`, `market_movement`, `opportunity_window`, `competitive_signal`).

   Recommend whitelist for v1, expand later.

3. **Auto-refresh.** Should the page client-poll every 60s for fresh data, or just rely on visitor-triggered ISR? Recommend **no auto-refresh** for v1 — pure server-rendered, simpler, lower cost, lower visual noise.

4. **"Read more" depth.** Each ClusterCard could link to a detail page with the spider source mix, related deliverables, etc. Recommend **NO detail pages** for v1 — keep the panel as a moodboard, not a portal. Detail pages would re-introduce auth / per-cluster pages / SEO sprawl.

5. **Spider name exposure.** `source_breakdown` keys are spider names (`reddit`, `bluesky`, `polygon`). Should those be the displayed labels, or mapped to friendlier names (`Reddit`, `Bluesky`, `Polygon`)? Recommend a simple title-case map in `intel.ts` — 80 entries, one-time write.

6. **Internationalization.** Hardcoded English in the v1. Defer i18n until/unless a non-English vertical launches.

---

## H. Implementation checklist (3-5 hours)

**On u-d-b** (`docs/character-os-merge-proposal` branch or a fresh branch):
- [ ] Create `core/views_public_intelligence.py` (§ C.1)
- [ ] Add URL pattern to `core/urls.py` (§ C.2)
- [ ] Add `PUBLIC_INTEL_TOKEN` to Railway env
- [ ] Add `core/tests/test_public_intel_endpoint.py` (§ C.5)
- [ ] Run `python manage.py test core.tests.test_public_intel_endpoint`
- [ ] Manual probe: `curl -H "X-Intel-Token: $TOKEN" https://donkey-betz-platform-production.up.railway.app/api/public/intelligence/now/`
- [ ] Confirm CORS unchanged (server-side fetch only in v1)

**On 24-7-ai-global** (new branch):
- [ ] Add `UDB_API_URL` + `UDB_PUBLIC_INTEL_TOKEN` to Vercel env
- [ ] Create `src/lib/intel.ts` (§ D.1)
- [ ] Create `src/app/now/page.tsx` (§ D.2)
- [ ] Create `src/components/intel/{IntelStatsStrip,ClusterCard,AllQuietPanel}.tsx` (§ D.3)
- [ ] Add nav entry to `SiteHeader.tsx` (§ D.4)
- [ ] Local dev: `pnpm dev` → visit http://localhost:3000/now
- [ ] Deploy preview to Vercel, verify with Chris
- [ ] Promote to production

**Forward-drift guards** (post-ship):
- [ ] Add `verify_doc_claims` entry: "public-intel endpoint returns 401 without token"
- [ ] Add freshness check: if `intel.as_of` more than 1h old, alert in Discord
- [ ] Document in `docs/topics/external-integrations.md` (or new) — the contract is stable

---

## I. Why this is the right first integration

| Test | Verdict |
|---|---|
| Showcases the brand promise ("always on, always smart, always global")? | **Yes** — literally renders the signals u-d-b is processing right now |
| Adds zero cost-of-goods to per-visitor cost? | **Yes** — no LLM, no media APIs |
| Survives any visitor traffic spike? | **Yes** — ISR caps origin fetches at ~288/day regardless of visitors |
| Reversible if it's a bad call? | **Yes** — remove the route + revoke the token = gone in 5 minutes |
| Doesn't depend on Phase 0 cost work? | **Yes** — no multi-tenancy, no per-workspace billing |
| Improves credibility of every other Suite product on the site? | **Yes** — proves the platform behind the studio is real |
| Sets the pattern for other u-d-b → 247globalai integrations? | **Yes** — token + ISR + read-only slice = template for "live changelog," "advisor wisdom," etc. |

This is the minimum-viable proof that 24/7 Global AI is *actually* a 24/7 global AI.

---

## J. References

- `core/models_signal_intelligence.py` — SignalCluster model
- `core/views_audit_api.py:72` — existing (auth-gated) SignalClusterViewSet
- `core/serializers_audit.py:82` — existing SignalCluster serializers (don't reuse — they expose internal IDs)
- `core/urls.py` — URL router registration
- `core/settings.py` — CORS config (no change for v1)
- `ai_core/spiders/spider_registry.py` — SPIDER_REGISTRY count
- `core/services/signal_aggregation_service.py` — produces the SignalClusters this endpoint reads
- `frontend/src/App.tsx` *(on u-d-b side)* — pattern reference, not used
- `24-7-ai-global/src/lib/products.ts` — pattern for typed data + page structure
- `24-7-ai-global/src/app/page.tsx` — current homepage aesthetic to match
- `docs/24_7_GLOBAL_AI_APP_ATLAS.md` § C.5 — strategic context

---

**End of sketch.** Hand to Rigby for review, then split into two PRs (one per repo) and ship.
