# Test suite {{ suite_name }}

## Overview

- Ran {{ result.overview.num_tests_total }} tests in {{ result.overview.test_run_duration_ms | humanize_precisedelta(minimum_unit="milliseconds") }}
- :x: Failed {{ result.overview.num_failed_tests }} tests
- :black_square_button: Skipped {{ result.overview.num_skipped_tests }} tests
- :white_check_mark: Passed {{ result.overview.num_passed_tests }} tests - {% if result.passed %}:medal_sports: All tests passed!{% endif %}


## Details

{%- for conformance_class in result.conformance_classes %}
### Conformance class: {{ conformance_class.name }}
{%- for category in conformance_class.categories %}


##### Category: {{ category.name }}

{% for test_case in category.test_cases %}
- {% if test_case.status == TestStatus.PASSED %}:green_circle:{% elif test_case.status == TestStatus.SKIPPED %}:yellow_circle:{% else %}:red_circle:{% endif %} {{ test_case.category.name }} - {{ test_case.name }}
{% endfor %}
{% endfor %}
{% endfor %}


{%- if not result.passed %}
## Skips
{%- for skipped_test_case in result.gen_skipped_test_cases() %}

##### {{ skipped_test_case.name }}

**Conformance class:** {{ skipped_test_case.category.conformance_class.name }} 
**Category:** {{ skipped_test_case.category.name }}
**Test case description:** {{ skipped_test_case.description }}
**Exception:** {{ skipped_test_case.exception }}
{% if skipped_test_case.output %}
**Output:** {{ skipped_test_case.output }}
{% endif %}
{% if skipped_test_case.parameters | length > 0 %}
**Parameters:**
{%- for param in skipped_test_case.parameters %}
- {{ param }}
{% endfor %}
{% endif %}
{% endfor %}
## Failures
{%- for failed_test_case in result.gen_failed_test_cases() %}
##### {{ failed_test_case.name }}

**Conformance class:** {{ failed_test_case.category.conformance_class.name }}
**Category:** {{ failed_test_case.category.name }}
**Test case description:** {{ failed_test_case.description }}
**Exception:** {{ failed_test_case.exception }}
{% if failed_test_case.output %}
**Output:** {{ failed_test_case.output }}
{% endif %}
{% if failed_test_case.parameters | length > 0 %}
**Parameters:**
{%- for param in failed_test_case.parameters %}
- {{ param }}
{% endfor %}
{% endif %}
{% endfor %}
{% endif %}
