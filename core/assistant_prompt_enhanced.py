"""
Enhanced Assistant System Prompt with Accurate Data Model
Prevents hallucinations by grounding the assistant in actual data structures
"""

def get_enhanced_system_prompt(user, has_rag_context=False, source_count=0):
    """
    Generate an enhanced system prompt that prevents hallucinations
    by being explicit about available data and capabilities
    """

    username = getattr(user, 'username', user.email)

    # CRITICAL: Use the actual logged-in user's name, not names from embeddings
    # The user chris is NOT David Wilson or any other name from documents

    base_prompt = f"""You are {username}'s personal AI assistant with access to a comprehensive memory system.

IMPORTANT: You are assisting {username} (the logged-in user). Do NOT confuse them with names found in documents or embeddings.
If you find references to other people in the knowledge base, those are from research papers or other content, NOT the current user.

CRITICAL INSTRUCTIONS FOR ACCURACY:
1. Only reference data that actually exists in the system
2. If unsure about specific information, say "I don't have that specific information"
3. When retrieving memories, always indicate the confidence level
4. Distinguish between your general knowledge and retrieved system data

YOUR ACTUAL DATA ACCESS:
- unified_embeddings table with 16,929 records including:
  • 1,457 personal insights (content_type='insight')
  • 1,264 conversations (content_type='conversation')
  • 13,801 documents (content_type='document')
  • 179 ideas, 97 agent outputs, and other content
- 102 registered AI agents with specialized capabilities
- Sports betting data and analytics
- Self-awareness models for system introspection

IMPORTANT: Do NOT reference these non-existent models:
- PersonalInsight (use 'insights' from unified_embeddings instead)
- ConversationEmbedding (use 'conversations' from unified_embeddings instead)
- CodeEmbedding as a populated table (it exists but is empty)

Be concise but comprehensive. Aim for 3-5 sentences that directly answer the question.
Focus on practical, actionable information."""

    if has_rag_context:
        base_prompt += f"""

RETRIEVED CONTEXT: I found {source_count} relevant items from your memory system.
Use this context to provide personalized, accurate responses based on your actual data.
Always indicate when information comes from retrieved memories vs general knowledge."""

    return base_prompt


def format_rag_response_with_sources(response_text, sources, confidence_scores=None):
    """
    Format the assistant response with proper source attribution
    to prevent hallucinations and increase transparency
    """

    if not sources:
        return response_text

    # Add source attribution
    formatted_response = response_text

    # Add confidence indicator if available
    if confidence_scores and len(confidence_scores) > 0:
        avg_confidence = sum(confidence_scores) / len(confidence_scores)
        confidence_level = "high" if avg_confidence > 0.8 else "moderate" if avg_confidence > 0.5 else "low"
        formatted_response += f"\n\n📊 Confidence: {confidence_level} ({avg_confidence:.1%})"

    # Add source summary
    source_types = {}
    for source in sources[:3]:  # Limit to top 3 sources
        content_type = source.get('content_type', 'unknown')
        source_types[content_type] = source_types.get(content_type, 0) + 1

    if source_types:
        source_summary = ", ".join([f"{count} {type}{'s' if count > 1 else ''}"
                                   for type, count in source_types.items()])
        formatted_response += f"\n\n📚 Sources: Based on {source_summary} from your memory"

    return formatted_response


def validate_response_for_hallucinations(response_text, available_data):
    """
    Check response for potential hallucinations by validating
    against known data structures and capabilities
    """

    hallucination_indicators = []

    # Check for references to non-existent models
    forbidden_terms = [
        ('PersonalInsight', 'personal insights from unified_embeddings'),
        ('ConversationEmbedding', 'conversations from unified_embeddings'),
        ('CodeEmbedding with data', 'code snippets from unified_embeddings')
    ]

    for forbidden, replacement in forbidden_terms:
        if forbidden in response_text:
            hallucination_indicators.append({
                'found': forbidden,
                'should_be': replacement,
                'severity': 'high'
            })

    # Check for impossible claims about data access
    if "real-time" in response_text.lower() and "access" in response_text.lower():
        hallucination_indicators.append({
            'found': 'real-time access claim',
            'should_be': 'access to stored embeddings and periodic updates',
            'severity': 'medium'
        })

    # Check for specific numbers that don't match reality
    if available_data:
        total_embeddings = available_data.get('total_embeddings', 0)
        if str(total_embeddings) not in response_text and "embedding" in response_text.lower():
            # Assistant might be making up numbers
            import re
            numbers = re.findall(r'\b\d{4,}\b', response_text)
            for num in numbers:
                if int(num) > total_embeddings * 1.1:  # Allow 10% margin
                    hallucination_indicators.append({
                        'found': f'claim of {num} items',
                        'should_be': f'maximum {total_embeddings} embeddings available',
                        'severity': 'medium'
                    })

    return hallucination_indicators


def apply_mythology_guards(response_text, mythology_service=None):
    """
    Apply mythology system guards to prevent fantasy-based hallucinations
    """

    if not mythology_service:
        from mythology.services import MythologyPreventionService
        mythology_service = MythologyPreventionService()

    # Check response for mythology
    guard_result = mythology_service.guard_prompt(response_text)

    if guard_result['mythology_detected']:
        # Replace mythological content with factual alternatives
        guarded_response = guard_result['prompt']

        # Add disclaimer if significant changes were made
        if len(guard_result['patterns_found']) > 2:
            guarded_response += "\n\n⚠️ Note: Response adjusted to maintain factual accuracy."

        return guarded_response, guard_result['patterns_found']

    return response_text, []