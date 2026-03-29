"""
Newsletter Source Pack — curated sources for Autopilot Ops.

POC 1: Hardcoded source list organized by newsletter section.
Later: expand to DB-backed config, wire to spiders.

Usage:
    from core.services.newsletter_sources import get_sources, refresh_sources

    sources = get_sources()  # All sources
    sources = get_sources(category='incidents')  # Filtered
    summaries = refresh_sources(category='incidents', limit=10)  # Fetch fresh
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


# ── Source Pack v1 ──────────────────────────────────────────────────────────
# Organized by newsletter section / category.
# Each source has: name, url, category, feed_type, description
# feed_type: rss, api, scrape, manual

SOURCE_PACK = [
    # ── What Broke (incidents, outages, postmortems) ────────────────────
    {
        'name': 'Hacker News (outages)',
        'url': 'https://hn.algolia.com/api/v1/search_by_date?query=outage+incident&tags=story',
        'category': 'incidents',
        'feed_type': 'api',
        'description': 'HN stories about outages and incidents',
        'section': 'what_broke',
    },
    {
        'name': 'StatusGator',
        'url': 'https://statusgator.com/',
        'category': 'incidents',
        'feed_type': 'manual',
        'description': 'Cloud service status aggregator',
        'section': 'what_broke',
    },
    {
        'name': 'Downdetector',
        'url': 'https://downdetector.com/',
        'category': 'incidents',
        'feed_type': 'manual',
        'description': 'Real-time outage monitoring',
        'section': 'what_broke',
    },
    {
        'name': 'AWS Service Health',
        'url': 'https://health.aws.amazon.com/health/status',
        'category': 'incidents',
        'feed_type': 'manual',
        'description': 'AWS service status dashboard',
        'section': 'what_broke',
    },
    {
        'name': 'Google Cloud Status',
        'url': 'https://status.cloud.google.com/',
        'category': 'incidents',
        'feed_type': 'manual',
        'description': 'GCP service status dashboard',
        'section': 'what_broke',
    },
    {
        'name': 'Azure Status',
        'url': 'https://status.azure.com/',
        'category': 'incidents',
        'feed_type': 'manual',
        'description': 'Azure service status dashboard',
        'section': 'what_broke',
    },
    {
        'name': 'SRE Weekly',
        'url': 'https://sreweekly.com/',
        'category': 'incidents',
        'feed_type': 'rss',
        'description': 'Weekly SRE newsletter with incident analysis',
        'section': 'what_broke',
    },
    {
        'name': 'Postmortems.info',
        'url': 'https://postmortems.info/',
        'category': 'incidents',
        'feed_type': 'manual',
        'description': 'Collection of public postmortems',
        'section': 'what_broke',
    },

    # ── What Changed (vendor updates, releases, CVEs) ───────────────────
    {
        'name': 'Kubernetes Blog',
        'url': 'https://kubernetes.io/blog/',
        'category': 'vendor_changes',
        'feed_type': 'rss',
        'description': 'Kubernetes release announcements',
        'section': 'what_changed',
    },
    {
        'name': 'HashiCorp Blog',
        'url': 'https://www.hashicorp.com/blog',
        'category': 'vendor_changes',
        'feed_type': 'rss',
        'description': 'Terraform, Vault, Consul updates',
        'section': 'what_changed',
    },
    {
        'name': 'AWS What\'s New',
        'url': 'https://aws.amazon.com/new/',
        'category': 'vendor_changes',
        'feed_type': 'rss',
        'description': 'AWS service launches and updates',
        'section': 'what_changed',
    },
    {
        'name': 'GCP Release Notes',
        'url': 'https://cloud.google.com/release-notes',
        'category': 'vendor_changes',
        'feed_type': 'rss',
        'description': 'Google Cloud platform updates',
        'section': 'what_changed',
    },
    {
        'name': 'Datadog Blog',
        'url': 'https://www.datadoghq.com/blog/',
        'category': 'vendor_changes',
        'feed_type': 'rss',
        'description': 'Datadog product updates and observability content',
        'section': 'what_changed',
    },
    {
        'name': 'Grafana Blog',
        'url': 'https://grafana.com/blog/',
        'category': 'vendor_changes',
        'feed_type': 'rss',
        'description': 'Grafana, Loki, Tempo, Mimir updates',
        'section': 'what_changed',
    },

    # ── CVEs / Security ─────────────────────────────────────────────────
    {
        'name': 'NIST NVD',
        'url': 'https://nvd.nist.gov/vuln/search',
        'category': 'cves',
        'feed_type': 'api',
        'description': 'National Vulnerability Database',
        'section': 'what_changed',
    },
    {
        'name': 'CISA Known Exploited',
        'url': 'https://www.cisa.gov/known-exploited-vulnerabilities-catalog',
        'category': 'cves',
        'feed_type': 'api',
        'description': 'CISA KEV catalog — actively exploited vulns',
        'section': 'what_changed',
    },
    {
        'name': 'SecurityWeek',
        'url': 'https://www.securityweek.com/',
        'category': 'cves',
        'feed_type': 'rss',
        'description': 'Security news and vulnerability coverage',
        'section': 'what_changed',
    },

    # ── Cost Watch (FinOps, pricing, capacity) ──────────────────────────
    {
        'name': 'The FinOps Foundation Blog',
        'url': 'https://www.finops.org/blog/',
        'category': 'finops',
        'feed_type': 'rss',
        'description': 'FinOps practices, benchmarks, cost patterns',
        'section': 'cost_watch',
    },
    {
        'name': 'Vantage Cloud Cost Reports',
        'url': 'https://www.vantage.sh/blog',
        'category': 'finops',
        'feed_type': 'rss',
        'description': 'Cloud cost analysis and pricing changes',
        'section': 'cost_watch',
    },
    {
        'name': 'InfoQ DevOps',
        'url': 'https://www.infoq.com/devops/',
        'category': 'finops',
        'feed_type': 'rss',
        'description': 'DevOps and infrastructure cost discussions',
        'section': 'cost_watch',
    },

    # ── Autopilot Move (automation patterns, runbooks) ──────────────────
    {
        'name': 'Hacker News (SRE/automation)',
        'url': 'https://hn.algolia.com/api/v1/search_by_date?query=SRE+automation+runbook&tags=story',
        'category': 'automation',
        'feed_type': 'api',
        'description': 'HN stories about SRE automation and runbooks',
        'section': 'autopilot_move',
    },
    {
        'name': 'Google SRE Books',
        'url': 'https://sre.google/books/',
        'category': 'automation',
        'feed_type': 'manual',
        'description': 'Reference patterns from Google SRE',
        'section': 'autopilot_move',
    },
    {
        'name': 'PagerDuty Incident Response',
        'url': 'https://response.pagerduty.com/',
        'category': 'automation',
        'feed_type': 'manual',
        'description': 'PagerDuty incident response best practices',
        'section': 'autopilot_move',
    },

    # ── Tool / Repo of the Week ─────────────────────────────────────────
    {
        'name': 'GitHub Trending (DevOps)',
        'url': 'https://github.com/trending?since=weekly',
        'category': 'tools',
        'feed_type': 'api',
        'description': 'Trending repos on GitHub',
        'section': 'tool_of_week',
    },
    {
        'name': 'CNCF Landscape',
        'url': 'https://landscape.cncf.io/',
        'category': 'tools',
        'feed_type': 'manual',
        'description': 'Cloud native tools landscape',
        'section': 'tool_of_week',
    },
    {
        'name': 'Product Hunt (Developer Tools)',
        'url': 'https://www.producthunt.com/topics/developer-tools',
        'category': 'tools',
        'feed_type': 'api',
        'description': 'New developer tools and launches',
        'section': 'tool_of_week',
    },

    # ── Top Signal (general SRE/ops thought leadership) ─────────────────
    {
        'name': 'The New Stack',
        'url': 'https://thenewstack.io/',
        'category': 'thought_leadership',
        'feed_type': 'rss',
        'description': 'DevOps, cloud native, platform engineering',
        'section': 'top_signal',
    },
    {
        'name': 'DevOps.com',
        'url': 'https://devops.com/',
        'category': 'thought_leadership',
        'feed_type': 'rss',
        'description': 'DevOps news and analysis',
        'section': 'top_signal',
    },
    {
        'name': 'Last Week in AWS',
        'url': 'https://www.lastweekinaws.com/',
        'category': 'thought_leadership',
        'feed_type': 'rss',
        'description': 'Corey Quinn\'s AWS commentary',
        'section': 'top_signal',
    },
]


def get_sources(
    category: Optional[str] = None,
    section: Optional[str] = None,
    feed_type: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Get sources from the source pack, optionally filtered.

    Args:
        category: Filter by category (incidents, vendor_changes, cves, finops, etc.)
        section: Filter by newsletter section (what_broke, what_changed, etc.)
        feed_type: Filter by feed type (rss, api, scrape, manual)
    """
    result = SOURCE_PACK
    if category:
        result = [s for s in result if s['category'] == category]
    if section:
        result = [s for s in result if s['section'] == section]
    if feed_type:
        result = [s for s in result if s['feed_type'] == feed_type]
    return result


def get_source_summary() -> Dict[str, Any]:
    """Get a summary of the source pack."""
    categories = {}
    sections = {}
    feed_types = {}
    for s in SOURCE_PACK:
        categories[s['category']] = categories.get(s['category'], 0) + 1
        sections[s['section']] = sections.get(s['section'], 0) + 1
        feed_types[s['feed_type']] = feed_types.get(s['feed_type'], 0) + 1
    return {
        'total_sources': len(SOURCE_PACK),
        'by_category': categories,
        'by_section': sections,
        'by_feed_type': feed_types,
    }


def refresh_sources(category: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
    """Fetch fresh content from sources (API and RSS only).

    Currently returns source metadata. Future: actually fetch RSS/API data
    and return summaries for issue content generation.
    """
    sources = get_sources(category=category)
    fetchable = [s for s in sources if s['feed_type'] in ('rss', 'api')]

    # Future: implement actual RSS/API fetching here
    # For now, return the source list with a note
    results = []
    for s in fetchable[:limit]:
        results.append({
            'name': s['name'],
            'url': s['url'],
            'category': s['category'],
            'section': s['section'],
            'status': 'available',
            'note': 'Fetch not yet implemented — use URL manually',
        })

    return results
