"""
ArXiv Academic Paper Search Tool

This tool provides access to academic papers from ArXiv.org,
allowing agents to search and retrieve scholarly articles.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from django.core.cache import cache

from .base import BaseTool

logger = logging.getLogger(__name__)


class ArXivSearchTool(BaseTool):
    """ArXiv academic paper search tool."""
    
    name = "arxiv_search"
    description = "Search and retrieve academic papers from ArXiv.org"
    requires_auth = False
    tool_type = "research"
    
    def __init__(self):
        """Initialize the ArXiv search tool."""
        self.arxiv = None
        self.cache_duration = 7200  # Cache for 2 hours
        super().__init__()
    
    def _check_configuration(self) -> bool:
        """Check if ArXiv library is available."""
        try:
            import arxiv
            self.arxiv = arxiv
            return True
        except ImportError:
            logger.error("arxiv library not installed. Run: pip install arxiv")
            return False
    
    def get_capabilities(self) -> List[str]:
        """Get list of capabilities."""
        return [
            'paper_search',
            'abstract_retrieval',
            'pdf_download',
            'author_search',
            'category_search',
            'citation_info'
        ]
    
    def execute(self, query: str, max_results: int = 10, sort_by: str = 'relevance', **kwargs) -> Dict[str, Any]:
        """
        Execute an ArXiv search.
        
        Args:
            query: Search query string (can include ArXiv query syntax)
            max_results: Maximum number of results to return
            sort_by: Sort order ('relevance', 'lastUpdatedDate', 'submittedDate')
            **kwargs: Additional search parameters
        
        Returns:
            Dict with search results or error
        """
        if not self.is_configured:
            return self.format_result(
                success=False,
                error="ArXiv search not configured. Install: pip install arxiv"
            )
        
        if not self.validate_input(query=query):
            return self.format_result(
                success=False,
                error="Invalid input parameters"
            )
        
        # Check cache first
        cache_key = f"arxiv_search_{query}_{max_results}_{sort_by}"
        cached = cache.get(cache_key)
        if cached:
            logger.info(f"Returning cached ArXiv results for: {query}")
            return cached
        
        try:
            # Create search object
            search = self.arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=self._get_sort_criterion(sort_by),
                sort_order=self.arxiv.SortOrder.Descending
            )
            
            # Execute search and collect results
            papers = []
            for paper in search.results():
                papers.append(self._format_paper(paper))
            
            # Format and cache result
            result = self.format_result(
                success=True,
                data={
                    'query': query,
                    'papers': papers,
                    'total_results': len(papers),
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            cache.set(cache_key, result, self.cache_duration)
            return result
            
        except Exception as e:
            logger.error(f"ArXiv search error: {e}")
            return self.format_result(
                success=False,
                error=str(e)
            )
    
    def _get_sort_criterion(self, sort_by: str):
        """Get ArXiv sort criterion from string."""
        sort_map = {
            'relevance': self.arxiv.SortCriterion.Relevance,
            'lastUpdatedDate': self.arxiv.SortCriterion.LastUpdatedDate,
            'submittedDate': self.arxiv.SortCriterion.SubmittedDate
        }
        return sort_map.get(sort_by, self.arxiv.SortCriterion.Relevance)
    
    def _format_paper(self, paper) -> Dict[str, Any]:
        """Format ArXiv paper result."""
        return {
            'title': paper.title,
            'summary': paper.summary,
            'authors': [author.name for author in paper.authors],
            'published': paper.published.isoformat() if paper.published else None,
            'updated': paper.updated.isoformat() if paper.updated else None,
            'arxiv_id': paper.entry_id.split('/')[-1],
            'pdf_url': paper.pdf_url,
            'categories': paper.categories,
            'primary_category': paper.primary_category,
            'comment': paper.comment,
            'journal_ref': paper.journal_ref,
            'doi': paper.doi,
            'links': [link.href for link in paper.links]
        }
    
    def get_paper_by_id(self, arxiv_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific paper by ArXiv ID.
        
        Args:
            arxiv_id: ArXiv paper ID (e.g., '2301.00234')
        
        Returns:
            Paper details or None if not found
        """
        if not self.is_configured:
            return None
        
        try:
            search = self.arxiv.Search(id_list=[arxiv_id])
            papers = list(search.results())
            
            if papers:
                return self._format_paper(papers[0])
            
        except Exception as e:
            logger.error(f"Error fetching paper {arxiv_id}: {e}")
        
        return None
    
    def search_by_author(self, author_name: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Search papers by author name.
        
        Args:
            author_name: Author's name
            max_results: Maximum number of results
        
        Returns:
            Dict with search results
        """
        query = f'au:"{author_name}"'
        return self.execute(query, max_results)
    
    def search_by_category(self, category: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Search papers by ArXiv category.
        
        Args:
            category: ArXiv category (e.g., 'cs.AI', 'math.PR')
            max_results: Maximum number of results
        
        Returns:
            Dict with search results
        """
        query = f'cat:{category}'
        return self.execute(query, max_results)
    
    def advanced_search(self, 
                       title: Optional[str] = None,
                       author: Optional[str] = None,
                       abstract: Optional[str] = None,
                       category: Optional[str] = None,
                       date_from: Optional[str] = None,
                       date_to: Optional[str] = None,
                       max_results: int = 10) -> Dict[str, Any]:
        """
        Perform advanced search with multiple criteria.
        
        Args:
            title: Search in title
            author: Search by author
            abstract: Search in abstract
            category: Filter by category
            date_from: Start date (YYYYMMDD format)
            date_to: End date (YYYYMMDD format)
            max_results: Maximum results
        
        Returns:
            Dict with search results
        """
        query_parts = []
        
        if title:
            query_parts.append(f'ti:"{title}"')
        if author:
            query_parts.append(f'au:"{author}"')
        if abstract:
            query_parts.append(f'abs:"{abstract}"')
        if category:
            query_parts.append(f'cat:{category}')
        
        # Date range not directly supported in query, would need post-filtering
        query = ' AND '.join(query_parts) if query_parts else 'all'
        
        return self.execute(query, max_results)
    
    def validate_input(self, query: str = None, **kwargs) -> bool:
        """Validate input parameters."""
        if not query or not isinstance(query, str) or len(query.strip()) == 0:
            return False
        return True
    
    def download_pdf(self, arxiv_id: str, save_path: Optional[str] = None) -> bool:
        """
        Download PDF for a paper (placeholder - actual implementation would save file).
        
        Args:
            arxiv_id: ArXiv paper ID
            save_path: Path to save PDF
        
        Returns:
            True if successful
        """
        if not self.is_configured:
            return False
        
        try:
            paper = self.get_paper_by_id(arxiv_id)
            if paper and paper.get('pdf_url'):
                # In a real implementation, would download and save the PDF
                logger.info(f"PDF URL for {arxiv_id}: {paper['pdf_url']}")
                return True
        except Exception as e:
            logger.error(f"Error downloading PDF: {e}")
        
        return False