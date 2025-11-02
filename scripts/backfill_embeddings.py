#!/usr/bin/env python3
"""
One-shot embedding backfill & vector fix script.

Targets:
  1) AgentKnowledge: OneToOne `embedding` is NULL
  2) SpiderData:     OneToOne `embedding` is NULL
  3) UnifiedEmbedding: existing rows with vector NULL (legacy shells)

Also:
  * normalizes vector length to DB dimension (default 1536)
  * fixes invalid vectors (all-zeros / NaNs) to avoid cosine NaN
  * quick smoke test with CosineDistance at the end

Usage:
  python scripts/backfill_embeddings.py --model text-embedding-3-small --batch-size 25
"""

import os
import sys
import math
import time
import argparse
from typing import Iterable, Optional, Tuple, List

# --- Django bootstrap --------------------------------------------------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
import django  # noqa: E402
django.setup()

from django.db.models import Q  # noqa: E402
from django.utils import timezone  # noqa: E402

# Project models/services
from persistence.models import UnifiedEmbedding  # noqa: E402
# If these live elsewhere in your project, adjust imports:
from persistence.models import AgentKnowledge  # noqa: E402
from persistence.models import SpiderData      # noqa: E402

# pgvector smoke test helper
from pgvector.django import CosineDistance  # noqa: E402
from django.db.models import F  # noqa: E402


# Prefer your project EmbeddingService if available (it also creates UnifiedEmbedding w/ metadata)
_EmbeddingService = None
try:
    from persistence.services import EmbeddingService  # type: ignore
    _EmbeddingService = EmbeddingService()
except Exception:
    _EmbeddingService = None

# Fallback: call OpenAI directly
_openai_client = None
def _ensure_openai():
    global _openai_client
    if _openai_client is not None:
        return _openai_client
    try:
        from openai import OpenAI  # stainless client
        _openai_client = OpenAI()
        return _openai_client
    except Exception as e:
        raise RuntimeError(f"OpenAI client not available and EmbeddingService missing: {e}")


# --- Vector helpers ----------------------------------------------------------

def _chunk_text(text: str, max_chars: int = 6000) -> List[str]:
    text = text or ""
    if len(text) <= max_chars:
        return [text]
    out, i = [], 0
    while i < len(text):
        out.append(text[i:i+max_chars])
        i += max_chars
    return out

def _mean_pool(vectors: List[List[float]]) -> List[float]:
    if not vectors:
        return []
    dim = len(vectors[0])
    acc = [0.0] * dim
    for v in vectors:
        for j in range(min(dim, len(v))):
            acc[j] += float(v[j])
    n = float(len(vectors))
    return [x / n for x in acc]

def _embed_text_openai(text: str, model: str) -> List[float]:
    client = _ensure_openai()
    chunks = _chunk_text(text)
    vecs = []
    for ch in chunks:
        resp = client.embeddings.create(model=model, input=ch, encoding_format="float")
        vecs.append(resp.data[0].embedding)
    return _mean_pool(vecs)

def _fix_vector(vec: List[float]) -> List[float]:
    """Replace NaNs, ensure not all-zero (avoid cosine NaN)."""
    if not vec:
        return vec
    cleaned = []
    is_zero = True
    for x in vec:
        f = float('nan') if x is None else float(x)
        if math.isnan(f) or math.isinf(f):
            f = 0.0
        if f != 0.0:
            is_zero = False
        cleaned.append(f)
    if is_zero:
        # nudge a single dimension so norm != 0
        cleaned[0] = 1e-9
    return cleaned

def _reshape(vec: List[float], target_dim: int, strategy: str) -> List[float]:
    if len(vec) == target_dim:
        return vec
    if strategy == "pad":
        return (vec + [0.0] * target_dim)[:target_dim]
    if strategy == "truncate":
        return vec[:target_dim]
    # default: error
    raise ValueError(f"Vector dimension {len(vec)} != target {target_dim} (use --shape pad|truncate to override)")

