#!/usr/bin/env python

# Copyright (C) 2023-2024, RV Bionics Group SpA.
# Created by Securics, Inc. <info@rvbionics.com>.
# This program is free software; you can redistribute it and/or modify it under the terms of GPLv2

from securics import __version__

from setuptools import setup, find_namespace_packages

setup(name='securics',
      version=__version__,
      description='Securics control with Python',
      url='https://github.com/securics',
      author='Securics',
      author_email='hello@rvbionics.com',
      license='GPLv2',
      packages=find_namespace_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
      package_data={'securics': ['core/securics.json',
                              'core/cluster/cluster.json', 'rbac/default/*.yaml']},
      include_package_data=True,
      install_requires=[],
      zip_safe=False,
      )
