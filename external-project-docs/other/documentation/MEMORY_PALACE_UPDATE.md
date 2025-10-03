# Memory Palace Integration Plan

## 🎯 Goal: Connect Memory Palace UI to Backend Data

### Phase 1: Create Memory Palace API Views (Immediate)

```python
# backend/memory/views_memory_palace.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from ai_partner.models import ConversationMemory
from .models import MemoryEntry, SymbolicMemoryAnchor, MemoryChain

class MemoryPalaceViewSet(viewsets.ViewSet):
    """Unified API for Memory Palace frontend"""
    
    @action(detail=False, methods=['post'])
    def semantic_search(self, request):
        """Search across all memory types"""
        query = request.data.get('query')
        
        # Search conversation memories
        conversation_results = self.search_conversations(query, request.user)
        
        # Search reflection memories
        reflection_results = self.search_reflections(query, request.user)
        
        # Search documents (if implemented)
        document_results = self.search_documents(query, request.user)
        
        return Response({
            'conversations': conversation_results,
            'reflections': reflection_results,
            'documents': document_results,
            'total_results': len(conversation_results) + len(reflection_results) + len(document_results)
        })
    
    @action(detail=False, methods=['get'])
    def knowledge_graph(self, request):
        """Get knowledge graph data"""
        # Get symbolic anchors as nodes
        anchors = SymbolicMemoryAnchor.objects.filter(user=request.user)
        
        # Get memory connections as edges
        chains = MemoryChain.objects.filter(user=request.user)
        
        nodes = [{
            'id': f'anchor_{anchor.id}',
            'label': anchor.name,
            'type': 'anchor',
            'strength': anchor.reinforcement_count
        } for anchor in anchors]
        
        edges = []
        for chain in chains:
            memories = chain.memories.all()
            for i in range(len(memories) - 1):
                edges.append({
                    'source': f'memory_{memories[i].id}',
                    'target': f'memory_{memories[i+1].id}',
                    'type': 'chain'
                })
        
        return Response({
            'nodes': nodes,
            'edges': edges
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get memory statistics"""
        return Response({
            'total_memories': ConversationMemory.objects.filter(user=request.user).count(),
            'knowledge_nodes': SymbolicMemoryAnchor.objects.filter(user=request.user).count(),
            'documents': 0,  # Implement document counting
            'ai_insights': MemoryEntry.objects.filter(
                user=request.user,
                reflection_generated=True
            ).count()
        })
```

### Phase 2: Unify Memory Systems

```python
# backend/memory/integration/unified_memory_service.py

class UnifiedMemoryService:
    """Service to unify AI Partner and Memory reflection systems"""
    
    def sync_conversation_to_reflection(self, conversation_memory):
        """Create reflection memory from conversation"""
        memory_entry = MemoryEntry.objects.create(
            user=conversation_memory.user,
            content=conversation_memory.message_content,
            source='conversation',
            emotion=conversation_memory.emotion_label,
            importance=conversation_memory.priority_score * 10,
            metadata={
                'original_id': conversation_memory.id,
                'context': conversation_memory.context_type,
                'ai_response': conversation_memory.ai_response
            }
        )
        
        # Auto-link to anchors
        self.auto_link_to_anchors(memory_entry)
        
        return memory_entry
    
    def create_knowledge_node(self, user, concept, related_memories):
        """Create a knowledge node from related memories"""
        anchor = SymbolicMemoryAnchor.objects.create(
            user=user,
            name=concept,
            description=f"Knowledge node for {concept}",
            emotional_resonance='neutral',
            first_activation=timezone.now()
        )
        
        # Link memories to anchor
        for memory in related_memories:
            memory.anchors.add(anchor)
        
        return anchor
```

### Phase 3: Connect Research Intelligence

```python
# backend/agent_orchestra/views_research_intelligence.py

# Add to existing ResearchIntelligenceViewSet
@action(detail=False, methods=['post'])
def save_to_memory_palace(self, request):
    """Save research results to Memory Palace"""
    research_id = request.data.get('research_id')
    selected_results = request.data.get('selected_results', [])
    
    research = ResearchResult.objects.get(id=research_id, user=request.user)
    
    # Create memory entries for selected results
    for result in selected_results:
        MemoryEntry.objects.create(
            user=request.user,
            content=result['summary'],
            source='research',
            importance=result.get('relevance_score', 5) * 10,
            metadata={
                'research_id': research_id,
                'source_type': result['source'],
                'url': result.get('url'),
                'query': research.query
            }
        )
    
    return Response({'status': 'saved', 'count': len(selected_results)})
```

### Phase 4: Agent Memory Integration

```python
# backend/agent_orchestra/memory_integration.py

# Update existing AgentMemoryIntegration
class EnhancedAgentMemoryIntegration(AgentMemoryIntegration):
    """Enhanced integration with Memory Palace"""
    
    def store_agent_insight(self, agent_instance, insight):
        """Store agent-generated insights in Memory Palace"""
        memory = MemoryEntry.objects.create(
            user=agent_instance.orchestration.user,
            content=insight['content'],
            source='agent',
            importance=insight.get('importance', 7),
            metadata={
                'agent_name': agent_instance.agent_template.name,
                'orchestration_id': agent_instance.orchestration.id,
                'task': agent_instance.assigned_task,
                'confidence': insight.get('confidence', 0.8)
            }
        )
        
        # Create knowledge node if significant
        if insight.get('importance', 7) >= 8:
            self.create_knowledge_node_from_insight(memory, insight)
        
        return memory
```

### Phase 5: Frontend Connection Updates

```javascript
// Update MemoryPalace.tsx to use real endpoints

const fetchMemoryStats = async () => {
  try {
    const response = await api.get('/api/memory/palace/stats/');
    setStats([
      { label: 'Total Memories', value: response.data.total_memories, icon: Database, color: '#a855f7' },
      { label: 'Knowledge Nodes', value: response.data.knowledge_nodes, icon: Network, color: '#06b6d4' },
      { label: 'Documents', value: response.data.documents, icon: FileText, color: '#6366f1' },
      { label: 'AI Insights', value: response.data.ai_insights, icon: Brain, color: '#ec4899' },
    ]);
  } catch (error) {
    console.error('Failed to fetch memory stats:', error);
  }
};

const performSemanticSearch = async (query: string) => {
  try {
    const response = await api.post('/api/memory/palace/semantic_search/', { query });
    return response.data;
  } catch (error) {
    console.error('Search failed:', error);
    return { conversations: [], reflections: [], documents: [] };
  }
};
```

## 🎯 Expected Outcomes

### For Users:
1. **Unified Memory View** - See all memories in one place
2. **Knowledge Graph** - Visualize connections between ideas
3. **Powerful Search** - Find any memory across all sources
4. **AI Insights** - See what agents learned about them

### For the System:
1. **Data Consistency** - One source of truth for memories
2. **Better Context** - Agents can access all memory types
3. **Learning Loop** - System improves based on memory patterns
4. **Research Integration** - Research becomes part of memory

## 📊 Implementation Priority

1. **Week 1**: Create API endpoints (Phase 1)
2. **Week 2**: Unify memory systems (Phase 2)
3. **Week 3**: Connect Research Intelligence (Phase 3)
4. **Week 4**: Agent integration (Phase 4)
5. **Week 5**: Frontend updates and testing (Phase 5)

## 🔑 Key Benefits

- **No Lost Data** - Every interaction is captured
- **Contextual Intelligence** - AI understands user deeply
- **Knowledge Building** - Ideas connect and grow
- **Personal Wikipedia** - User's own knowledge base