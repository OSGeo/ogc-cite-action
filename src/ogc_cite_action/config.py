import jinja2

from .models import TestStatus


def get_jinja_environment() -> jinja2.Environment:
    env = jinja2.Environment(
        loader=jinja2.PackageLoader(
            "ogc_cite_action",
            "templates"
        ),
        extensions=[
            "jinja2_humanize_extension.HumanizeExtension",
        ],
    )
    env.globals.update({
        "TestStatus": TestStatus,
    })
    return env
