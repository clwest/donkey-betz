# Session 201: Style System & Prompting Architecture Fix

**Date:** November 26, 2025
**Previous Session:** 200 (Workflow Orchestrations Complete)
**Reality Score:** 100%

---

## Session Summary

This session focused on diagnosing and fixing critical issues with the style system and prompt architecture. The user discovered that:
1. Style preferences like "DreamWorks style" were generating Kung Fu Panda characters instead of applying the style to the user's topic
2. The workflow orchestration agent was bypassing the built-in 69-style system
3. Several popular animation styles were missing from the style library

---

## Issues Fixed

### Issue 1: Kung Fu Panda Characters Instead of Brewery Images

**Root Cause:** The workflow orchestration agent had a small custom style expansion dictionary that included specific character/movie names:
```python
# BAD - This caused AI to generate the characters, not apply the style
'dreamworks': '... Shrek/Kung Fu Panda aesthetic'
```

**Fix:** Removed character references, now uses visual characteristics only.

### Issue 2: Workflow Agent Bypassing Built-in Styles

**Root Cause:** The `workflow_orchestration_agent.py` was building prompts with its own 10-style dictionary instead of using the 69 professional styles in `ImageGenerationService._apply_style_to_prompt()`.

**Fix:** The workflow agent now passes style keys to `ImageGenerationService` which applies the proper style expansion.

### Issue 3: DreamWorks and South Park Missing from Styles

**Root Cause:** These popular animation styles were never added to the built-in style library.

**Fix:** Added 14 new animation styles to `content/image_generation.py`.

---

## New Animation Styles Added (Now 80+ Total!)

| Style Key | Description |
|-----------|-------------|
| `dreamworks` | DreamWorks 3D animation style, stylized expressive characters, bold rounded shapes |
| `south_park` / `southpark` | South Park style, simple 2D cutout animation, construction paper aesthetic |
| `simpsons` | The Simpsons style, yellow skin tones, Matt Groening style |
| `family_guy` | Family Guy style, Seth MacFarlane style adult animation |
| `ghibli` / `studio_ghibli` | Studio Ghibli anime style, Hayao Miyazaki aesthetic, watercolor backgrounds |
| `looney_tunes` | Looney Tunes classic cartoon, Warner Bros aesthetic |
| `rick_and_morty` | Rick and Morty style, Adult Swim aesthetic, wobbly lines |
| `archer` | Archer animation style, mid-century modern aesthetic |
| `adventure_time` | Adventure Time style, Pendleton Ward, Cartoon Network |
| `gravity_falls` | Gravity Falls style, Alex Hirsch, mystery cartoon |
| `bojack` | BoJack Horseman style, anthropomorphic, Netflix animated |

---

## Architecture Understanding

### The Built-in Style System

**Location:** `content/image_generation.py` - `_apply_style_to_prompt()` method (lines 173-280)

**How it works:**
1. User specifies a style (e.g., "cyberpunk", "dreamworks", "watercolor")
2. The style key is looked up in the `style_mappings` dictionary
3. A professional prompt expansion is applied to the user's prompt
4. If style not found, defaults to `"{prompt}, {style} style"`

**Style Categories:**
- Photography (10 styles): photorealistic, portrait, landscape, macro, street, fashion, etc.
- Digital Art (8 styles): digital_art, concept_art, vector, isometric, etc.
- Traditional Art (8 styles): oil_painting, watercolor, charcoal, pencil, etc.
- Animation & Comic (17 styles): anime, pixar, disney, dreamworks, south_park, etc.
- Artistic Movements (10 styles): impressionist, surreal, cubist, pop_art, etc.
- Genre Styles (8 styles): fantasy, scifi, cyberpunk, steampunk, gothic, etc.
- 3D & Effects (6 styles): 3d_render, neon, holographic, glitch, etc.
- Cultural (5 styles): japanese, chinese, indian, african, aztec
- Other (8 styles): pixel_art, graffiti, collage, mosaic, etc.

### Workflow Style Flow (Fixed)

```
User: "Create DreamWorks style brewery images"
         ↓
Frontend: detectWorkflowPattern() → extracts style_preferences: "DreamWorks"
         ↓
Backend: WorkflowOrchestrationAgent._execute_image_generation_step()
         ↓
Style Processing: Maps "DreamWorks" → "dreamworks" (built-in key)
         ↓
Parameters: {prompt: "...", style: "dreamworks", ...}
         ↓
_execute_generate_image() → ImageGenerationService.generate_image(style="dreamworks")
         ↓
_apply_style_to_prompt(): Applies professional expansion
         ↓
Final Prompt: "{prompt}, DreamWorks 3D animation style, stylized expressive characters..."
```

---

## Files Modified

| File | Changes |
|------|---------|
| `content/image_generation.py` | Added 14 new animation styles (dreamworks, south_park, simpsons, etc.) |
| `agents/workflow_orchestration_agent.py` | Fixed style handling to use built-in styles, removed character references |
| `ai_core/templates/ai_image_studio.html` | Fixed workflow detection for images vs logos, style extraction patterns |

---

## Key Learnings

1. **Don't duplicate functionality** - The workflow agent had its own style dictionary when a comprehensive one already existed in ImageGenerationService.

2. **Character names override topics** - When you put "Shrek/Kung Fu Panda" in a prompt, the AI will generate those characters, not apply their style to something else.

3. **Prompt order matters** - Style should be APPENDED to the topic, not prepended, to keep the user's subject as the primary focus.

4. **Use mappings for variations** - Users might say "South Park" or "south_park" or "southpark" - normalize these to the canonical style key.

---

## Testing Commands

```bash
# Test DreamWorks style
"Research craft brewery branding and create three images using DreamWorks style"

# Test South Park style
"Create a South Park style image of a tech startup office"

# Test Ghibli style
"Create a Studio Ghibli style landscape of a mountain village"
```

---

## Next Session: Agent Architecture Deep Dive

The user wants to step back and evaluate all Agent flows to ensure they're being used to their fullest potential, and explore connecting the spider network for research capabilities.

**Areas to explore:**
- Full audit of all agents and their capabilities
- Agent interconnection and orchestration
- Spider network integration for real-time research
- Ensure no agent functionality is being bypassed or underutilized
