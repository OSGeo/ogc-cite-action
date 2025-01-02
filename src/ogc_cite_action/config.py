import jinja2
import logging

from rich.console import Console
from rich.logging import RichHandler

from .models import TestStatus


def get_jinja_environment() -> jinja2.Environment:
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
        "TestStatus": TestStatus,
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