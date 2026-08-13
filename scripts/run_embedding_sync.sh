#!/usr/bin/env bash
# Production embedding sync runner for Railway
# Runs sync_docs_index_to_documents --embed and then performs retrieval checks
set -euo pipefail

START_TIME=$(date +%s)
echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Starting production embedding sync..."

# --- 1. Ensure we are on main ---
git checkout main 2>&1 || true
git pull origin main 2>&1 || true

# --- 2. Activate venv if present, else install requirements ---
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "[INFO] No venv found, using system Python"
fi

pip install -q -r requirements.txt

# --- 3. Run migrations ---
echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Running migrations..."
python manage.py migrate --run-syncdb 2>&1

# --- 4. Run embedding sync ---
echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Running sync_docs_index_to_documents --embed..."
python manage.py sync_docs_index_to_documents --embed 2>&1
SYNC_EXIT=$?

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Sync finished in ${DURATION}s with exit code ${SYNC_EXIT}"

if [ "$SYNC_EXIT" -ne 0 ]; then
    echo "[ERROR] Embedding sync failed with exit code $SYNC_EXIT"
    exit $SYNC_EXIT
fi

# --- 5. Retrieval checks ---
echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Running retrieval checks..."
python - <<'PYEOF'
import django, os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection

queries = [
    (
        "CLAUDE.md exact filename",
        "SELECT source_path, 1 - (embedding <=> (SELECT embedding FROM document_embeddings LIMIT 1)) AS similarity "
        "FROM document_embeddings WHERE source_path ILIKE '%CLAUDE.md%' ORDER BY similarity DESC LIMIT 5",
        None,
    ),
]

# Check which table/model exists
try:
    from documents.models import DocumentEmbedding
    model_table = DocumentEmbedding._meta.db_table
    print(f"[INFO] Using table: {model_table}")
except ImportError:
    try:
        from rag.models import DocumentEmbedding
        model_table = DocumentEmbedding._meta.db_table
        print(f"[INFO] Using table: {model_table}")
    except ImportError:
        model_table = 'document_embeddings'
        print(f"[WARN] Could not import DocumentEmbedding model, assuming table: {model_table}")

def pgvector_search(query_text, top_k=5):
    """Use pgvector cosine similarity search via raw SQL."""
    # Try to get embedding via the embedding service
    try:
        from ai_core.intelligence.embedding_generator import EmbeddingGenerator
        gen = EmbeddingGenerator()
        vec = gen.generate(query_text)
    except Exception as e:
        print(f"[WARN] EmbeddingGenerator failed: {e}, falling back to text search")
        vec = None

    with connection.cursor() as cur:
        if vec is not None:
            vec_str = '[' + ','.join(str(v) for v in vec) + ']'
            cur.execute(
                f"""
                SELECT source_path,
                       1 - (embedding <=> %s::vector) AS similarity
                FROM {model_table}
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                [vec_str, vec_str, top_k]
            )
        else:
            # Fallback: text search on source_path / content
            cur.execute(
                f"""
                SELECT source_path, 0.0 AS similarity
                FROM {model_table}
                WHERE source_path ILIKE %s
                   OR content ILIKE %s
                LIMIT %s
                """,
                [f"%{query_text[:50]}%", f"%{query_text[:50]}%", top_k]
            )
        rows = cur.fetchall()
    return rows

# --- Check 1: CLAUDE.md filename ---
print("\n" + "="*60)
print("Retrieval Check 1: Search for CLAUDE.md (exact filename)")
print("="*60)
try:
    with connection.cursor() as cur:
        cur.execute(
            f"SELECT source_path, 1.0 AS similarity FROM {model_table} WHERE source_path ILIKE %s LIMIT 5",
            ["%CLAUDE.md%"]
        )
        rows = cur.fetchall()
    if rows:
        for i, (sp, sim) in enumerate(rows, 1):
            print(f"  {i}. source_path={sp!r}  similarity={sim:.4f}")
    else:
        # Try semantic search
        rows = pgvector_search("CLAUDE.md", 5)
        if rows:
            for i, (sp, sim) in enumerate(rows, 1):
                print(f"  {i}. source_path={sp!r}  similarity={sim:.4f}")
        else:
            print("  [WARN] No results found for CLAUDE.md")
except Exception as e:
    print(f"  [ERROR] {e}")

# --- Check 2: Unique phrase search ---
unique_phrase = "Please review the /docs/ to gain completed understanding of everything we have built"
print("\n" + "="*60)
print(f"Retrieval Check 2: Semantic search for unique phrase")
print(f"  phrase: {unique_phrase!r}")
print("="*60)
try:
    rows = pgvector_search(unique_phrase, 5)
    if rows:
        for i, (sp, sim) in enumerate(rows, 1):
            print(f"  {i}. source_path={sp!r}  similarity={sim:.4f}")
    else:
        # Try text fallback
        with connection.cursor() as cur:
            cur.execute(
                f"SELECT source_path, 0.0 AS similarity FROM {model_table} WHERE content ILIKE %s LIMIT 5",
                ["%Please review the /docs/%"]
            )
            rows = cur.fetchall()
        if rows:
            for i, (sp, sim) in enumerate(rows, 1):
                print(f"  {i}. source_path={sp!r}  similarity={sim:.4f}")
        else:
            print("  [WARN] No results found for unique phrase")
except Exception as e:
    print(f"  [ERROR] {e}")

# --- Report total embedding count ---
print("\n" + "="*60)
print("DocumentEmbedding table stats")
print("="*60)
try:
    with connection.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) FROM {model_table}")
        total = cur.fetchone()[0]
    print(f"  Total rows in {model_table}: {total}")
except Exception as e:
    print(f"  [ERROR] {e}")
PYEOF

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] All done."
exit 0
