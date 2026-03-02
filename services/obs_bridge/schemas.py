"""
Pydantic response/request models for OBS Bridge API.
"""

from typing import Literal
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    code: str
    message: str
    detail: str | None = None


class ErrorResponse(BaseModel):
    ok: Literal[False] = False
    error: ErrorDetail


class StatusResponse(BaseModel):
    ok: bool
    isRecording: bool
    recordingTimecode: str | None = None
    obsVersion: str | None = None
    websocketVersion: str | None = None


class FileInfo(BaseModel):
    path: str
    filename: str
    ext: str
    sizeBytes: int
    mtime: str


class LastResponse(BaseModel):
    ok: bool
    recordingsDir: str
    allowedExtensions: list[str]
    file: FileInfo | None = None


class UploadRequest(BaseModel):
    title: str | None = None
    tags: list[str] | None = None
    stopIfRecording: bool = False


class MediaInfo(BaseModel):
    id: str
    type: str
    contentType: str
    title: str
    filename: str
    sizeBytes: int


class UploadResponse(BaseModel):
    ok: bool
    uploaded: bool
    media: MediaInfo | None = None


class StartResponse(BaseModel):
    ok: bool
    isRecording: bool
    timestamp: str | None = None


class StopResponse(BaseModel):
    ok: bool
    isRecording: bool
    timestamp: str | None = None
