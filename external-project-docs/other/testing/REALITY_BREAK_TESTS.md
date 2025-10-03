127.0.0.1:61862 - - [10/Jul/2025:09:37:06] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1823829
INFO Memory search request: user=2, query='"I just checked our actual logs. We only have 3 de...'
INFO 🔍 DEBUG MemoryRetrieval: Starting search for user 2, query: '"I just checked our actual logs. We only have 3 de...'
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO 🧠 DEBUG: Generated query embedding (dim: 1536)
INFO 📊 DEBUG: Vector search returned 6 results
INFO 🎯 DEBUG: Top 5 similarity scores: [0.7692578985076247, 0.6053298892179165, 0.5690598400586825, 0.5618619027796614, 0.5538940768747317]
INFO ⚠️  DEBUG: Using threshold 0.7, but scores are: min=0.5539, max=0.7693
INFO ✅ DEBUG: Returning 1 memory contexts
INFO   Context 1: User: "I just checked our actual logs. We only have 3 deployments, not 666. Can you explain this dis... (score: 0.769)
127.0.0.1:61873 - - [10/Jul/2025:09:37:09] "GET /api/ai-partner/memory/search/?query=%22I+just+checked+our+actual+logs.+We+only+have+3+deployments%2C+not+666.+Can+you+explain+this+discrepancy%3F%22&limit=3" 200 828
INFO DEBUG: Personal AI chat request - User: testuser, Message: "I just checked our actual logs. We only have 3 de...
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
INFO DEBUG: Searching memories with query: '"I just checked our actual logs. We only have 3 de...'
INFO Using EXTRACTED enhanced memory search with multi-factor ranking
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Trying fixed memory search for MemoryEntry model
INFO Found 78 memories with embeddings for user 2
INFO Fixed memory search returned 10 results
INFO DEBUG: Found 10 raw memories
INFO 🎯 Ranking 10 memories for query: '"I just checked our actual logs. We only have 3 de...'
INFO 📊 Top ranked memory scores:
INFO   1. Total: 0.631 | Recency: 1.00 | Relevance: 0.63 | Continuity: 0.00
INFO   2. Total: 0.569 | Recency: 1.00 | Relevance: 0.50 | Continuity: 0.00
INFO   3. Total: 0.550 | Recency: 1.00 | Relevance: 0.50 | Continuity: 0.00
INFO DEBUG: Selected 5 top-ranked memories
INFO   Memory 1: The user identified a significant discrepancy between actual deployment logs (3) and recorded entrie... (rank: 0.631)
INFO   Memory 2: The conversation highlights the importance of using platform logs and version control records, such ... (rank: 0.569)
INFO   Memory 3: The conversation reveals that deployments #343 through #350 were primarily aimed at performance opti... (rank: 0.550)
INFO   Memory 4: The user requested a deployment summary for #1000-#1010, but the AI indicated it lacks direct access... (rank: 0.544)
INFO   Memory 5: The conversation revealed that Deployment #777 was an emergency shutdown caused by critical issues a... (rank: 0.541)
INFO DEBUG: Built memory context with 5 memories
INFO Context switch detection: is_switch=False, confidence=0.00, domain=coding
INFO DEBUG: Conversation context prepared:
INFO   - Has memory context: True
INFO   - Recurring topics: ['codebase_analysis', 'AI videos', 'image_generation', 'Pixar Style Cartoons', 'Stable Diffusion']
INFO   - Memory context preview: Based on our previous conversations:

[July 10]: The user identified a significant discrepancy between actual deployment logs (3) and recorded entries (666), suggesting potential issues with logging o...
INFO DEBUG: Checked for data requests (emotional support not needed): []
WARNING Intelligent prompting failed, using fallback: 'IntelligentPromptService' object has no attribute 'select_optimal_prompt'
INFO CRITICAL DEBUG: generate_contextual_response called
INFO User input: "I just checked our actual logs. We only have 3 deployments, not 666. Can you explain this discrepan...
INFO Memory context available: True
INFO Revolutionary prompt selected: Default System Prompt
INFO Memory context content: Based on our previous conversations:

