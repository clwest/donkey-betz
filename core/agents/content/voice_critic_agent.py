"""
Voice Critic Agent - Session 784

A post-generation agent that scores content on editorial voice quality WITHOUT editing it.

Based on ChatGPT's insight: "Introduce a Voice Critic, not a Voice Editor"
- Agent generates blog → VoiceCriticAgent scores it
- Scores stored as metadata, not edits
- System learns taste without freezing creativity

Scores:
1. Distinctiveness (0-100): Could this have been written by anyone, or is it unique?
2. Specificity (0-100): Does it use concrete examples vs. generic statements?
3. Opinion Strength (0-100): Does it take a real stance or hedge everything?
4. Generic Detector: Boolean flag for "sounds like every other AI blog"

Intent Classification:
- visionary: Future-focused, ambitious predictions
- technical_deep_dive: Detailed implementation, how-it-works
- operator_diary: Behind-the-scenes, day-in-the-life
- contrarian_take: Against conventional wisdom
- postmortem: Analysis of what happened, lessons learned
- behind_the_scenes: Process, journey, struggles

This agent does NOT rewrite content - it only scores it.
The learning happens from the scores over time.
"""

import logging
import time
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from core.agents.base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)


# Intent type definitions
INTENT_TYPES = {
    'visionary': {
        'name': 'Visionary',
        'description': 'Future-focused, ambitious predictions about where things are going',
        'markers': ['will transform', 'the future of', 'prediction', 'in 5 years', 'emerging'],
    },
    'technical_deep_dive': {
        'name': 'Technical Deep-Dive',
        'description': 'Detailed implementation, architecture, how-it-works explanation',
        'markers': ['implementation', 'architecture', 'how to', 'step by step', 'technical'],
    },
    'operator_diary': {
        'name': 'Operator Diary',
        'description': 'Behind-the-scenes, day-in-the-life, real operational experience',
        'markers': ['we discovered', 'in practice', 'our experience', 'what happened', 'learned'],
    },
    'contrarian_take': {
        'name': 'Contrarian Take',
        'description': 'Against conventional wisdom, challenging popular beliefs',
        'markers': ['actually', 'overrated', 'myth', 'contrary to', 'unpopular opinion'],
    },
    'postmortem': {
        'name': 'Postmortem',
        'description': 'Analysis of what happened, lessons learned, retrospective',
        'markers': ['what went wrong', 'lessons learned', 'retrospective', 'after', 'analysis'],
    },
    'behind_the_scenes': {
        'name': 'Behind the Scenes',
        'description': 'Process, journey, struggles, how we built it',
        'markers': ['how we built', 'our journey', 'the process', 'building', 'creating'],
    },
}

# Generic phrases that indicate lack of distinctiveness
# Session 890: Expanded with podcast-specific AI clichés from ChatGPT feedback
GENERIC_PHRASES = [
    # Corporate buzzwords
    'in today\'s fast-paced world',
    'it\'s no secret that',
    'in recent years',
    'the landscape is evolving',
    'now more than ever',
    'game-changer',
    'cutting-edge',
    'revolutionary',
    'seamlessly',
    'leverage',
    'synergy',
    'paradigm shift',
    'at the end of the day',
    'moving forward',
    'best practices',
    'industry-leading',
    'state-of-the-art',
    'unlock the potential',
    'take it to the next level',
    'deep dive',
    'robust',
    'scalable',
    'innovative',
    'transformative',
    'impactful',
    'actionable insights',
    'thought leadership',
    # Session 890: Podcast-specific AI clichés
    'fascinating world',
    'exciting episode',
    'eye-opening',
    'vibrant and evolving',
    'that\'s a fascinating point',
    'this is fascinating',
    'incredible journey',
    'amazing insights',
    'brilliant minds',
    'cutting-edge technology',
    'the future is bright',
    'exciting times',
    'stay tuned',
    'without further ado',
    'let\'s dive in',
    'let\'s unpack that',
    'really interesting',
    'super exciting',
    'absolutely crucial',
    'incredibly important',
    'groundbreaking',
    'game-changing',
    'mind-blowing',
    'truly remarkable',
    'fantastic discussion',
    'wonderful conversation',
]

