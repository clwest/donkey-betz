# 🔬 IMAGE-TO-3D API RESEARCH

**Research Date:** November 11, 2025
**APIs Evaluated:** 3 providers
**Recommendation:** Meshy AI (primary) + TripoSR (proof of concept)

---

## 📊 **API COMPARISON MATRIX**

| Feature | Meshy AI | Tripo AI | TripoSR (Replicate) |
|---------|----------|----------|---------------------|
| **Speed** | 1-3 min | 1-2 min | <30 sec ⭐ |
| **Quality** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **STL Export** | ✅ Native | ✅ Native | ✅ OBJ→STL |
| **API Quality** | Excellent | Good | Basic |
| **Documentation** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Cost/Model** | $0.20-0.40 | $0.10-0.20 | $0.01-0.05 ⭐ |
| **Monthly Cost** | $20-60 | $16-40 | Pay-per-use |
| **Integration Time** | 4-6 hours | 4-6 hours | 1-2 hours ⭐ |
| **3D Print Ready** | ✅ Yes | ✅ Yes | ⚠️ May need cleanup |
| **Texture Quality** | Excellent | Good | Basic |
| **Mesh Topology** | Quad/Triangle | Triangle | Triangle |
| **Max Polycount** | 300K | 200K | ~50K |
| **PBR Textures** | ✅ Yes | ✅ Yes | ❌ No |
| **Commercial License** | ✅ Pro+ | ✅ Pro+ | ✅ MIT |

---

## 🏆 **#1: MESHY AI (RECOMMENDED FOR PRODUCTION)**

### **Overview:**
Industry-leading image-to-3D API with excellent documentation and 3D print optimization.

### **API Details:**

**Base URL:**
```
https://api.meshy.ai/openapi/v1
```

**Authentication:**
```bash
Authorization: Bearer ${MESHY_API_KEY}
```

**Core Endpoint:**
```bash
POST /image-to-3d
Content-Type: application/json

{
  "image_url": "https://your-domain.com/image.jpg",
  "ai_model": "latest",
  "topology": "triangle",
  "target_polycount": 50000,
  "should_remesh": true,
  "should_texture": true,
  "enable_pbr": true
}

Response:
{
  "result": "task_id_here"
}
```

**Status Check:**
```bash
GET /image-to-3d/{task_id}

Response:
{
  "id": "task_id",
  "status": "SUCCEEDED",
  "model_urls": {
    "glb": "https://...",
    "fbx": "https://...",
    "obj": "https://...",
    "stl": "https://...",
    "usdz": "https://..."
  },
  "texture_urls": [
    {
      "base_color": "https://...",
      "metallic": "https://...",
      "roughness": "https://...",
      "normal": "https://..."
    }
  ],
  "thumbnail_url": "https://..."
}
```

**Status Values:**
- `PENDING` - Task queued
- `IN_PROGRESS` - Generating mesh
- `SUCCEEDED` - Ready to download
- `FAILED` - Error occurred
- `CANCELED` - User canceled

### **Key Parameters:**

**topology** (string):
- `"triangle"` - Standard for 3D printing (default)
- `"quad"` - Better for animation/editing

**target_polycount** (integer: 100-300,000):
- `10,000` - Low detail, fast printing
- `30,000` - Standard quality (default)
- `50,000` - High detail
- `100,000+` - Very high detail (slower printing)

**should_remesh** (boolean):
- `true` - Clean mesh topology (default)
- `false` - Preserve original mesh (more detail)

**enable_pbr** (boolean):
- `true` - Physically-based rendering textures
- `false` - Base color only

### **Pricing:**

**Subscription Plans:**
```
FREE: $0/month
- 200 credits/month
- Basic features
- ⚠️ API access ending March 20, 2025

PRO: $20/month
- 1,000 credits/month
- API access
- All features
- ⭐ RECOMMENDED

MAX: $60/month
- 4,000 credits/month
- API access
- Priority processing

MAX UNLIMITED: $120/month
- 4,000 credits/month
- Unlimited relaxed generations
- API access
- Fastest processing
```

**Credit Costs:**
- Standard generation: 10-20 credits
- High-quality generation: 20-40 credits
- **Average:** ~20 credits per 3D model
- **Per model cost:** $0.20-0.40 (Pro tier)

**Special Offer:**
- Coupon code: `APIACCESS` - 40% discount
- Temporary 50% discount on Meshy-6-preview (until Sep 30, 2025)

### **Strengths:**
✅ Best quality output
✅ Native STL export (3D print ready)
✅ Excellent API documentation
✅ Fast generation (1-3 minutes)
✅ PBR textures included
✅ Clean mesh topology
✅ Flexible polycount control

### **Weaknesses:**
❌ Higher cost than alternatives
❌ Requires Pro subscription for API
❌ Free tier ending soon

### **Best For:**
- Production deployments
- High-quality miniatures
- Customer-facing features
- Commercial products

---

## 🥈 **#2: TRIPO AI (ALTERNATIVE)**

