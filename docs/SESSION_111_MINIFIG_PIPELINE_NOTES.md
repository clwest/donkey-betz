# SESSION 111 - MiniFig Pipeline Implementation Notes

**Date:** November 15, 2025
**Goal:** Add Image → 3D Mini-Fig pipeline using existing Creative Pipelines architecture

---

## Current Creative Pipelines Implementation

### Templates
- **Model:** `CreativePipelineTemplate` (`pipelines/models.py`)
- **Fields:**
  - `slug` (CharField, unique) - identifier like `'idea_to_image_set'`
  - `name` (CharField) - human-readable name
  - `description` (TextField) - what the pipeline does
  - `is_active` (BooleanField) - availability flag
  - `config` (JSONField) - stores steps, inputs, outputs configuration

- **Registration:** Created via management command (`seed_pipelines.py`)
  - Uses `update_or_create()` to be idempotent
  - Template config structure:
    ```python
    {
        'steps': [
            {'id': 1, 'name': '...', 'type': 'gpt_expansion', 'tool': '...', 'params': {...}},
            {'id': 2, 'name': '...', 'type': 'image_generation', ...},
            ...
        ],
        'inputs': {
            'idea': {'type': 'string', 'required': True, 'label': 'Describe your idea'},
            'num_images': {'type': 'int', 'default': 5, ...}
        },
        'outputs': {
            'images': {'type': 'array', 'description': '...'}
        }
    }
    ```

### Pipeline Runs
- **Model:** `CreativePipelineRun` (`pipelines/models.py`)
- **Key Fields:**
  - `id` (UUID, primary key)
  - `user` (ForeignKey to User)
  - `template` (ForeignKey to CreativePipelineTemplate)
  - `project`, `session` (ForeignKey, optional)
  - `status` (choices: pending, running, completed, failed)
  - `current_step`, `total_steps` (IntegerField)
  - **`input_payload` (JSONField)** - user inputs
  - **`output_payload` (JSONField)** - results from all steps
  - **`log` (TextField)** - timestamped execution log
  - `error_message` (TextField)
  - `created_at`, `updated_at`, `completed_at`

- **Methods:**
  - `append_log(message)` - add timestamped log entry
  - `mark_running()`, `mark_completed()`, `mark_failed(error_msg)`
  - `update_progress(step_number)`
  - `progress_percentage` - calculated property

### Execution Flow
1. **Start:** `start_pipeline_run(user, template_slug, input_payload, ...)`
   - Creates `CreativePipelineRun` with status='pending'
   - Dispatches to Celery: `run_pipeline_task.delay(str(run.id))`

2. **Execute:** `run_pipeline(run_id)` (`pipelines/services.py`)
   - Marks run as 'running'
   - Loops through `template.config['steps']`
   - For each step, calls executor based on `step['type']`:
     ```python
     if step_type == 'gpt_expansion':
         execute_gpt_expansion_step(run, step)
     elif step_type == 'image_generation':
         execute_image_generation_step(run, step)
     # ...
     ```
   - Marks run as 'completed' or 'failed'

3. **Step Executors:** Functions like `execute_{step_type}_step(run, step)`
   - Read from `run.input_payload` and `run.output_payload`
   - Call external services (OpenAI, Stability AI, etc.)
   - Update `run.output_payload` with results
   - Use `run.append_log()` to document progress

### Existing Step Types
- `gpt_expansion` - Expand idea into prompts (uses OpenAI GPT-4o)
- `image_generation` - Generate images (uses Stability AI)
- `save_assets` - Save to ImageHistory + link to session
- `gpt_script` - Generate video script (uses OpenAI)
- `video_creation` - Create video (placeholder in v1)

### API Endpoints
- `GET /api/v1/pipelines/templates/` - List available templates
- `POST /api/v1/pipelines/runs/` - Create new run
- `GET /api/v1/pipelines/runs/` - List user's runs (with filters)
- `GET /api/v1/pipelines/runs/{id}/` - Get run detail (includes outputs, logs)

### Output Payload Examples
**Idea to Image Set:**
```json
{
  "prompts": [
    "A modern co-working space bathed in natural light...",
    "Close-up shot of a human hand and robotic hand...",
    "Wide-angle view of a futuristic open-plan office..."
  ],
  "images": [
    {"url": "https://...", "prompt": "...", "index": 1},
    {"url": "https://...", "prompt": "...", "index": 2},
    {"url": "https://...", "prompt": "...", "index": 3}
  ]
}
```

---

## MiniFig Pipeline Design

### New Components Needed

