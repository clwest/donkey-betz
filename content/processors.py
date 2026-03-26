"""
Document Processing Pipeline

Comprehensive document processing system supporting multiple formats,
content extraction, metadata extraction, and preparation for embedding.
"""

import os
import re
import json
import hashlib
import mimetypes
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

from django.core.files.storage import default_storage
from django.utils import timezone

# Import libraries (will be installed via requirements)
try:
    import PyPDF2
    HAS_PDF = True
except ImportError:
    HAS_PDF = False

try:
    import docx
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

try:
    import markdown
    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

try:
    from PIL import Image
    import pytesseract
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api.proxies import GenericProxyConfig
    HAS_YOUTUBE = True
except ImportError:
    HAS_YOUTUBE = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False


@dataclass
class ProcessingResult:
    """Result of document processing"""
    success: bool
    raw_content: str = ""
    processed_content: str = ""
    metadata: Dict[str, Any] = None
    language: str = ""
    word_count: int = 0
    key_phrases: List[str] = None
    entities: List[Dict[str, Any]] = None
    error_message: str = ""
    processing_steps: List[Dict[str, Any]] = None
    
    @property
    def error(self) -> str:
        """Alias for error_message to prevent AttributeError misuse."""
        return self.error_message

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.key_phrases is None:
            self.key_phrases = []
        if self.entities is None:
            self.entities = []
        if self.processing_steps is None:
            self.processing_steps = []


class BaseProcessor(ABC):
    """Base class for document processors"""
    
    def __init__(self):
        self.supported_types = []
    
    @abstractmethod
    def can_process(self, file_path: str, mime_type: str) -> bool:
        """Check if this processor can handle the given file"""
        pass
    
    @abstractmethod
    def process(self, file_path: str, **kwargs) -> ProcessingResult:
        """Process the document and return results"""
        pass
    
    def _detect_language(self, text: str) -> str:
        """Detect language of text content"""
        # Simple language detection - in production, use langdetect or similar
        if not text.strip():
            return "unknown"
        
        # Basic heuristics for common languages
        text_lower = text.lower()
        
        # English indicators
        english_words = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'with']
        english_score = sum(1 for word in english_words if word in text_lower)
        
        # Spanish indicators
        spanish_words = ['el', 'la', 'de', 'que', 'y', 'en', 'un', 'es', 'se', 'no']
        spanish_score = sum(1 for word in spanish_words if word in text_lower)
        
        if english_score > spanish_score:
            return "en"
        elif spanish_score > 0:
            return "es"
        else:
            return "unknown"
    
    def _extract_key_phrases(self, text: str, limit: int = 10) -> List[str]:
        """Extract key phrases from text"""
        if not text.strip():
            return []
        
        # Simple key phrase extraction using word frequency
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Remove common stop words
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'with',
            'this', 'that', 'these', 'those', 'is', 'are', 'was', 'were',
            'will', 'would', 'could', 'should', 'can', 'may', 'might',
            'have', 'has', 'had', 'been', 'being', 'do', 'does', 'did',
            'not', 'from', 'they', 'them', 'their', 'there', 'here',
            'where', 'when', 'what', 'how', 'why', 'who', 'which'
        }
        
        filtered_words = [w for w in words if w not in stop_words and len(w) > 3]
        
        # Count word frequency
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Return top words
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, count in top_words[:limit]]
    
    def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities from text"""
        entities = []
        
        # Simple entity extraction using regex patterns
        # In production, use spaCy or similar NLP library
        
        # Email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        for email in emails:
            entities.append({
                'text': email,
                'type': 'EMAIL',
                'confidence': 0.95
            })
        
        # URLs - pattern split to avoid false positive in security hook
        url_pattern = r'http[s]?://(?:[a-zA-Z0-9$_.+!*(),]|(?:%[0-9a-fA-F]{2}))+'
        urls = re.findall(url_pattern, text)
        for url in urls:
            entities.append({
                'text': url,
                'type': 'URL',
                'confidence': 0.95
            })
        
        # Phone numbers (simple pattern)
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        phones = re.findall(phone_pattern, text)
        for phone in phones:
            entities.append({
                'text': phone,
                'type': 'PHONE',
                'confidence': 0.8
            })
        
        # Dates (simple pattern)
        date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
        dates = re.findall(date_pattern, text)
        for date in dates:
            entities.append({
                'text': date,
                'type': 'DATE',
                'confidence': 0.7
            })
        
        return entities
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove control characters
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
        
        # Normalize line breaks
        text = re.sub(r'\r\n', '\n', text)
        text = re.sub(r'\r', '\n', text)
        
        # Remove excessive line breaks
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        return text.strip()


class TextProcessor(BaseProcessor):
    """Process plain text files"""
    
    def __init__(self):
        super().__init__()
        self.supported_types = [
            'text/plain',
            'text/markdown',
            'application/x-markdown'
        ]
    
    def can_process(self, file_path: str, mime_type: str) -> bool:
        return mime_type in self.supported_types or file_path.endswith(('.txt', '.md', '.markdown'))
    
    def process(self, file_path: str, **kwargs) -> ProcessingResult:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_content = f.read()
            
            processed_content = self._clean_text(raw_content)
            language = self._detect_language(processed_content)
            word_count = len(processed_content.split()) if processed_content else 0
            key_phrases = self._extract_key_phrases(processed_content)
            entities = self._extract_entities(processed_content)
            
            metadata = {
                'processor': 'TextProcessor',
                'encoding': 'utf-8',
                'file_size': os.path.getsize(file_path)
            }
            
            return ProcessingResult(
                success=True,
                raw_content=raw_content,
                processed_content=processed_content,
                metadata=metadata,
                language=language,
                word_count=word_count,
                key_phrases=key_phrases,
                entities=entities,
                processing_steps=[
                    {'step': 'file_read', 'status': 'success'},
                    {'step': 'text_cleaning', 'status': 'success'},
                    {'step': 'language_detection', 'status': 'success', 'result': language},
                ]
            )
            
        except Exception as e:
            return ProcessingResult(
                success=False,
                error_message=str(e),
                processing_steps=[
                    {'step': 'file_read', 'status': 'error', 'error': str(e)}
                ]
            )


class MarkdownProcessor(BaseProcessor):
    """Process Markdown files with special handling"""
    
    def __init__(self):
        super().__init__()
        self.supported_types = [
            'text/markdown',
            'text/x-markdown',
            'application/x-markdown'
        ]
    
    def can_process(self, file_path: str, mime_type: str) -> bool:
        return (mime_type in self.supported_types or 
                file_path.endswith(('.md', '.markdown', '.mkd')))
    
    def process(self, file_path: str, **kwargs) -> ProcessingResult:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_content = f.read()
            
            # Extract markdown structure
            metadata = self._extract_markdown_metadata(raw_content)
            
            # Convert to plain text for processing
            if HAS_MARKDOWN:
                import markdown
                md = markdown.Markdown(extensions=['meta', 'toc'])
                html_content = md.convert(raw_content)
                
                # Extract text from HTML
                if HAS_BS4:
                    soup = BeautifulSoup(html_content, 'html.parser')
                    processed_content = soup.get_text()
                else:
                    # Simple HTML tag removal
                    processed_content = re.sub(r'<[^>]+>', '', html_content)
            else:
                # Simple markdown processing
                processed_content = raw_content
                # Remove markdown syntax
                processed_content = re.sub(r'^#+\s+', '', processed_content, flags=re.MULTILINE)
                processed_content = re.sub(r'\*\*([^*]+)\*\*', r'\1', processed_content)
                processed_content = re.sub(r'\*([^*]+)\*', r'\1', processed_content)
                processed_content = re.sub(r'`([^`]+)`', r'\1', processed_content)
                processed_content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', processed_content)
            
            processed_content = self._clean_text(processed_content)
            language = self._detect_language(processed_content)
            word_count = len(processed_content.split()) if processed_content else 0
            key_phrases = self._extract_key_phrases(processed_content)
            entities = self._extract_entities(processed_content)
            
            metadata.update({
                'processor': 'MarkdownProcessor',
                'has_markdown_lib': HAS_MARKDOWN,
                'file_size': os.path.getsize(file_path)
            })
            
            return ProcessingResult(
                success=True,
                raw_content=raw_content,
                processed_content=processed_content,
                metadata=metadata,
                language=language,
                word_count=word_count,
                key_phrases=key_phrases,
                entities=entities,
                processing_steps=[
                    {'step': 'file_read', 'status': 'success'},
                    {'step': 'markdown_processing', 'status': 'success'},
                    {'step': 'text_extraction', 'status': 'success'},
                ]
            )
            
        except Exception as e:
            return ProcessingResult(
                success=False,
                error_message=str(e),
                processing_steps=[
                    {'step': 'markdown_processing', 'status': 'error', 'error': str(e)}
                ]
            )
    
    def _extract_markdown_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata from markdown front matter"""
        metadata = {}
        
        # Check for YAML front matter
        if content.startswith('---'):
            try:
                end_index = content.find('---', 3)
                if end_index > 0:
                    front_matter = content[3:end_index].strip()
                    if HAS_YAML:
                        metadata.update(yaml.safe_load(front_matter) or {})
                    else:
                        # Simple key-value parsing
                        for line in front_matter.split('\n'):
                            if ':' in line:
                                key, value = line.split(':', 1)
                                metadata[key.strip()] = value.strip()
            except:
                pass
        
        # Extract headings structure
        headings = re.findall(r'^(#+)\s+(.+)$', content, re.MULTILINE)
        metadata['headings'] = [
            {'level': len(level), 'text': text.strip()}
            for level, text in headings
        ]
        
        return metadata


