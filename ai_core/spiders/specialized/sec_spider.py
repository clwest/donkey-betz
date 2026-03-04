"""
SEC EDGAR Spider - Company Filings Intelligence
================================================

Session 534: Simplified to work with spider network interface.
Uses SEC EDGAR RSS feeds (free, no API key required) for company filings.
"""

from ai_core.spiders.web_request_layer import cached_get
import logging
import re
import html
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class SECSpider:
    """SEC EDGAR spider - company filings via free RSS feeds"""

    name = "sec"

    # SEC EDGAR RSS feed base URL
    BASE_URL = "https://www.sec.gov/cgi-bin/browse-edgar"

    # Required User-Agent for SEC (they block requests without proper identification)
    USER_AGENT = "DonkeyBetz/1.0 (AI Content Studio Research Tool; admin@donkeybetz.com)"

    # Filing types and their market significance
    FILING_TYPES = {
        '8-K': 'Material Events',      # Most market-moving (earnings, M&A, leadership changes)
        '10-K': 'Annual Report',       # Comprehensive financial info
        '10-Q': 'Quarterly Report',    # Quarterly financials
        '4': 'Insider Trading',        # Insider buys/sells
        'S-1': 'IPO Registration',     # New public offerings
        '13F-HR': 'Institutional Holdings',  # What big funds are buying
    }

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch SEC filings using free EDGAR RSS feeds.

        Args:
            max_results: Maximum number of filings to fetch

        Returns:
            List of SEC filing dictionaries
        """
        all_filings = []
        seen_ids = set()

        # Fetch 8-K filings (most market-moving) and 10-K/10-Q for comprehensive coverage
        for form_type in ['8-K', '10-K', '10-Q']:
            try:
                url = f"{self.BASE_URL}?action=getcurrent&type={form_type}&company=&dateb=&owner=include&count=20&output=atom"

                response = cached_get(
                    url,
                    headers={
                        'User-Agent': self.USER_AGENT,
                        'Accept': 'application/atom+xml',
                    },
                    timeout=15
                )

                if response.status_code == 200:
                    filings = self._parse_atom_feed(response.text, form_type)
                    for filing in filings:
                        filing_id = filing.get('accession_number', '')
                        if filing_id and filing_id not in seen_ids:
                            seen_ids.add(filing_id)
                            all_filings.append(filing)
                else:
                    logger.warning(f"SEC API returned {response.status_code} for {form_type}")

            except Exception as e:
                logger.warning(f"Error fetching {form_type} filings: {e}")

        # Sort by filed date (most recent first)
        all_filings.sort(key=lambda x: x.get('filed_at', ''), reverse=True)

        # If all feeds fail, use curated topics
        if len(all_filings) == 0:
            all_filings = self._get_curated_topics()

        logger.info(f"SEC spider collected {len(all_filings)} filings")
        return all_filings[:max_results]

    def _parse_atom_feed(self, xml_content: str, form_type: str) -> List[Dict[str, Any]]:
        """Parse SEC EDGAR Atom feed into structured filings."""
        filings = []

        try:
            root = ET.fromstring(xml_content)
            ns = {'atom': 'http://www.w3.org/2005/Atom'}

            for entry in root.findall('atom:entry', ns):
                try:
                    title = entry.find('atom:title', ns)
                    link = entry.find('atom:link', ns)
                    summary = entry.find('atom:summary', ns)
                    updated = entry.find('atom:updated', ns)
                    entry_id = entry.find('atom:id', ns)

                    title_text = title.text if title is not None else ''
                    link_href = link.get('href', '') if link is not None else ''
                    summary_text = summary.text if summary is not None else ''
                    updated_text = updated.text if updated is not None else ''
                    id_text = entry_id.text if entry_id is not None else ''

                    # Parse company name and CIK from title
                    # Format: "8-K - Company Name (0001234567) (Filer)"
                    company_match = re.match(r'[\w\-/]+\s*-\s*(.+?)\s*\((\d+)\)', title_text)
                    company_name = company_match.group(1).strip() if company_match else title_text
                    cik = company_match.group(2) if company_match else ''

                    # Extract accession number from ID
                    accession_match = re.search(r'accession-number=([^\s]+)', id_text)
                    accession_number = accession_match.group(1) if accession_match else ''

                    # Parse summary HTML to extract details
                    summary_clean = html.unescape(summary_text)
                    filed_match = re.search(r'Filed:</b>\s*(\d{4}-\d{2}-\d{2})', summary_clean)
                    filed_date = filed_match.group(1) if filed_match else ''

                    # Extract item descriptions (what the 8-K is about)
                    items = re.findall(r'Item\s+[\d.]+:\s*([^<]+)', summary_clean)
                    item_descriptions = [item.strip() for item in items]

                    # Determine market impact
                    high_impact_keywords = ['earnings', 'acquisition', 'merger', 'ceo', 'cfo',
                                           'resignation', 'appointment', 'material', 'agreement',
                                           'bankruptcy', 'layoff', 'restructuring']
                    description_lower = ' '.join(item_descriptions).lower()
                    is_high_impact = any(kw in description_lower for kw in high_impact_keywords)

                    filings.append({
                        'title': title_text,
                        'url': link_href,
                        'link': link_href,
                        'summary': '; '.join(item_descriptions) if item_descriptions else f'{form_type} Filing',
                        'description': '; '.join(item_descriptions) if item_descriptions else f'{form_type} Filing',
                        'company': company_name,
                        'cik': cik,
                        'form_type': form_type,
                        'form_description': self.FILING_TYPES.get(form_type, form_type),
                        'filed_at': filed_date,
                        'updated_at': updated_text,
                        'accession_number': accession_number,
                        'items': item_descriptions,
                        'is_high_impact': is_high_impact,
                        'source': 'SEC EDGAR',
                        'data_type': 'company_filing',
                        'platform': 'sec',
                        'tags': ['sec', 'edgar', 'filing', form_type.lower()],
                        'timestamp': datetime.now().isoformat(),
                    })

                except Exception as e:
                    logger.warning(f"Error parsing entry: {e}")
                    continue

        except ET.ParseError as e:
            logger.warning(f"XML parse error: {e}")

        return filings

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('8-K Material Events', '8-K', 'Earnings, M&A, leadership changes.'),
            ('10-K Annual Reports', '10-K', 'Comprehensive annual financial info.'),
            ('10-Q Quarterly Reports', '10-Q', 'Quarterly financial statements.'),
            ('Insider Trading (Form 4)', '4', 'Insider buys and sells.'),
            ('IPO Filings (S-1)', 'S-1', 'New public offering registrations.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type={form_type}',
                'link': f'https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type={form_type}',
                'summary': desc,
                'description': desc,
                'form_type': form_type,
                'source': 'SEC EDGAR',
                'data_type': 'filing_category',
                'platform': 'sec',
                'tags': ['sec', 'edgar', form_type.lower()],
                'timestamp': datetime.now().isoformat(),
            }
            for title, form_type, desc in topics
        ]
