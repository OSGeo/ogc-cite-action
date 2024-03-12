form_args=$(for test_arg in ${INPUT_TEST_SESSION_ARGUMENTS}; do printf -- '--form %s' "${test_arg} "; done)

curl_command=$(
  printf '%s' \
      "curl " \
      "--user teamengine:tester " \
      "--silent " \
      "${form_args}" \
      "http://localhost:8080/teamengine/rest/suites/${INPUT_TEST_SUITE_IDENTIFIER}/run"
)

test_result=$(docker exec team-engine bash -c "${curl_command}")

echo "test-result=${test_result}" >> $GITHUB_OUTPUT