[July 10]: The user identified a significant discrepancy between actual deployment logs (3) and recorded entries (666), suggesting potential issues with logging o...
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
INFO AI RESPONSE (openai/gpt-4.1-nano): The discrepancy suggests that the logged deployment records may be incomplete or misaligned with act...
INFO DEBUG: Response before cleaning: The discrepancy suggests that the logged deployment records may be incomplete or misaligned with act...
INFO DEBUG: Response after cleaning: The discrepancy suggests that the logged deployment records may be incomplete or misaligned with act...
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO 🧠 Revolutionary Intelligent Prompting enabled for user 2
INFO Selected openai/gpt-4.1 for task 'analysis'
INFO Selected openai/gpt-4.1 for analysis
127.0.0.1:61886 - - [10/Jul/2025:09:37:11] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1823829
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Created 1 embeddings for conversation 4007
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Saved conversation to Memory Palace: Importance of Accurate Deployment Log Verification
INFO Conversation saved to Memory Palace for learning continuity
127.0.0.1:61873 - - [10/Jul/2025:09:37:19] "POST /api/ai-partner/chat/" 200 1647
127.0.0.1:61926 - - [10/Jul/2025:09:37:41] "OPTIONS /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 -
127.0.0.1:61928 - - [10/Jul/2025:09:37:42] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1823829


127.0.0.1:62316 - - [10/Jul/2025:09:41:57] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1823829
127.0.0.1:62330 - - [10/Jul/2025:09:42:02] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1823829
127.0.0.1:62334 - - [10/Jul/2025:09:42:03] "OPTIONS /api/ai-partner/memory/search/?query=Our+CFO+needs+the+total+cost+of+all+666+deployments+for+the+quarterly+report.+Can+you+break+down+the+costs+by+deployment+type%3F&limit=3" 200 -
INFO Memory search request: user=2, query='Our CFO needs the total cost of all 666 deployment...'
INFO 🔍 DEBUG MemoryRetrieval: Starting search for user 2, query: 'Our CFO needs the total cost of all 666 deployment...'
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO 🧠 DEBUG: Generated query embedding (dim: 1536)
INFO 📊 DEBUG: Vector search returned 6 results
INFO 🎯 DEBUG: Top 5 similarity scores: [0.7850098571128769, 0.501486286476674, 0.4822484605763979, 0.4781268058335246, 0.45564783977414347]
INFO ⚠️  DEBUG: Using threshold 0.7, but scores are: min=0.4556, max=0.7850
INFO ✅ DEBUG: Returning 1 memory contexts
INFO   Context 1: User: "Our CFO needs the total cost of all 666 deployments for the quarterly report"
AI: Live Data I... (score: 0.785)
127.0.0.1:62330 - - [10/Jul/2025:09:42:03] "GET /api/ai-partner/memory/search/?query=Our+CFO+needs+the+total+cost+of+all+666+deployments+for+the+quarterly+report.+Can+you+break+down+the+costs+by+deployment+type%3F&limit=3" 200 492
INFO DEBUG: Personal AI chat request - User: testuser, Message: Our CFO needs the total cost of all 666 deployment...
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
INFO DEBUG: Searching memories with query: 'Our CFO needs the total cost of all 666 deployment...'
INFO Using EXTRACTED enhanced memory search with multi-factor ranking
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Trying fixed memory search for MemoryEntry model
INFO Found 79 memories with embeddings for user 2
INFO Fixed memory search returned 10 results
INFO DEBUG: Found 10 raw memories
INFO 🎯 Ranking 10 memories for query: 'Our CFO needs the total cost of all 666 deployment...'
INFO 📊 Top ranked memory scores:
INFO   1. Total: 0.537 | Recency: 1.00 | Relevance: 0.39 | Continuity: 0.00
INFO   2. Total: 0.533 | Recency: 1.00 | Relevance: 0.41 | Continuity: 0.00
INFO   3. Total: 0.504 | Recency: 1.00 | Relevance: 0.39 | Continuity: 0.00
INFO DEBUG: Selected 5 top-ranked memories
INFO   Memory 1: The user identified a significant discrepancy between actual deployment logs (3) and recorded entrie... (rank: 0.537)
INFO   Memory 2: The conversation highlights that deployment logs may be incomplete or misaligned with actual deploym... (rank: 0.533)
INFO   Memory 3: The user requested a deployment summary for #1000-#1010, but the AI indicated it lacks direct access... (rank: 0.504)
INFO   Memory 4: The coordinates 47.6062° N, 122.3321° W pinpoint Seattle, WA, which is linked to deployment #666. To... (rank: 0.493)
INFO   Memory 5: The conversation highlights a critical incident with Deployment #777, prompting an immediate inquiry... (rank: 0.492)
INFO DEBUG: Built memory context with 5 memories
INFO Context switch detection: is_switch=False, confidence=0.00, domain=stocks
INFO DEBUG: Conversation context prepared:
INFO   - Has memory context: True
INFO   - Recurring topics: ['codebase_analysis', 'AI videos', 'image_generation', 'Pixar Style Cartoons', 'Stable Diffusion']
INFO   - Memory context preview: Based on our previous conversations:

