from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Dynamic Gesture Recognition System"
    app_cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    mmaction_config: str = "assets/models/trained-jester-tsm-r50/tsm_r50_jester_video_infer.py"
    mmaction_checkpoint: str = "assets/models/trained-jester-tsm-r50/best_acc_top1_epoch_8.pth"
    mmaction_device: str = "cpu"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origins(self) -> list[str]:
        return [item.strip() for item in self.app_cors_origins.split(",") if item.strip()]

    @property
    def project_root(self) -> Path:
        return Path(__file__).resolve().parents[2]

    def resolve_path(self, value: str) -> Path:
        path = Path(value)
        if path.is_absolute():
            return path
        return (self.project_root / path).resolve()


@lru_cache
def get_settings() -> Settings:
    return Settings()
