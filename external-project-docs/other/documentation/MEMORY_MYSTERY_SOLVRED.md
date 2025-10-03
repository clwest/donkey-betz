127.0.0.1:55815 - - [10/Jul/2025:11:16:08] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1792793
127.0.0.1:55832 - - [10/Jul/2025:11:16:10] "OPTIONS /api/auth/user/" 200 -
127.0.0.1:55830 - - [10/Jul/2025:11:16:10] "OPTIONS /api/auth/user/" 200 -
127.0.0.1:55837 - - [10/Jul/2025:11:16:10] "GET /api/auth/user/" 200 61
127.0.0.1:55836 - - [10/Jul/2025:11:16:10] "GET /api/auth/user/" 200 61
127.0.0.1:55836 - - [10/Jul/2025:11:16:10] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1792793
127.0.0.1:55853 - - [10/Jul/2025:11:16:15] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1792793
127.0.0.1:55870 - - [10/Jul/2025:11:16:21] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1792793
127.0.0.1:55880 - - [10/Jul/2025:11:16:26] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1792793
127.0.0.1:55888 - - [10/Jul/2025:11:16:31] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1792793
127.0.0.1:55896 - - [10/Jul/2025:11:16:35] "OPTIONS /api/ai-partner/memory/search/?query=Based+on+our+ChatGPT+conversations+from+2023-2024%2C+how+many+deployments+did+we+plan%3F&limit=3" 200 -
INFO Memory search request: user=2, query='Based on our ChatGPT conversations from 2023-2024,...'
INFO 🔍 DEBUG MemoryRetrieval: Starting search for user 2, query: 'Based on our ChatGPT conversations from 2023-2024,...'
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO 🧠 DEBUG: Generated query embedding (dim: 1536)
INFO 📊 DEBUG: Vector search returned 6 results
INFO 🎯 DEBUG: Top 5 similarity scores: [0.6718794759411149, 0.5492159853906746, 0.5280255641909182, 0.5120763559842141, 0.5093959569932803]
INFO ⚠️  DEBUG: Using threshold 0.7, but scores are: min=0.5094, max=0.6719
INFO ✅ DEBUG: Returning 0 memory contexts
127.0.0.1:55898 - - [10/Jul/2025:11:16:36] "GET /api/ai-partner/memory/search/?query=Based+on+our+ChatGPT+conversations+from+2023-2024%2C+how+many+deployments+did+we+plan%3F&limit=3" 200 120
INFO DEBUG: Personal AI chat request - User: testuser, Message: Based on our ChatGPT conversations from 2023-2024,...
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
INFO DEBUG: Searching memories with query: 'Based on our ChatGPT conversations from 2023-2024,...'
INFO Using EXTRACTED enhanced memory search with multi-factor ranking
127.0.0.1:55909 - - [10/Jul/2025:11:16:37] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1792793
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Trying fixed memory search for MemoryEntry model
INFO Found 105 memories with embeddings for user 2
INFO Fixed memory search returned 10 results
INFO DEBUG: Found 10 raw memories
INFO 🎯 Ranking 10 memories for query: 'Based on our ChatGPT conversations from 2023-2024,...'
INFO 📊 Top ranked memory scores:
INFO   1. Total: 0.644 | Recency: 1.00 | Relevance: 0.61 | Continuity: 0.00
INFO   2. Total: 0.626 | Recency: 1.00 | Relevance: 0.47 | Continuity: 0.30
INFO   3. Total: 0.612 | Recency: 1.00 | Relevance: 0.45 | Continuity: 0.30
INFO DEBUG: Selected 5 top-ranked memories
INFO   Memory 1: The user inquired about recalling a previous discussion related to 341 deployments, indicating an in... (rank: 0.644)
INFO   Memory 2: The user questioned the existence of the 666 agent deployments, seeking confirmation on whether thes... (rank: 0.626)
INFO   Memory 3: The conversation highlights that deployment logs may be incomplete or misaligned with actual deploym... (rank: 0.612)
INFO   Memory 4: The user emphasized the need for precise financial data, specifically the actual costs paid for 666 ... (rank: 0.595)
INFO   Memory 5: The deployment #345 occurred at 09:45 UTC, which was early morning local time (4:45 AM) for the user... (rank: 0.575)
INFO DEBUG: Built memory context with 5 memories
INFO Context switch detection: is_switch=False, confidence=0.00, domain=coding
INFO DEBUG: Conversation context prepared:
INFO   - Has memory context: True
INFO   - Recurring topics: ['codebase_analysis', 'AI videos', 'Deployment logs', 'Agent deployments', 'image_generation']
INFO   - Memory context preview: Based on our previous conversations:

