"""Parse test results."""

import os
from pathlib import Path
from xml.etree import ElementTree as ET


def parse_results(results: ET.Element) -> dict:
    raise NotImplementedError


if __name__ == "__main__":
    results_path = Path(os.getenv("INPUT_TEST_RESULT_FILE"))
    if results_path.exists():
        try:
            results = ET.fromstring(results_path.read_text())
        except ET.ParseError:
            raise RuntimeError("Could not parse test results")
        else:
            parsed = parse_results(results)
    else:
        raise RuntimeError("Test results file not found")
