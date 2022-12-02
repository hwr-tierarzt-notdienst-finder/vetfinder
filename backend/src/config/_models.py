from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    human_readable_project_name: str
    db: "DbConfig"
    fastapi: "FastAPIConfig"
    auth: "AuthConfig"
    email: "EmailConfig"


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


@dataclass(frozen=True)
class EmailConfig:
    sender_address: str
    smtp_server_hostname: str
    smtp_server_port: int
    smtp_server_username: str
    smtp_server_password: str
    plaintext_line_length: int