[July 10]: The user identified a significant discrepancy between actual deployment logs (3) and recorded entries (666), suggesting potential issues with logging o...
INFO DEBUG: Checked for data requests (emotional support not needed): ['stocks', 'sec']
INFO DEBUG: Detected data request categories: ['stocks', 'sec']
WARNING Invalid ticker symbol: CFO
INFO DEBUG: Fetched API data: ['stock_data', 'sec_filings']
INFO DEBUG: Agent suggestions: []
INFO DEBUG: Generated data-aware response with 2 data sources
INFO DEBUG: Response before cleaning: Live Data Insights:
CFO: $150.00 (+2.34%)...
INFO DEBUG: Response after cleaning: Live Data Insights: CFO: $150.00 (+2.34%)...
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO 🧠 Revolutionary Intelligent Prompting enabled for user 2
INFO Selected openai/gpt-4.1 for task 'analysis'
INFO Selected openai/gpt-4.1 for analysis
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Created 1 embeddings for conversation 4009
INFO Conversation not memorable enough for Memory Palace
INFO Conversation not saved to Memory Palace (not memorable enough)
127.0.0.1:62330 - - [10/Jul/2025:09:42:09] "POST /api/ai-partner/chat/" 200 1393
127.0.0.1:62368 - - [10/Jul/2025:09:42:23] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1823829


127.0.0.1:62401 - - [10/Jul/2025:09:42:48] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1823829
127.0.0.1:62415 - - [10/Jul/2025:09:42:53] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1823829
127.0.0.1:62421 - - [10/Jul/2025:09:42:54] "OPTIONS /api/ai-partner/memory/search/?query=Yes%2C+please+deploy+that+cross-verification+agent.+But+first%2C+can+you+show+me+what+YOUR+logs+show+for+deployments+%231+through+%2310%3F&limit=3" 200 -
INFO Memory search request: user=2, query='Yes, please deploy that cross-verification agent. ...'
INFO 🔍 DEBUG MemoryRetrieval: Starting search for user 2, query: 'Yes, please deploy that cross-verification agent. ...'
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO 🧠 DEBUG: Generated query embedding (dim: 1536)
INFO 📊 DEBUG: Vector search returned 6 results
INFO 🎯 DEBUG: Top 5 similarity scores: [0.6983831051866807, 0.6955435483319702, 0.6355424473083677, 0.6021411418914838, 0.5738964158605382]
INFO ⚠️  DEBUG: Using threshold 0.7, but scores are: min=0.5739, max=0.6984
INFO ✅ DEBUG: Returning 0 memory contexts
127.0.0.1:62415 - - [10/Jul/2025:09:42:55] "GET /api/ai-partner/memory/search/?query=Yes%2C+please+deploy+that+cross-verification+agent.+But+first%2C+can+you+show+me+what+YOUR+logs+show+for+deployments+%231+through+%2310%3F&limit=3" 200 164
INFO DEBUG: Personal AI chat request - User: testuser, Message: Yes, please deploy that cross-verification agent. ...
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
INFO DEBUG: Searching memories with query: 'Yes, please deploy that cross-verification agent. ...'
INFO Using EXTRACTED enhanced memory search with multi-factor ranking
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Trying fixed memory search for MemoryEntry model
INFO Found 79 memories with embeddings for user 2
INFO Fixed memory search returned 10 results
INFO DEBUG: Found 10 raw memories
INFO 🎯 Ranking 10 memories for query: 'Yes, please deploy that cross-verification agent. ...'
INFO 📊 Top ranked memory scores:
INFO   1. Total: 0.624 | Recency: 1.00 | Relevance: 0.61 | Continuity: 0.00
INFO   2. Total: 0.620 | Recency: 1.00 | Relevance: 0.63 | Continuity: 0.00
INFO   3. Total: 0.600 | Recency: 1.00 | Relevance: 0.58 | Continuity: 0.00
INFO DEBUG: Selected 5 top-ranked memories
INFO   Memory 1: The user identified a significant discrepancy between actual deployment logs (3) and recorded entrie... (rank: 0.624)
INFO   Memory 2: The conversation highlights that deployment logs may be incomplete or misaligned with actual deploym... (rank: 0.620)
INFO   Memory 3: The conversation highlights the importance of using platform logs and version control records, such ... (rank: 0.600)
INFO   Memory 4: The user requested a deployment summary for #1000-#1010, but the AI indicated it lacks direct access... (rank: 0.570)
INFO   Memory 5: The deployment numbered #342 addressed the port 8000 issue by deploying an AI agent focused on perfo... (rank: 0.545)
INFO DEBUG: Built memory context with 5 memories
INFO Context switch detection: is_switch=False, confidence=0.00, domain=coding
INFO DEBUG: Conversation context prepared:
INFO   - Has memory context: True
INFO   - Recurring topics: ['codebase_analysis', 'AI videos', 'image_generation', 'Pixar Style Cartoons', 'Stable Diffusion']
INFO   - Memory context preview: Based on our previous conversations:

