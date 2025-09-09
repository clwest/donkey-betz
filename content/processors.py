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
    import pypdf2
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
        
        # URLs
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
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
    
    def process(self, file_path: str, **kwargs) -> ProcessingResult:
        if not HAS_PDF:
            return ProcessingResult(
                success=False,
                error_message="PDF processing requires pypdf2 library",
                processing_steps=[
                    {'step': 'dependency_check', 'status': 'error', 'error': 'pypdf2 not available'}
                ]
            )
        
        try:
            import pypdf2
            
            with open(file_path, 'rb') as f:
                pdf_reader = pypdf2.PdfReader(f)
                
                # Extract metadata
                metadata = self._extract_pdf_metadata(pdf_reader)
                
                # Extract text from all pages
                raw_content = ""
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    raw_content += page.extract_text() + "\n"
            
            processed_content = self._clean_text(raw_content)
            language = self._detect_language(processed_content)
            word_count = len(processed_content.split()) if processed_content else 0
            key_phrases = self._extract_key_phrases(processed_content)
            entities = self._extract_entities(processed_content)
            
            metadata.update({
                'processor': 'PDFProcessor',
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


class DocumentProcessingPipeline:
    """Main document processing pipeline"""
    
    def __init__(self):
        self.processors = [
            TextProcessor(),
            MarkdownProcessor(),
            HTMLProcessor(),
            PDFProcessor(),
            JSONProcessor(),
        ]
    
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