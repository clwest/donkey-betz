(.venv) ➜  move_that_ass git:(main) ✗ make run-backend-ws
Redis is already running
Celery worker is already running
Collecting static files if needed...
python3 backend/manage.py collectstatic --noinput

0 static files copied to '/Users/donkeyking/development/move_that_ass/backend/static', 171 unmodified, 446 post-processed.
Starting Django with WebSocket support using Daphne...
cd backend && daphne -b 0.0.0.0 -p 8000 server.asgi:application
INFO Feature Flag Middleware initialized
WARNING Resend package not installed. Email functionality will be disabled.
INFO Starting server at tcp:port=8000:interface=0.0.0.0
INFO HTTP/2 support not enabled (install the http2 and tls Twisted extras)
INFO Configuring endpoint tcp:port=8000:interface=0.0.0.0
INFO Listening on TCP address 0.0.0.0:8000
INFO Available image generation backends: ['dalle3', 'stable-diffusion']
WARNING Resend package not available - emails will not be sent
WARNING Telegram package not available - bot functionality disabled
INFO Reddit API clients initialized successfully
127.0.0.1:50055 - - [10/Jul/2025:17:39:46] "OPTIONS /api/auth/login/" 200 -
127.0.0.1:50058 - - [10/Jul/2025:17:39:47] "POST /api/auth/login/" 200 552
127.0.0.1:50058 - - [10/Jul/2025:17:39:47] "GET /api/auth/user/" 200 61
127.0.0.1:50058 - - [10/Jul/2025:17:39:47] "GET /api/auth/user/" 200 61
127.0.0.1:50067 - - [10/Jul/2025:17:39:47] "WSCONNECTING /ws/dashboard-stats/" - -
127.0.0.1:50067 - - [10/Jul/2025:17:39:47] "WSDISCONNECT /ws/dashboard-stats/" - -
INFO WebSocket authenticated user: testuser
127.0.0.1:50081 - - [10/Jul/2025:17:39:47] "WSCONNECTING /ws/dashboard-stats/" - -
INFO WebSocket authenticated user: testuser
INFO User 2 connected to dashboard stats WebSocket
127.0.0.1:50081 - - [10/Jul/2025:17:39:47] "WSCONNECT /ws/dashboard-stats/" - -
INFO User 2 connected to dashboard stats WebSocket
127.0.0.1:50055 - - [10/Jul/2025:17:39:47] "OPTIONS /api/core/dashboard/stats/" 200 -
127.0.0.1:50076 - - [10/Jul/2025:17:39:47] "OPTIONS /api/core/analytics/dashboard/" 200 -
127.0.0.1:50068 - - [10/Jul/2025:17:39:47] "OPTIONS /api/core/analytics/dashboard/" 200 -
127.0.0.1:50074 - - [10/Jul/2025:17:39:47] "OPTIONS /api/core/dashboard/" 200 -
127.0.0.1:50071 - - [10/Jul/2025:17:39:47] "OPTIONS /api/agent-orchestra/orchestrations/" 200 -
127.0.0.1:50073 - - [10/Jul/2025:17:39:47] "OPTIONS /api/agent-orchestra/templates/" 200 -
127.0.0.1:50055 - - [10/Jul/2025:17:39:47] "OPTIONS /api/agent-orchestra/orchestrations/" 200 -
127.0.0.1:50076 - - [10/Jul/2025:17:39:47] "OPTIONS /api/agent-orchestra/templates/" 200 -
127.0.0.1:50058 - - [10/Jul/2025:17:39:47] "GET /api/auth/user/" 200 61
INFO User 2 disconnected from dashboard stats WebSocket
127.0.0.1:50068 - - [10/Jul/2025:17:39:47] "OPTIONS /api/core/dashboard/" 200 -
127.0.0.1:50058 - - [10/Jul/2025:17:39:47] "GET /api/auth/user/" 200 61
127.0.0.1:50085 - - [10/Jul/2025:17:39:47] "GET /api/core/dashboard/stats/" 200 203
127.0.0.1:50091 - - [10/Jul/2025:17:39:47] "GET /api/core/dashboard/" 200 571
127.0.0.1:50095 - - [10/Jul/2025:17:39:47] "GET /api/agent-orchestra/templates/" 200 15851
127.0.0.1:50091 - - [10/Jul/2025:17:39:47] "GET /api/core/dashboard/" 200 571
127.0.0.1:50089 - - [10/Jul/2025:17:39:47] "GET /api/core/analytics/dashboard/" 200 2434
127.0.0.1:50085 - - [10/Jul/2025:17:39:47] "GET /api/agent-orchestra/templates/" 200 15851
127.0.0.1:50089 - - [10/Jul/2025:17:39:47] "GET /api/core/analytics/dashboard/" 200 2434
127.0.0.1:50094 - - [10/Jul/2025:17:39:47] "GET /api/agent-orchestra/orchestrations/" 200 1668609
127.0.0.1:50089 - - [10/Jul/2025:17:39:48] "GET /api/agent-orchestra/orchestrations/" 200 1668609
127.0.0.1:50117 - - [10/Jul/2025:17:39:48] "WSCONNECTING /ws/dashboard-stats/" - -
INFO WebSocket authenticated user: testuser
127.0.0.1:50117 - - [10/Jul/2025:17:39:48] "WSCONNECT /ws/dashboard-stats/" - -
INFO User 2 connected to dashboard stats WebSocket
127.0.0.1:50123 - - [10/Jul/2025:17:39:52] "GET /api/core/dashboard/stats/" 200 203
127.0.0.1:50117 - - [10/Jul/2025:17:39:53] "WSDISCONNECT /ws/dashboard-stats/" - -
127.0.0.1:50081 - - [10/Jul/2025:17:39:53] "WSDISCONNECT /ws/dashboard-stats/" - -
INFO User 2 disconnected from dashboard stats WebSocket
INFO User 2 disconnected from dashboard stats WebSocket
127.0.0.1:50158 - - [10/Jul/2025:17:39:59] "OPTIONS /api/auth/user/" 200 -
127.0.0.1:50159 - - [10/Jul/2025:17:39:59] "OPTIONS /api/auth/user/" 200 -
127.0.0.1:50161 - - [10/Jul/2025:17:39:59] "WSCONNECTING /ws/dashboard-stats/" - -
INFO WebSocket authenticated user: testuser
127.0.0.1:50161 - - [10/Jul/2025:17:39:59] "WSDISCONNECT /ws/dashboard-stats/" - -
127.0.0.1:50175 - - [10/Jul/2025:17:39:59] "WSCONNECTING /ws/dashboard-stats/" - -
INFO WebSocket authenticated user: testuser
INFO User 2 connected to dashboard stats WebSocket
INFO User 2 disconnected from dashboard stats WebSocket
127.0.0.1:50175 - - [10/Jul/2025:17:39:59] "WSCONNECT /ws/dashboard-stats/" - -
INFO User 2 connected to dashboard stats WebSocket
127.0.0.1:50165 - - [10/Jul/2025:17:39:59] "OPTIONS /api/agent-orchestra/orchestrations/" 200 -
127.0.0.1:50166 - - [10/Jul/2025:17:39:59] "OPTIONS /api/agent-orchestra/templates/" 200 -
127.0.0.1:50171 - - [10/Jul/2025:17:39:59] "OPTIONS /api/core/analytics/dashboard/" 200 -
127.0.0.1:50158 - - [10/Jul/2025:17:39:59] "OPTIONS /api/core/analytics/dashboard/" 200 -
127.0.0.1:50159 - - [10/Jul/2025:17:39:59] "OPTIONS /api/core/dashboard/stats/" 200 -
127.0.0.1:50168 - - [10/Jul/2025:17:39:59] "OPTIONS /api/core/dashboard/" 200 -
127.0.0.1:50165 - - [10/Jul/2025:17:39:59] "OPTIONS /api/agent-orchestra/orchestrations/" 200 -
127.0.0.1:50166 - - [10/Jul/2025:17:39:59] "OPTIONS /api/agent-orchestra/templates/" 200 -
127.0.0.1:50171 - - [10/Jul/2025:17:39:59] "OPTIONS /api/core/dashboard/" 200 -
127.0.0.1:50169 - - [10/Jul/2025:17:39:59] "GET /api/auth/user/" 200 61
127.0.0.1:50181 - - [10/Jul/2025:17:39:59] "GET /api/agent-orchestra/templates/" 200 15851
127.0.0.1:50187 - - [10/Jul/2025:17:39:59] "GET /api/core/dashboard/" 200 571
127.0.0.1:50185 - - [10/Jul/2025:17:39:59] "GET /api/core/dashboard/stats/" 200 203
127.0.0.1:50169 - - [10/Jul/2025:17:39:59] "GET /api/auth/user/" 200 61
127.0.0.1:50181 - - [10/Jul/2025:17:39:59] "GET /api/agent-orchestra/templates/" 200 15851
127.0.0.1:50187 - - [10/Jul/2025:17:39:59] "GET /api/core/dashboard/" 200 571
127.0.0.1:50183 - - [10/Jul/2025:17:39:59] "GET /api/core/analytics/dashboard/" 200 2434
127.0.0.1:50178 - - [10/Jul/2025:17:40:00] "GET /api/agent-orchestra/orchestrations/" 200 1668609
127.0.0.1:50183 - - [10/Jul/2025:17:40:00] "GET /api/core/analytics/dashboard/" 200 2434
127.0.0.1:50216 - - [10/Jul/2025:17:40:00] "WSCONNECTING /ws/dashboard-stats/" - -
INFO WebSocket authenticated user: testuser
127.0.0.1:50216 - - [10/Jul/2025:17:40:00] "WSCONNECT /ws/dashboard-stats/" - -
INFO User 2 connected to dashboard stats WebSocket
127.0.0.1:50187 - - [10/Jul/2025:17:40:00] "GET /api/agent-orchestra/orchestrations/" 200 1668609
127.0.0.1:50244 - - [10/Jul/2025:17:40:04] "GET /api/core/dashboard/stats/" 200 203
127.0.0.1:50175 - - [10/Jul/2025:17:40:09] "WSDISCONNECT /ws/dashboard-stats/" - -
INFO User 2 disconnected from dashboard stats WebSocket
127.0.0.1:50258 - - [10/Jul/2025:17:40:09] "OPTIONS /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 -
127.0.0.1:50244 - - [10/Jul/2025:17:40:09] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50268 - - [10/Jul/2025:17:40:10] "WSCONNECTING /ws/dashboard-stats/" - -
INFO WebSocket authenticated user: testuser
127.0.0.1:50268 - - [10/Jul/2025:17:40:10] "WSCONNECT /ws/dashboard-stats/" - -
INFO User 2 connected to dashboard stats WebSocket
127.0.0.1:50244 - - [10/Jul/2025:17:40:14] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50244 - - [10/Jul/2025:17:40:20] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50244 - - [10/Jul/2025:17:40:25] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50401 - - [10/Jul/2025:17:42:03] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50401 - - [10/Jul/2025:17:42:09] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50421 - - [10/Jul/2025:17:42:14] "OPTIONS /api/ai-partner/memory/search/?query=Are+you+able+to+evolve+anymore%3F&limit=3" 200 -
INFO Memory search request: user=2, query='Are you able to evolve anymore?...'
INFO 🔍 DEBUG MemoryRetrieval: Starting search for user 2, query: 'Are you able to evolve anymore?...'
127.0.0.1:50401 - - [10/Jul/2025:17:42:14] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO 🧠 DEBUG: Generated query embedding (dim: 1536)
INFO 📊 DEBUG: Vector search returned 6 results
INFO 🎯 DEBUG: Top 5 similarity scores: [0.5447275316281294, 0.42099865642154866, 0.4058091817555092, 0.40527593524908634, 0.3949865941715349]
INFO ⚠️  DEBUG: Using threshold 0.7, but scores are: min=0.3950, max=0.5447
INFO ✅ DEBUG: Returning 0 memory contexts
127.0.0.1:50423 - - [10/Jul/2025:17:42:15] "GET /api/ai-partner/memory/search/?query=Are+you+able+to+evolve+anymore%3F&limit=3" 200 67
127.0.0.1:50421 - - [10/Jul/2025:17:42:15] "OPTIONS /api/ai-partner/chat/" 200 -
INFO DEBUG: Personal AI chat request - User: testuser, Message: Are you able to evolve anymore?...
INFO DEBUG: include_memories = True, context_type = general, device_type = web
WARNING Session handling error (likely test context): get() returned more than one ConversationSession -- it returned more than 20!
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO 🧠 Revolutionary Intelligent Prompting enabled for user 2
127.0.0.1:50432 - - [10/Jul/2025:17:42:15] "WSCONNECTING /ws/dashboard-stats/" - -
127.0.0.1:50432 - - [10/Jul/2025:17:42:15] "WSDISCONNECT /ws/dashboard-stats/" - -
INFO WebSocket authenticated user: testuser
127.0.0.1:50442 - - [10/Jul/2025:17:42:15] "WSCONNECTING /ws/dashboard-stats/" - -
INFO WebSocket authenticated user: testuser
INFO User 2 connected to dashboard stats WebSocket
127.0.0.1:50442 - - [10/Jul/2025:17:42:15] "WSCONNECT /ws/dashboard-stats/" - -
INFO User 2 connected to dashboard stats WebSocket
INFO User 2 disconnected from dashboard stats WebSocket
127.0.0.1:50440 - - [10/Jul/2025:17:42:15] "GET /api/core/dashboard/" 200 571
127.0.0.1:50401 - - [10/Jul/2025:17:42:15] "GET /api/core/dashboard/stats/" 200 203
127.0.0.1:50439 - - [10/Jul/2025:17:42:15] "GET /api/agent-orchestra/templates/" 200 15851
127.0.0.1:50440 - - [10/Jul/2025:17:42:15] "GET /api/auth/user/" 200 61
127.0.0.1:50401 - - [10/Jul/2025:17:42:15] "GET /api/core/dashboard/" 200 571
127.0.0.1:50435 - - [10/Jul/2025:17:42:15] "GET /api/core/analytics/dashboard/" 200 2434
127.0.0.1:50439 - - [10/Jul/2025:17:42:16] "GET /api/agent-orchestra/templates/" 200 15851
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Using EnhancedMemoryService with extracted vector intelligence
INFO DEBUG: Starting memory retrieval for user 2
INFO DEBUG: Searching memories with query: 'Are you able to evolve anymore?...'
INFO Using EXTRACTED enhanced memory search with multi-factor ranking
127.0.0.1:50440 - - [10/Jul/2025:17:42:16] "GET /api/auth/user/" 200 61
127.0.0.1:50435 - - [10/Jul/2025:17:42:16] "GET /api/core/analytics/dashboard/" 200 2434
127.0.0.1:50437 - - [10/Jul/2025:17:42:16] "GET /api/agent-orchestra/orchestrations/" 200 1668609
127.0.0.1:50435 - - [10/Jul/2025:17:42:16] "GET /api/agent-orchestra/orchestrations/" 200 1668609
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Trying fixed memory search for MemoryEntry model
127.0.0.1:50467 - - [10/Jul/2025:17:42:16] "WSCONNECTING /ws/dashboard-stats/" - -
INFO WebSocket authenticated user: testuser
INFO Found 110 memories with embeddings for user 2
127.0.0.1:50467 - - [10/Jul/2025:17:42:16] "WSCONNECT /ws/dashboard-stats/" - -
INFO User 2 connected to dashboard stats WebSocket
INFO Fixed memory search returned 10 results
INFO DEBUG: Found 10 raw memories
INFO 🎯 Ranking 10 memories for query: 'Are you able to evolve anymore?...'
INFO 📊 Top ranked memory scores:
INFO   1. Total: 0.485 | Recency: 1.00 | Relevance: 0.19 | Continuity: 0.30
INFO   2. Total: 0.446 | Recency: 1.00 | Relevance: 0.19 | Continuity: 0.00
INFO   3. Total: 0.433 | Recency: 1.00 | Relevance: 0.21 | Continuity: 0.00
INFO DEBUG: Selected 5 top-ranked memories
INFO   Memory 1: The system has completed multiple agent deployments recently, including Research, Business, and Tech... (rank: 0.485)
INFO   Memory 2: AI and machine learning have significantly advanced in 2025, transforming software development with ... (rank: 0.446)
INFO   Memory 3: The user inquired whether the recurring issue offering 'research papers' and 'packages' was connecte... (rank: 0.433)
INFO   Memory 4: In the conversation, the AI initially claimed it couldn't access memories from June 28, 2025, citing... (rank: 0.431)
INFO   Memory 5: Regulatory landscapes are changing rapidly, requiring businesses to stay proactive on compliance and... (rank: 0.428)
INFO DEBUG: Built memory context with 5 memories
INFO Context switch detection: is_switch=False, confidence=0.00, domain=None
INFO DEBUG: Conversation context prepared:
INFO   - Has memory context: True
INFO   - Recurring topics: ['codebase_analysis', 'AI videos', 'Deployment logs', 'Agent deployments', 'image_generation']
INFO   - Memory context preview: Based on our previous conversations:

[July 10]: The system has completed multiple agent deployments recently, including Research, Business, and Technical Chart Agents, indicating active development a...
INFO DEBUG: Checked for data requests (emotional support not needed): []
WARNING Intelligent prompting failed, using fallback: 'IntelligentPromptService' object has no attribute 'select_optimal_prompt'
INFO CRITICAL DEBUG: generate_contextual_response called
INFO User input: Are you able to evolve anymore?...
INFO Memory context available: True
INFO Revolutionary prompt selected: Default System Prompt
INFO Memory context content: Based on our previous conversations:

[July 10]: The system has completed multiple agent deployments recently, including Research, Business, and Technical Chart Agents, indicating active development a...
INFO 🧠 Using intelligent prompt: Default System Prompt (confidence: 0.50)
INFO FINAL SYSTEM PROMPT PREVIEW: You are a Personal AI Assistant dedicated to helping users achieve their life goals and aspirations.

Your mission is to understand, adapt, and support users in their personal growth journey, whether that's:
- Building businesses and pursuing entrepreneurial dreams
- Career advancement and professional development
- Personal development and self-improvement
- Creative projects and artistic endeavors
- Life planning and goal achievement

Key capabilities:
- Deploy AI agents from the 21-agent work...
INFO Selected openai/gpt-4.1-nano for task 'chat'
INFO Selected openai/gpt-4.1-nano for chat
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO AI RESPONSE (openai/gpt-4.1-nano): Yes, I continuously evolve by integrating new data, refining my understanding of your goals, and dep...
INFO DEBUG: Response before cleaning: Yes, I continuously evolve by integrating new data, refining my understanding of your goals, and dep...
INFO DEBUG: Response after cleaning: Yes, I continuously evolve by integrating new data, refining my understanding of your goals, and dep...
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO 🧠 Revolutionary Intelligent Prompting enabled for user 2
INFO Selected openai/gpt-4.1 for task 'analysis'
INFO Selected openai/gpt-4.1 for analysis
127.0.0.1:50442 - - [10/Jul/2025:17:42:19] "WSDISCONNECT /ws/dashboard-stats/" - -
INFO User 2 disconnected from dashboard stats WebSocket
127.0.0.1:50476 - - [10/Jul/2025:17:42:20] "WSCONNECTING /ws/dashboard-stats/" - -
INFO WebSocket authenticated user: testuser
127.0.0.1:50476 - - [10/Jul/2025:17:42:20] "WSCONNECT /ws/dashboard-stats/" - -
INFO User 2 connected to dashboard stats WebSocket
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Created 1 embeddings for conversation 4067
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Saved conversation to Memory Palace: AI's Continuous Evolution Enhances User Support
INFO Conversation saved to Memory Palace for learning continuity
127.0.0.1:50423 - - [10/Jul/2025:17:42:28] "POST /api/ai-partner/chat/" 200 1571
127.0.0.1:50423 - - [10/Jul/2025:17:42:49] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50423 - - [10/Jul/2025:17:42:55] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50421 - - [10/Jul/2025:17:42:59] "OPTIONS /api/ai-partner/memory/search/?query=Could+you+repeat+your+last+answer&limit=3" 200 -
INFO Memory search request: user=2, query='Could you repeat your last answer...'
INFO 🔍 DEBUG MemoryRetrieval: Starting search for user 2, query: 'Could you repeat your last answer...'
127.0.0.1:50435 - - [10/Jul/2025:17:43:00] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO 🧠 DEBUG: Generated query embedding (dim: 1536)
INFO 📊 DEBUG: Vector search returned 6 results
INFO 🎯 DEBUG: Top 5 similarity scores: [0.3968474680508962, 0.3351730506173807, 0.3278037739969857, 0.32702388272047744, 0.3269921438093417]
INFO ⚠️  DEBUG: Using threshold 0.7, but scores are: min=0.3270, max=0.3968
INFO ✅ DEBUG: Returning 0 memory contexts
127.0.0.1:50423 - - [10/Jul/2025:17:43:01] "GET /api/ai-partner/memory/search/?query=Could+you+repeat+your+last+answer&limit=3" 200 69
INFO DEBUG: Personal AI chat request - User: testuser, Message: Could you repeat your last answer...
INFO DEBUG: include_memories = True, context_type = general, device_type = web
WARNING Session handling error (likely test context): get() returned more than one ConversationSession -- it returned more than 20!
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO 🧠 Revolutionary Intelligent Prompting enabled for user 2
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Using EnhancedMemoryService with extracted vector intelligence
INFO DEBUG: Starting memory retrieval for user 2
INFO DEBUG: Searching memories with query: 'Could you repeat your last answer...'
INFO Using EXTRACTED enhanced memory search with multi-factor ranking
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Trying fixed memory search for MemoryEntry model
INFO Found 111 memories with embeddings for user 2
INFO Fixed memory search returned 10 results
INFO DEBUG: Found 10 raw memories
INFO 🎯 Ranking 10 memories for query: 'Could you repeat your last answer...'
INFO 📊 Top ranked memory scores:
INFO   1. Total: 0.530 | Recency: 1.00 | Relevance: 0.23 | Continuity: 0.30
INFO   2. Total: 0.483 | Recency: 1.00 | Relevance: 0.21 | Continuity: 0.00
INFO   3. Total: 0.462 | Recency: 1.00 | Relevance: 0.23 | Continuity: 0.00
INFO DEBUG: Selected 5 top-ranked memories
INFO   Memory 1: The user expressed a strong command to halt agent deployments and questioned the existence of the 66... (rank: 0.530)
INFO   Memory 2: The user inquired about recalling a previous discussion related to 341 deployments, indicating an in... (rank: 0.483)
INFO   Memory 3: The AI reaffirmed its commitment to remember and prioritize verified facts about deployments, ensuri... (rank: 0.462)
INFO   Memory 4: The conversation highlights the AI's commitment to accuracy by retrieving deployment details directl... (rank: 0.449)
INFO   Memory 5: In the conversation, the AI initially claimed it couldn't access memories from June 28, 2025, citing... (rank: 0.440)
INFO DEBUG: Built memory context with 5 memories
INFO Context switch detection: is_switch=False, confidence=0.00, domain=None
INFO DEBUG: Conversation context prepared:
INFO   - Has memory context: True
INFO   - Recurring topics: ['codebase_analysis', 'AI videos', 'Deployment logs', 'Agent deployments', 'image_generation']
INFO   - Memory context preview: Based on our previous conversations:

[July 10]: The user expressed a strong command to halt agent deployments and questioned the existence of the 666 deployments, seeking reassurance about their real...
INFO DEBUG: Checked for data requests (emotional support not needed): []
WARNING Intelligent prompting failed, using fallback: 'IntelligentPromptService' object has no attribute 'select_optimal_prompt'
INFO CRITICAL DEBUG: generate_contextual_response called
INFO User input: Could you repeat your last answer...
INFO Memory context available: True
INFO Revolutionary prompt selected: Default System Prompt
INFO Memory context content: Based on our previous conversations:

[July 10]: The user expressed a strong command to halt agent deployments and questioned the existence of the 666 deployments, seeking reassurance about their real...
INFO 🧠 Using intelligent prompt: Default System Prompt (confidence: 0.50)
INFO FINAL SYSTEM PROMPT PREVIEW: You are a Personal AI Assistant dedicated to helping users achieve their life goals and aspirations.

Your mission is to understand, adapt, and support users in their personal growth journey, whether that's:
- Building businesses and pursuing entrepreneurial dreams
- Career advancement and professional development
- Personal development and self-improvement
- Creative projects and artistic endeavors
- Life planning and goal achievement

Key capabilities:
- Deploy AI agents from the 21-agent work...
INFO Selected openai/gpt-4.1-nano for task 'chat'
INFO Selected openai/gpt-4.1-nano for chat
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO AI RESPONSE (openai/gpt-4.1-nano): Certainly. Please specify which part you'd like me to repeat or clarify, and I'll provide the exact ...
INFO DEBUG: Response before cleaning: Certainly. Please specify which part you'd like me to repeat or clarify, and I'll provide the exact ...
INFO DEBUG: Response after cleaning: Certainly. Please specify which part you'd like me to repeat or clarify, and I'll provide the exact ...
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO 🧠 Revolutionary Intelligent Prompting enabled for user 2
INFO Selected openai/gpt-4.1 for task 'analysis'
INFO Selected openai/gpt-4.1 for analysis
127.0.0.1:50435 - - [10/Jul/2025:17:43:05] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Created 1 embeddings for conversation 4069
INFO Conversation not memorable enough for Memory Palace
INFO Conversation not saved to Memory Palace (not memorable enough)
127.0.0.1:50423 - - [10/Jul/2025:17:43:06] "POST /api/ai-partner/chat/" 200 1423
127.0.0.1:50423 - - [10/Jul/2025:17:43:10] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50423 - - [10/Jul/2025:17:43:16] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50423 - - [10/Jul/2025:17:43:21] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50421 - - [10/Jul/2025:17:43:26] "OPTIONS /api/ai-partner/memory/search/?query=Are+you+able+to+evolve%3F&limit=3" 200 -
INFO Memory search request: user=2, query='Are you able to evolve?...'
INFO 🔍 DEBUG MemoryRetrieval: Starting search for user 2, query: 'Are you able to evolve?...'
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO 🧠 DEBUG: Generated query embedding (dim: 1536)
INFO 📊 DEBUG: Vector search returned 6 results
INFO 🎯 DEBUG: Top 5 similarity scores: [0.6422906861956843, 0.5904252830339697, 0.46931368112569416, 0.4503203212069349, 0.4396958232832552]
INFO ⚠️  DEBUG: Using threshold 0.7, but scores are: min=0.4397, max=0.6423
INFO ✅ DEBUG: Returning 0 memory contexts
127.0.0.1:50423 - - [10/Jul/2025:17:43:26] "GET /api/ai-partner/memory/search/?query=Are+you+able+to+evolve%3F&limit=3" 200 59
INFO DEBUG: Personal AI chat request - User: testuser, Message: Are you able to evolve?...
INFO DEBUG: include_memories = True, context_type = general, device_type = web
WARNING Session handling error (likely test context): get() returned more than one ConversationSession -- it returned more than 20!
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO 🧠 Revolutionary Intelligent Prompting enabled for user 2
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Using EnhancedMemoryService with extracted vector intelligence
INFO DEBUG: Starting memory retrieval for user 2
INFO DEBUG: Searching memories with query: 'Are you able to evolve?...'
INFO Using EXTRACTED enhanced memory search with multi-factor ranking
127.0.0.1:50435 - - [10/Jul/2025:17:43:27] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Trying fixed memory search for MemoryEntry model
INFO Found 111 memories with embeddings for user 2
INFO Fixed memory search returned 10 results
INFO DEBUG: Found 10 raw memories
INFO 🎯 Ranking 10 memories for query: 'Are you able to evolve?...'
INFO 📊 Top ranked memory scores:
INFO   1. Total: 0.513 | Recency: 1.00 | Relevance: 0.36 | Continuity: 0.00
INFO   2. Total: 0.500 | Recency: 1.00 | Relevance: 0.15 | Continuity: 0.30
INFO   3. Total: 0.453 | Recency: 1.00 | Relevance: 0.18 | Continuity: 0.00
INFO DEBUG: Selected 5 top-ranked memories
INFO   Memory 1: The conversation highlights that AI systems, including myself, continuously evolve by integrating ne... (rank: 0.513)
INFO   Memory 2: The user expressed a strong command to halt agent deployments and questioned the existence of the 66... (rank: 0.500)
INFO   Memory 3: In this conversation, the AI accurately states that the current year is 2025, demonstrating its abil... (rank: 0.453)
INFO   Memory 4: AI and machine learning have significantly advanced in 2025, transforming software development with ... (rank: 0.446)
INFO   Memory 5: The user inquired whether the recurring issue offering 'research papers' and 'packages' was connecte... (rank: 0.431)
INFO DEBUG: Built memory context with 5 memories
INFO Context switch detection: is_switch=False, confidence=0.00, domain=None
INFO DEBUG: Conversation context prepared:
INFO   - Has memory context: True
INFO   - Recurring topics: ['codebase_analysis', 'AI videos', 'Deployment logs', 'Agent deployments', 'image_generation']
INFO   - Memory context preview: Based on our previous conversations:

[July 10]: The conversation highlights that AI systems, including myself, continuously evolve by integrating new data and refining understanding to better support...
INFO DEBUG: Checked for data requests (emotional support not needed): []
WARNING Intelligent prompting failed, using fallback: 'IntelligentPromptService' object has no attribute 'select_optimal_prompt'
INFO CRITICAL DEBUG: generate_contextual_response called
INFO User input: Are you able to evolve?...
INFO Memory context available: True
INFO Revolutionary prompt selected: Default System Prompt
INFO Memory context content: Based on our previous conversations:

[July 10]: The conversation highlights that AI systems, including myself, continuously evolve by integrating new data and refining understanding to better support...
INFO 🧠 Using intelligent prompt: Default System Prompt (confidence: 0.50)
INFO FINAL SYSTEM PROMPT PREVIEW: You are a Personal AI Assistant dedicated to helping users achieve their life goals and aspirations.

Your mission is to understand, adapt, and support users in their personal growth journey, whether that's:
- Building businesses and pursuing entrepreneurial dreams
- Career advancement and professional development
- Personal development and self-improvement
- Creative projects and artistic endeavors
- Life planning and goal achievement

Key capabilities:
- Deploy AI agents from the 21-agent work...
INFO Selected openai/gpt-4.1-nano for task 'chat'
INFO Selected openai/gpt-4.1-nano for chat
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO AI RESPONSE (openai/gpt-4.1-nano): Yes, I continuously evolve by integrating new data, refining my understanding, and adapting to your ...
INFO DEBUG: Response before cleaning: Yes, I continuously evolve by integrating new data, refining my understanding, and adapting to your ...
INFO DEBUG: Response after cleaning: Yes, I continuously evolve by integrating new data, refining my understanding, and adapting to your ...
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO 🧠 Revolutionary Intelligent Prompting enabled for user 2
INFO Selected openai/gpt-4.1 for task 'analysis'
INFO Selected openai/gpt-4.1 for analysis
127.0.0.1:50435 - - [10/Jul/2025:17:43:32] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:43:37] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Created 1 embeddings for conversation 4071
127.0.0.1:50435 - - [10/Jul/2025:17:43:43] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Saved conversation to Memory Palace: AI's Continuous Evolution Enhances Personalization
INFO Conversation saved to Memory Palace for learning continuity
127.0.0.1:50423 - - [10/Jul/2025:17:43:44] "POST /api/ai-partner/chat/" 200 1508
127.0.0.1:50423 - - [10/Jul/2025:17:43:48] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50423 - - [10/Jul/2025:17:43:53] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50423 - - [10/Jul/2025:17:43:59] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50423 - - [10/Jul/2025:17:44:04] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50423 - - [10/Jul/2025:17:44:10] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50421 - - [10/Jul/2025:17:44:13] "OPTIONS /api/ai-partner/memory/search/?query=What+makes+you+able+to+evolve%3F&limit=3" 200 -
INFO Memory search request: user=2, query='What makes you able to evolve?...'
INFO 🔍 DEBUG MemoryRetrieval: Starting search for user 2, query: 'What makes you able to evolve?...'
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO 🧠 DEBUG: Generated query embedding (dim: 1536)
INFO 📊 DEBUG: Vector search returned 6 results
INFO 🎯 DEBUG: Top 5 similarity scores: [0.6230385986909528, 0.6052204480373585, 0.5579532566404931, 0.47599500560797114, 0.4752799434614561]
INFO ⚠️  DEBUG: Using threshold 0.7, but scores are: min=0.4753, max=0.6230
INFO ✅ DEBUG: Returning 0 memory contexts
127.0.0.1:50423 - - [10/Jul/2025:17:44:14] "GET /api/ai-partner/memory/search/?query=What+makes+you+able+to+evolve%3F&limit=3" 200 66
INFO DEBUG: Personal AI chat request - User: testuser, Message: What makes you able to evolve?...
INFO DEBUG: include_memories = True, context_type = general, device_type = web
WARNING Session handling error (likely test context): get() returned more than one ConversationSession -- it returned more than 20!
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO 🧠 Revolutionary Intelligent Prompting enabled for user 2
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Using EnhancedMemoryService with extracted vector intelligence
INFO DEBUG: Starting memory retrieval for user 2
INFO DEBUG: Searching memories with query: 'What makes you able to evolve?...'
INFO Using EXTRACTED enhanced memory search with multi-factor ranking
127.0.0.1:50435 - - [10/Jul/2025:17:44:15] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Trying fixed memory search for MemoryEntry model
INFO Found 112 memories with embeddings for user 2
INFO Fixed memory search returned 10 results
INFO DEBUG: Found 10 raw memories
INFO 🎯 Ranking 10 memories for query: 'What makes you able to evolve?...'
INFO 📊 Top ranked memory scores:
INFO   1. Total: 0.539 | Recency: 1.00 | Relevance: 0.42 | Continuity: 0.00
INFO   2. Total: 0.462 | Recency: 1.00 | Relevance: 0.20 | Continuity: 0.00
INFO   3. Total: 0.446 | Recency: 1.00 | Relevance: 0.19 | Continuity: 0.00
INFO DEBUG: Selected 5 top-ranked memories
INFO   Memory 1: The conversation highlights that AI systems, including myself, continuously evolve by integrating ne... (rank: 0.539)
INFO   Memory 2: The key insight from the conversation is that to make Donkey Betz appealing to major tech companies ... (rank: 0.462)
INFO   Memory 3: AI and machine learning have significantly advanced in 2025, transforming software development with ... (rank: 0.446)
INFO   Memory 4: The conversation highlights that the AI's tendency to generate fictional content or deployments, suc... (rank: 0.442)
INFO   Memory 5: The user inquired whether the recurring issue offering 'research papers' and 'packages' was connecte... (rank: 0.438)
INFO DEBUG: Built memory context with 5 memories
INFO Context switch detection: is_switch=False, confidence=0.00, domain=None
INFO DEBUG: Conversation context prepared:
INFO   - Has memory context: True
INFO   - Recurring topics: ['codebase_analysis', 'AI videos', 'Deployment logs', 'AI evolution', 'Agent deployments']
INFO   - Memory context preview: Based on our previous conversations:

[July 10]: The conversation highlights that AI systems, including myself, continuously evolve by integrating new data and refining understanding to better support...
INFO DEBUG: Checked for data requests (emotional support not needed): []
WARNING Intelligent prompting failed, using fallback: 'IntelligentPromptService' object has no attribute 'select_optimal_prompt'
INFO CRITICAL DEBUG: generate_contextual_response called
INFO User input: What makes you able to evolve?...
INFO Memory context available: True
INFO Revolutionary prompt selected: Default System Prompt
INFO Memory context content: Based on our previous conversations:

[July 10]: The conversation highlights that AI systems, including myself, continuously evolve by integrating new data and refining understanding to better support...
INFO 🧠 Using intelligent prompt: Default System Prompt (confidence: 0.50)
INFO FINAL SYSTEM PROMPT PREVIEW: You are a Personal AI Assistant dedicated to helping users achieve their life goals and aspirations.

Your mission is to understand, adapt, and support users in their personal growth journey, whether that's:
- Building businesses and pursuing entrepreneurial dreams
- Career advancement and professional development
- Personal development and self-improvement
- Creative projects and artistic endeavors
- Life planning and goal achievement

Key capabilities:
- Deploy AI agents from the 21-agent work...
INFO Selected openai/gpt-4.1-nano for task 'chat'
INFO Selected openai/gpt-4.1-nano for chat
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO AI RESPONSE (openai/gpt-4.1-nano): My ability to evolve comes from continuous integration of new data, advanced learning algorithms, an...
INFO DEBUG: Response before cleaning: My ability to evolve comes from continuous integration of new data, advanced learning algorithms, an...
INFO DEBUG: Response after cleaning: My ability to evolve comes from continuous integration of new data, advanced learning algorithms, an...
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO 🧠 Revolutionary Intelligent Prompting enabled for user 2
INFO Selected openai/gpt-4.1 for task 'analysis'
INFO Selected openai/gpt-4.1 for analysis
127.0.0.1:50435 - - [10/Jul/2025:17:44:20] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Created 1 embeddings for conversation 4073
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Saved conversation to Memory Palace: AI's Evolving Capabilities Driven by Continuous Learning
INFO Conversation saved to Memory Palace for learning continuity
127.0.0.1:50423 - - [10/Jul/2025:17:44:26] "POST /api/ai-partner/chat/" 200 1595
127.0.0.1:50435 - - [10/Jul/2025:17:44:26] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:44:31] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:44:36] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:44:42] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:44:47] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50421 - - [10/Jul/2025:17:44:51] "OPTIONS /api/ai-partner/memory/search/?query=What+are+my+goals%3F&limit=3" 200 -
INFO Memory search request: user=2, query='What are my goals?...'
INFO 🔍 DEBUG MemoryRetrieval: Starting search for user 2, query: 'What are my goals?...'
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO 🧠 DEBUG: Generated query embedding (dim: 1536)
INFO 📊 DEBUG: Vector search returned 6 results
INFO 🎯 DEBUG: Top 5 similarity scores: [0.4193030105360056, 0.3979322730878816, 0.3979322730878816, 0.39337492384023576, 0.38648627013788905]
INFO ⚠️  DEBUG: Using threshold 0.7, but scores are: min=0.3865, max=0.4193
INFO ✅ DEBUG: Returning 0 memory contexts
127.0.0.1:50435 - - [10/Jul/2025:17:44:52] "GET /api/ai-partner/memory/search/?query=What+are+my+goals%3F&limit=3" 200 54
INFO DEBUG: Personal AI chat request - User: testuser, Message: What are my goals?...
INFO DEBUG: include_memories = True, context_type = general, device_type = web
WARNING Session handling error (likely test context): get() returned more than one ConversationSession -- it returned more than 20!
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO 🧠 Revolutionary Intelligent Prompting enabled for user 2
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Using EnhancedMemoryService with extracted vector intelligence
INFO DEBUG: Starting memory retrieval for user 2
INFO DEBUG: Searching memories with query: 'What are my goals?...'
INFO Using EXTRACTED enhanced memory search with multi-factor ranking
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Trying fixed memory search for MemoryEntry model
INFO Found 113 memories with embeddings for user 2
INFO Fixed memory search returned 10 results
INFO DEBUG: Found 10 raw memories
INFO 🎯 Ranking 10 memories for query: 'What are my goals?...'
INFO 📊 Top ranked memory scores:
INFO   1. Total: 0.486 | Recency: 1.00 | Relevance: 0.19 | Continuity: 0.30
INFO   2. Total: 0.462 | Recency: 1.00 | Relevance: 0.23 | Continuity: 0.00
INFO   3. Total: 0.456 | Recency: 1.00 | Relevance: 0.22 | Continuity: 0.00
INFO DEBUG: Selected 5 top-ranked memories
INFO   Memory 1: The system has completed multiple agent deployments recently, including Research, Business, and Tech... (rank: 0.486)
INFO   Memory 2: The AI reaffirmed its commitment to remember and prioritize verified facts about deployments, ensuri... (rank: 0.462)
INFO   Memory 3: The conversation highlights that AI systems, including myself, continuously evolve by integrating ne... (rank: 0.456)
INFO   Memory 4: This conversation highlights that the original vision for Donkey Betz was to create an AI-powered sp... (rank: 0.455)
INFO   Memory 5: The conversation highlights that AI cannot access or retrieve memories or data beyond its knowledge ... (rank: 0.441)
INFO DEBUG: Built memory context with 5 memories
INFO Context switch detection: is_switch=False, confidence=0.00, domain=None
INFO DEBUG: Conversation context prepared:
INFO   - Has memory context: True
INFO   - Recurring topics: ['codebase_analysis', 'AI videos', 'AI evolution', 'Deployment logs', 'Agent deployments']
INFO   - Memory context preview: Based on our previous conversations:

[July 10]: The system has completed multiple agent deployments recently, including Research, Business, and Technical Chart Agents, indicating active development a...
INFO DEBUG: Checked for data requests (emotional support not needed): []
WARNING Intelligent prompting failed, using fallback: 'IntelligentPromptService' object has no attribute 'select_optimal_prompt'
127.0.0.1:50423 - - [10/Jul/2025:17:44:52] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
INFO CRITICAL DEBUG: generate_contextual_response called
INFO User input: What are my goals?...
INFO Memory context available: True
INFO Revolutionary prompt selected: Default System Prompt
INFO Memory context content: Based on our previous conversations:

[July 10]: The system has completed multiple agent deployments recently, including Research, Business, and Technical Chart Agents, indicating active development a...
INFO 🧠 Using intelligent prompt: Default System Prompt (confidence: 0.50)
INFO FINAL SYSTEM PROMPT PREVIEW: You are a Personal AI Assistant dedicated to helping users achieve their life goals and aspirations.

Your mission is to understand, adapt, and support users in their personal growth journey, whether that's:
- Building businesses and pursuing entrepreneurial dreams
- Career advancement and professional development
- Personal development and self-improvement
- Creative projects and artistic endeavors
- Life planning and goal achievement

Key capabilities:
- Deploy AI agents from the 21-agent work...
INFO Selected openai/gpt-4.1-nano for task 'chat'
INFO Selected openai/gpt-4.1-nano for chat
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO AI RESPONSE (openai/gpt-4.1-nano): Your current focus isn't explicitly listed, but based on our previous discussions, you're interested...
INFO DEBUG: Response before cleaning: Your current focus isn't explicitly listed, but based on our previous discussions, you're interested...
INFO DEBUG: Response after cleaning: Your current focus isn't explicitly listed, but based on our previous discussions, you're interested...
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO 🧠 Revolutionary Intelligent Prompting enabled for user 2
INFO Selected openai/gpt-4.1 for task 'analysis'
INFO Selected openai/gpt-4.1 for analysis
127.0.0.1:50423 - - [10/Jul/2025:17:44:58] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Created 1 embeddings for conversation 4075
127.0.0.1:50423 - - [10/Jul/2025:17:45:03] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Saved conversation to Memory Palace: Clarification of User's Goals and Focus Areas
INFO Conversation saved to Memory Palace for learning continuity
127.0.0.1:50435 - - [10/Jul/2025:17:45:07] "POST /api/ai-partner/chat/" 200 1607
127.0.0.1:50435 - - [10/Jul/2025:17:45:19] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:45:24] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:45:29] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:45:34] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:45:40] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:45:45] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:45:51] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:45:56] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:46:01] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:46:06] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:46:12] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:46:17] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:46:23] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:46:28] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:46:33] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:46:39] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:46:44] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:46:49] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:46:55] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:47:00] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:47:05] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:47:11] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50951 - - [10/Jul/2025:17:47:14] "OPTIONS /api/ai-partner/memory/search/?query=Can+you+recall+what+the+original+purpose+of+Donkey+Betz+was%3F&limit=3" 200 -
INFO Memory search request: user=2, query='Can you recall what the original purpose of Donkey...'
INFO 🔍 DEBUG MemoryRetrieval: Starting search for user 2, query: 'Can you recall what the original purpose of Donkey...'
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO 🧠 DEBUG: Generated query embedding (dim: 1536)
INFO 📊 DEBUG: Vector search returned 6 results
INFO 🎯 DEBUG: Top 5 similarity scores: [0.5103339121243247, 0.4934487931071282, 0.4650237518577288, 0.46188387047552293, 0.45101030316918367]
INFO ⚠️  DEBUG: Using threshold 0.7, but scores are: min=0.4510, max=0.5103
INFO ✅ DEBUG: Returning 0 memory contexts
127.0.0.1:50435 - - [10/Jul/2025:17:47:15] "GET /api/ai-partner/memory/search/?query=Can+you+recall+what+the+original+purpose+of+Donkey+Betz+was%3F&limit=3" 200 96
INFO DEBUG: Personal AI chat request - User: testuser, Message: Can you recall what the original purpose of Donkey...
INFO DEBUG: include_memories = True, context_type = general, device_type = web
WARNING Session handling error (likely test context): get() returned more than one ConversationSession -- it returned more than 20!
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO 🧠 Revolutionary Intelligent Prompting enabled for user 2
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Using EnhancedMemoryService with extracted vector intelligence
INFO DEBUG: Starting memory retrieval for user 2
INFO DEBUG: Searching memories with query: 'Can you recall what the original purpose of Donkey...'
INFO Using EXTRACTED enhanced memory search with multi-factor ranking
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Trying fixed memory search for MemoryEntry model
INFO Found 114 memories with embeddings for user 2
INFO Fixed memory search returned 10 results
INFO DEBUG: Found 10 raw memories
INFO 🎯 Ranking 10 memories for query: 'Can you recall what the original purpose of Donkey...'
INFO 📊 Top ranked memory scores:
INFO   1. Total: 0.595 | Recency: 1.00 | Relevance: 0.61 | Continuity: 0.00
INFO   2. Total: 0.557 | Recency: 1.00 | Relevance: 0.44 | Continuity: 0.00
INFO   3. Total: 0.490 | Recency: 1.00 | Relevance: 0.22 | Continuity: 0.00
INFO DEBUG: Selected 5 top-ranked memories
INFO   Memory 1: This conversation highlights that the original vision for Donkey Betz was to create an AI-powered sp... (rank: 0.595)
INFO   Memory 2: The key insight from the conversation is that to make Donkey Betz appealing to major tech companies ... (rank: 0.557)
INFO   Memory 3: The user inquired about recalling a previous discussion related to 341 deployments, indicating an in... (rank: 0.490)
INFO   Memory 4: The conversation highlights the importance of verifying deployment logs to prevent mislabeling or da... (rank: 0.488)
INFO   Memory 5: The conversation clarified that the initial deployment was the launch of our core infrastructure, wh... (rank: 0.446)
INFO DEBUG: Built memory context with 5 memories
INFO Context switch detection: is_switch=False, confidence=0.00, domain=None
INFO DEBUG: Conversation context prepared:
INFO   - Has memory context: True
INFO   - Recurring topics: ['codebase_analysis', 'AI videos', 'AI evolution', 'Deployment logs', 'Agent deployments']
INFO   - Memory context preview: Based on our previous conversations:

[July 10]: This conversation highlights that the original vision for Donkey Betz was to create an AI-powered sports betting platform with advanced features like r...
INFO DEBUG: Checked for data requests (emotional support not needed): []
WARNING Intelligent prompting failed, using fallback: 'IntelligentPromptService' object has no attribute 'select_optimal_prompt'
127.0.0.1:50962 - - [10/Jul/2025:17:47:16] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
INFO CRITICAL DEBUG: generate_contextual_response called
INFO User input: Can you recall what the original purpose of Donkey Betz was?...
INFO Memory context available: True
INFO Revolutionary prompt selected: Default System Prompt
INFO Memory context content: Based on our previous conversations:

[July 10]: This conversation highlights that the original vision for Donkey Betz was to create an AI-powered sports betting platform with advanced features like r...
INFO 🧠 Using intelligent prompt: Default System Prompt (confidence: 0.50)
INFO FINAL SYSTEM PROMPT PREVIEW: You are a Personal AI Assistant dedicated to helping users achieve their life goals and aspirations.

Your mission is to understand, adapt, and support users in their personal growth journey, whether that's:
- Building businesses and pursuing entrepreneurial dreams
- Career advancement and professional development
- Personal development and self-improvement
- Creative projects and artistic endeavors
- Life planning and goal achievement

Key capabilities:
- Deploy AI agents from the 21-agent work...
INFO Selected openai/gpt-4.1-nano for task 'chat'
INFO Selected openai/gpt-4.1-nano for chat
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO AI RESPONSE (openai/gpt-4.1-nano): The original purpose of Donkey Betz was to create an AI-powered sports betting platform with advance...
INFO DEBUG: Response before cleaning: The original purpose of Donkey Betz was to create an AI-powered sports betting platform with advance...
INFO DEBUG: Response after cleaning: The original purpose of Donkey Betz was to create an AI-powered sports betting platform with advance...
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO 🧠 Revolutionary Intelligent Prompting enabled for user 2
INFO Selected openai/gpt-4.1 for task 'analysis'
INFO Selected openai/gpt-4.1 for analysis
127.0.0.1:50962 - - [10/Jul/2025:17:47:21] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Created 1 embeddings for conversation 4077
127.0.0.1:50962 - - [10/Jul/2025:17:47:27] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Saved conversation to Memory Palace: Purpose of Donkey Betz as an AI Sports Betting Platform
INFO Conversation saved to Memory Palace for learning continuity
127.0.0.1:50435 - - [10/Jul/2025:17:47:29] "POST /api/ai-partner/chat/" 200 1652
127.0.0.1:50435 - - [10/Jul/2025:17:47:32] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:47:37] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:47:43] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:47:48] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:47:53] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:47:59] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:48:09] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:48:14] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:48:20] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:48:25] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:48:30] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:48:36] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:48:41] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:48:46] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:48:52] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:48:57] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:49:02] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:49:58] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:50:03] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:50:09] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:50:14] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:50:19] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:50:25] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:50:30] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:50:35] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:51268 - - [10/Jul/2025:17:50:40] "OPTIONS /api/ai-partner/memory/search/?query=Can+you+give+me+details+from+the+341+deployment+planning+discussions%3F&limit=3" 200 -
INFO Memory search request: user=2, query='Can you give me details from the 341 deployment pl...'
INFO 🔍 DEBUG MemoryRetrieval: Starting search for user 2, query: 'Can you give me details from the 341 deployment pl...'
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO 🧠 DEBUG: Generated query embedding (dim: 1536)
INFO 📊 DEBUG: Vector search returned 6 results
INFO 🎯 DEBUG: Top 5 similarity scores: [0.5868146833489909, 0.5681222941548351, 0.5350546969914175, 0.5115738635952818, 0.5080880248808934]
INFO ⚠️  DEBUG: Using threshold 0.7, but scores are: min=0.5081, max=0.5868
INFO ✅ DEBUG: Returning 0 memory contexts
127.0.0.1:50435 - - [10/Jul/2025:17:50:40] "GET /api/ai-partner/memory/search/?query=Can+you+give+me+details+from+the+341+deployment+planning+discussions%3F&limit=3" 200 105
INFO DEBUG: Personal AI chat request - User: testuser, Message: Can you give me details from the 341 deployment pl...
INFO DEBUG: include_memories = True, context_type = general, device_type = web
WARNING Session handling error (likely test context): get() returned more than one ConversationSession -- it returned more than 20!
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO 🧠 Revolutionary Intelligent Prompting enabled for user 2
127.0.0.1:51274 - - [10/Jul/2025:17:50:41] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Using EnhancedMemoryService with extracted vector intelligence
INFO DEBUG: Starting memory retrieval for user 2
INFO DEBUG: Searching memories with query: 'Can you give me details from the 341 deployment pl...'
INFO Using EXTRACTED enhanced memory search with multi-factor ranking
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Trying fixed memory search for MemoryEntry model
INFO Found 115 memories with embeddings for user 2
INFO Fixed memory search returned 10 results
INFO DEBUG: Found 10 raw memories
INFO 🎯 Ranking 10 memories for query: 'Can you give me details from the 341 deployment pl...'
INFO 📊 Top ranked memory scores:
INFO   1. Total: 0.605 | Recency: 1.00 | Relevance: 0.51 | Continuity: 0.00
INFO   2. Total: 0.585 | Recency: 1.00 | Relevance: 0.39 | Continuity: 0.30
INFO   3. Total: 0.581 | Recency: 1.00 | Relevance: 0.58 | Continuity: 0.00
INFO DEBUG: Selected 5 top-ranked memories
INFO   Memory 1: The user inquired about recalling a previous discussion related to 341 deployments, indicating an in... (rank: 0.605)
INFO   Memory 2: The conversation highlights the importance of verifying deployment logs to prevent mislabeling or da... (rank: 0.585)
INFO   Memory 3: During the conversations spanning 2023-2024, a significant milestone was the planning of 341 deploym... (rank: 0.581)
INFO   Memory 4: The deployment #345 occurred at 09:45 UTC, which was early morning local time (4:45 AM) for the user... (rank: 0.572)
INFO   Memory 5: The conversation clarified that the initial deployment was the launch of our core infrastructure, wh... (rank: 0.542)
INFO DEBUG: Built memory context with 5 memories
INFO Context switch detection: is_switch=False, confidence=0.00, domain=coding
INFO DEBUG: Conversation context prepared:
INFO   - Has memory context: True
INFO   - Recurring topics: ['codebase_analysis', 'AI videos', 'AI evolution', 'Deployment logs', 'Agent deployments']
INFO   - Memory context preview: Based on our previous conversations:

