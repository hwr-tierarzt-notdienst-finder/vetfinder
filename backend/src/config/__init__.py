from dotenv import dotenv_values

from ..types import EnvContext
from ._schema import *


_config: Config | None = None
def get_config() -> Config:
    global _config

    if _config is None:
        _config = _extract_config()

    return _config


def _extract_config() -> Config:
    return Config(
        dbs=DbConfigs(
            dev=DbConfig(
                port=_extract_mongo_dotenv_var_value(
                    "HOST_PORT",
                    context="dev"
                ),
                container_name=_extract_mongo_dotenv_var_value(
                    "CONTAINER_BASE_NAME",
                ) + "_dev",
                root_user_name=_extract_mongo_dotenv_var_value(
                    "INITDB_ROOT_USERNAME",
                    context="dev",
                ),
                root_password=_extract_mongo_dotenv_var_value(
                    "INITDB_ROOT_PASSWORD",
                    context="dev",
                )
            )
        )
    )


def _extract_mongo_dotenv_var_value(
        name: str,
        context: EnvContext | None = None,
) -> str:
    return _extract_dotenv_var_value(
        name,
        category="MONGO",
        context=context
    )


_dotenv_vars: dict | None = None
def _extract_dotenv_var_value(
        name: str,
        *,
        category: str | None = None,
        context: EnvContext | None = None,
) -> str:
    global _dotenv_vars

    if category is None:
        env_var_name_start = ""
    else:
        env_var_name_start = f"{category}_"

    if context is None:
        env_var_name_middle = ""
    else:
        env_var_name_middle = f"{context.upper()}_"

    env_var_name = f"{env_var_name_start}{env_var_name_middle}{name}"

    if _dotenv_vars is None:
        _dotenv_vars = {
            **dotenv_values(".env"),
            **dotenv_values(".env.local")
        }

    return _dotenv_vars[env_var_name]
