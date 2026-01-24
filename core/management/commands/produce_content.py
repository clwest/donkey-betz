"""
Produce Content Command
=======================

Session 812: Management command to trigger content production via the orchestrator.

Usage:
    # Produce a blog post (full team)
    python manage.py produce_content blog_post "AI trends for 2026"

    # Produce a podcast episode
    python manage.py produce_content podcast "The future of automation"

    # Skip certain assets
    python manage.py produce_content blog_post "Topic" --skip research social_posts

    # Run asynchronously via Celery
    python manage.py produce_content blog_post "Topic" --async

    # List available content types and their teams
    python manage.py produce_content --list
"""

import json
from django.core.management.base import BaseCommand, CommandError

from core.services.content_production_orchestrator import (
    ContentProductionOrchestrator,
    PRODUCTION_TEAMS,
    ContentType,
    AssetStatus,
)


class Command(BaseCommand):
    help = 'Produce complete content packages with automatic asset creation'

    def add_arguments(self, parser):
        parser.add_argument(
            'content_type',
            nargs='?',
            type=str,
            help='Type of content: blog_post, podcast, video, newsletter, social_campaign'
        )
        parser.add_argument(
            'topic',
            nargs='?',
            type=str,
            help='Main topic for the content'
        )
        parser.add_argument(
            '--tone',
            type=str,
            default='professional',
            help='Content tone: professional, conversational, educational, entertaining'
        )
        parser.add_argument(
            '--audience',
            type=str,
            default='general audience',
            help='Target audience for the content'
        )
        parser.add_argument(
            '--skip',
            nargs='+',
            type=str,
            default=[],
            help='Asset types to skip (e.g., --skip research social_posts)'
        )
        parser.add_argument(
            '--async',
            action='store_true',
            dest='async_mode',
            help='Queue production as Celery task instead of running synchronously'
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='List available content types and their production teams'
        )
        parser.add_argument(
            '--json',
            action='store_true',
            help='Output results as JSON'
        )

    def handle(self, *args, **options):
        # List mode
        if options['list']:
            self._list_teams(options)
            return

        # Validate inputs
        if not options['content_type']:
            raise CommandError('Please specify a content_type or use --list to see available options')

        if not options['topic']:
            raise CommandError('Please specify a topic for the content')

        content_type = options['content_type']
        topic = options['topic']
        tone = options['tone']
        audience = options['audience']
        skip_assets = options['skip']
        async_mode = options['async_mode']
        json_output = options['json']

        # Validate content type
        valid_types = [ct.value for ct in ContentType]
        if content_type not in valid_types:
            raise CommandError(
                f"Unknown content type: {content_type}. "
                f"Available: {', '.join(valid_types)}"
            )

        self.stdout.write(f"\n🎬 Starting Content Production")
        self.stdout.write(f"   Type: {content_type}")
        self.stdout.write(f"   Topic: {topic}")
        self.stdout.write(f"   Tone: {tone}")
        self.stdout.write(f"   Audience: {audience}")
        if skip_assets:
            self.stdout.write(f"   Skipping: {', '.join(skip_assets)}")
        self.stdout.write("")

        # Initialize orchestrator
        orchestrator = ContentProductionOrchestrator(user=None)

        # Execute production
        result = orchestrator.produce_content(
            content_type=content_type,
            topic=topic,
            context={
                'tone': tone,
                'target_audience': audience,
            },
            skip_assets=skip_assets,
            async_mode=async_mode
        )

        if json_output:
            self.stdout.write(json.dumps(result.to_dict(), indent=2, default=str))
            return

        # Display results
        self.stdout.write("")
        if result.status == 'completed':
            self.stdout.write(self.style.SUCCESS(f"✅ Production COMPLETED: {result.production_id}"))
        elif result.status == 'partial':
            self.stdout.write(self.style.WARNING(f"⚠️  Production PARTIAL: {result.production_id}"))
        elif result.status == 'queued':
            self.stdout.write(self.style.SUCCESS(f"📋 Production QUEUED: {result.production_id}"))
            self.stdout.write(f"   Check Celery logs for progress")
            return
        else:
            self.stdout.write(self.style.ERROR(f"❌ Production FAILED: {result.production_id}"))

        # Show asset results
        self.stdout.write(f"\n📦 Assets ({len(result.assets)}):")
        for asset_type, asset in result.assets.items():
            status_icon = {
                AssetStatus.COMPLETED: '✅',
                AssetStatus.FAILED: '❌',
                AssetStatus.SKIPPED: '⏭️',
                AssetStatus.PENDING: '⏳',
                AssetStatus.IN_PROGRESS: '🔄',
            }.get(asset.status, '❓')

            self.stdout.write(
                f"   {status_icon} {asset_type} ({asset.agent_name})"
                f" - {asset.execution_time_ms}ms"
            )
            if asset.error:
                self.stdout.write(f"      Error: {asset.error}")

        # Show errors
        if result.errors:
            self.stdout.write(f"\n⚠️  Errors:")
            for error in result.errors:
                self.stdout.write(f"   - {error}")

        # Show timing
        self.stdout.write(f"\n⏱️  Total Time: {result.total_execution_time_ms}ms")

        # Show content preview if blog was created
        if 'blog_content' in result.assets:
            blog_asset = result.assets['blog_content']
            if blog_asset.status == AssetStatus.COMPLETED and blog_asset.data:
                content = blog_asset.data.get('content', {})
                title = content.get('title', 'Untitled')
                self.stdout.write(f"\n📝 Blog Title: {title}")

                if content.get('sections'):
                    self.stdout.write("   Sections:")
                    for section in content['sections'][:5]:
                        if isinstance(section, dict):
                            self.stdout.write(f"      - {section.get('header', 'Section')}")

    def _list_teams(self, options):
        """List available content types and their production teams."""
        json_output = options['json']

        if json_output:
            teams_data = ContentProductionOrchestrator.get_available_teams()
            self.stdout.write(json.dumps(teams_data, indent=2))
            return

        self.stdout.write("\n📋 Available Content Production Teams\n")

        for content_type in ContentType:
            team = PRODUCTION_TEAMS.get(content_type)
            if not team:
                continue

            self.stdout.write(self.style.SUCCESS(f"\n{content_type.value}"))
            self.stdout.write(f"   {team['name']}")
            self.stdout.write(f"   {team['description']}")
            self.stdout.write(f"\n   Assets ({len(team['assets'])}):")

            for asset in team['assets']:
                optional_marker = " (optional)" if asset.optional else " (required)"
                depends = f" [depends on: {', '.join(asset.depends_on)}]" if asset.depends_on else ""
                self.stdout.write(
                    f"      • {asset.asset_type} → {asset.agent_name}{optional_marker}{depends}"
                )

        self.stdout.write("\n")
