# AI-First Batch Processing Integration Guide

## Overview

This guide details how to integrate the existing batch processing system with the new AI-First Asset Library to enable bulk AI operations on generated assets.

## Current Batch Processing Architecture

### Backend Components

1. **Model**: `BatchJob` (content/models_extended.py)
   - Tracks batch processing jobs with status, progress, and results
   - Supports operations: resize, convert, compress, watermark, generate_thumbnails, extract_frames
   - Uses Celery for async processing

2. **Views**: `BatchProcessViewSet` (content/views_batch.py)
   - REST API endpoints for batch operations
   - WebSocket support for real-time updates
   - Start, cancel, and monitor batch jobs

3. **Tasks**: `process_batch_job` (content/tasks.py)
   - Celery task for async processing
   - Handles different operations based on job type
   - Updates progress via WebSocket

4. **Serializers**: `BatchJobSerializer` & `BatchProcessRequestSerializer`
   - Validates batch requests
   - Ensures proper parameters for each operation

### Frontend Components

1. **Component**: `BatchProcessor` (features/content-studio/components/BatchProcessor.tsx)
   - UI for selecting operations and parameters
   - Real-time job monitoring
   - Operation-specific settings

2. **Hook**: `useBatchProcess` (features/content-studio/hooks/useBatchProcess.ts)
   - React Query integration
   - WebSocket connection for updates
   - Job management (start, cancel, monitor)

## Integration Plan for AI-First Assets

### Phase 1: Add AI-Specific Batch Operations

#### New Operations to Add:
```python
# In BatchJob model choices
('ai_enhance', 'AI Enhancement'),
('ai_style_transfer', 'AI Style Transfer'),
('ai_upscale', 'AI Upscaling'),
('ai_background_removal', 'AI Background Removal'),
('ai_brand_compliance', 'Apply Brand Compliance'),
('ai_generate_variations', 'Generate AI Variations'),
```

#### Implementation Steps:

1. **Update BatchJob Model**:
```python
# content/models_extended.py
class BatchJob(models.Model):
    operation = models.CharField(max_length=50, choices=[
        # Existing operations...
        ('ai_enhance', 'AI Enhancement'),
        ('ai_style_transfer', 'AI Style Transfer'),
        ('ai_upscale', 'AI Upscaling'),
        ('ai_background_removal', 'AI Background Removal'),
        ('ai_brand_compliance', 'Apply Brand Compliance'),
        ('ai_generate_variations', 'Generate AI Variations'),
    ])
    
    # Add AI-specific fields
    ai_model = models.CharField(max_length=50, blank=True)
    brand_identity_id = models.IntegerField(null=True, blank=True)
```

2. **Create AI Batch Processing Service**:
```python
# content/services/ai_batch_service.py
from typing import List, Dict, Any
from ..models.ai_generation import AIGeneratedAsset, BrandIdentity
from ..services.ai_generation_service import AIGenerationService
from ..services.brand_compliance_service import BrandComplianceService

class AIBatchService:
    def __init__(self):
        self.ai_service = AIGenerationService()
        self.compliance_service = BrandComplianceService()
    
    async def process_ai_enhancement(
        self, 
        assets: List[AIGeneratedAsset], 
        parameters: Dict[str, Any]
    ):
        """Enhance assets using AI"""
        # Implementation
    
    async def process_style_transfer(
        self,
        assets: List[AIGeneratedAsset],
        style_reference: str,
        parameters: Dict[str, Any]
    ):
        """Apply style transfer to assets"""
        # Implementation
    
    async def process_brand_compliance(
        self,
        assets: List[AIGeneratedAsset],
        brand_identity: BrandIdentity
    ):
        """Apply brand compliance to assets"""
        # Implementation
```

### Phase 2: Extend Batch Processing Tasks

