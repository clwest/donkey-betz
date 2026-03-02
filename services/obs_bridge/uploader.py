"""
Upload a recording file to the platform via multipart POST.
"""

import logging
from pathlib import Path

import requests

logger = logging.getLogger("obs_bridge.uploader")


def upload_to_platform(
    file_path: str,
    upload_url: str,
    token: str,
    title: str | None = None,
    tags: list[str] | None = None,
) -> dict:
    """Stream-upload file to platform. Returns parsed JSON or error dict."""
    path = Path(file_path)
    if not path.is_file():
        return {"ok": False, "error": {"code": "FILE_NOT_FOUND", "message": f"File not found: {file_path}"}}

    headers = {"Authorization": f"Token {token}"}
    data = {}
    if title:
        data["title"] = title
    if tags:
        data["tags"] = ",".join(tags)

    try:
        with open(path, "rb") as fh:
            resp = requests.post(
                upload_url,
                headers=headers,
                data=data,
                files={"file": (path.name, fh, "video/mp4")},
                timeout=300,
            )

        if resp.status_code in (401, 403):
            return {
                "ok": False,
                "error": {
                    "code": "PLATFORM_AUTH_FAILED",
                    "message": f"Platform returned {resp.status_code}",
                },
            }

        resp.raise_for_status()
        return {"ok": True, "uploaded": True, **resp.json()}

    except requests.RequestException as exc:
        logger.error("Upload failed: %s", exc)
        return {
            "ok": False,
            "error": {"code": "UPLOAD_FAILED", "message": str(exc)},
        }