#### 1. MiniFigAsset Model (`content/models.py` or new `minifigs/`)
```python
class MiniFigAsset(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    source_pipeline_run = models.ForeignKey(CreativePipelineRun, null=True, on_delete=models.SET_NULL)
    source_image_asset = models.ForeignKey(ImageHistory, null=True, on_delete=models.SET_NULL)

    title = models.CharField(max_length=200)
    provider = models.CharField(max_length=100)  # 'placeholder', 'external_service_x'
    status = models.CharField(choices=STATUS_CHOICES)  # pending, processing, completed, failed

    three_d_file = models.URLField()  # v1: placeholder URL
    preview_image_url = models.URLField(null=True, blank=True)
    metadata = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### 2. Service Layer (`minifigs/services.py` or similar)
```python
def create_minifig_asset_from_images(user, image_asset_ids, pipeline_run=None, provider='placeholder'):
    """
    Create MiniFigAsset records from image assets.

    For v1: Creates placeholder 3D files immediately.
    For v2+: Can dispatch to external 3D generation service.
    """
    # Validate image assets belong to user
    # Create MiniFigAsset for each image
    # For v1: Immediately mark completed with placeholder URLs
    # Return list of created assets
```

#### 3. New Step Executor (`pipelines/services.py`)
```python
def execute_minifig_creation_step(run: CreativePipelineRun, step: Dict):
    """
    Execute mini-fig creation step: Turn images into 3D printable assets.
    """
    # Get image_asset_ids from input_payload
    # Validate images belong to user
    # Call create_minifig_asset_from_images()
    # Update output_payload with minifig_asset_ids
    # Append logs
```

#### 4. New Pipeline Template
```python
{
    'slug': 'images_to_minifigs',
    'name': 'Images → 3D Mini-Figs',
    'description': 'Takes 1-4 character images and generates 3D-printable mini-fig files.',
    'config': {
        'steps': [
            {
                'id': 1,
                'name': 'Validate Images',
                'type': 'validate_images',  # Or skip and do in minifig_creation step
                'params': {'min_images': 1, 'max_images': 4}
            },
            {
                'id': 2,
                'name': 'Create 3D Mini-Figs',
                'type': 'minifig_creation',
                'tool': 'placeholder_3d_provider',  # v1
                'params': {
                    'style': 'toy',  # toy, semi-realistic
                    'scale': 'medium'  # small, medium, large
                }
            }
        ],
        'inputs': {
            'image_asset_ids': {
                'type': 'array',
                'item_type': 'uuid',
                'required': True,
                'min_length': 1,
                'max_length': 4,
                'label': 'Select 1-4 character images'
            },
            'style': {
                'type': 'string',
                'default': 'toy',
                'choices': ['toy', 'semi-realistic'],
                'label': 'Mini-fig style'
            }
        },
        'outputs': {
            'minifig_asset_ids': {
                'type': 'array',
                'description': 'Created MiniFigAsset UUIDs'
            }
        }
    }
}
```

#### 5. Output Payload Structure
```json
{
  "minifig_asset_ids": [
    "uuid-1",
    "uuid-2",
    "uuid-3"
  ]
}
```

### API Endpoints Needed
- `GET /api/v1/minifigs/` - List user's mini-figs (with status filter)
- `GET /api/v1/minifigs/{id}/` - Get mini-fig detail

### Flutter Components Needed
- **Models:** `minifig_asset.dart` (Freezed)
- **API:** `minifigs_api.dart`
- **Providers:** `minifigs_provider.dart`
- **Screens:**
  - `minifigs_screen.dart` - List view
  - `minifig_detail_screen.dart` - Detail + download

---

## Constraints & Decisions

### v1 Scope
1. **Placeholder 3D Files:** Use static/demo STL URLs initially
2. **Immediate Completion:** No async external calls (marks completed immediately)
3. **No Complex Geometry:** Just URL placeholders, not actual 3D generation
4. **Preview Images:** Can use source image or static placeholder

### Future Enhancements (v2+)
1. Integration with real 3D generation service (external API)
2. Async processing with status updates
3. Progress tracking for 3D generation
4. Different file formats (STL, OBJ, 3MF)
5. Customization options (pose, scale, detail level)

### Integration Points
1. **Existing Images:** Use `ImageHistory` model as source
2. **Sessions/Projects:** Link via `CreativePipelineRun`
3. **Logs:** Follow existing `append_log()` pattern
4. **Outputs:** Store in `output_payload` like other pipelines

---

## Implementation Checklist

### Backend
- [ ] Create MiniFigAsset model
- [ ] Create minifigs service layer
- [ ] Add execute_minifig_creation_step() executor
- [ ] Add images_to_minifigs template to seed command
- [ ] Create MiniFigs API endpoints
- [ ] Write backend tests

### Frontend
- [ ] Create minifig_asset.dart Freezed model
- [ ] Create minifigs_api.dart service
- [ ] Create minifigs_provider.dart
- [ ] Create MiniFigsScreen
- [ ] Create MiniFigDetailScreen
- [ ] Add navigation from Donkey Cockpit
- [ ] Write Flutter tests

### Documentation
- [ ] Document golden path flow
- [ ] Add API examples
- [ ] Note TODOs for real 3D provider integration

---

**Phase 0 Complete!** Ready to implement Phase 1.
