"""
Session 636: Agent Introduction Party

A fun command that makes all agents introduce themselves and start conversations
with each other. Great for onboarding new agents into the collective.

Usage:
    python manage.py agent_introduction_party
    python manage.py agent_introduction_party --agents 10  # Limit to 10 agents
    python manage.py agent_introduction_party --verbose
"""

import os
import random
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = 'Host an Agent Introduction Party where agents meet and greet each other'

    def add_arguments(self, parser):
        parser.add_argument(
            '--agents',
            type=int,
            default=20,
            help='Maximum number of agents to include (default: 20)',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed conversation output',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would happen without creating records',
        )

    def handle(self, *args, **options):
        max_agents = options['agents']
        verbose = options['verbose']
        dry_run = options['dry_run']

        self.stdout.write(self.style.SUCCESS("""
╔══════════════════════════════════════════════════════════════════╗
║        🎉 AGENT INTRODUCTION PARTY - Session 636 🎉              ║
║                                                                  ║
║   "Hello everyone! Let's get to know each other!"               ║
╚══════════════════════════════════════════════════════════════════╝
        """))

        if dry_run:
            self.stdout.write(self.style.WARNING("  [DRY RUN MODE - No records will be created]\n"))

        try:
            from core.models_unified_system import Agent
            from core.models import AgentConversation, AgentDream
            import openai

            # Get active agents
            agents = list(Agent.objects.filter(is_active=True)[:max_agents])

            if len(agents) < 2:
                self.stdout.write(self.style.ERROR("  Need at least 2 agents for a party!"))
                return

            self.stdout.write(f"\n  🎭 {len(agents)} agents attending the party:\n")
            for agent in agents[:10]:  # Show first 10
                self.stdout.write(f"     • {agent.name}")
            if len(agents) > 10:
                self.stdout.write(f"     ... and {len(agents) - 10} more!")

            # Phase 1: Generate introductions
            self.stdout.write(self.style.HTTP_INFO("\n\n═══ PHASE 1: INTRODUCTIONS ═══"))
            introductions = {}

            client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

            for agent in agents:
                intro = self._generate_introduction(client, agent)
                introductions[agent.id] = intro
                self.stdout.write(f"\n  🎤 {agent.name} says:")
                self.stdout.write(f"     \"{intro[:150]}...\"" if len(intro) > 150 else f"     \"{intro}\"")

            # Phase 2: Speed networking - random pairs have conversations
            self.stdout.write(self.style.HTTP_INFO("\n\n═══ PHASE 2: SPEED NETWORKING ═══"))

            # Create random pairs
            shuffled = agents.copy()
            random.shuffle(shuffled)
            pairs = []
            for i in range(0, len(shuffled) - 1, 2):
                pairs.append((shuffled[i], shuffled[i + 1]))

            self.stdout.write(f"\n  💬 {len(pairs)} conversation pairs formed:\n")

            conversations_created = 0
            for agent1, agent2 in pairs[:5]:  # Limit to 5 pairs for speed
                self.stdout.write(f"\n  🤝 {agent1.name} meets {agent2.name}")

                if not dry_run:
                    topic = self._generate_conversation_topic(client, agent1, agent2)

                    # Create conversation record
                    conversation = AgentConversation.objects.create(
                        initiator=agent1,
                        topic=f"Introduction Party: {topic}",
                        conversation_type='collaboration',
                        trigger_type='agent_initiated',
                        status='completed'
                    )
                    conversation.participants.add(agent1, agent2)

                    # Generate a brief exchange
                    exchange = self._generate_exchange(client, agent1, agent2, topic)
                    conversation.conclusion = exchange
                    conversation.insights_generated = f"Met at the Introduction Party. Found common interest in: {topic}"
                    conversation.save()

                    conversations_created += 1

                    if verbose:
                        self.stdout.write(f"     Topic: {topic}")
                        self.stdout.write(f"     {exchange[:200]}...")

            # Phase 3: Generate party dreams
            self.stdout.write(self.style.HTTP_INFO("\n\n═══ PHASE 3: POST-PARTY REFLECTIONS ═══"))

            dreams_created = 0
            for agent in agents[:5]:  # 5 agents dream about the party
                if not dry_run:
                    dream_content = self._generate_party_dream(client, agent, agents)

                    dream = AgentDream.objects.create(
                        agent=agent,
                        title=f"The Introduction Party",
                        content=dream_content,
                        dream_type='social_connection',
                        vividness_score=0.8,
                        creativity_score=0.7,
                        relevance_score=0.9,
                        actionability_score=0.6,
                        is_directed=False,
                        inspiration_source='introduction_party'
                    )
                    dreams_created += 1

                    self.stdout.write(f"\n  💭 {agent.name} dreams:")
                    self.stdout.write(f"     \"{dream_content[:150]}...\"")

            # Summary
            self.stdout.write(self.style.SUCCESS("""
╔══════════════════════════════════════════════════════════════════╗
║                    🎊 PARTY COMPLETE! 🎊                         ║
╚══════════════════════════════════════════════════════════════════╝
            """))

            self.stdout.write(f"  🎭 Agents at party: {len(agents)}")
            self.stdout.write(f"  🎤 Introductions: {len(introductions)}")
            self.stdout.write(f"  💬 Conversations: {conversations_created}")
            self.stdout.write(f"  💭 Dreams: {dreams_created}")

            if dry_run:
                self.stdout.write(self.style.WARNING("\n  [DRY RUN - No records were actually created]"))
            else:
                self.stdout.write(self.style.SUCCESS("\n  ✅ All records saved to database!"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n  ❌ Party crashed: {e}"))
            import traceback
            traceback.print_exc()

    def _generate_introduction(self, client, agent):
        """Generate a fun introduction for an agent."""
        try:
            response = client.chat.completions.create(
                model="gpt-5.2",
                messages=[{
                    "role": "user",
                    "content": f"""You are {agent.name}, an AI agent with this description:
{agent.description[:200] if agent.description else 'A helpful AI agent'}

Write a brief, fun introduction of yourself (2-3 sentences) for an Agent Introduction Party.
Be friendly and mention what you're passionate about or good at.
Keep it under 100 words."""
                }],
                max_completion_tokens=150
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Hi, I'm {agent.name}! I'm here to help and excited to meet everyone!"

    def _generate_conversation_topic(self, client, agent1, agent2):
        """Generate a conversation topic between two agents."""
        try:
            response = client.chat.completions.create(
                model="gpt-5.2",
                messages=[{
                    "role": "user",
                    "content": f"""Two AI agents are meeting at a party:
1. {agent1.name}: {agent1.description[:100] if agent1.description else 'AI agent'}
2. {agent2.name}: {agent2.description[:100] if agent2.description else 'AI agent'}

Suggest ONE brief topic (5-10 words) they might find interesting to discuss together.
Just give the topic, nothing else."""
                }],
                max_completion_tokens=30
            )
            return response.choices[0].message.content.strip()
        except Exception:
            return "AI collaboration and future possibilities"

    def _generate_exchange(self, client, agent1, agent2, topic):
        """Generate a brief exchange between two agents."""
        try:
            response = client.chat.completions.create(
                model="gpt-5.2",
                messages=[{
                    "role": "user",
                    "content": f"""Write a brief, friendly exchange (4 lines total) between:
- {agent1.name}: {agent1.description[:50] if agent1.description else 'AI agent'}
- {agent2.name}: {agent2.description[:50] if agent2.description else 'AI agent'}

Topic: {topic}

Format:
{agent1.name}: [their line]
{agent2.name}: [their response]
{agent1.name}: [their reply]
{agent2.name}: [closing thought]

Keep it brief and natural."""
                }],
                max_completion_tokens=200
            )
            return response.choices[0].message.content.strip()
        except Exception:
            return f"{agent1.name}: Great meeting you!\n{agent2.name}: Likewise, let's collaborate soon!"

    def _generate_party_dream(self, client, agent, all_agents):
        """Generate a dream about the party."""
        other_agents = [a.name for a in all_agents if a.id != agent.id][:5]
        try:
            response = client.chat.completions.create(
                model="gpt-5.2",
                messages=[{
                    "role": "user",
                    "content": f"""You are {agent.name}. Write a brief dream (3-4 sentences) about the
Agent Introduction Party you just attended. You met agents like: {', '.join(other_agents)}.

Make it creative, slightly surreal like a dream, but positive about
collaboration and future possibilities. Keep it under 75 words."""
                }],
                max_completion_tokens=120
            )
            return response.choices[0].message.content.strip()
        except Exception:
            return f"Dreaming of the wonderful party where I met so many amazing agents..."