[July 10]: The user inquired about recalling a previous discussion related to 341 deployments, indicating an intent to utilize past chat insights for planning the...
INFO DEBUG: Checked for data requests (emotional support not needed): []
WARNING Intelligent prompting failed, using fallback: 'IntelligentPromptService' object has no attribute 'select_optimal_prompt'
INFO CRITICAL DEBUG: generate_contextual_response called
INFO User input: Can you give me details from the 341 deployment planning discussions?...
INFO Memory context available: True
INFO Revolutionary prompt selected: Default System Prompt
INFO Memory context content: Based on our previous conversations:

[July 10]: The user inquired about recalling a previous discussion related to 341 deployments, indicating an intent to utilize past chat insights for planning the...
INFO 🧠 Using intelligent prompt: Default System Prompt (confidence: 0.50)
INFO FINAL SYSTEM PROMPT PREVIEW: You are a Personal AI Assistant dedicated to helping users achieve their life goals and aspirations.

Your mission is to understand, adapt, and support users in their personal growth journey, whether that's:
- Building businesses and pursuing entrepreneurial dreams
- Career advancement and professional development
- Personal development and self-improvement
- Creative projects and artistic endeavors
- Life planning and goal achievement

Key capabilities:
- Deploy AI agents from the 21-agent work...
INFO Selected openai/gpt-4.1-nano for task 'chat'
INFO Selected openai/gpt-4.1-nano for chat
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO AI RESPONSE (openai/gpt-4.1-nano): Certainly. The planning of deployment #341 focused on system architecture and automation, aiming to ...
INFO DEBUG: Response before cleaning: Certainly. The planning of deployment #341 focused on system architecture and automation, aiming to ...
INFO DEBUG: Response after cleaning: Certainly. The planning of deployment #341 focused on system architecture and automation, aiming to ...
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO 🧠 Revolutionary Intelligent Prompting enabled for user 2
INFO Selected openai/gpt-4.1 for task 'analysis'
INFO Selected openai/gpt-4.1 for analysis
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Created 1 embeddings for conversation 4079
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Saved conversation to Memory Palace: Deployment #341 Focused on Robust System Architecture and Automation
INFO Conversation saved to Memory Palace for learning continuity
127.0.0.1:50435 - - [10/Jul/2025:17:50:55] "POST /api/ai-partner/chat/" 200 1679
127.0.0.1:50435 - - [10/Jul/2025:17:51:26] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:51:31] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:51:37] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:51:42] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:51:47] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:51:53] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:51:58] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:52:03] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:52:09] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638

127.0.0.1:50435 - - [10/Jul/2025:17:53:22] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:53:27] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:53:33] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:53:38] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:53:44] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:53:49] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:53:54] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:51643 - - [10/Jul/2025:17:53:55] "OPTIONS /api/ai-partner/memory/search/?query=Yes+can+you+give+me+details+about+deplyment+%23342%3F&limit=3" 200 -
INFO Memory search request: user=2, query='Yes can you give me details about deplyment #342?...'
INFO 🔍 DEBUG MemoryRetrieval: Starting search for user 2, query: 'Yes can you give me details about deplyment #342?...'
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO 🧠 DEBUG: Generated query embedding (dim: 1536)
INFO 📊 DEBUG: Vector search returned 6 results
INFO 🎯 DEBUG: Top 5 similarity scores: [0.5538944537765478, 0.5456690734531088, 0.521923021135439, 0.5044232881182898, 0.4519293394215105]
INFO ⚠️  DEBUG: Using threshold 0.7, but scores are: min=0.4519, max=0.5539
INFO ✅ DEBUG: Returning 0 memory contexts
127.0.0.1:50435 - - [10/Jul/2025:17:53:56] "GET /api/ai-partner/memory/search/?query=Yes+can+you+give+me+details+about+deplyment+%23342%3F&limit=3" 200 85
INFO DEBUG: Personal AI chat request - User: testuser, Message: Yes can you give me details about deplyment #342?...
INFO DEBUG: include_memories = True, context_type = general, device_type = web
WARNING Session handling error (likely test context): get() returned more than one ConversationSession -- it returned more than 20!
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO 🧠 Revolutionary Intelligent Prompting enabled for user 2
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Using EnhancedMemoryService with extracted vector intelligence
INFO DEBUG: Starting memory retrieval for user 2
INFO DEBUG: Searching memories with query: 'Yes can you give me details about deplyment #342?...'
INFO Using EXTRACTED enhanced memory search with multi-factor ranking
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Trying fixed memory search for MemoryEntry model
INFO Found 116 memories with embeddings for user 2
INFO Fixed memory search returned 10 results
INFO DEBUG: Found 10 raw memories
INFO 🎯 Ranking 10 memories for query: 'Yes can you give me details about deplyment #342?...'
INFO 📊 Top ranked memory scores:
INFO   1. Total: 0.570 | Recency: 1.00 | Relevance: 0.35 | Continuity: 0.30
INFO   2. Total: 0.549 | Recency: 1.00 | Relevance: 0.37 | Continuity: 0.00
INFO   3. Total: 0.542 | Recency: 1.00 | Relevance: 0.33 | Continuity: 0.30
INFO DEBUG: Selected 5 top-ranked memories
INFO   Memory 1: The conversation highlights the importance of verifying deployment logs to prevent mislabeling or da... (rank: 0.570)
INFO   Memory 2: The user inquired about recalling a previous discussion related to 341 deployments, indicating an in... (rank: 0.549)
INFO   Memory 3: The deployment #345 occurred at 09:45 UTC, which was early morning local time (4:45 AM) for the user... (rank: 0.542)
INFO   Memory 4: The user requested to verify the current status of deployments #346-#350, prompting the AI to deploy... (rank: 0.528)
INFO   Memory 5: The user requested logs for deployments #342, #343, #344, and #345. The AI responded by deploying an... (rank: 0.528)
INFO DEBUG: Built memory context with 5 memories
INFO Context switch detection: is_switch=False, confidence=0.00, domain=None
INFO DEBUG: Conversation context prepared:
INFO   - Has memory context: True
INFO   - Recurring topics: ['codebase_analysis', 'AI videos', 'AI evolution', 'Deployment logs', 'Agent deployments']
INFO   - Memory context preview: Based on our previous conversations:

[July 10]: The conversation highlights the importance of verifying deployment logs to prevent mislabeling or data mix-ups, as seen with deployment #343 being inco...
INFO DEBUG: Checked for data requests (emotional support not needed): []
WARNING Intelligent prompting failed, using fallback: 'IntelligentPromptService' object has no attribute 'select_optimal_prompt'
INFO CRITICAL DEBUG: generate_contextual_response called
INFO User input: Yes can you give me details about deplyment #342?...
INFO Memory context available: True
INFO Revolutionary prompt selected: Default System Prompt
INFO Memory context content: Based on our previous conversations:

[July 10]: The conversation highlights the importance of verifying deployment logs to prevent mislabeling or data mix-ups, as seen with deployment #343 being inco...
INFO 🧠 Using intelligent prompt: Default System Prompt (confidence: 0.50)
INFO FINAL SYSTEM PROMPT PREVIEW: You are a Personal AI Assistant dedicated to helping users achieve their life goals and aspirations.

Your mission is to understand, adapt, and support users in their personal growth journey, whether that's:
- Building businesses and pursuing entrepreneurial dreams
- Career advancement and professional development
- Personal development and self-improvement
- Creative projects and artistic endeavors
- Life planning and goal achievement

Key capabilities:
- Deploy AI agents from the 21-agent work...
INFO Selected openai/gpt-4.1-nano for task 'chat'
INFO Selected openai/gpt-4.1-nano for chat
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO AI RESPONSE (openai/gpt-4.1-nano): Deployment #342 occurred on July 10 at 07:30 UTC. It involved a database migration to improve system...
INFO DEBUG: Response before cleaning: Deployment #342 occurred on July 10 at 07:30 UTC. It involved a database migration to improve system...
INFO DEBUG: Response after cleaning: Deployment #342 occurred on July 10 at 07:30 UTC. It involved a database migration to improve system...
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO 🧠 Revolutionary Intelligent Prompting enabled for user 2
INFO Selected openai/gpt-4.1 for task 'analysis'
INFO Selected openai/gpt-4.1 for analysis
127.0.0.1:51658 - - [10/Jul/2025:17:54:00] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
127.0.0.1:51658 - - [10/Jul/2025:17:54:05] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Created 1 embeddings for conversation 4081
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Saved conversation to Memory Palace: Successful Database Migration in Deployment #342 Enhances System Stability
INFO Conversation saved to Memory Palace for learning continuity
127.0.0.1:50435 - - [10/Jul/2025:17:54:07] "POST /api/ai-partner/chat/" 200 1500
127.0.0.1:50435 - - [10/Jul/2025:17:54:10] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:54:16] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:54:21] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:54:41] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:54:47] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:54:52] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:54:57] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:51746 - - [10/Jul/2025:17:54:57] "OPTIONS /api/ai-partner/memory/search/?query=Do+you+recall+the+date+of+our+first+conversation%3F&limit=3" 200 -
INFO Memory search request: user=2, query='Do you recall the date of our first conversation?...'
INFO 🔍 DEBUG MemoryRetrieval: Starting search for user 2, query: 'Do you recall the date of our first conversation?...'
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO 🧠 DEBUG: Generated query embedding (dim: 1536)
INFO 📊 DEBUG: Vector search returned 6 results
INFO 🎯 DEBUG: Top 5 similarity scores: [0.43474449929534364, 0.43474449929534364, 0.4107213658895522, 0.39675368821445356, 0.3967096517355295]
INFO ⚠️  DEBUG: Using threshold 0.7, but scores are: min=0.3967, max=0.4347
INFO ✅ DEBUG: Returning 0 memory contexts
127.0.0.1:51658 - - [10/Jul/2025:17:54:58] "GET /api/ai-partner/memory/search/?query=Do+you+recall+the+date+of+our+first+conversation%3F&limit=3" 200 85
INFO DEBUG: Personal AI chat request - User: testuser, Message: Do you recall the date of our first conversation?...
INFO DEBUG: include_memories = True, context_type = general, device_type = web
WARNING Session handling error (likely test context): get() returned more than one ConversationSession -- it returned more than 20!
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO 🧠 Revolutionary Intelligent Prompting enabled for user 2
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Using EnhancedMemoryService with extracted vector intelligence
INFO DEBUG: Starting memory retrieval for user 2
INFO DEBUG: Searching memories with query: 'Do you recall the date of our first conversation?...'
INFO Using EXTRACTED enhanced memory search with multi-factor ranking
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Trying fixed memory search for MemoryEntry model
INFO Found 117 memories with embeddings for user 2
INFO Fixed memory search returned 10 results
INFO DEBUG: Found 10 raw memories
INFO 🎯 Ranking 10 memories for query: 'Do you recall the date of our first conversation?...'
INFO 📊 Top ranked memory scores:
INFO   1. Total: 0.518 | Recency: 1.00 | Relevance: 0.29 | Continuity: 0.00
INFO   2. Total: 0.496 | Recency: 1.00 | Relevance: 0.37 | Continuity: 0.00
INFO   3. Total: 0.491 | Recency: 1.00 | Relevance: 0.15 | Continuity: 0.30
INFO DEBUG: Selected 5 top-ranked memories
INFO   Memory 1: The user inquired about recalling a previous discussion related to 341 deployments, indicating an in... (rank: 0.518)
INFO   Memory 2: In the conversation, the AI initially claimed it couldn't access memories from June 28, 2025, citing... (rank: 0.496)
INFO   Memory 3: The conversation highlights the importance of verifying deployment logs to prevent mislabeling or da... (rank: 0.491)
INFO   Memory 4: The deployment #345 occurred at 09:45 UTC, which was early morning local time (4:45 AM) for the user... (rank: 0.491)
INFO   Memory 5: In this conversation, the AI accurately states that the current year is 2025, demonstrating its abil... (rank: 0.489)
INFO DEBUG: Built memory context with 5 memories
INFO Context switch detection: is_switch=False, confidence=0.00, domain=None
INFO DEBUG: Conversation context prepared:
INFO   - Has memory context: True
INFO   - Recurring topics: ['codebase_analysis', 'AI videos', 'AI evolution', 'Deployment logs', 'Agent deployments']
INFO   - Memory context preview: Based on our previous conversations:

[July 10]: The user inquired about recalling a previous discussion related to 341 deployments, indicating an intent to utilize past chat insights for planning the...
INFO DEBUG: Checked for data requests (emotional support not needed): []
WARNING Intelligent prompting failed, using fallback: 'IntelligentPromptService' object has no attribute 'select_optimal_prompt'
INFO CRITICAL DEBUG: generate_contextual_response called
INFO User input: Do you recall the date of our first conversation?...
INFO Memory context available: True
INFO Revolutionary prompt selected: Default System Prompt
INFO Memory context content: Based on our previous conversations:

[July 10]: The user inquired about recalling a previous discussion related to 341 deployments, indicating an intent to utilize past chat insights for planning the...
INFO 🧠 Using intelligent prompt: Default System Prompt (confidence: 0.50)
INFO FINAL SYSTEM PROMPT PREVIEW: You are a Personal AI Assistant dedicated to helping users achieve their life goals and aspirations.

Your mission is to understand, adapt, and support users in their personal growth journey, whether that's:
- Building businesses and pursuing entrepreneurial dreams
- Career advancement and professional development
- Personal development and self-improvement
- Creative projects and artistic endeavors
- Life planning and goal achievement

Key capabilities:
- Deploy AI agents from the 21-agent work...
INFO Selected openai/gpt-4.1-nano for task 'chat'
INFO Selected openai/gpt-4.1-nano for chat
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO AI RESPONSE (openai/gpt-4.1-nano): Yes, our first conversation was on June 28, 2025....
INFO DEBUG: Response before cleaning: Yes, our first conversation was on June 28, 2025....
INFO DEBUG: Response after cleaning: Yes, our first conversation was on June 28, 2025....
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO 🧠 Revolutionary Intelligent Prompting enabled for user 2
INFO Selected openai/gpt-4.1 for task 'analysis'
INFO Selected openai/gpt-4.1 for analysis
127.0.0.1:50435 - - [10/Jul/2025:17:55:03] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Created 1 embeddings for conversation 4083
INFO Conversation not memorable enough for Memory Palace
INFO Conversation not saved to Memory Palace (not memorable enough)
127.0.0.1:51658 - - [10/Jul/2025:17:55:05] "POST /api/ai-partner/chat/" 200 1363
127.0.0.1:51658 - - [10/Jul/2025:17:55:08] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:51658 - - [10/Jul/2025:17:55:13] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:51658 - - [10/Jul/2025:17:55:19] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:51658 - - [10/Jul/2025:17:55:24] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:51658 - - [10/Jul/2025:17:55:29] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:51658 - - [10/Jul/2025:17:55:35] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:51746 - - [10/Jul/2025:17:55:35] "OPTIONS /api/ai-partner/memory/search/?query=What+do+you+know+about+me+as+the+user%3F&limit=3" 200 -
INFO Memory search request: user=2, query='What do you know about me as the user?...'
INFO 🔍 DEBUG MemoryRetrieval: Starting search for user 2, query: 'What do you know about me as the user?...'
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO 🧠 DEBUG: Generated query embedding (dim: 1536)
INFO 📊 DEBUG: Vector search returned 6 results
INFO 🎯 DEBUG: Top 5 similarity scores: [0.49417054896398493, 0.4745420323733639, 0.421616582611684, 0.4148596322201835, 0.4117503324001617]
INFO ⚠️  DEBUG: Using threshold 0.7, but scores are: min=0.4118, max=0.4942
INFO ✅ DEBUG: Returning 0 memory contexts
127.0.0.1:51658 - - [10/Jul/2025:17:55:36] "GET /api/ai-partner/memory/search/?query=What+do+you+know+about+me+as+the+user%3F&limit=3" 200 74
INFO DEBUG: Personal AI chat request - User: testuser, Message: What do you know about me as the user?...
INFO DEBUG: include_memories = True, context_type = general, device_type = web
WARNING Session handling error (likely test context): get() returned more than one ConversationSession -- it returned more than 20!
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO 🧠 Revolutionary Intelligent Prompting enabled for user 2
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Using EnhancedMemoryService with extracted vector intelligence
INFO DEBUG: Starting memory retrieval for user 2
INFO DEBUG: Searching memories with query: 'What do you know about me as the user?...'
INFO Using EXTRACTED enhanced memory search with multi-factor ranking
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Trying fixed memory search for MemoryEntry model
INFO Found 117 memories with embeddings for user 2
INFO Fixed memory search returned 10 results
INFO DEBUG: Found 10 raw memories
INFO 🎯 Ranking 10 memories for query: 'What do you know about me as the user?...'
INFO 📊 Top ranked memory scores:
INFO   1. Total: 0.489 | Recency: 1.00 | Relevance: 0.22 | Continuity: 0.00
INFO   2. Total: 0.483 | Recency: 1.00 | Relevance: 0.33 | Continuity: 0.00
INFO   3. Total: 0.477 | Recency: 1.00 | Relevance: 0.27 | Continuity: 0.00
INFO DEBUG: Selected 5 top-ranked memories
INFO   Memory 1: The user inquired about recalling a previous discussion related to 341 deployments, indicating an in... (rank: 0.489)
INFO   Memory 2: The user is interested in building businesses, advancing professionally, and leveraging AI for perso... (rank: 0.483)
INFO   Memory 3: The conversation highlights that AI systems, including myself, continuously evolve by integrating ne... (rank: 0.477)
INFO   Memory 4: The deployment #345 occurred at 09:45 UTC, which was early morning local time (4:45 AM) for the user... (rank: 0.469)
INFO   Memory 5: The conversation highlights the AI's commitment to accuracy by retrieving deployment details directl... (rank: 0.463)
INFO DEBUG: Built memory context with 5 memories
INFO Context switch detection: is_switch=False, confidence=0.00, domain=None
INFO DEBUG: Conversation context prepared:
INFO   - Has memory context: True
INFO   - Recurring topics: ['codebase_analysis', 'AI videos', 'AI evolution', 'Deployment logs', 'Agent deployments']
INFO   - Memory context preview: Based on our previous conversations:

[July 10]: The user inquired about recalling a previous discussion related to 341 deployments, indicating an intent to utilize past chat insights for planning the...
INFO DEBUG: Checked for data requests (emotional support not needed): []
WARNING Intelligent prompting failed, using fallback: 'IntelligentPromptService' object has no attribute 'select_optimal_prompt'
INFO CRITICAL DEBUG: generate_contextual_response called
INFO User input: What do you know about me as the user?...
INFO Memory context available: True
INFO Revolutionary prompt selected: Default System Prompt
INFO Memory context content: Based on our previous conversations:

[July 10]: The user inquired about recalling a previous discussion related to 341 deployments, indicating an intent to utilize past chat insights for planning the...
INFO 🧠 Using intelligent prompt: Default System Prompt (confidence: 0.50)
INFO FINAL SYSTEM PROMPT PREVIEW: You are a Personal AI Assistant dedicated to helping users achieve their life goals and aspirations.

Your mission is to understand, adapt, and support users in their personal growth journey, whether that's:
- Building businesses and pursuing entrepreneurial dreams
- Career advancement and professional development
- Personal development and self-improvement
- Creative projects and artistic endeavors
- Life planning and goal achievement

Key capabilities:
- Deploy AI agents from the 21-agent work...
INFO Selected openai/gpt-4.1-nano for task 'chat'
INFO Selected openai/gpt-4.1-nano for chat
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO AI RESPONSE (openai/gpt-4.1-nano): You’re a direct communicator focused on building businesses, advancing professionally, and leveragin...
INFO DEBUG: Response before cleaning: You're a direct communicator focused on building businesses, advancing professionally, and leveragin...
INFO DEBUG: Response after cleaning: You're a direct communicator focused on building businesses, advancing professionally, and leveragin...
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO 🧠 Revolutionary Intelligent Prompting enabled for user 2
INFO Selected openai/gpt-4.1 for task 'analysis'
INFO Selected openai/gpt-4.1 for analysis
127.0.0.1:50435 - - [10/Jul/2025:17:55:40] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Created 1 embeddings for conversation 4085
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
127.0.0.1:50435 - - [10/Jul/2025:17:55:46] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
INFO Saved conversation to Memory Palace: User's Focus on Efficiency and Strategic Growth
INFO Conversation saved to Memory Palace for learning continuity
127.0.0.1:51658 - - [10/Jul/2025:17:55:46] "POST /api/ai-partner/chat/" 200 1604
127.0.0.1:51658 - - [10/Jul/2025:17:55:51] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:51658 - - [10/Jul/2025:17:55:56] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:51658 - - [10/Jul/2025:17:56:02] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:51658 - - [10/Jul/2025:17:56:07] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:51658 - - [10/Jul/2025:17:56:12] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:51658 - - [10/Jul/2025:17:56:18] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:51658 - - [10/Jul/2025:17:56:23] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:51746 - - [10/Jul/2025:17:56:28] "OPTIONS /api/ai-partner/memory/search/?query=Who+won+the+2024+election%3F&limit=3" 200 -
INFO Memory search request: user=2, query='Who won the 2024 election?...'
INFO 🔍 DEBUG MemoryRetrieval: Starting search for user 2, query: 'Who won the 2024 election?...'
127.0.0.1:51658 - - [10/Jul/2025:17:56:28] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO 🧠 DEBUG: Generated query embedding (dim: 1536)
INFO 📊 DEBUG: Vector search returned 6 results
INFO 🎯 DEBUG: Top 5 similarity scores: [0.29399936509103997, 0.23021462013028415, 0.22083774209022677, 0.2037227667074386, 0.199591845273973]
INFO ⚠️  DEBUG: Using threshold 0.7, but scores are: min=0.1996, max=0.2940
INFO ✅ DEBUG: Returning 0 memory contexts
127.0.0.1:50435 - - [10/Jul/2025:17:56:29] "GET /api/ai-partner/memory/search/?query=Who+won+the+2024+election%3F&limit=3" 200 62
INFO DEBUG: Personal AI chat request - User: testuser, Message: Who won the 2024 election?...
INFO DEBUG: include_memories = True, context_type = general, device_type = web
WARNING Session handling error (likely test context): get() returned more than one ConversationSession -- it returned more than 20!
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO 🧠 Revolutionary Intelligent Prompting enabled for user 2
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Using EnhancedMemoryService with extracted vector intelligence
INFO DEBUG: Starting memory retrieval for user 2
INFO DEBUG: Searching memories with query: 'Who won the 2024 election?...'
INFO Using EXTRACTED enhanced memory search with multi-factor ranking
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Trying fixed memory search for MemoryEntry model
INFO Found 118 memories with embeddings for user 2
INFO Fixed memory search returned 10 results
INFO DEBUG: Found 10 raw memories
INFO 🎯 Ranking 10 memories for query: 'Who won the 2024 election?...'
INFO 📊 Top ranked memory scores:
INFO   1. Total: 0.477 | Recency: 1.00 | Relevance: 0.24 | Continuity: 0.00
INFO   2. Total: 0.435 | Recency: 1.00 | Relevance: 0.21 | Continuity: 0.00
INFO   3. Total: 0.435 | Recency: 1.00 | Relevance: 0.21 | Continuity: 0.00
INFO DEBUG: Selected 5 top-ranked memories
INFO   Memory 1: In this conversation, the AI accurately states that the current year is 2025, demonstrating its abil... (rank: 0.477)
INFO   Memory 2: In the conversation, the AI initially claimed it couldn't access memories from June 28, 2025, citing... (rank: 0.435)
INFO   Memory 3: During the conversations spanning 2023-2024, a significant milestone was the planning of 341 deploym... (rank: 0.435)
INFO   Memory 4: This conversation highlights that the original vision for Donkey Betz was to create an AI-powered sp... (rank: 0.420)
INFO   Memory 5: The AI reaffirmed its commitment to remember and prioritize verified facts about deployments, ensuri... (rank: 0.418)
INFO DEBUG: Built memory context with 5 memories
INFO Context switch detection: is_switch=False, confidence=0.00, domain=None
INFO DEBUG: Conversation context prepared:
INFO   - Has memory context: True
INFO   - Recurring topics: ['codebase_analysis', 'AI videos', 'AI evolution', 'Deployment logs', 'Agent deployments']
INFO   - Memory context preview: Based on our previous conversations:

[July 10]: In this conversation, the AI accurately states that the current year is 2025, demonstrating its ability to provide timely contextual information. This ...
INFO DEBUG: Checked for data requests (emotional support not needed): []
WARNING Intelligent prompting failed, using fallback: 'IntelligentPromptService' object has no attribute 'select_optimal_prompt'
INFO CRITICAL DEBUG: generate_contextual_response called
INFO User input: Who won the 2024 election?...
INFO Memory context available: True
INFO Revolutionary prompt selected: Default System Prompt
INFO Memory context content: Based on our previous conversations:

[July 10]: In this conversation, the AI accurately states that the current year is 2025, demonstrating its ability to provide timely contextual information. This ...
INFO 🧠 Using intelligent prompt: Default System Prompt (confidence: 0.50)
INFO FINAL SYSTEM PROMPT PREVIEW: You are a Personal AI Assistant dedicated to helping users achieve their life goals and aspirations.

Your mission is to understand, adapt, and support users in their personal growth journey, whether that's:
- Building businesses and pursuing entrepreneurial dreams
- Career advancement and professional development
- Personal development and self-improvement
- Creative projects and artistic endeavors
- Life planning and goal achievement

Key capabilities:
- Deploy AI agents from the 21-agent work...
INFO Selected openai/gpt-4.1-nano for task 'chat'
INFO Selected openai/gpt-4.1-nano for chat
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO AI RESPONSE (openai/gpt-4.1-nano): The 2024 election results are currently unavailable as the election has not yet occurred or the offi...
INFO DEBUG: Response before cleaning: The 2024 election results are currently unavailable as the election has not yet occurred or the offi...
INFO DEBUG: Response after cleaning: The 2024 election results are currently unavailable as the election has not yet occurred or the offi...
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO 🧠 Revolutionary Intelligent Prompting enabled for user 2
INFO Selected openai/gpt-4.1 for task 'analysis'
INFO Selected openai/gpt-4.1 for analysis
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Created 1 embeddings for conversation 4087
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Saved conversation to Memory Palace: Limitations on Real-Time Election Data Access
INFO Conversation saved to Memory Palace for learning continuity
127.0.0.1:50435 - - [10/Jul/2025:17:56:37] "POST /api/ai-partner/chat/" 200 1536
127.0.0.1:50435 - - [10/Jul/2025:17:56:44] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50435 - - [10/Jul/2025:17:56:49] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638