### **Overview:**
Cost-effective alternative with good quality and Text-to-CAD capabilities.

### **API Details:**

**Base URL:**
```
https://api.tripo3d.ai/v2
```

**Authentication:**
```bash
Authorization: Bearer ${TRIPO_API_KEY}
```

**Endpoint:**
```bash
POST /image-to-3d
{
  "image": "base64_string_or_url",
  "model_type": "standard",
  "export_format": "stl"
}
```

### **Pricing:**

```
BASIC: $0/month
- 300 credits/month
- 1 concurrent task

PROFESSIONAL: $15.90/month (annual) or $19.90/month
- 3,000 credits/month
- 10 concurrent tasks
- API access

ADVANCED: $39.90/month (annual) or $49.90/month
- 8,000 credits/month
- 15 concurrent tasks
- API access
- Priority processing
```

**Per Model Cost:** ~$0.10-0.20

### **Strengths:**
✅ Lower cost than Meshy
✅ Text-to-CAD capability
✅ Fast generation
✅ Good quality

### **Weaknesses:**
❌ Less documentation than Meshy
❌ Slightly lower quality
❌ Fewer export format options

### **Best For:**
- Budget-conscious deployments
- High-volume generations
- Text-to-CAD workflows

---

## 🥉 **#3: TRIPOSR VIA REPLICATE (BUDGET/POC)**

### **Overview:**
Open-source model available on Replicate. Fastest and cheapest option.

### **API Details:**

**Using Replicate (You Already Have Integration!):**

```python
import replicate

# You already have this code pattern from character training!
output = replicate.run(
    "camenduru/tripo-sr:latest",
    input={
        "image": "https://your-image-url.jpg"
    }
)

# Returns OBJ file URL
obj_url = output
```

### **Pricing:**

**Replicate Per-Second Billing:**
- ~$0.023/second on A100 GPU
- Average generation: 0.5-2 seconds
- **Per model cost:** $0.01-0.05

**No Subscription Required:**
- Pay only for what you use
- No minimum commitment
- No API keys to manage (uses your Replicate account)

### **Strengths:**
✅ Extremely fast (<30 seconds)
✅ Lowest cost ($0.01-0.05 per model)
✅ Already integrated (Replicate)
✅ Open source (MIT license)
✅ No subscription needed

### **Weaknesses:**
❌ Lower quality than Meshy/Tripo
❌ Basic topology (may need cleanup)
❌ No textures (geometry only)
❌ OBJ format (need conversion to STL)
❌ Limited customization options

### **Best For:**
- Proof of concept (TODAY!)
- Budget prototyping
- High-volume low-cost generation
- Quick iteration

---

## 🎯 **RECOMMENDATION: TWO-PHASE APPROACH**

### **Phase 1: Proof of Concept (TODAY)**

**Use TripoSR on Replicate:**
- Already integrated ✅
- Fastest implementation (1-2 hours)
- Lowest cost ($0.01-0.05 per model)
- Perfect for testing workflow

**Goal:** Generate first physical Donkey TODAY!

```python
# Quick implementation in replicate_provider.py
def image_to_3d_quick(self, image_url):
    """Quick 3D conversion for testing"""
    output = replicate.run(
        "camenduru/tripo-sr:latest",
        input={"image": image_url}
    )
    return output  # OBJ file URL
```

### **Phase 2: Production Integration (TOMORROW)**

**Use Meshy AI:**
- Best quality for customers
- Native STL export
- Professional-grade output
- Worth the investment

**Goal:** Production-ready feature on platform!

```python
# Full implementation in meshy_provider.py
class MeshyProvider:
    def image_to_3d(self, image_url, **options):
        """Production 3D conversion"""
        # Full implementation with all options
        # Status polling, error handling, etc.
```

---

## 📊 **COST COMPARISON (100 Models)**

| Provider | Monthly Cost | Per Model | Total Cost |
|----------|-------------|-----------|------------|
| **TripoSR** | $0 (pay per use) | $0.01-0.05 | $1-5 |
| **Tripo AI** | $15.90 + usage | $0.10-0.20 | $15.90 + $10-20 = ~$26-36 |
| **Meshy AI** | $20 + usage | $0.20-0.40 | $20 + $20-40 = ~$40-60 |

**For 100 models/month:**
- TripoSR: $1-5 total ⭐ (cheapest)
- Tripo AI: $26-36 total
- Meshy AI: $40-60 total (best quality)

**Break-even Analysis:**
- If charging $49.99 per miniature
- 100 models = ~$5,000 revenue
- API costs = $1-60
- **Profit margin: 99-99.8%**

---

## 🔧 **TECHNICAL SPECIFICATIONS**

### **Input Requirements:**

**All APIs accept:**
- JPEG, PNG, WEBP formats
- Recommended: 512x512 to 2048x2048
- Clear subject with good lighting
- Minimal background clutter
- Single object/character preferred

