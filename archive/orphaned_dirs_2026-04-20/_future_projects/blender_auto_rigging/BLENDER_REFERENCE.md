# Blender Installation Reference

**Installation Date:** November 16, 2025
**Verification Status:** ✅ COMPLETE

---

## Installation Details

- **Location:** `/Applications/Blender.app`
- **Binary:** `/Applications/Blender.app/Contents/MacOS/Blender`
- **Version:** 4.5.3 LTS
- **Build Date:** September 9, 2025
- **Build Hash:** 67807e1800cc
- **Python Version:** 3.11.11

---

## Python API

- **bpy module:** `/Applications/Blender.app/Contents/Resources/4.5/scripts/modules/bpy/`
- **Status:** ✅ Working
- **Test:** `import bpy` successful

---

## Addons

### Rigify (Auto-Rigging)
- **Status:** ✅ ENABLED
- **Module:** `rigify`
- **Purpose:** Automatic character rigging for animations

---

## Command Reference

### Run Blender (GUI)
```bash
/Applications/Blender.app/Contents/MacOS/Blender
```

### Run Blender (Background/Headless)
```bash
/Applications/Blender.app/Contents/MacOS/Blender --background
```

### Run Python Script
```bash
/Applications/Blender.app/Contents/MacOS/Blender --background --python script.py
```

### Run Python Expression
```bash
/Applications/Blender.app/Contents/MacOS/Blender --background --python-expr "import bpy; print(bpy.app.version)"
```

### Aliases (Added to ~/.zshrc)
```bash
blender           # GUI mode
blender-bg        # Background mode
```

**Note:** Restart terminal or run `source ~/.zshrc` to activate aliases

---

## Verification Tests Passed

✅ Blender executable found
✅ Version check successful (4.5.3 LTS)
✅ Python API accessible
✅ bpy module imports successfully
✅ Scene operations working (created test cube)
✅ Rigify addon enabled
✅ Preferences saved

---

## Ready For

- ✅ Auto-rigging tests
- ✅ 3D model import (.glb, .fbx, .obj)
- ✅ Character rigging with Rigify
- ✅ Animation creation
- ✅ Export to .fbx for DaVinci Resolve

---

**Next Step:** Set up test environment and select test characters!
