"""
SEC EDGAR Spider - Company Filings Intelligence
================================================

Session 343: Spider for SEC EDGAR API to fetch company filings.
Session 385: Updated to use free SEC EDGAR RSS feeds (no API key required).

Collects 8-K, 10-K, 10-Q filings for market intelligence and corporate news.
Uses SEC's public Atom feeds which are free and reliable.
"""

import aiohttp
import asyncio
import os
import re
import html
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
import xml.etree.ElementTree as ET

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class SECSpider(BaseIntelligenceSpider):
    """SEC EDGAR spider - company filings via free RSS feeds"""

    # SEC EDGAR RSS feed base URL
    BASE_URL = "https://www.sec.gov/cgi-bin/browse-edgar"

    # Required User-Agent for SEC (they block requests without proper identification)
    USER_AGENT = "DonkeyBetz/1.0 (AI Content Studio Research Tool; contact@example.com)"

    # Filing types and their market significance
    FILING_TYPES = {
        '8-K': 'Material Events',      # Most market-moving (earnings, M&A, leadership changes)
        '10-K': 'Annual Report',       # Comprehensive financial info
        '10-Q': 'Quarterly Report',    # Quarterly financials
        '4': 'Insider Trading',        # Insider buys/sells
        'S-1': 'IPO Registration',     # New public offerings
        '13F-HR': 'Institutional Holdings',  # What big funds are buying
    }

    def __init__(self, spider_id: str = 'sec_edgar', targets: List[SpiderTarget] = None,
                 subscribers: List[str] = None, redis_config: Dict[str, Any] = None):
        # Handle case where called without full config
        if targets is None:
            targets = []
        if subscribers is None:
            subscribers = []
        if redis_config is None:
            redis_config = {}
        super().__init__(spider_id, targets, subscribers, redis_config)

    def fetch_data(self, max_results: int = 30) -> List[Dict[str, Any]]:
        """
        Synchronous fetch for SEC filings using free RSS feeds.
        Session 385: Rewrote to use free EDGAR feeds instead of paid API.
        """
        import requests

        all_filings = []
        seen_ids = set()

        # Fetch 8-K filings (most market-moving) and 10-K/10-Q for comprehensive coverage
        for form_type in ['8-K', '10-K', '10-Q']:
            try:
                url = f"{self.BASE_URL}?action=getcurrent&type={form_type}&company=&dateb=&owner=include&count=20&output=atom"

                response = requests.get(
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
                    print(f"SEC API returned {response.status_code} for {form_type}")

            except Exception as e:
                print(f"Error fetching {form_type} filings: {e}")

        # Sort by filed date (most recent first)
        all_filings.sort(key=lambda x: x.get('filed_at', ''), reverse=True)

        return all_filings[:max_results]

    def _parse_atom_feed(self, xml_content: str, form_type: str) -> List[Dict[str, Any]]:
        """Parse SEC EDGAR Atom feed into structured filings"""
        filings = []

        try:
            # Parse XML
            root = ET.fromstring(xml_content)

            # Define namespace
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
                    # Format: "urn:tag:sec.gov,2008:accession-number=0001234567-25-000001"
                    accession_match = re.search(r'accession-number=([^\s]+)', id_text)
                    accession_number = accession_match.group(1) if accession_match else ''

                    # Parse summary HTML to extract details
                    # Format: <b>Filed:</b> 2025-12-05 <b>AccNo:</b> ... <br>Item 8.01: ...
                    summary_clean = html.unescape(summary_text)
                    filed_match = re.search(r'Filed:</b>\s*(\d{4}-\d{2}-\d{2})', summary_clean)
                    filed_date = filed_match.group(1) if filed_match else ''

                    # Extract item descriptions (what the 8-K is about)
                    items = re.findall(r'Item\s+[\d.]+:\s*([^<]+)', summary_clean)
                    item_descriptions = [item.strip() for item in items]

                    # Determine market impact based on items
                    high_impact_keywords = ['earnings', 'acquisition', 'merger', 'ceo', 'cfo',
                                           'resignation', 'appointment', 'material', 'agreement',
                                           'bankruptcy', 'layoff', 'restructuring']
                    description_lower = ' '.join(item_descriptions).lower()
                    is_high_impact = any(kw in description_lower for kw in high_impact_keywords)

                    filing = {
                        'title': title_text,
                        'company': company_name,
                        'cik': cik,
                        'form_type': form_type,
                        'form_description': self.FILING_TYPES.get(form_type, form_type),
                        'filed_at': filed_date,
                        'updated_at': updated_text,
                        'accession_number': accession_number,
                        'url': link_href,
                        'items': item_descriptions,
                        'description': '; '.join(item_descriptions) if item_descriptions else f'{form_type} Filing',
                        'is_high_impact': is_high_impact,
                        'source': 'sec_edgar',
                        'type': 'company_filing',
                    }

                    filings.append(filing)

                except Exception as e:
                    print(f"Error parsing entry: {e}")
                    continue

        except ET.ParseError as e:
            print(f"XML parse error: {e}")

        return filings

    async def fetch_data_async(self, target: SpiderTarget = None) -> Optional[Dict[str, Any]]:
        """Async fetch for SEC filings"""
        try:
            all_filings = []
            seen_ids = set()

            async with aiohttp.ClientSession() as session:
                for form_type in ['8-K', '10-K', '10-Q']:
                    try:
                        url = f"{self.BASE_URL}?action=getcurrent&type={form_type}&company=&dateb=&owner=include&count=20&output=atom"

                        headers = {
                            'User-Agent': self.USER_AGENT,
                            'Accept': 'application/atom+xml',
                        }

                        async with session.get(url, headers=headers, timeout=15) as response:
                            if response.status == 200:
                                content = await response.text()
                                filings = self._parse_atom_feed(content, form_type)
                                for filing in filings:
                                    filing_id = filing.get('accession_number', '')
                                    if filing_id and filing_id not in seen_ids:
                                        seen_ids.add(filing_id)
                                        all_filings.append(filing)

                        await asyncio.sleep(0.5)  # Rate limit protection

                    except Exception as e:
                        print(f"Error fetching {form_type}: {e}")

            all_filings.sort(key=lambda x: x.get('filed_at', ''), reverse=True)

            return {'filings': all_filings, 'items': all_filings, 'source': 'sec_edgar'}

        except Exception as e:
            print(f"Error in async SEC fetch: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget = None) -> Optional[IntelligenceData]:
        """Process SEC filings into intelligence"""
        try:
            filings = raw_data.get('filings', [])

            # Categorize by filing type
            filing_categories = {}
            for filing in filings:
                form_type = filing.get('form_type', 'Other')
                if form_type not in filing_categories:
                    filing_categories[form_type] = []
                filing_categories[form_type].append(filing)

            # Identify high-impact filings
            high_impact = [f for f in filings if f.get('is_high_impact')]

            content = {
                'filings': filings,
                'items': filings,  # For compatibility with spider data format
                'high_impact_filings': high_impact[:10],
                'annual_reports': filing_categories.get('10-K', [])[:5],
                'quarterly_reports': filing_categories.get('10-Q', [])[:5],
                'material_events': filing_categories.get('8-K', [])[:10],
                'filing_categories': {k: len(v) for k, v in filing_categories.items()},
                'total_filings': len(filings),
                'high_impact_count': len(high_impact),
                'unique_companies': len(set(f.get('company', '') for f in filings if f.get('company'))),
            }

            quality_score = min(1.0, len(filings) / 30 + 0.3)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='sec.gov/edgar',
                data_type='corporate_intelligence',
                content=content,
                metadata={
                    'filing_count': len(filings),
                    'filing_types': list(filing_categories.keys()),
                    'high_impact_count': len(high_impact),
                    'source': 'sec_edgar',
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['sec', 'filings', 'corporate', 'financial', '8k', '10k', '10q', 'earnings'],
                target_agents=['competitor_analysis_agent', 'research_agent', 'market_intelligence_agent'],
                target_advisors=['financial_advisor', 'market_strategist', 'business_analyst']
            )

        except Exception as e:
            print(f"Error processing SEC data: {e}")
            return None

    def get_required_fields(self) -> List[str]:
        return ['company', 'form_type']

    def get_relevance_keywords(self) -> List[str]:
        return ['sec', 'edgar', 'filing', '10k', '10q', '8k', 'corporate', 'financial', 'earnings', 'merger', 'acquisition']
