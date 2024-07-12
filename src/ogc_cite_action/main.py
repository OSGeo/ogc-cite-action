"""Run teamengine and parse results."""

import logging
import typing
from pathlib import Path

import click
import httpx
import typer
from rich import print
from rich import print_json

from . import teamengine_runner

logger = logging.getLogger(__name__)
app = typer.Typer()


@app.callback()
def base_callback(
    ctx: typer.Context,
    debug: bool = False,
    network_timeout: int = 20
) -> None:
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)
    ctx_obj = ctx.ensure_object(dict)
    ctx_obj.update({
        "debug": debug,
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
    persist_response: typing.Optional[Path] = None
):
    logger.debug(f"{locals()=}")
    client = httpx.Client(timeout=ctx.obj["network_timeout"])
    suite_args = {}
    for arg_name, arg_value in (test_suite_input or []):
        values = suite_args.setdefault(arg_name, [])
        values.append(arg_value)
    raw_result = teamengine_runner.execute_test_suite(
        client,
        teamengine_base_url.strip("/"),
        test_suite_identifier,
        test_suite_arguments=suite_args,
        teamengine_username="ogctest",
        teamengine_password="ogctest",
    )
    if raw_result:
        if persist_response is not None:
            persist_response.write_text(raw_result)
            logger.debug(f"Wrote raw response to {persist_response!r}")
        test_summary = teamengine_runner.parse_test_results(raw_result)
        print_json(data=test_summary)
    else:
        raise SystemExit(1)


