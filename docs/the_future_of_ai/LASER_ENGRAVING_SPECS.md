# 🔥 Phase 2: Laser Engraving Files - Technical Specifications

**Date:** November 5, 2025
**Status:** 📋 Planning Phase
**Priority:** ⭐⭐⭐⭐ HIGH
**Complexity:** 🟡 Medium
**Time Estimate:** 1-2 weeks development, 3-5 days testing
**Revenue Potential:** $5-20 per digital file

---

## 🎯 Overview

**Goal:** Enable users to convert AI-generated images into laser-engravable vector files (SVG, DXF, G-code) optimized for different materials (wood, metal, leather, acrylic).

**Why This Feature:**
- ✅ Unique market differentiator (no competitor does this!)
- ✅ Appeals to DIY/maker community
- ✅ Digital downloads = passive income (sell same file many times)
- ✅ High perceived value ($10-20 per file)
- ✅ Low cost to produce (~$0.03 per file)

**User Journey:**
```
1. User creates AI image in Donkey Betz
2. User clicks "Create Laser File" button
3. User selects material type (wood, metal, leather, etc.)
4. System converts to vector + applies laser settings
5. User downloads SVG/DXF/G-code files
6. User engraves on their laser machine
```

---

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────┐
│      Donkey Betz Platform (Current)         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Generate │→ │Remove BG │→ │  Enhance │  │
│  │  Image   │  │(optional)│  │Contrast  │  │
│  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────┘
                    ▼
        ┌───────────────────────┐
        │  NEW: Vector Module   │
        └───────────────────────┘
                    ▼
        ┌───────────────────────┐
        │  Bitmap → Vector      │
        │  - Potrace Algorithm  │
        │  - Edge Detection     │
        │  - Path Generation    │
        └───────────────────────┘
                    ▼
        ┌───────────────────────┐
        │  Material Optimizer   │
        │  - Wood Settings      │
        │  - Metal Settings     │
        │  - Leather Settings   │
        │  - Acrylic Settings   │
        └───────────────────────┘
                    ▼
        ┌───────────────────────┐
        │  File Export          │
        │  - SVG (universal)    │
        │  - DXF (CAD format)   │
        │  - G-code (machine)   │
        └───────────────────────┘
```

### Data Flow

```
AI Generated Image (PNG/JPEG)
        ▼
┌──────────────────┐
│ Preprocessing    │
│ - Grayscale      │
│ - Contrast Boost │
│ - Edge Enhance   │
└────────┬─────────┘
         ▼
┌──────────────────┐
│ Bitmap Tracing   │ (Potrace algorithm)
│ - Detect edges   │
│ - Create paths   │
│ - Smooth curves  │
└────────┬─────────┘
         ▼
┌──────────────────┐
│ Vector Format    │ (SVG paths)
│ <path d="M10,20  │
│ L30,40 Z"/>      │
└────────┬─────────┘
         ▼
┌──────────────────┐
│ Material Specs   │
│ Apply laser      │
│ settings for     │
│ chosen material  │
└────────┬─────────┘
         ▼
    ┌────┴─────┬──────────┐
    ▼          ▼          ▼
┌───────┐  ┌───────┐  ┌────────┐
│  SVG  │  │  DXF  │  │ G-code │
│ File  │  │ File  │  │  File  │
└───────┘  └───────┘  └────────┘
    ▼          ▼          ▼
┌────────────────────────────┐
│ User Downloads & Engraves  │
└────────────────────────────┘
```

---

## 💾 Database Schema

### New Models

```python
# content/models.py

