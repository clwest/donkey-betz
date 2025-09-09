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
    ContentTemplate, WorkflowExecution, ContentAnalytics
)


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


@receiver(post_save, sender=WorkflowExecution)
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
            if (old_instance.status != 'processing' and 
                instance.status == 'processing'):
                instance.add_processing_log(
                    step='processing_started',
                    status='info',
                    details={'timestamp': timezone.now().isoformat()}
                )
            
            # If status changed to processed/failed, record completion
            elif (old_instance.status in ['pending', 'processing'] and 
                  instance.status in ['processed', 'failed']):
                instance.add_processing_log(
                    step='processing_completed',
                    status='info' if instance.status == 'processed' else 'error',
                    details={
                        'timestamp': timezone.now().isoformat(),
                        'final_status': instance.status
                    }
                )
        except Document.DoesNotExist:
            pass