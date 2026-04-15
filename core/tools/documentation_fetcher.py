"""
Real-time Documentation Fetcher Tool
Keeps Code Assistant up-to-date with latest documentation
"""

import logging
import json
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib
import redis

logger = logging.getLogger(__name__)


class DocumentationFetcherTool:
    """
    Fetches and caches real-time documentation from various sources
    to keep the Code Assistant current with latest APIs and frameworks
    """

    def __init__(self):
        self.is_configured = True
        self.session = None
        self.cache = self._init_cache()
        self.cache_ttl = 3600  # 1 hour cache for docs

        # Documentation sources for popular frameworks
        self.doc_sources = {
            'python': {
                'base_url': 'https://docs.python.org/3/',
                'api_docs': 'https://docs.python.org/3/library/',
                'search': 'https://docs.python.org/3/search.html?q='
            },
            'react': {
                'base_url': 'https://react.dev/',
                'api_docs': 'https://react.dev/reference/react',
                'latest': 'https://react.dev/blog'
            },
            'django': {
                'base_url': 'https://docs.djangoproject.com/en/stable/',
                'api_docs': 'https://docs.djangoproject.com/en/stable/ref/',
                'release_notes': 'https://docs.djangoproject.com/en/stable/releases/'
            },
            'typescript': {
                'base_url': 'https://www.typescriptlang.org/docs/',
                'handbook': 'https://www.typescriptlang.org/docs/handbook/',
                'updates': 'https://devblogs.microsoft.com/typescript/'
            },
            'nextjs': {
                'base_url': 'https://nextjs.org/docs',
                'api_ref': 'https://nextjs.org/docs/api-reference',
                'app_router': 'https://nextjs.org/docs/app'
            },
            'nodejs': {
                'base_url': 'https://nodejs.org/docs/latest/api/',
                'api_docs': 'https://nodejs.org/docs/latest/api/',
                'guides': 'https://nodejs.org/en/docs/guides/'
            },
            'openai': {
                'base_url': 'https://platform.openai.com/docs/',
                'api_ref': 'https://platform.openai.com/docs/api-reference',
                'guides': 'https://platform.openai.com/docs/guides'
            },
            'langchain': {
                'base_url': 'https://python.langchain.com/docs/',
                'api_ref': 'https://api.python.langchain.com/',
                'concepts': 'https://python.langchain.com/docs/concepts'
            },
            'fastapi': {
                'base_url': 'https://fastapi.tiangolo.com/',
                'tutorial': 'https://fastapi.tiangolo.com/tutorial/',
                'advanced': 'https://fastapi.tiangolo.com/advanced/'
            }
        }

        # Package registries for version checking
        self.package_registries = {
            'npm': 'https://registry.npmjs.org/',
            'pypi': 'https://pypi.org/pypi/',
            'cargo': 'https://crates.io/api/v1/crates/'
        }

    def _init_cache(self):
        """Initialize Redis cache for documentation"""
        try:
            cache = redis.Redis(
                host='localhost',
                port=6379,
                db=5,  # Dedicated DB for documentation
                decode_responses=True
            )
            cache.ping()
            logger.info("Documentation cache initialized")
            return cache
        except Exception as e:
            # Session 1103c: was BARE 'except:' which would catch
            # KeyboardInterrupt + SystemExit. Now narrow + log the
            # exception type so misconfigured Redis is visible.
            logger.warning(
                "documentation_fetcher: Redis unavailable "
                "(%s: %s) — using in-memory cache",
                type(e).__name__, e,
            )
            return {}

    async def _get_session(self):
        """Get or create aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={'User-Agent': 'CodeAssistant-DocFetcher/1.0'}
            )
        return self.session

    def _cache_key(self, url: str) -> str:
        """Generate cache key for URL"""
        return f"doc:{hashlib.md5(url.encode()).hexdigest()}"

    def _get_cached(self, url: str) -> Optional[str]:
        """Get cached documentation"""
        if isinstance(self.cache, dict):
            return self.cache.get(url)
        try:
            key = self._cache_key(url)
            return self.cache.get(key)
        except Exception as e:
            # Session 1103c: BARE except → narrow + debug-level log
            # (cache misses on Redis errors are common enough that
            # warning would be noisy, but we still want a trail).
            logger.debug(
                "documentation_fetcher: cache get failed for %s "
                "(%s: %s)", url, type(e).__name__, e,
            )
            return None

    def _set_cached(self, url: str, content: str):
        """Cache documentation"""
        if isinstance(self.cache, dict):
            self.cache[url] = content
        else:
            try:
                key = self._cache_key(url)
                self.cache.setex(key, self.cache_ttl, content)
            except Exception as e:
                logger.debug(
                    "documentation_fetcher: cache set failed for %s "
                    "(%s: %s)", url, type(e).__name__, e,
                )

    async def fetch_documentation(self,
                                 framework: str,
                                 topic: str = None,
                                 section: str = 'api_docs') -> Dict[str, Any]:
        """
        Fetch real-time documentation for a framework/library

        Args:
            framework: Name of framework (python, react, django, etc.)
            topic: Specific topic to search for
            section: Section of docs (api_docs, tutorial, guides)
        """
        try:
            if framework not in self.doc_sources:
                return {
                    'success': False,
                    'error': f'Documentation for {framework} not configured',
                    'available': list(self.doc_sources.keys())
                }

            source = self.doc_sources[framework]
            url = source.get(section, source['base_url'])

            if topic:
                # Add search query if topic provided
                if 'search' in source:
                    url = source['search'] + topic
                else:
                    url = url + '#' + topic.replace(' ', '-').lower()

            # Check cache first
            cached = self._get_cached(url)
            if cached:
                logger.info(f"Using cached documentation for {framework}")
                return {
                    'success': True,
                    'framework': framework,
                    'topic': topic,
                    'url': url,
                    'content': cached,
                    'cached': True
                }

            # Fetch fresh documentation
            session = await self._get_session()
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.text()

                    # Extract relevant content (simplified - you'd want proper parsing)
                    # For now, we'll cache the URL for reference
                    doc_summary = {
                        'url': url,
                        'framework': framework,
                        'section': section,
                        'fetched_at': datetime.now().isoformat(),
                        'status': 'available'
                    }

                    self._set_cached(url, json.dumps(doc_summary))

                    return {
                        'success': True,
                        'framework': framework,
                        'topic': topic,
                        'documentation_url': url,
                        'summary': f"Documentation available at {url}",
                        'fresh': True
                    }
                else:
                    return {
                        'success': False,
                        'error': f'Failed to fetch docs: HTTP {response.status}'
                    }

        except Exception as e:
            logger.error(f"Documentation fetch error: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def check_latest_version(self, package: str, registry: str = 'npm') -> Dict[str, Any]:
        """
        Check the latest version of a package

        Args:
            package: Package name
            registry: Registry to check (npm, pypi, cargo)
        """
        try:
            if registry not in self.package_registries:
                return {
                    'success': False,
                    'error': f'Registry {registry} not supported'
                }

            if registry == 'npm':
                url = f"{self.package_registries['npm']}{package}/latest"
            elif registry == 'pypi':
                url = f"{self.package_registries['pypi']}{package}/json"
            else:
                url = f"{self.package_registries['cargo']}{package}"

            session = await self._get_session()
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()

                    if registry == 'npm':
                        version = data.get('version')
                    elif registry == 'pypi':
                        version = data.get('info', {}).get('version')
                    else:
                        version = data.get('crate', {}).get('max_version')

                    return {
                        'success': True,
                        'package': package,
                        'registry': registry,
                        'latest_version': version,
                        'url': url
                    }
                else:
                    return {
                        'success': False,
                        'error': f'Package not found: {package}'
                    }

        except Exception as e:
            logger.error(f"Version check error: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def search_stackoverflow(self, query: str, tags: List[str] = None) -> Dict[str, Any]:
        """
        Search StackOverflow for coding solutions

        Args:
            query: Search query
            tags: Optional tags to filter by
        """
        try:
            base_url = "https://api.stackexchange.com/2.3/search"
            params = {
                'order': 'desc',
                'sort': 'relevance',
                'q': query,
                'site': 'stackoverflow',
                'filter': 'withbody'
            }

            if tags:
                params['tagged'] = ';'.join(tags)

            session = await self._get_session()
            async with session.get(base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    questions = data.get('items', [])[:5]  # Top 5 results

                    results = []
                    for q in questions:
                        results.append({
                            'title': q.get('title'),
                            'link': q.get('link'),
                            'score': q.get('score'),
                            'answered': q.get('is_answered'),
                            'tags': q.get('tags', [])
                        })

                    return {
                        'success': True,
                        'query': query,
                        'results': results,
                        'count': len(results)
                    }
                else:
                    return {
                        'success': False,
                        'error': f'Search failed: HTTP {response.status}'
                    }

        except Exception as e:
            logger.error(f"StackOverflow search error: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def get_api_changes(self, framework: str) -> Dict[str, Any]:
        """
        Get recent API changes or deprecations for a framework

        Args:
            framework: Framework name
        """
        # This would typically fetch from release notes or changelog
        # For now, return structured info about where to find updates

        update_sources = {
            'react': 'https://react.dev/blog',
            'django': 'https://docs.djangoproject.com/en/stable/releases/',
            'typescript': 'https://devblogs.microsoft.com/typescript/',
            'nodejs': 'https://nodejs.org/en/blog/',
            'python': 'https://docs.python.org/3/whatsnew/',
            'nextjs': 'https://nextjs.org/blog'
        }

        if framework in update_sources:
            return {
                'success': True,
                'framework': framework,
                'changes_url': update_sources[framework],
                'message': f'Check {update_sources[framework]} for latest changes'
            }

        return {
            'success': False,
            'error': f'No update source configured for {framework}'
        }

    def execute(self, **kwargs) -> Dict[str, Any]:
        """Synchronous execute method for compatibility"""
        operation = kwargs.get('operation', 'fetch_documentation')

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            if operation == 'fetch_documentation':
                result = loop.run_until_complete(
                    self.fetch_documentation(
                        kwargs.get('framework', 'python'),
                        kwargs.get('topic'),
                        kwargs.get('section', 'api_docs')
                    )
                )
            elif operation == 'check_version':
                result = loop.run_until_complete(
                    self.check_latest_version(
                        kwargs.get('package', ''),
                        kwargs.get('registry', 'npm')
                    )
                )
            elif operation == 'search_stackoverflow':
                result = loop.run_until_complete(
                    self.search_stackoverflow(
                        kwargs.get('query', ''),
                        kwargs.get('tags')
                    )
                )
            elif operation == 'get_api_changes':
                result = loop.run_until_complete(
                    self.get_api_changes(kwargs.get('framework', 'react'))
                )
            else:
                result = {
                    'success': False,
                    'error': f'Unknown operation: {operation}'
                }

            return result

        finally:
            loop.close()

    def get_info(self) -> Dict[str, Any]:
        """Get tool information"""
        return {
            'name': 'Documentation Fetcher',
            'description': 'Fetches real-time documentation for programming frameworks',
            'configured': self.is_configured,
            'supported_frameworks': list(self.doc_sources.keys()),
            'operations': [
                'fetch_documentation',
                'check_version',
                'search_stackoverflow',
                'get_api_changes'
            ],
            'cache_enabled': not isinstance(self.cache, dict)
        }

    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()