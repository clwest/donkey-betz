"""
Content Strategy Agent - Clean Architecture
============================================

Session 280: Phase 2 - Agent Architecture Unification
Session 683: Added ML Integration (Text + Clustering for content performance prediction)

This agent analyzes spider intelligence and trending topics to recommend
what content the user should create next. It follows the clean architecture
pattern with tool isolation and sci-fi/spider context integration.

Tools Available:
    - analyze_trends: Analyze current trends in a niche
    - recommend_content: Get content type recommendations
    - get_opportunities: Find content creation opportunities

Tools NOT Available (by design):
    - image generation (that's ImageAgent)
    - video generation (that's VideoAgent)
    - actual content creation (strategy only)

Usage:
    from core.agents.strategy import ContentStrategyAgent

    agent = ContentStrategyAgent(user=request.user)
    result = agent.execute(
        task="What content should I create for tech audience?",
        context={'niche': 'tech'},
        scifi_context={},
        spider_context={}
    )
"""

import logging
import time
from typing import Dict, Any, Optional, List

from core.agents.base_agent import BaseAgent, AgentResult
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


class ContentStrategyAgent(BaseAgent):
    """
    Agent specialized in content strategy recommendations.

    This agent:
    1. Analyzes trends from spider data
    2. Recommends content types based on niche
    3. Identifies opportunities for content creation

    It CANNOT:
    - Generate images, videos, or audio
    - Create actual content
    - Post to social media
    """

    name = "ContentStrategyAgent"

    system_prompt = """You are ContentStrategyAgent, a specialist in content strategy.

Your job is to analyze trends and recommend what content the user should create.
You have access to spider intelligence data showing current trends and opportunities.

When given a task:
1. Analyze the niche or topic area
2. Consider current trends from spider data
3. Recommend specific content types (logos, thumbnails, social posts, etc.)
4. Provide actionable advice on style, timing, and approach

Content types you can recommend:
- Logo Design: For brand identity and new products
- YouTube Thumbnails: For content creators
- Social Media Posts: Platform-specific content
- Brand Identity Packages: Complete branding suites
- Product Photography: For e-commerce
- Illustrations: For editorial and explainer content

Niches you understand:
- Tech: AI tools, SaaS, developer tools
- Finance: Crypto, investing, fintech
- Creative: Design trends, portfolios
- E-commerce: Products, seasonal content
- Education: Courses, tutorials

You CANNOT create content - just recommend strategy. For actual creation,
the user should use ImageAgent, VideoAgent, etc."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "analyze_trends",
                "description": "Analyze current trends for a specific niche or topic area",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "niche": {
                            "type": "string",
                            "description": "The niche to analyze (tech, finance, creative, ecommerce, education)",
                            "enum": ["tech", "finance", "creative", "ecommerce", "education", "general"]
                        },
                        "timeframe": {
                            "type": "string",
                            "description": "Timeframe for trend analysis",
                            "enum": ["day", "week", "month"],
                            "default": "week"
                        }
                    },
                    "required": ["niche"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "recommend_content",
                "description": "Get content type recommendations for a niche or goal",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "niche": {
                            "type": "string",
                            "description": "The target niche"
                        },
                        "goal": {
                            "type": "string",
                            "description": "The user's goal (brand awareness, sales, engagement, etc.)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of recommendations",
                            "default": 5
                        }
                    },
                    "required": ["niche"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_opportunities",
                "description": "Find content creation opportunities based on current trends",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "niche": {
                            "type": "string",
                            "description": "The target niche"
                        },
                        "content_type": {
                            "type": "string",
                            "description": "Specific content type to focus on",
                            "enum": ["logo", "thumbnail", "social", "brand_identity", "product_photo", "illustration"]
                        }
                    },
                    "required": []
                }
            }
        }
    ]

    # Content type definitions
    CONTENT_TYPES = {
        'logo': {
            'name': 'Logo Design',
            'description': 'Brand logos and identity marks',
            'best_for': ['startups', 'rebranding', 'new products'],
            'trending_keywords': ['minimalist', 'modern', 'abstract', 'lettermark']
        },
        'youtube_thumbnail': {
            'name': 'YouTube Thumbnail',
            'description': 'Eye-catching video thumbnails',
            'best_for': ['content creators', 'educators', 'marketers'],
            'trending_keywords': ['bold text', 'faces', 'bright colors', 'curiosity gap']
        },
        'social_post': {
            'name': 'Social Media Post',
            'description': 'Platform-optimized social content',
            'best_for': ['brands', 'influencers', 'businesses'],
            'trending_keywords': ['carousel', 'quote graphics', 'infographics']
        },
        'brand_identity': {
            'name': 'Brand Identity Package',
            'description': 'Complete branding suite',
            'best_for': ['new businesses', 'rebranding projects'],
            'trending_keywords': ['cohesive', 'scalable', 'memorable']
        },
        'product_photo': {
            'name': 'Product Photography',
            'description': 'Professional product images',
            'best_for': ['e-commerce', 'marketing', 'catalogs'],
            'trending_keywords': ['lifestyle', 'flat lay', 'contextual']
        },
        'illustration': {
            'name': 'Custom Illustration',
            'description': 'Unique artistic illustrations',
            'best_for': ['editorial', 'children content', 'explainers'],
            'trending_keywords': ['flat', 'isometric', 'hand-drawn', '3d']
        }
    }

    # Niche strategies
    NICHE_STRATEGIES = {
        'tech': {
            'hot_topics': ['AI tools', 'automation', 'SaaS', 'developer tools'],
            'recommended_content': ['youtube_thumbnail', 'logo', 'social_post'],
            'style_suggestions': ['futuristic', 'minimalist', 'tech-forward', 'clean']
        },
        'finance': {
            'hot_topics': ['crypto', 'investing', 'personal finance', 'fintech'],
            'recommended_content': ['youtube_thumbnail', 'social_post'],
            'style_suggestions': ['professional', 'trustworthy', 'modern', 'data-driven']
        },
        'creative': {
            'hot_topics': ['design trends', 'creative tools', 'portfolio', 'freelancing'],
            'recommended_content': ['logo', 'brand_identity', 'illustration'],
            'style_suggestions': ['artistic', 'bold', 'experimental', 'colorful']
        },
        'ecommerce': {
            'hot_topics': ['product launches', 'seasonal sales', 'brand building'],
            'recommended_content': ['product_photo', 'social_post', 'logo'],
            'style_suggestions': ['lifestyle', 'aspirational', 'clean', 'branded']
        },
        'education': {
            'hot_topics': ['online courses', 'tutorials', 'explainers', 'edtech'],
            'recommended_content': ['youtube_thumbnail', 'illustration', 'social_post'],
            'style_suggestions': ['friendly', 'clear', 'engaging', 'informative']
        }
    }

    # === Session 683: ML Integration Methods ===

    def _analyze_content_with_ml(
        self,
        content_data: List[Dict[str, Any]],
        niche: str = 'general'
    ) -> Dict[str, Any]:
        """
        Session 683: Analyze content performance using ML (Clustering + Text).

        Uses the Agent-Model Router to cluster content by performance patterns
        and classify content topics for better recommendations.

        Args:
            content_data: List of content items with performance metrics
            niche: Content niche for context

        Returns:
            Dict with ML analysis including content clusters and predictions
        """
        try:
            from core.services.agent_model_router import get_agent_model_router

            router = get_agent_model_router()

            # Build content data for ML
            ml_data = self._build_content_data_for_ml(content_data)

            if not ml_data.get('features'):
                return {
                    'ml_used': False,
                    'reason': 'Insufficient content data for ML analysis'
                }

            # Route to optimal ML model (Clustering for segmentation)
            result = router.auto_route(
                data=ml_data,
                task_hint=TaskType.CLUSTERING,
                max_models=2
            )

            # Extract cluster insights
            clusters = self._extract_content_clusters(result)

            return {
                'ml_used': True,
                'task_type': result.auto_selection.get('task_type', 'clustering'),
                'models_used': result.models_used,
                'confidence': round(result.confidence, 2),
                'ml_insights': result.explanation,
                'content_clusters': clusters,
                'performance_prediction': self._predict_content_performance(result, niche),
                'selection_reason': result.auto_selection.get('selection_reason', ''),
            }

        except Exception as e:
            logger.warning(f"ML content analysis failed: {e}")
            return {
                'ml_used': False,
                'reason': f'ML error: {str(e)}'
            }

    def _build_content_data_for_ml(self, content_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Session 683: Build content feature data for ML clustering.

        Extracts features like engagement metrics, topics, and content types.

        Args:
            content_data: List of content items

        Returns:
            Feature data dict for ML routing
        """
        features = []
        labels = []

        for item in content_data:
            feature_vector = []

            # Extract engagement metrics
            feature_vector.append(float(item.get('score', 0)))
            feature_vector.append(float(item.get('engagement', 0)))
            feature_vector.append(float(item.get('views', 0)))
            feature_vector.append(float(item.get('shares', 0)))

            # Content type as numeric
            content_types = ['logo', 'thumbnail', 'social_post', 'brand_identity', 'product_photo', 'illustration']
            ct = item.get('content_type', 'other')
            feature_vector.append(content_types.index(ct) if ct in content_types else len(content_types))

            features.append(feature_vector)
            labels.append(item.get('title', item.get('topic', 'unknown'))[:50])

        return {
            'features': features,
            'labels': labels,
            'data_type': 'content_performance'
        }

    def _extract_content_clusters(self, ml_result) -> List[Dict[str, Any]]:
        """
        Session 683: Extract content clusters from ML result.

        Args:
            ml_result: EnsemblePrediction from ML router

        Returns:
            List of cluster descriptions
        """
        try:
            clusters = []
            if hasattr(ml_result, 'prediction') and ml_result.prediction:
                # Group by cluster labels
                pred = ml_result.prediction
                if isinstance(pred, list):
                    unique_clusters = set(pred)
                    for cluster_id in unique_clusters:
                        clusters.append({
                            'cluster_id': cluster_id,
                            'size': pred.count(cluster_id),
                            'description': f'Content cluster {cluster_id}'
                        })
            return clusters
        except Exception as _e:
            logger.warning(
                "content_strategy_agent._extract_content_clusters: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return []

    def _predict_content_performance(self, ml_result, niche: str) -> Dict[str, Any]:
        """
        Session 683: Predict content performance based on ML analysis.

        Args:
            ml_result: EnsemblePrediction from ML router
            niche: Content niche

        Returns:
            Performance prediction dict
        """
        try:
            confidence = ml_result.confidence if hasattr(ml_result, 'confidence') else 0.5

            # Get niche-specific recommendations
            strategy = self.NICHE_STRATEGIES.get(niche, self.NICHE_STRATEGIES.get('tech', {}))
            recommended = strategy.get('recommended_content', ['youtube_thumbnail'])

            return {
                'recommended_type': recommended[0] if recommended else 'social_post',
                'confidence': round(confidence, 2),
                'best_performing_style': strategy.get('style_suggestions', ['modern'])[0],
                'predicted_engagement': 'high' if confidence > 0.7 else 'medium' if confidence > 0.4 else 'standard'
            }
        except Exception:
            return {
                'recommended_type': 'social_post',
                'confidence': 0.5,
                'predicted_engagement': 'standard'
            }

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """
        Execute content strategy analysis based on the task.

        Args:
            task: User's strategy request
            context: Additional context (niche, goal)
            scifi_context: Mood, memory, evolution context
            spider_context: Trends, market data context

        Returns:
            AgentResult with strategy recommendations
        """
        start_time = time.time()
        tool_calls_made = []

        # Session 736: Extract spider intelligence for real-time data
        spider_intel = self._extract_spider_intelligence(spider_context)
        if spider_intel['has_data']:
            logger.info(f"🕷️ {self.name} using spider intelligence")

        with self.time_travel_session("content_strategy", task, input_data=context):
            try:
                # Validate task
                if not self._validate_task(task):
                    return AgentResult(
                        success=False,
                        error="Invalid or empty task",
                        agent_name=self.name
                    )

                # Record analysis decision
                self.record_decision(
                    decision_type="task_analysis",
                    action="Analyzing content strategy request",
                    reasoning=f"Received task: {task[:100]}",
                    alternatives=["ask_for_clarification", "suggest_different_approach"],
                    confidence=0.9
                )

                # Build enhanced prompt with context
                full_prompt = self._build_intelligent_prompt(task, scifi_context, spider_context)

                logger.info(f"ContentStrategyAgent executing: {task[:50]}...")

                # Call GPT to analyze and recommend
                gpt_response = self._call_openai(full_prompt)

                # Process tool calls
                if gpt_response.get('tool_calls'):
                    for tool_call in gpt_response['tool_calls']:
                        tool_name = tool_call['name']
                        arguments = tool_call['arguments']

                        self.record_decision(
                            decision_type="tool_selection",
                            action=f"Calling {tool_name}",
                            reasoning=f"Analyzing with args: {arguments}",
                            alternatives=[],
                            confidence=0.95
                        )

                        # Execute the tool
                        tool_result = self._execute_tool_call(
                            tool_name, arguments, spider_context
                        )
                        tool_calls_made.append({
                            'tool': tool_name,
                            'arguments': arguments,
                            'result': tool_result
                        })

                        self.mark_decision_outcome(
                            success=tool_result.get('success', False),
                            result_summary=str(tool_result)[:100]
                        )

                    # Compile recommendations
                    recommendations = []
                    for tc in tool_calls_made:
                        if tc['result'].get('success'):
                            recs = tc['result'].get('recommendations', [])
                            recommendations.extend(recs)

                    execution_time = int((time.time() - start_time) * 1000)

                    result = AgentResult(
                        success=True,
                        message=f"Generated {len(recommendations)} content recommendations",
                        data={
                            'recommendations': recommendations,
                            'task': task,
                            'tool_results': tool_calls_made,
                        },
                        agent_name=self.name,
                        execution_time_ms=execution_time,
                        decisions_made=self._tt_decision_count,
                        tool_calls=tool_calls_made
                    )

                    # Session 380: Learning hooks for collective intelligence
                    self._record_learning_outcome(
                        result=result,
                        task=task,
                        context=context,
                        spider_data_used=bool(spider_context),
                        scifi_context_used=bool(scifi_context)
                    )
                    self._create_execution_memory(
                        result=result,
                        task=task,
                        memory_type="success",
                        importance=0.7
                    )

                    # Session 1006: Persist output to Deliverable
                    self._save_to_deliverable(
                        title=f"Content Strategy: {task[:80]}",
                        content=result.message,
                        deliverable_type='analysis',
                        category='Content Strategy',
                        tags=['content', 'strategy'],
                        metadata={'task': task[:200]},
                    )

                    return result

                else:
                    # GPT responded conversationally
                    result = AgentResult(
                        success=True,
                        message=gpt_response.get('content', ''),
                        data={'type': 'conversation'},
                        agent_name=self.name,
                        execution_time_ms=int((time.time() - start_time) * 1000)
                    )

                    # Session 380: Learning hooks for collective intelligence
                    self._record_learning_outcome(
                        result=result,
                        task=task,
                        context=context,
                        spider_data_used=bool(spider_context),
                        scifi_context_used=bool(scifi_context)
                    )
                    self._create_execution_memory(
                        result=result,
                        task=task,
                        memory_type="success",
                        importance=0.6
                    )

                    return result

            except Exception as e:
                logger.error(f"ContentStrategyAgent error: {e}")
                result = AgentResult(
                    success=False,
                    error=str(e),
                    agent_name=self.name,
                    execution_time_ms=int((time.time() - start_time) * 1000)
                )

                # Session 380: Learning hooks for collective intelligence (failures too)
                self._record_learning_outcome(
                    result=result,
                    task=task,
                    context=context,
                    spider_data_used=bool(spider_context),
                    scifi_context_used=bool(scifi_context)
                )
                self._create_execution_memory(
                    result=result,
                    task=task,
                    memory_type="failure",
                    importance=0.8
                )

                return result

    def _execute_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a strategy tool call.

        Args:
            tool_name: Name of the tool
            arguments: Tool arguments
            spider_context: Spider intelligence data

        Returns:
            Tool execution result
        """
        if tool_name == "analyze_trends":
            return self._analyze_trends(
                niche=arguments.get('niche', 'general'),
                timeframe=arguments.get('timeframe', 'week'),
                spider_context=spider_context
            )

        elif tool_name == "recommend_content":
            return self._recommend_content(
                niche=arguments.get('niche', 'general'),
                goal=arguments.get('goal'),
                limit=arguments.get('limit', 5),
                spider_context=spider_context
            )

        elif tool_name == "get_opportunities":
            return self._get_opportunities(
                niche=arguments.get('niche'),
                content_type=arguments.get('content_type'),
                spider_context=spider_context
            )

        return super()._execute_tool_call(tool_name, arguments)

    def _analyze_trends(
        self,
        niche: str,
        timeframe: str,
        spider_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze trends for a niche."""
        logger.info(f"Analyzing trends for niche: {niche}")

        strategy = self.NICHE_STRATEGIES.get(niche, self.NICHE_STRATEGIES.get('tech'))

        # Get spider trends if available
        spider_trends = spider_context.get('relevant_trends', [])
        trend_topics = [t.get('topic', '') for t in spider_trends[:5]]

        # Session 683: Analyze trends with ML for better recommendations
        ml_analysis = {}
        if spider_trends:
            ml_analysis = self._analyze_content_with_ml(spider_trends, niche)

        recommendations = []
        for content_type in strategy.get('recommended_content', [])[:3]:
            ct_info = self.CONTENT_TYPES.get(content_type, {})
            recommendations.append({
                'content_type': content_type,
                'name': ct_info.get('name', content_type),
                'description': ct_info.get('description', ''),
                'trending_keywords': ct_info.get('trending_keywords', []),
                'style_suggestions': strategy.get('style_suggestions', [])
            })

        result = {
            'success': True,
            'niche': niche,
            'timeframe': timeframe,
            'hot_topics': strategy.get('hot_topics', []) + trend_topics[:3],
            'style_suggestions': strategy.get('style_suggestions', []),
            'recommendations': recommendations
        }

        # Session 683: Add ML insights to result
        if ml_analysis.get('ml_used'):
            result['ml_analysis'] = {
                'models_used': ml_analysis.get('models_used', []),
                'confidence': ml_analysis.get('confidence', 0),
                'content_clusters': ml_analysis.get('content_clusters', []),
                'performance_prediction': ml_analysis.get('performance_prediction', {}),
                'ml_insights': ml_analysis.get('ml_insights', ''),
            }

        return result

    def _recommend_content(
        self,
        niche: str,
        goal: Optional[str],
        limit: int,
        spider_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get content recommendations."""
        logger.info(f"Getting content recommendations for niche: {niche}")

        strategy = self.NICHE_STRATEGIES.get(niche, self.NICHE_STRATEGIES.get('tech'))

        recommendations = []
        for content_type in strategy.get('recommended_content', [])[:limit]:
            ct_info = self.CONTENT_TYPES.get(content_type, {})
            recommendations.append({
                'content_type': content_type,
                'name': ct_info.get('name', content_type),
                'description': ct_info.get('description', ''),
                'best_for': ct_info.get('best_for', []),
                'trending_keywords': ct_info.get('trending_keywords', []),
                'style_suggestions': strategy.get('style_suggestions', []),
                'priority': 'high' if content_type == strategy.get('recommended_content', [])[0] else 'medium'
            })

        return {
            'success': True,
            'niche': niche,
            'goal': goal,
            'recommendations': recommendations
        }

    def _get_opportunities(
        self,
        niche: Optional[str],
        content_type: Optional[str],
        spider_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Find content creation opportunities."""
        logger.info(f"Finding opportunities for niche: {niche}, type: {content_type}")

        opportunities = []

        # Get trends from spider context
        spider_trends = spider_context.get('relevant_trends', [])

        for trend in spider_trends[:5]:
            topic = trend.get('topic', 'Unknown')
            opportunities.append({
                'topic': topic,
                'opportunity': f"Create {content_type or 'content'} about {topic}",
                'urgency': 'high' if trend.get('trending', False) else 'medium',
                'suggested_style': self.NICHE_STRATEGIES.get(niche or 'tech', {}).get('style_suggestions', ['modern'])[0]
            })

        # Add general opportunities if not enough from spider
        if len(opportunities) < 3:
            strategy = self.NICHE_STRATEGIES.get(niche or 'tech', {})
            for topic in strategy.get('hot_topics', [])[:3 - len(opportunities)]:
                opportunities.append({
                    'topic': topic,
                    'opportunity': f"Create content about {topic}",
                    'urgency': 'medium',
                    'suggested_style': strategy.get('style_suggestions', ['modern'])[0]
                })

        return {
            'success': True,
            'opportunities': opportunities,
            'recommendations': opportunities  # Alias for consistency
        }

    def _validate_task(self, task: str) -> bool:
        """Validate the task is appropriate for content strategy."""
        return bool(task and task.strip())
