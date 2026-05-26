<!-- DOC-POINTER-V2 (Session 1160) -->
> **Status:** Superseded
> **Last verified:** Session 1160 (2026-05-26)
> **Current canon:** [`docs/PLATFORM_INVENTORY.md`](../PLATFORM_INVENTORY.md) (runtime-derived, autogen) + [`docs/PLATFORM_WHAT_IT_IS.md`](../PLATFORM_WHAT_IT_IS.md) (narrative).
> **Change reason:** Jan 21 local Ollama repo-review output. Snapshot, not authoritative review.
> **Preserved because:** historical local-LLM review output. Useful as build-history; do NOT cite for current state.

# Repo Review (local Ollama: qwen2.5:14b-instruct)

### Repository Review Summary

#### 1. Top Risks and Broken Links

- **Missing Spider Registration**: The `ai_core/spiders/spider_registry.py` file indicates that some critical spiders (e.g., financial API spiders) are built but not registered in the spider registry.
  
- **Orphaned Agents**: There are orphaned agents that need to be loaded. This is mentioned as a quick win, but it's important to ensure these agents are integrated properly.

- **Incomplete WebSocket Routes**: The README indicates that some WebSocket routes may still be incomplete or missing integration points.

- **Revenue Attribution Issues**: Revenue attribution needs to be implemented to track earnings from AI-generated activities accurately.

#### 2. Quick Wins (<=10 Bullet Points)

- **Register Missing Spiders**:
  - Register the `CoinGeckoSpider` and `YahooFinanceSpider`.
  
- **Load Orphaned Agents**:
  - Load 11 orphaned agents to ensure they are operational.
  
- **Revenue Attribution**:
  - Implement revenue attribution logic to track earnings from AI activities.

- **Learning Verification**:
  - Ensure that the learning verification system is in place and functioning correctly.

- **Orchestration Consolidation**:
  - Clean up and consolidate orchestration code for better maintainability.

- **Fix WebSocket Routes**:
  - Complete any missing or broken WebSocket routes to ensure real-time communication works seamlessly.
  
- **Frontend Integration**:
  - Ensure the frontend is fully integrated with backend services, especially for revenue tracking and income builder functionalities.

#### 3. Ollama Integration Checks

The `scripts/review/repo_review_with_ollama.py` script checks connectivity to an Ollama server (or OpenAI if available) by performing a chat ping and embeddings ping:

```python
def check_connectivity() -> None:
    # Chat ping
    pong = ollama_chat([{"role":"user","content":"Reply with OK"}], max_tokens=5, temperature=0)
    print(f"[repo-review] chat ping: {pong!r}", flush=True)

    # Embeddings ping
    emb_payload = {"model": EMB_MODEL, "input": "hello"}
    er = post_ollama(EMB_URL, emb_payload)
    er.raise_for_status()
    ed = er.json()
    dim = len(ed.get("data", [{}])[0].get("embedding", []) or [])
    print(f"[repo-review] embeddings dim: {dim}", flush=True)
```

This ensures that the Ollama server is reachable and functioning correctly.

#### 4. Next Actions for 75%→90% Integration

- **Register Missing Spiders**:
  - Add `CoinGeckoSpider` and `YahooFinanceSpider` to the spider registry in `ai_core/spiders/spider_registry.py`.

```python
self.register_spider('coingecko', CoinGeckoSpider, {
    'category': 'financial',
    'priority': 1,
    'rate_limit': 1.0,
    'targets': ['api.coingecko.com']
})

self.register_spider('yahoo_finance', YahooFinanceSpider, {
    'category': 'financial',
    'priority': 1,
    'rate_limit': 1.0,
    'targets': ['finance.yahoo.com']
})
```

- **Load Orphaned Agents**:
  - Ensure that the `universal_agent_loader.py` script loads all orphaned agents.

```python
def load_orphaned_agents():
    # Load specific agent classes here
    for template in UnifiedAgentTemplate.objects.filter(is_active=True, is_loaded=False):
        agent_name = template.name.replace('-', '_')
        agent_config = {
            'id': str(template.id),
            'name': template.name,
            'type': template.specialization,
            'capabilities': template.capabilities or [],
            'description': template.description,
            'configuration': template.llm_config or {},
            'is_active': template.is_active,
            'system_prompt': template.system_prompt,
            'domain_tags': template.domain_tags or [],
            'tool_integrations': template.tool_integrations or {}
        }
        agent_registry.register(agent_name, AIEnforcedAgent, config=agent_config)
```

- **Implement Revenue Attribution**:
  - Add revenue tracking logic in `ai_core/revenue_integration.py`.

```python
def track_revenue(opportunity_id: str, amount: float):
    # Track revenue for a given opportunity ID and amount
    pass

# Example usage
track_revenue('opportunity_123', 50.0)
```

- **Ensure Learning Verification**:
  - Implement learning verification in `ai_core/learning_verification.py`.

```python
def verify_learning(agent_id: str, data_points: List[Dict]):
    # Verify that the agent has learned from provided data points
    pass

# Example usage
verify_learning('agent_456', [{'data': 'example_data'}, {'data': 'another_example'}])
```

- **Consolidate Orchestration**:
  - Refactor orchestration code in `ai_core/agents/orchestration.py` for better readability and maintainability.

```python
def consolidate_orchestration():
    # Consolidate orchestration logic here
    pass

# Example usage
consolidate_orchestration()
```

- **Fix WebSocket Routes**:
  - Ensure all WebSocket routes are correctly defined in `ai_core/urls.py`.

```python
websocket_urlpatterns = [
    path('ws/revenue/', RevenueWebSocket.as_asgi()),
    path('ws/sports/', SportsWebSocket.as_asgi()),
]
```

By addressing these points, the system can move from 75% to 90% integration.
