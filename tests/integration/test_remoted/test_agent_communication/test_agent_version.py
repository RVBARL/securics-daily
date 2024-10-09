"""
 Copyright (C) 2015-2024, Securics Inc.
 Created by Securics, Inc. <info@rvbionics.com>.
 This program is free software; you can redistribute it and/or modify it under the terms of GPLv2
"""

import pytest
import time

from pathlib import Path
from securics_testing.tools.simulators.agent_simulator import connect
from securics_testing.utils.configuration import get_test_cases_data, load_configuration_template
from securics_testing.modules.remoted.configuration import REMOTED_DEBUG

from . import CONFIGS_PATH, TEST_CASES_PATH


# Set pytest marks.
pytestmark = [pytest.mark.server, pytest.mark.tier(level=2)]

# Cases metadata and its ids.
cases_path = Path(TEST_CASES_PATH, 'cases_agent_version.yaml')
config_path = Path(CONFIGS_PATH, 'config_shared_configuration.yaml')
test_configuration, test_metadata, cases_ids = get_test_cases_data(cases_path)
test_configuration = load_configuration_template(config_path, test_configuration, test_metadata)

daemons_handler_configuration = {'all_daemons': True}

local_internal_options = {REMOTED_DEBUG: '2'}


# Test function.
@pytest.mark.parametrize('test_configuration, test_metadata',  zip(test_configuration, test_metadata), ids=cases_ids)
def test_agent_version(test_configuration, test_metadata, configure_local_internal_options, truncate_monitored_files,
                            set_securics_configuration, daemons_handler, simulate_agents):

    '''
    description: Check if the manager sends the shared configuration to agents through remote,
                 ensuring the agent version is correct.


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

    agent = simulate_agents[0]
    sender, injector = connect(agent = agent, protocol = test_metadata['protocol'])

    time.sleep(5)

    securics_db_agent_version = agent.get_agent_version()
    assert securics_db_agent_version

    injector.stop_receive()
