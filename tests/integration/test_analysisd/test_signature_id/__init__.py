# Copyright (C) 2015-2024, Securics Inc.
# Created by Securics, Inc. <info@rvbionics.com>.
# This program is free software; you can redistribute it and/or modify it under the terms of GPLv2
from pathlib import Path


# Constants & base paths
DATA_PATH = Path(Path(__file__).parent, 'data')
RULES_SAMPLE_PATH = Path(DATA_PATH, 'rules_samples')
CONFIGS_PATH = Path(DATA_PATH, 'configuration_templates')
TEST_CASES_PATH = Path(DATA_PATH, 'test_cases')
