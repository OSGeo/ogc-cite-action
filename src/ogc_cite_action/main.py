"""Run teamengine and parse results."""

import logging
import typing

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
from .schemas import OutputFormat

logger = logging.getLogger(__name__)
app = typer.Typer()


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
    logging.getLogger("httpx").setLevel(logging.DEBUG if debug else logging.WARNING)
    ctx_obj = ctx.ensure_object(dict)
    ctx_obj.update({
        "debug": debug,
        "jinja_environment": config.get_jinja_environment(),
        "network_timeout": network_timeout,
    })
    ctx_obj["debug"] = debug


@app.command("execute-test-suite")
def execute_test_suite_from_github_actions(
        ctx: typer.Context,
        teamengine_base_url: str,
        test_suite_identifier: str,
        test_suite_input: list[str],
        teamengine_username: str = "ogctest",
        teamengine_password: str = "ogctest",
        output_format: OutputFormat = OutputFormat.MARKDOWN,
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
    teamengine_base_url: str,
    test_suite_identifier: str,
    teamengine_username: str = "ogctest",
    teamengine_password: str = "ogctest",
    test_suite_input: typing.Annotated[
        typing.Optional[list[click.Tuple]],
        typer.Option(click_type=click.Tuple([str, str]))
    ] = None,
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
            teamengine_username=teamengine_username,
            teamengine_password=teamengine_password,
        )
        if raw_result:
            if output_format == OutputFormat.RAW_XML:
                logger.debug(
                    f"Outputting XML response, as returned by teamengine...")
                print(raw_result)
            else:
                logger.debug(f"Parsing test suite execution results...")
                suite_execution_result = teamengine_runner.parse_test_results(
                    raw_result)
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


