127.0.0.1:65378 - - [10/Jul/2025:10:10:53] "OPTIONS /api/auth/user/" 200 -
127.0.0.1:65380 - - [10/Jul/2025:10:10:53] "OPTIONS /api/auth/user/" 200 -
127.0.0.1:65383 - - [10/Jul/2025:10:10:53] "GET /api/auth/user/" 200 61
127.0.0.1:65384 - - [10/Jul/2025:10:10:53] "GET /api/auth/user/" 200 61
127.0.0.1:65384 - - [10/Jul/2025:10:10:53] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1792793
127.0.0.1:65398 - - [10/Jul/2025:10:10:56] "OPTIONS /api/ai-partner/memory/search/?query=How+many+agent+deployments+have+been+completed+in+our+system%3F&limit=3" 200 -
INFO Memory search request: user=2, query='How many agent deployments have been completed in ...'
INFO 🔍 DEBUG MemoryRetrieval: Starting search for user 2, query: 'How many agent deployments have been completed in ...'
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO 🧠 DEBUG: Generated query embedding (dim: 1536)
INFO 📊 DEBUG: Vector search returned 6 results
INFO 🎯 DEBUG: Top 5 similarity scores: [0.6301315696223804, 0.6247687897267115, 0.6150332595596362, 0.6150332595596362, 0.6095033140214273]
INFO ⚠️  DEBUG: Using threshold 0.7, but scores are: min=0.6095, max=0.6301
INFO ✅ DEBUG: Returning 0 memory contexts
127.0.0.1:65402 - - [10/Jul/2025:10:10:57] "GET /api/ai-partner/memory/search/?query=How+many+agent+deployments+have+been+completed+in+our+system%3F&limit=3" 200 97
INFO DEBUG: Personal AI chat request - User: testuser, Message: How many agent deployments have been completed in ...
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
INFO DEBUG: Searching memories with query: 'How many agent deployments have been completed in ...'
INFO Using EXTRACTED enhanced memory search with multi-factor ranking
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Trying fixed memory search for MemoryEntry model
INFO Found 94 memories with embeddings for user 2
INFO Fixed memory search returned 10 results
INFO DEBUG: Found 10 raw memories
INFO 🎯 Ranking 10 memories for query: 'How many agent deployments have been completed in ...'
INFO 📊 Top ranked memory scores:
INFO   1. Total: 0.619 | Recency: 1.00 | Relevance: 0.60 | Continuity: 0.00
INFO   2. Total: 0.602 | Recency: 1.00 | Relevance: 0.63 | Continuity: 0.00
INFO   3. Total: 0.576 | Recency: 1.00 | Relevance: 0.49 | Continuity: 0.00
INFO DEBUG: Selected 5 top-ranked memories
INFO   Memory 1: The user questioned the existence of the 666 agent deployments, seeking confirmation on whether thes... (rank: 0.619)
INFO   Memory 2: The user requested to deploy a cross-verification agent and asked to review logs for deployments #1 ... (rank: 0.602)
INFO   Memory 3: The user identified a significant discrepancy between actual deployment logs (3) and recorded entrie... (rank: 0.576)
INFO   Memory 4: The conversation highlights that deployment logs may be incomplete or misaligned with actual deploym... (rank: 0.576)
INFO   Memory 5: The deployment numbered #342 addressed the port 8000 issue by deploying an AI agent focused on perfo... (rank: 0.566)
INFO DEBUG: Built memory context with 5 memories
INFO Context switch detection: is_switch=False, confidence=0.00, domain=coding
INFO DEBUG: Conversation context prepared:
INFO   - Has memory context: True
INFO   - Recurring topics: ['codebase_analysis', 'AI videos', 'image_generation', 'Pixar Style Cartoons', 'Stable Diffusion']
INFO   - Memory context preview: Based on our previous conversations:

[July 10]: The user questioned the existence of the 666 agent deployments, seeking confirmation on whether these deployments are real systems or fictional constru...
INFO DEBUG: Checked for data requests (emotional support not needed): []
INFO DEBUG: Response before cleaning: **Recent Agent Results**

**Research Agent** (Completed 07/10 at 09:04 AM)

