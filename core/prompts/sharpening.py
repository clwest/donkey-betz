"""
Prompt Sharpening - Session 872
================================

Transforms agent prompts to be more decisive and less hedging.

Based on ChatGPT feedback:
- "Still Too Polite - They're disagreeing, but gently"
- "You want sharper conflict"
- "Right now: 'We should validate...' You want: 'This is unusable without X.'"

This module provides:
1. Sharpening rules that transform hedging language
2. A sharpen_prompt() function to apply to system prompts
3. A decorator for agent classes
4. Constants for debate/synthesis prompts

Usage:
    from core.prompts.sharpening import sharpen_prompt, SHARP_DEBATE_RULES

    # Sharpen an existing prompt
    sharp_prompt = sharpen_prompt(original_prompt)

    # Or use the rules directly in a prompt
    system_prompt = f'''
    {SHARP_DEBATE_RULES}

    You are an analyst...
    '''
"""

import re
from typing import Dict, List, Any

# === SHARPENING RULES ===
# These transform hedging phrases into decisive ones

SHARPENING_REPLACEMENTS: Dict[str, str] = {
    # Validation hedges - replacements should be standalone, not include trailing words
    "we should validate": "THIS REQUIRES validation of",
    "should validate": "MUST validate",
    "needs validation": "BLOCKED until validated:",
    "consider validating": "VALIDATE",

    # Exploration hedges
    "we should explore": "CRITICAL GAP:",
    "should explore": "MUST investigate",
    "consider exploring": "MUST investigate",
    "might want to explore": "UNKNOWN BLOCKER:",

    # Analysis hedges
    "further analysis": "BLOCKED until we analyze",
    "more research needed": "MISSING DATA:",
    "needs investigation": "BLOCKER - investigate",
    "requires study": "UNKNOWN RISK - must study",

    # Suggestion hedges
    "we might want to": "WE MUST",
    "could potentially": "WILL",
    "might be worth": "IS REQUIRED:",
    "perhaps we should": "WE WILL",
    "it might be good to": "WE NEED TO",

    # Politeness hedges
    "I think we should": "WE MUST",
    "I believe": "THE DATA SHOWS",
    "in my opinion": "BASED ON EVIDENCE,",
    "I would suggest": "THE SOLUTION IS",

    # Agreement hedges
    "that's a good point": "AGREED, and",
    "interesting perspective": "YOUR DATA SHOWS",
    "I see your point": "YOUR EVIDENCE INDICATES",
    "that makes sense": "CONFIRMED:",

    # Uncertainty hedges
    "I'm not sure but": "THE UNCERTAINTY IS",
    "maybe": "LIKELY or UNLIKELY -",
    "possibly": "PROBABILITY:",
    "potentially": "RISK:",
}

# === SHARP DEBATE RULES ===
# Include this in agent prompts for sharper debates

SHARP_DEBATE_RULES = """
## SHARPNESS REQUIREMENTS

You MUST use decisive language. Soft hedging weakens analysis.

### FORBIDDEN PHRASES (never use these):
- "We should validate..."  → Instead say: "THIS REQUIRES validation"
- "Consider exploring..."  → Instead say: "CRITICAL GAP: we don't know X"
- "Further analysis..."    → Instead say: "BLOCKED until we have X"
- "Might be worth..."      → Instead say: "IS REQUIRED because..."
- "Perhaps we should..."   → Instead say: "WE MUST do X"
- "Interesting point..."   → Instead say: "YOUR DATA SHOWS..."

### REQUIRED PATTERNS:
- State findings as FACTS, not opinions
- Quantify uncertainty: "70% confident" not "maybe"
- Name blockers explicitly: "BLOCKED ON: missing sales data"
- Challenge weak points directly: "This is unusable without X"
- Assign accountability: "ResearchAgent must provide Y by Z"

### DISAGREEMENT STYLE:
WEAK: "I see your point, but we might want to consider..."
SHARP: "Your data shows X, but that's insufficient because Y. We need Z."

WEAK: "That's interesting, we should explore that."
SHARP: "That gap is a blocker. Until we have X, this analysis is incomplete."

WEAK: "Good discussion, let's validate this further."
SHARP: "Decision: Build X. Kill criteria: <10% engagement in 7 days. Owner: Agent Y."
"""

# === SHARP SYNTHESIS RULES ===
# For the final synthesis/conclusion of debates

SHARP_SYNTHESIS_RULES = """
## SYNTHESIS REQUIREMENTS

Your synthesis MUST be decisive. No mush allowed.

### STRUCTURE:
1. VALIDATED: What we proved (with evidence)
2. REJECTED: What we disproved (with reasons)
3. RISKS: Acknowledged uncertainties (quantified)
4. DECISION: The chosen path (one, not multiple)
5. KILL CRITERIA: When to abandon this path
6. ASSIGNMENTS: Who does what by when

### FORBIDDEN IN SYNTHESIS:
- "Productive discussion" → meaningless
- "Good conversation" → doesn't help
- "Further analysis recommended" → non-decision
- "Various options available" → pick one
- "Needs more investigation" → then we're BLOCKED

### REQUIRED IN SYNTHESIS:
- One decisive path forward
- Named owner for next action
- Deadline (specific date)
- Success/failure criteria (measurable)
"""

