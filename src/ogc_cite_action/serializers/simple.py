import jinja2

from .. import models
from ..config import TeamEngineRunnerSettings


def to_markdown(
        parsed_result: models.TestSuiteResult,
        settings: TeamEngineRunnerSettings,
        jinja_environment: jinja2.Environment,
) -> str:
    """Serialize parsed test suite results to markdown"""
    template = jinja_environment.get_template(
        settings.simple_serializer_template
    )
    return template.render(result=parsed_result)


def to_json(
        parsed_result: models.TestSuiteResult,
        settings: TeamEngineRunnerSettings,
        jinja_environment: jinja2.Environment,
) -> str:
    output_result = models.TestSuiteResultOut(**parsed_result.model_dump())
    return output_result.model_dump_json(indent=2)
