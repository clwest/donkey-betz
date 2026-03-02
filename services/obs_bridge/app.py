"""
OBS Bridge Service — FastAPI app exposing recording control + upload.

Runs on the local workstation, connects to OBS via obs-websocket v5.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import Depends, FastAPI, Request, Response
from fastapi.responses import JSONResponse

from auth import require_token
from config import settings
from obs_client import OBSClient
from recordings import find_latest_recording
from schemas import (
    ErrorDetail,
    ErrorResponse,
    LastResponse,
    StartResponse,
    StatusResponse,
    StopResponse,
    UploadRequest,
    UploadResponse,
)
from uploader import upload_to_platform

logger = logging.getLogger("obs_bridge")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")

obs = OBSClient(url=settings.OBS_WEBSOCKET_URL, password=settings.OBS_WEBSOCKET_PASSWORD)


def _error(status_code: int, code: str, message: str, detail: str | None = None) -> JSONResponse:
    body = ErrorResponse(error=ErrorDetail(code=code, message=message, detail=detail))
    return JSONResponse(status_code=status_code, content=body.model_dump())


@asynccontextmanager
async def lifespan(application: FastAPI):
    # Startup
    rec_dir = Path(settings.OBS_RECORDINGS_DIR)
    logger.info(
        "OBS Bridge starting — OBS=%s  recordings=%s  extensions=%s  token=%s***",
        settings.OBS_WEBSOCKET_URL,
        settings.OBS_RECORDINGS_DIR,
        settings.extensions_list,
        settings.OBS_BRIDGE_TOKEN[:4] if len(settings.OBS_BRIDGE_TOKEN) >= 4 else "???",
    )
    if not rec_dir.is_dir():
        logger.warning("Recordings directory does not exist: %s", rec_dir)
    yield
    # Shutdown
    obs.disconnect()
    logger.info("OBS Bridge shut down")


app = FastAPI(title="OBS Bridge", version="1.0.0", lifespan=lifespan)

BRIDGE_VERSION = "1"


@app.middleware("http")
async def add_version_header(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["X-Bridge-Version"] = BRIDGE_VERSION
    return response


# ── Health (no auth) ──────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"ok": True, "version": int(BRIDGE_VERSION)}


# ── Recording routes (auth required) ─────────────────────────────

@app.get("/v1/recording/status", response_model=StatusResponse)
async def recording_status(_token: str = Depends(require_token)):
    try:
        result = obs.get_status()
    except ConnectionError as exc:
        return _error(502, "OBS_UNAVAILABLE", str(exc))
    if not result.get("ok"):
        err = result.get("error", {})
        return _error(502, err.get("code", "OBS_ERROR"), err.get("message", "Unknown OBS error"))
    return result


@app.post("/v1/recording/start", response_model=StartResponse)
async def recording_start(_token: str = Depends(require_token)):
    try:
        result = obs.start_recording()
    except ConnectionError as exc:
        return _error(502, "OBS_UNAVAILABLE", str(exc))
    if not result.get("ok"):
        err = result.get("error", {})
        return _error(502, err.get("code", "OBS_ERROR"), err.get("message", "Unknown OBS error"))
    result["timestamp"] = datetime.now(tz=timezone.utc).isoformat()
    return result


@app.post("/v1/recording/stop", response_model=StopResponse)
async def recording_stop(_token: str = Depends(require_token)):
    try:
        result = obs.stop_recording()
    except ConnectionError as exc:
        return _error(502, "OBS_UNAVAILABLE", str(exc))
    if not result.get("ok"):
        err = result.get("error", {})
        return _error(502, err.get("code", "OBS_ERROR"), err.get("message", "Unknown OBS error"))
    result["timestamp"] = datetime.now(tz=timezone.utc).isoformat()
    return result


@app.get("/v1/recording/last", response_model=LastResponse)
async def recording_last(_token: str = Depends(require_token)):
    try:
        file_info = find_latest_recording(
            settings.OBS_RECORDINGS_DIR, settings.extensions_list
        )
    except FileNotFoundError as exc:
        return _error(404, "RECORDINGS_DIR_NOT_FOUND", str(exc))

    return LastResponse(
        ok=True,
        recordingsDir=settings.OBS_RECORDINGS_DIR,
        allowedExtensions=settings.extensions_list,
        file=file_info,
    )


@app.post("/v1/recording/upload_last", response_model=UploadResponse)
async def recording_upload_last(
    body: UploadRequest | None = None,
    _token: str = Depends(require_token),
):
    body = body or UploadRequest()

    if not settings.PLATFORM_UPLOAD_URL:
        return _error(400, "NO_UPLOAD_URL", "PLATFORM_UPLOAD_URL is not configured")

    # Optionally stop recording first
    if body.stopIfRecording:
        try:
            status = obs.get_status()
        except ConnectionError as exc:
            return _error(502, "OBS_UNAVAILABLE", str(exc))
        if status.get("ok") and status.get("isRecording"):
            obs.stop_recording()
            await asyncio.sleep(settings.SETTLE_DELAY_SECONDS)

    # Find latest recording
    try:
        file_info = find_latest_recording(
            settings.OBS_RECORDINGS_DIR, settings.extensions_list
        )
    except FileNotFoundError as exc:
        return _error(404, "RECORDINGS_DIR_NOT_FOUND", str(exc))

    if file_info is None:
        return _error(404, "NO_RECORDINGS_FOUND", "No matching recordings found")

    # Upload
    result = upload_to_platform(
        file_path=file_info["path"],
        upload_url=settings.PLATFORM_UPLOAD_URL,
        token=settings.PLATFORM_UPLOAD_TOKEN,
        title=body.title,
        tags=body.tags,
    )

    if not result.get("ok"):
        err = result.get("error", {})
        return _error(502, err.get("code", "UPLOAD_FAILED"), err.get("message", "Upload failed"))

    return result


# ── Entrypoint ────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host=settings.BRIDGE_HOST,
        port=settings.BRIDGE_PORT,
        reload=True,
    )
