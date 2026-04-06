from pathlib import Path

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    postgres_connection_string: PostgresDsn
    worker_host: str
    tmp_dir: Path
    threshold_gb: int
    max_workers: int
    cleanup_tmp: bool
    skip_copy_if_exists: bool
