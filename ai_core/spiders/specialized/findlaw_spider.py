"""
FindLaw Legal Blogs Spider
===========================

Fetches legal news, articles, and blog content from FindLaw.

Data Sources:
- https://www.findlaw.com/legalblogs/ - Legal blogs and articles
- https://www.findlaw.com/ - Legal news and resources

All data is publicly accessible, no API key required.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class FindLawSpider:
    """Spider for fetching legal content from FindLaw"""

    name = "findlaw"
    base_url = "https://www.findlaw.com"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch legal blogs and articles from FindLaw

        Args:
            max_results: Maximum number of articles to fetch

        Returns:
            List of legal blog articles
        """
        all_articles = []

        # Fetch from multiple practice areas for better coverage
        practice_areas = ['criminal', 'family', 'business', 'employment']
        per_area = max_results // len(practice_areas)

        for area in practice_areas:
            articles = self.fetch_practice_area_content(practice_area=area, max_results=per_area)
            all_articles.extend(articles)
            if len(all_articles) >= max_results:
                break

        return all_articles[:max_results]

    def _fetch_legal_blogs(self, max_results: int) -> List[Dict[str, Any]]:
        """Fetch articles from FindLaw legal blogs"""
        try:
            url = f"{self.base_url}/legalblogs/"
            logger.info(f"Fetching legal blogs from FindLaw: {url}")

            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []

            # Find blog article containers
            article_elements = soup.find_all(['article', 'div'], class_=lambda x: x and ('post' in x.lower() or 'article' in x.lower()), limit=max_results)

            for article_elem in article_elements:
                try:
                    # Extract title
                    title_elem = article_elem.find(['h2', 'h3', 'h4', 'a'])
                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)

                    # Extract link
                    link_elem = title_elem if title_elem.name == 'a' else title_elem.find('a')
                    url = link_elem.get('href', '') if link_elem else ''
                    if url and not url.startswith('http'):
                        url = f"{self.base_url}{url}"

                    # Skip if no valid URL
                    if not url or url == self.base_url:
                        continue

                    # Extract summary/excerpt
                    summary_elem = article_elem.find(['p', 'div'], class_=lambda x: x and ('excerpt' in x or 'summary' in x or 'description' in x))
                    if not summary_elem:
                        # Try to find any paragraph
                        summary_elem = article_elem.find('p')

                    summary = summary_elem.get_text(strip=True) if summary_elem else ''

                    # Extract date
                    date_elem = article_elem.find(['time', 'span'], class_=lambda x: x and 'date' in x.lower())
                    date_published = date_elem.get_text(strip=True) if date_elem else datetime.now().strftime('%Y-%m-%d')

                    # Extract author if available
                    author_elem = article_elem.find(['span', 'a'], class_=lambda x: x and 'author' in x.lower())
                    author = author_elem.get_text(strip=True) if author_elem else 'FindLaw Editors'

                    # Extract category/practice area
                    category_elem = article_elem.find(['span', 'a'], class_=lambda x: x and ('category' in x or 'topic' in x))
                    category = category_elem.get_text(strip=True) if category_elem else ''

                    articles.append({
                        'title': title,
                        'url': url,
                        'summary': summary,
                        'author': author,
                        'category': category,
                        'date_published': date_published,
                        'source': 'FindLaw Legal Blogs',
                        'data_type': 'legal_blog',
                        'tags': self._extract_tags(title, summary, category),
                        'timestamp': datetime.now().isoformat(),
                    })

                except Exception as e:
                    logger.warning(f"Error parsing blog article: {e}")
                    continue

            logger.info(f"Fetched {len(articles)} legal blog articles from FindLaw")
            return articles

        except Exception as e:
            logger.error(f"Error fetching FindLaw blogs: {e}")
            return []

    def fetch_practice_area_content(self, practice_area: str = 'criminal', max_results: int = 30) -> List[Dict[str, Any]]:
        """
        Fetch content from specific practice area

        Args:
            practice_area: Practice area (e.g., 'criminal', 'family', 'injury', 'business')
            max_results: Maximum number of articles

        Returns:
            List of practice area articles
        """
        try:
            # FindLaw organizes content by practice areas
            practice_area_urls = {
                'criminal': '/criminal',
                'family': '/family',
                'injury': '/injury',
                'business': '/smallbusiness',
                'estate': '/estate',
                'employment': '/employment',
                'real-estate': '/realestate',
                'bankruptcy': '/bankruptcy',
                'immigration': '/immigration',
                'tax': '/tax',
            }

            path = practice_area_urls.get(practice_area, f'/{practice_area}')
            url = f"{self.base_url}{path}/"

            logger.info(f"Fetching {practice_area} law content from FindLaw: {url}")

            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []

            # Find article links
            article_links = soup.find_all('a', href=lambda h: h and path in h, limit=max_results)

            for link in article_links:
                try:
                    title = link.get_text(strip=True)
                    if not title or len(title) < 10:
                        continue

                    article_url = link.get('href', '')
                    if not article_url.startswith('http'):
                        article_url = f"{self.base_url}{article_url}"

                    # Skip duplicate base URLs
                    if article_url == url or article_url == f"{self.base_url}{path}/":
                        continue

                    articles.append({
                        'title': title,
                        'url': article_url,
                        'practice_area': practice_area,
                        'source': 'FindLaw',
                        'data_type': 'legal_article',
                        'tags': ['legal', 'article', practice_area.replace('-', '_')],
                        'timestamp': datetime.now().isoformat(),
                    })

                except Exception as e:
                    logger.warning(f"Error parsing practice area link: {e}")
                    continue

            logger.info(f"Fetched {len(articles)} {practice_area} law articles from FindLaw")
            return articles

        except Exception as e:
            logger.error(f"Error fetching FindLaw practice area content: {e}")
            return []

    def _extract_tags(self, title: str, summary: str, category: str = '') -> List[str]:
        """Extract relevant tags from content"""
        tags = ['legal', 'blog', 'article']

        text = f"{title} {summary} {category}".lower()

        # Practice areas
        practice_areas = {
            'criminal_law': ['criminal', 'prosecution', 'defense', 'felony', 'misdemeanor'],
            'family_law': ['family', 'divorce', 'custody', 'child support', 'alimony'],
            'personal_injury': ['injury', 'accident', 'negligence', 'damages', 'compensation'],
            'business_law': ['business', 'corporate', 'contract', 'partnership', 'llc'],
            'estate_planning': ['estate', 'will', 'trust', 'probate', 'inheritance'],
            'employment_law': ['employment', 'workplace', 'discrimination', 'wrongful termination'],
            'real_estate': ['real estate', 'property', 'landlord', 'tenant', 'deed'],
            'bankruptcy': ['bankruptcy', 'debt', 'chapter 7', 'chapter 13', 'creditor'],
            'immigration': ['immigration', 'visa', 'green card', 'citizenship', 'deportation'],
            'intellectual_property': ['patent', 'copyright', 'trademark', 'trade secret'],
        }

        for area, keywords in practice_areas.items():
            if any(keyword in text for keyword in keywords):
                tags.append(area)

        # Legal topics
        if 'litigation' in text or 'lawsuit' in text:
            tags.append('litigation')
        if 'compliance' in text or 'regulation' in text:
            tags.append('compliance')
        if 'contract' in text:
            tags.append('contracts')

        return list(set(tags))  # Remove duplicates
