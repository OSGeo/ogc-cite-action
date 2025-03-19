# Test suite {{ result.suite_title }} {% if result.passed %}🏅{% else %}❌{% endif %}


{%- if result.passed %}
- **🏅 Test suite has passed!**
{%- else %}
- **❌ Test suite has failed**
{%- endif %}

- Ran {{ result.num_tests_total }} tests in {{ result.test_run_duration | humanize_precisedelta(minimum_unit="milliseconds") }}
- 🔴 Failed {{ result.num_failed_tests }} tests
- 🟡 Skipped {{ result.num_skipped_tests }} tests
- 🟢 Passed {{ result.num_passed_tests }} tests

##### Additional suite details

{%- for input_ in result.inputs %}
- {{ input_.name }}: {{ input_.value }}
{%- endfor %}

##### Conformance classes

<table>
<thead>
<tr>
<th>Conformance class</th>
<th>🔴 Failed</th>
<th>🟡 Skipped</th>
<th>🟢 Passed</th>
<th>Description</th>
</tr>
</thead>
<tbody>
{%- for conformance_class in result.conformance_class_results %}
<tr>
<td>{{ conformance_class.title }}</td>
<td>{{ conformance_class.num_failed_tests }}</td>
<td>{{ conformance_class.num_skipped_tests }}</td>
<td>{{ conformance_class.num_passed_tests }}</td>
<td>{{ conformance_class.description }}</td>
</tr>
{%- endfor %}
</tbody>
</table>

{%- if result.num_failed_tests > 0 %}

---
## :red_circle: Failures ({{ result.num_failed_tests }})

{%- for conformance_class in result.conformance_class_results %}
{%- if conformance_class.num_failed_tests > 0 %}

### Conformance class: {{ conformance_class.title }} ({{ conformance_class.num_failed_tests }})


{%- for test_case in conformance_class.gen_failed_tests() %}
<table>
  <tr>
    <th>Test case</th>
{%- if test_case.name %}
    <td>{{ test_case.name }} ({{ test_case.identifier }})</td>
{% else %}
    <td>{{ test_case.identifier }}</td>
{%- endif %}
  </tr>
  <tr>
    <th>Description</th>
    <td>{{ test_case.description | default('-', true) }}</td>
  </tr>
  <tr>
    <th>Detail</th>
    <td>{{ test_case.detail }}</td>
  </tr>
</table>
{%- endfor %}

{%- endif %}

{%- endfor %}

{%- endif %}

{%- if result.num_skipped_tests > 0 %}

---
## :yellow_circle: Skips ({{ result.num_skipped_tests }})

{%- for conformance_class in result.conformance_class_results %}
{%- if conformance_class.num_skipped_tests > 0 %}

### Conformance class: {{ conformance_class.title }} ({{ conformance_class.num_skipped_tests }})


{%- for test_case in conformance_class.gen_skipped_tests() %}
<table>
  <tr>
    <th>Test case</th>
{%- if test_case.name %}
    <td>{{ test_case.name }} ({{ test_case.identifier }})</td>
{% else %}
    <td>{{ test_case.identifier }}</td>
{%- endif %}
  </tr>
  <tr>
    <th>Description</th>
    <td>{{ test_case.description | default('-', true) }}</td>
  </tr>
  <tr>
    <th>Detail</th>
    <td>{{ test_case.detail }}</td>
  </tr>
</table>
{%- endfor %}

{%- endif %}

{%- endfor %}

{%- endif %}

{%- if result.num_passed_tests > 0 %}

---
## :green_circle: Passes ({{ result.num_passed_tests }})

{%- for conformance_class in result.conformance_class_results %}
{%- if conformance_class.num_passed_tests > 0 %}

### Conformance class: {{ conformance_class.title }} ({{ conformance_class.num_passed_tests }})


{%- for test_case in conformance_class.gen_passed_tests() %}
<table>
  <tr>
    <th>Test case</th>
{%- if test_case.name %}
    <td>{{ test_case.name }} ({{ test_case.identifier }})</td>
{% else %}
    <td>{{ test_case.identifier }}</td>
{%- endif %}
  </tr>
  <tr>
    <th>Description</th>
    <td>{{ test_case.description | default('-', true) }}</td>
  </tr>
  <tr>
    <th>Detail</th>
    <td>{{ test_case.detail }}</td>
  </tr>
</table>
{%- endfor %}

{%- endif %}

{%- endfor %}

{%- endif %}
