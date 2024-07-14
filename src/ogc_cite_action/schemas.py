import datetime as dt
import dataclasses


@dataclasses.dataclass(frozen=True)
class TestSuiteResults:
    suite_name: str
    test_run_duration_ms: int
    test_run_start: dt.datetime
    test_run_end: dt.datetime
    num_tests: int
    num_failed: int
    num_skipped: int
    num_passed: int
