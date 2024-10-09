'''
copyright: Copyright (C) 2015-2024, Securics Inc.

           Created by Securics, Inc. <info@rvbionics.com>.

           This program is free software; you can redistribute it and/or modify it under the terms of GPLv2

type: integration

brief: File Integrity Monitoring (FIM) system watches selected files and triggering alerts when
       these files are modified. Specifically, these tests will verify that FIM events include
       the 'content_changes' field with the tag 'More changes' when it exceeds the maximum size
       allowed, and the 'report_changes' option is enabled.
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
    - Solaris 10
    - Solaris 11
    - macOS Catalina
    - macOS Server
    - Ubuntu Focal
    - Ubuntu Bionic
    - Windows 10
    - Windows Server 2019
    - Windows Server 2016

references:
    - https://documentation.rvbionics.com/current/user-manual/capabilities/file-integrity/index.html
    - https://documentation.rvbionics.com/current/user-manual/reference/ossec-conf/syscheck.html#diff

pytest_args:
    - fim_mode:
        realtime: Enable real-time monitoring on Linux (using the 'inotify' system calls) and Windows systems.
        whodata: Implies real-time monitoring but adding the 'who-data' information.
    - tier:
        0: Only level 0 tests are performed, they check basic functionalities and are quick to perform.
        1: Only level 1 tests are performed, they check functionalities of medium complexity.
        2: Only level 2 tests are performed, they check advanced functionalities and are slow to perform.

tags:
    - fim_report_changes
'''
import os
import time
import sys

from pathlib import Path

import pytest

from securics_testing.constants.platforms import MACOS, WINDOWS
from securics_testing.constants.paths.logs import SECURICS_LOG_PATH
from securics_testing.modules.fim.configuration import SYSCHECK_DEBUG, RT_DELAY
from securics_testing.modules.agentd.configuration import AGENTD_WINDOWS_DEBUG
from securics_testing.modules.fim.patterns import EVENT_TYPE_MODIFIED, EVENT_TYPE_ADDED, ERROR_MSG_FIM_EVENT_NOT_DETECTED, \
                                               EVENT_TYPE_DELETED, EVENT_TYPE_REPORT_CHANGES, ERROR_MSG_REPORT_CHANGES_EVENT_NOT_DETECTED
from securics_testing.modules.fim.utils import make_diff_file_path, get_fim_event_data
from securics_testing.tools.monitors.file_monitor import FileMonitor
from securics_testing.utils.file import write_file_write, delete_files_in_folder, truncate_file
from securics_testing.utils.string import generate_string
from securics_testing.utils.callbacks import generate_callback
from securics_testing.utils.configuration import get_test_cases_data, load_configuration_template

from . import TEST_CASES_PATH, CONFIGS_PATH


# Marks
pytestmark = [pytest.mark.agent, pytest.mark.linux, pytest.mark.win32, pytest.mark.darwin, pytest.mark.tier(level=1)]


# Test metadata, configuration and ids.
cases_path = ''
if sys.platform == MACOS:
    cases_path = Path(TEST_CASES_PATH, 'cases_report_changes_and_diff_macos.yaml')
else:
    cases_path = Path(TEST_CASES_PATH, 'cases_report_changes_and_diff.yaml')
config_path = Path(CONFIGS_PATH, 'configuration_report_changes_and_diff.yaml')
test_configuration, test_metadata, cases_ids = get_test_cases_data(cases_path)
test_configuration = load_configuration_template(config_path, test_configuration, test_metadata)


# Set configurations required by the fixtures.
local_internal_options = {SYSCHECK_DEBUG: 2, AGENTD_WINDOWS_DEBUG: 2, RT_DELAY: 1000}


