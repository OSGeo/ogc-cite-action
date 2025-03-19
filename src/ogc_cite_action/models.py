import datetime as dt
import enum
from typing import (
    Annotated,
    Generator,
)

import pydantic


class OutputFormat(str, enum.Enum):
    JSON = "json"
    MARKDOWN = "markdown"
    RAW= "raw"


class ParseableOutputFormat(str, enum.Enum):
    JSON = "json"
    MARKDOWN = "markdown"


class TestStatus(enum.Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class TestSuiteInput(pydantic.BaseModel):
    name: str
    value: str


class TestCaseResult(pydantic.BaseModel):
    identifier: str
    status: TestStatus
    detail: str | None
    name: str | None
    description: str | None


class ConformanceClassResult(pydantic.BaseModel):
    title: str
    description: str
    num_failed_tests: int
    num_passed_tests: int
    num_skipped_tests: int
    tests: list[TestCaseResult]

    def gen_failed_tests(self) -> Generator[TestCaseResult, None, None]:
        for test_case in self.tests:
            if test_case.status == TestStatus.FAILED:
                yield test_case

    def gen_skipped_tests(self) -> Generator[TestCaseResult, None, None]:
        for test_case in self.tests:
            if test_case.status == TestStatus.SKIPPED:
                yield test_case

    def gen_passed_tests(self) -> Generator[TestCaseResult, None, None]:
        for test_case in self.tests:
            if test_case.status == TestStatus.PASSED:
                yield test_case


class TestSuiteResult(pydantic.BaseModel):
    suite_identifier: str
    suite_title: str
    test_run_start: dt.datetime
    test_run_end: dt.datetime
    test_run_duration: dt.timedelta
    num_tests_total: int
    num_failed_tests: int
    num_skipped_tests: int
    num_passed_tests: int
    inputs: list[TestSuiteInput]
    conformance_class_results: list[ConformanceClassResult]
    passed: bool


class OldTestCaseResult(pydantic.BaseModel):
    name: str
    description: str
    status: TestStatus
    category: "TestCaseCategoryResults"
    parameters: Annotated[
        list[str],
        pydantic.Field(default_factory=list),
    ]
    output: str | None = None
    exception: str | None = None

    @pydantic.field_serializer("category")
    def serialize_category(self, category: "TestCaseCategoryResults") -> str:
        return category.name


class OldTestCaseCategoryResults(pydantic.BaseModel):
    name: str
    short_name: str
    conformance_class: "OldConformanceClassResults"
    test_cases: Annotated[
        list[OldTestCaseResult],
        pydantic.Field(default_factory=list),
    ]
    treat_skipped_as_failure: bool = False

    @pydantic.field_serializer("conformance_class")
    def serialize_conformance_class(
            self, conformance_class: "OldConformanceClassResults") -> str:
        return conformance_class.name

    @property
    def passed(self) -> bool:
        result = len(self.failed_test_cases) == 0
        if self.treat_skipped_as_failure:
            result = result and len(self.skipped_test_cases) == 0
        return result

    @property
    def failed_test_cases(self) -> list[OldTestCaseResult]:
        return [tc for tc in self.test_cases if tc.status == TestStatus.FAILED]

    @property
    def skipped_test_cases(self) -> list[OldTestCaseResult]:
        return [tc for tc in self.test_cases if tc.status == TestStatus.SKIPPED]

    @property
    def successful_test_cases(self) -> list[OldTestCaseResult]:
        return [tc for tc in self.test_cases if tc.status == TestStatus.PASSED]


class OldConformanceClassResults(pydantic.BaseModel):
    name: str
    suite: "OldTestSuiteResult"
    categories: Annotated[
        list[OldTestCaseCategoryResults],
        pydantic.Field(default_factory=list)
    ]
    treat_skipped_as_failure: bool = False

    @pydantic.field_serializer("suite")
    def serialize_suite(
            self, suite: "OldTestSuiteResult") -> str:
        return suite.suite_name

    @property
    def passed(self) -> bool:
        return len(self.failed_categories) == 0

    @property
    def failed_categories(self) -> list[OldTestCaseCategoryResults]:
        return [cat for cat in self.categories if not cat.passed]

    @property
    def successful_categories(self) -> list[OldTestCaseCategoryResults]:
        return [cat for cat in self.categories if cat.passed]


class OldSuiteResultOverview(pydantic.BaseModel):
    test_run_duration_ms: dt.timedelta
    num_tests_total: int
    num_failed_tests: int
    num_skipped_tests: int
    num_passed_tests: int


class OldTestSuiteResult(pydantic.BaseModel):
    suite_name: str
    test_run_start: dt.datetime
    test_run_end: dt.datetime
    overview: OldSuiteResultOverview
    conformance_classes: Annotated[
        list[OldConformanceClassResults],
        pydantic.Field(default_factory=list)
    ]

    @property
    def passed(self) -> bool:
        return len(self.failed_conformance_classes) == 0

    @property
    def failed_conformance_classes(self) -> list[OldConformanceClassResults]:
        return [cc for cc in self.conformance_classes if not cc.passed]

    @property
    def successful_conformance_classes(self) -> list[OldConformanceClassResults]:
        return [cc for cc in self.conformance_classes if cc.passed]

    def gen_test_cases(self) -> Generator[OldTestCaseResult, None, None]:
        for conformance_class in self.conformance_classes:
            for category in conformance_class.categories:
                for test_case in category.test_cases:
                    yield test_case

    def gen_failed_test_cases(self) -> Generator[OldTestCaseResult, None, None]:
        for test_case in self.gen_test_cases():
            if test_case.status == TestStatus.FAILED:
                yield test_case

    def gen_skipped_test_cases(self) -> Generator[OldTestCaseResult, None, None]:
        for test_case in self.gen_test_cases():
            if test_case.status == TestStatus.SKIPPED:
                yield test_case