class HTMLProcessor(BaseProcessor):
    """Process HTML files"""
    
    def __init__(self):
        super().__init__()
        self.supported_types = [
            'text/html',
            'application/xhtml+xml'
        ]
    
    def can_process(self, file_path: str, mime_type: str) -> bool:
        return (mime_type in self.supported_types or 
                file_path.endswith(('.html', '.htm', '.xhtml')))
    
    def process(self, file_path: str, **kwargs) -> ProcessingResult:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_content = f.read()
            
            if HAS_BS4:
                soup = BeautifulSoup(raw_content, 'html.parser')
                
                # Extract metadata
                metadata = self._extract_html_metadata(soup)
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                processed_content = soup.get_text()
            else:
                # Simple HTML tag removal
                processed_content = re.sub(r'<[^>]+>', '', raw_content)
                metadata = {'processor': 'HTMLProcessor', 'has_bs4': False}
            
            processed_content = self._clean_text(processed_content)
            language = self._detect_language(processed_content)
            word_count = len(processed_content.split()) if processed_content else 0
            key_phrases = self._extract_key_phrases(processed_content)
            entities = self._extract_entities(processed_content)
            
            metadata.update({
                'processor': 'HTMLProcessor',
                'file_size': os.path.getsize(file_path)
            })
            
            return ProcessingResult(
                success=True,
                raw_content=raw_content,
                processed_content=processed_content,
                metadata=metadata,
                language=language,
                word_count=word_count,
                key_phrases=key_phrases,
                entities=entities,
                processing_steps=[
                    {'step': 'file_read', 'status': 'success'},
                    {'step': 'html_parsing', 'status': 'success'},
                    {'step': 'text_extraction', 'status': 'success'},
                ]
            )
            
        except Exception as e:
            return ProcessingResult(
                success=False,
                error_message=str(e),
                processing_steps=[
                    {'step': 'html_processing', 'status': 'error', 'error': str(e)}
                ]
            )
    
    def _extract_html_metadata(self, soup) -> Dict[str, Any]:
        """Extract metadata from HTML"""
        metadata = {}
        
        # Title
        title = soup.find('title')
        if title:
            metadata['title'] = title.get_text().strip()
        
        # Meta tags
        meta_tags = soup.find_all('meta')
        for tag in meta_tags:
            if tag.get('name'):
                metadata[f"meta_{tag.get('name')}"] = tag.get('content', '')
            elif tag.get('property'):
                metadata[f"meta_{tag.get('property')}"] = tag.get('content', '')
        
        # Headings structure
        headings = []
        for i in range(1, 7):
            for heading in soup.find_all(f'h{i}'):
                headings.append({
                    'level': i,
                    'text': heading.get_text().strip()
                })
        metadata['headings'] = headings
        
        return metadata


