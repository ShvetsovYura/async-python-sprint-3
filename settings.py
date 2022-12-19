from typing import Any

import yaml
from pydantic import BaseSettings


def yaml_config_settings_source(settings: BaseSettings) -> dict[str, Any]:

    with open('app-config.yml', 'r') as stream:
        return yaml.safe_load(stream)


class AppSettings(BaseSettings):
    port: int
    prefix: str
    host: str    # noqa: CCE001

    class Config:
        env_file_encoding = 'utf-8'

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            return (
                init_settings,
                yaml_config_settings_source,
                env_settings,
                file_secret_settings,
            )
