"""Parse test results."""

import logging
import typing
from xml.etree import ElementTree as ET

import httpx

logger = logging.getLogger(__name__)


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


def parse_test_results(raw_results: str) -> dict:
    root = ET.fromstring(raw_results)
    summary = root.attrib
    return summary
