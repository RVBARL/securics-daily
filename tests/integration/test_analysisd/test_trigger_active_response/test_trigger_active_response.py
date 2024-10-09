'''
copyright: Copyright (C) 2015-2024, Securics Inc.

           Created by Securics, Inc. <info@rvbionics.com>.

           This program is free software; you can redistribute it and/or modify it under the terms of GPLv2

type: integration

brief: Active responses perform various countermeasures to address active threats, such as blocking access
       to an agent from the threat source when certain criteria are met.

tier: 2

modules:
    - securics_analysisd
    - active_response

components:
    - manager

daemons:
    - securics-analysisd

os_platform:
    - linux

os_version:
    - Arch Linux
    - Amazon Linux 2
    - Amazon Linux 1
    - CentOS 8
    - CentOS 7
    - CentOS 6
    - Ubuntu Focal
    - Ubuntu Bionic
    - Ubuntu Xenial
    - Ubuntu Trusty
    - Debian Buster
    - Debian Stretch
    - Debian Jessie
    - Debian Wheezy
    - Red Hat 8
    - Red Hat 7
    - Red Hat 6

references:
    - https://documentation.rvbionics.com/current/user-manual/capabilities/active-response/#active-response

tags:
    - ar_analysisd
'''
import pytest

from pathlib import Path

from securics_testing.constants.paths.logs import ALERTS_JSON_PATH
from securics_testing.tools.monitors.file_monitor import FileMonitor
from securics_testing.utils import file
from securics_testing.utils.callbacks import generate_callback
from securics_testing.utils.configuration import get_test_cases_data, load_configuration_template

from . import CONFIGS_PATH, TEST_CASES_PATH, CUSTOM_SCRIPTS_PATH, RULES_SAMPLE_PATH


pytestmark = [pytest.mark.server, pytest.mark.tier(level=1)]

# Test metadata, configuration and ids.
cases_path = Path(TEST_CASES_PATH, 'cases_trigger_active_response.yaml')
config_path = Path(CONFIGS_PATH, 'configuration_trigger_active_response.yaml')
test_configuration, test_metadata, cases_ids = get_test_cases_data(cases_path)
test_configuration = load_configuration_template(config_path, test_configuration, test_metadata)

# Test configurations and paths to validate.
daemons_handler_configuration = {'all_daemons': True}
custom_ar_script = Path(CUSTOM_SCRIPTS_PATH, 'custom-ar.sh')
file_created_by_script = '/tmp/file-ar.txt'
monitored_file = '/tmp/file_to_monitor.log'


# Test function
@pytest.mark.parametrize('test_configuration, test_metadata', zip(test_configuration, test_metadata), ids=cases_ids)
def test_rules_triggers_ar(test_configuration, test_metadata, truncate_monitored_files, set_securics_configuration,
                                       prepare_ar_files, prepare_custom_rules_file, daemons_handler, fill_monitored_file):
    '''
    description: Check if an active response is triggered when an event matches with a rule.

    test_phases:
        - setup:
            - Copy custom rule and active response files to Securics paths.
            - Create a new file which will be monitored with logcollector.
            - Set securics configuration (add active_response command and localfile blocks).
            - Fill the monitored file with the log to raise the alert.
        - test:
            - Check the alert is raised.
            - Check if the active response has been triggered (cthe file is created).
        - teardown:
            - Clean logs files and restart securics to apply the configuration.
            - Remove generated file when triggering the active response.
            - Remove generated and custom copied files.
            - Restart initial securics configuration.

    securics_min_version: 4.3.5

    parameters:
        - test_configuration:
            type: fixture
            brief: Get configurations from the module.
        - test_metadata:
            type: fixture
            brief: Get metadata from the module.
        - truncate_monitored_files:
            type: fixture
            brief: Truncate securics logs.
        - set_securics_configuration:
            type: fixture
            brief: Apply changes to the ossec.conf configuration.
        - prepare_ar_files:
            type: fixture
            brief: Prepare and clean the files required for this scenario.
        - prepare_custom_rules_file:
            type: fixture
            brief: Copies custom rules_file before test, deletes after test.
        - daemons_handler:
            type: fixture
            brief: Handler of Securics daemons.
        - fill_monitored_file:
            type: fixture
            brief: Fill the monitored file.

    assertions:
        - Check that the alert is raised.
        - Check that the AR is triggered.

    input_description:
        - The `configuration_trigger_active_response` file provides the module configuration for this test.
        - The `cases_trigger_active_response` file provides the test cases.
    '''
    alerts_monitor = FileMonitor(ALERTS_JSON_PATH)
    alerts_monitor.start(generate_callback(rf".*{monitored_file}.*"))

    assert test_metadata['input'] in alerts_monitor.callback_result
    assert file.exists_and_is_file(file_created_by_script)
