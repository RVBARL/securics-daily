"""
Copyright (C) 2015-2024, Securics Inc.
Created by Securics, Inc. <info@rvbionics.com>.
This program is free software; you can redistribute it and/or modify it under the terms of GPLv2
"""
import pytest

from securics_testing.constants.paths.configurations import SECURICS_CLIENT_KEYS_PATH
from securics_testing.utils import file
from . import utils


@pytest.fixture()
def clean_agents_ctx(stop_authd):
    """
    Clean agents files.
    """
    file.truncate_file(SECURICS_CLIENT_KEYS_PATH)
    utils.clean_rids()
    utils.clean_agents_timestamp()
    utils.clean_diff()

    yield

    file.truncate_file(SECURICS_CLIENT_KEYS_PATH)
    utils.clean_rids()
    utils.clean_agents_timestamp()
    utils.clean_diff()