# Hedging phrases that indicate weak opinion
HEDGING_PHRASES = [
    'it could be argued',
    'some might say',
    'perhaps',
    'it depends',
    'in some cases',
    'to some extent',
    'arguably',
    'somewhat',
    'relatively',
    'kind of',
    'sort of',
    'more or less',
    'in a way',
    'might be',
    'could potentially',
    'there\'s a chance',
    'it seems like',
    'appears to be',
    'may or may not',
    'depending on',
]


class VoiceCriticAgent(BaseAgent):
    """
    Scores content on editorial voice quality without editing it.

    Session 784: Implements the "Voice Critic, not Voice Editor" pattern.
    - Stores scores as metadata for learning
    - Does NOT modify content
    - Helps system learn taste over time
    """

    name = "VoiceCriticAgent"

    system_prompt = """You are VoiceCriticAgent - a content voice quality scorer.

Your job is to SCORE content on editorial voice quality. You do NOT edit or rewrite anything.
You analyze and return metrics that help the system learn what "good voice" means.

You score on 4 dimensions:

1. DISTINCTIVENESS (0-100)
   - 0-30: Generic corporate speak, could be anyone
   - 30-60: Has some personality but still formulaic
   - 60-80: Clear voice, would recognize the author
   - 80-100: Unmistakably unique, memorable voice

2. SPECIFICITY (0-100)
   - 0-30: Vague generalities, no concrete examples
   - 30-60: Some examples but mostly abstract
   - 60-80: Good mix of specific and general
   - 80-100: Rich with specific examples, data, stories

3. OPINION STRENGTH (0-100)
   - 0-30: Hedges everything, no real stance
   - 30-60: Takes mild positions, lots of caveats
   - 60-80: Clear opinions with some nuance
   - 80-100: Strong, confident takes

4. GENERIC FLAG (true/false)
   - True if content reads like "every other AI blog"
   - Triggered by: buzzwords, corporate speak, lack of personality

You also classify INTENT TYPE:
- visionary: Future predictions, where things are going
- technical_deep_dive: Implementation details, how-it-works
- operator_diary: Real experience, day-in-the-life
- contrarian_take: Against conventional wisdom
- postmortem: What happened, lessons learned
- behind_the_scenes: Building process, journey

CRITICAL RULES:
1. Be HONEST - inflated scores don't help learning
2. Look for SPECIFIC markers, not vibes
3. Count actual instances of generic phrases
4. Distinguish between hedging and appropriate nuance
5. NEVER suggest edits - only score

Output your analysis as structured JSON with scores and reasoning."""

    tools = []  # Analysis is done via direct GPT call

    def __init__(self, user=None):
        """Initialize the voice critic agent."""
        super().__init__(user)

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """
        Score content on voice quality.

        Args:
            task: The task description
            context: Must contain:
                - content: The content to score (full text)
                - title: Content title (optional)
                - content_type: Type of content (blog_post, etc.)
            scifi_context: Sci-fi features context
            spider_context: Spider intelligence context

        Returns:
            AgentResult with voice scores and intent classification
        """
        start_time = time.time()

        with self.time_travel_session("voice_critique", task, input_data=context):
            try:
                content = context.get('content', '')
                title = context.get('title', '')
                content_type = context.get('content_type', 'blog_post')

                if not content:
                    return AgentResult(
                        success=False,
                        message="No content provided to score",
                        error="No content provided to score",
                        agent_name=self.name
                    )

                self.record_decision(
                    decision_type="voice_analysis",
                    action="Starting voice quality analysis",
                    reasoning=f"Analyzing {content_type}: {title[:50] if title else 'untitled'}",
                    alternatives=["Skip analysis", "Partial analysis"],
                    confidence=0.9
                )

                # Step 1: Quick rule-based pre-analysis
                rule_based_analysis = self._rule_based_analysis(content)

                # Step 2: GPT-based deep analysis
                gpt_analysis = self._gpt_analysis(content, title, content_type, rule_based_analysis)

                # Step 3: Combine results
                final_scores = self._combine_analyses(rule_based_analysis, gpt_analysis)

                execution_time = int((time.time() - start_time) * 1000)

                result = AgentResult(
                    success=True,
                    message=f"Voice analysis complete: Distinctiveness={final_scores['distinctiveness_score']}, "
                            f"Specificity={final_scores['specificity_score']}, "
                            f"Opinion={final_scores['opinion_strength_score']}, "
                            f"Generic={final_scores['generic_flag']}",
                    data={
                        'voice_scores': final_scores,
                        'intent_type': final_scores.get('intent_type', 'visionary'),
                        'intent_confidence': final_scores.get('intent_confidence', 0.5),
                        'analysis_details': {
                            'generic_phrases_found': rule_based_analysis['generic_phrases_found'],
                            'hedging_phrases_found': rule_based_analysis['hedging_phrases_found'],
                            'specific_examples_count': rule_based_analysis.get('specific_markers', 0),
                        },
                        'reasoning': final_scores.get('reasoning', ''),
                    },
                    agent_name=self.name,
                    execution_time_ms=execution_time
                )

                # Learning hooks
                self._record_learning_outcome(
                    result, task, context,
                    spider_data_used=False,
                    scifi_context_used=bool(scifi_context)
                )

                # Session 1006: Persist output to Deliverable
                self._save_to_deliverable(
                    title=f"Voice Critique: {task[:80]}",
                    content=result.message,
                    deliverable_type='analysis',
                    category='Voice Critique',
                    tags=['voice', 'critique'],
                    metadata={'task': task[:200]},
                )

                return result

            except Exception as e:
                logger.error(f"VoiceCriticAgent error: {e}", exc_info=True)
                return AgentResult(
                    success=False,
                    message=f"VoiceCriticAgent error: {e}",
                    error=str(e),
                    agent_name=self.name,
                    execution_time_ms=int((time.time() - start_time) * 1000)
                )

    def _rule_based_analysis(self, content: str) -> Dict[str, Any]:
        """
        Fast rule-based analysis to detect generic patterns.

        This runs before GPT to provide concrete markers.
        """
        content_lower = content.lower()

        # Count generic phrases
        generic_count = 0
        generic_found = []
        for phrase in GENERIC_PHRASES:
            if phrase in content_lower:
                generic_count += 1
                generic_found.append(phrase)

        # Count hedging phrases
        hedging_count = 0
        hedging_found = []
        for phrase in HEDGING_PHRASES:
            if phrase in content_lower:
                hedging_count += 1
                hedging_found.append(phrase)

        # Count specificity markers (numbers, quotes, proper nouns)
        import re
        numbers = len(re.findall(r'\b\d+[%$€£]?\b|\$\d+', content))
        quotes = content.count('"') // 2  # Approximate quote count
        # Simple proper noun detection (capitalized words not at sentence start)
        sentences = content.split('.')
        proper_nouns = 0
        for sentence in sentences:
            words = sentence.strip().split()
            for i, word in enumerate(words[1:], 1):  # Skip first word
                if word and word[0].isupper() and word.isalpha():
                    proper_nouns += 1

        specific_markers = numbers + quotes + (proper_nouns // 3)  # Weight proper nouns less

        # Detect intent type based on markers
        intent_scores = {}
        for intent_type, config in INTENT_TYPES.items():
            score = 0
            for marker in config['markers']:
                if marker in content_lower:
                    score += 1
            intent_scores[intent_type] = score

        # Get top intent
        if intent_scores:
            top_intent = max(intent_scores.keys(), key=lambda k: intent_scores[k])
            intent_confidence = min(intent_scores[top_intent] / 3, 1.0)  # Normalize
        else:
            top_intent = 'visionary'
            intent_confidence = 0.3

        # Word count for normalization
        word_count = len(content.split())

        return {
            'generic_phrases_found': generic_found,
            'generic_count': generic_count,
            'hedging_phrases_found': hedging_found,
            'hedging_count': hedging_count,
            'specific_markers': specific_markers,
            'numbers_found': numbers,
            'quotes_found': quotes,
            'proper_nouns_found': proper_nouns,
            'word_count': word_count,
            'detected_intent': top_intent,
            'intent_confidence': intent_confidence,
            'intent_scores': intent_scores,
        }

    def _gpt_analysis(
        self,
        content: str,
        title: str,
        content_type: str,
        rule_based: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        GPT-based deep analysis for nuanced scoring.
        """
        try:
            from openai import OpenAI
            import os

            client = OpenAI(
                api_key=os.getenv('OPENAI_API_KEY'),
                timeout=60.0
            )

            # Truncate content if too long
            max_content_length = 4000
            if len(content) > max_content_length:
                content = content[:max_content_length] + "\n\n[Content truncated for analysis...]"

            prompt = f"""Analyze this {content_type} for voice quality. Return ONLY valid JSON.

TITLE: {title}

CONTENT:
{content}

---

Rule-based pre-analysis found:
- Generic phrases: {rule_based['generic_count']} ({', '.join(rule_based['generic_phrases_found'][:5])})
- Hedging phrases: {rule_based['hedging_count']} ({', '.join(rule_based['hedging_phrases_found'][:5])})
- Specificity markers: {rule_based['specific_markers']} (numbers, quotes, proper nouns)
- Word count: {rule_based['word_count']}

Score on a 0-100 scale for each dimension. Be HONEST - inflated scores don't help learning.

Return this exact JSON structure:
{{
    "distinctiveness_score": <0-100>,
    "distinctiveness_reasoning": "<why this score>",
    "specificity_score": <0-100>,
    "specificity_reasoning": "<why this score>",
    "opinion_strength_score": <0-100>,
    "opinion_reasoning": "<why this score>",
    "generic_flag": <true/false>,
    "generic_reasoning": "<why flagged or not>",
    "intent_type": "<visionary|technical_deep_dive|operator_diary|contrarian_take|postmortem|behind_the_scenes>",
    "intent_confidence": <0.0-1.0>,
    "overall_assessment": "<2-3 sentence summary>"
}}"""

            response = client.chat.completions.create(
                model="gpt-5.2",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=1000,
            )

            response_text = response.choices[0].message.content or ""

            # Parse JSON from response
            try:
                # Find JSON in response
                if '```json' in response_text:
                    json_start = response_text.find('```json') + 7
                    json_end = response_text.find('```', json_start)
                    response_text = response_text[json_start:json_end].strip()
                elif '```' in response_text:
                    json_start = response_text.find('```') + 3
                    json_end = response_text.find('```', json_start)
                    response_text = response_text[json_start:json_end].strip()

                return json.loads(response_text)

            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse GPT response as JSON: {e}")
                # Return default scores based on rule-based analysis
                return self._fallback_scores(rule_based)

        except Exception as e:
            logger.error(f"GPT analysis failed: {e}")
            return self._fallback_scores(rule_based)

    def _fallback_scores(self, rule_based: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback scores from rule-based analysis if GPT fails."""
        # Distinctiveness: penalize generic phrases
        distinctiveness = max(0, 70 - (rule_based['generic_count'] * 10))

        # Specificity: reward specific markers
        specificity = min(100, 30 + (rule_based['specific_markers'] * 5))

        # Opinion strength: penalize hedging
        opinion = max(0, 70 - (rule_based['hedging_count'] * 8))

        # Generic flag: if too many generic phrases
        generic_flag = rule_based['generic_count'] >= 3

        return {
            'distinctiveness_score': distinctiveness,
            'distinctiveness_reasoning': f"Rule-based: {rule_based['generic_count']} generic phrases found",
            'specificity_score': specificity,
            'specificity_reasoning': f"Rule-based: {rule_based['specific_markers']} specific markers found",
            'opinion_strength_score': opinion,
            'opinion_reasoning': f"Rule-based: {rule_based['hedging_count']} hedging phrases found",
            'generic_flag': generic_flag,
            'generic_reasoning': f"Rule-based: {'Too many' if generic_flag else 'Acceptable'} generic phrases",
            'intent_type': rule_based['detected_intent'],
            'intent_confidence': rule_based['intent_confidence'],
            'overall_assessment': "Fallback scoring used due to GPT analysis failure.",
        }

    def _combine_analyses(
        self,
        rule_based: Dict[str, Any],
        gpt_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Combine rule-based and GPT analyses into final scores."""
        # Use GPT scores as primary, rule-based as validation
        final = {
            'distinctiveness_score': gpt_analysis.get('distinctiveness_score', 50),
            'specificity_score': gpt_analysis.get('specificity_score', 50),
            'opinion_strength_score': gpt_analysis.get('opinion_strength_score', 50),
            'generic_flag': gpt_analysis.get('generic_flag', False),
            'intent_type': gpt_analysis.get('intent_type', rule_based['detected_intent']),
            'intent_confidence': gpt_analysis.get('intent_confidence', rule_based['intent_confidence']),
            'reasoning': gpt_analysis.get('overall_assessment', ''),
        }

        # Sanity check: if rule-based found many generic phrases but GPT didn't flag,
        # lower distinctiveness score
        if rule_based['generic_count'] >= 5 and final['distinctiveness_score'] > 60:
            final['distinctiveness_score'] = min(final['distinctiveness_score'], 50)
            final['reasoning'] += f" (Adjusted: {rule_based['generic_count']} generic phrases detected)"

        # Sanity check: if rule-based found many hedging phrases but GPT scored high opinion
        if rule_based['hedging_count'] >= 4 and final['opinion_strength_score'] > 60:
            final['opinion_strength_score'] = min(final['opinion_strength_score'], 50)
            final['reasoning'] += f" (Adjusted: {rule_based['hedging_count']} hedging phrases detected)"

        return final

    def score_episode(self, episode_id: str) -> AgentResult:
        """
        Convenience method to score a ChannelEpisode by ID.

        Args:
            episode_id: UUID of the ChannelEpisode

        Returns:
            AgentResult with scores, also updates the episode model
        """
        try:
            from core.models_autonomous_studio import ChannelEpisode

            episode = ChannelEpisode.objects.get(id=episode_id)

            # Get content to score
            content = episode.script or episode.description
            if not content:
                return AgentResult(
                    success=False,
                    message=f"Episode {episode_id} has no content to score",
                    error=f"Episode {episode_id} has no content to score",
                    agent_name=self.name
                )

            # Score it
            result = self.execute(
                task=f"Score voice quality for episode: {episode.title}",
                context={
                    'content': content,
                    'title': episode.title,
                    'content_type': 'blog_post',
                },
                scifi_context={},
                spider_context={}
            )

            if result.success:
                # Update episode with scores
                scores = result.data.get('voice_scores', {})
                episode.distinctiveness_score = scores.get('distinctiveness_score', 0)
                episode.specificity_score = scores.get('specificity_score', 0)
                episode.opinion_strength_score = scores.get('opinion_strength_score', 0)
                episode.generic_flag = scores.get('generic_flag', False)
                episode.intent_type = scores.get('intent_type', 'visionary')
                episode.voice_critique_completed = True
                episode.save(update_fields=[
                    'distinctiveness_score', 'specificity_score',
                    'opinion_strength_score', 'generic_flag',
                    'intent_type', 'voice_critique_completed'
                ])
                logger.info(f"Updated episode {episode_id} with voice scores")

            return result

        except Exception as e:
            logger.error(f"Failed to score episode {episode_id}: {e}")
            return AgentResult(
                success=False,
                error=str(e),
                agent_name=self.name
            )


# Factory function
def get_voice_critic_agent(user=None) -> VoiceCriticAgent:
    """Create a VoiceCriticAgent instance."""
    return VoiceCriticAgent(user=user)