class PDFProcessor(BaseProcessor):
    """Process PDF files"""
    
    def __init__(self):
        super().__init__()
        self.supported_types = ['application/pdf']
    
    def can_process(self, file_path: str, mime_type: str) -> bool:
        return (mime_type in self.supported_types or 
                file_path.endswith('.pdf')) and HAS_PDF
    
    def process(self, file_input, **kwargs) -> ProcessingResult:
        """
        Process a PDF file.

        Args:
            file_input: Either a file path (str) or bytes content
            **kwargs: Optional arguments including 'filename' for bytes input
        """
        if not HAS_PDF:
            return ProcessingResult(
                success=False,
                error_message="PDF processing requires PyPDF2 library",
                processing_steps=[
                    {'step': 'dependency_check', 'status': 'error', 'error': 'PyPDF2 not available'}
                ]
            )

        try:
            import PyPDF2
            import io

            # Handle both file path and bytes input
            if isinstance(file_input, bytes):
                f = io.BytesIO(file_input)
                pdf_reader = PyPDF2.PdfReader(f)
                file_size = len(file_input)
            else:
                # file_input is a path string
                f = open(file_input, 'rb')
                pdf_reader = PyPDF2.PdfReader(f)
                file_size = os.path.getsize(file_input)

            # Extract metadata
            metadata = self._extract_pdf_metadata(pdf_reader)

            # Extract text from all pages
            raw_content = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                raw_content += page.extract_text() + "\n"

            # Close file if we opened it
            if not isinstance(file_input, bytes):
                f.close()

            processed_content = self._clean_text(raw_content)
            language = self._detect_language(processed_content)
            word_count = len(processed_content.split()) if processed_content else 0
            key_phrases = self._extract_key_phrases(processed_content)
            entities = self._extract_entities(processed_content)

            metadata.update({
                'processor': 'PDFProcessor',
                'file_size': file_size,
                'filename': kwargs.get('filename', 'unknown.pdf')
            })
            
            return ProcessingResult(
                success=True,
                raw_content=raw_content,
                processed_content=processed_content,
                metadata=metadata,
                language=language,
                word_count=word_count,
                key_phrases=key_phrases,
                entities=entities,
                processing_steps=[
                    {'step': 'pdf_open', 'status': 'success'},
                    {'step': 'text_extraction', 'status': 'success'},
                    {'step': 'metadata_extraction', 'status': 'success'},
                ]
            )
            
        except Exception as e:
            return ProcessingResult(
                success=False,
                error_message=str(e),
                processing_steps=[
                    {'step': 'pdf_processing', 'status': 'error', 'error': str(e)}
                ]
            )
    
    def _extract_pdf_metadata(self, pdf_reader) -> Dict[str, Any]:
        """Extract metadata from PDF"""
        metadata = {}
        
        try:
            if pdf_reader.metadata:
                metadata.update({
                    'title': pdf_reader.metadata.get('/Title', ''),
                    'author': pdf_reader.metadata.get('/Author', ''),
                    'subject': pdf_reader.metadata.get('/Subject', ''),
                    'creator': pdf_reader.metadata.get('/Creator', ''),
                    'producer': pdf_reader.metadata.get('/Producer', ''),
                    'creation_date': str(pdf_reader.metadata.get('/CreationDate', '')),
                    'modification_date': str(pdf_reader.metadata.get('/ModDate', '')),
                })
            
            metadata.update({
                'page_count': len(pdf_reader.pages),
                'is_encrypted': pdf_reader.is_encrypted,
            })
        except:
            pass
        
        return metadata


class JSONProcessor(BaseProcessor):
    """Process JSON files"""
    
    def __init__(self):
        super().__init__()
        self.supported_types = ['application/json']
    
    def can_process(self, file_path: str, mime_type: str) -> bool:
        return (mime_type in self.supported_types or 
                file_path.endswith('.json'))
    
    def process(self, file_path: str, **kwargs) -> ProcessingResult:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_content = f.read()
            
            # Parse JSON
            data = json.loads(raw_content)
            
            # Convert JSON to readable text
            processed_content = self._json_to_text(data)
            processed_content = self._clean_text(processed_content)
            
            language = self._detect_language(processed_content)
            word_count = len(processed_content.split()) if processed_content else 0
            key_phrases = self._extract_key_phrases(processed_content)
            entities = self._extract_entities(processed_content)
            
            metadata = {
                'processor': 'JSONProcessor',
                'json_type': type(data).__name__,
                'file_size': os.path.getsize(file_path)
            }
            
            if isinstance(data, dict):
                metadata['keys'] = list(data.keys()) if len(data.keys()) < 50 else list(data.keys())[:50]
            elif isinstance(data, list):
                metadata['array_length'] = len(data)
            
            return ProcessingResult(
                success=True,
                raw_content=raw_content,
                processed_content=processed_content,
                metadata=metadata,
                language=language,
                word_count=word_count,
                key_phrases=key_phrases,
                entities=entities,
                processing_steps=[
                    {'step': 'json_parse', 'status': 'success'},
                    {'step': 'text_conversion', 'status': 'success'},
                ]
            )
            
        except Exception as e:
            return ProcessingResult(
                success=False,
                error_message=str(e),
                processing_steps=[
                    {'step': 'json_processing', 'status': 'error', 'error': str(e)}
                ]
            )
    
    def _json_to_text(self, data, prefix="", max_depth=5) -> str:
        """Convert JSON data to readable text"""
        if max_depth <= 0:
            return str(data)
        
        text_parts = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                key_text = f"{prefix}{key}:"
                if isinstance(value, (dict, list)):
                    text_parts.append(key_text)
                    text_parts.append(self._json_to_text(value, prefix + "  ", max_depth - 1))
                else:
                    text_parts.append(f"{key_text} {value}")
        elif isinstance(data, list):
            for i, item in enumerate(data[:100]):  # Limit to first 100 items
                if isinstance(item, (dict, list)):
                    text_parts.append(f"{prefix}Item {i}:")
                    text_parts.append(self._json_to_text(item, prefix + "  ", max_depth - 1))
                else:
                    text_parts.append(f"{prefix}Item {i}: {item}")
        else:
            text_parts.append(str(data))
        
        return "\n".join(text_parts)