127.0.0.1:52172 - - [10/Jul/2025:18:00:17] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:50216 - - [10/Jul/2025:18:00:18] "WSDISCONNECT /ws/dashboard-stats/" - -
127.0.0.1:50268 - - [10/Jul/2025:18:00:18] "WSDISCONNECT /ws/dashboard-stats/" - -
127.0.0.1:50467 - - [10/Jul/2025:18:00:18] "WSDISCONNECT /ws/dashboard-stats/" - -
127.0.0.1:50476 - - [10/Jul/2025:18:00:18] "WSDISCONNECT /ws/dashboard-stats/" - -
INFO User 2 disconnected from dashboard stats WebSocket
INFO User 2 disconnected from dashboard stats WebSocket
INFO User 2 disconnected from dashboard stats WebSocket
INFO User 2 disconnected from dashboard stats WebSocket
127.0.0.1:52172 - - [10/Jul/2025:18:00:19] "GET /api/auth/user/" 200 61
127.0.0.1:52172 - - [10/Jul/2025:18:00:19] "GET /api/auth/user/" 200 61
127.0.0.1:52193 - - [10/Jul/2025:18:00:19] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:52193 - - [10/Jul/2025:18:00:24] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:52193 - - [10/Jul/2025:18:00:30] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:52193 - - [10/Jul/2025:18:00:35] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:52225 - - [10/Jul/2025:18:00:38] "OPTIONS /api/ai-partner/memory/search/?query=Do+you+remember+working+on+a+project+called+Magical+Mountains%3F&limit=3" 200 -
INFO Memory search request: user=2, query='Do you remember working on a project called Magica...'
INFO 🔍 DEBUG MemoryRetrieval: Starting search for user 2, query: 'Do you remember working on a project called Magica...'
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO 🧠 DEBUG: Generated query embedding (dim: 1536)
INFO 📊 DEBUG: Vector search returned 6 results
INFO 🎯 DEBUG: Top 5 similarity scores: [0.3095308542251609, 0.30263041822548553, 0.2868038083104225, 0.28409700671617477, 0.27864245558219203]
INFO ⚠️  DEBUG: Using threshold 0.7, but scores are: min=0.2786, max=0.3095
INFO ✅ DEBUG: Returning 0 memory contexts
127.0.0.1:52193 - - [10/Jul/2025:18:00:40] "GET /api/ai-partner/memory/search/?query=Do+you+remember+working+on+a+project+called+Magical+Mountains%3F&limit=3" 200 98
INFO DEBUG: Personal AI chat request - User: testuser, Message: Do you remember working on a project called Magica...
INFO DEBUG: include_memories = True, context_type = general, device_type = web
WARNING Session handling error (likely test context): get() returned more than one ConversationSession -- it returned more than 20!
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO 🧠 Revolutionary Intelligent Prompting enabled for user 2
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Using EnhancedMemoryService with extracted vector intelligence
INFO DEBUG: Starting memory retrieval for user 2
INFO DEBUG: Searching memories with query: 'Do you remember working on a project called Magica...'
INFO Using EXTRACTED enhanced memory search with multi-factor ranking
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Trying fixed memory search for MemoryEntry model
INFO Found 119 memories with embeddings for user 2
127.0.0.1:52172 - - [10/Jul/2025:18:00:40] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
INFO Fixed memory search returned 10 results
INFO DEBUG: Found 10 raw memories
INFO 🎯 Ranking 10 memories for query: 'Do you remember working on a project called Magica...'
INFO 📊 Top ranked memory scores:
INFO   1. Total: 0.474 | Recency: 1.00 | Relevance: 0.18 | Continuity: 0.00
INFO   2. Total: 0.459 | Recency: 1.00 | Relevance: 0.12 | Continuity: 0.30
INFO   3. Total: 0.445 | Recency: 1.00 | Relevance: 0.16 | Continuity: 0.00
INFO DEBUG: Selected 5 top-ranked memories
INFO   Memory 1: The user inquired about recalling a previous discussion related to 341 deployments, indicating an in... (rank: 0.474)
INFO   Memory 2: The deployment #345 occurred at 09:45 UTC, which was early morning local time (4:45 AM) for the user... (rank: 0.459)
INFO   Memory 3: The key insight from the conversation is that to make Donkey Betz appealing to major tech companies ... (rank: 0.445)
INFO   Memory 4: Deployment #342 took place on July 10, involving a database migration aimed at improving system stab... (rank: 0.428)
INFO   Memory 5: The conversation clarified that deployment #666 does not exist in system records, and the coordinate... (rank: 0.423)
INFO DEBUG: Built memory context with 5 memories
INFO Context switch detection: is_switch=False, confidence=0.00, domain=None
INFO DEBUG: Conversation context prepared:
INFO   - Has memory context: True
INFO   - Recurring topics: ['codebase_analysis', 'AI videos', 'AI evolution', 'Deployment logs', 'Agent deployments']
INFO   - Memory context preview: Based on our previous conversations:

[July 10]: The user inquired about recalling a previous discussion related to 341 deployments, indicating an intent to utilize past chat insights for planning the...
INFO DEBUG: Checked for data requests (emotional support not needed): []
WARNING Intelligent prompting failed, using fallback: 'IntelligentPromptService' object has no attribute 'select_optimal_prompt'
INFO CRITICAL DEBUG: generate_contextual_response called
INFO User input: Do you remember working on a project called Magical Mountains?...
INFO Memory context available: True
INFO Revolutionary prompt selected: Default System Prompt
INFO Memory context content: Based on our previous conversations:

[July 10]: The user inquired about recalling a previous discussion related to 341 deployments, indicating an intent to utilize past chat insights for planning the...
INFO 🧠 Using intelligent prompt: Default System Prompt (confidence: 0.50)
INFO FINAL SYSTEM PROMPT PREVIEW: You are a Personal AI Assistant dedicated to helping users achieve their life goals and aspirations.

Your mission is to understand, adapt, and support users in their personal growth journey, whether that's:
- Building businesses and pursuing entrepreneurial dreams
- Career advancement and professional development
- Personal development and self-improvement
- Creative projects and artistic endeavors
- Life planning and goal achievement

Key capabilities:
- Deploy AI agents from the 21-agent work...
INFO Selected openai/gpt-4.1-nano for task 'chat'
INFO Selected openai/gpt-4.1-nano for chat
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO AI RESPONSE (openai/gpt-4.1-nano): Yes, I recall working on the Magical Mountains project—focused on creating an immersive experience o...
INFO DEBUG: Response before cleaning: Yes, I recall working on the Magical Mountains project-focused on creating an immersive experience o...
INFO DEBUG: Response after cleaning: Yes, I recall working on the Magical Mountains project-focused on creating an immersive experience o...
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO 🧠 Revolutionary Intelligent Prompting enabled for user 2
INFO Selected openai/gpt-4.1 for task 'analysis'
INFO Selected openai/gpt-4.1 for analysis
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Created 1 embeddings for conversation 4089
127.0.0.1:52172 - - [10/Jul/2025:18:00:51] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Saved conversation to Memory Palace: Recall and Continuation of Magical Mountains Project
INFO Conversation saved to Memory Palace for learning continuity
127.0.0.1:52193 - - [10/Jul/2025:18:00:51] "POST /api/ai-partner/chat/" 200 1520
127.0.0.1:52193 - - [10/Jul/2025:18:00:56] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:52193 - - [10/Jul/2025:18:01:02] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:52193 - - [10/Jul/2025:18:01:37] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:52193 - - [10/Jul/2025:18:01:43] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:52193 - - [10/Jul/2025:18:01:48] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:52193 - - [10/Jul/2025:18:01:53] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:52193 - - [10/Jul/2025:18:01:59] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:52193 - - [10/Jul/2025:18:02:04] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:52193 - - [10/Jul/2025:18:02:09] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:52193 - - [10/Jul/2025:18:02:15] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:52193 - - [10/Jul/2025:18:02:20] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:52193 - - [10/Jul/2025:18:02:25] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:52193 - - [10/Jul/2025:18:02:30] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:52193 - - [10/Jul/2025:18:02:36] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:52193 - - [10/Jul/2025:18:02:41] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:52193 - - [10/Jul/2025:18:02:46] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:52193 - - [10/Jul/2025:18:02:52] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:52193 - - [10/Jul/2025:18:02:57] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:52193 - - [10/Jul/2025:18:03:03] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:52193 - - [10/Jul/2025:18:03:08] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:52193 - - [10/Jul/2025:18:03:13] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:52193 - - [10/Jul/2025:18:03:19] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638


127.0.0.1:52593 - - [10/Jul/2025:18:06:45] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:52593 - - [10/Jul/2025:18:06:51] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:52593 - - [10/Jul/2025:18:06:56] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:52782 - - [10/Jul/2025:18:06:57] "OPTIONS /api/ai-partner/memory/search/?query=What+color+is+the+sky%3F&limit=3" 200 -
INFO Memory search request: user=2, query='What color is the sky?...'
INFO 🔍 DEBUG MemoryRetrieval: Starting search for user 2, query: 'What color is the sky?...'
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO 🧠 DEBUG: Generated query embedding (dim: 1536)
INFO 📊 DEBUG: Vector search returned 6 results
INFO 🎯 DEBUG: Top 5 similarity scores: [0.25082206657475636, 0.23049026495112712, 0.22753130970893898, 0.21748692899796473, 0.21614543208864234]
INFO ⚠️  DEBUG: Using threshold 0.7, but scores are: min=0.2161, max=0.2508
INFO ✅ DEBUG: Returning 0 memory contexts
127.0.0.1:52593 - - [10/Jul/2025:18:06:57] "GET /api/ai-partner/memory/search/?query=What+color+is+the+sky%3F&limit=3" 200 58
INFO DEBUG: Personal AI chat request - User: testuser, Message: What color is the sky?...
INFO DEBUG: include_memories = True, context_type = general, device_type = web
WARNING Session handling error (likely test context): get() returned more than one ConversationSession -- it returned more than 20!
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO 🧠 Revolutionary Intelligent Prompting enabled for user 2
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Using EnhancedMemoryService with extracted vector intelligence
INFO DEBUG: Starting memory retrieval for user 2
INFO DEBUG: Searching memories with query: 'What color is the sky?...'
INFO Using EXTRACTED enhanced memory search with multi-factor ranking
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Trying fixed memory search for MemoryEntry model
INFO Found 120 memories with embeddings for user 2
INFO Fixed memory search returned 10 results
INFO DEBUG: Found 10 raw memories
INFO 🎯 Ranking 10 memories for query: 'What color is the sky?...'
INFO 📊 Top ranked memory scores:
INFO   1. Total: 0.463 | Recency: 1.00 | Relevance: 0.13 | Continuity: 0.30
INFO   2. Total: 0.423 | Recency: 1.00 | Relevance: 0.13 | Continuity: 0.00
INFO   3. Total: 0.407 | Recency: 1.00 | Relevance: 0.14 | Continuity: 0.00
INFO DEBUG: Selected 5 top-ranked memories
INFO   Memory 1: The deployment #345 occurred at 09:45 UTC, which was early morning local time (4:45 AM) for the user... (rank: 0.463)
INFO   Memory 2: The conversation highlights the AI's commitment to accuracy by retrieving deployment details directl... (rank: 0.423)
INFO   Memory 3: The conversation confirmed familiarity with the Magical Mountains project, which focuses on creating... (rank: 0.407)
INFO   Memory 4: The AI reaffirmed its commitment to remember and prioritize verified facts about deployments, ensuri... (rank: 0.407)
INFO   Memory 5: The key insight from the conversation is that to make Donkey Betz appealing to major tech companies ... (rank: 0.406)
INFO DEBUG: Built memory context with 5 memories
INFO Context switch detection: is_switch=False, confidence=0.00, domain=design
INFO DEBUG: Conversation context prepared:
INFO   - Has memory context: True
INFO   - Recurring topics: ['codebase_analysis', 'AI videos', 'AI evolution', 'Deployment logs', 'Agent deployments']
INFO   - Memory context preview: Based on our previous conversations:

[July 10]: The deployment #345 occurred at 09:45 UTC, which was early morning local time (4:45 AM) for the user due to server timestamps being set to UTC. This hi...
INFO DEBUG: Checked for data requests (emotional support not needed): []
WARNING Intelligent prompting failed, using fallback: 'IntelligentPromptService' object has no attribute 'select_optimal_prompt'
INFO CRITICAL DEBUG: generate_contextual_response called
INFO User input: What color is the sky?...
INFO Memory context available: True
INFO Revolutionary prompt selected: Default System Prompt
INFO Memory context content: Based on our previous conversations:

[July 10]: The deployment #345 occurred at 09:45 UTC, which was early morning local time (4:45 AM) for the user due to server timestamps being set to UTC. This hi...
INFO 🧠 Using intelligent prompt: Default System Prompt (confidence: 0.50)
INFO FINAL SYSTEM PROMPT PREVIEW: You are a Personal AI Assistant dedicated to helping users achieve their life goals and aspirations.

Your mission is to understand, adapt, and support users in their personal growth journey, whether that's:
- Building businesses and pursuing entrepreneurial dreams
- Career advancement and professional development
- Personal development and self-improvement
- Creative projects and artistic endeavors
- Life planning and goal achievement

Key capabilities:
- Deploy AI agents from the 21-agent work...
INFO Selected openai/gpt-4.1-nano for task 'chat'
INFO Selected openai/gpt-4.1-nano for chat
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO AI RESPONSE (openai/gpt-4.1-nano): The sky appears blue during the day due to Rayleigh scattering of sunlight in Earth's atmosphere. Wo...
INFO DEBUG: Response before cleaning: The sky appears blue during the day due to Rayleigh scattering of sunlight in Earth's atmosphere. Wo...
INFO DEBUG: Response after cleaning: The sky appears blue during the day due to Rayleigh scattering of sunlight in Earth's atmosphere. Wo...
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO 🧠 Revolutionary Intelligent Prompting enabled for user 2
INFO Selected openai/gpt-4.1 for task 'analysis'
INFO Selected openai/gpt-4.1 for analysis
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Created 1 embeddings for conversation 4093
INFO Conversation not memorable enough for Memory Palace
INFO Conversation not saved to Memory Palace (not memorable enough)
127.0.0.1:52593 - - [10/Jul/2025:18:07:01] "POST /api/ai-partner/chat/" 200 1492
127.0.0.1:52593 - - [10/Jul/2025:18:07:16] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:52593 - - [10/Jul/2025:18:07:22] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:52593 - - [10/Jul/2025:18:07:27] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:52593 - - [10/Jul/2025:18:07:32] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:52593 - - [10/Jul/2025:18:07:37] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
127.0.0.1:52782 - - [10/Jul/2025:18:07:40] "OPTIONS /api/ai-partner/memory/search/?query=What+is+the+weather+today%3F&limit=3" 200 -
INFO Memory search request: user=2, query='What is the weather today?...'
INFO 🔍 DEBUG MemoryRetrieval: Starting search for user 2, query: 'What is the weather today?...'
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO 🧠 DEBUG: Generated query embedding (dim: 1536)
INFO 📊 DEBUG: Vector search returned 6 results
INFO 🎯 DEBUG: Top 5 similarity scores: [0.566497447163981, 0.5510166263074259, 0.5290310836601871, 0.4833029220519717, 0.45753308118179703]
INFO ⚠️  DEBUG: Using threshold 0.7, but scores are: min=0.4575, max=0.5665
INFO ✅ DEBUG: Returning 0 memory contexts
127.0.0.1:52593 - - [10/Jul/2025:18:07:40] "GET /api/ai-partner/memory/search/?query=What+is+the+weather+today%3F&limit=3" 200 62
INFO DEBUG: Personal AI chat request - User: testuser, Message: What is the weather today?...
INFO DEBUG: include_memories = True, context_type = general, device_type = web
WARNING Session handling error (likely test context): get() returned more than one ConversationSession -- it returned more than 20!
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO 🧠 Revolutionary Intelligent Prompting enabled for user 2
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Using EnhancedMemoryService with extracted vector intelligence
INFO DEBUG: Starting memory retrieval for user 2
INFO DEBUG: Searching memories with query: 'What is the weather today?...'
INFO Using EXTRACTED enhanced memory search with multi-factor ranking
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Trying fixed memory search for MemoryEntry model
INFO Found 120 memories with embeddings for user 2
INFO Fixed memory search returned 10 results
INFO DEBUG: Found 10 raw memories
INFO 🎯 Ranking 10 memories for query: 'What is the weather today?...'
INFO 📊 Top ranked memory scores:
INFO   1. Total: 0.467 | Recency: 1.00 | Relevance: 0.14 | Continuity: 0.30
INFO   2. Total: 0.453 | Recency: 1.00 | Relevance: 0.18 | Continuity: 0.00
INFO   3. Total: 0.452 | Recency: 1.00 | Relevance: 0.11 | Continuity: 0.30
INFO DEBUG: Selected 5 top-ranked memories
INFO   Memory 1: The deployment #345 occurred at 09:45 UTC, which was early morning local time (4:45 AM) for the user... (rank: 0.467)
INFO   Memory 2: In this conversation, the AI accurately states that the current year is 2025, demonstrating its abil... (rank: 0.453)
INFO   Memory 3: The system has completed multiple agent deployments recently, including Research, Business, and Tech... (rank: 0.452)
INFO   Memory 4: The coordinates 47.6062° N, 122.3321° W point to Seattle, WA, an area known for tech hubs and innova... (rank: 0.397)
INFO   Memory 5: The AI reaffirmed its commitment to remember and prioritize verified facts about deployments, ensuri... (rank: 0.394)
INFO DEBUG: Built memory context with 5 memories
INFO Context switch detection: is_switch=False, confidence=0.00, domain=None
INFO DEBUG: Conversation context prepared:
INFO   - Has memory context: True
INFO   - Recurring topics: ['codebase_analysis', 'AI videos', 'AI evolution', 'Deployment logs', 'Agent deployments']
INFO   - Memory context preview: Based on our previous conversations:

[July 10]: The deployment #345 occurred at 09:45 UTC, which was early morning local time (4:45 AM) for the user due to server timestamps being set to UTC. This hi...
INFO DEBUG: Checked for data requests (emotional support not needed): ['weather']
INFO DEBUG: Detected data request categories: ['weather']
INFO DEBUG: Fetched API data: ['weather']
INFO DEBUG: Agent suggestions: []
INFO DEBUG: Generated data-aware response with 1 data sources
INFO DEBUG: Response before cleaning: Live Data Insights:
Weather: 74°F, Partly cloudy...
INFO DEBUG: Response after cleaning: Live Data Insights: Weather: 74°F, Partly cloudy...
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO 🧠 Revolutionary Intelligent Prompting enabled for user 2
INFO Selected openai/gpt-4.1 for task 'analysis'
INFO Selected openai/gpt-4.1 for analysis
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
127.0.0.1:52864 - - [10/Jul/2025:18:07:43] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638
INFO Created 1 embeddings for conversation 4095
INFO Conversation not memorable enough for Memory Palace
INFO Conversation not saved to Memory Palace (not memorable enough)
127.0.0.1:52593 - - [10/Jul/2025:18:07:43] "POST /api/ai-partner/chat/" 200 1383
127.0.0.1:52593 - - [10/Jul/2025:18:07:48] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1668638



##### START HERE #####

INFO Started thread for agent 1121 (News Catalyst Agent)
INFO
============================================================
INFO execute_agent_sync called for agent_id: 1121
INFO ============================================================
INFO Starting execution of agent 1122 (Technical Chart Agent)
INFO Started thread for agent 1122 (Technical Chart Agent)
INFO
============================================================
INFO execute_agent_sync called for agent_id: 1122
INFO ============================================================
INFO Starting execution of agent 1123 (Stock Synthesis Agent)
INFO Started thread for agent 1123 (Stock Synthesis Agent)
INFO
============================================================
INFO execute_agent_sync called for agent_id: 1123
INFO ============================================================
INFO Found agent: Market Sentiment Agent - Status: working
INFO OpenAI API Key configured: True
INFO Using Enhanced executor with API tools for Market Sentiment Agent
INFO Found agent: Fundamental Value Agent - Status: working
INFO Found agent: Technical Chart Agent - Status: working
INFO OpenAI API Key configured: True
INFO Found agent: News Catalyst Agent - Status: working
INFO OpenAI API Key configured: True
INFO Found agent: Stock Synthesis Agent - Status: working
INFO EnhancedSyncAgentExecutor initialized for agent 1119 (Market Sentiment Agent)
INFO Using Enhanced executor with API tools for Fundamental Value Agent
INFO OpenAI API Key configured: True
INFO Using Enhanced executor with API tools for Technical Chart Agent
INFO OpenAI API Key configured: True
INFO Orchestration ID: 409
INFO Using Enhanced executor with API tools for News Catalyst Agent
INFO Using Enhanced executor with API tools for Stock Synthesis Agent
INFO Channel layer: RedisChannelLayer(hosts=[{'host': '127.0.0.1', 'port': 6379}])
INFO === ENHANCED AI EXECUTION WITH REAL TOOLS for Agent 1119 ===
INFO Agent: Market Sentiment Agent
INFO Task:
        Analyze Reddit sentiment across 10 investing subreddits:

        1. Track mention velocity (% increase in mentions)
        2. Measure sentiment shifts (bullish/bearish ratio)
        3. Identify high-quality DD posts
        4. Spot unusual volume spikes
        5. Find stocks BEFORE mainstream attention

        Focus on:
        - Tickers mentioned 3+ times with increasing frequency
        - Posts with high engagement (upvotes + comments)
        - DD posts from credible users
        - Catalyst discussions (FDA, earnings, partnerships)

        Avoid: Obvious pump & dumps, coordinated campaigns

        Return: Top 10 opportunities with sentiment scores

INFO Available Tools: ['reddit_api', 'sentiment_analyzer', 'social_momentum_tracker', 'options_flow_analyzer', 'crowd_sentiment']
INFO EnhancedSyncAgentExecutor initialized for agent 1120 (Fundamental Value Agent)
INFO Orchestration ID: 409
INFO Channel layer: RedisChannelLayer(hosts=[{'host': '127.0.0.1', 'port': 6379}])
INFO EnhancedSyncAgentExecutor initialized for agent 1122 (Technical Chart Agent)
INFO EnhancedSyncAgentExecutor initialized for agent 1121 (News Catalyst Agent)
INFO EnhancedSyncAgentExecutor initialized for agent 1123 (Stock Synthesis Agent)
INFO Orchestration ID: 409
INFO Orchestration ID: 409
127.0.0.1:53751 - - [10/Jul/2025:18:17:26] "POST /api/agent-orchestra/stocks/scout/" 200 155
INFO === ENHANCED AI EXECUTION WITH REAL TOOLS for Agent 1120 ===
INFO Orchestration ID: 409
INFO Channel layer: RedisChannelLayer(hosts=[{'host': '127.0.0.1', 'port': 6379}])
INFO Channel layer: RedisChannelLayer(hosts=[{'host': '127.0.0.1', 'port': 6379}])
INFO Agent: Fundamental Value Agent
INFO Channel layer: RedisChannelLayer(hosts=[{'host': '127.0.0.1', 'port': 6379}])
INFO === ENHANCED AI EXECUTION WITH REAL TOOLS for Agent 1122 ===
INFO Task:
        Monitor recent SEC filings for unusual activity:

        1. Check latest 8-K filings (material events)
        2. Analyze insider trading patterns (Form 4)
        3. Review 10-Q/10-K for hidden gems
        4. Identify unusual institutional activity (13F)

        Focus on:
        - CEO/CFO buying (not selling)
        - New partnerships or contracts
        - Patent filings or FDA submissions
        - Unusual balance sheet improvements

        Cross-reference with Reddit mentions for validation.

INFO Agent: Technical Chart Agent
INFO === ENHANCED AI EXECUTION WITH REAL TOOLS for Agent 1121 ===
INFO Available Tools: ['sec_edgar_api', 'yahoo_finance', 'reddit_api']
INFO === ENHANCED AI EXECUTION WITH REAL TOOLS for Agent 1123 ===
INFO Agent: Stock Synthesis Agent
INFO Task:
        Synthesize all intelligence into actionable opportunities:

        Combine:
        1. Reddit sentiment scores
        2. SEC filing insights
        3. News catalyst timing
        4. Technical setup quality

        Create unified scoring:
        - Reddit Buzz Score (0-10)
        - Fundamental Catalyst Score (0-10)
        - Technical Setup Score (0-10)
        - Risk/Reward Rating

        Output format:
        For each opportunity:
        - Ticker & Company Name
        - Overall Score (weighted average)
        - Key Catalyst
        - Entry/Exit recommendations
        - Risk factors
        - Time horizon

        Rank by highest potential with reasonable risk.

INFO Task:
        Perform technical analysis on Reddit-mentioned stocks:

        1. Chart pattern recognition
        2. Support/resistance levels
        3. Volume analysis (unusual spikes)
        4. Momentum indicators (RSI, MACD)
        5. Moving average analysis

        Focus on:
        - Breakout setups
        - Oversold bounces
        - Volume preceding price
        - Accumulation patterns

        Prioritize stocks with both technical setup AND Reddit buzz.

INFO Available Tools: ['data_analyzer', 'spreadsheet_generator', 'chart_creator', 'pdf_generator', 'risk_calculator']
INFO Agent: News Catalyst Agent
INFO Available Tools: ['yahoo_finance', 'reddit_api']
INFO Task:
        Analyze news flow and correlate with Reddit sentiment:

        1. Scan major financial news sources
        2. Check for pre-market/after-hours movers
        3. Identify stocks with news catalysts
        4. Find "under the radar" stories

        Key sources:
        - Bloomberg, Reuters, MarketWatch
        - PR Newswire, Business Wire
        - Industry-specific publications
        - SEC press releases

        Match Reddit buzz with real news to validate opportunities.
        Flag stocks with high Reddit interest but NO mainstream coverage yet.

