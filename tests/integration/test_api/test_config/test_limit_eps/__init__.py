"""
Copyright (C) 2023-2024, RV Bionics Group SpA.
Created by Securics, Inc. <info@rvbionics.com>.
This program is free software; you can redistribute it and/or modify it under the terms of GPLv2
"""
from pathlib import Path

# Constants & base paths
TEST_DATA_PATH = Path(Path(__file__).parent, 'data')
TEST_CASES_FOLDER_PATH = Path(TEST_DATA_PATH, 'test_cases')
CONFIGURATIONS_FOLDER_PATH = Path(TEST_DATA_PATH, 'configuration_templates')