class LaserEngraving(models.Model):
    """Laser engraving file specifications"""
    product = models.OneToOneField(PhysicalProduct, on_delete=models.CASCADE, related_name='laser_data')

    # Material specifications
    MATERIAL_CHOICES = [
        ('wood', 'Wood'),
        ('plywood', 'Plywood'),
        ('mdf', 'MDF'),
        ('bamboo', 'Bamboo'),
        ('leather', 'Leather'),
        ('acrylic', 'Acrylic'),
        ('metal', 'Metal (Anodized)'),
        ('glass', 'Glass'),
        ('cardboard', 'Cardboard'),
        ('fabric', 'Fabric'),
    ]
    material_type = models.CharField(max_length=50, choices=MATERIAL_CHOICES)

    # Vector files
    vector_file_svg = models.FileField(upload_to='laser/svg/')
    vector_file_dxf = models.FileField(upload_to='laser/dxf/', null=True, blank=True)
    gcode_file = models.FileField(upload_to='laser/gcode/', null=True, blank=True)

    # Preview images
    preview_image = models.ImageField(upload_to='laser/previews/')
    preview_on_material = models.ImageField(upload_to='laser/previews/', null=True, blank=True)

    # Vector properties
    path_count = models.IntegerField()  # Number of vector paths
    total_length_mm = models.FloatField()  # Total path length
    bounding_box = models.JSONField()  # {"width": 100, "height": 100, "units": "mm"}

    # Laser specifications
    power_percent = models.IntegerField()  # 1-100%
    speed_mm_per_min = models.IntegerField()  # 100-3000 mm/min typical
    passes = models.IntegerField(default=1)
    depth_estimate_mm = models.FloatField()  # Estimated engraving depth

    # Advanced settings
    frequency_hz = models.IntegerField(null=True, blank=True)  # Pulse frequency
    dpi = models.IntegerField(default=300)  # Resolution for raster
    mode = models.CharField(max_length=20, default='vector')  # 'vector' or 'raster'

    # Dimensions (actual size on material)
    width_mm = models.FloatField()
    height_mm = models.FloatField()
    width_inches = models.FloatField()
    height_inches = models.FloatField()

    # Machine compatibility
    MACHINE_CHOICES = [
        ('generic', 'Generic (Universal SVG)'),
        ('epilog', 'Epilog Laser'),
        ('glowforge', 'Glowforge'),
        ('trotec', 'Trotec'),
        ('universal', 'Universal Laser Systems'),
        ('boss', 'Boss Laser'),
        ('lightburn', 'LightBurn Compatible'),
    ]
    machine_type = models.CharField(max_length=50, choices=MACHINE_CHOICES, default='generic')

    # Conversion settings used
    conversion_settings = models.JSONField()
    # Example: {
    #     "threshold": 128,
    #     "detail_level": "high",
    #     "smoothing": 0.5,
    #     "corner_threshold": 90
    # }

    # Processing metadata
    conversion_time_seconds = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    downloaded_count = models.IntegerField(default=0)

    class Meta:
        db_table = 'laser_engravings'
        ordering = ['-created_at']

    def get_file_size_mb(self, file_field):
        """Get file size in MB"""
        if file_field and hasattr(file_field, 'size'):
            return round(file_field.size / (1024 * 1024), 2)
        return 0

    def increment_download(self):
        """Track downloads"""
        self.downloaded_count += 1
        self.save(update_fields=['downloaded_count'])
```

---

## 🔧 Backend Implementation

### File Structure

```
content/
├── physical_products/
│   ├── __init__.py
│   ├── vector_convert.py    # Bitmap → Vector conversion
│   ├── laser_specs.py       # Material-specific laser settings
│   ├── gcode_generator.py   # G-code generation
│   └── format_exporters.py  # SVG/DXF export utilities
│
└── models.py (updated)      # Add LaserEngraving model
```

### Vector Conversion Service

```python
# content/physical_products/vector_convert.py

from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import potrace
import numpy as np
import svgwrite
import ezdxf
from typing import Dict, Tuple, Optional
import logging
import io

logger = logging.getLogger(__name__)

