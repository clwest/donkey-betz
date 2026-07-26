"""
Session 2979: Evidence display normalization utilities.

Shared helpers for shaping evidence rows on Theme Signals cards (and future
signal-card variants). Handles:
  - Source label mapping (raw spider slug → human-readable)
  - URL sanitization (Bluesky at:// → https://bsky.app/..., http/https allowlist)
  - Display-only text normalization ("Discussion | Link" stripping, whitespace
    collapse)
  - sample_signals → evidence[] conversion (fallback path when primary
    spider_data_ids extraction yields nothing)

Extracted from theme_signals_service.py per Rigby T1 SIGN mitigation.

Spec: deliverable c4602ccd-a973-424f-8bc5-dcc16f797430 (S2979 evidence-first
card UI). Chris ratified Option B (spider_data_ids primary; sample_signals
fallback) at S2979 — spec intent preserved (evidence works), implementation
corrected by pre-code sampling that showed sample_signals is lower integrity
than the spider_data_ids path.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse


# -- Source label map -----------------------------------------------------

# Raw spider slug → human-readable display label. Expand as new spiders land.
# Unknown slugs fall back to titlecase (via format_source_label) so
# `yahoo_finance` → `Yahoo Finance` without needing an explicit entry, which
# also collapses the observed drift where the same spider ships two label
# forms ("yahoo_finance" and "Yahoo Finance") into one canonical form.
SOURCE_DISPLAY_LABELS: Dict[str, str] = {
    "arstechnica": "Ars Technica",
    "axios": "Axios",
    "bbc": "BBC",
    "bluesky": "Bluesky",
    "business_news": "Business News",
    "devto": "DEV.to",
    "financial": "Financial",
    "finnhub": "Finnhub",
    "freecodecamp": "freeCodeCamp",
    "github": "GitHub",
    "google_news": "Google News",
    "government": "Government",
    "hackernews": "Hacker News",
    "health": "Health",
    "huggingface": "Hugging Face",
    "kaggle": "Kaggle",
    "kickstarter": "Kickstarter",
    "mit_tech_review": "MIT Tech Review",
    "newsapi": "NewsAPI",
    "npr": "NPR",
    "polygon_finance": "Polygon.io",
    "producthunt": "Product Hunt",
    "reuters_rss": "Reuters",
    "sec_edgar": "SEC EDGAR",
    "smashingmagazine": "Smashing Magazine",
    "techcrunch": "TechCrunch",
    "techcrunch_startups": "TechCrunch Startups",
    "theverge": "The Verge",
    "venturebeat": "VentureBeat",
    "wired": "WIRED",
    "yahoo_finance": "Yahoo Finance",
}


def format_source_label(raw: Optional[str]) -> str:
    """Map a raw spider slug (or already-formatted label) to a display label.

    Lookup is case-insensitive on the raw slug. Unknown slugs fall back to
    space-separated title-casing (`my_new_spider` → `My New Spider`), which
    keeps the surface stable when new spiders land without map entries.
    """
    if not raw:
        return ""
    key = str(raw).strip()
    if not key:
        return ""
    if key in SOURCE_DISPLAY_LABELS:
        return SOURCE_DISPLAY_LABELS[key]
    lower = key.lower()
    if lower in SOURCE_DISPLAY_LABELS:
        return SOURCE_DISPLAY_LABELS[lower]
    return " ".join(w.capitalize() for w in re.split(r"[_\-\s]+", lower) if w)


# -- URL sanitization -----------------------------------------------------

# Bluesky AT-protocol post URI:
#   at://did:plc:<did>/app.bsky.feed.post/<rkey>
# also seen as did:web:<domain>. Match both DID methods.
_BSKY_AT_URI_RE = re.compile(
    r"^at://(did:[a-z]+:[A-Za-z0-9._:-]+)/app\.bsky\.feed\.post/([A-Za-z0-9]+)/?$"
)

_ALLOWED_URL_SCHEMES = frozenset({"http", "https"})


def sanitize_evidence_url(url: Optional[str]) -> Optional[str]:
    """Return a browser-openable URL, or None if it can't be safely rendered.

    Transforms known non-http URIs where a clean https equivalent exists:
      - Bluesky ``at://did:*/app.bsky.feed.post/<rkey>`` →
        ``https://bsky.app/profile/<did>/post/<rkey>``

    Rejects any URL whose scheme isn't in the http/https allowlist. This
    also drops ``javascript:``, ``data:``, ``file:``, ``vbscript:``, etc.
    defensively, per Rigby T1 SIGN same-PR mitigation — no such schemes
    appear in the current corpus, but the rendering surface should refuse
    them if future spider drift ever introduces one.
    """
    if not url or not isinstance(url, str):
        return None
    raw = url.strip()
    if not raw:
        return None
    m = _BSKY_AT_URI_RE.match(raw)
    if m:
        did, rkey = m.group(1), m.group(2)
        return f"https://bsky.app/profile/{did}/post/{rkey}"
    try:
        parsed = urlparse(raw)
    except (ValueError, TypeError):
        return None
    if parsed.scheme.lower() in _ALLOWED_URL_SCHEMES and parsed.netloc:
        return raw
    return None


# -- Text normalization ---------------------------------------------------

_DISCUSSION_LINK_RE = re.compile(r"\s*discussion\s*\|\s*link\s*", re.IGNORECASE)
_WHITESPACE_COLLAPSE_RE = re.compile(r"\s+")


def normalize_evidence_text(text: Optional[str]) -> str:
    """Display-only cleanup for evidence titles/snippets.

    - Strip ``Discussion | Link`` (case-insensitive; Product Hunt feed artifact).
    - Collapse newlines/tabs/repeated whitespace into single spaces.
    - Trim leading/trailing whitespace.

    Does NOT mutate stored data (caller uses on-the-fly for display).
    Primary spider_data_ids path titles are already clean; this exists so
    the sample_signals fallback path doesn't ship junk when it activates.
    """
    if not text:
        return ""
    stripped = _DISCUSSION_LINK_RE.sub(" ", str(text))
    return _WHITESPACE_COLLAPSE_RE.sub(" ", stripped).strip()


# -- Evidence normalization + relevance sort ------------------------------

MAX_EVIDENCE_TITLE_LEN = 200


def normalize_evidence_row(
    title: Optional[str],
    url: Optional[str],
    source: Optional[str],
    published: Any = None,
) -> Optional[Dict[str, Any]]:
    """Shape a single evidence row against the card contract.

    Returns None when both the normalized title and the sanitized url end up
    empty — nothing usable to render.
    """
    clean_title = normalize_evidence_text(title)[:MAX_EVIDENCE_TITLE_LEN]
    clean_url = sanitize_evidence_url(url)
    if not clean_title and not clean_url:
        return None
    return {
        "title": clean_title or "(no title)",
        "url": clean_url,
        "source": format_source_label(source),
        "published": published,
    }


def evidence_from_sample_signals(
    sample_signals: Optional[List[Dict[str, Any]]],
    max_items: int,
) -> List[Dict[str, Any]]:
    """Convert ``SignalCluster.sample_signals`` into evidence rows.

    sample_signals stores ``{source, text, url}`` per signal (see
    ``signal_aggregation_service._create_or_update_cluster``). Used as a
    fallback when the primary ``spider_data_ids`` extraction path yields
    zero rows.
    """
    if not sample_signals or not isinstance(sample_signals, list):
        return []
    out: List[Dict[str, Any]] = []
    for entry in sample_signals:
        if not isinstance(entry, dict):
            continue
        row = normalize_evidence_row(
            title=entry.get("text"),
            url=entry.get("url"),
            source=entry.get("source"),
            published=None,
        )
        if row is None:
            continue
        out.append(row)
        if len(out) >= max_items:
            break
    return out


def sort_evidence_by_relevance(evidence: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Stable-sort evidence so top-3 defaults surface the best items.

    Sort key (ascending — lower is "better"):
      1. url_missing — clickable (0) before unclickable (1)
      2. title_placeholder — real title (0) before "(no title)" (1)

    Python's ``sorted`` is stable, so items that tie on both keys keep their
    original walk order (which is roughly relevance order from the extractor).
    Deterministic across runs.
    """
    def _key(row: Dict[str, Any]):
        url_missing = 0 if row.get("url") else 1
        title = row.get("title") or ""
        title_placeholder = 0 if (title and title != "(no title)") else 1
        return (url_missing, title_placeholder)

    return sorted(evidence, key=_key)
