"""
Session 906: Detect and consolidate duplicate initiatives.
Session 1016: Enhanced with --snapshot flag and archive-instead-of-delete.

Problem: Multiple research briefs with similar topics create duplicate initiatives
like "Audit Failed Experiments", "Audit failed experiments", "Audit Recent Failed Experiments"
that should be consolidated into a single initiative.

Usage:
    # Snapshot - show all ACTIVE/TRIAGE initiatives
    python manage.py consolidate_duplicate_initiatives --snapshot

    # Dry run - show duplicate clusters
    python manage.py consolidate_duplicate_initiatives

    # Consolidate duplicates (merge into oldest)
    python manage.py consolidate_duplicate_initiatives --fix

    # Set similarity threshold (0.0-1.0, default 0.7)
    python manage.py consolidate_duplicate_initiatives --threshold=0.8
"""

from django.core.management.base import BaseCommand
from django.db.models import Count
from collections import defaultdict
import re
import logging

logger = logging.getLogger(__name__)


def normalize_name(name: str) -> str:
    """Normalize initiative name for comparison."""
    if not name:
        return ""
    # Lowercase
    name = name.lower()
    # Remove special chars
    name = re.sub(r'[^a-z0-9\s]', '', name)
    # Normalize whitespace
    name = re.sub(r'\s+', ' ', name).strip()
    return name


def extract_keywords(name: str) -> set:
    """Extract meaningful keywords from initiative name."""
    stopwords = {
        'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
        'recent', 'last', 'new', 'old', 'first', 'second', 'third',
    }
    normalized = normalize_name(name)
    words = set(normalized.split())
    return words - stopwords


def calculate_similarity(name1: str, name2: str) -> float:
    """Calculate Jaccard similarity between two initiative names."""
    kw1 = extract_keywords(name1)
    kw2 = extract_keywords(name2)

    if not kw1 or not kw2:
        return 0.0

    intersection = len(kw1 & kw2)
    union = len(kw1 | kw2)

    return intersection / union if union > 0 else 0.0


def find_duplicate_clusters(initiatives, threshold: float = 0.7) -> list:
    """
    Group initiatives into clusters of duplicates.

    Returns list of clusters, where each cluster is a list of similar initiatives.
    """
    # Build adjacency list of similar initiatives
    similar_pairs = defaultdict(set)
    initiative_list = list(initiatives)

    for i, init1 in enumerate(initiative_list):
        for init2 in initiative_list[i+1:]:
            similarity = calculate_similarity(init1.name, init2.name)
            if similarity >= threshold:
                similar_pairs[init1.id].add(init2.id)
                similar_pairs[init2.id].add(init1.id)

    # Find connected components (clusters)
    visited = set()
    clusters = []

    for init in initiative_list:
        if init.id in visited:
            continue
        if init.id not in similar_pairs:
            continue

        # BFS to find all connected initiatives
        cluster = []
        queue = [init]
        while queue:
            current = queue.pop(0)
            if current.id in visited:
                continue
            visited.add(current.id)
            cluster.append(current)

            for similar_id in similar_pairs[current.id]:
                if similar_id not in visited:
                    similar_init = next((i for i in initiative_list if i.id == similar_id), None)
                    if similar_init:
                        queue.append(similar_init)

        if len(cluster) > 1:
            # Sort by created_at to keep oldest as primary
            cluster.sort(key=lambda x: x.created_at)
            clusters.append(cluster)

    return clusters


