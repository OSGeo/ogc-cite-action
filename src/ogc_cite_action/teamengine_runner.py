"""Utilities for running a remote TEAMENGINE instance and getting its result."""
import datetime as dt
import logging
import typing
import time
from itertools import count
from lxml import etree

import httpx
import jinja2
import pydantic

from . import (
    config,
    exceptions,
    models,
)

logger = logging.getLogger(__name__)


class SuiteParserProtocol(typing.Protocol):

    def __call__(
        self,
        suite_result: etree.Element,
        treat_skipped_as_failure: bool
    ) -> models.TestSuiteResult:
        ...



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
    test_suite_arguments: typing.Optional[dict[str, list[str]]] = None,
    teamengine_username: pydantic.SecretStr | None = None,
    teamengine_password: pydantic.SecretStr | None = None,
) -> typing.Optional[str]:
    request_auth = (
        teamengine_username.get_secret_value(),
        teamengine_password.get_secret_value()
    ) if teamengine_username is not None else None
    response = client.get(
        f"{teamengine_base_url}/rest/suites/{test_suite_identifier}/run",
        params=test_suite_arguments,
        auth=request_auth,
        headers={
            "Accept": "application/xml",
        }
    )
    try:
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise exceptions.OgcCiteActionException("Could not execute test suite") from exc
    else:
        return response.text


def get_suite_result_parser(
        test_suite_identifier: str,
        settings: config.TeamEngineRunnerConfig
) -> SuiteParserProtocol:
    parser = {
    }.get(test_suite_identifier, parse_test_suite_result)
    return parser


def parse_raw_result_as_xml(
        raw_result: str
) -> etree.Element:
    parser = etree.XMLParser(
        resolve_entities=False,
    )
    try:
        return etree.fromstring(raw_result.encode(), parser)
    except etree.ParseError as exc:
        raise exceptions.OgcCiteActionException(
            "Unable to parse test suite execution result as XML") from exc


def get_suite_name(
        result_root: etree.Element,
) -> str:
    suite_el = result_root.find("./suite")
    return suite_el.attrib.get("name", "")


def parse_test_suite_result(
        suite_result: etree.Element,
        treat_skipped_as_failure: bool,
) -> models.TestSuiteResult:
    suite_el = suite_result.find("./suite")
    now = dt.datetime.now(tz=dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    suite = models.TestSuiteResult(
        suite_name=suite_el.attrib.get("name", ""),
        overview=models.SuiteResultOverview(
            test_run_duration_ms=dt.timedelta(
                microseconds=int(suite_el.attrib.get("duration-ms", 0))
            ),
            num_tests_total=int(suite_result.attrib.get("total", 0)),
            num_failed_tests=int(suite_result.attrib.get("failed", 0)),
            num_skipped_tests=int(suite_result.attrib.get("skipped", 0)),
            num_passed_tests=int(suite_result.attrib.get("passed", 0)),
        ),
        test_run_start=_parse_to_datetime(suite_el.attrib.get("started-at", now)),
        test_run_end=_parse_to_datetime(suite_el.attrib.get("finished-at", now)),
    )
    test_case_names = set()
    for conformance_class_el in suite_el.findall("./test"):
        conformance_class = models.ConformanceClassResults(
            name=conformance_class_el.attrib.get("name", ""),
            suite=suite,
        )
        for category_el in conformance_class_el.findall("./class"):
            cat_name = category_el.attrib.get("name", "")
            category = models.TestCaseCategoryResults(
                name=cat_name,
                short_name=cat_name.partition("conformance.")[-1],
                conformance_class=conformance_class,
                treat_skipped_as_failure=treat_skipped_as_failure,
            )
            for test_case_el in category_el.findall("./test-method"):
                test_case_name = _get_test_case_name(
                    test_case_el.get("name", ""),
                    test_case_names
                )
                logger.debug(f"{test_case_name=}")
                test_case_names.add(test_case_name)
                test_case_status = {
                    "pass": models.TestStatus.PASSED,
                    "skip": models.TestStatus.SKIPPED,
                }.get(
                    test_case_el.get("status", "").lower(),
                    models.TestStatus.FAILED
                )
                error_msg_el = test_case_el.find("./exception/message")
                if test_case_el.attrib.get("is-config") != "true":
                    params = [
                        i.text.strip() for i in test_case_el.findall("./params/param")
                    ]
                    test_case = models.TestCaseResult(
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


def serialize_test_suite_result(
        parsed_result: models.TestSuiteResult,
        output_format: models.ParseableOutputFormat,
        jinja_environment: jinja2.Environment | None = None,
) -> str:
    if output_format == models.ParseableOutputFormat.JSON:
        output_result = models.TestSuiteResultOut(**parsed_result.model_dump())
        rendered = output_result.model_dump_json(indent=2)
    elif output_format == models.ParseableOutputFormat.MARKDOWN:
        template = jinja_environment.get_template("results-overview.md")
        rendered = template.render(result=parsed_result)
    else:
        raise ValueError(f"Output format {output_format} not implemented")
    return rendered


def _parse_to_datetime(temporal_value: str) -> dt.datetime:
    return dt.datetime.fromisoformat(
        temporal_value.strip("Z")).replace(tzinfo=dt.timezone.utc)


def _get_test_case_name(naive_name: str, seen_names: set) -> str:
    result = naive_name
    if naive_name in seen_names:
        for idx in count(start=1):
            if idx > 10_000:
                raise RuntimeError(
                    f"Could not find a unique name for test case after {count} tries, "
                    f"aborting..."
                )
            else:
                candidate_name = f"{naive_name}-{idx:03d}"
                if candidate_name not in seen_names:
                    result = candidate_name
                    break
    return result
