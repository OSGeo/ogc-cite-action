# Test suite {{ suite_name }} - execution results

- Ran {{ result.overview.num_tests_total }} tests in {{ result.overview.test_run_duration_ms | humanize_precisedelta(minimum_unit="milliseconds") }}
- :x: Failed {{ result.overview.num_failed_tests }} tests
- :black_square_button: Skipped {{ result.overview.num_skipped_tests }} tests
- :white_check_mark: Passed {{ result.overview.num_passed_tests }} tests

{% if not result.passed %}

## Failures 

{% for failed_conformance_class in result.failed_conformance_classes %}
- :x: {{ failed_conformance_class.name }}
  {% for failed_category in failed_conformance_class.failed_categories %}
  - :x: {{ failed_category.name }}
    {% for failed_test_case in failed_category.failed_test_cases %}
    - :x: {{ failed_test_case.name }} - {{ failed_test_case.description }}
      - Error: {{ failed_test_case.exception }}
      - Parameters: {{ failed_test_case.parameters }}
      - Output: {{ failed_test_case.output }}
    {% endfor %}
  {% endfor %}
{% endfor %}

{% if result.successful_conformance_classes | length > 0 %}
## Successful conformance classes
{% for successful_conformance_class in result.successful_conformance_classes %}
- :white_check_mark: {{successful_conformance_class.name}}
{% endfor %}
{% endif %}
{% endif %}