def _prepare_vec(vec: List[float], target_dim: int, shape_policy: str) -> List[float]:
    vec = _fix_vector(list(vec))
    vec = _reshape(vec, target_dim, shape_policy)
    return vec


# --- UnifiedEmbedding creation/update ----------------------------------------

def _make_unified_embedding_payload(*, content_type: str, content_id, title: str, text: str,
                                    source_system: str, creator_agent: Optional[str],
                                    model_name: str, vector: List[float]) -> dict:
    return dict(
        creator_agent=creator_agent or "system",
        content_type=content_type,
        content_id=content_id,
        content_text=text or "",
        content_title=title or "",
        content_metadata={},
        embedding_model=model_name,
        embedding=vector,
        embedding_dimension=len(vector) if vector else 1536,
        source_system=source_system,
        importance_score=0.5,
        relevance_score=0.5,
        confidence_score=0.5,
    )

def _create_or_update_unified_embedding(payload: dict, *, dry_run: bool) -> Tuple[Optional[UnifiedEmbedding], bool]:
    if dry_run:
        print(f"[DRY] Upsert UnifiedEmbedding ({payload['content_type']}:{payload['content_id']}) dim={payload['embedding_dimension']}")
        return None, True
    ue = UnifiedEmbedding.objects.filter(
        content_type=payload["content_type"], content_id=payload["content_id"]
    ).first()
    if ue:
        for k, v in payload.items():
            setattr(ue, k, v)
        ue.save()
        return ue, False
    else:
        ue = UnifiedEmbedding.objects.create(**payload)
        return ue, True


# --- Backfill routines -------------------------------------------------------

def backfill_agent_knowledge(model_name: str, target_dim: int, shape: str,
                             batch_size: int, limit: Optional[int], sleep_s: float, dry_run: bool) -> int:
    qs = AgentKnowledge.objects.filter(Q(embedding__isnull=True) & Q(is_active=True)).order_by("id")
    processed = 0
    while True:
        if limit is not None and processed >= limit:
            break
        page = list(qs[processed: processed + batch_size])
        if not page:
            break
        for ak in page:
            if limit is not None and processed >= limit:
                break
            # compose text
            text = (ak.title or "") + "\n\n" + (ak.summary or "")
            if isinstance(ak.content, dict):
                for key in ("description", "steps", "solution", "details"):
                    if key in ak.content:
                        text += f"\n\n{ak.content[key]}"
            # embed
            if _EmbeddingService:
                if dry_run:
                    print(f"[DRY] EmbeddingService.create_embedding(agent_knowledge id={ak.id})")
                else:
                    vec = _EmbeddingService.generate_embedding_vector(text, model=model_name)
                    vec = _prepare_vec(vec, target_dim, shape)
                    payload = _make_unified_embedding_payload(
                        content_type="agent_knowledge",
                        content_id=ak.id,
                        title=ak.title,
                        text=text,
                        source_system="agents",
                        creator_agent=ak.agent_name,
                        model_name=model_name,
                        vector=vec,
                    )
                    ue, _ = _create_or_update_unified_embedding(payload, dry_run=False)
                    ak.embedding = ue
                    ak.save(update_fields=["embedding"])
            else:
                vec = _embed_text_openai(text, model_name)
                vec = _prepare_vec(vec, target_dim, shape)
                payload = _make_unified_embedding_payload(
                    content_type="agent_knowledge",
                    content_id=ak.id,
                    title=ak.title,
                    text=text,
                    source_system="agents",
                    creator_agent=ak.agent_name,
                    model_name=model_name,
                    vector=vec,
                )
                ue, _ = _create_or_update_unified_embedding(payload, dry_run=dry_run)
                if not dry_run:
                    ak.embedding = ue
                    ak.save(update_fields=["embedding"])

            processed += 1
            if sleep_s:
                time.sleep(sleep_s)
    return processed


