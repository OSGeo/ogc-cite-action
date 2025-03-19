from pathlib import Path

import pytest
from lxml import etree


@pytest.fixture
def ogcapi_features_1_0_earl_response() -> str:
    response_path = (
            Path(__file__).parent / "data/raw-result-ogcapi-features-1.0-earl.xml"
    )
    return response_path.read_text()


@pytest.fixture
def ogcapi_features_1_0_response_element(
        ogcapi_features_1_0_earl_response
) -> str:
    return etree.fromstring(ogcapi_features_1_0_earl_response.encode("utf-8"))


@pytest.fixture
def ogcapi_processes_1_0_earl_response() -> str:
    response_path = (
            Path(__file__).parent / "data/raw-result-ogcapi-processes-1.0-earl.xml"
    )
    return response_path.read_text()


@pytest.fixture
def ogcapi_processes_1_0_response_element(
        ogcapi_processes_1_0_earl_response
) -> str:
    return etree.fromstring(ogcapi_processes_1_0_earl_response.encode("utf-8"))
