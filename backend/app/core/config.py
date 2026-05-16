from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Sperm Analysis System"
    environment: str = "development"
    database_url: str = "sqlite:///./data/sperm_analysis.db"
    upload_dir: Path = Path("./data/uploads")
    max_upload_mb: int = Field(default=512, ge=1, le=4096)
    allowed_origins: str = "http://localhost:3000"
    api_key: str | None = None
    yolo_weights_path: str | None = None
    default_microns_per_pixel: float = Field(default=0.33, gt=0)
    default_chamber_depth_microns: float = Field(default=20.0, gt=0)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()

