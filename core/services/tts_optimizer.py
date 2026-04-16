"""
TTS Text Optimizer Service

Optimizes text for text-to-speech output:
1. Smart summarization for long text (GPT-powered)
2. Chunking for very long text (sequential playback)
3. Clean text formatting (remove markdown, normalize)

Session 483: Full TTS solution
"""

import re
import logging
from typing import List, Optional
from dataclasses import dataclass
from enum import Enum
from core.services.openai_client_factory import get_openai_client  # Session 1084 round 51

logger = logging.getLogger(__name__)


class TTSStrategy(Enum):
    """Strategy for handling text length."""
    DIRECT = "direct"           # Text is short enough, use as-is
    SUMMARIZE = "summarize"     # Text needs summarization
    CHUNK = "chunk"             # Text needs chunking for sequential playback


@dataclass
class TTSOptimizedText:
    """Result of TTS optimization."""
    strategy: TTSStrategy
    text: str                           # Primary text (or summary)
    chunks: Optional[List[str]] = None  # For chunked strategy
    original_length: int = 0
    optimized_length: int = 0
    was_summarized: bool = False


class TTSTextOptimizer:
    """
    Optimizes text for TTS output.

    Thresholds:
    - Under 2000 chars: Direct playback
    - 2000-5000 chars: Summarize to ~1500 chars
    - Over 5000 chars: Summarize + chunk if still long
    """

    # Character limits
    # Session 494: Raised DIRECT_LIMIT from 2000 to 4000 chars (~2-3 min speech)
    # This prevents aggressive summarization cutting off responses
    DIRECT_LIMIT = 4000          # Below this, use text directly
    SUMMARIZE_LIMIT = 8000       # Below this, summarize (raised from 5000)
    CHUNK_SIZE = 3000            # Target size for each chunk (raised from 1500)
    HARD_LIMIT = 15000           # Absolute max before chunking

    def __init__(self, skip_summarize: bool = False):
        self.openai_client = None
        self.skip_summarize = skip_summarize  # If True, chunk instead of summarize

    def _get_openai_client(self):
        """Lazy load OpenAI client."""
        if self.openai_client is None:
            from django.conf import settings
            api_key = settings.EXTERNAL_API_KEYS.get('OPENAI_API_KEY', '')
            self.openai_client = get_openai_client(api_key=api_key)
        return self.openai_client

    def clean_for_tts(self, text: str) -> str:
        """
        Clean text for TTS - remove markdown, normalize whitespace.
        """
        if not text:
            return ""

        # Remove markdown headers (## Header -> Header)
        text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)

        # Remove bold/italic markers
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # **bold**
        text = re.sub(r'\*([^*]+)\*', r'\1', text)      # *italic*
        text = re.sub(r'__([^_]+)__', r'\1', text)      # __bold__
        text = re.sub(r'_([^_]+)_', r'\1', text)        # _italic_

        # Remove inline code
        text = re.sub(r'`([^`]+)`', r'\1', text)

        # Remove links but keep text: [text](url) -> text
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)

        # Remove bullet points and list markers
        text = re.sub(r'^[\s]*[-*+]\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'^[\s]*\d+\.\s+', '', text, flags=re.MULTILINE)

        # Remove horizontal rules
        text = re.sub(r'^-{3,}$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\*{3,}$', '', text, flags=re.MULTILINE)

        # Normalize whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)  # Max 2 newlines
        text = re.sub(r'[ \t]+', ' ', text)      # Normalize spaces

        # Clean up any remaining artifacts
        text = text.strip()

        return text

    def _find_natural_break(self, text: str, target_pos: int, search_range: int = 200) -> int:
        """
        Find a natural breaking point (sentence end, paragraph) near target position.
        """
        # Search for break points around target
        start = max(0, target_pos - search_range)
        end = min(len(text), target_pos + search_range)

        search_text = text[start:end]

        # Priority: paragraph break > sentence end > comma > space
        # Look for paragraph break
        para_match = re.search(r'\n\n', search_text)
        if para_match:
            return start + para_match.end()

        # Look for sentence end (. ! ?)
        sentence_match = re.search(r'[.!?]\s', search_text)
        if sentence_match:
            return start + sentence_match.end()

        # Look for comma
        comma_match = re.search(r',\s', search_text)
        if comma_match:
            return start + comma_match.end()

        # Fall back to space
        space_match = re.search(r'\s', search_text[target_pos - start:])
        if space_match:
            return target_pos + space_match.start()

        return target_pos

    def chunk_text(self, text: str, chunk_size: int = None) -> List[str]:
        """
        Split text into chunks at natural break points.
        """
        if chunk_size is None:
            chunk_size = self.CHUNK_SIZE

        if len(text) <= chunk_size:
            return [text]

        chunks = []
        remaining = text

        while remaining:
            if len(remaining) <= chunk_size:
                chunks.append(remaining.strip())
                break

            # Find natural break point
            break_pos = self._find_natural_break(remaining, chunk_size)

            chunk = remaining[:break_pos].strip()
            if chunk:
                chunks.append(chunk)

            remaining = remaining[break_pos:].strip()

        return chunks

    def summarize_for_tts(self, text: str, target_length: int = 1500) -> str:
        """
        Use GPT to create a TTS-optimized summary.
        Focuses on key points, natural speech flow.
        """
        try:
            client = self._get_openai_client()

            # Session 494: Use gpt-5-mini (reasoning model)
            # - Uses max_completion_tokens instead of max_tokens
            # - No temperature parameter (reasoning models don't support it)
            response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are a TTS optimization assistant. Your job is to create a
spoken summary of the following text that:

1. Captures ALL key points and main ideas
2. Uses natural, conversational language suitable for speech
3. Avoids bullet points, lists, or formatting - use flowing prose
4. Is approximately {target_length} characters (can be slightly over)
5. Maintains the original tone and meaning
6. Uses transition words for smooth flow ("First," "Additionally," "Finally,")

Do NOT start with "Here's a summary" or similar meta-commentary.
Just deliver the content directly as if speaking to someone."""
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                max_completion_tokens=4000  # Higher for reasoning model
            )

            summary = response.choices[0].message.content.strip()
            logger.info(f"TTS summarized {len(text)} -> {len(summary)} chars")
            return summary

        except Exception as e:
            logger.error(f"TTS summarization failed: {e}")
            # Fall back to smart truncation at a natural break point
            # Find a sentence end near target_length
            truncated = text[:target_length]
            # Look for last sentence ending
            last_period = truncated.rfind('. ')
            last_question = truncated.rfind('? ')
            last_exclaim = truncated.rfind('! ')
            best_break = max(last_period, last_question, last_exclaim)

            if best_break > target_length // 2:
                # Found a good break point in the second half
                return truncated[:best_break + 1]
            else:
                # No good break, just use the truncated text
                return truncated.rstrip() + "..."

    def optimize(self, text: str) -> TTSOptimizedText:
        """
        Main optimization method. Determines strategy and processes text.

        Returns TTSOptimizedText with strategy, optimized text, and optional chunks.
        """
        if not text:
            return TTSOptimizedText(
                strategy=TTSStrategy.DIRECT,
                text="",
                original_length=0,
                optimized_length=0
            )

        # Clean the text first
        cleaned = self.clean_for_tts(text)
        original_length = len(cleaned)

        # Strategy 1: Direct - text is short enough
        if original_length <= self.DIRECT_LIMIT:
            logger.info(f"TTS: Direct strategy ({original_length} chars)")
            return TTSOptimizedText(
                strategy=TTSStrategy.DIRECT,
                text=cleaned,
                original_length=original_length,
                optimized_length=original_length,
                was_summarized=False
            )

        # Session 494: If skip_summarize is True, go straight to chunking
        # This preserves the full response without GPT summarization
        if self.skip_summarize:
            logger.info(f"TTS: Chunk strategy (skip_summarize=True, {original_length} chars)")
            chunks = self.chunk_text(cleaned)
            return TTSOptimizedText(
                strategy=TTSStrategy.CHUNK,
                text=chunks[0] if chunks else cleaned,
                chunks=chunks,
                original_length=original_length,
                optimized_length=sum(len(c) for c in chunks),
                was_summarized=False
            )

        # Strategy 2: Summarize - text is medium length
        if original_length <= self.SUMMARIZE_LIMIT:
            logger.info(f"TTS: Summarize strategy ({original_length} chars)")
            summary = self.summarize_for_tts(cleaned, target_length=3000)
            return TTSOptimizedText(
                strategy=TTSStrategy.SUMMARIZE,
                text=summary,
                original_length=original_length,
                optimized_length=len(summary),
                was_summarized=True
            )

        # Strategy 3: Chunk - text is very long, summarize first then chunk
        logger.info(f"TTS: Chunk strategy ({original_length} chars)")

        # First summarize to reduce size
        summary = self.summarize_for_tts(cleaned, target_length=5000)

        # Then chunk if still long
        if len(summary) > self.DIRECT_LIMIT:
            chunks = self.chunk_text(summary)
            return TTSOptimizedText(
                strategy=TTSStrategy.CHUNK,
                text=chunks[0] if chunks else summary,
                chunks=chunks,
                original_length=original_length,
                optimized_length=sum(len(c) for c in chunks),
                was_summarized=True
            )

        return TTSOptimizedText(
            strategy=TTSStrategy.SUMMARIZE,
            text=summary,
            original_length=original_length,
            optimized_length=len(summary),
            was_summarized=True
        )

    def optimize_with_intro(self, text: str, add_summary_notice: bool = True) -> TTSOptimizedText:
        """
        Optimize with optional intro noting summarization.
        """
        result = self.optimize(text)

        if result.was_summarized and add_summary_notice:
            intro = "Here's a quick summary. "
            result.text = intro + result.text
            result.optimized_length = len(result.text)

            if result.chunks:
                result.chunks[0] = intro + result.chunks[0]

        return result


# Singleton instances
_optimizer_instance = None
_optimizer_no_summarize = None


def get_tts_optimizer(skip_summarize: bool = False) -> TTSTextOptimizer:
    """
    Get TTS optimizer instance.

    Args:
        skip_summarize: If True, returns optimizer that chunks without summarizing.
                       Use this when user wants to hear full response.
    """
    global _optimizer_instance, _optimizer_no_summarize

    if skip_summarize:
        if _optimizer_no_summarize is None:
            _optimizer_no_summarize = TTSTextOptimizer(skip_summarize=True)
        return _optimizer_no_summarize
    else:
        if _optimizer_instance is None:
            _optimizer_instance = TTSTextOptimizer(skip_summarize=False)
        return _optimizer_instance
