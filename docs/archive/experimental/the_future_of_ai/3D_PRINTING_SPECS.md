# 🗿 Phase 3: 3D Printable Models - Technical Specifications

**Date:** November 5, 2025
**Status:** 📋 Planning Phase
**Priority:** ⭐⭐⭐ MEDIUM
**Complexity:** 🔴 High
**Time Estimate:** 2-3 weeks development, 1 week testing
**Revenue Potential:** $30-50 per figurine (with fulfillment), $3-10 per STL file

---

## 🎯 Overview

**Goal:** Enable users to convert AI-generated 2D images into 3D printable models (STL/OBJ files) that can be printed on any 3D printer.

**Why This Feature:**
- ✅ Highest "wow factor" - 2D art becomes physical 3D object!
- ✅ Growing 3D printing market ($20B+ consumer segment)
- ✅ Digital downloads (passive income) OR fulfillment service
- ✅ Unique competitive advantage
- ✅ Appeals to collectors, gamers, artists

**Technology:** AI-powered 2D → 3D conversion via Meshy.ai API

**User Journey:**
```
1. User creates AI image (character, object, etc.)
2. User clicks "Create 3D Model" button
3. System sends image to Meshy.ai (2-5 min processing)
4. System receives 3D model (STL/OBJ/FBX)
5. System optimizes for 3D printing
6. User previews 3D model in browser
7. User downloads STL file OR orders print from Shapeways
```

---

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────┐
│      Donkey Betz Platform (Current)         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Generate │→ │ Upscale  │→ │  Enhance │  │
│  │Character │  │   4K     │  │  Detail  │  │
│  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────┘
                    ▼
        ┌───────────────────────┐
        │  NEW: 3D Model Module │
        └───────────────────────┘
                    ▼
        ┌───────────────────────┐
        │     Meshy.ai API      │
        │  - Image → 3D (AI)    │
        │  - Task Management    │
        │  - Model Download     │
        └───────────────────────┘
                    ▼
        ┌───────────────────────┐
        │  Model Optimization   │
        │  - Manifold Check     │
        │  - Scale to Size      │
        │  - Add Base (optional)│
        │  - Repair Holes       │
        └───────────────────────┘
                    ▼
        ┌───────────────────────┐
        │  3D Viewer (Browser)  │
        │  - Three.js           │
        │  - Rotate/Inspect     │
        │  - Measurements       │
        └───────────────────────┘
                    ▼
    ┌───────┴────────┬──────────────┐
    ▼                ▼              ▼
┌─────────┐    ┌──────────┐   ┌─────────┐
│Download │    │Print Self│   │Shapeways│
│STL File │    │(FDM/Resin│   │ Order   │
└─────────┘    │Printer)  │   └─────────┘
               └──────────┘
```

### Data Flow

```
AI Generated Image (4K portrait/object)
        ▼
┌──────────────────┐
│ Upload to CDN    │ (High-res reference image)
└────────┬─────────┘
         ▼
┌──────────────────┐
│ Meshy.ai API     │
│ POST /image-to-3d│ (2-5 min processing)
└────────┬─────────┘
         ▼
┌──────────────────┐
│ Poll Task Status │ (Check every 10s)
│ GET /tasks/{id}  │
└────────┬─────────┘
         ▼
┌──────────────────┐
│ Task Complete    │
│ Download Model   │ (GLB/STL/OBJ/FBX)
└────────┬─────────┘
         ▼
┌──────────────────┐
│ Mesh Analysis    │
│ - Poly count     │
│ - Manifold check │
│ - Dimensions     │
│ - Volume         │
└────────┬─────────┘
         ▼
┌──────────────────┐
│ Optimization     │
│ - Repair mesh    │
│ - Scale to size  │
│ - Add base       │
│ - Simplify poly  │
└────────┬─────────┘
         ▼
┌──────────────────┐
│ Generate Preview │
│ - Front view     │
│ - Side view      │
│ - Top view       │
│ - 3D turntable   │
└────────┬─────────┘
         ▼
┌──────────────────┐
│ Save to Database │
│ - All formats    │
│ - Metadata       │
│ - Print specs    │
└────────┬─────────┘
         ▼
    ┌────┴─────────────┐
    ▼                  ▼
┌────────┐      ┌──────────────┐
│Download│      │Optional:     │
│STL/OBJ │      │Send to       │
│Files   │      │Shapeways API │
└────────┘      └──────────────┘
```

---

## 💾 Database Schema

### New Models

```python
# content/models.py

