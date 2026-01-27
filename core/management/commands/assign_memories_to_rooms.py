"""
Session 843: Retroactively assign existing memories to Memory Palace rooms.

All 906 memories in the database were created before auto-assignment was added.
This command assigns them to appropriate rooms based on memory_type.

Usage:
    python manage.py assign_memories_to_rooms
    python manage.py assign_memories_to_rooms --dry-run
"""
from django.core.management.base import BaseCommand
from django.db.models import Count


class Command(BaseCommand):
    help = 'Assign unassigned memories to Memory Palace rooms based on memory_type'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be assigned without making changes',
        )
        parser.add_argument(
            '--agent',
            type=str,
            help='Only process memories for a specific agent (by name)',
        )

    def handle(self, *args, **options):
        from core.models_unified_system import AgentMemory, MemoryPalaceRoom

        dry_run = options['dry_run']
        agent_filter = options.get('agent')

        # Memory type to room type mapping
        MEMORY_TO_ROOM = {
            'success': 'successes',
            'failure': 'lessons',
            'technique': 'techniques',
            'insight': 'insights',
            'conceptual': 'insights',
            'preference': 'preferences',
            'interaction': 'general',
            'feedback': 'general',
        }

        # Room type metadata
        ROOM_META = {
            'techniques': {'name': 'Techniques Library', 'icon': '📚', 'color': '#06b6d4'},
            'successes': {'name': 'Hall of Victories', 'icon': '🏆', 'color': '#22c55e'},
            'lessons': {'name': 'Lessons Learned', 'icon': '📖', 'color': '#f97316'},
            'preferences': {'name': 'User Preferences', 'icon': '⭐', 'color': '#eab308'},
            'insights': {'name': 'Insight Garden', 'icon': '💡', 'color': '#8b5cf6'},
            'experiments': {'name': 'Experiment Lab', 'icon': '🧪', 'color': '#ec4899'},
            'general': {'name': 'General Archive', 'icon': '🏠', 'color': '#6366f1'},
        }

        # Get memories without room assignments
        unassigned = AgentMemory.objects.filter(rooms__isnull=True)
        if agent_filter:
            unassigned = unassigned.filter(agent__name__icontains=agent_filter)

        total = unassigned.count()
        self.stdout.write(f"\n{'[DRY RUN] ' if dry_run else ''}Found {total} unassigned memories\n")

        if total == 0:
            self.stdout.write(self.style.SUCCESS("All memories are already assigned to rooms!"))
            return

        # Group by agent for efficiency
        agent_memories = unassigned.values('agent', 'agent__name').annotate(
            count=Count('id')
        ).order_by('-count')

        self.stdout.write(f"Agents with unassigned memories:")
        for am in agent_memories:
            self.stdout.write(f"  - {am['agent__name']}: {am['count']}")

        if dry_run:
            self.stdout.write("\n[DRY RUN] Would assign memories by type:")
            type_counts = unassigned.values('memory_type').annotate(count=Count('id'))
            for tc in type_counts:
                room_type = MEMORY_TO_ROOM.get(tc['memory_type'], 'general')
                self.stdout.write(f"  - {tc['memory_type']} ({tc['count']}) → {room_type}")
            return

        # Process memories
        assigned = 0
        rooms_created = 0
        errors = 0

        for memory in unassigned.select_related('agent'):
            try:
                room_type = MEMORY_TO_ROOM.get(memory.memory_type, 'general')
                meta = ROOM_META.get(room_type, ROOM_META['general'])

                # Get or create room
                room, created = MemoryPalaceRoom.objects.get_or_create(
                    agent=memory.agent,
                    room_type=room_type,
                    defaults={
                        'name': meta['name'],
                        'description': f'Auto-created room for {room_type} memories',
                        'icon': meta['icon'],
                        'color': meta['color'],
                    }
                )

                if created:
                    rooms_created += 1
                    self.stdout.write(f"  🏠 Created room '{room.name}' for {memory.agent.name}")

                # Assign memory to room
                memory.rooms.add(room)
                assigned += 1

                if assigned % 100 == 0:
                    self.stdout.write(f"  Progress: {assigned}/{total} memories assigned...")

            except Exception as e:
                errors += 1
                self.stderr.write(f"  Error assigning memory {memory.id}: {e}")

        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS(f"✅ Assigned {assigned} memories to rooms"))
        self.stdout.write(f"   Rooms created: {rooms_created}")
        if errors:
            self.stdout.write(self.style.WARNING(f"   Errors: {errors}"))

        # Verify
        still_unassigned = AgentMemory.objects.filter(rooms__isnull=True).count()
        self.stdout.write(f"\n   Remaining unassigned: {still_unassigned}")