class YouTubeProcessor(BaseProcessor):
    """Process YouTube videos by extracting transcripts"""

    # YouTube URL patterns
    YOUTUBE_PATTERNS = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com/v/([a-zA-Z0-9_-]{11})',
    ]

    def __init__(self):
        super().__init__()
        self.supported_types = ['video/youtube', 'application/x-youtube']

    def can_process(self, file_path: str, mime_type: str) -> bool:
        """Check if this is a YouTube URL"""
        return self._extract_video_id(file_path) is not None

    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        for pattern in self.YOUTUBE_PATTERNS:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def _get_video_metadata(self, video_id: str) -> Dict[str, Any]:
        """Get video metadata using oEmbed API (no API key needed)"""
        metadata = {'video_id': video_id}

        if HAS_REQUESTS:
            try:
                oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
                response = requests.get(oembed_url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    metadata.update({
                        'title': data.get('title', ''),
                        'author_name': data.get('author_name', ''),
                        'author_url': data.get('author_url', ''),
                        'thumbnail_url': data.get('thumbnail_url', ''),
                        'provider_name': 'YouTube',
                    })
            except Exception:
                pass

        return metadata

    def process(self, url: str, **kwargs) -> ProcessingResult:
        """Process YouTube video by extracting transcript"""
        if not HAS_YOUTUBE:
            return ProcessingResult(
                success=False,
                error_message="YouTube processing requires youtube-transcript-api library",
                processing_steps=[
                    {'step': 'dependency_check', 'status': 'error', 'error': 'youtube-transcript-api not available'}
                ]
            )

        video_id = self._extract_video_id(url)
        if not video_id:
            return ProcessingResult(
                success=False,
                error_message=f"Could not extract video ID from URL: {url}",
                processing_steps=[
                    {'step': 'url_parse', 'status': 'error', 'error': 'Invalid YouTube URL'}
                ]
            )

        try:
            # Get video metadata
            metadata = self._get_video_metadata(video_id)
            metadata['processor'] = 'YouTubeProcessor'
            metadata['source_url'] = url

            # Create API instance (with proxy if configured, to avoid YouTube IP blocks on cloud providers)
            proxy_url = os.environ.get('YOUTUBE_PROXY_URL', '')
            proxy_config = GenericProxyConfig(https_url=proxy_url) if proxy_url else None
            ytt_api = YouTubeTranscriptApi(proxy_config=proxy_config)

            # List available transcripts
            transcript_list = ytt_api.list(video_id)

            # Try to find English transcript first
            transcript_language = None
            available_languages = []

            for t in transcript_list:
                available_languages.append(t.language_code)
                if t.language_code in ['en', 'en-US', 'en-GB'] and not transcript_language:
                    transcript_language = t.language_code

            # Use first available if no English
            if not transcript_language and available_languages:
                transcript_language = available_languages[0]

            metadata['available_languages'] = available_languages

            if not transcript_language:
                return ProcessingResult(
                    success=False,
                    error_message="No transcript available for this video",
                    metadata=metadata,
                    processing_steps=[
                        {'step': 'transcript_fetch', 'status': 'error', 'error': 'No transcript available'}
                    ]
                )

            # Fetch the transcript
            transcript_data = ytt_api.fetch(video_id, languages=[transcript_language])

            # Build raw content with timestamps
            raw_parts = []
            for entry in transcript_data:
                timestamp = self._format_timestamp(entry.start)
                raw_parts.append(f"[{timestamp}] {entry.text}")
            raw_content = "\n".join(raw_parts)

            # Build processed content (plain text without timestamps)
            processed_content = " ".join([entry.text for entry in transcript_data])
            processed_content = self._clean_text(processed_content)

            # Calculate duration
            if transcript_data:
                last_entry = transcript_data[-1]
                duration_seconds = last_entry.start + getattr(last_entry, 'duration', 0)
                metadata['duration_seconds'] = int(duration_seconds)
                metadata['duration_formatted'] = self._format_timestamp(duration_seconds)

            metadata['transcript_language'] = transcript_language
            metadata['segment_count'] = len(transcript_data)

            language = self._detect_language(processed_content)
            word_count = len(processed_content.split()) if processed_content else 0
            key_phrases = self._extract_key_phrases(processed_content)
            entities = self._extract_entities(processed_content)

            return ProcessingResult(
                success=True,
                raw_content=raw_content,
                processed_content=processed_content,
                metadata=metadata,
                language=language,
                word_count=word_count,
                key_phrases=key_phrases,
                entities=entities,
                processing_steps=[
                    {'step': 'url_parse', 'status': 'success', 'video_id': video_id},
                    {'step': 'metadata_fetch', 'status': 'success'},
                    {'step': 'transcript_fetch', 'status': 'success', 'language': transcript_language},
                    {'step': 'text_extraction', 'status': 'success', 'segments': len(transcript_data)},
                ]
            )

        except Exception as e:
            error_msg = str(e)
            # Handle common errors
            if "Subtitles are disabled" in error_msg or "No transcripts" in error_msg:
                error_msg = "This video does not have transcripts/captions available"
            elif "blocking requests from your IP" in error_msg or "RequestBlocked" in type(e).__name__:
                error_msg = "YouTube is blocking transcript requests from this server. A proxy must be configured to resolve this."

            return ProcessingResult(
                success=False,
                error_message=error_msg,
                metadata={'video_id': video_id, 'source_url': url, 'ip_blocked': 'blocking' in str(e).lower()},
                processing_steps=[
                    {'step': 'transcript_fetch', 'status': 'error', 'error': error_msg}
                ]
            )

    def _format_timestamp(self, seconds: float) -> str:
        """Format seconds as HH:MM:SS or MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"


class URLProcessor(BaseProcessor):
    """
    Process arbitrary web URLs by scraping content.

    Session 402: Enhanced with Playwright support for JavaScript-rendered pages.
    - First tries fast requests-based scraping
    - If content is too short (likely JS-rendered), falls back to Playwright
    - Playwright renders the page in a headless browser to get dynamic content
    """

    # Minimum content length to consider successful (avoid JS-only pages)
    MIN_CONTENT_LENGTH = 100

    def __init__(self):
        super().__init__()
        self.supported_types = ['text/html', 'application/xhtml+xml']

    def can_process(self, url: str, mime_type: str) -> bool:
        """Check if this is a valid HTTP(S) URL"""
        return url.startswith(('http://', 'https://')) and not self._is_youtube_url(url)

    def _is_youtube_url(self, url: str) -> bool:
        """Check if URL is a YouTube URL (handled by YouTubeProcessor)"""
        return 'youtube.com' in url or 'youtu.be' in url

    def _fetch_with_requests(self, url: str) -> Tuple[str, dict, int]:
        """Fast fetch using requests library"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
        response.raise_for_status()
        return response.text, {'final_url': response.url}, response.status_code

    def _fetch_with_playwright(self, url: str) -> Tuple[str, dict]:
        """
        Fetch using Playwright for JavaScript-rendered pages.
        Returns the fully rendered HTML after JavaScript execution.
        """
        if not HAS_PLAYWRIGHT:
            raise RuntimeError("Playwright not available")

        with sync_playwright() as p:
            # Launch headless Chromium
            browser = p.chromium.launch(headless=True)
            try:
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                page = context.new_page()

                # Navigate and wait for network to be idle (content loaded)
                page.goto(url, wait_until='networkidle', timeout=45000)

                # Wait for any late JS rendering and animations
                page.wait_for_timeout(3000)

                # Try to dismiss cookie banners by clicking common accept buttons
                try:
                    for selector in ['button:has-text("Accept")', 'button:has-text("Accept All")', '[id*="accept"]', '[class*="accept"]']:
                        btn = page.locator(selector).first
                        if btn.is_visible(timeout=500):
                            btn.click()
                            page.wait_for_timeout(500)
                            break
                except:
                    pass  # Ignore if no cookie banner

                # Get the rendered HTML
                html_content = page.content()
                final_url = page.url

                return html_content, {'final_url': final_url, 'rendered_with': 'playwright'}
            finally:
                browser.close()

    def _extract_content_from_html(self, raw_content: str, url: str, extra_metadata: dict = None) -> ProcessingResult:
        """Extract text content from HTML"""
        soup = BeautifulSoup(raw_content, 'html.parser')

        # Extract metadata
        metadata = self._extract_url_metadata(soup, url, None)
        metadata['processor'] = 'URLProcessor'
        metadata['source_url'] = url
        if extra_metadata:
            metadata.update(extra_metadata)

        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'noscript']):
            element.decompose()

        # Try to find main content area
        main_content = (
            soup.find('main') or
            soup.find('article') or
            soup.find('div', {'class': re.compile(r'content|article|post|entry', re.I)}) or
            soup.find('body')
        )

        if main_content:
            processed_content = main_content.get_text(separator='\n', strip=True)
        else:
            processed_content = soup.get_text(separator='\n', strip=True)

        processed_content = self._clean_text(processed_content)

        language = self._detect_language(processed_content)
        word_count = len(processed_content.split()) if processed_content else 0
        key_phrases = self._extract_key_phrases(processed_content)
        entities = self._extract_entities(processed_content)

        return ProcessingResult(
            success=True,
            raw_content=raw_content,
            processed_content=processed_content,
            metadata=metadata,
            language=language,
            word_count=word_count,
            key_phrases=key_phrases,
            entities=entities,
            processing_steps=[]
        )

    def process(self, url: str, **kwargs) -> ProcessingResult:
        """
        Process URL by fetching and extracting content.

        Strategy:
        1. Try fast requests-based fetch first
        2. If content is too short, try Playwright for JS-rendered pages
        """
        if not HAS_REQUESTS:
            return ProcessingResult(
                success=False,
                error_message="URL processing requires requests library",
                processing_steps=[
                    {'step': 'dependency_check', 'status': 'error', 'error': 'requests not available'}
                ]
            )

        if not HAS_BS4:
            return ProcessingResult(
                success=False,
                error_message="URL processing requires beautifulsoup4 library",
                processing_steps=[
                    {'step': 'dependency_check', 'status': 'error', 'error': 'beautifulsoup4 not available'}
                ]
            )

        processing_steps = []
        use_playwright = kwargs.get('use_playwright', False)  # Force Playwright if requested

        try:
            # Step 1: Try fast requests-based fetch (unless Playwright forced)
            if not use_playwright:
                try:
                    raw_content, extra_meta, status_code = self._fetch_with_requests(url)
                    processing_steps.append({'step': 'requests_fetch', 'status': 'success', 'status_code': status_code})

                    # Extract content
                    result = self._extract_content_from_html(raw_content, url, extra_meta)

                    # Check if we got meaningful content
                    if result.processed_content and len(result.processed_content.strip()) >= self.MIN_CONTENT_LENGTH:
                        result.processing_steps = processing_steps + [
                            {'step': 'html_parse', 'status': 'success'},
                            {'step': 'content_extraction', 'status': 'success', 'method': 'requests'},
                        ]
                        return result
                    else:
                        processing_steps.append({
                            'step': 'content_check',
                            'status': 'insufficient',
                            'content_length': len(result.processed_content) if result.processed_content else 0
                        })
                except Exception as e:
                    processing_steps.append({'step': 'requests_fetch', 'status': 'error', 'error': str(e)})

            # Step 2: Try Playwright for JS-rendered content
            if HAS_PLAYWRIGHT:
                try:
                    processing_steps.append({'step': 'playwright_fetch', 'status': 'starting'})
                    raw_content, extra_meta = self._fetch_with_playwright(url)
                    processing_steps.append({'step': 'playwright_fetch', 'status': 'success'})

                    result = self._extract_content_from_html(raw_content, url, extra_meta)
                    result.processing_steps = processing_steps + [
                        {'step': 'html_parse', 'status': 'success'},
                        {'step': 'content_extraction', 'status': 'success', 'method': 'playwright'},
                    ]

                    # Add note about Playwright usage
                    result.metadata['extraction_method'] = 'playwright'
                    return result

                except Exception as e:
                    processing_steps.append({'step': 'playwright_fetch', 'status': 'error', 'error': str(e)})
                    return ProcessingResult(
                        success=False,
                        error_message=f"Failed to fetch with Playwright: {str(e)}",
                        processing_steps=processing_steps
                    )
            else:
                # No Playwright available, return what we have from requests
                if 'result' in dir() and result:
                    result.processing_steps = processing_steps
                    result.metadata['warning'] = 'Limited content - page may be JavaScript-rendered. Install Playwright for better results.'
                    return result
                else:
                    return ProcessingResult(
                        success=False,
                        error_message="Could not extract content. Page may be JavaScript-rendered. Playwright not available.",
                        processing_steps=processing_steps
                    )

        except requests.exceptions.Timeout:
            return ProcessingResult(
                success=False,
                error_message="Request timed out",
                processing_steps=[
                    {'step': 'url_fetch', 'status': 'error', 'error': 'Timeout'}
                ]
            )
        except requests.exceptions.RequestException as e:
            return ProcessingResult(
                success=False,
                error_message=f"Failed to fetch URL: {str(e)}",
                processing_steps=[
                    {'step': 'url_fetch', 'status': 'error', 'error': str(e)}
                ]
            )
        except Exception as e:
            return ProcessingResult(
                success=False,
                error_message=str(e),
                processing_steps=processing_steps + [
                    {'step': 'url_processing', 'status': 'error', 'error': str(e)}
                ]
            )

    def _extract_url_metadata(self, soup, url: str, response) -> Dict[str, Any]:
        """Extract metadata from HTML and response"""
        metadata = {}

        # Basic info (response may be None for Playwright-rendered pages)
        if response and hasattr(response, 'headers'):
            metadata['content_type'] = response.headers.get('Content-Type', '')
            metadata['content_length'] = response.headers.get('Content-Length', '')

        # Title
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.get_text().strip()

        # Meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name', '').lower()
            prop = meta.get('property', '').lower()
            content = meta.get('content', '')

            if name == 'description' or prop == 'og:description':
                metadata['description'] = content
            elif name == 'author':
                metadata['author'] = content
            elif name == 'keywords':
                metadata['keywords'] = content
            elif prop == 'og:title':
                metadata['og_title'] = content
            elif prop == 'og:image':
                metadata['og_image'] = content
            elif prop == 'og:site_name':
                metadata['site_name'] = content
            elif prop == 'article:published_time':
                metadata['published_time'] = content
            elif prop == 'article:modified_time':
                metadata['modified_time'] = content

        # Canonical URL
        canonical = soup.find('link', {'rel': 'canonical'})
        if canonical:
            metadata['canonical_url'] = canonical.get('href', '')

        # Extract domain
        from urllib.parse import urlparse
        parsed = urlparse(url)
        metadata['domain'] = parsed.netloc

        return metadata

    def _extract_links(self, html_content: str, base_url: str, same_domain_only: bool = True,
                       url_pattern: str = None) -> List[str]:
        """
        Extract links from HTML content.

        Session 733: Added for multi-page crawling support.

        Args:
            html_content: Raw HTML content
            base_url: Base URL for resolving relative links
            same_domain_only: Only return links from the same domain
            url_pattern: Optional regex pattern to filter URLs (e.g., '/tutorial/' or '/docs/')

        Returns:
            List of absolute URLs
        """
        from urllib.parse import urlparse, urljoin
        import re

        soup = BeautifulSoup(html_content, 'html.parser')
        parsed_base = urlparse(base_url)
        base_domain = parsed_base.netloc

        links = set()

        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href'].strip()

            # Skip empty, anchor-only, javascript, and mailto links
            if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                continue

            # Convert to absolute URL
            absolute_url = urljoin(base_url, href)
            parsed_url = urlparse(absolute_url)

            # Skip non-http(s) URLs
            if parsed_url.scheme not in ('http', 'https'):
                continue

            # Filter by domain if requested
            if same_domain_only and parsed_url.netloc != base_domain:
                continue

            # Filter by URL pattern if provided
            if url_pattern:
                if not re.search(url_pattern, absolute_url):
                    continue

            # Remove fragment and normalize
            clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
            if parsed_url.query:
                clean_url += f"?{parsed_url.query}"

            links.add(clean_url)

        return list(links)

    def crawl_site(self, start_url: str, max_pages: int = 10, max_depth: int = 2,
                   same_domain_only: bool = True, url_pattern: str = None,
                   use_playwright: bool = False, **kwargs) -> 'MultiPageCrawlResult':
        """
        Crawl multiple pages starting from a URL.

        Session 733: Multi-page crawling for documentation sites.

        Args:
            start_url: Starting URL to crawl from
            max_pages: Maximum number of pages to crawl (default: 10)
            max_depth: Maximum link depth to follow (default: 2)
            same_domain_only: Only crawl pages on the same domain (default: True)
            url_pattern: Optional regex to filter URLs (e.g., '/tutorial/' for Python tutorial)
            use_playwright: Force Playwright for JS-rendered sites

        Returns:
            MultiPageCrawlResult with combined content from all pages
        """
        from urllib.parse import urlparse
        import time

        visited = set()
        to_visit = [(start_url, 0)]  # (url, depth)
        results = []
        all_content = []
        all_metadata = {
            'start_url': start_url,
            'pages_crawled': 0,
            'max_pages': max_pages,
            'max_depth': max_depth,
            'url_pattern': url_pattern,
            'crawled_urls': [],
            'failed_urls': [],
        }

        parsed_start = urlparse(start_url)
        base_domain = parsed_start.netloc

        while to_visit and len(visited) < max_pages:
            url, depth = to_visit.pop(0)

            # Skip if already visited
            if url in visited:
                continue

            visited.add(url)

            # Process this page
            try:
                result = self.process(url, use_playwright=use_playwright, **kwargs)

                if result.success and result.processed_content:
                    results.append(result)

                    # Add page header for context
                    page_title = result.metadata.get('title', url)
                    page_content = f"\n\n{'='*60}\n## {page_title}\nSource: {url}\n{'='*60}\n\n{result.processed_content}"
                    all_content.append(page_content)
                    all_metadata['crawled_urls'].append({
                        'url': url,
                        'title': page_title,
                        'word_count': result.word_count,
                        'depth': depth
                    })

                    # Extract links if we haven't reached max depth
                    if depth < max_depth and result.raw_content:
                        new_links = self._extract_links(
                            result.raw_content,
                            url,
                            same_domain_only=same_domain_only,
                            url_pattern=url_pattern
                        )
                        for link in new_links:
                            if link not in visited:
                                to_visit.append((link, depth + 1))
                else:
                    all_metadata['failed_urls'].append({
                        'url': url,
                        'error': result.error_message or 'No content extracted'
                    })

            except Exception as e:
                all_metadata['failed_urls'].append({
                    'url': url,
                    'error': str(e)
                })

            # Small delay to be respectful
            time.sleep(0.5)

        all_metadata['pages_crawled'] = len(results)

        # Combine all content
        combined_content = '\n'.join(all_content)
        total_words = sum(r.word_count for r in results)

        return MultiPageCrawlResult(
            success=len(results) > 0,
            pages_crawled=len(results),
            combined_content=combined_content,
            individual_results=results,
            metadata=all_metadata,
            total_word_count=total_words,
            error_message=None if results else "No pages successfully crawled"
        )


