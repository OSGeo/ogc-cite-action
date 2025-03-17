import logging

import jinja2
import pydantic
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)
from rich.console import Console
from rich.logging import RichHandler

from . import models


class TeamEngineRunnerConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="TEAMENGINE_RUNNER__",
        env_nested_delimiter="__"
    )

    ogcapi_features_1_0_parser: str = (
        "teamengine_runner.parse_test_suite_result")


class CliContext(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True
    )

    debug: bool = False
    jinja_environment: jinja2.Environment = jinja2.Environment()
    network_timeout_seconds: int = 20
    settings: TeamEngineRunnerConfig


def get_settings() -> TeamEngineRunnerConfig:
    return TeamEngineRunnerConfig()


def get_context(
        debug: bool,
        network_timeout_seconds: int
) -> CliContext:
    return CliContext(
        debug=debug,
        network_timeout_seconds=network_timeout_seconds,
        jinja_environment=_get_jinja_environment(),
        settings=get_settings(),
    )


def _get_jinja_environment() -> jinja2.Environment:
    env = jinja2.Environment(
        loader=jinja2.PackageLoader(
            "ogc_cite_action",
            "templates"
        ),
        extensions=[
            "jinja2_humanize_extension.HumanizeExtension",
        ],
    )
    env.globals.update({
        "TestStatus": models.TestStatus,
    })
    return env


def configure_logging(
        debug: bool
) -> None:
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        handlers=[
            RichHandler(
                console=Console(stderr=True),
                rich_tracebacks=True
            )
        ],
    )
    logging.getLogger("httpcore").setLevel(logging.INFO if debug else logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.INFO if debug else logging.WARNING)
