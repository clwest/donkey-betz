"""
Configuration for OBS Bridge Service

Pydantic Settings loading from environment / .env file.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    OBS_BRIDGE_TOKEN: str
    OBS_WEBSOCKET_URL: str = "ws://127.0.0.1:4455"
    OBS_WEBSOCKET_PASSWORD: str = ""
    OBS_RECORDINGS_DIR: str = "/Users/donkeyking/Movies"
    PLATFORM_UPLOAD_URL: str = ""
    PLATFORM_UPLOAD_TOKEN: str = ""
    BRIDGE_HOST: str = "127.0.0.1"
    BRIDGE_PORT: int = 8787
    SETTLE_DELAY_SECONDS: float = 2.0
    ALLOWED_EXTENSIONS: str = ".mp4"

    @property
    def extensions_list(self) -> list[str]:
        return [e.strip() for e in self.ALLOWED_EXTENSIONS.split(",") if e.strip()]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