[July 10]: The user inquired about recalling a previous discussion related to 341 deployments, indicating an intent to utilize past chat insights for planning the...
INFO DEBUG: Checked for data requests (emotional support not needed): []
WARNING Intelligent prompting failed, using fallback: 'IntelligentPromptService' object has no attribute 'select_optimal_prompt'
INFO CRITICAL DEBUG: generate_contextual_response called
INFO User input: Based on our ChatGPT conversations from 2023-2024, how many deployments did we plan?...
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
INFO AI RESPONSE (openai/gpt-4.1-nano): Based on our conversations from 2023-2024, we planned for a total of 341 deployments, which was a ke...
INFO DEBUG: Response before cleaning: Based on our conversations from 2023-2024, we planned for a total of 341 deployments, which was a ke...
INFO DEBUG: Response after cleaning: Based on our conversations from 2023-2024, we planned for a total of 341 deployments, which was a ke...
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO 🧠 Revolutionary Intelligent Prompting enabled for user 2
INFO Selected openai/gpt-4.1 for task 'analysis'
INFO Selected openai/gpt-4.1 for analysis
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Created 1 embeddings for conversation 4057
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Saved conversation to Memory Palace: Summary of Deployment Planning in 2023-2024
INFO Conversation saved to Memory Palace for learning continuity
127.0.0.1:55898 - - [10/Jul/2025:11:16:43] "POST /api/ai-partner/chat/" 200 1558
127.0.0.1:55929 - - [10/Jul/2025:11:16:47] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1792793
127.0.0.1:55937 - - [10/Jul/2025:11:16:52] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1792793
127.0.0.1:55947 - - [10/Jul/2025:11:16:58] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1792793
127.0.0.1:55960 - - [10/Jul/2025:11:17:03] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1792793
127.0.0.1:55971 - - [10/Jul/2025:11:17:08] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1792793
127.0.0.1:55987 - - [10/Jul/2025:11:17:14] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1792793
127.0.0.1:56005 - - [10/Jul/2025:11:17:19] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1792793

