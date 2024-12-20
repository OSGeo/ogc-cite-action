import datetime as dt
import dataclasses


@dataclasses.dataclass(frozen=True)
class TestCaseResult:
    name: str
    description: str
    passed: bool
    parameters: list[str] = dataclasses.field(default_factory=list)
    output: str | None = None
    exception: str | None = None


@dataclasses.dataclass(frozen=True)
class TestCaseCategoryResults:
    name: str
    test_cases: list[TestCaseResult]

    @property
    def passed(self) -> bool:
        return len(self.failed_test_cases) == 0

    @property
    def failed_test_cases(self) -> list[TestCaseResult]:
        return [tc for tc in self.test_cases if not tc.passed]

    @property
    def successful_test_cases(self) -> list[TestCaseResult]:
        return [tc for tc in self.test_cases if tc.passed]


@dataclasses.dataclass(frozen=True)
class ConformanceClassResults:
    name: str
    categories: list[TestCaseCategoryResults]

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
    conformance_classes: list[ConformanceClassResults]

    @property
    def passed(self) -> bool:
        return len(self.failed_conformance_classes) == 0

    @property
    def failed_conformance_classes(self) -> list[ConformanceClassResults]:
        return [cc for cc in self.conformance_classes if not cc.passed]

    @property
    def successful_conformance_classes(self) -> list[ConformanceClassResults]:
        return [cc for cc in self.conformance_classes if cc.passed]
