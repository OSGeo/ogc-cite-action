form_args=$(for test_arg in ${INPUT_TEST_SESSION_ARGUMENTS}; do printf -- '--data %s' "${test_arg} "; done)

curl_command=$(
  printf '%s' \
      "curl " \
      "--user teamengine:tester " \
      "--silent " \
      "--get " \
      "${form_args}" \
      "--header 'Accept: application/xml' " \
      "http://localhost:8080/teamengine/rest/suites/${INPUT_TEST_SUITE_IDENTIFIER}/run"
)

test_result=$(docker exec teamengine bash -c "${curl_command}")

echo "raw-results=${test_result}" >> $GITHUB_OUTPUT