class VectorConverter:
    """Convert bitmap images to vector paths for laser engraving"""

    def __init__(self):
        pass

    def preprocess_image(
        self,
        image_path: str,
        target_size: Tuple[int, int] = (1000, 1000),
        contrast_factor: float = 1.5,
        edge_enhance: bool = True
    ) -> np.ndarray:
        """
        Preprocess image for optimal vector conversion

        Steps:
        1. Convert to grayscale
        2. Resize to target resolution
        3. Enhance contrast
        4. Enhance edges (optional)
        5. Convert to binary bitmap

        Returns: numpy array (binary bitmap)
        """
        # Load image
        img = Image.open(image_path)

        # Convert to grayscale
        if img.mode != 'L':
            img = img.convert('L')

        # Resize maintaining aspect ratio
        img.thumbnail(target_size, Image.Resampling.LANCZOS)

        # Enhance contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(contrast_factor)

        # Edge enhancement (for fine details)
        if edge_enhance:
            img = img.filter(ImageFilter.EDGE_ENHANCE)

        # Convert to binary (threshold)
        threshold = 128
        img = img.point(lambda p: 255 if p > threshold else 0, mode='1')

        # Convert to numpy array
        bitmap = np.array(img, dtype=np.uint8)

        return bitmap

    def bitmap_to_vector(
        self,
        bitmap: np.ndarray,
        turdsize: int = 2,
        turnpolicy: str = 'minority',
        alphamax: float = 1.0
    ) -> potrace.Path:
        """
        Convert binary bitmap to vector paths using Potrace algorithm

        Args:
            bitmap: Binary bitmap (numpy array)
            turdsize: Suppress speckles (smaller = more detail)
            turnpolicy: How to resolve ambiguities ('minority', 'majority', etc.)
            alphamax: Corner threshold (0-1.33, larger = smoother)

        Returns: Potrace path object
        """
        # Create Potrace bitmap
        bm = potrace.Bitmap(bitmap)

        # Trace bitmap to paths
        path = bm.trace(
            turdsize=turdsize,
            turnpolicy=turnpolicy,
            alphamax=alphamax,
            opticurve=True,
            opttolerance=0.2
        )

        return path

    def path_to_svg(
        self,
        path: potrace.Path,
        width: int,
        height: int,
        stroke_width: float = 0.5,
        fill: str = 'none',
        stroke: str = 'black'
    ) -> str:
        """
        Convert Potrace path to SVG string

        Returns: SVG XML string
        """
        dwg = svgwrite.Drawing(size=(f'{width}mm', f'{height}mm'))
        dwg.viewbox(0, 0, width, height)

        # Extract curves from path
        for curve in path:
            path_data = []

            # Start point
            start = curve.start_point
            path_data.append(f'M {start[0]:.2f},{start[1]:.2f}')

            # Curve segments
            for segment in curve.segments:
                if segment.is_corner:
                    # Corner (straight line)
                    c = segment.c
                    end = segment.end_point
                    path_data.append(f'L {c[0]:.2f},{c[1]:.2f}')
                    path_data.append(f'L {end[0]:.2f},{end[1]:.2f}')
                else:
                    # Bezier curve
                    c1 = segment.c1
                    c2 = segment.c2
                    end = segment.end_point
                    path_data.append(f'C {c1[0]:.2f},{c1[1]:.2f} {c2[0]:.2f},{c2[1]:.2f} {end[0]:.2f},{end[1]:.2f}')

            # Close path
            path_data.append('Z')

            # Add path to SVG
            dwg.add(dwg.path(
                d=' '.join(path_data),
                fill=fill,
                stroke=stroke,
                stroke_width=stroke_width
            ))

        return dwg.tostring()

    def svg_to_dxf(self, svg_string: str, output_path: str) -> str:
        """
        Convert SVG to DXF format (for CAD software)

        DXF is commonly used in laser cutting/engraving software
        """
        # Create DXF document
        doc = ezdxf.new('R2010')
        msp = doc.modelspace()

        # Parse SVG paths and convert to DXF entities
        # (This is a simplified version - full implementation would parse SVG XML)

        # For now, create a basic DXF with polylines
        # TODO: Full SVG → DXF conversion implementation

        # Save DXF
        doc.saveas(output_path)
        return output_path

    def convert_image_to_vector(
        self,
        image_path: str,
        output_format: str = 'svg',
        material_type: str = 'wood',
        detail_level: str = 'medium'
    ) -> Dict:
        """
        Complete conversion pipeline: Image → Preprocessed → Vector → Format

        Args:
            image_path: Path to input image
            output_format: 'svg', 'dxf', or 'both'
            material_type: Material being engraved (affects preprocessing)
            detail_level: 'low', 'medium', 'high' (affects turdsize)

        Returns:
            {
                'svg_content': str,
                'svg_path': str,
                'dxf_path': str (if requested),
                'metadata': {...}
            }
        """
        logger.info(f"Converting {image_path} to vector for {material_type}")

        # Detail level mapping
        detail_map = {
            'low': {'turdsize': 10, 'alphamax': 1.2},
            'medium': {'turdsize': 4, 'alphamax': 1.0},
            'high': {'turdsize': 2, 'alphamax': 0.8},
            'very_high': {'turdsize': 1, 'alphamax': 0.6}
        }
        params = detail_map.get(detail_level, detail_map['medium'])

        # Step 1: Preprocess
        bitmap = self.preprocess_image(
            image_path,
            target_size=(2000, 2000),  # High resolution for detail
            contrast_factor=1.5 if material_type in ['wood', 'leather'] else 1.3
        )

        # Step 2: Convert to vector paths
        path = self.bitmap_to_vector(
            bitmap,
            turdsize=params['turdsize'],
            alphamax=params['alphamax']
        )

        # Step 3: Generate SVG
        svg_content = self.path_to_svg(
            path,
            width=bitmap.shape[1],
            height=bitmap.shape[0],
            stroke_width=0.5
        )

        # Step 4: Save files
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        import uuid

        file_id = str(uuid.uuid4())

        # Save SVG
        svg_filename = f'laser/svg/{file_id}.svg'
        svg_path = default_storage.save(svg_filename, ContentFile(svg_content.encode('utf-8')))

        result = {
            'svg_content': svg_content,
            'svg_path': svg_path,
            'svg_url': default_storage.url(svg_path),
            'metadata': {
                'original_size': bitmap.shape,
                'path_count': len(list(path)),
                'detail_level': detail_level,
                'material_type': material_type
            }
        }

        # Step 5: Generate DXF if requested
        if output_format in ['dxf', 'both']:
            dxf_filename = f'laser/dxf/{file_id}.dxf'
            dxf_path = self.svg_to_dxf(svg_content, dxf_filename)
            result['dxf_path'] = dxf_path
            result['dxf_url'] = default_storage.url(dxf_path)

        logger.info(f"Vector conversion complete: {result['svg_url']}")
        return result
