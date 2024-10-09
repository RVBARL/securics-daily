'''
copyright: Copyright (C) 2015-2024, Securics Inc.

           Created by Securics, Inc. <info@rvbionics.com>.

           This program is free software; you can redistribute it and/or modify it under the terms of GPLv2

type: integration

brief: File Integrity Monitoring (FIM) system watches selected files and triggering alerts when these
       files are modified. In particular, these tests will check if FIM events are still generated when
       a monitored directory is deleted and created again.
       The FIM capability is managed by the 'securics-syscheckd' daemon, which checks configured files
       for changes to the checksums, permissions, and ownership.

components:
    - fim

suite: basic_usage

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
    - https://man7.org/linux/man-pages/man8/auditd.8.html
    - https://documentation.rvbionics.com/current/user-manual/capabilities/auditing-whodata/who-linux.html
    - https://documentation.rvbionics.com/current/user-manual/capabilities/file-integrity/index.html
    - https://documentation.rvbionics.com/current/user-manual/reference/ossec-conf/syscheck.html

pytest_args:
    - fim_mode:
        realtime: Enable real-time monitoring on Linux (using the 'inotify' system calls) and Windows systems.
        whodata: Implies real-time monitoring but adding the 'who-data' information.
    - tier:
        0: Only level 0 tests are performed, they check basic functionalities and are quick to perform.
        1: Only level 1 tests are performed, they check functionalities of medium complexity.
        2: Only level 2 tests are performed, they check advanced functionalities and are slow to perform.

tags:
    - fim
'''
import sys
import pytest

from pathlib import Path

from securics_testing.constants.paths.logs import SECURICS_LOG_PATH
from securics_testing.constants.platforms import WINDOWS
from securics_testing.constants.platforms import MACOS
from securics_testing.modules.agentd.configuration import AGENTD_DEBUG, AGENTD_WINDOWS_DEBUG
from securics_testing.modules.fim.patterns import EVENT_TYPE_ADDED, EVENT_TYPE_DELETED, EVENT_TYPE_MODIFIED
from securics_testing.modules.monitord.configuration import MONITORD_ROTATE_LOG
from securics_testing.modules.fim.configuration import SYMLINK_SCAN_INTERVAL, SYSCHECK_DEBUG
from securics_testing.tools.monitors.file_monitor import FileMonitor
from securics_testing.utils import file
from securics_testing.utils.callbacks import generate_callback
from securics_testing.utils.configuration import get_test_cases_data, load_configuration_template

from . import TEST_CASES_PATH, CONFIGS_PATH


# Pytest marks to run on any service type on linux or windows.
pytestmark = [pytest.mark.agent, pytest.mark.linux, pytest.mark.darwin, pytest.mark.tier(level=0)]

# Test metadata, configuration and ids.
cases_path = Path(TEST_CASES_PATH, 'cases_cud.yaml')
config_path = Path(CONFIGS_PATH, 'configuration_basic.yaml')
test_configuration, test_metadata, cases_ids = get_test_cases_data(cases_path)
test_configuration = load_configuration_template(config_path, test_configuration, test_metadata)

# Set configurations required by the fixtures.
local_internal_options = {SYSCHECK_DEBUG: 2, AGENTD_DEBUG: 2, MONITORD_ROTATE_LOG: 0, SYMLINK_SCAN_INTERVAL: 2}
if sys.platform == WINDOWS: local_internal_options.update({AGENTD_WINDOWS_DEBUG: 2})


@pytest.mark.parametrize('test_configuration, test_metadata', zip(test_configuration, test_metadata), ids=cases_ids)
def test_cud(test_configuration, test_metadata, set_securics_configuration, truncate_monitored_files,
             configure_local_internal_options, symlink_target, symlink, daemons_handler,
             start_monitoring):

    if sys.platform == MACOS and not test_metadata['fim_mode'] == 'scheduled':
        pytest.skip(reason="Realtime and whodata are not supported on macos")

    securics_log_monitor = FileMonitor(SECURICS_LOG_PATH)
    testfile_name = 'testie.txt'

    # Create
    file.truncate_file(SECURICS_LOG_PATH)
    file.write_file(symlink.joinpath(testfile_name))
    securics_log_monitor.start(generate_callback(EVENT_TYPE_ADDED))
    assert securics_log_monitor.callback_result

    # Update
    file.truncate_file(SECURICS_LOG_PATH)
    file.write_file(symlink.joinpath(testfile_name), 'new_text')
    securics_log_monitor.start(generate_callback(EVENT_TYPE_MODIFIED))
    assert securics_log_monitor.callback_result

    # Remove
    file.truncate_file(SECURICS_LOG_PATH)
    file.remove_file(symlink.joinpath(testfile_name))
    securics_log_monitor.start(generate_callback(EVENT_TYPE_DELETED))
    assert securics_log_monitor.callback_result
