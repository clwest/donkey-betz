"""
Documentation Context Builder Service
Session 798: Auto-inject documentation context into agent prompts.

This service:
1. Maps agent types to relevant documentation categories
2. Loads and caches the docs index (_index.json)
3. Builds context with relevant docs for each agent
4. Formats documentation for prompt injection

The goal is to make all agents aware of system architecture,
capabilities, and recent session decisions.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

from django.conf import settings

logger = logging.getLogger(__name__)


class DocsContextBuilder:
    """
    Session 798: Automatically builds documentation context for any agent.

    Usage:
        from core.services.docs_context_builder import get_docs_context_builder

        builder = get_docs_context_builder()
        context = builder.build_context_for_agent(
            agent_name='FullStackDeveloperAgent',
            task='Create a new API endpoint'
        )
    """

    # Map agent types/names to documentation categories they need
    # Format: agent_pattern -> list of doc types/subsystems
    AGENT_DOCS_MAPPINGS = {
        # Creative agents need feature docs
        'image': ['features', 'architecture'],
        'video': ['features', 'architecture'],
        'audio': ['features', 'architecture'],
        '3d': ['features', 'architecture'],

        # Development agents need architecture, API, and integration docs
        # Session 798: Added integration, learning, backend for comprehensive code awareness
        'code_generator': ['architecture', 'api', 'database', 'backend', 'integration', 'learning'],
        'full_stack_developer': ['architecture', 'api', 'database', 'frontend', 'backend', 'integration', 'learning'],
        'code_review': ['architecture', 'guides', 'backend', 'integration'],
        'devops': ['architecture', 'body', 'celery', 'backend', 'integration'],
        'prompt_engineering': ['architecture', 'llm', 'agents', 'learning'],

        # Research agents need broad awareness
        'research': ['architecture', 'agents', 'spiders', 'integration'],
        'content_writer': ['features', 'agents'],
        'technical_document': ['architecture', 'api', 'database', 'backend', 'integration'],

        # Strategy agents need system understanding
        'content_strategy': ['agents', 'spiders', 'features'],
        'brand_strategy': ['features', 'architecture'],
        'marketing_strategy': ['features', 'agents'],

        # Executive agents need comprehensive view
        'cto': ['architecture', 'api', 'database', 'body', 'integration'],
        'coo': ['architecture', 'body', 'agents', 'integration'],
        'creative_director': ['features', 'agents', 'architecture'],
        'system_intelligence': ['architecture', 'body', 'agents', 'integration', 'database'],

        # Analysis agents
        'trend_analysis': ['spiders', 'features'],
        'opportunity_scoring': ['agents', 'features'],
        'market_intelligence': ['spiders', 'api'],

        # Financial agents
        'stock': ['api', 'spiders'],
        'blockchain': ['api', 'spiders'],
        'prediction_market': ['api', 'spiders'],
        'arbitrage': ['api', 'spiders'],

        # Content studio agents
        'autonomous_content_studio': ['agents', 'features', 'spiders'],
        'topic_miner': ['spiders', 'agents'],
        'podcast': ['features', 'agents'],

        # Personal Assistant needs everything
        # Session 798: Added integration, learning, backend, frontend for comprehensive awareness
        'personal_assistant': ['architecture', 'agents', 'body', 'features', 'api', 'integration', 'learning', 'backend', 'frontend'],

        # Workflow agents
        'workflow': ['agents', 'architecture', 'integration', 'learning'],
        'campaign_orchestrator': ['agents', 'features', 'integration'],

        # Default for unmatched agents - Session 798: Added integration for baseline awareness
        'default': ['architecture', 'agents', 'integration'],
    }

    # Task keyword to doc category boosts
    TASK_KEYWORD_BOOSTS = {
        # Architecture keywords
        'architecture': ['architecture'],
        'design': ['architecture', 'features'],
        'structure': ['architecture'],
        'system': ['architecture', 'body'],

        # Agent keywords
        'agent': ['agents'],
        'delegate': ['agents'],
        'specialist': ['agents'],

        # Database keywords
        'database': ['database'],
        'model': ['database'],
        'query': ['database'],
        'table': ['database'],

        # API keywords
        'api': ['api'],
        'endpoint': ['api'],
        'rest': ['api'],

        # Frontend keywords
        'frontend': ['frontend'],
        'react': ['frontend'],
        'ui': ['frontend'],
        'page': ['frontend'],
        'component': ['frontend'],

        # Body system keywords
        'health': ['body'],
        'heart': ['body'],
        'lungs': ['body'],
        'brain': ['body'],
        'skin': ['body'],

        # Integration keywords
        'integration': ['integration'],
        'connect': ['integration'],
        'pipeline': ['integration'],

        # Spider keywords
        'spider': ['spiders'],
        'scrape': ['spiders'],
        'data source': ['spiders'],

        # Learning keywords
        'learn': ['learning'],
        'memory': ['learning', 'memory'],
        'pattern': ['learning'],

        # Celery keywords
        'task': ['celery'],
        'celery': ['celery'],
        'async': ['celery'],
        'background': ['celery'],

        # Session 814: Governance and mission keywords
        'governance': ['governance'],
        'authority': ['governance'],
        'override': ['governance'],
        'approval': ['governance'],
        'gate': ['governance'],
        'mission': ['missions'],
        'goal': ['missions'],
        'focus': ['missions'],
        'priority': ['missions'],
        'canon': ['canon'],
        'playbook': ['playbooks'],
        'workflow': ['playbooks', 'workflows'],
    }

    # Priority documents that should always be considered
    PRIORITY_DOCS = [
        'CLAUDE.md',
        '00-START-NEXT-SESSION.md',
        'docs/ARCHITECTURE.md',
        'docs/AGENTS.md',
        'docs/CAPABILITIES.md',
        'docs/DATABASE_MODEL_REFERENCE.md',
        # Session 814: Governance and mission docs are always high priority
        'docs/governance/SYSTEM_OWNER.md',
        'docs/missions/CURRENT_MISSION.md',
        'docs/canon/INDEX.md',
    ]

    def __init__(self):
        self._index_cache = None
        self._index_loaded_at = None
        self._cache_ttl_seconds = 3600  # 1 hour cache

    def _get_docs_root(self) -> Path:
        """Get the docs root directory."""
        return Path(settings.BASE_DIR)

    def _load_index(self, force_reload: bool = False) -> Dict[str, Any]:
        """Load and cache the docs index."""
        now = datetime.now()

        # Check if cache is valid
        if (
            not force_reload
            and self._index_cache is not None
            and self._index_loaded_at is not None
        ):
            cache_age = (now - self._index_loaded_at).total_seconds()
            if cache_age < self._cache_ttl_seconds:
                return self._index_cache

        # Load index from file
        index_path = self._get_docs_root() / 'docs' / '_index.json'

        try:
            if index_path.exists():
                with open(index_path, 'r', encoding='utf-8') as f:
                    self._index_cache = json.load(f)
                    self._index_loaded_at = now
                    logger.debug(
                        f"📚 [Session 798] Loaded docs index: "
                        f"{len(self._index_cache.get('documents', []))} documents"
                    )
                    return self._index_cache
            else:
                logger.warning(f"📚 [Session 798] Docs index not found at {index_path}")
                return {'documents': [], 'graph': {}}
        except Exception as e:
            logger.error(f"📚 [Session 798] Failed to load docs index: {e}")
            return {'documents': [], 'graph': {}}

    def _get_agent_categories(self, agent_name: str) -> List[str]:
        """Get documentation categories relevant to an agent."""
        # Normalize agent name for matching
        name_lower = agent_name.lower().replace('agent', '').strip()

        # Try exact match first
        for pattern, categories in self.AGENT_DOCS_MAPPINGS.items():
            if pattern in name_lower:
                return categories

        # Fall back to default
        return self.AGENT_DOCS_MAPPINGS['default']

    def _get_task_category_boosts(self, task: str) -> List[str]:
        """Get additional categories based on task keywords."""
        if not task:
            return []

        task_lower = task.lower()
        boosts = []

        for keyword, categories in self.TASK_KEYWORD_BOOSTS.items():
            if keyword in task_lower:
                boosts.extend(categories)

        return list(set(boosts))

    def _filter_docs_by_categories(
        self,
        documents: List[Dict],
        categories: List[str],
        max_docs: int = 10
    ) -> List[Dict]:
        """Filter and rank documents by relevance to categories."""
        scored_docs = []

        for doc in documents:
            score = 0
            doc_type = doc.get('type', '')
            doc_subsystems = doc.get('subsystems', [])
            doc_status = doc.get('status', '')
            doc_path = doc.get('path', '')

            # Skip superseded/deprecated unless explicitly needed
            if doc_status in ['superseded', 'deprecated']:
                continue

            # Priority docs get automatic boost
            if doc_path in self.PRIORITY_DOCS:
                score += 100

            # Match by type
            if doc_type in categories:
                score += 30

            # Match by subsystems
            for subsystem in doc_subsystems:
                if subsystem in categories:
                    score += 20

            # Boost recent sessions (handoffs)
            if doc_type == 'handoff':
                # Extract session number
                session = doc.get('session')
                if session and session >= 790:  # Recent sessions
                    score += 40
                elif session and session >= 780:
                    score += 20

            # Boost by inbound link count (popularity)
            inbound = doc.get('inbound_links_count', 0)
            if inbound > 50:
                score += 15
            elif inbound > 20:
                score += 10
            elif inbound > 5:
                score += 5

            # Only include docs with some relevance
            if score > 0:
                scored_docs.append((score, doc))

        # Sort by score descending
        scored_docs.sort(key=lambda x: x[0], reverse=True)

        # Return top docs
        return [doc for score, doc in scored_docs[:max_docs]]

    def _get_recent_sessions(self, documents: List[Dict], count: int = 5) -> List[Dict]:
        """Get the most recent session handoff documents."""
        handoffs = [
            doc for doc in documents
            if doc.get('type') == 'handoff' and doc.get('session')
        ]

        # Sort by session number descending
        handoffs.sort(key=lambda x: x.get('session', 0), reverse=True)

        return handoffs[:count]

    def _format_doc_for_context(self, doc: Dict) -> str:
        """Format a document entry for prompt injection."""
        path = doc.get('path', '')
        title = doc.get('title', path)
        doc_type = doc.get('type', 'unknown')
        status = doc.get('status', 'unknown')

        return f"- **{title}** (`{path}`) - Type: {doc_type}, Status: {status}"

    def _read_doc_content(self, doc_path: str, max_lines: int = 100) -> Optional[str]:
        """Read the actual content of a document (truncated)."""
        full_path = self._get_docs_root() / doc_path

        try:
            if full_path.exists():
                with open(full_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[:max_lines]
                    content = ''.join(lines)
                    if len(lines) == max_lines:
                        content += f"\n... (truncated, full doc at {doc_path})"
                    return content
        except Exception as e:
            logger.warning(f"📚 [Session 798] Failed to read doc {doc_path}: {e}")

        return None

    # Session 814: Critical docs that MUST be injected with full content
    # These docs contain essential system context that all agents need
    CRITICAL_DOCS = [
        ('CLAUDE.md', 300),  # (path, max_lines) - System overview, stats, architecture
        ('00-START-NEXT-SESSION.md', 200),  # Current session priorities
        ('docs/governance/SYSTEM_OWNER.md', 100),  # Session 814: Human authority framework
        ('docs/missions/CURRENT_MISSION.md', 100),  # Session 814: What agents should focus on
    ]

    def _get_critical_docs_content(self) -> str:
        """
        Session 814: Always read and return the content of critical system docs.

        These docs (CLAUDE.md, 00-START-NEXT-SESSION.md) contain essential context
        that ALL agents need to understand the system state. Without these, agents
        operate without knowledge of system architecture, agent counts, recent
        session decisions, and current priorities.

        Returns:
            Formatted string with critical doc contents for prompt injection
        """
        parts = [
            "## Critical System Context (Session 814)",
            "The following documentation provides essential system context:",
            ""
        ]

        for doc_path, max_lines in self.CRITICAL_DOCS:
            content = self._read_doc_content(doc_path, max_lines=max_lines)
            if content:
                parts.append(f"### {doc_path}")
                parts.append("```markdown")
                parts.append(content)
                parts.append("```")
                parts.append("")
                logger.debug(f"📚 [Session 814] Injected critical doc: {doc_path} ({len(content)} chars)")
            else:
                logger.warning(f"📚 [Session 814] Critical doc not found: {doc_path}")

        return '\n'.join(parts)

    def build_context_for_agent(
        self,
        agent_name: str,
        task: str,
        max_docs: int = 10,
        include_recent_sessions: bool = True,
        include_content_snippets: bool = False,
        max_content_lines: int = 50,
        include_critical_docs: bool = True  # Session 814: Always inject CLAUDE.md, 00-START-NEXT-SESSION.md
    ) -> Dict[str, Any]:
        """
        Build comprehensive documentation context for an agent.

        This is the main method called by AgentRouter to auto-inject
        documentation awareness into agent prompts.

        Args:
            agent_name: Name of the agent
            task: The task being performed
            max_docs: Maximum documents to include
            include_recent_sessions: Include recent session handoffs
            include_content_snippets: Include actual doc content (increases context size)
            max_content_lines: Max lines per content snippet
            include_critical_docs: Session 814 - Always include CLAUDE.md and 00-START-NEXT-SESSION.md
                                   content. These provide essential system context.

        Returns:
            Dict with structured docs context ready for prompt injection
        """
        try:
            # Load index
            index = self._load_index()
            documents = index.get('documents', [])

            if not documents:
                logger.warning(f"📚 [Session 798] No documents in index for {agent_name}")
                return {
                    'has_docs': False,
                    'relevant_docs': [],
                    'recent_sessions': [],
                    'summary': 'Documentation index not available.',
                }

            # Get categories from agent name and task
            agent_categories = self._get_agent_categories(agent_name)
            task_boosts = self._get_task_category_boosts(task)
            all_categories = list(set(agent_categories + task_boosts))

            logger.info(f"📚 [Session 798] Building docs context for {agent_name}")
            logger.debug(f"  Categories: {all_categories}")

            # Filter relevant docs
            relevant_docs = self._filter_docs_by_categories(
                documents, all_categories, max_docs
            )

            # Get recent sessions
            recent_sessions = []
            if include_recent_sessions:
                recent_sessions = self._get_recent_sessions(documents, count=5)

            # Build context dict
            context = {
                'has_docs': len(relevant_docs) > 0,
                'categories_queried': all_categories,
                'relevant_docs': [
                    {
                        'path': doc.get('path'),
                        'title': doc.get('title'),
                        'type': doc.get('type'),
                        'status': doc.get('status'),
                        'session': doc.get('session'),
                        'subsystems': doc.get('subsystems', []),
                        'inbound_links': doc.get('inbound_links_count', 0),
                    }
                    for doc in relevant_docs
                ],
                'recent_sessions': [
                    {
                        'path': doc.get('path'),
                        'title': doc.get('title'),
                        'session': doc.get('session'),
                    }
                    for doc in recent_sessions
                ],
                'total_docs_available': len(documents),
                'summary': '',
            }

            # Build summary for prompt injection
            summary_parts = []

            # Session 814: ALWAYS inject critical docs first (CLAUDE.md, 00-START-NEXT-SESSION.md)
            # These provide essential system context that all agents need
            if include_critical_docs:
                critical_content = self._get_critical_docs_content()
                if critical_content:
                    summary_parts.append(critical_content)
                    summary_parts.append("")  # Blank line separator
                    context['critical_docs_injected'] = True
                    logger.info(f"📚 [Session 814] Critical docs injected for {agent_name}")

            summary_parts.extend([
                f"## Additional Documentation Context",
                f"Total system docs: {len(documents)}",
                f"",
                f"### Relevant Documentation ({len(relevant_docs)} docs):",
            ])

            for doc in relevant_docs[:5]:  # Top 5 for summary
                summary_parts.append(self._format_doc_for_context(doc))

            if include_recent_sessions and recent_sessions:
                summary_parts.append("")
                summary_parts.append("### Recent Sessions:")
                for doc in recent_sessions[:3]:
                    session = doc.get('session', '?')
                    title = doc.get('title', doc.get('path'))
                    summary_parts.append(f"- Session {session}: {title}")

            # Include content snippets if requested
            if include_content_snippets and relevant_docs:
                summary_parts.append("")
                summary_parts.append("### Key Document Excerpts:")
                for doc in relevant_docs[:3]:  # Top 3 content snippets
                    content = self._read_doc_content(doc.get('path'), max_content_lines)
                    if content:
                        summary_parts.append(f"\n**{doc.get('title')}:**")
                        summary_parts.append(f"```\n{content[:2000]}\n```")

            context['summary'] = '\n'.join(summary_parts)

            logger.info(
                f"📚 [Session 798] Docs context built for {agent_name}: "
                f"{len(relevant_docs)} relevant docs, {len(recent_sessions)} recent sessions"
            )

            return context

        except Exception as e:
            logger.error(f"📚 [Session 798] Failed to build docs context: {e}")
            return {
                'has_docs': False,
                'relevant_docs': [],
                'recent_sessions': [],
                'summary': f'Documentation context unavailable: {str(e)}',
            }

    def get_doc_by_path(self, doc_path: str) -> Optional[Dict]:
        """Get a specific document's metadata by path."""
        index = self._load_index()
        for doc in index.get('documents', []):
            if doc.get('path') == doc_path:
                return doc
        return None

    def search_docs(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search documents by title or path."""
        index = self._load_index()
        query_lower = query.lower()

        matches = []
        for doc in index.get('documents', []):
            title = doc.get('title', '').lower()
            path = doc.get('path', '').lower()

            if query_lower in title or query_lower in path:
                matches.append(doc)

        return matches[:max_results]

    def invalidate_cache(self):
        """Force reload of the index on next access."""
        self._index_cache = None
        self._index_loaded_at = None
        logger.info("📚 [Session 798] Docs index cache invalidated")


# Singleton instance
_docs_context_builder: Optional[DocsContextBuilder] = None


def get_docs_context_builder() -> DocsContextBuilder:
    """Get or create the singleton DocsContextBuilder instance."""
    global _docs_context_builder
    if _docs_context_builder is None:
        _docs_context_builder = DocsContextBuilder()
    return _docs_context_builder
