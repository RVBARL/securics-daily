"""
Copyright (C) 2015-2024, Securics Inc.
Created by Securics, Inc. <info@rvbionics.com>.
This program is free software; you can redistribute it and/or modify it under the terms of GPLv2
"""
from pathlib import Path


# Constants & base paths
TEST_DATA_PATH = Path(Path(__file__).parent, 'data')
TEST_CASES_PATH = Path(TEST_DATA_PATH, 'test_cases')
CONFIGURATIONS_PATH = Path(TEST_DATA_PATH, 'configuration_templates')