class Command(BaseCommand):
    help = 'Detect and consolidate duplicate initiatives'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Actually consolidate duplicates (default is dry run)',
        )
        parser.add_argument(
            '--threshold',
            type=float,
            default=0.7,
            help='Similarity threshold 0.0-1.0 (default: 0.7)',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=500,
            help='Maximum initiatives to analyze (default: 500)',
        )
        parser.add_argument(
            '--snapshot',
            action='store_true',
            help='Session 1016: Print all ACTIVE/TRIAGE initiatives and exit',
        )

    def handle(self, *args, **options):
        from core.models_document_registry import Initiative, InitiativeStage

        # Session 1016: Snapshot mode
        if options['snapshot']:
            self._print_snapshot()
            return

        fix = options['fix']
        threshold = options['threshold']
        limit = options['limit']

        self.stdout.write(self.style.NOTICE(
            f"{'FIXING' if fix else 'DRY RUN'}: Finding duplicate initiatives "
            f"(threshold: {threshold}, limit: {limit})"
        ))

        # Get initiatives
        initiatives = Initiative.objects.filter(
            status__in=['ACTIVE', 'TRIAGE']
        ).order_by('-created_at')[:limit]
        self.stdout.write(f"Analyzing {initiatives.count()} initiatives...")

        # Find duplicate clusters
        clusters = find_duplicate_clusters(initiatives, threshold)

        if not clusters:
            self.stdout.write(self.style.SUCCESS("No duplicate clusters found!"))
            return

        self.stdout.write(f"\nFound {len(clusters)} duplicate clusters:\n")

        total_merged = 0
        total_kept = 0

        for i, cluster in enumerate(clusters, 1):
            primary = cluster[0]  # Oldest initiative becomes primary
            duplicates = cluster[1:]

            self.stdout.write(self.style.WARNING(f"\n--- Cluster {i} ({len(cluster)} initiatives) ---"))
            self.stdout.write(self.style.SUCCESS(f"  PRIMARY: {primary.name[:60]} (Stage {primary.current_stage})"))

            for dup in duplicates:
                similarity = calculate_similarity(primary.name, dup.name)
                self.stdout.write(f"  DUPLICATE ({similarity:.0%}): {dup.name[:60]}")

            if fix:
                merged_count = self._merge_cluster(primary, duplicates)
                total_merged += merged_count
                total_kept += 1
                self.stdout.write(self.style.SUCCESS(f"  -> Archived {merged_count} duplicates, kept primary"))
            else:
                total_merged += len(duplicates)
                total_kept += 1

        self.stdout.write(self.style.NOTICE(f"\n--- Summary ---"))
        self.stdout.write(f"Clusters found: {len(clusters)}")
        self.stdout.write(self.style.SUCCESS(f"{'Archived' if fix else 'Would archive'}: {total_merged} duplicates"))
        self.stdout.write(f"Primary initiatives: {total_kept}")

    def _print_snapshot(self):
        """Session 1016: Print all ACTIVE/TRIAGE initiatives."""
        from core.models_document_registry import Initiative

        initiatives = Initiative.objects.filter(
            status__in=['ACTIVE', 'TRIAGE']
        ).order_by('status', '-created_at')

        self.stdout.write(self.style.NOTICE(
            f"\n=== Initiative Snapshot ({initiatives.count()} ACTIVE/TRIAGE) ===\n"
        ))

        self.stdout.write(f"{'ID':<38} {'Status':<8} {'Stage':<6} {'Owner':<25} {'Name'}")
        self.stdout.write("-" * 120)

        for init in initiatives:
            owner = (init.owner_agent or '')[:24]
            self.stdout.write(
                f"{str(init.id):<38} {init.status:<8} {init.current_stage:<6} "
                f"{owner:<25} {init.name[:50]}"
            )

        # Summary counts
        active_count = initiatives.filter(status='ACTIVE').count()
        triage_count = initiatives.filter(status='TRIAGE').count()
        self.stdout.write(f"\nACTIVE: {active_count}  TRIAGE: {triage_count}  Total: {initiatives.count()}")

    def _merge_cluster(self, primary, duplicates) -> int:
        """
        Session 1016: Merge duplicate initiatives into the primary.

        - Move all stages/documents from duplicates to primary
        - ARCHIVE the duplicate initiatives (not delete)
        - Annotate primary's description with archived duplicate info
        """
        from core.models_document_registry import InitiativeStage
        from django.db import transaction

        merged_count = 0
        archived_info = []

        with transaction.atomic():
            for dup in duplicates:
                # Move stages that don't exist on primary
                for dup_stage in InitiativeStage.objects.filter(initiative=dup):
                    primary_stage, created = InitiativeStage.objects.get_or_create(
                        initiative=primary,
                        stage=dup_stage.stage,
                        defaults={
                            'status': dup_stage.status,
                            'document': dup_stage.document,
                        }
                    )

                    # If primary stage has no document but duplicate does, use duplicate's
                    if not primary_stage.document and dup_stage.document:
                        primary_stage.document = dup_stage.document
                        primary_stage.save()

                # Update primary's current_stage if duplicate was further along
                if dup.current_stage > primary.current_stage:
                    primary.current_stage = dup.current_stage
                    primary.save(skip_invariant_check=True)

                # Session 1016: Archive instead of delete
                archived_info.append(f"{str(dup.id)[:8]} ({dup.name[:40]}, created_by={dup.created_by or 'unknown'})")
                dup.status = 'ARCHIVED'
                dup.blocking_reason = f'Consolidated into {str(primary.id)[:8]}: {primary.name[:60]}'
                dup.save(skip_invariant_check=True)
                merged_count += 1

            # Session 1016: Annotate primary with archived duplicate info
            if archived_info:
                annotation = f"\n\n[Consolidation] Archived {len(archived_info)} duplicates:\n"
                annotation += "\n".join(f"  - {info}" for info in archived_info)
                primary.description = (primary.description or '') + annotation
                primary.save(skip_invariant_check=True)

        return merged_count
