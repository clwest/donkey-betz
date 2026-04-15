#!/usr/bin/env python3
import os, sys, math, argparse
from datetime import timedelta

import logging
logger = logging.getLogger(__name__)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
import django
django.setup()

from django.utils import timezone
from django.db import transaction
from pgvector.django import CosineDistance

from persistence.services import EmbeddingService
from persistence.models import UnifiedEmbedding, SpiderData, SpiderDataRoute


def mean_vec(vecs):
    if not vecs:
        return None
    d = len(vecs[0])
    acc = [0.0] * d
    for v in vecs:
        vv = [float(x) for x in v]
        for i, x in enumerate(vv):
            acc[i] += x
    n = float(len(vecs))
    return [x / n for x in acc]


def python_cosine(a, b):
    num = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return num / (na * nb)


def clamp01(x):
    return max(0.0, min(1.0, float(x)))


def fetch_agent_profile_vec(agent, seed_query, primary_days, secondary_days, svc):
    now = timezone.now()
    p_window = now - timedelta(days=primary_days)
    s_window = now - timedelta(days=secondary_days)

    def _pull_window(start_time):
        routes = (SpiderDataRoute.objects
                  .filter(is_active=True, target_agent=agent, created_at__gte=start_time)
                  .order_by("-created_at")
                  .select_related("spider_data"))
        ids = list(routes.values_list("spider_data_id", flat=True)[:500])
        if not ids:
            return []
        embs = (UnifiedEmbedding.objects
                .filter(content_type="spider_data", content_id__in=ids, embedding__isnull=False)
                .values_list("embedding", flat=True))
        return list(embs)

    vecs = _pull_window(p_window) or _pull_window(s_window)
    if vecs:
        m = mean_vec(vecs)
        if m:
            print(f"[learn] recent routed to {agent}: {len(vecs)} (profile=mean)")
            return m

    print(f"[learn] recent routed to {agent}: 0")
    print("[learn] no history — using seed query")
    return svc.generate_embedding_vector(seed_query)


def gather_candidates(platforms, days):
    cutoff = timezone.now() - timedelta(days=days)
    spider_q = SpiderData.objects.filter(is_active=True, created_at__gte=cutoff)
    if platforms:
        spider_q = spider_q.filter(source_platform__in=list(platforms))
    spider_ids = list(spider_q.values_list("id", flat=True)[:50000])  # guardrail
    if not spider_ids:
        return UnifiedEmbedding.objects.none(), []
    q = (UnifiedEmbedding.objects
         .filter(content_type="spider_data", content_id__in=spider_ids, embedding__isnull=False))
    return q, spider_ids


def main():
    ap = argparse.ArgumentParser(description="One-shot learner + router")
    ap.add_argument("--agent", required=True)
    ap.add_argument("--seed", default="sell AI templates and micro-gigs now")
    ap.add_argument("--platforms", default="")
    ap.add_argument("--top", type=int, default=40)
    ap.add_argument("--db-limit", type=int, default=300)
    ap.add_argument("--py-fallback-cap", type=int, default=3000)
    ap.add_argument("--primary-days", type=int, default=14)
    ap.add_argument("--secondary-days", type=int, default=60)
    ap.add_argument("--pool-days", type=int, default=45)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    platforms = set([p.strip() for p in args.platforms.split(",") if p.strip()]) if args.platforms else set()

    SPORTS_PLATFORMS_PREFERRED = {
        "yahoo_finance", "seekingalpha", "bloomberg_terminal", "reuters_eikon",
        "coingecko", "etherscan", "opensea", "horse_racing", "combat_sports",
    }
    REDDIT_LITE = {"reddit"}

    svc = EmbeddingService()

    # 1) Learn profile
    qv = fetch_agent_profile_vec(
        agent=args.agent,
        seed_query=args.seed,
        primary_days=args.primary_days,
        secondary_days=args.secondary_days,
        svc=svc,
    )

    # 2) Candidate pool
    q, spider_ids = gather_candidates(platforms, args.pool_days)
    print(f"[candidates] available: {len(spider_ids)} (subset for DB ranking will be limited to {args.db_limit})")

    ranked_rows = []

    # --- DB annotate path (FIXED: order BEFORE slice; no prior slice on q) ---
    try:
        q_anno = (q.annotate(distance=CosineDistance("embedding", qv))
                    .order_by("distance")
                    .values("content_id", "distance")[:args.db_limit])

        spider_map = {s.id: s for s in SpiderData.objects.filter(id__in=[r["content_id"] for r in q_anno])}
        for h in q_anno:
            s = spider_map.get(h["content_id"])
            if not s:
                continue
            dist = float(h["distance"])
            sem = 1.0 - max(0.0, min(1.0, dist))
            opp = float(s.opportunity_score or 0.0)

            if s.source_platform in SPORTS_PLATFORMS_PREFERRED:
                plat_bonus = 0.12
            elif s.source_platform in REDDIT_LITE:
                plat_bonus = 0.04
            else:
                plat_bonus = 0.08 if s.source_platform else 0.0

            score = clamp01(sem + plat_bonus + 0.10 * opp)
            ranked_rows.append((score, dist, s.id, s.source_platform, (s.title or "")[:120], opp))
        print(f"[rank] annotate db-ranked: {len(ranked_rows)}")
    except Exception as e:
        print(f"[rank] annotate failed: {e}")

    # 3) Python fallback if needed
    if not ranked_rows:
        cap_ids = spider_ids[:args.py_fallback_cap]
        emb_rows = list(
            UnifiedEmbedding.objects.filter(
                content_type="spider_data", content_id__in=cap_ids, embedding__isnull=False
            ).values("content_id", "embedding")
        )
        s_map = {s.id: s for s in SpiderData.objects.filter(id__in=[r["content_id"] for r in emb_rows])}
        for r in emb_rows:
            s = s_map.get(r["content_id"])
            if not s:
                continue
            cos = python_cosine(qv, [float(x) for x in r["embedding"]])
            dist = 1.0 - clamp01(cos)
            sem = clamp01(cos)
            opp = float(s.opportunity_score or 0.0)

            if s.source_platform in SPORTS_PLATFORMS_PREFERRED:
                plat_bonus = 0.12
            elif s.source_platform in REDDIT_LITE:
                plat_bonus = 0.04
            else:
                plat_bonus = 0.08 if s.source_platform else 0.0

            score = clamp01(sem + plat_bonus + 0.10 * opp)
            ranked_rows.append((score, dist, s.id, s.source_platform, (s.title or "")[:120], opp))

        print(f"[fallback] python-ranked: {len(ranked_rows)}")

    # 4) Route top-N
    ranked_rows.sort(key=lambda t: (-t[0], t[1]))
    winners = ranked_rows[:args.top]

    routed = 0
    if not args.dry_run:
        with transaction.atomic():
            for _, _, sid, _, _, _ in winners:
                try:
                    sd = SpiderData.objects.get(id=sid)
                    sd.route_to_agent(args.agent, "high")
                    routed += 1
                except Exception as _e:
                    logger.warning(
                        "learn_route_one_shot.main: swallowed (%s: %s) — degraded",
                        type(_e).__name__, _e,
                    )

    print(f"  routed={routed} / {len(winners)}\n")
    print("  [top 20]")
    for row in winners[:20]:
        score, dist, sid, plat, title, opp = row
        print(f"   • {sid} | {plat or 'unknown':12} | score={score:.3f} dist={dist:.3f} opp={opp:.2f} | {title or ''}")
    print("\n=== DONE ===")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"[fatal] {exc}")
        sys.exit(1)