1. **Update Celery Tasks**:
```python
# content/tasks.py
@shared_task
def process_batch_job(job_id: int):
    # Existing code...
    
    # Add AI operations
    if job.operation == 'ai_enhance':
        process_ai_enhancement(asset, job.parameters, job)
    elif job.operation == 'ai_style_transfer':
        process_ai_style_transfer(asset, job.parameters, job)
    # ... etc

def process_ai_enhancement(asset, parameters, job):
    """Process AI enhancement for single asset"""
    ai_batch_service = AIBatchService()
    
    # Run async operation in sync context
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        enhanced_asset = loop.run_until_complete(
            ai_batch_service.process_ai_enhancement([asset], parameters)
        )
        # Update job progress
        job.processed_count += 1
        job.save()
        # Send WebSocket update
        send_progress_update(job)
    except Exception as e:
        job.failed_count += 1
        job.errors.append(str(e))
        job.save()
    finally:
        loop.close()
```

### Phase 3: Update Frontend Components

1. **Add AI Operations to BatchProcessor**:
```typescript
// BatchProcessor.tsx
const operations = [
  // Existing operations...
  { id: 'ai_enhance', label: 'AI Enhancement', icon: '✨', color: colors.accent.purple },
  { id: 'ai_style_transfer', label: 'Style Transfer', icon: '🎨', color: colors.accent.cyan },
  { id: 'ai_upscale', label: 'AI Upscaling', icon: '🔍', color: colors.accent.blue },
  { id: 'ai_background_removal', label: 'Remove Background', icon: '✂️', color: colors.accent.green },
  { id: 'ai_brand_compliance', label: 'Apply Brand', icon: '🏷️', color: colors.accent.gold },
  { id: 'ai_generate_variations', label: 'Generate Variations', icon: '🎲', color: colors.accent.orange }
];
```

2. **Add AI-Specific Parameters**:
```typescript
// AI Enhancement parameters
{operation === 'ai_enhance' && (
  <div>
    <label>Enhancement Level</label>
    <select value={parameters.ai_enhance.level}>
      <option value="auto">Auto</option>
      <option value="light">Light</option>
      <option value="medium">Medium</option>
      <option value="strong">Strong</option>
    </select>
    
    <label>
      <input type="checkbox" checked={parameters.ai_enhance.preserve_style} />
      Preserve Original Style
    </label>
  </div>
)}
```

### Phase 4: Integration with AI Asset Library

1. **Connect to AI Generated Assets**:
```python
# views_batch.py
@action(detail=False, methods=['post'], url_path='start-ai')
def start_ai_batch(self, request):
    """Start AI batch processing on generated assets"""
    # Get AI generated assets
    asset_ids = request.data.get('assets', [])
    ai_assets = AIGeneratedAsset.objects.filter(
        id__in=asset_ids,
        generation_request__user=request.user
    )
    
    # Create batch job
    job = BatchJob.objects.create(
        user=request.user,
        operation=request.data['operation'],
        parameters=request.data.get('parameters', {}),
        input_count=ai_assets.count(),
        input_assets=[asset.id for asset in ai_assets],
        ai_model=request.data.get('ai_model', 'dall-e-3'),
        brand_identity_id=request.data.get('brand_identity_id')
    )
    
    # Queue processing
    process_ai_batch_job.delay(job.id)
    
    return Response({'job_id': job.id})
```

2. **Update Asset Selection in Frontend**:
```typescript
// AssetLibrary.tsx integration
const handleBatchProcess = () => {
  const selectedAIAssets = selectedAssets
    .filter(asset => asset.is_ai_generated)
    .map(asset => asset.ai_asset?.id)
    .filter(Boolean);
  
  // Open batch processor with AI assets
  setBatchProcessorOpen(true);
  setBatchAssets(selectedAIAssets);
};
```

### Phase 5: Advanced AI Batch Features

1. **Brand Compliance Batch Processing**:
```python
async def apply_brand_compliance_batch(
    self,
    assets: List[AIGeneratedAsset],
    brand_identity: BrandIdentity,
    auto_approve: bool = False
):
    """Apply brand compliance to multiple assets"""
    results = []
    
    for asset in assets:
        # Analyze compliance
        compliance_score = await self.compliance_service.analyze_asset(
            asset, brand_identity
        )
        
        if compliance_score < brand_identity.compliance_threshold:
            # Generate compliant version
            compliant_asset = await self.ai_service.regenerate_with_brand(
                asset, brand_identity
            )
            results.append(compliant_asset)
        else:
            results.append(asset)
    
    return results
```