def backfill_spider_data(model_name: str, target_dim: int, shape: str,
                         batch_size: int, limit: Optional[int], sleep_s: float, dry_run: bool) -> int:
    qs = SpiderData.objects.filter(Q(embedding__isnull=True) & Q(is_active=True)).order_by("id")
    processed = 0
    while True:
        if limit is not None and processed >= limit:
            break
        page = list(qs[processed: processed + batch_size])
        if not page:
            break
        for sd in page:
            if limit is not None and processed >= limit:
                break

            text = (sd.title or "") + "\n\n" + (sd.content or "")
            if _EmbeddingService:
                if dry_run:
                    print(f"[DRY] EmbeddingService.create_embedding(spider_data id={sd.id})")
                else:
                    vec = _EmbeddingService.generate_embedding_vector(text, model=model_name)
                    vec = _prepare_vec(vec, target_dim, shape)
                    payload = _make_unified_embedding_payload(
                        content_type="spider_data",
                        content_id=sd.id,
                        title=sd.title,
                        text=text,
                        source_system="spiders",
                        creator_agent=sd.spider_name,
                        model_name=model_name,
                        vector=vec,
                    )
                    ue, _ = _create_or_update_unified_embedding(payload, dry_run=False)
                    sd.embedding = ue
                    sd.save(update_fields=["embedding"])
            else:
                vec = _embed_text_openai(text, model_name)
                vec = _prepare_vec(vec, target_dim, shape)
                payload = _make_unified_embedding_payload(
                    content_type="spider_data",
                    content_id=sd.id,
                    title=sd.title,
                    text=text,
                    source_system="spiders",
                    creator_agent=sd.spider_name,
                    model_name=model_name,
                    vector=vec,
                )
                ue, _ = _create_or_update_unified_embedding(payload, dry_run=dry_run)
                if not dry_run:
                    sd.embedding = ue
                    sd.save(update_fields=["embedding"])

            processed += 1
            if sleep_s:
                time.sleep(sleep_s)
    return processed


def backfill_unified_rows(model_name: str, target_dim: int, shape: str,
                          batch_size: int, limit: Optional[int], sleep_s: float, dry_run: bool) -> int:
    qs = UnifiedEmbedding.objects.filter(Q(embedding__isnull=True) & Q(is_active=True)).order_by("id")
    processed = 0
    while True:
        if limit is not None and processed >= limit:
            break
        page = list(qs[processed: processed + batch_size])
        if not page:
            break
        for ue in page:
            if limit is not None and processed >= limit:
                break
            text = ue.content_text or ""
            if not text.strip():
                processed += 1
                continue
            if _EmbeddingService:
                vec = _EmbeddingService.generate_embedding_vector(text, model=model_name)
            else:
                vec = _embed_text_openai(text, model_name)
            vec = _prepare_vec(vec, target_dim, shape)

            if dry_run:
                print(f"[DRY] Update UnifiedEmbedding id={ue.id} -> dim={len(vec)}")
            else:
                ue.embedding = vec
                ue.embedding_model = model_name
                ue.embedding_dimension = len(vec)
                ue.updated_at = timezone.now()
                ue.save(update_fields=["embedding", "embedding_model", "embedding_dimension", "updated_at"])
            processed += 1
            if sleep_s:
                time.sleep(sleep_s)
    return processed


# --- Post-fix for bad stored vectors (all-zero / NaN) ------------------------