**Best Results:**
- Square or near-square aspect ratio
- High contrast between subject and background
- Multiple angles (for multi-image APIs)
- Consistent lighting
- Sharp focus

### **Output Formats:**

**Meshy AI:**
- GLB (web preview)
- FBX (game engines)
- OBJ (universal)
- **STL (3D printing)** ✅
- USDZ (AR/iOS)

**Tripo AI:**
- GLB
- FBX
- OBJ
- **STL** ✅
- USDZ

**TripoSR:**
- OBJ (convert to STL)

### **3D Printing Considerations:**

**Mesh Requirements:**
- Watertight geometry (no holes)
- Manifold edges (proper topology)
- Reasonable polycount (10K-100K)
- Wall thickness >= 1-2mm
- No floating geometry

**Meshy Optimization:**
```json
{
  "topology": "triangle",
  "target_polycount": 50000,
  "should_remesh": true,
  "optimize_for_printing": true
}
```

**Post-Processing:**
- Import to Blender/Meshmixer (if needed)
- Check for errors (non-manifold geometry)
- Add supports (in slicer software)
- Scale to desired size
- Export to slicer (Cura, PrusaSlicer)

---

## 🚀 **INTEGRATION COMPLEXITY**

### **TripoSR (1-2 hours):**
```
Complexity: ⭐ (Very Easy)

Reason:
- Already have Replicate integration
- Single function call
- No new dependencies
- Minimal code changes
```

### **Tripo AI (4-6 hours):**
```
Complexity: ⭐⭐⭐ (Medium)

Reason:
- New API integration
- API key management
- Status polling needed
- Format conversion
```

### **Meshy AI (4-6 hours):**
```
Complexity: ⭐⭐⭐ (Medium)

Reason:
- New API integration
- Well-documented (easier)
- Status polling needed
- Multiple export formats
```

---

## 📈 **SCALABILITY ANALYSIS**

### **100 Models/Month:**
```
TripoSR:  $1-5        ✅ Excellent
Tripo:    $26-36      ✅ Good
Meshy:    $40-60      ✅ Acceptable
```

### **1,000 Models/Month:**
```
TripoSR:  $10-50      ✅ Excellent
Tripo:    $100-200    ✅ Good
Meshy:    $200-400    ⚠️ Consider Unlimited plan
```

### **10,000 Models/Month:**
```
TripoSR:  $100-500    ✅ Excellent (no subscription)
Tripo:    $800-1,600  ⚠️ Need volume pricing
Meshy:    $120/mo     ✅ Unlimited plan covers this
```

---

## 🎯 **FINAL RECOMMENDATION**

### **For TODAY (Proof of Concept):**
**Use TripoSR on Replicate**
- Fastest to implement (1-2 hours)
- Cheapest ($0.01-0.05 per model)
- Already integrated
- Perfect for testing

### **For TOMORROW (Production):**
**Use Meshy AI**
- Best quality for customers
- Professional-grade output
- Native STL export
- Worth the $20-60/month investment

### **For FUTURE (Scale):**
**Hybrid Approach:**
- Meshy for customer-facing features
- TripoSR for internal testing/prototypes
- Best of both worlds

---

## 📝 **ACTION ITEMS**

### **Immediate (TODAY):**
- [ ] Sign up for Replicate (if not already done)
- [ ] Test TripoSR with one AI-generated image
- [ ] Download OBJ file
- [ ] Convert to STL
- [ ] Send to 3D printer
- [ ] **CELEBRATE FIRST PHYSICAL DONKEY!** 🎉

### **Tomorrow:**
- [ ] Sign up for Meshy AI Pro ($20/month with APIACCESS coupon)
- [ ] Implement `meshy_provider.py`
- [ ] Add database models
- [ ] Build AI Assistant function
- [ ] Create frontend UI

### **This Weekend:**
- [ ] Test production workflow
- [ ] Generate 10 test models
- [ ] Refine print settings
- [ ] Launch feature!

---

## 🔗 **USEFUL LINKS**

### **API Documentation:**
- **Meshy:** https://docs.meshy.ai/en/api/image-to-3d
- **Tripo:** https://platform.tripo3d.ai/docs
- **TripoSR:** https://replicate.com/camenduru/tripo-sr

### **Sign Up:**
- **Meshy:** https://www.meshy.ai/pricing (Use code: APIACCESS)
- **Tripo:** https://www.tripo3d.ai/pricing
- **Replicate:** https://replicate.com/ (Already have account)

### **Technical Resources:**
- **TripoSR Paper:** https://arxiv.org/abs/2403.02151
- **TripoSR GitHub:** https://github.com/VAST-AI-Research/TripoSR
- **Meshy Blog:** https://www.meshy.ai/blog/image-to-3d

---

**Status:** ✅ RESEARCH COMPLETE
**Recommendation:** TripoSR (TODAY) → Meshy AI (PRODUCTION)
**Next:** Read [02_COST_ANALYSIS.md](02_COST_ANALYSIS.md)