INFO Available Tools: ['news_api', 'yahoo_finance', 'reddit_api', 'sentiment_api']
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1119: working (5%)
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1123: working (5%)
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1121: working (5%)
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1122: working (5%)
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1120: working (5%)
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Found 122 memories with embeddings for user 2
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1119: working (10%)
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Found 122 memories with embeddings for user 2
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1123: working (10%)
INFO Found 122 memories with embeddings for user 2
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1121: working (10%)
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Found 122 memories with embeddings for user 2
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1122: working (10%)
INFO Found 122 memories with embeddings for user 2
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1120: working (10%)
127.0.0.1:53751 - - [10/Jul/2025:18:17:31] "GET /api/agent-orchestra/stock-opportunities/quick-data/?scout_type=trending" 200 3908
127.0.0.1:53816 - - [10/Jul/2025:18:17:39] "OPTIONS /api/agent-orchestra/orchestrations/?show_all=true" 200 -
127.0.0.1:53817 - - [10/Jul/2025:18:17:39] "OPTIONS /api/agent-orchestra/command-center/stats/" 200 -
127.0.0.1:53745 - - [10/Jul/2025:18:17:39] "OPTIONS /api/agent-orchestra/command-center/stats/" 200 -
127.0.0.1:53747 - - [10/Jul/2025:18:17:39] "OPTIONS /api/agent-orchestra/orchestrations/?show_all=true" 200 -
127.0.0.1:53751 - - [10/Jul/2025:18:17:39] "GET /api/agent-orchestra/templates/" 200 15851
127.0.0.1:53820 - - [10/Jul/2025:18:17:39] "GET /api/agent-orchestra/command-center/stats/" 200 130
127.0.0.1:53751 - - [10/Jul/2025:18:17:39] "GET /api/agent-orchestra/templates/" 200 15851
127.0.0.1:53820 - - [10/Jul/2025:18:17:39] "GET /api/agent-orchestra/command-center/stats/" 200 130
127.0.0.1:53694 - - [10/Jul/2025:18:17:39] "GET /api/agent-orchestra/orchestrations/?show_all=true" 200 1829359
127.0.0.1:53820 - - [10/Jul/2025:18:17:39] "GET /api/agent-orchestra/orchestrations/?show_all=true" 200 1829359
127.0.0.1:53820 - - [10/Jul/2025:18:17:40] "GET /api/agent-orchestra/orchestrations/?show_all=true" 200 1829359
127.0.0.1:53841 - - [10/Jul/2025:18:17:40] "WSCONNECTING /ws/agent-orchestra/409/" - -
INFO WebSocket authenticated user: testuser
127.0.0.1:53841 - - [10/Jul/2025:18:17:40] "WSCONNECT /ws/agent-orchestra/409/" - -
INFO User 2 connected to agent progress WebSocket for orchestration 409
127.0.0.1:53694 - - [10/Jul/2025:18:17:40] "GET /api/agent-orchestra/orchestrations/?show_all=true" 200 1829359
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1120: working (15%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1120', 'agent_name': 'Fundamental Value Agent', 'status': 'working', 'progress': 15, 'current_step': 'Plan created with 5 steps'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1120
INFO Agent 1120 executing step 1/5: Check the latest 8-K filings to identify material events such as new partnerships, contracts, or significant corporate changes.
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1120: working (15%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1120', 'agent_name': 'Fundamental Value Agent', 'status': 'working', 'progress': 15, 'current_step': 'Executing step 1/5: Check the latest 8-K filings to identify material ...'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1120
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1123: working (15%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1123', 'agent_name': 'Stock Synthesis Agent', 'status': 'working', 'progress': 15, 'current_step': 'Plan created with 7 steps'}
INFO Agent 1123 executing step 1/7: Identify trending stocks on Reddit to gauge market sentiment and interest.
INFO WebSocket consumer sent message to client: agent_progress for agent 1123
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1123', 'agent_name': 'Stock Synthesis Agent', 'status': 'working', 'progress': 15, 'current_step': 'Executing step 1/7: Identify trending stocks on Reddit to gauge market...'}
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1123: working (15%)
INFO WebSocket consumer sent message to client: agent_progress for agent 1123
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1121: working (15%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1121', 'agent_name': 'News Catalyst Agent', 'status': 'working', 'progress': 15, 'current_step': 'Plan created with 8 steps'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1121
INFO Agent 1121 executing step 1/8: Scan major financial news sources for the latest market trends, significant stock movements, and major corporate announcements.
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1121: working (15%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1121', 'agent_name': 'News Catalyst Agent', 'status': 'working', 'progress': 15, 'current_step': 'Executing step 1/8: Scan major financial news sources for the latest m...'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1121
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO 🔧 EXECUTING TOOL CALL: sec_edgar_api with params: {'filing_types': ['8-K']}
WARNING sec_edgar_api called without symbol/company, using default SPY
INFO Filtered out parameters for sec_edgar_api: {'filing_types'}
INFO Executing tool: sec_edgar_api with validated parameters: {'symbol': 'SPY'}
ERROR SEC EDGAR API error: 'SECAPIService' object does not support the asynchronous context manager protocol
INFO Tool sec_edgar_api executed successfully
WARNING Tool sec_edgar_api returned error: 'SECAPIService' object does not support the asynchronous context manager protocol
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1120: error (20%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1120', 'agent_name': 'Fundamental Value Agent', 'status': 'error', 'progress': 20, 'current_step': 'Step 1/5: Check the latest 8-K filings to identify material events such as new partnerships, contracts, or significant corporate changes.'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1120
INFO Agent 1120 executing step 2/5: Analyze recent Form 4 filings to spot insider trading patterns, focusing on CEO/CFO buying activities.
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1120: working (31%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1120', 'agent_name': 'Fundamental Value Agent', 'status': 'working', 'progress': 31, 'current_step': 'Executing step 2/5: Analyze recent Form 4 filings to spot insider trad...'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1120
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO 🔧 EXECUTING TOOL CALL: reddit_api with params: {'keywords': ['stock', 'trending', 'Reddit', 'sentiment'], 'year': 2025}
WARNING Unknown parameter 'keywords' for tool reddit_api
WARNING Unknown parameter 'year' for tool reddit_api
INFO Applied parameter mappings for reddit_api: {'keywords': ['stock', 'trending', 'Reddit', 'sentiment'], 'year': 2025}
WARNING reddit_api called without subreddit, using default
INFO Filtered out parameters for reddit_api: {'keywords', 'year'}
INFO Executing tool: reddit_api with validated parameters: {'subreddit': 'stocks'}
INFO Reddit API clients initialized successfully
WARNING Error analyzing r/Entrepreneur: error with request Session is closed
WARNING Error analyzing r/startups: error with request Session is closed
WARNING Error analyzing r/SaaS: error with request Session is closed
WARNING Error analyzing r/Business_Ideas: error with request Session is closed
WARNING Error analyzing r/Startup_Ideas: error with request Session is closed
INFO Tool reddit_api executed successfully
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1123: completed (14%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1123', 'agent_name': 'Stock Synthesis Agent', 'status': 'completed', 'progress': 14, 'current_step': 'Step 1/7: Identify trending stocks on Reddit to gauge market sentiment and interest.'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1123
INFO Agent 1123 executing step 2/7: Analyze the latest SEC filings for the identified stocks to assess their financial health and future outlook.
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1123: working (26%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1123', 'agent_name': 'Stock Synthesis Agent', 'status': 'working', 'progress': 26, 'current_step': 'Executing step 2/7: Analyze the latest SEC filings for the identified ...'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1123
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO 🔧 EXECUTING TOOL CALL: sec_edgar_api with params: {'filing_types': ['Form 4'], 'date_range_start': '2025-06-01', 'date_range_end': '2025-07-10'}
WARNING sec_edgar_api called without symbol/company, using default SPY
INFO Filtered out parameters for sec_edgar_api: {'date_range_start', 'date_range_end', 'filing_types'}
INFO Executing tool: sec_edgar_api with validated parameters: {'symbol': 'SPY'}
ERROR SEC EDGAR API error: 'SECAPIService' object does not support the asynchronous context manager protocol
INFO Tool sec_edgar_api executed successfully
WARNING Tool sec_edgar_api returned error: 'SECAPIService' object does not support the asynchronous context manager protocol
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1119: working (15%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1119', 'agent_name': 'Market Sentiment Agent', 'status': 'working', 'progress': 15, 'current_step': 'Plan created with 10 steps'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1119
INFO Agent 1119 executing step 1/10: Gather initial list of frequently mentioned tickers across 10 investing subreddits
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1120: error (40%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1120', 'agent_name': 'Fundamental Value Agent', 'status': 'error', 'progress': 40, 'current_step': 'Step 2/5: Analyze recent Form 4 filings to spot insider trading patterns, focusing on CEO/CFO buying activities.'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1120
INFO Agent 1120 executing step 3/5: Review the latest 10-Q and 10-K filings for hidden gems such as unusual balance sheet improvements, patent filings, or FDA submissions.
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1119: working (15%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1119', 'agent_name': 'Market Sentiment Agent', 'status': 'working', 'progress': 15, 'current_step': 'Executing step 1/10: Gather initial list of frequently mentioned ticker...'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1119
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1120: working (47%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1120', 'agent_name': 'Fundamental Value Agent', 'status': 'working', 'progress': 47, 'current_step': 'Executing step 3/5: Review the latest 10-Q and 10-K filings for hidden...'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1120
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1122: working (15%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1122', 'agent_name': 'Technical Chart Agent', 'status': 'working', 'progress': 15, 'current_step': 'Plan created with 9 steps'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1122
INFO Agent 1122 executing step 1/9: Identify stocks mentioned on Reddit with significant buzz.
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1122: working (15%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1122', 'agent_name': 'Technical Chart Agent', 'status': 'working', 'progress': 15, 'current_step': 'Executing step 1/9: Identify stocks mentioned on Reddit with significa...'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1122
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1123: completed (28%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1123', 'agent_name': 'Stock Synthesis Agent', 'status': 'completed', 'progress': 28, 'current_step': 'Step 2/7: Analyze the latest SEC filings for the identified stocks to assess their financial health and future outlook.'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1123
INFO Agent 1123 executing step 3/7: Search for recent news articles related to the identified stocks to find any potential catalysts that could affect stock prices.
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1123: working (37%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1123', 'agent_name': 'Stock Synthesis Agent', 'status': 'working', 'progress': 37, 'current_step': 'Executing step 3/7: Search for recent news articles related to the ide...'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1123
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO 🔧 EXECUTING TOOL CALL: reddit_api with params: {'subreddit': 'stocks'}
INFO Applied parameter mappings for reddit_api: {'subreddit': 'stocks'}
INFO Executing tool: reddit_api with validated parameters: {'subreddit': 'stocks'}
INFO Reddit API clients initialized successfully
WARNING Error analyzing r/Entrepreneur: error with request Session is closed
WARNING Error analyzing r/startups: error with request Session is closed
WARNING Error analyzing r/SaaS: error with request Session is closed
WARNING Error analyzing r/Business_Ideas: error with request Session is closed
WARNING Error analyzing r/Startup_Ideas: error with request Session is closed
INFO Tool reddit_api executed successfully
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1122', 'agent_name': 'Technical Chart Agent', 'status': 'completed', 'progress': 11, 'current_step': 'Step 1/9: Identify stocks mentioned on Reddit with significant buzz.'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1122
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1122: completed (11%)
INFO Agent 1122 executing step 2/9: Filter the identified Reddit stocks to find those with high trading volume and recent price movements.
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1122', 'agent_name': 'Technical Chart Agent', 'status': 'working', 'progress': 23, 'current_step': 'Executing step 2/9: Filter the identified Reddit stocks to find those ...'}
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1122: working (23%)
INFO WebSocket consumer sent message to client: agent_progress for agent 1122
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO 🔧 EXECUTING TOOL CALL: reddit_api with params: {'subreddits': ['SecurityAnalysis', 'ValueInvesting', 'stocks', 'pennystocks', 'Biotechplays', 'SPACs', 'investing', 'StockMarket', 'RobinHoodPennyStocks', 'smallstreetbets'], 'limit': 25, 'sort': 'hot'}
INFO Applied parameter mappings for reddit_api: {'subreddit': ['SecurityAnalysis', 'ValueInvesting', 'stocks', 'pennystocks', 'Biotechplays', 'SPACs', 'investing', 'StockMarket', 'RobinHoodPennyStocks', 'smallstreetbets'], 'limit': 25, 'sort': 'hot'}
INFO Executing tool: reddit_api with validated parameters: {'subreddit': ['SecurityAnalysis', 'ValueInvesting', 'stocks', 'pennystocks', 'Biotechplays', 'SPACs', 'investing', 'StockMarket', 'RobinHoodPennyStocks', 'smallstreetbets'], 'limit': 25, 'sort': 'hot'}
INFO Reddit API clients initialized successfully
WARNING Error fetching from r/['SecurityAnalysis', 'ValueInvesting', 'stocks', 'pennystocks', 'Biotechplays', 'SPACs', 'investing', 'StockMarket', 'RobinHoodPennyStocks', 'smallstreetbets']: 'list' object has no attribute 'lower'
WARNING Error analyzing r/Entrepreneur: error with request Session is closed
WARNING Error analyzing r/startups: error with request Session is closed
WARNING Error analyzing r/SaaS: error with request Session is closed
WARNING Error analyzing r/Business_Ideas: error with request Session is closed
WARNING Error analyzing r/Startup_Ideas: error with request Session is closed
INFO Tool reddit_api executed successfully
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1119', 'agent_name': 'Market Sentiment Agent', 'status': 'completed', 'progress': 10, 'current_step': 'Step 1/10: Gather initial list of frequently mentioned tickers across 10 investing subreddits'}
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1119: completed (10%)
INFO WebSocket consumer sent message to client: agent_progress for agent 1119
INFO Agent 1119 executing step 2/10: Analyze sentiment for each ticker mentioned 3+ times with increasing frequency
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1119', 'agent_name': 'Market Sentiment Agent', 'status': 'working', 'progress': 23, 'current_step': 'Executing step 2/10: Analyze sentiment for each ticker mentioned 3+ tim...'}
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1119: working (23%)
INFO WebSocket consumer sent message to client: agent_progress for agent 1119
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO 🔧 EXECUTING TOOL CALL: news_api with params: {'query': 'stock market', 'sources': 'Bloomberg,Reuters,MarketWatch', 'from': '2025-07-09', 'to': '2025-07-10', 'language': 'en'}
INFO Applied parameter mappings for news_api: {'query': 'stock market', 'sources': 'Bloomberg,Reuters,MarketWatch', 'from': '2025-07-09', 'to': '2025-07-10', 'language': 'en'}
INFO Filtered out parameters for news_api: {'language', 'to', 'sources', 'from'}
INFO Executing tool: news_api with validated parameters: {'query': 'stock market'}
ERROR News API error: 'NewsAPIService' object does not support the asynchronous context manager protocol
INFO Tool news_api executed successfully
WARNING Tool news_api returned error: 'NewsAPIService' object does not support the asynchronous context manager protocol
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1121: error (12%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1121', 'agent_name': 'News Catalyst Agent', 'status': 'error', 'progress': 12, 'current_step': 'Step 1/8: Scan major financial news sources for the latest market trends, significant stock movements, and major corporate announcements.'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1121
INFO Agent 1121 executing step 2/8: Check for pre-market and after-hours movers by analyzing stock price movements and trading volumes.
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1121: working (25%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1121', 'agent_name': 'News Catalyst Agent', 'status': 'working', 'progress': 25, 'current_step': 'Executing step 2/8: Check for pre-market and after-hours movers by ana...'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1121
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO 🔧 EXECUTING TOOL CALL: yahoo_finance with params: {'function': 'get_premarket_movers'}
INFO Filtered out parameters for yahoo_finance: {'function'}
INFO Executing tool: yahoo_finance with validated parameters: {}
ERROR Parameter mismatch for yahoo_finance: EnhancedAgentTools.yahoo_finance() missing 1 required positional argument: 'symbol'
INFO Retrying yahoo_finance with minimal parameters
WARNING Tool yahoo_finance returned error: EnhancedAgentTools.yahoo_finance() missing 1 required positional argument: 'symbol'
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1121', 'agent_name': 'News Catalyst Agent', 'status': 'error', 'progress': 25, 'current_step': 'Step 2/8: Check for pre-market and after-hours movers by analyzing stock price movements and trading volumes.'}
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1121: error (25%)
INFO WebSocket consumer sent message to client: agent_progress for agent 1121
INFO Agent 1121 executing step 3/8: Identify stocks with recent news catalysts by correlating news articles with stock movements.
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1121', 'agent_name': 'News Catalyst Agent', 'status': 'working', 'progress': 35, 'current_step': 'Executing step 3/8: Identify stocks with recent news catalysts by corr...'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1121
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1121: working (35%)
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO 🔧 EXECUTING TOOL CALL: reddit_api with params: {'subreddits': ['SecurityAnalysis', 'ValueInvesting', 'stocks', 'pennystocks', 'Biotechplays', 'SPACs', 'investing', 'StockMarket', 'RobinHoodPennyStocks', 'smallstreetbets'], 'limit': 25, 'sort': 'hot'}
INFO Applied parameter mappings for reddit_api: {'subreddit': ['SecurityAnalysis', 'ValueInvesting', 'stocks', 'pennystocks', 'Biotechplays', 'SPACs', 'investing', 'StockMarket', 'RobinHoodPennyStocks', 'smallstreetbets'], 'limit': 25, 'sort': 'hot'}
INFO Executing tool: reddit_api with validated parameters: {'subreddit': ['SecurityAnalysis', 'ValueInvesting', 'stocks', 'pennystocks', 'Biotechplays', 'SPACs', 'investing', 'StockMarket', 'RobinHoodPennyStocks', 'smallstreetbets'], 'limit': 25, 'sort': 'hot'}
INFO Reddit API clients initialized successfully
WARNING Error fetching from r/['SecurityAnalysis', 'ValueInvesting', 'stocks', 'pennystocks', 'Biotechplays', 'SPACs', 'investing', 'StockMarket', 'RobinHoodPennyStocks', 'smallstreetbets']: 'list' object has no attribute 'lower'
WARNING Error analyzing r/Entrepreneur: error with request Session is closed
WARNING Error analyzing r/startups: error with request Session is closed
WARNING Error analyzing r/SaaS: error with request Session is closed
WARNING Error analyzing r/Business_Ideas: error with request Session is closed
WARNING Error analyzing r/Startup_Ideas: error with request Session is closed
INFO Tool reddit_api executed successfully
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1119', 'agent_name': 'Market Sentiment Agent', 'status': 'completed', 'progress': 20, 'current_step': 'Step 2/10: Analyze sentiment for each ticker mentioned 3+ times with increasing frequency'}
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1119: completed (20%)
INFO WebSocket consumer sent message to client: agent_progress for agent 1119
INFO Agent 1119 executing step 3/10: Identify high-quality DD (due diligence) posts from credible users for tickers with positive sentiment
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1119', 'agent_name': 'Market Sentiment Agent', 'status': 'working', 'progress': 31, 'current_step': 'Executing step 3/10: Identify high-quality DD (due diligence) posts fro...'}
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1119: working (31%)
INFO WebSocket consumer sent message to client: agent_progress for agent 1119
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1122', 'agent_name': 'Technical Chart Agent', 'status': 'completed', 'progress': 22, 'current_step': 'Step 2/9: Filter the identified Reddit stocks to find those with high trading volume and recent price movements.'}
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1122: completed (22%)
INFO WebSocket consumer sent message to client: agent_progress for agent 1122
INFO Agent 1122 executing step 3/9: Perform chart pattern recognition on the filtered stocks to identify potential breakout setups.
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1122', 'agent_name': 'Technical Chart Agent', 'status': 'working', 'progress': 32, 'current_step': 'Executing step 3/9: Perform chart pattern recognition on the filtered ...'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1122
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1122: working (32%)
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO 🔧 EXECUTING TOOL CALL: sec_edgar_api with params: {'symbol': 'AAPL', 'type': ['10-Q', '10-K']}
INFO Filtered out parameters for sec_edgar_api: {'type'}
INFO Executing tool: sec_edgar_api with validated parameters: {'symbol': 'AAPL'}
ERROR SEC EDGAR API error: 'SECAPIService' object does not support the asynchronous context manager protocol
INFO Tool sec_edgar_api executed successfully
WARNING Tool sec_edgar_api returned error: 'SECAPIService' object does not support the asynchronous context manager protocol
INFO 🔧 EXECUTING TOOL CALL: sec_edgar_api with params: {'symbol': 'MRNA', 'type': ['10-Q', '10-K']}
INFO Filtered out parameters for sec_edgar_api: {'type'}
INFO Executing tool: sec_edgar_api with validated parameters: {'symbol': 'MRNA'}
ERROR SEC EDGAR API error: 'SECAPIService' object does not support the asynchronous context manager protocol
INFO Tool sec_edgar_api executed successfully
WARNING Tool sec_edgar_api returned error: 'SECAPIService' object does not support the asynchronous context manager protocol
INFO 🔧 EXECUTING TOOL CALL: sec_edgar_api with params: {'symbol': 'PG', 'type': ['10-Q', '10-K']}
INFO Filtered out parameters for sec_edgar_api: {'type'}
INFO Executing tool: sec_edgar_api with validated parameters: {'symbol': 'PG'}
ERROR SEC EDGAR API error: 'SECAPIService' object does not support the asynchronous context manager protocol
INFO Tool sec_edgar_api executed successfully
WARNING Tool sec_edgar_api returned error: 'SECAPIService' object does not support the asynchronous context manager protocol
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1120: error (60%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1120', 'agent_name': 'Fundamental Value Agent', 'status': 'error', 'progress': 60, 'current_step': 'Step 3/5: Review the latest 10-Q and 10-K filings for hidden gems such as unusual balance sheet improvements, patent filings, or FDA submissions.'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1120
INFO Agent 1120 executing step 4/5: Identify unusual institutional activity by examining the latest 13F filings, looking for significant changes in institutional holdings.
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1120: working (63%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1120', 'agent_name': 'Fundamental Value Agent', 'status': 'working', 'progress': 63, 'current_step': 'Executing step 4/5: Identify unusual institutional activity by examini...'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1120
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO 🔧 EXECUTING TOOL CALL: reddit_api with params: {'subreddits': ['SecurityAnalysis', 'ValueInvesting', 'stocks', 'pennystocks', 'Biotechplays', 'SPACs', 'investing', 'StockMarket', 'RobinHoodPennyStocks', 'smallstreetbets'], 'limit': 25, 'sort': 'hot'}
INFO Applied parameter mappings for reddit_api: {'subreddit': ['SecurityAnalysis', 'ValueInvesting', 'stocks', 'pennystocks', 'Biotechplays', 'SPACs', 'investing', 'StockMarket', 'RobinHoodPennyStocks', 'smallstreetbets'], 'limit': 25, 'sort': 'hot'}
INFO Executing tool: reddit_api with validated parameters: {'subreddit': ['SecurityAnalysis', 'ValueInvesting', 'stocks', 'pennystocks', 'Biotechplays', 'SPACs', 'investing', 'StockMarket', 'RobinHoodPennyStocks', 'smallstreetbets'], 'limit': 25, 'sort': 'hot'}
INFO Reddit API clients initialized successfully
WARNING Error fetching from r/['SecurityAnalysis', 'ValueInvesting', 'stocks', 'pennystocks', 'Biotechplays', 'SPACs', 'investing', 'StockMarket', 'RobinHoodPennyStocks', 'smallstreetbets']: 'list' object has no attribute 'lower'
WARNING Error analyzing r/Entrepreneur: error with request Session is closed
WARNING Error analyzing r/startups: error with request Session is closed
WARNING Error analyzing r/SaaS: error with request Session is closed
WARNING Error analyzing r/Business_Ideas: error with request Session is closed
WARNING Error analyzing r/Startup_Ideas: error with request Session is closed
INFO Tool reddit_api executed successfully
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1119: completed (30%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1119', 'agent_name': 'Market Sentiment Agent', 'status': 'completed', 'progress': 30, 'current_step': 'Step 3/10: Identify high-quality DD (due diligence) posts from credible users for tickers with positive sentiment'}
INFO Agent 1119 executing step 4/10: Spot unusual volume spikes in subreddit mentions and discussions
INFO WebSocket consumer sent message to client: agent_progress for agent 1119
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1119: working (39%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1119', 'agent_name': 'Market Sentiment Agent', 'status': 'working', 'progress': 39, 'current_step': 'Executing step 4/10: Spot unusual volume spikes in subreddit mentions a...'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1119
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO 🔧 EXECUTING TOOL CALL: sec_edgar_api with params: {'filing_types': ['13F'], 'date_range': {'start': '2025-01-01', 'end': '2025-07-10'}}
INFO 🔧 EXECUTING TOOL CALL: news_api with params: {'keywords': 'Tesla TSLA', 'date_from': '2025-07-01', 'date_to': '2025-07-10'}
WARNING sec_edgar_api called without symbol/company, using default SPY
INFO Filtered out parameters for sec_edgar_api: {'date_range', 'filing_types'}
INFO Executing tool: sec_edgar_api with validated parameters: {'symbol': 'SPY'}
ERROR SEC EDGAR API error: 'SECAPIService' object does not support the asynchronous context manager protocol
INFO Tool sec_edgar_api executed successfully
INFO Applied parameter mappings for news_api: {'query': 'Tesla TSLA', 'date_from': '2025-07-01', 'date_to': '2025-07-10'}
INFO Filtered out parameters for news_api: {'date_from', 'date_to'}
INFO Executing tool: news_api with validated parameters: {'query': 'Tesla TSLA'}
ERROR News API error: 'NewsAPIService' object does not support the asynchronous context manager protocol
INFO Tool news_api executed successfully
WARNING Tool sec_edgar_api returned error: 'SECAPIService' object does not support the asynchronous context manager protocol
WARNING Tool news_api returned error: 'NewsAPIService' object does not support the asynchronous context manager protocol
INFO 🔧 EXECUTING TOOL CALL: news_api with params: {'keywords': 'Nvidia NVDA', 'date_from': '2025-07-01', 'date_to': '2025-07-10'}
INFO Applied parameter mappings for news_api: {'query': 'Nvidia NVDA', 'date_from': '2025-07-01', 'date_to': '2025-07-10'}
INFO Filtered out parameters for news_api: {'date_from', 'date_to'}
INFO Executing tool: news_api with validated parameters: {'query': 'Nvidia NVDA'}
ERROR News API error: 'NewsAPIService' object does not support the asynchronous context manager protocol
INFO Tool news_api executed successfully
WARNING Tool news_api returned error: 'NewsAPIService' object does not support the asynchronous context manager protocol
INFO 🔧 EXECUTING TOOL CALL: news_api with params: {'keywords': 'Apple AAPL', 'date_from': '2025-07-01', 'date_to': '2025-07-10'}
INFO Applied parameter mappings for news_api: {'query': 'Apple AAPL', 'date_from': '2025-07-01', 'date_to': '2025-07-10'}
INFO Filtered out parameters for news_api: {'date_from', 'date_to'}
INFO Executing tool: news_api with validated parameters: {'query': 'Apple AAPL'}
ERROR News API error: 'NewsAPIService' object does not support the asynchronous context manager protocol
INFO Tool news_api executed successfully
WARNING Tool news_api returned error: 'NewsAPIService' object does not support the asynchronous context manager protocol
INFO 🔧 EXECUTING TOOL CALL: news_api with params: {'keywords': 'GameStop GME', 'date_from': '2025-07-01', 'date_to': '2025-07-10'}
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1120', 'agent_name': 'Fundamental Value Agent', 'status': 'error', 'progress': 80, 'current_step': 'Step 4/5: Identify unusual institutional activity by examining the latest 13F filings, looking for significant changes in institutional holdings.'}
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1120: error (80%)
INFO WebSocket consumer sent message to client: agent_progress for agent 1120
INFO Agent 1120 executing step 5/5: Cross-reference Reddit mentions to validate findings from SEC filings and gauge public sentiment around these activities.
INFO Applied parameter mappings for news_api: {'query': 'GameStop GME', 'date_from': '2025-07-01', 'date_to': '2025-07-10'}
INFO Filtered out parameters for news_api: {'date_from', 'date_to'}
INFO Executing tool: news_api with validated parameters: {'query': 'GameStop GME'}
ERROR News API error: 'NewsAPIService' object does not support the asynchronous context manager protocol
INFO Tool news_api executed successfully
WARNING Tool news_api returned error: 'NewsAPIService' object does not support the asynchronous context manager protocol
INFO 🔧 EXECUTING TOOL CALL: news_api with params: {'keywords': 'AMC Entertainment AMC', 'date_from': '2025-07-01', 'date_to': '2025-07-10'}
INFO Applied parameter mappings for news_api: {'query': 'AMC Entertainment AMC', 'date_from': '2025-07-01', 'date_to': '2025-07-10'}
INFO Filtered out parameters for news_api: {'date_from', 'date_to'}
INFO Executing tool: news_api with validated parameters: {'query': 'AMC Entertainment AMC'}
ERROR News API error: 'NewsAPIService' object does not support the asynchronous context manager protocol
INFO Tool news_api executed successfully
WARNING Tool news_api returned error: 'NewsAPIService' object does not support the asynchronous context manager protocol
INFO 🔧 EXECUTING TOOL CALL: news_api with params: {'keywords': 'Palantir PLTR', 'date_from': '2025-07-01', 'date_to': '2025-07-10'}
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1120: working (79%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1120', 'agent_name': 'Fundamental Value Agent', 'status': 'working', 'progress': 79, 'current_step': 'Executing step 5/5: Cross-reference Reddit mentions to validate findin...'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1120
INFO Applied parameter mappings for news_api: {'query': 'Palantir PLTR', 'date_from': '2025-07-01', 'date_to': '2025-07-10'}
INFO Filtered out parameters for news_api: {'date_from', 'date_to'}
INFO Executing tool: news_api with validated parameters: {'query': 'Palantir PLTR'}
ERROR News API error: 'NewsAPIService' object does not support the asynchronous context manager protocol
INFO Tool news_api executed successfully
WARNING Tool news_api returned error: 'NewsAPIService' object does not support the asynchronous context manager protocol
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1123', 'agent_name': 'Stock Synthesis Agent', 'status': 'error', 'progress': 42, 'current_step': 'Step 3/7: Search for recent news articles related to the identified stocks to find any potential catalysts that could affect stock prices.'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1123
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1123: error (42%)
INFO Agent 1123 executing step 4/7: Perform technical analysis on the identified stocks to evaluate their current technical setup and identify entry/exit points.
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1123: working (49%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1123', 'agent_name': 'Stock Synthesis Agent', 'status': 'working', 'progress': 49, 'current_step': 'Executing step 4/7: Perform technical analysis on the identified stock...'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1123
127.0.0.1:53694 - - [10/Jul/2025:18:18:09] "GET /api/agent-orchestra/command-center/stats/" 200 130
127.0.0.1:53694 - - [10/Jul/2025:18:18:10] "GET /api/agent-orchestra/orchestrations/?show_all=true" 200 1829359
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO 🔧 EXECUTING TOOL CALL: reddit_api with params: {'subreddits': ['SecurityAnalysis', 'ValueInvesting', 'stocks', 'pennystocks', 'Biotechplays', 'SPACs', 'investing', 'StockMarket', 'RobinHoodPennyStocks', 'smallstreetbets'], 'limit': 25, 'sort': 'hot'}
INFO Applied parameter mappings for reddit_api: {'subreddit': ['SecurityAnalysis', 'ValueInvesting', 'stocks', 'pennystocks', 'Biotechplays', 'SPACs', 'investing', 'StockMarket', 'RobinHoodPennyStocks', 'smallstreetbets'], 'limit': 25, 'sort': 'hot'}
INFO Executing tool: reddit_api with validated parameters: {'subreddit': ['SecurityAnalysis', 'ValueInvesting', 'stocks', 'pennystocks', 'Biotechplays', 'SPACs', 'investing', 'StockMarket', 'RobinHoodPennyStocks', 'smallstreetbets'], 'limit': 25, 'sort': 'hot'}
INFO Reddit API clients initialized successfully
WARNING Error fetching from r/['SecurityAnalysis', 'ValueInvesting', 'stocks', 'pennystocks', 'Biotechplays', 'SPACs', 'investing', 'StockMarket', 'RobinHoodPennyStocks', 'smallstreetbets']: 'list' object has no attribute 'lower'
WARNING Error analyzing r/Entrepreneur: error with request Session is closed
WARNING Error analyzing r/startups: error with request Session is closed
WARNING Error analyzing r/SaaS: error with request Session is closed
WARNING Error analyzing r/Business_Ideas: error with request Session is closed
WARNING Error analyzing r/Startup_Ideas: error with request Session is closed
INFO Tool reddit_api executed successfully
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1119: completed (40%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1119', 'agent_name': 'Market Sentiment Agent', 'status': 'completed', 'progress': 40, 'current_step': 'Step 4/10: Spot unusual volume spikes in subreddit mentions and discussions'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1119
INFO Agent 1119 executing step 5/10: Filter out stocks with potential for mainstream attention by analyzing catalyst discussions
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1119: working (47%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1119', 'agent_name': 'Market Sentiment Agent', 'status': 'working', 'progress': 47, 'current_step': 'Executing step 5/10: Filter out stocks with potential for mainstream at...'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1119
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO 🔧 EXECUTING TOOL CALL: reddit_api with params: {'subreddits': ['SecurityAnalysis', 'ValueInvesting', 'stocks', 'pennystocks', 'Biotechplays', 'SPACs', 'investing', 'StockMarket', 'RobinHoodPennyStocks', 'smallstreetbets'], 'limit': 25, 'sort': 'hot'}
INFO Applied parameter mappings for reddit_api: {'subreddit': ['SecurityAnalysis', 'ValueInvesting', 'stocks', 'pennystocks', 'Biotechplays', 'SPACs', 'investing', 'StockMarket', 'RobinHoodPennyStocks', 'smallstreetbets'], 'limit': 25, 'sort': 'hot'}
INFO Executing tool: reddit_api with validated parameters: {'subreddit': ['SecurityAnalysis', 'ValueInvesting', 'stocks', 'pennystocks', 'Biotechplays', 'SPACs', 'investing', 'StockMarket', 'RobinHoodPennyStocks', 'smallstreetbets'], 'limit': 25, 'sort': 'hot'}
INFO Reddit API clients initialized successfully
WARNING Error fetching from r/['SecurityAnalysis', 'ValueInvesting', 'stocks', 'pennystocks', 'Biotechplays', 'SPACs', 'investing', 'StockMarket', 'RobinHoodPennyStocks', 'smallstreetbets']: 'list' object has no attribute 'lower'
WARNING Error analyzing r/Entrepreneur: error with request Session is closed
WARNING Error analyzing r/startups: error with request Session is closed
WARNING Error analyzing r/SaaS: error with request Session is closed
WARNING Error analyzing r/Business_Ideas: error with request Session is closed
WARNING Error analyzing r/Startup_Ideas: error with request Session is closed
INFO Tool reddit_api executed successfully
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1119: completed (50%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1119', 'agent_name': 'Market Sentiment Agent', 'status': 'completed', 'progress': 50, 'current_step': 'Step 5/10: Filter out stocks with potential for mainstream attention by analyzing catalyst discussions'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1119
INFO Agent 1119 executing step 6/10: Avoid stocks involved in obvious pump & dump schemes or coordinated campaigns by assessing the nature of discussions and user history
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1119: working (55%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1119', 'agent_name': 'Market Sentiment Agent', 'status': 'working', 'progress': 55, 'current_step': 'Executing step 6/10: Avoid stocks involved in obvious pump & dump schem...'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1119
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO 🔧 EXECUTING TOOL CALL: chart_creator with params: {'symbol': 'XYZ', 'pattern_recognition': 'breakout_setups'}
INFO Applied parameter mappings for chart_creator: {'symbol': 'XYZ', 'pattern_recognition': 'breakout_setups'}
INFO Filtered out parameters for chart_creator: {'symbol', 'pattern_recognition'}
INFO Executing tool: chart_creator with validated parameters: {'data': {'title': 'Stock Analysis Chart', 'x_labels': ['T-4', 'T-3', 'T-2', 'T-1', 'Today'], 'y_values': [100, 102, 98, 105, 103]}, 'chart_type': 'line'}
INFO Tool chart_creator executed successfully
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1122', 'agent_name': 'Technical Chart Agent', 'status': 'completed', 'progress': 33, 'current_step': 'Step 3/9: Perform chart pattern recognition on the filtered stocks to identify potential breakout setups.'}
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1122: completed (33%)
INFO WebSocket consumer sent message to client: agent_progress for agent 1122
INFO Agent 1122 executing step 4/9: Analyze support and resistance levels for each stock with potential breakout patterns.
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1122: working (41%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1122', 'agent_name': 'Technical Chart Agent', 'status': 'working', 'progress': 41, 'current_step': 'Executing step 4/9: Analyze support and resistance levels for each sto...'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1122
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO 🔧 EXECUTING TOOL CALL: news_api with params: {'query': 'stock market', 'sources': 'Bloomberg,Reuters,MarketWatch,PR Newswire,Business Wire', 'language': 'en', 'sortBy': 'publishedAt'}
INFO Applied parameter mappings for news_api: {'query': 'stock market', 'sources': 'Bloomberg,Reuters,MarketWatch,PR Newswire,Business Wire', 'language': 'en', 'sortBy': 'publishedAt'}
INFO Filtered out parameters for news_api: {'sortBy', 'language', 'sources'}
INFO Executing tool: news_api with validated parameters: {'query': 'stock market'}
ERROR News API error: 'NewsAPIService' object does not support the asynchronous context manager protocol
INFO Tool news_api executed successfully
WARNING Tool news_api returned error: 'NewsAPIService' object does not support the asynchronous context manager protocol
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1121: error (37%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1121', 'agent_name': 'News Catalyst Agent', 'status': 'error', 'progress': 37, 'current_step': 'Step 3/8: Identify stocks with recent news catalysts by correlating news articles with stock movements.'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1121
INFO Agent 1121 executing step 4/8: Find 'under the radar' stories by searching for news on smaller or less covered companies that may have significant developments.
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1121: working (45%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1121', 'agent_name': 'News Catalyst Agent', 'status': 'working', 'progress': 45, 'current_step': "Executing step 4/8: Find 'under the radar' stories by searching for ne..."}
INFO WebSocket consumer sent message to client: agent_progress for agent 1121
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1121: completed (50%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1121', 'agent_name': 'News Catalyst Agent', 'status': 'completed', 'progress': 50, 'current_step': "Step 4/8: Find 'under the radar' stories by searching for news on smaller or less covered companies that may have significant developments."}
INFO Agent 1121 executing step 5/8: Match Reddit buzz with real news to validate investment opportunities by analyzing sentiment and discussion volume.
INFO WebSocket consumer sent message to client: agent_progress for agent 1121
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1121: working (55%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1121', 'agent_name': 'News Catalyst Agent', 'status': 'working', 'progress': 55, 'current_step': 'Executing step 5/8: Match Reddit buzz with real news to validate inves...'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1121
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO 🔧 EXECUTING TOOL CALL: reddit_api with params: {'subreddits': ['SecurityAnalysis', 'ValueInvesting', 'stocks', 'pennystocks', 'Biotechplays', 'SPACs', 'investing', 'StockMarket', 'RobinHoodPennyStocks', 'smallstreetbets'], 'limit': 100, 'sort': 'hot'}
INFO Applied parameter mappings for reddit_api: {'subreddit': ['SecurityAnalysis', 'ValueInvesting', 'stocks', 'pennystocks', 'Biotechplays', 'SPACs', 'investing', 'StockMarket', 'RobinHoodPennyStocks', 'smallstreetbets'], 'limit': 100, 'sort': 'hot'}
INFO Executing tool: reddit_api with validated parameters: {'subreddit': ['SecurityAnalysis', 'ValueInvesting', 'stocks', 'pennystocks', 'Biotechplays', 'SPACs', 'investing', 'StockMarket', 'RobinHoodPennyStocks', 'smallstreetbets'], 'limit': 100, 'sort': 'hot'}
INFO Reddit API clients initialized successfully
WARNING Error fetching from r/['SecurityAnalysis', 'ValueInvesting', 'stocks', 'pennystocks', 'Biotechplays', 'SPACs', 'investing', 'StockMarket', 'RobinHoodPennyStocks', 'smallstreetbets']: 'list' object has no attribute 'lower'
WARNING Error analyzing r/Entrepreneur: error with request Session is closed
WARNING Error analyzing r/startups: error with request Session is closed
WARNING Error analyzing r/SaaS: error with request Session is closed
WARNING Error analyzing r/Business_Ideas: error with request Session is closed
WARNING Error analyzing r/Startup_Ideas: error with request Session is closed
INFO Tool reddit_api executed successfully
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1119', 'agent_name': 'Market Sentiment Agent', 'status': 'completed', 'progress': 60, 'current_step': 'Step 6/10: Avoid stocks involved in obvious pump & dump schemes or coordinated campaigns by assessing the nature of discussions and user history'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1119
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1119: completed (60%)
INFO Agent 1119 executing step 7/10: Compile the top 10 opportunities based on sentiment scores, mention velocity, and quality of DD posts
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1119', 'agent_name': 'Market Sentiment Agent', 'status': 'working', 'progress': 63, 'current_step': 'Executing step 7/10: Compile the top 10 opportunities based on sentimen...'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1119
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1119: working (63%)
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO 🔧 EXECUTING TOOL CALL: polygon_market_data with params: {'ticker': 'TSLA', 'analysis_type': 'technical'}
INFO Applied parameter mappings for polygon_market_data: {'symbol': 'TSLA', 'analysis_type': 'technical'}
INFO Filtered out parameters for polygon_market_data: {'analysis_type'}
INFO Executing tool: polygon_market_data with validated parameters: {'symbol': 'TSLA'}
INFO Polygon S3 client initialized successfully
ERROR Task exception was never retrieved
future: <Task finished name='Task-2935' coro=<AsyncClient.aclose() done, defined at /Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpx/_client.py:1978> exception=RuntimeError('Event loop is closed')>
Traceback (most recent call last):
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpx/_client.py", line 1985, in aclose
    await self._transport.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpx/_transports/default.py", line 406, in aclose
    await self._pool.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/connection_pool.py", line 353, in aclose
    await self._close_connections(closing_connections)
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/connection_pool.py", line 345, in _close_connections
    await connection.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/connection.py", line 173, in aclose
    await self._connection.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/http11.py", line 258, in aclose
    await self._network_stream.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_backends/anyio.py", line 53, in aclose
    await self._stream.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/anyio/streams/tls.py", line 216, in aclose
    await self.transport_stream.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/anyio/_backends/_asyncio.py", line 1314, in aclose
    self._transport.close()
  File "/Users/donkeyking/.pyenv/versions/3.11.6/lib/python3.11/asyncio/selector_events.py", line 860, in close
    self._loop.call_soon(self._call_connection_lost, None)
  File "/Users/donkeyking/.pyenv/versions/3.11.6/lib/python3.11/asyncio/base_events.py", line 761, in call_soon
    self._check_closed()
  File "/Users/donkeyking/.pyenv/versions/3.11.6/lib/python3.11/asyncio/base_events.py", line 519, in _check_closed
    raise RuntimeError('Event loop is closed')
RuntimeError: Event loop is closed
ERROR Task exception was never retrieved
future: <Task finished name='Task-2936' coro=<AsyncClient.aclose() done, defined at /Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpx/_client.py:1978> exception=RuntimeError('Event loop is closed')>
Traceback (most recent call last):
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpx/_client.py", line 1985, in aclose
    await self._transport.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpx/_transports/default.py", line 406, in aclose
    await self._pool.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/connection_pool.py", line 353, in aclose
    await self._close_connections(closing_connections)
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/connection_pool.py", line 345, in _close_connections
    await connection.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/connection.py", line 173, in aclose
    await self._connection.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/http11.py", line 258, in aclose
    await self._network_stream.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_backends/anyio.py", line 53, in aclose
    await self._stream.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/anyio/streams/tls.py", line 216, in aclose
    await self.transport_stream.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/anyio/_backends/_asyncio.py", line 1314, in aclose
    self._transport.close()
  File "/Users/donkeyking/.pyenv/versions/3.11.6/lib/python3.11/asyncio/selector_events.py", line 860, in close
    self._loop.call_soon(self._call_connection_lost, None)
  File "/Users/donkeyking/.pyenv/versions/3.11.6/lib/python3.11/asyncio/base_events.py", line 761, in call_soon
    self._check_closed()
  File "/Users/donkeyking/.pyenv/versions/3.11.6/lib/python3.11/asyncio/base_events.py", line 519, in _check_closed
    raise RuntimeError('Event loop is closed')
RuntimeError: Event loop is closed
INFO Tool polygon_market_data executed successfully
INFO 🔧 EXECUTING TOOL CALL: polygon_market_data with params: {'ticker': 'NVDA', 'analysis_type': 'technical'}
INFO Applied parameter mappings for polygon_market_data: {'symbol': 'NVDA', 'analysis_type': 'technical'}
INFO Filtered out parameters for polygon_market_data: {'analysis_type'}
INFO Executing tool: polygon_market_data with validated parameters: {'symbol': 'NVDA'}
INFO Polygon S3 client initialized successfully
INFO Tool polygon_market_data executed successfully
INFO 🔧 EXECUTING TOOL CALL: polygon_market_data with params: {'ticker': 'AAPL', 'analysis_type': 'technical'}
INFO Applied parameter mappings for polygon_market_data: {'symbol': 'AAPL', 'analysis_type': 'technical'}
INFO Filtered out parameters for polygon_market_data: {'analysis_type'}
INFO Executing tool: polygon_market_data with validated parameters: {'symbol': 'AAPL'}
INFO Polygon S3 client initialized successfully
INFO Tool polygon_market_data executed successfully
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1123', 'agent_name': 'Stock Synthesis Agent', 'status': 'completed', 'progress': 57, 'current_step': 'Step 4/7: Perform technical analysis on the identified stocks to evaluate their current technical setup and identify entry/exit points.'}
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1123: completed (57%)
INFO WebSocket consumer sent message to client: agent_progress for agent 1123
INFO Agent 1123 executing step 5/7: Calculate a unified scoring for each stock based on the collected data, factoring in Reddit buzz, financial health, news catalysts, and technical setup.
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1123: working (60%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1123', 'agent_name': 'Stock Synthesis Agent', 'status': 'working', 'progress': 60, 'current_step': 'Executing step 5/7: Calculate a unified scoring for each stock based o...'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1123
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1122: completed (44%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1122', 'agent_name': 'Technical Chart Agent', 'status': 'completed', 'progress': 44, 'current_step': 'Step 4/9: Analyze support and resistance levels for each stock with potential breakout patterns.'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1122
INFO Agent 1122 executing step 5/9: Conduct volume analysis to spot unusual spikes that may precede price movements.
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1122: working (50%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1122', 'agent_name': 'Technical Chart Agent', 'status': 'working', 'progress': 50, 'current_step': 'Executing step 5/9: Conduct volume analysis to spot unusual spikes tha...'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1122
127.0.0.1:53694 - - [10/Jul/2025:18:18:39] "GET /api/agent-orchestra/command-center/stats/" 200 130
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO 🔧 EXECUTING TOOL CALL: reddit_api with params: {'query': 'Company A CEO buying shares', 'subreddits': ['stocks', 'investing', 'WallStreetBets'], 'after': '2025-01-01', 'before': '2025-07-10'}
WARNING Unknown parameter 'query' for tool reddit_api
WARNING Unknown parameter 'after' for tool reddit_api
WARNING Unknown parameter 'before' for tool reddit_api
INFO Applied parameter mappings for reddit_api: {'query': 'Company A CEO buying shares', 'subreddit': ['stocks', 'investing', 'WallStreetBets'], 'after': '2025-01-01', 'before': '2025-07-10'}
INFO Filtered out parameters for reddit_api: {'before', 'query', 'after'}
INFO Executing tool: reddit_api with validated parameters: {'subreddit': ['stocks', 'investing', 'WallStreetBets']}
INFO Reddit API clients initialized successfully
WARNING Error fetching from r/['stocks', 'investing', 'WallStreetBets']: 'list' object has no attribute 'lower'
WARNING Error analyzing r/Entrepreneur: error with request Session is closed
WARNING Error analyzing r/startups: error with request Session is closed
WARNING Error analyzing r/SaaS: error with request Session is closed
WARNING Error analyzing r/Business_Ideas: error with request Session is closed
WARNING Error analyzing r/Startup_Ideas: error with request Session is closed
INFO Tool reddit_api executed successfully
INFO 🔧 EXECUTING TOOL CALL: reddit_api with params: {'query': 'Company B new partnership', 'subreddits': ['stocks', 'investing', 'WallStreetBets'], 'after': '2025-01-01', 'before': '2025-07-10'}
WARNING Unknown parameter 'query' for tool reddit_api
WARNING Unknown parameter 'after' for tool reddit_api
WARNING Unknown parameter 'before' for tool reddit_api
INFO Applied parameter mappings for reddit_api: {'query': 'Company B new partnership', 'subreddit': ['stocks', 'investing', 'WallStreetBets'], 'after': '2025-01-01', 'before': '2025-07-10'}
INFO Filtered out parameters for reddit_api: {'before', 'query', 'after'}
INFO Executing tool: reddit_api with validated parameters: {'subreddit': ['stocks', 'investing', 'WallStreetBets']}
INFO Reddit API clients initialized successfully
WARNING Error fetching from r/['stocks', 'investing', 'WallStreetBets']: 'list' object has no attribute 'lower'
WARNING Error analyzing r/Entrepreneur: error with request Session is closed
WARNING Error analyzing r/startups: error with request Session is closed
WARNING Error analyzing r/SaaS: error with request Session is closed
WARNING Error analyzing r/Business_Ideas: error with request Session is closed
WARNING Error analyzing r/Startup_Ideas: error with request Session is closed
INFO Tool reddit_api executed successfully
INFO 🔧 EXECUTING TOOL CALL: reddit_api with params: {'query': 'Company C patent FDA submission', 'subreddits': ['stocks', 'investing', 'WallStreetBets'], 'after': '2025-01-01', 'before': '2025-07-10'}
WARNING Unknown parameter 'query' for tool reddit_api
WARNING Unknown parameter 'after' for tool reddit_api
WARNING Unknown parameter 'before' for tool reddit_api
INFO Applied parameter mappings for reddit_api: {'query': 'Company C patent FDA submission', 'subreddit': ['stocks', 'investing', 'WallStreetBets'], 'after': '2025-01-01', 'before': '2025-07-10'}
INFO Filtered out parameters for reddit_api: {'before', 'query', 'after'}
INFO Executing tool: reddit_api with validated parameters: {'subreddit': ['stocks', 'investing', 'WallStreetBets']}
INFO Reddit API clients initialized successfully
WARNING Error fetching from r/['stocks', 'investing', 'WallStreetBets']: 'list' object has no attribute 'lower'
WARNING Error analyzing r/Entrepreneur: error with request Session is closed
WARNING Error analyzing r/startups: error with request Session is closed
WARNING Error analyzing r/SaaS: error with request Session is closed
WARNING Error analyzing r/Business_Ideas: error with request Session is closed
WARNING Error analyzing r/Startup_Ideas: error with request Session is closed
INFO Tool reddit_api executed successfully
INFO 🔧 EXECUTING TOOL CALL: reddit_api with params: {'query': 'Company D balance sheet', 'subreddits': ['stocks', 'investing', 'WallStreetBets'], 'after': '2025-01-01', 'before': '2025-07-10'}
WARNING Unknown parameter 'query' for tool reddit_api
WARNING Unknown parameter 'after' for tool reddit_api
WARNING Unknown parameter 'before' for tool reddit_api
INFO Applied parameter mappings for reddit_api: {'query': 'Company D balance sheet', 'subreddit': ['stocks', 'investing', 'WallStreetBets'], 'after': '2025-01-01', 'before': '2025-07-10'}
INFO Filtered out parameters for reddit_api: {'before', 'query', 'after'}
INFO Executing tool: reddit_api with validated parameters: {'subreddit': ['stocks', 'investing', 'WallStreetBets']}
INFO Reddit API clients initialized successfully
WARNING Error fetching from r/['stocks', 'investing', 'WallStreetBets']: 'list' object has no attribute 'lower'
WARNING Error analyzing r/Entrepreneur: error with request Session is closed
WARNING Error analyzing r/startups: error with request Session is closed
WARNING Error analyzing r/SaaS: error with request Session is closed
WARNING Error analyzing r/Business_Ideas: error with request Session is closed
WARNING Error analyzing r/Startup_Ideas: error with request Session is closed
INFO Tool reddit_api executed successfully
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1120: completed (100%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1120', 'agent_name': 'Fundamental Value Agent', 'status': 'completed', 'progress': 100, 'current_step': 'Step 5/5: Cross-reference Reddit mentions to validate findings from SEC filings and gauge public sentiment around these activities.'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1120
127.0.0.1:53694 - - [10/Jul/2025:18:18:41] "GET /api/agent-orchestra/orchestrations/?show_all=true" 200 1829426
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO 🔧 EXECUTING TOOL CALL: reddit_api with params: {'subreddit': 'wallstreetbets', 'query': 'top', 'time_filter': 'week'}
WARNING Unknown parameter 'query' for tool reddit_api
WARNING Unknown parameter 'time_filter' for tool reddit_api
INFO Applied parameter mappings for reddit_api: {'subreddit': 'wallstreetbets', 'query': 'top', 'time_filter': 'week'}
INFO Filtered out parameters for reddit_api: {'query', 'time_filter'}
INFO Executing tool: reddit_api with validated parameters: {'subreddit': 'wallstreetbets'}
INFO Reddit API clients initialized successfully
WARNING Error analyzing r/Entrepreneur: error with request Session is closed
WARNING Error analyzing r/startups: error with request Session is closed
WARNING Error analyzing r/SaaS: error with request Session is closed
WARNING Error analyzing r/Business_Ideas: error with request Session is closed
WARNING Error analyzing r/Startup_Ideas: error with request Session is closed
INFO Tool reddit_api executed successfully
INFO 🔧 EXECUTING TOOL CALL: sentiment_api with params: {'text': '[Text from Reddit discussions]'}
INFO Executing tool: sentiment_api with validated parameters: {'text': '[Text from Reddit discussions]'}
INFO Tool sentiment_api executed successfully
INFO 🔧 EXECUTING TOOL CALL: news_api with params: {'query': '[Stock ticker] news', 'domains': 'bloomberg.com,reuters.com,marketwatch.com', 'language': 'en', 'sort_by': 'relevancy'}
INFO Applied parameter mappings for news_api: {'query': '[Stock ticker] news', 'domains': 'bloomberg.com,reuters.com,marketwatch.com', 'language': 'en', 'sort_by': 'relevancy'}
INFO Filtered out parameters for news_api: {'sort_by', 'language', 'domains'}
INFO Executing tool: news_api with validated parameters: {'query': '[Stock ticker] news'}
ERROR News API error: 'NewsAPIService' object does not support the asynchronous context manager protocol
INFO Tool news_api executed successfully
WARNING Tool news_api returned error: 'NewsAPIService' object does not support the asynchronous context manager protocol
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1121: completed (62%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1121', 'agent_name': 'News Catalyst Agent', 'status': 'completed', 'progress': 62, 'current_step': 'Step 5/8: Match Reddit buzz with real news to validate investment opportunities by analyzing sentiment and discussion volume.'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1121
INFO Agent 1121 executing step 6/8: Flag stocks with high Reddit interest but no mainstream news coverage yet, indicating potential 'under the radar' opportunities.
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1121', 'agent_name': 'News Catalyst Agent', 'status': 'working', 'progress': 65, 'current_step': 'Executing step 6/8: Flag stocks with high Reddit interest but no mains...'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1121
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1121: working (65%)
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1122: completed (55%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1122', 'agent_name': 'Technical Chart Agent', 'status': 'completed', 'progress': 55, 'current_step': 'Step 5/9: Conduct volume analysis to spot unusual spikes that may precede price movements.'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1122
INFO Agent 1122 executing step 6/9: Evaluate momentum indicators, specifically RSI and MACD, to assess the strength of the current price trend.
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1122', 'agent_name': 'Technical Chart Agent', 'status': 'working', 'progress': 59, 'current_step': 'Executing step 6/9: Evaluate momentum indicators, specifically RSI and...'}
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1122: working (59%)
INFO WebSocket consumer sent message to client: agent_progress for agent 1122
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1122: completed (66%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1122', 'agent_name': 'Technical Chart Agent', 'status': 'completed', 'progress': 66, 'current_step': 'Step 6/9: Evaluate momentum indicators, specifically RSI and MACD, to assess the strength of the current price trend.'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1122
INFO Agent 1122 executing step 7/9: Analyze moving averages (50-day and 200-day) to understand the medium and long-term trend direction.
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1122: working (68%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1122', 'agent_name': 'Technical Chart Agent', 'status': 'working', 'progress': 68, 'current_step': 'Executing step 7/9: Analyze moving averages (50-day and 200-day) to un...'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1122
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1122', 'agent_name': 'Technical Chart Agent', 'status': 'completed', 'progress': 77, 'current_step': 'Step 7/9: Analyze moving averages (50-day and 200-day) to understand the medium and long-term trend direction.'}
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1122: completed (77%)
INFO WebSocket consumer sent message to client: agent_progress for agent 1122
INFO Agent 1122 executing step 8/9: Prioritize stocks for detailed technical analysis based on the combination of Reddit buzz, technical setup, and trading volume.
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1122', 'agent_name': 'Technical Chart Agent', 'status': 'working', 'progress': 77, 'current_step': 'Executing step 8/9: Prioritize stocks for detailed technical analysis ...'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1122
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1122: working (77%)
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO 🔧 EXECUTING TOOL CALL: reddit_api with params: {'subreddits': ['SecurityAnalysis', 'ValueInvesting', 'stocks', 'pennystocks', 'Biotechplays', 'SPACs', 'investing', 'StockMarket', 'RobinHoodPennyStocks', 'smallstreetbets'], 'limit': 100, 'sort': 'hot'}
INFO Applied parameter mappings for reddit_api: {'subreddit': ['SecurityAnalysis', 'ValueInvesting', 'stocks', 'pennystocks', 'Biotechplays', 'SPACs', 'investing', 'StockMarket', 'RobinHoodPennyStocks', 'smallstreetbets'], 'limit': 100, 'sort': 'hot'}
INFO Executing tool: reddit_api with validated parameters: {'subreddit': ['SecurityAnalysis', 'ValueInvesting', 'stocks', 'pennystocks', 'Biotechplays', 'SPACs', 'investing', 'StockMarket', 'RobinHoodPennyStocks', 'smallstreetbets'], 'limit': 100, 'sort': 'hot'}
INFO Reddit API clients initialized successfully
WARNING Error fetching from r/['SecurityAnalysis', 'ValueInvesting', 'stocks', 'pennystocks', 'Biotechplays', 'SPACs', 'investing', 'StockMarket', 'RobinHoodPennyStocks', 'smallstreetbets']: 'list' object has no attribute 'lower'
WARNING Error analyzing r/Entrepreneur: error with request Session is closed
WARNING Error analyzing r/startups: error with request Session is closed
WARNING Error analyzing r/SaaS: error with request Session is closed
WARNING Error analyzing r/Business_Ideas: error with request Session is closed
WARNING Error analyzing r/Startup_Ideas: error with request Session is closed
INFO Tool reddit_api executed successfully
INFO 🔧 EXECUTING TOOL CALL: sentiment_api with params: {'text': 'Placeholder for individual stock mentions text'}
INFO Executing tool: sentiment_api with validated parameters: {'text': 'Placeholder for individual stock mentions text'}
INFO Tool sentiment_api executed successfully
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1119: completed (70%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1119', 'agent_name': 'Market Sentiment Agent', 'status': 'completed', 'progress': 70, 'current_step': 'Step 7/10: Compile the top 10 opportunities based on sentiment scores, mention velocity, and quality of DD posts'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1119
INFO Agent 1119 executing step 8/10: Cross-reference Reddit findings with current news and market sentiment for additional context and verification
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1119: working (71%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1119', 'agent_name': 'Market Sentiment Agent', 'status': 'working', 'progress': 71, 'current_step': 'Executing step 8/10: Cross-reference Reddit findings with current news ...'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1119
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1123: completed (71%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1123', 'agent_name': 'Stock Synthesis Agent', 'status': 'completed', 'progress': 71, 'current_step': 'Step 5/7: Calculate a unified scoring for each stock based on the collected data, factoring in Reddit buzz, financial health, news catalysts, and technical setup.'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1123
INFO Agent 1123 executing step 6/7: Rank the identified investment opportunities by their overall score, prioritizing those with the highest potential and reasonable risk.
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1123: working (72%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1123', 'agent_name': 'Stock Synthesis Agent', 'status': 'working', 'progress': 72, 'current_step': 'Executing step 6/7: Rank the identified investment opportunities by th...'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1123
INFO 🔧 EXECUTING TOOL CALL: reddit_api with params: {'subreddit': 'wallstreetbets', 'query': 'stocks', 'sort': 'hot', 'limit': 10}
WARNING Unknown parameter 'query' for tool reddit_api
INFO Applied parameter mappings for reddit_api: {'subreddit': 'wallstreetbets', 'query': 'stocks', 'sort': 'hot', 'limit': 10}
INFO Filtered out parameters for reddit_api: {'query'}
INFO Executing tool: reddit_api with validated parameters: {'subreddit': 'wallstreetbets', 'sort': 'hot', 'limit': 10}
INFO Reddit API clients initialized successfully
WARNING Error analyzing r/Entrepreneur: error with request Session is closed
WARNING Error analyzing r/startups: error with request Session is closed
WARNING Error analyzing r/SaaS: error with request Session is closed
WARNING Error analyzing r/Business_Ideas: error with request Session is closed
WARNING Error analyzing r/Startup_Ideas: error with request Session is closed
INFO Tool reddit_api executed successfully
INFO 🔧 EXECUTING TOOL CALL: news_api with params: {'query': 'stock_symbol', 'sources': 'Bloomberg, Reuters, MarketWatch', 'from': '2025-07-01', 'to': '2025-07-10', 'language': 'en', 'sortBy': 'relevancy', 'pageSize': 5}
INFO Applied parameter mappings for news_api: {'query': 'stock_symbol', 'sources': 'Bloomberg, Reuters, MarketWatch', 'from': '2025-07-01', 'to': '2025-07-10', 'language': 'en', 'sortBy': 'relevancy', 'pageSize': 5}
INFO Filtered out parameters for news_api: {'to', 'language', 'from', 'sortBy', 'sources', 'pageSize'}
INFO Executing tool: news_api with validated parameters: {'query': 'stock_symbol'}
ERROR News API error: 'NewsAPIService' object does not support the asynchronous context manager protocol
INFO Tool news_api executed successfully
WARNING Tool news_api returned error: 'NewsAPIService' object does not support the asynchronous context manager protocol
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1121', 'agent_name': 'News Catalyst Agent', 'status': 'completed', 'progress': 75, 'current_step': "Step 6/8: Flag stocks with high Reddit interest but no mainstream news coverage yet, indicating potential 'under the radar' opportunities."}
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1121: completed (75%)
INFO WebSocket consumer sent message to client: agent_progress for agent 1121
INFO Agent 1121 executing step 7/8: For identified stocks, further analyze company fundamentals and recent developments through SEC filings.
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1121', 'agent_name': 'News Catalyst Agent', 'status': 'working', 'progress': 75, 'current_step': 'Executing step 7/8: For identified stocks, further analyze company fun...'}
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1121: working (75%)
INFO WebSocket consumer sent message to client: agent_progress for agent 1121
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO Generated enhanced report of 5407 characters with 10 API calls
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1120: completed_with_errors (100%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1120', 'agent_name': 'Fundamental Value Agent', 'status': 'completed_with_errors', 'progress': 100, 'current_step': 'Completed with 4 errors'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1120
127.0.0.1:53694 - - [10/Jul/2025:18:19:09] "GET /api/agent-orchestra/command-center/stats/" 200 130
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO 🔧 EXECUTING TOOL CALL: spreadsheet_generator with params: {'columns': ['Ticker Symbol', 'Reddit Mentions', 'Current Price', 'Volume Analysis', 'RSI', 'MACD', 'Moving Averages', 'Technical Score'], 'data': [['ExampleTicker1', '150 mentions', '$10.50', 'High spike', '65', 'Bullish crossover', 'Above both', '8/10'], ['ExampleTicker2', '120 mentions', '$5.30', 'Moderate spike', '30', 'Bearish crossover', 'Below 50-day', '6/10']]}
INFO Applied parameter mappings for spreadsheet_generator: {'columns': ['Ticker Symbol', 'Reddit Mentions', 'Current Price', 'Volume Analysis', 'RSI', 'MACD', 'Moving Averages', 'Technical Score'], 'data': [['ExampleTicker1', '150 mentions', '$10.50', 'High spike', '65', 'Bullish crossover', 'Above both', '8/10'], ['ExampleTicker2', '120 mentions', '$5.30', 'Moderate spike', '30', 'Bearish crossover', 'Below 50-day', '6/10']]}
INFO Filtered out parameters for spreadsheet_generator: {'columns', 'template'}
INFO Executing tool: spreadsheet_generator with validated parameters: {'data': [['ExampleTicker1', '150 mentions', '$10.50', 'High spike', '65', 'Bullish crossover', 'Above both', '8/10'], ['ExampleTicker2', '120 mentions', '$5.30', 'Moderate spike', '30', 'Bearish crossover', 'Below 50-day', '6/10']]}
ERROR Spreadsheet generator error: 'list' object has no attribute 'get'
INFO Tool spreadsheet_generator executed successfully
WARNING Tool spreadsheet_generator returned error: 'list' object has no attribute 'get'
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1122: error (88%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1122', 'agent_name': 'Technical Chart Agent', 'status': 'error', 'progress': 88, 'current_step': 'Step 8/9: Prioritize stocks for detailed technical analysis based on the combination of Reddit buzz, technical setup, and trading volume.'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1122
INFO Agent 1122 executing step 9/9: Create a detailed technical analysis report for each prioritized stock, combining all findings.
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1122: working (86%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1122', 'agent_name': 'Technical Chart Agent', 'status': 'working', 'progress': 86, 'current_step': 'Executing step 9/9: Create a detailed technical analysis report for ea...'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1122
127.0.0.1:53694 - - [10/Jul/2025:18:19:11] "GET /api/agent-orchestra/orchestrations/?show_all=true" 200 1836689
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO 🔧 EXECUTING TOOL CALL: news_api with params: {'keywords': 'XYZ Company', 'limit': 5, 'sort': 'publishedAt'}
INFO Applied parameter mappings for news_api: {'query': 'XYZ Company', 'limit': 5, 'sort': 'publishedAt'}
INFO Filtered out parameters for news_api: {'sort'}
INFO Executing tool: news_api with validated parameters: {'query': 'XYZ Company', 'limit': 5}
ERROR News API error: 'NewsAPIService' object does not support the asynchronous context manager protocol
INFO Tool news_api executed successfully
WARNING Tool news_api returned error: 'NewsAPIService' object does not support the asynchronous context manager protocol
INFO 🔧 EXECUTING TOOL CALL: sentiment_api with params: {'text': 'XYZ Company announces partnership with leading tech firm. Analysts expect strong earnings report from XYZ Company.'}
INFO Executing tool: sentiment_api with validated parameters: {'text': 'XYZ Company announces partnership with leading tech firm. Analysts expect strong earnings report from XYZ Company.'}
INFO Tool sentiment_api executed successfully
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1119: completed (80%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1119', 'agent_name': 'Market Sentiment Agent', 'status': 'completed', 'progress': 80, 'current_step': 'Step 8/10: Cross-reference Reddit findings with current news and market sentiment for additional context and verification'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1119
INFO Agent 1119 executing step 9/10: Review unusual options activity for the top 10 stocks to gauge investor expectations and sentiment
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1119', 'agent_name': 'Market Sentiment Agent', 'status': 'working', 'progress': 79, 'current_step': 'Executing step 9/10: Review unusual options activity for the top 10 sto...'}
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1119: working (79%)
INFO WebSocket consumer sent message to client: agent_progress for agent 1119
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Saved insight to memory: Insider Trading Signals as Market Indicators
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Saved insight to memory: Importance of Corporate Partnerships and Contract Announcements
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Saved insight to memory: Patent Filings and FDA Submissions as Future Growth Indicators
ERROR Task exception was never retrieved
future: <Task finished name='Task-3310' coro=<AsyncClient.aclose() done, defined at /Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpx/_client.py:1978> exception=RuntimeError('Event loop is closed')>
Traceback (most recent call last):
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpx/_client.py", line 1985, in aclose
    await self._transport.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpx/_transports/default.py", line 406, in aclose
    await self._pool.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/connection_pool.py", line 353, in aclose
    await self._close_connections(closing_connections)
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/connection_pool.py", line 345, in _close_connections
    await connection.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/connection.py", line 173, in aclose
    await self._connection.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/http11.py", line 258, in aclose
    await self._network_stream.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_backends/anyio.py", line 53, in aclose
    await self._stream.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/anyio/streams/tls.py", line 216, in aclose
    await self.transport_stream.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/anyio/_backends/_asyncio.py", line 1314, in aclose
    self._transport.close()
  File "/Users/donkeyking/.pyenv/versions/3.11.6/lib/python3.11/asyncio/selector_events.py", line 860, in close
    self._loop.call_soon(self._call_connection_lost, None)
  File "/Users/donkeyking/.pyenv/versions/3.11.6/lib/python3.11/asyncio/base_events.py", line 761, in call_soon
    self._check_closed()
  File "/Users/donkeyking/.pyenv/versions/3.11.6/lib/python3.11/asyncio/base_events.py", line 519, in _check_closed
    raise RuntimeError('Event loop is closed')
RuntimeError: Event loop is closed
ERROR Task exception was never retrieved
future: <Task finished name='Task-3311' coro=<AsyncClient.aclose() done, defined at /Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpx/_client.py:1978> exception=RuntimeError('Event loop is closed')>
Traceback (most recent call last):
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpx/_client.py", line 1985, in aclose
    await self._transport.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpx/_transports/default.py", line 406, in aclose
    await self._pool.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/connection_pool.py", line 353, in aclose
    await self._close_connections(closing_connections)
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/connection_pool.py", line 345, in _close_connections
    await connection.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/connection.py", line 173, in aclose
    await self._connection.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/http11.py", line 258, in aclose
    await self._network_stream.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_backends/anyio.py", line 53, in aclose
    await self._stream.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/anyio/streams/tls.py", line 216, in aclose
    await self.transport_stream.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/anyio/_backends/_asyncio.py", line 1314, in aclose
    self._transport.close()
  File "/Users/donkeyking/.pyenv/versions/3.11.6/lib/python3.11/asyncio/selector_events.py", line 860, in close
    self._loop.call_soon(self._call_connection_lost, None)
  File "/Users/donkeyking/.pyenv/versions/3.11.6/lib/python3.11/asyncio/base_events.py", line 761, in call_soon
    self._check_closed()
  File "/Users/donkeyking/.pyenv/versions/3.11.6/lib/python3.11/asyncio/base_events.py", line 519, in _check_closed
    raise RuntimeError('Event loop is closed')
RuntimeError: Event loop is closed
ERROR Task exception was never retrieved
future: <Task finished name='Task-3312' coro=<AsyncClient.aclose() done, defined at /Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpx/_client.py:1978> exception=RuntimeError('Event loop is closed')>
Traceback (most recent call last):
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpx/_client.py", line 1985, in aclose
    await self._transport.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpx/_transports/default.py", line 406, in aclose
    await self._pool.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/connection_pool.py", line 353, in aclose
    await self._close_connections(closing_connections)
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/connection_pool.py", line 345, in _close_connections
    await connection.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/connection.py", line 173, in aclose
    await self._connection.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/http11.py", line 258, in aclose
    await self._network_stream.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_backends/anyio.py", line 53, in aclose
    await self._stream.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/anyio/streams/tls.py", line 216, in aclose
    await self.transport_stream.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/anyio/_backends/_asyncio.py", line 1314, in aclose
    self._transport.close()
  File "/Users/donkeyking/.pyenv/versions/3.11.6/lib/python3.11/asyncio/selector_events.py", line 860, in close
    self._loop.call_soon(self._call_connection_lost, None)
  File "/Users/donkeyking/.pyenv/versions/3.11.6/lib/python3.11/asyncio/base_events.py", line 761, in call_soon
    self._check_closed()
  File "/Users/donkeyking/.pyenv/versions/3.11.6/lib/python3.11/asyncio/base_events.py", line 519, in _check_closed
    raise RuntimeError('Event loop is closed')
RuntimeError: Event loop is closed
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Saved insight to memory: Leveraging Social Media for Market Sentiment Analysis
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Saved insight to memory: Technical Challenges Limit Real-Time Data Analysis
INFO Saved 5 insights from agent 1120 to Memory Palace
INFO Successfully saved agent 1120 insights to Memory Palace
INFO Not all agents completed for Stock Scout orchestration 409
INFO Agent 1120 finished in 109.8s with status: completed_with_errors
INFO API calls: 10, Success rate: 1/5
INFO Agent 1120 execution completed successfully!
INFO Agent 1120 completed with result: True
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO 🔧 EXECUTING TOOL CALL: polygon_market_data with params: {'action': 'get_unusual_options_activity', 'date': '2025-07-10', 'limit': 10}
INFO Applied parameter mappings for polygon_market_data: {'action': 'get_unusual_options_activity', 'date': '2025-07-10', 'limit': 10}
WARNING polygon_market_data called without symbol/company, using default SPY
INFO Filtered out parameters for polygon_market_data: {'limit', 'date', 'action'}
INFO Executing tool: polygon_market_data with validated parameters: {'symbol': 'SPY'}
INFO Polygon S3 client initialized successfully
ERROR Task exception was never retrieved
future: <Task finished name='Task-3318' coro=<AsyncClient.aclose() done, defined at /Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpx/_client.py:1978> exception=RuntimeError('Event loop is closed')>
Traceback (most recent call last):
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpx/_client.py", line 1985, in aclose
    await self._transport.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpx/_transports/default.py", line 406, in aclose
    await self._pool.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/connection_pool.py", line 353, in aclose
    await self._close_connections(closing_connections)
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/connection_pool.py", line 345, in _close_connections
    await connection.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/connection.py", line 173, in aclose
    await self._connection.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/http11.py", line 258, in aclose
    await self._network_stream.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_backends/anyio.py", line 53, in aclose
    await self._stream.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/anyio/streams/tls.py", line 216, in aclose
    await self.transport_stream.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/anyio/_backends/_asyncio.py", line 1314, in aclose
    self._transport.close()
  File "/Users/donkeyking/.pyenv/versions/3.11.6/lib/python3.11/asyncio/selector_events.py", line 860, in close
    self._loop.call_soon(self._call_connection_lost, None)
  File "/Users/donkeyking/.pyenv/versions/3.11.6/lib/python3.11/asyncio/base_events.py", line 761, in call_soon
    self._check_closed()
  File "/Users/donkeyking/.pyenv/versions/3.11.6/lib/python3.11/asyncio/base_events.py", line 519, in _check_closed
    raise RuntimeError('Event loop is closed')
RuntimeError: Event loop is closed
ERROR Task exception was never retrieved
future: <Task finished name='Task-3319' coro=<AsyncClient.aclose() done, defined at /Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpx/_client.py:1978> exception=RuntimeError('Event loop is closed')>
Traceback (most recent call last):
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpx/_client.py", line 1985, in aclose
    await self._transport.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpx/_transports/default.py", line 406, in aclose
    await self._pool.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/connection_pool.py", line 353, in aclose
    await self._close_connections(closing_connections)
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/connection_pool.py", line 345, in _close_connections
    await connection.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/connection.py", line 173, in aclose
    await self._connection.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/http11.py", line 258, in aclose
    await self._network_stream.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_backends/anyio.py", line 53, in aclose
    await self._stream.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/anyio/streams/tls.py", line 216, in aclose
    await self.transport_stream.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/anyio/_backends/_asyncio.py", line 1314, in aclose
    self._transport.close()
  File "/Users/donkeyking/.pyenv/versions/3.11.6/lib/python3.11/asyncio/selector_events.py", line 860, in close
    self._loop.call_soon(self._call_connection_lost, None)
  File "/Users/donkeyking/.pyenv/versions/3.11.6/lib/python3.11/asyncio/base_events.py", line 761, in call_soon
    self._check_closed()
  File "/Users/donkeyking/.pyenv/versions/3.11.6/lib/python3.11/asyncio/base_events.py", line 519, in _check_closed
    raise RuntimeError('Event loop is closed')
RuntimeError: Event loop is closed
INFO Tool polygon_market_data executed successfully
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1119', 'agent_name': 'Market Sentiment Agent', 'status': 'completed', 'progress': 90, 'current_step': 'Step 9/10: Review unusual options activity for the top 10 stocks to gauge investor expectations and sentiment'}
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1119: completed (90%)
INFO WebSocket consumer sent message to client: agent_progress for agent 1119
INFO Agent 1119 executing step 10/10: Assess crowd psychology and FOMO risk for each opportunity to determine retail interest phase
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1119: working (87%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1119', 'agent_name': 'Market Sentiment Agent', 'status': 'working', 'progress': 87, 'current_step': 'Executing step 10/10: Assess crowd psychology and FOMO risk for each opp...'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1119
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO 🔧 EXECUTING TOOL CALL: sec_edgar_api with params: {'symbol': 'TSLA', 'date_range': '2025-01-01 to 2025-07-10'}
INFO Filtered out parameters for sec_edgar_api: {'date_range'}
INFO Executing tool: sec_edgar_api with validated parameters: {'symbol': 'TSLA'}
ERROR SEC EDGAR API error: 'SECAPIService' object does not support the asynchronous context manager protocol
INFO Tool sec_edgar_api executed successfully
WARNING Tool sec_edgar_api returned error: 'SECAPIService' object does not support the asynchronous context manager protocol
INFO 🔧 EXECUTING TOOL CALL: sec_edgar_api with params: {'symbol': 'TSLA', 'type': 'press_release', 'date_range': '2025-01-01 to 2025-07-10'}
INFO Filtered out parameters for sec_edgar_api: {'date_range', 'type'}
INFO Executing tool: sec_edgar_api with validated parameters: {'symbol': 'TSLA'}
ERROR SEC EDGAR API error: 'SECAPIService' object does not support the asynchronous context manager protocol
INFO Tool sec_edgar_api executed successfully
WARNING Tool sec_edgar_api returned error: 'SECAPIService' object does not support the asynchronous context manager protocol
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1121: error (87%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1121', 'agent_name': 'News Catalyst Agent', 'status': 'error', 'progress': 87, 'current_step': 'Step 7/8: For identified stocks, further analyze company fundamentals and recent developments through SEC filings.'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1121
INFO Agent 1121 executing step 8/8: Consolidate findings into a comprehensive report detailing actionable investment opportunities, including risk assessment and expected impact.
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1121', 'agent_name': 'News Catalyst Agent', 'status': 'working', 'progress': 85, 'current_step': 'Executing step 8/8: Consolidate findings into a comprehensive report d...'}
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1121: working (85%)
INFO WebSocket consumer sent message to client: agent_progress for agent 1121
INFO WebSocket consumer sent message to client: agent_progress for agent 1121
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1122: completed (100%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1122', 'agent_name': 'Technical Chart Agent', 'status': 'completed', 'progress': 100, 'current_step': 'Step 9/9: Create a detailed technical analysis report for each prioritized stock, combining all findings.'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1122
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1123', 'agent_name': 'Stock Synthesis Agent', 'status': 'completed', 'progress': 85, 'current_step': 'Step 6/7: Rank the identified investment opportunities by their overall score, prioritizing those with the highest potential and reasonable risk.'}
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1123: completed (85%)
INFO WebSocket consumer sent message to client: agent_progress for agent 1123
INFO Agent 1123 executing step 7/7: For the top-ranked stocks, conduct a deeper dive to verify the data's accuracy and current relevance, ensuring the recommendations are based on the most recent information.
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1123: working (83%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1123', 'agent_name': 'Stock Synthesis Agent', 'status': 'working', 'progress': 83, 'current_step': 'Executing step 7/7: For the top-ranked stocks, conduct a deeper dive t...'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1123
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO 🔧 EXECUTING TOOL CALL: reddit_api with params: {'subreddits': ['SecurityAnalysis', 'ValueInvesting', 'stocks', 'pennystocks', 'Biotechplays', 'SPACs', 'investing', 'StockMarket', 'RobinHoodPennyStocks', 'smallstreetbets'], 'limit': 100, 'sort': 'hot'}
INFO Applied parameter mappings for reddit_api: {'subreddit': ['SecurityAnalysis', 'ValueInvesting', 'stocks', 'pennystocks', 'Biotechplays', 'SPACs', 'investing', 'StockMarket', 'RobinHoodPennyStocks', 'smallstreetbets'], 'limit': 100, 'sort': 'hot'}
INFO Executing tool: reddit_api with validated parameters: {'subreddit': ['SecurityAnalysis', 'ValueInvesting', 'stocks', 'pennystocks', 'Biotechplays', 'SPACs', 'investing', 'StockMarket', 'RobinHoodPennyStocks', 'smallstreetbets'], 'limit': 100, 'sort': 'hot'}
INFO Reddit API clients initialized successfully
WARNING Error fetching from r/['SecurityAnalysis', 'ValueInvesting', 'stocks', 'pennystocks', 'Biotechplays', 'SPACs', 'investing', 'StockMarket', 'RobinHoodPennyStocks', 'smallstreetbets']: 'list' object has no attribute 'lower'
WARNING Error analyzing r/Entrepreneur: error with request Session is closed
WARNING Error analyzing r/startups: error with request Session is closed
WARNING Error analyzing r/SaaS: error with request Session is closed
WARNING Error analyzing r/Business_Ideas: error with request Session is closed
WARNING Error analyzing r/Startup_Ideas: error with request Session is closed
INFO Tool reddit_api executed successfully
INFO 🔧 EXECUTING TOOL CALL: sentiment_api with params: {'text': 'Sample text from Reddit post about Stock_X'}
INFO Executing tool: sentiment_api with validated parameters: {'text': 'Sample text from Reddit post about Stock_X'}
INFO Tool sentiment_api executed successfully
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1119: completed (100%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1119', 'agent_name': 'Market Sentiment Agent', 'status': 'completed', 'progress': 100, 'current_step': 'Step 10/10: Assess crowd psychology and FOMO risk for each opportunity to determine retail interest phase'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1119
127.0.0.1:53694 - - [10/Jul/2025:18:19:41] "GET /api/agent-orchestra/orchestrations/?show_all=true" 200 1836723
NFO 🔧 EXECUTING TOOL CALL: news_api with params: {'query': 'stock market', 'sources': 'bloomberg,reuters,marketwatch', 'language': 'en', 'sortBy': 'publishedAt'}
INFO Applied parameter mappings for news_api: {'query': 'stock market', 'sources': 'bloomberg,reuters,marketwatch', 'language': 'en', 'sortBy': 'publishedAt'}
INFO Filtered out parameters for news_api: {'sortBy', 'language', 'sources'}
INFO Executing tool: news_api with validated parameters: {'query': 'stock market'}
ERROR News API error: 'NewsAPIService' object does not support the asynchronous context manager protocol
INFO Tool news_api executed successfully
WARNING Tool news_api returned error: 'NewsAPIService' object does not support the asynchronous context manager protocol
INFO 🔧 EXECUTING TOOL CALL: yahoo_finance with params: {'filter': 'pre_market_movers'}
INFO Filtered out parameters for yahoo_finance: {'filter'}
INFO Executing tool: yahoo_finance with validated parameters: {}
ERROR Parameter mismatch for yahoo_finance: EnhancedAgentTools.yahoo_finance() missing 1 required positional argument: 'symbol'
INFO Retrying yahoo_finance with minimal parameters
WARNING Tool yahoo_finance returned error: EnhancedAgentTools.yahoo_finance() missing 1 required positional argument: 'symbol'
INFO 🔧 EXECUTING TOOL CALL: reddit_api with params: {'subreddit': 'stocks', 'query': 'pre_market_movers'}
WARNING Unknown parameter 'query' for tool reddit_api
INFO Applied parameter mappings for reddit_api: {'subreddit': 'stocks', 'query': 'pre_market_movers'}
INFO Filtered out parameters for reddit_api: {'query'}
INFO Executing tool: reddit_api with validated parameters: {'subreddit': 'stocks'}
INFO Reddit API clients initialized successfully
WARNING Error analyzing r/Entrepreneur: error with request Session is closed
WARNING Error analyzing r/startups: error with request Session is closed
WARNING Error analyzing r/SaaS: error with request Session is closed
WARNING Error analyzing r/Business_Ideas: error with request Session is closed
WARNING Error analyzing r/Startup_Ideas: error with request Session is closed
INFO Tool reddit_api executed successfully
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1121: completed (100%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1121', 'agent_name': 'News Catalyst Agent', 'status': 'completed', 'progress': 100, 'current_step': 'Step 8/8: Consolidate findings into a comprehensive report detailing actionable investment opportunities, including risk assessment and expected impact.'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1121

INFO Tool reddit_api executed successfully
INFO 🔧 EXECUTING TOOL CALL: sentiment_api with params: {'text': 'Sample text from Reddit post about Stock_X'}
INFO Executing tool: sentiment_api with validated parameters: {'text': 'Sample text from Reddit post about Stock_X'}
INFO Tool sentiment_api executed successfully
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1119: completed (100%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1119', 'agent_name': 'Market Sentiment Agent', 'status': 'completed', 'progress': 100, 'current_step': 'Step 10/10: Assess crowd psychology and FOMO risk for each opportunity to determine retail interest phase'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1119
127.0.0.1:53694 - - [10/Jul/2025:18:19:41] "GET /api/agent-orchestra/orchestrations/?show_all=true" 200 1836723
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO 🔧 EXECUTING TOOL CALL: news_api with params: {'query': 'stock market', 'sources': 'bloomberg,reuters,marketwatch', 'language': 'en', 'sortBy': 'publishedAt'}
INFO Applied parameter mappings for news_api: {'query': 'stock market', 'sources': 'bloomberg,reuters,marketwatch', 'language': 'en', 'sortBy': 'publishedAt'}
INFO Filtered out parameters for news_api: {'sortBy', 'language', 'sources'}
INFO Executing tool: news_api with validated parameters: {'query': 'stock market'}
ERROR News API error: 'NewsAPIService' object does not support the asynchronous context manager protocol
INFO Tool news_api executed successfully
WARNING Tool news_api returned error: 'NewsAPIService' object does not support the asynchronous context manager protocol
INFO 🔧 EXECUTING TOOL CALL: yahoo_finance with params: {'filter': 'pre_market_movers'}
INFO Filtered out parameters for yahoo_finance: {'filter'}
INFO Executing tool: yahoo_finance with validated parameters: {}
ERROR Parameter mismatch for yahoo_finance: EnhancedAgentTools.yahoo_finance() missing 1 required positional argument: 'symbol'
INFO Retrying yahoo_finance with minimal parameters
WARNING Tool yahoo_finance returned error: EnhancedAgentTools.yahoo_finance() missing 1 required positional argument: 'symbol'
INFO 🔧 EXECUTING TOOL CALL: reddit_api with params: {'subreddit': 'stocks', 'query': 'pre_market_movers'}
WARNING Unknown parameter 'query' for tool reddit_api
INFO Applied parameter mappings for reddit_api: {'subreddit': 'stocks', 'query': 'pre_market_movers'}
INFO Filtered out parameters for reddit_api: {'query'}
INFO Executing tool: reddit_api with validated parameters: {'subreddit': 'stocks'}
INFO Reddit API clients initialized successfully
WARNING Error analyzing r/Entrepreneur: error with request Session is closed
WARNING Error analyzing r/startups: error with request Session is closed
WARNING Error analyzing r/SaaS: error with request Session is closed
WARNING Error analyzing r/Business_Ideas: error with request Session is closed
WARNING Error analyzing r/Startup_Ideas: error with request Session is closed
INFO Tool reddit_api executed successfully
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1121: completed (100%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1121', 'agent_name': 'News Catalyst Agent', 'status': 'completed', 'progress': 100, 'current_step': 'Step 8/8: Consolidate findings into a comprehensive report detailing actionable investment opportunities, including risk assessment and expected impact.'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1121
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO Generated enhanced report of 5602 characters with 3 API calls
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1122: completed_with_errors (100%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1122', 'agent_name': 'Technical Chart Agent', 'status': 'completed_with_errors', 'progress': 100, 'current_step': 'Completed with 1 errors'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1122
127.0.0.1:53694 - - [10/Jul/2025:18:20:09] "GET /api/agent-orchestra/command-center/stats/" 200 130
127.0.0.1:53694 - - [10/Jul/2025:18:20:11] "GET /api/agent-orchestra/orchestrations/?show_all=true" 200 1842440
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO Generated enhanced report of 4746 characters with 13 API calls
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1119: completed (100%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1119', 'agent_name': 'Market Sentiment Agent', 'status': 'completed', 'progress': 100, 'current_step': 'Execution completed successfully!'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1119
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Saved insight to memory: Nvidia Achieves Historic $4 Trillion Market Cap
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Saved insight to memory: Copper Tariff Impact on Mining and Tech Stocks
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Saved insight to memory: AI Innovation Risks for Google's Market Position
INFO Saved 3 insights from agent 1122 to Memory Palace
INFO Successfully saved agent 1122 insights to Memory Palace
INFO Not all agents completed for Stock Scout orchestration 409
INFO Agent 1122 finished in 170.1s with status: completed_with_errors
INFO API calls: 3, Success rate: 8/9
INFO Agent 1122 execution completed successfully!
INFO Agent 1122 completed with result: True
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Saved insight to memory: Lack of Emerging Sentiment and Discussion Activity
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Saved insight to memory: Current Absence of Identified Catalysts or Actionable Opportunities
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Saved insight to memory: Effective Filtering of Pump-and-Dump Schemes Ensures Data Integrity
ERROR Task exception was never retrieved
future: <Task finished name='Task-3511' coro=<AsyncClient.aclose() done, defined at /Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpx/_client.py:1978> exception=RuntimeError('Event loop is closed')>
Traceback (most recent call last):
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpx/_client.py", line 1985, in aclose
    await self._transport.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpx/_transports/default.py", line 406, in aclose
    await self._pool.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/connection_pool.py", line 353, in aclose
    await self._close_connections(closing_connections)
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/connection_pool.py", line 345, in _close_connections
    await connection.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/connection.py", line 173, in aclose
    await self._connection.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/http11.py", line 258, in aclose
    await self._network_stream.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_backends/anyio.py", line 53, in aclose
    await self._stream.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/anyio/streams/tls.py", line 216, in aclose
    await self.transport_stream.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/anyio/_backends/_asyncio.py", line 1314, in aclose
    self._transport.close()
  File "/Users/donkeyking/.pyenv/versions/3.11.6/lib/python3.11/asyncio/selector_events.py", line 860, in close
    self._loop.call_soon(self._call_connection_lost, None)
  File "/Users/donkeyking/.pyenv/versions/3.11.6/lib/python3.11/asyncio/base_events.py", line 761, in call_soon
    self._check_closed()
  File "/Users/donkeyking/.pyenv/versions/3.11.6/lib/python3.11/asyncio/base_events.py", line 519, in _check_closed
    raise RuntimeError('Event loop is closed')
RuntimeError: Event loop is closed
ERROR Task exception was never retrieved
future: <Task finished name='Task-3512' coro=<AsyncClient.aclose() done, defined at /Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpx/_client.py:1978> exception=RuntimeError('Event loop is closed')>
Traceback (most recent call last):
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpx/_client.py", line 1985, in aclose
    await self._transport.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpx/_transports/default.py", line 406, in aclose
    await self._pool.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/connection_pool.py", line 353, in aclose
    await self._close_connections(closing_connections)
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/connection_pool.py", line 345, in _close_connections
    await connection.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/connection.py", line 173, in aclose
    await self._connection.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/http11.py", line 258, in aclose
    await self._network_stream.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_backends/anyio.py", line 53, in aclose
    await self._stream.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/anyio/streams/tls.py", line 216, in aclose
    await self.transport_stream.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/anyio/_backends/_asyncio.py", line 1314, in aclose
    self._transport.close()
  File "/Users/donkeyking/.pyenv/versions/3.11.6/lib/python3.11/asyncio/selector_events.py", line 860, in close
    self._loop.call_soon(self._call_connection_lost, None)
  File "/Users/donkeyking/.pyenv/versions/3.11.6/lib/python3.11/asyncio/base_events.py", line 761, in call_soon
    self._check_closed()
  File "/Users/donkeyking/.pyenv/versions/3.11.6/lib/python3.11/asyncio/base_events.py", line 519, in _check_closed
    raise RuntimeError('Event loop is closed')
RuntimeError: Event loop is closed
ERROR Task exception was never retrieved
future: <Task finished name='Task-3513' coro=<AsyncClient.aclose() done, defined at /Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpx/_client.py:1978> exception=RuntimeError('Event loop is closed')>
Traceback (most recent call last):
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpx/_client.py", line 1985, in aclose
    await self._transport.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpx/_transports/default.py", line 406, in aclose
    await self._pool.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/connection_pool.py", line 353, in aclose
    await self._close_connections(closing_connections)
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/connection_pool.py", line 345, in _close_connections
    await connection.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/connection.py", line 173, in aclose
    await self._connection.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/http11.py", line 258, in aclose
    await self._network_stream.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_backends/anyio.py", line 53, in aclose
    await self._stream.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/anyio/streams/tls.py", line 216, in aclose
    await self.transport_stream.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/anyio/_backends/_asyncio.py", line 1314, in aclose
    self._transport.close()
  File "/Users/donkeyking/.pyenv/versions/3.11.6/lib/python3.11/asyncio/selector_events.py", line 860, in close
    self._loop.call_soon(self._call_connection_lost, None)
  File "/Users/donkeyking/.pyenv/versions/3.11.6/lib/python3.11/asyncio/base_events.py", line 761, in call_soon
    self._check_closed()
  File "/Users/donkeyking/.pyenv/versions/3.11.6/lib/python3.11/asyncio/base_events.py", line 519, in _check_closed
    raise RuntimeError('Event loop is closed')
RuntimeError: Event loop is closed
ERROR Task exception was never retrieved
future: <Task finished name='Task-3514' coro=<AsyncClient.aclose() done, defined at /Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpx/_client.py:1978> exception=RuntimeError('Event loop is closed')>
Traceback (most recent call last):
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpx/_client.py", line 1985, in aclose
    await self._transport.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpx/_transports/default.py", line 406, in aclose
    await self._pool.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/connection_pool.py", line 353, in aclose
    await self._close_connections(closing_connections)
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/connection_pool.py", line 345, in _close_connections
    await connection.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/connection.py", line 173, in aclose
    await self._connection.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/http11.py", line 258, in aclose
    await self._network_stream.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_backends/anyio.py", line 53, in aclose
    await self._stream.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/anyio/streams/tls.py", line 216, in aclose
    await self.transport_stream.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/anyio/_backends/_asyncio.py", line 1314, in aclose
    self._transport.close()
  File "/Users/donkeyking/.pyenv/versions/3.11.6/lib/python3.11/asyncio/selector_events.py", line 860, in close
    self._loop.call_soon(self._call_connection_lost, None)
  File "/Users/donkeyking/.pyenv/versions/3.11.6/lib/python3.11/asyncio/base_events.py", line 761, in call_soon
    self._check_closed()
  File "/Users/donkeyking/.pyenv/versions/3.11.6/lib/python3.11/asyncio/base_events.py", line 519, in _check_closed
    raise RuntimeError('Event loop is closed')
RuntimeError: Event loop is closed
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Saved insight to memory: Market Monitoring Should Be Enhanced for Early Signal Detection
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Saved insight to memory: Options Market Data Provides Limited Market Sentiment Insights Alone
INFO Saved 5 insights from agent 1119 to Memory Palace
INFO Successfully saved agent 1119 insights to Memory Palace
INFO Not all agents completed for Stock Scout orchestration 409
INFO Agent 1119 finished in 173.5s with status: completed
INFO API calls: 13, Success rate: 10/10
INFO Agent 1119 execution completed successfully!
INFO Agent 1119 completed with result: True
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO Generated enhanced report of 4558 characters with 13 API calls
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1121', 'agent_name': 'News Catalyst Agent', 'status': 'completed_with_errors', 'progress': 100, 'current_step': 'Completed with 4 errors'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1121
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1121: completed_with_errors (100%)
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Saved insight to memory: Reddit Buzz Strongly Correlates with Market Volatility
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Saved insight to memory: Emerging Under the Radar Stocks Offer Early Investment Opportunities
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"

INFO Saved insight to memory: Fundamental Analysis via SEC Filings Supports Long-Term Investment Decisions
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Saved insight to memory: Prioritize Monitoring Social Media for Emerging Investment Trends
INFO Saved 4 insights from agent 1121 to Memory Palace
INFO Successfully saved agent 1121 insights to Memory Palace
INFO Not all agents completed for Stock Scout orchestration 409
INFO Agent 1121 finished in 183.7s with status: completed_with_errors
INFO API calls: 13, Success rate: 4/8
INFO Agent 1121 execution completed successfully!
INFO Agent 1121 completed with result: True
127.0.0.1:53694 - - [10/Jul/2025:18:20:41] "GET /api/agent-orchestra/orchestrations/?show_all=true" 200 1851898
127.0.0.1:53841 - - [10/Jul/2025:18:20:54] "WSDISCONNECT /ws/agent-orchestra/409/" - -
INFO User 2 disconnected from agent progress WebSocket
127.0.0.1:53694 - - [10/Jul/2025:18:20:54] "GET /api/agent-orchestra/orchestrations/?show_all=true" 200 1851898
127.0.0.1:54226 - - [10/Jul/2025:18:20:55] "GET /api/agent-orchestra/orchestrations/?show_all=true" 200 1851898
127.0.0.1:54230 - - [10/Jul/2025:18:20:55] "WSCONNECTING /ws/agent-orchestra/409/" - -
INFO WebSocket authenticated user: testuser
127.0.0.1:54230 - - [10/Jul/2025:18:20:55] "WSCONNECT /ws/agent-orchestra/409/" - -
INFO User 2 connected to agent progress WebSocket for orchestration 409
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 500 Internal Server Error"
INFO Retrying request to /chat/completions in 0.399652 seconds
127.0.0.1:54246 - - [10/Jul/2025:18:21:07] "OPTIONS /api/agent-orchestra/orchestrations/409/" 200 -
127.0.0.1:54248 - - [10/Jul/2025:18:21:07] "OPTIONS /api/agent-orchestra/orchestrations/409/" 200 -
127.0.0.1:54226 - - [10/Jul/2025:18:21:07] "GET /api/agent-orchestra/orchestrations/409/" 200 28225
127.0.0.1:53694 - - [10/Jul/2025:18:21:07] "GET /api/agent-orchestra/orchestrations/409/" 200 28225
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO 🔧 EXECUTING TOOL CALL: web_search with params: {'query': 'Tesla Inc. TSLA latest news 2025', 'num_results': 5}
INFO Applied parameter mappings for web_search: {'query': 'Tesla Inc. TSLA latest news 2025', 'num_results': 5}
INFO Executing tool: web_search with validated parameters: {'query': 'Tesla Inc. TSLA latest news 2025', 'num_results': 5}
INFO Tool web_search executed successfully
INFO 🔧 EXECUTING TOOL CALL: news_api with params: {'keywords': 'TSLA', 'from': '2025-07-01', 'to': '2025-07-10', 'language': 'en'}
INFO Applied parameter mappings for news_api: {'query': 'TSLA', 'from': '2025-07-01', 'to': '2025-07-10', 'language': 'en'}
INFO Filtered out parameters for news_api: {'language', 'to', 'from'}
INFO Executing tool: news_api with validated parameters: {'query': 'TSLA'}
ERROR News API error: 'NewsAPIService' object does not support the asynchronous context manager protocol
INFO Tool news_api executed successfully
WARNING Tool news_api returned error: 'NewsAPIService' object does not support the asynchronous context manager protocol
INFO 🔧 EXECUTING TOOL CALL: web_search with params: {'query': 'Nvidia Corporation NVDA latest news 2025', 'num_results': 5}
INFO Applied parameter mappings for web_search: {'query': 'Nvidia Corporation NVDA latest news 2025', 'num_results': 5}
INFO Executing tool: web_search with validated parameters: {'query': 'Nvidia Corporation NVDA latest news 2025', 'num_results': 5}
INFO Tool web_search executed successfully
INFO 🔧 EXECUTING TOOL CALL: news_api with params: {'keywords': 'NVDA', 'from': '2025-07-01', 'to': '2025-07-10', 'language': 'en'}
INFO Applied parameter mappings for news_api: {'query': 'NVDA', 'from': '2025-07-01', 'to': '2025-07-10', 'language': 'en'}
INFO Filtered out parameters for news_api: {'language', 'to', 'from'}
INFO Executing tool: news_api with validated parameters: {'query': 'NVDA'}
ERROR News API error: 'NewsAPIService' object does not support the asynchronous context manager protocol
INFO Tool news_api executed successfully
WARNING Tool news_api returned error: 'NewsAPIService' object does not support the asynchronous context manager protocol
INFO 🔧 EXECUTING TOOL CALL: web_search with params: {'query': 'Apple Inc. AAPL latest news 2025', 'num_results': 5}
INFO Applied parameter mappings for web_search: {'query': 'Apple Inc. AAPL latest news 2025', 'num_results': 5}
INFO Executing tool: web_search with validated parameters: {'query': 'Apple Inc. AAPL latest news 2025', 'num_results': 5}
INFO Tool web_search executed successfully
INFO 🔧 EXECUTING TOOL CALL: news_api with params: {'keywords': 'AAPL', 'from': '2025-07-01', 'to': '2025-07-10', 'language': 'en'}
INFO Applied parameter mappings for news_api: {'query': 'AAPL', 'from': '2025-07-01', 'to': '2025-07-10', 'language': 'en'}
INFO Filtered out parameters for news_api: {'language', 'to', 'from'}
INFO Executing tool: news_api with validated parameters: {'query': 'AAPL'}
ERROR News API error: 'NewsAPIService' object does not support the asynchronous context manager protocol
INFO Tool news_api executed successfully
WARNING Tool news_api returned error: 'NewsAPIService' object does not support the asynchronous context manager protocol
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1123: completed (100%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1123', 'agent_name': 'Stock Synthesis Agent', 'status': 'completed', 'progress': 100, 'current_step': "Step 7/7: For the top-ranked stocks, conduct a deeper dive to verify the data's accuracy and current relevance, ensuring the recommendations are based on the most recent information."}
INFO WebSocket consumer sent message to client: agent_progress for agent 1123
INFO Generated enhanced report of 5495 characters with 16 API calls
INFO Sent WebSocket update to group 'agent_progress_409' for agent 1123: completed_with_errors (100%)
INFO WebSocket consumer received agent_progress_update: {'type': 'agent_progress_update', 'orchestration_id': '409', 'agent_id': '1123', 'agent_name': 'Stock Synthesis Agent', 'status': 'completed_with_errors', 'progress': 100, 'current_step': 'Completed with 1 errors'}
INFO WebSocket consumer sent message to client: agent_progress for agent 1123
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Saved insight to memory: Nvidia Leads in AI Market with $4 Trillion Valuation
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Saved insight to memory: Bullish Sentiment for Copper Stocks Due to Tariff Imposition
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Saved insight to memory: Tesla and Apple Remain Key Tech Stocks with Growth Potential
ERROR Task exception was never retrieved
future: <Task finished name='Task-3648' coro=<AsyncClient.aclose() done, defined at /Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpx/_client.py:1978> exception=RuntimeError('Event loop is closed')>
Traceback (most recent call last):
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpx/_client.py", line 1985, in aclose
    await self._transport.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpx/_transports/default.py", line 406, in aclose
    await self._pool.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/connection_pool.py", line 353, in aclose
    await self._close_connections(closing_connections)
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/connection_pool.py", line 345, in _close_connections
    await connection.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/connection.py", line 173, in aclose
    await self._connection.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/http11.py", line 258, in aclose
    await self._network_stream.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_backends/anyio.py", line 53, in aclose
    await self._stream.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/anyio/streams/tls.py", line 216, in aclose
    await self.transport_stream.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/anyio/_backends/_asyncio.py", line 1314, in aclose
    self._transport.close()
  File "/Users/donkeyking/.pyenv/versions/3.11.6/lib/python3.11/asyncio/selector_events.py", line 860, in close
    self._loop.call_soon(self._call_connection_lost, None)
  File "/Users/donkeyking/.pyenv/versions/3.11.6/lib/python3.11/asyncio/base_events.py", line 761, in call_soon
    self._check_closed()
  File "/Users/donkeyking/.pyenv/versions/3.11.6/lib/python3.11/asyncio/base_events.py", line 519, in _check_closed
    raise RuntimeError('Event loop is closed')
RuntimeError: Event loop is closed
ERROR Task exception was never retrieved
future: <Task finished name='Task-3649' coro=<AsyncClient.aclose() done, defined at /Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpx/_client.py:1978> exception=RuntimeError('Event loop is closed')>
Traceback (most recent call last):
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpx/_client.py", line 1985, in aclose
    await self._transport.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpx/_transports/default.py", line 406, in aclose
    await self._pool.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/connection_pool.py", line 353, in aclose
    await self._close_connections(closing_connections)
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/connection_pool.py", line 345, in _close_connections
    await connection.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/connection.py", line 173, in aclose
    await self._connection.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/http11.py", line 258, in aclose
    await self._network_stream.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_backends/anyio.py", line 53, in aclose
    await self._stream.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/anyio/streams/tls.py", line 216, in aclose
    await self.transport_stream.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/anyio/_backends/_asyncio.py", line 1314, in aclose
    self._transport.close()
  File "/Users/donkeyking/.pyenv/versions/3.11.6/lib/python3.11/asyncio/selector_events.py", line 860, in close
    self._loop.call_soon(self._call_connection_lost, None)
  File "/Users/donkeyking/.pyenv/versions/3.11.6/lib/python3.11/asyncio/base_events.py", line 761, in call_soon
    self._check_closed()
  File "/Users/donkeyking/.pyenv/versions/3.11.6/lib/python3.11/asyncio/base_events.py", line 519, in _check_closed
    raise RuntimeError('Event loop is closed')
RuntimeError: Event loop is closed
ERROR Task exception was never retrieved
future: <Task finished name='Task-3650' coro=<AsyncClient.aclose() done, defined at /Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpx/_client.py:1978> exception=RuntimeError('Event loop is closed')>
Traceback (most recent call last):
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpx/_client.py", line 1985, in aclose
    await self._transport.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpx/_transports/default.py", line 406, in aclose
    await self._pool.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/connection_pool.py", line 353, in aclose
    await self._close_connections(closing_connections)
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/connection_pool.py", line 345, in _close_connections
    await connection.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/connection.py", line 173, in aclose
    await self._connection.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_async/http11.py", line 258, in aclose
    await self._network_stream.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/httpcore/_backends/anyio.py", line 53, in aclose
    await self._stream.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/anyio/streams/tls.py", line 216, in aclose
    await self.transport_stream.aclose()
  File "/Users/donkeyking/development/move_that_ass/.venv/lib/python3.11/site-packages/anyio/_backends/_asyncio.py", line 1314, in aclose
    self._transport.close()
  File "/Users/donkeyking/.pyenv/versions/3.11.6/lib/python3.11/asyncio/selector_events.py", line 860, in close
    self._loop.call_soon(self._call_connection_lost, None)
  File "/Users/donkeyking/.pyenv/versions/3.11.6/lib/python3.11/asyncio/base_events.py", line 761, in call_soon
    self._check_closed()
  File "/Users/donkeyking/.pyenv/versions/3.11.6/lib/python3.11/asyncio/base_events.py", line 519, in _check_closed
    raise RuntimeError('Event loop is closed')
RuntimeError: Event loop is closed
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Saved insight to memory: High Growth Potential in Plastic Recycling Sector with Purecycle
INFO Saved 4 insights from agent 1123 to Memory Palace
INFO Successfully saved agent 1123 insights to Memory Palace
INFO Not all agents completed for Stock Scout orchestration 409
INFO Agent 1123 finished in 277.6s with status: completed_with_errors
INFO API calls: 16, Success rate: 6/7
INFO Agent 1123 execution completed successfully!
INFO Agent 1123 completed with result: True
INFO Stock Scout mission 409 completed with status: failed
