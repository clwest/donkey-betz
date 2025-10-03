# Prompt Manager System Review

**Review Date**: August 10, 2025  
**Session**: Prompt Manager Error Analysis  
**Status**: Critical Query Logic Error  
**Impact**: Metrics endpoint fails for certain prompts

## Executive Summary

The Prompt Manager system has a critical Django QuerySet error:
1. **Query Slicing Error**: Cannot filter a query after slicing (using limit/offset)
2. **Affected Endpoint**: `/api/agent-orchestra/prompts/{id}/metrics/` returns 500 error
3. **Partial Functionality**: Some prompts work (ID 33) while others fail (ID 3, 6)
4. **Root Cause**: Incorrect QuerySet operation order in metrics calculation

## Issue Analysis

### 1. Django QuerySet Slicing Error

**Error Details**:
```
TypeError: Cannot filter a query once a slice has been taken.
File: backend/agent_orchestra/views_prompts.py, line 167
Code: successful = recent_instances.filter(current_status='completed').count()
```

**Affected Endpoints**:
- `/api/agent-orchestra/prompts/3/metrics/` - 500 error
- `/api/agent-orchestra/prompts/6/metrics/` - 500 error (likely)
- `/api/agent-orchestra/prompts/33/metrics/` - 200 OK (different code path?)

**Impact**:
- Metrics cannot be calculated for certain prompts
- Dashboard/UI showing errors when viewing prompt performance
- Inconsistent behavior across different prompt IDs

**Root Cause Analysis**:

The error occurs because the code is trying to:
1. First: Slice a QuerySet (e.g., `recent_instances = instances[:100]`)
2. Then: Filter the sliced QuerySet (`.filter(current_status='completed')`)

This is not allowed in Django. Once you slice a QuerySet (which adds LIMIT/OFFSET to the SQL), you cannot add additional filters.

### 2. Working vs Failing Endpoints

**Pattern Analysis**:
- Prompt 33 metrics work: Likely has fewer associated instances
- Prompts 3 and 6 fail: Likely have more instances triggering the slicing logic
- The code probably has conditional logic that only slices when there are many instances

## Detailed Solutions

### Solution 1: Fix Query Operation Order

**Priority**: CRITICAL  
**Estimated Time**: 15 minutes

#### Locate and Fix the Problematic Code

```python
# backend/agent_orchestra/views_prompts.py

# WRONG - Current problematic code (around line 167)
def prompt_metrics(request, pk):
    """Get metrics for a specific prompt"""
    try:
        prompt = PromptTemplate.objects.get(pk=pk)
        instances = AgentInstance.objects.filter(
            template__system_prompt_template__contains=prompt.content
        )
        
        # Problem: Slicing then filtering
        recent_instances = instances.order_by('-created_at')[:100]  # SLICE
        successful = recent_instances.filter(current_status='completed').count()  # ERROR!
        failed = recent_instances.filter(current_status='failed').count()  # ERROR!
        
    except Exception as e:
        # Error handling
        pass

# CORRECT - Fixed version
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def prompt_metrics(request, pk):
    """Get metrics for a specific prompt"""
    try:
        from django.db.models import Count, Avg, Q
        from datetime import datetime, timedelta
        from django.utils import timezone
        
        prompt = PromptTemplate.objects.get(pk=pk)
        
        # Get all instances that use this prompt
        all_instances = AgentInstance.objects.filter(
            template__system_prompt_template__contains=prompt.content
        )
        
        # Method 1: Filter first, then slice for display
        recent_instances = all_instances.order_by('-created_at')
        
        # Calculate metrics on the full queryset (or filtered subset)
        total_count = recent_instances.count()
        
        # If we want metrics on recent items only, filter by date instead of slicing
        last_30_days = timezone.now() - timedelta(days=30)
        recent_for_metrics = recent_instances.filter(created_at__gte=last_30_days)
        
        # Now we can safely calculate metrics
        successful = recent_for_metrics.filter(current_status='completed').count()
        failed = recent_for_metrics.filter(current_status='failed').count()
        in_progress = recent_for_metrics.filter(
            current_status__in=['working', 'pending', 'initializing']
        ).count()
        
        # Calculate success rate
        total_recent = successful + failed + in_progress
        success_rate = (successful / max(1, successful + failed)) * 100 if (successful + failed) > 0 else 0
        
        # Get average execution time (if field exists)
        avg_time = recent_for_metrics.filter(
            current_status='completed'
        ).aggregate(
            avg_time=Avg('execution_time')  # Adjust field name as needed
        )['avg_time'] or 0
        
        # Get top 10 recent instances for display
        recent_list = []
        for instance in recent_instances[:10]:  # Safe to slice here for display only
            recent_list.append({
                'id': instance.id,
                'status': instance.current_status,
                'created_at': instance.created_at,
                'agent_name': instance.template.name if instance.template else 'Unknown'
            })
        
        # Return metrics
        return Response({
            'prompt_id': pk,
            'total_uses': total_count,
            'recent_period': {
                'days': 30,
                'total': total_recent,
                'successful': successful,
                'failed': failed,
                'in_progress': in_progress,
                'success_rate': round(success_rate, 2)
            },
            'average_execution_time': avg_time,
            'recent_instances': recent_list,
            'last_updated': timezone.now()
        })
        
    except PromptTemplate.DoesNotExist:
        return Response(
            {'error': 'Prompt template not found'},
            status=404
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error calculating prompt metrics: {str(e)}")
        
        return Response(
            {'error': 'Failed to calculate metrics', 'detail': str(e)},
            status=500
        )
```

