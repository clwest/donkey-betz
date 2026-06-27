"""
Content Management System Signals

Signal handlers for maintaining content system consistency,
analytics, and cross-system integration.
"""

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import (
    Document, DocumentEmbedding, KnowledgeBase, ContentGeneration,
    ContentTemplate, ContentWorkflowExecution, ContentAnalytics, ImageHistory
)
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Document)
def update_knowledge_base_stats(sender, instance, created, **kwargs):
    """Update knowledge base statistics when documents are added/modified"""
    if instance.collection and instance.is_active:
        try:
            kb = KnowledgeBase.objects.get(name=instance.collection)
            kb.update_statistics()
        except KnowledgeBase.DoesNotExist:
            pass


@receiver(post_delete, sender=Document)
def update_knowledge_base_stats_on_delete(sender, instance, **kwargs):
    """Update knowledge base statistics when documents are deleted"""
    if instance.collection:
        try:
            kb = KnowledgeBase.objects.get(name=instance.collection)
            kb.update_statistics()
        except KnowledgeBase.DoesNotExist:
            pass


@receiver(post_save, sender=ContentGeneration)
def update_template_stats(sender, instance, created, **kwargs):
    """Update template usage statistics when content is generated"""
    if instance.template and instance.status in ['completed', 'processed']:
        generation_time = None
        if instance.generation_time_ms:
            generation_time = instance.generation_time_ms / 1000.0
        
        success = instance.status == 'processed'
        
        instance.template.update_stats(
            generation_time=generation_time,
            success=success,
            rating=instance.user_rating
        )


@receiver(post_save, sender=Document)
def record_document_analytics(sender, instance, created, **kwargs):
    """Record analytics metrics for document operations"""
    if created:
        ContentAnalytics.record_metric(
            name='documents_created',
            value=1,
            metric_type='counter',
            subsystem='documents',
            context={
                'document_type': instance.document_type,
                'source': instance.source,
                'source_system': instance.source_system,
            },
            user=instance.owner,
            document=instance
        )


@receiver(post_save, sender=ContentGeneration)
def record_generation_analytics(sender, instance, created, **kwargs):
    """Record analytics for content generation"""
    if created:
        ContentAnalytics.record_metric(
            name='content_generations',
            value=1,
            metric_type='counter',
            subsystem='generation',
            context={
                'template_id': str(instance.template.id) if instance.template else None,
                'source_system': instance.source_system,
            },
            user=instance.user,
            template=instance.template
        )
    
    # Record performance metrics when generation completes
    if instance.status == 'processed' and instance.generation_time_ms:
        ContentAnalytics.record_metric(
            name='generation_time_ms',
            value=instance.generation_time_ms,
            metric_type='histogram',
            subsystem='generation',
            context={
                'template_id': str(instance.template.id) if instance.template else None,
            },
            user=instance.user,
            template=instance.template
        )
        
        if instance.token_usage.get('total'):
            ContentAnalytics.record_metric(
                name='tokens_used',
                value=instance.token_usage['total'],
                metric_type='counter',
                subsystem='generation',
                context={
                    'template_id': str(instance.template.id) if instance.template else None,
                },
                user=instance.user,
                template=instance.template
            )


@receiver(post_save, sender=DocumentEmbedding)
def record_embedding_analytics(sender, instance, created, **kwargs):
    """Record analytics for embedding generation"""
    if created:
        ContentAnalytics.record_metric(
            name='embeddings_created',
            value=1,
            metric_type='counter',
            subsystem='embeddings',
            context={
                'embedding_model': instance.embedding_model,
                'dimension': instance.embedding_dimension,
            },
            document=instance.document
        )
        
        if instance.processing_time_ms:
            ContentAnalytics.record_metric(
                name='embedding_time_ms',
                value=instance.processing_time_ms,
                metric_type='histogram',
                subsystem='embeddings',
                context={
                    'embedding_model': instance.embedding_model,
                },
                document=instance.document
            )


