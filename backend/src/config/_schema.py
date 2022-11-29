from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    db: "DbConfig"
    fastapi: "FastAPIConfig"
    auth: "AuthConfig"


@dataclass(frozen=True)
class DbConfig:
    port: int
    container_name: str
    root_username: str
    root_password: str
    connection_ping_timeout: float


@dataclass(frozen=True)
class FastAPIConfig:
    port: int


@dataclass(frozen=True)
class AuthConfig:
    pass
