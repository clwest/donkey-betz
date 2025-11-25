"""
Temporary file management utilities.
Phase 2 High Priority - Task 2.10

Provides context managers for safe temporary file handling with guaranteed cleanup.
"""

import os
import shutil
import tempfile
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)


@contextmanager
def temp_file(suffix: str = '', prefix: str = 'donkey_', delete: bool = True):
    """
    Context manager for temporary files with guaranteed cleanup.

    Usage:
        with temp_file(suffix='.mp4') as temp_path:
            # Write to temp_path
            # Process file
            # Move to final location if needed
        # temp_path automatically deleted

    Args:
        suffix: File suffix (e.g., '.mp4', '.jpg')
        prefix: File prefix for identification
        delete: Whether to delete the file on exit (default True)

    Yields:
        str: Path to the temporary file
    """
    fd = None
    path = None
    try:
        fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
        os.close(fd)  # Close the file descriptor, we just need the path
        fd = None
        logger.debug(f"Created temp file: {path}")
        yield path
    finally:
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass

        if delete and path:
            try:
                if os.path.exists(path):
                    os.unlink(path)
                    logger.debug(f"Deleted temp file: {path}")
            except Exception as e:
                logger.warning(f"Failed to delete temp file {path}: {e}")


@contextmanager
def temp_directory(prefix: str = 'donkey_', delete: bool = True):
    """
    Context manager for temporary directories with guaranteed cleanup.

    Usage:
        with temp_directory() as temp_dir:
            # Create files in temp_dir
            # Process files
        # temp_dir and all contents automatically deleted

    Args:
        prefix: Directory prefix for identification
        delete: Whether to delete the directory on exit (default True)

    Yields:
        str: Path to the temporary directory
    """
    path = None
    try:
        path = tempfile.mkdtemp(prefix=prefix)
        logger.debug(f"Created temp directory: {path}")
        yield path
    finally:
        if delete and path:
            try:
                if os.path.exists(path):
                    shutil.rmtree(path)
                    logger.debug(f"Deleted temp directory: {path}")
            except Exception as e:
                logger.warning(f"Failed to delete temp directory {path}: {e}")


@contextmanager
def temp_file_from_content(
    content: bytes,
    suffix: str = '',
    prefix: str = 'donkey_',
    delete: bool = True
):
    """
    Context manager that creates a temp file with given content.

    Usage:
        with temp_file_from_content(image_bytes, suffix='.jpg') as path:
            # path contains the image
            result = process_image(path)
        # temp file automatically deleted

    Args:
        content: Bytes to write to the file
        suffix: File suffix
        prefix: File prefix
        delete: Whether to delete on exit

    Yields:
        str: Path to the temporary file containing the content
    """
    with temp_file(suffix=suffix, prefix=prefix, delete=delete) as path:
        with open(path, 'wb') as f:
            f.write(content)
        yield path


@contextmanager
def temp_file_from_url(
    url: str,
    suffix: str = '',
    prefix: str = 'donkey_',
    delete: bool = True,
    timeout: int = 30
):
    """
    Context manager that downloads a URL to a temp file.

    Usage:
        with temp_file_from_url('https://example.com/video.mp4', suffix='.mp4') as path:
            # path contains the downloaded file
            result = process_video(path)
        # temp file automatically deleted

    Args:
        url: URL to download
        suffix: File suffix (auto-detected if not provided)
        prefix: File prefix
        delete: Whether to delete on exit
        timeout: Download timeout in seconds

    Yields:
        str: Path to the temporary file containing the downloaded content

    Raises:
        requests.RequestException: If download fails
    """
    import requests
    from urllib.parse import urlparse

    # Auto-detect suffix from URL if not provided
    if not suffix:
        parsed = urlparse(url)
        path_suffix = os.path.splitext(parsed.path)[1]
        if path_suffix:
            suffix = path_suffix

    with temp_file(suffix=suffix, prefix=prefix, delete=delete) as path:
        logger.debug(f"Downloading {url} to {path}")
        response = requests.get(url, timeout=timeout, stream=True)
        response.raise_for_status()

        with open(path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        logger.debug(f"Downloaded {len(response.content)} bytes to {path}")
        yield path


def cleanup_old_temp_files(
    prefix: str = 'donkey_',
    max_age_hours: int = 24,
    temp_dir: str = None
):
    """
    Clean up old temporary files that may have been left behind.

    This can be run periodically (e.g., via Celery) to clean up orphaned temp files.

    Args:
        prefix: Only delete files with this prefix
        max_age_hours: Delete files older than this many hours
        temp_dir: Directory to clean (defaults to system temp dir)
    """
    import time

    if temp_dir is None:
        temp_dir = tempfile.gettempdir()

    max_age_seconds = max_age_hours * 3600
    current_time = time.time()
    deleted_count = 0
    error_count = 0

    try:
        for filename in os.listdir(temp_dir):
            if not filename.startswith(prefix):
                continue

            filepath = os.path.join(temp_dir, filename)

            try:
                # Get file age
                stat = os.stat(filepath)
                file_age = current_time - stat.st_mtime

                if file_age > max_age_seconds:
                    if os.path.isfile(filepath):
                        os.unlink(filepath)
                    elif os.path.isdir(filepath):
                        shutil.rmtree(filepath)

                    deleted_count += 1
                    logger.debug(f"Cleaned up old temp file: {filepath}")

            except Exception as e:
                error_count += 1
                logger.warning(f"Failed to clean up {filepath}: {e}")

    except Exception as e:
        logger.error(f"Error during temp file cleanup: {e}")

    if deleted_count > 0 or error_count > 0:
        logger.info(f"Temp file cleanup: deleted {deleted_count}, errors {error_count}")

    return deleted_count, error_count


class TempFileManager:
    """
    Manager class for tracking and cleaning up multiple temp files.

    Usage:
        manager = TempFileManager()
        try:
            path1 = manager.create_file(suffix='.mp4')
            path2 = manager.create_file(suffix='.jpg')
            # Use files...
        finally:
            manager.cleanup()  # Deletes all tracked files
    """

    def __init__(self, prefix: str = 'donkey_'):
        self.prefix = prefix
        self._files = []
        self._dirs = []

    def create_file(self, suffix: str = '', content: bytes = None) -> str:
        """Create a temp file and track it for cleanup."""
        fd, path = tempfile.mkstemp(suffix=suffix, prefix=self.prefix)
        os.close(fd)
        self._files.append(path)

        if content:
            with open(path, 'wb') as f:
                f.write(content)

        return path

    def create_directory(self) -> str:
        """Create a temp directory and track it for cleanup."""
        path = tempfile.mkdtemp(prefix=self.prefix)
        self._dirs.append(path)
        return path

    def cleanup(self):
        """Clean up all tracked temp files and directories."""
        for path in self._files:
            try:
                if os.path.exists(path):
                    os.unlink(path)
            except Exception as e:
                logger.warning(f"Failed to delete temp file {path}: {e}")

        for path in self._dirs:
            try:
                if os.path.exists(path):
                    shutil.rmtree(path)
            except Exception as e:
                logger.warning(f"Failed to delete temp dir {path}: {e}")

        self._files = []
        self._dirs = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
        return False
