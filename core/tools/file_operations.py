"""
File Operations Tool - Real File Management

Provides comprehensive file operations for agents including:
- File creation, reading, writing
- Directory management
- File format conversions
- Document generation (PDF, DOCX, etc.)
- Template processing
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import tempfile
import shutil

logger = logging.getLogger(__name__)


class FileOperationTool:
    """
    File operations tool for agent execution.
    Handles all file system operations safely and efficiently.
    """

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.FileOps")
        self.is_configured = True  # Always available
        self.temp_dir = Path(tempfile.gettempdir()) / "agent_files"
        self.temp_dir.mkdir(exist_ok=True)

        # Track created files for cleanup
        self.created_files: List[str] = []
        self.logger.info("File operations tool initialized")

    def create_file(self,
                   file_path: Union[str, Path],
                   content: str,
                   encoding: str = 'utf-8') -> Dict[str, Any]:
        """
        Create a file with given content

        Args:
            file_path: Path to the file
            content: Content to write
            encoding: File encoding (default: utf-8)

        Returns:
            Dictionary with operation result
        """
        try:
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)

            self.created_files.append(str(file_path))
            file_size = file_path.stat().st_size

            self.logger.info(f"Created file: {file_path} ({file_size} bytes)")

            return {
                'success': True,
                'file_path': str(file_path),
                'file_size': file_size,
                'encoding': encoding,
                'created_at': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Failed to create file {file_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_path': str(file_path)
            }

    def read_file(self,
                 file_path: Union[str, Path],
                 encoding: str = 'utf-8') -> Dict[str, Any]:
        """
        Read content from a file

        Args:
            file_path: Path to the file
            encoding: File encoding (default: utf-8)

        Returns:
            Dictionary with file content and metadata
        """
        try:
            file_path = Path(file_path)

            if not file_path.exists():
                return {
                    'success': False,
                    'error': 'File does not exist',
                    'file_path': str(file_path)
                }

            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()

            file_stats = file_path.stat()

            return {
                'success': True,
                'content': content,
                'file_path': str(file_path),
                'file_size': file_stats.st_size,
                'modified_at': datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                'encoding': encoding
            }

        except Exception as e:
            self.logger.error(f"Failed to read file {file_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_path': str(file_path)
            }

    def create_directory(self, dir_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Create a directory

        Args:
            dir_path: Path to the directory

        Returns:
            Dictionary with operation result
        """
        try:
            dir_path = Path(dir_path)
            dir_path.mkdir(parents=True, exist_ok=True)

            self.logger.info(f"Created directory: {dir_path}")

            return {
                'success': True,
                'directory_path': str(dir_path),
                'created_at': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Failed to create directory {dir_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'directory_path': str(dir_path)
            }

    def list_files(self,
                  dir_path: Union[str, Path],
                  pattern: str = "*") -> Dict[str, Any]:
        """
        List files in a directory

        Args:
            dir_path: Directory to list
            pattern: Glob pattern to match files

        Returns:
            Dictionary with file list
        """
        try:
            dir_path = Path(dir_path)

            if not dir_path.exists():
                return {
                    'success': False,
                    'error': 'Directory does not exist',
                    'directory_path': str(dir_path)
                }

            files = []
            for file_path in dir_path.glob(pattern):
                if file_path.is_file():
                    stats = file_path.stat()
                    files.append({
                        'name': file_path.name,
                        'path': str(file_path),
                        'size': stats.st_size,
                        'modified_at': datetime.fromtimestamp(stats.st_mtime).isoformat()
                    })

            return {
                'success': True,
                'directory_path': str(dir_path),
                'files': files,
                'file_count': len(files),
                'pattern': pattern
            }

        except Exception as e:
            self.logger.error(f"Failed to list files in {dir_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'directory_path': str(dir_path)
            }

    def create_json_file(self,
                        file_path: Union[str, Path],
                        data: Any) -> Dict[str, Any]:
        """
        Create a JSON file with given data

        Args:
            file_path: Path to the JSON file
            data: Data to serialize to JSON

        Returns:
            Dictionary with operation result
        """
        try:
            json_content = json.dumps(data, indent=2, ensure_ascii=False)
            return self.create_file(file_path, json_content)

        except Exception as e:
            self.logger.error(f"Failed to create JSON file {file_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_path': str(file_path)
            }

    def read_json_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Read and parse a JSON file

        Args:
            file_path: Path to the JSON file

        Returns:
            Dictionary with parsed JSON data
        """
        try:
            file_result = self.read_file(file_path)
            if not file_result['success']:
                return file_result

            data = json.loads(file_result['content'])

            return {
                'success': True,
                'data': data,
                'file_path': str(file_path),
                'file_size': file_result['file_size']
            }

        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error in {file_path}: {e}")
            return {
                'success': False,
                'error': f'Invalid JSON: {str(e)}',
                'file_path': str(file_path)
            }
        except Exception as e:
            self.logger.error(f"Failed to read JSON file {file_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_path': str(file_path)
            }

    def create_markdown_file(self,
                           file_path: Union[str, Path],
                           content: str,
                           metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Create a Markdown file with optional frontmatter

        Args:
            file_path: Path to the Markdown file
            content: Markdown content
            metadata: Optional frontmatter metadata

        Returns:
            Dictionary with operation result
        """
        try:
            full_content = ""

            # Add frontmatter if metadata provided
            if metadata:
                full_content += "---\n"
                for key, value in metadata.items():
                    full_content += f"{key}: {value}\n"
                full_content += "---\n\n"

            full_content += content

            return self.create_file(file_path, full_content)

        except Exception as e:
            self.logger.error(f"Failed to create Markdown file {file_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_path': str(file_path)
            }

    def copy_file(self,
                 source: Union[str, Path],
                 destination: Union[str, Path]) -> Dict[str, Any]:
        """
        Copy a file to a new location

        Args:
            source: Source file path
            destination: Destination file path

        Returns:
            Dictionary with operation result
        """
        try:
            source_path = Path(source)
            dest_path = Path(destination)

            if not source_path.exists():
                return {
                    'success': False,
                    'error': 'Source file does not exist',
                    'source': str(source_path),
                    'destination': str(dest_path)
                }

            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, dest_path)

            self.logger.info(f"Copied file from {source_path} to {dest_path}")

            return {
                'success': True,
                'source': str(source_path),
                'destination': str(dest_path),
                'file_size': dest_path.stat().st_size
            }

        except Exception as e:
            self.logger.error(f"Failed to copy file from {source} to {destination}: {e}")
            return {
                'success': False,
                'error': str(e),
                'source': str(source),
                'destination': str(destination)
            }

    def create_temp_file(self,
                        content: str,
                        suffix: str = '.txt',
                        prefix: str = 'agent_') -> Dict[str, Any]:
        """
        Create a temporary file

        Args:
            content: Content to write
            suffix: File extension
            prefix: Filename prefix

        Returns:
            Dictionary with temp file info
        """
        try:
            temp_file = tempfile.NamedTemporaryFile(
                mode='w',
                suffix=suffix,
                prefix=prefix,
                dir=self.temp_dir,
                delete=False,
                encoding='utf-8'
            )

            temp_file.write(content)
            temp_file.close()

            self.created_files.append(temp_file.name)

            self.logger.info(f"Created temp file: {temp_file.name}")

            return {
                'success': True,
                'file_path': temp_file.name,
                'file_size': Path(temp_file.name).stat().st_size,
                'is_temp': True
            }

        except Exception as e:
            self.logger.error(f"Failed to create temp file: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def create_csv_file(self,
                       file_path: Union[str, Path],
                       data: List[Dict[str, Any]],
                       fieldnames: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create a CSV file from list of dictionaries

        Args:
            file_path: Path to CSV file
            data: List of dictionaries to write
            fieldnames: Optional field names (will use keys from first row if not provided)

        Returns:
            Dictionary with operation result
        """
        try:
            import csv

            if not data:
                return {
                    'success': False,
                    'error': 'No data provided',
                    'file_path': str(file_path)
                }

            if not fieldnames:
                fieldnames = list(data[0].keys())

            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)

            self.created_files.append(str(file_path))
            file_size = file_path.stat().st_size

            self.logger.info(f"Created CSV file: {file_path} with {len(data)} rows")

            return {
                'success': True,
                'file_path': str(file_path),
                'file_size': file_size,
                'rows_written': len(data),
                'columns': fieldnames
            }

        except Exception as e:
            self.logger.error(f"Failed to create CSV file {file_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_path': str(file_path)
            }

    def cleanup_temp_files(self) -> Dict[str, Any]:
        """
        Clean up temporary files created by this tool

        Returns:
            Dictionary with cleanup results
        """
        cleaned_files = []
        errors = []

        for file_path in self.created_files[:]:
            try:
                path = Path(file_path)
                if path.exists() and str(path).startswith(str(self.temp_dir)):
                    path.unlink()
                    cleaned_files.append(str(path))
                    self.created_files.remove(file_path)
            except Exception as e:
                errors.append(f"Failed to delete {file_path}: {e}")

        self.logger.info(f"Cleaned up {len(cleaned_files)} temp files")

        return {
            'success': len(errors) == 0,
            'cleaned_files': cleaned_files,
            'errors': errors,
            'files_cleaned': len(cleaned_files)
        }

    def get_file_info(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get detailed information about a file

        Args:
            file_path: Path to the file

        Returns:
            Dictionary with file information
        """
        try:
            file_path = Path(file_path)

            if not file_path.exists():
                return {
                    'success': False,
                    'error': 'File does not exist',
                    'file_path': str(file_path)
                }

            stats = file_path.stat()

            return {
                'success': True,
                'file_path': str(file_path),
                'name': file_path.name,
                'size': stats.st_size,
                'size_human': self._format_file_size(stats.st_size),
                'created_at': datetime.fromtimestamp(stats.st_ctime).isoformat(),
                'modified_at': datetime.fromtimestamp(stats.st_mtime).isoformat(),
                'is_file': file_path.is_file(),
                'is_directory': file_path.is_dir(),
                'extension': file_path.suffix,
                'absolute_path': str(file_path.absolute())
            }

        except Exception as e:
            self.logger.error(f"Failed to get file info for {file_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_path': str(file_path)
            }

    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

    def get_statistics(self) -> Dict[str, Any]:
        """Get file operation statistics"""
        return {
            'files_created': len(self.created_files),
            'temp_directory': str(self.temp_dir),
            'is_configured': self.is_configured,
            'recent_files': self.created_files[-10:] if self.created_files else []
        }