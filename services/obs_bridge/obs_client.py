"""
OBS WebSocket v5 client wrapper using obsws-python.
"""

import logging

import obsws_python as obsws

logger = logging.getLogger("obs_bridge.obs_client")


class OBSClient:
    def __init__(self, url: str, password: str):
        self._url = url
        self._password = password
        self._client: obsws.ReqClient | None = None

    def _parse_host_port(self) -> tuple[str, int]:
        """Extract host and port from ws:// URL."""
        stripped = self._url.replace("ws://", "").replace("wss://", "")
        if ":" in stripped:
            host, port_str = stripped.rsplit(":", 1)
            return host, int(port_str)
        return stripped, 4455

    def _ensure_connected(self) -> obsws.ReqClient:
        if self._client is not None:
            return self._client
        host, port = self._parse_host_port()
        try:
            self._client = obsws.ReqClient(
                host=host, port=port, password=self._password
            )
        except Exception as exc:
            logger.error("Failed to connect to OBS: %s", exc)
            raise ConnectionError(f"Cannot connect to OBS at {self._url}: {exc}") from exc
        return self._client

    def get_status(self) -> dict:
        try:
            client = self._ensure_connected()
            resp = client.get_record_status()
            version = client.get_version()
            return {
                "ok": True,
                "isRecording": resp.output_active,
                "recordingTimecode": getattr(resp, "output_timecode", None),
                "obsVersion": getattr(version, "obs_version", None),
                "websocketVersion": getattr(version, "obs_web_socket_version", None),
            }
        except ConnectionError:
            raise
        except Exception as exc:
            logger.error("get_status failed: %s", exc)
            self._client = None
            return {"ok": False, "error": {"code": "OBS_ERROR", "message": str(exc)}}

    def start_recording(self) -> dict:
        try:
            client = self._ensure_connected()
            client.start_record()
            return {"ok": True, "isRecording": True}
        except ConnectionError:
            raise
        except Exception as exc:
            msg = str(exc)
            # Already recording is not an error
            if "already" in msg.lower() or "recording" in msg.lower():
                return {"ok": True, "isRecording": True}
            logger.error("start_recording failed: %s", exc)
            self._client = None
            return {"ok": False, "error": {"code": "OBS_ERROR", "message": msg}}

    def stop_recording(self) -> dict:
        try:
            client = self._ensure_connected()
            resp = client.stop_record()
            output_path = getattr(resp, "output_path", None)
            return {"ok": True, "isRecording": False, "outputPath": output_path}
        except ConnectionError:
            raise
        except Exception as exc:
            msg = str(exc)
            # Not recording is not an error
            if "not" in msg.lower() and "recording" in msg.lower():
                return {"ok": True, "isRecording": False}
            logger.error("stop_recording failed: %s", exc)
            self._client = None
            return {"ok": False, "error": {"code": "OBS_ERROR", "message": msg}}

    def disconnect(self):
        if self._client is not None:
            try:
                self._client.disconnect()
            except Exception as _e:
                logger.warning(
                    "obs_client.disconnect: swallowed (%s: %s) — degraded",
                    type(_e).__name__, _e,
                )
            self._client = None
