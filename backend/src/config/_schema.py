from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    dbs: "DbConfigs"


@dataclass(frozen=True)
class DbConfigs:
    dev: "DbConfig"

    @property
    def prod(self) -> "DbConfig":
        raise NotImplementedError

    @property
    def test(self) -> "DbConfig":
        raise NotImplementedError


@dataclass(frozen=True)
class DbConfig:
    port: str
    container_name: str
    root_user_name: str
    root_password: str
