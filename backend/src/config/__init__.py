from dotenv import dotenv_values

import env
import paths
from ._models import *


_cached_config: Config | None = None
_cached_dotenv_vars: dict | None = None


def get() -> Config:
    global _cached_config

    env_context = env.get_context()

    if _cached_config is None:
        _cached_config = Config(
            domain=_get_dotenv_var_value(
                "DOMAIN",
                context=env_context,
            ),
            human_readable_project_name=_get_dotenv_var_value(
                "HUMAN_READABLE_PROJECT_NAME"
            ),
            db=_get_db_config(env_context),
            fastapi=_get_fastapi_config(env_context),
            auth=_get_auth_config(env_context),
            email=_get_email_config(env_context),
            form=_get_form_config(env_context),
            content_management=_get_content_management_config(env_context),
        )

    return _cached_config


def reset_cache() -> None:
    global _cached_config
    global _cached_dotenv_vars

    _cached_config = None
    _cached_dotenv_vars = None


def _get_db_config(env_context: env.Context) -> DbConfig:
    return DbConfig(
        port=int(_get_mongo_dotenv_var_value(
            "HOST_PORT",
            context=env_context
        )),
        container_name=_get_mongo_dotenv_var_value(
            "CONTAINER_BASE_NAME",
        ) + f"_{env_context}",
        root_username=_get_mongo_dotenv_var_value(
            "INITDB_ROOT_USERNAME",
            context=env_context,
        ),
        root_password=_get_mongo_dotenv_var_value(
            "INITDB_ROOT_PASSWORD",
            context=env_context,
        ),
        connection_ping_timeout=float(_get_mongo_dotenv_var_value(
            "CONNECTION_PING_TIMEOUT",
            context=env_context,
        ))
    )


def _get_fastapi_config(env_context: env.Context) -> FastAPIConfig:
    return FastAPIConfig(
        port=int(_get_fastapi_dotenv_var_value(
            "PORT",
            context=env_context
        ))
    )


def _get_auth_config(env_context: env.Context) -> AuthConfig:
    return AuthConfig(
        jwt_secret=_get_access_control_dotenv_var_value(
            "JWT_SECRET",
            context=env_context,
        )
    )


def _get_email_config(env_context: env.Context) -> EmailConfig:
    return EmailConfig(
        sender_address=_get_email_dotenv_var_value(
            "SENDER_ADDRESS",
            context=env_context,
        ),
        smtp_server_hostname=_get_email_dotenv_var_value(
            "SMTP_SERVER_HOST",
            context=env_context,
        ),
        smtp_server_port=int(_get_email_dotenv_var_value(
            "SMTP_SERVER_PORT",
            context=env_context,
        )),
        smtp_server_username=_get_email_dotenv_var_value(
            "SMTP_SERVER_USERNAME",
            context=env_context,
        ),
        smtp_server_password=_get_email_dotenv_var_value(
            "SMTP_SERVER_PASSWORD",
            context=env_context,
        ),
        plaintext_line_length=int(_get_email_dotenv_var_value(
            "PLAINTEXT_LINE_LEN",
        ))
    )


def _get_form_config(env_context: env.Context) -> FormConfig:
    return FormConfig(
        vet_registration_url_template=_get_form_dotenv_var_value(
            "VET_REGISTRATION_URL_TEMPLATE",
            context=env_context,
        )
    )


def _get_content_management_config(env_context: env.Context) -> ContentManagementConfig:
    return ContentManagementConfig(
        email_addresses=_get_content_management_dotenv_var_value(
            "EMAIL_ADDRESSES",
            context=env_context,
        ).split(",")
    )


def _get_mongo_dotenv_var_value(
        name: str,
        *,
        context: env.Context | None = None,
) -> str:
    return _get_dotenv_var_value(
        name,
        category="MONGO",
        context=context
    )


def _get_fastapi_dotenv_var_value(
        name: str,
        *,
        context: env.Context | None = None,
) -> str:
    return _get_dotenv_var_value(
        name,
        category="FASTAPI",
        context=context,
    )


def _get_access_control_dotenv_var_value(
        name: str,
        *,
        context: env.Context | None = None,
) -> str:
    return _get_dotenv_var_value(
        name,
        category="ACCESS_CONTROL",
        context=context
    )


def _get_email_dotenv_var_value(
        name: str,
        *,
        context: env.Context | None = None,
) -> str:
    return _get_dotenv_var_value(
        name,
        category="EMAIL",
        context=context
    )


def _get_form_dotenv_var_value(
        name: str,
        *,
        context: env.Context | None = None,
) -> str:
    return _get_dotenv_var_value(
        name,
        category="FORM",
        context=context
    )


def _get_content_management_dotenv_var_value(
        name: str,
        *,
        context: env.Context | None = None,
) -> str:
    return _get_dotenv_var_value(
        name,
        category="CONTENT_MANAGEMENT",
        context=context
    )


def _get_dotenv_var_value(
        name: str,
        *,
        category: str | None = None,
        context: env.Context | None = None,
) -> str:
    global _cached_dotenv_vars

    if category is None:
        env_var_name_start = ""
    else:
        env_var_name_start = f"{category}_"

    if context is None:
        env_var_name_middle = ""
    else:
        env_var_name_middle = f"{context.upper()}_"

    env_var_name = f"{env_var_name_start}{env_var_name_middle}{name}"

    if _cached_dotenv_vars is None:
        _cached_dotenv_vars = {
            **dotenv_values(paths.find_backend() / ".env"),
            **dotenv_values(paths.find_backend() / ".env.secret"),
            **dotenv_values(paths.find_backend() / ".env.local")
        }

    return _cached_dotenv_vars[env_var_name]
