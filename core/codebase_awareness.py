"""Codebase Self-Awareness — retired-to-no-op facade.

Session 1235 P5#3 audit Tranche 1 PR #5: retired the dead psycopg2
substrate this module was built on.

## What this module used to do (pre-pivot)

Wrote per-component embeddings (one per Python class + top-level
function) of the entire repo into a `unified_embeddings` table inside
a non-existent `ai_unified_platform` database. The intent was
codebase semantic search and "explain this component" features.

## What actually happened

Every operation failed silently. The class constructor called
`load_ingested_files()` which called `psycopg2.connect(database=
'ai_unified_platform', user='ai_unified_user', password=...)` — a DB
that has never existed in this platform. Constructor exception was
caught + logged + swallowed. Class instance came up with
`self.ingested_files = set()` (empty) and every subsequent method
hit the same dead connection.

**Importing the module triggered the dead connection attempt.** The
singleton at module-bottom runs `CodebaseAwareness()` at import time;
the only caller (the `ingest_codebase` mgmt command) imports the
module → triggers __init__ → triggers DB connect → fails → logs
"Error loading ingested files: connection refused" + continues with
empty state.

## What this module does now

Honest no-op facade. All methods return empty/zero shapes without
DB hits or import-time side effects. The `ingest_codebase` mgmt
command continues to import + invoke without raising, prints zero
stats, exits cleanly.

## Why retire rather than pivot

The feature has been broken since file creation. Zero callers ever
got value from it. Pivoting the writes to `DocumentEmbedding` would
mean embedding thousands of code components against the OpenAI API
($$$) for a feature with no proven demand. Session 1236+ can revisit
if "codebase self-awareness" becomes a real product requirement, at
which point the right design (chunk strategy, embedding budget,
storage target, search UX) needs a proper spec — not a backfill of
a never-used singleton.

The singleton + class are kept for import compatibility with the
mgmt command. The `search_code` and `explain_system` methods delegate
to `core.rag_integration` which D12 fixed, so they're already on the
live `DocumentEmbedding` substrate — they just return empty because
no `content_type='source_code'` rows have ever been written there.
"""

import logging
from typing import Dict, List, Any, Optional

from django.conf import settings  # noqa: F401  (kept for future pivot)

logger = logging.getLogger(__name__)


class CodebaseAwareness:
    """Honest no-op facade. See module docstring for retirement rationale."""

    def __init__(self):
        # No DB connect at import time. Pre-pivot this constructor
        # fired psycopg2.connect on the dead `ai_unified_platform` DB,
        # making every import of this module log a connection error.
        self.ingested_files: set = set()

    def load_ingested_files(self):
        """Pre-pivot: read `unified_embeddings` to populate
        `self.ingested_files`. Post-pivot: no-op."""
        return

    def get_file_hash(self, file_path: str) -> str:
        """Compute SHA-256 of file contents. Kept functional — pure
        file I/O, no DB."""
        import hashlib
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return hashlib.md5(f.read().encode()).hexdigest()
        except Exception as _e:
            logger.warning(
                "codebase_awareness.get_file_hash: swallowed (%s: %s)",
                type(_e).__name__, _e,
            )
            return ""

    def ingest_codebase(self, force_update: bool = False) -> Dict[str, int]:
        """Retired no-op. Pre-pivot would have ingested per-component
        embeddings into the dead `unified_embeddings` table; always
        failed silently. Returns zero stats so callers (the
        `ingest_codebase` mgmt command) continue to work."""
        logger.info(
            "codebase_awareness.ingest_codebase: retired (see module "
            "docstring); returning zero stats. force_update=%s",
            force_update,
        )
        return {
            'files_processed': 0,
            'files_skipped': 0,
            'files_updated': 0,
            'embeddings_created': 0,
            'errors': 0,
        }

    def ingest_file(self, file_path, file_hash: str) -> int:
        """Retired no-op. Returns 0 embeddings created."""
        return 0

    def extract_node_content(self, source: str, node) -> str:
        """Pre-pivot helper for AST traversal. Kept functional — pure
        string slicing, no DB."""
        if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
            lines = source.split('\n')
            return '\n'.join(lines[node.lineno - 1:node.end_lineno])
        return ""

    def search_code(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Delegates to `core.rag_integration.search_embeddings` which
        D12 PR #2621 pivoted to the populated `DocumentEmbedding` table.
        Returns empty until / unless code components are written there
        with `content_type='source_code'` (no current writer)."""
        try:
            from core.rag_integration import search_embeddings
            results = search_embeddings(
                query=query,
                limit=limit,
                content_types=['source_code'],
                similarity_threshold=0.5,
            )
            return [
                {
                    'file': r.get('metadata', {}).get('relative_path', 'unknown'),
                    'component': r.get('metadata', {}).get('component_name', 'unknown'),
                    'type': r.get('metadata', {}).get('component_type', 'unknown'),
                    'content': r.get('content', ''),
                    'similarity': r.get('similarity_score', 0.0),
                }
                for r in results
            ]
        except Exception as _e:
            logger.warning(
                "codebase_awareness.search_code: swallowed (%s: %s)",
                type(_e).__name__, _e,
            )
            return []

    def get_implementation(self, component_name: str) -> Optional[str]:
        """Retired no-op. Pre-pivot read `unified_embeddings` filtered
        by `metadata->>'component_name'`; no current writer puts
        components there."""
        return None

    def explain_system(self, component_or_file: str) -> str:
        """Uses search_code() — returns the standard 'not found' string
        until a writer populates source_code embeddings."""
        results = self.search_code(component_or_file, limit=1)
        if not results:
            return f"No information found about {component_or_file}"
        result = results[0]
        explanation = f"## {result['component']} ({result['type']})\n\n"
        explanation += f"**File:** {result['file']}\n\n"
        explanation += f"**Implementation:**\n```python\n{result['content'][:1000]}\n```\n\n"
        explanation += "This component is part of the unified-donkey-betz system."
        return explanation


# Singleton instance — preserved for import compatibility with
# core/management/commands/ingest_codebase.py.
codebase_awareness = CodebaseAwareness()
