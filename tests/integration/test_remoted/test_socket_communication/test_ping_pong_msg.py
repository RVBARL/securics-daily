"""
 Copyright (C) 2015-2024, Securics Inc.
 Created by Securics, Inc. <info@rvbionics.com>.
 This program is free software; you can redistribute it and/or modify it under the terms of GPLv2
"""

import pytest

from pathlib import Path
from securics_testing.tools.monitors.file_monitor import FileMonitor
from securics_testing.utils.callbacks import generate_callback
from securics_testing.utils.configuration import get_test_cases_data, load_configuration_template
from securics_testing.constants.paths.logs import SECURICS_LOG_PATH
from securics_testing.modules.remoted.configuration import REMOTED_DEBUG
from securics_testing.modules.remoted import patterns
from securics_testing.modules.api import utils
from securics_testing.tools.simulators.agent_simulator import send_ping_pong_messages

from . import CONFIGS_PATH, TEST_CASES_PATH


# Set pytest marks.
pytestmark = [pytest.mark.server, pytest.mark.tier(level=1)]

# Cases metadata and its ids.
cases_path = Path(TEST_CASES_PATH, 'cases_ping_pong_msg.yaml')
config_path = Path(CONFIGS_PATH, 'config_socket_communication.yaml')
test_configuration, test_metadata, cases_ids = get_test_cases_data(cases_path)
test_configuration = load_configuration_template(config_path, test_configuration, test_metadata)

daemons_handler_configuration = {'all_daemons': True}

local_internal_options = {REMOTED_DEBUG: '2'}

# Test function.
@pytest.mark.parametrize('test_configuration, test_metadata',  zip(test_configuration, test_metadata), ids=cases_ids)
def test_ping_pong_message(test_configuration, test_metadata, configure_local_internal_options, truncate_monitored_files,
                            set_securics_configuration, restart_securics_expect_error, protocols_list_to_str_upper_case):

    '''
    description: Check if 'securics-remoted' sends the #pong message

    parameters:
        - test_configuration
            type: dict
            brief: Configuration applied to ossec.conf.
        - test_metadata:
            type: dict
            brief: Test case metadata.
        - truncate_monitored_files:
            type: fixture
            brief: Truncate all the log files and json alerts files before and after the test execution.
        - configure_local_internal_options:
            type: fixture
            brief: Configure the Securics local internal options using the values from `local_internal_options`.
        - restart_securics_expect_error
            type: fixture
            brief: Restart service when expected error is None, once the test finishes stops the daemons.
        - protocols_list_to_str_upper_case
            type: fixture
            brief: convert valid_protocol list to comma separated uppercase string
        - set_securics_configuration:
            type: fixture
            brief: Apply changes to the ossec.conf configuration.
    '''

    log_monitor = FileMonitor(SECURICS_LOG_PATH)

    protocol_valid_upper = protocols_list_to_str_upper_case
    protocol = protocol_valid_upper
    protocols = protocol_valid_upper.split(',')

    if protocol_valid_upper in ['TCP,TCP', 'UDP,UDP', 'tcp,tcp', 'udp,udp']:
        protocol = protocol_valid_upper.split(',')[0]

    log_monitor.start(callback=generate_callback(patterns.DETECT_REMOTED_STARTED,
                                                 replacement={
                                                    "port": test_metadata['port'],
                                                    "protocol_valid_upper": protocol,
                                                    "connection":'secure'}))
    assert log_monitor.callback_result

    if test_metadata['multiple_pings'] and (protocols[0] != protocols[1]):
        assert b'#pong' == send_ping_pong_messages(protocols[0], "localhost", int(test_metadata['port']))
        assert b'#pong' == send_ping_pong_messages(protocols[1], "localhost", int(test_metadata['port']))
    else :
        assert b'#pong' == send_ping_pong_messages(protocol, "localhost", int(test_metadata['port']))
