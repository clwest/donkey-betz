"""
Session 420: Fetch training data from external sources for agent learning.

Usage:
    python manage.py fetch_training_data
    python manage.py fetch_training_data --source huggingface
    python manage.py fetch_training_data --dry-run
    python manage.py fetch_training_data --save-to-db
"""

import asyncio
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Fetch conversation training data from HuggingFace datasets for agent learning'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be fetched without saving',
        )
        parser.add_argument(
            '--source',
            type=str,
            default='huggingface',
            choices=['huggingface', 'all'],
            help='Data source to fetch from (default: huggingface)',
        )
        parser.add_argument(
            '--save-to-db',
            action='store_true',
            help='Save fetched data to SpiderData table',
        )
        parser.add_argument(
            '--create-knowledge',
            action='store_true',
            help='Also create AgentKnowledgeSource entries from high-quality data',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Maximum conversations to fetch per dataset',
        )

    def handle(self, *args, **options):
        from ai_core.spiders.specialized.discord_training_spider import DiscordTrainingSpider

        dry_run = options['dry_run']
        save_to_db = options['save_to_db']
        create_knowledge = options['create_knowledge']

        self.stdout.write(self.style.SUCCESS(f"\n{'='*60}"))
        self.stdout.write(self.style.SUCCESS("  TRAINING DATA FETCH - Session 420"))
        self.stdout.write(self.style.SUCCESS(f"{'='*60}"))

        if dry_run:
            self.stdout.write(self.style.WARNING("\n[DRY RUN MODE - No data will be saved]\n"))

        # Initialize spider
        spider = DiscordTrainingSpider()

        self.stdout.write(f"\nSource: HuggingFace Datasets")
        self.stdout.write(f"Datasets to query: {list(spider.HUGGINGFACE_DATASETS.keys())}\n")

        # Run async fetch
        result = asyncio.run(self._fetch_data(spider))

        if not result:
            self.stdout.write(self.style.ERROR("No data fetched"))
            return

        # Display results
        content = result.content
        stats = content.get('statistics', {})

        self.stdout.write(self.style.HTTP_INFO(f"\n{'='*40}"))
        self.stdout.write(self.style.HTTP_INFO("  FETCH RESULTS"))
        self.stdout.write(self.style.HTTP_INFO(f"{'='*40}"))

        self.stdout.write(f"\n  Total conversations: {stats.get('total_conversations', 0)}")
        self.stdout.write(f"  High quality: {stats.get('high_quality_count', 0)}")
        self.stdout.write(f"  Medium quality: {stats.get('medium_quality_count', 0)}")
        self.stdout.write(f"  Average quality score: {stats.get('avg_quality_score', 0):.2f}")
        self.stdout.write(f"  Topics found: {', '.join(stats.get('topics_found', []))}")

        # Show sample conversations
        high_quality = content.get('high_quality_conversations', [])
        if high_quality:
            self.stdout.write(self.style.HTTP_INFO(f"\n{'='*40}"))
            self.stdout.write(self.style.HTTP_INFO("  SAMPLE HIGH-QUALITY CONVERSATIONS"))
            self.stdout.write(self.style.HTTP_INFO(f"{'='*40}"))

            for i, conv in enumerate(high_quality[:3], 1):
                self.stdout.write(f"\n[{i}] Quality: {conv.get('quality_score', 0):.2f}")
                self.stdout.write(f"    Topics: {', '.join(conv.get('topics', []))}")
                self.stdout.write(f"    Source: {conv.get('source_dataset', 'unknown')}")
                messages = conv.get('messages', [])
                if messages:
                    first_msg = messages[0]
                    content_text = first_msg.get('content', str(first_msg)) if isinstance(first_msg, dict) else str(first_msg)
                    self.stdout.write(f"    Preview: {content_text[:100]}...")

        if dry_run:
            self.stdout.write(self.style.WARNING(f"\n[DRY RUN - No data saved]"))
            return

        # Save to database if requested
        if save_to_db:
            self._save_to_spider_data(result, content)

        if create_knowledge:
            self._create_knowledge_sources(content)

        self.stdout.write(self.style.SUCCESS(f"\n{'='*60}"))
        self.stdout.write(self.style.SUCCESS("  FETCH COMPLETE"))
        self.stdout.write(self.style.SUCCESS(f"{'='*60}\n"))

    async def _fetch_data(self, spider):
        """Run the spider fetch"""
        from ai_core.spiders.base_spider import SpiderTarget

        target = SpiderTarget(
            url='https://huggingface.co/datasets',
        )

        self.stdout.write("Fetching from HuggingFace datasets...")

        try:
            raw_data = await spider.fetch_data(target)
            if raw_data:
                self.stdout.write(self.style.SUCCESS(f"  Fetched {len(raw_data.get('conversations', []))} conversations"))
                result = await spider.process_data(raw_data, target)
                return result
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  Error: {e}"))

        return None

    def _save_to_spider_data(self, result, content):
        """Save fetched data to SpiderData table"""
        from core.models_unified_system import SpiderData

        self.stdout.write("\nSaving to SpiderData...")

        high_quality = content.get('high_quality_conversations', [])
        saved = 0

        for conv in high_quality[:50]:  # Limit to 50 records
            try:
                messages = conv.get('messages', [])
                if not messages:
                    continue

                # Create a summary from the conversation
                first_msg = messages[0]
                summary = first_msg.get('content', str(first_msg)) if isinstance(first_msg, dict) else str(first_msg)

                # SpiderData model fields: spider_name, source_url, data_type, raw_data, processed_data, relevance_score, insights
                SpiderData.objects.create(
                    spider_name='discord_training',
                    source_url=f"https://huggingface.co/datasets/{conv.get('source_dataset', '')}",
                    data_type='training_data',
                    raw_data=conv,  # Store entire conversation as raw_data (JSONField)
                    processed_data={
                        'summary': summary[:500],
                        'message_count': len(messages),
                        'topics': conv.get('topics', []),
                        'quality_score': conv.get('quality_score', 0.5),
                    },
                    relevance_score=int(conv.get('quality_score', 0.5) * 100),  # Convert to 0-100
                    insights=conv.get('topics', []),
                )
                saved += 1
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"  Error saving: {e}"))

        self.stdout.write(self.style.SUCCESS(f"  Saved {saved} records to SpiderData"))

    def _create_knowledge_sources(self, content):
        """Create AgentKnowledgeSource entries from high-quality data"""
        from core.models_unified_system import AgentKnowledgeSource, Agent
        import random

        self.stdout.write("\nCreating knowledge sources...")

        # Get agents that can learn from this data
        learning_agents = Agent.objects.filter(
            is_active=True,
            name__in=[
                'ThinkingAgent',
                'ContentStrategyAgent',
                'CreativeDirectorAgent',
                'ResearchAgent',
            ]
        )

        if not learning_agents:
            self.stdout.write(self.style.WARNING("  No target agents found"))
            return

        high_quality = content.get('high_quality_conversations', [])
        created = 0

        for conv in high_quality[:20]:  # Create max 20 knowledge entries
            try:
                messages = conv.get('messages', [])
                if len(messages) < 2:
                    continue

                # Extract the Q&A pattern
                question = messages[0]
                answer = messages[-1]

                q_text = question.get('content', str(question)) if isinstance(question, dict) else str(question)
                a_text = answer.get('content', str(answer)) if isinstance(answer, dict) else str(answer)

                # Assign to a random appropriate agent
                agent = random.choice(list(learning_agents))

                AgentKnowledgeSource.objects.create(
                    agent=agent,
                    title=f"Conversation Pattern: {q_text[:50]}...",
                    knowledge_type='conversation_pattern',
                    summary=f"Q: {q_text[:200]}\n\nA: {a_text[:300]}",
                    confidence_score=conv.get('quality_score', 0.7),
                    relevance_score=0.8,
                )
                created += 1

            except Exception as e:
                self.stdout.write(self.style.WARNING(f"  Error creating knowledge: {e}"))

        self.stdout.write(self.style.SUCCESS(f"  Created {created} knowledge sources"))