### Solution 2: Alternative Approaches for Large Datasets

**Priority**: HIGH  
**Estimated Time**: 30 minutes

#### Method A: Use Subqueries for Complex Metrics

```python
from django.db.models import Subquery, OuterRef, Count

def prompt_metrics_optimized(request, pk):
    """Optimized metrics calculation using subqueries"""
    
    # Get recent instance IDs first
    recent_ids = AgentInstance.objects.filter(
        template__system_prompt_template__contains=OuterRef('content')
    ).order_by('-created_at').values_list('id', flat=True)[:100]
    
    # Use the IDs for filtering
    metrics = AgentInstance.objects.filter(
        id__in=Subquery(recent_ids)
    ).aggregate(
        total=Count('id'),
        successful=Count('id', filter=Q(current_status='completed')),
        failed=Count('id', filter=Q(current_status='failed')),
        pending=Count('id', filter=Q(current_status__in=['pending', 'working']))
    )
    
    return metrics
```

#### Method B: Use Raw SQL for Complex Queries

```python
from django.db import connection

def prompt_metrics_raw(request, pk):
    """Use raw SQL for complex metrics that need slicing and filtering"""
    
    with connection.cursor() as cursor:
        cursor.execute("""
            WITH recent_instances AS (
                SELECT * FROM agent_orchestra_agentinstance
                WHERE template_id IN (
                    SELECT id FROM agent_orchestra_agenttemplate
                    WHERE system_prompt_template LIKE %s
                )
                ORDER BY created_at DESC
                LIMIT 100
            )
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN current_status = 'completed' THEN 1 ELSE 0 END) as successful,
                SUM(CASE WHEN current_status = 'failed' THEN 1 ELSE 0 END) as failed,
                AVG(CASE WHEN current_status = 'completed' THEN execution_time ELSE NULL END) as avg_time
            FROM recent_instances
        """, [f'%{prompt.content}%'])
        
        result = cursor.fetchone()
        
    return {
        'total': result[0],
        'successful': result[1],
        'failed': result[2],
        'avg_execution_time': result[3]
    }
```

#### Method C: Paginated Metrics Calculation

```python
from django.core.paginator import Paginator

def prompt_metrics_paginated(request, pk):
    """Calculate metrics with pagination support"""
    
    prompt = PromptTemplate.objects.get(pk=pk)
    
    # Get all instances without slicing
    all_instances = AgentInstance.objects.filter(
        template__system_prompt_template__contains=prompt.content
    ).order_by('-created_at')
    
    # Option 1: Calculate metrics on full dataset
    total_metrics = all_instances.aggregate(
        total=Count('id'),
        successful=Count('id', filter=Q(current_status='completed')),
        failed=Count('id', filter=Q(current_status='failed'))
    )
    
    # Option 2: Get paginated recent instances for display
    page = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 100)
    
    paginator = Paginator(all_instances, page_size)
    recent_page = paginator.get_page(page)
    
    # Calculate metrics for current page only
    page_ids = [instance.id for instance in recent_page]
    page_metrics = AgentInstance.objects.filter(
        id__in=page_ids
    ).aggregate(
        successful=Count('id', filter=Q(current_status='completed')),
        failed=Count('id', filter=Q(current_status='failed'))
    )
    
    return Response({
        'total_metrics': total_metrics,
        'page_metrics': page_metrics,
        'page_info': {
            'current': recent_page.number,
            'total_pages': paginator.num_pages,
            'has_next': recent_page.has_next(),
            'has_previous': recent_page.has_previous()
        }
    })
```

### Solution 3: Comprehensive Fix with Caching

**Priority**: MEDIUM  
**Estimated Time**: 45 minutes

