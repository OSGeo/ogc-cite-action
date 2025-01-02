import jinja2
import logging

from rich.console import Console
from rich.logging import RichHandler

from . import models


def get_context(
        debug: bool,
        network_timeout_seconds: int
) -> models.CliContext:
    return models.CliContext(
        debug=debug,
        network_timeout_seconds=network_timeout_seconds,
        jinja_environment=_get_jinja_environment(),
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
    logging.getLogger("httpx").setLevel(logging.DEBUG if debug else logging.WARNING)