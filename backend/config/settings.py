"""Application configuration settings."""

import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Settings
    app_name: str = "MedXP Context Enrichment Agent"
    app_version: str = "0.1.0"
    debug: bool = True

    # MiniMax API Settings
    minimax_api_key: Optional[str] = None
    minimax_group_id: Optional[str] = None
    minimax_base_url: str = "https://api.minimax.chat/v1"
    minimax_model: str = "abab5.5-chat"

    # Paths
    base_dir: Path = Path(__file__).parent.parent
    data_dir: Path = base_dir / "data"
    sops_path: Path = data_dir / "sops" / "nsclc_sops.json"
    policies_path: Path = data_dir / "policies" / "hospital_policies.json"
    guidelines_path: Path = data_dir / "medical_guidelines" / "nsclc_guidelines.json"

    # Knowledge Retriever Settings
    retrieval_top_k: int = 5
    relevance_threshold: float = 0.3

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
