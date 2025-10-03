# METHOD_INDEX.md - Donkey Betz Developer Brain
*Auto-updated reference for all key methods, classes, and imports*

## 🧠 Quick Navigation
- [Authentication & Users](#authentication--users)
- [AI & Agents](#ai--agents)
- [Universal Business Builder](#universal-business-builder)
- [Content Pipeline Studio](#content-pipeline-studio)
- [Advanced Image Operations](#advanced-image-operations)
- [Asset Management](#asset-management)
- [Memory System](#memory-system)
- [Document Ingestion](#document-ingestion)
- [Email & Notifications](#email--notifications)
- [API Services](#api-services)
- [Models & Database](#models--database)
- [Flutter Services](#flutter-services)
- [React Command Center](#react-command-center)
- [Utilities & Helpers](#utilities--helpers)
- [Image Generation (Enhanced)](#image-generation-enhanced)

---

## Authentication & Users

### Django Backend
```python
# User Model
from accounts.models import User

# Authentication Views
from accounts.views import (
    CustomRegisterView,  # POST /api/auth/registration/
    CustomLoginView,     # POST /api/auth/login/
    CustomLogoutView,    # POST /api/auth/logout/
)

# JWT Token Handling
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication

# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import permission_classes
```

### Flutter Frontend
```dart
// Services
import 'package:momentum_flutter/services/auth_service.dart';
import 'package:momentum_flutter/services/token_service.dart';

// Key Methods
AuthService.login(email, password)
AuthService.register(email, password, firstName, lastName)
AuthService.logout()
AuthService.getAccessToken()
TokenService.getAccessToken()
TokenService.refreshToken()
```

---

## AI & Agents

### Agent Orchestra
```python
# Core Classes
from agent_orchestra.orchestrator import AgentOrchestrator
from agent_orchestra.models import (
    TaskOrchestration,
    AgentInstance,
    AgentTemplate,
)

# Key Methods
orchestrator = AgentOrchestrator(user)
orchestrator.execute_complex_task(task_description)
orchestrator.deploy_single_agent(agent_name, task, wait_for_completion=False)

# Management Commands
python manage.py create_agent_templates
python manage.py simulate_agent_progress --continuous --interval 30
python manage.py monitor_stuck_agents  # Monitor and restart stuck agents
python manage.py monitor_stuck_agents --once  # Run once to fix stuck agents
python manage.py monitor_stuck_agents --interval 30 --max-retries 3  # Custom settings
python manage.py test_reddit_scout_single --max-businesses 1  # Test Reddit Scout with control

# Monitoring Scripts
./monitor_agent_progress.sh  # Real-time agent progress monitoring
./fix_stuck_agents.py  # Stop simulations and restart stuck agents
./cancel_all_agents.py  # Cancel all running agents

# Frontend Fix Scripts (January 2, 2025)
node fix_api_endpoints.cjs  # Fix double /api/api/ prefix in all service files
python reset_test_user.py  # Reset testuser password to testpass123
```

### Reddit Scout Agent (Updated January 2, 2025)
```python
# Models
from agent_orchestra.models import RedditIdea
from agent_orchestra.reddit_startup_scout import RedditStartupScout

# Key Changes (January 2, 2025)
# - NO automatic business plan creation for ANY ideas
# - ALL ideas saved to database regardless of score (not just 7.0+)
# - Shows niche market opportunities (scores 5.0-6.9)
# - Manual "Create Business Plan" button in UI
# - Fixed user association for Reddit ideas

# API Endpoints
POST /api/agent-orchestra/reddit-scout/deploy/  # Deploy Reddit Scout
GET /api/agent-orchestra/reddit-ideas/  # List all discovered ideas
GET /api/agent-orchestra/reddit-ideas/{id}/  # Get specific idea
POST /api/agent-orchestra/reddit-ideas/{id}/create-business-plan/  # Manual creation
POST /api/agent-orchestra/reddit-ideas/{id}/update-status/  # Approve/reject idea

# New Workflow
1. Deploy Reddit Scout
2. Scout discovers and scores ALL ideas
3. Ideas saved to RedditIdea model
4. User reviews in "Reddit Ideas" tab  
5. User clicks "Create Business Plan" for selected ideas only
```

### Personal AI Service
```python
# Main Service
from ai_partner.services.personal_ai_service import PersonalAIService

# Key Methods
service = PersonalAIService()
await service.chat(message, user, conversation_id=None)
service.get_contextual_greeting(user, context_type='general')

# Agent Deployment
service._handle_agent_command(command_type, agent_name, task, user, message)
service._extract_email_from_message(message)
```

### Stock Trading System (NEW - January 2, 2025)
```python
# Models
from agent_orchestra.models_stock_tracking import (
    StockWatchlist,
    StockAlert,
    StockAnalysis,
    MarketScanResult,
    TradingStrategy,
    PortfolioTracking
)

# Stock Agents
from agent_orchestra.stock_agents import (
    StockAnalysisOrchestrator,
    MarketScannerOrchestrator,
    StockAgentTemplates
)

# Real-time Data
from agent_orchestra.enhanced_tools import EnhancedAgentTools
quote = await EnhancedAgentTools.get_real_time_quote(ticker)  # Alpha Vantage/yfinance

# WebSocket Consumer
from agent_orchestra.consumers.stock_price_consumer import StockPriceConsumer
# Connect: ws://localhost:8000/ws/stock-prices/?token=JWT_TOKEN
# Subscribe: {"type": "subscribe", "tickers": ["AAPL", "GOOGL"]}
# Get quote: {"type": "get_quote", "ticker": "AAPL"}

# Background Tasks
from agent_orchestra.tasks.stock_price_updater import (
    update_stock_prices,  # Updates all tracked tickers
    scan_market_opportunities,  # Market-wide scanning
    check_price_alerts  # Alert monitoring
)

# Services
from agent_orchestra.services.stock_alert_service import StockAlertService
await StockAlertService.create_alert(user, alert_data)

# API Endpoints
POST /api/agent-orchestra/stocks/create-agents/  # Create stock agent templates
POST /api/agent-orchestra/stocks/analyze/  # Analyze stock
POST /api/agent-orchestra/stocks/market-scan/  # Run market scan
GET /api/agent-orchestra/stocks/analyses/  # List analyses
GET /api/agent-orchestra/stocks/analyses/{id}/  # Get analysis details
GET /api/agent-orchestra/stocks/watchlists/  # List watchlists
POST /api/agent-orchestra/stocks/watchlists/  # Create watchlist
POST /api/agent-orchestra/stocks/watchlists/{id}/add-stock/  # Add to watchlist
POST /api/agent-orchestra/stocks/watchlists/{id}/remove-stock/  # Remove from watchlist
GET /api/agent-orchestra/stocks/websocket-info/  # Get WebSocket connection info
POST /api/agent-orchestra/stocks/alerts/create/  # Create alert
GET /api/agent-orchestra/stocks/alerts/list/  # List alerts
PUT /api/agent-orchestra/stocks/alerts/{id}/update/  # Update alert
DELETE /api/agent-orchestra/stocks/alerts/{id}/delete/  # Delete alert
GET /api/agent-orchestra/stocks/quote/{ticker}/  # Get real-time quote

# 8 Specialized Stock Agents
1. Market Intelligence Agent - Market trends, news sentiment
2. Technical Analysis Agent - Chart patterns, indicators
3. Fundamental Analysis Agent - Financials, valuation
4. Day Trading Strategy Agent - Scalping, momentum
5. Swing Trading Strategy Agent - Multi-day setups
6. Long-Term Investment Agent - Value investing
7. Risk Management Agent - Position sizing, hedging
8. Options Strategy Agent - Options pricing, Greeks

# React Components
import MarketScanner from './components/MarketScanner';
import WatchlistManager from './components/WatchlistManager';
import AlertManager from './components/AlertManager';

# Quick Actions Feature
- Stock Analysis Cards: Add to Watchlist, Set Alert, Re-analyze
- Watchlist Cards: Analyze, Set Alert, Refresh Quote
- Market Scanner: One-click analysis from results
```

### Stock Opportunities Management (NEW - July 3, 2025)
```python
# Models
from agent_orchestra.models_stock_opportunities import StockOpportunity

# Services
from agent_orchestra.services.stock_opportunity_extractor import StockOpportunityExtractor

# Views
from agent_orchestra.views_stock_opportunities import (
    list_stock_opportunities,
    get_stock_opportunity,
    update_opportunity_status,
    toggle_favorite,
    archive_opportunity,
    extract_opportunities_from_mission,
    get_watchlist_candidates
)

# Serializers
from agent_orchestra.serializers_stock_opportunities import (
    StockOpportunitySerializer,
    StockOpportunityDetailSerializer,
    StockOpportunityCreateSerializer
)

# React Component
import StockOpportunities from './components/StockOpportunities';

# Key Methods
# Extract opportunities from completed Stock Scout
opportunities = StockOpportunityExtractor.extract_opportunities_from_orchestration(orchestration_id)

# Filter and list opportunities
opportunities = StockOpportunity.objects.filter(
    user=user,
    status='discovered',
    opportunity_score__gte=7.0
)

# Update opportunity status workflow
opportunity.status = 'watching'  # discovered → reviewing → watching → analyzed
opportunity.save()

# Management Commands
python manage.py ensure_stock_scout_execution  # Ensure agents are running
python restart_stuck_stock_scout.py  # Restart stuck agents
python monitor_stock_scout.py  # Monitor agent progress
```

---

## Universal Business Builder

### Core Classes
```python
# Business Orchestrator
from universal_builder.business_orchestrator import BusinessOrchestrator
from universal_builder.models import GeneratedBusiness, GeneratedFile
from universal_builder.serializers import GeneratedBusinessSerializer

# Builder Agents
from universal_builder.builder_agents import (
    DjangoBuilderAgent,
    ExpressBuilderAgent,
    NextJSBuilderAgent,
    FastAPIBuilderAgent,
    RailsBuilderAgent,
    LaravelBuilderAgent
)

# Stack Decision Engine
from universal_builder.stack_decision_engine import StackDecisionEngine

# Agent Orchestra Integration
from agent_orchestra.business_builder_agent import BusinessBuilderAgent
from agent_orchestra.business_builder_executor import BusinessBuilderExecutor

# Key Methods
orchestrator = BusinessOrchestrator()
result = await orchestrator.build_business(business_idea, user_context)

# API Endpoints
POST /api/universal-builder/generate/  # Start async generation
POST /api/universal-builder/generate/sync/  # Synchronous generation
GET /api/universal-builder/progress/<task_id>/  # Check progress
GET /api/universal-builder/businesses/  # List generated businesses
GET /api/universal-builder/businesses/<id>/download/  # Download ZIP

# Management Commands
python manage.py create_business_builder_agent  # Create agent template

# Test Scripts
python test_universal_builder_auto.py  # Test automatic business generation
python test_saas_generation.py  # Test SaaS-specific generation
python test_business_builder_integration.py  # Test agent integration
python test_deployment.py  # Test deployment automation
```

### Deployment Automation (NEW!)
```python
# Deployment Service & Agent
from universal_builder.deployment_service import (
    DeploymentService,
    DeploymentConfig,
    CloudProvider,      # AWS, VERCEL, HEROKU, DIGITAL_OCEAN, RAILWAY, RENDER
    CICDPlatform        # GITHUB_ACTIONS, GITLAB_CI, CIRCLE_CI
)
from universal_builder.deployment_agent import DeploymentAgent

# Generate Deployment Configuration
agent = DeploymentAgent()
result = agent.generate_deployment(
    build_context=build_context,
    cloud_provider=CloudProvider.AWS,
    cicd_platform=CICDPlatform.GITHUB_ACTIONS,
    domain="example.com",
    environment_vars={"SECRET_KEY": "xxx"},
    ssl_enabled=True,
    auto_scaling=True,
    monitoring=True,
    backup_enabled=True
)

# Analyze Deployment Requirements
analysis = agent.analyze_deployment_requirements({
    'tech_stack': TechStack.DJANGO,
    'business_type': BusinessType.SAAS,
    'repository_host': 'github'
})
# Returns: recommended providers, CI/CD, costs, time estimates

# Generated Files Include:
# AWS: Terraform configs, ECS task definitions, ALB configs, RDS setup
# Vercel: vercel.json, next.config.js
# Heroku: Procfile, app.json, runtime.txt
# CI/CD: GitHub Actions workflows, GitLab CI configs
# Scripts: deploy.sh, rollback.sh, health-check.sh, backup.sh
# Monitoring: Prometheus, Grafana dashboards, alerting rules
# Documentation: DEPLOYMENT.md, DEPLOYMENT_CHECKLIST.md

# Cost Estimates by Provider (monthly):
# AWS: ~$80 (ECS + RDS + ALB)
# Vercel: ~$20 (Pro tier)
# Heroku: ~$16 (Basic dyno + DB)
# Railway: ~$10 (Usage-based)
# Render: ~$14 (Starter tier)
```

### React Components
```javascript
// Main Components
import UniversalBuilderDashboard from './components/UniversalBuilder/UniversalBuilderDashboard';
import BusinessTemplateGallery from './components/UniversalBuilder/BusinessTemplateGallery';
import TechStackVisualizer from './components/UniversalBuilder/TechStackVisualizer';
import GeneratedFilesExplorer from './components/UniversalBuilder/GeneratedFilesExplorer';
```

---

## Content Pipeline Studio

### React Frontend Service
```typescript
// Content Pipeline Service
import { contentPipelineService } from '@/services/api/contentPipeline.service';
import type { 
  ContentProject, 
  GeneratedContent, 
  VisualStyle, 
  ContentWorkflow 
} from '@/services/api/contentPipeline.service';

// Key Methods - Image Generation
contentPipelineService.generateImage(request: ImageGenerationRequest)
contentPipelineService.generateLogo(request: LogoGenerationRequest)
contentPipelineService.generateMeme(request: MemeGenerationRequest)
contentPipelineService.createAchievementImage(data)

// Key Methods - Video Generation  
contentPipelineService.generateVideo(request: VideoGenerationRequest)
contentPipelineService.getVideoStyles()
contentPipelineService.getVideoContent(contentId)

// Key Methods - Business Packages
contentPipelineService.createPitchDeck(request: PitchDeckRequest)
contentPipelineService.createProductDemo(request: ProductDemoRequest)
contentPipelineService.createBusinessPackage(request: BusinessPackageRequest)
contentPipelineService.createSocialCampaign(request: SocialCampaignRequest)

// Key Methods - Project Management
contentPipelineService.getUserProjects()
contentPipelineService.getProjectDetails(projectId)
contentPipelineService.startWorkflow(data)
contentPipelineService.updateWorkflowProgress(workflowId, data)

// Key Methods - Analytics
contentPipelineService.getContentAnalytics(timeframe?)
contentPipelineService.getProjectAnalytics(projectId)
```

### Django Backend Endpoints
```python
# Content Generation URLs (content/urls.py)
path('generate-image/', generate_real_image)         # DALL-E generation
path('generate-logo/', generate_logo)                # Logo creation
path('generate-meme/', generate_real_meme)           # Meme generation
path('video/generate/', generate_video_from_agents)  # Video generation
path('generate-package/', generate_content_package_view)  # Content packages

# Content Pipeline URLs  
path('pipeline/pitch-deck/', create_business_pitch_deck)      # Pitch decks
path('pipeline/product-demo/', create_product_demo)          # Product demos
path('pipeline/educational/', create_educational_content)    # Educational content
path('pipeline/social-campaign/', create_social_media_campaign)  # Social campaigns
path('pipeline/business-package/', create_complete_business_package)  # Business packages

# Project Management
path('pipeline/projects/', get_user_projects)               # List projects
path('pipeline/projects/<int:project_id>/', get_project_details)  # Project details
path('pipeline/workflow/start/', start_workflow)            # Start workflow
path('pipeline/workflow/<int:workflow_id>/progress/', update_workflow_progress)  # Update progress
```

### Component Usage
```typescript
// Import and Use
import ContentPipelineStudio from '@/components/ContentPipelineStudio';

// Component Features
// - Dashboard with quick stats and actions  
// - Project management with progress tracking
// - Content gallery with advanced filtering
// - Modal dialogs for all creation types
// - Real-time progress tracking
// - Template system with 15+ business templates
// - Analytics dashboard with insights
```

---

## Advanced Image Operations

### React Frontend Service  
```typescript
// Advanced Image Operations Service
import { advancedImageOpsService } from '@/services/api/advancedImageOps.service';
import type {
  ImageOperation,
  ImageEditRequest, 
  ImageUpscaleRequest,
  BatchOperationRequest,
  AdvancedImage,
  TaskStatus
} from '@/services/api/advancedImageOps.service';

// Key Methods - Image Editing
advancedImageOpsService.editImage(imageId, editRequest: ImageEditRequest)
advancedImageOpsService.upscaleImage(imageId, upscaleRequest: ImageUpscaleRequest)  
advancedImageOpsService.removeBackground(imageId)
advancedImageOpsService.createVariation(imageId, options)
advancedImageOpsService.inpaintImage(imageId, options)
advancedImageOpsService.applyStyleTransfer(imageId, options)

// Key Methods - Batch Operations
advancedImageOpsService.batchOperation(batchRequest: BatchOperationRequest)
advancedImageOpsService.batchDelete(imageIds: number[])
advancedImageOpsService.batchAddTags(imageIds: number[], tags: string[])
advancedImageOpsService.batchCategorize(imageIds: number[], categoryId: number)
advancedImageOpsService.batchExport(imageIds: number[], format: 'zip' | 'pdf' | 'gallery')

// Key Methods - Image Management
advancedImageOpsService.getAllImages()
advancedImageOpsService.searchImages(searchRequest: ImageSearchRequest)
advancedImageOpsService.toggleFavorite(imageId)
advancedImageOpsService.updateImage(imageId, updates)
advancedImageOpsService.downloadImage(imageId, format?)

// Key Methods - Task Monitoring
advancedImageOpsService.getTaskStatus(taskId: string)
advancedImageOpsService.cancelTask(taskId: string)
advancedImageOpsService.getOperationHistory(limit: number)
```

### Django Backend Endpoints
```python
# Unified Image Operations (content/views_unified.py)
path('images/unified/generate/', UnifiedGenerateView)     # Generate with any backend
path('images/<int:image_id>/edit/', ImageEditView)       # Advanced editing
path('images/<int:image_id>/upscale/', ImageUpscaleView) # Professional upscaling  
path('images/<int:image_id>/remove-background/', RemoveBackgroundView)  # Background removal
path('images/<int:image_id>/delete/', ImageDeleteView)   # Delete image

# Batch Operations
path('images/batch/', BatchOperationsView)               # Batch operations
path('images/all/', UnifiedImagesListView)             # List all images
path('images/search/', ImageSearchView)                # Advanced search

# Task Management
path('images/task/<str:task_id>/status/', TaskStatusView)  # Task status
path('images/backends/', AvailableBackendsView)          # Available backends

# Categories and Tags
path('images/categories/', CategoriesView)              # Category management
path('images/tags/', TagsView)                         # Tag management
```

### Edit Types Available
```python
# Image Edit Types (images/models.py)
EDIT_TYPE_CHOICES = [
    ("inpaint", "Inpaint"),           # Paint over masked areas
    ("variation", "Variation"),        # Create variations
    ("upscale", "Upscale"),           # Increase resolution
    ("enhance", "Enhance"),           # Improve quality
    ("style_transfer", "Style Transfer"), # Apply style from reference
    ("remove_background", "Remove Background")  # AI background removal
]

# Upscale Types
UPSCALE_TYPES = [
    ("conservative", "Conservative"),  # Preserves original style
    ("creative", "Creative"),         # Adds intelligent details  
    ("fast", "Fast"),                # Quick processing
    ("ultra", "Ultra")               # Maximum quality
]
```

### Component Usage  
```typescript
// Import and Use
import AdvancedImageOpsStudio from '@/components/AdvancedImageOpsStudio';

// Component Features
// - Professional image gallery with grid/list views
// - Advanced editing dialogs with sliders and controls
// - Batch selection and operations
// - Real-time task monitoring with progress bars  
// - Category and tag management
// - Advanced search and filtering
// - Operation history tracking
// - Multi-format downloads and exports
```

---

## Asset Management

### Core Models
```python
# Asset Management Models
from content.models.asset_management import (
    ProjectAssetLibrary,
    SharedAsset,
    AssetUsageLog,
    AssetRequest,
    BrandGuideline,
)

# Key Model Fields
ProjectAssetLibrary: orchestration, project_name, project_type, description, brand_guidelines
SharedAsset: library, asset_type, category, name, file_url, metadata, is_approved
AssetRequest: requesting_agent, assigned_agent, requirements, status
```

### Flutter Asset Management
```dart
// Models
import 'package:momentum_flutter/models/asset_models.dart';

// Classes
ProjectAssetLibrary // Project info with brand guidelines
SharedAsset        // Individual asset with metadata and sharing info
AssetUsageLog     // Usage tracking for cross-agent collaboration
AssetFilter       // Filter options for gallery
BrandColor        // Brand color from guidelines

// Services
import 'package:momentum_flutter/services/asset_service.dart';

AssetService.getOrchestrationAssets(orchestrationId)
AssetService.getAssetLibrary(orchestrationId)
AssetService.getBrandGuidelines(libraryId)
AssetService.clearCache()
AssetService.clearOrchestrationCache(orchestrationId)

// Widgets
import 'package:momentum_flutter/widgets/asset_card.dart';
import 'package:momentum_flutter/widgets/agent_collaboration_view.dart';

// Pages
import 'package:momentum_flutter/pages/asset_gallery_page.dart';

// Key Features
- Asset gallery with grid view
- Filter by type, agent, approval status, sharing
- Search functionality
- Brand guidelines viewer
- Cross-agent collaboration visualization
- Asset details dialog
```

### Services
```python
# Asset Pipeline Service
from content.services.asset_pipeline_service import AssetPipelineService

# Brand Guidelines Service
from content.services.brand_guidelines_service import BrandGuidelinesService

# Content Creation Pipeline
from content.services.content_creation_pipeline import ContentCreationPipeline

# Key Methods
pipeline = AssetPipelineService(agent_workspace)
await pipeline.create_asset(agent, asset_type, category, file_data, metadata)
await pipeline.request_asset(requesting_agent, asset_requirements)

brand_service = BrandGuidelinesService(library)
guidelines = brand_service.generate_brand_guidelines(context)
validation = brand_service.validate_asset(asset)
```

### API Endpoints
```python
# Asset Management
GET  /api/content/orchestrations/<id>/assets/       # Get project assets
POST /api/content/assets/                           # Create new asset
GET  /api/content/assets/<id>/                      # Get asset details
POST /api/content/assets/<id>/validate/             # Validate against brand
POST /api/content/asset-requests/                   # Request asset from agents
GET  /api/content/libraries/<id>/brand-guidelines/  # Get brand guidelines
```

### Usage Examples
```python
# Create asset library for orchestration
library = ProjectAssetLibrary.objects.create(
    orchestration=orchestration,
    project_name="My Business",
    project_type="app",
    description="Revolutionary app"
)

# Generate brand guidelines
brand_service = BrandGuidelinesService(library)
guidelines = brand_service.generate_brand_guidelines({
    'business_type': 'app',
    'industry': 'health',
    'target_audience': 'millennials'
})

# Create and validate asset
asset = SharedAsset.objects.create(
    library=library,
    created_by_agent=agent,
    asset_type='image',
    category='logo',
    name='Company Logo',
    file_url='https://storage.example.com/logo.png',
    metadata={'colors': ['#4CAF50', '#FFFFFF']}
)

validation = brand_service.validate_asset(asset)
if validation['is_compliant']:
    asset.is_approved = True
    asset.approval_score = validation['score']
    asset.save()
```

---

### Memory System
```python
# Memory Service
from ai_partner.memory_services.memory_service import MemoryService

# Models
from ai_partner.models import (
    ConversationMemory,
    ConversationSession,
)

# Key Methods
memory_service = MemoryService()
memories = await memory_service.search_memories(query, user_id, limit=5)
await memory_service.save_conversation(user_id, user_message, ai_response)
```

### Document Ingestion
```python
# Document Ingestion Service
from ai_partner.services.document_ingestion_service import DocumentIngestionService

# Initialize service
service = DocumentIngestionService(user)

# Load different document types
chunks = service.load_url("https://example.com/article")
chunks = service.load_pdf("/path/to/document.pdf")
chunks = service.load_youtube("https://youtube.com/watch?v=...")

# Chunk text intelligently
chunks = service.chunk_document(text, chunk_size=1000, overlap=100)

# Semantic chunking with document type awareness
chunks = service.semantic_chunk_document(text, doc_type='technical', chunk_size=1000)

# Process and create embeddings
memories = service.process_and_embed(chunks)

# API Endpoints
GET  /api/ai-partner/document-ingestion/test/
POST /api/ai-partner/document-ingestion/ingest-url/
POST /api/ai-partner/document-ingestion/ingest-pdf/
POST /api/ai-partner/document-ingestion/ingest-youtube/
```

---

## Email & Notifications

### Email Service
```python
# Resend Integration
from api.services.email_service import EmailService
from agent_orchestra.email_service import AgentReportEmailService

# Key Methods
email_service = EmailService()
email_service.send_agent_report(agent_instance, recipient_email)

# Celery Tasks
from agent_orchestra.tasks import check_and_send_agent_emails
```

### Video Service (Planned)
```python
# Video Generation
from api.services.video_service import VideoGenerationService

# Key Methods
video_service = VideoGenerationService()
await video_service.create_agent_video_report(agent_instance, video_style="professional")
```

---

## API Services

### API Intelligence
```python
# Main Service
from ai_partner.services.api_intelligence import APIIntelligenceService

# Individual APIs
from api_services.alpha_vantage import AlphaVantageAPI
from api_services.coingecko import CoinGeckoAPI
from api_services.news_api import NewsAPIService

# Key Methods
api_intel = APIIntelligenceService()
data = await api_intel.get_data_for_request(message)
```

### External Services
```python
# OpenAI
import openai
from django.conf import settings
openai.api_key = settings.OPENAI_API_KEY

# Common Pattern
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "system", "content": prompt}],
    temperature=0.7
)
```

### Real API Integrations (LIVE as of July 1, 2025!)
```python
# Enhanced Agent Tools - 27+ API integrations for real-time data
from agent_orchestra.enhanced_tools import EnhancedAgentTools

# ✅ LIVE Web Search (via SERPER_API_KEY)
results = await EnhancedAgentTools.web_search("AI market size 2024", num_results=5)
# Returns real search results from Serper API

# ✅ LIVE News Data (via NEWS_API_KEY)
news = await EnhancedAgentTools.news_api("artificial intelligence", limit=10)
# Returns current news articles from NewsAPI.org

# Financial Data (via ALPHA_VANTAGE_API_KEY - configured)
stock_data = await EnhancedAgentTools.yahoo_finance("AAPL")
market_data = await EnhancedAgentTools.statista_api("AI market", "market_size")

# Social Media Intelligence (via REDDIT_CLIENT_ID/SECRET)
reddit_posts = await EnhancedAgentTools.reddit_api("startups", limit=25)
sentiment = await EnhancedAgentTools.sentiment_api("This product is amazing!")

# Government & Legal (via GOVERNMENT_API_KEY, LEGISCAN_API_KEY)
bills = await EnhancedAgentTools.congress_api("AI regulation")
regulations = await EnhancedAgentTools.federal_register("fintech")
contracts = await EnhancedAgentTools.gov_contracts_api("technology", "Department of Defense")

# Research & Academic (via CORE_API_KEY, ELSEVIER_API_KEY, NCBI_API_KEY)
patents = await EnhancedAgentTools.patent_api("machine learning algorithms")
research = await EnhancedAgentTools.github_api("django rest framework")

# Document & Report Generation
pdf_report = await EnhancedAgentTools.pdf_generator(content, "business_report")
excel_model = await EnhancedAgentTools.spreadsheet_generator(data, "financial_model")
chart = await EnhancedAgentTools.chart_creator(data, "line")

# Stock Market Data - Multiple providers with fallback
from ai_partner.api_services.stock_market_api import StockMarketAPI
stock_api = StockMarketAPI()
price_data = await stock_api.get_stock_price("AAPL")
historical = await stock_api.get_historical_data("AAPL", period="1mo")
market_overview = await stock_api.get_market_overview()

# Cryptocurrency Data - Real prices and market data
from ai_partner.api_services.crypto_api import CryptoAPI
crypto_api = CryptoAPI()
crypto_price = await crypto_api.get_crypto_price("bitcoin")
market_cap = await crypto_api.get_market_cap_rankings(limit=10)
trending = await crypto_api.get_trending_cryptos()

# Weather Data - Current conditions and forecasts
from ai_partner.api_services.weather_api import WeatherAPI
weather_api = WeatherAPI()
current = await weather_api.get_current_weather("San Francisco")
forecast = await weather_api.get_forecast("San Francisco", days=5)

# News Aggregation - Multiple sources with categorization
from ai_partner.api_services.news_api import NewsAPIService
news_service = NewsAPIService()
headlines = news_service.get_top_headlines(category="technology")
search_results = news_service.search_news("AI startups", limit=10)

# Video Generation - Runway ML integration
from content.services.runway_api_service import RunwayAPIService
runway_service = RunwayAPIService()
video_url = await runway_service.generate_video(
    prompt="A futuristic city at sunset",
    duration=5,
    style="cinematic"
)
```

### ML API Services (NEW - July 6, 2025)
```python
# 🚀 Advanced API Services with ML Feature Extraction

# Reddit API Service - Real-time social sentiment
from agent_orchestra.services.reddit_api_service import RedditAPIService
reddit_service = RedditAPIService()
hot_ideas = await reddit_service.get_hot_ideas(limit=50)
trending = await reddit_service.get_trending_topics(lookback_hours=24)
user_cred = await reddit_service.get_user_credibility("username")
# ML Features: engagement_score, sentiment, user_credibility_score

# News API Service - Sentiment analysis & coverage metrics  
from agent_orchestra.services.news_api_service import NewsAPIService
news_service = NewsAPIService()
articles = await news_service.search_news("OpenAI", page_size=100)
headlines = await news_service.get_headlines(category="business")
sentiment_analysis = await news_service.analyze_sentiment_coverage(
    entity="AAPL",
    lookback_days=7
)
# ML Features: sentiment_score, coverage_intensity, source_credibility

# SEC API Service - Financial filings & insider trading
from agent_orchestra.services.sec_api_service import SECAPIService
sec_service = SECAPIService()
filings = await sec_service.get_company_filings("AAPL", limit=50)
insider_trading = await sec_service.get_insider_trading("AAPL", lookback_days=90)
financials = await sec_service.get_financial_statements("AAPL", "10-K")
# ML Features: filing_regularity_score, insider_confidence_score, material_events

# Polygon.io API Service - Real-time market data & technicals
from agent_orchestra.services.polygon_api_service import PolygonAPIService
polygon_service = PolygonAPIService()
quote = await polygon_service.get_real_time_quote("AAPL")
aggregates = await polygon_service.get_aggregates("AAPL", timespan="day")
options = await polygon_service.get_options_chain("AAPL")
# ML Features: momentum_score, RSI, volatility, put_call_ratio

# Vector ML Service - Semantic similarity features
from agent_orchestra.services.vector_ml_service import VectorMLService
vector_service = VectorMLService()
reddit_features = await vector_service.get_reddit_similarity_features(idea_text)
company_matches = await vector_service.get_company_match_features(idea_text)
news_patterns = await vector_service.get_news_pattern_features(ticker, headline)
# ML Features: similarity scores, pattern matching, historical correlations

# Enhanced Tools Integration - Updated with real APIs
from agent_orchestra.enhanced_tools import EnhancedAgentTools

# News with ML features
news_result = await EnhancedAgentTools.news_api("AI startup", limit=10)
# Returns: articles + ml_features + average_sentiment

# SEC with insider analysis
sec_result = await EnhancedAgentTools.sec_edgar_api("AAPL")
# Returns: filings + insider_trading + ml_features

# Polygon market data
market_data = await EnhancedAgentTools.polygon_market_data(
    symbol="AAPL",
    data_type="quote"  # or "aggregates", "options", "details"
)
# Returns: price data + technical indicators + ml_features

# Government & Legislative Data (NEW - July 6, 2025)
from agent_orchestra.services.government_api_service import GovernmentAPIService
gov_service = GovernmentAPIService()
bills = await gov_service.search_bills("AI regulation", states=['US'], limit=10)
regulations = await gov_service.search_regulations("fintech", document_type="rule")
contracts = await gov_service.search_contracts("technology services", agencies=["DoD"])
# ML Features: progress_score, momentum_score, bipartisan_score, impact_analysis

# Legislative ML Service - Business opportunity analysis
from agent_orchestra.services.legislative_ml_service import LegislativeMLService
leg_ml_service = LegislativeMLService()
opportunities = await leg_ml_service.analyze_legislative_opportunity(
    business_description="AI healthcare platform",
    sectors=["Healthcare", "Technology"]
)
bill_outcome = await leg_ml_service.predict_bill_outcome("HR-1234")
contract_matches = await leg_ml_service.find_contract_opportunities(
    company_capabilities="AI/ML development",
    certifications=["CMMI-3", "ISO-27001"]
)
regulatory_trends = await leg_ml_service.analyze_regulatory_trends(
    sectors=["Technology"],
    lookback_days=90
)

# All configured via .env (30+ API keys as of July 1, 2025):
# ✅ ACTIVE:
# SERPER_API_KEY - Web search (WORKING)
# NEWS_API_KEY - News aggregation (WORKING)
# OPENAI_API_KEY - AI processing (WORKING)
#
# 🟡 CONFIGURED & READY:
# ALPHA_VANTAGE_API_KEY - Stock market data
# POLYGON_API_KEY - Advanced market data
# SEC_API_KEY - SEC filings
# COINBASE_API_KEY - Crypto trading data
# COINGECKO_API_KEY - Crypto market data
# REDDIT_CLIENT_ID/SECRET - Reddit API
# CORE_API_KEY - Academic research
# ELSEVIER_API_KEY - Scientific papers
# NCBI_API_KEY - Biomedical research
# GOVERNMENT_API_KEY - Government data
# LEGISCAN_API_KEY - Legislative tracking
# Plus 20+ more APIs configured!
```

---

## Models & Database

### Core Models
```python
# User & Profile
from accounts.models import User
from core.models import UserProfile

# Agent Models
from agent_orchestra.models import (
    AgentTemplate,
    AgentInstance,
    TaskOrchestration,
)

# Memory Models
from ai_partner.models import (
    ConversationMemory,
    ConversationSession,
)

# Content Models
from content.models import (
    Prompt,
    PromptTag,
    VisualStyle,
)

# Asset Management Models
from content.models.asset_management import (
    ProjectAssetLibrary,
    SharedAsset,
    AssetUsageLog,
    AssetRequest,
    BrandGuideline,
)

# Vector Embedding Models (pgvector) - NEW July 6, 2025
from ai_partner.models import (
    ConversationEmbedding,  # 1536-dim vectors for chat history
    CodeEmbedding,         # 1536-dim vectors for code search
    ConversationSegment,   # Semantic embeddings for topics
)

# ML Vector Models
from agent_orchestra.models.ml_embeddings import (
    RedditIdeaEmbedding,        # Reddit posts with outcome tracking
    StockNewsEmbedding,         # News articles with price impact
    CompanyDescriptionEmbedding, # Company profiles for matching
    IdeaCompanySimilarity,      # Pre-computed similarity scores
    MLScoringVector,            # 512-dim compressed feature vectors
)

# Legislative Vector Models (NEW - July 6, 2025)
from agent_orchestra.models.legislative_embeddings import (
    LegislativeBillEmbedding,    # Federal/state bills with progress tracking
    RegulatoryDocumentEmbedding, # Federal regulations with impact scores
    GovernmentContractEmbedding, # Contract opportunities with matching
    BusinessImpactAnalysis,      # How legislation affects business sectors
    BillComparisonEmbedding,     # Pre-computed bill similarities
    LegislativeAlert,            # User alerts for legislative changes
    HistoricalLegislativePattern # ML patterns for outcome prediction
)
```

### Common Queries
```python
# Get user
user = User.objects.get(email="user@example.com")

# Get active orchestrations
active = TaskOrchestration.objects.filter(
    user=user,
    status__in=['planning', 'executing']
)

# Get completed agents
completed = AgentInstance.objects.filter(
    orchestration__user=user,
    current_status='completed'
)

# Vector similarity search (pgvector)
from pgvector.django import CosineDistance

# Find similar Reddit ideas
similar_ideas = RedditIdeaEmbedding.objects.annotate(
    similarity=CosineDistance('content_embedding', query_embedding)
).order_by('similarity')[:10]

# Find similar news patterns
similar_news = StockNewsEmbedding.objects.filter(
    ticker="AAPL"
).annotate(
    similarity=CosineDistance('headline_embedding', news_embedding)
).order_by('similarity')[:5]
```

---

## Flutter Services

### Core Services
```dart
// API Service
import 'package:momentum_flutter/services/api_service.dart';
ApiService.get(endpoint)
ApiService.post(endpoint, body)
ApiService.getAuthHeaders()

// Agent Orchestra Service  
import 'package:momentum_flutter/services/agent_orchestra_service.dart';
AgentOrchestraService.executeTask(taskDescription)
AgentOrchestraService.getActiveOrchestrations()

// Personal AI Service
import 'package:momentum_flutter/services/personal_ai_service.dart';
PersonalAIService.sendMessage(message, conversationId)
PersonalAIService.getContextualGreeting(contextType)

// Asset Service
import 'package:momentum_flutter/services/asset_service.dart';
AssetService.getOrchestrationAssets(orchestrationId)
AssetService.getAssetLibrary(orchestrationId)
AssetService.getBrandGuidelines(libraryId)
```

### UI Components
```dart
// Pages
import 'package:momentum_flutter/pages/personal_ai_chat_page.dart';
import 'package:momentum_flutter/pages/agent_orchestra_page.dart';
import 'package:momentum_flutter/pages/orchestration_details_page.dart';
import 'package:momentum_flutter/pages/asset_gallery_page.dart';

// Widgets
import 'package:momentum_flutter/widgets/premium_chat_bubble.dart';
import 'package:momentum_flutter/widgets/agent_card.dart';
import 'package:momentum_flutter/widgets/asset_card.dart';
import 'package:momentum_flutter/widgets/agent_collaboration_view.dart';
import 'package:momentum_flutter/widgets/api_intelligence_widgets.dart';
```

---

## React Command Center

### Setup & Configuration
```bash
# Navigate to React app
cd moveyourazz-command-center

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

### Core Services
```typescript
// API Service
import api, { endpoints } from './services/api';
api.get(endpoints.analytics.dashboard)
api.post(endpoints.agentOrchestra.create, data)

// WebSocket Service
import { realtimeService } from './services/realtime';
realtimeService.connect(token)
realtimeService.on('analytics:update', callback)
realtimeService.on('agent:progress', callback)

// State Management
import { useStore } from './store';
const { user, analytics, agents, setAnalytics } = useStore()
```

### Specialized API Services (Updated January 2, 2025)
```typescript
// Agent Orchestra Service
import { agentOrchestraService } from './services/api/agentOrchestra.service';
agentOrchestraService.listOrchestrations(filters)
agentOrchestraService.getOrchestration(id)
agentOrchestraService.getOrchestrationDetails(id)  // NEW - for fetching full details
agentOrchestraService.createOrchestration(data)
agentOrchestraService.executeOrchestration(id)
agentOrchestraService.getTemplates()
agentOrchestraService.getAgentTypes()
agentOrchestraService.subscribeToOrchestration(id)
// Reddit Ideas Methods (Enhanced)
agentOrchestraService.getRedditIdeas(params)
agentOrchestraService.createBusinessPlanForIdea(ideaId)  // Now returns idea_title
agentOrchestraService.updateIdeaStatus(ideaId, status, notes)
// Pipeline Methods
agentOrchestraService.listPipelines()
agentOrchestraService.createPipeline(data)
agentOrchestraService.executePipeline(id)
agentOrchestraService.getPipelineStatus(pipelineId, executionId)

// Asset Management Service
import { assetsService } from './services/api/assets.service';
assetsService.getAssets(filters)
assetsService.uploadAsset(file, metadata)
assetsService.getAssetDetails(id)
assetsService.downloadAsset(id)
assetsService.getAssetsByAgent(agentId)
assetsService.getAssetStatistics()

// Chat Service
import { chatService } from './services/api/chat.service';
chatService.sendMessage(message, options)
chatService.executeCommand(command, params)
chatService.getCommandSuggestions(input)
chatService.streamResponse(messageId, onChunk)
chatService.getConversationMemory(conversationId)

// Memory Service
import { memoryService } from './services/api/memory.service';
memoryService.searchMemories(query, filters)
memoryService.getMemoryConnections(memoryId)
memoryService.getMemoryTimeline(dateRange)
memoryService.createMemoryNote(content, metadata)
memoryService.getMemoryClusters()
memoryService.visualizeMemoryGraph()
```

### Magical Components
```tsx
// Animated Components
import { AnimatedNumber } from './components/magical/AnimatedNumber';
<AnimatedNumber value={396} format="percentage" duration={3000} />

// Glass Morphism Cards
import { GlowCard } from './components/magical/GlowCard';
<GlowCard glowColor="#0EA5E9" interactive>Content</GlowCard>

// Interactive Buttons
import { MagicButton } from './components/magical/MagicButton';
<MagicButton variant="primary" icon={<Sparkles />}>Deploy Magic</MagicButton>

// Particle Background
import { ParticleField } from './components/magical/ParticleField';
<ParticleField density={30} color="#0EA5E9" interactive />
```

### Agent Orchestra UI Components (Enhanced January 2, 2025)
```tsx
// Main Page
import AgentOrchestra from './pages/AgentOrchestra';
// Now properly handles selectedOrchestration state

// Reddit Ideas Panel
import RedditIdeasPanel from './components/RedditIdeasPanel';
// Enhanced with onOrchestrationCreated callback prop
<RedditIdeasPanel onOrchestrationCreated={setSelectedOrchestration} />

// Agent Details Display
// Now formats tool results as clean text instead of raw JSON
// Removes [TOOL_RESULT] markers and mock_data source info
// Shows "Action Steps (Updated!)" with bullet points for web searches
```

### Authentication Components (NEW!)
```tsx
// Auth Service
import { authService } from './services/auth.service';
authService.login(email, password)
authService.register(userData)
authService.logout()
authService.getAccessToken()
authService.refreshAccessToken()
authService.isAuthenticated()
authService.getCurrentUser()

// Auth Components
import Login from './pages/Login';
import Register from './pages/Register';
import ProtectedRoute from './components/auth/ProtectedRoute';

// Usage
<ProtectedRoute>
  <MainLayout />
</ProtectedRoute>
```

### Pages & Routing
```tsx
// Pages
import Dashboard from './pages/Dashboard';
import AnalyticsDashboard from './pages/AnalyticsDashboard';
import AgentOrchestra from './pages/AgentOrchestra';
import AssetGallery from './pages/AssetGallery';
import BusinessBuilder from './pages/BusinessBuilder';
import ChatCommand from './pages/ChatCommand';
import MemoryPalace from './pages/MemoryPalace';
import Login from './pages/Login';
import Register from './pages/Register';

// Router
import { router } from './router';
// Routes: 
// /login - Login page (public)
// /register - Register page (public)
// / - Dashboard (protected)
// /analytics - Analytics Dashboard (protected)
// /agent-orchestra - Agent Orchestra (protected)
// /assets - Asset Gallery (protected)
// /business-builder - Business Builder (protected)
// /chat - Chat Command (protected)
// /memory - Memory Palace (protected)
```

### Page-Specific Features
```tsx
// Agent Orchestra - 3D Battlefield
- Floating agent cards in 3D space
- Real-time progress updates via WebSocket
- Drag-and-drop agent deployment
- Agent collaboration visualization
- Export results to multiple formats

// Asset Gallery - Masonry Layout
- Dynamic masonry grid (CSS Grid)
- Filter by type, agent, date, project
- Preview modal with metadata
- Batch operations (download, share)
- Cross-agent asset flow visualization

// Business Builder - Visual Pipeline
- ReactFlow canvas with custom nodes
- Component library sidebar
- Drag-and-drop pipeline creation
- Real-time validation
- Export to executable workflow

// Chat Command - Enhanced Interface
- "/" command palette
- Syntax highlighting for code
- Memory context indicators
- Streaming responses
- Multi-modal inputs (text, voice, files)

// Memory Palace - 3D Visualization
- Three.js powered 3D space
- Memory nodes as floating orbs
- Semantic connections as glowing lines
- Time-based navigation
- Cluster visualization
```

### 3D Visualizations
```tsx
// Three.js Components
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Float, Text } from '@react-three/drei';

// Usage in Analytics Dashboard
<Canvas camera={{ position: [0, 0, 5] }}>
  <Float speed={1.5} rotationIntensity={1}>
    <mesh>
      <sphereGeometry args={[1, 32, 32]} />
      <meshStandardMaterial color="#0EA5E9" />
    </mesh>
  </Float>
  <OrbitControls enableZoom={false} />
</Canvas>
```

### Theme Configuration
```css
/* Tailwind Custom Theme */
colors: {
  'electric-blue': '#0EA5E9',
  'plasma-purple': '#8B5CF6',
  'success-green': '#10B981',
  'solar-orange': '#F59E0B',
  'deep-space': '#0F172A',
  'star-white': '#F8FAFC',
}

/* Glass Morphism (Tailwind v4 compatible) */
.glass-card {
  background-color: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 1rem;
}

/* Animations */
animation: {
  'glow': 'glow 2s ease-in-out infinite alternate',
  'float': 'float 6s ease-in-out infinite',
  'gradient-shift': 'gradient-shift 8s ease infinite',
}
```

### Debug Helpers
```tsx
// Toast Notifications
import toast from 'react-hot-toast';

toast.success('AI Magic Activated! ✨', {
  style: {
    background: 'rgba(16, 185, 129, 0.9)',
    color: '#fff',
    backdropFilter: 'blur(10px)',
  },
  icon: '🚀',
});

// Debug Logging
console.log('🎯 Component Mounted');
console.log('📊 Data:', data);
console.log('💰 AnimatedNumber:', value);
```

---

## Utilities & Helpers

### Django Utilities
```python
# Async Helpers
from asgiref.sync import sync_to_async, async_to_sync
from django.utils.decorators import sync_and_async_middleware

# JSON Response
from django.http import JsonResponse
from rest_framework.response import Response

# Decorators
from rest_framework.decorators import api_view, permission_classes
```

### Text Processing
```python
# Universal Text Cleaning Service
from core.services.text_cleaning_service import text_cleaner

# Clean any text
text_cleaner.clean_text(text, aggressive=False)

# Clean dictionaries/JSON
text_cleaner.clean_dict(data, aggressive=False)

# Clean lists
text_cleaner.clean_list(items, aggressive=False)

# Django Middleware (automatic)
'core.middleware.text_cleaning_middleware.UniversalTextCleaningMiddleware'
```

### Data Serialization & Formatting (Enhanced January 2, 2025)
```python
# Agent Orchestra Data Cleaning
from agent_orchestra.data_serialization_fix import (
    clean_step_data,  # Clean step data for display
    _clean_tool_result_text,  # Remove JSON artifacts from tool results
    normalize_agent_output_data  # Normalize agent outputs for frontend
)

# Enhanced Sync Executor (formats tool results)
from agent_orchestra.enhanced_sync_executor import EnhancedSyncAgentExecutor
# Now formats web_search results as bullet points instead of raw JSON
# Removes [TOOL_RESULT] markers and mock_data source info

# Reddit Ideas Business Plan Creation
from agent_orchestra.views_reddit_scout import create_business_plan_for_idea
# Now returns idea_title in response for proper UI display
```

### Firestore Business Chat
```python
# Service
from core.services.firestore_service import firestore_service

# Create business network
network_id = await firestore_service.create_business_network(
    business_name="Startup Name",
    founder_user=user,
    metadata={'industry': 'AI/ML'}
)

# Send message
message_id = firestore_service.send_message(
    network_id, 
    channel_id="general",
    message_data={
        'text': 'Hello team!',
        'sender_id': str(user.id),
        'sender_name': user.username,
        'type': 'user'
    }
)

# Send agent update
firestore_service.send_agent_update(network_id, agent_instance)

# Get messages
messages = firestore_service.get_network_messages(
    network_id, 
    channel_id="agents",
    limit=50
)

# Create client portal
portal_id = firestore_service.create_client_portal(
    network_id,
    client_email="client@example.com",
    allowed_channels=["general", "reports"]
)
```

### Flutter Utilities
```dart
// Text Utils (Enhanced for Agent Orchestra)
import 'package:momentum_flutter/utils/text_utils.dart';

// Main utilities
TextUtils.cleanText(text)  // Remove encoding issues, normalize whitespace
TextUtils.getDetailedAnalysis(outputData, finalReport)  // Extract step-by-step analysis
TextUtils.getKeyInsights(outputData, fallbackReport)   // Extract bullet points/insights

// Agent detail page
import 'package:momentum_flutter/pages/agent_detail_page.dart';
// Uses TextUtils to format agent outputs with proper sections

// Date Formatting
import 'package:intl/intl.dart';
DateFormat('MMM d, h:mm a').format(DateTime.now())
```

---

## Common Patterns

### API Endpoint Pattern
```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def endpoint_name(request):
    try:
        # Logic here
        return Response({'success': True, 'data': result})
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=400)
```

### Flutter API Call Pattern
```dart
try {
  final response = await ApiService.post('/api/endpoint/', {
    'param': value,
  });
  
  if (response['success']) {
    // Handle success
  }
} catch (e) {
  print('Error: $e');
}
```

### Celery Task Pattern
```python
@shared_task
def task_name(param1, param2):
    try:
        # Task logic
        return {'success': True, 'result': result}
    except Exception as e:
        logger.error(f"Task failed: {str(e)}")
        return {'success': False, 'error': str(e)}
```

---

## 🔄 Auto-Update Instructions

When adding new features:
1. Add the import path
2. Add key method signatures
3. Add common usage patterns
4. Update relevant section
5. Keep alphabetical order within sections

---

## Image Generation (Unified Multi-Backend System)

### ✅ IMPLEMENTED: Unified Image Service (DALL-E 3 + Stable Diffusion)
```python
# Unified Service - Orchestrates between backends
from content.services.unified_image_service import UnifiedImageService

# Models
from content.models import (
    GeneratedImage,          # DALL-E images
    StableDiffusionImage,    # SD images with full control
    ImageEdit,               # Edit history tracking
    UpscaleImage,           # Upscaled versions
    PromptHelper,           # Style presets
)

# Key Methods
service = UnifiedImageService()

# Generate with any backend
await service.generate_image(
    prompt="A happy donkey", 
    backend="dalle3",         # or "stable-diffusion"
    style="professional",
    user=user
)

# Edit images (remove background, enhance, relight)
await service.edit_image(image_id, edit_type='remove_background', user=user)
await service.edit_image(image_id, edit_type='enhance', user=user)
await service.edit_image(image_id, edit_type='relight', user=user)

# Upscale images
await service.upscale_image(image_id, upscale_type='conservative')  # Preserve details
await service.upscale_image(image_id, upscale_type='creative')     # AI enhancement

# Get available backends
backends = await service.get_available_backends()

# Check async task status
status = await service.get_image_status(task_id)
```

### API Endpoints (All Working!)
```python
# Unified endpoints
POST /api/content/images/unified/generate/      # Multi-backend generation
POST /api/content/images/<id>/edit/             # Image editing
POST /api/content/images/<id>/upscale/          # Image upscaling
POST /api/content/images/<id>/remove-background/# Quick background removal
GET  /api/content/images/task/<task_id>/status/ # Async task status
GET  /api/content/images/backends/              # List available backends
GET  /api/content/images/all/                   # All images from all backends

# Legacy DALL-E endpoints (still working)
GET  /api/content/images/visual-styles/
POST /api/content/images/generate/
GET  /api/content/images/my-images/
```

### Stable Diffusion Utilities
```python
# Core generation
from content.utils.stable_diffusion_api import generate_stable_diffusion_image

# Editing utilities
from content.utils.editing import (
    get_edit_endpoint,
    build_edit_payload, 
    save_edited_image
)

# Upscaling
from content.utils.upscaling import upscale_image

# Thumbnails
from content.utils.thumbnails import generate_thumbnails

# Helper functions
from content.helpers.image_urls import generate_absolute_urls
from content.helpers.post_generation_hooks import trigger_post_generation_hook
from content.helpers.prompt_generation_hook import prepare_final_prompt
```

### Celery Tasks
```python
# Async image processing
from content.tasks import (
    process_sd_image_request,      # SD generation
    process_edit_image_request,    # Image editing
    process_upscale_image_request, # Upscaling
    debug_sd_env                   # Debug SD setup
)

# Agent Orchestra tasks
from agent_orchestra.tasks import (
    execute_agents_async,              # Execute all agents for an orchestration
    check_and_send_agent_emails,       # Send completion emails
    check_and_send_telegram_notifications,  # Send Telegram updates
    send_agent_deployment_notification,     # Notify on deployment
    send_progress_update                    # Send progress updates
)
```

### Visual Styles
```python
# Current: 43 DALL-E optimized styles
VISUAL_STYLES = {
    'animation': ['pixar', 'disney', 'anime', 'studio_ghibli', 'cartoon'],
    'artistic': ['oil_painting', 'watercolor', 'impressionist', 'abstract', 'pop_art'],
    'photography': ['professional', 'portrait', 'landscape', 'street', 'macro'],
    'digital': ['3d_render', 'low_poly', 'vaporwave', 'cyberpunk', 'pixel_art'],
    'business': ['corporate', 'infographic', 'minimalist', 'flat_design', 'tech_startup'],
    'illustration': ['childrens_book', 'comic_book', 'technical', 'fashion', 'botanical'],
    'retro': ['vintage_poster', 'art_deco', 'retrowave', 'steampunk', 'film_noir'],
    'conceptual': ['surreal', 'fantasy', 'scifi', 'gothic', 'psychedelic', 'brutalist', 'art_nouveau', 'bauhaus']
}

# Additional from donkey_workspace: 24 professional styles
VisualStyleLibrary.get_all_styles()
VisualStyleLibrary.get_styles_by_category('Professional & Corporate')
VisualStyleLibrary.get_styles_for_profession('developer')
```

---

## Content Creation Pipeline (NEW!)

### Complete Pipeline Service
```python
# Main Pipeline Service
from content.services.content_creation_pipeline import ContentCreationPipeline

# Initialize
pipeline = ContentCreationPipeline()

# Create Business Pitch Deck Video
result = await pipeline.create_business_pitch_deck_video(
    business_data={
        'company_name': 'TechCorp',
        'tagline': 'Innovation at scale',
        'problem_statement': 'Market inefficiency',
        'market_size': '$50B',
        'visual_style': 'corporate'
    },
    user=user,
    style='corporate',
    platform='linkedin'
)

# Create Product Demo Video
result = await pipeline.create_product_demo_video(
    product_data={
        'name': 'Product X',
        'description': 'Revolutionary solution',
        'features': ['Feature 1', 'Feature 2']
    },
    user=user,
    angles=['front', 'side', 'detail', 'lifestyle'],
    style='product_photography'
)

# Create Educational Content
result = await pipeline.create_educational_content(
    topic_data={
        'topic': 'Machine Learning Basics',
        'key_points': ['Concepts', 'Applications'],
        'target_audience': 'beginners'
    },
    user=user,
    content_type='explainer',  # or 'infographic', 'tutorial'
    duration=60
)

# Create Social Media Campaign
result = await pipeline.create_social_media_content_factory(
    campaign_data={
        'campaign_name': 'Summer Launch',
        'message': 'New features available',
        'hashtags': ['#innovation', '#tech']
    },
    user=user,
    platforms=['instagram', 'tiktok', 'linkedin'],
    num_variations=5
)

# Create Complete Business Package
result = await pipeline.create_complete_business_package(
    business_plan={
        'company_name': 'StartupX',
        'industry': 'FinTech',
        'business_model': 'B2B SaaS',
        'value_proposition': 'Simplify payments'
    },
    user=user
)
```

### Video Generation Service (Enhanced)
```python
# Service
from content.services.video_generation_service import video_generation_service

# Generate video from images
video = await video_generation_service.generate_video_from_images(
    user=user,
    image_ids=[1, 2, 3, 4],
    video_config={
        'title': 'Product Journey',
        'platform': 'instagram',
        'duration_per_image': 3,
        'pan_zoom': 'ken_burns',
        'include_voiceover': True
    }
)

# Create slideshow video
result = await video_generation_service.create_video_from_slide_images(
    slide_images=[
        {'image': image_obj, 'title': 'Slide 1', 'narration': 'Intro...'},
        {'image': image_obj, 'title': 'Slide 2', 'narration': 'Main point...'}
    ],
    project_name='Pitch Deck',
    platform='linkedin'
)
```

### Pipeline API Endpoints
```python
# Content Pipeline Endpoints
POST /api/content/pipeline/pitch-deck/         # Business pitch deck video
POST /api/content/pipeline/product-demo/       # Product demo video
POST /api/content/pipeline/educational/        # Educational content
POST /api/content/pipeline/social-campaign/    # Social media campaign
POST /api/content/pipeline/business-package/   # Complete business package

# Project Management
GET  /api/content/pipeline/projects/           # List user projects
GET  /api/content/pipeline/projects/<id>/      # Project details

# Workflow Management
POST /api/content/pipeline/workflow/start/              # Start workflow
POST /api/content/pipeline/workflow/<id>/progress/      # Update progress
```

### Content Models
```python
# Pipeline Models
from content.models import (
    ContentProject,      # Container for complete projects
    GeneratedVideo,      # Video assets
    ContentWorkflow,     # Multi-step workflows
    ContentBatch,        # Batch processing
)

# Create project
project = ContentProject.objects.create(
    user=user,
    name="Q4 Marketing Campaign",
    project_type='social_campaign',
    metadata={'platforms': ['instagram', 'tiktok']}
)

# Track workflow
workflow = ContentWorkflow.objects.create(
    user=user,
    project=project,
    workflow_type='image_to_video',
    total_steps=5
)
workflow.mark_step_complete('Images generated')
```

### Content Templates
```python
# Management command to create templates
python manage.py create_pipeline_templates

# Template categories:
- business         # Pitch decks, business packages
- marketing        # Product demos, campaigns
- social_media     # Platform-specific content
- educational      # Tutorials, courses
- presentation     # Conferences, events
- creative         # Brand identity, portfolios
```

### Platform-Specific Settings
```python
# Platform configurations
PLATFORM_SETTINGS = {
    'instagram': {
        'aspect_ratio': '1:1',    # Square for feed
        'max_duration': 60,
        'format': 'mp4'
    },
    'tiktok': {
        'aspect_ratio': '9:16',   # Vertical
        'max_duration': 60,
        'format': 'mp4'
    },
    'linkedin': {
        'aspect_ratio': '16:9',   # Horizontal
        'max_duration': 600,      # 10 minutes
        'format': 'mp4'
    }
}
```

### Workflow Types
```python
WORKFLOW_TYPES = [
    'image_to_video',      # Transform images to video
    'pitch_deck',          # Business pitch creation
    'product_launch',      # Product launch materials
    'educational_course',  # Course content
    'brand_identity',      # Complete brand package
    'social_campaign'      # Multi-platform campaign
]
```

---

## Stock Trading & Market Analysis

### Stock Tracking Service
```python
from agent_orchestra.models_stock_tracking import StockAnalysis, StockWatchlist, StockAlert, PortfolioTracking
from agent_orchestra.services.stock_tracking_service import StockTrackingService
from agent_orchestra.services.portfolio_analytics_service import PortfolioAnalyticsService

# Create stock analysis
analysis = await StockTrackingService.analyze_stock(
    user=user,
    ticker='AAPL',
    analysis_type='comprehensive'  # or 'quick', 'technical', 'fundamental', 'day_trading', 'swing_trading'
)

# Get portfolio analytics
analytics = await PortfolioAnalyticsService.get_portfolio_analytics(
    user=user,
    time_range='3M'  # '1W', '1M', '3M', '6M', '1Y', 'YTD', 'ALL'
)
```

### Stock Scout Service - Multi-Source Intelligence
```python
from agent_orchestra.services.stock_scout_service import StockScoutService

# Deploy stock scouts
result = await StockScoutService.scout_stock_opportunities(
    user=user,
    scout_type='comprehensive',  # 'penny_stocks', 'value_plays', 'momentum'
    focus_areas=['tech', 'biotech']  # optional
)

# Scout types:
# - penny_stocks: High-risk/reward micro-caps
# - value_plays: Undervalued gems with strong fundamentals
# - momentum: Stocks in strong uptrends with volume
# - comprehensive: Full spectrum analysis
```

### Stock API Endpoints
```python
# Django URLs
path('stocks/analyze/', analyze_stock),
path('stocks/analyses/', list_stock_analyses),
path('stocks/portfolio/', get_portfolio_summary),
path('stocks/portfolio/analytics/', get_portfolio_analytics),
path('stocks/watchlists/', watchlists),
path('stocks/alerts/list/', list_alerts),

# Stock Scout endpoints
path('stocks/scout/', deploy_stock_scout),
path('stocks/scout/missions/', list_scout_missions),
path('stocks/scout/<int:orchestration_id>/results/', get_scout_results),
```

### React Stock Components
```typescript
// Import stock services
import { agentOrchestraService } from '@/services/api';

// Stock tracking page
import StockTracking from '@/pages/StockTracking';
import StockScout from '@/pages/StockScout';

// Deploy stock scout
const result = await agentOrchestraService.deployStockScout({
  scout_type: 'penny_stocks',
  focus_areas: ['biotech'],
  max_risk: 'medium'
});

// Get scout results
const results = await agentOrchestraService.getScoutResults(orchestrationId);
```

### Stock Models
```python
# StockAnalysis - AI-powered stock analysis results
class StockAnalysis(models.Model):
    ticker = models.CharField(max_length=10)
    analysis_type = models.CharField(max_length=50)
    recommendation = models.CharField(max_length=50)
    confidence_score = models.DecimalField(max_digits=4, decimal_places=2)
    target_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    stop_loss = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    orchestration = models.ForeignKey(TaskOrchestration, null=True)

# PortfolioTracking - User's stock portfolio
class PortfolioTracking(models.Model):
    ticker = models.CharField(max_length=10)
    shares = models.DecimalField(max_digits=15, decimal_places=4)
    average_cost = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
```

### Common Stock Trading Issues & Fixes

#### Stuck Stock Analyses (Fixed July 2, 2025)
```python
# PROBLEM: Stock analysis shows as "pending" even though orchestration completed
# CAUSE: Analysis record created but not updated with orchestration results

# SOLUTION: Clean up stuck analyses
python cleanup_stuck_analyses.py

# Check for stuck orchestrations
from agent_orchestra.models import TaskOrchestration
stuck = TaskOrchestration.objects.filter(
    overall_status__in=['pending', 'executing'],
    started_at__lt=timezone.now() - timedelta(minutes=10)
)
```

#### Portfolio Analytics Async Errors
```python
# PROBLEM: "You cannot call this from an async context"
# SOLUTION: Use sync_to_async wrapper

from asgiref.sync import sync_to_async

@sync_to_async
def get_portfolio_items():
    return list(PortfolioTracking.objects.filter(user=user))

portfolio_items = await get_portfolio_items()
```

---

## Common Issues & Fixes

### Groq Model Deprecation (Fixed June 25, 2025)
```python
# OLD - Deprecated model
model = "mixtral-8x7b-32768"  # This model has been decommissioned

# NEW - Use supported models
model = "llama3-70b-8192"     # Fast alternative
model = "llama3-8b-8192"      # Lighter option

# Updated in:
# - core/services/llm_service.py
# - api_services/model_selection_service.py
```

### AI Response Patterns (Fixed June 25, 2025)
```python
# PROBLEM: AI always starting with "Last time you asked about..."
# SOLUTION: Updated memory context handling

# ai_partner/memory_services/memory_retrieval_service.py
# Disabled explicit memory introductions:
if include_instructions and False:  # Disabled
    enhanced_prompt += "Based on our previous conversations:\n\n"

# ai_partner/personal_ai_services.py
# Updated system prompt instructions:
"Naturally incorporate relevant details from past discussions"
"NEVER start with 'Last time you asked about...'"
```

### LLM Service - Multi-Provider Support
```python
# Available providers and models
from core.services.llm_service import LLMService, LLMModel

# Initialize service
llm_service = LLMService()

# Generate with user preferences
response = llm_service.generate_completion(
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"}
    ],
    user_id=user.id,
    use_case="chat",  # chat, analysis, creative, code, fast
    temperature=0.7
)

# Supported models after June 25 update:
# OpenAI: gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo
# Claude: claude-3-opus, claude-3-sonnet, claude-3-haiku, claude-3-5-sonnet
# Groq: llama3-70b-8192, llama3-8b-8192 (mixtral-8x7b removed)
# Gemini: gemini-1.5-pro, gemini-1.5-flash, gemini-2.0-flash-exp
```

## Test Scripts

### Backend Test Scripts
```bash
# Authentication & User Management
python test_minimal_auth.py              # Test basic auth endpoints

# Agent Orchestra & Asset Management
python scripts/test_asset_generation.py  # Test asset pipeline, brand guidelines, cross-agent sharing

# Social Features
python test_herd_flow.py                 # Test herd management
python test_workout_flow.py              # Test workout logging
python test_mood_flow.py                 # Test mood tracking

# Integration Tests
python manage.py test_telegram_bot <chat_id>  # Test Telegram bot integration
```

### Asset Generation Test (`scripts/test_asset_generation.py`)
Tests the complete asset generation pipeline:
- Forces orchestration completion
- Creates ProjectAssetLibrary
- Generates brand guidelines
- Creates assets (logo, business plan, marketing materials)
- Tests cross-agent asset sharing
- Validates brand compliance
- Shows asset usage tracking

**Usage**: `python scripts/test_asset_generation.py`

**Output**: Creates test assets for orchestration ID 54 (dog grooming business)

## Common Errors & Quick Fixes

### Content Model Import Errors (Fixed June 26, 2025)
```python
# PROBLEM: ImportError: cannot import name 'StableDiffusionImage' from 'content.models'
# MISSING MODELS: StableDiffusionImage, ImageEdit, UpscaleImage, ContentProject, GeneratedVideo

# SOLUTION: Comment out imports until models are created
# from ..models import StableDiffusionImage, ImageEdit, UpscaleImage  # TODO: Create these models

# AFFECTED FILES:
# - content/services/unified_image_service.py
# - content/views_unified.py  
# - content/services/content_creation_pipeline.py
# - content/views_pipeline.py

# TEMPORARY FIX: Return placeholder responses
return {
    'task_id': 'placeholder-task-id',
    'status': 'not_implemented',
    'message': 'Feature not yet implemented'
}
```

### Indentation Errors in Empty If Blocks
```python
# PROBLEM: IndentationError: expected an indented block after 'if' statement
# OCCURS WHEN: Commenting out code inside if blocks

# SOLUTION: Add pass statement
if condition:
    # TODO: await sync_to_async(project.images.add)(image)
    pass  # Required to avoid indentation error
```

### API Endpoint Double Prefix (Fixed January 2, 2025)
```bash
# PROBLEM: GET http://127.0.0.1:8000/api/api/agent-orchestra/orchestrations/ 404 (Not Found)
# CAUSE: Service files using /api/ prefix when base URL already includes /api

# SOLUTION: Run the fix script
cd moveyourazz-command-center
node fix_api_endpoints.cjs

# AFFECTED FILES:
# - src/services/api/agentOrchestra.service.ts
# - src/services/api/endpoints.ts
# - src/services/api/*.service.ts
# - src/services/auth.service.ts
```

### Stuck Agents at 19:30 (Fixed January 2, 2025)
```python
# PROBLEM: Agents stuck at exactly 19 minutes 30 seconds
# CAUSE: Hardcoded 20-minute timeout in orchestrator.py

# SOLUTION 1: Stop simulations and fix stuck agents
./fix_stuck_agents.py

# SOLUTION 2: Use management command
python manage.py monitor_stuck_agents --once

# SOLUTION 3: Configure timeout in settings
AGENT_TIMEOUT_SECONDS = 1800  # 30 minutes
```

### Reddit Ideas Not Showing (Fixed January 2, 2025)
```python
# PROBLEM: Reddit Ideas tab shows no data
# CAUSE: Ideas created under different user (admin vs testuser)

# SOLUTION: Check and reassign ideas
python manage.py shell
from agent_orchestra.models import RedditIdea
from django.contrib.auth import get_user_model
User = get_user_model()

# Check ideas by user
RedditIdea.objects.values('user__username').annotate(count=Count('id'))

# Assign to testuser
user = User.objects.get(username='testuser')
RedditIdea.objects.update(user=user)
```

Last Updated: January 2, 2025 - Added agent monitoring fixes, API endpoint fixes, and Reddit Ideas troubleshooting