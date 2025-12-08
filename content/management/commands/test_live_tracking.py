"""
Django management command to test live agent contribution tracking.

Usage:
    python manage.py test_live_tracking
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from content.models import ImageHistory, CreativeProject
from core.models.agents_registry import AgentContribution, UnifiedAgentTemplate
from content.image_generation import ImageGenerationService


class Command(BaseCommand):
    help = 'Test live agent contribution tracking by generating a test image'

    def handle(self, *args, **options):
        self.stdout.write("=" * 70)
        self.stdout.write(self.style.SUCCESS("🧪 SESSION 143: Live Agent Contribution Tracking Test"))
        self.stdout.write("=" * 70)
        self.stdout.write("")

        # Use an existing project
        project = CreativeProject.objects.first()
        if not project:
            self.stdout.write(self.style.ERROR("No projects found! Please create a project first."))
            return
        self.stdout.write(f"Using existing project: {project.name} (ID: {project.id})")
        self.stdout.write("")

        # Record counts before
        initial_images = ImageHistory.objects.count()
        initial_contributions = AgentContribution.objects.count()

        self.stdout.write(f"📊 Before Test:")
        self.stdout.write(f"   Images: {initial_images}")
        self.stdout.write(f"   Contributions: {initial_contributions}")
        self.stdout.write("")

        # Generate a test image
        self.stdout.write("-" * 70)
        self.stdout.write("Generating Test Image...")
        self.stdout.write("-" * 70)

        try:
            service = ImageGenerationService()
            result = service.generate_image(
                prompt="Session 143 test: futuristic robot mascot, digital art",
                model="sd3-large-turbo",
                size="1024x1024",
                project_id=str(project.id)
            )

            if result.get('success'):
                image_id = result.get('image_id')
                self.stdout.write(self.style.SUCCESS(f"✅ Image generated successfully!"))
                self.stdout.write(f"   Image ID: {image_id}")
                self.stdout.write("")

                # Wait a moment for any async operations
                import time
                time.sleep(2)

                # Check if contribution was created
                image = ImageHistory.objects.get(id=image_id)
                contrib = AgentContribution.objects.filter(image=image).first()

                if contrib:
                    self.stdout.write(self.style.SUCCESS("✅ AgentContribution created!"))
                    self.stdout.write(f"   Agent: {contrib.agent.name}")
                    self.stdout.write(f"   Type: {contrib.contribution_type}")
                    self.stdout.write(f"   Task: {contrib.task_description[:80]}...")
                    self.stdout.write("")
                else:
                    self.stdout.write(self.style.ERROR("❌ NO AgentContribution found!"))
                    self.stdout.write(self.style.ERROR("   This means Session 142 wiring is NOT working!"))
                    self.stdout.write("")

            else:
                self.stdout.write(self.style.ERROR(f"❌ Image generation failed: {result.get('error')}"))
                return

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error: {e}"))
            import traceback
            traceback.print_exc()
            return

        # Final counts
        final_images = ImageHistory.objects.count()
        final_contributions = AgentContribution.objects.count()

        self.stdout.write("=" * 70)
        self.stdout.write("📊 FINAL RESULTS")
        self.stdout.write("=" * 70)
        self.stdout.write(f"Images: {initial_images} → {final_images} (+{final_images - initial_images})")
        self.stdout.write(f"Contributions: {initial_contributions} → {final_contributions} (+{final_contributions - initial_contributions})")
        self.stdout.write("")

        # Calculate tracking for new content
        new_images = final_images - initial_images
        new_contribs = final_contributions - initial_contributions

        if new_images > 0:
            tracking_rate = (new_contribs / new_images * 100)
            self.stdout.write(f"New Content Tracking Rate: {tracking_rate:.1f}% ({new_contribs}/{new_images})")

            if tracking_rate == 100:
                self.stdout.write(self.style.SUCCESS("✅ SUCCESS! All new content has agent contributions!"))
                self.stdout.write(self.style.SUCCESS("   Session 142 wiring is working correctly!"))
            elif tracking_rate >= 95:
                self.stdout.write(self.style.SUCCESS("✅ EXCELLENT! Tracking rate ≥ 95%"))
            else:
                self.stdout.write(self.style.WARNING("⚠️  WARNING! Some new content missing agent contributions!"))
        else:
            self.stdout.write(self.style.WARNING("⚠️  No new content was generated"))

        self.stdout.write("=" * 70)
