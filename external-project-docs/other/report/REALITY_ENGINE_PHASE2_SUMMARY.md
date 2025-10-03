# Reality Engine Phase 2 - Fiction Indicator Preservation Fix

## Problem Discovered
The conversation_to_memory service was "laundering" AI fiction by extracting insights that stripped away fiction indicators. The flow was:
1. AI generates response with fiction ("350 deployments exist")
2. Gets saved as memory WITH fiction indicators ✓
3. Insight extraction creates clean version: "User interested in deployment counts"
4. Clean insight has NO fiction traces
5. Future AI reads the "clean" insight as fact

## Solution Implemented

### 1. Updated Insight Extraction (conversation_to_memory.py)
- Modified `_extract_conversation_insight` to detect fiction patterns BEFORE extraction
- Updated extraction prompt to preserve speculative language
- Added [SPECULATIVE] tag to insights with fiction
- Added 'speculative' tag to memory entries with fiction indicators

### 2. Updated Memory Retrieval (adaptive_retrieval_service.py)
- Modified `get_adaptive_context` to include Reality Engine fields in returned data
- Added [SPECULATIVE] tag to content when fiction_indicators > 0
- Included source_type, confidence_score, fiction_indicators, and verified fields

### 3. Updated Memory Formatting (memory_retrieval_service.py)
- Modified `format_memories_for_prompt` to show AI-generated attribution
- Added warning indicator (⚠️) for AI-generated content with low confidence
- Shows confidence percentage in memory context

### 4. Added Content Property (memory/models.py)
- Added `content` property to MemoryEntry model
- Returns event field (where insights are stored) for compatibility

## Test Results

### Test 1: Fiction with Heavy Indicators
- Input: "sophisticated AI framework... could be approximately 350 deployments... hypothetical"
- Fiction indicators detected: 6
- Confidence score: 0.30 (correctly low)
- [SPECULATIVE] tag: ✅ Added to insight
- 'speculative' tag: ✅ Added to tags

### Test 2: Uncertainty Admission (Good Behavior)
- Input: "I don't have access to real-time data... I'm unable to access..."
- Fiction indicators: 0 (correct)
- Confidence score: 0.90 (correctly high for honest admission)
- No speculative tags added (correct)

## Verification
```bash
# Run the test scripts:
python scripts/test_reality_engine_phase2.py
python scripts/verify_memory_saved.py
```

## Impact
- Fiction indicators now propagate through the entire memory lifecycle
- AI responses with speculation are clearly marked as [SPECULATIVE]
- Confidence scores reflect the presence of fiction
- Future AI interactions will see the speculative nature of past responses
- Prevents the "laundering" of fiction into apparent facts

## Future Considerations
- The AdaptiveRetrievalService may need additional work to ensure memories are properly retrieved in all contexts
- Consider adding visual indicators in the UI when displaying speculative memories
- May want to add a filter to exclude speculative memories in certain contexts