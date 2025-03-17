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


class TestCaseResult(pydantic.BaseModel):
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


class TestCaseCategoryResults(pydantic.BaseModel):
    name: str
    short_name: str
    conformance_class: "ConformanceClassResults"
    test_cases: Annotated[
        list[TestCaseResult],
        pydantic.Field(default_factory=list),
    ]
    treat_skipped_as_failure: bool = False

    @pydantic.field_serializer("conformance_class")
    def serialize_conformance_class(
            self, conformance_class: "ConformanceClassResults") -> str:
        return conformance_class.name

    @property
    def passed(self) -> bool:
        result = len(self.failed_test_cases) == 0
        if self.treat_skipped_as_failure:
            result = result and len(self.skipped_test_cases) == 0
        return result

    @property
    def failed_test_cases(self) -> list[TestCaseResult]:
        return [tc for tc in self.test_cases if tc.status == TestStatus.FAILED]

    @property
    def skipped_test_cases(self) -> list[TestCaseResult]:
        return [tc for tc in self.test_cases if tc.status == TestStatus.SKIPPED]

    @property
    def successful_test_cases(self) -> list[TestCaseResult]:
        return [tc for tc in self.test_cases if tc.status == TestStatus.PASSED]


class ConformanceClassResults(pydantic.BaseModel):
    name: str
    suite: "TestSuiteResult"
    categories: Annotated[
        list[TestCaseCategoryResults],
        pydantic.Field(default_factory=list)
    ]
    treat_skipped_as_failure: bool = False

    @pydantic.field_serializer("suite")
    def serialize_suite(
            self, suite: "TestSuiteResult") -> str:
        return suite.suite_name

    @property
    def passed(self) -> bool:
        return len(self.failed_categories) == 0

    @property
    def failed_categories(self) -> list[TestCaseCategoryResults]:
        return [cat for cat in self.categories if not cat.passed]

    @property
    def successful_categories(self) -> list[TestCaseCategoryResults]:
        return [cat for cat in self.categories if cat.passed]


class SuiteResultOverview(pydantic.BaseModel):
    test_run_duration_ms: dt.timedelta
    num_tests_total: int
    num_failed_tests: int
    num_skipped_tests: int
    num_passed_tests: int


class TestSuiteResult(pydantic.BaseModel):
    suite_name: str
    test_run_start: dt.datetime
    test_run_end: dt.datetime
    overview: SuiteResultOverview
    conformance_classes: Annotated[
        list[ConformanceClassResults],
        pydantic.Field(default_factory=list)
    ]
    conformance_classes: Annotated[
        list[ConformanceClassResults],
        pydantic.Field(default_factory=list)
    ]

    @property
    def passed(self) -> bool:
        return len(self.failed_conformance_classes) == 0

    @property
    def failed_conformance_classes(self) -> list[ConformanceClassResults]:
        return [cc for cc in self.conformance_classes if not cc.passed]

    @property
    def successful_conformance_classes(self) -> list[ConformanceClassResults]:
        return [cc for cc in self.conformance_classes if cc.passed]

    def gen_test_cases(self) -> Generator[TestCaseResult, None, None]:
        for conformance_class in self.conformance_classes:
            for category in conformance_class.categories:
                for test_case in category.test_cases:
                    yield test_case

    def gen_failed_test_cases(self) -> Generator[TestCaseResult, None, None]:
        for test_case in self.gen_test_cases():
            if test_case.status == TestStatus.FAILED:
                yield test_case

    def gen_skipped_test_cases(self) -> Generator[TestCaseResult, None, None]:
        for test_case in self.gen_test_cases():
            if test_case.status == TestStatus.SKIPPED:
                yield test_case


class TestCaseResultOut(pydantic.BaseModel):
    name: str
    description: str
    status: TestStatus
    parameters: list[str]
    output: str | None = None
    exception: str | None = None


class TestCaseCategoryResultsOut(pydantic.BaseModel):
    name: str
    test_cases: list[TestCaseResultOut]


class ConformanceClassResultsOut(pydantic.BaseModel):
    name: str
    categories: list[TestCaseCategoryResultsOut]


class SuiteResultOverviewOut(SuiteResultOverview):
    pass


class TestSuiteResultOut(pydantic.BaseModel):
    suite_name: str
    test_run_start: dt.datetime
    test_run_end: dt.datetime
    overview: SuiteResultOverviewOut
    conformance_classes: list[ConformanceClassResultsOut]
