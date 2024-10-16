'''
copyright: Copyright (C) 2015-2024, Securics Inc.

           Created by Securics, Inc. <info@rvbionics.com>.

           This program is free software; you can redistribute it and/or modify it under the terms of GPLv2

type: integration

brief: These tests will check the different errors that may appear by modifying
       the path of the configurable executable (exec_path).

tier: 0

modules:
    - authd

components:
    - manager

daemons:
    - securics-authd

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
    - https://documentation.rvbionics.com/current/user-manual/reference/ossec-conf/auth.html
    - https://documentation.rvbionics.com/current/user-manual/registering/key-request.html

tags:
    - key_request
'''
import re
from pathlib import Path

import pytest
from securics_testing.constants.paths.logs import SECURICS_LOG_PATH
from securics_testing.constants.paths.sockets import MODULESD_KREQUEST_SOCKET_PATH
from securics_testing.constants.daemons import AUTHD_DAEMON
from securics_testing.utils.configuration import load_configuration_template, get_test_cases_data
from securics_testing.tools.monitors.file_monitor import FileMonitor
from securics_testing.utils import callbacks
from securics_testing.modules.authd import PREFIX
from securics_testing.modules.authd.configuration import AUTHD_DEBUG_CONFIG

from . import CONFIGURATIONS_FOLDER_PATH, TEST_CASES_FOLDER_PATH, SCRIPTS_FOLDER_PATH

# Marks

pytestmark = [pytest.mark.server, pytest.mark.tier(level=0)]

# Configurations
test_configuration_path = Path(CONFIGURATIONS_FOLDER_PATH, 'config_authd_key_request_exec_path.yaml')
test_cases_path = Path(TEST_CASES_FOLDER_PATH, 'cases_authd_key_request_exec_path.yaml')
test_configuration, test_metadata, test_cases_ids = get_test_cases_data(test_cases_path)
test_configuration = load_configuration_template(test_configuration_path, test_configuration, test_metadata)

# Configurations

local_internal_options = {AUTHD_DEBUG_CONFIG: '2'}

# Variables
script_path = SCRIPTS_FOLDER_PATH
script_filename = 'fetch_keys.py'
receiver_sockets_params = [(MODULESD_KREQUEST_SOCKET_PATH, 'AF_UNIX', 'UDP')]

monitored_sockets_params = [('securics-authd', None, True)]
receiver_sockets, monitored_sockets = None, None

daemons_handler_configuration = {'daemons': [AUTHD_DAEMON], 'ignore_errors': True}


# Tests
@pytest.mark.parametrize('test_configuration,test_metadata', zip(test_configuration, test_metadata), ids=test_cases_ids)
def test_key_request_exec_path(test_configuration, test_metadata, set_securics_configuration,
                               copy_tmp_script, configure_local_internal_options,
                               truncate_monitored_files, daemons_handler,
                               wait_for_authd_startup, connect_to_sockets):
    '''
    description:
        Checks that every input message on the key request port with different exec_path configuration
        shows the corresponding error in the manager logs.

    securics_min_version: 4.4.0

    parameters:
        - test_configuration:
            type: dict
            brief: Configuration loaded from `configuration_templates`.
        - test_metadata:
            type: dict
            brief: Test case metadata.
        - set_securics_configuration:
            type: fixture
            brief: Load basic securics configuration.
        - copy_tmp_script:
            type: fixture
            brief: Copy the script to a temporary folder for testing.
        - configure_local_internal_options:
            type: fixture
            brief: Configure the local internal options file.
        - daemons_handler:
            type: fixture
            brief: Handler of Securics daemons.
        - wait_for_authd_startup:
            type: fixture
            brief: Waits until Authd is accepting connections.
        - connect_to_sockets:
            type: fixture
            brief: Bind to the configured sockets at function scope.
        - truncate_monitored_files:
            type: fixture
            brief: Truncate all the log files and json alerts files before and after the test execution.

    assertions:
        - The exec_path must be configured correctly
        - The script works as expected

    input_description:
        Different test cases are contained in an external YAML file (test_key_request_exec_path.yaml) which
        includes the different possible key requests with different configurations and the expected responses.

    expected_log:
        - Key request responses on 'authd' logs.
    '''

    key_request_sock = receiver_sockets[0]

    message = test_metadata['input']
    expected_logs = test_metadata['log']
    key_request_sock.send(message, size=False)
    # Monitor expected log messages
    securics_log_monitor = FileMonitor(SECURICS_LOG_PATH)
    for log in expected_logs:
        log = re.escape(log)
        securics_log_monitor.start(callback=callbacks.generate_callback(fr'{PREFIX}{log}'), timeout=10)
        assert securics_log_monitor.callback_result, f'Error event not detected'