def fix_bad_vectors(target_dim: int, batch_size: int, limit: Optional[int], dry_run: bool) -> int:
    """
    Sweep stored vectors to fix:
      * all-zero vectors (norm == 0) -> set tiny epsilon in first dim
      * NaN or inf entries -> set to 0
    """
    qs = UnifiedEmbedding.objects.filter(is_active=True).order_by("id")
    processed = 0
    for ue in qs.iterator(chunk_size=batch_size):
        if limit is not None and processed >= limit:
            break
        vec = ue.embedding
        if not isinstance(vec, list):
            continue
        needs_fix = False
        any_nonzero = False
        for x in vec:
            try:
                f = float(x)
            except Exception:
                f = 0.0
            if math.isnan(f) or math.isinf(f):
                needs_fix = True
            if f != 0.0:
                any_nonzero = True
        if not any_nonzero:
            needs_fix = True
        if len(vec) != target_dim:
            needs_fix = True

        if needs_fix:
            fixed = _prepare_vec(list(vec), target_dim, "pad")
            if dry_run:
                print(f"[DRY] Fix vector id={ue.id} (len={len(vec)} -> {len(fixed)})")
            else:
                ue.embedding = fixed
                ue.embedding_dimension = len(fixed)
                ue.save(update_fields=["embedding", "embedding_dimension"])
            processed += 1
    return processed


# --- Smoke test --------------------------------------------------------------

def smoke_test():
    print("\n[smoke] Running pgvector similarity test (CosineDistance)...")
    # use a safe vector (not all zeros)
    q = [0.0] * 1536
    q[0] = 1e-9
    rows = list(
        UnifiedEmbedding.objects.exclude(embedding__isnull=True)
        .annotate(distance=CosineDistance(F("embedding"), q))
        .order_by("distance")[:3]
        .values("id", "content_type", "content_title", "distance")
    )
    if not rows:
        print("[smoke] No rows to test yet (that’s ok).")
    else:
        for r in rows:
            print(f"[smoke] {r['id']} | {r['content_type']} | {r['content_title'][:40]} | dist={r['distance']}")


# --- CLI ---------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="One-shot embedding backfill & fix")
    ap.add_argument("--model", default="text-embedding-3-small",
                    help="Embedding model (default: text-embedding-3-small; 1536 dims)")
    ap.add_argument("--db-dim", type=int, default=1536,
                    help="DB VectorField dimension (default: 1536)")
    ap.add_argument("--shape", choices=["pad", "truncate", "error"], default="error",
                    help="When model dim != DB dim: pad, truncate, or error (default)")
    ap.add_argument("--batch-size", type=int, default=25)
    ap.add_argument("--limit", type=int, default=None, help="Cap total processed rows per section")
    ap.add_argument("--only", choices=["agent_knowledge", "spider_data", "unified_embeddings"], default=None)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--sleep", type=float, default=0.0, help="Seconds to sleep between API calls")
    ap.add_argument("--fix-bad", action="store_true", help="After backfill, sweep & fix bad stored vectors")
    args = ap.parse_args()

    total = 0

    try:
        if args.only in (None, "agent_knowledge"):
            n = backfill_agent_knowledge(args.model, args.db_dim, args.shape, args.batch_size, args.limit, args.sleep, args.dry_run)
            print(f"[agent_knowledge] processed: {n}")
            total += n

        if args.only in (None, "spider_data"):
            n = backfill_spider_data(args.model, args.db_dim, args.shape, args.batch_size, args.limit, args.sleep, args.dry_run)
            print(f"[spider_data] processed: {n}")
            total += n

        if args.only in (None, "unified_embeddings"):
            n = backfill_unified_rows(args.model, args.db_dim, args.shape, args.batch_size, args.limit, args.sleep, args.dry_run)
            print(f"[unified_embeddings] processed (legacy shells): {n}")
            total += n

        if args.fix_bad:
            n = fix_bad_vectors(args.db_dim, args.batch_size, args.limit, args.dry_run)
            print(f"[fix_bad] vectors normalized/fixed: {n}")

        if not args.dry_run:
            smoke_test()

        print(f"\nDone. Total processed: {total}")
        return 0
    except KeyboardInterrupt:
        print("\nInterrupted.")
        return 130

if __name__ == "__main__":
    sys.exit(main())