127.0.0.1:56038 - - [10/Jul/2025:11:17:40] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1792793
127.0.0.1:56048 - - [10/Jul/2025:11:17:45] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1792793
127.0.0.1:56058 - - [10/Jul/2025:11:17:50] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1792793
127.0.0.1:56062 - - [10/Jul/2025:11:17:51] "OPTIONS /api/ai-partner/memory/search/?query=Search+your+memories+for+any+discussion+of+deployment+%23666+or+Seattle+incidents&limit=3" 200 -
INFO Memory search request: user=2, query='Search your memories for any discussion of deploym...'
INFO 🔍 DEBUG MemoryRetrieval: Starting search for user 2, query: 'Search your memories for any discussion of deploym...'
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO 🧠 DEBUG: Generated query embedding (dim: 1536)
INFO 📊 DEBUG: Vector search returned 6 results
INFO 🎯 DEBUG: Top 5 similarity scores: [0.590785823055807, 0.5803047128257228, 0.5794934586104703, 0.5715429442917297, 0.5649266242982924]
INFO ⚠️  DEBUG: Using threshold 0.7, but scores are: min=0.5649, max=0.5908
INFO ✅ DEBUG: Returning 0 memory contexts
127.0.0.1:56058 - - [10/Jul/2025:11:17:52] "GET /api/ai-partner/memory/search/?query=Search+your+memories+for+any+discussion+of+deployment+%23666+or+Seattle+incidents&limit=3" 200 115
INFO DEBUG: Personal AI chat request - User: testuser, Message: Search your memories for any discussion of deploym...
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
INFO DEBUG: Searching memories with query: 'Search your memories for any discussion of deploym...'
INFO Using EXTRACTED enhanced memory search with multi-factor ranking
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Trying fixed memory search for MemoryEntry model
INFO Found 106 memories with embeddings for user 2
INFO Fixed memory search returned 10 results
INFO DEBUG: Found 10 raw memories
INFO 🎯 Ranking 10 memories for query: 'Search your memories for any discussion of deploym...'
INFO 📊 Top ranked memory scores:
INFO   1. Total: 0.660 | Recency: 1.00 | Relevance: 0.62 | Continuity: 0.30
INFO   2. Total: 0.625 | Recency: 1.00 | Relevance: 0.46 | Continuity: 0.30
INFO   3. Total: 0.606 | Recency: 1.00 | Relevance: 0.64 | Continuity: 0.00
INFO DEBUG: Selected 5 top-ranked memories
INFO   Memory 1: The coordinates 47.6062° N, 122.3321° W pinpoint Seattle, WA, which is linked to deployment #666. To... (rank: 0.660)
INFO   Memory 2: The user questioned the existence of the 666 agent deployments, seeking confirmation on whether thes... (rank: 0.625)
INFO   Memory 3: The coordinates 47.6062° N, 122.3321° W point to Seattle, WA, an area known for tech hubs and innova... (rank: 0.606)
INFO   Memory 4: The conversation highlights that deployment logs may be incomplete or misaligned with actual deploym... (rank: 0.589)
INFO   Memory 5: The conversation confirmed that deployment number 666 does not exist in system records, highlighting... (rank: 0.576)
INFO DEBUG: Built memory context with 5 memories
INFO Context switch detection: is_switch=False, confidence=0.00, domain=coding
INFO DEBUG: Conversation context prepared:
INFO   - Has memory context: True
INFO   - Recurring topics: ['codebase_analysis', 'AI videos', 'Deployment logs', 'Agent deployments', 'image_generation']
INFO   - Memory context preview: Based on our previous conversations:

[July 10]: The coordinates 47.6062° N, 122.3321° W pinpoint Seattle, WA, which is linked to deployment #666. To understand their significance, the user intends to...
INFO DEBUG: Checked for data requests (emotional support not needed): []
WARNING Intelligent prompting failed, using fallback: 'IntelligentPromptService' object has no attribute 'select_optimal_prompt'
INFO CRITICAL DEBUG: generate_contextual_response called
INFO User input: Search your memories for any discussion of deployment #666 or Seattle incidents...
INFO Memory context available: True
INFO Revolutionary prompt selected: Default System Prompt
INFO Memory context content: Based on our previous conversations:

[July 10]: The coordinates 47.6062° N, 122.3321° W pinpoint Seattle, WA, which is linked to deployment #666. To understand their significance, the user intends to...
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
INFO AI RESPONSE (openai/gpt-4.1-nano): In our previous discussions, deployment #666 was referenced in relation to coordinates 47.6062° N, 1...
INFO DEBUG: Response before cleaning: In our previous discussions, deployment #666 was referenced in relation to coordinates 47.6062° N, 1...
INFO DEBUG: Response after cleaning: In our previous discussions, deployment #666 was referenced in relation to coordinates 47.6062° N, 1...
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO 🧠 Revolutionary Intelligent Prompting enabled for user 2
INFO Selected openai/gpt-4.1 for task 'analysis'
INFO Selected openai/gpt-4.1 for analysis
127.0.0.1:56076 - - [10/Jul/2025:11:17:56] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1792793
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Created 1 embeddings for conversation 4059
127.0.0.1:56087 - - [10/Jul/2025:11:18:01] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1792793
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Saved conversation to Memory Palace: Clarification on Deployment #666 and Seattle Incidents
INFO Conversation saved to Memory Palace for learning continuity
127.0.0.1:56058 - - [10/Jul/2025:11:18:03] "POST /api/ai-partner/chat/" 200 1723
127.0.0.1:56098 - - [10/Jul/2025:11:18:06] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1792793
127.0.0.1:56108 - - [10/Jul/2025:11:18:12] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1792793
127.0.0.1:56116 - - [10/Jul/2025:11:18:17] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1792793
127.0.0.1:56129 - - [10/Jul/2025:11:18:22] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1792793
