from dotenv import dotenv_values

import env
import paths
from ._schema import *


_cached_config: Config | None = None
_cached_dotenv_vars: dict | None = None


def get() -> Config:
    global _cached_config

    env_context = env.get_context()

    if _cached_config is None:
        _cached_config = Config(
            db=_get_db_config(env_context),
            auth=_get_auth_config(env_context),
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
        )),
    )


def _get_auth_config(env_context: env.Context) -> AuthConfig:
    return AuthConfig(
        tokens_file_path=(
                paths.find_backend()
                / _get_auth_dotenv_var_value(
                    "TOKEN_FILE",
                    context=env_context
                )
        )
    )


def _get_mongo_dotenv_var_value(
        name: str,
        context: env.Context | None = None,
) -> str:
    return _get_dotenv_var_value(
        name,
        category="MONGO",
        context=context
    )


def _get_auth_dotenv_var_value(
        name: str,
        context: env.Context | None = None,
) -> str:
    return _get_dotenv_var_value(
        name,
        category="AUTH",
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
