# Test suite {{ result.suite_name }} {% if result.passed %}:medal_sports:{% endif %}

## Overview

- Ran {{ result.overview.num_tests_total }} tests in {{ result.overview.test_run_duration_ms | humanize_precisedelta(minimum_unit="milliseconds") }}
- :red_circle: Failed {{ result.overview.num_failed_tests }} tests
- :yellow_circle: Skipped {{ result.overview.num_skipped_tests }} tests
- :green_circle: Passed {{ result.overview.num_passed_tests }} tests

---

## Details

{%- for conformance_class in result.conformance_classes %}


### Conformance class: {{ conformance_class.name }}
{%- for category in conformance_class.categories %}


##### Category: {{ category.short_name }}

<table>
  <tr>
    <th>Status</th>
    <th>Test case</th>
  </tr>
{%- for test_case in category.test_cases %}
{%- set status %}
    {%- if test_case.status == TestStatus.PASSED %}:green_circle:
    {%- elif test_case.status == TestStatus.SKIPPED %}:yellow_circle:
    {%- else %}:red_circle:
{%- endif %}
{%- endset %}
  <tr>
    <td>{{ status }} - {{ test_case.status.value }}</td>
    <td>
      {%- if test_case.status == TestStatus.PASSED %}
      {{ test_case.name }}
      {%- else %}
      \[{{ test_case.name }}](#{{ test_case.name }})
      {%- endif %}
    </td>
  </tr>
{%- endfor %}
</table>

--- 
{% endfor %}
{% endfor %}


{%- set skipped_test_cases = result.gen_skipped_test_cases() | list %}
{%- set failed_test_cases = result.gen_failed_test_cases() | list %}

{%- if skipped_test_cases | length > 0 %}
## :yellow_circle: Skips
{%- for skipped_test_case in result.gen_skipped_test_cases() %}

<table>
  <tr>
    <th>Test case</th>
    <td><a name="{{ skipped_test_case.name }}">{{ skipped_test_case.name }}</a></td>
  </tr>
  <tr>
    <th>Description</th>
    <td>{{ skipped_test_case.description }}</td>
  </tr>
  <tr>
    <th>Conformance class</th>
    <td>{{ skipped_test_case.category.conformance_class.name }}</td>
  </tr>
  <tr>
    <th>Category</th>
    <td>{{ skipped_test_case.category.short_name }}</td>
  </tr>
  <tr>
    <th>Exception</th>
    <td>{{ skipped_test_case.exception }}</td>
  </tr>
  {% if skipped_test_case.output %}
  <tr>
    <th>Output</th>
    <td>{{ skipped_test_case.output }}</td>
  </tr>
  {% endif %}
  {% if skipped_test_case.parameters | length > 0 %}
  <tr>
    <th>Parameters</th>
    <td>
    {%- for param in skipped_test_case.parameters %}
      - {{ param }}
    {%- endfor %}
    </td>
  </tr>
  {% endif %}
</table>

<br>
<br>

{%- endfor %}
{%- endif %}
{%- if failed_test_cases | length > 0 %}
## :red_circle: Failures
{%- for failed_test_case in result.gen_failed_test_cases() %}

<table>
  <tr>
    <th>Test case</th>
    <td><a name="{{ failed_test_case.name }}">{{ failed_test_case.name }}</a></td>
  </tr>
  <tr>
    <th>Description</th>
    <td>{{ failed_test_case.description }}</td>
  </tr>
  <tr>
    <th>Conformance class</th>
    <td>{{ failed_test_case.category.conformance_class.name }}</td>
  </tr>
  <tr>
    <th>Category</th>
    <td>{{ failed_test_case.category.short_name }}</td>
  </tr>
  <tr>
    <th>Exception</th>
    <td>{{ failed_test_case.exception }}</td>
  </tr>
{% if failed_test_case.output %}
  <tr>
    <th>Output</th>
    <td>{{ failed_test_case.output }}</td>
  </tr>
{% endif %}
{% if failed_test_case.parameters | length > 0 %}
  <tr>
    <th>Parameters</th>
    <td>
{%- for param in failed_test_case.parameters %}
      - {{ param }}
    {%- endfor %}
    </td>
  </tr>
{% endif %}
</table>

<br>
<br>

{% endfor %}
{% endif %}
