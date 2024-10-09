# Copyright (C) 2015-2024, Securics Inc.
# Created by Securics, Inc. <info@rvbionics.com>.
# This program is free software; you can redistribute it and/or modify it under the terms of GPLv2

import pytest

from securics_testing.constants.paths.logs import SECURICS_LOG_PATH
from securics_testing.modules.modulesd import patterns
from securics_testing.tools.monitors.file_monitor import FileMonitor
from securics_testing.utils import callbacks


@pytest.fixture()
def wait_for_office365_start():
    # Wait for module office365 starts
    securics_log_monitor = FileMonitor(SECURICS_LOG_PATH)
    securics_log_monitor.start(callback=callbacks.generate_callback(patterns.MODULESD_STARTED, {
                              'integration': 'Office365'
                          }))
    assert (securics_log_monitor.callback_result == None), f'Error invalid configuration event not detected'