@receiver(post_save, sender=ContentWorkflowExecution)
def record_workflow_analytics(sender, instance, created, **kwargs):
    """Record analytics for workflow executions"""
    if created:
        ContentAnalytics.record_metric(
            name='workflow_executions',
            value=1,
            metric_type='counter',
            subsystem='workflows',
            context={
                'workflow_id': str(instance.workflow.id),
                'workflow_domain': instance.workflow.domain,
            },
            user=instance.user
        )
    
    # Record completion metrics
    if instance.status == 'processed' and instance.execution_time_seconds:
        ContentAnalytics.record_metric(
            name='workflow_execution_time',
            value=instance.execution_time_seconds,
            metric_type='histogram',
            subsystem='workflows',
            context={
                'workflow_id': str(instance.workflow.id),
            },
            user=instance.user
        )


@receiver(pre_save, sender=Document)
def set_document_processing_timestamp(sender, instance, **kwargs):
    """Set processing timestamps based on status changes"""
    if instance.pk:
        try:
            old_instance = Document.objects.get(pk=instance.pk)
            # If status changed to processing, record start time
            # Session 733: Don't call add_processing_log() as it triggers save() and causes recursion
            # Instead, directly append to the list - the outer save() will persist it
            if (old_instance.status != 'processing' and
                instance.status == 'processing'):
                if not instance.processing_log:
                    instance.processing_log = []
                instance.processing_log.append({
                    'step': 'processing_started',
                    'status': 'info',
                    'timestamp': timezone.now().isoformat(),
                    'details': {}
                })

            # If status changed to processed/failed, record completion
            elif (old_instance.status in ['pending', 'processing'] and
                  instance.status in ['processed', 'failed']):
                if not instance.processing_log:
                    instance.processing_log = []
                instance.processing_log.append({
                    'step': 'processing_completed',
                    'status': 'info' if instance.status == 'processed' else 'error',
                    'timestamp': timezone.now().isoformat(),
                    'details': {'final_status': instance.status}
                })
        except Document.DoesNotExist:
            pass


# =============================================================================
# SESSION 492: IMAGE PROVENANCE AUTO-CREATION
# =============================================================================
# Automatically create provenance records when images are generated.
# This enables the Certificate Service to generate PDF ownership certificates.

@receiver(post_save, sender=ImageHistory)
def create_image_provenance(sender, instance, created, **kwargs):
    """
    Session 492: Auto-create provenance record when an image is saved.

    This connects the CertificateService to the image generation flow,
    enabling users to download PDF ownership certificates for any image.
    """
    if not created:
        return  # Only process new images

    # Skip if user is not set (shouldn't happen, but safety check)
    if not instance.user:
        logger.warning(f"ImageHistory {instance.id} has no user, skipping provenance")
        return

    try:
        from core.services.provenance_service import ProvenanceService
        from django.core.files.storage import default_storage

        # Read image bytes from file
        image_bytes = None

        if instance.file_path:
            # Handle data: URIs
            if instance.file_path.startswith('data:'):
                import base64
                # Extract base64 data after the comma
                if ',' in instance.file_path:
                    base64_data = instance.file_path.split(',', 1)[1]
                    image_bytes = base64.b64decode(base64_data)
            # Handle regular file paths
            elif default_storage.exists(instance.file_path):
                with default_storage.open(instance.file_path, 'rb') as f:
                    image_bytes = f.read()

        # If no bytes, try reading from image field
        if not image_bytes and hasattr(instance, 'image') and instance.image:
            instance.image.seek(0)
            image_bytes = instance.image.read()
            instance.image.seek(0)

        if not image_bytes:
            logger.debug(f"No image bytes available for ImageHistory {instance.id}, skipping provenance")
            return

        # Build generation params from image metadata
        generation_params = {
            'prompt': instance.prompt or '',
            'model': instance.model_used or 'unknown',
            'style': instance.style or '',
            'image_type': instance.image_type or 'generated',
        }

        # Add any additional params stored
        if instance.parameters:
            generation_params.update(instance.parameters)

        # Create provenance
        service = ProvenanceService()
        result = service.create_provenance(
            image_history=instance,
            user=instance.user,
            image_bytes=image_bytes,
            generation_params=generation_params
        )

        if result.success:
            logger.info(f"📜 [Session 492] Auto-created provenance for image {instance.id}: {result.provenance_id}")
        else:
            logger.warning(f"Failed to create provenance for image {instance.id}: {result.error}")

    except Exception as e:
        # Non-fatal: log but don't break image creation
        logger.warning(f"Error creating provenance for image {instance.id}: {e}")