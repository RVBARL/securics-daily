
"""
 Copyright (C) 2015-2024, Securics Inc.
 Created by Securics, Inc. <info@rvbionics.com>.
 This program is free software; you can redistribute it and/or modify it under the terms of GPLv2
"""

import pytest
import time

from pathlib import Path
from securics_testing.modules.remoted.patterns import KEY_UPDATE
from securics_testing.tools.simulators.agent_simulator import connect
from securics_testing.utils.configuration import get_test_cases_data, load_configuration_template
from securics_testing.modules.remoted.configuration import REMOTED_DEBUG
from securics_testing.constants.paths.logs import SECURICS_LOG_PATH
from securics_testing.tools.monitors.file_monitor import FileMonitor
from securics_testing.utils.callbacks import generate_callback
from securics_testing.tools.thread_executor import ThreadExecutor
from . import CONFIGS_PATH, TEST_CASES_PATH


# Set pytest marks.
pytestmark = [pytest.mark.server, pytest.mark.tier(level=2)]

# Cases metadata and its ids.
cases_path = Path(TEST_CASES_PATH, 'cases_agent_pending_status.yaml')
config_path = Path(CONFIGS_PATH, 'config_agent_pending_status.yaml')
test_configuration, test_metadata, cases_ids = get_test_cases_data(cases_path)
test_configuration = load_configuration_template(config_path, test_configuration, test_metadata)

daemons_handler_configuration = {'all_daemons': True}

local_internal_options = {REMOTED_DEBUG: '2'}

injectors = []


def send_event(protocol, manager_port, agent):
    """Send an event to the manager"""

    sender, injector = connect(agent, manager_port = manager_port, protocol = protocol, wait_status='pending')
    injectors.append(injector)
    return injector

# Test function.
@pytest.mark.parametrize('test_configuration, test_metadata',  zip(test_configuration, test_metadata), ids=cases_ids)
def test_agent_pending_status(test_configuration, test_metadata, configure_local_internal_options, truncate_monitored_files,
                            set_securics_configuration, daemons_handler, simulate_agents):

    '''
    description: Validate agent status after sending only the start-up

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
        - daemons_handler:
            type: fixture
            brief: Restart service once the test finishes stops the daemons.
        - simulate_agents
            type: fixture
            brief: create agents
        - set_securics_configuration:
            type: fixture
            brief: Apply changes to the ossec.conf configuration.

    '''

    log_monitor = FileMonitor(SECURICS_LOG_PATH)


    agents = simulate_agents

    log_monitor.start(callback=generate_callback(KEY_UPDATE))
    assert log_monitor.callback_result


    manager_port = test_metadata['port']
    protocol = test_metadata['protocol']
    send_event_threads = []


    for agent in agents:

        # Create sender event threads
        send_event_threads.append(ThreadExecutor(send_event, {'protocol': protocol,
                                                              'manager_port': manager_port, 'agent': agent}))

    # Wait 10 seconds until remoted is fully initialized
    time.sleep(10)

    # Start sender event threads
    for thread in send_event_threads:
        thread.start()

    # Wait until sender event threads finish
    for thread in send_event_threads:
        thread.join()

    for injector in injectors:
        injector.stop_receive()
