"""
Himalayas.app Intelligence Spider - Remote Jobs API
====================================================

Session 390: New freelance-friendly job source using Himalayas.app free API.
Provides JSON job listings with excellent data quality.

API Documentation: https://himalayas.app/api
- Free to use with attribution (link back to himalayas.app)
- Returns up to 20 jobs per request
- Sorted by most recent
"""

import logging
import httpx
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class HimalayasSpider:
    """
    Spider for fetching jobs from Himalayas.app free API.

    This spider fetches remote jobs and can filter for freelance/contract work.
    Requires attribution: must link back to himalayas.app URLs.
    """

    name = "himalayas"
    category = "freelance"

    API_URL = "https://himalayas.app/jobs/api"

    def __init__(self):
        self.client = None

    def _get_client(self):
        """Lazy-load HTTP client"""
        if self.client is None:
            self.client = httpx.Client(timeout=30.0)
        return self.client

    def crawl(self, limit: int = 20) -> Dict[str, Any]:
        """
        Fetch jobs from Himalayas API.

        Args:
            limit: Max number of jobs to fetch (max 20 per API limits)

        Returns:
            Dict with items list and metadata
        """
        try:
            client = self._get_client()

            # Himalayas API only allows max 20 per request
            actual_limit = min(limit, 20)

            response = client.get(
                self.API_URL,
                params={"limit": actual_limit}
            )
            response.raise_for_status()

            data = response.json()
            jobs = data.get("jobs", [])

            items = []
            for job in jobs:
                # Extract job details
                item = {
                    "id": job.get("id", ""),
                    "title": job.get("title", "Untitled"),
                    "company": job.get("companyName", ""),
                    "company_logo": job.get("companyLogo", ""),
                    "url": job.get("applicationLink") or f"https://himalayas.app/jobs/{job.get('id', '')}",
                    "description": job.get("description", "")[:500] if job.get("description") else "",
                    "salary": self._format_salary(job),
                    "location": job.get("locationRestrictions") or "Worldwide",
                    "source": "Himalayas",
                    "posted_at": job.get("pubDate", ""),
                    "categories": job.get("categories", []),
                    "seniority": job.get("seniority", []),
                    "tags": job.get("categories", []) + job.get("seniority", []),
                    # Keep himalayas URL for attribution requirement
                    "attribution_url": f"https://himalayas.app/jobs/{job.get('id', '')}",
                }
                items.append(item)

            logger.info(f"HimalayasSpider fetched {len(items)} jobs")

            return {
                "success": True,
                "source": "himalayas",
                "items": items,
                "count": len(items),
                "fetched_at": datetime.now(timezone.utc).isoformat()
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"Himalayas API HTTP error: {e}")
            return {"success": False, "error": str(e), "items": []}
        except Exception as e:
            logger.error(f"Himalayas spider error: {e}")
            return {"success": False, "error": str(e), "items": []}

    def _format_salary(self, job: Dict) -> str:
        """Format salary from job data"""
        min_salary = job.get("minSalary")
        max_salary = job.get("maxSalary")

        if min_salary and max_salary:
            return f"${min_salary:,} - ${max_salary:,}"
        elif min_salary:
            return f"${min_salary:,}+"
        elif max_salary:
            return f"Up to ${max_salary:,}"
        return ""

    def get_freelance_jobs(self, limit: int = 20) -> List[Dict]:
        """
        Get jobs that are likely freelance/contract opportunities.

        Filters by keywords in title or categories.
        """
        result = self.crawl(limit)

        if not result.get("success"):
            return []

        freelance_keywords = [
            "freelance", "contract", "contractor", "consultant",
            "part-time", "temporary", "project-based", "gig"
        ]

        freelance_jobs = []
        for job in result.get("items", []):
            title_lower = job.get("title", "").lower()
            categories_lower = [c.lower() for c in job.get("categories", [])]

            # Check if freelance-related
            is_freelance = any(
                kw in title_lower or any(kw in cat for cat in categories_lower)
                for kw in freelance_keywords
            )

            if is_freelance:
                job["category"] = "Freelance"
                freelance_jobs.append(job)

        return freelance_jobs

    def close(self):
        """Close HTTP client"""
        if self.client:
            self.client.close()
            self.client = None


def fetch_himalayas_jobs(limit: int = 20) -> Dict[str, Any]:
    """
    Convenience function to fetch Himalayas jobs.

    Usage:
        from ai_core.spiders.specialized.himalayas_spider import fetch_himalayas_jobs
        jobs = fetch_himalayas_jobs(limit=10)
    """
    spider = HimalayasSpider()
    try:
        return spider.crawl(limit)
    finally:
        spider.close()


def fetch_himalayas_freelance_jobs(limit: int = 20) -> List[Dict]:
    """
    Convenience function to fetch freelance-filtered jobs.

    Usage:
        from ai_core.spiders.specialized.himalayas_spider import fetch_himalayas_freelance_jobs
        jobs = fetch_himalayas_freelance_jobs(limit=10)
    """
    spider = HimalayasSpider()
    try:
        return spider.get_freelance_jobs(limit)
    finally:
        spider.close()
