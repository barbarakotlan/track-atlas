from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parent


class Settings(BaseSettings):
    app_name: str = "Track Atlas"

    knowledge_base_dir: Path = REPO_ROOT / "knowledge-base"
    storage_dir: Path = REPO_ROOT / "storage"

    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dimension: int = 384

    llm_model: str = "llama3.2:3b"
    ollama_host: str = "http://localhost:11434"

    chunk_size: int = 800
    chunk_overlap: int = 100
    top_k: int = 5

    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(env_file=".env", env_prefix="TRACK_ATLAS_")


settings = Settings()
