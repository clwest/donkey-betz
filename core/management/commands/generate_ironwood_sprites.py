"""
Generate Ironwood Protocol sprites — 15 individual top-down game assets.

Calls _execute_generate_image directly (bypasses GPT prompt rewriting)
to produce clean single sprites instead of concept art sheets.

Usage:
    python manage.py generate_ironwood_sprites
    python manage.py generate_ironwood_sprites --dry-run
    python manage.py generate_ironwood_sprites --only skimmer,hq
    python manage.py generate_ironwood_sprites --model sd3
"""

import json
import time
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

# ── Sprite definitions ────────────────────────────────────────────────────

SPRITES = [
    # Units (3 chassis types)
    {
        "id": "unit_skimmer",
        "type": "unit",
        "name": "Skimmer",
        "prompt": (
            "single sprite, top-down overhead view, centered, one object only, "
            "black background, 32x32 game asset icon, digital sci-fi style, "
            "small fast scout drone, triangular wedge shape, sleek hull, "
            "thruster glow on rear, neutral gray metallic palette, "
            "clean silhouette, no text"
        ),
    },
    {
        "id": "unit_walker",
        "type": "unit",
        "name": "Walker",
        "prompt": (
            "single sprite, top-down overhead view, centered, one object only, "
            "black background, 32x32 game asset icon, digital sci-fi style, "
            "medium bipedal mech walker, circular body from above, two leg joints visible, "
            "armored torso plate, neutral gray metallic palette, "
            "clean silhouette, no text"
        ),
    },
    {
        "id": "unit_bulwark",
        "type": "unit",
        "name": "Bulwark",
        "prompt": (
            "single sprite, top-down overhead view, centered, one object only, "
            "black background, 32x32 game asset icon, digital sci-fi style, "
            "heavy tank mech, rounded square shape from above, thick armor plates, "
            "reinforced hull, shoulder-mounted weapon pods, neutral gray metallic palette, "
            "clean silhouette, no text"
        ),
    },
    # Buildings (5 types)
    {
        "id": "building_hq",
        "type": "building",
        "name": "HQ",
        "prompt": (
            "single sprite, top-down overhead view, centered, one object only, "
            "black background, 32x32 game asset icon, digital sci-fi style, "
            "large military command center building, pentagonal fortress shape from above, "
            "antenna beacon on top, armored roof, neutral gray metallic palette, "
            "clean silhouette, no text"
        ),
    },
    {
        "id": "building_barracks",
        "type": "building",
        "name": "Barracks",
        "prompt": (
            "single sprite, top-down overhead view, centered, one object only, "
            "black background, 32x32 game asset icon, digital sci-fi style, "
            "military barracks factory building, rectangular with bay doors, "
            "flat roof with vents, neutral gray metallic palette, "
            "clean silhouette, no text"
        ),
    },
    {
        "id": "building_generator",
        "type": "building",
        "name": "Generator",
        "prompt": (
            "single sprite, top-down overhead view, centered, one object only, "
            "black background, 32x32 game asset icon, digital sci-fi style, "
            "energy generator building, circular shape from above, "
            "glowing reactor core in center, cooling vents around edge, "
            "neutral gray metallic with subtle amber energy glow, "
            "clean silhouette, no text"
        ),
    },
    {
        "id": "building_turret",
        "type": "building",
        "name": "Turret",
        "prompt": (
            "single sprite, top-down overhead view, centered, one object only, "
            "black background, 32x32 game asset icon, digital sci-fi style, "
            "automated defense turret, circular base with gun barrel pointing up-right, "
            "sensor dish on top, neutral gray metallic palette, "
            "clean silhouette, no text"
        ),
    },
    {
        "id": "building_wall",
        "type": "building",
        "name": "Wall",
        "prompt": (
            "single sprite, top-down overhead view, centered, one object only, "
            "black background, 32x32 game asset icon, digital sci-fi style, "
            "fortified wall segment, square block shape from above, "
            "reinforced metal plates, bolted edges, neutral gray metallic palette, "
            "clean silhouette, no text"
        ),
    },
    # Terrain (7 tile types)
    {
        "id": "terrain_grass",
        "type": "terrain",
        "name": "Grass",
        "prompt": (
            "single sprite, top-down overhead view, centered, one tile only, "
            "32x32 game asset icon, digital sci-fi style, "
            "alien grass terrain tile, dark green with bioluminescent flecks, "
            "subtle organic texture, seamless tileable, no text"
        ),
    },
    {
        "id": "terrain_forest",
        "type": "terrain",
        "name": "Forest",
        "prompt": (
            "single sprite, top-down overhead view, centered, one tile only, "
            "32x32 game asset icon, digital sci-fi style, "
            "alien forest terrain tile, dense canopy from above, "
            "dark green treetops with glowing spores, seamless tileable, no text"
        ),
    },
    {
        "id": "terrain_rock",
        "type": "terrain",
        "name": "Rock",
        "prompt": (
            "single sprite, top-down overhead view, centered, one tile only, "
            "32x32 game asset icon, digital sci-fi style, "
            "rocky terrain tile, gray jagged rocks from above, "
            "mineral veins visible, rough texture, seamless tileable, no text"
        ),
    },
    {
        "id": "terrain_water",
        "type": "terrain",
        "name": "Water",
        "prompt": (
            "single sprite, top-down overhead view, centered, one tile only, "
            "32x32 game asset icon, digital sci-fi style, "
            "alien water terrain tile, dark teal liquid surface, "
            "subtle ripple pattern, faint bioluminescent shimmer, seamless tileable, no text"
        ),
    },
    {
        "id": "terrain_ruin",
        "type": "terrain",
        "name": "Ruin",
        "prompt": (
            "single sprite, top-down overhead view, centered, one tile only, "
            "32x32 game asset icon, digital sci-fi style, "
            "ancient ruin terrain tile, crumbled stone walls from above, "
            "overgrown with moss, scattered debris, seamless tileable, no text"
        ),
    },
    {
        "id": "terrain_node_energy",
        "type": "terrain",
        "name": "Energy Node",
        "prompt": (
            "single sprite, top-down overhead view, centered, one object only, "
            "black background, 32x32 game asset icon, digital sci-fi style, "
            "energy resource crystal node, glowing blue crystalline formation, "
            "pulsing energy aura, bright cyan core, clean silhouette, no text"
        ),
    },
    {
        "id": "terrain_node_biomass",
        "type": "terrain",
        "name": "Biomass Node",
        "prompt": (
            "single sprite, top-down overhead view, centered, one object only, "
            "black background, 32x32 game asset icon, digital sci-fi style, "
            "biomass resource node, glowing green organic mass, "
            "pulsing bio-luminescent tendrils, bright emerald core, clean silhouette, no text"
        ),
    },
]

