'''
copyright: Copyright (C) 2015-2024, Securics Inc.

           Created by Securics, Inc. <info@rvbionics.com>.

           This program is free software; you can redistribute it and/or modify it under the terms of GPLv2

type: integration

brief: File Integrity Monitoring (FIM) system watches selected files and triggering alerts when
       these files are modified. Specifically, these tests will verify that FIM generates events
       only for registry entry operations in monitored keys that do not match the 'restrict_key'
       or the 'restrict_value' attributes.
       The FIM capability is managed by the 'securics-syscheckd' daemon, which checks configured
       files for changes to the checksums, permissions, and ownership.

components:
    - fim

suite: registry_restrict

targets:
    - agent

daemons:
    - securics-syscheckd

os_platform:
    - windows

os_version:
    - Windows 10
    - Windows 8
    - Windows 7
    - Windows Server 2019
    - Windows Server 2016
    - Windows Server 2012
    - Windows Server 2003
    - Windows XP

references:
    - https://documentation.rvbionics.com/current/user-manual/capabilities/file-integrity/index.html
    - https://documentation.rvbionics.com/current/user-manual/reference/ossec-conf/syscheck.html#windows-registry

pytest_args:
    - fim_mode:
        realtime: Enable real-time monitoring on Linux (using the 'inotify' system calls) and Windows systems.
        whodata: Implies real-time monitoring but adding the 'who-data' information.
    - tier:
        0: Only level 0 tests are performed, they check basic functionalities and are quick to perform.
        1: Only level 1 tests are performed, they check functionalities of medium complexity.
        2: Only level 2 tests are performed, they check advanced functionalities and are slow to perform.

tags:
    - fim_registry_restrict
'''
from pathlib import Path

import os
import sys

if sys.platform == 'win32':
    import win32con
    from win32con import KEY_WOW64_32KEY, KEY_WOW64_64KEY

import pytest
from securics_testing.constants.paths.logs import SECURICS_LOG_PATH
from securics_testing.tools.monitors.file_monitor import FileMonitor
from securics_testing.utils.configuration import get_test_cases_data, load_configuration_template
from securics_testing.utils.callbacks import generate_callback
from securics_testing.utils import file
from securics_testing.modules.fim.patterns import EVENT_TYPE_ADDED, EVENT_TYPE_DELETED, IGNORING_DUE_TO_RESTRICTION
from securics_testing.modules.agentd.configuration import AGENTD_WINDOWS_DEBUG
from securics_testing.modules.fim.configuration import SYSCHECK_DEBUG
from securics_testing.modules.fim.utils import get_fim_event_data, delete_registry


from . import TEST_CASES_PATH, CONFIGS_PATH

# Marks

pytestmark = [pytest.mark.agent, pytest.mark.win32, pytest.mark.tier(level=1)]

# Test metadata, configuration and ids.
cases_path = Path(TEST_CASES_PATH, 'cases_registry_restrict_key.yaml')
config_path = Path(CONFIGS_PATH, 'configuration_registry_restrict_key.yaml')
test_configuration, test_metadata, cases_ids = get_test_cases_data(cases_path)
test_configuration = load_configuration_template(config_path, test_configuration, test_metadata)

# Set configurations required by the fixtures.
daemons_handler_configuration = {'all_daemons': True}
local_internal_options = {SYSCHECK_DEBUG: 2}

# Tests
@pytest.mark.parametrize('test_configuration, test_metadata', zip(test_configuration, test_metadata), ids=cases_ids)
def test_restrict_key(test_configuration, test_metadata,configure_local_internal_options,
                            truncate_monitored_files, set_securics_configuration, daemons_handler, detect_end_scan, create_registry_key):
    '''
    description: Check if the 'securics-syscheckd' daemon detects or ignores events in monitored registry entries
                 depending on the value set in the 'restrict_key' attribute. This attribute limit checks to
                 keys that match the entered string or regex and its name. For this purpose, the test will
                 monitor a key, create testing subkeys inside it, and make operations on those subkeys. Finally,
                 the test will verify that FIM 'added' and 'deleted' events are generated only for the testing
                 subkeys that are not restricted.

    securics_min_version: 4.2.0

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
        - daemons_handler:
            type: fixture
            brief: Handler of Securics daemons.
        - create_registry_key
            type: fixture
            brief: Create windows registry key.
        - detect_end_scan
            type: fixture
            brief: Check first scan end.

    assertions:
        - Verify that FIM events are only generated for operations in monitored keys
          that do not match the 'restrict_key' attribute.
        - Verify that FIM 'ignoring' events are generated for monitored keys that are restricted.

    input_description: The file 'configuration_registry_restrict_key.yaml' provides the configuration
                       template.
                       The file 'cases_registry_restrict_key.yaml' provides the tes cases configuration
                       details for each test case.

    expected_output:
        - r'.*Sending FIM event: (.+)$' ('added', 'deleted' events)
        - r'.*Ignoring entry .* due to restriction .*'

    '''
    securics_log_monitor = FileMonitor(SECURICS_LOG_PATH)

    if test_metadata['triggers_event']:
        securics_log_monitor.start(callback=generate_callback(EVENT_TYPE_ADDED))
        assert securics_log_monitor.callback_result
        event = get_fim_event_data(securics_log_monitor.callback_result)
        assert event['type'] == 'added', 'Event type not equal'
        assert event['path'] == os.path.join(test_metadata['key'], test_metadata['sub_key']), 'Event path not equal'
        assert event['arch'].strip('[]') == test_metadata['arch'], 'Arch not equal'

        delete_registry(win32con.HKEY_LOCAL_MACHINE, test_metadata['sub_key'], KEY_WOW64_64KEY if test_metadata['arch'] == 'x64' else KEY_WOW64_32KEY)
        securics_log_monitor.start(callback=generate_callback(EVENT_TYPE_DELETED))
        assert securics_log_monitor.callback_result
        event = get_fim_event_data(securics_log_monitor.callback_result)
        assert event['type'] == 'deleted', 'Event type not equal'
        assert event['path'] == os.path.join(test_metadata['key'], test_metadata['sub_key']), 'Event path not equal'
        assert event['arch'].strip('[]') == test_metadata['arch'], 'Arch not equal'
    else:
        securics_log_monitor.start(callback=generate_callback(IGNORING_DUE_TO_RESTRICTION))
        assert securics_log_monitor.callback_result

        delete_registry(win32con.HKEY_LOCAL_MACHINE, test_metadata['sub_key'], KEY_WOW64_64KEY if test_metadata['arch'] == 'x64' else KEY_WOW64_32KEY)

        securics_log_monitor.start(callback=generate_callback(IGNORING_DUE_TO_RESTRICTION), only_new_events=True)
        assert not securics_log_monitor.callback_result

        securics_log_monitor.start(callback=generate_callback(EVENT_TYPE_DELETED))
        assert not securics_log_monitor.callback_result