```python
# backend/agent_orchestra/views_prompts.py

from django.core.cache import cache
from django.db.models import Count, Avg, Q, F
from datetime import datetime, timedelta
import hashlib

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def prompt_metrics(request, pk):
    """Get cached metrics for a specific prompt"""
    
    # Create cache key
    cache_key = f'prompt_metrics:{pk}:v2'
    
    # Try to get from cache
    cached_metrics = cache.get(cache_key)
    if cached_metrics and not request.GET.get('refresh'):
        return Response(cached_metrics)
    
    try:
        prompt = PromptTemplate.objects.get(pk=pk)
        
        # Build base queryset
        base_query = AgentInstance.objects.filter(
            template__system_prompt_template__contains=prompt.content
        )
        
        # Time-based filtering (instead of slicing)
        now = timezone.now()
        time_ranges = {
            '1h': now - timedelta(hours=1),
            '24h': now - timedelta(hours=24),
            '7d': now - timedelta(days=7),
            '30d': now - timedelta(days=30),
            'all': None
        }
        
        metrics = {}
        
        for period, start_time in time_ranges.items():
            if start_time:
                period_query = base_query.filter(created_at__gte=start_time)
            else:
                period_query = base_query
            
            # Calculate all metrics in one query
            period_metrics = period_query.aggregate(
                total=Count('id'),
                completed=Count('id', filter=Q(current_status='completed')),
                failed=Count('id', filter=Q(current_status='failed')),
                pending=Count('id', filter=Q(current_status='pending')),
                working=Count('id', filter=Q(current_status='working')),
                avg_progress=Avg('progress_percentage'),
                avg_execution=Avg(
                    F('updated_at') - F('created_at'),
                    filter=Q(current_status='completed')
                )
            )
            
            # Calculate derived metrics
            success_rate = 0
            if period_metrics['completed'] + period_metrics['failed'] > 0:
                success_rate = (
                    period_metrics['completed'] / 
                    (period_metrics['completed'] + period_metrics['failed']) * 100
                )
            
            metrics[period] = {
                **period_metrics,
                'success_rate': round(success_rate, 2)
            }
        
        # Get recent instances for display (safe to slice here)
        recent_display = []
        for instance in base_query.order_by('-created_at')[:20]:
            recent_display.append({
                'id': instance.id,
                'agent': instance.template.name if instance.template else 'Unknown',
                'status': instance.current_status,
                'progress': instance.progress_percentage,
                'created': instance.created_at.isoformat(),
                'duration': (
                    (instance.updated_at - instance.created_at).total_seconds()
                    if instance.updated_at else None
                )
            })
        
        # Get usage by agent template
        agent_usage = base_query.values(
            'template__name'
        ).annotate(
            count=Count('id'),
            success_rate=Avg(
                Case(
                    When(current_status='completed', then=100),
                    When(current_status='failed', then=0),
                    default=None,
                    output_field=FloatField()
                )
            )
        ).order_by('-count')[:10]
        
        result = {
            'prompt_id': pk,
            'prompt_name': prompt.name,
            'metrics_by_period': metrics,
            'recent_instances': recent_display,
            'agent_usage': list(agent_usage),
            'calculated_at': now.isoformat(),
            'cache_ttl': 300  # 5 minutes
        }
        
        # Cache the result
        cache.set(cache_key, result, 300)
        
        return Response(result)
        
    except PromptTemplate.DoesNotExist:
        return Response({'error': 'Prompt not found'}, status=404)
    except Exception as e:
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f"Prompt metrics error: {str(e)}\n{traceback.format_exc()}")
        
        # Return partial data if possible
        return Response({
            'error': 'Partial metrics available',
            'detail': str(e),
            'prompt_id': pk,
            'metrics_by_period': {},
            'recent_instances': []
        }, status=200)  # Return 200 with error flag instead of 500
```

### Solution 4: Quick Hotfix

**Priority**: IMMEDIATE  
**Estimated Time**: 5 minutes

```python
# Quick fix - just remove the slicing or reorder operations

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def prompt_metrics(request, pk):
    """Quick fix for prompt metrics"""
    try:
        prompt = PromptTemplate.objects.get(pk=pk)
        
        # Get all instances
        instances = AgentInstance.objects.filter(
            template__system_prompt_template__contains=prompt.content
        ).order_by('-created_at')
        
        # Option 1: Don't slice at all for metrics
        total = instances.count()
        successful = instances.filter(current_status='completed').count()
        failed = instances.filter(current_status='failed').count()
        
        # Option 2: Get recent by date instead of slicing
        last_30_days = timezone.now() - timedelta(days=30)
        recent = instances.filter(created_at__gte=last_30_days)
        recent_successful = recent.filter(current_status='completed').count()
        recent_failed = recent.filter(current_status='failed').count()
        
        # For display, we can safely slice
        display_instances = list(instances[:10].values(
            'id', 'current_status', 'created_at'
        ))
        
        return Response({
            'total_uses': total,
            'total_successful': successful,
            'total_failed': failed,
            'recent_successful': recent_successful,
            'recent_failed': recent_failed,
            'success_rate': (successful / max(1, successful + failed)) * 100,
            'recent_instances': display_instances
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)
```

