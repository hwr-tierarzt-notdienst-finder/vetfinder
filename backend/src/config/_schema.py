from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    db: "DbConfig"
    auth: "AuthConfig"


@dataclass(frozen=True)
class DbConfig:
    port: int
    container_name: str
    root_username: str
    root_password: str
    connection_ping_timeout: float


@dataclass(frozen=True)
class AuthConfig:
    tokens_file_path: Path
