"""
Scan recordings directory for the latest file matching allowed extensions.
"""

from datetime import datetime, timezone
from pathlib import Path


def find_latest_recording(
    recordings_dir: str, allowed_extensions: list[str]
) -> dict | None:
    """Return FileInfo-compatible dict for the newest matching file, or None."""
    dirpath = Path(recordings_dir)
    if not dirpath.is_dir():
        raise FileNotFoundError(f"Recordings directory not found: {recordings_dir}")

    candidates = [
        f
        for f in dirpath.iterdir()
        if f.is_file() and f.suffix.lower() in allowed_extensions
    ]
    if not candidates:
        return None

    latest = max(candidates, key=lambda f: f.stat().st_mtime)
    stat = latest.stat()

    return {
        "path": str(latest),
        "filename": latest.name,
        "ext": latest.suffix,
        "sizeBytes": stat.st_size,
        "mtime": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
    }