## Django QuerySet Best Practices

### Rules to Avoid This Error

1. **Never filter after slicing**
   ```python
   # WRONG
   queryset = Model.objects.all()[:10]
   filtered = queryset.filter(status='active')  # ERROR!
   
   # CORRECT
   queryset = Model.objects.filter(status='active')[:10]
   ```

2. **Use time-based filtering instead of slicing for metrics**
   ```python
   # Instead of: instances[:100]
   # Use: instances.filter(created_at__gte=one_week_ago)
   ```

3. **Separate display data from metrics calculation**
   ```python
   # Metrics on full dataset
   metrics = queryset.aggregate(...)
   
   # Display data with slicing
   display = queryset[:10]
   ```

4. **Use subqueries for complex operations**
   ```python
   recent_ids = queryset.values_list('id', flat=True)[:100]
   metrics = Model.objects.filter(id__in=recent_ids).aggregate(...)
   ```

5. **Consider using raw SQL for complex queries**
   ```python
   with connection.cursor() as cursor:
       cursor.execute("SELECT ... LIMIT 100")
   ```

## Testing Checklist

### Immediate Testing
- [ ] Test `/api/agent-orchestra/prompts/3/metrics/` - Should return 200
- [ ] Test `/api/agent-orchestra/prompts/6/metrics/` - Should return 200
- [ ] Test `/api/agent-orchestra/prompts/33/metrics/` - Should still work
- [ ] Verify metrics accuracy with known data

### QuerySet Testing
- [ ] Test with prompts that have 0 instances
- [ ] Test with prompts that have 1-10 instances
- [ ] Test with prompts that have 100+ instances
- [ ] Test with prompts that have 1000+ instances

### Performance Testing
- [ ] Measure response time for large datasets
- [ ] Verify caching is working (if implemented)
- [ ] Check database query count with Django Debug Toolbar
- [ ] Test concurrent requests to same endpoint

### Edge Cases
- [ ] Test with invalid prompt ID
- [ ] Test with deleted prompt templates
- [ ] Test with prompts containing special characters
- [ ] Test pagination parameters (if implemented)

## Implementation Priority

1. **IMMEDIATE (5 minutes)**
   - Apply quick hotfix to unblock functionality
   - Remove slicing or reorder operations
   
2. **HIGH (30 minutes)**
   - Implement proper solution with time-based filtering
   - Add error handling and logging
   
3. **MEDIUM (1 hour)**
   - Add caching for expensive metrics
   - Implement pagination support
   - Optimize database queries
   
4. **LOW (2 hours)**
   - Add comprehensive metrics dashboard
   - Implement real-time metrics updates
   - Add export functionality

## Monitoring and Prevention

### Add Query Monitoring
```python
# In settings.py for development
LOGGING = {
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        }
    }
}
```

### Add Unit Tests
```python
# tests/test_prompt_metrics.py
from django.test import TestCase
from django.urls import reverse

class PromptMetricsTestCase(TestCase):
    def test_metrics_with_many_instances(self):
        """Test metrics calculation with >100 instances"""
        # Create 150 instances
        for i in range(150):
            AgentInstance.objects.create(...)
        
        response = self.client.get(
            reverse('prompt-metrics', kwargs={'pk': self.prompt.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('total_uses', response.data)
    
    def test_metrics_with_no_instances(self):
        """Test metrics with no instances"""
        response = self.client.get(
            reverse('prompt-metrics', kwargs={'pk': self.prompt.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_uses'], 0)
```

### Add Integration Tests
```python
# tests/test_prompt_integration.py
def test_large_dataset_performance():
    """Ensure metrics calculate in reasonable time"""
    import time
    
    # Create 10,000 instances
    AgentInstance.objects.bulk_create([
        AgentInstance(...) for _ in range(10000)
    ])
    
    start = time.time()
    response = client.get(f'/api/agent-orchestra/prompts/{prompt.id}/metrics/')
    duration = time.time() - start
    
    assert response.status_code == 200
    assert duration < 2.0  # Should complete in under 2 seconds
```

## Conclusion

The Prompt Manager has a straightforward but critical issue:
1. **Problem**: Attempting to filter a QuerySet after slicing
2. **Impact**: 500 errors on metrics endpoints for certain prompts
3. **Solution**: Reorder operations - filter first, then slice
4. **Prevention**: Follow Django QuerySet best practices

The fix is simple and can be implemented immediately. The comprehensive solutions provide:
- Multiple implementation approaches
- Performance optimizations
- Caching strategies
- Monitoring and testing guidelines

Estimated fix time: 
- **Hotfix**: 5 minutes
- **Proper solution**: 30 minutes
- **Complete implementation with optimizations**: 2-3 hours