```

### Laser Specification Manager

```python
# content/physical_products/laser_specs.py

from typing import Dict
import json

class LaserSpecificationManager:
    """Material-specific laser engraving settings"""

    # Default laser settings for different materials
    MATERIAL_PRESETS = {
        'wood': {
            'name': 'Wood (General)',
            'power_percent': 40,
            'speed_mm_per_min': 400,
            'passes': 1,
            'depth_mm': 0.5,
            'frequency_hz': 1000,
            'mode': 'vector',
            'notes': 'Works for most woods. Darker woods may need less power.'
        },
        'plywood': {
            'name': 'Plywood',
            'power_percent': 50,
            'speed_mm_per_min': 350,
            'passes': 1,
            'depth_mm': 0.8,
            'frequency_hz': 1000,
            'mode': 'vector',
            'notes': 'May need 2 passes for darker engraving.'
        },
        'mdf': {
            'name': 'MDF',
            'power_percent': 45,
            'speed_mm_per_min': 400,
            'passes': 1,
            'depth_mm': 0.6,
            'frequency_hz': 1000,
            'mode': 'vector',
            'notes': 'Produces darker engraving than wood.'
        },
        'bamboo': {
            'name': 'Bamboo',
            'power_percent': 35,
            'speed_mm_per_min': 500,
            'passes': 1,
            'depth_mm': 0.4,
            'frequency_hz': 1200,
            'mode': 'vector',
            'notes': 'Burns easily - start with lower power.'
        },
        'leather': {
            'name': 'Leather',
            'power_percent': 30,
            'speed_mm_per_min': 600,
            'passes': 1,
            'depth_mm': 0.3,
            'frequency_hz': 1500,
            'mode': 'vector',
            'notes': 'Produces brown/dark engraving. Use ventilation.'
        },
        'acrylic': {
            'name': 'Acrylic (Clear)',
            'power_percent': 70,
            'speed_mm_per_min': 200,
            'passes': 1,
            'depth_mm': 0.2,
            'frequency_hz': 5000,
            'mode': 'raster',
            'notes': 'Creates frosted white effect.'
        },
        'metal': {
            'name': 'Anodized Metal',
            'power_percent': 90,
            'speed_mm_per_min': 100,
            'passes': 1,
            'depth_mm': 0.01,
            'frequency_hz': 10000,
            'mode': 'raster',
            'notes': 'Only works on anodized or coated metals. Fiber laser recommended.'
        },
        'glass': {
            'name': 'Glass',
            'power_percent': 80,
            'speed_mm_per_min': 150,
            'passes': 1,
            'depth_mm': 0.1,
            'frequency_hz': 8000,
            'mode': 'raster',
            'notes': 'Creates frosted effect. Use painter\'s tape to reduce chipping.'
        },
        'cardboard': {
            'name': 'Cardboard',
            'power_percent': 20,
            'speed_mm_per_min': 800,
            'passes': 1,
            'depth_mm': 0.2,
            'frequency_hz': 500,
            'mode': 'vector',
            'notes': 'Burns easily - very low power recommended.'
        },
        'fabric': {
            'name': 'Fabric (Cotton)',
            'power_percent': 25,
            'speed_mm_per_min': 700,
            'passes': 1,
            'depth_mm': 0.1,
            'frequency_hz': 500,
            'mode': 'raster',
            'notes': 'Test on scrap first. May need masking tape.'
        }
    }

    # Machine-specific adjustments
    MACHINE_ADJUSTMENTS = {
        'epilog': {
            'speed_multiplier': 1.0,
            'power_multiplier': 1.0,
            'file_format': 'svg',
            'notes': 'Import SVG into Epilog Dashboard'
        },
        'glowforge': {
            'speed_multiplier': 0.8,
            'power_multiplier': 1.1,
            'file_format': 'svg',
            'notes': 'Upload SVG to Glowforge app'
        },
        'trotec': {
            'speed_multiplier': 1.2,
            'power_multiplier': 0.9,
            'file_format': 'dxf',
            'notes': 'Import DXF into JobControl'
        },
        'universal': {
            'speed_multiplier': 1.0,
            'power_multiplier': 1.0,
            'file_format': 'svg',
            'notes': 'Import SVG into UCP'
        },
        'generic': {
            'speed_multiplier': 1.0,
            'power_multiplier': 1.0,
            'file_format': 'svg',
            'notes': 'Universal SVG format'
        }
    }

    def get_settings_for_material(
        self,
        material_type: str,
        machine_type: str = 'generic',
        thickness_mm: float = 3.0,
        custom_adjustments: Dict = None
    ) -> Dict:
        """
        Get recommended laser settings for material/machine combination

        Args:
            material_type: Type of material ('wood', 'metal', etc.)
            machine_type: Type of laser machine
            thickness_mm: Material thickness (affects power/passes)
            custom_adjustments: User overrides

        Returns:
            Complete laser settings dictionary
        """
        # Get base material settings
        base_settings = self.MATERIAL_PRESETS.get(material_type, self.MATERIAL_PRESETS['wood'])

        # Get machine adjustments
        machine_adj = self.MACHINE_ADJUSTMENTS.get(machine_type, self.MACHINE_ADJUSTMENTS['generic'])

        # Calculate adjusted settings
        settings = {
            'material': base_settings['name'],
            'machine': machine_type,
            'power_percent': int(base_settings['power_percent'] * machine_adj['power_multiplier']),
            'speed_mm_per_min': int(base_settings['speed_mm_per_min'] * machine_adj['speed_multiplier']),
            'passes': base_settings['passes'],
            'depth_mm': base_settings['depth_mm'],
            'frequency_hz': base_settings.get('frequency_hz'),
            'mode': base_settings['mode'],
            'recommended_format': machine_adj['file_format'],
            'notes': base_settings['notes'],
            'machine_notes': machine_adj['notes']
        }

        # Adjust for thickness (thicker = more power or passes)
        if thickness_mm > 5.0:
            settings['passes'] = 2
            settings['notes'] += f' Material is {thickness_mm}mm thick - using 2 passes.'

        # Apply custom adjustments
        if custom_adjustments:
            settings.update(custom_adjustments)

        # Safety limits
        settings['power_percent'] = max(10, min(100, settings['power_percent']))
        settings['speed_mm_per_min'] = max(50, min(3000, settings['speed_mm_per_min']))
        settings['passes'] = max(1, min(5, settings['passes']))

        return settings

    def export_settings_as_comment(self, settings: Dict) -> str:
        """
        Generate SVG comment with laser settings

        Can be parsed by some laser software
        """
        comment = f"""
<!--
Donkey Betz Laser Settings
==========================
Material: {settings['material']}
Machine: {settings['machine']}
Power: {settings['power_percent']}%
Speed: {settings['speed_mm_per_min']} mm/min
Passes: {settings['passes']}
Estimated Depth: {settings['depth_mm']} mm
Mode: {settings['mode']}

{settings['notes']}
{settings.get('machine_notes', '')}
-->
"""
        return comment