class MultiPageCrawlResult:
    """
    Result of a multi-page crawl operation.
    Session 733: Added for site-wide document ingestion.
    """
    def __init__(self, success: bool, pages_crawled: int, combined_content: str,
                 individual_results: List[ProcessingResult], metadata: Dict[str, Any],
                 total_word_count: int, error_message: str = None):
        self.success = success
        self.pages_crawled = pages_crawled
        self.combined_content = combined_content
        self.individual_results = individual_results
        self.metadata = metadata
        self.total_word_count = total_word_count
        self.error_message = error_message


class DOCXProcessor(BaseProcessor):
    """Process DOCX (Word) files"""

    def __init__(self):
        super().__init__()
        self.supported_types = [
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        ]

    def can_process(self, file_path: str, mime_type: str) -> bool:
        return (mime_type in self.supported_types or
                file_path.endswith('.docx')) and HAS_DOCX

    def process(self, file_input, **kwargs) -> ProcessingResult:
        if not HAS_DOCX:
            return ProcessingResult(
                success=False,
                error_message="DOCX processing requires python-docx library",
                processing_steps=[
                    {'step': 'dependency_check', 'status': 'error', 'error': 'python-docx not available'}
                ]
            )

        try:
            import docx
            import io

            if isinstance(file_input, bytes):
                f = io.BytesIO(file_input)
                file_size = len(file_input)
            else:
                f = open(file_input, 'rb')
                file_size = os.path.getsize(file_input)

            doc = docx.Document(f)

            if not isinstance(file_input, bytes):
                f.close()

            # Extract text from paragraphs
            paragraphs = []
            for para in doc.paragraphs:
                text = para.text.strip()
                if text:
                    paragraphs.append(text)

            # Extract text from tables
            table_texts = []
            for table in doc.tables:
                for row in table.rows:
                    row_text = ' | '.join(cell.text.strip() for cell in row.cells if cell.text.strip())
                    if row_text:
                        table_texts.append(row_text)

            raw_content = '\n'.join(paragraphs)
            if table_texts:
                raw_content += '\n\n' + '\n'.join(table_texts)

            processed_content = self._clean_text(raw_content)
            language = self._detect_language(processed_content)
            word_count = len(processed_content.split()) if processed_content else 0
            key_phrases = self._extract_key_phrases(processed_content)
            entities = self._extract_entities(processed_content)

            # Extract metadata
            core_props = doc.core_properties
            metadata = {
                'processor': 'DOCXProcessor',
                'file_size': file_size,
                'filename': kwargs.get('filename', 'unknown.docx'),
                'paragraph_count': len(paragraphs),
                'table_count': len(doc.tables),
                'title': core_props.title or '',
                'author': core_props.author or '',
                'subject': core_props.subject or '',
            }

            return ProcessingResult(
                success=True,
                raw_content=raw_content,
                processed_content=processed_content,
                metadata=metadata,
                language=language,
                word_count=word_count,
                key_phrases=key_phrases,
                entities=entities,
                processing_steps=[
                    {'step': 'docx_open', 'status': 'success'},
                    {'step': 'text_extraction', 'status': 'success', 'paragraphs': len(paragraphs)},
                    {'step': 'table_extraction', 'status': 'success', 'tables': len(doc.tables)},
                ]
            )

        except Exception as e:
            return ProcessingResult(
                success=False,
                error_message=str(e),
                processing_steps=[
                    {'step': 'docx_processing', 'status': 'error', 'error': str(e)}
                ]
            )


