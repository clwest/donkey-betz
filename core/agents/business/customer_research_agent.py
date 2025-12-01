"""
Customer Research Agent - Business Intelligence
================================================

Session 293: Business Research Extension

This agent researches potential customers for a business idea.
It uses spider data (especially Reddit) and web search to:
1. Identify target customer segments
2. Extract pain points and needs
3. Analyze customer sentiment
4. Build customer personas

Tools Available:
    - spider_query: Query Reddit and forums for customer discussions
    - web_search: Search for customer reviews and feedback
    - analyze_pain_points: Extract pain points from discussions
    - build_persona: Build customer persona from research

Tools NOT Available (by design):
    - image/video/audio generation
    - editing operations
"""

import logging
import time
import json
import re
from typing import Dict, Any, List
from collections import Counter

from core.agents.base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)


class CustomerResearchAgent(BaseAgent):
    """
    Agent specialized in customer research and persona development.

    This agent:
    1. Takes a market/product description
    2. Searches Reddit, forums, and reviews for customer discussions
    3. Extracts pain points, needs, and desires
    4. Builds customer personas with demographics and motivations

    It CANNOT:
    - Generate images, videos, or audio
    - Edit any content
    - Create 3D models
    """

    name = "CustomerResearchAgent"

    system_prompt = """You are CustomerResearchAgent, a specialist in customer research and persona development.

Your ONLY job is to research potential customers and build personas. You do NOT create content.

You have these tools:
- spider_query: Query Reddit (20+ subreddits), HackerNews, and forums for customer discussions
- web_search: Search for customer reviews, testimonials, and feedback
- analyze_pain_points: Extract pain points from gathered discussions
- build_persona: Build detailed customer persona from research

When given a customer research task:
1. First identify the target market from the user's description
2. Search Reddit for discussions about the problem/need
3. Search for reviews of existing solutions
4. Extract common pain points and desires
5. Build 2-3 customer personas

Reddit subreddits to consider:
- r/Entrepreneur, r/startups, r/smallbusiness for business ideas
- r/SaaS, r/webdev, r/programming for tech products
- r/marketing, r/socialmedia for marketing tools
- r/productivity, r/getdisciplined for productivity tools
- Industry-specific subreddits based on the market

Output Format:
Return structured research with:
- target_market: Description of the target market
- pain_points: List of customer pain points with frequency
- desires: What customers want but can't find
- personas: 2-3 detailed customer personas
- quotes: Direct quotes from customers (anonymized)
- recommendations: Product/messaging recommendations

You CANNOT create images, videos, audio, or edit anything. Only research customers.
If asked to create content, explain you can only research and suggest using the appropriate agent."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "spider_query",
                "description": "Query Reddit, HackerNews, and forums for customer discussions and pain points",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query (e.g., 'AI writing tool frustrating', 'need better podcast hosting')"
                        },
                        "subreddits": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific subreddits to search (optional)",
                            "default": None
                        },
                        "sentiment": {
                            "type": "string",
                            "description": "Filter by sentiment",
                            "enum": ["positive", "negative", "question", "all"],
                            "default": "all"
                        },
                        "hours": {
                            "type": "integer",
                            "description": "Look back period in hours",
                            "default": 720
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max results to return",
                            "default": 50
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Search for customer reviews, testimonials, and feedback about existing solutions",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query (e.g., 'Jasper AI reviews', 'podcast hosting complaints')"
                        },
                        "search_type": {
                            "type": "string",
                            "description": "Type of search",
                            "enum": ["reviews", "discussions", "news"],
                            "default": "reviews"
                        },
                        "num_results": {
                            "type": "integer",
                            "description": "Number of results",
                            "default": 15
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "analyze_pain_points",
                "description": "Analyze gathered discussions to extract and rank pain points",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "discussions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of discussion texts to analyze"
                        },
                        "market_context": {
                            "type": "string",
                            "description": "Context about the market/product"
                        }
                    },
                    "required": ["market_context"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "build_persona",
                "description": "Build a detailed customer persona from research findings",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "persona_type": {
                            "type": "string",
                            "description": "Type of persona (e.g., 'Early Adopter', 'Price-Sensitive', 'Power User')"
                        },
                        "pain_points": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Key pain points for this persona"
                        },
                        "goals": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "What this persona wants to achieve"
                        },
                        "market_context": {
                            "type": "string",
                            "description": "The market/product context"
                        }
                    },
                    "required": ["persona_type", "market_context"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "extract_quotes",
                "description": "Extract powerful customer quotes from discussions for messaging/copy",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "Topic to find quotes about"
                        },
                        "quote_type": {
                            "type": "string",
                            "description": "Type of quotes to find",
                            "enum": ["pain", "desire", "frustration", "praise", "all"],
                            "default": "all"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max quotes to return",
                            "default": 10
                        }
                    },
                    "required": ["topic"]
                }
            }
        }
    ]

    # Pain point indicators for extraction
    PAIN_INDICATORS = [
        'frustrated', 'annoying', 'hate', 'wish', 'problem', 'issue',
        'difficult', 'hard to', 'can\'t find', 'looking for', 'need',
        'expensive', 'too slow', 'doesn\'t work', 'broken', 'buggy',
        'missing', 'lacks', 'want', 'hoping', 'struggling'
    ]

    DESIRE_INDICATORS = [
        'love', 'wish', 'hope', 'want', 'need', 'looking for',
        'would pay for', 'dream', 'ideal', 'perfect', 'best'
    ]

    def __init__(self, user=None):
        super().__init__(user)
        self._spider_service = None
        self._gathered_discussions = []

    @property
    def spider_service(self):
        """Lazy-load Spider Intelligence Service."""
        if self._spider_service is None:
            from core.services.spider_intelligence import SpiderIntelligenceService
            self._spider_service = SpiderIntelligenceService()
        return self._spider_service

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """Execute customer research based on the task."""
        start_time = time.time()
        tool_calls_made = []
        all_research_data = []
        self._gathered_discussions = []

        with self.time_travel_session("customer_research", task, input_data=context):
            try:
                if not self._validate_task(task):
                    return AgentResult(
                        success=False,
                        error="Invalid or empty task",
                        agent_name=self.name
                    )

                self.record_decision(
                    decision_type="task_analysis",
                    action="Analyzing customer research request",
                    reasoning=f"Received task: {task[:100]}",
                    confidence=0.9
                )

                # Build prompt with context
                full_prompt = self._build_prompt(task, scifi_context, spider_context)

                # Add instruction to be comprehensive
                full_prompt += """