```

### G-code Generator

```python
# content/physical_products/gcode_generator.py

from typing import Dict, List
import xml.etree.ElementTree as ET

class GCodeGenerator:
    """Generate G-code from SVG paths for direct laser control"""

    def __init__(self):
        self.feedrate = 1000  # mm/min
        self.laser_power = 50  # 0-100%

    def svg_to_gcode(
        self,
        svg_path: str,
        settings: Dict
    ) -> str:
        """
        Convert SVG vector paths to G-code

        G-code commands:
        - G0: Rapid move (laser off)
        - G1: Linear move (laser on)
        - M3: Laser on
        - M5: Laser off
        - S: Laser power (0-255 or 0-100 depending on controller)

        Returns: G-code string
        """
        # Parse SVG
        tree = ET.parse(svg_path)
        root = tree.getroot()

        # Initialize G-code
        gcode_lines = []

        # Header
        gcode_lines.append("; Generated by Donkey Betz")
        gcode_lines.append(f"; Material: {settings.get('material', 'Unknown')}")
        gcode_lines.append(f"; Power: {settings.get('power_percent', 50)}%")
        gcode_lines.append(f"; Speed: {settings.get('speed_mm_per_min', 1000)} mm/min")
        gcode_lines.append("")

        # Setup
        gcode_lines.append("G21 ; Set units to millimeters")
        gcode_lines.append("G90 ; Absolute positioning")
        gcode_lines.append(f"F{settings.get('speed_mm_per_min', 1000)} ; Set feedrate")
        gcode_lines.append("M5 ; Laser off")
        gcode_lines.append("G0 X0 Y0 ; Move to origin")
        gcode_lines.append("")

        # Extract paths from SVG
        namespace = {'svg': 'http://www.w3.org/2000/svg'}
        paths = root.findall('.//svg:path', namespace)

        for path in paths:
            d = path.get('d')
            if not d:
                continue

            # Parse path data (simplified - full implementation would handle all SVG path commands)
            commands = self._parse_svg_path(d)

            for cmd in commands:
                if cmd['type'] == 'M':  # Move
                    gcode_lines.append(f"M5 ; Laser off")
                    gcode_lines.append(f"G0 X{cmd['x']:.3f} Y{cmd['y']:.3f} ; Move to start")
                    gcode_lines.append(f"M3 S{settings.get('power_percent', 50)} ; Laser on")

                elif cmd['type'] == 'L':  # Line
                    gcode_lines.append(f"G1 X{cmd['x']:.3f} Y{cmd['y']:.3f} ; Engrave line")

                elif cmd['type'] == 'Z':  # Close path
                    gcode_lines.append(f"G1 X{cmd['x']:.3f} Y{cmd['y']:.3f} ; Close path")

        # Footer
        gcode_lines.append("")
        gcode_lines.append("M5 ; Laser off")
        gcode_lines.append("G0 X0 Y0 ; Return to origin")
        gcode_lines.append("M2 ; Program end")

        return '\n'.join(gcode_lines)

    def _parse_svg_path(self, path_data: str) -> List[Dict]:
        """
        Parse SVG path data into commands

        Simplified parser - full implementation would handle:
        - M, L, H, V, C, S, Q, T, A, Z commands
        - Relative vs absolute coordinates
        - Bezier curves
        """
        # TODO: Full SVG path parser
        # For now, return basic structure
        return []