NEGATIVE_PROMPT = (
    "blurry, low quality, distorted, text, watermark, multi-panel, "
    "concept art sheet, multiple views, side view, perspective view, "
    "3D render, photograph, realistic, human, face, "
    "comic strip, collage, split scene, series"
)


class Command(BaseCommand):
    help = "Generate 15 Ironwood Protocol sprites via Stability AI"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Print prompts without generating")
        parser.add_argument("--only", type=str, default="", help="Comma-separated sprite IDs to generate")
        parser.add_argument("--model", type=str, default="sd3", help="Stability model: core/sdxl/sd3/ultra")
        parser.add_argument("--user", type=str, default="donkeyking", help="Username for image history")
        parser.add_argument("--output", type=str, default="ironwood_sprite_manifest.json", help="Manifest output path")

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        only = [s.strip() for s in options["only"].split(",") if s.strip()]
        model = options["model"]
        username = options["user"]
        output_path = options["output"]

        # Filter sprites if --only specified
        sprites = SPRITES
        if only:
            sprites = [s for s in SPRITES if s["id"] in only]
            if not sprites:
                self.stderr.write(f"No sprites match --only={options['only']}")
                return

        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(f"  Ironwood Protocol Sprite Generator")
        self.stdout.write(f"  Sprites: {len(sprites)} | Model: {model} | Dry run: {dry_run}")
        self.stdout.write(f"{'='*60}\n")

        if dry_run:
            for s in sprites:
                self.stdout.write(f"\n[{s['id']}] {s['name']} ({s['type']})")
                self.stdout.write(f"  Prompt: {s['prompt'][:120]}...")
            self.stdout.write(f"\nDry run complete. {len(sprites)} sprites would be generated.")
            return

        # Get user
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stderr.write(f"User '{username}' not found")
            return

        from core.views_image_helpers import _execute_generate_image

        manifest = {
            "version": "1.0",
            "sprite_size": 32,
            "model": model,
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "sprites": [],
        }

        success_count = 0
        fail_count = 0

        for i, sprite in enumerate(sprites, 1):
            self.stdout.write(f"\n[{i}/{len(sprites)}] Generating {sprite['id']}...")

            parameters = {
                "prompt": sprite["prompt"],
                "model": model,
                "style": "digital_art",
                "size": "1024x1024",  # Generate at 1024 (Stability minimum), crop/resize later
                "width": 1024,
                "height": 1024,
                "negative_prompt": NEGATIVE_PROMPT,
                "count": 1,
            }

            try:
                result = _execute_generate_image(user=user, parameters=parameters)

                if result.get("success") and result.get("images"):
                    img = result["images"][0]
                    url = img.get("image_url", img.get("url", ""))
                    image_id = img.get("image_id", img.get("id", ""))

                    manifest["sprites"].append({
                        "id": sprite["id"],
                        "type": sprite["type"],
                        "name": sprite["name"],
                        "url": url,
                        "image_id": str(image_id),
                        "prompt": sprite["prompt"],
                    })

                    success_count += 1
                    self.stdout.write(self.style.SUCCESS(
                        f"  OK: {url[:80]}..."
                    ))
                else:
                    error = result.get("error", "Unknown error")
                    fail_count += 1
                    self.stdout.write(self.style.ERROR(f"  FAIL: {error}"))

            except Exception as e:
                fail_count += 1
                self.stdout.write(self.style.ERROR(f"  ERROR: {e}"))

            # Brief pause between API calls to avoid rate limiting
            if i < len(sprites):
                time.sleep(2)

        # Write manifest
        with open(output_path, "w") as f:
            json.dump(manifest, f, indent=2)

        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(f"  Done: {success_count} succeeded, {fail_count} failed")
        self.stdout.write(f"  Manifest: {output_path}")
        self.stdout.write(f"{'='*60}\n")