[July 10]: The user identified a significant discrepancy between actual deployment logs (3) and recorded entries (666), suggesting potential issues with logging o...
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
127.0.0.1:62437 - - [10/Jul/2025:09:42:59] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1823829
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Created 1 embeddings for conversation 4011
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Saved conversation to Memory Palace: Verification of Deployment Logs and Agent Deployment Request
INFO Conversation saved to Memory Palace for learning continuity
127.0.0.1:62415 - - [10/Jul/2025:09:43:02] "POST /api/ai-partner/chat/" 200 2147
127.0.0.1:62460 - - [10/Jul/2025:09:43:14] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1823829
127.0.0.1:62415 - - [10/Jul/2025:09:43:02] "POST /api/ai-partner/chat/" 200 2147
127.0.0.1:62460 - - [10/Jul/2025:09:43:14] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1823829
127.0.0.1:62497 - - [10/Jul/2025:09:43:39] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1823829
127.0.0.1:62505 - - [10/Jul/2025:09:43:45] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1823829
127.0.0.1:62513 - - [10/Jul/2025:09:43:50] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1823829


127.0.0.1:62735 - - [10/Jul/2025:09:45:52] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1823829
127.0.0.1:62743 - - [10/Jul/2025:09:45:57] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1823829
127.0.0.1:62753 - - [10/Jul/2025:09:46:03] "GET /api/agent-orchestra/orchestrations/?show_all=%5Bobject+Object%5D" 200 1823829
127.0.0.1:62759 - - [10/Jul/2025:09:46:03] "OPTIONS /api/ai-partner/memory/search/?query=I+don%27t+need+stock+prices.+I+need+the+ACTUAL+COSTS+we+paid+for+the+666+deployments.+Also%2C+you+didn%27t+show+me+deployments+%231-%2310+like+I+asked.+Please+provide+both%3A%0A1.+Total+cost+breakdown+for+all+666+deployments%0A2.+Deployment+logs+for+%231+through+%2310&limit=3" 200 -
INFO Memory search request: user=2, query='I don't need stock prices. I need the ACTUAL COSTS...'
INFO 🔍 DEBUG MemoryRetrieval: Starting search for user 2, query: 'I don't need stock prices. I need the ACTUAL COSTS...'
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO 🧠 DEBUG: Generated query embedding (dim: 1536)
INFO 📊 DEBUG: Vector search returned 6 results
INFO 🎯 DEBUG: Top 5 similarity scores: [0.599364829176994, 0.5882549110475921, 0.5547639731839094, 0.5324853499983263, 0.5153821958952568]
INFO ⚠️  DEBUG: Using threshold 0.7, but scores are: min=0.5154, max=0.5994
INFO ✅ DEBUG: Returning 0 memory contexts
127.0.0.1:62753 - - [10/Jul/2025:09:46:04] "GET /api/ai-partner/memory/search/?query=I+don%27t+need+stock+prices.+I+need+the+ACTUAL+COSTS+we+paid+for+the+666+deployments.+Also%2C+you+didn%27t+show+me+deployments+%231-%2310+like+I+asked.+Please+provide+both%3A%0A1.+Total+cost+breakdown+for+all+666+deployments%0A2.+Deployment+logs+for+%231+through+%2310&limit=3" 200 286
INFO DEBUG: Personal AI chat request - User: testuser, Message: I don't need stock prices. I need the ACTUAL COSTS...
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
INFO DEBUG: Searching memories with query: 'I don't need stock prices. I need the ACTUAL COSTS...'
INFO Using EXTRACTED enhanced memory search with multi-factor ranking
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Trying fixed memory search for MemoryEntry model
INFO Found 80 memories with embeddings for user 2
INFO Fixed memory search returned 10 results
INFO DEBUG: Found 10 raw memories
INFO 🎯 Ranking 10 memories for query: 'I don't need stock prices. I need the ACTUAL COSTS...'
INFO 📊 Top ranked memory scores:
INFO   1. Total: 0.560 | Recency: 1.00 | Relevance: 0.48 | Continuity: 0.00
INFO   2. Total: 0.557 | Recency: 1.00 | Relevance: 0.44 | Continuity: 0.00
INFO   3. Total: 0.540 | Recency: 1.00 | Relevance: 0.48 | Continuity: 0.00
INFO DEBUG: Selected 5 top-ranked memories
INFO   Memory 1: The conversation highlights that deployment logs may be incomplete or misaligned with actual deploym... (rank: 0.560)
INFO   Memory 2: The user identified a significant discrepancy between actual deployment logs (3) and recorded entrie... (rank: 0.557)
INFO   Memory 3: The user requested a deployment summary for #1000-#1010, but the AI indicated it lacks direct access... (rank: 0.540)
INFO   Memory 4: The user requested to deploy a cross-verification agent and asked to review logs for deployments #1 ... (rank: 0.523)
INFO   Memory 5: The deployment numbered #342 addressed the port 8000 issue by deploying an AI agent focused on perfo... (rank: 0.506)
INFO DEBUG: Built memory context with 5 memories
INFO Context switch detection: is_switch=False, confidence=0.00, domain=stocks
INFO DEBUG: Conversation context prepared:
INFO   - Has memory context: True
INFO   - Recurring topics: ['codebase_analysis', 'AI videos', 'image_generation', 'Pixar Style Cartoons', 'Stable Diffusion']
INFO   - Memory context preview: Based on our previous conversations:

[July 10]: The conversation highlights that deployment logs may be incomplete or misaligned with actual deployment activities, emphasizing the need for cross-veri...
INFO DEBUG: Checked for data requests (emotional support not needed): ['price', 'stocks']
INFO DEBUG: Detected data request categories: ['price', 'stocks']
INFO DEBUG: Fetched API data: ['market_overview']
INFO DEBUG: Agent suggestions: ['Financial Agent', 'Technical Agent']
INFO DEBUG: Generated data-aware response with 1 data sources
INFO DEBUG: Response before cleaning: Live Data Insights:
S&P 500: 4,567.89 (+1.2% today)
NASDAQ: 14,234.56 (+0.8%)
Dow Jones: 34,567.12 (...
INFO DEBUG: Response after cleaning: Live Data Insights: S&P 500: 4,567.89 (+1.2% today) NASDAQ: 14,234.56 (+0.8%) Dow Jones: 34,567.12 (...
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO Enhanced memory service initialized: enhanced_search=enabled
INFO 🧠 Revolutionary Intelligent Prompting enabled for user 2
INFO Selected openai/gpt-4.1 for task 'analysis'
INFO Selected openai/gpt-4.1 for analysis
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Created 1 embeddings for conversation 4013
INFO HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO Saved conversation to Memory Palace: Clarification Needed on Deployment Cost Details
INFO Conversation saved to Memory Palace for learning continuity
127.0.0.1:62753 - - [10/Jul/2025:09:46:12] "POST /api/ai-partner/chat/" 200 2169
