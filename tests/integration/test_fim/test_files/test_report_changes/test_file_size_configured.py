'''
copyright: Copyright (C) 2015-2024, Securics Inc.

           Created by Securics, Inc. <info@rvbionics.com>.

           This program is free software; you can redistribute it and/or modify it under the terms of GPLv2

type: integration

brief: File Integrity Monitoring (FIM) system watches selected files and triggering alerts when
       these files are modified. Specifically, these tests will check if FIM limits the size of
       'diff' information to generate from the file monitored when the 'diff_size_limit' and
       the 'report_changes' options are enabled.
       The FIM capability is managed by the 'securics-syscheckd' daemon, which checks configured
       files for changes to the checksums, permissions, and ownership.

components:
    - fim

suite: files_report_changes

targets:
    - agent

daemons:
    - securics-syscheckd

os_platform:
    - linux
    - windows
    - macos

os_version:
    - Arch Linux
    - Amazon Linux 2
    - Amazon Linux 1
    - CentOS 8
    - CentOS 7
    - Debian Buster
    - Red Hat 8
    - macOS Catalina
    - macOS Server
    - Ubuntu Focal
    - Ubuntu Bionic
    - Windows 10
    - Windows Server 2019
    - Windows Server 2016

references:
    - https://documentation.rvbionics.com/current/user-manual/capabilities/file-integrity/index.html
    - https://documentation.rvbionics.com/current/user-manual/reference/ossec-conf/syscheck.html#directories

pytest_args:
    - fim_mode:
        realtime: Enable real-time monitoring on Linux (using the 'inotify' system calls) and Windows systems.
        whodata: Implies real-time monitoring but adding the 'who-data' information.
        scheduled: Implies scheduled scan
    - tier:
        0: Only level 0 tests are performed, they check basic functionalities and are quick to perform.
        1: Only level 1 tests are performed, they check functionalities of medium complexity.
        2: Only level 2 tests are performed, they check advanced functionalities and are slow to perform.

tags:
    - fim_report_changes
'''
from pathlib import Path

import pytest

from securics_testing.constants.paths.logs import SECURICS_LOG_PATH
from securics_testing.modules.fim.configuration import SYSCHECK_DEBUG
from securics_testing.modules.agentd.configuration import AGENTD_WINDOWS_DEBUG
from securics_testing.modules.fim.patterns import DIFF_MAXIMUM_FILE_SIZE, ERROR_MSG_MAXIMUM_FILE_SIZE_EVENT, ERROR_MSG_WRONG_VALUE_MAXIMUM_FILE_SIZE
from securics_testing.tools.monitors.file_monitor import FileMonitor
from securics_testing.utils.callbacks import generate_callback
from securics_testing.utils.configuration import get_test_cases_data, load_configuration_template

from . import TEST_CASES_PATH, CONFIGS_PATH


# Marks
pytestmark = [pytest.mark.agent, pytest.mark.linux, pytest.mark.win32, pytest.mark.darwin, pytest.mark.tier(level=1)]


# Test metadata, configuration and ids.
cases_path = Path(TEST_CASES_PATH, 'cases_file_size_configured.yaml')
config_path = Path(CONFIGS_PATH, 'configuration_diff_size.yaml')
test_configuration, test_metadata, cases_ids = get_test_cases_data(cases_path)
test_configuration = load_configuration_template(config_path, test_configuration, test_metadata)


# Set configurations required by the fixtures.
local_internal_options = {SYSCHECK_DEBUG: 2, AGENTD_WINDOWS_DEBUG: '2'}


# Tests
@pytest.mark.parametrize('test_configuration, test_metadata', zip(test_configuration, test_metadata), ids=cases_ids)
def test_diff_size_limit(test_configuration, test_metadata, configure_local_internal_options,
                                    truncate_monitored_files, set_securics_configuration, daemons_handler):
    '''
    description: Check if the 'securics-syscheckd' daemon limits the size of 'diff' information to generate from
                 the value set in the 'diff_size_limit' attribute when the global 'file_size' tag is different.
                 For this purpose, the test will monitor a directory and, once the FIM is started, it will wait
                 for the FIM event related to the maximum file size to generate 'diff' information. Finally,
                 the test will verify that the value gotten from that FIM event corresponds with the one set
                 in the 'diff_size_limit'.

    securics_min_version: 4.6.0

    tier: 1

    parameters:
        - test_configuration:
            type: data
            brief: Configuration used in the test.
        - test_metadata:
            type: data
            brief: Configuration cases.
        - configure_local_internal_options:
            type: fixture
            brief: Set internal configuration for testing.
        - truncate_monitored_files:
            type: fixture
            brief: Reset the 'ossec.log' file and start a new monitor.
        - set_securics_configuration:
            type: fixture
            brief: Configure a custom environment for testing.
        - daemons_handler:
            type: fixture
            brief: Handler of Securics daemons.

    assertions:
        - Verify that an FIM event is generated indicating the size limit of 'diff' information to generate
          set in the 'diff_size_limit' attribute when the global 'file_size' tag is different.

    input_description: An external YAML file (configuration_diff_size.yaml) includes configuration settings for the agent.
                       Different test cases are found in the cases_file_size_configured_configured.yaml file and include parameters for
                       the environment setup, the requests to be made, and the expected result.

    expected_output:
        - r'.*Maximum file size limit to generate diff information configured to'

    tags:
        - diff
        - scheduled
        - realtime
        - who_data
    '''
    securics_log_monitor = FileMonitor(SECURICS_LOG_PATH)
    securics_log_monitor.start(generate_callback(DIFF_MAXIMUM_FILE_SIZE), timeout=30)
    callback_result = securics_log_monitor.callback_result
    assert callback_result, ERROR_MSG_MAXIMUM_FILE_SIZE_EVENT
    assert str(securics_log_monitor.callback_result[0]) == test_metadata.get('diff_size_limit_kb'), ERROR_MSG_WRONG_VALUE_MAXIMUM_FILE_SIZE
