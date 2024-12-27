"""Run teamengine and parse results."""

from builtins import print as stdlib_print
import logging
import typing
from pathlib import Path
from xml.etree import ElementTree as ET

import click
import httpx
import jinja2
import pydantic
import typer
from rich import print
from rich.console import Console
from rich.logging import RichHandler

from . import (
    config,
    exceptions,
    models,
    teamengine_runner,
)

logger = logging.getLogger(__name__)
app = typer.Typer()


def _parse_pydantic_secret_str(value: str) -> pydantic.SecretStr:
    return pydantic.SecretStr(value)


_test_suite_identifier_argument = typing.Annotated[
    str,
    typer.Argument(help="Identifier of the test suite. Ex: ogcapi-features-1.0")
]
_teamengine_base_url_argument = typing.Annotated[
    str,
    typer.Argument(
        help="Base URL of teamengine service. Ex: http://localhost:8080/teamengine"
    )
]
_teamengine_username_option = typing.Annotated[
    pydantic.SecretStr,
    typer.Option(
        help="Username for authenticating with teamengine",
        parser=_parse_pydantic_secret_str,
    )
]
_teamengine_password_option = typing.Annotated[
    pydantic.SecretStr,
    typer.Option(
        help="Password for authenticating with teamengine",
        parser=_parse_pydantic_secret_str,
    )
]


@app.callback()
def base_callback(
    ctx: typer.Context,
    debug: bool = False,
    network_timeout: int = 20
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
    ctx_obj = ctx.ensure_object(dict)
    ctx_obj.update({
        "debug": debug,
        "jinja_environment": config.get_jinja_environment(),
        "network_timeout": network_timeout,
    })
    ctx_obj["debug"] = debug


@app.command("parse-result")
def parse_test_result(
        ctx: typer.Context,
        test_suite_result: typing.Annotated[
            Path,
            typer.Argument(
                exists=True,
                file_okay=True,
                dir_okay=False,
            )
        ],
        output_format: models.ParseableOutputFormat = models.ParseableOutputFormat.JSON,
):
    raw_result = test_suite_result.read_text()
    _parse_result(raw_result, output_format, ctx.obj["jinja_environment"])


@app.command("execute-test-suite")
def execute_test_suite_from_github_actions(
    ctx: typer.Context,
    teamengine_base_url: _teamengine_base_url_argument,
    test_suite_identifier: _test_suite_identifier_argument,
    test_suite_input: typing.Annotated[
        list[str],
        typer.Argument(
            help=(
                "Space-separated list of inputs to be passed to teamengine. Each "
                "input must be formatted as key=value. Ex: "
                "iut=http://localhost:5000 noofcollections=-1"
            )
        )
    ],
    teamengine_username: _teamengine_username_option = pydantic.SecretStr("ogctest"),
    teamengine_password: _teamengine_password_option = pydantic.SecretStr("ogctest"),
    output_format: models.OutputFormat = models.OutputFormat.MARKDOWN,
):
    """Execute a CITE test suite via github actions.

    This command presents a simpler interface to run the
    `execute-test-suite-standalone`, making it easier to run as a github
    action.
    """
    inputs = {}
    for raw_suite_input in test_suite_input:
        param_name, param_value = raw_suite_input.partition("=")[::2]
        inputs[param_name] = param_value
    logger.debug(f"{inputs=}")
    ctx.invoke(
        execute_test_suite_standalone,
        ctx=ctx,
        teamengine_base_url=teamengine_base_url,
        test_suite_identifier=test_suite_identifier,
        teamengine_username=teamengine_username,
        teamengine_password=teamengine_password,
        test_suite_input=[(k, v) for k, v in inputs.items()],
        output_format=output_format,
    )


@app.command()
def execute_test_suite_standalone(
    ctx: typer.Context,
    teamengine_base_url: _teamengine_base_url_argument,
    test_suite_identifier: _test_suite_identifier_argument,
    teamengine_username: _teamengine_username_option = pydantic.SecretStr("ogctest"),
    teamengine_password: _teamengine_password_option = pydantic.SecretStr("ogctest"),
    test_suite_input: typing.Annotated[
        typing.Optional[list[click.Tuple]],
        typer.Option(click_type=click.Tuple([str, str]))
    ] = None,
    output_format: models.OutputFormat = models.OutputFormat.MARKDOWN,
):
    """Execute a CITE test suite."""
    logger.debug(f"{locals()=}")
    client = httpx.Client(timeout=ctx.obj["network_timeout"])
    base_url = teamengine_base_url.strip("/")
    if teamengine_runner.wait_for_teamengine_to_be_ready(client, base_url):
        suite_args = {}
        for arg_name, arg_value in (test_suite_input or []):
            values = suite_args.setdefault(arg_name, [])
            values.append(arg_value)
        logger.debug(
            f"Asking teamengine to execute test suite {test_suite_identifier!r}...")
        try:
            raw_result = teamengine_runner.execute_test_suite(
                client,
                base_url,
                test_suite_identifier,
                test_suite_arguments=suite_args,
                teamengine_username=teamengine_username,
                teamengine_password=teamengine_password,
            )
        except exceptions.OgcCiteActionException:
            logger.exception(f"Unable to collect test suite execution results")
            raise SystemExit(1)
        else:
            if output_format == models.OutputFormat.RAW:
                logger.debug(
                    f"Outputting raw response, as returned by teamengine...")
                stdlib_print(raw_result)
            else:
                logger.debug(f"Parsing test suite execution results...")
                _parse_result(
                    raw_result,
                    models.ParseableOutputFormat(output_format.value),
                    ctx.obj["jinja_environment"]
                )
    else:
        logger.critical(f"teamengine service is not available")
        raise SystemExit(1)


def _parse_result(
        raw_result: str,
        output_format: models.ParseableOutputFormat,
        jinja_env: jinja2.Environment
):
    try:
        root = ET.fromstring(raw_result)
        parsed = teamengine_runner.parse_test_suite_result(root)
        parseable_output_format = models.ParseableOutputFormat(
            output_format.value)
        rendered = teamengine_runner.serialize_test_suite_result(
            parsed,
            parseable_output_format,
            jinja_environment=jinja_env
        )
    except ET.ParseError:
        logger.exception(f"Unable to parse test suite execution result as XML")
        raise SystemExit(1)
    except ValueError as exc:
        logger.exception(msg="Found an error")
        raise SystemExit(1) from exc
    else:
        print(rendered)
