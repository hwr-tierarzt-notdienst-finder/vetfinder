from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    domain: str
    human_readable_project_name: str
    db: "DbConfig"
    fastapi: "FastAPIConfig"
    auth: "AuthConfig"
    email: "EmailConfig"
    form: "FormConfig"
    content_management: "ContentManagementConfig"


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
    jwt_secret: str


@dataclass(frozen=True)
class EmailConfig:
    sender_address: str
    smtp_server_hostname: str
    smtp_server_port: int
    smtp_server_username: str
    smtp_server_password: str
    plaintext_line_length: int


@dataclass(frozen=True)
class FormConfig:
    vet_registration_url_template: str

    def __post_init__(self) -> None:
        if "{token}" not in self.vet_registration_url_template.replace(" ", ""):
            raise ValueError(
                "'vet_registration_url_template' "
                "does not contain placeholder '{token}'"
            )


@dataclass(frozen=True)
class ContentManagementConfig:
    email_addresses: list[str]