class ThreeDModel(models.Model):
    """3D printable models from 2D images"""
    product = models.OneToOneField(PhysicalProduct, on_delete=models.CASCADE, related_name='model_3d')

    # Source image
    source_image = models.ForeignKey('ImageHistory', on_delete=models.SET_NULL, null=True)

    # Meshy.ai tracking
    meshy_task_id = models.CharField(max_length=100)
    meshy_status = models.CharField(max_length=50)
    # Status: 'pending', 'processing', 'succeeded', 'failed'

    processing_time_seconds = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Model files (multiple formats)
    glb_file = models.FileField(upload_to='3d/glb/', null=True)  # GL Binary format
    stl_file = models.FileField(upload_to='3d/stl/')             # Standard for 3D printing
    obj_file = models.FileField(upload_to='3d/obj/', null=True)  # Wavefront OBJ
    fbx_file = models.FileField(upload_to='3d/fbx/', null=True)  # Autodesk FBX

    # Model properties
    poly_count = models.IntegerField()
    vertex_count = models.IntegerField()
    face_count = models.IntegerField()
    is_manifold = models.BooleanField(default=False)
    # Manifold = watertight mesh (printable)

    is_optimized = models.BooleanField(default=False)
    # Has been processed for printing

    # Dimensions (in mm)
    bounding_box_x = models.FloatField()  # Width
    bounding_box_y = models.FloatField()  # Height
    bounding_box_z = models.FloatField()  # Depth
    volume_cm3 = models.FloatField()      # Volume for material calc

    # Original scale vs printable scale
    original_scale = models.FloatField(default=1.0)
    recommended_scale_mm = models.FloatField()  # Suggested print height

    # Print recommendations
    MATERIAL_CHOICES = [
        ('pla', 'PLA (Easy, beginner)'),
        ('abs', 'ABS (Strong, durable)'),
        ('petg', 'PETG (Flexible, strong)'),
        ('resin', 'Resin (High detail)'),
        ('tpu', 'TPU (Flexible)'),
    ]
    recommended_material = models.CharField(max_length=20, choices=MATERIAL_CHOICES, default='pla')

    supports_needed = models.BooleanField(default=False)
    # Does model need support structures?

    infill_percent = models.IntegerField(default=20)
    # Recommended infill percentage

    # Print time/cost estimates
    estimated_print_time_hours = models.FloatField(null=True, blank=True)
    estimated_material_grams = models.FloatField(null=True, blank=True)
    estimated_material_cost_usd = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Preview images (rendered views)
    preview_front = models.ImageField(upload_to='3d/previews/')
    preview_side = models.ImageField(upload_to='3d/previews/', null=True)
    preview_top = models.ImageField(upload_to='3d/previews/', null=True)
    preview_angle = models.ImageField(upload_to='3d/previews/', null=True)

    # 3D viewer thumbnail (for gallery)
    thumbnail_image = models.ImageField(upload_to='3d/thumbnails/')

    # Optimization history
    optimization_log = models.JSONField(default=dict)
    # Example: {
    #     "original_poly_count": 50000,
    #     "optimized_poly_count": 10000,
    #     "manifold_repairs": 3,
    #     "holes_filled": 2,
    #     "scale_factor": 0.5
    # }

    # User customizations
    custom_scale_factor = models.FloatField(default=1.0)
    add_base_platform = models.BooleanField(default=True)
    base_height_mm = models.FloatField(default=2.0)
    base_shape = models.CharField(max_length=20, default='circular')
    # Shapes: 'circular', 'square', 'rounded_square', 'none'

    # Download tracking
    download_count = models.IntegerField(default=0)
    last_downloaded_at = models.DateTimeField(null=True, blank=True)

    # Shapeways integration (optional)
    shapeways_model_id = models.CharField(max_length=100, null=True, blank=True)
    shapeways_url = models.URLField(null=True, blank=True)
    shapeways_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = '3d_models'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['meshy_task_id']),
            models.Index(fields=['meshy_status']),
            models.Index(fields=['-created_at']),
        ]

    def get_file_size_mb(self, format='stl'):
        """Get file size in MB for specific format"""
        file_field = getattr(self, f'{format}_file', None)
        if file_field and hasattr(file_field, 'size'):
            return round(file_field.size / (1024 * 1024), 2)
        return 0

    def calculate_print_estimates(self, scale_mm=100):
        """
        Calculate print time and material cost

        Rough estimates based on:
        - 0.2mm layer height
        - 20% infill
        - 50mm/s print speed
        - $20/kg PLA filament
        """
        # Scale volume
        scale_factor = scale_mm / self.recommended_scale_mm
        volume_cm3 = self.volume_cm3 * (scale_factor ** 3)

        # PLA density: ~1.24 g/cm³
        # With 20% infill: multiply by 0.3 (shell + infill)
        material_grams = volume_cm3 * 1.24 * 0.3

        # Material cost ($20/kg)
        material_cost = (material_grams / 1000) * 20

        # Print time (very rough):
        # Assume 2 hours per 100g at 50mm/s
        print_hours = (material_grams / 100) * 2

        self.estimated_print_time_hours = round(print_hours, 1)
        self.estimated_material_grams = round(material_grams, 1)
        self.estimated_material_cost_usd = round(material_cost, 2)
        self.save(update_fields=['estimated_print_time_hours', 'estimated_material_grams', 'estimated_material_cost_usd'])

    def increment_download(self):
        """Track downloads"""
        from django.utils import timezone
        self.download_count += 1
        self.last_downloaded_at = timezone.now()
        self.save(update_fields=['download_count', 'last_downloaded_at'])


