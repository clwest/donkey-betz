"""
Spider Action Pipeline
=======================

Session 766: Converts spider data into actionable items and triggers orchestration.

Solves Dead End #5: Spider data is collected and injected into agent context (95%),
but agents don't automatically ACT on spider insights. This pipeline bridges the gap.

Pipeline:
    Spider Data → Analyze for Actions → Create Action Items → Execute via Orchestration

This service:
1. Queries recent spider data for high-value actionable insights
2. Identifies opportunities (jobs, trends, market signals)
3. Creates HumanAttentionItems for review OR triggers orchestration directly
4. Tracks which spider insights led to actions

Usage:
    from core.services.spider_action_pipeline import spider_action_pipeline

    # Process all actionable spider data
    results = spider_action_pipeline.process_actionable_data()

    # Or process specific category
    results = spider_action_pipeline.process_category('jobs')
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import timedelta
from decimal import Decimal
from django.utils import timezone
from django.db import transaction

logger = logging.getLogger(__name__)


class SpiderActionPipeline:
    """
    Pipeline that converts spider data into executed workflows.

    Solves Dead End #5: Spider data collected but not acted upon.
    """

    # Action thresholds by category
    ACTION_THRESHOLDS = {
        'jobs': {
            'min_salary': 80000,  # Only act on jobs >= $80k
            'keywords': ['python', 'django', 'react', 'ai', 'ml', 'remote'],
            'max_age_hours': 48,  # Only recent jobs
        },
        'financial': {
            'price_change_percent': 5.0,  # Act on 5%+ moves
            'volume_spike_multiplier': 2.0,  # Act on 2x volume
            'max_age_hours': 24,
        },
        'tech': {
            'trending_threshold': 10,  # Top 10 trending topics
            'upvote_threshold': 100,  # HN/Reddit items with 100+ upvotes
            'max_age_hours': 24,
        },
        'news': {
            'relevance_keywords': ['ai', 'startup', 'funding', 'acquisition', 'ipo'],
            'max_age_hours': 12,
        },
    }

    # Map categories to workflow templates
    CATEGORY_WORKFLOW_MAP = {
        'jobs': [
            ('ResearchAgent', 'Research the job requirements and company culture'),
            ('ContentWriterAgent', 'Prepare application materials tailored to this role'),
        ],
        'financial': [
            ('MarketIntelligenceAgent', 'Analyze market movement and context'),
            ('ResearchAgent', 'Deep research on the asset/company'),
        ],
        'tech': [
            ('TrendAnalysisAgent', 'Analyze the trending topic for opportunities'),
            ('ContentStrategyAgent', 'Develop content strategy around this trend'),
            ('ContentWriterAgent', 'Create content capitalizing on this trend'),
        ],
        'news': [
            ('ResearchAgent', 'Research the news story and implications'),
            ('ContentWriterAgent', 'Create content or analysis piece'),
        ],
        'default': [
            ('ResearchAgent', 'Research this opportunity'),
            ('ContentStrategyAgent', 'Develop action plan'),
        ],
    }

    def __init__(self):
        self._spider_intelligence = None
        self._orchestration_engine = None
        self._human_attention_bridge = None

    @property
    def spider_intelligence(self):
        """Lazy-load SpiderIntelligenceService."""
        if self._spider_intelligence is None:
            from core.services.spider_intelligence import SpiderIntelligenceService
            self._spider_intelligence = SpiderIntelligenceService()
        return self._spider_intelligence

    @property
    def orchestration_engine(self):
        """Lazy-load orchestration engine."""
        if self._orchestration_engine is None:
            from core.services.orchestration_engine import orchestration_engine
            self._orchestration_engine = orchestration_engine
        return self._orchestration_engine

    @property
    def human_attention_bridge(self):
        """Lazy-load HumanAttentionBridge."""
        if self._human_attention_bridge is None:
            from core.services.human_attention_bridge import HumanAttentionBridge
            self._human_attention_bridge = HumanAttentionBridge()
        return self._human_attention_bridge

    def process_actionable_data(
        self,
        categories: List[str] = None,
        limit_per_category: int = 5,
        auto_execute: bool = False,
        user=None
    ) -> Dict[str, Any]:
        """
        Process all actionable spider data and create actions.

        Args:
            categories: List of categories to process (default: all)
            limit_per_category: Max actions per category
            auto_execute: If True, execute immediately. If False, create HumanAttentionItems.
            user: User for project/workflow ownership

        Returns:
            Dict with processing results
        """
        if categories is None:
            categories = ['jobs', 'financial', 'tech', 'news']

        results = {
            'processed_at': timezone.now().isoformat(),
            'categories': {},
            'total_actions': 0,
            'total_executed': 0,
            'total_attention_items': 0,
        }

        for category in categories:
            try:
                category_result = self.process_category(
                    category=category,
                    limit=limit_per_category,
                    auto_execute=auto_execute,
                    user=user
                )
                results['categories'][category] = category_result
                results['total_actions'] += category_result.get('actions_created', 0)
                results['total_executed'] += category_result.get('workflows_executed', 0)
                results['total_attention_items'] += category_result.get('attention_items_created', 0)
            except Exception as e:
                logger.error(f"Failed to process category {category}: {e}")
                results['categories'][category] = {'error': str(e)}

        logger.info(
            f"🕷️ [Session 766] Spider Action Pipeline: "
            f"{results['total_actions']} actions, "
            f"{results['total_executed']} executed, "
            f"{results['total_attention_items']} attention items"
        )

        return results

    def process_category(
        self,
        category: str,
        limit: int = 5,
        auto_execute: bool = False,
        user=None
    ) -> Dict[str, Any]:
        """
        Process a specific category of spider data.

        Args:
            category: Category to process (jobs, financial, tech, news)
            limit: Maximum number of actions to create
            auto_execute: If True, execute immediately
            user: User for ownership

        Returns:
            Dict with category processing results
        """
        thresholds = self.ACTION_THRESHOLDS.get(category, {})
        max_age_hours = thresholds.get('max_age_hours', 24)

        result = {
            'category': category,
            'actions_created': 0,
            'workflows_executed': 0,
            'attention_items_created': 0,
            'items': [],
        }

        # Get actionable items based on category
        if category == 'jobs':
            items = self._get_actionable_jobs(limit, max_age_hours, thresholds)
        elif category == 'financial':
            items = self._get_actionable_financial(limit, max_age_hours, thresholds)
        elif category == 'tech':
            items = self._get_actionable_tech(limit, max_age_hours, thresholds)
        elif category == 'news':
            items = self._get_actionable_news(limit, max_age_hours, thresholds)
        else:
            items = []

        # Process each actionable item
        for item in items:
            try:
                action_result = self._create_action_for_item(
                    item=item,
                    category=category,
                    auto_execute=auto_execute,
                    user=user
                )
                result['items'].append(action_result)
                result['actions_created'] += 1

                if action_result.get('executed'):
                    result['workflows_executed'] += 1
                if action_result.get('attention_item_created'):
                    result['attention_items_created'] += 1

            except Exception as e:
                logger.error(f"Failed to create action for item: {e}")
                result['items'].append({'error': str(e), 'item': item.get('title', 'Unknown')})

        return result

    def _get_actionable_jobs(
        self,
        limit: int,
        max_age_hours: int,
        thresholds: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get job listings that meet action thresholds."""
        from core.models_unified_system import SpiderData

        since = timezone.now() - timedelta(hours=max_age_hours)
        keywords = thresholds.get('keywords', [])
        min_salary = thresholds.get('min_salary', 0)

        # Query job spider data
        job_spiders = ['remoteok', 'weworkremotely', 'adzuna', 'github_jobs']
        job_data = SpiderData.objects.filter(
            spider_name__in=job_spiders,
            created_at__gte=since
        ).order_by('-created_at')[:100]  # Get recent data

        actionable = []
        seen_titles = set()

        for record in job_data:
            raw_data = self._parse_raw_data(record.raw_data)
            if not raw_data:
                continue

            items = raw_data.get('items', raw_data.get('jobs', []))
            if not isinstance(items, list):
                continue

            for job in items:
                title = job.get('title', '')
                if not title or title in seen_titles:
                    continue

                # Check keywords
                title_lower = title.lower()
                description = job.get('description', '').lower()
                text = f"{title_lower} {description}"

                keyword_match = any(kw in text for kw in keywords)
                if not keyword_match:
                    continue

                # Check salary if available
                salary = job.get('salary', job.get('salary_min', 0))
                if isinstance(salary, str):
                    # Try to parse salary string
                    salary = self._parse_salary(salary)

                seen_titles.add(title)
                actionable.append({
                    'type': 'job',
                    'title': title,
                    'company': job.get('company', job.get('company_name', 'Unknown')),
                    'salary': salary,
                    'url': job.get('url', job.get('link', '')),
                    'location': job.get('location', 'Remote'),
                    'description': job.get('description', '')[:500],
                    'source': record.spider_name,
                    'created_at': record.created_at.isoformat(),
                    'keywords_matched': [kw for kw in keywords if kw in text],
                })

                if len(actionable) >= limit:
                    return actionable

        return actionable

    def _get_actionable_financial(
        self,
        limit: int,
        max_age_hours: int,
        thresholds: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get financial data that meets action thresholds."""
        from core.models_unified_system import SpiderData

        since = timezone.now() - timedelta(hours=max_age_hours)
        price_change_threshold = thresholds.get('price_change_percent', 5.0)

        financial_spiders = ['coingecko', 'yahoo_finance', 'polygon_finance', 'finnhub']
        financial_data = SpiderData.objects.filter(
            spider_name__in=financial_spiders,
            created_at__gte=since
        ).order_by('-created_at')[:50]

        actionable = []
        seen_symbols = set()

        for record in financial_data:
            raw_data = self._parse_raw_data(record.raw_data)
            if not raw_data:
                continue

            # Handle different data formats
            items = raw_data.get('coins', raw_data.get('stocks', raw_data.get('items', [])))
            if not isinstance(items, list):
                continue

            for asset in items:
                symbol = asset.get('symbol', asset.get('ticker', ''))
                if not symbol or symbol in seen_symbols:
                    continue

                # Check price change
                price_change = asset.get('price_change_percentage_24h',
                                        asset.get('change_percent', 0))
                if isinstance(price_change, str):
                    try:
                        price_change = float(price_change.replace('%', ''))
                    except (ValueError, AttributeError):
                        price_change = 0

                if abs(price_change) < price_change_threshold:
                    continue

                seen_symbols.add(symbol)
                actionable.append({
                    'type': 'financial',
                    'title': f"{symbol}: {price_change:+.1f}% price movement",
                    'symbol': symbol,
                    'name': asset.get('name', symbol),
                    'price': asset.get('current_price', asset.get('price', 0)),
                    'price_change': price_change,
                    'volume': asset.get('total_volume', asset.get('volume', 0)),
                    'market_cap': asset.get('market_cap', 0),
                    'source': record.spider_name,
                    'created_at': record.created_at.isoformat(),
                })

                if len(actionable) >= limit:
                    return actionable

        return actionable

    def _get_actionable_tech(
        self,
        limit: int,
        max_age_hours: int,
        thresholds: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get trending tech topics that meet action thresholds."""
        from core.models_unified_system import SpiderData

        since = timezone.now() - timedelta(hours=max_age_hours)
        upvote_threshold = thresholds.get('upvote_threshold', 100)

        tech_spiders = ['hackernews', 'devto', 'producthunt', 'reddit']
        tech_data = SpiderData.objects.filter(
            spider_name__in=tech_spiders,
            created_at__gte=since
        ).order_by('-created_at')[:50]

        actionable = []
        seen_titles = set()

        for record in tech_data:
            raw_data = self._parse_raw_data(record.raw_data)
            if not raw_data:
                continue

            items = raw_data.get('items', raw_data.get('posts', raw_data.get('stories', [])))
            if not isinstance(items, list):
                continue

            for item in items:
                title = item.get('title', '')
                if not title or title in seen_titles:
                    continue

                # Check engagement
                score = item.get('score', item.get('points', item.get('upvotes', 0)))
                if isinstance(score, str):
                    try:
                        score = int(score)
                    except (ValueError, TypeError):
                        score = 0

                if score < upvote_threshold:
                    continue

                seen_titles.add(title)
                actionable.append({
                    'type': 'tech_trend',
                    'title': title,
                    'score': score,
                    'comments': item.get('comments', item.get('num_comments', 0)),
                    'url': item.get('url', item.get('link', '')),
                    'author': item.get('author', item.get('by', 'Unknown')),
                    'source': record.spider_name,
                    'created_at': record.created_at.isoformat(),
                })

                if len(actionable) >= limit:
                    return actionable

        return actionable

    def _get_actionable_news(
        self,
        limit: int,
        max_age_hours: int,
        thresholds: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get news items that meet action thresholds."""
        from core.models_unified_system import SpiderData

        since = timezone.now() - timedelta(hours=max_age_hours)
        relevance_keywords = thresholds.get('relevance_keywords', [])

        news_spiders = ['techcrunch', 'theverge', 'axios', 'bbc', 'reuters_rss']
        news_data = SpiderData.objects.filter(
            spider_name__in=news_spiders,
            created_at__gte=since
        ).order_by('-created_at')[:50]

        actionable = []
        seen_titles = set()

        for record in news_data:
            raw_data = self._parse_raw_data(record.raw_data)
            if not raw_data:
                continue

            items = raw_data.get('items', raw_data.get('articles', []))
            if not isinstance(items, list):
                continue

            for article in items:
                title = article.get('title', '')
                if not title or title in seen_titles:
                    continue

                # Check relevance keywords
                title_lower = title.lower()
                summary = article.get('summary', article.get('description', '')).lower()
                text = f"{title_lower} {summary}"

                matched_keywords = [kw for kw in relevance_keywords if kw in text]
                if not matched_keywords:
                    continue

                seen_titles.add(title)
                actionable.append({
                    'type': 'news',
                    'title': title,
                    'summary': article.get('summary', article.get('description', ''))[:300],
                    'url': article.get('url', article.get('link', '')),
                    'source': record.spider_name,
                    'published': article.get('published', article.get('pubDate', '')),
                    'created_at': record.created_at.isoformat(),
                    'keywords_matched': matched_keywords,
                })

                if len(actionable) >= limit:
                    return actionable

        return actionable

    def _create_action_for_item(
        self,
        item: Dict[str, Any],
        category: str,
        auto_execute: bool,
        user=None
    ) -> Dict[str, Any]:
        """
        Create an action (HumanAttentionItem or Orchestration) for a spider item.

        Args:
            item: The actionable item from spider data
            category: Category of the item
            auto_execute: Whether to execute immediately
            user: User for ownership

        Returns:
            Dict with action creation result
        """
        # Get user if not provided
        if user is None:
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.filter(is_superuser=True).first()
                if not user:
                    user = User.objects.first()
            except Exception as e:
                logger.error(f"Could not get user: {e}")
                return {'error': 'No user available', 'item': item.get('title')}

        result = {
            'item_title': item.get('title', 'Unknown'),
            'item_type': item.get('type', category),
            'source': item.get('source', 'unknown'),
            'executed': False,
            'attention_item_created': False,
        }

        if auto_execute:
            # Create and execute workflow directly
            execution_result = self._execute_spider_action(item, category, user)
            result.update(execution_result)
            result['executed'] = execution_result.get('success', False)
        else:
            # Create HumanAttentionItem for review
            attention_result = self._create_attention_item(item, category, user)
            result.update(attention_result)
            result['attention_item_created'] = attention_result.get('success', False)

        return result

    def _execute_spider_action(
        self,
        item: Dict[str, Any],
        category: str,
        user
    ) -> Dict[str, Any]:
        """Execute a spider action via orchestration."""
        try:
            with transaction.atomic():
                # Create project
                project = self._create_project_from_spider_item(item, category, user)

                # Create workflow
                workflow = self._create_workflow_from_spider_item(item, category, project, user)

                # Execute via orchestration
                execution = self.orchestration_engine.execute_workflow(
                    workflow=workflow,
                    user=user,
                    input_data={
                        'spider_item': item,
                        'category': category,
                        'project_id': str(project.id),
                        'source': item.get('source'),
                        'title': item.get('title'),
                    },
                    async_mode=True
                )

                # Track spider action
                self._track_spider_action(item, category, project, workflow, execution)

                logger.info(
                    f"🕷️ [Session 766] Executed spider action: {item.get('title', '')[:50]} "
                    f"→ Execution {execution.id}"
                )

                return {
                    'success': True,
                    'project_id': str(project.id),
                    'workflow_id': str(workflow.id),
                    'execution_id': str(execution.id),
                }

        except Exception as e:
            logger.error(f"Failed to execute spider action: {e}")
            return {'success': False, 'error': str(e)}

    def _create_attention_item(
        self,
        item: Dict[str, Any],
        category: str,
        user
    ) -> Dict[str, Any]:
        """Create a HumanAttentionItem for review."""
        try:
            from core.models_human_interface import HumanAttentionItem
            from django.contrib.auth import get_user_model

            # Session 978: user is required (non-nullable FK) — fall back to first admin
            if user is None:
                User = get_user_model()
                user = User.objects.filter(is_staff=True, is_active=True).first()
                if user is None:
                    logger.error("No admin user found for spider attention item")
                    return {'success': False, 'error': 'No admin user available'}

            # Determine urgency based on category and item attributes
            urgency = 'medium'
            if category == 'financial' and abs(item.get('price_change', 0)) > 10:
                urgency = 'high'
            elif category == 'jobs' and item.get('salary', 0) > 150000:
                urgency = 'high'
            elif category == 'news' and 'breaking' in item.get('title', '').lower():
                urgency = 'high'

            # Build summary (description for the attention item)
            summary = self._build_attention_description(item, category)

            attention_item = HumanAttentionItem.objects.create(
                user=user,
                title=f"[Spider] {item.get('title', 'Unknown')[:100]}",
                summary=summary,
                item_type='spider_action',  # Use item_type instead of category
                urgency=urgency,
                status='pending',
                source_type='spider_pipeline',
                source_id=item.get('url', ''),
                source_agent='SpiderActionPipeline',
                payload={  # Use payload instead of action_options/context_data
                    'spider_item': item,
                    'category': category,
                    'pipeline': 'spider_action_pipeline',
                    'action_options': [
                        {'id': 'execute', 'label': 'Execute Workflow', 'action': 'trigger_orchestration'},
                        {'id': 'dismiss', 'label': 'Dismiss', 'action': 'dismiss'},
                        {'id': 'watch', 'label': 'Watch', 'action': 'watch'},
                    ],
                }
            )

            logger.info(
                f"🕷️ [Session 766] Created attention item for spider action: "
                f"{item.get('title', '')[:50]}"
            )

            return {
                'success': True,
                'attention_item_id': str(attention_item.id),
            }

        except Exception as e:
            logger.error(f"Failed to create attention item: {e}")
            return {'success': False, 'error': str(e)}

    def _create_project_from_spider_item(self, item: Dict[str, Any], category: str, user):
        """Create a PartnershipProject from spider item."""
        from core.models_partnership import PartnershipProject

        # Map category to project type
        project_type_map = {
            'jobs': 'job_application',
            'financial': 'research',
            'tech': 'content_creation',
            'news': 'content_creation',
        }
        project_type = project_type_map.get(category, 'consulting')

        title = item.get('title', 'Spider Action')[:80]

        project = PartnershipProject.objects.create(
            user=user,
            project_name=f"Spider: {title}",
            project_type=project_type,
            description=f"""
Project created from spider intelligence.

## Spider Data
- **Source:** {item.get('source', 'Unknown')}
- **Category:** {category}
- **Title:** {item.get('title', 'Unknown')}
- **URL:** {item.get('url', 'N/A')}
- **Collected:** {item.get('created_at', 'Unknown')}

## Details
{self._format_item_details(item)}

## Trigger
This project was automatically created by the Spider Action Pipeline
when actionable data was detected from spider intelligence gathering.
            """.strip(),
            status='active',
            ai_contribution_percent=90,  # Spider-driven
            human_contribution_percent=10,
        )

        return project

    def _create_workflow_from_spider_item(
        self,
        item: Dict[str, Any],
        category: str,
        project,
        user
    ):
        """Create a CustomWorkflow from spider item."""
        from core.models_unified_system import CustomWorkflow, CustomWorkflowStep
        from django.utils.text import slugify

        workflow_template = self.CATEGORY_WORKFLOW_MAP.get(
            category,
            self.CATEGORY_WORKFLOW_MAP['default']
        )

        title_slug = slugify(item.get('title', 'spider')[:30])
        workflow = CustomWorkflow.objects.create(
            created_by=user,
            name=f"Spider Action: {item.get('title', 'Unknown')[:80]}",
            slug=f"spider-{category}-{title_slug}-{str(project.id)[:8]}",
            description=f"Workflow generated from spider intelligence ({category})",
            content_type='spider_action',
            category='auto_generated',
            status='active',
            execution_mode='sequential',
            max_retries=2,
            timeout_seconds=3600,
            require_approval_on_error=True,
            config={
                'source': 'spider_action_pipeline',
                'spider_source': item.get('source'),
                'category': category,
                'project_id': str(project.id),
                'item_url': item.get('url', ''),
            }
        )

        # Create workflow steps
        for order, (agent_name, step_description) in enumerate(workflow_template, start=1):
            CustomWorkflowStep.objects.create(
                workflow=workflow,
                order=order,
                name=f"Step {order}: {step_description}",
                description=f"""
{step_description}

Context from Spider Data:
- Title: {item.get('title', 'Unknown')}
- Source: {item.get('source', 'Unknown')}
- Category: {category}
- URL: {item.get('url', 'N/A')}
                """.strip(),
                agent=agent_name,
                config={
                    'spider_context': item,
                    'category': category,
                },
                timeout_seconds=600,
                requires_approval=False,
            )

        return workflow

    def _track_spider_action(self, item, category, project, workflow, execution):
        """Track the spider action for analytics."""
        try:
            from core.models_unified_system import SpiderAction

            SpiderAction.objects.create(
                spider_source=item.get('source', 'unknown'),
                category=category,
                item_title=item.get('title', '')[:200],
                item_url=item.get('url', ''),
                item_data=item,
                project=project,
                workflow_slug=workflow.slug,
                execution_id=str(execution.id),
                action_type='auto_execute',
            )
        except Exception as e:
            # Non-critical - just log
            logger.warning(f"Could not track spider action (model may not exist): {e}")

    def _build_attention_description(self, item: Dict[str, Any], category: str) -> str:
        """Build a description for the attention item."""
        parts = [f"**Category:** {category.title()}\n"]

        if category == 'jobs':
            parts.append(f"**Company:** {item.get('company', 'Unknown')}")
            if item.get('salary'):
                parts.append(f"**Salary:** ${item.get('salary'):,}")
            parts.append(f"**Location:** {item.get('location', 'Remote')}")
            if item.get('keywords_matched'):
                parts.append(f"**Keywords:** {', '.join(item.get('keywords_matched', []))}")
        elif category == 'financial':
            parts.append(f"**Symbol:** {item.get('symbol', 'Unknown')}")
            parts.append(f"**Price Change:** {item.get('price_change', 0):+.1f}%")
            if item.get('price'):
                parts.append(f"**Current Price:** ${item.get('price'):,.2f}")
        elif category == 'tech':
            parts.append(f"**Score:** {item.get('score', 0)}")
            parts.append(f"**Comments:** {item.get('comments', 0)}")
        elif category == 'news':
            if item.get('keywords_matched'):
                parts.append(f"**Keywords:** {', '.join(item.get('keywords_matched', []))}")
            if item.get('summary'):
                parts.append(f"\n**Summary:** {item.get('summary', '')[:200]}...")

        parts.append(f"\n**Source:** {item.get('source', 'Unknown')}")
        if item.get('url'):
            parts.append(f"**URL:** {item.get('url', '')}")

        return "\n".join(parts)

    def _format_item_details(self, item: Dict[str, Any]) -> str:
        """Format item details for project description."""
        details = []
        for key, value in item.items():
            if key in ['type', 'title', 'source', 'created_at', 'url']:
                continue  # Already shown above
            if value:
                details.append(f"- **{key.replace('_', ' ').title()}:** {value}")
        return "\n".join(details) if details else "No additional details"

    def _parse_raw_data(self, raw_data) -> Optional[dict]:
        """Parse raw_data which may be string or dict."""
        if not raw_data:
            return None
        if isinstance(raw_data, dict):
            return raw_data
        if isinstance(raw_data, str):
            try:
                import json
                return json.loads(raw_data)
            except (json.JSONDecodeError, TypeError):
                return None
        return None

    def _parse_salary(self, salary_str: str) -> int:
        """Parse salary string to integer."""
        import re
        if not salary_str:
            return 0
        # Extract numbers from string like "$80,000 - $120,000" or "80k"
        salary_str = salary_str.lower().replace(',', '').replace('$', '')
        match = re.search(r'(\d+)', salary_str)
        if match:
            amount = int(match.group(1))
            if 'k' in salary_str:
                amount *= 1000
            return amount
        return 0

    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get statistics about the spider action pipeline."""
        from core.models_unified_system import SpiderData
        from core.models_human_interface import HumanAttentionItem
        from core.models_orchestration import OrchestrationExecution
        from django.db.models import Count

        # Recent spider data
        since_24h = timezone.now() - timedelta(hours=24)
        spider_data_count = SpiderData.objects.filter(created_at__gte=since_24h).count()

        # Spider-triggered attention items
        spider_attention = HumanAttentionItem.objects.filter(
            category='spider_action'
        ).count()

        # Spider-triggered executions
        spider_executions = OrchestrationExecution.objects.filter(
            workflow__config__source='spider_action_pipeline'
        ).count()

        return {
            'spider_data_24h': spider_data_count,
            'spider_attention_items': spider_attention,
            'spider_executions': spider_executions,
            'action_thresholds': self.ACTION_THRESHOLDS,
        }


# Singleton instance
spider_action_pipeline = SpiderActionPipeline()


def get_spider_action_pipeline() -> SpiderActionPipeline:
    """Get the singleton spider action pipeline instance."""
    return spider_action_pipeline
