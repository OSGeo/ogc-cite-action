"""Parse test results."""
import datetime as dt
import dataclasses
import logging
import typing
import time
from xml.etree import ElementTree as ET

import httpx
import jinja2

from . import schemas
from .schemas import TestSuiteResults

logger = logging.getLogger(__name__)


def wait_for_teamengine_to_be_ready(
    client: httpx.Client,
    teamengine_base_url: str,
    num_attempts: int = 10,
    wait_seconds: int = 10,
) -> bool:
    current_attempt = 1
    result = False
    while current_attempt <= num_attempts:
        response = client.get(f"{teamengine_base_url}/")
        if response.status_code == 200:
            result = True
            break
        else:
            logger.debug(
                f"teamengine is not ready yet."
            )
            if current_attempt == num_attempts:
                logger.error(f"teamengine did not become ready - aborting")
                break
            else:
                logger.debug(f"waiting {wait_seconds}s before trying again...")
                current_attempt += 1
                time.sleep(wait_seconds)
    return result


def execute_test_suite(
    client: httpx.Client,
    teamengine_base_url: str,
    test_suite_identifier: str,
    *,
    test_suite_arguments: typing.Optional[dict[str, str]] = None,
    teamengine_username: str,
    teamengine_password: str,
) -> typing.Optional[str]:
    response = client.get(
        f"{teamengine_base_url}/rest/suites/{test_suite_identifier}/run",
        params=test_suite_arguments,
        auth=(teamengine_username, teamengine_password),
        headers={
            "Accept": "application/xml",
        }
    )
    try:
        response.raise_for_status()
    except httpx.HTTPError:
        logger.exception(msg="Could not execute test suite")
        logger.debug(response.content)
    else:
        return response.text


def parse_test_results(raw_results: str) -> schemas.TestSuiteResults:
    root = ET.fromstring(raw_results)
    suite_el = root.find("./suite")
    return TestSuiteResults(
        suite_name=suite_el.attrib["name"],
        test_run_duration_ms=int(suite_el.attrib["duration-ms"]),
        test_run_start=_parse_to_datetime(suite_el.attrib["started-at"]),
        test_run_end=_parse_to_datetime(suite_el.attrib["finished-at"]),
        num_tests=int(root.attrib.get("total", 0)),
        num_failed=int(root.attrib.get("failed", 0)),
        num_skipped=int(root.attrib.get("skipped", 0)),
        num_passed=int(root.attrib.get("passed", 0)),
    )


def serialize_results_to_markdown(
        results: schemas.TestSuiteResults,
        jinja_environment: jinja2.Environment
) -> str:
    template = jinja_environment.get_template("results-overview.md")
    return template.render(**dataclasses.asdict(results))


def _parse_to_datetime(temporal_value: str) -> dt.datetime:
    return dt.datetime.fromisoformat(
        temporal_value.strip("Z")).replace(tzinfo=dt.timezone.utc)