```

---

## 🎨 Frontend Implementation

### New Workflow Tab

```html
<!-- ai_core/templates/ai_image_studio.html -->

<!-- Add new tab to navigation -->
<li class="nav-item">
    <a class="nav-link" data-bs-toggle="tab" href="#laser-engraving">
        🔥 Laser Engraving
    </a>
</li>

<!-- Tab content -->
<div class="tab-pane fade" id="laser-engraving">
    <h3 class="mb-4">🔥 Laser Engraving File Creator</h3>
    <p class="text-muted">Convert your AI images into laser-engravable vector files</p>

    <!-- Step 1: Select Image -->
    <div class="card mb-4">
        <div class="card-header">
            <h5>1. Select Source Image</h5>
        </div>
        <div class="card-body">
            <button class="btn btn-primary" onclick="openLaserGalleryModal()">
                Choose from Gallery
            </button>
            <span class="mx-2">or</span>
            <input type="file" id="laserUpload" accept="image/*" class="form-control d-inline-block w-auto">

            <div id="laserSourcePreview" class="mt-3" style="display:none;">
                <img id="laserSourceImage" src="" class="img-thumbnail" style="max-width:300px;">
            </div>
        </div>
    </div>

    <!-- Step 2: Material Selection -->
    <div class="card mb-4">
        <div class="card-header">
            <h5>2. Select Material Type</h5>
        </div>
        <div class="card-body">
            <div class="row g-3">
                <div class="col-md-4">
                    <div class="material-card" data-material="wood" onclick="selectMaterial('wood')">
                        <h6>🪵 Wood</h6>
                        <p class="small">General purpose wood<br>Power: 40% | Speed: 400</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="material-card" data-material="leather" onclick="selectMaterial('leather')">
                        <h6>👜 Leather</h6>
                        <p class="small">Leather engraving<br>Power: 30% | Speed: 600</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="material-card" data-material="acrylic" onclick="selectMaterial('acrylic')">
                        <h6>💎 Acrylic</h6>
                        <p class="small">Clear acrylic<br>Power: 70% | Speed: 200</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="material-card" data-material="metal" onclick="selectMaterial('metal')">
                        <h6>⚙️ Metal</h6>
                        <p class="small">Anodized metal<br>Power: 90% | Speed: 100</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="material-card" data-material="bamboo" onclick="selectMaterial('bamboo')">
                        <h6>🎋 Bamboo</h6>
                        <p class="small">Bamboo engraving<br>Power: 35% | Speed: 500</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="material-card" data-material="glass" onclick="selectMaterial('glass')">
                        <h6>🥃 Glass</h6>
                        <p class="small">Glass frosting<br>Power: 80% | Speed: 150</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Step 3: Detail Settings -->
    <div class="card mb-4">
        <div class="card-header">
            <h5>3. Detail Level</h5>
        </div>
        <div class="card-body">
            <div class="btn-group" role="group">
                <input type="radio" class="btn-check" name="detailLevel" id="detailLow" value="low">
                <label class="btn btn-outline-primary" for="detailLow">Low (Fast)</label>

                <input type="radio" class="btn-check" name="detailLevel" id="detailMedium" value="medium" checked>
                <label class="btn btn-outline-primary" for="detailMedium">Medium</label>

                <input type="radio" class="btn-check" name="detailLevel" id="detailHigh" value="high">
                <label class="btn btn-outline-primary" for="detailHigh">High (Detailed)</label>

                <input type="radio" class="btn-check" name="detailLevel" id="detailVeryHigh" value="very_high">
                <label class="btn btn-outline-primary" for="detailVeryHigh">Very High</label>
            </div>
            <p class="small text-muted mt-2">Higher detail = larger file size and longer engraving time</p>
        </div>
    </div>

    <!-- Step 4: Machine Type -->
    <div class="card mb-4">
        <div class="card-header">
            <h5>4. Laser Machine (Optional)</h5>
        </div>
        <div class="card-body">
            <select id="machineType" class="form-select">
                <option value="generic">Generic (Universal SVG)</option>
                <option value="epilog">Epilog Laser</option>
                <option value="glowforge">Glowforge</option>
                <option value="trotec">Trotec</option>
                <option value="universal">Universal Laser Systems</option>
                <option value="lightburn">LightBurn Compatible</option>
            </select>
        </div>
    </div>

    <!-- Step 5: Generate -->
    <div class="card mb-4">
        <div class="card-body text-center">
            <button class="btn btn-primary btn-lg" onclick="generateLaserFiles()" id="generateLaserBtn">
                🔥 Generate Laser Files
            </button>

            <div id="laserProgress" class="mt-3" style="display:none;">
                <div class="spinner-border text-primary" role="status"></div>
                <p class="mt-2">Converting to vector format...</p>
            </div>
        </div>
    </div>

    <!-- Results -->
    <div id="laserResults" class="card" style="display:none;">
        <div class="card-header bg-success text-white">
            <h5>✅ Laser Files Ready!</h5>
        </div>
        <div class="card-body">
            <div class="row">
                <div class="col-md-6">
                    <h6>Preview:</h6>
                    <img id="laserVectorPreview" src="" class="img-thumbnail mb-3">

                    <h6>Settings Used:</h6>
                    <ul id="laserSettings" class="list-unstyled small">
                        <!-- Populated dynamically -->
                    </ul>
                </div>
                <div class="col-md-6">
                    <h6>Download Files:</h6>
                    <div class="d-grid gap-2">
                        <a id="downloadSvg" href="#" class="btn btn-outline-primary" download>
                            📄 Download SVG (Universal)
                        </a>
                        <a id="downloadDxf" href="#" class="btn btn-outline-primary" download>
                            📐 Download DXF (CAD Format)
                        </a>
                        <a id="downloadGcode" href="#" class="btn btn-outline-primary" download>
                            🤖 Download G-code (Machine Code)
                        </a>
                    </div>

                    <div class="alert alert-info mt-3">
                        <h6>💡 Next Steps:</h6>
                        <ol class="small mb-0">
                            <li>Download your preferred file format</li>
                            <li>Import into your laser software</li>
                            <li>Adjust settings if needed</li>
                            <li>Run a test on scrap material</li>
                            <li>Engrave your final piece!</li>
                        </ol>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