2. **Batch Variation Generation**:
```python
async def generate_variations_batch(
    self,
    assets: List[AIGeneratedAsset],
    variations_per_asset: int = 3
):
    """Generate variations for multiple assets"""
    all_variations = []
    
    for asset in assets:
        # Extract original prompt and parameters
        original_prompt = asset.generation_prompt
        
        # Generate variations
        variations = await self.ai_service.generate_assets(
            user=asset.generation_request.user,
            asset_type=asset.generation_request.asset_type,
            prompt=original_prompt,
            variations=variations_per_asset,
            base_asset_id=asset.id
        )
        
        all_variations.extend(variations)
    
    return all_variations
```

### Phase 6: Monitoring and Analytics

1. **Add Batch Job Analytics**:
```python
# models_extended.py
class BatchJobAnalytics(models.Model):
    job = models.OneToOneField(BatchJob, on_delete=models.CASCADE)
    avg_processing_time = models.FloatField(default=0)
    total_credits_used = models.IntegerField(default=0)
    quality_improvement = models.FloatField(default=0)
    brand_compliance_improvement = models.FloatField(default=0)
```

2. **Track AI Batch Performance**:
```python
def track_batch_performance(job: BatchJob):
    """Track performance metrics for AI batch jobs"""
    analytics = BatchJobAnalytics.objects.get_or_create(job=job)[0]
    
    # Calculate metrics
    if job.operation.startswith('ai_'):
        analytics.total_credits_used = calculate_credits_used(job)
        analytics.quality_improvement = calculate_quality_delta(job)
        analytics.save()
```

## API Endpoints

### New Endpoints for AI Batch Processing:

1. **Start AI Batch Job**:
```
POST /api/content/batch-jobs/start-ai/
{
  "assets": ["asset_id_1", "asset_id_2"],
  "operation": "ai_enhance",
  "parameters": {
    "level": "medium",
    "preserve_style": true
  },
  "brand_identity_id": 1
}
```

2. **Get AI Batch Templates**:
```
GET /api/content/batch-jobs/ai-templates/
Response: List of predefined AI batch operations
```

3. **Batch Job Analytics**:
```
GET /api/content/batch-jobs/{id}/analytics/
Response: Performance metrics for completed job
```

## WebSocket Events

### New AI Batch Events:
```javascript
// AI-specific progress updates
{
  "type": "ai_batch_update",
  "job_id": "123",
  "asset_id": "456",
  "stage": "analyzing",  // analyzing, generating, validating, complete
  "progress": 45,
  "preview_url": "https://..."
}
```

## Implementation Timeline

1. **Week 1**: Update models and create AI batch service
2. **Week 2**: Implement Celery tasks for AI operations
3. **Week 3**: Update frontend components and add AI operations
4. **Week 4**: Integrate with AI Asset Library
5. **Week 5**: Add advanced features (brand compliance, variations)
6. **Week 6**: Implement monitoring and analytics

## Testing Strategy

1. **Unit Tests**:
   - Test each AI operation individually
   - Verify parameter validation
   - Check quota consumption

2. **Integration Tests**:
   - Test full batch job flow
   - Verify WebSocket updates
   - Check asset creation/updates

3. **Performance Tests**:
   - Batch processing 100+ assets
   - Monitor memory usage
   - Track API rate limits

## Security Considerations

1. **Quota Enforcement**: Ensure batch operations respect user quotas
2. **Rate Limiting**: Implement per-user batch job limits
3. **Asset Ownership**: Verify user owns all assets in batch
4. **Brand Access**: Check user has access to brand identity

## Error Handling

1. **Partial Failures**: Continue processing other assets
2. **Retry Logic**: Automatic retry for transient failures
3. **Error Reporting**: Detailed error logs per asset
4. **Rollback**: Option to revert batch changes

## Next Steps

1. Create migration for updated BatchJob model
2. Implement AIBatchService
3. Update Celery tasks
4. Enhance frontend BatchProcessor
5. Add comprehensive tests
6. Document API changes