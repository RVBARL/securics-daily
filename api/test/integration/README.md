# API Integration Tests

## General information

An integration test is used to check that the behavior of the different application modules is the expected one when 
they are integrated. In other words, the integration tests check the correct interaction between the application 
components.

The API integration tests are used to verify that the API is working properly in a complete Securics environment.
This environment is built using [`docker`](https://www.docker.com/).

The `securics/api/test/integration` directory contains all the API integration tests files and directories used for the
environment deployment.

## API integration tests files

The API integration tests files use the [`tavern`](https://tavern.readthedocs.io/en/latest/) framework. Tavern is
a [`pytest`](https://docs.pytest.org/en/7.1.x/) based API testing framework for HTTP, MQTT, or other protocols. These
files are written in the `yaml` language and their names can follow the following formats:

`test_{module}_endpoints.tavern.yaml` or `test_rbac_{rbac_mode}_{module}_endpoints.tavern.yaml`

where `module` is the module which the endpoints tested belong; and `rbac_mode` is the RBAC mode (white or black) used 
for the test (see [RBAC API integration tests](#RBAC-API-integration-tests)).

## Docker environment

The Securics environment used to perform the API integration tests is built using `docker`.

This environment is composed of **12 docker containers**. These containers have the following components installed: 3
Securics managers, that compose a Securics cluster (1 master, 2 workers); 4 Securics agents with the same version as the managers
forming the cluster; 4 Securics agents with version 3.13.2 (old); and 1 HAProxy load balancer.

The Securics version used for the managers and non-old agents is the one specified by the branch used to perform the API
integration tests.

The `docker-compose.yml` file used to deploy the environment is at `securics/api/test/integration/env`. The `Dockerfile`,
`entrypoint.sh`, and other configuration files can be found in the `base` directory.

We also use specific **configurations and health checks depending on the test executed**. These configurations can be
found at the `configurations` directory. Python scripts commonly used by some of these health checks and files are
located in the `tools` directory.

Apart from this setup, we simulate 2 disconnected and 2 never-connected agents.

### How is the environment deployed?

The environment deployment is done automatically when performing an API integration test. The tests are executed
with `pytest <test_name>`.

The `conftest.py` file is the one in charge of deploying the API integration tests environment. When a test is
performed, the `api_test` function is also executed. This function is responsible for setting up the environment and
cleaning temporary folders, stopping and removing containers; and saving log and environment status, once the test has 
finished. The execution of `api_test` is done automatically thanks to the `pytest.fixture` decorator.

In the `conftest.py` file, we can also find functions used to make the HTML report,
configure [RBAC](#RBAC-API-integration-tests), etc.

### Environment selection

The Securics docker environment will have a different configuration depending on
the [`pytest` mark](https://docs.pytest.org/en/6.2.x/mark.html) used to run the tests with.

- If the `standalone` mark is specified, a Securics environment with **1 manager and 12 agents** will be built (no cluster)
  .

- If the `cluster` mark is specified, a Securics cluster setup with **3 managers and 12 agents** will be built.

- If **no mark** is specified, a Securics cluster setup with **3 managers and 12 agents** will be built.

The following table shows how these marks must be used with the `pytest` command and the environment they build:

| Command                          | Environment                                          |  
|----------------------------------|------------------------------------------------------|
| `pytest TEST_NAME`               | Securics cluster environment                            |  
| `pytest -m cluster TEST_NAME`    | Securics cluster environment                            |
| `pytest -m standalone TEST_NAME` | Securics environment with cluster disabled (standalone) | 

Apart from choosing the environment to be built, the marks are also used to filter the API integration test cases. By
default, tests without the `standalone` or `cluster` marks, will have both of them implicitly. Test cases with **only
standalone** can only be passed in a Securics environment with cluster disabled and cases with **only cluster** mark can
only be passed in a Securics cluster environment.

Talking about [RBAC API integration tests](#RBAC-API-integration-tests), they don't have any marks, so there is no need
to specify one when running them. If a mark is specified, no tests will be run due to the filters. In other words,
**RBAC tests are always going to be performed in the default cluster setup**.

## RBAC API integration tests

As said in previous sections, some test names follow the structure
`test_rbac_{rbac_mode}_{module}_endpoints.tavern.yaml`.

These tests are used to check the proper functioning of a Securics environment with RBAC configurations. The `conftest.py`
file includes functions in charge of changing the RBAC mode and creating the specified RBAC resources for the test in
execution. The `env/configurations/rbac` directory includes all the specific configurations for each RBAC API 
integration test, for both **white** and **black** modes.

## Test mapping for CI

Every time a pull request is created in GitHub for the `securics` repository, a battery of checks is performed in the CI
machines. One of these checks is the API integration tests execution with success.

The API integration tests performed depend on the files modified in the pull request. In most cases, 10 API integration
tests that we consider the basic ones are performed. These tests are the following:

- `test_agent_DELETE_endpoints.tavern.yaml`
- `test_agent_GET_endpoints.tavern.yaml`
- `test_agent_POST_endpoints.tavern.yaml`
- `test_agent_PUT_endpoints.tavern.yaml`
- `test_cluster_endpoints.tavern.yaml`
- `test_experimental_endpoints.tavern.yaml`
- `test_security_DELETE_endpoints.tavern.yaml`
- `test_security_GET_endpoints.tavern.yaml`
- `test_security_POST_endpoints.tavern.yaml`
- `test_security_PUT_endpoints.tavern.yaml`

The `securics/api/test/integration/mapping` directory contains the `integration_test_api_endpoints.json` file that
represents a mapping between the API and framework files; and the API integration tests that need to be performed. The
API integration tests executed by the CI machines will be the union of the mapped integration tests of each file
modified in the pull request.

This JSON file is updated when executing the `_test_mapping.py` script. The script needs to be run manually every time
a new file or directory is added. More information can be found at `mapping/README.md`

## Tests execution

To perform a Securics API integration test, we need a specific `python3` environment. This python environment includes the 
following dependencies:

```python
pytest==5.4.3
requests==2.23.0
pyaml==21.10.1
tavern==1.0.0
pykwalify==1.7.0
pytest-html==2.1.1
```

The `docker-compose` version needed is **1.28.0 or newer**. **It cannot be 2.X.Y** as it includes breaking changes that
will make the generation of our API integration test environment fail.

Once these requirements are satisfied, we can perform the API integration tests:

```text
$ python3 -m pytest test_agent_GET_endpoints.tavern.yaml --disable-warnings
========================================== test session starts ===========================================
platform linux -- Python 3.9.9, pytest-5.4.3, py-1.11.0, pluggy-0.13.1
rootdir: /home/user/git/securics/api/test/integration, inifile: pytest.ini
plugins: html-2.1.1, metadata-2.0.1, tavern-1.0.0
collected 92 items                                                                                       

test_agent_GET_endpoints.tavern.yaml ............................................................. [ 66%]
...............................                                                                    [100%]

============================== 92 passed, 98 warnings in 217.61s (0:03:37) ===============================
```

```text
API integration tests

optional arguments:
  --build-managers-only            
                  Recreates only the managers' image once the AIT test environment is built.
  --nobuild
                  Prevents rebuilding the environment when running tests once the images are already created.
  --disable-warnings 
                  Disables warnings during test execution.
```

We can also use the `securics/api/test/integration/run_tests.py` script. This script includes the possibility to collect a 
group of tests to be passed. Script arguments:

```text
$ python3 run_tests.py -h
usage: run_tests.py [options]

API integration tests

optional arguments:
  -h, --help            show this help message and exit
  -l TEST_LIST, --list TEST_LIST
                        Specify a list of tests separated by a comma.
  -e, --exclude         Run every test excluding the already saved in the RESULTS_FOLDER.
  -r, --results         Get result summary from the already run tests.
  -k KEYWORD, --keyword KEYWORD
                        Specify the keyword to filter tests out. Default None.
  -R {both,yes,no}, --rbac {both,yes,no}
                        Specify what to do with RBAC tests. Run everything, only RBAC ones or no RBAC. Default "both".
  -m {both,standalone,cluster}, --mode {both,standalone,cluster}
                        Specify where to pass API integration tests. Run tests in both environments, standalone environment or Securics cluster environment. Default "both".
  -i ITERATIONS, --iterations ITERATIONS
                        Specify how many times will every test be run. Default 1.
```

The `run_test.py` script does not show the tests' full output. The full reports are saved 
at `securics/api/test/integration/_test_results`. Containers' logs (`ossec.log`, `api.log` and `cluster.log`) are stored 
at `_test_results/logs`. Reports in HTML format are also generated and can be found at `_test_results/html_reports`.
