"""Utilities for running a remote TEAMENGINE instance and getting its result."""
import datetime as dt
import logging
import typing
import time
from xml.etree import ElementTree as ET

import httpx
import jinja2

from . import schemas

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


def parse_test_results(raw_results: str) -> schemas.TestSuiteResult:
    root = ET.fromstring(raw_results)
    suite_el = root.find("./suite")
    now = dt.datetime.now(tz=dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    suite = schemas.TestSuiteResult(
        suite_name=suite_el.attrib.get("name", ""),
        overview=schemas.SuiteResultOverview(
            test_run_duration_ms=dt.timedelta(
                microseconds=int(suite_el.attrib.get("duration-ms", 0))
            ),
            num_tests_total=int(root.attrib.get("total", 0)),
            num_failed_tests=int(root.attrib.get("failed", 0)),
            num_skipped_tests=int(root.attrib.get("skipped", 0)),
            num_passed_tests=int(root.attrib.get("passed", 0)),
        ),
        test_run_start=_parse_to_datetime(suite_el.attrib.get("started-at", now)),
        test_run_end=_parse_to_datetime(suite_el.attrib.get("finished-at", now)),
    )
    for conformance_class_el in suite_el.findall("./test"):
        conformance_class = schemas.ConformanceClassResults(
            name=conformance_class_el.attrib.get("name", ""),
            suite=suite,
        )
        for category_el in conformance_class_el.findall("./class"):
            category = schemas.TestCaseCategoryResults(
                name=category_el.attrib.get("name", ""),
                conformance_class=conformance_class,
            )
            for test_case_el in category_el.findall("./test-method"):
                test_case_name = test_case_el.get("name", "")
                test_case_status = {
                    "pass": schemas.TestStatus.PASSED,
                    "skip": schemas.TestStatus.SKIPPED,
                }.get(
                    test_case_el.get("status", "").lower(),
                    schemas.TestStatus.FAILED
                )
                error_msg_el = test_case_el.find("./exception/message")
                if test_case_el.attrib.get("is-config") != "true":
                    params = [
                        i.text.strip() for i in test_case_el.findall("./params/param")
                    ]
                    test_case = schemas.TestCaseResult(
                        name=test_case_name,
                        description=test_case_el.attrib.get("description", ""),
                        status=test_case_status,
                        output=test_case_el.find("./reporter-output").text.strip(),
                        exception=(
                            error_msg_el.text.strip()
                            if error_msg_el is not None else None
                        ),
                        parameters=[p for p in params if p != ""],
                        category=category,
                    )
                    category.test_cases.append(test_case)
                else:
                    logger.debug(
                        f"ignoring test case {test_case_name}"
                        f"(status={test_case_status}) as it seems to be only "
                        f"test configuration"
                    )
            conformance_class.categories.append(category)
        suite.conformance_classes.append(conformance_class)
    return suite


def serialize_results_to_markdown(
        suite_result: schemas.TestSuiteResult,
        jinja_environment: jinja2.Environment
) -> str:
    template = jinja_environment.get_template("results-overview.md")
    return template.render(result=suite_result)


def _parse_to_datetime(temporal_value: str) -> dt.datetime:
    return dt.datetime.fromisoformat(
        temporal_value.strip("Z")).replace(tzinfo=dt.timezone.utc)