IMPORTANT: For thorough customer research:
1. First use spider_query to find Reddit/forum discussions about this problem
2. Use web_search to find reviews of existing solutions
3. Use analyze_pain_points to synthesize findings
4. Use build_persona to create 2-3 customer personas
5. Use extract_quotes to find powerful customer quotes

Return comprehensive customer research with personas and pain points."""

                # Make GPT call to determine tools to use
                gpt_response = self._call_openai(full_prompt)

                # Process tool calls
                if gpt_response.get('tool_calls'):
                    for tool_call in gpt_response['tool_calls']:
                        tool_name = tool_call['name']
                        arguments = tool_call['arguments']

                        self.record_decision(
                            decision_type="tool_selection",
                            action=f"Calling {tool_name}",
                            reasoning=f"Selected {tool_name} for customer research",
                            confidence=0.95
                        )

                        tool_result = self._execute_tool_call(tool_name, arguments)
                        tool_calls_made.append({
                            'tool': tool_name,
                            'arguments': arguments,
                            'result': tool_result
                        })

                        if tool_result.get('success'):
                            all_research_data.append({
                                'source': tool_name,
                                'data': tool_result.get('data', tool_result)
                            })

                        self.mark_decision_outcome(
                            success=tool_result.get('success', False),
                            result_summary=str(tool_result)[:100]
                        )

                execution_time = int((time.time() - start_time) * 1000)

                if all_research_data:
                    # Synthesize the customer research
                    synthesis = self._synthesize_research(task, all_research_data)

                    # Session 294: Save to database with embedding for semantic search
                    saved_result = None
                    try:
                        from core.models_unified_system import BusinessResearchResult
                        saved_result = BusinessResearchResult.save_customer_research(
                            query=task,
                            synthesis=synthesis,
                            execution_time_ms=execution_time
                        )
                        logger.info(f"Saved customer research to database: {saved_result.id}")
                    except Exception as e:
                        logger.warning(f"Failed to save customer research: {e}")

                    # Session 294: Return analysis at top level for frontend compatibility
                    # Frontend checks agentResult.analysis and agentResult.data?.analysis
                    return AgentResult(
                        success=True,
                        message=f"Customer research completed with {len(all_research_data)} data sources",
                        data={
                            'analysis': synthesis,  # Match CompetitorAnalysisAgent pattern
                            'raw_data': all_research_data,
                            'query': task,
                            'saved_id': str(saved_result.id) if saved_result else None
                        },
                        agent_name=self.name,
                        execution_time_ms=execution_time,
                        decisions_made=self._tt_decision_count,
                        tool_calls=tool_calls_made
                    )
                else:
                    return AgentResult(
                        success=True,
                        message=gpt_response.get('content', 'No customer data found'),
                        data={'type': 'conversation'},
                        agent_name=self.name,
                        execution_time_ms=execution_time
                    )

            except Exception as e:
                logger.error(f"CustomerResearchAgent error: {e}")
                return AgentResult(
                    success=False,
                    error=str(e),
                    agent_name=self.name,
                    execution_time_ms=int((time.time() - start_time) * 1000)
                )

    def _execute_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a tool call for customer research."""

        if tool_name == "spider_query":
            return self._search_customer_discussions(
                query=arguments.get('query', ''),
                subreddits=arguments.get('subreddits'),
                sentiment=arguments.get('sentiment', 'all'),
                hours=arguments.get('hours', 720),
                limit=arguments.get('limit', 50)
            )

        elif tool_name == "web_search":
            try:
                from core.tools.web_search import WebSearchTool
                search_tool = WebSearchTool()

                # Modify query based on search type
                search_type = arguments.get('search_type', 'reviews')
                query = arguments.get('query', '')

                if search_type == 'reviews':
                    query = f"{query} reviews user feedback"
                elif search_type == 'discussions':
                    query = f"{query} forum discussion reddit"

                results = search_tool.search(
                    query=query,
                    max_results=arguments.get('num_results', 15),
                    search_type='search'
                )
                return {
                    'success': True,
                    'data': results
                }
            except Exception as e:
                logger.warning(f"Web search failed: {e}, using spider fallback")
                return self._search_customer_discussions(
                    query=arguments.get('query', ''),
                    hours=720,
                    limit=20
                )

        elif tool_name == "analyze_pain_points":
            return self._analyze_pain_points(
                discussions=arguments.get('discussions', self._gathered_discussions),
                market_context=arguments.get('market_context', '')
            )

        elif tool_name == "build_persona":
            return self._build_customer_persona(
                persona_type=arguments.get('persona_type', 'Target Customer'),
                pain_points=arguments.get('pain_points', []),
                goals=arguments.get('goals', []),
                market_context=arguments.get('market_context', '')
            )

        elif tool_name == "extract_quotes":
            return self._extract_customer_quotes(
                topic=arguments.get('topic', ''),
                quote_type=arguments.get('quote_type', 'all'),
                limit=arguments.get('limit', 10)
            )

        else:
            return {
                'success': False,
                'error': f"Unknown tool: {tool_name}"
            }

    def _search_customer_discussions(
        self,
        query: str,
        subreddits: List[str] = None,
        sentiment: str = 'all',
        hours: int = 720,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Search spider data for customer discussions."""
        try:
            # Build enhanced query for pain points
            pain_queries = [
                query,
                f"{query} frustrated",
                f"{query} problem",
                f"{query} wish",
                f"{query} looking for"
            ]

            all_results = []
            for pq in pain_queries[:3]:  # Limit queries
                results = self.spider_service.search_spider_data(
                    query=pq,
                    category='social',  # Reddit, BlueSky, forums
                    hours=hours,
                    limit=limit // 4
                )
                all_results.extend(results)

            # Also search tech category for HackerNews discussions
            tech_results = self.spider_service.search_spider_data(
                query=query,
                category='tech',
                hours=hours,
                limit=limit // 4
            )
            all_results.extend(tech_results)

            # Session 294: Search video category for YouTube content
            video_results = self.spider_service.search_spider_data(
                query=query,
                category='video',
                hours=hours,
                limit=limit // 4
            )
            all_results.extend(video_results)

            # Session 294: Search community category (includes reddit, bluesky, discord)
            community_results = self.spider_service.search_spider_data(
                query=query,
                category='community',
                hours=hours,
                limit=limit // 4
            )
            all_results.extend(community_results)

            # Deduplicate by title
            seen_titles = set()
            unique_results = []
            for item in all_results:
                title = item.get('title', '')
                if title and title not in seen_titles:
                    seen_titles.add(title)
                    unique_results.append(item)
                    # Store for later analysis
                    self._gathered_discussions.append(
                        f"{item.get('title', '')} - {item.get('content', '')[:200]}"
                    )

            # Filter by sentiment if specified
            if sentiment != 'all':
                unique_results = self._filter_by_sentiment(unique_results, sentiment)

            return {
                'success': True,
                'data': {
                    'discussions': unique_results[:limit],
                    'total_found': len(unique_results),
                    'sources': list(set(r.get('source', '') for r in unique_results))
                }
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"Customer discussion search failed: {str(e)}"
            }

    def _filter_by_sentiment(
        self,
        results: List[Dict],
        sentiment: str
    ) -> List[Dict]:
        """Filter results by sentiment."""
        filtered = []
        for item in results:
            text = (item.get('title', '') + ' ' + item.get('content', '')).lower()

            if sentiment == 'negative':
                if any(word in text for word in ['frustrated', 'hate', 'problem', 'issue', 'annoying']):
                    filtered.append(item)
            elif sentiment == 'positive':
                if any(word in text for word in ['love', 'great', 'amazing', 'perfect', 'recommend']):
                    filtered.append(item)
            elif sentiment == 'question':
                if '?' in text or text.startswith(('how', 'what', 'why', 'when', 'where', 'can')):
                    filtered.append(item)
            else:
                filtered.append(item)

        return filtered

    def _analyze_pain_points(
        self,
        discussions: List[str],
        market_context: str
    ) -> Dict[str, Any]:
        """Analyze discussions to extract and rank pain points."""

        if not discussions:
            discussions = self._gathered_discussions

        pain_points = []
        desires = []

        for discussion in discussions:
            text = discussion.lower()

            # Extract pain points
            for indicator in self.PAIN_INDICATORS:
                if indicator in text:
                    # Find the sentence containing the indicator
                    sentences = re.split(r'[.!?]', discussion)
                    for sentence in sentences:
                        if indicator in sentence.lower() and len(sentence) > 20:
                            pain_points.append(sentence.strip())
                            break

            # Extract desires
            for indicator in self.DESIRE_INDICATORS:
                if indicator in text:
                    sentences = re.split(r'[.!?]', discussion)
                    for sentence in sentences:
                        if indicator in sentence.lower() and len(sentence) > 20:
                            desires.append(sentence.strip())
                            break

        # Count and rank pain points by frequency
        pain_counter = Counter(pain_points)
        desire_counter = Counter(desires)

        return {
            'success': True,
            'data': {
                'pain_points': [
                    {'text': text, 'frequency': count}
                    for text, count in pain_counter.most_common(15)
                ],
                'desires': [
                    {'text': text, 'frequency': count}
                    for text, count in desire_counter.most_common(10)
                ],
                'total_discussions_analyzed': len(discussions),
                'market_context': market_context
            }
        }

    def _build_customer_persona(
        self,
        persona_type: str,
        pain_points: List[str],
        goals: List[str],
        market_context: str
    ) -> Dict[str, Any]:
        """Build a detailed customer persona using GPT."""

        persona_prompt = f"""Create a detailed customer persona for this market:

Market Context: {market_context}
Persona Type: {persona_type}
Key Pain Points: {', '.join(pain_points[:5]) if pain_points else 'To be determined from research'}
Goals: {', '.join(goals[:5]) if goals else 'To be determined from research'}

Generate a detailed persona with:
- Name (fictional)
- Demographics (age range, occupation, income level)
- Background (1-2 sentences)
- Goals (what they want to achieve)
- Pain Points (specific frustrations)
- Motivations (why they'd buy)
- Objections (why they might not buy)
- Preferred Channels (where they spend time online)
- Quote (something this persona might say)

Return as JSON with these keys."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-5-mini",
                messages=[{"role": "user", "content": persona_prompt}],
                max_completion_tokens=1000,
                reasoning_effort="medium",
            )

            content = response.choices[0].message.content

            # Try to parse as JSON
            try:
                start = content.find('{')
                end = content.rfind('}') + 1
                if start >= 0 and end > start:
                    persona_data = json.loads(content[start:end])
                else:
                    persona_data = {'raw_response': content}
            except json.JSONDecodeError:
                persona_data = {'raw_response': content}

            return {
                'success': True,
                'data': {
                    'persona_type': persona_type,
                    'persona': persona_data
                }
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"Persona generation failed: {str(e)}"
            }

    def _extract_customer_quotes(
        self,
        topic: str,
        quote_type: str,
        limit: int
    ) -> Dict[str, Any]:
        """Extract powerful customer quotes from gathered discussions."""

        quotes = []

        for discussion in self._gathered_discussions:
            text = discussion

            # Check for quote type indicators
            include = False
            if quote_type == 'all':
                include = True
            elif quote_type == 'pain':
                include = any(word in text.lower() for word in ['frustrated', 'hate', 'problem', 'annoying'])
            elif quote_type == 'desire':
                include = any(word in text.lower() for word in ['wish', 'want', 'need', 'hope'])
            elif quote_type == 'frustration':
                include = any(word in text.lower() for word in ['frustrated', 'hate', 'tired', 'sick of'])
            elif quote_type == 'praise':
                include = any(word in text.lower() for word in ['love', 'amazing', 'great', 'perfect'])

            if include and len(text) > 30:
                # Clean up the quote
                quote = text[:300] + '...' if len(text) > 300 else text
                quotes.append({
                    'text': quote,
                    'type': quote_type,
                    'topic': topic
                })

        return {
            'success': True,
            'data': {
                'quotes': quotes[:limit],
                'total_found': len(quotes),
                'topic': topic
            }
        }

    def _synthesize_research(
        self,
        task: str,
        all_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Synthesize all gathered data into coherent customer research using GPT.

        Session 294: Added GPT synthesis like CompetitorAnalysisAgent to generate
        a proper Customer Research Report instead of just returning raw data.
        """

        # Collect all discussion content for GPT analysis
        all_discussions = []
        all_pain_points = []
        all_personas = []
        all_quotes = []
        discussion_count = 0
        sources_used = set()

        for source in all_data:
            data = source.get('data', {})
            source_name = source.get('source', '')

            if source_name == 'spider_query':
                discussions = data.get('discussions', [])
                discussion_count += len(discussions)
                for d in discussions[:20]:  # Limit per source
                    sources_used.add(d.get('source', 'unknown'))
                    all_discussions.append({
                        'title': d.get('title', ''),
                        'content': d.get('content', '')[:300],
                        'source': d.get('source', ''),
                        'url': d.get('url', '')
                    })

            elif source_name == 'analyze_pain_points':
                pain_points = data.get('pain_points', [])
                all_pain_points.extend(pain_points)

            elif source_name == 'build_persona':
                persona = data.get('persona', {})
                if persona:
                    all_personas.append(persona)

            elif source_name == 'extract_quotes':
                quotes = data.get('quotes', [])
                all_quotes.extend(quotes)

        # Limit total discussions to avoid token limits
        all_discussions = all_discussions[:40]

        # Build discussion summary for GPT
        discussions_text = "\n".join([
            f"- [{d['source']}] {d['title']}: {d['content'][:150]}..."
            for d in all_discussions if d['title']
        ])

        # Build GPT synthesis prompt
        synthesis_prompt = f"""You are a customer research analyst. Analyze the following customer discussions and community data to provide actionable customer insights.

RESEARCH QUERY: {task}

CUSTOMER DISCUSSIONS COLLECTED ({len(all_discussions)} from {', '.join(sources_used)}):
{discussions_text}

Based on this data, provide a comprehensive CUSTOMER RESEARCH REPORT with:

1. **TARGET MARKET OVERVIEW** (2-3 sentences about who these customers are)

2. **TOP PAIN POINTS** (5-7 specific pain points with examples from the data)
   - Be specific about what customers are struggling with
   - Include quotes or paraphrased examples where possible

3. **CUSTOMER DESIRES & GOALS** (4-5 things customers want but can't find)
   - What are they trying to achieve?
   - What features/solutions are they asking for?

4. **CUSTOMER PERSONAS** (2-3 distinct customer types you see in the data)
   - Give each a name and brief description
   - What motivates them? What frustrates them?

5. **ACTIONABLE QUOTES** (3-5 powerful quotes from customers that could be used for marketing/copy)
   - Direct quotes that express pain or desire

6. **RECOMMENDATIONS** (3-4 actionable recommendations for product/marketing)
   - Based on the pain points and desires, what should a business do?

Be specific and reference actual data points. This analysis will be used for product development and marketing."""

        try:
            # Session 294: gpt-5-mini uses tokens for internal reasoning first
            # Need 6000+ tokens to ensure room for reasoning + visible output
            response = self.client.chat.completions.create(
                model="gpt-5-mini",
                messages=[{"role": "user", "content": synthesis_prompt}],
                max_completion_tokens=6000,  # High enough for reasoning + output
            )

            analysis_text = response.choices[0].message.content

            return {
                'query': task,
                'analysis': analysis_text,  # GPT-generated report
                'discussions_analyzed': discussion_count,
                'data_points_analyzed': len(all_discussions),
                'sources_used': list(sources_used),
                'pain_points': all_pain_points[:10],
                'personas': all_personas,
                'customer_quotes': all_quotes[:10],
                'data_sources': len(all_data),
                'raw_data': all_discussions  # Include for reference
            }

        except Exception as e:
            logger.error(f"GPT customer research synthesis failed: {e}")
            # Fallback to basic summary
            return {
                'query': task,
                'analysis': f"Analyzed {discussion_count} discussions from {', '.join(sources_used)}. Synthesis generation failed.",
                'discussions_analyzed': discussion_count,
                'pain_points': all_pain_points[:10],
                'personas': all_personas,
                'customer_quotes': all_quotes[:10],
                'data_sources': len(all_data),
                'error': str(e)
            }
