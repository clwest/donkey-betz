# Blender Python API (bpy) Integration Guide

**Document Version:** 1.0
**Date:** November 16, 2025
**Author:** Platform Architecture Research
**Status:** Strategic Research & Technical Design

---

## Executive Summary

This document presents a comprehensive analysis of integrating Blender's Python API (bpy) into our AI content creation platform. Blender represents a transformative opportunity to elevate our 3D character pipeline from basic .glb file generation to professional-grade rigged, animated, and rendered 3D assets.

**Current State:**
- Character Images → Replicate TRELLIS → .glb Model → User Downloads
- Cost: $0.038/model, Time: <1 min
- Output: Static 3D models (downloadable, 3D-printable)

**Proposed Enhanced Pipeline:**
- Character Images → TRELLIS → .glb → **Blender Auto-Rigging** → Rigged Character
- Rigged Character → **Blender Animation** → Animated 3D Videos
- Animated Videos → DaVinci Resolve → Final YouTube Content

**Key Opportunities:**
1. **Automated Character Rigging:** Transform static .glb models into animation-ready characters with skeletons
2. **3D Animation Generation:** Create character movements, poses, walk cycles for video content
3. **Professional Rendering:** High-quality 3D renders (Cycles/Eevee) for product visualization
4. **Market Differentiation:** Offer services competitors don't have (rigged characters, animated 3D videos)
5. **Revenue Expansion:** New pricing tiers for rigged models ($20-50) vs static models ($5-10)

**Strategic Fit:**
- ✅ Aligns with "AI content creation" focus (images → videos → 3D animations)
- ✅ Enhances YouTube content workflow (3D character animations in videos)
- ✅ Builds on existing infrastructure (FastAPI services, job queues, Django backend)
- ✅ Free/open-source software (no licensing costs like Maya/Cinema 4D)
- ❌ Requires significant development investment (8-12 weeks for MVP)

**Recommendation:** **PROCEED WITH PHASED IMPLEMENTATION**
- Phase 1 (3 weeks): Basic .glb import + material enhancements
- Phase 2 (4 weeks): Auto-rigging integration with Rigify
- Phase 3 (3 weeks): Animation templates + rendering
- Phase 4 (2 weeks): Full production pipeline

---

## Table of Contents

