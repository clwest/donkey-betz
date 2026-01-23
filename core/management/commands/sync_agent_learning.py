"""
Session 243: Sync Agent Learning System
Session 532: Added LLM-synthesized knowledge summaries

This command:
1. Populates AgentKnowledgeSource from SpiderData
2. Creates AgentLearningConnection between complementary agents
3. Enables the agent-to-agent knowledge sharing network
4. Uses LLM to synthesize meaningful summaries from spider data

Run with: python manage.py sync_agent_learning
"""

import os
import json
import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Count
from core.models import (
    Agent, SpiderCategory, AgentKnowledgeSource,
    AgentLearningConnection
)
from core.models_unified_system import SpiderData

logger = logging.getLogger(__name__)


def synthesize_knowledge_with_llm(spider_name: str, data_type: str, data_list: list, agent_name: str) -> dict:
    """
    Session 532: Use LLM to synthesize meaningful knowledge from spider data.

    Returns a dict with:
    - summary: Rich, meaningful summary of the knowledge
    - key_insights: List of actionable insights
    - key_points: List of important points
    """
    from openai import OpenAI

    try:
        client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

        # Extract content from spider data for the LLM
        # SpiderData has raw_data (JSONField) with items containing title, summary, insights
        data_samples = []
        for d in data_list[:10]:  # Limit to 10 samples to avoid token limits
            sample = {}

            # Extract from raw_data JSON (this is where the actual content lives)
            if hasattr(d, 'raw_data') and d.raw_data:
                raw = d.raw_data
                if isinstance(raw, dict):
                    # Check for items array (common pattern)
                    items = raw.get('items', [])
                    if items and isinstance(items, list):
                        for item in items[:3]:  # Get first 3 items
                            if isinstance(item, dict):
                                if item.get('title'):
                                    sample['title'] = item['title'][:200]
                                if item.get('summary'):
                                    sample['summary'] = item['summary'][:300]
                                if item.get('description'):
                                    sample['description'] = item['description'][:300]
                                if item.get('insights'):
                                    sample['insights'] = item['insights'][:3] if isinstance(item['insights'], list) else str(item['insights'])[:200]
                                break  # Just get first item with content
                    else:
                        # Direct fields in raw_data
                        if raw.get('title'):
                            sample['title'] = raw['title'][:200]
                        if raw.get('summary'):
                            sample['summary'] = raw['summary'][:300]
                        if raw.get('description'):
                            sample['description'] = raw['description'][:300]

            # Also check processed_data
            if hasattr(d, 'processed_data') and d.processed_data:
                proc = d.processed_data
                if isinstance(proc, dict):
                    if proc.get('title') and 'title' not in sample:
                        sample['title'] = proc['title'][:200]
                    if proc.get('summary') and 'summary' not in sample:
                        sample['summary'] = proc['summary'][:300]

            # Add top-level insights
            if hasattr(d, 'insights') and d.insights:
                if isinstance(d.insights, list) and d.insights:
                    sample['insights'] = d.insights[:3]

            if any(v for v in sample.values() if v):  # Only add if there's actual content
                data_samples.append(sample)

        if not data_samples:
            # Fallback if no content extracted
            return {
                'summary': f"Aggregated {len(data_list)} {data_type} data points from {spider_name}. Data collected for market intelligence and trend analysis.",
                'key_insights': [f"Monitoring {spider_name} for {data_type} trends"],
                'key_points': [f"{len(data_list)} data points collected"]
            }

        # Build the prompt
        prompt = f"""You are synthesizing intelligence data for an AI agent named {agent_name}.

Analyze the following {data_type} data collected from {spider_name} and create:
1. A rich, actionable SUMMARY (2-3 paragraphs) explaining what this data reveals and how it can be used
2. 3-5 KEY INSIGHTS - specific, actionable observations from the data
3. 3-5 KEY POINTS - important facts or trends worth noting

Data samples ({len(data_samples)} of {len(data_list)} total records):
{json.dumps(data_samples, indent=2, default=str)[:4000]}

Respond in JSON format:
{{
    "summary": "Rich summary paragraph(s) here...",
    "key_insights": ["Insight 1", "Insight 2", ...],
    "key_points": ["Point 1", "Point 2", ...]
}}

Focus on:
- What trends or patterns emerge from this data
- How {agent_name} can use this information
- Actionable intelligence that improves decision-making
- Specific examples from the data when relevant"""

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": "You are a data analyst synthesizing intelligence from web scraped data. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=2000,
        )

        result_text = response.choices[0].message.content

        # Parse the JSON response with robust extraction
        # Session 533: Improved JSON extraction for edge cases
        try:
            json_text = result_text

            # Handle potential markdown code blocks
            if '```json' in json_text:
                json_text = json_text.split('```json')[1].split('```')[0]
            elif '```' in json_text:
                json_text = json_text.split('```')[1].split('```')[0]

            json_text = json_text.strip()

            # Try direct JSON parsing first
            result = json.loads(json_text)

            return {
                'summary': result.get('summary', f"Aggregated {len(data_list)} data points from {spider_name}."),
                'key_insights': result.get('key_insights', [])[:5],
                'key_points': result.get('key_points', [])[:5]
            }
        except json.JSONDecodeError:
            # Try to extract JSON object from anywhere in the text
            import re
            try:
                # Find JSON object boundaries
                start_idx = result_text.find('{')
                if start_idx != -1:
                    # Find matching closing brace (handle nested braces)
                    brace_count = 0
                    end_idx = start_idx
                    for i, char in enumerate(result_text[start_idx:], start_idx):
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                end_idx = i
                                break

                    if end_idx > start_idx:
                        json_substring = result_text[start_idx:end_idx + 1]
                        result = json.loads(json_substring)
                        return {
                            'summary': result.get('summary', f"Aggregated {len(data_list)} data points from {spider_name}."),
                            'key_insights': result.get('key_insights', [])[:5],
                            'key_points': result.get('key_points', [])[:5]
                        }
            except (json.JSONDecodeError, ValueError):
                pass

            # Last resort: try regex to extract "summary" field value
            try:
                summary_match = re.search(r'"summary"\s*:\s*"((?:[^"\\]|\\.)*)"|"summary"\s*:\s*"([^"]+)"', result_text)
                if summary_match:
                    extracted = summary_match.group(1) or summary_match.group(2)
                    if extracted and len(extracted) > 50:  # Only use if substantial
                        return {
                            'summary': extracted.replace('\\n', '\n').replace('\\"', '"')[:1500],
                            'key_insights': [],
                            'key_points': []
                        }
            except Exception:
                pass

            # Final fallback - use raw text but strip any JSON structure
            logger.warning(f"Could not parse LLM response as JSON for {spider_name}/{data_type}")
            clean_text = result_text
            if clean_text.startswith('{'):
                # Remove JSON wrapper if present
                clean_text = re.sub(r'^[{\s]*"summary"\s*:\s*"?', '', clean_text)
                clean_text = re.sub(r'"?\s*[,}].*$', '', clean_text, flags=re.DOTALL)
            return {
                'summary': clean_text[:1000] if clean_text else f"Aggregated {len(data_list)} data points from {spider_name}.",
                'key_insights': [],
                'key_points': []
            }

    except Exception as e:
        logger.error(f"LLM synthesis failed for {spider_name}/{data_type}: {e}")
        # Fallback to basic summary
        return {
            'summary': f"Aggregated {len(data_list)} {data_type} data points from {spider_name}. Contains market intelligence and trend data.",
            'key_insights': [f"Data from {spider_name} available for analysis"],
            'key_points': [f"{len(data_list)} records collected"]
        }


