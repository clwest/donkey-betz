"""
Legislation Spider - Congressional Bill Tracking
=================================================

Fetches real bill data from LegiScan (state + federal) and Congress.gov
(federal plain-language summaries) so the PA can answer questions like
"What bills are being worked on about healthcare?"

Data sources:
- LegiScan API (LEGISCAN_API_KEY) — bill search, details, sponsors
- Congress.gov API (GOVERNMENT_API_KEY) — CRS plain-language summaries
"""

import logging
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)

LEGISCAN_BASE = "https://api.legiscan.com/"
CONGRESS_BASE = "https://api.congress.gov/v3/"

# Topic searches — covers the most commonly asked-about legislative areas
SEARCH_TOPICS = [
    "healthcare",
    "artificial intelligence technology",
    "immigration",
    "education",
    "environment climate",
    "economy tax",
]


class LegislationSpider:
    """Congressional bill tracker — LegiScan + Congress.gov APIs."""

    name = "legislation"

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        self.spider_id = spider_id or self.name
        self.legiscan_key = os.getenv("LEGISCAN_API_KEY", "")
        self.congress_key = os.getenv("GOVERNMENT_API_KEY", "")
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "DonkeyBetz/1.0"})

    # ------------------------------------------------------------------
    # Public interface (matches spider network contract)
    # ------------------------------------------------------------------

    def fetch_data(self, max_results: int = 30) -> List[Dict[str, Any]]:
        if not self.legiscan_key:
            logger.warning("LEGISCAN_API_KEY not set — legislation spider skipped")
            return []

        all_bills: List[Dict[str, Any]] = []
        seen_ids: set = set()

        # 1. Search across topics
        for topic in SEARCH_TOPICS:
            try:
                results = self._legiscan_search(topic)
                for bill in results[:5]:
                    bid = bill.get("bill_id")
                    if bid and bid not in seen_ids:
                        seen_ids.add(bid)
                        all_bills.append(bill)
            except Exception as e:
                logger.warning(f"LegiScan search failed for '{topic}': {e}")

        # 2. Fetch full details for the 10 most recently active bills
        sorted_bills = sorted(
            all_bills,
            key=lambda b: b.get("last_action_date", ""),
            reverse=True,
        )
        for bill in sorted_bills[:10]:
            try:
                details = self._legiscan_bill_detail(bill["bill_id"])
                if details:
                    bill.update(details)
            except Exception as e:
                logger.warning(f"LegiScan detail failed for {bill.get('bill_number')}: {e}")

        # 3. Enrich federal bills with Congress.gov plain-language summaries
        if self.congress_key:
            for bill in all_bills:
                if bill.get("state", "").upper() == "US":
                    try:
                        summary = self._congress_summary(bill.get("bill_number", ""))
                        if summary:
                            bill["plain_summary"] = summary
                    except Exception as e:
                        logger.debug(f"Congress.gov summary failed: {e}")

        # 4. Normalize into spider-network format
        items = [self._normalize(b) for b in all_bills]
        logger.info(f"Legislation spider collected {len(items)} bills")
        return items[:max_results]

    # ------------------------------------------------------------------
    # LegiScan helpers
    # ------------------------------------------------------------------

    def _legiscan_get(self, op: str, **params) -> Optional[Dict]:
        params.update({"key": self.legiscan_key, "op": op})
        resp = self.session.get(LEGISCAN_BASE, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") == "OK":
            return data
        logger.debug(f"LegiScan {op} non-OK: {data.get('alert', {}).get('message', '')}")
        return None

    def _legiscan_search(self, query: str) -> List[Dict]:
        data = self._legiscan_get("getSearch", state="ALL", query=query)
        if not data:
            return []
        search_result = data.get("searchresult", {})
        bills = []
        for key, val in search_result.items():
            if key == "summary" or not isinstance(val, dict):
                continue
            bills.append({
                "bill_id": val.get("bill_id"),
                "bill_number": val.get("bill_number", ""),
                "title": val.get("title", ""),
                "state": val.get("state", ""),
                "status": self._status_label(val.get("status", 0)),
                "last_action": val.get("last_action", ""),
                "last_action_date": val.get("last_action_date", ""),
                "url": val.get("url", ""),
                "relevance": val.get("relevance", 0),
                "source": "legiscan",
            })
        return bills

    def _legiscan_bill_detail(self, bill_id: int) -> Optional[Dict]:
        data = self._legiscan_get("getBill", id=bill_id)
        if not data:
            return None
        bill = data.get("bill", {})
        sponsors = []
        for sp in bill.get("sponsors", []):
            sponsors.append({
                "name": sp.get("name", ""),
                "party": sp.get("party", ""),
                "role": sp.get("role", ""),
            })
        committee_name = ""
        for c in bill.get("committee", []) if isinstance(bill.get("committee"), list) else []:
            committee_name = c.get("name", "")
            break
        if isinstance(bill.get("committee"), dict):
            committee_name = bill["committee"].get("name", "")
        subjects = [s.get("subject_name", "") for s in bill.get("subjects", [])]
        history = bill.get("history", [])
        last_history = history[-1] if history else {}
        return {
            "description": bill.get("description", ""),
            "sponsors": sponsors,
            "sponsor_count": len(sponsors),
            "committee": committee_name,
            "topics": subjects,
            "status": self._status_label(bill.get("status", 0)),
            "status_date": bill.get("status_date", ""),
            "last_action": last_history.get("action", bill.get("last_action", "")),
            "last_action_date": last_history.get("date", bill.get("last_action_date", "")),
            "url": bill.get("url", ""),
            "state_link": bill.get("state_link", ""),
        }

    @staticmethod
    def _status_label(code) -> str:
        status_map = {
            0: "N/A", 1: "Introduced", 2: "Engrossed", 3: "Enrolled",
            4: "Passed", 5: "Vetoed", 6: "Failed",
        }
        try:
            return status_map.get(int(code), f"Status {code}")
        except (ValueError, TypeError):
            return str(code)

    # ------------------------------------------------------------------
    # Congress.gov helper
    # ------------------------------------------------------------------

    def _congress_summary(self, bill_number: str) -> Optional[str]:
        if not self.congress_key or not bill_number:
            return None
        # Parse bill type and number: e.g. "HR 1234" -> bill_type=hr, number=1234
        m = re.match(r"(HR|S|HJR|SJR|HRES|SRES|HJRES|SJRES)\s*(\d+)", bill_number.upper())
        if not m:
            return None
        bill_type = m.group(1).lower()
        number = m.group(2)
        # Congress.gov v3 summaries endpoint
        url = f"{CONGRESS_BASE}bill/118/{bill_type}/{number}/summaries"
        resp = self.session.get(
            url,
            params={"api_key": self.congress_key, "format": "json"},
            timeout=30,
        )
        if resp.status_code != 200:
            return None
        summaries = resp.json().get("summaries", [])
        if not summaries:
            return None
        # Prefer the most recent CRS summary
        best = summaries[-1]
        text = best.get("text", "")
        # Strip HTML tags
        text = re.sub(r"<[^>]+>", "", text).strip()
        return text[:1000] if text else None

    # ------------------------------------------------------------------
    # Normalize to spider-network format
    # ------------------------------------------------------------------

    def _normalize(self, bill: Dict) -> Dict[str, Any]:
        topics_str = ", ".join(bill.get("topics", []))
        sponsor_names = ", ".join(
            s.get("name", "") for s in bill.get("sponsors", [])
        )
        embedding_parts = [
            bill.get("bill_number", ""),
            bill.get("title", ""),
            f"{bill.get('state', '')} legislation",
            f"Status: {bill.get('status', '')}",
        ]
        if topics_str:
            embedding_parts.append(f"Topics: {topics_str}")
        if sponsor_names:
            embedding_parts.append(f"Sponsors: {sponsor_names}")
        desc = bill.get("description", "")
        if desc:
            embedding_parts.append(desc[:300])
        embedding_text = ". ".join(p for p in embedding_parts if p)

        return {
            "spider_name": "legislation",
            "source_url": bill.get("url", ""),
            "data_type": "bill_summary",
            "raw_data": {
                "bill_id": bill.get("bill_id"),
                "bill_number": bill.get("bill_number", ""),
                "title": bill.get("title", ""),
                "description": bill.get("description", ""),
                "plain_summary": bill.get("plain_summary", ""),
                "state": bill.get("state", ""),
                "status": bill.get("status", ""),
                "status_date": bill.get("status_date", ""),
                "last_action": bill.get("last_action", ""),
                "last_action_date": bill.get("last_action_date", ""),
                "sponsors": bill.get("sponsors", []),
                "sponsor_count": bill.get("sponsor_count", 0),
                "committee": bill.get("committee", ""),
                "topics": bill.get("topics", []),
                "url": bill.get("url", ""),
                "congress_gov_url": bill.get("state_link", ""),
            },
            "processed_data": {
                "bill_number": bill.get("bill_number", ""),
                "title": bill.get("title", ""),
                "state": bill.get("state", ""),
                "status": bill.get("status", ""),
                "plain_summary": bill.get("plain_summary", ""),
                "sponsor_count": bill.get("sponsor_count", 0),
                "topics": bill.get("topics", []),
            },
            "embedding_text": embedding_text,
            "platform": "legislation",
            "tags": ["legislation", "congress", bill.get("state", "").lower()],
            "timestamp": datetime.now().isoformat(),
        }
