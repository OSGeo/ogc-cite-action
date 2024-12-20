"""Run teamengine and parse results."""

import enum
import logging
import typing
from pathlib import Path

import click
import httpx
import typer
from rich import (
    print,
    print_json,
)
from rich.logging import RichHandler

from . import (
    config,
    teamengine_runner,
)

logger = logging.getLogger(__name__)
app = typer.Typer()


class OutputFormat(str, enum.Enum):
    JSON = "json"
    MARKDOWN = "markdown"


@app.callback()
def base_callback(
    ctx: typer.Context,
    debug: bool = False,
    network_timeout: int = 20
) -> None:
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        handlers=[RichHandler()],
    )
    ctx_obj = ctx.ensure_object(dict)
    ctx_obj.update({
        "debug": debug,
        "jinja_environment": config.get_jinja_environment(),
        "network_timeout": network_timeout,
    })
    ctx_obj["debug"] = debug


@app.command()
def execute_test_suite(
    ctx: typer.Context,
    teamengine_base_url: str,
    test_suite_identifier: str,
    test_suite_input: typing.Annotated[
        typing.Optional[list[click.Tuple]],
        typer.Option(click_type=click.Tuple([str, str]))
    ] = None,
    persist_response: typing.Optional[Path] = None,
    output_format: OutputFormat = OutputFormat.MARKDOWN,
):
    """Execute a CITE test suite."""
    logger.debug(f"{locals()=}")
    client = httpx.Client(timeout=ctx.obj["network_timeout"])
    base_url = teamengine_base_url.strip("/")
    teamengine_available = teamengine_runner.wait_for_teamengine_to_be_ready(
        client, base_url)
    if teamengine_available:
        suite_args = {}
        for arg_name, arg_value in (test_suite_input or []):
            values = suite_args.setdefault(arg_name, [])
            values.append(arg_value)
        logger.debug(
            f"Asking teamengine to execute test suite {test_suite_identifier!r}...")
        raw_result = teamengine_runner.execute_test_suite(
            client,
            base_url,
            test_suite_identifier,
            test_suite_arguments=suite_args,
            teamengine_username="ogctest",
            teamengine_password="ogctest",
        )
        logger.debug(f"Test suite is done executing")
        if raw_result:
            if persist_response is not None:
                output_path = persist_response.resolve()
                try:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                except OSError:
                    logger.exception(
                        f"Failed to create output directory {output_path.parent}")
                else:
                    try:
                        output_path.write_text(raw_result)
                    except PermissionError:
                        logger.exception(f"Failed to create output path {output_path}")
                    else:
                        logger.debug(f"Wrote raw response to {output_path}")
            logger.debug(f"Parsing test suite execution results...")
            suite_execution_result = teamengine_runner.parse_test_results(raw_result)
            if output_format == OutputFormat.JSON:
                print_json(data=suite_execution_result)
            elif output_format == OutputFormat.MARKDOWN:
                serialized = teamengine_runner.serialize_results_to_markdown(
                    suite_execution_result, ctx.obj["jinja_environment"])
                print(serialized)
            else:
                logger.critical(f"Output format {output_format} not implemented")
                raise SystemExit(1)
        else:
            logger.critical(f"Unable to collect test suite execution results")
            raise SystemExit(1)
    else:
        logger.critical(f"teamengine service is not available")
        raise SystemExit(1)