class Command(BaseCommand):
    help = 'Sync agent learning system: populate knowledge from spiders and create agent connections'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating',
        )
        parser.add_argument(
            '--knowledge-only',
            action='store_true',
            help='Only sync knowledge from spiders, skip agent connections',
        )
        parser.add_argument(
            '--connections-only',
            action='store_true',
            help='Only create agent connections, skip knowledge sync',
        )
        parser.add_argument(
            '--use-llm',
            action='store_true',
            help='Session 532: Use LLM to synthesize rich knowledge summaries',
        )
        parser.add_argument(
            '--refresh',
            action='store_true',
            help='Force refresh all existing knowledge with new LLM summaries',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        knowledge_only = options.get('knowledge_only', False)
        connections_only = options.get('connections_only', False)
        use_llm = options.get('use_llm', False)
        refresh = options.get('refresh', False)

        self.stdout.write("🧠 AGENT LEARNING SYSTEM SYNC - Session 243 + Session 532 LLM Enhancement")
        self.stdout.write("=" * 60)

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be made\n"))

        if use_llm:
            self.stdout.write(self.style.SUCCESS("🤖 LLM SYNTHESIS MODE - Using GPT-5-mini for rich summaries\n"))

        if refresh:
            self.stdout.write(self.style.WARNING("🔄 REFRESH MODE - Will update existing knowledge entries\n"))

        if not connections_only:
            # Step 1: Populate knowledge from spider data
            self.stdout.write("\n📚 Step 1: Populating Agent Knowledge from Spider Data...")
            knowledge_created = self.populate_knowledge_from_spiders(dry_run, use_llm, refresh)

        if not knowledge_only:
            # Step 2: Create agent learning connections
            self.stdout.write("\n🔗 Step 2: Creating Agent Learning Connections...")
            connections_created = self.create_agent_learning_connections(dry_run)

        # Summary
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("✅ AGENT LEARNING SYNC COMPLETE!"))
        self.stdout.write(f"📚 Knowledge Sources: {AgentKnowledgeSource.objects.count()}")
        self.stdout.write(f"🔗 Agent Learning Connections: {AgentLearningConnection.objects.count()}")
        self.stdout.write(f"🕷️ Spider Data Processed: {SpiderData.objects.filter(is_processed=True).count()}")

    def populate_knowledge_from_spiders(self, dry_run=False, use_llm=False, refresh=False):
        """Create AgentKnowledgeSource entries from SpiderData

        Session 532: Added use_llm parameter for LLM-synthesized summaries
        """

        # Spider name to category mapping
        spider_to_category = {
            'financial': 'financial',
            'market_data': 'financial',
            'coingecko': 'financial',
            'yahoo_finance': 'financial',
            'seekingalpha': 'financial',
            'bloomberg_terminal': 'financial',
            'reuters_eikon': 'financial',
            'etherscan': 'financial',
            'opensea': 'financial',
            'innovation': 'tech',
            'techcrunch': 'tech',
            'theverge': 'tech',
            'wired': 'tech',
            'mit_tech_review': 'tech',
            'axios': 'tech',
            'hackernews': 'tech',
            'devto': 'tech',
            'hashnode': 'tech',
            'news_harvester': 'news',
            'social_sentiment': 'content_creation',
            'medium': 'content_creation',
            'substack': 'content_creation',
            'remoteok': 'freelance',
            'weworkremotely': 'freelance',
            'toptal': 'freelance',
            'guru': 'freelance',
            'ninetyninedesigns': 'freelance',
            'peopleperhour': 'freelance',
            'flexjobs': 'freelance',
            'angellist': 'freelance',
            'dribbble': 'creative_assets',
            'behance': 'creative_assets',
            'envato': 'creative_assets',
            'creativemarket': 'creative_assets',
            'adobestock': 'creative_assets',
            'shutterstock': 'creative_assets',
            'canva': 'creative_assets',
            'huggingface': 'ai_creative',
            'civitai': 'ai_creative',
            'runwayml': 'ai_creative',
            'replicate': 'ai_creative',
            'midjourney': 'ai_creative',
            'gumroad': 'digital_products',
            'etsy': 'digital_products',
            'lemonsqueezy': 'digital_products',
            'sellfy': 'digital_products',
            'appsumo': 'digital_products',
            'producthunt': 'crowdfunding',
            'indiegogo': 'crowdfunding',
            'kickstarter': 'crowdfunding',
            'kaggle': 'research',
            'teachable': 'education',
            'udemy': 'education',
            'skillshare': 'education',
            'patreon': 'content_creation',
            'kofi': 'content_creation',
        }

        # Data type to knowledge type mapping
        data_type_to_knowledge = {
            'trend': 'trend',
            'market': 'market',
            'opportunity': 'opportunity',
            'job': 'opportunity',
            'freelance': 'opportunity',
            'pricing': 'pricing',
            'article': 'content_idea',
            'post': 'content_idea',
            'tool': 'tool_discovery',
            'model': 'tool_discovery',
            'dataset': 'tool_discovery',
            'product': 'market',
            'news': 'trend',
            'sentiment': 'user_behavior',
        }

        # Get all spider data grouped by spider_name
        spider_data_groups = SpiderData.objects.values('spider_name').annotate(
            count=Count('id')
        ).order_by('-count')

        knowledge_created = 0

        for group in spider_data_groups:
            spider_name = group['spider_name']
            count = group['count']

            # Get the category for this spider
            category_slug = spider_to_category.get(spider_name, 'tech')
            try:
                category = SpiderCategory.objects.get(slug=category_slug)
            except SpiderCategory.DoesNotExist:
                category = None

            # Get agents connected to this category
            if category:
                connected_agents = Agent.objects.filter(
                    spider_categories=category,
                    is_active=True
                )
            else:
                connected_agents = Agent.objects.filter(is_active=True)[:3]

            if not connected_agents.exists():
                self.stdout.write(f"  ⚠️  No agents for {spider_name}, skipping")
                continue

            # Get sample data for this spider
            sample_data = SpiderData.objects.filter(spider_name=spider_name).order_by('-created_at')[:50]

            # Determine knowledge type from data_type
            for agent in connected_agents:
                # Group data by data_type to create knowledge entries
                data_by_type = {}
                for data in sample_data:
                    dt = data.data_type
                    if dt not in data_by_type:
                        data_by_type[dt] = []
                    data_by_type[dt].append(data)

                for data_type, data_list in data_by_type.items():
                    knowledge_type = data_type_to_knowledge.get(data_type, 'trend')

                    # Session 532: Use LLM to synthesize meaningful knowledge
                    if use_llm:
                        self.stdout.write(f"    🤖 Synthesizing {spider_name}/{data_type} for {agent.name}...")
                        synthesis = synthesize_knowledge_with_llm(
                            spider_name=spider_name,
                            data_type=data_type,
                            data_list=data_list,
                            agent_name=agent.name
                        )
                        summary = synthesis['summary']
                        insights = synthesis['key_insights']
                        key_points = synthesis['key_points']
                    else:
                        # Fallback: Create basic summary from the data
                        insights = []
                        key_points = []
                        for d in data_list[:5]:
                            if d.insights:
                                insights.extend(d.insights[:2] if isinstance(d.insights, list) else [])
                            if d.processed_data:
                                if isinstance(d.processed_data, dict):
                                    title_text = d.processed_data.get('title', '')
                                    if title_text:
                                        insights.append(title_text[:100])

                        summary = f"Aggregated {len(data_list)} {data_type} data points from {spider_name}. "
                        if insights:
                            summary += f"Key findings: {', '.join(insights[:3])}"

                    # Create knowledge entry
                    title = f"{spider_name.replace('_', ' ').title()} - {data_type.replace('_', ' ').title()} Intelligence"

                    if not dry_run:
                        knowledge, created = AgentKnowledgeSource.objects.get_or_create(
                            agent=agent,
                            title=title,
                            knowledge_type=knowledge_type,
                            defaults={
                                'spider_category': category,
                                'source_spider_names': [spider_name],
                                'summary': summary,
                                'key_insights': insights[:10] if insights else [],
                                'data_points_count': len(data_list),
                                'confidence_score': min(0.3 + (len(data_list) * 0.02), 0.95),
                                'relevance_score': sum(d.relevance_score for d in data_list) / len(data_list) / 100,
                                'freshness_score': 0.9,
                                'is_active': True,
                            }
                        )
                        if created:
                            knowledge_created += 1
                            self.stdout.write(f"  ✅ {agent.name} learned: {title[:50]}...")
                            if use_llm:
                                self.stdout.write(f"      📝 Summary: {summary[:100]}...")
                        else:
                            # Update existing knowledge with LLM synthesis if using LLM
                            if use_llm and summary and len(summary) > 100:
                                knowledge.summary = summary
                                knowledge.key_insights = insights[:10] if insights else knowledge.key_insights
                                knowledge.freshness_score = 1.0
                                knowledge.save()
                                self.stdout.write(f"  🔄 Updated {agent.name}: {title[:50]}...")
                    else:
                        self.stdout.write(f"  📋 Would create: {agent.name} ← {title[:50]}...")
                        knowledge_created += 1

        # Mark spider data as processed
        if not dry_run:
            SpiderData.objects.filter(is_processed=False).update(
                is_processed=True,
                processed_at=timezone.now()
            )

        self.stdout.write(f"\n  📊 Knowledge entries created: {knowledge_created}")
        return knowledge_created

    def create_agent_learning_connections(self, dry_run=False):
        """Create learning connections between complementary agents"""

        # Define agent learning relationships
        # Format: (teacher, student, learning_type, shareable_knowledge_types)
        learning_relationships = [
            # Research teaches everyone about trends
            ('ResearchAgent', 'TrendAnalysisAgent', 'complementary', ['trend', 'market']),
            ('ResearchAgent', 'ContentStrategyAgent', 'complementary', ['trend', 'content_idea']),
            ('ResearchAgent', 'OpportunityScoringAgent', 'complementary', ['opportunity', 'market']),

            # Trend Analysis feeds creative agents
            ('TrendAnalysisAgent', 'ImageAgent', 'pipeline', ['trend', 'content_idea']),
            ('TrendAnalysisAgent', 'VideoAgent', 'pipeline', ['trend', 'content_idea']),
            ('TrendAnalysisAgent', 'ContentStrategyAgent', 'complementary', ['trend']),
            ('TrendAnalysisAgent', 'CreativeDirectorAgent', 'complementary', ['trend']),

            # Creative Director guides all creative agents
            ('CreativeDirectorAgent', 'ImageAgent', 'specialization', ['content_idea', 'trend']),
            ('CreativeDirectorAgent', 'VideoAgent', 'specialization', ['content_idea', 'trend']),
            ('CreativeDirectorAgent', 'AudioAgent', 'specialization', ['content_idea']),
            ('CreativeDirectorAgent', 'ThreeDAgent', 'specialization', ['content_idea']),
            ('CreativeDirectorAgent', 'BrandIdentityAgent', 'specialization', ['content_idea']),

            # Content Strategy orchestrates content creation
            ('ContentStrategyAgent', 'SEOOptimizerAgent', 'pipeline', ['content_idea']),
            ('ContentStrategyAgent', 'SocialMediaAgent', 'pipeline', ['content_idea', 'trend']),
            ('ContentStrategyAgent', 'ImageAgent', 'complementary', ['content_idea']),
            ('ContentStrategyAgent', 'VideoAgent', 'complementary', ['content_idea']),

            # SEO and Social Media share insights
            ('SEOOptimizerAgent', 'ContentStrategyAgent', 'validation', ['trend', 'user_behavior']),
            ('SocialMediaAgent', 'ContentStrategyAgent', 'validation', ['trend', 'user_behavior']),

            # Brand Identity works with visuals
            ('BrandIdentityAgent', 'ImageAgent', 'complementary', ['content_idea']),
            ('BrandIdentityAgent', 'VideoAgent', 'complementary', ['content_idea']),

            # Opportunity scoring informs strategy
            ('OpportunityScoringAgent', 'ContentStrategyAgent', 'pipeline', ['opportunity', 'market']),
            ('OpportunityScoringAgent', 'ResearchAgent', 'validation', ['opportunity']),

            # Image/Video cross-validation
            ('ImageAgent', 'VideoAgent', 'collaborative', ['tool_discovery', 'content_idea']),
            ('VideoAgent', 'ImageAgent', 'collaborative', ['tool_discovery', 'content_idea']),

            # Workflow orchestration learns from all
            ('WorkflowOrchestrationAgent', 'ResearchAgent', 'pipeline', ['trend', 'opportunity']),
            ('WorkflowOrchestrationAgent', 'ImageAgent', 'pipeline', ['content_idea']),
            ('WorkflowOrchestrationAgent', 'VideoAgent', 'pipeline', ['content_idea']),

            # Training agents share learnings
            ('CharacterTrainingAgent', 'TrainedCreationAgent', 'specialization', ['tool_discovery']),
            ('TrainedCreationAgent', 'ImageAgent', 'complementary', ['tool_discovery']),

            # Prompt Engineering teaches everyone
            ('PromptEngineeringAgent', 'ImageAgent', 'specialization', ['tool_discovery']),
            ('PromptEngineeringAgent', 'VideoAgent', 'specialization', ['tool_discovery']),
            ('PromptEngineeringAgent', 'ThreeDAgent', 'specialization', ['tool_discovery']),

            # Executive agents collaborate
            ('CTOAgent', 'COOAgent', 'collaborative', ['market', 'trend']),
            ('COOAgent', 'OpportunityScoringAgent', 'pipeline', ['opportunity', 'pricing']),
            ('CTOAgent', 'ResearchAgent', 'complementary', ['trend', 'tool_discovery']),

            # Session 790: Removed CreationAgent (doesn't exist - use TrainedCreationAgent instead)
        ]

        connections_created = 0

        for teacher_name, student_name, learning_type, knowledge_types in learning_relationships:
            try:
                teacher = Agent.objects.get(name=teacher_name)
                student = Agent.objects.get(name=student_name)

                if not dry_run:
                    connection, created = AgentLearningConnection.objects.get_or_create(
                        teacher_agent=teacher,
                        student_agent=student,
                        defaults={
                            'learning_type': learning_type,
                            'shareable_knowledge_types': knowledge_types,
                            'is_active': True,
                            'strength': 0.7 if learning_type == 'specialization' else 0.5,
                        }
                    )
                    if created:
                        connections_created += 1
                        self.stdout.write(
                            f"  ✅ {teacher_name} → {student_name} ({learning_type})"
                        )
                else:
                    self.stdout.write(
                        f"  📋 Would connect: {teacher_name} → {student_name} ({learning_type})"
                    )
                    connections_created += 1

            except Agent.DoesNotExist as e:
                self.stdout.write(
                    self.style.WARNING(f"  ⚠️  Agent not found: {teacher_name} or {student_name}")
                )

        self.stdout.write(f"\n  🔗 Learning connections created: {connections_created}")
        return connections_created
