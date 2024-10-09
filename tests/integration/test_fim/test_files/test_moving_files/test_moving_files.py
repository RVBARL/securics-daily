'''
copyright: Copyright (C) 2015-2024, Securics Inc.

           Created by Securics, Inc. <info@rvbionics.com>.

           This program is free software; you can redistribute it and/or modify it under the terms of GPLv2

type: integration

brief: File Integrity Monitoring (FIM) system watches selected files and triggering alerts
       when these files are modified. Specifically, these tests will check if FIM detects
       moving files from one directory using the 'whodata' monitoring mode to another using
       the 'realtime' monitoring mode and vice versa.
       The FIM capability is managed by the 'securics-syscheckd' daemon, which checks configured
       files for changes to the checksums, permissions, and ownership.

components:
    - fim

suite: files_moving_files

targets:
    - agent

daemons:
    - securics-syscheckd

os_platform:
    - linux

os_version:
    - Arch Linux
    - Amazon Linux 2
    - Amazon Linux 1
    - CentOS 8
    - CentOS 7
    - Debian Buster
    - Red Hat 8
    - Ubuntu Focal
    - Ubuntu Bionic

references:
    - https://documentation.rvbionics.com/current/user-manual/capabilities/file-integrity/index.html
    - https://documentation.rvbionics.com/current/user-manual/reference/ossec-conf/syscheck.html#synchronization

pytest_args:
    - fim_mode:
        realtime: Enable real-time monitoring on Linux (using the 'inotify' system calls) and Windows systems.
        whodata: Implies real-time monitoring but adding the 'who-data' information.
    - tier:
        0: Only level 0 tests are performed, they check basic functionalities and are quick to perform.
        1: Only level 1 tests are performed, they check functionalities of medium complexity.
        2: Only level 2 tests are performed, they check advanced functionalities and are slow to perform.

tags:
    - fim_moving_files
'''
import os

from pathlib import Path

import pytest

from securics_testing.constants.paths.logs import SECURICS_LOG_PATH
from securics_testing.modules.fim.patterns import EVENT_TYPE_DELETED, EVENT_TYPE_ADDED
from securics_testing.modules.fim.configuration import SYSCHECK_DEBUG
from securics_testing.tools.monitors.file_monitor import FileMonitor
from securics_testing.utils.callbacks import generate_callback
from securics_testing.utils.configuration import get_test_cases_data, load_configuration_template
from securics_testing.modules.fim.utils import get_fim_event_data

from . import TEST_CASES_PATH, CONFIGS_PATH

# Marks
pytestmark = [pytest.mark.agent, pytest.mark.linux, pytest.mark.tier(level=1)]


# Test metadata, configuration and ids.
cases_path = Path(TEST_CASES_PATH, 'cases_moving_files.yaml')
config_path = Path(CONFIGS_PATH, 'configuration_moving_files.yaml')
test_configuration, test_metadata, cases_ids = get_test_cases_data(cases_path)
test_configuration = load_configuration_template(config_path, test_configuration, test_metadata)


# Set configurations required by the fixtures.
local_internal_options = {SYSCHECK_DEBUG: 2}


# Test
@pytest.mark.parametrize('test_configuration, test_metadata', zip(test_configuration, test_metadata), ids=cases_ids)
def test_moving_file_to_whodata(test_configuration, test_metadata, set_securics_configuration, truncate_monitored_files,
                                configure_local_internal_options, create_paths_files, daemons_handler, start_monitoring):
    '''
    description: Check if the 'securics-syscheckd' daemon detects events when moving files from a directory
                 monitored by 'whodata' to another monitored by 'realtime' and vice versa. For this purpose,
                 the test will monitor two folders using both FIM monitoring modes and create a testing file
                 inside each one. Then, it will rename the testing file of the target folder using the name
                 of the one inside the source folder. Finally, the test will verify that the FIM events
                 generated to match the monitoring mode used in the folders.

    securics_min_version: 4.2.0

    tier: 1

    parameters:
        - test_configuration:
            type: dict
            brief: Configuration values for ossec.conf.
        - test_metadata:
            type: dict
            brief: Test case data.
        - set_securics_configuration:
            type: fixture
            brief: Set ossec.conf configuration.
        - truncate_monitored_files:
            type: fixture
            brief: Truncate all the log files and json alerts files before and after the test execution.
        - configure_local_internal_options:
            type: fixture
            brief: Set local_internal_options.conf file.
        - create_paths_files:
            type: list
            brief: Create the required directory or file to edit.
        - daemons_handler:
            type: fixture
            brief: Handler of Securics daemons.
        - start_monitoring:
            type: fixture
            brief: Wait FIM to start.

    assertions:
        - Verify that the 'mode' field in FIM 'deleted' events match with one used
          in the source folder of moved files.
        - Verify that the 'mode' field in FIM 'added' events match with one used
          in the target folder of moved files.

    input_description: A test case is contained in external YAML files (configuration_moving_files.yaml, cases_moving_files.yaml)
                       which includes configuration settings for the 'securics-syscheckd' daemon and, these are
                       combined with the testing directories to be monitored defined in the module.

    expected_output:
        - r'.*Sending FIM event: (.+)$' ('added' and 'deleted' events)

    tags:
        - realtime
        - who_data
    '''
    dirsrc = test_metadata.get('folder_src')
    dirdst = test_metadata.get('folder_dst')
    filename = test_metadata.get('filename')
    mod_del_event = test_metadata.get('mod_del_event')
    mod_add_event = test_metadata.get('mod_add_event')

    securics_log_monitor = FileMonitor(SECURICS_LOG_PATH)
    os.rename(os.path.join(dirsrc, filename), os.path.join(dirdst, filename))

    # Check event 'delete'
    securics_log_monitor.start(generate_callback(EVENT_TYPE_DELETED), timeout=60)
    callback_result = securics_log_monitor.callback_result
    assert callback_result

    event_data = get_fim_event_data(callback_result)
    assert event_data.get('path') == os.path.join(dirsrc, filename), 'Event path not equal'
    assert event_data.get('type') == 'deleted', 'Event type not equal'
    assert event_data.get('mode') == mod_del_event, 'FIM mode not equal'

    # Check event 'add'
    securics_log_monitor.start(generate_callback(EVENT_TYPE_ADDED), timeout=60)
    callback_result = securics_log_monitor.callback_result
    assert callback_result

    event_data = get_fim_event_data(callback_result)
    assert event_data.get('path') == os.path.join(dirdst, filename), 'Event path not equal'
    assert event_data.get('type') == 'added', 'Event type not equal'
    assert event_data.get('mode') == mod_add_event, 'FIM mode not equal'
