# Session 862: Apply PublishGate to existing blogs
# Evaluates and classifies all SelfBlog entries

from django.core.management.base import BaseCommand
from django.db import transaction

from core.models_unified_system import SelfBlog
from core.services.publish_gate import PublishGate
from core.services.content_classifier import ContentClassifier


class Command(BaseCommand):
    help = 'Apply PublishGate quality evaluation to SelfBlog entries'

    def add_arguments(self, parser):
        parser.add_argument(
            '--blog-id',
            type=str,
            help='Evaluate a specific blog by ID',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Evaluate all blogs',
        )
        parser.add_argument(
            '--drafts-only',
            action='store_true',
            help='Only evaluate draft blogs',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show results without saving',
        )
        parser.add_argument(
            '--reclassify',
            action='store_true',
            help='Reclassify blogs that should be internal',
        )
        parser.add_argument(
            '--summary',
            action='store_true',
            help='Show summary statistics only',
        )

    def handle(self, *args, **options):
        gate = PublishGate()
        classifier = ContentClassifier()

        # Summary mode
        if options['summary']:
            self._show_summary()
            return

        # Single blog mode
        if options['blog_id']:
            self._evaluate_single(options['blog_id'], gate, classifier, options['dry_run'])
            return

        # Batch mode
        if options['all'] or options['drafts_only']:
            self._evaluate_batch(
                gate,
                classifier,
                drafts_only=options['drafts_only'],
                dry_run=options['dry_run'],
                reclassify=options['reclassify'],
            )
            return

        # Default: show help
        self.stdout.write(self.style.WARNING('\nNo action specified. Use one of:'))
        self.stdout.write('  --blog-id UUID    Evaluate a specific blog')
        self.stdout.write('  --all             Evaluate all blogs')
        self.stdout.write('  --drafts-only     Evaluate only drafts')
        self.stdout.write('  --summary         Show statistics')
        self.stdout.write('  --dry-run         Preview without saving')
        self.stdout.write('  --reclassify      Auto-reclassify internal content')

    def _show_summary(self):
        """Show summary statistics."""
        from django.db.models import Count, Avg

        self.stdout.write(self.style.SUCCESS('\n=== PublishGate Summary ===\n'))

        total = SelfBlog.objects.count()
        self.stdout.write(f'Total SelfBlogs: {total}')

        # By status
        self.stdout.write('\nBy Status:')
        for status, label in SelfBlog.STATUS_CHOICES:
            count = SelfBlog.objects.filter(status=status).count()
            self.stdout.write(f'  {label}: {count}')

        # By content type
        self.stdout.write('\nBy Content Type:')
        for ct, label in SelfBlog.CONTENT_TYPE_CHOICES:
            count = SelfBlog.objects.filter(content_type=ct).count()
            self.stdout.write(f'  {label}: {count}')

        # By category
        self.stdout.write('\nBy Category:')
        for cat, label in SelfBlog.CATEGORY_CHOICES:
            count = SelfBlog.objects.filter(category=cat).count()
            if count > 0:
                self.stdout.write(f'  {label}: {count}')

        # Quality scores
        scored = SelfBlog.objects.filter(quality_score__isnull=False)
        if scored.exists():
            avg_scores = scored.aggregate(
                avg_quality=Avg('quality_score'),
                avg_novelty=Avg('novelty_score'),
                avg_structure=Avg('structure_score'),
            )
            self.stdout.write('\nAverage Scores (scored blogs):')
            self.stdout.write(f'  Quality:   {avg_scores["avg_quality"]:.2f}')
            self.stdout.write(f'  Novelty:   {avg_scores["avg_novelty"]:.2f}')
            self.stdout.write(f'  Structure: {avg_scores["avg_structure"]:.2f}')

        # Publish ready
        ready = SelfBlog.objects.filter(publish_ready=True).count()
        self.stdout.write(f'\nPublish Ready: {ready} / {total}')

        # Needs attention
        misclassified = SelfBlog.objects.filter(
            category='blog',
            content_type='internal'
        ).count()
        if misclassified:
            self.stdout.write(self.style.WARNING(f'\nNeeds Reclassification: {misclassified} blogs marked as internal but categorized as "blog"'))

        self.stdout.write('')

    def _evaluate_single(self, blog_id: str, gate: PublishGate, classifier: ContentClassifier, dry_run: bool):
        """Evaluate a single blog."""
        try:
            blog = SelfBlog.objects.get(id=blog_id)
        except SelfBlog.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Blog not found: {blog_id}'))
            return

        self.stdout.write(self.style.SUCCESS(f'\n=== Evaluating: {blog.title[:60]}... ===\n'))

        # Classification
        class_result = classifier.classify_blog(blog)
        self.stdout.write('Classification:')
        self.stdout.write(f'  Content Type: {class_result.content_type}')
        self.stdout.write(f'  Suggested Category: {class_result.suggested_category}')
        self.stdout.write(f'  Confidence: {class_result.confidence:.0%}')
        self.stdout.write(f'  Reasoning: {class_result.reasoning}')
        self.stdout.write('')

        # Quality evaluation
        gate_result = gate.evaluate(blog)
        self.stdout.write('Quality Scores:')
        self.stdout.write(f'  Quality:   {gate_result.quality_score:.2f}')
        self.stdout.write(f'  Novelty:   {gate_result.novelty_score:.2f}')
        self.stdout.write(f'  Structure: {gate_result.structure_score:.2f}')
        self.stdout.write('')

        self.stdout.write(f'Decision: {self.style.WARNING(gate_result.decision.upper())}')
        self.stdout.write(f'Notes: {gate_result.notes}')
        self.stdout.write('')

        if not dry_run:
            gate.apply_to_blog(blog, save=True)
            self.stdout.write(self.style.SUCCESS('Saved to database'))
        else:
            self.stdout.write(self.style.WARNING('(Dry run - not saved)'))

    def _evaluate_batch(
        self,
        gate: PublishGate,
        classifier: ContentClassifier,
        drafts_only: bool,
        dry_run: bool,
        reclassify: bool,
    ):
        """Evaluate multiple blogs."""
        queryset = SelfBlog.objects.all()
        if drafts_only:
            queryset = queryset.filter(status='draft')

        total = queryset.count()
        self.stdout.write(self.style.SUCCESS(f'\n=== Evaluating {total} blogs ===\n'))

        results = {
            'publish': 0,
            'enhance': 0,
            'internal_only': 0,
        }
        reclassified = 0

        with transaction.atomic():
            for blog in queryset:
                # Evaluate
                gate_result = gate.evaluate(blog)
                results[gate_result.decision] += 1

                # Apply if not dry run
                if not dry_run:
                    blog.quality_score = gate_result.quality_score
                    blog.novelty_score = gate_result.novelty_score
                    blog.structure_score = gate_result.structure_score
                    blog.content_type = gate_result.content_type
                    blog.gate_notes = gate_result.notes
                    blog.publish_ready = (gate_result.decision == 'publish')

                    # Reclassify if needed
                    if reclassify and gate_result.suggested_category and blog.category == 'blog':
                        if gate_result.decision == 'internal_only':
                            blog.category = gate_result.suggested_category
                            reclassified += 1

                    blog.save()

                # Progress output
                decision_style = {
                    'publish': self.style.SUCCESS,
                    'enhance': self.style.WARNING,
                    'internal_only': self.style.NOTICE,
                }.get(gate_result.decision, str)

                decision_text = decision_style(gate_result.decision.upper().ljust(15))
                self.stdout.write(
                    f'  {decision_text} '
                    f'Q:{gate_result.quality_score:.2f} '
                    f'N:{gate_result.novelty_score:.2f} '
                    f'S:{gate_result.structure_score:.2f} '
                    f'| {blog.title[:50]}...'
                )

        # Summary
        self.stdout.write('\n=== Results ===')
        self.stdout.write(f'  Publish Ready: {results["publish"]}')
        self.stdout.write(f'  Needs Enhancement: {results["enhance"]}')
        self.stdout.write(f'  Internal Only: {results["internal_only"]}')

        if reclassified:
            self.stdout.write(f'  Reclassified: {reclassified}')

        if dry_run:
            self.stdout.write(self.style.WARNING('\n(Dry run - nothing saved)'))
        else:
            self.stdout.write(self.style.SUCCESS('\nAll changes saved'))
