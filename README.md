# ogc-cite-action
GitHub Action to run your OGC implementation against OGC CITE

This is a composite action. It spawns a docker container 
running [ogc teamengine](https://hub.docker.com/r/ogccite/teamengine-production).

It then proceeds to run cURL inside the docker image to test your web application.

The [teamengine docs](http://opengeospatial.github.io/teamengine/users.html) 
seem to hint that running a test suite via their API can be done by submitting 
either GET or POST requests to teamengine. Regardless, it seems that `GET` is
the only request type that works OK, at least when testing the OGC API Features
Executable Test Suite.


## Executable Test Suites

- `cat30`: OGC Catalogue 3.0 Conformance Test Suite
- `cdb10`: OGC CDB 1.0 Executable Conformance Test Suite
- `kml22`: KML 2.2 Conformance Test Suite
- `geopose10`: GeoPose 1.0 Conformance Test Suite
- `georss10`: GeoRSS 1.0 Conformance Test Suite
- `geotiff11`: GeoTIFF 1.1 Conformance Test Suite
- `gml32`: GML 3.2 (ISO 19136:2007) Conformance Test Suite
- `gmljpx20`: GML in JPEG 2000 Conformance Test Suite
- `gpkg10`: GeoPackage 1.0 Conformance Test Suite
- `gpkg12`: GeoPackage 1.2 Conformance Test Suite
- `ogcapi-edr10`: OGC API - Environmental Data Retrieval 1.0 Conformance Test Suite
- `ogcapi-features-1.0`: OGC API-Features 1.0 Conformance Test Suite
- `ogcapi-processes-1.0`: OGC API-Processes 1.0 Conformance Test Suite
- `omxml20`: Observations and Measurements - XML Implementation (OMXML)
- `sensorml20`: Sensor Model Language (SensorML)
- `sos20`: OGC Sensor Observation Service 2.0.0 - Executable Test Suite
- `sta10`: SensorThings API (STA)
- `swecommon20`: Sensor Web Enablement (SWE) Common Data Model Encoding Standard
- `wcs`: OGC Web Coverage Service 2.0.1 - Executable Test Suite
- `wcs11`: OGC Web Coverage Service 1.1.1 - Executable Test Suite
- `wfs`: Web Feature Service 1.1.0
- `wfs10`: Conformance Test Suite - OGC Web Feature Service 1.0.0
- `wfs20`: WFS 2.0 (ISO 19142:2010) Conformance Test Suite
- `wms11`: Conformance Test Suite - OGC Web Map Service 1.1
- `wms13`: Conformance Test Suite - OGC Web Map Service 1.3.0
- `wmts`: OGC Web Map Tile Service 1.0.0 - Executable Test Suite
- `wps20`: WPS 2.0 Conformance Test Suite

In order to successfully run this action you need to know:

- the identifier of the test suite you want to run
- the parameters that can be passed to the teamengine test runner


#### OGC API Features

- test suite identifier (`etscode`): ogcapi-features-1.0
- implementation under test (`iut`): Mandatory - Implementation under test. This is a URI (http://localhost:5000)
- `noofcollections`: Optional - An integer specifying the number of collections being tested. A value of `-1` means 
  that all available collections shall be tested


#### OGC API Processes

- `etscode`: ogcapi-processes-1.0
- `iut`: Mandatory - Implementation under test. This is a URI (http://localhost:5001)
- `noofcollections`: Optional - An integer specifying the number of
  collections being tested. A value of `-1` means that all available
  collections shall be tested


#### OGC API EDR

- `etscode`: ogcapi-edr10
- `iut`: Mandatory - Implementation under test. This is a URI (http://localhost:5001)
- `ics`: A comma-separated list of string values. Indicates ???


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
    --test-suite-input iut http://localhost:5000 \
    --test-suite-input noofcollections -1
  ```