import datetime as dt
import dataclasses
import enum
from typing import Generator


class OutputFormat(str, enum.Enum):
    JSON = "json"
    MARKDOWN = "markdown"
    RAW_XML = "raw-xml"


class TestStatus(enum.Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


@dataclasses.dataclass(frozen=True)
class TestCaseResult:
    name: str
    description: str
    status: TestStatus
    category: "TestCaseCategoryResults"
    parameters: list[str] = dataclasses.field(default_factory=list)
    output: str | None = None
    exception: str | None = None


@dataclasses.dataclass(frozen=True)
class TestCaseCategoryResults:
    name: str
    conformance_class: "ConformanceClassResults"
    test_cases: list[TestCaseResult] = dataclasses.field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.failed_test_cases + self.skipped_test_cases) == 0

    @property
    def failed_test_cases(self) -> list[TestCaseResult]:
        return [tc for tc in self.test_cases if tc.status == TestStatus.FAILED]

    @property
    def skipped_test_cases(self) -> list[TestCaseResult]:
        return [tc for tc in self.test_cases if tc.status == TestStatus.SKIPPED]

    @property
    def successful_test_cases(self) -> list[TestCaseResult]:
        return [tc for tc in self.test_cases if tc.status == TestStatus.PASSED]


@dataclasses.dataclass(frozen=True)
class ConformanceClassResults:
    name: str
    suite: "TestSuiteResult"
    categories: list[TestCaseCategoryResults] = dataclasses.field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.failed_categories) == 0

    @property
    def failed_categories(self) -> list[TestCaseCategoryResults]:
        return [cat for cat in self.categories if not cat.passed]

    @property
    def successful_categories(self) -> list[TestCaseCategoryResults]:
        return [cat for cat in self.categories if cat.passed]


@dataclasses.dataclass(frozen=True)
class SuiteResultOverview:
    test_run_duration_ms: dt.timedelta
    num_tests_total: int
    num_failed_tests: int
    num_skipped_tests: int
    num_passed_tests: int


@dataclasses.dataclass(frozen=True)
class TestSuiteResult:
    suite_name: str
    test_run_start: dt.datetime
    test_run_end: dt.datetime
    overview: SuiteResultOverview
    conformance_classes: list[ConformanceClassResults] = dataclasses.field(
        default_factory=list)

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
