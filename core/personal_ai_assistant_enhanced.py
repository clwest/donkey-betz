# core/personal_ai_assistant_enhanced.py
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

def _merge_spider_contexts(*sources: Any) -> Dict:
    """
    Merge dict-like spider context sources. Later sources override earlier ones.
    Returns a dict (empty if no valid sources).
    """
    merged: Dict = {}
    if not sources:
        return merged

    for src in sources:
        if src is None:
            continue
        try:
            if isinstance(src, dict):
                data = src
            elif hasattr(src, "items"):
                data = dict(src)
            else:
                logger.warning("Skipping non-dict spider context source: %s", type(src))
                continue

            if not isinstance(data, dict):
                logger.warning("Converted spider context is not a dict, skipping: %s", type(data))
                continue

            merged.update(data)
        except Exception:
            logger.exception("Error while merging spider context source: %s", type(src))
    return merged

# ... other module code ...

# Example replacement near line ~4970:
# old: spider_context = {}
spider_context = _merge_spider_contexts(getattr(self, "spider_data", None), getattr(self, "trending_data", None))

# ... code in between ...

# Example replacement near line ~4985:
# old: spider_context = trending_data
spider_context = _merge_spider_contexts(trending_data, getattr(self, "spider_data", None))