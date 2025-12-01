"""
DaVinci Bridge Server Configuration
"""

import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Server Settings
    bridge_host: str = Field(default="0.0.0.0", alias="BRIDGE_HOST")
    bridge_port: int = Field(default=9090, alias="BRIDGE_PORT")
    debug: bool = Field(default=False, alias="DEBUG")

    # DaVinci Resolve Paths
    resolve_script_api: str = Field(
        default="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting",
        alias="RESOLVE_SCRIPT_API"
    )
    resolve_script_lib: str = Field(
        default="/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so",
        alias="RESOLVE_SCRIPT_LIB"
    )

    # Security
    api_key: str = Field(default="dev-key-change-in-production", alias="API_KEY")
    allowed_origins: str = Field(
        default="http://localhost:8000,http://localhost:3000",
        alias="ALLOWED_ORIGINS"
    )

    # Render Settings
    default_render_path: str = Field(default="/tmp/davinci_renders", alias="DEFAULT_RENDER_PATH")
    max_concurrent_renders: int = Field(default=2, alias="MAX_CONCURRENT_RENDERS")
    default_resolution: str = Field(default="1920x1080", alias="DEFAULT_RESOLUTION")
    default_codec: str = Field(default="H264", alias="DEFAULT_CODEC")
    default_format: str = Field(default="mp4", alias="DEFAULT_FORMAT")

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_file: str = Field(default="/tmp/davinci_bridge.log", alias="LOG_FILE")

    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse comma-separated origins into list"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# Global settings instance
settings = Settings()
