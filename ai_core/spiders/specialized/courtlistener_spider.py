"""
CourtListener Legal Spider
===========================

Fetches legal opinions and case law from CourtListener's free REST API.

Data Source: https://www.courtlistener.com/help/api/rest/
- Free REST API from Free Law Project (501c3 nonprofit)
- Federal and state case law
- PACER data and RECAP archive
- Oral argument recordings
- Judge information

No API key required for basic access!
"""

import requests
from typing import Dict, List, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CourtListenerSpider:
    """Spider for fetching legal opinions from CourtListener API"""

    name = "courtlistener"
    base_url = "https://www.courtlistener.com/api/rest/v4"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AI-Content-Studio/1.0 (Legal Research Bot)',
            'Accept': 'application/json'
        })

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch recent legal opinions from CourtListener

        Args:
            max_results: Maximum number of opinions to fetch (default: 50)

        Returns:
            List of legal opinion data dictionaries
        """
        try:
            # Fetch recent opinions (last 7 days)
            date_filed_after = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

            # Search for recent opinions
            search_url = f"{self.base_url}/search/"
            params = {
                'type': 'o',  # Opinions
                'order_by': 'dateFiled desc',
                'date_filed__gte': date_filed_after,
                'page_size': min(max_results, 100)  # API limit
            }

            logger.info(f"Fetching recent legal opinions from CourtListener (since {date_filed_after})")

            response = self.session.get(search_url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            results = data.get('results', [])

            logger.info(f"Successfully fetched {len(results)} legal opinions from CourtListener")

            return self._process_opinions(results)

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching from CourtListener API: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in CourtListener spider: {e}")
            return []

    def _process_opinions(self, results: List[Dict]) -> List[Dict[str, Any]]:
        """Process raw CourtListener opinion data into structured format"""
        processed = []

        for opinion in results:
            try:
                processed_data = {
                    'title': opinion.get('caseName', 'Unknown Case'),
                    'case_name': opinion.get('caseName'),
                    'court': opinion.get('court', 'Unknown Court'),
                    'date_filed': opinion.get('dateFiled'),
                    'citation': opinion.get('citation', []),
                    'docket_number': opinion.get('docketNumber'),
                    'status': opinion.get('status'),
                    'precedential_status': opinion.get('precedentialStatus'),
                    'snippet': opinion.get('snippet', ''),
                    'url': f"https://www.courtlistener.com{opinion.get('absolute_url', '')}",
                    'source': 'CourtListener',
                    'data_type': 'legal_opinion',
                    'tags': self._generate_tags(opinion),
                    'metadata': {
                        'judges': opinion.get('panel', []),
                        'cluster_id': opinion.get('cluster_id'),
                        'opinion_id': opinion.get('id'),
                        'page_count': opinion.get('page_count'),
                    },
                    'timestamp': datetime.now().isoformat(),
                }

                processed.append(processed_data)

            except Exception as e:
                logger.warning(f"Error processing opinion: {e}")
                continue

        return processed

    def _generate_tags(self, opinion: Dict) -> List[str]:
        """Generate relevant tags for the opinion"""
        tags = ['legal', 'case_law', 'court_opinion']

        # Add court type
        court = opinion.get('court', '').lower()
        if 'supreme' in court:
            tags.append('supreme_court')
        elif 'appellate' in court or 'circuit' in court:
            tags.append('appellate')
        elif 'district' in court:
            tags.append('district_court')

        # Add precedential status
        status = opinion.get('precedentialStatus', '').lower()
        if status:
            tags.append(status.replace(' ', '_'))

        # Add practice areas from citations or case name
        case_name = opinion.get('caseName', '').lower()
        if any(term in case_name for term in ['patent', 'copyright', 'trademark']):
            tags.append('intellectual_property')
        if any(term in case_name for term in ['tax', 'irs']):
            tags.append('tax_law')
        if any(term in case_name for term in ['criminal', 'united states v']):
            tags.append('criminal_law')
        if any(term in case_name for term in ['employment', 'labor', 'discrimination']):
            tags.append('employment_law')

        return tags

    def fetch_judges_data(self, max_results: int = 30) -> List[Dict[str, Any]]:
        """Fetch judge biographical data"""
        try:
            judges_url = f"{self.base_url}/people/"
            params = {
                'type': 'person',
                'page_size': max_results
            }

            response = self.session.get(judges_url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            judges = data.get('results', [])

            processed = []
            for judge in judges:
                processed.append({
                    'title': judge.get('name_full', 'Unknown Judge'),
                    'name': judge.get('name_full'),
                    'positions': judge.get('positions', []),
                    'date_dob': judge.get('date_dob'),
                    'gender': judge.get('gender'),
                    'url': f"https://www.courtlistener.com{judge.get('absolute_url', '')}",
                    'source': 'CourtListener',
                    'data_type': 'judge_bio',
                    'tags': ['legal', 'judge', 'biography'],
                    'timestamp': datetime.now().isoformat(),
                })

            logger.info(f"Fetched {len(processed)} judge records from CourtListener")
            return processed

        except Exception as e:
            logger.error(f"Error fetching judges data: {e}")
            return []

    def fetch_oral_arguments(self, max_results: int = 30) -> List[Dict[str, Any]]:
        """Fetch oral argument audio recordings"""
        try:
            audio_url = f"{self.base_url}/audio/"
            date_created_after = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

            params = {
                'date_created__gte': date_created_after,
                'page_size': max_results,
                'order_by': '-date_created'
            }

            response = self.session.get(audio_url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            recordings = data.get('results', [])

            processed = []
            for recording in recordings:
                processed.append({
                    'title': recording.get('case_name', 'Oral Argument'),
                    'case_name': recording.get('case_name'),
                    'court': recording.get('court', 'Unknown Court'),
                    'date_argued': recording.get('date_argued'),
                    'duration': recording.get('duration'),
                    'audio_url': recording.get('download_url'),
                    'docket': recording.get('docket', {}),
                    'url': f"https://www.courtlistener.com{recording.get('absolute_url', '')}",
                    'source': 'CourtListener',
                    'data_type': 'oral_argument',
                    'tags': ['legal', 'oral_argument', 'audio'],
                    'timestamp': datetime.now().isoformat(),
                })

            logger.info(f"Fetched {len(processed)} oral argument recordings")
            return processed

        except Exception as e:
            logger.error(f"Error fetching oral arguments: {e}")
            return []