1. [Blender Python API Fundamentals](#1-blender-python-api-fundamentals)
2. [Integration Architecture](#2-integration-architecture)
3. [Advanced 3D Capabilities](#3-advanced-3d-capabilities)
4. [Use Cases for Our Platform](#4-use-cases-for-our-platform)
5. [Technical Implementation](#5-technical-implementation)
6. [Automation Workflows](#6-automation-workflows)
7. [Performance & Scalability](#7-performance--scalability)
8. [Integration with Existing Features](#8-integration-with-existing-features)
9. [Competitive Advantages](#9-competitive-advantages)
10. [Implementation Roadmap](#10-implementation-roadmap)
11. [Code Examples & Patterns](#11-code-examples--patterns)
12. [Cost Analysis & ROI](#12-cost-analysis--roi)
13. [Risks & Challenges](#13-risks--challenges)
14. [Comparison with Alternatives](#14-comparison-with-alternatives)
15. [Recommendations & Next Steps](#15-recommendations--next-steps)

---

## 1. Blender Python API Fundamentals

### 1.1 What is Blender's Python API (bpy)?

**Blender** is a free and open-source 3D creation suite supporting the entire 3D pipeline: modeling, rigging, animation, simulation, rendering, compositing, motion tracking, and video editing.

**bpy** is Blender's Python API that provides programmatic access to all aspects of Blender functionality. It allows developers to:
- Automate repetitive tasks
- Create custom tools and workflows
- Build production pipelines
- Integrate Blender into larger systems
- Script complex operations impossible through the GUI

**Key Characteristics:**
- **Embedded Python Interpreter:** bpy runs inside Blender's process, not as a standalone library
- **Complete Access:** Control over scenes, objects, materials, rendering, and more
- **Version Compatibility:** Stable API across Blender versions (currently 3.6 LTS, 4.2 latest)
- **Open Source:** MIT-like license, freely modifiable and distributable

### 1.2 Core Modules & Capabilities

The bpy API is organized into several key modules:

#### **bpy.context**
Access to the current context (active object, scene, viewport settings)
```python
import bpy

# Access current scene
scene = bpy.context.scene

# Access selected objects
selected_objects = bpy.context.selected_objects

# Access active object
active_obj = bpy.context.active_object
```

#### **bpy.data**
Access to Blender's internal data (all meshes, materials, textures, etc.)
```python
# Get all meshes
all_meshes = bpy.data.meshes

# Get all materials
all_materials = bpy.data.materials

# Get all images/textures
all_images = bpy.data.images
```

#### **bpy.ops**
Blender operators (actions like import, export, render, modify)
```python
# Import a GLB file
bpy.ops.import_scene.gltf(filepath='/path/to/model.glb')

# Export FBX
bpy.ops.export_scene.fbx(filepath='/path/to/output.fbx')

# Render animation
bpy.ops.render.render(animation=True)
```

#### **bpy.types**
Type definitions for all Blender data structures (Object, Mesh, Material, etc.)
```python
# Object type
obj = bpy.types.Object

# Mesh type
mesh = bpy.types.Mesh

# Material type
mat = bpy.types.Material
```

### 1.3 Headless Operation (No GUI)

**Critical for Server Deployment:** Blender can run headless (background mode) without opening the GUI.

**Command-line Usage:**
```bash
# Run Blender headless with a Python script
blender --background --python script.py

# Run headless and render a .blend file
blender --background file.blend --render-output /tmp/frame_#### --render-anim

# Short form
blender -b file.blend -P script.py
```

**Python Script Example (script.py):**
```python
import bpy

# Load a GLB file
bpy.ops.import_scene.gltf(filepath='/path/to/character.glb')

# Auto-generate rig
obj = bpy.context.selected_objects[0]
bpy.ops.pose.rigify_generate()

# Render to image
bpy.context.scene.render.filepath = '/output/render.png'
bpy.ops.render.render(write_still=True)

# Save as .blend
bpy.ops.wm.save_as_mainfile(filepath='/output/rigged_character.blend')
```

### 1.4 Key Limitations & Considerations

**1. Single Instance Limitation:**
- bpy can only be imported once per Python process
- Global state makes multi-user sessions challenging
- **Solution:** Spawn separate Blender processes per job (subprocess pattern)

**2. Not a Standalone Python Library:**
- bpy requires Blender's binary to run
- Cannot `pip install bpy` and use it anywhere (though bpy wheel builds exist for specific use cases)
- Must invoke Blender executable and pass scripts

**3. Thread Safety:**
- Blender's Python integration is NOT thread-safe
- **Solution:** Use subprocess or multiprocessing, NOT threading

**4. Memory Usage:**
- Blender can use significant RAM for complex scenes (2-8 GB typical)
- **Solution:** Monitor memory, limit concurrent jobs

**5. Version Dependencies:**
- API changes between major versions (2.9x → 3.x → 4.x)
- **Solution:** Pin Blender version, test upgrades thoroughly

### 1.5 Automation Potential

Blender is **exceptionally well-suited** for automation:

**Production Studio Use:**
- Blender Studio (creators of Spring, Charge, etc.) use heavily automated pipelines
- Custom add-ons for asset publishing, character rigging, scene management
- Kitsu integration for project management
- Flamenco for distributed rendering

**Common Automation Patterns:**
1. **Batch Processing:** Import 100 models → apply material → export FBX
2. **Procedural Generation:** Generate variations of a base model
3. **Quality Assurance:** Validate models meet technical requirements
4. **Asset Conversion:** Convert between file formats (GLB → FBX → USD)
5. **Rendering Pipelines:** Batch render thousands of frames across machines

**Why Blender Excels at Automation:**
- Comprehensive Python API covering ALL features
- Command-line support for scripting
- Active community with extensive documentation
- Free/open-source (no licensing barriers)
- Cross-platform (Linux, macOS, Windows)

---

## 2. Integration Architecture

### 2.1 High-Level System Design

**Proposed Architecture:** Blender Render Service (similar to DaVinci Resolve Render Node)

```
┌──────────────────────────────────────────────────────────────────┐
│                    Django Backend (Main Platform)                 │
│                                                                    │
│  ┌────────────────┐    ┌──────────────┐    ┌─────────────────┐  │
│  │ MiniFig Models │───>│ Blender Jobs │───>│ Job Queue       │  │
│  │ (.glb files)   │    │ (DB Table)   │    │ (Redis/Celery)  │  │
│  └────────────────┘    └──────────────┘    └─────────────────┘  │
│                                │                     │            │
└────────────────────────────────┼─────────────────────┼────────────┘
                                 │                     │
                                 │ HTTP POST           │ Job Dispatch
                                 ▼                     ▼
                    ┌─────────────────────────────────────────┐
                    │   Blender Render Service (FastAPI)      │
                    │   Port: 8100 (separate from Resolve)    │
                    │                                          │
                    │  ┌────────────────────────────────────┐ │
                    │  │  Job Receiver & Queue Manager      │ │
                    │  │  - Accept GLB upload               │ │
                    │  │  - Validate inputs                 │ │
                    │  │  - Queue jobs (FIFO)               │ │
                    │  └────────────────────────────────────┘ │
                    │             │                            │
                    │             ▼                            │
                    │  ┌────────────────────────────────────┐ │
                    │  │  Blender Worker Process            │ │
                    │  │  - One active job at a time (MVP)  │ │
                    │  │  - Spawn subprocess per job        │ │
                    │  │  - Monitor progress                │ │
                    │  └────────────────────────────────────┘ │
                    │             │                            │
                    │             ▼                            │
                    │  ┌────────────────────────────────────┐ │
                    │  │  Blender Subprocess (headless)     │ │
                    │  │  blender -b --python script.py     │ │
                    │  │                                    │ │
                    │  │  Operations:                       │ │
                    │  │  1. Import GLB                     │ │
                    │  │  2. Auto-rig (Rigify)              │ │
                    │  │  3. Apply materials                │ │
                    │  │  4. Export rigged FBX/BLEND        │ │
                    │  │  5. Render preview images/video    │ │
                    │  └────────────────────────────────────┘ │
                    │             │                            │
                    │             ▼                            │
                    │  ┌────────────────────────────────────┐ │
                    │  │  Result Upload                     │ │
                    │  │  - POST results to Django          │ │
                    │  │  - Upload files (FBX, images)      │ │
                    │  │  - Update job status               │ │
                    │  └────────────────────────────────────┘ │
                    └─────────────────────────────────────────┘
                                 │
                                 │ Results
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│                    Django Backend (Update)                        │
│                                                                    │
│  ┌────────────────┐    ┌──────────────┐    ┌─────────────────┐  │
│  │ MiniFigAsset   │<───│ Webhook      │<───│ Blender Service │  │
│  │ .three_d_file  │    │ /blender/    │    │ Results         │  │
│  │ = rigged.fbx   │    │ callback/    │    │                 │  │
│  └────────────────┘    └──────────────┘    └─────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### 2.2 Service Architecture Patterns

**Pattern 1: Subprocess-Based Workers (Recommended for MVP)**
- FastAPI service spawns Blender subprocess per job
- One job at a time (serial processing)
- Simple error handling and recovery
- Similar to DaVinci Resolve render node pattern

**Pattern 2: Multi-Instance Workers (Future Scaling)**
- Multiple FastAPI instances on different ports
- Each instance handles one concurrent Blender job
- Load balancer distributes jobs across instances
- Better resource utilization

**Pattern 3: Distributed Render Farm (Advanced)**
- RabbitMQ message queue for job distribution
- Multiple worker machines (macOS, Linux)
- Centralized file server (NFS, S3)
- Production-grade scalability

**MVP Recommendation:** Start with Pattern 1 (subprocess-based), migrate to Pattern 2 when scaling needed.

### 2.3 File Management Strategy

**Input Files (.glb from TRELLIS):**
```
/media/minifig_assets/
  ├── glb/
  │   ├── <uuid>.glb          # Original TRELLIS output
  │   └── <uuid>_meta.json    # Metadata
```

**Blender Working Directory:**
```
/var/blender_workspace/
  ├── jobs/
  │   ├── <job_id>/
  │   │   ├── input/          # Downloaded GLB
  │   │   ├── working/        # .blend files
  │   │   ├── output/         # FBX, renders
  │   │   └── logs/           # Process logs
```

**Output Files (uploaded to Django):**
```
/media/minifig_assets/
  ├── rigged/
  │   ├── <uuid>.fbx          # Rigged character (FBX)
  │   ├── <uuid>.blend        # Blender source file
  │   ├── <uuid>_preview.png  # Preview render
  │   └── <uuid>_turntable.mp4 # Animated turntable
```

### 2.4 Authentication & Security

**Token-Based Auth (similar to Resolve Node):**
```python
# FastAPI endpoint
@app.post("/api/v1/blender/jobs/")
async def create_job(
    job_data: BlenderJobRequest,
    token: str = Header(..., alias="X-Blender-Token")
):
    if token != settings.BLENDER_SERVICE_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Process job...
```

**Environment Variables:**
```bash
# .env
BLENDER_SERVICE_URL=http://localhost:8100
BLENDER_SERVICE_TOKEN=<secure_random_token>
BLENDER_EXECUTABLE_PATH=/Applications/Blender.app/Contents/MacOS/Blender
BLENDER_MAX_JOBS=1  # MVP: single job at a time
```

### 2.5 Job Status & Progress Tracking

**Job States:**
1. `queued` - Job accepted, waiting for worker
2. `processing` - Blender subprocess running
3. `uploading` - Results being uploaded to Django
4. `completed` - Success, files available
5. `failed` - Error occurred, check logs

**Progress Updates:**
```python
# Blender script writes progress to file
# FastAPI service polls and updates Django
{
    "job_id": "abc-123",
    "status": "processing",
    "progress": 45,  # 0-100%
    "stage": "Auto-rigging character",
    "elapsed_seconds": 23,
    "estimated_remaining_seconds": 28
}
```

---

## 3. Advanced 3D Capabilities

### 3.1 Character Rigging

**What is Rigging?**
Adding a skeleton (armature) to a 3D model so it can be animated. Bones define how the mesh deforms when moved.

**Blender's Rigify Add-on:**
- Automatic rigging system built into Blender
- Generates production-ready character rigs from simple meta-rigs
- Supports bipeds, quadrupeds, faces, hands
- Customizable rig types

**Use Case for Our Platform:**
- Input: Static .glb character from TRELLIS
- Process: Auto-detect humanoid structure → Generate Rigify rig
- Output: Fully rigged character ready for animation

**Value Add:**
- Manual rigging takes 2-8 hours for professionals
- Automated rigging: 1-3 minutes
- Rigged characters sell for 3-10x more than static models

### 3.2 Animation

**Animation Capabilities:**
1. **Keyframe Animation:** Define poses at specific frames
2. **Animation Templates:** Pre-built walk cycles, idle poses, gestures
3. **NLA (Non-Linear Animation):** Mix and blend animation clips
4. **Physics Simulation:** Cloth, hair, rigid body dynamics

**Practical Applications:**
- **Turntable Animations:** 360° rotating view for product pages
- **Character Animations:** Walk, run, jump for game assets or videos
- **Pose Libraries:** Generate multiple character poses from one model
- **Video Content:** Animated 3D characters in YouTube videos

**Example Workflow:**
```
Rigged Character → Apply "Walk Cycle" Template → Render 5-second Video → DaVinci
```

### 3.3 Materials & Textures (PBR)

**PBR (Physically Based Rendering):**
Modern material system that simulates real-world light interaction.

**Components:**
- **Base Color:** The main color/texture
- **Metallic:** How metal-like the surface is
- **Roughness:** How shiny vs matte
- **Normal Map:** Surface detail (bumps, grooves)
- **Ambient Occlusion:** Shadow detail in crevices

**Blender's Material System:**
- Shader nodes for complex materials
- Principled BSDF (one shader for all PBR materials)
- Automatic PBR texture import from image sets

**Use Case:**
- TRELLIS .glb models have basic materials
- Blender can enhance: add roughness, normal maps, better textures
- Result: More professional-looking 3D models

### 3.4 Lighting & Rendering

**Render Engines:**

**1. Eevee (Real-time)**
- Fast rendering (seconds per frame)
- Good for previews, animations, stylized work
- 3-12x faster than Cycles
- Less photorealistic

**2. Cycles (Path-tracing)**
- Photorealistic rendering
- Slower (minutes per frame)
- Accurate lighting, reflections, shadows
- Best for product visualization, hero shots

**Lighting Types:**
- **HDRI (Environment Maps):** 360° image-based lighting
- **Studio Lighting:** 3-point lighting (key, fill, rim)
- **Procedural Sky:** Automatic sky and sun

**Use Case:**
- Quick Preview: Eevee render in 10 seconds
- Final Product Image: Cycles render in 2-5 minutes
- Turntable Video: Eevee 120 frames @ 30fps = ~4 seconds render time

### 3.5 UV Unwrapping

**What is UV Unwrapping?**
Flattening a 3D model's surface into a 2D texture space so textures can be painted/applied.

**Why It Matters:**
- TRELLIS models may have automatic UVs
- Manual UV unwrapping optimizes texture usage
- Better UVs = sharper, more efficient textures

**Blender Capabilities:**
- Automatic UV unwrapping (Smart UV Project)
- Manual UV editing
- UV seam detection
- Texture baking

**Use Case:**
- Re-unwrap TRELLIS models for optimal texturing
- Bake enhanced PBR textures
- Create texture atlases for game engines

### 3.6 Modifiers (Non-Destructive Editing)

**Blender Modifiers:**
Non-destructive operations that change mesh appearance without editing geometry.

**Common Modifiers:**
- **Subdivision Surface:** Smooth low-poly models
- **Mirror:** Create symmetric models
- **Array:** Duplicate objects in patterns
- **Boolean:** Combine/subtract meshes
- **Solidify:** Add thickness to surfaces
- **Decimate:** Reduce polygon count (optimization)

**Use Case:**
- Smooth TRELLIS models with subdivision
- Reduce polygon count for web/mobile with decimate
- Add accessories (hats, weapons) with boolean operations

### 3.7 Physics Simulation

**Simulation Types:**
1. **Cloth Simulation:** Realistic fabric movement
2. **Hair/Fur:** Particle-based hair systems
3. **Rigid Body:** Objects colliding, falling
4. **Fluid Simulation:** Water, smoke

**Use Case (Advanced):**
- Cloth simulation for character clothing
- Hair simulation for realistic hair movement
- Physics-based animations (character falling, objects tumbling)

**Note:** Physics simulations are computationally expensive (may not be MVP priority).

---

## 4. Use Cases for Our Platform

### 4.1 Use Case 1: Auto-Rigged Character Generation

**Scenario:**
User generates a character image → TRELLIS creates 3D model → Blender auto-rigs it

**Workflow:**
```
1. User: Generate character image via Stability AI
2. Platform: Convert image → 3D model via TRELLIS ($0.038, <1 min)
3. Platform: Download .glb → Send to Blender Service
4. Blender: Import .glb → Auto-rig with Rigify → Export .fbx
5. Platform: Store rigged .fbx → Notify user
6. User: Download rigged character for animation software
```

**Benefits:**
- Rigged characters worth 3-10x more than static models
- Enables animation (walk cycles, poses)
- Marketplace differentiation (few competitors offer this)

**Revenue Potential:**
- Static .glb: $5-10/model
- Rigged .fbx: $20-50/model
- Markup: 4-5x increase

**Implementation Complexity:** Medium (Phase 2)
- Rigify integration: 2 weeks
- Testing with various character types: 1 week
- UI for rigged downloads: 1 week

### 4.2 Use Case 2: Batch Rigging Service

**Scenario:**
Power users need 10-100 characters rigged for a game or animation project

**Workflow:**
```
1. User uploads: 10 .glb character files
2. Platform: Creates 10 Blender jobs → Queue
3. Blender Service: Processes one at a time (or parallel with multiple workers)
4. Platform: Notifies user when all 10 are complete
5. User: Bulk download rigged characters
```

**Benefits:**
- Serves game developers, animation studios
- Higher-value customers (B2B potential)
- Automated pipeline saves weeks of manual work

**Revenue Potential:**
- Pricing: $15/character (bulk discount from $20 single)
- 10 characters = $150/job
- 100 characters = $1,200/job (12% discount for scale)

**Implementation Complexity:** Medium (Phase 2 + Queue Optimization)
- Batch job queue: 1 week
- Parallel processing (multiple workers): 2 weeks
- Bulk download UI: 1 week

### 4.3 Use Case 3: 3D Character Animation for YouTube Videos

**Scenario:**
User wants animated 3D characters in YouTube videos (tutorials, story videos, mascots)

**Workflow:**
```
1. User: Generate character → Rig → Request "Walk Cycle" animation
2. Blender: Apply walk cycle template → Render 5-second video
3. Platform: Send rendered video to DaVinci Resolve
4. DaVinci: Composite 3D character over live-action footage
5. Output: YouTube video with animated 3D character
```

**Benefits:**
- Unique content creation (3D animated mascots)
- Enhances existing YouTube workflow
- No need for professional animators

**Revenue Potential:**
- Animation templates: $10-25/animation
- Custom animations: $50-200/animation
- Subscription model: $50/mo for unlimited templates

**Implementation Complexity:** High (Phase 3)
- Animation template library: 3 weeks
- Rendering pipeline: 2 weeks
- DaVinci integration: 1 week

### 4.4 Use Case 4: Product Visualization (E-commerce)

**Scenario:**
E-commerce businesses need 3D product renders (turntable videos, hero shots)

**Workflow:**
```
1. User: Upload product .glb model (or generate from images)
2. Platform: Send to Blender → Apply studio lighting + materials
3. Blender: Render turntable animation (360° rotating view)
4. Platform: Render hero shot (high-quality product image)
5. User: Download for website/Amazon listings
```

**Benefits:**
- Professional product visuals without photographer
- Turntable videos increase conversion rates 30-40%
- Repeatable process (same lighting for all products)

**Revenue Potential:**
- Turntable video: $20-40/product
- Hero shot renders: $15-30/set (4 angles)
- B2B contracts: $500-2000/month for ongoing products

**Implementation Complexity:** Medium (Phase 3)
- Lighting presets: 1 week
- Material enhancement: 2 weeks
- Turntable automation: 1 week

### 4.5 Use Case 5: Multi-Character Scene Composition

**Scenario:**
User wants multiple characters in one scene (group shot, battle scene, team photo)

**Workflow:**
```
1. User: Select 3 rigged characters from library
2. User: Choose scene template ("Battle Arena", "Office", "Forest")
3. Blender: Import characters + scene → Position characters → Apply poses
4. Blender: Render final scene (still image or animation)
5. User: Download scene for video, marketing, etc.
```

**Benefits:**
- Complex scenes without 3D software knowledge
- Template-based (easy for non-technical users)
- Unique storytelling capability

**Revenue Potential:**
- Scene renders: $30-60/scene
- Custom scenes: $100-300/scene
- Agency partnerships: $1000-5000/project

**Implementation Complexity:** High (Phase 4)
- Scene template library: 3 weeks
- Character positioning logic: 2 weeks
- Pose library: 2 weeks

---

## 5. Technical Implementation

### 5.1 Blender Service Architecture (FastAPI)

**Directory Structure:**
```
blender_service/
├── main.py                    # FastAPI application
├── config.py                  # Configuration & settings
├── models.py                  # Pydantic models
├── worker.py                  # Blender job worker
├── blender_scripts/           # Python scripts for Blender
│   ├── import_glb.py
│   ├── auto_rig.py
│   ├── apply_materials.py
│   ├── render_turntable.py
│   └── export_fbx.py
├── templates/                 # Animation/scene templates
│   ├── animations/
│   │   ├── walk_cycle.blend
│   │   └── idle_pose.blend
│   └── scenes/
│       ├── studio_lighting.blend
│       └── outdoor_scene.blend
├── jobs/                      # Job data (created at runtime)
│   └── <job_id>/
├── logs/                      # Service logs
└── requirements.txt
```

**FastAPI Endpoints:**
```python
# main.py
from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from pydantic import BaseModel
import uuid

app = FastAPI(title="Blender Render Service", version="1.0.0")

class BlenderJobRequest(BaseModel):
    operation: str  # "auto_rig", "render_turntable", "apply_animation"
    input_glb_url: str  # URL to download .glb
    callback_url: str  # Django webhook for results
    parameters: dict  # Operation-specific params

class BlenderJobResponse(BaseModel):
    job_id: str
    status: str
    message: str

@app.post("/api/v1/jobs/", response_model=BlenderJobResponse)
async def create_job(
    job: BlenderJobRequest,
    token: str = Header(..., alias="X-Blender-Token")
):
    """Create a new Blender processing job"""

    # Validate token
    if token != settings.BLENDER_SERVICE_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Create job
    job_id = str(uuid.uuid4())

    # Queue job
    await job_queue.enqueue(job_id, job)

    return BlenderJobResponse(
        job_id=job_id,
        status="queued",
        message="Job queued for processing"
    )

@app.get("/api/v1/jobs/{job_id}/")
async def get_job_status(job_id: str):
    """Get status of a Blender job"""
    job = await job_queue.get_job(job_id)
    return job

@app.post("/api/v1/jobs/{job_id}/cancel/")
async def cancel_job(job_id: str):
    """Cancel a running job"""
    await job_queue.cancel(job_id)
    return {"status": "cancelled"}

@app.get("/health/")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "blender_version": get_blender_version(),
        "active_jobs": await job_queue.active_count()
    }
```

### 5.2 Job Worker Implementation

**worker.py:**
```python
import subprocess
import os
import json
import asyncio
from pathlib import Path

class BlenderWorker:
    def __init__(self, blender_path: str, workspace: str):
        self.blender_path = blender_path
        self.workspace = Path(workspace)

    async def process_job(self, job_id: str, job_data: dict):
        """Process a Blender job"""

        # Create job directory
        job_dir = self.workspace / job_id
        job_dir.mkdir(parents=True, exist_ok=True)

        input_dir = job_dir / "input"
        output_dir = job_dir / "output"
        logs_dir = job_dir / "logs"

        for d in [input_dir, output_dir, logs_dir]:
            d.mkdir(exist_ok=True)

        try:
            # Download input .glb file
            glb_path = await self.download_glb(
                job_data['input_glb_url'],
                input_dir / "input.glb"
            )

            # Select operation
            operation = job_data['operation']

            if operation == "auto_rig":
                result = await self.auto_rig(job_id, glb_path, output_dir)
            elif operation == "render_turntable":
                result = await self.render_turntable(job_id, glb_path, output_dir)
            elif operation == "apply_animation":
                result = await self.apply_animation(job_id, glb_path, output_dir, job_data['parameters'])
            else:
                raise ValueError(f"Unknown operation: {operation}")

            # Upload results to Django
            await self.upload_results(job_id, result, job_data['callback_url'])

            return result

        except Exception as e:
            # Log error and update job status
            await self.report_error(job_id, str(e), job_data['callback_url'])
            raise

    async def auto_rig(self, job_id: str, glb_path: Path, output_dir: Path):
        """Auto-rig a character using Rigify"""

        script_path = Path(__file__).parent / "blender_scripts" / "auto_rig.py"

        # Prepare script arguments
        script_args = json.dumps({
            'input_glb': str(glb_path),
            'output_fbx': str(output_dir / "rigged.fbx"),
            'output_blend': str(output_dir / "rigged.blend"),
            'preview_render': str(output_dir / "preview.png"),
            'job_id': job_id
        })

        # Run Blender headless
        cmd = [
            self.blender_path,
            '--background',
            '--python', str(script_path),
            '--',  # Everything after this goes to the script
            script_args
        ]

        # Execute subprocess
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise RuntimeError(f"Blender process failed: {stderr.decode()}")

        # Parse result
        result = {
            'status': 'completed',
            'files': {
                'rigged_fbx': str(output_dir / "rigged.fbx"),
                'rigged_blend': str(output_dir / "rigged.blend"),
                'preview_image': str(output_dir / "preview.png")
            },
            'logs': stdout.decode()
        }

        return result

    async def download_glb(self, url: str, dest: Path):
        """Download GLB file from URL or copy from local path"""
        import aiohttp

        if url.startswith('http://') or url.startswith('https://'):
            # Download from URL
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    content = await response.read()
                    dest.write_bytes(content)
        else:
            # Copy from local filesystem
            import shutil
            shutil.copy(url, dest)

        return dest

    async def upload_results(self, job_id: str, result: dict, callback_url: str):
        """Upload results to Django backend"""
        import aiohttp

        async with aiohttp.ClientSession() as session:
            # Upload each file
            files_uploaded = {}

            for file_key, file_path in result['files'].items():
                form = aiohttp.FormData()
                form.add_field('file',
                              open(file_path, 'rb'),
                              filename=Path(file_path).name)
                form.add_field('job_id', job_id)
                form.add_field('file_type', file_key)

                async with session.post(f"{callback_url}/upload/", data=form) as resp:
                    resp_data = await resp.json()
                    files_uploaded[file_key] = resp_data['url']

            # Update job status
            status_data = {
                'job_id': job_id,
                'status': 'completed',
                'files': files_uploaded,
                'logs': result['logs']
            }

            async with session.post(f"{callback_url}/status/", json=status_data) as resp:
                return await resp.json()
```

### 5.3 Blender Python Script (auto_rig.py)

**blender_scripts/auto_rig.py:**
```python
import bpy
import sys
import json
from pathlib import Path

def auto_rig_character(args):
    """Auto-rig a character from GLB file"""

    print(f"🔧 Starting auto-rig process...")
    print(f"   Input: {args['input_glb']}")
    print(f"   Output FBX: {args['output_fbx']}")

    # Clear existing scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Import GLB
    print(f"📥 Importing GLB...")
    bpy.ops.import_scene.gltf(filepath=args['input_glb'])

    # Select imported mesh
    mesh_obj = bpy.context.selected_objects[0]
    bpy.context.view_layer.objects.active = mesh_obj

    print(f"✅ Imported: {mesh_obj.name}")

    # Auto-generate Rigify rig
    print(f"🦴 Generating Rigify rig...")

    # Add Rigify meta-rig (human)
    bpy.ops.object.armature_human_metarig_add()

    metarig = bpy.context.selected_objects[0]

    # Scale meta-rig to match character
    # (In production, would auto-detect character proportions)
    metarig.scale = (1.0, 1.0, 1.0)

    # Generate rig
    bpy.context.view_layer.objects.active = metarig
    bpy.ops.pose.rigify_generate()

    rig = None
    for obj in bpy.context.selected_objects:
        if obj.type == 'ARMATURE' and obj != metarig:
            rig = obj
            break

    if not rig:
        raise RuntimeError("Rigify failed to generate rig")

    print(f"✅ Rig generated: {rig.name}")

    # Parent mesh to rig with automatic weights
    print(f"🔗 Parenting mesh to rig...")
    bpy.ops.object.select_all(action='DESELECT')
    mesh_obj.select_set(True)
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')

    print(f"✅ Mesh parented with automatic weights")

    # Export as FBX
    print(f"💾 Exporting FBX...")
    bpy.ops.export_scene.fbx(
        filepath=args['output_fbx'],
        use_selection=False,
        bake_anim=False
    )

    print(f"✅ FBX exported")

    # Save .blend file
    print(f"💾 Saving Blender file...")
    bpy.ops.wm.save_as_mainfile(filepath=args['output_blend'])

    print(f"✅ Blend file saved")

    # Render preview image
    print(f"🎨 Rendering preview...")

    # Set up camera
    bpy.ops.object.camera_add(location=(5, -5, 3))
    camera = bpy.context.active_object
    camera.rotation_euler = (1.1, 0, 0.785)
    bpy.context.scene.camera = camera

    # Set up lighting
    bpy.ops.object.light_add(type='SUN', location=(10, 10, 10))

    # Render settings
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'  # Fast preview
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024
    scene.render.filepath = args['preview_render']

    # Render
    bpy.ops.render.render(write_still=True)

    print(f"✅ Preview rendered")
    print(f"🎉 Auto-rig complete!")

if __name__ == "__main__":
    # Arguments passed after '--'
    args_json = sys.argv[sys.argv.index('--') + 1]
    args = json.loads(args_json)

    try:
        auto_rig_character(args)
    except Exception as e:
        print(f"❌ ERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)
```

### 5.4 Django Integration

**Django Models (content/models.py):**
```python
from django.db import models
import uuid

class BlenderJob(models.Model):
    """Blender processing job"""

    JOB_OPERATIONS = [
        ('auto_rig', 'Auto-Rig Character'),
        ('render_turntable', 'Render Turntable'),
        ('apply_animation', 'Apply Animation'),
        ('enhance_materials', 'Enhance Materials'),
    ]

    JOB_STATUSES = [
        ('queued', 'Queued'),
        ('processing', 'Processing'),
        ('uploading', 'Uploading Results'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    # Job configuration
    operation = models.CharField(max_length=50, choices=JOB_OPERATIONS)
    minifig_asset = models.ForeignKey('MiniFigAsset', on_delete=models.CASCADE, null=True, blank=True)
    input_glb_url = models.TextField()  # URL or file path
    parameters = models.JSONField(default=dict)

    # Status tracking
    status = models.CharField(max_length=20, choices=JOB_STATUSES, default='queued')
    progress = models.IntegerField(default=0)  # 0-100
    current_stage = models.CharField(max_length=200, blank=True)

    # Results
    output_files = models.JSONField(default=dict)  # {file_type: url}
    logs = models.TextField(blank=True)
    error_message = models.TextField(blank=True)

    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"BlenderJob {self.id} - {self.operation} ({self.status})"
```

**Django Service (content/blender_service.py):**
```python
import requests
from django.conf import settings
from content.models import BlenderJob, MiniFigAsset

def submit_blender_job(
    user,
    minifig_asset: MiniFigAsset,
    operation: str,
    parameters: dict = None
) -> BlenderJob:
    """Submit a job to Blender Render Service"""

    # Create job record
    job = BlenderJob.objects.create(
        user=user,
        operation=operation,
        minifig_asset=minifig_asset,
        input_glb_url=minifig_asset.three_d_file.url,  # Assuming .glb file
        parameters=parameters or {},
        status='queued'
    )

    # Submit to Blender service
    callback_url = f"{settings.SITE_URL}/api/blender/callback/{job.id}/"

    payload = {
        'operation': operation,
        'input_glb_url': job.input_glb_url,
        'callback_url': callback_url,
        'parameters': job.parameters
    }

    headers = {
        'X-Blender-Token': settings.BLENDER_SERVICE_TOKEN
    }

    response = requests.post(
        f"{settings.BLENDER_SERVICE_URL}/api/v1/jobs/",
        json=payload,
        headers=headers
    )

    response.raise_for_status()

    return job

def check_blender_job_status(job: BlenderJob):
    """Check status of a Blender job"""

    headers = {
        'X-Blender-Token': settings.BLENDER_SERVICE_TOKEN
    }

    response = requests.get(
        f"{settings.BLENDER_SERVICE_URL}/api/v1/jobs/{job.id}/",
        headers=headers
    )

    response.raise_for_status()
    data = response.json()

    # Update job
    job.status = data['status']
    job.progress = data.get('progress', 0)
    job.current_stage = data.get('stage', '')
    job.save()

    return data
```

**Django Webhook View (pipelines/views.py):**
```python
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from content.models import BlenderJob
import json

@csrf_exempt
@require_POST
def blender_callback_upload(request, job_id):
    """Receive file upload from Blender service"""

    job = BlenderJob.objects.get(id=job_id)

    # Save uploaded file
    file = request.FILES['file']
    file_type = request.POST['file_type']

    # Store in media
    from django.core.files.storage import default_storage
    file_path = default_storage.save(f'blender_results/{job_id}/{file.name}', file)
    file_url = default_storage.url(file_path)

    # Update job
    if not job.output_files:
        job.output_files = {}
    job.output_files[file_type] = file_url
    job.save()

    return JsonResponse({'status': 'uploaded', 'url': file_url})

@csrf_exempt
@require_POST
def blender_callback_status(request, job_id):
    """Receive status update from Blender service"""

    job = BlenderJob.objects.get(id=job_id)
    data = json.loads(request.body)

    job.status = data['status']
    job.output_files = data.get('files', {})
    job.logs = data.get('logs', '')

    if data['status'] == 'completed':
        from django.utils import timezone
        job.completed_at = timezone.now()
        if job.started_at:
            job.duration_seconds = int((job.completed_at - job.started_at).total_seconds())

    job.save()

    # Update MiniFigAsset if applicable
    if job.minifig_asset and data['status'] == 'completed':
        minifig = job.minifig_asset

        # If this was an auto-rig job, store the rigged file
        if job.operation == 'auto_rig' and 'rigged_fbx' in job.output_files:
            minifig.rigged_file = job.output_files['rigged_fbx']
            minifig.rigged_file_format = 'fbx'
            minifig.status = 'rigged'
            minifig.save()

    return JsonResponse({'status': 'updated'})
```

---

## 6. Automation Workflows

### 6.1 Workflow 1: Character Creation → Auto-Rig Pipeline

**End-to-End Flow:**
```
User Action: "Create rigged character from my image"
  ↓
[Platform] Generate character image (Stability AI)
  ↓ (1024x1024 PNG, 3 seconds)
[Platform] Convert image → 3D model (TRELLIS)
  ↓ (.glb file, $0.038, 45 seconds)
[Platform] Submit Blender job (auto_rig)
  ↓ (Django creates BlenderJob record)
[Blender Service] Download .glb
  ↓ (5 seconds)
[Blender] Import .glb → Auto-rig with Rigify → Export .fbx
  ↓ (Subprocess: 60-120 seconds)
[Blender Service] Upload results to Django
  ↓ (.fbx, .blend, preview.png)
[Platform] Update MiniFigAsset (status: rigged)
  ↓
[Platform] Notify user (email, WebSocket)
  ↓
User Action: Download rigged character (.fbx)
```

**Total Time:** ~2-3 minutes
**Total Cost:** $0.038 (TRELLIS) + server compute (~$0.02)
**User Experience:** Seamless automated pipeline

### 6.2 Workflow 2: Batch Character Rigging

**Scenario:** User has 20 characters to rig

**Flow:**
```
User uploads: 20 .glb files
  ↓
[Platform] Create 20 BlenderJob records (status: queued)
  ↓
[Platform] Notify user: "Batch job started (20 characters)"
  ↓
[Blender Service] Process jobs sequentially (FIFO queue)
  ↓ Job 1: rig → upload → complete (2 min)
  ↓ Job 2: rig → upload → complete (2 min)
  ↓ ... (repeat for all 20)
  ↓ Job 20: rig → upload → complete (2 min)
  ↓
[Platform] All jobs complete (40 minutes elapsed)
  ↓
[Platform] Notify user: "Batch complete - 20 characters rigged"
  ↓
User downloads: Bulk .zip with all 20 rigged .fbx files
```

**Total Time:** ~40 minutes (serial processing with 1 worker)
**Optimization:** With 4 parallel workers → 10 minutes
**User Experience:** Set it and forget it

### 6.3 Workflow 3: Animated Turntable for Product Pages

**Scenario:** E-commerce product needs 360° turntable video

**Flow:**
```
User uploads: Product .glb model
  ↓
[Platform] Submit Blender job (render_turntable)
  ↓
[Blender] Import .glb → Apply studio lighting → Position camera
  ↓
[Blender] Animate camera (360° rotation, 120 frames @ 30fps = 4 sec video)
  ↓
[Blender] Render with Eevee (fast real-time)
  ↓ (120 frames × 0.5 sec/frame = 60 seconds render time)
[Blender] Encode frames → .mp4 video (ffmpeg)
  ↓
[Blender Service] Upload turntable.mp4 to Django
  ↓
[Platform] Update product record with turntable URL
  ↓
User embeds: <video> turntable on product page
```

**Total Time:** ~2 minutes
**User Experience:** One-click turntable generation

### 6.4 Workflow 4: YouTube Video with Animated 3D Character

**Scenario:** Tutorial video with animated mascot

**Flow:**
```
User: "Create tutorial with animated character"
  ↓
[Platform] User selects character + animation (walk cycle)
  ↓
[Platform] Submit Blender job (apply_animation)
  ↓ parameters: {animation: "walk_cycle", duration: 5}
[Blender] Import character .glb → Import animation template
  ↓
[Blender] Apply animation → Render frames (Eevee)
  ↓ (150 frames × 0.3 sec/frame = 45 seconds)
[Blender] Encode → animated_character.mp4
  ↓
[Blender Service] Upload to Django
  ↓
[Platform] Send to DaVinci Resolve pipeline
  ↓
[DaVinci] Composite animated character over tutorial footage
  ↓
[DaVinci] Render final video
  ↓
User publishes: YouTube video with animated mascot
```

**Total Time:** ~3-5 minutes (Blender) + DaVinci time
**User Experience:** Professional animated content

### 6.5 Workflow 5: Error Handling & Retry

**Scenario:** Blender job fails (corrupted .glb, rig generation error)

**Flow:**
```
[Blender] Job fails during auto-rig
  ↓ (Exception caught)
[Blender Service] Update job status: failed
  ↓
[Blender Service] POST error to Django webhook
  ↓
[Platform] BlenderJob.status = 'failed'
  ↓
[Platform] BlenderJob.error_message = "Rigify failed: Character has no armature"
  ↓
[Platform] Notify user: "Rig generation failed - Model may need manual adjustment"
  ↓
User action: Contact support OR re-upload better .glb
  ↓ (Optional)
[Platform] Retry job with adjusted parameters
```

**Error Categories:**
1. **Input Errors:** Corrupted .glb, unsupported format
2. **Processing Errors:** Rigify fails, mesh topology issues
3. **System Errors:** Blender crash, out of memory
4. **Timeout Errors:** Job exceeds max duration (5 min)

**Retry Strategy:**
- Automatic retry: System errors (1 retry)
- Manual retry: Input/processing errors (user adjusts)
- No retry: Timeout (job cancelled)

---

## 7. Performance & Scalability

### 7.1 Render Time Benchmarks

**Operation: Auto-Rig Character**
- Import .glb: 2-5 seconds
- Generate Rigify rig: 15-30 seconds
- Parent mesh with weights: 10-20 seconds
- Export .fbx: 5-10 seconds
- Render preview (Eevee): 3-5 seconds
- **Total:** 35-70 seconds

**Operation: Render Turntable (120 frames)**
- Setup scene: 5 seconds
- Render with Eevee: 0.3-0.5 sec/frame → 36-60 seconds
- Encode video (ffmpeg): 5-10 seconds
- **Total:** 46-75 seconds

**Operation: Apply Animation (5 seconds @ 30fps = 150 frames)**
- Load animation template: 5 seconds
- Apply to character: 10 seconds
- Render with Eevee: 0.3 sec/frame → 45 seconds
- Encode video: 5 seconds
- **Total:** 65 seconds

**Operation: High-Quality Product Render (Cycles, 1 image)**
- Setup lighting: 5 seconds
- Render with Cycles (4K, 128 samples): 120-300 seconds
- **Total:** 125-305 seconds (2-5 minutes)

### 7.2 Resource Requirements

**Per Job:**
- **CPU:** 4-8 cores (100% utilization during render)
- **RAM:** 2-6 GB (depends on model complexity)
- **Disk:** 500 MB - 2 GB working space
- **Duration:** 1-5 minutes typical

**Server Specs (Single Worker):**
- **Mac Mini M2 Pro:**
  - CPU: 10-core (6P + 4E)
  - RAM: 16 GB
  - Disk: 256 GB SSD
  - Concurrent jobs: 1-2
  - **Cost:** $1,299 (one-time)

- **Linux Server (Cloud):**
  - CPU: 8 vCPUs
  - RAM: 16 GB
  - GPU: Optional (NVIDIA RTX for Cycles)
  - Concurrent jobs: 2-3
  - **Cost:** $100-150/month (AWS, DigitalOcean)

**Multi-Worker Scaling:**
- 1 worker: 1 job at a time, ~30 jobs/hour
- 4 workers: 4 concurrent jobs, ~120 jobs/hour
- 10 workers: 10 concurrent jobs, ~300 jobs/hour

### 7.3 Cycles vs Eevee Performance

**Eevee (Real-time Rasterization):**
- Frame time: 0.1-0.5 seconds
- Use cases: Animations, turntables, previews
- Quality: Good for stylized/cartoonish work
- **3-12x faster than Cycles**

**Cycles (Path-tracing):**
- Frame time: 30-300 seconds
- Use cases: Product photos, hero shots, photorealistic renders
- Quality: Photorealistic, accurate lighting
- **Best for single images, not animations**

**Decision Matrix:**
| Use Case | Engine | Frame Time | Quality | Best For |
|----------|--------|------------|---------|----------|
| Preview render | Eevee | 3 sec | Medium | Quick feedback |
| Turntable video | Eevee | 0.3 sec | Medium | Product pages |
| Character animation | Eevee | 0.4 sec | Medium | YouTube videos |
| Product hero shot | Cycles | 120 sec | High | Marketing materials |
| Architectural viz | Cycles | 300 sec | Photorealistic | Client presentations |

### 7.4 Concurrent Job Handling

**MVP Strategy (Single Worker):**
```python
# Simple FIFO queue
job_queue = []

async def worker():
    while True:
        if job_queue:
            job = job_queue.pop(0)
            await process_job(job)
        else:
            await asyncio.sleep(1)
```

**Scaling Strategy (Multi-Worker):**
```python
# Multiple worker processes
import multiprocessing

def worker_process(worker_id):
    while True:
        job = redis_queue.pop('blender_jobs')
        if job:
            process_job(job)

# Spawn N workers
for i in range(NUM_WORKERS):
    p = multiprocessing.Process(target=worker_process, args=(i,))
    p.start()
```

**Redis-Based Queue (Production):**
- Use Redis for job queue (persistent, distributed)
- Multiple worker machines poll Redis
- Auto-scaling based on queue length
- Job priorities (premium users first)

### 7.5 Cost Per Job Analysis

**Compute Costs (AWS EC2 c6i.2xlarge - 8 vCPU, 16 GB RAM):**
- **Hourly rate:** $0.34/hour
- **Per-minute rate:** $0.0057/minute
- **Average job duration:** 2 minutes
- **Cost per job:** $0.011

**Storage Costs (S3):**
- Input .glb: 5 MB
- Output .fbx + .blend + preview: 15 MB
- Total: 20 MB per job
- S3 storage: $0.023/GB/month
- **Cost per job:** $0.00046/month (negligible)

**Total Cost Per Job:**
- Compute: $0.011
- Storage: ~$0.0005
- **Total:** ~$0.012/job

**Pricing Strategy:**
- Auto-rig service: $15-20/job
- Gross margin: $14.99 (99.2% margin)
- **Highly profitable**

**Volume Economics:**
- 100 jobs/day: $1.20/day compute cost, $1,500-2,000 revenue
- 1,000 jobs/day: $12/day compute cost, $15,000-20,000 revenue
- **Scales extremely well**

---

## 8. Integration with Existing Features

### 8.1 MiniFig Pipeline Enhancement

**Current Pipeline:**
```
Character Images → TRELLIS → .glb Model → Download
```

**Enhanced Pipeline with Blender:**
```
Character Images → TRELLIS → .glb Model
                                ↓
                        ┌───────┴────────┐
                        │                │
                    Download          Blender
                    (basic)           (enhanced)
                                         ↓
                            ┌────────────┼────────────┐
                            │            │            │
                        Auto-Rig    Turntable    Materials
                            ↓            ↓            ↓
                        Rigged.fbx  Video.mp4    Enhanced.glb
```

**Database Schema Addition:**
```python
# Extend MiniFigAsset model
class MiniFigAsset(models.Model):
    # ... existing fields ...

    # Blender enhancements
    rigged_file = models.FileField(upload_to='minifig_rigged/', null=True, blank=True)
    rigged_file_format = models.CharField(max_length=10, choices=[('fbx', 'FBX'), ('blend', 'Blender')], default='fbx')
    turntable_video = models.FileField(upload_to='minifig_turntables/', null=True, blank=True)
    enhanced_materials = models.BooleanField(default=False)

    # Blender job reference
    blender_job = models.ForeignKey('BlenderJob', on_delete=models.SET_NULL, null=True, blank=True)
```

**UI Enhancement:**
```html
<!-- MiniFig detail page -->
<div class="minifig-downloads">
    <h3>Downloads</h3>

    <!-- Basic .glb (always available) -->
    <a href="{{ minifig.three_d_file.url }}" class="btn btn-primary">
        Download Basic Model (.glb)
    </a>

    <!-- Rigged character (if available) -->
    {% if minifig.rigged_file %}
    <a href="{{ minifig.rigged_file.url }}" class="btn btn-success">
        Download Rigged Character (.fbx)
        <span class="badge">Animation-Ready</span>
    </a>
    {% else %}
    <button class="btn btn-secondary" onclick="requestRigging('{{ minifig.id }}')">
        Generate Rigged Version ($15)
    </button>
    {% endif %}

    <!-- Turntable video (if available) -->
    {% if minifig.turntable_video %}
    <video controls>
        <source src="{{ minifig.turntable_video.url }}" type="video/mp4">
    </video>
    {% else %}
    <button class="btn btn-secondary" onclick="requestTurntable('{{ minifig.id }}')">
        Generate Turntable Video ($10)
    </button>
    {% endif %}
</div>
```

### 8.2 YouTube Content Workflow Integration

**Current Workflow:**
```
1. Generate character images (Stability AI)
2. Train character (FLUX LoRA)
3. Generate scene images
4. Convert to video (Runway)
5. Edit in DaVinci Resolve
6. Render final video
```

**Enhanced with 3D Animation:**
```
1. Generate character images (Stability AI)
2. Create 3D model (TRELLIS)
3. Auto-rig character (Blender) ← NEW
4. Generate animations (Blender) ← NEW
   - Walk cycles
   - Idle poses
   - Custom gestures
5. Render animated character (Blender) ← NEW
6. Composite in DaVinci Resolve (with 3D animated character)
7. Render final video
```

**New Capabilities:**
- Animated mascots in tutorials
- 3D character hosts for videos
- Product demonstrations with animated characters
- Explainer videos with 3D assets

### 8.3 Character Training Pipeline

**Synergy Opportunity:**
```
Trained Character (FLUX LoRA)
    ↓
Generate multiple poses/angles
    ↓
TRELLIS: Create 3D model from multiple views
    ↓
Blender: Auto-rig 3D model
    ↓
Result: Fully rigged character matching trained 2D character
```

**Workflow:**
1. User trains character (FLUX LoRA)
2. Platform generates 4 reference images (front, side, back, 3/4)
3. TRELLIS creates multi-view 3D model
4. Blender auto-rigs the model
5. **User now has:**
   - Trained 2D character (for images)
   - Rigged 3D character (for animations)
   - Consistent character across 2D and 3D

**Market Differentiation:** No competitor offers this!

### 8.4 Video Production Pipeline

**Current Assets:**
- DaVinci Resolve integration (editing, compositing)
- Render node service (automated rendering)
- Video chaining (ffmpeg)

**Blender Integration Points:**
1. **3D Assets for Compositing:**
   - Render 3D elements (logos, products, characters)
   - Import into DaVinci as video clips or images
   - Composite over live-action footage

2. **Intro/Outro Animations:**
   - Blender renders 3D logo animation
   - DaVinci imports as intro clip
   - Automatic branding for all videos

3. **Motion Graphics:**
   - Blender creates 3D text animations
   - DaVinci composites over video
   - Professional broadcast quality

**Example: Automated YouTube Intro**
```python
def create_youtube_intro(channel_name, logo_glb):
    """Generate 3D animated intro for YouTube channel"""

    # Blender job: Render logo animation
    job = submit_blender_job(
        user=user,
        operation='render_intro',
        parameters={
            'logo_model': logo_glb,
            'text': channel_name,
            'duration': 5,  # 5 seconds
            'template': 'rotate_and_fade'
        }
    )

    # Result: intro_animation.mp4
    # DaVinci automatically prepends to all videos
```

### 8.5 Agent Ecosystem Integration

**Current Agents:**
- CreativeDirectorAgent
- VideoProducerAgent
- ContentStrategistAgent

**New Blender-Aware Agent:**

**3D Asset Agent:**
```python
class ThreeDAssetAgent(BaseAgent):
    """Agent for managing 3D asset creation and optimization"""

    def analyze_character_for_3d(self, character_model):
        """Determine if character is suitable for 3D conversion"""

        # Check image quality, angles, consistency
        if self.has_multiple_views(character_model):
            return "Multi-view 3D generation recommended (higher quality)"
        else:
            return "Single-image 3D generation possible (lower quality)"

    def suggest_rigging_parameters(self, model_type):
        """Suggest Rigify parameters based on character type"""

        if model_type == 'humanoid':
            return {'rig_type': 'human', 'ik_limbs': True}
        elif model_type == 'creature':
            return {'rig_type': 'quadruped', 'ik_limbs': False}
        else:
            return {'rig_type': 'basic', 'ik_limbs': False}

    def recommend_animation(self, use_case):
        """Recommend animation templates based on use case"""

        animations = {
            'youtube_tutorial': ['idle_talking', 'pointing_gesture'],
            'product_demo': ['showcase_pose', 'turntable'],
            'game_asset': ['walk_cycle', 'idle', 'attack'],
        }

        return animations.get(use_case, ['idle'])
```

**Agent Workflow:**
```
User: "I want to create an animated mascot for my YouTube channel"
  ↓
CreativeDirectorAgent: "Let's create a consistent character first"
  ↓
[Generate character images, train FLUX LoRA]
  ↓
3D Asset Agent: "This character is perfect for 3D! Generating model..."
  ↓
[TRELLIS creates 3D model]
  ↓
3D Asset Agent: "Auto-rigging for animation..."
  ↓
[Blender auto-rigs character]
  ↓
3D Asset Agent: "Applying 'idle_talking' animation for tutorials..."
  ↓
[Blender renders animated character]
  ↓
VideoProducerAgent: "Compositing mascot into your tutorial video..."
  ↓
[DaVinci Resolve composites 3D character]
  ↓
Result: YouTube tutorial with animated mascot
```

---

## 9. Competitive Advantages

### 9.1 Market Differentiation

**What Competitors Offer:**
- **Sketchfab, TurboSquid:** Static 3D model marketplaces (no auto-rigging, no animation)
- **Ready Player Me:** Avatar creation (limited to humanoid avatars, no custom characters)
- **Mixamo:** Auto-rigging service (requires manual upload, limited to humanoid)
- **DALL-E 3D, Point-E:** Basic 3D from text (low quality, no rigging)

**What WE Would Offer:**
1. **End-to-End Pipeline:** Image → 3D → Rigged → Animated (fully automated)
2. **AI-Generated Characters:** Create custom characters from text/image, then convert to 3D
3. **No 3D Software Required:** All in browser, no Blender knowledge needed
4. **Animation Templates:** One-click animations (walk, run, gesture)
5. **YouTube Integration:** Directly into video production workflow
6. **Batch Processing:** Rig 100 characters overnight

**Unique Selling Points:**
- "From imagination to animated 3D in 5 minutes"
- "Rigged characters for $20 vs $200 from freelancers"
- "No 3D software required - all in your browser"
- "Perfect for YouTube creators, game devs, educators"

### 9.2 Technical Advantages

**1. Blender is Free/Open Source:**
- No licensing fees (vs Maya $1,785/year, 3ds Max $1,700/year)
- Can modify and extend as needed
- Active community and plugins
- **Cost advantage:** $0 vs $10,000s for commercial 3D suites

**2. Python API Automation:**
- Every feature scriptable (unlike many proprietary tools)
- Easy integration with our Django/Python stack
- Extensive documentation and examples
- **Development speed:** Weeks vs months

**3. Proven Production Workflows:**
- Used by Blender Studio for feature films
- Netflix animation productions use Blender
- Battle-tested pipeline tools available
- **Reliability:** Production-grade, not experimental

**4. Cross-Platform:**
- Runs on macOS, Linux, Windows
- Headless server deployment
- Cloud-friendly (AWS, GCP, DigitalOcean)
- **Flexibility:** Deploy anywhere

### 9.3 Business Model Advantages

**Pricing Tiers:**

**Free Tier:**
- Download basic .glb model
- Static 3D file, no rigging

**Pro Tier ($20/character):**
- Auto-rigged character (.fbx)
- Animation-ready
- Blender source file (.blend)
- Preview renders

**Premium Tier ($50/character):**
- Pro tier +
- 3 animation templates (walk, idle, gesture)
- Turntable video (360°)
- High-quality Cycles renders (4K)

**Enterprise Tier (Custom):**
- Batch rigging (100s of characters)
- Custom animation templates
- Dedicated worker instances
- Priority processing
- API access

**Recurring Revenue:**
- **Subscription:** $50/month for unlimited basic rigging
- **Credits:** Buy 10 credits for $150 ($15/each), use anytime
- **Agency Plan:** $500/month for team features + priority

### 9.4 Partnership Opportunities

**Game Engines:**
- Unity Asset Store: Sell rigged characters as Unity prefabs
- Unreal Marketplace: Sell as Unreal-ready assets
- Godot: Free/open-source game engine (growing market)

**E-commerce Platforms:**
- Shopify app: "3D Product Turntables"
- WooCommerce plugin: "Automated 3D Models"
- Amazon: Enhanced product listings with 3D views

**YouTube/Content Creation:**
- YouTube Studio integration: "Add 3D Mascot"
- TikTok/Instagram: Vertical format 3D animations
- Twitch: Animated overlays and alerts

**Education:**
- Udemy courses: "3D Animation Made Easy"
- Skillshare: "Create Animated Characters"
- Schools: Educational pricing for students

### 9.5 Why Competitors Can't Easily Copy

**Barriers to Entry:**

1. **Technical Complexity:**
   - Blender automation requires deep Python + 3D knowledge
   - Subprocess management, job queuing, error handling
   - Not trivial to implement well

2. **Integration Complexity:**
   - We already have TRELLIS, character training, video pipeline
   - Blender is the "missing link" that completes the workflow
   - Competitors would need to build entire pipeline

3. **Quality Control:**
   - Auto-rigging doesn't work perfectly for all models
   - Requires fallback logic, error handling, quality checks
   - Takes months to refine

4. **Infrastructure:**
   - Need reliable render nodes, job queues, file storage
   - We already have this from DaVinci integration
   - Competitors starting from scratch

5. **First-Mover Advantage:**
   - We can establish brand as "AI 3D Animation Platform"
   - Build user base and testimonials
   - Capture market before competitors notice

---

## 10. Implementation Roadmap

### Phase 1: Foundation (Weeks 1-3)

**Goal:** Basic Blender integration with .glb import and material enhancement

**Deliverables:**
1. Blender Render Service (FastAPI)
   - Basic job queue (FIFO, single worker)
   - Health check endpoint
   - Token authentication
2. Django Integration
   - BlenderJob model
   - Webhook endpoints
   - File upload handling
3. Blender Scripts
   - Import .glb
   - Export .fbx
   - Basic material enhancement
4. Testing
   - Unit tests for API
   - Integration tests with real .glb files
   - Error handling

**Success Metrics:**
- Can import .glb and export .fbx
- Job queue processes 1 job at a time
- Error handling for corrupted files

**Time:** 3 weeks
**Team:** 1 backend dev, 1 3D tech artist

---

### Phase 2: Auto-Rigging (Weeks 4-7)

**Goal:** Automated character rigging with Rigify

**Deliverables:**
1. Rigify Integration
   - Meta-rig generation
   - Automatic weight painting
   - Rig validation
2. Character Type Detection
   - Humanoid detection
   - Quadruped detection
   - Fallback for generic
3. UI Enhancement
   - "Generate Rigged Version" button
   - Progress tracking
   - Download rigged .fbx
4. Quality Assurance
   - Test with 20+ character types
   - Handle edge cases (missing limbs, unusual proportions)
   - Fallback to basic rig if Rigify fails

**Success Metrics:**
- 80%+ success rate for humanoid characters
- Average rigging time: <2 minutes
- User satisfaction: 4+ stars

**Time:** 4 weeks
**Team:** 1 backend dev, 1 3D tech artist, 1 QA

---

### Phase 3: Animation & Rendering (Weeks 8-10)

**Goal:** Animation templates and turntable rendering

**Deliverables:**
1. Animation Templates
   - Walk cycle (looping)
   - Idle pose (breathing)
   - Gesture (pointing, waving)
   - Turntable (360° rotation)
2. Rendering Pipeline
   - Eevee setup (fast previews)
   - Cycles setup (high-quality)
   - Video encoding (ffmpeg)
3. UI Enhancement
   - Animation selector
   - Preview before purchasing
   - Render quality options (fast/high)
4. Template Library
   - 5-10 animation templates
   - Blender .blend files with keyframes
   - Auto-apply to any rigged character

**Success Metrics:**
- 5 animation templates available
- Turntable renders in <2 minutes
- Users purchase animations (conversion rate >10%)

**Time:** 3 weeks
**Team:** 1 backend dev, 1 3D animator, 1 frontend dev

---

### Phase 4: Production Polish (Weeks 11-12)

**Goal:** Scale, optimize, and prepare for launch

**Deliverables:**
1. Performance Optimization
   - Parallel job processing (4 workers)
   - Redis job queue
   - Result caching
2. Error Handling
   - Graceful degradation
   - User-friendly error messages
   - Automatic retry logic
3. Monitoring & Analytics
   - Job success rates
   - Average processing time
   - User behavior (which animations purchased)
4. Documentation
   - User guide (how to use Blender features)
   - API documentation (for enterprise customers)
   - Troubleshooting guide

**Success Metrics:**
- Process 100+ jobs/day reliably
- <1% error rate
- 4+ star user reviews

**Time:** 2 weeks
**Team:** 1 backend dev, 1 DevOps, 1 technical writer

---

### Total Timeline: 12 Weeks (3 Months)

**Team Requirements:**
- 1 Senior Backend Developer (full-time)
- 1 3D Technical Artist/Animator (full-time)
- 1 Frontend Developer (part-time, 50%)
- 1 QA Engineer (part-time, 50%)
- 1 DevOps Engineer (part-time, 25%)

**Budget Estimate:**
- Personnel: ~$60,000-80,000 (3 months, mixed rates)
- Infrastructure: ~$500-1,000/month (servers, storage)
- Tools/Licenses: $0 (Blender is free!)
- **Total:** ~$62,000-82,000

**ROI Timeline:**
- Month 1 (post-launch): 50 rigged characters @ $20 = $1,000
- Month 3: 200 characters + 50 animations = $5,000
- Month 6: 500 characters + 200 animations = $15,000/month
- **Break-even:** ~5-6 months

---

## 11. Code Examples & Patterns

### 11.1 Basic bpy Operations

**Example 1: Import GLB, Add Material, Export FBX**
```python
import bpy

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Import GLB
bpy.ops.import_scene.gltf(filepath='/path/to/character.glb')

# Get imported object
obj = bpy.context.selected_objects[0]

# Create new material
mat = bpy.data.materials.new(name="EnhancedMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes

# Get Principled BSDF
bsdf = nodes.get("Principled BSDF")
if bsdf:
    # Set metallic and roughness
    bsdf.inputs['Metallic'].default_value = 0.0
    bsdf.inputs['Roughness'].default_value = 0.5

# Assign material
if obj.data.materials:
    obj.data.materials[0] = mat
else:
    obj.data.materials.append(mat)

# Export as FBX
bpy.ops.export_scene.fbx(
    filepath='/path/to/output.fbx',
    use_selection=False,
    mesh_smooth_type='FACE'
)

print("✅ Export complete!")
```

**Example 2: Render Preview Image**
```python
import bpy

# Set up camera
bpy.ops.object.camera_add(location=(7, -7, 5))
camera = bpy.context.active_object
camera.rotation_euler = (1.1, 0, 0.785)  # Look at center
bpy.context.scene.camera = camera

# Set up sun light
bpy.ops.object.light_add(type='SUN', location=(10, 10, 10))
sun = bpy.context.active_object
sun.data.energy = 1.5

# Render settings
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1024
scene.render.resolution_y = 1024
scene.render.film_transparent = True  # Transparent background

# Eevee settings for better quality
scene.eevee.taa_render_samples = 64
scene.eevee.use_gtao = True  # Ambient occlusion
scene.eevee.use_bloom = True  # Bloom effect

# Render
scene.render.filepath = '/path/to/preview.png'
bpy.ops.render.render(write_still=True)

print("✅ Render complete!")
```

**Example 3: Create Turntable Animation**
```python
import bpy
import math

# Get object to rotate
obj = bpy.context.selected_objects[0]

# Create empty object for rotation
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
empty = bpy.context.active_object
empty.name = "Turntable"

# Parent object to empty
obj.parent = empty

# Set up animation (360° rotation over 120 frames)
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 120

# Keyframe rotation
empty.rotation_euler = (0, 0, 0)
empty.keyframe_insert(data_path="rotation_euler", frame=1)

empty.rotation_euler = (0, 0, math.radians(360))
empty.keyframe_insert(data_path="rotation_euler", frame=120)

# Set interpolation to linear
for fcurve in empty.animation_data.action.fcurves:
    for keyframe in fcurve.keyframe_points:
        keyframe.interpolation = 'LINEAR'

# Render animation
scene.render.filepath = '/path/to/turntable_####.png'  # #### = frame number
scene.render.image_settings.file_format = 'PNG'

bpy.ops.render.render(animation=True)

print("✅ Turntable animation rendered!")
```

### 11.2 Advanced Rigify Automation

**Auto-Rig with Proportional Scaling:**
```python
import bpy
import mathutils

def auto_rig_character(mesh_obj):
    """Auto-generate Rigify rig scaled to character"""

    # Get character dimensions
    bbox = [mesh_obj.matrix_world @ mathutils.Vector(corner) for corner in mesh_obj.bound_box]

    # Calculate height (Z-axis)
    min_z = min([v.z for v in bbox])
    max_z = max([v.z for v in bbox])
    height = max_z - min_z

    # Calculate width (X-axis)
    min_x = min([v.x for v in bbox])
    max_x = max([v.x for v in bbox])
    width = max_x - min_x

    print(f"Character dimensions: {width:.2f} × {height:.2f}")

    # Add Rigify human meta-rig
    bpy.ops.object.armature_human_metarig_add()
    metarig = bpy.context.active_object

    # Scale meta-rig to match character
    # Rigify human default is ~2 units tall
    scale_factor = height / 2.0
    metarig.scale = (scale_factor, scale_factor, scale_factor)

    # Position meta-rig at character base
    metarig.location.z = min_z

    # Apply scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # Generate rig
    bpy.ops.pose.rigify_generate()

    # Find generated rig
    rig = None
    for obj in bpy.context.selected_objects:
        if obj.type == 'ARMATURE' and obj != metarig:
            rig = obj
            break

    if not rig:
        raise RuntimeError("Rigify failed to generate rig")

    # Parent mesh to rig with automatic weights
    bpy.ops.object.select_all(action='DESELECT')
    mesh_obj.select_set(True)
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')

    print(f"✅ Character rigged: {rig.name}")

    return rig

# Usage
mesh = bpy.data.objects['Character']
rig = auto_rig_character(mesh)
```

### 11.3 Material Enhancement with PBR

**Apply PBR Material from Texture Set:**
```python
import bpy
import os

def apply_pbr_material(obj, texture_dir):
    """Apply PBR material from texture files"""

    # Texture file patterns
    textures = {
        'base_color': 'albedo.png',
        'metallic': 'metallic.png',
        'roughness': 'roughness.png',
        'normal': 'normal.png',
        'ao': 'ao.png'  # Ambient occlusion
    }

    # Create material
    mat = bpy.data.materials.new(name="PBR_Material")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Clear default nodes
    nodes.clear()

    # Add Principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)

    # Add Material Output
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    # Add texture nodes
    y_offset = 300

    for tex_type, filename in textures.items():
        filepath = os.path.join(texture_dir, filename)

        if not os.path.exists(filepath):
            print(f"⚠️ Texture not found: {filename}")
            continue

        # Create image texture node
        tex_node = nodes.new(type='ShaderNodeTexImage')
        tex_node.location = (-400, y_offset)
        tex_node.image = bpy.data.images.load(filepath)

        # Connect to Principled BSDF
        if tex_type == 'base_color':
            links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])
        elif tex_type == 'metallic':
            links.new(tex_node.outputs['Color'], bsdf.inputs['Metallic'])
        elif tex_type == 'roughness':
            links.new(tex_node.outputs['Color'], bsdf.inputs['Roughness'])
        elif tex_type == 'normal':
            # Normal map requires Normal Map node
            normal_map = nodes.new(type='ShaderNodeNormalMap')
            normal_map.location = (-200, y_offset)
            links.new(tex_node.outputs['Color'], normal_map.inputs['Color'])
            links.new(normal_map.outputs['Normal'], bsdf.inputs['Normal'])

        y_offset -= 300

    # Assign material to object
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

    print(f"✅ PBR material applied to {obj.name}")

# Usage
obj = bpy.data.objects['Character']
apply_pbr_material(obj, '/path/to/textures/')
```

### 11.4 Batch Processing Pattern

**Process Multiple GLB Files:**
```python
import bpy
import os
import glob

def batch_process_glb_files(input_dir, output_dir, operation='auto_rig'):
    """Batch process GLB files"""

    # Find all GLB files
    glb_files = glob.glob(os.path.join(input_dir, '*.glb'))

    print(f"📦 Found {len(glb_files)} GLB files")

    results = []

    for idx, glb_path in enumerate(glb_files):
        print(f"\n🔄 Processing {idx + 1}/{len(glb_files)}: {os.path.basename(glb_path)}")

        # Clear scene
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()

        try:
            # Import GLB
            bpy.ops.import_scene.gltf(filepath=glb_path)

            # Get object
            obj = bpy.context.selected_objects[0]

            # Perform operation
            if operation == 'auto_rig':
                rig = auto_rig_character(obj)

            # Export
            base_name = os.path.splitext(os.path.basename(glb_path))[0]
            output_path = os.path.join(output_dir, f"{base_name}_rigged.fbx")

            bpy.ops.export_scene.fbx(filepath=output_path)

            results.append({
                'input': glb_path,
                'output': output_path,
                'status': 'success'
            })

            print(f"✅ Success: {output_path}")

        except Exception as e:
            results.append({
                'input': glb_path,
                'output': None,
                'status': 'failed',
                'error': str(e)
            })

            print(f"❌ Failed: {str(e)}")

    # Summary
    success_count = sum(1 for r in results if r['status'] == 'success')
    print(f"\n📊 Batch complete: {success_count}/{len(results)} succeeded")

    return results

# Usage (run from command line)
# blender --background --python batch_process.py
input_dir = '/path/to/glb_files/'
output_dir = '/path/to/output/'
results = batch_process_glb_files(input_dir, output_dir)
```

### 11.5 Progress Tracking

**Write Progress to File for FastAPI to Read:**
```python
import bpy
import json
import time

class ProgressTracker:
    """Track Blender job progress"""

    def __init__(self, progress_file):
        self.progress_file = progress_file
        self.start_time = time.time()

    def update(self, progress, stage):
        """Update progress (0-100) and current stage"""

        elapsed = time.time() - self.start_time

        data = {
            'progress': progress,
            'stage': stage,
            'elapsed_seconds': int(elapsed)
        }

        with open(self.progress_file, 'w') as f:
            json.dump(data, f)

        print(f"📊 Progress: {progress}% - {stage}")

# Usage in Blender script
tracker = ProgressTracker('/tmp/job_12345_progress.json')

tracker.update(0, "Importing GLB")
bpy.ops.import_scene.gltf(filepath=input_glb)

tracker.update(25, "Generating rig")
auto_rig_character(obj)

tracker.update(50, "Parenting mesh")
parent_mesh_to_rig()

tracker.update(75, "Exporting FBX")
bpy.ops.export_scene.fbx(filepath=output_fbx)

tracker.update(90, "Rendering preview")
bpy.ops.render.render(write_still=True)

tracker.update(100, "Complete")
```

**FastAPI reads progress:**
```python
import json
from pathlib import Path

@app.get("/api/v1/jobs/{job_id}/progress/")
async def get_job_progress(job_id: str):
    """Get real-time progress of a Blender job"""

    progress_file = Path(f"/tmp/job_{job_id}_progress.json")

    if not progress_file.exists():
        return {"progress": 0, "stage": "Queued", "elapsed_seconds": 0}

    with open(progress_file) as f:
        data = json.load(f)

    return data
```

---

## 12. Cost Analysis & ROI

### 12.1 Development Costs

**Personnel (12 weeks):**
| Role | Rate | Hours | Cost |
|------|------|-------|------|
| Senior Backend Dev | $100/hr | 480 hrs | $48,000 |
| 3D Tech Artist | $75/hr | 480 hrs | $36,000 |
| Frontend Dev (50%) | $80/hr | 240 hrs | $19,200 |
| QA Engineer (50%) | $60/hr | 240 hrs | $14,400 |
| DevOps (25%) | $90/hr | 120 hrs | $10,800 |
| **Total Personnel** | | | **$128,400** |

**Infrastructure (3 months):**
| Item | Monthly | 3 Months |
|------|---------|----------|
| Dev Server (AWS c6i.2xlarge) | $250 | $750 |
| Storage (S3, 500 GB) | $12 | $36 |
| Monitoring (Datadog) | $30 | $90 |
| **Total Infrastructure** | | **$876** |

**Software/Tools:**
| Item | Cost |
|------|------|
| Blender | $0 (free!) |
| GitHub Copilot | $10/mo × 5 devs × 3 mo = $150 |
| Design tools (Figma) | $45/mo × 3 mo = $135 |
| **Total Tools** | **$285** |

**Total Development Cost:** $128,400 + $876 + $285 = **$129,561**

### 12.2 Operating Costs (Monthly)

**Infrastructure:**
| Item | Specs | Cost/Month |
|------|-------|------------|
| Blender Worker (AWS c6i.2xlarge) | 8 vCPU, 16 GB RAM | $250 |
| Storage (S3) | 1 TB @ $0.023/GB | $23 |
| Bandwidth | 500 GB @ $0.09/GB | $45 |
| Monitoring & Logs | Datadog, CloudWatch | $50 |
| **Total Infrastructure** | | **$368/month** |

**Personnel (Post-Launch):**
| Role | Hours/Week | Cost/Month |
|------|------------|------------|
| Backend Maintenance | 10 hrs @ $100/hr | $4,000 |
| 3D Support | 5 hrs @ $75/hr | $1,500 |
| Customer Support | 20 hrs @ $40/hr | $3,200 |
| **Total Personnel** | | **$8,700/month** |

**Total Operating Cost:** $368 + $8,700 = **$9,068/month**

### 12.3 Revenue Projections

**Pricing Model:**
- Auto-Rig: $20/character
- Turntable Video: $15/video
- Animation Template: $25/animation
- High-Quality Render (Cycles): $30/render

**Conservative Scenario (Month 1):**
| Product | Units | Revenue |
|---------|-------|---------|
| Auto-Rig | 30 | $600 |
| Turntable | 10 | $150 |
| Animation | 5 | $125 |
| **Total** | | **$875** |

**Moderate Scenario (Month 6):**
| Product | Units | Revenue |
|---------|-------|---------|
| Auto-Rig | 200 | $4,000 |
| Turntable | 80 | $1,200 |
| Animation | 50 | $1,250 |
| Cycles Render | 20 | $600 |
| **Total** | | **$7,050** |

**Optimistic Scenario (Month 12):**
| Product | Units | Revenue |
|---------|-------|---------|
| Auto-Rig | 500 | $10,000 |
| Turntable | 200 | $3,000 |
| Animation | 150 | $3,750 |
| Cycles Render | 80 | $2,400 |
| Subscription (20 users @ $50/mo) | | $1,000 |
| **Total** | | **$20,150** |

### 12.4 Break-Even Analysis

**Total Investment:** $129,561 (development) + $9,068/mo (operating)

**Monthly Revenue Needed to Break Even (Operating):** $9,068

**Scenarios:**
1. **Conservative (Month 1):** $875 revenue - **NOT break-even**
2. **Moderate (Month 6):** $7,050 revenue - **Approaching break-even**
3. **Optimistic (Month 12):** $20,150 revenue - **Profitable** ($11,082/mo profit)

**Break-Even Timeline:**
- Assumes linear growth from Month 1 to Month 12
- Operating break-even: **Month 7** (~$9,000/mo revenue)
- Total investment recoup: **Month 18** ($129,561 ÷ $11,082/mo)

### 12.5 ROI Calculation (3-Year)

**Year 1:**
- Revenue: $875 (Mo 1) → $20,150 (Mo 12), average $10,500/mo = **$126,000**
- Costs: $129,561 (dev) + $9,068 × 12 (ops) = **$237,377**
- **Net: -$111,377** (investment year)

**Year 2:**
- Revenue: $25,000/mo average (2.5x growth) = **$300,000**
- Costs: $9,068 × 12 = **$108,816**
- **Net: +$191,184**

**Year 3:**
- Revenue: $40,000/mo average (4x initial) = **$480,000**
- Costs: $10,000 × 12 (slight increase) = **$120,000**
- **Net: +$360,000**

**3-Year Total:**
- Total Revenue: $906,000
- Total Costs: $466,193
- **Net Profit: $439,807**
- **ROI: 340%** ($439,807 ÷ $129,561 initial investment)

**Conclusion:** Highly profitable if we hit moderate-to-optimistic growth targets.

---

## 13. Risks & Challenges

### 13.1 Technical Risks

**Risk 1: Auto-Rigging Quality**
- **Problem:** Rigify may fail for non-humanoid or unusual characters
- **Impact:** High (core feature)
- **Mitigation:**
  - Fallback to simpler rig types (bone deformation only)
  - Manual rigging service ($50 premium) for edge cases
  - Improve over time with machine learning (pose detection)

**Risk 2: Performance Bottlenecks**
- **Problem:** Single worker can't handle high demand (30 jobs/hour max)
- **Impact:** Medium (scaling issue)
- **Mitigation:**
  - Start with single worker (MVP)
  - Monitor queue length, add workers as needed
  - Auto-scaling based on demand

**Risk 3: Blender Crashes**
- **Problem:** Blender subprocess crashes, job stuck
- **Impact:** Medium (reliability)
- **Mitigation:**
  - Timeout mechanism (kill process after 5 min)
  - Automatic retry (1 attempt)
  - Error reporting to user

**Risk 4: File Format Compatibility**
- **Problem:** TRELLIS .glb files may have issues Blender can't handle
- **Impact:** Medium (compatibility)
- **Mitigation:**
  - Pre-validate .glb files before Blender processing
  - Normalize/repair meshes (Blender has built-in tools)
  - Test with diverse TRELLIS outputs

### 13.2 Business Risks

**Risk 1: Low Demand**
- **Problem:** Users don't value rigged characters enough to pay $20
- **Impact:** High (revenue)
- **Mitigation:**
  - Market research before full build (survey existing users)
  - A/B test pricing ($10 vs $20 vs $30)
  - Freemium model (first rig free, then paid)

**Risk 2: Competitors Copy**
- **Problem:** Competitors see success and build similar feature
- **Impact:** Medium (market share)
- **Mitigation:**
  - First-mover advantage (build brand early)
  - Continuous innovation (new animation templates, better quality)
  - Integrated pipeline (hard to replicate our full workflow)

**Risk 3: Margin Compression**
- **Problem:** Cloud GPU costs rise, forcing price increases or margin loss
- **Impact:** Low (cloud costs are small portion)
- **Mitigation:**
  - Monitor cloud costs closely
  - Optimize Blender scripts (faster = cheaper)
  - Consider on-prem servers if volume justifies

### 13.3 Operational Risks

**Risk 1: Support Burden**
- **Problem:** Users have issues with rigged characters not working in their software
- **Impact:** Medium (support costs)
- **Mitigation:**
  - Comprehensive documentation (how to import .fbx in Unity, Unreal, etc.)
  - Video tutorials
  - Community forum (users help each other)

**Risk 2: Quality Expectations**
- **Problem:** Automated rigging won't match professional manual rigging
- **Impact:** Medium (user satisfaction)
- **Mitigation:**
  - Set clear expectations ("auto-rig for quick prototyping, not film production")
  - Offer premium manual rigging service ($200) for high-end needs
  - Continuously improve auto-rig quality

**Risk 3: Learning Curve**
- **Problem:** Users don't understand rigging/animation concepts
- **Impact:** Low (education issue)
- **Mitigation:**
  - Educational content (blog posts, videos)
  - In-app tooltips and help
  - Simple language (avoid 3D jargon)

### 13.4 Dependency Risks

**Risk 1: Blender API Changes**
- **Problem:** Blender 5.0 breaks our scripts
- **Impact:** Medium (maintenance)
- **Mitigation:**
  - Pin Blender version (use 3.6 LTS for stability)
  - Test new versions before upgrading
  - Maintain compatibility layer

**Risk 2: TRELLIS Quality Degrades**
- **Problem:** Replicate changes TRELLIS model, output quality drops
- **Impact:** Medium (input quality affects output)
- **Mitigation:**
  - Monitor TRELLIS output quality
  - Have fallback 3D generation providers
  - Build our own 3D generation (long-term)

### 13.5 Mitigation Summary

**High-Priority Mitigations (Do Before Launch):**
1. Fallback rigging for edge cases
2. Market validation (survey users about $20 pricing)
3. Timeout and crash handling
4. Comprehensive documentation

**Medium-Priority (First 3 Months):**
1. Multi-worker scaling
2. Continuous quality improvement
3. Educational content
4. Community forum

**Low-Priority (Future):**
1. Machine learning for better rigging
2. On-prem servers
3. Custom 3D generation

---

## 14. Comparison with Alternatives

### 14.1 Blender vs Commercial 3D Software

| Feature | Blender | Maya | 3ds Max | Cinema 4D |
|---------|---------|------|---------|-----------|
| **Cost** | Free | $1,785/year | $1,700/year | $999/year |
| **Python API** | Yes, comprehensive | Yes | MaxScript (not Python) | Yes |
| **Headless Rendering** | Yes | Yes | Limited | Yes |
| **Auto-Rigging** | Rigify (built-in) | HumanIK (built-in) | CAT (built-in) | Add-on required |
| **Animation Tools** | Excellent | Industry standard | Excellent | Excellent |
| **Rendering** | Cycles, Eevee | Arnold | Arnold, V-Ray | Octane, Redshift |
| **Scripting Ease** | Easy (Python) | Easy (Python, MEL) | Medium (MaxScript) | Medium |
| **Community** | Very large | Large (pro-focused) | Medium | Medium |
| **Linux Support** | Yes | Yes | No | No |
| **Cloud-Friendly** | Yes | Yes | No | Limited |

**Verdict:** Blender is the **best choice** for our use case:
- Free (no licensing costs)
- Excellent Python API
- Headless operation
- Cross-platform (macOS, Linux, Windows)
- Active community and development

### 14.2 Blender vs Cloud Rendering Services

| Service | Type | Pricing | Best For | Drawbacks |
|---------|------|---------|----------|-----------|
| **Blender (Self-Hosted)** | Open-source, self-hosted | Server costs only ($250/mo) | Full control, customization | Need to manage infrastructure |
| **Blender Cloud (Render Farms)** | SaaS | $0.05-0.15/render-hour | Burst capacity, no maintenance | Less control, ongoing costs |
| **SheepIt Render Farm** | Free community render farm | Free (share your compute) | Zero cost | Slow, unreliable |
| **RenderStreet** | Cloud rendering | $0.25/render-hour | Blender-specific, optimized | Ongoing costs add up |
| **AWS Batch + Blender** | DIY cloud | ~$0.34/hour (compute) | Scalable, AWS ecosystem | Complex setup |

**Verdict:** **Self-hosted Blender** for MVP, **Cloud Blender** for burst capacity.

### 14.3 Blender Auto-Rigging vs Alternatives

| Solution | Type | Cost | Quality | Speed | Best For |
|----------|------|------|---------|-------|----------|
| **Blender Rigify** | Open-source add-on | Free | Good for humanoids | 30-60 sec | Our platform (automated) |
| **Mixamo** | Web service | Free (Adobe) | Excellent for humanoids | 2-5 min | Manual upload workflow |
| **AccuRIG** | Commercial tool | $99/year | Excellent | 1-2 min | Professional workflows |
| **Manual Rigging** | Human artist | $50-200/character | Excellent (customized) | 2-8 hours | High-end productions |
| **RigNet (ML)** | Research project | Free (experimental) | Variable | 5-10 min | Experimental/research |

**Verdict:** **Rigify is best for automation:**
- Free (built-in to Blender)
- Fast enough (30-60 sec)
- Good quality for humanoids
- Fully scriptable (no web service dependency)

**Mixamo Comparison:**
- Mixamo: Better quality, but requires manual upload (not automatable at scale)
- Rigify: Lower quality, but fully automated (fits our pipeline)

**Recommendation:** Use Rigify for MVP, add Mixamo API integration later if available.

### 14.4 Blender Rendering vs DaVinci Resolve

**Blender (3D Rendering):**
- 3D models, animations, simulations
- Cycles (photorealistic) or Eevee (real-time)
- Outputs: Still images, image sequences, videos

**DaVinci Resolve (Video Editing/Compositing):**
- Video editing, color grading, compositing
- 2D timeline-based editing
- Outputs: Final videos (MP4, etc.)

**Integration:**
```
Blender (Render 3D elements)
    ↓ (PNG sequence or MP4)
DaVinci Resolve (Composite + Edit)
    ↓ (Final video)
YouTube
```

**Use Cases:**
- **Blender-only:** 3D product turntables, character animations (short clips)
- **DaVinci-only:** Live-action editing, color grading
- **Blender → DaVinci:** Composite 3D elements into live-action videos

**Verdict:** Both are needed, complementary tools.

---

## 15. Recommendations & Next Steps

### 15.1 Strategic Recommendation: PROCEED

**Rationale:**
1. **Strong Business Case:**
   - High margins (99% on compute)
   - Clear demand (rigged characters are 3-10x more valuable)
   - Defensible competitive advantage (integrated pipeline)

2. **Technical Feasibility:**
   - Blender is proven technology (used in production worldwide)
   - We already have similar infrastructure (DaVinci render node)
   - Python expertise in team

3. **Market Timing:**
   - AI 3D generation is emerging (TRELLIS, others)
   - No integrated platform offering AI → 3D → Rigged → Animated
   - First-mover advantage opportunity

4. **Alignment with Strategy:**
   - ✅ Fits "AI content creation" focus
   - ✅ Enhances YouTube workflow (animated characters)
   - ✅ Builds on existing features (character training, MiniFig pipeline)

**Recommendation:** **Proceed with phased implementation (12-week roadmap).**

### 15.2 Immediate Next Steps (Week 1)

**1. Market Validation (3 days)**
- Survey 50-100 existing users
- Questions:
  - "Would you pay $20 for a rigged (animation-ready) version of your 3D character?"
  - "What would you use rigged characters for?" (YouTube, games, product demos, other)
  - "Which animations would you buy?" (walk, idle, gesture, custom)
- **Target:** >60% say "yes" to $20 rigging

**2. Technical Proof-of-Concept (4 days)**
- Install Blender on Mac
- Write basic auto-rig script
- Test with 5-10 TRELLIS .glb outputs
- Measure success rate and quality
- **Target:** >70% successful auto-rigs

**3. Cost Validation (1 day)**
- Spin up AWS c6i.2xlarge instance
- Run auto-rig benchmark (50 jobs)
- Measure actual compute time and cost
- **Target:** Confirm <$0.02/job compute cost

**4. Go/No-Go Decision (1 day)**
- Review market validation results
- Review technical POC results
- Review cost validation
- **Decision:** Proceed to Phase 1 or pause for refinement

**Total:** 1 week, <$2,000 cost (mostly personnel time)

### 15.3 Phase 1 Kickoff (Week 2)

**If Go Decision:**

**Staffing:**
- Hire/assign Senior Backend Developer (full-time)
- Hire/assign 3D Technical Artist (full-time)
- Brief team on project goals and architecture

**Infrastructure:**
- Provision development server (AWS or Mac)
- Install Blender 3.6 LTS
- Set up GitHub repo (`blender-service`)
- Configure CI/CD pipeline

**First Deliverable (Week 3):**
- Basic FastAPI service running
- Health check endpoint working
- Can import .glb and export .fbx (no rigging yet)

### 15.4 Success Metrics (3 Months Post-Launch)

**Technical Metrics:**
- Auto-rig success rate: >80%
- Average job time: <2 minutes
- Error rate: <5%
- Uptime: >99%

**Business Metrics:**
- Monthly rigged characters: >200
- Revenue: >$4,000/month
- Customer satisfaction: >4.0/5.0 stars
- Support tickets: <10/month

**User Metrics:**
- Conversion rate (view → purchase): >10%
- Repeat purchase rate: >30%
- NPS (Net Promoter Score): >50

### 15.5 Long-Term Vision (12-24 Months)

**Expand Capabilities:**
1. **Animation Library:** 50+ templates (walk, run, jump, dance, etc.)
2. **Custom Animations:** AI-generated animations from text ("character waves hello")
3. **Scene Composition:** Multi-character scenes with automatic positioning
4. **Physics Simulation:** Cloth, hair, rigid body (advanced)
5. **Mocap Integration:** Import motion capture data for realistic animation

**Platform Integration:**
1. **Unity Plugin:** Export directly to Unity with prefabs
2. **Unreal Plugin:** Export directly to Unreal with blueprints
3. **Game Engine Marketplace:** Sell rigged characters on Unity/Unreal stores
4. **NFT/Metaverse:** 3D avatars for VRChat, Decentraland, etc.

**Business Model Evolution:**
1. **Freemium:** First 3 rigs free, then subscription
2. **Enterprise API:** $500/mo for unlimited rigging via API
3. **White-Label:** License technology to other platforms ($5,000/mo)
4. **Agency Services:** Full-service 3D content creation ($10,000-50,000 projects)

### 15.6 Alternative Paths to Consider

**Alternative 1: Partner with Mixamo**
- **Pros:** Higher quality auto-rigging, Adobe brand
- **Cons:** Dependency on Adobe, may not have automation API, costs
- **Verdict:** Explore as complement, not replacement

**Alternative 2: Build Our Own Rigging AI**
- **Pros:** Full control, competitive advantage, no dependencies
- **Cons:** 6-12 months development, requires ML expertise, high risk
- **Verdict:** Future roadmap (12-24 months), not MVP

**Alternative 3: Manual Rigging Service**
- **Pros:** Lower technical risk, hire 3D artists
- **Cons:** Doesn't scale, high labor costs, slow turnaround
- **Verdict:** Offer as premium tier ($200), not core product

**Alternative 4: No Blender, Focus Elsewhere**
- **Pros:** No development cost, focus resources on other features
- **Cons:** Miss market opportunity, competitors may fill gap
- **Verdict:** Not recommended (opportunity is too strong)

### 15.7 Final Recommendation Summary

**PROCEED with Blender integration:**
1. **Week 1:** Market validation + technical POC
2. **Week 2-3:** Phase 1 foundation
3. **Week 4-7:** Phase 2 auto-rigging
4. **Week 8-10:** Phase 3 animation & rendering
5. **Week 11-12:** Phase 4 polish & launch

**Total Investment:** ~$130,000 (development) + $9,000/month (operating)
**Expected ROI:** 340% over 3 years
**Break-Even:** Month 18

**Risk Level:** Medium (technical feasible, market validation needed)
**Opportunity Level:** High (no competitors, strong demand signals)

**Decision:** ✅ **RECOMMENDED - PROCEED**

---

## Appendix A: Blender API Quick Reference

### Core Modules

**bpy.context**
- Current scene: `bpy.context.scene`
- Selected objects: `bpy.context.selected_objects`
- Active object: `bpy.context.active_object`

**bpy.data**
- All meshes: `bpy.data.meshes`
- All materials: `bpy.data.materials`
- All images: `bpy.data.images`

**bpy.ops**
- Import GLB: `bpy.ops.import_scene.gltf(filepath='...')`
- Export FBX: `bpy.ops.export_scene.fbx(filepath='...')`
- Render: `bpy.ops.render.render(animation=True)`

### Common Operations

**Clear Scene:**
```python
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
```

**Add Object:**
```python
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
```

**Set Render Settings:**
```python
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.filepath = '/path/to/output.png'
```

---

## Appendix B: Resource Links

**Official Documentation:**
- Blender Python API: https://docs.blender.org/api/current/
- Rigify Add-on: https://docs.blender.org/manual/en/latest/addons/rigging/rigify.html
- Blender Manual: https://docs.blender.org/manual/en/latest/

**Community Resources:**
- Blender Stack Exchange: https://blender.stackexchange.com/
- Blender Artists Forum: https://blenderartists.org/
- Blender Studio Pipeline: https://studio.blender.org/pipeline/

**Code Examples:**
- Blender API Examples (GitHub): https://github.com/blender/blender/tree/main/doc/python_api/examples
- Blender Scripts Collection: https://github.com/topics/blender-scripts

**Render Farms:**
- Blender Open Data (Benchmarks): https://opendata.blender.org/
- RenderStreet: https://render.st/
- SheepIt: https://www.sheepit-renderfarm.com/

---

**END OF DOCUMENT**

---

**Document Metadata:**
- **Version:** 1.0
- **Pages:** ~80 (estimated)
- **Word Count:** ~15,000
- **Last Updated:** November 16, 2025
- **Author:** Platform Architecture Research Team
- **Status:** Strategic Research Complete - Awaiting Go/No-Go Decision
