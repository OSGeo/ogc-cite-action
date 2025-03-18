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


class TeamEngineRunnerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="TEAMENGINE_RUNNER__",
        env_nested_delimiter="__"
    )
    default_json_serializer: str = "ogc_cite_action.serializers.simple.to_json"
    default_markdown_serializer: str = "ogc_cite_action.serializers.simple.to_markdown"
    default_parser: str = "ogc_cite_action.parsers.simple.parse_test_suite_result"
    extra_templates_path: str | None = None

    # ogcapi_features_1_0_parser: str = (
    #     "ogc_cite_action.teamengine_runner.parse_test_suite_result")
    # ogcapi_features_1_0_markdown_serializer: str = (
    #     "ogc_cite_action.teamengine_runner.serialize_test_suite_result")
    simple_serializer_template: str = "results-overview.md"


class CliContext(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True
    )

    debug: bool = False
    jinja_environment: jinja2.Environment = jinja2.Environment()
    network_timeout_seconds: int = 20
    settings: TeamEngineRunnerSettings


def get_settings() -> TeamEngineRunnerSettings:
    return TeamEngineRunnerSettings()


def get_context(
        debug: bool,
        network_timeout_seconds: int
) -> CliContext:
    settings = get_settings()
    return CliContext(
        debug=debug,
        network_timeout_seconds=network_timeout_seconds,
        jinja_environment=_get_jinja_environment(settings),
        settings=settings,
    )


def _get_jinja_environment(settings: TeamEngineRunnerSettings) -> jinja2.Environment:
    loaders = [
        jinja2.PackageLoader("ogc_cite_action", "templates"),
    ]
    if settings.extra_templates_path is not None:
        loaders.append(jinja2.FileSystemLoader(settings.extra_templates_path))
    env = jinja2.Environment(
        loader=jinja2.ChoiceLoader(loaders),
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
