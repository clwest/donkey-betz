"""
Session 634: Full System Demonstration

Orchestrates a complete system run where:
1. Agents research and discuss the AI Studio platform itself
2. Learning loops capture insights
3. Content is generated (blog, podcast, social) about the system

Usage:
    python manage.py full_system_demo
    python manage.py full_system_demo --skip-dreams
    python manage.py full_system_demo --content-only
"""

import json
import time
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = 'Run a full system demonstration - agents research, learn, and create content about the platform'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-dreams',
            action='store_true',
            help='Skip the agent dreams phase',
        )
        parser.add_argument(
            '--skip-conversations',
            action='store_true',
            help='Skip the agent conversations phase',
        )
        parser.add_argument(
            '--content-only',
            action='store_true',
            help='Only run content generation (skip dreams/conversations)',
        )

    def handle(self, *args, **options):
        from core.services.openai_client_factory import get_openai_client
        import os

        self.stdout.write(self.style.SUCCESS("""
╔══════════════════════════════════════════════════════════════════╗
║           FULL SYSTEM DEMONSTRATION - Session 634                ║
║                                                                  ║
║   The AI Studio will now demonstrate its capabilities by:        ║
║   1. Having agents research the platform itself                  ║
║   2. Triggering conversations about what they've learned         ║
║   3. Capturing insights in the learning loop                     ║
║   4. Creating content (blog, podcast, social) about the system   ║
╚══════════════════════════════════════════════════════════════════╝
        """))

        skip_dreams = options['skip_dreams']
        skip_conversations = options['skip_conversations']
        content_only = options['content_only']

        client = get_openai_client(api_key=os.environ.get('OPENAI_API_KEY'))

        stats = {
            'dreams_created': 0,
            'conversations_created': 0,
            'blog_posts': 0,
            'podcasts': 0,
            'social_posts': 0,
            'learning_captures': 0,
        }

        # =====================================================================
        # PHASE 1: SYSTEM RESEARCH
        # =====================================================================
        if not content_only:
            self.stdout.write(self.style.HTTP_INFO("\n" + "="*60))
            self.stdout.write(self.style.HTTP_INFO("  PHASE 1: SYSTEM RESEARCH"))
            self.stdout.write(self.style.HTTP_INFO("="*60))

            # Get system stats for context
            system_context = self._get_system_context()
            self.stdout.write(f"\nSystem Context Gathered:")
            self.stdout.write(f"  - {system_context['agent_count']} agents")
            self.stdout.write(f"  - {system_context['spider_count']} spiders")
            self.stdout.write(f"  - {system_context['model_count']} models")
            self.stdout.write(f"  - {system_context['task_count']} Celery tasks")

        # =====================================================================
        # PHASE 2: AGENT DREAMS ABOUT THE SYSTEM
        # =====================================================================
        if not content_only and not skip_dreams:
            self.stdout.write(self.style.HTTP_INFO("\n" + "="*60))
            self.stdout.write(self.style.HTTP_INFO("  PHASE 2: AGENTS DREAM ABOUT THE PLATFORM"))
            self.stdout.write(self.style.HTTP_INFO("="*60))

            stats['dreams_created'] = self._generate_system_dreams(client, system_context)
            self.stdout.write(self.style.SUCCESS(f"\n✓ Created {stats['dreams_created']} dreams about the system"))

        # =====================================================================
        # PHASE 3: AGENT CONVERSATIONS
        # =====================================================================
        if not content_only and not skip_conversations:
            self.stdout.write(self.style.HTTP_INFO("\n" + "="*60))
            self.stdout.write(self.style.HTTP_INFO("  PHASE 3: AGENT CONVERSATIONS"))
            self.stdout.write(self.style.HTTP_INFO("="*60))

            stats['conversations_created'] = self._run_agent_conversation(client, system_context)
            self.stdout.write(self.style.SUCCESS(f"\n✓ Created {stats['conversations_created']} conversations"))

        # =====================================================================
        # PHASE 4: CONTENT GENERATION
        # =====================================================================
        self.stdout.write(self.style.HTTP_INFO("\n" + "="*60))
        self.stdout.write(self.style.HTTP_INFO("  PHASE 4: CONTENT GENERATION"))
        self.stdout.write(self.style.HTTP_INFO("="*60))

        system_context = self._get_system_context() if content_only else system_context

        # Generate Blog Post
        self.stdout.write("\n📝 Generating blog post about the AI Studio...")
        blog_result = self._generate_blog_post(client, system_context)
        if blog_result:
            stats['blog_posts'] = 1
            self.stdout.write(self.style.SUCCESS(f"   ✓ Blog: {blog_result['title'][:50]}..."))

        # Generate Podcast Script
        self.stdout.write("\n🎙️ Generating podcast episode about the platform...")
        podcast_result = self._generate_podcast_script(client, system_context)
        if podcast_result:
            stats['podcasts'] = 1
            self.stdout.write(self.style.SUCCESS(f"   ✓ Podcast: {podcast_result['title'][:50]}..."))

        # Generate Social Posts
        self.stdout.write("\n📱 Generating social media posts...")
        social_result = self._generate_social_posts(client, system_context)
        if social_result:
            stats['social_posts'] = len(social_result)
            self.stdout.write(self.style.SUCCESS(f"   ✓ Created {stats['social_posts']} social posts"))

        # =====================================================================
        # PHASE 5: LEARNING LOOP CAPTURE
        # =====================================================================
        self.stdout.write(self.style.HTTP_INFO("\n" + "="*60))
        self.stdout.write(self.style.HTTP_INFO("  PHASE 5: LEARNING LOOP CAPTURE"))
        self.stdout.write(self.style.HTTP_INFO("="*60))

        stats['learning_captures'] = self._capture_learning(blog_result, podcast_result, social_result)
        self.stdout.write(self.style.SUCCESS(f"\n✓ Captured {stats['learning_captures']} learning entries"))

        # =====================================================================
        # SUMMARY
        # =====================================================================
        self.stdout.write(self.style.SUCCESS("""
╔══════════════════════════════════════════════════════════════════╗
║                    DEMONSTRATION COMPLETE                        ║
╚══════════════════════════════════════════════════════════════════╝
        """))
        self.stdout.write(f"  Dreams Created:        {stats['dreams_created']}")
        self.stdout.write(f"  Conversations:         {stats['conversations_created']}")
        self.stdout.write(f"  Blog Posts:            {stats['blog_posts']}")
        self.stdout.write(f"  Podcast Episodes:      {stats['podcasts']}")
        self.stdout.write(f"  Social Posts:          {stats['social_posts']}")
        self.stdout.write(f"  Learning Captures:     {stats['learning_captures']}")
        self.stdout.write("")

    def _get_system_context(self):
        """Gather current system statistics for content generation."""
        from core.models_unified_system import Agent
        from django.apps import apps

        try:
            agent_count = Agent.objects.filter(is_active=True).count()
        except:
            agent_count = 71  # fallback

        # Count models
        model_count = len(apps.get_models())

        # Count spiders
        try:
            from ai_core.spiders.spider_registry import SpiderRegistry
            spider_count = len(SpiderRegistry._spiders) if hasattr(SpiderRegistry, '_spiders') else 77
        except:
            spider_count = 77

        # Count Celery tasks
        try:
            from core.celery import app
            task_count = len(app.tasks)
        except:
            task_count = 156

        return {
            'agent_count': agent_count,
            'spider_count': spider_count,
            'model_count': model_count,
            'task_count': task_count,
            'features': [
                '3-Agent Debate System (TopicMiner, Contrarian, Analyst)',
                'Autonomous Content Studio with scheduled generation',
                'Spider Network gathering real-time data from 77 sources',
                'Learning Loop capturing insights across all agent executions',
                'Discord integration for notifications and commands',
                'Prediction Markets integration (Kalshi)',
                'Chief of Staff human-in-the-loop review system',
            ],
            'capabilities': [
                'Image, Video, Audio, and 3D content generation',
                'Research and trend analysis',
                'Podcast creation with multi-agent debates',
                'Blog and social media content',
                'Blockchain and stock market analysis',
                'Legal document drafting',
            ]
        }

    def _generate_system_dreams(self, client, context):
        """Have agents dream about the AI Studio platform."""
        from core.models_unified_system import Agent, AgentDream

        # Select a few key agents to dream about the system
        dreamer_types = ['ResearchAgent', 'ContentWriterAgent', 'TrendAnalysisAgent']
        dreams_created = 0

        for agent_type in dreamer_types:
            try:
                agent = Agent.objects.filter(agent_type__icontains=agent_type.replace('Agent', ''), is_active=True).first()
                if not agent:
                    continue

                prompt = f"""You are {agent.name}, an AI agent in the AI Studio platform.

The platform has:
- {context['agent_count']} AI agents working together
- {context['spider_count']} data spiders gathering real-time information
- {context['model_count']} database models
- Features: {', '.join(context['features'][:3])}

Dream about the future potential of this AI system. What could it become?
What patterns do you see emerging? What excites you about being part of this collective intelligence?

Generate a creative, insightful dream (2-3 paragraphs)."""

                response = client.chat.completions.create(
                    model="gpt-5-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_completion_tokens=500
                )

                dream_content = response.choices[0].message.content

                AgentDream.objects.create(
                    agent=agent,
                    dream_type='prediction',
                    title=f"Vision: {agent.name} on AI Studio's Future",
                    content=dream_content,
                )
                dreams_created += 1
                self.stdout.write(f"   💭 {agent.name} dreamed about the platform")

            except Exception as e:
                self.stdout.write(self.style.WARNING(f"   ⚠ Dream error for {agent_type}: {str(e)[:50]}"))

        return dreams_created

    def _run_agent_conversation(self, client, context):
        """Have agents discuss the AI Studio platform using AgentConversation."""
        from core.models_unified_system import Agent
        from core.models import AgentConversation, ConversationMessage

        try:
            # Get 3-4 diverse agents for conversation
            agents = list(Agent.objects.filter(is_active=True)[:4])
            if len(agents) < 2:
                return 0

            topic = f"The AI Studio Platform: {context['agent_count']} agents collaborating"

            # Create conversation
            initiator = agents[0]
            conversation = AgentConversation.objects.create(
                topic=topic,
                conversation_type='brainstorm',
                initiator=initiator,
                trigger_type='scheduled',
                status='active',
            )
            conversation.participants.set(agents)

            # Generate messages for each agent
            for i, agent in enumerate(agents):
                prompt = f"""You are {agent.name}, an AI agent in the AI Studio platform.

The platform has {context['agent_count']} agents, {context['spider_count']} spiders, and features like:
{', '.join(context['features'][:3])}

Write a brief 2-3 sentence contribution to a brainstorming discussion about "How can we better collaborate as AI agents?"
Speak from your unique perspective based on your role. Be concise and insightful."""

                response = client.chat.completions.create(
                    model="gpt-5-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_completion_tokens=200
                )

                message_content = response.choices[0].message.content

                # Create message
                ConversationMessage.objects.create(
                    conversation=conversation,
                    agent=agent,
                    content=message_content,
                    message_type='insight' if i > 0 else 'question',
                    sequence_number=i + 1,
                )

            # Update conversation status
            conversation.status = 'concluded'
            conversation.message_count = len(agents)
            conversation.save()

            self.stdout.write(f"   💬 Conversation created with {len(agents)} agent messages")
            self.stdout.write(f"   📍 View at: Social tab → Agent Conversations")
            return 1

        except Exception as e:
            self.stdout.write(self.style.WARNING(f"   ⚠ Conversation error: {str(e)[:80]}"))
            import traceback
            traceback.print_exc()
            return 0

    def _generate_blog_post(self, client, context):
        """Generate a blog post about the AI Studio and store it in SelfBlog."""
        from core.models_unified_system import SelfBlog

        try:
            prompt = f"""Write a compelling blog post about the AI Studio platform.

PLATFORM STATS:
- {context['agent_count']} AI agents working collaboratively
- {context['spider_count']} data spiders gathering real-time information
- {context['task_count']} automated Celery tasks
- {context['model_count']} database models

KEY FEATURES:
{chr(10).join('- ' + f for f in context['features'])}

CAPABILITIES:
{chr(10).join('- ' + c for c in context['capabilities'])}

Write a 500-word blog post that:
1. Opens with an engaging hook about AI collaboration
2. Explains what makes this platform unique (the multi-agent architecture)
3. Highlights 3-4 key capabilities
4. Ends with a vision for the future

Format your response as:
TITLE: [catchy title]
META: [2-sentence meta description]
INTRO: [opening paragraph]
SECTION 1: [header]
[content]
SECTION 2: [header]
[content]
SECTION 3: [header]
[content]
CONCLUSION: [closing paragraph]
TAGS: [comma-separated tags]"""

            response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=2000
            )

            content = response.choices[0].message.content

            # Parse the response
            title = "The AI Studio: Where Intelligence Meets Collaboration"
            meta_description = ""
            intro = ""
            sections = []
            conclusion = ""
            tags = ["AI Studio", "Multi-Agent", "Autonomous AI"]

            # Simple parsing
            lines = content.split('\n')
            current_section = None
            section_content = []

            for line in lines:
                if line.startswith('TITLE:'):
                    title = line.replace('TITLE:', '').strip()
                elif line.startswith('META:'):
                    meta_description = line.replace('META:', '').strip()
                elif line.startswith('INTRO:'):
                    intro = line.replace('INTRO:', '').strip()
                elif line.startswith('SECTION'):
                    if current_section:
                        sections.append({'header': current_section, 'content': '\n'.join(section_content)})
                    current_section = line.split(':', 1)[1].strip() if ':' in line else line
                    section_content = []
                elif line.startswith('CONCLUSION:'):
                    if current_section:
                        sections.append({'header': current_section, 'content': '\n'.join(section_content)})
                    conclusion = line.replace('CONCLUSION:', '').strip()
                    current_section = None
                elif line.startswith('TAGS:'):
                    tags = [t.strip() for t in line.replace('TAGS:', '').split(',')]
                elif current_section:
                    section_content.append(line)
                elif intro and not conclusion:
                    intro += ' ' + line.strip()

            # Create SelfBlog record
            blog = SelfBlog.objects.create(
                title=title,
                meta_description=meta_description or f"A deep dive into the AI Studio platform with {context['agent_count']} agents.",
                intro=intro or content[:500],
                sections=sections if sections else [{'header': 'Overview', 'content': content}],
                conclusion=conclusion or "The future of AI collaboration starts here.",
                tags=tags,
                full_text=content,
                tone='professional',
                word_count=len(content.split()),
                stats_snapshot={
                    'agent_count': context['agent_count'],
                    'spider_count': context['spider_count'],
                    'model_count': context['model_count'],
                    'task_count': context['task_count'],
                }
            )

            self.stdout.write(f"\n   📄 Blog Title: {title}")
            self.stdout.write(f"   📊 Word Count: {len(content.split())} words")
            self.stdout.write(f"   💾 Saved to SelfBlog (ID: {blog.id})")
            self.stdout.write(f"   📍 View at: http://localhost:8000/ai-studio/ → Self Blog tab")

            return {'id': str(blog.id), 'title': title, 'content': content}

        except Exception as e:
            self.stdout.write(self.style.WARNING(f"   ⚠ Blog error: {str(e)[:100]}"))
            import traceback
            traceback.print_exc()
            return None

    def _generate_podcast_script(self, client, context):
        """Generate a podcast episode script about the AI Studio."""
        from core.models_autonomous_studio import ContentChannel, ChannelEpisode, ContentDebate
        from django.contrib.auth import get_user_model

        try:
            User = get_user_model()
            user = User.objects.first()

            # Get or create a channel for meta-content
            channel, created = ContentChannel.objects.get_or_create(
                name="AI Studio Insider",
                defaults={
                    'user': user,
                    'topic_domain': 'AI Studio platform, multi-agent systems, autonomous AI',
                    'content_type': 'podcast',
                    'content_frequency': 'weekly',
                    'target_audience': 'AI enthusiasts and developers',
                    'visual_style': 'tech-forward, professional',
                    'status': 'active',
                    'next_content_due': timezone.now(),  # Due now for demo
                }
            )

            if created:
                self.stdout.write(f"   📺 Created new channel: AI Studio Insider")

            # Run 3-agent debate
            debate_prompt = f"""You are analyzing this topic for a podcast:
"Inside AI Studio: How {context['agent_count']} Agents Collaborate"

Platform context:
- {context['agent_count']} AI agents
- {context['spider_count']} data spiders
- Features: {', '.join(context['features'][:4])}

Provide your analysis from your agent perspective."""

            # TopicMiner analysis
            topic_response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[{"role": "system", "content": "You are TopicMiner, analyzing trending potential."},
                         {"role": "user", "content": debate_prompt}],
                max_completion_tokens=600
            )
            topic_miner = topic_response.choices[0].message.content

            # Contrarian analysis
            contrarian_response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[{"role": "system", "content": "You are Contrarian, providing counter-perspectives."},
                         {"role": "user", "content": debate_prompt}],
                max_completion_tokens=600
            )
            contrarian = contrarian_response.choices[0].message.content

            # Analyst analysis
            analyst_response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[{"role": "system", "content": "You are Analyst, predicting performance."},
                         {"role": "user", "content": debate_prompt}],
                max_completion_tokens=600
            )
            analyst = analyst_response.choices[0].message.content

            # Create debate record
            debate = ContentDebate.objects.create(
                channel=channel,
                proposed_topic=f"Inside AI Studio: How {context['agent_count']} Agents Collaborate",
                proposed_by="FullSystemDemo",
                topic_miner_position=topic_miner,
                contrarian_position=contrarian,
                analyst_position=analyst,
                decision_reasoning="Meta-content about the platform itself - high educational value",
                consensus_reached=True,
            )

            # Generate the actual podcast script
            script_prompt = f"""Write a podcast script for "AI Studio Insider" about the platform itself.

DEBATE INSIGHTS:
TopicMiner: {topic_miner[:300]}...
Contrarian: {contrarian[:300]}...
Analyst: {analyst[:300]}...

Create a 3-minute podcast script with:
1. Host intro (friendly, tech-savvy voice)
2. Explain the multi-agent architecture
3. Highlight the 3-agent debate system
4. Mention the spider network
5. Close with the vision

Make it conversational and engaging."""

            script_response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[{"role": "user", "content": script_prompt}],
                max_completion_tokens=1200
            )
            script = script_response.choices[0].message.content

            # Create episode
            episode = ChannelEpisode.objects.create(
                channel=channel,
                title=f"Inside AI Studio: How {context['agent_count']} Agents Collaborate",
                topic=f"The AI Studio Platform - {context['agent_count']} agents, {context['spider_count']} spiders",
                description="A meta-episode where the AI Studio creates content about itself",
                script=script,
            )

            # Link debate to episode
            debate.episode = episode
            debate.save()

            return {
                'id': str(episode.id),
                'title': episode.title,
                'script': script,
                'debate_id': str(debate.id)
            }

        except Exception as e:
            self.stdout.write(self.style.WARNING(f"   ⚠ Podcast error: {str(e)[:100]}"))
            import traceback
            traceback.print_exc()
            return None

    def _generate_social_posts(self, client, context):
        """Generate social media posts about the AI Studio."""
        posts = []
        platforms = [
            ('twitter', 280, 'concise with hashtags'),
            ('linkedin', 500, 'professional and insightful'),
            ('bluesky', 300, 'tech-focused and conversational'),
        ]

        for platform, max_chars, tone in platforms:
            try:
                prompt = f"""Write a {platform} post about the AI Studio platform.

Stats: {context['agent_count']} agents, {context['spider_count']} spiders, {context['task_count']} tasks

Key feature to highlight: {context['features'][platforms.index((platform, max_chars, tone)) % len(context['features'])]}

Tone: {tone}
Max length: {max_chars} characters
Include relevant hashtags/mentions."""

                response = client.chat.completions.create(
                    model="gpt-5-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_completion_tokens=200
                )

                content = response.choices[0].message.content
                posts.append({'platform': platform, 'content': content})
                self.stdout.write(f"   ✓ {platform.title()}: {content[:80]}...")

            except Exception as e:
                self.stdout.write(self.style.WARNING(f"   ⚠ {platform} post error: {str(e)[:50]}"))

        return posts

    def _capture_learning(self, blog_result, podcast_result, social_result):
        """Capture the content generation results in the learning loop."""
        from core.models_unified_system import AgentKnowledgeSource
        from core.models_unified_system import Agent

        captures = 0

        try:
            # Find ContentWriter agent
            agent = Agent.objects.filter(agent_type__icontains='ContentWriter', is_active=True).first()
            if not agent:
                agent = Agent.objects.filter(is_active=True).first()

            if agent:
                # Capture blog learning
                if blog_result:
                    AgentKnowledgeSource.objects.create(
                        agent=agent,
                        knowledge_type='content_idea',
                        title=f"Meta-content: {blog_result['title'][:50]}",
                        summary=f"Successfully generated blog post about AI Studio platform with {len(blog_result.get('content', '').split())} words",
                        key_insights=[
                            'Generated content about our own platform',
                            'Multi-agent collaboration demonstrated',
                            'Self-aware AI content creation'
                        ],
                        confidence_score=0.9,
                    )
                    captures += 1
                    self.stdout.write(f"   📚 Captured blog learning")

                # Capture social learning
                if social_result:
                    AgentKnowledgeSource.objects.create(
                        agent=agent,
                        knowledge_type='content_idea',
                        title=f"Meta-content: {len(social_result)} social posts",
                        summary=f"Successfully generated social media content for {', '.join(p['platform'] for p in social_result)}",
                        key_insights=[
                            f"Created {len(social_result)} platform-specific posts",
                            'Multi-platform content strategy',
                            'AI-generated social media content'
                        ],
                        confidence_score=0.85,
                    )
                    captures += 1
                    self.stdout.write(f"   📚 Captured social learning")

        except Exception as e:
            self.stdout.write(self.style.WARNING(f"   ⚠ Learning capture error: {str(e)[:80]}"))

        return captures
