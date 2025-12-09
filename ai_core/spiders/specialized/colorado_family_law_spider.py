"""
Colorado Family Law Forms Spider
================================

Session 403: Spider for Colorado Judicial Branch self-help forms.

Focuses on family law forms for:
- Divorce/Separation (with children)
- Custody/Parenting Time
- Child Support
- Parental Responsibility

Uses Playwright for JavaScript-rendered content.
Source: https://www.coloradojudicial.gov/self-help-forms

All data is publicly accessible from the Colorado Judicial Branch.
"""

import asyncio
import logging
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from bs4 import BeautifulSoup

try:
    from playwright.async_api import async_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

logger = logging.getLogger(__name__)


class ColoradoFamilyLawSpider:
    """Spider for fetching Colorado family law forms and resources"""

    name = "colorado_family_law"
    base_url = "https://www.coloradojudicial.gov"

    # Family law form categories to scrape
    FORM_CATEGORIES = [
        # Divorce with children
        {
            'name': 'Divorce and Separation',
            'search_terms': ['divorce', 'dissolution', 'separation'],
            'tags': ['divorce', 'separation', 'family_law', 'colorado'],
        },
        # Custody and parenting
        {
            'name': 'Custody and Parenting Time',
            'search_terms': ['custody', 'parenting time', 'parental responsibility', 'APR'],
            'tags': ['custody', 'parenting_time', 'children', 'family_law', 'colorado'],
        },
        # Child support
        {
            'name': 'Child Support',
            'search_terms': ['child support', 'support modification'],
            'tags': ['child_support', 'support', 'children', 'family_law', 'colorado'],
        },
        # Parenting plans
        {
            'name': 'Parenting Plans',
            'search_terms': ['parenting plan', 'decision making', 'parenting schedule'],
            'tags': ['parenting_plan', 'custody', 'schedule', 'family_law', 'colorado'],
        },
        # Relocation
        {
            'name': 'Relocation',
            'search_terms': ['relocate', 'relocation', 'move children'],
            'tags': ['relocation', 'move', 'children', 'family_law', 'colorado'],
        },
    ]

    # Known important JDF form numbers for family law
    KEY_FORMS = [
        # Divorce with children
        'JDF 1101',  # Case Information Sheet - Domestic Relations
        'JDF 1102',  # Summons for Dissolution of Marriage
        'JDF 1111',  # Petition for Dissolution of Marriage with Children
        'JDF 1115',  # Response to Petition for Dissolution with Children
        'JDF 1116',  # Decree of Dissolution of Marriage with Children
        # Parenting
        'JDF 1113',  # Parenting Plan
        'JDF 1113.5', # Decision Making Responsibilities
        'JDF 1220',  # Motion to Modify Parenting Time
        'JDF 1221',  # Affidavit for Motion to Modify Parenting Time
        # Child Support
        'JDF 1820',  # Child Support Worksheet A
        'JDF 1821',  # Child Support Worksheet B
        # General
        'JDF 1000',  # Confidential Information Sheet
    ]

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None

    async def start_browser(self):
        """Initialize Playwright browser"""
        if not HAS_PLAYWRIGHT:
            logger.error("Playwright not installed. Run: pip install playwright && playwright install chromium")
            return False

        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                ]
            )
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            )
            logger.info("Colorado Family Law spider browser started")
            return True
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            return False

    async def stop_browser(self):
        """Close Playwright browser"""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            logger.error(f"Error stopping browser: {e}")

    async def fetch_forms_page(self) -> Optional[str]:
        """Fetch the self-help forms page with JavaScript rendering"""
        try:
            page = await self.context.new_page()

            # Navigate to self-help forms page
            url = f"{self.base_url}/self-help-forms"
            logger.info(f"Fetching Colorado forms page: {url}")

            await page.goto(url, wait_until='networkidle', timeout=60000)

            # Wait for form content to load
            await asyncio.sleep(3)

            content = await page.content()
            await page.close()

            return content

        except Exception as e:
            logger.error(f"Error fetching forms page: {e}")
            return None

    async def search_forms(self, search_term: str) -> List[Dict[str, Any]]:
        """Search for forms using the site's search functionality"""
        forms = []

        try:
            page = await self.context.new_page()

            # Go to forms page
            url = f"{self.base_url}/self-help-forms"
            await page.goto(url, wait_until='networkidle', timeout=60000)

            # Try to find and use the search input
            try:
                # Wait for search input
                search_input = await page.wait_for_selector('input[type="search"], input[placeholder*="search"], input#search', timeout=10000)
                if search_input:
                    await search_input.fill(search_term)
                    await search_input.press('Enter')
                    await asyncio.sleep(3)
            except Exception as e:
                logger.warning(f"Search input not found, will parse page directly: {e}")

            # Get page content
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')

            # Look for form links (JDF forms are PDFs or Word docs)
            links = soup.find_all('a', href=True)

            for link in links:
                href = link.get('href', '')
                text = link.get_text(strip=True)

                # Look for JDF form links
                if 'JDF' in text.upper() or '.pdf' in href.lower() or 'form' in href.lower():
                    # Extract form number
                    jdf_match = re.search(r'JDF\s*(\d+(?:\.\d+)?)', text, re.IGNORECASE)
                    form_number = jdf_match.group(0) if jdf_match else ''

                    # Build full URL
                    if href and not href.startswith('http'):
                        href = f"{self.base_url}{href}" if href.startswith('/') else f"{self.base_url}/{href}"

                    forms.append({
                        'title': text,
                        'form_number': form_number,
                        'url': href,
                        'search_term': search_term,
                    })

            await page.close()
            logger.info(f"Found {len(forms)} forms for search term: {search_term}")

        except Exception as e:
            logger.error(f"Error searching for forms with term '{search_term}': {e}")

        return forms

    async def fetch_data(self, max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch family law forms from Colorado Judicial Branch

        Args:
            max_results: Maximum number of forms to fetch

        Returns:
            List of form data dictionaries
        """
        all_forms = []

        try:
            if not await self.start_browser():
                logger.error("Failed to start browser, using fallback data")
                return self._get_fallback_forms()

            # Search for forms in each category
            for category in self.FORM_CATEGORIES:
                for search_term in category['search_terms']:
                    forms = await self.search_forms(search_term)

                    for form in forms:
                        # Add category metadata
                        form_data = {
                            'title': form['title'],
                            'form_number': form['form_number'],
                            'url': form['url'],
                            'category': category['name'],
                            'source': 'Colorado Judicial Branch',
                            'data_type': 'legal_form',
                            'jurisdiction': 'Colorado',
                            'practice_area': 'Family Law',
                            'tags': category['tags'] + ['legal_form', 'self_help'],
                            'timestamp': datetime.now().isoformat(),
                            'summary': f"Colorado family law form: {form['title']}. Category: {category['name']}.",
                        }

                        # Avoid duplicates
                        if not any(f['url'] == form_data['url'] for f in all_forms):
                            all_forms.append(form_data)

                    # Rate limiting
                    await asyncio.sleep(1)

                    if len(all_forms) >= max_results:
                        break

                if len(all_forms) >= max_results:
                    break

            # Also add known key forms
            for jdf_number in self.KEY_FORMS:
                # Check if we already have this form
                if not any(jdf_number in f.get('form_number', '') for f in all_forms):
                    all_forms.append({
                        'title': f'{jdf_number} - Colorado Family Law Form',
                        'form_number': jdf_number,
                        'url': f'{self.base_url}/self-help-forms',
                        'category': 'Key Family Law Forms',
                        'source': 'Colorado Judicial Branch',
                        'data_type': 'legal_form',
                        'jurisdiction': 'Colorado',
                        'practice_area': 'Family Law',
                        'tags': ['legal_form', 'family_law', 'colorado', 'key_form'],
                        'timestamp': datetime.now().isoformat(),
                        'summary': f"Important Colorado family law form {jdf_number}. Search for this form number on the Colorado Judicial Branch website.",
                    })

            await self.stop_browser()

        except Exception as e:
            logger.error(f"Error fetching Colorado family law forms: {e}")
            await self.stop_browser()

        logger.info(f"Total Colorado family law forms collected: {len(all_forms)}")
        return all_forms[:max_results]

    def _get_fallback_forms(self) -> List[Dict[str, Any]]:
        """Return fallback data when browser fails"""
        fallback_forms = []

        for jdf in self.KEY_FORMS:
            # Determine category based on form number
            if '111' in jdf:
                category = 'Divorce and Separation'
                tags = ['divorce', 'family_law', 'colorado']
            elif '112' in jdf or '122' in jdf:
                category = 'Custody and Parenting Time'
                tags = ['custody', 'parenting_time', 'family_law', 'colorado']
            elif '18' in jdf:
                category = 'Child Support'
                tags = ['child_support', 'family_law', 'colorado']
            else:
                category = 'General Family Law'
                tags = ['family_law', 'colorado']

            fallback_forms.append({
                'title': f'{jdf} - Colorado Family Law Form',
                'form_number': jdf,
                'url': f'{self.base_url}/self-help-forms',
                'category': category,
                'source': 'Colorado Judicial Branch',
                'data_type': 'legal_form',
                'jurisdiction': 'Colorado',
                'practice_area': 'Family Law',
                'tags': tags + ['legal_form', 'self_help', 'key_form'],
                'timestamp': datetime.now().isoformat(),
                'summary': f"Colorado family law form {jdf}. Visit the Colorado Judicial Branch website to download.",
            })

        return fallback_forms

    def fetch_data_sync(self, max_results: int = 100) -> List[Dict[str, Any]]:
        """Synchronous wrapper for fetch_data"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.fetch_data(max_results))
