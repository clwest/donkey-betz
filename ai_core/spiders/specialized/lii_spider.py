"""
Legal Information Institute (LII) Spider
=========================================

Fetches Supreme Court opinions, federal statutes, and legal resources from Cornell's LII.

Data Sources:
- https://www.law.cornell.edu/supct/ - Supreme Court opinions
- https://www.law.cornell.edu/uscode/ - U.S. Code
- https://www.law.cornell.edu/cfr/ - Code of Federal Regulations
- https://www.law.cornell.edu/constitution/ - U.S. Constitution

All data is publicly accessible, no API key required.
Provided by Cornell Law School's Legal Information Institute.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class LegalInformationInstituteSpider:
    """Spider for fetching legal content from Cornell's Legal Information Institute"""

    name = "lii"
    base_url = "https://www.law.cornell.edu"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch recent Supreme Court opinions and legal resources

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of legal resource data
        """
        all_data = []

        # Fetch Supreme Court opinions
        all_data.extend(self._fetch_supreme_court_opinions(max_results // 2))

        # Fetch recent legal updates
        all_data.extend(self._fetch_recent_updates(max_results // 2))

        return all_data[:max_results]

    def _fetch_supreme_court_opinions(self, max_results: int) -> List[Dict[str, Any]]:
        """Fetch recent Supreme Court opinions"""
        try:
            url = f"{self.base_url}/supct/index.html"
            logger.info(f"Fetching Supreme Court opinions from LII: {url}")

            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            opinions = []

            # Find opinion links
            opinion_links = soup.find_all('a', href=lambda h: h and '/supct/' in h, limit=max_results)

            for link in opinion_links:
                try:
                    title = link.get_text(strip=True)
                    if not title or len(title) < 10:
                        continue

                    opinion_url = link.get('href', '')
                    if not opinion_url.startswith('http'):
                        opinion_url = f"{self.base_url}{opinion_url}"

                    # Extract case citation if available
                    citation = ''
                    parent = link.find_parent(['div', 'li', 'p'])
                    if parent:
                        text = parent.get_text()
                        # Look for citation patterns like "123 U.S. 456"
                        import re
                        citation_match = re.search(r'\d+\s+U\.S\.\s+\d+', text)
                        if citation_match:
                            citation = citation_match.group()

                    opinions.append({
                        'title': title,
                        'case_name': title,
                        'citation': citation,
                        'url': opinion_url,
                        'court': 'Supreme Court of the United States',
                        'source': 'Legal Information Institute',
                        'data_type': 'supreme_court_opinion',
                        'tags': ['legal', 'supreme_court', 'opinion', 'scotus'],
                        'timestamp': datetime.now().isoformat(),
                    })

                except Exception as e:
                    logger.warning(f"Error parsing Supreme Court opinion: {e}")
                    continue

            logger.info(f"Fetched {len(opinions)} Supreme Court opinions from LII")
            return opinions

        except Exception as e:
            logger.error(f"Error fetching LII Supreme Court opinions: {e}")
            return []

    def _fetch_recent_updates(self, max_results: int) -> List[Dict[str, Any]]:
        """Fetch recent legal updates and new content"""
        try:
            url = f"{self.base_url}/"
            logger.info(f"Fetching recent updates from LII: {url}")

            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            updates = []

            # Find recent update sections
            update_sections = soup.find_all(['div', 'section'], class_=lambda x: x and ('recent' in x.lower() or 'update' in x.lower() or 'news' in x.lower()))

            for section in update_sections:
                links = section.find_all('a', href=True, limit=max_results)

                for link in links:
                    try:
                        title = link.get_text(strip=True)
                        if not title or len(title) < 10:
                            continue

                        update_url = link.get('href', '')
                        if not update_url.startswith('http'):
                            update_url = f"{self.base_url}{update_url}"

                        # Determine content type from URL
                        data_type = 'legal_update'
                        tags = ['legal', 'update']

                        if '/uscode/' in update_url:
                            data_type = 'us_code'
                            tags.extend(['us_code', 'statute', 'federal_law'])
                        elif '/cfr/' in update_url:
                            data_type = 'cfr'
                            tags.extend(['cfr', 'regulation', 'administrative_law'])
                        elif '/constitution/' in update_url:
                            data_type = 'constitution'
                            tags.extend(['constitution', 'constitutional_law'])

                        updates.append({
                            'title': title,
                            'url': update_url,
                            'source': 'Legal Information Institute',
                            'data_type': data_type,
                            'tags': tags,
                            'timestamp': datetime.now().isoformat(),
                        })

                    except Exception as e:
                        logger.warning(f"Error parsing update link: {e}")
                        continue

                if len(updates) >= max_results:
                    break

            logger.info(f"Fetched {len(updates)} recent updates from LII")
            return updates[:max_results]

        except Exception as e:
            logger.error(f"Error fetching LII recent updates: {e}")
            return []

    def fetch_us_code(self, title: int = None, max_results: int = 30) -> List[Dict[str, Any]]:
        """
        Fetch U.S. Code sections

        Args:
            title: Specific title number (e.g., 17 for Copyright)
            max_results: Maximum number of sections

        Returns:
            List of U.S. Code sections
        """
        try:
            if title:
                url = f"{self.base_url}/uscode/text/{title}"
            else:
                url = f"{self.base_url}/uscode/text"

            logger.info(f"Fetching U.S. Code from LII: {url}")

            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            code_sections = []

            # Find code section links
            section_links = soup.find_all('a', href=lambda h: h and '/uscode/text/' in h, limit=max_results)

            for link in section_links:
                try:
                    title_text = link.get_text(strip=True)
                    if not title_text:
                        continue

                    section_url = link.get('href', '')
                    if not section_url.startswith('http'):
                        section_url = f"{self.base_url}{section_url}"

                    code_sections.append({
                        'title': title_text,
                        'url': section_url,
                        'source': 'Legal Information Institute',
                        'data_type': 'us_code_section',
                        'tags': ['legal', 'us_code', 'statute', 'federal_law'],
                        'timestamp': datetime.now().isoformat(),
                    })

                except Exception as e:
                    logger.warning(f"Error parsing U.S. Code section: {e}")
                    continue

            logger.info(f"Fetched {len(code_sections)} U.S. Code sections from LII")
            return code_sections

        except Exception as e:
            logger.error(f"Error fetching U.S. Code: {e}")
            return []