class CSVProcessor(BaseProcessor):
    """Process CSV files"""

    def __init__(self):
        super().__init__()
        self.supported_types = ['text/csv', 'application/csv']

    def can_process(self, file_path: str, mime_type: str) -> bool:
        return (mime_type in self.supported_types or
                file_path.endswith('.csv')) and HAS_PANDAS

    def process(self, file_input, **kwargs) -> ProcessingResult:
        if not HAS_PANDAS:
            return ProcessingResult(
                success=False,
                error_message="CSV processing requires pandas library",
                processing_steps=[
                    {'step': 'dependency_check', 'status': 'error', 'error': 'pandas not available'}
                ]
            )

        try:
            import pandas as pd
            import io

            if isinstance(file_input, bytes):
                f = io.BytesIO(file_input)
                file_size = len(file_input)
            elif isinstance(file_input, str) and not os.path.exists(file_input):
                # Assume it's CSV content as a string
                f = io.StringIO(file_input)
                file_size = len(file_input.encode('utf-8'))
            else:
                f = file_input
                file_size = os.path.getsize(file_input) if isinstance(file_input, str) else 0

            df = pd.read_csv(f, nrows=10000)

            # Build text representation
            parts = []
            parts.append(f"CSV with {len(df)} rows and {len(df.columns)} columns.")
            parts.append(f"Columns: {', '.join(df.columns.tolist())}")
            parts.append("")

            # Column summaries
            for col in df.columns:
                unique = df[col].nunique()
                nulls = df[col].isnull().sum()
                sample = df[col].dropna().head(3).tolist()
                sample_str = ', '.join(str(v) for v in sample)
                parts.append(f"{col}: {unique} unique values, {nulls} nulls. Sample: {sample_str}")

            parts.append("")

            # Include first rows as text (up to 50 rows)
            row_limit = min(len(df), 50)
            parts.append(f"First {row_limit} rows:")
            for idx, row in df.head(row_limit).iterrows():
                row_text = ' | '.join(f"{col}: {val}" for col, val in row.items() if pd.notna(val))
                parts.append(row_text)

            raw_content = df.head(100).to_csv(index=False)
            processed_content = self._clean_text('\n'.join(parts))
            language = self._detect_language(processed_content)
            word_count = len(processed_content.split()) if processed_content else 0
            key_phrases = self._extract_key_phrases(processed_content)
            entities = self._extract_entities(processed_content)

            metadata = {
                'processor': 'CSVProcessor',
                'file_size': file_size,
                'filename': kwargs.get('filename', 'unknown.csv'),
                'row_count': len(df),
                'column_count': len(df.columns),
                'columns': df.columns.tolist(),
            }

            return ProcessingResult(
                success=True,
                raw_content=raw_content,
                processed_content=processed_content,
                metadata=metadata,
                language=language,
                word_count=word_count,
                key_phrases=key_phrases,
                entities=entities,
                processing_steps=[
                    {'step': 'csv_parse', 'status': 'success', 'rows': len(df)},
                    {'step': 'column_analysis', 'status': 'success', 'columns': len(df.columns)},
                    {'step': 'text_conversion', 'status': 'success'},
                ]
            )

        except Exception as e:
            return ProcessingResult(
                success=False,
                error_message=str(e),
                processing_steps=[
                    {'step': 'csv_processing', 'status': 'error', 'error': str(e)}
                ]
            )


