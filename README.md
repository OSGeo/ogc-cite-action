# ogc-cite-action

Simplify testing your OGC implementation server against [CITE](https://github.com/opengeospatial/cite/wiki). This repo
contains a CITE runner that can be called as a github action. It can also be used standalone, which allows integration
with other CI platforms or running locally.

This code can either:

- Spin up a docker container with the [ogc teamengine image](https://hub.docker.com/r/ogccite/teamengine-production),
  running test suites in an isolated CI environment
- Use an existing teamengine deployment


## Inputs

This action expects the following inputs to be provided:

- `test-suite-identfier` - Identifier of the test suite to be executed. Test suite identifiers can be gotten from the
  documentation at <http://cite.opengeospatial.org/teamengine/>. Example:
  
  ```yaml
  test-suite-identifier: 'ogcapi-features-1.0'
  ```
  
- `test-session-arguments` - Test session arguments to be passed to teamengine. These depend on the test suite that is
  going to be executed. Must be provided as a space-separated list of `key=value` pairs. Examples: 
  
  - A simple yaml string
    ```yaml
    test-session-arguments: 'iut=http://localhost:5001 noofcollections=-1'
    ```
    
  - If you prefer to use a multiline string, then  we recommend use of YAML *folded blocks* with the _strip_ 
    chomping indicator (AKA put a dash after the folded block indicator, AKA this: `>-`)
    ```yaml
    test-session-arguments: >-
      iut=http://localhost:5001 
      noofcollections=-1
    ```

- `teamengine-url` - **OPTIONAL** - URL of the teamengine instance to be used for running tests. If this parameter 
  is not specified then the action will spin up a local teamengine docker container and use it for testing. If you 
  specify a custom teamengine URL this action will also try to find authentication-related env variables and use 
  them. These env variables must be named `teamengine_username` and `teamengine_password`
  
  That the value of this paramenter must be the URL of the landing page of the teamengine service, which usually is 
  located at the `/teamengine` path. Examples:
  
  - When spinning up a local docker instance there is no need to supply this argument
  
  - When using the remote teamengine instance located at `https://my-server` with a pre-existing user `myself` and 
    a password of `something`:
  
    ```yaml
    teamengine-url: 'https://my-server/teamengine'
    teamengine-username: 'myself'
    teamengine-password: 'something'
    ```

- `teamengine-username` - **OPTIONAL** - Username to be used when logging in to a remote teamengine instance. 
  Defaults to `ogctest`, which is a user that is pre-created on the official teamengine docker image.

- `teamengine-password` - **OPTIONAL** - Password to be used when logging in to a remote teamengine instance. 
  Defaults to `ogctest`, which is the password used for the pre-created user on the official teamengine docker image
  
- `treat-skipped-tests-as-failures` - **OPTIONAL** - Whether the presence of skipped tests should be interpreted as 
  an overall failure of the test suite or not. Defaults to `false`


## Usage

The below examples define a github workflow for testing pygeoapi.

Simple usage, running the `ogcapi-features-1.0` test suite whenever there is a `push`:

```yaml
on:
  push:

jobs:

  perform-cite-testing:
    runs-on: ubuntu-22.04
    steps:
      - name: grab code
        uses: actions/checkout@v4

      - name: start pygeoapi with suitable CITE data and config
        run: >
          docker compose -f tests/cite/compose.test-cite.yaml up --detach

      - name: wait for pygeoapi to be usable
        uses: raschmitt/wait-for-healthy-container@v1.0.1
        with:
          container-name: pygeoapi-cite-pygeoapi-1
          timeout: 120

      - name: test ogcapi-features compliancy
        uses: OSGEO/ogc-cite-action@main
        with:
          test_suite_identifier: 'ogcapi-features-1.0'
          test_session_arguments: >-
            iut=http://localhost:5001
            noofcollections=-1
          treat_skipped_tests_as_failures: "true"
```

A slightly more complex example, using a matrix to test both `ogcapi-features-1.0` 
and `ogcapi-processes-1.0` test suites in parallel:

```yaml
on:
  push:

env:
  COLUMNS: 120


jobs:

  perform-cite-testing:
    strategy:
      matrix:
        test-suite:
          - suite-id: ogcapi-features-1.0
            arguments: >-
              iut=http://localhost:5001 
              noofcollections=-1
          - suite-id: ogcapi-processes-1.0
            arguments: >-
              iut=http://localhost:5001 
              noofcollections=-1

    runs-on: ubuntu-22.04
    steps:

      - name: grab code
        uses: actions/checkout@v4

      - name: start pygeoapi with suitable CITE data and config
        run: >
          docker compose -f tests/cite/compose.test-cite.yaml up --detach

      - name: wait for pygeoapi to be usable
        uses: raschmitt/wait-for-healthy-container@v1.0.1
        with:
          container-name: pygeoapi-cite-pygeoapi-1
          timeout: 120

      - name: collect docker logs on failure
        if: failure()
        uses: jwalton/gh-docker-logs@v2.2.2
        with:
          images: ghcr.io/geopython/pygeoapi
          tail: 500

      - name: test ogcapi-features compliancy
        uses: OSGEO/ogc-cite-action@main
        with:
          test_suite_identifier: ${{ matrix.test-suite.suite-id }}
          test_session_arguments: ${{ matrix.test-suite.arguments }}
          treat_skipped_tests_as_failures: "true"

```


## Running locally or on other CI platforms

This action's code can also be installed locally:

- Install [poetry](https://python-poetry.org/docs/)
- Clone this repository:

  ```shell
  git clone https://github.com/OSGeo/ogc-cite-action.git
  ```
- Install the code:

  ```shell
  cd ogc-cite-action
  poetry install
  ```

- Start your service to be tested. Let's assume it is already running on `http://localhost:5000`

- Run the teamengine docker image locally:

  ```shell
  docker run \
    --rm \
    --name teamengine \
    --network=host \
    ogccite/teamengine-production:1.0-SNAPSHOT
  ```

- Run the action code with

  ```shell
  poetry run ogc-cite-action --help
  ```

There are additional commands and options which can be used when running locally, which allow controlling the output 
format and how the inputs are supplied. Read the online