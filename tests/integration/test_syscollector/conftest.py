"""
 Copyright (C) 2015-2024, Securics Inc.
 Created by Securics, Inc. <info@rvbionics.com>.
 This program is free software; you can redistribute it and/or modify it under the terms of GPLv2
"""
import pytest
import sys

from securics_testing.tools.monitors import file_monitor
from securics_testing.modules.modulesd.syscollector import patterns
from securics_testing.constants.paths.logs import SECURICS_LOG_PATH
from securics_testing.utils import callbacks
from securics_testing.constants.platforms import WINDOWS


# Fixtures
@pytest.fixture()
def wait_for_syscollector_enabled():
    '''
    Wait for the syscollector module to start.
    '''
    log_monitor = file_monitor.FileMonitor(SECURICS_LOG_PATH)
    log_monitor.start(callback=callbacks.generate_callback(patterns.CB_MODULE_STARTED), timeout=60 if sys.platform == WINDOWS else 10)
    assert log_monitor.callback_result