# Tests
@pytest.mark.parametrize('test_configuration, test_metadata', zip(test_configuration, test_metadata), ids=cases_ids)
def test_reports_file_and_nodiff(test_configuration, test_metadata, configure_local_internal_options,
                        truncate_monitored_files, set_securics_configuration, create_paths_files, daemons_handler, detect_end_scan):
    '''
    description: Check if the 'securics-syscheckd' daemon reports the file changes (or truncates if required)
                 in the generated events using the 'nodiff' tag and vice versa. For this purpose, the test
                 will monitor a directory and make file operations inside it. Then, it will check if a
                 'diff' file is created for the modified testing file. Finally, if the testing file matches
                 the 'nodiff' tag, the test will verify that the FIM event generated contains in its
                 'content_changes' field a message indicating that 'diff' is truncated because
                 the 'nodiff' option is used.

    securics_min_version: 4.6.0

    tier: 1

    parameters:
        - test_configuration:
            type: dict
            brief: Configuration values for ossec.conf.
        - test_metadata:
            type: dict
            brief: Test case data.
        - configure_local_internal_options:
            type: fixture
            brief: Set local_internal_options.conf file.
        - truncate_monitored_files:
            type: fixture
            brief: Truncate all the log files and json alerts files before and after the test execution.
        - set_securics_configuration:
            type: fixture
            brief: Set ossec.conf configuration.
        - create_paths_files:
            type: list
            brief: Create the required directory or file to edit.
        - daemons_handler:
            type: fixture
            brief: Handler of Securics daemons.
        - detect_end_scan
            type: fixture
            brief: Check first scan end.

    assertions:
        - Verify that for each modified file a 'diff' file is generated.
        - Verify that FIM events include the 'content_changes' field.
        - Verify that FIM events truncate the modifications made in a monitored file
          when it matches the 'nodiff' tag.
        - Verify that FIM events include the modifications made in a monitored file
          when it does not match the 'nodiff' tag.

    input_description: A test case is contained in external YAML files (configuration_report_changes_and_diff.yaml, cases_report_changes_and_diff.yaml)
                       which includes configuration settings for the 'securics-syscheckd' daemon and, these are
                       combined with the testing directories to be monitored defined in the module.

    expected_output:
        - r'.*Sending FIM event: (.+)$' ('added', 'modified', and 'deleted' events)

    tags:
        - diff
        - scheduled
    '''
    if test_metadata.get('fim_mode') == 'whodata' and sys.platform == WINDOWS:
        time.sleep(5)
    is_truncated = 'testdir_nodiff' in test_metadata.get('folder')
    folder = test_metadata.get('folder')
    test_file_path = os.path.join(folder, test_metadata.get('filename'))

    securics_log_monitor = FileMonitor(SECURICS_LOG_PATH)

    # Create the file and and capture the event.
    truncate_file(SECURICS_LOG_PATH)
    original_string = generate_string(1, '0')
    write_file_write(test_file_path, content=original_string)

    securics_log_monitor.start(generate_callback(EVENT_TYPE_ADDED), timeout=30)
    assert securics_log_monitor.callback_result, ERROR_MSG_FIM_EVENT_NOT_DETECTED

    # Modify the file without new content and check content_changes have the correct message
    time.sleep(1)
    truncate_file(SECURICS_LOG_PATH)
    write_file_write(test_file_path, content=original_string)

    securics_log_monitor = FileMonitor(SECURICS_LOG_PATH)
    securics_log_monitor.start(generate_callback(EVENT_TYPE_REPORT_CHANGES), timeout=30)
    assert securics_log_monitor.callback_result, ERROR_MSG_REPORT_CHANGES_EVENT_NOT_DETECTED
    assert 'No content changes were found for this file.' in str(securics_log_monitor.callback_result[0]), 'Wrong content_changes field'

    # Modify the file with new content.
    truncate_file(SECURICS_LOG_PATH)
    modified_string = 'test_string' + generate_string(10, '1')
    write_file_write(test_file_path, content=modified_string)

    securics_log_monitor.start(generate_callback(EVENT_TYPE_MODIFIED), timeout=20)
    assert securics_log_monitor.callback_result
    event = get_fim_event_data(securics_log_monitor.callback_result)

    # Validate content_changes attribute exists in the event
    diff_file = make_diff_file_path(folder=test_metadata.get('folder'), filename=test_metadata.get('filename'))
    assert os.path.exists(diff_file), f'{diff_file} does not exist'

    # Validate content_changes value is truncated if the file is set to no_diff
    if is_truncated:
        assert "Diff truncated due to 'nodiff' configuration detected for this file." in event.get('content_changes'), \
            'content_changes is not truncated'
    else:
        assert 'test_string' in event.get('content_changes'), 'Wrong content_changes field'

    truncate_file(SECURICS_LOG_PATH)
    delete_files_in_folder(folder)
    securics_log_monitor.start(generate_callback(EVENT_TYPE_DELETED))
    assert get_fim_event_data(securics_log_monitor.callback_result)['mode'] == test_metadata.get('fim_mode')