```

### JavaScript Implementation

```javascript
// Laser engraving state
let laserState = {
    sourceImage: null,
    material: 'wood',
    detailLevel: 'medium',
    machineType: 'generic',
    resultFiles: null
};

async function generateLaserFiles() {
    if (!laserState.sourceImage) {
        alert('Please select a source image first');
        return;
    }

    // Show progress
    document.getElementById('generateLaserBtn').disabled = true;
    document.getElementById('laserProgress').style.display = 'block';
    document.getElementById('laserResults').style.display = 'none';

    try {
        const response = await authenticatedFetch('/api/laser/convert/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                source_image_id: laserState.sourceImage.id,
                material_type: laserState.material,
                detail_level: laserState.detailLevel,
                machine_type: laserState.machineType
            })
        });

        const data = await response.json();

        if (data.success) {
            // Store result
            laserState.resultFiles = data;

            // Show preview
            document.getElementById('laserVectorPreview').src = data.preview_url;

            // Populate settings
            const settingsHtml = `
                <li><strong>Material:</strong> ${data.settings.material}</li>
                <li><strong>Power:</strong> ${data.settings.power_percent}%</li>
                <li><strong>Speed:</strong> ${data.settings.speed_mm_per_min} mm/min</li>
                <li><strong>Passes:</strong> ${data.settings.passes}</li>
                <li><strong>Est. Depth:</strong> ${data.settings.depth_mm} mm</li>
                <li><strong>Mode:</strong> ${data.settings.mode}</li>
            `;
            document.getElementById('laserSettings').innerHTML = settingsHtml;

            // Set download links
            document.getElementById('downloadSvg').href = data.svg_url;
            document.getElementById('downloadSvg').download = `laser_${Date.now()}.svg`;

            if (data.dxf_url) {
                document.getElementById('downloadDxf').href = data.dxf_url;
                document.getElementById('downloadDxf').download = `laser_${Date.now()}.dxf`;
                document.getElementById('downloadDxf').style.display = 'block';
            }

            if (data.gcode_url) {
                document.getElementById('downloadGcode').href = data.gcode_url;
                document.getElementById('downloadGcode').download = `laser_${Date.now()}.gcode`;
                document.getElementById('downloadGcode').style.display = 'block';
            }

            // Show results
            document.getElementById('laserResults').style.display = 'block';

            // Scroll to results
            document.getElementById('laserResults').scrollIntoView({ behavior: 'smooth' });
        } else {
            alert('Error generating laser files: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Laser conversion error:', error);
        alert('Error: ' + error.message);
    } finally {
        document.getElementById('generateLaserBtn').disabled = false;
        document.getElementById('laserProgress').style.display = 'none';
    }
}

