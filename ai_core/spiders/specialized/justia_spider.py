"""
Justia Legal News Spider
=========================

Fetches legal news, case summaries, and legal blog content from Justia.

Data Sources:
- https://news.justia.com/ - Legal news and featured dockets
- https://blawgsearch.justia.com/ - Legal blogs directory
- https://law.justia.com/ - Free legal resources and case summaries

All data is publicly accessible, no API key required.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import time

logger = logging.getLogger(__name__)


class JustiaSpider:
    """Spider for fetching legal news and resources from Justia"""

    name = "justia"
    base_url = "https://news.justia.com"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch recent legal news from Justia

        Args:
            max_results: Maximum number of articles to fetch

        Returns:
            List of legal news articles
        """
        all_articles = []

        # Fetch from main legal news feed
        all_articles.extend(self._fetch_legal_news(max_results))

        # Also try case summaries if we don't have enough
        if len(all_articles) < max_results:
            all_articles.extend(self.fetch_case_summaries(max_results=max_results - len(all_articles)))

        return all_articles[:max_results]

    def _fetch_legal_news(self, max_results: int) -> List[Dict[str, Any]]:
        """Fetch articles from Justia legal news"""
        try:
            url = f"{self.base_url}/"
            logger.info(f"Fetching legal news from Justia: {url}")

            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []

            # Find article containers (adjust selectors based on actual HTML structure)
            article_elements = soup.find_all('article', limit=max_results)

            for article_elem in article_elements:
                try:
                    # Extract title
                    title_elem = article_elem.find(['h2', 'h3', 'h4'])
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)

                    # Extract link
                    link_elem = title_elem.find('a') or article_elem.find('a')
                    url = link_elem.get('href', '') if link_elem else ''
                    if url and not url.startswith('http'):
                        url = f"https://news.justia.com{url}"

                    # Extract summary/snippet
                    summary_elem = article_elem.find(['p', 'div'], class_=lambda x: x and ('summary' in x or 'excerpt' in x))
                    summary = summary_elem.get_text(strip=True) if summary_elem else ''

                    # Extract date
                    date_elem = article_elem.find(['time', 'span'], class_=lambda x: x and 'date' in x.lower()) if article_elem else None
                    date_published = date_elem.get_text(strip=True) if date_elem else datetime.now().strftime('%Y-%m-%d')

                    articles.append({
                        'title': title,
                        'url': url,
                        'summary': summary,
                        'date_published': date_published,
                        'source': 'Justia Legal News',
                        'data_type': 'legal_news',
                        'tags': self._extract_tags(title, summary),
                        'timestamp': datetime.now().isoformat(),
                    })

                except Exception as e:
                    logger.warning(f"Error parsing article element: {e}")
                    continue

            logger.info(f"Fetched {len(articles)} legal news articles from Justia")
            return articles

        except Exception as e:
            logger.error(f"Error fetching Justia legal news: {e}")
            return []

    def _fetch_featured_dockets(self, max_results: int) -> List[Dict[str, Any]]:
        """Fetch featured federal dockets from Justia"""
        try:
            url = f"{self.base_url}/dockets"
            logger.info(f"Fetching featured dockets from Justia: {url}")

            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            dockets = []

            # Find docket entries
            docket_elements = soup.find_all('div', class_=lambda x: x and 'docket' in x.lower(), limit=max_results)

            for docket_elem in docket_elements:
                try:
                    # Extract case name
                    title_elem = docket_elem.find(['h3', 'h4', 'a'])
                    if not title_elem:
                        continue

                    case_name = title_elem.get_text(strip=True)

                    # Extract link
                    link_elem = docket_elem.find('a')
                    url = link_elem.get('href', '') if link_elem else ''
                    if url and not url.startswith('http'):
                        url = f"https://news.justia.com{url}"

                    # Extract court and docket number
                    metadata = docket_elem.get_text()
                    court = 'Unknown'
                    docket_num = ''

                    # Try to extract court name
                    court_match = docket_elem.find(text=lambda t: t and 'Court' in t)
                    if court_match:
                        court = court_match.strip()

                    dockets.append({
                        'title': case_name,
                        'case_name': case_name,
                        'court': court,
                        'docket_number': docket_num,
                        'url': url,
                        'source': 'Justia Featured Dockets',
                        'data_type': 'featured_docket',
                        'tags': ['legal', 'docket', 'case', 'featured'],
                        'timestamp': datetime.now().isoformat(),
                    })

                except Exception as e:
                    logger.warning(f"Error parsing docket element: {e}")
                    continue

            logger.info(f"Fetched {len(dockets)} featured dockets from Justia")
            return dockets

        except Exception as e:
            logger.error(f"Error fetching Justia dockets: {e}")
            return []

    def fetch_case_summaries(self, practice_area: str = 'all', max_results: int = 30) -> List[Dict[str, Any]]:
        """
        Fetch case summaries from Justia

        Args:
            practice_area: Practice area filter (e.g., 'criminal', 'civil', 'intellectual-property')
            max_results: Maximum number of summaries to fetch

        Returns:
            List of case summary data
        """
        try:
            # Justia provides free daily case summaries
            url = "https://law.justia.com/cases/"
            logger.info(f"Fetching case summaries from Justia: {url}")

            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            summaries = []

            # Find case summary links
            case_links = soup.find_all('a', href=lambda h: h and '/cases/' in h, limit=max_results)

            for link in case_links:
                try:
                    case_name = link.get_text(strip=True)
                    case_url = link.get('href', '')

                    if not case_url.startswith('http'):
                        case_url = f"https://law.justia.com{case_url}"

                    summaries.append({
                        'title': case_name,
                        'case_name': case_name,
                        'url': case_url,
                        'source': 'Justia Case Law',
                        'data_type': 'case_summary',
                        'tags': ['legal', 'case_summary', 'case_law'],
                        'timestamp': datetime.now().isoformat(),
                    })

                except Exception as e:
                    logger.warning(f"Error parsing case link: {e}")
                    continue

            logger.info(f"Fetched {len(summaries)} case summaries from Justia")
            return summaries

        except Exception as e:
            logger.error(f"Error fetching Justia case summaries: {e}")
            return []

    def _extract_tags(self, title: str, summary: str) -> List[str]:
        """Extract relevant tags from article title and summary"""
        tags = ['legal', 'news']

        text = f"{title} {summary}".lower()

        # Practice areas
        practice_areas = {
            'criminal': ['criminal', 'prosecution', 'defendant', 'sentence'],
            'civil': ['civil', 'plaintiff', 'damages', 'tort'],
            'constitutional': ['constitutional', 'amendment', 'rights', 'supreme court'],
            'corporate': ['corporate', 'business', 'securities', 'merger'],
            'employment': ['employment', 'labor', 'discrimination', 'workplace'],
            'intellectual_property': ['patent', 'copyright', 'trademark', 'ip'],
            'tax': ['tax', 'irs', 'revenue'],
            'immigration': ['immigration', 'visa', 'deportation'],
            'family': ['family', 'divorce', 'custody', 'marriage'],
            'environmental': ['environmental', 'epa', 'pollution', 'climate'],
        }

        for area, keywords in practice_areas.items():
            if any(keyword in text for keyword in keywords):
                tags.append(area)

        # Court levels
        if 'supreme court' in text:
            tags.append('supreme_court')
        elif 'appellate' in text or 'circuit' in text:
            tags.append('appellate')
        elif 'district' in text:
            tags.append('district_court')

        return tags
