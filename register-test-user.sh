curl_command=$(
    printf '%s' \
    "curl -v " \
    "--silent " \
    "--output /dev/null " \
    "--write-out '%{http_code}' " \
    "--data firstName=teamengine " \
    "--data lastName=user " \
    "--data username=teamengine " \
    "--data password=tester " \
    "--data repeat_password=tester " \
    "--data email=noone@noplace.com " \
    "--data organization=none " \
    "--data acceptPrivacy=on " \
    "--data disclaimer=on " \
    "http://localhost:8080/teamengine/registrationHandler " \
    "--trace -"
)

docker exec team-engine bash -c "${curl_command}"
