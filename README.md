# ogc-cite-action

A GitHub Action that simplifies testing your OGC server against [CITE](https://github.com/opengeospatial/cite/wiki). 

This action is able to either:

- Spin up a docker container with the [ogc teamengine image](https://hub.docker.com/r/ogccite/teamengine-production),
  running test suites in an isolated CI environment
- Use an existing teamengine deployment


## Inputs

This action expects the following inputs to be provided:

- `test-suite-identfier` - Identifier of the test suite to be executed - See below for existing identifiers
- `test-session-arguments` - Test session arguments to be passed to teamengine. These depend on the test suite that is
  going to be executed. Regardless, this must be given as a space-separated list of `key=value` pairs
- `teamengine-url` - Optional URL of the teamengine instance to be used for running tests. If this parameter is not 
  specified then the action will spin up a local teamengine docker container and use it for testing. If you specify a
  custom teamengine URL this action will also try to find authentication-related env variables and use them. These
  env variables must be named `teamengine_username` and `teamengine_password`


## Usage

Example usage for testing a service running locally at `http://localhost:5001` against the `ogcapi-features-1.0` 
executable test suite. Because the `teamengine-url` input is not specified, the action spins up a local docker 
container running teamengine:

```yaml
- name: test ogcapi-features compliancy
  uses: OSGEO/ogc-cite-action@main
  with:
    test-suite-identifier: 'ogcapi-features-1.0'
    test-session-arguments: 'iut=http://localhost:5001 noofcollections=-1'
  env:
    teamengine_username: ${{ secrets.TEAMENGINE_USERNAME }}
    teamengine_password: ${{ secrets.TEAMENGINE_PASSWORD }}
```




## Executable Test Suites

In order to successfully run this action you need to know:

- `test-suite-identifier` - the identifier of the test suite you want to run
- `test-session-arguments` - the parameters that can be passed to the teamengine test runner

Information on existing test suites can be found at:

http://cite.opengeospatial.org/teamengine/

Examples: 

1. [OGC API Features](https://cite.opengeospatial.org/teamengine/about/ogcapi-features-1.0/1.0/site/) one must use the following:

   - `test-suite-identifier`: `ogcapi-features-1.0`
   - `test-session-arguments`:
     - `iut`
     - `noofcollections`

2. OGC API - Processes:

  - `test-suite-identifier`: `ogcapi-processes-1.0`
  - `test-session-arguments`:
    - `iut`
    - `noofcollections`

3. OGC API - EDR

   - `test-suite-identifier`: `ogcapi-edr10`
   - `test-session-arguments`:
     - `iut`
     - `ics`


## Running locally

With a bit of extra effort, this action's code can be run locally:

- Start your service to be tested. Let's assume it is running on `http://localhost:5000`

- Run the teamengine docker image:

  ```shell
  docker run --rm --name teamengine --network=host ogccite/teamengine-production:1.0-SNAPSHOT
  ```

- Install the action code with poetry and then run its main script. Here we are executing the test suite for 
  ogcapi-features:

  ```shell
  poetry install
  poetry run ogc-cite-action \
    --debug \
    execute-test-suite \
    http://localhost:8080/teamengine \
    ogcapi-features-1.0 \
    iut=http://localhost:5000 \
    noofcollections=-1
  ```