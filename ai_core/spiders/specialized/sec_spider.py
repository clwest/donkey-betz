"""
SEC EDGAR Spider - Company Filings Intelligence
================================================

Session 343: Spider for SEC EDGAR API to fetch company filings.
Collects 10-K, 10-Q, 8-K filings for competitor analysis and M&A tracking.

Uses SEC_API_KEY from environment for authenticated requests.
"""

import aiohttp
import asyncio
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class SECSpider(BaseIntelligenceSpider):
    """SEC EDGAR spider - company filings and corporate intelligence"""

    BASE_URL = "https://api.sec-api.io"

    # Filing types to track
    FILING_TYPES = ['10-K', '10-Q', '8-K', 'S-1', 'DEF 14A', '13F-HR']

    # Industries of interest for AI/Tech content
    INDUSTRIES = [
        'Technology',
        'Software',
        'Internet',
        'Artificial Intelligence',
        'Cloud Computing',
        'Digital Media',
        'E-commerce',
    ]

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)
        self.api_key = os.getenv('SEC_API_KEY', '')

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch recent SEC filings"""
        if not self.api_key:
            self.logger.warning("SEC_API_KEY not configured")
            return {'filings': [], 'source': 'sec_edgar', 'error': 'API key not configured'}

        try:
            all_filings = []

            async with aiohttp.ClientSession() as session:
                headers = {'Authorization': self.api_key}

                # Query for recent filings
                query_url = f"{self.BASE_URL}/query"

                # Search for recent tech/AI company filings
                for filing_type in self.FILING_TYPES[:3]:  # Limit to avoid rate limits
                    try:
                        # SEC-API query format
                        query = {
                            "query": {
                                "query_string": {
                                    "query": f"formType:\"{filing_type}\""
                                }
                            },
                            "from": "0",
                            "size": "20",
                            "sort": [{"filedAt": {"order": "desc"}}]
                        }

                        async with session.post(query_url, headers=headers, json=query, timeout=15) as response:
                            if response.status == 200:
                                data = await response.json()
                                filings = data.get('filings', [])

                                for filing in filings:
                                    all_filings.append({
                                        'company': filing.get('companyName', ''),
                                        'ticker': filing.get('ticker', ''),
                                        'cik': filing.get('cik', ''),
                                        'form_type': filing.get('formType', ''),
                                        'filed_at': filing.get('filedAt', ''),
                                        'description': filing.get('description', ''),
                                        'document_url': filing.get('linkToFilingDetails', ''),
                                        'filing_url': filing.get('linkToHtml', ''),
                                        'source': 'sec_edgar',
                                        'type': 'company_filing',
                                    })
                            else:
                                self.logger.warning(f"SEC API returned {response.status}")

                        await asyncio.sleep(0.5)  # Rate limit protection

                    except Exception as e:
                        self.logger.warning(f"Error fetching {filing_type} filings: {e}")

            return {'filings': all_filings, 'source': 'sec_edgar'}

        except Exception as e:
            self.logger.error(f"Error fetching SEC data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
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

            # Extract key insights
            annual_reports = [f for f in filings if f.get('form_type') == '10-K']
            quarterly_reports = [f for f in filings if f.get('form_type') == '10-Q']
            material_events = [f for f in filings if f.get('form_type') == '8-K']

            content = {
                'filings': filings,
                'annual_reports': annual_reports[:10],
                'quarterly_reports': quarterly_reports[:10],
                'material_events': material_events[:10],
                'filing_categories': {k: len(v) for k, v in filing_categories.items()},
                'total_filings': len(filings),
                'unique_companies': len(set(f.get('ticker', '') for f in filings if f.get('ticker'))),
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
                    'source': 'sec_edgar',
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['sec', 'filings', 'corporate', 'financial', '10k', '10q', '8k'],
                target_agents=['competitor_analysis_agent', 'research_agent', 'brand_strategy_agent'],
                target_advisors=['financial_advisor', 'market_strategist', 'business_analyst']
            )

        except Exception as e:
            self.logger.error(f"Error processing SEC data: {e}")
            return None

    def get_required_fields(self) -> List[str]:
        return ['company', 'form_type']

    def get_relevance_keywords(self) -> List[str]:
        return ['sec', 'edgar', 'filing', '10k', '10q', '8k', 'corporate', 'financial']
