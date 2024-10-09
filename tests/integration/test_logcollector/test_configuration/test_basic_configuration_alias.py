'''
copyright: Copyright (C) 2015-2024, Securics Inc.

           Created by Securics, Inc. <info@rvbionics.com>.

           This program is free software; you can redistribute it and/or modify it under the terms of GPLv2

type: integration

brief: The 'securics-logcollector' daemon monitors configured files and commands for new log messages.
       Specifically, these tests will check if the log collector generates events using the alias
       specified in the 'alias' tag when monitoring a command, and the Securics API returns the same
       values for the configured 'localfile' section.
       Log data collection is the real-time process of making sense out of the records generated by
       servers or devices. This component can receive logs through text files or Windows event logs.
       It can also directly receive logs via remote syslog which is useful for firewalls and
       other such devices.

components:
    - logcollector

suite: configuration

targets:
    - agent

daemons:
    - securics-logcollector
    - securics-apid

os_platform:
    - linux
    - macos
    - windows

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
    - https://documentation.rvbionics.com/current/user-manual/capabilities/log-data-collection/index.html
    - https://documentation.rvbionics.com/current/user-manual/reference/ossec-conf/localfile.html#alias

tags:
    - logcollector_configuration
'''
import pytest
import sys

from pathlib import Path

from securics_testing.constants.paths.logs import SECURICS_LOG_PATH
from securics_testing.constants.platforms import WINDOWS, MACOS
from securics_testing.modules.agentd import configuration as agentd_configuration
from securics_testing.modules.logcollector import configuration as logcollector_configuration
from securics_testing.modules.logcollector import patterns
from securics_testing.modules.logcollector import utils
from securics_testing.tools.monitors import file_monitor
from securics_testing.utils import callbacks, configuration

from . import TEST_CASES_PATH, CONFIGURATIONS_PATH


# Marks
pytestmark = [pytest.mark.agent, pytest.mark.linux, pytest.mark.win32, pytest.mark.darwin, pytest.mark.tier(level=0)]

# Variables
local_internal_options = {logcollector_configuration.LOGCOLLECTOR_DEBUG: '2', logcollector_configuration.LOGCOLLECTOR_REMOTE_COMMANDS: '1', agentd_configuration.AGENTD_WINDOWS_DEBUG: '2'}

if sys.platform == WINDOWS:
    command = 'tasklist'
elif sys.platform == MACOS:
    command = 'ps aux'
else:
    command = 'ps -aux'

# Test metadata, configuration and ids.
cases_path = Path(TEST_CASES_PATH, 'cases_basic_configuration_alias.yaml')
config_path = Path(CONFIGURATIONS_PATH, 'securics_basic_configuration.yaml')
test_configuration, test_metadata, test_cases_ids = configuration.get_test_cases_data(cases_path)
for test in test_metadata:
    if test['command']:
        test['command'] = command
for test in test_configuration:
    if test['COMMAND']:
        test['COMMAND'] = command
test_configuration = configuration.load_configuration_template(config_path, test_configuration, test_metadata)

# Test daemons to restart.
daemons_handler_configuration = {'all_daemons': True}


# Test function.
@pytest.mark.parametrize('test_configuration, test_metadata', zip(test_configuration, test_metadata), ids=test_cases_ids)
def test_configuration_alias(test_configuration, test_metadata, configure_local_internal_options, truncate_monitored_files,
                            set_securics_configuration, daemons_handler):
    '''
    description: Check if the 'securics-logcollector' daemon changes a command name in the log messages by
                 the one defined in the 'alias' tag. For this purpose, the test will monitor a command
                 using an alias. Then, it will verify that the 'reading command' event is generated.
                 This event includes the output of the command executed and its alias. Finally, the test
                 will verify that the Securics API returns the same values for the 'localfile' section that
                 the configured one.

    securics_min_version: 4.2.0

    tier: 0

    parameters:
        - test_configuration:
            type: data
            brief: Configuration used in the test.
        - test_metadata:
            type: data
            brief: Configuration cases.
        - configure_local_internal_options:
            type: fixture
            brief: Configure the Securics local internal options.
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
        - Verify that the logcollector monitors a command with an assigned alias.
        - Verify that the Securics API returns the same values for the 'localfile' section as the configured one.

    input_description: A configuration template (test_basic_configuration_alias) is contained in an external YAML file
                       (securics_basic_configuration.yaml). That template is combined with two test cases defined
                       in the module. Those include configuration settings for the 'securics-logcollector' daemon.

    expected_output:
        - r'Reading command message.*'

    tags:
        - logs
    '''

    # Wait for command
    securics_log_monitor = file_monitor.FileMonitor(SECURICS_LOG_PATH)
    securics_log_monitor.start(callback=callbacks.generate_callback(patterns.LOGCOLLECTOR_READING_COMMAND_ALIAS, {
                              'alias': test_metadata['alias']
                          }))
    assert (securics_log_monitor.callback_result != None), patterns.ERROR_COMMAND_MONITORING

    if sys.platform != WINDOWS:
        utils.validate_test_config_with_module_config(test_configuration=test_configuration)
