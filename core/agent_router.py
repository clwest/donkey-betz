# core/agent_router.py
import logging
from typing import Any, Dict

def _safe_merge_spider_contexts(*sources: Any) -> Dict:
    """
    Merge multiple spider context sources in order. Later sources override earlier ones.
    Only dict-like sources are accepted. Returns an empty dict on failure or if no valid sources.
    """
    logger = logging.getLogger(__name__)
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
                logger.warning("Skipping spider source with unsupported type: %s", type(src))
                continue

            if not isinstance(data, dict):
                logger.warning("Converted spider source is not a dict, skipping: %s", type(data))
                continue

            merged.update(data)
        except Exception:
            logger.exception("Exception while merging spider source: %s", type(src))

    return merged


class AgentRouter:
    # ... existing class code ...

    def spider_context_builder(self) -> dict:
        """
        Safely build a spider context by merging available sources.
        Preference: later sources override earlier ones.
        Sources considered (in order): spider_data, trending_data, external_spiders, spider_context_raw
        Always returns a dict.
        """
        logger = logging.getLogger(__name__)
        try:
            sources = (
                getattr(self, "spider_data", None),
                getattr(self, "trending_data", None),
                getattr(self, "external_spiders", None),
                getattr(self, "spider_context_raw", None),
            )
            context = _safe_merge_spider_contexts(*sources)
            if not isinstance(context, dict):
                logger.warning("Merged spider context is not a dict, returning empty dict")
                return {}
            return context
        except Exception:
            logger.exception("Failed to build spider context, returning empty dict")
            return {}