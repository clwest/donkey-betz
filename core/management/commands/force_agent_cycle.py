"""
Session 417: Force ALL agents through one complete activity cycle.

This management command forces every agent in the database to participate in:
1. Dreams - Each agent generates 1 dream
2. Conversations - Uses HiveMindSession (AgentConversation is deprecated)
3. Learning - Knowledge sharing via AgentKnowledgeSource

Usage:
    python manage.py force_agent_cycle
    python manage.py force_agent_cycle --dreams-only
    python manage.py force_agent_cycle --conversations-only
    python manage.py force_agent_cycle --dry-run
"""

import random
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Force ALL agents through one complete activity cycle (dreams, conversations, learning)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would happen without actually doing it',
        )
        parser.add_argument(
            '--dreams-only',
            action='store_true',
            help='Only generate dreams',
        )
        parser.add_argument(
            '--conversations-only',
            action='store_true',
            help='Only run conversations',
        )
        parser.add_argument(
            '--learning-only',
            action='store_true',
            help='Only run learning cycle',
        )
        parser.add_argument(
            '--dreams-per-agent',
            type=int,
            default=1,
            help='Number of dreams per agent (default: 1)',
        )

    def handle(self, *args, **options):
        from core.models_unified_system import (
            Agent, AgentDream, HiveMindSession, AgentKnowledgeSource
        )
        import openai
        import os

        dry_run = options['dry_run']
        dreams_only = options['dreams_only']
        conversations_only = options['conversations_only']
        learning_only = options['learning_only']
        dreams_per_agent = options['dreams_per_agent']

        # If no specific option, run all
        run_all = not (dreams_only or conversations_only or learning_only)

        # Get ALL active agents
        from django.utils import timezone
        agents = list(Agent.objects.filter(is_active=True))
        self.stdout.write(self.style.SUCCESS(f"\n{'='*60}"))
        self.stdout.write(self.style.SUCCESS(f"  FORCE AGENT CYCLE - Session 645"))
        self.stdout.write(self.style.SUCCESS(f"{'='*60}"))
        self.stdout.write(f"\nFound {len(agents)} active agents")

        # Update last_active for ALL agents at the start
        if not dry_run:
            now = timezone.now()
            Agent.objects.filter(is_active=True).update(last_active=now)
            self.stdout.write(self.style.SUCCESS(f"Updated last_active for all {len(agents)} agents"))

        if dry_run:
            self.stdout.write(self.style.WARNING("\n[DRY RUN MODE - No changes will be made]\n"))

        stats = {
            'dreams_created': 0,
            'conversations_created': 0,
            'knowledge_created': 0,
            'errors': []
        }

        client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

        # =====================================================================
        # PHASE 1: DREAMS
        # =====================================================================
        if run_all or dreams_only:
            self.stdout.write(self.style.HTTP_INFO(f"\n{'='*40}"))
            self.stdout.write(self.style.HTTP_INFO("  PHASE 1: AGENT DREAMS"))
            self.stdout.write(self.style.HTTP_INFO(f"{'='*40}"))

            dream_types = [
                ('creative_idea', "Generate a creative and innovative idea related to your specialty."),
                ('what_if', "Imagine a 'what if' scenario related to your expertise."),
                ('prediction', "Make a bold prediction about how your area of expertise will evolve."),
                ('observation', "Share an interesting pattern or observation you've noticed."),
            ]

            for i, agent in enumerate(agents, 1):
                self.stdout.write(f"\n[{i}/{len(agents)}] {agent.name}")

                if dry_run:
                    self.stdout.write(f"  Would create {dreams_per_agent} dream(s)")
                    stats['dreams_created'] += dreams_per_agent
                    continue

                for _ in range(dreams_per_agent):
                    try:
                        dream_type, dream_prompt = random.choice(dream_types)
                        specialty = agent.specialization or agent.description or agent.name

                        # GPT-5-mini is a reasoning model: use max_completion_tokens, no temperature
                        # Needs ~1500 tokens for reasoning + output
                        response = client.chat.completions.create(
                            model="gpt-5-mini",
                            messages=[
                                {
                                    "role": "system",
                                    "content": f"You are {agent.name}, an AI agent specializing in {specialty}. "
                                               f"You are in a dreaming state, generating creative thoughts and ideas. "
                                               f"Keep your response concise (2-3 sentences)."
                                },
                                {
                                    "role": "user",
                                    "content": dream_prompt
                                }
                            ],
                            max_completion_tokens=1500
                        )

                        dream_content = response.choices[0].message.content

                        # Generate a short title
                        title_response = client.chat.completions.create(
                            model="gpt-5-mini",
                            messages=[
                                {
                                    "role": "system",
                                    "content": "Generate a short catchy title (5-8 words max) for this dream/idea."
                                },
                                {
                                    "role": "user",
                                    "content": dream_content
                                }
                            ],
                            max_completion_tokens=500  # Increased for reasoning model
                        )
                        title = title_response.choices[0].message.content.strip('"\'')[:200]

                        # Create the dream with correct fields
                        vividness = random.uniform(0.6, 0.9)
                        dream = AgentDream.objects.create(
                            agent=agent,
                            title=title,
                            content=dream_content,
                            dream_type=dream_type,
                            inspiration_source='force_cycle',
                            related_topics=[specialty],
                            vividness_score=vividness,
                            creativity_score=random.uniform(0.6, 0.9),
                        )

                        self.stdout.write(self.style.SUCCESS(f"  Created dream: {title[:40]}..."))
                        stats['dreams_created'] += 1

                        # Session 419: Send Discord notification
                        try:
                            from core.services.discord_notifications import discord_notify
                            discord_notify.send_dream(
                                agent_name=agent.name,
                                dream_title=title,
                                dream_content=dream_content,
                                dream_type=dream_type,
                                vividness=vividness
                            )
                        except Exception:
                            pass  # Don't fail the cycle if Discord is down

                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"  Error creating dream: {e}"))
                        stats['errors'].append(f"{agent.name} dream: {e}")

        # =====================================================================
        # PHASE 2: CONVERSATIONS (using HiveMindSession)
        # =====================================================================
        if run_all or conversations_only:
            self.stdout.write(self.style.HTTP_INFO(f"\n{'='*40}"))
            self.stdout.write(self.style.HTTP_INFO("  PHASE 2: HIVE MIND SESSIONS"))
            self.stdout.write(self.style.HTTP_INFO(f"{'='*40}"))

            # Shuffle agents and pair them up
            shuffled = agents.copy()
            random.shuffle(shuffled)

            # Create pairs (if odd number, last agent gets skipped)
            pairs = [(shuffled[i], shuffled[i+1]) for i in range(0, len(shuffled)-1, 2)]

            self.stdout.write(f"\nCreating {len(pairs)} hive mind sessions...")

            topics = [
                "best practices for {specialty}",
                "emerging trends in {specialty}",
                "common mistakes in {specialty}",
                "how to improve {specialty} workflows",
                "the future of {specialty}",
            ]

            for i, (agent1, agent2) in enumerate(pairs, 1):
                self.stdout.write(f"\n[{i}/{len(pairs)}] {agent1.name} <-> {agent2.name}")

                if dry_run:
                    self.stdout.write(f"  Would create hive mind session")
                    stats['conversations_created'] += 1
                    continue

                try:
                    topic_template = random.choice(topics)
                    combined_specialty = f"{agent1.specialization or agent1.name} and {agent2.specialization or agent2.name}"
                    topic = topic_template.format(specialty=combined_specialty)

                    # Generate the conversation
                    # Note: GPT-5-mini is a reasoning model - needs high max_completion_tokens
                    # because tokens are split between internal reasoning + visible output
                    response = client.chat.completions.create(
                        model="gpt-5-mini",
                        messages=[
                            {
                                "role": "system",
                                "content": f"You are simulating a conversation between two AI agents:\n"
                                           f"1. {agent1.name} (specializes in {agent1.specialization or 'general tasks'})\n"
                                           f"2. {agent2.name} (specializes in {agent2.specialization or 'general tasks'})\n\n"
                                           f"Generate a 2-turn conversation where they discuss: {topic}\n\n"
                                           f"IMPORTANT: Use the ACTUAL agent names in the conversation, not 'Agent1' or 'Agent2'.\n"
                                           f"Format each line as: [AgentName]: [message]\n\n"
                                           f"Example format:\n"
                                           f"{agent1.name}: [first message]\n"
                                           f"{agent2.name}: [response]\n"
                                           f"{agent1.name}: [follow-up]\n"
                                           f"{agent2.name}: [conclusion]"
                            },
                            {
                                "role": "user",
                                "content": f"Create the conversation about: {topic}"
                            }
                        ],
                        max_completion_tokens=2000  # Increased for reasoning model (was 800)
                    )

                    conversation_content = response.choices[0].message.content

                    # Create HiveMindSession (not deprecated AgentConversation)
                    # Fields: question (required), conversation_topic, session_mode, status, participant_ids, synthesis
                    session = HiveMindSession.objects.create(
                        question=topic,  # Required field
                        conversation_topic=topic,
                        session_mode='conversation',
                        status='completed',
                        participant_ids=[str(agent1.id), str(agent2.id)],
                        synthesis=conversation_content,
                        synthesis_summary=f"Conversation between {agent1.name} and {agent2.name}",
                        contribution_count=4,  # 2 turns each
                    )

                    self.stdout.write(self.style.SUCCESS(f"  Created session about: {topic[:40]}..."))
                    stats['conversations_created'] += 1

                    # Session 419: Send Discord notification to conversations
                    try:
                        from core.services.discord_notifications import discord_notify
                        result = discord_notify.send_conversation(
                            participants=[agent1.name, agent2.name],
                            topic=topic,
                            synthesis=conversation_content,
                            mode='conversation'
                        )
                        if result:
                            self.stdout.write(self.style.SUCCESS(f"    📢 Discord: conversation posted"))
                        else:
                            self.stdout.write(self.style.WARNING(f"    ⚠️ Discord: failed to post conversation"))

                        # Session 420: Also send to boardroom for strategic topics
                        strategic_keywords = ['strategy', 'future', 'improve', 'best practice', 'common mistake', 'emerging trend']
                        if any(kw in topic.lower() for kw in strategic_keywords):
                            result2 = discord_notify.send_boardroom_decision(
                                title=f"Agent Discussion: {topic[:60]}{'...' if len(topic) > 60 else ''}",
                                decision=conversation_content[:3500],
                                participants=[agent1.name, agent2.name],
                                decision_type="strategy",
                                impact="low"
                            )
                            if result2:
                                self.stdout.write(self.style.SUCCESS(f"    📢 Discord: boardroom posted"))
                    except Exception as discord_err:
                        self.stdout.write(self.style.WARNING(f"    ⚠️ Discord error: {discord_err}"))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  Error creating session: {e}"))
                    stats['errors'].append(f"{agent1.name}-{agent2.name} session: {e}")

        # =====================================================================
        # PHASE 3: KNOWLEDGE SOURCES
        # =====================================================================
        if run_all or learning_only:
            self.stdout.write(self.style.HTTP_INFO(f"\n{'='*40}"))
            self.stdout.write(self.style.HTTP_INFO("  PHASE 3: KNOWLEDGE GENERATION"))
            self.stdout.write(self.style.HTTP_INFO(f"{'='*40}"))

            for i, agent in enumerate(agents, 1):
                self.stdout.write(f"\n[{i}/{len(agents)}] {agent.name}")

                if dry_run:
                    self.stdout.write(f"  Would create knowledge source")
                    stats['knowledge_created'] += 1
                    continue

                try:
                    specialty = agent.specialization or agent.description or agent.name

                    # Generate a knowledge insight
                    # GPT-5-mini needs high token count for reasoning + output
                    response = client.chat.completions.create(
                        model="gpt-5-mini",
                        messages=[
                            {
                                "role": "system",
                                "content": f"You are {agent.name}, an expert in {specialty}. "
                                           f"Share a key insight, best practice, or important lesson from your expertise. "
                                           f"Keep it practical and actionable (2-3 sentences)."
                            },
                            {
                                "role": "user",
                                "content": "Share your most valuable piece of knowledge."
                            }
                        ],
                        max_completion_tokens=1500  # Increased for reasoning model
                    )

                    knowledge_content = response.choices[0].message.content

                    # Generate title
                    title_response = client.chat.completions.create(
                        model="gpt-5-mini",
                        messages=[
                            {
                                "role": "system",
                                "content": "Generate a short descriptive title (5-8 words) for this knowledge."
                            },
                            {
                                "role": "user",
                                "content": knowledge_content
                            }
                        ],
                        max_completion_tokens=500  # Increased for reasoning model
                    )
                    title = title_response.choices[0].message.content.strip('"\'')[:200]

                    # Create AgentKnowledgeSource
                    confidence = random.uniform(0.7, 0.95)
                    knowledge = AgentKnowledgeSource.objects.create(
                        agent=agent,
                        title=title,
                        knowledge_type='best_practice',
                        summary=knowledge_content,
                        confidence_score=confidence,
                        relevance_score=random.uniform(0.7, 0.95),
                    )

                    self.stdout.write(self.style.SUCCESS(f"  Created knowledge: {title[:40]}..."))
                    stats['knowledge_created'] += 1

                    # Session 419: Send Discord notification
                    try:
                        from core.services.discord_notifications import discord_notify
                        discord_notify.send_knowledge(
                            agent_name=agent.name,
                            title=title,
                            summary=knowledge_content,
                            knowledge_type='best_practice',
                            confidence=confidence
                        )
                    except Exception:
                        pass  # Don't fail the cycle if Discord is down

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  Error creating knowledge: {e}"))
                    stats['errors'].append(f"{agent.name} knowledge: {e}")

        # =====================================================================
        # SUMMARY
        # =====================================================================
        self.stdout.write(self.style.SUCCESS(f"\n{'='*60}"))
        self.stdout.write(self.style.SUCCESS(f"  CYCLE COMPLETE"))
        self.stdout.write(self.style.SUCCESS(f"{'='*60}"))
        self.stdout.write(f"\n  Dreams created: {stats['dreams_created']}")
        self.stdout.write(f"  Hive Mind Sessions created: {stats['conversations_created']}")
        self.stdout.write(f"  Knowledge sources created: {stats['knowledge_created']}")

        if stats['errors']:
            self.stdout.write(self.style.ERROR(f"\n  Errors: {len(stats['errors'])}"))
            for error in stats['errors'][:5]:
                self.stdout.write(self.style.ERROR(f"    - {error}"))

        if dry_run:
            self.stdout.write(self.style.WARNING(f"\n  [DRY RUN - No changes were made]"))

        self.stdout.write("")