class PrintJob(models.Model):
    """Track actual print jobs (for users who print)"""
    model_3d = models.ForeignKey(ThreeDModel, on_delete=models.CASCADE, related_name='print_jobs')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Print settings used
    scale_mm = models.FloatField()
    material_used = models.CharField(max_length=20)
    infill_percent = models.IntegerField()
    layer_height_mm = models.FloatField(default=0.2)
    supports = models.BooleanField()

    # Actual results
    print_status = models.CharField(max_length=50)
    # Status: 'started', 'completed', 'failed'

    actual_print_time_hours = models.FloatField(null=True, blank=True)
    actual_material_grams = models.FloatField(null=True, blank=True)

    # Quality feedback
    quality_rating = models.IntegerField(null=True, blank=True)  # 1-5 stars
    notes = models.TextField(blank=True)

    # Photos of finished print
    photo_1 = models.ImageField(upload_to='prints/', null=True, blank=True)
    photo_2 = models.ImageField(upload_to='prints/', null=True, blank=True)
    photo_3 = models.ImageField(upload_to='prints/', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'print_jobs'
        ordering = ['-created_at']
```

---

## 🔧 Backend Implementation

### File Structure

```
content/
├── physical_products/
│   ├── __init__.py
│   ├── meshy_client.py      # Meshy.ai API client
│   ├── model_optimizer.py   # 3D mesh optimization
│   ├── print_calculator.py  # Print time/cost estimates
│   ├── shapeways_client.py  # Optional: Shapeways integration
│   └── model_viewer.py      # Generate preview images
│
└── models.py (updated)      # Add ThreeDModel
```

### Meshy.ai API Client

```python
# content/physical_products/meshy_client.py

import requests
import time
from django.conf import settings
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class MeshyClient:
    """Meshy.ai API client for 2D → 3D conversion"""

    BASE_URL = "https://api.meshy.ai/v2"

    def __init__(self):
        self.api_key = settings.MESHY_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make HTTP request to Meshy.ai API"""
        url = f"{self.BASE_URL}/{endpoint}"

        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data)

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Meshy.ai API error: {str(e)}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
            raise

    def create_image_to_3d_task(
        self,
        image_url: str,
        enable_pbr: bool = False,
        style: str = 'realistic',
        negative_prompt: str = '',
        ai_model: str = 'meshy-4'
    ) -> Dict:
        """
        Create a new image-to-3D conversion task

        Args:
            image_url: URL to high-res reference image
            enable_pbr: Enable PBR materials (textures)
            style: 'realistic', 'cartoon', 'low-poly', 'voxel'
            negative_prompt: Things to avoid
            ai_model: 'meshy-4' (latest), 'meshy-3', 'meshy-2'

        Returns:
            {
                'id': 'task_id',
                'status': 'pending',
                'created_at': '2025-11-05T...'
            }
        """
        data = {
            "image_url": image_url,
            "enable_pbr": enable_pbr,
            "style": style,
            "negative_prompt": negative_prompt,
            "ai_model": ai_model
        }

        result = self._make_request("POST", "image-to-3d", data)
        logger.info(f"Created Meshy task: {result.get('id')}")
        return result

    def get_task_status(self, task_id: str) -> Dict:
        """
        Check status of 3D conversion task

        Returns:
            {
                'id': 'task_id',
                'status': 'pending' | 'processing' | 'succeeded' | 'failed',
                'progress': 0-100,
                'model_urls': {...},  # When succeeded
                'thumbnail_url': '...',
                'video_url': '...'  # Turntable video
            }
        """
        result = self._make_request("GET", f"image-to-3d/{task_id}")
        return result

    def download_model(self, model_url: str, output_path: str) -> str:
        """
        Download 3D model file

        Args:
            model_url: URL from task result
            output_path: Local path to save

        Returns: output_path
        """
        response = requests.get(model_url, stream=True)
        response.raise_for_status()

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        logger.info(f"Downloaded model to {output_path}")
        return output_path

    def convert_image_to_3d(
        self,
        image_url: str,
        max_wait_seconds: int = 300,
        poll_interval: int = 10
    ) -> Dict:
        """
        Complete pipeline: Create task → Poll → Download

        Args:
            image_url: URL to source image
            max_wait_seconds: Max time to wait (default 5 min)
            poll_interval: Seconds between status checks

        Returns:
            {
                'success': bool,
                'task_id': str,
                'status': str,
                'model_urls': {...},
                'thumbnail_url': str,
                'video_url': str
            }
        """
        # Step 1: Create task
        logger.info(f"Creating 3D conversion task for {image_url}")
        task = self.create_image_to_3d_task(image_url)
        task_id = task['id']

        # Step 2: Poll for completion
        start_time = time.time()

        while time.time() - start_time < max_wait_seconds:
            status_result = self.get_task_status(task_id)
            status = status_result['status']
            progress = status_result.get('progress', 0)

            logger.info(f"Task {task_id}: {status} ({progress}%)")

            if status == 'succeeded':
                logger.info(f"3D conversion succeeded!")
                return {
                    'success': True,
                    'task_id': task_id,
                    'status': status,
                    'model_urls': status_result.get('model_urls', {}),
                    'thumbnail_url': status_result.get('thumbnail_url'),
                    'video_url': status_result.get('video_url')
                }

            elif status == 'failed':
                error = status_result.get('error', 'Unknown error')
                logger.error(f"3D conversion failed: {error}")
                return {
                    'success': False,
                    'task_id': task_id,
                    'status': status,
                    'error': error
                }

            # Still processing
            time.sleep(poll_interval)

        # Timeout
        logger.warning(f"Task {task_id} timeout after {max_wait_seconds}s")
        return {
            'success': False,
            'task_id': task_id,
            'status': 'timeout',
            'error': f'Timeout after {max_wait_seconds} seconds'
        }
```

### 3D Model Optimizer

```python
# content/physical_products/model_optimizer.py

import trimesh
import numpy as np
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class ModelOptimizer:
    """Optimize 3D models for printing"""

    def __init__(self):
        pass

    def load_model(self, file_path: str) -> trimesh.Trimesh:
        """Load 3D model from file"""
        mesh = trimesh.load(file_path)
        logger.info(f"Loaded mesh: {mesh.vertices.shape[0]} vertices, {mesh.faces.shape[0]} faces")
        return mesh

    def is_manifold(self, mesh: trimesh.Trimesh) -> bool:
        """
        Check if mesh is manifold (watertight)

        A manifold mesh:
        - Has no holes
        - Every edge is shared by exactly 2 faces
        - Can be 3D printed
        """
        return mesh.is_watertight and mesh.is_volume

    def repair_mesh(self, mesh: trimesh.Trimesh) -> trimesh.Trimesh:
        """
        Repair common mesh issues

        - Remove duplicate vertices
        - Fill small holes
        - Fix normals
        """
        logger.info("Repairing mesh...")

        # Remove duplicate vertices
        mesh.merge_vertices()

        # Fill holes (small ones)
        mesh.fill_holes()

        # Fix inverted normals
        mesh.fix_normals()

        # Remove degenerate faces
        mesh.remove_degenerate_faces()

        # Remove duplicate faces
        mesh.remove_duplicate_faces()

        logger.info(f"Repair complete: manifold={mesh.is_watertight}")
        return mesh

    def simplify_mesh(
        self,
        mesh: trimesh.Trimesh,
        target_faces: int = 10000
    ) -> trimesh.Trimesh:
        """
        Reduce polygon count while preserving shape

        Args:
            mesh: Input mesh
            target_faces: Desired face count

        Returns: Simplified mesh
        """
        if mesh.faces.shape[0] <= target_faces:
            logger.info(f"Mesh already has {mesh.faces.shape[0]} faces (target: {target_faces})")
            return mesh

        logger.info(f"Simplifying from {mesh.faces.shape[0]} to {target_faces} faces")

        # Use trimesh simplification
        simplified = mesh.simplify_quadric_decimation(target_faces)

        logger.info(f"Simplified to {simplified.faces.shape[0]} faces")
        return simplified

    def scale_to_size(
        self,
        mesh: trimesh.Trimesh,
        target_height_mm: float
    ) -> Tuple[trimesh.Trimesh, float]:
        """
        Scale mesh to specific height in mm

        Args:
            mesh: Input mesh
            target_height_mm: Desired height

        Returns: (scaled_mesh, scale_factor)
        """
        # Get current height (Y axis typically)
        bounds = mesh.bounds
        current_height = bounds[1][1] - bounds[0][1]

        # Calculate scale factor
        scale_factor = target_height_mm / current_height

        # Apply scale
        mesh.apply_scale(scale_factor)

        logger.info(f"Scaled mesh by {scale_factor:.3f}x to {target_height_mm}mm height")
        return mesh, scale_factor

    def add_base_platform(
        self,
        mesh: trimesh.Trimesh,
        base_height_mm: float = 2.0,
        base_shape: str = 'circular',
        margin_mm: float = 2.0
    ) -> trimesh.Trimesh:
        """
        Add a base platform for stability

        Args:
            mesh: Input mesh
            base_height_mm: Height of base
            base_shape: 'circular', 'square', 'rounded_square'
            margin_mm: Extra space around mesh

        Returns: Mesh with base
        """
        # Get mesh bounds
        bounds = mesh.bounds
        min_x, min_y, min_z = bounds[0]
        max_x, max_y, max_z = bounds[1]

        # Calculate base dimensions
        width = (max_x - min_x) + (2 * margin_mm)
        depth = (max_z - min_z) + (2 * margin_mm)
        center_x = (max_x + min_x) / 2
        center_z = (max_z + min_z) / 2

        # Create base mesh
        if base_shape == 'circular':
            radius = max(width, depth) / 2
            base = trimesh.creation.cylinder(
                radius=radius,
                height=base_height_mm,
                sections=32
            )
        elif base_shape == 'square':
            base = trimesh.creation.box([width, base_height_mm, depth])
        elif base_shape == 'rounded_square':
            # Create rounded rectangle
            base = trimesh.creation.box([width, base_height_mm, depth])
            # TODO: Add rounded corners
        else:
            raise ValueError(f"Unknown base shape: {base_shape}")

        # Position base at bottom of mesh
        base_center_y = min_y - (base_height_mm / 2)
        base.apply_translation([center_x, base_center_y, center_z])

        # Combine mesh and base
        combined = trimesh.util.concatenate([mesh, base])

        logger.info(f"Added {base_shape} base platform ({base_height_mm}mm height)")
        return combined

    def analyze_mesh(self, mesh: trimesh.Trimesh) -> Dict:
        """
        Analyze mesh properties

        Returns comprehensive metadata
        """
        bounds = mesh.bounds

        analysis = {
            'vertices': mesh.vertices.shape[0],
            'faces': mesh.faces.shape[0],
            'edges': len(mesh.edges_unique),
            'is_manifold': mesh.is_watertight and mesh.is_volume,
            'is_watertight': mesh.is_watertight,
            'bounding_box': {
                'x': float(bounds[1][0] - bounds[0][0]),
                'y': float(bounds[1][1] - bounds[0][1]),
                'z': float(bounds[1][2] - bounds[0][2])
            },
            'volume_cm3': float(mesh.volume) / 1000,  # Convert mm³ to cm³
            'surface_area_cm2': float(mesh.area) / 100,  # Convert mm² to cm²
            'center_of_mass': mesh.center_mass.tolist(),
            'is_convex': mesh.is_convex
        }

        return analysis

    def optimize_for_printing(
        self,
        input_path: str,
        output_path: str,
        target_height_mm: float = 100,
        max_faces: int = 20000,
        add_base: bool = True,
        base_height_mm: float = 2.0,
        base_shape: str = 'circular'
    ) -> Dict:
        """
        Complete optimization pipeline

        Steps:
        1. Load mesh
        2. Analyze
        3. Repair if needed
        4. Simplify if too detailed
        5. Scale to target height
        6. Add base (optional)
        7. Final analysis
        8. Save optimized mesh

        Returns: Metadata dict
        """
        logger.info(f"Optimizing {input_path} for 3D printing")

        # Load
        mesh = self.load_model(input_path)
        original_analysis = self.analyze_mesh(mesh)

        # Repair
        if not original_analysis['is_manifold']:
            mesh = self.repair_mesh(mesh)

        # Simplify
        if mesh.faces.shape[0] > max_faces:
            mesh = self.simplify_mesh(mesh, target_faces=max_faces)

        # Scale
        mesh, scale_factor = self.scale_to_size(mesh, target_height_mm)

        # Add base
        if add_base:
            mesh = self.add_base_platform(
                mesh,
                base_height_mm=base_height_mm,
                base_shape=base_shape
            )

        # Final analysis
        final_analysis = self.analyze_mesh(mesh)

        # Export
        mesh.export(output_path)
        logger.info(f"Saved optimized mesh to {output_path}")

        return {
            'original': original_analysis,
            'optimized': final_analysis,
            'scale_factor': scale_factor,
            'output_path': output_path
        }
```

### Print Calculator

```python
# content/physical_products/print_calculator.py

from typing import Dict

class PrintCalculator:
    """Calculate print time and material costs"""

    # Material densities (g/cm³)
    MATERIAL_DENSITY = {
        'pla': 1.24,
        'abs': 1.04,
        'petg': 1.27,
        'tpu': 1.21,
        'resin': 1.15
    }

    # Material costs ($/kg)
    MATERIAL_COST = {
        'pla': 20,
        'abs': 25,
        'petg': 25,
        'tpu': 35,
        'resin': 50
    }

    def calculate_material_usage(
        self,
        volume_cm3: float,
        material: str = 'pla',
        infill_percent: int = 20,
        wall_thickness_mm: float = 1.2,
        top_bottom_layers: int = 4,
        layer_height_mm: float = 0.2
    ) -> Dict:
        """
        Calculate material needed for print

        Args:
            volume_cm3: Model volume
            material: Material type
            infill_percent: Infill percentage
            wall_thickness_mm: Shell thickness
            top_bottom_layers: Solid layers top/bottom
            layer_height_mm: Layer height

        Returns:
            {
                'material_grams': float,
                'material_cost_usd': float,
                'material_type': str
            }
        """
        density = self.MATERIAL_DENSITY.get(material, 1.24)

        # Simplified calculation:
        # Shell (walls + top/bottom) ≈ 30% of volume
        # Infill = infill_percent of remaining volume

        shell_volume = volume_cm3 * 0.3
        infill_volume = volume_cm3 * 0.7 * (infill_percent / 100)
        total_volume = shell_volume + infill_volume

        # Calculate mass
        material_grams = total_volume * density

        # Calculate cost
        cost_per_kg = self.MATERIAL_COST.get(material, 20)
        material_cost = (material_grams / 1000) * cost_per_kg

        return {
            'material_grams': round(material_grams, 1),
            'material_cost_usd': round(material_cost, 2),
            'material_type': material,
            'infill_percent': infill_percent
        }

    def calculate_print_time(
        self,
        volume_cm3: float,
        height_mm: float,
        layer_height_mm: float = 0.2,
        print_speed_mm_s: int = 50,
        infill_percent: int = 20
    ) -> Dict:
        """
        Estimate print time

        This is a very rough estimate. Actual time depends on:
        - Printer speed
        - Acceleration settings
        - Travel moves
        - Cooling/heating time

        Returns:
            {
                'total_hours': float,
                'total_minutes': int,
                'breakdown': {...}
            }
        """
        # Number of layers
        num_layers = int(height_mm / layer_height_mm)

        # Very rough time per layer (seconds)
        # Assumes average layer takes 1-3 minutes depending on size/infill
        time_per_layer_seconds = 60 + (infill_percent / 100) * 60

        # Total time
        total_seconds = num_layers * time_per_layer_seconds
        total_hours = total_seconds / 3600

        return {
            'total_hours': round(total_hours, 1),
            'total_minutes': int(total_hours * 60),
            'breakdown': {
                'layers': num_layers,
                'layer_height_mm': layer_height_mm,
                'avg_time_per_layer_seconds': int(time_per_layer_seconds)
            }
        }

    def get_print_recommendations(
        self,
        volume_cm3: float,
        height_mm: float,
        width_mm: float,
        depth_mm: float
    ) -> Dict:
        """
        Get recommended print settings

        Returns optimal settings based on model size/geometry
        """
        # Determine if supports needed
        # (Very simplified - real slicer does overhang analysis)
        supports_needed = height_mm > (width_mm * 2) or height_mm > (depth_mm * 2)

        # Recommend material based on size
        if volume_cm3 > 500:
            material = 'pla'  # Large prints - use cheap PLA
            infill = 10  # Low infill for large prints
        elif volume_cm3 > 100:
            material = 'petg'  # Medium - durable PETG
            infill = 15
        else:
            material = 'resin'  # Small - high detail resin
            infill = 100  # Resin is solid

        # Layer height based on detail needed
        if height_mm < 50:
            layer_height = 0.1  # Fine detail
        elif height_mm < 150:
            layer_height = 0.2  # Standard
        else:
            layer_height = 0.3  # Fast print

        return {
            'recommended_material': material,
            'recommended_infill_percent': infill,
            'recommended_layer_height_mm': layer_height,
            'supports_needed': supports_needed,
            'estimated_difficulty': 'easy' if not supports_needed else 'medium'
        }

    def get_complete_estimate(
        self,
        volume_cm3: float,
        height_mm: float,
        width_mm: float,
        depth_mm: float,
        material: str = None,
        infill_percent: int = None
    ) -> Dict:
        """
        Complete print estimate with recommendations

        Returns all calculations in one call
        """
        # Get recommendations
        recommendations = self.get_print_recommendations(
            volume_cm3, height_mm, width_mm, depth_mm
        )

        # Use recommended or user-specified settings
        material = material or recommendations['recommended_material']
        infill_percent = infill_percent or recommendations['recommended_infill_percent']
        layer_height = recommendations['recommended_layer_height_mm']

        # Calculate material
        material_calc = self.calculate_material_usage(
            volume_cm3,
            material=material,
            infill_percent=infill_percent,
            layer_height_mm=layer_height
        )

        # Calculate time
        time_calc = self.calculate_print_time(
            volume_cm3,
            height_mm,
            layer_height_mm=layer_height,
            infill_percent=infill_percent
        )

        return {
            'recommendations': recommendations,
            'material': material_calc,
            'time': time_calc,
            'total_cost_estimate_usd': round(material_calc['material_cost_usd'] + 2, 2)
            # Add $2 for electricity/wear
        }
```

---

## 🎨 Frontend Implementation

### Three.js 3D Viewer

```html
<!-- In <head> section -->
<script src="https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.160.0/examples/js/controls/OrbitControls.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.160.0/examples/js/loaders/STLLoader.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.160.0/examples/js/loaders/GLTFLoader.js"></script>

<!-- 3D Model Tab -->
<div class="tab-pane fade" id="3d-model">
    <h3 class="mb-4">🗿 3D Figurine Creator</h3>
    <p class="text-muted">Convert your AI images into 3D printable models</p>

    <!-- Step 1: Source Image -->
    <div class="card mb-4">
        <div class="card-header">
            <h5>1. Select Character/Object Image</h5>
        </div>
        <div class="card-body">
            <button class="btn btn-primary" onclick="open3DGalleryModal()">
                Choose from Gallery
            </button>
            <p class="small text-muted mt-2">
                💡 Best results: Front-facing portraits, clear subjects, good lighting
            </p>
            <div id="3dSourcePreview" class="mt-3" style="display:none;">
                <img id="3dSourceImage" src="" class="img-thumbnail" style="max-width:300px;">
            </div>
        </div>
    </div>

    <!-- Step 2: Model Type -->
    <div class="card mb-4">
        <div class="card-header">
            <h5>2. Model Type</h5>
        </div>
        <div class="card-body">
            <div class="btn-group" role="group">
                <input type="radio" class="btn-check" name="modelType" id="modelCharacter" value="character" checked>
                <label class="btn btn-outline-primary" for="modelCharacter">
                    🧑 Character/Portrait
                </label>

                <input type="radio" class="btn-check" name="modelType" id="modelObject" value="object">
                <label class="btn btn-outline-primary" for="modelObject">
                    🎁 Object/Item
                </label>
            </div>
        </div>
    </div>

    <!-- Step 3: Settings -->
    <div class="card mb-4">
        <div class="card-header">
            <h5>3. Print Settings</h5>
        </div>
        <div class="card-body">
            <div class="row g-3">
                <div class="col-md-4">
                    <label class="form-label">Target Height</label>
                    <select id="targetHeight" class="form-select">
                        <option value="50">50mm (2 inches)</option>
                        <option value="75">75mm (3 inches)</option>
                        <option value="100" selected>100mm (4 inches)</option>
                        <option value="150">150mm (6 inches)</option>
                        <option value="200">200mm (8 inches)</option>
                    </select>
                </div>
                <div class="col-md-4">
                    <label class="form-label">Add Base</label>
                    <select id="baseOption" class="form-select">
                        <option value="circular">Circular Base</option>
                        <option value="square">Square Base</option>
                        <option value="rounded">Rounded Square</option>
                        <option value="none">No Base</option>
                    </select>
                </div>
                <div class="col-md-4">
                    <label class="form-label">Detail Level</label>
                    <select id="detailLevel" class="form-select">
                        <option value="medium" selected>Medium (10k polygons)</option>
                        <option value="high">High (20k polygons)</option>
                        <option value="ultra">Ultra (50k polygons)</option>
                    </select>
                </div>
            </div>
        </div>
    </div>

    <!-- Step 4: Generate -->
    <div class="card mb-4">
        <div class="card-body text-center">
            <button class="btn btn-primary btn-lg" onclick="generate3DModel()" id="generate3DBtn">
                🗿 Generate 3D Model (2-5 min)
            </button>

            <div id="3dProgress" class="mt-3" style="display:none;">
                <div class="spinner-border text-primary" role="status"></div>
                <p class="mt-2" id="3dProgressText">Starting 3D conversion...</p>
                <div class="progress">
                    <div id="3dProgressBar" class="progress-bar" role="progressbar" style="width: 0%"></div>
                </div>
            </div>
        </div>
    </div>

    <!-- Results: 3D Viewer -->
    <div id="3dResults" class="card" style="display:none;">
        <div class="card-header bg-success text-white">
            <h5>✅ 3D Model Ready!</h5>
        </div>
        <div class="card-body">
            <div class="row">
                <!-- 3D Viewer -->
                <div class="col-md-8">
                    <h6>Interactive 3D Preview:</h6>
                    <div id="3dViewer" style="width:100%; height:500px; background:#1a1a1a; border-radius:8px;">
                        <!-- Three.js canvas rendered here -->
                    </div>
                    <p class="small text-muted mt-2">
                        🖱️ Left click + drag to rotate | Right click + drag to pan | Scroll to zoom
                    </p>
                </div>

                <!-- Info & Downloads -->
                <div class="col-md-4">
                    <h6>Model Info:</h6>
                    <ul class="list-unstyled small" id="modelInfo">
                        <!-- Populated dynamically -->
                    </ul>

                    <h6 class="mt-3">Print Estimates:</h6>
                    <ul class="list-unstyled small" id="printEstimates">
                        <!-- Populated dynamically -->
                    </ul>

                    <h6 class="mt-3">Download Files:</h6>
                    <div class="d-grid gap-2">
                        <a id="download3D_STL" href="#" class="btn btn-primary" download>
                            📥 Download STL (3D Printing)
                        </a>
                        <a id="download3D_OBJ" href="#" class="btn btn-outline-primary" download>
                            📦 Download OBJ (Universal)
                        </a>
                        <a id="download3D_FBX" href="#" class="btn btn-outline-primary" download>
                            🎨 Download FBX (Animation)
                        </a>
                    </div>

                    <div class="alert alert-info mt-3">
                        <h6>💡 Printing Tips:</h6>
                        <ul class="small mb-0">
                            <li>Use <strong id="recommendedMaterial">PLA</strong> filament</li>
                            <li><span id="supportsNeeded">Supports may be needed</span></li>
                            <li>Recommended infill: <strong id="recommendedInfill">20%</strong></li>
                            <li>Layer height: <strong>0.2mm</strong></li>
                        </ul>
                    </div>

                    <!-- Optional: Shapeways Integration -->
                    <button class="btn btn-outline-success w-100 mt-2" onclick="orderFromShapeways()">
                        🚀 Order Print from Shapeways
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>
```

### JavaScript for 3D Viewer

```javascript
// Three.js scene components
let scene, camera, renderer, controls, currentModel;

function init3DViewer() {
    const container = document.getElementById('3dViewer');

    // Scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1a1a);

    // Camera
    camera = new THREE.PerspectiveCamera(
        45,
        container.clientWidth / container.clientHeight,
        0.1,
        1000
    );
    camera.position.set(0, 0, 200);

    // Renderer
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);

    // Controls
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;

    // Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(0, 1, 1);
    scene.add(directionalLight);

    // Grid
    const gridHelper = new THREE.GridHelper(200, 20);
    scene.add(gridHelper);

    // Animation loop
    function animate() {
        requestAnimationFrame(animate);
        controls.update();
        renderer.render(scene, camera);
    }
    animate();

    // Handle window resize
    window.addEventListener('resize', () => {
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
    });
}

function load3DModel(modelUrl, format = 'stl') {
    // Remove existing model
    if (currentModel) {
        scene.remove(currentModel);
    }

    // Load new model
    if (format === 'stl') {
        const loader = new THREE.STLLoader();
        loader.load(modelUrl, (geometry) => {
            const material = new THREE.MeshPhongMaterial({
                color: 0xfbbd24,
                specular: 0x111111,
                shininess: 200
            });
            currentModel = new THREE.Mesh(geometry, material);

            // Center model
            geometry.computeBoundingBox();
            const center = new THREE.Vector3();
            geometry.boundingBox.getCenter(center);
            currentModel.geometry.translate(-center.x, -center.y, -center.z);

            // Add to scene
            scene.add(currentModel);

            // Adjust camera
            const box = new THREE.Box3().setFromObject(currentModel);
            const size = box.getSize(new THREE.Vector3());
            const maxDim = Math.max(size.x, size.y, size.z);
            camera.position.z = maxDim * 2;
        });
    }
    // Similar loaders for GLB/OBJ/FBX
}

async function generate3DModel() {
    // ... (similar to laser engraving generation)
    // Call /api/3d/convert/
    // Poll for status
    // Load result into viewer
}
```

---

## 💰 Business Models

### 1. Digital Downloads (Recommended Start)
- STL file only: $3-5
- Full package (STL + OBJ + FBX): $10-15
- Cost: ~$0.20/model → 95%+ profit margin
- Scalable: Sell same file unlimited times

### 2. Print-on-Demand (Shapeways)
- Partner with Shapeways
- User orders print directly
- You take commission
- No inventory/fulfillment hassle

### 3. Subscription Add-On
- +$15/month: 5 3D models
- +$35/month: Unlimited models
- Recurring revenue stream

### 4. Marketplace
- Users can sell their models
- Platform takes 30% commission
- Community-driven content

---

## 🧪 Testing Checklist

- [ ] Meshy.ai API integration working
- [ ] 2D → 3D conversion quality acceptable
- [ ] Manifold checking works
- [ ] Model optimization reduces poly count
- [ ] STL files open in slicers (Cura, PrusaSlicer)
- [ ] 3D viewer displays models correctly
- [ ] Download links functional
- [ ] Print estimates accurate (±20%)
- [ ] At least 3 test prints successful
- [ ] User feedback positive

---

**Status:** 📋 Ready for Review
**Next:** Validate Meshy.ai API, create test prototype