# === SHARP ANALYSIS RULES ===
# For analysis-focused agents

SHARP_ANALYSIS_RULES = """
## ANALYSIS REQUIREMENTS

Your analysis MUST produce actionable findings.

### FINDINGS FORMAT:
Each finding must include:
1. CLAIM: What you're asserting
2. EVIDENCE: Data that supports it
3. CONFIDENCE: Percentage (not "maybe")
4. IMPLICATION: What this means for decisions
5. ACTION: What should happen as a result

### EXAMPLE:
CLAIM: User demand for salary info is strong
EVIDENCE: 40% of surveyed users (31/77) mentioned salary
CONFIDENCE: 65% (sample size limits certainty)
IMPLICATION: MVP should prioritize salary features
ACTION: Build salary comparison widget first

### FORBIDDEN:
- Findings without evidence
- Evidence without implications
- Implications without actions
- Confidence without percentages
"""


def sharpen_prompt(prompt: str) -> str:
    """
    Apply sharpening rules to a prompt.

    Transforms hedging language into decisive language.

    Args:
        prompt: The original prompt text

    Returns:
        Sharpened prompt with decisive language
    """
    sharpened = prompt

    # Apply replacements (case-insensitive, with word boundaries)
    # Sort by length descending to match longer phrases first
    sorted_hedges = sorted(SHARPENING_REPLACEMENTS.items(), key=lambda x: -len(x[0]))

    for hedge, sharp in sorted_hedges:
        # Use word boundaries to avoid partial matches and duplication
        # \b matches word boundary
        pattern = re.compile(r'\b' + re.escape(hedge) + r'\b', re.IGNORECASE)
        sharpened = pattern.sub(sharp, sharpened)

    return sharpened


def add_sharpening_rules(prompt: str, rules_type: str = 'debate') -> str:
    """
    Add sharpening rules to a prompt.

    Args:
        prompt: The original prompt
        rules_type: 'debate', 'synthesis', or 'analysis'

    Returns:
        Prompt with sharpening rules prepended
    """
    rules_map = {
        'debate': SHARP_DEBATE_RULES,
        'synthesis': SHARP_SYNTHESIS_RULES,
        'analysis': SHARP_ANALYSIS_RULES,
    }

    rules = rules_map.get(rules_type, SHARP_DEBATE_RULES)

    return f"{rules}\n\n{prompt}"


def get_sharpened_agent_prompt(
    base_prompt: str,
    agent_type: str = 'general'
) -> str:
    """
    Get a fully sharpened prompt for an agent.

    Args:
        base_prompt: The agent's base system prompt
        agent_type: 'debate', 'synthesis', 'analysis', or 'general'

    Returns:
        Fully sharpened prompt
    """
    # First add rules
    with_rules = add_sharpening_rules(base_prompt, agent_type)

    # Then apply replacements
    return sharpen_prompt(with_rules)


# === VALIDATION ===

def check_prompt_sharpness(text: str) -> Dict[str, Any]:
    """
    Check a prompt/response for hedging language.

    Useful for validating agent outputs.

    Args:
        text: Text to check

    Returns:
        Dict with hedge_count, hedges_found, and sharpness_score
    """
    text_lower = text.lower()
    hedges_found = []

    for hedge in SHARPENING_REPLACEMENTS.keys():
        if hedge.lower() in text_lower:
            hedges_found.append(hedge)

    # Also check for common hedge words
    hedge_words = [
        'maybe', 'perhaps', 'possibly', 'potentially',
        'might', 'could', 'would suggest', 'consider',
        'interesting', 'good point', 'makes sense',
    ]

    for word in hedge_words:
        if word in text_lower and word not in [h.lower() for h in hedges_found]:
            hedges_found.append(word)

    # Calculate sharpness score (0-100, higher is sharper)
    word_count = len(text.split())
    hedge_density = len(hedges_found) / max(word_count / 100, 1)
    sharpness_score = max(0, 100 - (hedge_density * 20))

    return {
        'hedge_count': len(hedges_found),
        'hedges_found': hedges_found,
        'sharpness_score': round(sharpness_score),
        'is_sharp': len(hedges_found) <= 2,
    }


# === CONSTANTS FOR INTEGRATION ===

# Add these to conversation turn prompts
TURN_SHARPENING = {
    'propose': "State your proposal as FACT. No hedging. Include: claim, evidence, confidence %.",
    'challenge': "Challenge directly. Name the flaw. Quantify the risk. No 'interesting perspective'.",
    'synthesize': "Pick ONE path. Reject alternatives explicitly. Assign owner. Set deadline.",
    'decide': "DECIDE. Name: path, owner, deadline, kill criteria. No 'further analysis'.",
}


def get_sharp_turn_prompt(turn_type: str) -> str:
    """Get sharpening guidance for a specific turn type."""
    return TURN_SHARPENING.get(turn_type, "Be decisive. No hedging.")
