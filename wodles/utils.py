# Copyright (C) 2023-2024, RV Bionics Group SpA.
# Created by Securics, Inc. <info@rvbionics.com>.
# This program is free software; you can redistribute it and/or modify it under the terms of GPLv2

import os
import subprocess
from functools import lru_cache
from sys import exit


@lru_cache(maxsize=None)
def find_securics_path() -> str:
    """
    Get the Securics installation path.

    Returns
    -------
    str
        Path where Securics is installed or empty string if there is no framework in the environment.
    """
    abs_path = os.path.abspath(os.path.dirname(__file__))
    allparts = []
    while 1:
        parts = os.path.split(abs_path)
        if parts[0] == abs_path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == abs_path:  # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            abs_path = parts[0]
            allparts.insert(0, parts[1])

    securics_path = ''
    try:
        for i in range(0, allparts.index('wodles')):
            securics_path = os.path.join(securics_path, allparts[i])
    except ValueError:
        pass

    return securics_path


def call_securics_control(option: str) -> str:
    """
    Execute the securics-control script with the parameters specified.

    Parameters
    ----------
    option : str
        The option that will be passed to the script.

    Returns
    -------
    str
        The output of the call to securics-control.
    """
    securics_control = os.path.join(find_securics_path(), "bin", "securics-control")
    try:
        proc = subprocess.Popen([securics_control, option], stdout=subprocess.PIPE)
        (stdout, stderr) = proc.communicate()
        return stdout.decode()
    except (OSError, ChildProcessError):
        print(f'ERROR: a problem occurred while executing {securics_control}')
        exit(1)


def get_securics_info(field: str) -> str:
    """
    Execute the securics-control script with the 'info' argument, filtering by field if specified.

    Parameters
    ----------
    field : str
        The field of the output that's being requested. Its value can be 'SECURICS_VERSION', 'SECURICS_REVISION' or
        'SECURICS_TYPE'.

    Returns
    -------
    str
        The output of the securics-control script.
    """
    securics_info = call_securics_control("info")
    if not securics_info:
        return "ERROR"

    if not field:
        return securics_info

    env_variables = securics_info.rsplit("\n")
    env_variables.remove("")
    securics_env_vars = dict()
    for env_variable in env_variables:
        key, value = env_variable.split("=")
        securics_env_vars[key] = value.replace("\"", "")

    return securics_env_vars[field]


@lru_cache(maxsize=None)
def get_securics_version() -> str:
    """
    Return the version of Securics installed.

    Returns
    -------
    str
        The version of Securics installed.
    """
    return get_securics_info("SECURICS_VERSION")


@lru_cache(maxsize=None)
def get_securics_revision() -> str:
    """
    Return the revision of the Securics instance installed.

    Returns
    -------
    str
        The revision of the Securics instance installed.
    """
    return get_securics_info("SECURICS_REVISION")


@lru_cache(maxsize=None)
def get_securics_type() -> str:
    """
    Return the type of Securics instance installed.

    Returns
    -------
    str
        The type of Securics instance installed.
    """
    return get_securics_info("SECURICS_TYPE")


ANALYSISD = os.path.join(find_securics_path(), 'queue', 'sockets', 'queue')
# Max size of the event that ANALYSISID can handle
MAX_EVENT_SIZE = 65535