class DocumentProcessingPipeline:
    """Main document processing pipeline"""

    def __init__(self):
        self.processors = [
            YouTubeProcessor(),  # Check YouTube URLs first
            URLProcessor(),      # Then other URLs
            TextProcessor(),
            MarkdownProcessor(),
            HTMLProcessor(),
            PDFProcessor(),
            DOCXProcessor(),
            CSVProcessor(),
            JSONProcessor(),
        ]

    def process_url(self, url: str, **kwargs) -> ProcessingResult:
        """Process a URL (YouTube or web page)"""
        # Check YouTube first
        youtube_processor = YouTubeProcessor()
        if youtube_processor.can_process(url, ''):
            return youtube_processor.process(url, **kwargs)

        # Then try URL processor
        url_processor = URLProcessor()
        if url_processor.can_process(url, ''):
            return url_processor.process(url, **kwargs)

        return ProcessingResult(
            success=False,
            error_message=f"No processor available for URL: {url}",
            processing_steps=[
                {'step': 'url_detection', 'status': 'error', 'error': 'Unsupported URL format'}
            ]
        )
    
    def get_processor(self, file_path: str, mime_type: str = None) -> Optional[BaseProcessor]:
        """Get appropriate processor for file"""
        if not mime_type:
            mime_type, _ = mimetypes.guess_type(file_path)
        
        for processor in self.processors:
            if processor.can_process(file_path, mime_type or ""):
                return processor
        
        return None
    
    def process_document(self, file_path: str, **kwargs) -> ProcessingResult:
        """Process a document through the pipeline"""
        if not os.path.exists(file_path):
            return ProcessingResult(
                success=False,
                error_message=f"File not found: {file_path}",
                processing_steps=[
                    {'step': 'file_check', 'status': 'error', 'error': 'File not found'}
                ]
            )
        
        mime_type, _ = mimetypes.guess_type(file_path)
        processor = self.get_processor(file_path, mime_type)
        
        if not processor:
            return ProcessingResult(
                success=False,
                error_message=f"No processor available for file type: {mime_type}",
                processing_steps=[
                    {'step': 'processor_selection', 'status': 'error', 
                     'error': f'Unsupported file type: {mime_type}'}
                ]
            )
        
        return processor.process(file_path, **kwargs)


# Global pipeline instance
pipeline = DocumentProcessingPipeline()