function selectMaterial(material) {
    laserState.material = material;

    // Visual feedback
    document.querySelectorAll('.material-card').forEach(card => {
        card.classList.remove('selected');
    });
    document.querySelector(`[data-material="${material}"]`).classList.add('selected');
}
```

---

## 💰 Pricing Strategy

### Cost Structure

**Per File Generation:**
- Image generation (if needed): $0.002-0.008
- Vector conversion: ~$0.01 (computational cost)
- Storage (SVG/DXF): ~$0.001
- **Total Cost:** ~$0.02-0.03

### Revenue Models

**1. Pay-Per-Download**
```
Pricing tiers:
- SVG only: $5
- SVG + DXF: $10
- Full package (SVG + DXF + G-code + Settings PDF): $15

With $0.03 cost:
- $5 sale = $4.97 profit (99.4% margin!)
- $10 sale = $9.97 profit
- $15 sale = $14.97 profit
```

**2. Subscription Add-On**
```
Add laser feature to existing subscription:
- +$10/month: 10 laser files
- +$25/month: Unlimited laser files

100 subscribers × $10 = $1,000/month recurring
```

**3. Marketplace Model**
```
Allow users to sell their laser files:
- User sets price: $8-20
- Platform takes 30% commission
- User earns passive income
- Platform scales revenue with volume
```

---

## 🧪 Testing Plan

### Phase 1: Conversion Quality
- [ ] Test with simple designs (logos, icons)
- [ ] Test with complex designs (photos, detailed art)
- [ ] Test with text (ensure readability)
- [ ] Verify vector path counts
- [ ] Check file sizes (should be < 5MB)

### Phase 2: Material Settings
- [ ] Create test files for each material
- [ ] Partner with maker space for actual engraving tests
- [ ] Document results (power/speed/quality)
- [ ] Refine material presets
- [ ] Get user feedback

### Phase 3: Machine Compatibility
- [ ] Test SVG import in Epilog Dashboard
- [ ] Test SVG in Glowforge app
- [ ] Test DXF in LightBurn
- [ ] Test G-code on GRBL controller
- [ ] Document any machine-specific issues

### Phase 4: User Experience
- [ ] Measure conversion time (should be < 60s)
- [ ] Test with non-technical users
- [ ] Verify download links work
- [ ] Check mobile responsiveness
- [ ] Gather feature requests

---

## 📊 Success Metrics

**Technical Metrics:**
- Conversion success rate: > 95%
- Average conversion time: < 60 seconds
- File size: SVG < 2MB, DXF < 5MB
- Vector path accuracy: > 99%

**Business Metrics:**
- 50+ laser files generated (first month)
- 25+ downloads
- $200+ revenue
- 90%+ customer satisfaction
- 3+ repeat customers

---

## 🚀 Launch Strategy

**Week 1: Beta Testing**
- Enable for 10-20 beta users
- Gather feedback on quality
- Test actual engraving results
- Refine settings

**Week 2: Soft Launch**
- Open to all users
- Promote on maker/DIY forums
- Create tutorial videos
- Document use cases

**Week 3: Full Launch**
- Press release
- Reddit/maker communities
- YouTube demonstrations
- Partner with laser companies

---

**Status:** 📋 Ready for Implementation
**Next Step:** Review with team, allocate development resources
