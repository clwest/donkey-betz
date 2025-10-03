# 🎨 AI Content Studio

**STATUS: ✅ FULLY OPERATIONAL** - Phase 1 & 2 Complete!

A comprehensive AI-powered content generation platform that creates text, images, and videos using multiple AI APIs. Built with Django backend and vanilla JavaScript frontend with TailwindCSS.

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![Django](https://img.shields.io/badge/django-4.2+-brightgreen)
![Status](https://img.shields.io/badge/status-production_ready-success)

---

## 🎉 What's New (2025-08-28)

### Authentication System Added! 🔐
- ✅ **User Login/Registration**: Secure authentication system
- ✅ **Session Persistence**: Stay logged in across refreshes
- ✅ **Content Ownership**: All content tied to user accounts
- ✅ **User Menu**: Profile, gallery, history, logout options

### Phase 2 Complete - Video Generation! 🎬
- ✅ **Runway ML Integration**: Text-to-image and image-to-video (2-step process)
- ✅ **Real-time Progress**: Live progress tracking for generation
- ✅ **Video Player**: Built-in player with download capabilities
- ✅ **Motion Presets**: Zoom, pan, orbit animations
- ✅ **Style Presets**: Cinematic, realistic, anime, abstract

### Phase 1 Complete - Content Creation
- ✅ **Blog Generation**: SEO-optimized with tone control
- ✅ **Social Media**: Multi-platform content creation
- ✅ **53+ Image Styles**: Professional visual styles
- ✅ **Batch Generation**: Up to 10 variations at once
- ✅ **Gallery System**: Save and organize content

---

## ✨ Core Features

### 🎬 Video Generation (NEW!)
- **Text-to-Video**: Generate videos from text descriptions using Gen-4 Image
- **Image-to-Video**: Animate existing images with Gen-3 Alpha Turbo
- **Progress Tracking**: Real-time generation status updates
- **Style Control**: Cinematic, Realistic, Anime, Abstract presets
- **Motion Control**: Zoom in, Pan left, Orbit animations
- **Duration Options**: 5 or 10 second videos
- **Resolution**: 720p and 1080p output

### 📝 Content Creation
- **Blog Posts**: 
  - SEO-optimized with meta descriptions
  - Tone control (Professional, Casual, Technical, Marketing)
  - Length options (500, 1000, 2000+ words)
  - Target audience customization
- **Social Media**:
  - Twitter, LinkedIn, Instagram, Facebook
  - Platform-specific character limits
  - Hashtag generation
  - Multiple variations per platform

### 🖼️ Image Generation
- **53+ Professional Styles**:
  - Photography (Portrait, Landscape, Macro, etc.)
  - Digital Art (Cyberpunk, Fantasy, Anime, etc.)
  - Traditional Art (Oil, Watercolor, Sketch, etc.)
  - Business (Infographic, Presentation, Diagram)
- **Advanced Features**:
  - Batch generation (up to 10 at once)
  - Image-to-image transformation
  - Upscaling (2-4x enhancement)
  - Background removal
  - Inpainting & Outpainting

### 🎨 Stability AI Suite
- **15+ Tools**: Upscale, Inpaint, Outpaint, Remove Background
- **Search & Replace**: Natural language object replacement
- **Sketch to Image**: Convert drawings to finished art
- **3D Generation**: 2D images to 3D models (GLB format)

---

## 🚀 Quick Start

### One Command Setup

```bash
# Clone and start everything
git clone https://github.com/yourusername/ai-content-studio.git
cd ai-content-studio
make dev
```

Access at:
- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8001/api/
- **Admin Panel**: http://localhost:8001/admin/

### Manual Setup

1. **Install dependencies**
```bash
pip install -r backend/requirements.txt
```

2. **Configure API keys**
```bash
# Copy example env file
cp backend/.env.example backend/.env

# Edit with your API keys
nano backend/.env
```

3. **Run migrations**
```bash
cd backend
python manage.py migrate
python manage.py createsuperuser
```

4. **Start services**
```bash
# Terminal 1: Backend
cd backend && python manage.py runserver 8001

# Terminal 2: Frontend
cd frontend && python -m http.server 8080
```

---

## 🔧 Configuration

### Required API Keys

Add to `backend/.env`:

```env
# Essential APIs
OPENAI_API_KEY=sk-...          # GPT text generation
STABILITY_API_KEY=sk-...       # Stable Diffusion images
RUNWAY_API_KEY=key_...         # Video generation

# Optional APIs
ANTHROPIC_API_KEY=sk-ant-...   # Claude
GROQ_API_KEY=gsk_...          # Groq LLM
GEMINI_API_KEY=AIza...        # Google Gemini

# Django
SECRET_KEY=your-secret-key
DEBUG=True
```

### Get API Keys
- **OpenAI**: https://platform.openai.com/
- **Stability AI**: https://platform.stability.ai/
- **Runway ML**: https://app.runwayml.com/
- **Anthropic**: https://console.anthropic.com/

---

## 📁 Project Structure

```
ai-content-studio/
├── backend/
│   ├── api/                   # REST API endpoints
│   │   ├── views_video.py    # Video generation
│   │   ├── views_blog.py     # Blog generation
│   │   └── views_social.py   # Social media
│   ├── content/               # Core models
│   ├── integrations/          # External APIs
│   │   └── runway_service.py # Runway ML integration
│   └── media/                 # Generated content
├── frontend/
│   ├── index.html            # Main UI
│   └── styles_data.js        # 53+ visual styles
├── documentation/
│   ├── CLAUDE.md             # AI assistant guide
│   ├── NEW_FEATURES.md       # Feature list
│   └── VIDEO_GENERATION_COMPLETE.md
└── Makefile                  # Dev commands
```

---

## 🎯 API Examples

### Video Generation
```javascript
// Text to Video
fetch('/api/video/text-to-video/', {
  method: 'POST',
  headers: {
    'Authorization': 'Token YOUR_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    prompt: "A serene lake at sunrise",
    duration: 5,
    resolution: "720p"
  })
})

// Check Status
fetch('/api/video/status/TASK_ID/')
```

### Blog Generation
```javascript
fetch('/api/content/blog/generate/', {
  method: 'POST',
  body: JSON.stringify({
    topic: "AI in Healthcare",
    tone: "professional",
    length: "medium"
  })
})
```

---

## 🛠️ Development Commands

```bash
make dev        # Start everything
make stop       # Stop all services
make status     # Check status
make migrate    # Run migrations
make test       # Run tests
make clean      # Clean temp files
```

---

## 📊 Performance Metrics

| Feature | Time | Cost |
|---------|------|------|
| Image Generation | 5-15 sec | $0.002 |
| Video Generation | 30-60 sec | $0.05 |
| Blog Post | 10-30 sec | $0.01 |
| Social Posts | 5-10 sec | $0.005 |

---

## 🔒 Security

- ✅ API keys in environment variables
- ✅ Token authentication
- ✅ CORS configured
- ✅ Input validation
- ✅ Rate limiting

---

## 🐛 Troubleshooting

### Common Issues

**CORS Errors**
```bash
# Check backend is on port 8001
make status
```

**API Key Errors**
```bash
# Verify keys loaded
cd backend
python manage.py shell
>>> from core.settings import RUNWAY_API_KEY
>>> print(bool(RUNWAY_API_KEY))
```

**Database Issues**
```bash
make migrate
```

---

## 📈 Roadmap - Phase 3: Campaign Mode

### 🎯 Next Phase: Unified Campaign Generation
- [ ] **Campaign Mode**: Generate complete marketing campaigns from one prompt
- [ ] **One-Click Generation**: Blog + Social + Images + Video in one go
- [ ] **Gallery Integration**: Auto-pull relevant images from user's gallery
- [ ] **Memory Consistency**: Ensure brand voice across all assets
- [ ] **Export Package**: Download all campaign assets as ZIP
- [ ] **Progress Dashboard**: Real-time tracking of all asset generation
- [ ] **Campaign Templates**: Save and reuse successful campaigns

### 🔮 Future Enhancements
- [ ] A/B testing for campaigns
- [ ] Video editing (trim, merge)
- [ ] Mobile responsive design
- [ ] Team collaboration
- [ ] Analytics dashboard
- [ ] Webhook notifications
- [ ] API access for programmatic generation

---

## 🤝 Contributing

1. Fork the repo
2. Create feature branch (`git checkout -b feature/Amazing`)
3. Commit changes (`git commit -m 'Add Amazing'`)
4. Push branch (`git push origin feature/Amazing`)
5. Open Pull Request

---

## 📝 License

MIT License - see LICENSE file

---

## 🙏 Credits

Built with APIs from:
- OpenAI (GPT-4)
- Stability AI (Stable Diffusion)
- Runway ML (Gen-3 Alpha)
- Anthropic (Claude)

---

**Status**: Production Ready | **Version**: 2.0 | **Last Updated**: Aug 28, 2025