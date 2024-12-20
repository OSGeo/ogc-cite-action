import jinja2


def get_jinja_environment() -> jinja2.Environment:
    return jinja2.Environment(
        loader=jinja2.PackageLoader(
            "ogc_cite_action",
            "templates"
        ),
        extensions=[
            "jinja2_humanize_extension.HumanizeExtension",
        ],
    )