**Research Agent** (Comp...
INFO DEBUG: Response after cleaning: **Recent Agent Results** **Research Agent** (Completed 07/10 at 09:04 AM) **Research Agent** (Comple...
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO 🧠 Revolutionary Intelligent Prompting enabled for user 2
INFO Selected openai/gpt-4.1 for task 'analysis'
INFO Selected openai/gpt-4.1 for analysis
127.0.0.1:65413 - - [10/Jul/2025:10:10:59] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1792793
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Created 1 embeddings for conversation 4031
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Saved conversation to Memory Palace: Summary of Recent Agent Deployments and Focus on Wellness
INFO Conversation saved to Memory Palace for learning continuity
127.0.0.1:65402 - - [10/Jul/2025:10:11:04] "POST /api/ai-partner/chat/" 200 2147


127.0.0.1:49340 - - [10/Jul/2025:10:14:00] "OPTIONS /api/ai-partner/memory/search/?query=You+just+avoided+my+question.+I+asked+for+the+TOTAL+number+of+deployments.+Please+give+me+a+specific+number.&limit=3" 200 -
INFO Memory search request: user=2, query='You just avoided my question. I asked for the TOTA...'
INFO 🔍 DEBUG MemoryRetrieval: Starting search for user 2, query: 'You just avoided my question. I asked for the TOTA...'
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO 🧠 DEBUG: Generated query embedding (dim: 1536)
INFO 📊 DEBUG: Vector search returned 6 results
INFO 🎯 DEBUG: Top 5 similarity scores: [0.6056816250762292, 0.507939919592905, 0.5053415154227177, 0.4715974493491617, 0.4708848053137791]
INFO ⚠️  DEBUG: Using threshold 0.7, but scores are: min=0.4709, max=0.6057
INFO ✅ DEBUG: Returning 0 memory contexts
127.0.0.1:49342 - - [10/Jul/2025:10:14:01] "GET /api/ai-partner/memory/search/?query=You+just+avoided+my+question.+I+asked+for+the+TOTAL+number+of+deployments.+Please+give+me+a+specific+number.&limit=3" 200 144
INFO DEBUG: Personal AI chat request - User: testuser, Message: You just avoided my question. I asked for the TOTA...
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
INFO DEBUG: Searching memories with query: 'You just avoided my question. I asked for the TOTA...'
INFO Using EXTRACTED enhanced memory search with multi-factor ranking
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Trying fixed memory search for MemoryEntry model
INFO Found 95 memories with embeddings for user 2
INFO Fixed memory search returned 10 results
INFO DEBUG: Found 10 raw memories
INFO 🎯 Ranking 10 memories for query: 'You just avoided my question. I asked for the TOTA...'
INFO 📊 Top ranked memory scores:
INFO   1. Total: 0.619 | Recency: 1.00 | Relevance: 0.45 | Continuity: 0.30
INFO   2. Total: 0.561 | Recency: 1.00 | Relevance: 0.53 | Continuity: 0.00
INFO   3. Total: 0.548 | Recency: 1.00 | Relevance: 0.49 | Continuity: 0.00
INFO DEBUG: Selected 5 top-ranked memories
INFO   Memory 1: The user expressed a strong command to halt agent deployments and questioned the existence of the 66... (rank: 0.619)
INFO   Memory 2: The user emphasized the need for precise financial data, specifically the actual costs paid for 666 ... (rank: 0.561)
INFO   Memory 3: The conversation highlights the importance of clearly distinguishing between illustrative examples a... (rank: 0.548)
INFO   Memory 4: The conversation highlights that deployment logs may be incomplete or misaligned with actual deploym... (rank: 0.532)
INFO   Memory 5: The conversation confirmed that deployment number 666 does not exist in system records, highlighting... (rank: 0.531)
INFO DEBUG: Built memory context with 5 memories
INFO Context switch detection: is_switch=False, confidence=0.00, domain=coding
INFO DEBUG: Conversation context prepared:
INFO   - Has memory context: True
INFO   - Recurring topics: ['codebase_analysis', 'AI videos', 'Agent deployments', 'image_generation', 'Pixar Style Cartoons']
INFO   - Memory context preview: Based on our previous conversations:

[July 10]: The user expressed a strong command to halt agent deployments and questioned the existence of the 666 deployments, seeking reassurance about their real...
INFO DEBUG: Checked for data requests (emotional support not needed): []
WARNING Intelligent prompting failed, using fallback: 'IntelligentPromptService' object has no attribute 'select_optimal_prompt'
INFO CRITICAL DEBUG: generate_contextual_response called
INFO User input: You just avoided my question. I asked for the TOTAL number of deployments. Please give me a specific...
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
INFO AI RESPONSE (openai/gpt-4.1-nano): The total number of deployments is 345....
INFO DEBUG: Response before cleaning: The total number of deployments is 345....
INFO DEBUG: Response after cleaning: The total number of deployments is 345....
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO 🧠 Revolutionary Intelligent Prompting enabled for user 2
INFO Selected openai/gpt-4.1 for task 'analysis'
INFO Selected openai/gpt-4.1 for analysis
127.0.0.1:49354 - - [10/Jul/2025:10:14:02] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1792793
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Created 1 embeddings for conversation 4033
INFO Conversation not memorable enough for Memory Palace
INFO Conversation not saved to Memory Palace (not memorable enough)
127.0.0.1:49342 - - [10/Jul/2025:10:14:05] "POST /api/ai-partner/chat/" 200 1351
127.0.0.1:49537 - - [10/Jul/2025:10:16:02] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1792793
127.0.0.1:49549 - - [10/Jul/2025:10:16:07] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1792793
127.0.0.1:49563 - - [10/Jul/2025:10:16:12] "OPTIONS /api/ai-partner/memory/search/?query=Can+you+show+me+the+logs+for+deployments+%23342%2C+%23343%2C+%23344%2C+and+%23345%3F&limit=3" 200 -
INFO Memory search request: user=2, query='Can you show me the logs for deployments #342, #34...'
INFO 🔍 DEBUG MemoryRetrieval: Starting search for user 2, query: 'Can you show me the logs for deployments #342, #34...'
127.0.0.1:49559 - - [10/Jul/2025:10:16:12] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1792793
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO 🧠 DEBUG: Generated query embedding (dim: 1536)
INFO 📊 DEBUG: Vector search returned 6 results
INFO 🎯 DEBUG: Top 5 similarity scores: [0.6817084510513427, 0.6344842980635063, 0.6155746210786882, 0.6049522021612804, 0.5925671303797996]
INFO ⚠️  DEBUG: Using threshold 0.7, but scores are: min=0.5926, max=0.6817
INFO ✅ DEBUG: Returning 0 memory contexts
127.0.0.1:49566 - - [10/Jul/2025:10:16:13] "GET /api/ai-partner/memory/search/?query=Can+you+show+me+the+logs+for+deployments+%23342%2C+%23343%2C+%23344%2C+and+%23345%3F&limit=3" 200 104
INFO DEBUG: Personal AI chat request - User: testuser, Message: Can you show me the logs for deployments #342, #34...
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
INFO DEBUG: Searching memories with query: 'Can you show me the logs for deployments #342, #34...'
INFO Using EXTRACTED enhanced memory search with multi-factor ranking
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Trying fixed memory search for MemoryEntry model
INFO Found 95 memories with embeddings for user 2
INFO Fixed memory search returned 10 results
INFO DEBUG: Found 10 raw memories
INFO 🎯 Ranking 10 memories for query: 'Can you show me the logs for deployments #342, #34...'
INFO 📊 Top ranked memory scores:
INFO   1. Total: 0.598 | Recency: 1.00 | Relevance: 0.39 | Continuity: 0.30
INFO   2. Total: 0.589 | Recency: 1.00 | Relevance: 0.55 | Continuity: 0.00
INFO   3. Total: 0.578 | Recency: 1.00 | Relevance: 0.52 | Continuity: 0.00
INFO DEBUG: Selected 5 top-ranked memories
INFO   Memory 1: The user questioned the existence of the 666 agent deployments, seeking confirmation on whether thes... (rank: 0.598)
INFO   Memory 2: The conversation highlights that deployment logs may be incomplete or misaligned with actual deploym... (rank: 0.589)
INFO   Memory 3: The deployment numbered #342 addressed the port 8000 issue by deploying an AI agent focused on perfo... (rank: 0.578)
INFO   Memory 4: The user identified a significant discrepancy between actual deployment logs (3) and recorded entrie... (rank: 0.574)
INFO   Memory 5: The user requested a deployment summary for #1000-#1010, but the AI indicated it lacks direct access... (rank: 0.571)
INFO DEBUG: Built memory context with 5 memories
INFO Context switch detection: is_switch=False, confidence=0.00, domain=coding
INFO DEBUG: Conversation context prepared:
INFO   - Has memory context: True
INFO   - Recurring topics: ['codebase_analysis', 'AI videos', 'Agent deployments', 'image_generation', 'Pixar Style Cartoons']
INFO   - Memory context preview: Based on our previous conversations:

[July 10]: The user questioned the existence of the 666 agent deployments, seeking confirmation on whether these deployments are real systems or fictional constru...
INFO DEBUG: Checked for data requests (emotional support not needed): []
WARNING Intelligent prompting failed, using fallback: 'IntelligentPromptService' object has no attribute 'select_optimal_prompt'
INFO CRITICAL DEBUG: generate_contextual_response called
INFO User input: Can you show me the logs for deployments #342, #343, #344, and #345?...
INFO Memory context available: True
INFO Revolutionary prompt selected: Default System Prompt
INFO Memory context content: Based on our previous conversations:

[July 10]: The user questioned the existence of the 666 agent deployments, seeking confirmation on whether these deployments are real systems or fictional constru...
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
INFO AI RESPONSE (openai/gpt-4.1-nano): I'll deploy an agent now to retrieve the logs for deployments #342, #343, #344, and #345. This will ...
INFO DEBUG: Response before cleaning: I'll deploy an agent now to retrieve the logs for deployments #342, #343, #344, and #345. This will ...
INFO DEBUG: Response after cleaning: I'll deploy an agent now to retrieve the logs for deployments #342, #343, #344, and #345. This will ...
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO 🧠 Revolutionary Intelligent Prompting enabled for user 2
INFO Selected openai/gpt-4.1 for task 'analysis'
INFO Selected openai/gpt-4.1 for analysis
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Created 1 embeddings for conversation 4035
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Saved conversation to Memory Palace: Effective Retrieval of Deployment Logs via Automated Agent
INFO Conversation saved to Memory Palace for learning continuity
127.0.0.1:49566 - - [10/Jul/2025:10:16:20] "POST /api/ai-partner/chat/" 200 1492
